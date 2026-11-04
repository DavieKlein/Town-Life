import math, random
import numpy as np
from pt import *


def paint_hair(cv, mask, ramp, centre, strands=46, seed=1, sigma=6.0, hl=None, hl_amt=0.22, thr=(0.30, 0.46, 0.64), spread=1.0,
               swirl=0.35, length=(9, 22), line=None, curl=0.0, base=0.0, wid=(0.7, 1.3), outline=1.0, flow=None):
    rnd = random.Random(seed)
    t = cv.lam(mask, sigma, gain=0.9) + base
    light = np.zeros((W, W), np.float32)
    dark = np.zeros((W, W), np.float32)
    cx, cy = centre
    ys, xs = np.nonzero(mask[::S, ::S] > 0.5)
    if len(xs) == 0:
        return
    for i in range(strands):
        k = rnd.randrange(len(xs))
        x, y = float(xs[k]), float(ys[k])
        pts = [(x, y)]
        L = rnd.uniform(*length)
        steps = int(L / 1.2)
        for _ in range(steps):
            if flow is not None:
                ang = flow(x, y)
            else:
                ang = math.atan2(y - cy, x - cx) + swirl
            ang += rnd.uniform(-0.15, 0.15) * spread + curl * 0.05
            x += math.cos(ang) * 1.2
            y += math.sin(ang) * 1.2
            if mask[int(min(max(y, 0), N - 1)) * S, int(min(max(x, 0), N - 1)) * S] < 0.5:
                break
            pts.append((x, y))
        if len(pts) < 3:
            continue
        w = rnd.uniform(*wid)
        st = mask_stroke(pts, w * 0.8, w * 0.2, w_mid=w)
        if i % 2 == 0:
            light += st
        else:
            dark += st
    t = t + hl_amt * 1.3 * np.clip(blur(light, 0.3 * S) * 2.2, 0, 1) - hl_amt * 1.6 * np.clip(blur(dark, 0.3 * S) * 2.2, 0, 1)
    if hl is not None:
        t = t + hl_amt * blur(hl, 2.2 * S)
    cv.toon(mask, t, ramp, thr)
    if outline:
        cv.outline(mask, line if line is not None else hexc("201010"), outline)
    return t
