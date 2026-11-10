#!/usr/bin/env python3
"""s72 proposal driver (nothing in the game is touched; output goes to OUT only).

  python3 run.py OUT render [names] [--ss 4 --samples 48]   Blender renders -> OUT/r_<name>/<facing>_<i>.png (+ anchors.json)
  python3 run.py OUT peek [names]                           raw (unquantized) contact sheet OUT/peek.png
  python3 run.py OUT sprites                                quantize with the real face pass (+ s72 additions) -> OUT/spr_<name>.png
  python3 run.py OUT compose                                lineup / faces / walk sheet / mock screens
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(TOOLS, ".."))
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import s72_build  # noqa: E402

OUT = os.path.abspath(sys.argv[1])
STEP = sys.argv[2]
args = [a for a in sys.argv[3:] if not a.startswith("--")]
opts = {a.split("=")[0]: a.split("=")[1] for a in sys.argv[3:] if a.startswith("--") and "=" in a}
NAMES = args or s72_build.ORDER
SS = int(opts.get("--ss", 4))
SAMPLES = int(opts.get("--samples", 48))
FACINGS = ["s", "se", "e"]


def render():
    for n in NAMES:
        subprocess.run(["blender", "-b", "-noaudio", "--python", os.path.join(HERE, "s72_char.py"), "--", n,
                        os.path.join(OUT, "r_" + n), str(SS), str(SAMPLES)], check=True, capture_output=True)
        print("rendered", n, flush=True)


def peek():
    ims = []
    for n in NAMES:
        row = [Image.open(os.path.join(OUT, "r_" + n, f"{f}_0.png")).convert("RGBA").resize((128, 256), Image.LANCZOS) for f in FACINGS]
        ims.append(row)
    W = 128 * 3 * len(ims) // 1
    sheet = Image.new("RGBA", (128 * 3 * len(ims), 256), (150, 160, 150, 255))
    for i, row in enumerate(ims):
        for j, im in enumerate(row):
            sheet.alpha_composite(im, (i * 384 + j * 128, 0))
    sheet.convert("RGB").save(os.path.join(OUT, "peek.png"))


if STEP == "render":
    render()
elif STEP == "peek":
    peek()
else:
    import s72_post  # noqa: E402
    s72_post.run(STEP, OUT, NAMES, SS)
