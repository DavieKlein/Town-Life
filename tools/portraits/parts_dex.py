import numpy as np, math
from pt import *
from hairlib import paint_hair
from chars import LINE, SK_LINE
from bodies import *

GOLD = [hexc(h) for h in ("a06c14", "e0a828", "ffd458", "fff2a8")]


def back(cv, ch, E):
    pass


def body(cv, ch, E, face):
    vault = ch.get("vault")
    neck_paint(cv, ch, face, w=11.5, shade=0.32)
    pts = [(0, 128), (2, 120), (10, 111), (26, 105), (44, 102), (54, 104), (64, 107), (74, 104), (84, 102), (102, 105), (118, 111), (126, 120), (128, 128)]
    sh, t = shoulders(cv, ch, pts, None, folds=(((24, 128), (30, 114)), ((104, 128), (98, 116)), ((14, 124), (20, 114))))
    cv.toon(sh, t, ch["cloth"], [0.30, 0.46, 0.66])
    cv.outline(sh, hexc("3a1a08") if not vault else hexc("30343c"), 1.0)
    if not vault:
        # green Corner Market apron: bib + straps over the orange shirt
        bib = mask_poly([(40, 128), (44, 116), (52, 110), (76, 110), (84, 116), (88, 128)])
        cv.toon(bib, 0.55 + 0.12 * (cv.xx < 60) - 0.1 * (cv.yy > 120) + 0.1 * cv.lam(bib, 5), ch["apron"], [0.30, 0.50, 0.72])
        cv.outline(bib, hexc("0c2c18"), 0.9)
        for sg in (-1, 1):
            strap = mask_stroke([(64 + sg * 11, 107.5), (64 + sg * 14, 112), (64 + sg * 13, 118)], 4.2)
            cv.toon(strap, 0.6 + 0 * cv.xx, ch["apron"], [0.35, 0.7])
            cv.outline(strap, hexc("0c2c18"), 0.8)
        tag = mask_poly([(70, 116), (79, 116), (79, 121), (70, 121)])
        cv.paint(tag, hexc("f6e8b0")); cv.outline(tag, hexc("5a4a20"), 0.6)
        cv.paint(mask_stroke([(72, 118.5), (77, 118.5)], 0.7), hexc("7a5a28"))
    # polo collar: two flaps + open placket
    sc = mask_ell(64, 103.5, 13.5, 6.4) * (cv.yy > 100)
    cv.toon(sc, 0.5 + 0.1 * (cv.xx < 64) - 0.25 * blur(face, 2 * S), ch["skin"], [0.30, 0.46, 0.66, 0.86])
    for sg in (-1, 1):
        fl = mask_poly([(64 + sg * 2, 99.5), (64 + sg * 15, 100), (64 + sg * 17, 106), (64 + sg * 9, 111), (64 + sg * 1, 106.5)])
        cv.toon(fl, 0.6 + 0.2 * (sg < 0) - 0.2 * blur(face, 2 * S), ch["collar"] if not vault else ch["cloth"], [0.35, 0.65])
        cv.outline(fl, hexc("5a4a30") if not vault else hexc("30343c"), 0.8)
    if vault:
        # slick gold tie
        tie = mask_poly([(61.5, 106), (66.5, 106), (68, 112), (66.5, 128), (61.5, 128), (60, 112)])
        cv.toon(tie, 0.55 + 0.2 * (cv.xx < 64), GOLD, [0.35, 0.62, 0.86])
        cv.outline(tie, hexc("5a3a08"), 0.8)
        knot = mask_poly([(60.5, 103.5), (67.5, 103.5), (66.8, 108.6), (61.2, 108.6)])
        cv.toon(knot, 0.6 + 0.2 * (cv.xx < 64), GOLD, [0.35, 0.62, 0.86])
        cv.outline(knot, hexc("5a3a08"), 0.8)
        # badge
        bd = mask_ell(82, 116, 3.4, 3.4)
        cv.paint(bd, GOLD[2]); cv.outline(bd, hexc("5a3a08"), 0.7)
        cv.paint(mask_ell(81.2, 115.2, 1.0, 1.0), GOLD[3])


def skin_extra(cv, ch, E, t_ref):
    pass


def nose_extra(cv, ch, E):
    pass


def after_eyes(cv, ch, E):
    pass


def front(cv, ch, E, face):
    if not ch.get("vault"):
        # messy short hair, spiky fringe
        pts = [(33, 60), (31, 44), (34, 30), (41, 19), (52, 11), (64, 8), (76, 9), (87, 14), (94, 23), (97, 36), (95, 60),
               (93, 50), (91, 41), (87, 36), (83, 40), (79, 32), (74, 40), (69, 31), (63, 39), (58, 31), (53, 40), (48, 32), (44, 41), (40, 36), (37, 47), (36, 54)]
        hair = mask_poly(cr_spline(pts, closed=True, n=5))
        # a few spikes on top
        for (x0, x1, yt) in ((50, 56, 5), (62, 68, 3), (74, 80, 5)):
            hair = np.maximum(hair, mask_poly([(x0, 14), ((x0 + x1) / 2 + 1, yt), (x1, 14)]))
        hl = mask_ell(66, 14, 14, 4, rot=-0.1)
        paint_hair(cv, hair, ch["hair"], (66, 6), strands=80, seed=21, sigma=5.5, hl=hl, hl_amt=0.3, swirl=1.1, length=(7, 20), spread=1.5,
                   flow=lambda x, y: math.atan2(max(y - 2, 3) * 0.9, (x - 66) * 0.5))
    else:
        # slick side-parted hair, glossy
        pts = [(33, 60), (31, 44), (34, 30), (41, 19), (52, 11), (66, 7), (80, 9), (91, 16), (96, 28), (96, 44), (95, 60),
               (93, 48), (90, 40), (84, 34), (74, 31), (62, 30.5), (52, 33), (44, 38), (39, 45), (37, 54)]
        hair = mask_poly(cr_spline(pts, closed=True, n=5))
        hl = mask_ell(60, 15, 20, 3.2, rot=-0.12) + mask_ell(80, 22, 9, 2.2, rot=0.5)
        paint_hair(cv, hair, ch["hair"], (40, 40), strands=90, seed=23, sigma=6, hl=np.clip(hl, 0, 1), hl_amt=0.4, length=(10, 28), spread=0.8,
                   flow=lambda x, y: math.atan2(-0.28 * (y - 8), 1.0) + 0.1 * math.sin(x * 0.2))
        cv.paint(mask_stroke(cr_spline([(46, 14.5), (52, 23), (56, 32)], n=6), 0.7, 0.4), hexc("0c0806"))   # parting line
