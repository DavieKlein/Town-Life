import numpy as np, math
from pt import *
from hairlib import paint_hair
from chars import LINE, SK_LINE
from bodies import *


def back(cv, ch, E):
    pass


def body(cv, ch, E, face):
    neck = neck_paint(cv, ch, face, w=11.5, shade=0.30)
    pts = [(0, 128), (2, 120), (10, 111), (26, 105), (44, 102), (54, 104), (64, 107), (74, 104), (84, 102), (102, 105), (118, 111), (126, 120), (128, 128)]
    sh, t = shoulders(cv, ch, pts, None, folds=(((24, 128), (30, 114)), ((104, 128), (98, 116)), ((14, 124), (20, 114))))
    cv.toon(sh, t, ch["cloth"], [0.30, 0.46, 0.66])
    cv.outline(sh, hexc("2a0a14"), 1.0)
    # white blouse: wide V filling the cardigan opening
    v = mask_poly(cr_spline([(46, 103), (64, 108), (82, 103), (86, 128), (42, 128)], n=6) + [(86, 128), (42, 128)])
    tt = 0.55 + 0.12 * (cv.xx < 60) - 0.3 * blur(face, 2 * S) - 0.1 * (cv.yy > 118)
    cv.toon(v, tt, ch["collar"], [0.35, 0.62])
    cv.outline(v, hexc("2a0a14"), 0.9)
    # cardigan edges (two buttons band)
    for sg in (-1, 1):
        cv.paint(mask_stroke([(64 + sg * 22, 104), (64 + sg * 21, 116), (64 + sg * 22, 128)], 1.0), ch["cloth"][3])
    # round collar of the blouse and neck skin
    sc = mask_ell(64, 103.5, 14, 6.6) * (cv.yy > 100)
    cv.toon(sc, 0.5 + 0.1 * (cv.xx < 64) - 0.25 * blur(face, 2 * S), ch["skin"], [0.30, 0.46, 0.66, 0.86])
    col = dilate(sc, 1.6 * S) * (1 - sc) * (cv.yy > 99.5)
    cv.toon(col, 0.8 + 0 * cv.xx, ch["collar"], [0.35, 0.62])
    cv.outline(col, hexc("5a4a50"), 0.8)
    # pearls
    for i in range(9):
        a = math.pi * (0.12 + 0.76 * i / 8)
        px, py = 64 + 12.5 * math.cos(a), 101 + 8.6 * math.sin(a)
        cv.paint(mask_ell(px, py, 1.15, 1.15), hexc("fffaf6")); cv.paint(mask_ell(px + 0.2, py + 0.3, 0.55, 0.45), hexc("d4cae0"))


def skin_extra(cv, ch, E, t_ref):
    pass


def nose_extra(cv, ch, E):
    # age lines
    L = SK_LINE
    for sg in (-1, 1):
        cv.paint(mask_stroke(cr_spline([(64 + sg * 9, 71), (64 + sg * 11.5, 77), (64 + sg * 11.5, 83)], n=6), 0.55, 0.3), L * 0.9)       # smile line
        for k, dy in enumerate((-1.2, 0.6, 2.2)):
            cv.paint(mask_stroke([(64 + sg * 22, 55 + dy), (64 + sg * 25.5, 54 + dy * 1.8)], 0.5, 0.25), L * 0.9)   # crow's feet
        cv.paint(mask_stroke(cr_spline([(64 + sg * 13, 62.5), (64 + sg * 15, 63.5), (64 + sg * 17, 62.8)], n=4), 0.5, 0.3), L * 0.8)  # eye bags
    for k, dy in enumerate((0, 3)):
        cv.paint(mask_stroke(cr_spline([(53, 33 + dy), (64, 31.8 + dy), (75, 33 + dy)], n=6), 0.5, 0.3, w_mid=0.55) * 0.8, L)         # forehead


def after_eyes(cv, ch, E):
    # round glasses
    FR = hexc("6a2a3c")
    for sg in (-1, 1):
        cx, cy = 64 + sg * 13.6, 56.3
        ring = mask_ell(cx, cy, 10.6, 9.6) * (1 - mask_ell(cx, cy, 9.1, 8.1))
        cv.paint(ring, FR)
        cv.paint(mask_stroke(cr_spline([(cx - 6, cy - 5.5), (cx - 4, cy - 7.2), (cx + 0, cy - 7.8)], n=6), 0.9, 0.4), hexc("ffffff") * 0.9)   # lens glint
        cv.paint(mask_stroke([(cx + 3.5, cy + 6.5), (cx + 6.5, cy + 4.0)], 0.7, 0.4), hexc("ffffff") * 0.7)
        cv.paint(mask_stroke([(cx + sg * 10.5, cy - 2.2), (64 + sg * 29.5, 53.5)], 0.9), FR)   # temple arm
    cv.paint(mask_stroke(cr_spline([(64 - 3.2, 54.8), (64, 53.6), (64 + 3.2, 54.8)], n=6), 1.0), FR)   # bridge


def front(cv, ch, E, face):
    rnd = random.Random(2)
    pts = []
    for k in range(120):
        a = 2 * math.pi * k / 120
        r = 1 + 0.055 * math.sin(11 * a) + 0.03 * math.sin(5 * a + 1)
        pts.append((64 + 39 * r * math.cos(a), 36 + 31 * r * math.sin(a)))
    cap = mask_poly(pts)
    hole = mask_poly(cr_spline([(64, 34), (74, 34.5), (85, 37), (92, 46), (91, 62), (91, 70), (64, 70), (37, 70), (37, 62), (36, 46), (43, 37), (54, 34.5)], closed=True, n=6))
    cut = mask_poly([(0, 0), (128, 0), (128, 66), (100, 66), (98, 62), (30, 62), (28, 66), (0, 66)])
    hair = np.clip(cap - hole, 0, 1) * cut
    hair = np.maximum(hair, 0)
    hl = mask_ell(70, 12, 18, 4.5, rot=-0.1) + mask_ell(34, 40, 3, 10)
    paint_hair(cv, hair, ch["hair"], (64, 34), strands=90, seed=7, sigma=5, hl=np.clip(hl, 0, 1), hl_amt=0.28, swirl=1.4, length=(5, 14), spread=3.0, curl=2.0, wid=(0.8, 1.5))
    # bun on top
    bun = mask_ell(64, 10, 13, 7)
    paint_hair(cv, bun * (1 - face), ch["hair"], (64, 10), strands=30, seed=9, sigma=4, hl=mask_ell(60, 7.5, 5, 2.2), hl_amt=0.3, swirl=1.5, length=(4, 10), spread=2.0, outline=1.0)
