import subprocess,sys
VOW=set("a i u a. i. u. A I U @ e o".split())
def pho(text,voice="mb-ar1"):
    out=subprocess.run(["espeak-ng","-v",voice,"-q","--pho",text],capture_output=True,text=True).stdout
    ph=[]
    for l in out.splitlines():
        p=l.split()
        if not p: continue
        if p[0]=="_": continue
        ph.append(p[0])
    # merge consecutive identical vowels
    m=[]
    for x in ph:
        if m and x==m[-1] and isvowel(x): continue
        m.append(x)
    # glide handling
    out=[]
    for k,x in enumerate(m):
        if out and isvowel(x) and isvowel(out[-1]):
            base=x.rstrip('.:')
            nxtv = k+1<len(m) and isvowel(m[k+1])
            if base in ('i','u') and (nxtv or base!=out[-1].rstrip('.:')):
                out.append('j' if base=='i' else 'w'); continue
            if base not in ('i','u'):
                out.append('j' if out[-1].rstrip('.:')=='i' else 'w')
        out.append(x)
    return out
def isvowel(x): return x.rstrip(":").rstrip(".") in ("a","i","u","e","o","@")
def syllabify(ph):
    idx=[i for i,x in enumerate(ph) if isvowel(x)]
    if not idx: return [ph]
    syl=[]; start=0
    for k,v in enumerate(idx):
        if k+1<len(idx):
            nxt=idx[k+1]; cons=nxt-v-1
            end = v+1+max(0,cons-1)  # last consonant goes to next onset
        else: end=len(ph)
        syl.append(ph[start:end]); start=end
    return syl
if __name__=="__main__":
    for line in sys.argv[1:]:
        s=syllabify(pho(line)); print(len(s)," | ".join(" ".join(x) for x in s))
