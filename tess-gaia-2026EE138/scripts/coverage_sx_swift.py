"""Which SPHEREx L2 frames and Swift pointings contain 2026 EE138?
Inputs: Horizons ephemeris (data/eph_geo.txt), IRSA ObsCore SPHEREx rows (CSV),
HEASARC swiftmastr rows (CSV). Object position interpolated to each exposure mid-time."""
import csv, sys, json, math, numpy as np
from astropy.time import Time
from matplotlib.path import Path

eph, sxcsv, swcsv = sys.argv[1:4]
L = open(eph).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
mjd = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').mjd for l in L])
RA = np.array([float(l.split(',')[3]) for l in L]); DE = np.array([float(l.split(',')[4]) for l in L])
V = np.array([float(l.split(',')[5]) for l in L])
pos = lambda t: (np.interp(t, mjd, RA), np.interp(t, mjd, DE), np.interp(t, mjd, V))
def sep(a, b, c, d):
    a, b, c, d = map(math.radians, (a, b, c, d))
    return math.degrees(math.acos(min(1, math.sin(b)*math.sin(d) + math.cos(b)*math.cos(d)*math.cos(a-c))))

sx = []
for r in csv.DictReader(open(sxcsv)):
    t = (float(r['t_min']) + float(r['t_max'])) / 2
    if t < mjd[0] or t > mjd[-1]: continue
    ra, de, v = pos(t)
    p = list(map(float, r['s_region'].split()[2:])); xy = np.array(p).reshape(-1, 2)
    if Path(xy).contains_point((ra, de)):
        sx.append(dict(obs_id=r['obs_id'], band=r['energy_bandpassname'], mjd=t, date=Time(t, format='mjd').iso[:16],
                       ra=ra, dec=de, V=v, coll=r['obs_collection'], url=r['access_url']))
print(f'SPHEREx frames containing object: {len(sx)}')
for d in sorted({s["date"][:7] for s in sx}): print(' ', d, sum(s["date"][:7] == d for s in sx))

sw = []; best = (99, None)
for r in csv.DictReader(open(swcsv)):
    t0, t1 = float(r['start_time']), float(r['stop_time'] or r['start_time'])
    if t0 < mjd[0] or t0 > mjd[-1]: continue
    s = min(sep(*pos(t)[:2], float(r['ra']), float(r['dec'])) for t in np.linspace(t0, t1, 5))
    if s < best[0]: best = (s, r['name'], Time(t0, format='mjd').iso[:10])
    if s < 0.25:   # XRT ~0.2 deg radius, UVOT 17' square
        sw.append(dict(obsid=r['obsid'], target=r['name'], date=Time(t0, format='mjd').iso[:19], sep_deg=round(s, 3),
                       uvot_s=float(r['uvot_exposure'] or 0), xrt_s=float(r['xrt_exposure'] or 0), V=round(pos(t0)[2], 2)))
print(f'Swift obs within 0.25 deg: {len(sw)}; closest {best[0]:.2f} deg ({best[1]}, {best[2]})')
for s in sw: print(' ', s)
json.dump(dict(spherex=sx, swift=sw, swift_closest=best), open('data/coverage_sx_swift.json', 'w'), indent=1)
