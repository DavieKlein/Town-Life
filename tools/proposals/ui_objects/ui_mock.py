#!/usr/bin/env python3
"""UI proposal mock-ups (owner feedback C): clearer, bolder menus. Draws two variants of every UI element on real
in-game screenshots (240x160, from tools/headless_run.py) and writes comparison sheets.

  python3 ui_mock.py BG_DIR OUT_DIR

BG_DIR needs clean screenshots park.png (city, no menu), cc.png, market.png and cur_*.png (the current UI, for
the "current vs proposed" row). Own design: nothing here is taken from another game. The text is the
DejaVu Sans Bold TTF (free licence) rendered without anti-aliasing at 9 px, to be baked into a Butano sprite font
(tools script to come, after approval).
Variant A "Paper": cream panel, dark ink text, gold rounded highlight bar. Warm like the early story.
Variant B "Night": navy panel like the HUD, white outlined text, gold title, teal rounded highlight bar.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F9 = ImageFont.truetype(FONT, 9)
F8 = ImageFont.truetype(FONT, 8)
F11 = ImageFont.truetype(FONT, 11)
F20 = ImageFont.truetype(FONT, 20)


def text(d, x, y, s, fill, font=F9, outline=None, shadow=None, anchor="ls", align=None):
    """Hard-edged text; (x, y) = baseline start. outline = 1 px all around, shadow = 1 px down-right."""
    d.fontmode = "1"
    if align == "right":
        anchor = "rs"
    elif align == "centre":
        anchor = "ms"
    if outline:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    d.text((x + dx, y + dy), s, font=font, fill=outline, anchor=anchor)
    if shadow:
        d.text((x + 1, y + 1), s, font=font, fill=shadow, anchor=anchor)
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)


def width(s, font=F9):
    return int(font.getlength(s))


def rrect(d, box, r, fill, outline=None, w=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=w)


class Style:
    """Colours + drawing of one variant."""

    def __init__(self, name):
        self.name = name
        if name == "A":
            self.panel, self.border, self.edge = (244, 232, 200), (70, 46, 34), (255, 250, 232)
            self.title_bg, self.title_fg, self.title_out = (200, 76, 52), (255, 255, 255), (96, 28, 20)
            self.text, self.text_out, self.text_sh = (50, 34, 30), None, (255, 250, 232)
            self.bar, self.bar_edge, self.bar_text, self.bar_out = (250, 200, 64), (110, 66, 24), (50, 34, 30), None
            self.dim = (150, 130, 110)
            self.hint = (110, 90, 80)
        else:
            self.panel, self.border, self.edge = (24, 30, 62), (150, 176, 230), (60, 72, 130)
            self.title_bg, self.title_fg, self.title_out = (14, 18, 40), (255, 214, 92), (14, 18, 40)
            self.text, self.text_out, self.text_sh = (255, 255, 255), (10, 12, 30), None
            self.bar, self.bar_edge, self.bar_text, self.bar_out = (46, 196, 182), (190, 255, 246), (8, 24, 44), None
            self.dim = (120, 130, 170)
            self.hint = (170, 186, 230)

    def card(self, d, x, y, w, h, title=None):
        """Panel with a drop shadow, rounded border and an optional title band; returns the content top."""
        rrect(d, (x + 2, y + 2, x + w + 1, y + h + 1), 4, (10, 8, 16))
        rrect(d, (x, y, x + w - 1, y + h - 1), 4, self.panel, self.border, 2)
        rrect(d, (x + 2, y + 2, x + w - 3, y + h - 3), 2, None, self.edge, 1)
        top = y + 4
        if title:
            d.rounded_rectangle((x + 2, y + 2, x + w - 3, y + 15), radius=2, fill=self.title_bg)
            d.rectangle((x + 2, y + 9, x + w - 3, y + 15), fill=self.title_bg)
            text(d, x + 7, y + 12, title, self.title_fg, F9, outline=self.title_out)
            top = y + 17
        return top

    def row(self, d, x, y, w, label, selected, right=None, h=13):
        """One option row (pitch 14): selected = full-width rounded bar exactly fitting the row, cursor triangle."""
        if selected:
            rrect(d, (x, y, x + w - 1, y + h - 1), 3, self.bar, self.bar_edge, 1)
            d.polygon([(x + 4, y + 3), (x + 4, y + h - 4), (x + 8, y + h // 2)], fill=self.bar_text)
            fg, out = self.bar_text, self.bar_out
        else:
            fg, out = self.text, self.text_out
        text(d, x + 12, y + 10, label, fg, F9, outline=out, shadow=self.text_sh if not selected else None)
        if right:
            text(d, x + w - 5, y + 10, right, fg, F9, outline=out, align="right")

    def button(self, d, x, y, letter, colour):
        d.ellipse((x, y, x + 9, y + 9), fill=colour, outline=(20, 14, 12))
        text(d, x + 5, y + 8, letter, (255, 255, 255), F8, anchor="ms")


def draw_menu(img, st, title, options, sel, x=None, y=5, w=112, hint=True, info=None):
    d = ImageDraw.Draw(img)
    x = 240 - w - 4 if x is None else x
    n = len(options) if options else len(info)
    h = 17 + n * 14 + (19 if hint else 5)
    top = st.card(d, x, y, w, h, title)
    if info:
        for i, line in enumerate(info):
            text(d, x + 8, top + 11 + i * 12, line, st.text, F9, outline=st.text_out, shadow=st.text_sh)
        ty = top + 3 + len(info) * 12
    else:
        for i, label in enumerate(options):
            st.row(d, x + 5, top + 2 + i * 14, w - 10, label, i == sel)
        ty = top + 2 + n * 14
    if hint:
        st.button(d, x + 7, ty + 3, "A", (70, 150, 70))
        text(d, x + 19, ty + 11, "OK" if info else "Choose", st.hint, F9, outline=st.text_out if st.name == "B" else None)
        if not info:
            st.button(d, x + 66, ty + 3, "B", (200, 70, 60))
            text(d, x + 78, ty + 11, "Back", st.hint, F9, outline=st.text_out if st.name == "B" else None)
    return img


def draw_hud(img, st):
    """HUD clock and money: bold text, gold money, same panel."""
    d = ImageDraw.Draw(img)
    d.rectangle((4, 132, 51, 144), fill=(40, 48, 88))
    d.rectangle((4, 148, 51, 157), fill=(40, 48, 88))
    text(d, 7, 143, "8:05", (255, 255, 255), F11, outline=(10, 12, 30))
    text(d, 7 + width("8:05", F11) + 3, 143, "am", (200, 210, 255), F8, outline=(10, 12, 30))
    text(d, 7, 156, "$20", (255, 214, 92), F11, outline=(10, 12, 30))
    return img


def draw_pause(img, st):
    d = ImageDraw.Draw(img)
    top = st.card(d, 4, 4, 232, 120, None)
    text(d, 12, 20, "Day 1", st.title_fg if st.name == "B" else st.text, F11, outline=st.text_out if st.name == "B" else None,
         shadow=st.text_sh)
    text(d, 62, 20, "8:05 am", st.text, F9, outline=st.text_out, shadow=st.text_sh)
    text(d, 116, 20, "$20", (255, 214, 92) if st.name == "B" else (150, 100, 10), F11, outline=st.text_out)
    needs = [("Hunger", 50), ("Energy", 50), ("Hygiene", 50), ("Fun", 50), ("Bladder", 50)]
    for i, (n, v) in enumerate(needs):
        yy = 36 + i * 13
        text(d, 12, yy + 8, n, st.text, F9, outline=st.text_out, shadow=st.text_sh)
        rrect(d, (58, yy, 112, yy + 8), 2, (30, 20, 20) if st.name == "A" else (8, 10, 24), (70, 50, 40) if st.name == "A" else (90, 110, 170))
        col = (240, 170, 40)
        rrect(d, (60, yy + 2, 60 + int(50 * v / 100), yy + 6), 1, col)
        text(d, 128, yy + 8, str(v), st.text, F9, outline=st.text_out, align="right")
    text(d, 12, 109, "Goal: Explore the city", st.hint if st.name == "B" else (110, 70, 50), F9, outline=None)
    for i, label in enumerate(["Resume", "Save game", "Quit to title"]):
        st.row(d, 138, 34 + i * 16, 92, label, i == 0, h=14)
    st.button(d, 144, 90, "A", (70, 150, 70))
    text(d, 156, 98, "OK", st.hint, F9, outline=st.text_out if st.name == "B" else None)
    st.button(d, 180, 90, "B", (200, 70, 60))
    text(d, 192, 98, "Back", st.hint, F9, outline=st.text_out if st.name == "B" else None)
    return img


def draw_dialog(img, st):
    d = ImageDraw.Draw(img)
    top = st.card(d, 14, 34, 212, 66, "Save game")
    text(d, 22, top + 12, "Overwrite saved game?", st.text, F9, outline=st.text_out, shadow=st.text_sh)
    st.row(d, 22, top + 20, 90, "Yes", True)
    st.row(d, 22, top + 35, 90, "No", False)
    return img


def draw_title(img, st):
    d = ImageDraw.Draw(img)
    # no HUD on the title: replace its strip by a mirrored piece of the view
    strip = img.crop((0, 96, 240, 128)).transpose(Image.FLIP_TOP_BOTTOM)
    img.paste(strip, (0, 128))
    shade = Image.new("RGB", img.size, (14, 18, 40) if st.name == "B" else (60, 40, 30))
    img.paste(Image.blend(img, shade, 0.62))
    d = ImageDraw.Draw(img)
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (2, 2), (-2, 2), (2, -2), (-2, -2)):
        d.fontmode = "1"
        d.text((120 + dx, 44 + dy), "TOWN LIFE", font=F20, fill=(20, 12, 30), anchor="ms")
    d.text((120, 46), "TOWN LIFE", font=F20, fill=(10, 8, 20), anchor="ms")
    d.text((120, 44), "TOWN LIFE", font=F20, fill=(255, 214, 92), anchor="ms")
    text(d, 120, 60, "A story of the city", (255, 255, 255), F9, outline=(14, 10, 24), anchor="ms")
    top = st.card(d, 64, 78, 112, 46, None)
    st.row(d, 69, 83, 102, "Continue", True)
    st.row(d, 69, 98, 102, "New Game", False)
    text(d, 120, 154, "build Nov 4 2026", (200, 200, 220), F8, outline=(14, 10, 24), anchor="ms")
    return img


def draw_dialogue_box(img, st, portrait):
    """Future dialogue box: 44 px at the bottom, portrait standing on it, gold name tag, 3 lines, A button,
    friendship meter (red bottom, green top) at the right edge."""
    d = ImageDraw.Draw(img)
    bx, by, bw, bh = 2, 112, 236, 46
    rrect(d, (bx + 2, by + 2, bx + bw + 1, by + bh + 1), 5, (10, 8, 16))
    rrect(d, (bx, by, bx + bw - 1, by + bh - 1), 5, st.panel, st.border, 2)
    rrect(d, (bx + 2, by + 2, bx + bw - 3, by + bh - 3), 3, None, st.edge, 1)
    # portrait standing on the box
    img.paste(portrait, (bx + 6, by - 46), portrait)
    d = ImageDraw.Draw(img)
    # name tag (gold)
    rrect(d, (bx + 74, by - 7, bx + 130, by + 8), 3, (250, 200, 64), (110, 66, 24))
    text(d, bx + 102, by + 5, "Mia", (50, 34, 30), F9, anchor="ms")
    lines = ["Fresh bread today!", "Only $2 a loaf.", "What'll it be?"]
    for i, ln in enumerate(lines):
        text(d, bx + 76, by + 20 + i * 11, ln, st.text, F9, outline=st.text_out, shadow=st.text_sh)
    st.button(d, bx + bw - 34, by + bh - 15, "A", (70, 150, 70))
    # friendship meter: vertical, red bottom -> green top, number above it
    mx, my, mh = bx + bw - 15, by + 13, 26
    rrect(d, (mx - 1, my - 1, mx + 7, my + mh + 1), 3, (20, 14, 12))
    fill = int(mh * 0.62)
    for k in range(mh):
        t = k / (mh - 1)
        col = (int(220 - 160 * t), int(60 + 150 * t), 60)
        if k < fill:
            d.line((mx + 1, my + mh - 1 - k, mx + 6, my + mh - 1 - k), fill=col)
    text(d, mx + 3, by + 11, "62", st.text, F8, outline=st.text_out if st.name == "B" else None, anchor="ms")
    return img


def a_cue(d, x, y, frame=0):
    """'You can interact' cue: round gold bubble with a tail and a hand-drawn pixel "A" (5x7), bobbing
    (frames 0..3 -> 0, -1, -2, -1 px). 15 px wide, fits one 16x16 sprite."""
    y -= (0, 1, 2, 1)[frame % 4]
    ink, gold = (40, 24, 12), (252, 206, 70)
    d.ellipse((x - 7, y - 17, x + 7, y - 3), fill=gold, outline=ink)
    d.polygon([(x - 3, y - 4), (x + 3, y - 4), (x, y)], fill=ink)
    d.polygon([(x - 2, y - 5), (x + 2, y - 5), (x, y - 2)], fill=gold)
    glyph = (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
    for gy, row in enumerate(glyph):
        for gx, c in enumerate(row):
            if c == "#":
                d.point((x - 2 + gx, y - 14 + gy), fill=ink)


def label(img, s, y=1):
    d = ImageDraw.Draw(img)
    d.rectangle((0, y - 1, 5 + width(s, F8), y + 8), fill=(0, 0, 0))
    d.fontmode = "1"
    d.text((3, y + 7), s, font=F8, fill=(255, 235, 120), anchor="ls")
    return img


def sheet(images, cols, scale, labels=None, pad=4, bg=(30, 30, 36)):
    w, h = images[0].size
    rows = (len(images) + cols - 1) // cols
    o = Image.new("RGB", (cols * (w * scale + pad) + pad, rows * (h * scale + pad) + pad), bg)
    for i, im in enumerate(images):
        o.paste(im.resize((w * scale, h * scale), Image.NEAREST), (pad + (i % cols) * (w * scale + pad), pad + (i // cols) * (h * scale + pad)))
    return o


def main():
    bg_dir, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)

    def load(n):
        return Image.open(os.path.join(bg_dir, n)).convert("RGB")

    park, cc, market = load("park.png"), load("cc.png"), load("market.png")
    mia = Image.open("/home/user/Town-Life/graphics/npc_mia.bmp").convert("RGB")
    # portrait placeholder: head and shoulders of the first (south) idle frame, 2x
    fr = mia.crop((0, 0, 32, 64))
    fr = fr.crop((4, 6, 28, 34)).resize((48, 56), Image.NEAREST)
    pm = Image.new("RGBA", fr.size)
    for yy in range(fr.height):
        for xx in range(fr.width):
            p = fr.getpixel((xx, yy))
            pm.putpixel((xx, yy), (0, 0, 0, 0) if p == (255, 0, 255) else p + (255,))
    shots = {}
    for st_name in "AB":
        st = Style(st_name)
        sc = {}
        sc["bench menu"] = draw_menu(draw_hud(park.copy(), st), st, "Park Bench", ["Sit", "Sleep"], 0)
        sc["shop (4 rows, no scrolling)"] = draw_menu(draw_hud(market.copy(), st), st, "Corner Market",
                                                      ["Bread $2", "Apple $1", "Ready meal $5", "Soda $1"], 2, w=120)
        sc["info message"] = draw_menu(draw_hud(cc.copy(), st), st, "Notice board", None, 0,
                                       info=["No jobs posted", "yet. Check", "back soon!"])
        sc["pause screen"] = draw_pause(draw_hud(cc.copy(), st), st)
        sc["dialog"] = draw_dialog(draw_hud(cc.copy(), st), st)
        sc["title screen"] = draw_title(park.copy(), st)
        sc["dialogue box (future)"] = draw_dialogue_box(draw_hud(market.copy(), st), st, pm)
        shots[st_name] = sc
        for k, im in sc.items():
            im.save(os.path.join(out, f"ui_{st_name}_{k.split(' ')[0]}.png"))
    cur = {"bench menu": "cur_menu.png", "shop (4 rows, no scrolling)": "cur_shop.png", "info message": "cur_info.png",
           "pause screen": "cur_pause.png", "dialog": "cur_dialog.png", "title screen": "cur_title.png"}
    names = list(shots["A"].keys())
    # sheet 1: variants A | B, one row per element (2x)
    rows = []
    for k in names:
        rows.append(sheet([label(shots["A"][k].copy(), "A  Paper: " + k), label(shots["B"][k].copy(), "B  Night: " + k)], 2, 2))
    W = max(r.width for r in rows)
    o = Image.new("RGB", (W, sum(r.height for r in rows)), (30, 30, 36))
    y = 0
    for r in rows:
        o.paste(r, (0, y))
        y += r.height
    o.save(os.path.join(out, "ui_proposal.png"))
    print("ui_proposal.png", o.size)
    # sheet 2: current vs proposed (A and B), 2x, only elements that exist today
    rows = []
    for k in names:
        if k in cur and os.path.exists(os.path.join(bg_dir, cur[k])):
            rows.append(sheet([label(load(cur[k]), "CURRENT: " + k), label(shots["A"][k].copy(), "A  Paper"),
                               label(shots["B"][k].copy(), "B  Night")], 3, 1))
    W = max(r.width for r in rows)
    # 1x triplets are small: stack them at 2x
    big = [r.resize((r.width * 2 // 1, r.height * 2 // 1), Image.NEAREST) for r in rows]
    o = Image.new("RGB", (max(r.width for r in big), sum(r.height for r in big)), (30, 30, 36))
    y = 0
    for r in big:
        o.paste(r, (0, y))
        y += r.height
    o.save(os.path.join(out, "ui_compare.png"))
    print("ui_compare.png", o.size)
    # sheet 3: text sharpness, current vs proposed, 4x crops of the menu rows
    c = load("cur_shop.png").crop((112, 2, 240, 74)).resize((384, 216), Image.NEAREST)
    pa = shots["A"]["shop (4 rows, no scrolling)"].crop((112, 2, 240, 74)).resize((384, 216), Image.NEAREST)
    pb = shots["B"]["shop (4 rows, no scrolling)"].crop((112, 2, 240, 74)).resize((384, 216), Image.NEAREST)
    o = Image.new("RGB", (388 * 3, 220), (30, 30, 36))
    for i, (im, nm) in enumerate(((c, "CURRENT 8x8 font"), (pa, "A  bold 9 px"), (pb, "B  bold 9 px + outline"))):
        o.paste(label(im.copy(), nm, 2), (i * 388, 0))
    o.save(os.path.join(out, "ui_text_zoom.png"))


if __name__ == "__main__":
    main()
