"""Unique tiles in ONE 31x21-cell window (248x168 px) at a chosen spp, for any scene, with the real quantizer. Used to calibrate the noisy
low-sample full-map numbers against the City Centre.   python3 windowcheck.py SCENE x0,y0 SPP WORKDIR   (x0,y0 = window top-left in image px)"""
import os
import subprocess
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s49"))
import lib  # noqa: E402
import build_assets as ba  # noqa: E402

scene, xy, spp, work = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
x0, y0 = (int(v) for v in xy.split(","))
os.makedirs(work, exist_ok=True)
box = f"{x0},{y0},{x0 + 248},{y0 + 168}"
procs = []
for layer in ("floor", "objects"):
    out = f"{work}/{scene}_{x0}_{y0}_{layer}.png"
    if not os.path.exists(out):
        procs.append(subprocess.Popen(["blender", "-b", "-noaudio", "--python", os.path.join(HERE, "render.py"), "--", scene, layer, out, "2", spp,
                                       box], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
for p in procs:
    p.wait()
for layer, banks, tr in (("floor", ba.FLOOR_BANKS, False), ("objects", ba.OBJECT_BANKS, True)):
    img = ba.grade(ba.sharpen(lib.down(Image.open(f"{work}/{scene}_{x0}_{y0}_{layer}.png"))))
    img = img.crop((0, 0, 248, 168))
    pal, cells, tiles, info = ba.convert_layer(img, banks, tr, None, layer)
    ids = (cells & 0xFFFF).astype(np.int64)
    print(f"{scene} {layer} @ spp {spp}: {len(np.unique(ids[ids > 0]))} unique tiles of {ids.size} cells in the window")
