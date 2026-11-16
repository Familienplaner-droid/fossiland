"""Convert Blender renders into compact web assets in /home/claude/fossil3d/site/assets."""
import os, sys, glob
import numpy as np
from PIL import Image

SRC = "/home/claude/fossil3d/out/"
DST = "/home/claude/fossil3d/site/assets/"
os.makedirs(DST, exist_ok=True)


def webp(src, dst, q=82, size=None):
    im = Image.open(src).convert("RGBA")
    if size:
        im = im.resize(size, Image.LANCZOS)
    im.save(DST + dst, "WEBP", quality=q, method=6, alpha_quality=90)


what = sys.argv[1:] or ["tiles", "floors", "props", "scenes", "skel"]

if "tiles" in what:
    sheet = Image.open(SRC + "tiles_sheet.png").convert("RGBA")
    slot = sheet.width / 9
    T = 126
    atlas = Image.new("RGBA", (9 * T, 6 * T))
    for r in range(6):
        for c in range(9):
            cx, cy = (c + 0.5) * slot, (r + 0.5) * slot
            atlas.paste(sheet.crop((round(cx - T / 2), round(cy - T / 2), round(cx + T / 2), round(cy + T / 2))), (c * T, r * T))
    atlas.save(DST + "tiles.webp", "WEBP", quality=84, method=6, alpha_quality=90)

if "floors" in what:
    for f in sorted(glob.glob(SRC + "floor_*.png")):
        webp(f, os.path.basename(f).replace(".png", ".webp"), q=72, size=(384, 432))

if "props" in what:
    for n in "skull vert rib leg foot amber ammo tooth trilo t_brush t_pick t_probe t_canteen coin t_radar t_jack".split():
        if os.path.exists(SRC + n + ".png"):
            webp(SRC + n + ".png", n + ".webp", q=86)

if "scenes" in what:
    for f in sorted(glob.glob(SRC + "scene_*.png")):
        webp(f, os.path.basename(f).replace(".png", ".webp"), q=88)

if "skel" in what:
    for f in sorted(glob.glob(SRC + "sk_*_mask.png")):
        cid = os.path.basename(f)[3:-9]
        col = Image.open(SRC + f"sk_{cid}.png").convert("RGBA")
        m = np.asarray(Image.open(f).convert("RGBA")).astype(np.int32)
        bits = (m[..., 0] > 127) * 1 + (m[..., 1] > 127) * 2 + (m[..., 2] > 127) * 4
        lut = np.array([0, 1, 2, 3, 4, 5, 6, 0])  # rgb bits -> part: R=1 G=2 RG=3 B=4 RB=5 GB=6
        # bits: R=1,G=2,B=4 ; colours: 1:(1,0,0)=1 2:(0,1,0)=2 3:(1,1,0)=3 4:(0,0,1)=4 5:(1,0,1)=5 6:(0,1,1)=6
        idx = np.where(m[..., 3] > 100, lut[bits], 0)
        a = np.asarray(col)[..., 3]
        # dilate part indices into anti-aliased edge / shadow-free coloured pixels
        for _ in range(4):
            hole = (idx == 0) & (a > 0)
            if not hole.any():
                break
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                sh = np.roll(np.roll(idx, dy, 0), dx, 1)
                fill = hole & (sh > 0) & (idx == 0)
                idx[fill] = sh[fill]
        Image.fromarray((idx * 40).astype(np.uint8), "L").save(DST + f"sk_{cid}_m.png", optimize=True)
        col.save(DST + f"sk_{cid}.webp", "WEBP", quality=80, method=6, alpha_quality=85)

tot = sum(os.path.getsize(p) for p in glob.glob(DST + "*"))
print(len(os.listdir(DST)), "files", round(tot / 1024), "KB")
