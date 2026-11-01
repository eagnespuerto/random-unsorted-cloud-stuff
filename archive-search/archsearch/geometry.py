"""Minimal s_region handling: parse STC-S / DALI polygons and circles, test point containment."""
from __future__ import annotations

import math
import re

_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_SHAPE = re.compile(r"(POLYGON|CIRCLE|BOX|POSITION|POINT)", re.I)


def parse_region(s) -> list[tuple[str, list[float]]] | None:
    """Return [(shape, numbers), ...] or None if unparseable. UNION -> several shapes."""
    if s is None:
        return None
    if not isinstance(s, str):  # DALI polygon as float array
        try:
            v = [float(x) for x in s]
            return [("POLYGON", v)] if len(v) >= 6 else None
        except TypeError:
            return None
    parts = _SHAPE.split(s)
    shapes = []
    for i in range(1, len(parts) - 1, 2):
        nums = [float(x) for x in _NUM.findall(parts[i + 1])]
        shapes.append((parts[i].upper(), nums))
    return shapes or None


def _tan(ra, dec, ra0, dec0):
    """Gnomonic projection (deg) about (ra0, dec0)."""
    r, d, r0, d0 = map(math.radians, (ra, dec, ra0, dec0))
    cosc = math.sin(d0) * math.sin(d) + math.cos(d0) * math.cos(d) * math.cos(r - r0)
    if cosc <= 0:
        return None
    x = math.cos(d) * math.sin(r - r0) / cosc
    y = (math.cos(d0) * math.sin(d) - math.sin(d0) * math.cos(d) * math.cos(r - r0)) / cosc
    return math.degrees(x), math.degrees(y)


def _sep(ra1, de1, ra2, de2):
    r1, d1, r2, d2 = map(math.radians, (ra1, de1, ra2, de2))
    c = math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(r1 - r2)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def contains(region, ra: float, dec: float, margin: float = 0.0) -> bool | None:
    """True/False if the point (within `margin` deg) lies in the region; None if unknown."""
    shapes = parse_region(region)
    if not shapes:
        return None
    known = False
    for shape, v in shapes:
        if shape == "CIRCLE" and len(v) >= 3:
            known = True
            if _sep(ra, dec, v[-3], v[-2]) <= v[-1] + margin:
                return True
        elif shape == "POLYGON" and len(v) >= 6 and len(v) % 2 == 0:
            known = True
            pts = [_tan(v[i], v[i + 1], ra, dec) for i in range(0, len(v), 2)]
            if any(p is None for p in pts):
                continue
            if _point_in_poly(pts) or (margin and min(math.hypot(*p) for p in pts) <= margin):
                return True
            if margin and _dist_to_edges(pts) <= margin:
                return True
    return False if known else None


def _point_in_poly(pts) -> bool:
    """Ray casting for the origin (the projected test point)."""
    inside = False
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        if (y1 > 0) != (y2 > 0) and 0 < x1 + (0 - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def _dist_to_edges(pts) -> float:
    best = float("inf")
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0, min(1, -(x1 * dx + y1 * dy) / L))
        best = min(best, math.hypot(x1 + t * dx, y1 + t * dy))
    return best
