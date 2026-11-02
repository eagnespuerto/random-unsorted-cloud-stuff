"""Write ADES (XML, version 2022) for the SPHEREx (code 288) positions of 2026 RY158.
usage: python scripts/write_ades.py "Submitter Name"   (from ry158-2026/)  -> data/2026RY158_sphrx_ades.xml"""
import json, sys
from xml.sax.saxutils import escape
from astropy.time import Time

NAME = sys.argv[1] if len(sys.argv) > 1 else "SUBMITTER NAME"
TRK = "RY158SX"                                   # tracklet id; MPC does not resolve the designation "2026 RY158"
A = sorted(json.load(open("data/sx_astrometry.json")), key=lambda a: a["mjd_utc_mid"])

def t(mjd): return Time(mjd, format="mjd", scale="utc").isot[:23] + "Z"
obs = []
for a in A:
    p = a["pos_km"]
    obs.append(f"""   <optical>
    <trkSub>{TRK}</trkSub>
    <mode>CCD</mode>
    <stn>288</stn>
    <sys>ICRF_KM</sys>
    <ctr>399</ctr>
    <pos1>{p[0]:.4f}</pos1>
    <pos2>{p[1]:.4f}</pos2>
    <pos3>{p[2]:.4f}</pos3>
    <obsTime>{t(a["mjd_utc_mid"])}</obsTime>
    <ra>{a["ra"]:.6f}</ra>
    <dec>{a["dec"]:.6f}</dec>
    <rmsRA>{a["rmsRA"]:.2f}</rmsRA>
    <rmsDec>{a["rmsDec"]:.2f}</rmsDec>
    <astCat>Gaia3</astCat>
    <remarks>SPHEREx QR3 L2 {a["oid"]} D1, template-subtracted</remarks>
   </optical>""")

xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ades version="2022">
 <obsBlock>
  <obsContext>
   <observatory>
    <mpcCode>288</mpcCode>
    <name>SPHEREx</name>
   </observatory>
   <submitter>
    <name>{escape(NAME)}</name>
   </submitter>
   <observers>
    <name>SPHEREx Science Team</name>
   </observers>
   <measurers>
    <name>{escape(NAME)}</name>
   </measurers>
   <telescope>
    <design>Reflector</design>
    <aperture>0.2</aperture>
    <detector>CCD</detector>
   </telescope>
   <comment>
    <line>Archival SPHEREx QR3 Level-2 images (NASA/IPAC IRSA), detector D1 (0.75-1.09 um).</line>
    <line>Positions from Gaussian fits on reference-subtracted images, tied per frame to Gaia DR3.</line>
    <line>Precoveries of the object JPL lists as 2026 RY158 (MPC designation lookup returns nothing).</line>
   </comment>
  </obsContext>
  <obsData>
{chr(10).join(obs)}
  </obsData>
 </obsBlock>
</ades>
"""
open("data/2026RY158_sphrx_ades.xml", "w").write(xml)
print(len(A), "observations ->", "data/2026RY158_sphrx_ades.xml")
