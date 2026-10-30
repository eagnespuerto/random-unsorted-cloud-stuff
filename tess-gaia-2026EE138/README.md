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

Near-stationary motion in S45–46 means FFI stacks barely smear it, which helps a shift-stack. Field is high
latitude (b ≈ +55°), so crowding is low. Still, V ≈ 22.7 sits at the faint end of published TESS shift-stack
recoveries, so a detection is unlikely without a deep, careful stack.

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
