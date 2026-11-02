"""Download SPHEREx L2 cutouts for 2026 RY158: the archsearch science frames (object predicted on them) plus,
for each, same-band frames of the same sky taken >= 2 days away (object long gone) to use as templates.
usage: python scripts/sx_get.py   (run from ry158-2026/)  -> sx/cut/*.npz, sx/jobs.json"""
import csv, io, json, os, subprocess, sys, tempfile, warnings, bisect
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
warnings.simplefilter("ignore")

SIZE = 0.12                                   # cutout side (deg)
OUT = "sx/cut"; os.makedirs(OUT, exist_ok=True)
L = open("data/eph_sx.txt").read().split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
E = [tuple(map(float, l.split()[:3])) for l in L]; J = [e[0] for e in E]
def eph(mjd):
    jd = mjd + 2400000.5; i = bisect.bisect(J, jd) - 1; a, b = E[i], E[i + 1]; f = (jd - a[0]) / (b[0] - a[0])
    return a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f

def curl(url, out=None):
    cmd = ["curl", "-sS", "-f", "-m", "300", "--retry", "5", "--retry-all-errors", url] + (["-o", out] if out else [])
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout

sci = {(r["obs_id"], r["access_url"][-2:]): float(r["t_min"]) for r in csv.DictReader(open("data/archsearch_2026.csv"))
       if r["facility_name"] == "SPHEREx"}
jobs = {}                                     # (obs_id, band) -> (url, ra, dec, role, sci_key)
for (oid, band), mjd in sorted(sci.items()):
    ra, dec = eph(mjd)
    txt = curl(f"https://irsa.ipac.caltech.edu/SIA?COLLECTION=spherex_qr3&POS=CIRCLE+{ra}+{dec}+0.001&RESPONSEFORMAT=CSV&MAXREC=100000")
    rows = [r for r in csv.DictReader(io.StringIO(txt)) if r["energy_bandpassname"].endswith(band)]
    me = [r for r in rows if r["obs_id"] == oid]
    if not me: print("science frame not in SIA:", oid, band, file=sys.stderr); continue
    jobs[(oid, band, oid)] = (me[0]["access_url"], ra, dec, "sci")
    ref = sorted((r for r in rows if abs(float(r["t_min"]) - mjd) >= 2), key=lambda r: abs(float(r["t_min"]) - mjd))[:10]
    for r in ref: jobs[(r["obs_id"], band, oid)] = (r["access_url"], ra, dec, "ref")
    print(oid, band, "refs:", len(ref), flush=True)
json.dump([[*k, *v] for k, v in jobs.items()], open("sx/jobs.json", "w"))

def get(item):
    (oid, band, skey), (url, ra, dec, role) = item
    f = f"{OUT}/{skey}_{band}_{role}_{oid}.npz"
    if os.path.exists(f): return
    for k in range(3):
        try:
            with tempfile.NamedTemporaryFile(suffix=".fits", dir="sx") as t:
                curl(f"{url}?center={ra},{dec}&size={SIZE}&gzip=false", t.name)
                h = fits.open(t.name); H = h["IMAGE"].header
                np.savez_compressed(f, img=h["IMAGE"].data.astype("f4"), flg=h["FLAGS"].data,
                                    hdr=WCS(H).to_header(relax=True).tostring(), mjd=H["MJD-AVG"], band=band)
            return
        except Exception as e:
            print(oid, band, e, file=sys.stderr, flush=True)
    print("FAIL", oid, band, flush=True)

print(len(jobs), "cutouts", flush=True)
with ThreadPoolExecutor(6) as ex: list(ex.map(get, jobs.items()))
print("FINISHED", flush=True)
