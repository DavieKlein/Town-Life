#!/usr/bin/env python3
"""In-game style mocks (240x160, real HUD strip from a headless screenshot, real player sprite sheet, UI mock-up menus).
  python3 mock52.py FINALDIR OUTDIR"""
import os, sys
from PIL import Image, ImageDraw
REPO = "/home/user/Town-Life"
S52 = "/tmp/claude-0/s52"
sys.path.insert(0, "/tmp/claude-0/s55/tools/proposals/ui_objects")
sys.path.insert(0, f"{REPO}/tools/proposals/ui_objects")
import ui_mock as um   # noqa

fin, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
hud = Image.open(f"{S52}/out/hud3.png").convert("RGB").crop((0, 128, 240, 160))
pl = Image.open(f"{S52}/out/player_rgba.png")


def player_frame(facing, idle=True, i=0):
    n = facing * 9 + (0 if idle else 1 + i)
    return pl.crop((0, n * 64, 32, n * 64 + 64))


FACE = dict(s=0, sw=1, w=2, nw=3, n=4, ne=5, e=6, se=7)
BG = (6, 6, 12)


def proj(sc, x, y, w, h):
    ox, oy = h * 16 + 24, sc["oy"]
    return ox + 16 * (x - y), oy + 8 * (x + y)


def shot(q, oy, W, H, px, py, face="se", cam=None, overlays=(), cue=None, menu=None, left=None, menu_x=None):
    sc = dict(oy=oy)
    ix, iy = (int(round(v)) for v in proj(sc, px, py, W, H))
    mw, mh = q.size
    if left is not None:
        cam = (max(0, min(mw - 240, ix - left)), max(0, min(mh - 128, iy - 64 - 12)))
    if cam is None:
        cx = max(0, min(mw - 240, ix - 120))
        cy = max(0, min(mh - 128, iy - 64 - 12))
    else:
        cx, cy = cam
    scr = Image.new("RGBA", (240, 160), BG + (255,))
    scr.paste(q.convert("RGBA"), (-cx, -cy))
    d = ImageDraw.Draw(scr, "RGBA")
    d.ellipse((ix - cx - 9, iy - cy - 3, ix - cx + 9, iy - cy + 3), fill=(0, 0, 0, 90))
    scr.alpha_composite(player_frame(FACE[face]), (ix - cx - 16, iy - cy - 54))
    d = ImageDraw.Draw(scr)
    if cue:
        cxp, cyp = (int(round(v)) for v in proj(sc, *cue[:2], W, H))
        um.a_cue(d, cxp - cx, cyp - cy - cue[2])
    scr = scr.convert("RGB")
    scr.paste(hud, (0, 128))
    if menu:
        st = um.Style("A")
        title, opts, sel, info = menu
        um.draw_menu(scr, st, title, opts, sel, x=menu_x, info=info)
    return scr, (cx, cy)


def load(name):
    return Image.open(f"{fin}/{name}_q.png").convert("RGB")


def mask_bg(q):
    """The previews have black where nothing is drawn; keep as the map backdrop."""
    return q


if __name__ == "__main__":
    q = Image.open(f"{fin}/room_b2_q.png").convert("RGB")
    mk = lambda *a, **k: shot(*a, **k)[0]
    mk(q, 84, 8, 7, 5.2, 2.9, "n").save(f"{out}/mock_b2_arrive.png")
    mk(q, 84, 8, 7, 5.3, 2.3, "n", left=108, menu_x=4, cue=(5.9, 0.9, 40),
       menu=("Bed", ["Sleep", "Take a nap", "Leave"], 0, None)).save(f"{out}/mock_b2_bed.png")
    mk(q, 84, 8, 7, 2.5, 1.3, "n", left=62, cue=(2.5, 0.5, 52),
       menu=("Window", None, 0, ["Mia is opening the", "shutters down below.", "A new day."])).save(f"{out}/mock_b2_window.png")
    print("ok")
