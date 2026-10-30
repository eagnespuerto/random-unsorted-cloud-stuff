# 2026 ED138 — coverage by other space missions

Track 2012–2026: RA ≈ 240–275°, Dec ≈ −46° to −42° (JPL Horizons, daily). `scripts/track.py` interpolates it.

| Mission | Source of pointing log | Closest approach to object | Field reach | Result |
|---|---|---|---|---|
| CHEOPS (2020–) | ESASky TAP `observations.mv_cheops_obs_fdw`, all 2,938 visits (`data/cheops_visits_esasky.csv`) | 2.9° (GJ 674, Jul–Aug 2020) | ~100″ | Not observed |
| NuSTAR (2012–) | HEASARC `numaster`, 235 obs in RA 235–280, Dec −48…−38 (`data/nustar_numaster_box.csv`) | 2.4° (4U 1705−44, Apr 2016) | ~0.1° | Not observed (and no X-ray emission expected) |
| AstroSat UVIT (2015–) | UVIT-cat field headers (482 fields, 2016–2022; github.com/swagatastro98/UVIT-cat) | 17° from the track at any time | ~0.23° | Not in catalogued fields |

AstroSat caveat: UVIT-cat excludes fields near the Galactic plane, and the full ISSDC AstroBrowse log needs a login,
so an unlisted UVIT pointing can't be fully excluded. The object would be NUV ≈ 22–23 AB, at or below UVIT depth.
AstroSat's X-ray instruments (SXT, LAXPC, CZTI) cannot detect it.
