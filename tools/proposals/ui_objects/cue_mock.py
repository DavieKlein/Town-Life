#!/usr/bin/env python3
"""'You can interact' cue mock-up (owner feedback D): a small bobbing A bubble above the nearest interactable
in reach. Takes headless screenshots with the player standing in reach of each object (tools/headless_run.py +
make_save.py), draws the cue (4 bob frames) and writes interact_cue.png.   python3 cue_mock.py ROM OUT_DIR"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_mock as ui

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
# name, map, object x, y (cells), player x, y (in reach), cue height above the object's ground point (px)
CASES = [
    ("Park bench", "city_centre", 7.3, 39.4, 7.3, 40.9, 22),
    ("Street bin", "city_centre", 5.0, 21.1, 5.0, 22.2, 40),
    ("Fountain", "city_centre", 53.0, 41.0, 53.0, 44.2, 36),
    ("Public sink", "public_toilet", 1.0, 3.4, 1.8, 3.4, 40),
    ("Diner counter", "diner", 6.4, 4.5, 6.4, 5.6, 38),
    ("Library shelf", "community_centre", 4.7, 1.0, 4.7, 2.1, 46),
]


def player_feet(a):
    mask = np.zeros(a.shape[:2], bool)
    for c in ((80, 120, 216), (72, 112, 200), (64, 96, 176), (56, 80, 152)):
        mask |= (a == np.array(c)).all(2)
    mask[128:] = False
    c = np.pad(np.cumsum(np.cumsum(mask.astype(int), 0), 1), ((1, 0), (1, 0)))
    dens = np.pad(c[24:, 24:] - c[:-24, 24:] - c[24:, :-24] + c[:-24, :-24], ((12, 12), (12, 12)))
    cy, cx = np.unravel_index(dens.argmax(), dens.shape)
    ys, xs = np.nonzero(mask[max(0, cy - 14):cy + 15, max(0, cx - 14):cx + 15])
    return int(xs.mean()) + max(0, cx - 14), int(ys.min()) + max(0, cy - 14) + 40


def main():
    rom, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    tiles = []
    for i, (name, m, ox, oy, px, py, hh) in enumerate(CASES):
        sav = os.path.join(out, f"cue{i}.sav")
        subprocess.run(["python3", os.path.join(HERE, "make_save.py"), sav, m, str(px), str(py), "0", "480", "50"], check=True)
        shot = os.path.join(out, f"cue{i}.png")
        subprocess.run(["python3", os.path.join(ROOT, "tools", "headless_run.py"), rom,
                        f"loadsram {sav}; reset; wait 100; press a; wait 330; shot {shot}"], stdout=subprocess.DEVNULL, cwd=ROOT)
        im = Image.open(shot).convert("RGB")
        fx, fy = player_feet(np.asarray(im).astype(int))
        dx, dy = (ox - px) * 16, (oy - py) * 16
        sx, sy = fx + (dx - dy), fy + (dx + dy) / 2
        frames = []
        for f in range(2):
            fr = im.copy()
            ui.a_cue(ImageDraw.Draw(fr), int(sx), int(sy) - hh, f * 2)
            # crop around the object
            cx, cy = int(sx), int(sy) - int(hh * 0.55)
            c = Image.new("RGB", (120, 90))
            c.paste(fr.crop((0, 0, 240, 128)), (60 - cx, 45 - cy))
            frames.append(c)
        tiles.append(ui.label(frames[0], name))
    S = 3
    o = Image.new("RGB", (3 * (120 * S + 4) + 4, 2 * (90 * S + 4) + 4), (30, 30, 36))
    for i, t in enumerate(tiles):
        o.paste(t.resize((120 * S, 90 * S), Image.NEAREST), (4 + (i % 3) * (120 * S + 4), 4 + (i // 3) * (90 * S + 4)))
    # bobbing strip: the 4 frames, large
    strip = Image.new("RGB", (4 * 64, 66), (60, 120, 60))
    for f in range(4):
        t = Image.new("RGB", (20, 22), (60, 120, 60))
        ui.a_cue(ImageDraw.Draw(t), 10, 20, f)
        strip.paste(t.resize((60, 66), Image.NEAREST), (f * 64, 0))
    o2 = Image.new("RGB", (o.width, o.height + 76), (30, 30, 36))
    o2.paste(o, (0, 0))
    o2.paste(strip, (8, o.height + 6))
    d = ImageDraw.Draw(o2)
    d.fontmode = "1"
    d.text((276, o.height + 28), "bob: 0, -1, -2, -1 px (4 frames, 8 frames each), sprite 16x16, shown only for the", font=ui.F9, fill=(255, 235, 120))
    d.text((276, o.height + 42), "nearest object in reach; hidden while a menu or an activity is running.", font=ui.F9, fill=(255, 235, 120))
    o2.save(os.path.join(out, "interact_cue.png"))
    print("interact_cue.png", o2.size)


if __name__ == "__main__":
    main()
