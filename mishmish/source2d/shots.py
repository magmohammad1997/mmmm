import json
T=json.load(open("../w/timing_v2.json"))
W,H=1080,1920
def cam(z0,z1,x0,y0,x1=None,y1=None): return [z0,z1,x0,x1 if x1 is not None else x0,y0,y1 if y1 is not None else y0]
G=lambda x,y,s=1.1,**k:dict(who='girl',x=x,y=y,s=s,**k)
C=lambda x,y,s=.95,**k:dict(who='cat',x=x,y=y,s=s,**k)
MG=[731,207,190]; MR=[700,200,205]
shots=[
 dict(t0=0,t1=3.4,bg='garden',moon=MG,title=1,cam=cam(1.0,1.06,540,960),actors=[G(360,1560,1.3,pose='wave',eyes='happy',enter=1),C(800,1570,1.1,pose='idle',enter=1)],fx=['sparkles']),
 dict(t0=3.4,t1=5.3,bg='glowgold',cam=cam(1.5,1.65,540,1180),punch=1,actors=[C(540,1700,1.3,pose='cheer',meow=1,eyes='open')],fx=['stars']),
 dict(t0=5.3,t1=7.4,bg='garden',moon=MG,cam=cam(1.25,1.15,420,1150),actors=[G(420,1560,1.1,pose='wave',eyes='auto')],fx=['sparkles']),
 dict(t0=7.4,t1=9.9,bg='glowpink',cam=cam(1.7,1.9,540,1100),punch=1,actors=[C(540,1650,1.3,pose='cheer',meow=1,eyes='happy')],fx=['hearts']),
 # verse 1
 dict(t0=9.9,t1=13.9,bg='garden',moon=MG,cam=cam(1.0,1.08,540,1000),actors=[G(-150,1540,1.3,pose='walk',vx=150,eyes='auto'),C(-470,1550,1.05,pose='walk',vx=150)]),
 dict(t0=13.9,t1=16.0,bg='roof',moon=MR,cam=cam(1.0,1.05,540,1000),actors=[C(150,1560,1.25,pose='walk',vx=200,eyes='open',lookY=-.5)]),
 dict(t0=16.0,t1=18.1,bg='glowblue',cam=cam(1.6,1.75,540,1100),punch=1,actors=[G(540,1640,1.25,pose='sing',eyes='auto')],fx=['stars']),
 dict(t0=18.1,t1=20.0,bg='roof',moon=MR,cam=cam(1.1,1.2,540,1150),actors=[G(330,1620,1.3,pose='think',eyes='open'),C(800,1620,1.05,pose='idle',lookY=-1,lookX=-.3)]),
 dict(t0=20.0,t1=22.1,bg='glow',moon=[540,900,330,'wink'],cam=cam(1.0,1.1,540,960),fx=['sparkles']),
 dict(t0=22.1,t1=23.7,bg='glowgold',cam=cam(1.5,1.6,540,1150),punch=1,actors=[G(380,1650,1.1,pose='cheer',eyes='happy'),C(760,1650,.95,pose='cheer',eyes='happy')]),
 # chorus 1
 dict(t0=23.7,t1=28.1,bg='sky',clouds=1,speed=1,cam=cam(1.0,1.08,540,1000),punch=1,actors=[G(350,1350,1.25,pose='fly',eyes='auto'),C(800,1200,1.05,pose='fly',eyes='happy')],fx=['sparkles']),
 dict(t0=28.1,t1=30.0,bg='glowpink',cam=cam(1.6,1.75,540,1120),punch=1,actors=[C(540,1650,1.3,pose='dance',meow=1,eyes='open')],fx=['hearts']),
 dict(t0=30.0,t1=32.6,bg='glow',cam=cam(1.25,1.35,540,1150),punch=1,actors=[G(370,1650,1.1,pose='dance',eyes='auto'),C(760,1650,.95,pose='dance',eyes='happy')],fx=['stars']),
 dict(t0=32.6,t1=34.6,bg='sky',clouds=1,speed=1,cam=cam(1.5,1.6,450,1000),actors=[G(450,1400,1.1,pose='fly',eyes='happy')],fx=['sparkles']),
 dict(t0=34.6,t1=37.6,bg='sky',clouds=1,moon=[540,520,260,'happy'],cam=cam(1.0,1.05,540,960),actors=[G(320,1500,1.2,pose='fly',eyes='auto'),C(790,1400,1.0,pose='fly',eyes='happy')]),
 # verse 2
 dict(t0=37.6,t1=41.8,bg='garden',moon=MG,cam=cam(1.0,1.06,540,1000),rocket=dict(x=560,y=1280,s=1.2,flame=99,lift=99),actors=[G(190,1590,1.15,pose='wave',eyes='auto'),C(905,1600,.95,pose='cheer',eyes='happy')]),
 dict(t0=41.8,t1=44.0,bg='garden',moon=MG,cam=cam(1.0,1.0,540,1000),rocket=dict(x=560,y=1280,s=1.2,flame=0.1,lift=0.8,riders=1)),
 dict(t0=44.0,t1=46.1,bg='sky',clouds=1,speed=1,cam=cam(1.0,1.1,540,960),rocket=dict(x=540,y=1300,s=1.1,flame=0,lift=99,riders=1),fx=['sparkles']),
 # chorus 2 on the moon
 dict(t0=46.1,t1=50.1,bg='moon',cam=cam(1.0,1.08,540,1050),punch=1,actors=[G(340,1580,1.3,pose='dance',eyes='auto'),C(800,1590,1.1,pose='dance',eyes='happy')],fx=['stars']),
 dict(t0=50.1,t1=52.6,bg='glowblue',cam=cam(1.6,1.7,540,1120),punch=1,actors=[G(540,1650,1.25,pose='sing',eyes='auto')],fx=['sparkles']),
 dict(t0=52.6,t1=55.2,bg='glowpink',cam=cam(1.35,1.45,540,1150),punch=1,actors=[G(380,1650,1.1,pose='cheer',eyes='happy'),C(760,1650,.95,pose='cheer',eyes='happy',meow=1)],fx=['hearts']),
 dict(t0=55.2,t1=60.0,bg='moon',end=1,cam=cam(1.0,1.1,540,1100),actors=[G(350,1580,1.3,pose='hug',eyes='happy'),C(800,1590,1.1,pose='idle',eyes='happy',holdStar=1)],fx=['sparkles']),
]
d=dict(dur=60,bpm=120,beat0=0.066,lines=T['lines'],shots=shots,bgs=dict(garden='bg/garden_1.png',roof='bg/roof_1.png',sky='bg/sky_1.png',moon='bg/moon_1.png'))
json.dump(d,open("data.json","w"),ensure_ascii=False)
print(len(shots))
