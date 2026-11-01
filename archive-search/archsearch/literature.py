"""Papers about the object from NASA ADS (needs ADS_API_TOKEN; free at ui.adsabs.harvard.edu)."""
from __future__ import annotations

import os

import requests

ADS_URL = "https://api.adsabs.harvard.edu/v1/search/query"


def ads_papers(name: str, start: str, end: str, rows: int = 50) -> list[dict]:
    """Papers mentioning the object, published between start and end (YYYY-MM-DD).
    Uses SIMBAD-linked object: search plus a quoted full-text fallback."""
    token = os.environ.get("ADS_API_TOKEN")
    if not token:
        raise RuntimeError("Set ADS_API_TOKEN to search the literature")
    q = f'(object:"{name}" OR abs:"{name}") pubdate:[{start[:7]} TO {end[:7]}]'
    r = requests.get(
        ADS_URL,
        params={"q": q, "fl": "bibcode,title,author,pubdate,abstract,doi", "rows": rows, "sort": "date desc"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    out = []
    for d in r.json()["response"]["docs"]:
        out.append({
            "bibcode": d["bibcode"],
            "title": (d.get("title") or [""])[0],
            "authors": ", ".join((d.get("author") or [])[:3]) + (" et al." if len(d.get("author") or []) > 3 else ""),
            "pubdate": d.get("pubdate"),
            "abstract": d.get("abstract", ""),
            "url": f"https://ui.adsabs.harvard.edu/abs/{d['bibcode']}",
        })
    return out
