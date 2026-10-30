"""Query SMOKA (all Subaru instruments) in 1x1 deg tiles along the 1999-2026 track of 2026 EE138.
SMOKA caps a search at 20,000 rows, so any tile that hits the cap is split into quarters.
usage: python smoka_tiles.py <ephemeris> <form defaults json> <outdir>"""
import json, os, re, subprocess, sys, numpy as np
eph, dfl, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
L = open(eph).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
RA = np.array([float(l.split(',')[3]) for l in L]); DE = np.array([float(l.split(',')[4]) for l in L])
F = [(k, v) for k, v in json.load(open(dfl)) if k not in ('instruments', 'RadOrRec', 'longitudeF', 'longitudeT', 'latitudeF', 'latitudeT', 'asciitable', 'diff')]
F += [('instruments', i) for i in "SUP FCS HDS OHS IRC CIA COM CAC MIR MCS HIC FMS HSC CRS IRD SWS MMZ VMP SCX PFS".split()]

def query(r0, r1, d0, d1):
    f = f"{out}/t_{r0:.2f}_{d0:.2f}_{r1-r0:.2f}.txt"
    if not os.path.exists(f):
        cmd = ["curl", "-sS", "-m", "600", "-X", "POST", "https://smoka.nao.ac.jp/fssearch", "-o", f]
        for k, v in F + [('RadOrRec', 'rectangle'), ('longitudeF', r0), ('longitudeT', r1), ('latitudeF', d0), ('latitudeT', d1),
                         ('asciitable', 'Ascii'), ('diff', '100000'), ('action', 'Search')]:
            cmd += ["--data-urlencode", f"{k}={v}"]
        subprocess.run(cmd, check=True)
    n = sum(1 for l in open(f, errors='ignore') if re.match(r'[A-Z]{4}\d{8}', l))
    if n >= 20000:
        os.remove(f); h = (r1 - r0) / 2
        return sum(query(r, r + h, d, d + h) for r in (r0, r0 + h) for d in (d0, d0 + h))
    return n

tiles = sorted({(np.floor(r - dr), np.floor(d - dd)) for r, d in zip(RA[::30], DE[::30]) for dr in (-0.8, 0, 0.8) for dd in (-0.8, 0, 0.8)})
tot = 0
for r0, d0 in tiles:
    n = query(r0, r0 + 1, d0, d0 + 1); tot += n; print(f"tile RA {r0:.0f} Dec {d0:+.0f}: {n}", flush=True)
print("TOTAL", tot, "frames in", len(tiles), "tiles")
