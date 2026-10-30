"""Per-exposure check of the 22 Subaru exposures (SMOKA) whose field may contain 2026 EE138:
object offset from the pointing centre at the exact UT start, JPL 3-sigma position uncertainty,
and a rough expected S/N from typical single-exposure depths.
usage: python subaru_exposures.py  -> data/subaru_exposures.json"""
import json, math, subprocess, urllib.parse
EXP = [  # frame, date, UT, filter, exptime, pointing RA, Dec (from SMOKA)
 ("SUPA00312180","2004-06-17","07:03:55","W-J-VR",60,"10:31:17.98","+09:27:00.1"),
 ("SUPA00312220","2004-06-17","07:11:58","W-J-VR",60,"10:31:17.98","+09:27:00.1"),
 ("SUPA00312260","2004-06-17","07:20:00","W-J-VR",60,"10:31:17.98","+09:27:00.1"),
 ("HSCA06338000","2016-03-17","06:04:03","HSC-r",30,"10:51:09.22","+06:30:00.0"),
 ("HSCA06344000","2016-03-17","06:36:17","HSC-r",30,"10:51:09.22","+06:30:00.0"),
 ("HSCA06362000","2016-03-17","08:12:28","HSC-r",30,"10:51:09.22","+06:30:00.0"),
 ("HSCA06368000","2016-03-17","08:44:48","HSC-r",30,"10:51:09.22","+06:30:00.0"),
 ("HSCA06398000","2016-03-17","11:33:30","HSC-r",30,"10:51:09.22","+06:30:00.0"),
 ("HSCA06404000","2016-03-17","12:05:49","HSC-r",30,"10:51:09.22","+06:30:00.0"),
 ("HSCA20311200","2020-01-19","11:44:37","HSC-z",200,"10:59:27.40","+04:35:51.0"),
 ("HSCA20395800","2020-01-21","10:27:28","HSC-Y",200,"10:59:27.41","+04:35:51.0"),
 ("HSCA20405200","2020-01-21","13:39:38","HSC-i2",200,"10:59:27.40","+04:35:51.0"),
 ("HSCA20429800","2020-01-22","10:28:40","HSC-i2",200,"10:56:56.11","+04:55:03.1"),
 ("HSCA20430000","2020-01-22","10:32:41","HSC-i2",200,"11:02:07.87","+04:55:03.0"),
 ("HSCA20432400","2020-01-22","11:20:48","HSC-i2",200,"11:00:07.87","+04:25:08.0"),
 ("HSCA20614400","2020-01-28","09:50:20","HSC-Y",200,"10:56:56.11","+04:55:03.1"),
 ("HSCA20614600","2020-01-28","09:54:15","HSC-Y",200,"11:02:07.87","+04:55:03.0"),
 ("HSCA20718000","2020-01-30","11:22:55","HSC-z",200,"11:00:07.86","+04:25:08.1"),
 ("HSCA20742800","2020-02-19","07:37:02","HSC-z",200,"10:56:56.10","+04:55:03.1"),
 ("HSCA20858000","2020-02-22","07:54:16","HSC-g",150,"10:58:24.29","+04:51:35.1"),
 ("HSCA20861800","2020-02-22","08:50:13","HSC-g",150,"10:58:24.29","+04:51:35.1"),
 ("HSCA20972000","2020-02-25","08:05:40","HSC-r2",150,"10:58:24.29","+04:51:35.1"),
]
# object mags from DECam/Rubin colours: V~22.7-23.1 (Horizons), g-r=0.58, r-i=0.26; z, Y ~ i-0.2
# 5-sigma single-exposure depths (typical, dark): HSC-SSP Wide g 150s 25.5, r 150s 25.4, i 200s 25.2,
# z 200s 24.5, Y 200s 23.6; HSC r 30s 24.3; Suprime-Cam VR 60s 24.6
DEPTH = {"HSC-g": 25.5, "HSC-r2": 25.4, "HSC-i2": 25.2, "HSC-z": 24.5, "HSC-Y": 23.6, "HSC-r": 24.3, "W-J-VR": 24.6}
def hms(s, f=15): sg = -1 if s[0] == '-' else 1; p = [float(x) for x in s.lstrip('+-').split(':')]; return sg * f * (p[0] + p[1]/60 + p[2]/3600)
def horizons(t):
    q = dict(format='text', COMMAND="'DES=2026 EE138;'", MAKE_EPHEM='YES', EPHEM_TYPE='OBSERVER', CENTER="'568@399'",
             TLIST=f"'{t}'", QUANTITIES="'1,9,36'", ANG_FORMAT='DEG', CSV_FORMAT='YES', EXTRA_PREC='YES')
    txt = subprocess.run(["curl", "-s", "https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(q)], capture_output=True, text=True).stdout
    p = [x.strip() for x in txt.split('$$SOE')[1].split('$$EOE')[0].strip().split(',')]
    nums = [x for x in p[1:] if x.replace('.', '', 1).replace('-', '', 1).replace('+', '', 1).isdigit()]
    return float(nums[0]), float(nums[1]), float(nums[2]), float(nums[-2]), float(nums[-1])  # RA, Dec, V, 3sig smaa ("), smia (")
out = []
for fr, d, ut, filt, et, pra, pde in EXP:
    from astropy.time import Time
    jd = Time(f"{d}T{ut}").jd + et / 2 / 86400
    ra, de, V, s1, s2 = horizons(jd)
    P, D = hms(pra), hms(pde, 1)
    dx = (ra - P) * math.cos(math.radians(de)); dy = de - D; r = math.hypot(dx, dy)
    g = V + 0.35; rr = g - 0.58; i = rr - 0.26; m = {"HSC-g": g, "HSC-r2": rr, "HSC-r": rr, "HSC-i2": i, "HSC-z": i - 0.2, "HSC-Y": i - 0.25, "W-J-VR": V - 0.2}[filt]
    snr = 5 * 10 ** (0.4 * (DEPTH[filt] - m))
    out.append(dict(frame=fr, date=d, ut=ut, filter=filt, exptime=et, obj_ra=round(ra, 5), obj_dec=round(de, 5), V=V,
                    offset_east_deg=round(dx, 3), offset_north_deg=round(dy, 3), r_deg=round(r, 3),
                    unc3sig_arcsec=round(max(s1, s2), 1), mag_est=round(m, 2), snr_est=round(snr)))
    print(f"{fr} {d} {ut} {filt:7s} {et:4d}s  r={r:.3f} deg  3sig={max(s1, s2):6.1f}\"  mag~{m:.2f}  S/N~{snr:.0f}")
json.dump(out, open('data/subaru_exposures.json', 'w'), indent=1)
