"""List Pan-STARRS1 3pi warp images that contain 2026 EE138 at their epoch.
Queries ps1filenames.py (type=warp) at track positions every ~0.1 deg for 2009-2015, keeps warps whose
skycell (at that position) was observed when the object was within 0.15 deg of the query point,
then re-checks each kept warp's MJD against the ephemeris. Output: data/ps1_warps.json
usage: python ps1_warps.py <ephemeris> <ca bundle>"""
import sys, json, subprocess, numpy as np
from astropy.time import Time
eph, ca = sys.argv[1:3]
L = open(eph).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
mjd = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').mjd for l in L])
RA = np.array([float(l.split(',')[3]) for l in L]); DE = np.array([float(l.split(',')[4]) for l in L])
V = np.array([float(l.split(',')[5]) for l in L])
sel = (mjd > 54900) & (mjd < 57400)                      # 2009-03 .. 2016-01
pts, last = [], None
for m, r, d in zip(mjd[sel], RA[sel], DE[sel]):
    if last is None or np.hypot((r - last[0]) * np.cos(np.radians(d)), d - last[1]) > 0.1: pts.append((r, d)); last = (r, d)
print(len(pts), 'query points', file=sys.stderr)
warps = {}
for r, d in pts:
    txt = subprocess.run(["curl", "-sS", "--cacert", ca, "-m", "120",
                          f"https://ps1images.stsci.edu/cgi-bin/ps1filenames.py?ra={r}&dec={d}&type=warp"], capture_output=True, text=True).stdout
    for l in txt.splitlines()[1:]:
        p = l.split()
        if len(p) < 9: continue
        t = float(p[5]); ro, do = np.interp(t, mjd, RA), np.interp(t, mjd, DE)
        if np.hypot((ro - r) * np.cos(np.radians(d)), do - d) < 0.15:
            warps[p[8]] = dict(file=p[7], skycell=f"{p[0]}.{int(p[1]):03d}", filter=p[4], mjd=t, date=Time(t, format='mjd').iso[:19],
                               obj_ra=round(float(ro), 5), obj_dec=round(float(do), 5), V=round(float(np.interp(t, mjd, V)), 2), bad=p[9] if len(p) > 9 else '')
W = sorted(warps.values(), key=lambda w: w['mjd'])
print(len(W), 'warps')
import collections
print(collections.Counter(w['filter'] for w in W)); print(collections.Counter(w['date'][:4] for w in W))
json.dump(W, open('data/ps1_warps.json', 'w'), indent=1)
