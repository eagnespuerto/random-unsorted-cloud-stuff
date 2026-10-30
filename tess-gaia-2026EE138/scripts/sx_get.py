"""Download SPHEREx L2 cutouts (IMAGE, VARIANCE, WCS, MJD, wavelength map) for every frame that
contains one of the 2026 EE138 track regions (one region per SPHEREx pass).
usage: python sx_get.py <obscore.csv> <outdir>"""
import csv, os, re, subprocess, sys, tempfile, warnings
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from matplotlib.path import Path
warnings.simplefilter("ignore")

REG = {"A": (165.905, 4.142), "B": (167.532, 3.409), "C": (166.283, 3.879)}   # Apr-Jun 2025, Dec 2025, May 2026
SIZE = 0.14
src, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)

def curl(url, out=None):
    cmd = ["curl", "-sS", "-f", "-m", "300", url] + (["-o", out] if out else [])
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout

jobs = []
for r in csv.DictReader(open(src)):
    poly = Path(np.array(list(map(float, r["s_region"].split()[2:]))).reshape(-1, 2))
    for name, (ra, dec) in REG.items():
        if poly.contains_point((ra, dec)): jobs.append((name, r["obs_id"], r["energy_bandpassname"], r["access_url"], ra, dec))
print(f"{len(jobs)} cutouts", flush=True)

def get(j):
    name, oid, band, link, ra, dec = j
    f = f"{OUT}/{name}_{oid}_{band[-2:]}.npz"
    if os.path.exists(f): return
    for _ in range(3):
        try:
            url = [u for u in re.findall(r"https://[^<\"]+\.fits", curl(link)) if "/level2/" in u][0]
            with tempfile.NamedTemporaryFile(suffix=".fits", dir=OUT) as t:
                curl(f"{url}?center={ra},{dec}&size={SIZE}&gzip=false", t.name)
                h = fits.open(t.name); H = h["IMAGE"].header; Hw = H.copy()
                for k in [k for k in Hw if k[:2] in ("A_", "B_", "AP", "BP")]: del Hw[k]
                ny, nx = h["IMAGE"].data.shape; yy, xx = np.mgrid[:ny, :nx]
                lam = WCS(Hw, fobj=h, key="W").pixel_to_world_values(xx, yy)[0].astype("f4")
                np.savez_compressed(f, img=h["IMAGE"].data.astype("f4"), var=h["VARIANCE"].data.astype("f4"),
                    flg=h["FLAGS"].data, lam=lam, hdr=WCS(H).to_header(relax=True).tostring(), mjd=H["MJD-AVG"], band=band)
            return
        except Exception as e: err = e
    print("FAIL", name, oid, band, err, flush=True)

with ThreadPoolExecutor(16) as ex: list(ex.map(get, jobs))
print("FINISHED", flush=True)
