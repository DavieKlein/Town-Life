"""
s62 proposal: Victor Vault's golden car, rendered for the GBA iso camera.
  blender -b -noaudio --python tools/blender_car.py -- <out_dir> <supersample> <samples> [scale]
Writes <out_dir>/car_<facing>.png  facing: se (+x, front visible), nw (-x, rear visible), sw (+y), ne (-y)
Frame FW x FH px, the car's ground centre at (FEET_X, FEET_Y).  scale 1.0 = real size (4.9 m), the player is 1.78 m.
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector

CELL_M = 0.75
FW, FH = 192, 112
FEET_X, FEET_Y = 96, 74


def mat(name, col, rough=0.4, metal=0.0, emit=None, emit_strength=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    return m


def obj_from_bm(bm, name, m, smooth=False, bevel=0.0, subsurf=0):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if bevel:
        md = o.modifiers.new("bev", "BEVEL")
        md.width = bevel
        md.segments = 4
        md.limit_method = "ANGLE"
        md.angle_limit = math.radians(25)
    if subsurf:
        md = o.modifiers.new("sub", "SUBSURF")
        md.levels = subsurf
        md.render_levels = subsurf
    return o


def hull(pts, name, m, bevel=0.0, smooth=True):
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    return obj_from_bm(bm, name, m, smooth=smooth, bevel=bevel)


def box(x0, x1, y0, y1, z0, z1, m, name="box", bevel=0.0):
    pts = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    return hull(pts, name, m, bevel=bevel, smooth=False)


def cyl(x, y, z, r, depth, m, axis="y", verts=24, name="cyl"):
    rot = {"y": (math.pi / 2, 0, 0), "x": (0, math.pi / 2, 0), "z": (0, 0, 0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=(x, y, z), rotation=rot, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(m)
    return o


def build_car(parts):
    gold = mat("gold", (1.0, 0.62, 0.06), rough=0.3, metal=1.0)
    gold2 = mat("gold2", (0.98, 0.78, 0.25), rough=0.18, metal=1.0)
    chrome = mat("chrome", (0.9, 0.92, 0.96), rough=0.08, metal=1.0)
    glass = mat("glass", (0.02, 0.05, 0.11), rough=0.03, metal=0.5)
    tire = mat("tire", (0.025, 0.025, 0.03), rough=0.8)
    dark = mat("dark", (0.04, 0.04, 0.05), rough=0.5)
    lamp = mat("lamp", (1, 0.95, 0.75), emit=(1, 0.95, 0.7), emit_strength=6.0)
    tail = mat("tail", (0.55, 0.02, 0.02), emit=(1, 0.05, 0.03), emit_strength=1.6)
    white = mat("white", (0.96, 0.96, 0.94), rough=0.4)
    roofm = mat("roof", (0.03, 0.03, 0.04), rough=0.15, metal=0.2)
    black = mat("black", (0.02, 0.02, 0.03), rough=0.5)
    s = parts.get("scale", 1.0)
    LXP = 2.8 + 0.15
    objs = []
    # body: convex hull of the lower body, rounded (long, low limousine, 5.6 m)
    LX = 2.8
    P = []
    for sy in (-1, 1):
        P += [(-LX, sy * 0.86, 0.27), (LX, sy * 0.86, 0.27),
              (-LX + 0.02, sy * 0.80, 0.88), (-1.6, sy * 0.89, 0.93), (0.6, sy * 0.90, 0.92),
              (1.7, sy * 0.86, 0.88), (LX - 0.04, sy * 0.78, 0.74),
              (-LX - 0.04, sy * 0.78, 0.55), (LX + 0.04, sy * 0.74, 0.5)]
    objs.append(hull(P, "body", gold, bevel=0.1))
    C = []
    for sy in (-1, 1):
        C += [(-1.95, sy * 0.84, 0.90), (1.05, sy * 0.84, 0.90), (-1.55, sy * 0.70, 1.27), (0.55, sy * 0.70, 1.27)]
    objs.append(hull(C, "glass", glass, bevel=0.03))
    R = []
    for sy in (-1, 1):
        R += [(-1.58, sy * 0.68, 1.265), (0.58, sy * 0.68, 1.265), (-1.58, sy * 0.68, 1.31), (0.58, sy * 0.68, 1.31)]
    objs.append(hull(R, "roof", roofm, bevel=0.03))
    # sill + trim + door seams
    for sy in (-1, 1):
        objs.append(box(-2.2, 2.2, sy * 0.90 - 0.01, sy * 0.90 + 0.03, 0.27, 0.34, dark, "sill"))
        objs.append(box(-2.6, 2.6, sy * 0.905 - 0.005, sy * 0.905 + 0.025, 0.60, 0.67, chrome, "trim"))
        for dx in (1.15, -0.05, -1.45, -2.2):
            objs.append(box(dx - 0.01, dx + 0.01, sy * 0.905 - 0.005, sy * 0.905 + 0.02, 0.42, 0.88, black, "seam"))
        objs.append(box(0.9, 1.04, sy * 0.95, sy * 1.10, 0.97, 1.05, gold2, "mirror"))
        objs.append(box(0.95, 1.0, sy * 0.88, sy * 0.96, 0.92, 1.0, chrome, "mirror_arm"))
    # wheels
    for wx in (1.85, -1.75):
        for sy in (-1, 1):
            objs.append(cyl(wx, sy * 0.72, 0.34, 0.34, 0.22, tire, name="tire"))
            objs.append(cyl(wx, sy * 0.84, 0.34, 0.22, 0.06, chrome, name="rim"))
            objs.append(cyl(wx, sy * 0.87, 0.34, 0.10, 0.05, gold2, name="hub"))
            objs.append(cyl(wx, sy * 0.89, 0.34, 0.41, 0.02, black, name="arch"))
    # front end (+x)
    objs.append(box(LX - 0.02, LX + 0.05, -0.42, 0.42, 0.32, 0.62, chrome, "grille", bevel=0.01))
    for k in range(5):
        objs.append(box(LX + 0.04, LX + 0.06, -0.40, 0.40, 0.35 + k * 0.055, 0.375 + k * 0.055, black, "slat"))
    for sy in (-1, 1):
        objs.append(box(LX - 0.06, LX + 0.04, sy * 0.52, sy * 0.80, 0.54, 0.66, lamp, "lamp"))
    objs.append(box(LX - 0.02, LX + 0.14, -0.88, 0.88, 0.24, 0.35, chrome, "bumper_f", bevel=0.04))
    objs.append(box(LX + 0.12, LX + 0.145, -0.26, 0.26, 0.27, 0.40, white, "plate_f"))
    objs.append(hull([(2.5, -0.05, 0.74), (2.5, 0.05, 0.74), (LX - 0.06, 0, 0.74), (LX - 0.08, 0, 0.92), (2.38, 0, 0.80)], "ornament", gold2))
    # rear end (-x)
    objs.append(box(-LX - 0.08, -LX - 0.02, -0.84, 0.84, 0.60, 0.72, tail, "tail"))
    objs.append(box(-LX - 0.16, -LX + 0.02, -0.88, 0.88, 0.24, 0.35, chrome, "bumper_r", bevel=0.04))
    objs.append(box(-LX - 0.145, -LX - 0.115, -0.26, 0.26, 0.40, 0.52, white, "plate_r"))
    for sy in (-1, 1):
        objs.append(cyl(-LX - 0.1, sy * 0.45, 0.30, 0.05, 0.12, chrome, axis="x", verts=12, name="exhaust"))
    # plate text
    for (x, rot, sign) in ((LXP, math.pi / 2, 1), (-LXP, -math.pi / 2, -1)):
        cu = bpy.data.curves.new("txt", "FONT")
        cu.body = "VV"
        cu.size = 0.2
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.extrude = 0.004
        try:
            cu.font = bpy.data.fonts.load("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        except Exception:
            pass
        o = bpy.data.objects.new("plate_txt", cu)
        bpy.context.scene.collection.objects.link(o)
        o.data.materials.append(black)
        o.rotation_euler = (math.pi / 2, 0, rot)
        o.location = (x, 0, (0.335 if sign > 0 else 0.46))
        objs.append(o)
    # parent everything to a holder
    holder = bpy.data.objects.new("car", None)
    bpy.context.scene.collection.objects.link(holder)
    for o in objs:
        o.parent = holder
    holder.scale = (s, s, s)
    return holder


def setup(ss, samples):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.render.film_transparent = True
    sc.render.filter_size = 1.0
    sc.view_settings.view_transform = "Standard"
    sc.render.resolution_x = FW * ss
    sc.render.resolution_y = FH * ss
    sc.render.image_settings.color_mode = "RGBA"
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.sensor_fit = "HORIZONTAL"
    cam.ortho_scale = FW * math.cos(math.radians(45)) * CELL_M / 16
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    co.rotation_euler = (math.radians(60), 0, math.radians(45))
    a = FW / 2 - FEET_X
    b = FH / 2 - FEET_Y
    ux, uy = b + a / 2, b - a / 2
    target = Vector((ux / 16 * CELL_M, -uy / 16 * CELL_M, 0))
    fwd = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)),
                  math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))
    co.location = target - fwd * 40
    # sky-gradient world so the metal has something to reflect
    world = bpy.data.worlds.new("world")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    cr = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], cr.inputs["Fac"])
    cr.color_ramp.elements[0].position = 0.35
    cr.color_ramp.elements[0].color = (0.30, 0.22, 0.14, 1)
    cr.color_ramp.elements[1].position = 0.75
    cr.color_ramp.elements[1].color = (0.75, 0.88, 1.0, 1)
    nt.links.new(cr.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.1
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.8
    sun.angle = math.radians(8)
    so = bpy.data.objects.new("sun", sun)
    sc.collection.objects.link(so)
    so.rotation_euler = Vector((-0.25, 0.7, -0.65)).normalized().to_track_quat("-Z", "Y").to_euler()


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out = argv[0]
    ss = int(argv[1]) if len(argv) > 1 else 4
    samples = int(argv[2]) if len(argv) > 2 else 64
    scale = float(argv[3]) if len(argv) > 3 else 1.0
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup(ss, samples)
    car = build_car({"scale": scale})
    sc = bpy.context.scene
    # facing -> heading (game +x = blender +x, game +y = blender -y)
    for name, yaw in (("se", 0), ("nw", 180), ("sw", -90), ("ne", 90)):
        car.rotation_euler = (0, 0, math.radians(yaw))
        sc.render.filepath = os.path.join(out, f"car_{name}.png")
        bpy.ops.render.render(write_still=True)


main()
