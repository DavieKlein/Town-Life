#!/usr/bin/env python3
"""s62: OBJ piece plan for the car sheets.  python3 car_plan.py DIR   (uses DIR/car_se_q.png and car_nw_q.png)"""
import sys
import numpy as np
from PIL import Image
d = sys.argv[1]
SHAPES = [(8, 8), (16, 8), (8, 16), (16, 16), (32, 8), (8, 32), (32, 16), (16, 32), (32, 32), (64, 32), (32, 64), (64, 64)]
tot = {}
for n in ("se", "nw"):
    a = np.array(Image.open(f"{d}/car_{n}_q.png"))[..., 3] > 0
    ys, xs = np.nonzero(a)
    x0, x1, y0, y1 = xs.min() // 8 * 8, (xs.max() + 8) // 8 * 8, ys.min() // 8 * 8, (ys.max() + 8) // 8 * 8
    pieces = []
    for cy in range(y0, y1, 64):
        for cx in range(x0, x1, 64):
            blk = a[cy:min(cy + 64, y1), cx:min(cx + 64, x1)]
            if not blk.any():
                continue
            by, bx = np.nonzero(blk)
            w = (bx.max() + 8) // 8 * 8 - bx.min() // 8 * 8
            h = (by.max() + 8) // 8 * 8 - by.min() // 8 * 8
            best = min((sw * sh, sw, sh) for sw, sh in SHAPES if sw >= w and sh >= h)
            pieces.append(best[1:])
    tiles = sum(p[0] * p[1] // 64 for p in pieces)
    print(n, "bbox", (x1 - x0, y1 - y0), "pieces", pieces, "sprites", len(pieces), "tiles", tiles, "bytes", tiles * 32)
    tot[n] = (len(pieces), tiles)
