import subprocess,json,math,sys,time,os,datetime
from concurrent.futures import ThreadPoolExecutor
# usage: q3.py Y0 Y1  (inclusive years), uses ephd2.txt
y0,y1=int(sys.argv[1]),int(sys.argv[2])
def jd(y): return (datetime.datetime(y,1,1)-datetime.datetime(2000,1,1,12)).total_seconds()/86400+2451545.0
j0,j1=jd(y0)-30,jd(y1+1)+30
L=open('ephd2.txt').read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
E=[e for e in (tuple(map(float,l.split()[:3])) for l in L) if j0<=e[0]<=j1]
def sep(a,b,c,d):
    a,b,c,d=map(math.radians,(a,b,c,d));return math.degrees(math.acos(min(1,math.sin(b)*math.sin(d)+math.cos(b)*math.cos(d)*math.cos(a-c))))
pts=[E[0]]
for e in E[1:]:
    if sep(e[1],e[2],pts[-1][1],pts[-1][2])>0.5: pts.append(e)
D=f'raw_{y0}_{y1}'; os.makedirs(D,exist_ok=True)
N=len(pts); done=[0]; mark=[0]
def q(i):
    f=f'{D}/{i}.json'
    if not os.path.exists(f):
        e=pts[i]; rows=None
        for k in range(4):
            try:
                out=subprocess.run(["curl","-sS","-m","180","-X","POST","https://api.starglass.cfa.harvard.edu/public/dasch/dr7/queryexps","-H","Content-Type: application/json","-d",json.dumps({"ra_deg":e[1],"dec_deg":e[2]})],capture_output=True,text=True,check=True).stdout
                rows=json.loads(out); break
            except Exception as x: print(i,x,file=sys.stderr,flush=True); time.sleep(5)
        if rows is None: print(f"[{y0}-{y1}] FAIL point {i}",flush=True); return
        hdr=rows[0].split(','); keep=[]
        for row in rows[1:]:
            d=dict(zip(hdr,row.split(',')))
            if str(y0)<=d['expdate'][:4]<=str(y1): d['qra'],d['qdec']=e[1],e[2]; keep.append(d)
        json.dump(keep,open(f,'w'))
    done[0]+=1; p=done[0]*100//N
    if p>=mark[0]+10:
        mark[0]=p//10*10; print(f"[{y0}-{y1}] {mark[0]}% ({done[0]}/{N})",flush=True)
print(f"[{y0}-{y1}] start, {N} points",flush=True)
with ThreadPoolExecutor(6) as ex: list(ex.map(q,range(N)))
res={}
for i in range(N):
    try:
        for d in json.load(open(f'{D}/{i}.json')): res.setdefault("|".join((d['series'],d['platenum'],d['expnum'])),[]).append(d)
    except FileNotFoundError: pass
json.dump(res,open(f'plates_{y0}_{y1}.json','w')); print(f"[{y0}-{y1}] FINISHED, {len(res)} plates",flush=True)
