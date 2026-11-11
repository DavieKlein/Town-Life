"""Render a crop of the proposal scene with both layers and compose it like the game (graded, 5-bit colour).
  python3 crop.py OUTPREFIX x0,y0,x1,y1 [samples] [zoom]     -> OUTPREFIX_floor.png / _objects.png / .png (composite)"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s49"))
import lib  # noqa: E402
prefix, box = sys.argv[1], sys.argv[2]
samples = sys.argv[3] if len(sys.argv) > 3 else "24"
zoom = int(sys.argv[4]) if len(sys.argv) > 4 else 2
procs = []
for layer in ("floor", "objects"):
    out = f"{prefix}_{layer}.png"
    procs.append(subprocess.Popen(["blender", "-b", "-noaudio", "--python", os.path.join(HERE, "render.py"), "--", "old_block", layer, out,
                                   "2", samples, box], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
for p in procs:
    p.wait()
im = lib.compose(prefix)
im.save(prefix + ".png")
lib.zoom(im, zoom).save(prefix + "_z.png")
print("ok", im.size)
