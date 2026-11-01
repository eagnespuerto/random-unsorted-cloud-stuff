"""archsearch "M87" 2019-01-01 2020-01-01 [--moving] [--services curated|registry|all|MAST,IRSA] [--out hits.csv]"""
from __future__ import annotations

import argparse
import sys

from .search import search


def main(argv=None):
    p = argparse.ArgumentParser(prog="archsearch", description="Search public telescope archives for an object over a date range.")
    p.add_argument("object", help='Name ("M87", "2026 ED138", "SN 2023ixf") or "ra dec" in degrees')
    p.add_argument("start", help="Start date, e.g. 2020-01-01")
    p.add_argument("end", help="End date, e.g. 2021-01-01")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--moving", dest="moving", action="store_true", default=None, help="Force Horizons ephemeris (solar-system object)")
    g.add_argument("--fixed", dest="moving", action="store_false", help="Force fixed-target lookup")
    p.add_argument("--services", default="curated", help="curated (default), registry, all, or comma list of names/TAP URLs")
    p.add_argument("--radius", type=float, default=10.0, help="Search radius in arcsec (default 10)")
    p.add_argument("--maxrec", type=int, default=5000)
    p.add_argument("--timeout", type=float, default=90, help="Per-service timeout in seconds")
    p.add_argument("--exclude", help='Comma list of collection/instrument substrings to drop, e.g. "Swift/BAT"')
    p.add_argument("--out", help="Write all rows to .csv or .json")
    p.add_argument("--papers", action="store_true", help="Also list ADS papers (needs ADS_API_TOKEN)")
    a = p.parse_args(argv)

    err = lambda *x: print(*x, file=sys.stderr)
    res = search(a.object, a.start, a.end, a.services, a.moving, a.radius, a.maxrec, a.timeout,
                 progress=lambda n, s: err(f"  {n:<10} {s}"),
                 exclude=a.exclude.split(",") if a.exclude else None)
    t = res.target
    where = f"RA {t.ra:.5f} Dec {t.dec:+.5f}" if not t.moving else f"moving, {len(t.eph_mjd)} ephemeris points"
    print(f"\n{t.name} ({where}), {res.start} → {res.end}: {len(res.rows)} observations\n")
    s = res.summary()
    if s:
        hdr = f"{'service':<9} {'facility':<14} {'instrument':<16} {'collection':<18} {'n':>6}  {'first':<10}  {'last':<10}"
        print(hdr + "\n" + "-" * len(hdr))
        for g in s:
            print(f"{g['service'][:9]:<9} {g['facility'][:14]:<14} {g['instrument'][:16]:<16} {g['collection'][:18]:<18} "
                  f"{g['n']:>6}  {g['first'] or '':<10}  {g['last'] or '':<10}")
    if a.out:
        (res.to_json if a.out.endswith(".json") else res.to_csv)(a.out)
        print(f"\nWrote {a.out}")
    if a.papers:
        from .literature import ads_papers
        try:
            papers = ads_papers(t.name, res.start, res.end)
            print(f"\nADS: {len(papers)} papers")
            for pp in papers[:20]:
                print(f"  {pp['pubdate'][:7]}  {pp['authors'][:30]:<30}  {pp['title'][:80]}")
        except Exception as e:
            err(f"ADS: {e}")


if __name__ == "__main__":
    main()
