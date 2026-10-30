"""Stamp grid of notable (non-null) archival detections of 2026 ED138: SPHEREx stacks and Swift/UVOT U."""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
plt.rcParams.update({"font.family": "DejaVu Sans", "font.weight": "normal", "axes.titleweight": "normal"})

def clipped_stack(A):
    A = A - np.median(A.reshape(len(A), -1), axis=1)[:, None, None]
    med = np.median(A, 0); mad = 1.4826 * np.median(np.abs(A - med), 0) + 1e-12
    return np.nanmean(np.where(np.abs(A - med) < 4 * mad, A, np.nan), 0)

O = json.load(open("sx/phot.json"))["obj"]; S = np.load("sx/stamps.npy")
def sx(sel): idx = [i for i, x in enumerate(O) if sel(x)]; return clipped_stack(S[idx]), len(idx)
U = np.load("sw/uvot_stamps.npy"); res = json.load(open("sw/uvot_result.json"))

panels = [
    (*sx(lambda x: x["reg"] == "2026a" and x["band"][-1] in "123"), 36, 7, "SPHEREx 0.75–2.4 µm, Mar–Apr 2026", "75 ± 11 µJy, 7σ peak"),
    (*sx(lambda x: x["band"][-1] in "123"), 36, 7, "SPHEREx 0.75–2.4 µm, all passes", "60 ± 13 µJy"),
    (np.mean(U, 0), 3, 15, 3, "Swift/UVOT U, 2011-07-14, stack", f"U = {res['U_vega']:.2f} ± {res['U_err']:.2f}, 4.7σ"),
] + [(U[k], 1, 15, 3, f"Swift/UVOT U, snapshot {k+1}", "minus other snapshots") for k in range(3)]

fig, ax = plt.subplots(2, 3, figsize=(13.5, 10.4))
for a, (im, n, hw, r, t1, t2) in zip(ax.flat, panels):
    s = 1.4826 * np.nanmedian(np.abs(im - np.nanmedian(im)))
    a.imshow(im, origin="lower", cmap="gray", vmin=-3 * s, vmax=5 * s, extent=[-hw, hw, -hw, hw])
    a.invert_xaxis(); a.add_patch(Circle((0, 0), r, fill=False, ec="#d62728", lw=1.3))
    a.set_title(f"{t1}\n{t2}" + (f"  (N = {n})" if n > 3 else ""), fontsize=11)
    a.set_xlabel("arcsec (east left)", fontsize=9); a.set_ylabel("arcsec (north up)", fontsize=9); a.tick_params(labelsize=8)
fig.suptitle("2026 ED138: Notable archival detections (template-subtracted, centred on JPL prediction)", fontsize=13, fontweight="normal")
plt.tight_layout(rect=[0, 0, 1, 0.96], h_pad=3.0); plt.savefig("stamp_grid_2026ED138.png", dpi=110)
print("saved")
