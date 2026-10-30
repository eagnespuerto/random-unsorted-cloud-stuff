"""Match SMOKA frames (tile files from smoka_tiles.py) to the 2026 EE138 position at each frame's
start time (Maunakea ephemeris). Reports the closest frame per instrument and every frame whose
field could contain the object. Adapted from ../other-missions/scripts/smoka_check.py.
usage: python smoka_check.py <ephemeris> <tile dir>   -> data/subaru_smoka.json"""
import glob, json, math, re, sys, numpy as np
from astropy.time import Time
L = open(sys.argv[1]).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
jd = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').jd for l in L])
RA = np.array([float(l.split(',')[3]) for l in L]); DE = np.array([float(l.split(',')[4]) for l in L])
V = np.array([float(l.split(',')[5]) for l in L])
def sep(a, b, c, d):
    a, b, c, d = map(math.radians, (a, b, c, d))
    return math.degrees(math.acos(min(1, math.sin(b)*math.sin(d) + math.cos(b)*math.cos(d)*math.cos(a-c))))
FOV = {'HSC': 0.75, 'SUP': 0.30, 'FCS': 0.06, 'MCS': 0.07, 'PFS': 0.7, 'HIC': 0.05, 'COM': 0.01, 'CIA': 0.01}
rx = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d+)\s+([+-]\d{2}:\d{2}:\d{2}\.\d+)\s+(\d{2}:\d{2}:\d{2}\.\d+|----)')
seen, rows = set(), []
for f in glob.glob(f"{sys.argv[2]}/t_*.txt"):
    for l in open(f, errors='ignore'):
        p = l.split()
        if len(p) < 10 or not re.fullmatch(r'[A-Z]{4}\d{8}', p[0]) or p[0] in seen: continue
        m = rx.search(l)
        if not m: continue
        seen.add(p[0])
        ra = sum(float(x) / 60**i for i, x in enumerate(m.group(1).split(':'))) * 15
        dd = m.group(2); de = (-1 if dd[0] == '-' else 1) * sum(float(x) / 60**i for i, x in enumerate(dd[1:].split(':')))
        t = Time(p[1] + 'T' + (m.group(3) if m.group(3) != '----' else '10:00:00.0')).jd
        if t < jd[0] or t > jd[-1]: continue
        d = sep(ra, de, np.interp(t, jd, RA), np.interp(t, jd, DE)); i3 = p[0][:3]
        rows.append(dict(sep=round(d, 4), margin=round(d - FOV.get(i3, 0.02), 4), frame=p[0], date=p[1], inst=i3,
                         obj=p[5], V=round(float(np.interp(t, jd, V)), 2), ra=round(ra, 5), dec=round(de, 5)))
print("frames:", len(rows))
best = {}
for r in sorted(rows, key=lambda r: r['margin']): best.setdefault(r['inst'], r)
for k, r in sorted(best.items(), key=lambda kv: kv[1]['margin']):
    print(f"{k}: sep {r['sep']:.3f} deg (reach {FOV.get(k, 0.02)}), {r['date']} {r['frame']} target {r['obj']} V={r['V']}")
hits = [r for r in rows if r['margin'] < 0]
print("frames whose field may contain the object:", len(hits))
for r in sorted(hits, key=lambda r: r['date'])[:60]: print('HIT', r)
json.dump(dict(best_per_inst=sorted(best.values(), key=lambda r: r['margin']), hits=hits), open('data/subaru_smoka.json', 'w'), indent=1)
