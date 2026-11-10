"""s71 proposal: renders the idle sprites of the player or Mia with the REAL actor renderers (blender_actor.py /
blender_cast.py) plus light / filter variants, applied with a render_pre handler (no real file is changed).

  blender -b -noaudio --python s71_actor.py -- <cur|v1|v2|v3> <player|mia> <out_dir> <ss> <samples>

cur  as in the game
v1   smooth-shaded + 1x subdivided bodies, softer key light (sun angle 30 deg), stronger sky fill, wider pixel filter (1.4): softer shading, rounder forms
v2   v1 + warm bounce from below and a cool rim light from behind: richer, more modelled look
v3   same light as v1, 6x supersampling, 3x samples, filter 1.6 (smoother silhouettes); the colour work is in variants.py
"""
import math
import os
import runpy
import sys

import bpy
from mathutils import Vector

TOOLS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
i = sys.argv.index("--")
VARIANT, WHO, OUT, SS, SAMPLES = sys.argv[i + 1:i + 6]
DONE = [False]


@bpy.app.handlers.persistent
def pre(scene, *a):
    sc = bpy.context.scene
    if VARIANT == "cur":
        return
    sc.render.filter_size = 1.4 if VARIANT != "v3" else 1.6
    if DONE[0]:
        return
    DONE[0] = True
    for o in list(sc.objects):
        if o.type == "LIGHT" and o.data.type == "SUN":
            o.data.angle = math.radians(30)
            o.data.energy = o.data.energy * 0.85
    if sc.world:
        bg = sc.world.node_tree.nodes["Background"]
        bg.inputs["Strength"].default_value = 1.5
    for o in list(sc.objects):                  # rounder, softer bodies: smooth shading + 1 subdivision level (after the armature)
        if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers):
            for poly in o.data.polygons:
                poly.use_smooth = True
            md = o.modifiers.new("s71_subsurf", "SUBSURF")
            md.levels = md.render_levels = 1
    if VARIANT == "v2":
        for name, rot, col, en in (("bounce", (math.radians(180 - 40), 0, math.radians(30)), (1.0, 0.72, 0.5), 0.7),
                                   ("rim", (math.radians(60), 0, math.radians(200)), (0.7, 0.85, 1.0), 1.1)):
            ld = bpy.data.lights.new(name, "SUN")
            ld.energy, ld.color, ld.angle = en, col, math.radians(40)
            lo = bpy.data.objects.new(name, ld)
            lo["s71_extra"] = True
            sc.collection.objects.link(lo)
            lo.rotation_euler = rot


bpy.app.handlers.render_pre.append(pre)
if WHO == "player":
    sys.argv = ["blender", "--", os.path.join(TOOLS, "..", "art_source", "quaternius_characters", "Male_LongSleeve.fbx"), OUT, SS, SAMPLES,
                '{"Shirt": "#2c5fb8", "Pants": "#a98655", "Hair": "#4a2a18", "Skin": "#f0c09a", "Shoes": "#3a2a22", "Socks": "#f2efe6"}',
                "0", "idle"]
    runpy.run_path(os.path.join(TOOLS, "blender_actor.py"), run_name="__main__")
else:
    sys.argv = ["blender", "--", WHO, OUT, SS, SAMPLES, "sprites"]
    runpy.run_path(os.path.join(TOOLS, "blender_cast.py"), run_name="__main__")
