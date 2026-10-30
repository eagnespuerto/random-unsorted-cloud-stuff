"""Shift-and-stack 2026 EE138 in Pan-STARRS1 3pi warp cutouts (60", 0.25"/px, linear counts).
Per warp: flux in nJy via FPA.ZP and EXPTIME, north-up 0.25" grid centred on the JPL position,
local median removed. Per filter: clipped mean (3 sigma) over epochs; 1.5" aperture, 6-10" annulus.
Noise from the same stack at 8 control offsets 15" away. Also a combined g+r+i stack.
usage: python ps1_stack.py <ca bundle> <cutout dir>  -> data/ps1_stack.json, data/ps1_stamps.npz"""
import sys, os, json, subprocess, numpy as np, warnings
from concurrent.futures import ThreadPoolExecutor
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import map_coordinates
warnings.simplefilter("ignore")
ca, D = sys.argv[1:3]; os.makedirs(D, exist_ok=True)
W = json.load(open('data/ps1_warps.json'))
def get(w):
    f = f"{D}/{os.path.basename(w['file'])}"
    if not os.path.exists(f):
        u = f"https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?red={w['file']}&ra={w['obj_ra']}&dec={w['obj_dec']}&size=240&format=fits"
        for _ in range(3):
            if subprocess.run(["curl", "-sS", "-f", "--cacert", ca, "-m", "120", "-o", f, u]).returncode == 0: break
    return f
with ThreadPoolExecutor(8) as ex: files = list(ex.map(get, W))

HW, PIX = 40, 0.25                              # stamp +-10" on 0.25" grid
g = np.arange(-HW, HW + 1) * PIX / 3600; GX, GY = np.meshgrid(g, g)
R = np.hypot(GX, GY) * 3600; APER, ANN = R <= 1.5, (R >= 6) & (R <= 10)
def stamp(w, f, dx=0.0, dy=0.0):
    try: h = fits.open(f)
    except Exception: return None
    img = h[0].data.astype(float); H = h[0].header; wcs = WCS(H)
    if img is None or 'FPA.ZP' not in H: return None
    nJy = 3631e9 * 10 ** (-0.4 * (H['FPA.ZP'] + 2.5 * np.log10(H['EXPTIME'])))
    img = (img - np.nanmedian(img)) * nJy
    ra, de = w['obj_ra'] + dx / 3600 / np.cos(np.radians(w['obj_dec'])), w['obj_dec'] + dy / 3600
    x, y = wcs.world_to_pixel_values(ra + GX / np.cos(np.radians(de)), de + GY)
    s = map_coordinates(img, [y, x], order=1, cval=np.nan)
    return None if np.isnan(s[R <= 4]).any() else s
def clipmean(A):
    med = np.nanmedian(A, 0); mad = 1.4826 * np.nanmedian(np.abs(A - med), 0) + 1e-9
    return np.nanmean(np.where(np.abs(A - med) < 3 * mad, A, np.nan), 0)
phot = lambda S: float(np.nansum(S[APER]) - np.nanmedian(S[ANN]) * APER.sum())
SETS = {b: [i for i, w in enumerate(W) if w['filter'] == b and w['bad'] in ('0', '')] for b in 'grizy'}
SETS['gri'] = SETS['g'] + SETS['r'] + SETS['i']
res, stamps = {}, {}
for name, idx in SETS.items():
    def run(dx=0, dy=0):
        st = [s for s in (stamp(W[i], files[i], dx, dy) for i in idx) if s is not None]
        return (clipmean(np.array(st)), len(st)) if len(st) >= 3 else (None, len(st))
    S, n = run()
    if S is None: continue
    ctrl = [phot(run(15 * np.cos(a), 15 * np.sin(a))[0]) for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
    f, s = phot(S), float(np.std(ctrl))
    st_all = [x for x in (stamp(W[i], files[i]) for i in idx) if x is not None]
    Smed = np.nanmedian(np.array(st_all), 0)                     # median stack: robust to single bad epochs
    core = np.where(R <= 3, S - np.nanmedian(S[ANN]), 0); core[core < 0] = 0
    cx, cy = (float((core * GX).sum() / core.sum() * 3600), float((core * GY).sum() / core.sum() * 3600)) if core.sum() > 0 else (None, None)
    res[name] = dict(median_stack_snr=round(phot(Smed) / s, 2), centroid_offset_arcsec=None if cx is None else round(float(np.hypot(cx, cy)), 2), n=n, flux_nJy=round(f, 1), ctrl_sigma_nJy=round(s, 1), snr=round(f / s, 2),
                     mag_ab=round(31.4 - 2.5 * np.log10(f), 2) if f > 0 else None, lim3_ab=round(31.4 - 2.5 * np.log10(3 * s), 2))
    stamps[name] = S; print(name, res[name], flush=True)
json.dump(res, open('data/ps1_stack.json', 'w'), indent=1)
np.savez_compressed('data/ps1_stamps.npz', **stamps)

# jackknife: early vs late halves (by date) of the i and g+r+i epochs, same control noise scaled by sqrt(2)
for name in ('i', 'gri'):
    ok = [i for i in sorted(SETS[name], key=lambda i: W[i]['mjd']) if stamp(W[i], files[i]) is not None]
    for half, sel in (('early', ok[:len(ok) // 2]), ('late', ok[len(ok) // 2:])):
        Sh = clipmean(np.array([stamp(W[i], files[i]) for i in sel]))
        snr = phot(Sh) / (res[name]['ctrl_sigma_nJy'] * np.sqrt(2))
        res[name][f'{half}_snr'] = round(float(snr), 2)
        res[name][f'{half}_dates'] = f"{W[sel[0]]['date'][:10]} - {W[sel[-1]]['date'][:10]}"
    print(name, 'jackknife', {k: v for k, v in res[name].items() if 'early' in k or 'late' in k}, flush=True)
json.dump(res, open('data/ps1_stack.json', 'w'), indent=1)
