#!/usr/bin/env python3
"""
Town Life - art for the two job minigames (owner-approved mock-ups in tools/proposals/minigames: STOCK IT! and PLATE RUSH).
The mock-up drawing code is ported here; the static scenery becomes full-screen 8bpp backgrounds and everything that moves becomes
a small sprite sheet (16-colour palette, index 0 = transparent).

Writes (graphics/*.bmp + .json, run by build_assets.py or alone: python3 tools/minigame_art.py [--preview DIR]):
  mg_stock_bg, mg_dish_bg    240x160 backgrounds padded to 256x256 (8bpp; palette entry 0 is unused because it is the transparent
                             colour; shown with create_bg(8, 48))
  mg_items                   16x16: milk, can, cereal, apple (4th section of the replay job)
  mg_fx                      16x16: 0 red X, 1 sparkle, 2 plate icon, 3 broken plate icon, 4 pip empty, 5 pip full, 6/7 shards
  mg_plate                   32x16: 0 dirty, 1 soapy, 2 clean, 3 broken
  mg_pan                     64x64: greasy pan (pan drawn at (20, 32))
  mg_rack                    8x32:  a clean plate standing in the rack
  mg_vline / mg_hline        8x32 / 32x8 gold selection lines
  mg_cover_dish              32x32: the counter in front of the dish washer (drawn over the player sprite)
The player is the existing graphics/player_wash sheet (facing n for STOCK IT!, facing s for PLATE RUSH).
"""
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
W, H = 240, 160

# ---------------------------------------------------------------------------------------------------- drawing toolkit
FONT = np.array(Image.open(os.path.join(ROOT, "butano", "common", "graphics", "common_fixed_8x8_font.bmp")))


def glyph(c, col):
    i = ord(c) - 33
    g = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    if i < 0 or i >= 110:
        return g
    px = g.load()
    for y in range(8):
        for x in range(8):
            v = FONT[i * 8 + y, x]
            if v == 1:
                px[x, y] = tuple(col[:3]) + (255,)
            elif v == 2:
                px[x, y] = (0, 0, 0, 255)
    return g


def text(img, s, x, y, col=(255, 255, 255), scale=1):
    for ch in s:
        g = glyph(ch, col)
        if scale > 1:
            g = g.resize((8 * scale, 8 * scale), 0)
        img.alpha_composite(g, (x, y))
        x += 8 * scale
    return x


def tw(s, scale=1):
    return 8 * len(s) * scale


def ctext(img, s, cx, y, col=(255, 255, 255), scale=1):
    text(img, s, cx - tw(s, scale) // 2, y, col, scale)


def new(col=(0, 0, 0, 255)):
    return Image.new("RGBA", (W, H), col)


def R(img, x, y, w, h, c):
    ImageDraw.Draw(img).rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def P(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c)


OL = (30, 18, 14, 255)
CREAM = (241, 228, 195, 255)
WOODD = (90, 58, 34, 255)
WOODM = (138, 90, 48, 255)
WOODL = (185, 128, 72, 255)
RED = (200, 55, 45, 255)
YEL = (240, 192, 64, 255)
BLUE = (58, 111, 192, 255)
GRN = (47, 125, 70, 255)
GOLD = (240, 200, 80, 255)
WHITE = (255, 255, 255, 255)
STEEL = (176, 186, 198, 255)
STEELD = (120, 130, 146, 255)
STEELL = (226, 234, 242, 255)
CYAN = (90, 230, 240, 255)
PINK = (255, 90, 170, 255)
DR = (190, 48, 56, 255)


def btn(img, x, y, label, col):
    d = ImageDraw.Draw(img)
    d.ellipse([x, y, x + 10, y + 10], fill=OL)
    d.ellipse([x + 1, y + 1, x + 9, y + 9], fill=col)
    if label == "UP":
        d.polygon([(x + 5, y + 2), (x + 8, y + 7), (x + 2, y + 7)], fill=WHITE)
    else:
        g = glyph(label, (255, 255, 255))
        px = g.load()
        for yy in range(8):
            for xx in range(8):
                if px[xx, yy][:3] == (0, 0, 0):
                    px[xx, yy] = (0, 0, 0, 0)
        img.alpha_composite(g, (x + 1, y + 1))


# ---------------------------------------------------------------------------------------------------- products (16x16)
def milk(img, x, y):
    d = ImageDraw.Draw(img)
    d.polygon([(x + 4, y + 4), (x + 8, y), (x + 12, y + 4)], fill=OL)
    R(img, x + 3, y + 3, 10, 13, OL)
    d.polygon([(x + 5, y + 4), (x + 8, y + 1), (x + 11, y + 4)], fill=(220, 232, 250, 255))
    R(img, x + 4, y + 4, 8, 11, (245, 248, 255, 255))
    R(img, x + 4, y + 8, 8, 4, BLUE)
    R(img, x + 6, y + 9, 4, 2, WHITE)


def can(img, x, y):
    R(img, x + 3, y + 2, 10, 13, OL)
    R(img, x + 4, y + 3, 8, 11, (200, 200, 210, 255))
    R(img, x + 4, y + 5, 8, 7, RED)
    R(img, x + 4, y + 7, 8, 3, CREAM)
    R(img, x + 7, y + 8, 2, 1, RED)
    R(img, x + 4, y + 5, 1, 7, (225, 90, 80, 255))
    R(img, x + 3, y + 2, 10, 1, (120, 120, 135, 255))
    R(img, x + 3, y + 14, 10, 1, (120, 120, 135, 255))


def cereal(img, x, y):
    R(img, x + 2, y + 0, 12, 16, OL)
    R(img, x + 3, y + 1, 10, 14, YEL)
    R(img, x + 3, y + 1, 2, 14, (250, 215, 110, 255))
    d = ImageDraw.Draw(img)
    d.ellipse([x + 5, y + 6, x + 11, y + 11], fill=(200, 110, 40, 255))
    d.ellipse([x + 6, y + 7, x + 10, y + 9], fill=(250, 240, 230, 255))
    R(img, x + 3, y + 2, 10, 2, RED)


def apple(img, x, y):
    d = ImageDraw.Draw(img)
    d.ellipse([x + 2, y + 4, x + 13, y + 15], fill=OL)
    d.ellipse([x + 3, y + 5, x + 12, y + 14], fill=RED)
    R(img, x + 7, y + 1, 2, 4, OL)
    R(img, x + 9, y + 2, 3, 2, GRN)
    P(img, x + 5, y + 7, (240, 130, 110, 255))


ITEMS = [milk, can, cereal, apple]
SEC = [("MILK", BLUE), ("CANS", RED), ("CEREAL", (230, 160, 40, 255))]


def sparkle(img, x, y, c=(255, 245, 170, 255)):
    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 2), (0, -2), (2, 0), (-2, 0)]:
        P(img, x + dx, y + dy, c)


# ---------------------------------------------------------------------------------------------------- STOCK IT! scenery
def stock_bg():
    img = new()
    R(img, 0, 14, 240, 58, (226, 196, 150, 255))
    for x in range(0, 240, 16):
        R(img, x, 14, 1, 58, (214, 182, 134, 255))
    R(img, 0, 56, 240, 16, (150, 100, 56, 255))
    for x in range(0, 240, 10):
        R(img, x, 56, 1, 16, (128, 84, 46, 255))
    for y in range(72, 144, 8):
        R(img, 0, y, 240, 8, (176, 120, 66, 255) if (y // 8) % 2 else (166, 110, 60, 255))
        R(img, 0, y, 240, 1, (120, 78, 40, 255))
        off = (y // 8 * 37) % 40
        for x in range(off, 240, 40):
            R(img, x, y, 1, 8, (120, 78, 40, 255))
    R(img, 0, 72, 240, 3, (110, 72, 38, 255))
    # shelf unit (items are sprites)
    for i, (nm, col) in enumerate(SEC):
        sx = i * 80
        R(img, sx, 14, 4, 58, WOODD)
        R(img, sx + 1, 14, 1, 58, WOODM)
        R(img, sx + 4, 26, 72, 45, (120, 80, 44, 255))
        for by in (45, 67):
            R(img, sx + 4, by, 72, 4, WOODL)
            R(img, sx + 4, by + 3, 72, 1, WOODD)
            R(img, sx + 4, by, 72, 1, (215, 160, 100, 255))
        R(img, sx + 10, 15, 60, 11, OL)
        R(img, sx + 11, 16, 58, 9, col)
        ctext(img, nm, sx + 40, 17, (255, 255, 255))
    R(img, 236, 14, 4, 58, WOODD)
    # top bar (text is drawn by the game)
    R(img, 0, 0, 240, 14, (58, 36, 22, 255))
    R(img, 0, 13, 240, 1, OL)
    R(img, 0, 12, 240, 1, WOODM)
    d = ImageDraw.Draw(img)
    d.ellipse([4, 2, 14, 12], fill=(240, 230, 200, 255), outline=OL)
    d.line([9, 7, 9, 4], fill=OL)
    d.line([9, 7, 12, 7], fill=OL)
    for i in range(4):
        R(img, 194 + i * 10, 4, 8, 6, OL)
        R(img, 195 + i * 10, 5, 6, 4, (70, 50, 36, 255))
    # belt
    R(img, 0, 144, 240, 16, (60, 62, 70, 255))
    R(img, 0, 144, 240, 2, (120, 124, 136, 255))
    R(img, 0, 158, 240, 2, (30, 30, 36, 255))
    for x in range(0, 240, 12):
        R(img, x, 148, 2, 8, (80, 82, 92, 255))
    R(img, 0, 144, 46, 16, (42, 28, 18, 255))
    text(img, "NEXT", 4, 148, (255, 225, 150))
    return img


# ---------------------------------------------------------------------------------------------------- PLATE RUSH scenery
ZX = [96, 146, 196]


def portrait32(name):
    """The dialogue portrait (frame 0) downscaled to 32x32, from the generated pt_<name>_a..d sheets."""
    full = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    for q, (ox, oy) in zip("abcd", ((0, 0), (64, 0), (0, 64), (64, 64))):
        im = Image.open(os.path.join(ROOT, "graphics", f"pt_{name}_{q}.bmp"))
        pal = im.getpalette()
        px = np.array(im)[:64, :64]
        rgba = np.zeros((64, 64, 4), np.uint8)
        for y in range(64):
            for x in range(64):
                k = px[y, x]
                if k != 0:
                    rgba[y, x] = (pal[k * 3], pal[k * 3 + 1], pal[k * 3 + 2], 255)
        full.alpha_composite(Image.fromarray(rgba, "RGBA"), (ox, oy))
    # crop the bust (head and shoulders), then scale
    bust = full.crop((8, 6, 120, 118)).resize((32, 32), Image.BOX)
    a = np.array(bust)
    a[..., 3] = np.where(a[..., 3] > 100, 255, 0)
    return Image.fromarray(a, "RGBA")


def plate(img, cx, cy, state="dirty", w=24):
    d = ImageDraw.Draw(img)
    h = 10
    d.ellipse([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], fill=OL)
    d.ellipse([cx - w // 2 + 1, cy - h // 2 + 1, cx + w // 2 - 1, cy + h // 2 - 1],
              fill=(246, 246, 242, 255) if state != "dirty" else (232, 222, 196, 255))
    d.ellipse([cx - w // 2 + 4, cy - h // 2 + 2, cx + w // 2 - 4, cy + h // 2 - 2],
              fill=(228, 232, 236, 255) if state != "dirty" else (220, 208, 180, 255))
    if state == "dirty":
        for dx, dy, c in [(-6, -1, (140, 70, 36, 255)), (0, 1, (190, 50, 40, 255)), (5, -1, (120, 150, 60, 255)),
                          (-1, -2, (240, 200, 90, 255)), (7, 1, (140, 70, 36, 255))]:
            R(img, cx + dx, cy + dy, 3, 2, c)
    elif state == "soap":
        for dx, dy in [(-7, 0), (-2, -2), (3, 1), (7, -1), (0, 1)]:
            d.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2], fill=WHITE, outline=(170, 200, 230, 255))
    elif state == "clean":
        for dx, dy in [(-6, -1), (6, 0)]:
            sparkle(img, cx + dx, cy + dy - 2, (255, 255, 200, 255))


def shards(img, cx, cy):
    d = ImageDraw.Draw(img)
    for dx, dy in [(-6, -1), (-2, 1), (3, -2), (7, 1)]:
        x, y = cx + dx, cy + dy
        d.polygon([(x - 3, y + 1), (x + 2, y - 2), (x + 3, y + 2)], fill=(246, 246, 242, 255), outline=OL)


def pan(img, cx, cy):
    d = ImageDraw.Draw(img)
    R(img, cx + 13, cy - 1, 14, 3, OL)
    R(img, cx + 14, cy, 12, 1, (90, 60, 40, 255))
    d.ellipse([cx - 15, cy - 6, cx + 15, cy + 6], fill=OL)
    d.ellipse([cx - 14, cy - 5, cx + 14, cy + 5], fill=(70, 74, 86, 255))
    d.ellipse([cx - 10, cy - 3, cx + 10, cy + 3], fill=(52, 54, 64, 255))
    for dx, dy, w in [(-8, -1, 6), (0, 0, 8), (5, -2, 5), (-3, 2, 5)]:
        R(img, cx + dx, cy + dy, w, 2, (176, 120, 40, 255))


def dish_bg():
    img = new()
    R(img, 0, 14, 240, 38, (246, 226, 170, 255))
    for x in range(0, 240, 24):
        R(img, x, 14, 1, 38, (232, 208, 150, 255))
    R(img, 0, 52, 240, 4, DR)
    R(img, 0, 56, 240, 1, WHITE)
    for r in range(3):
        for c in range(20):
            col = (30, 30, 38, 255) if (r + c) % 2 == 0 else (238, 238, 238, 255)
            R(img, c * 12, 57 + r * 12, 12, 12, col)
    R(img, 0, 56, 240, 1, STEELD)
    # neon sign
    R(img, 6, 17, 76, 32, (24, 20, 40, 255))
    R(img, 7, 18, 74, 30, (40, 26, 64, 255))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle([2, 13, 86, 53], fill=(255, 90, 170, 40))
    img.alpha_composite(ov)
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    text(s, "LOU'S", 0, 0, PINK, 2)
    img.alpha_composite(s.crop((0, 0, 80, 16)), (10, 21))
    R(img, 12, 41, 64, 2, CYAN)
    # order window with Lou and Mia
    R(img, 116, 16, 118, 36, STEEL)
    R(img, 117, 17, 116, 34, STEELD)
    R(img, 119, 19, 112, 30, (120, 78, 50, 255))
    try:
        img.alpha_composite(portrait32("lou"), (126, 19))
        img.alpha_composite(portrait32("mia"), (176, 19))
    except Exception as e:      # portraits not generated yet
        print("no portraits for the order window:", e)
    R(img, 116, 48, 118, 4, STEEL)
    R(img, 116, 48, 118, 1, STEELL)
    # sink with suds + brush
    R(img, 74, 76, 46, 18, STEELD)
    R(img, 75, 77, 44, 16, (150, 170, 190, 255))
    R(img, 75, 77, 44, 4, (100, 150, 200, 255))
    d = ImageDraw.Draw(img)
    for x, y, r in [(78, 76, 5), (86, 73, 6), (95, 75, 5), (103, 72, 6), (111, 75, 5), (92, 70, 4), (82, 70, 3), (108, 69, 3)]:
        d.ellipse([x - r, y - r + 2, x + r, y + r + 2], fill=(248, 252, 255, 255), outline=(170, 200, 230, 255))
    R(img, 100, 66, 4, 12, WOODM)
    R(img, 98, 76, 8, 4, YEL)
    # tap
    R(img, 138, 64, 5, 26, STEEL)
    R(img, 138, 64, 2, 26, STEELL)
    R(img, 138, 64, 16, 4, STEEL)
    R(img, 152, 64, 4, 12, STEEL)
    R(img, 150, 76, 8, 3, STEELD)
    R(img, 130, 76, 6, 6, (200, 60, 50, 255))
    for y in (80, 85):
        R(img, 153, y, 2, 3, (120, 190, 250, 255))
    # empty rack
    R(img, 174, 84, 50, 10, STEELD)
    R(img, 175, 85, 48, 8, (100, 108, 122, 255))
    R(img, 174, 84, 50, 2, STEELL)
    # player's apron basket (the player sprite is drawn between this and the counter cover)
    # counter
    R(img, 0, 92, 240, 18, STEEL)
    for y, c in [(93, STEELL), (98, (192, 200, 212, 255)), (104, (168, 178, 192, 255))]:
        R(img, 0, y, 240, 1, c)
    R(img, 0, 106, 240, 2, STEELD)
    R(img, 0, 110, 240, 3, STEELL)
    R(img, 0, 113, 240, 1, STEELD)
    R(img, 0, 114, 240, 46, DR)
    for x in range(8, 240, 24):
        R(img, x, 148, 2, 2, (240, 200, 200, 255))
    R(img, 0, 114, 240, 1, (230, 120, 120, 255))
    R(img, 0, 157, 240, 3, (110, 24, 32, 255))
    # dirty stack
    R(img, 40, 90, 36, 3, STEELD)
    for k in range(4):
        y = 88 - k * 3
        d.ellipse([42, y - 4, 72, y + 4], fill=OL)
        d.ellipse([43, y - 3, 71, y + 3], fill=(236, 226, 200, 255))
        if k % 2 == 0:
            R(img, 52 + k * 3, y - 1, 5, 2, (150, 60, 30, 255))
    R(img, 56, 78, 6, 2, (210, 50, 40, 255))
    # top bar (text by the game)
    R(img, 0, 0, 240, 14, (26, 60, 66, 255))
    R(img, 0, 12, 240, 1, STEEL)
    R(img, 0, 13, 240, 1, OL)
    # zone brackets
    for x in ZX:
        for dx in (-15, 14):
            R(img, x + dx, 96, 1, 10, (255, 255, 255, 255))
    # labels + button icons
    for nm, x, b in [("DIRTY", 50, None), ("SCRUB", ZX[0], ("A", (200, 60, 60, 255))), ("RINSE", ZX[1], ("B", (200, 160, 40, 255))),
                     ("STACK", ZX[2], ("UP", (60, 130, 200, 255)))]:
        ctext(img, nm, x, 136, (255, 235, 225))
        if b:
            btn(img, x - 5, 120, b[0], b[1])
    return img


# ---------------------------------------------------------------------------------------------------- sprite sheets
def key_frame(draw_fn, w, h):
    """Draws onto a magenta key background; returns an RGBA image with the key made transparent."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_fn(img)
    return img


def quantize_sheet(frames, ncolors=15):
    """RGBA frames -> (indices array list, palette) with ONE shared palette; index 0 = transparent."""
    w, h = frames[0].size
    rgb_all = []
    for f in frames:
        a = np.array(f)
        rgb_all.append(a[a[..., 3] > 0][:, :3])
    allpx = np.concatenate(rgb_all)
    uniq = np.unique(allpx, axis=0)
    if len(uniq) <= ncolors:
        pal = [tuple(int(v) for v in c) for c in uniq]
    else:
        sheet = Image.fromarray(allpx.reshape(1, -1, 3).astype(np.uint8), "RGB")
        q = sheet.quantize(colors=ncolors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        p = q.getpalette()[:ncolors * 3]
        pal = [(p[i], p[i + 1], p[i + 2]) for i in range(0, len(p), 3)]
        # keep the outline colour exact
        pal = [tuple(int(v) & 0xF8 for v in c) for c in pal]
    pal = [(255, 0, 255)] + [tuple(c) for c in pal]
    parr = np.array(pal[1:], dtype=np.int32)
    out = []
    for f in frames:
        a = np.array(f)
        idx = np.zeros((h, w), np.uint8)
        for y in range(h):
            for x in range(w):
                if a[y, x, 3] > 0:
                    d = ((parr - a[y, x, :3].astype(np.int32)) ** 2).sum(1)
                    idx[y, x] = int(d.argmin()) + 1
        out.append(idx)
    pal += [(0, 0, 0)] * (16 - len(pal))
    return out, pal[:16]


def write_bmp(path, pixels, width, height, bpp, palette):
    import struct
    data = bytearray()
    for y in range(height - 1, -1, -1):
        row = bytearray()
        if bpp == 8:
            row.extend(bytes(pixels[y]))
        else:
            for x in range(0, width, 2):
                row.append(((int(pixels[y][x]) & 0xF) << 4) | (int(pixels[y][x + 1]) & 0xF))
        row.extend(b"\0" * ((-len(row)) % 4))
        data.extend(row)
    pal = bytearray()
    for r, g, b in palette:
        pal.extend(bytes((b, g, r, 0)))
    offset = 14 + 40 + len(pal)
    header = struct.pack("<2sIHHI", b"BM", offset + len(data), 0, 0, offset)
    info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, bpp, 0, len(data), 2835, 2835, len(palette), len(palette))
    with open(path, "wb") as f:
        f.write(header + info + pal + data)


def write_sprite_sheet(name, frames):
    w, h = frames[0].size
    idx, pal = quantize_sheet(frames)
    pixels = [row for f in idx for row in f.tolist()]
    write_bmp(os.path.join(ROOT, "graphics", name + ".bmp"), pixels, w, h * len(frames), 4, pal)
    with open(os.path.join(ROOT, "graphics", name + ".json"), "w", newline="\n") as f:
        f.write(f'{{\n    "type": "sprite",\n    "height": {h}\n}}\n')


def write_bg(name, img):
    """Full-screen background, 8bpp: colour 0 is the (unused) transparent colour, up to 255 real colours."""
    rgb = img.convert("RGB")
    q = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    p = q.getpalette()[:255 * 3]
    colours = [tuple(int(v) & 0xF8 for v in p[i:i + 3]) for i in range(0, len(p), 3)]
    pal = [(255, 0, 255)] + colours
    pal += [(0, 0, 0)] * (256 - len(pal))
    arr = np.array(q).astype(np.int32) + 1
    # Butano wants regular BGs of 256 x 256: pad (the extra tiles are all empty and get merged)
    full = np.zeros((256, 256), np.uint8)
    full[:arr.shape[0], :arr.shape[1]] = arr.astype(np.uint8)
    write_bmp(os.path.join(ROOT, "graphics", name + ".bmp"), full.tolist(), 256, 256, 8, pal[:256])
    with open(os.path.join(ROOT, "graphics", name + ".json"), "w", newline="\n") as f:
        f.write('{\n    "type": "regular_bg",\n    "bpp_mode": "bpp_8"\n}\n')


def build(preview=None):
    sb = stock_bg()
    db = dish_bg()
    write_bg("mg_stock_bg", sb)
    write_bg("mg_dish_bg", db)
    write_sprite_sheet("mg_items", [key_frame(lambda im, f=f: f(im, 0, 0), 16, 16) for f in ITEMS])

    def fx_x(im):
        d = ImageDraw.Draw(im)
        for k in range(3):
            d.line([1 + k, 1, 13 + k, 13], fill=(255, 60, 50, 255))
            d.line([13 + k, 1, 1 + k, 13], fill=(255, 60, 50, 255))

    def fx_sparkle(im):
        sparkle(im, 8, 8)

    def icon_plate(im, broken=False):
        d = ImageDraw.Draw(im)
        d.ellipse([1, 4, 11, 10], fill=OL)
        d.ellipse([2, 5, 10, 9], fill=(220, 60, 50, 255) if broken else (240, 244, 248, 255))
        if broken:
            R(im, 6, 4, 1, 7, OL)

    def pip(im, full):
        R(im, 2, 5, 8, 6, OL)
        R(im, 3, 6, 6, 4, GOLD if full else (70, 50, 36, 255))

    def shard(im, k):
        d = ImageDraw.Draw(im)
        pts = [(4, 8), (9, 5), (10, 10)] if k == 0 else [(3, 5), (8, 4), (6, 10)]
        d.polygon(pts, fill=(246, 246, 242, 255), outline=OL)

    fx = [key_frame(fx_x, 16, 16), key_frame(fx_sparkle, 16, 16), key_frame(icon_plate, 16, 16),
          key_frame(lambda im: icon_plate(im, True), 16, 16), key_frame(lambda im: pip(im, False), 16, 16),
          key_frame(lambda im: pip(im, True), 16, 16), key_frame(lambda im: shard(im, 0), 16, 16),
          key_frame(lambda im: shard(im, 1), 16, 16)]
    write_sprite_sheet("mg_fx", fx)
    write_sprite_sheet("mg_plate", [key_frame(lambda im: plate(im, 16, 8, "dirty"), 32, 16),
                                    key_frame(lambda im: plate(im, 16, 8, "soap"), 32, 16),
                                    key_frame(lambda im: plate(im, 16, 8, "clean"), 32, 16),
                                    key_frame(lambda im: shards(im, 16, 8), 32, 16)])
    write_sprite_sheet("mg_pan", [key_frame(lambda im: pan(im, 20, 32), 64, 64)])

    def rack_plate(im):
        R(im, 2, 6, 3, 22, OL)
        R(im, 3, 7, 2, 20, (244, 248, 252, 255))
        R(im, 3, 7, 1, 20, (200, 226, 248, 255))

    write_sprite_sheet("mg_rack", [key_frame(rack_plate, 8, 32)])
    write_sprite_sheet("mg_vline", [key_frame(lambda im: R(im, 0, 0, 1, 32, GOLD), 8, 32)])
    write_sprite_sheet("mg_hline", [key_frame(lambda im: R(im, 0, 3, 32, 1, GOLD), 32, 8)])
    cover = db.crop((6, 92, 38, 124)).copy()
    write_sprite_sheet("mg_cover_dish", [cover.convert("RGBA")])
    if preview:
        os.makedirs(preview, exist_ok=True)
        sb.convert("RGB").resize((720, 480), 0).save(os.path.join(preview, "mg_stock_bg.png"))
        db.convert("RGB").resize((720, 480), 0).save(os.path.join(preview, "mg_dish_bg.png"))
    print("minigame art written")


if __name__ == "__main__":
    prev = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    build(prev)
