"""Builds and renders 3D museum skeletons from the same 2D body plans the game uses.
Each render produces a colour image and a part-index mask (1 skull, 2 spine, 3 ribs, 4 limbs, 5 feet/fins, 6 stand)."""
import sys, math, random, re, time
sys.path.insert(0, "/home/claude/fossil3d")
import bpy
from mathutils import Vector
from lib import *

RW, RH = 760, 384

PLANS = {
    "biped": dict(spine=[[8, 62], [40, 57], [78, 49], [116, 43], [136, 35], [146, 27]], skull=[160, 24, 1], ribs=[90, 118], legs=[[[80, 51], [90, 70], [82, 86]]], arms=[[[122, 45], [130, 56], [138, 58]]], feet=[[[82, 86], [97, 89]]]),
    "longneck": dict(spine=[[6, 66], [40, 61], [80, 53], [116, 47], [138, 31], [150, 15]], skull=[161, 11, .78], ribs=[82, 116], legs=[[[82, 55], [87, 73], [85, 88]], [[116, 49], [119, 70], [117, 88]]], arms=[], feet=[[[85, 88], [95, 90]], [[117, 88], [127, 90]]]),
    "quad": dict(spine=[[6, 63], [40, 53], [80, 45], [120, 47], [146, 55]], skull=[160, 59, .95], ribs=[70, 122], legs=[[[80, 47], [86, 69], [82, 88]], [[121, 49], [123, 70], [121, 88]]], arms=[], feet=[[[82, 88], [92, 90]], [[121, 88], [131, 90]]]),
    "mammal": dict(spine=[[4, 70], [12, 54], [36, 43], [76, 39], [114, 41], [134, 47]], skull=[150, 52, 1], ribs=[58, 112], legs=[[[56, 42], [61, 65], [58, 87]], [[112, 44], [115, 66], [113, 87]]], arms=[], feet=[[[58, 87], [68, 89]], [[113, 87], [123, 89]]], sk="mam"),
    "wing": dict(spine=[[56, 62], [76, 56], [96, 52], [110, 44]], skull=[124, 40, .9], ribs=[76, 98], legs=[[[98, 50], [72, 32], [22, 22]], [[102, 50], [128, 30], [178, 18]]], arms=[], legW=2.4, membrane=["M22 22L98 50L78 60Z", "M178 18L102 50L96 56Z"], feet=[[[78, 58], [74, 74], [82, 80]]], sk="beak", stand=1, wings=1),
    "sea": dict(spine=[[10, 60], [40, 58], [70, 54], [100, 54], [122, 42], [138, 26], [146, 16]], skull=[156, 14, .72], ribs=[58, 100], legs=[[[94, 60], [114, 76]], [[88, 60], [104, 80]]], arms=[], legW=5.5, feet=[[[62, 60], [46, 76]], [[56, 60], [38, 78]]], footW=5.5, stand=1),
    "fish": dict(spine=[[18, 50], [46, 52], [86, 50], [124, 48], [140, 48]], skull=[156, 48, 1], ribs=[60, 124], legs=[[[120, 54], [132, 70]], [[70, 54], [78, 66]]], arms=[], legW=4.5, fin="M18 50L4 30L12 50L4 70Z", stand=1),
}
SKULLS = {
    "rep": dict(d="M-12 -2Q-9 -11 3 -9Q14 -7 18 0Q16 4 6 5L-8 5Q-13 4 -12 -2Z", jaw="M-10 5Q2 7 15 5L15 7Q3 12 -8 9Z", eye=(-3, -3), teeth=1),
    "mam": dict(d="M-12 -3Q-10 -11 0 -10Q8 -9 12 -4L18 0Q16 5 6 5L-8 5Q-14 3 -12 -3Z", jaw="M-8 5Q2 7 13 5L13 7Q2 11 -6 9Z", eye=(-1, -4)),
    "beak": dict(d="M-10 -3Q-6 -9 2 -7L24 -1L2 3Q-8 4 -10 -3Z", eye=(-2, -3)),
    "gast": dict(d="M-10 -4Q-6 -12 4 -10Q16 -8 20 2Q12 6 0 5L-8 4Q-13 2 -10 -4Z", eye=(-2, -4)),
}
CRE = [  # id, plan, skull, skull scale
    ("dime", "quad", None, 1), ("edap", "quad", None, .8), ("scut", "quad", None, 1), ("inos", "mammal", None, 1.15), ("meso", "fish", None, .75),
    ("plat", "longneck", None, 1), ("herr", "biped", None, 1), ("coel", "biped", None, .85), ("eora", "biped", None, .8), ("noth", "sea", None, 1),
    ("arch", "biped", "beak", .8), ("allo", "biped", None, 1.15), ("steg", "quad", None, .8), ("brac", "longneck", None, 1), ("dipl", "longneck", None, 1), ("icht", "fish", None, 1), ("rham", "wing", None, 1),
    ("tric", "quad", None, 1), ("velo", "biped", None, .85), ("anky", "quad", None, 1), ("spin", "biped", None, 1), ("trex", "biped", None, 1.4), ("pter", "wing", None, 1), ("mosa", "fish", None, 1.25), ("pars", "biped", None, 1), ("igua", "biped", None, 1),
    ("gast", "biped", "gast", 1.2), ("basi", "fish", None, 1), ("darw", "mammal", None, .75), ("prop", "mammal", None, .85), ("andr", "mammal", None, 1.3), ("prac", "mammal", None, 1),
    ("mamm", "mammal", None, 1.2), ("smil", "mammal", None, 1), ("nash", "mammal", None, 1), ("baer", "mammal", None, 1.1), ("megl", "mammal", None, 1), ("glyp", "quad", None, .8),
    ("acant", "quad", None, .9),
    ("pikai", "fish", None, .55),
    ("sacab", "fish", None, .7), ("clima", "fish", None, .65), ("dunkl", "fish", None, 1.35), ("bothr", "fish", None, .75), ("clado", "fish", None, .9), ("megal", "fish", None, 1.4),
    ("tikta", "quad", None, .9), ("hylon", "quad", None, .7), ("crass", "quad", None, 1.05),
    ("deino", "mammal", None, 1.3), ("thyla", "mammal", None, .95), ("chali", "mammal", None, 1.05), ("titan", "biped", "gast", 1.1),
]

U = 1 / 20.0


def W(x, y):  # svg body coords -> world (X, Z)
    return ((x - 95) * U, (90 - y) * U)


def parse(d):
    """SVG path (M m L l Q q Z) -> list of subpaths [(x,y),...] with quadratics sampled."""
    toks = re.findall(r"[MmLlQqZz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    i, cur, start, subs, pts, cmd = 0, (0, 0), (0, 0), [], [], None
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        t = toks[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t; i += 1
            if cmd in "Zz":
                if pts:
                    subs.append((pts, True)); pts = []
                cur = start
                continue
        if cmd in "Mm":
            x, y = num(), num()
            if cmd == "m": x, y = cur[0] + x, cur[1] + y
            if pts: subs.append((pts, False))
            pts = [(x, y)]; cur = start = (x, y)
            cmd = "L" if cmd == "M" else "l"
        elif cmd in "Ll":
            x, y = num(), num()
            if cmd == "l": x, y = cur[0] + x, cur[1] + y
            pts.append((x, y)); cur = (x, y)
        elif cmd in "Qq":
            cx, cy, x, y = num(), num(), num(), num()
            if cmd == "q": cx, cy, x, y = cur[0] + cx, cur[1] + cy, cur[0] + x, cur[1] + y
            for k in range(1, 9):
                tt = k / 8
                pts.append(((1 - tt) ** 2 * cur[0] + 2 * tt * (1 - tt) * cx + tt * tt * x, (1 - tt) ** 2 * cur[1] + 2 * tt * (1 - tt) * cy + tt * tt * y))
            cur = (x, y)
        else:
            i += 1
    if pts: subs.append((pts, False))
    return subs


def lerp_path(P, n):
    seg, L = [], 0
    for i in range(1, len(P)):
        d = math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); seg.append(d); L += d
    out = []
    for k in range(n):
        t = k / (n - 1) * L; i = 0
        while i < len(seg) - 1 and t > seg[i]:
            t -= seg[i]; i += 1
        f = t / seg[i] if seg[i] else 0
        out.append((P[i][0] + (P[i + 1][0] - P[i][0]) * f, P[i][1] + (P[i + 1][1] - P[i][1]) * f, k / (n - 1)))
    return out


def y_at(P, x):
    if x <= P[0][0]: return P[0][1]
    for i in range(1, len(P)):
        if x <= P[i][0]:
            f = (x - P[i - 1][0]) / (P[i][0] - P[i - 1][0]); return P[i - 1][1] + (P[i][1] - P[i - 1][1]) * f
    return P[-1][1]


class Builder:
    def __init__(self):
        self.bone = mat_basic("bone", hexc("#efe2c4"), rough=0.5, noise=(hexc("#dcc79c"), 3.0, 6), bump=0.22, bump_scale=22, ao=0.35)
        self.ivory = mat_basic("ivory", hexc("#fbf3e2"), rough=0.3, coat=0.4, ao=0.2)
        self.memb = mat_basic("memb", hexc("#e6d2a8"), rough=0.6, alpha=0.55, ao=0.2)
        self.dark = mat_basic("claw", hexc("#6a5238"), rough=0.35)
        self.metal = mat_basic("stand", hexc("#3a3f46"), rough=0.3, metal=1.0)
        self.parts = {}
        self.cur = 0

    def tag(self, before):
        for ob in bpy.context.scene.objects:
            if ob.name not in before and ob.type in ('MESH', 'CURVE'):
                ob.pass_index = self.cur
                self.parts[ob.name] = self.cur

    def part(self, idx, fn, *a, **k):
        before = set(o.name for o in bpy.context.scene.objects)
        self.cur = idx
        r = fn(*a, **k)
        self.tag(before)
        return r

    # --- primitives in svg body coordinates ---
    def tube_svg(self, pts, w, y=0.0, mat=None, taper=None, joints=False):
        P = [(*W(x, yy)[:1], y, W(x, yy)[1]) for x, yy in pts]
        P = [(p[0], p[1], p[2]) for p in P]
        if len(P) >= 3 and not joints:
            P = smooth_path(P, max(8, len(P) * 6))
        r = w * U * 0.55
        radii = None
        if taper:
            n = len(P); radii = [taper[0] + (taper[1] - taper[0]) * i / (n - 1) for i in range(n)]
        tube(P, r, mat or self.bone, radii=radii)
        if joints:
            for p in P:
                sphere(p, r * 1.3, mat or self.bone, seg=16)

    def slab_svg(self, d, depth, y=0.0, mat=None, xform=None):
        for pts, closed in parse(d):
            if xform: pts = [xform(*p) for p in pts]
            outline = [W(*p) for p in pts]
            if len(outline) >= 3:
                slab(outline, depth, min(0.04, depth * 0.3), mat or self.bone, loc=(0, y + depth / 2, 0))

    def path_svg(self, d, w, y=0.0, mat=None, xform=None, taper=None):
        for pts, closed in parse(d):
            if xform: pts = [xform(*p) for p in pts]
            if len(pts) >= 2:
                self.tube_svg(pts, w, y, mat, taper=taper)

    def ell(self, cx, cy, rx, ry, depth, y=0.0, mat=None):
        X, Z = W(cx, cy)
        sphere((X, y, Z), 1, mat or self.bone, scale=(rx * U, depth, ry * U), seg=24)


def build(cid, plan, skt, ss):
    B = Builder()
    P = PLANS[plan]
    D = 0.32 if plan not in ("fish", "wing") else 0.12   # half body depth for paired limbs

    # spine (part 2)
    def spine():
        pts = lerp_path(P["spine"], 26)
        for x, y, t in pts:
            r = (1.5 + math.sin(min(1, t * 1.15) * math.pi) * 1.9) * U * 1.15
            X, Z = W(x, y)
            sphere((X, 0, Z), r, B.bone, scale=(0.95, 1.1, 1.0), seg=16)
            if 0.15 < t < 0.85 and plan != "fish":
                cone((X, 0, Z + r * 1.15), r * 0.5, r * 0.2, r * 1.1, B.bone, verts=10)
        tube([(W(x, y)[0], 0, W(x, y)[1]) for x, y, t in pts], 0.035, B.bone)
    B.part(2, spine)

    # ribs (part 3)
    def ribs():
        x = P["ribs"][0]
        while x <= P["ribs"][1]:
            y = y_at(P["spine"], x)
            t = (x - P["ribs"][0]) / (P["ribs"][1] - P["ribs"][0])
            l = ((8 if plan == "fish" else 10) + math.sin(t * math.pi) * (7 if plan == "fish" else 10)) * U
            X, Z = W(x, y)
            spread = 0.12 + l * 0.75
            for s in (-1, 1):
                pts = smooth_path([(X, s * 0.05, Z), (X + 0.1, s * spread, Z - l * 0.45), (X - 0.04, s * spread * 0.55, Z - l)], 14)
                tube(pts, 0.055, B.bone, radii=[1 - 0.45 * i / 13 for i in range(14)])
            x += 5.5
    B.part(3, ribs)

    # limbs (part 4)
    def limbs():
        lw = P.get("legW", 4)
        sides = (-D, D) if not P.get("wings") else (-0.05, 0.05)
        for li, leg in enumerate(P["legs"]):
            ys = sides if not P.get("wings") else (sides[li % 2],)
            for y in ys:
                B.tube_svg(leg, lw, y, joints=True)
        for arm in P["arms"]:
            for y in (-D * 0.8, D * 0.8):
                B.tube_svg(arm, 1.6 if cid == "trex" else 2.6, y, joints=True)
        for d in P.get("membrane", []):
            B.slab_svg(d, 0.04, -0.02, B.memb)
    B.part(4, limbs)

    # feet / fins (part 5)
    def feet():
        if P.get("fin"):
            B.slab_svg(P["fin"], 0.08, 0)
        else:
            fw = P.get("footW", 3)
            sides = (-D, D) if not P.get("wings") else (0,)
            for f in P["feet"]:
                for y in sides:
                    B.tube_svg(f, fw, y, joints=(plan == "wing"))
                    if plan not in ("sea",):
                        X, Z = W(*f[-1])
                        cone((X + 0.08, y, Z), 0.05, 0.0, 0.14, B.dark, rot=(0, math.pi / 2, 0), verts=10)
    B.part(5, feet)

    # skull (part 1)
    sx, sy, ps = P["skull"]
    SK = SKULLS[skt or P.get("sk", "rep")]
    S = ps * ss
    xf = lambda x, y: (sx + x * S, sy + y * S)

    def skull():
        dep = 0.5 * S
        for pts, closed in parse(SK["d"]):
            outline = [W(*xf(*p)) for p in pts]
            ob = slab(outline, dep, 0.11 * S, B.bone, loc=(0, dep / 2, 0))
            bpy.context.view_layer.objects.active = ob
            for o in bpy.context.selected_objects: o.select_set(False)
            ob.select_set(True)
            bpy.ops.object.convert(target='MESH')
            ex, ez = W(*xf(*SK["eye"]))
            cut = cyl((ex, 0, ez), 2.7 * S * U, 2, None, rot=(math.pi / 2, 0, 0))
            cut.hide_render = True
            bo = ob.modifiers.new("b", 'BOOLEAN'); bo.object = cut; bo.operation = 'DIFFERENCE'
            if SK is SKULLS["rep"]:
                fx, fz = W(*xf(6, -2))
                cut2 = cyl((fx, 0, fz), 2.0 * S * U, 2, None, rot=(math.pi / 2, 0, 0))
                cut2.scale = (1.5, 1, 1)
                cut2.hide_render = True
                b2 = ob.modifiers.new("b2", 'BOOLEAN'); b2.object = cut2; b2.operation = 'DIFFERENCE'
            smooth(ob)
        if SK.get("jaw"):
            for pts, closed in parse(SK["jaw"]):
                slab([W(*xf(*p)) for p in pts], dep * 0.8, 0.05 * S, B.bone, loc=(0, dep * 0.4, 0))
        if SK.get("teeth"):
            for i in range(6):
                X, Z = W(*xf(-4 + i * 3.2, 5.6))
                cone((X, -0.08 * S, Z - 0.04 * S), 0.035 * S, 0, 0.11 * S, B.ivory, rot=(math.pi, 0, 0), verts=10)
    B.part(1, skull)

    deco(B, cid, P, xf, S)

    # display stand for flying / swimming animals (part 6)
    if P.get("stand"):
        def stand():
            X, Z = W(96, 54)
            cyl((X, 0.0, Z / 2), 0.03, Z, B.metal)
            cyl((X, 0.0, 0.04), 0.5, 0.08, B.metal, bevel=0.02)
        B.part(6, stand)
    return B


def sail(B, P, x0, x1, h, idx=2):
    def f():
        y0, y1 = y_at(P["spine"], x0), y_at(P["spine"], x1)
        xm = (x0 + x1) / 2
        ym = y_at(P["spine"], xm) - h * 2
        top = []
        for k in range(11):
            t = k / 10
            x = x0 + (x1 - x0) * t
            by = (1 - t) ** 2 * y0 + 2 * t * (1 - t) * ym + t * t * y1
            top.append((x, by))
            if 0 < k < 10:
                B.tube_svg([(x, y_at(P["spine"], x)), (x, by)], 1.6, 0, taper=(1, 0.5))
        base = [(x, y_at(P["spine"], x)) for x in [x1 - (x1 - x0) * k / 10 for k in range(11)]]
        outline = [W(*p) for p in top + base]
        slab(outline, 0.03, 0.01, B.memb, loc=(0, 0.015, 0))
    B.part(idx, f)


def deco(B, cid, P, xf, S):
    sp = lambda d, idx, w, mat=None, sk=False, taper=None: B.part(idx, B.path_svg, d, w, 0, mat, xf if sk else None, taper)
    sh = lambda d, idx, dep=0.06, mat=None, sk=False, y=0.0: B.part(idx, B.slab_svg, d, dep, y, mat, xf if sk else None)
    if cid == "dime": sail(B, P, 44, 112, 26)
    if cid == "edap": sail(B, P, 48, 108, 18)
    if cid == "spin": sail(B, P, 70, 128, 20)
    if cid == "steg":
        pts = lerp_path(P["spine"], 14)[3:11]
        for k, (x, y, t) in enumerate(pts):
            sh(f"M{x-5} {y-2}L{x} {y-12-math.sin(k/7*math.pi)*8}L{x+5} {y-2}Z", 2, 0.05, y=(-0.07 if k % 2 else 0.07))
    if cid == "anky":
        B.part(2, B.ell, 9, 62, 7, 5, 0.22)
        for x, y, t in lerp_path(P["spine"], 12)[3:10]:
            for s in (-0.18, 0.18):
                B.part(2, lambda X=x, Y=y, s=s: cone((W(X, Y)[0], s, W(X, Y)[1] + 0.12), 0.07, 0, 0.22, B.bone, verts=10))
    if cid == "glyp":
        def shell():
            X, Z = W(78, 40)
            ob = sphere((X, 0, Z - 0.35), 1, B.bone, scale=(2.55, 0.85, 1.25), seg=32)
            m = mat_basic("shell", hexc("#e6d3a8"), rough=0.55, ao=0.3)
            nt = m.node_tree
            vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = 'DISTANCE_TO_EDGE'
            sock(vor, "Scale").default_value = 9
            bm = nt.nodes.new("ShaderNodeBump"); sock(bm, "Strength").default_value = 0.8
            nt.links.new(sock(vor, "Distance", out=True), sock(bm, "Height"))
            nt.links.new(sock(bm, "Normal", out=True), sock(nt.nodes["Principled BSDF"], "Normal"))
            assign(ob, m)
            bx = bpy.data.objects.new("cutter", None)
        B.part(2, shell)
    if cid == "tric":
        sh("M-10 -2Q-24 -20 -6 -16Z", 1, 0.08, sk=True)
        sp("M-2 -8L4 -18", 1, 2.2, B.ivory, sk=True, taper=(1, 0.2))
        sp("M6 -6L11 -15", 1, 2.2, B.ivory, sk=True, taper=(1, 0.2))
        sp("M15 -2L20 -7", 1, 2.0, B.ivory, sk=True, taper=(1, 0.2))
    if cid == "scut":
        for x, y in [(-6, -8), (0, -9), (6, -7)]:
            X, Y = xf(x, y)
            B.part(1, B.ell, X, Y, 2.2 * S, 2.2 * S, 0.1)
    if cid == "pars": sp("M-6 -6Q-20 -18 -32 -14", 1, 3, sk=True, taper=(1, 0.6))
    if cid == "pter": sh("M-6 -5L-28 -13L-4 -9Z", 1, 0.05, sk=True)
    if cid == "rham":
        sp("M56 62L18 80", 2, 1.6)
        sh("M14 80L18 74L22 80L18 86Z", 2, 0.04)
    if cid == "arch":
        for k in range(4):
            sp(f"M{130+k*2} 54l{10+k*2} {-6+k*5}", 4, 1.2, B.ivory)
    if cid == "igua": sp("M138 58l4 -6", 4, 1.6, B.ivory, taper=(1, 0.3))
    if cid == "mamm": sp("M12 4Q28 14 16 22Q10 24 14 18", 1, 2.8, B.ivory, sk=True, taper=(1, 0.45))
    if cid == "smil": sp("M9 5L9.5 15", 1, 1.6, B.ivory, sk=True, taper=(1, 0.15))
    if cid == "inos": sp("M9 5L9.5 13", 1, 1.4, B.ivory, sk=True, taper=(1, 0.15))
    if cid == "deino":
        for y in (-0.1, 0.1): B.part(1, B.path_svg, "M6 8Q9 18 2 24", 2.6, y, B.ivory, xf, (1, 0.35))
    if cid == "thyla": sp("M9 5Q11 12 9.5 18", 1, 1.6, B.ivory, sk=True, taper=(1, 0.15))
    if cid == "dunkl":
        for d in ["M2 6L14 10", "M0 -6Q10 -12 18 -6"]: sp(d, 1, 2.2, sk=True, taper=(1, .6))
    if cid == "andr": sp("M11 5L11 9", 1, 1.2, B.ivory, sk=True, taper=(1, 0.2))
    if cid == "nash":
        sp("M14 -2Q16 -14 22 -20", 1, 3.2, B.ivory, sk=True, taper=(1, 0.1))
        sp("M5 -8L8 -14", 1, 2.2, B.ivory, sk=True, taper=(1, 0.2))
    if cid == "megl":
        for d in ["M-4 -9L-10 -26", "M-8 -18L-20 -22", "M-9 -23L-4 -32", "M-4 -9L4 -24", "M2 -18L12 -22"]:
            for y in (-0.12, 0.12):
                B.part(1, B.path_svg, d, 1.8, y, B.bone, xf, None)
    if cid == "trex":
        X, Z = W(*xf(4, -1))
    if cid == "basi":
        for y in (-0.1, 0.1):
            B.part(4, B.tube_svg, [(40, 58), (44, 64)], 1.2, y)


def setup_render(B, cid, path):
    sc = bpy.context.scene
    cam = camera((-2.2, -14, 4.6), (0.15, 0, 2.05), ortho=10.2)
    shadow_catcher(60, 0)
    area((-5, -7, 9), (0, 0, 1.5), power=900, size=7, color=(1.0, 0.95, 0.88))
    area((6, 6, 6), (0, 0, 2), power=700, size=4, color=(1.0, 0.78, 0.55))  # warm rim
    area((-6, 4, 3), (0, 0, 2), power=250, size=4, color=(0.7, 0.8, 1.0))   # cool fill from back-left
    world_color((0.55, 0.45, 0.38), 0.35)
    render(path + ".png")
    # --- mask pass ---
    cols = {1: (1, 0, 0), 2: (0, 1, 0), 3: (1, 1, 0), 4: (0, 0, 1), 5: (1, 0, 1), 6: (0, 1, 1)}
    mats = {}
    for i, c in cols.items():
        m = bpy.data.materials.new(f"mask{i}")
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.remove(nt.nodes["Principled BSDF"])
        e = nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = (*c, 1); e.inputs[1].default_value = 1
        nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs[0])
        mats[i] = m
    for ob in sc.objects:
        if ob.type in ('MESH', 'CURVE'):
            if ob.is_shadow_catcher:
                ob.hide_render = True
                continue
            idx = B.parts.get(ob.name, 0)
            if idx and ob.data and hasattr(ob.data, "materials"):
                ob.data.materials.clear()
                ob.data.materials.append(mats[idx])
    for ob in list(sc.objects):
        if ob.type == 'LIGHT':
            ob.hide_render = True
    world_color((0, 0, 0), 0)
    sc.cycles.samples = 1
    sc.cycles.use_adaptive_sampling = False
    sc.cycles.use_denoising = False
    sc.cycles.filter_width = 0.01
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    render(path + "_mask.png")


if __name__ == "__main__":
    ids = sys.argv[-1].split(",")
    for cid, plan, skt, ss in CRE:
        if ids != ["all"] and cid not in ids:
            continue
        t = time.time()
        sc = reset(samples=28, w=RW, h=RH)
        B = build(cid, plan, skt, ss)
        setup_render(B, cid, OUT + "sk_" + cid)
        print("DONE", cid, round(time.time() - t, 1), flush=True)
