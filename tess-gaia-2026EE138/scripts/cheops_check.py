"""Closest CHEOPS visit to 2026 EE138 (ESASky observations.mv_cheops_obs_fdw, all public visits).
CHEOPS field ~0.3 deg wide (1024 px x 1"), science window ~200" across.
usage: python cheops_check.py <ephemeris> <cheops.csv>"""
import csv, sys, math, numpy as np
from astropy.time import Time
L = open(sys.argv[1]).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
jd = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').jd for l in L])
RA = np.array([float(l.split(',')[3]) for l in L]); DE = np.array([float(l.split(',')[4]) for l in L])
def sep(a, b, c, d):
    a, b, c, d = map(math.radians, (a, b, c, d))
    return math.degrees(math.acos(min(1, math.sin(b)*math.sin(d) + math.cos(b)*math.cos(d)*math.cos(a-c))))
rows = []
for r in csv.DictReader(open(sys.argv[2])):
    t0, t1 = Time(r['v_start_u']).jd, Time(r['v_stop_u']).jd
    s = min(sep(np.interp(t, jd, RA), np.interp(t, jd, DE), float(r['ra_deg']), float(r['dec_deg'])) for t in np.linspace(t0, t1, 5))
    rows.append((s, r['targname'], r['v_start_u'][:10], r['obs_id']))
rows.sort(); print('visits:', len(rows), '| date range:', min(r[2] for r in rows), '-', max(r[2] for r in rows))
for r in rows[:5]: print(f'{r[0]:7.2f} deg  {r[1]:20s} {r[2]}  obs {r[3]}')
