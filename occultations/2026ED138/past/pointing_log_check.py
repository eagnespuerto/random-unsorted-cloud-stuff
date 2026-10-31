import json, math, csv, re
from astropy.io.votable import parse_single_table as P
from astropy.time import Time
from scipy.stats import norm
E = [e for e in json.load(open("past/events.json")) if e["frame"] == "geocentric"]
def sep(a, b, c, d):
    a, b, c, d = map(math.radians, (a, b, c, d))
    return math.degrees(math.acos(min(1, math.sin(b) * math.sin(d) + math.cos(b) * math.cos(d) * math.cos(a - c))))
obs = []   # (label, ra, dec, mjd0, mjd1, fov)
spec = {"xmmmaster": ("time", "end_time", None, 0.25, "XMM-Newton"), "chanmaster": ("time", None, "exposure", 0.25, "Chandra"),
        "swiftmastr": ("start_time", "stop_time", None, 0.2, "Swift"), "rosmaster": ("start_time", "end_time", None, 1.0, "ROSAT"),
        "suzamaster": ("time", "stop_time", None, 0.15, "Suzaku"), "exomaster": ("time", "end_time", None, 1.0, "EXOSAT"),
        "xrismmastr": ("time", "end_time", None, 0.3, "XRISM"), "ixmaster": ("time", "end_time", None, 0.1, "IXPE")}
for tab, (c0, c1, cd, fov, lab) in spec.items():
    try: t = P(f"xr/{tab}.xml").to_table()
    except Exception: continue
    for r in t:
        try:
            m0 = float(r[c0]); m1 = float(r[c1]) if c1 else m0 + float(r[cd]) / 86400
        except Exception: continue
        if m0 == m0 and m1 == m1: obs.append((lab + " " + str(r["name"]), float(r["ra"]), float(r["dec"]), m0, m1, fov))
for r in csv.DictReader(open("irsa/wise_merge_results.csv")):           # WISE/NEOWISE frames that contain the object
    m = float(r["mjd_obs"]); obs.append(("WISE " + r["Image_ID"], float(r["ra_obj"]), float(r["dec_obj"]), m - 6e-5, m + 6e-5, 0.39))
for h in json.load(open("sx/hits.json")):                              # SPHEREx images that contain the object
    m = h[0] - 2400000.5; obs.append(("SPHEREx " + h[1] + " " + h[2], h[5], h[6], m - 6.6e-4, m + 6.6e-4, 1.7))
print("pointings/frames loaded:", len(obs))
hits = []
for e in E:
    mjd = e["jd"] - 2400000.5; win = (e["sig3_km"] / max(e["v_kms"], 1) + 120) / 86400
    sig = e["sig3_arcsec"] / 3; lim = e["limit_arcsec"]
    p = norm.cdf((lim - e["ca_arcsec"]) / sig) - norm.cdf((-lim - e["ca_arcsec"]) / sig)
    for lab, ra, dec, m0, m1, fov in obs:
        if m1 < mjd - win or m0 > mjd + win: continue
        if sep(ra, dec, e["star_ra"], e["star_dec"]) < fov:
            hits.append(dict(utc=Time(e["jd"], format="jd").iso[:19], G=e["G"], star=e["star"], obs=lab, p_shadow_on_earth=round(float(p), 2),
                             ca_km=e["ca_km"], sig3_km=e["sig3_km"], window_s=round(win * 86400), dur_s=e["max_dur_s"]))
            print(hits[-1], flush=True)
json.dump(hits, open("past/geo_obs_matches.json", "w"), indent=1)
print("matches:", len(hits))
