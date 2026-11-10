#!/usr/bin/env python3
"""s71 style proposal driver (nothing in the game is touched; output goes to OUT only).

  python3 run.py OUT render      # Blender crop renders (cur / v1 / v2; v3 reuses cur) -> OUT/renders/*.png + timing.json
  python3 run.py OUT actors      # Blender actor renders (player, Mia) for the 4 variants
  python3 run.py OUT compose     # quantize (real quantizer), stats, comparison PNGs, GBA-size mock screens
"""
import io
import json
import os
import re
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(TOOLS, ".."))
OUT = os.path.abspath(sys.argv[1])
STEP = sys.argv[2]
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)

CROPS = {"fountain": ("city_centre", "1044,868,1292,1036"),
         "market": ("corner_market", "150,160,398,328")}
VARS = ["cur", "v1", "v2", "v3"]
LABEL = {"cur": "CURRENT", "v1": "V1 Soft", "v2": "V2 Rich", "v3": "V3 Smooth colour"}
SAMPLES = 192
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
os.makedirs(OUT + "/renders", exist_ok=True)


def render_crops():
    from concurrent.futures import ThreadPoolExecutor
    tj = OUT + "/renders/timing.json"
    timing = json.load(open(tj)) if os.path.exists(tj) else {}
    jobs = []
    for v in ("cur", "v1", "v2"):
        for name, (scene, box) in CROPS.items():
            for layer in ("floor", "objects"):
                f = f"{OUT}/renders/{name}_{v}_{layer}.png"
                if not os.path.exists(f):
                    jobs.append((v, name, scene, box, layer, f))

    def one(job):
        v, name, scene, box, layer, f = job
        t0 = time.time()
        r = subprocess.run(["blender", "-b", "-noaudio", "--python", HERE + "/s71_render.py", "--", v, scene, layer, f,
                            "2", str(SAMPLES), box], capture_output=True, text=True)
        wall = time.time() - t0
        m = re.findall(r"Time: ?(\d+):(\d+\.\d+) \(", r.stdout)
        cyc = float(m[-1][0]) * 60 + float(m[-1][1]) if m else None
        build = re.findall(r"\[s71 +([\d.]+)s\] build done", r.stdout)
        timing[f"{name}_{v}_{layer}"] = dict(wall=wall, render_total=cyc, build_py=float(build[-1]) if build else None)
        json.dump(timing, open(tj, "w"), indent=1)
        print(name, v, layer, f"{wall:.0f}s", timing[f"{name}_{v}_{layer}"], flush=True)
        if not os.path.exists(f):
            print(r.stdout[-1500:], r.stderr[-1500:])

    with ThreadPoolExecutor(2) as ex:
        list(ex.map(one, jobs))


ACTORS = {"cur": (4, 48), "v1": (4, 48), "v2": (4, 48), "v3": (6, 128)}


def render_actors():
    for v in VARS:
        for who in ("player", "mia"):
            d = f"{OUT}/actors/{v}_{who}"
            if os.path.exists(d + "/se_0.png") and os.path.exists(d + "/anchors.json"):
                continue
            ss, sm = ACTORS[v]
            t0 = time.time()
            subprocess.run(["blender", "-b", "-noaudio", "--python", HERE + "/s71_actor.py", "--", v, who, d, str(ss), str(sm)],
                           capture_output=True, text=True)
            print("actor", v, who, f"{time.time() - t0:.0f}s", flush=True)


# --------------------------------------------------------------------------------------------- compose
def zoom(im, n):
    return im.resize((im.width * n, im.height * n), Image.NEAREST)


def label(im, text, h=22):
    out = Image.new("RGB", (im.width, im.height + h), (24, 24, 30))
    out.paste(im, (0, h))
    ImageDraw.Draw(out).text((6, 3), text, font=ImageFont.truetype(FONT, 14), fill=(255, 220, 120))
    return out


def quantize_all():
    import build_assets as ba
    import variants as V
    sys.path.insert(0, os.path.join(TOOLS, "proposals", "s49"))
    import lib
    W, H = 248, 168
    res = {}
    for v in VARS:
        src = "cur" if v == "v3" else v
        canv = {l: Image.new("RGBA", (2 * W, H), (0, 0, 0, 0)) for l in ("floor", "objects")}
        for i, name in enumerate(CROPS):
            for l in canv:
                im = lib.down(Image.open(f"{OUT}/renders/{name}_{src}_{l}.png"))
                canv[l].paste(V.process(im, v), (i * W, 0))
        # un-quantized reference (graded, 5-bit)
        ref = Image.new("RGBA", canv["floor"].size, (10, 12, 24, 255))
        ref.alpha_composite(canv["floor"])
        ref.alpha_composite(canv["objects"])
        ref = np.asarray(lib.to555(ref)).astype(np.float64)
        out = {}
        for l, banks, tr in (("floor", 8, False), ("objects", 7, True)):
            pal, cells, tiles, info = V.convert(canv[l], banks, tr, l, v)
            out[l] = (ba.layer_preview(pal, cells, tiles), info["drawn"], cells, len(tiles))
        comp = out["floor"][0].copy()
        d = out["objects"][1]
        comp[d] = out["objects"][0][d]
        res[v] = dict(img=comp, stats={})
        for i, name in enumerate(CROPS):
            sl = slice(i * W, (i + 1) * W)
            st = {}
            for l in ("floor", "objects"):
                cells = out[l][2][:, i * 31:(i + 1) * 31]
                ids = np.unique(cells & 0xFFFF)
                st[l] = int((ids > 0).sum())
            st["mae"] = float(np.abs(comp[:, sl].astype(np.float64) - ref[:, sl]).mean())
            res[v]["stats"][name] = st
        print(v, json.dumps(res[v]["stats"]), flush=True)
    return res, W, H


def crops_compare(res, W, H):
    for i, name in enumerate(CROPS):
        tiles = []
        for v in VARS:
            c = Image.fromarray(res[v]["img"][:, i * W:(i + 1) * W]).convert("RGB")
            st = res[v]["stats"][name]
            tiles.append(label(zoom(c, 2), f"{LABEL[v]}   tiles floor {st['floor']} + obj {st['objects']}"))
        sheet = Image.new("RGB", (sum(t.width for t in tiles) + 6 * 3, tiles[0].height), (0, 0, 0))
        x = 0
        for t in tiles:
            sheet.paste(t, (x, 0))
            x += t.width + 6
        sheet.save(f"{OUT}/s71_{name}_compare.png")


def sprite_sheets():
    """Quantize the 8 idle facings of player and Mia per variant with the real face-pass pipeline (captured, not written)."""
    import build_assets as ba
    import face_pass
    import cast
    import variants as V
    out = {}
    captured = {}
    ba.write_bmp = lambda path, pixels, w, h, bpp, pal: captured.update(px=pixels, pal=pal, w=w, h=h)
    ba.write_text = lambda *a, **k: None
    orig_frame = ba.sprite_frame
    orig_km = ba.kmeans

    def frame_selective(path, ss, w, h):
        """v3: 1 px outline in a darkened copy of the neighbouring body colour instead of one flat near-black."""
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
        pad = np.pad(rgb * alpha[..., None], ((1, 1), (1, 1), (0, 0)))
        pa = np.pad(alpha.astype(float), 1)
        s = sum(np.roll(np.roll(pad, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1))[1:-1, 1:-1]
        n = sum(np.roll(np.roll(pa, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1))[1:-1, 1:-1]
        near = s / np.maximum(n, 1)[..., None]
        rgb[edge] = np.clip(near[edge] * 0.38 + np.array([14, 8, 22]), 0, 255)
        return rgb, alpha | edge

    for v in VARS:
        ss = ACTORS[v][0]
        for who in ("player", "mia"):
            d = f"{OUT}/actors/{v}_{who}"
            ba.sprite_frame = frame_selective if v == "v3" else orig_frame
            if v == "v3":
                ba.kmeans = face_pass.kmeans = V.kmeans_lab
            stems = [f"{f}_0" for f in ba.FACINGS]
            frames = [ba.sprite_frame(f"{d}/{s}.png", ss, 32, 64) for s in stems]
            anchors = json.load(open(d + "/anchors.json"))
            skin = ba.PLAYER_COLOURS["Skin"] if who == "player" else cast.CHARS[who]["colours"]["Skin"]
            ba.write_face_sheet("s71_" + who, frames, stems, list(ba.FACINGS), 32, 64, anchors, who if who != "player" else "player", skin)
            pal = captured["pal"]
            px = np.array(captured["px"], dtype=np.int64)
            sheet = np.zeros((px.shape[0], 32, 4), dtype=np.uint8)
            for ci, c in enumerate(pal):
                if ci == 0:
                    continue
                sheet[px == ci, :3] = c
            sheet[px > 0, 3] = 255
            out[(v, who)] = {f: Image.fromarray(sheet[i * 64:(i + 1) * 64], "RGBA") for i, f in enumerate(ba.FACINGS)}
            ba.kmeans = face_pass.kmeans = orig_km
    ba.sprite_frame = orig_frame
    return out


def sprites_compare(spr):
    cols = []
    for v in VARS:
        bg = Image.new("RGBA", (4 * 40, 72), (122, 116, 104, 255))
        for k, (who, f) in enumerate((("player", "se"), ("player", "sw"), ("mia", "se"), ("mia", "sw"))):
            sh = Image.new("RGBA", (16, 8), (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse((0, 0, 15, 7), fill=(20, 18, 28, 120))
            bg.alpha_composite(sh, (k * 40 + 12, 54 + 2 + 4 - 2 + 0))
            bg.alpha_composite(spr[(v, who)][f], (k * 40 + 4, 3))
        cols.append(label(zoom(bg.convert("RGB"), 3), LABEL[v] + " - You / Mia"))
    sheet = Image.new("RGB", (sum(c.width for c in cols) + 18, cols[0].height))
    x = 0
    for c in cols:
        sheet.paste(c, (x, 0))
        x += c.width + 6
    sheet.save(f"{OUT}/s71_sprites_compare.png")


def hud_strip():
    bg = Image.open(f"{ROOT}/graphics/hud.bmp").convert("RGB")
    strip = bg.crop((8, 176, 248, 208)).copy()
    d = ImageDraw.Draw(strip)
    vals = (62, 80, 70, 55, 75, 60)
    for s, vv in enumerate(vals):
        fill = round(vv / 100 * 20)
        col = (88, 200, 88) if fill > 12 else (232, 160, 48) if fill > 6 else (200, 56, 48)
        x = 58 + 30 * s
        d.rectangle((x, 23, x + 19, 25), fill=(60, 24, 28))
        d.rectangle((x, 23, x + max(fill - 1, 0), 25), fill=col)
    f11 = ImageFont.truetype(FONT, 11)
    f9 = ImageFont.truetype(FONT, 9)
    d.text((13, 1), "8:00", font=f11, fill=(255, 255, 255), stroke_width=1, stroke_fill=(20, 24, 48))
    d.text((13, 16), "$20", font=f11, fill=(255, 210, 60), stroke_width=1, stroke_fill=(20, 24, 48))
    d.text((38, 1), "am", font=f9, fill=(255, 255, 255))
    return strip


def mocks(res, W, H, spr):
    shots = {}
    hud = hud_strip()
    fx, fy = 108, 118          # feet position inside the 248x168 fountain crop (walkable paving south-west of the fountain)
    for v in VARS:
        base = Image.fromarray(res[v]["img"][:, :W]).convert("RGBA")
        sh = Image.new("RGBA", (16, 8), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse((0, 0, 15, 7), fill=(20, 18, 28, 110))
        base.alpha_composite(sh, (fx - 8, fy - 4))
        base.alpha_composite(spr[(v, "player")]["se"], (fx - 16, fy - 54))
        view = base.crop((4, 20, 244, 148)).convert("RGB")
        screen = Image.new("RGB", (240, 160))
        screen.paste(view, (0, 0))
        screen.paste(hud, (0, 128))
        shots[v] = screen
        zoom(screen, 3).save(f"{OUT}/s71_mock_{v}_3x.png")
    tiles = [label(zoom(shots[v], 2), LABEL[v]) for v in VARS]
    sheet = Image.new("RGB", (480 * 2 + 6, tiles[0].height * 2 + 6))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * 486, (i // 2) * (t.height + 6)))
    sheet.save(f"{OUT}/s71_mock_all_2x.png")
    for v in VARS:
        shots[v].save(f"{OUT}/s71_mock_{v}_1x.png")


def compose():
    res, W, H = quantize_all()
    crops_compare(res, W, H)
    spr = sprite_sheets()
    sprites_compare(spr)
    mocks(res, W, H, spr)
    json.dump({v: res[v]["stats"] for v in VARS}, open(OUT + "/stats.json", "w"), indent=1)


{"render": render_crops, "actors": render_actors, "compose": compose}[STEP]()
