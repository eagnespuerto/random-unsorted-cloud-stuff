"""Astrometry of 2026 RY158 in SPHEREx D1 frames, tied to Gaia DR3 per frame.
Per science frame, in native detector pixels:
  1. template = median of the reference frames resampled onto the science pixel grid (via WCS), diff = sci - template
  2. 2-D Gaussian + constant fit to the object in diff, within 3 px of the JPL (observer SPHEREx) prediction
  3. same fit to Gaia DR3 stars (G 10.5-16.5, isolated, propagated to epoch) in the science image ->
     median WCS offset (applied to the object) and its scatter
Output: data/sx_astrometry.json.  usage: python scripts/sx_astrometry.py  (from ry158-2026/)"""
import bisect, glob, io, json, math, subprocess, warnings
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.ndimage import map_coordinates
from scipy.optimize import curve_fit
warnings.simplefilter("ignore")

L = open("data/eph_sx.txt").read().split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
E = [tuple(map(float, l.split()[:3])) for l in L]; J = [e[0] for e in E]
def eph(mjd):
    jd = mjd + 2400000.5; i = bisect.bisect(J, jd) - 1; a, b = E[i], E[i + 1]; f = (jd - a[0]) / (b[0] - a[0])
    return a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f

def load(f):
    z = np.load(f); return z["img"].astype("f8"), WCS(fits.Header.fromstring(str(z["hdr"]))), float(z["mjd"])

def g2(xy, a, x0, y0, s, c):
    x, y = xy; return (a * np.exp(-((x - x0) ** 2 + (y - y0) ** 2) / (2 * s * s)) + c).ravel()

def fit(img, x, y, box=4):
    """Gaussian fit around pixel (x, y); returns (x0, y0, sx0, sy0, sigma_px, amp, snr) or None."""
    x, y = float(x), float(y); ix, iy = int(round(x)), int(round(y)); ny, nx = img.shape
    if ix - box < 0 or iy - box < 0 or ix + box >= nx or iy + box >= ny: return None
    sub = img[iy - box:iy + box + 1, ix - box:ix + box + 1]
    if not np.isfinite(sub).all(): return None
    yy, xx = np.mgrid[iy - box:iy + box + 1, ix - box:ix + box + 1]
    try:
        p, cov = curve_fit(g2, (xx, yy), sub.ravel(), p0=[sub.max() - np.median(sub), x, y, 0.6, np.median(sub)])
    except Exception:
        return None
    res = sub.ravel() - g2((xx, yy), *p); rms = res.std()
    cov = cov * 1.0                                        # curve_fit already scales by residual variance
    if not (0.3 < abs(p[3]) < 1.5) or p[0] <= 0 or np.hypot(p[1] - x, p[2] - y) > 2: return None
    return p[1], p[2], math.sqrt(cov[1, 1]), math.sqrt(cov[2, 2]), abs(p[3]), p[0], p[0] / rms

def gaia(ra, dec, rad):
    q = ("SELECT ra,dec,pmra,pmdec,phot_g_mean_mag FROM gaiadr3.gaia_source WHERE "
         f"1=CONTAINS(POINT(ra,dec),CIRCLE({ra},{dec},{rad})) AND phot_g_mean_mag BETWEEN 9 AND 16.5")
    out = subprocess.run(["curl", "-sSf", "--retry", "5", "--retry-all-errors", "https://gea.esac.esa.int/tap-server/tap/sync",
                          "--data-urlencode", "REQUEST=doQuery", "--data-urlencode", "LANG=ADQL",
                          "--data-urlencode", "FORMAT=csv", "--data-urlencode", f"QUERY={q}"],
                         capture_output=True, text=True, check=True).stdout
    return np.genfromtxt(io.StringIO(out), delimiter=",", names=True)

PX = 6.15                                                  # arcsec per pixel (approx, for errors)
rows = []
for f in sorted(glob.glob("sx/cut/*_D1_sci_*.npz")):
    oid = f.split("/")[-1].split("_D1_sci_")[0]
    sci, w, mjd = load(f); ny, nx = sci.shape
    yy, xx = np.mgrid[:ny, :nx]; RA, DE = w.pixel_to_world_values(xx, yy)
    T = []
    for r in glob.glob(f"sx/cut/{oid}_D1_ref_*.npz"):
        im, wr, _ = load(r); X, Y = wr.world_to_pixel_values(RA, DE)
        T.append(map_coordinates(im, [Y, X], order=1, cval=np.nan))
    diff = sci - np.nanmedian(T, 0); diff -= np.nanmedian(diff)
    ra0, de0 = eph(mjd); x0, y0 = w.world_to_pixel_values(ra0, de0)
    # start the fit from the brightest diff pixel within 3 px of the prediction
    m = (np.hypot(xx - x0, yy - y0) <= 3) & np.isfinite(diff)
    k = np.argmax(np.where(m, diff, -np.inf)); o = fit(diff, xx.flat[k], yy.flat[k])
    if o is None or o[6] < 5: print(oid, "object fit failed or S/N < 5"); continue
    # Gaia tie on the science image
    rc, dc = w.pixel_to_world_values(nx / 2, ny / 2)
    G = gaia(float(rc), float(dc), 0.085); dt = (Time(mjd, format="mjd").jyear - 2016.0)
    gra = G["ra"] + np.nan_to_num(G["pmra"]) * dt / 3.6e6 / np.cos(np.radians(G["dec"]))
    gde = G["dec"] + np.nan_to_num(G["pmdec"]) * dt / 3.6e6
    dE, dN, fw = [], [], []
    for i in range(len(G)):
        d = np.hypot((gra - gra[i]) * np.cos(np.radians(gde[i])), gde - gde[i]) * 3600
        if np.sort(d)[1] < 20 or G["phot_g_mean_mag"][i] < 10.5 or G["phot_g_mean_mag"][i] > 16.5: continue  # isolated only
        sx, sy = w.world_to_pixel_values(gra[i], gde[i]); s = fit(sci, sx, sy)
        if s is None or s[6] < 20: continue
        fw.append(2.355 * s[4] * PX)
        mr, md = w.pixel_to_world_values(s[0], s[1])
        dE.append((gra[i] - mr) * math.cos(math.radians(gde[i])) * 3600); dN.append((gde[i] - md) * 3600)
    dE, dN = np.array(dE), np.array(dN)
    if len(dE) < 4: print(oid, "too few Gaia stars", len(dE)); continue
    cE, cN = np.median(dE), np.median(dN)
    sE, sN = 1.4826 * np.median(np.abs(dE - cE)), 1.4826 * np.median(np.abs(dN - cN))
    ora, ode = w.pixel_to_world_values(o[0], o[1])
    ra = float(ora + cE / 3600 / math.cos(math.radians(ode))); dec = float(ode + cN / 3600)
    # error: centroid (fit) + tie (scatter/sqrt n) in quadrature, 0.3" floor for SIP/PSF systematics
    eR = math.sqrt((o[2] * PX) ** 2 + sE ** 2 / len(dE) + 0.3 ** 2)
    eD = math.sqrt((o[3] * PX) ** 2 + sN ** 2 / len(dN) + 0.3 ** 2)
    rows.append(dict(oid=oid, mjd_utc_mid=mjd, ra=ra, dec=dec, rmsRA=round(eR, 2), rmsDec=round(eD, 2),
                     snr=round(float(o[6]), 1), fwhm_arcsec=round(float(2.355 * o[4] * PX), 1), star_fwhm_arcsec=round(float(np.median(fw)), 1), nstars=int(len(dE)),
                     tie_dE=round(float(cE), 2), tie_dN=round(float(cN), 2), star_rms_E=round(float(sE), 2), star_rms_N=round(float(sN), 2),
                     pred_dE=round(float((ra - ra0) * math.cos(math.radians(dec)) * 3600), 2), pred_dN=round(float((dec - de0) * 3600), 2)))
    print(rows[-1], flush=True)
json.dump(rows, open("data/sx_astrometry.json", "w"), indent=1)
print(len(rows), "positions")
