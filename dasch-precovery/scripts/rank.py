import json,sys,collections
o=json.load(open(sys.argv[1]))
print("series:",collections.Counter(x[1] for x in o).most_common())
lim=sorted([x for x in o if x[7]],key=lambda x:-float(x[7]))
print("with limmag:",len(lim))
for x in lim[:12]: print(x[0],x[1]+x[2],"exp",x[4],"edge",x[5],"lim",x[7],"wcs",x[8],"V",x[9])
print("-- longest uncalibrated --")
for x in sorted([x for x in o if not x[7]],key=lambda x:-float(x[4] or 0))[:12]: print(x[0],x[1]+x[2],"exp",x[4],"edge",x[5],"wcs",x[8],"V",x[9])
