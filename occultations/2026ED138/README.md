# 2026 ED138 — stellar occultations

## Existing work
`occ.py`, `occ2.py`, `hitwindows_svg.py`, `hit_windows.*`, `occ_2026ED138_overlay.png`: satellite passages through the
shadow of the 2026-10-31 ~01:21 UTC event (star RA 18h11m15.97s, Dec −42°13′19.0″), using CelesTrak TLEs in `tle/`.

## Gaia DR3 candidate search, 2026-10-30 to 2028-12-31 (`gaia_occultation_search.py`)
- Hourly geocentric JPL Horizons ephemeris (orbit solution of 2026-10-29), interpolated to 1-minute steps.
- Gaia DR3 stars G < 18.5 along the track, propagated with proper motion.
- Kept if geocentric closest approach (CA) < Earth radius + 450 km body radius (+3σ ephemeris margin).
- Results: 75 candidates, 62 with the shadow nominally on Earth (5 in 2026, 28 in 2027, 29 in 2028).
  Full list: `gaia_occultation_candidates_2026-2028.csv` / `.json`.

| UTC | G | Geocentric CA | Max duration | Note |
|---|---|---|---|---|
| 2026-10-31 01:23 | 15.9 | 1,521 km | 39 s | same star as the existing event; CA differs from the earlier 0.099″ (newer orbit) |
| 2026-11-26 06:41 | 15.3 | 2,132 km | 29 s | |
| 2027-05-19 08:52 | 13.7 | 3,115 km | 45 s | bright star |
| 2027-05-27 03:46 | 13.1 | 4,871 km | 41 s | brightest star; near Earth's limb |
| 2027-12-02 03:44 | 16.0 | 775 km | 28 s | most central |
| 2028-04-10 22:51 | 14.9 | 6,352 km | 103 s | slow, grazing |
| 2028-05-14 17:52 | 13.7 | 2,923 km | 48 s | bright star |
| 2028-07-24 06:03 | 15.1 | 901 km | 40 s | central |

Caveats: 3σ ephemeris uncertainty (0.04–0.07″ ≈ 1,400–2,400 km) exceeds the ~900 km shadow, so paths need
astrometric refinement before each event; body size is assumed; ground tracks (night side, star altitude) are not
computed yet. Stars are 3–6 mag brighter than the object (V ≈ 19.7), so drops are near-total — good for atmosphere tests.
