#!/usr/bin/env python3
"""s62: in-game mocks inside VaultMart (240x160, real HUD strip, real player + Valet sprites).
  python3 mock_vm.py OUTDIR      (needs out/vma_q.png, out/vmb_q.png)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/tmp/claude-0/s62/tools/proposals/ui_objects")
import ui_mock as um
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
G = "/tmp/claude-0/s62/graphics"
hud = Image.open("/tmp/claude-0/s52/out/hud3.png").convert("RGB").crop((0, 128, 240, 160))
pl = Image.open("/tmp/claude-0/s52/out/player_rgba.png")
FACE = dict(s=0, sw=1, w=2, nw=3, n=4, ne=5, e=6, se=7)


def sheet(name):
    im = Image.open(f"{G}/{name}.bmp")
    arr = np.array(im.convert("RGBA"))
    arr[np.array(im) == 0] = (0, 0, 0, 0)
    return Image.fromarray(arr)


valet = sheet("npc_robot")
dexv = sheet("npc_dex_vault")
W, H = 17, 18


def proj(x, y):
    return H * 16 + 24 + 16 * (x - y), 64 + 8 * (x + y)


def frame(sh, f):
    n = FACE[f]
    return sh.crop((0, n * 64, 32, n * 64 + 64))


def shot(q, player, npcs, menu=None, cue=None, left=None, top=None):
    ix, iy = (int(round(v)) for v in proj(*player[:2]))
    mw, mh = q.size
    cx = max(0, min(mw - 240, ix - 120)) if left is None else left
    cy = max(0, min(mh - 128, iy - 64 - 12)) if top is None else top
    scr = Image.new("RGBA", (240, 160), (6, 6, 12, 255))
    scr.paste(q.convert("RGBA"), (-cx, -cy))
    d = ImageDraw.Draw(scr, "RGBA")
    ents = [(sh, x, y, f) for (sh, x, y, f) in npcs] + [(pl, player[0], player[1], player[2])]
    ents.sort(key=lambda e: e[2] + e[1])
    for sh, x, y, f in ents:
        px, py = (int(round(v)) for v in proj(x, y))
        d.ellipse((px - cx - 9, py - cy - 3, px - cx + 9, py - cy + 3), fill=(0, 0, 0, 80))
        scr.alpha_composite(frame(sh, f), (px - cx - 16, py - cy - 54))
    d = ImageDraw.Draw(scr)
    if cue:
        px, py = proj(*cue[:2])
        um.a_cue(d, int(px - cx), int(py - cy - cue[2]))
    scr = scr.convert("RGB")
    scr.paste(hud, (0, 128))
    if menu:
        um.draw_menu(scr, um.Style("A"), menu[0], menu[1], 0, x=menu[2], info=menu[3])
    return scr


for v, kx, ky in (("a", 12.3, 14.9), ("b", 12.8, 15.5)):
    q = Image.open(f"/tmp/claude-0/s62/out/vm{v}_q.png").convert("RGB")
    # arrival at the door, Valet watching from the kiosks
    shot(q, (8.0, 16.2, "n"), [(valet, kx, ky, "sw")]).save(f"{out}/mock_{v}_door.png")
    # at the kiosk bank with the robot talking
    shot(q, (kx - 1.0, ky + 0.5, "ne"), [(valet, kx + 1.6, ky + 0.2, "sw")], left=None,
         menu=("Valet", None, 4, ["Have a nice day.", "Next customer."])).save(f"{out}/mock_{v}_kiosk.png")
print("ok")
