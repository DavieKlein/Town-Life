"""Quick look at a crop with the real renderer, composed like the game (graded, 5-bit colour), no quantizer.
  python3 look.py IDENT x0,y0,x1,y1 OUT_PREFIX [samples] [zoom]"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s49"))
import lib  # noqa: E402
ident, box, prefix = sys.argv[1:4]
samples = sys.argv[4] if len(sys.argv) > 4 else "24"
zoom = int(sys.argv[5]) if len(sys.argv) > 5 else 2
ps = [subprocess.Popen(["blender", "-b", "-noaudio", "--python", os.path.join(HERE, "render.py"), "--", ident, l, f"{prefix}_{l}.png",
                        "2", samples, box], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for l in ("floor", "objects")]
for p in ps:
    p.wait()
im = lib.compose(prefix)
lib.zoom(im, zoom).save(prefix + ".png")
print("ok", im.size)
