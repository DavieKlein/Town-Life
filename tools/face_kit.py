"""
Town Life - modelled faces for the character sprites (runs INSIDE Blender; used by blender_actor.py, blender_acts.py, blender_cast.py).
Owner-approved "option B" (proposal tools/proposals/s54): player-V2 proportions (head 1.28x, hands 1.38x, set on the Idle/Walk keyframes),
small 3D face features (eyes, brows, nose shade, mouth, blush, hair strands, fitted glasses) glued to the Head bone, and
projected anchor points per rendered frame (anchors.json) that tools/face_pass.py uses for the post-quantization pixel pass.
"""
import json
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import face_cfg  # noqa: E402

HEAD_K = 1.28
HAND_K = 1.38
SHOULDER_K = 1.14        # player only (V2)

EXPR_NEUTRAL = dict(brow_dy=0.0, brow_tilt=0, mouth_curve=0.0, mouth_open=0.0, lid=0.0, lid_tilt=0, squint=0.0, blush=0.35, teeth=False)


def hexc(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c]
    return (c[0], c[1], c[2], 1)


def shade(h, f):
    h = h.lstrip("#")
    c = [min(255, max(0, int(int(h[i:i + 2], 16) * f))) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(c)


def mix(a, b, t):
    a = a.lstrip("#")
    b = b.lstrip("#")
    c = [int(int(a[i:i + 2], 16) * (1 - t) + int(b[i:i + 2], 16) * t) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(c)


def mat(col, rough=0.6):
    m = bpy.data.materials.new("p")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(col)
    b.inputs["Roughness"].default_value = rough
    return m


def parent_bone(arm, obj, bone):
    """Glue obj (already placed at its rest-pose world matrix) to a bone without moving it."""
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    obj.parent = arm
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    bpy.context.view_layer.update()
    pb = arm.pose.bones[bone]
    pm = arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
    obj.matrix_parent_inverse = pm.inverted()
    obj.matrix_world = mw


def scale_keys(bone, kk):
    """The actions key the bone scales, so the proportions are applied to the keyframes themselves."""
    for act in bpy.data.actions:
        for fc in act.fcurves:
            if fc.data_path == 'pose.bones["%s"].scale' % bone:
                for kp in fc.keyframe_points:
                    kp.co[1] *= kk
                    kp.handle_left[1] *= kk
                    kp.handle_right[1] *= kk
                fc.update()


def apply_proportions(head=HEAD_K, hand=HAND_K):
    scale_keys("Head", head)
    for sd in "LR":
        scale_keys("Palm." + sd, hand)


def player_pose_tweaks(arm):
    """Broader shoulders (player V2): call after every frame_set. Neck and shoulders keep their own scale."""
    pb = arm.pose.bones
    for n in ("Neck", "Shoulder.L", "Shoulder.R"):
        pb[n].bone.inherit_scale = "NONE"
    pb["Torso"].scale = (SHOULDER_K, 1, 1)


class Face:
    """Builds the face features of one character and projects the anchors. Everything is created in the REST pose."""

    def __init__(self, sc, arm, name, skin, mesh_o):
        self.sc, self.arm, self.name = sc, arm, name
        self.F = face_cfg.FACE[name]
        self.skin = skin
        self.skin_d = mix(skin, "#6a2a2a", 0.30)
        self.mesh_o = mesh_o
        me = self.me = self.mesh_o.data
        head_i = self.mesh_o.vertex_groups["Head"].index
        self.head_vs = {v.index for v in me.vertices if any(g.group == head_i and g.weight > 0.5 for g in v.groups)}
        head_polys = [p for p in me.polygons if all(vi in self.head_vs for vi in p.vertices)]
        co = [v.co[:] for v in me.vertices]
        self.bvh = BVHTree.FromPolygons(co, [p.vertices[:] for p in head_polys])
        hair_polys = [p for p in head_polys if me.materials[p.material_index].name.split(".")[0] in ("Hair", "HairBase", "Hair2")]
        self.bvh_hair = BVHTree.FromPolygons(co, [p.vertices[:] for p in hair_polys]) if hair_polys else None
        eyes_c = [p.center for p in me.polygons if me.materials[p.material_index].name.split(".")[0] == "Eyes" and p.center.z > 3]
        self.EX = abs(sum(c.x for c in eyes_c if c.x > 0) / max(1, len([c for c in eyes_c if c.x > 0])))
        self.EZ = sum(c.z for c in eyes_c) / len(eyes_c)
        self.feats = []
        self.glasses = []        # cast.py head props that are replaced by fitted glasses
        self.anch = {}

    def surf_y(self, x, z, default=-0.24):
        h = self.bvh.ray_cast(Vector((x, -3, z)), Vector((0, 1, 0)))
        return h[0].y if h[0] is not None else default

    def add(self, kind, loc, size, col, rot=(0, 0, 0), seg=12):
        """Place an object in armature rest coordinates and glue it to the Head bone."""
        if kind == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=max(6, seg // 2), radius=1)
        elif kind == "cyl":
            bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=1, depth=2)
        elif kind == "torus":
            bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.10, major_segments=32, minor_segments=8)
        else:
            bpy.ops.mesh.primitive_cube_add(size=2)
        o = bpy.context.object
        kk = self.arm.matrix_world.to_scale()[0]
        o.scale = (size[0] * kk, size[1] * kk, size[2] * kk)
        o.rotation_euler = rot
        o.location = self.arm.matrix_world @ Vector(loc)
        o.data.materials.append(mat(col, 0.5))
        if kind != "box":
            bpy.ops.object.shade_smooth()
        parent_bone(self.arm, o, "Head")
        self.feats.append(o)
        return o

    def anchor(self, name, loc):
        e = bpy.data.objects.new("anc_" + name, None)
        self.sc.collection.objects.link(e)
        e.location = self.arm.matrix_world @ Vector(loc)
        parent_bone(self.arm, e, "Head")
        return e

    def hide_prop_glasses(self, objs):
        self.glasses = list(objs)

    def build(self, ex=EXPR_NEUTRAL):
        arm, F, EX, EZ, surf_y, add = self.arm, self.F, self.EX, self.EZ, self.surf_y, self.add
        me, head_vs, mesh_o = self.me, self.head_vs, self.mesh_o
        SKIN, SKIN_D = self.skin, self.skin_d
        for o in self.feats:
            bpy.data.objects.remove(o, do_unlink=True)
        self.feats.clear()
        arm.data.pose_position = "REST"
        bpy.context.view_layer.update()
        fem = F["female"]
        for sx in (-1, 1):
            x = sx * EX
            z = EZ
            y0 = surf_y(x, z)
            add("sphere", (x, y0 + 0.020, z), (0.058, 0.026, 0.041), "#f7f3ec", seg=16)
            add("sphere", (x * 0.97, y0 - 0.004, z - 0.002), (0.034, 0.012, 0.034), F["iris"], seg=14)
            add("sphere", (x * 0.97, y0 - 0.011, z - 0.002), (0.018, 0.008, 0.018), "#0b0a0e", seg=10)
            add("sphere", (x * 0.97, y0 - 0.017, z + 0.014), (0.008, 0.004, 0.008), "#ffffff", seg=8)
            add("box", (x, y0 - 0.002, z + 0.040), (0.062, 0.010, 0.0075 if not fem else 0.011), "#1a1418")
            if fem:
                add("box", (x + sx * 0.055, y0 - 0.002, z + 0.046), (0.014, 0.008, 0.006), "#1a1418", rot=(0, sx * 0.5, 0))
            by = surf_y(x, z + 0.12) - 0.006
            add("box", (x + sx * 0.005, by, z + 0.125 + ex["brow_dy"]), (0.080 if not fem else 0.074, 0.013, 0.016 if not fem else 0.011),
                F["brow"], rot=(0, -sx * math.radians(ex["brow_tilt"]), 0))
            if ex["blush"] > 0:
                cy = surf_y(x * 1.25, z - 0.115)
                add("sphere", (x * 1.2, cy + 0.003, z - 0.115), (0.055, 0.010, 0.036), mix(SKIN, "#ff6a78", 0.06 + 0.26 * ex["blush"]), seg=12)
            hx = Vector((sx * 3, 0.02, EZ - 0.05))
            hit = self.bvh.ray_cast(hx, Vector((-sx, 0, 0)))
            if hit[0] is not None:
                add("sphere", (hit[0].x - sx * 0.004, 0.02, EZ - 0.05), (0.012, 0.045, 0.06), SKIN_D, seg=10)
        tip = self.nose_tip()
        add("box", (0, tip.y + 0.012, tip.z - 0.045), (0.075, 0.012, 0.012), SKIN_D)
        for sx in (-1, 1):
            add("sphere", (sx * 0.028, tip.y + 0.004, tip.z - 0.026), (0.011, 0.009, 0.009), "#3a1c1c", seg=8)
        add("box", (0, surf_y(0, EZ - 0.02) - 0.004, EZ - 0.04), (0.006, 0.005, 0.07), mix(SKIN, "#ffffff", 0.14))
        zm = tip.z - 0.115 - ex["mouth_open"] * 0.2
        W = 0.085 if not fem else 0.075
        n = 7
        lip = F["lips"]
        pts = []
        for i in range(n + 1):
            t = -1 + 2 * i / n
            pts.append((t * W, zm + ex["mouth_curve"] * (t * t - 0.35)))
        for i in range(n):
            (xa, za), (xb, zb) = pts[i], pts[i + 1]
            xm, zmid = (xa + xb) / 2, (za + zb) / 2
            ang = math.atan2(zb - za, xb - xa)
            yv = surf_y(xm, zmid) - 0.008
            add("box", (xm, yv, zmid), (abs(xb - xa) / 2 + 0.004, 0.009, 0.0075 if not fem else 0.0095), mix(lip, "#3a1a1a", 0.35), rot=(0, -ang, 0))
        if fem:
            add("box", (0, surf_y(0, zm - 0.02) - 0.008, zm - 0.02 + ex["mouth_curve"] * -0.1), (W * 0.55, 0.008, 0.009), mix(lip, "#ffffff", 0.25))
        if self.bvh_hair is not None:
            rnd = random.Random(7)
            hc = F["hair"]
            dark, light = shade(hc, 0.68), mix(hc, "#ffffff", 0.42)

            def strand(origin, direction, col, w, ln):
                h = self.bvh_hair.ray_cast(origin, direction)
                loc, nrm = h[0], h[1]
                if loc is None:
                    return
                down = Vector((0, 0, -1))
                tg = down - nrm * down.dot(nrm)
                if tg.length < 0.2:
                    tg = Vector((0, 1, 0)) - nrm * nrm.y
                tg.normalize()
                xx = tg.cross(nrm).normalized()
                mrot = Matrix((xx, tg, nrm)).transposed()
                kk = arm.matrix_world.to_scale()[0]
                bpy.ops.mesh.primitive_cube_add(size=2)
                o = bpy.context.object
                o.scale = (w * kk, ln * kk, 0.007 * kk)
                o.rotation_euler = mrot.to_euler()
                o.location = arm.matrix_world @ (loc - nrm * 0.002)
                o.data.materials.append(mat(col, 0.45))
                parent_bone(arm, o, "Head")
                self.feats.append(o)
            top = max(v.co.z for v in me.vertices if v.index in head_vs)
            for i in range(13):
                x = -0.21 + 0.035 * i + rnd.uniform(-0.01, 0.01)
                strand(Vector((x, -0.05 + rnd.uniform(-0.1, 0.05), top + 1)), Vector((0, 0, -1)), dark if i % 2 else light, 0.010, rnd.uniform(0.03, 0.05))
            for i in range(7):
                x = -0.16 + 0.053 * i
                strand(Vector((x, -3, EZ + 0.23 + rnd.uniform(0, 0.12))), Vector((0, 1, 0)), light if i % 2 else dark, 0.009, rnd.uniform(0.03, 0.05))
            for sx in (-1, 1):
                strand(Vector((sx * 3, 0.0, EZ + 0.30)), Vector((-sx, 0, 0)), light, 0.010, 0.05)
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

    def nose_tip(self):
        me = self.me
        return min((me.vertices[i].co for i in self.head_vs if abs(me.vertices[i].co.x) < 0.05 and self.EZ - 0.25 < me.vertices[i].co.z < self.EZ),
                   key=lambda c: c.y)

    def make_anchors(self):
        EX, EZ, surf_y, anchor = self.EX, self.EZ, self.surf_y, self.anchor
        self.arm.data.pose_position = "REST"
        bpy.context.view_layer.update()
        tip = self.nose_tip()

        def ys(x, z):
            return surf_y(x, z) - 0.035
        zm = tip.z - 0.115
        A = self.anch
        A["eyeP"] = anchor("eyeP", (EX, ys(EX, EZ), EZ))          # character's left (+x)
        A["eyeM"] = anchor("eyeM", (-EX, ys(-EX, EZ), EZ))
        A["browP"] = anchor("browP", (EX, ys(EX, EZ + 0.125), EZ + 0.125))
        A["browM"] = anchor("browM", (-EX, ys(-EX, EZ + 0.125), EZ + 0.125))
        A["mouth"] = anchor("mouth", (0, ys(0, zm), zm))
        A["mouthP"] = anchor("mouthP", (0.08, ys(0.08, zm), zm))
        A["mouthM"] = anchor("mouthM", (-0.08, ys(-0.08, zm), zm))
        A["nose"] = anchor("nose", (0, tip.y - 0.03, tip.z - 0.03))
        A["cheekP"] = anchor("cheekP", (EX * 1.25, ys(EX * 1.25, EZ - 0.115), EZ - 0.115))
        A["cheekM"] = anchor("cheekM", (-EX * 1.25, ys(-EX * 1.25, EZ - 0.115), EZ - 0.115))
        top = max(self.me.vertices[i].co.z for i in self.head_vs)
        A["crown"] = anchor("crown", (-0.10, -0.12, top + 0.03))
        A["chin"] = anchor("chin", (0, -0.2, EZ - 0.33))
        A["headtop"] = anchor("headtop", (0, 0.1, top + 0.03))

    def project(self, co, fwd, fw, fh):
        """Frame pixel positions of the anchors for the current pose + visibility from the camera."""
        sc = self.sc
        bpy.context.view_layer.update()
        deps = bpy.context.evaluated_depsgraph_get()
        res = {}
        fn = fwd.normalized()
        for name, e in self.anch.items():
            p = e.matrix_world.translation.copy()
            nv = world_to_camera_view(sc, co, p)
            origin = p - fn * 10
            hit, loc, nrm, idx, ob, mw = sc.ray_cast(deps, origin, fn, distance=10.5)
            vis = bool(hit and (loc - origin).length > 10 - 0.03)
            res[name] = [round(nv.x * fw, 3), round((1 - nv.y) * fh, 3), vis]
        return res

