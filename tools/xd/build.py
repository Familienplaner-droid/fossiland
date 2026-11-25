# baut xd_sheet.webp aus /tmp/xd/<id>.png und gibt JS-Daten aus
import os,json,numpy as np
from PIL import Image
from scipy import ndimage
ORDER="xmeg xgeode xmeteor xtrophy xstatue xtric xcave xcore xvolc xmicro xclock xhour xfire xterra xtusk xtrex xcab xfount xmosaic xcar chest chesto".split()
FOOT={"xtusk":2,"xtrex":2,"xcab":2,"xfount":2,"xmosaic":2,"xcar":2.5}
items=[]
for id in ORDER:
  p=f"/tmp/xd/{id}.png"
  if not os.path.exists(p):continue
  im=Image.open(p).convert("RGBA");a=np.array(im)[...,3]>128
  lab,n=ndimage.label(a);sz=ndimage.sum(a,lab,range(n+1));big=np.isin(lab,[i for i in range(1,n+1) if sz[i]>sz.max()*.002])
  ys,xs=np.where(big);im=im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
  sc=min(1,(240 if id.startswith("chest") else 420)/max(im.size));im=im.resize((round(im.width*sc),round(im.height*sc)),Image.LANCZOS)
  A=np.array(im)[...,3]>128;h,w=A.shape
  rows=[y for y in range(h) if A[y].any()];yb=rows[-1]
  band=A[int(h*.9):];xs=np.where(band.any(0))[0];bw=xs.max()-xs.min()+1
  ax=int(np.where(A[yb])[0].mean())
  k=1 if id in FOOT or id.startswith("chest") else round(min(1.6,max(.5,.82*w/bw)),2)
  items.append((id,im,[w,h,ax,yb],k))
# packen: Reihen bis 2048 breit
X=Y=rh=0;pos={};W=2048
for id,im,m,k in items:
  if X+im.width>W:X=0;Y+=rh+2;rh=0
  pos[id]=[X,Y,im.width,im.height];X+=im.width+2;rh=max(rh,im.height)
H=Y+rh;sheet=Image.new("RGBA",(W,H))
for id,im,m,k in items:sheet.paste(im,tuple(pos[id][:2]))
sheet.save("/home/claude/fossiland/src/assets/xd_sheet.webp",quality=86,method=6)
print("size",W,H,os.path.getsize("/home/claude/fossiland/src/assets/xd_sheet.webp")//1024,"KB")
json.dump({"pos":pos,"sheet":[W,H],"meta":{id:m for id,_,m,_ in items},"k":{id:k for id,_,_,k in items}},open("/tmp/xd/data.json","w"))
print(json.dumps({id:k for id,_,_,k in items}))
