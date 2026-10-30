# 2026 EE138 — TESS and Gaia search (cursory)

TNO, a = 71.1 au, e = 0.51, i = 11.2°, H = 3.95 (JPL SBDB, orbit soln 2026-10-27, arc 2013–2026).
Distance 72–77 au, V = 22.5–22.9 over 2014–2026. Track: RA 161.6–167.7°, Dec +7.0…+3.2°, b ≈ +54…+56°.
Astrometry: `data/2026EE138.obs` (DECam W84 2013–2020, Rubin X05 2026). Ephemeris: `data/eph_geo.txt` (Horizons, daily).

## Result

| Mission | Coverage | Expected brightness | Result |
|---|---|---|---|
| TESS | On silicon in 3 sectors (`scripts/tess_check.py`, tess-point, sectors 1–134; matches TESSCut) | V ≈ 22.7 (T ≈ 22.2) | Covered, not detectable in single FFIs; only a shift-stack could reach it, and it's at/below that limit |
| Gaia | Mission ran 2014-07-25 – 2025-01-15 | V 22.5–22.9 → G ≈ 22.3–22.7 | Not detectable (G limit ≈ 20.7). Not in `gaiadr3.sso_source` or `gaiafpr.sso_source` |

### TESS sectors (`data/tess_coverage.txt`)

| Sector | Dates | Cam/CCD | Object position (mid) | Motion over sector |
|---|---|---|---|---|
| 45 | 2021-11-06 – 12-02 | 4/3 | 165.84°, +4.54° | ~21 px (near stationary point) |
| 46 | 2021-12-02 – 12-30 | 3/2 | 165.88°, +4.51° | ~7 px (stationary) |
| 72 | 2023-11-11 – 12-07 | 4/2 | 166.66°, +3.99° | ~21 px, col ≈ 158 (near CCD edge) |

### Shift-stacks — not detected (`scripts/tess_shiftstack.py`, `data/tess_shiftstack.json`)
Per sector: drop flagged and the brightest-sky 20% of frames, subtract each pixel's sector median, sample a
north-up 21″ stamp on the predicted track, clipped mean. Noise from 8 control tracks 12 px away.
Expected signal: T ≈ 22.2 → 0.19 e⁻/s.

| Sector | Frames | Flux (e⁻/s) | Control σ | 3σ limit |
|---|---|---|---|---|
| 45 | 2,655 | 0.18 | 1.05 | T > 19.2 |
| 46 | 2,748 | 1.73 | 0.66 | T > 19.7 (2.6σ bump = star residual) |
| 72 | 6,413 | 0.07 | 0.32 | T > 20.5 |

Best limit is ~1.7 mag short of the object. Noise is set by star residuals, not photon noise.

### Sector 46 re-stack (`scripts/tess_s46_deep.py`, `data/tess_s46_deep.json`)
S46 looked like the best chance (object near its stationary point), but it's the worst:
- The object loops within ~2 px (≈40″) for the first ~3 weeks and only moves off in the last ~6 days
  (6.3 px total). A sector-median template partly removes the object, and per-frame templates that
  exclude the object's position exist only for the last ~17 hours of usable data.
- A G = 12.5 star (Gaia DR3 3815098193520100224) passes 26″ (1.3 px) from the track at sector end, and a
  G = 14.8 star 37″ from it early on. A 10-mag-brighter star leaves residuals far above 0.19 e⁻/s.
- Re-stack (1-h bins, template from bins with the object ≥2 px away, bins within 60″ of the G = 12.5 star
  dropped): 1.09 ± 0.53 e⁻/s (2.0σ), reversed-motion null 0.2σ, T > 19.9 (3σ). The flux is ~6× what the
  object can give, so it's a residual, not the object.
- A cross-sector template (S72 sky at the S46 position) would avoid self-subtraction, but camera/PSF
  mismatch on the G = 12.5 star would still dominate. Not attempted.

## Colours (from current obs)

| Source | Date | Colour |
|---|---|---|
| DECam | 2018-03-19 | g−r = 0.58 |
| Rubin | 2026-04-10 | r−i = 0.32 |
| Rubin | 2026-04-11 | r−i = 0.19 (2 pairs) |
| Rubin | 2026-04-14 | r−i = 0.18 |
| Rubin | 2026-04-16 | r−i = 0.33 |
| Rubin | 2026-06-26 | r−i = 0.33 |

Mean: g−r = 0.58, r−i = 0.26 (neutral / less-red class).
