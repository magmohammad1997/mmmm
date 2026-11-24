import sys, os, re, shutil, numpy as np, soundfile as sf, librosa, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import song
from transformers import pipeline
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
SR = 24000
lines = [diac for sec, sb, ls in song.PLAN for diac, disp, mel in ls]
def norm(s):
    s = re.sub(r"[ً-ْٰـ]", "", s); s = re.sub(r"[^ء-ي ]", "", s)
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")
    return re.sub(" +", " ", s).strip()
def cer(a, b):
    a, b = norm(a).replace(" ", ""), norm(b).replace(" ", "")
    d = np.arange(len(b) + 1)
    for i, ca in enumerate(a, 1):
        nd = d.copy(); nd[0] = i
        for j, cb in enumerate(b, 1): nd[j] = min(d[j] + 1, nd[j - 1] + 1, d[j - 1] + (ca != cb))
        d = nd
    return d[-1] / max(1, len(a))
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small", device="cpu")
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for i in map(int, sys.argv[1:]):
    ref = lines[i]; plain = norm(ref)
    cands = []
    for k, (txt, seed) in enumerate([(plain + ".", 11), (ref + ".", 23), (plain + ".", 37), (ref + ".", 41), (plain + "!", 53)]):
        torch.manual_seed(seed + i)
        y = m.generate(txt, language_id="ar", audio_prompt_path="ref/ar_f.wav", exaggeration=0.6, cfg_weight=0.45, temperature=0.65).squeeze(0).numpy()
        y = librosa.resample(y, orig_sr=m.sr, target_sr=SR) if m.sr != SR else y
        yt, _ = librosa.effects.trim(y, top_db=35)
        hyp = asr(librosa.resample(yt, orig_sr=SR, target_sr=16000).astype(np.float32), generate_kwargs={"language": "arabic", "task": "transcribe"})["text"]
        c = cer(ref, hyp); d = len(yt) / SR
        n = len(song.syllabify(song.pho(ref)))
        if d > .33 * n + .8: c += 1
        print(i, k, round(c, 3), round(d, 2), hyp, flush=True)
        cands.append((c, k, y))
        if c < .05: break
    c, k, y = min(cands, key=lambda x: x[0])
    sf.write(f"tts/{i}.wav", y, SR); print("BEST", i, k, round(c, 3), flush=True)
