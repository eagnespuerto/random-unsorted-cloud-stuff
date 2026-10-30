---
name: stamp-grid
description: Make a stamp grid PNG of archival stamps / shift-stacks of a moving object (TESS, SPHEREx, Swift/UVOT, etc.) in this repo's house style - non-bold "Object: subtitle" header, non-bold two-line panel titles, red aperture circle on the predicted position. Use when asked for a stamp grid, stamp panel, or cutout grid of detections or non-detections.
---

# Stamp grid

House style (matches `uv-xray-atmosphere/stamp_grid_2026ED138.png`):
- Figure header: `"<Object>: <subtitle>"`, single line, **not bold** (fontsize 13). Subtitle says what the stamps are,
  e.g. `Notable archival detections (template-subtracted, centred on JPL prediction)`.
- Panel title: two lines, not bold (fontsize 11): line 1 = instrument, band, date/pass; line 2 = result
  (flux ± err, σ, or limit). Append `  (N = n)` when n > 3 frames were stacked.
- Grayscale, robust stretch −3σ … +5σ (MAD), origin lower, east left / north up, axes in arcsec.
- Red (`#d62728`, lw 1.3) circle = photometry aperture at the predicted position (stamp centre).
- DejaVu Sans, every weight `normal`; 3 columns, figsize 4.5 × ncols by 5.2 × nrows, dpi 110.
- Save as `stamp_grid_<OBJECT_NO_SPACES>.png` in the object's folder; embed at the top of its README
  (`![...](stamp_grid_....png)`).

## Steps
1. Save each stamp as a 2-D array (`.npy`, or keys in a `.npz`) centred on the predicted position.
   Store stamp half-width and aperture radius in arcsec.
2. Write a `stamp_grid.json` spec next to the stamps (format in the script docstring).
3. Run `python .claude/skills/stamp-grid/make_stamp_grid.py <folder>/stamp_grid.json`.
4. Look at the PNG (Read it) before committing: check that titles fit and the circle is centred.
5. Commit the spec with the PNG so the grid can be regenerated.

Include non-detections when they are the result; then the line-2 text gives the limit
(e.g. `not detected, T > 21.0 (3σ)`) and the subtitle should not say "detections".
