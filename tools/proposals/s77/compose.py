"""Renders proposal crops with the REAL renderer, runs the REAL quantizer (build_assets.convert_layer: 8 floor / 7 object banks, graded + sharpened like
the game) and composites the real player / Teo sprites and the real HUD strip, so the previews look like the game screen.

  python3 compose.py shots OUTDIR [name ...]     renders + builds the named shots (default: all)
Shots are defined in SHOTS at the bottom.  Samples: env S77_SPP (default 96; the final run uses 192)."""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(TOOLS, ".."))
GFX = os.path.join(ROOT, "graphics")
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(HERE, "..", "s49"))
import build_assets as ba  # noqa: E402
import lib  # noqa: E402

FACE = dict(s=0, sw=1, w=2, nw=3, n=4, ne=5, e=6, se=7)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SPP = os.environ.get("S77_SPP", "96")

# scene origins (image px of world (0, 0)); ix = ox + (x - y) * 16, iy = oy + (x + y) * 8 - z * 26.1
ORIGIN = {"city_centre": (976, 200), "cc_a": (976, 200), "cc_b": (976, 200), "old_block": (1040, 175), "ob_open": (1040, 175),
          "ob_closed": (1040, 175), "sewer": (9 * 16 + 24, 215)}
SIZE = {"sewer": (640, 568)}


def proj(ident, x, y, z=0.0):
    ox, oy = ORIGIN[ident]
    return ox + (x - y) * 16, oy + (x + y) * 8 - z * 26.1


def render(ident, box, prefix):
    """Both layers of a crop (image px x0,y0,x1,y1), cached on disk."""
    ps = []
    for layer in ("floor", "objects"):
        f = f"{prefix}_{layer}.png"
        if not os.path.exists(f):
            ps.append(subprocess.Popen(["blender", "-b", "-noaudio", "--python", os.path.join(HERE, "render.py"), "--", ident, layer, f, "2", SPP, box],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    for p in ps:
        p.wait()


def quantize(prefix):
    """Floor + objects through the real quantizer, composited like the game screen (RGB PIL image)."""
    res = {}
    for layer, banks, tr in (("floor", 8, False), ("objects", 7, True)):
        im = ba.grade(ba.sharpen(lib.down(Image.open(f"{prefix}_{layer}.png"))))
        pal, cells, tiles, info = ba.convert_layer(im, banks, tr, None, layer)
        res[layer] = (ba.layer_preview(pal, cells, tiles), info["drawn"])
    comp = res["floor"][0].copy()
    d = res["objects"][1]
    comp[d] = res["objects"][0][d]
    return Image.fromarray(comp)


def sheet_frame(name, facing, per, idx=0, w=32, h=64):
    im = Image.open(os.path.join(GFX, name + ".bmp"))
    idxs = np.array(im)
    rgba = np.array(im.convert("RGBA"))
    rgba[idxs == 0] = (0, 0, 0, 0)
    n = FACE[facing] * per + idx
    return Image.fromarray(rgba).crop((0, n * h, w, n * h + h))


def hud_strip():
    im = Image.open(os.path.join(GFX, "hud.bmp")).convert("RGB").crop((0, 176, 240, 208))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 11)
    d.text((8, 5), "11:52", font=f, fill=(236, 230, 210))
    d.text((8, 17), "$41", font=f, fill=(240, 200, 70))
    bi = Image.open(os.path.join(GFX, "hud_bar.bmp"))
    idxs = np.array(bi)
    rgba = np.array(bi.convert("RGBA"))
    rgba[idxs == 0] = (0, 0, 0, 0)
    full = Image.fromarray(rgba)
    for i, lvl in enumerate((12, 9, 10, 11, 13, 8)):
        b = full.crop((0, lvl * 8, 32, lvl * 8 + 8))
        im.paste(b, (62 + 30 * i - 2, 19), b)
    return im


def cue(scr, sx, sy):
    """The gold 'A' cue bubble (ui_icons frame 2)."""
    im = Image.open(os.path.join(GFX, "ui_icons.bmp"))
    idxs = np.array(im)
    rgba = np.array(im.convert("RGBA"))
    rgba[idxs == 0] = (0, 0, 0, 0)
    f = Image.fromarray(rgba).crop((0, 32, 16, 48))
    scr.alpha_composite(f, (sx - 8, sy - 16))


def screen(ident, q, left, top, actors, cue_at=None, hud=True, clip=None, qorigin=(0, 0)):
    """240x160 game screen: the 240x128 viewport at (left, top) of the quantized image q (image px), actors = [(x, y, z, facing, sheet, per, idx, w, kind)],
    sorted by depth. kind 'shadow' draws the blob. clip = {actor index: pixels of the sprite's lower part to hide (descending into a hole)}."""
    scr = Image.new("RGBA", (240, 160), (6, 6, 12, 255))
    scr.paste(q.crop((left, top, left + 240, top + 128)).convert("RGBA"), (0, 0))
    d = ImageDraw.Draw(scr, "RGBA")
    for i, a in sorted(enumerate(actors), key=lambda t: t[1][0] + t[1][1]):
        x, y, z, facing, sheet, per, idx, w = a[:8]
        ix, iy = proj(ident, x, y, z)
        sx, sy = int(round(ix)) - left, int(round(iy)) - top
        d.ellipse((sx - 9, sy - 3, sx + 9, sy + 3), fill=(0, 0, 0, 90))
        fr = sheet_frame(sheet, facing, per, idx, w=w)
        if clip and i in clip:
            keep = max(0, 64 - clip[i])
            fr = fr.crop((0, 0, fr.width, keep))
        scr.alpha_composite(fr, (sx - w // 2, sy - 54))
    if cue_at:
        ix, iy = proj(ident, *cue_at)
        cue(scr, int(round(ix)) - left, int(round(iy)) - top - 18)
    scr = scr.convert("RGB")
    if hud:
        scr.paste(hud_strip(), (0, 128))
    return scr


def window_for(ident, px, py, qsize):
    ix, iy = proj(ident, px, py)
    left = int(round(ix)) - 120
    top = int(round(iy)) - 76
    left = max(0, min(left, qsize[0] - 240))
    top = max(0, min(top, qsize[1] - 128))
    return left, top


P = dict(player=("player", 18, 32), teo=("npc_teo", 13, 32))


def actor(kind, x, y, facing, idx=0, z=0.0):
    sheet, per, w = P[kind]
    return (x, y, z, facing, sheet, per, idx, w)


def shot(out, ident, px, py, actors, cue_at=None, samples=None, name=None, clip=None, hud=True):
    """Crop window centred (camera rules) on (px, py); returns the 240x160 screen and writes OUT_1x.png / OUT_3x.png."""
    left, top = window_for(ident, px, py, SIZE.get(ident, (10 ** 6, 10 ** 6)))
    box = f"{left},{top},{left + 240},{top + 128}"
    prefix = os.path.join(os.path.dirname(out), "_r_" + os.path.basename(out))
    render(ident, box, prefix)
    q = quantize(prefix)
    full = Image.new("RGB", (left + 240, top + 128))
    full.paste(q, (left, top))
    scr = screen(ident, full, left, top, actors, cue_at=cue_at, clip=clip, hud=hud)
    scr.save(out + "_1x.png")
    lib.zoom(scr, 3).save(out + "_3x.png")
    return scr


def sewer_full(outdir):
    """The whole sewer map quantized once (cached), as a PIL image."""
    prefix = os.path.join(outdir, "_r_sewer_full")
    render("sewer", "0,0,640,568", prefix)
    q = quantize(prefix)
    q.save(os.path.join(outdir, "sewer_full_1x_raw.png"))
    return q


def base(out, ident, px, py, outdir=None):
    """Quantized image + window origin of an already rendered shot (cached renders) for re-compositing with other actors / overlays."""
    if ident == "sewer":
        q = sewer_full(outdir)
        left, top = window_for(ident, px, py, q.size)
        return q, left, top
    left, top = window_for(ident, px, py, SIZE.get(ident, (10 ** 6, 10 ** 6)))
    box = f"{left},{top},{left + 240},{top + 128}"
    prefix = os.path.join(os.path.dirname(out), "_r_" + os.path.basename(out))
    render(ident, box, prefix)
    q = quantize(prefix)
    full = Image.new("RGB", (left + 240, top + 128))
    full.paste(q, (left, top))
    return full, left, top


def shot_sewer(out, px, py, actors, outdir, cue_at=None, clip=None, hud=True):
    q = sewer_full(outdir)
    left, top = window_for("sewer", px, py, q.size)
    scr = screen("sewer", q, left, top, actors, cue_at=cue_at, clip=clip, hud=hud)
    scr.save(out + "_1x.png")
    lib.zoom(scr, 3).save(out + "_3x.png")
    return scr
