"""SDSS imaging fields (SkyServer DR18 Field table) that contained 2026 EE138 at their r-band time.
Field bounds raMin/raMax/decMin/decMax are used directly (fields are 10x13.5 arcmin).
usage: python sdss_check.py <APO ephemeris> <fields.csv>  -> data/sdss_fields_with_object.json"""
import csv, sys, json, numpy as np
from astropy.time import Time
L = open(sys.argv[1]).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
mjd = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').mjd for l in L])
c = lambda k: np.array([float(l.split(',')[k]) for l in L])
RA, DE, V, U1 = c(3), c(4), c(5), c(7)
rows = [r for r in csv.DictReader(l for l in open(sys.argv[2]) if not l.startswith('#'))]
hits, best = [], (99, None)
for r in rows:
    t = float(r['mjd_r'])
    if t < mjd[0] or t > mjd[-1]: continue
    ra, de = np.interp(t, mjd, RA), np.interp(t, mjd, DE)
    a0, a1, d0, d1 = (float(r[k]) for k in ('raMin', 'raMax', 'decMin', 'decMax'))
    dist = np.hypot(max(a0 - ra, 0, ra - a1) * np.cos(np.radians(de)), max(d0 - de, 0, de - d1))
    if dist < best[0]: best = (dist, r, ra, de, t)
    if dist == 0:
        hits.append(dict(run=int(r['run']), rerun=r['rerun'], camcol=int(r['camcol']), field=int(r['field']), mjd_r=t,
                         date=Time(t, format='mjd').iso[:19], obj_ra=round(float(ra), 5), obj_dec=round(float(de), 5),
                         V=round(float(np.interp(t, mjd, V)), 2), unc3sig_arcsec=round(float(np.interp(t, mjd, U1)), 1),
                         quality=int(r['quality'])))
print(len(rows), 'fields;', len(hits), 'contain the object')
for h in hits: print(h)
if not hits: print('closest: %.3f deg' % best[0], best[1]['run'], best[1]['camcol'], best[1]['field'], Time(best[4], format='mjd').iso[:10])
json.dump(hits, open('data/sdss_fields_with_object.json', 'w'), indent=1)
