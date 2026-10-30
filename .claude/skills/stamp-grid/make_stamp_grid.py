"""Generic stamp grid in the repo's house style (see SKILL.md).
usage: python make_stamp_grid.py spec.json
spec = {"title": "2026 EE138", "subtitle": "TESS and SPHEREx shift-stacks (...)", "out": "stamp_grid.png",
        "ncols": 3, "panels": [{"file": "x.npz", "key": "s45", "hw": 168, "r": 31.5,
                                "title": "TESS S45, 2021-11", "subtitle": "not detected", "n": 2655}, ...]}
file: .npy (2-D, or 3-D with "index") or .npz (with "key"). hw = stamp half-width, r = aperture radius (arcsec).
Paths in the spec are relative to the spec file."""
import json, os, sys, math, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
plt.rcParams.update({"font.family": "DejaVu Sans", "font.weight": "normal", "axes.titleweight": "normal"})

spec_path = sys.argv[1]; base = os.path.dirname(os.path.abspath(spec_path)); S = json.load(open(spec_path))
def load(p):
    a = np.load(os.path.join(base, p["file"]))
    a = a[p["key"]] if "key" in p else a
    return a[p["index"]] if a.ndim == 3 else a

P = S["panels"]; nc = S.get("ncols", 3); nr = math.ceil(len(P) / nc)
fig, ax = plt.subplots(nr, nc, figsize=(4.5 * nc, 5.2 * nr), squeeze=False)
for a in ax.flat[len(P):]: a.axis("off")
for a, p in zip(ax.flat, P):
    im = load(p); hw = p["hw"]
    s = 1.4826 * np.nanmedian(np.abs(im - np.nanmedian(im))) or 1
    a.imshow(im, origin="lower", cmap="gray", vmin=-3 * s, vmax=5 * s, extent=[-hw, hw, -hw, hw])
    a.invert_xaxis(); a.add_patch(Circle((0, 0), p["r"], fill=False, ec="#d62728", lw=1.3))
    n = p.get("n", 0)
    a.set_title(f"{p['title']}\n{p['subtitle']}" + (f"  (N = {n})" if n > 3 else ""), fontsize=11)
    a.set_xlabel("arcsec (east left)", fontsize=9); a.set_ylabel("arcsec (north up)", fontsize=9); a.tick_params(labelsize=8)
fig.suptitle(f"{S['title']}: {S['subtitle']}", fontsize=13, fontweight="normal")
plt.tight_layout(rect=[0, 0, 1, 0.96], h_pad=3.0)
out = os.path.join(base, S["out"]); plt.savefig(out, dpi=110); print("saved", out)
