"""s72 post-processing: sprite quantization with the REAL face pass (+ small s72 additions), comparison sheets, in-game mock."""
import json
import math
import os
import pickle
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import face_cfg
import face_pass as fp
import s72_build

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FW, FH = 32, 64
FACINGS = ["s", "se", "e"]
GAME_ORDER = ["s", "sw", "w", "nw", "n", "ne", "e", "se"]


def sprite_frame(path, ss, w, h):
    """Same as build_assets.sprite_frame: supersampled RGBA render -> (rgb, alpha) with a 1 px dark outline."""
    img = np.asarray(Image.open(path).convert("RGBA")).astype(np.float64) / 255.0
    img[..., :3] *= img[..., 3:4]
    img = img.reshape(h, ss, w, ss, 4).mean(axis=(1, 3))
    rgb = np.where(img[..., 3:4] > 0, img[..., :3] / np.maximum(img[..., 3:4], 1e-6), 0) * 255
    alpha = img[..., 3] >= 0.45
    grown = alpha.copy()
    grown[1:, :] |= alpha[:-1, :]
    grown[:-1, :] |= alpha[1:, :]
    grown[:, 1:] |= alpha[:, :-1]
    grown[:, :-1] |= alpha[:, 1:]
    edge = grown & ~alpha
    rgb[edge] = [40.0, 30.0, 40.0]
    return rgb, alpha | edge


def extra_paint(idx, anc, ctx, facing, who):
    """s72 additions on top of face_pass.paint_face: lashes (women), under-eye bags / smile corners (age, big smiles), fuller lower lip."""
    F = face_cfg.FACE[who]
    P = s72_build.B[who]["face"]
    mode = fp.FACE_EYES.get(facing, 0)
    if mode != 2:
        return
    eP, eM = anc["eyeP"], anc["eyeM"]
    if not (eP[2] and eM[2]):
        return
    H, W = idx.shape
    fl = lambda v: int(math.floor(v))
    ey = fl((eP[1] + eM[1]) / 2)
    xl, xr = sorted([fl(eP[0]), fl(eM[0])])
    if xr - xl < 2:
        c = (xl + xr) // 2
        xl, xr = c - 1, c + 1
    SK = ctx["skin_set"]

    def put(x, y, c, skin_only=True):
        if 0 <= x < W and 0 <= y < H and idx[y, x] != 0 and idx[y, x] != ctx["out"]:
            if not skin_only or idx[y, x] in SK:
                idx[y, x] = c
    for (x, out) in ((xl, -1), (xr, +1)):
        if F["female"]:
            put(x + out, ey, ctx["out"])                    # outer lash flick
        if P["age"] >= 1:
            put(x, ey + 2, ctx["skin_shade"])               # under-eye bag
        if P["brow_w"] >= 1.2:
            put(x - out, ey - 1, ctx["brow"])               # heavy brow runs further towards the nose
    mx, my = anc["mouth"][0], anc["mouth"][1]
    my = max(int(round(my - 0.2)), ey + 3)
    if facing == "s":
        if F["female"]:
            put(fl(mx - 0.5), my + 1, ctx["blush"])         # lower lip
            put(fl(mx + 0.5), my + 1, ctx["blush"])
        if P["smile"] >= 0.7:
            put(fl(mx - 1.5), my - 1, ctx["skin_shade"])    # smile creases
            put(fl(mx + 2.5), my - 1, ctx["skin_shade"])
    else:
        if F["female"]:
            put(fl(mx), my + 1, ctx["blush"])


def run(step, OUT, NAMES, SS):
    if step == "sprites":
        sprites(OUT, NAMES, SS)
    elif step == "compose":
        compose(OUT, NAMES)


def sprites(OUT, NAMES, SS):
    for n in NAMES:
        d = os.path.join(OUT, "r_" + n)
        stems = [f"{f}_{i}" for f in FACINGS for i in range(3)]
        frames = [sprite_frame(os.path.join(d, s + ".png"), SS, FW, FH) for s in stems]
        anchors = json.load(open(os.path.join(d, "anchors.json")))
        skin = s72_build.B[n]["colours"]["Skin"]
        pal, idxs = fp.quantize_sheet(frames, fp.reserved_colours(n, skin))
        ctx = fp.make_ctx(pal, n, skin)
        for st, idx in zip(stems, idxs):
            fp.paint_face(idx, anchors[st], ctx, st.split("_")[0])
            extra_paint(idx, anchors[st], ctx, st.split("_")[0], n)
        pickle.dump(dict(stems=stems, pal=pal, idx=idxs, anchors=anchors), open(os.path.join(OUT, f"spr_{n}.pkl"), "wb"))
        print("sprites", n, flush=True)


def to_rgba(idx, pal):
    out = np.zeros(idx.shape + (4,), np.uint8)
    for i in range(1, 16):
        out[idx == i] = list(int(v) for v in pal[i]) + [255]
    return Image.fromarray(out, "RGBA")


def load_new(OUT, n):
    d = pickle.load(open(os.path.join(OUT, f"spr_{n}.pkl"), "rb"))
    return {s: to_rgba(i, d["pal"]) for s, i in zip(d["stems"], d["idx"])}, d


def load_cur(n):
    """Current game sprites: graphics/npc_<id>.bmp (8 facings idle) or player.bmp (8 facings x 9 frames). -> {stem: RGBA}"""
    path = os.path.join(ROOT, "graphics", ("player" if n == "player" else "npc_" + n) + ".bmp")
    im = Image.open(path)
    pal = im.getpalette()
    a = np.array(im)
    per = (a.shape[0] // FH // 8) if n == "player" else 1
    out = {}
    for f in FACINGS:
        for i in range(3 if n == "player" else 1):
            k = GAME_ORDER.index(f) * per + i
            fr = a[k * FH:(k + 1) * FH]
            rgba = np.zeros((FH, FW, 4), np.uint8)
            for c in range(1, 16):
                rgba[fr == c] = pal[3 * c:3 * c + 3] + [255]
            out[f"{f}_{i}"] = Image.fromarray(rgba, "RGBA")
    return out


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


LABEL = dict(player="You (player)", mia="Mia", rosa="Rosa", dex="Dex", pimm="Mr. Pimm", lou="Big Lou", victor="Victor Vault",
             okafor="Dr. Okafor", robot="Valet (unchanged)")


def paste(sheet, im, x, y, z):
    sheet.alpha_composite(im.resize((im.width * z, im.height * z), Image.NEAREST), (x, y))


def compose(OUT, NAMES):
    BG = (176, 188, 168, 255)
    ft, fs = font(15), font(12)
    new = {n: load_new(OUT, n)[0] for n in NAMES}
    cur = {n: load_cur(n) for n in list(NAMES) + ["robot"]}
    # ---- (a) lineup: current vs proposal, facings s / se / e at 3x, feet aligned
    groups = [["player", "mia", "rosa", "dex"], ["pimm", "lou", "victor", "okafor", "robot"]]
    Z = 3
    cw = 3 * FW * Z + 18
    W = max(len(g) for g in groups) * cw + 90
    rowh = FH * Z + 8
    H = len(groups) * (2 * rowh + 52) + 10
    sheet = Image.new("RGBA", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    y = 8
    for g in groups:
        for gi, n in enumerate(g):
            x0 = 90 + gi * cw
            dr.text((x0 + 4, y), LABEL[n], fill=(20, 20, 30, 255), font=ft)
        for r, (lab, src) in enumerate((("Current", cur), ("Proposal", new))):
            yy = y + 24 + r * rowh
            dr.text((6, yy + FH * Z // 2), lab, fill=(20, 20, 30, 255), font=ft)
            dr.line([(88, yy + 54 * Z + 8), (W - 4, yy + 54 * Z + 8)], fill=(120, 130, 115, 255))
            for gi, n in enumerate(g):
                s = cur["robot"] if (n == "robot") else src[n]
                for fi, f in enumerate(FACINGS):
                    paste(sheet, s[f"{f}_0"], 90 + gi * cw + fi * FW * Z, yy, Z)
        y += 2 * rowh + 52
    sheet.convert("RGB").save(os.path.join(OUT, "1_lineup_current_vs_proposal.png"))

    # ---- (b) face close-ups at 6x: head crop of current (s, se) and proposal (s, se, e)
    Z = 6
    CW, CH = 22, 24

    def head_crop(im):
        a = np.array(im)[..., 3] > 0
        rows = np.where(a.any(1))[0]
        top = rows[0]
        cols = np.where(a[top:top + 12].any(0))[0]
        cx = int(round((cols.min() + cols.max()) / 2))
        box = (cx - CW // 2, top - 1, cx - CW // 2 + CW, top - 1 + CH)
        c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        c.alpha_composite(im.crop(box)) if False else c.paste(im.crop(box), (0, 0))
        return c
    cols = [("Current s", cur, "s_0"), ("Current se", cur, "se_0"), ("Proposal s", new, "s_0"), ("Proposal se", new, "se_0"), ("Proposal e", new, "e_0")]
    cellw, cellh = CW * Z + 8, CH * Z + 8
    sheet = Image.new("RGBA", (110 + len(cols) * cellw, 28 + len(NAMES) * cellh), BG)
    dr = ImageDraw.Draw(sheet)
    for ci, (lab, _, _) in enumerate(cols):
        dr.text((110 + ci * cellw + 6, 6), lab, fill=(20, 20, 30, 255), font=ft)
    for ri, n in enumerate(NAMES):
        dr.text((6, 28 + ri * cellh + CH * Z // 2 - 8), LABEL[n], fill=(20, 20, 30, 255), font=ft)
        for ci, (lab, src, key) in enumerate(cols):
            paste(sheet, head_crop(src[n][key]), 110 + ci * cellw + 4, 28 + ri * cellh + 4, Z)
    sheet.convert("RGB").save(os.path.join(OUT, "2_face_closeups_6x.png"))

    # ---- (c) idle + 2 walk frames, 3 facings, proposal, 2x
    Z = 2
    pw = 9 * FW * Z + 14
    sheet = Image.new("RGBA", (2 * pw + 10, 4 * (FH * Z + 26) + 6), BG)
    dr = ImageDraw.Draw(sheet)
    for ni, n in enumerate(NAMES):
        x0 = 6 + (ni % 2) * pw
        y0 = 4 + (ni // 2) * (FH * Z + 26)
        dr.text((x0, y0), LABEL[n], fill=(20, 20, 30, 255), font=fs)
        for fi, f in enumerate(FACINGS):
            for i in range(3):
                paste(sheet, new[n][f"{f}_{i}"], x0 + (fi * 3 + i) * FW * Z, y0 + 14, Z)
    sheet.convert("RGB").save(os.path.join(OUT, "3_idle_walk_frames_2x.png"))

    mock(OUT, new)


# ---------------------------------------------------------------------------------------------- in-game mock (diner)
def read_palette(name):
    t = open(os.path.join(ROOT, "src", "tl_world_data.cpp")).read()
    m = re.search(r"constexpr bn::color %s\[\] = \{(.*?)\};" % name, t, re.S)
    cols = [tuple(int(v) * 8 for v in c) for c in re.findall(r"bn::color\((\d+), (\d+), (\d+)\)", m.group(1))]
    return [cols[i:i + 16] for i in range(0, len(cols), 16)]


def layer_image(name, tw, th):
    pal = read_palette(name + "_palette")
    words = np.fromfile(os.path.join(ROOT, "data", name + "_tiles.bin"), dtype="<u4").reshape(-1, 8)
    cells = np.fromfile(os.path.join(ROOT, "data", name + "_cells.bin"), dtype="<u4").reshape(th, tw)
    out = np.zeros((th * 8, tw * 8, 4), np.uint8)
    for cy in range(th):
        for cx in range(tw):
            c = int(cells[cy, cx])
            tid = c & 0xFFFF
            if tid == 0 and name.endswith("objects"):
                continue
            d = np.array([[(int(words[tid][r]) >> (4 * x)) & 15 for x in range(8)] for r in range(8)])
            if c >> 16 & 1:
                d = d[:, ::-1]
            if c >> 17 & 1:
                d = d[::-1, :]
            p = pal[(c >> 20) & 15]
            for v in range(16):
                if name.endswith("objects") and v == 0:
                    continue
                m = d == v
                if m.any():
                    out[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8][m] = list(p[v]) + [255]
    return Image.fromarray(out, "RGBA")


def mock(OUT, new):
    IW, IH, OX, OY = 384, 272, 184, 64
    floor = layer_image("diner_floor", IW // 8, IH // 8)
    objs = layer_image("diner_objects", IW // 8, IH // 8)
    base = floor.copy()
    base.alpha_composite(objs)
    base.convert("RGB").save(os.path.join(OUT, "diner_map_debug.png"))
    cast = [("lou", 6.4, 2.6, "s_0", True), ("mia", 9.3, 4.7, "s_0", False), ("pimm", 9.4, 6.6, "se_0", False),
            ("player", 7.2, 6.2, "e_0", False), ("dex", 4.4, 7.5, "se_0", False)]
    comp = floor.copy()
    comp.alpha_composite(objs)
    for n, x, y, key, behind in cast:
        ix = OX + (x - y) * 16
        iy = OY + (x + y) * 8
        spr = new[n][key]
        if behind:                       # behind the counter: redraw the objects layer over his legs
            lay = floor.copy()
            lay.alpha_composite(objs)
            lay.alpha_composite(spr, (int(ix - 16), int(iy - 54)))
            keep = objs.copy()
            m = Image.new("L", objs.size, 0)
            ImageDraw.Draw(m).rectangle([ix - 26, iy - 14, ix + 26, iy + 20], fill=255)
            a = objs.split()[3]
            from PIL import ImageChops
            keep.putalpha(ImageChops.multiply(a, m))
            lay.alpha_composite(keep)
            comp = lay
        else:
            comp.alpha_composite(spr, (int(ix - 16), int(iy - 54)))
    cx, cy = 196, 150
    view = comp.crop((cx - 120, cy - 64, cx + 120, cy + 64))
    hud = Image.new("RGBA", (240, 32), (36, 30, 44, 255))
    d = ImageDraw.Draw(hud)
    d.rectangle([4, 4, 56, 27], fill=(70, 56, 80, 255))
    d.text((8, 8), "8:00 am", fill=(240, 230, 200, 255), font=font(9))
    d.text((8, 18), "$20", fill=(240, 200, 70, 255), font=font(9))
    for i in range(6):
        d.rectangle([66 + i * 28, 8, 66 + i * 28 + 22, 22], fill=(60, 50, 70, 255))
        d.rectangle([68 + i * 28, 16, 66 + i * 28 + 20 - (i * 3), 20], fill=(80, 200, 90, 255))
    screen = Image.new("RGBA", (240, 160), (0, 0, 0, 255))
    screen.paste(view, (0, 0))
    screen.paste(hud, (0, 128))
    screen.convert("RGB").save(os.path.join(OUT, "4_mock_diner_1x.png"))
    screen.convert("RGB").resize((720, 480), Image.NEAREST).save(os.path.join(OUT, "5_mock_diner_3x.png"))
