import numpy as np
from pt import *
from hairlib import paint_hair
from chars import LINE, SK_LINE
from bodies import *


def back(cv, ch, E):
    pts = [(34, 92), (29, 76), (28, 54), (30, 34), (38, 18), (52, 9), (64, 7), (76, 9), (90, 18), (98, 34), (100, 54), (99, 76), (94, 92), (86, 95), (80, 88), (48, 88), (42, 95)]
    hair = mask_poly(cr_spline(pts, closed=True, n=6))
    paint_hair(cv, hair, ch["hair"], (64, 30), strands=60, seed=11, sigma=8, hl=mask_ell(40, 40, 3.5, 16), hl_amt=0.3, swirl=1.2, length=(10, 30),
               flow=lambda x, y: math.atan2(1.0, (x - 64) * 0.045), base=-0.1)


def body(cv, ch, E, face):
    neck = neck_paint(cv, ch, face, w=10.5, shade=0.30)
    pts = [(0, 128), (2, 120), (10, 112), (26, 106), (44, 103), (54, 105), (64, 108), (74, 105), (84, 103), (102, 106), (118, 112), (126, 120), (128, 128)]
    sh, t = shoulders(cv, ch, pts, None, folds=(((26, 128), (31, 116)), ((100, 128), (96, 118)), ((78, 128), (80, 118))))
    cv.toon(sh, t, ch["cloth"], [0.30, 0.46, 0.66])
    cv.outline(sh, hexc("0a3030"), 1.0)
    # scoop neckline: skin shows
    sc = mask_ell(64, 103, 15.5, 8.5) * (cv.yy > 100)
    cv.toon(sc, 0.5 + 0.1 * (cv.xx < 64) - 0.25 * blur(face, 2 * S) , ch["skin"], [0.30, 0.46, 0.66, 0.86])
    ring = dilate(sc, 1.0 * S) * (1 - sc) * (cv.yy > 100)
    cv.toon(ring, 0.5 + 0 * cv.xx, ch["cloth"], [0.9])
    cv.paint(dilate(sc, 1.0 * S) * (1 - sc) * (cv.yy > 99) * mask_poly([(40, 99), (90, 99), (90, 128), (40, 128)]) * 0.0, LINE)
    cv.outline(sc * (cv.yy > 100), hexc("0a3030"), 0.8)
    # little gold heart pendant
    cv.paint(mask_stroke(cr_spline([(54, 100.5), (64, 108.5), (74, 100.5)], n=8), 0.6), hexc("f0c850"))
    cv.paint(mask_ell(64, 109.6, 1.5, 1.5), hexc("f0c850"))


def skin_extra(cv, ch, E, t_ref):
    pass


def nose_extra(cv, ch, E):
    rnd = random.Random(3)
    for k in range(13):                       # freckles over the nose bridge and cheeks
        sg = rnd.choice((-1, 1))
        x = 64 + sg * rnd.uniform(1.5, 13)
        y = rnd.uniform(62, 71) + (0 if abs(x - 64) < 6 else 1.5)
        cv.paint(mask_ell(x, y, 0.55, 0.5), ch["skin"][0])


def after_eyes(cv, ch, E):
    pass


def front(cv, ch, E, face):
    # fringe: swept, cut with a few locks
    pts = [(30, 56), (29, 36), (36, 19), (50, 10), (64, 8), (78, 10), (92, 19), (99, 36), (98, 56),
           (97, 40), (91, 37), (86, 38), (82, 44), (79, 36), (72, 39), (68, 45), (64, 37), (58, 43), (54, 37), (48, 44), (44, 38), (38, 46), (36, 56)]
    hair = mask_poly(cr_spline(pts, closed=True, n=6))
    paint_hair(cv, hair, ch["hair"], (66, 6), strands=80, seed=12, sigma=6, hl=mask_ell(70, 16, 15, 4, rot=-0.1), hl_amt=0.3, swirl=1.1, length=(8, 22),
               flow=lambda x, y: math.atan2(max(y - 4, 3) * 0.9, (x - 66) * 0.55))
