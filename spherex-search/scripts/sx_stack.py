"""Template-subtracted forced photometry + shift-and-stack of 2026 ED138 in SPHEREx L2 cutouts.
For every image where the object is on the cutout: sample a 72" stamp (2" grid, north up) centred on
the predicted position; subtract the median stamp of the same sky from same-band images taken when the
object was >30" away; measure aperture flux. Repeat at offset 'control' tracks for an empirical null."""
import bisect, glob, json, math, sys, warnings
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import map_coordinates
warnings.simplefilter("ignore")

L = open("eph_sx.txt").read().split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
E = [tuple(map(float, l.split()[:4])) for l in L]; J = [e[0] for e in E]
def eph(mjd):
    jd = mjd + 2400000.5; i = bisect.bisect(J, jd) - 1; f = jd - J[i]; a, b = E[i], E[i + 1]
    return a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f, a[3]
def sep(a, b, c, d):
    a, b, c, d = map(math.radians, (a, b, c, d))
    return math.degrees(math.acos(min(1, math.sin(b) * math.sin(d) + math.cos(b) * math.cos(d) * math.cos(a - c))))

S, HW = 2.0 / 3600, 18                       # 2" grid, +-36"
g = np.arange(-HW, HW + 1) * S
GX, GY = np.meshgrid(g, g)                    # GX = east offset (deg), GY = north offset
R = np.hypot(GX, GY) * 3600
APER, AN0, AN1 = R <= 7.0, (R > 15) & (R <= 30), None

C = []
for f in sorted(glob.glob("sx/cut/*.npz")):
    z = np.load(f, allow_pickle=False)
    w = WCS(fits.Header.fromstring(str(z["hdr"])))
    pa = w.proj_plane_pixel_area().value * (math.pi / 180) ** 2   # sr per pixel
    C.append(dict(f=f, reg=f.split("/")[-1].split("_")[0], band=str(z["band"]), mjd=float(z["mjd"]),
                  img=z["img"], var=z["var"], lam=z["lam"], w=w, pa=pa))
print("cutouts:", len(C), file=sys.stderr)

def stamp(c, ra, dec, arr):
    cd = math.cos(math.radians(dec))
    x, y = c["w"].world_to_pixel_values(ra + GX / cd, dec + GY)
    ny, nx = arr.shape
    if x.min() < 1 or y.min() < 1 or x.max() > nx - 2 or y.max() > ny - 2: return None
    return map_coordinates(arr, [y, x], order=1, mode="nearest")

def phot(d, c):
    """aperture sum in MJy/sr * grid-pixel -> uJy; grid pixel = (2")^2"""
    bg = np.nanmedian(d[AN0])
    return (np.nansum(d[APER] - bg)) * (S * math.pi / 180) ** 2 * 1e12

def run(dra=0.0, ddec=0.0, keep=False):
    out, stamps = [], []
    for c in C:
        ra, dec, V = eph(c["mjd"]); ra += dra / math.cos(math.radians(dec)); dec += ddec
        sci = stamp(c, ra, dec, c["img"])
        if sci is None or np.isnan(sci).any(): continue
        tmpl = []
        pool = [t for t in C if t is not c and t["band"] == c["band"] and t["reg"] == c["reg"]]
        rng = np.random.default_rng(int(c["mjd"] * 1e5) % 2**32); rng.shuffle(pool)
        for t in pool:
            if len(tmpl) >= 40: break
            if t is c or t["band"] != c["band"] or t["reg"] != c["reg"]: continue
            ro, do, _ = eph(t["mjd"]); ro += dra / math.cos(math.radians(do)); do += ddec
            if sep(ro, do, ra, dec) * 3600 < 30: continue
            s = stamp(t, ra, dec, t["img"])
            if s is not None and not np.isnan(s).any(): tmpl.append(s)
        if len(tmpl) < 3: continue
        T = np.median(tmpl, axis=0)
        d = sci - T
        x, y = c["w"].world_to_pixel_values(ra, dec)
        lam = float(c["lam"][int(round(float(y))), int(round(float(x)))])
        out.append(dict(band=c["band"], mjd=c["mjd"], lam=lam, flux=float(phot(d, c)), ntmpl=len(tmpl), V=V, reg=c["reg"]))
        if keep: stamps.append(d)
    return out, stamps

obj, st = run(keep=True)
ctrl = []
for k in range(6):
    a = 2 * math.pi * k / 6
    print('control', k, file=sys.stderr, flush=True)
    ctrl.append(run(dra=2 / 60 * math.cos(a), ddec=2 / 60 * math.sin(a))[0])
json.dump(dict(obj=obj, ctrl=ctrl), open("sx/phot.json", "w"))
np.save("sx/stamps.npy", np.array(st)); json.dump([o["band"] for o in obj], open("sx/stamp_bands.json", "w"))
print("done", len(obj), "object epochs", file=sys.stderr)
