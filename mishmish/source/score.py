import sys, re, numpy as np, soundfile as sf, librosa
from transformers import pipeline
LYR = open(sys.argv[1]).read()
def norm(s):
    s = re.sub(r"\[.*?\]", " ", s); s = re.sub(r"[ً-ْٰـ]", "", s); s = re.sub(r"[^ء-ي ]", " ", s)
    for a, b in (("أ","ا"),("إ","ا"),("آ","ا"),("ة","ه"),("ى","ي")): s = s.replace(a, b)
    return re.sub(r"\s+", "", s)
def cer(a, b):
    d = np.arange(len(b) + 1)
    for i, ca in enumerate(a, 1):
        nd = d.copy(); nd[0] = i
        for j, cb in enumerate(b, 1): nd[j] = min(d[j] + 1, nd[j - 1] + 1, d[j - 1] + (ca != cb))
        d = nd
    return d[-1] / len(a)
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small", device="cpu", chunk_length_s=30)
ref = norm(LYR)
for f in sys.argv[2:]:
    y, sr = sf.read(f); y = y.mean(1) if y.ndim > 1 else y; y = librosa.resample(y, orig_sr=sr, target_sr=16000).astype(np.float32)
    txt = asr(y, generate_kwargs={"language": "arabic", "task": "transcribe"})["text"]
    print(f"CER {cer(ref, norm(txt)):.3f} {f}\n   {txt}", flush=True)
