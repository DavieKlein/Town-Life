"""
Town Life - 3D character renderer (runs INSIDE Blender, called by tools/build_assets.py).

  blender -b -noaudio --python tools/blender_character.py -- <out_dir> <supersample> <samples>

Builds a simple stylised character from primitives, poses it for an idle frame and a 4-frame walk
cycle, and renders 4 isometric facings with the same camera scale as the maps:
  <out_dir>/<facing>_<frame>.png   facing in down/right/up/left, frame 0 = idle, 1..4 = walk
Each frame is FRAME_W x FRAME_H pixels (times supersample) with the feet at (FEET_X, FEET_Y).
"""

import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as scn  # noqa: E402
from blender_render import make_material, rgb  # noqa: E402

CELL_M = scn.CELL_M
FRAME_W, FRAME_H = 32, 64
FEET_X, FEET_Y = 16, 58

SKIN = dict(c="#f0c09a", rough=0.6)
CHAR_MATS = {
    "skin": SKIN,
    "hair": dict(c="#5a3420", rough=0.5),
    "jacket": dict(c="#2f5aa8", rough=0.6),
    "shirt": dict(c="#f2efe6", rough=0.6),
    "pants": dict(c="#c8a46a", rough=0.7),
    "shoes": dict(c="#3a2a22", rough=0.4),
    "eyes": dict(c="#1e1a1a", rough=0.3),
}


def new_obj(name, mesh_op, mat, parent=None, **kw):
    """Creates a mesh at a WORLD location and parents it (rest pose has no rotations)."""
    mesh_op(**kw)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(MATS[mat])
    for p in ob.data.polygons:
        p.use_smooth = True
    if parent is not None:
        world = Vector(ob.location)
        ob.parent = parent
        ob.location = world - WORLD_LOC[parent.name]
    return ob


def empty(name, loc, parent=None):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    WORLD_LOC[name] = Vector(loc)
    if parent is not None:
        e.parent = parent
        e.location = Vector(loc) - WORLD_LOC[parent.name]
    else:
        e.location = loc
    return e


def build_character():
    root = empty("root", (0, 0, 0))
    # ---- legs (pivot at the hips) ----
    legs = {}
    for side, sx in (("l", -0.1), ("r", 0.1)):
        hip = empty(f"hip_{side}", (sx, 0, 0.92), root)
        new_obj(f"thigh_{side}", bpy.ops.mesh.primitive_cylinder_add, "pants", hip,
                radius=0.075, depth=0.46, location=(sx, 0, 0.69), vertices=12)
        knee = empty(f"knee_{side}", (sx, 0, 0.46), hip)
        new_obj(f"shin_{side}", bpy.ops.mesh.primitive_cylinder_add, "pants", knee,
                radius=0.065, depth=0.42, location=(sx, 0, 0.25), vertices=12)
        shoe = new_obj(f"shoe_{side}", bpy.ops.mesh.primitive_cube_add, "shoes", knee,
                       size=1, location=(sx, -0.05, 0.045))
        shoe.scale = (0.1, 0.22, 0.09)
        legs[side] = (hip, knee)
    # ---- torso ----
    torso = new_obj("torso", bpy.ops.mesh.primitive_cylinder_add, "jacket", root,
                    radius=0.2, depth=0.6, location=(0, 0, 1.2), vertices=16)
    torso.scale = (1.0, 0.62, 1.0)
    shirt = new_obj("shirt", bpy.ops.mesh.primitive_cube_add, "shirt", root, size=1, location=(0, -0.11, 1.36))
    shirt.scale = (0.1, 0.03, 0.24)
    belt = new_obj("hips", bpy.ops.mesh.primitive_cylinder_add, "pants", root,
                   radius=0.19, depth=0.14, location=(0, 0, 0.92), vertices=16)
    belt.scale = (1.0, 0.65, 1.0)
    # ---- arms (pivot at the shoulders) ----
    arms = {}
    for side, sx in (("l", -0.255), ("r", 0.255)):
        sh = empty(f"shoulder_{side}", (sx, 0, 1.46), root)
        new_obj(f"arm_{side}", bpy.ops.mesh.primitive_cylinder_add, "jacket", sh,
                radius=0.06, depth=0.55, location=(sx, 0, 1.18), vertices=10)
        new_obj(f"hand_{side}", bpy.ops.mesh.primitive_uv_sphere_add, "skin", sh,
                radius=0.055, location=(sx, 0, 0.88), segments=10, ring_count=6)
        arms[side] = sh
    # ---- head ----
    new_obj("neck", bpy.ops.mesh.primitive_cylinder_add, "skin", root, radius=0.055, depth=0.12,
            location=(0, 0, 1.55), vertices=10)
    head = new_obj("head", bpy.ops.mesh.primitive_uv_sphere_add, "skin", root, radius=0.13,
                   location=(0, 0, 1.69), segments=20, ring_count=12)
    head.scale = (0.95, 0.95, 1.1)
    hair = new_obj("hair", bpy.ops.mesh.primitive_uv_sphere_add, "hair", root, radius=0.142,
                   location=(0, 0.03, 1.73), segments=20, ring_count=12)
    hair.scale = (1.0, 1.0, 0.95)
    face = new_obj("face", bpy.ops.mesh.primitive_uv_sphere_add, "skin", root, radius=0.12,
                   location=(0, -0.035, 1.665), segments=20, ring_count=12)
    face.scale = (0.92, 0.9, 1.0)
    for sx in (-0.045, 0.045):
        new_obj("eye", bpy.ops.mesh.primitive_uv_sphere_add, "eyes", root, radius=0.02,
                location=(sx, -0.14, 1.69), segments=8, ring_count=6)
    return root, legs, arms


def pose(legs, arms, phase):
    """phase None = idle; otherwise 0..1 around the walk cycle."""
    if phase is None:
        swing = 0.0
        bend_l = bend_r = 0.0
    else:
        swing = math.sin(phase * 2 * math.pi) * math.radians(28)
        bend_l = max(0.0, -math.sin(phase * 2 * math.pi)) * math.radians(35)
        bend_r = max(0.0, math.sin(phase * 2 * math.pi)) * math.radians(35)
    hip_l, knee_l = legs["l"]
    hip_r, knee_r = legs["r"]
    # rotation around X: positive = leg swings backwards (character faces -Y)
    hip_l.rotation_euler = (swing, 0, 0)
    hip_r.rotation_euler = (-swing, 0, 0)
    knee_l.rotation_euler = (bend_l, 0, 0)
    knee_r.rotation_euler = (bend_r, 0, 0)
    arms["l"].rotation_euler = (-swing * 0.8, 0, math.radians(-4))
    arms["r"].rotation_euler = (swing * 0.8, 0, math.radians(4))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_dir = argv[0]
    ss = int(argv[1]) if len(argv) > 1 else 4
    samples = int(argv[2]) if len(argv) > 2 else 32
    os.makedirs(out_dir, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.render.film_transparent = True
    sc.render.filter_size = 1.0
    sc.view_settings.view_transform = "Standard"
    sc.render.resolution_x = FRAME_W * ss
    sc.render.resolution_y = FRAME_H * ss
    sc.render.image_settings.color_mode = "RGBA"

    global MATS
    MATS = {k: make_material(k, v) for k, v in CHAR_MATS.items()}
    root, legs, arms = build_character()

    # camera: same projection as the maps, feet at (FEET_X, FEET_Y)
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.sensor_fit = "HORIZONTAL"
    cam.ortho_scale = FRAME_W * math.cos(math.radians(45)) * CELL_M / 16
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    co.rotation_euler = (math.radians(60), 0, math.radians(45))
    a = FRAME_W / 2 - FEET_X
    b = FRAME_H / 2 - FEET_Y
    ux, uy = b + a / 2, b - a / 2
    target = Vector((ux / 16 * CELL_M, -uy / 16 * CELL_M, 0))
    fwd = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)),
                  math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))
    co.location = target - fwd * 40

    world = bpy.data.worlds.new("world")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.66, 0.8, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.5
    sun.angle = math.radians(10)
    so = bpy.data.objects.new("sun", sun)
    sc.collection.objects.link(so)
    so.rotation_euler = Vector((-0.25, 0.7, -0.65)).normalized().to_track_quat("-Z", "Y").to_euler()

    facings = {"down": 0, "right": 90, "up": 180, "left": -90}
    frames = [None, 0.0, 0.25, 0.5, 0.75]
    for name, angle in facings.items():
        root.rotation_euler = (0, 0, math.radians(angle))
        for i, phase in enumerate(frames):
            pose(legs, arms, phase)
            sc.render.filepath = os.path.join(out_dir, f"{name}_{i}.png")
            bpy.ops.render.render(write_still=True)


MATS = {}
WORLD_LOC = {}
main()
