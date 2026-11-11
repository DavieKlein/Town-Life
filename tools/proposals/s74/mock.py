"""In-game mock of Old Block: a 240x160 screen (viewport 240x128 + the real HUD strip from graphics/hud.bmp), the real player sprite
(graphics/player.bmp) and a placeholder resident (Mia's sprite stands in for Ines / Teo, which do not exist yet).
  python3 mock.py CROP_PREFIX OUT.png [px py facing]    CROP_PREFIX = a crop.py output whose box is exactly the camera window
  Camera window for a player at (px, py): left = ix - 120, top = iy - 76 (ix, iy = image coords of the player's feet).
  python3 mock.py --window px py     prints the crop box to render."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GFX = os.path.join(ROOT, "graphics")
OX0, OY0 = 60 * 0 + 48 * 16 + 16, 175          # origin of the proposed old_block scene (H * 16 + 16, 175)
FACE = dict(s=0, sw=1, w=2, nw=3, n=4, ne=5, e=6, se=7)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def proj(x, y):
    return OX0 + (x - y) * 16, OY0 + (x + y) * 8


def window(px, py):
    ix, iy = proj(px, py)
    return int(round(ix)) - 120, int(round(iy)) - 76


def sheet_frame(name, facing, per, idx=0, h=64):
    im = Image.open(os.path.join(GFX, name + ".bmp"))
    idxs = np.array(im)
    rgba = np.array(im.convert("RGBA"))
    rgba[idxs == 0] = (0, 0, 0, 0)
    n = FACE[facing] * per + idx
    return Image.fromarray(rgba).crop((0, n * h, 32, n * h + h))


def hud_strip():
    im = Image.open(os.path.join(GFX, "hud.bmp")).convert("RGB").crop((0, 176, 240, 208))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 11)
    d.text((8, 5), "8:20", font=f, fill=(236, 230, 210))
    d.text((8, 17), "$38", font=f, fill=(240, 200, 70))
    bars = bars_sheet()
    for i, lvl in enumerate((14, 10, 12, 9, 13, 8)):
        b = bars[lvl]
        im.paste(b, (62 + 30 * i - 2, 19), b)
    return im


def bars_sheet():
    im = Image.open(os.path.join(GFX, "hud_bar.bmp"))
    idxs = np.array(im)
    rgba = np.array(im.convert("RGBA"))
    rgba[idxs == 0] = (0, 0, 0, 0)
    full = Image.fromarray(rgba)
    return [full.crop((0, k * 8, 32, k * 8 + 8)) for k in range(16)]


def make(crop_png, out, actors):
    q = Image.open(crop_png).convert("RGB")
    scr = Image.new("RGBA", (240, 160), (6, 6, 12, 255))
    scr.paste(q.crop((0, 0, 240, 128)).convert("RGBA"), (0, 0))
    left, top = window(actors[-1][0], actors[-1][1])
    d = ImageDraw.Draw(scr, "RGBA")
    for (x, y, facing, sheet, per) in sorted(actors, key=lambda a: a[0] + a[1]):
        ix, iy = proj(x, y)
        sx, sy = int(round(ix)) - left, int(round(iy)) - top
        d.ellipse((sx - 9, sy - 3, sx + 9, sy + 3), fill=(0, 0, 0, 90))
        scr.alpha_composite(sheet_frame(sheet, facing, per), (sx - 16, sy - 54))
    scr = scr.convert("RGB")
    scr.paste(hud_strip(), (0, 128))
    # "A" cue bubble over the laundromat door is drawn by the engine; here a small gold marker as a stand-in
    big = Image.new("RGB", (240 + 6 + 720, 480), (24, 26, 34))
    big.paste(scr, (0, 0))
    big.paste(scr.resize((720, 480), Image.NEAREST), (246, 0))
    big.save(out)
    scr.save(out.replace(".png", "_1x.png"))
    print("saved", out)


if __name__ == "__main__":
    if sys.argv[1] == "--window":
        l, t = window(float(sys.argv[2]), float(sys.argv[3]))
        print(f"{l},{t},{l + 240},{t + 128}")
    else:
        prefix, out = sys.argv[1], sys.argv[2]
        pl = (float(sys.argv[3]), float(sys.argv[4]), sys.argv[5])
        npc = (float(sys.argv[6]), float(sys.argv[7]), sys.argv[8]) if len(sys.argv) > 8 else None
        acts = []
        if npc:
            acts.append((npc[0], npc[1], npc[2], "npc_mia", 13))
        acts.append((pl[0], pl[1], pl[2], "player", 18))
        make(prefix + ".png", out, acts)
