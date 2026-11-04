"""Tiny 2D painting toolkit for the portrait proposal (supersampled masks, toon-shaded tone maps, 2 palettes per portrait)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw

N = 128          # final portrait size
S = 6            # supersampling
W = N * S


def cr_spline(pts, closed=False, n=10):
    """Catmull-Rom through pts."""
    pts = [np.array(p, float) for p in pts]
    out = []
    m = len(pts)
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = pts[(i - 1) % m] if (closed or i > 0) else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % m]
        p3 = pts[(i + 2) % m] if (closed or i + 2 < m) else pts[-1]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(pts[-1])
    return [tuple(p) for p in out]


def mirror(half, cx=64.0):
    """half = right-side points ordered top -> bottom (x >= cx); returns a closed loop."""
    left = [(2 * cx - x, y) for (x, y) in reversed(half[1:-1])]
    return half + left


def blur(a, sigma):
    """Gaussian blur (sigma in supersampled px) via FFT."""
    if sigma <= 0.01:
        return a
    h, w = a.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    g = np.exp(-2 * (math.pi * sigma) ** 2 * (fx * fx + fy * fy))
    return np.fft.irfft2(np.fft.rfft2(a) * g, s=a.shape).astype(np.float32)


def mask_poly(pts):
    im = Image.new("L", (W, W), 0)
    ImageDraw.Draw(im).polygon([(x * S, y * S) for x, y in pts], fill=255)
    return np.asarray(im, dtype=np.float32) / 255.0


def mask_ell(cx, cy, rx, ry, rot=0.0):
    if abs(rot) < 1e-6:
        im = Image.new("L", (W, W), 0)
        ImageDraw.Draw(im).ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=255)
        return np.asarray(im, dtype=np.float32) / 255.0
    pts = []
    for k in range(48):
        a = 2 * math.pi * k / 48
        x, y = rx * math.cos(a), ry * math.sin(a)
        c, s = math.cos(rot), math.sin(rot)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return mask_poly(pts)


def mask_stroke(pts, w0, w1=None, w_mid=None, step=0.3):
    """Variable-width stroke along a polyline/spline (width in final px)."""
    im = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(im)
    pts = [np.array(p, float) for p in pts]
    seg = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    total = sum(seg) or 1e-6
    acc = 0.0
    w1 = w0 if w1 is None else w1
    for i in range(len(pts) - 1):
        n = max(1, int(seg[i] / step))
        for k in range(n + 1):
            t = (acc + seg[i] * k / n) / total
            if w_mid is None:
                w = w0 + (w1 - w0) * t
            else:
                w = (w0 + (w_mid - w0) * (t * 2) if t < 0.5 else w_mid + (w1 - w_mid) * (t * 2 - 1))
            p = pts[i] + (pts[i + 1] - pts[i]) * k / n
            r = max(w, 0.01) * 0.5 * S
            d.ellipse([p[0] * S - r, p[1] * S - r, p[0] * S + r, p[1] * S + r], fill=255)
        acc += seg[i]
    return np.asarray(im, dtype=np.float32) / 255.0


def dilate(m, px):
    """Binary dilation by px (supersampled px) using a max filter on a thresholded mask."""
    from PIL import ImageFilter
    k = int(px) * 2 + 1
    im = Image.fromarray((m > 0.5).astype(np.uint8) * 255)
    return np.asarray(im.filter(ImageFilter.MaxFilter(k)), dtype=np.float32) / 255.0


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


class Canvas:
    def __init__(self):
        self.rgb = np.zeros((W, W, 3), np.float32)
        self.a = np.zeros((W, W), np.float32)
        yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
        self.xx, self.yy = xx / S, yy / S

    def paint(self, m, col):
        """col: rgb triple or (W,W,3) array."""
        mm = m[..., None]
        c = np.asarray(col, np.float32)
        self.rgb = self.rgb * (1 - mm) + c * mm
        self.a = np.maximum(self.a, m)

    def outline(self, m, col, px=1.0, inside=False):
        ring = dilate(m, px * S) * (1 - (m > 0.5)) if not inside else (m > 0.5) * (1 - 0)
        self.paint(ring, col)
        self.a = np.maximum(self.a, ring)

    def toon(self, m, t, ramp, thr):
        idx = np.searchsorted(np.asarray(thr), t)
        idx = np.clip(idx, 0, len(ramp) - 1)
        col = np.asarray(ramp, np.float32)[idx]
        self.paint(m, col)

    def lam(self, m, sigma, gain=1.0, light=(-0.5, -0.6, 0.62)):
        """Rounded-bulge shading of a mask: Lambert term of the blurred mask treated as a height field, ~0.5 flat."""
        h = blur(m, sigma * S)
        h = h / max(h.max(), 1e-6)
        gy, gx = np.gradient(h * sigma * 2.2 * gain)
        gx = gx * S
        gy = gy * S
        n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
        n /= np.linalg.norm(n, axis=-1, keepdims=True)
        L = np.array(light, np.float32)
        L /= np.linalg.norm(L)
        d = n @ L
        flat = L[2]
        return 0.55 + (d - flat) * 1.4

    def to_img(self):
        a = self.a
        img = np.concatenate([self.rgb, a[..., None] * 255.0 / 255.0 * 255], -1)
        return img


def downsample(cv, n=None):
    """Area-average to n x n (default N), alpha-weighted."""
    n = n or N
    s = W // n
    rgb = cv.rgb * cv.a[..., None]
    rgb = rgb.reshape(n, s, n, s, 3).mean((1, 3))
    a = cv.a.reshape(n, s, n, s).mean((1, 3))
    out = np.where(a[..., None] > 0.02, rgb / np.maximum(a[..., None], 1e-6), 0)
    return out, a
