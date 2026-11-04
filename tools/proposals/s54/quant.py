"""Quantizer copied from tools/build_assets.py (sprite_frame / write_sprite_sheet / kmeans) + the face pixel pass (option B)."""
import numpy as np, json, math, os
from PIL import Image
WEIGHT = np.array([0.30, 0.59, 0.11]) ** 0.5
OUTLINE = np.array([40.0, 30.0, 40.0])
def to5(c): return np.clip(np.round(c / 8.0), 0, 31) * 8.0
def kmeans(points, k, weights=None, iters=12, seed=1):
    rng = np.random.default_rng(seed); n = len(points)
    if n <= k: return points.copy()
    if weights is None: weights = np.ones(n)
    centers = [points[rng.choice(n, p=weights / weights.sum())]]
    d2 = ((points - centers[0]) ** 2).sum(1)
    for _ in range(1, k):
        p = d2 * weights
        if p.sum() <= 0: break
        centers.append(points[rng.choice(n, p=p / p.sum())]); d2 = np.minimum(d2, ((points - centers[-1]) ** 2).sum(1))
    centers = np.array(centers)
    for _ in range(iters):
        dist = ((points[:, None, :] - centers[None, :, :]) ** 2).sum(2); lab = dist.argmin(1)
        for j in range(len(centers)):
            m = lab == j
            if m.any(): centers[j] = (points[m] * weights[m, None]).sum(0) / weights[m].sum()
    return centers

def sprite_frame(path, ss, w, h):
    img = np.asarray(Image.open(path).convert("RGBA")).astype(np.float64) / 255.0
    img[..., :3] *= img[..., 3:4]
    img = img.reshape(h, ss, w, ss, 4).mean(axis=(1, 3))
    rgb = np.where(img[..., 3:4] > 0, img[..., :3] / np.maximum(img[..., 3:4], 1e-6), 0) * 255
    alpha = img[..., 3] >= 0.45
    grown = alpha.copy()
    grown[1:, :] |= alpha[:-1, :]; grown[:-1, :] |= alpha[1:, :]; grown[:, 1:] |= alpha[:, :-1]; grown[:, :-1] |= alpha[:, 1:]
    edge = grown & ~alpha
    rgb[edge] = OUTLINE
    return rgb, alpha | edge

def quantize_sheet(frames, reserved=()):
    """frames: [(rgb, alpha)]. 14 colours incl. outline-free kmeans; `reserved` colours take slots away from k-means (option B)."""
    px = np.concatenate([rgb[alpha] for rgb, alpha in frames]) * WEIGHT
    nfree = 14 - len(reserved)
    cols = to5(kmeans(px, nfree, iters=15) / WEIGHT)
    cols = np.concatenate([cols, np.array(reserved, dtype=np.float64).reshape(-1, 3), [OUTLINE]])
    pal = np.zeros((16, 3)); pal[1:1 + len(cols)] = to5(cols)
    nres = len(reserved)
    allow = np.array([i for i in range(len(cols)) if not (nfree <= i < nfree + nres)])   # reserved colours are only used by the face pass
    cw = pal[1:1 + len(cols)][allow] * WEIGHT
    out = []
    for rgb, alpha in frames:
        d = ((rgb[..., None, :] * WEIGHT - cw[None, None]) ** 2).sum(3)
        idx = allow[d.argmin(2)] + 1
        idx[~alpha] = 0
        out.append(idx.astype(np.uint8))
    return pal, out

def to_image(idx, pal):
    a = pal[idx].astype(np.uint8)
    rgba = np.concatenate([a, (idx > 0)[..., None].astype(np.uint8) * 255], axis=2)
    return Image.fromarray(rgba, "RGBA")

def nearest(pal, rgb, lo=1, hi=16):
    d = ((pal[lo:hi] - np.array(rgb)) ** 2 * np.array([0.30, 0.59, 0.11])).sum(1)
    return int(d.argmin()) + lo

# ----------------------------------------------------------------------------- option B: face pixel pass
FACE_EYES = {"s": 2, "sw": 2, "se": 2, "w": 1, "e": 1}      # eyes visible per facing (3/4 and front views show both)
def skin_class(rgb):
    r, g, b = [float(v) for v in rgb]
    return r > 150 and 0.66 < g / r < 0.93 and 0.10 < (r - b) / r < 0.56

def paint_face(idx, anc, ctx, opt, facing):
    """idx: 64x32 palette indices (0 = transparent). anc: {name: [x, y, visible]} in frame pixels (from Blender).
    ctx: palette indices out, eyew, mouth, blush, brow, skin_shade, hair_hi + skin set. One eye 1x2 px, outer white, brow, mouth, blush."""
    H, W = idx.shape
    OUTI = ctx["out"]; SK = ctx["skin_set"]
    fl = lambda v: int(math.floor(v))
    def put(x, y, c, skin_only=False, over_outline=False):
        if not (0 <= x < W and 0 <= y < H): return
        cur = idx[y, x]
        if cur == 0 or (cur == OUTI and not over_outline): return
        if skin_only and cur not in SK: return
        idx[y, x] = c
    mode = FACE_EYES.get(facing, 0)
    if mode == 0: return idx
    eP, eM = anc["eyeP"], anc["eyeM"]
    if mode == 2:
        ey = fl((eP[1] + eM[1]) / 2)
        xs = sorted([fl(eP[0]), fl(eM[0])]); xl, xr = xs
        if xr - xl < 2:
            c = (xl + xr) // 2
            xl, xr = c - 1, c + 1
        eyes = [(xl, -1), (xr, +1)]
    else:
        e = eM if eM[2] else eP
        ex = fl(e[0]); ey = fl(e[1])
        eyes = [(ex, +1 if anc["mouth"][0] < ex or anc["nose"][0] > ex else -1)]
    for (x, out) in eyes:
        if 0 <= x < W and 0 <= ey < H and idx[ey, x] != 0 and ctx["lum"][idx[ey, x]] < 70:    # sunglasses etc.: leave as is
            put(x, ey, ctx["eyew"]) if opt.get("glint", True) and mode == 2 else None
            continue
        put(x, ey, OUTI, over_outline=True); put(x, ey + 1, OUTI, over_outline=True)
        if opt.get("white", True) and mode == 2:
            put(x + out, ey + 1, ctx["eyew"], skin_only=True)
        if opt.get("brow", True):
            put(x, ey - 1, ctx["brow"], skin_only=True); put(x + out, ey - 1, ctx["brow"], skin_only=True)
    if opt.get("blush", True) and mode == 2:
        for (x, out) in eyes: put(x + out, ey + 2, ctx["blush"], skin_only=True)
    nx, ny = anc["nose"][0], anc["nose"][1]
    mx, my = anc["mouth"][0], anc["mouth"][1]
    my = max(int(round(my - 0.2)), ey + 3 if mode == 2 else ey + 3)
    if mode == 2 and anc["mouth"][2]:
        if facing == "s":
            put(fl(mx - 0.5), my, ctx["mouth"], skin_only=True); put(fl(mx + 0.5), my, ctx["mouth"], skin_only=True)
        else:
            put(fl(mx), my, ctx["mouth"], skin_only=True)
            put(fl(nx), max(ey + 2, fl(ny)), ctx["skin_shade"], skin_only=True) if opt.get("nose", True) else None
    elif mode == 1 and anc["mouth"][2]:
        put(fl(mx), my, ctx["mouth"], skin_only=True)
    if opt.get("hair", True) and anc["crown"][2]:
        put(fl(anc["crown"][0]), fl(anc["crown"][1]) + 1, ctx["hair_hi"])
    return idx
