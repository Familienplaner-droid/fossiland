"""Museumsmodelle für Wirbellose und frühe Tiere (Erweiterung Kambrium–Karbon).
Gleiche Kamera/Licht/Maske wie skel3d.py. Teile: 1..5 = Spielteile 0..4, 6 = Ständer."""
import sys, math, time
sys.path.insert(0, "/home/claude/fossil3d")
import bpy
from mathutils import Vector, Matrix
from lib import *
import skel3d as K
from skel3d import W, U, Builder, setup_render, RW, RH

def P3(x, y, d=0.0):
    X, Z = W(x, y); return (X, d, Z)

class IB(Builder):
    def ell(self, x, y, rx, ry, dep, d=0.0, mat=None, rot=0.0):
        ob = sphere(P3(x, y, d), 1, mat or self.bone, scale=(rx * U, dep, ry * U), seg=28)
        if rot: ob.rotation_euler = (0, -rot, 0)
        return ob
    def poly(self, pts, dep, d=0.0, mat=None, bev=None):
        return slab([W(*p) for p in pts], dep, bev if bev is not None else min(0.05, dep * 0.35), mat or self.bone, loc=(0, d, 0))
    def line(self, pts, w, d=0.0, mat=None, taper=(1, 1), joints=False, n=None):
        P = [P3(x, y, dd) for x, y, dd in [(p[0], p[1], p[2] if len(p) > 2 else d) for p in pts]]
        if len(P) >= 3: P = smooth_path(P, n or max(10, len(P) * 6))
        m = len(P); tube(P, w * U * 0.55, mat or self.bone, radii=[taper[0] + (taper[1] - taper[0]) * i / (m - 1) for i in range(m)])
        if joints:
            for p in [P3(x, y, d) for x, y in pts]: sphere(p, w * U * 0.7, mat or self.bone, seg=14)
    def spike(self, a, b, r, d=0.0, mat=None):
        self.line([a, b], r, d, mat, taper=(1, 0.08))

def arc(cx, cy, rx, ry, a0, a1, n=24):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / (n - 1))), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / (n - 1)))) for k in range(n)]

# ---------- Trilobiten (Rückenansicht, schräg auf Ständer) ----------
def trilo(B, hx0=128, hl=34, hw=26, nseg=17, tx0=46, taper=.55, gen=48, pleu=9, pyl=10, pyw=10, tail=0, eyes=1, glab=1.0, spines_up=0):
    tx1 = hx0
    def head():
        B.poly(arc(hx0, 50, hl, hw, -90, 90, 40) + [(hx0 - 3, 50 + hw), (hx0 - 3, 50 - hw)][::-1][::-1], .16, .02)
        B.ell(hx0 + hl * .42, 50, hl * .46 * glab, hw * .3 * glab, .2, .0)
        B.ell(hx0 + 1, 50, 4, hw * .36, .16, .01)
        if eyes:
            for s in (-1, 1):
                B.ell(hx0 + hl * .3, 50 + s * hw * .52, 6 * eyes, 4 * eyes, .16 * eyes, -.01)
        B.line(arc(hx0, 50, hl * .93, hw * .93, -88, 88, 30), 1.6, -.02)
    B.part(1, head)
    def hwid(t): return hw * (1 - (1 - taper) * t)
    xs = [tx1 - (tx1 - tx0) * (i + .5) / nseg for i in range(nseg)]
    dx = (tx1 - tx0) / nseg
    def thorax():
        for i, x in enumerate(xs):
            w = hwid(i / max(1, nseg - 1))
            h = dx * .44
            B.poly([(x + h, 50 - w), (x + h, 50 + w), (x - h, 50 + w), (x - h, 50 - w)], .1, .03, bev=.035)
            B.ell(x, 50, dx * .6, w * .3, .16, .0)
            for s in (-1, 1):
                B.line([(x + h * .3, 50 + s * w * .34), (x - h * .5, 50 + s * w * .95)], 1.0, -.03)
    B.part(2, thorax)
    def pyg():
        w = pyw
        B.poly(arc(tx0, 50, pyl, w, 90, 270, 30), .14, .02)
        B.ell(tx0 - pyl * .25, 50, pyl * .55, w * .3, .17, 0)
    B.part(3, pyg)
    def legs():
        for i, x in enumerate(xs[::2]):
            w = hwid(2 * i / max(1, nseg - 1))
            for s in (-1, 1):
                B.line([(x + 1, 50 + s * (w - 4)), (x - 1, 50 + s * (w + 5)), (x - 4, 50 + s * (w + 8))], 1.5, .14, joints=True)
    B.part(4, legs)
    def spines():
        for s in (-1, 1):
            B.spike((hx0 - 1, 50 + s * (hw - 1)), (hx0 - gen, 50 + s * (hw + 5)), 3.0)
        if pleu:
            for i, x in enumerate(xs):
                w = hwid(i / max(1, nseg - 1))
                for s in (-1, 1):
                    B.spike((x, 50 + s * (w - 2)), (x - pleu * .7, 50 + s * (w + pleu * .45)), 1.6, .02)
        if tail:
            B.spike((tx0 - pyl + 2, 50), (tx0 - pyl - tail, 50), 2.6)
        if spines_up:
            B.spike((hx0 + hl * .4, 50), (hx0 + hl * .4 + 1, 50), 2.2, -.3)
    B.part(5, spines)

# ---------- Anomalocaris / Opabinia (Rückenansicht) ----------
def anoma(B):
    def head():
        B.ell(150, 50, 13, 11, .22)
        for s in (-1, 1):
            B.line([(148, 50 + s * 7), (144, 50 + s * 18)], 2.4, .0)
            B.ell(143, 50 + s * 21, 6, 4.5, .2, -.02)
        B.ell(157, 50, 5, 5, .1, -.15)
    B.part(1, head)
    xs = [136 - i * 7.4 for i in range(11)]
    def body():
        for i, x in enumerate(xs):
            B.ell(x, 50, 4.4, 13 - i * .7, .2)
    B.part(2, body)
    def flaps():
        for i, x in enumerate(xs):
            w = 13 - i * .7; L = 16 - i * .5
            for s in (-1, 1):
                B.poly([(x + 3, 50 + s * (w - 2)), (x - 1, 50 + s * (w + L)), (x - 8, 50 + s * (w + L * .8)), (x - 5, 50 + s * (w - 3))], .04, .03, B.memb, bev=.004)
    B.part(3, flaps)
    def app():
        for s in (-1, 1):
            pts = [(158, 50 + s * 5), (168, 50 + s * 10), (177, 50 + s * 13), (184, 50 + s * 12), (188, 50 + s * 8)]
            B.line(pts, 3.2, -.02, joints=True, taper=(1, .5))
            for (x, y) in pts[1:4]:
                B.spike((x, y), (x + 2, y - s * 5), 1.0, -.02)
    B.part(4, app)
    def tail():
        for k, (dx, dy) in enumerate([(24, 7), (26, 15), (22, 23)]):
            for s in (-1, 1):
                B.poly([(60, 50 + s * 2), (60 - dx, 50 + s * dy), (60 - dx - 4, 50 + s * (dy + 3)), (58, 50 + s * 5)], .05, .02 + k * .01, B.memb, bev=.004)
    B.part(5, tail)

def opabi(B):
    def head():
        B.ell(138, 50, 9, 9, .2)
        for (y, l) in [(50, 0), (44, 1), (56, 1), (40, 2), (60, 2)]:
            x = 141 - l * 4
            B.line([(x, 50 + (y - 50) * .4, -.05), (x + 2, y, -.25)], 1.6)
            B.ell(x + 2, y, 3, 3, .1, -.27)
    B.part(1, head)
    xs = [126 - i * 5.8 for i in range(15)]
    def body():
        for i, x in enumerate(xs):
            B.ell(x, 50, 3.4, 9 - i * .3, .17)
    B.part(2, body)
    def flaps():
        for i, x in enumerate(xs):
            w = 9 - i * .3
            for s in (-1, 1):
                B.poly([(x + 2.5, 50 + s * (w - 2)), (x - 1, 50 + s * (w + 10)), (x - 5, 50 + s * (w + 8)), (x - 3, 50 + s * (w - 2))], .04, .03, B.memb, bev=.004)
    B.part(3, flaps)
    def prob():
        B.line([(146, 50, .05), (160, 50, .02), (172, 51, -.02), (180, 50, -.06)], 2.6, taper=(1, .7), n=30)
        for s in (-1, 1):
            B.line([(180, 50), (185, 50 + s * 3), (188, 50 + s * 1)], 1.6, -.06, taper=(1, .4))
            for k in range(3):
                B.spike((183 + k * 1.5, 50 + s * 2.4), (184 + k * 1.5, 50 + s * .6), .6, -.06)
    B.part(4, prob)
    def tail():
        for k, (dx, dy) in enumerate([(12, 3), (13, 7), (11, 11)]):
            for s in (-1, 1):
                B.poly([(40, 50 + s * 1.5), (40 - dx, 50 + s * dy), (40 - dx - 3, 50 + s * (dy + 2.5)), (39, 50 + s * 4)], .05, .02 + k * .01, B.memb, bev=.004)
    B.part(5, tail)

# ---------- Hallucigenia (Seitenansicht, steht auf den Beinen) ----------
def hallu(B):
    sp = [(30, 60), (60, 58), (100, 56), (140, 57), (158, 60)]
    def body():
        B.line(sp, 6.5, 0, taper=(.75, 1), n=40)
    B.part(2, body)
    def head():
        B.ell(165, 61, 8, 6, .26)
        for s in (-1, 1):
            B.ell(169, 58, 1.3, 1.3, .05, s * .2)
    B.part(1, head)
    xs = [56 + i * 15 for i in range(7)]
    def spines():
        for x in xs:
            y = K.y_at(sp, x) - 3
            for s in (-1, 1):
                B.spike((x, y, s * .12), (x - 4, y - 24, s * .3), 2.6)
    B.part(3, spines)
    def legs():
        for i, x in enumerate([50 + j * 14 for j in range(8)]):
            y = K.y_at(sp, x) + 3
            for s in (-1, 1):
                B.line([(x, y), (x + 1, y + 14), (x + 3, 88)], 2.0, s * .22, taper=(1, .7))
                B.spike((x + 3, 88), (x + 7, 89), .8, s * .22, B.dark)
    B.part(4, legs)
    def tail():
        B.line([(32, 60), (22, 63), (16, 70), (17, 77)], 4.6, 0, taper=(1, .35))
    B.part(5, tail)

def mount(B, tilt=-26, piv=(0, 0, 2.0), rod_to=None):
    sc = bpy.context.scene
    obs = [o for o in sc.objects if o.name in B.parts]
    e = bpy.data.objects.new("pivot", None); link(e); e.location = piv
    bpy.context.view_layer.update()
    for o in obs:
        mw = o.matrix_world.copy(); o.parent = e; o.matrix_parent_inverse = e.matrix_world.inverted(); 
    e.rotation_euler = (math.radians(tilt), 0, 0)
    bpy.context.view_layer.update()
    def stand():
        X, Z = W(96, 54)
        cyl((X, .35, piv[2] / 2), 0.035, piv[2], B.metal)
        cyl((X, .35, 0.04), 0.55, 0.08, B.metal, bevel=0.02)
    B.part(6, stand)

SPEC = {
    "parad": lambda B: (trilo(B, hx0=130, hl=30, hw=26, nseg=19, tx0=40, taper=.5, gen=58, pleu=11, pyl=6, pyw=7), mount(B)),
    "anoma": lambda B: (anoma(B), mount(B)),
    "opabi": lambda B: (opabi(B), mount(B)),
    "hallu": lambda B: hallu(B),
}

if __name__ == "__main__":
    ids = sys.argv[-1].split(",")
    for cid in (SPEC if ids == ["all"] else ids):
        t = time.time()
        reset(samples=28, w=RW, h=RH)
        B = IB()
        SPEC[cid](B)
        setup_render(B, cid, K.OUT + "sk_" + cid) if hasattr(K, "OUT") else setup_render(B, cid, "/home/claude/fossil3d/out/sk_" + cid)
        print("DONE", cid, round(time.time() - t, 1), flush=True)
