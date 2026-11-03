#!/usr/bin/env python3
"""
Town Life - map and placeholder graphics generator (pure Python 3, no dependencies).

Generates:
  graphics/city_centre.bmp/.json    512x512 8bpp regular background
  graphics/old_block.bmp/.json      512x512 8bpp regular background
  graphics/corner_market.bmp/.json  256x256 8bpp regular background (interior)
  graphics/player.bmp/.json         16x144 4bpp sprite sheet (9 frames of 16x16)
  include/tl_world_data.h           collision + warps + map table for all maps

Run from the repository root:   python3 tools/gen_graphics.py
Optional preview PNGs (needs Pillow): python3 tools/gen_graphics.py --preview <dir>

The outputs are committed, so the CI build does not need to run this script.

How maps work
-------------
Every map is a grid of 16x16 "metatiles". Each grid cell holds a terrain character (see TERRAIN),
which decides how the cell is painted and whether it is solid. On top of the terrain, "stamps"
draw bigger things (buildings, fountain, signs...) and mark their footprint as solid, except for
the cells listed as walkable (e.g. doors). Warps are trigger rectangles (in metatiles) that move
the player to another map.
"""

import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MT = 16

# ---------------------------------------------------------------------------
# Background palette (8bpp, shared by all maps). Index 0 = backdrop (black).
# ---------------------------------------------------------------------------
BG_COLOURS = [
    ("void", (0, 0, 0)),
    ("outline", (32, 32, 40)),
    ("white", (240, 240, 236)),
    # grass / plants
    ("grass1", (96, 176, 72)), ("grass2", (80, 156, 64)), ("grass3", (52, 116, 52)), ("grass4", (136, 200, 96)),
    ("leaf1", (56, 132, 60)), ("leaf2", (40, 100, 52)), ("leaf3", (96, 172, 80)), ("leaf4", (28, 76, 44)),
    # asphalt / road
    ("asph1", (84, 84, 96)), ("asph2", (96, 96, 108)), ("asph3", (70, 70, 82)),
    ("yellow", (232, 200, 64)), ("orange", (240, 128, 32)), ("red", (208, 56, 56)), ("darkred", (150, 36, 40)),
    # sidewalk
    ("side1", (184, 180, 170)), ("side2", (156, 152, 144)), ("side3", (206, 202, 192)),
    # plaza (gold-ish paving near the tower)
    ("plaza1", (214, 196, 156)), ("plaza2", (186, 166, 128)), ("plaza3", (230, 216, 184)),
    # old block sidewalk / cobbles
    ("old1", (166, 154, 138)), ("old2", (138, 126, 112)), ("old3", (186, 176, 160)),
    ("cob1", (132, 120, 108)), ("cob2", (104, 94, 86)), ("cob3", (160, 148, 134)),
    # brick
    ("brick1", (172, 76, 58)), ("brick2", (138, 58, 46)), ("mortar", (200, 170, 146)),
    ("brickb1", (128, 84, 60)), ("brickb2", (100, 64, 46)),
    # gold
    ("gold1", (248, 208, 72)), ("gold2", (216, 168, 40)), ("gold3", (160, 116, 24)), ("gold4", (255, 240, 168)),
    # glass
    ("glass1", (96, 152, 204)), ("glass2", (144, 196, 236)), ("glass3", (60, 104, 156)), ("glass4", (200, 228, 248)),
    # wood
    ("wood1", (168, 110, 60)), ("wood2", (130, 82, 42)), ("wood3", (200, 146, 88)), ("wood4", (96, 60, 32)),
    # walls
    ("cream1", (234, 218, 180)), ("cream2", (206, 188, 150)),
    ("conc1", (164, 166, 172)), ("conc2", (134, 136, 146)), ("conc3", (192, 194, 200)),
    ("blue1", (64, 112, 184)), ("blue2", (40, 76, 136)),
    ("green1", (48, 140, 84)), ("green2", (32, 104, 60)),
    ("slate1", (92, 96, 120)), ("slate2", (70, 74, 96)),
    # water
    ("water1", (56, 112, 196)), ("water2", (80, 144, 220)), ("water3", (40, 88, 160)), ("water4", (168, 212, 244)),
    # dirt
    ("dirt1", (176, 140, 96)), ("dirt2", (150, 116, 76)), ("dirt3", (196, 164, 120)),
    # misc
    ("pink", (232, 112, 168)), ("purple", (140, 88, 196)), ("teal", (56, 168, 160)),
    ("court1", (196, 96, 64)), ("court2", (172, 80, 52)),
    ("floor1", (206, 150, 92)), ("floor2", (182, 128, 74)), ("floor3", (224, 172, 112)),
    ("iwall1", (240, 222, 178)), ("iwall2", (214, 192, 146)),
]
C = {name: i for i, (name, _) in enumerate(BG_COLOURS)}
assert len(BG_COLOURS) <= 256

# Sprite palette (4bpp, 16 colours, index 0 transparent)
SPRITE_PALETTE = [
    (255, 0, 255), (88, 168, 72), (48, 112, 56), (88, 88, 100), (176, 176, 168), (232, 208, 72),
    (232, 216, 176), (184, 64, 48), (120, 76, 40), (112, 176, 232), (32, 32, 40), (248, 248, 248),
    (240, 192, 152), (56, 96, 200), (48, 104, 192), (232, 112, 168),
]


# ---------------------------------------------------------------------------
# BMP writers
# ---------------------------------------------------------------------------
def _write_bmp(path, pixels, width, height, bpp, palette):
    data = bytearray()
    for y in range(height - 1, -1, -1):
        row = bytearray()
        if bpp == 8:
            row.extend(bytes(pixels[y]))
        else:
            for x in range(0, width, 2):
                row.append(((pixels[y][x] & 0xF) << 4) | (pixels[y][x + 1] & 0xF))
        row.extend(b"\0" * ((-len(row)) % 4))
        data.extend(row)
    colours = len(palette)
    pal = bytearray()
    for r, g, b in palette:
        pal.extend(bytes((b, g, r, 0)))
    offset = 14 + 40 + len(pal)
    header = struct.pack("<2sIHHI", b"BM", offset + len(data), 0, 0, offset)
    info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, bpp, 0, len(data), 2835, 2835, colours, colours)
    with open(path, "wb") as f:
        f.write(header + info + pal + data)


def write_text(path, text):
    with open(path, "w", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------------------
# Canvas + tiny 3x5 pixel font for signs
# ---------------------------------------------------------------------------
_GLYPHS = """
A .#. #.# ### #.# #.#
B ##. #.# ##. #.# ##.
C .## #.. #.. #.. .##
D ##. #.# #.# #.# ##.
E ### #.. ##. #.. ###
F ### #.. ##. #.. #..
G .## #.. #.# #.# .##
H #.# #.# ### #.# #.#
I ### .#. .#. .#. ###
J ..# ..# ..# #.# .#.
K #.# #.# ##. #.# #.#
L #.. #.. #.. #.. ###
M #.# ### ### #.# #.#
N ##. #.# #.# #.# #.#
O .#. #.# #.# #.# .#.
P ##. #.# ##. #.. #..
Q .#. #.# #.# ##. .##
R ##. #.# ##. #.# #.#
S .## #.. .#. ..# ##.
T ### .#. .#. .#. .#.
U #.# #.# #.# #.# ###
V #.# #.# #.# #.# .#.
W #.# #.# ### ### #.#
X #.# #.# .#. #.# #.#
Y #.# #.# .#. .#. .#.
Z ### ..# .#. #.. ###
! .#. .#. .#. ... .#.
"""
FONT = {}
for _line in _GLYPHS.strip().splitlines():
    _parts = _line.split()
    FONT[_parts[0]] = "".join(_parts[1:])
    assert len(FONT[_parts[0]]) == 15, _line


class Canvas:
    def __init__(self, w, h, fill=0):
        self.w, self.h = w, h
        self.p = [[fill] * w for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = C[c] if isinstance(c, str) else c

    def get(self, x, y):
        return self.p[y][x]

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def frame(self, x, y, w, h, c):
        for xx in range(x, x + w):
            self.set(xx, y, c)
            self.set(xx, y + h - 1, c)
        for yy in range(y, y + h):
            self.set(x, yy, c)
            self.set(x + w - 1, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def circle(self, cx, cy, r, c):
        for yy in range(int(cy - r - 1), int(cy + r + 2)):
            for xx in range(int(cx - r - 1), int(cx + r + 2)):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    @staticmethod
    def text_width(s):
        return sum(2 if ch == " " else 4 for ch in s) - 1

    def text(self, x, y, s, c):
        for ch in s:
            if ch == " ":
                x += 2
                continue
            g = FONT[ch]
            for i, bit in enumerate(g):
                if bit == "#":
                    self.set(x + i % 3, y + i // 3, c)
            x += 4

    def text_centered(self, cx, y, s, c):
        self.text(cx - self.text_width(s) // 2, y, s, c)


# ---------------------------------------------------------------------------
# Terrain painters: f(lx, ly) -> colour name for local pixel (0..15)
# ---------------------------------------------------------------------------
def grass(x, y):
    if (x, y) in ((3, 2), (11, 5), (6, 10), (13, 13), (1, 13)):
        return "grass3"
    if (x, y) in ((4, 2), (12, 5), (7, 10), (14, 13), (2, 13)):
        return "grass4"
    return "grass1" if (x * 7 + y * 3) % 11 else "grass2"


def sidewalk(x, y):
    if x % 8 == 0 or y % 8 == 0:
        return "side2"
    if x % 8 == 1 and y % 8 == 1:
        return "side3"
    return "side1"


def plaza(x, y):
    off = 4 if (y // 4) % 2 else 0
    if y % 4 == 0 or (x + off) % 8 == 0:
        return "plaza2"
    if y % 4 == 1 and (x + off) % 8 == 1:
        return "plaza3"
    return "plaza1"


def old_side(x, y):
    if x == 0 or y == 0:
        return "old2"
    if (x, y) in ((5, 6), (6, 7), (7, 7), (8, 8), (11, 3), (12, 4)):  # cracks
        return "old2"
    if x == 1 and y == 1:
        return "old3"
    return "old1"


def cobble(x, y):
    off = 4 if (y // 4) % 2 else 0
    lx, ly = (x + off) % 4, y % 4
    if lx == 3 or ly == 3:
        return "cob2"
    if lx == 0 and ly == 0:
        return "cob3"
    return "cob1"


def asphalt(x, y):
    if (x % 8, y % 8) in ((2, 3), (6, 6)):
        return "asph2"
    if (x % 8, y % 8) in ((5, 1),):
        return "asph3"
    return "asph1"


def road_h(x, y):
    if 7 <= y <= 8 and 2 <= x <= 13:
        return "yellow"
    return asphalt(x, y)


def road_v(x, y):
    if 7 <= x <= 8 and 2 <= y <= 13:
        return "yellow"
    return asphalt(x, y)


def zebra_h(x, y):   # crossing a horizontal road (pedestrians walk north-south)
    if 2 <= x <= 13 and (y % 8) in (1, 2, 3, 4):
        return "white"
    return asphalt(x, y)


def zebra_v(x, y):   # crossing a vertical road
    if 2 <= y <= 13 and (x % 8) in (1, 2, 3, 4):
        return "white"
    return asphalt(x, y)


def water(x, y):
    if (x, y) in ((2, 3), (3, 3), (4, 3), (10, 7), (11, 7), (12, 7), (5, 12), (6, 12), (7, 12)):
        return "water4"
    if (x, y) in ((3, 4), (11, 8), (6, 13)):
        return "water2"
    return "water1" if (x + y) % 9 else "water3"


def embankment(x, y):
    # railing on top, stone blocks below
    if y in (1, 2) or (y < 7 and x % 8 == 1):
        return "outline" if y == 2 or x % 8 == 1 else "conc2"
    if y < 7:
        return sidewalk(x, y + 8)
    if y == 7:
        return "conc2"
    off = 4 if ((y - 8) // 4) % 2 else 0
    if (y - 8) % 4 == 3 or (x + off) % 8 == 7:
        return "conc2"
    return "conc1"


def bridge_l(x, y):
    if x < 3:
        return "conc3" if x == 1 else "outline"
    return asphalt(x, y)


def bridge_m(x, y):
    return road_v(x, y)


def bridge_r(x, y):
    if x > 12:
        return "conc3" if x == 14 else "outline"
    return asphalt(x, y)


def barrier(x, y):
    if 4 <= y <= 9:
        if y in (4, 9):
            return "outline"
        return "orange" if ((x + y) // 3) % 2 else "white"
    if 10 <= y <= 13 and x in (2, 3, 12, 13):
        return "outline"
    return asphalt(x, y)


def tree(x, y, base=grass):
    d = ((x - 7.5) ** 2 + (y - 6.5) ** 2) ** 0.5
    if d <= 6.8:
        if d > 6.0:
            return "leaf4"
        if (x - 7.5) + (y - 6.5) < -4:
            return "leaf3"
        if (x - 7.5) + (y - 6.5) > 4:
            return "leaf2"
        return "leaf1"
    if 6 <= x <= 9 and y >= 12:
        return "wood2" if x != 6 else "wood4"
    if 4 <= x <= 11 and y == 15:
        return "grass3" if base == grass else "side2"
    return base(x, y)


def planter_tree(x, y):
    d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5
    if 6.5 < d <= 7.5:
        return "conc2"
    if d <= 6.5:
        return tree(x, y + 1, lambda a, b: "dirt2")
    return sidewalk(x, y)


def bench(x, y, base):
    if 3 <= y <= 5 and 1 <= x <= 14:
        return "wood2" if y == 5 else "wood1"
    if 7 <= y <= 10 and 1 <= x <= 14:
        return "wood4" if y == 10 else ("wood3" if y == 7 else "wood1")
    if 11 <= y <= 13 and x in (2, 3, 12, 13):
        return "outline"
    return base(x, y)


def park_path(x, y):
    if (x, y) in ((3, 4), (10, 2), (7, 11), (13, 9)):
        return "dirt2"
    if (x, y) in ((4, 4), (11, 2)):
        return "dirt3"
    return "dirt1"


def flowers(x, y):
    spots = {(3, 3): "pink", (10, 2): "yellow", (6, 7): "white", (13, 8): "red", (2, 11): "yellow",
             (9, 12): "pink", (12, 14): "white", (6, 14): "red"}
    if (x, y) in spots:
        return spots[(x, y)]
    if (x, y - 1) in spots or (x, y + 1) in spots:
        return "leaf1"
    return grass(x, y)


def hedge(x, y):
    if y >= 14:
        return "leaf4"
    if y <= 1:
        return "leaf3" if x % 4 else "leaf1"
    return "leaf1" if (x * 3 + y * 5) % 7 else "leaf2"


def lamp(x, y, base=sidewalk):
    if 6 <= x <= 9 and 0 <= y <= 3:
        return "yellow" if 1 <= y <= 2 and 7 <= x <= 8 else "outline"
    if 7 <= x <= 8 and 4 <= y <= 13:
        return "slate2" if x == 7 else "slate1"
    if 5 <= x <= 10 and 13 <= y <= 14:
        return "outline"
    return base(x, y)


def wood_fence(x, y):
    if y in (5, 6, 10) or (x in (2, 13) and 3 <= y <= 13):
        return "wood2" if y != 6 else "wood4"
    return grass(x, y)


def site_fence(x, y):
    if y <= 13:
        if y in (0, 13) or x in (0, 15):
            return "slate2"
        if 5 <= y <= 7:
            return "orange"
        return "conc1" if (x // 4) % 2 else "conc3"
    return "dirt2"


def dirt(x, y):
    if (x, y) in ((2, 3), (9, 6), (5, 11), (13, 13)):
        return "dirt2"
    if (x, y) in ((11, 2), (4, 8)):
        return "dirt3"
    return "dirt1"


def rubble(x, y):
    if (x, y) in ((3, 3), (4, 3), (3, 4), (10, 9), (11, 9), (11, 10), (6, 13), (7, 13)):
        return "conc2"
    if (x, y) in ((4, 4), (10, 10), (7, 14)):
        return "conc3"
    return dirt(x, y)


def garden(x, y):
    if y % 8 in (2, 3, 4):
        if x % 4 == 1 and y % 8 == 3:
            return "leaf3"
        if x % 4 in (0, 2) and y % 8 in (3, 4):
            return "leaf1"
        return "dirt2"
    return "dirt3" if y % 8 == 6 else "dirt1"


def wood_floor(x, y):
    if y % 4 == 3:
        return "floor2"
    off = 6 if (y // 4) % 2 else 0
    if (x + off) % 12 == 0:
        return "floor2"
    if y % 4 == 0:
        return "floor3"
    return "floor1"


def int_wall(x, y):
    # 16px: top part light wall, lower half wooden wainscot
    if y < 9:
        return "iwall1" if y != 8 else "iwall2"
    if y == 9 or y == 15:
        return "wood4"
    return "wood1" if x % 4 else "wood2"


def int_side_wall(x, y):
    return "wood2" if (x + y) % 5 else "wood4"


def void(x, y):
    return "void"


def doormat(x, y):
    if 1 <= x <= 14 and 2 <= y <= 13:
        return "darkred" if (x + y) % 2 else "red"
    return wood_floor(x, y)


def court(x, y):
    return "court1" if (x // 8 + y // 8) % 2 else "court2"


# char -> (painter, solid)
TERRAIN = {
    ".": (grass, False),
    "s": (sidewalk, False),
    "P": (plaza, False),
    "o": (old_side, False),
    "c": (cobble, False),
    "R": (asphalt, False),
    "h": (road_h, False),
    "v": (road_v, False),
    "Z": (zebra_h, False),
    "z": (zebra_v, False),
    "~": (water, True),
    "E": (embankment, True),
    "[": (bridge_l, False),
    "=": (bridge_m, False),
    "]": (bridge_r, False),
    "X": (barrier, True),
    "t": (tree, True),
    "q": (planter_tree, True),
    "b": (lambda x, y: bench(x, y, park_path), True),
    "B": (lambda x, y: bench(x, y, plaza), True),
    "n": (lambda x, y: bench(x, y, old_side), True),
    "p": (park_path, False),
    "f": (flowers, False),
    "H": (hedge, True),
    "l": (lamp, True),
    "L": (lambda x, y: lamp(x, y, old_side), True),
    "F": (wood_fence, True),
    "C": (site_fence, True),
    "d": (dirt, False),
    "u": (rubble, False),
    "g": (garden, False),
    "w": (wood_floor, False),
    "W": (int_wall, True),
    "Y": (int_side_wall, True),
    " ": (void, True),
    "m": (doormat, False),
    "k": (court, False),
}


# ---------------------------------------------------------------------------
# Stamps: big objects painted in pixels over a rectangle of metatiles.
# Signature: fn(canvas, x, y, w, h) with x, y, w, h in PIXELS.
# ---------------------------------------------------------------------------
def brick_wall(cv, x, y, w, h, c1="brick1", c2="brick2"):
    for yy in range(h):
        for xx in range(w):
            off = 4 if (yy // 4) % 2 else 0
            if yy % 4 == 3 or (xx + off) % 8 == 7:
                c = "mortar"
            else:
                c = c1 if (xx // 8 + yy // 4) % 3 else c2
            cv.set(x + xx, y + yy, c)


def window(cv, x, y, w=8, h=8, frame="white", glass="glass1", lit=False):
    cv.rect(x, y, w, h, frame)
    cv.rect(x + 1, y + 1, w - 2, h - 2, "yellow" if lit else glass)
    cv.set(x + 1, y + 1, "glass4" if not lit else "gold4")
    cv.set(x + 2, y + 1, "glass4" if not lit else "gold4")
    cv.hline(x + 1, y + h // 2, w - 2, frame)


def door(cv, x, y, w=10, h=14, colour="wood1", frame="wood4"):
    cv.rect(x, y, w, h, frame)
    cv.rect(x + 1, y + 1, w - 2, h - 1, colour)
    cv.rect(x + 2, y + 2, w - 4, 4, "glass1")
    cv.set(x + w - 3, y + h // 2 + 1, "gold1")


def tower(cv, x, y, w, h):
    # Victor Vault's golden VaultTech tower
    crown = 32
    body_y = y + crown
    body_h = h - crown
    # crown: stepped golden top with antenna
    cv.rect(x + w // 2 - 1, y, 2, 10, "gold3")
    cv.set(x + w // 2 - 1, y, "red")
    cv.set(x + w // 2, y, "red")
    cv.rect(x + 40, y + 10, w - 80, 8, "gold2")
    cv.rect(x + 24, y + 18, w - 48, 8, "gold1")
    cv.rect(x + 8, y + 26, w - 16, 6, "gold2")
    for xx in range(x + 40, x + w - 40, 4):
        cv.set(xx, y + 10, "gold4")
    for xx in range(x + 24, x + w - 24, 4):
        cv.set(xx, y + 18, "gold4")
    # body: glass curtain wall with gold frame
    cv.rect(x, body_y, w, body_h, "gold3")
    cv.rect(x + 2, body_y, w - 4, body_h - 2, "gold2")
    for wy in range(body_y + 4, y + h - 40, 16):
        for wx in range(x + 6, x + w - 10, 12):
            shade = "glass3" if wx > x + w * 3 // 4 else "glass1"
            cv.rect(wx, wy, 8, 11, shade)
            cv.rect(wx, wy, 3, 3, "glass4" if shade == "glass1" else "glass2")
            cv.hline(wx, wy + 11, 8, "gold1")
    # sign plate
    sy = y + h - 36
    cv.rect(x + 12, sy, w - 24, 11, "outline")
    cv.frame(x + 12, sy, w - 24, 11, "gold1")
    cv.text_centered(x + w // 2, sy + 3, "VAULTTECH", "gold1")
    # entrance (big glass doors, locked for now)
    dx = x + w // 2 - 16
    cv.rect(dx - 2, y + h - 22, 36, 22, "gold3")
    cv.rect(dx, y + h - 20, 32, 20, "glass3")
    cv.rect(dx + 2, y + h - 18, 13, 18, "glass1")
    cv.rect(dx + 17, y + h - 18, 13, 18, "glass1")
    cv.vline(dx + 15, y + h - 20, 20, "gold1")
    cv.vline(dx + 16, y + h - 20, 20, "gold1")
    cv.rect(dx + 3, y + h - 17, 3, 6, "glass4")
    cv.rect(dx + 18, y + h - 17, 3, 6, "glass4")


def corner_market(cv, x, y, w, h):
    # flat roof edge
    cv.rect(x, y, w, 6, "wood4")
    cv.rect(x, y + 6, w, h - 6, "brick1")
    brick_wall(cv, x, y + 6, w, h - 6)
    # sign board
    cv.rect(x + 8, y + 10, w - 16, 13, "green2")
    cv.rect(x + 9, y + 11, w - 18, 11, "green1")
    cv.text_centered(x + w // 2, y + 14, "CORNER MARKET", "white")
    # upper windows
    for wx in range(x + 8, x + w - 8, 20):
        window(cv, wx, y + 28, 12, 12, lit=True)
    # awning (green/white stripes, scalloped)
    ay = y + h - 40
    for xx in range(w):
        c = "green1" if (xx // 6) % 2 == 0 else "white"
        for yy in range(10):
            cv.set(x + xx, ay + yy, c)
        if (xx % 6) in (1, 2, 3, 4):
            cv.set(x + xx, ay + 10, c)
    cv.hline(x, ay, w, "green2")
    # shop windows with goods
    wy = y + h - 26
    for wx in (x + 4, x + w - 32):
        cv.rect(wx, wy, 28, 18, "wood4")
        cv.rect(wx + 1, wy + 1, 26, 16, "glass2")
        for i, c in enumerate(("red", "yellow", "orange", "green1", "pink", "red", "yellow")):
            cv.rect(wx + 3 + i * 3, wy + 10, 2, 3, c)
            cv.rect(wx + 4 + i * 3, wy + 5, 2, 3, ("orange", "green1", "red", "yellow")[i % 4])
        cv.hline(wx + 1, wy + 13, 26, "wood2")
        cv.hline(wx + 1, wy + 8, 26, "wood2")
    # door (center), the warp is on this metatile
    door(cv, x + 2 * MT + 2, y + h - 16, 12, 16, "wood1", "wood4")


def apartment(cv, x, y, w, h, c1="brick1", c2="brick2", roof="slate1", lit=(), doors=()):
    cv.rect(x, y, w, 8, roof)
    cv.hline(x, y + 7, w, "outline")
    if c1.startswith("brick"):
        brick_wall(cv, x, y + 8, w, h - 8, c1, c2)
    else:
        cv.rect(x, y + 8, w, h - 8, c1)
        for yy in range(y + 8, y + h, 8):
            cv.hline(x, yy, w, c2)
    i = 0
    for wy in range(y + 12, y + h - 16, 16):
        for wx in range(x + 4, x + w - 8, 16):
            window(cv, wx, wy, 8, 10, lit=(i in lit))
            i += 1
    for d in doors:
        door(cv, x + d * 16 + 3, y + h - 15, 10, 15, "blue1", "outline")
    cv.hline(x, y + h - 1, w, "outline")


def office(cv, x, y, w, h):
    cv.rect(x, y, w, h, "conc1")
    cv.rect(x, y, w, 6, "conc2")
    for wy in range(y + 10, y + h - 24, 12):
        cv.rect(x + 4, wy, w - 8, 7, "glass3")
        for wx in range(x + 4, x + w - 4, 8):
            cv.vline(wx, wy, 7, "conc2")
            cv.set(wx + 2, wy + 1, "glass2")
    cv.rect(x + w // 2 - 12, y + h - 20, 24, 20, "conc2")
    cv.rect(x + w // 2 - 10, y + h - 18, 20, 18, "glass1")
    cv.vline(x + w // 2, y + h - 18, 18, "conc3")
    cv.hline(x, y + h - 1, w, "outline")


def cafe(cv, x, y, w, h):
    apartment(cv, x, y, w, h - 24, "cream1", "cream2", "wood4", lit=(1,))
    by = y + h - 24
    cv.rect(x, by, w, 24, "cream1")
    for xx in range(w):
        c = "red" if (xx // 5) % 2 == 0 else "white"
        for yy in range(8):
            cv.set(x + xx, by + yy, c)
    cv.rect(x + 6, by - 10, 30, 9, "wood4")
    cv.text(x + 8, by - 8, "CAFE", "white")
    window(cv, x + 4, by + 10, 20, 12, lit=True)
    door(cv, x + w // 2 - 5 + 10, by + 10, 10, 14, "red", "wood4")
    cv.hline(x, y + h - 1, w, "outline")


def laundromat(cv, x, y, w, h):
    apartment(cv, x, y, w, h - 26, "cream2", "cream1", "slate2", lit=(0, 3))
    by = y + h - 26
    cv.rect(x, by, w, 26, "conc3")
    cv.rect(x + 4, by + 2, w - 8, 9, "blue2")
    cv.text_centered(x + w // 2, by + 4, "LAUNDRY", "white")
    cv.rect(x + 4, by + 13, w - 24, 12, "glass2")
    for wx in range(x + 7, x + w - 24, 10):
        cv.circle(wx + 3, by + 19, 3, "conc2")
        cv.circle(wx + 3, by + 19, 2, "glass1")
    door(cv, x + w - 17, by + 11, 10, 15, "blue1", "outline")
    cv.hline(x, y + h - 1, w, "outline")


def bakery(cv, x, y, w, h):
    apartment(cv, x, y, w, h - 24, "brickb1", "brickb2", "slate1", lit=(0,))
    by = y + h - 24
    cv.rect(x, by, w, 24, "cream1")
    for xx in range(w):
        c = "orange" if (xx // 5) % 2 == 0 else "cream1"
        for yy in range(7):
            cv.set(x + xx, by + yy, c)
    cv.rect(x + 4, by - 10, 31, 9, "wood4")
    cv.text(x + 6, by - 8, "BREAD", "yellow")
    window(cv, x + 4, by + 9, 18, 12, lit=True)
    door(cv, x + w - 16, by + 9, 10, 15, "wood1", "wood4")
    cv.hline(x, y + h - 1, w, "outline")


def bus_stop(cv, x, y, w, h):
    cv.rect(x + 2, y + 1, w - 4, 4, "blue2")
    cv.rect(x + 2, y + 5, w - 4, h - 7, "glass2")
    cv.rect(x + 4, y + h - 6, w - 8, 3, "wood1")
    cv.vline(x + 2, y + 1, h - 2, "outline")
    cv.vline(x + w - 3, y + 1, h - 2, "outline")
    cv.rect(x + 4, y + 7, 14, 7, "white")
    cv.text(x + 5, y + 8, "BUS", "blue2")


def sign_closed(cv, x, y, w, h):
    cv.rect(x + 2, y + 1, w - 4, 10, "white")
    cv.rect(x + 3, y + 2, w - 6, 8, "red")
    cv.text_centered(x + w // 2, y + 4, "CLOSED", "white")
    cv.vline(x + 6, y + 11, h - 12, "outline")
    cv.vline(x + w - 7, y + 11, h - 12, "outline")


def fountain(cv, x, y, w, h):
    cx, cy = x + w / 2 - 0.5, y + h / 2 - 0.5
    cv.circle(cx, cy, 15, "conc2")
    cv.circle(cx, cy, 13.5, "conc3")
    cv.circle(cx, cy, 12, "water1")
    cv.circle(cx, cy, 4, "conc3")
    cv.circle(cx, cy, 2.5, "water4")
    for (dx, dy) in ((-7, -3), (6, 4), (-3, 8), (5, -8)):
        cv.set(int(cx + dx), int(cy + dy), "water4")
        cv.set(int(cx + dx) + 1, int(cy + dy), "water2")


def cafe_table(cv, x, y, w, h):
    cv.circle(x + 7.5, y + 6.5, 6, "red")
    cv.circle(x + 7.5, y + 6.5, 3, "white")
    cv.vline(x + 7, y + 12, 3, "outline")
    cv.vline(x + 8, y + 12, 3, "outline")


def billboard(cv, x, y, w, h):
    cv.rect(x, y, w, h - 10, "gold3")
    cv.rect(x + 2, y + 2, w - 4, h - 14, "outline")
    cv.text_centered(x + w // 2, y + 6, "SMART CITY", "gold1")
    cv.text_centered(x + w // 2, y + 14, "COMING SOON", "white")
    cv.text_centered(x + w // 2, y + 23, "VAULTTECH", "gold2")
    cv.vline(x + 8, y + h - 10, 10, "slate2")
    cv.vline(x + w - 9, y + h - 10, 10, "slate2")


def crane(cv, x, y, w, h):
    mx = x + 10
    for yy in range(y + 8, y + h):
        cv.set(mx, yy, "yellow")
        cv.set(mx + 5, yy, "yellow")
        if (yy - y) % 6 == 0:
            cv.hline(mx, yy, 6, "gold2")
        if (yy - y) % 6 == 3:
            cv.set(mx + 2, yy, "gold2")
            cv.set(mx + 3, yy, "gold2")
    cv.rect(x, y + 6, w, 4, "yellow")
    for xx in range(x, x + w, 4):
        cv.set(xx, y + 7, "gold3")
    cv.rect(x + w - 10, y + 10, 1, 18, "outline")
    cv.rect(x + w - 12, y + 28, 5, 4, "conc2")
    cv.rect(mx - 2, y + 2, 10, 6, "orange")
    cv.rect(mx, y + 3, 4, 3, "glass2")


def bulldozer(cv, x, y, w, h):
    cv.rect(x + 2, y + h - 10, w - 4, 8, "outline")
    for xx in range(x + 3, x + w - 3, 3):
        cv.set(xx, y + h - 6, "conc2")
    cv.rect(x + 6, y + 6, w - 14, h - 16, "yellow")
    cv.rect(x + 10, y + 2, 10, 8, "yellow")
    cv.rect(x + 12, y + 3, 6, 5, "glass2")
    cv.rect(x + w - 8, y + 10, 6, h - 14, "conc2")
    cv.hline(x + 6, y + 12, w - 14, "gold3")


def court_lines(cv, x, y, w, h):
    cv.frame(x + 2, y + 2, w - 4, h - 4, "white")
    cv.hline(x + 2, y + h // 2, w - 4, "white")
    cv.circle(x + w / 2, y + h / 2, 10, "white")
    cv.circle(x + w / 2, y + h / 2, 9, "court1")
    cv.hline(x + 2, y + h // 2, w - 4, "white")
    # hoop at the top
    cv.rect(x + w // 2 - 8, y - 2, 16, 3, "white")
    cv.vline(x + w // 2, y + 1, 4, "outline")
    cv.circle(x + w / 2 - 0.5, y + 7, 3, "orange")
    cv.circle(x + w / 2 - 0.5, y + 7, 2, "court2")


def graffiti_wall(cv, x, y, w, h):
    brick_wall(cv, x, y, w, h, "brickb1", "brickb2")
    cv.hline(x, y, w, "outline")
    cols = ("pink", "teal", "yellow", "purple", "orange")
    for i in range(0, w - 8, 9):
        c = cols[(i // 9) % len(cols)]
        cv.circle(x + i + 5, y + h / 2, 4, c)
        cv.circle(x + i + 8, y + h / 2 - 2, 3, cols[(i // 9 + 2) % len(cols)])
    cv.text(x + 4, y + h - 7, "OLD BLOCK", "white")
    cv.hline(x, y + h - 1, w, "outline")


def shelf(cv, x, y, w, h):
    cv.rect(x, y + 2, w, h - 3, "wood4")
    cv.rect(x + 1, y + 3, w - 2, h - 5, "wood2")
    goods = ("red", "yellow", "green1", "orange", "blue1", "pink", "white", "purple")
    for i, xx in enumerate(range(x + 2, x + w - 2, 3)):
        c = goods[(i * 3 + x // 16) % len(goods)]
        cv.rect(xx, y + 4, 2, 4, c)
        cv.rect(xx, y + 9, 2, 3, goods[(i * 5 + 1) % len(goods)])
    cv.hline(x + 1, y + 8, w - 2, "wood3")
    cv.hline(x, y + h - 1, w, "outline")


def wall_shelf(cv, x, y, w, h):
    cv.rect(x, y + 1, w, h - 2, "wood2")
    goods = ("red", "yellow", "green1", "orange", "blue1", "pink")
    for row in (0, 1):
        yy = y + 3 + row * 6
        for i, xx in enumerate(range(x + 2, x + w - 2, 4)):
            cv.rect(xx, yy, 3, 4, goods[(i + row * 2) % len(goods)])
        cv.hline(x + 1, yy + 4, w - 2, "wood3")


def counter(cv, x, y, w, h):
    cv.rect(x, y + 3, w, h - 4, "wood4")
    cv.rect(x + 1, y + 4, w - 2, 4, "wood3")
    cv.rect(x + 1, y + 8, w - 2, h - 10, "wood1")
    # cash register
    rx = x + w // 2 - 6
    cv.rect(rx, y, 12, 7, "conc2")
    cv.rect(rx + 2, y + 1, 8, 3, "teal")
    cv.hline(x, y + h - 1, w, "outline")


def fridge(cv, x, y, w, h):
    cv.rect(x + 1, y, w - 2, h, "conc3")
    cv.frame(x + 1, y, w - 2, h, "conc2")
    for yy in range(y + 3, y + h - 3, 16):
        cv.rect(x + 3, yy, w - 6, 12, "glass2")
        for i in range(3):
            cv.rect(x + 4 + i * 3, yy + 2, 2, 3, ("red", "white", "orange")[i])
            cv.rect(x + 4 + i * 3, yy + 7, 2, 3, ("green1", "yellow", "blue1")[i])


def crates(cv, x, y, w, h):
    for (cx, cy) in ((x + 1, y + 2), (x + 8, y + 5)):
        cv.rect(cx, cy, 8, 8, "wood1")
        cv.frame(cx, cy, 8, 8, "wood4")
        cv.set(cx + 2, cy + 2, "wood4")
        cv.set(cx + 5, cy + 5, "wood4")
    for i in range(4):
        cv.set(x + 3 + i, y + 3, "red")


def plant(cv, x, y, w, h):
    cv.rect(x + 5, y + 10, 6, 5, "brick1")
    cv.circle(x + 7.5, y + 6, 5, "leaf1")
    cv.circle(x + 6, y + 4, 2, "leaf3")


def back_window(cv, x, y, w, h):
    window(cv, x + 2, y + 1, w - 4, 7, frame="wood4", glass="glass2")


# ---------------------------------------------------------------------------
# Map model
# ---------------------------------------------------------------------------
class Map:
    def __init__(self, ident, display_name, w, h, fill):
        self.ident = ident
        self.display_name = display_name
        self.w, self.h = w, h
        self.grid = [[fill] * w for _ in range(h)]
        self.stamps = []
        self.solid_override = {}
        self.warps = []

    def put(self, mx, my, ch):
        if 0 <= mx < self.w and 0 <= my < self.h:
            self.grid[my][mx] = ch

    def fill(self, mx, my, w, h, ch):
        for y in range(my, my + h):
            for x in range(mx, mx + w):
                self.put(x, y, ch)

    def stamp(self, fn, mx, my, w, h, walkable=(), solid=True, **kw):
        self.stamps.append((fn, mx, my, w, h, kw))
        if solid:
            for y in range(my, my + h):
                for x in range(mx, mx + w):
                    if (x - mx, y - my) not in walkable:
                        self.solid_override[(x, y)] = True
                    else:
                        self.solid_override[(x, y)] = False

    def warp(self, mx, my, w, h, target, tx=None, ty=None, facing=None):
        """Trigger rect in metatiles. tx/ty: target position in PIXELS (None keeps current)."""
        self.warps.append((mx, my, w, h, target, tx, ty, facing))

    def render(self):
        cv = Canvas(self.w * MT, self.h * MT)
        solid = [[False] * self.w for _ in range(self.h)]
        for my in range(self.h):
            for mx in range(self.w):
                painter, s = TERRAIN[self.grid[my][mx]]
                solid[my][mx] = s
                for ly in range(MT):
                    for lx in range(MT):
                        cv.p[my * MT + ly][mx * MT + lx] = C[painter(lx, ly)]
        for fn, mx, my, w, h, kw in self.stamps:
            fn(cv, mx * MT, my * MT, w * MT, h * MT, **kw)
        for (mx, my), s in self.solid_override.items():
            solid[my][mx] = s
        return cv, solid


# ---------------------------------------------------------------------------
# District 1: City Centre
# ---------------------------------------------------------------------------
def build_city_centre():
    m = Map("city_centre", "City Centre", 32, 32, "s")

    # Borders
    m.fill(0, 0, 32, 1, "H")
    m.fill(0, 0, 1, 28, "H")
    m.fill(31, 0, 1, 28, "H")

    # Main street (north-south) and avenue (west-east, continues east to Old Block)
    for y in range(0, 27):
        m.put(8, y, "R"); m.put(9, y, "v"); m.put(10, y, "R")
    for x in range(8, 32):
        m.put(x, 14, "R"); m.put(x, 15, "h"); m.put(x, 16, "R")
    m.fill(8, 14, 3, 3, "R")
    m.fill(12, 14, 1, 3, "Z")
    m.fill(28, 14, 1, 3, "Z")
    m.fill(8, 12, 3, 1, "z")
    m.fill(8, 18, 3, 1, "z")
    m.fill(31, 13, 1, 5, "s")
    m.fill(31, 14, 1, 3, "R")
    m.put(31, 15, "h")

    # North end of the main street: road works (future district)
    m.fill(8, 1, 3, 1, "X")

    # River with the closed bridge to the Docks
    m.fill(0, 28, 32, 1, "E")
    m.fill(0, 29, 32, 3, "~")
    for y in range(28, 32):
        m.put(8, y, "["); m.put(9, y, "="); m.put(10, y, "]")
    m.fill(8, 27, 3, 1, "X")
    m.stamp(sign_closed, 11, 26, 2, 1)

    # North-west: office block
    m.stamp(office, 1, 2, 6, 8)
    m.put(2, 11, "q"); m.put(6, 11, "q")
    m.put(7, 13, "l")

    # North-middle: apartments above Corner Market
    m.stamp(apartment, 11, 1, 8, 5, lit=(2, 5, 9, 12), doors=(1, 6))
    m.put(11, 13, "l"); m.put(18, 13, "l")

    # Corner Market (door at relative (2, 5) -> warp into the interior)
    m.stamp(corner_market, 12, 7, 6, 6, walkable=((2, 5),))
    m.warp(14, 12, 1, 1, "corner_market", 8 * MT, 12 * MT + 4, "up")

    # VaultTech tower with golden plaza
    m.fill(19, 1, 12, 13, "P")
    m.stamp(tower, 20, 1, 8, 11)
    m.put(19, 12, "q"); m.put(28, 12, "q"); m.put(30, 4, "q"); m.put(30, 8, "q")

    # South-west: City Park (the bench you will sleep on lives here)
    m.fill(1, 18, 7, 10, ".")
    m.fill(4, 18, 1, 10, "p")
    m.fill(1, 22, 7, 1, "p")
    m.put(3, 20, "b"); m.put(5, 20, "b")
    m.put(2, 24, "b")
    for (x, y) in ((1, 19), (7, 19), (1, 27), (7, 23), (6, 27), (2, 26)):
        m.put(x, y, "t")
    for (x, y) in ((2, 18), (6, 18), (3, 25), (1, 23)):
        m.put(x, y, "f")
    m.fill(5, 24, 2, 2, "~")
    m.put(7, 17, "l")

    # South-middle: fountain square
    m.fill(11, 18, 9, 9, "P")
    m.stamp(fountain, 14, 21, 2, 2)
    m.put(12, 20, "B"); m.put(17, 20, "B"); m.put(12, 24, "B"); m.put(17, 24, "B")
    m.put(11, 18, "q"); m.put(19, 18, "q")
    m.put(19, 26, "q")
    m.put(11, 17, "l"); m.put(19, 17, "l")

    # South-east: cafe, bus stop, bank/office
    m.stamp(cafe, 21, 18, 4, 5)
    m.stamp(cafe_table, 21, 23, 1, 1)
    m.stamp(cafe_table, 23, 23, 1, 1)
    m.stamp(office, 26, 18, 5, 8)
    m.stamp(bus_stop, 22, 17, 2, 1)
    m.put(21, 26, "q"); m.put(24, 26, "q")
    m.put(27, 13, "l")

    # Exit east to Old Block (keep the vertical position)
    m.warp(31, 13, 1, 5, "old_block", 1 * MT + 8, None, "right")
    return m


# ---------------------------------------------------------------------------
# District 1: Old Block
# ---------------------------------------------------------------------------
def build_old_block():
    m = Map("old_block", "Old Block", 32, 32, "o")

    # Borders
    m.fill(0, 0, 32, 1, "F")
    m.fill(0, 0, 1, 28, "F")
    m.fill(0, 13, 1, 5, "o")
    m.fill(0, 14, 1, 3, "c")

    # Cobbled main street and a narrow side street
    m.fill(0, 14, 26, 3, "c")
    m.fill(12, 1, 2, 27, "c")

    # River (no bridge here)
    m.fill(0, 28, 32, 1, "E")
    m.fill(0, 29, 32, 3, "~")

    # VaultTech demolition site on the east side
    m.fill(26, 1, 1, 27, "C")
    m.fill(27, 0, 5, 28, "u")
    m.fill(27, 0, 5, 1, "C")
    m.stamp(crane, 27, 2, 4, 6)
    m.stamp(bulldozer, 28, 17, 3, 2)
    m.stamp(billboard, 22, 9, 4, 3)

    # North-west: row houses
    m.stamp(apartment, 1, 2, 3, 5, c1="brick1", c2="brick2", roof="slate1", lit=(1,), doors=(1,))
    m.stamp(apartment, 4, 2, 3, 5, c1="cream1", c2="cream2", roof="slate2", lit=(0, 4), doors=(1,))
    m.stamp(apartment, 7, 2, 3, 5, c1="brickb1", c2="brickb2", roof="slate1", doors=(1,))
    m.put(10, 3, "t"); m.put(10, 6, "L")

    # Community garden + graffiti wall
    m.fill(1, 8, 6, 1, "F")
    m.fill(1, 9, 6, 3, "g")
    m.put(1, 12, "f"); m.put(6, 12, "f")
    m.fill(2, 12, 4, 1, ".")
    m.stamp(graffiti_wall, 7, 9, 4, 3)
    m.put(11, 12, "L")

    # North-east: more row houses + laundromat
    m.stamp(apartment, 14, 2, 3, 5, c1="cream2", c2="cream1", roof="slate1", lit=(2,), doors=(1,))
    m.stamp(apartment, 17, 2, 3, 5, c1="brick1", c2="brick2", roof="slate2", lit=(0, 3), doors=(1,))
    m.stamp(apartment, 20, 2, 3, 5, c1="brickb1", c2="brickb2", roof="slate1", doors=(1,))
    m.stamp(laundromat, 14, 8, 5, 5)
    m.put(23, 3, "t"); m.put(24, 6, "t"); m.put(20, 12, "L")
    m.put(19, 9, "n")

    # South-west: neighbourhood basketball court
    m.fill(1, 18, 10, 10, ".")
    m.fill(2, 19, 6, 6, "k")
    m.stamp(court_lines, 2, 19, 6, 6, solid=False)
    m.put(4, 19, "Y"); m.put(5, 19, "Y")   # hoop pole (solid)
    m.put(9, 20, "n"); m.put(9, 23, "n")
    for (x, y) in ((1, 26), (5, 26), (10, 18), (10, 26), (1, 18)):
        m.put(x, y, "t")
    m.put(11, 17, "L")

    # South-east: bakery + old apartment block
    m.stamp(apartment, 14, 18, 5, 6, c1="cream2", c2="cream1", roof="slate2", lit=(1, 6), doors=(2,))
    m.stamp(bakery, 20, 18, 4, 5)
    m.put(15, 26, "t"); m.put(19, 26, "t"); m.put(22, 25, "f"); m.put(24, 24, "L")
    m.put(25, 17, "L")

    # Exit west to City Centre
    m.warp(0, 13, 1, 5, "city_centre", 30 * MT + 8, None, "left")
    return m


# ---------------------------------------------------------------------------
# District 1: Corner Market interior
# ---------------------------------------------------------------------------
def build_corner_market():
    m = Map("corner_market", "Corner Market", 16, 16, " ")
    m.fill(1, 2, 14, 12, "Y")
    m.fill(2, 3, 12, 2, "W")
    m.fill(2, 5, 12, 8, "w")
    m.fill(7, 13, 2, 1, "m")

    m.stamp(wall_shelf, 3, 3, 4, 1)
    m.stamp(back_window, 7, 3, 2, 1)
    m.stamp(wall_shelf, 9, 3, 4, 1)
    m.stamp(shelf, 3, 7, 4, 1)
    m.stamp(shelf, 3, 9, 4, 1)
    m.stamp(shelf, 9, 7, 3, 1)
    m.stamp(shelf, 9, 9, 3, 1)
    m.stamp(fridge, 13, 5, 1, 5)
    m.stamp(counter, 10, 11, 3, 1)
    m.stamp(crates, 2, 11, 1, 1)
    m.stamp(plant, 2, 5, 1, 1)

    # Leave through the door mat
    m.warp(7, 13, 2, 1, "city_centre", 14 * MT + 8, 13 * MT + 6, "down")
    return m


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def count_tiles(cv):
    tiles = set()
    for ty in range(0, cv.h, 8):
        for tx in range(0, cv.w, 8):
            tiles.add(tuple(tuple(cv.p[ty + y][tx:tx + 8]) for y in range(8)))
    return len(tiles)


def emit_maps(maps, preview_dir=None):
    names = [m.ident for m in maps]
    out = []
    out.append("// Generated by tools/gen_graphics.py - do not edit by hand.")
    out.append("// Include this file from exactly one .cpp (tl_world.cpp).")
    out.append("#ifndef TL_WORLD_DATA_H")
    out.append("#define TL_WORLD_DATA_H")
    out.append("")
    out.append('#include "tl_world.h"')
    for m in maps:
        out.append(f'#include "bn_regular_bg_items_{m.ident}.h"')
    out.append("")
    out.append("namespace tl::world_data")
    out.append("{")

    for m in maps:
        cv, solid = m.render()
        tiles = count_tiles(cv)
        print(f"{m.ident}: {m.w * MT}x{m.h * MT} px, {tiles} unique 8x8 tiles")
        assert tiles <= 800, f"{m.ident}: too many unique tiles ({tiles})"
        bg_palette = [rgb for _, rgb in BG_COLOURS]
        bg_palette += [(0, 0, 0)] * ((-len(bg_palette)) % 16)
        _write_bmp(os.path.join(ROOT, "graphics", m.ident + ".bmp"), cv.p, cv.w, cv.h, 8, bg_palette)
        write_text(os.path.join(ROOT, "graphics", m.ident + ".json"),
                   '{\n    "type": "regular_bg",\n    "bpp_mode": "bpp_8"\n}\n')
        if preview_dir:
            from PIL import Image
            img = Image.new("RGB", (cv.w, cv.h))
            img.putdata([BG_COLOURS[i][1] for row in cv.p for i in row])
            img.save(os.path.join(preview_dir, m.ident + ".png"))

        out.append(f"    // ---- {m.display_name} ----")
        out.append(f"    constexpr uint8_t {m.ident}_solid[{m.w * m.h}] = {{")
        for my in range(m.h):
            row = ",".join("1" if solid[my][mx] else "0" for mx in range(m.w))
            out.append(f"        {row},  // {''.join(m.grid[my])}")
        out.append("    };")
        out.append("")
        out.append(f"    constexpr warp {m.ident}_warps[] = {{")
        for (mx, my, w, h, target, tx, ty, facing) in m.warps:
            assert target in names, target
            txs = "keep_coordinate" if tx is None else str(tx)
            tys = "keep_coordinate" if ty is None else str(ty)
            fs = f"direction::{facing}" if facing else "direction::down"
            out.append(f"        {{ {mx * MT}, {my * MT}, {w * MT}, {h * MT}, map_id::{target}, {txs}, {tys}, {fs} }},")
        out.append("    };")
        out.append("")

    out.append("    constexpr map_info maps[] = {")
    for m in maps:
        out.append(f'        {{ "{m.display_name}", &bn::regular_bg_items::{m.ident}, {m.w}, {m.h}, '
                   f'{m.ident}_solid, {m.ident}_warps, int(sizeof({m.ident}_warps) / sizeof(warp)) }},')
    out.append("    };")
    out.append("}")
    out.append("")
    out.append("#endif")
    out.append("")
    write_text(os.path.join(ROOT, "include", "tl_world_data.h"), "\n".join(out))

    # map ids header
    ids = ["// Generated by tools/gen_graphics.py - do not edit by hand.",
           "#ifndef TL_MAP_ID_H", "#define TL_MAP_ID_H", "", "namespace tl", "{",
           "    enum class map_id", "    {"]
    for n in names:
        ids.append(f"        {n},")
    ids += ["    };", "", f"    constexpr int maps_count = {len(names)};", "}", "", "#endif", ""]
    write_text(os.path.join(ROOT, "include", "tl_map_id.h"), "\n".join(ids))


# ---------------------------------------------------------------------------
# Player sprite sheet: 9 frames of 16x16, stacked vertically.
#   0-2 down (stand, step A, step B), 3-5 up, 6-8 side (facing right)
# ---------------------------------------------------------------------------
CHARS = {".": 0, "h": 8, "s": 12, "e": 10, "b": 13, "p": 3, "k": 10, "w": 11}
HEAD_DOWN = ["................", ".....hhhhhh.....", "....hhhhhhhh....", "....hhhhhhhh....",
             "....hssssssh....", "....sessssess...", "....ssssssss....", ".....ssssss....."]
HEAD_UP = ["................", ".....hhhhhh.....", "....hhhhhhhh....", "....hhhhhhhh....",
           "....hhhhhhhh....", "....hhhhhhhh....", "....shhhhhhs....", ".....ssssss....."]
HEAD_SIDE = ["................", ".....hhhhhh.....", "....hhhhhhhh....", "....hhhhhhhh....",
             "....hhhsssss....", "....hhsssses....", "....hsssssss....", ".....ssssss....."]
BODY_FRONT = ["....bbbbbbbb....", "...bbbbbbbbbb...", "...sbbbbbbbbs...", "...sbbbbbbbbs..."]
BODY_SIDE = [".....bbbbbb.....", ".....bbbbbb.....", ".....bbsbbb.....", ".....bbsbbb....."]
LEGS_FRONT = [
    ["....pppppppp....", "....ppp..ppp....", "....ppp..ppp....", "....kkk..kkk...."],
    ["....pppppppp....", "....ppp..ppp....", "....kkk..ppp....", ".........kkk...."],
    ["....pppppppp....", "....ppp..ppp....", "....ppp..kkk....", "....kkk........."],
]
LEGS_SIDE = [
    [".....pppppp.....", "......pppp......", "......pppp......", "......kkkkk....."],
    [".....pppppp.....", ".....pp..pp.....", "....pp....pp....", "...kk......kk..."],
    [".....pppppp.....", "......pppp......", ".....pp.pp......", ".....kk.kkk....."],
]


def generate_player():
    frames = [HEAD_DOWN + BODY_FRONT + l for l in LEGS_FRONT]
    frames += [HEAD_UP + BODY_FRONT + l for l in LEGS_FRONT]
    frames += [HEAD_SIDE + BODY_SIDE + l for l in LEGS_SIDE]
    pixels = []
    for f in frames:
        assert len(f) == 16
        for row in f:
            assert len(row) == 16, row
            pixels.append([CHARS[c] for c in row])
    _write_bmp(os.path.join(ROOT, "graphics", "player.bmp"), pixels, 16, 16 * len(frames), 4, SPRITE_PALETTE)
    write_text(os.path.join(ROOT, "graphics", "player.json"), '{\n    "type": "sprite",\n    "height": 16\n}\n')


if __name__ == "__main__":
    preview = None
    if len(sys.argv) >= 3 and sys.argv[1] == "--preview":
        preview = sys.argv[2]
        os.makedirs(preview, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "graphics"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "include"), exist_ok=True)
    emit_maps([build_city_centre(), build_old_block(), build_corner_market()], preview)
    generate_player()
