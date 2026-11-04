import numpy as np, math
from pt import *
from hairlib import paint_hair
from chars import LINE, SK_LINE
from bodies import *


def back(cv, ch, E):
    pass


def body(cv, ch, E, face):
    neck_paint(cv, ch, face, w=15.5, shade=0.32)
    # broad shoulders, white shirt
    pts = [(0, 128), (0, 118), (6, 108), (24, 102), (44, 101), (54, 103), (64, 106), (74, 103), (84, 101), (104, 102), (122, 108), (128, 118), (128, 128)]
    sh, t = shoulders(cv, ch, pts, None, folds=(((20, 128), (28, 112)), ((108, 128), (100, 112)), ((8, 124), (14, 112))), gain=1.2)
    cv.toon(sh, t + 0.25, ch["collar"], [0.30, 0.55, 0.8])
    cv.outline(sh, hexc("3a3430"), 1.0)
    # red apron bib with straps
    bib = mask_poly([(32, 128), (38, 114), (48, 108), (80, 108), (90, 114), (96, 128)])
    cv.toon(bib, 0.55 + 0.14 * (cv.xx < 60) - 0.1 * (cv.yy > 120) + 0.1 * cv.lam(bib, 6), ch["cloth"], [0.28, 0.48, 0.72])
    cv.outline(bib, hexc("3a0c0a"), 0.9)
    for sg in (-1, 1):
        strap = mask_stroke([(64 + sg * 15, 104), (64 + sg * 19, 108.5), (64 + sg * 20, 114)], 5.4)
        cv.toon(strap, 0.6 + 0.15 * (sg < 0), ch["cloth"], [0.35, 0.7])
        cv.outline(strap, hexc("3a0c0a"), 0.8)
    # neck opening of the shirt: round collar
    sc = mask_ell(64, 103.5, 15, 6.4) * (cv.yy > 100)
    cv.toon(sc, 0.5 + 0.1 * (cv.xx < 64) - 0.25 * blur(face, 2 * S), ch["skin"], [0.30, 0.46, 0.66, 0.86])
    col = dilate(sc, 1.6 * S) * (1 - sc) * (cv.yy > 99.5) * (np.abs(cv.xx - 64) < 18)
    cv.toon(col, 0.75 + 0 * cv.xx, ch["collar"], [0.35, 0.62])
    cv.outline(col, hexc("5a5048"), 0.8)
    # pocket with a pencil
    pk = mask_poly([(40, 120), (51, 120), (51, 128), (40, 128)])
    cv.paint(pk, ch["cloth"][0]); cv.outline(pk, hexc("2a0806"), 0.6)
    cv.paint(mask_stroke([(47, 118), (48, 124)], 1.3), hexc("f0c850"))


def skin_extra(cv, ch, E, t_ref):
    pass


def nose_extra(cv, ch, E):
    for sg in (-1, 1):   # smile lines
        cv.paint(mask_stroke(cr_spline([(64 + sg * 10.5, 71), (64 + sg * 13.5, 77), (64 + sg * 13, 84)], n=6), 0.55, 0.3), SK_LINE * 0.9)


def after_eyes(cv, ch, E):
    # big dark moustache over the lip
    m = mask_poly(cr_spline([(64, 73.2), (56, 72.8), (49, 75), (45, 80.5), (49, 82.8), (56, 79.2), (64, 78.0), (72, 79.2), (79, 82.8), (83, 80.5), (79, 75), (72, 72.8)], closed=True, n=6))
    paint_hair(cv, m, ch["hair"], (64, 70), strands=34, seed=8, sigma=2.5, hl=None, swirl=0.0, length=(4, 10), wid=(0.7, 1.2),
               flow=lambda x, y: math.atan2(1.0, (x - 64) * 0.13), outline=0.9, line=hexc("120a06"))


def front(cv, ch, E, face):
    # a bit of dark hair at the temples under the hat
    for sg in (-1, 1):
        m = mask_poly(cr_spline([(64 + sg * 29, 36), (64 + sg * 33.5, 42), (64 + sg * 35, 56), (64 + sg * 31.5, 52), (64 + sg * 30, 44)], closed=True, n=5))
        paint_hair(cv, m, ch["hair"], (64, 30), strands=10, seed=14 + sg, sigma=2, hl=None, swirl=0.0, length=(3, 6), outline=0.8)
    # tall puffy chef hat: band + billowing top
    band = mask_poly(cr_spline([(30, 36), (29, 24), (32, 16), (96, 16), (99, 24), (98, 36), (80, 33), (64, 32), (46, 33)], closed=True, n=5))
    puff = mask_ell(64, 9, 31, 11) + mask_ell(40, 12, 13, 9) + mask_ell(88, 12, 13, 9) + mask_ell(64, 4, 15, 6.5)
    puff = np.clip(puff, 0, 1)
    allh = np.clip(puff + band, 0, 1)
    t = cv.lam(allh, 7, gain=1.0) + 0.1
    cv.toon(allh, t, ch["hat"], [0.30, 0.50, 0.72])
    cv.outline(allh, hexc("5a6070"), 1.0)
    folds = np.zeros((W, W), np.float32)
    for (a, b) in (((44, 24), (42, 8)), ((56, 24), (54, 5)), ((72, 24), (74, 5)), ((84, 24), (86, 8))):
        folds += mask_stroke(cr_spline([a, ((a[0] + b[0]) / 2 + 1.2, (a[1] + b[1]) / 2), b], n=5), 0.8, 0.3)
    cv.paint(np.clip(blur(folds, 0.4 * S) * 2.4, 0, 1) * puff * (1 - mask_poly([(30, 14), (99, 14), (99, 40), (30, 40)])) * 0 + np.clip(blur(folds, 0.4 * S) * 2.4, 0, 1) * allh * 0.6, ch["hat"][0])
    seam = mask_stroke(cr_spline([(30, 27.5), (64, 29.5), (98, 27.5)], n=6), 0.7)
    cv.paint(seam * 0.7, ch["hat"][0])
