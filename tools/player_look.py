"""
Town Life - the player's V2 look (owner-approved, ported from the s35 proposal; runs INSIDE Blender):
cream collar / cuffs / zip on the sweater, brown belt with a gold buckle, chunky red sneakers with white soles.
(The head / hand / shoulder proportions come from tools/face_kit.py; the eyes from the modelled face.)
Call apply(arm) after the armature is scaled and parented (root scale set), with the colours already applied.
"""
import math
import os

import bpy
from mathutils import Matrix, Vector

from face_kit import hexc, parent_bone


def _mat(name, col, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(col)
    b.inputs["Roughness"].default_value = rough
    return m


def _slot(me, name, col, rough=0.6):
    me.materials.append(_mat(name, col, rough))
    return len(me.materials) - 1


def _add(arm, kind, loc, scale, mat, name, rot=(0, 0, 0), seg=16):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=max(6, seg // 2), radius=1)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=1, depth=2)
    else:
        bpy.ops.mesh.primitive_cube_add(size=2)
    o = bpy.context.object
    o.name = name
    k = arm.matrix_world.to_scale()[0]
    o.scale = (scale[0] * k, scale[1] * k, scale[2] * k)
    o.rotation_euler = rot
    o.location = arm.matrix_world @ Vector(loc)
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def apply(arm):
    body = bpy.data.objects["BaseHuman"]
    me = body.data
    cube = bpy.data.objects.get("Cube")
    if cube:
        cube.hide_render = True
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    collar = _slot(me, "Collar", "#f4efe0")
    cuff = _slot(me, "Cuff", os.environ.get("TL_CUFF", "#22407f"))
    zipm = _slot(me, "Zip", "#f4efe0")
    sole = _slot(me, "Sole", "#f6f3ea", 0.5)
    shoeb = _slot(me, "ShoeB", "#c8352e")
    for p in me.polygons:
        c = p.center
        nm = me.materials[p.material_index].name.split(".")[0]
        if nm == "Shirt":
            if c.z > 3.90 and abs(c.x) < 0.40:
                p.material_index = collar
            elif abs(c.x) > 1.68:
                p.material_index = cuff
            elif abs(c.x) < 0.085 and c.z > 2.5 and c.y < 0.0 and p.normal.y < -0.3:
                p.material_index = zipm
            elif c.z < 2.47 and abs(c.x) < 0.6:
                p.material_index = cuff
        elif nm == "Eyes" and c.z < 1:                 # the FBX "Eyes" material below knee height is the shoes
            p.material_index = sole if c.z < 0.045 else shoeb
    mshoe = _mat("SneakerBody", "#c8352e")
    msole = _mat("SneakerSole", "#f6f3ea", 0.5)
    mtoe = _mat("SneakerToe", "#f6f3ea", 0.5)
    mlace = _mat("SneakerStripe", "#2a2630", 0.6)
    for side, sx in (("L", 0.30), ("R", -0.31)):
        parts = [
            _add(arm, "sphere", (sx, -0.17, 0.145), (0.20, 0.34, 0.15), mshoe, "snk_up" + side, seg=14),
            _add(arm, "cube", (sx, -0.16, 0.04), (0.19, 0.31, 0.04), msole, "snk_sole" + side),
            _add(arm, "sphere", (sx, -0.36, 0.12), (0.155, 0.13, 0.10), mtoe, "snk_toe" + side, seg=12),
            _add(arm, "cube", (sx, -0.10, 0.26), (0.175, 0.09, 0.022), mlace, "snk_lace" + side),
        ]
        for o in parts:
            parent_bone(arm, o, "Foot." + side)
    # zip line down the chest (follows the sweater's front surface)
    sv = [v.co for v in me.vertices if abs(v.co.x) < 0.12]

    def front(z0, z1):
        return min(v.y for v in sv if z0 < v.z < z1)
    yA, yB = front(2.55, 2.75), front(3.75, 3.95)
    zA, zB = 2.65, 3.85
    ln = math.hypot(yB - yA, zB - zA)
    ang = math.atan2(yB - yA, zB - zA)
    zp = _add(arm, "cube", (0, (yA + yB) / 2 - 0.012, (zA + zB) / 2), (0.022, 0.016, ln / 2), _mat("ZipM", "#f4efe0", 0.4), "zip",
              rot=(-ang, 0, 0))
    parent_bone(arm, zp, "Torso")
    belt = _add(arm, "cyl", (0, 0.03, 2.40), (0.56, 0.43, 0.085), _mat("Belt", "#3a2616"), "belt", seg=24)
    buckle = _add(arm, "cube", (0, -0.405, 2.40), (0.10, 0.03, 0.10), _mat("Buckle", "#e8c04a", 0.3), "buckle")
    for o in (belt, buckle):
        parent_bone(arm, o, "Hips")
    arm.data.pose_position = "POSE"
