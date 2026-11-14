"""Kachelbare Bodentexturen für das Grabungsfeld (ein Atlas je Zeitalter: 3 Schichten x weich/hart)."""
import numpy as np
from PIL import Image
SOILS=[
 [["#dd8f6c","#c2714f","#9a5538"],["#9a4e3e","#7d3d30","#5a2a21"],["#857b72","#686059","#4c4540"]],
 [["#e6bc7c","#cf9f5f","#a97a43"],["#b06e45","#93573a","#6e3f29"],["#857b72","#686059","#4c4540"]],
 [["#e6bc7c","#cf9f5f","#a97a43"],["#a07a52","#86633f","#634830"],["#d3caa9","#b8ae8d","#918769"]],
 [["#d9b680","#c09a63","#9b7746"],["#ece7da","#d3cdbc","#aaa391"],["#7d746c","#615a54","#46413d"]],
 [["#9a7a54","#80633f","#5e472c"],["#6e5a44","#574634","#3d3024"],["#4f4b45","#3b3934","#2a2825"]],
 [["#e3f1f7","#c2dce8","#98bfd1"],["#dcbc8c","#c3a170","#9c7e52"],["#8e8a84","#716d68","#55524e"]]]
N=384
hx=lambda h:np.array([int(h[i:i+2],16) for i in (1,3,5)],np.float32)/255
yy,xx=np.mgrid[0:N,0:N]
def field(rng,scale,power=2.0):
    # periodisches Rauschen über FFT, dadurch automatisch nahtlos
    f=np.fft.fftfreq(N)[:,None]**2+np.fft.fftfreq(N)[None,:]**2
    amp=1/np.maximum(f,1e-6)**(power/2);amp[0,0]=0;amp*=np.exp(-f*(N/scale)**-2*0) 
    amp[f>(scale/N)**2*40]=0 if scale<0 else amp[f>(scale/N)**2*40]
    ph=rng.random((N,N))*2*np.pi
    v=np.real(np.fft.ifft2(amp*np.exp(1j*ph)));v=(v-v.mean())/v.std();return v
def blob_layer(rng,count,rmin,rmax,hard):
    h=np.zeros((N,N),np.float32);col=np.zeros((N,N),np.float32);ids=np.zeros((N,N),np.float32)
    for k in range(count):
        cx,cy=rng.random()*N,rng.random()*N;r=rng.uniform(rmin,rmax);ex=rng.uniform(.7,1.3);a=rng.random()*np.pi;tone=rng.random()
        for ox in (-N,0,N):
            for oy in (-N,0,N):
                dx=xx-(cx+ox);dy=yy-(cy+oy)
                if abs(cx+ox-N/2)>N/2+rmax*1.4 or abs(cy+oy-N/2)>N/2+rmax*1.4:continue
                u=(dx*np.cos(a)+dy*np.sin(a))/(r*ex);w=(-dx*np.sin(a)+dy*np.cos(a))/(r/ex)
                d=u*u+w*w;m=d<1
                bump=np.sqrt(np.clip(1-d,0,1))*r*.9
                upd=m&(bump>h);h[upd]=bump[upd];col[upd]=tone;ids[upd]=1
    return h,col,ids
def make(era,layer,hard,seed):
    rng=np.random.default_rng(seed)
    light,dark,peb=[hx(c) for c in SOILS[era][layer]]
    base=light*0.94+dark*0.06 if hard else light
    ice=era==5 and layer==0
    # Grundrelief: grob + fein
    big=field(rng,6,2.6);fine=field(rng,60,1.2)
    height=big*2.2+fine*0.6
    # Steine/Kiesel
    if ice: cnt,rmin,rmax=(6,4,9) if not hard else (14,6,14)
    else: cnt,rmin,rmax=(60,2,6) if not hard else (42,6,15)
    bh,bt,bid=blob_layer(rng,cnt,rmin,rmax,hard)
    if not hard:
        bh2,bt2,bid2=blob_layer(rng,22,4,9,False);m=bh2>bh;bh[m]=bh2[m];bt[m]=bt2[m];bid[m]=bid2[m]
    H=height+bh*1.6
    # Beleuchtung von oben links
    gy,gx=np.gradient(H)
    nx,ny,nz=-gx,-gy,np.ones_like(H)*2.2;l=np.sqrt(nx**2+ny**2+nz**2);nx/=l;ny/=l;nz/=l
    L=np.array([-.55,-.6,.58]);L/=np.linalg.norm(L)
    shade=np.clip(nx*L[0]+ny*L[1]+nz*L[2],0,1)
    # Schlagschatten der Steine (verschobene Maske, nahtlos durch roll)
    sh=np.roll(np.roll(bid,4,0),4,1)*(1-bid)
    sh=np.maximum(sh,np.roll(np.roll(bid,2,0),2,1)*(1-bid))
    # Farbe
    tint=(big*0.05+fine*0.025)[...,None]
    soil=base[None,None,:]*(1+tint)
    if ice:
        soil=soil*(0.92+0.1*field(rng,20,1.5)[...,None]*0.3)
    pc=np.where(hard,1,0)
    stone=(peb*(0.8+0.45*bt[...,None]) if not hard else (peb*0.55+light*0.45)*(0.8+0.4*bt[...,None]))
    if not hard:
        # helle und dunkle Körnchen gemischt
        lightgrain=np.clip(light*1.12,0,1)
        stone=np.where((bt>0.6)[...,None],lightgrain*(0.95+0.1*bt[...,None]),stone)
    col=np.where(bid[...,None]>0,stone,soil)
    lit=col*(0.55+0.75*shade[...,None])
    lit*= (1-0.32*sh[...,None])
    # feine Sprenkel
    sp=rng.random((N,N));lit=np.where((sp>0.985)[...,None],lit*0.75,lit);lit=np.where((sp<0.012)[...,None],np.clip(lit*1.18,0,1),lit)
    if ice:
        # Eisrisse
        cr=np.abs(field(rng,10,2.4));lit=np.where((cr<0.035)[...,None],lit*0.82,lit)
        lit=np.clip(lit+0.08*np.clip(shade-0.7,0,1)[...,None]*3,0,1)
    return (np.clip(lit,0,1)*255).astype(np.uint8)
if __name__=="__main__":
    import sys
    out=sys.argv[1]
    for era in range(6):
        atlas=Image.new("RGB",(N*3,N*2))
        for layer in range(3):
            for hard in (0,1):
                atlas.paste(Image.fromarray(make(era,layer,hard,era*100+layer*10+hard)),(layer*N,hard*N))
        atlas.save(f"{out}/soil_{era}.webp","WEBP",quality=80,method=6)
        print(era)
