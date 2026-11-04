#!/usr/bin/env python3
"""Dialogue layout mocks with the new big portraits (own layouts, Paper style from tools/proposals/ui_objects/ui_mock.py).
  python3 mock55.py   -> /tmp/claude-0/s55/dlg_*.png"""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, "/tmp/claude-0/s55/tools/proposals/ui_objects")
import ui_mock as um
P = "/tmp/claude-0/s55/keep/por"
OUT = "/tmp/claude-0/s55"
ST = um.Style("A")
NAME = {"player": "Sam", "mia": "Mia", "rosa": "Rosa", "victor": "Victor Vault"}


def portrait(c, e, size=128, flip=False, pre="q2"):
    im = Image.open(f"{P}/{pre}_{128 if size >= 112 else 96}_{c}_{e}.png").convert("RGBA")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im


def wrap(s, maxw):
    out, cur = [], ""
    for w in s.split(" "):
        n = (cur + " " + w).strip()
        if um.width(n) <= maxw:
            cur = n
        else:
            out.append(cur); cur = w
    out.append(cur)
    return out


def meter(img, d, x, y, h, val, label_y=None):
    um.rrect(d, (x - 1, y - 1, x + 7, y + h + 1), 3, (20, 14, 12))
    fill = int(h * val / 100)
    for k in range(h):
        t = k / (h - 1)
        col = (int(220 - 160 * t), int(60 + 150 * t), 60)
        if k < fill:
            d.line((x + 1, y + h - 1 - k, x + 6, y + h - 1 - k), fill=col)
    um.text(d, x + 3, (label_y if label_y is not None else y - 3), str(val), ST.text, um.F8, anchor="ms", outline=(255, 250, 232))


def tag(d, x, y, w, name):
    um.rrect(d, (x, y, x + w, y + 14), 3, (200, 72, 48), (70, 40, 30), 1)
    um.text(d, x + w // 2, y + 11, name, (255, 232, 140), um.F9, anchor="ms", outline=(96, 28, 20))


def layout1(bg, c, e, lines, val=62):
    """Portrait 128x128 stands in front of the box at the left (bottom flush with the screen), name tag + 4 text lines to the right, meter at the right edge."""
    img = bg.convert("RGBA").copy()
    d = ImageDraw.Draw(img)
    bx, by, bw, bh = 2, 106, 236, 50
    um.rrect(d, (bx + 2, by + 2, bx + bw + 1, by + bh + 1), 5, (10, 8, 16))
    um.rrect(d, (bx, by, bx + bw - 1, by + bh - 1), 5, ST.panel, ST.border, 2)
    um.rrect(d, (bx + 2, by + 2, bx + bw - 3, by + bh - 3), 3, None, ST.edge, 1)
    img.alpha_composite(portrait(c, e), (-14, 30), ) if False else img.alpha_composite(portrait(c, e).crop((14, 0, 128, 128)), (0, 30))
    d = ImageDraw.Draw(img)
    tag(d, 118, by - 7, 62 if len(NAME[c]) < 6 else 86, NAME[c])
    tx = 116
    for i, ln in enumerate(wrap(lines, 106)[:4]):
        um.text(d, tx, by + 13 + i * 10, ln, ST.text, um.F9, shadow=ST.text_sh)
    meter(img, d, 224, by + 12, 28, val)
    ST.button(d, 210, by + bh - 14, "A", (70, 150, 70))
    return img.convert("RGB")


def layout2(bg, c, e, question, choices, sel=0, val=62, small=True):
    """NPC portrait (96x96, mirrored to face the text) stands at the right of a lower box, tall meter between text and portrait, choices on the left."""
    img = bg.convert("RGBA").copy()
    d = ImageDraw.Draw(img)
    bx, by, bw, bh = 2, 94, 236, 62
    um.rrect(d, (bx + 2, by + 2, bx + bw + 1, by + bh + 1), 5, (10, 8, 16))
    um.rrect(d, (bx, by, bx + bw - 1, by + bh - 1), 5, ST.panel, ST.border, 2)
    um.rrect(d, (bx + 2, by + 2, bx + bw - 3, by + bh - 3), 3, None, ST.edge, 1)
    img.alpha_composite(portrait(c, e, 96, flip=True), (142, 62))
    d = ImageDraw.Draw(img)
    tag(d, 8, by - 7, 62 if len(NAME[c]) < 6 else 86, NAME[c])
    um.text(d, 9, by + 15, question, ST.text, um.F9, shadow=ST.text_sh)
    for i, ch in enumerate(choices):
        ST.row(d, 7, by + 19 + i * 13, 122, ch, i == sel, h=12)
    meter(img, d, 132, 66, 74, val, label_y=62)
    ST.button(d, 126 - 0, by + bh - 4 - 8, "A", (70, 150, 70)) if False else None
    return img.convert("RGB")


def patched(path):
    im = Image.open(path).convert("RGB")
    im.paste(im.crop((0, 44, 240, 58)), (0, 0))
    return im


if __name__ == "__main__":
    bgs = {"street": patched("/tmp/claude-0/s53/b0.png"), "room": Image.open(f"/tmp/claude-0/s55/mock_bg_room.png").convert("RGB") if os.path.exists("/tmp/claude-0/s55/mock_bg_room.png") else patched("/tmp/claude-0/s53/S9.png")}
    texts = {"mia": ("happy", "Good morning, Sam! The coffee is on and the gossip is hot. Want a bun?"),
             "player": ("neutral", "I need a job, Rosa. Anything at all, I can start today."),
             "rosa": ("sad", "Oh dear. Victor's men were here again asking about the old block."),
             "victor": ("angry", "Smart City will happen, boy. Old Block is already a pile of bricks!")}
    for k, bgn in (("street", "street"), ("room", "room")):
        ims = [layout1(bgs[bgn], c, texts[c][0], texts[c][1], v) for c, v in (("mia", 62), ("player", 40), ("rosa", 78), ("victor", 12))]
        W, H = 240 * 3, 160 * 3
        sheet = Image.new("RGB", (W * 2 + 12, H * 2 + 12), (20, 20, 30))
        for i, im in enumerate(ims):
            sheet.paste(im.resize((W, H), Image.NEAREST), ((i % 2) * (W + 12), (i // 2) * (H + 12)))
        sheet.save(f"{OUT}/dlg_layout1_{k}.png")
        for i, im in enumerate(ims):
            im.save(f"{OUT}/individual/dlg1_{k}_{i}.png") if os.path.isdir(f"{OUT}/individual") else None
    ch = {"mia": ["Sure, I'll do it.", "What's it pay?", "Not today, sorry."], "victor": ["You can't buy it.", "Is that a threat?", "..."]}
    ims = [layout2(bgs["street"], "mia", "happy", "Can you cover my shift?", ch["mia"], 1, 62),
           layout2(bgs["street"], "victor", "angry", "Old Block is mine now.", ch["victor"], 0, 12),
           layout2(bgs["room"], "rosa", "happy", "More tea, dear?", ["Yes please, Rosa.", "About Old Block?", "I should go."], 1, 78),
           layout2(bgs["room"], "player", "sad", "You look tired, Sam.", ["I lost my job.", "I'm fine, thanks.", "Just a long night."], 0, 40)]
    sheet = Image.new("RGB", (W * 2 + 12, H * 2 + 12), (20, 20, 30))
    for i, im in enumerate(ims):
        sheet.paste(im.resize((W, H), Image.NEAREST), ((i % 2) * (W + 12), (i // 2) * (H + 12)))
    sheet.save(f"{OUT}/dlg_layout2.png")
    print("ok")
