import sys, math, random, time
sys.path.insert(0, "/home/claude/fossil3d")
import bpy
from mathutils import Vector
from lib import *

W, H = 1024, 320
ERA = int(sys.argv[-1])
R = random.Random(ERA * 17 + 3)

CFG = [
    dict(name="perm", zen="#7a3a3a", hor="#f2b58a", fog="#e8a07a", sun=(0.35, 0.16), sunc="#ffe2b8", ground="#b45a3c", hills="#a24a34", far="#c0705a"),
    dict(name="trias", zen="#e0874a", hor="#fde3b0", fog="#f6c890", sun=(0.72, 0.2), sunc="#fff3c9", ground="#d99a5a", hills="#c87a44", far="#e0a070"),
    dict(name="jura", zen="#3f9ccc", hor="#d9f1ea", fog="#bfe2dc", sun=(0.62, 0.32), sunc="#fffbe0", ground="#5f9a48", hills="#4a8a46", far="#8cbfa8"),
    dict(name="kreide", zen="#7a3148", hor="#f7a868", fog="#e88a64", sun=(0.42, 0.06), sunc="#ffd9a0", ground="#6a5a34", hills="#5a4038", far="#8a5a58"),
    dict(name="palaeo", zen="#5bb3c8", hor="#eaf7dc", fog="#cde9d6", sun=(0.55, 0.3), sunc="#fffbe0", ground="#4f9a46", hills="#3a8148", far="#86b8a0"),
    dict(name="eis", zen="#6f9cc4", hor="#eef5f8", fog="#dfeaf2", sun=(-0.35, 0.22), sunc="#ffffff", ground="#eef4f8", hills="#d4e4ec", far="#b8cfdc"),
]
C = CFG[ERA]
sc = reset(samples=64, w=W, h=H, transparent=False)
sc.cycles.diffuse_bounces = 2
CAM = Vector((0, -16, 1.7))
cam = camera(tuple(CAM), (0, 10, 2.4), lens=30)
bpy.context.view_layer.update()
sc.view_settings.view_transform = 'Standard'
try:
    sc.view_settings.look = 'Medium High Contrast'
except Exception:
    pass

# ---------- sky ----------
w = sc.world
nt = w.node_tree
N, L = nt.nodes, nt.links
bg = N["Background"]
tc = N.new("ShaderNodeTexCoord")
sep = N.new("ShaderNodeSeparateXYZ")
L.new(sock(tc, "Generated", out=True), sep.inputs[0])
mr = N.new("ShaderNodeMapRange")
L.new(sep.outputs[2], mr.inputs[0])
mr.inputs[1].default_value = -0.05
mr.inputs[2].default_value = 0.45
ramp = N.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (*hexc(C["hor"]), 1)
ramp.color_ramp.elements[1].color = (*hexc(C["zen"]), 1)
L.new(mr.outputs[0], ramp.inputs[0])
L.new(ramp.outputs[0], bg.inputs[0])
bg.inputs[1].default_value = 0.8


def fog_mat(name, color, rough=0.8, density=0.0075, noise=None, bump=0.0, bump_scale=2.0, emit=None):
    m = mat_basic(name, hexc(color), rough=rough, noise=noise, bump=bump, bump_scale=bump_scale,
                  emission=emit, emis_strength=(3.0 if emit else 0.0))
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    out = N["Material Output"]
    p = N["Principled BSDF"]
    em = N.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*hexc(C["fog"]), 1)
    cd = N.new("ShaderNodeCameraData")
    mth = N.new("ShaderNodeMath"); mth.operation = 'MULTIPLY'; mth.inputs[1].default_value = -density
    L.new(sock(cd, "View Distance", out=True), mth.inputs[0])
    ex = N.new("ShaderNodeMath"); ex.operation = 'EXPONENT'
    L.new(mth.outputs[0], ex.inputs[0])
    inv = N.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    L.new(ex.outputs[0], inv.inputs[1])
    mix = N.new("ShaderNodeMixShader")
    L.new(inv.outputs[0], mix.inputs[0])
    L.new(p.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs[0])
    return m


def terrain(y0, depth, width, amp, nscale, mat, z=0.0, seed=0, flat_near=0.0, subdiv=7):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, y0 + depth / 2, z))
    ob = bpy.context.active_object
    ob.scale = (width, depth, 1)
    bpy.ops.object.transform_apply(scale=True)
    sd = ob.modifiers.new("sd", 'SUBSURF'); sd.subdivision_type = 'SIMPLE'; sd.levels = sd.render_levels = subdiv
    tex = bpy.data.textures.new(f"tx{seed}", 'CLOUDS'); tex.noise_scale = nscale; tex.noise_depth = 3
    dp = ob.modifiers.new("dp", 'DISPLACE'); dp.texture = tex; dp.strength = amp; dp.texture_coords = 'GLOBAL'
    dp.mid_level = 0.35
    smooth(ob)
    assign(ob, mat)
    return ob


def ground_y(y):  # rough helper so props sit on near ground
    return 0.0


# ---------- sun disc ----------
sx, sy = C["sun"]
sdir = (cam.matrix_world.to_3x3() @ Vector((sx * 0.6, (sy * 2.6 - 0.2) * 0.1875, -1))).normalized()
spos = CAM + sdir * 150
sunm = mat_basic("sun", hexc(C["sunc"]), emission=hexc(C["sunc"]), emis_strength=8)
sphere(tuple(spos), 3.0 if ERA != 3 else 5.0, sunm, seg=32)
glow = bpy.data.materials.new("glow")
glow.use_nodes = True
gn = glow.node_tree
gN, gL = gn.nodes, gn.links
gN.remove(gN["Principled BSDF"])
e = gN.new("ShaderNodeEmission"); e.inputs[0].default_value = (*hexc(C["sunc"]), 1); e.inputs[1].default_value = 1.6
tr = gN.new("ShaderNodeBsdfTransparent")
lw = gN.new("ShaderNodeLayerWeight"); lw.inputs[0].default_value = 0.5
pw = gN.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0
iv = gN.new("ShaderNodeMath"); iv.operation = 'SUBTRACT'; iv.inputs[0].default_value = 1.0
gL.new(sock(lw, "Facing", out=True), iv.inputs[1])
gL.new(iv.outputs[0], pw.inputs[0])
mx = gN.new("ShaderNodeMixShader")
gL.new(pw.outputs[0], mx.inputs[0]); gL.new(tr.outputs[0], mx.inputs[1]); gL.new(e.outputs[0], mx.inputs[2])
gL.new(mx.outputs[0], gN["Material Output"].inputs[0])
g = sphere(tuple(spos), 10 if ERA != 3 else 14, glow, seg=32)
g.visible_shadow = False
g.visible_diffuse = False

# sun lamp roughly from the sun direction
sl = sun(strength=3.2 if ERA != 5 else 2.4, angle=4, color=hexc(C["sunc"]))
d = Vector((sdir.x, sdir.y * 0.4 - 0.5, max(0.55, sdir.z)))
sl.rotation_euler = d.normalized().to_track_quat('Z', 'Y').to_euler()
world_strength = 0.75

# ---------- terrain layers ----------
mg = fog_mat("ground", C["ground"], noise=(tuple(c * 0.8 for c in hexc(C["ground"])), 0.6, 4), bump=0.3, bump_scale=3)
mh = fog_mat("hills", C["hills"], noise=(tuple(c * 0.82 for c in hexc(C["hills"])), 0.3, 4))
mf = fog_mat("far", C["far"], density=0.012)
terrain(-20, 34, 90, 0.9, 3.0, mg, z=-0.6, seed=1)
terrain(12, 28, 140, 4.5 if ERA != 1 else 3.0, 7.0, mh, z=-1.2, seed=2)
terrain(38, 40, 220, 14 if ERA in (0, 5) else 9, 14.0, mf, z=-3.0, seed=3)


# ---------- prop builders ----------
def trunk_mat():
    return fog_mat("trunk", "#6b4a32", noise=(hexc("#4a3020"), 6, 4))


def conifer(x, y, s, snow=False):
    tm = trunk_mat()
    lm = fog_mat("needle", R.choice(["#2f6a40", "#3a7444", "#2a5a3a"]) if ERA != 0 else "#4a6a32", noise=(hexc("#1e4a2c"), 3, 3), bump=0.6, bump_scale=12)
    snm = fog_mat("snow", "#ffffff", rough=0.6)
    cyl((x, y, s * 0.5), 0.12 * s, s, tm)
    for k in range(5):
        zz = s * (0.7 + k * 0.48)
        r = s * (0.95 - k * 0.17)
        c = cone((x, y, zz), r, r * 0.12, s * 0.85, lm, verts=14)
        c.rotation_euler = (R.uniform(-.06, .06), R.uniform(-.06, .06), R.random() * 3)
        tx = bpy.data.textures.new("cn", 'CLOUDS'); tx.noise_scale = 0.25
        sdv = c.modifiers.new("sd", 'SUBSURF'); sdv.levels = sdv.render_levels = 2; sdv.subdivision_type = 'SIMPLE'
        dpp = c.modifiers.new("dp", 'DISPLACE'); dpp.texture = tx; dpp.strength = 0.18 * s
        if snow:
            cone((x, y, zz + s * 0.18), r * 0.62, 0, s * 0.55, snm, verts=10)


def cycad(x, y, s):
    tm = fog_mat("cyt", "#7a5638", noise=(hexc("#5a3a22"), 8, 4), bump=0.6, bump_scale=20)
    lm = fog_mat("cyl", "#5f8a3a", noise=(hexc("#40682a"), 4, 3))
    cyl((x, y, s * 0.45), 0.22 * s, s * 0.9, tm)
    for k in range(9):
        a = k / 9 * math.tau + R.random() * 0.3
        tip = (x + math.cos(a) * s * 1.3, y + math.sin(a) * s * 1.3, s * 0.7)
        tube(smooth_path([(x, y, s * 0.95), (x + math.cos(a) * s * 0.7, y + math.sin(a) * s * 0.7, s * 1.35), tip], 10), 0.11 * s, lm,
             radii=[0.5, 1, 1, 1, 0.9, 0.8, 0.6, 0.4, 0.2, 0.1]).data.bevel_resolution = 1
        ob = bpy.context.scene.objects[-1] if False else None


def palm(x, y, s):
    tm = fog_mat("pt", "#8a6a48", noise=(hexc("#5e442e"), 10, 4), bump=0.8, bump_scale=30)
    lm = fog_mat("pl", "#4f7a34", noise=(hexc("#3a5a24"), 4, 3))
    lean = R.uniform(-0.6, 0.6)
    top = (x + lean * s, y, s * 3)
    tube(smooth_path([(x, y, 0), (x + lean * s * 0.2, y, s * 1.5), top], 12), 0.16 * s, tm, radii=[1.2, 1.1, 1, .95, .9, .85, .8, .78, .75, .72, .7, .7])
    for k in range(8):
        a = k / 8 * math.tau
        tube(smooth_path([top, (top[0] + math.cos(a) * s * 0.9, top[1] + math.sin(a) * s * 0.9, top[2] + s * 0.35),
                          (top[0] + math.cos(a) * s * 1.7, top[1] + math.sin(a) * s * 1.7, top[2] - s * 0.4)], 12),
             0.16 * s, lm, radii=[0.3, 0.8, 1, 1, .95, .85, .7, .6, .45, .3, .2, .1])


def leafy(x, y, s):
    tm = trunk_mat()
    lm = fog_mat("lf", R.choice(["#3f8a44", "#4f9a4a", "#5aa050"]), noise=(hexc("#2f6a36"), 2, 4), bump=0.5, bump_scale=6)
    cyl((x, y, s * 0.6), 0.14 * s, s * 1.2, tm)
    for k in range(5):
        sphere((x + R.uniform(-0.5, 0.5) * s, y + R.uniform(-0.4, 0.4) * s, s * (1.5 + R.uniform(0, 0.7))), s * R.uniform(0.55, 0.8), lm, seg=16)


def rock(x, y, s, col):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=s, location=(x, y, s * 0.2))
    ob = bpy.context.active_object
    ob.scale = (1.3, 1, 0.7)
    ob.rotation_euler = (R.random(), R.random(), R.random() * 3)
    assign(ob, fog_mat("rock", col, noise=(tuple(c * 0.7 for c in hexc(col)), 2, 6), bump=0.5, bump_scale=4))


def mesa(x, y, r, h, col):
    m = fog_mat("mesa", col, noise=(tuple(c * 0.75 for c in hexc(col)), 0.8, 2))
    ob = cyl((x, y, h / 2 - 1), r, h, m, verts=40)
    tex = bpy.data.textures.new("ms", 'CLOUDS'); tex.noise_scale = 1.2
    sd = ob.modifiers.new("sd", 'SUBSURF'); sd.levels = sd.render_levels = 3; sd.subdivision_type = 'SIMPLE'
    dp = ob.modifiers.new("dp", 'DISPLACE'); dp.texture = tex; dp.strength = r * 0.25
    cone((x, y, -0.5), r * 1.6, r * 0.9, 2.0, m, verts=40)


def sauropod(x, y, s, col="#3f6a48"):
    m = fog_mat("sau", col, noise=(tuple(c * 0.8 for c in hexc(col)), 3, 3))
    sphere((x, y, s * 1.6), s * 1.0, m, scale=(1.7, 0.75, 0.75))
    tube(smooth_path([(x + s * 1.3, y, s * 1.8), (x + s * 2.2, y, s * 2.8), (x + s * 2.6, y, s * 4.2)], 14), s * 0.32, m, radii=[1.2, 1, .9, .8, .75, .7, .65, .6, .55, .5, .5, .5, .5, .5])
    sphere((x + s * 2.75, y, s * 4.25), s * 0.3, m, scale=(1.6, 0.8, 0.8))
    tube(smooth_path([(x - s * 1.4, y, s * 1.7), (x - s * 2.6, y, s * 1.3), (x - s * 4.0, y, s * 0.6)], 14), s * 0.36, m, radii=[1, .9, .8, .7, .6, .5, .4, .35, .3, .25, .2, .15, .1, .08])
    for dx in (-0.8, -0.4, 0.5, 0.9):
        for dy in (-0.25, 0.25):
            cyl((x + dx * s, y + dy * s, s * 0.6), s * 0.2, s * 1.3, m, verts=12)


def mammoth(x, y, s, col="#6a5040"):
    m = fog_mat("mam", col, noise=(tuple(c * 0.75 for c in hexc(col)), 4, 6), bump=0.8, bump_scale=18)
    iv = fog_mat("tusk", "#f2ead8", rough=0.4)
    sphere((x, y, s * 1.55), s * 1.0, m, scale=(1.35, 0.85, 0.95))
    sphere((x + s * 0.4, y, s * 2.35), s * 0.55, m)  # hump
    sphere((x + s * 1.25, y, s * 2.0), s * 0.62, m, scale=(1, 0.85, 1.1))
    tube(smooth_path([(x + s * 1.6, y, s * 1.9), (x + s * 1.9, y, s * 1.1), (x + s * 1.75, y, s * 0.45)], 10), s * 0.17, m, radii=[1.3, 1.2, 1.1, 1, .9, .8, .7, .7, .6, .6])
    for dy in (-0.22, 0.22):
        tube(smooth_path([(x + s * 1.55, y + dy * s, s * 1.65), (x + s * 2.3, y + dy * s * 1.3, s * 1.0), (x + s * 2.4, y + dy * s * 1.6, s * 1.75)], 12), s * 0.08, iv, radii=[1.2, 1.1, 1, 1, .9, .8, .7, .6, .5, .4, .3, .2])
    for dx in (-0.6, 0.7):
        for dy in (-0.3, 0.3):
            cyl((x + dx * s, y + dy * s, s * 0.55), s * 0.24, s * 1.1, m, verts=12)


def ptero(x, y, z, s):
    m = fog_mat("pt", "#3a2a30")
    sphere((x, y, z), s * 0.25, m, scale=(1.6, 0.6, 0.5))
    for sg in (-1, 1):
        tube([(x, y, z), (x + s * 0.3, y + sg * s * 0.9, z + s * 0.35), (x - s * 0.1, y + sg * s * 1.8, z + s * 0.1)], s * 0.08, m)
        slab([(0, 0), (s * 0.3, sg * s * 0.9), (-s * 0.1, sg * s * 1.8), (-s * 0.35, sg * s * 0.4)], 0.02, 0.005, m, loc=(x, y, z + 0.02), rot=(0, 0, 0))
    sphere((x + s * 0.5, y, z + s * 0.05), s * 0.12, m, scale=(2.5, 0.6, 0.6))


def dune_ripples():
    pass


def snow_flakes(n):
    sm = mat_basic("flake", (1, 1, 1), emission=(1, 1, 1), emis_strength=1.5)
    for i in range(n):
        d = R.uniform(2, 14)
        x = R.uniform(-1, 1) * d * 1.2
        sphere((x, CAM.y + d, R.uniform(0.2, 1.0) * d * 0.35 + 0.5), R.uniform(0.012, 0.03) * (1 + d * 0.08), sm, seg=8)


def scatter(fn, n, yr, xr, *a, **k):
    for i in range(n):
        y = R.uniform(*yr)
        x = R.uniform(-xr, xr) * (1 + (y + 16) / 30)
        fn(x, y, *a, **k)


# ---------- per-era composition ----------
if ERA == 0:  # Perm: red desert with mesas and sparse conifers
    for (x, y, r, h) in [(-22, 30, 6, 9), (-8, 40, 4, 11), (14, 34, 7, 8), (30, 45, 5, 12), (2, 55, 9, 10)]:
        mesa(x, y, r, h, "#b0583c")
    scatter(lambda x, y: conifer(x, y, R.uniform(0.6, 1.0)), 9, (2, 14), 12)
    scatter(lambda x, y: rock(x, y, R.uniform(0.2, 0.6), "#8a4a34"), 18, (-8, 10), 9)
elif ERA == 1:  # Trias: dunes with cycads
    scatter(lambda x, y: cycad(x, y, R.uniform(0.8, 1.3)), 10, (-4, 14), 10)
    scatter(lambda x, y: conifer(x, y, R.uniform(0.7, 1.0)), 4, (10, 20), 14)
    scatter(lambda x, y: rock(x, y, R.uniform(0.15, 0.4), "#b0784a"), 14, (-9, 8), 8)
elif ERA == 2:  # Jura: lush forest, sauropods
    scatter(lambda x, y: conifer(x, y, R.uniform(1.0, 1.8)), 22, (4, 26), 14)
    scatter(lambda x, y: cycad(x, y, R.uniform(0.6, 0.9)), 6, (-5, 6), 8)
    sauropod(6, 22, 1.2)
    sauropod(12, 30, 1.0, "#4a7050")
    sauropod(-14, 34, 0.9, "#4a7050")
elif ERA == 3:  # Kreide: volcano at sunset, palms, pterosaurs
    vm = fog_mat("volc", "#4a2a2a", noise=(hexc("#2a1818"), 1.5, 6), bump=0.5, bump_scale=2)
    v = cone((-14, 52, 6), 22, 3.0, 18, vm, verts=64)
    tex = bpy.data.textures.new("vv", 'CLOUDS'); tex.noise_scale = 3
    sd = v.modifiers.new("sd", 'SUBSURF'); sd.levels = sd.render_levels = 3; sd.subdivision_type = 'SIMPLE'
    dp = v.modifiers.new("dp", 'DISPLACE'); dp.texture = tex; dp.strength = 1.5
    lava = mat_basic("lava", hexc("#ff7a2a"), emission=hexc("#ff6a1a"), emis_strength=12)
    cyl((-14, 52, 15.05), 2.9, 0.2, lava)
    for k in range(5):
        tube(smooth_path([(-14 + R.uniform(-1, 1), 50, 14.8), (-14 + R.uniform(-3, 3), 49, 9), (-14 + R.uniform(-5, 5), 47, 3)], 10), 0.25, lava, radii=[1, 1, .9, .8, .7, .6, .5, .4, .3, .2])
    smk = fog_mat("smoke", "#5a4a4a", rough=1)
    for k in range(9):
        sphere((-14 + k * 1.6 + R.uniform(-1, 1), 52 + k * 0.5, 17 + k * 1.6), 2.2 + k * 0.5, smk, seg=16)
    scatter(lambda x, y: palm(x, y, R.uniform(0.7, 1.1)), 9, (-2, 14), 12)
    for k in range(3):
        ptero(R.uniform(2, 14), R.uniform(10, 25), R.uniform(6, 10), 1.0)
elif ERA == 4:  # Paläogen: lake and leafy trees (Messel)
    wm = mat_basic("water", hexc("#3a8a9a"), rough=0.05, coat=0.0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(6, 18, -0.15))
    lk = bpy.context.active_object; lk.scale = (34, 12, 1); assign(lk, wm)
    scatter(lambda x, y: leafy(x, y, R.uniform(0.9, 1.6)), 16, (4, 28), 14)
    scatter(lambda x, y: leafy(x, y, R.uniform(0.6, 0.9)), 4, (-6, 2), 10)
    scatter(lambda x, y: rock(x, y, R.uniform(0.2, 0.5), "#7a6a5a"), 10, (-9, 6), 8)
else:  # Eiszeit: snow, spruce, mammoths, glaciers
    ice = fog_mat("ice", "#cfe2ee", rough=0.2, noise=(hexc("#ffffff"), 0.5, 3))
    for (x, y, r, h) in [(-20, 60, 16, 26), (6, 70, 20, 32), (30, 58, 14, 22)]:
        c = cone((x, y, h / 2 - 3), r, 0.5, h, ice, verts=48)
        tex = bpy.data.textures.new("gl", 'CLOUDS'); tex.noise_scale = 4
        sd = c.modifiers.new("sd", 'SUBSURF'); sd.levels = sd.render_levels = 3; sd.subdivision_type = 'SIMPLE'
        dp = c.modifiers.new("dp", 'DISPLACE'); dp.texture = tex; dp.strength = 3
    scatter(lambda x, y: conifer(x, y, R.uniform(0.8, 1.4), snow=True), 14, (4, 22), 14)
    mammoth(5, 16, 1.0)
    mammoth(9.5, 20, 0.85, "#5a4434")
    mammoth(-9, 26, 0.8, "#5a4434")
    scatter(lambda x, y: rock(x, y, R.uniform(0.2, 0.5), "#8a8a8e"), 8, (-9, 6), 8)
    snow_flakes(140)

t = time.time()
render(OUT + f"scene_{ERA}.png")
print("DONE scene", ERA, round(time.time() - t, 1))
