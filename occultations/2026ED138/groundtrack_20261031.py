import json, math, numpy as np, warnings; warnings.simplefilter("ignore")
from astropy.time import Time; import astropy.units as u
from astropy.coordinates import EarthLocation, AltAz, SkyCoord, get_sun
L = open(__import__("sys").argv[1] if len(__import__("sys").argv) > 1 else "occ/eph.txt").read().split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
A = np.array([[float(x) for x in l.split()[:3]] + [float(l.split()[-4]), float(l.split()[-2]), float(l.split()[-1])] for l in L[:72]])
JD, RA, DE, DEL, S3A, S3D = A.T
sra, sde = 272.81653, -42.22194            # Gaia DR3 6724366794838332544 at epoch (from search)
AU = 1.495978707e8; RE = 6371.0
a, d = math.radians(sra), math.radians(sde)
e = np.array([-math.sin(a), math.cos(a), 0]); n = np.array([-math.sin(d)*math.cos(a), -math.sin(d)*math.sin(a), math.cos(d)])
s = np.array([math.cos(d)*math.cos(a), math.cos(d)*math.sin(a), math.sin(d)])
t = np.arange(-600, 601, 10) / 86400 + 2461344.5 + (1 + 23/60) / 24          # 01:13-01:33 UTC
ra = np.interp(t, JD, RA); de = np.interp(t, JD, DE); dl = np.interp(t, JD, DEL)
xi = (ra - sra) * math.cos(d) * math.pi / 180 * dl * AU; eta = (de - sde) * math.pi / 180 * dl * AU
k = np.argmin(np.hypot(xi, eta)); print("geocentric CA %.0f km at %s UTC; shadow speed %.1f km/s" % (np.hypot(xi, eta)[k], Time(t[k], format="jd").iso[11:19],
      np.hypot(np.diff(xi), np.diff(eta))[k] / 10))
print("3-sigma cross-track uncertainty ~ %.0f km" % (max(S3A[0], S3D[0]) / 206265 * dl[k] * AU))
def ground(x, y, tt):
    z2 = RE**2 - x*x - y*y
    if z2 <= 0: return None
    p = x * e + y * n + math.sqrt(z2) * s                         # inertial (ICRS-ish) vector, star above horizon
    gmst = Time(tt, format="jd").sidereal_time("mean", "greenwich").rad
    lon = (math.degrees(math.atan2(p[1], p[0]) - gmst) + 540) % 360 - 180; lat = math.degrees(math.asin(p[2] / RE))
    return lat, lon
# body radius from preprint diameter 612-968 km -> use 400 km
R = 400.0
nx, ny = -np.diff(eta)[k], np.diff(xi)[k]; nn = math.hypot(nx, ny); nx, ny = nx / nn, ny / nn   # unit normal to motion
track = {}
for lab, off in (("centre", 0), ("north/edge+", R), ("south/edge-", -R)):
    pts = []
    for i in range(len(t)):
        g = ground(xi[i] + off * nx, eta[i] + off * ny, t[i])     # observer projection on fundamental plane = object offset
        if g: pts.append((Time(t[i], format="jd").iso[11:19], round(g[0], 2), round(g[1], 2)))
    track[lab] = pts
for p in track["centre"][::6]: print("centre", p)
json.dump(track, open("groundtrack_20261031.json", "w"), indent=1)
OBS = {"Rubin/Gemini-S (Cerro Pachón)": (-30.24, -70.74), "CTIO": (-30.17, -70.81), "La Silla": (-29.26, -70.73), "Las Campanas": (-29.01, -70.69),
       "Paranal": (-24.63, -70.40), "El Leoncito (CASLEO)": (-31.80, -69.30), "Bosque Alegre": (-31.60, -64.55), "OPD/LNA Brazil": (-22.53, -45.58),
       "SAAO Sutherland": (-32.38, 20.81), "Siding Spring": (-31.27, 149.06), "Mt John NZ": (-43.99, 170.46), "OAN San Pedro Mártir": (31.04, -115.46),
       "Kitt Peak/NOIRLab": (31.96, -111.60), "OSN/Calar Alto Spain": (37.2, -2.55), "Teide/La Palma": (28.3, -16.5), "Pic du Midi": (42.94, 0.14)}
tc = Time(t[k], format="jd"); star = SkyCoord(sra * u.deg, sde * u.deg)
print("\nObservatory checks at %s UTC (star altitude / Sun altitude / distance from shadow centre-line):" % tc.iso[11:19])
cen = np.array([[p[1], p[2]] for p in track["centre"]])
for nm, (la, lo) in OBS.items():
    loc = EarthLocation(lat=la * u.deg, lon=lo * u.deg); fr = AltAz(obstime=tc, location=loc)
    alt = star.transform_to(fr).alt.deg; sun = get_sun(tc).transform_to(fr).alt.deg
    if len(cen):
        dist = min(math.degrees(math.acos(min(1, math.sin(math.radians(la))*math.sin(math.radians(c[0])) + math.cos(math.radians(la))*math.cos(math.radians(c[0]))*math.cos(math.radians(lo - c[1]))))) for c in cen) * 111.2
    else: dist = float("nan")
    print(f"  {nm:30s} star {alt:5.1f}°  Sun {sun:6.1f}°  {dist:6.0f} km from centre-line")
