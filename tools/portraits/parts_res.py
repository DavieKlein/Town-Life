"""s75: dialogue-portrait parts for the new residents (one module, dispatch on ch["kind"]); same interface as tools/portraits/parts_*.py."""
import math
import random
import numpy as np
from pt import *
from hairlib import paint_hair
from chars import LINE, SK_LINE
from bodies import *

UNI_PTS = [(0, 128), (0, 118), (6, 108), (24, 102), (44, 101), (54, 103), (64, 106), (74, 103), (84, 101), (104, 102), (122, 108), (128, 118), (128, 128)]
SMALL_PTS = [(0, 128), (6, 122), (16, 114), (32, 108), (48, 106), (56, 107), (64, 109), (72, 107), (80, 106), (96, 108), (112, 114), (122, 122), (128, 128)]
FOLDS = (((20, 128), (28, 112)), ((108, 128), (100, 112)), ((8, 124), (14, 112)))


def _shirt(cv, ch, face, pts, key="cloth", edge="2a2a30", gain=1.2):
    sh, t = shoulders(cv, ch, pts, None, folds=FOLDS, gain=gain)
    cv.toon(sh, t, ch[key], [0.30, 0.46, 0.66])
    cv.outline(sh, hexc(edge), 1.0)
    return sh


def _collar_open(cv, ch, face, rx=14, ry=6.4, col="collar"):
    sc = mask_ell(64, 103.5, rx, ry) * (cv.yy > 100)
    cv.toon(sc, 0.5 + 0.1 * (cv.xx < 64) - 0.25 * blur(face, 2 * S), ch["skin"], [0.30, 0.46, 0.66, 0.86])
    rim = dilate(sc, 1.8 * S) * (1 - sc) * (cv.yy > 99.5) * (np.abs(cv.xx - 64) < rx + 4)
    cv.toon(rim, 0.7 + 0 * cv.xx, ch[col], [0.35, 0.62])
    cv.outline(rim, hexc("2a2a30"), 0.8)


def _cap(cv, ch, face, top, low, brim_y, brim_w, key="cap", edge="1a1a22", band=None, badge=None):
    """peaked / round cap. top = y of the crown, low = y of the lower edge on the forehead, brim_y = peak centre y."""
    pts = [(30, low), (29, low - 10), (35, top + 14), (47, top + 4), (62, top), (78, top + 4), (92, top + 14), (99, low - 10), (98, low)]
    dome = mask_poly(cr_spline(pts, n=6) + [(98, low + 1), (64, low + 1.5), (30, low + 1)])
    cv.toon(dome, cv.lam(dome, 9, gain=1.0) + 0.08, ch[key], [0.28, 0.46, 0.68])
    cv.outline(dome, hexc(edge), 1.0)
    if band:
        b = mask_poly([(29.5, low - 7), (98.5, low - 7), (98, low + 1), (30, low + 1)])
        cv.toon(b, 0.5 + 0.2 * (cv.yy < low - 3), ch[band], [0.3, 0.6])
        cv.outline(b, hexc(edge), 0.8)
    brim = mask_poly(cr_spline([(32, low), (50, low + 0.5), (64, low + 1), (78, low + 0.5), (96, low), (101, brim_y - 1), (88, brim_y + 2.5), (64, brim_y + 3.8), (40, brim_y + 2.5), (27, brim_y - 1)], closed=True, n=6))
    cv.toon(brim, 0.45 + 0.15 * (cv.yy < low + 2), ch[key], [0.3, 0.55, 0.8])
    cv.outline(brim, hexc(edge), 0.9)
    if badge:
        cv.paint(mask_ell(64, low - 8, 5.2, 4.2), ch[badge][2]); cv.outline(mask_ell(64, low - 8, 5.2, 4.2), ch[badge][0], 0.8)
        cv.paint(mask_ell(64, low - 8, 2.4, 1.9), ch[badge][3])


def _hair_sides(cv, ch, face, y0=44, y1=68, seed=3, thick=7):
    for sg in (-1, 1):
        m = mask_poly(cr_spline([(64 + sg * 29, y0), (64 + sg * (29 + thick), y0 + 5), (64 + sg * (28 + thick), y1), (64 + sg * 29, y1 - 4)], closed=True, n=6)) * (1 - face)
        paint_hair(cv, m, ch["hair"], (64, 40), strands=22, seed=seed + sg, sigma=3, hl=None, swirl=0.0, length=(4, 9), wid=(0.6, 1.0),
                   flow=lambda x, y: math.atan2(1.0, 0.1))


def back(cv, ch, E):
    k = ch["kind"]
    if k == "valdez":
        m = mask_ell(64, 24, 28, 22)
        paint_hair(cv, m, ch["hair"], (64, 20), strands=60, seed=4, sigma=5, hl=mask_ell(56, 12, 10, 3), hl_amt=0.2, swirl=1.2, length=(5, 12), spread=2.4, curl=1.5)
        for sg in (-1, 1):
            m2 = mask_poly(cr_spline([(64 + sg * 28, 40), (64 + sg * 36, 50), (64 + sg * 35, 74), (64 + sg * 28, 70)], closed=True, n=6))
            paint_hair(cv, m2, ch["hair"], (64, 40), strands=24, seed=7 + sg, sigma=3, length=(4, 9), flow=lambda x, y: math.atan2(1.0, 0.1))


def body(cv, ch, E, face):
    k = ch["kind"]
    if k == "ines":
        neck_paint(cv, ch, face, w=15, shade=0.32)
        _shirt(cv, ch, face, UNI_PTS, edge="5a3008")
        bib = mask_poly([(34, 128), (42, 114), (50, 106), (78, 106), (86, 114), (94, 128)])
        cv.toon(bib, 0.55 + 0.12 * (cv.xx < 60) - 0.08 * (cv.yy > 120), ch["collar"], [0.3, 0.55, 0.8])
        cv.outline(bib, hexc("14284a"), 0.9)
        for sg in (-1, 1):
            st = mask_stroke([(64 + sg * 14, 104), (64 + sg * 20, 108.5), (64 + sg * 22, 114)], 5.0)
            cv.toon(st, 0.6 + 0.15 * (sg < 0), ch["collar"], [0.35, 0.7]); cv.outline(st, hexc("14284a"), 0.8)
        _collar_open(cv, ch, face, 15, 6.4, "cloth")
        cv.paint(mask_poly([(48, 120), (62, 120), (62, 128), (48, 128)]), ch["collar"][1]); cv.outline(mask_poly([(48, 120), (62, 120), (62, 128), (48, 128)]), hexc("14284a"), 0.6)
    elif k == "teo":
        neck_paint(cv, ch, face, w=9.5, shade=0.30)
        _shirt(cv, ch, face, SMALL_PTS, edge="0e3a22")
        _collar_open(cv, ch, face, 11, 5.0, "cloth")
        # skateboard strap over the shoulder
        cv.paint(mask_stroke([(86, 106), (66, 128)], 4.2), hexc("3a2a1e")); cv.paint(mask_stroke([(86, 106), (66, 128)], 1.2) * 0.8, hexc("c9a064"))
    elif k == "grigor":
        neck_paint(cv, ch, face, w=15.5, shade=0.32)
        _shirt(cv, ch, face, UNI_PTS, edge="0a121e", gain=1.3)
        cv.paint(mask_stroke(cr_spline([(40, 128), (64, 118), (88, 128)], n=6), 5.0) * 0.5, ch["cloth"][0])       # knit rib at the neck
        _collar_open(cv, ch, face, 16, 6.8, "cloth")
        for i in range(6):                                                                       # cable-knit lines
            cv.paint(mask_stroke([(34 + i * 12, 112 + (i % 2) * 2), (34 + i * 12, 128)], 0.5, 0.3), ch["cloth"][3] * 0.8)
        cv.paint(mask_ell(94, 122, 3.2, 3.2), hexc("e2b53a")); cv.outline(mask_ell(94, 122, 3.2, 3.2), hexc("7a5a10"), 0.6)   # gold anchor pin
    elif k in ("pruitt", "kessler"):
        neck_paint(cv, ch, face, w=14.5 if k == "pruitt" else 11.5, shade=0.32)
        _shirt(cv, ch, face, UNI_PTS if k == "pruitt" else SMALL_PTS[:0] + UNI_PTS, edge="2a3040")
        v = mask_poly(cr_spline([(48, 102), (64, 112), (80, 102), (84, 128), (44, 128)], n=6) + [(84, 128), (44, 128)])
        cv.toon(v, 0.62 + 0.1 * (cv.xx < 60) - 0.3 * blur(face, 2 * S), ch["collar"], [0.35, 0.62]); cv.outline(v, hexc("5a6070"), 0.8)
        tie = mask_poly([(61, 108), (67, 108), (69, 128), (59, 128)])
        cv.toon(tie, 0.6 + 0 * cv.xx, ch["gold"], [0.4, 0.7]); cv.outline(tie, hexc("5a4208"), 0.7)
        for sg in (-1, 1):                                                                       # epaulettes
            ep = mask_poly([(64 + sg * 38, 106), (64 + sg * 52, 111), (64 + sg * 49, 116), (64 + sg * 36, 111)])
            cv.toon(ep, 0.55 + 0 * cv.xx, ch["gold"], [0.4, 0.7]); cv.outline(ep, hexc("5a4208"), 0.7)
        r = 5.6 if k == "kessler" else 4.8                                                      # the oversized badge
        bx, by = 90, 118
        cv.paint(mask_ell(bx, by, r, r), ch["gold"][2]); cv.outline(mask_ell(bx, by, r, r), ch["gold"][0], 0.9)
        cv.paint(mask_ell(bx - 1, by - 1, r * 0.5, r * 0.5), ch["gold"][3])
        if k == "pruitt":                                                                         # crossword clipboard in a corner
            cb = mask_poly([(6, 128), (10, 112), (36, 114), (34, 128)])
            cv.paint(cb, hexc("f4f2e8")); cv.outline(cb, hexc("4a4a52"), 0.8)
            for i in range(4):
                for j in range(3):
                    cv.paint(mask_poly([(13 + j * 7, 116 + i * 3.2), (18 + j * 7, 116 + i * 3.2), (18 + j * 7, 118.6 + i * 3.2), (13 + j * 7, 118.6 + i * 3.2)]) * ((i + j) % 2), hexc("3a3a44"))
    elif k == "nella":
        neck_paint(cv, ch, face, w=12.5, shade=0.30)
        _shirt(cv, ch, face, UNI_PTS, edge="2a4a3a")
        _collar_open(cv, ch, face, 13, 6.0, "cloth")
        bib = mask_poly([(40, 128), (46, 112), (52, 104), (76, 104), (82, 112), (88, 128)])        # floury baker's apron bib with volume
        cv.toon(bib, 0.62 + 0.14 * (cv.xx < 60) - 0.12 * (cv.yy > 120) - 0.1 * blur(face, 2 * S), ch["collar"], [0.3, 0.55, 0.8])
        cv.outline(bib, hexc("6a5a3a"), 0.9)
        for sg in (-1, 1):
            st = mask_stroke([(64 + sg * 11, 103), (64 + sg * 19, 108), (64 + sg * 24, 114)], 4.0)
            cv.toon(st, 0.55 + 0.15 * (sg < 0), ch["collar"], [0.35, 0.7]); cv.outline(st, hexc("6a5a3a"), 0.8)
        cv.paint(mask_ell(58, 120, 4.5, 3.0) * 0.8, hexc("fffdf6")); cv.paint(mask_ell(70, 114, 3, 2) * 0.7, hexc("fffdf6"))   # flour smudges
    elif k == "valdez":
        neck_paint(cv, ch, face, w=11.5, shade=0.30)
        _shirt(cv, ch, face, SMALL_PTS[:0] + UNI_PTS, edge="4a1e2a")
        # purple shawl wrapped over the shoulders, V in front
        sh = mask_poly(cr_spline([(0, 128), (2, 118), (12, 108), (30, 102), (50, 101), (64, 112), (78, 101), (98, 102), (116, 108), (126, 118), (128, 128)], n=6) + [(128, 128), (0, 128)])
        cv.toon(sh, cv.lam(sh, 14, gain=1.0) + 0.18 - 0.2 * blur(face, 2 * S), ch["shawl"], [0.3, 0.5, 0.75])
        cv.outline(sh, hexc("240a3a"), 1.0)
        for i in range(5):                                                                        # fringe / weave lines
            cv.paint(mask_stroke(cr_spline([(8 + i * 24, 124), (14 + i * 24, 114), (22 + i * 24, 104)], n=6), 0.5, 0.3), ch["shawl"][3] * 0.7)
        cv.paint(mask_stroke(cr_spline([(50, 104), (64, 122), (78, 104)], n=6), 1.0), ch["shawl"][0])
        for i in range(8):                                                                        # shell necklace
            a = math.pi * (0.1 + 0.8 * i / 7)
            cv.paint(mask_ell(64 + 11 * math.cos(a), 100 + 8 * math.sin(a), 1.5, 1.4), hexc("fff4d8"))


def skin_extra(cv, ch, E, t_ref):
    pass


def nose_extra(cv, ch, E):
    k = ch["kind"]
    L = SK_LINE
    if k in ("ines", "grigor", "pruitt", "valdez"):
        for sg in (-1, 1):
            cv.paint(mask_stroke(cr_spline([(64 + sg * 10.5, 71), (64 + sg * 13.5, 77), (64 + sg * 13, 84)], n=6), 0.55, 0.3), L * 0.9)
    if k in ("grigor", "valdez"):
        for sg in (-1, 1):
            for dy in (-1.2, 0.6, 2.2):
                cv.paint(mask_stroke([(64 + sg * 22, 55 + dy), (64 + sg * 25.5, 54 + dy * 1.8)], 0.5, 0.25), L * 0.9)
    if k == "grigor":
        m = mask_poly(cr_spline([(64, 74), (56, 74.2), (50, 77), (49, 81.5), (56, 79), (64, 78), (72, 79), (79, 81.5), (78, 77), (72, 74.2)], closed=True, n=6))
        paint_hair(cv, m, ch["hair"], (64, 70), strands=30, seed=6, sigma=2, length=(3, 7), wid=(0.5, 0.9), outline=0.7, flow=lambda x, y: math.atan2(1.0, (x - 64) * 0.12), line=hexc("5a5a70"))
    if k == "kessler":
        m = mask_poly(cr_spline([(64, 74.4), (58, 74.6), (54, 76.4), (58, 77), (64, 76.2), (70, 77), (74, 76.4), (70, 74.6)], closed=True, n=6))
        paint_hair(cv, m, ch["hair"], (64, 70), strands=10, seed=6, sigma=2, length=(2, 5), wid=(0.4, 0.7), outline=0.6)
    if k == "pruitt":                                                                           # stubble dots
        rnd = random.Random(5)
        for _ in range(70):
            x, y = rnd.uniform(40, 88), rnd.uniform(78, 98)
            if ((x - 64) / 26) ** 2 + ((y - 74) / 24) ** 2 < 1.0 and y > 76:
                cv.paint(mask_ell(x, y, 0.5, 0.5) * 0.7, ch["hair"][1])
    if k == "teo":
        for sg in (-1, 1):
            for dx in (-3, 0, 3):
                cv.paint(mask_ell(64 + sg * 17 + dx, 66 + abs(dx) * 0.3, 0.55, 0.45) * 0.55, hexc("8a4a30"))     # freckles


def after_eyes(cv, ch, E):
    pass


def front(cv, ch, E, face):
    k = ch["kind"]
    if k == "ines":
        _hair_sides(cv, ch, face, 46, 64, 2, 4)
        # head scarf: wide dome with a yellow band, knot and curlers
        pts = [(26, 44), (24, 30), (34, 16), (50, 8), (64, 6), (78, 8), (94, 16), (104, 30), (102, 44)]
        dome = mask_poly(cr_spline(pts, n=6) + [(100, 46), (64, 40.5), (28, 46)])
        cv.toon(dome, cv.lam(dome, 10, gain=1.0) + 0.08, ch["scarf"], [0.28, 0.46, 0.68])
        cv.outline(dome, hexc("48082a"), 1.0)
        for (x, y) in ((40, 22), (58, 14), (78, 18), (90, 30), (46, 32), (68, 28), (32, 36), (84, 40)):           # polka dots
            cv.paint(mask_ell(x, y, 1.9, 1.5) * dome, hexc("ffe9a0"))
        band = mask_poly(cr_spline([(25, 43), (64, 38), (103, 43)], n=6) + [(103, 48), (64, 43.5), (25, 48)])
        cv.toon(band, 0.55 + 0.2 * (cv.yy < 44), ch["band"], [0.3, 0.6]); cv.outline(band, hexc("7a5a10"), 0.8)
        for i, c in enumerate((hexc("f08ab8"), hexc("8ad0e8"), hexc("f08ab8"), hexc("f4e070"))):               # curlers on the forehead
            cx = 38 + i * 17.5
            cv.paint(mask_ell(cx, 36.5, 6, 3.6), c); cv.outline(mask_ell(cx, 36.5, 6, 3.6), hexc("48082a"), 0.7)
            cv.paint(mask_stroke([(cx - 3.5, 35.4), (cx + 3.5, 35.4)], 0.4), hexc("ffffff") * 0.8)
        knot = mask_ell(64, 6, 9, 5)
        cv.toon(knot, 0.55 + 0.2 * (cv.xx < 64), ch["scarf"], [0.3, 0.6]); cv.outline(knot, hexc("48082a"), 0.9)
    elif k == "teo":
        _hair_sides(cv, ch, face, 44, 62, 5, 4)
        _cap(cv, ch, face, 8, 41, 45, 0, key="cap", edge="4a1c08", badge=None)
        cv.paint(mask_ell(64, 9, 3, 2.2), ch["cap"][0])
        cv.paint(mask_stroke(cr_spline([(64, 10), (63, 24), (66, 38)], n=6), 0.6), ch["cap"][0])
    elif k == "grigor":
        _hair_sides(cv, ch, face, 44, 62, 6, 4)
        # beard: outside the jaw line + chin, mouth stays visible
        ring = dilate(face, 5 * S) * (1 - (face > 0.5)) * (cv.yy > 62)
        chin = mask_ell(64, 97, 15, 6.5) * (cv.yy > 92)
        beard = np.clip(ring + chin * (1 - 0.0), 0, 1)
        paint_hair(cv, beard, ch["hair"], (64, 70), strands=70, seed=9, sigma=4, hl=None, swirl=0.0, length=(5, 11), wid=(0.7, 1.2), flow=lambda x, y: math.atan2(1.0, (x - 64) * 0.05), line=hexc("5a5a70"))
        _cap(cv, ch, face, 6, 36, 40, 0, key="cap", edge="14161c", band="band", badge="gold")
    elif k == "pruitt":
        _hair_sides(cv, ch, face, 50, 64, 3, 4)
        _cap(cv, ch, face, 8, 44, 49, 0, key="cap", edge="14161c", band="band", badge="gold")           # oversized: pulled low
        cv.paint(mask_stroke(cr_spline([(46, 52), (56, 52.8), (66, 52)], n=4), 0.6) * 0.0, LINE)
    elif k == "kessler":
        _hair_sides(cv, ch, face, 46, 62, 3, 3)
        _cap(cv, ch, face, 6, 36, 40, 0, key="cap", edge="14161c", band="band", badge="gold")
    elif k == "nella":
        _hair_sides(cv, ch, face, 44, 66, 8, 5)
        m = mask_poly(cr_spline([(30, 46), (28, 30), (38, 16), (54, 8), (64, 6), (74, 8), (90, 16), (100, 30), (98, 46), (88, 36), (64, 32), (40, 36)], closed=True, n=6)) * (1 - face)
        paint_hair(cv, m, ch["hair"], (64, 24), strands=60, seed=5, sigma=5, hl=mask_ell(52, 14, 12, 3), hl_amt=0.25, swirl=1.2, length=(5, 12), spread=2.2)
        band = mask_poly(cr_spline([(27, 40), (64, 33), (101, 40)], n=6) + [(101, 47), (64, 40.5), (27, 47)])          # terracotta bandana
        cv.toon(band, 0.55 + 0.2 * (cv.yy < 40), ch["band"], [0.3, 0.6]); cv.outline(band, hexc("4a1408"), 0.9)
        for x in (38, 54, 74, 90):
            cv.paint(mask_ell(x, 40 + (x % 7) * 0.2, 1.3, 1.1) * band, ch["band"][3])
        knot = mask_ell(96, 36, 6, 4.5)
        cv.toon(knot, 0.55 + 0.2 * (cv.xx < 96), ch["band"], [0.3, 0.6]); cv.outline(knot, hexc("4a1408"), 0.9)
    elif k == "valdez":
        m = mask_ell(64, 22, 27, 14) * (cv.yy < 36)
        hl = mask_ell(50, 14, 12, 3)
        paint_hair(cv, m, ch["hair"], (64, 24), strands=70, seed=2, sigma=5, hl=hl, hl_amt=0.25, swirl=1.2, length=(5, 12), spread=2.0, curl=1.2)
        fr = mask_poly(cr_spline([(34, 46), (34, 30), (46, 20), (64, 17), (82, 20), (94, 30), (94, 46), (86, 36), (64, 30), (42, 36)], closed=True, n=6)) * (1 - face * 0.0)
        paint_hair(cv, fr * (1 - face), ch["hair"], (64, 26), strands=60, seed=4, sigma=5, hl=mask_ell(70, 22, 14, 3), hl_amt=0.25, swirl=1.3, length=(5, 12), spread=2.2, curl=1.0)
        bun = mask_ell(64, 9, 17, 11)                                                                            # tall updo (s76)
        paint_hair(cv, bun, ch["hair"], (64, 10), strands=50, seed=11, sigma=4, hl=mask_ell(56, 5, 7, 2.5), hl_amt=0.3, swirl=1.6, length=(4, 9), spread=1.6, outline=1.0)
        cv.paint(mask_stroke(cr_spline([(46, 14), (58, 8), (74, 8), (84, 14)], n=6), 1.2, 0.8) * bun, hexc("cfc8d6"))   # silver streak across the updo
        cv.paint(mask_ell(80, 12, 3.2, 3.2) * bun, hexc("f2c94c")); cv.outline(mask_ell(80, 12, 3.2, 3.2), hexc("8a6a10"), 0.6)   # gold hair comb
        for sg in (-1, 1):                                                                                      # giant hoop earrings
            cx, cy = 64 + sg * 30.5, 76
            ring = mask_ell(cx, cy, 6.8, 8.2) * (1 - mask_ell(cx, cy, 5.0, 6.4))
            cv.paint(ring, hexc("f2c94c")); cv.outline(ring, hexc("8a6a10"), 0.6)
            cv.paint(mask_stroke(cr_spline([(cx - 4, cy - 3), (cx - 3.6, cy + 3)], n=4), 0.7), hexc("fff6c0"))
