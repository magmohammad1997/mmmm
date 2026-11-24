import sys, soundfile as sf, librosa, numpy as np, json
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small", device="cpu")
x, sr = sf.read(sys.argv[1]); x = x if x.ndim == 1 else x.mean(1); x = librosa.resample(x, orig_sr=sr, target_sr=16000)
tm = json.load(open("timing.json"))
for L in tm["lines"]:
    a, b = int((L["start"] - .3) * 16000), int((L["end"] + .3) * 16000)
    r = asr(x[a:b].astype(np.float32), generate_kwargs={"language": "arabic", "task": "transcribe"})
    print(f'{L["text"]}  ==>  {r["text"]}')
