"""Procedural head-and-shoulders portraits (own design). python3 chars.py <char> <expr> -> por/<char>_<expr>.png (alpha)."""
import math, random, sys, os
import numpy as np
from PIL import Image
from pt import *

LINE = hexc("2a1a1c")          # outline / lashes
SK_LINE = hexc("7a4038")       # soft skin lines (creases, nostrils)

EXPR = {
    # brow offsets (inner, mid, outer) in px (negative = up); eye open (0..1.3); slant (inner upper lid down, +) ; lower (lower lid up, +)
    "neutral": dict(brow=(0, -0.3, 0.5), open=1.0, slant=0.0, lower=0.0, mouth=dict(corner=0.3, open=0.0, wide=1.0, teeth=False), blush=0.0, gaze=(0, 0.2), pupil=1.0),
    "happy":   dict(brow=(-0.8, -1.8, -1.0), open=0.7, slant=0.0, lower=2.2, mouth=dict(corner=3.2, open=5.2, wide=1.28, teeth=True), blush=1.0, gaze=(0, 0.2), pupil=1.1),
    "angry":   dict(brow=(3.2, 0.8, -1.6), open=0.86, slant=1.5, lower=0.3, mouth=dict(corner=-1.6, open=3.0, wide=1.12, teeth=True, clench=True), blush=0.0, gaze=(0, 0.2), pupil=0.85),
    "sad":     dict(brow=(-2.6, -1.0, 1.8), open=0.82, slant=-1.2, lower=0.0, mouth=dict(corner=-2.4, open=0.0, wide=0.82, teeth=False), blush=0.0, gaze=(0, 0.9), pupil=1.15),
    "surprised": dict(brow=(-4.2, -5.2, -3.6), open=1.32, slant=0.0, lower=0.0, mouth=dict(corner=0.0, open=7.5, wide=0.7, teeth=False, round=True), blush=0.0, gaze=(0, 0.0), pupil=0.8),
}

CH = {
    "player": dict(
        fw=0.9, jaw=0.95, chin=96, fem=False, eye_w=1.12, iris_r=4.5, brow_w=2.5,
        skin=["a85c48", "d98e72", "f2b896", "fdd8b8", "fff0d8"], blush="f08a7a", lip=["b0504a", "d27468", "7a2e30"],
        iris=["3a2a1c", "6a4a2c", "a07a48"], hair=["2a1812", "4e3020", "7a5232", "b08050"], brow_col="2e1c14",
        cloth=["20386c", "3262b4", "4c82d8", "7aa8f0"], collar=["c8a878", "ecdcb4", "fff4d8"],
    ),
    "mia": dict(
        fw=0.86, jaw=0.88, chin=95, fem=True, eye_w=1.15, iris_r=4.9, brow_w=1.7,
        skin=["a85c4c", "e0987e", "f8c4a6", "ffe0c8", "fff2e2"], blush="f0807a", lip=["b83c48", "dc5a62", "7a2434"],
        iris=["1c5a62", "2aa0a8", "8adcd0"], hair=["7a2a14", "c4501c", "ee7c34", "ffb060"], brow_col="a04420",
        cloth=["167a78", "28aaa4", "50d0c4", "9af0e0"], collar=["167a78", "28aaa4", "50d0c4"],
    ),
    "rosa": dict(
        fw=0.94, jaw=0.98, chin=95, fem=True, eye_w=1.05, iris_r=4.2, brow_w=1.7,
        skin=["9a5a4a", "d08c74", "ecb498", "f8d2b8", "ffe8d4"], blush="e87878", lip=["a84050", "cc6068", "6a2430"],
        iris=["3a3a30", "6a6850", "a8a078"], hair=["7c7a8c", "aaa8ba", "d4d2e0", "fafaff"], brow_col="8a889a",
        cloth=["4a1424", "802c40", "b0485c", "d87488"], collar=["d8d2d0", "f6f2f0", "ffffff"],
    ),
    "victor": dict(
        fw=0.95, jaw=1.06, chin=97, brow_gain=1.5, fem=False, eye_w=1.05, iris_r=4.1, brow_w=3.2,
        skin=["9a5238", "cc7e5c", "e8a47e", "f6c49c", "ffe0c0"], blush="e08060", lip=["a8544a", "c8786a", "6a2c2c"],
        iris=["20202a", "484a58", "808498"], hair=["8c8aa0", "bcbad0", "e6e4f2", "ffffff"], brow_col="d8d6e8",
        cloth=["8a5a10", "d8a22c", "f8d450", "fff0a0"], collar=["101014", "2a2a34", "4a4a58"],
    ),
}
CH["dex"] = dict(
    fw=0.9, jaw=0.92, chin=96, fem=False, eye_w=1.1, iris_r=4.4, brow_w=2.4,
    skin=["8a5230", "c07c50", "dfa676", "f0c394", "ffdfb8"], blush="f08a6a", lip=["a8504a", "ca7468", "782e30"],
    iris=["2a1a10", "5a3a20", "8a6034"], hair=["140c0a", "2a1c18", "46302a", "6a4a3c"], brow_col="1a100c",
    cloth=["8c3a14", "d8662a", "f08a46", "ffb878"], collar=["b8a888", "e8dcc0", "fff4dc"], apron=["1c5a30", "2f7a45", "4c9c60", "7cc890"],
)
CH["dex_vault"] = dict(CH["dex"], cloth=["6a7078", "a3a9b2", "c8cdd4", "eef0f3"], collar=["a0a4ac", "eef0f3", "ffffff"], vault=True, parts="dex")
CH["pimm"] = dict(
    fw=0.88, jaw=0.9, chin=94, fem=False, eye_w=1.0, iris_r=4.0, brow_w=3.0, brow_gain=1.2,
    skin=["9a6a58", "d09a84", "e9bf9c", "f6d8c0", "fff0e0"], blush="e88a78", lip=["a0605a", "c48478", "6a3430"],
    iris=["2a3a4a", "5a7288", "90aec0"], hair=["8a8a96", "bcbcc8", "e8e8ee", "ffffff"], brow_col="d4d4de",
    cloth=["6a5430", "a98d5c", "c8ac78", "e6d0a0"], collar=["6a1a1a", "a8312f", "d05048"], cap=["4a3420", "8b6b45", "b08c5c", "d0aa78"],
)
CH["lou"] = dict(
    fw=1.1, jaw=1.1, chin=98, fem=False, eye_w=1.0, iris_r=4.2, brow_w=3.0, rosy=True,
    skin=["9a5e3c", "cc8c60", "e6b48a", "f6d0a8", "ffe8cc"], blush="ec7a68", lip=["a8504a", "ca7468", "782e30"],
    iris=["2a1a10", "5a3a20", "8a6034"], hair=["20140c", "3a2a1e", "5a4230", "7a5c44"], brow_col="2a1a10",
    cloth=["8a1e1a", "b83a32", "d85a4c", "f08a78"], collar=["b8b4aa", "f4f1ea", "ffffff"], hat=["a8b0c0", "dfe4ee", "fbfbfb", "ffffff"],
)
CH["okafor"] = dict(
    fw=0.88, jaw=0.9, chin=95, fem=True, eye_w=1.08, iris_r=4.4, brow_w=1.9,
    skin=["6a3c24", "9a6240", "c08a60", "dca87c", "f0ccaa"], blush="d0705a", lip=["7a2c34", "a8505a", "50181e"],
    iris=["1e1208", "3e2814", "70502c"], hair=["0c0806", "1c1410", "30241c", "4a3a2e"], brow_col="140c08",
    cloth=["8a9aa4", "c8d4d8", "eef2f2", "ffffff"], collar=["12625f", "1f9a94", "3cc4bc", "8ae8dc"],
)
CH["robot"] = dict(CH["player"], skin=CH["player"]["skin"], blush="f08a7a")
for c in CH.values():
    for k in ("skin", "iris", "hair", "cloth", "collar", "lip", "apron", "cap", "hat"):
        if k in c:
            c[k] = [hexc(h) for h in c[k]]
    c["blush"] = hexc(c["blush"]); c["brow_col"] = hexc(c["brow_col"])


def face_loop(ch):
    half = [(64, 21), (76, 22.5), (86, 28), (91.5, 38), (93, 50), (92.5, 62), (90, 73), (84.5, 84), (76, 92), (64, 95)]
    out = []
    for (x, y) in half:
        kx = ch["fw"] * (1 + (ch["jaw"] - 1) * min(1, max(0, (y - 58) / 25)))
        yy = y if y < 60 else 60 + (y - 60) * (ch["chin"] - 60) / 35
        out.append((64 + (x - 64) * kx, yy))
    return cr_spline(mirror(out), closed=True, n=8)


def eye_geom(ch, ex_, sg):
    """returns functions for upper / lower lid of one eye."""
    hw = 7.2 * ch["eye_w"]
    ex = 64 + sg * 13.0 * (ch["fw"] / 0.9) ** 0.6
    return ex, hw


def draw_eye(cv, ch, E, sg, ey=56.0):
    ex, hw = eye_geom(ch, 0, sg)
    H = 5.4 if not ch["fem"] else 6.0
    op = E["open"]
    us = np.linspace(-1, 1, 41)
    # sg>0 : right-hand eye on screen; inner corner is at u=-1 (towards the nose)
    xs = ex + sg * hw * us
    yu = ey - op * H * (1 - us ** 2) ** 0.65 + E["slant"] * (1 - us) * 0.5 - 0.6 * (us + 1) * 0.5 * (1 if ch["fem"] else 0.4)
    ylow = ey + (0.45 + 0.5 * op) * 1.55 * (1 - us ** 2) ** 0.8 - E["lower"] * (1 - us ** 2) ** 0.8 - 0.3 * (us + 1) * 0.5
    ylow = np.maximum(ylow, yu + 0.2)
    poly = list(zip(xs, yu)) + list(zip(xs[::-1], ylow[::-1]))
    m = mask_poly(poly)
    cv.__dict__.setdefault('eyes', []).append(dict(m=m, sg=sg, ex=ex, ey=ey, gx=E['gaze'][0], gy=E['gaze'][1], ir=ch['iris_r'], pr=1.75 * E['pupil']))
    # sclera
    shade = blur(mask_poly(list(zip(xs, yu - 2.2)) + list(zip(xs[::-1], yu + 1.6))), 1.2 * S)
    sclera = np.where(shade[..., None] > 0.45, hexc("d4d6ea"), hexc("fffafa"))
    cv.paint(m, sclera)
    # iris / pupil clipped to the eye
    gx, gy = E["gaze"]
    ir = ch["iris_r"] * (1.0 if E["open"] < 1.2 else 0.95)
    icx, icy = ex + gx + sg * 0.0, ey + gy - 0.2
    imask = mask_ell(icx, icy, ir, ir * 1.04)
    ygrad = np.clip((cv.yy - (icy - ir)) / (2 * ir), 0, 1)
    ic = np.where(ygrad[..., None] < 0.38, ch["iris"][0], np.where(ygrad[..., None] < 0.72, ch["iris"][1], ch["iris"][2]))
    cv.paint(imask * m, ic)
    # limbal ring + pupil
    ring = imask * (1 - mask_ell(icx, icy, ir - 0.75, ir * 1.04 - 0.75))
    cv.paint(ring * m, ch["iris"][0] * 0.55)
    pr = 1.75 * E["pupil"]
    cv.paint(mask_ell(icx, icy + 0.1, pr, pr) * m, LINE)
    cv.paint(mask_ell(icx - 1.3, icy - 1.4, 0.95, 0.95) * m, hexc("ffffff"))
    cv.paint(mask_ell(icx + 1.4, icy + 1.3, 0.5, 0.5) * m * (E["open"] > 0.5), hexc("d8f0ff"))
    # upper lid shadow (soft) on the eyeball
    cv.paint(mask_stroke(list(zip(xs, yu + 0.9)), 1.4) * m * 0.55, hexc("38242c"))
    # lids
    w_lid = 1.55 if ch["fem"] else 1.35
    lid = list(zip(xs, yu))
    cv.paint(mask_stroke(lid, w_lid * 0.8, w_lid, w_mid=w_lid * 1.1), LINE)
    if ch["fem"] or E["open"] < 0.7:   # outer flick / lashes
        ox, oy = xs[-1], yu[-1]
        cv.paint(mask_stroke([(ox - sg * 0.6, oy + 0.3), (ox + sg * 1.4, oy - 0.7), (ox + sg * 2.4, oy - 1.4)], 1.1, 0.5), LINE)
    if E["open"] > 0.35:   # crease
        cr = [(x, y - 1.7 - op * 0.9) for x, y in zip(xs[6:-5:2], yu[6:-5:2])]
        cv.paint(mask_stroke(cr, 0.7, 0.4) * (1 - m), SK_LINE)
    lower = list(zip(xs[3:-3], ylow[3:-3]))
    cv.paint(mask_stroke(lower, 0.55), SK_LINE * 0.9)
    # inner corner
    cv.paint(mask_ell(xs[0] + sg * 0.5, ey + 0.5, 0.7, 0.55), hexc("e8a090"))
    return m


def draw_brow(cv, ch, E, sg, by=47.5):
    ex, hw = eye_geom(ch, 0, sg)
    bi, bm, bo = [v * ch.get('brow_gain', 1.0) for v in E["brow"]]
    thick = ch["brow_w"]
    if ch["fem"]:
        arch = -1.0
    else:
        arch = -0.5
    pts = [(ex - sg * hw * 0.95, by + bi + 1.0), (ex - sg * hw * 0.2, by + bm + arch * 1.2), (ex + sg * hw * 0.55, by + (bm + bo) * 0.5 + arch), (ex + sg * hw * 1.3, by + bo + 1.2)]
    sp = cr_spline(pts, n=8)
    m = mask_stroke(sp, thick * 0.9, thick * 0.35, w_mid=thick)
    cv.paint(m, ch["brow_col"])
    return m


def draw_mouth(cv, ch, E, ex_t, my=80.5):
    M = E["mouth"]
    c, op, wd = M["corner"], M["open"], M["wide"]
    hw = 8.6 * wd
    us = np.linspace(-1, 1, 41)
    xs = 64 + hw * us
    cur = -c * (us ** 2)                              # corners rise for a smile (c > 0)
    yu = my + cur + 0.4 * (1 - us ** 2) * 0.0
    # cupid's bow
    yu = yu - 0.7 * np.exp(-(us / 0.35) ** 2) * 0
    if M.get("round"):
        yl = yu + op * (1 - us ** 2) ** 0.5
        yu = yu - 0.3 * (1 - us ** 2)
    else:
        yl = yu + op * (1 - us ** 2) ** 0.9
    lipw = 1.9 if ch["fem"] else 1.5
    LIP, LD = ch["lip"][1], ch["lip"][2]
    if op > 0.3:
        mm = mask_poly(list(zip(xs, yu)) + list(zip(xs[::-1], yl[::-1])))
        cv.paint(mm, hexc("4a1a24"))
        if M["teeth"]:
            th = mask_poly(list(zip(xs, yu + 0.2)) + list(zip(xs[::-1], np.minimum(yu + 0.2 + op * 0.62, yl - 0.6)[::-1])))
            cv.paint(th * mm * (np.abs(cv.xx - 64) < hw * 0.88), hexc("fffcf6"))
            if M.get("clench"):
                cv.paint(mask_stroke([(64 - hw * 0.8, my + op * 0.32 + 0.6), (64 + hw * 0.8, my + op * 0.32 + 0.6)], 0.5) * mm, hexc("9a8a90"))
        tg = mask_ell(64, my + op * 0.9 + 0.2, hw * 0.45, op * 0.3 + 0.2)
        cv.paint(tg * mm * (not M.get("clench")), hexc("d85a68"))
        # upper lip over the opening, lower lip under
        cv.paint(mask_stroke(list(zip(xs, yu - lipw * 0.3)), lipw * 0.9, lipw * 0.9, w_mid=lipw * 1.2) * (1 - 0 * mm), LIP)
        low = mask_stroke(list(zip(xs[4:-4], yl[4:-4] + lipw * 0.55)), lipw * 1.15, lipw * 0.6, w_mid=lipw * 1.6)
        cv.paint(low * (1 - mm), LIP)
        cv.paint(mask_stroke(list(zip(xs[8:-8], yl[8:-8] + lipw * 0.55)), lipw * 0.5) * (1 - mm) * 0.5, LD)
        cv.paint(mask_stroke(list(zip(xs, yu)), 0.75) * 0 + mask_stroke(list(zip(xs, yl)), 0.7), hexc("4a1a24"))
        cv.paint(mask_stroke(list(zip(xs, yu - 0.1)), 0.8), hexc("4a1a24"))
        cv.paint(mask_stroke(list(zip(xs, yu - lipw * 0.55)), 0.5) * 0.0, LD)
        for sgn in (-1, 1):   # corners
            cv.paint(mask_ell(64 + sgn * hw * 1.02, yu[0] - 0.3, 0.5, 0.7), SK_LINE)
    else:
        top = mask_stroke(list(zip(xs, yu - lipw * 0.35)), lipw * 0.9, lipw * 0.9, w_mid=lipw * 1.2)
        low = mask_stroke(list(zip(xs[3:-3], yu[3:-3] + lipw * 0.75)), lipw * 0.9, lipw * 0.9, w_mid=lipw * 1.45)
        cv.paint(low, LIP)
        cv.paint(top, LD * 0.0 + ch["lip"][0] * 1.0 + 12)
        cv.paint(mask_stroke(list(zip(xs, yu)), 0.85), hexc("5a2430"))
        for sgn in (-1, 1):
            cv.paint(mask_ell(64 + sgn * hw * 1.03, yu[0] - 0.2, 0.55, 0.65), SK_LINE)
        cv.paint(mask_stroke(list(zip(xs[10:-10], yu[10:-10] + lipw * 1.6)), 0.5) * 0.4, ch["lip"][2])
    return hw


def render(name, ex, seed=3):
    ch = CH[name]
    E = EXPR[ex]
    cv = Canvas()
    if name == "robot":
        import robot
        return robot.render(ex)
    P = __import__("parts_" + ch.get("parts", name))
    cv_cfg = dict(ch=ch, E=E, cv=cv)
    P.back(cv, ch, E)
    # neck
    neck = mask_poly([(51, 80), (77, 80), (79, 112), (49, 112)])
    face = mask_poly(face_loop(ch))
    P.body(cv, ch, E, face)
    # ears
    for sg in (-1, 1):
        ear = mask_ell(64 + sg * 29.8 * ch["fw"], 60, 3.7, 7.4, rot=sg * 0.1)
        cv.paint(ear, ch["skin"][2]); cv.outline(ear, SK_LINE * 0.8, 0.8)
        cv.paint(mask_ell(64 + sg * 30.2 * ch["fw"], 60.5, 1.6, 4.4, rot=sg * 0.1), ch["skin"][1])
    # face tone
    def ss(a, b, x): return np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))
    t = 0.62 + 0.3 * cv.lam(face, 7.0, gain=0.5) - 0.186 - 0.30 * ss(74, 94, cv.xx) + 0.06 * (1 - ss(40, 64, cv.xx)) - 0.1 * ss(84, 96, cv.yy)
    fx, fy = cv.xx, cv.yy
    def soft(m, s): return blur(m, s * S)
    t = t + 0.09 * soft(mask_ell(64, 33, 20, 7), 4.0)                      # forehead light
    for sg in (-1, 1):
        t = t - 0.20 * soft(mask_ell(64 + sg * 13, 55, 9, 5), 2.2)         # eye sockets
        t = t + (0.07 + 0.03 * (sg < 0)) * soft(mask_ell(64 + sg * 19, 68, 6, 5), 2.5)   # cheekbone light
    t = t - 0.22 * soft(mask_poly([(66.5, 58), (70, 60), (71.5, 70), (67, 71)]), 1.6)    # nose shadow (light from left)
    t = t + 0.10 * soft(mask_ell(63.4, 58, 1.7, 7), 1.6)                   # bridge highlight
    t = t - 0.22 * soft(mask_ell(64, 72.6, 6.5, 2.0), 1.4)                  # under the nose
    t = t - 0.12 * soft(mask_ell(64, 88.5, 7, 2.4), 1.5)                    # under the lip
    t = t - 0.06 * soft(mask_ell(64, 92, 9, 2.5), 2.0)                      # chin shade
    P.skin_extra(cv, ch, E, t_ref=[t])
    t = t_ref_get(t)
    cv.toon(face, t, ch["skin"], [0.30, 0.46, 0.72, 0.90])
    cv.outline(face, SK_LINE * 0.55 + LINE * 0.3, 0.9)
    # blush
    if E["blush"] > 0 or ch.get("rosy"):
        b = max(E["blush"], 0.55 if ch.get("rosy") else 0)
        for sg in (-1, 1):
            cv.paint(mask_ell(64 + sg * 19, 69, 6.3, 3.4) * face * 0.6 * b, ch["blush"])
    # nose
    nostr = mask_ell(60.4, 71.6, 1.5, 1.0), mask_ell(67.6, 71.6, 1.5, 1.0)
    for m in nostr:
        cv.paint(m, SK_LINE * 0.8)
    cv.paint(mask_stroke([(59.0, 70.0), (60.6, 72.6), (64, 73.4), (67.4, 72.6), (69, 70.0)], 0.65), SK_LINE * 0.75)
    cv.paint(mask_ell(64.2, 69.2, 1.6, 1.0) * 0.85, ch["skin"][4])        # tip glint
    P.nose_extra(cv, ch, E)
    for sg in (-1, 1):
        draw_eye(cv, ch, E, sg)
    P.after_eyes(cv, ch, E)
    for sg in (-1, 1):
        draw_brow(cv, ch, E, sg)
    draw_mouth(cv, ch, E, None)
    P.front(cv, ch, E, face)
    return cv


def t_ref_get(t):
    return t


if __name__ == "__main__":
    name, ex = sys.argv[1], sys.argv[2]
    cv = render(name, ex)
    rgb, a = downsample(cv)
    im = np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8)
    os.makedirs("por", exist_ok=True)
    Image.fromarray(im, "RGBA").save(f"por/{name}_{ex}_raw.png")
