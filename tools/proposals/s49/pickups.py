#!/usr/bin/env python3
"""Pixel-art pickup sprites for the can & bottle deposit proposal (own design, 16x16 frames, one shared 15-colour
palette, index 0 = transparent). Six items x 2 sparkle frames. Writes pickups_sheet.png (8x) and graphics-ready
pickups.bmp (16x16 frames stacked vertically; NOT added to the game yet)."""
import os
import sys
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/s49"
P = {
    ".": None,
    "o": (30, 28, 40),        # outline
    "s": (206, 214, 228),     # silver
    "S": (128, 138, 158),     # silver shade
    "r": (216, 58, 42),       # red can
    "R": (150, 34, 24),
    "b": (58, 106, 208),      # blue can
    "B": (36, 72, 150),
    "g": (66, 170, 94),       # green glass
    "G": (30, 110, 58),
    "n": (150, 98, 44),       # brown glass
    "N": (96, 60, 26),
    "c": (150, 208, 232),     # clear glass
    "C": (96, 156, 190),
    "w": (255, 255, 255),     # sparkle / highlight
}
# 16x16, item drawn lying on the ground (screen-aligned, slightly tilted): each 'row' string is 16 wide
CAN = {
    "red": ("r", "R"), "blue": ("b", "B"), "silver": ("s", "S"),
}
def _place(art, ox=2, oy=5):
    rows = [["."] * 16 for _ in range(16)]
    for y, r in enumerate(art):
        for x, ch in enumerate(r):
            rows[oy + y][ox + x] = ch
    return ["".join(r) for r in rows]


def can(a, d):
    """Drink can lying on its side: lighter end cap on the left, rim band, shaded underside."""
    art = [
        "...oooooooo...",
        "..oSssAAAAAo..",
        ".oswsSAAAAAAo.",
        ".osssSAAAAAdo.",
        "..oSSsAAAAdo..",
        "...oooooooo...",
    ]
    return [r.replace("A", a).replace("d", d) for r in _place(art, 1, 5)]


def bottle(a, d):
    """Glass bottle lying on its side: round body on the left, neck and cap on the right."""
    art = [
        "..oooooooo......",
        ".oAAwAAAAAooo...",
        "oAAwAAAAAAAAAoos",
        "oAAAAAAAAAAAAoss",
        ".oAAAAAAAddooo..",
        "..oooooooo......",
    ]
    return [r.replace("A", a).replace("d", d) for r in _place(art, 0, 5)]


ITEMS = {
    "can_red": can("r", "R"), "can_blue": can("b", "B"), "can_silver": can("s", "S"),
    "bottle_green": bottle("g", "G"), "bottle_brown": bottle("n", "N"), "bottle_clear": bottle("c", "C"),
}

def spark(rows, frame, pos=(11, 4)):
    """frame 0: one white pixel + 4 dim neighbours; frame 1: a bigger plus sign (the twinkle)."""
    rows = [list(r) for r in rows]
    x, y = pos
    def put(px, py, ch):
        if 0 <= px < 16 and 0 <= py < 16:
            rows[py][px] = ch
    put(x, y, "w")
    if frame == 1:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(x + dx, y + dy, "w")
        put(x + 2, y, "w"); put(x - 2, y, "w"); put(x, y - 2, "w"); put(x, y + 2, "w")
    return ["".join(r) for r in rows]

def render(rows):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            c = P.get(ch)
            if c:
                im.putpixel((x, y), c + (255,))
    return im

def frames():
    out = {}
    for k, rows in ITEMS.items():
        out[k] = [render(spark(rows, f, (12, 3) if k.startswith("can") else (11, 3))) for f in (0, 1)]
    return out

if __name__ == "__main__":
    fr = frames()
    sheet = Image.new("RGBA", (16 * 6, 32), (60, 90, 60, 255))
    for i, k in enumerate(ITEMS):
        for f in (0, 1):
            sheet.alpha_composite(fr[k][f], (i * 16, f * 16))
    sheet.convert("RGB").resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save(os.path.join(OUT, "pickups_sheet.png"))
    print("ok", len(P) - 1, "colours")
