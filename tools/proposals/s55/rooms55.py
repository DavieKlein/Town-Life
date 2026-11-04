"""s52 proposal: the player's room above the Corner Market.
  market_stairs      : Corner Market interior (v2) with the stairs in the storeroom (replaces the staff table position)
  market_stairs_gate : same, after the firing: VaultTech gate across the foot of the stairs
  room_attic         : variant A, attic room with exposed roof trusses
  room_plain         : variant B, plain small room with a big window
Imported at the END of tools/scene.py (proposal copy) so the scenes are registered in SCENES."""
import inspect
import math
import random

import scene as scn
from scene import *   # noqa: F401,F403  (helpers: wall_y, wall_x, cutaway_floor, rug, potted_plant, ...)

# ---------------------------------------------------------------------------------------------
# 1. storeroom stairs
# ---------------------------------------------------------------------------------------------
SX0, SX1 = 15.0, 16.25         # stair flight x range (cells)
S_BOT, S_TOP = 4.0, 0.9        # foot (y) and landing (y)
S_N, S_RISE = 14, 0.2


def stairs_flight(s):
    """Straight wooden flight rising towards -y against the east side of the storeroom; closed +x side, open -x side with
    a handrail (the two lowest steps stay open so you can step on from the west)."""
    dy = (S_BOT - S_TOP) / S_N
    x0, x1 = SX0, SX1
    for i in range(S_N):
        ya, yb = S_BOT - (i + 1) * dy, S_BOT - i * dy
        z1 = (i + 1) * S_RISE
        s.box(x0, ya, x1, yb, 0, z1 - 0.05, "wood_dark")                   # riser block
        s.box(x0 - 0.03, ya - 0.02, x1 + 0.02, yb, z1 - 0.05, z1, "wood")   # tread with nosing
        s.box(x0 - 0.03, yb - 0.02, x1 + 0.02, yb, z1 - S_RISE, z1 - S_RISE + 0.02, "wood_dark") if False else None
    zl = S_N * S_RISE
    s.box(x0, 0.0, x1, S_TOP, zl - 0.14, zl, "wood")                       # landing
    s.box(x0, 0.0, x1, S_TOP, 0, zl - 0.14, "wood_dark")
    s.set_solid(x0 - 0.05, 0.0, x1 + 0.1, 3.45)
    s.occluder(x0 - 0.05, 0.0, x1 + 0.1, 3.5, zl + 0.5)
    # handrail on the open side (starts at step 3)
    k0 = 3
    yk0 = S_BOT - (k0 + 0.5) * dy
    zk0 = (k0 + 1) * S_RISE

    def post(y, z):
        s.box(x0 - 0.06, y - 0.035, x0 + 0.02, y + 0.035, z, z + 0.95, "wood_dark")
    post(yk0, zk0)
    post(S_BOT - (8 + 0.5) * dy, 9 * S_RISE)
    post(S_BOT - (13 + 0.5) * dy, 14 * S_RISE)
    s.tube([(x0 - 0.02, yk0, zk0 + 0.95), (x0 - 0.02, S_TOP, zl + 0.95)], 0.03, "wood")
    s.tube([(x0 - 0.02, S_TOP, zl + 0.95), (x0 - 0.02, 0.15, zl + 0.95)], 0.03, "wood")
    s.sphere(x0 - 0.02, yk0, zk0 + 1.0, 0.065, "wood")
    s.box(x0 - 0.06, 0.1, x0 + 0.02, 0.22, zl, zl + 0.95, "wood_dark")
    # plaque "PRIVATE" over the landing + a warm light
    s.box(14.75, 0.0, 16.4, 0.07, 3.0, 3.25, "wood_dark")
    s.text("PRIVATE", 15.57, 0.08, 3.05, 0.15, "sign_text", face="left")


def _patched_market(gate):
    src = inspect.getsource(scn.market_v2)
    src = src.replace("def market_v2():", "def _impl(gate):")
    src = src.replace('Scene("corner_market", "Corner Market"',
                      'Scene("market_gate_" + gate if gate else "market_stairs", "Corner Market stairs"')
    old_table = '''    s.prop("house/Table_RoundSmall", 15.0, 1.3, h=0.62, solid=True)
    s.box(14.7, 1.15, 15.0, 1.45, 0.62, 0.72, "goods_white")
    s.box(15.1, 1.0, 15.5, 1.25, 0.62, 0.75, "metal_dark")'''
    new_table = '''    s.prop("house/Table_RoundSmall", 13.4, 2.4, h=0.62, solid=True)
    s.box(13.1, 2.25, 13.4, 2.55, 0.62, 0.72, "goods_white")
    s.box(13.5, 2.1, 13.9, 2.35, 0.62, 0.75, "metal_dark")'''
    assert old_table in src
    src = src.replace(old_table, new_table)
    old_poster = 's.box(14.6, 0.0, 15.7, 0.05, 1.5, 2.2, "poster_red")'
    assert old_poster in src
    src = src.replace(old_poster, "pass")
    head, tail = src.rsplit("    return s", 1)
    ns = dict(vars(scn))
    ns.update(stairs_flight=stairs_flight, SX0=SX0, SX1=SX1, S_BOT=S_BOT)
    ns["vault_gate_a"] = vault_gate_a
    ns["vault_gate_b"] = vault_gate_b
    exec(head + '''    stairs_flight(s)
    s.point_light(15.6, 1.6, 2.9, 230, colour=(1.0, 0.82, 0.55))
    s.point_light(14.6, 3.4, 1.6, 90, colour=(1.0, 0.85, 0.6))
    if gate == "a":
        vault_gate_a(s)
    elif gate == "b":
        vault_gate_b(s)
    else:
        s.warp(SX0, 3.5, SX1, S_BOT, "room_attic", 5.8, 2.6, "up")
    return s
''', ns)
    return ns["_impl"](gate)


GX0, GX1 = SX0 - 0.15, SX1 + 0.1         # gate span (x)
GY = 4.1                                  # gate plane (y)


def staff_sign(s, z0=1.85, z1=3.05, x0=14.1, x1=16.95, y=None):
    """Big red board with white bold "STAFF" / "ONLY" (two big lines), white border."""
    y = GY + 0.1 if y is None else y
    cx = (x0 + x1) / 2
    s.box(x0, y - 0.07, x1, y + 0.05, z0, z1, "sign_red")
    for (a0, a1, b0, b1) in ((x0, x1, z1 - 0.05, z1), (x0, x1, z0, z0 + 0.05)):
        s.box(a0, y + 0.05, a1, y + 0.065, b0, b1, "sign_white")
    for xx in (x0, x1 - 0.05):
        s.box(xx, y + 0.05, xx + 0.05, y + 0.065, z0, z1, "sign_white")
    zc = (z0 + z1) / 2
    s.text("STAFF", cx, y + 0.075, zc + 0.28, 0.6, "sign_white", face="left", bold=True, extrude=0.012)
    s.text("ONLY", cx, y + 0.075, zc - 0.28, 0.6, "sign_white", face="left", bold=True, extrude=0.012)


def vault_gate_a(s):
    """Variant A, sturdy steel bar gate: heavy white posts with dark caps, 6 thick grey bars, top + bottom + mid rails,
    gold VaultTech V plate in the middle, card reader with a red lamp, big red STAFF ONLY sign above."""
    x0, x1, gy, top = GX0, GX1, GY, 1.55
    for px in (x0, x1 - 0.14):
        s.box(px, gy - 0.1, px + 0.14, gy + 0.08, 0, top + 0.4, "robot_white")
        s.box(px - 0.02, gy - 0.12, px + 0.16, gy + 0.1, top + 0.4, top + 0.48, "metal_dark")
    for (za, zb) in ((0.1, 0.22), (0.78, 0.88), (top - 0.14, top)):
        s.box(x0, gy - 0.06, x1, gy + 0.05, za, zb, "metal_light")
    n = 6
    span = x1 - x0 - 0.28
    for k in range(n):
        bx = x0 + 0.14 + 0.07 + k * (span - 0.14) / (n - 1)
        s.box(bx - 0.04, gy - 0.04, bx + 0.04, gy + 0.04, 0.22, top - 0.14, "robot_white")
    xm = (x0 + x1) / 2
    s.box(xm - 0.34, gy + 0.05, xm + 0.34, gy + 0.09, 0.4, 1.28, "metal_dark")
    s.box(xm - 0.3, gy + 0.09, xm + 0.3, gy + 0.1, 0.44, 1.24, "gold_dark")
    s.text("V", xm, gy + 0.115, 0.84, 0.75, "gold_bright", face="left", bold=True, extrude=0.02)
    s.box(x1 - 0.1, gy + 0.08, x1 + 0.0, gy + 0.16, 0.95, 1.3, "metal_dark")          # reader
    s.box(x1 - 0.08, gy + 0.16, x1 - 0.02, gy + 0.175, 1.18, 1.26, "neon_red")
    s.box(x1 - 0.08, gy + 0.16, x1 - 0.02, gy + 0.175, 1.0, 1.1, "metal_light")
    sx = x0 + 0.03
    s.box(sx, 3.3, sx + 0.08, gy, 0.1, 0.22, "metal_light")                              # side panel (open west)
    s.box(sx, 3.3, sx + 0.08, gy, top - 0.14, top, "metal_light")
    for k in range(4):
        by = 3.42 + k * 0.2
        s.box(sx, by - 0.035, sx + 0.07, by + 0.035, 0.22, top - 0.14, "robot_white")
    s.box(sx - 0.04, 3.22, sx + 0.1, 3.36, 0, top + 0.4, "robot_white")
    staff_sign(s, 1.85, 3.05)
    s.set_solid(x0, 3.3, x1, gy + 0.05)
    s.occluder(x0, 3.3, x1, gy + 0.1, 3.0)
    s.point_light(15.4, 4.5, 2.2, 55, colour=(0.85, 0.95, 1.0))


def vault_gate_b(s):
    """Variant B, roll-down shutter: white-grey corrugated steel slats in a heavy frame, dark roller box on top carrying the big
    red STAFF ONLY sign, yellow/black hazard strip on the bottom bar, gold V disc, card reader on the right."""
    x0, x1, gy = GX0, GX1, GY
    top = 1.75
    for px in (x0, x1 - 0.12):
        s.box(px, gy - 0.1, px + 0.12, gy + 0.08, 0, top + 0.3, "metal_light")
    s.box(x0 - 0.04, gy - 0.12, x1 + 0.04, gy + 0.1, top, top + 0.3, "metal_light")           # roller box
    z = 0.2
    k = 0
    while z < top - 0.02:
        s.box(x0 + 0.12, gy - 0.03, x1 - 0.12, gy + 0.03, z, z + 0.1, "goods_white" if k % 2 == 0 else "shutter_grey")
        s.box(x0 + 0.12, gy + 0.03, x1 - 0.12, gy + 0.05, z + 0.075, z + 0.1, "metal_light")
        z += 0.125
        k += 1
    for i in range(7):                                                                          # hazard bottom bar
        xa = x0 + 0.12 + i * (x1 - x0 - 0.24) / 7
        xb = xa + (x1 - x0 - 0.24) / 7
        s.box(xa, gy - 0.05, xb, gy + 0.07, 0.0, 0.2, "price_yellow" if i % 2 == 0 else "hazard_black")
    xm = (x0 + x1) / 2
    s.cyl(xm, gy + 0.06, 0.74, 1.3, 0.3, "gold_dark", axis="y", verts=28) if False else None
    s.box(xm - 0.32, gy + 0.05, xm + 0.32, gy + 0.09, 0.62, 1.34, "metal_dark")
    s.box(xm - 0.28, gy + 0.09, xm + 0.28, gy + 0.1, 0.66, 1.3, "gold_dark")
    s.text("V", xm, gy + 0.115, 0.98, 0.78, "gold_bright", face="left", bold=True, extrude=0.02)
    s.box(x1 - 0.02, gy + 0.0, x1 + 0.08, gy + 0.1, 0.9, 1.25, "robot_white")             # reader on the post
    s.box(x1 - 0.0, gy + 0.1, x1 + 0.06, gy + 0.115, 1.12, 1.2, "neon_red")
    sx = x0 + 0.03
    s.box(sx, 3.3, sx + 0.08, gy, 0.0, top, "metal_dark")                                       # side wall piece
    s.box(sx + 0.08, 3.32, sx + 0.1, gy - 0.02, 0.1, top - 0.1, "shutter_grey")
    staff_sign(s, top + 0.35, top + 1.55, y=gy + 0.1)
    s.set_solid(x0, 3.3, x1, gy + 0.05)
    s.occluder(x0, 3.3, x1, gy + 0.1, 3.2)
    s.point_light(15.4, 4.5, 2.2, 55, colour=(0.85, 0.95, 1.0))


def vault_gate(s):
    vault_gate_a(s)


def market_stairs():
    return _patched_market(False)


def market_gate_a():
    return _patched_market("a")


def market_gate_b():
    return _patched_market("b")


# ---------------------------------------------------------------------------------------------
# 2. the room above the shop
# ---------------------------------------------------------------------------------------------
RW, RH = 8, 7                  # cells (last row / column = cutaway stubs, solid)


def room_shell(ident, name, paper, wains, wh, origin_y, gable=False, hole=(5.1, 6.3, 3.5, 6.0)):
    s = Scene(ident, name, RW, RH, origin_x=RH * 16 + 24, origin_y=origin_y, img_w=(RW + RH) * 16 + 48,
              img_h=origin_y + (RW + RH) * 8 + 36)
    s.sun = False
    hx0, hx1, hy0, hy1 = hole
    # floor with the stairwell hole
    cutaway_floor(s, 0, 0, RW, hy0, "floor_wood2")
    cutaway_floor(s, 0, hy0, hx0, RH, "floor_wood2")
    cutaway_floor(s, hx1, hy0, RW, RH, "floor_wood2")
    cutaway_floor(s, hx0, hy1, hx1, RH, "floor_wood2")
    s.box(hx0, hy0, hx1, hy1, -0.42, -0.4, "metal_dark", layer="floor")
    # walls
    wall_x(s, 0.0, RH - 0.4, 0.0, wh, paper=paper, wains=wains, wain_h=0.95, cap=not gable)
    wall_y(s, -0.4, RW, 0.0, wh, paper=paper, wains=wains, wain_h=0.95)
    wall_stub_y(s, 0, RW, RH, mat=paper)
    wall_stub_x(s, 0, RH, RW, mat=paper)
    s.set_solid(RW - 1, 0, RW, RH)
    s.set_solid(0, RH - 1, RW, RH)
    s.occluder(-0.4, -0.4, RW, 0.1, wh)
    s.occluder(-0.4, 0, 0.1, RH, wh)
    return s


def stairwell(s, hole=(5.1, 6.3, 3.5, 6.0)):
    """Steps going down (towards +y), balustrade on three sides, open at the top (north). Warp on the top steps."""
    hx0, hx1, hy0, hy1 = hole
    nst = 4
    sd = (hy1 - hy0 - 0.5) / nst
    for i in range(nst):
        ya = hy0 + 0.5 + i * sd
        z = -0.14 * (i + 1)
        s.box(hx0 + 0.02, ya, hx1 - 0.02, ya + sd, z - 0.05, z, "wood", layer="floor")
        s.box(hx0 + 0.02, ya, hx1 - 0.02, ya + sd, -0.4, z - 0.05, "wood_dark", layer="floor")
    s.box(hx0 + 0.02, hy0, hx1 - 0.02, hy0 + 0.5, -0.07, 0.0, "wood", layer="floor")           # top sill
    zr = 0.95
    posts = ((hx0 - 0.04, hy0 + 0.25), (hx0 - 0.04, (hy0 + hy1) / 2), (hx0 - 0.04, hy1 - 0.1),
             (hx1 - 0.03, hy0 + 0.25), (hx1 - 0.03, (hy0 + hy1) / 2), (hx1 - 0.03, hy1 - 0.1))
    for (px, py) in posts:
        s.box(px, py - 0.04, px + 0.07, py + 0.04, 0, zr, "wood_dark")
    for k in (0, 3):                                  # taller newels at the entrance
        px = (hx0 - 0.04) if k == 0 else (hx1 - 0.03)
        s.box(px - 0.01, hy0 + 0.2, px + 0.08, hy0 + 0.3, zr, zr + 0.1, "wood")
    s.tube([(hx0, hy0 + 0.25, zr), (hx0, hy1 - 0.1, zr)], 0.03, "wood")
    s.tube([(hx1, hy0 + 0.25, zr), (hx1, hy1 - 0.1, zr)], 0.03, "wood")
    s.tube([(hx0, hy1 - 0.1, zr), (hx1, hy1 - 0.1, zr)], 0.03, "wood")
    for yy in (hy0 + 1.0, hy0 + 1.7, hy0 + 2.2):     # balusters
        for xx in (hx0 + 0.03, hx1 - 0.03):
            s.box(xx - 0.015, yy - 0.015, xx + 0.015, yy + 0.015, 0, zr, "wood_dark")
    s.set_solid(hx0 - 0.1, hy0 + 0.55, hx1 + 0.05, RH)
    s.warp(hx0 + 0.15, hy0 + 0.1, hx1 - 0.15, hy0 + 0.6, "market_stairs", 14.3, 3.75, "right") if False else None
    s.warp(hx0 + 0.1, hy0 + 0.05, hx1 - 0.1, hy0 + 0.55, "corner_market", 14.3, 3.75, "right")


def window_street(s, wx0, wx1, wz0, wz1, curtain=True):
    """Window in the back wall (y = 0) with a painted street view (houses + the golden VaultTech tower) behind the glass."""
    paper = "wp_peach"
    # frame, sill and mullions
    s.box(wx0 - 0.06, -0.12, wx1 + 0.06, 0.06, wz0 - 0.08, wz0, "trim_white")
    s.box(wx0 - 0.06, -0.12, wx1 + 0.06, 0.06, wz1, wz1 + 0.08, "trim_white")
    s.box(wx0 - 0.08, -0.12, wx0, 0.06, wz0 - 0.08, wz1 + 0.08, "trim_white")
    s.box(wx1, -0.12, wx1 + 0.08, 0.06, wz0 - 0.08, wz1 + 0.08, "trim_white")
    nmull = max(1, int((wx1 - wx0) / 1.1))
    for k in range(1, nmull + 1):
        mx = wx0 + k * (wx1 - wx0) / (nmull + 1)
        s.box(mx - 0.025, -0.12, mx + 0.025, 0.04, wz0, wz1, "trim_white")
    s.box(wx0, -0.12, wx1, 0.04, (wz0 + wz1) / 2 - 0.02, (wz0 + wz1) / 2 + 0.02, "trim_white")
    s.box(wx0 - 0.2, 0.0, wx1 + 0.2, 0.2, wz0 - 0.14, wz0 - 0.08, "trim_white")
    by = -0.32
    s.box(wx0 - 0.3, by - 0.06, wx1 + 0.5, by, wz0 - 0.4, wz1 + 0.1, "wp_blue")
    s.box(wx0 - 0.3, by, wx1 + 0.5, by + 0.02, wz0 - 0.4, wz0 + 0.12, "concrete")

    def house(x0, x1, h, mat, roof="slate"):
        s.box(x0, by, x1, by + 0.07, wz0 - 0.4, wz0 + h, mat)
        s.box(x0 - 0.02, by, x1 + 0.02, by + 0.08, wz0 + h, wz0 + h + 0.05, roof)
        for k in range(int((x1 - x0) / 0.22)):
            for r in range(int(h / 0.3)):
                s.box(x0 + 0.06 + k * 0.22, by + 0.07, x0 + 0.15 + k * 0.22, by + 0.09, wz0 + 0.1 + r * 0.3,
                      wz0 + 0.22 + r * 0.3, "lamp_glass" if (k + r) % 3 == 0 else "glass")
    wd = wx1 - wx0
    house(wx0 - 0.1, wx0 + 0.5, 0.75, "brick_red")
    house(wx0 + 0.55, wx0 + 1.1, 1.0, "plaster_cream")
    house(wx0 + 1.15, wx0 + 1.6, 0.6, "brick_brown")
    if wd > 2.4:
        house(wx0 + 1.65, wx0 + 2.2, 0.9, "plaster_purple")
        house(wx0 + 2.25, wx0 + 2.8, 0.7, "brick_red")
    s.box(wx1 - 0.55, by, wx1 - 0.3, by + 0.09, wz0 - 0.4, wz1 + 0.3, "gold_bright")                # VaultTech tower
    s.box(wx1 - 0.48, by, wx1 - 0.44, by + 0.1, wz0 - 0.4, wz1 + 0.3, "gold_dark")
    s.sphere(wx1 - 0.9, by + 0.12, wz0 + 0.1, 0.2, "leaves_light", sz=1.0)
    if curtain:
        for cx0, cx1 in ((wx0 - 0.45, wx0 + 0.08), (wx1 - 0.08, wx1 + 0.45)):
            s.box(cx0, 0.02, cx1, 0.17, wz0 - 0.25, wz1 + 0.25, "curtain_red")
        s.box(wx0 - 0.55, 0.0, wx1 + 0.55, 0.12, wz1 + 0.25, wz1 + 0.3, "brass")


def bed_y(s, x0, y0, length=2.8, width=1.4, wake=True):
    """Bed along the west wall (long axis y), headboard at y0. Patchwork quilt, two pillows, folded blanket."""
    x1, y1 = x0 + width, y0 + length
    s.box(x0, y0 - 0.1, x1, y1, 0.12, 0.42, "wood")
    s.box(x0, y0 - 0.1, x1, y0 + 0.02, 0.12, 1.15, "wood_dark")
    s.box(x0 + 0.02, y1 - 0.08, x1 - 0.02, y1, 0.12, 0.62, "wood_dark")
    s.box(x0 + 0.06, y0 + 0.05, x1 - 0.06, y1 - 0.1, 0.42, 0.58, "paper_cream")
    cols = ("rug_teal", "rug_gold", "rug_red", "rug_cream", "rug_green")
    nq = int((length - 1.0) / 0.34)
    for qi in range(nq):
        for qj in range(2):
            c = cols[(qi + qj * 2) % 5]
            xa = x0 + 0.08 + qj * (width - 0.16) / 2
            s.box(xa, y0 + 0.9 + qi * 0.34, xa + (width - 0.16) / 2, y0 + 0.9 + (qi + 1) * 0.34, 0.58, 0.635, c)
    s.box(x0 + 0.12, y0 + 0.1, x0 + 0.62, y0 + 0.7, 0.58, 0.72, "paper_cream")
    s.box(x0 + 0.7, y0 + 0.15, x1 - 0.1, y0 + 0.72, 0.58, 0.70, "paper_cream")
    s.box(x0 + 0.1, y1 - 0.5, x1 - 0.1, y1 - 0.15, 0.635, 0.7, "rug_navy")
    s.set_solid(x0, y0 - 0.1, x1 - 0.001, y1 - 0.001)
    s.occluder(x0, y0 - 0.1, x1, y1, 1.2)


def bed_x(s, x0, y0, length=2.8, width=1.4):
    """Bed along the back wall (long axis x), headboard at x0."""
    x1, y1 = x0 + length, y0 + width
    s.box(x0 - 0.1, y0, x1, y1, 0.12, 0.42, "wood")
    s.box(x0 - 0.1, y0, x0 + 0.02, y1, 0.12, 1.15, "wood_dark")
    s.box(x1 - 0.08, y0 + 0.02, x1, y1 - 0.02, 0.12, 0.62, "wood_dark")
    s.box(x0 + 0.05, y0 + 0.06, x1 - 0.1, y1 - 0.06, 0.42, 0.58, "paper_cream")
    cols = ("rug_gold", "rug_teal", "rug_red", "rug_green", "rug_cream")
    nq = int((length - 1.0) / 0.34)
    for qi in range(nq):
        for qj in range(2):
            c = cols[(qi + qj * 2) % 5]
            ya = y0 + 0.08 + qj * (width - 0.16) / 2
            s.box(x0 + 0.9 + qi * 0.34, ya, x0 + 0.9 + (qi + 1) * 0.34, ya + (width - 0.16) / 2, 0.58, 0.635, c)
    s.box(x0 + 0.1, y0 + 0.12, x0 + 0.7, y0 + 0.62, 0.58, 0.72, "paper_cream")
    s.box(x0 + 0.15, y0 + 0.7, x0 + 0.72, y1 - 0.1, 0.58, 0.70, "paper_cream")
    s.box(x1 - 0.5, y0 + 0.1, x1 - 0.15, y1 - 0.1, 0.635, 0.7, "rug_navy")
    s.set_solid(x0 - 0.1, y0, x1 - 0.001, y1 - 0.001)
    s.occluder(x0 - 0.1, y0, x1, y1, 1.2)


def bedside_y(s, x0, x1, y0, y1):
    """Bedside table against the back wall (y = 0) with a lamp, a book and a framed photo."""
    s.box(x0, y0, x1, y1, 0, 0.55, "wood")
    s.box(x0 + 0.04, y1, x1 - 0.04, y1 + 0.02, 0.1, 0.25, "wood_dark")
    s.box(x0 + 0.04, y1, x1 - 0.04, y1 + 0.02, 0.3, 0.45, "wood_dark")
    cx = (x0 + x1) / 2
    s.cyl(cx - 0.1, y0 + 0.3, 0.55, 0.78, 0.04, "brass")
    s.cyl(cx - 0.1, y0 + 0.3, 0.72, 0.98, 0.16, "lamp_shade", r2=0.1)
    s.box(cx + 0.12, y0 + 0.2, cx + 0.3, y0 + 0.36, 0.55, 0.6, "book_a")
    s.set_solid(x0, y0, x1 - 0.001, y1 - 0.001)
    s.occluder(x0, y0, x1, y1, 1.0)
    s.point_light(cx - 0.1, y0 + 0.3, 0.95, 55, colour=(1.0, 0.78, 0.45), radius=0.12)


def wardrobe_y(s, x0, x1, wh=2.2):
    """Two-door wardrobe against the back wall (y = 0)."""
    s.box(x0, 0.04, x1, 0.95, 0, wh, "wood")
    s.box(x0 - 0.03, 0.04, x1 + 0.03, 0.98, wh, wh + 0.1, "wood_dark")
    w = (x1 - x0 - 0.16) / 2
    for dx0 in (x0 + 0.06, x0 + 0.1 + w):
        s.box(dx0, 0.95, dx0 + w, 0.99, 0.12, wh - 0.1, "wood_dark")
        s.box(dx0 + 0.1, 0.99, dx0 + w - 0.1, 1.0, 0.25, wh - 0.25, "wood")
    mx = (x0 + x1) / 2
    s.box(mx - 0.06, 1.0, mx - 0.02, 1.04, 0.9, 1.3, "brass")
    s.box(mx + 0.02, 1.0, mx + 0.06, 1.04, 0.9, 1.3, "brass")
    s.set_solid(x0, 0.04, x1 - 0.001, 0.999)
    s.occluder(x0, 0.04, x1, 0.95, wh + 0.1)


def wardrobe_x(s, y0, y1, wh=2.2):
    """Two-door wardrobe against the west wall (x = 0)."""
    s.box(0.04, y0, 0.95, y1, 0, wh, "wood")
    s.box(0.04, y0 - 0.03, 0.98, y1 + 0.03, wh, wh + 0.1, "wood_dark")
    w = (y1 - y0 - 0.16) / 2
    for dy0 in (y0 + 0.06, y0 + 0.1 + w):
        s.box(0.95, dy0, 0.99, dy0 + w, 0.12, wh - 0.1, "wood_dark")
        s.box(0.99, dy0 + 0.1, 1.0, dy0 + w - 0.1, 0.25, wh - 0.25, "wood")
    my = (y0 + y1) / 2
    s.box(1.0, my - 0.06, 1.04, my - 0.02, 0.9, 1.3, "brass")
    s.box(1.0, my + 0.02, 1.04, my + 0.06, 0.9, 1.3, "brass")
    s.set_solid(0.04, y0, 0.999, y1 - 0.001)
    s.occluder(0.04, y0, 0.95, y1, wh + 0.1)


def desk_y(s, x0, x1, chair=True):
    """Small desk against the back wall (y = 0): lamp, laptop, mug with a plant, photo frame, notebook."""
    s.box(x0, 0.1, x1, 0.8, 0.68, 0.74, "wood")
    for lx in (x0 + 0.05, x1 - 0.12):
        s.box(lx, 0.15, lx + 0.07, 0.22, 0, 0.68, "wood_dark")
        s.box(lx, 0.68, lx + 0.07, 0.75, 0, 0.68, "wood_dark")
    s.box(x0 + 0.1, 0.1, x1 - 0.1, 0.75, 0.5, 0.56, "wood_dark")                       # drawer
    s.box(x0 + 0.35, 0.18, x0 + 0.85, 0.5, 0.74, 0.77, "tv_body")                      # laptop base
    s.box(x0 + 0.35, 0.18, x0 + 0.85, 0.2, 0.77, 1.0, "tv_body")
    s.box(x0 + 0.38, 0.2, x0 + 0.82, 0.215, 0.79, 0.98, "tv_screen")
    s.cyl(x1 - 0.22, 0.28, 0.74, 0.8, 0.065, "pot")                                    # mug with a little plant
    s.sphere(x1 - 0.22, 0.28, 0.9, 0.11, "leaves_light")
    s.box(x0 + 0.1, 0.5, x0 + 0.3, 0.52, 0.74, 0.92, "frame_wood")                      # photo frame
    s.box(x0 + 0.12, 0.52, x0 + 0.28, 0.53, 0.77, 0.89, "picture_sea")
    s.box(x0 + 0.95, 0.4, x0 + 1.25, 0.62, 0.74, 0.78, "book_d")                        # notebook
    s.set_solid(x0, 0.1, x1 - 0.001, 0.8)
    s.occluder(x0, 0.1, x1, 0.8, 0.9)
    if chair:
        s.prop("house/Chair_1", (x0 + x1) / 2 - 0.2, 1.35, rot=0, h=0.9, colours={"Wood": "#9a6a3a"}, solid=True)


def string_lights(s, pts, z0=2.45):
    """Fairy lights: a sagging wire with warm bulbs along a wall (pts = list of (x, y) at the wall face)."""
    rnd = random.Random(5)
    segs = []
    for (a, b) in zip(pts, pts[1:]):
        n = 5
        for i in range(n + 1):
            t = i / n
            sag = 0.22 * math.sin(math.pi * t)
            segs.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, z0 - sag))
    s.tube(segs, 0.012, "cord_black")
    for i, p in enumerate(segs):
        if i % 2 == 1:
            col = ("lamp_glass", "flower_red", "flower_yellow", "lamp_glass", "flower_pink")[i % 5]
            s.sphere(p[0], p[1], p[2] - 0.05, 0.045, col)


def personal_things(s, rnd, mat_apron="awning_green"):
    pass


def wall_pinboard_x(s, y0, y1, z0, z1):
    """Cork board on the west wall with notes, a shift plan and the Corner Market apron on a hook."""
    s.box(0.0, y0 - 0.05, 0.05, y1 + 0.05, z0 - 0.05, z1 + 0.05, "frame_wood")
    s.box(0.05, y0, 0.07, y1, z0, z1, "cork")
    notes = [("paper_cream", 0.2, 0.55), ("price_yellow", 0.55, 0.25), ("poster_blue", 0.75, 0.6), ("goods_pink", 0.35, 0.15)]
    for i, (m, fy, fz) in enumerate(notes):
        ya = y0 + 0.08 + fy * (y1 - y0 - 0.4)
        za = z0 + 0.08 + fz * (z1 - z0 - 0.3)
        s.box(0.07, ya, 0.09, ya + 0.2, za, za + 0.22, m)
        s.box(0.09, ya + 0.09, 0.1, ya + 0.11, za + 0.18, za + 0.2, "red_paint")      # pin


def apron_hook_x(s, y, z):
    """The green Corner Market apron on a wall hook (west wall)."""
    s.box(0.0, y - 0.04, 0.12, y + 0.04, z + 0.62, z + 0.66, "wood_dark")
    s.box(0.04, y - 0.15, 0.1, y + 0.15, z + 0.0, z + 0.64, "awning_green")
    s.box(0.1, y - 0.1, 0.12, y + 0.1, z + 0.12, z + 0.3, "wood_green")               # pocket
    s.box(0.1, y - 0.2, 0.12, y - 0.1, z + 0.3, z + 0.34, "awning_green")              # strap
    s.box(0.1, y + 0.02, 0.125, y + 0.12, z + 0.45, z + 0.52, "paper_cream")          # name tag


def apron_hook_y(s, x, z):
    s.box(x - 0.04, 0.0, x + 0.04, 0.12, z + 0.62, z + 0.66, "wood_dark")
    s.box(x - 0.15, 0.04, x + 0.15, 0.1, z + 0.0, z + 0.64, "awning_green")
    s.box(x - 0.1, 0.1, x + 0.1, 0.12, z + 0.12, z + 0.3, "wood_green")
    s.box(x - 0.12, 0.1, x - 0.02, 0.125, z + 0.45, z + 0.52, "paper_cream")


def floor_bits(s, rnd, spots):
    """Backpack, red sneakers, a basketball, a stack of books... spots = dict of (x, y)."""
    bx, by = spots["backpack"]
    s.box(bx, by, bx + 0.45, by + 0.3, 0, 0.5, "wood_blue")
    s.box(bx + 0.04, by + 0.3, bx + 0.41, by + 0.36, 0.05, 0.3, "wood_dark")
    s.box(bx + 0.1, by + 0.36, bx + 0.35, by + 0.38, 0.1, 0.22, "price_yellow")
    s.box(bx + 0.1, by - 0.01, bx + 0.35, by + 0.01, 0.4, 0.5, "metal_light")
    s.set_solid(bx, by, bx + 0.449, by + 0.38)
    sx, sy = spots["shoes"]
    for k in (0, 1):
        s.box(sx + k * 0.22, sy, sx + 0.18 + k * 0.22, sy + 0.34, 0, 0.1, "red_paint")
        s.box(sx + k * 0.22, sy, sx + 0.18 + k * 0.22, sy + 0.34, 0, 0.03, "paper_cream")
        s.box(sx + k * 0.22 + 0.02, sy, sx + 0.16 + k * 0.22, sy + 0.12, 0.1, 0.16, "red_paint")
    bx2, by2 = spots["ball"]
    s.sphere(bx2, by2, 0.12, 0.12, "orange_paint")
    s.box(bx2 - 0.12, by2 - 0.005, bx2 + 0.12, by2 + 0.005, 0.115, 0.125, "metal_dark") if False else None
    kx, ky = spots["books"]
    for i, c in enumerate(("book_a", "book_d", "book_b", "book_e")):
        s.box(kx + (i % 2) * 0.03, ky, kx + 0.34 + (i % 2) * 0.03, ky + 0.26, i * 0.045, (i + 1) * 0.045, c)


# --------------------------------------------------------------------------------------- variant A
def room_attic():
    """Variant A: attic under the roof - exposed trusses and ridge beam, gable end on the west wall, dormer-style window,
    warm peach walls, string lights, cosy lived-in corners."""
    WH = 2.6
    s = room_shell("room_attic", "Room above the shop (attic)", "wp_peach", "wood_dark", WH, 100, gable=True)
    rnd = random.Random(7)
    # gable end above the west wall (flat triangle) with a sloped trim made of two beams, plus roof trusses
    ridge_y, ridge_z = RH / 2.0, 3.75
    s.poly([(0.0, 0.0, WH), (0.0, RH - 0.4, WH), (0.0, ridge_y, ridge_z)], "wp_peach")
    s.box(0.0, 0.0, 0.07, RH - 0.4, WH - 0.05, WH, "trim_white")
    dark = "wood_dark"

    def truss(x, r=0.06):
        s.tube([(x, -0.05, WH - 0.02), (x, ridge_y, ridge_z)], r, dark)
        s.tube([(x, RH - 0.5, WH - 0.02), (x, ridge_y, ridge_z)], r, dark)
    truss(0.05, 0.07)
    s.box(0.0, 1.0, 0.1, RH - 1.4, 2.95, 3.05, dark)                                        # collar tie in the gable
    s.box(0.0, ridge_y - 0.05, 0.1, ridge_y + 0.05, 3.05, ridge_z - 0.05, dark)               # king post
    s.tube([(0.0, ridge_y, ridge_z), (1.3, ridge_y, ridge_z)], 0.05, dark)                  # short ridge stub
    # window with street view (dormer feeling: deep sill), centred above the desk
    window_street(s, 2.7, 4.3, 1.05, 2.15)
    # bed (west wall), bedside table + lamp between bed and window
    bed_y(s, 0.12, 1.15)
    # (bedside to the east of the bed along the back wall would collide with the window: put it at the foot of the bed)
    s.box(0.12, 4.2, 0.7, 4.8, 0, 0.5, "wood")
    s.box(0.14, 4.2, 0.68, 4.215, 0.1, 0.4, "wood_dark")
    s.cyl(0.4, 4.5, 0.5, 0.7, 0.04, "brass")
    s.cyl(0.4, 4.5, 0.66, 0.9, 0.15, "lamp_shade", r2=0.1)
    s.set_solid(0.12, 4.2, 0.699, 4.799)
    s.point_light(0.4, 4.5, 0.9, 50, colour=(1.0, 0.78, 0.45), radius=0.12)
    # wardrobe on the back wall (right), desk under the window, plant, bookcase
    wardrobe_y(s, 5.0, 6.85)
    desk_y(s, 2.55, 4.45)
    s.prop("house/Light_Floor1", 4.85, 0.55, h=1.55, solid=True) if False else None
    s.cyl(4.75, 0.45, 0.0, 1.5, 0.02, "metal_dark")
    s.cyl(4.75, 0.45, 0.0, 0.04, 0.12, "metal_dark")
    s.cyl(4.75, 0.45, 1.35, 1.65, 0.17, "lamp_shade", r2=0.11)
    s.set_solid(4.6, 0.3, 4.9, 0.6)
    s.point_light(4.75, 0.5, 1.5, 70, colour=(1.0, 0.8, 0.5), radius=0.15)
    # bookcase low on the west wall near the front
    s.box(0.04, 5.1, 0.55, 6.5, 0, 1.2, "wood")
    for lv in range(3):
        zb = 0.08 + lv * 0.36
        s.box(0.04, 5.1, 0.55, 6.5, zb, zb + 0.03, "wood_dark")
        y = 5.15
        while y < 6.4:
            w = rnd.uniform(0.07, 0.13)
            s.box(0.1, y, 0.5, y + w, zb + 0.03, zb + 0.03 + rnd.uniform(0.18, 0.28),
                  rnd.choice(["book_a", "book_b", "book_c", "book_d", "book_e", "book_f"]))
            y += w + 0.01
    s.box(0.04, 5.1, 0.55, 6.5, 1.2, 1.25, "wood_dark")
    s.set_solid(0.04, 5.1, 0.549, 6.499)
    s.occluder(0.04, 5.1, 0.55, 6.5, 1.3)
    # little radio + a framed photo on the bookcase top
    s.box(0.15, 5.4, 0.45, 5.8, 1.25, 1.4, "metal_dark")
    s.cyl(0.3, 5.55, 1.4, 1.5, 0.03, "metal_light")
    s.box(0.12, 6.0, 0.4, 6.05, 1.25, 1.45, "frame_wood")
    potted_plant(s, 0.55, 6.75, "bush")
    # rug, wall decor
    s.cyl(3.3, 3.5, 0.0, 0.012, 1.45, "rug_red", layer="floor", verts=40)
    s.cyl(3.3, 3.5, 0.012, 0.02, 1.2, "rug_cream", layer="floor", verts=40)
    s.cyl(3.3, 3.5, 0.02, 0.028, 0.95, "rug_teal", layer="floor", verts=40)
    s.cyl(3.3, 3.5, 0.028, 0.036, 0.4, "rug_gold", layer="floor", verts=40)
    picture_y(s, 5.4, 6.4, 0.0, 2.3, 2.5, "picture_hill") if False else None
    picture_x(s, 2.6, 3.4, 0.0, 1.55, 2.25, "picture_sea")
    wall_pinboard_x(s, 4.9, 6.1, 1.45, 2.25) if False else None
    wall_clock_x(s, 0.0, 4.55, 2.2, 0.2)
    apron_hook_x(s, 3.9, 1.35)
    picture_y(s, 7.0, 7.25, 0.0, 1.2, 1.5, "poster_yellow") if False else None
    string_lights(s, [(0.06, 0.15), (0.06, 3.0), (0.06, 6.2)], z0=2.45)
    floor_bits(s, rnd, dict(backpack=(2.9, 5.7), shoes=(1.6, 4.5), ball=(1.8, 6.2), books=(1.45, 3.9)))
    s.set_solid(2.9, 5.7, 3.349, 6.099)
    # lighting
    s.point_light(3.5, 2.5, 2.6, 160, colour=(1.0, 0.85, 0.62))
    s.point_light(3.5, 0.4, 1.8, 110, colour=(0.85, 0.92, 1.0))        # daylight from the window
    s.point_light(2.0, 5.5, 2.3, 60, colour=(1.0, 0.8, 0.55))
    stairwell(s)
    return s


# --------------------------------------------------------------------------------------- variant B
def room_plain():
    """Variant B: plain small room with a big window and a window seat; butter-yellow walls, flat ceiling (cut away)."""
    WH = 2.8
    s = room_shell("room_plain", "Room above the shop (window)", "wp_cream", "wood_red", WH, 84, hole=(4.6, 5.8, 3.5, 6.0))
    rnd = random.Random(9)
    # big window with window seat (back wall, left part)
    wx0, wx1, wz0, wz1 = 0.9, 4.2, 0.9, 2.35
    s.box(wx0 - 0.15, -0.4, wx1 + 0.15, 0.0, 0.0, wz0 - 0.1, "wp_cream")
    s.box(wx0 - 0.15, -0.4, wx1 + 0.15, 0.0, wz1 + 0.1, WH, "wp_cream")
    s.box(wx0 - 0.15, -0.4, wx0, 0.0, wz0 - 0.1, wz1 + 0.1, "wp_cream")
    s.box(wx1, -0.4, wx1 + 0.15, 0.0, wz0 - 0.1, wz1 + 0.1, "wp_cream")
    window_street(s, wx0, wx1, wz0, wz1)
    # window seat: bench box with cushions, two pillows and a folded throw
    s.box(wx0 - 0.15, 0.05, wx1 + 0.15, 0.78, 0.0, 0.42, "wood")
    s.box(wx0 - 0.15, 0.78, wx1 + 0.15, 0.82, 0.05, 0.38, "wood_dark")
    s.box(wx0 - 0.1, 0.1, wx1 + 0.1, 0.76, 0.42, 0.5, "rug_teal")
    s.box(wx0 + 0.1, 0.18, wx0 + 0.6, 0.55, 0.5, 0.64, "rug_gold")
    s.box(wx0 + 0.65, 0.2, wx0 + 1.1, 0.55, 0.5, 0.62, "rug_red")
    s.box(wx1 - 0.9, 0.15, wx1 - 0.1, 0.65, 0.5, 0.56, "rug_cream")
    s.set_solid(wx0 - 0.15, 0.05, wx1 + 0.149, 0.78)
    s.occluder(wx0 - 0.15, 0.05, wx1 + 0.15, 0.78, 0.6)
    # bed in the back-right corner along the back wall; bedside table west of it; wardrobe + desk on the west wall
    bed_x(s, 4.85, 0.12, length=2.95, width=1.4)
    s.box(4.35, 0.05, 4.8, 0.55, 0, 0.5, "wood")
    s.cyl(4.58, 0.3, 0.5, 0.7, 0.04, "brass")
    s.cyl(4.58, 0.3, 0.66, 0.9, 0.15, "lamp_shade", r2=0.1)
    s.set_solid(4.35, 0.05, 4.799, 0.549)
    s.point_light(4.58, 0.3, 0.9, 50, colour=(1.0, 0.78, 0.45), radius=0.12)
    wardrobe_x(s, 1.3, 3.0)
    # desk on the west wall (long side along y), chair facing the desk
    dx0, dy0, dy1 = 0.1, 3.3, 5.0
    s.box(dx0, dy0, dx0 + 0.7, dy1, 0.68, 0.74, "wood")
    for ly in (dy0 + 0.04, dy1 - 0.1):
        s.box(dx0 + 0.05, ly, dx0 + 0.12, ly + 0.07, 0, 0.68, "wood_dark")
        s.box(dx0 + 0.58, ly, dx0 + 0.65, ly + 0.07, 0, 0.68, "wood_dark")
    s.box(dx0 + 0.1, dy0 + 0.05, dx0 + 0.6, dy1 - 0.05, 0.5, 0.56, "wood_dark")
    s.box(dx0 + 0.1, dy0 + 0.25, dx0 + 0.15, dy0 + 0.75, 0.74, 0.77, "tv_body")
    s.box(dx0 + 0.1, dy0 + 0.25, dx0 + 0.12, dy0 + 0.75, 0.77, 0.99, "tv_body")
    s.box(dx0 + 0.12, dy0 + 0.28, dx0 + 0.135, dy0 + 0.72, 0.79, 0.97, "tv_screen")
    s.box(dx0 + 0.3, dy0 + 0.35, dx0 + 0.6, dy0 + 0.75, 0.74, 0.77, "tv_body") if False else None
    s.cyl(dx0 + 0.4, dy1 - 0.25, 0.74, 0.8, 0.06, "pot")
    s.sphere(dx0 + 0.4, dy1 - 0.25, 0.9, 0.11, "leaves_light")
    s.box(dx0 + 0.2, dy0 + 1.0, dx0 + 0.5, dy0 + 1.3, 0.74, 0.77, "book_d")
    s.box(dx0 + 0.55, dy1 - 0.65, dx0 + 0.6, dy1 - 0.45, 0.74, 0.92, "frame_wood")
    s.set_solid(dx0, dy0, dx0 + 0.699, dy1 - 0.001)
    s.occluder(dx0, dy0, dx0 + 0.7, dy1, 0.9)
    s.prop("house/Chair_1", 1.55, 4.15, rot=270, h=0.9, colours={"Wood": "#9a6a3a"}, solid=True)
    # pinboard + apron over the desk; clock and a poster
    wall_pinboard_x(s, 3.35, 4.65, 1.25, 2.05)
    apron_hook_x(s, 5.4, 1.35)
    wall_clock_x(s, 0.0, 0.6, 2.15, 0.2)
    picture_y(s, 7.0, 7.9, 0.0, 1.6, 2.4, "picture_hill") if False else None
    picture_y(s, 5.3, 6.2, 0.0, 1.9, 2.5, "picture_sea")
    # bookshelf (wall shelf, planks) + plant corner
    for zz in (1.55, 1.95):
        s.box(0.0, 5.5, 0.35, 6.9, zz, zz + 0.04, "wood")
        y = 5.55
        while y < 6.8:
            w = rnd.uniform(0.07, 0.13)
            s.box(0.04, y, 0.3, y + w, zz + 0.04, zz + 0.04 + rnd.uniform(0.15, 0.26),
                  rnd.choice(["book_a", "book_b", "book_c", "book_d", "book_e", "book_f"]))
            y += w + 0.01
    potted_plant(s, 0.55, 6.6, "flowers")
    s.cyl(0.9, 0.6, 0.0, 1.5, 0.02, "metal_dark") if False else None
    # rug (rectangular, runner style) in the middle and string lights
    rug(s, 1.7, 1.9, 3.9, 4.4, "rug_red", "rug_cream", "rug_teal")
    string_lights(s, [(0.9, 0.12), (4.2, 0.12), (7.8, 0.12)], z0=2.62)
    floor_bits(s, rnd, dict(backpack=(2.3, 5.5), shoes=(6.5, 2.35), ball=(4.9, 2.4), books=(2.5, 5.0)))
    s.set_solid(2.3, 5.5, 2.749, 5.899)
    s.set_solid(4.78, 2.28, 5.02, 2.52)
    s.point_light(2.5, 0.5, 2.2, 190, colour=(1.0, 0.92, 0.75))     # window light (sunny, warm)
    s.point_light(5.5, 3.5, 2.4, 110, colour=(1.0, 0.85, 0.62))
    s.point_light(1.5, 5.0, 2.2, 50, colour=(1.0, 0.82, 0.55))
    stairwell(s, hole=(4.6, 5.8, 3.5, 6.0))
    return s



# --------------------------------------------------------------------------------------- variant B2 (calm furniture)
def bed_calm_x(s, x0, y0, length=2.95, width=1.45):
    """Calm bed along the back wall (long axis x), headboard at x0: oak frame with a tall panelled headboard, cream mattress, ONE
    dusty-blue duvet with a turned-back cream sheet, two big cream pillows, one folded mustard blanket at the foot."""
    x1, y1 = x0 + length, y0 + width
    s.box(x0, y0, x1, y1, 0.1, 0.4, "wood")                                           # frame / base
    s.box(x0 - 0.12, y0 - 0.02, x0 + 0.05, y1 + 0.02, 0.1, 1.2, "wood_dark")           # headboard
    s.box(x0 - 0.04, y0 + 0.1, x0 + 0.06, y1 - 0.1, 0.5, 1.08, "wood")                # inset panel
    s.box(x0 - 0.15, y0 - 0.05, x0 + 0.08, y1 + 0.05, 1.2, 1.28, "wood")               # cap
    s.box(x1 - 0.08, y0 - 0.01, x1, y1 + 0.01, 0.1, 0.62, "wood_dark")                 # footboard
    s.box(x0 + 0.06, y0 + 0.05, x1 - 0.09, y1 - 0.05, 0.4, 0.54, "pillow_white")       # mattress
    # duvet: one calm colour, hangs over the long sides a little
    s.box(x0 + 0.95, y0 - 0.04, x1 - 0.1, y1 + 0.04, 0.34, 0.68, "duvet_blue")
    # soft fold: turned-back sheet band + a low ridge
    s.box(x0 + 0.78, y0 - 0.04, x0 + 1.12, y1 + 0.04, 0.5, 0.74, "pillow_white")
    # pillows (two stacked soft boxes each)
    for (ya, yb) in ((y0 + 0.1, y0 + 0.7), (y0 + 0.76, y1 - 0.1)):
        s.box(x0 + 0.1, ya, x0 + 0.74, yb, 0.54, 0.74, "pillow_white")
    # folded blanket at the foot
    s.box(x1 - 0.62, y0 + 0.05, x1 - 0.14, y1 - 0.05, 0.68, 0.8, "blanket_mustard")
    s.set_solid(x0 - 0.12, y0 - 0.02, x1 - 0.001, y1 - 0.001)
    s.occluder(x0 - 0.12, y0 - 0.02, x1, y1, 1.3)


def desk_calm_x(s, dx0, dy0, dy1):
    """Desk on the west wall: top, two slab legs, one drawer, a laptop, a lamp and a mug. Nothing smaller."""
    s.box(dx0, dy0, dx0 + 0.72, dy1, 0.7, 0.76, "wood")
    for ya, yb in ((dy0, dy0 + 0.1), (dy1 - 0.1, dy1)):
        s.box(dx0 + 0.04, ya + 0.0, dx0 + 0.68, yb, 0.0, 0.7, "wood_dark")
    s.box(dx0 + 0.12, dy0 + 0.1, dx0 + 0.6, dy1 - 0.1, 0.5, 0.7, "wood_dark")           # modesty panel
    s.box(dx0 + 0.72, dy0 + 0.3, dx0 + 0.74, dy0 + 0.9, 0.52, 0.66, "wood")             # drawer front
    s.box(dx0 + 0.74, dy0 + 0.55, dx0 + 0.77, dy0 + 0.65, 0.57, 0.6, "brass")
    s.box(dx0 + 0.2, dy0 + 0.22, dx0 + 0.58, dy0 + 0.74, 0.76, 0.8, "metal_light")       # laptop base
    s.box(dx0 + 0.2, dy0 + 0.22, dx0 + 0.24, dy0 + 0.74, 0.8, 1.08, "metal_dark")        # lid
    s.box(dx0 + 0.24, dy0 + 0.27, dx0 + 0.25, dy0 + 0.69, 0.84, 1.04, "tv_screen")
    s.cyl(dx0 + 0.3, dy1 - 0.22, 0.76, 0.82, 0.12, "brass")                              # lamp
    s.cyl(dx0 + 0.3, dy1 - 0.22, 0.82, 1.2, 0.025, "brass")
    s.cyl(dx0 + 0.3, dy1 - 0.22, 1.05, 1.35, 0.17, "lamp_shade", r2=0.1)
    s.point_light(dx0 + 0.3, dy1 - 0.22, 1.3, 60, colour=(1.0, 0.8, 0.5), radius=0.12)
    s.cyl(dx0 + 0.55, dy0 + 0.9, 0.76, 0.9, 0.06, "pot")
    s.set_solid(dx0, dy0, dx0 + 0.719, dy1 - 0.001)
    s.occluder(dx0, dy0, dx0 + 0.72, dy1, 1.0)


def room_b2():
    """Variant B2: variant B (butter-yellow walls, big window with seat) with calmer, larger furniture."""
    WH = 2.8
    s = room_shell("room_b2", "Room above the shop (B2)", "wp_cream", "wood_red", WH, 84, hole=(4.6, 5.8, 3.5, 6.0))
    wx0, wx1, wz0, wz1 = 0.9, 4.2, 0.9, 2.35
    s.box(wx0 - 0.15, -0.4, wx1 + 0.15, 0.0, 0.0, wz0 - 0.1, "wp_cream")
    s.box(wx0 - 0.15, -0.4, wx1 + 0.15, 0.0, wz1 + 0.1, WH, "wp_cream")
    s.box(wx0 - 0.15, -0.4, wx0, 0.0, wz0 - 0.1, wz1 + 0.1, "wp_cream")
    s.box(wx1, -0.4, wx1 + 0.15, 0.0, wz0 - 0.1, wz1 + 0.1, "wp_cream")
    window_street(s, wx0, wx1, wz0, wz1)
    # window seat: wooden box, ONE long mustard cushion, ONE teal pillow
    s.box(wx0 - 0.15, 0.05, wx1 + 0.15, 0.78, 0.0, 0.42, "wood")
    s.box(wx0 - 0.15, 0.78, wx1 + 0.15, 0.82, 0.05, 0.38, "wood_dark")
    s.box(wx0 - 0.08, 0.1, wx1 + 0.08, 0.76, 0.42, 0.54, "blanket_mustard")
    s.box(wx0 + 0.1, 0.16, wx0 + 0.72, 0.58, 0.54, 0.7, "rug_teal")
    s.set_solid(wx0 - 0.15, 0.05, wx1 + 0.149, 0.78)
    s.occluder(wx0 - 0.15, 0.05, wx1 + 0.15, 0.78, 0.6)
    # bed (back-right), bedside table with a lamp, wardrobe, desk
    bed_calm_x(s, 4.85, 0.12)
    s.box(4.3, 0.05, 4.78, 0.55, 0, 0.5, "wood")
    s.box(4.34, 0.55, 4.74, 0.57, 0.1, 0.4, "wood_dark") if False else None
    s.cyl(4.54, 0.3, 0.5, 0.58, 0.09, "brass")
    s.cyl(4.54, 0.3, 0.58, 0.95, 0.15, "lamp_shade", r2=0.1)
    s.set_solid(4.3, 0.05, 4.779, 0.549)
    s.point_light(4.54, 0.3, 0.9, 50, colour=(1.0, 0.78, 0.45), radius=0.12)
    wardrobe_x(s, 1.3, 3.0)
    desk_calm_x(s, 0.1, 3.3, 5.0)
    s.prop("house/Chair_1", 1.55, 4.15, rot=270, h=0.9, colours={"Wood": "#9a6a3a"}, solid=True)
    # walls: apron on its hook, clock, one sea picture, one wall shelf with three big things
    apron_hook_x(s, 5.4, 1.35)
    wall_clock_x(s, 0.0, 0.6, 2.15, 0.2)
    picture_x(s, 3.45, 4.55, 0.0, 1.5, 2.25, "picture_sea")
    picture_y(s, 5.3, 6.2, 0.0, 1.9, 2.5, "picture_sea")
    s.box(0.0, 5.5, 0.35, 6.9, 1.55, 1.6, "wood")
    s.box(0.05, 5.55, 0.32, 5.95, 1.6, 1.88, "metal_dark")                                 # little radio
    s.cyl(0.18, 5.75, 1.88, 1.93, 0.05, "metal_light")
    s.box(0.05, 6.15, 0.3, 6.75, 1.6, 1.86, "book_d")                                       # one stack of books
    s.box(0.07, 6.2, 0.28, 6.7, 1.86, 1.93, "paper_cream")
    potted_plant(s, 0.55, 6.6, "flowers")
    # one calm rug: terracotta field with a cream border
    s.box(1.7, 1.9, 3.9, 4.4, 0.0, 0.012, "rug_cream", layer="floor")
    s.box(1.88, 2.08, 3.72, 4.22, 0.012, 0.02, "rug_terra", layer="floor")
    # warm bulbs only (no multicolour)
    string_lights(s, [(0.9, 0.12), (4.2, 0.12), (7.8, 0.12)], z0=2.62)
    # floor: red sneakers by the bed, the backpack by the desk
    sx, sy = 6.5, 2.35
    for k in (0, 1):
        s.box(sx + k * 0.24, sy, sx + 0.2 + k * 0.24, sy + 0.36, 0, 0.1, "red_paint")
        s.box(sx + k * 0.24, sy, sx + 0.2 + k * 0.24, sy + 0.36, 0, 0.03, "paper_cream")
    bx, by = 2.3, 5.5
    s.box(bx, by, bx + 0.45, by + 0.3, 0, 0.5, "wood_blue")
    s.box(bx + 0.04, by + 0.3, bx + 0.41, by + 0.36, 0.05, 0.3, "wood_dark")
    s.set_solid(bx, by, bx + 0.449, by + 0.37)
    s.point_light(2.5, 0.5, 2.2, 190, colour=(1.0, 0.92, 0.75))
    s.point_light(5.5, 3.5, 2.4, 110, colour=(1.0, 0.85, 0.62))
    s.point_light(1.5, 5.0, 2.2, 50, colour=(1.0, 0.82, 0.55))
    stairwell(s, hole=(4.6, 5.8, 3.5, 6.0))
    return s


SCENES += [market_stairs, market_gate_a, market_gate_b, room_attic, room_plain, room_b2]
