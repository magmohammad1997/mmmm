import sys, os, torch, json
from diffusers import StableDiffusionPipeline, LCMScheduler
torch.set_num_threads(4)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg")
pipe = StableDiffusionPipeline.from_pretrained("Lykon/dreamshaper-8", torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5"); pipe.fuse_lora()
STYLE = ("2D cartoon background art for a children's animated TV show, clean flat vector illustration, smooth gradients, bold clean shapes, "
         "bright saturated cheerful colors, cute, high quality, empty scene, no people, no characters, no animals, no text")
NEG = "people, person, girl, boy, child, animal, cat, character, text, watermark, logo, signature, ugly, blurry, dark, scary, realistic photo, 3d render"
SCENES = json.load(open(sys.argv[1]))
for name, desc, seeds in SCENES:
    for sd in seeds:
        f = f"{OUT}/{name}_{sd}.png"
        if os.path.exists(f): continue
        img = pipe(prompt=f"{desc}, {STYLE}", negative_prompt=NEG, num_inference_steps=6, guidance_scale=1.5,
                   width=544, height=960, generator=torch.Generator().manual_seed(sd)).images[0]
        img.save(f); print("saved", f, flush=True)
