"""Check which TESS sectors (1-134) put 2026 EE138 on silicon, using its
Horizons position at each sector's start, middle and end (mid +/- 13 d)."""
import sys, numpy as np
from astropy.time import Time
import tess_stars2px as t

eph = sys.argv[1] if len(sys.argv) > 1 else 'data/eph_geo.txt'
L = open(eph).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
jd = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').jd for l in L])
ra = np.array([float(l.split(',')[3]) for l in L]); de = np.array([float(l.split(',')[4]) for l in L])
V = np.array([float(l.split(',')[5]) for l in L])

sc = t.TESS_Spacecraft_Pointing_Data()
print('sector  date        offset  RA        Dec      V      cam ccd  col     row')
for i, sec in enumerate(sc.sectors):
    for off in (-13, 0, 13):
        T = sc.midtimes[i] + off
        if T < jd[0] or T > jd[-1]: continue
        r, d = np.interp(T, jd, ra), np.interp(T, jd, de)
        res = t.tess_stars2px_function_entry(0, r, d, scInfo=sc)
        for s, cam, ccd, col, row in zip(res[3], res[4], res[5], res[6], res[7]):
            if s == sec:
                print(f'{sec:5d}  {Time(T,format="jd").iso[:10]}  {off:+4d}  {r:8.4f} {d:+8.4f} {np.interp(T,jd,V):5.2f}   {cam}   {ccd}  {col:6.1f}  {row:6.1f}')
