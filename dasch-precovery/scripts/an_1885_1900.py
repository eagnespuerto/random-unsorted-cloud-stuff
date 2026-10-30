import json,math,datetime,bisect
L=open('ephd.txt').read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
E=[tuple(map(float,(l.split()[0],l.split()[1],l.split()[2],l.split()[3]))) for l in L]
JD=[e[0] for e in E]
def eph(jd):
    i=max(0,min(len(E)-2,bisect.bisect(JD,jd)-1)); f=(jd-JD[i])
    a,b=E[i],E[i+1]; return tuple(a[k]+(b[k]-a[k])*f for k in (1,2,3))
def sep(a,b,c,d):
    a,b,c,d=map(math.radians,(a,b,c,d))
    return math.degrees(math.acos(min(1,math.sin(b)*math.sin(d)+math.cos(b)*math.cos(d)*math.cos(a-c))))
def jd(s):
    s=s.rstrip('Z'); t=datetime.datetime.fromisoformat(s)
    return (t-datetime.datetime(2000,1,1,12)).total_seconds()/86400+2451545.0
P=json.load(open('plates.json')); out=[]
for k,v in P.items():
    d=v[0]
    if not d['expdate']: continue
    j=jd(d['expdate']); ra,de,V=eph(j)
    # best margin: edgedist from each query point minus offset to object
    m=max(float(x['edgedist'])-sep(ra,de,x['qra'],x['qdec']) for x in v if x['edgedist'])
    cd=sep(ra,de,float(d['ra']),float(d['dec']))
    lim=d['limMagAtlas'] or d['limMagApass']
    if m>0: out.append((d['expdate'][:16],d['series'],d['platenum'],d['expnum'],d['exptime'],round(m,2),round(cd,2),lim,d['wcssource'],round(V,2),ra,de))
out.sort()
print(len(P),"plates pre-1901 near track;",len(out),"with object inside plate")
for o in out: print(*o[:10])
json.dump(out,open('covered.json','w'))
