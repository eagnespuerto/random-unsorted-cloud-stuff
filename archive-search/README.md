# archsearch: what did every public telescope see of X between dates A and B?

Prototype. Self-contained, so it can be moved to its own repository as-is.

Give it an object and a date range. It:

1. **Resolves the object.** Fixed targets go through Sesame/SIMBAD, or you can give `"ra dec"`. Solar-system objects get a JPL Horizons ephemeris.
2. **Queries many archives in parallel** through the IVOA **ObsCore** standard (`ivoa.obscore` over TAP). The curated set is MAST, IRSA, ESO, CADC, HEASARC, GAVO and CASDA. With `--services all` it adds every ObsCore service in the IVOA registry (~50).
3. **Matches each observation's footprint** (`s_region`) against the object. For moving objects this is done at each exposure's mid-time.
4. **Merges the results.** It groups by facility/instrument, flags mirrored copies (CADC's HST/JWST copies, for example), and exports CSV/JSON.
5. **Optionally**: finds ADS papers (`--papers`), or answers questions in plain English with Claude calling these as tools (`archsearch-ask`).

```bash
pip install -e ".[agent,test]"

archsearch "M87" 2017-01-01 2019-01-01 --exclude Swift/BAT
archsearch "210.910674 54.311653" 2023-05-15 2023-07-01 --services all --out sn2023ixf.csv
archsearch "2026 ED138" 2026-03-15 2026-04-10 --moving --services IRSA

export ANTHROPIC_API_KEY=...  ADS_API_TOKEN=...   # ADS token is free from ui.adsabs.harvard.edu
archsearch-ask "What X-ray and UV data exist for SN 2023ixf in its first two months?"
```

Python API: `from archsearch import search; res = search("M87", "2017-01-01", "2019-01-01")`, then `res.summary()`, `res.rows`, `res.to_csv(...)`.

## Checks so far (live, 2026-11-01)

| Query | Result |
|---|---|
| M87, 2017–2018, 4 archives | 7.6k observations: HST, Chandra, NuSTAR, NEOWISE, ALMA, Swift |
| SN 2023ixf, May 15–Jul 1 2023, all ~50 services | HST, JWST, Gemini, Swift, NICER, NuSTAR, XMM, Chandra, NEOWISE, EVN, DAO; about 2 min |
| 2026 ED138 (moving), Mar 15–Apr 10 2026, IRSA | 116 SPHEREx frames. Matches 116 of the 118 in `../spherex-search` (the 2 missed have the object at a frame edge), with no false positives; 20 s |

## How the queries work around service quirks

Each service gets the most precise query it accepts, worked out on its first query:

- **Fixed target:** `CONTAINS(POINT(target), s_region)`, then `INTERSECTS(CIRCLE, s_region)`, then a pointing-centre circle with a local footprint check.
- **Moving target:** the track is split into segments. Each segment is a point or circle query restricted to that segment's time window. Every returned row is then checked against `s_region` at mid-exposure.
- **Quirks seen in practice:**
  - MAST and IRSA reject `INTERSECTS`.
  - IRSA rejects a parenthesized geometry clause, so segments can't be OR-ed into one query.
  - MAST can time out on the time filter. The fallback queries by position only and filters dates locally, and says so in the status line.
  - Some services lack `s_region` or `obs_release_date`.

## Limitations / next steps

- **Coverage.** Only archives that publish ObsCore are searched. Important missing pieces need custom connectors:
  - ZTF/ATLAS/Pan-STARRS forced photometry
  - TESS full-frame images (TESScut), Gaia epochs
  - Subaru (SMOKA), NOIRLab Astro Data Lab, Rubin, DASCH plates
  - GCN/ATel/TNS for transients
- **Moving objects:** the ephemeris is geocentric. Spacecraft parallax (JWST, TESS, Swift) and fast NEOs need an observer-specific ephemeris. Frames where the object sits at the edge can be missed.
- **Wide-field monitors** (Swift/BAT, Fermi) match almost every position; use `--exclude`.
- **Mirror detection** only matches identical `obs_collection` + `obs_id`.
- **Proprietary data:** `obs_release_date` is returned where available, but nothing is filtered on it yet.
- **"RAG" part:** today the agent sends ADS abstracts straight to Claude. Next: embed abstracts and proposal abstracts (MAST/ESO/Chandra cycles) in a vector store for "who observed this and why" questions; cache archive results; add a small web UI.
- **No async/rate limiting yet:** one thread per service, with a configurable timeout.

## Layout

```
archsearch/resolve.py     name → position or ephemeris (Sesame, SIMBAD, JPL Horizons)
archsearch/services.py    curated archive list + IVOA registry discovery (cached in ~/.cache/archsearch)
archsearch/obscore.py     ADQL generation, per-service fallbacks, moving-target segments
archsearch/geometry.py    STC-S / DALI s_region parsing, point-in-footprint
archsearch/search.py      parallel fan-out, merge, mirror flagging, CSV/JSON export
archsearch/literature.py  NASA ADS search
archsearch/agent.py       Claude tool-use wrapper (archsearch-ask)
archsearch/cli.py         command line
tests/                    offline tests (pytest)
```
