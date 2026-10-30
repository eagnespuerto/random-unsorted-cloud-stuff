"""Fetch a DASCH cutout of plate mc27133 at the predicted position of 2026 ED138,
measure aperture SNR there against random background apertures, and render a PNG."""
import base64, gzip, json, subprocess
import numpy as np
from astropy.io import fits
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

RA, DEC = 145.788972, 12.730369  # JPL Horizons, 1934-03-16 04:11 UT (mid-exposure)
out = subprocess.run(["curl", "-sS", "-m", "180", "-X", "POST",
    "https://api.starglass.cfa.harvard.edu/public/dasch/dr7/cutout",
    "-H", "Content-Type: application/json", "-d",
    json.dumps({"plate_id": "mc27133", "solution_number": 0,
                "center_ra_deg": RA, "center_dec_deg": DEC})],
    capture_output=True, text=True, check=True).stdout
open("mc27133.fits", "wb").write(gzip.decompress(base64.b64decode(json.loads(out))))

d = fits.open("mc27133.fits")[0].data.astype(float)  # 1.44"/px, centered on prediction
c = d.shape[0] // 2
yy, xx = np.mgrid[:d.shape[0], :d.shape[1]]

def ap(x, y, r=3, ri=7, ro=12):
    R = np.hypot(xx - x, yy - y)
    s, b = d[R <= r], d[(R > ri) & (R <= ro)]
    return s.sum() - np.median(b) * s.size

f0 = ap(c, c)
rng = np.random.default_rng(1)
F = np.array([ap(*rng.integers(40, d.shape[0] - 40, 2)) for _ in range(3000)])
sig = 1.4826 * np.median(np.abs(F - np.median(F)))
print(f"SNR at prediction: {(f0 - np.median(F)) / sig:.2f}; percentile {(F < f0).mean():.2f}")

fig, ax = plt.subplots(1, 2, figsize=(12, 6))
for a, hw, t in ((ax[0], c, "mc27133  1934-03-16  20′ field"),
                 (ax[1], 60, "zoom 2.9′; red = 3σ (4.5″)")):
    s = d[c - hw:c + hw + 1, c - hw:c + hw + 1]
    lo, hi = np.percentile(s, [5, 99.5])
    a.imshow(s, origin="lower", cmap="gray", vmin=lo, vmax=hi,
             extent=[-hw - .5, hw + .5, -hw - .5, hw + .5])
    a.set_title(t)
    a.add_patch(Circle((0, 0), 4.5 / 1.44 if hw < 100 else 15, fill=False, ec="r", lw=1.2))
plt.tight_layout(); plt.savefig("mc27133_cutout.png", dpi=110)
