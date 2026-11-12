"""
s75 post-processing (nothing in the game is touched): quantize the renders like the game does and compose the deliverables.

  python3 res_post.py OUT sprites     quantized frames -> OUT/spr/<name>_<stem>.png (RGBA, 1x)
  python3 res_post.py OUT lineup      OUT/lineup_3x.png   (new residents + Mia + Big Lou for scale)
  python3 res_post.py OUT mock CROP.png   OUT/mock_1x.png, OUT/mock_3x.png (CROP = 240x128 Old Block window from s74 crop.py)
Humans use the real face pass (tools/face_pass.py: 11 colours + eye white / mouth / blush + outline); TRENCH-E / critters use plain k-means.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(TOOLS, ".."))
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TOOLS, "proposals", "s74"))
import res_build  # noqa: E402

res_build.inject()
import face_pass as fp  # noqa: E402
import json  # noqa: E402

OUT = os.path.abspath(sys.argv[1])
STEP = sys.argv[2]
SS = 4
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FACINGS = ["s", "se", "e"]
HUMAN_STEMS = [f + "_0" for f in FACINGS] + ["se_w0"]


def sprite_frame(path, ss, w, h):
    img = np.asarray(Image.open(path).convert("RGBA")).astype(np.float64) / 255.0
    img[..., :3] *= img[..., 3:4]
    img = img.reshape(h, ss, w, ss, 4).mean(axis=(1, 3))
    rgb = np.where(img[..., 3:4] > 0, img[..., :3] / np.maximum(img[..., 3:4], 1e-6), 0) * 255
    alpha = img[..., 3] >= 0.45
    grown = alpha.copy()
    grown[1:, :] |= alpha[:-1, :]; grown[:-1, :] |= alpha[1:, :]
    grown[:, 1:] |= alpha[:, :-1]; grown[:, :-1] |= alpha[:, 1:]
    edge = grown & ~alpha
    rgb[edge] = [40.0, 30.0, 40.0]
    return rgb, alpha | edge


def to_rgba(pal, idx):
    out = np.zeros(idx.shape + (4,), np.uint8)
    out[..., :3] = pal[idx].astype(np.uint8)
    out[..., 3] = np.where(idx > 0, 255, 0)
    return Image.fromarray(out)


def save(name, stem, pal, idx):
    os.makedirs(os.path.join(OUT, "spr"), exist_ok=True)
    to_rgba(pal, idx).save(os.path.join(OUT, "spr", f"{name}_{stem}.png"))


def sprites():
    for n in res_build.ORDER:
        d = os.path.join(OUT, "r_" + n)
        frames = [sprite_frame(os.path.join(d, s + ".png"), SS, 32, 64) for s in HUMAN_STEMS]
        skin = res_build.B[n]["colours"]["Skin"]
        pal, idxs = fp.quantize_sheet(frames, fp.reserved_colours(n, skin))
        ctx = fp.make_ctx(pal, n, skin)
        anchors = json.load(open(os.path.join(d, "anchors.json")))
        for st, idx in zip(HUMAN_STEMS, idxs):
            fp.paint_face(idx, anchors[st], ctx, st.split("_")[0])
            save(n, st, pal, idx)
    # primitives: robot (64x64), duchess / captain (32x32)
    jobs = [("robot", 64, 64, [f"{f}_{fr}" for fr in ("idle", "dig_up", "dig_down") for f in FACINGS]),
            ("duchess", 32, 32, [f"e_{fr}" for fr in ("stand", "walkA", "walkB", "sit")]),
            ("captain", 32, 32, ["e_perch", "e_flap"])]
    for n, w, h, stems in jobs:
        frames = [sprite_frame(os.path.join(OUT, "r_" + n, s + ".png"), 8, w, h) for s in stems]
        px = np.concatenate([rgb[a & (rgb != np.array([40.0, 30.0, 40.0])).any(-1)] for rgb, a in frames]) * fp.WEIGHT
        cols = fp.to5(fp.kmeans(px, 14, iters=15) / fp.WEIGHT)
        pal = np.zeros((16, 3)); pal[0] = (255, 0, 255); pal[1:15] = cols; pal[15] = fp.OUTLINE
        cw = pal[1:] * fp.WEIGHT
        for st, (rgb, a) in zip(stems, frames):
            d2 = ((rgb[..., None, :] * fp.WEIGHT - cw[None, None]) ** 2).sum(3)
            idx = (d2.argmin(2) + 1).astype(np.uint8)
            idx[~a] = 0
            save(n, st, pal, idx)


def existing(name, facing, k):
    """frame k (0 idle, 1.. walk) of a shipped cast sheet graphics/npc_<name>.bmp (13 frames per facing)."""
    order = dict(s=0, sw=1, w=2, nw=3, n=4, ne=5, e=6, se=7)
    im = Image.open(os.path.join(ROOT, "graphics", f"npc_{name}.bmp"))
    ix = np.array(im); rgba = np.array(im.convert("RGBA")); rgba[ix == 0] = (0, 0, 0, 0)
    n = order[facing] * 13 + k
    return Image.fromarray(rgba).crop((0, n * 64, 32, n * 64 + 64))


def load(name, stem):
    return Image.open(os.path.join(OUT, "spr", f"{name}_{stem}.png"))


def lineup():
    sprites_ok = os.path.exists(os.path.join(OUT, "spr"))
    assert sprites_ok
    Z = 3
    W, H = 2560, 2 * 230 + 20
    sheet = Image.new("RGB", (W, H), (150, 158, 146))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(FONT, 14)
    ground = (128, 136, 124)

    def cell(img, x, y, wpx, hpx, feet):
        im = img.resize((img.width * Z, img.height * Z), Image.NEAREST)
        sheet.paste(im, (x, y + hpx * Z - feet * Z - 0), im)

    def row(items, y):
        x = 8
        for label, cells in items:
            w0 = x
            for (img, feet) in cells:
                fw = img.width * Z
                cell(img, x, y + 18, img.width, 64, 54 if img.height == 64 and img.width == 32 else feet)
                x += fw
            d.text((w0 + 4, y), label, font=f, fill=(20, 24, 30))
            x += 20
    def humans(n):
        return [(load(n, s), 54) for s in HUMAN_STEMS]
    def old(n):
        return [(existing(n, "s", 0), 54), (existing(n, "se", 0), 54), (existing(n, "e", 0), 54), (existing(n, "se", 4), 54)]
    row([("Mia (existing)", old("mia")), ("Big Lou (existing)", old("lou")), ("Ines", humans("ines")), ("Teo", humans("teo")),
         ("Nella (bakery)", humans("nella")), ("Mrs. Valdez", humans("valdez"))], 0)
    # second row: sprites that are not 32x64
    y = 230
    x = 8
    for label, cells in [("Grigor", humans("grigor")), ("Guard Pruitt", humans("pruitt")), ("Kessler", humans("kessler"))]:
        d.text((x + 4, y), label, font=f, fill=(20, 24, 30))
        for img, feet in cells:
            cell(img, x, y + 18, 32, 64, 54); x += 96
        x += 20
    d.text((x + 4, y), "TRENCH-E 3 (64x64: s, se, e, dig)", font=f, fill=(20, 24, 30))
    for st in ("s_idle", "se_idle", "e_idle", "se_dig_up"):
        img = load("robot", st); im = img.resize((64 * 2, 64 * 2), Image.NEAREST)   # shown at 2x to fit
        sheet.paste(im, (x, y + 18 + 64 * Z - 50 * 2 - 0 - 64 * 2 + 50 * 2 - 40), im); x += 128
    x += 20
    d.text((x + 4, y), "Duchess / Captain (32x32)", font=f, fill=(20, 24, 30))
    for st, nm in [("stand", "duchess"), ("walkA", "duchess"), ("sit", "duchess"), ("perch", "captain")]:
        img = load(nm, "e_" + st); im = img.resize((96, 96), Image.NEAREST)
        sheet.paste(im, (x, y + 18 + 192 - 96 - 10), im); x += 96
    sheet.crop((0, 0, 2440, H)).save(os.path.join(OUT, "lineup_3x.png"))


def mock(crop_png):
    import mock as m
    left, top = m.window(31.0, 22.0)
    q = Image.open(crop_png).convert("RGB")
    scr = Image.new("RGBA", (240, 160), (6, 6, 12, 255))
    scr.paste(q.crop((0, 0, 240, 128)).convert("RGBA"), (0, 0))
    d = ImageDraw.Draw(scr, "RGBA")
    acts = [(32.9, 19.9, "ines_se", "h"), (27.5, 23.6, "teo_e", "h"), (35.6, 22.3, "duchess_e_walkA", "d"), (31.0, 22.0, "player", "p")]
    for (x, y, key, kind) in sorted(acts, key=lambda a: a[0] + a[1]):
        ix, iy = m.proj(x, y)
        sx, sy = int(round(ix)) - left, int(round(iy)) - top
        d.ellipse((sx - 9, sy - 3, sx + 9, sy + 3), fill=(0, 0, 0, 90))
        if kind == "p":
            scr.alpha_composite(m.sheet_frame("player", "ne", 18), (sx - 16, sy - 54))
        elif kind == "h":
            nm, st = key.split("_")
            scr.alpha_composite(load(nm, st + "_0"), (sx - 16, sy - 54))
        else:
            img = load("duchess", "e_walkA").transpose(Image.FLIP_LEFT_RIGHT)
            scr.alpha_composite(img, (sx - 16, sy - 23))
    scr = scr.convert("RGB")
    scr.paste(m.hud_strip(), (0, 128))
    scr.save(os.path.join(OUT, "mock_1x.png"))
    scr.resize((720, 480), Image.NEAREST).save(os.path.join(OUT, "mock_3x.png"))


if STEP == "sprites":
    sprites()
elif STEP == "lineup":
    lineup()
elif STEP == "mock":
    mock(sys.argv[3])
