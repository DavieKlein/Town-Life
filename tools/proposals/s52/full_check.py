#!/usr/bin/env python3
"""Like crop_check.py but each crop is quantized on its own and may be any size (multiples of 8).
  python3 full_check.py OUTDIR [--samples N] name:scene:x0,y0,x1,y1 ...   (box '' = whole scene -> use 'all')"""
import os, subprocess, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TOOLS)
import build_assets as ba  # noqa
sys.path.insert(0, os.path.join(HERE, "..", "s49"))
import lib  # noqa
args = sys.argv[1:]
out = args.pop(0)
samples = "192"
if args and args[0] == "--samples":
    args.pop(0); samples = args.pop(0)
os.makedirs(out, exist_ok=True)
for a in args:
    name, scene, box = a.split(":")
    box = "" if box == "all" else box
    imgs = {}
    for l in ("floor", "objects"):
        f = f"{out}/{name}_{l}.png"
        if not os.path.exists(f):
            r = subprocess.run(["blender", "-b", "-noaudio", "--python", f"{TOOLS}/blender_render.py", "--", scene, l, f, "2", samples, box],
                               capture_output=True, text=True)
            if not os.path.exists(f):
                print(r.stdout[-2000:], r.stderr[-1000:]); sys.exit(1)
        imgs[l] = ba.grade(ba.sharpen(lib.down(Image.open(f))))
    w, h = imgs["floor"].size
    W8, H8 = (w + 7) // 8 * 8, (h + 7) // 8 * 8
    res = {}
    for l, banks, tr in (("floor", 8, False), ("objects", 7, True)):
        im = Image.new("RGBA", (W8, H8), (0, 0, 0, 0)); im.paste(imgs[l], (0, 0))
        pal, cells, tiles, info = ba.convert_layer(im, banks, tr, None, l)
        res[l] = (ba.layer_preview(pal, cells, tiles), info["drawn"])
    comp = res["floor"][0].copy()
    d = res["objects"][1]
    comp[d] = res["objects"][0][d]
    Image.fromarray(comp).save(f"{out}/{name}_q.png")
    print("done", name, comp.shape)
