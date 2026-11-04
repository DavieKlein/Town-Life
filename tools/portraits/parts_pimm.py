import numpy as np, math
from pt import *
from hairlib import paint_hair
from chars import LINE, SK_LINE
from bodies import *


def back(cv, ch, E):
    # tufts of white hair behind the ears
    for sg in (-1, 1):
        pts = [(64 + sg * 28, 44), (64 + sg * 36, 50), (64 + sg * 37, 66), (64 + sg * 32, 76), (64 + sg * 29, 66)]
        m = mask_poly(cr_spline(pts, closed=True, n=6))
        paint_hair(cv, m, ch["hair"], (64 + sg * 24, 40), strands=24, seed=3 + sg, sigma=3, hl=None, swirl=0.0, length=(4, 9), wid=(0.6, 1.0),
                   flow=lambda x, y: math.atan2(1.0, 0.2), line=hexc("40384c"))


def body(cv, ch, E, face):
    neck_paint(cv, ch, face, w=10.5, shade=0.30)
    pts = [(0, 128), (2, 121), (10, 113), (26, 107), (44, 104), (54, 105.5), (64, 108), (74, 105.5), (84, 104), (102, 107), (118, 113), (126, 121), (128, 128)]
    sh, t = shoulders(cv, ch, pts, None, folds=(((24, 128), (30, 116)), ((104, 128), (98, 118)), ((14, 124), (20, 116))))
    cv.toon(sh, t, ch["cloth"], [0.30, 0.46, 0.66])
    cv.outline(sh, hexc("2c2210"), 1.0)
    # knitted red scarf, wrapped twice, one end hanging
    for (cy, th, k) in ((103, 7.6, 0), (108.5, 6.6, 1)):
        sc = mask_ell(64, cy, 19, th)
        t2 = 0.5 + 0.2 * cv.lam(sc, 4, gain=0.8) + 0.08 * (cv.xx < 64) - (0.3 * blur(face, 2 * S) if k == 0 else 0)
        rib = (np.sin((cv.xx + cv.yy * 0.4) * 1.6) > 0.5).astype(np.float32) * 0.07
        cv.toon(sc, t2 + rib, ch["collar"], [0.32, 0.55, 0.8])
        cv.outline(sc, hexc("3a0c0c"), 0.9)
    tail = mask_poly([(70, 108), (82, 110), (84, 128), (72, 128)])
    cv.toon(tail, 0.55 + 0.12 * cv.lam(tail, 3) - 0.1 * (cv.yy > 120), ch["collar"], [0.32, 0.55, 0.8])
    cv.outline(tail, hexc("3a0c0c"), 0.9)
    for k in range(3):
        cv.paint(mask_stroke([(73, 112 + k * 5), (81.5, 113 + k * 5)], 0.8), ch["collar"][0])


def skin_extra(cv, ch, E, t_ref):
    pass


def nose_extra(cv, ch, E):
    L = SK_LINE
    for sg in (-1, 1):
        cv.paint(mask_stroke(cr_spline([(64 + sg * 9.5, 71), (64 + sg * 12, 77), (64 + sg * 11.6, 84)], n=6), 0.6, 0.3), L * 0.9)
        for dy in (-1.4, 0.4, 2.2):
            cv.paint(mask_stroke([(64 + sg * 22, 55 + dy), (64 + sg * 25.5, 54 + dy * 1.8)], 0.5, 0.25), L * 0.9)
        cv.paint(mask_stroke(cr_spline([(64 + sg * 13, 62.5), (64 + sg * 15, 63.6), (64 + sg * 17.5, 62.8)], n=4), 0.5, 0.3), L * 0.8)
    for dy in (0, 3):
        cv.paint(mask_stroke(cr_spline([(51, 38 + dy), (64, 37 + dy), (77, 38 + dy)], n=6), 0.5, 0.3, w_mid=0.55) * 0.8, L)
    # white stubble moustache
    m = mask_poly(cr_spline([(64, 74), (57, 74.2), (52, 77), (51, 80.5), (57, 78.4), (64, 77.6), (71, 78.4), (77, 80.5), (76, 77), (71, 74.2)], closed=True, n=6))
    paint_hair(cv, m, ch["hair"], (64, 70), strands=26, seed=6, sigma=2, hl=None, swirl=0.0, length=(3, 7), wid=(0.5, 0.9),
               flow=lambda x, y: math.atan2(1.0, (x - 64) * 0.12), outline=0.7, line=hexc("40384c"))


def after_eyes(cv, ch, E):
    pass


def front(cv, ch, E, face):
    # flat cap: low dome, pulled to one side, short brim at the front
    pts = [(31, 41), (31, 32), (37, 22), (48, 14), (62, 10), (76, 11), (88, 16), (95, 25), (97, 35), (97, 42)]
    dome = mask_poly(cr_spline(pts, n=6) + [(97, 44), (80, 40.5), (64, 39.5), (48, 40.5), (31, 44)])
    t = cv.lam(dome, 9, gain=1.0) + 0.05
    tweed = (np.sin(cv.xx * 2.2 + cv.yy * 1.1) * np.sin(cv.xx * 1.1 - cv.yy * 2.2) > 0.1).astype(np.float32) * 0.06
    cv.toon(dome, t + tweed, ch["cap"], [0.28, 0.46, 0.68])
    cv.outline(dome, hexc("2a1c0e"), 1.0)
    # panel seams
    cv.paint(mask_stroke(cr_spline([(64, 11), (63, 24), (66, 39)], n=6), 0.6), ch["cap"][0])
    cv.paint(mask_stroke(cr_spline([(40, 26), (50, 28), (60, 38)], n=6), 0.5, 0.3), ch["cap"][0])
    # brim
    brim = mask_poly(cr_spline([(35, 41), (50, 41.5), (64, 42), (78, 41.5), (93, 41), (97, 44.5), (86, 47), (64, 48.4), (42, 47), (31, 44.5)], closed=True, n=6))
    cv.toon(brim, 0.5 + 0.2 * (cv.yy < 44) - 0.1 * (cv.xx > 80), ch["cap"], [0.28, 0.5, 0.8])
    cv.outline(brim, hexc("2a1c0e"), 0.9)
