"""
Town Life - unique character builds + realistic faces (runs INSIDE Blender; owner-approved s72 proposal, V1 Soft actor rendering).
Used by blender_cast.py (NPCs), blender_actor.py and blender_acts.py (player). The per-character table is tools/char_build.py.

  load(sc, name, fbx_path)   imports the rig, recolours, applies the BODY BUILD (belly / girth / hips / bust) in the rest pose,
                             measures + scales, returns a dict (arm, meshes, body_mesh, pivot, body, root, BD)
  dress(L, sc)               head / hand proportions, props, Face72 (+ anchors), clothing / hair extras, V1 Soft (smooth + 1 subdivision)
  tweak(arm, BD)             per-frame posture (shoulders, chest depth, lean, arm length): call after EVERY frame_set
  soft_world(sc) / soft_sun(sc)   V1 Soft light: stronger sky fill, wider (softer) key light, wider pixel filter
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
from blender_render import rgb  # noqa: E402
import face_kit  # noqa: E402
from face_kit import hexc, mix, shade, parent_bone  # noqa: E402
import player_look  # noqa: E402
import char_build  # noqa: E402


def smooth(t):
    return max(0.0, min(1.0, t))


# ------------------------------------------------------------------------------------------------ body shape (mesh edits at rest)
def deform_body(arm, me_o, BD):
    me = me_o.data
    names = {g.index: g.name for g in me_o.vertex_groups}
    bones = arm.data.bones
    gx, gl, ga = BD["girth"]
    belly, bellyx, bust, hips = BD.get("belly", 0), BD.get("bellyx", 0.0), BD.get("bust", 0), BD.get("hips", 0)
    for v in me.vertices:
        if not v.groups:
            continue
        g = max(v.groups, key=lambda a: a.weight)
        gn = names[g.group]
        co = v.co.copy()
        x, y, z = co
        if gn in ("Hips", "Abdomen", "Torso", "Body"):
            fx = fy = gx
            if gn == "Torso" and z > 3.3:          # shoulder girdle keeps its width (the Torso bone scale handles it)
                fx = 1.0 + (gx - 1.0) * 0.5
            c = Vector((0, -0.02, z))
            co.x = c.x + (x - c.x) * fx
            co.y = c.y + (y - c.y) * fy
            if belly or bellyx:
                gb = math.exp(-(((z - 2.65) / 0.38) ** 2))
                m = smooth((0.12 - y) / 0.28)
                co.y -= belly * gb * m
                co.x *= 1 + bellyx * gb
            if bust:
                gb = math.exp(-(((z - 3.38) / 0.22) ** 2))
                co.y -= bust * gb * smooth((0.05 - y) / 0.2)
            if hips:
                gb = math.exp(-(((z - 2.15) / 0.38) ** 2))
                co.x *= 1 + hips * gb
                co.y -= 0.0
        elif gn.startswith("UpperLeg") or gn.startswith("LowerLeg"):
            b = bones[gn]
            a, t = b.head_local, b.tail_local
            d = t - a
            u = max(0.0, min(1.0, (co - a).dot(d) / max(1e-6, d.dot(d))))
            c = a + d * u
            co = c + (co - c) * gl
            if hips and gn.startswith("UpperLeg"):
                gb = math.exp(-(((z - 2.0) / 0.45) ** 2))
                co.x *= 1 + hips * 0.7 * gb
        elif gn.startswith("UpperArm") or gn.startswith("LowerArm") or gn.startswith("Shoulder"):
            b = bones[gn]
            a, t = b.head_local, b.tail_local
            d = t - a
            u = max(0.0, min(1.0, (co - a).dot(d) / max(1e-6, d.dot(d))))
            c = a + d * u
            co = c + (co - c) * ga
        elif gn == "Neck":
            c = Vector((0, 0.1, z))
            k = 0.5 * (1 + (gx + gl) / 2)
            co.x = c.x + (x - c.x) * k
        v.co = co
    me.update()


def rot_bone(pb, deg):
    if not deg:
        return
    m = pb.bone.matrix_local.to_3x3().inverted()
    axis = (m @ Vector((1, 0, 0))).normalized()
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = Quaternion(axis, math.radians(deg)) @ pb.rotation_quaternion


def tweak(arm, BD):
    """Per-character posture and builds (shoulders, chest depth, lean, arm length). Called after every frame_set."""
    pb = arm.pose.bones
    for n in ("Neck", "Shoulder.L", "Shoulder.R"):
        pb[n].bone.inherit_scale = "NONE"
    pb["Torso"].scale = (BD["shoulder"], BD["chest"], 1)
    if BD.get("arms_len"):
        for sd in "LR":
            pb["UpperArm." + sd].scale = (1, BD["arms_len"], 1)
    for n, d in zip(("Abdomen", "Torso", "Neck", "Head"), BD["lean"]):
        rot_bone(pb[n], d)
    bpy.context.view_layer.update()


# ------------------------------------------------------------------------------------------------ props
def mat(col, rough=0.6):
    m = bpy.data.materials.new("p")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(col)
    b.inputs["Roughness"].default_value = rough
    return m


def prim(kind, pos, size, col, parent, rot=(0, 0, 0)):
    if kind == "box":
        bpy.ops.mesh.primitive_cube_add(size=1)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, vertices=32)
    elif kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16)
    elif kind == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=size[0], minor_radius=size[2], major_segments=40, minor_segments=8)
    o = bpy.context.active_object
    if kind == "torus":
        o.scale = (1, size[1] / size[0], 1)
    else:
        o.scale = size
    o.location = pos
    o.rotation_euler = [math.radians(a) for a in rot]
    if kind != "box":
        bpy.ops.object.shade_smooth()
    o.data.materials.append(mat(col))
    o.parent = parent
    return o


def add_extra(arm, bone, kind, loc, size, col, rot=(0, 0, 0)):
    """Mesh-space prop glued to a bone (clothing silhouettes, hair volume): size = radii / half extents."""
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1)
    elif kind == "tcone":
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0.86, depth=2, vertices=40)
    else:
        bpy.ops.mesh.primitive_cube_add(size=2)
    o = bpy.context.object
    kk = arm.matrix_world.to_scale()[0]
    o.scale = (size[0] * kk, size[1] * kk, size[2] * kk)
    o.rotation_euler = [math.radians(a) for a in rot]
    o.location = arm.matrix_world @ Vector(loc)
    o.data.materials.append(mat(col, 0.7))
    if kind != "box":
        bpy.ops.object.shade_smooth()
    parent_bone(arm, o, bone)
    return o


# ------------------------------------------------------------------------------------------------ realistic face
class Face72(face_kit.Face):
    def __init__(self, sc, arm, name, skin, mesh_o, BD):
        super().__init__(sc, arm, name, skin, mesh_o)
        self.BD = BD

    """s72 face: eye sockets + lids, arched brows, nose with wings, upper / lower lips, ears, jaw / age cues, hair volume."""

    def build(self, ex=face_kit.EXPR_NEUTRAL):
        arm, F, EX, EZ, surf_y, add = self.arm, self.F, self.EX, self.EZ, self.surf_y, self.add
        BD = self.BD
        FP = BD['face']
        SKIN, SKIN_D = self.skin, self.skin_d
        for o in self.feats:
            bpy.data.objects.remove(o, do_unlink=True)
        self.feats.clear()
        arm.data.pose_position = "REST"
        bpy.context.view_layer.update()
        fem = F["female"]
        age = FP["age"]
        sock_c = mix(SKIN, "#5a2a30", 0.20 + 0.05 * age)
        lid_c = mix(SKIN, "#7a4038", 0.10)
        for sx in (-1, 1):
            x = sx * EX
            z = EZ
            y0 = surf_y(x, z)
            add("sphere", (x, y0 + 0.010, z + 0.004), (0.080, 0.022, 0.062), sock_c, seg=20)                 # eye socket (soft shadow ring)
            add("sphere", (x, y0 + 0.020, z), (0.058, 0.026, 0.042), "#f7f3ec", seg=20)                      # eyeball
            add("sphere", (x * 0.97, y0 - 0.002, z - 0.003), (0.038, 0.013, 0.038), F["iris"], seg=18)       # iris (big, readable)
            add("sphere", (x * 0.97, y0 - 0.011, z - 0.003), (0.019, 0.008, 0.019), "#0b0a0e", seg=12)       # pupil
            add("sphere", (x * 0.97 - sx * 0.01, y0 - 0.018, z + 0.016), (0.0085, 0.004, 0.0085), "#ffffff", seg=8)
            add("sphere", (x, y0 - 0.006, z + 0.033), (0.066, 0.020, 0.024), lid_c, seg=18)                  # upper lid
            add("box", (x, y0 - 0.010, z + 0.046), (0.066, 0.009, 0.0085 if not fem else 0.012), "#1a1418")  # lash line
            if fem:
                add("box", (x + sx * 0.058, y0 - 0.008, z + 0.050), (0.016, 0.008, 0.006), "#1a1418", rot=(0, sx * 0.55, 0))
            if age >= 1:
                add("sphere", (x, y0 - 0.002, z - 0.057), (0.052, 0.008, 0.011), mix(SKIN, "#4a2630", 0.30 + 0.06 * age), seg=10)   # lower lid / bag
            if age >= 2:
                for i in (-1, 0, 1):                                                                         # crow's feet
                    add("box", (x + sx * 0.085, y0 + 0.004, z + i * 0.022), (0.022, 0.004, 0.0035), mix(SKIN, "#4a2630", 0.45),
                        rot=(0, sx * (0.35 * i), 0))
            # brows: two segments make an arch; brow_w = thickness, brow_tilt = outer end up (+) or down (-)
            bz = z + 0.130 + ex["brow_dy"]
            by = surf_y(x, bz) - 0.008
            th = (0.0145 if not fem else 0.0105) * FP["brow_w"]
            til = math.radians(FP["brow_tilt"])
            add("box", (x - sx * 0.026, by, bz - 0.004), (0.040, 0.014, th), F["brow"], rot=(0, sx * (til * 0.4 + 0.15), 0))
            add("box", (x + sx * 0.030, by, bz + 0.004 + 0.006 * math.sin(til) * 4), (0.042, 0.014, th * 0.9), F["brow"], rot=(0, -sx * (til * 0.6 + 0.25), 0))
            if ex["blush"] > 0:
                cy = surf_y(x * 1.25, z - 0.115)
                add("sphere", (x * 1.2, cy + 0.003, z - 0.115), (0.055, 0.010, 0.036), mix(SKIN, "#ff6a78", 0.06 + 0.26 * ex["blush"]), seg=12)
            # ears (skin colour with a darker inner shape)
            hx = Vector((sx * 3, 0.03, EZ - 0.04))
            hit = self.bvh.ray_cast(hx, Vector((-sx, 0, 0)))
            if hit[0] is not None:
                ex_ = hit[0].x
                add("sphere", (ex_ + sx * 0.012, 0.035, EZ - 0.04), (0.016, 0.048, 0.072), SKIN, seg=14)
                add("sphere", (ex_ + sx * 0.026, 0.030, EZ - 0.04), (0.006, 0.026, 0.046), SKIN_D, seg=10)
        # nose: bridge, tip, wings, nostrils, shadow under the tip
        tip = self.nose_tip()
        nw, nl = FP["nose"]
        ty = tip.y - (nl - 1) * 0.03
        add("box", (0, surf_y(0, EZ - 0.01) - 0.006, EZ - 0.05), (0.014, 0.006, 0.085), mix(SKIN, "#ffffff", 0.16))        # bridge highlight
        add("sphere", (0, ty + 0.002, tip.z - 0.038), (0.034 * nw, 0.030 * nl, 0.030), mix(SKIN, "#ffffff", 0.05), seg=14)   # tip
        for sx in (-1, 1):
            add("sphere", (sx * 0.040 * nw, tip.y + 0.020, tip.z - 0.040), (0.021 * nw, 0.020, 0.024), SKIN, seg=10)       # wings
            add("sphere", (sx * 0.024 * nw, ty - 0.008, tip.z - 0.058), (0.010, 0.008, 0.007), "#3a1c1c", seg=8)           # nostrils
        add("box", (0, tip.y + 0.016, tip.z - 0.066), (0.052 * nw, 0.010, 0.007), SKIN_D)
        # mouth: upper lip (darker), lower lip (fuller, lighter), dark mouth line with smile / smirk
        zm = tip.z - 0.125 - ex["mouth_open"] * 0.2
        W = (0.082 if not fem else 0.074) * (1.12 if FP["smile"] > 0.7 else 1.0)
        lip = F["lips"]
        sm = FP["smile"] * 0.030
        n = 8
        pts = []
        for i in range(n + 1):
            t = -1 + 2 * i / n
            z_ = zm + sm * (t * t - 0.35) + (0.010 * t if FP.get("smirk") else 0.0)
            pts.append((t * W, z_))
        for i in range(n):
            (xa, za), (xb, zb) = pts[i], pts[i + 1]
            xm, zmid = (xa + xb) / 2, (za + zb) / 2
            ang = math.atan2(zb - za, xb - xa)
            yv = surf_y(xm, zmid) - 0.010
            add("box", (xm, yv, zmid), (abs(xb - xa) / 2 + 0.004, 0.008, 0.0050), mix(lip, "#2a1010", 0.55), rot=(0, -ang, 0))
        yl = surf_y(0, zm)
        lw = 0.013 if fem else 0.008
        add("sphere", (0, yl - 0.004, zm + 0.014 + sm * -0.2), (W * 0.82, 0.012, 0.012 + (0.004 if fem else 0.0)), mix(lip, "#3a1a1a", 0.20), seg=16)    # upper lip
        add("sphere", (0, yl - 0.006, zm - 0.016 - sm * 0.2), (W * 0.70, 0.014, 0.014 + (0.005 if fem else 0.0)), mix(lip, "#ffffff", 0.12), seg=16)      # lower lip
        # jaw, chin, jowls, cheek hollows
        jw = FP["jaw"]
        zc = EZ - 0.34
        add("sphere", (0, surf_y(0, zc) - 0.004, zc + 0.01), (0.060 * jw, 0.034, 0.042), SKIN, seg=14)                                  # chin
        if jw > 1.2 or FP.get("jowls"):
            for sx in (-1, 1):
                add("sphere", (sx * 0.17 * jw, surf_y(sx * 0.17, EZ - 0.27) + 0.002, EZ - 0.27), (0.075 * jw, 0.05, 0.075), SKIN, seg=14)   # jaw / jowls
        if age >= 3:
            for sx in (-1, 1):
                add("sphere", (sx * 0.15, surf_y(sx * 0.15, EZ - 0.19) - 0.004, EZ - 0.19), (0.05, 0.014, 0.06), mix(SKIN, "#5a2a30", 0.22), seg=12)   # hollow cheeks
        if age >= 1:
            for sx in (-1, 1):                                                                                       # nasolabial folds
                xa, za = sx * 0.050 * nw, tip.z - 0.075
                xb, zb = sx * (W + 0.012), zm + 0.012
                ang = math.atan2(zb - za, xb - xa)
                add("box", ((xa + xb) / 2, surf_y((xa + xb) / 2, (za + zb) / 2) - 0.006, (za + zb) / 2),
                    (math.hypot(xb - xa, zb - za) / 2, 0.006, 0.0035), mix(SKIN, "#5a2a30", 0.38 + 0.06 * age), rot=(0, -ang, 0))
        if age >= 2:
            for i in range(2 if age == 2 else 3):                                                                   # forehead lines
                zf = EZ + 0.20 + 0.032 * i
                add("box", (0, surf_y(0, zf) - 0.004, zf), (0.12 - 0.01 * i, 0.004, 0.0032), mix(SKIN, "#5a2a30", 0.32))
        if FP.get("stubble"):
            add("sphere", (0, surf_y(0, EZ - 0.30) + 0.004, EZ - 0.285), (0.15, 0.040, 0.085), mix(SKIN, "#2a2018", 0.30), seg=16)
        if FP.get("moustache"):
            hc = F["hair"]
            for sx in (-1, 1):
                add("sphere", (sx * 0.045, yl - 0.020, zm + 0.040), (0.058, 0.024, 0.021), hc, rot=(0, -sx * 0.30, 0), seg=14)
        # hair volume pieces from the build table
        for h in BD["hair"]:
            add(h[0], h[1], h[2], h[3], rot=tuple(math.radians(a) for a in (h[4] if len(h) > 4 else (0, 0, 0))), seg=18)
        # fitted glasses (as in face_kit)
        g = F["glasses"]
        if g:
            for o in self.glasses:
                o.hide_render = True
        if g == "victor":
            for sx in (-1, 1):
                x = sx * EX
                y0 = surf_y(x, EZ)
                add("box", (x, y0 - 0.032, EZ + 0.005), (0.092, 0.012, 0.056), "#101016")
                add("box", (x - sx * 0.02, y0 - 0.046, EZ + 0.025), (0.030, 0.003, 0.010), "#7a8a9a", rot=(0, sx * 0.4, 0))
                add("box", (x, y0 - 0.032, EZ + 0.064), (0.095, 0.014, 0.008), "#f2c94c")
                add("box", (sx * (EX + 0.12), 0.0, EZ + 0.0), (0.008, 0.16, 0.012), "#f2c94c")
            add("box", (0, surf_y(0, EZ + 0.02) - 0.03, EZ + 0.03), (0.04, 0.010, 0.010), "#f2c94c")
        if g == "rosa":
            for sx in (-1, 1):
                x = sx * EX
                y0 = surf_y(x, EZ)
                add("torus", (x, y0 - 0.03, EZ + 0.005), (0.078, 0.078, 0.078), "#2a2a30", rot=(math.pi / 2, 0, 0))
            add("box", (0, surf_y(0, EZ + 0.02) - 0.03, EZ + 0.02), (0.05, 0.008, 0.008), "#2a2a30")
            for sx in (-1, 1):
                add("box", (sx * (EX + 0.15), 0.0, EZ + 0.01), (0.007, 0.16, 0.008), "#2a2a30")




# ------------------------------------------------------------------------------------------------ loading / dressing
def load(sc, name, fbx, colours=None):
    BD = char_build.B[name]
    colours = colours or BD["colours"]
    pivot = bpy.data.objects.new("pivot", None)
    sc.collection.objects.link(pivot)
    body = bpy.data.objects.new("body", None)
    sc.collection.objects.link(body)
    body.parent = pivot
    k = BD["height"] / 1.78
    body.scale = (k, k, k)
    bpy.ops.import_scene.fbx(filepath=fbx)
    arm = next(o for o in sc.objects if o.type == "ARMATURE")
    meshes = [o for o in sc.objects if o.type == "MESH"]
    body_mesh = max(meshes, key=lambda o: len(o.data.vertices))
    for m in list(bpy.data.materials):
        if m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
            bsdf = m.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Alpha"].default_value = 1.0
            bsdf.inputs["Roughness"].default_value = 0.65
            base = m.name.split(".")[0]
            if base in colours:
                for l in list(m.node_tree.links):
                    if l.to_socket == bsdf.inputs["Base Color"]:
                        m.node_tree.links.remove(l)
                bsdf.inputs["Base Color"].default_value = rgb(colours[base])
    idle = next(a for a in bpy.data.actions if a.name.endswith("_Idle"))
    arm.animation_data_create()
    arm.animation_data.action = idle
    sc.frame_set(1)
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    deform_body(arm, body_mesh, BD)
    arm.data.pose_position = "POSE"
    sc.frame_set(1)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    zs = []
    for o in meshes:
        ev = o.evaluated_get(deps)
        me = ev.to_mesh()
        zs += [(ev.matrix_world @ v.co).z for v in me.vertices]
        ev.to_mesh_clear()
    s = 1.78 / (max(zs) - min(zs))
    root = bpy.data.objects.new("root", None)
    sc.collection.objects.link(root)
    arm.parent = root
    root.parent = body
    root.scale = (s, s, s)
    root.location = (0, 0, -min(zs) * s)
    bpy.context.view_layer.update()
    return dict(name=name, BD=BD, arm=arm, meshes=meshes, body_mesh=body_mesh, pivot=pivot, body=body, root=root, idle=idle)


HAND_CRISP = os.environ.get("TL_HANDMODE", "crisp") == "crisp"
HAND_GROUPS = ("Palm.", "MiddleHand.", "Fingers.", "Thumb1.", "Thumb2.")


def hand_verts(o):
    """Indices of the body vertices that belong mainly to the hand bones (s75)."""
    gi = {g.index for g in o.vertex_groups if g.name.startswith(HAND_GROUPS)}
    out = set()
    for v in o.data.vertices:
        w = sum(g.weight for g in v.groups if g.group in gi)
        if w >= 0.5:
            out.add(v.index)
    return out


HAND_TINT = tuple(float(x) for x in os.environ.get("TL_HANDTINT", "0.96,0.86,0.80").split(","))


def tint_hands(o, hv):
    """s75: hands get their own skin material a little warmer / darker than the lit face skin, so they do not quantize
    to the pale cuff / collar cream and read as gloves."""
    si = [i for i, m in enumerate(o.data.materials) if m and m.name.split(".")[0] == "Skin"]
    if not si or HAND_TINT == (1.0, 1.0, 1.0):
        return
    m = o.data.materials[si[0]].copy()
    m.name = "SkinHand"
    bsdf = m.node_tree.nodes["Principled BSDF"]
    c = list(bsdf.inputs["Base Color"].default_value)
    bsdf.inputs["Base Color"].default_value = (c[0] * HAND_TINT[0], c[1] * HAND_TINT[1], c[2] * HAND_TINT[2], 1)
    o.data.materials.append(m)
    k = len(o.data.materials) - 1
    for poly in o.data.polygons:
        if o.data.materials[poly.material_index].name.split(".")[0] == "Skin" and all(v in hv for v in poly.vertices):
            poly.material_index = k


def dress(L, sc):
    """Proportions, props, face (+ anchors), extras, V1 Soft shading. Returns the Face72."""
    BD, arm, body, body_mesh, name = L["BD"], L["arm"], L["body"], L["body_mesh"], L["name"]
    props = [(prim(p[0], p[1], p[2], p[3], body, rot=(p[4] if len(p) > 4 else (0, 0, 0))), p) for p in BD["props"]]
    bpy.context.view_layer.update()
    face_kit.apply_proportions(BD["head"], float(os.environ.get("TL_HAND", BD["hand"])))
    face = Face72(sc, arm, name, BD["colours"]["Skin"], body_mesh, BD)
    for o, p in props:
        if p[1][2] > 1.55:
            parent_bone(arm, o, "Head")
    if BD.get("v2"):
        player_look.apply(arm)
    face.build()
    face.make_anchors()
    for bone, kind, loc, size, col, *r in BD["extras"]:
        add_extra(arm, bone, kind, loc, size, col, r[0] if r else (0, 0, 0))
    if BD.get("gloves"):                                          # s76: rubber gloves (Ines): two spheres per hand
        arm.data.pose_position = "REST"
        bpy.context.view_layer.update()
        for sd in "LR":
            pal = arm.data.bones["Palm." + sd]
            tip = arm.data.bones["Fingers.%s_end" % sd]
            mid = (Vector(pal.head_local) + Vector(tip.tail_local)) / 2
            add_extra(arm, "Palm." + sd, "sphere", tuple(mid), (0.125, 0.125, 0.125), BD["gloves"])
            add_extra(arm, "Palm." + sd, "sphere", tuple(Vector(pal.head_local)), (0.105, 0.105, 0.105), BD["gloves"])
    arm.data.pose_position = "POSE"
    for o in sc.objects:                                      # V1 Soft: smooth shading + one subdivision level on the bodies
        if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers):
            hv = hand_verts(o)
            tint_hands(o, hv)
            for poly in o.data.polygons:
                poly.use_smooth = not (HAND_CRISP and all(v in hv for v in poly.vertices))   # s75: hands stay faceted (thumb / fingers read)
            if HAND_CRISP:
                cr = o.data.attributes.get("crease_edge") or o.data.attributes.new("crease_edge", "FLOAT", "EDGE")
                for e in o.data.edges:
                    if e.vertices[0] in hv and e.vertices[1] in hv:
                        cr.data[e.index].value = 1.0
            md = o.modifiers.new("s72_subsurf", "SUBSURF")
            md.levels = md.render_levels = 1
    return face


def soft_render(sc):
    sc.render.filter_size = 1.4                               # V1 Soft pixel filter


def soft_world(world):
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.66, 0.8, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.5


def soft_sun(sc):
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.5 * 0.85
    sun.angle = math.radians(30)
    so = bpy.data.objects.new("sun", sun)
    sc.collection.objects.link(so)
    so.rotation_euler = Vector((-0.25, 0.7, -0.65)).normalized().to_track_quat("-Z", "Y").to_euler()
    return so
