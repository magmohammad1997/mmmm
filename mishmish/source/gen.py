import sys, os, time
ACE = "/tmp/claude-0/-home-user-mmmm/60bfbe50-aaa8-55f3-8b23-dc6b0da5b6af/scratchpad/ace"
sys.path.insert(0, ACE); os.chdir(ACE)
import torch; torch.set_num_threads(4)
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music
LYR = """[Intro]
مياو!

[Verse]
في ليلةٍ حلوةٍ فيها نجوم
مشمشُ القطّةُ فوقَ السطحِ تحوم
رأتْ قمرًا يضحكُ من بعيد
قالتْ: يا قمرُ.. سأصلُ أكيد!

[Chorus]
طيري طيري يا مشمشُ طيري
فوقَ الغيومِ إلى القمرِ سيري
مياو مياو.. والنجومُ تغنّي
يا قمرَ الليلِ اضحكْ وغنّي

[Verse 2]
صاروخٌ من كرتونٍ وقلبٌ كبير
وصلتْ.. وعادتْ بنجمةٍ تُنير

[Chorus]
طيري طيري يا مشمشُ طيري
فوقَ الغيومِ إلى القمرِ سيري
مياو مياو.. والنجومُ تغنّي
يا قمرَ الليلِ اضحكْ وغنّي
"""
CAP = ("Cheerful Arabic children's cartoon song, cute sweet young female vocal singing clearly in Arabic, "
       "bouncy happy kids pop, glockenspiel, ukulele, claps, soft piano, playful and catchy, bright and magical, clean mix")
dit = AceStepHandler()
t = time.time()
dit.initialize_service(project_root=ACE, config_path="acestep-v15-turbo", device="cpu")
print("init", time.time() - t, flush=True)
llm = LLMHandler()
_td = dit.tiled_decode
def _dec(lat, *a, **k):
    import gc
    dit.model = None; dit.text_encoder = None; gc.collect()   # free RAM before VAE decode (one take per process)
    return _td(lat, chunk_size=128, overlap=16, offload_wav_to_cpu=True)
dit.tiled_decode = _dec
import gc
out = sys.argv[1]; seeds = [int(s) for s in sys.argv[2:]] or [7]
for sd in seeds:
    t = time.time()
    p = GenerationParams(caption=CAP, lyrics=LYR, bpm=120, keyscale="C Major", timesignature="4", vocal_language="ar",
                         duration=60, inference_steps=8, seed=sd, thinking=False, use_cot_metas=False, use_cot_caption=False, use_cot_language=False)
    r = generate_music(dit, llm, p, GenerationConfig(batch_size=1, audio_format="wav", use_random_seed=False, seeds=[sd]), save_dir=out)
    gc.collect()
    print("seed", sd, r.success, r.error, [a.get("path") for a in r.audios], time.time() - t, flush=True)
