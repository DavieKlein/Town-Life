"""VaultMart Valet robot portrait: grey shell, gold trim, dark screen face (expressions are drawn on the screen)."""
import numpy as np, math
from pt import *

LINE = hexc("1c1e28")
SHELL = [hexc(h) for h in ("5a6070", "8a92a2", "c0c6d2", "eef1f6")]
GOLD = [hexc(h) for h in ("a06c14", "e0a828", "ffd458", "fff2a8")]
SCR = [hexc(h) for h in ("0a1424", "142a44", "1c3c5c")]
CYAN = [hexc(h) for h in ("1ca8c8", "5cdcf0", "d8fcff")]


def rrect(x0, y0, x1, y1, r):
    pts = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(7):
            a = math.radians(a0 + 90 * k / 6)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return mask_poly(pts)


def render(ex):
    cv = Canvas()
    # antenna
    cv.paint(mask_stroke([(64, 20), (64, 8)], 2.0), SHELL[0]); cv.outline(mask_stroke([(64, 20), (64, 8)], 2.0), LINE, 0.8)
    ball = mask_ell(64, 7, 3.6, 3.6)
    cv.toon(ball, 0.6 + 0.3 * cv.lam(ball, 1.5), GOLD, [0.3, 0.55, 0.8]); cv.outline(ball, LINE, 0.8)
    # neck
    neck = rrect(54, 84, 74, 108, 3)
    cv.toon(neck, 0.4 + 0.3 * (np.sin(cv.yy * 1.6) > 0) - 0.1, SHELL, [0.3, 0.5, 0.8]); cv.outline(neck, LINE, 0.9)
    # shoulders / chest
    pts = [(0, 128), (0, 118), (6, 108), (22, 102), (44, 100), (64, 104), (84, 100), (106, 102), (122, 108), (128, 118), (128, 128)]
    sh = mask_poly(cr_spline(pts, n=6) + [(128, 128), (0, 128)])
    t = cv.lam(sh, 14, gain=1.2, light=(-0.6, -0.5, 0.6)) + 0.1
    cv.toon(sh, t, SHELL, [0.30, 0.50, 0.72])
    cv.outline(sh, LINE, 1.0)
    # gold chest plate with a V mark
    plate = rrect(46, 112, 82, 128, 4)
    cv.toon(plate, 0.55 + 0.25 * (cv.xx < 64) + 0.1 * cv.lam(plate, 3), GOLD, [0.3, 0.55, 0.82]); cv.outline(plate, hexc("5a3a08"), 0.9)
    cv.paint(mask_poly([(55, 116), (59, 116), (64, 124), (69, 116), (73, 116), (66, 127), (62, 127)]), hexc("5a3a08"))
    for sg in (-1, 1):   # shoulder joints
        j = mask_ell(64 + sg * 50, 112, 9, 8)
        cv.toon(j, 0.5 + 0.3 * cv.lam(j, 3), GOLD, [0.3, 0.55, 0.82]); cv.outline(j, hexc("5a3a08"), 0.9)
    # head: rounded shell
    head = rrect(30, 14, 98, 88, 20)
    t = cv.lam(head, 9, gain=0.9, light=(-0.5, -0.6, 0.62)) + 0.12
    cv.toon(head, t, SHELL, [0.30, 0.50, 0.74])
    cv.outline(head, LINE, 1.1)
    # side ear pods (gold)
    for sg in (-1, 1):
        pod = rrect(64 + sg * 34 - 4, 40, 64 + sg * 34 + 4, 62, 3)
        cv.toon(pod, 0.55 + 0.2 * (sg < 0), GOLD, [0.3, 0.55, 0.82]); cv.outline(pod, hexc("5a3a08"), 0.8)
    # screen
    scr = rrect(38, 26, 90, 76, 12)
    t = 0.3 + 0.35 * np.clip((cv.yy - 26) / 50, 0, 1)
    cv.toon(scr, t, SCR, [0.45, 0.8]); cv.outline(scr, hexc("3a4050"), 1.3)
    cv.paint(mask_stroke(cr_spline([(44, 33), (48, 29.5), (56, 28.4)], n=5), 1.0, 0.4) * 0.55, hexc("8ab4d8"))   # glass glint
    # face on the screen
    def eye(cx, cy, w, h, rot=0.0, shape="rect"):
        m = rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, min(w, h) / 2.2) if shape == "rect" else mask_ell(cx, cy, w / 2, h / 2)
        cv.paint(blur(m, 1.6 * S) * 0.5, CYAN[0])
        cv.toon(m, 0.5 + 0.5 * np.clip((cy + h / 2 - cv.yy) / max(h, 1), 0, 1), CYAN, [0.3, 0.7])
        return m
    ey = 46
    if ex == "neutral":
        eye(53, ey, 8, 11); eye(75, ey, 8, 11)
        cv.paint(mask_stroke(cr_spline([(54, 62), (64, 63.5), (74, 62)], n=6), 1.4), CYAN[1])
    elif ex == "happy":
        for cx in (53, 75):
            cv.paint(mask_stroke(cr_spline([(cx - 5.5, ey + 3), (cx, ey - 5), (cx + 5.5, ey + 3)], n=6), 2.6), CYAN[1])
        cv.paint(mask_stroke(cr_spline([(50, 58), (56, 65), (64, 67.5), (72, 65), (78, 58)], n=6), 2.8), CYAN[1])
    elif ex == "angry":
        for sg in (-1, 1):
            cx = 64 + sg * 11
            m = eye(cx, ey + 1, 9, 9)
            # lid: dark wedge, lower on the inner side (towards the middle)
            lid = mask_poly([(cx - sg * 6, ey - 10), (cx + sg * 6, ey - 10), (cx + sg * 6, ey - 4.5), (cx - sg * 6, ey + 0.5)])
            lid = mask_poly([(cx + sg * 6, ey - 10), (cx - sg * 6, ey - 10), (cx - sg * 6, ey + 0.5), (cx + sg * 6, ey - 5.5)])
            cv.toon(lid * m, 0.1 + 0 * cv.xx, SCR, [0.5, 0.8])
        cv.paint(mask_stroke(cr_spline([(54, 65), (64, 61.5), (74, 65)], n=6), 1.6), CYAN[1])
    elif ex == "sad":
        for sg in (-1, 1):
            cx = 64 + sg * 11
            m = eye(cx, ey + 2, 8, 9)
            lid = mask_poly([(cx - sg * 6, ey - 8), (cx + sg * 6, ey - 8), (cx + sg * 6, ey + 1.5), (cx - sg * 6, ey - 3.5)])
            cv.toon(lid * m, 0.1 + 0 * cv.xx, SCR, [0.5, 0.8])
        cv.paint(mask_stroke(cr_spline([(54, 65), (64, 60.5), (74, 65)], n=6), 1.4), CYAN[1])
        cv.paint(mask_ell(80, 55, 1.5, 2.4), CYAN[2])   # a pixel "tear"
    else:  # surprised
        for cx in (53, 75):
            m = mask_ell(cx, ey, 6.6, 7.4)
            cv.paint(blur(m, 1.6 * S) * 0.5, CYAN[0]); cv.toon(m, 0.5 + 0.5 * np.clip((ey + 7 - cv.yy) / 14, 0, 1), CYAN, [0.3, 0.7])
            cv.paint(mask_ell(cx, ey, 2.6, 2.8), SCR[0])
        mo = mask_ell(64, 63, 4.2, 5.2)
        cv.paint(mo, CYAN[1]); cv.paint(mask_ell(64, 63, 2.2, 3.0), SCR[0])
    # cheek vents + gold trim line under the screen
    cv.paint(mask_stroke([(40, 82), (88, 82)], 1.6), GOLD[1])
    return cv
