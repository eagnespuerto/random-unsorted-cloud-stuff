import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from skyfield.api import load, EarthSatellite
ts=load.timescale()
a=np.radians((18+11/60+15.9665/3600)*15); d=-np.radians(42+13/60+18.988/3600)
e=np.array([-np.sin(a),np.cos(a),0]); n=np.array([-np.sin(d)*np.cos(a),-np.sin(d)*np.sin(a),np.cos(d)])
s=np.array([np.cos(d)*np.cos(a),np.cos(d)*np.sin(a),np.sin(d)])
RE=6378.; R=435.; SIG=7140.
CA=0.099/206265*47.7578*1.495978707e8
pa=np.radians(156.10); mv=np.radians(66.10)
P0=CA*np.array([np.sin(pa),np.cos(pa)]); vh=np.array([np.sin(mv),np.cos(mv)]); V=23.31
perp=np.array([vh[1],-vh[0]])  # cross-track unit (+ = toward PA 156, i.e. away from geocentre side)
dt=np.arange(-1800,1800.01,0.5); t=ts.utc(2026,10,31,1,21,43.1+dt)
L=open('tle/active.txt').read().splitlines()
tel="HST XMM-NEWTON SWIFT NUSTAR NEOSSAT ASTROSAT CHEOPS IXPE XRISM EINSTEIN SVOM SPHEREX PANDORA".split()
sats={}
for i in range(0,len(L)-2,3):
    nm=L[i].strip()
    if any(nm.startswith(x) for x in tel): sats[nm]=EarthSatellite(L[i+1],L[i+2],nm,ts)
offs=np.arange(-SIG,SIG+1,5.)
out={}
for nm,sat in sats.items():
    r=sat.at(t).position.km; xi=e@r; eta=n@r; z=s@r
    X=np.vstack([xi,eta])-P0[:,None]
    al=vh@X - V*dt; cr=perp@X
    vis=~((z<0)&(np.hypot(xi,eta)<RE))
    hit=[]
    for o in offs:
        m=(np.hypot(al,cr-o)<R)&vis
        if m.any(): hit.append(o)
    out[nm]=dict(xi=xi,eta=eta,al=al,cr=cr,vis=vis,hit=hit)
    if hit: print(f"{nm:20s} hit for cross-track shifts {min(hit):+.0f}..{max(hit):+.0f} km  ({(max(hit)-min(hit)+5)/(2*SIG)*100:.1f}% of ±1σ, ~{(max(hit)-min(hit)+5)/(2*SIG)*68.3:.1f}% chance if uniform... )")
    else: print(f"{nm:20s} no hit within ±1σ")
# Gaussian probability
from math import erf,sqrt
for nm,v in out.items():
    if v['hit']:
        h=np.array(v['hit']); p=np.sum(np.exp(-0.5*(h/SIG)**2))*5/(SIG*np.sqrt(2*np.pi))
        print(f"  {nm}: Gaussian P(hit) ≈ {p*100:.1f}%  (min |shift| {np.abs(h).min():.0f} km)")
fig,ax=plt.subplots(1,2,figsize=(15,7))
A=ax[0]; A.add_patch(plt.Circle((0,0),RE,fc='#eef',ec='k'))
u=np.linspace(-15000,15000,2); 
for o,sty,c in [(0,'-',2),(R,'-',1),(-R,'-',1)]:
    p=P0[:,None]+vh[:,None]*u+perp[:,None]*o; A.plot(p[0],p[1],'b',lw=c)
for o in (SIG,-SIG):
    p=P0[:,None]+vh[:,None]*u+perp[:,None]*o; A.plot(p[0],p[1],'r--')
col={'CHEOPS':'g','SPHEREX (MIDEX 9)':'m'}
for nm,c in col.items():
    v=out[nm]; w=np.abs(dt)<=900
    A.plot(v['xi'][w],v['eta'][w],c,lw=2,label=nm+' (±15 min)')
    for tt in range(-900,901,300):
        k=np.argmin(abs(dt-tt)); A.plot(v['xi'][k],v['eta'][k],c+'o',ms=4); A.annotate(f"{tt//60:+d}m",(v['xi'][k],v['eta'][k]),fontsize=8,color=c)
A.plot(*P0,'bo',ms=8); A.set_aspect('equal'); A.set_xlim(-14000,14000); A.set_ylim(-14000,14000)
A.set_title('Fundamental plane (E right, N up), times rel. 01:21:43 UTC'); A.legend(loc='upper left'); A.set_xlabel('ξ km'); A.set_ylabel('η km')
B=ax[1]
B.axhspan(-SIG,SIG,color='r',alpha=.07); B.axhline(SIG,color='r',ls='--'); B.axhline(-SIG,color='r',ls='--')
B.add_patch(plt.Circle((0,0),R,fc='b',alpha=.3)); B.axhline(0,color='b',lw=.5)
for nm,c in col.items():
    v=out[nm]; B.plot(v['al'],v['cr'],c,lw=2,label=nm)
    B.plot(np.where(v['vis'],np.nan,v['al']),v['cr'],'k',lw=3)
    for tt in range(-600,601,60):
        k=np.argmin(abs(dt-tt)); B.plot(v['al'][k],v['cr'][k],c+'.',ms=5)
        if tt%300==0: B.annotate(f"{tt//60:+d}m",(v['al'][k],v['cr'][k]),fontsize=8,color=c)
B.set_xlim(-12000,12000); B.set_ylim(-9000,9000); B.set_aspect('equal')
B.set_title('Satellite track relative to shadow centre\n(blue disk = shadow, red band = ±1σ path shift, black = star behind Earth)')
B.set_xlabel('along-track km'); B.set_ylabel('cross-track km (+ = PA 156° side)'); B.legend()
plt.tight_layout(); plt.savefig('occ_2026ED138_overlay.png',dpi=110)
