#!/usr/bin/env python3
"""
Town Life - isometric map + sprite generator (pure Python 3, Pillow only for --preview).

Generates (all committed, CI does not run this script):
  graphics/<map>_floor.bmp/.json    8bpp regular BG: ground (below the player)
  graphics/<map>_objects.bmp/.json  8bpp regular BG: buildings, trees... (above or below the player)
  graphics/hud.bmp/.json            8bpp regular BG: HUD bar at the bottom of the screen
  graphics/player.bmp/.json         4bpp sprite sheet, 6 frames of 16x32
  include/tl_map_id.h               enum map_id
  include/tl_world_data.h           per-map collision, warps, occluders and the map table

Usage:  python3 tools/gen_iso.py [--preview DIR]

Projection (2:1 isometric)
--------------------------
World units: 1 unit = 1 screen pixel horizontally, 1 cell = 16 units.
  +x (world) goes down-right on screen, +y goes down-left.
  screen_x = origin_x + x - y
  screen_y = origin_y + (x + y) / 2 - z        (z = height in pixels)
Boxes (buildings, shelves...) show three faces: the "left" face (plane y = y1, facing down-left),
the "right" face (plane x = x1, facing down-right) and the top.

All BGs share one 8bpp palette that is built automatically from the RGB colours used.
"""

import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELL = 16


# ---------------------------------------------------------------------------
# Colours: painters return RGB tuples; the palette is collected automatically.
# ---------------------------------------------------------------------------
def q(c):
    """Quantize to GBA 15-bit colour (keeps the palette small and exact)."""
    return tuple(max(0, min(255, int(round(v)))) & 0xF8 for v in c)


def shade(c, f):
    return q((c[0] * f, c[1] * f, c[2] * f))


def mix(a, b, t):
    return q(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


class Palette:
    def __init__(self):
        self.colours = [(0, 0, 0)]       # index 0 = transparent / black backdrop
        self.index = {}

    def get(self, rgb):
        rgb = q(rgb)
        if rgb not in self.index:
            self.index[rgb] = len(self.colours)
            self.colours.append(rgb)
            assert len(self.colours) <= 256, "too many colours"
        return self.index[rgb]


PAL = Palette()

# Named base colours
OUTLINE = (40, 32, 40)
WHITE = (240, 240, 232)
BLACK = (0, 0, 0)

ASPHALT = (88, 88, 100)
ASPHALT_D = (72, 72, 84)
ASPHALT_L = (104, 104, 116)
LINE_Y = (232, 192, 64)
PAVE = (184, 104, 80)          # brick paving
PAVE_D = (144, 80, 64)
PAVE_L = (208, 136, 104)
CURB = (176, 176, 168)
CURB_D = (136, 136, 128)
GRASS = (96, 168, 72)
GRASS_D = (72, 136, 56)
GRASS_L = (136, 200, 96)

BRICK = (176, 72, 56)
BRICK_D = (136, 56, 48)
BRICK_B = (128, 80, 56)
BRICK_BD = (96, 64, 48)
MORTAR = (200, 168, 144)
CREAM = (232, 216, 176)
MINT = (168, 216, 192)
STONE = (192, 184, 168)
GLASS = (104, 160, 208)
GLASS_L = (168, 208, 240)
GLASS_D = (64, 104, 152)
GREEN = (48, 136, 88)
GREEN_D = (32, 96, 64)
WOOD = (168, 112, 64)
WOOD_D = (120, 72, 40)
WOOD_L = (208, 152, 96)
ROOF = (120, 120, 128)
ROOF_D = (96, 96, 104)
GOLD = (240, 200, 72)
RED = (208, 56, 56)
BLUE = (64, 104, 176)
LEAF = (64, 140, 64)
LEAF_D = (40, 100, 48)
LEAF_DD = (24, 72, 40)
LEAF_L = (112, 184, 80)
TRUNK = (112, 72, 40)

FLOOR_W = (208, 152, 96)
FLOOR_WD = (176, 120, 72)
FLOOR_WL = (224, 176, 120)
IWALL = (240, 224, 184)
IWALL_D = (208, 188, 148)

GOODS = [(224, 64, 64), (240, 192, 64), (96, 176, 80), (240, 136, 48), (80, 128, 208), (232, 120, 176),
         (240, 240, 232)]


# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.p = [[0] * w for _ in range(h)]

    def set(self, x, y, rgb):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = 0 if rgb is None else PAL.get(rgb)

    def get_rgb(self, x, y):
        return PAL.colours[self.p[y][x]]

    def rect(self, x, y, w, h, rgb):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                self.set(xx, yy, rgb)

    def disc(self, cx, cy, r, rgb, ry=None):
        ry = r if ry is None else ry
        for yy in range(int(cy - ry - 1), int(cy + ry + 2)):
            for xx in range(int(cx - r - 1), int(cx + r + 2)):
                if ((xx + 0.5 - cx) / r) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1:
                    self.set(xx, yy, rgb)


# 3x5 font for signs
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
K #.# #.# ##. #.# #.#
L #.. #.. #.. #.. ###
M #.# ### ### #.# #.#
N ##. #.# #.# #.# #.#
O .#. #.# #.# #.# .#.
P ##. #.# ##. #.. #..
R ##. #.# ##. #.# #.#
S .## #.. .#. ..# ##.
T ### .#. .#. .#. .#.
U #.# #.# #.# #.# ###
V #.# #.# #.# #.# .#.
Y #.# #.# .#. .#. .#.
"""
FONT = {}
for _line in _GLYPHS.strip().splitlines():
    _parts = _line.split()
    FONT[_parts[0]] = "".join(_parts[1:])


def glyph_on(ch, gx, gy):
    g = FONT.get(ch)
    return g is not None and 0 <= gx < 3 and 0 <= gy < 5 and g[gy * 3 + gx] == "#"


def text_at(s, u, v, u0, v_top):
    """Text painted on a face: returns True if face pixel (u, v) is part of the text.
    Each glyph stays upright; the face shear naturally slants the baseline."""
    col = int(u - u0)
    row = int(v_top - v)
    if col < 0 or row < 0 or row >= 5:
        return False
    x = 0
    for ch in s:
        w = 2 if ch == " " else 4
        if col < x + w:
            return ch != " " and glyph_on(ch, col - x, row)
        x += w
    return False


def text_len(s):
    return sum(2 if ch == " " else 4 for ch in s) - 1


# ---------------------------------------------------------------------------
# Iso map
# ---------------------------------------------------------------------------
class IsoMap:
    def __init__(self, ident, name, w, h, bg_w, bg_h, origin_x, origin_y, floor_fn):
        self.ident, self.name = ident, name
        self.w, self.h = w, h                    # cells
        self.bg_w, self.bg_h = bg_w, bg_h
        self.ox, self.oy = origin_x, origin_y
        self.floor_fn = floor_fn                 # f(map, cx, cy, u, v) -> rgb
        self.grid = [["."] * w for _ in range(h)]
        self.solid = [[False] * w for _ in range(h)]
        self.objects = []                        # (depth, draw_fn)
        self.occluders = []                      # (x0, y0, x1, y1, sx0, sy0, sx1, sy1)
        self.warps = []

    def proj(self, x, y, z=0):
        return self.ox + x - y, self.oy + (x + y) / 2 - z

    def fill(self, cx, cy, w, h, ch):
        for y in range(cy, cy + h):
            for x in range(cx, cx + w):
                self.grid[y][x] = ch

    def at(self, cx, cy):
        if 0 <= cx < self.w and 0 <= cy < self.h:
            return self.grid[cy][cx]
        return None

    def set_solid(self, cx, cy, w=1, h=1, value=True):
        for y in range(cy, cy + h):
            for x in range(cx, cx + w):
                if 0 <= x < self.w and 0 <= y < self.h:
                    self.solid[y][x] = value

    # -- objects --------------------------------------------------------------
    def box(self, x0, y0, x1, y1, h, painter, solid=True, occlude=True, walkable=()):
        """Axis-aligned box in WORLD UNITS. painter(face, u, v, L, H) -> rgb or None."""
        def draw(cv):
            render_box(self, cv, x0, y0, x1, y1, h, painter)
        self.objects.append(((x0 + x1 + y0 + y1) / 2, draw))
        if solid:
            for cy in range(int(y0 // CELL), int((y1 - 1) // CELL) + 1):
                for cx in range(int(x0 // CELL), int((x1 - 1) // CELL) + 1):
                    if (cx, cy) not in walkable:
                        self.set_solid(cx, cy)
        if occlude:
            sx0, _ = self.proj(x0, y1)
            sx1, _ = self.proj(x1, y0)
            _, sy0 = self.proj(x0, y0, h)
            _, sy1 = self.proj(x1, y1)
            self.occluders.append((x0, y0, x1, y1, int(sx0), int(sy0), int(sx1), int(sy1)))

    def decoration(self, cx, cy, draw_fn, solid=True, occlude=True, height=48, half_width=16):
        """Screen-space drawing anchored at the centre of a cell (on the ground)."""
        bx, by = self.proj(cx * CELL + 8, cy * CELL + 8)

        def draw(cv):
            draw_fn(cv, bx, by)
        self.objects.append(((cx * CELL + 8) + (cy * CELL + 8) + 0.1, draw))
        if solid:
            self.set_solid(cx, cy)
        if occlude:
            self.occluders.append((cx * CELL, cy * CELL, cx * CELL + CELL, cy * CELL + CELL,
                                   int(bx - half_width), int(by - height), int(bx + half_width), int(by + 4)))

    def warp(self, cx, cy, w, h, target, tx, ty, facing):
        """Trigger rect in cells; target position in world units."""
        self.warps.append((cx * CELL, cy * CELL, w * CELL, h * CELL, target, tx, ty, facing))

    # -- rendering ------------------------------------------------------------
    def render(self):
        floor = Canvas(self.bg_w, self.bg_h)
        for py in range(self.bg_h):
            for px in range(self.bg_w):
                a = px + 0.5 - self.ox
                b = py + 0.5 - self.oy
                wx = b + a / 2
                wy = b - a / 2
                if 0 <= wx < self.w * CELL and 0 <= wy < self.h * CELL:
                    cx, cy = int(wx // CELL), int(wy // CELL)
                    floor.set(px, py, self.floor_fn(self, cx, cy, wx - cx * CELL, wy - cy * CELL))
        objects = Canvas(self.bg_w, self.bg_h)
        for _, draw in sorted(self.objects, key=lambda o: o[0]):
            draw(objects)
        return floor, objects

    def view_bounds(self):
        xs, ys = [], []
        for (x, y) in ((0, 0), (self.w * CELL, 0), (0, self.h * CELL), (self.w * CELL, self.h * CELL)):
            sx, sy = self.proj(x, y)
            xs.append(sx)
            ys.append(sy)
        top = min(ys) - 80
        return int(min(xs)), int(max(0, top)), int(max(xs)), int(max(ys))


def render_box(m, cv, x0, y0, x1, y1, h, painter):
    sxa, _ = m.proj(x0, y1)
    sxb, _ = m.proj(x1, y0)
    _, sya = m.proj(x0, y0, h)
    _, syb = m.proj(x1, y1)
    L_len, R_len = x1 - x0, y1 - y0
    for py in range(int(sya) - 1, int(syb) + 2):
        for px in range(int(sxa) - 1, int(sxb) + 2):
            a = px + 0.5 - m.ox
            b = py + 0.5 - m.oy
            # top face (z = h)
            tb = b + h
            tx, ty = tb + a / 2, tb - a / 2
            if x0 <= tx < x1 and y0 <= ty < y1:
                c = painter("top", tx - x0, ty - y0, L_len, R_len)
                if c is not None:
                    cv.set(px, py, shade(c, 1.12))
                continue
            # left face (y = y1)
            wx = a + y1
            z = (wx + y1) / 2 - b
            if x0 <= wx < x1 and 0 <= z < h:
                c = painter("left", wx - x0, z, L_len, h)
                if c is not None:
                    cv.set(px, py, c)
                continue
            # right face (x = x1)
            wy = x1 - a
            z = (x1 + wy) / 2 - b
            if y0 <= wy < y1 and 0 <= z < h:
                c = painter("right", wy - y0, z, R_len, h)
                if c is not None:
                    cv.set(px, py, shade(c, 0.78))


# ---------------------------------------------------------------------------
# Floor painters  f(map, cx, cy, u, v) -> rgb      (u along x, v along y; 0..16)
# ---------------------------------------------------------------------------
def floor_street(m, cx, cy, u, v):
    t = m.at(cx, cy)
    if t == "s":   # brick paving (herringbone-ish rows)
        row = int(v // 4)
        off = 4 if row % 2 else 0
        if v % 4 < 1 or (u + off) % 8 < 1:
            c = PAVE_D
        elif (u + off) % 8 < 2 and v % 4 < 2:
            c = PAVE_L
        else:
            c = PAVE
        # curb along roads
        for (dx, dy, uu) in ((0, 1, 16 - v), (1, 0, 16 - u), (0, -1, v), (-1, 0, u)):
            if m.at(cx + dx, cy + dy) in ("r", "h", "v", "z", "Z", "x") and uu < 2.5:
                return CURB if uu > 1 else CURB_D
        return c
    if t in ("r", "h", "v", "z", "Z", "x"):
        c = ASPHALT
        if (int(u) * 7 + int(v) * 13) % 23 == 0:
            c = ASPHALT_L
        elif (int(u) * 5 + int(v) * 3) % 19 == 0:
            c = ASPHALT_D
        if t == "h" and 7 <= v < 9 and 3 <= u < 13:
            c = LINE_Y
        if t == "v" and 7 <= u < 9 and 3 <= v < 13:
            c = LINE_Y
        if t == "Z" and 2 <= v < 14 and int(u) % 6 < 3:     # crossing a road along x
            c = WHITE
        if t == "z" and 2 <= u < 14 and int(v) % 6 < 3:     # crossing a road along y
            c = WHITE
        return c
    if t == "g":
        if (int(u) * 3 + int(v) * 7) % 11 == 0:
            return GRASS_D
        if (int(u) * 5 + int(v) * 11) % 17 == 0:
            return GRASS_L
        return GRASS
    if t == "c":  # checkered entrance tiles
        d = (int(u) // 4 + int(v) // 4) % 2
        return (232, 232, 224) if d else (88, 96, 136)
    return BLACK


def floor_interior(m, cx, cy, u, v):
    t = m.at(cx, cy)
    if t == "m":
        if 2 <= u < 14 and 2 <= v < 14:
            return RED if (int(u) + int(v)) % 2 else (168, 40, 40)
    # wooden planks running along x
    plank = int(v // 4)
    off = (plank * 7) % 16
    if v % 4 < 1 or (u + off) % 16 < 1:
        return FLOOR_WD
    if v % 4 < 2:
        return FLOOR_WL
    return FLOOR_W


# ---------------------------------------------------------------------------
# Face painters
# ---------------------------------------------------------------------------
def brick(u, v, c=BRICK, cd=BRICK_D):
    row = int(v // 4)
    off = 4 if row % 2 else 0
    if v % 4 < 1 or (u + off) % 8 < 1:
        return MORTAR
    return cd if (int((u + off) // 8) + row) % 4 == 0 else c


def roof_top(u, v, L, R):
    if u < 2 or v < 2 or u > L - 2 or v > R - 2:
        return STONE
    return ROOF if (int(u) + int(v) * 3) % 7 else ROOF_D


def window_pane(u, v, u0, v0, w, h, frame=WHITE, lit=False):
    if not (u0 <= u < u0 + w and v0 <= v < v0 + h):
        return None
    if u < u0 + 1 or u >= u0 + w - 1 or v < v0 + 1 or v >= v0 + h - 1:
        return frame
    if abs(u - (u0 + w / 2)) < 0.5:
        return frame
    if lit:
        return (248, 216, 112)
    return GLASS_L if (v > v0 + h - 4 and u < u0 + 4) else GLASS


def corner_market_painter(face, u, v, L, H):
    if face == "top":
        return roof_top(u, v, L, H)
    if v >= H - 3:
        return GREEN_D if v >= H - 1 else GREEN
    ground = 30
    if face == "left":
        # sign band
        if ground + 3 <= v < ground + 13 and 8 <= u < L - 8:
            if text_at("CORNER MARKET", u, v, 12, ground + 10):
                return WHITE
            return GREEN if 9 <= u < L - 9 and ground + 4 <= v < ground + 12 else GREEN_D
        # upper floor windows
        if v > ground + 14:
            for wu in range(10, int(L) - 10, 18):
                c = window_pane(u, v, wu, ground + 16, 9, 10, lit=(wu // 18) % 2 == 0)
                if c:
                    return c
            return brick(u, v)
        # awning (green / white stripes) with shadow below
        if ground - 7 <= v < ground:
            return GREEN if int(u // 4) % 2 == 0 else WHITE
        if ground - 9 <= v < ground - 7:
            return GREEN_D if int(u) % 4 < 2 else shade(BRICK_D, 0.7)
        # door (cell 2 of 5) and shop windows
        door_u0 = 2 * CELL + 2
        if door_u0 <= u < door_u0 + 12 and v < 20:
            if u < door_u0 + 1 or u >= door_u0 + 11 or v >= 19:
                return WOOD_D
            if 4 <= v < 16 and door_u0 + 3 <= u < door_u0 + 9:
                return GLASS_L if v > 12 else GLASS
            if abs(u - (door_u0 + 9)) < 1 and 8 <= v < 10:
                return GOLD
            return WOOD
        for (wu0, wu1) in ((3, door_u0 - 3), (door_u0 + 15, L - 3)):
            if wu0 <= u < wu1 and 4 <= v < 19:
                if u < wu0 + 1 or u >= wu1 - 1 or v < 5 or v >= 18:
                    return WOOD_D
                if int(v) in (9, 13):
                    return WOOD
                if v < 9 or 10 <= v < 13:
                    return GOODS[int(u // 3) % len(GOODS)] if int(u) % 3 != 2 else GLASS_L
                return GLASS
        if v < 4:
            return WOOD_D if v < 1 else STONE
        return brick(u, v)
    # right face: plain brick with windows
    if v > ground + 14:
        c = window_pane(u, v, 12, ground + 16, 9, 10)
        if c:
            return c
    return brick(u, v)


def apartment_painter(base=BRICK_B, base_d=BRICK_BD, door_u=24, lit=()):
    def painter(face, u, v, L, H):
        if face == "top":
            return roof_top(u, v, L, H)
        if v >= H - 3:
            return STONE
        if face == "left":
            if door_u <= u < door_u + 11 and v < 20:
                if u < door_u + 1 or u >= door_u + 10 or v >= 19:
                    return OUTLINE
                return BLUE if not (3 <= v < 15 and door_u + 3 <= u < door_u + 8) else GLASS
            for fl, v0 in enumerate((26, 46)):
                for i, wu in enumerate(range(6, int(L) - 8, 16)):
                    c = window_pane(u, v, wu, v0, 8, 12, lit=(fl * 10 + i) in lit)
                    if c:
                        return c
                    if wu - 1 <= u < wu + 9 and v0 - 2 <= v < v0:
                        return STONE        # sill
        else:
            for v0 in (26, 46):
                for wu in range(6, int(L) - 8, 16):
                    c = window_pane(u, v, wu, v0, 8, 12)
                    if c:
                        return c
        if v < 3:
            return STONE
        return brick(u, v, base, base_d)
    return painter


def office_painter(face, u, v, L, H):
    if face == "top":
        return roof_top(u, v, L, H)
    if v >= H - 3:
        return (176, 184, 192)
    # glass curtain wall with grey frames
    if int(u) % 12 < 2 or int(v) % 14 < 2:
        return (160, 168, 176)
    return GLASS_L if (int(v) % 14 > 10 and int(u) % 12 < 5) else GLASS_D if face == "right" else GLASS


def townhouse_painter(base, trim, door_u, door_colour):
    def painter(face, u, v, L, H):
        if face == "top":
            return roof_top(u, v, L, H)
        if v >= H - 4:
            return trim
        if face == "right":   # front of the townhouses (faces down-right)
            if door_u <= u < door_u + 11 and v < 20:
                if u < door_u + 1 or u >= door_u + 10 or v >= 19:
                    return OUTLINE
                return door_colour if not (4 <= v < 14 and door_u + 3 <= u < door_u + 8) else GLASS
            for v0 in (8, 30):
                for wu in range(4, int(L) - 6, 14):
                    if v0 == 8 and abs(wu - door_u) < 12:
                        continue
                    c = window_pane(u, v, wu, v0, 8, 12, frame=trim)
                    if c:
                        return c
        if v < 3:
            return trim
        return base if int(v) % 6 else shade(base, 0.92)
    return painter


def wall_painter(face, u, v, L, H):
    # interior wall: light plaster above wooden wainscot
    if face == "top":
        return WOOD_D
    if v < 14:
        if v < 1 or v >= 13:
            return WOOD_D
        return WOOD if int(u) % 6 else WOOD_D
    if v >= H - 2:
        return WOOD_D
    return IWALL if int(v) % 12 else IWALL_D


def shelf_painter(face, u, v, L, H):
    if face == "top":
        return WOOD_L
    if u < 1 or u >= L - 1 or v < 2:
        return WOOD_D
    if int(v) % 8 == 0:
        return WOOD
    if int(v) % 8 >= 6:
        return WOOD_D
    return GOODS[(int(u // 3) + int(v // 8) * 2) % len(GOODS)] if int(u) % 3 != 2 else WOOD_D


def fridge_painter(face, u, v, L, H):
    if face == "top":
        return (208, 212, 216)
    if u < 1 or u >= L - 1 or v < 2 or v >= H - 2:
        return (176, 180, 188)
    if face == "left" and 4 <= v < H - 6:
        if int(u) % 12 < 1:
            return (176, 180, 188)
        if int(v) % 8 in (2, 3, 4) and int(u) % 3 != 2:
            return GOODS[(int(u // 3) + int(v // 8)) % len(GOODS)]
        return GLASS_L
    return (216, 220, 224)


def counter_painter(face, u, v, L, H):
    if face == "top":
        return WOOD_L if (int(u) + int(v)) % 9 else WOOD
    if v >= H - 2:
        return WOOD_L
    if v < 2:
        return WOOD_D
    return WOOD if int(u) % 8 else WOOD_D


def bench_painter(face, u, v, L, H):
    if face == "top":
        return WOOD_L if int(v) % 3 else WOOD_D
    return WOOD_D if v < 3 else WOOD


def pot_painter(face, u, v, L, H):
    if face == "top":
        return (96, 64, 40)
    return (176, 96, 64) if v > 1 else (128, 64, 48)


# ---------------------------------------------------------------------------
# Screen-space decorations: fn(cv, bx, by) where (bx, by) = ground point
# ---------------------------------------------------------------------------
def tree(cv, bx, by):
    cv.disc(bx, by - 1, 9, (56, 112, 48), ry=4)              # ground shadow-ish
    cv.rect(bx - 2, by - 22, 4, 22, TRUNK)
    cv.rect(bx - 2, by - 22, 1, 22, (144, 96, 56))
    clusters = [(-7, -30, 9), (7, -30, 9), (0, -38, 10), (-4, -24, 8), (5, -24, 8), (0, -30, 9)]
    for (dx, dy, r) in clusters:
        cv.disc(bx + dx, by + dy, r + 1, LEAF_DD)
    for (dx, dy, r) in clusters:
        cv.disc(bx + dx, by + dy, r, LEAF_D)
    for (dx, dy, r) in clusters:
        cv.disc(bx + dx - 2, by + dy - 2, r - 3, LEAF)
    for (dx, dy, r) in clusters:
        cv.disc(bx + dx - 3, by + dy - 4, max(1, r - 7), LEAF_L)


def lamp(cv, bx, by):
    cv.disc(bx, by, 3, (64, 64, 72), ry=1.5)
    cv.rect(bx - 1, by - 40, 2, 40, (56, 56, 72))
    cv.rect(bx, by - 40, 1, 40, (96, 96, 112))
    cv.rect(bx - 4, by - 46, 8, 6, (56, 56, 72))
    cv.rect(bx - 3, by - 45, 6, 4, (248, 232, 160))
    cv.rect(bx - 2, by - 48, 4, 2, (56, 56, 72))


def plant(cv, bx, by):
    leaves = [(-5, -14), (5, -14), (0, -20), (-3, -10), (4, -9), (0, -15)]
    for (dx, dy) in leaves:
        cv.disc(bx + dx, by + dy, 5, LEAF_D, ry=3)
    for (dx, dy) in leaves:
        cv.disc(bx + dx - 1, by + dy - 1, 3, LEAF_L if dy < -14 else LEAF, ry=2)


def hydrant(cv, bx, by):
    cv.rect(bx - 3, by - 10, 6, 10, RED)
    cv.rect(bx - 3, by - 10, 2, 10, (232, 96, 96))
    cv.rect(bx - 4, by - 12, 8, 2, (168, 40, 40))
    cv.rect(bx - 5, by - 7, 10, 2, (168, 40, 40))


# ---------------------------------------------------------------------------
# District 1 prototype: street corner at Corner Market
# ---------------------------------------------------------------------------
def build_street():
    W, H = 14, 10
    m = IsoMap("city_centre", "City Centre", W, H, 512, 512, H * CELL + 16, 96, floor_street)

    m.fill(0, 0, W, H, "s")
    # roads: along x (gy 5..7) and along y (gx 5..7)
    m.fill(5, 5, W - 5, 3, "r")
    m.fill(5, 6, W - 5, 1, "h")
    m.fill(5, 5, 3, H - 5, "r")
    m.fill(6, 8, 1, H - 8, "v")
    m.fill(5, 5, 3, 3, "x")
    m.fill(9, 5, 1, 3, "Z")
    m.fill(5, 8, 3, 1, "z")
    # grass strip in the front corner
    m.fill(9, 9, W - 9, 1, "g")
    # checkered tiles in front of the shop door
    m.fill(6, 3, 1, 1, "c")

    # buildings along the back
    m.box(4 * CELL, 0, 9 * CELL, 3 * CELL, 56, corner_market_painter, walkable=((6, 2),))
    m.box(9 * CELL, 0, 14 * CELL, 3 * CELL, 64, apartment_painter(lit=(1, 12)))
    m.box(0, 0, 4 * CELL, 4 * CELL, 76, office_painter)
    m.box(0, 4 * CELL, 3 * CELL, 7 * CELL, 48, townhouse_painter(CREAM, (240, 240, 232), 18, (176, 48, 48)))
    m.box(0, 7 * CELL, 3 * CELL, 10 * CELL, 52, townhouse_painter(MINT, (240, 240, 232), 18, BLUE))

    # Corner Market door -> interior
    m.warp(6, 2, 1, 1, "corner_market", 3 * CELL + 8, 4 * CELL + 6, "up")

    # street furniture
    m.decoration(4, 3, plant, height=24, half_width=10)
    m.box(4 * CELL + 4, 3 * CELL + 4, 4 * CELL + 12, 3 * CELL + 12, 6, pot_painter, solid=False, occlude=False)
    m.decoration(8, 3, plant, height=24, half_width=10)
    m.box(8 * CELL + 4, 3 * CELL + 4, 8 * CELL + 12, 3 * CELL + 12, 6, pot_painter, solid=False, occlude=False)
    m.decoration(13, 4, hydrant, height=14, half_width=6)
    m.decoration(4, 4, lamp, height=50, half_width=6)
    m.decoration(8, 8, lamp, height=50, half_width=6)
    m.decoration(10, 9, tree, height=50, half_width=16)
    m.decoration(13, 9, tree, height=50, half_width=16)
    m.box(11 * CELL + 2, 8 * CELL + 5, 12 * CELL + 14, 8 * CELL + 11, 7, bench_painter, occlude=False)
    m.set_solid(11, 8)
    m.set_solid(12, 8)
    m.decoration(3, 8, tree, height=50, half_width=16)
    m.decoration(4, 9, plant, height=24, half_width=10, solid=True)
    return m


def build_corner_market():
    W, H = 8, 6
    m = IsoMap("corner_market", "Corner Market", W, H, 256, 256, H * CELL + 24, 72, floor_interior)
    m.fill(0, 0, W, H, "w")
    m.fill(3, 5, 1, 1, "m")
    # back walls (thin boxes behind the room)
    m.box(-4, 0, 0, H * CELL, 56, wall_painter, solid=False, occlude=False)
    m.box(-4, -4, W * CELL, 0, 56, wall_painter, solid=False, occlude=False)
    # furniture
    m.box(1 * CELL, 0, 5 * CELL, 1 * CELL - 4, 34, shelf_painter)
    m.box(5 * CELL + 4, 0, 8 * CELL, 1 * CELL - 2, 40, fridge_painter)
    m.box(1 * CELL + 4, 2 * CELL + 4, 4 * CELL + 12, 3 * CELL - 2, 22, shelf_painter)
    m.box(5 * CELL, 4 * CELL, 7 * CELL, 5 * CELL - 2, 16, counter_painter)
    m.decoration(0, 4, plant, height=24, half_width=10)
    m.box(0 * CELL + 4, 4 * CELL + 4, 0 * CELL + 12, 4 * CELL + 12, 6, pot_painter, solid=False, occlude=False)
    # leave through the door mat
    m.warp(3, 5, 1, 1, "city_centre", 6 * CELL + 8, 3 * CELL + 10, "down")
    return m


# ---------------------------------------------------------------------------
# HUD (bottom bar, 32 px). BG is 256x256; visible screen area = bg x 8..247, y 48..207.
# ---------------------------------------------------------------------------
ICONS = {
    "hunger": [
        "................",
        "..#.#.#.....##..",
        "..#.#.#....###..",
        "..#.#.#....###..",
        "..#####....###..",
        "...###.....###..",
        "....#......###..",
        "....#.......#...",
        "....#.......#...",
        "....#.......#...",
        "....#.......#...",
        "....#.......#...",
        "....#.......#...",
        "....#.......#...",
        "................",
        "................",
    ],
    "energy": [
        "................",
        ".........###....",
        "........##......",
        ".......##.......",
        "......###.......",
        "......###.......",
        "......###.......",
        ".......###......",
        "........####..#.",
        ".........######.",
        "...........##...",
        "................",
        "...######.......",
        "...#............",
        "...######.......",
        "................",
    ],
    "hygiene": [
        "................",
        ".......#........",
        ".......#........",
        "......###.......",
        "......###.......",
        ".....#####......",
        ".....#####......",
        "....#######.....",
        "....###.###.....",
        "....##.####.....",
        "....###.###.....",
        ".....#####......",
        "......###.......",
        "................",
        "................",
        "................",
    ],
    "fun": [
        "................",
        ".......#........",
        ".......#........",
        "......###.......",
        "......###.......",
        ".##############.",
        "..############..",
        "....########....",
        ".....######.....",
        "....###..###....",
        "....##....##....",
        "...##......##...",
        "................",
        "................",
        "................",
        "................",
    ],
}


def build_hud():
    cv = Canvas(256, 256)
    top = 176
    panel = (40, 48, 88)
    panel_l = (72, 84, 136)
    panel_d = (24, 28, 56)
    cv.rect(8, top, 240, 32, panel_d)
    # clock / money panel
    cv.rect(10, top + 2, 66, 28, panel)
    cv.rect(10, top + 2, 66, 1, panel_l)
    cv.rect(14, top + 15, 58, 1, panel_l)
    # need slots
    names = ["hunger", "energy", "hygiene", "fun"]
    for i, n in enumerate(names):
        x = 80 + i * 42
        cv.rect(x, top + 2, 40, 28, panel)
        cv.rect(x, top + 2, 40, 1, panel_l)
        for yy, row in enumerate(ICONS[n]):
            for xx, ch in enumerate(row):
                if ch == "#":
                    cv.set(x + 12 + xx + 1, top + 3 + yy + 1, panel_d)
                    cv.set(x + 12 + xx, top + 3 + yy, WHITE)
        # bar background (bar fill is drawn by sprites/updates later; mock fill for now)
        cv.rect(x + 4, top + 22, 32, 5, (16, 16, 24))
        fill = (26, 18, 22, 28)[i]
        cv.rect(x + 5, top + 23, fill, 3, (88, 200, 88) if fill > 16 else (232, 160, 48))
        cv.rect(x + 5 + fill, top + 23, 30 - fill, 3, (168, 48, 48))
    return cv


# ---------------------------------------------------------------------------
# Player sprite: 16x32, frames 0-2 front (facing down-left), 3-5 back (facing up-left)
# ---------------------------------------------------------------------------
SPRITE_PAL = [
    (255, 0, 255), (32, 24, 32), (240, 196, 160), (200, 144, 112), (88, 56, 40), (144, 96, 56),
    (56, 88, 152), (32, 56, 104), (96, 136, 200), (236, 232, 220), (200, 168, 112), (152, 120, 72),
    (64, 44, 36), (72, 32, 32), (176, 176, 168), (255, 255, 255),
]
SP = {".": 0, "o": 1, "s": 2, "S": 3, "h": 4, "H": 5, "j": 6, "J": 7, "k": 8, "w": 9, "p": 10,
      "P": 11, "b": 12, "e": 13}

HEAD_FRONT = [
    "................",
    ".....oooooo.....",
    "....oHHHhhho....",
    "...oHHhhhhhho...",
    "...ohhhhhhhhho..",
    "...ohsssshhhho..",
    "..osssssssShho..",
    "..osesseessSho..",
    "..osssssssSSo...",
    "...ossseesSo....",
    "....oSsssSo.....",
    ".....oSSSo......",
]
HEAD_BACK = [
    "................",
    ".....oooooo.....",
    "....oHHHhhho....",
    "...oHHhhhhhho...",
    "...ohhhhhhhhho..",
    "...ohhhhhhhhho..",
    "..ohhhhhhhhhho..",
    "..oShhhhhhhhho..",
    "...oShhhhhhho...",
    "....oShhhhho....",
    ".....ohhhho.....",
    ".....oSSSo......",
]
TORSO_FRONT = [
    "....ookwjjoo....",
    "...okkjwwjjJo...",
    "..okkjjwwjjJJo..",
    "..okjjjwwjjJJo..",
    "..okjjjjwjjJJo..",
    "..okjjjjjjjJJo..",
    "..ojjjjjjjjJJo..",
    "..osJjjjjjjJso..",
    "..oSoPppppPoSo..",
    "...oppppppPPo...",
]
TORSO_BACK = [
    "....ookjjjoo....",
    "...okkjjjjjJo...",
    "..okkjjjjjjJJo..",
    "..okjjjjjjjJJo..",
    "..okjjjjjjjJJo..",
    "..okjjjjjjjJJo..",
    "..ojjjjjjjjJJo..",
    "..osJjjjjjjJso..",
    "..oSoPppppPoSo..",
    "...oppppppPPo...",
]
LEGS = [
    [
        "...opppppPPPo...",
        "...oppppoPPPo...",
        "...opppo.oPPo...",
        "...opppo.oPPo...",
        "...opppo.oPPo...",
        "...opppo.oPPo...",
        "...opppo.oPPo...",
        "..obbbbo.obbbo..",
        "..obbbbo.obbbbo.",
        "...oooo...oooo..",
    ],
    [
        "...opppppPPPo...",
        "...oppppoPPPo...",
        "...opppo..oPPo..",
        "..opppo...oPPo..",
        "..opppo...oPPo..",
        "..opppo....oPo..",
        ".opppo.....oPo..",
        ".obbbbo....oPo..",
        ".obbbbo...obbbo.",
        "..oooo....oooo..",
    ],
    [
        "...opppppPPPo...",
        "...oppppoPPPo...",
        "...oppo..oPPPo..",
        "...oppo...oPPPo.",
        "...oppo...oPPPo.",
        "...oppo....oPPo.",
        "...oppo....oPPo.",
        "...oppo...obbbbo",
        "..obbbo...obbbbo",
        "..oooo.....oooo.",
    ],
]


def build_player():
    frames = [HEAD_FRONT + TORSO_FRONT + l for l in LEGS] + [HEAD_BACK + TORSO_BACK + l for l in LEGS]
    pixels = []
    for f in frames:
        assert len(f) == 32, len(f)
        for row in f:
            assert len(row) == 16, row
            pixels.append([SP[c] for c in row])
    return pixels, 16, 32 * len(frames)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def write_bmp(path, pixels, width, height, bpp, palette):
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
    pal = bytearray()
    for r, g, b in palette:
        pal.extend(bytes((b, g, r, 0)))
    offset = 14 + 40 + len(pal)
    header = struct.pack("<2sIHHI", b"BM", offset + len(data), 0, 0, offset)
    info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, bpp, 0, len(data), 2835, 2835,
                       len(palette), len(palette))
    with open(path, "wb") as f:
        f.write(header + info + pal + data)


def write_text(path, text):
    with open(path, "w", newline="\n") as f:
        f.write(text)


def unique_tiles(cv):
    tiles = set()
    for ty in range(0, cv.h, 8):
        for tx in range(0, cv.w, 8):
            t = tuple(tuple(cv.p[ty + y][tx:tx + 8]) for y in range(8))
            # Butano also reduces flipped tiles
            hf = tuple(tuple(reversed(r)) for r in t)
            vf = tuple(reversed(t))
            hvf = tuple(reversed(hf))
            if not ({t, hf, vf, hvf} & tiles):
                tiles.add(t)
    return len(tiles)


def save_preview(cv, path, objects=None):
    from PIL import Image
    img = Image.new("RGB", (cv.w, cv.h))
    data = []
    for y in range(cv.h):
        for x in range(cv.w):
            i = objects.p[y][x] if objects is not None and objects.p[y][x] else cv.p[y][x]
            data.append(PAL.colours[i])
    img.putdata(data)
    img.save(path)


def main():
    preview = None
    if len(sys.argv) >= 3 and sys.argv[1] == "--preview":
        preview = sys.argv[2]
        os.makedirs(preview, exist_ok=True)

    maps = [build_street(), build_corner_market()]
    rendered = []
    for m in maps:
        floor, objects = m.render()
        rendered.append((m, floor, objects))
    hud = build_hud()

    palette = list(PAL.colours) + [(0, 0, 0)] * ((-len(PAL.colours)) % 16)
    print(f"palette: {len(PAL.colours)} colours")

    gfx = os.path.join(ROOT, "graphics")
    total = 0
    bg_json = '{\n    "type": "regular_bg",\n    "bpp_mode": "bpp_8"\n}\n'
    for m, floor, objects in rendered:
        for suffix, cv in (("floor", floor), ("objects", objects)):
            n = unique_tiles(cv)
            total = max(total, 0)
            print(f"{m.ident}_{suffix}: {cv.w}x{cv.h}, ~{n} unique tiles")
            write_bmp(os.path.join(gfx, f"{m.ident}_{suffix}.bmp"), cv.p, cv.w, cv.h, 8, palette)
            write_text(os.path.join(gfx, f"{m.ident}_{suffix}.json"), bg_json)
        if preview:
            save_preview(floor, os.path.join(preview, m.ident + ".png"), objects)
    n = unique_tiles(hud)
    print(f"hud: ~{n} unique tiles")
    write_bmp(os.path.join(gfx, "hud.bmp"), hud.p, hud.w, hud.h, 8, palette)
    write_text(os.path.join(gfx, "hud.json"), bg_json)

    pixels, w, h = build_player()
    write_bmp(os.path.join(gfx, "player.bmp"), pixels, w, h, 4, SPRITE_PAL)
    write_text(os.path.join(gfx, "player.json"), '{\n    "type": "sprite",\n    "height": 32\n}\n')

    # ---- headers ----
    names = [m.ident for m in maps]
    ids = ["// Generated by tools/gen_iso.py - do not edit by hand.", "#ifndef TL_MAP_ID_H",
           "#define TL_MAP_ID_H", "", "namespace tl", "{", "    enum class map_id", "    {"]
    ids += [f"        {n}," for n in names]
    ids += ["    };", "", f"    constexpr int maps_count = {len(names)};", "}", "", "#endif", ""]
    write_text(os.path.join(ROOT, "include", "tl_map_id.h"), "\n".join(ids))

    out = ["// Generated by tools/gen_iso.py - do not edit by hand.",
           "// Include this file from exactly one .cpp (tl_world.cpp).",
           "#ifndef TL_WORLD_DATA_H", "#define TL_WORLD_DATA_H", "", '#include "tl_world.h"']
    for m in maps:
        out.append(f'#include "bn_regular_bg_items_{m.ident}_floor.h"')
        out.append(f'#include "bn_regular_bg_items_{m.ident}_objects.h"')
    out += ["", "namespace tl::world_data", "{"]
    for m in maps:
        out.append(f"    // ---- {m.name} ----")
        out.append(f"    constexpr uint8_t {m.ident}_solid[{m.w * m.h}] = {{")
        for cy in range(m.h):
            row = ",".join("1" if m.solid[cy][cx] else "0" for cx in range(m.w))
            out.append(f"        {row},  // {''.join(m.grid[cy])}")
        out.append("    };")
        out.append(f"    constexpr warp {m.ident}_warps[] = {{")
        for (x, y, w, h, target, tx, ty, facing) in m.warps:
            assert target in names
            out.append(f"        {{ {x}, {y}, {w}, {h}, map_id::{target}, {tx}, {ty}, direction::{facing} }},")
        out.append("    };")
        out.append(f"    constexpr occluder {m.ident}_occluders[] = {{")
        for o in m.occluders:
            out.append("        { " + ", ".join(str(int(v)) for v in o) + " },")
        out.append("    };")
        out.append("")
    out.append("    constexpr map_info maps[] = {")
    for m in maps:
        vx0, vy0, vx1, vy1 = m.view_bounds()
        out.append(f'        {{ "{m.name}", &bn::regular_bg_items::{m.ident}_floor, '
                   f'&bn::regular_bg_items::{m.ident}_objects, {m.w}, {m.h}, {m.ox}, {m.oy}, {m.bg_w}, {m.bg_h}, '
                   f'{vx0}, {vy0}, {vx1}, {vy1}, {m.ident}_solid, '
                   f'{m.ident}_warps, int(sizeof({m.ident}_warps) / sizeof(warp)), '
                   f'{m.ident}_occluders, int(sizeof({m.ident}_occluders) / sizeof(occluder)) }},')
    out += ["    };", "}", "", "#endif", ""]
    write_text(os.path.join(ROOT, "include", "tl_world_data.h"), "\n".join(out))


if __name__ == "__main__":
    main()
