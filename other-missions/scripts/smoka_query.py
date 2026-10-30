import json,subprocess,sys
F=[(k,v) for k,v in json.load(open('sub/defaults.json')) if k not in ('instruments','RadOrRec','longitudeF','longitudeT','latitudeF','latitudeT','asciitable','diff')]
F+=[('instruments',i) for i in "SUP FCS HDS OHS IRC CIA COM CAC MIR MCS HIC FMS HSC CRS IRD SWS MMZ VMP SCX PFS".split()]
F+=[('RadOrRec','rectangle'),('longitudeF',sys.argv[1]),('longitudeT',sys.argv[2]),('latitudeF',sys.argv[3]),('latitudeT',sys.argv[4]),('asciitable','Ascii'),('diff','100000'),('action','Search')]
cmd=["curl","-sS","-m","300","-X","POST","https://smoka.nao.ac.jp/fssearch","-o",sys.argv[5],"-w","%{http_code} %{size_download}\n"]
for k,v in F: cmd+=["--data-urlencode",f"{k}={v}"]
print(subprocess.run(cmd,capture_output=True,text=True).stdout)
