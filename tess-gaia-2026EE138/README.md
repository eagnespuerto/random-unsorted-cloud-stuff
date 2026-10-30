# 2026 EE138 — TESS, Gaia, Swift and SPHEREx search

![TESS and SPHEREx stacks](stamp_grid_2026EE138.png)

TNO, a = 71.1 au, e = 0.51, i = 11.2°, H = 3.95 (JPL SBDB, orbit soln 2026-10-27, arc 2013–2026).
Distance 72–77 au, V = 22.5–22.9 over 2014–2026. Track: RA 161.6–167.7°, Dec +7.0…+3.2°, b ≈ +54…+56°.
Astrometry: `data/2026EE138.obs` (DECam W84 2013–2020, Rubin X05 2026). Ephemeris: `data/eph_geo.txt` (Horizons, daily).

## Result

| Mission | Coverage | Expected brightness | Result |
|---|---|---|---|
| TESS | On silicon in 3 sectors (`scripts/tess_check.py`, tess-point, sectors 1–134; matches TESSCut) | V ≈ 22.7 (T ≈ 22.2) | Covered, not detectable in single FFIs; only a shift-stack could reach it, and it's at/below that limit |
| Gaia | Mission ran 2014-07-25 – 2025-01-15 | V 22.5–22.9 → G ≈ 22.3–22.7 | Not detectable (G limit ≈ 20.7). Not in `gaiadr3.sso_source` or `gaiafpr.sso_source` |
| Swift | HEASARC `swiftmastr`, 1,093 obs in RA 158–171°, Dec 1–9.5° | — | Never observed: closest 0.27° (UGC 5923, 2015-07-12), outside UVOT/XRT fields. No colours possible |
| CHEOPS | ESASky `mv_cheops_obs_fdw`, all 2,938 public visits (2020-02 – 2023-12) (`scripts/cheops_check.py`) | V ≈ 22.7, far beyond CHEOPS | Not observed: closest 2.4° (EE Leo, 2021-04-08). 2024–2026 unchecked (DACE down, HTTP 503) |
| SPHEREx | 292 L2 frames contain the object (QR2; Apr–Jun 2025, Dec 2025, May 2026) | z ≈ 21.9 AB → ~6 µJy | Not detected: 14 ± 8 µJy (0.75–2.4 µm), 0 ± 12 µJy (2.4–5 µm) |

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

## Swift (`scripts/coverage_sx_swift.py`, `data/coverage_sx_swift.json`)
No pointing ever covered the object. Even if one had, V ≈ 22.7 is far below UVOT depth (the 2026 ED138 U-band
detection in `../uv-xray-atmosphere` was a ~4,800 s stack of a U ≈ 21 object). No Swift colour estimates.

## SPHEREx (`scripts/sx_get.py`, `scripts/sx_stack.py`, `data/sx_phot.json`)
- IRSA ObsCore: 292 frames contain the object at exposure mid-time (`data/coverage_sx_swift.json`); QR3 has none here yet.
- Method as in `../spherex-search`: 72″ north-up stamp per frame minus the median of ≤40 same-band, same-region
  frames with the object >30″ away; 7″ aperture, 15–30″ annulus; 6 control tracks 2′ away.
  882/898 cutouts downloaded (16 failed); 231 frames had enough templates.

| Stack | N | Flux (µJy) | Control scatter | Verdict |
|---|---|---|---|---|
| Apr–Jun 2025, 0.75–2.4 µm | 36 | 9.5 | 6.0 | 1.6σ |
| Dec 2025, 0.75–2.4 µm | 69 | 11.2 | 15.6 | <1σ |
| May 2026, 0.75–2.4 µm | 18 | 31.7 | 18.2 | 1.7σ |
| **All, 0.75–2.4 µm** | 123 | **13.7** | 8.0 | 1.7σ, not detected; 3σ < 24 µJy above zero |
| All, 2.4–5 µm | 108 | 0.4 | 12.1 | nothing |

Expected from Rubin/DECam z ≈ 21.9 AB: ~6 µJy at ~1 µm, i.e. ~0.8σ in the best stack. No colour/spectral constraint.

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
