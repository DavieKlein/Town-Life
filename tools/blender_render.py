"""
Town Life - Blender renderer (runs INSIDE Blender, called by tools/build_assets.py).

  blender -b -noaudio --python tools/blender_render.py -- <scene_ident> <floor|objects> <out.png> <scale> <samples>

Builds the scene from tools/scene.py, sets up an isometric orthographic camera that matches the
game's 2:1 projection exactly, and renders one layer:
  floor   - everything on the "floor" layer; objects are invisible to the camera but cast shadows
  objects - everything on the "objects" layer with a transparent background
"""

import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as scn  # noqa: E402

CELL_M = scn.CELL_M


def bl(x, y, z=0.0):
    return (x * CELL_M, -y * CELL_M, z)


# ---------------------------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------------------------
def rgb(h):
    """sRGB hex -> linear tuple."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


def surface_coords(nt):
    """Vector usable as 2D texture coords on any face: floors use (X, Y), walls use (X + Y, Z)."""
    tc = nt.nodes.new("ShaderNodeTexCoord")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep_n = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sep_n.inputs[0])
    absn = nt.nodes.new("ShaderNodeMath")
    absn.operation = "ABSOLUTE"
    nt.links.new(sep_n.outputs["Z"], absn.inputs[0])
    is_floor = nt.nodes.new("ShaderNodeMath")
    is_floor.operation = "GREATER_THAN"
    is_floor.inputs[1].default_value = 0.5
    nt.links.new(absn.outputs[0], is_floor.inputs[0])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "SUBTRACT"
    nt.links.new(sep.outputs["X"], add.inputs[0])
    nt.links.new(sep.outputs["Y"], add.inputs[1])
    wall = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(add.outputs[0], wall.inputs["X"])
    nt.links.new(sep.outputs["Z"], wall.inputs["Y"])
    floor = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs["X"], floor.inputs["X"])
    nt.links.new(sep.outputs["Y"], floor.inputs["Y"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "VECTOR"
    nt.links.new(is_floor.outputs[0], mix.inputs["Factor"])
    nt.links.new(wall.outputs[0], mix.inputs[4])
    nt.links.new(floor.outputs[0], mix.inputs[5])
    return mix.outputs[1]


def grit_material(nt, bsdf, coords, kind, spec):
    """Worn city surfaces: fine grain, large dirt patches, cracks and weeds in the joints."""
    L = nt.links

    def noise(scale, detail=3.0):
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        L.new(coords, n.inputs["Vector"])
        return n.outputs["Fac"]

    def ramp(fac, stops):
        r = nt.nodes.new("ShaderNodeValToRGB")
        r.color_ramp.elements[0].position, r.color_ramp.elements[0].color = stops[0][0], rgb(stops[0][1])
        r.color_ramp.elements[1].position, r.color_ramp.elements[1].color = stops[-1][0], rgb(stops[-1][1])
        for pos, col in stops[1:-1]:
            e = r.color_ramp.elements.new(pos)
            e.color = rgb(col)
        L.new(fac, r.inputs["Fac"])
        return r.outputs["Color"]

    def mix(a, b, fac, mode="MIX"):
        m = nt.nodes.new("ShaderNodeMix")
        m.data_type = "RGBA"
        m.blend_type = mode
        if isinstance(fac, float):
            m.inputs["Factor"].default_value = fac
        else:
            L.new(fac, m.inputs["Factor"])
        L.new(a, m.inputs[6])
        L.new(b, m.inputs[7])
        return m.outputs[2]

    def threshold(fac, lo, hi):
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = lo
        mr.inputs["From Max"].default_value = hi
        L.new(fac, mr.inputs["Value"])
        return mr.outputs["Result"]

    # cracks: thin Voronoi cell edges, only in some areas
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = spec.get("crack_scale", 1.6)
    L.new(coords, vor.inputs["Vector"])
    crack = threshold(vor.outputs["Distance"], 0.035, 0.0)          # 1 on the edge
    crack_mask = threshold(noise(0.7), 0.52, 0.62)                  # cracks only in patches
    cm = nt.nodes.new("ShaderNodeMath")
    cm.operation = "MULTIPLY"
    L.new(crack, cm.inputs[0])
    L.new(crack_mask, cm.inputs[1])

    if kind == "asphalt_grit":
        base = ramp(noise(70.0, 2.0), [(0.3, "#3e3e48"), (0.5, "#4c4c56"), (0.7, "#5a5a64")])
        patch = ramp(noise(1.8), [(0.4, "#ffffff"), (0.7, "#a8a8b4")])
        col = mix(base, patch, 1.0, "MULTIPLY")
        dark = nt.nodes.new("ShaderNodeRGB")
        dark.outputs[0].default_value = rgb("#22222a")
        col = mix(col, dark.outputs[0], cm.outputs[0])
    else:
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.inputs["Color1"].default_value = rgb(spec["c"])
        brick.inputs["Color2"].default_value = rgb(spec["c2"])
        brick.inputs["Mortar"].default_value = (0, 0, 0, 1)
        brick.inputs["Scale"].default_value = 1.0
        brick.inputs["Mortar Size"].default_value = spec.get("mortar_size", 0.012)
        brick.inputs["Brick Width"].default_value = spec.get("bw", 0.22)
        brick.inputs["Row Height"].default_value = spec.get("bh", 0.11)
        brick.inputs["Color2"].default_value = rgb(spec["c2"])
        L.new(coords, brick.inputs["Vector"])
        grain = ramp(noise(40.0, 2.0), [(0.3, "#d8d8d8"), (0.7, "#ffffff")])
        col = mix(brick.outputs["Color"], grain, 1.0, "MULTIPLY")
        dirt = ramp(noise(2.2), [(0.45, "#ffffff"), (0.75, "#9c9484")])
        col = mix(col, dirt, 1.0, "MULTIPLY")
        # joints: dark mortar, with green weeds in places
        weeds = ramp(noise(5.0), [(0.55, spec["mortar"]), (0.62, "#4e7a30")])
        col = mix(col, weeds, brick.outputs["Fac"])
        dark = nt.nodes.new("ShaderNodeRGB")
        dark.outputs[0].default_value = rgb("#3a3430")
        col = mix(col, dark.outputs[0], cm.outputs[0])
    L.new(col, bsdf.inputs["Base Color"])


def make_material(name, spec):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = spec.get("rough", 0.7)
    if "metal" in spec:
        bsdf.inputs["Metallic"].default_value = spec["metal"]
    kind = spec.get("kind", "flat")
    col = spec.get("c", "#ff00ff")
    if kind == "flat":
        bsdf.inputs["Base Color"].default_value = rgb(col)
    elif kind == "noise":
        coords = surface_coords(nt)
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = spec.get("scale", 8.0)
        noise.inputs["Detail"].default_value = 4.0
        nt.links.new(coords, noise.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = rgb(col)
        ramp.color_ramp.elements[1].color = rgb(spec["c2"])
        ramp.color_ramp.elements[0].position = 0.35
        ramp.color_ramp.elements[1].position = 0.65
        nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    elif kind == "brick":
        coords = surface_coords(nt)
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.inputs["Color1"].default_value = rgb(col)
        brick.inputs["Color2"].default_value = rgb(spec["c2"])
        brick.inputs["Mortar"].default_value = rgb(spec["mortar"])
        brick.inputs["Scale"].default_value = 1.0
        brick.inputs["Mortar Size"].default_value = spec.get("mortar_size", 0.012)
        brick.inputs["Brick Width"].default_value = spec.get("bw", 0.24)
        brick.inputs["Row Height"].default_value = spec.get("bh", 0.075)
        brick.offset = spec.get("offset", 0.5)
        nt.links.new(coords, brick.inputs["Vector"])
        nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    elif kind == "checker":
        coords = surface_coords(nt)
        chk = nt.nodes.new("ShaderNodeTexChecker")
        chk.inputs["Color1"].default_value = rgb(col)
        chk.inputs["Color2"].default_value = rgb(spec["c2"])
        chk.inputs["Scale"].default_value = spec.get("scale", 3.0)
        nt.links.new(coords, chk.inputs["Vector"])
        nt.links.new(chk.outputs["Color"], bsdf.inputs["Base Color"])
    elif kind == "stripes":
        coords = surface_coords(nt)
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(coords, sep.inputs[0])
        div = nt.nodes.new("ShaderNodeMath")
        div.operation = "DIVIDE"
        div.inputs[1].default_value = spec.get("w", 0.1)
        nt.links.new(sep.outputs["X"], div.inputs[0])
        fl = nt.nodes.new("ShaderNodeMath")
        fl.operation = "FLOOR"
        nt.links.new(div.outputs[0], fl.inputs[0])
        md = nt.nodes.new("ShaderNodeMath")
        md.operation = "MODULO"
        md.inputs[1].default_value = 2.0
        nt.links.new(fl.outputs[0], md.inputs[0])
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        mx.inputs[6].default_value = rgb(col)
        mx.inputs[7].default_value = rgb(spec["c2"])
        nt.links.new(md.outputs[0], mx.inputs["Factor"])
        nt.links.new(mx.outputs[2], bsdf.inputs["Base Color"])
    elif kind in ("asphalt_grit", "paving_grit", "slab_grit"):
        coords = surface_coords(nt)
        grit_material(nt, bsdf, coords, kind, spec)
    if "emit" in spec:
        bsdf.inputs["Emission Color"].default_value = rgb(spec.get("emit_c", col))
        bsdf.inputs["Emission Strength"].default_value = spec["emit"]
    return m


MATERIALS = {
    "paving": dict(kind="paving_grit", c="#b05e48", c2="#94503e", mortar="#5e4a40", bw=0.22, bh=0.11,
                   mortar_size=0.014),
    "slabs": dict(kind="paving_grit", c="#b8b2a6", c2="#a8a296", mortar="#6a665e", bw=0.75, bh=0.75,
                  mortar_size=0.02, crack_scale=0.9),
    "asphalt": dict(kind="asphalt_grit", rough=0.9),
    "curb": dict(kind="noise", c="#c8c4ba", c2="#9e9a90", scale=14),
    "paint_white": dict(c="#e8e8e0"),
    "paint_yellow": dict(c="#e8b830"),
    "grass": dict(kind="noise", c="#4f9a3a", c2="#6cb24a", scale=6, rough=0.95),
    "soil": dict(kind="noise", c="#6a4a30", c2="#5a3e28", scale=10),
    "brick_red": dict(kind="brick", c="#b04838", c2="#963c30", mortar="#c8b4a0"),
    "brick_brown": dict(kind="brick", c="#8a5a40", c2="#744a34", mortar="#b8a690"),
    "stone": dict(kind="noise", c="#d0c8b4", c2="#bcb4a0", scale=12),
    "trim_white": dict(c="#ecebe4", rough=0.5),
    "concrete": dict(kind="noise", c="#a8acb2", c2="#989ca4", scale=10),
    "metal_dark": dict(c="#2e3038", rough=0.4, metal=0.6),
    "metal_light": dict(c="#b8bec8", rough=0.35, metal=0.7),
    "glass": dict(c="#3c5a80", rough=0.08),
    "glass_office": dict(c="#5a88b8", rough=0.05),
    "lamp_glass": dict(c="#fff0c0", emit=2.0, emit_c="#ffe8a8"),
    "roof": dict(kind="noise", c="#7c7c84", c2="#6a6a72", scale=20),
    "leaves": dict(kind="noise", c="#2a5c30", c2="#4c8438", scale=5, rough=0.9),
    "leaves_light": dict(kind="noise", c="#3a7a36", c2="#62983e", scale=7, rough=0.9),
    "trunk": dict(c="#6a4428"),
    "pot": dict(c="#b0603c"),
    "terracotta": dict(kind="noise", c="#b8643c", c2="#9a5030", scale=30),
    "slate": dict(kind="brick", c="#4a5260", c2="#3e4654", mortar="#2c323c", bw=0.35, bh=0.12),
    "flower_red": dict(kind="noise", c="#d8303c", c2="#b81c2c", scale=40),
    "flower_pink": dict(kind="noise", c="#e86aa8", c2="#c84a88", scale=40),
    "flower_yellow": dict(kind="noise", c="#f0c830", c2="#d8a018", scale=40),
    "flower_white": dict(kind="noise", c="#f4f0e8", c2="#d8d4cc", scale=40),
    "leaves_dark": dict(kind="noise", c="#1c4628", c2="#2e5e34", scale=6, rough=0.9),
    "chalkboard": dict(c="#26302c", rough=0.9),
    "chalk": dict(c="#e8e8e0"),
    "red_paint": dict(c="#c02828", rough=0.4),
    "wood": dict(kind="noise", c="#a8703c", c2="#946030", scale=6),
    "wood_dark": dict(c="#5c3a20"),
    "wood_green": dict(c="#2c6a44", rough=0.45),
    "wood_blue": dict(c="#2e4e8a", rough=0.45),
    "wood_red": dict(c="#9a2e2a", rough=0.45),
    "brass": dict(c="#d8a838", rough=0.3, metal=0.8),
    "awning_green": dict(c="#2a8a4c", rough=0.8),
    "awning_white": dict(c="#ecebe0", rough=0.8),
    "sign_green": dict(c="#1e6a3a", rough=0.5),
    "sign_text": dict(c="#fff4d8", emit=0.6),
    "shop_light": dict(c="#f4e2b4", emit=0.5),
    "goods_red": dict(c="#d83a3a", rough=0.5),
    "goods_yellow": dict(c="#f0c832", rough=0.5),
    "goods_green": dict(c="#4caa44", rough=0.5),
    "goods_orange": dict(c="#f08a2a", rough=0.5),
    "goods_blue": dict(c="#3a6ad0", rough=0.5),
    "goods_pink": dict(c="#e070b0", rough=0.5),
    "goods_white": dict(c="#f0f0ea", rough=0.5),
    "tiles_checker": dict(kind="checker", c="#e8e8e0", c2="#3a4a7a", scale=2.0, rough=0.3),
    "plaster_cream": dict(kind="noise", c="#e6d6aa", c2="#dccc9e", scale=6),
    "plaster_mint": dict(kind="noise", c="#9ccab0", c2="#92c0a6", scale=6),
    "floor_wood": dict(kind="brick", c="#c08048", c2="#a86c3c", mortar="#6a4224", bw=1.2, bh=0.14,
                       mortar_size=0.008, offset=0.37, rough=0.35),
    "mat_red": dict(c="#a82c2c", rough=0.9),
    "wall_plaster": dict(kind="noise", c="#f0e2bc", c2="#e8d8b0", scale=5),
    "fridge_white": dict(c="#e4e8ec", rough=0.3),
    "fridge_glass": dict(c="#b8e0f8", emit=0.8, emit_c="#d8f0ff"),
    "screen": dict(c="#40c0b0", emit=1.0),
    "gold": dict(c="#e8b840", rough=0.25, metal=0.9),
    "gold_dark": dict(c="#a87c28", rough=0.35, metal=0.8),
    "gold_bright": dict(c="#ffd860", emit=0.8),
    "water": dict(c="#2a5a8a", rough=0.05),
    "pond_edge": dict(kind="noise", c="#a8a294", c2="#948e80", scale=10),
    "path_dirt": dict(kind="noise", c="#c8a878", c2="#b8986a", scale=8),
    "plaza_stone": dict(kind="brick", c="#d8d0bc", c2="#c8c0aa", mortar="#9a9284", bw=0.6, bh=0.6,
                        mortar_size=0.015, offset=0.0),
    "plaza_gold": dict(kind="checker", c="#e8dcc0", c2="#c8a858", scale=1.5, rough=0.3),
    "barrier_stripes": dict(kind="checker", c="#f08a1a", c2="#f4f2ea", scale=4.0),
    "orange_paint": dict(c="#f07a1a", rough=0.5),
    "metal_grey": dict(c="#8a8c94", rough=0.4, metal=0.5),
    "bin_green": dict(c="#2e5a3a", rough=0.5),
    "fence_wood": dict(kind="noise", c="#8a6a48", c2="#6e543a", scale=12),
    "chain_link": dict(kind="checker", c="#5a5c64", c2="#3a3c44", scale=40.0, rough=0.5),
    "poster_red": dict(kind="noise", c="#c83838", c2="#f0d8a0", scale=9),
    "poster_yellow": dict(kind="noise", c="#e8c040", c2="#3a4a8a", scale=7),
    "poster_blue": dict(kind="noise", c="#3a6ac8", c2="#f0ece0", scale=8),
    "milk_white": dict(c="#f4f4f0", rough=0.5),
    "print_cream": dict(c="#f6eed2", rough=0.5),
    "bottle_green": dict(c="#3c8a4a", rough=0.15),
    "bottle_clear": dict(c="#a8d4e8", rough=0.1),
    "bottle_brown": dict(c="#8a4a24", rough=0.15),
    "shelf_base": dict(c="#7a7e88", rough=0.5),
    "shelf_back": dict(c="#e8e4dc", rough=0.6),
    "shelf_white": dict(c="#f0eee8", rough=0.4),
    "shelf_end": dict(c="#a8703c", rough=0.5),
    "price_yellow": dict(c="#f4d23a", rough=0.5),
    "fridge_light": dict(c="#e8f4fc", emit=0.9, emit_c="#f0f8ff"),
    "sign_blue": dict(c="#2a5aa8", rough=0.5),
    "apple_red": dict(c="#c8282a", rough=0.35),
    "orange_fruit": dict(c="#f08a1a", rough=0.5),
    "banana_yellow": dict(c="#f2d040", rough=0.5),
    "lettuce_green": dict(c="#6ab84a", rough=0.7),
    "belt_dark": dict(c="#26262c", rough=0.8),
    "basket_red": dict(c="#c83232", rough=0.5),
    "crate": dict(kind="brick", c="#b08048", c2="#a07040", mortar="#6a4a28", bw=0.6, bh=0.12),
    # ---- interiors v2 ----
    "wp_cream": dict(kind="stripes", c="#f1dfb2", c2="#e8d09c", w=0.11),
    "wp_peach": dict(kind="stripes", c="#f0cdb4", c2="#e7bda0", w=0.12),
    "wp_sage": dict(kind="stripes", c="#b9d2b0", c2="#a9c6a0", w=0.1),
    "wp_blue": dict(kind="stripes", c="#b8cce0", c2="#a6bdd6", w=0.1),
    "wall_cap": dict(c="#f7f0dc", rough=0.6),
    "floor_edge": dict(c="#5a4030", rough=0.8),
    "floor_wood2": dict(kind="brick", c="#b87440", c2="#9e5f34", mortar="#5c3a20", bw=1.0, bh=0.13,
                        mortar_size=0.01, offset=0.31, rough=0.35),
    "floor_wood_dark": dict(kind="brick", c="#8a5a38", c2="#7a4c2e", mortar="#3e2818", bw=1.1, bh=0.14,
                            mortar_size=0.01, offset=0.43, rough=0.35),
    "tile_cafe": dict(kind="checker", c="#efe4c8", c2="#a8402c", scale=2.2, rough=0.25),
    "tile_kitchen": dict(kind="checker", c="#f0ead6", c2="#5f9a8c", scale=2.4, rough=0.25),
    "tile_bath": dict(kind="brick", c="#cfe4ea", c2="#bad6df", mortar="#8da7b0", bw=0.3, bh=0.3,
                      mortar_size=0.03, offset=0.0, rough=0.2),
    "tile_wall_white": dict(kind="brick", c="#f2f2ee", c2="#e6e8e6", mortar="#a8b0b4", bw=0.25, bh=0.15,
                            mortar_size=0.04, offset=0.5, rough=0.2),
    "store_floor": dict(kind="brick", c="#9a9ea6", c2="#8e929a", mortar="#5e6068", bw=0.6, bh=0.6,
                        mortar_size=0.02, offset=0.0),
    "rug_red": dict(c="#a83a34", rough=0.95),
    "rug_cream": dict(c="#ecdcb4", rough=0.95),
    "rug_navy": dict(c="#34487a", rough=0.95),
    "rug_green": dict(c="#4e8a5a", rough=0.95),
    "rug_gold": dict(c="#d8a84a", rough=0.95),
    "rug_teal": dict(c="#4a9a96", rough=0.95),
    "cardboard": dict(kind="noise", c="#bc8e5c", c2="#a87c4c", scale=14),
    "cardboard_dark": dict(c="#8e6a42"),
    "window_sky": dict(c="#d4ecff", emit=1.4, emit_c="#d8eeff"),
    "clock_face": dict(c="#f6f2e2", rough=0.4),
    "tv_screen": dict(c="#2c4c80", emit=0.9, emit_c="#3a68b0"),
    "tv_body": dict(c="#1c1c22", rough=0.4),
    "bucket_yellow": dict(c="#e8c02c", rough=0.4),
    "mop": dict(c="#d8d4c4", rough=0.9),
    "poster_green": dict(kind="noise", c="#4a9a5a", c2="#f0e8c8", scale=9),
    "poster_orange": dict(kind="noise", c="#e88a3a", c2="#f6e8c0", scale=8),
    "chalk_menu": dict(c="#2a3430", rough=0.9),
    "glass_lid": dict(c="#bfe0f0", rough=0.05),
    "ice_cream_pink": dict(c="#f0a0c0"),
    "frozen_blue": dict(c="#4a78c8"),
    "metal_shelf": dict(c="#7c828c", rough=0.4, metal=0.5),
    "sofa_orange": dict(c="#c4643a", rough=0.9),
    "lamp_shade": dict(c="#f8e8b8", emit=0.5, emit_c="#ffe8b0"),
    "plate_white": dict(c="#f4f4ee", rough=0.3),
    "curtain_red": dict(c="#b8503c", rough=0.95),
    "frame_wood": dict(c="#6a4428"),
    "picture_sea": dict(kind="noise", c="#3a7aa8", c2="#e8d8a0", scale=6),
    "picture_hill": dict(kind="noise", c="#5a9a52", c2="#e8c870", scale=7),
    "tag_red": dict(c="#d83a2a", rough=0.5),
    # ---- interiors v2b ----
    "marble": dict(kind="checker", c="#eceef2", c2="#cfd4dc", scale=0.75, rough=0.12),
    "wall_panel_cold": dict(kind="brick", c="#dfe3e9", c2="#d2d7de", mortar="#c9a550", bw=1.5, bh=3.6,
                            mortar_size=0.012, offset=0.0, rough=0.25),
    "steel": dict(c="#c4cad4", rough=0.25, metal=0.8),
    "cork": dict(kind="noise", c="#b98a52", c2="#a37640", scale=34),
    "neon_red": dict(c="#ff5048", emit=3.0, emit_c="#ff3a30"),
    "neon_blue": dict(c="#60c8ff", emit=3.0, emit_c="#40b0ff"),
    "neon_gold": dict(c="#ffd870", emit=2.5, emit_c="#ffc850"),
    "chrome": dict(c="#d8dde6", rough=0.15, metal=0.9),
    "robot_white": dict(c="#f0f4f8", rough=0.2),
    "robot_eye": dict(c="#60e0ff", emit=4.0, emit_c="#50d8ff"),
    "tile_bw": dict(kind="checker", c="#f2f0e8", c2="#2a2a34", scale=2.6, rough=0.2),
    "diner_red": dict(c="#b8302c", rough=0.45),
    "diner_teal": dict(c="#3a9a92", rough=0.45),
    "locker_blue": dict(c="#4a78b8", rough=0.4, metal=0.3),
    "locker_green": dict(c="#4a9a6a", rough=0.4, metal=0.3),
    "locker_orange": dict(c="#e08a40", rough=0.4, metal=0.3),
    "locker_grey": dict(c="#8a909a", rough=0.4, metal=0.3),
    "stall_panel": dict(c="#6a9ab4", rough=0.5),
    "carpet_blue": dict(kind="noise", c="#3a5a8a", c2="#34527e", scale=40, rough=1.0),
    "carpet_green": dict(kind="noise", c="#4a7a5a", c2="#42705a", scale=40, rough=1.0),
    "book_a": dict(c="#9a2e2a"), "book_b": dict(c="#2e5a8a"), "book_c": dict(c="#3a7a4a"),
    "book_d": dict(c="#c8a038"), "book_e": dict(c="#6a3a7a"), "book_f": dict(c="#e8e0cc"),
    "paper_cream": dict(c="#f6f0dc", rough=0.9),
    "fake_leaf": dict(c="#58b868", rough=0.35),
    "wp_grey": dict(c="#c8ccd4", rough=0.3),
    "glass_pane": dict(c="#a8d0e8", rough=0.03),
    "pie_crust": dict(c="#d89a50"),
    "pie_red": dict(c="#b83a44"),
    "coffee": dict(c="#3a2418", rough=0.3),
    "wp_shabby": dict(kind="noise", c="#cbbb90", c2="#a89572", scale=4),
    "wp_shabby_blue": dict(kind="noise", c="#92a9b0", c2="#788f98", scale=4),
    "plaster_bare": dict(kind="noise", c="#aaa496", c2="#8a8478", scale=9, rough=1.0),
    "floor_bare": dict(kind="brick", c="#8c6c48", c2="#76593a", mortar="#2e2016", bw=1.0, bh=0.12,
                       mortar_size=0.03, offset=0.37, rough=0.8),
    "stain": dict(c="#4a3a28", rough=1.0),
    "tile_dirty": dict(kind="brick", c="#bcc4c0", c2="#a8b2b0", mortar="#5a6260", bw=0.25, bh=0.25,
                       mortar_size=0.05, offset=0.0, rough=0.5),
    "tile_floor_dirty": dict(kind="brick", c="#b0bcbc", c2="#9aa8a8", mortar="#4a5252", bw=0.3, bh=0.3,
                             mortar_size=0.05, offset=0.0, rough=0.5),
    "mattress": dict(kind="noise", c="#8a98a8", c2="#6e7c8c", scale=12, rough=1.0),
    "blanket_old": dict(c="#8a4a3a", rough=1.0),
    "fridge_old": dict(c="#d6cea0", rough=0.5),
    "hotplate": dict(c="#2a2a2e", rough=0.5),
    "coil_hot": dict(c="#ff5a2a", emit=2.0, emit_c="#ff4a1a"),
    "rust": dict(c="#8a4a2a", rough=0.9),
    "bulb": dict(c="#fff2c0", emit=8.0, emit_c="#ffe8a0"),
    "cord_black": dict(c="#1a1a1a"),
}



# ---------------------------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------------------------
def add_box(bm, p):
    x0, x1 = sorted((p["x0"] * CELL_M, p["x1"] * CELL_M))
    y0, y1 = sorted((-p["y0"] * CELL_M, -p["y1"] * CELL_M))
    z0, z1 = p["z0"], p["z1"]
    vs = [bm.verts.new(v) for v in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                    (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f])


def add_wedge(bm, p):
    # top edge against the wall at y0 (engine), bottom outer edge at y1, plus a valance strip
    x0, x1 = p["x0"] * CELL_M, p["x1"] * CELL_M
    ya, yb = -p["y0"] * CELL_M, -p["y1"] * CELL_M
    zt, zb = p["z_top"], p["z_bottom"]
    t = 0.04
    pts = [(x0, ya, zt), (x1, ya, zt), (x1, yb, zb), (x0, yb, zb),
           (x0, ya, zt + t), (x1, ya, zt + t), (x1, yb, zb + t), (x0, yb, zb + t)]
    vs = [bm.verts.new(v) for v in pts]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f])
    val = [(x0, yb, zb - 0.22), (x1, yb, zb - 0.22), (x1, yb, zb + t), (x0, yb, zb + t)]
    vv = [bm.verts.new(v) for v in val]
    bm.faces.new(vv)


def add_cyl(bm, p):
    axis = p.get("axis", "z")
    if axis != "z":
        from mathutils import Matrix
        depth = p["z1"] - p["z0"]
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=p.get("verts", 24), radius1=p["r"],
                                    radius2=p.get("r2", p["r"]), depth=depth)
        rot = Matrix.Rotation(math.radians(90), 4, "X" if axis == "y" else "Y")
        bmesh.ops.transform(bm, matrix=rot, verts=res["verts"])
        x, y, _ = bl(p["x"], p["y"])
        bmesh.ops.translate(bm, verts=res["verts"], vec=Vector((x, y, p["z0"])))
        return
    r = p["r"]
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=p.get("verts", 16), radius1=r, radius2=p.get("r2", r),
                                depth=p["z1"] - p["z0"])
    x, y, _ = bl(p["x"], p["y"])
    bmesh.ops.translate(bm, verts=res["verts"], vec=Vector((x, y, (p["z0"] + p["z1"]) / 2)))


def add_sphere(bm, p):
    res = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=p["r"])
    for v in res["verts"]:
        v.co.z *= p.get("sz", 1.0)
    x, y, _ = bl(p["x"], p["y"])
    bmesh.ops.translate(bm, verts=res["verts"], vec=Vector((x, y, p["z"])))


def add_poly(bm, p):
    """One flat polygon through points (x, y in cells, z in metres), e.g. a gable end."""
    vs = [bm.verts.new(bl(x, y, z)) for (x, y, z) in p["pts"]]
    bm.faces.new(vs)


def add_tube(bm, p):
    """Smooth round tube along a polyline (Catmull-Rom), e.g. the curved arm of a street lamp."""
    pts = [Vector(bl(x, y, z)) for (x, y, z) in p["pts"]]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    path = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(6):
            t = k / 6
            path.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                               (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    path.append(pts[-1])
    r, n = p["r"], 10
    rings = []
    for i, c in enumerate(path):
        d = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
        a = d.cross(Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))).normalized()
        b = d.cross(a).normalized()
        rings.append([bm.verts.new(c + (a * math.cos(2 * math.pi * j / n) + b * math.sin(2 * math.pi * j / n)) * r)
                      for j in range(n)])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(n):
            bm.faces.new((r0[j], r0[(j + 1) % n], r1[(j + 1) % n], r1[j]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])


MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "art_source", "quaternius_buildings")

# Colour schemes for the Quaternius buildings: material base name -> sRGB hex.
SCHEMES = {
    "red": {"Main": "#b4523e", "Bricks": "#8e3c30", "Light": "#efe2c0", "Dark": "#4a3434"},
    "cream": {"Main": "#e8d6a8", "Bricks": "#cdb688", "Light": "#f6f2e6", "Dark": "#6a5844"},
    "blue": {"Main": "#7c90cc", "Bricks": "#5c6ea8", "Light": "#eeeef4", "Dark": "#3a4060"},
    "mint": {"Main": "#9ccab2", "Bricks": "#7aae96", "Light": "#f2f4ee", "Dark": "#3c5a50"},
    "purple": {"Main": "#9a84c4", "Bricks": "#7a66a4", "Light": "#f0ecf6", "Dark": "#463c60"},
    "orange": {"Main": "#e08a50", "Bricks": "#c06c3c", "Light": "#f6ead8", "Dark": "#5a3a2a"},
    "grey": {"Main": "#b8b8bc", "Bricks": "#9a9aa0", "Light": "#f0f0f0", "Dark": "#404048"},
}


def add_model(p, layer_visible):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(MODEL_DIR, p["name"] + ".fbx"))
    obs = [o for o in bpy.data.objects if o not in before]
    scheme = SCHEMES.get(p["colours"], {})
    for o in obs:
        if o.type != "MESH":
            continue
        for slot in o.material_slots:
            if slot.material is None:
                continue
            m = slot.material.copy()
            base = m.name.split(".")[0]
            if m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
                bsdf = m.node_tree.nodes["Principled BSDF"]
                bsdf.inputs["Alpha"].default_value = 1.0      # the FBX files import with alpha 0
                bsdf.inputs["Roughness"].default_value = 0.7
                if base in scheme:
                    bsdf.inputs["Base Color"].default_value = rgb(scheme[base])
                if base == "Glass":
                    bsdf.inputs["Roughness"].default_value = 0.1
            slot.material = m
        o.rotation_euler = (o.rotation_euler.x, o.rotation_euler.y,
                            o.rotation_euler.z + (math.radians(90) if p["front"] == "right" else 0))
        o.scale = tuple(v * p["scale"] for v in o.scale)
        o.visible_camera = (p["layer"] == layer_visible)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in obs if o.type == "MESH" for c in o.bound_box]
    mnx, mxx = min(v.x for v in pts), max(v.x for v in pts)
    mny, mxy = min(v.y for v in pts), max(v.y for v in pts)
    mnz = min(v.z for v in pts)
    x0, y0, x1, y1 = p["fp"]
    if p["front"] == "left":
        dx = x0 * CELL_M - mnx          # left edge
        dy = -y1 * CELL_M - mny         # facade (min Blender Y) on the facade line
    else:
        dx = x1 * CELL_M - mxx          # facade (max Blender X) on the facade line
        dy = -y0 * CELL_M - mxy         # top edge (engine y0 = max Blender Y)
    for o in obs:
        if o.parent is None:
            o.location = (o.location.x + dx, o.location.y + dy, o.location.z - mnz)


KIT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "art_source", "quaternius_downtown")


def fix_kit_material(m):
    """Downtown City MegaKit materials mix the texture with a vertex-colour wear mask meant for game
    engine shaders, and reference normal/ORM maps we don't ship. Use the base colour texture only."""
    if not m.use_nodes or "Principled BSDF" not in m.node_tree.nodes:
        return
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    for link in list(nt.links):
        if link.to_node == bsdf and link.to_socket.name in ("Normal", "Metallic", "Roughness", "Alpha"):
            nt.links.remove(link)
    base_tex = None
    for nd in nt.nodes:
        if nd.type == "TEX_IMAGE" and nd.image is not None:
            n = nd.image.name
            if "Normal" in n or "ORM" in n:
                nd.image = None
            elif base_tex is None:
                base_tex = nd
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.75
    bsdf.inputs["Alpha"].default_value = 1.0
    if "Glass" in m.name:
        for link in list(nt.links):
            if link.to_node == bsdf and link.to_socket.name == "Base Color":
                nt.links.remove(link)
        bsdf.inputs["Base Color"].default_value = rgb("#3c5a80")
        bsdf.inputs["Roughness"].default_value = 0.08
    elif base_tex is not None:
        nt.links.new(base_tex.outputs["Color"], bsdf.inputs["Base Color"])
        if "interior" in base_tex.image.name.lower():
            bsdf.inputs["Emission Color"].default_value = (1, 1, 1, 1)
            nt.links.new(base_tex.outputs["Color"], bsdf.inputs["Emission Color"])
            bsdf.inputs["Emission Strength"].default_value = 0.35


def add_kit(p, layer_visible):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(KIT_DIR, p["name"] + ".gltf"))
    obs = [o for o in bpy.data.objects if o not in before]
    for o in obs:
        if o.type == "MESH":
            for slot in o.material_slots:
                if slot.material is not None and not slot.material.get("tl_fixed"):
                    fix_kit_material(slot.material)
                    slot.material["tl_fixed"] = True
        o.visible_camera = (p["layer"] == layer_visible)
    for o in obs:
        if o.parent is None:
            o.rotation_euler = (o.rotation_euler.x, o.rotation_euler.y, o.rotation_euler.z + math.radians(p["rot"]))
            o.scale = tuple(v * p["scale"] for v in o.scale)
            x, y, _ = bl(p["x"], p["y"])
            o.location = (x, y, p["z"])



PROP_DIRS = {"house": ["quaternius_house"], "food": ["quaternius_food"]}
ART_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "art_source")
_PROP_TEMPLATES = {}


def _prop_path(name):
    pack, base = name.split("/")
    for d in PROP_DIRS[pack]:
        full = d if os.path.isabs(d) else os.path.join(ART_DIR, d)
        f = os.path.join(full, base + ".fbx")
        if os.path.exists(f):
            return f
    raise FileNotFoundError(name)


def _prop_template(name, colours):
    """Imports a prop once per (name, colours) and keeps it unlinked as a template."""
    key = (name, tuple(sorted(colours.items())))
    if key in _PROP_TEMPLATES:
        return _PROP_TEMPLATES[key]
    from mathutils import Matrix
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=_prop_path(name))
    obs = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    meshes = [o for o in obs if o.type == "MESH"]
    worlds = {o: o.matrix_world.copy() for o in meshes}
    for o in meshes:
        for slot in o.material_slots:
            m = slot.material
            if m is None:
                continue
            base = m.name.split(".")[0]
            if m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
                bsdf = m.node_tree.nodes["Principled BSDF"]
                bsdf.inputs["Alpha"].default_value = 1.0
                bsdf.inputs["Roughness"].default_value = 0.6
                if base in colours:
                    bsdf.inputs["Base Color"].default_value = rgb(colours[base])
                if base in ("Glass", "Mirror"):
                    bsdf.inputs["Roughness"].default_value = 0.08
                if base == "Light":
                    bsdf.inputs["Emission Color"].default_value = (1, 0.9, 0.6, 1)
                    bsdf.inputs["Emission Strength"].default_value = 1.5
    pts = [worlds[o] @ Vector(c) for o in meshes for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    for o in obs:
        for c in list(o.users_collection):
            c.objects.unlink(o)
    _PROP_TEMPLATES[key] = (meshes, worlds, mn, mx)
    return _PROP_TEMPLATES[key]


def add_prop(p, layer_visible):
    from mathutils import Matrix
    meshes, worlds, mn, mx = _prop_template(p["name"], p["colours"])
    root = bpy.data.objects.new("prop", None)
    bpy.context.scene.collection.objects.link(root)
    for o in meshes:
        c = o.copy()
        c.parent = root
        c.matrix_parent_inverse = Matrix.Identity(4)
        c.matrix_basis = worlds[o]
        c.visible_camera = (p["layer"] == layer_visible)
        bpy.context.scene.collection.objects.link(c)
    cx, cy = (mn.x + mx.x) / 2, (mn.y + mx.y) / 2
    x, y, _ = bl(p["x"], p["y"])
    root.matrix_world = (Matrix.Translation((x, y, p["z"])) @ Matrix.Rotation(math.radians(p["rot"]), 4, "Z")
                         @ Matrix.Scale(p["scale"], 4) @ Matrix.Translation((-cx, -cy, -mn.z)))


def build(scene_obj, layer_visible):
    mats = {}

    def mat(name):
        if name not in mats:
            mats[name] = make_material(name, MATERIALS[name])
        return mats[name]

    groups = {}
    for p in scene_obj.prims:
        if p["type"] == "model":
            add_model(p, layer_visible)
        elif p["type"] == "kit":
            add_kit(p, layer_visible)
        elif p["type"] == "prop":
            add_prop(p, layer_visible)
    for p in scene_obj.prims:
        if p["type"] in ("text", "model", "kit", "prop"):
            continue
        groups.setdefault((p["layer"], p["mat"]), []).append(p)

    for (layer, mname), prims in groups.items():
        bm = bmesh.new()
        smooth = False
        for p in prims:
            t = p["type"]
            if t == "box":
                add_box(bm, p)
            elif t == "wedge":
                add_wedge(bm, p)
            elif t == "cyl":
                add_cyl(bm, p)
                smooth = True
            elif t == "sphere":
                add_sphere(bm, p)
                smooth = True
            elif t == "poly":
                add_poly(bm, p)
            elif t == "tube":
                add_tube(bm, p)
                smooth = True
        me = bpy.data.meshes.new(f"{layer}_{mname}")
        bm.to_mesh(me)
        bm.free()
        if smooth:
            for poly in me.polygons:
                poly.use_smooth = True
        me.materials.append(mat(mname))
        ob = bpy.data.objects.new(me.name, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.visible_camera = (layer == layer_visible)

    for p in scene_obj.prims:
        if p["type"] != "text":
            continue
        cu = bpy.data.curves.new("txt", type="FONT")
        cu.body = p["s"]
        cu.size = p["size"]
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.extrude = p["extrude"]
        ob = bpy.data.objects.new("txt", cu)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = bl(p["x"], p["y"], p["z"])
        if p["face"] == "left":
            ob.rotation_euler = (math.radians(90), 0, 0)
        else:
            ob.rotation_euler = (math.radians(90), 0, math.radians(90))
        cu.materials.append(mat(p["mat"]))
        ob.visible_camera = (p["layer"] == layer_visible)


def setup_camera_and_lights(s, scale):
    sc = bpy.context.scene
    sc.render.resolution_x = s.img_w * scale
    sc.render.resolution_y = s.img_h * scale
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.sensor_fit = "HORIZONTAL"
    cam.ortho_scale = s.img_w * math.cos(math.radians(45)) * CELL_M / 16
    cam.clip_start = 0.1
    cam.clip_end = 500
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    co.rotation_euler = (math.radians(60), 0, math.radians(45))
    a = s.img_w / 2 - s.origin_x
    b = s.img_h / 2 - s.origin_y
    ux, uy = b + a / 2, b - a / 2
    target = Vector(bl(ux / 16, uy / 16, 0))
    fwd = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)),
                  math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))
    co.location = target - fwd * 80

    world = bpy.data.worlds.new("world")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    if s.sun:
        bg.inputs["Color"].default_value = (0.55, 0.66, 0.85, 1)
        bg.inputs["Strength"].default_value = 0.9
        sun = bpy.data.lights.new("sun", "SUN")
        sun.energy = 4.2
        sun.angle = math.radians(4)
        sun.color = (1.0, 0.96, 0.88)
        so = bpy.data.objects.new("sun", sun)
        sc.collection.objects.link(so)
        d = Vector((-0.25, 0.7, -0.65)).normalized()
        so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    else:
        wc = getattr(s, "world", (0.9, 0.8, 0.65))
        bg.inputs["Color"].default_value = (wc[0], wc[1], wc[2], 1)
        bg.inputs["Strength"].default_value = getattr(s, "world_strength", 0.35)
        d = Vector((-0.25, 0.7, -0.65)).normalized()
        sun = bpy.data.lights.new("fill", "SUN")
        sun.energy = getattr(s, "fill_energy", 1.2)
        sun.angle = math.radians(20)
        sun.color = getattr(s, "fill", (1.0, 0.92, 0.8))
        so = bpy.data.objects.new("fill", sun)
        sc.collection.objects.link(so)
        so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    for L in s.lights:
        pl = bpy.data.lights.new("pt", "POINT")
        pl.energy = L["energy"]
        pl.color = L["colour"]
        pl.shadow_soft_size = L["radius"]
        po = bpy.data.objects.new("pt", pl)
        sc.collection.objects.link(po)
        po.location = bl(L["x"], L["y"], L["z"])


def add_grime(m):
    """Darkens creases, corners and the bottom of walls with an ambient-occlusion multiply: the
    lived-in, slightly dirty look of classic pre-rendered city games."""
    if not m.use_nodes or "Principled BSDF" not in m.node_tree.nodes or m.get("tl_grime"):
        return
    m["tl_grime"] = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    src = None
    for link in list(nt.links):
        if link.to_node == bsdf and link.to_socket.name == "Base Color":
            src = link.from_socket
            nt.links.remove(link)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 0.9
    ao.samples = 8
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.32, 0.3, 0.38, 1)     # cool, slightly purple grime
    ramp.color_ramp.elements[1].position = 0.85
    nt.links.new(ao.outputs["AO"], ramp.inputs["Fac"])
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    if src is not None:
        nt.links.new(src, mul.inputs[6])
    else:
        mul.inputs[6].default_value = bsdf.inputs["Base Color"].default_value
    nt.links.new(ramp.outputs["Color"], mul.inputs[7])
    nt.links.new(mul.outputs[2], bsdf.inputs["Base Color"])


def stylize(layer_visible):
    """Outlines (Freestyle) on the visible layer + grime on every material."""
    sc = bpy.context.scene
    col = bpy.data.collections.new("tl_visible")
    sc.collection.children.link(col)
    for o in list(sc.objects):
        if o.type in ("MESH", "FONT") and o.visible_camera:
            col.objects.link(o)
    for m in bpy.data.materials:
        add_grime(m)
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    sc.render.line_thickness = 1.0
    vl = sc.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(120)
    ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("tl")
    ls.select_by_collection = True
    ls.collection = col
    ls.select_by_visibility = True
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("tl_lines")
    style = ls.linestyle
    style.color = (0.07, 0.05, 0.09)
    style.thickness = 1.6
    style.alpha = 0.85


# Material classes for the ID pass (special palette entries in the game): 1 window glass (lit at
# night), 2 water (ripple palette cycling), 3 lamp glass (bright at night).
def material_class(name):
    n = name.lower()
    if "water" in n:
        return 2
    if "lamp_glass" in n:
        return 3
    if "glass" in n and "fridge" not in n:
        return 1
    return 0


def id_materials():
    """Replace every material with a flat emission that encodes, per pixel, the iso depth of the
    surface (world x + y in engine units, 16 per cell) in R (low byte) and G (high byte) and the
    material class in B (class * 40). Rendered with 1 sample, no filter, Raw view."""
    for m in list(bpy.data.materials):
        cls = material_class(m.name)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Position"], sep.inputs[0])

        def op(kind, a, b=None, value=None):
            n = nt.nodes.new("ShaderNodeMath")
            n.operation = kind
            for i, v in enumerate((a, b)):
                if v is None:
                    continue
                if isinstance(v, (int, float)):
                    n.inputs[i].default_value = v
                else:
                    nt.links.new(v, n.inputs[i])
            if value is not None:
                n.inputs[1].default_value = value
            return n.outputs[0]

        d = op("SUBTRACT", sep.outputs["X"], sep.outputs["Y"])          # engine x + y = (bx - by) / CELL_M * 16
        d = op("MULTIPLY", d, 16.0 / CELL_M)
        d = op("MAXIMUM", d, 0.0)
        d = op("FLOOR", op("ADD", d, 0.5))
        low = op("DIVIDE", op("MODULO", d, 256.0), 255.0)
        high = op("DIVIDE", op("FLOOR", op("DIVIDE", d, 256.0)), 255.0)
        comb = nt.nodes.new("ShaderNodeCombineColor")
        nt.links.new(low, comb.inputs[0])
        nt.links.new(high, comb.inputs[1])
        comb.inputs[2].default_value = cls * 40 / 255.0
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = 1.0
        nt.links.new(comb.outputs[0], em.inputs["Color"])
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(em.outputs[0], out.inputs["Surface"])
        m.blend_method = "OPAQUE"


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    ident, layer, out = argv[0], argv[1], argv[2]
    scale = int(argv[3]) if len(argv) > 3 else 2
    samples = int(argv[4]) if len(argv) > 4 else 64
    s = next(f() for f in scn.SCENES if f().ident == ident)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.cycles.max_bounces = 4
    sc.cycles.seed = 1
    sc.render.film_transparent = True
    sc.render.filter_size = 1.2
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.filepath = out
    id_pass = len(argv) > 6 and argv[6] == "id"
    build(s, layer)
    setup_camera_and_lights(s, scale)
    if id_pass:
        id_materials()
        for o in sc.objects:
            if o.type == "LIGHT":
                o.hide_render = True
        sc.cycles.samples = 1
        sc.cycles.max_bounces = 0
        sc.render.filter_size = 0.01
        sc.render.dither_intensity = 0.0
        sc.view_settings.view_transform = "Raw"
        sc.view_settings.look = "None"
        sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    else:
        stylize(layer)
    if len(argv) > 5 and argv[5]:
        # optional crop for quick tests: x0,y0,x1,y1 in image pixels (top-left origin)
        x0, y0, x1, y1 = (float(v) for v in argv[5].split(","))
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x = x0 / s.img_w
        sc.render.border_max_x = x1 / s.img_w
        sc.render.border_min_y = 1 - y1 / s.img_h
        sc.render.border_max_y = 1 - y0 / s.img_h
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
