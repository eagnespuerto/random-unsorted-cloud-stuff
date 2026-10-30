import re,math,bisect,subprocess,json,sys
from astropy.io.votable import parse_single_table as P
def load(f,c0=1):
    out=[]
    for l in open(f).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines():
        t=l.split(); n=[x for x in t[1:] if re.fullmatch(r'-?\d+\.\d+',x)]; out.append((float(t[0]),float(n[0]),float(n[1])))
    return out
E=[e for e in load('ephd2.txt') if e[0]<2445335.5]+[e for e in load('irsa/eph_8399.txt') if e[0]<2451149.5]+load('sub/eph_mk.txt')
E.sort(); J=[e[0] for e in E]
def eph(mjd):
    jd=mjd+2400000.5
    if jd<J[0] or jd>J[-1]: return None
    i=max(0,min(len(E)-2,bisect.bisect(J,jd)-1)); f=jd-J[i]; a,b=E[i],E[i+1]; return a[1]+(b[1]-a[1])*f,a[2]+(b[2]-a[2])*f
def sep(a,b,c,d):
    a,b,c,d=map(math.radians,(a,b,c,d)); return math.degrees(math.acos(min(1,math.sin(b)*math.sin(d)+math.cos(b)*math.cos(d)*math.cos(a-c))))
T={ # table: (start col, end expr col or None, duration col (s), fov radius deg, label)
 'xmmmaster':('time','end_time',None,0.25,'XMM-Newton (EPIC/OM)'),
 'chanmaster':('time',None,'exposure',0.25,'Chandra'),
 'swiftmastr':('start_time','stop_time',None,0.2,'Swift XRT/UVOT'),
 'rosmaster':('start_time','end_time',None,None,'ROSAT pointed'),
 'suzamaster':('time','stop_time',None,0.15,'Suzaku'),
 'ascamaster':('time',None,'duration',0.4,'ASCA'),
 'exomaster':('time','end_time',None,1.0,'EXOSAT'),
 'xrismmastr':('time','end_time',None,0.3,'XRISM'),
 'ixmaster':('time','end_time',None,0.1,'IXPE'),
}
res={};hits=[]
for tab,(c0,c1,cd,fov,lab) in T.items():
    cols=f"ra,dec,{c0}"+(f",{c1}" if c1 else "")+(f",{cd}" if cd else "")+(",instrument" if tab=='rosmaster' else "")+",name"
    q=f"SELECT {cols} FROM {tab} WHERE ra BETWEEN 195 AND 285 AND dec BETWEEN -51 AND -35"
    subprocess.run(["curl","-sS","-m","300","-G","https://heasarc.gsfc.nasa.gov/xamin/vo/tap/sync","--data-urlencode","LANG=ADQL","--data-urlencode","REQUEST=doQuery","--data-urlencode",f"QUERY={q}","-o",f"xr/{tab}.xml"])
    try: t=P(f"xr/{tab}.xml").to_table()
    except Exception as e: print(lab,'query failed'); continue
    best=None; n=0
    for r in t:
        try: m0=float(r[c0])
        except Exception: continue
        if m0!=m0: continue
        m1=float(r[c1]) if c1 and r[c1]==r[c1] and r[c1] else m0+(float(r[cd])/86400 if cd and r[cd]==r[cd] else 0)
        if m1<m0 or m1-m0>30: m1=m0
        f=fov if fov else (1.0 if 'PSPC' in str(r['instrument']).upper() else 0.25)
        ds=[eph(m0+(m1-m0)*k/4) for k in range(5)]; ds=[d for d in ds if d]
        if not ds: continue
        n+=1; s=min(sep(d[0],d[1],float(r['ra']),float(r['dec'])) for d in ds)
        if s<f: hits.append(dict(mission=lab,target=str(r['name']),mjd0=m0,mjd1=m1,sep=round(s,3),fov=f,ra=float(r['ra']),dec=float(r['dec'])))
        if best is None or s-f<best[0]: best=(s-f,s,f,str(r['name']),m0)
    from astropy.time import Time
    res[lab]=dict(n_obs=n,closest_deg=round(best[1],2) if best else None,fov=best[2] if best else None,target=best[3] if best else None,date=Time(best[4],format='mjd').iso[:10] if best else None)
    print(lab,res[lab],flush=True)
json.dump(dict(summary=res,hits=hits),open('xr/pointed.json','w'),indent=1)
for h in hits: print('HIT',h)
