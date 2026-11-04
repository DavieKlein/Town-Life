#!/usr/bin/env python3
"""Builds /tmp/claude-0/s52/room_proposal.png from final/*_q.png and out/mock_*.png"""
import sys
from PIL import Image, ImageDraw, ImageFont
S = "/tmp/claude-0/s52"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONTR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_t = ImageFont.truetype(FONT, 26); f_h = ImageFont.truetype(FONT, 18); f_b = ImageFont.truetype(FONTR, 14); f_bb = ImageFont.truetype(FONT, 14)
W = 1200; PAD = 16
BG = (28, 30, 38)
secs = []


def z(im, n):
    return im.resize((im.width * n, im.height * n), Image.NEAREST)


def ld(p):
    return Image.open(p).convert("RGB")


def block(title, lines, ims, labels, n, cols):
    """returns an image: heading, bullet text lines, grid of images"""
    h_text = 30 + len(lines) * 19 + 6
    ims = [z(i, n) for i in ims]
    cw = max(i.width for i in ims); ch = max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    h = h_text + rows * (ch + 24) + PAD
    out = Image.new("RGB", (W, h), BG)
    d = ImageDraw.Draw(out)
    d.text((PAD, 4), title, font=f_h, fill=(255, 214, 92))
    for i, l in enumerate(lines):
        d.text((PAD, 34 + i * 19), l, font=f_b, fill=(235, 235, 235))
    gx = (W - cols * cw - (cols - 1) * 12) // 2
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x = gx + (i % cols) * (cw + 12); y = h_text + (i // cols) * (ch + 24)
        d.text((x, y), lab, font=f_bb, fill=(160, 220, 255))
        out.paste(im, (x, y + 20))
    return out


mst, mgt = ld(f"{S}/final/market_st_q.png"), ld(f"{S}/final/market_gate_q.png")
ra, rb = ld(f"{S}/final/room_a_q.png"), ld(f"{S}/final/room_b_q.png")
mock = lambda n: ld(f"{S}/out/{n}.png")

head = Image.new("RGB", (W, 92), BG)
d = ImageDraw.Draw(head)
d.text((PAD, 8), "Town Life - the room above Corner Market (proposal, s52)", font=f_t, fill=(255, 255, 255))
d.text((PAD, 44), "Real renderer + real quantizer (sharp style C). Nothing is in the game yet - pick A or B (and the stairs/gate).", font=f_b, fill=(235, 235, 235))
d.text((PAD, 64), "Story: the room comes with the job. Stairs in the storeroom behind the checkout. Day 1 starts here, 7:00.", font=f_b, fill=(235, 235, 235))
secs.append(head)
secs.append(block("1  Storeroom with the stairs  (left: now, right: after the firing)", [
    "Stairs replace the staff table spot (table moved west). 14 steps, handrail, PRIVATE plaque; the player steps onto the",
    "foot of the stairs from the west = warp up. After Victor buys the store: white/grey VaultMart staff gate with a gold V,",
    "keycard reader (red LED) and the sign STAFF ONLY - VAULTMART. Foot is solid, no warp, A shows a locked message.",
], [mst, mgt], ["storeroom + stairs (open)", "storeroom + VaultTech gate (locked)"], 2, 2))
secs.append(block("2  The room upstairs - two variants (cutaway, 8x7 cells: 7x6 walkable)", [
    "Entry: stairwell with balustrade, you appear on the top step. Warm palette, string lights, patchwork quilt, Corner Market apron",
    "on a hook, backpack + red sneakers, photo frame, pinboard, plants, round/runner rug, street view with the VaultTech tower.",
], [ra, rb], ["A: attic - gable end, exposed beams, dormer-style window", "B: plain room - big window with window seat"], 2, 2))
secs.append(block("3  In-game mocks (240x160, real HUD strip + real player sprite)", [
    "Left: arriving at the top of the stairs.  Right: at the bed with the A cue and the proposed menu (paper style, daytime).",
    "The room is taller than the 128 px play area, so the camera scrolls vertically like in the market.",
], [mock("mock_a_arrive"), mock("mock_a_bed"), mock("mock_b_arrive"), mock("mock_b_bed")],
    ["A - arrive", "A - bed", "B - arrive", "B - bed"], 2, 2))
secs.append(block("4  Window view mocks", ["Look outside: info text (3 lines), different per story state."],
                  [mock("mock_a_window"), mock("mock_b_window")], ["A - window", "B - window"], 2, 2))
inter = Image.new("RGB", (W, 300), BG)
d = ImageDraw.Draw(inter)
d.text((PAD, 4), "5  Interactions in the room", font=f_h, fill=(255, 214, 92))
rows = [
    ("Bed (Sleep)", "Sleep: Energy +1.0 per game min (bench +0.5), clock 8x (bench 4x), hunger slows down like now, Fun +5 at wake-up;"),
    ("", "ends with 'Slept well.' + optional 'Save game?' dialog (bed = save point). Nap: 1 h, Energy +20. D-pad/B wakes you."),
    ("Wardrobe", "Info now: 'Work shirts, jeans... and a green apron.' Later: Change clothes (outfits bought/earned)."),
    ("Desk", "Read (Fun + like a bookshelf, quality 1) / Check notes = shows the current objective; later: write letters, plan."),
    ("Window", "Look outside - flavour text by story state: Day 1 'Mia is opening the shutters.'; after the firing: 'VaultTech's"),
    ("", "tower glows over the roofs. Everything below feels colder.' Night: lamps on the street, the VaultTech sign."),
    ("Bookshelf", "Read a book (Fun +, a few story hints). Apron/pinboard: info line about shifts and Old Block flyers."),
    ("Stairs", "Walk onto the top steps = fade to the storeroom (no menu). Before firing: free. After firing: gate below, so"),
    ("", "the room is cut off; the first night is on the bench (story). Later it may be reachable again (final chapter)."),
    ("Dev notes", "Maps room_attic / room_plain (+ market_stairs). 4 new interactable kinds: bed, wardrobe, desk, window (shelf exists)."),
]
y = 38
for k, v in rows:
    d.text((PAD, y), k, font=f_bb, fill=(160, 220, 255)); d.text((PAD + 130, y), v, font=f_b, fill=(235, 235, 235)); y += 24
secs.append(inter)
H = sum(s.height for s in secs) + 12 * len(secs)
out = Image.new("RGB", (W, H), BG)
y = 0
for s_ in secs:
    out.paste(s_, (0, y)); y += s_.height + 12
out.save(f"{S}/room_proposal.png")
print(out.size)
