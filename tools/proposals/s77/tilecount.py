"""Unique-tile count of the proposed sewer map with the real quantizer (uses the cached full render of shots.py).  python3 tilecount.py OUTDIR"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compose as c  # noqa: E402

out = sys.argv[1]
ba, lib = c.ba, c.lib
tot = 0
for layer, banks, tr in (("floor", 8, False), ("objects", 7, True)):
    im = ba.grade(ba.sharpen(lib.down(Image.open(f"{out}/_r_sewer_full_{layer}.png"))))
    pal, cells, tiles, info = ba.convert_layer(im, banks, tr, None, layer)
    n = len(tiles) - 1
    tot += n
    th, tw = cells.shape
    best = 0
    ids = (cells & 0xFFFF)
    for y in range(0, th - 17):
        for x in range(0, tw - 30):
            w = ids[y:y + 18, x:x + 31]
            best = max(best, len(np.unique(w[w > 0])))
    print(f"{layer}: map {tw}x{th} cells, unique tiles {n} (~{n * 32 / 1024:.0f} KB), worst 31x18 window {best} (cache 624)")
print("total unique tiles", tot)
