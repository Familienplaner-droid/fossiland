import json,re
d=json.load(open("/tmp/xd/data.json"));OV={"xvolc":1.0}
p="/home/claude/fossiland/src/game.html";s=open(p).read()
s=re.sub(r'const XDPOS=\{[^;]*\};','const XDPOS='+json.dumps(d["pos"],separators=(",",":"))+';',s,1)
s=re.sub(r'const XDSHEET=\[[^\]]*\];','const XDSHEET='+json.dumps(d["sheet"])+';',s,1)
s=re.sub(r'const XDMETA=\{[^;]*\};\n','',s)
s=s.replace('const XDSHEET=','const XDMETA='+json.dumps(d["meta"],separators=(",",":"))+';\nconst XDSHEET=',1)
for id,k in d["k"].items():
  k=OV.get(id,k);s=re.sub(r'\["%s",(\[[0-9,]+\]),[0-9.]+'%id,lambda m:'["%s",%s,%s'%(id,m.group(1),k),s,1)
open(p,"w").write(s)
