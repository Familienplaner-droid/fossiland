import bpy, math, random
from mathutils import Vector

OUT = "/home/claude/fossil3d/out/"


def reset(samples=48, w=512, h=512, transparent=True):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    sc.cycles.max_bounces = 6
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 6
    sc.cycles.transparent_max_bounces = 8
    sc.render.film_transparent = transparent
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'AgX'
    for look in ('AgX - Punchy', 'Punchy', 'AgX - Medium High Contrast'):
        try:
            sc.view_settings.look = look
            break
        except Exception:
            pass
    world = bpy.data.worlds.new("W")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.5, 0.45, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    return sc


def world_color(rgb, strength):
    w = bpy.context.scene.world
    w.node_tree.nodes["Background"].inputs[0].default_value = (*rgb, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = strength


def hexc(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


def sock(node, name, kind=None, out=False):
    coll = node.outputs if out else node.inputs
    for s in coll:
        if s.name == name and (kind is None or s.type == kind):
            return s
    raise KeyError(name)


def mat_basic(name, color, rough=0.6, metal=0.0, noise=None, bump=0.0, bump_scale=8.0, ao=0.0,
              transmission=0.0, ior=1.45, coat=0.0, emission=None, emis_strength=0.0, alpha=1.0, spec=0.5):
    """Principled material. noise=(color2, scale, detail) mixes a second colour via noise."""
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    p = N["Principled BSDF"]
    sock(p, "Roughness").default_value = rough
    sock(p, "Metallic").default_value = metal
    try:
        sock(p, "Specular IOR Level").default_value = spec
    except KeyError:
        pass
    if transmission:
        sock(p, "Transmission Weight").default_value = transmission
        sock(p, "IOR").default_value = ior
    if coat:
        sock(p, "Coat Weight").default_value = coat
    if emission is not None:
        sock(p, "Emission Color").default_value = (*emission, 1)
        sock(p, "Emission Strength").default_value = emis_strength
    if alpha < 1:
        sock(p, "Alpha").default_value = alpha
    col_out = None
    tc = N.new("ShaderNodeTexCoord")
    if noise:
        c2, sc, det = noise
        nz = N.new("ShaderNodeTexNoise")
        sock(nz, "Scale").default_value = sc
        sock(nz, "Detail").default_value = det
        L.new(sock(tc, "Object", out=True), sock(nz, "Vector"))
        mix = N.new("ShaderNodeMix")
        mix.data_type = 'RGBA'
        cr = N.new("ShaderNodeValToRGB")
        cr.color_ramp.elements[0].position = 0.35
        cr.color_ramp.elements[1].position = 0.65
        L.new(sock(nz, "Factor", out=True), cr.inputs[0])
        L.new(cr.outputs[0], sock(mix, "Factor", "VALUE"))
        sock(mix, "A", "RGBA").default_value = (*color, 1)
        sock(mix, "B", "RGBA").default_value = (*c2, 1)
        col_out = sock(mix, "Result", "RGBA", out=True)
    else:
        sock(p, "Base Color").default_value = (*color, 1)
    if ao:
        aon = N.new("ShaderNodeAmbientOcclusion")
        aon.samples = 6
        sock(aon, "Distance").default_value = ao
        mix2 = N.new("ShaderNodeMix")
        mix2.data_type = 'RGBA'
        mix2.blend_type = 'MULTIPLY'
        gam = N.new("ShaderNodeMapRange")
        L.new(sock(aon, "AO", out=True), gam.inputs[0])
        gam.inputs[1].default_value = 0.0
        gam.inputs[2].default_value = 1.0
        gam.inputs[3].default_value = 0.35
        gam.inputs[4].default_value = 1.0
        if col_out is not None:
            L.new(col_out, sock(mix2, "A", "RGBA"))
        else:
            sock(mix2, "A", "RGBA").default_value = (*color, 1)
        sock(mix2, "Factor", "VALUE").default_value = 1.0
        comb = N.new("ShaderNodeCombineColor")
        for i in range(3):
            L.new(gam.outputs[0], comb.inputs[i])
        L.new(comb.outputs[0], sock(mix2, "B", "RGBA"))
        col_out = sock(mix2, "Result", "RGBA", out=True)
    if col_out is not None:
        L.new(col_out, sock(p, "Base Color"))
    if bump:
        nz2 = N.new("ShaderNodeTexNoise")
        sock(nz2, "Scale").default_value = bump_scale
        sock(nz2, "Detail").default_value = 6
        L.new(sock(tc, "Object", out=True), sock(nz2, "Vector"))
        b = N.new("ShaderNodeBump")
        sock(b, "Strength").default_value = bump
        L.new(sock(nz2, "Factor", out=True), sock(b, "Height"))
        L.new(sock(b, "Normal", out=True), sock(p, "Normal"))
    return m


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def smooth(obj):
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def tube(points, radius, mat=None, name="tube", res=4, radii=None, caps=True):
    """points: list of (x,y,z). radii: per-point multipliers."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.use_fill_caps = caps
    cu.resolution_u = 8
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1)
        sp.points[i].radius = (radii[min(i, len(radii) - 1)] if len(radii) == len(points) else radii[min(len(radii) - 1, round(i * (len(radii) - 1) / max(1, len(points) - 1)))]) if radii else 1.0
    ob = bpy.data.objects.new(name, cu)
    link(ob)
    if mat:
        cu.materials.append(mat)
    return ob


def smooth_path(ctrl, n=24):
    """Catmull-Rom through control points."""
    if len(ctrl) < 3:
        a, b = Vector(ctrl[0]), Vector(ctrl[-1])
        return [tuple(a.lerp(b, t / (n - 1))) for t in range(n)]
    P = [Vector(c) for c in ctrl]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = []
    segs = len(P) - 3
    per = max(2, n // segs)
    for i in range(segs):
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            v = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append(tuple(v))
    out.append(tuple(P[-2]))
    return out


def slab(outline, depth, bevel, mat=None, name="slab", loc=(0, 0, 0), rot=(math.pi / 2, 0, 0)):
    """Closed 2D outline (x,y) extruded by depth with rounded bevel. Default rot maps local XY to world XZ."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    cu.extrude = max(0.0001, depth / 2 - bevel)
    cu.bevel_depth = bevel
    cu.bevel_resolution = 3
    sp = cu.splines.new('POLY')
    sp.points.add(len(outline) - 1)
    for i, p in enumerate(outline):
        sp.points[i].co = (p[0], p[1], 0, 1)
    sp.use_cyclic_u = True
    ob = bpy.data.objects.new(name, cu)
    link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    if mat:
        cu.materials.append(mat)
    return ob


def sphere(loc, r, mat=None, scale=(1, 1, 1), seg=24, name="sph"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = scale
    smooth(ob)
    if mat:
        assign(ob, mat)
    return ob


def cone(loc, r1, r2, depth, mat=None, rot=(0, 0, 0), verts=24, name="cone"):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    smooth(ob)
    if mat:
        assign(ob, mat)
    return ob


def cyl(loc, r, depth, mat=None, rot=(0, 0, 0), verts=32, name="cyl", bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    if bevel:
        md = ob.modifiers.new("bv", 'BEVEL')
        md.width = bevel
        md.segments = 3
        md.limit_method = 'ANGLE'
    smooth(ob)
    if mat:
        assign(ob, mat)
    return ob


def rcube(loc, size, mat=None, bevel=0.1, name="cube", subdiv=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    md = ob.modifiers.new("bv", 'BEVEL')
    md.width = bevel
    md.segments = 4
    if subdiv:
        s = ob.modifiers.new("sd", 'SUBSURF')
        s.levels = s.render_levels = subdiv
    smooth(ob)
    if mat:
        assign(ob, mat)
    return ob


def sun(rot=(math.radians(50), math.radians(10), math.radians(-35)), strength=3.0, angle=8.0, color=(1, 0.96, 0.9)):
    l = bpy.data.lights.new("sun", 'SUN')
    l.energy = strength
    l.angle = math.radians(angle)
    l.color = color
    ob = bpy.data.objects.new("sun", l)
    link(ob)
    ob.rotation_euler = rot
    return ob


def area(loc, target=(0, 0, 0), power=300, size=4, color=(1, 1, 1)):
    l = bpy.data.lights.new("area", 'AREA')
    l.energy = power
    l.size = size
    l.color = color
    ob = bpy.data.objects.new("area", l)
    link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


def camera(loc, target, ortho=None, lens=50):
    c = bpy.data.cameras.new("cam")
    if ortho:
        c.type = 'ORTHO'
        c.ortho_scale = ortho
    else:
        c.lens = lens
    c.clip_end = 500
    ob = bpy.data.objects.new("cam", c)
    link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def shadow_catcher(size=40, z=0.0):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    ob = bpy.context.active_object
    ob.is_shadow_catcher = True
    return ob


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def fit_ortho(cam, margin=0.08, aspect=1.0):
    """Shift an ortho camera and set its scale so every visible mesh/curve fits."""
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    for ob in bpy.context.scene.objects:
        if ob.type not in ('MESH', 'CURVE') or ob.hide_render or getattr(ob, 'is_shadow_catcher', False):
            continue
        for c in ob.bound_box:
            p = inv @ (ob.matrix_world @ Vector(c))
            xs.append(p.x); ys.append(p.y)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = max(w, h * aspect) * (1 + margin)
    cam.location = cam.matrix_world @ Vector((cx, cy, 0))
