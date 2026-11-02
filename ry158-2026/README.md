# 2026 RY158: SPHEREx frames before discovery

![SPHEREx stamp grid](stamp_grid_2026RY158.png)

**Orbit** (JPL SBDB, copy of an MPC orbit): a ≈ 435 au, e = 0.975, q = 11.0 au, i = 95.5°, H = 4.06. The arc is only 11 days (2026-09-10 – 09-21, 19 observations), and the condition code is 7. The MPC API does not resolve the designation (2026-11-02), so neither astrometry nor a covariance is public. In Aug–Sep 2026 the object is at 13.6 au, V ≈ 15.8, RA ≈ 100–111°, Dec ≈ −69…−71°.

## Result

- **Frames:** `archsearch "2026 RY158" 2026-08-15 2026-11-01 --moving` found 22 SPHEREx QR3 exposures (D1 + D4) from 2026-08-15 to 09-09. They are listed in `data/archsearch_2026.csv`.
  - All 22 exposures fall 1–26 days *before* the first MPC observation.
  - MAST timed out. Swift returned only wide-field rows.
- **Detected in every D1 frame** at 1.4–2.1 mJy (7″ aperture).
  - In 19 of 22 frames, the brightest residual within 60″ is ≤ 10″ from the JPL prediction.
  - On 08-15, 26 days before the arc starts, the peak is about 6″ east of the prediction. The short-arc orbit already holds to about 1 SPHEREx pixel there.
  - These frames are precovery astrometry that would extend the arc.
- **D4 (2.4–3.8 µm):** the stack gives 0.36 ± 0.03 mJy, but single frames are dominated by star residuals (only 3 of 22 peaks are on target). Treat it as a tentative detection.
- **Caveats:**
  - D1 spans 0.75–1.09 µm across the detector. The jump from ~1.45 mJy (Aug) to ~2.0 mJy (Sep) can partly come from a different wavelength at the object's position, so it is not necessarily variability.
  - The source looks broader than the SPHEREx PSF in the deep stacks. That would be worth checking for a coma, since q = 11 au makes it a Centaur. It is not tested here.
  - The quoted flux is aperture flux, not total flux.

## Method

- `scripts/sx_get.py` downloads 0.12° cutouts for each science frame, plus up to 10 same-band reference frames of the same sky taken ≥ 2 days away. Positions come from Horizons with observer SPHEREx (`500@-163182`, `data/eph_sx.txt`).
- `scripts/sx_stack.py` builds the stamps and photometry:
  - Each frame is resampled to a north-up 3″ grid, and the median reference is subtracted.
  - Photometry uses a 7″ aperture and a 15–30″ background annulus. Per-frame noise comes from 12 blank offset apertures.
  - Stacks are a 3σ-clipped mean. The error is the scatter divided by √N.
  - Outputs: `data/sx_phot.json` (per frame) and `data/sx_stamps.npz`.
- TESS also covers the predicted track in 14 sectors (2018–2025, V ≈ 16–18; `data/eph_geo.txt` + tess-point). Those epochs are a year or more outside the arc, so the position there is too uncertain to put a stamp on.

Regenerate:

```
python scripts/sx_get.py            # ~480 cutouts into sx/cut (not committed, ~12 MB)
python scripts/sx_stack.py
python ../.claude/skills/stamp-grid/make_stamp_grid.py stamp_grid.json
```
