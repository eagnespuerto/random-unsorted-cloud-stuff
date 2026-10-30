import subprocess,json,math,sys,time,os
from concurrent.futures import ThreadPoolExecutor
L=open('ephd.txt').read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
E=[tuple(map(float,l.split()[:3])) for l in L]
def sep(a,b,c,d):
    a,b,c,d=map(math.radians,(a,b,c,d));return math.degrees(math.acos(min(1,math.sin(b)*math.sin(d)+math.cos(b)*math.cos(d)*math.cos(a-c))))
pts=[E[0]]
for e in E[1:]:
    if sep(e[1],e[2],pts[-1][1],pts[-1][2])>0.5: pts.append(e)
os.makedirs('raw',exist_ok=True)
def q(i):
    f=f'raw/{i}.json'
    if os.path.exists(f): return
    e=pts[i]
    rows=None
    for k in range(4):
        try:
            out=subprocess.run(["curl","-sS","-m","180","-X","POST","https://api.starglass.cfa.harvard.edu/public/dasch/dr7/queryexps","-H","Content-Type: application/json","-d",json.dumps({"ra_deg":e[1],"dec_deg":e[2]})],capture_output=True,text=True,check=True).stdout
            rows=json.loads(out); break
        except Exception as x: print(i,x,file=sys.stderr,flush=True); time.sleep(5)
    if rows is None: print("fail",i,flush=True); return
    hdr=rows[0].split(','); keep=[]
    for row in rows[1:]:
        d=dict(zip(hdr,row.split(',')))
        if d['expdate'][:4]<'1901': d['qra'],d['qdec']=e[1],e[2]; keep.append(d)
    json.dump(keep,open(f,'w')); print("done",i,len(keep),flush=True)
print("points",len(pts),flush=True)
with ThreadPoolExecutor(4) as ex: list(ex.map(q,range(len(pts))))
res={}
for i in range(len(pts)):
    try:
        for d in json.load(open(f'raw/{i}.json')): res.setdefault("|".join((d['series'],d['platenum'],d['expnum'])),[]).append(d)
    except FileNotFoundError: pass
json.dump(res,open('plates.json','w')); print("FINISHED",len(res),flush=True)
