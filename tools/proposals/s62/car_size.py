#!/usr/bin/env python3
"""s62: sprite-piece overlay + size comparison with the player; writes car_size.png and car_costs.json"""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
O = "/tmp/claude-0/s62"
F = lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", n)
SHAPES = [(8, 8), (16, 8), (8, 16), (16, 16), (32, 8), (8, 32), (32, 16), (16, 32), (32, 32), (64, 32), (32, 64), (64, 64)]
pl = Image.open("/tmp/claude-0/s52/out/player_rgba.png").crop((0, 0, 32, 64)).convert("RGBA")


def plan(img):
    a = np.array(img)[..., 3] > 0
    ys, xs = np.nonzero(a)
    x0, x1, y0, y1 = xs.min() // 8 * 8, (xs.max() + 8) // 8 * 8, ys.min() // 8 * 8, (ys.max() + 8) // 8 * 8
    best = None
    # try a few grid origins and keep the cheapest cover
    for ox in range(0, 8, 8):
        pieces = []
        for cy in range(y0, y1, 64):
            for cx in range(x0, x1, 64):
                blk = a[cy:min(cy + 64, y1), cx:min(cx + 64, x1)]
                if not blk.any():
                    continue
                by, bx = np.nonzero(blk)
                bx0, bx1 = bx.min() // 8 * 8, (bx.max() + 8) // 8 * 8
                by0, by1 = by.min() // 8 * 8, (by.max() + 8) // 8 * 8
                w, h = bx1 - bx0, by1 - by0
                sw, sh = min((s for s in SHAPES if s[0] >= w and s[1] >= h), key=lambda s: s[0] * s[1])
                pieces.append((cx + bx0, cy + by0, sw, sh))
        tiles = sum(p[2] * p[3] // 64 for p in pieces)
        if best is None or tiles < best[0]:
            best = (tiles, pieces)
    return best


COL = [(255, 80, 80), (80, 220, 255), (120, 255, 120), (255, 255, 90), (255, 140, 255), (255, 170, 60)]
out = Image.new("RGB", (1240, 900), (24, 28, 56))
d = ImageDraw.Draw(out)
costs = []
y = 10
for name, folder in (("full size (5.6 m)", "car"), ("compact (0.75x, 4.2 m)", "car75")):
    row_x = 20
    for n in ("se", "nw"):
        img = Image.open(f"{O}/{folder}/car_{n}_q.png").convert("RGBA")
        tiles, pieces = plan(img)
        a = np.array(img)[..., 3] > 0
        ys, xs = np.nonzero(a)
        bg = Image.new("RGBA", img.size, (112, 118, 130, 255)); bg.alpha_composite(img)
        # player next to it for scale (at the car's feet height)
        bg.alpha_composite(pl, (img.width - 38, 74 - 54 + 6 - 8))
        dd = ImageDraw.Draw(bg)
        for i, (px, py, w, h) in enumerate(pieces):
            dd.rectangle((px, py, px + w - 1, py + h - 1), outline=COL[i % len(COL)] + (255,))
        x0, y0, x1, y1 = xs.min() - 6, ys.min() - 6, xs.max() + 6, ys.max() + 6
        crop = bg.crop((max(0, x0), max(0, y0), min(192, img.width), min(112, y1))).convert("RGB")
        crop = crop.resize((crop.width * 3, crop.height * 3), Image.NEAREST)
        if row_x + crop.width > 1240:
            row_x = 20
        out.paste(crop, (row_x, y + 28))
        d.text((row_x, y + 2), f"{name}, {n.upper()}: {xs.max()+1-xs.min()}x{ys.max()+1-ys.min()} px -> {len(pieces)} OBJ, {tiles} tiles", font=F(15), fill=(248, 208, 96))
        costs.append((name, n, xs.max() + 1 - xs.min(), ys.max() + 1 - ys.min(), len(pieces), tiles, [(w, h) for _, _, w, h in pieces]))
        row_x += crop.width + 20
    y += 28 + 3 * 118 + 12
out = out.crop((0, 0, 1240, y))
out.save(f"{O}/car_size.png")
print(costs)
lines = ["# Sprite cost (4bpp OBJ, 1 palette bank for the whole car; SW/NE are h-flips of SE/NW):"]
for c in costs:
    lines.append(f"{c[0]:>24}  {c[1].upper()}: {c[2]}x{c[3]} px, {c[4]} sprites {c[6]}, {c[5]} tiles = {c[5]*32/1024:.1f} KB VRAM ({c[5]/1024*100:.0f} % of the 1024 OBJ tiles)")
json.dump(lines, open(f"{O}/car_costs.json", "w"))
