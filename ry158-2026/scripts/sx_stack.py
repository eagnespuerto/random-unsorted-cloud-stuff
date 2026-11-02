"""Template-subtracted SPHEREx stamps of 2026 RY158 centred on the JPL prediction (observer SPHEREx).
Per science frame: resample science + its reference frames (same band, same sky, >= 2 d away) onto a north-up
3" grid of +-HW", subtract the median reference, measure a 7" aperture with a 15-30" annulus, and record the
brightest residual peak within 60" (offset from prediction). Stacks per date group = clipped mean.
usage: python scripts/sx_stack.py  (from ry158-2026/)  -> data/sx_phot.json, data/sx_stamps.npz, stamp_grid.json"""
import bisect, glob, json, math, warnings
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.ndimage import map_coordinates, gaussian_filter
warnings.simplefilter("ignore")

L = open("data/eph_sx.txt").read().split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
E = [tuple(map(float, l.split()[:4])) for l in L]; J = [e[0] for e in E]
def eph(mjd):
    jd = mjd + 2400000.5; i = bisect.bisect(J, jd) - 1; a, b = E[i], E[i + 1]; f = (jd - a[0]) / (b[0] - a[0])
    return a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f, a[3]

PIX, HW = 3.0, 90                              # grid step and stamp half-width (arcsec)
g = np.arange(-HW, HW + PIX / 2, PIX) / 3600
GX, GY = np.meshgrid(g, g); R = np.hypot(GX, GY) * 3600
APER, ANN, SRCH = R <= 7.0, (R > 15) & (R <= 30), R <= 60

def load(f):
    z = np.load(f); return dict(img=z["img"], w=WCS(fits.Header.fromstring(str(z["hdr"]))), mjd=float(z["mjd"]))
def stamp(c, ra, dec):
    x, y = c["w"].world_to_pixel_values(ra + GX / math.cos(math.radians(dec)), dec + GY)
    ny, nx = c["img"].shape
    if x.min() < 0 or y.min() < 0 or x.max() > nx - 1 or y.max() > ny - 1: return None
    s = map_coordinates(c["img"], [y, x], order=1, mode="nearest")
    return None if np.isnan(s).mean() > 0.02 else s
def phot(d):                                   # MJy/sr summed over (3")^2 grid cells -> uJy
    return float(np.nansum(d[APER] - np.nanmedian(d[ANN])) * (PIX / 3600 * math.pi / 180) ** 2 * 1e12)

rows, stamps = [], {}
for f in sorted(glob.glob("sx/cut/*_sci_*.npz")):
    oid, band = f.split("/")[-1].split("_sci_")[0].rsplit("_", 1)
    c = load(f); ra, dec, V = eph(c["mjd"]); s = stamp(c, ra, dec)
    refs = [stamp(load(r), ra, dec) for r in glob.glob(f"sx/cut/{oid}_{band}_ref_*.npz")]
    refs = [r for r in refs if r is not None]
    if s is None or len(refs) < 3: print("skip", oid, band, len(refs)); continue
    d = s - np.nanmedian(refs, 0); d = np.nan_to_num(d - np.nanmedian(d))
    sm = gaussian_filter(d, 2); k = np.unravel_index(np.argmax(np.where(SRCH, sm, -np.inf)), sm.shape)
    rows.append(dict(oid=oid, band=band, mjd=c["mjd"], V=V, flux=phot(d), nref=len(refs),
                     peak_dE=round(float(GX[k] * 3600), 1), peak_dN=round(float(GY[k] * 3600), 1)))
    stamps[(oid, band)] = d; print(rows[-1], flush=True)

# empirical per-frame noise: aperture at 12 random blank offsets in each difference stamp
rng = np.random.default_rng(1)
def noise(d):
    v = []
    for _ in range(12):
        dx, dy = rng.uniform(-50, 50, 2)
        if math.hypot(dx, dy) < 25: continue
        sh = np.roll(np.roll(d, -int(round(dy / PIX)), 0), -int(round(dx / PIX)), 1); v.append(phot(sh))
    return float(np.std(v)) if len(v) > 3 else np.nan
for r in rows: r["err"] = noise(stamps[(r["oid"], r["band"])])
json.dump(rows, open("data/sx_phot.json", "w"), indent=1)

groups = [("D1", "2026-08-15", 61267, 61268), ("D1", "2026-08-22–24", 61274, 61277),
          ("D1", "2026-09-03–05", 61286, 61289), ("D1", "2026-09-08–09", 61291, 61293),
          ("D1", "2026-08-15–09-09", 0, 1e9), ("D4", "2026-08-15–09-09", 0, 1e9)]
LAM = {"D1": "0.75–1.09 µm", "D4": "2.42–3.82 µm"}
arrs, panels = {}, []
for band, lab, m0, m1 in groups:
    sel = [r for r in rows if r["band"] == band and m0 <= r["mjd"] < m1]
    if not sel: continue
    fl = np.array([r["flux"] for r in sel]); er = np.array([r["err"] for r in sel])
    med = np.median(fl); mad = 1.4826 * np.median(np.abs(fl - med)) or np.inf
    keep = [r for r, x in zip(sel, fl) if abs(x - med) <= 3 * mad] or sel
    F = np.array([r["flux"] for r in keep]); n = len(keep)
    err = F.std(ddof=1) / math.sqrt(n) if n > 3 else math.sqrt(np.nansum(np.array([r["err"] for r in keep]) ** 2)) / n
    img = np.mean([stamps[(r["oid"], r["band"])] for r in keep], 0)
    key = f"k{len(arrs)}"; arrs[key] = img - np.median(img[ANN])
    snr = F.mean() / err
    res = (f"{F.mean() / 1000:.2f} ± {err / 1000:.2f} mJy ({snr:.0f}σ)" if snr >= 3
           else f"{F.mean():.0f} ± {err:.0f} µJy, not detected")
    panels.append(dict(file="data/sx_stamps.npz", key=key, hw=HW, r=7.0, n=n,
                       title=f"SPHEREx {band} ({LAM[band]}), {lab}", subtitle=res))
    print(band, lab, n, round(F.mean(), 1), round(err, 1))
np.savez_compressed("data/sx_stamps.npz", **arrs)
json.dump(dict(title="2026 RY158", ncols=3, out="stamp_grid_2026RY158.png",
               subtitle="SPHEREx frames before discovery (template-subtracted, centred on JPL prediction)",
               panels=panels), open("stamp_grid.json", "w"), indent=1, ensure_ascii=False)
