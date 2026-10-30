"""Draw each telescope's hit window against a sideways shift of the predicted path.
Run occ2.py's analysis first (same folder, needs tle/active.txt); writes hit_windows.svg."""
import numpy as np
src=open('occ2.py').read().split('fig,ax')[0].replace('print(','(lambda *a,**k:None)(')
exec(src)
rows=[]
for nm,v in out.items():
    if not v['hit']: continue
    h=np.array(v['hit']); mid=h.mean()
    m=(np.hypot(v['al'],v['cr']-mid)<R)&v['vis']; tmid=dt[m].mean()
    p=np.sum(np.exp(-0.5*(h/SIG)**2))*5/(SIG*np.sqrt(2*np.pi))
    rows.append((np.abs(h).min(),nm.split(' (')[0],h.min(),h.max(),tmid,p))
rows.sort()
miss=[n for n,v in out.items() if not v['hit']]
NAMES={'SPHEREX':'SPHEREx','ASTROSAT':'AstroSat','NUSTAR':'NuSTAR','NEOSSAT':'NEOSSat','PANDORA':'Pandora','EINSTEIN PROBE':'Einstein Probe','XMM-NEWTON':'XMM-Newton','HST':'Hubble','SWIFT':'Swift'}
nmf=lambda n:NAMES.get(n.split(' (')[0],n.split(' (')[0])
FG,MUTE,BG,SH,RED='#1b2433','#6b7688','#f7f9fc','#2f5fd0','#c8323c'
HI={'CHEOPS':'#1d8a4e','SPHEREx':'#b0329a'}
X0,X1,K0,K1=180,700,-9000,9000
X=lambda k:X0+(k-K0)/(K1-K0)*(X1-X0)
top,dy=200,32; yb=top+dy*len(rows)
W,H=860,yb+110
s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Cross-track path shift that would put each space telescope in the 2026 ED138 shadow; only CHEOPS is hit at the nominal path, and each telescope has under 5 percent chance within the plus or minus 1 sigma uncertainty." font-family="DejaVu Sans, Helvetica, Arial, sans-serif" style="color:{FG}">',
f'<rect width="{W}" height="{H}" fill="{BG}"/>',
f'<text x="{W/2:.0f}" y="30" font-size="12.5" font-weight="bold" text-anchor="middle" fill="#000">2026 ED138 occultation · 2026-10-31 01:21:43 UTC</text>',
f'<text x="{W/2:.0f}" y="48" font-size="12.5" text-anchor="middle" fill="#000">Which sideways shift of the predicted path puts each space telescope in the shadow</text>']
# nominal shadow band and sigma lines (behind everything)
s.append(f'<rect x="{X(-R):.1f}" y="70" width="{X(R)-X(-R):.1f}" height="{yb-70}" fill="{SH}" fill-opacity="0.14"/>')
s.append(f'<text x="{X(0):.1f}" y="66" font-size="11" text-anchor="middle" fill="{SH}">nominal path · shadow ≈870 km</text>')
for k,l in((-SIG,'−1σ'),(SIG,'+1σ')):
    s.append(f'<line x1="{X(k):.1f}" y1="78" x2="{X(k):.1f}" y2="{yb}" stroke="{RED}" stroke-width="1.5" stroke-dasharray="6 4"/>')
    s.append(f'<text x="{X(k):.1f}" y="90" font-size="11.5" text-anchor="middle" fill="{RED}" dx="{-14 if k<0 else 14}">{l}</text>')
# gaussian density lane
kk=np.linspace(K0,K1,181); g=np.exp(-0.5*(kk/SIG)**2)
pts=' '.join(f'{X(k):.1f},{140-g_*40:.1f}' for k,g_ in zip(kk,g))
s.append(f'<polyline points="{X(K0):.1f},140 {pts} {X(K1):.1f},140" fill="{RED}" fill-opacity="0.08" stroke="{RED}" stroke-width="1.2"/>')
s.append(f'<text x="{X0-10}" y="128" font-size="11.5" text-anchor="end" fill="{MUTE}">path likelihood</text>')
# Earth disk lane
ec=-CA; s.append(f'<rect x="{X(max(ec-RE,K0)):.1f}" y="160" width="{X(ec+RE)-X(max(ec-RE,K0)):.1f}" height="8" rx="2" fill="{MUTE}" fill-opacity="0.45"/>')
s.append(f'<line x1="{X(ec):.1f}" y1="155" x2="{X(ec):.1f}" y2="173" stroke="currentColor" stroke-width="1.2"/>')
s.append(f'<text x="{X(ec):.1f}" y="186" font-size="10.5" text-anchor="middle" fill="{MUTE}">Earth centre</text>')
s.append(f'<text x="{X0-10}" y="168" font-size="11.5" text-anchor="end" fill="{MUTE}">Earth\'s disk</text>')
s.append(f'<text x="{X1+20}" y="{top-12}" font-size="10.5" fill="{MUTE}">time*</text><text x="{X1+140}" y="{top-12}" font-size="10.5" text-anchor="end" fill="{MUTE}">P(hit)</text>')
for i,(mn,nm,a,b,tm,p) in enumerate(rows):
    nm=nmf(nm); y=top+dy*i+dy/2; c=HI.get(nm,MUTE); w='bold' if nm in HI else 'normal'
    s.append(f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" stroke="currentColor" stroke-opacity="0.1"/>')
    s.append(f'<text x="{X0-10}" y="{y+4}" font-size="12.5" font-weight="{w}" text-anchor="end" fill="{c if nm in HI else "currentColor"}">{nm}</text>')
    s.append(f'<rect x="{X(a):.1f}" y="{y-7}" width="{X(b)-X(a):.1f}" height="14" rx="3" fill="{c}"/>')
    lab=f'{a:+,.0f} to {b:+,.0f} km'.replace('-','−')
    lx,an=(X(b)+6,'start') if X(b)<X1-110 else (X(a)-6,'end')
    s.append(f'<text x="{lx:.1f}" y="{y+4}" font-size="10.5" text-anchor="{an}" fill="{MUTE}">{lab}</text>')
    tt=f'{int(round(tm)):+d} s'.replace('-','−')
    s.append(f'<text x="{X1+20}" y="{y+4}" font-size="11.5" fill="currentColor">{tt}</text><text x="{X1+140}" y="{y+4}" font-size="11.5" text-anchor="end" fill="currentColor">{p*100:.1f}%</text>')
# axis
s.append(f'<line x1="{X0}" y1="{yb}" x2="{X1}" y2="{yb}" stroke="currentColor"/>')
for k in range(-9000,9001,3000):
    s.append(f'<line x1="{X(k):.1f}" y1="{yb}" x2="{X(k):.1f}" y2="{yb+5}" stroke="currentColor"/><text x="{X(k):.1f}" y="{yb+18}" font-size="11" text-anchor="middle" fill="currentColor">'+(f'{k:+,d}' if k else '0').replace('-','−')+'</text>')
s.append(f'<text x="{X0}" y="{yb+38}" font-size="11.5" fill="currentColor">← north (toward Earth centre)</text><text x="{X1}" y="{yb+38}" font-size="11.5" text-anchor="end" fill="currentColor">south (away) →</text>')
s.append(f'<text x="{(X0+X1)/2}" y="{yb+38}" font-size="11.5" text-anchor="middle" fill="currentColor">path shift (km)</text>')
s.append(f'<text x="24" y="{yb+66}" font-size="10.5" fill="{MUTE}">No hit within ±1σ: {", ".join(nmf(n) for n in miss)}. *Time of crossing relative to 01:21:43 UTC, at the middle of the window.</text>')
s.append(f'<text x="24" y="{yb+84}" font-size="10.5" fill="{MUTE}">Shadow width and 1σ (±7,140 km) measured from the plot; sideways shift only; CelesTrak orbits ~1 day old; star must not be behind Earth.</text>')
s.append('</svg>')
open('hit_windows.svg','w').write('\n'.join(s))
for r in rows: print(r)
