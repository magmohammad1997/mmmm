import soundfile as sf, numpy as np, json, sys
from scipy import signal
x,sr=sf.read(sys.argv[1]); x=x if x.ndim==1 else x.mean(1)
b,a=signal.butter(2,[300/(sr/2),3000/(sr/2)],'band'); y=signal.lfilter(b,a,x)
hop=sr//30; e=np.array([np.sqrt((y[i*hop:(i+1)*hop]**2).mean()) for i in range(1800)])
e=e/np.percentile(e[e>0],95); m=np.clip((e-.08)/.7,0,1)**.8
json.dump([round(float(v),3) for v in m],open('mouth.json','w'))
