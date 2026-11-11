"""Tile-budget measurement for the proposed Old Block map with the REAL quantizer (build_assets.convert_layer).
  python3 tilecount.py WORKDIR [samples]
Renders the full map (both layers, 2x, `samples` spp), downsamples, sharpen + grade, converts with 8 floor / 7 object banks and prints the
unique tile counts and the worst 31x21 window. (Low sample counts leave render noise, which defeats tile de-duplication: treat the
numbers as an upper bound; the real build uses 192 spp + the cache.)"""
import os
import subprocess
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s49"))
import lib  # noqa: E402
import build_assets as ba  # noqa: E402

work = sys.argv[1]
samples = sys.argv[2] if len(sys.argv) > 2 else "32"
os.makedirs(work, exist_ok=True)
procs = []
for layer in ("floor", "objects"):
    out = f"{work}/full_{layer}.png"
    if not os.path.exists(out):
        procs.append(subprocess.Popen(["blender", "-b", "-noaudio", "--python", os.path.join(HERE, "render.py"), "--", "old_block", layer,
                                       out, "2", samples], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
for p in procs:
    p.wait()
res = {}
for layer, banks, tr in (("floor", ba.FLOOR_BANKS, False), ("objects", ba.OBJECT_BANKS, True)):
    img = ba.grade(ba.sharpen(lib.down(Image.open(f"{work}/full_{layer}.png"))))
    w, h = (img.width // 8) * 8, (img.height // 8) * 8
    img = img.crop((0, 0, w, h))
    pal, cells, tiles, info = ba.convert_layer(img, banks, tr, None, layer)
    ids = (cells & 0xFFFF).astype(np.int64)
    th, tw = cells.shape
    worst = 0
    for cy in range(0, max(1, th - 20), 2):
        for cx in range(0, max(1, tw - 30), 2):
            worst = max(worst, len(np.unique(ids[cy:cy + 21, cx:cx + 31])))
    used = int((ids > 0).sum())
    print(f"old_block {layer}: image {img.width}x{img.height}, {len(tiles)} unique tiles ({len(tiles) * 32 / 1024:.0f} KB), "
          f"{used} non-empty cells of {th * tw}, worst 31x21 window {worst}  (cache: 624 slots)")
    res[layer] = (len(tiles), worst, used)
print("TOTAL unique tiles", sum(v[0] for v in res.values()), "-> data approx", sum(v[0] for v in res.values()) * 32 // 1024, "KB + cells")
