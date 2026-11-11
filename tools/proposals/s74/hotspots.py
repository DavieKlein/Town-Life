"""Where is the tile window full?  python3 hotspots.py WORKDIR  (uses WORKDIR/full_*.png from tilecount.py)
Prints, per layer, the 31x21 window with the most unique tiles (in map cells x/y of the window centre via the iso projection of the image
centre) and a coarse heat map of unique-tile counts per window."""
import os
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s49"))
import lib  # noqa: E402
import build_assets as ba  # noqa: E402
import oldblock as ob  # noqa: E402

work = sys.argv[1]
for layer, banks, tr in (("floor", ba.FLOOR_BANKS, False), ("objects", ba.OBJECT_BANKS, True)):
    img = ba.grade(ba.sharpen(lib.down(Image.open(f"{work}/full_{layer}.png"))))
    w, h = (img.width // 8) * 8, (img.height // 8) * 8
    pal, cells, tiles, info = ba.convert_layer(img.crop((0, 0, w, h)), banks, tr, None, layer)
    ids = (cells & 0xFFFF).astype(np.int64)
    th, tw = cells.shape
    res = []
    for cy in range(0, max(1, th - 20), 4):
        for cx in range(0, max(1, tw - 30), 4):
            res.append((len(np.unique(ids[cy:cy + 21, cx:cx + 31])), cx, cy))
    res.sort(reverse=True)
    print(layer, "top windows (count, image px centre x,y):")
    for n, cx, cy in res[:6]:
        px, py = (cx + 15.5) * 8, (cy + 10.5) * 8
        # invert iso: ix = ox + (x-y)*16 ; iy = oy + (x+y)*8   (z = 0)
        u = (px - (ob.H * 16 + 16)) / 16.0
        v = (py - 175) / 8.0
        print(f"  {n}  image ({px:.0f},{py:.0f})  ~ map cell ({(u + v) / 2:.1f}, {(v - u) / 2:.1f})")
    np.save(f"{work}/ids_{layer}.npy", ids)
