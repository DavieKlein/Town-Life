"""
Town Life - activity poses of the player (runs INSIDE Blender, called by tools/build_assets.py).

  blender -b -noaudio --python tools/blender_acts.py -- <fbx> <out_dir> <supersample> <samples> <colours_json> [acts] [facings]

Poses the Quaternius rig does not ship (eat, drink, read, search a bin) are made procedurally: the Idle pose
is bent bone by bone (rotations about the bone head, in armature space: +X = character's left side, -Y =
forward, +Z = up) and small prop meshes (food, book, water) are placed at the hands.
For every activity 8 facings x 4 frames of 32x64 are rendered with the map camera:
  <out_dir>/<activity>_<facing>_<frame>.png
"""

import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as scn  # noqa: E402
from blender_render import rgb  # noqa: E402
import face_kit  # noqa: E402
import player_look  # noqa: E402

CELL_M = scn.CELL_M
FRAME_W, FRAME_H = 64, 64      # wide frames: bending / reaching poses stick out sideways
FEET_X, FEET_Y = 32, 54
HEIGHT_M = 1.78
FACINGS = {"s": 45, "sw": 0, "w": -45, "nw": -90, "n": -135, "ne": 180, "e": 135, "se": 90}
AXES = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}

SS = 4


def setup_camera(fw, fh, fx, fy):
    sc = bpy.context.scene
    sc.render.resolution_x = fw * SS
    sc.render.resolution_y = fh * SS
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


def material(colour, rough=0.6):
    m = bpy.data.materials.new("prop")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(colour)
    b.inputs["Roughness"].default_value = rough
    return m


def make_prop(kind, colour, size):
    """A mesh of the given size in metres (placed later by Rig.place)."""
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.5)
    else:
        bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(material(colour))
    return o


class Rig:
    def __init__(self, arm):
        self.arm = arm
        self.rest = {}
        for pb in arm.pose.bones:
            self.rest[pb.name] = (pb.location.copy(), pb.rotation_quaternion.copy(), pb.scale.copy())
        self.k = 1.0

    @staticmethod
    def update():
        bpy.context.view_layer.update()

    def reset(self):
        for pb in self.arm.pose.bones:
            loc, rot, sca = self.rest[pb.name]
            pb.location, pb.rotation_quaternion, pb.scale = loc.copy(), rot.copy(), sca.copy()
        self.update()
        self.k = 1.0 / self.arm.matrix_world.to_scale().x

    def rot(self, bone, axis, deg):
        """Rotates a bone (and its children) about its head around an armature-space axis."""
        pb = self.arm.pose.bones[bone]
        m = pb.matrix.copy()
        h = m.translation.copy()
        r = Matrix.Rotation(math.radians(deg), 4, AXES[axis])
        pb.matrix = Matrix.Translation(h) @ r @ Matrix.Translation(-h) @ m
        self.update()

    def pose(self, ops):
        self.reset()
        for (bone, axis, deg) in ops:
            self.rot(bone, axis, deg)

    def pos(self, bone, t=0.0, to=None):
        pb = self.arm.pose.bones[bone]
        a = pb.head.copy()
        b = self.arm.pose.bones[to].head.copy() if to else pb.tail.copy()
        return a.lerp(b, t)

    def place(self, obj, p, rot_ops=(), scale=1.0):
        """Puts obj at armature-space point p, rotated by (axis, deg) steps (armature space)."""
        r = Matrix.Identity(4)
        for axis, deg in rot_ops:
            r = Matrix.Rotation(math.radians(deg), 4, AXES[axis]) @ r
        obj.matrix_world = self.arm.matrix_world @ Matrix.Translation(p) @ r @ Matrix.Scale(self.k * scale, 4)
        obj.hide_render = False
        obj.hide_viewport = False


def hand_centre(rig, side):
    return rig.pos("Palm." + side, 0.5, "MiddleHand." + side)


def eat_pose(i):
    lift = [0.35, 0.65, 1.0, 0.75][i]
    return [
        ("UpperArm.R", "X", -20 - 20 * lift),
        ("UpperArm.R", "Z", 30),
        ("LowerArm.R", "X", -90 - 50 * lift),
        ("LowerArm.R", "Z", 20),
        ("UpperArm.L", "X", -8),
        ("Head", "X", [0, 3, 9, 4][i]),
    ]


def drink_pose(i):
    bend = [38, 32, 18, 30][i]
    reach = [1.0, 0.75, 0.0, 0.6][i]
    ops = [("Abdomen", "X", bend * 0.5), ("Torso", "X", bend * 0.5)]
    for side, sgn in (("R", -1), ("L", 1)):
        ops += [
            ("UpperArm." + side, "X", -40 - 25 * reach),
            ("UpperArm." + side, "Z", -sgn * 28),
            ("LowerArm." + side, "X", -70 - 40 * (1 - reach)),
            ("LowerArm." + side, "Z", -sgn * 25),
        ]
    ops += [("Head", "X", [-6, -6, 12, -4][i])]
    return ops


def wash_pose(i):
    """Leans over the basin: hands reach down into the water, scoop it up to the bent face, splash."""
    bend = [34, 56, 46, 40][i]
    reach = [0.5, 1.0, 0.0, 0.1][i]       # 1 = hands down in the basin, 0 = hands at the face
    ops = [("Abdomen", "X", bend * 0.5), ("Torso", "X", bend * 0.5)]
    for side, sgn in (("R", -1), ("L", 1)):
        ops += [
            ("UpperArm." + side, "X", -35 - 40 * reach),
            ("UpperArm." + side, "Z", -sgn * (14 + 8 * reach)),
            ("LowerArm." + side, "X", -50 - 75 * (1 - reach) - (0 if i else 0)),
            ("LowerArm." + side, "Z", -sgn * 18),
        ]
    ops += [("Head", "X", [8, 14, 30, 26][i])]
    return ops


def read_pose(i):
    ops = [("Torso", "X", 6), ("Head", "X", [24, 26, 24, 28][i])]
    for side, sgn in (("R", -1), ("L", 1)):
        ops += [
            ("UpperArm." + side, "X", -50),
            ("UpperArm." + side, "Z", -sgn * 22),
            ("LowerArm." + side, "X", -85),
            ("LowerArm." + side, "Z", -sgn * 30),
        ]
    return ops


def search_pose(i):
    bend = [48, 58, 50, 60][i]
    ops = [("Abdomen", "X", bend * 0.55), ("Torso", "X", bend * 0.45), ("Head", "X", -18)]
    for side, sgn in (("R", -1), ("L", 1)):
        phase = [(1.0, 0.2), (0.4, 1.0), (1.0, 0.3), (0.2, 1.0)][i][0 if side == "R" else 1]
        ops += [
            ("UpperArm." + side, "X", -50 - 20 * phase),
            ("UpperArm." + side, "Z", -sgn * 8),
            ("LowerArm." + side, "X", -20 - 25 * (1 - phase)),
        ]
    return ops


# crouch depth, lean, arm reach per pickup frame: reach down, grab, rise holding the can, stand holding it
PICKUP = [(30, 22, -35), (62, 38, -20), (34, 14, -70), (0, 0, -60)]


def pickup_pose(i):
    th, lean, arm = PICKUP[i]
    ops = [("UpperLeg.R", "X", -th), ("UpperLeg.L", "X", -th), ("LowerLeg.R", "X", 2 * th), ("LowerLeg.L", "X", 2 * th),
           ("Foot.R", "X", -th), ("Foot.L", "X", -th),
           ("Abdomen", "X", lean * 0.5), ("Torso", "X", lean * 0.5), ("Head", "X", -lean * 0.5)]
    for side, sgn in (("R", -1), ("L", 1)):
        a = arm if side == "R" else (arm * 0.5 if i < 3 else -8)
        ops += [("UpperArm." + side, "X", a), ("UpperArm." + side, "Z", -sgn * 6)]
        if i == 3 and side == "R":
            ops += [("LowerArm.R", "X", -70)]
    return ops


def shower_pose(i):
    """Standing under the shower, head tilted back, both hands scrubbing hair and face (4 frames: hands up, back, forward, rinse)."""
    sway = [0, 1, 0, -1][i]
    ops = [("Torso", "X", -4), ("Head", "X", [-14, -18, -12, -20][i]), ("Abdomen", "Z", sway * 3)]
    for side, sgn in (("R", -1), ("L", 1)):
        lift = [1.0, 0.7, 1.0, 0.5][i]
        ops += [("UpperArm." + side, "X", -78 - 10 * lift),
                ("UpperArm." + side, "Z", -sgn * (22 + 5 * sway * sgn)),
                ("LowerArm." + side, "X", -118 - 14 * lift),
                ("LowerArm." + side, "Z", -sgn * 30)]
    return ops


def main():
    global SS
    argv = sys.argv[sys.argv.index("--") + 1:]
    fbx, out_dir = argv[0], argv[1]
    SS = int(argv[2])
    samples = int(argv[3])
    colours = json.loads(argv[4])
    only = argv[5].split(",") if len(argv) > 5 else ["eat", "drink", "read", "search", "wash", "pickup", "shower"]
    facings = argv[6].split(",") if len(argv) > 6 else list(FACINGS)
    os.makedirs(out_dir, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.render.film_transparent = True
    sc.render.filter_size = 1.0
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.color_mode = "RGBA"

    bpy.ops.import_scene.fbx(filepath=fbx)
    arm = next(o for o in sc.objects if o.type == "ARMATURE")
    meshes = [o for o in sc.objects if o.type == "MESH"]
    for m in bpy.data.materials:
        if m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
            bsdf = m.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Alpha"].default_value = 1.0
            bsdf.inputs["Roughness"].default_value = 0.65
            base = m.name.split(".")[0]
            if base in colours:
                bsdf.inputs["Base Color"].default_value = rgb(colours[base])

    idle = next(a for a in bpy.data.actions if a.name.endswith("_Idle"))
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

    # player V2 look + modelled face (same as blender_actor.py)
    face_kit.apply_proportions()
    player_look.apply(arm)
    face = face_kit.Face(sc, arm, "player", colours["Skin"], next(m for m in meshes if m.name == "BaseHuman"))
    face.build()
    face.make_anchors()
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()
    anchors = {}
    camfwd = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)),
                     math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))

    setup_camera(FRAME_W, FRAME_H, FEET_X, FEET_Y)
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

    # freeze the idle pose; from now on the pose is set by hand
    arm.animation_data.action = idle
    sc.frame_set(1)
    face_kit.player_pose_tweaks(arm)
    bpy.context.view_layer.update()
    arm.animation_data.action = None
    rig = Rig(arm)

    food = make_prop("sphere", "#c8893c", (0.17, 0.12, 0.10))
    bite = make_prop("sphere", "#e8c88c", (0.08, 0.07, 0.07))
    book = make_prop("cube", "#a8322c", (0.20, 0.27, 0.035))
    page_l = make_prop("cube", "#e0d4b0", (0.18, 0.25, 0.03))
    page_r = make_prop("cube", "#e0d4b0", (0.18, 0.25, 0.03))
    flip = make_prop("cube", "#e8dcb8", (0.18, 0.25, 0.012))
    water = make_prop("sphere", "#58a8e8", (0.16, 0.11, 0.05))
    drop = make_prop("sphere", "#90ccf8", (0.04, 0.04, 0.07))
    drop2 = make_prop("sphere", "#90ccf8", (0.04, 0.04, 0.07))
    can = make_prop("cube", "#c8d0d8", (0.07, 0.07, 0.12))
    streaks = [make_prop("cube", "#9fd4f8", (0.014, 0.014, 0.3)) for _ in range(14)]
    props = [can, food, bite, book, page_l, page_r, flip, water, drop, drop2] + streaks

    def shot(name):
        sc.render.filepath = os.path.join(out_dir, name)
        bpy.ops.render.render(write_still=True)

    ground = root.location.z
    for act in only:
        for fname in facings:
            root.rotation_euler = (0, 0, math.radians(FACINGS[fname]))
            for i in range(4):
                for p in props:
                    p.hide_render = True
                    p.hide_viewport = True
                ops = {"eat": eat_pose, "drink": drink_pose, "read": read_pose, "search": search_pose, "wash": wash_pose, "pickup": pickup_pose, "shower": shower_pose}[act](i)
                rig.pose(ops)
                k = rig.k
                if act == "pickup":
                    root.location.z = ground - 0.9 * (1 - math.cos(math.radians(PICKUP[i][0]))) * HEIGHT_M / 1.78
                if act == "eat":
                    hc = hand_centre(rig, "R")
                    rig.place(food, hc + Vector((0, -0.12, 0.05)) * k, [("X", 15)])
                    if i >= 2:
                        rig.place(bite, hc + Vector((0, -0.2, 0.07)) * k)
                elif act == "drink":
                    hc = (hand_centre(rig, "R") + hand_centre(rig, "L")) / 2
                    if i in (1, 2):
                        rig.place(water, hc + Vector((0, -0.04, 0.03)) * k)
                    if i == 3:
                        rig.place(drop, hc + Vector((0, -0.04, -0.08)) * k)
                elif act == "wash":
                    hc = (hand_centre(rig, "R") + hand_centre(rig, "L")) / 2
                    if i == 1:
                        rig.place(water, hc + Vector((0, -0.03, -0.05)) * k)
                    if i == 2:
                        rig.place(water, hc + Vector((0, -0.03, 0.03)) * k)
                    if i == 3:
                        rig.place(drop, hc + Vector((0.14, -0.06, -0.02)) * k)
                        rig.place(drop2, hc + Vector((-0.14, -0.08, -0.12)) * k)
                elif act == "shower":
                    # falling water: streaks on a ring round the body, shifted down per frame
                    for k, st in enumerate(streaks):
                        a = k * 2.4 + 0.5
                        rad = 0.2 + 0.1 * (k % 3)
                        z = 2.05 - ((k * 0.29 + i * 0.25) % 1.0) * 1.9
                        st.matrix_world = Matrix.Translation(Vector((math.cos(a) * rad, math.sin(a) * rad * 0.8, z)))
                        st.hide_render = False
                        st.hide_viewport = False
                elif act == "pickup":
                    hc = hand_centre(rig, "R")
                    if i == 0:
                        rig.place(can, hc * 0 + Vector((hc.x, hc.y - 0.12 * k, 0.04 * k)))
                    elif i == 1:
                        rig.place(can, hc + Vector((0, -0.02, 0.0)) * k)
                    else:
                        rig.place(can, hc + Vector((0, -0.02, 0.0)) * k)
                elif act == "read":
                    hc = (hand_centre(rig, "R") + hand_centre(rig, "L")) / 2
                    tilt = [("X", -62)]
                    base = hc + Vector((0, -0.05, 0.02)) * k
                    rig.place(book, base, tilt)
                    off = Vector((0.1, 0, 0)) * k
                    rig.place(page_l, base - off + Vector((0, -0.01, 0.025)) * k, tilt)
                    rig.place(page_r, base + off + Vector((0, -0.01, 0.025)) * k, tilt)
                    if i in (1, 2):
                        ang = [0, -30, -75, 0][i]
                        rig.place(flip, base + Vector((0.01, -0.012, 0.06)) * k, [("Y", ang), ("X", -62)])
                shot(f"{act}_{fname}_{i}.png")
                anchors[f"{act}_{fname}_{i}"] = face.project(sc.camera, camfwd, FRAME_W, FRAME_H)
    with open(os.path.join(out_dir, "anchors.json"), "w") as f:
        json.dump(anchors, f)


main()
