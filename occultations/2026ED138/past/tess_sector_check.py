import json, subprocess, csv, io, math, functools
from astropy.time import Time
from scipy.stats import norm
E = [e for e in json.load(open("past/events.json")) if e["frame"] == "TESS"]
def curl(url, params=None):
    cmd = ["curl", "-sS", "-m", "300", "-G", url] + sum([["--data-urlencode", f"{k}={v}"] for k, v in (params or {}).items()], [])
    return subprocess.run(cmd, capture_output=True, text=True).stdout
@functools.lru_cache(None)
def sector_dates(sec):
    txt = curl("https://mast.stsci.edu/vo-tap/api/v0.1/caom/sync", {"LANG": "ADQL", "FORMAT": "csv",
          "QUERY": f"SELECT TOP 20 t_min,t_max FROM ivoa.obscore WHERE obs_collection='TESS' AND obs_id LIKE 'tess%-s{sec:04d}-0%-s'"})
    r = list(csv.DictReader(io.StringIO(txt)))
    return (min(float(x["t_min"]) for x in r), max(float(x["t_max"]) for x in r)) if r else None
out = []
for e in E:
    j = json.loads(curl(f"https://mast.stsci.edu/tesscut/api/v0.1/sector?ra={e['star_ra']}&dec={e['star_dec']}&radius=0"))
    mjd = e["jd"] - 2400000.5; inside = None
    for s in j.get("results", []):
        d = sector_dates(int(s["sector"]))
        if d and d[0] <= mjd <= d[1]: inside = (int(s["sector"]), s["camera"], s["ccd"])
    sig = e["sig3_arcsec"] / 3; lim = e["limit_arcsec"]
    p = norm.cdf((lim - e["ca_arcsec"]) / sig) - norm.cdf((-lim - e["ca_arcsec"]) / sig)    # chance the shadow covered TESS
    out.append(dict(e, tess_sector=inside, p_hit=round(float(p), 3), utc=Time(e["jd"], format="jd").iso[:19]))
    print(out[-1]["utc"], "G %.2f" % e["G"], "sector", inside, "P(hit) %.2f" % p, flush=True)
json.dump(out, open("past/tess_events.json", "w"), indent=1)
