"""s62 proposal: VaultMart = the Corner Market interior after the VaultTech takeover (cold).
  vaultmart_a : variant A, everything replaced (regimented shelf rows, kiosk bank at the door, robot-arm restock station)
  vaultmart_b : variant B, same layout as the Corner Market (every warm item swapped for its cold twin)
Both keep the L-shaped room, the storeroom, the stairs and the approved roll-down shutter gate (B) with the red STAFF ONLY sign."""
import random

import scene as scn
from scene import *   # noqa: F401,F403
import rooms55 as r55

WH = 3.2
SY = 5.0
W, H = 17, 18


# ---------------------------------------------------------------------------------------------
# cold kit
# ---------------------------------------------------------------------------------------------
def vm_pack(s, x, yf, z, w=0.3, h=0.3, d=0.22):
    """One identical boxed product facing +y: white box, cyan band, tiny gold V mark."""
    s.box(x, yf - d, x + w, yf, z, z + h, "vm_box")
    s.box(x - 0.008, yf - d - 0.008, x + w + 0.008, yf + 0.012, z + h * 0.38, z + h * 0.62, "vm_band")


def vm_row(s, x0, x1, yf, z, h=0.3, w=0.36, gap=0.05, d=0.24):
    x = x0 + 0.06
    while x + w < x1 - 0.06:
        vm_pack(s, x, yf, z, w, h, d)
        x += w + gap


def vm_label_strip(s, x0, x1, y1, lz):
    """Digital price label rail on the shelf edge: dark strip with little glowing price windows."""
    s.box(x0, y1 - 0.02, x1, y1 + 0.012, lz - 0.07, lz + 0.035, "vm_label")
    x = x0 + 0.12
    k = 0
    while x + 0.2 < x1 - 0.08:
        s.box(x, y1 + 0.012, x + 0.2, y1 + 0.024, lz - 0.055, lz - 0.01, "vm_glow" if k % 3 else "vm_amber")
        x += 1.1
        k += 1


def vm_gondola(s, x0, y0, x1, y1, h, levels=4, pack_h=None, solid=True):
    """White metal shelving, products facing +y, identical boxes, digital price rails, cyan header trim."""
    s.box(x0, y0, x1, y1, 0, 0.14, "vm_panel")
    ym = (y0 + y1) / 2
    s.box(x0, ym - 0.04, x1, ym + 0.04, 0.14, h, "vm_back")
    step = (h - 0.14) / levels
    for i in range(levels):
        lz = 0.14 + i * step
        s.box(x0, y0, x1, y1, lz, lz + 0.035, "vm_shelf")
        vm_row(s, x0, x1, y1 - 0.06, lz + 0.035, h=pack_h or min(0.32, step - 0.1))
        vm_label_strip(s, x0, x1, y1, lz)
    s.box(x0, y0, x1, y1, h - 0.03, h, "vm_shelf")
    s.box(x0, y1 - 0.03, x1, y1 + 0.02, h - 0.03, h + 0.06, "vm_band")                 # cyan header trim
    s.box(x0 + 0.05, y0 + 0.12, x1 - 0.05, y1 - 0.12, h, h + 0.07, "vm_led")            # built-in fluorescent bar on top
    s.box(x1 - 0.06, y0, x1, y1, 0, h + 0.05, "vm_frame")
    s.box(x0, y0, x0 + 0.06, y1, 0, h + 0.05, "vm_frame")
    if solid:
        s.set_solid(x0, y0, x1 - 0.001, y1 - 0.001)
        s.occluder(x0, y0, x1, y1, h + 0.3)


def vm_bin(s, x0, y0, x1, y1, h=0.5, z=0.0):
    """Pale display bin of identical grey 'produce' cubes (the old fruit crates)."""
    s.box(x0, y0, x1, y1, z, z + h, "vm_frame")
    s.box(x0 + 0.05, y0 + 0.05, x1 - 0.05, y1 - 0.05, z + h - 0.03, z + h, "vm_shelf")
    n = int((x1 - x0) / 0.22)
    for i in range(n):
        for j in range(int((y1 - y0) / 0.22)):
            xx, yy = x0 + 0.1 + i * 0.22, y0 + 0.1 + j * 0.22
            s.box(xx, yy, xx + 0.17, yy + 0.17, z + h, z + h + 0.12, "vm_grey_apple" if (i + j) % 2 else "vm_box2")


def kiosk(s, x, y, w=1.3, d=0.75, state="green"):
    """Self-checkout kiosk facing +y (customers stand at +y): white pedestal, scanner glass with red laser, big cyan screen on a
    mast, bagging shelf, card reader, status lamp, small gold V on the front."""
    s.box(x, y, x + w, y + d, 0, 0.95, "robot_white")
    s.box(x, y + d - 0.02, x + w, y + d + 0.01, 0.0, 0.1, "metal_dark")                    # kick plate
    s.box(x + 0.04, y + d - 0.01, x + 0.5, y + d + 0.01, 0.12, 0.88, "vm_panel")             # side recess panel
    s.box(x + 0.1, y + 0.1, x + 0.48, y + d - 0.1, 0.5, 0.54, "steel")                      # bagging shelf
    s.box(x + 0.54, y + 0.12, x + w - 0.1, y + d - 0.1, 0.95, 0.99, "metal_dark")            # scanner top
    s.box(x + 0.62, y + 0.28, x + w - 0.18, y + d - 0.28, 0.99, 1.0, "vm_screen_dk")
    s.box(x + 0.62, y + 0.35, x + w - 0.18, y + d - 0.36, 1.0, 1.008, "vm_redlamp")           # laser line
    s.box(x + 0.62, y + 0.1, x + w - 0.1, y + 0.2, 0.99, 1.62, "robot_white")                 # mast
    s.box(x + 0.5, y + 0.18, x + w - 0.04, y + 0.28, 1.12, 1.62, "metal_dark")               # screen housing
    s.box(x + 0.55, y + 0.28, x + w - 0.09, y + 0.3, 1.16, 1.58, "vm_screen")                # screen
    s.box(x + 0.7, y + 0.3, x + w - 0.24, y + 0.31, 1.34, 1.38, "vm_label")                  # screen text bars
    s.box(x + 0.7, y + 0.3, x + w - 0.4, y + 0.31, 1.22, 1.26, "vm_label")
    s.cyl(x + w - 0.22, y + 0.15, 1.62, 1.74, 0.07, "vm_green" if state == "green" else "vm_redlamp", verts=10)
    s.box(x + 0.08, y + d, x + 0.34, y + d + 0.03, 0.56, 0.86, "metal_dark")                 # card reader
    s.box(x + 0.12, y + d + 0.03, x + 0.3, y + d + 0.04, 0.78, 0.82, "vm_glow")
    s.text("V", x + w - 0.45, y + d + 0.025, 0.5, 0.34, "gold_bright", face="left", bold=True, extrude=0.012)
    s.set_solid(x, y, x + w - 0.001, y + d - 0.001)
    s.occluder(x, y, x + w, y + d, 1.8)


def robot_arm(s, bx, by, tx, ty, tz=1.45, carry=True):
    """Industrial robot arm on a hazard-striped plate: base drum, shoulder, two tubes, elbow with cyan eye, gripper holding a box
    towards (tx, ty, tz)."""
    for k in range(8):       # hazard frame on the floor
        a0 = bx - 0.75 + k * 0.1875
        s.box(a0, by - 0.75, a0 + 0.1875, by - 0.68, 0.0, 0.01 + 0.0005 * (k % 2), "price_yellow" if k % 2 == 0 else "hazard_black", layer="floor")
        s.box(a0, by + 0.68, a0 + 0.1875, by + 0.75, 0.0, 0.01 + 0.0005 * (k % 2), "price_yellow" if k % 2 == 0 else "hazard_black", layer="floor")
        s.box(bx - 0.75, a0, bx - 0.68, a0 + 0.1875, 0.0, 0.0115 + 0.0005 * (k % 2), "price_yellow" if k % 2 == 0 else "hazard_black", layer="floor")
        s.box(bx + 0.68, a0, bx + 0.75, a0 + 0.1875, 0.0, 0.0115 + 0.0005 * (k % 2), "price_yellow" if k % 2 == 0 else "hazard_black", layer="floor")
    s.cyl(bx, by, 0.0, 0.2, 0.42, "metal_dark", verts=24)
    s.cyl(bx, by, 0.2, 0.62, 0.26, "robot_white", verts=24)
    s.cyl(bx, by, 0.62, 0.7, 0.3, "gold", verts=24)
    s.cyl(bx, by, 0.7, 1.05, 0.2, "robot_white", verts=24)
    sh = (bx, by, 1.15)
    s.sphere(*sh, 0.2, "metal_dark")
    el = (bx + (tx - bx) * 0.22, by + (ty - by) * 0.22, 2.15)
    s.tube([sh, el], 0.14, "gold")
    s.sphere(*el, 0.2, "metal_dark")
    wr = (bx + (tx - bx) * 0.74, by + (ty - by) * 0.74, tz + 0.5)
    s.tube([el, wr], 0.11, "gold")
    s.sphere(*wr, 0.14, "metal_dark")
    s.sphere(el[0], el[1] + 0.17, el[2] + 0.02, 0.07, "vm_glow")                         # eye
    gx, gy = tx - 0.02, ty - 0.02
    s.box(gx - 0.12, gy - 0.12, gx + 0.12, gy + 0.12, tz + 0.18, tz + 0.34, "metal_dark")   # gripper palm
    s.box(gx - 0.16, gy - 0.14, gx - 0.11, gy + 0.14, tz - 0.12, tz + 0.2, "metal_dark")    # fingers
    s.box(gx + 0.11, gy - 0.14, gx + 0.16, gy + 0.14, tz - 0.12, tz + 0.2, "metal_dark")
    if carry:
        vm_pack(s, gx - 0.12, gy + 0.12, tz - 0.14, 0.24, 0.3, 0.24)
    s.set_solid(bx - 0.5, by - 0.5, bx + 0.499, by + 0.499)
    s.occluder(bx - 0.5, by - 0.5, bx + 0.5, by + 0.5, 2.5)


def camera_dome(s, x, y, z, wall="y"):
    """Black dome camera on a short white bracket, red recording dot."""
    if wall == "y":     # on a wall facing +y at y
        s.box(x - 0.1, y, x + 0.1, y + 0.1, z + 0.12, z + 0.17, "robot_white")
        s.sphere(x, y + 0.2, z + 0.1, 0.17, "metal_dark", sz=0.8)
        s.sphere(x, y + 0.34, z + 0.1, 0.035, "vm_redlamp")
    elif wall == "x":
        s.box(x, y - 0.1, x + 0.1, y + 0.1, z + 0.12, z + 0.17, "robot_white")
        s.sphere(x + 0.2, y, z + 0.1, 0.17, "metal_dark", sz=0.8)
        s.sphere(x + 0.34, y, z + 0.1, 0.035, "vm_redlamp")
    else:               # free-standing on top of a post: x, y, z = top
        s.sphere(x, y, z + 0.06, 0.17, "metal_dark", sz=0.8)
        s.sphere(x, y + 0.15, z + 0.05, 0.035, "vm_redlamp")


def sec_gate(s, cx=8.0, y=15.1):
    """Security gate at the entrance: two white pillars with cyan beam strips, a gold V plate, camera dome on top."""
    for px in (cx - 1.85, cx + 1.45):
        s.box(px, y, px + 0.4, y + 0.45, 0, 1.75, "robot_white")
        s.box(px - 0.02, y - 0.02, px + 0.42, y + 0.47, 1.75, 1.85, "metal_dark")
        s.box(px + (0.4 if px < cx else -0.02), y + 0.08, px + (0.42 if px < cx else 0.0), y + 0.37, 0.25, 1.55, "vm_glow")
        s.box(px + 0.06, y + 0.45, px + 0.34, y + 0.47, 1.05, 1.5, "metal_dark")
        s.text("V", px + 0.2, y + 0.475, 1.28, 0.3, "gold_bright", face="left", bold=True, extrude=0.01)
        s.set_solid(px, y, px + 0.399, y + 0.449)
        s.occluder(px, y, px + 0.4, y + 0.45, 1.9)
    camera_dome(s, cx - 1.65, y + 0.2, 1.85, wall="top")


def wall_light_y(s, x0, x1, y, z=2.9):
    s.box(x0, y, x1, y + 0.26, z, z + 0.1, "robot_white")
    s.box(x0 + 0.1, y + 0.02, x1 - 0.1, y + 0.24, z - 0.02, z, "vm_led")


def wall_light_x(s, y0, y1, x, z=2.9):
    s.box(x, y0, x + 0.26, y1, z, z + 0.1, "robot_white")
    s.box(x + 0.02, y0 + 0.1, x + 0.24, y1 - 0.1, z - 0.02, z, "vm_led")


def ceiling_rails(s, rows, x0, x1, z=3.12):
    """Hint of the ceiling: thin steel rails with hanging fluorescent strips (open view from above)."""
    for (ry, xa, xb) in rows:
        s.box(xa, ry - 0.03, xb, ry + 0.03, z, z + 0.05, "metal_dark")
        x = xa + 0.4
        while x + 2.4 < xb:
            s.box(x, ry - 0.14, x + 2.4, ry + 0.14, z - 0.1, z - 0.04, "vm_led")
            s.box(x - 0.03, ry - 0.17, x + 2.43, ry + 0.17, z - 0.04, z, "robot_white")
            x += 3.2


def vault_v_logo(s, x, y, z, size=0.9, face="left"):
    """Gold V in a navy roundel on a wall."""
    if face == "left":
        s.cyl(x, y, z, z + 0.06, size * 0.52, "vm_navy", axis="y", verts=32)
        s.cyl(x, y + 0.04, z, z + 0.03, size * 0.52 + 0.03, "gold", axis="y", verts=32) if False else None
        s.text("V", x, y + 0.075, z, size, "gold_bright", face="left", bold=True, extrude=0.02)
    else:
        s.cyl(x, y, z, z + 0.06, size * 0.52, "vm_navy", axis="x", verts=32)
        s.text("V", x + 0.075, y, z, size, "gold_bright", face="right", bold=True, extrude=0.02)


def sign_board_y(s, x0, x1, y, z0, z1, line1, line2=None, size1=0.3, size2=0.2):
    """Navy sign board with gold border and text on a +y facing wall."""
    s.box(x0 - 0.05, y, x1 + 0.05, y + 0.07, z0 - 0.05, z1 + 0.05, "gold")
    s.box(x0, y + 0.07, x1, y + 0.11, z0, z1, "vm_navy")
    xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
    if line2:
        s.text(line1, xm, y + 0.12, zm + (z1 - z0) * 0.2, size1, "gold_bright", face="left", bold=True, extrude=0.012)
        s.text(line2, xm, y + 0.12, zm - (z1 - z0) * 0.22, size2, "sign_white", face="left", bold=True, extrude=0.012)
    else:
        s.text(line1, xm, y + 0.12, zm, size1, "gold_bright", face="left", bold=True, extrude=0.012)


def flat_screen_y(s, x, y, z, w=1.2, h=0.7, kind=0):
    s.box(x - w / 2 - 0.04, y, x + w / 2 + 0.04, y + 0.06, z - 0.04, z + h + 0.04, "metal_dark")
    s.box(x - w / 2, y + 0.06, x + w / 2, y + 0.07, z, z + h, "vm_screen")
    if kind == 0:     # ad: gold V + two bars
        s.box(x - w * 0.4, y + 0.07, x - w * 0.1, y + 0.08, z + h * 0.2, z + h * 0.8, "vm_navy")
        s.box(x, y + 0.07, x + w * 0.4, y + 0.08, z + h * 0.55, z + h * 0.7, "vm_navy")
        s.box(x, y + 0.07, x + w * 0.3, y + 0.08, z + h * 0.3, z + h * 0.42, "vm_navy")
    else:
        for k in range(3):
            s.box(x - w * 0.4, y + 0.07, x + w * (0.4 - 0.12 * k), y + 0.08, z + h * (0.2 + 0.25 * k), z + h * (0.32 + 0.25 * k), "vm_navy")


def totem_sign(s, x, y, line, h=2.3):
    """Floor standing flag sign (self-checkout)."""
    s.box(x - 0.05, y - 0.05, x + 0.05, y + 0.05, 0, h, "metal_dark")
    s.box(x - 0.2, y - 0.2, x + 0.2, y + 0.2, 0, 0.06, "metal_dark")
    s.box(x - 0.7, y - 0.05, x + 0.7, y + 0.05, h - 0.55, h, "vm_navy")
    s.box(x - 0.72, y - 0.06, x + 0.72, y + 0.06, h - 0.58, h - 0.55, "gold")
    s.text(line, x, y + 0.07, h - 0.27, 0.15, "vm_glow", face="left", bold=True, extrude=0.01)
    s.set_solid(x - 0.2, y - 0.2, x + 0.2, y + 0.2)


# ---------------------------------------------------------------------------------------------
# shell shared by both variants
# ---------------------------------------------------------------------------------------------
def vm_shell(ident, title):
    s = Scene(ident, title, W, H, origin_x=H * 16 + 24, origin_y=64,
              img_w=(W + H) * 16 + 48, img_h=64 + (W + H) * 8 + 36)
    s.sun = False
    cutaway_floor(s, 0, SY, W, H, "vm_floor")
    cutaway_floor(s, 11, 0, W, SY, "vm_floor_store")
    # entrance: dark grey mat strip, gold edge, cyan guide lines toward the kiosks
    s.box(6.0, 16.2, 10.0, 17.7, 0.0, 0.02, "vm_carpet", layer="floor")
    s.box(6.0, 16.2, 10.0, 16.26, 0.02, 0.026, "gold", layer="floor")
    s.box(6.15, 16.35, 9.85, 17.6, 0.02, 0.026, "vm_panel", layer="floor") if False else None
    wall_y(s, -0.4, 10.6, SY, WH, paper="vm_wall", wains="vm_panel")
    wall_x(s, 0.0, SY, 11.0, WH, paper="vm_wall", wains="vm_panel")
    wall_x(s, SY, H - 0.4, 0.0, WH, paper="vm_wall", wains="vm_panel")
    wall_y(s, 10.6, W, 0.0, WH, paper="vm_wall", wains="vm_panel")
    wall_stub_y(s, 0, 6.0, H, mat="vm_wall")
    wall_stub_y(s, 10.0, W, H, mat="vm_wall")
    wall_stub_x(s, 0, H, W, mat="vm_wall")
    wall_stub_y(s, 11.0, 12.0, SY, mat="vm_wall")
    wall_stub_y(s, 15.0, W - 0.4, SY, mat="vm_wall")
    for jx in (12.0, 14.86):
        s.box(jx, SY - 0.4, jx + 0.14, SY, 0, 2.35, "metal_light")
    s.set_solid(0, 0, 11, SY - 0.001)
    s.set_solid(11, 4, 12, 5)
    s.set_solid(15, 4, 16.999, 5)
    s.set_solid(W - 1, 0, W, H)
    s.set_solid(0, H - 1, 6, H)
    s.set_solid(10, H - 1, W, H)
    s.occluder(-0.4, SY - 0.4, 10.6, SY + 0.1, WH)
    s.occluder(-0.4, SY, 0.1, H, WH)
    # wall mounted fluorescent trays
    wall_light_y(s, 0.6, 5.4, SY + 0.05)
    wall_light_y(s, 5.9, 10.2, SY + 0.05)
    wall_light_x(s, 6.2, 11.0, 0.05)
    wall_light_x(s, 12.2, 17.2, 0.05)
    wall_light_y(s, 11.6, 16.6, 0.05)
    wall_light_x(s, 0.6, 4.6, 11.05)
    # the shutter gate + stairs (approved)
    stairs_flight(s)
    r55.vault_gate_b(s)
    s.warp(14.25, 3.5, SX1, S_BOT, "player_room", 5.2, 3.0, "down")
    s.warp(6.5, 17.1, 9.5, H, "city_centre", 44.0, 19.0, "down")
    camera_dome(s, 9.9, SY + 0.05, 2.45, wall="y")
    camera_dome(s, 16.9, 0.05, 2.45, wall="y")
    return s


def storeroom(s):
    """Storeroom: steel shelves with identical white crates, stacked grey crates, the Valet robot's charging dock."""
    s.box(11.3, 0.1, 13.9, 0.9, 0, 0.1, "vm_panel")
    for lz in (0.1, 0.8, 1.5):
        s.box(11.3, 0.1, 13.9, 0.9, lz, lz + 0.04, "vm_shelf")
    for px in (11.3, 13.8):
        s.box(px, 0.1, px + 0.1, 0.9, 0, 2.0, "vm_frame")
    for lz in (0.14, 0.84, 1.54):
        x = 11.45
        for _ in range(4):
            s.box(x, 0.3, x + 0.5, 0.82, lz, lz + 0.55, "vm_box")
            s.box(x - 0.005, 0.3, x + 0.505, 0.83, lz + 0.2, lz + 0.32, "vm_band")
            x += 0.54
    s.set_solid(11.3, 0.1, 13.899, 0.899)
    s.occluder(11.3, 0.1, 13.9, 0.9, 2.1)
    for (bx, by, bw, bd, bz, bh) in ((11.15, 1.4, 0.8, 0.9, 0, 0.55), (11.2, 1.45, 0.65, 0.7, 0.55, 0.45),
                                     (11.15, 2.4, 0.8, 0.8, 0, 0.5)):
        s.box(bx, by, bx + bw, by + bd, bz, bz + bh, "vm_box2")
        s.box(bx + 0.02, by + bd - 0.005, bx + bw - 0.02, by + bd + 0.012, bz + bh * 0.4, bz + bh * 0.6, "vm_band")
    s.set_solid(11.1, 1.3, 11.999, 3.299)
    s.occluder(11.1, 1.3, 12.0, 3.3, 1.1)
    # charging dock (where the staff table was): pad + upright with a status light
    s.box(12.8, 1.9, 14.0, 2.9, 0, 0.06, "metal_dark")
    s.box(12.85, 1.95, 13.95, 2.85, 0.06, 0.075, "vm_glow")
    s.box(13.55, 1.95, 13.95, 2.15, 0.075, 1.35, "robot_white")
    s.box(13.6, 2.15, 13.9, 2.17, 0.9, 1.2, "vm_screen")
    s.cyl(13.75, 2.05, 1.35, 1.45, 0.07, "vm_green", verts=10)
    s.set_solid(12.8, 1.9, 13.999, 2.899)
    # wall bits
    wall_light_y(s, 11.6, 16.6, 0.05)
    s.box(11.0, 2.0, 11.06, 3.2, 1.6, 2.3, "vm_navy")
    s.text("NO STAFF CARD", 11.07, 2.6, 2.1, 0.12, "vm_glow", face="right", bold=True, extrude=0.006) if False else None
    flat_screen_y(s, 12.9, 0.05, 1.4, 1.2, 0.7, kind=1) if False else None
    for (lx, ly) in ((13.5, 2.5),):
        s.point_light(lx, ly, 2.6, 120, colour=(0.85, 0.95, 1.0))
    s.point_light(15.6, 1.6, 2.9, 190, colour=(0.8, 0.9, 1.0))


def fridge_cold(s, fx0, fx1, fy1, fh=2.2):
    """The old dairy fridge in cold white: identical white cartons with a cyan band, 'COLD' header."""
    s.box(fx0, 5.05, fx1, fy1, 0, 0.25, "fridge_white")
    s.box(fx0, 5.05, fx1, 5.4, 0.25, fh, "fridge_light")
    s.box(fx0, 5.05, fx1, fy1, fh - 0.25, fh, "fridge_white")
    s.box(fx0, 5.05, fx0 + 0.12, fy1, 0, fh, "fridge_white")
    s.box(fx1 - 0.12, 5.05, fx1, fy1, 0, fh, "fridge_white")
    for lz in (0.25, 0.85, 1.4):
        s.box(fx0, 5.05, fx1, fy1 - 0.1, lz, lz + 0.03, "metal_light")
        x = fx0 + 0.15
        while x + 0.2 < fx1 - 0.15:
            s.box(x, fy1 - 0.3, x + 0.2, fy1 - 0.1, lz + 0.03, lz + 0.36, "vm_box")
            s.box(x - 0.005, fy1 - 0.305, x + 0.205, fy1 - 0.09, lz + 0.14, lz + 0.22, "vm_band")
            x += 0.26
    for k in range(1, 3):
        xk = fx0 + k * (fx1 - fx0) / 3
        s.box(xk - 0.03, fy1 - 0.08, xk + 0.03, fy1, 0.25, fh - 0.25, "metal_light")
    s.box(fx0 + 0.5, fy1 - 0.05, fx1 - 0.5, fy1 + 0.02, fh + 0.05, fh + 0.4, "vm_navy")
    s.text("COLD", (fx0 + fx1) / 2, fy1 + 0.03, fh + 0.22, 0.24, "vm_glow", face="left", bold=True, extrude=0.01)
    s.set_solid(fx0, 5.05, fx1 - 0.001, fy1 - 0.001)
    s.occluder(fx0, 5.05, fx1, fy1, fh + 0.45)


def freezer_cold(s):
    cx0, cy0, cx1, cy1 = 0.15, 11.3, 1.7, 14.3
    s.box(cx0, cy0, cx1, cy1, 0, 0.85, "fridge_white")
    s.box(cx0 + 0.1, cy0 + 0.1, cx1 - 0.1, cy1 - 0.1, 0.78, 0.8, "frozen_blue")
    for (a, b, c, d) in ((cx0 - 0.03, cy0 - 0.03, cx1 + 0.03, cy0 + 0.1), (cx0 - 0.03, cy1 - 0.1, cx1 + 0.03, cy1 + 0.03),
                         (cx0 - 0.03, cy0, cx0 + 0.1, cy1), (cx1 - 0.1, cy0, cx1 + 0.03, cy1)):
        s.box(a, b, c, d, 0.85, 0.93, "metal_light")
    for i in range(10):
        for j in range(3):
            yy = cy0 + 0.25 + i * 0.255
            xx = cx0 + 0.25 + j * 0.42
            s.box(xx, yy, xx + 0.32, yy + 0.2, 0.8, 0.9, "vm_box")
    s.box(cx0 + 0.02, cy0 + 1.7, cx1 - 0.02, cy1 - 0.02, 0.93, 0.97, "glass_lid")
    s.box(cx0 + 0.02, cy0 + 1.7, cx1 - 0.02, cy0 + 1.78, 0.97, 1.0, "metal_light")
    s.box(cx0 + 0.3, cy0 + 0.3, cx0 + 0.9, cy0 + 0.36, 0.93, 0.97, "vm_glow") if False else None
    s.set_solid(cx0, cy0, cx1 - 0.001, cy1 - 0.001)
    s.occluder(cx0, cy0, cx1, cy1, 1.1)


def west_signs(s):
    """West wall: ad screens + a navy roundel instead of the clock and bunting."""
    # screens on the west wall (facing +x) are built mirrored with a tiny helper
    for (ya, za) in ((12.1, 1.6), (16.0, 1.6)):
        s.box(0.0, ya - 0.6, 0.06, ya + 0.6, za - 0.04, za + 0.74, "metal_dark")
        s.box(0.06, ya - 0.56, 0.075, ya + 0.56, za, za + 0.7, "vm_screen")
        s.box(0.075, ya - 0.4, 0.085, ya - 0.1, za + 0.12, za + 0.58, "vm_navy")
        s.box(0.075, ya + 0.05, 0.085, ya + 0.4, za + 0.38, za + 0.5, "vm_navy")
    vault_v_logo(s, 0.0, 12.9, 2.1, size=1.0, face="right") if False else None


def finish_lights(s):
    for (lx, ly) in ((3, 8), (7, 8), (12, 10), (3, 14), (8, 14), (13, 12)):
        s.point_light(lx, ly, 2.9, 150, colour=(0.82, 0.93, 1.0))
    s.point_light(9.5, 5.5, 1.8, 50, colour=(0.8, 0.92, 1.0))
    s.point_light(8.0, 16.5, 2.4, 90, colour=(0.85, 0.95, 1.0))


# ---------------------------------------------------------------------------------------------
# variant B: same layout as the Corner Market, every warm item swapped
# ---------------------------------------------------------------------------------------------
def vaultmart_b():
    s = vm_shell("vaultmart_b", "VaultMart B")
    storeroom(s)
    # north wall run
    vm_gondola(s, 1.2, 5.05, 6.0, 5.95, 2.0, levels=4)
    # bakery table -> sealed white loaf cabinet
    s.box(6.25, 5.1, 7.85, 5.9, 0, 0.85, "robot_white")
    s.box(6.2, 5.05, 7.9, 5.95, 0.85, 0.9, "vm_shelf")
    for bx in (6.45, 6.85, 7.25):
        s.box(bx, 5.45, bx + 0.32, 5.85, 0.9, 1.05, "vm_box2")
    s.box(6.1, SY, 8.0, SY + 0.06, 1.45, 2.15, "vm_navy")
    s.text("NUTRIENT LOAF", 7.05, SY + 0.07, 1.9, 0.14, "vm_glow", face="left", bold=True, extrude=0.008)
    s.text("$2", 7.05, SY + 0.07, 1.62, 0.2, "gold_bright", face="left", bold=True, extrude=0.01)
    s.set_solid(6.2, 5.05, 7.899, 5.949)
    s.occluder(6.2, 5.05, 7.9, 5.95, 1.1)
    fridge_cold(s, 8.2, 10.9, 6.3)
    # wall decor north: ad screens, V roundel, big sign
    sign_board_y(s, 1.4, 5.8, 5.9, 2.2, 3.0, "VAULTMART", "SMART SHOPPING", size1=0.42, size2=0.21)
    for px in (1.5, 5.6):
        s.box(px, 5.88, px + 0.1, 5.98, 2.0, 2.2, "metal_dark")
    vault_v_logo(s, 7.05, SY + 0.07, 2.62, size=0.8)
    flat_screen_y(s, 9.3, SY + 0.05, 2.15, 1.3, 0.75)
    # west run
    sw = SwapProxy(s)
    vm_gondola(sw, 6.15, 0.05, 10.85, 0.95, 2.0, levels=4)
    freezer_cold(s)
    # produce stand -> white bins
    s.box(0.0, 14.55, 0.07, 17.3, 1.75, 2.2, "vm_navy")
    s.text("FRESH?", 0.08, 15.95, 1.98, 0.2, "vm_glow", face="right", bold=True, extrude=0.008)
    s.box(0.2, 14.5, 1.7, 17.3, 0, 0.3, "vm_panel")
    for k in range(3):
        y0 = 14.6 + k * 0.92
        vm_bin(s, 0.35, y0, 1.55, y0 + 0.82, h=0.12, z=0.3)
    s.set_solid(0.2, 14.5, 1.699, 17.299)
    s.occluder(0.2, 14.5, 1.7, 17.3, 0.8)
    west_signs(s)
    # free-standing gondolas
    vm_gondola(s, 4.0, 9.05, 9.0, 9.95, 1.55, levels=3)
    vm_gondola(s, 4.0, 12.05, 9.0, 12.95, 1.55, levels=3)
    s.box(4.0, 9.95, 9.0, 10.0, 1.5, 1.65, "vm_navy")
    s.text("VAULT PRICE", 6.5, 10.02, 1.58, 0.16, "gold_bright", face="left", bold=True, extrude=0.008)
    s.box(4.0, 12.95, 9.0, 13.0, 1.5, 1.65, "vm_navy")
    s.text("SMART PICK", 6.5, 13.02, 1.58, 0.16, "gold_bright", face="left", bold=True, extrude=0.008)
    # produce island -> white island with identical boxes
    s.box(11.2, 8.2, 13.8, 9.5, 0, 0.6, "vm_frame")
    s.box(11.1, 8.1, 13.9, 9.6, 0.6, 0.66, "vm_shelf")
    for k in range(3):
        x0 = 11.17 + k * 0.86
        vm_bin(s, x0, 8.2, x0 + 0.8, 9.5, h=0.0, z=0.66)
    s.box(11.3, 9.6, 13.7, 9.64, 0.28, 0.5, "vm_label")
    s.set_solid(11.1, 8.1, 13.899, 9.599)
    s.occluder(11.1, 8.1, 13.9, 9.6, 1.2)
    # checkout -> 3 self-checkout kiosks in a row where the counter was (+ robot arm in the corner by the storeroom)
    for i, kx in enumerate((11.1, 12.55, 14.0)):
        kiosk(s, kx, 14.05, w=1.35, d=0.75, state="green" if i != 2 else "red")
    totem_sign(s, 10.7, 14.45, "SELF CHECKOUT")
    robot_arm(s, 12.5, 11.2, 12.8, 9.95, tz=0.95, carry=True)
    # entrance: security gate + door camera, cold planters gone
    sec_gate(s)
    for k in range(4):         # grey basket stack by the door
        z = k * 0.12
        s.box(5.0, 16.0 - 1.2, 5.9, 16.7 - 1.2, z, z + 0.1, "vm_box2") if False else None
    finish_lights(s)
    return s


# ---------------------------------------------------------------------------------------------
# variant A: everything replaced (regimented layout)
# ---------------------------------------------------------------------------------------------
def vaultmart_a():
    s = vm_shell("vaultmart_a", "VaultMart A")
    storeroom(s)
    # north wall: one long shelf bank + cold wall
    vm_gondola(s, 1.2, 5.05, 8.0, 5.95, 2.05, levels=4)
    fridge_cold(s, 8.2, 10.9, 6.3)
    sign_board_y(s, 1.5, 7.7, 5.9, 2.25, 3.05, "VAULTMART", "SMART SHOPPING", size1=0.48, size2=0.23)
    for px in (1.6, 7.5):
        s.box(px, 5.88, px + 0.1, 5.98, 2.05, 2.25, "metal_dark")
    vault_v_logo(s, 8.9, SY + 0.07, 2.6, size=0.75)
    flat_screen_y(s, 9.9, SY + 0.05, 2.25, 0.9, 0.55, kind=1)
    west_signs(s)
    # west wall: shelves + freezer + produce bins (lined up)
    sw = SwapProxy(s)
    vm_gondola(sw, 6.15, 0.05, 10.85, 0.95, 2.0, levels=4)
    freezer_cold(s)
    s.box(0.2, 14.5, 1.7, 17.3, 0, 0.3, "vm_panel")
    for k in range(3):
        y0 = 14.6 + k * 0.92
        vm_bin(s, 0.35, y0, 1.55, y0 + 0.82, h=0.12, z=0.3)
    s.set_solid(0.2, 14.5, 1.699, 17.299)
    s.occluder(0.2, 14.5, 1.7, 17.3, 0.8)
    # three long identical rows
    for (yy, tag) in ((8.0, "SAVE"), (10.9, "SMART PICK"), (13.4, "VAULT PRICE")):
        vm_gondola(s, 2.4, yy, 8.8, yy + 0.8, 1.55, levels=3)
        s.box(2.4, yy + 0.8, 8.8, yy + 0.85, 1.5, 1.65, "vm_navy")
        s.text(tag, 5.6, yy + 0.87, 1.58, 0.16, "gold_bright", face="left", bold=True, extrude=0.008)
    # restock station (robot arm beside a shelf bank)
    vm_gondola(s, 11.1, 7.4, 14.9, 8.2, 1.7, levels=3)
    for k in range(3):
        s.box(11.4 + k * 0.52, 8.35, 11.8 + k * 0.52, 8.7, 0.0, 0.25 + 0.2 * (k % 2), "vm_box2") if False else None
    robot_arm(s, 13.0, 9.9, 13.3, 8.55, tz=1.05)
    # pallet of crates next to the arm
    s.box(14.2, 9.4, 15.4, 10.4, 0.0, 0.12, "metal_dark")
    for (i, j) in ((0, 0), (1, 0), (0, 1)):
        s.box(14.25 + i * 0.55, 9.45 + j * 0.48, 14.75 + i * 0.55, 9.9 + j * 0.48, 0.12, 0.45, "vm_box")
        s.box(14.24 + i * 0.55, 9.9 + j * 0.48, 14.76 + i * 0.55, 9.915 + j * 0.48, 0.24, 0.34, "vm_band")
    s.set_solid(14.2, 9.4, 15.399, 10.399)
    s.occluder(14.2, 9.4, 15.4, 10.4, 0.6)
    # kiosk bank near the door, facing the entrance
    for i, kx in enumerate((10.9, 12.5, 14.1)):
        kiosk(s, kx, 13.3, w=1.45, d=0.75, state="green" if i != 1 else "red")
    totem_sign(s, 10.55, 13.6, "SELF CHECKOUT")
    # gold V inlay in the floor + cyan guide line
    s.cyl(8.0, 14.6, 0.0, 0.02, 0.0, "gold", layer="floor") if False else None
    s.box(7.2, 14.35, 8.8, 14.4, 0.0, 0.012, "vm_stripe", layer="floor")
    sec_gate(s)
    finish_lights(s)
    return s


SCENES.extend([vaultmart_a, vaultmart_b])
