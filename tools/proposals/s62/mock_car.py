#!/usr/bin/env python3
"""s62: in-game mocks of Victor Vault's golden car at the Corner Market kerb (240x160 with the real HUD strip).
  python3 mock_car.py CARDIR CITYQ OUTDIR"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageOps
cardir, cityq, out = sys.argv[1:4]
SC = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
os.makedirs(out, exist_ok=True)
G = "/tmp/claude-0/s62/graphics"
OX, OY = 976, 200                       # city_centre origin
CROP = (1100, 560)
city = Image.open(cityq).convert("RGB")
hud = Image.open("/tmp/claude-0/s52/out/hud3.png").convert("RGB").crop((0, 128, 240, 160))
pl = Image.open("/tmp/claude-0/s52/out/player_rgba.png")
FACE = dict(s=0, sw=1, w=2, nw=3, n=4, ne=5, e=6, se=7)


def sheet(name):
    im = Image.open(f"{G}/{name}.bmp")
    pal = im.getpalette()
    rgba = im.convert("RGBA")
    a = np.array(im)
    arr = np.array(rgba)
    arr[a == 0] = (0, 0, 0, 0)
    return Image.fromarray(arr)


victor, valet = sheet("npc_victor"), sheet("npc_robot")
FEET = (16, 54)


def frame(sh, facing):
    n = FACE[facing]
    return sh.crop((0, n * 64, 32, n * 64 + 64))


def proj(x, y):
    return OX + 16 * (x - y), OY + 8 * (x + y)


CAR = {}
for n in ("se", "nw"):
    CAR[n] = Image.open(f"{cardir}/car_{n}_q.png").convert("RGBA")
CAR["sw"] = ImageOps.mirror(CAR["se"])
CAR["ne"] = ImageOps.mirror(CAR["nw"])
CFEET = (96, 74)
LEN, WID = SC * 5.6 / 0.75, SC * 1.9 / 0.75                    # cells


def shadow(scr, cx, cy, heading, sc=1.0):
    """parallelogram footprint, semi-transparent (separate shadow sprite in the game)"""
    L, Wd = LEN * sc / 2 + 0.2, WID * sc / 2 + 0.1
    if heading in ("se", "nw"):
        pts = [(cx - L, cy - Wd), (cx + L, cy - Wd), (cx + L, cy + Wd), (cx - L, cy + Wd)]
    else:
        pts = [(cx - Wd, cy - L), (cx + Wd, cy - L), (cx + Wd, cy + L), (cx - Wd, cy + L)]
    ov = Image.new("RGBA", scr.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon([proj(*p) for p in pts], fill=(0, 0, 0, 95))
    return ov


def sparkle(d, x, y, big=True):
    c = (255, 250, 200, 255)
    d.point((x, y), c)
    for k in (1, 2) if big else (1,):
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            d.point((x + dx, y + dy), c if k == 1 else (255, 220, 90, 255))


def scene(cam, cars=(), people=(), overlay=None, with_hud=True, sparkles=()):
    """cam = (left, top) in city image px; cars = [(x, y, heading)]; people = [(sheet, x, y, facing)] drawn back-to-front by y."""
    scr = Image.new("RGBA", (240, 128), (0, 0, 0, 255))
    scr.paste(city.convert("RGBA"), (-(cam[0] - CROP[0]), -(cam[1] - CROP[1])))
    items = [("p", sh, x, y, f) for (sh, x, y, f) in people] + [("c", None, x, y, h) for (x, y, h) in cars]
    items.sort(key=lambda it: it[3] + (0.02 if it[0] == "c" else 0))   # car drawn after people behind it
    full = Image.new("RGBA", (240, 128), (0, 0, 0, 0))
    for (x, y, h) in cars:
        sx, sy = proj(x, y)
        ov = shadow(scr, x, y, h)
        ov = ov.transform(scr.size, Image.AFFINE, (1, 0, cam[0], 0, 1, cam[1]))
        scr.alpha_composite(ov)
    for kind, sh, x, y, f in items:
        sx, sy = proj(x, y)
        px, py = int(round(sx - cam[0])), int(round(sy - cam[1]))
        if kind == "p":
            scr.alpha_composite(frame(sh, f), (px - FEET[0], py - FEET[1])) if -40 < px < 270 else None
        else:
            fr = CAR[f]
            ox, oy = px - CFEET[0], py - CFEET[1]
            tmp = Image.new("RGBA", (240 + 400, 128 + 200), (0, 0, 0, 0))
            tmp.alpha_composite(fr, (ox + 200, oy + 100)) if (-200 < ox < 440 and -100 < oy < 228) else None
            scr.alpha_composite(tmp.crop((200, 100, 440, 228)))
    # the south-kerb lamp post (window x 72..77, y 48..127) stands IN FRONT of the car: restore it (the game's front layer does this)
    base = city.convert("RGBA").crop((cam[0] - CROP[0] + 72, cam[1] - CROP[1] + 48, cam[0] - CROP[0] + 78, cam[1] - CROP[1] + 128))
    scr.alpha_composite(base, (72, 48))
    d = ImageDraw.Draw(scr)
    for (sx_, sy_, big) in sparkles:
        sparkle(d, sx_, sy_, big)
    if overlay:
        overlay(scr)
    scr = scr.convert("RGB")
    if with_hud:
        full = Image.new("RGB", (240, 160))
        full.paste(scr, (0, 0))
        full.paste(hud, (0, 128))
        return full
    return scr


def spk_for(car_xy, heading, phase):
    sx, sy = proj(*car_xy)
    return sx, sy


CAM = (1224, 666)       # window top-left; centre = (44, 21)
CARY = 23.55
if __name__ == "__main__":
    # 1. parked at the kerb, Victor + Valet on the pavement, player watching
    def spk(cam):
        def f(scr):
            d = ImageDraw.Draw(scr)
            sx, sy = proj(44.3, CARY)
            for (dx, dy, big) in ((-52, -40, 1), (-18, -50, 0), (22, -44, 1), (50, -22, 0), (-66, -14, 0)):
                sparkle(d, int(sx - cam[0]) + dx, int(sy - cam[1]) + dy, big)
        return f
    park = scene(CAM, cars=[(44.3, CARY, "nw")],
                 people=[(victor, 43.1, 19.9, "s"), (valet, 45.3, 20.4, "sw"), (pl, 40.4, 19.2, "e")], overlay=spk(CAM))
    park.save(f"{out}/mock_park.png")
    # 2. drive-in, 4 frames (moving -x, rear visible, decelerating) + leave (moving +x)
    xs = (58.0, 52.5, 47.8, 44.3)
    for i, x in enumerate(xs):
        scene(CAM, cars=[(x, CARY, "nw")], people=[(pl, 40.6, 19.6, "e")], with_hud=True).save(f"{out}/mock_drive{i}.png")
    scene(CAM, cars=[(50.8, CARY, "se")], people=[(victor, 43.2, 18.9, "n"), (pl, 40.6, 19.6, "e")]).save(f"{out}/mock_leave.png")
    # 3. close-up: Victor + Valet at the door (car behind)
    print("ok")
