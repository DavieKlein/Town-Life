#!/usr/bin/env python3
"""Sharpness experiment: renders of 4 crops (run_variants.sh) -> the REAL quantizer (build_assets.convert_layer, 8 floor +
7 object banks of 15/7 colours, tile dedup) -> side-by-side sheets.

The 4 crops (street corner, fountain square, public toilet, library reading area; each 240x144 px = one screen) are
packed into one 480x288 canvas per layer so they compete for the same 8 / 7 palette banks (the whole map has
the same 8 / 7 banks for ~2.7 Mpx, so this is, if anything, slightly easier than the real thing).

  python3 sharpness.py [IN_DIR] [OUT_DIR]
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib                      # noqa: E402
ba = lib.ba

IN = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/s49/sh"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/claude-0/s49"
CROPS = ["street", "fountain", "toilet", "library"]
NAMES = {"street": "Street corner (bin, lamp, shopfront)", "fountain": "Fountain square",
         "toilet": "Public toilet interior", "library": "Library reading area"}
VARS = {"A": "A  current (filter 1.2, 96 spp, 0.8 px soft outline, grain)",
        "B": "B  filter 0.5, 192 spp",
        "C": "C  B + 1.25 px crisp outline + unsharp + stronger grade",
        "D": "D  C + flat objects / less grain"}
W, H = 240, 144


def blur3(a):
    k = np.array([1, 2, 1]) / 4.0
    p = np.pad(a, ((1, 1), (1, 1)) + ((0, 0),) * (a.ndim - 2), mode="edge")
    t = p[:-2] * k[0] + p[1:-1] * k[1] + p[2:] * k[2]
    return t[:, :-2] * k[0] + t[:, 1:-1] * k[1] + t[:, 2:] * k[2]


def sharpen(img, amount=0.9):
    """Alpha-aware unsharp mask on the RGB channels (3x3 binomial blur; transparent pixels do not leak in)."""
    a = np.asarray(img).astype(np.float64)
    al = a[..., 3:4] / 255.0
    w = blur3(al)
    bl = blur3(a[..., :3] * al) / np.maximum(w, 1e-6)
    out = a[..., :3] + amount * (a[..., :3] - bl)
    a[..., :3] = np.where(al > 0, np.clip(out, 0, 255), a[..., :3])
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def grade_c(img):
    """Variant C/D grade: the current grade with more saturation and contrast."""
    a = np.asarray(img).astype(np.float64) / 255.0
    rgb = a[..., :3]
    luma = (rgb * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    rgb = luma + (rgb - luma) * 1.3
    rgb = np.clip(0.5 + (rgb - 0.5) * 1.22, 0, 1)
    shadow = np.clip(1.0 - luma / 0.45, 0, 1)
    rgb = rgb * (1 - 0.18 * shadow) + shadow * 0.18 * rgb * np.array([0.82, 0.8, 1.15])
    a[..., :3] = np.clip(rgb, 0, 1)
    return Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")


def prepare(var, name, layer):
    im = lib.down(Image.open(f"{IN}/{name}_{layer}_{var}.png"))
    if var in ("C", "D"):
        return grade_c(sharpen(im))
    return ba.grade(im)


def run(var):
    res = {}
    cells_by = {}
    for layer, banks, transparent in (("floor", 8, False), ("objects", 7, True)):
        canvas = Image.new("RGBA", (2 * W, 2 * H), (0, 0, 0, 0))
        for i, n in enumerate(CROPS):
            canvas.paste(prepare(var, n, layer), ((i % 2) * W, (i // 2) * H))
        pal, cells, tiles, info = ba.convert_layer(canvas, banks, transparent, None, layer)
        pv = ba.layer_preview(pal, cells, tiles)
        res[layer] = (pv, info["drawn"])
        cells_by[layer] = (cells, len(tiles))
    fl, (ob, drawn) = res["floor"][0], res["objects"]
    comp = fl.copy()
    comp[drawn] = ob[drawn]
    out = {}
    for i, n in enumerate(CROPS):
        x0, y0 = (i % 2) * W, (i // 2) * H
        im = Image.fromarray(comp[y0:y0 + H, x0:x0 + W])
        stats = {}
        for layer in ("floor", "objects"):
            cells, total = cells_by[layer]
            ids = (cells[y0 // 8:(y0 + H) // 8, x0 // 8:(x0 + W) // 8] & 0xFFFF)
            stats[layer] = len(np.unique(ids[ids > 0]))
        g = np.asarray(im.convert("L")).astype(np.float64)
        gx, gy = np.abs(np.diff(g, axis=1)), np.abs(np.diff(g, axis=0))
        stats["edge"] = float(((gx > 40).mean() + (gy > 40).mean()) / 2 * 100)      # % strong-edge pixel pairs
        out[n] = (im, stats)
    tot = {l: cells_by[l][1] for l in cells_by}
    return out, tot


def font(n=12):
    return ImageFont.truetype(lib.FONT, n)


def main():
    results, totals = {}, {}
    for v in "ABCD":
        if all(os.path.exists(f"{IN}/{n}_{l}_{v}.png") for n in CROPS for l in ("floor", "objects")):
            results[v], totals[v] = run(v)
            print(v, "unique tiles in the 4-crop canvas:", totals[v])
        else:
            print("variant", v, "not rendered yet")
    os.makedirs(OUT, exist_ok=True)
    # per crop: full screen, one image per variant, plus stats
    for n in CROPS:
        for v, r in results.items():
            r[n][0].save(f"{OUT}/sharp_{n}_{v}.png")
    # the main sheet: per crop, a 2x2 grid of detail windows (120x72 at 3x) for the 4 variants
    DX, DY, DW, DH = {"street": (80, 40), "fountain": (64, 40), "toilet": (70, 20), "library": (60, 30)}, None, 120, 72
    n3 = 3
    pad, bar = 6, 18
    cw, ch = DW * n3, DH * n3
    rows = []
    for n in CROPS:
        rows.append(n)
    sheet = Image.new("RGB", (2 * (cw + pad) + pad, len(rows) * (2 * (ch + bar + pad) + 28) + pad), (28, 30, 38))
    d = ImageDraw.Draw(sheet)
    y = pad
    for n in CROPS:
        d.text((pad, y + 4), NAMES[n], fill=(255, 220, 120), font=font(14))
        y += 28
        for k, v in enumerate("ABCD"):
            if v not in results:
                continue
            im, st = results[v][n]
            dx, dy = DX[n]
            tile = im.crop((dx, dy, dx + DW, dy + DH)).resize((cw, ch), Image.NEAREST)
            x = pad + (k % 2) * (cw + pad)
            yy = y + (k // 2) * (ch + bar + pad)
            d.text((x, yy + 2), f"{VARS[v][:48]}", fill=(255, 255, 255), font=font(11))
            sheet.paste(tile, (x, yy + bar))
            d.text((x + 4, yy + bar + ch - 16), f"tiles F{st['floor']} O{st['objects']}  edges {st['edge']:.1f}%",
                   fill=(255, 255, 0), font=font(11))
        y += 2 * (ch + bar + pad)
    sheet.save(f"{OUT}/sharpness.png")
    print("wrote", f"{OUT}/sharpness.png", sheet.size)
    # stats table
    with open(f"{OUT}/sharpness_stats.txt", "w") as f:
        for v in results:
            f.write(f"{v}: canvas unique tiles {totals[v]}\n")
            for n in CROPS:
                st = results[v][n][1]
                f.write(f"   {n:9s} floor {st['floor']:4d} objects {st['objects']:4d} strong-edge {st['edge']:.2f}%\n")
    print(open(f"{OUT}/sharpness_stats.txt").read())


if __name__ == "__main__":
    main()
