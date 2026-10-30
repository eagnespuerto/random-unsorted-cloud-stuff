"""Forced aperture photometry of 2026 EE138 on SDSS frames (DR17 calibrated 'frame' files, nanomaggies).
1.5" radius aperture at the JPL position (time-corrected per filter), local annulus 8-15";
noise from 200 random apertures in source-free sky of the same frame.
usage: python sdss_forced.py <APO ephemeris> <ca bundle> <workdir>  -> data/sdss_forced.json"""
import sys, os, json, subprocess, numpy as np, warnings
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
warnings.simplefilter("ignore")
eph, ca, W = sys.argv[1:4]
L = open(eph).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
mjd = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').mjd for l in L])
RA = np.array([float(l.split(',')[3]) for l in L]); DE = np.array([float(l.split(',')[4]) for l in L])
RAP = 1.5   # aperture radius, arcsec (~1x seeing FWHM)
FIELDS = [(3518, 4, 121), (6160, 3, 12), (6160, 3, 13)]
# filter time offsets from r in the SDSS scan order r-i-u-z-g, 71.7 s apart
DT = {'r': 0, 'i': 71.7, 'u': 143.4, 'z': 215.1, 'g': 286.8}
hits = {(h['run'], h['camcol'], h['field']): h['mjd_r'] for h in json.load(open('data/sdss_fields_with_object.json'))}
res = []
for run, cc, fld in FIELDS:
    for b in 'gri z':
        if b == ' ': continue
        fn = f"frame-{b}-{run:06d}-{cc}-{fld:04d}.fits"
        if not os.path.exists(f"{W}/{fn}"):
            subprocess.run(["curl", "-sS", "--cacert", ca, "-m", "300", "-o", f"{W}/{fn}.bz2",
                            f"https://data.sdss.org/sas/dr17/eboss/photoObj/frames/301/{run}/{cc}/{fn}.bz2"], check=True)
            subprocess.run(["bunzip2", "-f", f"{W}/{fn}.bz2"], check=True)
        h = fits.open(f"{W}/{fn}"); img = h[0].data.astype(float); w = WCS(h[0].header)
        t = hits[(run, cc, fld)] + DT[b] / 86400
        x, y = w.world_to_pixel_values(np.interp(t, mjd, RA), np.interp(t, mjd, DE))
        ny, nx = img.shape
        if not (10 < x < nx - 10 and 10 < y < ny - 10): continue
        yy, xx = np.mgrid[:ny, :nx]; pix = 0.396
        def ap(x0, y0):
            r = np.hypot(xx - x0, yy - y0) * pix
            return np.sum(img[r <= RAP]) - np.median(img[(r > 8) & (r < 15)]) * np.sum(r <= RAP)
        f = ap(x, y)
        rng = np.random.default_rng(1); ctrl = []
        thr = np.median(img) + 5 * 1.4826 * np.median(np.abs(img - np.median(img)))
        while len(ctrl) < 200:
            cx, cy = rng.uniform(30, nx - 30), rng.uniform(30, ny - 30)
            if np.hypot(cx - x, cy - y) < 40: continue
            r = np.hypot(xx - cx, yy - cy) * pix
            if img[r <= 6].max() > thr: continue      # skip apertures with sources
            ctrl.append(ap(cx, cy))
        s = float(np.std(ctrl))
        mag = 22.5 - 2.5 * np.log10(f) if f > 0 else None
        res.append(dict(run=run, camcol=cc, field=fld, band=b, flux_nmgy=round(float(f), 4), err_nmgy=round(s, 4),
                        snr=round(float(f / s), 2), mag=None if mag is None else round(float(mag), 2),
                        lim5=round(float(22.5 - 2.5 * np.log10(5 * s)), 2), x=round(float(x), 1), y=round(float(y), 1)))
        print(res[-1], flush=True)
json.dump(res, open('data/sdss_forced.json', 'w'), indent=1)
