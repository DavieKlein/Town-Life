"""
Town Life - animated character renderer (runs INSIDE Blender, called by tools/build_assets.py).

  blender -b -noaudio --python tools/blender_actor.py -- <fbx> <out_dir> <supersample> <samples> <colours_json>

Imports a rigged, animated CC0 character (Quaternius "Animated Men/Women Characters"), recolours
its materials, scales it to HEIGHT_M and renders, for 8 isometric facings, one idle frame and
WALK_FRAMES frames of the walk cycle with the same camera scale as the maps:
  <out_dir>/<facing>_<frame>.png   facing in s/sw/w/nw/n/ne/e/se (screen directions), frame 0 = idle
Each frame is FRAME_W x FRAME_H pixels (times supersample) with the feet at (FEET_X, FEET_Y).
"""

import json
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as scn  # noqa: E402
from blender_render import rgb  # noqa: E402

CELL_M = scn.CELL_M
FRAME_W, FRAME_H = 32, 64
FEET_X, FEET_Y = 16, 54
HEIGHT_M = 1.78
WALK_FRAMES = 8

# 8 facings in clockwise screen order, starting with "screen down". The angle rotates the model
# (which faces Blender -Y = world +y = screen down-left at 0 degrees) around Z.
FACINGS = {"s": 45, "sw": 0, "w": -45, "nw": -90, "n": -135, "ne": 180, "e": 135, "se": 90}


def find_action(suffix):
    for a in bpy.data.actions:
        if a.name.endswith(suffix):
            return a
    raise RuntimeError("action not found: " + suffix)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    fbx, out_dir = argv[0], argv[1]
    ss = int(argv[2]) if len(argv) > 2 else 4
    samples = int(argv[3]) if len(argv) > 3 else 32
    colours = json.loads(argv[4]) if len(argv) > 4 else {}
    model_yaw = float(argv[5]) if len(argv) > 5 else 0.0
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

    bpy.ops.import_scene.fbx(filepath=fbx)
    arm = next(o for o in sc.objects if o.type == "ARMATURE")
    meshes = [o for o in sc.objects if o.type == "MESH"]
    for m in bpy.data.materials:
        if m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
            bsdf = m.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Alpha"].default_value = 1.0          # the FBX files import with alpha 0
            bsdf.inputs["Roughness"].default_value = 0.65
            base = m.name.split(".")[0]
            if base in colours:
                bsdf.inputs["Base Color"].default_value = rgb(colours[base])

    # scale to the wanted height, feet on the ground at the origin
    idle = find_action("_Idle")
    walk = find_action("_Walk")
    arm.animation_data_create()
    arm.animation_data.action = idle
    sc.frame_set(1)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    zs = []
    for o in meshes:
        ev = o.evaluated_get(deps)
        me = ev.to_mesh()
        zs += [(ev.matrix_world @ v.co).z for v in me.vertices]
        ev.to_mesh_clear()
    height = max(zs) - min(zs)
    root = bpy.data.objects.new("root", None)
    sc.collection.objects.link(root)
    arm.parent = root
    s = HEIGHT_M / height
    root.scale = (s, s, s)
    root.location = (0, 0, -min(zs) * s)

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

    w0, w1 = int(walk.frame_range[0]), int(walk.frame_range[1])
    cycle = w1 - w0
    for name, angle in FACINGS.items():
        root.rotation_euler = (0, 0, math.radians(angle + model_yaw))
        arm.animation_data.action = idle
        sc.frame_set(1)
        sc.render.filepath = os.path.join(out_dir, f"{name}_0.png")
        bpy.ops.render.render(write_still=True)
        arm.animation_data.action = walk
        for i in range(WALK_FRAMES):
            sc.frame_set(w0 + round(i * cycle / WALK_FRAMES))
            sc.render.filepath = os.path.join(out_dir, f"{name}_{i + 1}.png")
            bpy.ops.render.render(write_still=True)


main()
