"""Blender wrapper for proposal renders (not used by the game).
blender -b --python render_scene.py -- <scene> <layer> <out.png> [x0,y0,x1,y1] [scale] [samples] [flags]
flags (comma separated): bin2 (street bins v2), binold, machine, sharp (variant C renderer settings).
Always adds PROPOSAL_MATERIALS and registers public_toilet_v3 as scene 'public_toilet_v3'."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import proposal_scenes as ps          # noqa: E402
import scene as scn                   # noqa: E402
import blender_render as br           # noqa: E402
import bpy                            # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
ident, layer, out = argv[0], argv[1], argv[2]
crop = argv[3] if len(argv) > 3 else ""
scale = int(argv[4]) if len(argv) > 4 and argv[4] else 2
samples = int(argv[5]) if len(argv) > 5 and argv[5] else 96
flags = set(argv[6].split(",")) if len(argv) > 6 else set()
br.MATERIALS.update(ps.PROPOSAL_MATERIALS)
if "bin2" in flags:
    scn.trash_can = ps.street_bin_v2
if "bin_indoor" in flags:
    scn.trash_can = ps.indoor_bin
if "machine" in flags:
    ps.city_with_machine()
scn.SCENES.append(ps.public_toilet_v3)
scn.SCENES.append(ps.machine_lab)
if ident == "public_toilet_v3":
    pass
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
br.build(s, layer)
br.setup_camera_and_lights(s, scale)
br.stylize(layer)
if crop:
    x0, y0, x1, y1 = (float(v) for v in crop.split(","))
    sc.render.use_border = True
    sc.render.use_crop_to_border = True
    sc.render.border_min_x = x0 / s.img_w
    sc.render.border_max_x = x1 / s.img_w
    sc.render.border_min_y = 1 - y1 / s.img_h
    sc.render.border_max_y = 1 - y0 / s.img_h
bpy.ops.render.render(write_still=True)
