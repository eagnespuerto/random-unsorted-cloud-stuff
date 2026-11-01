"""Fan an object + date range out to many ObsCore archives in parallel and merge the results."""
from __future__ import annotations

import csv
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from astropy.time import Time

from .obscore import query_service
from .resolve import Target, resolve
from .services import pick


@dataclass
class Result:
    target: Target
    start: str
    end: str
    rows: list[dict] = field(default_factory=list)   # each row has a 'service' key
    status: dict[str, str] = field(default_factory=dict)  # service -> "N rows (mode)" or error

    def summary(self) -> list[dict]:
        """Rows grouped by facility / instrument / collection, with date span and counts.
        Rows flagged as mirrors of another archive's copy are left out."""
        groups: dict[tuple, dict] = {}
        for r in self.rows:
            if r.get("mirror_of"):
                continue
            key = (r["service"], r.get("facility_name") or "?", r.get("instrument_name") or "?", r.get("obs_collection") or "?")
            g = groups.setdefault(key, {"n": 0, "first": None, "last": None, "types": Counter()})
            g["n"] += 1
            g["types"][r.get("dataproduct_type") or "?"] += 1
            for t in (r.get("t_min"),):
                if t is not None:
                    g["first"] = t if g["first"] is None else min(g["first"], t)
                    g["last"] = t if g["last"] is None else max(g["last"], t)
        out = []
        for (svc, fac, inst, coll), g in sorted(groups.items(), key=lambda kv: -kv[1]["n"]):
            out.append({
                "service": svc, "facility": fac, "instrument": inst, "collection": coll, "n": g["n"],
                "first": _iso(g["first"]), "last": _iso(g["last"]),
                "types": ", ".join(f"{k}:{v}" for k, v in g["types"].most_common()),
            })
        return out

    def to_csv(self, path: str):
        cols = ["service"] + sorted({k for r in self.rows for k in r} - {"service"})
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, cols)
            w.writeheader()
            w.writerows(self.rows)

    def to_json(self, path: str):
        with open(path, "w") as f:
            json.dump({"target": self.target.name, "moving": self.target.moving, "start": self.start, "end": self.end,
                       "status": self.status, "summary": self.summary(), "rows": self.rows}, f, indent=1, default=str)


def _iso(mjd):
    return None if mjd is None else Time(mjd, format="mjd").iso[:10]


def search(name: str, start: str, end: str, services=None, moving: bool | None = None,
           radius_arcsec: float = 10.0, maxrec: int = 5000, timeout: float = 90,
           workers: int = 12, progress=None, exclude=None) -> Result:
    """Find observations of `name` between `start` and `end` (any astropy Time string)
    in every selected ObsCore archive. `services`: see services.pick().
    `exclude`: collection/instrument substrings to drop (e.g. ["Swift/BAT"])."""
    t0, t1 = Time(start), Time(end)
    target = resolve(name, t0, t1, moving)
    res = Result(target, t0.iso[:10], t1.iso[:10])
    svcs = pick(services)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(query_service, url, target, t0.mjd, t1.mjd, radius_arcsec / 3600, maxrec, timeout): n
                for n, url in svcs.items()}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                rows, note = fut.result()
                if exclude:
                    ex_l = [x.lower() for x in exclude]
                    rows = [r for r in rows if not any(
                        x in f"{r.get('obs_collection')} {r.get('instrument_name')}".lower() for x in ex_l)]
                for r in rows:
                    r["service"] = n
                res.rows.extend(rows)
                res.status[n] = f"{len(rows)} rows ({note})"
            except Exception as e:
                res.status[n] = f"error: {e}"
            if progress:
                progress(n, res.status[n])
    res.rows.sort(key=lambda r: r.get("t_min") or 0)
    _mark_mirrors(res.rows, list(svcs))
    return res


def _mark_mirrors(rows: list[dict], order: list[str]):
    """Archives mirror each other (e.g. CADC holds HST/JWST copies). Flag a row as
    `mirror_of` the first service (in `order`) that has the same collection + obs_id."""
    rank = {n: i for i, n in enumerate(order)}
    first: dict[tuple, str] = {}
    for r in sorted(rows, key=lambda r: rank.get(r["service"], 999)):
        oid = r.get("obs_id")
        if not oid:
            continue
        k = (str(r.get("obs_collection") or "").upper(), str(oid).lower())
        if k in first and first[k] != r["service"]:
            r["mirror_of"] = first[k]
        else:
            first.setdefault(k, r["service"])
