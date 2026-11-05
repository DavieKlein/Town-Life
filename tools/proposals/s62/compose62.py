#!/usr/bin/env python3
"""s62: phone-viewable sheets.  python3 compose62.py   -> /tmp/claude-0/s62/vaultmart.png, car.png, individual/*.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
O = "/tmp/claude-0/s62"
os.makedirs(f"{O}/individual", exist_ok=True)
F = lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", n)
FR = lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", n)
DARK = (24, 28, 56); GOLD = (248, 208, 96); WHITE = (240, 240, 248); GREY = (170, 178, 210)


def up(im, z):
    return im.resize((im.width * z, im.height * z), Image.NEAREST)


def sheet(title, blocks, W=1240, sub=None):
    """blocks: list of ('img', PIL, caption) | ('row', [(PIL, caption)...]) | ('text', [lines])"""
    y = 70 + (30 if sub else 0)
    parts = []
    for b in blocks:
        if b[0] == "img":
            parts.append((y, b)); y += b[1].height + 70
        elif b[0] == "row":
            h = max(i.height for i, _ in b[1]); parts.append((y, b)); y += h + 70
        else:
            parts.append((y, b)); y += 28 * len(b[1]) + 30
    im = Image.new("RGB", (W, y + 10), DARK)
    d = ImageDraw.Draw(im)
    d.text((20, 14), title, font=F(30), fill=GOLD)
    if sub:
        d.text((20, 52), sub, font=FR(18), fill=GREY)
    for yy, b in parts:
        if b[0] == "img":
            d.text((20, yy), b[2], font=F(20), fill=WHITE)
            im.paste(b[1], ((W - b[1].width) // 2, yy + 34))
        elif b[0] == "row":
            n = len(b[1]); gap = 20
            tw = sum(i.width for i, _ in b[1]) + gap * (n - 1)
            x = (W - tw) // 2
            for i, c in b[1]:
                d.text((x, yy), c, font=F(18), fill=WHITE)
                im.paste(i, (x, yy + 32)); x += i.width + gap
        else:
            for k, ln in enumerate(b[1]):
                d.text((20, yy + 28 * k), ln, font=FR(15), fill=WHITE if not ln.startswith("#") else GOLD)
    return im


def save_ind(im, name):
    im.save(f"{O}/individual/{name}.png")


if sys.argv[1:] == ["vm"] or len(sys.argv) == 1:
    cm = Image.open(f"{O}/out/cm_q.png").convert("RGB")
    va = Image.open(f"{O}/out/vma_q.png").convert("RGB")
    vb = Image.open(f"{O}/out/vmb_q.png").convert("RGB")
    for n, im in (("corner_market", cm), ("vaultmart_A", va), ("vaultmart_B", vb)):
        save_ind(up(im, 3), f"{n}_3x")
    mocks = {}
    for v in "ab":
        for k in ("door", "kiosk"):
            m = Image.open(f"{O}/mock/mock_{v}_{k}.png"); mocks[(v, k)] = m
            save_ind(up(m, 3), f"mock_{v.upper()}_{k}_3x")
    blocks = [
        ("row", [(cm, "BEFORE: Corner Market (warm, day 1 morning)"), (vb, "AFTER: VaultMart, variant B (same layout)")]),
        ("text", ["# Same L-shaped room, same storeroom, stairs and shutter gate; every warm item swapped for its cold twin.",
                  "Wood -> white metal, bunting/plants/chalk -> screens + navy signs, checkout -> 3 self-checkouts, crates -> bins."]),
        ("img", up(va, 2), "VARIANT A: everything replaced (regimented shelf rows, kiosk bank at the door, robot-arm restock)"),
        ("img", up(vb, 2), "VARIANT B: same layout as the Corner Market (the player recognises the old store)"),
        ("row", [(up(mocks[("a", "door")], 2), "A: coming in (security gate, Valet)"), (up(mocks[("a", "kiosk")], 2), "A: at the kiosks")]),
        ("row", [(up(mocks[("b", "door")], 2), "B: coming in (security gate, Valet)"), (up(mocks[("b", "kiosk")], 2), "B: at the kiosks")]),
        ("text", ["# Cold kit (all inside the real renderer + quantizer, 64 spp preview here, 192 spp in the build):",
                  "glossy white floor tiles, LED trays on the walls, a fluorescent bar on every shelf,",
                  "white steel gondolas with IDENTICAL white boxes + cyan band, digital price rails,",
                  "3 self-checkout kiosks, security gate pillars with cyan beams + dome camera,",
                  "gold robot arm restocking a shelf, gold V logos, navy VAULTMART / SMART SHOPPING board,",
                  "red STAFF ONLY roll-down shutter (approved gate B) at the stairs."]),
    ]
    im = sheet("VaultMart: the Corner Market after Victor Vault's takeover", blocks,
               sub="Proposal s62. Real renderer + quantizer previews, 1 px = 1 GBA px (2x/3x enlarged). Nothing is in the repo.")
    im.save(f"{O}/vaultmart.png"); print("vaultmart.png", im.size)

if sys.argv[1:] == ["car"] or len(sys.argv) == 1:
    import json
    cd = f"{O}/car"; c75 = f"{O}/car75"
    se, nw = (Image.open(f"{cd}/car_{n}_q.png").convert("RGBA") for n in ("se", "nw"))
    sw, ne = ImageOps.mirror(se), ImageOps.mirror(nw)
    pl = Image.open("/tmp/claude-0/s52/out/player_rgba.png").crop((0, 0, 32, 64))
    BG = (112, 118, 130, 255)

    def tile(img, bbox=None):
        a = Image.new("RGBA", img.size, BG); a.alpha_composite(img); return a.crop(bbox or (10, 10, 182, 110))
    grid = Image.new("RGB", (172 * 2 + 10, 100 * 2 + 10), (24, 28, 56))
    for i, im in enumerate((se, nw, sw, ne)):
        grid.paste(tile(im).convert("RGB"), ((i % 2) * 182, (i // 2) * 110))
    save_ind(up(grid, 3), "car_4_facings_3x")
    # size comparison with the player (46 px) at 1x -> 3x
    cmp = Image.new("RGBA", (360, 120), BG)
    cmp.alpha_composite(se, (-10, 10)); cmp.alpha_composite(Image.open(f"{c75}/car_se_q.png").convert("RGBA"), (150, 10))
    cmp.alpha_composite(pl, (322, 46 + 0 - 12 - 0)) if False else None
    cmp.alpha_composite(pl.convert("RGBA"), (170, 52)) if False else None
    for i in range(4):
        m = Image.open(f"{O}/mock/mock_drive{i}.png"); save_ind(up(m, 3), f"car_drive_{i}_3x")
    park = Image.open(f"{O}/mock/mock_park.png"); save_ind(up(park, 3), "car_parked_3x")
    leave = Image.open(f"{O}/mock/mock_leave.png"); save_ind(up(leave, 3), "car_leaving_3x")
    for n, im in (("se", se), ("nw", nw)):
        save_ind(up(tile(im).convert("RGB"), 4), f"car_{n}_4x")
    seq = [(up(Image.open(f"{O}/mock/mock_drive{i}.png").crop((0, 0, 240, 128)), 2), f"frame {i + 1}/4") for i in range(4)]
    szimg = Image.open(f"{O}/car_size.png").convert("RGB") if os.path.exists(f"{O}/car_size.png") else None
    blocks = [
        ("img", up(grid, 3), "The golden limo, 4 facings (SW and NE are exact mirrors of SE and NW: only 2 images in ROM)"),
        ("img", up(park, 4), "Parked at the Corner Market kerb: Victor + Valet on the pavement, player watching (240x160 view, 4x)"),
        ("row", seq[:2]), ("row", seq[2:]),
        ("img", up(leave, 3), "After the scene it glides off to the east (SE facing, front visible)"),
    ]
    if szimg:
        blocks.append(("img", szimg, "Sprite sizes and VRAM cost"))
    txt = json.load(open(f"{O}/car_costs.json")) if os.path.exists(f"{O}/car_costs.json") else []
    if txt:
        blocks.append(("text", txt))
    im = sheet("Victor Vault's golden car", blocks, sub="Proposal s62. Own design: 5.6 m gold limousine, black vinyl roof, tinted glass, chrome, 'VV' plates, gold hubs.")
    im.save(f"{O}/car.png"); print("car.png", im.size)
