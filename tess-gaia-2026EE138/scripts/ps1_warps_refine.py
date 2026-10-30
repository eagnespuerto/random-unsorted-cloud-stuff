"""Second pass for ps1_warps.py: for every distinct exposure MJD found, ask ps1filenames.py for warps
at the object's exact position at that MJD, so each epoch comes from the skycell that contains it.
usage: python ps1_warps_refine.py <ephemeris> <ca bundle>  (rewrites data/ps1_warps.json)"""
import sys, json, subprocess, numpy as np
from astropy.time import Time
from concurrent.futures import ThreadPoolExecutor
eph, ca = sys.argv[1:3]
L = open(eph).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
mjd = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').mjd for l in L])
RA = np.array([float(l.split(',')[3]) for l in L]); DE = np.array([float(l.split(',')[4]) for l in L])
V = np.array([float(l.split(',')[5]) for l in L])
old = json.load(open('data/ps1_warps.json'))
epochs = sorted({round(w['mjd'], 5) for w in old})
def ask(t):
    r, d = float(np.interp(t, mjd, RA)), float(np.interp(t, mjd, DE))
    txt = subprocess.run(["curl", "-sS", "--cacert", ca, "-m", "120",
                          f"https://ps1images.stsci.edu/cgi-bin/ps1filenames.py?ra={r}&dec={d}&type=warp"], capture_output=True, text=True).stdout
    out = []
    for l in txt.splitlines()[1:]:
        p = l.split()
        if len(p) >= 9 and abs(float(p[5]) - t) < 1e-4:
            out.append(dict(file=p[7], skycell=f"{p[0]}.{int(p[1]):03d}", filter=p[4], mjd=float(p[5]), date=Time(float(p[5]), format='mjd').iso[:19],
                            obj_ra=round(r, 5), obj_dec=round(d, 5), V=round(float(np.interp(t, mjd, V)), 2), bad=p[9] if len(p) > 9 else ''))
    return out
with ThreadPoolExecutor(6) as ex: res = list(ex.map(ask, epochs))
W = {}
for o in res:
    for w in o: W[w['file']] = w
W = sorted(W.values(), key=lambda w: w['mjd'])
import collections
print(len(epochs), 'epochs ->', len(W), 'warps at exact position;', sum(1 for o in res if not o), 'epochs with none')
print(collections.Counter(w['filter'] for w in W))
json.dump(W, open('data/ps1_warps.json', 'w'), indent=1)
