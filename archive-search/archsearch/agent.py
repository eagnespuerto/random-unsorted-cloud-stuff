"""Ask questions in plain English; Claude calls the archive and ADS search tools.

    export ANTHROPIC_API_KEY=...   (or `ant auth login`)
    export ADS_API_TOKEN=...       (optional, for papers)
    archsearch-ask "What X-ray data exist for M87 during the 2017 EHT campaign?"
"""
from __future__ import annotations

import json
import sys

import anthropic
from anthropic import beta_tool

from .literature import ads_papers
from .search import search

MODEL = "claude-opus-5-5"
SYSTEM = """You help astronomers find archival observations and papers about an object over a date range.
Use search_archives for observations (IVOA ObsCore services: MAST, IRSA, ESO, CADC, HEASARC, GAVO, CASDA)
and search_papers for literature. Report what exists by facility/instrument with dates and counts, note
services that failed or were truncated, separate wide-field monitoring (e.g. Swift/BAT) from pointed
observations, and say plainly when coverage is missing. Cite obs_collection names and ADS bibcodes."""

_last = {}


@beta_tool
def search_archives(object_name: str, start_date: str, end_date: str, moving: str = "auto",
                    services: str = "curated") -> str:
    """Find observations of an astronomical object in public telescope archives.

    Args:
        object_name: Object name ("M87", "SN 2023ixf", "2026 ED138") or "ra dec" in degrees.
        start_date: Start date, YYYY-MM-DD.
        end_date: End date, YYYY-MM-DD.
        moving: "yes" for solar-system objects (uses JPL Horizons), "no" for fixed targets, "auto" to try both.
        services: "curated" (major archives), "registry" (every ObsCore service, slow), or comma list like "MAST,IRSA".
    """
    mv = {"yes": True, "no": False}.get(moving)
    try:
        res = search(object_name, start_date, end_date, services, mv)
    except Exception as e:
        return json.dumps({"error": str(e)})
    _last["result"] = res
    t = res.target
    return json.dumps({
        "target": t.name, "moving": t.moving,
        "position": None if t.moving else [round(t.ra, 5), round(t.dec, 5)],
        "n_observations": len(res.rows), "service_status": res.status,
        "summary": res.summary()[:60],
    }, default=str)


@beta_tool
def search_papers(object_name: str, start_date: str, end_date: str) -> str:
    """Search NASA ADS for papers about an object published in a date range. Returns titles and abstracts.

    Args:
        object_name: Object name.
        start_date: Start date, YYYY-MM-DD.
        end_date: End date, YYYY-MM-DD.
    """
    try:
        papers = ads_papers(object_name, start_date, end_date, rows=25)
    except Exception as e:
        return json.dumps({"error": str(e)})
    for p in papers:
        p["abstract"] = p["abstract"][:1200]
    return json.dumps(papers)


def ask(question: str, verbose: bool = True) -> str:
    client = anthropic.Anthropic()
    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        tools=[search_archives, search_papers],
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": question}],
    )
    final = None
    for message in runner:
        final = message
        if verbose:
            for b in message.content:
                if b.type == "tool_use":
                    print(f"→ {b.name}({json.dumps(b.input)})", file=sys.stderr)
    if final is None or final.stop_reason == "refusal":
        return "(no answer: request was declined)"
    return "".join(b.text for b in final.content if b.type == "text")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print(ask(" ".join(sys.argv[1:])))


if __name__ == "__main__":
    main()
