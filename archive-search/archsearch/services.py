"""Which archives to query: a curated list, or every ObsCore TAP service in the IVOA registry."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

# Large, reliable ObsCore services. Name -> TAP base URL.
CURATED = {
    "MAST": "https://mast.stsci.edu/vo-tap/api/v0.1/caom",          # HST, JWST, TESS, GALEX, Kepler, PS1...
    "IRSA": "https://irsa.ipac.caltech.edu/TAP",                     # Spitzer, WISE, SPHEREx, ZTF, 2MASS...
    "ESO": "https://archive.eso.org/tap_obs",                         # VLT, VISTA, VST, La Silla
    "CADC": "https://ws.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/argus",              # CFHT, Gemini, JCMT, HST copies
    "HEASARC": "https://heasarc.gsfc.nasa.gov/xamin/vo/tap",          # Chandra, Swift, XMM, NuSTAR, Fermi...
    "GAVO": "https://dc.g-vo.org/tap",                                # plate archives, assorted surveys
    "CASDA": "https://casda.csiro.au/casda_vo_tools/tap",             # ASKAP radio
}

CACHE = Path(os.environ.get("ARCHSEARCH_CACHE", Path.home() / ".cache" / "archsearch"))


def registry_services(max_age_days: float = 7) -> dict[str, str]:
    """All TAP services in the IVOA registry that declare the ObsCore data model (cached)."""
    path = CACHE / "obscore_services.json"
    if path.exists() and time.time() - path.stat().st_mtime < max_age_days * 86400:
        return json.loads(path.read_text())
    import pyvo

    found = {}
    for res in pyvo.registry.search(datamodel="obscore"):
        try:
            url = res.get_service("tap").baseurl
        except Exception:
            continue
        name = res.short_name or res.ivoid
        found.setdefault(name, url)
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(found, indent=1))
    return found


def pick(spec: str | list[str] | None) -> dict[str, str]:
    """'curated' (default), 'registry', 'all' (both), or a list of names / TAP URLs."""
    if spec in (None, "curated"):
        return dict(CURATED)
    if spec == "registry":
        return registry_services()
    if spec == "all":  # curated names win; drop registry entries pointing at the same URL
        out = dict(CURATED)
        seen = {_norm(u) for u in CURATED.values()}
        for n, u in registry_services().items():
            if _norm(u) not in seen and n not in out:
                seen.add(_norm(u))
                out[n] = u
        return out
    items = spec.split(",") if isinstance(spec, str) else spec
    out = {}
    for s in items:
        s = s.strip()
        if s.startswith("http"):
            out[s] = s
        elif s.upper() in CURATED:
            out[s.upper()] = CURATED[s.upper()]
        else:
            raise ValueError(f"Unknown service '{s}'. Known: {', '.join(CURATED)} or a TAP URL")
    return out


def _norm(url: str) -> str:
    return url.split("://", 1)[-1].rstrip("/").lower()
