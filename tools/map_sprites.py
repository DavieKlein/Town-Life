#!/usr/bin/env python3
"""Town Life - flag-driven map sprites (s75): the movable cable-works barriers and Teo's door bridge in Old Block.
Own pixel art, 64x32 frames, one shared 16-colour palette (index 0 = transparent), drawn with PIL polygons.
Frames: 0 barrier piece, 1 barrier piece with laundry draped over it, 2 Teo's door lying across the trench.
SPRITES lists the placements: (map, frame, x, y, flag_on, flag_off) with the piece's upper-right ground corner (cells).
A sprite is visible while flag_on is set (or None) and flag_off is not set (or None).
build_assets.build_map_sprites() writes graphics/map_sprites.bmp/json and include/tl_map_sprites.h.
Preview: python3 tools/map_sprites.py OUT.png"""
import sys
from PIL import Image, ImageDraw

PAL = [None, (28, 26, 36), (236, 120, 36), (244, 244, 240), (128, 134, 150), (96, 100, 116), (255, 196, 40),
       (200, 70, 80), (90, 160, 210), (240, 210, 120), (122, 78, 40), (170, 112, 60), (70, 44, 24), (255, 255, 255), (60, 140, 90), (210, 190, 150)]
W, H = 64, 32
# barrier piece: ground A (upper right) = (44, 16), ground B (lower left) = (16, 30), height 16 px
AX, AY, BX, BY, BH = 44, 16, 16, 30, 16

SPRITES = [
    # the barrier line x 10.5 across the avenue y 18.5..25.5 in four pieces; state C moves the two middle ones aside (laundry on them)
    ("old_block", 0, 10.5, 18.5, None, None),
    ("old_block", 0, 10.5, 20.25, None, "barrier_moved"),
    ("old_block", 0, 10.5, 22.0, None, "barrier_moved"),
    ("old_block", 0, 10.5, 23.75, None, None),
    ("old_block", 1, 10.5, 16.75, "barrier_moved", None),
    ("old_block", 1, 10.5, 25.5, "barrier_moved", None),
    ("old_block", 2, 11.3, 21.3, "door_bridge", None),
]

# where the frame's anchor point lies (pixels): barrier = upper-right ground corner, bridge = corner (x0, y0)
ANCHORS = {0: (AX, AY), 1: (AX, AY), 2: (22, 4)}


def _frame(kind):
    im = Image.new("P", (W, H), 0)
    im.putpalette([c for p in PAL for c in (p or (0, 0, 0))])
    d = ImageDraw.Draw(im)
    if kind in (0, 1):
        def q(*pts, fill, outline=1):
            d.polygon(list(pts), fill=fill, outline=outline)
        # legs
        for t in (0.12, 0.88):
            gx, gy = AX + (BX - AX) * t, AY + (BY - AY) * t
            q((gx - 1, gy), (gx + 1, gy), (gx + 1, gy - 9), (gx - 1, gy - 9), fill=5)
        # two striped planks
        for z0, z1 in ((4, 9), (10, 15)):
            n = 7
            for i in range(n):
                t0, t1 = i / n, (i + 1) / n
                x0, y0 = AX + (BX - AX) * t0, AY + (BY - AY) * t0
                x1, y1 = AX + (BX - AX) * t1, AY + (BY - AY) * t1
                q((x0, y0 - z0), (x1, y1 - z0), (x1, y1 - z1), (x0, y0 - z1), fill=2 if i % 2 == 0 else 3, outline=None)
            d.line([(AX, AY - z0), (BX, BY - z0), (BX, BY - z1), (AX, AY - z1), (AX, AY - z0)], fill=1)
        # amber lamp on top of the right leg
        d.rectangle([AX - 4, AY - BH - 3, AX - 1, AY - BH], fill=6, outline=1)
        if kind == 1:
            # laundry draped over the top plank: sheet, shirt and towel
            for (t0, t1, col) in ((0.25, 0.45, 3), (0.48, 0.62, 7), (0.66, 0.82, 8)):
                x0, y0 = AX + (BX - AX) * t0, AY + (BY - AY) * t0
                x1, y1 = AX + (BX - AX) * t1, AY + (BY - AY) * t1
                d.polygon([(x0, y0 - 17), (x1, y1 - 17), (x1, y1 - 7), (x0, y0 - 7)], fill=col, outline=1)
    else:
        P = (22, 4)
        c = lambda ux, uy: (P[0] + 32 * ux - 22 * uy, P[1] + 16 * ux + 11 * uy)
        quad = [c(0, 0), c(1, 0), c(1, 1), c(0, 1)]
        d.polygon([(x, y + 3) for x, y in quad], fill=12, outline=1)           # thickness
        d.polygon(quad, fill=11, outline=1)
        for u in (0.25, 0.5, 0.75):                                            # planks
            d.line([c(u, 0.04), c(u, 0.96)], fill=10)
        d.polygon([c(0.08, 0.08), c(0.92, 0.08), c(0.92, 0.92), c(0.08, 0.92)], outline=10)
        hx, hy = c(0.85, 0.5)
        d.rectangle([hx - 1, hy - 1, hx + 1, hy], fill=6, outline=1)           # door knob
    return im


def frames_list():
    """Returns (pixel rows for all frames stacked, palette)."""
    rows = []
    for k in range(3):
        im = _frame(k)
        rows += [[im.getpixel((x, y)) for x in range(W)] for y in range(H)]
    return rows, [p or (0, 0, 0) for p in PAL]


if __name__ == "__main__":
    out = Image.new("RGB", (W * 3 * 4, H * 4), (110, 130, 90))
    for k in range(3):
        im = _frame(k).convert("RGBA")
        data = [(0, 0, 0, 0) if im.getpixel((x, y))[:3] == (0, 0, 0) and _frame(k).getpixel((x, y)) == 0 else im.getpixel((x, y)) for y in range(H) for x in range(W)]
        im.putdata(data)
        out.paste(im.resize((W * 4, H * 4), Image.NEAREST), (k * W * 4, 0), im.resize((W * 4, H * 4), Image.NEAREST))
    out.save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/map_sprites.png")
