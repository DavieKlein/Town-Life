"""Tile density of the proposal crops with the REAL quantizer (build_assets.convert_layer, 8 floor / 7 object banks).
  python3 tilecount.py SHOTS_DIR
Prints, per crop, unique tiles and cells, and the largest number of distinct tiles in any 31 x 18 window (the engine window; the tile cache has
624 slots). The crops are rendered at low sample counts: noise defeats de-duplication, so the numbers are an upper bound."""
import os
import sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(HERE, "..", "s49"))
import build_assets as ba  # noqa: E402
import lib  # noqa: E402

d = sys.argv[1]
for name in sorted(set(f.rsplit("_", 1)[0] for f in os.listdir(d) if f.endswith(("_floor.png", "_objects.png")))):
    row = [name]
    worst_total = 0
    wins = {}
    for layer, banks, tr in (("floor", 8, False), ("objects", 7, True)):
        img = ba.grade(ba.sharpen(lib.down(Image.open(f"{d}/{name}_{layer}.png"))))
        w, h = (img.width // 8) * 8, (img.height // 8) * 8
        pal, cells, tiles, info = ba.convert_layer(img.crop((0, 0, w, h)), banks, tr, None, layer)
        ids = (cells & 0xFFFF).astype(np.int64)
        th, tw = ids.shape
        wins[layer] = ids
        row.append("%s %d unique / %d cells" % (layer, len(np.unique(ids[ids > 0])), th * tw))
    th, tw = wins["floor"].shape
    for cy in range(0, max(1, th - 17), 2):
        for cx in range(0, max(1, tw - 30), 2):
            u = len(np.unique(wins["floor"][cy:cy + 18, cx:cx + 31])) + 0
            worst_total = max(worst_total, u)
    row.append("worst floor 31x18 window %d" % worst_total)
    print(" | ".join(row))
