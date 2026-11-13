"""Old Block REV 3 PROPOSAL scene (s82). NOT built into the game. Reuses the real helpers of tools/scene_oldblock.py (laundromat, bakery, arch,
cable works, row houses, garden, court, ...) and adds the new pieces of the proposal: shopfront(), market_hall(), bandstand(), cafe_terrace(),
cinema(), workshop(), playground(), allotments(). Scene ident "old_block" so the real renderer (tools/blender_render.py) can render it through
render.py without editing any game file.   Layout constants (LAYOUT3) feed layout_rev3.py (the labelled top-down plan)."""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TOOLS)
import scene as sc  # noqa: E402
import scene_oldblock as ob  # noqa: E402
from scene import (Scene, door_left, lamp_curved, trash_can, potted_plant, shrub, flower_bed, hedge, bench_along_x, fence_wood,  # noqa: E402
                   a_frame_sign, hydrant, newspaper_box)

W, H = ob.W, ob.H
FY = ob.FY
R = ob.R

NEW_MATERIALS = {
    "neon_marquee": dict(c="#ffd25a", rough=0.4),
}

# ---- layout of the proposal (cells): (id, label, x0, y0, x1, y1, kind)  kind: b building, o open, r road, w works, n NEW (highlighted)
LAYOUT3 = [
    ("avenue", "AVENUE STUB", 0, 18.5, 14.5, 25.5, "r"),
    ("works", "CABLE WORKS (barrier, trench, sewer manhole)", 2, 13.5, 14.5, 18.5, "w"),
    ("arch", "ARCH", 14.5, 18.5, 15.7, 25.5, "b"),
    ("street", "COBBLE STREET (main street)", 15.7, 19.5, 68.0, 24.5, "r"),
    ("h1", "Valdez house", 16.5, 9.0, 21.0, 18.0, "b"),
    ("corner", "Ruiz corner shop (NEW)", 21.0, 12.0, 25.5, 18.0, "n"),
    ("laundry", "INES' LAUNDROMAT", 25.5, 10.0, 34.0, 18.0, "b"),
    ("barber", "Figaro barber (NEW)", 34.0, 12.0, 38.5, 18.0, "n"),
    ("bakery", "BELLINI BAKERY", 38.5, 10.0, 45.0, 18.0, "b"),
    ("cafe", "Cafe Aurora + terrace (NEW)", 45.0, 12.0, 51.0, 18.0, "n"),
    ("h4", "Row house 4 + stoop", 51.0, 10.0, 56.0, 18.0, "b"),
    ("cinema", "THE ROXY cinema (NEW)", 56.0, 8.0, 65.0, 18.0, "n"),
    ("workshop", "Workshop (NEW)", 65.0, 12.0, 68.0, 18.0, "n"),
    ("square", "MARKET SQUARE: covered hall, bandstand, stalls, chess, benches (NEW focal point)", 31.0, 26.0, 49.0, 40.0, "n"),
    ("garden", "COMMUNITY GARDEN (opened up, gate on Mill Lane)", 13.0, 27.5, 28.0, 40.0, "o"),
    ("mill", "MILL LANE (NEW loop street)", 28.5, 24.5, 31.0, 58.0, "n"),
    ("lane", "BAKER'S LANE", 50.0, 24.5, 55.0, 58.0, "r"),
    ("orchard_row", "ORCHARD ROW (NEW, closes the loop)", 28.5, 56.0, 55.0, 60.0, "n"),
    ("cottages", "cottages (Lane Grocery stays)", 38.0, 40.0, 49.3, 56.0, "b"),
    ("cottages2", "3 cottages on Orchard Row (NEW)", 32.0, 50.0, 47.0, 56.0, "n"),
    ("playground", "PLAYGROUND + basketball cage (NEW)", 56.0, 28.5, 67.0, 47.0, "n"),
    ("allot", "ALLOTMENTS + sheds (was orchard)", 56.0, 48.0, 79.0, 62.0, "o"),
    ("meadow", "meadow / orchard (quiet)", 14.0, 41.0, 28.0, 62.0, "o"),
    ("site", "DEMOLITION SITE + Co-op Hall", 68.6, 4.0, 80.0, 34.0, "w"),
]


# --------------------------------------------------------------------------------------------------------------------------------------
# new helpers
# --------------------------------------------------------------------------------------------------------------------------------------
def shopfront(s, x0, x1, fy, floors, wall, name, awning=("awning_green", "awning_white"), sign="sign_cream", sign_text_mat="ink_black",
              door_x=None, seed=5, ground_h=3.2, door_mat="wood_dark", pole=False):
    """Generic 2-3 storey shop: big shop window with a lit interior, door, striped awning, sign band, upper windows with flower boxes."""
    rnd = R(seed)
    hgt = ob.house_body(s, x0, x1, fy, 8.0, floors, wall, ground_h=ground_h)
    dx = door_x if door_x is not None else x1 - 1.3
    gx0, gx1 = x0 + 0.4, dx - 0.9
    s.box(gx0 - 0.12, fy - 0.04, gx1 + 0.12, fy + 0.06, 0.45, 2.7, "trim_white")                       # window frame
    s.box(gx0, fy - 0.1, gx1, fy - 0.02, 0.6, 2.55, "shop_light")                                       # lit interior
    s.box(gx0, fy - 0.02, gx1, fy + 0.06, 0.45, 0.7, "wood_dark")                                       # stall riser
    door_left(s, dx - 0.55, dx + 0.55, fy, 2.3, mat=door_mat)
    s.box(dx - 0.5, fy + 0.5, dx + 0.5, fy + 0.95, 0.0, 0.03, "mat_red", layer="floor")
    k = 0
    xx = x0 + 0.1
    while xx < x1 - 0.1:                                                                                # striped awning
        s.wedge(xx, fy, min(xx + 0.5, x1 - 0.1), fy + 1.2, 3.0, 2.6, "y", awning[k % 2])
        xx += 0.5
        k += 1
    s.box(x0 + 0.5, fy - 0.05, x1 - 0.5, fy + 0.1, 3.15, 3.75, sign)
    s.text(name, (x0 + x1) / 2, fy + 0.11, 3.45, 0.32, sign_text_mat, face="left", bold=True)
    for f in range(1, floors):
        ob.storey_windows(s, x0, x1, fy, ground_h + (f - 1) * 2.8 - 0.5, rnd=rnd, boxes=True)
    ob.drainpipe(s, x1 - 0.12, fy, hgt)
    if pole:                                                                                            # barber pole beside the door
        px = dx + 0.95
        s.cyl(px, fy + 0.25, 0.9, 2.0, 0.09, "paint_white", verts=12)
        for z in (1.05, 1.35, 1.65):
            s.cyl(px, fy + 0.25, z, z + 0.12, 0.095, "red_paint", verts=12)
        s.cyl(px, fy + 0.25, 2.0, 2.08, 0.12, "metal_dark", verts=12)
        s.cyl(px, fy + 0.25, 0.85, 0.9, 0.12, "metal_dark", verts=12)
    return hgt


def market_hall(s, x0, y0, x1, y1):
    """Covered market hall: open on all sides (posts + king-post roof), stalls under it, string lights. Roof 2.9 m so it never hides the street."""
    z = 2.5
    for xx in (x0 + 0.3, (x0 + x1) / 2, x1 - 0.3):
        for yy in (y0 + 0.3, y1 - 0.3):
            s.cyl(xx, yy, 0, z, 0.1, "wood_dark", verts=8)
            s.set_solid(xx - 0.15, yy - 0.15, xx + 0.15, yy + 0.15)
    s.box(x0, y0, x1, y1, z, z + 0.15, "wood")                                                          # roof deck
    ym = (y0 + y1) / 2
    s.wedge(x0 - 0.3, ym, x1 + 0.3, y1 + 0.4, z + 1.1, z, "y", "tin_roof")
    s.wedge(x0 - 0.3, ym, x1 + 0.3, y0 - 0.4, z + 1.1, z, "y", "tin_roof")
    s.poly([(x1 + 0.3, y0 - 0.4, z), (x1 + 0.3, y1 + 0.4, z), (x1 + 0.3, ym, z + 1.1)], "wood")
    s.box(x0 - 0.1, y1 + 0.35, x1 + 0.1, y1 + 0.45, z - 0.1, z + 0.35, "sign_green")
    s.text("MARKET HALL", (x0 + x1) / 2, y1 + 0.46, z + 0.12, 0.3, "sign_cream", face="left", bold=True)
    # stalls under the roof: tables with crates of produce
    for k in range(3):
        sx = x0 + 1.0 + k * (x1 - x0 - 2.0) / 3
        s.box(sx, y0 + 1.0, sx + 1.6, y0 + 1.9, 0.0, 0.8, "wood")
        s.box(sx - 0.05, y0 + 0.95, sx + 1.65, y0 + 1.95, 0.8, 0.86, "cloth_red" if k % 2 == 0 else "cloth_green")
        for j in range(5):
            s.sphere(sx + 0.3 + j * 0.28, y0 + 1.45, 0.98, 0.13, ("tomato", "orange_fruit", "cabbage")[(j + k) % 3])
        s.set_solid(sx, y0 + 1.0, sx + 1.6, y0 + 1.9)
        s.occluder(sx, y0 + 1.0, sx + 1.6, y0 + 1.9, 1.0)
    s.occluder(x0, y0, x1, y1, z + 1.3)


def bandstand(s, x, y):
    """Low octagon-ish bandstand: stone plinth with steps, six slim posts and a shallow copper cone roof (2.7 m)."""
    s.cyl(x, y, 0, 0.45, 1.5, "stone", verts=12)
    s.cyl(x, y, 0.45, 0.5, 1.4, "plaza_stone", verts=12)
    for k in range(6):
        import math
        a = k * math.pi / 3
        s.cyl(x + 1.2 * math.cos(a), y + 1.2 * math.sin(a), 0.5, 2.5, 0.05, "metal_dark", verts=8)
    s.cyl(x, y, 2.5, 2.9, 1.6, "roof", verts=12, r2=0.25)
    s.sphere(x, y, 2.95, 0.12, "gold")
    s.set_solid(x - 1.4, y - 1.4, x + 1.4, y + 1.4)
    s.occluder(x - 1.6, y - 1.6, x + 1.6, y + 1.6, 3.0)


def cafe_terrace(s, x0, x1, fy):
    """Cafe Aurora: warm yellow shopfront with a wide window, a terrace of 4 round tables with parasols on a low timber deck in front."""
    shopfront(s, x0, x1, fy, 2, "plaster_ochre", "CAFE AURORA", awning=("awning_yellow", "awning_white"), sign="sign_green",
              sign_text_mat="sign_cream", door_x=x1 - 1.3, seed=21, door_mat="wood_green")
    s.box(x0 + 0.3, fy + 1.3, x1 - 0.3, fy + 4.2, 0.0, 0.08, "wood", layer="floor")                       # deck
    for (tx, ty) in ((x0 + 1.3, fy + 2.2), (x0 + 3.2, fy + 2.0), (x0 + 1.5, fy + 3.5), (x0 + 3.4, fy + 3.5)):
        s.cyl(tx, ty, 0.08, 0.76, 0.03, "metal_dark", verts=8)
        s.cyl(tx, ty, 0.76, 0.8, 0.38, "wood_dark", verts=14)
        s.cyl(tx - 0.65, ty, 0.08, 0.5, 0.02, "metal_dark", verts=6)
        s.cyl(tx - 0.65, ty, 0.5, 0.56, 0.18, "cloth_red", verts=10)
        s.cyl(tx + 0.65, ty, 0.08, 0.5, 0.02, "metal_dark", verts=6)
        s.cyl(tx + 0.65, ty, 0.5, 0.56, 0.18, "cloth_red", verts=10)
        s.set_solid(tx - 0.4, ty - 0.4, tx + 0.4, ty + 0.4)
    s.cyl(x0 + 4.6, fy + 2.0, 0, 1.9, 0.03, "metal_dark", verts=8)                                         # one parasol (low canopy, 2 m)
    s.cyl(x0 + 4.6, fy + 2.0, 1.9, 2.2, 0.9, "awning_red", verts=12, r2=0.1)


def cinema(s, x0, x1, fy):
    """THE ROXY: small neighbourhood cinema, cream facade with a red marquee over the entrance, a vertical blade sign, three poster cases."""
    hgt = ob.house_body(s, x0, x1, fy, 9.0, 3, "plaster_cream", ground_h=3.6)
    dx = (x0 + x1) / 2
    door_left(s, dx - 1.1, dx + 1.1, fy, 2.6, mat="wood_red")
    s.box(dx - 2.2, fy, dx + 2.2, fy + 1.9, 3.2, 3.5, "red_paint")                                        # marquee
    s.box(dx - 2.2, fy + 1.8, dx + 2.2, fy + 1.9, 2.7, 3.2, "neon_marquee")
    s.text("ROXY", dx, fy + 1.91, 2.95, 0.4, "red_paint", face="left", bold=True)
    for k in range(9):                                                                                    # bulbs
        s.sphere(dx - 2.0 + k * 0.5, fy + 1.92, 3.5, 0.06, "lamp_amber")
    for (cx) in (x0 + 0.6, x1 - 2.4, x1 - 1.4):                                                           # poster cases
        s.box(cx, fy - 0.02, cx + 0.8, fy + 0.08, 1.0, 2.1, "metal_dark")
        s.box(cx + 0.06, fy + 0.06, cx + 0.74, fy + 0.1, 1.08, 2.02, ("poster_blue", "poster_red", "poster_yellow")[int(cx) % 3])
    s.box(x1 - 0.5, fy + 0.1, x1 - 0.3, fy + 0.6, 3.6, 7.6, "neon_red")                                   # blade sign
    s.box(x1 - 0.55, fy + 0.1, x1 - 0.25, fy + 0.18, 3.6, 7.6, "metal_dark")
    ob.storey_windows(s, x0, x1, fy, 3.6 - 0.5, rnd=R(31), boxes=False)
    ob.drainpipe(s, x0 + 0.12, fy, hgt)
    s.box(dx - 1.4, fy + 0.5, dx + 1.4, fy + 1.6, 0.0, 0.03, "mat_red", layer="floor")


def workshop(s, x0, x1, fy):
    """Small brick workshop with a roller door, a hanging gear sign and crates."""
    hgt = ob.house_body(s, x0, x1, fy, 7.0, 1, "brick_red", ground_h=3.2)
    dx = (x0 + x1) / 2
    s.box(dx - 1.0, fy, dx + 1.0, fy + 0.08, 0.0, 2.4, "metal_grey")
    for k in range(10):
        s.box(dx - 1.0, fy + 0.07, dx + 1.0, fy + 0.1, 0.1 + k * 0.23, 0.13 + k * 0.23, "metal_dark")
    s.box(x0 + 0.2, fy - 0.05, x1 - 0.2, fy + 0.1, 2.7, 3.15, "sign_blue")
    s.text("WORKSHOP", dx, fy + 0.11, 2.9, 0.25, "sign_cream", face="left", bold=True)
    ob.crate_stack(s, x0 + 0.5, fy + 0.9, 2)


def playground(s, x0, y0, x1, y1, rnd):
    """Rubber-mat playground: swing frame, slide, spring rider, sandpit, low fence on the south / east, bench."""
    s.box(x0, y0, x1, y1, 0.0, 0.01, "court_green", layer="floor")
    s.box(x0 + 5.0, y0 + 4.0, x0 + 8.4, y0 + 7.2, 0.01, 0.06, "path_dirt", layer="floor")               # sandpit
    for (px, py) in ((x0 + 1.6, y0 + 1.5), (x0 + 1.6, y0 + 3.9)):                                          # swing frame
        s.cyl(px, py, 0, 2.3, 0.06, "metal_dark", verts=8)
    s.tube([(x0 + 1.6, y0 + 1.5, 2.3), (x0 + 1.6, y0 + 3.9, 2.3)], 0.05, "metal_dark")
    for sy in (y0 + 2.2, y0 + 3.2):
        s.tube([(x0 + 1.6, sy, 2.3), (x0 + 1.6, sy, 0.5)], 0.015, "metal_grey")
        s.box(x0 + 1.45, sy - 0.2, x0 + 1.75, sy + 0.2, 0.45, 0.5, "wood_red")
    s.set_solid(x0 + 1.3, y0 + 1.2, x0 + 1.9, y0 + 4.2)
    s.box(x0 + 4.0, y0 + 0.8, x0 + 4.8, y0 + 1.8, 0.0, 1.9, "metal_dark")                                  # slide tower + chute
    s.wedge(x0 + 4.8, y0 + 0.9, x0 + 7.0, y0 + 1.7, 1.8, 0.05, "x", "metal_light") if False else s.box(x0 + 4.8, y0 + 0.9, x0 + 6.6, y0 + 1.7, 0.2, 0.5, "metal_light")
    s.set_solid(x0 + 3.9, y0 + 0.7, x0 + 6.7, y0 + 1.9)
    s.cyl(x0 + 7.0, y0 + 9.0, 0.0, 0.4, 0.05, "metal_grey", verts=8)                                       # spring rider
    s.sphere(x0 + 7.0, y0 + 9.0, 0.55, 0.28, "cloth_yellow", sz=0.8, sx=1.4)
    chain_y = y1 + 0.3
    sc.chain_link(s, x0 - 0.3, x1 + 0.3, chain_y, h=1.1)
    bench_along_x(s, x0 + 2.0, x0 + 4.0, y0 + 6.5)
    trash_can(s, x0 + 0.6, y0 + 6.6)


def allotments(s, x0, y0, x1, y1, rnd):
    """Allotments: rows of low beds, little sheds in different colours, water butts, bean canes. (replaces the orchard block)"""
    cols = ["wood_green", "wood_blue", "wood_red", "wood"]
    for r_ in range(3):
        for c_ in range(5):
            bx, by = x0 + 1.5 + c_ * 4.2, y0 + 1.5 + r_ * 4.4
            s.box(bx, by, bx + 2.6, by + 2.4, 0.0, 0.3, "wood")
            s.box(bx + 0.1, by + 0.1, bx + 2.5, by + 2.3, 0.28, 0.33, "soil")
            for i in range(4):
                s.sphere(bx + 0.5 + 0.55 * i, by + 1.2, 0.5, 0.17, "cabbage" if (r_ + c_) % 2 else "leaves_light", sz=0.7)
            s.set_solid(bx, by, bx + 2.6, by + 2.4)
        sx, sy = x1 - 3.6, y0 + 1.2 + r_ * 4.4
        s.box(sx, sy, sx + 2.0, sy + 1.7, 0, 1.9, cols[r_ % 4])
        s.box(sx - 0.15, sy - 0.15, sx + 2.15, sy + 1.85, 1.9, 2.0, "tin_roof")
        s.set_solid(sx, sy, sx + 2.0, sy + 1.7)
        s.occluder(sx - 0.15, sy - 0.15, sx + 2.15, sy + 1.85, 2.1)


# --------------------------------------------------------------------------------------------------------------------------------------
# ground + scene
# --------------------------------------------------------------------------------------------------------------------------------------
def ground3(s, rnd):
    """Floor layer of the proposal. Distinct tops everywhere (grass 0.0, pavement 0.008, cobble 0.012, plaza 0.016): coplanar faces render black."""
    s.box(0, 6.0, 68.0, 62.0, -0.4, -0.04, "slab_flat", layer="floor")
    s.box(13.0, 26.2, W, H, -0.1, 0.0, "grass_flat", layer="floor")
    s.box(0, 34.5, 10.5, H, -0.1, 0.0, "grass_flat", layer="floor")
    # avenue stub + trench (as built)
    s.box(0, 18.5, 11.3, 25.5, -0.1, -0.02, "asphalt", layer="floor")
    s.box(13.3, 18.5, 14.5, 25.5, -0.1, -0.02, "asphalt", layer="floor")
    s.box(11.3, 18.5, 13.3, 25.5, -0.6, -0.55, "mud", layer="floor")
    s.set_solid(11.3, 18.5, 13.3, 25.5)
    s.box(0, 14.5, 15.7, 18.5, -0.1, 0.0, "paving_flat", layer="floor")
    s.box(0, 25.5, 16.0, 27.4, -0.1, 0.0, "paving_flat", layer="floor")
    # main street + pavements
    s.box(14.5, 19.5, 68.0, 24.5, -0.1, 0.012, "cobble", layer="floor")
    s.box(15.7, 19.5, 68.0, 19.62, -0.1, 0.05, "curb", layer="floor")
    s.box(15.7, 24.38, 68.0, 24.5, -0.1, 0.05, "curb", layer="floor")
    s.box(15.7, 18.0, 68.0, 19.5, -0.1, 0.008, "paving_flat", layer="floor")
    s.box(16.0, 24.5, 68.0, 26.2, -0.1, 0.008, "paving_flat", layer="floor")
    # Mill Lane (N-S, new), Baker's Lane (N-S), Orchard Row (E-W, new): the loop
    s.box(30.5, 26.2, 33.0, 58.0, -0.1, 0.012, "cobble", layer="floor")
    s.box(50.0, 26.2, 55.0, 58.0, -0.1, 0.012, "cobble", layer="floor")
    s.box(33.0, 55.5, 50.0, 59.5, -0.1, 0.012, "cobble", layer="floor")
    s.box(30.5, 55.5, 33.0, 59.5, -0.1, 0.012, "cobble", layer="floor")
    s.box(49.2, 26.2, 50.0, 55.5, -0.1, 0.008, "paving_flat", layer="floor")
    s.box(33.0, 59.5, 55.0, 60.3, -0.1, 0.008, "paving_flat", layer="floor")
    # market square
    s.box(33.5, 26.2, 49.0, 41.0, -0.1, 0.016, "plaza_stone", layer="floor")
    s.box(35.0, 31.0, 36.2, 41.0, 0.016, 0.02, "tiles_checker", layer="floor") if False else None
    s.box(55.8, 26.2, 68.0, 48.0, -0.1, 0.004, "slab_flat", layer="floor")


def old_block_rev3():
    oy = 175
    s = Scene("old_block", "Old Block", W, H, origin_x=H * 16 + 16, origin_y=oy, img_w=(W + H) * 16 + 32, img_h=oy + (W + H) * 8 + 16)
    rnd = R(1931)
    ground3(s, rnd)
    ob.hoarding_and_drums(s, rnd)
    ob.cable_works(s, rnd)
    ob.works_edge(s)
    ob.arch(s)
    # ---- north row: continuous, 9 frontages ----
    ob.row_house(s, 16.5, 21.0, FY, 3, "plaster_terra", 18.6, door_mat="wood_green", seed=11, shutters=True, extras=("stain",))
    ob.balcony(s, 17.2, 19.9, FY, 6.0)
    shopfront(s, 21.0, 25.5, FY, 2, "plaster_mint", "RUIZ CORNER SHOP", awning=("awning_red", "awning_white"), door_x=24.2, seed=41, door_mat="wood_red")
    newspaper_box(s, 22.0, 19.4, "sign_blue")
    ob.laundromat(s, 25.5, 34.0, FY)
    shopfront(s, 34.0, 38.5, FY, 2, "plaster_blue", "FIGARO", awning=("awning_red", "awning_white"), sign="sign_blue", sign_text_mat="sign_cream",
              door_x=37.2, seed=42, pole=True)
    ob.bakery(s, 38.5, 45.0, FY)
    cafe_terrace(s, 45.0, 51.0, FY)
    ob.row_house(s, 51.0, 56.0, FY, 3, "plaster_rose", 53.1, door_mat="wood_red", seed=12, extras=("dish", "stain"))
    cinema(s, 56.0, 65.0, FY)
    workshop(s, 65.0, 68.0, FY)
    # ---- street dressing: lamps on the pavement between doors, bunting, pots ----
    for x in (21.0, 34.2, 44.9, 55.8, 65.2):
        lamp_curved(s, x, 19.1, arm="y")
    ob.bunting(s, 25.5, 18.15, 4.3, 34.0, 18.15, 4.3, 9, rnd, sag=0.15)
    for (x, y) in ((17.6, 19.2), (23.0, 19.2), (39.0, 19.2), (53.6, 19.2)):
        potted_plant(s, x, y, "flowers")
    # ---- west of Mill Lane: the garden, opened up (gate on the street pavement) and a quiet meadow ----
    ob.garden(s, 13.0, 27.5, 30.0, 40.0, rnd)
    ob.meadow(s, 14.0, 41.0, 30.0, 62.0, rnd)
    # ---- market square ----
    market_hall(s, 36.0, 29.0, 46.0, 34.0)
    bandstand(s, 35.6, 38.0)
    ob.plane_tree(s, 47.6, 36.5, 1.0)
    ob.chess_table(s, 46.8, 31.0 + 4.0)
    s.cyl(41.0, 38.6, 0, 0.45, 1.0, "stone", verts=20)
    s.cyl(41.0, 38.6, 0.45, 0.5, 0.88, "pond_flat", verts=20)
    for (bx, by) in ((38.0, 40.2), (44.0, 40.2), (34.4, 32.0)):
        bench_along_x(s, bx, bx + 1.8, by)
    for (x, y) in ((34.0, 27.4), (48.5, 27.4), (48.5, 40.0)):
        trash_can(s, x, y) if (x, y) == (48.5, 27.4) else potted_plant(s, x, y, "bay")
    for y in (30.0, 44.0):
        lamp_curved(s, 49.6, y, arm="y")
    # ---- Baker's Lane (cottages west side incl. Lane Grocery), Orchard Row cottages, playground, allotments ----
    ob.cottage(s, 49.0, 41.0, colours="cream")
    ob.cottage(s, 49.0, 49.5, name="2Story_GableRoof_Mat", colours="blue")
    for (cx, col) in ((35.0, "orange"), (40.0, "mint"), (45.0, "cream")):
        s.model("1Story_GableRoof_Mat", cx, 55.4, front="left", colours=col, scale=2.1)
    playground(s, 57.0, 28.5, 67.0, 47.0, rnd)
    ob.court(s, 56.0, 28.5, 67.0, 37.5, rnd) if False else None
    allotments(s, 56.0, 48.0, 79.0, 62.0, rnd)
    ob.demolition_site(s, 68.0, 4.0, 80.0, 34.0, rnd)
    ob.hedge(s, 17.0, 49.0, 62.5, 0.9)
    s.sun_strength = 4.0
    return s
