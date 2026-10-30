"""Swift/UVOT U-band detection of 2026 ED138 in obsid 00031929004 (2011-07-14, 3 snapshots, 4.8 ks).
Each snapshot minus the mean of the other two, sampled at the object's JPL position for that snapshot;
3" aperture, 7-12" annulus. Noise from 300 random tracks 30-150" away. Motion null tests + Gaussian position fit.
Inputs: sw00031929004uuu_sk.img.gz (HEASARC Swift archive) and pos.json (JPL Horizons per snapshot)."""
import json, math, sys, warnings
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
warnings.simplefilter("ignore")
IMG = sys.argv[1] if len(sys.argv) > 1 else "sw/00031929004uuu.img.gz"
POS = sys.argv[2] if len(sys.argv) > 2 else "sw/pos.json"
P = [p for p in json.load(open(POS)) if p["ext"].startswith("uu")]
ext = {e.name: e for e in fits.open(IMG)[1:]}; W = {k: WCS(e.header) for k, e in ext.items()}
S = 0.5 / 3600; HW = 30; g = np.arange(-HW, HW + 1) * S; GX, GY = np.meshgrid(g, g)
R = np.hypot(GX, GY) * 3600; AP, AN = R <= 3.0, (R > 7) & (R <= 12)

def stamp(n, ra, dec):
    e = ext[n]; cd = math.cos(math.radians(dec)); x, y = W[n].world_to_pixel_values(ra + GX / cd, dec + GY)
    return map_coordinates(e.data / e.header["EXPOSURE"], [y, x], order=1, mode="nearest")
def diff(ra, dec, k):
    return stamp(P[k]["ext"], ra, dec) - np.mean([stamp(P[j]["ext"], ra, dec) for j in range(3) if j != k], axis=0)
def meas(ra, dec, k):
    d = diff(ra, dec, k); return float((d[AP] - np.median(d[AN])).sum() / 4)       # (0.5"/1.0")^2 resampling factor
def track(pos): per = [meas(pos[k][0], pos[k][1], k) for k in range(3)]; return sum(per), per

if __name__ == "__main__":
    p = [(q["ra"], q["dec"]) for q in P]
    rng = np.random.default_rng(2); c = []
    for _ in range(300):
        r = rng.uniform(30, 150) / 3600; a = rng.uniform(0, 2 * math.pi)
        c.append(track([(x + r * math.cos(a) / math.cos(math.radians(y)), y + r * math.sin(a)) for x, y in p])[0])
    c = np.array(c); m0 = np.median(c); sig = 1.4826 * np.median(np.abs(c - m0))
    dx = [(q[0] - p[1][0], q[1] - p[1][1]) for q in p]; cd = math.cos(math.radians(p[1][1]))
    tests = {"predicted motion": p, "reversed motion": [p[2], p[1], p[0]], "stationary at middle position": [p[1]] * 3,
             "stationary at snapshot-1 position": [p[0]] * 3, "stationary at snapshot-3 position": [p[2]] * 3,
             "double rate": [(p[1][0] + 2 * a, p[1][1] + 2 * b) for a, b in dx],
             "rotated 90 deg": [(p[1][0] - b / cd, p[1][1] + a * cd) for a, b in dx]}
    res = {}
    for k, v in tests.items():
        t, per = track(v); res[k] = dict(sum_cps=t, sigma=(t - m0) / sig, per_snapshot=per)
        print(f"{k:34s} {(t - m0) / sig:+.1f} sigma   per-snapshot {np.round(per, 4)}")
    D = [diff(p[k][0], p[k][1], k) for k in range(3)]; st = np.mean(D, axis=0); st -= np.median(st)
    y, x = np.mgrid[:st.shape[0], :st.shape[1]]; X = (x - HW) * 0.5; Y = (y - HW) * 0.5; m = np.hypot(X, Y) < 6
    model = lambda q: q[0] * np.exp(-((X - q[1]) ** 2 + (Y - q[2]) ** 2) / (2 * (2.5 / 2.355) ** 2)) + q[3]
    fit = least_squares(lambda q: (model(q) - st)[m], [st.max(), 0, 0, 0])
    rate = np.mean([meas(p[k][0], p[k][1], k) for k in range(3)])
    U = 18.34 - 2.5 * math.log10(rate * 1.10)                                       # Vega ZP, ~3"->5" aperture correction
    snr = res["predicted motion"]["sigma"]
    print(f"U(Vega) = {U:.2f} ± {1.0857 / snr:.2f}; offset from prediction E {fit.x[1]:+.2f}\" N {fit.x[2]:+.2f}\"")
    json.dump(dict(tests=res, noise_sigma_cps=sig, mean_rate_cps=rate, U_vega=U, U_err=1.0857 / snr,
                   fit_offset_arcsec=[float(fit.x[1]), float(fit.x[2])], positions=P), open("sw/uvot_result.json", "w"), indent=1)
    np.save("sw/uvot_stamps.npy", np.array(D))
