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


