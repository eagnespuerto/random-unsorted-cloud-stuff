# 2026 ED138 — DASCH (Harvard plates) precovery search, 1885–1936

**Result: no precovery.** About 8,500 Harvard plates contain the predicted position, but only one
(mc27133) has a catalog limit near the object's brightness, and nothing is visible there.

## Method
- Orbit: JPL SBDB/Horizons (solution 2026-10-29, arc 1937–2026). Predicted V ≈ 18.6–19.1
  throughout 1885–1936; 3σ position uncertainty ≤ 30″ (≈ 4.5″ in 1934).
- Daily geocentric ephemeris sampled every 0.5° along the track; DASCH DR7 `queryexps`
  run at each point (`scripts/q3.py`, `scripts/q_1885_1900.py`).
- Plate kept if the object's interpolated position at exposure time lies inside the plate
  (`scripts/an2.py`). Per-period lists: `coverage/plates_*.csv`.

## Plates containing the object, and the deepest one per period

| Period | Plates | Deepest (catalog limit) | Object V |
|---|---|---|---|
| 1885–1900 | 424 | i5271, 1891-12-20 — 14.47 | 18.85 |
| 1901–1910 | 2,259 | i30076, 1903-02-24 — 15.40 | 18.82 |
| 1911–1920 | 2,727 | mc15506, 1918-12-07 — 15.96 | 18.69 |
| 1921–1930 | 1,880 | mc19343, 1922-12-13 — 16.45 | 18.68 |
| 1931–1936 | 1,205 | **mc27133, 1934-03-16 — 18.12** | 18.65 |

Uncalibrated long exposures (mc/md/mf, 60–120 min) typically reach ~17–17.5, still short.

## mc27133 check
- 120-min exposure on the 16-inch Metcalf, started 1934-03-16 03:11 UT; WCS solved from the scanned image.
- Predicted mid-exposure position: RA 09h43m09.35s, Dec +12°43′49.3″ (J2000), 3σ ±4.5″; motion ~2.9″/h.
- The plate's two catalog limits disagree (18.1 ATLAS vs 15.5 APASS); a red TNO would also be
  fainter in the plate's blue-sensitive emulsion.
- Cutout (`mc27133.fits`, `mc27133_cutout.png`, `scripts/cutout_check.py`): aperture SNR at the
  prediction ≈ 0.0, the median of 3,000 random background apertures. Nearest star ~32″ away.
  **Non-detection.**
