"""Owner feedback round (s49): proposal helpers and scenes. Nothing here is used by the game yet.

Import this module AFTER `scene` (it patches/extends it) from a Blender wrapper (render_scene.py):
  - street_bin_v2 / indoor_bin: new bins (patch scn.trash_can with one of them to see them in context)
  - sink_unit_v3: clearer wash basin (white bowl with a dark inside, chrome mixer tap, mirror with a sheen)
  - public_toilet_v3: wet-floor sign moved to the mop corner, new sink, indoor pedal bin
  - deposit_machine: "RETURN & EARN" reverse-vending machine (own design), placed against the park toilet
  - PROPOSAL_MATERIALS: extra materials the wrapper adds to blender_render.MATERIALS
"""
import math
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import scene as scn   # noqa: E402

PROPOSAL_MATERIALS = {
    "bin_steel_green": dict(c="#2f7a56", rough=0.38, metal=0.55),       # powder-coated dark green steel
    "bin_galv": dict(c="#aeb6c0", rough=0.3, metal=0.8),                # galvanised bands and lid
    "bin_hole": dict(c="#101418", rough=0.9),
    "bin_label": dict(c="#f4f0e0", rough=0.6),
    "bin_plastic_white": dict(c="#f1f1ea", rough=0.35),                 # indoor plastic pedal bin
    "bin_plastic_blue": dict(c="#4f86c6", rough=0.35),
    "rvm_green": dict(c="#1d8a5e", rough=0.35, metal=0.3),             # machine body
    "rvm_dark": dict(c="#1a2a24", rough=0.5, metal=0.5),
    "rvm_screen": dict(c="#5fe8d0", emit=1.4, emit_c="#6ff0d8"),
    "rvm_lamp_g": dict(c="#4cff7a", emit=2.5, emit_c="#5cff88"),
    "rvm_lamp_y": dict(c="#ffd23a", emit=2.5, emit_c="#ffd860"),
    "rvm_sign": dict(c="#f6fff6", emit=1.1, emit_c="#f6fff6"),                   # lit sign panel
    "mirror_sheen": dict(c="#cfe8f6", emit=0.5, emit_c="#dff0fa"),
}


class O:
    """Orientation helper: build an object facing +y (face='y', `a` runs along +x = screen right) or +x (face='x',
    `a` runs along -y = screen right) from one description. Origin (ox, oy) = the left end of the front line."""

    def __init__(self, s, ox, oy, face="y", ka=1.0, kz=1.0, kr=1.0):
        self.s, self.ox, self.oy, self.face = s, ox, oy, face
        self.ka, self.kz, self.kr = ka, kz, kr           # scale of a / d (cells), of heights, of radii and text

    def pt(self, a, d):
        a, d = a * self.ka, d * self.ka
        return (self.ox + a, self.oy + d) if self.face == "y" else (self.ox + d, self.oy - a)

    def box(self, a0, d0, a1, d1, z0, z1, mat, **k):
        (x0, y0), (x1, y1) = self.pt(a0, d0), self.pt(a1, d1)
        self.s.box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), z0 * self.kz, z1 * self.kz, mat, **k)

    def cyl(self, a, d, z0, z1, r, mat, axis="z", **k):
        x, y = self.pt(a, d)
        if axis == "d":
            axis = "y" if self.face == "y" else "x"
            self.s.cyl(x, y, z0 * self.kz, z0 * self.kz + (z1 - z0) * self.kr, r * self.kr, mat, axis=axis, **k)
        else:
            self.s.cyl(x, y, z0 * self.kz, z1 * self.kz, r * self.kr, mat, axis=axis, **k)

    def text(self, t, a, d, z, size, mat):
        x, y = self.pt(a, d)
        self.s.text(t, x, y, z * self.kz, size * self.kr, mat, face="left" if self.face == "y" else "right")

    def solid(self, a0, d0, a1, d1):
        (x0, y0), (x1, y1) = self.pt(a0, d0), self.pt(a1, d1)
        self.s.set_solid(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

    def occ(self, a0, d0, a1, d1, h):
        (x0, y0), (x1, y1) = self.pt(a0, d0), self.pt(a1, d1)
        self.s.occluder(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), h * self.kz)


# ----------------------------------------------------------------------------------------------- bins
def street_bin_v2(s, x, y, tint=None):
    """Urban steel litter bin: dark green powder-coated drum on a dark plinth, galvanised bands, rows of dark
    perforation slots, galvanised domed lid with a dark mouth on the two visible sides, small label, ash plate.
    (cyl radii are in metres, x / y offsets in cells = metres / 0.75)"""
    C = 1 / 0.75
    R = 0.27 * C                                                                           # drum radius in cells
    s.cyl(x, y, 0.0, 0.1, 0.31, "metal_dark", verts=16)                                     # plinth ring
    s.cyl(x, y, 0.1, 0.94, 0.27, "bin_steel_green", verts=16)                               # drum
    for z, m in ((0.13, "bin_galv"), (0.49, "goods_yellow"), (0.89, "bin_galv")):
        s.cyl(x, y, z, z + 0.055, 0.285, m, verts=16)                                       # bands (middle one: yellow)
    for z0, offs in ((0.22, 0), (0.6, 1)):                                                  # perforation slots
        for k in range(5):
            th = math.radians(10 + k * 17.5 + offs * 8.5)
            px, py = x + R * math.cos(th), y + R * math.sin(th)
            s.box(px - 0.04, py - 0.04, px + 0.04, py + 0.04, z0, z0 + 0.2, "bin_hole")
    s.cyl(x, y, 0.94, 1.02, 0.31, "bin_galv", verts=16)                                      # lid rim
    s.cyl(x, y, 1.02, 1.14, 0.28, "bin_galv", verts=16, r2=0.17)                             # dome
    s.box(x - 0.14, y + R - 0.03, x + 0.14, y + R + 0.07, 0.96, 1.07, "bin_hole")            # mouth (+y side)
    s.box(x + R - 0.03, y - 0.14, x + R + 0.07, y + 0.14, 0.96, 1.07, "bin_hole")            # mouth (+x side)
    s.set_solid(x - 0.3, y - 0.3, x + 0.3, y + 0.3)
    s.occluder(x - 0.4, y - 0.4, x + 0.4, y + 0.4, 1.15)


def indoor_bin(s, x, y, tint=None):
    """Small indoor pedal bin: off-white plastic body, blue lid with a white knob, chrome pedal, chrome band."""
    s.cyl(x, y, 0.03, 0.5, 0.17, "bin_plastic_white", verts=16, r2=0.19)
    s.cyl(x, y, 0.36, 0.4, 0.185, "chrome", verts=16)
    s.cyl(x, y, 0.5, 0.56, 0.205, "bin_plastic_blue", verts=16)
    s.cyl(x, y, 0.56, 0.62, 0.18, "bin_plastic_blue", verts=16, r2=0.12)
    s.cyl(x, y, 0.62, 0.66, 0.04, "bin_plastic_white", verts=8)
    s.box(x - 0.07, y + 0.2, x + 0.07, y + 0.36, 0.0, 0.05, "chrome")                      # pedal
    s.box(x - 0.02, y + 0.18, x + 0.02, y + 0.22, 0.04, 0.3, "chrome")
    s.set_solid(x - 0.22, y - 0.22, x + 0.22, y + 0.22)
    s.occluder(x - 0.3, y - 0.3, x + 0.3, y + 0.3, 0.7)


# ----------------------------------------------------------------------------------------------- sink
class Swap(scn.SwapProxy):
    """SwapProxy plus poly()."""

    def poly(self, pts, mat, layer="objects"):
        return self.s.poly([(p[1], p[0], p[2]) for p in pts], mat, layer)

    def cyl(self, x, y, *a, axis="z", **k):
        return self.s.cyl(y, x, *a, axis={"x": "y", "y": "x"}.get(axis, axis), **k)


def sink_unit_v3(s, x, y, k=1.25):
    """Wash basin on the back wall (faces +y), readable at 1 px per cm: white pedestal and bowl with a DARK
    inside, big chrome mixer tap, soap dispenser, mirror with a thick white frame, a light-blue face and two
    diagonal white sheen strips. k = size factor."""
    X = lambda d: x + d * k
    Y = lambda d: y + d * k
    Z = lambda d: d * k
    s.cyl(x, Y(0.2), 0.0, Z(0.8), 0.12 * k, "bin_plastic_white", verts=12)                 # round pedestal
    s.box(X(-0.5), Y(0.0), X(0.5), Y(0.56), Z(0.78), Z(0.96), "robot_white")                # bowl body (thick)
    s.box(X(-0.38), Y(0.1), X(0.38), Y(0.48), Z(0.95), Z(0.99), "metal_dark")               # dark inside of the bowl
    s.cyl(x, Y(0.3), Z(0.95), Z(0.97), 0.05 * k, "chrome", verts=8)                         # drain
    s.cyl(x, Y(0.12), Z(0.96), Z(1.2), 0.04 * k, "chrome", verts=10)                        # tap column
    s.tube([(x, Y(0.12), Z(1.18)), (x, Y(0.22), Z(1.27)), (x, Y(0.36), Z(1.2))], 0.035 * k, "chrome")
    s.box(X(0.06), Y(0.08), X(0.22), Y(0.16), Z(1.1), Z(1.15), "chrome")                    # lever
    s.box(X(0.56), Y(0.0), X(0.74), Y(0.12), Z(0.95), Z(1.2), "goods_green")               # wall soap dispenser
    s.box(X(0.58), Y(0.12), X(0.72), Y(0.15), Z(1.1), Z(1.14), "metal_dark")
    s.cyl(x, Y(0.02), Z(1.72), Z(1.78), 0.42, "chrome", axis="y", verts=28)             # round mirror: chrome ring
    s.cyl(x, Y(0.05), Z(1.72), Z(1.76), 0.36, "mirror_sheen", axis="y", verts=28)       # light-blue glass
    s.cyl(x, Y(0.08), Z(1.72), Z(1.75), 0.17, "robot_white", axis="y", verts=20)         # sheen blob (reflected light)
    s.cyl(x - 0.1 * k, Y(0.08), Z(1.9), Z(1.93), 0.06, "robot_white", axis="y", verts=12)
    s.set_solid(X(-0.56), y, X(0.56), Y(0.6))
    s.occluder(X(-0.56), y, X(0.56), Y(0.6), Z(1.15))


# ----------------------------------------------------------------------------------------------- toilet
def public_toilet_v3():
    """Public toilet with the fixes of owner feedback 1 + 3: the wet-floor sign stands by the mop (back-right
    corner), the WC has free floor in front of it, a clearer sink, an indoor pedal bin."""
    W, H = 6, 6
    s = scn.std_room("public_toilet_v3", "Public toilet v3", W, H, "tile_floor_dirty", "plaster_bare", "tile_dirty", 1.7, 3.0,
                     (2, 5), "city_centre", 3.0, 40.9, mat_cols=("metal_dark", "stain"))
    scn.toilet_unit(s, 2.9, 0.0)
    s.box(2.2, 0.0, 3.7, 0.06, 2.3, 2.9, "sign_blue")
    s.text("WC", 2.95, 0.09, 2.6, 0.5, "robot_white", face="left")
    scn.window_x(s, 1.0, 2.4, 0.0, 1.5, 2.5)
    sink_unit_v3(Swap(s), 3.5, 0.0)
    s.box(0.0, 4.4, 0.3, 4.9, 1.1, 1.5, "chrome")                                            # hand dryer
    s.box(0.3, 4.5, 0.34, 4.8, 1.2, 1.4, "metal_dark")
    s.box(0.4, 0.0, 1.7, 0.05, 1.7, 2.5, "paper_cream")
    s.text("PLEASE KEEP", 1.05, 0.08, 2.3, 0.15, "metal_dark", face="left")
    s.text("CLEAN", 1.05, 0.08, 2.05, 0.15, "metal_dark", face="left")
    s.box(0.4, 0.0, 1.7, 0.3, 1.0, 1.05, "wood_dark")
    for i in range(4):
        s.cyl(0.65 + i * 0.28, 0.14, 1.05, 1.23, 0.1, "robot_white", verts=12)
    indoor_bin(s, 0.75, 1.15)                                                                # small pedal bin
    # mop + bucket + broom in the back-right corner
    s.cyl(4.55, 0.55, 0.0, 0.38, 0.22, "bucket_yellow", verts=14, r2=0.27)
    s.cyl(4.55, 0.55, 0.36, 0.38, 0.19, "stain", verts=14)
    s.tube([(4.5, 0.5, 0.3), (4.18, 0.2, 1.45)], 0.022, "wood")
    s.sphere(4.5, 0.5, 0.3, 0.1, "robot_white", sz=0.6)
    s.tube([(4.9, 0.18, 0.05), (4.78, 0.15, 1.45)], 0.022, "wood")
    s.box(4.72, 0.12, 4.98, 0.34, 0.0, 0.12, "goods_yellow")
    s.box(4.2, 0.0, 4.75, 0.05, 1.7, 2.3, "poster_yellow")
    s.box(4.3, 0.05, 4.65, 0.07, 1.95, 2.05, "metal_dark")
    s.box(4.3, 0.05, 4.55, 0.07, 1.8, 1.88, "metal_dark")
    # wet-floor A-frame sign: in the corner next to the mop, against the back wall, out of everybody's way
    s.box(5.2, 0.3, 5.75, 0.38, 0.0, 0.6, "goods_yellow")
    s.box(5.2, 0.5, 5.75, 0.58, 0.0, 0.6, "goods_yellow")
    s.set_solid(5.2, 0.3, 5.75, 0.58)
    for (gx, gz0, gz1) in ((1.9, 0.15, 1.4), (4.1, 0.15, 1.1)):
        s.box(gx, 0.0, gx + 0.1, 0.045, gz0, gz1, "stain")
    s.point_light(2.5, 2.5, 2.6, 85, colour=(0.9, 0.98, 1.0))
    s.point_light(4.5, 4.0, 2.6, 60, colour=(0.9, 0.98, 1.0))
    return s


# ----------------------------------------------------------------------------------------------- deposit machine
def deposit_machine(s, ox, oy, face="x", ka=1.6, kz=1.15, kr=1.35):
    """RETURN & EARN: reverse-vending machine, 1.5 x 0.9 cells (1.1 x 0.68 m), 2.0 m tall, green steel body with a
    steel hood, round rubber loading port, a screen, a receipt slot, a lit sign with a recycling mark and two
    status lamps. (ox, oy) = left end of the front line, front facing `face`."""
    o = O(s, ox, oy, face, ka, kz, kr)
    o.box(0.0, 0.0, 1.5, 0.9, 0.0, 0.16, "rvm_dark")                                       # plinth (flush, dark)
    o.box(0.02, 0.02, 1.48, 0.88, 0.16, 1.84, "rvm_green")                                  # body
    o.box(-0.04, -0.04, 1.54, 0.96, 1.84, 1.95, "steel")                                    # hood
    o.box(0.1, 0.9, 1.4, 0.94, 1.44, 1.8, "rvm_sign")                                    # sign panel
    o.box(0.1, 0.9, 1.4, 0.93, 1.44, 1.47, "rvm_green")
    o.text("RETURN", 0.95, 0.95, 1.7, 0.2, "rvm_green")
    o.text("& EARN", 0.95, 0.95, 1.52, 0.17, "rvm_green")
    o.cyl(0.3, 0.93, 1.62, 1.66, 0.14, "rvm_green", axis="d", verts=20)                     # recycling mark: ring ...
    o.cyl(0.3, 0.945, 1.62, 1.66, 0.085, "robot_white", axis="d", verts=20)
    for k in range(3):                                                                      # ... with three arrows
        th = math.radians(90 + 120 * k)
        ca, cz = 0.3 + 0.17 * math.cos(th), 1.64 + 0.115 * math.sin(th)
        o.box(ca - 0.045, 0.95, ca + 0.045, 0.97, cz - 0.03, cz + 0.03, "robot_white")
    o.cyl(0.4, 0.9, 1.15, 1.2, 0.22, "rvm_dark", axis="d", verts=24)                          # loading port (rubber ring)
    o.cyl(0.4, 0.93, 1.15, 1.2, 0.15, "metal_dark", axis="d", verts=24)                       # dark opening
    o.box(0.88, 0.9, 1.34, 0.95, 0.96, 1.36, "rvm_dark")                                     # screen bezel
    o.box(0.91, 0.95, 1.31, 0.97, 1.0, 1.32, "rvm_screen")                                   # screen
    o.text("0.00", 1.11, 0.98, 1.2, 0.14, "rvm_dark")
    o.box(0.95, 0.97, 1.27, 0.98, 1.04, 1.08, "rvm_dark")
    o.box(0.9, 0.9, 1.3, 0.97, 0.7, 0.86, "goods_yellow")                                    # receipt slot panel
    o.box(0.96, 0.97, 1.24, 0.99, 0.76, 0.8, "rvm_dark")                                     # slot
    o.box(0.1, 0.9, 0.76, 0.93, 0.26, 0.5, "robot_white")                                    # instructions label
    o.text("CANS+BOTTLES", 0.43, 0.94, 0.38, 0.1, "rvm_green")
    o.box(0.02, 0.9, 1.48, 0.93, 0.16, 0.24, "goods_yellow")                                 # hazard stripe at the foot
    o.cyl(0.35, 0.5, 1.95, 2.07, 0.07, "rvm_lamp_g", verts=10)                               # beacon lights on the hood
    o.cyl(1.15, 0.5, 1.95, 2.07, 0.07, "rvm_lamp_y", verts=10)
    o.solid(-0.02, -0.02, 1.52, 0.94)
    o.occ(-0.04, -0.04, 1.54, 0.96, 2.1)
    s.point_light(*o.pt(0.7, 1.7), 1.5, 60, colour=(0.8, 1.0, 0.9))


orig_trash = scn.trash_can


def city_with_machine():
    """Hook for the renderer: city_centre with the machine against the east wall of the park toilet."""
    orig = scn.park_toilet

    def park_toilet(s, x0, y0, x1, y1):
        orig(s, x0, y0, x1, y1)
        deposit_machine(s, x1 + 0.12, y0 + 2.3, "x")
    scn.park_toilet = park_toilet


def machine_lab():
    """Close-up lab: the machine facing +y (lit side) next to the proposed street bin, the current bin and the indoor bin."""
    W, H = 9, 7
    s = scn.Scene("machine_lab", "Machine lab", W, H, origin_x=H * 16 + 16, origin_y=110,
                  img_w=(W + H) * 16 + 32, img_h=110 + (W + H) * 8 + 16)
    s.box(0, 0, W, H, -0.1, 0.0, "paving", layer="floor")
    deposit_machine(s, 1.2, 1.2, "y", 1.6, 1.15, 1.35)
    street_bin_v2(s, 5.6, 2.4)
    orig_trash(s, 7.0, 2.4)
    indoor_bin(s, 5.6, 4.2)
    return s
