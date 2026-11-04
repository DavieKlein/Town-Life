import sys, numpy as np
sys.path.insert(0, '/home/user/Town-Life/tools')
from PIL import Image
import build_assets as ba

def down(img, f=2):
    a = np.asarray(img.convert('RGBA')).astype(np.float64) / 255.0
    a[..., :3] *= a[..., 3:4]
    h, w = a.shape[0] // f, a.shape[1] // f
    a = a[:h*f, :w*f].reshape(h, f, w, f, 4).mean(axis=(1, 3))
    rgb = np.where(a[..., 3:4] > 0, a[..., :3] / np.maximum(a[..., 3:4], 1e-6), 0)
    a = np.concatenate([rgb, a[..., 3:4]], axis=2)
    return Image.fromarray(np.clip(a * 255 + .5, 0, 255).astype(np.uint8), 'RGBA')

def compose(prefix, f=2, bg=(10, 12, 24)):
    fl = ba.grade(down(Image.open(prefix + '_floor.png'), f))
    ob = ba.grade(down(Image.open(prefix + '_objects.png'), f))
    base = Image.new('RGBA', fl.size, bg + (255,))
    base.alpha_composite(fl); base.alpha_composite(ob)
    a = np.asarray(base.convert('RGB')).astype(np.float64)
    a = np.clip(np.round(a / 8.0), 0, 31) * 8       # GBA 5-bit colour
    return Image.fromarray(a.astype(np.uint8))

if __name__ == '__main__':
    im = compose(sys.argv[1])
    im.save(sys.argv[2]); print(im.size)
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(sys.argv[2].replace('.png', '_3x.png'))
