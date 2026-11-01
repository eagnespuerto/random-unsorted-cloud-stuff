"""ADQL against ivoa.obscore, with fallbacks for services that lack s_region or optional columns."""
from __future__ import annotations

import math

import numpy as np
import pyvo
import requests

from .geometry import contains as region_contains
from .resolve import Target

COLS = ("obs_collection, facility_name, instrument_name, dataproduct_type, calib_level, "
        "obs_id, target_name, s_ra, s_dec, s_fov, t_min, t_max, t_exptime, em_min, em_max, "
        "access_url, access_format")
# Tried in order until the service accepts one (s_region and obs_release_date are not everywhere).
COL_SETS = (COLS + ", s_region, obs_release_date", COLS + ", s_region", COLS)


class _TimeoutSession(requests.Session):
    def __init__(self, timeout: float):
        super().__init__()
        self._timeout = timeout

    def request(self, *a, **kw):
        kw.setdefault("timeout", self._timeout)
        return super().request(*a, **kw)


def _segments(target: Target, mjd0: float, mjd1: float, radius: float,
              max_span: float = 1.0, max_segments: int = 60):
    """(ra, dec, r, t0, t1) pieces covering the track in [mjd0, mjd1]; the object moves
    at most ~max_span deg from the segment's mid-point."""
    if not target.moving:
        return [(target.ra, target.dec, radius, mjd0, mjd1)]
    ts = [mjd0 + (mjd1 - mjd0) * i / 200 for i in range(201)]
    path = sum(_sep(*target.position_at(a), *target.position_at(b)) for a, b in zip(ts[:-1], ts[1:]))
    n = int(min(max_segments, max(1, math.ceil(path / (2 * max_span)), math.ceil((mjd1 - mjd0) / 30))))
    edges = [mjd0 + (mjd1 - mjd0) * i / n for i in range(n + 1)]
    segs = []
    for t0, t1 in zip(edges[:-1], edges[1:]):
        ram, dem = target.position_at(0.5 * (t0 + t1))
        span = max(_sep(*target.position_at(t0), ram, dem), _sep(*target.position_at(t1), ram, dem))
        segs.append((ram, dem, span + radius, t0, t1))
    return segs


def _sep(ra1, de1, ra2, de2):
    r1, d1, r2, d2 = map(math.radians, (ra1, de1, ra2, de2))
    c = math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(r1 - r2)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def _geo(ra, dec, r, mode: str, pad: float = 0.25) -> str:
    if mode == "contains":      # target point inside the footprint (fixed targets)
        return f"CONTAINS(POINT('ICRS', {ra:.6f}, {dec:.6f}), s_region)=1"
    if mode == "intersects":    # search circle overlaps the footprint
        return f"INTERSECTS(CIRCLE('ICRS', {ra:.6f}, {dec:.6f}, {r:.6f}), s_region)=1"
    # pointing centre within r + pad; post-filtered with s_region / s_fov
    return f"CONTAINS(POINT('ICRS', s_ra, s_dec), CIRCLE('ICRS', {ra:.6f}, {dec:.6f}, {r + pad:.6f}))=1"


MODE_NOTE = {"contains": "footprint", "intersects": "footprint", "centre": "pointing-centre search"}


def _is_network(e: Exception) -> bool:
    m = str(e).lower()
    return isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)) or \
        any(k in m for k in ("proxy", "timed out", "timeout", "504", "gateway", "connection"))


def _run(svc, sql: str, maxrec: int):
    tab = svc.run_sync(sql, maxrec=maxrec).to_table()
    return [{k: _clean(row[k]) for k in tab.colnames} for row in tab]


def query_service(url: str, target: Target, mjd0: float, mjd1: float,
                  radius: float = 0.003, maxrec: int = 5000, timeout: float = 90) -> tuple[list[dict], str]:
    """Return (rows, note). Picks the most precise geometry the service accepts, learned
    on the first track segment. Quirks seen in practice: MAST and IRSA reject INTERSECTS;
    IRSA rejects a parenthesized geometry clause (so segments can't be OR-ed into one
    query); MAST can time out on a server-side time filter, so we retry with geometry only
    and filter on time locally. Moving-target rows are then checked against s_region at
    each exposure's mid-time."""
    svc = pyvo.dal.TAPService(url, session=_TimeoutSession(timeout))
    if target.moving:
        # contains: point query at each segment mid-point, so keep segments short
        modes = [("intersects", 1.0, 0.0), ("contains", 0.1, 0.0), ("centre", 1.0, 2.0)]
    else:
        modes = [("contains", 1.0, 0.0), ("intersects", 1.0, 0.0), ("centre", 1.0, 0.25)]

    def attempt(seg, mode, pad, cols, server_time):
        ra, dec, r, t0, t1 = seg
        where = _geo(ra, dec, r, mode, pad)
        if server_time:
            where += f" AND t_min <= {t1:.6f} AND t_max >= {t0:.6f}"
        rows = _run(svc, f"SELECT TOP {maxrec} {cols} FROM ivoa.obscore WHERE {where}", maxrec)
        if len(rows) >= maxrec:
            truncated[0] = True
        if not server_time:
            rows = [x for x in rows if x.get("t_min") is not None
                    and x["t_min"] <= t1 and (x.get("t_max") or x["t_min"]) >= t0]
        return rows

    errors, plan, rows, truncated = [], None, [], [False]
    for mode, span, pad in modes:
        segs = _segments(target, mjd0, mjd1, radius, max_span=span)
        for cols in COL_SETS:
            for server_time in (True, False):
                try:
                    rows = attempt(segs[0], mode, pad, cols, server_time)
                    plan = (mode, pad, cols, server_time, segs)
                    break
                except Exception as e:
                    errors.append(f"{mode}: {str(e)[:100]}")
                    if _is_network(e) and server_time:
                        continue          # retry without the time filter
                    if _is_network(e):
                        raise RuntimeError(f"unreachable/slow: {str(e)[:120]}") from e
                    break                 # syntax/column problem: next column set
            if plan:
                break
        if plan:
            break
    if not plan:
        raise RuntimeError(" | ".join(errors[-2:]))

    mode, pad, cols, server_time, segs = plan
    for seg in segs[1:]:
        rows += attempt(seg, mode, pad, cols, server_time)
    note = MODE_NOTE[mode]
    if target.moving or mode == "centre":
        rows = [r for r in rows if _on_target(r, target, radius)]
        note += ", footprint checked locally"
    if not server_time:
        note += ", time filtered locally"
    if truncated[0]:
        note += ", INCOMPLETE: hit maxrec before date filter, raise --maxrec" if not server_time else ", hit maxrec"
    return _dedupe(rows), note


def _on_target(row, target: Target, radius: float) -> bool:
    """Is the object inside this observation's footprint at mid-exposure?"""
    try:
        tmid = 0.5 * (float(row["t_min"]) + float(row.get("t_max") or row["t_min"]))
    except (TypeError, ValueError, KeyError):
        return True
    ra, dec = target.position_at(tmid)
    inside = region_contains(row.get("s_region"), ra, dec, margin=radius)
    if inside is not None:
        return inside
    return _near_track(row, target, radius)


def _dedupe(rows):
    seen, out = set(), []
    for r in rows:
        k = (r.get("obs_collection"), r.get("obs_id"), r.get("access_url"))
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def _near_track(row, target: Target, radius: float) -> bool:
    """Post-filter for moving targets: object position at mid-exposure vs. pointing centre."""
    try:
        tmid = 0.5 * (float(row["t_min"]) + float(row["t_max"]))
        ra, dec = target.position_at(tmid)
        fov = float(row.get("s_fov") or 0) or 0.5
        return _sep(ra, dec, float(row["s_ra"]), float(row["s_dec"])) <= fov / 2 * 1.42 + radius
    except (TypeError, ValueError, KeyError):
        return True  # can't check; keep it


def _clean(v):
    if v is np.ma.masked:
        return None
    if isinstance(v, bytes):
        return v.decode()
    if isinstance(v, np.generic):
        v = v.item()
    if isinstance(v, float) and math.isnan(v):
        return None
    return v
