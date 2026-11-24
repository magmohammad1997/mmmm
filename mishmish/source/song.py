"""Original cartoon song 'Mishmish & the Moon' — full synthesis (vocals via MBROLA+WORLD, instruments in numpy)."""
import json, subprocess, os, sys
import numpy as np, soundfile as sf, pyworld as pw
from scipy import signal
sys.path.insert(0, os.path.dirname(__file__))
from syl import pho, syllabify, isvowel

SR = 44100
BPM = 120
BEAT = 60 / BPM
TOTAL = 60.0
W = os.path.dirname(os.path.abspath(__file__))

def m2f(m): return 440 * 2 ** ((m - 69) / 12)
N = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
def note(s):  # "C5" -> midi
    return 12 * (int(s[-1]) + 1) + N[s[:-1]]

# ---------------- lyrics + melody (beats from line start; 'r' = rest) ----------------
V1 = [
 ("فِي لَيْلَةٍ حُلْوَةٍ فِيهَا نُجُومْ", "في ليلةٍ حلوةٍ فيها نجوم",
  "r:.5 G4:.5 A4:.5 C5:.5 C5:1 C5:.5 C5:.5 E5:.5 D5:.5 C5:.5 A4:.5 C5:2"),
 ("مِشْمِشُ الْقِطَّةُ فَوْقَ السَّطْحِ تَحُومْ", "مشمشُ القطّةُ فوقَ السطحِ تحوم",
  "r:.5 G4:.5 A4:.5 C5:.5 D5:1 D5:.5 D5:.5 F5:.5 E5:.5 D5:.5 C5:.5 D5:2"),
 ("رَأَتْ قَمَرًا يَضْحَكُ مِنْ بَعِيدْ", "رأتْ قمرًا يضحكُ من بعيد",
  "r:.5 G4:.5 A4:.5 C5:.5 E5:1 E5:.5 E5:.5 G5:.5 E5:.5 D5:.5 C5:.5 A4:2"),
 ("قَالَتْ يَا قَمَرُ سَأَصِلُ أَكِيدْ", "قالتْ: يا قمرُ.. سأصلُ أكيد!",
  "G4:.5 A4:.5 C5:.5 C5:.5 D5:.5 E5:.5 D5:.5 C5:.5 D5:.5 E5:.5 F5:1 D5:2"),
]
CH = [
 ("طِيرِي طِيرِي يَا مِشْمِشُ طِيرِي", "طيري طيري يا مشمشُ طيري",
  "C5:.75 A4:.75 C5:.5 F5:1 E5:1 D5:.5 E5:.5 D5:1 B4:1 D5:1"),
 ("فَوْقَ الْغُيُومِ إِلَى الْقَمَرِ سِيرِي", "فوقَ الغيومِ إلى القمرِ سيري",
  "B4:.5 B4:.5 B4:.5 B4:.5 G4:.5 B4:.5 E5:1 E5:.5 D5:.5 C5:1 A4:2"),
 ("مِيَاوْ مِيَاوْ وَالنُّجُومُ تُغَنِّي", "مياو مياو.. والنجومُ تغنّي",
  "C5:.5 F5:1 C5:.5 F5:1 E5:.5 D5:.5 D5:.5 D5:.5 E5:.5 F5:.5 G5:2"),
 ("يَا قَمَرَ اللَّيْلِ اضْحَكْ وَغَنِّي", "يا قمرَ الليلِ اضحكْ وغنّي",
  "E5:.5 E5:.5 D5:.5 C5:.5 D5:1 E5:1 D5:.5 C5:.5 D5:1 C5:2"),
]
V2 = [
 ("صَارُوخٌ مِنْ كَرْتُونٍ وَقَلْبٌ كَبِيرْ", "صاروخٌ من كرتونٍ وقلبٌ كبير",
  "A4:.5 A4:.5 C5:.5 C5:.5 E5:.5 E5:.5 D5:.5 C5:.5 C5:.5 A4:.5 C5:1 C5:2"),
 ("وَصَلَتْ وَعَادَتْ بِنَجْمَةٍ تُنِيرْ", "وصلتْ.. وعادتْ بنجمةٍ تُنير ✨",
  "G4:.5 G4:.5 C5:.5 C5:.5 E5:.5 E5:.5 G5:.5 E5:.5 D5:.5 D5:.5 E5:1 D5:2"),
]
# (section, start beat)
PLAN = [("intro", 0, [("مِيَاوْ", "مياو! 🐱", "r:4 G5:.5 C6:1.5")])]
PLAN += [("verse1", 8 + 8 * i, [l]) for i, l in enumerate(V1)]
PLAN += [("chorus", 40 + 8 * i, [l]) for i, l in enumerate(CH)]
PLAN += [("verse2", 72 + 8 * i, [l]) for i, l in enumerate(V2)]
PLAN += [("chorus2", 88 + 8 * i, [l]) for i, l in enumerate(CH)]

CONS_LEN = {"S": .085, "s": .08, "s.": .08, "X": .08, "x": .08, "H": .07, "f": .07, "h": .06,
            "t": .055, "t.": .055, "k": .06, "q": .06, "b": .05, "d": .05, "d.": .05, "?": .03,
            "R": .045, "l": .05, "m": .06, "n": .055, "j": .045, "w": .05, "Z": .07, "G": .06}

def parse_mel(s):
    out = []
    for tok in s.split():
        n, d = tok.split(":"); out.append((None if n == "r" else note(n), float(d)))
    return out

def build_line(diac, mel, start_beat):
    """returns (pho_lines, notes[(t0,t1,midi)], syllable_times) times in seconds relative to song"""
    syls = syllabify(pho(diac))
    notes = []; t = start_beat * BEAT
    for m, d in parse_mel(mel):
        if m is not None: notes.append([t, t + d * BEAT, m])
        t += d * BEAT
    if len(notes) != len(syls):
        raise SystemExit(f"syllable mismatch {len(syls)} vs {len(notes)}: {diac}")
    segs = []  # (phoneme, t0, t1, midi)
    for k, (sy, (t0, t1, m)) in enumerate(zip(syls, notes)):
        vi = next(i for i, p in enumerate(sy) if isvowel(p))
        onset, vow, coda = sy[:vi], sy[vi], sy[vi + 1:]
        # onset before the beat
        ot = t0 - sum(CONS_LEN.get(p, .06) for p in onset)
        for p in onset:
            l = CONS_LEN.get(p, .06); segs.append((p, ot, ot + l, m)); ot += l
        # end of this syllable: next syllable's onset start (or note end w/ small release)
        end = t1
        if k + 1 < len(syls) and abs(notes[k + 1][0] - t1) < 1e-6:
            nsy = syls[k + 1]; nvi = next(i for i, p in enumerate(nsy) if isvowel(p))
            end = t1 - sum(CONS_LEN.get(p, .06) for p in nsy[:nvi])
        else:
            end = t1 - 0.06
        cl = sum(CONS_LEN.get(p, .06) for p in coda)
        segs.append((vow, t0, max(t0 + .05, end - cl), m))
        ct = max(t0 + .05, end - cl)
        for p in coda:
            l = CONS_LEN.get(p, .06); segs.append((p, ct, ct + l, m)); ct += l
    return segs, notes, [(n[0], n[1]) for n in notes]

def synth_vocal():
    allsegs, allnotes, lines = [], [], []
    for sec, sb, ls in PLAN:
        for diac, disp, mel in ls:
            segs, notes, st = build_line(diac, mel, sb)
            allsegs += segs; allnotes += notes
            lines.append({"section": sec, "text": disp, "start": notes[0][0], "end": notes[-1][1],
                          "syl": st})
    # single .pho for whole song with silences between
    allsegs.sort(key=lambda s: s[1])
    out = []; t = 0.0
    for p, t0, t1, m in allsegs:
        if t0 > t + 1e-4:
            out.append(f"_ {int(round((t0 - t) * 1000))}")
        t0 = max(t0, t)
        dur = max(10, int(round((t1 - t0) * 1000)))
        p = {"R": "r"}.get(p, p)
        f = m2f(m) / 2.0  # synthesize an octave down, WORLD lifts it later
        out.append(f"{p} {dur} 0 {f:.1f} 100 {f:.1f}" if isvowel(p) or p in ("l","m","n","r","j","w") else f"{p} {dur}")
        t = t0 + dur / 1000
    out.append(f"_ {int((TOTAL + 0.5 - t) * 1000)}")
    open(f"{W}/song.pho", "w").write("\n".join(out) + "\n")
    subprocess.run(["mbrola", "-e", "/usr/share/mbrola/ar1/ar1", f"{W}/song.pho", f"{W}/raw16.wav"], check=True)
    x, sr = sf.read(f"{W}/raw16.wav")
    x = x.astype(np.float64)
    # WORLD: exact melody pitch, vibrato, cartoon formant lift
    fp = 5.0
    f0, tt = pw.harvest(x, sr, f0_floor=70, f0_ceil=700, frame_period=fp)
    sp = pw.cheaptrick(x, f0, tt, sr); ap = pw.d4c(x, f0, tt, sr)
    target = np.zeros_like(f0)
    nts = sorted(allnotes)
    for i, (a, b, m) in enumerate(nts):
        idx = (tt >= a - 0.12) & (tt < b + 0.05)
        f = m2f(m)
        local = tt[idx] - a
        vib = np.where(local > 0.25, 1 + 0.012 * np.sin(2 * np.pi * 5.5 * local) * np.clip((local - .25) * 3, 0, 1), 1)
        cur = np.full(idx.sum(), f) * vib
        # portamento from previous note
        if i and a - nts[i - 1][1] < 0.05:
            pf = m2f(nts[i - 1][2]); k = np.clip((local + 0.04) / 0.07, 0, 1)
            cur = (pf ** (1 - k)) * (cur ** k)
        target[idx] = cur
    voiced = f0 > 0
    newf0 = np.where(voiced & (target > 0), target, np.where(voiced, f0 * 2, 0))
    # formant shift up (cartoon kid/cat voice)
    alpha = 1.22
    nb = sp.shape[1]; src = np.arange(nb) / alpha
    sp2 = np.array([np.interp(src, np.arange(nb), row) for row in sp])
    y = pw.synthesize(newf0, sp2, ap, sr, fp)
    y = signal.resample_poly(y, 441, 160)
    return y[: int(TOTAL * SR)], lines

# ---------------- instruments ----------------
def env(n, a=.005, d=.2, s=0., r=.05, sr=SR):
    t = np.arange(n) / sr
    e = np.minimum(1, t / max(a, 1e-4))
    e = np.where(t > a, s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)), e)
    tail = int(r * sr)
    if tail and n > tail: e[-tail:] *= np.linspace(1, 0, tail)
    return e

def add(buf, x, t, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if i < len(buf): buf[i:j] += g * x[: j - i]

def kick():
    n = int(.35 * SR); t = np.arange(n) / SR
    f = 50 + 120 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) + 0.3 * np.random.randn(n) * np.exp(-t * 200)

def clap():
    n = int(.25 * SR); t = np.arange(n) / SR; nz = np.random.randn(n)
    b, a = signal.butter(2, [900 / (SR / 2), 5000 / (SR / 2)], "band")
    e = sum(np.exp(-np.clip(t - d, 0, None) * 60) * (t >= d) for d in (0, .01, .02)) * 0.5 + np.exp(-t * 18) * .6
    return signal.lfilter(b, a, nz) * e

def hat(open_=False):
    n = int((.25 if open_ else .05) * SR); t = np.arange(n) / SR
    b, a = signal.butter(2, 7000 / (SR / 2), "high")
    return signal.lfilter(b, a, np.random.randn(n)) * np.exp(-t * (15 if open_ else 80))

def pluck(f, dur, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    mod = np.sin(2 * np.pi * f * 2 * t) * 1.5 * bright * np.exp(-t * 6)
    return np.sin(2 * np.pi * f * t + mod) * env(n, .003, .35, 0.15, .08)

def bell(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    mod = np.sin(2 * np.pi * f * 3.5 * t) * 2.0 * np.exp(-t * 4)
    return np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 3.0)

def bass(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = signal.sawtooth(2 * np.pi * f * t) * .5 + np.sin(2 * np.pi * f * t)
    b, a = signal.butter(2, 600 / (SR / 2))
    return signal.lfilter(b, a, x) * env(n, .005, .25, .55, .04)

def pad(fs, dur):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f in fs:
        for dt in (-0.12, 0.12):
            x += signal.sawtooth(2 * np.pi * f * (1 + dt / 100) * t)
    b, a = signal.butter(2, 1800 / (SR / 2))
    return signal.lfilter(b, a, x) / len(fs) * env(n, .25, 10, 1, .3)

def whoosh(dur=2.0, up=True):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.random.randn(n)
    out = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        k = i / n if up else 1 - i / n
        fc = 300 + 7000 * k ** 2
        b, a = signal.butter(2, [fc * .7 / (SR / 2), min(.99, fc * 1.3 / (SR / 2))], "band")
        out[i:i + blk] = signal.lfilter(b, a, x[i:i + blk])
    return out * (t / dur if up else 1 - t / dur) ** 2

CH_ = {"C": ["C", "E", "G"], "Am": ["A", "C", "E"], "F": ["F", "A", "C"], "G": ["G", "B", "D"],
       "Em": ["E", "G", "B"], "Dm": ["D", "F", "A"]}
PROG = (["C", "F", "C", "G"] +                      # intro (bars 0-3? only 2 bars used, see below)
        [])
BARS = (["F", "G"] +                                # intro 0-1
        ["C", "Am", "F", "G"] * 2 +                 # verse1 2-9
        ["F", "G", "Em", "Am", "F", "G", "C", "C"] + # chorus 10-17
        ["Am", "F", "C", "G"] +                     # verse2 18-21
        ["F", "G", "Em", "Am", "F", "G", "C", "C"])  # chorus2 22-29

def instrumental():
    L = int((TOTAL + 1.5) * SR)
    drums, bas, keys, pads, fx, bells = (np.zeros(L) for _ in range(6))
    np.random.seed(7)
    K, C, H, HO = kick(), clap(), hat(), hat(True)
    for bar, ch in enumerate(BARS):
        t0 = bar * 4 * BEAT
        notes = CH_[ch]; root = note(notes[0] + "2")
        sec = "intro" if bar < 2 else "verse" if bar < 10 or 18 <= bar < 22 else "chorus"
        # pads
        pads_f = [m2f(note(n + "4")) for n in notes]
        add(pads, pad(pads_f, 4 * BEAT + .3), t0, .9 if sec == "chorus" else .6)
        # bass: bouncy eighths in chorus, quarters elsewhere
        steps = [0, 1, 1.5, 2, 3, 3.5] if sec == "chorus" else [0, 2, 2.5, 3.5] if sec == "verse" else [0]
        for s in steps:
            m = root + (12 if s in (1.5, 3.5) else 0)
            add(bas, bass(m2f(m), (0.45 if sec != "intro" else 3.8) * BEAT), t0 + s * BEAT, .8)
        # plucked keys arpeggio (eighths)
        if sec != "intro" or True:
            arp = [note(notes[i % 3] + ("5" if i >= 3 else "4")) for i in (0, 1, 2, 3, 2, 1, 0, 1)]
            for i, m in enumerate(arp):
                add(keys, pluck(m2f(m), .4, 1.3 if sec == "chorus" else .8), t0 + i * .5 * BEAT, .32)
        # drums
        if sec != "intro":
            for b in range(4):
                tb = t0 + b * BEAT
                if sec == "chorus" or b in (0, 2): add(drums, K, tb, 1.0)
                if b in (1, 3): add(drums, C, tb, .55)
                add(drums, H, tb + .5 * BEAT, .25)
                if sec == "chorus": add(drums, H, tb, .15)
            if sec == "chorus" and bar % 2 == 1: add(drums, HO, t0 + 3.5 * BEAT, .2)
        else:
            add(drums, K, t0 + (3 * BEAT if bar == 1 else 0), .6)
    # sparkly bell motif in intro & over chorus (the "star" theme)
    motif = [("E6", 0), ("G6", .5), ("C7", 1), ("B6", 1.5), ("G6", 2), ("E6", 3)]
    for start in (0, 4 * BEAT, 40 * BEAT, 88 * BEAT, 116 * BEAT):
        for n, b in motif: add(bells, bell(m2f(note(n)), 1.5), start + b * BEAT, .22)
    # transitions
    for tb in (40, 88):
        w = whoosh(2.0); add(fx, w, tb * BEAT - 2.0, .25)
        add(fx, clap() * 0, 0)
    # drum fill before chorus
    for tb in (38, 86):
        for i in range(8): add(drums, C, (tb + 1 + i * .125) * BEAT + 0, .18 + .04 * i)
    # final chord ring
    add(keys, bell(m2f(note("C6")), 3), 119.5 * BEAT, .2)
    # sidechain pump on pads/keys
    pump = np.ones(L)
    for b in range(int(TOTAL / BEAT)):
        i = int(b * BEAT * SR); n = int(.25 * SR)
        if 2 * 4 <= b: pump[i:i + n] = np.minimum(pump[i:i + n], .45 + .55 * np.linspace(0, 1, n) ** .5)
    mix = drums * .55 + bas * .45 + keys * pump * .5 + pads * pump * .14 + fx + bells * .8
    return mix

def reverb(x, sec=1.6, wet=.18):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = np.random.RandomState(1).randn(n) * np.exp(-t * 4.5)
    b, a = signal.butter(1, 5000 / (SR / 2)); ir = signal.lfilter(b, a, ir); ir /= np.abs(ir).sum() ** .5 * 6
    return x + wet * signal.fftconvolve(x, ir)[: len(x)]

if __name__ == "__main__":
    voc, lines = synth_vocal()
    # vocal chain: HPF, presence, compression-ish, double in chorus
    b, a = signal.butter(2, 150 / (SR / 2), "high"); voc = signal.lfilter(b, a, voc)
    voc = voc / (np.abs(voc).max() + 1e-9)
    voc = np.tanh(voc * 2.2) / np.tanh(2.2)
    dbl = np.zeros_like(voc); d = int(.018 * SR); dbl[d:] = voc[:-d]
    chmask = np.zeros_like(voc)
    for a0, a1 in ((40 * BEAT, 72 * BEAT), (88 * BEAT, 120 * BEAT)): chmask[int(a0 * SR):int(a1 * SR)] = 1
    voc = voc + .35 * dbl * chmask
    inst = instrumental()[: int(TOTAL * SR)]
    L = int(TOTAL * SR); voc = np.pad(voc, (0, max(0, L - len(voc))))[:L]
    vl = reverb(voc, 1.4, .25); vr = reverb(np.roll(voc, 200), 1.5, .25)
    il = reverb(inst, 1.2, .12)
    left = il + vl * .9; right = il + vr * .9
    st = np.stack([left, right], 1)
    st /= np.abs(st).max() / .89
    fade = int(.05 * SR); st[:fade] *= np.linspace(0, 1, fade)[:, None]; st[-int(1.2 * SR):] *= np.linspace(1, 0, int(1.2 * SR))[:, None] ** .5
    sf.write(f"{W}/song.wav", st, SR, subtype="PCM_16")
    sf.write(f"{W}/vocal_only.wav", voc / np.abs(voc).max() * .9, SR)
    json.dump({"bpm": BPM, "lines": lines}, open(f"{W}/timing.json", "w"), ensure_ascii=False, indent=1)
    print("done", len(lines), "lines")
