"""Turn an object name into a sky position (fixed target) or an ephemeris (moving target)."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.time import Time


@dataclass
class Target:
    name: str
    moving: bool
    ra: float | None = None   # deg, fixed targets
    dec: float | None = None
    # moving targets: arrays of MJD (UTC), RA, Dec (deg), geocentric
    eph_mjd: np.ndarray = field(default_factory=lambda: np.array([]))
    eph_ra: np.ndarray = field(default_factory=lambda: np.array([]))
    eph_dec: np.ndarray = field(default_factory=lambda: np.array([]))

    def position_at(self, mjd: float) -> tuple[float, float]:
        if not self.moving:
            return self.ra, self.dec
        # unwrap RA so interpolation across 0/360 works
        ra = np.degrees(np.unwrap(np.radians(self.eph_ra)))
        return float(np.interp(mjd, self.eph_mjd, ra) % 360), float(np.interp(mjd, self.eph_mjd, self.eph_dec))


def resolve_fixed(name: str) -> Target | None:
    """Sesame (SIMBAD/NED/VizieR) name lookup. Also accepts 'ra dec' in degrees."""
    parts = name.replace(",", " ").split()
    if len(parts) == 2:
        try:
            return Target(name, False, float(parts[0]), float(parts[1]))
        except ValueError:
            pass
    try:
        c = SkyCoord.from_name(name)
        return Target(name, False, float(c.ra.deg), float(c.dec.deg))
    except Exception:
        pass
    try:  # Sesame can be flaky; ask SIMBAD directly
        from astroquery.simbad import Simbad
        tab = Simbad.query_object(name)
        if tab is not None and len(tab):
            return Target(name, False, float(tab["ra"][0]), float(tab["dec"][0]))
    except Exception:
        pass
    return None


def resolve_moving(name: str, start: Time, end: Time, step: str | None = None) -> Target | None:
    """JPL Horizons geocentric ephemeris. Fine for space telescopes far from Earth's
    neighbourhood only roughly; nearby NEOs need the observatory's own location."""
    from astroquery.jplhorizons import Horizons

    if step is None:
        days = max(end.mjd - start.mjd, 1)
        step = f"{max(1, int(days / 400))}d" if days > 2 else "1h"
    epochs = {"start": start.iso[:16], "stop": end.iso[:16], "step": step}
    for id_type in ("smallbody", None):
        try:
            eph = Horizons(id=name, location="500@399", epochs=epochs, id_type=id_type).ephemerides()
            break
        except Exception:
            eph = None
    if eph is None or len(eph) == 0:
        return None
    mjd = Time(np.asarray(eph["datetime_jd"]), format="jd").mjd
    return Target(name, True, eph_mjd=mjd, eph_ra=np.asarray(eph["RA"], float), eph_dec=np.asarray(eph["DEC"], float))


def resolve(name: str, start: Time, end: Time, moving: bool | None = None) -> Target:
    """moving=None tries a fixed-target lookup first, then Horizons."""
    if moving is not True:
        t = resolve_fixed(name)
        if t:
            return t
        if moving is False:
            raise ValueError(f"Could not resolve '{name}' with Sesame")
    t = resolve_moving(name, start, end)
    if t:
        return t
    raise ValueError(f"Could not resolve '{name}' (Sesame or JPL Horizons)")
