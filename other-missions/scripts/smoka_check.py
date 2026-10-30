import re,math,bisect,collections,json
from astropy.time import Time
L=open('sub/eph_mk.txt').read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
E=[]
for l in L:
    t=l.split(); nums=[x for x in t[1:] if re.fullmatch(r'-?\d+\.\d+',x)]
    E.append((float(t[0]),float(nums[0]),float(nums[1]),float(nums[2]) if len(nums)>2 else None))
J=[e[0] for e in E]
def eph(jd):
    i=max(0,min(len(E)-2,bisect.bisect(J,jd)-1)); f=jd-J[i]; a,b=E[i],E[i+1]; return a[1]+(b[1]-a[1])*f,a[2]+(b[2]-a[2])*f,a[3]
def sep(a,b,c,d):
    a,b,c,d=map(math.radians,(a,b,c,d)); return math.degrees(math.acos(min(1,math.sin(b)*math.sin(d)+math.cos(b)*math.cos(d)*math.cos(a-c))))
FOV={'HSC':0.75,'SUP':0.30,'FCS':0.06,'MCS':0.07,'PFS':0.7}
rx=re.compile(r'(\d{2}:\d{2}:\d{2}\.\d+)\s+([+-]\d{2}:\d{2}:\d{2}\.\d+)\s+(\d{2}:\d{2}:\d{2}\.\d+|----)')
rows=[]
for l in open('sub/res.txt'):
    p=l.split()
    if len(p)<10 or not re.fullmatch(r'[A-Z]{4}\d{8}',p[0]): continue
    m=rx.search(l); ra=sum(float(x)/60**i for i,x in enumerate(m.group(1).split(':')))*15
    dd=m.group(2); de=(-1 if dd[0]=='-' else 1)*sum(float(x)/60**i for i,x in enumerate(dd[1:].split(':')))
    ut=m.group(3) if m.group(3)!='----' else '10:00:00.0'
    t=Time(p[1]+'T'+ut).jd; i3=p[0][:3]; ora,ode,V=eph(t); d=sep(ra,de,ora,ode)
    rows.append(dict(sep=d,margin=d-FOV.get(i3,0.02),frame=p[0],date=p[1],inst=i3,obj=p[5],V=V,ra=ra,dec=de))
print("frames:",len(rows))
best={}
for r in sorted(rows,key=lambda r:r['margin']): best.setdefault(r['inst'],r)
for k,r in sorted(best.items(),key=lambda kv:kv[1]['margin']): print(f"{k}: sep {r['sep']:.2f} deg (FOV reach {FOV.get(k,0.02)}), {r['date']} {r['frame']} target {r['obj']}")
json.dump(sorted(best.values(),key=lambda r:r['margin']),open('sub/best_per_inst.json','w'),indent=1)
