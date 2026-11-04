"""Render all portraits (raw float RGBA at several sizes) and quantize: python3 build_all.py  -> por/q_<char>_<expr>.png, por/pal_<char>.json"""
import sys, os, json, pickle
import numpy as np
from multiprocessing import Pool
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt import *
import chars
from pt import hexc

CHARS = ["player", "mia", "rosa", "victor"]
EXS = ["neutral", "happy", "angry", "sad", "surprised"]
SIZES = (128, 96)


def job(a):
    c, e = a
    cv = chars.render(c, e)
    out = {}
    for n in SIZES:
        rgb, al = downsample(cv, n)
        out[n] = (rgb.astype(np.float32), al.astype(np.float32))
    return (c, e), out


def kmeans(pts, w, k, iters=20, seed=1):
    rng = np.random.default_rng(seed)
    n = len(pts)
    if n <= k:
        return pts.copy()
    cen = [pts[rng.choice(n, p=w / w.sum())]]
    d2 = ((pts - cen[0]) ** 2).sum(1)
    for _ in range(1, k):
        p = d2 * w
        if p.sum() <= 0: break
        cen.append(pts[rng.choice(n, p=p / p.sum())]); d2 = np.minimum(d2, ((pts - cen[-1]) ** 2).sum(1))
    cen = np.array(cen)
    for _ in range(iters):
        lab = ((pts[:, None] - cen[None]) ** 2).sum(2).argmin(1)
        for j in range(len(cen)):
            m = lab == j
            if m.any(): cen[j] = (pts[m] * w[m, None]).sum(0) / w[m].sum()
    return cen


def to555(c):
    return np.clip(np.round(c / 8.0), 0, 31) * 8.0


def make_palette(imgs, k, reserved):
    """imgs: list of (rgb, mask) crops; returns k colours (reserved first)."""
    px = np.concatenate([rgb[m] for rgb, m in imgs])
    q = to555(px)
    cols, cnt = np.unique(q.astype(np.int32), axis=0, return_counts=True)
    cols = cols.astype(np.float64)
    WT = np.array([0.30, 0.59, 0.11]) ** 0.5
    free = k - len(reserved)
    w = cnt.astype(np.float64) ** 0.8
    cen = kmeans(cols * WT, w, free) / WT
    pal = np.array(list(reserved) + [to555(c) for c in cen])
    return pal


def apply_pal(rgb, pal):
    WT = np.array([0.30, 0.59, 0.11]) ** 0.5
    d = (((rgb[..., None, :] - pal[None, None]) * WT) ** 2).sum(-1)
    return d.argmin(-1)


def quantize_char(c, frames, n=128, splits=2):
    """frames: {expr: (rgb, a)}. splits=2: top/bottom halves each get a 15-colour palette; 1: one palette for all."""
    res = {}
    h = n
    bands = [(0, h)] if splits == 1 else [(0, h // 2), (h // 2, h)]
    pals = []
    for (y0, y1) in bands:
        crops = [(frames[e][0][y0:y1], frames[e][1][y0:y1] > 0.5) for e in frames]
        reserved = [chars.LINE, hexc("fffafa"), chars.CH[c]["blush"]] + ([hexc("4a1a24")] if y0 > 0 else [])
        pals.append(make_palette(crops, 15, [to555(r) for r in reserved]))
    for e, (rgb, a) in frames.items():
        out = np.zeros((h, n, 3), np.uint8)
        idx = np.zeros((h, n), np.uint8)
        for (y0, y1), pal in zip(bands, pals):
            ii = apply_pal(rgb[y0:y1], pal)
            out[y0:y1] = pal[ii].astype(np.uint8)
            idx[y0:y1] = ii + 1
        idx[a <= 0.5] = 0
        res[e] = (out, idx)
    return res, pals


if __name__ == "__main__":
    jobs = [(c, e) for c in CHARS for e in EXS]
    with Pool(4) as p:
        R = dict(p.map(job, jobs))
    pickle.dump(R, open("por/raw.pkl", "wb"))
    for n in SIZES:
        for c in CHARS:
            fr = {e: R[(c, e)][n] for e in EXS}
            for splits in (2, 1):
                res, pals = quantize_char(c, fr, n, splits)
                for e, (rgb, idx) in res.items():
                    im = np.dstack([rgb, (idx > 0) * 255]).astype(np.uint8)
                    Image.fromarray(im, "RGBA").save(f"por/q{splits}_{n}_{c}_{e}.png")
                json.dump([p.astype(int).tolist() for p in pals], open(f"por/pal{splits}_{n}_{c}.json", "w"))
    print("done")
