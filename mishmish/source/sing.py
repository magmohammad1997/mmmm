"""Turn natural neural-TTS speech into singing:
 1) Chatterbox multilingual speaks each lyric line (Arabic, natural voice)
 2) DTW-align it to the MBROLA guide vocal (which has the exact note timing)
 3) WORLD re-synthesis on the guide's timeline with the melody's exact pitch."""
import json, os, sys, numpy as np, soundfile as sf, librosa, pyworld as pw
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import song
W = os.path.dirname(os.path.abspath(__file__))
SR = 24000; FP = 5.0
SHIFT = -12  # sing an octave below the written melody (natural range)

def tts_lines(texts, cache, nsyl):
    os.makedirs(cache, exist_ok=True)
    uniq = {}
    for i, t in enumerate(texts): uniq.setdefault(t, i)   # chorus repeats reuse the first take
    todo = [i for t, i in uniq.items() if not os.path.exists(f"{cache}/{i}.wav")]
    if todo:
        import torch
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
        ref = os.environ.get("REF_WAV")
        for i in todo:
            best = None
            for attempt in range(4):
                torch.manual_seed(3 + 17 * attempt + i)
                kw = dict(language_id="ar", exaggeration=0.65, cfg_weight=0.4, temperature=0.7)
                if ref: kw["audio_prompt_path"] = ref
                y = m.generate(texts[i], **kw).squeeze(0).numpy()
                if m.sr != SR: y = librosa.resample(y, orig_sr=m.sr, target_sr=SR)
                yt, _ = librosa.effects.trim(y, top_db=35); d = len(yt) / SR
                ok = 0.12 * nsyl[i] <= d <= 0.33 * nsyl[i] + 0.8
                print("tts", i, attempt, round(d, 2), "ok" if ok else "retry", flush=True)
                if best is None or abs(d - .22 * nsyl[i]) < abs(best[1] - .22 * nsyl[i]): best = (y, d)
                if ok: break
            sf.write(f"{cache}/{i}.wav", best[0], SR)
    for t, i in uniq.items():
        for j, t2 in enumerate(texts):
            if t2 == t and j != i and not os.path.exists(f"{cache}/{j}.wav"):
                import shutil; shutil.copy(f"{cache}/{i}.wav", f"{cache}/{j}.wav")

def mfcc(y, sr):
    hop = int(sr * FP / 1000)
    M = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20, hop_length=hop, n_fft=int(sr * .025) // 2 * 2 * 2)[1:]
    return (M - M.mean(1, keepdims=True)) / (M.std(1, keepdims=True) + 1e-6)

def main():
    # collect lines in the order of song.PLAN, with their notes
    lines = []
    for sec, sb, ls in song.PLAN:
        for diac, disp, mel in ls:
            segs, notes, st = song.build_line(diac, mel, sb)
            a = min(s[1] for s in segs); b = max(s[2] for s in segs)
            lines.append(dict(diac=diac, notes=notes, a=a, b=b))
    texts = [l["diac"] + ("!" if len(l["notes"]) < 4 else ".") for l in lines]
    tts_lines(texts, f"{W}/tts", [len(l["notes"]) for l in lines])
    guide, gsr = sf.read(f"{W}/raw16.wav"); guide = librosa.resample(guide, orig_sr=gsr, target_sr=SR)
    total = int(song.TOTAL * SR); out = np.zeros(total + SR)
    hop = int(SR * FP / 1000)
    for i, L in enumerate(lines):
        y, _ = sf.read(f"{W}/tts/{i}.wav")
        y, _ = librosa.effects.trim(y, top_db=35)
        a, b = L["a"] - .03, L["b"] + .03
        g = guide[int(a * SR):int(b * SR)]
        Mg, My = mfcc(g, SR), mfcc(y, SR)
        D, wp = librosa.sequence.dtw(Mg, My, metric="cosine", step_sizes_sigma=np.array([[1, 1], [0, 1], [1, 0]]),
                                     weights_add=np.array([0, .15, .15]))
        wp = wp[::-1]
        nG = Mg.shape[1]; jmap = np.zeros(nG)
        for k in range(nG):
            js = wp[wp[:, 0] == k, 1]; jmap[k] = np.median(js) if len(js) else (jmap[k - 1] if k else 0)
        jmap = np.maximum.accumulate(signal.medfilt(jmap, 5))
        # WORLD on the TTS line
        y64 = y.astype(np.float64)
        f0, t = pw.harvest(y64, SR, f0_floor=70, f0_ceil=600, frame_period=FP)
        sp = pw.cheaptrick(y64, f0, t, SR); ap = pw.d4c(y64, f0, t, SR)
        idx = np.clip(np.round(jmap).astype(int), 0, len(f0) - 1)
        sp2, ap2, v2 = sp[idx], ap[idx], f0[idx] > 0
        # target pitch from the melody on the guide timeline
        times = a + np.arange(nG) * FP / 1000
        tgt = np.zeros(nG); notes = L["notes"]
        for n, (n0, n1, m) in enumerate(notes):
            f = song.m2f(m + SHIFT)
            sel = (times >= n0 - .1) & (times < (notes[n + 1][0] - .1 if n + 1 < len(notes) else n1 + .2))
            loc = times[sel] - n0
            vib = 1 + .013 * np.sin(2 * np.pi * 5.6 * loc) * np.clip((loc - .22) * 4, 0, 1)
            tgt[sel] = f * vib
        # smooth note transitions (portamento ~40ms)
        tg = tgt.copy(); tg[tg == 0] = np.nan
        tg = np.exp(np.convolve(np.nan_to_num(np.log(np.where(np.isnan(tg), 1, tg))), np.ones(9) / 9, "same"))
        tgt = np.where(tgt > 0, tg, 0)
        newf0 = np.where(v2 & (tgt > 0), tgt, 0.0)
        z = pw.synthesize(newf0, np.ascontiguousarray(sp2), np.ascontiguousarray(ap2), SR, FP)
        fade = int(.02 * SR); z[:fade] *= np.linspace(0, 1, fade); z[-fade:] *= np.linspace(1, 0, fade)
        s0 = int(a * SR); out[s0:s0 + len(z)] += z[: len(out) - s0]
        print("line", i, "ok", flush=True)
    out = out[:total]
    sf.write(f"{W}/sung24.wav", out / (np.abs(out).max() + 1e-9) * .9, SR)

if __name__ == "__main__":
    main()
