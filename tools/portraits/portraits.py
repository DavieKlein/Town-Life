"""Dialogue portraits (own parametric 2D painter, owner-approved s55): 128x128, 5 expressions, ONE 15-colour palette per character.
Render + quantize: render_all(cache_dir) -> {char: {expr: (index image 128x128 uint8, palette 16x3)}}; build_assets writes the graphics.
Run alone for a contact sheet:  python3 tools/portraits/portraits.py OUTDIR"""
import sys, os, json, pickle, hashlib
import numpy as np
from multiprocessing import Pool
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pt import *
import chars
from pt import hexc

CHARS = ["player", "mia", "rosa", "dex", "dex_vault", "pimm", "lou", "victor", "robot", "okafor", "ines", "teo", "grigor", "valdez", "pruitt", "kessler", "nella"]
NAMES = {"player": "Sam", "mia": "Mia", "rosa": "Rosa", "dex": "Dex", "dex_vault": "Dex", "pimm": "Mr. Pimm", "lou": "Big Lou", "victor": "Victor Vault", "robot": "Valet"}
EXS = ["neutral", "happy", "angry", "sad", "surprised"]
N = 128
SMALL = 96          # the choice layout (layout 2) uses a 96 px version of every portrait


def job(a):
    c, e = a
    cv = chars.render(c, e)
    out = {}
    for n in (N, SMALL):
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


WT = np.array([0.30, 0.59, 0.11]) ** 0.5


def quantize_char(c, frames):
    """frames {(size, expr): (rgb, a)} -> ({(size, expr): idx (1..15, 0 transparent)}, palette (15, 3)): ONE palette for all."""
    reserved = [to555(r) for r in (chars.LINE if c != "robot" else hexc("1c1e28"), hexc("fffafa"), chars.CH[c]["blush"])]
    px = np.concatenate([rgb[a > 0.5] for rgb, a in frames.values()])
    cols, cnt = np.unique(to555(px).astype(np.int32), axis=0, return_counts=True)
    cols = cols.astype(np.float64)
    cen = kmeans(cols * WT, cnt.astype(np.float64) ** 0.8, 15 - len(reserved)) / WT
    pal = np.array(list(reserved) + [to555(x) for x in cen])
    out = {}
    for k, (rgb, a) in frames.items():
        d = (((rgb[..., None, :] - pal[None, None]) * WT) ** 2).sum(-1)
        idx = d.argmin(-1) + 1
        idx[a <= 0.5] = 0
        out[k] = idx.astype(np.uint8)
    return out, pal.astype(int)


def render_all(cache_dir, only=None):
    os.makedirs(cache_dir, exist_ok=True)
    h = hashlib.sha1()
    for f in sorted(os.listdir(HERE)):
        if f.endswith(".py"):
            h.update(open(os.path.join(HERE, f), "rb").read())
    key = h.hexdigest()[:12]
    path = os.path.join(cache_dir, f"portraits_{key}.pkl")
    if os.path.exists(path):
        return pickle.load(open(path, "rb"))
    jobs = [(c, e) for c in CHARS if (only is None or c in only) for e in EXS]
    with Pool(min(4, os.cpu_count() or 1)) as p:
        R = dict(p.map(job, jobs))
    res = {}
    for c in CHARS:
        if only is not None and c not in only:
            continue
        idx, pal = quantize_char(c, {(n, e): R[(c, e)][n] for e in EXS for n in (N, SMALL)})
        res[c] = dict(idx=idx, pal=pal)
    if only is None:
        pickle.dump(res, open(path, "wb"))
    return res


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    res = render_all(os.path.join(out, "cache"), only)
    cs = list(res)
    sheet = Image.new("RGB", (5 * 260 + 10, len(cs) * 260 + 10), (236, 226, 200))
    for j, c in enumerate(cs):
        pal = np.vstack([[236, 226, 200], res[c]["pal"]]).astype(np.uint8)
        for i, e in enumerate(EXS):
            im = Image.fromarray(pal[res[c]["idx"][(N, e)]], "RGB").resize((256, 256), Image.NEAREST)
            sheet.paste(im, (5 + i * 260, 5 + j * 260))
    sheet.save(os.path.join(out, "sheet.png"))
    for c in cs:
        pal = np.vstack([[236, 226, 200], res[c]["pal"]]).astype(np.uint8)
        row = Image.new("RGB", (5 * 258, 256))
        for i, e in enumerate(EXS):
            row.paste(Image.fromarray(pal[res[c]["idx"][(N, e)]], "RGB").resize((256, 256), Image.NEAREST), (i * 258, 0))
        row.save(os.path.join(out, f"row_{c}.png"))
