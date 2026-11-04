"""blender -b -noaudio --python faces.py -- <char> <outdir> <ss> <samples> <opt: base|A|C1|C2> <what: sprites|walk|portrait|all>
Renders cast sprites (idle 8 facings, optional walk frames) and expression portraits with modelled face features.
Writes <outdir>/<facing>_<frame>.png, <outdir>/anchors.json (projected face anchor points per sprite frame, in 32x64 frame px)
and <outdir>/portrait_<expr>.png (256x256)."""
import bpy, sys, os, math, json, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
KEEP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, KEEP)
import cast_snapshot as cdef

CELL_M = 0.75
FW_, FH_, FX, FY = 32, 64, 16, 54
FACINGS = {"s": 45, "sw": 0, "w": -45, "nw": -90, "n": -135, "ne": 180, "e": 135, "se": 90}
WALK_FACINGS = ["s", "sw", "se", "e"]

OPTS = {
    "base": dict(head=1.0, hand=1.0, face=False, size=1.0),
    "A":    dict(head=1.28, hand=1.38, face=True, size=1.0),
    "C1":   dict(head=1.45, hand=1.38, face=True, size=1.0),
    "C2":   dict(head=1.28, hand=1.38, face=True, size=1.10),
}
# per-character face look (colours); eyes sit where the model has its eye balls
FACE = {
    "player": dict(iris="#5a3a22", brow="#3a2214", lips="#b5605a", female=False, hair="#5a3420"),
    "mia":    dict(iris="#2f8a78", brow="#a24a1e", lips="#c4505a", female=True, hair="#c8622a"),
    "rosa":   dict(iris="#6f8fb0", brow="#8e8e98", lips="#b0505a", female=True, hair="#c4c4cc"),
    "victor": dict(iris="#2a1a10", brow="#e8e0c8", lips="#a8604a", female=False, hair="#f1ead4"),
}
EXPR = {
    "neutral": dict(brow_dy=0.0, brow_tilt=0, mouth_curve=0.0, mouth_open=0.0, lid=0.0, lid_tilt=0, squint=0.0, blush=0.35, teeth=False),
    "happy":   dict(brow_dy=0.025, brow_tilt=-4, mouth_curve=0.055, mouth_open=0.05, lid=0.14, lid_tilt=0, squint=0.0, blush=0.9, teeth=True),
    "angry":   dict(brow_dy=-0.03, brow_tilt=24, mouth_curve=-0.035, mouth_open=0.0, lid=0.30, lid_tilt=24, squint=0.0, blush=0.0, teeth=False),
    "sad":     dict(brow_dy=0.015, brow_tilt=-20, mouth_curve=-0.045, mouth_open=0.0, lid=0.32, lid_tilt=-12, squint=0.0, blush=0.0, teeth=False),
}

argv = sys.argv[sys.argv.index("--") + 1:]
cname, out_dir, ss, samples, optname, what = argv[0], argv[1], int(argv[2]), int(argv[3]), argv[4], argv[5]
O = OPTS[optname]
C = cdef.CHARS[cname]
F = FACE[cname]
os.makedirs(out_dir, exist_ok=True)

def hexc(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c]
    return (c[0], c[1], c[2], 1)
def shade(h, f):
    h = h.lstrip("#"); c = [min(255, max(0, int(int(h[i:i + 2], 16) * f))) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(c)
def mix(a, b, t):
    a = a.lstrip("#"); b = b.lstrip("#")
    c = [int(int(a[i:i + 2], 16) * (1 - t) + int(b[i:i + 2], 16) * t) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(c)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = samples; sc.cycles.use_denoising = False
sc.render.film_transparent = True; sc.render.filter_size = 1.0
sc.view_settings.view_transform = "Standard"
sc.render.image_settings.color_mode = "RGBA"

def mat(col, rough=0.6):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(col); b.inputs["Roughness"].default_value = rough
    return m

def prim(kind, pos, size, col, parent, rot=(0, 0, 0)):
    if kind == "box": bpy.ops.mesh.primitive_cube_add(size=1)
    elif kind == "cyl": bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, vertices=32)
    elif kind == "sphere": bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16)
    elif kind == "torus": bpy.ops.mesh.primitive_torus_add(major_radius=size[0], minor_radius=size[2], major_segments=40, minor_segments=8)
    o = bpy.context.active_object
    if kind == "torus": o.scale = (1, size[1] / size[0], 1)
    else: o.scale = size
    o.location = pos; o.rotation_euler = [math.radians(a) for a in rot]
    if kind != "box": bpy.ops.object.shade_smooth()
    o.data.materials.append(mat(col, 0.65)); o.parent = parent
    return o

# ---------------------------------------------------------------- character (same set-up as tools/blender_cast.py)
pivot = bpy.data.objects.new("pivot", None); sc.collection.objects.link(pivot)
body = bpy.data.objects.new("body", None); sc.collection.objects.link(body); body.parent = pivot
k = C["height"] / 1.78 * O["size"]
body.scale = (k * C.get("widen", 1.0), k * C.get("depth", 1.0), k)
bpy.ops.import_scene.fbx(filepath="/home/user/Town-Life/art_source/quaternius_characters/%s.fbx" % C["model"])
arm = next(o for o in sc.objects if o.type == "ARMATURE")
meshes = [o for o in sc.objects if o.type == "MESH"]
mesh_o = next(o for o in meshes if o.name in ("BaseHuman", "Female"))
for m in list(bpy.data.materials):
    if m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Alpha"].default_value = 1.0; b.inputs["Roughness"].default_value = 0.65
        base = m.name.split(".")[0]
        if base in C["colours"]:
            for l in list(m.node_tree.links):
                if l.to_socket == b.inputs["Base Color"]: m.node_tree.links.remove(l)
            b.inputs["Base Color"].default_value = hexc(C["colours"][base])
idle = next(a for a in bpy.data.actions if a.name.endswith("_Idle"))
walk = next(a for a in bpy.data.actions if a.name.endswith("_Walk"))
arm.animation_data_create(); arm.animation_data.action = idle
sc.frame_set(1); bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get(); zs = []
for o in meshes:
    ev = o.evaluated_get(deps); me = ev.to_mesh()
    zs += [(ev.matrix_world @ v.co).z for v in me.vertices]; ev.to_mesh_clear()
s = 1.78 / (max(zs) - min(zs))
root = bpy.data.objects.new("root", None); sc.collection.objects.link(root)
arm.parent = root; root.parent = body
root.scale = (s, s, s); root.location = (0, 0, -min(zs) * s)

def parent_bone(obj, bone):
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    obj.parent = arm; obj.parent_type = "BONE"; obj.parent_bone = bone
    bpy.context.view_layer.update()
    pb = arm.pose.bones[bone]
    pm = arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
    obj.matrix_parent_inverse = pm.inverted(); obj.matrix_world = mw

def scale_keys(bone, kk):
    for act in bpy.data.actions:
        for fc in act.fcurves:
            if fc.data_path == 'pose.bones["%s"].scale' % bone:
                for kp in fc.keyframe_points:
                    kp.co[1] *= kk; kp.handle_left[1] *= kk; kp.handle_right[1] *= kk
                fc.update()

arm.data.pose_position = "REST"; bpy.context.view_layer.update()
props = []
for p in C["props"]:
    o = prim(p[0], p[1], p[2], p[3], body, rot=(p[4] if len(p) > 4 else (0, 0, 0)))
    props.append((o, p))
bpy.context.view_layer.update()
GLASSES = []
for o, p in props:                       # head props follow the (scaled) head bone
    if p[1][2] > 1.55:
        parent_bone(o, "Head")
        if p[3] in ("#0c0c10", "#2a2a30"): GLASSES.append(o)       # sunglasses / Rosa's glasses (replaced by fitted ones in face options)
if O["head"] != 1.0:
    scale_keys("Head", O["head"])
if O["hand"] != 1.0:
    for sd in "LR": scale_keys("Palm." + sd, O["hand"])

# ---------------------------------------------------------------- face features
me = mesh_o.data
head_i = mesh_o.vertex_groups["Head"].index
def in_head(v): return any(g.group == head_i and g.weight > 0.5 for g in v.groups)
head_vs = {v.index for v in me.vertices if in_head(v)}
head_polys = [p for p in me.polygons if all(vi in head_vs for vi in p.vertices)]
bvh = BVHTree.FromPolygons([v.co[:] for v in me.vertices], [p.vertices[:] for p in head_polys])
hair_polys = [p for p in head_polys if me.materials[p.material_index].name.split(".")[0] in ("Hair", "HairBase")]
bvh_hair = BVHTree.FromPolygons([v.co[:] for v in me.vertices], [p.vertices[:] for p in hair_polys]) if hair_polys else None
eyes_c = [p.center for p in me.polygons if me.materials[p.material_index].name.split(".")[0] == "Eyes" and p.center.z > 3]
EX = abs(sum(c.x for c in eyes_c if c.x > 0) / max(1, len([c for c in eyes_c if c.x > 0])))
EZ = sum(c.z for c in eyes_c) / len(eyes_c)
SKIN = C["colours"]["Skin"]
SKIN_D = mix(SKIN, "#6a2a2a", 0.30)
FEATS = []     # created face objects

def surf_y(x, z, default=-0.24):
    h = bvh.ray_cast(Vector((x, -3, z)), Vector((0, 1, 0)))
    return h[0].y if h[0] is not None else default

def add(kind, loc, size, col, rot=(0, 0, 0), seg=12):
    """Place an object in armature rest coordinates (REST pose) and glue it to the Head bone."""
    if kind == "sphere": bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=max(6, seg // 2), radius=1)
    elif kind == "cyl": bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=1, depth=2)
    elif kind == "torus": bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.10, major_segments=32, minor_segments=8)
    else: bpy.ops.mesh.primitive_cube_add(size=2)
    o = bpy.context.object
    kk = arm.matrix_world.to_scale()[0]
    o.scale = (size[0] * kk, size[1] * kk, size[2] * kk)
    o.rotation_euler = rot
    o.location = arm.matrix_world @ Vector(loc)
    o.data.materials.append(mat(col, 0.5))
    if kind != "box": bpy.ops.object.shade_smooth()
    parent_bone(o, "Head"); FEATS.append(o)
    return o

def anchor(name, loc):
    e = bpy.data.objects.new("anc_" + name, None); sc.collection.objects.link(e)
    e.location = arm.matrix_world @ Vector(loc); parent_bone(e, "Head"); e.name = "anc_" + name
    return e

def surface_frame(origin, direction, bv):
    h = bv.ray_cast(origin, direction)
    return (h[0], h[1]) if h[0] is not None else (None, None)

def build_face(ex):
    """ex = expression dict. Everything in armature rest space (units ~0.356 m)."""
    for o in FEATS:
        bpy.data.objects.remove(o, do_unlink=True)
    FEATS.clear()
    arm.data.pose_position = "REST"; bpy.context.view_layer.update()
    fem = F["female"]
    for sx in (-1, 1):
        x = sx * EX; z = EZ; y0 = surf_y(x, z)
        # eye: white, iris, pupil, highlight
        add("sphere", (x, y0 + 0.020, z), (0.058, 0.026, 0.041), "#f7f3ec", seg=16)
        add("sphere", (x * 0.97, y0 - 0.004, z - 0.002), (0.034, 0.012, 0.034), F["iris"], seg=14)
        add("sphere", (x * 0.97, y0 - 0.011, z - 0.002), (0.018, 0.008, 0.018), "#0b0a0e", seg=10)
        add("sphere", (x * 0.97, y0 - 0.017, z + 0.014), (0.008, 0.004, 0.008), "#ffffff", seg=8)
        # upper lash line (thicker for the female looks)
        add("box", (x, y0 - 0.002, z + 0.040), (0.062, 0.010, 0.0075 if not fem else 0.011), "#1a1418")
        if fem: add("box", (x + sx * 0.055, y0 - 0.002, z + 0.046), (0.014, 0.008, 0.006), "#1a1418", rot=(0, sx * 0.5, 0))
        # eyelids (skin) for angry / sad, squint (lower lid) for happy
        if ex["lid"] > 0:
            ht = 0.04
            zc = z + 0.042 - ex["lid"] * 0.085
            tilt = -sx * math.radians(ex["lid_tilt"] * 0.55)
            add("box", (x, y0 - 0.008, zc + ht), (0.060, 0.007, ht), SKIN, rot=(0, tilt, 0))
            add("box", (x, y0 - 0.014, zc), (0.060, 0.005, 0.0065), "#241a1c", rot=(0, tilt, 0))
        if ex["squint"] > 0:
            zb = z - 0.05 + ex["squint"] * 0.10
            add("box", (x, y0 - 0.008, zb - 0.025), (0.048, 0.006, 0.025), SKIN, rot=(0, sx * math.radians(-8), 0))
        # eyebrow
        by = surf_y(x, z + 0.12) - 0.006
        add("box", (x + sx * 0.005, by, z + 0.125 + ex["brow_dy"]), (0.080 if not fem else 0.074, 0.013, 0.016 if not fem else 0.011),
            F["brow"], rot=(0, -sx * math.radians(ex["brow_tilt"]), 0))
        # cheek blush
        if ex["blush"] > 0:
            cy = surf_y(x * 1.25, z - 0.115)
            add("sphere", (x * 1.2, cy + 0.003, z - 0.115), (0.055, 0.010, 0.036), mix(SKIN, "#ff6a78", 0.06 + 0.26 * ex["blush"]), seg=12)
        # ear detail (inner ear)
        hx = Vector((sx * 3, 0.02, EZ - 0.05)); hit = bvh.ray_cast(hx, Vector((-sx, 0, 0)))
        if hit[0] is not None:
            add("sphere", (hit[0].x - sx * 0.004, 0.02, EZ - 0.05), (0.012, 0.045, 0.06), SKIN_D, seg=10)
    # nose shading: shadow under the tip + nostrils
    tip = min((mesh_o.data.vertices[i].co for i in head_vs if abs(mesh_o.data.vertices[i].co.x) < 0.05 and EZ - 0.25 < mesh_o.data.vertices[i].co.z < EZ), key=lambda c: c.y)
    add("box", (0, tip.y + 0.012, tip.z - 0.045), (0.075, 0.012, 0.012), SKIN_D)
    for sx in (-1, 1): add("sphere", (sx * 0.028, tip.y + 0.004, tip.z - 0.026), (0.011, 0.009, 0.009), "#3a1c1c", seg=8)
    add("box", (0, surf_y(0, EZ - 0.02) - 0.004, EZ - 0.04), (0.006, 0.005, 0.07), mix(SKIN, "#ffffff", 0.14))   # nose bridge highlight
    # mouth
    zm = tip.z - 0.115 - ex["mouth_open"] * 0.2
    W = 0.085 if not F["female"] else 0.075
    n = 7
    lip = F["lips"]
    pts = []
    for i in range(n + 1):
        t = -1 + 2 * i / n
        pts.append((t * W, zm + ex["mouth_curve"] * (t * t - 0.35)))
    if ex["mouth_open"] > 0:
        xc = 0; yv = surf_y(0, zm) - 0.004
        add("box", (0, yv + 0.004, zm - ex["mouth_open"] * 0.35), (W * 0.82, 0.010, ex["mouth_open"] * 0.55 + 0.01), "#3a1214")
        if ex["teeth"]:
            add("box", (0, yv - 0.005, zm - 0.012), (W * 0.74, 0.006, 0.012), "#fbf8f0")
        add("box", (0, yv - 0.003, zm - ex["mouth_open"] * 0.75), (W * 0.45, 0.006, 0.007), "#d05a62")
    for i in range(n):
        (xa, za), (xb, zb) = pts[i], pts[i + 1]
        xm, zmid = (xa + xb) / 2, (za + zb) / 2
        ang = math.atan2(zb - za, xb - xa)
        yv = surf_y(xm, zmid) - 0.008
        add("box", (xm, yv, zmid), (abs(xb - xa) / 2 + 0.004, 0.009, 0.0075 if not F["female"] else 0.0095), mix(lip, "#3a1a1a", 0.35) if ex["mouth_open"] == 0 else "#5a1c22", rot=(0, -ang, 0))
    if ex["mouth_open"] == 0 and F["female"]:      # fuller lower lip
        add("box", (0, surf_y(0, zm - 0.02) - 0.008, zm - 0.02 + ex["mouth_curve"] * -0.1), (W * 0.55, 0.008, 0.009), mix(lip, "#ffffff", 0.25))
    # hair detail: strands (dark) + highlights (light) following the surface
    if bvh_hair is not None:
        rnd = random.Random(7)
        hc = F["hair"]
        dark, light = shade(hc, 0.68), mix(hc, "#ffffff", 0.42)
        def strand(origin, direction, col, w, ln):
            loc, nrm = surface_frame(origin, direction, bvh_hair)
            if loc is None: return
            down = Vector((0, 0, -1)); tg = (down - nrm * down.dot(nrm))
            if tg.length < 0.2: tg = Vector((0, 1, 0)) - nrm * nrm.y   # on top: run front-to-back
            tg.normalize(); xx = tg.cross(nrm).normalized()
            mrot = Matrix((xx, tg, nrm)).transposed()
            kk = arm.matrix_world.to_scale()[0]
            bpy.ops.mesh.primitive_cube_add(size=2)
            o = bpy.context.object
            o.scale = (w * kk, ln * kk, 0.007 * kk)
            o.rotation_euler = mrot.to_euler(); o.location = arm.matrix_world @ (loc - nrm * 0.002)
            o.data.materials.append(mat(col, 0.45)); parent_bone(o, "Head"); FEATS.append(o)
        top = max(v.co.z for v in me.vertices if v.index in head_vs)
        for i in range(13):                                  # strands across the crown / fringe from above
            x = -0.21 + 0.035 * i + rnd.uniform(-0.01, 0.01)
            strand(Vector((x, -0.05 + rnd.uniform(-0.1, 0.05), top + 1)), Vector((0, 0, -1)), dark if i % 2 else light, 0.010, rnd.uniform(0.03, 0.05))
        for i in range(7):                                  # fringe strands from the front
            x = -0.16 + 0.053 * i
            strand(Vector((x, -3, EZ + 0.23 + rnd.uniform(0, 0.12))), Vector((0, 1, 0)), light if i % 2 else dark, 0.009, rnd.uniform(0.03, 0.05))
        for sx in (-1, 1):                                  # side sheen
            strand(Vector((sx * 3, 0.0, EZ + 0.30)), Vector((-sx, 0, 0)), light, 0.010, 0.05)
    # glasses fitted to the (scaled) face; the old props are hidden when the face is modelled
    for g in GLASSES: g.hide_render = True
    if cname == "victor" and not ex.get("noglasses", False):
        for sx in (-1, 1):
            x = sx * EX; y0 = surf_y(x, EZ)
            add("box", (x, y0 - 0.032, EZ + 0.005), (0.092, 0.012, 0.056), "#101016")
            add("box", (x - sx * 0.02, y0 - 0.046, EZ + 0.025), (0.030, 0.003, 0.010), "#7a8a9a", rot=(0, sx * 0.4, 0))
            add("box", (x, y0 - 0.032, EZ + 0.064), (0.095, 0.014, 0.008), "#f2c94c")        # gold top rim
            add("box", (sx * (EX + 0.12), 0.0, EZ + 0.0), (0.008, 0.16, 0.012), "#f2c94c")      # arm towards the ear
        add("box", (0, surf_y(0, EZ + 0.02) - 0.03, EZ + 0.03), (0.04, 0.010, 0.010), "#f2c94c")
    if cname == "rosa":
        for sx in (-1, 1):
            x = sx * EX; y0 = surf_y(x, EZ)
            add("torus", (x, y0 - 0.03, EZ + 0.005), (0.078, 0.078, 0.078), "#2a2a30", rot=(math.pi / 2, 0, 0))
        add("box", (0, surf_y(0, EZ + 0.02) - 0.03, EZ + 0.02), (0.05, 0.008, 0.008), "#2a2a30")
        for sx in (-1, 1): add("box", (sx * (EX + 0.15), 0.0, EZ + 0.01), (0.007, 0.16, 0.008), "#2a2a30")
    # anchors (empties) for the pixel pass; make once
    return

ANCH = {}
def make_anchors():
    arm.data.pose_position = "REST"; bpy.context.view_layer.update()
    tip = min((me.vertices[i].co for i in head_vs if abs(me.vertices[i].co.x) < 0.05 and EZ - 0.25 < me.vertices[i].co.z < EZ), key=lambda c: c.y)
    ys = lambda x, z: surf_y(x, z) - 0.035
    zm = tip.z - 0.115
    ANCH["eyeP"] = anchor("eyeP", (EX, ys(EX, EZ), EZ))          # character's left (+x)
    ANCH["eyeM"] = anchor("eyeM", (-EX, ys(-EX, EZ), EZ))
    ANCH["browP"] = anchor("browP", (EX, ys(EX, EZ + 0.125), EZ + 0.125))
    ANCH["browM"] = anchor("browM", (-EX, ys(-EX, EZ + 0.125), EZ + 0.125))
    ANCH["mouth"] = anchor("mouth", (0, ys(0, zm), zm))
    ANCH["mouthP"] = anchor("mouthP", (0.08, ys(0.08, zm), zm))
    ANCH["mouthM"] = anchor("mouthM", (-0.08, ys(-0.08, zm), zm))
    ANCH["nose"] = anchor("nose", (0, tip.y - 0.03, tip.z - 0.03))
    ANCH["cheekP"] = anchor("cheekP", (EX * 1.25, ys(EX * 1.25, EZ - 0.115), EZ - 0.115))
    ANCH["cheekM"] = anchor("cheekM", (-EX * 1.25, ys(-EX * 1.25, EZ - 0.115), EZ - 0.115))
    top = max(me.vertices[i].co.z for i in head_vs)
    ANCH["crown"] = anchor("crown", (-0.10, -0.12, top + 0.03))     # for a hair highlight pixel
    ANCH["chin"] = anchor("chin", (0, -0.2, EZ - 0.33))
    ANCH["headtop"] = anchor("headtop", (0, 0.1, top + 0.03))

# ---------------------------------------------------------------- camera / lights
world = bpy.data.worlds.new("world"); sc.world = world; world.use_nodes = True
def setup_cam_sprite():
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
    return co, fwd

def project_anchors(co, fwd):
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    res = {}
    fn = fwd.normalized()
    for name, e in ANCH.items():
        p = e.matrix_world.translation.copy()
        nv = world_to_camera_view(sc, co, p)
        origin = p - fn * 10
        hit, loc, nrm, idx, ob, mw = sc.ray_cast(deps, origin, fn, distance=10.5)
        vis = hit and (loc - origin).length > 10 - 0.03
        res[name] = [round(nv.x * FW_, 3), round((1 - nv.y) * FH_, 3), bool(vis)]
    return res

anchors_out = {}
def shot(path):
    sc.render.filepath = os.path.join(out_dir, path); bpy.ops.render.render(write_still=True)

if what in ("sprites", "walk", "all"):
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.66, 0.8, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.5; sun.angle = math.radians(10)
    so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
    so.rotation_euler = Vector((-0.25, 0.7, -0.65)).normalized().to_track_quat("-Z", "Y").to_euler()
    co, fwd = setup_cam_sprite()
    if O["face"]:
        build_face(EXPR["neutral"])
    make_anchors()
    arm.data.pose_position = "POSE"; bpy.context.view_layer.update()
    for fname, angle in FACINGS.items():
        pivot.rotation_euler = (0, 0, math.radians(angle))
        arm.animation_data.action = idle; sc.frame_set(1)
        shot(f"{fname}_0.png"); anchors_out[f"{fname}_0"] = project_anchors(co, fwd)
    if what in ("walk", "all"):
        w0, w1 = int(walk.frame_range[0]), int(walk.frame_range[1]); cyc = w1 - w0
        arm.animation_data.action = walk
        for fname in WALK_FACINGS:
            pivot.rotation_euler = (0, 0, math.radians(FACINGS[fname]))
            for i in range(8):
                sc.frame_set(w0 + round(i * cyc / 8))
                shot(f"{fname}_{i + 1}.png"); anchors_out[f"{fname}_{i + 1}"] = project_anchors(co, fwd)
    json.dump(anchors_out, open(os.path.join(out_dir, "anchors.json"), "w"))
    bpy.data.objects.remove(so)
    for o in [o for o in sc.objects if o.type == "CAMERA"]: bpy.data.objects.remove(o)

if what in ("portrait", "all"):
    arm.data.pose_position = "POSE"
    res = 256
    sc.render.resolution_x = sc.render.resolution_y = res
    FWp, ptop = C.get("pcam", (0.62, 1.78))
    FWp += 0.04 * (O["head"] - 1) / 0.28 * 0.6; ptop += 0.05 * (O["head"] - 1) / 0.28
    ZC = ptop * k - FWp * 0.40
    cam = bpy.data.cameras.new("c"); cam.type = "ORTHO"; cam.ortho_scale = FWp
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
    pivot.rotation_euler = (0, 0, math.radians(22.0))
    exprs = ["neutral", "happy", "angry", "sad"]
    for en in exprs:
        ex = dict(EXPR[en])
        if cname == "victor" and en in ("angry", "sad"): ex["noglasses"] = True
        if O["face"]:
            build_face(ex)
        else:
            for g in GLASSES: g.hide_render = ex.get("noglasses", False)
        arm.data.pose_position = "POSE"; arm.animation_data.action = idle; sc.frame_set(1)
        shot(f"portrait_{en}.png")
        if not O["face"]: break
