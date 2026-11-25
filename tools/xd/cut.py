import sys,numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
def cut(src):
    im=Image.open(src)
    if im.mode=="RGBA" and np.array(im)[...,3].min()<200:
        o=im
    else:
        im=im.convert("RGB");a=np.array(im).astype(int);mn,mx=a.min(-1),a.max(-1)
        bgc=(mn>175)&((mx-mn)<16)
        lab,n=ndimage.label(bgc);idx=range(n+1)
        sz=ndimage.sum(bgc,lab,idx);mean=ndimage.mean(mn,lab,idx)
        edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
        keep=[i for i in range(1,n+1) if i in edge or (sz[i]>1500 and mean[i]>238)]
        bg=np.isin(lab,keep);bg=ndimage.binary_closing(bg,iterations=1);bg=ndimage.binary_dilation(bg,iterations=1)
        al=Image.fromarray(np.where(bg,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.8))
        o=im.convert("RGBA");o.putalpha(al)
    return o.crop(o.getchannel("A").getbbox())
if __name__=="__main__":
    out=sys.argv[1];ids=sys.argv[2::2];srcs=sys.argv[3::2];tiles=[]
    for i,s in zip(ids,srcs):
        o=cut(s);o.save(f"{out}/{i}.png");print(i,o.size)
        t=Image.new("RGBA",(300,300),(40,90,60,255));o2=o.copy();o2.thumbnail((290,290));t.alpha_composite(o2,((300-o2.width)//2,(300-o2.height)//2));tiles.append(t)
    cols=6;rows=(len(tiles)+cols-1)//cols
    sh=Image.new("RGB",(300*cols,300*rows));[sh.paste(t.convert("RGB"),((k%cols)*300,(k//cols)*300)) for k,t in enumerate(tiles)];sh.save(f"{out}/check.png")
