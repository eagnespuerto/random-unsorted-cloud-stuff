"""Stellar occultation search for 2026 ED138, 2026-10-30 .. 2028-12-31, Gaia DR3 stars G<18.5.
Resumable (one cached JSON per 5-day segment) and parallel (4 Gaia queries at once).
Geocentric closest approach (CA) from an hourly JPL ephemeris; star positions propagated with proper motion.
Keeps events whose geocentric CA < Earth radius + body radius + 3-sigma ephemeris uncertainty."""
import csv, io, json, math, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
L = open(sys.argv[1] if len(sys.argv) > 1 else "occ/eph.txt").read().split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
A = np.array([[float(x) for x in l.split()[:3]] + [float(l.split()[-4]), float(l.split()[-2]), float(l.split()[-1])] for l in L])
JD, RA, DE, DEL, S3RA, S3DE = A.T
AU = 1.495978707e8; RE = 6378.0; RBODY = 450.0           # body radius guess (H=2.85, albedo ~0.15)
SEG = 5 * 24                                                # hours per segment
os.makedirs("occ/seg", exist_ok=True)
segs = list(range(0, len(JD) - 1, SEG)); N = len(segs)

def gaia(q):
    for _ in range(3):
        txt = subprocess.run(["curl", "-sS", "-m", "300", "-G", "https://gea.esac.esa.int/tap-server/tap/sync",
                              "--data-urlencode", "REQUEST=doQuery", "--data-urlencode", "LANG=ADQL",
                              "--data-urlencode", "FORMAT=csv", "--data-urlencode", f"QUERY={q}"],
                             capture_output=True, text=True).stdout
        if txt.startswith("source_id"): return list(csv.DictReader(io.StringIO(txt)))
    return None

def work(si):
    f = f"occ/seg/{si}.json"
    if os.path.exists(f): return json.load(open(f))
    i0 = segs[si]; i1 = min(i0 + SEG + 1, len(JD))
    ra0, ra1 = RA[i0:i1].min() - 0.005, RA[i0:i1].max() + 0.005
    de0, de1 = DE[i0:i1].min() - 0.005, DE[i0:i1].max() + 0.005
    stars = gaia(f"SELECT source_id,ra,dec,pmra,pmdec,phot_g_mean_mag FROM gaiadr3.gaia_source WHERE ra BETWEEN {ra0} AND {ra1} "
                 f"AND dec BETWEEN {de0} AND {de1} AND phot_g_mean_mag<18.5")
    if stars is None: print(f"segment {si}: Gaia query failed", flush=True); return []
    jd = JD[i0:i1]; tf = np.linspace(jd[0], jd[-1], (len(jd) - 1) * 60 + 1)       # 1-minute grid
    raf = np.interp(tf, jd, RA[i0:i1]); def_ = np.interp(tf, jd, DE[i0:i1])
    yr = 2016.0 + (tf[len(tf) // 2] - 2457389.0) / 365.25
    out = []
    for s in stars:
        sde = float(s["dec"]) + float(s["pmdec"] or 0) / 3.6e6 * (yr - 2016.0)
        sra = float(s["ra"]) + float(s["pmra"] or 0) / 3.6e6 * (yr - 2016.0) / math.cos(math.radians(sde))
        d = np.hypot((raf - sra) * math.cos(math.radians(sde)), def_ - sde) * 3600
        k = int(d.argmin()); ca = float(d[k])
        dl = float(np.interp(tf[k], JD, DEL)); lim = (RE + RBODY) / (dl * AU) * 206265
        s3 = float(max(np.interp(tf[k], JD, S3RA), np.interp(tf[k], JD, S3DE)))
        if ca < lim + s3:
            k0, k1 = max(k - 60, 0), min(k + 60, len(tf) - 1)
            rate = math.hypot((raf[k1] - raf[k0]) * math.cos(math.radians(sde)), def_[k1] - def_[k0]) * 3600 / ((tf[k1] - tf[k0]) * 24)
            v = rate / 3600 * dl * AU / 206265
            out.append(dict(jd=float(tf[k]), star=s["source_id"], G=float(s["phot_g_mean_mag"]), star_ra=sra, star_dec=sde,
                            ca_arcsec=round(ca, 4), ca_km=round(ca / 206265 * dl * AU), earth_limit_arcsec=round(lim, 4),
                            sig3_arcsec=round(s3, 3), delta_au=round(dl, 3), v_kms=round(v, 2),
                            max_dur_s=round(2 * RBODY / v, 1), on_earth_nominal=bool(ca < lim)))
    json.dump(out, open(f, "w"))
    return out

done = 0; mark = 0; allout = []
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(work, range(N)):
        allout += r; done += 1; p = done * 100 // N
        if p >= mark + 10:
            mark = p // 10 * 10; print(f"occultation search {mark}% ({done}/{N} segments, {len(allout)} candidates)", flush=True)
allout.sort(key=lambda e: e["jd"])
json.dump(allout, open("occ/events.json", "w"), indent=1)
print("FINISHED", len(allout), "candidates", flush=True)
