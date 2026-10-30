"""Template-subtracted forced photometry + shift-and-stack of 2026 EE138 in SPHEREx L2 cutouts
(adapted from ../spherex-search/scripts/sx_stack.py). For each frame with the object on the cutout:
72" north-up stamp (2" grid) at the predicted position, minus the median of <=40 same-band, same-region
stamps taken when the object was >30" away; 7" aperture, 15-30" annulus. 6 control tracks 2' away.
usage: python sx_stack.py <ephemeris> <cutout dir>  -> data/sx_phot.json, data/sx_stamps.npz"""
import glob, json, math, sys, warnings, numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.ndimage import map_coordinates
warnings.simplefilter("ignore")

L = open(sys.argv[1]).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
EM = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').mjd for l in L])
ER = np.array([float(l.split(',')[3]) for l in L]); ED = np.array([float(l.split(',')[4]) for l in L])
eph = lambda m: (float(np.interp(m, EM, ER)), float(np.interp(m, EM, ED)))
def sep(a, b, c, d):
    a, b, c, d = map(math.radians, (a, b, c, d))
    return math.degrees(math.acos(min(1, math.sin(b)*math.sin(d) + math.cos(b)*math.cos(d)*math.cos(a-c))))

S, HW = 2.0 / 3600, 18
g = np.arange(-HW, HW + 1) * S; GX, GY = np.meshgrid(g, g); R = np.hypot(GX, GY) * 3600
APER, ANN = R <= 7.0, (R > 15) & (R <= 30)

C = []
for f in sorted(glob.glob(f"{sys.argv[2]}/*.npz")):
    z = np.load(f)
    C.append(dict(reg=f.split("/")[-1][0], band=str(z["band"]), mjd=float(z["mjd"]), img=z["img"], lam=z["lam"],
                  w=WCS(fits.Header.fromstring(str(z["hdr"])))))
print("cutouts:", len(C), file=sys.stderr)

def stamp(c, ra, dec):
    cd = math.cos(math.radians(dec)); x, y = c["w"].world_to_pixel_values(ra + GX / cd, dec + GY)
    ny, nx = c["img"].shape
    if x.min() < 1 or y.min() < 1 or x.max() > nx - 2 or y.max() > ny - 2: return None
    s = map_coordinates(c["img"], [y, x], order=1, mode="nearest"); return None if np.isnan(s).any() else s
phot = lambda d: float(np.nansum(d[APER] - np.nanmedian(d[ANN])) * (S * math.pi / 180) ** 2 * 1e12)  # MJy/sr -> uJy

def run(dra=0.0, ddec=0.0, keep=False):
    out, st = [], []
    for c in C:
        ra, dec = eph(c["mjd"]); ra += dra / math.cos(math.radians(dec)); dec += ddec
        sci = stamp(c, ra, dec)
        if sci is None: continue
        pool = [t for t in C if t is not c and t["band"] == c["band"] and t["reg"] == c["reg"]]
        np.random.default_rng(int(c["mjd"] * 1e5) % 2**32).shuffle(pool); tm = []
        for t in pool:
            if len(tm) >= 40: break
            ro, do = eph(t["mjd"]); ro += dra / math.cos(math.radians(do)); do += ddec
            if sep(ro, do, ra, dec) * 3600 < 30: continue
            s = stamp(t, ra, dec)
            if s is not None: tm.append(s)
        if len(tm) < 3: continue
        d = sci - np.median(tm, 0)
        x, y = c["w"].world_to_pixel_values(ra, dec)
        out.append(dict(reg=c["reg"], band=c["band"], mjd=c["mjd"], lam=float(c["lam"][int(round(float(y))), int(round(float(x)))]),
                        flux=phot(d), ntmpl=len(tm)))
        if keep: st.append(d)
    return out, st

obj, st = run(keep=True)
ctrl = []
for k in range(6):
    a = 2 * math.pi * k / 6; print("control", k, file=sys.stderr, flush=True)
    ctrl.append(run(2 / 60 * math.cos(a), 2 / 60 * math.sin(a))[0])

def clipped(A):
    A = np.array(A); med = np.median(A, 0); mad = 1.4826 * np.median(np.abs(A - med), 0) + 1e-12
    return np.nanmean(np.where(np.abs(A - med) < 4 * mad, A, np.nan), 0)
def wmean(rows):
    f = np.array([r["flux"] for r in rows]); m = np.median(f); mad = 1.4826 * np.median(np.abs(f - m))
    k = np.abs(f - m) < 4 * mad; return float(f[k].mean()), float(f[k].std() / math.sqrt(k.sum())), int(k.sum())
SEL = {"A_2025AprJun": lambda r: r["reg"] == "A", "B_2025Dec": lambda r: r["reg"] == "B",
       "C_2026May": lambda r: r["reg"] == "C", "all": lambda r: True}
res, stamps = {}, {}
for name, fsel in SEL.items():
    for bname, bs in (("short", "123"), ("long", "456")):          # D1-D3 0.75-2.4 um, D4-D6 2.4-5 um
        sel = lambda r: fsel(r) and r["band"][-1] in bs
        rows = [r for r in obj if sel(r)]
        if len(rows) < 3: continue
        f, e, n = wmean(rows); cs = [wmean([r for r in c if sel(r)])[0] for c in ctrl]
        res[f"{name}_{bname}"] = dict(n=n, flux_uJy=round(f, 2), err_uJy=round(e, 2), ctrl_scatter_uJy=round(float(np.std(cs)), 2))
        stamps[f"{name}_{bname}"] = clipped([s for r, s in zip(obj, st) if sel(r)])
        print(name, bname, res[f"{name}_{bname}"], file=sys.stderr)
json.dump(dict(summary=res, obj=obj), open("data/sx_phot.json", "w"), indent=1)
np.savez_compressed("data/sx_stamps.npz", **stamps)
