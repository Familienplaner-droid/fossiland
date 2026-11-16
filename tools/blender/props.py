import sys, math, random, time
sys.path.insert(0, "/home/claude/fossil3d")
import bpy
from mathutils import Vector
from lib import *

PXU = 128
which = sys.argv[-1]


def bone_mat(name="bone", tone=1.0):
    c = tuple(x * tone for x in hexc("#efe0bd"))
    return mat_basic(name, c, rough=0.55, noise=(tuple(x * tone for x in hexc("#d8bf8e")), 3.5, 6),
                     bump=0.25, bump_scale=18, ao=0.25)


def setup_top(wu, hu, samples=48):
    sc = reset(samples=samples, w=int(wu * PXU), h=int(hu * PXU))
    camera((0, 0, 30), (0, 0, 0), ortho=max(wu, hu))
    shadow_catcher(40, 0)
    sun(rot=(math.radians(18), math.radians(-10), math.radians(-25)), strength=2.6, angle=28)
    world_color((0.8, 0.76, 0.7), 1.3)
    return sc


def knobs(p, d, r, m, z):
    """two spheres at a bone end, perpendicular to direction d"""
    n = Vector((-d[1], d[0], 0)).normalized()
    for s in (-1, 1):
        sphere((p[0] + n.x * r * 0.75 * s, p[1] + n.y * r * 0.75 * s, z), r, m, scale=(1, 1, 0.8), seg=20)


def long_bone(a, b, r, m, z=0.16, knob=1.5, bend=0.0):
    a, b = Vector((*a, z)), Vector((*b, z))
    d = (b - a).normalized()
    mid = (a + b) / 2 + Vector((-d.y, d.x, 0)) * bend
    pts = smooth_path([tuple(a), tuple(mid), tuple(b)], 16)
    radii = [1.0 - 0.25 * math.sin(i / (len(pts) - 1) * math.pi) for i in range(len(pts))]
    tube(pts, r, m, radii=radii)
    knobs(a, d, r * knob, m, z)
    knobs(b, d, r * knob, m, z)


def skull_sprite():
    setup_top(2, 2)
    m = bone_mat()
    s = 1.75 / 30.0
    # profile outline sampled from the 2D skull path (quadratic segments)
    path = [((-12, -2), (-9, -11), (3, -9)), ((3, -9), (14, -7), (18, 0)), ((18, 0), (16, 4), (6, 5))]
    pts = []
    for p0, c, p1 in path:
        for k in range(10):
            t = k / 10
            x = (1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * c[0] + t * t * p1[0]
            y = (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * c[1] + t * t * p1[1]
            pts.append((x, y))
    pts += [(6, 5), (-8, 5), (-11.5, 3.5)]
    off = (-3, 0.5)
    outline = [((x + off[0]) * s, -(y + off[1]) * s + 0.25) for x, y in pts]
    sk = slab(outline, 0.5, 0.12, m, name="skull", loc=(0, 0, 0.25), rot=(0, 0, 0))
    bpy.context.view_layer.objects.active = sk
    sk.select_set(True)
    bpy.ops.object.convert(target='MESH')
    for (hx, hy, hr, sx) in [(-3 + off[0], -3 + off[1], 2.6, 1.0), (6 + off[0], -2 + off[1], 2.2, 1.5), (14.5 + off[0], -1 + off[1], 0.9, 1.0)]:
        cut = cyl((hx * s, -hy * s + 0.25, 0.25), hr * s, 2, None)
        cut.scale = (sx, 1, 1)
        bo = sk.modifiers.new("b", 'BOOLEAN')
        bo.object = cut
        bo.operation = 'DIFFERENCE'
        cut.hide_render = True
    smooth(sk)
    # lower jaw
    jaw = [(-10, 6.2), (14, 5.6), (13.5, 7.6), (-8, 9)]
    slab([((x + off[0]) * s, -(y + off[1]) * s + 0.25) for x, y in jaw], 0.3, 0.08, m, name="jaw", loc=(0, 0, 0.16), rot=(0, 0, 0))
    tm = mat_basic("tooth", hexc("#fbf6ea"), rough=0.3, ao=0.1)
    for i in range(7):
        x = (-3 + i * 2.6 + off[0]) * s
        y = -(5.6 + off[1]) * s + 0.25
        cone((x, y - 0.06, 0.28), 0.05, 0.0, 0.18, tm, rot=(math.pi / 2, 0, 0), verts=12)


def vert_sprite():
    setup_top(4, 1)
    m = bone_mat()
    for i in range(4):
        x = -1.5 + i
        cyl((x, -0.05, 0.2), 0.15, 0.5, m, rot=(0, math.pi / 2, 0))
        for e in (-1, 1):
            sphere((x + e * 0.22, -0.05, 0.2), 0.21, m, scale=(0.42, 1, 0.95))
        # spinous process (towards image top)
        tube(smooth_path([(x, 0.1, 0.22), (x + 0.05, 0.3, 0.2), (x + 0.12, 0.44, 0.18)], 8), 0.07, m, radii=[1, 0.8, 0.6, .5, .45, .4, .4, .35, .3])
        # transverse processes
        for sgn in (-1, 1):
            tube([(x, -0.1, 0.2), (x + sgn * 0.2, -0.36, 0.16)], 0.05, m)
        # disc between vertebrae
        if i < 3:
            cyl((x + 0.5, -0.05, 0.18), 0.17, 0.12, bone_mat("disc", 0.8), rot=(0, math.pi / 2, 0))


def rib_sprite():
    setup_top(1, 3)
    m = bone_mat()
    for k, (dx, sc) in enumerate([(0.0, 1.0), (-0.22, 0.82)]):
        pts = smooth_path([(-0.18 + dx, 1.3 * sc, 0.14), (0.22 + dx, 0.5 * sc, 0.14), (0.25 + dx, -0.4 * sc, 0.14), (-0.05 + dx, -1.32 * sc, 0.14)], 30)
        n = len(pts)
        tube(pts, 0.085 * sc, m, radii=[1.0 - 0.5 * i / (n - 1) for i in range(n)])
        sphere((pts[0][0] - 0.04, pts[0][1] + 0.04, 0.14), 0.11 * sc, m, scale=(1, 1, .8))


def leg_sprite():
    setup_top(2, 3)
    m = bone_mat()
    long_bone((-0.5, 1.15), (-0.45, -0.75), 0.17, m, z=0.2, knob=1.25, bend=0.08)
    long_bone((-0.35, -1.1), (0.7, -1.2), 0.11, m, z=0.15, knob=1.2)
    # little fibula
    tube(smooth_path([(-0.2, 0.9, 0.12), (-0.18, -0.6, 0.12)], 6), 0.05, m)


def foot_sprite():
    setup_top(2, 2)
    m = bone_mat()
    cm = mat_basic("claw", hexc("#5a4632"), rough=0.35, ao=0.1)
    for k, dy in enumerate((-0.16, 0, 0.16)):
        long_bone((-0.8, 0.5 + dy), (0.35, 0.52 + dy * 0.6), 0.075, m, z=0.12, knob=1.3)
    toes = [(0.28, -0.78), (0.55, -0.85), (0.85, -0.68)]
    for i, (tx, ty) in enumerate(toes):
        pts = smooth_path([(0.42 + (i - 1) * 0.1, 0.4, 0.12), (tx - 0.02, (0.4 + ty) / 2, 0.12), (tx, ty, 0.12)], 12)
        tube(pts, 0.07, m, radii=[1 - 0.3 * j / 11 for j in range(12)])
        for j in (4, 8):
            sphere(pts[j], 0.075, m, scale=(1, 1, .8), seg=14)
        d = Vector(pts[-1]) - Vector(pts[-3])
        ang = math.atan2(d.y, d.x) - math.pi / 2
        cone((tx + d.normalized().x * 0.08, ty + d.normalized().y * 0.08, 0.12), 0.06, 0.0, 0.2, cm, rot=(0, 0, ang), verts=12).rotation_euler = (math.pi / 2, 0, ang + math.pi)


def amber():
    setup_top(1, 1, samples=96)
    m = mat_basic("amber", hexc("#f0901e"), rough=0.08, transmission=0.55, ior=1.54, coat=1.0,
                  emission=hexc("#ff9a2a"), emis_strength=0.6, noise=(hexc("#b85a0a"), 2.5, 3))
    b = sphere((0, 0, 0.2), 0.36, m, scale=(0.82, 1.0, 0.6), seg=40)
    tex = bpy.data.textures.new("am", 'CLOUDS'); tex.noise_scale = 0.4
    sd = b.modifiers.new("d", 'DISPLACE'); sd.texture = tex; sd.strength = 0.06
    im = mat_basic("ins", hexc("#2a1606"), rough=0.6)
    sphere((0.05, 0.02, 0.22), 0.06, im, scale=(1.6, 0.8, 0.6), seg=12)
    sphere((-0.06, 0.04, 0.22), 0.045, im, seg=12)
    for s in (-1, 1):
        tube([(0.02, 0.02, 0.22), (0.12, 0.02 + s * 0.12, 0.22)], 0.012, im)


def ammonite():
    setup_top(1, 1)
    m = mat_basic("ammo", hexc("#d9c7a6"), rough=0.45, noise=(hexc("#a88a63"), 5, 6), bump=0.2, bump_scale=25, ao=0.2, coat=0.3)
    pts, radii = [], []
    turns = 3.2
    n = 120
    for i in range(n):
        a = i / (n - 1) * turns * 2 * math.pi
        r = 0.03 * math.exp(0.13 * a)
        pts.append((r * math.cos(a), r * math.sin(a), 0.14))
        radii.append(0.4 + r * 3.6)
    tube(pts, 0.05, m, radii=radii, res=6)
    for i in range(30, n, 3):
        a = i / (n - 1) * turns * 2 * math.pi
        r = 0.03 * math.exp(0.13 * a)
        w = 0.05 * radii[i]
        p = Vector((r * math.cos(a), r * math.sin(a), 0.14))
        d = Vector((math.cos(a), math.sin(a), 0))
        tube([tuple(p - d * w * 1.1 + Vector((0, 0, 0.02))), tuple(p + d * w * 1.1 + Vector((0, 0, 0.02)))], 0.012 + w * 0.12, m)


def tooth():
    setup_top(1, 1)
    em = mat_basic("enamel", hexc("#3d4652"), rough=0.18, coat=1.0, noise=(hexc("#6b7685"), 6, 4))
    rm = mat_basic("root", hexc("#8a6a4a"), rough=0.7, noise=(hexc("#5e442e"), 8, 6), bump=0.3, bump_scale=30)
    slab([(-0.28, 0.2), (0.28, 0.2), (0.02, -0.4), (-0.02, -0.4)], 0.14, 0.05, em, loc=(0, 0, 0.08), rot=(0, 0, 0))
    slab([(-0.36, 0.32), (0.36, 0.32), (0.3, 0.16), (-0.3, 0.16)], 0.16, 0.05, rm, loc=(0, 0, 0.08), rot=(0, 0, 0))


def trilobite():
    setup_top(1, 1)
    m = mat_basic("tri", hexc("#8c8076"), rough=0.5, noise=(hexc("#5a5048"), 6, 6), bump=0.3, bump_scale=30, ao=0.15)
    sphere((0, 0.24, 0.07), 0.3, m, scale=(1, 0.5, 0.35))  # head shield
    for i in range(8):
        y = 0.1 - i * 0.065
        w = 0.27 - i * 0.02
        cyl((0, y, 0.07), 0.04, w * 2, m, rot=(0, math.pi / 2, 0), verts=16).scale = (1, 1.0, 1)
    sphere((0, -0.4, 0.06), 0.12, m, scale=(1, 0.55, 0.4))  # tail
    tube(smooth_path([(0, 0.35, 0.13), (0, 0, 0.13), (0, -0.4, 0.11)], 10), 0.06, m, radii=[1, .9, .85, .8, .75, .7, .65, .6, .5, .4])
    em = mat_basic("eye", hexc("#3a322c"), rough=0.2)
    for s in (-1, 1):
        sphere((s * 0.13, 0.27, 0.13), 0.04, em, seg=12)


TOOLCAM = []


def tool_scene(samples=64):
    sc = reset(samples=samples, w=192, h=192)
    TOOLCAM[:] = [camera((2.6, -3.4, 3.2), (0, 0, 0.35), ortho=3)]
    sun(rot=(math.radians(40), math.radians(10), math.radians(-40)), strength=3.6, angle=10)
    area((-3, 2, 3), (0, 0, 0.3), power=180, size=3, color=(1.0, 0.8, 0.7))
    world_color((0.8, 0.75, 0.7), 0.8)
    return sc


def brush():
    tool_scene()
    wood = mat_basic("wood", hexc("#a0683d"), rough=0.4, noise=(hexc("#7a4a28"), 3, 8), coat=0.5)
    met = mat_basic("met", hexc("#c9ccd1"), rough=0.25, metal=1.0)
    hair = mat_basic("hair", hexc("#f2d48a"), rough=0.7, noise=(hexc("#c9a25a"), 30, 2), ao=0.1)
    root = bpy.data.objects.new("root", None)
    link(root)
    b = cyl((0, 0, 0.1), 0.24, 0.42, hair)
    b.scale = (1.15, 0.6, 1)
    for o in [cyl((0, 0, 1.15), 0.13, 1.3, wood, bevel=0.03), sphere((0, 0, 1.82), 0.14, wood),
              cyl((0, 0, 0.42), 0.2, 0.28, met, bevel=0.03), b]:
        o.parent = root
    root.rotation_euler = (0, math.radians(-30), math.radians(15))


def pick():
    tool_scene()
    wood = mat_basic("wood", hexc("#8a5530"), rough=0.4, noise=(hexc("#6a3e20"), 3, 8), coat=0.5)
    met = mat_basic("met", hexc("#9aa3ad"), rough=0.3, metal=1.0)
    root = bpy.data.objects.new("root", None)
    link(root)
    h = cyl((0, 0, 0), 0.08, 2.0, wood, bevel=0.02)
    h.parent = root
    head = tube(smooth_path([(-0.85, 0, 0.75), (0, 0, 1.02), (0.85, 0, 0.72)], 24), 0.11, met,
                radii=[0.25 + 0.75 * math.sin(i / 23 * math.pi) for i in range(24)])
    head.parent = root
    cyl((0, 0, 0.92), 0.13, 0.32, met, rot=(math.pi / 2, 0, 0), bevel=0.02).parent = root
    root.rotation_euler = (math.radians(15), math.radians(-35), math.radians(20))
    root.location = (0, 0, 0.2)


def probe():
    tool_scene()
    met = mat_basic("met", hexc("#c9ccd1"), rough=0.22, metal=1.0)
    pink = mat_basic("pink", hexc("#ff5a8a"), rough=0.3, coat=0.8)
    amb = mat_basic("lamp", hexc("#ffb53d"), rough=0.2, emission=hexc("#ffb53d"), emis_strength=4)
    root = bpy.data.objects.new("root", None)
    link(root)
    for o in [cyl((0, 0, 0), 0.05, 1.8, met), cone((0, 0, -1.0), 0.05, 0.0, 0.2, met, rot=(math.pi, 0, 0)),
              rcube((0, 0, 1.05), (0.42, 0.26, 0.5), pink, bevel=0.08), sphere((0, -0.14, 1.12), 0.07, amb),
              tube(smooth_path([(-0.25, 0, 0.9), (-0.32, 0, 1.05), (-0.25, 0, 1.2)], 8), 0.035, met)]:
        o.parent = root
    root.rotation_euler = (math.radians(10), math.radians(-25), math.radians(10))
    root.location = (0, 0, 0.6)


def canteen():
    tool_scene()
    green = mat_basic("green", hexc("#5e8a52"), rough=0.5, noise=(hexc("#4a7040"), 4, 6), bump=0.1, bump_scale=40, coat=0.3)
    met = mat_basic("met", hexc("#8a9099"), rough=0.3, metal=1.0)
    strap = mat_basic("strap", hexc("#7a5636"), rough=0.7)
    root = bpy.data.objects.new("root", None)
    link(root)
    b = cyl((0, 0, 0), 0.7, 0.42, green, rot=(math.pi / 2, 0, 0), bevel=0.15, verts=48)
    b.parent = root
    cyl((0, 0, 0), 0.71, 0.08, met, rot=(math.pi / 2, 0, 0), verts=48).parent = root
    cyl((0, 0, 0.78), 0.12, 0.2, met, bevel=0.03).parent = root
    cyl((0, 0, 0.92), 0.15, 0.1, met, bevel=0.03).parent = root
    t = tube(smooth_path([(-0.72, 0, 0.3), (-0.8, 0, 0.9), (0, 0, 1.25), (0.8, 0, 0.9), (0.72, 0, 0.3)], 24), 0.05, strap)
    t.scale = (1, 1, 1)
    t.parent = root
    root.rotation_euler = (0, 0, math.radians(-25))
    root.location = (0, 0, 0.75)


def coin():
    sc = reset(samples=64, w=96, h=96)
    camera((0, -0.01, 6), (0, 0, 0), ortho=1.25)
    sun(rot=(math.radians(35), math.radians(-15), math.radians(-25)), strength=3.5, angle=12)
    area((-2, 2, 2), (0, 0, 0), power=100, size=2)
    world_color((0.9, 0.8, 0.6), 1.0)
    gold = mat_basic("gold", hexc("#ffb53d"), rough=0.22, metal=1.0, noise=(hexc("#e8a030"), 5, 3))
    cyl((0, 0, 0), 0.55, 0.12, gold, bevel=0.035, verts=64)
    rim = tube([(0.47 * math.cos(a / 40 * 6.283), 0.47 * math.sin(a / 40 * 6.283), 0.065) for a in range(41)], 0.025, gold)
    # embossed bone
    bm = mat_basic("goldb", hexc("#ffd27a"), rough=0.2, metal=1.0)
    tube([(-0.22, -0.22, 0.07), (0.22, 0.22, 0.07)], 0.06, bm)
    for (x, y) in [(-0.22, -0.22), (0.22, 0.22)]:
        d = Vector((1, 1, 0)).normalized()
        n = Vector((-d.y, d.x, 0))
        for s in (-1, 1):
            sphere((x + n.x * 0.06 * s, y + n.y * 0.06 * s, 0.07), 0.075, bm, scale=(1, 1, .5), seg=16)


def radar():
    """Bodenradar: Handgerät mit Bildschirm, Antennenplatte und Griff."""
    tool_scene()
    body = mat_basic("body", hexc("#ffb53d"), rough=0.35, coat=0.7)
    dark = mat_basic("dark", hexc("#3a2a20"), rough=0.5)
    scr = mat_basic("scr", hexc("#2fd38a"), rough=0.2, emission=hexc("#2fd38a"), emis_strength=2.5)
    met = mat_basic("met", hexc("#c9ccd1"), rough=0.25, metal=1.0)
    pink = mat_basic("pink", hexc("#ff5a8a"), rough=0.3, coat=0.8)
    root = bpy.data.objects.new("root", None)
    link(root)
    parts = [rcube((0, 0, 1.0), (0.9, 0.34, 0.62), body, bevel=0.1),
             rcube((0, -0.18, 1.04), (0.66, 0.04, 0.42), scr, bevel=0.03),
             cyl((0, 0, 0.45), 0.08, 0.7, dark, bevel=0.02),
             cyl((0, 0, 0.0), 0.5, 0.08, met, bevel=0.03, verts=48),
             sphere((0.3, -0.2, 1.36), 0.06, pink),
             cyl((-0.32, 0, 1.45), 0.025, 0.4, met)]
    # Wellen auf dem Bildschirm
    for i, r in enumerate((0.08, 0.16, 0.24)):
        t = tube(smooth_path([(-r, -0.21, 1.0), (0, -0.21, 1.0 + r * .7), (r, -0.21, 1.0)], 10), 0.012, dark)
        parts.append(t)
    for o in parts:
        o.parent = root
    root.rotation_euler = (math.radians(8), math.radians(-12), math.radians(18))
    root.location = (0, 0, 0.4)


def jackhammer():
    """Presslufthammer: Körper, T-Griff und Meißelspitze."""
    tool_scene()
    body = mat_basic("body", hexc("#ff5a8a"), rough=0.35, coat=0.8)
    met = mat_basic("met", hexc("#c9ccd1"), rough=0.22, metal=1.0)
    dark = mat_basic("dark", hexc("#3a2a20"), rough=0.55)
    root = bpy.data.objects.new("root", None)
    link(root)
    parts = [cyl((0, 0, 1.0), 0.26, 0.9, body, bevel=0.05, verts=40),
             cyl((0, 0, 1.5), 0.2, 0.14, dark, bevel=0.03),
             cyl((0, 0, 1.68), 0.07, 0.3, met),
             cyl((0, 0, 1.82), 0.07, 1.0, dark, rot=(0, math.pi / 2, 0), bevel=0.03),
             cyl((0, 0, 0.5), 0.12, 0.16, met, bevel=0.02),
             cyl((0, 0, 0.22), 0.06, 0.45, met),
             cone((0, 0, -0.05), 0.06, 0.0, 0.14, met, rot=(math.pi, 0, 0))]
    for z in (0.8, 1.0, 1.2):
        parts.append(cyl((0, 0, z), 0.27, 0.04, dark, verts=40))
    for o in parts:
        o.parent = root
    root.rotation_euler = (math.radians(6), math.radians(-18), math.radians(12))
    root.location = (0, 0, 0.2)


JOBS = {"skull": skull_sprite, "vert": vert_sprite, "rib": rib_sprite, "leg": leg_sprite, "foot": foot_sprite,
        "amber": amber, "ammo": ammonite, "tooth": tooth, "trilo": trilobite,
        "t_brush": brush, "t_pick": pick, "t_probe": probe, "t_canteen": canteen, "coin": coin, "t_radar": radar, "t_jack": jackhammer}
names = list(JOBS) if which == "all" else which.split(",")
for n in names:
    t = time.time()
    JOBS[n]()
    if n.startswith("t_"):
        fit_ortho(TOOLCAM[0], 0.06)
    render(OUT + n + ".png")
    print("DONE", n, round(time.time() - t, 1))
