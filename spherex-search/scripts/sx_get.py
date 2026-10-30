"""Download SPHEREx L2 cutouts around each survey pass's 2026 ED138 track region.
Keeps IMAGE, VARIANCE, FLAGS, celestial WCS header, MJD-AVG and wavelength map per cutout."""
import csv, io, json, os, subprocess, sys, tempfile, warnings
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
warnings.simplefilter("ignore")

REG = {"2025": (271.045, -42.860, 0.40), "2026a": (274.982, -42.586, 0.18), "2026b": (272.456, -42.673, 0.20)}
OUT = "sx/cut"; os.makedirs(OUT, exist_ok=True)

def curl(url, out=None):
    cmd = ["curl", "-sS", "-f", "-m", "300", url] + (["-o", out] if out else [])
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout

# 1. image list per region via SIA (gives direct IBE URLs)
jobs = {}
for name, (ra, dec, size) in REG.items():
    for coll in ("spherex_qr3", "spherex_qr2"):
        txt = curl(f"https://irsa.ipac.caltech.edu/SIA?COLLECTION={coll}&POS=CIRCLE+{ra}+{dec}+0.001&RESPONSEFORMAT=CSV&MAXREC=100000")
        for r in csv.DictReader(io.StringIO(txt)):
            key = (name, r["obs_id"], r["energy_bandpassname"])
            if key not in jobs:  # qr3 queried first, so it wins
                jobs[key] = (r["access_url"], ra, dec, size, coll)
jobs = sorted(jobs.items())
N = len(jobs); print(f"start, {N} cutouts", flush=True)

done = [0]; mark = [0]
def get(item):
    (name, oid, band), (url, ra, dec, size, coll) = item
    f = f"{OUT}/{name}_{oid}_{band[-2:]}.npz"
    if not os.path.exists(f):
        for k in range(3):
            try:
                with tempfile.NamedTemporaryFile(suffix=".fits", dir="sx") as t:
                    curl(f"{url}?center={ra},{dec}&size={size}&gzip=false", t.name)
                    h = fits.open(t.name)
                    H = h["IMAGE"].header
                    Hw = H.copy()
                    for kk in [k for k in Hw if k[:2] in ("A_", "B_", "AP", "BP")]: del Hw[kk]
                    ny, nx = h["IMAGE"].data.shape
                    yy, xx = np.mgrid[:ny, :nx]
                    lam = WCS(Hw, fobj=h, key="W").pixel_to_world_values(xx, yy)[0].astype("f4")
                    np.savez_compressed(f, img=h["IMAGE"].data.astype("f4"), var=h["VARIANCE"].data.astype("f4"),
                        flg=h["FLAGS"].data, lam=lam, hdr=WCS(H).to_header(relax=True).tostring(),
                        mjd=H["MJD-AVG"], coll=coll, band=band)
                break
            except Exception as e:
                print(name, oid, band, e, file=sys.stderr, flush=True)
        else:
            print(f"FAIL {name} {oid} {band}", flush=True); return
    done[0] += 1; p = done[0] * 100 // N
    if p >= mark[0] + 10:
        mark[0] = p // 10 * 10; print(f"{mark[0]}% ({done[0]}/{N})", flush=True)

with ThreadPoolExecutor(6) as ex: list(ex.map(get, jobs))
print("FINISHED", flush=True)
