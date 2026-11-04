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
import face_kit  # noqa: E402
import player_look  # noqa: E402

CELL_M = scn.CELL_M
FRAME_W, FRAME_H = 32, 64
FEET_X, FEET_Y = 16, 54
HEIGHT_M = 1.78
WALK_FRAMES = 8

# 8 facings in clockwise screen order, starting with "screen down". The angle rotates the model
# (which faces Blender -Y = world +y = screen down-left at 0 degrees) around Z.
FACINGS = {"s": 45, "sw": 0, "w": -45, "nw": -90, "n": -135, "ne": 180, "e": 135, "se": 90}


def setup_camera(fw, fh, fx, fy, co=None):
    """Orthographic camera with the map projection; world origin lands on frame pixel (fx, fy)."""
    sc = bpy.context.scene
    sc.render.resolution_x = fw * SS_CURRENT[0]
    sc.render.resolution_y = fh * SS_CURRENT[0]
    if co is None:
        cam = bpy.data.cameras.new("cam")
        cam.type = "ORTHO"
        cam.sensor_fit = "HORIZONTAL"
        co = bpy.data.objects.new("cam", cam)
        sc.collection.objects.link(co)
        sc.camera = co
    co.data.ortho_scale = fw * math.cos(math.radians(45)) * CELL_M / 16
    co.rotation_euler = (math.radians(60), 0, math.radians(45))
    a = fw / 2 - fx
    b = fh / 2 - fy
    ux, uy = b + a / 2, b - a / 2
    target = Vector((ux / 16 * CELL_M, -uy / 16 * CELL_M, 0))
    fwd = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)),
                  math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))
    co.location = target - fwd * 40
    return co


SS_CURRENT = [4]
FACE = [None]          # face_kit.Face of the player (V2 look + modelled face), set in main()
ANCHORS = {}           # frame stem -> projected face anchors (written to anchors.json)
CAMFWD = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)),
                 math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))


def tweak(arm):
    """Player V2 shoulders: re-applied after every frame_set (the actions key the torso scale)."""
    face_kit.player_pose_tweaks(arm)
    bpy.context.view_layer.update()


def record(stem, co, fw, fh):
    ANCHORS[stem] = FACE[0].project(co, CAMFWD, fw, fh)


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
    mode = argv[6] if len(argv) > 6 else "walk"
    SS_CURRENT[0] = ss
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
    bpy.context.view_layer.update()

    # player V2 look: proportions on the keyframes, outfit details, modelled face (anchors for the pixel pass)
    face_kit.apply_proportions()
    player_look.apply(arm)
    FACE[0] = face_kit.Face(sc, arm, "player", colours["Skin"], next(m for m in meshes if m.name == "BaseHuman"))
    FACE[0].build()
    FACE[0].make_anchors()
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()

    co = setup_camera(FRAME_W, FRAME_H, FEET_X, FEET_Y)

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

    if mode == "actions":
        render_actions(sc, arm, meshes, root, co, out_dir, model_yaw)
        save_anchors(out_dir)
        return

    if mode == "idle":
        for name, angle in FACINGS.items():
            root.rotation_euler = (0, 0, math.radians(angle + model_yaw))
            sc.frame_set(1)
            tweak(arm)
            sc.render.filepath = os.path.join(out_dir, f"{name}_0.png")
            bpy.ops.render.render(write_still=True)
            record(f"{name}_0", co, FRAME_W, FRAME_H)
        save_anchors(out_dir)
        return

    w0, w1 = int(walk.frame_range[0]), int(walk.frame_range[1])
    cycle = w1 - w0
    for name, angle in FACINGS.items():
        root.rotation_euler = (0, 0, math.radians(angle + model_yaw))
        arm.animation_data.action = idle
        sc.frame_set(1)
        tweak(arm)
        sc.render.filepath = os.path.join(out_dir, f"{name}_0.png")
        bpy.ops.render.render(write_still=True)
        record(f"{name}_0", co, FRAME_W, FRAME_H)
        arm.animation_data.action = walk
        for i in range(WALK_FRAMES):
            sc.frame_set(w0 + round(i * cycle / WALK_FRAMES))
            tweak(arm)
            sc.render.filepath = os.path.join(out_dir, f"{name}_{i + 1}.png")
            bpy.ops.render.render(write_still=True)
            record(f"{name}_{i + 1}", co, FRAME_W, FRAME_H)
    save_anchors(out_dir)


def save_anchors(out_dir):
    with open(os.path.join(out_dir, "anchors.json"), "w") as f:
        json.dump(ANCHORS, f)


# Interaction poses (approved by the owner): sitting on a bench, sleeping on the side, washing.
ACTION_FRAME = 64                      # sit / sleep frames are 64x64, origin at (32, 44)
ACTION_FEET = (32, 44)
SIT_FRAMES = (80, 100, 120, 140)       # inside the Sitting action's seated loop
WASH_FRAMES = 4


def render_actions(sc, arm, meshes, root, co, out_dir, model_yaw):
    base_loc = root.location.copy()

    def shot(path):
        sc.render.filepath = os.path.join(out_dir, path)
        bpy.ops.render.render(write_still=True)

    # sitting, facing screen down-left (benches have their back towards -y)
    setup_camera(ACTION_FRAME, ACTION_FRAME, *ACTION_FEET, co=co)
    sit = find_action("_Sitting")
    arm.animation_data.action = sit
    f0 = int(sit.frame_range[0])
    root.rotation_euler = (0, 0, math.radians(model_yaw))
    for i, f in enumerate(SIT_FRAMES):
        sc.frame_set(f0 + f)
        tweak(arm)
        shot(f"sit_{i}.png")
        record(f"sit_{i}", co, ACTION_FRAME, ACTION_FRAME)

    # sleeping on the side: 40 % sitting blended into idle, laid on its side along the bench (x)
    arm.animation_data.action = None
    ad = arm.animation_data
    t1 = ad.nla_tracks.new()
    t1.strips.new("idle", 1, find_action("_Idle"))
    t2 = ad.nla_tracks.new()
    s2 = t2.strips.new("sit", 1, sit)
    s2.influence = 0.4
    sc.frame_set(60)
    tweak(arm)
    root.rotation_euler = (0, math.radians(-90), 0)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in meshes:
        ev = o.evaluated_get(deps)
        me = ev.to_mesh()
        pts += [ev.matrix_world @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    mz = min(p.z for p in pts)
    root.location = (root.location.x - cx, root.location.y - cy, root.location.z - mz + 0.48)
    shot("lie_0.png")
    ad.nla_tracks.remove(t2)
    ad.nla_tracks.remove(t1)
    root.location = base_loc

    # washing (hands rubbing in front of the chest), 8 facings, normal 32x64 frames
    setup_camera(FRAME_W, FRAME_H, FEET_X, FEET_Y, co=co)
    clap = find_action("_Clapping")
    arm.animation_data.action = clap
    c0, c1 = int(clap.frame_range[0]), int(clap.frame_range[1])
    for name, angle in FACINGS.items():
        root.rotation_euler = (0, 0, math.radians(angle + model_yaw))
        for i in range(WASH_FRAMES):
            sc.frame_set(c0 + round(i * (c1 - c0) / WASH_FRAMES))
            tweak(arm)
            shot(f"wash_{name}_{i}.png")
            record(f"wash_{name}_{i}", co, FRAME_W, FRAME_H)

main()
