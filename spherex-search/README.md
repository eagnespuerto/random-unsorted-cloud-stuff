# 2026 ED138 — Kepler/K2 and SPHEREx search

## Kepler / K2 — not observed
In 2009–2018 the object was at RA 249–263°, Dec ≈ −45° (ecliptic latitude ≈ −22°).
- Kepler prime field: closest approach 95°.
- K2 C0–C19: never on silicon (K2fov). Nearest: C11 20.3°, C2 23.4°, C9 24.7° from field centre (fields reach ~7°).

## SPHEREx — detected in Mar–Apr 2026 stack; marginal in 2025
- IRSA ObsCore (`spherex_qr2`/`qr3`): 360 L2 images contain the object, in three passes
  (Aug 23–Oct 2 2025, Mar 20–Apr 3 2026, Aug 20–Sep 8 2026). List: `data/spherex_images_containing_object.csv`.
- Field is ~11° from the Galactic plane, so photometry is template-subtracted: for each image, a 72″ north-up stamp
  at the predicted position minus the median stamp of the same sky from ≤40 same-band images with the object >30″ away.
  7″ aperture, 15–30″ annulus. Null test: identical pipeline on 6 tracks offset 2′.
  (`scripts/sx_get.py`, `scripts/sx_stack.py`; results `data/photometry.json`, image `spherex_stack.png`.)

| Stack | N | Flux (µJy) | Control scatter | Verdict |
|---|---|---|---|---|
| Mar–Apr 2026, 0.75–2.4 µm | 45 | 75 ± 11 | ~6 | **Detected**, peak 7σ, centroid within 0.5″ |
| Aug–Oct 2025, 0.75–2.4 µm (precovery) | 47 | 68 ± 22 | ~25 | Hint only (~2.5–3σ) |
| Aug–Sep 2026, 0.75–2.4 µm | 53 | 27 ± 24 | ~4 | Not detected (star residual nearby) |
| All passes, 0.75–2.4 µm | 150 | 60 ± 13 | ~9 | Detected |
| All passes, 2.4–5 µm | 137 | −2 ± 10 | ~9 | Nothing |

Expected from Rubin (X05) photometry (z ≈ 19.35, y ≈ 19.27): ~70–90 µJy near 1–1.6 µm — consistent.

## MPC cross-check (`data/mpc_observations_ades.json`)
- No SPHEREx observations in the MPC database.
- Same-night overlap: Rubin 2026-03-31 08:28–09:00 UT; SPHEREx 18:58–19:05 UT (4 frames) plus 11 frames on 03-30.
  Those 16 frames alone: 5 ± 33 µJy (too noisy).
- The 2025 SPHEREx pass falls in the gap between W84 (2023-04-07) and Rubin discovery (2026-03-04).
- The 1937 point is Harvard A plate 19892 (Boyden, code 074), DASCH scan, S/N 3.4 — consistent with the
  1885–1936 DASCH search in `../dasch-precovery`.

## Caveats
Template images are at slightly different wavelengths (linear-variable filter), so bright stars leave residuals.
Run used ≤40 templates and 6 control tracks to keep runtime short; a fuller run could tighten the 2025 result.
