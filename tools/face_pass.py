"""
Town Life - face pixel pass for character sprites (owner-approved "option B", ported from tools/proposals/s54/quant.py + bpass.py).

Quantises a sprite sheet to 11 free colours + 3 reserved colours (eye white, mouth, blush) + the outline colour, so the palette
index layout is: 1..11 free, 12 eye white, 13 mouth, 14 blush, 15 outline. The reserved entries are only used by the pass,
which draws eyes (1x2 dark px + a white corner), brow, mouth, blush, a nose-shade pixel (3/4 views) and a hair highlight on the
quantised frame, driven by the Blender-projected anchors (anchors.json: {frame: {anchor: [x, y, visible]}}).
Only front and 3/4 facings get a face (FACE_EYES); a frame whose eyes are hidden (bent over a sink, back views) is left alone.
"""
import math
import numpy as np

import face_cfg

WEIGHT = np.array([0.30, 0.59, 0.11]) ** 0.5
OUTLINE = np.array([40.0, 30.0, 40.0])
NFREE = 11
EYEW, MOUTH, BLUSH, OUT = 1 + NFREE, 2 + NFREE, 3 + NFREE, 15


def to5(c):
    return np.clip(np.round(c / 8.0), 0, 31) * 8.0


def kmeans(points, k, weights=None, iters=12, seed=1):
    rng = np.random.default_rng(seed)
    n = len(points)
    if n <= k:
        return points.copy()
    if weights is None:
        weights = np.ones(n)
    centers = [points[rng.choice(n, p=weights / weights.sum())]]
    d2 = ((points - centers[0]) ** 2).sum(1)
    for _ in range(1, k):
        p = d2 * weights
        if p.sum() <= 0:
            break
        centers.append(points[rng.choice(n, p=p / p.sum())])
        d2 = np.minimum(d2, ((points - centers[-1]) ** 2).sum(1))
    centers = np.array(centers)
    for _ in range(iters):
        dist = ((points[:, None, :] - centers[None, :, :]) ** 2).sum(2)
        lab = dist.argmin(1)
        for j in range(len(centers)):
            m = lab == j
            if m.any():
                centers[j] = (points[m] * weights[m, None]).sum(0) / weights[m].sum()
    return centers


def hx(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def reserved_colours(name, skin_hex):
    skin = np.array(hx(skin_hex), float)
    blush = skin * 0.78 + np.array([255, 110, 120]) * 0.22
    return [[246, 242, 238], hx(face_cfg.FACE[name]["plips"]), blush]


def quantize_sheet(frames, reserved):
    """frames: [(rgb, alpha)] with the outline already in rgb. Returns (palette 16x3 incl. transparent entry 0, [index arrays])."""
    px = np.concatenate([rgb[alpha] for rgb, alpha in frames]) * WEIGHT
    cols = to5(kmeans(px, NFREE, iters=15) / WEIGHT)
    cols = np.concatenate([cols, np.array(reserved, dtype=np.float64).reshape(-1, 3), [OUTLINE]])
    pal = np.zeros((16, 3))
    pal[1:1 + len(cols)] = to5(cols)
    pal[0] = (255, 0, 255)
    allow = np.array([i for i in range(len(cols)) if not (NFREE <= i < NFREE + 3)])   # reserved colours: face pass only
    cw = pal[1:1 + len(cols)][allow] * WEIGHT
    out = []
    for rgb, alpha in frames:
        d = ((rgb[..., None, :] * WEIGHT - cw[None, None]) ** 2).sum(3)
        idx = allow[d.argmin(2)] + 1
        idx[~alpha] = 0
        out.append(idx.astype(np.uint8))
    return pal, out


def nearest(pal, rgb, lo, hi):
    d = ((pal[lo:hi] - np.array(rgb)) ** 2 * np.array([0.30, 0.59, 0.11])).sum(1)
    return int(d.argmin()) + lo


def skin_class(rgb):
    r, g, b = [float(v) for v in rgb]
    return r > 150 and 0.66 < g / r < 0.93 and 0.10 < (r - b) / r < 0.56


def make_ctx(pal, name, skin_hex):
    F = face_cfg.FACE[name]
    skin = np.array(hx(skin_hex), float)
    hair = np.array(hx(F["hair"]), float)
    lo, hi = 1, 1 + NFREE
    ctx = dict(out=OUT, eyew=EYEW, mouth=MOUTH, blush=BLUSH)
    ctx["skin_shade"] = nearest(pal, skin * 0.80 + np.array([40, 0, 20]) * 0.2, lo, hi)
    ctx["brow"] = nearest(pal, hair * 0.62, lo, hi)
    ctx["hair_hi"] = nearest(pal, hair * 0.5 + np.array([255, 255, 255]) * 0.5 if name != "victor" else hair * 1.0, lo, hi)
    ctx["skin_set"] = {i for i in range(lo, hi) if skin_class(pal[i])}
    ctx["lum"] = [0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2] for p in pal]
    return ctx


FACE_EYES = {"s": 2, "sw": 2, "se": 2, "w": 1, "e": 1}      # eyes visible per facing (3/4 and front views show both)


def paint_face(idx, anc, ctx, facing, opt=None):
    """idx: HxW palette indices (0 = transparent), modified in place. anc: {name: [x, y, visible]} in frame pixels."""
    opt = opt or {}
    H, W = idx.shape
    OUTI = ctx["out"]
    SK = ctx["skin_set"]
    fl = lambda v: int(math.floor(v))

    def put(x, y, c, skin_only=False, over_outline=False):
        if not (0 <= x < W and 0 <= y < H):
            return
        cur = idx[y, x]
        if cur == 0 or (cur == OUTI and not over_outline):
            return
        if skin_only and cur not in SK:
            return
        idx[y, x] = c
    mode = FACE_EYES.get(facing, 0)
    if mode == 0:
        return idx
    eP, eM = anc["eyeP"], anc["eyeM"]
    if mode == 2:
        if not (eP[2] and eM[2]):
            return idx
        ey = fl((eP[1] + eM[1]) / 2)
        xl, xr = sorted([fl(eP[0]), fl(eM[0])])
        if xr - xl < 2:
            c = (xl + xr) // 2
            xl, xr = c - 1, c + 1
        eyes = [(xl, -1), (xr, +1)]
    else:
        if not (eM[2] or eP[2]):
            return idx
        e = eM if eM[2] else eP
        ex = fl(e[0])
        ey = fl(e[1])
        eyes = [(ex, +1 if anc["mouth"][0] < ex or anc["nose"][0] > ex else -1)]
    for (x, out) in eyes:
        if 0 <= x < W and 0 <= ey < H and idx[ey, x] != 0 and ctx["lum"][idx[ey, x]] < 70:    # sunglasses etc.: leave as is
            continue
        put(x, ey, OUTI, over_outline=True)
        put(x, ey + 1, OUTI, over_outline=True)
        if mode == 2:
            put(x + out, ey + 1, ctx["eyew"], skin_only=True)
        put(x, ey - 1, ctx["brow"], skin_only=True)
        put(x + out, ey - 1, ctx["brow"], skin_only=True)
    if mode == 2:
        for (x, out) in eyes:
            put(x + out, ey + 2, ctx["blush"], skin_only=True)
    nx, ny = anc["nose"][0], anc["nose"][1]
    mx, my = anc["mouth"][0], anc["mouth"][1]
    my = max(int(round(my - 0.2)), ey + 3)
    if mode == 2 and anc["mouth"][2]:
        if facing == "s":
            put(fl(mx - 0.5), my, ctx["mouth"], skin_only=True)
            put(fl(mx + 0.5), my, ctx["mouth"], skin_only=True)
        else:
            put(fl(mx), my, ctx["mouth"], skin_only=True)
            put(fl(nx), max(ey + 2, fl(ny)), ctx["skin_shade"], skin_only=True)
    elif mode == 1 and anc["mouth"][2]:
        put(fl(mx), my, ctx["mouth"], skin_only=True)
    if anc["crown"][2]:
        put(fl(anc["crown"][0]), fl(anc["crown"][1]) + 1, ctx["hair_hi"])
    return idx
