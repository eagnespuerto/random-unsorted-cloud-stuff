"""Shift-and-stack (north-up, 21\" grid) 2026 EE138 in TESSCut FFI cutouts.
Per sector: drop flagged / high-background frames, subtract each pixel's sector median (static sky),
remove per-frame residual level, then sample a +-8 px stamp centred on the predicted position in
every frame and take a clipped mean. Same pipeline on 8 control tracks (offset 12 px) gives the null.
usage: python tess_shiftstack.py <ephemeris> <cutout.fits> [...]    -> data/tess_shiftstack.json, stamps .npy"""
import sys, json, numpy as np, warnings
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from scipy.ndimage import map_coordinates
warnings.simplefilter("ignore")

L = open(sys.argv[1]).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
jd = np.array([Time.strptime(l.split(',')[0].strip(), '%Y-%b-%d %H:%M').jd for l in L])
RA = np.array([float(l.split(',')[3]) for l in L]); DE = np.array([float(l.split(',')[4]) for l in L])
V = np.array([float(l.split(',')[5]) for l in L])
HW, AP, ZP = 8, 1.5, 20.44                     # stamp half-width (px), aperture radius (px), TESS zero point
yy, xx = np.mgrid[-HW:HW + 1, -HW:HW + 1]; R = np.hypot(xx, yy)
APER, ANN = R <= AP, (R >= 4) & (R <= 7)

def clipmean(A):
    med = np.nanmedian(A, 0); mad = 1.4826 * np.nanmedian(np.abs(A - med), 0) + 1e-9
    return np.nanmean(np.where(np.abs(A - med) < 3 * mad, A, np.nan), 0)

out, stamps = {}, {}
for f in sys.argv[2:]:
    h = fits.open(f); sec = h[0].header['SECTOR']; d = h[1].data
    w = WCS(h[2].header)
    t = d['TIME'] + 2457000; F = d['FLUX'].astype('f8'); q = d['QUALITY']
    ok = (q == 0) & np.isfinite(t) & np.isfinite(F).all((1, 2))
    b = np.nanmedian(F.reshape(len(t), -1), 1)                   # frame sky level (FLUX_BKG is empty in these cutouts)
    ok &= b < np.nanpercentile(b[ok], 80)                         # drop scattered-light frames
    t, F = t[ok], F[ok]
    D = F - np.nanmedian(F, 0)                                    # remove static sky
    D -= np.nanmedian(D.reshape(len(t), -1), 1)[:, None, None]
    ny, nx = D.shape[1:]
    ra0, de0 = np.interp(t, jd, RA), np.interp(t, jd, DE)
    x0, y0 = w.world_to_pixel_values(ra0, de0)
    PIX = 21.0 / 3600                                             # sample on a north-up 21" sky grid
    def track(dx=0, dy=0, keep=False):
        S = []
        for k in range(len(t)):
            dd = de0[k] + (yy + dy) * PIX
            X, Y = w.world_to_pixel_values(ra0[k] + (xx + dx) * PIX / np.cos(np.radians(dd)), dd)
            if X.min() < 0 or Y.min() < 0 or X.max() > nx - 1 or Y.max() > ny - 1: continue
            S.append(map_coordinates(D[k], [Y, X], order=1))
        S = clipmean(np.array(S)); fl = float(np.nansum(S[APER] - np.nanmedian(S[ANN])))
        return fl, S, len(t)
    fl, S, n = track()
    ctrl = [track(12 * np.cos(a), 12 * np.sin(a))[0] for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
    sig = float(np.std(ctrl)); Vm = float(np.interp(t.mean(), jd, V))
    lim = ZP - 2.5 * np.log10(3 * sig)
    out[sec] = dict(n_frames=n, flux_e_s=round(fl, 4), ctrl_sigma_e_s=round(sig, 4), snr=round(fl / sig, 2),
                    T_3sigma_limit=round(float(lim), 2), V_pred=round(Vm, 2), T_pred=round(Vm - 0.5, 2),
                    dates=f"{Time(t[0], format='jd').iso[:10]} - {Time(t[-1], format='jd').iso[:10]}",
                    track_px=round(float(np.hypot(x0[-1] - x0[0], y0[-1] - y0[0])), 1))
    stamps[sec] = S; print(sec, out[sec], flush=True)
json.dump(out, open('data/tess_shiftstack.json', 'w'), indent=1)
np.savez_compressed('data/tess_stamps.npz', **{f's{k}': v for k, v in stamps.items()})
