import numpy as np
from pt import *
from hairlib import paint_hair
from chars import LINE, SK_LINE
from bodies import *


def back(cv, ch, E):
    pass


def body(cv, ch, E, face):
    neck = neck_paint(cv, ch, face, w=10.5, shade=0.30)
    # white lab coat
    pts = [(0, 128), (2, 120), (10, 112), (26, 106), (44, 103), (54, 105), (64, 108), (74, 105), (84, 103), (102, 106), (118, 112), (126, 120), (128, 128)]
    sh, t = shoulders(cv, ch, pts, None, folds=(((24, 128), (30, 116)), ((104, 128), (98, 118)), ((14, 124), (20, 114))))
    cv.toon(sh, t, ch["cloth"], [0.30, 0.46, 0.66])
    cv.outline(sh, hexc("3a4a52"), 1.0)
    # teal scrubs: deep V between the coat lapels
    v = mask_poly(cr_spline([(46, 103), (64, 111), (82, 103), (88, 128), (40, 128)], n=6) + [(88, 128), (40, 128)])
    tt = 0.55 + 0.12 * (cv.xx < 60) - 0.3 * blur(face, 2 * S) - 0.1 * (cv.yy > 118)
    cv.toon(v, tt, ch["collar"], [0.35, 0.62])
    cv.outline(v, hexc("0a3a3a"), 0.9)
    # V neckline of the scrubs: skin
    sc = mask_poly([(54, 101), (74, 101), (64, 114)]) * (cv.yy > 100)
    cv.toon(sc, 0.5 + 0.1 * (cv.xx < 64) - 0.25 * blur(face, 2 * S), ch["skin"], [0.30, 0.46, 0.66, 0.86])
    cv.outline(sc, hexc("0a3a3a"), 0.8)
    # coat lapels
    for sg in (-1, 1):
        cv.paint(mask_stroke(cr_spline([(64 + sg * 12, 104), (64 + sg * 20, 114), (64 + sg * 24, 128)], n=6), 1.1, 0.5), ch["cloth"][3] * 0.9)
        cv.paint(mask_stroke(cr_spline([(64 + sg * 12, 104), (64 + sg * 20, 114), (64 + sg * 24, 128)], n=6), 0.5, 0.2), hexc("3a4a52"))
    # chest pocket with a pen
    cv.paint(mask_poly([(92, 116), (104, 116), (104, 128), (92, 128)]), ch["cloth"][1])
    cv.paint(mask_stroke([(98, 112), (98, 122)], 0.9), hexc("2a58c8"))
    # stethoscope: dark tube round the neck down to the chest piece
    TUBE = hexc("2a2a34")
    cv.paint(mask_stroke(cr_spline([(48, 98), (46, 108), (52, 118), (60, 124)], n=8), 1.5), TUBE)
    cv.paint(mask_stroke(cr_spline([(80, 98), (82, 108), (76, 118), (68, 124)], n=8), 1.5), TUBE)
    cv.paint(mask_ell(64, 125.5, 4.2, 3.6), hexc("c8d0d8"))
    cv.paint(mask_ell(64, 125.5, 2.4, 2.0), hexc("8a96a4"))
    cv.paint(mask_stroke([(50, 99.5), (78, 99.5)], 0.0), TUBE)


def skin_extra(cv, ch, E, t_ref):
    pass


def nose_extra(cv, ch, E):
    pass


def after_eyes(cv, ch, E):
    # slim dark glasses: rectangular frames with a lens glint
    FR = hexc("2a2630")
    for sg in (-1, 1):
        cx, cy = 64 + sg * 13.6, 56.3
        ring = mask_poly([(cx - 10, cy - 7), (cx + 10, cy - 7), (cx + 10, cy + 7), (cx - 10, cy + 7)]) * (1 - mask_poly([(cx - 8.6, cy - 5.6), (cx + 8.6, cy - 5.6), (cx + 8.6, cy + 5.6), (cx - 8.6, cy + 5.6)]))
        cv.paint(ring, FR)
        cv.paint(mask_stroke([(cx - 6, cy - 3.5), (cx - 2.5, cy - 4.8)], 0.8, 0.4), hexc("ffffff") * 0.85)
        cv.paint(mask_stroke([(cx + sg * 10, cy - 2.2), (64 + sg * 29.5, 53.5)], 0.9), FR)
    cv.paint(mask_stroke(cr_spline([(64 - 3.2, 54.8), (64, 53.6), (64 + 3.2, 54.8)], n=6), 1.0), FR)


def front(cv, ch, E, face):
    # short, close-cropped natural hair: a cap hugging the head
    rnd = random.Random(4)
    pts = []
    for k in range(120):
        a = 2 * math.pi * k / 120
        r = 1 + 0.045 * math.sin(13 * a) + 0.025 * math.sin(6 * a + 1)
        pts.append((64 + 35 * r * math.cos(a), 35 + 24 * r * math.sin(a)))
    cap = mask_poly(pts)
    hole = mask_poly(cr_spline([(64, 36), (74, 36.5), (85, 39), (91, 47), (90, 60), (90, 68), (64, 68), (38, 68), (38, 60), (37, 47), (43, 39), (54, 36.5)], closed=True, n=6))
    cut = mask_poly([(0, 0), (128, 0), (128, 64), (100, 64), (98, 60), (30, 60), (28, 64), (0, 64)])
    hair = np.maximum(np.clip(cap - hole, 0, 1) * cut, 0)
    hl = mask_ell(68, 12, 16, 4.0, rot=-0.1) + mask_ell(36, 40, 3, 9)
    paint_hair(cv, hair, ch["hair"], (64, 34), strands=100, seed=8, sigma=5, hl=np.clip(hl, 0, 1), hl_amt=0.25, swirl=1.4, length=(4, 10), spread=3.2, curl=2.4, wid=(0.8, 1.5))
