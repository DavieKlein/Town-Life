#!/usr/bin/env python3
"""
Town Life - asset builder.

  python3 tools/build_assets.py [--rerender] [--fast] [--preview DIR]

1. Renders every scene in tools/scene.py with Blender (floor + objects layer), cached in
   art_cache/ (git-ignored). --rerender forces new renders, --fast uses low quality for testing.
2. Converts each layer to GBA 4bpp tiles: up to BANKS 16-colour palettes per layer; every 8x8 tile
   picks the palette that fits it best. Tiles are deduplicated (also flipped versions).
3. Writes the generated game data:
     src/tl_world_data.cpp     tiles, cells and palettes per layer + collision, warps, occluders
     include/tl_map_id.h       enum map_id
     graphics/hud.bmp/.json    HUD bar (4bpp)
     graphics/player.bmp/.json player sprite sheet
Requirements: Blender (apt-get install blender), numpy, Pillow.
"""

import hashlib
import os
import subprocess
import sys

import numpy as np
from PIL import Image

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import scene as scn          # noqa: E402
import hud_sprites           # noqa: E402
import critters              # noqa: E402
import interactions          # noqa: E402

CACHE = os.path.join(ROOT, "art_cache")
FLOOR_BANKS = 7
OBJECT_BANKS = 7
RENDER_SCALE = 2
RENDER_SAMPLES = 96


# ---------------------------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------------------------
def scene_hash(s, layer, scale, samples):
    h = hashlib.sha1()
    for f in ("scene.py", "blender_render.py"):
        h.update(open(os.path.join(TOOLS, f), "rb").read())
    h.update(f"{s.ident}{layer}{scale}{samples}".encode())
    return h.hexdigest()[:12]


def render(s, layer, force, fast):
    scale, samples = (1, 24) if fast else (RENDER_SCALE, RENDER_SAMPLES)
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, f"{s.ident}_{layer}_{scene_hash(s, layer, scale, samples)}.png")
    if force or not os.path.exists(out):
        print(f"rendering {s.ident} {layer} ({scale}x, {samples} samples)...", flush=True)
        cmd = ["blender", "-b", "-noaudio", "--python", os.path.join(TOOLS, "blender_render.py"), "--",
               s.ident, layer, out, str(scale), str(samples)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if not os.path.exists(out):
            print(r.stdout[-3000:], r.stderr[-3000:])
            raise RuntimeError("render failed")
    img = Image.open(out).convert("RGBA")
    if img.size != (s.img_w, s.img_h):
        # premultiplied box downscale
        a = np.asarray(img).astype(np.float64) / 255.0
        a[..., :3] *= a[..., 3:4]
        f = img.size[0] // s.img_w
        a = a.reshape(s.img_h, f, s.img_w, f, 4).mean(axis=(1, 3))
        rgb = np.where(a[..., 3:4] > 0, a[..., :3] / np.maximum(a[..., 3:4], 1e-6), 0)
        a = np.concatenate([rgb, a[..., 3:4]], axis=2)
        img = Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")
    return grade(img)


def grade(img):
    """Colour grade before quantization: a bit more contrast and saturation and cool, slightly
    purple shadows, for the moodier look of classic pre-rendered city games."""
    a = np.asarray(img).astype(np.float64) / 255.0
    rgb = a[..., :3]
    luma = (rgb * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    rgb = luma + (rgb - luma) * 1.15                                   # saturation
    rgb = np.clip(0.5 + (rgb - 0.5) * 1.1, 0, 1)                       # contrast
    shadow = np.clip(1.0 - luma / 0.45, 0, 1)                          # 1 in deep shadow
    rgb = rgb * (1 - 0.18 * shadow) + shadow * 0.18 * rgb * np.array([0.82, 0.8, 1.15])
    a[..., :3] = np.clip(rgb, 0, 1)
    return Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")


# ---------------------------------------------------------------------------------------------
# 4bpp multi-palette conversion
# ---------------------------------------------------------------------------------------------
WEIGHT = np.array([0.30, 0.59, 0.11]) ** 0.5


def to5(c):
    return np.clip(np.round(c / 8.0), 0, 31) * 8.0


def kmeans(points, k, weights=None, iters=12, seed=1):
    rng = np.random.default_rng(seed)
    n = len(points)
    if n <= k:
        return points.copy()
    if weights is None:
        weights = np.ones(n)
    # k-means++ init
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


def convert_layer(img, banks, transparent):
    """img: RGBA PIL image (dims multiple of 8). Returns (palettes[banks][16] rgb, cells, tiles)."""
    a = np.asarray(img).astype(np.float64)
    h, w = a.shape[0], a.shape[1]
    th, tw = h // 8, w // 8
    rgb = a[..., :3]
    opaque = a[..., 3] >= 128 if transparent else a[..., 3] >= 8
    tiles_rgb = rgb.reshape(th, 8, tw, 8, 3).transpose(0, 2, 1, 3, 4).reshape(th * tw, 64, 3) * WEIGHT
    tiles_op = opaque.reshape(th, 8, tw, 8).transpose(0, 2, 1, 3).reshape(th * tw, 64)
    used = np.where(tiles_op.any(1))[0]

    # initial bank assignment: k-means on tile mean colour + spread
    feats = []
    wts = []
    for t in used:
        px = tiles_rgb[t][tiles_op[t]]
        feats.append(np.concatenate([px.mean(0), px.std(0) * 0.5]))
        wts.append(len(px))
    feats = np.array(feats)
    wts = np.array(wts, dtype=np.float64)
    centers = kmeans(feats, banks, wts, iters=15)
    assign = ((feats[:, None, :] - centers[None]) ** 2).sum(2).argmin(1)

    palettes = None
    for it in range(4):
        palettes = []
        for b in range(banks):
            idx = used[assign == b]
            if len(idx) == 0:
                palettes.append(np.zeros((15, 3)))
                continue
            px = np.concatenate([tiles_rgb[t][tiles_op[t]] for t in idx])
            if len(px) > 40000:
                px = px[np.random.default_rng(it).choice(len(px), 40000, replace=False)]
            cols = kmeans(px, 15, iters=10, seed=b + it)
            if len(cols) < 15:
                cols = np.concatenate([cols, np.repeat(cols[-1:], 15 - len(cols), 0)])
            palettes.append(to5(cols / WEIGHT) * WEIGHT)
        palettes = np.array(palettes)                     # banks x 15 x 3 (weighted space)
        # reassign tiles to the best bank
        errs = np.zeros((len(used), banks))
        for c0 in range(0, len(used), 2048):
            chunk = used[c0:c0 + 2048]
            trgb = tiles_rgb[chunk]
            top = tiles_op[chunk]
            for b in range(banks):
                d = ((trgb[:, :, None, :] - palettes[b][None, None]) ** 2).sum(3).min(2)
                errs[c0:c0 + len(chunk), b] = (d * top).sum(1)
        new_assign = errs.argmin(1)
        if (new_assign == assign).all() and it > 0:
            break
        assign = new_assign

    # final indices
    tile_bank = np.zeros(th * tw, dtype=np.int32)
    tile_idx = np.zeros((th * tw, 64), dtype=np.uint8)
    for b in range(banks):
        sel = used[assign == b]
        for c0 in range(0, len(sel), 4096):
            chunk = sel[c0:c0 + 4096]
            d = ((tiles_rgb[chunk][:, :, None, :] - palettes[b][None, None]) ** 2).sum(3)
            idx = (d.argmin(2) + 1).astype(np.uint8)
            idx[~tiles_op[chunk]] = 0
            tile_idx[chunk] = idx
            tile_bank[chunk] = b

    pal_rgb = []
    for b in range(banks):
        cols = [(0, 0, 0)] + [tuple(int(v) for v in c) for c in to5(palettes[b] / WEIGHT)]
        pal_rgb.append(cols)

    # deduplicate tiles (tile 0 = empty)
    uniq = {bytes(64): 0}
    tiles = [bytes(64)]
    cells = np.zeros(th * tw, dtype=np.uint32)
    for t in range(th * tw):
        d = tile_idx[t].reshape(8, 8)
        if not d.any():
            continue
        variants = ((d, 0), (d[:, ::-1], 1), (d[::-1, :], 2), (d[::-1, ::-1], 3))
        found = None
        for v, flip in variants:
            key = v.tobytes()
            if key in uniq:
                found = (uniq[key], flip)
                break
        if found is None:
            uniq[d.tobytes()] = len(tiles)
            found = (len(tiles), 0)
            tiles.append(d.tobytes())
        tid, flip = found
        cells[t] = tid | ((flip & 1) << 16) | ((flip >> 1) << 17) | (int(tile_bank[t]) << 20)
    return pal_rgb, cells.reshape(th, tw), tiles


def layer_preview(pal, cells, tiles):
    th, tw = cells.shape
    out = np.zeros((th * 8, tw * 8, 3), dtype=np.uint8)
    for cy in range(th):
        for cx in range(tw):
            c = int(cells[cy, cx])
            tid = c & 0xFFFF
            if tid == 0:
                continue
            d = np.frombuffer(tiles[tid], dtype=np.uint8).reshape(8, 8)
            if c >> 16 & 1:
                d = d[:, ::-1]
            if c >> 17 & 1:
                d = d[::-1, :]
            p = np.array(pal[(c >> 20) & 15])
            out[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8] = p[d]
    return out


# ---------------------------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------------------------
def tile_words(t):
    d = np.frombuffer(t, dtype=np.uint8).reshape(8, 8)
    words = []
    for row in d:
        v = 0
        for x in range(8):
            v |= int(row[x]) << (4 * x)
        words.append(v)
    return words


def write_bmp(path, pixels, width, height, bpp, palette):
    import struct
    data = bytearray()
    for y in range(height - 1, -1, -1):
        row = bytearray()
        if bpp == 8:
            row.extend(bytes(pixels[y]))
        else:
            for x in range(0, width, 2):
                row.append(((pixels[y][x] & 0xF) << 4) | (pixels[y][x + 1] & 0xF))
        row.extend(b"\0" * ((-len(row)) % 4))
        data.extend(row)
    pal = bytearray()
    for r, g, b in palette:
        pal.extend(bytes((b, g, r, 0)))
    offset = 14 + 40 + len(pal)
    header = struct.pack("<2sIHHI", b"BM", offset + len(data), 0, 0, offset)
    info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, bpp, 0, len(data), 2835, 2835,
                       len(palette), len(palette))
    with open(path, "wb") as f:
        f.write(header + info + pal + data)


def write_text(path, text):
    with open(path, "w", newline="\n") as f:
        f.write(text)


EXTERNS = []


def emit_layer(out, name, pal, cells, tiles):
    """Tiles and cells go to data/<name>_tiles.bin / _cells.bin (linked by Butano's DATA rule);
    the palette stays in the generated C++ file."""
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    words = np.array([w for t in tiles for w in tile_words(t)], dtype="<u4")
    words.tofile(os.path.join(ROOT, "data", f"{name}_tiles.bin"))
    cells.astype("<u4").flatten().tofile(os.path.join(ROOT, "data", f"{name}_cells.bin"))
    EXTERNS.append(f'extern "C" const uint32_t {name}_tiles_bin[];')
    EXTERNS.append(f'extern "C" const uint32_t {name}_cells_bin[];')
    out.append(f"    constexpr int {name}_tiles_count = {len(tiles)};")
    out.append(f"    constexpr bn::color {name}_palette[] = {{")
    for bank in pal:
        out.append("        " + ", ".join(f"bn::color({r // 8}, {g // 8}, {b // 8})" for (r, g, b) in bank) + ",")
    out.append("    };")


# ---------------------------------------------------------------------------------------------
def main():
    force = "--rerender" in sys.argv
    fast = "--fast" in sys.argv
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
        os.makedirs(preview, exist_ok=True)

    scenes = [f() for f in scn.SCENES]
    names = [s.ident for s in scenes]
    out = ["// Generated by tools/build_assets.py - do not edit by hand.",
           '#include "tl_world.h"', "", '#include "bn_color.h"', "",
           "namespace tl", "{", "namespace", "{"]
    table = []
    for s in scenes:
        assert s.img_w % 8 == 0 and s.img_h % 8 == 0
        layers = {}
        for layer, banks, transparent in (("floor", FLOOR_BANKS, False), ("objects", OBJECT_BANKS, True)):
            img = render(s, layer, force, fast)
            pal, cells, tiles = convert_layer(img, banks, transparent)
            th, tw = cells.shape
            # worst case unique tiles visible in one 31x21 window (must fit the VRAM cache)
            ids = (cells & 0xFFFF).astype(np.int64)
            worst = 0
            for cy in range(0, max(1, th - 20), 2):
                for cx in range(0, max(1, tw - 30), 2):
                    worst = max(worst, len(np.unique(ids[cy:cy + 21, cx:cx + 31])))
            print(f"{s.ident} {layer}: {len(tiles)} unique tiles, worst window {worst}")
            layers[layer] = (pal, cells, tiles)
            emit_layer(out, f"{s.ident}_{layer}", pal, cells, tiles)
            if preview:
                Image.fromarray(layer_preview(pal, cells, tiles)).save(os.path.join(preview, f"{s.ident}_{layer}.png"))
        if preview:
            f = layer_preview(*layers["floor"])
            o = layer_preview(*layers["objects"])
            mask = (layers["objects"][1] & 0xFFFF) > 0
            comp = f.copy()
            m = np.kron(mask, np.ones((8, 8), dtype=bool))
            ob = o.astype(np.int32).sum(2) > 0
            comp[ob] = o[ob]
            Image.fromarray(comp).save(os.path.join(preview, f"{s.ident}.png"))

        # gameplay data
        out.append(f"    constexpr uint8_t {s.ident}_solid[] = {{")
        for cy in range(s.h):
            out.append("        " + ",".join("1" if s.solid[cy][cx] else "0" for cx in range(s.w)) + ",")
        out.append("    };")
        out.append(f"    constexpr warp {s.ident}_warps[] = {{")
        for (x0, y0, x1, y1, target, tx, ty, facing) in s.warps:
            assert target in names, target
            out.append(f"        {{ {int(x0 * 16)}, {int(y0 * 16)}, {int((x1 - x0) * 16)}, {int((y1 - y0) * 16)}, "
                       f"map_id::{target}, {int(tx * 16)}, {int(ty * 16)}, direction::{facing} }},")
        out.append("    };")
        out.append(f"    constexpr occluder {s.ident}_occluders[] = {{")
        for (x0, y0, x1, y1, hm) in s.occluders:
            sx0, _ = s.proj(x0, y1)
            sx1, _ = s.proj(x1, y0)
            _, sy0 = s.proj(x0, y0, hm)
            _, sy1 = s.proj(x1, y1)
            out.append(f"        {{ {int(x0 * 16)}, {int(y0 * 16)}, {int(x1 * 16)}, {int(y1 * 16)}, "
                       f"{int(sx0)}, {int(sy0)}, {int(sx1)}, {int(sy1)} }},")
        out.append("    };")
        out.append("")
        spawns = critters.SPAWNS.get(s.ident, [])
        if spawns:
            out.append(f"    constexpr critter_spawn {s.ident}_critters[] = {{")
            for sp in spawns:
                tx, ty = (sp[3], sp[4]) if len(sp) > 3 else (-1 / 16, -1 / 16)
                out.append(f"        {{ critter_kind::{sp[0]}, {int(sp[1] * 16)}, {int(sp[2] * 16)}, "
                           f"{int(tx * 16)}, {int(ty * 16)} }},")
            out.append("    };")
        critter_entry = (f"{s.ident}_critters, int(sizeof({s.ident}_critters) / sizeof(critter_spawn))"
                         if spawns else "nullptr, 0")
        things = interactions.INTERACTABLES.get(s.ident, [])
        if things:
            out.append(f"    constexpr interactable {s.ident}_interactables[] = {{")
            for t in things:
                radius = t[3] if len(t) > 3 else 0
                out.append(f"        {{ interactable_kind::{t[0]}, {int(t[1] * 16)}, {int(t[2] * 16)}, "
                           f"{int(radius * 16)} }},")
            out.append("    };")
        interact_entry = (f"{s.ident}_interactables, int(sizeof({s.ident}_interactables) / sizeof(interactable))"
                          if things else "nullptr, 0")
        xs = [s.proj(x, y)[0] for (x, y) in ((0, 0), (s.w, 0), (0, s.h), (s.w, s.h))]
        ys = [s.proj(x, y)[1] for (x, y) in ((0, 0), (s.w, 0), (0, s.h), (s.w, s.h))]
        view = (max(0, int(min(xs))), 0, min(s.img_w, int(max(xs))), min(s.img_h, int(max(ys)) + 8))

        def layer_entry(layer):
            n = f"{s.ident}_{layer}"
            return (f"{{ {n}_tiles_bin, {n}_tiles_count, {n}_cells_bin, {n}_palette, "
                    f"int(sizeof({n}_palette) / sizeof(bn::color)) / 16 }}")
        table.append(f'        {{ "{s.name}", {layer_entry("floor")}, {layer_entry("objects")}, {s.w}, {s.h}, '
                     f"{s.origin_x}, {s.origin_y}, {s.img_w}, {s.img_h}, {view[0]}, {view[1]}, {view[2]}, {view[3]}, "
                     f"{s.ident}_solid, {s.ident}_warps, int(sizeof({s.ident}_warps) / sizeof(warp)), "
                     f"{s.ident}_occluders, int(sizeof({s.ident}_occluders) / sizeof(occluder)), "
                     f"{critter_entry}, {interact_entry} }},")

    out += ["}", "", "namespace", "{", "    constexpr map_info maps[] = {"] + table + ["    };", "}", "",
            "static_assert(sizeof(maps) / sizeof(map_info) == maps_count);", "",
            "const map_info& get_map(map_id id)", "{", "    return maps[int(id)];", "}", "}", ""]
    ns = out.index("namespace tl")
    out = out[:ns] + EXTERNS + [""] + out[ns:]
    write_text(os.path.join(ROOT, "src", "tl_world_data.cpp"), "\n".join(out))

    ids = ["// Generated by tools/build_assets.py - do not edit by hand.", "#ifndef TL_MAP_ID_H",
           "#define TL_MAP_ID_H", "", "namespace tl", "{", "    enum class map_id", "    {"]
    ids += [f"        {n}," for n in names]
    ids += ["    };", "", f"    constexpr int maps_count = {len(names)};", "}", "", "#endif", ""]
    write_text(os.path.join(ROOT, "include", "tl_map_id.h"), "\n".join(ids))

    # HUD (4bpp, 16 colours)
    hud = hud_sprites.build_hud()
    pal = hud_sprites.PAL_COLOURS + [(0, 0, 0)] * (16 - len(hud_sprites.PAL_COLOURS))
    assert len(pal) == 16
    write_bmp(os.path.join(ROOT, "graphics", "hud.bmp"), hud.p, hud.w, hud.h, 4, pal)
    write_text(os.path.join(ROOT, "graphics", "hud.json"),
               '{\n    "type": "regular_bg",\n    "bpp_mode": "bpp_4"\n}\n')

    build_player(force, fast)
    build_player_actions(force, fast)
    build_critters(force, fast)
    build_ui_sprites()


CRITTER_FRAMES = {"pigeon": 5, "squirrel": 4}


def sprite_frame(path, ss, w, h):
    """Supersampled RGBA render -> (rgb float array, alpha mask) with a 1 px dark outline."""
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


def write_sprite_sheet(name, frames, w, h):
    """frames: list of (rgb, alpha). One shared 15-colour palette, outline colour reserved."""
    outline = np.array([40.0, 30.0, 40.0])
    px = np.concatenate([rgb[alpha] for rgb, alpha in frames]) * WEIGHT
    cols = to5(kmeans(px, 14, iters=15) / WEIGHT)
    cols = np.concatenate([cols, [outline]])
    palette = [(255, 0, 255)] + [tuple(int(v) for v in c) for c in to5(cols)]
    palette += [(0, 0, 0)] * (16 - len(palette))
    cw = cols * WEIGHT
    pixels = []
    for rgb, alpha in frames:
        d = ((rgb[..., None, :] * WEIGHT - cw[None, None]) ** 2).sum(3)
        idx = d.argmin(2) + 1
        idx[~alpha] = 0
        pixels.extend(idx.astype(np.uint8).tolist())
    write_bmp(os.path.join(ROOT, "graphics", name + ".bmp"), pixels, w, h * len(frames), 4, palette)
    write_text(os.path.join(ROOT, "graphics", name + ".json"),
               f'{{\n    "type": "sprite",\n    "height": {h}\n}}\n')


def build_ui_sprites():
    pixels, pal = hud_sprites.build_need_bar()
    pal = pal + [(0, 0, 0)] * (16 - len(pal))
    write_bmp(os.path.join(ROOT, "graphics", "need_bar.bmp"), pixels, 32, len(pixels), 4, pal)
    write_text(os.path.join(ROOT, "graphics", "need_bar.json"), '{\n    "type": "sprite",\n    "height": 8\n}\n')
    left, right, highlight, pal = hud_sprites.build_menu_panel()
    pal = pal + [(0, 0, 0)] * (16 - len(pal))
    for name, px, w, h in (("menu_left", left, 64, 64), ("menu_right", right, 32, 64),
                           ("menu_highlight", highlight, 32, 16)):
        write_bmp(os.path.join(ROOT, "graphics", name + ".bmp"), px, w, len(px), 4, pal)
        write_text(os.path.join(ROOT, "graphics", name + ".json"),
                   f'{{\n    "type": "sprite",\n    "height": {h}\n}}\n')


def build_player_actions(force, fast):
    """Interaction poses of the player (approved designs): sitting + sleeping on a bench
    (64x64 frames, origin at (32, 44)) and washing (32x64 frames, 8 facings x 4)."""
    import json
    ss, samples = (2, 16) if fast else (4, 48)
    colours = json.dumps(PLAYER_COLOURS)
    fbx = os.path.join(ROOT, "art_source", "quaternius_characters", PLAYER_MODEL + ".fbx")
    h = hashlib.sha1()
    for f in ("scene.py", "blender_render.py", "blender_actor.py"):
        h.update(open(os.path.join(TOOLS, f), "rb").read())
    h.update(f"actions{ss}{samples}{colours}{PLAYER_MODEL}".encode())
    out_dir = os.path.join(CACHE, "player_actions_" + h.hexdigest()[:12])
    last = os.path.join(out_dir, "wash_se_3.png")
    if force or not os.path.exists(last):
        print("rendering player actions...", flush=True)
        r = subprocess.run(["blender", "-b", "-noaudio", "--python", os.path.join(TOOLS, "blender_actor.py"),
                            "--", fbx, out_dir, str(ss), str(samples), colours, "0", "actions"],
                           capture_output=True, text=True)
        if not os.path.exists(last):
            print(r.stdout[-3000:], r.stderr[-3000:])
            raise RuntimeError("player action render failed")
    frames = [sprite_frame(os.path.join(out_dir, f"sit_{i}.png"), ss, 64, 64) for i in range(4)]
    frames.append(sprite_frame(os.path.join(out_dir, "lie_0.png"), ss, 64, 64))
    write_sprite_sheet("player_rest", frames, 64, 64)
    frames = [sprite_frame(os.path.join(out_dir, f"wash_{f}_{i}.png"), ss, FRAME_W, FRAME_H)
              for f in FACINGS for i in range(4)]
    write_sprite_sheet("player_wash", frames, FRAME_W, FRAME_H)


def build_critters(force, fast):
    """Pigeons and squirrels: static Everything Library models (CC BY 4.0, David OReilly) posed
    and rendered by tools/blender_critter.py into 32x32 frames."""
    ss, samples = (2, 16) if fast else (4, 48)
    h = hashlib.sha1()
    for f in ("scene.py", "blender_critter.py"):
        h.update(open(os.path.join(TOOLS, f), "rb").read())
    h.update(f"{ss}{samples}".encode())
    out_dir = os.path.join(CACHE, "critters_" + h.hexdigest()[:12])
    last = os.path.join(out_dir, "squirrel_3.png")
    if force or not os.path.exists(last):
        print("rendering animals...", flush=True)
        r = subprocess.run(["blender", "-b", "-noaudio", "--python", os.path.join(TOOLS, "blender_critter.py"),
                            "--", out_dir, str(ss), str(samples)], capture_output=True, text=True)
        if not os.path.exists(last):
            print(r.stdout[-3000:], r.stderr[-3000:])
            raise RuntimeError("animal render failed")
    for name, count in CRITTER_FRAMES.items():
        frames = [sprite_frame(os.path.join(out_dir, f"{name}_{i}.png"), ss, 32, 32) for i in range(count)]
        write_sprite_sheet(name, frames, 32, 32)


# ---------------------------------------------------------------------------------------------
# Player: rigged CC0 character (art_source/quaternius_characters) rendered by tools/blender_actor.py
# ---------------------------------------------------------------------------------------------
FACINGS = ["s", "sw", "w", "nw", "n", "ne", "e", "se"]   # clockwise screen directions
FRAMES_PER_FACING = 9                                     # idle + 8 walk frames
FRAME_W, FRAME_H = 32, 64
PLAYER_MODEL = "Male_LongSleeve"
# Our own protagonist outfit (material name -> sRGB): blue top, khaki trousers, brown hair.
PLAYER_COLOURS = {"Shirt": "#2f5aa8", "Pants": "#c8a46a", "Hair": "#5a3420", "Skin": "#f0c09a",
                  "Shoes": "#3a2a22", "Socks": "#f2efe6"}


def build_player(force, fast):
    import json
    ss, samples = (2, 16) if fast else (4, 48)
    colours = json.dumps(PLAYER_COLOURS)
    fbx = os.path.join(ROOT, "art_source", "quaternius_characters", PLAYER_MODEL + ".fbx")
    h = hashlib.sha1()
    for f in ("scene.py", "blender_render.py", "blender_actor.py"):
        h.update(open(os.path.join(TOOLS, f), "rb").read())
    h.update(f"{ss}{samples}{colours}{PLAYER_MODEL}".encode())
    out_dir = os.path.join(CACHE, "player_" + h.hexdigest()[:12])
    last = os.path.join(out_dir, f"se_{FRAMES_PER_FACING - 1}.png")
    if force or not os.path.exists(last):
        print("rendering player...", flush=True)
        r = subprocess.run(["blender", "-b", "-noaudio", "--python", os.path.join(TOOLS, "blender_actor.py"),
                            "--", fbx, out_dir, str(ss), str(samples), colours], capture_output=True, text=True)
        if not os.path.exists(last):
            print(r.stdout[-3000:], r.stderr[-3000:])
            raise RuntimeError("character render failed")

    frames = []
    for facing in FACINGS:
        for i in range(FRAMES_PER_FACING):
            img = np.asarray(Image.open(os.path.join(out_dir, f"{facing}_{i}.png")).convert("RGBA")).astype(np.float64)
            img /= 255.0
            img[..., :3] *= img[..., 3:4]
            img = img.reshape(FRAME_H, ss, FRAME_W, ss, 4).mean(axis=(1, 3))
            rgb = np.where(img[..., 3:4] > 0, img[..., :3] / np.maximum(img[..., 3:4], 1e-6), 0) * 255
            alpha = img[..., 3] >= 0.45
            frames.append((rgb, alpha))

    # dark outline around the silhouette (helps readability on busy backgrounds)
    outline_rgb = np.array([40.0, 30.0, 40.0])
    for rgb, alpha in frames:
        grown = alpha.copy()
        grown[1:, :] |= alpha[:-1, :]
        grown[:-1, :] |= alpha[1:, :]
        grown[:, 1:] |= alpha[:, :-1]
        grown[:, :-1] |= alpha[:, 1:]
        edge = grown & ~alpha
        rgb[edge] = outline_rgb
        alpha |= edge

    px = np.concatenate([rgb[alpha] for rgb, alpha in frames]) * WEIGHT
    cols = kmeans(px, 14, iters=15)
    cols = to5(cols / WEIGHT)
    cols = np.concatenate([cols, [outline_rgb]])
    palette = [(255, 0, 255)] + [tuple(int(v) for v in c) for c in to5(cols)]
    palette += [(0, 0, 0)] * (16 - len(palette))
    cw = cols * WEIGHT
    pixels = []
    for rgb, alpha in frames:
        d = ((rgb[..., None, :] * WEIGHT - cw[None, None]) ** 2).sum(3)
        idx = d.argmin(2) + 1
        idx[~alpha] = 0
        pixels.extend(idx.astype(np.uint8).tolist())
    write_bmp(os.path.join(ROOT, "graphics", "player.bmp"), pixels, FRAME_W, FRAME_H * len(frames), 4, palette)
    write_text(os.path.join(ROOT, "graphics", "player.json"), '{\n    "type": "sprite",\n    "height": 64\n}\n')

    # soft shadow under the feet (drawn with alpha blending)
    shadow = []
    for y in range(8):
        row = []
        for x in range(16):
            d = ((x + 0.5 - 8) / 7.5) ** 2 + ((y + 0.5 - 4) / 3.5) ** 2
            row.append(1 if d <= 1.0 else 0)
        shadow.append(row)
    write_bmp(os.path.join(ROOT, "graphics", "shadow.bmp"), shadow, 16, 8, 4,
              [(255, 0, 255), (16, 16, 24)] + [(0, 0, 0)] * 14)
    write_text(os.path.join(ROOT, "graphics", "shadow.json"), '{\n    "type": "sprite",\n    "height": 8\n}\n')

if __name__ == "__main__":
    main()
