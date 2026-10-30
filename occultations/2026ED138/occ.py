import numpy as np
from skyfield.api import load, EarthSatellite
ts=load.timescale()
a=np.radians((18+11/60+15.9665/3600)*15); d=-np.radians(42+13/60+18.988/3600)
e=np.array([-np.sin(a),np.cos(a),0]); n=np.array([-np.sin(d)*np.cos(a),-np.sin(d)*np.sin(a),np.cos(d)])
s=np.array([np.cos(d)*np.cos(a),np.cos(d)*np.sin(a),np.sin(d)])
CA=0.099/206265*47.7578*1.495978707e8
pa=np.radians(156.10); mv=np.radians(66.10)
P0=CA*np.array([np.sin(pa),np.cos(pa)]); V=23.31*np.array([np.sin(mv),np.cos(mv)])
dt=np.arange(-1200,1200.01,1.0)
t=ts.utc(2026,10,31,1,21,43.1+dt)
P=P0[:,None]+V[:,None]*dt
L=open('tle/active.txt').read().splitlines()
res=[]
for i in range(0,len(L)-2,3):
    sat=EarthSatellite(L[i+1],L[i+2],L[i].strip(),ts)
    r=sat.at(t).position.km
    xi=e@r; eta=n@r; z=s@r
    dist=np.hypot(xi-P[0],eta-P[1])
    k=dist.argmin()
    blocked=(z[k]<0 and np.hypot(xi[k],eta[k])<6378)
    res.append((dist[k],L[i].strip(),dt[k],blocked,(t[k]-sat.epoch)))
res.sort()
tel="HST XMM-NEWTON SWIFT NUSTAR NEOSSAT ASTROSAT CHEOPS IXPE XRISM EINSTEIN SVOM SPHEREX PANDORA".split()
for r in res:
    if any(r[1].startswith(x) for x in tel): print("%8.0f km  %-20s dt=%+5.0fs blocked=%s TLEage=%.1fd"%r)
print("closest any:",[("%.0f"%r[0],r[1],r[2]) for r in res[:5]])
