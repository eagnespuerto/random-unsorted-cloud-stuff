# 2026 ED138 — coverage by other space missions

Track 2012–2026: RA ≈ 240–275°, Dec ≈ −46° to −42° (JPL Horizons, daily). `scripts/track.py` interpolates it.

| Mission | Source of pointing log | Closest approach to object | Field reach | Result |
|---|---|---|---|---|
| CHEOPS (2020–) | ESASky TAP `observations.mv_cheops_obs_fdw`, all 2,938 visits (`data/cheops_visits_esasky.csv`) | 2.9° (GJ 674, Jul–Aug 2020) | ~100″ | Not observed |
| NuSTAR (2012–) | HEASARC `numaster`, 235 obs in RA 235–280, Dec −48…−38 (`data/nustar_numaster_box.csv`) | 2.4° (4U 1705−44, Apr 2016) | ~0.1° | Not observed (and no X-ray emission expected) |
| Pandora (2026–) | 20 prime targets, Table 1 of arXiv:2610.30028 | 48° (WASP-80) | small | Not observed (secondary/auxiliary lists unpublished) |
| SVOM VT (2024–) | 2,459 GCN Circulars mentioning SVOM, 591 with positions (`scripts/gcn_check.py`) | 4.5° (sb25043004, 2025-04-30) | ~26′ | No follow-up near the object |
| Euclid (2023–) | ESA archives `eas` (Q1) and `easidr` (DR1, ~250,900 products), `ivoa.obscore` | 47° (NISP/VIS frames at RA 351°, Dec −66°, 2024-11-08) | ~0.75° | Not observed; none within 25° of the track |
| Subaru (1999–) | SMOKA archive, all Subaru instruments, 6,616 frames in RA 225–277°, Dec −47.5…−40.5° (`scripts/smoka_query.py`, `scripts/smoka_check.py`) | 2.5° (COMICS, HD 142527, 2005-08-24); HSC 6.7° | ≤0.75° (HSC) | Not observed |
| AstroSat UVIT (2015–) | UVIT-cat field headers (482 fields, 2016–2022; github.com/swagatastro98/UVIT-cat) | 17° from the track at any time | ~0.23° | Not in catalogued fields |

AstroSat caveat: UVIT-cat excludes fields near the Galactic plane, and the full ISSDC AstroBrowse log needs a login,
so an unlisted UVIT pointing can't be fully excluded. The object would be NUV ≈ 22–23 AB, at or below UVIT depth.
AstroSat's X-ray instruments (SXT, LAXPC, CZTI) cannot detect it.

SVOM caveat: GCN covers burst/transient follow-ups only; planned General Program pointings aren't public here.
ECLAIRs/GRM wide fields are X-ray/gamma-ray and cannot detect the object. `gcn_check.py` expects the GCN archive
(https://gcn.nasa.gov/circulars/archive.json.tar.gz) unpacked under `miss/gcn/x/`.

Euclid caveat: only released data (Q1, DR1) is searchable. The Wide Survey avoids the Galactic plane, and the object
sits at b ≈ −11°, so unreleased survey data is also unlikely to cover it.

Subaru caveat: SMOKA shows only data past its proprietary period (~18 months). Suprime-Cam, FOCAS and MOIRCS have no
frames in the region at all; the object never rises above ~27° altitude from Mauna Kea.
