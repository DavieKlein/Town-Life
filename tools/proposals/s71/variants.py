"""s71 proposal: per-variant pixel pipeline (grade / sharpen / quantizer), all done by monkeypatching build_assets in
memory (the real files are not changed).

cur  build_assets.sharpen(0.9) + grade (sat 1.3, contrast 1.22, cool shadows) + k-means in weighted RGB
v1   softer: sharpen 0.55, grade sat 1.15 / contrast 1.08, lighter cool tint
v2   richer + calmer: sharpen 0.5, sat 1.12 / contrast 1.03, warm shadow tint
v3   current look, but: k-means palettes in CIE Lab (perceptual), 20 iterations, and a limited palette-aware ordered
     dither (4x4 Bayer between the two nearest palette colours, only in smooth tiles and only between close colours)
"""
import inspect
import os
import sys

import numpy as np
from PIL import Image

TOOLS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, TOOLS)
import build_assets as ba  # noqa: E402

SHARP = {"cur": 0.9, "v1": 0.55, "v2": 0.5, "v3": 0.75}
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16.0
DITHER_GAP = 34.0        # max distance (weighted RGB units) between two palette colours that may be dithered
DITHER_TILE_STD = 15.0   # only tiles whose weighted-RGB std is below this (smooth gradients)


def grade(img, variant):
    if variant in ("cur", "v3"):
        return ba.grade(img)
    sat, con, tint, warm = (1.15, 1.08, 0.12, False) if variant == "v1" else (1.12, 1.03, 0.14, True)
    a = np.asarray(img).astype(np.float64) / 255.0
    rgb = a[..., :3]
    luma = (rgb * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    rgb = luma + (rgb - luma) * sat
    rgb = np.clip(0.5 + (rgb - 0.5) * con, 0, 1)
    shadow = np.clip(1.0 - luma / 0.45, 0, 1)
    tv = np.array([1.08, 0.97, 0.9]) if warm else np.array([0.85, 0.83, 1.1])
    rgb = rgb * (1 - tint * shadow) + shadow * tint * rgb * tv
    a[..., :3] = np.clip(rgb, 0, 1)
    return Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")


def process(img, variant):
    return grade(ba.sharpen(img, SHARP[variant]), variant)


# ---------------------------------------------------------------------------------------------- Lab k-means (v3)
def _srgb_to_lab(c):
    c = c / 255.0
    lin = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = lin @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def _lab_to_srgb(lab):
    fy = (lab[..., 0] + 16) / 116
    fx = fy + lab[..., 1] / 500
    fz = fy - lab[..., 2] / 200
    f = np.stack([fx, fy, fz], -1)
    xyz = np.where(f ** 3 > 0.008856, f ** 3, (f - 16 / 116) / 7.787) * np.array([0.95047, 1.0, 1.08883])
    m = np.linalg.inv(np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]))
    lin = np.clip(xyz @ m.T, 0, 1)
    c = np.where(lin > 0.0031308, 1.055 * lin ** (1 / 2.4) - 0.055, 12.92 * lin)
    return np.clip(c, 0, 1) * 255.0


_orig_kmeans = ba.kmeans


def kmeans_lab(points, k, weights=None, iters=12, seed=1):
    """Same interface as build_assets.kmeans (points are weighted RGB), clusters in CIE Lab instead."""
    if len(points) <= k or points.shape[1] != 3:
        return _orig_kmeans(points, k, weights, iters, seed)
    lab = _srgb_to_lab(np.clip(points / ba.WEIGHT, 0, 255))
    lab[..., 0] *= 1.25                                        # keep luminance steps a bit more important than hue
    c = _orig_kmeans(lab, k, weights, iters=max(iters, 20), seed=seed)
    c[..., 0] /= 1.25
    return _lab_to_srgb(c) * ba.WEIGHT


# ---------------------------------------------------------------------------------------------- limited ordered dither
def dither_idx(idx, d, X, Y, pal, tiles_rgb_chunk):
    """idx (N,64) nearest-palette indices (1-based); d (N,64,k) squared distances; pal (k,3). Replaces idx by the second nearest
    colour where a 4x4 Bayer threshold says so, only inside smooth tiles and only between close palette colours."""
    order = np.argsort(d, axis=2)[:, :, :2]
    c1, c2 = order[..., 0], order[..., 1]
    d1 = np.take_along_axis(d, c1[..., None], 2)[..., 0]
    d2 = np.take_along_axis(d, c2[..., None], 2)[..., 0]
    gap = ((pal[c1] - pal[c2]) ** 2).sum(-1)
    t = np.where(gap > 1e-6, (d1 - d2 + gap) / (2 * np.maximum(gap, 1e-6)), 0.0)
    smooth = tiles_rgb_chunk.std(axis=1).mean(axis=1) < DITHER_TILE_STD           # (N,)
    thr = BAYER[Y & 3, X & 3]
    ok = smooth[:, None] & (gap < DITHER_GAP ** 2) & (gap > 1e-6) & (t > 0.2) & (t < 0.8)
    return np.where(ok & (t > thr), c2 + 1, idx).astype(np.uint8)


def _patched_convert():
    src = inspect.getsource(ba.convert_layer)
    a = "            idx = (d.argmin(2) + 1).astype(np.uint8)\n"
    assert src.count(a) == 1
    src = src.replace(a, a + "            if DITHER_ON[0]:\n                idx = DITHER(idx, d, tiles_x[chunk], tiles_y[chunk], palettes[b], tiles_rgb[chunk])\n")
    src = src.replace("def convert_layer(", "def convert_layer_s71(")
    ns = ba.__dict__
    ns["DITHER"] = dither_idx
    ns["DITHER_ON"] = DITHER_ON
    exec(compile(src, "convert_layer_s71", "exec"), ns)
    return ns["convert_layer_s71"]


DITHER_ON = [False]
_convert = _patched_convert()


def convert(img, banks, transparent, layer, variant):
    """Quantize with the real converter; v3 uses Lab k-means + limited dither."""
    if variant == "v3":
        ba.kmeans = kmeans_lab
        DITHER_ON[0] = True
    try:
        return _convert(img, banks, transparent, None, layer)
    finally:
        ba.kmeans = _orig_kmeans
        DITHER_ON[0] = False
