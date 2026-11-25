import sys, math, time
sys.path.insert(0, "/home/claude/fossil3d")
import bpy
from mathutils import Vector
from lib import *

from propsbase import setup_top, bone_mat, long_bone
OUTS = "/home/claude/fossil3d/outspr/"
Z = 0.14
def ell(x, y, rx, ry, rz, m, z=Z, rot=0):
    o = sphere((x, y, z), 1, m, scale=(rx, ry, rz), seg=28); o.rotation_euler = (0, 0, rot); return o
def poly(pts, dep, m, z=0.0, bev=0.03):
    return slab(pts, dep, bev, m, loc=(0, 0, z + dep / 2), rot=(0, 0, 0))
def line(pts, r, m, taper=(1, 1), z=Z, n=None):
    P = [(p[0], p[1], p[2] if len(p) > 2 else z) for p in pts]
    if len(P) >= 3: P = smooth_path(P, n or len(P) * 8)
    k = len(P); tube(P, r, m, radii=[taper[0] + (taper[1] - taper[0]) * i / (k - 1) for i in range(k)])
def spike(a, b, r, m, z=Z): line([a, b], r, m, (1, .06), z)
def arc(cx, cy, rx, ry, a0, a1, n=30):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / (n - 1))), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / (n - 1)))) for k in range(n)]
def jointed(pts, r, m, z=Z):
    for a, b in zip(pts, pts[1:]): line([a, b], r, m, (1, .85), z)
    for p in pts[:-1]: sphere((p[0], p[1], z), r * 1.25, m, seg=16)
def memb():
    return mat_basic("memb", hexc("#e8d4aa"), rough=0.6, ao=0.2)

# ---- Trilobit ----
def tr_head():
    setup_top(2, 2); m = bone_mat()
    poly(arc(0, -.3, .86, 1.12, 0, 180, 40), .14, m)
    ell(0, .2, .26, .46, .16, m); ell(0, -.22, .2, .1, .12, m)
    for s in (-1, 1):
        ell(s * .46, .02, .13, .2, .12, m); spike((s * .8, -.28), (s * .86, -.98), .07, m, .08)
    line(arc(0, -.3, .8, 1.04, 5, 175, 30), .025, m, z=.15)
def tr_seg():
    setup_top(4, 1); m = bone_mat()
    for y in (.2, -.2):
        poly([(-1.55, y + .13), (1.55, y + .13), (1.55, y - .13), (-1.55, y - .13)], .1, m, bev=.04)
        ell(0, y, .4, .16, .14, m)
        for s in (-1, 1):
            spike((s * 1.5, y), (s * 1.95, y - .3), .07, m, .06)
            line([(s * .55, y + .05), (s * 1.4, y - .06)], .02, m, z=.12)
def tr_tail():
    setup_top(1, 3); m = bone_mat()
    poly(arc(0, .9, .44, .9, 180, 360, 30) + [(.44, .9), (-.44, .9)][::-1][::-1], .13, m)
    for k in range(4): ell(0, .75 - k * .22, .15 - k * .02, .09, .1, m)
    spike((0, .05), (0, -1.4), .08, m, .08)
def tr_leg():
    setup_top(2, 3); m = bone_mat()
    jointed([(-.5, 1.3), (-.45, .7), (-.5, .1), (-.45, -.5), (-.35, -1.05), (.15, -1.2), (.7, -1.15)], .085, m)
    for k in range(9): line([(-.38, 1.05 - k * .17), (-.05, .95 - k * .19)], .03, m, (1, .4))
def tr_spine():
    setup_top(2, 2); m = bone_mat()
    spike((-.8, .75), (.85, -.85), .13, m); spike((-.35, .85), (.9, -.2), .09, m, .1)

# ---- Anomalocaris & Co ----
def so_head():
    setup_top(2, 2); m = bone_mat()
    ell(0, .1, .62, .52, .25, m)
    for s in (-1, 1):
        line([(s * .4, .3), (s * .72, .7)], .07, m); ell(s * .76, .74, .2, .16, .14, m, .16)
    for k in range(12):
        a = k / 12 * 2 * math.pi; ell(.0 + .3 * math.cos(a), -.45 + .3 * math.sin(a), .1, .07, .07, m, .3, a)
def so_body():
    setup_top(4, 1); m = bone_mat()
    for k in range(6): ell(-1.55 + k * .62, 0, .28, .4 - k * .02, .2, m)
def so_flap():
    setup_top(1, 3); m = memb()
    poly([(-.15, 1.35), (.35, 1.2), (.4, .2), (.2, -1.0), (0, -1.4), (-.3, -.9), (-.4, .4)], .05, m, bev=.02)
    b = bone_mat()
    for k in range(6): line([(-.1 + k * .02, 1.1 - k * .05), (.05 + k * .03, -.8 + k * .1)], .015, b, z=.07)
def so_app():
    setup_top(2, 3); m = bone_mat()
    pts = [(-.5, 1.3), (-.5, .75), (-.48, .2), (-.42, -.35), (-.3, -.85), (.1, -1.15), (.55, -1.1), (.8, -.85)]
    jointed(pts, .1, m)
    for (x, y) in pts[1:-1]: spike((x + .05, y), (x + .38, y - .12), .035, m, .12)
def so_tail():
    setup_top(2, 2); m = memb()
    for k, ang in enumerate((-10, -32, -55)):
        a = math.radians(ang); L = 1.35
        x0, y0 = -.7, .7; x1, y1 = x0 + L * math.cos(a), y0 + L * math.sin(a)
        nx, ny = -math.sin(a) * .13, math.cos(a) * .13
        poly([(x0, y0), (x1 + nx, y1 + ny), (x1 + math.cos(a) * .2, y1 + math.sin(a) * .2), (x1 - nx, y1 - ny)], .05, m, z=k * .02, bev=.01)
    ell(-.7, .7, .18, .16, .1, bone_mat())

# ---- Hallucigenia ----
def lo_head():
    setup_top(2, 2); m = bone_mat()
    line([(-.95, -.3), (-.2, -.15)], .2, m, (1, 1.1)); ell(.25, -.05, .5, .38, .3, m)
    ell(.55, .08, .06, .06, .05, mat_basic("eye", hexc("#4a3a2a"), rough=.4), .42)
def lo_body():
    setup_top(4, 1); m = bone_mat()
    line([(-1.9, 0), (1.9, .05)], .24, m)
    for k in range(13): ell(-1.7 + k * .28, .02, .04, .25, .245, m)
def lo_spine():
    setup_top(1, 3); m = bone_mat()
    spike((-.08, -1.25), (.1, 1.35), .17, m); spike((.22, -1.25), (.32, .9), .11, m, .08)
def lo_leg():
    setup_top(2, 3); m = bone_mat(); c = mat_basic("claw", hexc("#5a4632"), rough=.35)
    line([(-.5, 1.35), (-.48, .3), (-.45, -.8), (-.3, -1.15)], .13, m, (1, .7))
    for k in range(2): line([(-.3, -1.15), (.25 + k * .3, -1.2 - k * .05)], .05, c, (1, .2))
def lo_tail():
    setup_top(2, 2); m = bone_mat()
    line([(-.95, .55), (-.2, .5), (.35, .2), (.6, -.3), (.62, -.85)], .19, m, (1, .35))

# ---- Seeskorpione, Skorpion, Tausendfüßer ----
def ar_head():
    setup_top(2, 2); m = bone_mat()
    poly(arc(0, -.2, .8, .95, 0, 180, 30), .14, m)
    for s in (-1, 1): ell(s * .38, .25, .14, .1, .1, m, .2)
    line(arc(0, -.2, .74, .88, 8, 172, 24), .025, m, z=.15)
def ar_seg():
    setup_top(4, 1); m = bone_mat()
    for y, w in ((.22, 1.7), (-.2, 1.6)): ell(0, y, w, .2, .14, m)
    for y in (.22, -.2): line([(-1.3, y + .05), (1.3, y + .05)], .02, m, z=.24)
def ar_abd():
    setup_top(1, 3); m = bone_mat()
    for k in range(4): ell(0, 1.0 - k * .62, .36 - k * .04, .28, .16, m)
def ar_leg():
    setup_top(2, 3); m = bone_mat()
    jointed([(-.45, 1.3), (-.35, .65), (-.4, 0), (-.3, -.6), (-.1, -1.1), (.25, -1.3)], .09, m)
    for k in range(5): spike((-.35 + k * .02, .9 - k * .45), (-.12 + k * .03, .85 - k * .45), .03, m, .12)
def ar_tail():
    setup_top(2, 2); m = bone_mat()
    ell(-.55, .55, .25, .22, .14, m); spike((-.45, .45), (.85, -.85), .14, m)

# ---- Cameroceras ----
def sh_tip():
    setup_top(2, 2); m = bone_mat()
    spike((-.6, .6), (.9, -.9), .42, m); line([(-.45, .45), (.1, -.1)], .03, m, z=.32)
def sh_cham():
    setup_top(4, 1); m = bone_mat(); d = mat_basic("sep", hexc("#8a7354"), rough=.5)
    line([(-1.9, 0), (1.9, 0)], .33, m, (.85, 1))
    for k in range(7): ell(-1.6 + k * .53, 0, .05, .34, .34, d)
def sh_body():
    setup_top(2, 3); m = bone_mat(); d = mat_basic("hole", hexc("#5b4a36"), rough=.5)
    line([(0, 1.3), (0, -1.0)], .55, m, (.85, 1)); ell(0, -1.05, .5, .18, .2, d, .45)
def sh_arm():
    setup_top(2, 3); m = bone_mat()
    line([(-.5, 1.3), (-.2, .6), (-.35, -.1), (.1, -.7), (.5, -1.1), (.7, -.8)], .12, m, (1, .3))
    for k in range(6): ell(-.3 + k * .14, .9 - k * .35, .05, .05, .05, m, .3)
def sh_beak():
    setup_top(2, 2); m = mat_basic("beak", hexc("#5a4632"), rough=.35)
    poly([(-.7, .5), (.6, .1), (.75, -.45), (.2, -.2), (-.7, -.1)], .25, m, bev=.08)

# ---- Riesenlibelle ----
def in_head():
    setup_top(2, 2); m = bone_mat()
    ell(0, -.1, .45, .4, .3, m)
    for s in (-1, 1): ell(s * .45, .25, .38, .4, .3, m, .2)
def in_thor():
    setup_top(4, 1); m = bone_mat()
    ell(-.3, 0, 1.2, .42, .32, m); ell(1.1, 0, .4, .3, .25, m)
def in_abd():
    setup_top(1, 3); m = bone_mat()
    for k in range(6): ell(0, 1.15 - k * .44, .2, .21, .16, m)
def in_wing():
    setup_top(2, 3); m = memb(); b = bone_mat()
    poly([(-.35, 1.35), (.25, 1.2), (.45, -.6), (.2, -1.35), (-.15, -1.3), (-.4, -.4)], .04, m, bev=.015)
    line([(-.3, 1.3), (-.25, -1.3)], .035, b, z=.07)
    for k in range(9): line([(-.27, 1.0 - k * .28), (.3, .9 - k * .28)], .012, b, z=.07)
def in_leg():
    setup_top(2, 3); m = bone_mat()
    jointed([(-.4, 1.3), (-.2, .4), (-.35, -.4), (.0, -1.0), (.4, -1.25)], .07, m)
    for k in range(6): spike((-.28 + k * .03, .1 - k * .2), (-.08 + k * .03, .05 - k * .2), .02, m, .1)

JOBS = {k: v for k, v in globals().items() if k[:3] in ("tr_", "so_", "lo_", "ar_", "sh_", "in_")}
if __name__ == "__main__":
    for n in (JOBS if sys.argv[-1] == "all" else sys.argv[-1].split(",")):
        t = time.time(); JOBS[n](); render(OUTS + n + ".png"); print("DONE", n, round(time.time() - t, 1), flush=True)
