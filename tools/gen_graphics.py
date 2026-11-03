#!/usr/bin/env python3
"""
Town Life - placeholder graphics generator.

Generates, without any external dependencies (pure Python 3):
  graphics/town.bmp      512x512 4bpp indexed background (the town tilemap)
  graphics/town.json     Butano asset descriptor
  graphics/player.bmp    16x144 4bpp indexed sprite sheet (9 frames of 16x16)
  graphics/player.json   Butano asset descriptor
  include/town_map_data.h  collision data (one byte per 16x16 metatile)

Run from the repository root:  python3 tools/gen_graphics.py
The outputs are committed, so the CI build does not need to run this script.
"""

import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Shared 16 colour palette (index 0 = transparent for sprites)
# ---------------------------------------------------------------------------
PALETTE = [
    (255, 0, 255),    # 0  transparent / backdrop
    (88, 168, 72),    # 1  grass
    (48, 112, 56),    # 2  dark green
    (88, 88, 100),    # 3  asphalt
    (176, 176, 168),  # 4  sidewalk grey
    (232, 208, 72),   # 5  yellow
    (232, 216, 176),  # 6  wall cream / sand
    (184, 64, 48),    # 7  roof red
    (120, 76, 40),    # 8  brown
    (112, 176, 232),  # 9  window blue
    (32, 32, 40),     # 10 dark outline
    (248, 248, 248),  # 11 white
    (240, 192, 152),  # 12 skin
    (56, 96, 200),    # 13 shirt blue
    (48, 104, 192),   # 14 water blue
    (232, 112, 168),  # 15 pink
]

MT = 16          # metatile size in pixels
MAP_W = 32       # map width in metatiles  (32 * 16 = 512 px)
MAP_H = 32       # map height in metatiles


def write_bmp_4bpp(path, pixels, width, height):
    """Writes an uncompressed 4bpp indexed BMP. pixels[y][x] = palette index."""
    row_bytes = ((width + 1) // 2 + 3) & ~3
    data = bytearray()
    for y in range(height - 1, -1, -1):
        row = bytearray()
        for x in range(0, width, 2):
            hi = pixels[y][x] & 0xF
            lo = pixels[y][x + 1] & 0xF if x + 1 < width else 0
            row.append((hi << 4) | lo)
        row.extend(b"\0" * (row_bytes - len(row)))
        data.extend(row)
    pal = bytearray()
    for r, g, b in PALETTE:
        pal.extend(bytes((b, g, r, 0)))
    offset = 14 + 40 + len(pal)
    header = struct.pack("<2sIHHI", b"BM", offset + len(data), 0, 0, offset)
    info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 4, 0, len(data), 2835, 2835, 16, 16)
    with open(path, "wb") as f:
        f.write(header + info + pal + data)


def write_text(path, text):
    with open(path, "w", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------------------
# Metatiles (16x16). Each is a function returning a 16x16 list of indices.
# ---------------------------------------------------------------------------
def fill(c):
    return [[c] * MT for _ in range(MT)]


def grass():
    t = fill(1)
    for (x, y) in ((3, 2), (11, 5), (6, 9), (13, 12), (2, 13), (8, 14)):
        t[y][x] = 2
    return t


def asphalt():
    t = fill(3)
    return t


def road_h():
    t = asphalt()
    for x in range(3, 13):
        t[7][x] = 5
        t[8][x] = 5
    return t


def road_v():
    t = asphalt()
    for y in range(3, 13):
        t[y][7] = 5
        t[y][8] = 5
    return t


def sidewalk():
    t = fill(4)
    for i in range(MT):
        t[15][i] = 3
        t[i][15] = 3
        t[7][i] = 3
    for y in range(0, 7):
        t[y][7] = 3
    for y in range(8, 15):
        t[y][11] = 3
    return t


def roof():
    t = fill(7)
    for y in (3, 7, 11, 15):
        for x in range(MT):
            t[y][x] = 8
    for y in range(MT):
        off = 0 if (y // 4) % 2 == 0 else 4
        for x in range(off, MT, 8):
            t[y][x] = 8
    return t


def wall():
    t = fill(6)
    for x in range(MT):
        t[15][x] = 10
    return t


def window():
    t = wall()
    for y in range(3, 12):
        for x in range(3, 13):
            t[y][x] = 11
    for y in range(4, 11):
        for x in range(4, 12):
            t[y][x] = 9
    for x in range(4, 12):
        t[7][x] = 11
    for y in range(4, 11):
        t[y][7] = 11
    return t


def door():
    t = wall()
    for y in range(2, 16):
        for x in range(4, 12):
            t[y][x] = 8
    for y in range(2, 16):
        t[y][4] = 10
        t[y][11] = 10
    for x in range(4, 12):
        t[2][x] = 10
    t[9][9] = 5
    return t


def tree():
    t = grass()
    cx, cy, r = 7.5, 6.5, 6.8
    for y in range(MT):
        for x in range(MT):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d <= r:
                t[y][x] = 2
                if d <= r - 1 and (x - cx) + (y - cy) < -3:
                    t[y][x] = 1
    for y in range(12, 16):
        for x in range(6, 10):
            t[y][x] = 8
    return t


def flowers():
    t = grass()
    for (x, y, c) in ((3, 3, 15), (10, 2, 5), (6, 7, 11), (13, 8, 15), (2, 11, 5), (9, 12, 15), (12, 14, 11)):
        t[y][x] = c
        t[y - 1][x] = 2
    return t


def water():
    t = fill(14)
    for (x, y) in ((2, 3), (3, 3), (4, 3), (9, 6), (10, 6), (11, 6), (5, 11), (6, 11), (7, 11), (12, 13), (13, 13)):
        t[y][x] = 11
    return t


def path():
    t = fill(6)
    for (x, y) in ((2, 2), (9, 4), (5, 9), (12, 11), (3, 14), (14, 6)):
        t[y][x] = 4
    return t


def fence():
    t = grass()
    for x in range(MT):
        t[6][x] = 8
        t[10][x] = 8
    for x in (2, 13):
        for y in range(3, 14):
            t[y][x] = 8
    return t


def bench():
    t = path()
    for x in range(1, 15):
        t[5][x] = 8
        t[6][x] = 8
        t[9][x] = 8
    for y in range(9, 14):
        t[y][2] = 10
        t[y][13] = 10
    return t


def fountain():
    t = path()
    cx, cy = 7.5, 7.5
    for y in range(MT):
        for x in range(MT):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d <= 7.5:
                t[y][x] = 4
            if d <= 6:
                t[y][x] = 14
            if d <= 2:
                t[y][x] = 11
    return t


# char -> (metatile function, solid)
TILES = {
    ".": (grass, False),
    "R": (asphalt, False),
    "h": (road_h, False),
    "v": (road_v, False),
    "s": (sidewalk, False),
    "T": (roof, True),
    "H": (wall, True),
    "W": (window, True),
    "D": (door, True),
    "t": (tree, True),
    "f": (flowers, False),
    "~": (water, True),
    "p": (path, False),
    "F": (fence, True),
    "b": (bench, True),
    "o": (fountain, True),
}


# ---------------------------------------------------------------------------
# Town layout (32x32 metatiles)
# ---------------------------------------------------------------------------
def build_layout():
    g = [["." for _ in range(MAP_W)] for _ in range(MAP_H)]

    def put(x, y, c):
        if 0 <= x < MAP_W and 0 <= y < MAP_H:
            g[y][x] = c

    # Roads: 3 metatiles wide, centre lane has the yellow dashes.
    road_rows = (9, 21)
    road_cols = (9, 21)
    for ry in road_rows:
        for x in range(MAP_W):
            put(x, ry, "R"); put(x, ry + 1, "h"); put(x, ry + 2, "R")
    for rx in road_cols:
        for y in range(MAP_H):
            put(rx, y, "R"); put(rx + 1, y, "v"); put(rx + 2, y, "R")
    for ry in road_rows:
        for rx in road_cols:
            for dy in range(3):
                for dx in range(3):
                    put(rx + dx, ry + dy, "R")

    # Sidewalks along every road.
    for ry in road_rows:
        for x in range(MAP_W):
            for y in (ry - 1, ry + 3):
                if g[y][x] == ".":
                    put(x, y, "s")
    for rx in road_cols:
        for y in range(MAP_H):
            for x in (rx - 1, rx + 3):
                if g[y][x] == ".":
                    put(x, y, "s")

    def house(x, y, door_dx=1, pathway=True):
        # 4 wide: 2 roof rows + 1 wall row
        for dx in range(4):
            put(x + dx, y, "T")
            put(x + dx, y + 1, "T")
            put(x + dx, y + 2, "W")
        put(x + door_dx, y + 2, "D")
        if pathway:
            yy = y + 3
            while yy < MAP_H and g[yy][x + door_dx] in ".f":
                put(x + door_dx, yy, "p")
                yy += 1

    # Residential blocks (blocks span 1..7, 13..19, 25..30)
    house(2, 2)
    house(14, 2, 2)
    house(26, 2)
    house(2, 14)
    house(26, 14, 2)
    house(2, 25)
    house(14, 25, 1)
    house(26, 25)

    # Little garden decorations
    for x in (1, 6, 7):
        put(x, 6, "f")
    for (x, y) in ((6, 3), (7, 4), (13, 5), (19, 3), (25, 6), (30, 6), (6, 17), (7, 16),
                   (30, 17), (25, 18), (6, 29), (19, 28), (13, 29), (30, 30)):
        put(x, y, "t")
    for x in range(14, 20):
        if g[29][x] == ".":
            put(x, 29, "f")
    for x in range(1, 8):
        if g[19][x] == "." and x != 3:
            put(x, 19, "F")
    for x in range(25, 31):
        if g[19][x] == "." and x != 28:
            put(x, 19, "F")

    # Central park (block 13..19 x 13..19)
    for y in range(13, 20):
        for x in range(13, 20):
            put(x, y, ".")
    for x in range(13, 20):
        put(x, 16, "p")
    for y in range(13, 20):
        put(16, y, "p")
    put(16, 16, "o")
    for (x, y) in ((13, 13), (19, 13), (13, 19), (19, 19)):
        put(x, y, "t")
    for (x, y) in ((14, 14), (18, 14)):
        put(x, y, "f")
    # Pond in the lower right of the park
    for (x, y) in ((17, 17), (18, 17), (17, 18), (18, 18)):
        put(x, y, "~")
    put(14, 18, "f")
    put(15, 17, "b")

    # Tree border around the whole town
    for x in range(MAP_W):
        if g[0][x] not in "Rhv":
            put(x, 0, "t")
        if g[MAP_H - 1][x] not in "Rhv":
            put(x, MAP_H - 1, "t")
    for y in range(MAP_H):
        if g[y][0] not in "Rhv":
            put(0, y, "t")
        if g[y][MAP_W - 1] not in "Rhv":
            put(MAP_W - 1, y, "t")

    # Road ends at the map edge are blocked by fences (the town is closed for now)
    for rx in road_cols:
        for dx in range(3):
            put(rx + dx, 0, "F")
            put(rx + dx, MAP_H - 1, "F")
    for ry in road_rows:
        for dy in range(3):
            put(0, ry + dy, "F")
            put(MAP_W - 1, ry + dy, "F")

    return g


def generate_town():
    layout = build_layout()
    cache = {}
    w, h = MAP_W * MT, MAP_H * MT
    pixels = [[0] * w for _ in range(h)]
    for my in range(MAP_H):
        for mx in range(MAP_W):
            c = layout[my][mx]
            if c not in cache:
                cache[c] = TILES[c][0]()
            tile = cache[c]
            for y in range(MT):
                pixels[my * MT + y][mx * MT:mx * MT + MT] = tile[y]
    write_bmp_4bpp(os.path.join(ROOT, "graphics", "town.bmp"), pixels, w, h)
    write_text(os.path.join(ROOT, "graphics", "town.json"),
               '{\n    "type": "regular_bg",\n    "bpp_mode": "bpp_4"\n}\n')

    # Collision header
    lines = []
    lines.append("// Generated by tools/gen_graphics.py - do not edit by hand.")
    lines.append("#ifndef TOWN_MAP_DATA_H")
    lines.append("#define TOWN_MAP_DATA_H")
    lines.append("")
    lines.append("#include <cstdint>")
    lines.append("")
    lines.append("namespace town_map_data")
    lines.append("{")
    lines.append(f"    constexpr int metatile_size = {MT};")
    lines.append(f"    constexpr int width = {MAP_W};   // in metatiles")
    lines.append(f"    constexpr int height = {MAP_H};  // in metatiles")
    lines.append("")
    lines.append("    // Layout legend:")
    for k, (fn, solid) in TILES.items():
        lines.append(f"    //   '{k}' {fn.__name__}{' (solid)' if solid else ''}")
    lines.append("")
    lines.append("    // 1 = solid, 0 = walkable. Row-major, one byte per metatile.")
    lines.append("    constexpr uint8_t solid[width * height] = {")
    for my in range(MAP_H):
        row = ", ".join("1" if TILES[c][1] else "0" for c in layout[my])
        lines.append(f"        {row},  // {''.join(layout[my])}")
    lines.append("    };")
    lines.append("}")
    lines.append("")
    lines.append("#endif")
    lines.append("")
    write_text(os.path.join(ROOT, "include", "town_map_data.h"), "\n".join(lines))
    return layout


# ---------------------------------------------------------------------------
# Player sprite sheet: 9 frames of 16x16, stacked vertically.
#   0-2 down (stand, step A, step B), 3-5 up, 6-8 side (facing right)
# ---------------------------------------------------------------------------
CHARS = {".": 0, "h": 8, "s": 12, "e": 10, "b": 13, "p": 3, "k": 10, "w": 11}

HEAD_DOWN = [
    "................",
    ".....hhhhhh.....",
    "....hhhhhhhh....",
    "....hhhhhhhh....",
    "....hssssssh....",
    "....sessssess...",
    "....ssssssss....",
    ".....ssssss.....",
]
HEAD_UP = [
    "................",
    ".....hhhhhh.....",
    "....hhhhhhhh....",
    "....hhhhhhhh....",
    "....hhhhhhhh....",
    "....hhhhhhhh....",
    "....shhhhhhs....",
    ".....ssssss.....",
]
HEAD_SIDE = [
    "................",
    ".....hhhhhh.....",
    "....hhhhhhhh....",
    "....hhhhhhhh....",
    "....hhhsssss....",
    "....hhsssses....",
    "....hsssssss....",
    ".....ssssss.....",
]
BODY_FRONT = [
    "....bbbbbbbb....",
    "...bbbbbbbbbb...",
    "...sbbbbbbbbs...",
    "...sbbbbbbbbs...",
]
BODY_SIDE = [
    ".....bbbbbb.....",
    ".....bbbbbb.....",
    ".....bbsbbb.....",
    ".....bbsbbb.....",
]
LEGS_FRONT = [
    [   # stand
        "....pppppppp....",
        "....ppp..ppp....",
        "....ppp..ppp....",
        "....kkk..kkk....",
    ],
    [   # step A
        "....pppppppp....",
        "....ppp..ppp....",
        "....kkk..ppp....",
        ".........kkk....",
    ],
    [   # step B
        "....pppppppp....",
        "....ppp..ppp....",
        "....ppp..kkk....",
        "....kkk.........",
    ],
]
LEGS_SIDE = [
    [
        ".....pppppp.....",
        "......pppp......",
        "......pppp......",
        "......kkkkk.....",
    ],
    [
        ".....pppppp.....",
        ".....pp..pp.....",
        "....pp....pp....",
        "...kk......kk...",
    ],
    [
        ".....pppppp.....",
        "......pppp......",
        ".....pp.pp......",
        ".....kk.kkk.....",
    ],
]


def generate_player():
    frames = []
    for legs in LEGS_FRONT:
        frames.append(HEAD_DOWN + BODY_FRONT + legs)
    for legs in LEGS_FRONT:
        frames.append(HEAD_UP + BODY_FRONT + legs)
    for legs in LEGS_SIDE:
        frames.append(HEAD_SIDE + BODY_SIDE + legs)
    pixels = []
    for f in frames:
        assert len(f) == 16
        for row in f:
            assert len(row) == 16, row
            pixels.append([CHARS[c] for c in row])
    write_bmp_4bpp(os.path.join(ROOT, "graphics", "player.bmp"), pixels, 16, 16 * len(frames))
    write_text(os.path.join(ROOT, "graphics", "player.json"),
               '{\n    "type": "sprite",\n    "height": 16\n}\n')


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "graphics"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "include"), exist_ok=True)
    layout = generate_town()
    generate_player()
    for row in layout:
        print("".join(row))
