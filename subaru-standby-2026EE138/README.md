# 2026 EE138 — Subaru follow-up (on standby)

Waiting on accounts. Coverage was found in `../tess-gaia-2026EE138` (SMOKA search, 2026-10-30): 22 public
Subaru exposures contain the object, each expected to detect it (S/N ~20–80). Nothing downloaded yet.

## Why it matters
- **Colours:** HSC-SSP Wide (Jan–Feb 2020) has g, r2, i2, z and Y within ~5 weeks → g−r, r−i, i−z, z−Y on
  one system. Pan-STARRS stacks give only i = 22.43 ± 0.11 and r = 22.91 ± 0.29; Swift/SPHEREx give nothing.
- **Precovery astrometry:** Suprime-Cam 2004-06-17 (3 × 60 s VR) would extend the arc 9 years back
  (first obs now 2013-04-01). HSC 2016-03-17 (6 × 30 s r) adds a well-sampled night. Single-epoch positions
  can go to the MPC, unlike the Pan-STARRS stack.

## Exposures (`exposures.csv`)
| Date | Instrument / programme | Filter × exp | Offset | JPL 3σ | Est. S/N |
|---|---|---|---|---|---|
| 2004-06-17 | Suprime-Cam, F43 | VR × 3 × 60 s | 0.18° | 4.4″ | ~24 |
| 2016-03-17 | HSC, Jedicke | r × 6 × 30 s | 0.14° | 0.5″ | ~26 |
| 2020-01-19 – 01-30 | HSC-SSP Wide | z × 2, Y × 3, i × 4 (200 s) | 0.50–0.74° | 0.7″ | 22–76 |
| 2020-02-19 – 02-25 | HSC-SSP Wide | z, g × 2, r (150–200 s) | 0.36–0.48° | 0.6″ | 49–77 |

`edge` in `exposures.csv` = offset > 0.7° (2020-01-28 Y, 2020-01-30 z): may fall off-chip or in a gap.

## Accounts (free)
1. SMOKA (raw frames, all 22 exposures): https://smoka.nao.ac.jp/register.jsp
2. HSC-SSP Public Data Release (processed single-visit images, 2020 SSP data):
   https://hsc-release.mtk.nao.ac.jp/datasearch/new_user/new — docs https://hsc-release.mtk.nao.ac.jp/doc/

Don't paste passwords into a chat or commit them; downloads are done by whoever holds the account.

## Plan once access is in place
1. **SMOKA:** request the frames in `smoka_frame_ids.txt` (2,158 CCD frames = all CCDs of the 22 exposures;
   only one CCD per exposure holds the object, picked from the WCS after download). Raw frames need bias/flat
   (SMOKA calibration frames from the same nights) — or use processed HSC-SSP data where it exists.
2. **HSC-SSP:** fetch single-visit calexp CCDs (not coadds — coadds reject/smear moving objects) for the
   12 SSP exposures at the positions in `exposures.csv`.
3. Per exposure: forced PSF photometry at the JPL position, local template from other visits of the same
   field, centroid → astrometry vs Gaia DR3. Colours from same-night/same-run pairs where possible;
   the ~5-week span changes distance and phase angle only slightly at Δ ≈ 72 au; correct with Horizons V.
4. Add results to a stamp grid (`/stamp-grid` skill) and report precovery positions (2004, 2016) to the MPC.

## Source
Frame list from `../tess-gaia-2026EE138/data/subaru_smoka.json`; per-exposure geometry from
`../tess-gaia-2026EE138/data/subaru_exposures.json` (`scripts/subaru_exposures.py`).
