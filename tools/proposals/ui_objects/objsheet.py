#!/usr/bin/env python3
"""Builds the object proposal sheets (owner feedback D, E, F) from preview renders (see rend.sh / preview.py:
Blender quick-look renders of floor + objects, graded like the game, 5-bit colour) and in-game screenshots.
Needs a scratch copy of tools/ with the proposal scenes (public_toilet_v2, ref_sheet, ...)."""
import json, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/user/Town-Life/tools/proposals/ui_objects")
import ui_mock as ui

W = "/tmp/claude-0/s47/work/"
OUT = "/tmp/claude-0/s47/"
sys.path.insert(0, W + "tools")
import scene as scn


def scene(name, which="after"):
    return next(f() for f in scn.SCENES if f().ident == name)


def crop(img, s, x, y, z, w=84, h=72, dy=0):
    cx, cy = s.proj(x, y, z)
    cx, cy = int(round(cx)), int(round(cy)) + dy
    c = Image.new("RGB", (w, h), (10, 12, 24))
    c.paste(img, (w // 2 - cx, h // 2 - cy))
    return c


def tag(im, text):
    return (im, text)


def sheet(rows, scale=3, pad=4, colw=None):
    """rows: list of lists of (image, label); the label is drawn on a bar under the scaled picture."""
    w, h = rows[0][0][0].size
    bar = 16
    cols = max(len(r) for r in rows)
    o = Image.new("RGB", (cols * (w * scale + pad) + pad, len(rows) * (h * scale + bar + pad) + pad), (30, 30, 36))
    d = ImageDraw.Draw(o)
    d.fontmode = "1"
    for j, r in enumerate(rows):
        for i, (im, t) in enumerate(r):
            x, y = pad + i * (w * scale + pad), pad + j * (h * scale + bar + pad)
            o.paste(im.resize((w * scale, h * scale), Image.NEAREST), (x, y))
            d.rectangle((x, y + h * scale, x + w * scale - 1, y + h * scale + bar - 1), fill=(14, 14, 20))
            d.text((x + 3, y + h * scale + 12), t, font=ui.F8, fill=(255, 235, 120))
    return o


def caption(o, lines, colour=(255, 235, 120)):
    import textwrap
    lines = [w for ln in lines for w in textwrap.wrap(ln, max(30, o.width // 7))]
    h = 14 * len(lines) + 8
    n = Image.new("RGB", (o.width, o.height + h), (30, 30, 36))
    n.paste(o, (0, 0))
    d = ImageDraw.Draw(n)
    d.fontmode = "1"
    for i, ln in enumerate(lines):
        d.text((6, o.height + 14 + i * 14 - 2), ln, font=ui.F9, fill=colour)
    return n


def main():
    pt_b, pt_a = Image.open(W + "pt_before_c.png"), Image.open(W + "pt_after_c.png")
    sb = scn.public_toilet() if False else None
    # scenes: before = repo public_toilet, after = public_toilet_v2
    import scene_orig as so
    s_b = so.public_toilet()
    s_a = scn.public_toilet_v2()
    # ---- objects_fix: before / after
    cc_b, cc_a = Image.open(W + "cc_before_c.png"), Image.open(W + "cc_after_c.png")
    scc = so.community_centre()
    rows = [
        [tag(crop(pt_b, s_b, 1.2, 1.2, 0.6), "NOW: WC hidden by panel"),
         tag(crop(pt_a, s_a, 2.9, 0.8, 0.6), "PROPOSED: white WC, open")],
        [tag(crop(pt_b, s_b, 0.6, 3.4, 0.9), "NOW: tiny grey sink"),
         tag(crop(pt_a, s_a, 0.4, 3.5, 1.0), "PROPOSED: basin, tap, mirror")],
        [tag(crop(pt_b, s_b, 0.95, 4.65, 0.4), "NOW: dark bin, dark tile"),
         tag(crop(pt_a, s_a, 0.75, 1.0, 0.4), "PROPOSED: flared, white band")],
        [tag(crop(cc_b, scc, 6.7, 4.4, 0.5, dy=0), "NOW: dark chairs, blue rug"),
         tag(crop(cc_a, scc, 6.7, 4.4, 0.5, dy=0), "PROPOSED: light oak chairs")],
    ]
    o = sheet(rows, 3)
    o = caption(o, ["Preview renders (Blender, same grade as the game, before the 15-colour tile quantizer).",
                    "Streets: the street bins get the same flared bin with a white band (see reference sheet).",
                    "Everything else in the checked list reads clearly and stays as it is."])
    o.save(OUT + "objects_fix.png"); print("objects_fix", o.size)
    # ---- toilet_fill: whole room before / after
    a = pt_b.resize((pt_b.width * 3, pt_b.height * 3), Image.NEAREST)
    b = pt_a.resize((pt_a.width * 3, pt_a.height * 3), Image.NEAREST)
    o = Image.new("RGB", (a.width * 2 + 12, a.height + 4), (30, 30, 36))
    o.paste(a, (4, 0)); o.paste(b, (a.width + 8, 0))
    d = ImageDraw.Draw(o); d.fontmode = "1"
    for (x, t) in ((8, "NOW"), (a.width + 12, "PROPOSED")):
        d.rectangle((x - 3, 3, x + 90, 18), fill=(0, 0, 0)); d.text((x, 14), t, font=ui.F9, fill=(255, 235, 120))
    o = caption(o, ["Right side filled: mop + bucket + broom, hygiene poster, 'wet floor' sign, second bin, hand dryer,",
                    "toilet-roll shelf, 'please keep clean' notice. WC moved to the open back wall (no panel in front).",
                    "Game changes if approved: toilet 1.2,1.5 -> 2.9,1.5; sink 1.0,3.4 -> 0.5,3.5; new bin interactable 4.55,3.4."])
    o.save(OUT + "toilet_fill.png"); print("toilet_fill", o.size)
    # ---- reference objects
    ref = Image.open(W + "ref_c.png")
    home = Image.open(W + "home_c.png")
    sr = scn.ref_sheet()
    sh = scn.home_room()
    rows = [
        [tag(crop(home, sh, 8.0, 0.8, 0.6), "TOILET now (home room)"),
         tag(crop(ref, sr, 1.2, 0.8, 0.6), "TOILET proposed")],
        [tag(crop(home, sh, 5.8, 1.1, 0.9), "SHOWER now (thin frame)"),
         tag(crop(ref, sr, 7.15, 0.85, 1.0), "SHOWER proposed")],
        [tag(crop(home, sh, 0.9, 6.5, 0.2), "BED now (mattress)"),
         tag(crop(ref, sr, 10.4, 1.5, 0.3), "BED proposed")],
        [tag(crop(ref, sr, 16.6, 1.2, 0.5), "STREET BIN now"),
         tag(crop(ref, sr, 19.4, 1.2, 0.5), "BIN proposed")],
        [tag(Image.new("RGB", (84, 72), (40, 40, 50)), "DUMPSTER (none yet)"),
         tag(crop(ref, sr, 13.9, 1.0, 0.7, w=84, h=72), "DUMPSTER proposed (Old Block)")],
    ]
    o = sheet(rows, 3)
    o = caption(o, ["'Now' = what exists in the repo (home_room is built but has no entrance yet). 'Proposed' = own designs,",
                    "bigger/exaggerated, strong silhouettes: white porcelain, chrome, bright blue curtain, green steel with a",
                    "yellow stripe. Rendered with the real Blender pipeline; the game adds the 15-colour tile quantizer."])
    o.save(OUT + "reference_objects.png"); print("reference_objects", o.size)
    # ---- objects_check: all interactables in game, verdicts
    names = json.load(open("/tmp/claude-0/s47/chk/verdicts.json"))
    items = []
    for i, (verdict, note) in enumerate(names):
        c, nm = chk_crop(i)
        d = ImageDraw.Draw(c)
        col = {"clear": (60, 200, 80), "ok": (240, 200, 60), "unclear": (240, 70, 60)}[verdict]
        c = c.resize((240, 180), Image.NEAREST)
        t = Image.new("RGB", (240, 226), (30, 30, 36))
        t.paste(c, (0, 0))
        d = ImageDraw.Draw(t); d.fontmode = "1"
        d.rectangle((0, 180, 239, 225), fill=(20, 20, 26))
        d.text((4, 194), nm, font=ui.F9, fill=(255, 255, 255))
        d.text((4, 208), verdict.upper() + ": " + note, font=ui.F9, fill=col)
        items.append(t)
    cols = 3
    rows_n = (len(items) + cols - 1) // cols
    o = Image.new("RGB", (cols * 244 + 4, rows_n * 230 + 4), (30, 30, 36))
    for k, t in enumerate(items):
        o.paste(t, (4 + (k % cols) * 244, 4 + (k // cols) * 230))
    o.save(OUT + "objects_check.png"); print("objects_check", o.size)


def chk_crop(i):
    j = json.load(open(f"/tmp/claude-0/s47/chk/{i:02d}.json"))
    im = Image.open(f"/tmp/claude-0/s47/chk/{i:02d}.png").convert("RGB").crop((0, 0, 240, 128))
    sx, sy = int(j["sx"]), int(j["sy"])
    c = Image.new("RGB", (120, 90), (0, 0, 0))
    c.paste(im, (60 - sx, 45 - sy))
    d = ImageDraw.Draw(c)
    for (ax, ay) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, py = 60 + ax * 17, 45 + ay * 17
        d.line([(px, py), (px - ax * 5, py)], fill=(255, 230, 0))
        d.line([(px, py), (px, py - ay * 5)], fill=(255, 230, 0))
    return c, j["name"]


if __name__ == "__main__":
    main()
