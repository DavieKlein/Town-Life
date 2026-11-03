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

import random

CELL_M = 0.75          # metres per cell
PX_PER_M_Z = 19.6 / CELL_M   # vertical screen pixels per metre of height


# Bounding boxes (metres, Blender axes, front facing -Y) of the CC0 Quaternius buildings in
# art_source/quaternius_buildings, measured after import.
MODEL_DIMS = {
    "1Story_GableRoof_Mat": ((-1.05, -1.19, -0.01), (1.05, 1.19, 2.02)),
    "1Story_Mat": ((-1.08, -1.1, -0.02), (1.08, 1.08, 1.66)),
    "1Story_RoundRoof_Mat": ((-1.05, -1.06, -0.02), (1.04, 1.06, 2.37)),
    "1Story_Sign_Mat": ((-1.08, -1.08, -0.02), (1.08, 1.08, 1.78)),
    "2Story_2_Mat": ((-1.08, -1.1, -0.02), (1.08, 1.08, 2.75)),
    "2Story_Balcony_Mat": ((-1.08, -1.45, -0.0), (1.08, 1.08, 2.94)),
    "2Story_Center_Mat": ((-1.21, -1.42, -0.0), (1.21, 1.08, 2.73)),
    "2Story_Columns_Mat": ((-1.08, -1.41, -0.01), (1.08, 1.08, 2.76)),
    "2Story_Double_Mat": ((-1.03, -1.45, -0.0), (1.39, 1.08, 2.74)),
    "2Story_GableRoof_Mat": ((-1.08, -1.19, -0.02), (1.08, 1.19, 3.12)),
    "2Story_Mat": ((-1.08, -1.45, -0.0), (1.08, 1.08, 2.74)),
    "2Story_RoundRoof_Mat": ((-1.06, -1.06, -0.02), (1.06, 1.06, 2.88)),
    "2Story_Sidehouse_Mat": ((-2.39, -1.26, -0.01), (1.07, 1.27, 2.75)),
    "2Story_Sign_Mat": ((-1.08, -1.08, -0.02), (1.08, 1.08, 2.74)),
    "2Story_Slim_Mat": ((-0.55, -1.08, -0.02), (0.57, 1.08, 2.74)),
    "2Story_Stairs_Mat": ((-1.08, -1.45, -0.0), (1.08, 1.08, 2.74)),
    "2Story_Wide_2Doors_Mat": ((-3.41, -1.18, -0.02), (3.41, 1.08, 2.73)),
    "2Story_Wide_Mat": ((-1.91, -1.18, -0.02), (1.91, 1.08, 2.73)),
    "3Story_Balcony_Mat": ((-1.08, -1.43, -0.0), (1.08, 1.08, 4.21)),
    "3Story_Slim_Mat": ((-0.55, -1.08, -0.02), (0.57, 1.08, 3.98)),
    "3Story_Small_Mat": ((-0.96, -0.93, -0.01), (0.95, 1.13, 3.84)),
    "4Story_Center_Mat": ((-1.21, -1.45, -0.0), (1.21, 1.08, 5.09)),
    "4Story_Mat": ((-1.03, -1.45, -0.0), (1.39, 1.08, 5.09)),
    "4Story_Wide_2Doors_Mat": ((-3.41, -1.62, -0.02), (3.41, 1.08, 5.13)),
    "4Story_Wide_2Doors_Roof_Mat": ((-3.41, -1.62, -0.02), (3.41, 1.08, 5.66)),
    "6Story_Stack_Mat": ((-1.08, -1.42, -0.0), (1.08, 1.08, 7.8)),
}


# Downtown City MegaKit models (art_source/quaternius_downtown, CC0): bounding boxes in metres,
# Blender axes at rotation 0 (facades face -Y = world +y = screen down-left; origin at the facade).
KIT_DIMS = {
    "Building_Medium_2_001": ((-7.528, -0.568, -0.01), (7.528, 12.488, 24.998)),
    "Prop_Bollard": ((-0.108, -0.114, 0.0), (0.108, 0.114, 0.892)),
    "Prop_ManholeCover": ((-0.463, -0.463, -0.014), (0.463, 0.463, 0.019)),
    "Prop_Planter_Single": ((-1.0, -1.0, 0.0), (1.0, 1.0, 0.6)),
    "Sidewalk_Planter": ((-0.987, -0.883, 0.0), (0.987, 0.883, 0.506)),
    "Prop_ACUnit": ((-0.411, -0.329, -0.0), (0.483, 0.019, 0.6)),
}


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
        self.lamps = []      # night light pools on the ground: (x, y) in cells
        self.sun = True

    # -- primitives -----------------------------------------------------------------
    def box(self, x0, y0, x1, y1, z0, z1, mat, layer="objects", bevel=0.0):
        self.prims.append(dict(type="box", x0=x0, y0=y0, x1=x1, y1=y1, z0=z0, z1=z1, mat=mat,
                               layer=layer, bevel=bevel))

    def cyl(self, x, y, z0, z1, r, mat, layer="objects", verts=16, r2=None):
        """Cylinder (or cone: r2 = top radius)."""
        self.prims.append(dict(type="cyl", x=x, y=y, z0=z0, z1=z1, r=r, mat=mat, layer=layer, verts=verts,
                               r2=r if r2 is None else r2))

    def poly(self, pts, mat, layer="objects"):
        """Flat polygon through points (x, y in cells, z in metres)."""
        self.prims.append(dict(type="poly", pts=[list(q) for q in pts], mat=mat, layer=layer))

    def tube(self, pts, r, mat, layer="objects"):
        """Smooth round tube through points (x, y in cells, z in metres)."""
        self.prims.append(dict(type="tube", pts=[list(q) for q in pts], r=r, mat=mat, layer=layer))

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

    def model(self, name, x, y, front="left", colours="red", scale=2.1, door=None, layer="objects"):
        """Places a CC0 Quaternius building (art_source/quaternius_buildings/<name>.fbx).
        front 'left': facade faces +y (down-left on screen); x = left edge, y = facade line (cells).
        front 'right': facade faces +x (down-right); x = facade line, y = top edge (cells).
        door: (cx, cy) cell that stays walkable. Returns the footprint (x0, y0, x1, y1) in cells."""
        mn, mx = MODEL_DIMS[name]
        w = (mx[0] - mn[0]) * scale / CELL_M
        d = (mx[1] - mn[1]) * scale / CELL_M
        height = (mx[2] - mn[2]) * scale
        if front == "left":
            fp = (x, y - d, x + w, y)
        else:
            fp = (x - d, y, x, y + w)
        self.prims.append(dict(type="model", name=name, fp=fp, front=front, colours=colours, scale=scale,
                               layer=layer))
        self.set_solid(fp[0], fp[1], fp[2] - 0.001, fp[3] - 0.001)
        if door:
            self.set_solid(door[0], door[1], door[0] + 0.999, door[1] + 0.999, False)
        self.occluder(fp[0], fp[1], fp[2], fp[3], height + 0.3)
        return fp

    def kit(self, name, x, y, rot=0, z=0.0, layer="objects", solid=True, occlude=True, scale=1.0):
        """Places a Downtown City MegaKit model with its origin at cell (x, y). rot in degrees (0 or 180
        for buildings: 0 = facade facing +y). Returns the footprint (x0, y0, x1, y1) in cells."""
        self.prims.append(dict(type="kit", name=name, x=x, y=y, z=z, rot=rot, layer=layer, scale=scale))
        mn, mx = KIT_DIMS[name]
        if rot % 360 == 0:
            fp = (x + mn[0] * scale / CELL_M, y - mx[1] * scale / CELL_M, x + mx[0] * scale / CELL_M,
                  y - mn[1] * scale / CELL_M)
        else:
            fp = (x - mx[0] * scale / CELL_M, y + mn[1] * scale / CELL_M, x - mn[0] * scale / CELL_M,
                  y + mx[1] * scale / CELL_M)
        if solid:
            self.set_solid(fp[0], fp[1], fp[2] - 0.001, fp[3] - 0.001)
        if occlude:
            self.occluder(fp[0], fp[1], fp[2], fp[3], (mx[2] - mn[2]) * scale + 0.2)
        return fp

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
    s.lamps.append((x, y))


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
def vaulttech_tower(s, x0, y0, x1, y1):
    """Victor Vault's golden VaultTech tower: podium + tall glass shaft with gold fins and a crown."""
    podium_h = 4.5
    s.box(x0, y0, x1, y1, 0, podium_h, "gold_dark")
    # podium glass front with gold mullions
    s.box(x0 + 0.6, y1 - 0.05, x1 - 0.6, y1 + 0.03, 0.4, podium_h - 0.6, "glass_office")
    x = x0 + 0.6
    while x <= x1 - 0.6:
        s.box(x - 0.06, y1 - 0.05, x + 0.06, y1 + 0.08, 0.4, podium_h - 0.6, "gold")
        x += 1.5
    s.box(x0, y1 - 0.1, x1, y1 + 0.12, podium_h - 0.6, podium_h, "gold")
    # entrance + sign
    xm = (x0 + x1) / 2
    s.box(xm - 2.0, y1 - 0.05, xm + 2.0, y1 + 0.1, 0, 3.0, "glass")
    s.box(xm - 2.2, y1 - 0.05, xm + 2.2, y1 + 0.15, 3.0, 3.25, "gold")
    s.box(xm - 3.6, y1 - 0.05, xm + 3.6, y1 + 0.14, podium_h + 0.2, podium_h + 1.2, "metal_dark")
    s.text("VAULTTECH", xm, y1 + 0.16, podium_h + 0.48, 0.62, "gold_bright", face="left")
    # shaft (inset), glass with gold fins and floor bands
    sx0, sy0, sx1, sy1 = x0 + 1.0, y0 + 1.0, x1 - 1.0, y1 - 1.0
    top = 34.0
    s.box(sx0, sy0, sx1, sy1, podium_h, top, "glass_office")
    x = sx0
    while x <= sx1 + 0.01:
        s.box(x - 0.08, sy1 - 0.02, x + 0.08, sy1 + 0.12, podium_h, top, "gold")
        x += 1.25
    y = sy0
    while y <= sy1 + 0.01:
        s.box(sx1 - 0.02, y - 0.08, sx1 + 0.12, y + 0.08, podium_h, top, "gold")
        y += 1.25
    z = podium_h + 3.0
    while z < top:
        s.box(sx0, sy1 - 0.02, sx1, sy1 + 0.1, z, z + 0.25, "gold")
        s.box(sx1 - 0.02, sy0, sx1 + 0.1, sy1, z, z + 0.25, "gold")
        z += 3.0
    s.box(sx0 + 0.6, sy0 + 0.6, sx1 - 0.6, sy1 - 0.6, top, top + 1.5, "gold")
    s.box(sx0 + 1.6, sy0 + 1.6, sx1 - 1.6, sy1 - 1.6, top + 1.5, top + 3.0, "gold")
    s.cyl((sx0 + sx1) / 2, (sy0 + sy1) / 2, top + 3.0, top + 8.0, 0.12, "gold")
    s.set_solid(x0, y0, x1 - 0.001, y1 - 0.001)
    s.occluder(x0, y0, x1, y1, top + 8.0)


def fountain(s, cx, cy, r=2.2):
    s.cyl(cx, cy, 0, 0.55, r * CELL_M, "stone", verts=24)
    s.cyl(cx, cy, 0.4, 0.5, r * CELL_M - 0.2, "water", verts=24)
    s.cyl(cx, cy, 0.5, 1.4, 0.35, "stone", verts=16)
    s.cyl(cx, cy, 1.4, 1.5, 0.9, "stone", verts=16)
    s.cyl(cx, cy, 1.45, 1.52, 0.75, "water", verts=16)
    s.cyl(cx, cy, 1.5, 2.1, 0.12, "stone", verts=10)
    s.sphere(cx, cy, 2.15, 0.16, "water")
    s.set_solid(cx - r, cy - r, cx + r - 0.001, cy + r - 0.001)
    s.occluder(cx - r, cy - r, cx + r, cy + r, 2.3)


def barrier(s, x0, x1, y, closed_sign=False):
    """Striped road barrier along x at row y."""
    s.box(x0, y - 0.15, x1, y + 0.15, 0.55, 0.85, "barrier_stripes")
    for x in (x0 + 0.3, (x0 + x1) / 2, x1 - 0.3):
        s.box(x - 0.08, y - 0.08, x + 0.08, y + 0.08, 0, 0.6, "metal_dark")
    if closed_sign:
        xm = (x0 + x1) / 2
        s.box(xm - 1.3, y - 0.05, xm + 1.3, y + 0.05, 0.9, 1.7, "red_paint")
        s.text("CLOSED", xm, y + 0.06, 1.18, 0.42, "paint_white", face="left")
    s.set_solid(x0, y - 0.3, x1 - 0.001, y + 0.299)
    s.occluder(x0, y - 0.4, x1, y + 0.4, 1.8 if closed_sign else 0.9)


def cone(s, x, y):
    s.cyl(x, y, 0, 0.55, 0.13, "orange_paint", verts=10)
    s.box(x - 0.25, y - 0.25, x + 0.25, y + 0.25, 0, 0.04, "orange_paint")


def bus_stop(s, x0, x1, y):
    """Bus shelter along x with its open side facing +y."""
    s.box(x0, y - 0.6, x1, y - 0.5, 0, 2.3, "glass_office")
    s.box(x0, y - 0.6, x0 + 0.08, y + 0.2, 0, 2.3, "metal_dark")
    s.box(x1 - 0.08, y - 0.6, x1, y + 0.2, 0, 2.3, "metal_dark")
    s.box(x0 - 0.1, y - 0.7, x1 + 0.1, y + 0.3, 2.3, 2.4, "metal_dark")
    s.box(x0 + 0.3, y - 0.5, x1 - 0.3, y - 0.2, 0.42, 0.48, "wood")
    s.box(x0 + 0.1, y - 0.5, x0 + 1.3, y - 0.45, 1.2, 2.1, "sign_blue")
    s.text("BUS", x0 + 0.7, y - 0.44, 1.55, 0.36, "paint_white", face="left")
    s.set_solid(x0, y - 0.7, x1 - 0.001, y - 0.3)
    s.occluder(x0, y - 0.7, x1, y + 0.3, 2.4)


def lamp_curved(s, x, y, arm="y"):
    """Street lamp with a curved arm reaching over the road (arm towards +y or -y)."""
    d = 1 if arm == "y" else -1
    s.cyl(x, y, 0, 0.3, 0.12, "metal_dark")
    s.cyl(x, y, 0, 4.2, 0.07, "metal_grey")
    s.tube([(x, y, 4.0), (x, y, 4.2), (x, y + d * 0.2 / CELL_M, 4.42), (x, y + d * 0.55 / CELL_M, 4.55),
            (x, y + d * 1.0 / CELL_M, 4.52)], 0.06, "metal_grey")
    s.box(x - 0.25, y + d * 1.0 / CELL_M - 0.3, x + 0.25, y + d * 1.0 / CELL_M + 0.3, 4.38, 4.5, "metal_grey")
    s.box(x - 0.2, y + d * 1.0 / CELL_M - 0.25, x + 0.2, y + d * 1.0 / CELL_M + 0.25, 4.34, 4.39, "lamp_glass")
    s.set_solid(x - 0.2, y - 0.2, x + 0.2, y + 0.2)
    s.occluder(x - 0.4, y - 0.4, x + 0.4, y + 0.4, 4.6)
    s.lamps.append((x, y + d * 1.0 / CELL_M))


def newspaper_box(s, x, y, colour="sign_blue"):
    s.box(x - 0.3, y - 0.25, x + 0.3, y + 0.25, 0.25, 1.05, colour)
    s.box(x - 0.24, y + 0.22, x + 0.24, y + 0.27, 0.55, 0.95, "glass")
    s.box(x - 0.18, y + 0.23, x + 0.18, y + 0.28, 0.6, 0.85, "print_cream")
    s.box(x - 0.3, y - 0.25, x + 0.3, y + 0.25, 1.05, 1.1, "metal_dark")
    for (dx, dy) in ((-0.2, -0.15), (0.2, -0.15), (-0.2, 0.15), (0.2, 0.15)):
        s.box(x + dx - 0.03, y + dy - 0.03, x + dx + 0.03, y + dy + 0.03, 0, 0.25, "metal_dark")
    s.set_solid(x - 0.3, y - 0.3, x + 0.3, y + 0.3)
    s.occluder(x - 0.4, y - 0.4, x + 0.4, y + 0.4, 1.2)


def trash_can(s, x, y):
    s.cyl(x, y, 0, 0.85, 0.24, "bin_green", verts=12)
    s.cyl(x, y, 0.85, 0.92, 0.27, "metal_dark", verts=12)
    s.box(x - 0.05, y + 0.15, x + 0.12, y + 0.3, 0.92, 1.0, "goods_white")      # litter sticking out
    s.set_solid(x - 0.25, y - 0.25, x + 0.25, y + 0.25)
    s.occluder(x - 0.4, y - 0.4, x + 0.4, y + 0.4, 1.0)


def parking_meter(s, x, y):
    s.cyl(x, y, 0, 1.1, 0.04, "metal_grey", verts=8)
    s.box(x - 0.12, y - 0.1, x + 0.12, y + 0.1, 1.1, 1.45, "metal_grey")
    s.box(x - 0.08, y + 0.08, x + 0.08, y + 0.11, 1.22, 1.38, "glass")
    s.set_solid(x - 0.1, y - 0.1, x + 0.1, y + 0.1)
    s.occluder(x - 0.3, y - 0.3, x + 0.3, y + 0.3, 1.5)


def fence_wood(s, x0, x1, y, h=1.4):
    """Wooden board fence along x."""
    s.box(x0, y - 0.08, x1, y + 0.08, 0.3, 0.42, "wood_dark")
    s.box(x0, y - 0.08, x1, y + 0.08, h - 0.35, h - 0.23, "wood_dark")
    x = x0
    i = 0
    while x < x1 - 0.05:
        top = h + (0.06 if i % 2 else 0.0)
        s.box(x, y + 0.04, min(x + 0.17, x1), y + 0.1, 0.05, top, "fence_wood" if i % 3 else "wood")
        x += 0.2
        i += 1
    s.set_solid(x0, y - 0.2, x1 - 0.001, y + 0.2)
    s.occluder(x0, y - 0.3, x1, y + 0.3, h + 0.1)


def chain_link(s, x0, x1, y, h=2.0):
    """Chain-link fence along x (mesh drawn as a dark see-through pattern)."""
    s.box(x0, y - 0.02, x1, y + 0.02, 0.05, h, "chain_link")
    s.box(x0, y - 0.04, x1, y + 0.04, h - 0.04, h, "metal_grey")
    x = x0
    while x <= x1 + 0.01:
        s.cyl(x, y, 0, h + 0.05, 0.04, "metal_grey", verts=8)
        x += 2.5
    s.set_solid(x0, y - 0.2, x1 - 0.001, y + 0.2)
    s.occluder(x0, y - 0.3, x1, y + 0.3, h + 0.1)


def poster(s, x0, x1, y_face, z0, z1, mat):
    """Poster pasted on a wall that faces +y."""
    s.box(x0, y_face - 0.01, x1, y_face + 0.025, z0, z1, mat)


def weeds(s, x, y, n=3, rnd=None):
    """A clump of weeds / small bushes on the ground (objects layer, not solid)."""
    import random
    rnd = rnd or random.Random(int(x * 97 + y * 13))
    for _ in range(n):
        dx, dy = rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3)
        s.sphere(x + dx, y + dy, 0.05, rnd.uniform(0.1, 0.18), "leaves_light" if rnd.random() < 0.5 else "leaves",
                 sz=0.7)


def ivy(s, x0, x1, y_face, z1, rnd=None):
    """Climbing plants on a wall facing +y, from the ground up to about z1."""
    import random
    rnd = rnd or random.Random(int(x0 * 31 + y_face))
    x = x0
    while x < x1:
        top = rnd.uniform(0.6, z1)
        z = 0.15
        while z < top:
            s.sphere(x + rnd.uniform(-0.15, 0.15), y_face + 0.08, z, rnd.uniform(0.14, 0.24),
                     "leaves" if rnd.random() < 0.6 else "leaves_light", sz=0.8)
            z += 0.28
        x += rnd.uniform(0.3, 0.55)


def city_centre():
    """District 1: City Centre. Main avenue along x, a cross street along y, the river with the closed
    bridge to the Docks along the bottom, road works to the north (future Station Quarter)."""
    W, H = 72, 60
    oy = 200
    s = Scene("city_centre", "City Centre", W, H, origin_x=H * 16 + 16, origin_y=oy,
              img_w=(W + H) * 16 + 32, img_h=oy + (W + H) * 8 + 16)
    AV0, AV1 = 22, 30          # avenue (road) y range
    CS0, CS1 = 26, 34          # cross street (road) x range
    RIVER = 52                 # water from here to H
    road_z = -0.02

    # ---- ground: sidewalks/blocks, roads, curbs, markings ----
    s.box(0, 0, CS0, AV0, -0.1, 0.0, "paving", layer="floor")
    s.box(CS1, 0, W, AV0, -0.1, 0.0, "paving", layer="floor")
    s.box(0, AV1, CS0, RIVER, -0.1, 0.0, "paving", layer="floor")
    s.box(CS1, AV1, W, RIVER, -0.1, 0.0, "paving", layer="floor")
    s.box(0, AV0, W, AV1, -0.1, road_z, "asphalt", layer="floor")
    s.box(CS0, 0, CS1, AV0, -0.1, road_z, "asphalt", layer="floor")
    s.box(CS0, AV1, CS1, RIVER, -0.1, road_z, "asphalt", layer="floor")
    for (x0, x1) in ((0, CS0), (CS1, W)):
        s.box(x0, AV0 - 0.15, x1 - (0.15 if x0 == 0 else 0), AV0, -0.1, 0.05, "curb", layer="floor")
        s.box(x0 + (0.15 if x0 else 0), AV1, x1, AV1 + 0.15, -0.1, 0.05, "curb", layer="floor")
    for (y0, y1) in ((0, AV0), (AV1, RIVER)):
        s.box(CS0 - 0.15, y0, CS0, y1, -0.1, 0.05, "curb", layer="floor")
        s.box(CS1, y0, CS1 + 0.15, y1, -0.1, 0.05, "curb", layer="floor")
    for x in list(range(1, CS0 - 4, 3)) + list(range(CS1 + 5, W, 3)):
        s.box(x, 25.9, x + 1.6, 26.1, road_z, road_z + 0.01, "paint_yellow", layer="floor")
    for y in list(range(1, AV0 - 4, 3)) + list(range(AV1 + 5, RIVER - 1, 3)):
        s.box(29.9, y, 30.1, y + 1.6, road_z, road_z + 0.01, "paint_yellow", layer="floor")
    for i in range(6):                                   # zebra crossings around the junction
        yy = AV0 + 0.6 + i * 1.25
        s.box(CS0 - 3.0, yy, CS0 - 0.8, yy + 0.6, road_z, road_z + 0.01, "paint_white", layer="floor")
        s.box(CS1 + 0.8, yy, CS1 + 3.0, yy + 0.6, road_z, road_z + 0.01, "paint_white", layer="floor")
        xx = CS0 + 0.6 + i * 1.25
        s.box(xx, AV0 - 3.0, xx + 0.6, AV0 - 0.8, road_z, road_z + 0.01, "paint_white", layer="floor")
        s.box(xx, AV1 + 0.8, xx + 0.6, AV1 + 3.0, road_z, road_z + 0.01, "paint_white", layer="floor")
    for (x, y) in ((12, 26), (48, 24), (30, 10), (30, 40), (62, 27)):
        s.kit("Prop_ManholeCover", x, y, layer="floor", solid=False, occlude=False)
    # white edge lines along the curbs, grey stone slabs on the avenue sidewalks
    for (x0, x1) in ((0, CS0), (CS1, W)):
        s.box(x0 + (0.6 if x0 else 0), AV0 + 0.45, x1 - (0.6 if x0 == 0 else 0), AV0 + 0.6,
              road_z, road_z + 0.012, "paint_white", layer="floor")
        s.box(x0 + (0.6 if x0 else 0), AV1 - 0.6, x1 - (0.6 if x0 == 0 else 0), AV1 - 0.45,
              road_z, road_z + 0.012, "paint_white", layer="floor")
        s.box(x0, AV0 - 4, x1, AV0 - 0.15, 0.0, 0.012, "slabs", layer="floor")
        s.box(x0, AV1 + 0.15, x1, AV1 + 4, 0.0, 0.012, "slabs", layer="floor")
    for (y0, y1) in ((0, AV0), (AV1, RIVER)):
        s.box(CS0 + 0.45, y0 + (0.6 if y0 else 0), CS0 + 0.6, y1 - (0.6 if y0 == 0 else 0.6), road_z, road_z + 0.012,
              "paint_white", layer="floor")
        s.box(CS1 - 0.6, y0 + (0.6 if y0 else 0), CS1 - 0.45, y1 - (0.6 if y0 == 0 else 0.6), road_z, road_z + 0.012,
              "paint_white", layer="floor")

    # ---- north: road works (future Station Quarter) ----
    barrier(s, CS0, CS1, 1.2)
    for x in (CS0 + 1.0, CS0 + 4.0, CS1 - 1.0):
        cone(s, x, 2.6)
    chain_link(s, CS0 - 4, CS0 - 0.3, 0.4)
    chain_link(s, CS1 + 0.3, CS1 + 4, 0.4)
    for x in (CS0 - 3.4, CS0 - 1.8, CS1 + 1.2, CS1 + 3.1):
        weeds(s, x, 0.9, 4)

    # ---- north-west block: downtown apartment building (MegaKit) ----
    s.kit("Building_Medium_2_001", 11.0, AV0 - 4.0)
    for (x0, x1, mat) in ((2.2, 3.4, "poster_red"), (3.6, 4.6, "poster_yellow"), (17.4, 18.6, "poster_blue")):
        poster(s, x0, x1, AV0 - 4.0 + 0.62, 0.55, 2.0, mat)
    ivy(s, 0.3, 1.6, AV0 - 4.0 + 0.6, 2.6)
    for x in (0.8, 6.0, 20.6):
        weeds(s, x, AV0 - 3.0, 3)

    # ---- north-east block: Corner Market, a slim house and the VaultTech tower ----
    corner_market_building(s, CS1 + 5, AV0 - 4)
    s.model("2Story_Slim_Mat", CS1 + 15.6, AV0 - 4, front="left", colours="purple")
    s.box(54, 14, W, AV0 - 4, -0.1, 0.01, "plaza_gold", layer="floor")
    vaulttech_tower(s, 56, 2, 70, 14)
    for x in (55.5, 70.5):
        s.kit("Prop_Planter_Single", x, 16.5, solid=True, occlude=True)
    for x in (58, 61, 65, 68):
        s.kit("Prop_Bollard", x, 17.3)

    # ---- sidewalk furniture along the avenue ----
    for x in (3, 15, 51, 66):
        lamp_curved(s, x, AV0 - 0.8, arm="y")
        lamp_curved(s, x, AV1 + 0.8, arm="-y")
    for x in (5.0, 17.0, 53.0, 68.0):
        trash_can(s, x, AV0 - 0.9)
    for x in (9.5, 12.5, 58.5, 61.5):
        parking_meter(s, x, AV0 - 0.7)
    newspaper_box(s, 45.0, AV1 + 2.6, "sign_blue")
    newspaper_box(s, 46.0, AV1 + 2.6, "red_paint")
    trash_can(s, 38.5, AV1 + 1.0)
    for x in (CS1 + 16.6, CS1 + 18.0):
        weeds(s, x, AV0 - 3.6, 3)
    ivy(s, CS1 + 15.6, CS1 + 16.6, AV0 - 4 + 0.05, 2.2)
    potted_plant(s, CS1 + 16.2, AV0 - 3.5, "flowers")
    potted_plant(s, CS1 + 18.9, AV0 - 3.5, "bush")
    shrub(s, CS1 + 19.6, AV0 - 3.6, 0.4, "leaves_light")
    conifer(s, CS1 + 3.9, AV0 - 3.3, 3.4)
    shrub(s, CS1 + 4.3, AV0 - 2.6, 0.4)
    street_tree(s, CS1 + 2.4, AV0 - 1.2)
    poster(s, CS1 + 5.2, CS1 + 6.2, AV0 - 4 + 0.08, 0.6, 1.8, "poster_yellow")
    for x in (8.0, 19.0):
        s.kit("Sidewalk_Planter", x, AV0 - 1.4, solid=True, occlude=False)
        tree(s, x, AV0 - 1.4, 0.95)
    hydrant(s, CS1 + 1.2, AV0 - 1.0)
    bus_stop(s, 40.0, 44.0, AV1 + 3.2)

    # ---- south-west block: City Park (the bench where you will sleep) ----
    P0, P1 = AV1 + 4, RIVER - 4
    s.box(1, P0, CS0 - 4, P1, -0.1, 0.06, "grass", layer="floor")
    s.box(1, P0 - 0.12, CS0 - 4, P0, -0.1, 0.1, "curb", layer="floor")
    s.box(CS0 - 4, P0, CS0 - 3.88, P1, -0.1, 0.1, "curb", layer="floor")
    s.box(1, P1, CS0 - 4, P1 + 0.12, -0.1, 0.1, "curb", layer="floor")
    s.box(10, P0, 12, P1, 0.0, 0.08, "path_dirt", layer="floor")
    s.box(1, 40, 10, 42, 0.0, 0.08, "path_dirt", layer="floor")
    s.box(12, 40, CS0 - 4, 42, 0.0, 0.08, "path_dirt", layer="floor")
    bench_along_x(s, 6.0, 8.6, 39.4)
    bench_along_x(s, 14.0, 16.6, 39.4)
    s.box(14.5, 43.5, 20.5, 46.8, -0.1, 0.09, "pond_edge", layer="floor")
    s.box(14.8, 43.8, 20.2, 46.5, -0.1, 0.1, "water", layer="floor")
    s.set_solid(14.5, 43.5, 20.499, 46.799)
    for (x, y, sc) in ((3.5, 36.5, 1.0), (19.5, 36.5, 1.1), (4.0, 45.5, 1.05), (7.5, 46.0, 0.85), (21.0, 41.0, 0.9)):
        tree(s, x, y, sc)
    for (x, y) in ((6.0, 43.5), (13.5, 36.8)):
        planter(s, x, y)

    # ---- south-east block: fountain square ----
    s.box(CS1 + 4, AV1 + 4, W, RIVER - 4, -0.1, 0.01, "plaza_stone", layer="floor")
    fountain(s, 53, 41)
    for (x0, x1, y) in ((47, 49.6, 38.0), (56.4, 59.0, 38.0), (47, 49.6, 45.0), (56.4, 59.0, 45.0)):
        bench_along_x(s, x0, x1, y)
    for (x, y) in ((40, 36), (66, 36), (40, 46), (66, 46)):
        tree(s, x, y, 1.0)
    for (x, y) in ((44, 41), (62, 41)):
        lamp_post(s, x, y)

    # ---- riverside: embankment, railing, water and the closed bridge to the Docks ----
    for (x0, x1) in ((0, CS0), (CS1, W)):
        s.box(x0, RIVER - 0.3, x1, RIVER, -1.2, 0.0, "stone", layer="floor")
        s.box(x0, RIVER - 0.25, x1, RIVER - 0.15, 0.95, 1.02, "metal_dark")
        x = x0 + 0.5
        while x < x1:
            s.box(x - 0.04, RIVER - 0.24, x + 0.04, RIVER - 0.16, 0, 0.98, "metal_dark")
            x += 1.5
        s.set_solid(x0, RIVER - 0.5, x1 - 0.001, H - 0.001)
        s.occluder(x0, RIVER - 0.5, x1, RIVER, 1.0)
    s.box(0, RIVER, W, H, -1.6, -0.7, "water", layer="floor")
    s.box(CS0 - 0.6, RIVER, CS1 + 0.6, H, -0.7, road_z - 0.012, "stone", layer="floor")  # bridge deck
    s.box(CS0, RIVER, CS1, H, road_z - 0.01, road_z, "asphalt", layer="floor")
    for xr in (CS0 - 0.5, CS1 + 0.3):
        s.box(xr, RIVER, xr + 0.2, H, 0, 0.9, "stone")
    s.set_solid(CS0 - 0.6, RIVER, CS1 + 0.599, H - 0.001)
    barrier(s, CS0, CS1, RIVER - 1.0, closed_sign=True)
    for x in (CS0 + 1.0, CS1 - 1.0):
        cone(s, x, RIVER - 2.4)

    s.sun_strength = 4.2
    return s


# ---- small "lived-in" details (inspired by the owner's own building packs) -----------------------
FLOWERS = ("flower_red", "flower_pink", "flower_yellow", "flower_white")


def flower_box(s, x0, x1, y_face, z, rnd=None):
    """Window box with flowers and trailing leaves under a window on a +y facing wall."""
    rnd = rnd or random.Random(int(x0 * 100 + z * 10))
    s.box(x0, y_face, x1, y_face + 0.3, z - 0.22, z, "terracotta")
    n = max(3, int((x1 - x0) * 5))
    for i in range(n):
        x = x0 + 0.1 + (x1 - x0 - 0.2) * i / (n - 1)
        s.sphere(x, y_face + 0.15 + rnd.uniform(-0.05, 0.05), z + 0.08, 0.1, "leaves_light")
        s.sphere(x + rnd.uniform(-0.05, 0.05), y_face + 0.2, z + 0.16 + rnd.uniform(0, 0.08), 0.07,
                 rnd.choice(FLOWERS))
    for i in range(n // 2):
        x = x0 + 0.15 + (x1 - x0 - 0.3) * rnd.random()
        s.sphere(x, y_face + 0.32, z - 0.25 - rnd.uniform(0, 0.15), 0.07, "leaves")


def potted_plant(s, x, y, kind="bay"):
    """Terracotta pot with a ball-shaped bay tree, a bush or flowers."""
    s.cyl(x, y, 0, 0.45, 0.22, "terracotta", r2=0.26)
    if kind == "bay":
        s.cyl(x, y, 0.4, 1.0, 0.025, "trunk")
        s.sphere(x, y, 1.2, 0.32, "leaves")
    elif kind == "bush":
        s.sphere(x, y, 0.65, 0.3, "leaves_light")
        s.sphere(x + 0.1, y + 0.1, 0.78, 0.2, "leaves")
    else:
        s.sphere(x, y, 0.55, 0.22, "leaves_light")
        rnd = random.Random(int(x * 31 + y * 7))
        for _ in range(6):
            s.sphere(x + rnd.uniform(-0.18, 0.18), y + rnd.uniform(-0.18, 0.18), 0.66 + rnd.uniform(0, 0.08),
                     0.07, rnd.choice(FLOWERS))
    s.set_solid(x - 0.25, y - 0.25, x + 0.25, y + 0.25)


def conifer(s, x, y, h=3.2):
    s.cyl(x, y, 0, 0.5, 0.08, "trunk")
    for i, (z0, r) in enumerate(((0.3, 0.75), (1.1, 0.6), (1.8, 0.45), (2.4, 0.3))):
        s.cyl(x, y, z0 * h / 3.2, (z0 + 1.0) * h / 3.2, r, "leaves_dark", verts=10, r2=0.05)
    s.set_solid(x - 0.3, y - 0.3, x + 0.3, y + 0.3)
    s.occluder(x - 0.8, y - 0.8, x + 0.8, y + 0.8, h)


def shrub(s, x, y, r=0.45, mat="leaves"):
    rnd = random.Random(int(x * 13 + y * 17))
    for _ in range(4):
        s.sphere(x + rnd.uniform(-r, r) * 0.5, y + rnd.uniform(-r, r) * 0.5, r * 0.8 + rnd.uniform(0, 0.15),
                 r * rnd.uniform(0.6, 0.9), mat)


def produce_display(s, x0, x1, y):
    """Fruit and vegetable crates on a low stand in front of a shop window (facade at y)."""
    s.box(x0, y + 0.1, x1, y + 0.9, 0, 0.5, "wood_dark")
    fruit = ("apple_red", "orange_fruit", "lettuce_green", "banana_yellow", "apple_red")
    n = int((x1 - x0) / 0.8)
    for i in range(n):
        cx0 = x0 + 0.05 + i * (x1 - x0) / n
        cx1 = cx0 + (x1 - x0) / n - 0.1
        s.box(cx0, y + 0.15, cx1, y + 0.85, 0.5, 0.72, "crate")
        rnd = random.Random(i + int(x0 * 10))
        for _ in range(7):
            s.sphere(rnd.uniform(cx0 + 0.12, cx1 - 0.12), rnd.uniform(y + 0.3, y + 0.7), 0.74, 0.08,
                     fruit[i % len(fruit)])
    s.set_solid(x0, y, x1, y + 0.9)


def a_frame_sign(s, x, y):
    """Chalkboard sidewalk sign."""
    s.box(x - 0.35, y - 0.12, x + 0.35, y - 0.04, 0, 0.95, "wood")
    s.box(x - 0.29, y - 0.04, x + 0.29, y - 0.01, 0.1, 0.88, "chalkboard")
    for i, w in enumerate((0.4, 0.3, 0.36)):
        s.box(x - w / 2, y - 0.01, x + w / 2, y + 0.005, 0.66 - i * 0.17, 0.69 - i * 0.17, "chalk")
    s.set_solid(x - 0.3, y - 0.2, x + 0.3, y + 0.1)


def street_tree(s, x, y):
    """Small sidewalk tree in an iron grate."""
    s.box(x - 0.6, y - 0.6, x + 0.6, y + 0.6, 0, 0.03, "metal_dark", layer="floor")
    s.box(x - 0.45, y - 0.45, x + 0.45, y + 0.45, 0.0, 0.035, "soil", layer="floor")
    tree(s, x, y, 0.8)


def corner_market_building(s, x0, fy):
    """Corner Market: 10 cells wide, 8 deep, facade at y = fy facing +y. Door warps inside."""
    x1 = x0 + 10
    y0 = fy - 8
    cm_h = 4.4
    s.box(x0, y0, x1, fy, 0, cm_h, "brick_red")
    s.box(x0, fy - 0.1, x1, fy + 0.05, 0, 0.45, "stone")                       # plinth
    window_left_shop(s, x0 + 0.6, x0 + 3.6, fy, 0.5, 2.5)
    window_left_shop(s, x0 + 6.4, x0 + 9.4, fy, 0.5, 2.5)
    door_left(s, x0 + 4.2, x0 + 5.8, fy, 2.3, mat="wood_green")
    x = x0 + 0.2
    i = 0
    while x < x1 - 0.2:
        s.wedge(x, fy, min(x + 0.5, x1 - 0.2), fy + 1.3, 2.95, 2.55, "y",
                "awning_green" if i % 2 == 0 else "awning_white")
        x += 0.5
        i += 1
    s.box(x0 + 0.8, fy - 0.05, x1 - 0.8, fy + 0.12, 3.05, 3.85, "sign_green")
    s.box(x0 + 0.7, fy - 0.05, x1 - 0.7, fy + 0.15, 3.0, 3.07, "brass")
    s.box(x0 + 0.7, fy - 0.05, x1 - 0.7, fy + 0.15, 3.83, 3.9, "brass")
    s.text("CORNER MARKET", x0 + 5.0, fy + 0.13, 3.27, 0.42, "sign_text", face="left")
    s.box(x0, fy - 0.1, x1, fy + 0.1, cm_h - 0.25, cm_h, "stone")                # cornice
    # upper storey (flat above the shop) with flower boxes, slate roof and a chimney
    up_h = cm_h + 2.8
    s.box(x0, y0, x1, fy - 0.02, cm_h, up_h, "brick_red")
    for wx in (x0 + 1.0, x0 + 4.0, x0 + 7.0):
        window_left(s, wx, wx + 2.0, fy - 0.02, cm_h + 0.8, cm_h + 2.3)
        flower_box(s, wx - 0.05, wx + 2.05, fy - 0.02, cm_h + 0.72)
    s.box(x0, fy - 0.1, x1, fy + 0.08, up_h - 0.18, up_h, "stone")
    ridge_y = (y0 + fy) / 2
    ridge_z = up_h + 2.3
    s.wedge(x0 - 0.1, ridge_y, x1 + 0.1, fy + 0.45, ridge_z, up_h - 0.2, "y", "slate")
    s.wedge(x0 - 0.1, ridge_y, x1 + 0.1, y0 - 0.45, ridge_z, up_h - 0.2, "y", "slate")
    s.poly([(x1, y0, up_h), (x1, fy, up_h), (x1, ridge_y, ridge_z)], "brick_red")
    s.poly([(x0, y0, up_h), (x0, ridge_y, ridge_z), (x0, fy, up_h)], "brick_red")
    s.box(x1 - 2.2, ridge_y - 1.2, x1 - 1.4, ridge_y - 0.4, up_h + 1.0, ridge_z + 1.0, "brick_brown")
    s.box(x1 - 2.3, ridge_y - 1.3, x1 - 1.3, ridge_y - 0.3, ridge_z + 1.0, ridge_z + 1.12, "stone")
    # shop front details
    produce_display(s, x0 + 0.7, x0 + 3.5, fy)
    potted_plant(s, x0 + 3.85, fy + 0.45, "bay")
    potted_plant(s, x0 + 6.15, fy + 0.45, "bay")
    a_frame_sign(s, x0 + 7.4, fy + 1.6)
    s.set_solid(x0, y0, x1 - 0.001, fy - 0.001)
    s.set_solid(x0 + 4, fy - 1, x0 + 5.999, fy - 0.001, False)                  # door cells walkable
    s.occluder(x0, y0, x1, fy, cm_h + 5.6)
    s.warp(x0 + 4, fy - 1, x0 + 6, fy, "corner_market", 6.0, 7.6, "up")


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
M = 1 / CELL_M   # metres -> cells


def product(s, kind, x, y_front, z, colour, rnd):
    """One grocery item standing at (x, front edge y_front) on height z. Sizes are exaggerated so
    the items stay readable at GBA resolution. Returns the item's width in cells."""
    if kind == "milk":
        w, d, h = 0.15 * M, 0.15 * M, 0.27
        y0 = y_front - d
        s.box(x, y0, x + w, y_front, z, z + h, "milk_white")
        s.box(x - 0.01, y0 - 0.01, x + w + 0.01, y_front + 0.012, z + 0.07, z + 0.16, colour)   # printed band
        s.box(x + 0.02, y0 + 0.04, x + w - 0.02, y_front - 0.04, z + h, z + h + 0.05, colour)  # gable top
        return w
    if kind == "cereal":
        w, d, h = 0.22 * M, 0.09 * M, 0.34
        y0 = y_front - d
        s.box(x, y0, x + w, y_front, z, z + h, colour)
        s.box(x + 0.05, y_front - 0.01, x + w - 0.05, y_front + 0.012, z + 0.1, z + 0.24, "print_cream")
        return w
    if kind == "can":
        r = 0.065
        cx, cy = x + r * M, y_front - r * M
        s.cyl(cx, cy, z, z + 0.15, r, "metal_light", verts=10)
        s.cyl(cx, cy, z + 0.025, z + 0.125, r + 0.004, colour, verts=10)
        return 2 * r * M
    if kind == "bottle":
        r = 0.055
        cx, cy = x + r * M, y_front - r * M
        s.cyl(cx, cy, z, z + 0.2, r, colour, verts=10)
        s.cyl(cx, cy, z + 0.2, z + 0.27, r * 0.45, colour, verts=8)
        s.cyl(cx, cy, z + 0.27, z + 0.3, r * 0.5, "goods_red", verts=8)
        s.cyl(cx, cy, z + 0.06, z + 0.13, r + 0.004, "print_cream", verts=10)
        return 2 * r * M
    if kind == "jar":
        r = 0.07
        cx, cy = x + r * M, y_front - r * M
        s.cyl(cx, cy, z, z + 0.16, r, colour, verts=10)
        s.cyl(cx, cy, z + 0.16, z + 0.19, r * 0.9, "brass", verts=10)
        return 2 * r * M
    raise ValueError(kind)


def product_row(s, kind, colours, x0, x1, y_front, z, rnd):
    x = x0 + 0.05
    while True:
        colour = rnd.choice(colours)
        # measure first with a dry run width
        widths = {"milk": 0.15 * M, "cereal": 0.22 * M, "can": 0.13 * M, "bottle": 0.11 * M, "jar": 0.14 * M}
        if x + widths[kind] > x1 - 0.05:
            break
        x += product(s, kind, x, y_front, z, colour, rnd) + 0.035 * M


def gondola(s, x0, y0, x1, y1, h, rows, rnd):
    """Open supermarket shelving, products facing +y (towards the camera)."""
    s.box(x0, y0, x1, y1, 0, 0.14, "shelf_base")
    ym = (y0 + y1) / 2
    s.box(x0, ym - 0.04, x1, ym + 0.04, 0.14, h, "shelf_back")
    levels = [0.14 + i * (h - 0.14) / len(rows) for i in range(len(rows))]
    for lz, (kind, colours) in zip(levels, rows):
        s.box(x0, y0, x1, y1, lz, lz + 0.035, "shelf_white")
        s.box(x0, y1 - 0.02, x1, y1 + 0.01, lz - 0.05, lz + 0.035, "price_yellow")   # price strip
        product_row(s, kind, colours, x0, x1, y1 - 0.06, lz + 0.035, rnd)
    s.box(x0, y0, x1, y1, h - 0.03, h, "shelf_white")
    s.box(x1 - 0.06, y0, x1, y1, 0, h + 0.05, "shelf_end")                          # end panel (+x)
    s.box(x0, y0, x0 + 0.06, y1, 0, h + 0.05, "shelf_end")
    s.set_solid(x0, y0, x1 - 0.001, y1 - 0.001)
    s.occluder(x0, y0, x1, y1, h + 0.3)


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
    s.box(0, 0, W, 0.05, 0, 0.9, "wood")
    s.box(0, 0, 0.05, H, 0, 0.9, "wood")
    s.box(0, 0, W, 0.07, 0.88, 0.95, "wood_dark")
    s.box(0, 0, 0.07, H, 0.88, 0.95, "wood_dark")
    s.box(-0.4, -0.4, W, 0, wall_h, wall_h + 0.08, "wood_dark")
    s.box(-0.4, 0, 0, H, wall_h, wall_h + 0.08, "wood_dark")
    s.occluder(-0.4, -0.4, W, 0.1, wall_h)
    s.occluder(-0.4, 0, 0.1, H, wall_h)

    import random
    rnd = random.Random(11)
    boxes = ["goods_red", "goods_yellow", "goods_blue", "goods_orange", "goods_green"]
    cans = ["goods_red", "goods_green", "goods_orange", "goods_blue"]
    jars = ["goods_red", "goods_orange", "goods_yellow"]
    bottles = ["bottle_green", "bottle_clear", "bottle_brown"]

    # wall shelving along the back wall
    gondola(s, 0.3, 0.05, 6.6, 0.95, 2.0,
            [("can", cans), ("jar", jars), ("cereal", boxes), ("bottle", bottles)], rnd)
    # two aisles
    gondola(s, 2.6, 2.8, 7.6, 3.9, 1.5, [("cereal", boxes), ("can", cans), ("jar", jars)], rnd)
    gondola(s, 2.6, 5.1, 7.6, 6.2, 1.5, [("bottle", bottles), ("cereal", boxes), ("can", cans)], rnd)

    # dairy fridge: open, lit front with milk cartons and bottles on shelves
    fx0, fx1, fy1, fh = 7.1, 11.8, 1.3, 2.2
    s.box(fx0, 0.05, fx1, fy1, 0, 0.25, "fridge_white")
    s.box(fx0, 0.05, fx1, 0.4, 0.25, fh, "fridge_light")
    s.box(fx0, 0.05, fx1, fy1, fh - 0.25, fh, "fridge_white")
    s.box(fx0, 0.05, fx0 + 0.12, fy1, 0, fh, "fridge_white")
    s.box(fx1 - 0.12, 0.05, fx1, fy1, 0, fh, "fridge_white")
    for lz, kind in ((0.25, "milk"), (0.85, "milk"), (1.4, "bottle")):
        s.box(fx0, 0.05, fx1, fy1 - 0.1, lz, lz + 0.03, "metal_light")
        product_row(s, kind, ["goods_blue", "goods_red", "goods_green"] if kind == "milk" else bottles,
                    fx0 + 0.15, fx1 - 0.15, fy1 - 0.2, lz + 0.03, rnd)
    for k in range(1, 4):
        xk = fx0 + k * (fx1 - fx0) / 4
        s.box(xk - 0.03, fy1 - 0.08, xk + 0.03, fy1, 0.25, fh - 0.25, "metal_light")   # door frames
    s.box(fx0 + 1.0, fy1 - 0.05, fx1 - 1.0, fy1 + 0.02, fh + 0.05, fh + 0.4, "sign_blue")
    s.text("DAIRY", (fx0 + fx1) / 2, fy1 + 0.03, fh + 0.22, 0.24, "sign_text", face="left")
    s.set_solid(fx0, 0.05, fx1 - 0.001, fy1 - 0.001)
    s.occluder(fx0, 0.05, fx1, fy1, fh + 0.45)

    # fresh fruit & vegetables along the left wall (facing +x)
    fruit = [("apple_red", 0.075), ("orange_fruit", 0.08), ("banana_yellow", 0.07), ("lettuce_green", 0.1)]
    for i, (mat, r) in enumerate(fruit):
        y0 = 1.9 + i * 1.25
        y1 = y0 + 1.1
        s.box(0.3, y0, 1.7, y1, 0, 0.55, "crate")
        s.box(0.3, y0, 0.9, y1, 0.55, 0.85, "crate")
        for (bx0, bx1, bz) in ((0.95, 1.65, 0.55), (0.35, 0.85, 0.85)):
            yy = y0 + 0.12
            row = 0
            while yy < y1 - 0.12:
                xx = bx0 + (0.08 if row % 2 else 0.0)
                while xx < bx1 - 0.05:
                    s.sphere(xx + r * M * 0.5, yy, bz + r * 0.8, r, mat)
                    xx += r * M * 1.6
                yy += r * M * 1.4
                row += 1
        s.box(1.68, y0 + 0.3, 1.72, y1 - 0.3, 0.3, 0.45, "price_yellow")
    s.box(0.0, 2.6, 0.06, 6.2, 2.0, 2.45, "sign_green")
    s.text("FRESH FRUIT", 0.07, 4.4, 2.2, 0.24, "sign_text", face="right")
    s.set_solid(0.3, 1.9, 1.699, 6.899)
    s.occluder(0.3, 1.9, 1.7, 6.9, 1.0)

    # checkout with conveyor belt, register and baskets
    s.box(8.6, 5.3, 11.4, 6.3, 0, 0.9, "wood")
    s.box(8.55, 5.25, 11.45, 6.35, 0.9, 0.95, "wood_dark")
    s.box(8.7, 5.45, 10.3, 6.15, 0.95, 0.98, "belt_dark")
    s.box(10.5, 5.5, 11.2, 6.1, 0.95, 1.2, "metal_dark")
    s.box(10.6, 5.6, 11.1, 6.0, 1.2, 1.26, "screen")
    s.set_solid(8.6, 5.3, 11.399, 6.299)
    s.occluder(8.6, 5.3, 11.4, 6.3, 1.3)
    for k in range(4):
        z = k * 0.12
        s.box(8.0, 7.3, 8.9, 8.0, z, z + 0.1, "basket_red")
    s.box(8.05, 7.35, 8.85, 7.95, 0.46, 0.47, "basket_red")
    s.set_solid(8.0, 7.3, 8.899, 7.999)
    s.occluder(8.0, 7.3, 8.9, 8.0, 0.6)

    # plant by the door
    s.box(10.6, 7.6, 11.4, 8.4, 0, 0.5, "pot")
    for (dx, dy, dz, r) in ((0, 0, 0.9, 0.35), (-0.15, 0.1, 0.75, 0.3), (0.15, -0.1, 0.8, 0.28), (0.05, 0.05, 1.15, 0.25)):
        s.sphere(11.0 + dx / CELL_M, 8.0 + dy / CELL_M, dz, r, "leaves_light")
    s.set_solid(10.6, 7.6, 11.399, 8.399)
    s.occluder(10.5, 7.5, 11.5, 8.5, 1.4)

    # bright shop lights
    s.point_light(4, 2, 2.8, 140, colour=(1.0, 0.92, 0.78))
    s.point_light(4, 5, 2.8, 140, colour=(1.0, 0.92, 0.78))
    s.point_light(9.5, 4, 2.8, 120, colour=(1.0, 0.92, 0.78))
    s.point_light(1.5, 7.5, 2.6, 60)
    # exit
    s.warp(5, H - 0.6, 7, H, "city_centre", 44.0, 19.0, "down")
    return s


SCENES = [city_centre, corner_market_interior]
