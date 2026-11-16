import sys, math, random, time
sys.path.insert(0, "/home/claude/fossil3d")
import bpy
from lib import *

SOILS = [
    [["#dd8f6c", "#c2714f", "#9a5538"], ["#9a4e3e", "#7d3d30", "#5a2a21"], ["#857b72", "#686059", "#4c4540"]],
    [["#e6bc7c", "#cf9f5f", "#a97a43"], ["#b06e45", "#93573a", "#6e3f29"], ["#857b72", "#686059", "#4c4540"]],
    [["#e6bc7c", "#cf9f5f", "#a97a43"], ["#a07a52", "#86633f", "#634830"], ["#d3caa9", "#b8ae8d", "#918769"]],
    [["#d9b680", "#c09a63", "#9b7746"], ["#ece7da", "#d3cdbc", "#aaa391"], ["#7d746c", "#615a54", "#46413d"]],
    [["#9a7a54", "#80633f", "#5e472c"], ["#6e5a44", "#574634", "#3d3024"], ["#4f4b45", "#3b3934", "#2a2825"]],
    [["#e3f1f7", "#c2dce8", "#98bfd1"], ["#dcbc8c", "#c3a170", "#9c7e52"], ["#8e8a84", "#716d68", "#55524e"]],
]
PX = 110          # pixels per unit
SLOT = 1.3        # units per atlas slot
COLS, ROWS = 9, 6
mode = sys.argv[-1] if len(sys.argv) > 1 else "tiles"


def tile(cx, cy, cols, era, layer, var, seed):
    rnd = random.Random(seed)
    light, dark, peb = [hexc(c) for c in cols]
    hard = var == 2
    base = dark if hard else light
    ice = (era == 5 and layer == 0)
    if ice:
        m = mat_basic(f"m{seed}", base, rough=0.12, coat=1.0, noise=(hexc("#ffffff"), 3.0, 4), bump=0.15, bump_scale=6, ao=0.25)
    else:
        m = mat_basic(f"m{seed}", base, rough=0.85, noise=(tuple(c * 0.82 for c in base), 4.5, 8), bump=0.35, bump_scale=14, ao=0.3)
    ob = rcube((cx, cy, 0), (1.0, 1.0, 0.55), m, bevel=0.14, name="tile")
    sd = ob.modifiers.new("sd", 'SUBSURF')
    sd.levels = sd.render_levels = 3
    tex = bpy.data.textures.new(f"t{seed}", 'CLOUDS')
    tex.noise_scale = 0.35
    dp = ob.modifiers.new("dp", 'DISPLACE')
    dp.texture = tex
    dp.strength = 0.07 if not ice else 0.03
    dp.texture_coords = 'GLOBAL'
    # pebbles / inclusions
    n = rnd.randint(3, 5) + (4 if hard else 0)
    pm = mat_basic(f"p{seed}", peb if not ice else hexc("#ffffff"), rough=0.5 if not ice else 0.1,
                   noise=(tuple(c * 0.7 for c in peb), 6, 4), bump=0.2, bump_scale=20)
    for i in range(n):
        x = cx + rnd.uniform(-0.36, 0.36)
        y = cy + rnd.uniform(-0.36, 0.36)
        r = rnd.uniform(0.045, 0.1) * (1.25 if hard else 1)
        s = sphere((x, y, 0.27), r, pm, scale=(1.2, rnd.uniform(0.8, 1.1), 0.55), seg=16)
        s.rotation_euler = (0, 0, rnd.uniform(0, 3.14))
    if hard:  # embedded rock chunk
        rm = mat_basic(f"r{seed}", tuple(c * 0.75 for c in peb), rough=0.55, bump=0.4, bump_scale=10, ao=0.2)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.17, location=(cx + rnd.uniform(-0.2, 0.2), cy + rnd.uniform(-0.2, 0.2), 0.25))
        rk = bpy.context.active_object
        rk.scale = (1.3, 1.0, 0.6)
        rk.rotation_euler = (0.2, 0.3, rnd.uniform(0, 3))
        assign(rk, rm)


if mode == "tiles":
    sc = reset(samples=40, w=int(COLS * SLOT * PX), h=int(ROWS * SLOT * PX))
    for e in range(ROWS):
        for l in range(3):
            for v in range(3):
                col = l * 3 + v
                cx = (col - (COLS - 1) / 2) * SLOT
                cy = ((ROWS - 1) / 2 - e) * SLOT
                tile(cx, cy, SOILS[e][l], e, l, v, seed=e * 100 + l * 10 + v)
    camera((0, 0, 20), (0, 0, 0), ortho=COLS * SLOT)
    sun(rot=(math.radians(35), math.radians(-12), math.radians(-20)), strength=3.2, angle=10)
    world_color((0.75, 0.72, 0.68), 0.9)
    t = time.time()
    render(OUT + "tiles_sheet.png")
    print("tiles", time.time() - t)
else:  # pit floors
    for e in range(6):
        sc = reset(samples=32, w=512, h=576, transparent=False)
        dk = tuple(c * 0.3 for c in hexc(SOILS[e][1][1]))
        m = mat_basic("floor", dk, rough=0.95, noise=(tuple(c * 0.55 for c in dk), 3.0, 8), bump=0.6, bump_scale=9, ao=0.6)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        pl = bpy.context.active_object
        pl.scale = (8.6, 9.6, 1)
        bpy.ops.object.transform_apply(scale=True)
        sd = pl.modifiers.new("sd", 'SUBSURF'); sd.subdivision_type = 'SIMPLE'; sd.levels = sd.render_levels = 6
        tex = bpy.data.textures.new("fl", 'CLOUDS'); tex.noise_scale = 0.6
        dp = pl.modifiers.new("dp", 'DISPLACE'); dp.texture = tex; dp.strength = 0.25; dp.texture_coords = 'GLOBAL'
        assign(pl, m)
        rnd = random.Random(e)
        pm = mat_basic("peb", tuple(c * 1.6 for c in dk), rough=0.7, ao=0.3)
        for i in range(60):
            sphere((rnd.uniform(-4, 4), rnd.uniform(-4.5, 4.5), 0.1), rnd.uniform(0.05, 0.14), pm, scale=(1.2, 1, .6), seg=12)
        camera((0, 0, 20), (0, 0, 0), ortho=9)
        sun(rot=(math.radians(35), math.radians(-12), math.radians(-20)), strength=1.6, angle=20)
        world_color((0.4, 0.35, 0.3), 0.4)
        render(OUT + f"floor_{e}.png")
