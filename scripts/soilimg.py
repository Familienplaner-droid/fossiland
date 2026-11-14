"""Bodentextur-Atlas aus KI-Bildern: Kanten nahtlos machen, tiefere Schichten in den Farben des Zeitalters ableiten."""
import numpy as np, sys
from PIL import Image
A='/mnt/user-data/attachments/3c81d767-102f-5b19-b6b9-5bdb74ffc20c/'
SRC={5:'8e3cc9b1',4:'120cec92',3:'561853bf',2:'4bf8f4ff',1:'54622593',0:'a37eda18'}
SOILS=[
 [["#dd8f6c","#c2714f","#9a5538"],["#9a4e3e","#7d3d30","#5a2a21"],["#857b72","#686059","#4c4540"]],
 [["#e6bc7c","#cf9f5f","#a97a43"],["#b06e45","#93573a","#6e3f29"],["#857b72","#686059","#4c4540"]],
 [["#e6bc7c","#cf9f5f","#a97a43"],["#a07a52","#86633f","#634830"],["#d3caa9","#b8ae8d","#918769"]],
 [["#d9b680","#c09a63","#9b7746"],["#ece7da","#d3cdbc","#aaa391"],["#7d746c","#615a54","#46413d"]],
 [["#9a7a54","#80633f","#5e472c"],["#6e5a44","#574634","#3d3024"],["#4f4b45","#3b3934","#2a2825"]],
 [["#e3f1f7","#c2dce8","#98bfd1"],["#dcbc8c","#c3a170","#9c7e52"],["#8e8a84","#716d68","#55524e"]]]
N=512
hx=lambda h:np.array([int(h[i:i+2],16) for i in (1,3,5)],np.float32)
def seamless(a):
    n=a.shape[0];b=np.roll(np.roll(a,n//2,0),n//2,1)
    i=np.arange(n);d=np.minimum(i,n-1-i)/(n*.22);d=np.clip(d,0,1);d=d*d*(3-2*d)
    w=np.minimum(d[:,None],d[None,:])[...,None]
    return a*w+b*(1-w)
def lum(a):return a@np.array([.299,.587,.114],np.float32)
for era,f in SRC.items():
    img=np.asarray(Image.open(A+f+'-image.png').convert('RGB').resize((1024,1024),Image.LANCZOS)).astype(np.float32)
    img=seamless(img)
    img=np.asarray(Image.fromarray(img.clip(0,255).astype(np.uint8)).resize((N,N),Image.LANCZOS)).astype(np.float32)
    L0=lum(img);mean=img.reshape(-1,3).mean(0);detail=(L0-L0.mean())
    atlas=np.zeros((N*2,N*3,3),np.float32)
    for layer in range(3):
        light=hx(SOILS[era][layer][0])
        if layer==0:
            # oberste Schicht: Originalbild, Farbe nur leicht Richtung Zeitalter-Palette verschoben
            t=img+(light-mean)*.35
        else:
            # tiefere Schichten: Struktur desselben Bildes, gedreht, in der Schichtfarbe
            d=np.rot90(detail,layer)
            k=1.15 if layer==1 else 1.3
            t=light[None,None,:]+d[...,None]*k*(light.mean()/max(60,L0.mean()))
        # harte Variante: gleiche Farbe, mehr Kontrast, etwas dunkler, andere Lage
        th=np.rot90(t,2);tm=th.reshape(-1,3).mean(0);th=(tm+(th-tm)*1.45)*.97
        atlas[:N,layer*N:(layer+1)*N]=t;atlas[N:,layer*N:(layer+1)*N]=th
    Image.fromarray(atlas.clip(0,255).astype(np.uint8)).save(f"{sys.argv[1]}/soil_{era}.webp","WEBP",quality=78,method=6)
    print(era)
