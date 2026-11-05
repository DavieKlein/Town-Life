#!/usr/bin/env python3
"""s62: render the golden car (blender_car.py), outline + quantise to ONE 15-colour palette shared by all facings,
write PNGs and the sprite-piece plan.  python3 car_sprites.py OUTDIR [samples] [scale]"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_assets as ba  # noqa

out = sys.argv[1]
samples = sys.argv[2] if len(sys.argv) > 2 else "64"
scale = sys.argv[3] if len(sys.argv) > 3 else "1.0"
SS = 4
FW, FH = 192, 112
os.makedirs(out, exist_ok=True)
raw = f"{out}/raw"
if not os.path.exists(f"{raw}/car_se.png") or "--rerender" in sys.argv:
    subprocess.run(["blender", "-b", "-noaudio", "--python", f"{HERE}/blender_car.py", "--", raw, str(SS), samples, scale],
                   check=True, capture_output=True)
names = ("se", "nw", "sw", "ne")
frames = {}
for n in names:
    img = Image.open(f"{raw}/car_{n}.png")
    # grade like the game (sharpen + grade run on rgb before quantisation)
    rgb, alpha = ba.sprite_frame(f"{raw}/car_{n}.png", SS, FW, FH)
    g = rgb.astype(np.float64)
    lum = (g * [0.3, 0.59, 0.11]).sum(2, keepdims=True)
    g = lum + (g - lum) * 1.35                      # saturation
    g = (g - 110) * 1.25 + 110                      # contrast
    rgb = np.clip(g, 0, 255)
    frames[n] = (rgb, alpha)
outline = np.array([40.0, 30.0, 40.0])
# palette from the two unique facings (sw / ne are mirrors of se / nw)
px = np.concatenate([frames[n][0][frames[n][1]] for n in ("se", "nw")]) * ba.WEIGHT
cols = ba.to5(ba.kmeans(px, 14, iters=20) / ba.WEIGHT)
cols = np.concatenate([cols, [outline]])
pal = [(255, 0, 255)] + [tuple(int(v) for v in c) for c in ba.to5(cols)]
cw = cols * ba.WEIGHT
res = {}
for n in names:
    rgb, alpha = frames[n]
    d = ((rgb[..., None, :] * ba.WEIGHT - cw[None, None]) ** 2).sum(3)
    idx = d.argmin(2) + 1
    idx[~alpha] = 0
    res[n] = idx.astype(np.uint8)
    im = np.zeros((FH, FW, 4), np.uint8)
    for i, c in enumerate(pal):
        if i:
            im[idx == i] = (*c, 255)
    Image.fromarray(im).save(f"{out}/car_{n}_q.png")
    ys, xs = np.nonzero(idx)
    print(n, "bbox", xs.min(), ys.min(), xs.max() + 1, ys.max() + 1, "size", xs.max() + 1 - xs.min(), ys.max() + 1 - ys.min())
np.save(f"{out}/palette.npy", np.array(pal))
json.dump(pal, open(f"{out}/palette.json", "w"))
