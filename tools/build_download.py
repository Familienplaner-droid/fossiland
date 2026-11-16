# Offline-Datei bauen: alle Grafiken eingebettet. Aufruf: python3 tools/build_download.py [Ziel.html]
import base64, os, re, json, io
from PIL import Image
import sys
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=R+'/src/game.html'; AS=R+'/src/assets/'; OUT=sys.argv[1] if len(sys.argv)>1 else R+'/Fossiland.html'
s=open(SRC).read()
mime={'webp':'image/webp','png':'image/png'}
emb={}
for fn in sorted(os.listdir(AS)):
    ext=fn.rsplit('.',1)[1]
    emb[fn]=f"data:{mime[ext]};base64,"+base64.b64encode(open(AS+fn,'rb').read()).decode()
# CSS url(assets/x) -> data uri
s=re.sub(r'url\(assets/([^)]+)\)',lambda m:f'url({emb[m.group(1)]})',s)
assert 'assets/' not in re.sub(r'const ASSET="assets/"','',s), [m.start() for m in re.finditer('assets/',s)][:5]
# app icon: skull sprite on rounded earth tile
ic=Image.open(AS+'icon.webp').convert('RGB').resize((180,180),Image.LANCZOS)
b=io.BytesIO();ic.save(b,'PNG');icon='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
head_end=s.index('</style>')+len('</style>')
head=s[:head_end]; body=s[head_end:]
doc=('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
 '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
 '<meta name="theme-color" content="#2a1c13">\n<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-capable" content="yes">\n'
 '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n<meta name="apple-mobile-web-app-title" content="Fossiland">\n'
 f'<link rel="icon" href="{icon}">\n<link rel="apple-touch-icon" href="{icon}">\n'
 '<style>html{-webkit-text-size-adjust:100%}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}</style>\n'
 + head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','') +
 '\n</head>\n<body>\n<script>window.EMB='+json.dumps(emb)+';</script>\n' + body + '\n</body>\n</html>\n')
open(OUT,'w').write(doc)
print(round(os.path.getsize(OUT)/1024/1024,2),'MB')
