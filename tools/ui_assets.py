#!/usr/bin/env python3
"""UI assets (approved "Paper" / "Night" style): panel pieces, highlight bar pieces, A/B button icons, the "A" cue
bubble and the bold pixel fonts. Run by build_assets.py (or alone: python3 tools/ui_assets.py).

Writes
  graphics/ui_pan_{te,tm,ne,nm,be,bm,de,dm}.bmp/.json   panel pieces (top titled/untitled, bottom, body; E = end,
                                                          M = middle; the right end is the left end flipped)
  graphics/ui_bar_{l,m,r}.bmp/.json                      rounded highlight bar pieces
  graphics/ui_icons.bmp/.json                            16x16 frames: 0 = A button, 1 = B button, 2 = "A" cue bubble
  src/tl_ui_font_data.cpp                                DejaVu Sans Bold baked to 2-bit glyph rows (9 px and 11 px)

The panel pieces use the UI palette indices below; tl_ui.cpp holds the real colours of both styles (the BMP palette
here is only the Night style, as a preview). DejaVu licence: art_source/fonts/LICENSE-DejaVu.txt.
"""
import os
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# UI palette indices (same meaning in both styles, see tl_ui.cpp)
(TRANSP, PANEL, BORDER, EDGE, TITLE_BG, TITLE_OUT, TEXT, BAR, BAR_EDGE, BAR_TEXT, HINT, TEXT_OUT, WHITE, GOLD,
 MONEY, NAVY) = range(16)

NIGHT_PAL = {PANEL: (24, 30, 62), BORDER: (150, 176, 230), EDGE: (60, 72, 130), TITLE_BG: (14, 18, 40),
             TITLE_OUT: (14, 18, 40), TEXT: (255, 255, 255), BAR: (46, 196, 182), BAR_EDGE: (190, 255, 246),
             BAR_TEXT: (8, 24, 44), HINT: (170, 186, 230), TEXT_OUT: (10, 12, 30), WHITE: (255, 255, 255),
             GOLD: (255, 214, 92), MONEY: (255, 214, 92), NAVY: (10, 12, 30)}


def write_bmp(path, im, palette):
    """4-bit indexed BMP; palette[0] is the transparent colour (magenta)."""
    w, h = im.size
    px = im.load()
    data = bytearray()
    for y in range(h - 1, -1, -1):
        row = bytearray()
        for x in range(0, w, 2):
            row.append(((px[x, y] & 0xF) << 4) | (px[x + 1, y] & 0xF))
        row.extend(b"\0" * ((-len(row)) % 4))
        data.extend(row)
    pal = bytearray()
    for r, g, b in palette:
        pal.extend(bytes((b, g, r, 0)))
    offset = 14 + 40 + len(pal)
    header = struct.pack("<2sIHHI", b"BM", offset + len(data), 0, 0, offset)
    info = struct.pack("<IiiHHIIiiII", 40, w, h, 1, 4, 0, len(data), 2835, 2835, len(palette), len(palette))
    with open(path, "wb") as f:
        f.write(header + info + pal + data)


def write_item(name, im, frame_h, palette):
    write_bmp(os.path.join(ROOT, "graphics", name + ".bmp"), im, palette)
    with open(os.path.join(ROOT, "graphics", name + ".json"), "w", newline="\n") as f:
        f.write(f'{{\n    "type": "sprite",\n    "height": {frame_h}\n}}\n')


def preview_palette():
    pal = [(255, 0, 255)] + [NIGHT_PAL.get(i, (0, 0, 0)) for i in range(1, 16)]
    return pal


# ------------------------------------------------------------------------------------------------ panels
def panel_model(titled):
    """256x128 panel: 2 px border, 1 px inner edge, optional title band (rows 2..15); corners rounded."""
    im = Image.new("P", (256, 128), TRANSP)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 255, 127), radius=4, fill=PANEL, outline=BORDER, width=2)
    d.rounded_rectangle((2, 2, 253, 125), radius=2, outline=EDGE, width=1)
    if titled:
        d.rounded_rectangle((2, 2, 253, 15), radius=2, fill=TITLE_BG)
        d.rectangle((2, 9, 253, 15), fill=TITLE_BG)
    return im


def build_panels():
    pal = preview_palette()
    t, n = panel_model(True), panel_model(False)
    pieces = {
        "te": t.crop((0, 0, 64, 32)), "tm": t.crop((96, 0, 160, 32)),
        "ne": n.crop((0, 0, 64, 32)), "nm": n.crop((96, 0, 160, 32)),
        "be": n.crop((0, 96, 64, 128)), "bm": n.crop((96, 96, 160, 128)),
        "de": n.crop((0, 32, 64, 96)), "dm": n.crop((96, 32, 160, 96)),
    }
    for k, im in pieces.items():
        write_item("ui_pan_" + k, im, im.height, pal)


def build_bars():
    """Highlight bar: 13 rows tall, drawn at rows 9..21 of a 32-row sprite; the left cap holds the cursor triangle."""
    im = Image.new("P", (256, 32), TRANSP)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 9, 255, 21), radius=3, fill=BAR, outline=BAR_EDGE, width=1)
    d.polygon([(4, 12), (4, 18), (8, 15)], fill=BAR_TEXT)
    pal = preview_palette()
    write_item("ui_bar_l", im.crop((0, 0, 16, 32)), 32, pal)
    # middle and right pieces without the triangle
    im2 = Image.new("P", (256, 32), TRANSP)
    d2 = ImageDraw.Draw(im2)
    d2.rounded_rectangle((0, 9, 255, 21), radius=3, fill=BAR, outline=BAR_EDGE, width=1)
    write_item("ui_bar_m", im2.crop((96, 0, 160, 32)), 32, pal)
    write_item("ui_bar_r", im2.crop((240, 0, 256, 32)), 32, pal)


# ------------------------------------------------------------------------------------------------ icons
ICON_PAL = [(255, 0, 255), (252, 206, 70), (40, 24, 12), (70, 150, 70), (200, 70, 60), (255, 255, 255),
            (20, 14, 12), (255, 238, 150)] + [(0, 0, 0)] * 8
GLYPH_A = (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
GLYPH_B = ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####.")


def glyph(im, rows, x, y, colour):
    for gy, row in enumerate(rows):
        for gx, c in enumerate(row):
            if c == "#":
                im.putpixel((x + gx, y + gy), colour)


def build_icons():
    """Frames of 16x16: A button (green), B button (red), the bobbing "A" cue bubble (gold, tail tip at (7, 15))."""
    out = Image.new("P", (16, 48), TRANSP)
    for i, (fill, rows) in enumerate(((3, GLYPH_A), (4, GLYPH_B))):
        f = Image.new("P", (16, 16), 0)
        d = ImageDraw.Draw(f)
        d.ellipse((3, 3, 12, 12), fill=fill, outline=6)
        glyph(f, rows, 5, 4, 5)
        out.paste(f, (0, i * 16))
    f = Image.new("P", (16, 16), 0)
    d = ImageDraw.Draw(f)
    d.polygon([(5, 11), (9, 11), (7, 15)], fill=2)
    d.polygon([(6, 11), (8, 11), (7, 13)], fill=1)
    d.ellipse((0, 0, 14, 13), fill=1, outline=2)
    d.arc((2, 2, 12, 11), 200, 290, fill=7)                     # small highlight
    glyph(f, GLYPH_A, 5, 3, 2)
    out.paste(f, (0, 32))
    write_item("ui_icons", out, 16, ICON_PAL)


# ------------------------------------------------------------------------------------------------ dialogue pieces
def build_tag():
    """Name tag of the dialogue box (ui palette): frame 0 = left cap, frame 1 = middle (the right cap is the left one
    flipped). 16x16 frames, the tag is 12 px high (rows 2..13)."""
    out = Image.new("P", (16, 32), TRANSP)
    left = Image.new("P", (16, 16), TRANSP)
    d = ImageDraw.Draw(left)
    d.rounded_rectangle((0, 2, 40, 13), radius=3, fill=TITLE_BG, outline=BORDER, width=1)
    mid = Image.new("P", (16, 16), TRANSP)
    d = ImageDraw.Draw(mid)
    d.rectangle((0, 3, 15, 12), fill=TITLE_BG)
    d.line((0, 2, 15, 2), fill=BORDER)
    d.line((0, 13, 15, 13), fill=BORDER)
    out.paste(left.crop((0, 0, 16, 16)), (0, 0))
    out.paste(mid, (0, 16))
    write_item("ui_tag", out, 16, preview_palette())


def build_key():
    """Key / cursor cell of the name entry keyboard: a rounded highlight (the highlight bar colours), 16x16."""
    im = Image.new("P", (16, 16), TRANSP)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 1, 15, 14), radius=3, fill=BAR, outline=BAR_EDGE, width=1)
    write_item("ui_key", im, 16, preview_palette())


METER_H = 28           # inner height of the friendship meter in pixels = number of fill frames - 1
METER_PAL = [(255, 0, 255), (16, 14, 24), (200, 210, 230), (34, 36, 58), (214, 52, 44), (240, 130, 44), (244, 208, 60),
             (160, 214, 62), (62, 196, 84), (255, 214, 92), (255, 255, 255)] + [(0, 0, 0)] * 5


def build_meter():
    """Vertical friendship meter, 16x32 frames: frame n has n pixel rows filled from the bottom, colours graded red (bottom)
    to green (top); a gold tick marks 70 (where City Coins start)."""
    frames = Image.new("P", (16, 32 * (METER_H + 1)), TRANSP)
    for n in range(METER_H + 1):
        f = Image.new("P", (16, 32), TRANSP)
        d = ImageDraw.Draw(f)
        d.rounded_rectangle((3, 0, 12, 31), radius=2, fill=1)
        d.rounded_rectangle((4, 1, 11, 30), radius=1, fill=2)
        d.rectangle((5, 2, 10, 29), fill=3)
        for r in range(n):                       # r = pixel row from the bottom of the inner area
            colour = 4 if r < 6 else 5 if r < 11 else 6 if r < 16 else 7 if r < 21 else 8
            y = 29 - r
            d.line((5, y, 10, y), fill=colour)
            if r % 3 == 1:
                f.putpixel((5, y), 10 if colour != 8 else 10)
        tick = 29 - round(METER_H * 0.7)
        f.putpixel((4, tick), 9)
        f.putpixel((11, tick), 9)
        frames.paste(f, (0, 32 * n))
    write_item("ui_meter", frames, 32, METER_PAL)


# ------------------------------------------------------------------------------------------------ fonts
def build_font(size, baseline):
    """Glyph cells 16 x 16: pixel (2 + ink x), baseline row `baseline`; 2 bits per pixel (0 none, 1 fill, 2 outline)."""
    font = ImageFont.truetype(FONT_PATH, size)
    rows_out, widths = [], []
    for code in range(32, 127):
        ch = chr(code)
        im = Image.new("L", (16, 16), 0)
        d = ImageDraw.Draw(im)
        d.fontmode = "1"
        d.text((2, baseline), ch, font=font, fill=255, anchor="ls")
        fill = [[im.getpixel((x, y)) > 127 for x in range(16)] for y in range(16)]
        glyph_rows = []
        ink_right = 0
        for y in range(16):
            word = 0
            for x in range(16):
                v = 0
                if fill[y][x]:
                    v = 1
                    ink_right = max(ink_right, x - 2 + 1)
                else:
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = y + dy, x + dx
                            if 0 <= yy < 16 and 0 <= xx < 16 and fill[yy][xx]:
                                v = 2
                word |= v << (2 * x)
            glyph_rows.append(word)
        adv = int(round(font.getlength(ch)))
        if ch != " ":
            adv = max(adv, ink_right)
        widths.append(adv)
        rows_out.extend(glyph_rows)
    return rows_out, widths


def write_font_cpp():
    lines = ['// GENERATED by tools/ui_assets.py - DejaVu Sans Bold baked into 2-bit glyph rows (see art_source/fonts).',
             '', '#include "tl_ui_font.h"', '', 'namespace tl::ui', '{']
    for name, size, base in (("font9", 9, 11), ("font11", 11, 12)):
        rows, widths = build_font(size, base)
        lines.append(f'    const uint32_t {name}_rows[95 * 16] = {{')
        for i in range(0, len(rows), 8):
            lines.append("        " + ", ".join(f"0x{v:08x}" for v in rows[i:i + 8]) + ",")
        lines.append("    };")
        lines.append(f'    const uint8_t {name}_widths[95] = {{ ' + ", ".join(str(w) for w in widths) + " };")
        lines.append(f'    const font_data {name} = {{ {name}_rows, {name}_widths, {base} }};')
        lines.append("")
    lines.append("}")
    path = os.path.join(ROOT, "src", "tl_ui_font_data.cpp")
    with open(path, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def main():
    build_panels()
    build_bars()
    build_icons()
    build_tag()
    build_key()
    build_meter()
    write_font_cpp()
    print("ui assets written")


if __name__ == "__main__":
    main()
