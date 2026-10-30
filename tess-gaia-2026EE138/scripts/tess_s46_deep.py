"""Sector 46 re-stack for 2026 EE138 (object moves only ~6 px, so a sector-median template eats it).
Per frame: template = median of frames where the object was >= EXCL px away (sampled at the same pixels),
north-up 21" stamp, clipped mean. Null tests: reversed motion, stationary, and 8 offset control tracks.
Also stacks by thirds of the sector to see where any signal comes from.
usage: python tess_s46_deep.py <ephemeris> <s46 cutout.fits>  -> data/tess_s46_deep.json, data/tess_s46_stamps.npz"""
import sys, json, numpy as np, warnings
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.ndimage import map_coordinates
warnings.simplefilter("ignore")

L = open(sys.argv[1]).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
jd = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').jd for l in L])
RA = np.array([float(l.split(',')[3]) for l in L]); DE = np.array([float(l.split(',')[4]) for l in L])
HW, AP, ZP, EXCL, PIX = 8, 1.5, 20.44, 2.0, 21.0 / 3600
yy, xx = np.mgrid[-HW:HW + 1, -HW:HW + 1]; R = np.hypot(xx, yy); APER, ANN = R <= AP, (R >= 4) & (R <= 7)

h = fits.open(sys.argv[2]); d = h[1].data; w = WCS(h[2].header)
t = d['TIME'] + 2457000; F = d['FLUX'].astype('f8'); q = d['QUALITY']
ok = (q == 0) & np.isfinite(t) & np.isfinite(F).all((1, 2))
b = np.nanmedian(F.reshape(len(t), -1), 1); ok &= b < np.nanpercentile(b[ok], 80)
t, F = t[ok], F[ok]; F = F - np.nanmedian(F.reshape(len(t), -1), 1)[:, None, None]
ny, nx = F.shape[1:]
# bin to 1-hour means: beats down noise cheaply and keeps templates fast
nb = int((t[-1] - t[0]) * 24) + 1; idx = ((t - t[0]) * 24).astype(int)
tb = np.array([t[idx == k].mean() for k in range(nb) if (idx == k).sum() >= 3])
Fb = np.array([F[idx == k].mean(0) for k in range(nb) if (idx == k).sum() >= 3])
ra0, de0 = np.interp(tb, jd, RA), np.interp(tb, jd, DE)
STAR = (165.84310, 4.50858)                                       # Gaia DR3 3815098193520100224, G = 12.5
far_star = np.hypot((ra0 - STAR[0]) * np.cos(np.radians(de0)), de0 - STAR[1]) * 3600 > 60
tb, Fb, ra0, de0 = tb[far_star], Fb[far_star], ra0[far_star], de0[far_star]
x0, y0 = w.world_to_pixel_values(ra0, de0)
print('hour bins:', len(tb), 'track px:', round(float(np.hypot(x0[-1]-x0[0], y0[-1]-y0[0])), 2), file=sys.stderr)

def clipmean(A):
    med = np.nanmedian(A, 0); mad = 1.4826 * np.nanmedian(np.abs(A - med), 0) + 1e-9
    return np.nanmean(np.where(np.abs(A - med) < 3 * mad, A, np.nan), 0)

def stack(rate=1.0, dx=0, dy=0, sel=None):
    """rate=1 follows the object, -1 reverses its motion about mid-sector, 0 is stationary."""
    m = len(tb) // 2; S = []
    ra = ra0[m] + rate * (ra0 - ra0[m]) ; de = de0[m] + rate * (de0 - de0[m])
    X0, Y0 = w.world_to_pixel_values(ra, de)
    for k in (range(len(tb)) if sel is None else sel):
        dd = de[k] + (yy + dy) * PIX
        X, Y = w.world_to_pixel_values(ra[k] + (xx + dx) * PIX / np.cos(np.radians(dd)), dd)
        if X.min() < 0 or Y.min() < 0 or X.max() > nx - 1 or Y.max() > ny - 1: continue
        far = np.hypot(X0 - X0[k], Y0 - Y0[k]) >= EXCL           # template frames: object (or test track) away
        if far.sum() < 10: continue
        T = np.median(Fb[far], 0)
        S.append(map_coordinates(Fb[k] - T, [Y, X], order=1))
    if len(S) < 5: return np.nan, None, len(S)
    S = clipmean(np.array(S)); return float(np.nansum(S[APER] - np.nanmedian(S[ANN]))), S, len(S)

fl, S, n = stack()
ctrl = [stack(dx=12 * np.cos(a), dy=12 * np.sin(a))[0] for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
sig = float(np.nanstd(ctrl))
res = dict(n_hour_bins=n, flux_e_s=round(fl, 3), ctrl_sigma_e_s=round(sig, 3), snr=round(fl / sig, 2),
           T_3sigma_limit=round(ZP - 2.5 * np.log10(3 * sig), 2), T_pred=22.23,
           expected_flux_e_s=round(10 ** (-0.4 * (22.23 - ZP)), 3))
st = {'s46_deep': S}
for name, r in (('reversed', -1.0), ('stationary', 0.0)):
    f2, S2, _ = stack(rate=r); res[f'{name}_snr'] = round(f2 / sig, 2); st[f's46_{name}'] = S2
thirds = np.array_split(np.arange(len(tb)), 3)
res['thirds_snr'] = [round(stack(sel=s)[0] / (sig * np.sqrt(3)), 2) for s in thirds]
# closest bright Gaia stars to the track (from gaia_s46.csv if given)
if len(sys.argv) > 3:
    import csv
    for r in csv.DictReader(open(sys.argv[3])):
        if float(r['phot_g_mean_mag']) > 15: continue
        dmin = np.min(np.hypot((ra0 - float(r['ra'])) * np.cos(np.radians(de0)), de0 - float(r['dec'])) * 3600)
        res.setdefault('bright_stars', []).append(dict(G=round(float(r['phot_g_mean_mag']), 2), closest_arcsec=round(float(dmin), 1)))
print(json.dumps(res, indent=1))
json.dump(res, open('data/tess_s46_deep.json', 'w'), indent=1)
np.savez_compressed('data/tess_s46_stamps.npz', **st)
