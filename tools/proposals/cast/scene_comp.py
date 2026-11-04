import sys; sys.path.insert(0,'/tmp/claude-0/s42')
from PIL import Image, ImageDraw, ImageFont
import numpy as np
def load(p, fix=True):
    im = Image.open(p).convert('RGBA')
    if fix:   # cover the "build ..." stamp in the top-left by smearing the row below it
        a = np.array(im)
        for y in range(0, 10): a[y, :175] = a[10, :175]
        im = Image.fromarray(a)
    return im
def put(base, name, face, x, y, shadow=True):
    sp = Image.open(f'sprites/{name}_{face}.png').convert('RGBA')
    if shadow:
        sh = Image.new('RGBA', base.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([x - 8, y - 3, x + 8, y + 3], fill=(10, 10, 20, 90))
        base.alpha_composite(sh)
    base.alpha_composite(sp, (x - 16, y - 54))
def font(sz):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz)
def tag(img, S, x, y, txt, h=60):
    d = ImageDraw.Draw(img); f = font(15)
    w = d.textlength(txt, font=f)
    cx, cy = x * S, (y - h) * S
    d.rectangle([cx - w / 2 - 5, cy - 2, cx + w / 2 + 5, cy + 20], fill=(24, 28, 56)); d.rectangle([cx - w / 2 - 5, cy - 2, cx + w / 2 + 5, cy + 20], outline=(248, 208, 96))
    d.text((cx - w / 2, cy), txt, font=f, fill=(248, 208, 96))
if __name__ == '__main__':
    base = load('shots/m4.png')
    cast = [("rosa", "sw", 94, 50, "Rosa"), ("dex", "ne", 58, 70, "Dex"), ("pimm", "se", 26, 58, "Mr. Pimm")]
    for n, f, x, y, t in sorted(cast, key=lambda c: c[3]):
        put(base, n, f, x, y)
    S = 4
    big = base.resize((240 * S, 160 * S), Image.NEAREST).convert('RGB')
    for n, f, x, y, t in cast: tag(big, S, x, y + 3, t, h=0)
    tag(big, S, 182, 70, "Mia", 0)
    tag(big, S, 120, 88, "You", 0)
    out = Image.new('RGB', (240 * S, 160 * S + 34), (24, 28, 56)); out.paste(big, (0, 34))
    d = ImageDraw.Draw(out); d.text((10, 6), "Corner Market proposal: Rosa, Dex and Mr. Pimm in the shop (Mia + player for scale)", font=font(17), fill=(255, 255, 255))
    out.save('in_scene.png')
