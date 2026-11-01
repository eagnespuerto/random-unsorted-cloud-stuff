"""Offline tests (no network)."""
import numpy as np

from archsearch.geometry import contains, parse_region
from archsearch.obscore import _geo, _segments
from archsearch.resolve import Target, resolve_fixed
from archsearch.services import CURATED, pick


def test_polygon_and_circle():
    sq = "POLYGON ICRS 10 10 11 10 11 11 10 11"
    assert contains(sq, 10.5, 10.5) is True
    assert contains(sq, 12, 10.5) is False
    assert contains(sq, 11.002, 10.5, margin=0.01) is True        # near edge, within margin
    assert contains("POLYGON 359.5 0 0.5 0 0.5 1 359.5 1", 0.1, 0.5) is True   # RA wrap
    assert contains("CIRCLE ICRS 10 10 1", 10.5, 10.2) is True
    assert contains("UNION (Polygon ICRS 1 1 2 1 2 2 1 2) (Circle ICRS 50 0 1)", 50.2, 0.1) is True
    assert contains(None, 1, 1) is None
    assert contains(np.array([10, 10, 11, 10, 11, 11, 10, 11.0]), 10.5, 10.5) is True  # DALI array
    assert parse_region("garbage") is None


def test_coordinates_input():
    t = resolve_fixed("187.7 12.39")
    assert not t.moving and t.ra == 187.7 and t.dec == 12.39


def test_moving_interpolation_wraps_ra():
    t = Target("x", True, eph_mjd=np.array([0.0, 1.0]), eph_ra=np.array([359.8, 0.2]), eph_dec=np.array([0.0, 0.0]))
    ra, dec = t.position_at(0.5)
    assert abs(ra - 0.0) < 1e-6 or abs(ra - 360.0) < 1e-6


def test_segments_cover_track():
    t = Target("x", True, eph_mjd=np.array([0.0, 10.0]), eph_ra=np.array([10.0, 20.0]), eph_dec=np.array([0.0, 0.0]))
    segs = _segments(t, 0, 10, 0.001, max_span=1.0)
    assert len(segs) >= 5
    assert segs[0][3] == 0 and abs(segs[-1][4] - 10) < 1e-9
    fixed = _segments(Target("y", False, 1, 2), 0, 10, 0.01)
    assert fixed == [(1, 2, 0.01, 0, 10)]


def test_adql_has_no_parentheses_around_geometry():
    # IRSA rejects "(CONTAINS(...)=1 AND ...)"
    q = _geo(1, 2, 0.1, "contains")
    assert q.startswith("CONTAINS(") and q.endswith("=1")


def test_pick_services():
    assert pick(None) == CURATED
    assert pick("mast,IRSA") == {"MAST": CURATED["MAST"], "IRSA": CURATED["IRSA"]}
    assert pick(["https://example.org/tap"]) == {"https://example.org/tap": "https://example.org/tap"}
