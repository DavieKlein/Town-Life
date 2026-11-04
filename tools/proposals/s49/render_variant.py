"""Blender wrapper for the sharpness experiment (proposal, not used by the game).
blender -b --python render_variant.py -- <scene> <layer> <out.png> <variant A|B|C|D> [x0,y0,x1,y1] [scale] [samples]
Variants (see sharpness.py): A = current renderer, B = pixel filter 0.5 + 2x samples (no denoiser available),
C = B + crisp 1 px opaque outlines, D = C + flatter materials (less procedural grain/noise on objects)."""
import os
import sys

TOOLS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, TOOLS)
import bpy                     # noqa: E402
import blender_render as br    # noqa: E402
import scene as scn            # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
ident, layer, out, var = argv[0], argv[1], argv[2], argv[3]
crop = argv[4] if len(argv) > 4 else ""
scale = int(argv[5]) if len(argv) > 5 else 2
samples = int(argv[6]) if len(argv) > 6 else (96 if var == "A" else 192)

if var == "D":
    # flatter, cleaner object materials: pull the noise ramp colours together and drop the finest grain;
    # ground materials (asphalt / paving) keep their grit but lose the 1-2 px grain.
    _orig = br.make_material

    def mix(a, b, t):
        ca, cb = br.rgb(a), br.rgb(b)
        return "#%02x%02x%02x" % tuple(int(255 * (ca[i] * (1 - t) + cb[i] * t) ** (1 / 2.2) + 0.5) for i in range(3))

    for k, spec in br.MATERIALS.items():
        if spec.get("kind") == "noise" and spec.get("scale", 8) >= 12:
            spec["c2"] = mix(spec["c"], spec["c2"], 0.3)             # fine-grained (>= 12 /m) textures: nearly flat
        elif spec.get("kind") == "noise":
            spec["c2"] = mix(spec["c"], spec["c2"], 0.6)
    _grit = br.grit_material

    def grit(nt, bsdf, coords, kind, spec):
        _grit(nt, bsdf, coords, kind, spec)
        for n in nt.nodes:                                             # no 1-2 px grain: make the fine noise slow
            if n.bl_idname == "ShaderNodeTexNoise" and n.inputs["Scale"].default_value >= 30:
                n.inputs["Scale"].default_value = 6.0
    br.grit_material = grit

if var in ("C", "D"):
    _style = br.stylize

    def style(layer_visible):
        _style(layer_visible)
        sc = bpy.context.scene
        ls = sc.view_layers[0].freestyle_settings.linesets[0]
        ls.linestyle.thickness = 2.5 * scale / 2          # 1.25 px in the final image, opaque, near black
        ls.linestyle.alpha = 1.0
        ls.linestyle.color = (0.03, 0.02, 0.05)
    br.stylize = style

s = next(f() for f in scn.SCENES if f().ident == ident)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = samples
sc.cycles.max_bounces = 4
sc.cycles.seed = 1
sc.render.film_transparent = True
sc.render.filter_size = 1.2 if var == "A" else 0.5
sc.cycles.use_denoising = False          # OpenImageDenoise is not built into this Blender; use more samples instead
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
