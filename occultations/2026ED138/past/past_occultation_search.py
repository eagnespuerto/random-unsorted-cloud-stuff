"""Past stellar occultations by 2026 ED138, 1990-01-01 .. 2026-10-30, Gaia DR3 G<16.5.
Geocentric candidates: CA < (R_earth + R_body)/Delta + 3 sigma.
TESS candidates (2018-07-25 on): TESS-centric CA < R_body/Delta + 3 sigma (TESS orbit gives up to ~11" parallax).
Resumable (one JSON per 20-day segment), 6 Gaia queries in parallel, progress every 10%."""
import csv, glob, io, json, math, os, subprocess
from concurrent.futures import ThreadPoolExecutor
import numpy as np
def load(files):
    rows = []
    for f in files:
        for l in open(f).read().split("$$SOE")[1].split("$$EOE")[0].strip().splitlines():
            p = l.split(); rows.append([float(p[0]), float(p[1]), float(p[2]), float(p[3]), float(p[-2]), float(p[-1])])
    a = np.array(sorted({r[0]: r for r in rows}.values())); return a.T
G = load(sorted(glob.glob("past/geo_*.txt"))); T = load(["past/tess.txt"])
AU = 1.495978707e8; RE = 6378.0; RB = 450.0; SEG = 20.0
t0, t1 = G[0][0], G[0][-1]; segs = np.arange(t0, t1, SEG); N = len(segs)
os.makedirs("past/seg", exist_ok=True)

def gaia(q):
    for _ in range(4):
        txt = subprocess.run(["curl", "-sS", "-m", "300", "-G", "https://gea.esac.esa.int/tap-server/tap/sync",
                              "--data-urlencode", "REQUEST=doQuery", "--data-urlencode", "LANG=ADQL",
                              "--data-urlencode", "FORMAT=csv", "--data-urlencode", f"QUERY={q}"], capture_output=True, text=True).stdout
        if txt.startswith("source_id"): return list(csv.DictReader(io.StringIO(txt)))
    return None

def events(E, a, b, stars, lim_km, tag):
    m = (E[0] >= a - 0.05) & (E[0] <= b + 0.05)
    if m.sum() < 2: return []
    jd, ra, de, dl, s3a, s3d = (x[m] for x in E)
    tf = np.linspace(jd[0], jd[-1], int((jd[-1] - jd[0]) * 1440) + 1)               # 1-minute grid
    raf = np.interp(tf, jd, ra); def_ = np.interp(tf, jd, de)
    out = []
    for s in stars:
        yr = 2016.0 + (tf[len(tf) // 2] - 2457389.0) / 365.25
        sde = float(s["dec"]) + float(s["pmdec"] or 0) / 3.6e6 * (yr - 2016.0)
        sra = float(s["ra"]) + float(s["pmra"] or 0) / 3.6e6 * (yr - 2016.0) / math.cos(math.radians(sde))
        d = np.hypot((raf - sra) * math.cos(math.radians(sde)), def_ - sde) * 3600
        k = int(d.argmin()); ca = float(d[k]); D = float(np.interp(tf[k], jd, dl))
        lim = lim_km / (D * AU) * 206265; s3 = float(max(np.interp(tf[k], jd, s3a), np.interp(tf[k], jd, s3d)))
        if ca < lim + s3:
            k0, k1 = max(k - 60, 0), min(k + 60, len(tf) - 1)
            rate = math.hypot((raf[k1] - raf[k0]) * math.cos(math.radians(sde)), def_[k1] - def_[k0]) * 3600 / ((tf[k1] - tf[k0]) * 24)
            v = rate / 3600 * D * AU / 206265
            out.append(dict(frame=tag, jd=float(tf[k]), star=s["source_id"], G=float(s["phot_g_mean_mag"]), star_ra=sra, star_dec=sde,
                            ca_arcsec=round(ca, 4), ca_km=round(ca / 206265 * D * AU), limit_arcsec=round(lim, 4), sig3_arcsec=round(s3, 3),
                            sig3_km=round(s3 / 206265 * D * AU), delta_au=round(D, 3), v_kms=round(v, 2), max_dur_s=round(2 * RB / v, 1),
                            nominal_hit=bool(ca < lim)))
    return out

YEARS = {}
def year_stars(y):
    f = f"past/stars_{y}.json"
    if os.path.exists(f): return json.load(open(f))
    a = 2447892.5 + (y - 1990) * 365.25; m = (G[0] >= a - 21) & (G[0] <= a + 365.25 + 21)
    pad = 0.006 + float(max(G[4][m].max(), G[5][m].max())) / 3600
    q = (f"SELECT source_id,ra,dec,pmra,pmdec,phot_g_mean_mag FROM gaiadr3.gaia_source WHERE ra BETWEEN {G[1][m].min()-pad} AND {G[1][m].max()+pad} "
         f"AND dec BETWEEN {G[2][m].min()-pad} AND {G[2][m].max()+pad} AND phot_g_mean_mag<16.5")
    stars = gaia(q)
    if stars is None: print(f"year {y}: Gaia query failed", flush=True); return None
    json.dump(stars, open(f, "w")); return stars

def work(i):
    f = f"past/seg/{i}.json"
    if os.path.exists(f): return json.load(open(f))
    a = segs[i]; b = min(a + SEG, t1); m = (G[0] >= a) & (G[0] <= b)
    pad = 0.006 + float(max(G[4][m].max(), G[5][m].max())) / 3600
    y = 1990 + int((a - 2447892.5) // 365.25)
    ys = [YEARS.get(y)] + ([YEARS.get(y + 1)] if (b - 2447892.5) // 365.25 + 1990 > y else [])
    if any(s is None for s in ys): print(f"segment {i}: no star list", flush=True); return []
    r0, r1, d0, d1 = G[1][m].min() - pad, G[1][m].max() + pad, G[2][m].min() - pad, G[2][m].max() + pad
    stars = {s["source_id"]: s for L in ys for s in L if r0 <= float(s["ra"]) <= r1 and d0 <= float(s["dec"]) <= d1}.values()
    out = events(G, a, b, stars, RE + RB, "geocentric") + events(T, a, b, stars, RB, "TESS")
    json.dump(out, open(f, "w")); return out

yrs = list(range(1990, 2027)); done_y = 0; mark_y = 0
with ThreadPoolExecutor(6) as ex:
    for y, st in zip(yrs, ex.map(year_stars, yrs)):
        YEARS[y] = st; done_y += 1; p = done_y * 100 // len(yrs)
        if p >= mark_y + 10: mark_y = p // 10 * 10; print(f"star lists {mark_y}% ({done_y}/{len(yrs)} years)", flush=True)

done = 0; mark = 0; allout = []
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(work, range(N)):
        allout += r; done += 1; p = done * 100 // N
        if p >= mark + 10:
            mark = p // 10 * 10; print(f"past occultation search {mark}% ({done}/{N} segments, {len(allout)} candidates)", flush=True)
allout.sort(key=lambda e: e["jd"]); json.dump(allout, open("past/events.json", "w"), indent=1)
print("FINISHED", len(allout), "candidates", flush=True)
