"""Misst in jedem Exponat-Bild (src/assets/ex_*.webp) den Holzsockel:
vordere Ecke unten (bx,by), linke und rechte Ecke (lx,ly / rx,ry).
Ausgabe als JS-Objekt HALLMETA zum Einfügen in game.html.
Aufruf: python3 tools/hall/meta.py src/assets"""
import sys, os, json, numpy as np
from PIL import Image
from scipy import ndimage
d = sys.argv[1]; out = {}
for f in sorted(os.listdir(d)):
    if not (f.startswith("ex_") and f.endswith(".webp")): continue
    a = np.array(Image.open(os.path.join(d, f)).convert("RGBA")).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    wood = (al > 200) & (r > 70) & (r < 215) & (g < r * .62) & (b < r * .55)   # rotbraunes Holz
    wood = ndimage.binary_opening(wood, iterations=4)   # dünne Umrisslinien der Knochen entfernen
    lab, n = ndimage.label(wood); sz = ndimage.sum(wood, lab, range(n + 1))
    big = int(np.argmax(sz)); top = np.where(lab == big)[0].min(); sl = ndimage.find_objects(lab)
    cy = [c[0] for c in ndimage.center_of_mass(wood, lab, range(1, n + 1))]   # Mitte jeder Fläche: rötliche Hörner liegen über dem Sockel
    # Sockel kann durch Füße geteilt sein; Teile oberhalb des Sockels (rötliche Knochen) zählen nicht
    m = np.isin(lab, [i for i in range(1, n + 1) if sz[i] > sz.max() * .03 and sl[i - 1][0].stop > top and cy[i - 1] > top])
    ys, xs = np.where(m)
    by = ys.max(); bx = int(xs[ys >= by - 2].mean())
    lx = xs.min(); ly = int(ys[xs <= lx + 2].mean())
    rx = xs.max(); ry = int(ys[xs >= rx - 2].mean())
    out[f[3:-5]] = [a.shape[1], a.shape[0], bx, int(by), int(lx), ly, int(rx), ry]
print("const HALLMETA=" + json.dumps(out, separators=(",", ":")) + ";   // [w,h, Sockel vorne x,y, links x,y, rechts x,y]  (tools/hall/meta.py)")
