"""s74 PROPOSAL: Old Block (district 1, east of the City Centre). Scene code only - NOT in scene.SCENES of the game.

Imports the real scene helpers (tools/scene.py) and adds new ones. Layout constants (LAYOUT) are shared with plan.py so the
top-down plan PNG and the 3D scene never drift apart. Everything is in map cells (1 cell = 0.75 m), z in metres.

Map "old_block": 60 x 48 cells.  x grows to the east (down-right on screen), y to the south (down-left).
Camera sees faces that look towards +y and +x, so every shopfront stands on the NORTH side of a street (facade towards +y)
and everything on the SOUTH side of the main street is low or open (garden, court, chess plaza), otherwise it would hide the street.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import scene as sc  # noqa: E402
from scene import (Scene, CELL_M, window_left, window_right, door_left, flat_roof, lamp_curved, newspaper_box,  # noqa: E402
                   trash_can, hydrant, cone, potted_plant, flower_box, shrub, flower_bed, hedge, a_frame_sign, conifer,
                   bench_along_x, fence_wood, chain_link, poster, weeds, ivy, vault_v_logo, FLOWERS, planter)

W, H = 80, 64
M = 1 / CELL_M

# ---- shared layout (cells). plan.py draws these boxes with labels. kind: 'b' building, 'o' open area, 'w' works/cold, 'r' road ----
FY = 18.0                       # facade line of the north row (facing +y)
STREET = (19.5, 24.5)           # cobble street y range (Cobble Street)
ROAD_A = (18.5, 25.5)           # avenue stub outside the arch (matches the City Centre avenue width of 8: y 22..30 there)
LAYOUT = [
    # (id, label, x0, y0, x1, y1, kind)
    ("avenue", "AVENUE STUB (from City Centre)", 0, 18.5, 14.5, 25.5, "r"),
    ("hoard", "VaultTech hoarding + drums", 2, 13.5, 14.5, 18.5, "w"),
    ("barrier", "BARRIERS", 10.2, 14.5, 10.8, 34.5, "w"),
    ("trench", "TRENCH", 11.3, 18.5, 13.3, 25.5, "w"),
    ("arch", "ARCH", 14.5, 18.5, 15.7, 25.5, "b"),
    ("thicket", "BUSH THICKET (sneak lane)", 10.8, 27.5, 18.2, 34.5, "o"),
    ("street", "COBBLE STREET", 15.7, 19.5, 68.0, 24.5, "r"),
    ("lane", "BAKER'S LANE (N-S)", 50.0, 24.5, 55.0, 62.0, "r"),
    ("h1", "Valdez house", 16.5, 9.0, 21.0, 18.0, "b"),
    ("alley", "alley + Teo's den", 21.0, 6.0, 25.5, 18.0, "o"),
    ("laundry", "INES' LAUNDROMAT", 25.5, 10.0, 34.0, 18.0, "b"),
    ("yard", "yard + back room", 34.0, 6.0, 40.5, 18.0, "o"),
    ("backroom", "BACK ROOM (future home)", 34.4, 9.5, 37.4, 14.5, "b"),
    ("bakery", "BELLINI BAKERY (+ Okafor's flat)", 40.5, 10.0, 47.0, 18.0, "b"),
    ("square", "FOUNTAIN SQUARE (market)", 47.0, 12.0, 53.0, 18.0, "o"),
    ("h4", "Row house 4", 53.0, 10.0, 57.5, 18.0, "b"),
    ("h5", "House 5", 61.0, 10.0, 65.5, 18.0, "b"),
    ("stall", "ROSA'S STALL", 59.5, 20.5, 65.0, 24.0, "o"),
    ("garden", "COMMUNITY GARDEN", 17.0, 27.0, 29.0, 40.0, "o"),
    ("chess", "CHESS PLAZA", 29.5, 26.5, 35.0, 32.0, "o"),
    ("pond", "POND PARK", 36.0, 28.0, 47.0, 37.0, "o"),
    ("cottages", "COTTAGES (west of lane)", 38.0, 40.0, 49.3, 62.0, "b"),
    ("court", "COURT", 56.0, 28.5, 67.0, 37.5, "o"),
    ("orchard", "ORCHARD + allotments", 56.0, 40.0, 79.0, 62.0, "o"),
    ("meadow", "MEADOW + paths", 17.0, 41.0, 37.0, 62.0, "o"),
    ("fence", "SITE FENCE", 68.0, 4.0, 68.6, 34.0, "w"),
    ("site", "DEMOLITION SITE + Co-op Hall", 68.6, 4.0, 80.0, 34.0, "w"),
]


# ------------------------------------------------------------------------------------------------------------------
# New materials (registered into blender_render.MATERIALS by render.py; names are new, nothing existing is overwritten)
# ------------------------------------------------------------------------------------------------------------------
NEW_MATERIALS = {
    "plaster_ochre": dict(kind="noise", c="#dba85c", c2="#cd9a50", scale=6),
    "plaster_rose": dict(kind="noise", c="#dd9486", c2="#cf8678", scale=6),
    "plaster_teal": dict(kind="noise", c="#6aaaa2", c2="#5e9c94", scale=6),
    "plaster_blue": dict(kind="noise", c="#7f9fc6", c2="#7090b8", scale=6),
    "plaster_terra": dict(kind="noise", c="#c8744c", c2="#b8683f", scale=6),
    "plaster_stain": dict(c="#8c7a60", rough=0.95),
    "cobble": dict(kind="paving_grit", c="#8a8374", c2="#7e786b", mortar="#5c574e", bw=0.5, bh=0.4, mortar_size=0.02, crack_scale=0.5),
    "asphalt_patch": dict(kind="asphalt_grit", rough=0.95),
    "vault_hoard": dict(c="#2d3a4e", rough=0.5),
    "vault_cold": dict(kind="noise", c="#8d98a6", c2="#7d8896", scale=9),
    "cloth_red": dict(c="#c8403c", rough=0.95),
    "cloth_blue": dict(c="#3f6fb8", rough=0.95),
    "cloth_white": dict(c="#f1ede0", rough=0.95),
    "cloth_yellow": dict(c="#eec23c", rough=0.95),
    "cloth_green": dict(c="#4c9a5a", rough=0.95),
    "cloth_pink": dict(c="#e585ab", rough=0.95),
    "awning_red": dict(c="#c43a30", rough=0.8),
    "awning_yellow": dict(c="#e8b83a", rough=0.8),
    "awning_sun": dict(c="#e29a52", rough=0.85),
    "court_green": dict(kind="noise", c="#3f8a58", c2="#377e50", scale=10),
    "court_rust": dict(kind="noise", c="#b4583c", c2="#a64e34", scale=10),
    "yellow_machine": dict(c="#eab21c", rough=0.45, metal=0.3),
    "rubber_track": dict(c="#202228", rough=0.9),
    "mud": dict(kind="noise", c="#4e3a28", c2="#3e2e20", scale=14),
    "rubble": dict(kind="noise", c="#9a948a", c2="#8e887e", scale=8),
    "boards": dict(kind="noise", c="#7a6448", c2="#5e4c36", scale=16),
    "bush_dark": dict(kind="noise", c="#24502c", c2="#386a34", scale=5, rough=0.95),
    "sunflower": dict(c="#f2c418", rough=0.6),
    "tomato": dict(c="#d8352a", rough=0.4),
    "cabbage": dict(kind="noise", c="#8cc07a", c2="#6aa860", scale=40),
    "barrel_blue": dict(c="#2e5e92", rough=0.4),
    "tin_roof": dict(kind="brick", c="#8e969e", c2="#7e868e", mortar="#5c6268", bw=0.25, bh=2.0, mortar_size=0.015, rough=0.5),
    "bread_crust": dict(c="#c0803a", rough=0.7),
    "washer_white": dict(c="#e8ecef", rough=0.35),
    "washer_dial": dict(c="#35506e", rough=0.2),
    "skin_guard": dict(c="#d9a47e", rough=0.8),
    "sign_cream": dict(c="#f1e6c4", rough=0.7),
    "ink_black": dict(c="#1a1a1e", rough=0.6),
    "notice_orange": dict(c="#f08a20", rough=0.6),
    "lamp_amber": dict(c="#ffb23a", emit=2.2, emit_c="#ffb23a"),
    "wire_dark": dict(c="#24262c", rough=0.7),
    "pond_flat": dict(c="#3f7f8c", rough=0.08),
    # tile-budget materials: low-contrast / large-scale versions so that big areas de-duplicate into few tiles
    "grass_flat": dict(kind="noise", c="#559f3e", c2="#5aa443", scale=4, rough=0.95),
    "slab_flat": dict(kind="noise", c="#aaa499", c2="#a39d92", scale=4),
    "paving_flat": dict(kind="paving_grit", c="#a8604a", c2="#9c5844", mortar="#6a5448", bw=0.5, bh=0.25, mortar_size=0.01, crack_scale=0.3),
    "brick_flat": dict(c="#86583e", rough=0.85),
    "mesh_flat": dict(c="#50525a", rough=0.6),
    "brick_big": dict(kind="brick", c="#8a5a40", c2="#7e5239", mortar="#a89480", bw=0.6, bh=0.3),
}


def R(*a):
    return random.Random(*a)


# ------------------------------------------------------------------------------------------------------------------
# Generic helpers
# ------------------------------------------------------------------------------------------------------------------
def storey_windows(s, x0, x1, fy, z_base, wall_trim="trim_white", skip=(), rnd=None, boxes=True, shutters=False, bay=2.1):
    """Row of windows on a +y facing wall, 1 per `bay` cells. skip = set of bay indexes without a window."""
    rnd = rnd or R(int(x0 * 7 + z_base))
    n = max(1, int((x1 - x0) / bay))
    pad = ((x1 - x0) - n * bay) / 2
    for i in range(n):
        if i in skip:
            continue
        wx0 = x0 + pad + i * bay + 0.3
        wx1 = wx0 + bay - 0.6
        window_left(s, wx0, wx1, fy - 0.02, z_base + 0.75, z_base + 2.25, frame=wall_trim)
        if boxes and rnd.random() < 0.55:
            flower_box(s, wx0 - 0.05, wx1 + 0.05, fy - 0.02, z_base + 0.72, rnd)
        if shutters and rnd.random() < 0.6:
            col = rnd.choice(["wood_green", "wood_blue", "wood_red"])
            s.box(wx0 - 0.28, fy - 0.03, wx0 - 0.04, fy + 0.04, z_base + 0.75, z_base + 2.25, col)
            s.box(wx1 + 0.04, fy - 0.03, wx1 + 0.28, fy + 0.04, z_base + 0.75, z_base + 2.25, col)


def stoop(s, xm, fy, w=1.5):
    """Three stone steps up to a door + iron rail on one side."""
    for k in range(3):
        s.box(xm - w / 2 - 0.1 * k, fy, xm + w / 2 + 0.1 * k, fy + 0.45 - 0.14 * k, 0, 0.14 * (3 - k) + 0.02, "stone")
    s.box(xm + w / 2 + 0.25, fy + 0.02, xm + w / 2 + 0.31, fy + 0.45, 0.3, 1.0, "metal_dark")
    s.box(xm + w / 2 + 0.25, fy + 0.02, xm + w / 2 + 0.31, fy + 0.07, 0.9, 1.0, "metal_dark")


def drainpipe(s, x, fy, h):
    s.cyl(x, fy + 0.07, 0.0, h, 0.05, "metal_dark", verts=8)


def ac_unit(s, x, fy, z):
    s.box(x, fy + 0.02, x + 0.7, fy + 0.4, z, z + 0.45, "washer_white")
    s.box(x + 0.08, fy + 0.4, x + 0.62, fy + 0.43, z + 0.08, z + 0.37, "metal_dark")


def dish(s, x, y, z):
    s.cyl(x, y, z, z + 0.05, 0.28, "washer_white", axis="y", r2=0.28)
    s.cyl(x, y, z - 0.3, z, 0.03, "metal_dark", verts=6)


def house_body(s, x0, x1, fy, depth, floors, wall, trim_cornice=True, roof="flat", rnd=None, ground_h=3.0, floor_h=2.8):
    """Plain terraced house shell. Returns total wall height."""
    y0 = fy - depth
    hgt = ground_h + (floors - 1) * floor_h
    s.box(x0, y0, x1, fy, 0, hgt, wall)
    s.box(x0, fy - 0.04, x1, fy + 0.02, 0, 0.5, "stone")                      # plinth
    if trim_cornice:
        s.box(x0 - 0.05, fy - 0.1, x1 + 0.05, fy + 0.12, hgt - 0.22, hgt, "stone")
    if roof == "flat":
        flat_roof(s, x0, y0, x1, fy, hgt, rim="stone")
    else:
        ridge_y = (y0 + fy) / 2
        rz = hgt + 1.6
        s.wedge(x0 - 0.1, ridge_y, x1 + 0.1, fy + 0.4, rz, hgt - 0.1, "y", roof)
        s.wedge(x0 - 0.1, ridge_y, x1 + 0.1, y0 - 0.4, rz, hgt - 0.1, "y", roof)
        s.poly([(x1, y0, hgt), (x1, fy, hgt), (x1, ridge_y, rz)], wall)
        s.poly([(x0, y0, hgt), (x0, ridge_y, rz), (x0, fy, hgt)], wall)
    s.set_solid(x0, y0, x1 - 0.001, fy - 0.001)
    s.occluder(x0, y0, x1, fy, hgt + (1.8 if roof != "flat" else 0.5))
    return hgt


def row_house(s, x0, x1, fy, floors, wall, door_x, door_mat="wood_blue", depth=8.0, roof="flat", seed=1, shutters=False,
              extras=()):
    rnd = R(seed)
    hgt = house_body(s, x0, x1, fy, depth, floors, wall, roof=roof, rnd=rnd)
    door_left(s, door_x - 0.6, door_x + 0.6, fy, 2.3, mat=door_mat)
    stoop(s, door_x, fy + 0.04)
    s.box(door_x + 0.8, fy - 0.01, door_x + 1.05, fy + 0.02, 1.4, 1.65, "brass")        # house number plate
    # ground floor windows either side of the door
    for (a, b) in ((x0 + 0.4, door_x - 1.1), (door_x + 1.1, x1 - 0.4)):
        if b - a > 1.2:
            window_left(s, a, b, fy - 0.02, 0.9, 2.3)
            if rnd.random() < 0.5:
                flower_box(s, a - 0.05, b + 0.05, fy - 0.02, 0.88, rnd)
    for f in range(1, floors):
        storey_windows(s, x0, x1, fy, 3.0 + (f - 1) * 2.8 - 0.5, rnd=rnd, shutters=shutters)
    if "ac" in extras:
        ac_unit(s, x1 - 1.4, fy, 3.2)
    if "dish" in extras:
        dish(s, x0 + 1.2, fy + 0.35, hgt - 0.9)
    if "stain" in extras:                                                                     # damp streaks under the cornice
        for k in range(3):
            xx = x0 + 0.6 + rnd.random() * (x1 - x0 - 1.2)
            s.box(xx, fy - 0.0, xx + 0.12, fy + 0.012, hgt - 2.2, hgt - 0.25, "plaster_stain")
    drainpipe(s, x1 - 0.12, fy, hgt)
    return hgt


def balcony(s, x0, x1, fy, z, mat="metal_dark", plants=True):
    s.box(x0, fy, x1, fy + 0.7, z - 0.12, z, "stone")
    s.box(x0, fy + 0.66, x1, fy + 0.7, z, z + 0.9, mat)                                        # solid-ish rail (bars drawn as posts)
    s.box(x0, fy, x0 + 0.05, fy + 0.7, z, z + 0.9, mat)
    s.box(x1 - 0.05, fy, x1, fy + 0.7, z, z + 0.9, mat)
    if plants:
        rnd = R(int(x0 * 10))
        for k in range(3):
            potted_plant(s, x0 + 0.4 + k * (x1 - x0 - 0.8) / 2, fy + 0.35, "bush") if False else None
            s.sphere(x0 + 0.3 + rnd.random() * (x1 - x0 - 0.6), fy + 0.4, z + 0.2, 0.16, "leaves_light")


def cloth_line(s, x0, y0, z0, x1, y1, z1, n, rnd, sag=0.22, cols=None):
    """Washing line between two points with hanging cloths (flat polys). Cloths are in the vertical plane of the line."""
    cols = cols or ["cloth_red", "cloth_blue", "cloth_white", "cloth_yellow", "cloth_green", "cloth_pink"]
    pts = []
    for i in range(7):
        t = i / 6
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t - sag * 4 * t * (1 - t)))
    s.tube(pts, 0.012, "wire_dark")
    for i in range(n):
        t = (i + 0.5) / n
        px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        pz = z0 + (z1 - z0) * t - sag * 4 * t * (1 - t)
        w = rnd.uniform(0.18, 0.34)
        h = rnd.uniform(0.35, 0.6)
        dx, dy = (x1 - x0), (y1 - y0)
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L * w / 2, dy / L * w / 2
        s.poly([(px - ux, py - uy, pz), (px + ux, py + uy, pz), (px + ux, py + uy, pz - h), (px - ux, py - uy, pz - h)],
               rnd.choice(cols))


def bunting(s, x0, y0, z0, x1, y1, z1, n, rnd, sag=0.35):
    cols = ["cloth_red", "cloth_yellow", "cloth_blue", "cloth_green", "cloth_white", "cloth_pink"]
    pts = []
    for i in range(9):
        t = i / 8
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t - sag * 4 * t * (1 - t)))
    s.tube(pts, 0.01, "wire_dark")
    for i in range(n):
        t = (i + 0.5) / n
        px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        pz = z0 + (z1 - z0) * t - sag * 4 * t * (1 - t)
        dx, dy = (x1 - x0), (y1 - y0)
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L * 0.1, dy / L * 0.1
        s.poly([(px - ux, py - uy, pz), (px + ux, py + uy, pz), (px, py, pz - 0.28)], cols[i % len(cols)])


def pole(s, x, y, h=4.4, solid=True):
    s.cyl(x, y, 0, h, 0.06, "wood_dark", verts=8)
    s.cyl(x, y, 0, 0.3, 0.1, "concrete", verts=8)
    if solid:
        s.set_solid(x - 0.15, y - 0.15, x + 0.15, y + 0.15)
        s.occluder(x - 0.3, y - 0.3, x + 0.3, y + 0.3, h)


def crate_stack(s, x, y, n=2, rot=0.0):
    for k in range(n):
        s.box(x, y, x + 0.7, y + 0.5, 0.3 * k, 0.3 * (k + 1), "crate")
    s.set_solid(x, y, x + 0.7, y + 0.5)
    s.occluder(x, y, x + 0.7, y + 0.5, 0.3 * n + 0.05)


def chain_link_y(s, x, y0, y1, h=2.0, solid=True):
    """Chain-link fence along y (N-S) at plane x."""
    s.box(x - 0.02, y0, x + 0.02, y1, 0.05, h, "mesh_flat")
    s.box(x - 0.04, y0, x + 0.04, y1, h - 0.04, h, "metal_grey")
    yy = y0
    while yy <= y1 + 0.01:
        s.cyl(x, yy, 0, h + 0.05, 0.04, "metal_grey", verts=8)
        yy += 2.5
    if solid:
        s.set_solid(x - 0.2, y0, x + 0.2, y1 - 0.001)
        s.occluder(x - 0.3, y0, x + 0.3, y1, h + 0.1)


def bush_ball(s, x, y, r, rnd, h=None):
    """Dense overgrown bush made of several spheres."""
    h = h or r * 1.6
    mats = ["bush_dark", "leaves", "leaves_light"]
    for _ in range(5):
        s.sphere(x + rnd.uniform(-r, r) * 0.7, y + rnd.uniform(-r, r) * 0.7, rnd.uniform(0.3, h), r * rnd.uniform(0.55, 0.85),
                 rnd.choice(mats))


# ------------------------------------------------------------------------------------------------------------------
# Landmarks
# ------------------------------------------------------------------------------------------------------------------
def laundromat(s, x0, x1, fy):
    """INES' LAUNDROMAT: wide lit shopfront with machines turning, TWO DOLLARS chalkboard, yellow awning, 3 storeys.
    Mia's flat = the third-floor window with the yellow flower box (x0 + 1.7..3.6)."""
    rnd = R(74)
    hgt = house_body(s, x0, x1, fy, 8.0, 3, "plaster_ochre", ground_h=3.4)
    # shopfront: big glass recess with lit machines
    gx0, gx1 = x0 + 0.5, x1 - 3.1
    for (a, b, c, d2, z0, z1) in ((gx0 - 0.15, fy - 0.04, gx0, fy + 0.06, 0.45, 2.9), (gx1, fy - 0.04, gx1 + 0.15, fy + 0.06, 0.45, 2.9),
                                  (gx0 - 0.15, fy - 0.04, gx1 + 0.15, fy + 0.06, 0.45, 0.62), (gx0 - 0.15, fy - 0.04, gx1 + 0.15, fy + 0.06, 2.75, 2.9)):
        s.box(a, b, c, d2, z0, z1, "wood_blue")                                                      # frame (4 bars: the window stays open)
    s.box(gx0, fy + 0.0, gx1, fy + 0.02, 0.62, 2.75, "shop_light")                                  # lit back wall (proud of the facade)
    mx = gx0 + 0.15
    k = 0
    while mx + 0.85 < gx1:
        z0, z1 = 0.7, 1.55
        s.box(mx, fy + 0.02, mx + 0.8, fy + 0.2, z0, z1, "washer_white")
        s.cyl(mx + 0.4, fy + 0.2, z0 + 0.48, z0 + 0.52, 0.27, "washer_dial", axis="y", verts=20)
        s.cyl(mx + 0.4, fy + 0.22, z0 + 0.48, z0 + 0.53, 0.2, "glass_office", axis="y", verts=20)
        s.box(mx + 0.1, fy + 0.2, mx + 0.7, fy + 0.23, z0 + 0.74, z0 + 0.8, "washer_dial")
        if k % 2 == 0:
            s.sphere(mx + 0.38, fy + 0.26, 1.43, 0.09, rnd.choice(["cloth_red", "cloth_blue", "cloth_yellow"]))   # sock in the porthole
        s.box(mx, fy + 0.02, mx + 0.8, fy + 0.2, 1.62, 2.4, "washer_white")                       # dryer stack above
        s.cyl(mx + 0.4, fy + 0.2, 2.0, 2.04, 0.26, "washer_dial", axis="y", verts=20)
        mx += 0.95
        k += 1
    # door (right of the window) + stoop
    dx = x1 - 1.55
    door_left(s, dx - 0.62, dx + 0.62, fy, 2.4, mat="wood_blue")
    s.box(dx - 0.35, fy - 0.01, dx + 0.35, fy + 0.03, 2.5, 2.9, "sign_cream")
    s.text("OPEN", dx, fy + 0.05, 2.67, 0.3, "red_paint", face="left")
    # yellow/white striped awning
    x = gx0 - 0.2
    i = 0
    while x < gx1 + 0.2:
        s.wedge(x, fy, min(x + 0.5, gx1 + 0.2), fy + 1.2, 3.3, 2.9, "y", "awning_yellow" if i % 2 == 0 else "awning_white")
        x += 0.5
        i += 1
    # painted sign board above
    s.box(x0 + 0.4, fy - 0.05, x1 - 0.4, fy + 0.1, 3.5, 4.3, "wood_blue")
    s.box(x0 + 0.34, fy - 0.05, x1 - 0.34, fy + 0.12, 3.46, 3.5, "brass")
    s.text("INES' LAUNDROMAT", (x0 + x1) / 2, fy + 0.12, 3.98, 0.42, "sign_cream", face="left", bold=True)
    s.text("clean shirts, clean souls!", (x0 + x1) / 2, fy + 0.12, 3.64, 0.17, "gold_bright", face="left")
    # chalkboard
    sx, sy = gx0 + 1.2, fy + 1.55
    s.box(sx - 0.38, sy - 0.12, sx + 0.38, sy - 0.04, 0, 1.0, "wood")
    s.box(sx - 0.32, sy - 0.04, sx + 0.32, sy - 0.01, 0.1, 0.93, "chalkboard")
    s.text("TWO", sx, sy + 0.0, 0.7, 0.2, "chalk", face="left")
    s.text("DOLLARS", sx, sy + 0.0, 0.42, 0.17, "chalk", face="left")
    s.set_solid(sx - 0.35, sy - 0.2, sx + 0.35, sy + 0.1)
    # upper floors: windows, Mia's window (third floor, yellow flower box), AC, dish
    storey_windows(s, x0, x1, fy, 3.4 - 0.5, rnd=rnd, shutters=True)
    mw0 = x0 + 1.6
    storey_windows(s, x0, x1, fy, 3.4 + 2.8 - 0.5, rnd=rnd, skip=(0,), boxes=False)
    window_left(s, mw0, mw0 + 1.5, fy - 0.02, 6.2 + 0.75 - 0.5 + 0.0, 6.2 + 2.25 - 0.5 - 0.0, frame="trim_white")
    s.box(mw0 - 0.05, fy - 0.02, mw0 + 1.55, fy + 0.28, 6.2 + 0.2, 6.2 + 0.42, "awning_yellow")
    for k2 in range(5):
        s.sphere(mw0 + 0.15 + k2 * 0.3, fy + 0.15, 6.2 + 0.52, 0.09, rnd.choice(["flower_yellow", "flower_white", "leaves_light"]))
    ac_unit(s, x1 - 1.6, fy, 6.2)
    dish(s, x0 + 0.5, fy + 0.4, 8.6)
    drainpipe(s, x0 + 0.1, fy, hgt)
    drainpipe(s, x1 - 0.1, fy, hgt)
    s.box(x1 - 0.05, fy - 8.0, x1 + 0.01, fy, 0.0, hgt, "plaster_ochre")                         # east wall skin (mural lives on it)
    # door mat / lamp
    s.box(dx - 0.55, fy + 0.5, dx + 0.55, fy + 0.95, 0.0, 0.03, "mat_red", layer="floor")
    # a bag of laundry and a bench by the window
    bench_along_x(s, gx0 + 3.0, gx0 + 4.8, fy + 0.95)
    s.sphere(gx0 + 3.9, fy + 0.6, 0.45, 0.2, "cloth_white")
    return hgt


def mural_east_wall(s, x, y0, y1, z0):
    """Big painted sun + fish mural on the +x facing wall of the laundromat (plane x), made of flat polys / discs."""
    xm = x + 0.02
    s.box(xm - 0.01, y0 + 1.0, xm + 0.02, y1 - 0.6, z0, z0 + 3.2, "plaster_blue")
    s.cyl(xm, (y0 + y1) / 2, z0 + 2.2, z0 + 2.26, 1.0, "flower_yellow", axis="x", verts=28)
    s.cyl(xm + 0.01, (y0 + y1) / 2, z0 + 2.2, z0 + 2.27, 0.7, "sunflower", axis="x", verts=28)
    for k in range(10):                                                                        # rays
        a = k * math.pi / 5
        yy, zz = (y0 + y1) / 2 + math.cos(a) * 1.5, z0 + 2.2 + math.sin(a) * 1.5 * 0.75
        s.box(xm, yy - 0.08, xm + 0.04, yy + 0.08, zz - 0.15, zz + 0.15, "flower_yellow")
    s.sphere(xm + 0.04, y0 + 1.6, z0 + 0.9, 0.5, "flower_red", sz=0.5, sy=1.2)                  # a fish
    s.poly([(xm + 0.03, y0 + 2.1, z0 + 0.9), (xm + 0.03, y0 + 2.6, z0 + 1.3), (xm + 0.03, y0 + 2.6, z0 + 0.5)], "flower_red")
    s.box(xm, y0 + 1.1, xm + 0.04, y1 - 0.7, z0 - 0.05, z0 + 0.0, "poster_green")


def backroom_annex(s, x0, y0, x1, y1):
    """Lean-to back room against the laundromat's east wall: tin roof, boarded window, door facing +x with a bell and a mat."""
    h0, h1 = 2.6, 2.2
    s.box(x0, y0, x1, y1, 0, h0, "plaster_cream")
    s.box(x0 - 0.05, y0, x1 + 0.05, y1 + 0.05, h0, h0 + 0.1, "stone")
    # sloped tin roof (wedge slopes along y, so use a flat roof with a tilt-ish box + rim)
    s.box(x0 - 0.15, y0 - 0.15, x1 + 0.25, y1 + 0.2, h0 + 0.1, h0 + 0.2, "tin_roof")
    s.box(x0 - 0.15, y0 - 0.15, x1 + 0.25, y0 - 0.05, h0 + 0.2, h0 + 0.35, "tin_roof")
    # door on the +x face
    ym = (y0 + y1) / 2 + 0.2
    s.box(x1 - 0.02, ym - 0.62, x1 + 0.05, ym + 0.62, 0, 2.15, "trim_white")
    s.box(x1 - 0.01, ym - 0.5, x1 + 0.08, ym + 0.5, 0, 2.05, "wood_green")
    s.box(x1 + 0.06, ym - 0.35, x1 + 0.1, ym + 0.35, 1.0, 1.04, "wood_dark")
    s.box(x1 + 0.06, ym + 0.32, x1 + 0.2, ym + 0.42, 1.0, 1.14, "brass")
    s.box(x1 + 0.4, ym - 0.5, x1 + 1.3, ym + 0.5, 0.0, 0.03, "mat_red", layer="floor")
    s.box(x1 + 0.02, ym - 0.25, x1 + 0.3, ym + 0.25, 2.25, 2.6, "sign_cream")
    s.text("ROOM", x1 + 0.31, ym, 2.45, 0.16, "ink_black", face="right")
    # boarded-up window and a lamp
    s.box(x1 - 0.02, y0 + 0.35, x1 + 0.04, y0 + 1.0, 0.9, 1.7, "trim_white")
    for k in range(3):
        s.box(x1 + 0.0, y0 + 0.3, x1 + 0.08, y0 + 1.06, 0.95 + k * 0.25, 1.1 + k * 0.25, "boards")
    s.set_solid(x0, y0, x1 - 0.001, y1 - 0.001)
    s.set_solid(x1 - 0.5, ym - 0.5, x1 + 0.2, ym + 0.5, False) if False else None
    s.occluder(x0, y0, x1, y1, h0 + 0.5)


def bakery(s, x0, x1, fy):
    """BELLINI BAKERY ('Forno Bellini'): rose plaster, red/white awning, bread window, hanging sign, Dr. Okafor's flat above."""
    rnd = R(75)
    hgt = house_body(s, x0, x1, fy, 8.0, 2, "plaster_rose", ground_h=3.2)
    gx0, gx1 = x0 + 0.5, x0 + 3.6
    s.box(gx0 - 0.15, fy - 0.04, gx1 + 0.15, fy + 0.06, 0.45, 2.7, "trim_white")
    s.box(gx0, fy - 0.25, gx1, fy - 0.17, 0.6, 2.55, "shop_light")
    s.box(gx0 + 0.03, fy - 0.16, gx1 - 0.03, fy + 0.0, 0.7, 0.78, "wood")                           # counter shelf
    s.box(gx0 + 0.03, fy - 0.16, gx1 - 0.03, fy + 0.0, 1.45, 1.5, "wood")
    for shelf in (0.78, 1.5):
        xx = gx0 + 0.2
        while xx < gx1 - 0.4:
            s.sphere(xx + 0.17, fy - 0.07, shelf + 0.11, 0.14, "bread_crust", sz=0.7, sx=1.5, sy=0.8)
            xx += 0.52
    dx = x0 + 5.0
    door_left(s, dx - 0.55, dx + 0.55, fy, 2.3, mat="wood_red")
    x = x0 + 0.2
    i = 0
    while x < x1 - 0.2:
        s.wedge(x, fy, min(x + 0.5, x1 - 0.2), fy + 1.3, 3.0, 2.6, "y", "awning_red" if i % 2 == 0 else "awning_white")
        x += 0.5
        i += 1
    s.box(x0 + 0.6, fy - 0.05, x1 - 0.6, fy + 0.1, 3.15, 3.7, "wood_red")
    s.text("BELLINI BAKERY", (x0 + x1) / 2, fy + 0.11, 3.42, 0.34, "sign_cream", face="left", bold=True)
    # hanging bread sign (bracket + pretzel-ish disc)
    s.box(x1 - 0.1, fy + 0.0, x1 + 0.3, fy + 0.05, 3.0, 3.04, "metal_dark") if False else None
    s.tube([(x1 - 0.5, fy + 0.02, 2.95), (x1 - 0.5, fy + 0.5, 2.95)], 0.025, "metal_dark")
    s.cyl(x1 - 0.5, fy + 0.5, 2.5, 2.54, 0.22, "bread_crust", axis="y", verts=14) if False else None
    s.sphere(x1 - 0.5, fy + 0.52, 2.65, 0.2, "bread_crust", sz=0.7, sx=1.3, sy=0.5)
    storey_windows(s, x0, x1, fy, 3.2 - 0.5, rnd=rnd, boxes=False)
    # Dr. Okafor's window: lace curtain + a tiny stethoscope-green plant box
    flower_box(s, x0 + 0.9, x0 + 2.4, fy - 0.02, 3.2 + 0.25, rnd)
    chimney_x = x1 - 1.2
    s.box(chimney_x, fy - 5.5, chimney_x + 0.9, fy - 4.6, hgt, hgt + 2.0, "brick_brown")
    s.box(chimney_x - 0.1, fy - 5.6, chimney_x + 1.0, fy - 4.5, hgt + 2.0, hgt + 2.12, "stone")
    produce_bread_crates(s, x0 + 0.6, fy + 0.4)
    a_frame_sign(s, x0 + 6.0, fy + 1.5)
    s.box(dx - 0.5, fy + 0.5, dx + 0.5, fy + 0.95, 0.0, 0.03, "mat_red", layer="floor")
    drainpipe(s, x1 - 0.1, fy, hgt)
    return hgt


def produce_bread_crates(s, x, y):
    s.box(x, y, x + 1.4, y + 0.6, 0, 0.5, "wood_dark")
    for k in range(3):
        s.sphere(x + 0.3 + 0.4 * k, y + 0.3, 0.62, 0.15, "bread_crust", sz=0.7, sx=1.4)
    s.set_solid(x, y, x + 1.4, y + 0.6)


def arch(s):
    """OLD BLOCK - EST. 1931: brick pillars, iron arch, sign half pasted over with VaultTech posters."""
    ax0, ax1 = 14.5, 15.7
    for (y0, y1) in ((18.5, 19.7), (24.3, 25.5)):
        s.box(ax0, y0, ax1, y1, 0, 4.0, "brick_brown")
        s.box(ax0 - 0.1, y0 - 0.1, ax1 + 0.1, y1 + 0.1, 3.75, 4.0, "stone")
        s.box(ax0 - 0.1, y0 - 0.1, ax1 + 0.1, y1 + 0.1, 0, 0.45, "stone")
        s.set_solid(ax0, y0, ax1 - 0.001, y1 - 0.001)
        s.occluder(ax0 - 0.1, y0 - 0.1, ax1 + 0.1, y1 + 0.1, 4.2)
    # arch beam + iron lettering board
    s.box(ax0, 18.5, ax1, 25.5, 4.0, 4.5, "brick_brown")
    s.box(ax0 - 0.1, 18.4, ax1 + 0.1, 25.6, 4.5, 4.62, "stone")
    s.box(ax0 + 0.15, 19.0, ax0 + 0.35, 25.0, 4.62, 5.9, "metal_dark")                            # sign board (faces +x and -x), seen from +x
    s.box(ax1 - 0.4, 19.0, ax1 - 0.2, 25.0, 4.62, 5.9, "metal_dark")
    s.box(ax1 - 0.21, 19.15, ax1 - 0.15, 24.85, 4.75, 5.75, "sign_cream")
    s.text("OLD BLOCK", ax1 - 0.14, 22.0, 5.3, 0.62, "ink_black", face="right", bold=True)
    s.text("EST. 1931", ax1 - 0.14, 22.0, 4.92, 0.27, "red_paint", face="right", bold=True)
    for (yy, zz, m) in ((19.6, 5.45, "poster_blue"), (20.6, 5.1, "poster_yellow"), (24.3, 5.5, "poster_blue")):    # VaultTech posters pasted over
        s.box(ax1 - 0.16, yy, ax1 - 0.08, yy + 0.9, zz - 0.55, zz + 0.35, m)
    s.box(ax1 - 0.15, 23.6, ax1 - 0.06, 24.3, 4.7, 5.5, "notice_orange")
    # iron lamps on the pillars
    for y in (19.1, 24.9):
        s.box(ax0 + 0.35, y - 0.15, ax0 + 0.65, y + 0.15, 4.1, 4.5, "lamp_glass")
    s.lamps.append((15.1, 19.1))
    s.lamps.append((15.1, 24.9))


def cable_works(s, rnd):
    """VaultLink cable works in the avenue stub: barrier line at x=10.5, trench x 11.3..13.3, drums, TRENCH-E 3, Pruitt, signs."""
    bx = 10.5
    # barrier panels across the road (y 18.5..25.5), each an orange/white striped board on two feet + amber lamps
    y = 18.6
    while y < 25.4:
        s.box(bx - 0.1, y, bx + 0.1, y + 1.15, 0.55, 1.15, "barrier_stripes")
        s.box(bx - 0.1, y, bx + 0.1, y + 1.15, 1.15, 1.2, "gold_dark")
        for yy in (y + 0.1, y + 1.0):
            s.box(bx - 0.1, yy - 0.04, bx + 0.1, yy + 0.04, 0, 0.58, "metal_dark")
        y += 1.18
    s.set_solid(bx - 0.25, 18.5, bx + 0.25, 25.5)
    s.occluder(bx - 0.3, 18.5, bx + 0.3, 25.5, 1.3)
    for yy in (18.9, 22.0, 25.1):
        s.box(bx - 0.08, yy - 0.08, bx + 0.08, yy + 0.08, 1.2, 1.28, "metal_dark")
        s.cyl(bx, yy, 1.28, 1.52, 0.1, "lamp_amber", verts=10)
        s.lights and None
    s.lamps.append((bx, 22.0))
    # hazard board with the sign text
    s.box(bx - 0.14, 20.0, bx - 0.06, 24.0, 1.3, 2.5, "sign_white")
    s.box(bx - 0.16, 19.95, bx - 0.04, 24.05, 2.5, 2.58, "hazard_black")
    for yy in (20.2, 23.8):
        s.box(bx - 0.04, yy - 0.05, bx + 0.0, yy + 0.05, 0, 1.3, "metal_dark")
    s.text("SURVEY IN PROGRESS", bx - 0.15, 22.0, 2.2, 0.26, "ink_black", face="left", bold=True) if False else None
    # (sign faces +x/-x; readable from the player's west side we need face 'right' on the west plane -> text on the +x side only)
    s.text("SURVEY IN PROGRESS", bx + 0.04, 22.0, 2.18, 0.26, "ink_black", face="right", bold=True)
    s.text("NO ENTRY", bx + 0.04, 22.0, 1.82, 0.3, "red_paint", face="right", bold=True)
    s.text("VaultLink HyperFibre - laying the future", bx + 0.04, 22.0, 1.5, 0.12, "ink_black", face="right")
    # trench: lower mud box between road pieces is built in the ground pass (see ground()); here the warning tape + spoil heap
    for y in (18.55, 25.35):
        s.box(11.2, y - 0.04, 13.4, y + 0.04, 0.25, 0.3, "notice_orange")
    for x in (11.25, 13.35):
        for y in (18.7, 22.0, 25.2):
            s.cyl(x, y, 0, 0.3, 0.03, "metal_dark", verts=6)
        s.box(x - 0.01, 18.6, x + 0.01, 25.4, 0.25, 0.3, "barrier_stripes")
    # spoil heap at the north end of the trench
    for (xx, yy, r) in ((12.3, 17.9, 0.5), (11.7, 17.5, 0.35), (12.9, 17.6, 0.4)):
        s.sphere(xx, yy, 0.05, r, "mud", sz=0.6)
    # cable drums
    for (x, y) in ((12.0, 26.3), (13.4, 26.5), (12.7, 27.4), (13.1, 17.0)):
        cable_drum(s, x, y)
    # a cable laid into the trench
    s.tube([(11.5, 22.8, -0.3), (12.2, 22.9, -0.3), (13.1, 22.7, -0.3), (13.9, 22.9, -0.1)], 0.08, "notice_orange")
    trench_e(s, 12.3, 21.3)
    pruitt(s, 8.6, 19.9)
    # camera on a pole + plastic floodlight
    s.cyl(9.6, 25.9, 0, 3.4, 0.05, "metal_grey", verts=8)
    s.box(9.45, 25.75, 9.85, 26.1, 3.3, 3.55, "vault_cold")
    s.cyl(9.65, 26.12, 3.43, 3.48, 0.07, "glass", axis="y", verts=10)
    s.set_solid(9.4, 25.8, 9.9, 26.0)
    s.occluder(9.4, 25.7, 9.9, 26.1, 3.6)


def cable_drum(s, x, y):
    s.cyl(x, y, 0.0, 0.07, 0.62, "wood", verts=18)
    s.cyl(x, y, 0.07, 0.95, 0.4, "notice_orange", verts=18)
    s.cyl(x, y, 0.95, 1.02, 0.62, "wood", verts=18)
    s.cyl(x, y, 0.35, 0.65, 0.42, "wire_dark", verts=18)
    s.box(x - 0.2, y + 0.38, x + 0.2, y + 0.43, 0.45, 0.8, "gold_dark")
    s.set_solid(x - 0.45, y - 0.45, x + 0.45, y + 0.45)
    s.occluder(x - 0.5, y - 0.5, x + 0.5, y + 0.5, 1.05)


def trench_e(s, x, y):
    """TRENCH-E 3: small yellow tracked work robot with a bucket arm and one eye lamp (placeholder model, sprite later)."""
    s.box(x - 0.7, y - 0.5, x + 0.7, y - 0.2, 0.0, 0.42, "rubber_track")
    s.box(x - 0.7, y + 0.2, x + 0.7, y + 0.5, 0.0, 0.42, "rubber_track")
    s.box(x - 0.55, y - 0.28, x + 0.55, y + 0.28, 0.25, 0.8, "yellow_machine")
    s.box(x - 0.2, y - 0.2, x + 0.3, y + 0.2, 0.8, 1.05, "yellow_machine")
    s.cyl(x + 0.35, y, 0.9, 0.94, 0.09, "lamp_amber", axis="x", verts=10)
    s.tube([(x + 0.4, y, 0.7), (x + 0.9, y, 1.0), (x + 1.2, y, 0.55)], 0.05, "metal_dark")
    s.box(x + 1.1, y - 0.2, x + 1.5, y + 0.2, 0.3, 0.6, "yellow_machine")
    s.set_solid(x - 0.7, y - 0.5, x + 1.5, y + 0.5)
    s.occluder(x - 0.7, y - 0.5, x + 1.5, y + 0.5, 1.1)


def pruitt(s, x, y):
    """Guard Pruitt on a folding chair on a drum, doing a crossword (PLACEHOLDER figure: the real sprite comes from the cast pipeline)."""
    s.cyl(x, y, 0, 0.5, 0.5, "notice_orange", verts=14)
    s.box(x - 0.2, y - 0.2, x + 0.2, y + 0.2, 0.5, 0.56, "metal_dark")
    s.box(x - 0.15, y - 0.2, x + 0.15, y - 0.15, 0.56, 1.0, "metal_dark")
    s.box(x - 0.17, y - 0.12, x + 0.17, y + 0.12, 0.56, 1.0, "vault_hoard")
    s.sphere(x, y, 1.12, 0.12, "skin_guard")
    s.cyl(x, y, 1.2, 1.26, 0.17, "vault_hoard", verts=12)
    s.box(x + 0.1, y + 0.1, x + 0.35, y + 0.4, 0.7, 0.72, "sign_cream")
    s.set_solid(x - 0.5, y - 0.5, x + 0.5, y + 0.5)
    s.occluder(x - 0.5, y - 0.5, x + 0.5, y + 0.5, 1.3)


def sneak_fence_and_bushes(s, rnd):
    """VaultTech chain-link fence x=10.5 from the barrier to y=34.5 with a bent-open flap at y 30.2..31.2, hidden by a hedge on the
    player's side; behind the fence the overgrown thicket with a one-cell lane (see LANE_CELLS)."""
    bx = 10.5
    chain_link_y(s, bx, 25.5, 30.2)
    chain_link_y(s, bx, 31.2, 34.5)
    chain_link_y(s, bx, 14.5, 18.5)
    # the flap: bottom corner of the fence peeled up and bent aside
    s.poly([(bx, 30.2, 0.05), (bx, 31.2, 0.05), (bx + 0.45, 31.0, 0.55), (bx + 0.45, 30.4, 0.7)], "chain_link")
    s.cyl(bx, 30.2, 0, 2.05, 0.04, "metal_grey", verts=8)
    s.cyl(bx, 31.2, 0, 2.05, 0.04, "metal_grey", verts=8)
    s.box(bx - 0.04, 30.2, bx + 0.04, 31.2, 1.9, 2.0, "metal_grey")
    # hedge on the player's side hiding the flap (with a hollow behind the leaves)
    for yy in (28.9, 29.5, 30.1, 31.3, 31.9, 32.5):
        bush_ball(s, bx - 0.8, yy, 0.55, rnd, h=1.4)
    s.set_solid(bx - 1.5, 28.6, bx - 0.2, 30.0)
    s.set_solid(bx - 1.5, 31.4, bx - 0.2, 33.0)
    for yy in (30.5, 31.0):
        s.sphere(bx - 0.75, yy, 1.2, 0.3, "leaves_light")               # the 'branch' Mia lifts
    # VaultTech sign on the fence
    s.box(bx - 0.06, 26.2, bx - 0.02, 28.2, 0.9, 1.7, "sign_blue")
    s.text("VAULTTECH SITE", bx - 0.07, 27.2, 1.4, 0.2, "paint_white", face="left") if False else None
    # THICKET: dense bushes everywhere x 10.9..18.2, y 27.4..34.5 except the lane
    lane = [(10.9, 30.35, 17.0, 31.05), (16.4, 27.0, 17.1, 31.05)]
    def in_lane(x, y):
        for (a, b, c, d) in lane:
            if a - 0.35 <= x <= c + 0.35 and b - 0.35 <= y <= d + 0.35:
                return True
        return False
    for xx in [10.9 + 0.8 * i for i in range(10)]:
        for yy in [27.5 + 0.8 * j for j in range(9)]:
            x, y = xx + rnd.uniform(-0.2, 0.2), yy + rnd.uniform(-0.2, 0.2)
            if in_lane(x, y):
                continue
            # camera-side rows (large y) stay lower so the squeezing player stays partly visible
            if yy > 31.3:
                # camera-side rows must stay LOW: at 2:1 iso anything 0.75 m tall hides ~2.5 cells of ground behind it
                if rnd.random() < 0.22:
                    bush_ball(s, x, y, 0.32, rnd, h=1.0)        # a few clumps the squeezing player can pass behind
                else:
                    s.sphere(x, y, 0.12, rnd.uniform(0.18, 0.26), rnd.choice(["leaves", "bush_dark", "leaves_light"]), sz=0.7)
            else:
                bush_ball(s, x, y, rnd.uniform(0.45, 0.62), rnd, h=1.6)
    for (a, b, c, d) in lane:                                                                   # worn earth path of the lane
        s.box(a, b + 0.1, c, d - 0.1, 0.0, 0.012, "path_dirt", layer="floor")
    # roses Ines counts
    for (x, y) in ((13.0, 31.6), (14.4, 29.7)):
        s.sphere(x, y, 1.0, 0.1, "flower_red")
    s.set_solid(10.9, 27.4, 18.2, 30.2)         # thicket body solid ...
    s.set_solid(10.9, 31.1, 18.2, 34.5)
    s.set_solid(10.9, 30.2, 16.3, 31.1, False) if False else None
    s.set_solid(16.3, 27.4, 18.2, 30.2)
    s.set_solid(10.9, 30.2, 16.3, 31.1, False)  # ... except the lane (gated by flag `sneak_route` in the real game)
    s.set_solid(16.0, 27.0, 17.2, 30.2, False)


def plane_tree(s, x, y, sc=1.25):
    s.cyl(x, y, 0, 2.4 * sc, 0.17 * sc, "concrete", verts=10, r2=0.12 * sc)
    for (dx, dy, dz, r) in ((0, 0, 3.6, 1.35), (-0.9, 0.5, 3.1, 1.0), (0.8, -0.6, 3.2, 1.0), (0.5, 0.9, 2.9, 0.9), (-0.4, -0.8, 3.9, 0.9),
                            (0.0, 0.0, 4.4, 0.8)):
        s.sphere(x + dx / CELL_M * sc * 0.5, y + dy / CELL_M * sc * 0.5, dz * sc, r * sc, "leaves_light" if dz > 3.3 else "leaves")
    s.box(x - 1.1, y - 1.1, x + 1.1, y + 1.1, 0, 0.04, "soil", layer="floor")
    s.set_solid(x - 0.25, y - 0.25, x + 0.25, y + 0.25)
    s.occluder(x - 1.4, y - 1.4, x + 1.4, y + 1.4, 5.0)


def chess_table(s, x, y):
    s.cyl(x, y, 0, 0.62, 0.3, "stone", verts=10, r2=0.22)
    s.box(x - 0.55, y - 0.55, x + 0.55, y + 0.55, 0.62, 0.7, "tiles_checker")
    for (dx, dy) in ((-0.95, 0.0), (0.95, 0.0)):
        s.cyl(x + dx, y + dy, 0, 0.42, 0.2, "wood_dark", verts=10)
    for k in range(6):                                                    # chess pieces
        s.cyl(x - 0.3 + 0.12 * k, y - 0.1 + 0.08 * (k % 2), 0.7, 0.86 - 0.02 * (k % 3), 0.045, "ink_black" if k % 2 else "sign_cream",
              verts=8)
    s.set_solid(x - 0.6, y - 0.6, x + 0.6, y + 0.6)
    s.occluder(x - 0.6, y - 0.6, x + 0.6, y + 0.6, 0.9)
    for (dx, dy) in ((-0.95, 0.0), (0.95, 0.0)):
        s.set_solid(x + dx - 0.2, y + dy - 0.2, x + dx + 0.2, y + dy + 0.2)


def rosas_stall(s, x, y):
    """Handcart with a sun-faded striped awning, crates, scale and hand-lettered price cards (x, y = cart centre)."""
    s.box(x - 1.2, y - 0.7, x + 1.2, y + 0.7, 0.55, 0.7, "wood")                       # cart bed
    s.box(x - 1.2, y - 0.7, x + 1.2, y - 0.62, 0.7, 1.0, "wood")                       # side boards
    s.box(x - 1.2, y + 0.62, x + 1.2, y + 0.7, 0.7, 0.95, "wood")
    s.box(x + 1.15, y - 0.7, x + 1.2, y + 0.7, 0.7, 0.95, "wood")
    for yy in (y - 0.8, y + 0.8):
        s.cyl(x - 0.6, yy, 0.45, 0.5, 0.45, "wood_dark", axis="y", verts=18)                 # wheels
    s.tube([(x - 1.2, y - 0.5, 0.75), (x - 2.2, y - 0.3, 0.45), (x - 2.3, y + 0.3, 0.45), (x - 1.2, y + 0.5, 0.75)], 0.04, "wood_dark")
    # awning on two poles
    for (px, py) in ((x - 1.1, y + 0.9), (x + 1.1, y + 0.9)):
        s.cyl(px, py, 0, 2.6, 0.04, "wood_dark", verts=8)
    for k in range(6):
        s.wedge(x - 1.4 + k * 0.5, y - 0.9, x - 0.9 + k * 0.5, y + 1.1, 2.75, 2.3, "y", "awning_sun" if k % 2 == 0 else "awning_white")
    # goods: bread loaves, oranges, a scale
    for k in range(5):
        s.sphere(x - 0.9 + 0.35 * k, y - 0.25, 0.85, 0.15, "bread_crust", sz=0.7, sx=1.4)
    for k in range(6):
        s.sphere(x + 0.1 + 0.2 * (k % 3), y + 0.25 + 0.2 * (k // 3), 0.82, 0.1, "orange_fruit")
    s.box(x + 0.7, y - 0.1, x + 1.0, y + 0.2, 0.7, 0.78, "metal_dark")
    s.cyl(x + 0.85, y + 0.05, 0.78, 0.82, 0.13, "metal_light", verts=12)
    # signboard with a smiley O: BREAD NOT BARCODES
    s.box(x - 1.3, y + 1.15, x + 1.3, y + 1.25, 0.15, 0.7, "sign_cream")
    s.text("BREAD NOT BARCODES", x, y + 1.26, 0.43, 0.16, "red_paint", face="left", bold=True)
    for k in range(3):                                                                    # price cards
        s.box(x - 0.6 + 0.4 * k, y + 0.72, x - 0.38 + 0.4 * k, y + 0.74, 1.0, 1.14, "sign_cream")
    crate_stack(s, x + 1.5, y - 0.2, 3)
    crate_stack(s, x + 1.5, y + 0.4, 2)
    s.set_solid(x - 2.4, y - 0.9, x + 1.3, y + 0.85)
    s.occluder(x - 1.4, y - 0.9, x + 1.3, y + 1.1, 2.9)


def garden(s, x0, y0, x1, y1, rnd):
    """Community garden: low fence, raised beds with crops, shed, rain barrel, compost, scarecrow, bench with a WATER ME sign."""
    s.box(x0, y0, x1, y1, -0.1, 0.0, "grass_flat", layer="floor")
    # dirt paths
    s.box(x0 + 5.8, y0, x0 + 6.8, y1, 0.0, 0.01, "path_dirt", layer="floor")
    s.box(x0, y0 + 5.0, x1, y0 + 5.8, 0.0, 0.01, "path_dirt", layer="floor")
    s.box(x0 + 5.8, y0 - 1.0, x0 + 6.8, y0, 0.0, 0.01, "path_dirt", layer="floor")
    # low wooden fence with a gate gap at the path
    fence_wood(s, x0, x0 + 5.6, y0 + 0.05, h=0.85)
    fence_wood(s, x0 + 7.0, x1, y0 + 0.05, h=0.85)
    for xx in (x0 + 5.6, x0 + 7.0):
        s.box(xx - 0.06, y0 - 0.05, xx + 0.06, y0 + 0.15, 0, 1.15, "wood_dark")
    s.box(x0 + 5.5, y0 - 0.06, x0 + 7.1, y0 + 0.16, 1.1, 1.18, "wood_dark")
    s.text("COMMUNITY GARDEN", x0 + 6.3, y0 + 0.17, 1.4, 0.2, "paint_white", face="left") if False else None
    s.box(x0 + 3.6, y0 + 0.06, x0 + 5.3, y0 + 0.14, 0.9, 1.35, "wood_green")
    s.text("GARDEN", x0 + 4.45, y0 + 0.15, 1.25, 0.2, "sign_cream", face="left", bold=True)
    s.text("(water me - Ines)", x0 + 4.45, y0 + 0.15, 1.0, 0.1, "sign_cream", face="left")
    fence_wood(s, x0 - 0.0, x0 + 0.1, y0 + 0.05, h=0.85) if False else None
    # raised beds
    beds = [(x0 + 0.8, y0 + 1.0), (x0 + 3.0, y0 + 1.0), (x0 + 7.4, y0 + 1.0), (x0 + 9.6, y0 + 1.0),
            (x0 + 0.8, y0 + 6.4), (x0 + 3.0, y0 + 6.4), (x0 + 7.4, y0 + 6.4), (x0 + 9.6, y0 + 6.4)]
    crops = ["tomato", "cabbage", "sunflower", "beans", "cabbage", "tomato", "flowers", "sunflower"]
    for (bx, by), crop in zip(beds, crops):
        bw, bd = 1.9, 3.4
        s.box(bx, by, bx + bw, by + bd, 0.0, 0.42, "wood")
        s.box(bx + 0.1, by + 0.1, bx + bw - 0.1, by + bd - 0.1, 0.4, 0.45, "soil")
        for i in range(8):
            px, py = bx + 0.3 + (i % 2) * 1.3 + rnd.uniform(-0.1, 0.1), by + 0.35 + (i // 2) * 0.8
            if crop == "tomato":
                s.cyl(px, py, 0.45, 1.6, 0.025, "wood_dark", verts=6)
                s.sphere(px, py, 0.8, 0.22, "leaves")
                s.sphere(px + 0.12, py + 0.1, 0.62, 0.08, "tomato")
                s.sphere(px - 0.1, py + 0.05, 0.95, 0.08, "tomato")
            elif crop == "cabbage":
                s.sphere(px, py, 0.62, 0.22, "cabbage", sz=0.7)
            elif crop == "sunflower":
                s.cyl(px, py, 0.45, 1.9, 0.03, "leaves", verts=6)
                s.cyl(px, py + 0.0, 1.9, 1.98, 0.17, "sunflower", verts=12)
                s.sphere(px, py, 1.96, 0.09, "trunk", sz=0.4)
            elif crop == "beans":
                s.cyl(px, py, 0.45, 1.7, 0.02, "wood_dark", verts=6)
                for k in range(3):
                    s.sphere(px + rnd.uniform(-0.1, 0.1), py + rnd.uniform(-0.1, 0.1), 0.7 + k * 0.3, 0.12, "leaves_light")
            else:
                s.sphere(px, py, 0.6, 0.14, "leaves_light")
                s.sphere(px, py, 0.72, 0.09, rnd.choice(FLOWERS))
        s.set_solid(bx, by, bx + bw, by + bd)
        s.occluder(bx, by, bx + bw, by + bd, 2.0 if crop in ("sunflower", "tomato", "beans") else 0.7)
    # shed + rain barrel + compost + scarecrow + bench
    sx, sy = x0 + 0.6, y1 - 3.4
    s.box(sx, sy, sx + 3.0, sy + 2.6, 0, 2.1, "wood_green")
    s.box(sx - 0.2, sy - 0.2, sx + 3.2, sy + 2.8, 2.1, 2.22, "tin_roof")
    door_left(s, sx + 0.5, sx + 1.6, sy + 2.6, 1.7, mat="wood_dark", frame="wood")
    s.set_solid(sx, sy, sx + 3.0, sy + 2.6)
    s.occluder(sx - 0.2, sy - 0.2, sx + 3.2, sy + 2.8, 2.3)
    s.cyl(sx + 3.6, sy + 0.5, 0, 0.9, 0.38, "barrel_blue", verts=14)
    s.cyl(sx + 3.6, sy + 0.5, 0.9, 0.93, 0.34, "dirty_liquid", verts=14)
    s.set_solid(sx + 3.2, sy + 0.1, sx + 4.0, sy + 0.9)
    s.occluder(sx + 3.2, sy + 0.1, sx + 4.0, sy + 0.9, 0.95)
    crate_stack(s, x1 - 2.6, y1 - 2.0, 3)
    s.box(x1 - 2.6, y1 - 3.0, x1 - 1.6, y1 - 2.2, 0, 0.8, "cardboard_dark")                  # compost bin
    s.set_solid(x1 - 2.6, y1 - 3.0, x1 - 1.6, y1 - 2.2)
    s.cyl(x1 - 4.2, y0 + 4.2, 0, 1.7, 0.03, "wood_dark", verts=6)                            # scarecrow
    s.box(x1 - 4.9, y0 + 4.18, x1 - 3.5, y0 + 4.22, 1.35, 1.4, "wood_dark")
    s.sphere(x1 - 4.2, y0 + 4.2, 1.78, 0.14, "cloth_yellow")
    s.cyl(x1 - 4.2, y0 + 4.2, 1.88, 1.92, 0.22, "wood_dark", verts=10)
    s.cyl(x1 - 4.2, y0 + 4.2, 1.92, 2.08, 0.1, "wood_dark", verts=10)
    s.box(x1 - 4.7, y0 + 4.1, x1 - 3.7, y0 + 4.3, 1.0, 1.35, "cloth_red")
    s.set_solid(x1 - 4.4, y0 + 4.0, x1 - 4.0, y0 + 4.4)
    bench_along_x(s, x0 + 5.0, x0 + 6.6, y0 + 9.6)
    s.box(x0 + 5.1, y0 + 9.3, x0 + 6.5, y0 + 9.35, 0.9, 1.25, "sign_cream")
    s.text("WATER ME", x0 + 5.8, y0 + 9.36, 1.07, 0.13, "red_paint", face="left", bold=True)
    for (px, py) in ((x0 + 0.2, y0 + 5.2), (x1 - 0.5, y0 + 5.4)):
        potted_plant(s, px, py, "flowers")
    # fence on the other sides
    fence_wood(s, x0, x1, y1 + 0.2, h=0.9) if False else None
    for (px, py) in ((x0 + 12.0 - 0.8, y1 - 0.4),):
        shrub(s, px, py, 0.5, "leaves")
    s.box(x0 - 0.2, y1 - 0.1, x1, y1 + 0.1, 0.0, 0.6, "bush_dark")


def court(s, x0, y0, x1, y1, rnd):
    """Street court: concrete slab, painted court with lines, hoops at both ends, low chain-link fence (south/east), benches."""
    s.box(x0 - 0.5, y0 - 0.5, x1 + 0.5, y1 + 0.5, -0.1, 0.004, "concrete", layer="floor")
    s.box(x0, y0, x1, y1, 0.0, 0.012, "court_rust", layer="floor")
    s.box(x0 + 0.7, y0 + 0.7, x1 - 0.7, y1 - 0.7, 0.012, 0.022, "court_green", layer="floor")
    lw = 0.07
    ox0, oy0, ox1, oy1 = x0 + 0.7, y0 + 0.7, x1 - 0.7, y1 - 0.7
    for (a, b, c, d) in ((ox0, oy0, ox1, oy0 + lw), (ox0, oy1 - lw, ox1, oy1), (ox0, oy0, ox0 + lw, oy1), (ox1 - lw, oy0, ox1, oy1)):
        s.box(a, b, c, d, 0.022, 0.03, "paint_white", layer="floor")
    xm = (ox0 + ox1) / 2
    s.box(xm - lw / 2, oy0, xm + lw / 2, oy1, 0.022, 0.03, "paint_white", layer="floor")
    s.cyl(xm, (oy0 + oy1) / 2, 0.022, 0.03, 1.5, "paint_white", layer="floor", verts=28)
    s.cyl(xm, (oy0 + oy1) / 2, 0.03, 0.04, 1.36, "court_green", layer="floor", verts=28)
    for kx0, kx1 in ((ox0, ox0 + 3.4), (ox1 - 3.4, ox1)):                                   # keys
        s.box(kx0, (oy0 + oy1) / 2 - 1.5, kx1, (oy0 + oy1) / 2 + 1.5, 0.022, 0.03, "paint_white", layer="floor")
        s.box(kx0 + (lw if kx0 == ox0 else 0), (oy0 + oy1) / 2 - 1.5 + lw, kx1 - (0 if kx0 == ox0 else lw), (oy0 + oy1) / 2 + 1.5 - lw,
              0.03, 0.04, "court_rust", layer="floor")
    # scuffs and cracks
    for _ in range(14):
        sx, sy = rnd.uniform(ox0, ox1), rnd.uniform(oy0, oy1)
        s.box(sx, sy, sx + rnd.uniform(0.1, 0.35), sy + rnd.uniform(0.06, 0.18), 0.04 + rnd.random() * 0.004, 0.047 + rnd.random() * 0.004, "concrete",
              layer="floor")
    for (hx, face) in ((x0 + 1.0, 1), (x1 - 1.0, -1)):
        hoop(s, hx, (oy0 + oy1) / 2, face)
    # low fence: south side (camera side) and east side as low chain-link; the other sides open to the street
    chain_link(s, x0 - 0.5, x1 + 0.5, y1 + 0.5, h=1.3)
    chain_link_y(s, x1 + 0.5, y0 - 0.5, y1 + 0.5, h=1.3)
    chain_link_y(s, x0 - 0.5, y0 + 2.0, y1 + 0.5, h=1.3)
    # ball + bench + water bottle
    s.sphere(xm - 2.5, (oy0 + oy1) / 2 + 1.8, 0.18, 0.18, "orange_paint")
    bench_along_x(s, x0 + 2.0, x0 + 4.2, y0 - 0.4)
    bench_along_x(s, x1 - 4.2, x1 - 2.0, y0 - 0.4)
    trash_can(s, x0 + 5.0, y0 - 0.4)
    s.sphere(xm + 3.0, oy0 + 1.0, 0.06, 0.06, "bottle_clear", sz=2.0)


def hoop(s, x, y, face):
    """Basketball hoop: pole, backboard, rim, net. face +1 = board faces +x, -1 = board faces -x."""
    s.cyl(x - face * 0.5, y, 0, 3.1, 0.06, "metal_dark", verts=8)
    s.tube([(x - face * 0.5, y, 3.0), (x - face * 0.1, y, 3.05)], 0.04, "metal_dark")
    s.box(x - 0.04, y - 0.55, x + 0.04, y + 0.55, 2.7, 3.45, "sign_cream")
    s.box(x - 0.045, y - 0.18, x + 0.045, y + 0.18, 2.8, 3.0, "red_paint")
    ring = []
    for k in range(13):
        a = k * math.pi * 2 / 12
        ring.append((x + face * (0.3 + 0.2 * math.cos(a)), y + 0.2 * math.sin(a), 2.62))
    s.tube(ring, 0.022, "orange_paint")
    s.cyl(x + face * 0.3, y, 2.2, 2.62, 0.2, "cloth_white", verts=10, r2=0.1) if False else None
    s.set_solid(x - face * 0.6, y - 0.12, x - face * 0.4, y + 0.12)
    s.occluder(x - 0.4, y - 0.6, x + 0.4, y + 0.6, 3.5)


def demolition_site(s, x0, y0, x1, y1, rnd):
    rnd = R(68)
    """Fenced site: orange mesh fence (x0), notices, Co-op Hall (derelict), yellow digger, NODE 7 hatch, rubble, floodlight."""
    s.box(x0, y0, x1, y1, -0.1, 0.0, "rubble", layer="floor")
    for k in range(5):
        sx, sy = rnd.uniform(x0 + 0.5, x1 - 0.5), rnd.uniform(y0 + 14.0, y1 - 0.5)
        s.box(sx, sy, sx + rnd.uniform(0.5, 1.8), sy + rnd.uniform(0.4, 1.2), 0.0, 0.02 + rnd.random() * 0.02, "mud", layer="floor")
    # fence panels (orange net = barrier_stripes would be too loud; use chain_link + orange top rail) and notices
    chain_link_y(s, x0 - 0.1, y0, y1, h=2.1)
    s.box(x0 - 0.14, y0, x0 - 0.06, y1, 2.0, 2.1, "notice_orange")
    for k, yy in enumerate((16.0, 26.5, 30.0)):                         # VaultTech notices + Teo's counter posters
        m = "notice_orange" if k % 3 != 2 else "poster_green"
        s.box(x0 - 0.16, yy, x0 - 0.1, yy + 0.8, 0.9, 1.7, m)
    s.box(x0 - 0.2, 20.1, x0 - 0.06, 24.0, 0.3, 2.0, "metal_dark") if False else None
    # closed gate across the street end
    s.box(x0 - 0.12, 19.6, x0 - 0.04, 24.4, 0.1, 2.0, "metal_dark")
    for yy in (19.6, 24.4):
        s.box(x0 - 0.14, yy - 0.06, x0 - 0.02, yy + 0.06, 0, 2.2, "metal_grey")
    s.box(x0 - 0.19, 21.1, x0 - 0.1, 22.9, 1.1, 1.8, "notice_orange")
    s.text("NOTICE", x0 - 0.2, 22.0, 1.55, 0.2, "ink_black", face="right", bold=True)
    s.text("demolition: unsigned", x0 - 0.2, 22.0, 1.25, 0.1, "ink_black", face="right")
    # Co-op Hall
    hx0, hy0, hx1, hy1 = x0 + 1.8, 7.0, x1 - 0.4, 16.5
    s.box(hx0, hy0, hx1, hy1, 0, 5.2, "brick_flat")
    s.box(hx0 - 0.1, hy1 - 0.1, hx1 + 0.1, hy1 + 0.1, 4.8, 5.2, "stone")
    s.box(hx0, hy0 - 0.1, hx1, hy1 + 0.1, 5.2, 5.3, "stone")
    s.box(hx0 + 0.4, hy0 + 0.4, hx1 - 0.4, hy1 - 0.4, 5.3, 5.4, "roof")
    # big arched door boarded, chained; windows boarded
    dxm = (hx0 + hx1) / 2
    s.box(dxm - 1.0, hy1 - 0.02, dxm + 1.0, hy1 + 0.1, 0, 3.0, "boards")
    s.box(dxm - 1.15, hy1 - 0.02, dxm + 1.15, hy1 + 0.14, 3.0, 3.25, "stone")
    for wx in (hx0 + 0.7, hx1 - 2.1):
        s.box(wx, hy1 - 0.02, wx + 1.2, hy1 + 0.04, 1.2, 3.0, "metal_dark")      # empty window opening behind the boards
        s.box(wx - 0.02, hy1 + 0.0, wx + 1.22, hy1 + 0.08, 1.4, 1.7, "boards")
        s.box(wx - 0.02, hy1 + 0.0, wx + 1.22, hy1 + 0.08, 2.2, 2.5, "boards")
    s.box(hx0 + 0.9, hy1 - 0.03, hx1 - 0.9, hy1 + 0.09, 3.9, 4.6, "sign_cream")
    s.text("OLD BLOCK CO-OPERATIVE", (hx0 + hx1) / 2, hy1 + 0.1, 4.38, 0.26, "ink_black", face="left", bold=True)
    s.text("1931", (hx0 + hx1) / 2, hy1 + 0.1, 4.06, 0.2, "red_paint", face="left", bold=True)
    s.set_solid(hx0, hy0, hx1, hy1)
    s.occluder(hx0, hy0, hx1, hy1, 5.6)
    # digger
    digger(s, x0 + 5.0, 26.0)
    # NODE 7 hatch: steel plate in the ground, orange cables in, warm glow
    hx, hy = x0 + 1.0, 22.5
    s.box(hx - 0.7, hy - 0.7, hx + 0.7, hy + 0.7, 0.0, 0.05, "metal_grey", layer="floor")
    s.box(hx - 0.5, hy - 0.5, hx + 0.5, hy + 0.5, 0.05, 0.08, "metal_dark", layer="floor")
    s.box(hx - 0.35, hy - 0.06, hx + 0.35, hy + 0.06, 0.08, 0.1, "gold_dark", layer="floor")
    s.tube([(hx - 2.0, hy + 0.9, 0.04), (hx - 1.2, hy + 0.5, 0.06), (hx - 0.6, hy + 0.2, 0.1)], 0.07, "notice_orange")
    s.tube([(hx - 2.0, hy + 1.3, 0.04), (hx - 1.0, hy + 0.9, 0.06), (hx - 0.5, hy + 0.4, 0.1)], 0.07, "notice_orange")
    s.box(hx + 0.9, hy - 0.45, hx + 1.9, hy - 0.4, 0.0, 0.6, "sign_blue") if False else None
    s.box(hx - 0.8, hy + 0.7, hx + 0.8, hy + 0.75, 0.0, 0.5, "sign_white")
    s.text("NODE 7", hx, hy + 0.76, 0.34, 0.14, "ink_black", face="left", bold=True)
    # floodlight on a pole and rubble heaps
    pole(s, x0 + 3.0, 18.8, 4.6)
    s.box(x0 + 2.7, 18.6, x0 + 3.3, 19.0, 4.5, 4.9, "vault_cold")
    s.box(x0 + 2.75, 19.0, x0 + 3.25, 19.04, 4.55, 4.85, "lamp_glass")
    for (xx, yy, r) in ((x0 + 3.5, 29.8, 1.0), (x0 + 6.8, 21.0, 0.8), (x0 + 6.0, 30.5, 0.9), (x0 + 1.5, 31.0, 0.7)):
        for _ in range(3):
            s.sphere(xx + rnd.uniform(-r, r), yy + rnd.uniform(-r, r), 0.1, rnd.uniform(0.25, 0.5) * r, "rubble", sz=0.6)
        s.set_solid(xx - r, yy - r, xx + r, yy + r)
    s.set_solid(x0, y0, x1, y1)           # whole site is out of bounds for now (opened in Chapter 5)


def digger(s, x, y):
    s.box(x - 1.3, y - 1.2, x + 1.3, y - 0.6, 0, 0.55, "rubber_track")
    s.box(x - 1.3, y + 0.6, x + 1.3, y + 1.2, 0, 0.55, "rubber_track")
    s.box(x - 1.0, y - 0.6, x + 1.0, y + 0.6, 0.4, 1.0, "yellow_machine")
    s.box(x - 0.9, y - 0.5, x + 0.1, y + 0.5, 1.0, 2.1, "yellow_machine")
    s.box(x - 0.85, y - 0.48, x + 0.12, y + 0.48, 1.2, 1.95, "glass_office")
    s.box(x - 1.0, y - 0.5, x - 0.8, y + 0.5, 1.0, 1.3, "metal_dark")
    s.tube([(x + 0.2, y, 1.0), (x + 1.3, y, 2.4), (x + 2.6, y, 1.9)], 0.11, "yellow_machine")
    s.tube([(x + 2.6, y, 1.9), (x + 3.0, y, 1.3)], 0.09, "yellow_machine")
    s.box(x + 2.9, y - 0.5, x + 3.6, y + 0.5, 0.5, 1.2, "yellow_machine")
    s.box(x + 3.2, y - 0.5, x + 3.6, y + 0.5, 0.4, 0.55, "metal_dark")
    s.box(x - 0.2, y - 0.3, x + 0.2, y + 0.3, 2.1, 2.2, "lamp_amber")
    s.text("VAULTTECH", x - 0.1, y + 0.62, 0.75, 0.2, "ink_black", face="left", bold=True)
    s.set_solid(x - 1.3, y - 1.2, x + 3.7, y + 1.2)
    s.occluder(x - 1.3, y - 1.2, x + 3.7, y + 1.2, 2.5)


def hoarding_and_drums(s, rnd):
    """North side of the avenue stub: VaultTech hoarding wall with posters (cold), cable drum stack, portable toilet."""
    x0, x1, y = 2.0, 14.5, 15.0
    s.box(x0, y - 0.1, x1, y + 0.1, 0, 2.4, "vault_hoard")
    s.box(x0 - 0.05, y - 0.12, x1 + 0.05, y + 0.12, 2.4, 2.5, "gold_dark")
    for k in range(6):
        px = x0 + 0.6 + k * 2.1
        s.box(px, y + 0.1, px + 1.6, y + 0.13, 0.5, 2.1, rnd.choice(["poster_blue", "poster_yellow", "poster_blue"]))
    vault_v_logo(s, 5.0, y + 0.13, 1.3, 1.1)
    s.text("SMART CITY COMING SOON", 10.0, y + 0.14, 1.9, 0.28, "gold_bright", face="left", bold=True)
    s.text("VaultLink HyperFibre", 10.0, y + 0.14, 1.45, 0.2, "paint_white", face="left")
    s.set_solid(x0, y - 0.3, x1, y + 0.3)
    s.occluder(x0, y - 0.3, x1, y + 0.3, 2.6)
    # portaloo
    px, py = 7.4, 16.6
    s.box(px, py, px + 1.3, py + 1.2, 0, 2.3, "vault_cold")
    s.box(px, py + 1.2, px + 1.3, py + 1.24, 0.05, 2.1, "sign_blue")
    s.box(px + 0.2, py + 1.24, px + 1.1, py + 1.27, 0.2, 1.9, "wood_blue")
    s.set_solid(px, py, px + 1.3, py + 1.24)
    s.occluder(px, py, px + 1.3, py + 1.24, 2.4)
    for (x, y2) in ((4.2, 16.7), (5.3, 17.0)):
        cable_drum(s, x, y2)


def street_dressing(s, rnd):
    """Lamps, bins, hydrant, bunting, washing lines (kept sparse: dense detail fills the 624-slot tile window)."""
    for x in (19.0, 38.0, 57.0):
        lamp_curved(s, x, 19.1, arm="y")
    for (x, y) in ((28.0, 26.2), (44.0, 25.8)):
        trash_can(s, x, y)
    hydrant(s, 40.0, 25.4)
    newspaper_box(s, 17.4, 25.6, "sign_blue")
    poles = [(27.0, 25.9), (58.5, 25.9)]
    for (px, py) in poles:
        pole(s, px, py, 4.6)
        cloth_line(s, px, 18.1, 4.8, px, py, 4.5, 6, rnd)
    bunting(s, 25.5, 18.15, 4.3, 34.0, 18.15, 4.3, 9, rnd, sag=0.15)
    for (x, y) in ((17.7, 19.2), (45.6, 19.1), (55.1, 19.2)):
        potted_plant(s, x, y, "flowers")
    crate_stack(s, 26.0, 19.0, 2)
    for (x, y) in ((17.0, 24.9), (36.0, 19.8), (49.0, 24.8)):
        weeds(s, x, y, 3, rnd)


def ground(s, rnd):
    """Floor layer: slabs base, avenue stub + trench, cobble street, Baker's Lane, pavements, yard, meadow."""
    s.box(0, 6.0, 68.0, 62.0, -0.4, -0.04, "slab_flat", layer="floor")     # base only under the walkable part of the map
    s.box(0, 18.5, 11.3, 25.5, -0.1, -0.02, "asphalt", layer="floor")
    s.box(13.3, 18.5, 14.5, 25.5, -0.1, -0.02, "asphalt", layer="floor")
    s.box(11.3, 18.5, 13.3, 25.5, -0.6, -0.55, "mud", layer="floor")
    for (a, b, c, d) in ((11.3, 18.5, 11.36, 25.5), (13.24, 18.5, 13.3, 25.5), (11.3, 18.5, 13.3, 18.56), (11.3, 25.44, 13.3, 25.5)):
        s.box(a, b, c, d, -0.55, -0.02, "soil", layer="floor")
    s.set_solid(11.3, 18.5, 13.3, 25.5)
    s.box(14.5, 19.5, 68.0, 24.5, -0.1, -0.02, "cobble", layer="floor")
    s.box(15.7, 19.5, 68.0, 19.62, -0.1, 0.05, "curb", layer="floor")
    s.box(15.7, 24.38, 50.0, 24.5, -0.1, 0.05, "curb", layer="floor")
    s.box(55.0, 24.38, 68.0, 24.5, -0.1, 0.05, "curb", layer="floor")
    for x in range(0, 10, 3):
        s.box(x + 0.5, 21.95, x + 1.9, 22.05, -0.02, -0.01, "paint_yellow", layer="floor")
    # pavements
    s.box(0, 14.5, 15.7, 18.5, -0.1, 0.0, "paving_flat", layer="floor")
    s.box(0, 25.5, 16.0, 27.4, -0.1, 0.0, "paving_flat", layer="floor")
    s.box(15.7, 18.0, 68.0, 19.5, -0.1, 0.0, "paving_flat", layer="floor")
    s.box(16.0, 24.5, 50.0, 26.2, -0.1, 0.0, "paving_flat", layer="floor")
    s.box(55.0, 24.5, 68.0, 26.2, -0.1, 0.0, "paving_flat", layer="floor")
    # Baker's Lane (N-S), cobbles with pavements either side
    s.box(50.0, 24.5, 55.0, 62.0, -0.1, -0.02, "cobble", layer="floor")
    s.box(49.2, 26.2, 50.0, 62.0, -0.1, 0.0, "paving_flat", layer="floor")
    s.box(55.0, 26.2, 55.8, 40.0, -0.1, 0.0, "paving_flat", layer="floor")
    # alley north between Valdez house and the laundromat (cobbles), the pocket square, the alley between houses 4 and 5
    s.box(21.0, 8.0, 25.5, 18.0, -0.1, -0.01, "cobble", layer="floor")
    s.box(47.0, 12.0, 53.0, 18.0, -0.1, 0.0, "plaza_stone", layer="floor")
    s.box(57.5, 10.0, 61.0, 18.0, -0.1, -0.01, "cobble", layer="floor")
    # yard
    s.box(34.0, 6.0, 40.5, 18.0, -0.1, 0.01, "path_dirt", layer="floor")
    s.box(34.0, 15.5, 40.5, 18.0, 0.01, 0.02, "cobble", layer="floor")
    # a few cracks
    for _ in range(8):
        x, y = rnd.uniform(16, 67), rnd.uniform(19.8, 24.2)
        s.box(x, y, x + rnd.uniform(0.3, 0.8), y + rnd.uniform(0.1, 0.25), 0.0, 0.006 + rnd.random() * 0.004, "plaster_stain", layer="floor")
    for x in (26.5, 42.0):
        s.box(x, 24.0, x + 0.6, 24.4, 0.0, 0.015, "metal_dark", layer="floor")
    # south zone: chess plaza, pond park grass, meadow grass, court slab area
    s.box(29.5, 26.2, 35.0, 32.0, -0.1, 0.0, "plaza_stone", layer="floor")
    s.box(16.0, 26.2, 17.0, 40.0, -0.1, 0.0, "slab_flat", layer="floor")
    s.box(17.0, 40.0, 49.2, H, -0.1, 0.0, "grass_flat", layer="floor")
    s.box(35.0, 26.2, 49.2, 40.0, -0.1, 0.0, "grass_flat", layer="floor")
    s.box(55.8, 40.0, W, H, -0.1, 0.0, "grass_flat", layer="floor")
    s.box(68.0, 34.0, W, 40.0, -0.1, 0.0, "grass_flat", layer="floor")
    s.box(0, 34.5, 10.5, H, -0.1, 0.0, "grass_flat", layer="floor")
    s.box(55.8, 26.2, 68.0, 40.0, -0.1, 0.0, "slab_flat", layer="floor")
    # dirt paths: garden -> meadow -> cottages -> lane, and through the orchard
    for (a, b, c, d) in ((23.0, 40.0, 24.2, 52.0), (23.0, 52.0, 49.2, 53.2), (35.0, 40.0, 36.2, 52.0), (55.8, 50.0, 66.0, 51.2), (60.0, 40.0, 61.2, 62.0)):
        s.box(a, b, c, d, 0.0, 0.012, "path_dirt", layer="floor")


def pond_park(s, x0, y0, x1, y1, rnd):
    """Low pond park: water, stone rim, reeds, benches, flower beds."""
    s.box(x0 + 1.5, y0 + 1.5, x1 - 1.5, y1 - 1.5, -0.3, 0.004, "pond_edge", layer="floor")
    s.box(x0 + 1.9, y0 + 1.9, x1 - 1.9, y1 - 1.9, -0.3, 0.008, "pond_flat", layer="floor")
    s.set_solid(x0 + 1.5, y0 + 1.5, x1 - 1.5, y1 - 1.5)
    for k in range(8):
        px = rnd.uniform(x0 + 2, x1 - 2)
        s.sphere(px, y1 - 1.7, 0.2, 0.1, "leaves", sz=2.5)
    bench_along_x(s, x0 + 2.0, x0 + 4.0, y1 - 0.6)
    bench_along_x(s, x1 - 4.0, x1 - 2.0, y1 - 0.6)
    flower_bed(s, x0 + 0.2, y0 + 0.2, x0 + 2.2, y0 + 1.0, rnd)
    flower_bed(s, x1 - 2.2, y0 + 0.2, x1 - 0.2, y0 + 1.0, rnd)
    shrub(s, x0 + 0.5, y1 - 0.5, 0.5, "leaves_light")


def cottage(s, x, y, name="1Story_GableRoof_Mat", colours="cream", scale=2.1):
    """Detached house west of Baker's Lane (facade towards +x), from the CC0 Quaternius model. Returns the footprint."""
    return s.model(name, x, y, front="right", colours=colours, scale=scale)


def orchard(s, x0, y0, x1, y1, rnd):
    for (x, y) in ((x0 + 2, y0 + 3), (x0 + 6, y0 + 3), (x0 + 10, y0 + 3), (x0 + 2, y0 + 9), (x0 + 6, y0 + 9), (x0 + 10, y0 + 9)):
        s.cyl(x, y, 0, 1.3, 0.09, "trunk", verts=8)
        for (dx, dy, dz, r) in ((0, 0, 1.9, 0.75), (0.5, 0.2, 1.6, 0.5), (-0.4, 0.3, 1.7, 0.5)):
            s.sphere(x + dx, y + dy, dz, r, "leaves_light")
        for _ in range(4):
            s.sphere(x + rnd.uniform(-0.6, 0.6), y + rnd.uniform(-0.6, 0.6), 1.5 + rnd.random() * 0.5, 0.07, "apple_red")
        s.set_solid(x - 0.25, y - 0.25, x + 0.25, y + 0.25)
        s.occluder(x - 0.9, y - 0.9, x + 0.9, y + 0.9, 2.8)
    for (x, y) in ((x0 + 1, y0 + 14), (x0 + 5, y0 + 15), (x0 + 8, y0 + 14)):                 # allotment beds
        s.box(x, y, x + 2.4, y + 3.0, 0, 0.35, "wood")
        s.box(x + 0.1, y + 0.1, x + 2.3, y + 2.9, 0.33, 0.38, "soil")
        for k in range(4):
            s.sphere(x + 0.5 + 0.5 * k, y + 1.5, 0.55, 0.2, "cabbage", sz=0.7)
        s.set_solid(x, y, x + 2.4, y + 3.0)
    bench_along_x(s, x0 + 4.0, x0 + 6.0, y0 + 6.5)


def meadow(s, x0, y0, x1, y1, rnd):
    for (x, y) in ((x0 + 3, y0 + 3), (x0 + 12, y0 + 9), (x0 + 5, y0 + 15), (x0 + 15, y0 + 17)):
        s.cyl(x, y, 0, 1.5, 0.1, "trunk", verts=8)
        for (dx, dy, dz, r) in ((0, 0, 2.3, 1.0), (0.6, 0.3, 2.0, 0.7), (-0.5, 0.4, 2.1, 0.7)):
            s.sphere(x + dx, y + dy, dz, r, "leaves")
        s.set_solid(x - 0.25, y - 0.25, x + 0.25, y + 0.25)
        s.occluder(x - 1.2, y - 1.2, x + 1.2, y + 1.2, 3.5)
    for (x, y) in ((x0 + 8, y0 + 3), (x0 + 8, y0 + 17)):
        bench_along_x(s, x, x + 1.8, y)
    for _ in range(14):
        weeds(s, rnd.uniform(x0, x1), rnd.uniform(y0, y1), 2, rnd)
    for (x, y) in ((x0 + 1, y0 + 9), (x0 + 14, y0 + 2)):
        flower_bed(s, x, y, x + 2.0, y + 0.9, rnd)


def old_block():
    oy = 175
    s = Scene("old_block", "Old Block", W, H, origin_x=H * 16 + 16, origin_y=oy,
              img_w=(W + H) * 16 + 32, img_h=oy + (W + H) * 8 + 16)
    rnd = R(1931)
    ground(s, rnd)
    # ---- zone A: cable works (cold), the arch ----
    hoarding_and_drums(s, rnd)
    cable_works(s, rnd)
    sneak_fence_and_bushes(s, rnd)
    arch(s)
    # ---- north row, spread out with alleys and a square between the buildings ----
    row_house(s, 16.5, 21.0, FY, 3, "plaster_terra", 18.6, door_mat="wood_green", seed=11, shutters=True, extras=("stain",))
    balcony(s, 17.2, 19.9, FY, 6.0)
    s.box(18.2, FY + 0.3, 18.6, FY + 0.5, 6.1, 6.55, "brass")
    s.sphere(18.4, FY + 0.4, 6.6, 0.1, "cloth_green")                                   # Captain's cage
    # alley (21..25.5): Teo's den = a tiny lean-to shed, a barrel
    s.box(22.2, 9.2, 24.4, 11.2, 0, 1.7, "boards")
    s.box(22.0, 9.0, 24.6, 11.4, 1.7, 1.8, "tin_roof")
    s.cyl(22.0, 14.0, 0, 0.9, 0.3, "barrel_blue", verts=12)
    s.occluder(22.0, 9.0, 24.6, 11.4, 1.9)
    laundromat(s, 25.5, 34.0, FY)
    mural_east_wall(s, 34.0, 10.0, 18.0, 0.6)
    backroom_annex(s, 34.4, 9.5, 37.4, 14.5)
    fence_wood(s, 34.0, 36.2, 17.4, h=1.3)
    fence_wood(s, 37.9, 40.5, 17.4, h=1.3)
    s.box(36.2, 17.3, 36.35, 17.5, 0, 1.5, "wood_dark")
    s.box(37.75, 17.3, 37.9, 17.5, 0, 1.5, "wood_dark")
    crate_stack(s, 38.4, 11.0, 3)
    crate_stack(s, 38.4, 12.0, 2)
    crate_stack(s, 38.7, 9.2, 2)
    pole(s, 39.3, 14.8, 3.8)
    pole(s, 39.3, 7.2, 3.8)
    cloth_line(s, 39.3, 7.2, 3.5, 39.3, 14.8, 3.5, 8, rnd)
    s.cyl(35.8, 16.0, 0, 0.12, 0.45, "cloth_red", verts=14)
    s.sphere(35.8, 16.0, 0.25, 0.22, "plaster_ochre", sz=0.7, sx=1.4)                   # Duchess (placeholder)
    trash_can(s, 35.0, 11.2)
    bakery(s, 40.5, 47.0, FY)
    # pocket square (47..53): stone basin, benches, poster wall for Mia's posters
    s.cyl(50.0, 14.5, 0, 0.5, 1.2, "stone", verts=20)
    s.cyl(50.0, 14.5, 0.5, 0.52, 1.0, "pond_flat", verts=20)
    s.cyl(50.0, 14.5, 0.5, 1.4, 0.15, "stone", verts=10)
    s.occluder(48.7, 13.2, 51.3, 15.8, 1.5)
    bench_along_x(s, 47.6, 49.4, 17.2)
    bench_along_x(s, 50.6, 52.4, 17.2)
    s.box(52.2, 12.4, 52.9, 12.5, 0, 1.7, "wood_dark")
    s.box(52.0, 12.5, 52.95, 13.5, 0.7, 1.6, "poster_yellow")
    row_house(s, 53.0, 57.5, FY, 3, "plaster_blue", 55.1, door_mat="wood_red", seed=12, extras=("dish", "stain"))
    row_house(s, 61.0, 65.5, FY, 2, "plaster_teal", 63.1, door_mat="wood_green", seed=13, extras=("ac",))
    # ---- street end: Rosa's stall, Teo's door ramp ----
    rosas_stall(s, 63.2, 22.2)
    s.wedge(60.2, 24.5, 61.6, 26.3, 0.75, 0.0, "y", "wood_green")
    s.box(60.2, 24.3, 61.6, 24.5, 0, 0.75, "brick_red")
    # ---- south side: garden, chess, pond park ----
    garden(s, 17.0, 27.0, 29.0, 40.0, rnd)
    plane_tree(s, 31.0, 36.0, 1.0)
    chess_table(s, 32.2, 28.2)
    pond_park(s, 36.0, 28.0, 47.0, 37.0, rnd)
    # ---- Baker's Lane: lamps and detached cottages on its west side (facades towards +x), spaced out ----
    for y in (30.0, 44.0, 58.0):
        lamp_curved(s, 49.6, y, arm="y")
    cottage(s, 49.0, 41.0, colours="cream")
    cottage(s, 49.0, 49.5, name="2Story_GableRoof_Mat", colours="blue")
    cottage(s, 49.0, 57.0, colours="orange")
    # ---- east of the lane: court, orchard ----
    court(s, 56.0, 28.5, 67.0, 37.5, rnd)
    orchard(s, 56.0, 40.0, 67.0, 62.0, rnd)
    orchard(s, 68.0, 40.0, 79.0, 62.0, rnd)                    # second orchard / allotment block east of the first (more to walk)
    meadow(s, 17.0, 41.0, 37.0, 62.0, rnd)
    # ---- the demolition site ----
    demolition_site(s, 68.0, 4.0, 80.0, 34.0, rnd)
    street_dressing(s, rnd)
    hedge(s, 17.0, 49.0, 63.0, 0.9)
    chain_link(s, 0, 10.5, 34.5, h=1.6)
    hedge(s, 0.5, 10.0, 36.0, 1.0)
    # collision borders
    s.set_solid(0, 0, 0.5, H)
    s.set_solid(0, 0, W, 0.5)
    s.set_solid(0, H - 0.5, W, H)
    s.set_solid(W - 0.5, 0, W, H)
    s.set_solid(0, 18.0, 0.6, 34.0, False)
    s.set_solid(0, 0, 16.0, 14.4)
    s.set_solid(0, 34.5, 16.0, H)
    # rear zone behind the north row is closed; alleys, yard and pocket square stay open (their props keep their own solids)
    keep = [(21.0, 8.0, 25.5, 17.9), (34.0, 6.0, 40.5, 17.9), (47.0, 12.0, 53.0, 17.9), (57.5, 10.0, 61.0, 17.9)]
    saved = [row[:] for row in s.solid]
    s.set_solid(16.0, 0, 68.0, 17.9)
    r = sc.SOLID_RES
    for (a, b, c, d) in keep:
        for sy in range(int(b * r), int(d * r)):
            for sx in range(int(a * r), int(c * r)):
                s.solid[sy][sx] = saved[sy][sx]
    s.sun_strength = 4.0
    return s


LANE_CELLS = [(10.9, 30.35, 17.0, 31.05), (16.4, 27.0, 17.1, 31.05)]
