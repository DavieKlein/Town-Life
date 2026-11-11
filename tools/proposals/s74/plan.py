"""Top-down layout plan of the proposed Old Block map (80 x 64 cells) -> PNG.   python3 plan.py OUT.png"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oldblock as ob   # noqa: E402  (imports the real scene helpers only; no Blender needed)
import data             # noqa: E402

K = 12                       # px per cell
OX, OY = 40, 56
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F9, F14 = (ImageFont.truetype(FONT, n) for n in (9, 15))
COL = {"r": (112, 108, 100), "b": (214, 150, 96), "o": (118, 170, 98), "w": (110, 130, 170)}
OVR = {"hoard": (60, 74, 104), "barrier": (240, 130, 30), "trench": (80, 56, 36), "arch": (150, 96, 70), "thicket": (40, 100, 56),
       "backroom": (200, 190, 160), "court": (180, 96, 70), "garden": (96, 150, 80), "site": (96, 106, 126), "fence": (150, 150, 160),
       "avenue": (96, 98, 106), "street": (132, 124, 112), "h1": (206, 122, 90), "laundry": (224, 170, 90), "bakery": (222, 140, 130),
       "h4": (120, 150, 200), "h5": (110, 170, 160), "alley": (150, 130, 100), "square": (196, 190, 170), "lane": (126, 118, 108), "pond": (70, 130, 150), "cottages": (230, 200, 150), "orchard": (110, 160, 80), "meadow": (136, 180, 110), "yard": (196, 172, 120), "stall": (230, 160, 70), "chess": (170, 160, 140)}


def P(x, y):
    return OX + x * K, OY + y * K


def main(out):
    W, H = ob.W, ob.H
    im = Image.new("RGB", (OX + W * K + 250, OY + H * K + 90), (24, 26, 34))
    d = ImageDraw.Draw(im)
    d.rectangle([P(0, 0), P(W, H)], fill=(66, 64, 60))
    for (id_, label, x0, y0, x1, y1, kind) in ob.LAYOUT:
        d.rectangle([P(x0, y0), P(x1, y1)], fill=OVR.get(id_, COL[kind]), outline=(20, 20, 24))
    for x in range(0, W + 1, 5):
        d.line([P(x, 0), P(x, H)], fill=(86, 84, 80), width=1)
        d.text((P(x, 0)[0] - 6, OY - 14), str(x), font=F9, fill=(200, 200, 200))
    for y in range(0, H + 1, 5):
        d.line([P(0, y), P(W, y)], fill=(86, 84, 80), width=1)
        d.text((OX - 24, P(0, y)[1] - 5), str(y), font=F9, fill=(200, 200, 200))
    for (id_, label, x0, y0, x1, y1, kind) in ob.LAYOUT:
        d.rectangle([P(x0, y0), P(x1, y1)], outline=(10, 10, 14), width=1)
    for (a, b, c, e) in ob.LANE_CELLS:
        d.rectangle([P(a, b), P(c, e)], fill=(236, 214, 120), outline=(120, 90, 20))
    d.rectangle([P(10.2, 14.5), P(10.8, 25.5)], fill=(255, 140, 20))
    lab = {"avenue": (1.0, 21.0), "hoard": (3, 14.0), "street": (30.0, 21.0), "h1": (16.7, 12.0), "laundry": (26.0, 13.5), "alley": (21.3, 6.5),
           "yard": (34.2, 6.5), "bakery": (40.7, 13.5), "square": (47.2, 12.2), "h4": (53.1, 13.5), "h5": (61.1, 13.5),
           "garden": (17.4, 31.5), "chess": (29.7, 27.0), "pond": (38.0, 31.0), "court": (58.0, 31.0), "stall": (59.6, 20.6),
           "backroom": (34.5, 10.0), "thicket": (11.0, 29.0), "lane": (50.2, 45.0), "cottages": (38.5, 55.0), "orchard": (57.0, 52.0),
           "meadow": (24.0, 45.0), "site": (69.5, 24.0)}
    names = {"avenue": "AVENUE STUB\n(cold: cable works)", "hoard": "HOARDING", "street": "COBBLE STREET (warm)", "h1": "VALDEZ\nhouse", "laundry": "INES'\nLAUNDROMAT",
             "alley": "ALLEY\nTeo's den", "yard": "YARD", "bakery": "BELLINI\nBAKERY", "square": "SQUARE", "h4": "HOUSE 4", "h5": "HOUSE 5",
             "garden": "COMMUNITY\nGARDEN", "chess": "CHESS", "pond": "POND PARK", "court": "COURT", "stall": "STALL", "backroom": "BACK\nROOM",
             "thicket": "THICKET", "lane": "BAKER'S\nLANE", "cottages": "COTTAGES\n(spaced out,\nwith yards)", "orchard": "ORCHARD +\nALLOTMENTS",
             "meadow": "MEADOW, trees,\nfootpaths", "site": "DEMOLITION SITE\n+ Co-op Hall"}
    for k, pos in lab.items():
        d.multiline_text(P(*pos), names[k], font=F9, fill=(255, 255, 255), spacing=1)
    d.text((P(14.0, 17.3)[0] - 10, P(14.0, 17.3)[1]), "ARCH", font=F9, fill=(255, 240, 200))
    d.text((P(9.0, 14.0)[0] - 18, P(9.0, 14.0)[1] - 12), "barriers", font=F9, fill=(255, 170, 60))
    d.text((P(11.2, 25.8)[0] - 10, P(11.2, 25.8)[1]), "trench", font=F9, fill=(200, 160, 110))
    for (kind, x, y, r, lbl) in data.INTERACTABLES:
        px, py = P(x, y)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 230, 80), outline=(0, 0, 0))
    for (x0, y0, x1, y1, tgt, lbl) in data.WARPS:
        d.rectangle([P(x0, y0), P(x1, y1)], outline=(255, 80, 200), width=2)
        d.text((P(x0, y0)[0], P(x0, y0)[1] - 11), ">" + tgt, font=F9, fill=(255, 130, 220))
    for (nid, x, y, lbl, when) in data.NPCS:
        px, py = P(x, y)
        d.polygon([(px, py - 6), (px - 5, py + 4), (px + 5, py + 4)], fill=(80, 230, 255), outline=(0, 0, 0))
        d.text((px + 6, py - 6), nid, font=F9, fill=(160, 240, 255))
    for (m, x, y, lbl) in data.HOOKS:
        px, py = P(x, y)
        d.rectangle([px - 12, py - 6, px + 12, py + 6], fill=(40, 40, 70), outline=(255, 255, 255))
        d.text((px - 11, py - 6), m, font=F9, fill=(255, 255, 255))
    lx, ly = OX + W * K + 14, OY
    d.text((lx, ly), "OLD BLOCK  80 x 64 cells", font=F14, fill=(255, 255, 255))
    ly += 24
    d.text((lx, ly), "plan: x -> east, y v south\n(game camera: x goes down-right)", font=F9, fill=(200, 200, 210))
    ly += 36
    items = [("cold / VaultTech zone", (60, 74, 104)), ("barriers + trench", (240, 130, 30)), ("sneak lane (1 cell)", (236, 214, 120)),
             ("bush thicket", (40, 100, 56)), ("houses / shops (warm)", (214, 150, 96)), ("open areas", (118, 170, 98)), ("street", (132, 124, 112))]
    for n, c in items:
        d.rectangle([lx, ly, lx + 14, ly + 10], fill=c, outline=(0, 0, 0))
        d.text((lx + 20, ly - 1), n, font=F9, fill=(230, 230, 230))
        ly += 16
    ly += 6
    d.ellipse([lx, ly, lx + 8, ly + 8], fill=(255, 230, 80))
    d.text((lx + 16, ly - 1), "interactable", font=F9, fill=(230, 230, 230))
    ly += 16
    d.polygon([(lx + 4, ly), (lx - 1, ly + 9), (lx + 9, ly + 9)], fill=(80, 230, 255))
    d.text((lx + 16, ly - 1), "NPC / actor", font=F9, fill=(230, 230, 230))
    ly += 16
    d.rectangle([lx, ly, lx + 14, ly + 10], outline=(255, 80, 200), width=2)
    d.text((lx + 20, ly - 1), "warp", font=F9, fill=(230, 230, 230))
    ly += 16
    d.rectangle([lx, ly, lx + 22, ly + 10], fill=(40, 40, 70), outline=(255, 255, 255))
    d.text((lx + 4, ly - 1), "M09", font=F9, fill=(255, 255, 255))
    d.text((lx + 28, ly - 1), "mission hook", font=F9, fill=(230, 230, 230))
    ly += 24
    d.text((lx, ly), "Camera sees +x / +y faces:\nshopfronts on the NORTH side,\nopen / low things SOUTH.", font=F9, fill=(200, 200, 210))
    d.text((OX, 12), "OLD BLOCK - top-down layout (proposal s74)", font=F14, fill=(255, 255, 255))
    d.text((OX, OY + H * K + 8), "West edge (x=0) = avenue from the City Centre. Barriers x=10.5, trench x 11.3-13.3, arch x 14.5-15.7. "
           "Sneak lane = flap (10.5,30.7) -> east -> north -> exits at the arch (16.5,27).", font=F9, fill=(200, 200, 210))
    im.save(out)
    print("saved", out, im.size)


if __name__ == "__main__":
    main(sys.argv[1])
