"""
Town Life - collectible props (runs INSIDE Blender, called by tools/build_assets.py -> build_collectibles).

  blender -b -noaudio --python tools/blender_props.py -- <out_dir> <samples>

Twelve small 3D props lying on the ground (4 old city coins, 4 lost postcards, 4 VaultTech flyers), rendered with the map camera
(60 deg pitch, 45 deg yaw, orthographic) like every other sprite: transparent background, sun + sky light, Cycles. Two sizes per
prop: small_<name>.png (16x16 game frame, 30 px per metre) and big_<name>.png (32x32 icon for the collection screen, 60 px per
metre), both written at 8x supersampling (128 / 256 px; build_assets box-downsamples and outlines them).
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

CELL_M = 0.75
SS_PX = 128


def rgb(h):
    h = h.lstrip("#")
    lin = lambda v: ((v / 255 + 0.055) / 1.055) ** 2.4 if v / 255 > 0.04045 else v / 255 / 12.92
    return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), 1.0)


_mats = {}


def mat(colour, rough=0.5, metal=0.0, emit=0.0):
    key = (colour, rough, metal, emit)
    if key not in _mats:
        m = bpy.data.materials.new("m")
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = rgb(colour)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        if emit:
            b.inputs["Emission Color"].default_value = rgb(colour)
            b.inputs["Emission Strength"].default_value = emit
        _mats[key] = m
    return _mats[key]


def finish(o, colour, rough=0.5, metal=0.0, emit=0.0):
    o.data.materials.append(mat(colour, rough, metal, emit))
    return o


def box(x0, y0, z0, x1, y1, z1, colour, rough=0.6, metal=0.0, rot=0.0, pivot=(0, 0), emit=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.scale = (x1 - x0, y1 - y0, z1 - z0)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    bpy.ops.object.transform_apply(scale=True)
    if rot:
        o.location = Vector((o.location.x - pivot[0], o.location.y - pivot[1], o.location.z))
        o.rotation_euler = (0, 0, math.radians(rot))
        o.location = Matrix.Rotation(math.radians(rot), 3, "Z") @ o.location
        o.location = Vector((o.location.x + pivot[0], o.location.y + pivot[1], o.location.z))
    return finish(o, colour, rough, metal, emit)


def cyl(x, y, z0, z1, r, colour, rough=0.5, metal=0.0, verts=48, r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r if r2 is None else r2, depth=z1 - z0)
    o = bpy.context.active_object
    o.location = (x, y, (z0 + z1) / 2)
    bpy.ops.object.shade_smooth()
    return finish(o, colour, rough, metal)


def torus(x, y, z, R, r, colour, rough=0.4, metal=0.0):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=48, minor_segments=10)
    o = bpy.context.active_object
    o.location = (x, y, z)
    bpy.ops.object.shade_smooth()
    return finish(o, colour, rough, metal)


def poly(pts, z0, z1, colour, rough=0.6, metal=0.0):
    me = bpy.data.meshes.new("p")
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, z0)) for (x, y) in pts]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    for v in [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z = z1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("p", me)
    bpy.context.collection.objects.link(o)
    return finish(o, colour, rough, metal)


def star_pts(cx, cy, r_out, r_in, n=5, rot=90):
    pts = []
    for k in range(2 * n):
        a = math.radians(rot + k * 180 / n)
        r = r_out if k % 2 == 0 else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ---------------------------------------------------------------------------------------------------- coins
def coin_copper():
    cyl(0, 0, 0, 0.026, 0.17, "#a85a2c", 0.38, 0.85)
    torus(0, 0, 0.026, 0.155, 0.014, "#c87a40", 0.3, 0.9)
    cyl(0, 0, 0.026, 0.03, 0.105, "#8e4a24", 0.45, 0.8)
    poly(star_pts(0, 0, 0.075, 0.032), 0.03, 0.036, "#d28a4c", 0.3, 0.9)


def coin_silver():
    cyl(0, 0, 0, 0.026, 0.2, "#b8c0ca", 0.28, 0.9)
    torus(0, 0, 0.026, 0.186, 0.015, "#e6ebf0", 0.2, 0.95)
    cyl(0, 0, 0.026, 0.031, 0.13, "#9ca6b2", 0.35, 0.9)
    torus(0, 0, 0.032, 0.085, 0.01, "#eef2f6", 0.2, 0.95)
    cyl(0, 0, 0.03, 0.036, 0.04, "#dde3ea", 0.25, 0.95)


def coin_brass_hole():
    cyl(0, 0, 0, 0.026, 0.17, "#c4983c", 0.35, 0.9)
    torus(0, 0, 0.026, 0.155, 0.014, "#e0b852", 0.25, 0.9)
    box(-0.05, -0.05, 0.022, 0.05, 0.05, 0.04, "#241a14", 0.9)             # the square hole
    torus(0, 0, 0.032, 0.095, 0.008, "#d8ae48", 0.3, 0.9)


def coin_token():
    cyl(0, 0, 0, 0.034, 0.2, "#5e5a4c", 0.6, 0.6)                           # dark pewter token, thick
    torus(0, 0, 0.034, 0.185, 0.016, "#8c8878", 0.45, 0.7)
    box(-0.025, -0.1, 0.034, 0.025, 0.1, 0.044, "#a8a490", 0.4, 0.7)         # embossed V
    box(-0.1, -0.025, 0.034, 0.1, 0.025, 0.044, "#a8a490", 0.4, 0.7)


# ---------------------------------------------------------------------------------------------------- postcards
def card(rot, border="#f2ecd8"):
    box(-0.19, -0.13, 0.0, 0.19, 0.13, 0.008, border, 0.8, rot=rot)


def rotated(x0, y0, z0, x1, y1, z1, colour, rot, rough=0.7, emit=0.0):
    box(x0, y0, z0, x1, y1, z1, colour, rough, rot=rot, emit=emit)


def stamp(rot, colour):
    rotated(0.115, 0.055, 0.008, 0.17, 0.115, 0.0105, "#f6f2e6", rot)
    rotated(0.12, 0.06, 0.0105, 0.165, 0.11, 0.0125, colour, rot)


def lines(rot):
    for k in range(3):
        rotated(0.02, -0.095 + k * 0.034, 0.008, 0.16 - k * 0.02, -0.088 + k * 0.034, 0.0096, "#3a4a6a", rot)


def card_lake():
    r = 18
    card(r)
    rotated(-0.17, -0.115, 0.008, 0.0, 0.11, 0.0095, "#7ec0ec", r, 0.5)
    rotated(-0.17, -0.115, 0.0095, 0.0, -0.03, 0.0108, "#4a9a58", r, 0.8)
    rotated(-0.14, -0.03, 0.0108, -0.07, 0.04, 0.012, "#f4f6f8", r, 0.6)
    stamp(r, "#d8402e")
    lines(r)


def card_sunset():
    r = -24
    card(r)
    rotated(-0.17, -0.115, 0.008, 0.0, 0.11, 0.0095, "#f08a34", r, 0.5)
    rotated(-0.17, -0.115, 0.0095, 0.0, -0.01, 0.0108, "#2c4c88", r, 0.4)
    rotated(-0.11, 0.02, 0.0095, -0.06, 0.07, 0.0112, "#ffe066", r, 0.4, emit=0.4)
    stamp(r, "#2e6ab8")
    lines(r)


def card_skyline():
    r = 8
    card(r)
    rotated(-0.17, -0.115, 0.008, 0.0, 0.11, 0.0095, "#1c2a4c", r, 0.5)
    for k, (x0, x1, h) in enumerate(((-0.17, -0.13, 0.12), (-0.13, -0.09, 0.2), (-0.09, -0.05, 0.15), (-0.05, -0.01, 0.22))):
        rotated(x0, -0.115, 0.0095, x1, -0.115 + h, 0.011, "#0e1424", r, 0.6)
        rotated(x0 + 0.01, -0.115 + h * 0.4, 0.011, x0 + 0.02, -0.115 + h * 0.4 + 0.02, 0.0118, "#ffd860", r, 0.4, emit=1.0)
    stamp(r, "#e0a82c")
    lines(r)


def card_lighthouse():
    r = -10
    card(r)
    rotated(-0.17, -0.115, 0.008, 0.0, 0.11, 0.0095, "#7edcd4", r, 0.5)
    rotated(-0.17, -0.115, 0.0095, 0.0, -0.05, 0.0108, "#2e8a94", r, 0.4)
    rotated(-0.1, -0.06, 0.0108, -0.07, 0.07, 0.013, "#f6f4f0", r, 0.6)
    rotated(-0.1, -0.01, 0.013, -0.07, 0.03, 0.0132, "#d8402e", r, 0.6)
    rotated(-0.105, 0.07, 0.013, -0.065, 0.09, 0.0136, "#2a2a30", r, 0.6)
    stamp(r, "#4aa05a")
    lines(r)


# ---------------------------------------------------------------------------------------------------- flyers
def sheet(rot, colour="#f4f4f0"):
    box(-0.12, -0.17, 0.0, 0.12, 0.17, 0.004, colour, 0.85, rot=rot)


def vlogo(rot, z, colour, s=1.0, cx=0.0, cy=0.02):
    """A "V" made of two bars (the VaultTech mark) lying on the sheet, tip towards -y."""
    for sgn in (-1, 1):
        o = box(-0.012 * s, -0.05 * s, z, 0.012 * s, 0.05 * s, z + 0.002, colour, 0.5)
        o.rotation_euler = (0, 0, math.radians(rot - sgn * 24))
        c = Matrix.Rotation(math.radians(rot), 3, "Z") @ Vector((cx + sgn * 0.026 * s, cy, 0))
        o.location = Vector((c.x, c.y, z + 0.001))


def flyer_gold():
    r = 14
    sheet(r)
    box(-0.12, 0.1, 0.004, 0.12, 0.17, 0.0055, "#d9a82c", 0.4, metal=0.6, rot=r)
    vlogo(r, 0.0055, "#14141a", 1.3)
    for k in range(4):
        box(-0.09, -0.04 - k * 0.04, 0.004, 0.09 - (k % 2) * 0.05, -0.027 - k * 0.04, 0.0052, "#8a8a92", 0.9, rot=r)
    box(-0.12, -0.17, 0.004, 0.12, -0.135, 0.0058, "#14141a", 0.6, rot=r)


def flyer_black():
    r = -18
    sheet(r, "#e9e9e6")
    box(-0.12, -0.02, 0.004, 0.12, 0.17, 0.0056, "#16161c", 0.5, rot=r)
    vlogo(r, 0.0056, "#e2b53a", 2.0, cy=0.075)
    box(-0.09, -0.065, 0.004, 0.09, -0.045, 0.0056, "#16161c", 0.7, rot=r)
    for k in range(3):
        box(-0.09, -0.1 - k * 0.035, 0.004, 0.06 - k * 0.03, -0.09 - k * 0.035, 0.0052, "#7a7a82", 0.9, rot=r)


def flyer_crumpled():
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.115)
    o = bpy.context.active_object
    o.location = (0, 0, 0.09)
    import random
    rnd = random.Random(3)
    me = o.data
    for v in me.vertices:
        f = 1 + rnd.uniform(-0.28, 0.28)
        v.co = Vector((v.co.x * f * 1.08, v.co.y * f, v.co.z * f * 0.82))
    bpy.ops.object.shade_flat()
    finish(o, "#eeeeea", 0.9)
    # gold smear + black corner peeking out
    box(-0.04, 0.02, 0.15, 0.06, 0.1, 0.162, "#d9a82c", 0.4, metal=0.5, rot=30)
    box(-0.1, -0.06, 0.1, -0.04, 0.0, 0.112, "#16161c", 0.6, rot=-20)


def flyer_folded():
    r = 10
    for sgn in (-1, 1):
        o = box(-0.12, 0.0, 0.0, 0.12, 0.17, 0.004, "#f4f4f0" if sgn > 0 else "#e2e2dc", 0.85)
        o.location.y = 0
        o.rotation_euler = (math.radians(sgn * 11), 0, 0)
        o.location = Vector((0, 0.0, 0.0))
        if sgn < 0:
            o.rotation_euler = (math.radians(180 - 11), 0, 0)
            o.location = Vector((0, 0.0, 0.0))
    # header band on the front half
    o = box(-0.12, 0.1, 0.004, 0.12, 0.17, 0.0056, "#d9a82c", 0.4, metal=0.5)
    o.rotation_euler = (math.radians(11), 0, 0)
    o2 = box(-0.03, 0.03, 0.0056, 0.03, 0.09, 0.0066, "#14141a", 0.5)
    o2.rotation_euler = (math.radians(11), 0, 0)
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob not in ():
            pass
    bpy.ops.object.select_all(action="DESELECT")


ITEMS = [
    ("coin_copper", coin_copper), ("coin_silver", coin_silver), ("coin_brass", coin_brass_hole), ("coin_token", coin_token),
    ("card_lake", card_lake), ("card_sunset", card_sunset), ("card_skyline", card_skyline), ("card_lighthouse", card_lighthouse),
    ("flyer_gold", flyer_gold), ("flyer_black", flyer_black), ("flyer_crumpled", flyer_crumpled), ("flyer_folded", flyer_folded),
]


def setup(sc, fw, fh, pxm):
    sc.render.resolution_x = SS_PX
    sc.render.resolution_y = SS_PX * fh // fw
    for o in [o for o in sc.objects if o.type == "CAMERA"]:
        bpy.data.objects.remove(o)
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.sensor_fit = "HORIZONTAL"
    cam.ortho_scale = fw / pxm
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    co.rotation_euler = (math.radians(60), 0, math.radians(45))
    fwd = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)), math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))
    co.location = Vector((0, 0, 0.02)) - fwd * 40


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_dir, samples = argv[0], int(argv[1])
    os.makedirs(out_dir, exist_ok=True)
    for size, (fw, fh, pxm) in (("small", (16, 16, 30.0)), ("big", (32, 32, 62.0))):
        for name, build in ITEMS:
            bpy.ops.wm.read_factory_settings(use_empty=True)
            sc = bpy.context.scene
            sc.render.engine = "CYCLES"
            sc.cycles.samples = samples
            sc.cycles.use_denoising = False
            sc.render.film_transparent = True
            sc.render.filter_size = 1.0
            sc.view_settings.view_transform = "Standard"
            sc.render.image_settings.color_mode = "RGBA"
            _mats.clear()
            build()
            setup(sc, fw, fh, pxm)
            world = bpy.data.worlds.new("world")
            sc.world = world
            world.use_nodes = True
            world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.62, 0.68, 0.82, 1)
            world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.1
            sun = bpy.data.lights.new("sun", "SUN")
            sun.energy = 3.8
            sun.angle = math.radians(8)
            so = bpy.data.objects.new("sun", sun)
            sc.collection.objects.link(so)
            so.rotation_euler = Vector((-0.25, 0.7, -0.65)).normalized().to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = os.path.join(out_dir, f"{size}_{name}.png")
            bpy.ops.render.render(write_still=True)


main()
