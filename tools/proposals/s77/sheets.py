"""Contact sheets + the ladder / manhole transition mock frames.  python3 sheets.py OUTDIR  (after shots.py has rendered everything)"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compose as c  # noqa: E402
import sewer as sw  # noqa: E402

out = sys.argv[1]
lib = c.lib
A = c.actor
FONT = c.FONT
MX, MY = sw.EXIT_OB


def tint(im, rgb, a):
    return Image.blend(im, Image.new("RGB", im.size, rgb), a)


def mock_menu(scr):
    """Approximation of the Paper-style pop-up menu (panel top-right, red title band, gold highlight bar). MOCK ONLY."""
    d = ImageDraw.Draw(scr)
    f9 = ImageFont.truetype(FONT, 9)
    x, y, w, h = 146, 5, 90, 58
    d.rounded_rectangle((x, y, x + w, y + h), 5, fill=(239, 227, 194), outline=(60, 40, 30))
    d.rounded_rectangle((x, y, x + w, y + 16), 5, fill=(176, 58, 46), outline=(60, 40, 30))
    d.text((x + 8, y + 3), "Manhole", font=f9, fill=(255, 240, 210))
    d.rounded_rectangle((x + 5, y + 20, x + w - 5, y + 33), 4, fill=(232, 184, 64))
    d.text((x + 10, y + 22), "Climb down", font=f9, fill=(40, 28, 20))
    d.text((x + 10, y + 36), "Leave", font=f9, fill=(40, 28, 20))
    d.text((x + 10, y + 46), "A Choose  B Back", font=ImageFont.truetype(FONT, 7), fill=(90, 70, 50))
    return scr


def hole_overlay(scr, sx, sy, cover_dx=14):
    """The two small sprites the engine would add: a dark hole disc over the baked closed cover and the iron cover slid aside."""
    sc = scr.convert("RGBA")
    d = ImageDraw.Draw(sc, "RGBA")
    d.ellipse((sx - 12, sy - 6, sx + 12, sy + 6), fill=(52, 51, 47, 255))
    d.ellipse((sx - 9, sy - 4, sx + 9, sy + 4), fill=(8, 10, 10, 255))
    d.ellipse((sx + cover_dx - 11, sy - 4, sx + cover_dx + 11, sy + 8), fill=(75, 74, 70, 255), outline=(40, 40, 36, 255))
    d.line((sx + cover_dx - 7, sy + 2, sx + cover_dx + 7, sy + 2), fill=(52, 51, 47, 255))
    return sc.convert("RGB")


frames = []

# ---- 1-3: City Centre variant A ---------------------------------------------------------------------------------------
q, left, top = c.base(f"{out}/cc_a", "cc_a", 64.9, 28.4)
mx, my = 66.9, 27.95
ix, iy = c.proj("cc_a", mx, my)
hx, hy = int(round(ix)) - left, int(round(iy)) - top
s1 = c.screen("cc_a", q, left, top, [A("player", 64.9, 28.4, "e")], cue_at=(mx, my - 0.1))
frames.append((mock_menu(s1), "1  A at the manhole: pop-up menu"))
base = c.screen("cc_a", q, left, top, [])
base = hole_overlay(base, hx, hy)
px_, py_ = c.proj("cc_a", 65.5, 28.0)
fr = c.sheet_frame("player_pickup", "e", 4, 2, w=64, h=64).convert("RGBA")
b2 = base.convert("RGBA")
ImageDraw.Draw(b2, "RGBA").ellipse((int(round(px_)) - left - 9, int(round(py_)) - top - 3, int(round(px_)) - left + 9, int(round(py_)) - top + 3), fill=(0, 0, 0, 90))
b2.alpha_composite(fr, (int(round(px_)) - left - 32, int(round(py_)) - top - 54))
frames.append((b2.convert("RGB"), "2  crouch (existing pickup frames), hole + cover = 2 small sprites"))
frames.append((tint(b2.convert("RGB"), (0, 0, 0), 0.62), "3  fade to black (existing fade)"))

# ---- 4-6: sewer west ladder ---------------------------------------------------------------------------------------------
q2, l2, t2 = c.base(None, "sewer", 2.4, 0.6, outdir=out)


def sew(z, facing, idx, y=0.0):
    ix, iy = c.proj("sewer", sw.WEST_SHAFT, y, z)          # the camera follows the climbing player
    return c.screen("sewer", q2, l2, max(0, min(int(round(iy)) - 76, q2.size[1] - 128)), [A("player", sw.WEST_SHAFT, y, facing, idx=idx, z=z)])


frames.append((tint(sew(0.0, "n", 6, y=-0.2), (0, 0, 0), 0.45), "4  arrive at the ladder foot, fade in"))
frames.append((tint(sew(1.7, "n", 9, y=-1.0), (255, 255, 255), 0.30), "5  climb up the rungs (4-frame climb sheet or the n-walk frames)"))
frames.append((tint(sew(3.6, "n", 12, y=-1.0), (255, 255, 255), 0.75), "6  near the top: white fade (the shaft of light)"))

# ---- 7-8: Old Block ---------------------------------------------------------------------------------------------------------
q3, l3, t3 = c.base(f"{out}/ob_open", "ob_open", MX + 1.5, MY + 0.9)
s7 = c.screen("ob_open", q3, l3, t3, [A("player", MX, MY, "sw", idx=0, z=0.0)], clip={0: 34})
frames.append((tint(s7, (255, 255, 255), 0.55), "7  white fade out, head and shoulders come out of the hole"))
s8 = c.screen("ob_open", q3, l3, t3, [A("player", MX + 1.5, MY + 0.9, "sw"), A("teo", MX + 2.9, MY - 1.3, "sw")])
frames.append((s8, "8  standing beside the open manhole, Teo waits"))

lib.labelled(frames, n=2, cols=2, title="s77 transition mock: manhole -> sewer ladder -> Old Block manhole (menu panel = approximation)").save(f"{out}/sheet4_transition.png")


# ---- contact sheets -------------------------------------------------------------------------------------------------------------
def load(n):
    return Image.open(f"{out}/{n}_1x.png")


lib.labelled([(load("cc_a"), "A  crooked road manhole, east end of the avenue"),
              (load("cc_b"), "B  Water Board hatch on the river walk (lid open)")], n=2, cols=2,
             title="s77 entrance variants (City Centre, real renderer + quantizer + player sprite)").save(f"{out}/sheet1_entrances.png")

full = Image.open(f"{out}/sewer_full_1x_raw.png")
sheet = Image.new("RGB", (1400, 540), (28, 30, 38))
d = ImageDraw.Draw(sheet)
d.text((6, 4), "s77 sewer map 30 x 9 cells: 1x (left) and 3x crop around nook, bridge and east ladder (right)", font=ImageFont.truetype(FONT, 13), fill=(255, 220, 120))
sheet.paste(full.crop((0, 40, 640, 540)), (6, 28))
sheet.paste(lib.zoom(full.crop((380, 270, 620, 450)), 3), (660, 28))
sheet.save(f"{out}/sheet2_sewer_map.png")

names = [("west", "west ladder foot (entrance end), cue"), ("bridge", "iron bridge over the channel"), ("collapse", "collapsed wall + broken pipe: detour"),
         ("nook", "Mothball's nook (empty, CLOSED sign)"), ("east", "east ladder (exit to Old Block)"), ("front", "front walkway: daylight stripes, rat")]
lib.labelled([(load("sewer_" + n), t) for n, t in names], n=2, cols=3,
             title="s77 sewer in game screens (240x128 viewport + HUD, real player sprite)").save(f"{out}/sheet3_sewer_screens.png")

lib.labelled([(load("ob_open"), "Old Block exit, cover slid aside (Teo waits)"), (load("ob_closed"), "same spot, cover closed (A cue)")], n=2, cols=2,
             title="s77 exit manhole on Cobble Street, just inside the arch").save(f"{out}/sheet5_exit.png")
print("sheets done")
