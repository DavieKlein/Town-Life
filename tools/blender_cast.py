"""
Town Life - cast renderer (runs INSIDE Blender, called by tools/build_assets.py; ported from the approved proposal).

  blender -b -noaudio --python tools/blender_cast.py -- <name> <outdir> <ss> <samples> <sprites|portrait|both> [portrait yaw]

Writes <outdir>/<facing>_0.png (idle, 8 facings, 32x64 frames x ss, feet at (16, 54)) and <outdir>/portrait.png (256x256).
The look comes from tools/cast.py.
"""
import bpy, sys, os, math, json
from mathutils import Vector
TOOLS = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TOOLS)
from blender_render import rgb
import cast as cdef
import face_kit
CELL_M = 0.75
FW_, FH_, FX, FY = 32, 64, 16, 54
FACINGS = {"s": 45, "sw": 0, "w": -45, "nw": -90, "n": -135, "ne": 180, "e": 135, "se": 90}

argv = sys.argv[sys.argv.index("--") + 1:]
name, out_dir, ss, samples, mode = argv[0], argv[1], int(argv[2]), int(argv[3]), argv[4]
pyaw = float(argv[5]) if len(argv) > 5 else 22.0
C = cdef.CHARS[name]
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = samples; sc.cycles.use_denoising = False
sc.render.film_transparent = True; sc.render.filter_size = 1.0
sc.view_settings.view_transform = "Standard"
sc.render.image_settings.color_mode = "RGBA"

def mat(col, rough=0.6, emit=0.0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(col); b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = rgb(col); b.inputs["Emission Strength"].default_value = emit
    return m

def prim(kind, pos, size, col, parent, rough=0.6, emit=0.0, rot=(0, 0, 0)):
    if kind == "box": bpy.ops.mesh.primitive_cube_add(size=1)
    elif kind == "cyl": bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, vertices=32)
    elif kind == "cone": bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=1, vertices=32)
    elif kind == "tcone": bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0.72, depth=1, vertices=32)
    elif kind == "sphere": bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16)
    elif kind == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=size[0], minor_radius=size[2], major_segments=40, minor_segments=8)
    o = bpy.context.active_object
    if kind == "torus": o.scale = (1, size[1] / size[0], 1)
    else: o.scale = size
    o.location = pos; o.rotation_euler = [math.radians(a) for a in rot]
    if kind != "box": bpy.ops.object.shade_smooth()
    o.data.materials.append(mat(col, rough, emit)); o.parent = parent
    return o

def build_robot(parent):
    W, G, D = "#eceff2", "#e2b53a", "#3c424c"
    prim("cyl", (0, 0, 0.065), (0.23, 0.23, 0.07), W, parent)                 # hover base
    prim("cyl", (0, 0, 0.105), (0.235, 0.235, 0.025), G, parent)              # gold ring
    prim("cyl", (0, 0, 0.04), (0.17, 0.17, 0.02), "#35d6ff", parent, emit=1.5)  # hover glow
    prim("tcone", (0, 0, 0.46), (0.21, 0.21, 0.62), W, parent)                # tapered body
    prim("cyl", (0, 0, 0.42), (0.178, 0.178, 0.06), G, parent)               # gold stripe
    prim("box", (0, -0.15, 0.58), (0.11, 0.03, 0.09), "#10202c", parent)     # chest panel
    prim("box", (-0.03, -0.168, 0.58), (0.025, 0.01, 0.025), "#35d6ff", parent, emit=1.5)
    prim("box", (0.03, -0.168, 0.58), (0.025, 0.01, 0.025), "#ff9a4a", parent, emit=1.5)
    for sx in (-1, 1):                                                         # arms with claws
        prim("cyl", (sx * 0.215, 0, 0.56), (0.03, 0.03, 0.30), D, parent, rot=(0, sx * -12, 0))
        prim("sphere", (sx * 0.245, 0, 0.40), (0.05, 0.05, 0.05), W, parent)
        prim("box", (sx * 0.25, -0.03, 0.36), (0.05, 0.025, 0.045), G, parent)
    prim("cyl", (0, 0, 0.82), (0.05, 0.05, 0.08), D, parent)                  # neck
    prim("cone", (-0.05, -0.06, 0.80), (0.05, 0.03, 0.05), G, parent, rot=(0, 90, 0))  # bow tie
    prim("cone", (0.05, -0.06, 0.80), (0.05, 0.03, 0.05), G, parent, rot=(0, -90, 0))
    prim("sphere", (0, 0, 1.03), (0.20, 0.18, 0.17), W, parent)               # head
    prim("box", (0, -0.17, 1.04), (0.25, 0.05, 0.16), "#050b16", parent, rough=1.0)  # screen
    for sx in (-1, 1): prim("cyl", (sx * 0.065, -0.2, 1.075), (0.03, 0.03, 0.012), "#35d6ff", parent, emit=1.2, rot=(90, 0, 0))  # eyes
    for (x, z) in [(-0.07, 1.0), (-0.035, 0.978), (0.0, 0.972), (0.035, 0.978), (0.07, 1.0)]:  # smile
        prim("cyl", (x, -0.2, z), (0.012, 0.012, 0.012), "#35d6ff", parent, emit=1.2, rot=(90, 0, 0))
    prim("cyl", (0, 0, 1.25), (0.012, 0.012, 0.14), D, parent)                # antenna
    prim("sphere", (0, 0, 1.33), (0.035, 0.035, 0.035), G, parent, emit=0.6)
    for sx in (-1, 1): prim("cyl", (sx * 0.2, 0, 1.03), (0.04, 0.04, 0.05), G, parent, rot=(0, 90, 0))  # ear discs

pivot = bpy.data.objects.new("pivot", None); sc.collection.objects.link(pivot)
body = bpy.data.objects.new("body", None); sc.collection.objects.link(body); body.parent = pivot
k = C["height"] / 1.78
if C.get("model") == "ROBOT":
    body.scale = (1, 1, 1)
    build_robot(body)
    meshes_h = C["height"]
    k = 1.0
else:
    body.scale = (k * C.get("widen", 1.0), k * C.get("depth", 1.0), k)
    fbx = os.path.join(TOOLS, "..", "art_source", "quaternius_characters", C["model"] + ".fbx")
    bpy.ops.import_scene.fbx(filepath=fbx)
    arm = next(o for o in sc.objects if o.type == "ARMATURE")
    meshes = [o for o in sc.objects if o.type == "MESH" and o.parent == arm or o.type == "MESH"]
    meshes = [o for o in sc.objects if o.type == "MESH" and not o.get("tl_prop")]
    for m in list(bpy.data.materials):
        if m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
            bsdf = m.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Alpha"].default_value = 1.0; bsdf.inputs["Roughness"].default_value = 0.65
            base = m.name.split(".")[0]
            if base in C["colours"]:
                # TieTexture etc. may have a texture linked: unlink Base Color first
                for l in list(m.node_tree.links):
                    if l.to_socket == bsdf.inputs["Base Color"]: m.node_tree.links.remove(l)
                bsdf.inputs["Base Color"].default_value = rgb(C["colours"][base])
    arm.animation_data_create()
    arm.animation_data.action = next(a for a in bpy.data.actions if a.name.endswith("_Idle"))
    sc.frame_set(1); bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get(); zs = []
    for o in meshes:
        ev = o.evaluated_get(deps); me = ev.to_mesh()
        zs += [(ev.matrix_world @ v.co).z for v in me.vertices]; ev.to_mesh_clear()
    s = 1.78 / (max(zs) - min(zs))
    root = bpy.data.objects.new("root", None); sc.collection.objects.link(root)
    arm.parent = root; root.parent = body
    root.scale = (s, s, s); root.location = (0, 0, -min(zs) * s)
    FACE = None
    props = [(prim(p[0], p[1], p[2], p[3], body, rot=(p[4] if len(p) > 4 else (0, 0, 0))), p) for p in C["props"]]
    if mode == "sprites":
        # sprites get the s54 face (option B): player-V2 head / hand proportions, modelled face glued to the head bone.
        # (portraits keep the unchanged look until a new portrait proposal is approved)
        bpy.context.view_layer.update()
        FACE = face_kit.Face(sc, arm, name, C["colours"]["Skin"], meshes[0])
        for o, p in props:                       # head props (caps, hats, glasses, buns) follow the scaled head bone
            if p[1][2] > 1.55:
                face_kit.parent_bone(arm, o, "Head")
                if p[3] in ("#0c0c10", "#2a2a30") and cdef.CHARS[name].get("model") != "ROBOT" and name in ("rosa", "victor"):
                    FACE.glasses.append(o)
        face_kit.apply_proportions()
        FACE.build()
        FACE.make_anchors()
        arm.data.pose_position = "POSE"

# lighting like the actors
world = bpy.data.worlds.new("world"); sc.world = world; world.use_nodes = True

def setup_cam_sprite(co=None):
    sc.render.resolution_x = FW_ * ss; sc.render.resolution_y = FH_ * ss
    cam = bpy.data.cameras.new("cam"); cam.type = "ORTHO"; cam.sensor_fit = "HORIZONTAL"
    co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    co.data.ortho_scale = FW_ * math.cos(math.radians(45)) * CELL_M / 16
    co.rotation_euler = (math.radians(60), 0, math.radians(45))
    a = FW_ / 2 - FX; b = FH_ / 2 - FY
    ux, uy = b + a / 2, b - a / 2
    target = Vector((ux / 16 * CELL_M, -uy / 16 * CELL_M, 0))
    fwd = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)), math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))
    co.location = target - fwd * 40
    return co

FACE = globals().get("FACE")
if mode in ("sprites", "both"):
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.66, 0.8, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.5; sun.angle = math.radians(10)
    so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
    so.rotation_euler = Vector((-0.25, 0.7, -0.65)).normalized().to_track_quat("-Z", "Y").to_euler()
    cam_o = setup_cam_sprite()
    camfwd = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)), math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))
    anchors = {}
    # sprites of humans also get the 8-frame walk cycle (frames 1..8, like the player); the robot hovers (idle only)
    walk = None
    if mode == "sprites" and C.get("model") != "ROBOT":
        walk = next(a for a in bpy.data.actions if a.name.endswith("_Walk"))
        idle_act = next(a for a in bpy.data.actions if a.name.endswith("_Idle"))
        w0, w1 = int(walk.frame_range[0]), int(walk.frame_range[1])
    for fname, angle in FACINGS.items():
        pivot.rotation_euler = (0, 0, math.radians(angle))
        if walk is not None:
            arm.animation_data.action = idle_act
        sc.frame_set(1)
        sc.render.filepath = os.path.join(out_dir, f"{fname}_0.png")
        bpy.ops.render.render(write_still=True)
        if FACE is not None:
            anchors[f"{fname}_0"] = FACE.project(cam_o, camfwd, FW_, FH_)
        if walk is not None:
            arm.animation_data.action = walk
            for i in range(8):
                sc.frame_set(w0 + round(i * (w1 - w0) / 8))
                sc.render.filepath = os.path.join(out_dir, f"{fname}_{i + 1}.png")
                bpy.ops.render.render(write_still=True)
                if FACE is not None:
                    anchors[f"{fname}_{i + 1}"] = FACE.project(cam_o, camfwd, FW_, FH_)
    if FACE is not None:
        json.dump(anchors, open(os.path.join(out_dir, "anchors.json"), "w"))
    # remove sprite sun for portrait
    bpy.data.objects.remove(so)

if mode in ("portrait", "both"):
    res = 256
    sc.render.resolution_x = sc.render.resolution_y = res
    FW, ptop = C.get("pcam", (0.62, 1.78))
    ZC = ptop * k - FW * 0.40
    for o in [o for o in sc.objects if o.type == "CAMERA"]: bpy.data.objects.remove(o)
    cam = bpy.data.cameras.new("c"); cam.type = "ORTHO"; cam.ortho_scale = FW
    co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
    co.location = (0, -6, ZC); co.rotation_euler = (math.radians(90), 0, 0)
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.62, 0.8, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    def light(kind, e, loc, col, size=1.0):
        l = bpy.data.lights.new("l", kind); l.energy = e; l.color = col
        if kind == "AREA": l.size = size
        o = bpy.data.objects.new("l", l); sc.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector((0, 0, ZC)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    light("AREA", 170, (-2.2, -2.6, ZC + 1.4), (1, 0.95, 0.88), 1.8)
    light("AREA", 260, (2.4, 1.8, ZC + 0.8), (0.6, 0.75, 1.0), 1.0)
    light("AREA", 40, (1.8, -2.5, ZC), (1, 0.85, 0.8), 2)
    pivot.rotation_euler = (0, 0, math.radians(pyaw))
    sc.render.filepath = os.path.join(out_dir, "portrait.png")
    bpy.ops.render.render(write_still=True)
