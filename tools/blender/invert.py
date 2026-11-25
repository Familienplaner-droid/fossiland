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

# ---------- Seeskorpione / Skorpion (Rückenansicht) ----------
def eury(B, kind="euryp"):
    # Teile: 1 Kopf (Prosoma), 2 Panzer (vordere Segmente), 3 Hinterleib (hintere Segmente), 4 Beine, 5 Schwanz
    hx = 150; hl, hw = (16, 17) if kind != "pulmo" else (13, 13)
    def head():
        B.poly(arc(hx, 50, hl, hw, -95, 95, 30), .16, .02)
        for s in (-1, 1): B.ell(hx + 4, 50 + s * hw * .45, 3.2, 2.4, .12, -.02)
        if kind == "ptery":
            for s in (-1, 1):
                pts = [(hx + 12, 50 + s * 6), (hx + 24, 50 + s * 11), (hx + 34, 50 + s * 10)]
                B.line(pts, 3.0, -.02, joints=True)
                B.ell(hx + 38, 50 + s * 10, 7, 3.6, .14, -.02)
                for k in range(4): B.spike((hx + 34 + k * 2.4, 50 + s * (8.2)), (hx + 35 + k * 2.4, 50 + s * 5.6), .6, -.03)
        if kind == "pulmo":
            for s in (-1, 1):
                B.line([(hx + 10, 50 + s * 8), (hx + 18, 50 + s * 20), (hx + 28, 50 + s * 22)], 3.2, -.02, joints=True)
                B.ell(hx + 34, 50 + s * 21, 8, 4.6, .16, -.02)
                B.spike((hx + 38, 50 + s * 19), (hx + 46, 50 + s * 17), 1.6, -.02)
                B.spike((hx + 38, 50 + s * 23), (hx + 45, 50 + s * 22), 1.4, -.02)
    B.part(1, head)
    n1, n2 = (6, 6) if kind != "pulmo" else (7, 5)
    x0 = hx - hl * .2; seg = 7.2 if kind != "pulmo" else 6.4
    xs1 = [x0 - (i + .5) * seg for i in range(n1)]
    w1 = [hw * (1.02 + .1 * math.sin(i / (n1 - 1) * math.pi)) for i in range(n1)]
    def front():
        for x, w in zip(xs1, w1): B.ell(x, 50, seg * .6, w, .14)
    B.part(2, front)
    xb = xs1[-1] - seg * .5
    if kind == "pulmo":
        xs2 = [xb - (i + .5) * 8.5 for i in range(n2)]; w2 = [5.5 - i * .2 for i in range(n2)]
    else:
        xs2 = [xb - (i + .5) * seg * .95 for i in range(n2)]; w2 = [hw * (.85 - .1 * i) for i in range(n2)]
    def back():
        for x, w in zip(xs2, w2): B.ell(x, 50, (8.5 if kind == "pulmo" else seg) * .58, w, .15)
    B.part(3, back)
    def legs():
        n = 4
        for k in range(n):
            x = hx - 2 - k * 6
            for s in (-1, 1):
                L = 18 + k * 4
                pts = [(x, 50 + s * (hw - 3)), (x - 3 - k * 2, 50 + s * (hw + L * .5)), (x - 8 - k * 4, 50 + s * (hw + L))]
                B.line(pts, 2.0, .06, joints=True, taper=(1, .5))
        if kind != "pulmo":
            for s in (-1, 1):   # Schwimmpaddel
                B.line([(hx - 24, 50 + s * (hw - 2)), (hx - 32, 50 + s * (hw + 12))], 2.6, .05, joints=True)
                B.ell(hx - 40, 50 + s * (hw + 17), 9, 5, .07, .05, rot=-.5 * s)
    B.part(4, legs)
    xt = xs2[-1] - (8.5 if kind == "pulmo" else seg) * .55
    def tail():
        if kind == "ptery":
            B.ell(xt - 9, 50, 11, 8, .1); B.line([(xt - 2, 50), (xt - 18, 50)], 1.2, -.02)
        elif kind == "pulmo":
            B.ell(xt - 5, 50, 6, 4, .16); B.line([(xt - 9, 50), (xt - 15, 50 + 3), (xt - 16, 50 + 7)], 2.0, -.04, taper=(1, .1))
        else:
            B.spike((xt + 1, 50), (xt - 26, 50), 2.6)
    B.part(5, tail)

# ---------- Tausendfüßer ----------
def milli(B, n=22, w=9, legs=2):
    # 1 Kopf, 2 Panzer (vordere Hälfte), 3 Hinterleib (hintere Hälfte), 4 Beine, 5 Schwanz (letztes Segment)
    hx = 176; seg = 140 / n
    xs = [hx - 6 - (i + .5) * seg for i in range(n)]
    def head():
        B.ell(hx, 50, 6, w * .8, .2)
        for s in (-1, 1): B.line([(hx + 4, 50 + s * 3), (hx + 12, 50 + s * 8), (hx + 16, 50 + s * 7)], 1.2, -.02, taper=(1, .5))
    B.part(1, head)
    half = n // 2
    B.part(2, lambda: [B.ell(x, 50, seg * .58, w, .2) for x in xs[:half]])
    B.part(3, lambda: [B.ell(x, 50, seg * .58, w * (1 - .25 * max(0, i - n + 5) / 5), .2) for i, x in enumerate(xs) if half <= i < n - 1])
    def lg():
        for i, x in enumerate(xs[:-1]):
            for s in (-1, 1):
                for q in range(legs):
                    xx = x + (q - .5) * seg * .45
                    B.line([(xx, 50 + s * (w - 1)), (xx - 1, 50 + s * (w + 5)), (xx - 3, 50 + s * (w + 8))], 1.0, .1, taper=(1, .5))
    B.part(4, lg)
    B.part(5, lambda: B.ell(xs[-1], 50, seg * .6, w * .7, .18))

# ---------- Riesenlibelle ----------
def dragon(B):
    # 1 Kopf, 2 Brust, 3 Hinterleib, 4 Flügel, 5 Beine
    B.part(1, lambda: [B.ell(160, 50, 6, 8, .2)] + [B.ell(161, 50 + s * 5, 4.5, 4.5, .2, -.03) for s in (-1, 1)])
    B.part(2, lambda: B.ell(145, 50, 10, 6.5, .22))
    B.part(3, lambda: [B.ell(132 - i * 9, 50, 5, 3.2 - i * .1, .16) for i in range(10)])
    def wings():
        for s in (-1, 1):
            for k, (xb, xt, L, W2) in enumerate([(149, 168, 42, 16), (138, 118, 40, 18)]):
                tip = (xt, 50 + s * L)
                pts = [(xb + 3, 50 + s * 5), (xt + 4, 50 + s * L * .6), (xt + 3, 50 + s * (L - 2)), (xt - 3, 50 + s * L), (xt - W2, 50 + s * L * .7), (xb - 5, 50 + s * 6)]
                B.poly(pts, .03, .03 + k * .01, B.memb, bev=.004)
                B.line([(xb + 2, 50 + s * 5), (xt + 3, 50 + s * (L - 1))], .9, .02 + k * .01)
                for q in range(1, 4):
                    B.line([(xb - q * 2, 50 + s * 5), (xt - q * W2 / 4, 50 + s * (L - 3 - q * 4))], .4, .02 + k * .01)
    B.part(4, wings)
    B.part(5, lambda: [B.line([(150 - k * 5, 50 + s * 4), (153 - k * 7, 50 + s * 12), (150 - k * 9, 50 + s * 17)], 1.2, .12, joints=True, taper=(1, .5)) for k in range(3) for s in (-1, 1)])

# ---------- Cameroceras (gestrecktes Kammergehäuse, seitlich aufgeschnitten) ----------
def cone(B):
    # 1 Spitze, 2 Kammern, 3 Wohnkammer, 4 Fangarme, 5 Schnabel
    x0, x1 = 12, 150; r0, r1 = 1.5, 15
    R = lambda x: r0 + (r1 - r0) * (x - x0) / (x1 - x0)
    B.part(1, lambda: B.spike((40, 50), (x0, 50), R(40) * .55 * 2))
    def ch():
        for x in range(40, 118, 6):
            B.ell(x + 3, 50, 3.6, R(x + 3), .2 + R(x) * .01)
            B.ell(x + .5, 50, .8, R(x) * 1.02, .22, -.01, B.dark)
    B.part(2, ch)
    B.part(3, lambda: [B.ell(x, 50, 4.6, R(x), .22 + R(x) * .01) for x in range(120, 152, 4)])
    def arms():
        for k in range(8):
            s = -1 + 2 * k / 7
            B.line([(152, 50 + s * 9), (166, 50 + s * 13), (178, 50 + s * 15 + 2 * math.sin(k)), (186, 50 + s * 12)], 1.8, -.02, taper=(1, .3))
    B.part(4, arms)
    B.part(5, lambda: [B.ell(156, 50, 4, 3, .1, -.06, B.dark), B.spike((158, 50), (163, 50), 1.6, -.07, B.dark)])

SPEC = {
    "parad": lambda B: (trilo(B, hx0=130, hl=30, hw=26, nseg=19, tx0=40, taper=.5, gen=58, pleu=11, pyl=6, pyw=7), mount(B)),
    "anoma": lambda B: (anoma(B), mount(B)),
    "opabi": lambda B: (opabi(B), mount(B)),
    "hallu": lambda B: hallu(B),
    "isote": lambda B: (trilo(B, hx0=128, hl=34, hw=30, nseg=8, tx0=74, taper=.85, gen=0, pleu=0, pyl=34, pyw=27, eyes=.8, glab=1.1), mount(B)),
    "asaph": lambda B: (trilo(B, hx0=125, hl=30, hw=27, nseg=8, tx0=80, taper=.9, gen=0, pleu=0, pyl=28, pyw=24, eyes=1.0), B.part(5, lambda: [B.line([(134, 50 + s * 15, -.05), (134.5, 50 + s * 15, -.9)], 2.2) or B.ell(134.5, 50 + s * 15, 3, 3, .15, -.95) for s in (-1, 1)]), mount(B)),
    "dalma": lambda B: (trilo(B, hx0=130, hl=30, hw=25, nseg=11, tx0=70, taper=.6, gen=24, pleu=0, pyl=16, pyw=14, tail=14, eyes=1.5), mount(B)),
    "euryp": lambda B: (eury(B, "euryp"), mount(B)),
    "megag": lambda B: (eury(B, "euryp"), mount(B)),
    "ptery": lambda B: (eury(B, "ptery"), mount(B)),
    "pulmo": lambda B: (eury(B, "pulmo"), mount(B)),
    "pneum": lambda B: (milli(B, n=14, w=8, legs=2), mount(B)),
    "arthr": lambda B: (milli(B, n=24, w=14, legs=1), mount(B)),
    "megan": lambda B: (dragon(B), mount(B)),
    "camer": lambda B: (cone(B), mount(B, tilt=-10)),
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
