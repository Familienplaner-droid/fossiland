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


