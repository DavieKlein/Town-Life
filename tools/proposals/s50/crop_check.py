#!/usr/bin/env python3
"""Crop check for the sharp style: renders crops of scenes with the REAL renderer (blender_render.py), runs sharpen +
grade + the real quantizer (build_assets.convert_layer, 8 floor / 7 object banks) and writes 3x zoom PNGs.
  python3 crop_check.py OUTDIR name:scene:x0,y0,x1,y1 [...]   (crops <= 240x144 px each, packed into one canvas)"""
import os, subprocess, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TOOLS)
import build_assets as ba  # noqa
sys.path.insert(0, os.path.join(HERE, "..", "s49"))
import lib  # noqa

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
crops = [a.split(":") for a in sys.argv[2:]]
W, H = 240, 144
cols = 2
canv = {l: Image.new("RGBA", (cols * W, ((len(crops) + 1) // 2) * H), (0, 0, 0, 0)) for l in ("floor", "objects")}
for i, (name, scene, box) in enumerate(crops):
    for l in ("floor", "objects"):
        f = f"{out}/{name}_{l}.png"
        if not os.path.exists(f):
            subprocess.run(["blender", "-b", "-noaudio", "--python", f"{TOOLS}/blender_render.py", "--", scene, l, f, "2", "192", box],
                           capture_output=True)
        im = ba.grade(ba.sharpen(lib.down(Image.open(f))))
        canv[l].paste(im, ((i % cols) * W, (i // cols) * H))
res = {}
for l, banks, tr in (("floor", 8, False), ("objects", 7, True)):
    pal, cells, tiles, info = ba.convert_layer(canv[l], banks, tr, None, l)
    res[l] = (ba.layer_preview(pal, cells, tiles), info["drawn"])
comp = res["floor"][0].copy()
d = res["objects"][1]
comp[d] = res["objects"][0][d]
img = Image.fromarray(comp)
img.save(f"{out}/_q.png")
for i, (name, _, _) in enumerate(crops):
    x, y = (i % cols) * W, (i // cols) * H
    lib.zoom(img.crop((x, y, x + W, y + H)), 4).save(f"{out}/{name}_q.png")
print("done")
