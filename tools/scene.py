"""
Town Life - scene descriptions shared by the Blender renderer and the asset builder.

Coordinates
-----------
* x, y in CELLS (floats allowed). One cell = 16 engine world units = CELL_M metres.
  Engine +x goes down-right on screen, +y goes down-left.
* z in METRES.
Blender coordinates: X = x * CELL_M, Y = -y * CELL_M, Z = z.

A scene holds:
* prims: 3D primitives for Blender, each on layer "floor" (drawn below the player) or
  "objects" (drawn above or below the player depending on depth).
* solid cells, warps and occluders for the game engine.
"""

CELL_M = 0.75          # metres per cell
PX_PER_M_Z = 19.6 / CELL_M   # vertical screen pixels per metre of height


class Scene:
    def __init__(self, ident, name, w, h, origin_x, origin_y, img_w, img_h):
        self.ident, self.name = ident, name
        self.w, self.h = w, h
        self.origin_x, self.origin_y = origin_x, origin_y   # image pixel of world (0, 0)
        self.img_w, self.img_h = img_w, img_h
        self.prims = []
        self.solid = [[False] * w for _ in range(h)]
        self.warps = []
        self.occluders = []
        self.lights = []
        self.sun = True

    # -- primitives -----------------------------------------------------------------
    def box(self, x0, y0, x1, y1, z0, z1, mat, layer="objects", bevel=0.0):
        self.prims.append(dict(type="box", x0=x0, y0=y0, x1=x1, y1=y1, z0=z0, z1=z1, mat=mat,
                               layer=layer, bevel=bevel))

    def cyl(self, x, y, z0, z1, r, mat, layer="objects", verts=16):
        self.prims.append(dict(type="cyl", x=x, y=y, z0=z0, z1=z1, r=r, mat=mat, layer=layer, verts=verts))

    def sphere(self, x, y, z, r, mat, layer="objects", sz=1.0):
        self.prims.append(dict(type="sphere", x=x, y=y, z=z, r=r, mat=mat, layer=layer, sz=sz))

    def text(self, s, x, y, z, size, mat, face="left", layer="objects", extrude=0.01):
        """Text on a face. face 'left' = facing +y (down-left), 'right' = facing +x (down-right).
        (x, y, z) = centre of the text baseline area."""
        self.prims.append(dict(type="text", s=s, x=x, y=y, z=z, size=size, mat=mat, face=face,
                               layer=layer, extrude=extrude))

    def wedge(self, x0, y0, x1, y1, z_top, z_bottom, depth_axis, mat, layer="objects"):
        """Awning: a slanted slab sticking out of a wall. depth_axis 'y' = sticks out towards +y."""
        self.prims.append(dict(type="wedge", x0=x0, y0=y0, x1=x1, y1=y1, z_top=z_top, z_bottom=z_bottom,
                               axis=depth_axis, mat=mat, layer=layer))

    def point_light(self, x, y, z, energy, colour=(1.0, 0.85, 0.6), radius=0.3):
        self.lights.append(dict(x=x, y=y, z=z, energy=energy, colour=colour, radius=radius))

    # -- gameplay ---------------------------------------------------------------------
    def set_solid(self, x0, y0, x1, y1, value=True):
        for cy in range(int(y0), int(y1 + 0.999)):
            for cx in range(int(x0), int(x1 + 0.999)):
                if 0 <= cx < self.w and 0 <= cy < self.h:
                    self.solid[cy][cx] = value

    def occluder(self, x0, y0, x1, y1, height_m):
        """Footprint in cells + height in metres (screen bbox is computed by the asset builder)."""
        self.occluders.append((x0, y0, x1, y1, height_m))

    def warp(self, x0, y0, x1, y1, target, tx, ty, facing):
        """Trigger rect + target position in cells (floats)."""
        self.warps.append((x0, y0, x1, y1, target, tx, ty, facing))

    # -- projection (image pixels) ---------------------------------------------------------
    def proj(self, x, y, z=0.0):
        ux, uy = x * 16, y * 16
        return self.origin_x + ux - uy, self.origin_y + (ux + uy) / 2 - z * PX_PER_M_Z


# ---------------------------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------------------------
def window_left(s, x0, x1, y_face, z0, z1, frame="trim_white", glass="glass", sill=True):
    """Window on a face at plane y = y_face (facing +y)."""
    d = 0.03 / 0.75
    s.box(x0, y_face - d, x1, y_face + d, z0, z1, frame)
    s.box(x0 + 0.12, y_face - d, x1 - 0.12, y_face + 2 * d, z0 + 0.09, z1 - 0.09, glass)
    xm = (x0 + x1) / 2
    s.box(xm - 0.04, y_face - d, xm + 0.04, y_face + 2.5 * d, z0 + 0.09, z1 - 0.09, frame)
    if sill:
        s.box(x0 - 0.08, y_face - d, x1 + 0.08, y_face + 0.15, z0 - 0.08, z0, "stone")


def window_right(s, y0, y1, x_face, z0, z1, frame="trim_white", glass="glass", sill=True):
    """Window on a face at plane x = x_face (facing +x)."""
    d = 0.03 / 0.75
    s.box(x_face - d, y0, x_face + d, y1, z0, z1, frame)
    s.box(x_face - d, y0 + 0.12, x_face + 2 * d, y1 - 0.12, z0 + 0.09, z1 - 0.09, glass)
    ym = (y0 + y1) / 2
    s.box(x_face - d, ym - 0.04, x_face + 2.5 * d, ym + 0.04, z0 + 0.09, z1 - 0.09, frame)
    if sill:
        s.box(x_face - d, y0 - 0.08, x_face + 0.15, y1 + 0.08, z0 - 0.08, z0, "stone")


def door_left(s, x0, x1, y_face, z1, mat="wood_green", frame="trim_white"):
    d = 0.04 / 0.75
    s.box(x0 - 0.1, y_face - d, x1 + 0.1, y_face + d, 0, z1 + 0.12, frame)
    s.box(x0, y_face - d, x1, y_face + 1.5 * d, 0, z1, mat)
    s.box(x0 + 0.2, y_face - d, x1 - 0.2, y_face + 2 * d, z1 * 0.45, z1 - 0.2, "glass")
    s.box(x1 - 0.32, y_face, x1 - 0.22, y_face + 3 * d, z1 * 0.42, z1 * 0.47, "brass")


def door_right(s, y0, y1, x_face, z1, mat="wood_green", frame="trim_white"):
    d = 0.04 / 0.75
    s.box(x_face - d, y0 - 0.1, x_face + d, y1 + 0.1, 0, z1 + 0.12, frame)
    s.box(x_face - d, y0, x_face + 1.5 * d, y1, 0, z1, mat)
    s.box(x_face - d, y0 + 0.2, x_face + 2 * d, y1 - 0.2, z1 * 0.45, z1 - 0.2, "glass")
    s.box(x_face, y1 - 0.32, x_face + 3 * d, y1 - 0.22, z1 * 0.42, z1 * 0.47, "brass")


def flat_roof(s, x0, y0, x1, y1, z, rim="stone"):
    s.box(x0, y0, x1, y1, z, z + 0.04, "roof")
    t = 0.25
    s.box(x0, y1 - t, x1, y1, z, z + 0.35, rim)
    s.box(x1 - t, y0, x1, y1, z, z + 0.35, rim)
    s.box(x0, y0, x0 + t, y1, z, z + 0.35, rim)
    s.box(x0, y0, x1, y0 + t, z, z + 0.35, rim)


def tree(s, x, y, scale=1.0):
    s.cyl(x, y, 0, 1.6 * scale, 0.12 * scale, "trunk")
    for (dx, dy, dz, r) in ((0, 0, 2.6, 1.0), (-0.6, 0.3, 2.2, 0.75), (0.5, -0.4, 2.3, 0.75),
                            (0.3, 0.6, 2.0, 0.65), (-0.2, -0.5, 3.0, 0.7), (0.0, 0.2, 3.3, 0.55)):
        s.sphere(x + dx / CELL_M * scale, y + dy / CELL_M * scale, dz * scale, r * scale, "leaves")
    s.box(x - 0.9, y - 0.9, x + 0.9, y + 0.9, 0, 0.04, "soil", layer="floor")
    s.set_solid(x - 0.4, y - 0.4, x + 0.4, y + 0.4)
    s.occluder(x - 1.6, y - 1.6, x + 1.6, y + 1.6, 4.0 * scale)


def lamp_post(s, x, y):
    s.cyl(x, y, 0, 0.25, 0.1, "metal_dark")
    s.cyl(x, y, 0, 3.6, 0.07, "metal_dark")
    s.box(x - 0.22, y - 0.22, x + 0.22, y + 0.22, 3.55, 3.95, "lamp_glass")
    s.box(x - 0.28, y - 0.28, x + 0.28, y + 0.28, 3.95, 4.05, "metal_dark")
    s.set_solid(x - 0.2, y - 0.2, x + 0.2, y + 0.2)
    s.occluder(x - 0.4, y - 0.4, x + 0.4, y + 0.4, 4.1)


def planter(s, x, y):
    s.box(x - 0.45, y - 0.45, x + 0.45, y + 0.45, 0, 0.55, "pot")
    s.box(x - 0.38, y - 0.38, x + 0.38, y + 0.38, 0.5, 0.56, "soil")
    for (dx, dy, dz, r) in ((0, 0, 0.95, 0.38), (-0.18, 0.15, 0.8, 0.28), (0.2, -0.12, 0.82, 0.28),
                            (0.05, 0.2, 1.15, 0.24)):
        s.sphere(x + dx / CELL_M, y + dy / CELL_M, dz, r, "leaves_light")
    s.set_solid(x - 0.45, y - 0.45, x + 0.45, y + 0.45)
    s.occluder(x - 0.6, y - 0.6, x + 0.6, y + 0.6, 1.4)


def bench_along_x(s, x0, x1, y):
    s.box(x0, y - 0.25, x1, y + 0.25, 0.42, 0.48, "wood")
    s.box(x0, y - 0.3, x1, y - 0.22, 0.48, 0.9, "wood")
    for x in (x0 + 0.2, x1 - 0.2):
        s.box(x - 0.05, y - 0.3, x + 0.05, y + 0.25, 0, 0.45, "metal_dark")
    s.set_solid(x0, y - 0.3, x1, y + 0.3)
    s.occluder(x0, y - 0.4, x1, y + 0.4, 1.0)


def hydrant(s, x, y):
    s.cyl(x, y, 0, 0.7, 0.13, "red_paint")
    s.sphere(x, y, 0.7, 0.13, "red_paint")
    s.cyl(x, y, 0.38, 0.48, 0.2, "red_paint")
    s.set_solid(x - 0.3, y - 0.3, x + 0.3, y + 0.3)
    s.occluder(x - 0.4, y - 0.4, x + 0.4, y + 0.4, 0.9)


# ---------------------------------------------------------------------------------------------
# City Centre street corner (prototype)
# ---------------------------------------------------------------------------------------------
def street_corner():
    W, H = 28, 26
    s = Scene("city_centre", "City Centre", W, H, origin_x=H * 16 + 16, origin_y=208,
              img_w=(W + H) * 16 + 32, img_h=208 + (W + H) * 8 + 16)

    # ---- ground (floor layer) ----
    s.box(0, 0, W, 12, -0.1, 0.0, "paving", layer="floor")                # sidewalks
    s.box(0, 12, 11, H, -0.1, 0.0, "paving", layer="floor")
    s.box(19, 20, W, H, -0.1, 0.0, "paving", layer="floor")
    road_z = -0.02
    s.box(11, 12, W, 20, -0.1, road_z, "asphalt", layer="floor")           # road along x
    s.box(11, 20, 19, H, -0.1, road_z, "asphalt", layer="floor")           # road along y
    # curbs
    s.box(11, 11.85, W, 12.0, -0.1, 0.05, "curb", layer="floor")
    s.box(19, 20.0, W, 20.15, -0.1, 0.05, "curb", layer="floor")
    s.box(10.85, 12, 11.0, H, -0.1, 0.05, "curb", layer="floor")
    s.box(19.0, 20, 19.15, H, -0.1, 0.05, "curb", layer="floor")
    s.box(10.85, 11.85, 11.0, 12, -0.1, 0.05, "curb", layer="floor")
    # lane markings
    for x in range(20, W, 3):
        s.box(x, 15.9, x + 1.6, 16.1, road_z, road_z + 0.01, "paint_yellow", layer="floor")
    for y in range(21, H, 3):
        s.box(14.9, y, 15.1, y + 1.6, road_z, road_z + 0.01, "paint_yellow", layer="floor")
    # zebra crossings
    for i in range(6):
        y = 12.6 + i * 1.25
        s.box(19.6, y, 21.6, y + 0.6, road_z, road_z + 0.01, "paint_white", layer="floor")
    for i in range(6):
        x = 11.6 + i * 1.25
        s.box(x, 20.6, x + 0.6, 22.6, road_z, road_z + 0.01, "paint_white", layer="floor")
    # little park in the front corner
    s.box(22, 23, W, H, -0.1, 0.06, "grass", layer="floor")
    s.box(22, 23, W, 23.12, -0.1, 0.1, "curb", layer="floor")
    s.box(21.88, 23, 22, H, -0.1, 0.1, "curb", layer="floor")
    # entrance tiles in front of Corner Market
    s.box(11.6, 8.0, 14.4, 9.6, 0.0, 0.01, "tiles_checker", layer="floor")

    # ---- Corner Market: x 8..18, y 0..8, front face at y = 8 ----
    cm_h = 4.4
    s.box(8, 0, 18, 8, 0, cm_h, "brick_red")
    s.box(8, 7.9, 18, 8.05, 0, 0.45, "stone")                              # plinth
    window_left_shop(s, 8.6, 11.6, 8, 0.5, 2.5)
    window_left_shop(s, 14.4, 17.4, 8, 0.5, 2.5)
    door_left(s, 12.2, 13.8, 8, 2.3, mat="wood_green")
    # awning: green/white stripes sticking out
    x = 8.2
    i = 0
    while x < 17.8:
        s.wedge(x, 8, min(x + 0.5, 17.8), 9.3, 2.95, 2.55, "y", "awning_green" if i % 2 == 0 else "awning_white")
        x += 0.5
        i += 1
    # sign board
    s.box(8.8, 7.95, 17.2, 8.12, 3.05, 3.85, "sign_green")
    s.box(8.7, 7.95, 17.3, 8.15, 3.0, 3.07, "brass")
    s.box(8.7, 7.95, 17.3, 8.15, 3.83, 3.9, "brass")
    s.text("CORNER MARKET", 13.0, 8.13, 3.27, 0.42, "sign_text", face="left")
    s.box(8, 7.9, 18, 8.1, cm_h - 0.25, cm_h, "stone")                    # cornice
    flat_roof(s, 8, 0, 18, 8, cm_h)
    # right side (x = 18) is hidden by the apartments
    s.set_solid(8, 0, 17.999, 7.999)
    s.set_solid(12, 7, 13.999, 7.999, False)                                # door cells walkable
    s.occluder(8, 0, 18, 8, cm_h + 0.4)
    s.warp(12, 7, 14, 8, "corner_market", 6.0, 7.6, "up")

    # ---- apartments: x 18..28, y 0..8 ----
    ap_h = 7.2
    s.box(18, 0, 28, 8, 0, ap_h, "brick_brown")
    s.box(18, 7.9, 28, 8.05, 0, 0.5, "stone")
    for fl, z0 in enumerate((1.0, 4.1)):
        for xi in (19.0, 21.4, 24.6, 26.8):
            window_left(s, xi, xi + 1.4, 8, z0 + (0.0 if fl else 0.0), z0 + 1.9)
    door_left(s, 22.9, 24.1, 8, 2.3, mat="wood_blue")
    s.box(18, 7.9, 28, 8.1, 3.4, 3.55, "stone")                             # floor band
    s.box(18, 7.9, 28, 8.12, ap_h - 0.3, ap_h, "stone")
    flat_roof(s, 18, 0, 28, 8, ap_h)
    s.set_solid(18, 0, 27.999, 7.999)
    s.occluder(18, 0, 28, 8, ap_h + 0.4)

    # ---- glass office on the corner: x 0..8, y 0..8 ----
    of_h = 7.6
    s.box(0, 0, 8, 8, 0, of_h, "concrete")
    for z0 in (0.6, 2.5, 4.4):
        s.box(0.4, 7.95, 7.6, 8.06, z0, z0 + 1.5, "glass_office")
        s.box(7.95, 0.4, 8.06, 7.6, z0, z0 + 1.5, "glass_office")
        for k in range(1, 6):
            s.box(0.4 + k * 1.2, 7.95, 0.48 + k * 1.2, 8.1, z0, z0 + 1.5, "metal_light")
            s.box(7.95, 0.4 + k * 1.2, 8.1, 0.48 + k * 1.2, z0, z0 + 1.5, "metal_light")
    flat_roof(s, 0, 0, 8, 8, of_h, rim="metal_light")
    s.set_solid(0, 0, 7.999, 7.999)
    s.occluder(0, 0, 8, 8, of_h + 0.4)

    # ---- townhouses: x 0..7, front face at x = 7 ----
    for (y0, y1, mat, door_mat) in ((8, 15, "plaster_cream", "wood_red"), (15, 22, "plaster_mint", "wood_blue")):
        th = 6.2
        s.box(0, y0, 7, y1, 0, th, mat)
        s.box(6.9, y0, 7.05, y1, 0, 0.45, "stone")
        door_right(s, y0 + 3.0, y0 + 4.4, 7, 2.3, mat=door_mat)
        window_right(s, y0 + 0.8, y0 + 2.3, 7, 0.9, 2.5)
        window_right(s, y0 + 5.0, y1 - 0.6, 7, 0.9, 2.5)
        window_right(s, y0 + 0.8, y0 + 2.3, 7, 3.6, 5.2)
        window_right(s, y0 + 2.9, y0 + 4.4, 7, 3.6, 5.2)
        window_right(s, y0 + 5.0, y1 - 0.6, 7, 3.6, 5.2)
        s.box(6.9, y0, 7.12, y1, th - 0.35, th, "trim_white")
        s.box(6.75, y1 - 0.25, 7.05, y1 + 0.02, 0, th, "trim_white")
        flat_roof(s, 0, y0, 7, y1, th)
        s.set_solid(0, y0, 6.999, y1 - 0.001)
        s.occluder(0, y0, 7, y1, th + 0.4)
    # garden in front-left
    s.box(0, 22, 7, H, -0.1, 0.06, "grass", layer="floor")
    s.box(0, 22, 7.0, 22.12, -0.1, 0.1, "curb", layer="floor")
    tree(s, 3.5, 24.0)

    # ---- street furniture ----
    planter(s, 11.0, 9.2)
    planter(s, 15.0, 9.2)
    lamp_post(s, 9.4, 11.2)
    lamp_post(s, 20.5, 21.0)
    hydrant(s, 26.5, 10.5)
    bench_along_x(s, 23.0, 25.2, 21.3)
    tree(s, 24.5, 24.6)
    tree(s, 9.0, 23.5, 0.9)
    return s


def window_left_shop(s, x0, x1, y_face, z0, z1):
    """Shop window with goods on display (no transparent glass: goods sit in a lit recess)."""
    d = 0.03 / 0.75
    s.box(x0 - 0.12, y_face - d, x1 + 0.12, y_face + 1.5 * d, z0 - 0.12, z1 + 0.12, "wood_green")
    s.box(x0, y_face - 0.25, x1, y_face - 0.17, z0, z1, "shop_light")
    import random
    rnd = random.Random(int(x0 * 100))
    cols = ["goods_red", "goods_yellow", "goods_green", "goods_orange", "goods_blue", "goods_pink"]
    for shelf_z in (z0 + 0.05, z0 + 0.75, z0 + 1.4):
        s.box(x0 + 0.02, y_face - 0.15, x1 - 0.02, y_face + 0.02, shelf_z, shelf_z + 0.05, "wood")
        x = x0 + 0.1
        while x < x1 - 0.35:
            w = rnd.uniform(0.18, 0.32)
            hgt = rnd.uniform(0.25, 0.5)
            s.box(x, y_face - 0.12, x + w, y_face + 0.0, shelf_z + 0.05, shelf_z + 0.05 + hgt, rnd.choice(cols))
            x += w + 0.05
    s.box(x0, y_face + 2 * d, x1, y_face + 2.6 * d, z0 + (z1 - z0) * 0.48, z0 + (z1 - z0) * 0.5, "wood_green")


# ---------------------------------------------------------------------------------------------
# Corner Market interior
# ---------------------------------------------------------------------------------------------
def corner_market_interior():
    W, H = 12, 9
    s = Scene("corner_market", "Corner Market", W, H, origin_x=H * 16 + 24, origin_y=104,
              img_w=(W + H) * 16 + 48, img_h=104 + (W + H) * 8 + 24)
    s.sun = False
    s.box(0, 0, W, H, -0.1, 0.0, "floor_wood", layer="floor")
    s.box(5.2, H - 0.9, 6.8, H, 0.0, 0.015, "mat_red", layer="floor")
    # back walls (cutaway room like the classic iso life-sims)
    wall_h = 3.0
    s.box(-0.4, -0.4, W, 0, 0, wall_h, "wall_plaster")
    s.box(-0.4, 0, 0, H, 0, wall_h, "wall_plaster")
    s.box(0, 0, W, 0.05, 0, 0.9, "wood")                     # wainscot
    s.box(0, 0, 0.05, H, 0, 0.9, "wood")
    s.box(0, 0, W, 0.07, 0.88, 0.95, "wood_dark")
    s.box(0, 0, 0.07, H, 0.88, 0.95, "wood_dark")
    s.box(-0.4, -0.4, W, 0, wall_h, wall_h + 0.08, "wood_dark")
    s.box(-0.4, 0, 0, H, wall_h, wall_h + 0.08, "wood_dark")
    window_left(s, 7.0, 9.0, 0.0, 1.3, 2.5, frame="wood_dark", sill=False)
    s.occluder(-0.4, -0.4, W, 0.1, wall_h)
    s.occluder(-0.4, 0, 0.1, H, wall_h)

    import random
    rnd = random.Random(7)
    cols = ["goods_red", "goods_yellow", "goods_green", "goods_orange", "goods_blue", "goods_pink", "goods_white"]

    def shelf(x0, y0, x1, y1, h, face):
        s.box(x0, y0, x1, y1, 0, 0.12, "wood_dark")
        s.box(x0, y0, x1, y1, h - 0.05, h, "wood")
        levels = [0.12 + i * (h - 0.2) / 3 for i in range(3)]
        for lz in levels:
            s.box(x0, y0, x1, y1, lz, lz + 0.04, "wood")
            if face == "left":
                x = x0 + 0.08
                while x < x1 - 0.25:
                    w = rnd.uniform(0.14, 0.28)
                    s.box(x, y1 - 0.4, x + w, y1 - 0.05, lz + 0.04, lz + 0.04 + rnd.uniform(0.2, (h - 0.2) / 3 - 0.06),
                          rnd.choice(cols))
                    x += w + 0.04
        if face == "left":
            s.box(x0, y0, x0 + 0.06, y1, 0, h, "wood_dark")
            s.box(x1 - 0.06, y0, x1, y1, 0, h, "wood_dark")
            s.box(x0, y0, x1, y0 + 0.06, 0, h, "wood_dark")
        s.set_solid(x0, y0, x1 - 0.001, y1 - 0.001)
        s.occluder(x0, y0, x1, y1, h)

    shelf(0.6, 0.1, 6.2, 1.1, 2.1, "left")                  # wall shelf
    shelf(2.0, 3.4, 7.0, 4.5, 1.5, "left")                  # aisle shelf
    shelf(2.0, 5.4, 6.0, 6.5, 1.3, "left")                  # second aisle
    # fridge with lit glass doors
    s.box(9.4, 0.1, 11.9, 1.4, 0, 2.1, "fridge_white")
    s.box(9.55, 1.38, 11.75, 1.45, 0.15, 1.95, "fridge_glass")
    for k in range(1, 3):
        s.box(9.55 + k * 0.73, 1.38, 9.6 + k * 0.73, 1.5, 0.15, 1.95, "fridge_white")
    s.set_solid(9.4, 0.1, 11.899, 1.399)
    s.occluder(9.4, 0.1, 11.9, 1.4, 2.1)
    # counter with cash register
    s.box(8.4, 5.4, 11.0, 6.5, 0, 1.0, "wood")
    s.box(8.35, 5.35, 11.05, 6.55, 1.0, 1.06, "wood_dark")
    s.box(9.2, 5.7, 10.0, 6.2, 1.06, 1.3, "metal_dark")
    s.box(9.3, 5.75, 9.9, 6.15, 1.3, 1.36, "screen")
    s.set_solid(8.4, 5.4, 10.999, 6.499)
    s.occluder(8.4, 5.4, 11.0, 6.5, 1.4)
    # plant
    s.box(0.5, 7.0, 1.3, 7.8, 0, 0.5, "pot")
    for (dx, dy, dz, r) in ((0, 0, 0.9, 0.35), (-0.15, 0.1, 0.75, 0.3), (0.15, -0.1, 0.8, 0.28), (0.05, 0.05, 1.15, 0.25)):
        s.sphere(0.9 + dx / CELL_M, 7.4 + dy / CELL_M, dz, r, "leaves_light")
    s.set_solid(0.5, 7.0, 1.299, 7.799)
    s.occluder(0.4, 6.9, 1.4, 7.9, 1.4)
    # crates
    s.box(10.5, 7.2, 11.6, 8.2, 0, 0.55, "crate")
    s.box(10.7, 7.4, 11.4, 8.0, 0.55, 1.0, "crate")
    s.set_solid(10.5, 7.2, 11.599, 8.199)
    s.occluder(10.5, 7.2, 11.6, 8.2, 1.0)
    # warm lights
    s.point_light(4, 3, 2.8, 120)
    s.point_light(9, 5, 2.8, 100)
    s.point_light(3, 7, 2.6, 60)
    # exit
    s.warp(5, H - 0.6, 7, H, "city_centre", 13.0, 9.0, "down")
    return s


SCENES = [street_corner, corner_market_interior]
