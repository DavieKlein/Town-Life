#!/usr/bin/env python3
"""deposit.png: machine design + pickups + flow mock-ups on the park render (HUD from a real screenshot) + numbers."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ui_objects"))
import lib                      # noqa: E402
import pickups                  # noqa: E402
import ui_mock as ui            # noqa: E402
from PIL import Image, ImageDraw

G = os.path.abspath(os.path.join(HERE, "..", "..", "..", "graphics"))
PR = "/tmp/claude-0/s49/pr/"
OUT = "/tmp/claude-0/s49/deposit.png"
OX, OY = 976, 200            # city_centre origin: proj(x, y) = (976 + (x - y) * 16, 200 + (x + y) * 8)
CROP = (320, 456)            # image px of the top-left corner of the 240x128 play area in the mock-ups
DAY = ui.Style("A")


def proj(x, y):
    return OX + (x - y) * 16 - CROP[0], OY + (x + y) * 8 - CROP[1]


def sprite_sheet(name, fw, fh, index):
    im = Image.open(f"{G}/{name}.bmp")
    pal = im.getpalette()
    rgba = im.convert("RGBA")
    px = rgba.load()
    src = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if src[x, y] == 0:
                px[x, y] = (0, 0, 0, 0)
    return rgba.crop((0, index * fh, fw, (index + 1) * fh))


def base():
    bg = lib.compose(PR + "park_mach")                                  # 240x144
    play = bg.crop((CROP[0] - 320, CROP[1] - 440, CROP[0] - 320 + 240, CROP[1] - 440 + 128)).convert("RGBA")
    hud = Image.open("/tmp/claude-0/s48/sb_cue.png").convert("RGB").crop((0, 128, 240, 160))
    full = Image.new("RGB", (240, 160))
    full.paste(play.convert("RGB"), (0, 0))
    full.paste(hud, (0, 128))
    return full


def put_player(img, x, y, facing=0, pose=None, frame=0):
    px, py = proj(x, y)
    if pose == "search":
        spr = sprite_sheet("player_search", 64, 64, facing * 4 + frame)
        img.paste(spr, (int(px) - 32, int(py) - 54), spr)
    else:
        spr = sprite_sheet("player", 32, 64, facing * 9)
        img.paste(spr, (int(px) - 16, int(py) - 54), spr)


def put_pickup(img, x, y, kind, frame=0):
    px, py = proj(x, y)
    spr = pickups.frames()[kind][frame]
    img.paste(spr, (int(px) - 8, int(py) - 11), spr)


def cue(img, x, y):
    px, py = proj(x, y)
    ui.a_cue(ImageDraw.Draw(img), int(px), int(py) - 52, 1)


def toast(img, lines, y=4):
    d = ImageDraw.Draw(img)
    ui.draw_menu(img, DAY, None, None, 0, x=4, y=y, w=140, hint=False, info=lines)


def spots_scene():
    """The pickups lie near the bench and the hut (world coords, cells)."""
    return [("can_red", 5.4, 39.9), ("bottle_green", 1.4, 38.4), ("can_silver", 8.3, 37.0),
            ("bottle_brown", 11.9, 42.7), ("can_blue", 13.4, 39.9)]


def panel_world(stage):
    img = base()
    for kind, x, y in spots_scene():
        if stage >= 2 and (x, y) == (5.4, 39.9):
            continue
        put_pickup(img, x, y, kind, 1 if kind in ("can_red", "bottle_brown") else 0)
    if stage == 1:
        put_player(img, 6.4, 39.2, 1)
        cue(img, 6.4, 39.2)
    elif stage == 2:
        put_player(img, 6.2, 39.4, 1, "search", 2)
        toast(img, ["Picked up a can.", "Bag 5/10"], 5)
    elif stage == 3:
        put_player(img, 6.4, 38.0, 6)
        cue(img, 6.4, 38.0)
    return img


def panel_menu():
    img = panel_world(3)
    ui.draw_menu(img, DAY, "Return & Earn", ["Return all (7)", "Check credit", "Leave"], 0, y=5, w=116)
    return img


def panel_result():
    img = panel_world(3)
    ui.draw_menu(img, DAY, "Return & Earn", None, 0, y=5, w=140,
                 info=["4 cans, 3 bottles:", "$2.50 -> $2 paid,", "credit 2/4. Thanks!"])
    return img


def panel_full():
    img = panel_world(1)
    ui.draw_menu(img, DAY, "Bag full", None, 0, y=5, w=140, info=["You can't carry any", "more (10/10). Take it", "to the machine."])
    return img


def panel_pause():
    img = Image.open("/tmp/claude-0/s48/pause.png").convert("RGB")
    d = ImageDraw.Draw(img)
    # bag + credit under the money (free space right of "$20" in the title row)
    ui.text(d, 172, 20, "Bag 7/10", (50, 34, 30), ui.F9, shadow=(255, 250, 232))
    ui.text(d, 12, 117, "Bag: 4 cans, 3 bottles   Credit 2/4", (110, 90, 80), ui.F8)
    return img


def table_image(w=720):
    rows = [
        ("Can", "1 credit = $0.25"), ("Bottle", "2 credits = $0.50"), ("Credit", "4 credits = $1 paid at once, rest stays (0-3)"),
        ("Bag", "10 items (cans + bottles), perk later: 20"), ("Pickups", "26 spots, 10 active at once, top-up at 6:00"),
        ("Mix", "60 % can / 40 % bottle -> avg $0.35 per item"), ("Per day", "max 10 x $0.35 = $3.50 (about one day of cheap food)"),
        ("Cost", "per pick-up: Energy -0.5, Hygiene -1 (bush / hedge -2)"), ("Time", "~45 game minutes for a full sweep + return"),
    ]
    img = Image.new("RGB", (w, 28 + 22 * len(rows)), (28, 30, 38))
    d = ImageDraw.Draw(img)
    f = lib.ImageFont.truetype(lib.FONT, 13)
    d.text((6, 4), "Numbers (fit docs/story_chapter1.md section 4: food $4-6 per day, odd jobs ~$9/h, dishes $16/shift)", fill=(255, 220, 120),
           font=lib.ImageFont.truetype(lib.FONT, 12))
    for i, (a, b) in enumerate(rows):
        d.text((8, 28 + i * 22), a, fill=(150, 200, 255), font=f)
        d.text((110, 28 + i * 22), b, fill=(255, 255, 255), font=f)
    return img


def main():
    lab = lib.compose(PR + "lab")
    machine = lab.crop((70, 40, 215, 185))
    sheet = Image.open(PR + "pickups_sheet.png")
    spr = sheet.resize((sheet.width // 2, sheet.height // 2), Image.NEAREST)        # 4x
    TW = 1458
    top = Image.new("RGB", (TW, 470), (28, 30, 38))
    d = ImageDraw.Draw(top)
    f = lib.ImageFont.truetype(lib.FONT, 14)
    d.text((6, 4), "RETURN & EARN machine: own design, green steel, round rubber port, lit sign, 2 status lamps", fill=(255, 220, 120), font=f)
    top.paste(lib.zoom(machine, 3), (6, 28))
    X = 470
    d.text((X, 34), "Pickups lie on the ground (16x16 sprites, one", fill=(255, 255, 255), font=f)
    d.text((X, 54), "14-colour palette, 2-frame twinkle so they are findable):", fill=(255, 255, 255), font=f)
    top.paste(spr.convert("RGB"), (X, 80))
    d.text((X, 200), "can red / blue / silver, bottle green / brown / clear", fill=(180, 190, 220), font=f)
    for i, s_ in enumerate(["Placement: against the east wall of the park toilet,",
                            "front facing +x (screen down-right). The player stands",
                            "on the lawn side; reach 28 units like every fixture.",
                            "The park bench stays where it is (it is just south).",
                            "Lit sign + lamps keep the shaded +x face readable."]):
        d.text((X, 250 + i * 20), s_, fill=(255, 255, 255), font=f)
    panels = [
        (panel_world(0), "1  In the park: five finds lie around (sparkle twinkles)"),
        (panel_world(1), "2  Close enough: the gold A cue appears"),
        (panel_world(2), "3  A: bend-down (search pose, ~1.2 s), toast"),
        (panel_world(3), "4  At the machine: A cue"),
        (panel_menu(), "5  Menu (Paper UI by day, Night UI by night)"),
        (panel_result(), "6  Result: whole dollars paid, rest stays as credit"),
        (panel_full(), "7  Bag full: can't pick up more"),
        (panel_pause(), "8  Pause screen: Bag / Credit"),
    ]
    flow = lib.labelled(panels, n=3, cols=2, title="Interaction flow (mock-ups on in-game graphics, 3x)")
    tab = table_image(flow.width)
    out = Image.new("RGB", (flow.width, top.height + flow.height + tab.height), (28, 30, 38))
    out.paste(top, (0, 0))
    out.paste(flow, (0, top.height))
    out.paste(tab, (0, top.height + flow.height))
    out.save(OUT)
    print(out.size)


if __name__ == "__main__":
    main()
