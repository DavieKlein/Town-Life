import numpy as np
from pt import *
from hairlib import paint_hair
from chars import LINE, SK_LINE


def back(cv, ch, E):
    pass


def body(cv, ch, E, face):
    sk = ch["skin"]
    # neck
    neck = mask_poly(cr_spline([(52, 80), (51.5, 96), (50, 106), (50, 112), (78, 112), (77, 106), (76.5, 96), (76, 80)], closed=True, n=4))
    t = cv.lam(neck, 8, gain=0.8) - 0.05
    t = t - 0.34 * blur(face * 1.0, 1.6 * S) * (cv.yy > 80) * 1.0
    t = t - 0.2 * blur(mask_poly([(64, 96), (90, 96), (90, 112), (64, 112)]) * neck, 3 * S)
    cv.toon(neck, t, sk, [0.30, 0.46, 0.66, 0.86])
    cv.outline(neck, SK_LINE * 0.55 + LINE * 0.3, 0.9)
    # sweater: shoulders and torso
    half = [(64, 103), (74, 103.5), (88, 101), (104, 104), (116, 110), (124, 120), (128, 128)]
    loop = mirror(half) + [(0, 128)] if False else None
    pts = [(0, 128), (2, 120), (10, 110), (24, 104), (42, 101), (52, 103), (64, 106), (76, 103), (86, 101), (104, 104), (118, 110), (126, 120), (128, 128)]
    sh = mask_poly(cr_spline(pts, n=6) + [(128, 128), (0, 128)])
    t = cv.lam(sh, 16, gain=1.3, light=(-0.6, -0.5, 0.6))
    # folds
    fold = np.zeros((W, W), np.float32)
    for (a, b) in (((24, 128), (30, 116)), ((16, 124), (22, 114)), ((104, 128), (96, 118)), ((112, 126), (106, 116)), ((78, 128), (80, 120)), ((52, 128), (50, 121))):
        fold += mask_stroke(cr_spline([a, ((a[0] + b[0]) / 2 + 1.5, (a[1] + b[1]) / 2), b], n=6), 1.3, 0.4)
    t = t - 0.16 * blur(fold, 0.5 * S)
    t = t - 0.22 * blur(mask_poly([(64, 100), (96, 100), (128, 128), (64, 128)]), 8 * S) * 0.5
    # shadow of the chin/head on the sweater
    t = t - 0.25 * blur(mask_ell(64, 104, 22, 5), 2.5 * S)
    # sweater knit: faint vertical ribs on the front panel
    rib = (np.sin(cv.xx * 3.2) > 0.2).astype(np.float32) * 0.045
    cv.toon(sh, t + rib, ch["cloth"], [0.30, 0.46, 0.66])
    cv.outline(sh, hexc("101830"), 1.0)
    # crew-neck collar (cream rib knit): a ring around the neck base
    ring = mask_ell(64, 103, 14.5, 6.2) * (1 - mask_ell(64, 102.2, 11.2, 4.4))
    ring = ring * (cv.yy > 99.5)
    cl = ch["collar"]
    tt = 0.55 + 0.25 * (cv.xx < 64) - 0.3 * (cv.yy > 106)
    cv.toon(ring, tt + 0.0, cl, [0.30, 0.62])
    cv.outline(ring, hexc("5a4630"), 0.9)
    # inside the collar the dark neck hole shows the neck skin
    inner = mask_ell(64, 102.2, 11.2, 4.4) * (cv.yy > 100)
    cv.toon(inner, 0.35 + 0 * cv.xx, sk, [0.30, 0.46, 0.66, 0.86])


def skin_extra(cv, ch, E, t_ref):
    pass


def nose_extra(cv, ch, E):
    pass


def after_eyes(cv, ch, E):
    pass


def front(cv, ch, E, face):
    pts = [(34, 61), (32, 46), (33, 33), (38, 22), (48, 13), (60, 8), (72, 6.5), (83, 9.5), (91, 16), (95, 27), (96.5, 42), (94.5, 59),
           (91.5, 52), (90, 43), (87, 36), (82, 28), (76, 32), (72, 39), (68, 32), (63, 37), (59, 30), (55, 37), (51, 29), (47, 37), (43, 33), (40, 43), (37, 49), (37, 56)]
    hair = mask_poly(cr_spline(pts, closed=True, n=6))
    hl = mask_ell(70, 15, 15, 4.5, rot=-0.15)
    paint_hair(cv, hair, ch["hair"], (78, 4), strands=70, seed=5, sigma=6.5, hl=hl, hl_amt=0.28, swirl=0.9, length=(8, 24), spread=1.4)
