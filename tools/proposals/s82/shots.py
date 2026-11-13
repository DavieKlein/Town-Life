"""Key-view crops of the proposal (real renderer) -> PNGs through the real grade + quantizer.
  python3 shots.py OUTDIR [samples]
Crops are cell rectangles (x0, y0, x1, y1, zmax metres) converted to image pixels with the scene projection."""
import os
import subprocess
import sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "s49"))
import build_assets as ba  # noqa: E402
import lib  # noqa: E402
import rev3  # noqa: E402

out = sys.argv[1]
samples = sys.argv[2] if len(sys.argv) > 2 else "48"
os.makedirs(out, exist_ok=True)
S = rev3.old_block_rev3()
VIEWS = {
    "A_market_square": (31, 24, 50, 42, 3.4),
    "B_north_row_west": (20, 17.5, 52, 24, 7.5),
    "C_cinema_east": (50, 17, 68, 25, 8.5),
    "D_orchard_row": (28, 50, 56, 61, 3.5),
}
procs = []
boxes = {}
for name, (x0, y0, x1, y1, zm) in VIEWS.items():
    pts = [S.proj(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (0, zm)]
    bx = (int(min(p[0] for p in pts)), int(min(p[1] for p in pts)), int(max(p[0] for p in pts)), int(max(p[1] for p in pts)))
    boxes[name] = bx
    for layer in ("floor", "objects"):
        f = f"{out}/{name}_{layer}.png"
        if not os.path.exists(f):
            procs.append(subprocess.Popen(["blender", "-b", "-noaudio", "--python", os.path.join(HERE, "render.py"), "--", "old_block", layer, f, "2", samples,
                                           "%d,%d,%d,%d" % bx], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        if len(procs) >= 3:
            procs.pop(0).wait()
for p in procs:
    p.wait()
for name in VIEWS:
    ims = {l: ba.grade(ba.sharpen(lib.down(Image.open(f"{out}/{name}_{l}.png")))) for l in ("floor", "objects")}
    w, h = ims["floor"].size
    w8, h8 = (w // 8) * 8, (h // 8) * 8
    res = {}
    for l, banks, tr in (("floor", 8, False), ("objects", 7, True)):
        pal, cells, tiles, info = ba.convert_layer(ims[l].crop((0, 0, w8, h8)), banks, tr, None, l)
        res[l] = (ba.layer_preview(pal, cells, tiles), info["drawn"])
    comp = res["floor"][0].copy()
    d = res["objects"][1]
    comp[d] = res["objects"][0][d]
    img = Image.fromarray(comp)
    img.save(f"{out}/{name}_1x.png")
    img.resize((img.width * 3, img.height * 3), Image.NEAREST).save(f"{out}/{name}.png")
    print(name, boxes[name], img.size)
