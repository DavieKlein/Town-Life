import sys, numpy as np
from PIL import Image
sys.path.insert(0, '/home/user/Town-Life/tools')
import build_assets as ba
FAC = ["s","sw","w","nw","n","ne","e","se"]
OUT = np.array([40., 30., 40.])
def quant(frames):
    """frames: list of (rgb, alpha) -> list of RGBA PIL images with one shared 15-colour palette."""
    px = np.concatenate([rgb[a] for rgb, a in frames]) * ba.WEIGHT
    cols = ba.to5(ba.kmeans(px, 14, iters=15) / ba.WEIGHT)
    cols = ba.to5(np.concatenate([cols, [OUT]]))
    cw = cols * ba.WEIGHT
    res = []
    for rgb, a in frames:
        d = ((rgb[..., None, :] * ba.WEIGHT - cw[None, None]) ** 2).sum(3); idx = d.argmin(2)
        img = np.zeros(rgb.shape[:2] + (4,), np.uint8)
        img[..., :3] = cols[idx].astype(np.uint8); img[..., 3] = a * 255
        res.append(Image.fromarray(img, 'RGBA'))
    return res
def sprites(name, ss, size=(32, 64)):
    fr = [ba.sprite_frame(f'r/{name}/{f}_0.png', ss, *size) for f in FAC]
    return dict(zip(FAC, quant(fr)))
def portrait(name, size=64):
    p = f'r/{name}/portrait.png'; ss = Image.open(p).size[0] // size
    return quant([ba.sprite_frame(p, ss, size, size)])[0]
