"""
Town Life - ambient animal renderer (runs INSIDE Blender, called by tools/build_assets.py).

  blender -b -noaudio --python tools/blender_critter.py -- <out_dir> <supersample> <samples> [yaw_test]

Renders the static Everything Library animal models (art_source/everything_library_animals,
CC BY 4.0, David OReilly) into 32x32 sprite frames, facing RIGHT on screen (the game mirrors
them for left), with the same camera scale as the maps. Static models are "animated" here:
wing beats by bending the wings, pecking / running by tilting the body.
  <out_dir>/pigeon_<i>.png   0 stand, 1 peck, 2 wings up, 3 wings mid, 4 wings down
  <out_dir>/squirrel_<i>.png 0 sit, 1 run A, 2 run B, 3 climb
Feet at (FEET_X, FEET_Y) inside each frame.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as scn  # noqa: E402

CELL_M = scn.CELL_M
FRAME = 32
FEET_X, FEET_Y = 16, 23
GLB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "art_source", "everything_library_animals", "city_animals.glb")
# rotations that make each model face right on screen (picked from a yaw test render)
YAW = {"GroundedPigeon": 135, "Pigeon": 270, "GraySquirrel": 90}
UNIT = 0.01             # the GLB meshes are in centimetres
BASE_PITCH = float(os.environ.get("TL_BASE_PITCH", "90"))   # the GLB lost the FBX up-axis rotation


def setup_scene(ss, samples):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.render.film_transparent = True
    sc.render.filter_size = 1.0
    sc.view_settings.view_transform = "Standard"
    sc.render.resolution_x = FRAME * ss
    sc.render.resolution_y = FRAME * ss
    sc.render.image_settings.color_mode = "RGBA"
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.sensor_fit = "HORIZONTAL"
    cam.ortho_scale = FRAME * math.cos(math.radians(45)) * CELL_M / 16
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    co.rotation_euler = (math.radians(60), 0, math.radians(45))
    a = FRAME / 2 - FEET_X
    b = FRAME / 2 - FEET_Y
    ux, uy = b + a / 2, b - a / 2
    target = Vector((ux / 16 * CELL_M, -uy / 16 * CELL_M, 0))
    fwd = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)),
                  math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))
    co.location = target - fwd * 40
    world = bpy.data.worlds.new("world")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.66, 0.8, 1)
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.5
    sun.angle = math.radians(10)
    so = bpy.data.objects.new("sun", sun)
    sc.collection.objects.link(so)
    so.rotation_euler = Vector((-0.25, 0.7, -0.65)).normalized().to_track_quat("-Z", "Y").to_euler()


def load_models():
    bpy.ops.import_scene.gltf(filepath=GLB)
    # colours are vertex colours: wire them to Base Color
    for m in bpy.data.materials:
        if not m.use_nodes or "Principled BSDF" not in m.node_tree.nodes:
            continue
        nt = m.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        for link in list(nt.links):
            if link.to_node == bsdf and link.to_socket.name in ("Base Color", "Normal", "Alpha"):
                nt.links.remove(link)
        bsdf.inputs["Alpha"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.7
        vc = nt.nodes.new("ShaderNodeVertexColor")
        nt.links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
    roots = {}
    for name in ("Pigeon", "GroundedPigeon", "GraySquirrel"):
        r = bpy.data.objects[name]
        holder = bpy.data.objects.new("H_" + name, None)
        bpy.context.scene.collection.objects.link(holder)
        bpy.context.view_layer.update()
        mw = r.matrix_world.copy()
        r.parent = holder
        r.matrix_world = mw
        bpy.context.view_layer.update()
        meshes = [o for o in [r] + list(r.children_recursive) if o.type == "MESH"]
        all_meshes = meshes
        if name == "GraySquirrel":
            meshes = meshes[:1]          # two pose variants; we only use the first
        for o in all_meshes:
            if o.data.color_attributes:
                for m in o.data.materials:
                    for nd in m.node_tree.nodes:
                        if nd.type == "VERTEX_COLOR":
                            nd.layer_name = o.data.color_attributes[0].name
        pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
        cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
        cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
        mz = min(p.z for p in pts)
        r.matrix_world.translation -= Vector((cx, cy, mz))
        roots[name] = holder
    return roots


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_dir = argv[0]
    ss = int(argv[1]) if len(argv) > 1 else 4
    samples = int(argv[2]) if len(argv) > 2 else 48
    yaw_test = len(argv) > 3 and argv[3] == "yaw_test"
    os.makedirs(out_dir, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    roots = load_models()
    setup_scene(ss, samples)
    sc = bpy.context.scene

    def render(name, path, scale, yaw=None, z=0.0, pitch=0.0, bend=None, mesh_index=None, shift=0.0):
        if yaw is None:
            yaw = YAW[name]
        for n, h in roots.items():
            for o in [h] + list(h.children_recursive):
                o.hide_render = n != name
        h = roots[name]
        h.location = (shift, shift, z)   # metres; (+1, +1) in Blender = screen right
        h.scale = (scale * UNIT, scale * UNIT, scale * UNIT)
        # pitch tilts around the model's own side axis (applied before the yaw)
        h.rotation_mode = "XYZ"
        h.rotation_euler = (math.radians(pitch + BASE_PITCH), 0, math.radians(yaw))
        meshes = [o for o in h.children_recursive if o.type == "MESH"]
        for i, o in enumerate(meshes):
            if mesh_index is not None:
                o.hide_render = i != mesh_index
            for md in list(o.modifiers):
                o.modifiers.remove(md)
            if bend is not None:
                md = o.modifiers.new("bend", "SIMPLE_DEFORM")
                md.deform_method = "BEND"
                md.deform_axis = "X"
                md.angle = math.radians(bend)
        sc.render.filepath = os.path.join(out_dir, path)
        bpy.ops.render.render(write_still=True)

    if yaw_test:
        for yaw in range(0, 360, 45):
            render("GroundedPigeon", f"yaw_pigeon_{yaw}.png", 2.0, yaw=yaw)
            render("GraySquirrel", f"yaw_squirrel_{yaw}.png", 2.0, yaw=yaw, mesh_index=0)
            render("Pigeon", f"yaw_fly_{yaw}.png", 1.4, yaw=yaw, z=0.3)
        return

    render("GroundedPigeon", "pigeon_0.png", 2.0)
    render("GroundedPigeon", "pigeon_1.png", 2.0, pitch=25)
    for i, bend in enumerate((-70, 0, 70)):
        render("Pigeon", f"pigeon_{2 + i}.png", 0.9, z=0.1, bend=bend, shift=0.2)
    render("GraySquirrel", "squirrel_0.png", 1.6, mesh_index=0)
    render("GraySquirrel", "squirrel_1.png", 1.6, pitch=12, mesh_index=0)
    render("GraySquirrel", "squirrel_2.png", 1.6, pitch=-12, mesh_index=0)
    render("GraySquirrel", "squirrel_3.png", 1.8, pitch=-75, z=0.0, mesh_index=0)


main()
