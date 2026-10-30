import json,glob,re,math,datetime,sys
exec(open('miss/check.py').read())
KEY=sys.argv[1] if len(sys.argv)>1 else 'SVOM'
fs=glob.glob('miss/gcn/x/archive.json/*.json')
sx=re.compile(r'(\d{1,2})[h: ]\s?(\d{1,2})[m: ]\s?(\d{1,2}(?:\.\d+)?)s?\s*,?\s*(?:Dec(?:l)?\.?\s*(?:\(J2000\))?\s*[:=]?\s*)?([+\-−]\s?\d{1,2})[d°: ]\s?(\d{1,2})[\'m: ]\s?(\d{1,2}(?:\.\d+)?)')
dg=re.compile(r'RA(?:,\s*Dec)?\s*(?:\(J2000(?:\.0)?\))?\s*[:=]\s*([0-9]{1,3}\.\d+)\s*(?:deg)?\s*,?\s*(?:Dec\s*(?:\(J2000(?:\.0)?\))?\s*[:=]\s*)?([+\-−]?\s?[0-9]{1,2}\.\d+)',re.I)
n=0;out=[]
for f in fs:
    c=json.load(open(f)); body=c.get('body','')+' '+c.get('subject','')
    if KEY not in body: continue
    t=c['createdOn']/1000; d=datetime.datetime.fromtimestamp(t,datetime.UTC)
    if d.year<2024 or (d.year==2024 and d.month<6): continue
    n+=1; jd=min(t/86400+2440587.5,J[-1]); ora,ode=eph(jd)
    pos=[]
    for m in sx.finditer(body):
        try:
            h,mi,s,dd,dm,ds=m.groups(); dd=dd.replace(' ','').replace('−','-'); sgn=-1 if dd.startswith('-') else 1
            ra=15*(int(h)+int(mi)/60+float(s)/3600); de=sgn*(abs(int(dd))+int(dm)/60+float(ds)/3600)
            if ra<360 and abs(de)<=90: pos.append((ra,de))
        except ValueError: pass
    for m in dg.finditer(body):
        try:
            ra=float(m.group(1)); de=float(m.group(2).replace(' ','').replace('−','-'))
            if ra<360 and abs(de)<=90: pos.append((ra,de))
        except ValueError: pass
    for ra,de in pos: out.append((sep(ra,de,ora,ode),c['circularId'],d.date().isoformat(),c['subject'][:80],ra,de))
out.sort()
print(f"{KEY}-mentioning circulars since 2024-06:",n,"; with parsed positions:",len(set(o[1] for o in out)))
seen=set()
for o in out:
    if o[1] in seen: continue
    seen.add(o[1]); print("%.2f deg"%o[0],o[1],o[2],o[3],"(%.3f,%.3f)"%(o[4],o[5]))
    if len(seen)>=8: break
