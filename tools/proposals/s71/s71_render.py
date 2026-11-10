"""s71 proposal: renders a scene crop with the REAL renderer (tools/blender_render.py) plus style-variant patches.
Runs inside Blender (nothing in tools/ or the game is modified; the variants are monkeypatches applied here):

  blender -b -noaudio --python s71_render.py -- <cur|v1|v2|v3> <scene> <layer> <out.png> <scale> <samples> "x0,y0,x1,y1"

cur  the current sharp style C (unpatched)
v1   "Soft": bevelled boxes (s.box bevel), 32-segment cylinders / spheres, smooth shading with weighted normals,
     softer sun, thinner and softer outlines
v2   "Rich": v1 + material detail (colour variation, micro bump, wood grain, fabric weave), warmer bounce light and a
     warmer / lighter grime colour, 6 light bounces
v3   "Smooth colour": the geometry and lighting of the current look; the change is in the quantizer (variants.py)
"""
import math
import os
import time
import sys

import bmesh
import bpy
from mathutils import Vector

TOOLS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, TOOLS)
import blender_render as br  # noqa: E402

CELL_M = br.CELL_M
VARIANT = "cur"
T0 = time.time()


# ------------------------------------------------------------------------------------------------ geometry (v1, v2)
CROP = [None]


def in_crop(scene_obj, p):
    """Only the crop is rendered, so only prims that can show up in it are softened (keeps the test renders fast; a full
    rebuild would soften everything - see README for the cost estimate)."""
    if CROP[0] is None:
        return True
    X0, Y0, X1, Y1 = CROP[0]
    cx = (p.get("x0", p.get("x", 0)) + p.get("x1", p.get("x", 0))) / 2
    cy = (p.get("y0", p.get("y", 0)) + p.get("y1", p.get("y", 0))) / 2
    u, v = cx - cy, cx + cy
    ox, oy = scene_obj.origin_x / 16.0, scene_obj.origin_y / 8.0
    return (X0 / 16.0 - ox - 4 <= u <= X1 / 16.0 - ox + 4) and (Y0 / 8.0 - oy - 4 <= v <= Y1 / 8.0 - oy + 14)


def soften_prims(scene_obj):
    for p in scene_obj.prims:
        t = p["type"]
        if t in ("box", "cyl") and not in_crop(scene_obj, p):
            continue
        if t == "box" and not p.get("bevel"):
            dx = abs(p["x1"] - p["x0"]) * CELL_M
            dy = abs(p["y1"] - p["y0"]) * CELL_M
            dz = abs(p["z1"] - p["z0"])
            mn, mx = min(dx, dy, dz), max(dx, dy)
            if p["z0"] < -0.01 or mn < 0.06 or mx > 4.0 or dz > 2.6:
                continue                      # ground slabs, thin sheets, big wall pieces stay sharp
            p["bevel"] = min(0.07, 0.3 * mn)
        elif t == "cyl":
            p["verts"] = max(p.get("verts", 16), 32)


SCENE = [None]
_orig_sphere = br.add_sphere


def add_sphere_hi(bm, p):
    if not in_crop(SCENE[0], dict(x0=p["x"], x1=p["x"], y0=p["y"], y1=p["y"])):
        return _orig_sphere(bm, p)
    res = bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=20, radius=p["r"])
    for v in res["verts"]:
        v.co.z *= p.get("sz", 1.0)
        v.co.x *= p.get("sx", 1.0)
        v.co.y *= p.get("sy", 1.0)
    x, y, _ = br.bl(p["x"], p["y"])
    bmesh.ops.translate(bm, verts=res["verts"], vec=Vector((x, y, p["z"])))


def smooth_all():
    for o in list(bpy.context.scene.objects):
        if o.type != "MESH" or not (o.name.startswith("floor_") or o.name.startswith("objects_")):
            continue
        me = o.data
        if len(me.polygons) > 20000:
            continue
        for poly in me.polygons:
            poly.use_smooth = True
        try:
            me.use_auto_smooth = True
            me.auto_smooth_angle = math.radians(36)
        except Exception:
            pass
        md = o.modifiers.new("wn", "WEIGHTED_NORMAL")
        md.mode = "FACE_AREA"
        md.keep_sharp = True
        md.weight = 50


# ------------------------------------------------------------------------------------------------ material detail (v2)
SKIP = ("glass", "water", "screen", "sign", "lamp", "bulb", "neon", "light", "emit", "puddle", "text", "coil", "mirror")
WOOD = ("wood", "oak", "plank", "shelf", "crate", "bench", "table", "desk")
FABRIC = ("mattress", "rug", "blanket", "sofa", "cloth", "towel", "duvet", "pillow", "cushion", "apron", "awning", "seat", "carpet", "couch")


def _insert_before_base(nt, bsdf, builder):
    """builder(src_socket_or_None, default_colour) -> output colour socket; relinks into Base Color."""
    src = None
    for link in list(nt.links):
        if link.to_node == bsdf and link.to_socket.name == "Base Color":
            src = link.from_socket
            nt.links.remove(link)
    out = builder(src, tuple(bsdf.inputs["Base Color"].default_value))
    nt.links.new(out, bsdf.inputs["Base Color"])


def add_detail(m):
    n = m.name.lower()
    if not m.use_nodes or "Principled BSDF" not in m.node_tree.nodes or any(k in n for k in SKIP) or m.get("tl_detail"):
        return
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    if bsdf.inputs["Emission Strength"].default_value > 0.01:
        return
    m["tl_detail"] = True
    wood = any(k in n for k in WOOD)
    fabric = any(k in n for k in FABRIC)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    if wood:
        mp.inputs["Scale"].default_value = (5.0, 60.0, 22.0)           # long grain along x
        scale, detail, contrast = 9.0, 6.0, 0.32
    elif fabric:
        mp.inputs["Scale"].default_value = (45.0, 45.0, 45.0)
        scale, detail, contrast = 6.0, 3.0, 0.28
    else:
        mp.inputs["Scale"].default_value = (14.0, 14.0, 14.0)           # fine mottling / cast-surface noise
        scale, detail, contrast = 5.0, 5.0, 0.16
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    noise.inputs["Roughness"].default_value = 0.6
    nt.links.new(mp.outputs["Vector"], noise.inputs["Vector"])
    fac = noise.outputs["Fac"]
    if fabric:                                                          # weave: a fine checker on top of the noise
        chk = nt.nodes.new("ShaderNodeTexChecker")
        chk.inputs["Scale"].default_value = 70.0
        nt.links.new(tc.outputs["Object"], chk.inputs["Vector"])
        chk.inputs["Color1"].default_value = (1, 1, 1, 1)
        chk.inputs["Color2"].default_value = (0.72, 0.72, 0.72, 1)
        mixw = nt.nodes.new("ShaderNodeMath")
        mixw.operation = "MULTIPLY"
        nt.links.new(fac, mixw.inputs[0])
        nt.links.new(chk.outputs["Fac"], mixw.inputs[1])
        fac2 = nt.nodes.new("ShaderNodeMath")
        fac2.operation = "ADD"
        nt.links.new(fac, fac2.inputs[0])
        nt.links.new(mixw.outputs[0], fac2.inputs[1])
        fac2.inputs[1].default_value = 0.0
        fac = fac2.outputs[0]
    # brightness factor 1 - c/2 + c * fac  (mean ~1)
    ma = nt.nodes.new("ShaderNodeMath")
    ma.operation = "MULTIPLY_ADD"
    ma.inputs[1].default_value = contrast
    ma.inputs[2].default_value = 1.0 - contrast * (0.5 if not fabric else 1.0)
    nt.links.new(fac, ma.inputs[0])

    def builder(src, default):
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        if src is not None:
            nt.links.new(src, mix.inputs[6])
        else:
            mix.inputs[6].default_value = default
        comb = nt.nodes.new("ShaderNodeCombineColor")
        for i in range(3):
            nt.links.new(ma.outputs[0], comb.inputs[i])
        nt.links.new(comb.outputs[0], mix.inputs[7])
        return mix.outputs[2]

    _insert_before_base(nt, bsdf, builder)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35 if (wood or fabric) else 0.18
    bump.inputs["Distance"].default_value = 0.01
    nt.links.new(fac, bump.inputs["Height"])
    if not bsdf.inputs["Normal"].is_linked:
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


# ------------------------------------------------------------------------------------------------ patches
_orig_build = br.build
_orig_stylize = br.stylize
_orig_lights = br.setup_camera_and_lights
_orig_grime = br.add_grime


def tlog(msg):
    print(f"[s71 {time.time() - T0:6.1f}s] {msg}", flush=True)


def build(scene_obj, layer_visible):
    SCENE[0] = scene_obj
    tlog("build start")
    if VARIANT in ("v1", "v2"):
        soften_prims(scene_obj)
        tlog("softened prims: %d bevel" % sum(1 for q in scene_obj.prims if q.get("bevel")))
    _orig_build(scene_obj, layer_visible)
    tlog("build done")
    if VARIANT in ("v1", "v2"):
        smooth_all()
        tlog("smooth done")


def stylize(layer_visible):
    if VARIANT == "v2":
        for m in bpy.data.materials:            # outline colour of thin parts is read from the base colour: set it first
            c = br._base_colour(m)
            if c is not None:
                m.diffuse_color = (c[0] * 0.5, c[1] * 0.48, c[2] * 0.55, 1.0)
        for m in bpy.data.materials:
            add_detail(m)
    tlog("stylize start")
    _orig_stylize(layer_visible)
    tlog("stylize done")
    if VARIANT in ("v1", "v2"):
        fs = bpy.context.view_layer.freestyle_settings
        sharp = layer_visible == "objects"
        for i, ls in enumerate(fs.linesets):
            st = ls.linestyle
            if not sharp:                       # floor: softer than before
                st.thickness, st.alpha = 1.1, 0.55
                st.color = (0.16, 0.12, 0.16)
            elif i == 0:
                st.thickness, st.alpha = 1.7, 0.85
                st.color = (0.11, 0.08, 0.12)
            else:
                st.thickness, st.alpha = 0.8, 0.8


def add_grime(m):
    _orig_grime(m)
    if VARIANT == "v2" and m.use_nodes:
        for nd in m.node_tree.nodes:
            if nd.bl_idname == "ShaderNodeValToRGB" and nd.inputs["Fac"].is_linked and \
                    nd.inputs["Fac"].links[0].from_node.bl_idname == "ShaderNodeAmbientOcclusion":
                nd.color_ramp.elements[0].color = (0.52, 0.44, 0.44, 1)     # lighter, warm bounce instead of cool grime


def lights(s, scale):
    _orig_lights(s, scale)
    sc = bpy.context.scene
    if VARIANT in ("v1", "v2"):
        for o in sc.objects:
            if o.type == "LIGHT" and o.data.type == "SUN":
                o.data.angle = math.radians(9 if s.sun else 32)             # softer shadow edges
    if VARIANT == "v2":
        sc.cycles.max_bounces = 6
        for o in sc.objects:
            if o.type == "LIGHT" and o.data.type == "SUN":
                o.data.color = (1.0, 0.92, 0.80) if s.sun else o.data.color
        bg = sc.world.node_tree.nodes["Background"]
        if s.sun:
            bg.inputs["Color"].default_value = (0.66, 0.68, 0.80, 1)      # warmer sky = warm bounce in the shadows
            bg.inputs["Strength"].default_value = 1.05
        else:
            bg.inputs["Strength"].default_value = bg.inputs["Strength"].default_value * 1.25


def main():
    global VARIANT
    i = sys.argv.index("--")
    VARIANT = sys.argv[i + 1]
    sys.argv = sys.argv[:i + 1] + sys.argv[i + 2:]
    if len(sys.argv) > i + 6 and sys.argv[i + 6]:
        CROP[0] = None if os.environ.get("S71_FULL") else [float(q) for q in sys.argv[i + 6].split(",")]
    br.build, br.stylize, br.setup_camera_and_lights, br.add_grime = build, stylize, lights, add_grime
    if VARIANT in ("v1", "v2"):
        br.add_sphere = add_sphere_hi
    br.main()


main()
