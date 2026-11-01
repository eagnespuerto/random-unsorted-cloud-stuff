"""Stack archsearch-selected SPHEREx frames into stamp-grid panels (sigma-clipped mean)."""
import json, numpy as np
from astropy.time import Time
P = json.load(open("phot_2026a.json")); S = np.load("stamps_2026a.npy")
f = np.array([p["flux"] for p in P]); band = np.array([p["band"][-2:] for p in P]); mjd = np.array([p["mjd"] for p in P])

def stack(sel):
    idx = np.where(sel)[0]
    x = f[idx]; med = np.median(x); mad = 1.4826 * np.median(np.abs(x - med))
    keep = idx[np.abs(x - med) <= 3 * mad]
    fl = f[keep]; err = fl.std(ddof=1) / np.sqrt(len(fl))
    img = S[keep].mean(0)
    g = np.arange(-18, 19) * 2.0; R = np.hypot(*np.meshgrid(g, g))
    img = img - np.median(img[(R > 15) & (R <= 30)])   # same local background as the photometry
    return img, fl.mean(), err, len(keep), len(idx)

d1, d2 = Time(mjd.min(), format="mjd").iso[5:10], Time(mjd.max(), format="mjd").iso[5:10]
groups = [("0.75–2.4 µm (D1–D3)", np.isin(band, ["D1", "D2", "D3"])),
          ("2.4–5.0 µm (D4–D6)", np.isin(band, ["D4", "D5", "D6"]))]
groups += [(f"{b}", band == b) for b in ["D1", "D2", "D3", "D4", "D5", "D6"]]
arrs, panels = {}, []
for name, sel in groups:
    if sel.sum() < 2: continue
    img, fl, er, n, ntot = stack(sel)
    key = "k%d" % len(arrs); arrs[key] = img
    snr = fl / er
    res = f"{fl:.0f} ± {er:.0f} µJy ({snr:.1f}σ)" if snr >= 3 else f"{fl:.0f} ± {er:.0f} µJy, not detected"
    panels.append({"file": "stamps_grid.npz", "key": key, "hw": 36, "r": 7.0,
                   "title": f"SPHEREx {name}, 2026 {d1}–{d2}", "subtitle": res, "n": int(n)})
    print(name, n, ntot, round(fl, 1), round(er, 1))
np.savez_compressed("stamps_grid.npz", **arrs)
json.dump({"title": "2026 ED138", "ncols": 3, "out": "stamp_grid_2026ED138_archsearch.png",
           "subtitle": "SPHEREx frames found by archsearch, template-subtracted stacks centred on JPL prediction",
           "panels": panels}, open("stamp_grid.json", "w"), indent=1, ensure_ascii=False)
