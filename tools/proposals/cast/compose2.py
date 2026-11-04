import sys
sys.path.insert(0, '/tmp/claude-0/s42')
import os, q2, cdef
from PIL import Image, ImageDraw, ImageFont
ORDER = ["player", "mia", "rosa", "dex", "dex_vault", "pimm", "lou", "victor", "robot"]
LAB = {"player": "You", "mia": "Mia", "rosa": "Rosa Bellini", "dex": "Dex (shop)", "dex_vault": "Dex (VaultMart)",
       "pimm": "Mr. Pimm", "lou": "Big Lou", "victor": "Victor Vault", "robot": "Valet (robot)"}
def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
os.makedirs('sprites', exist_ok=True); os.makedirs('portraits', exist_ok=True)
SP = {n: q2.sprites(n, 4) for n in ORDER}
PT = {n: q2.portrait(n) for n in ORDER}
for n in ORDER:
    for f, im in SP[n].items(): im.save(f'sprites/{n}_{f}.png')
    PT[n].save(f'portraits/{n}.png')
BG = (118, 124, 116, 255)
def centered(d, cx, y, s, f, fill=(255, 255, 255)):
    w = d.textlength(s, font=f); d.text((cx - w / 2, y), s, font=f, fill=fill)
# lineup
S1 = 4; cw = 32 * S1 + 16
W = max(cw * len(ORDER), 3 * 270 + 20)
rows_h = 64 * S1 + 50
H = rows_h + 3 * (2 * 64 * 2 + 40) + 40
img = Image.new('RGBA', (W, H), BG); d = ImageDraw.Draw(img)
f1, f2 = font(17), font(15)
d.text((10, 6), "Town Life - cast proposal (idle sprites, 4x; facing s)", font=f1, fill=(255, 255, 255))
for i, n in enumerate(ORDER):
    x0 = i * cw + 8
    d.ellipse([x0 + 8, 64 * S1 - 4 + 20, x0 + 120, 64 * S1 + 12 + 20 + 6], fill=(98, 104, 96, 255))  # soft ground patch
    img.alpha_composite(SP[n]['s'].resize((32 * S1, 64 * S1), Image.NEAREST), (x0, 24))
    centered(d, x0 + 64, 64 * S1 + 30, LAB[n], f2)
y0 = rows_h + 10
d.text((10, y0 - 4), "Other facings (2x): sw, w, nw, n  /  ne, e, se", font=f1, fill=(255, 255, 255))
y0 += 24
FAC1, FAC2 = ["sw", "w", "nw", "n"], ["ne", "e", "se"]
for i, n in enumerate(ORDER):
    bx = 10 + (i % 3) * 270 + (W - 3 * 270 - 20) // 2; by = y0 + (i // 3) * (2 * 128 + 40)
    for j, f in enumerate(FAC1):
        img.alpha_composite(SP[n][f].resize((64, 128), Image.NEAREST), (bx + j * 64, by))
    for j, f in enumerate(FAC2):
        img.alpha_composite(SP[n][f].resize((64, 128), Image.NEAREST), (bx + j * 64 + 32, by + 128))
    centered(d, bx + 128, by + 256 + 2, LAB[n], f2)
img.convert('RGB').save('lineup.png')
# portraits
S = 4; pad = 14
cols = 3; cwp = 64 * S + 2 * pad; chp = 64 * S + 46
img = Image.new('RGBA', (cols * cwp, 3 * chp + 30), (30, 34, 56, 255)); d = ImageDraw.Draw(img)
d.text((10, 4), "Dialogue portraits (64x64, shown 4x)", font=f1, fill=(248, 208, 96))
for i, n in enumerate(ORDER):
    x0 = (i % cols) * cwp + pad; y0 = 30 + (i // cols) * chp
    d.rectangle([x0 - 2, y0 - 2, x0 + 64 * S + 1, y0 + 64 * S + 1], fill=(72, 84, 136, 255))
    d.rectangle([x0, y0, x0 + 64 * S - 1, y0 + 64 * S - 1], fill=(40, 48, 88, 255))
    img.alpha_composite(PT[n].resize((64 * S, 64 * S), Image.NEAREST), (x0, y0))
    centered(d, x0 + 32 * S, y0 + 64 * S + 8, LAB[n], f1, (248, 208, 96))
img.convert('RGB').save('portraits.png')
