"""s77 PROPOSAL: the Old Block sneak route goes through the sewer (replaces fence flap + bush lane). Nothing here is part of the game.

Scenes (registered in-process by render.py only):
  sewer      "Old Block Sewer": 30 x 9 cell cutaway tunnel, west ladder (from the City Centre) and east ladder (to Old Block)
  cc_a / cc_b   City Centre east end: variant A = crooked road manhole with Teo's chalk arrow + cone,
                variant B = Water Board hatch on the river walk (open, ladder rails sticking out)
  ob_open / ob_closed   Old Block, Cobble Street just inside the arch: the exit manhole, cover slid aside / cover closed
Everything is built from the real scene.py primitives and helpers; new materials are only in NEW_MATERIALS (this file).
Units: x, y in map cells (1 cell = 0.75 m), z in metres.
"""
import math
import os
import random
import sys

TOOLS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import scene as sc  # noqa: E402
from scene import Scene, CELL_M, cone, lamp_curved  # noqa: E402

M = 1 / CELL_M            # metres -> cells

NEW_MATERIALS = {
    "sw_brick": dict(kind="brick", c="#7a5e4a", c2="#675040", mortar="#40493c", bw=0.26, bh=0.09, mortar_size=0.012, rough=0.9),
    "sw_brick_dark": dict(kind="brick", c="#5c4638", c2="#4c392e", mortar="#303a30", bw=0.26, bh=0.09, mortar_size=0.012, rough=0.9),
    "sw_brick_lit": dict(kind="brick", c="#a58a68", c2="#927856", mortar="#6e6552", bw=0.26, bh=0.09, mortar_size=0.012, rough=0.9),
    "sw_stone": dict(kind="paving_grit", c="#7c7d72", c2="#6c6d62", mortar="#33372e", bw=0.7, bh=0.7, mortar_size=0.02, crack_scale=0.8),
    "sw_stone_clean": dict(kind="paving_grit", c="#8e8c7c", c2="#7e7c6c", mortar="#3a3d32", bw=0.7, bh=0.7, mortar_size=0.02, crack_scale=0.8),
    "sw_cap": dict(kind="noise", c="#8e9088", c2="#7e8078", scale=10),
    "water_sewer": dict(kind="water", c="#26342c", c2="#5a6e52", rough=0.12, depth_scale=0.5, wave_scale=1.5, bump=0.12, ior=1.2,
                        cx=11.25, cy=-2.85, hx=11.4, hy=0.95, shape="box"),
    "sw_bed": dict(c="#2a2e2a", rough=0.9),
    "sw_moss": dict(kind="noise", c="#4c6a30", c2="#3a5626", scale=7, rough=0.95),
    "sw_slime": dict(c="#7f9a3c", rough=0.3),
    "sw_puddle": dict(c="#26363a", rough=0.05),
    "sw_pipe_green": dict(c="#4d7260", rough=0.45, metal=0.5),
    "sw_pipe_rust": dict(c="#8a4e2c", rough=0.6, metal=0.4),
    "sw_iron": dict(c="#34363a", rough=0.5, metal=0.7),
    "sw_light_patch": dict(c="#d8dcc0", emit=0.10, emit_c="#d8dcc0"),
    "sw_pool1": dict(c="#9aa890", emit=0.05, emit_c="#9aa890"),
    "sw_pool2": dict(c="#c4cdb4", emit=0.09, emit_c="#c4cdb4"),
    "sw_pool3": dict(c="#e4e8d4", emit=0.14, emit_c="#e4e8d4"),
    "sw_shaft_glow": dict(c="#b9cbd8", emit=0.35, emit_c="#b9cbd8"),
    "sw_shaft_glow2": dict(c="#dce8f0", emit=0.8, emit_c="#dce8f0"),
    "sw_rat": dict(c="#4a4038", rough=0.9),
    "sw_rat_tail": dict(c="#c48a86", rough=0.9),
    "sw_foam": dict(c="#cfd6c4", rough=0.9),
    "sw_cover": dict(c="#4b4a46", rough=0.55, metal=0.5),
    "sw_cover_rim": dict(c="#4a4944", rough=0.6, metal=0.5),
    "sw_void": dict(c="#07090a", rough=1.0),
    "sw_chalk": dict(c="#f4f1e6", rough=0.95),
    "sw_hatch": dict(c="#a9afb8", rough=0.45, metal=0.5),
    "sw_hatch_paint": dict(c="#c8a02c", rough=0.6),
}


# ---------------------------------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------------------------------
def manhole_ring(s, x, y, layer="floor", z=0.0):
    """Iron frame ring + dark well (open manhole) in the ground. z = ground height (top of the paving)."""
    s.cyl(x, y, z + 0.004, z + 0.03, 0.62, "sw_cover_rim", layer=layer, verts=32)          # frame ring (outer)
    s.cyl(x, y, z + 0.03, z + 0.05, 0.5, "sw_void", layer=layer, verts=32)                   # dark well (distinct top height: no coplanar faces)


def manhole_cover(s, x, y, layer="floor", z=0.0, rot=0.0, lift=0.0):
    """Round iron cover with a cross pattern (made of thin bars). lift = extra height (cover resting on the frame)."""
    base = z + 0.034 + lift
    s.cyl(x, y, base, base + 0.03, 0.55, "sw_cover", layer=layer, verts=32)
    for k in range(4):                                                                       # raised cross bars
        a = math.radians(rot + k * 45)
        dx, dy = math.cos(a) * 0.46, math.sin(a) * 0.46
        s.tube([(x - dx, y - dy, base + 0.04), (x + dx, y + dy, base + 0.04)], 0.018, "sw_cover_rim", layer=layer)
    s.cyl(x, y, base + 0.03, base + 0.045, 0.1, "sw_cover_rim", layer=layer, verts=12)       # lifting eye


def ladder_rungs(s, x, y, z0, z1, width=0.5, depth=0.0, axis="x", step=0.28, thick=1.0):
    """Ladder: two rails + rungs. axis 'x': ladder plane normal is +y (against a wall at y), rails at x +- width/2."""
    th = 0.05 * thick
    for dx in (-width / 2, width / 2):
        s.box(x + dx - th, y - th, x + dx + th, y + th, z0, z1, "sw_iron")
    z = z0 + 0.2
    while z < z1:
        s.box(x - width / 2, y - th * 0.7, x + width / 2, y + th * 0.7, z - 0.025 * thick, z + 0.025 * thick, "sw_iron")
        z += step


def rat(s, x, y, ang=0.0, big=1.0):
    """A cartoon-sized rat (0.4 m): body ellipsoid, head, ears, pink tail."""
    ca, sa = math.cos(ang), math.sin(ang)
    s.sphere(x, y, 0.1 * big, 0.17 * big * M, "sw_rat", sz=0.7, sx=1.7)
    hx, hy = x + ca * 0.3 * big * M * 1.2, y + sa * 0.3 * big * M * 1.2
    s.sphere(hx, hy, 0.12 * big, 0.09 * big * M * 1.3, "sw_rat", sz=0.8)
    s.sphere(hx - sa * 0.05, hy + ca * 0.05, 0.2 * big, 0.04 * big, "sw_rat_tail")
    s.sphere(hx + sa * 0.05, hy - ca * 0.05, 0.2 * big, 0.04 * big, "sw_rat_tail")
    tx, ty = x - ca * 0.34 * big * M * 1.2, y - sa * 0.34 * big * M * 1.2
    s.tube([(x - ca * 0.2 * big * M, y - sa * 0.2 * big * M, 0.06), (tx, ty, 0.03), (tx - ca * 0.2 * M + sa * 0.1 * M, ty - sa * 0.2 * M - ca * 0.1 * M, 0.02)],
           0.012, "sw_rat_tail")


def shaft_halfpipe(s, cx, r, ztop, n=14):
    """Back half of a round brick shaft behind the back wall (y < 0), seen from inside (cutaway). Bands get lighter towards the top."""
    bands = [(0.0, 3.2, "sw_brick"), (3.2, 3.9, "sw_brick_lit"), (3.9, 4.55, "sw_shaft_glow"), (4.55, ztop, "sw_shaft_glow2")]
    pts = [(cx + r * math.cos(math.pi * i / n), -r * math.sin(math.pi * i / n)) for i in range(n + 1)]
    for (z0, z1, mat) in bands:
        for (a, b) in zip(pts, pts[1:]):
            s.poly([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], mat)
    # floor of the shaft + the pool of daylight that falls down it (spills onto the walkway)
    s.box(cx - r, -r, cx + r, 0.0, -0.1, 0.0, "sw_stone", layer="floor")
    s.cyl(cx, 0.0, 0.003, 0.008, r * 0.95, "sw_pool1", layer="floor", verts=28)
    s.cyl(cx, 0.0, 0.008, 0.012, r * 0.68, "sw_pool2", layer="floor", verts=28)
    s.cyl(cx, 0.0, 0.012, 0.016, r * 0.38, "sw_pool3", layer="floor", verts=24)
    # ladder on the shaft's back wall
    ladder_rungs(s, cx, -r + 0.07, 0.0, 5.0, width=0.5)
    s.box(cx - 0.14, -r + 0.02, cx + 0.14, -r + 0.14, 0.0, 0.5, "sw_iron")          # no-op stub (ladder foot bracket)
    # warm-white point light from the top of the shaft
    s.point_light(cx, -0.4, 4.4, 120, colour=(0.85, 0.92, 1.0), radius=0.6)


def cage_lamp(s, x, y=0.0, z=2.15):
    """Caged amber wall lamp on the back wall (faces +y) + its light."""
    s.box(x - 0.18, y, x + 0.18, y + 0.22, z, z + 0.42, "sw_iron")
    s.box(x - 0.14, y + 0.2, x + 0.14, y + 0.3, z + 0.05, z + 0.37, "lamp_amber")
    for k in range(3):
        s.box(x - 0.17 + k * 0.17, y + 0.28, x - 0.15 + k * 0.17, y + 0.33, z + 0.02, z + 0.4, "sw_iron")
    s.lamps.append((x, y + 1.2))
    s.point_light(x, y + 0.9, z + 0.2, 75, colour=(1.0, 0.72, 0.42), radius=0.25)


def grate_bridge(s, x0, x1, y0=2.5, y1=5.1):
    """Iron grate foot bridge over the channel: bars along y, two side rails, brick abutments are the walkway edges."""
    xx = x0 + 0.05
    while xx < x1 - 0.05:
        s.box(xx, y0 - 0.05, xx + 0.1, y1 + 0.05, -0.02, 0.07, "sw_iron")
        xx += 0.26
    for y in (y0 - 0.02, y1 - 0.02):                                                                  # side girders
        s.box(x0, y, x1, y + 0.09, -0.12, 0.1, "sw_iron")
    for x in (x0 + 0.02, x1 - 0.12):
        s.box(x, y0 - 0.05, x + 0.1, y1 + 0.05, -0.02, 0.07, "sw_iron")
    # handrails on both sides (thin tubes on posts), low so they do not hide the walkway
    for y in (y0 + 0.08, y1 - 0.1):
        s.tube([(x0 + 0.05, y, 0.85), (x1 - 0.05, y, 0.85)], 0.025, "sw_iron")
        for x in (x0 + 0.1, (x0 + x1) / 2, x1 - 0.1):
            s.cyl(x, y, 0.07, 0.86, 0.022, "sw_iron", verts=6)


# ---------------------------------------------------------------------------------------------------------------------
# THE SEWER (map "sewer", 30 x 9 cells)
# ---------------------------------------------------------------------------------------------------------------------
W_S, H_S = 30, 9
WEST_SHAFT, EAST_SHAFT = 2.4, 27.4           # shaft centres (x); shaft radius 1.4
CH0, CH1 = 2.5, 5.1                          # water channel y range
COLLAPSE = (13.0, 16.4)                      # back walkway blocked here (the walk crosses the channel by the two bridges)
BRIDGES = ((10.2, 12.4), (17.2, 19.4))
NOOK = (21.2, 25.2)                          # Mothball's nook on the back walkway


def sewer():
    oy = 215
    s = Scene("sewer", "Old Block Sewer", W_S, H_S, origin_x=H_S * 16 + 24, origin_y=oy, img_w=(W_S + H_S) * 16 + 48,
              img_h=oy + (W_S + H_S) * 8 + 36)
    s.sun = False
    s.world = (0.46, 0.58, 0.54)
    s.world_strength = 0.38
    s.fill = (0.82, 0.96, 0.92)
    s.fill_energy = 1.15
    rnd = random.Random(77)
    r = 1.4

    # ---- floors: back walkway, front walkway, channel bed + water -------------------------------------------------
    s.box(0, 0, W_S, CH0, -0.1, 0.0, "sw_stone", layer="floor")
    s.box(0, CH1, W_S, H_S, -0.1, 0.0, "sw_stone", layer="floor")
    s.box(0, CH0, W_S, CH1, -1.1, -0.9, "sw_bed", layer="floor")
    s.box(0, CH0 - 0.001, W_S, CH1 + 0.001, -0.9, -0.55, "water_sewer", layer="floor")
    s.box(0, CH0 - 0.04, W_S, CH0, -0.62, 0.0, "sw_brick_dark", layer="floor")                       # channel wall (faces +y, visible)
    # tide-line moss and slime on the channel wall
    for x in (4.5, 9.0, 14.2, 22.0, 26.5):
        s.box(x, CH0 - 0.05, x + rnd.uniform(0.8, 1.6), CH0 - 0.04, -0.58, -0.4, "sw_moss", layer="floor")
    # swept-clean dry stones in the nook (the walkway is darker everywhere else)
    s.box(NOOK[0] - 0.2, 0.3, NOOK[1] + 0.2, CH0 - 0.1, 0.0, 0.012, "sw_stone_clean", layer="floor")
    # damp patches / puddles (distinct heights, never coplanar)
    for (x, y, rx, ry, h) in ((7.5, 1.7, 0.7, 0.35, 0.004), (20.0, 1.2, 0.5, 0.3, 0.006), (14.5, 6.9, 0.8, 0.4, 0.005), (22.5, 7.4, 0.6, 0.3, 0.008),
                              (6.0, 7.6, 0.5, 0.3, 0.007)):
        s.sphere(x, y, h - 0.01, 1.0, "sw_puddle", layer="floor", sz=0.02, sx=rx, sy=ry)

    # ---- back wall (y 0) with the two shaft gaps, pilasters, corbelled haunch ---------------------------------------
    wh = 2.5
    gaps = [(WEST_SHAFT - r, WEST_SHAFT + r), (EAST_SHAFT - r, EAST_SHAFT + r)]
    segs = [(-0.5, gaps[0][0]), (gaps[0][1], gaps[1][0]), (gaps[1][1], W_S + 0.0)]
    for (a, b) in segs:
        s.box(a, -0.6, b, 0.0, 0.0, wh, "sw_brick")
        for k, (dz, dy) in enumerate(((0.0, 0.0), (0.18, 0.14), (0.36, 0.28), (0.54, 0.40))):     # corbel courses = the vault springing
            s.box(a, -0.6, b, dy, wh + dz, wh + dz + 0.18, "sw_brick_dark" if k % 2 else "sw_brick")
        s.box(a, -0.6, b, 0.46, wh + 0.72, wh + 0.8, "sw_cap")                                      # cut face of the vault, capped
        s.set_solid(a, -0.6, b, 0.45)
    s.occluder(-0.5, -0.6, W_S, 0.1, 3.3)
    for x in (7.2, 12.6, 19.0, 25.0):                                                                # pilasters
        if any(g[0] - 0.3 < x < g[1] + 0.3 for g in gaps):
            continue
        s.box(x, 0.0, x + 0.55, 0.3, 0.0, 2.55, "sw_brick_dark")
        s.box(x - 0.05, -0.05, x + 0.6, 0.35, 2.4, 2.55, "sw_cap")
        s.box(x - 0.05, 0.0, x + 0.6, 0.35, 0.0, 0.3, "sw_cap")
    # ---- west wall (x 0, faces +x, visible) with a stone plinth; east end low stub ------------------------------------
    # the end wall is a cross-section of the barrel vault: its top edge follows the arch (stepped strips, brick voussoir band + cap)
    ys = -0.6
    while ys < H_S - 0.4 - 1e-6:
        y1 = min(ys + 0.5, H_S - 0.4)
        u = (min(max((ys + y1) / 2, 0.0), H_S - 0.4)) / (H_S - 0.4)                  # 0 .. 1 across the tunnel
        top = wh + 0.3 + 1.05 * math.sin(math.pi * u) ** 0.8
        s.box(-0.6, ys, 0.0, y1, 0.0, top - 0.3, "sw_brick")
        s.box(-0.6, ys, 0.0, y1, top - 0.3, top - 0.12, "sw_brick_lit")                   # voussoir band
        s.box(-0.62, ys, 0.02, y1, top - 0.12, top, "sw_cap")
        ys = y1
    s.box(0.0, 0.4, 0.25, H_S - 0.4, 0.0, 0.22, "sw_cap")
    s.set_solid(-0.6, -0.6, 0.0, H_S)
    s.occluder(-0.6, -0.6, 0.1, H_S, 2.9)
    s.box(W_S, 0, W_S + 0.4, CH0, -0.1, 0.34, "sw_brick_dark")                                      # east end low stubs; a full plug closes the channel
    s.box(W_S, CH1, W_S + 0.4, H_S, -0.1, 0.34, "sw_brick_dark")
    s.box(W_S, CH0, W_S + 0.4, CH1, -1.1, 0.34, "sw_brick_dark")                                       # east end low stub
    s.box(0.0, H_S - 0.4, W_S, H_S, 0.0, 0.34, "sw_brick_dark")                                      # front parapet (low cutaway stub)
    s.box(0.0, H_S - 0.45, W_S, H_S - 0.4, 0.34, 0.4, "sw_cap")
    s.set_solid(0, H_S - 0.5, W_S, H_S)
    # the channel enters / leaves through round tunnel mouths in the end walls: shown as dark discs on the west wall

    # ---- shafts + ladders --------------------------------------------------------------------------------------------
    shaft_halfpipe(s, WEST_SHAFT, r, 5.2)
    shaft_halfpipe(s, EAST_SHAFT, r, 5.2)
    # painted direction on the wall by the east ladder, plate by the west one
    s.text("OLD BLOCK", 23.6, 0.05, 1.7, 0.34, "sw_chalk", face="left", bold=True)
    s.text(">>>", 23.6, 0.05, 1.28, 0.3, "sw_chalk", face="left", bold=True)
    s.box(4.4, 0.0, 5.7, 0.05, 1.35, 1.95, "sw_iron")
    s.text("WATER BOARD", 5.05, 0.08, 1.75, 0.15, "brass", face="left")
    s.text("No. 4  1931", 5.05, 0.08, 1.52, 0.15, "brass", face="left")

    # ---- pipes along the back wall, orange VaultLink cable, brackets ---------------------------------------------------
    s.tube([(3.9, 0.3, 2.0), (12.0, 0.3, 2.0), (22.4, 0.32, 2.0), (25.9, 0.3, 2.0)], 0.12, "sw_pipe_green")
    s.tube([(3.9, 0.2, 1.62), (11.0, 0.2, 1.62), (13.0, 0.25, 1.4), (25.9, 0.2, 1.62)], 0.065, "sw_pipe_rust")
    s.tube([(3.9, 0.17, 2.3), (26.0, 0.17, 2.3)], 0.055, "notice_orange")                                  # AURUM trunk 7 cable
    s.tube([(26.0, 0.17, 2.3), (26.2, -0.5, 2.45), (26.3, -1.0, 3.8), (26.35, -1.0, 5.2)], 0.055, "notice_orange")
    s.tube([(3.9, 0.17, 2.3), (3.8, -0.4, 2.45), (3.5, -0.95, 3.8), (3.45, -0.95, 5.2)], 0.055, "notice_orange")
    for x in (5.0, 8.2, 11.5, 14.5, 17.5, 20.5, 23.5):
        s.box(x, 0.0, x + 0.09, 0.3, 1.55, 2.38, "sw_iron")
    # an outfall pipe mouth with slime streak and drip (x 8.6)
    s.cyl(8.6, 0.0, 1.0, 1.1, 0.34, "sw_iron", axis="y", verts=20)
    s.cyl(8.6, 0.0, 1.0, 1.05, 0.26, "sw_void", axis="y", verts=20)
    s.box(8.35, 0.0, 8.85, 0.03, 0.0, 0.7, "sw_slime")
    s.sphere(8.62, 1.25, 0.55, 0.035, "sw_foam")                                                               # a falling drip
    s.cyl(8.62, 1.55, 0.015, 0.025, 0.3, "sw_puddle", layer="floor", verts=18)
    # ---- lamps ---------------------------------------------------------------------------------------------------------
    cage_lamp(s, 6.4)
    cage_lamp(s, 20.0)
    cage_lamp(s, 9.6, z=2.05)
    # light from a street grate above the walkway: stripes of daylight (the grate itself is above the cut)
    for k in range(5):
        xx = 11.6 + k * 0.5
        s.box(xx, 5.9, xx + 0.17, 8.2, 0.012, 0.02, "sw_light_patch", layer="floor")
    # ---- the collapse (back walkway blocked) --------------------------------------------------------------------------
    c0, c1 = COLLAPSE
    for (x, y, w, d, h) in ((13.2, 0.5, 1.0, 0.8, 0.5), (13.8, 1.1, 1.1, 0.8, 0.8), (14.8, 0.6, 0.9, 0.9, 0.62), (15.3, 1.4, 1.0, 0.7, 0.35),
                            (14.2, 1.9, 0.9, 0.55, 0.28), (13.1, 1.5, 0.6, 0.6, 0.3), (15.9, 0.5, 0.5, 0.6, 0.3)):
        s.box(x, y, x + w, y + d, 0.0, h, "sw_brick_dark" if (x * 3) % 2 < 1 else "sw_brick")
    s.sphere(14.7, 1.2, 0.0, 0.6, "mud", sz=0.3, sx=1.3)
    s.tube([(11.0, 0.2, 1.62), (13.0, 0.35, 1.5), (14.6, 1.0, 0.8), (15.4, 1.9, 0.55)], 0.065, "sw_pipe_rust")  # the broken pipe hangs down
    for (x, y) in ((13.6, 2.2), (16.1, 2.2)):
        s.box(x, y, x + 0.08, y + 0.08, 0.0, 0.7, "barrier_stripes")
    s.tube([(13.64, 2.24, 0.62), (16.14, 2.24, 0.62)], 0.012, "notice_orange")
    s.set_solid(c0, 0.45, c1, CH0 + 0.1)
    s.occluder(c0, 0.45, c1, 2.1, 0.9)
    # ---- bridges over the channel --------------------------------------------------------------------------------------
    for (a, b) in BRIDGES:
        grate_bridge(s, a, b)
    # ---- Mothball's nook: empty for now (brick niche frame, two hooks, a dead string of lights, a CLOSED sign) -------
    n0, n1 = NOOK
    for x in (n0, n1 - 0.55):
        s.box(x, 0.0, x + 0.55, 0.5, 0.0, 2.3, "sw_brick_lit")
        s.box(x - 0.06, -0.05, x + 0.61, 0.56, 2.3, 2.42, "sw_cap")
    s.box(n0, 0.0, n1, 0.5, 2.0, 2.3, "sw_brick_lit")                                                          # lintel (arch drawn as flat lintel + keystone)
    s.box(n0 + 1.6, 0.0, n0 + 2.4, 0.56, 2.0, 2.38, "sw_cap")
    s.box(n0 + 0.55, -0.05, n1 - 0.55, 0.08, 0.0, 2.0, "sw_brick_dark")                                       # dark back panel of the niche
    for x in (n0 + 0.9, n1 - 0.95):                                                                            # brass hooks
        s.box(x, 0.08, x + 0.07, 0.3, 1.7, 1.76, "brass")
        s.box(x, 0.24, x + 0.07, 0.3, 1.55, 1.76, "brass")
    s.tube([(n0 + 0.6, 0.12, 1.95), (n0 + 1.2, 0.12, 1.7), (n0 + 1.9, 0.12, 1.88), (n0 + 2.6, 0.12, 1.72), (n1 - 0.6, 0.12, 1.92)], 0.012, "sw_iron")
    for x, z in ((n0 + 1.2, 1.64), (n0 + 1.9, 1.82), (n0 + 2.6, 1.66)):
        s.sphere(x, 0.13, z, 0.05, "sw_chalk")
    s.box(n0 + 0.7, 0.3, n0 + 1.6, 0.34, 0.95, 1.6, "wood")                                                    # hanging sign "CLOSED"
    s.text("CLOSED", n0 + 1.15, 0.37, 1.18, 0.17, "ink_black", face="left", bold=True)
    s.sphere(n0 + 1.15, 0.37, 1.45, 0.05, "gold")                                                              # a little moon on it
    # ---- front walkway dressing (kept low: the camera is on this side) --------------------------------------------------
    s.box(21.0, 6.6, 22.0, 7.4, 0.0, 0.5, "wood")                                                               # crate
    s.box(21.1, 6.7, 21.9, 7.3, 0.5, 0.52, "wood_dark")
    s.set_solid(21.0, 6.6, 22.0, 7.4)
    s.occluder(21.0, 6.6, 22.0, 7.4, 0.55)
    s.cyl(24.8, 7.2, 0.0, 0.5, 0.32, "barrel_blue", verts=14)                                                    # bucket / drum
    s.cyl(24.8, 7.2, 0.5, 0.53, 0.28, "sw_puddle", verts=14)
    s.set_solid(24.4, 6.8, 25.2, 7.6)
    s.tube([(7.0, 7.4, 0.04), (7.8, 7.0, 0.06), (8.4, 7.5, 0.05), (7.8, 7.9, 0.04), (7.2, 7.6, 0.04)], 0.045, "notice_orange")   # coil of cable
    for (x, y) in ((6.2, 3.8), (7.0, 4.2), (17.0, 3.2), (24.0, 4.3)):
        s.cyl(x, y, -0.549, -0.54, 0.18, "sw_foam", layer="floor", verts=12)
    # ---- rats ------------------------------------------------------------------------------------------------------------
    rat(s, 10.0, 7.7, ang=math.radians(10))
    rat(s, 18.6, 1.0, ang=math.radians(190))
    rat(s, 28.2, 4.6, ang=math.radians(100), big=0.9)
    # ---- a hanging dead bulb and drips in the middle of the tunnel (they cast no vault, so a cable from the wall) ---------
    s.point_light(14.5, 4.0, 3.0, 55, colour=(0.7, 0.85, 0.8), radius=0.4)                                        # cold glow over the channel
    s.point_light(23.2, 2.0, 2.2, 40, colour=(1.0, 0.8, 0.55), radius=0.3)                                        # warm spill on the nook
    s.point_light(4.5, 6.0, 3.0, 40, colour=(0.8, 0.9, 1.0), radius=0.4)
    s.point_light(26.0, 6.0, 3.0, 40, colour=(0.8, 0.9, 1.0), radius=0.4)
    # ---- collision borders + exits ---------------------------------------------------------------------------------------
    s.set_solid(0, CH0, W_S, CH1)                    # the channel (bridges re-open it)
    for (a, b) in BRIDGES:
        s.set_solid(a + 0.1, CH0, b - 0.1, CH1, False)
    s.set_solid(W_S - 0.5, 0, W_S, H_S)
    s.warp(WEST_SHAFT - 0.7, -1.2, WEST_SHAFT + 0.7, -0.4, "city_centre", 0, 0, "down")           # (target only documents the idea)
    s.warp(EAST_SHAFT - 0.7, -1.2, EAST_SHAFT + 0.7, -0.4, "old_block", 0, 0, "down")
    return s


# ---------------------------------------------------------------------------------------------------------------------
# CITY CENTRE variants
# ---------------------------------------------------------------------------------------------------------------------
def chalk_arrow(s, x, y, ang_deg, length=1.6):
    """A hand-drawn chalk arrow on the asphalt (thin flat bars, floor layer)."""
    a = math.radians(ang_deg)
    ca, sa = math.cos(a), math.sin(a)
    z0 = -0.012
    def bar(px0, py0, px1, py1, w=0.07):
        nx, ny = -(py1 - py0), (px1 - px0)
        n = math.hypot(nx, ny)
        nx, ny = nx / n * w, ny / n * w
        s.poly([(px0 + nx, py0 + ny, z0), (px1 + nx, py1 + ny, z0), (px1 - nx, py1 - ny, z0), (px0 - nx, py0 - ny, z0)], "sw_chalk", layer="floor")
    x0, y0 = x - ca * length / 2, y - sa * length / 2
    x1, y1 = x + ca * length / 2, y + sa * length / 2
    bar(x0, y0, x1, y1)
    for sgn in (-1, 1):
        b = math.radians(ang_deg + 180 + sgn * 35)
        bar(x1, y1, x1 + math.cos(b) * 0.5, y1 + math.sin(b) * 0.5)


def cc_a():
    """Variant A: crooked road manhole at the east end of the avenue (south lane), Teo's chalk arrow, a cone and a wedge of brick holding the lid."""
    s = sc.city_centre()
    s.ident = "cc_a"
    mx, my = 66.4, 27.6
    manhole_ring(s, mx, my, layer="floor", z=-0.02)
    # the cover sits crooked: shifted +x / +y, a dark crescent shows on the far side
    manhole_cover(s, mx + 0.5, my + 0.34, layer="floor", z=-0.02, rot=20, lift=0.0)
    chalk_arrow(s, 68.9, 28.8, -150, 1.5)               # points back to the cover from the east (towards Old Block), faint
    cone(s, mx - 0.9, my + 0.9)
    # a loose brick next to it
    s.box(mx + 1.1, my - 0.5, mx + 1.4, my - 0.38, 0.0, 0.1, "brick_red")
    return s


def cc_b():
    """Variant B: Water Board hatch on the river walk (east of the fountain square, between the trees and the railing), open."""
    s = sc.city_centre()
    s.ident = "cc_b"
    hx0, hy0, hx1, hy1 = 57.6, 49.2, 59.5, 50.6           # opening (cells)
    z = 0.012
    s.box(hx0 - 0.2, hy0 - 0.2, hx1 + 0.2, hy1 + 0.2, z - 0.01, z + 0.05, "sw_cover_rim", layer="floor")          # steel frame (flat)
    s.box(hx0, hy0, hx1, hy1, z + 0.05, z + 0.07, "sw_void", layer="floor")                                      # dark shaft
    # ladder rails climb out of the shaft along the south edge, chunky so they read at GBA size
    ladder_rungs(s, (hx0 + hx1) / 2, hy1 - 0.14, 0.0, 0.75, width=0.7, step=0.25, thick=1.8)
    # the lid, hinged on the WEST edge and swung up outward (a leaning plate: it does not hide the opening from the camera) + painted stripe
    s.poly([(hx0 - 0.05, hy0, 0.06), (hx0 - 0.05, hy1, 0.06), (hx0 - 0.6, hy1, 1.0), (hx0 - 0.6, hy0, 1.0)], "sw_hatch")
    s.poly([(hx0 - 0.2, hy0 + 0.15, 0.3), (hx0 - 0.2, hy1 - 0.15, 0.3), (hx0 - 0.37, hy1 - 0.15, 0.55), (hx0 - 0.37, hy0 + 0.15, 0.55)], "sw_hatch_paint")
    s.tube([(hx0, hy0 + 0.1, 0.06), (hx0 - 0.3, hy0 + 0.1, 0.5)], 0.02, "sw_iron")                               # hinge arm
    # cut padlock hanging on the frame
    s.cyl(hx1 + 0.2, hy1 - 0.2, 0.0, 0.1, 0.05, "brass", verts=8)
    # sign post: WATER BOARD - AUTHORISED ONLY
    s.cyl(56.6, 50.9, 0, 1.55, 0.04, "metal_dark", verts=6)
    s.box(56.1, 50.84, 57.2, 50.9, 1.15, 1.75, "sign_blue")
    s.text("WATER BOARD", 56.65, 50.82, 1.55, 0.14, "robot_white", face="left", bold=True)
    s.text("AUTHORISED ONLY", 56.65, 50.82, 1.32, 0.1, "robot_white", face="left")
    s.set_solid(56.45, 50.8, 56.8, 51.0)
    return s


# ---------------------------------------------------------------------------------------------------------------------
# OLD BLOCK exit
# ---------------------------------------------------------------------------------------------------------------------
EXIT_OB = (19.4, 22.6)


def _ob(ident, opened):
    import scene_oldblock as ob
    s = ob.old_block()
    s.ident = ident
    mx, my = EXIT_OB
    zc = 0.0
    manhole_ring(s, mx, my, layer="floor", z=zc)
    if opened:
        # the cover slid aside, resting on the cobbles (its edge overlaps the frame a little), a ladder top shows in the well
        manhole_cover(s, mx - 1.05, my + 0.5, layer="floor", z=zc, rot=10, lift=0.02)
        ladder_rungs(s, mx, my - 0.32, 0.0, 0.55, width=0.55, step=0.25, thick=1.8)
        # warm glow from below? the well stays dark; a faint hint of the tunnel lamp
        s.point_light(mx, my, 0.1, 18, colour=(1.0, 0.75, 0.45), radius=0.2)
    else:
        manhole_cover(s, mx, my, layer="floor", z=zc, rot=0, lift=0.0)
    return s


def ob_open():
    return _ob("ob_open", True)


def ob_closed():
    return _ob("ob_closed", False)


FUNCS = {"sewer": sewer, "cc_a": cc_a, "cc_b": cc_b, "ob_open": ob_open, "ob_closed": ob_closed}
