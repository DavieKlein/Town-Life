"""Shared helpers for the s49 proposal scripts: preview composition (graded like the game, 5-bit colour), zoom, labels."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

TOOLS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, TOOLS)
import build_assets as ba   # noqa: E402

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def down(img, f=2):
    a = np.asarray(img.convert("RGBA")).astype(np.float64) / 255.0
    a[..., :3] *= a[..., 3:4]
    h, w = a.shape[0] // f, a.shape[1] // f
    a = a[:h * f, :w * f].reshape(h, f, w, f, 4).mean(axis=(1, 3))
    rgb = np.where(a[..., 3:4] > 0, a[..., :3] / np.maximum(a[..., 3:4], 1e-6), 0)
    return Image.fromarray(np.clip(np.concatenate([rgb, a[..., 3:4]], axis=2) * 255 + .5, 0, 255).astype(np.uint8), "RGBA")


def to555(im):
    a = np.asarray(im.convert("RGB")).astype(np.float64)
    return Image.fromarray((np.clip(np.round(a / 8.0), 0, 31) * 8).astype(np.uint8))


def compose(prefix, bg=(10, 12, 24)):
    fl = ba.grade(down(Image.open(prefix + "_floor.png")))
    ob = ba.grade(down(Image.open(prefix + "_objects.png")))
    base = Image.new("RGBA", fl.size, bg + (255,))
    base.alpha_composite(fl)
    base.alpha_composite(ob)
    return to555(base)


def zoom(im, n):
    return im.resize((im.width * n, im.height * n), Image.NEAREST)


def labelled(tiles, n=3, cols=2, pad=6, bar=18, title=None):
    """tiles: list of (PIL image, label); returns a sheet at n x nearest-neighbour."""
    w = max(t[0].width for t in tiles) * n
    h = max(t[0].height for t in tiles) * n
    rows = (len(tiles) + cols - 1) // cols
    top = 24 if title else 0
    out = Image.new("RGB", (cols * (w + pad) + pad, top + rows * (h + bar + pad) + pad), (28, 30, 38))
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(FONT, 12)
    if title:
        d.text((pad, 4), title, fill=(255, 220, 120), font=ImageFont.truetype(FONT, 14))
    for i, (im, lab) in enumerate(tiles):
        x = pad + (i % cols) * (w + pad)
        y = top + pad + (i // cols) * (h + bar + pad)
        out.paste(zoom(im.convert("RGB"), n), (x, y + bar))
        d.text((x, y + 2), lab, fill=(255, 255, 255), font=f)
    return out
