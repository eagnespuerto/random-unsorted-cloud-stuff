import json, glob, numpy as np, warnings; warnings.simplefilter("ignore")
from astropy.io import fits; from astropy.wcs import WCS; from astropy.time import Time
import astropy.units as u; from astropy.coordinates import SkyCoord, EarthLocation
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.weight": "normal", "axes.titleweight": "normal"})
T = [json.loads(l) for l in open("past/tess/targets.jsonl")]
fig, axes = plt.subplots(2, 1, figsize=(11, 7.5)); res = []
for ax, t in zip(axes, T):
    sec = t["tess_sector"][0]; f = glob.glob(f"past/tess/s{sec}/*.fits")[0]; h = fits.open(f)
    d = h[1].data; w = WCS(h[2].header)
    x, y = w.world_to_pixel_values(t["star_ra"], t["star_dec"]); xi, yi = int(round(float(x))), int(round(float(y)))
    flux = d["FLUX"]; q = d["QUALITY"]; tb = d["TIME"]
    ap = flux[:, yi-1:yi+1+1, xi-1:xi+1+1].sum(axis=(1, 2))          # 3x3 px
    bg = np.nanmedian(np.concatenate([flux[:, :3, :].reshape(len(flux), -1), flux[:, -3:, :].reshape(len(flux), -1)], axis=1), axis=1) * 9
    lc = ap - bg; ok = (q == 0) & np.isfinite(lc)
    # event time -> BTJD (barycentric, toward the star)
    te = Time(t["jd"], format="jd", scale="utc"); c = SkyCoord(t["star_ra"] * u.deg, t["star_dec"] * u.deg)
    btjd = (te.tdb + te.light_travel_time(c, location=EarthLocation.from_geocentric(0, 0, 0, unit=u.m))).jd - 2457000
    cad = np.nanmedian(np.diff(tb[ok])) * 86400
    k = np.argmin(np.abs(tb - btjd)); near = ok & (np.abs(tb - btjd) < 1.0)
    base = np.nanmedian(lc[near]); rms = 1.4826 * np.nanmedian(np.abs(lc[near] - base))
    # star's own flux: TESS ZP 20.44 e-/s at Tmag 10 -> 15000 e-/s ; Tmag ~ G - 0.5 for these colours (approx)
    star_e = 15000 * 10 ** (-0.4 * ((t["G"] - 0.5) - 10))
    dip_full = star_e * min(t["max_dur_s"] / cad, 1)
    res.append(dict(sector=sec, utc=t["utc"], btjd=round(btjd, 5), cadence_s=round(cad), event_cadence_quality=int(q[k]),
                    event_cadence_offset_from_baseline_sigma=round(float((lc[k] - base) / rms), 2) if ok[k] else None,
                    rms_e_per_s=round(float(rms), 1), expected_max_dip_e_per_s=round(dip_full, 1),
                    expected_dip_in_sigma=round(dip_full / rms, 2), p_hit=t["p_hit"]))
    m = np.abs(tb - btjd) < 1.0
    ax.plot((tb[m & ok] - btjd) * 24, lc[m & ok], ".", ms=3, color="#444")
    ax.axvline(0, color="#d62728", lw=1); ax.axhline(base - dip_full, color="#1f77b4", ls="--", lw=1)
    ax.set_title(f"TESS sector {sec}: Gaia DR3 {t['star']} (G {t['G']:.1f}), predicted event {t['utc']} UTC, P(hit) {t['p_hit']:.2f}", fontsize=11)
    ax.set_xlabel("hours from predicted event"); ax.set_ylabel("3×3 px flux − background (e⁻/s)")
fig.suptitle("2026 ED138: TESS full-frame light curves at the two in-sector past occultation candidates", fontsize=11, fontweight="normal")
plt.tight_layout(rect=[0, 0, 1, 0.96]); plt.savefig("past/tess/tess_lcs.png", dpi=100)
for r in res: print(r)
json.dump(res, open("past/tess/tess_lc_result.json", "w"), indent=1)
