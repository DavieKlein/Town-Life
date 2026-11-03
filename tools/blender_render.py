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
    if "emit" in spec:
        bsdf.inputs["Emission Color"].default_value = rgb(spec.get("emit_c", col))
        bsdf.inputs["Emission Strength"].default_value = spec["emit"]
    return m


MATERIALS = {
    "paving": dict(kind="brick", c="#b8644a", c2="#a0503c", mortar="#7a5a4a", bw=0.22, bh=0.11, mortar_size=0.01),
    "asphalt": dict(kind="noise", c="#4a4a52", c2="#5a5a62", scale=14, rough=0.9),
    "curb": dict(kind="noise", c="#b4b2aa", c2="#a2a098", scale=10),
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
    "leaves": dict(kind="noise", c="#3c7a34", c2="#5a9a40", scale=4, rough=0.9),
    "leaves_light": dict(kind="noise", c="#4c9a3c", c2="#74b850", scale=6, rough=0.9),
    "trunk": dict(c="#6a4428"),
    "pot": dict(c="#b0603c"),
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
    r = p["r"]
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=p.get("verts", 16), radius1=r, radius2=r,
                                depth=p["z1"] - p["z0"])
    x, y, _ = bl(p["x"], p["y"])
    bmesh.ops.translate(bm, verts=res["verts"], vec=Vector((x, y, (p["z0"] + p["z1"]) / 2)))


def add_sphere(bm, p):
    res = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=p["r"])
    for v in res["verts"]:
        v.co.z *= p.get("sz", 1.0)
    x, y, _ = bl(p["x"], p["y"])
    bmesh.ops.translate(bm, verts=res["verts"], vec=Vector((x, y, p["z"])))


def build(scene_obj, layer_visible):
    mats = {}

    def mat(name):
        if name not in mats:
            mats[name] = make_material(name, MATERIALS[name])
        return mats[name]

    groups = {}
    for p in scene_obj.prims:
        if p["type"] == "text":
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
        bg.inputs["Color"].default_value = (0.9, 0.8, 0.65, 1)
        bg.inputs["Strength"].default_value = 0.35
        d = Vector((-0.25, 0.7, -0.65)).normalized()
        sun = bpy.data.lights.new("fill", "SUN")
        sun.energy = 1.2
        sun.angle = math.radians(20)
        sun.color = (1.0, 0.92, 0.8)
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
    build(s, layer)
    setup_camera_and_lights(s, scale)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
