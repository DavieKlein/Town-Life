"""
Town Life - HUD background and temporary player sprite (pure Python 3).
Used by tools/build_assets.py.
"""

PAL_COLOURS = [(0, 0, 0)]
PAL_INDEX = {}


def q(c):
    return tuple(max(0, min(255, int(round(v)))) & 0xF8 for v in c)


class _Pal:
    colours = PAL_COLOURS

    def get(self, rgb):
        rgb = q(rgb)
        if rgb not in PAL_INDEX:
            PAL_INDEX[rgb] = len(PAL_COLOURS)
            PAL_COLOURS.append(rgb)
        return PAL_INDEX[rgb]


PAL = _Pal()
WHITE = (240, 240, 232)


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


ICONS["bladder"] = [
    "................",
    "...##########...",
    "...#........#...",
    "...##########...",
    "....########....",
    "....########....",
    "..############..",
    "..############..",
    "..#..........#..",
    "...#........#...",
    "....#......#....",
    ".....######.....",
    "......####......",
    "......####......",
    ".....######.....",
    "................",
]


ICONS["social"] = [
    "................",
    "..#########.....",
    ".#WWWWWWWWW#....",
    ".#WW.W.W.WW#....",
    ".#WWWWWWWWW#....",
    "..###WW####.....",
    "....#W#..#######",
    ".........#GGGGG#",
    ".........#GG.G.#",
    ".........#GGGGG#",
    ".........#GGGGG#",
    "..........##G###",
    "............#G#.",
    ".............#..",
    "................",
    "................",
]
SOCIAL_COLOURS = {"W": (240, 240, 232), "G": (232, 176, 64)}


# ---------------------------------------------------------------------------
# s78 need icons (owner request): bed, knife+fork, shower, game controller, toilet, speech bubble.
# 14 px wide max, centred in a 14x14 box; build_hud adds a 1 px dark outline (16x16 per slot icon).
# Glyph letters: W white, s silver, S dark silver, b brown, B dark brown, n blue, L light blue,
# G grey, d dark detail (cut-out), y gold.
# Switch the look with HUD_ICON_STYLE: "A" = white / light-blue monochrome glyphs (owner choice, active),
# "B" = small coloured icons, "OLD" = the s64 glyphs (kept for comparison). Env var TL_HUD_ICONS overrides it.
# ---------------------------------------------------------------------------
import os

HUD_ICON_STYLE = "A"

NEW_ICONS = {
    "energy": [          # bed
        "bb..........bb",
        "bb..........bb",
        "bb..........bb",
        "bbWWWWnnnnnnbb",
        "bbWWWWnnnnnnbb",
        "bbbbbbbbbbbbbb",
        "BBBBBBBBBBBBBB",
        "bb..........bb",
        "bb..........bb",
    ],
    "hunger": [          # fork + knife
        "s.ss.s...ss",
        "s.ss.s..sss",
        "s.ss.s..sss",
        "s.ss.s..sss",
        "ssssss..sss",
        "ssssss..sss",
        "..ss....sss",
        "..ss....sss",
        "..SS.....SS",
        "..SS.....SS",
        "..SS.....SS",
        "..SS.....SS",
        "..SS.....SS",
    ],
    "bladder": [         # toilet bowl, side view
        "SSSSS.........",
        "WWWWW.........",
        "WWWWW.........",
        "WWWWW.........",
        "SSSSSSSSSSSSSS",
        "WWWWWWWWWWWWWW",
        ".WWWWWWWWWWWSS",
        "..WWWWWWWWWSS.",
        "...WWWWWWWSS..",
        "....WWWWWSS...",
        "....WWWWS.....",
        "...WWWWWWS....",
    ],
    "social": [          # speech bubble
        ".WWWWWWWWWWW.",
        "WWWWWWWWWWWWW",
        "WWWWWWWWWWWWW",
        "WWWdWWdWWdWWW",
        "WWWWWWWWWWWWW",
        "WWWWWWWWWWWWW",
        ".WWWWWWWWWWW.",
        "..WWWW.......",
        "..WWW........",
        "..WW.........",
    ],
    "fun": [             # game controller
        ".GGGGGGGGGGGG.",
        "GGGdGGGGGGGGGG",
        "GGdddGGGyGyGGG",
        "GGGdGGGGGGGGGG",
        "GGGGGGGGGGGGGG",
        ".GGGGGGGGGGGG.",
        ".GGGG....GGGG.",
        ".GGG......GGG.",
        "..GG......GG..",
    ],
    "hygiene": [         # shower head with drops
        "......ss......",
        "......ss......",
        "....ssssss....",
        "..ssssssssss..",
        "..SSSSSSSSSS..",
        "..............",
        ".LL..LL..LL...",
        ".uu..uu..uu...",
        "..............",
        "...LL..LL..LL.",
        "...uu..uu..uu.",
        "..............",
        ".LL..LL..LL...",
        ".uu..uu..uu...",
    ],
}

COL_B = {"W": (240, 240, 232), "s": (208, 216, 224), "S": (144, 152, 176), "b": (184, 120, 64), "B": (128, 80, 40),
         "n": (88, 144, 216), "L": (144, 208, 248), "u": (56, 120, 216), "G": (160, 160, 176),
         "d": (16, 16, 24), "y": (232, 176, 64)}
SHADE_A = (160, 176, 224)
COL_A = {"W": (240, 240, 232), "s": (240, 240, 232), "S": SHADE_A, "b": (240, 240, 232), "B": SHADE_A,
         "n": SHADE_A, "L": (240, 240, 232), "u": SHADE_A, "G": (240, 240, 232), "d": (16, 16, 24), "y": (16, 16, 24)}
OUTLINE = (16, 16, 24)


def _icon_pixels(rows, cols):
    """16x16 dict {(x, y): rgb}: glyph centred in 14x14 plus a 1 px (8-neighbour) outline."""
    h = len(rows)
    w = max(len(r) for r in rows)
    ox = 1 + (14 - w) // 2
    oy = 1 + (14 - h) // 2
    fill = {}
    for yy, row in enumerate(rows):
        for xx, ch in enumerate(row):
            if ch in cols:
                fill[(ox + xx, oy + yy)] = cols[ch]
    out = dict(fill)
    for (x, y) in fill:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                k = (x + dx, y + dy)
                if k not in fill and 0 <= k[0] < 16 and 0 <= k[1] < 16:
                    out[k] = OUTLINE
    return out


def build_hud():
    cv = Canvas(256, 256)
    top = 176
    panel = (40, 48, 88)
    panel_l = (72, 84, 136)
    panel_d = (24, 28, 56)
    cv.rect(8, top, 240, 32, panel_d)
    # clock / money panel
    cv.rect(10, top + 2, 50, 28, panel)
    cv.rect(10, top + 2, 50, 1, panel_l)
    cv.rect(14, top + 15, 42, 1, panel_l)
    # s64 HUD variant A: six slim slots, 28 px wide at pitch 30 starting at bg x 62 (tl_field.cpp places the
    # hud_bar sprites at x = -46 + 30 * slot): Hunger, Energy, Hygiene, Fun, Bladder, Social.
    names = ["hunger", "energy", "hygiene", "fun", "bladder", "social"]
    style = os.environ.get("TL_HUD_ICONS", HUD_ICON_STYLE)
    for i, n in enumerate(names):
        x = 62 + i * 30
        cv.rect(x, top + 2, 28, 28, panel)
        cv.rect(x, top + 2, 28, 1, panel_l)
        if style == "OLD":
            for yy, row in enumerate(ICONS[n]):
                for xx, ch in enumerate(row):
                    if ch == "#":
                        cv.set(x + 6 + xx + 1, top + 3 + yy + 1, panel_d)
                        cv.set(x + 6 + xx, top + 3 + yy, WHITE)
            for yy, row in enumerate(ICONS[n]):
                for xx, ch in enumerate(row):
                    if ch in SOCIAL_COLOURS:
                        cv.set(x + 6 + xx, top + 3 + yy, SOCIAL_COLOURS[ch])
        else:
            px = _icon_pixels(NEW_ICONS[n], COL_A if style == "A" else COL_B)
            for (ix, iy), rgb in px.items():
                cv.set(x + 6 + ix, top + 2 + iy, rgb)
        # bar background (22 px); the fill is a sprite (graphics/hud_bar.bmp) updated by the game
        cv.rect(x + 3, top + 22, 22, 5, (16, 16, 24))
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




BAR_LEVELS = 16


def build_need_bar():
    """32x8 frames, BAR_LEVELS levels: frame i fills i * 30 / (BAR_LEVELS - 1) px of a 30x3 bar
    (green when high, orange in the middle, red when low)."""
    pal = [(255, 0, 255), (88, 200, 88), (232, 160, 48), (200, 56, 48), (60, 24, 28)]
    pixels = []
    for level in range(BAR_LEVELS):
        fill = round(level * 30 / (BAR_LEVELS - 1))
        colour = 1 if fill > 18 else (2 if fill > 9 else 3)
        for y in range(8):
            row = [0] * 32
            if y < 3:
                for x in range(30):
                    row[x] = colour if x < fill else 4
            pixels.append(row)
    return pixels, pal


def build_hud_bar():
    """32x8 frames, BAR_LEVELS levels: slim 20x3 bar for the six HUD slots."""
    pal = [(255, 0, 255), (88, 200, 88), (232, 160, 48), (200, 56, 48), (60, 24, 28)]
    pixels = []
    for level in range(BAR_LEVELS):
        fill = round(level * 20 / (BAR_LEVELS - 1))
        colour = 1 if fill > 12 else (2 if fill > 6 else 3)
        for y in range(8):
            row = [0] * 32
            if y < 3:
                for x in range(20):
                    row[x] = colour if x < fill else 4
            pixels.append(row)
    return pixels, pal


def build_menu_panel():
    """96x64 menu panel (title strip + body) split by the game into a 64x64 and a 32x64 sprite,
    plus a 64x16 selection highlight split into two 32x16 frames (left, right). Same colours as the HUD bar."""
    pal = [(255, 0, 255), (24, 28, 56), (40, 48, 88), (72, 84, 136), (16, 16, 24)]
    w, h = 96, 64
    panel = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if x == 0 or y == 0 or x == w - 1 or y == h - 1:
                panel[y][x] = 3
            elif y <= 12:
                panel[y][x] = 2
            else:
                panel[y][x] = 1
    for x in range(1, w - 1):
        panel[13][x] = 3
    left = [row[:64] for row in panel]
    right = [row[64:] for row in panel]
    full = [[3 if (y in (0, 13) or x in (0, 63)) else 2 for x in range(64)] if y < 14 else [0] * 64
            for y in range(16)]
    # two 32x16 frames (left half, right half) stacked vertically
    highlight = [row[:32] for row in full] + [row[32:] for row in full]
    return left, right, highlight, pal


def build_light_pool():
    """Night light pool under a street lamp: 64x32 iso ellipse, 4 warm levels with checker dithering.
    The game draws it with additive-style blending (top weight ~0.5, bottom weight 1)."""
    pal = [(255, 0, 255), (56, 40, 16), (104, 80, 32), (160, 124, 56), (216, 172, 88)]
    w, h = 64, 32
    pixels = []
    for y in range(h):
        row = []
        for x in range(w):
            dx = (x + 0.5 - w / 2) / (w / 2)
            dy = (y + 0.5 - h / 2) / (h / 2)
            v = max(0.0, 1.0 - (dx * dx + dy * dy)) ** 0.8
            level = v * 4 + (0.5 if (x + y) % 2 else 0.0)
            row.append(min(4, int(level)))
        pixels.append(row)
    return pixels, pal
