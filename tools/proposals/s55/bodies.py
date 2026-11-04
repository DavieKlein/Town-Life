import numpy as np
from pt import *
from chars import LINE, SK_LINE


def neck_paint(cv, ch, face, w=13.0, top=80, shade=0.34):
    sk = ch["skin"]
    cx = 64
    neck = mask_poly(cr_spline([(cx - w, top), (cx - w - 0.4, 96), (cx - w - 2, 106), (cx - w - 2, 112), (cx + w + 2, 112), (cx + w + 2, 106), (cx + w + 0.4, 96), (cx + w, top)], closed=True, n=4))
    t = cv.lam(neck, 8, gain=0.8) - 0.05
    t = t - shade * blur(face * 1.0, 1.6 * S) * (cv.yy > 80)
    t = t - 0.2 * blur(mask_poly([(64, 96), (90, 96), (90, 112), (64, 112)]) * neck, 3 * S)
    cv.toon(neck, t, sk, [0.30, 0.46, 0.66, 0.86])
    cv.outline(neck, SK_LINE * 0.55 + LINE * 0.3, 0.9)
    return neck


def shoulders(cv, ch, pts, outline_col, light=(-0.6, -0.5, 0.6), folds=(), sigma=16, gain=1.3):
    sh = mask_poly(cr_spline(pts, n=6) + [(128, 128), (0, 128)])
    t = cv.lam(sh, sigma, gain=gain, light=light)
    fold = np.zeros((W, W), np.float32)
    for (a, b) in folds:
        fold += mask_stroke(cr_spline([a, ((a[0] + b[0]) / 2 + 1.5, (a[1] + b[1]) / 2), b], n=6), 1.3, 0.4)
    t = t - 0.16 * blur(fold, 0.5 * S)
    t = t - 0.22 * blur(mask_poly([(64, 100), (96, 100), (128, 128), (64, 128)]), 8 * S) * 0.5
    t = t - 0.25 * blur(mask_ell(64, 104, 22, 5), 2.5 * S)
    return sh, t
