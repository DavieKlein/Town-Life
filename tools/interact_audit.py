"""Interactable audit (s82): python3 tools/interact_audit.py OUTDIR [map ids]
Rebuilds every map image from the generated data (data/<map>_<layer>_tiles/cells.bin + the palettes in src/tl_world_data.cpp, the same
composite build_assets --preview writes) and draws a numbered marker at every entry of tools/interactions.INTERACTABLES (red cross = the
point the game uses, circle = reach) and every NPC placement (blue dot). Writes OUTDIR/<map>_full.png (whole map, markers) and
OUTDIR/<map>_crops_NN.png (4x zoomed crops, 12 markers per sheet, labelled `idx kind (x,y)`), so a human can check that each interactable
sits exactly on a visible, recognisable object. Also prints a text table."""
import sys, os, re
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import scene as sc
import interactions as I
import cast


def palettes():
    txt = open(os.path.join(ROOT, "src", "tl_world_data.cpp")).read()
    out = {}
    for m in re.finditer(r"constexpr bn::color (\w+)_palette\[\] = \{\n(.*?)\n    \};", txt, re.S):
        cols = re.findall(r"bn::color\((\d+), (\d+), (\d+)\)", m.group(2))
        out[m.group(1)] = np.array([[int(a) * 255 // 31 for a in c] for c in cols], dtype=np.uint8)
    return out


def layer_image(name, pal, w8, h8):
    tiles = np.fromfile(os.path.join(ROOT, "data", name + "_tiles.bin"), dtype="<u4")
    cells = np.fromfile(os.path.join(ROOT, "data", name + "_cells.bin"), dtype="<u4")[:w8 * h8].reshape(h8, w8)
    out = np.zeros((h8 * 8, w8 * 8, 3), dtype=np.uint8)
    have = np.zeros((h8 * 8, w8 * 8), dtype=bool)
    shifts = np.arange(8) * 4
    for cy in range(h8):
        for cx in range(w8):
            c = int(cells[cy, cx])
            tid = c & 0xFFFF
            if tid == 0:
                continue
            words = tiles[tid * 8:tid * 8 + 8]
            d = ((words[:, None] >> shifts[None, :]) & 15).astype(np.int64)
            if c >> 16 & 1:
                d = d[:, ::-1]
            if c >> 17 & 1:
                d = d[::-1, :]
            p = pal[((c >> 20) & 15) * 16:((c >> 20) & 15) * 16 + 16]
            out[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8] = p[d]
            have[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8] = d > 0
    return out, have


def map_image(s, pals):
    w8, h8 = s.img_w // 8, s.img_h // 8
    f, _ = layer_image(s.ident + "_floor", pals[s.ident + "_floor"], w8, h8)
    o, have = layer_image(s.ident + "_objects", pals[s.ident + "_objects"], w8, h8)
    f[have] = o[have]
    return Image.fromarray(f)


def main():
    out = sys.argv[1]
    only = set(sys.argv[2:])
    os.makedirs(out, exist_ok=True)
    pals = palettes()
    for fn in sc.SCENES:
        s = fn()
        if only and s.ident not in only:
            continue
        if s.ident + "_floor" not in pals:
            continue
        im = map_image(s, pals).convert("RGB")

        def proj(x, y, z=0.0):
            return s.origin_x + (x - y) * 16, s.origin_y + (x + y) * 8 - z * sc.PX_PER_M_Z

        marks = []
        for i, it in enumerate(I.INTERACTABLES.get(s.ident, [])):
            marks.append((i, it[0], it[1], it[2], it))
        d = ImageDraw.Draw(im)
        for (i, kind, x, y, it) in marks:
            px, py = proj(x, y)
            d.line((px - 5, py - 5, px + 5, py + 5), fill=(255, 0, 0), width=2)
            d.line((px - 5, py + 5, px + 5, py - 5), fill=(255, 0, 0), width=2)
            d.text((px + 6, py - 12), str(i), fill=(255, 255, 0))
        for p in cast.PLACEMENTS:
            if p[1] == s.ident:
                px, py = proj(p[2], p[3])
                d.ellipse((px - 3, py - 3, px + 3, py + 3), outline=(0, 200, 255))
        im.save(os.path.join(out, s.ident + "_full.png"))
        # crops
        base = map_image(s, pals).convert("RGB")
        crops = []
        for (i, kind, x, y, it) in marks:
            px, py = proj(x, y)
            box = (int(px - 40), int(py - 52), int(px + 40), int(py + 20))
            c = base.crop(box).resize((320, 288), Image.NEAREST)
            dd = ImageDraw.Draw(c)
            cx, cy = (px - box[0]) * 4, (py - box[1]) * 4
            dd.line((cx - 10, cy - 10, cx + 10, cy + 10), fill=(255, 0, 0), width=3)
            dd.line((cx - 10, cy + 10, cx + 10, cy - 10), fill=(255, 0, 0), width=3)
            dd.text((4, 4), "%d %s (%.1f,%.1f)" % (i, kind, x, y), fill=(255, 255, 0))
            crops.append(c)
            print("%s %2d %-12s (%.2f, %.2f) %s" % (s.ident, i, kind, x, y, it[3:]))
        for k in range(0, len(crops), 12):
            sheet = Image.new("RGB", (4 * 320, 3 * 288), (20, 20, 20))
            for j, c in enumerate(crops[k:k + 12]):
                sheet.paste(c, ((j % 4) * 320, (j // 4) * 288))
            sheet.save(os.path.join(out, "%s_crops_%02d.png" % (s.ident, k // 12)))


if __name__ == "__main__":
    main()
