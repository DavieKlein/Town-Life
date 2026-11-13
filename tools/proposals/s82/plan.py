"""Labelled top-down plans: CURRENT Old Block (with numbered problem markers) next to the REV 3 proposal.   python3 plan.py OUT.png
Also writes OUT_current_iso.png: the real current map (rebuilt from data/*.bin) at 0.5x with the same numbered markers."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import scene as sc  # noqa: E402,F401
import scene_oldblock as ob  # noqa: E402
import rev3  # noqa: E402

K = 8
OX, OY = 30, 70
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F8, F11, F16 = (ImageFont.truetype(FONT, n) for n in (8, 11, 16))
COL = {"r": (112, 108, 100), "b": (214, 150, 96), "o": (118, 170, 98), "w": (96, 112, 150), "n": (240, 190, 70)}
W, H = ob.W, ob.H

CURRENT = [r for r in ob.LAYOUT if r[0] not in ("thicket",)]
# problem markers on the current map: (number, x, y, short text)
PROBLEMS = [
    (1, 50.0, 15.0, "pocket square hidden behind house 4"),
    (2, 40.0, 33.0, "pond park: benches on bare grass, nothing to do"),
    (3, 23.0, 15.5, "alleys / yard are gated dead ends"),
    (4, 46.0, 16.0, "north row: building - gap - building rhythm"),
    (5, 20.0, 34.0, "garden in the far corner, only a small gate"),
    (6, 52.0, 58.0, "Baker's Lane dead-ends at the map edge"),
    (7, 62.0, 55.0, "orchard + court = leftover east end"),
    (8, 36.0, 22.0, "street clutter: lamps, poles, lines"),
    (9, 7.0, 22.0, "cold works zone fills the whole entry"),
]


def draw_plan(d, layout, ox, oy, title, highlight_new=False):
    def P(x, y):
        return ox + x * K, oy + y * K
    d.rectangle([P(0, 0), P(W, H)], fill=(66, 64, 60))
    for (id_, label, x0, y0, x1, y1, kind) in layout:
        d.rectangle([P(x0, y0), P(x1, y1)], fill=COL[kind], outline=(20, 20, 24), width=2 if kind == "n" and highlight_new else 1)
    for x in range(0, W + 1, 10):
        d.line([P(x, 0), P(x, H)], fill=(90, 88, 84), width=1)
        d.text((P(x, 0)[0] - 5, oy - 12), str(x), font=F8, fill=(200, 200, 200))
    for y in range(0, H + 1, 10):
        d.line([P(0, y), P(W, y)], fill=(90, 88, 84), width=1)
        d.text((ox - 18, P(0, y)[1] - 4), str(y), font=F8, fill=(200, 200, 200))
    for (id_, label, x0, y0, x1, y1, kind) in layout:
        short = label.split(" (")[0].replace("MARKET SQUARE: covered hall, bandstand, stalls, chess, benches", "MARKET SQUARE")
        w = (x1 - x0) * K
        words = short.split()
        lines, cur = [], ""
        for wd in words:
            if len(cur + " " + wd) * 5 > max(w, 24) and cur:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        lines.append(cur)
        d.multiline_text((P(x0, y0)[0] + 2, P(x0, y0)[1] + 2), "\n".join(lines[:4]), font=F8, fill=(255, 255, 255), spacing=0)
    d.text((ox, oy - 38), title, font=F16, fill=(255, 255, 255))


def main(out):
    mw = OX + W * K + 40
    im = Image.new("RGB", (2 * mw + 40, OY + H * K + 230), (24, 26, 34))
    d = ImageDraw.Draw(im)
    draw_plan(d, CURRENT, OX, OY, "CURRENT (s81): Old Block 80 x 64 cells")
    for (n, x, y, t) in PROBLEMS:
        px, py = OX + x * K, OY + y * K
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(220, 40, 40), outline=(255, 255, 255), width=2)
        d.text((px - 3 - (3 if n > 9 else 0), py - 6), str(n), font=F11, fill=(255, 255, 255))
    draw_plan(d, rev3.LAYOUT3, OX + mw, OY, "REV 3 PROPOSAL (orange = new / changed)", True)
    # the loop (arrows): Cobble Street -> Mill Lane -> Orchard Row -> Baker's Lane -> Cobble Street
    pts = [(24, 22), (31.7, 22), (31.7, 57.5), (52.5, 57.5), (52.5, 22)]
    pp = [(OX + mw + x * K, OY + y * K) for (x, y) in pts]
    d.line(pp + [pp[0]], fill=(255, 255, 255), width=3)
    d.text((pp[2][0] - 70, pp[2][1] - 20), "LOOP (no dead ends)", font=F11, fill=(255, 255, 255))
    y0 = OY + H * K + 14
    d.text((OX, y0), "What feels off (red numbers)", font=F11, fill=(255, 220, 120))
    for i, (n, x, y, t) in enumerate(PROBLEMS):
        d.text((OX + (i // 5) * 380, y0 + 18 + (i % 5) * 14), "%d  %s" % (n, t), font=F8, fill=(235, 235, 235))
    d.text((OX + mw, y0), "Key moves", font=F11, fill=(255, 220, 120))
    moves = ["north row = continuous frontage: corner shop, laundromat, barber, bakery, cafe terrace, house, cinema, workshop",
             "market square (covered hall, bandstand, fountain, chess, stalls) replaces the pond park and gets the story props",
             "Mill Lane + Orchard Row close a loop with Baker's Lane (cottages along it), the garden gets a lane gate",
             "playground + basketball cage and allotments replace the leftover orchard / court",
             "street clutter cut: one lamp per frontage gap, no poles / lines over the street"]
    for i, t in enumerate(moves):
        d.text((OX + mw, y0 + 18 + i * 14), "- " + t, font=F8, fill=(235, 235, 235))
    im.save(out)
    # iso overview of the current map with the same markers
    import interact_audit as ia
    pals = ia.palettes()
    s = ob.old_block()
    base = ia.map_image(s, pals).convert("RGB")
    dd = ImageDraw.Draw(base)
    for (n, x, y, t) in PROBLEMS:
        px, py = s.origin_x + (x - y) * 16, s.origin_y + (x + y) * 8
        dd.ellipse([px - 14, py - 14, px + 14, py + 14], fill=(220, 40, 40), outline=(255, 255, 255), width=3)
        dd.text((px - 5, py - 9), str(n), font=F16, fill=(255, 255, 255))
    base.resize((base.width // 2, base.height // 2), Image.LANCZOS).save(out.replace(".png", "_current_iso.png"))


if __name__ == "__main__":
    main(sys.argv[1])
