import numpy as np, math
from pt import *
from hairlib import paint_hair
from chars import LINE, SK_LINE
from bodies import *

GOLD = [hexc(h) for h in ("a06c14", "e0a828", "ffd458", "fff2a8")]


def back(cv, ch, E):
    pass


def body(cv, ch, E, face):
    neck = neck_paint(cv, ch, face, w=13.5, shade=0.34)
    # black shirt + gold jacket with wide lapels
    pts = [(0, 128), (1, 119), (8, 110), (26, 104), (44, 101), (54, 103), (64, 106), (74, 103), (84, 101), (102, 104), (120, 110), (127, 119), (128, 128)]
    sh, t = shoulders(cv, ch, pts, None, folds=(((22, 128), (28, 114)), ((106, 128), (100, 114)), ((12, 124), (18, 114))), gain=1.2)
    cv.toon(sh, t, ch["cloth"], [0.28, 0.46, 0.68])
    cv.outline(sh, hexc("3a2208"), 1.0)
    shirt = mask_poly([(50, 102), (64, 108), (78, 102), (80, 128), (48, 128)])
    cv.toon(shirt, 0.5 + 0.25 * (cv.xx < 64) - 0.3 * blur(face, 2 * S), ch["collar"], [0.55, 0.85])
    cv.outline(shirt, hexc("0a0a10"), 0.8)
    # lapels
    for sg in (-1, 1):
        lap = mask_poly([(64 + sg * 13, 100), (64 + sg * 3, 107.5), (64 + sg * 11, 124), (64 + sg * 25, 128), (64 + sg * 27, 110), (64 + sg * 22, 102)])
        cv.toon(lap, 0.62 + 0.15 * (sg < 0) + 0.15 * cv.lam(lap, 4), GOLD, [0.35, 0.6, 0.85])
        cv.outline(lap, hexc("5a3a08"), 0.8)
    # V pin
    pin = mask_poly([(58.5, 114), (63.4, 114), (64, 120), (66.6, 114), (71.5, 114), (65, 126), (62.5, 126)]) * 0 + mask_poly([(72, 113), (77, 113), (74.8, 119)])
    cv.paint(pin, GOLD[3]); cv.outline(pin, hexc("5a3a08"), 0.6)
    # collar flap of the shirt
    cv.paint(mask_stroke([(52, 102), (64, 108.5), (76, 102)], 1.2), hexc("0a0a10"))


def skin_extra(cv, ch, E, t_ref):
    pass


def nose_extra(cv, ch, E):
    L = SK_LINE
    for sg in (-1, 1):
        cv.paint(mask_stroke(cr_spline([(64 + sg * 9.5, 71), (64 + sg * 12, 77), (64 + sg * 11.6, 84)], n=6), 0.6, 0.3), L * 0.9)   # nasolabial fold
        cv.paint(mask_stroke([(64 + sg * 22.5, 56), (64 + sg * 25.3, 55.2)], 0.5, 0.25), L * 0.9)
    cv.paint(mask_stroke(cr_spline([(53, 33), (64, 32), (75, 33)], n=6), 0.55, 0.35) * 0.7, L)


def after_eyes(cv, ch, E):
    # moustache + goatee drawn BEFORE the mouth
    wh = ch["hair"]
    mous = mask_poly(cr_spline([(64, 73.6), (58, 73.0), (52, 76.5), (48.5, 82), (52, 82.5), (58, 79.4), (64, 78.6), (70, 79.4), (76, 82.5), (79.5, 82), (76, 76.5), (70, 73.0)], closed=True, n=6))
    chin = mask_poly(cr_spline([(52, 84.5), (57, 83.0), (64, 82.2), (71, 83.0), (76, 84.5), (75, 92), (70, 99), (64, 101.5), (58, 99), (53, 92)], closed=True, n=6))
    for m, sd in ((chin, 31), (mous, 32)):
        paint_hair(cv, m, wh, (64, 70), strands=40, seed=sd, sigma=2.5, hl=None, hl_amt=0.28, swirl=0.0, length=(4, 10), wid=(0.6, 1.0),
                   flow=lambda x, y: math.atan2(1.0, (x - 64) * 0.12), outline=0.8, line=hexc("40384c"))
    # tinted shades (lenses over the eyes)
    FR = hexc("a8741c")
    for sg in (-1, 1):
        cx, cy = 64 + sg * 13.4, 56.0
        lens = mask_poly(cr_spline([(cx - 10.5, cy - 4.5), (cx, cy - 6.4), (cx + 10.5, cy - 4.8), (cx + 9.5, cy + 2.5), (cx + 4, cy + 7.4), (cx - 4, cy + 6.8), (cx - 9.6, cy + 2)], closed=True, n=6))
        AM = [hexc("7a4410"), hexc("b87a1c"), hexc("e0a438")]
        cv.paint(lens, AM[1])
        cv.paint(lens * (cv.yy < cy - 2.5) , AM[0])
        e = [q for q in cv.eyes if q["sg"] == sg][0]
        cv.paint(lens * e["m"], AM[2] * 0.0 + hexc("c89030"))
        ic = mask_ell(e["ex"] + e["gx"], e["ey"] + e["gy"] - 0.2, e["ir"] * 0.95, e["ir"] * 0.95)
        cv.paint(ic * e["m"] * lens, hexc("2a1a10"))
        cv.paint(mask_ell(e["ex"] + e["gx"] - 1.2, e["ey"] + e["gy"] - 1.3, 0.8, 0.8) * e["m"] * lens, hexc("fffafa"))
        cv.paint(mask_stroke([(cx - 6, cy - 2.2), (cx - 2.5, cy - 4.4)], 1.1, 0.5), AM[2])
        cv.paint(mask_stroke([(cx - 7, cy + 3.8), (cx - 2, cy + 6.0)], 0.9, 0.4), AM[2])
        cv.outline(lens, FR, 0.9)
    cv.paint(mask_stroke(cr_spline([(64 - 3.8, 53.6), (64, 52.4), (64 + 3.8, 53.6)], n=6), 1.2), FR)
    for sg in (-1, 1):
        cv.paint(mask_stroke([(64 + sg * 23.6, 53.4), (64 + sg * 29.2, 53.2)], 0.9), FR)


def front(cv, ch, E, face):
    # swept-back white hair with a pompadour wave
    pts = [(33, 62), (31, 48), (33, 33), (40, 20), (52, 11), (66, 5), (80, 6), (91, 13), (96, 24), (96, 38), (95, 62),
           (92, 50), (91, 42), (86, 35), (80, 31), (70, 29.5), (60, 29), (52, 31), (45, 35), (40, 42), (37, 52)]
    hair = mask_poly(cr_spline(pts, closed=True, n=6))
    hl = mask_ell(62, 14, 20, 3.8, rot=-0.15) + mask_ell(80, 22, 10, 2.5, rot=0.5)
    paint_hair(cv, hair, ch["hair"], (40, 40), strands=100, seed=44, sigma=6, hl=np.clip(hl, 0, 1), hl_amt=0.32, length=(10, 30), spread=1.2,
               flow=lambda x, y: math.atan2(-0.35 * (y - 8), 1.0) + (math.pi if False else 0) + 0.15 * math.sin(x * 0.2),
               line=hexc("40384c"))
