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
import math

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


# Quaternius CC0 props (Ultimate House Interior Pack, Ultimate Food Pack): native bounding boxes in Blender
# units (about 2x metres), key 'pack/name'. Pack folders: art_source/quaternius_house, quaternius_food.
PROP_DIMS = {
    "house/Chair_2": ((-0.381, -0.381, -0.003), (0.381, 0.445, 1.686)),
    "house/Couch_Small1": ((-1.443, -1.02, -0.013), (1.443, 1.183, 1.897)),
    "house/Couch_Small2": ((-1.057, -1.317, -0.0), (1.057, 0.675, 1.269)),
    "house/OfficeChair": ((-0.361, -0.365, 0.0), (0.36, 0.442, 1.128)),
    "house/Stool": ((-0.338, -0.355, -0.009), (0.338, 0.355, 1.363)),
    "house/Table_RoundLarge": ((-1.857, -0.97, 0.005), (1.857, 0.97, 1.126)),
    "house/Trashcan_Cylindric": ((-0.377, -0.377, -0.0), (0.377, 0.377, 1.074)),
    "house/Bathroom_Mirror1": ((-0.324, -0.062, -0.465), (0.324, 0.04, 0.465)),
    "house/Bathroom_Shower1": ((-0.824, -0.868, -0.095), (1.072, 1.025, 3.453)),
    "house/Bathroom_Sink": ((-0.695, -0.512, 0.151), (0.695, 0.304, 1.597)),
    "house/Bathroom_Toilet": ((-0.598, -0.792, -0.013), (0.598, 0.9, 1.888)),
    "house/Bathroom_Towel": ((-0.561, -0.035, -0.621), (0.624, 0.127, 0.032)),
    "house/Bathroom_WashingMachine": ((-0.646, -0.706, -0.0), (0.646, 0.618, 1.47)),
    "house/Bed_Single": ((-0.967, -1.97, -0.0), (1.013, 1.97, 1.355)),
    "house/Bookshelf": ((-1.159, -0.378, -0.024), (1.159, 0.378, 4.415)),
    "house/Carpet_1": ((-1.058, -1.537, -0.001), (1.073, 1.556, 0.036)),
    "house/Carpet_Round": ((-1.246, -1.266, -0.0), (1.246, 1.266, 0.016)),
    "house/Chair_1": ((-0.381, -0.381, -0.003), (0.381, 0.445, 1.764)),
    "house/Couch_Medium1": ((-2.344, -1.02, -0.013), (2.344, 1.183, 1.897)),
    "house/Curtains_Single": ((-0.776, -0.056, -0.0), (0.856, 0.421, 4.344)),
    "house/Drawer_1": ((-1.397, -0.56, -0.009), (1.397, 0.559, 1.343)),
    "house/Houseplant_1": ((-0.292, -0.371, 0.002), (0.477, 0.323, 0.719)),
    "house/Houseplant_3": ((-0.169, -0.169, 0.001), (0.173, 0.169, 0.846)),
    "house/Kitchen_Cabinet1": ((-0.505, -0.566, 0.007), (0.505, 0.505, 1.574)),
    "house/Kitchen_Cabinet2": ((-0.505, -0.566, 0.007), (0.505, 0.505, 1.574)),
    "house/Kitchen_Fridge": ((-0.649, -0.718, 0.007), (0.649, 0.584, 3.316)),
    "house/Kitchen_Oven": ((-0.505, -0.615, -0.0), (0.505, 0.505, 1.617)),
    "house/Kitchen_Sink": ((-0.505, -0.615, -0.0), (0.505, 0.505, 1.924)),
    "house/Light_Floor1": ((-0.14, -0.148, 0.014), (0.14, 0.148, 1.618)),
    "house/NightStand_1": ((-0.476, -0.476, 0.004), (0.476, 0.476, 0.829)),
    "house/Shelf_Small1": ((-0.972, -0.275, -0.021), (0.972, 0.275, 0.556)),
    "house/Table_RoundSmall": ((-0.97, -0.97, -0.003), (0.97, 0.97, 1.145)),
    "house/Trashcan_Small1": ((-0.252, -0.164, -0.007), (0.252, 0.142, 0.706)),
    "house/Window_Large1": ((-0.916, -0.071, -0.0), (0.916, 0.071, 1.698)),
    "food/Apple": ((-0.401, -0.399, -0.394), (0.401, 0.399, 0.458)),
    "food/Banana": ((-0.707, -0.116, -0.446), (0.469, 0.193, 0.958)),
    "food/Bottle1": ((-0.226, -0.226, -0.001), (0.226, 0.226, 1.563)),
    "food/Bread": ((-0.347, -0.6, 0.007), (0.347, 0.6, 0.854)),
    "food/Carrot": ((-0.469, -0.475, -0.987), (0.478, 0.456, 1.792)),
    "food/Cheese_Singles": ((-0.418, -0.567, -0.025), (0.613, 0.408, 0.004)),
    "food/Jar_Large": ((-0.317, -0.301, -0.004), (0.317, 0.301, 0.634)),
    "food/KetchupBottle": ((-0.25, -0.25, -0.017), (0.25, 0.25, 1.516)),
    "food/Lettuce_Whole": ((-0.831, -0.831, -0.734), (0.831, 0.831, 0.634)),
    "food/MustardBottle": ((-0.25, -0.25, -0.017), (0.25, 0.25, 1.516)),
    "food/Orange": ((-0.372, -0.372, -0.34), (0.372, 0.372, 0.402)),
    "food/PeanutButter": ((-0.237, -0.226, 0.003), (0.237, 0.226, 0.728)),
    "food/Soda": ((-0.456, -0.456, 0.004), (0.456, 0.456, 1.927)),
    "food/Tomato": ((-0.376, -0.376, -0.224), (0.376, 0.376, 0.402)),
}


SOLID_RES = 4     # collision sub-cells per map cell (must match solid_res in include/tl_world.h)


class Scene:
    def __init__(self, ident, name, w, h, origin_x, origin_y, img_w, img_h):
        self.ident, self.name = ident, name
        self.w, self.h = w, h
        self.origin_x, self.origin_y = origin_x, origin_y   # image pixel of world (0, 0)
        self.img_w, self.img_h = (img_w + 7) // 8 * 8, (img_h + 7) // 8 * 8      # whole 8x8 tiles
        self.prims = []
        self.solid = [[False] * (w * SOLID_RES) for _ in range(h * SOLID_RES)]   # fine collision grid
        self.warps = []
        self.occluders = []
        self.lights = []
        self.lamps = []      # night light pools on the ground: (x, y) in cells
        self.sun = True

    # -- primitives -----------------------------------------------------------------
    def box(self, x0, y0, x1, y1, z0, z1, mat, layer="objects", bevel=0.0):
        self.prims.append(dict(type="box", x0=x0, y0=y0, x1=x1, y1=y1, z0=z0, z1=z1, mat=mat,
                               layer=layer, bevel=bevel))

    def cyl(self, x, y, z0, z1, r, mat, layer="objects", verts=16, r2=None, axis="z"):
        """Cylinder (or cone: r2 = top radius). axis 'x' / 'y': a disc lying against a wall (z0..z1 is then
        the centre height +- r / thickness along the axis: z0 = centre height, z1 - z0 = thickness)."""
        self.prims.append(dict(type="cyl", x=x, y=y, z0=z0, z1=z1, r=r, mat=mat, layer=layer, verts=verts,
                               r2=r if r2 is None else r2, axis=axis))

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

    def prop(self, name, x, y, rot=0, h=None, scale=None, z=0.0, layer="objects", solid=True, occlude=True,
             colours=None, pad=0.0):
        """Places a Quaternius CC0 prop ('house/Bed_Single', 'food/Bread', ...). (x, y) = centre of its footprint
        in cells, rot = degrees about z (multiples of 90: 0 faces +y, 90 faces +x, 180 faces -y, 270 faces -x),
        h = real height in metres or scale = factor on the native size. z = height of its underside (m).
        Returns the footprint (x0, y0, x1, y1) in cells."""
        mn, mx = PROP_DIMS[name]
        sc = scale if scale is not None else h / (mx[2] - mn[2])
        w = (mx[0] - mn[0]) * sc / CELL_M
        d = (mx[1] - mn[1]) * sc / CELL_M
        if (rot // 90) % 2:
            w, d = d, w
        fp = (x - w / 2, y - d / 2, x + w / 2, y + d / 2)
        self.prims.append(dict(type="prop", name=name, x=x, y=y, rot=rot, scale=sc, z=z, layer=layer,
                               colours=colours or {}))
        height = (mx[2] - mn[2]) * sc
        if solid and layer == "objects":
            self.set_solid(fp[0] + pad, fp[1] + pad, fp[2] - 0.001 - pad, fp[3] - 0.001 - pad)
        if occlude and layer == "objects":
            self.occluder(fp[0], fp[1], fp[2], fp[3], height + z + 0.1)
        return fp

    # -- gameplay ---------------------------------------------------------------------
    def set_solid(self, x0, y0, x1, y1, value=True):
        """Marks the rect (cells, floats) solid on the fine grid (SOLID_RES sub-cells per cell),
        rounded outward to whole sub-cells."""
        r = SOLID_RES
        for sy in range(max(0, math.floor(y0 * r + 1e-6)), min(self.h * r, math.ceil(y1 * r - 1e-6))):
            for sx in range(max(0, math.floor(x0 * r + 1e-6)), min(self.w * r, math.ceil(x1 * r - 1e-6))):
                self.solid[sy][sx] = value

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
    """Panelled door with a proper frame (jambs + lintel), glass pane with muntins, lever handle, step."""
    d = 0.04 / 0.75
    xm = (x0 + x1) / 2
    s.box(x0 - 0.14, y_face - d, x1 + 0.14, y_face + d, 0, z1 + 0.14, frame)               # recess behind the leaf
    s.box(x0 - 0.14, y_face - d, x0, y_face + 2.2 * d, 0, z1, frame)                       # jambs stand out
    s.box(x1, y_face - d, x1 + 0.14, y_face + 2.2 * d, 0, z1, frame)
    s.box(x0 - 0.2, y_face - d, x1 + 0.2, y_face + 3 * d, z1, z1 + 0.14, frame)             # lintel
    s.box(x0, y_face - d, x1, y_face + 1.2 * d, 0, z1, mat)                                # door leaf
    pw = (x1 - x0 - 0.36) / 2
    for px0 in (x0 + 0.12, xm + 0.06):                                                      # raised lower panels
        s.box(px0, y_face + d, px0 + pw, y_face + 1.8 * d, 0.14, z1 * 0.4, mat)
    gx0, gx1, gz0, gz1 = x0 + 0.2, x1 - 0.2, z1 * 0.5, z1 - 0.2
    s.box(gx0 - 0.05, y_face + d, gx1 + 0.05, y_face + 1.8 * d, gz0 - 0.05, gz1 + 0.05, mat)  # pane surround
    s.box(gx0, y_face + d, gx1, y_face + 2 * d, gz0, gz1, "glass")
    s.box(xm - 0.025, y_face + 1.5 * d, xm + 0.025, y_face + 2.6 * d, gz0, gz1, frame)       # muntins
    s.box(gx0, y_face + 1.5 * d, gx1, y_face + 2.6 * d, (gz0 + gz1) / 2 - 0.025, (gz0 + gz1) / 2 + 0.025, frame)
    s.box(x1 - 0.34, y_face + d, x1 - 0.2, y_face + 2.2 * d, z1 * 0.38, z1 * 0.48, "brass")  # handle plate
    s.box(x1 - 0.42, y_face + 2 * d, x1 - 0.22, y_face + 3.4 * d, z1 * 0.42, z1 * 0.45, "brass")  # lever
    s.box(x0 - 0.25, y_face, x1 + 0.25, y_face + 0.4, 0.0, 0.09, "stone")                   # door step
    s.box(x0 - 0.2, y_face + 0.4, x1 + 0.2, y_face + 0.5, 0.0, 0.05, "stone")


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
def vaulttech_door(s, xm, y1):
    """Automatic sliding glass doors: metal frame, two glass leaves with a visible split, push bars,
    kick rails, a sensor box above and a metal threshold."""
    hw = 2.0                                         # half width in cells
    hz = 3.0                                         # clear height (m)
    s.box(xm - hw - 0.2, y1 - 0.06, xm + hw + 0.2, y1 + 0.12, 0, hz + 0.45, "metal_dark")     # recess / reveal
    s.box(xm - hw - 0.18, y1 + 0.02, xm - hw + 0.02, y1 + 0.2, 0, hz + 0.1, "metal_light")    # side posts
    s.box(xm + hw - 0.02, y1 + 0.02, xm + hw + 0.18, y1 + 0.2, 0, hz + 0.1, "metal_light")
    s.box(xm - hw - 0.18, y1 + 0.02, xm + hw + 0.18, y1 + 0.2, hz + 0.1, hz + 0.28, "metal_light")  # header
    s.box(xm - hw, y1 - 0.02, xm + hw, y1 + 0.02, 0.0, hz + 0.1, "glass_office")                # glass behind
    # two leaves: glass in an aluminium frame, each with a kick rail and a vertical push bar at the split
    for sgn in (-1, 1):
        lx0 = xm - hw + 0.03 if sgn < 0 else xm + 0.04
        lx1 = xm - 0.04 if sgn < 0 else xm + hw - 0.03
        s.box(lx0, y1 + 0.05, lx1, y1 + 0.16, 0.0, hz, "metal_light")                              # leaf frame
        s.box(lx0 + 0.06, y1 + 0.16, lx1 - 0.06, y1 + 0.2, 0.34, hz - 0.1, "glass")             # glass pane
        s.box(lx0, y1 + 0.16, lx1, y1 + 0.2, 0.0, 0.34, "metal_grey")                              # kick rail
        s.box(lx0, y1 + 0.16, lx1, y1 + 0.2, 1.1, 1.16, "metal_light")                              # mid rail
        bx = (xm - 0.2) if sgn < 0 else (xm + 0.14)
        s.box(bx, y1 + 0.2, bx + 0.06, y1 + 0.3, 0.8, 1.9, "chrome")                              # push bar
        s.box(bx - 0.01, y1 + 0.2, bx + 0.07, y1 + 0.24, 0.85, 0.9, "chrome")
        s.box(bx - 0.01, y1 + 0.2, bx + 0.07, y1 + 0.24, 1.8, 1.85, "chrome")
    s.box(xm - 0.04, y1 + 0.02, xm + 0.04, y1 + 0.2, 0.0, hz, "metal_dark")                          # the split
    s.box(xm - hw - 0.1, y1, xm + hw + 0.1, y1 + 0.55, 0.0, 0.05, "metal_light")                    # threshold plate
    s.box(xm - 0.05, y1 + 0.1, xm + 0.05, y1 + 0.55, 0.0, 0.07, "metal_dark")                        # door track
    # sensor box + sign plate above
    s.box(xm - 0.7, y1 + 0.1, xm + 0.7, y1 + 0.3, hz + 0.28, hz + 0.5, "metal_dark")
    s.box(xm - 0.1, y1 + 0.3, xm + 0.1, y1 + 0.34, hz + 0.32, hz + 0.44, "neon_blue")
    s.box(xm - 1.6, y1 + 0.2, xm - 1.0, y1 + 0.24, hz + 0.3, hz + 0.45, "gold_bright")
    s.box(xm + 1.0, y1 + 0.2, xm + 1.6, y1 + 0.24, hz + 0.3, hz + 0.45, "gold_bright")


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
    vaulttech_door(s, xm, y1)
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
    R = r * CELL_M
    s.cyl(cx, cy, 0, 0.45, R, "stone", verts=32)                       # basin body
    s.cyl(cx, cy, 0.4, 0.5, R - 0.2, "fountain_surface", verts=32)                # water surface inside the rim
    ring = [(cx + math.cos(a * math.pi / 16) * (R - 0.1) / CELL_M, cy + math.sin(a * math.pi / 16) * (R - 0.1) / CELL_M, 0.52)
            for a in range(33)]
    s.tube(ring, 0.1, "stone")                                         # rounded stone rim
    s.cyl(cx, cy, 0.5, 1.4, 0.35, "stone", verts=16)
    s.cyl(cx, cy, 1.4, 1.5, 0.9, "stone", verts=16)
    s.cyl(cx, cy, 1.45, 1.52, 0.75, "fountain_surface", verts=16)
    s.cyl(cx, cy, 1.5, 2.1, 0.12, "stone", verts=10)
    s.sphere(cx, cy, 2.15, 0.16, "fountain_surface")
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
    # arched door of the community centre / library, with a sign beside it
    s.set_solid(11.2, AV0 - 4.0, 12.4, AV0 - 3.2, False)
    arched_door(s, 11.8, AV0 - 4.0 + 0.1)
    s.box(12.9, AV0 - 3.3, 15.1, AV0 - 3.12, 1.85, 2.5, "sign_blue")
    s.text("COMMUNITY", 14.0, AV0 - 3.1, 2.28, 0.2, "robot_white", face="left")
    s.text("CENTRE", 14.0, AV0 - 3.1, 2.02, 0.2, "robot_white", face="left")
    s.warp(11.2, AV0 - 3.7, 12.4, AV0 - 3.24, "community_centre", 9.5, 12.4, "up")
    for (x0, x1, mat) in ((2.2, 3.4, "poster_red"), (3.6, 4.6, "poster_yellow"), (17.4, 18.6, "poster_blue")):
        poster(s, x0, x1, AV0 - 4.0 + 0.62, 0.55, 2.0, mat)
    ivy(s, 0.3, 1.6, AV0 - 4.0 + 0.6, 2.6)
    for x in (0.8, 6.0, 20.6):
        weeds(s, x, AV0 - 3.0, 3)
    for (x, kind) in ((5.4, "flowers"), (16.6, "bush"), (21.6, "flowers")):
        potted_plant(s, x, AV0 - 3.4, kind)
    conifer(s, 23.6, AV0 - 3.0, 3.0)
    shrub(s, 24.4, AV0 - 2.2, 0.4, "leaves_light")

    # ---- north-east block: Corner Market, a slim house and the VaultTech tower ----
    corner_market_building(s, CS1 + 5, AV0 - 4)
    diner_building(s, 49.2, 57.4, AV0 - 4)
    s.box(54, 14, W, AV0 - 4, -0.1, 0.01, "plaza_gold", layer="floor")
    vaulttech_tower(s, 56, 2, 70, 14)
    s.set_solid(61.5, 13.0, 64.5, 14.0, False)                                        # lobby entrance
    s.warp(61.5, 13.3, 64.5, 14.0, "vaulttech_lobby", 9.0, 14.4, "up")
    for x in (58.8, 70.5):
        s.kit("Prop_Planter_Single", x, 16.5, solid=True, occlude=True)
    for x in (61, 65, 68):
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
    for x in (CS1 + 16.0, CS1 + 22.6):
        weeds(s, x, AV0 - 3.6, 3)
    conifer(s, CS1 + 3.9, AV0 - 3.3, 3.4)
    shrub(s, CS1 + 4.3, AV0 - 2.6, 0.4)
    street_tree(s, CS1 + 2.4, AV0 - 1.2)
    poster(s, CS1 + 5.2, CS1 + 6.2, AV0 - 4 + 0.08, 0.6, 1.8, "poster_yellow")
    for x in (8.0, 19.0):
        s.kit("Sidewalk_Planter", x, AV0 - 1.4, solid=True, occlude=False)
        tree(s, x, AV0 - 1.4, 0.95)
    hydrant(s, CS1 + 1.2, AV0 - 1.0)
    bus_stop(s, 40.0, 44.0, AV1 + 3.2)
    for x in (5.5, 20.5, 57.0, 63.5):
        street_tree(s, x, AV1 + 2.4)
    for x in (4.0, 18.0, 42.0, 64.0):
        street_tree(s, x, RIVER - 2.0)
    for x in (47.5, 48.4):
        potted_plant(s, x, AV1 + 3.4, "bush")

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
    s.box(14.8, 43.8, 20.2, 46.5, -0.1, 0.1, "pond_surface", layer="floor")
    s.set_solid(14.5, 43.5, 20.499, 46.799)
    for (x, y, sc) in ((7.6, 36.2, 1.0), (19.5, 36.5, 1.1), (4.0, 45.5, 1.05), (7.5, 46.0, 0.85), (21.0, 41.0, 0.9)):
        tree(s, x, y, sc)
    for (x, y) in ((6.0, 43.5), (13.5, 36.8)):
        planter(s, x, y)
    park_toilet(s, 1.6, 36.8, 4.6, 39.8)
    flower_bed(s, 12.4, 42.4, 14.0, 43.2)
    flower_bed(s, 16.4, 37.6, 18.4, 38.5)
    hedge(s, 1.4, 9.6, P1 - 0.5)
    hedge(s, 12.4, 14.0, P1 - 0.5)
    for (x, y, r, m) in ((1.8, 35.0, 0.45, "leaves"), (8.6, 35.2, 0.4, "leaves_light"), (16.2, 35.0, 0.45, "leaves"),
                         (21.2, 46.6, 0.45, "leaves_light"), (12.8, 45.6, 0.4, "leaves")):
        shrub(s, x, y, r, m)
    conifer(s, 1.8, 46.4, 3.2)
    conifer(s, 21.4, 35.2, 3.6)

    # ---- south-east block: fountain square ----
    s.box(CS1 + 4, AV1 + 4, W, RIVER - 4, -0.1, 0.01, "plaza_stone", layer="floor")
    fountain(s, 53, 41)
    for (x0, x1, y) in ((47, 49.6, 38.0), (56.4, 59.0, 38.0), (47, 49.6, 45.0), (56.4, 59.0, 45.0)):
        bench_along_x(s, x0, x1, y)
    for (x, y) in ((40, 36), (66, 36), (40, 46), (66, 46)):
        tree(s, x, y, 1.0)
    for (x, y) in ((44, 41), (62, 41)):
        lamp_post(s, x, y)
    for (x, y) in ((46.3, 38.0), (59.7, 38.0), (46.3, 45.0), (59.7, 45.0)):
        potted_plant(s, x, y, "flowers")
    for (x0, y0) in ((49.6, 35.6), (54.6, 35.6), (49.6, 46.6), (54.6, 46.6)):
        flower_bed(s, x0, y0, x0 + 1.8, y0 + 0.8)
    for (x, y) in ((38.6, 47.0), (67.4, 47.0)):
        conifer(s, x, y, 3.0)

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
    s.set_solid(x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6)


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


def flower_bed(s, x0, y0, x1, y1, rnd=None):
    """Low stone-edged bed full of flowers and small leafy plants."""
    rnd = rnd or random.Random(int(x0 * 37 + y0 * 11))
    s.box(x0, y0, x1, y1, 0, 0.18, "stone")
    s.box(x0 + 0.1, y0 + 0.1, x1 - 0.1, y1 - 0.1, 0.18, 0.2, "soil")
    n = int((x1 - x0) * (y1 - y0) * 9) + 4
    for _ in range(n):
        x = rnd.uniform(x0 + 0.2, x1 - 0.2)
        y = rnd.uniform(y0 + 0.2, y1 - 0.2)
        s.sphere(x, y, 0.27, rnd.uniform(0.08, 0.12), "leaves_light" if rnd.random() < 0.4 else "leaves")
        s.sphere(x + rnd.uniform(-0.08, 0.08), y + rnd.uniform(-0.08, 0.08), 0.36, 0.065, rnd.choice(FLOWERS))
    s.set_solid(x0, y0, x1, y1)


def hedge(s, x0, x1, y, h=0.8):
    """Clipped hedge along x."""
    s.box(x0, y - 0.3, x1, y + 0.3, 0, h - 0.15, "leaves")
    rnd = random.Random(int(x0 * 7 + y * 3))
    x = x0 + 0.2
    while x < x1 - 0.1:
        s.sphere(x, y + rnd.uniform(-0.1, 0.1), h - 0.15, 0.24, "leaves" if rnd.random() < 0.6 else "leaves_light")
        x += 0.35
    s.set_solid(x0, y - 0.3, x1, y + 0.3)
    s.occluder(x0, y - 0.4, x1, y + 0.4, h)


def street_tree(s, x, y):
    """Small sidewalk tree in an iron grate."""
    s.box(x - 0.6, y - 0.6, x + 0.6, y + 0.6, 0, 0.03, "metal_dark", layer="floor")
    s.box(x - 0.45, y - 0.45, x + 0.45, y + 0.45, 0.0, 0.035, "soil", layer="floor")
    tree(s, x, y, 0.8)


def park_toilet(s, x0, y0, x1, y1):
    """Small public toilet in City Park: brick walls, flat roof, a WC sign and a door facing +y."""
    h = 2.9
    s.box(x0, y0, x1, y1, 0, h, "brick_brown")
    s.box(x0 - 0.1, y1 - 0.12, x1 + 0.1, y1 + 0.05, 0, 0.4, "concrete")                # plinth
    s.box(x0 - 0.15, y0 - 0.15, x1 + 0.15, y1 + 0.15, h, h + 0.12, "concrete")           # roof slab
    s.box(x0 - 0.15, y0 - 0.15, x1 + 0.15, y1 + 0.15, h + 0.12, h + 0.16, "roof")
    xm = (x0 + x1) / 2
    door_left(s, xm - 0.6, xm + 0.6, y1, 2.2, mat="sign_blue")
    s.box(xm - 1.0, y1 - 0.05, xm + 1.0, y1 + 0.1, 2.35, 2.85, "sign_blue")
    s.text("WC", xm, y1 + 0.13, 2.6, 0.38, "robot_white", face="left")
    window_left(s, x0 + 0.25, x0 + 0.85, y1, 1.4, 2.1)
    window_left(s, x1 - 0.85, x1 - 0.25, y1, 1.4, 2.1)
    s.set_solid(x0, y0, x1 - 0.001, y1 - 0.001)
    s.set_solid(xm - 0.6, y1 - 0.8, xm + 0.6, y1, False)                                 # doorway
    s.occluder(x0, y0, x1, y1, h + 0.3)
    s.warp(xm - 0.6, y1 - 0.5, xm + 0.6, y1, "public_toilet", 3.5, 4.3, "up")


def arched_door(s, xm, y_face, hw=0.58, hz=1.65, r=0.44):
    """Door leaves filling the arched opening of the community centre: dark wood with raised panels, a fan
    window with muntins in the arch, brass handles and a stone step. xm / y_face in cells."""
    d = 0.04 / 0.75
    rc = r / CELL_M
    s.box(xm - hw - 0.02, y_face - d, xm + hw + 0.02, y_face + d, 0, hz, "wood_dark")              # leaves
    s.cyl(xm, y_face, hz, hz + 0.1, r, "wood_dark", axis="y", verts=24)
    s.cyl(xm, y_face + d, hz + 0.02, hz + 0.1, r - 0.1, "glass", axis="y", verts=24)             # fan window
    s.box(xm - 0.03, y_face + d, xm + 0.03, y_face + 2 * d, hz, hz + r - 0.08, "metal_dark")     # muntins
    s.box(xm - rc + 0.1, y_face + d, xm + rc - 0.1, y_face + 2 * d, hz + 0.02, hz + 0.06, "metal_dark")
    s.box(xm - hw, y_face + d, xm - 0.02, y_face + 1.8 * d, 1.0, 1.55, "wood_dark")              # raised panels
    s.box(xm + 0.02, y_face + d, xm + hw, y_face + 1.8 * d, 1.0, 1.55, "wood_dark")
    s.box(xm - hw, y_face + d, xm - 0.02, y_face + 1.8 * d, 0.2, 0.85, "wood_dark")
    s.box(xm + 0.02, y_face + d, xm + hw, y_face + 1.8 * d, 0.2, 0.85, "wood_dark")
    s.box(xm - 0.015, y_face + d, xm + 0.015, y_face + 2 * d, 0, hz, "metal_dark")                # leaf split
    for sgn in (-1, 1):
        s.box(xm + sgn * 0.14 - 0.02, y_face + d, xm + sgn * 0.14 + 0.02, y_face + 3 * d, 0.85, 1.15, "brass")
    s.box(xm - hw - 0.12, y_face - 0.02, xm + hw + 0.12, y_face + 0.4, 0.0, 0.1, "stone")          # step


def diner_building(s, x0, x1, fy):
    """The diner: a wide one-storey corner diner in purple stucco, facade at y = fy facing +y, big display
    windows, a striped awning, a large neon DINER sign and a glass door. Rear annex goes back 7.5 cells."""
    h = 4.2
    yb = fy - 4.0                      # the front block is 4 cells deep, the annex goes further back
    ya = fy - 7.5
    xa = x1 - 1.6                      # annex stops before the VaultTech tower
    s.box(x0, yb, x1, fy, 0, h, "plaster_purple")
    s.box(x0, ya, xa, yb, 0, h, "plaster_purple")
    s.box(x0 - 0.05, fy - 0.08, x1 + 0.05, fy + 0.05, 0, 0.4, "stone")                # plinth
    # parapet cornice and roof with a rim, vent and two air-conditioning boxes
    s.box(x0 - 0.1, fy - 0.1, x1 + 0.1, fy + 0.12, h - 0.2, h + 0.1, "trim_white")
    s.box(x0 - 0.1, ya, x0 + 0.05, yb, h - 0.2, h + 0.1, "trim_white")
    s.box(x0, yb, x1, fy - 0.1, h, h + 0.04, "roof")
    s.box(x0, ya, xa, yb, h, h + 0.04, "roof")
    s.box(x0 + 1.0, yb + 0.6, x0 + 2.4, yb + 1.6, h + 0.04, h + 0.65, "metal_light")
    s.box(x0 + 1.1, yb + 0.7, x0 + 2.3, yb + 0.9, h + 0.65, h + 0.72, "metal_dark")
    s.box(x0 + 3.2, yb + 1.2, x0 + 4.4, yb + 2.0, h + 0.04, h + 0.55, "metal_light")
    s.cyl(x1 - 2.6, yb + 1.0, h + 0.04, h + 0.8, 0.14, "metal_grey", verts=10)
    # display windows with a warm lit interior (counter, red stools silhouetted) and a lit sign band
    for (wx0, wx1) in ((x0 + 0.7, x0 + 2.9), (x1 - 3.1, x1 - 0.7)):
        s.box(wx0 - 0.14, fy - 0.1, wx1 + 0.14, fy + 0.08, 0.62, 2.42, "metal_light")
        s.box(wx0, fy - 0.2, wx1, fy - 0.12, 0.76, 2.28, "shop_light")
        s.box(wx0, fy - 0.2, wx1, fy - 0.0, 0.76, 1.12, "diner_teal")                # counter front
        n = int((wx1 - wx0) / 0.6)
        for k in range(n):
            sx = wx0 + 0.3 + k * (wx1 - wx0 - 0.4) / max(n - 1, 1)
            s.cyl(sx, fy - 0.12, 1.12, 1.4, 0.1, "diner_red", verts=8)
        s.box(wx0, fy - 0.01, wx1, fy + 0.04, 0.76, 2.28, "glass")
        s.box((wx0 + wx1) / 2 - 0.03, fy - 0.1, (wx0 + wx1) / 2 + 0.03, fy + 0.07, 0.76, 2.28, "metal_light")
        s.box(wx0 - 0.1, fy - 0.1, wx1 + 0.1, fy + 0.2, 0.52, 0.62, "stone")             # sill
    s.text("OPEN", x1 - 1.9, fy + 0.07, 1.9, 0.26, "neon_blue", face="left")
    s.box(x1 - 2.6, fy + 0.04, x1 - 1.2, fy + 0.07, 1.72, 1.74, "neon_red")
    # door: aluminium frame, glass leaf with a push bar, step and a mat
    dx0, dx1 = 52.25, 53.75
    d = 0.04 / 0.75
    s.box(dx0 - 0.14, fy - d, dx1 + 0.14, fy + 1.5 * d, 0, 2.5, "metal_light")
    s.box(dx0, fy - 1.2 * d, dx1, fy + 2 * d, 0, 2.38, "glass")
    s.box(dx0, fy - 1.2 * d, dx1, fy + 2.4 * d, 0, 0.35, "metal_light")               # kick plate
    s.box((dx0 + dx1) / 2 - 0.03, fy - 1.2 * d, (dx0 + dx1) / 2 + 0.03, fy + 3 * d, 0.35, 2.38, "metal_dark")
    s.box(dx0 + 0.12, fy + 3 * d, dx0 + 0.2, fy + 7 * d, 0.9, 1.5, "chrome")          # handles
    s.box(dx1 - 0.2, fy + 3 * d, dx1 - 0.12, fy + 7 * d, 0.9, 1.5, "chrome")
    s.box(dx0 - 0.2, fy, dx1 + 0.2, fy + 0.45, 0.0, 0.07, "stone")                    # step
    s.box(dx0 - 0.1, fy + 0.05, dx1 + 0.1, fy + 0.4, 0.07, 0.09, "mat_red")
    # striped awning along the whole front
    x = x0 + 0.1
    i = 0
    while x < x1 - 0.1:
        s.wedge(x, fy, min(x + 0.5, x1 - 0.1), fy + 1.2, 2.95, 2.6, "y",
                "diner_red" if i % 2 == 0 else "awning_white")
        x += 0.5
        i += 1
    # big neon sign band above the awning
    s.box(x0 + 0.6, fy - 0.05, x1 - 0.6, fy + 0.16, 3.05, 4.0, "diner_teal")
    s.box(x0 + 0.5, fy - 0.05, x1 - 0.5, fy + 0.2, 3.0, 3.08, "chrome")
    s.box(x0 + 0.5, fy - 0.05, x1 - 0.5, fy + 0.2, 3.97, 4.05, "chrome")
    xm = (x0 + x1) / 2
    s.text("DINER", xm, fy + 0.2, 3.5, 0.78, "neon_red", face="left")
    s.box(xm - 2.4, fy + 0.17, xm + 2.4, fy + 0.2, 3.2, 3.24, "neon_blue")
    s.box(xm - 2.4, fy + 0.17, xm + 2.4, fy + 0.2, 3.82, 3.86, "neon_blue")
    # street details
    potted_plant(s, 51.35, fy + 0.7, "bay")
    potted_plant(s, 54.65, fy + 0.7, "flowers")
    a_frame_sign(s, 56.4, fy + 1.5)
    weeds(s, x0 + 0.4, fy + 0.5, 3)
    s.set_solid(x0, ya, xa - 0.001, yb)
    s.set_solid(x0, yb, x1 - 0.001, fy - 0.001)
    s.set_solid(52.0, fy - 1.0, 53.999, fy - 0.001, False)                            # door cells walkable
    s.occluder(x0, yb, x1, fy, h + 0.8)
    s.occluder(x0, ya, xa, yb, h + 0.8)
    s.warp(52.0, fy - 1.0, 54.0, fy, "diner", 5.5, 8.4, "up")


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
    potted_plant(s, x0 + 3.75, fy + 0.45, "bay")
    potted_plant(s, x0 + 6.25, fy + 0.45, "bay")
    a_frame_sign(s, x0 + 7.4, fy + 1.6)
    s.set_solid(x0, y0, x1 - 0.001, fy - 0.001)
    s.set_solid(x0 + 4, fy - 1, x0 + 5.999, fy - 0.001, False)                  # door cells walkable
    s.occluder(x0, y0, x1, fy, cm_h + 5.6)
    s.warp(x0 + 4, fy - 1, x0 + 6, fy, "corner_market", 8.0, 16.4, "up")


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


PRODUCT_PROPS = {"ketchup": ("food/KetchupBottle", 0.26), "mustard": ("food/MustardBottle", 0.26),
                 "pbutter": ("food/PeanutButter", 0.15), "jarL": ("food/Jar_Large", 0.17),
                 "bottle1": ("food/Bottle1", 0.30), "soda": ("food/Soda", 0.17)}


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
    if kind in PRODUCT_PROPS:
        name, h = PRODUCT_PROPS[kind]
        mn, mx = PROP_DIMS[name]
        sc = h / (mx[2] - mn[2])
        w, d = (mx[0] - mn[0]) * sc / CELL_M, (mx[1] - mn[1]) * sc / CELL_M
        s.prop(name, x + w / 2, y_front - d / 2 - 0.01, h=h, z=z, solid=False, occlude=False)
        return w
    raise ValueError(kind)


def product_width(kind):
    if kind in PRODUCT_PROPS:
        name, h = PRODUCT_PROPS[kind]
        mn, mx = PROP_DIMS[name]
        return (mx[0] - mn[0]) * h / (mx[2] - mn[2]) / CELL_M
    return {"milk": 0.15 * M, "cereal": 0.22 * M, "can": 0.13 * M, "bottle": 0.11 * M, "jar": 0.14 * M}[kind]


def product_row(s, kind, colours, x0, x1, y_front, z, rnd):
    x = x0 + 0.05
    while True:
        colour = rnd.choice(colours)
        # measure first with a dry run width
        if x + product_width(kind) > x1 - 0.05:
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






class SwapProxy:
    """Mirrors every call across the x = y diagonal so helpers written for 'facing +y' (gondola, product...)
    can build things standing against a wall at x facing +x. Use: gondola(SwapProxy(s), u0, v0, u1, v1, ...)
    -> engine x = v (depth), engine y = u (along the wall)."""

    def __init__(self, s):
        self.s = s

    def box(self, x0, y0, x1, y1, *a, **k):
        return self.s.box(y0, x0, y1, x1, *a, **k)

    def cyl(self, x, y, *a, **k):
        return self.s.cyl(y, x, *a, **k)

    def sphere(self, x, y, *a, **k):
        return self.s.sphere(y, x, *a, **k)

    def set_solid(self, x0, y0, x1, y1, value=True):
        return self.s.set_solid(y0, x0, y1, x1, value)

    def occluder(self, x0, y0, x1, y1, h):
        return self.s.occluder(y0, x0, y1, x1, h)

    def prop(self, name, x, y, rot=0, **k):
        return self.s.prop(name, y, x, rot=(90 - rot) % 360, **k)








# ---------------------------------------------------------------------------------------------
# Interiors v2: cutaway rooms (proposal)
# ---------------------------------------------------------------------------------------------
def wall_y(s, x0, x1, y, h, paper="wp_cream", wains="wood_green", wain_h=0.95, cap=True, trim="trim_white"):
    """Back wall running along x, interior face at y facing +y. Body is 0.4 cells thick (towards -y)."""
    s.box(x0, y - 0.4, x1, y, 0, h, paper)
    s.box(x0, y, x1, y + 0.035, 0.12, wain_h, wains)                         # wainscot panelling
    s.box(x0, y, x1, y + 0.05, 0, 0.12, trim)                         # skirting
    s.box(x0, y, x1, y + 0.07, wain_h, wain_h + 0.07, trim)          # chair rail
    s.box(x0, y, x1, y + 0.05, h - 0.1, h, trim)                      # crown moulding
    if cap:
        s.box(x0, y - 0.48, x1, y + 0.08, h, h + 0.12, "wall_cap")           # thick light wall top


def wall_x(s, y0, y1, x, h, paper="wp_cream", wains="wood_green", wain_h=0.95, cap=True, trim="trim_white"):
    """Back wall running along y, interior face at x facing +x. Body is 0.4 cells thick (towards -x)."""
    s.box(x - 0.4, y0, x, y1, 0, h, paper)
    s.box(x, y0, x + 0.035, y1, 0.12, wain_h, wains)
    s.box(x, y0, x + 0.05, y1, 0, 0.12, trim)
    s.box(x, y0, x + 0.07, y1, wain_h, wain_h + 0.07, trim)
    s.box(x, y0, x + 0.05, y1, h - 0.1, h, trim)
    if cap:
        s.box(x - 0.48, y0, x + 0.08, y1, h, h + 0.125, "wall_cap")


def wall_stub_y(s, x0, x1, y, h=0.34, mat="wp_cream"):
    """Low cutaway wall facing the camera (y = its front face), thick light top."""
    s.box(x0, y - 0.4, x1, y, 0, h, mat)
    s.box(x0, y - 0.45, x1, y + 0.05, h, h + 0.1, "wall_cap")
    s.box(x0, y, x1, y + 0.02, 0, 0.1, "trim_white")


def wall_stub_x(s, y0, y1, x, h=0.34, mat="wp_cream"):
    s.box(x - 0.4, y0, x, y1, 0, h, mat)
    s.box(x - 0.45, y0, x + 0.05, y1, h, h + 0.11, "wall_cap")
    s.box(x, y0, x + 0.02, y1, 0, 0.1, "trim_white")


def window_y(s, x0, x1, y, z0, z1, curtain=False):
    """Window in a +y facing back wall: white frame, glowing sky pane, mullions, sill."""
    s.box(x0 - 0.1, y - 0.05, x1 + 0.1, y + 0.05, z0 - 0.1, z1 + 0.1, "trim_white")
    s.box(x0, y - 0.2, x1, y + 0.06, z0, z1, "window_sky")
    mid = (x0 + x1) / 2
    s.box(mid - 0.025, y, mid + 0.025, y + 0.09, z0, z1, "trim_white")
    s.box(x0, y, x1, y + 0.09, (z0 + z1) / 2 - 0.02, (z0 + z1) / 2 + 0.02, "trim_white")
    s.box(x0 - 0.15, y, x1 + 0.15, y + 0.16, z0 - 0.16, z0 - 0.08, "trim_white")   # sill
    if curtain:
        for cx0, cx1 in ((x0 - 0.3, x0 + 0.1), (x1 - 0.1, x1 + 0.3)):
            s.box(cx0, y, cx1, y + 0.14, z0 - 0.15, z1 + 0.25, "curtain_red")
        s.box(x0 - 0.4, y, x1 + 0.4, y + 0.12, z1 + 0.25, z1 + 0.3, "brass")


def window_x(s, y0, y1, x, z0, z1, curtain=False):
    s.box(x - 0.05, y0 - 0.1, x + 0.05, y1 + 0.1, z0 - 0.1, z1 + 0.1, "trim_white")
    s.box(x - 0.2, y0, x + 0.06, y1, z0, z1, "window_sky")
    mid = (y0 + y1) / 2
    s.box(x, mid - 0.025, x + 0.09, mid + 0.025, z0, z1, "trim_white")
    s.box(x, y0, x + 0.09, y1, (z0 + z1) / 2 - 0.02, (z0 + z1) / 2 + 0.02, "trim_white")
    s.box(x, y0 - 0.15, x + 0.16, y1 + 0.15, z0 - 0.16, z0 - 0.08, "trim_white")
    if curtain:
        for cy0, cy1 in ((y0 - 0.3, y0 + 0.1), (y1 - 0.1, y1 + 0.3)):
            s.box(x, cy0, x + 0.14, cy1, z0 - 0.15, z1 + 0.25, "curtain_red")
        s.box(x, y0 - 0.4, x + 0.12, y1 + 0.4, z1 + 0.25, z1 + 0.3, "brass")


def wall_clock_y(s, x, y, z, r=0.28):
    s.cyl(x, y + 0.03, z, z + 0.05, r + 0.04, "wood_dark", axis="y", verts=24)
    s.cyl(x, y + 0.08, z, z + 0.03, r, "clock_face", axis="y", verts=24)
    s.box(x - 0.012, y + 0.1, x + 0.012, y + 0.115, z, z + r * 0.8, "metal_dark")          # minute hand
    s.box(x - 0.012 + 0.0, y + 0.1, x + r * 0.55, y + 0.115, z - 0.012, z + 0.012, "metal_dark")  # hour hand


def wall_clock_x(s, x, y, z, r=0.28):
    s.cyl(x + 0.03, y, z, z + 0.05, r + 0.04, "wood_dark", axis="x", verts=24)
    s.cyl(x + 0.08, y, z, z + 0.03, r, "clock_face", axis="x", verts=24)
    s.box(x + 0.1, y - 0.012, x + 0.115, y + 0.012, z, z + r * 0.8, "metal_dark")
    s.box(x + 0.1, y, x + 0.115, y + r * 0.55, z - 0.012, z + 0.012, "metal_dark")


def picture_y(s, x0, x1, y, z0, z1, mat):
    s.box(x0 - 0.05, y, x1 + 0.05, y + 0.05, z0 - 0.05, z1 + 0.05, "frame_wood")
    s.box(x0, y + 0.05, x1, y + 0.065, z0, z1, mat)


def picture_x(s, y0, y1, x, z0, z1, mat):
    s.box(x, y0 - 0.05, x + 0.05, y1 + 0.05, z0 - 0.05, z1 + 0.05, "frame_wood")
    s.box(x + 0.05, y0, x + 0.065, y1, z0, z1, mat)


def rug(s, x0, y0, x1, y1, outer, band, field, layer="floor"):
    s.box(x0, y0, x1, y1, 0.0, 0.012, outer, layer=layer)
    s.box(x0 + 0.18, y0 + 0.18, x1 - 0.18, y1 - 0.18, 0.012, 0.02, band, layer=layer)
    s.box(x0 + 0.32, y0 + 0.32, x1 - 0.32, y1 - 0.32, 0.02, 0.028, field, layer=layer)
    n = max(2, int((x1 - x0 - 1.0) / 0.9))
    for i in range(n):                       # diamond-ish motifs along the middle
        cx = x0 + (x1 - x0) * (i + 0.5) / n
        cy = (y0 + y1) / 2
        s.box(cx - 0.14, cy - 0.14, cx + 0.14, cy + 0.14, 0.028, 0.036, band, layer=layer)
        s.box(cx - 0.07, cy - 0.07, cx + 0.07, cy + 0.07, 0.036, 0.044, outer, layer=layer)


def cutaway_floor(s, x0, y0, x1, y1, mat):
    """Floor slab with a visible edge thickness (for the cut sides)."""
    s.box(x0, y0, x1, y1, -0.4, -0.02, "floor_edge", layer="floor")
    s.box(x0, y0, x1, y1, -0.02, 0.0, mat, layer="floor")


def cardboard_box(s, x, y, w, d, h, z=0.0):
    s.box(x, y, x + w, y + d, z, z + h, "cardboard")
    s.box(x + 0.02, y + d - 0.01, x + w - 0.02, y + d + 0.012, z + h * 0.45, z + h * 0.6, "cardboard_dark")   # label band
    s.box(x + w * 0.5 - 0.03, y, x + w * 0.5 + 0.03, y + d, z + h, z + h + 0.008, "cardboard_dark")          # tape


def crate_of(s, x0, y0, x1, y1, fruit_prop, h_item, rnd, z_base=0.0, hgt=0.3, tilt_layers=2, colours=None):
    """Wooden crate with a heap of real food models."""
    s.box(x0, y0, x1, y1, z_base, z_base + hgt, "crate")
    s.box(x0 + 0.06, y0 + 0.06, x1 - 0.06, y1 - 0.06, z_base + hgt, z_base + hgt + 0.012, "wood_dark")
    cols = max(2, int((x1 - x0 - 0.2) / 0.22))
    rows = max(2, int((y1 - y0 - 0.2) / 0.22))
    for layer in range(tilt_layers):
        inset = 0.1 + layer * 0.1
        for i in range(cols - layer):
            for j in range(rows - layer):
                px = x0 + inset + (x1 - x0 - 2 * inset) * ((i + 0.5) / max(1, cols - layer)) + rnd.uniform(-0.03, 0.03)
                py = y0 + inset + (y1 - y0 - 2 * inset) * ((j + 0.5) / max(1, rows - layer)) + rnd.uniform(-0.03, 0.03)
                s.prop(fruit_prop, px, py, rot=rnd.choice((0, 90, 180, 270)), h=h_item * rnd.uniform(0.9, 1.1),
                       z=z_base + hgt + layer * h_item * 0.62, solid=False, occlude=False, colours=colours)


def market_v2():
    W, H = 17, 18
    s = Scene("corner_market", "Corner Market", W, H, origin_x=H * 16 + 24, origin_y=64,
              img_w=(W + H) * 16 + 48, img_h=64 + (W + H) * 8 + 36)
    s.sun = False
    WH = 3.2                       # wall height (m)
    SY = 5.0                       # y of the shop's north wall
    # --- floors (cutaway slab with visible edge) ---
    cutaway_floor(s, 0, SY, W, H, "floor_wood2")
    cutaway_floor(s, 11, 0, W, SY, "store_floor")
    # entrance tiles + runner rugs + door mat
    s.box(4.2, 13.4, 11.2, 17.6, 0.0, 0.01, "tile_cafe", layer="floor")
    s.box(4.2, 13.4, 11.2, 13.48, 0.01, 0.014, "rug_red", layer="floor")
    rug(s, 4.3, 10.2, 9.2, 11.8, "rug_red", "rug_cream", "rug_navy")           # runner between the gondolas
    rug(s, 5.0, 6.5, 9.8, 7.9, "rug_green", "rug_cream", "rug_teal")           # runner in the back aisle
    s.box(6.5, 16.3, 9.5, 17.6, 0.012, 0.03, "mat_red", layer="floor")
    s.box(6.6, 16.4, 9.4, 17.5, 0.03, 0.036, "rug_gold", layer="floor")
    s.box(6.75, 16.55, 9.25, 17.35, 0.036, 0.042, "mat_red", layer="floor")

    # --- walls: north (shop) x -0.4..10.6, storeroom west wall, storeroom back wall ---
    wall_y(s, -0.4, 10.6, SY, WH)
    wall_x(s, 0.0, SY, 11.0, WH, paper="wp_cream", wains="wood_dark")        # storeroom west wall
    wall_x(s, SY, H - 0.4, 0.0, WH)                                            # shop west wall
    wall_y(s, 10.6, W, 0.0, WH, paper="wp_sage", wains="wood_dark")           # storeroom back wall
    # cutaway edges (low stubs): front with the door gap, right side, storeroom partition with doorway
    wall_stub_y(s, 0, 6.0, H)
    wall_stub_y(s, 10.0, W, H)
    wall_stub_x(s, 0, H, W)
    wall_stub_y(s, 11.0, 12.0, SY)
    wall_stub_y(s, 15.0, W - 0.4, SY)
    for jx in (12.0, 14.86):         # door jambs at the storeroom doorway
        s.box(jx, SY - 0.4, jx + 0.14, SY, 0, 2.35, "wood_dark")
    s.set_solid(0, 0, 11, SY - 0.001)                                          # void north of the shop
    s.set_solid(11, 4, 12, 5)                                                  # partition stubs (row 4)
    s.set_solid(15, 4, 16.999, 5)
    s.set_solid(W - 1, 0, W, H)                                                # right stub column
    s.set_solid(0, H - 1, 6, H)                                                # front stub row
    s.set_solid(10, H - 1, W, H)
    s.occluder(-0.4, SY - 0.4, 10.6, SY + 0.1, WH)
    s.occluder(-0.4, SY, 0.1, H, WH)

    rnd = random.Random(11)
    boxes = ["goods_red", "goods_yellow", "goods_blue", "goods_orange", "goods_green"]
    cans = ["goods_red", "goods_green", "goods_orange", "goods_blue"]
    jars = ["goods_red", "goods_orange", "goods_yellow"]
    bottles = ["bottle_green", "bottle_clear", "bottle_brown"]

    # --- north wall run (row 5): corner plant, wall shelving, bakery table, dairy fridge ---
    potted_plant(s, 0.75, 5.7, "bay")
    gondola(s, 1.2, 5.05, 6.0, 5.95, 2.0,
            [("can", cans), ("ketchup", ["x"]), ("jarL", ["x"]), ("cereal", boxes)], rnd)
    # bakery table with real bread
    s.box(6.25, 5.1, 7.85, 5.9, 0, 0.85, "wood")
    s.box(6.2, 5.05, 7.9, 5.95, 0.85, 0.9, "wood_dark")
    for i, bx in enumerate((6.55, 7.0, 7.45)):
        s.prop("food/Bread", bx, 5.5, rot=90 if i % 2 else 0, h=0.2, z=0.9, solid=False, occlude=False)
    s.box(6.35, 5.62, 7.75, 5.9, 0.9, 1.0, "wood_dark")
    s.set_solid(6.2, 5.05, 7.899, 5.949)
    s.occluder(6.2, 5.05, 7.9, 5.95, 1.1)
    s.box(6.1, SY, 8.0, SY + 0.06, 1.45, 2.15, "chalk_menu")
    s.box(6.05, SY, 8.05, SY + 0.04, 1.4, 1.45, "wood")
    s.text("FRESH BREAD", 7.05, SY + 0.07, 1.9, 0.2, "chalk", face="left")
    s.text("$2", 7.05, SY + 0.07, 1.62, 0.18, "chalk", face="left")
    # dairy fridge (lit)
    fx0, fx1, fy1, fh = 8.2, 10.9, 6.3, 2.2
    s.box(fx0, 5.05, fx1, fy1, 0, 0.25, "fridge_white")
    s.box(fx0, 5.05, fx1, 5.4, 0.25, fh, "fridge_light")
    s.box(fx0, 5.05, fx1, fy1, fh - 0.25, fh, "fridge_white")
    s.box(fx0, 5.05, fx0 + 0.12, fy1, 0, fh, "fridge_white")
    s.box(fx1 - 0.12, 5.05, fx1, fy1, 0, fh, "fridge_white")
    for lz, kind in ((0.25, "milk"), (0.85, "milk"), (1.4, "bottle")):
        s.box(fx0, 5.05, fx1, fy1 - 0.1, lz, lz + 0.03, "metal_light")
        product_row(s, kind, ["goods_blue", "goods_red", "goods_green"] if kind == "milk" else bottles,
                    fx0 + 0.15, fx1 - 0.15, fy1 - 0.2, lz + 0.03, rnd)
    for k in range(1, 3):
        xk = fx0 + k * (fx1 - fx0) / 3
        s.box(xk - 0.03, fy1 - 0.08, xk + 0.03, fy1, 0.25, fh - 0.25, "metal_light")
    s.box(fx0 + 0.5, fy1 - 0.05, fx1 - 0.5, fy1 + 0.02, fh + 0.05, fh + 0.4, "sign_blue")
    s.text("DAIRY", (fx0 + fx1) / 2, fy1 + 0.03, fh + 0.22, 0.24, "sign_text", face="left")
    s.set_solid(fx0, 5.05, fx1 - 0.001, fy1 - 0.001)
    s.occluder(fx0, 5.05, fx1, fy1, fh + 0.45)

    # wall decor north: clerestory windows above the shelves, clock, bunting, posters
    window_y(s, 1.7, 3.2, SY, 2.2, 2.95)
    window_y(s, 3.7, 5.2, SY, 2.2, 2.95)
    wall_clock_y(s, 7.05, SY, 2.65)
    picture_y(s, 9.0, 10.2, SY, 2.75, 3.05, "poster_orange")
    z0 = 2.2
    for i in range(9):                       # bunting along the top of the wall
        bx = 1.0 + i * 1.05
        col = ("flower_red", "flower_yellow", "awning_green", "wood_blue", "flower_pink")[i % 5]
        s.poly([(bx, SY + 0.06, 3.05), (bx + 0.5, SY + 0.06, 3.05), (bx + 0.25, SY + 0.06, 2.72)], col)

    # --- west wall run: shelving, freezer chest, fruit & veg crates ---
    sw = SwapProxy(s)
    gondola(sw, 6.15, 0.05, 10.85, 0.95, 2.0,
            [("bottle1", ["x"]), ("mustard", ["x"]), ("pbutter", ["x"]), ("cereal", boxes)], rnd)
    # freezer chest with a half-open sliding glass lid
    cx0, cy0, cx1, cy1 = 0.15, 11.3, 1.7, 14.3
    s.box(cx0, cy0, cx1, cy1, 0, 0.85, "fridge_white")
    s.box(cx0 + 0.1, cy0 + 0.1, cx1 - 0.1, cy1 - 0.1, 0.78, 0.8, "frozen_blue")
    s.box(cx0 - 0.03, cy0 - 0.03, cx1 + 0.03, cy0 + 0.1, 0.85, 0.93, "metal_light")
    s.box(cx0 - 0.03, cy1 - 0.1, cx1 + 0.03, cy1 + 0.03, 0.85, 0.93, "metal_light")
    s.box(cx0 - 0.03, cy0, cx0 + 0.1, cy1, 0.85, 0.93, "metal_light")
    s.box(cx1 - 0.1, cy0, cx1 + 0.03, cy1, 0.85, 0.93, "metal_light")
    fz = ("ice_cream_pink", "frozen_blue", "goods_yellow", "goods_green", "goods_orange", "goods_white")
    for i in range(10):
        for j in range(3):
            yy = cy0 + 0.25 + i * 0.255
            xx = cx0 + 0.25 + j * 0.42
            s.box(xx, yy, xx + 0.32, yy + 0.2, 0.8, 0.8 + 0.1 + (0.02 * ((i + j) % 2)), fz[(i * 2 + j) % len(fz)])
    s.box(cx0 + 0.02, cy0 + 1.7, cx1 - 0.02, cy1 - 0.02, 0.93, 0.97, "glass_lid")         # closed half of the lid
    s.box(cx0 + 0.02, cy0 + 1.7, cx1 - 0.02, cy0 + 1.78, 0.97, 1.0, "metal_light")
    s.set_solid(cx0, cy0, cx1 - 0.001, cy1 - 0.001)
    s.occluder(cx0, cy0, cx1, cy1, 1.1)
    # fruit & veg crates (real food models) on the west wall
    s.box(0.0, 14.55, 0.07, 17.3, 1.75, 2.2, "sign_green")
    s.text("FRESH FRUIT", 0.08, 15.95, 1.98, 0.22, "sign_text", face="right")
    s.box(0.2, 14.5, 1.7, 17.3, 0, 0.3, "wood_dark")                    # low stand
    produce = [("food/Apple", 0.15), ("food/Orange", 0.14), ("food/Tomato", 0.14)]
    for k, (pn, hh) in enumerate(produce):
        y0 = 14.6 + k * 0.92
        crate_of(s, 0.35, y0, 1.55, y0 + 0.82, pn, hh, rnd, z_base=0.3, hgt=0.14)
    s.set_solid(0.2, 14.5, 1.699, 17.299)
    s.occluder(0.2, 14.5, 1.7, 17.3, 0.8)
    # west wall decor
    window_x(s, 7.3, 8.8, 0.0, 2.2, 2.95)
    window_x(s, 9.3, 10.8, 0.0, 2.2, 2.95)
    wall_clock_x(s, 0.0, 12.8, 2.6)
    for i in range(7):
        by = 6.0 + i * 1.05
        col = ("flower_yellow", "wood_red", "awning_green", "flower_pink", "wood_blue")[i % 5]
        s.poly([(0.06, by, 3.05), (0.06, by + 0.5, 3.05), (0.06, by + 0.25, 2.72)], col)

    # --- free-standing gondolas with 2-cell aisles ---
    gondola(s, 4.0, 9.05, 9.0, 9.95, 1.55, [("bottle", bottles), ("cereal", boxes), ("can", cans)], rnd)
    gondola(s, 4.0, 12.05, 9.0, 12.95, 1.55, [("jar", jars), ("ketchup", ["x"]), ("soda", ["x"])], rnd)
    s.box(4.0, 9.95, 9.0, 10.0, 1.5, 1.65, "sign_blue")                  # header board (visible from the aisle below)
    s.text("OFFERS", 6.5, 10.02, 1.58, 0.16, "sign_text", face="left")
    s.box(4.0, 12.95, 9.0, 13.0, 1.5, 1.65, "price_yellow")
    s.text("2 FOR 1", 6.5, 13.02, 1.58, 0.16, "metal_dark", face="left")

    # --- produce island (right) ---
    s.box(11.2, 8.2, 13.8, 9.5, 0, 0.6, "wood")
    s.box(11.1, 8.1, 13.9, 9.6, 0.6, 0.66, "wood_dark")
    for k, (pn, hh) in enumerate([("food/Lettuce_Whole", 0.18), ("food/Carrot", 0.2), ("food/Apple", 0.15)]):
        x0 = 11.17 + k * 0.86
        crate_of(s, x0, 8.2, x0 + 0.8, 9.5, pn, hh, rnd, z_base=0.66, hgt=0.12, tilt_layers=2)
    s.box(11.3, 9.6, 13.7, 9.64, 0.28, 0.5, "price_yellow")
    s.set_solid(11.1, 8.1, 13.899, 9.599)
    s.occluder(11.1, 8.1, 13.9, 9.6, 1.2)

    # --- checkout (near the entrance) ---
    cx0, cx1, cy0, cy1 = 11.0, 15.6, 14.05, 14.95
    s.box(cx0, cy0, cx1, cy1, 0, 0.9, "wood")
    s.box(cx0, cy1 - 0.03, cx1, cy1 + 0.01, 0.1, 0.8, "wood_green")                # painted front panel
    s.box(cx0 - 0.05, cy0 - 0.05, cx1 + 0.05, cy1 + 0.05, 0.9, 0.95, "wood_dark")
    s.box(cx0 + 0.15, cy0 + 0.1, cx0 + 2.2, cy1 - 0.1, 0.95, 0.98, "belt_dark")
    for k in range(6):
        s.box(cx0 + 0.3 + k * 0.33, cy0 + 0.1, cx0 + 0.33 + k * 0.33, cy1 - 0.1, 0.98, 0.985, "metal_dark")
    s.box(cx0 + 2.5, cy0 + 0.1, cx0 + 3.4, cy1 - 0.1, 0.95, 1.15, "metal_dark")        # register
    s.box(cx0 + 2.55, cy0 + 0.15, cx0 + 3.35, cy1 - 0.15, 1.15, 1.2, "screen")
    s.box(cx0 + 2.6, cy1 - 0.25, cx0 + 3.3, cy1 - 0.08, 1.0, 1.1, "price_yellow")       # keys
    s.box(cx0 + 3.6, cy0 + 0.15, cx1 - 0.1, cy1 - 0.15, 0.95, 1.12, "goods_blue")      # card reader / scale stand
    for k in range(5):                                                                # candy rack at the end
        s.box(cx1 - 0.05, cy0 + 0.05 + k * 0.17, cx1 + 0.0, cy0 + 0.2 + k * 0.17, 0.95, 1.15,
              ("goods_red", "goods_yellow", "goods_pink", "goods_green", "goods_orange")[k])
    s.box(cx0 + 1.2, cy0 + 0.1, cx0 + 1.28, cy0 + 0.18, 0.98, 1.55, "metal_dark")      # little OPEN sign on a pole
    s.box(cx0 + 0.9, cy0 + 0.05, cx0 + 1.6, cy0 + 0.2, 1.55, 1.75, "sign_green")
    s.text("OPEN", cx0 + 1.25, cy0 + 0.22, 1.65, 0.14, "sign_text", face="left")
    s.set_solid(cx0, cy0, cx1 - 0.001, cy1 - 0.001)
    s.occluder(cx0, cy0, cx1, cy1, 1.3)
    # basket stack by the door + magazine / newspaper rack
    for k in range(4):
        z = k * 0.12
        s.box(5.0, 16.0, 5.9, 16.7, z, z + 0.1, "basket_red")
    s.box(5.05, 16.05, 5.85, 16.65, 0.46, 0.47, "basket_red")
    s.set_solid(5.0, 16.0, 5.899, 16.699)
    s.occluder(5.0, 16.0, 5.9, 16.7, 0.6)
    potted_plant(s, 10.5, 16.4, "bush")
    potted_plant(s, 2.4, 16.4, "flowers")
    potted_plant(s, 15.4, 13.4, "bay")
    # --- storeroom ---
    s.box(11.3, 0.1, 13.9, 0.9, 0, 0.1, "metal_shelf")
    for lz in (0.1, 0.8, 1.5):
        s.box(11.3, 0.1, 13.9, 0.9, lz, lz + 0.04, "metal_shelf")
    for px in (11.3, 13.8):
        s.box(px, 0.1, px + 0.1, 0.9, 0, 2.0, "metal_shelf")
    for lz, items in ((0.14, (0.55, 0.6, 0.55, 0.5)), (0.84, (0.5, 0.6, 0.7, 0.55)), (1.54, (0.45, 0.55, 0.6, 0.5))):
        x = 11.45
        for wd in items:
            cardboard_box(s, x, 0.3, wd * 0.58, 0.55, 0.4 + 0.05 * (int(x * 10) % 3), z=lz)
            x += wd * 0.58 + 0.05
    s.set_solid(11.3, 0.1, 13.899, 0.899)
    s.occluder(11.3, 0.1, 13.9, 0.9, 2.1)
    # box stacks on the west wall
    for (bx, by, bw, bd, bz, bh) in ((11.15, 1.4, 0.8, 0.9, 0, 0.55), (11.2, 1.45, 0.65, 0.7, 0.55, 0.45),
                                     (11.15, 2.4, 0.8, 0.8, 0, 0.5)):
        cardboard_box(s, bx, by, bw, bd, bh, z=bz)
    s.set_solid(11.1, 1.3, 11.999, 3.299)
    s.occluder(11.1, 1.3, 12.0, 3.3, 1.1)
    # mop bucket + mop
    s.cyl(11.55, 3.8, 0, 0.32, 0.22, "bucket_yellow", r2=0.28)
    s.cyl(11.55, 3.8, 0.28, 0.3, 0.24, "dirty_liquid")
    s.cyl(11.75, 3.7, 0.1, 1.3, 0.025, "wood")
    s.sphere(11.75, 3.7, 0.08, 0.18, "mop", sz=0.7)
    s.set_solid(11.2, 3.5, 11.999, 3.999)
    # staff table with chairs, mug and radio
    s.prop("house/Table_RoundSmall", 15.0, 1.3, h=0.62, solid=True)
    s.box(14.7, 1.15, 15.0, 1.45, 0.62, 0.72, "goods_white")
    s.box(15.1, 1.0, 15.5, 1.25, 0.62, 0.75, "metal_dark")
    # storeroom wall decor
    window_y(s, 12.6, 14.0, 0.0, 1.35, 2.3)
    s.box(14.6, 0.0, 15.7, 0.05, 1.5, 2.2, "poster_red")
    s.box(11.0, 2.0, 11.06, 3.2, 1.5, 2.2, "sign_blue")
    s.text("STAFF ONLY", 11.07, 2.6, 1.85, 0.17, "sign_text", face="right")
    wall_clock_x(s, 11.0, 4.0, 2.4, 0.22)

    # lights
    for (lx, ly) in ((3, 8), (7, 8), (12, 10), (3, 14), (8, 14), (13, 12)):
        s.point_light(lx, ly, 2.9, 130, colour=(1.0, 0.9, 0.72))
    s.point_light(13.5, 2.5, 2.6, 110, colour=(1.0, 0.92, 0.78))
    s.point_light(9.5, 5.5, 1.8, 40, colour=(0.85, 0.95, 1.0))
    s.warp(6.5, 17.1, 9.5, H, "city_centre", 44.0, 19.0, "down")
    return s




# ---------------------------------------------------------------------------------------------
# More interiors (proposals): bathhouse, diner, community centre, VaultTech lobby
# ---------------------------------------------------------------------------------------------
def std_room(ident, name, W, H, floor_mat, paper, wains, wain_h, wh, door, target, tx, ty, origin_y=64,
             mat_cols=("mat_red", "rug_gold")):
    """Cutaway room: back walls at x = 0 and y = 0, low stubs at the front (y = H) and right (x = W) with a door gap
    door = (x0, x1) cells (integers). Last row / column are the stubs (solid). Exit warp on the door mat."""
    s = Scene(ident, name, W, H, origin_x=H * 16 + 24, origin_y=origin_y, img_w=(W + H) * 16 + 48,
              img_h=origin_y + (W + H) * 8 + 36)
    s.sun = False
    cutaway_floor(s, 0, 0, W, H, floor_mat)
    wall_y(s, -0.4, W, 0.0, wh, paper=paper, wains=wains, wain_h=wain_h)
    wall_x(s, 0.0, H - 0.4, 0.0, wh, paper=paper, wains=wains, wain_h=wain_h)
    wall_stub_y(s, 0, door[0], H)
    wall_stub_y(s, door[1], W, H)
    wall_stub_x(s, 0, H, W)
    s.set_solid(W - 1, 0, W, H)
    s.set_solid(0, H - 1, door[0], H)
    s.set_solid(door[1], H - 1, W, H)
    s.occluder(-0.4, -0.4, W, 0.1, wh)
    s.occluder(-0.4, 0, 0.1, H, wh)
    mx0, mx1 = door[0] + 0.6, door[1] - 0.6
    s.box(mx0, H - 1.7, mx1, H, 0.0, 0.03, mat_cols[0], layer="floor")
    s.box(mx0 + 0.1, H - 1.6, mx1 - 0.1, H, 0.03, 0.036, mat_cols[1], layer="floor")
    s.box(mx0 + 0.25, H - 1.45, mx1 - 0.25, H, 0.036, 0.042, mat_cols[0], layer="floor")
    s.warp(mx0, H - 0.9, mx1, H, target, tx, ty, "down")
    return s


def counter(s, x0, y0, x1, y1, h, body, top, trim="trim_white", solid=True):
    s.box(x0, y0, x1, y1, 0, h, body)
    s.box(x0 - 0.05, y0 - 0.05, x1 + 0.05, y1 + 0.05, h, h + 0.05, top)
    s.box(x0, y1, x1, y1 + 0.02, 0.0, 0.1, trim)
    if solid:
        s.set_solid(x0, y0, x1 - 0.001, y1 - 0.001)
        s.occluder(x0, y0, x1, y1, h + 0.1)


def monitor_y(s, x, y, z, w=0.5, h=0.38, screen="tv_screen"):
    """Desktop monitor on a stand facing +y."""
    s.box(x - 0.08, y - 0.05, x + 0.08, y + 0.05, z, z + 0.03, "tv_body")
    s.box(x - 0.02, y - 0.02, x + 0.02, y + 0.02, z + 0.03, z + 0.12, "tv_body")
    s.box(x - w / 2, y - 0.04, x + w / 2, y + 0.04, z + 0.12, z + 0.12 + h, "tv_body")
    s.box(x - w / 2 + 0.03, y + 0.04, x + w / 2 - 0.03, y + 0.05, z + 0.15, z + 0.09 + h, screen)


def bookcase(s, x0, x1, y0, y1, h, levels, rnd):
    """Open bookcase against a wall, facing +y; books are random thin boxes."""
    s.box(x0, y0, x1, y0 + 0.08, 0, h, "wood")                         # back panel
    s.box(x0, y0, x0 + 0.07, y1, 0, h, "wood_dark")                    # sides
    s.box(x1 - 0.07, y0, x1, y1, 0, h, "wood_dark")
    s.box(x0, y0, x1, y1, h - 0.05, h, "wood_dark")                    # top
    s.box(x0, y0, x1, y1, 0, 0.1, "wood_dark")                         # plinth
    cols = ["book_a", "book_b", "book_c", "book_d", "book_e", "book_f"]
    step = (h - 0.15) / levels
    for lv in range(levels):
        zb = 0.1 + lv * step
        s.box(x0 + 0.07, y0 + 0.08, x1 - 0.07, y1, zb, zb + 0.03, "wood_dark")
        x = x0 + 0.12
        while x < x1 - 0.14:
            if rnd.random() < 0.06:
                x += rnd.uniform(0.1, 0.25)
                continue
            w = rnd.uniform(0.045, 0.1)
            hh = rnd.uniform(step * 0.55, step * 0.85)
            if x + w > x1 - 0.12:
                break
            s.box(x, y0 + 0.1, x + w, y1 - 0.05, zb + 0.03, zb + 0.03 + hh, rnd.choice(cols))
            x += w + 0.008
    s.set_solid(x0, y0, x1 - 0.001, y1 - 0.001)
    s.occluder(x0, y0, x1, y1, h + 0.1)


def fake_plant(s, x, y, r=0.3, pot="robot_white"):
    s.box(x - 0.26, y - 0.26, x + 0.26, y + 0.26, 0, 0.45, pot)
    s.box(x - 0.28, y - 0.28, x + 0.28, y + 0.28, 0.45, 0.5, "gold")
    s.sphere(x, y, 0.95, 0.4, "fake_leaf")
    s.cyl(x, y, 0.5, 0.8, 0.03, "steel")
    s.set_solid(x - 0.3, y - 0.3, x + 0.3, y + 0.3)
    s.occluder(x - 0.4, y - 0.4, x + 0.4, y + 0.4, 1.4)


def bench(s, x0, y0, x1, y1, seat="wood", legs="metal_dark", h=0.45):
    s.box(x0, y0, x1, y1, h - 0.07, h, seat)
    for (lx, ly) in ((x0 + 0.08, y0 + 0.08), (x1 - 0.14, y0 + 0.08), (x0 + 0.08, y1 - 0.14), (x1 - 0.14, y1 - 0.14)):
        s.box(lx, ly, lx + 0.06, ly + 0.06, 0, h - 0.07, legs)
    s.set_solid(x0, y0, x1 - 0.001, y1 - 0.001)
    s.occluder(x0, y0, x1, y1, h + 0.1)


# ------------------------------------------------------------------ bathhouse


# ------------------------------------------------------------------ diner
def diner():
    W, H = 11, 10
    s = std_room("diner", "Diner", W, H, "tile_bw", "wp_cream", "diner_red", 1.0, 3.2, (4, 7),
                 "city_centre", 53.0, 19.6, mat_cols=("diner_red", "rug_cream"))
    s.box(0.0, 0.0, W, 0.35, 0.0, 0.012, "diner_red", layer="floor")                 # red border strip at the back
    # kitchen pass-through (painted opening with a glowing kitchen behind)
    kx0, kx1 = 5.2, 8.6
    s.box(kx0, 0.0, kx1, 0.04, 0.95, 1.9, "wood_dark")
    s.box(kx0 + 0.15, 0.04, kx1 - 0.15, 0.07, 1.05, 1.8, "shop_light")
    s.box(kx0 + 0.05, 0.04, kx1 - 0.05, 0.3, 0.9, 0.97, "chrome")                      # ledge
    for i in range(5):                                                                    # order tickets on a rail
        s.box(kx0 + 0.45 + i * 0.55, 0.07, kx0 + 0.6 + i * 0.55, 0.09, 1.45, 1.75, "paper_cream")
    s.box(kx0 + 0.2, 0.06, kx1 - 0.2, 0.1, 1.82, 1.86, "chrome")
    for i in range(4):                                                                    # hanging pans silhouettes
        s.cyl(kx0 + 0.6 + i * 0.75, 0.12, 1.35, 1.38, 0.17, "metal_dark", axis="y", verts=16)
    s.box(kx0 + 0.6, 0.0, kx1 - 0.6, 0.06, 2.1, 2.7, "metal_dark")
    s.text("DINER", (kx0 + kx1) / 2, 0.09, 2.4, 0.5, "neon_red", face="left")
    s.box(kx0 - 0.2, 0.0, kx1 + 0.2, 0.05, 2.02, 2.06, "neon_blue")
    # back shelves with cups
    s.box(0.2, 0.05, 3.3, 0.6, 0, 1.25, "wood")
    for lz in (0.45, 0.85, 1.22):
        s.box(0.2, 0.05, 3.3, 0.6, lz, lz + 0.04, "wood_dark")
    for k in range(7):
        x = 0.5 + k * 0.42
        s.cyl(x, 0.35, 0.49, 0.62, 0.08, ("goods_white", "diner_teal", "diner_red", "goods_yellow")[k % 4], verts=10)
        s.cyl(x, 0.35, 0.89, 1.0, 0.08, ("diner_teal", "goods_white", "goods_yellow", "diner_red")[k % 4], verts=10)
    s.set_solid(0.2, 0.05, 3.299, 0.599)
    s.occluder(0.2, 0.05, 3.3, 0.6, 1.3)
    window_y(s, 0.7, 2.2, 0.0, 1.55, 2.55, curtain=True)
    s.box(3.5, 0.0, 5.0, 0.05, 1.5, 2.6, "chalk_menu")
    s.box(3.45, 0.0, 5.05, 0.04, 1.45, 1.5, "wood")
    s.text("MENU", 4.25, 0.07, 2.35, 0.2, "chalk", face="left")
    for i, ln in enumerate(("COFFEE $2", "PANCAKES $4", "BURGER $6")):
        s.text(ln, 4.25, 0.07, 2.05 - i * 0.2, 0.13, "chalk", face="left")
    wall_clock_y(s, 10.0, 0.0, 2.5, 0.28)
    # jukebox-like music box (own design): arched cabinet with glowing panel, speaker slats and lights
    jx0, jx1 = 9.1, 10.5
    jm = (jx0 + jx1) / 2
    s.box(jx0, 0.05, jx1, 0.85, 0, 1.15, "wood_red")
    s.cyl(jm, 0.45, 1.15, 0.8, 0.7, "wood_red", axis="y", verts=24)
    s.cyl(jm, 0.9, 1.15, 0.03, 0.55, "neon_gold", axis="y", verts=24)
    s.box(jx0 + 0.15, 0.85, jx1 - 0.15, 0.9, 0.12, 0.62, "metal_dark")
    for k in range(6):
        s.box(jx0 + 0.18, 0.9, jx1 - 0.18, 0.92, 0.16 + k * 0.075, 0.2 + k * 0.075, "chrome")
    s.box(jx0 + 0.1, 0.85, jx0 + 0.18, 0.9, 0.7, 1.1, "neon_blue")
    s.box(jx1 - 0.18, 0.85, jx1 - 0.1, 0.9, 0.7, 1.1, "neon_red")
    s.box(jm - 0.18, 0.85, jm + 0.18, 0.9, 0.7, 1.08, "tv_screen")
    s.box(jm - 0.25, 0.85, jm + 0.25, 0.92, 1.4, 1.5, "chrome")
    s.text("MUSIC", jm, 0.95, 1.45, 0.1, "metal_dark", face="left")
    s.set_solid(jx0, 0.05, jx1 - 0.001, 0.849)
    s.occluder(jx0, 0.05, jx1, 0.9, 1.9)
    # counter with pie case, coffee machine, register
    cx0, cx1 = 3.6, 8.8
    counter(s, cx0, 3.2, cx1, 4.1, 0.95, "diner_teal", "rug_cream", trim="chrome")
    s.box(cx0, 4.1, cx1, 4.15, 0.7, 0.78, "chrome")                                     # chrome foot rail band
    s.box(3.8, 3.3, 5.2, 3.95, 0.99, 1.04, "goods_white")                                # pie case
    s.box(3.85, 3.35, 5.15, 3.9, 1.04, 1.45, "glass_lid")
    for k in range(2):
        for j in range(3):
            if k == 1 and j == 2:
                continue
            px, py = 4.1 + k * 0.6, 3.5 + j * 0.2
            s.cyl(px, py, 1.045, 1.12, 0.12, "pie_crust", verts=12)
            s.cyl(px, py, 1.12, 1.15, 0.1, "pie_red" if (j + k) % 2 else "banana_yellow", verts=12)
    s.box(3.8, 3.3, 5.2, 3.35, 1.45, 1.5, "chrome")
    s.box(6.0, 3.3, 6.7, 3.8, 0.99, 1.15, "metal_dark")                                   # register
    s.box(6.05, 3.35, 6.65, 3.6, 1.15, 1.22, "screen")
    s.box(7.4, 3.3, 8.2, 3.85, 0.99, 1.45, "chrome")                                      # coffee machine
    s.box(7.45, 3.6, 8.15, 3.85, 1.0, 1.1, "tv_body")
    s.cyl(7.65, 3.6, 1.12, 1.4, 0.09, "glass_lid", verts=10)
    s.cyl(8.0, 3.6, 1.12, 1.4, 0.09, "glass_lid", verts=10)
    s.cyl(7.65, 3.6, 1.12, 1.25, 0.085, "coffee", verts=10)
    s.cyl(8.0, 3.6, 1.12, 1.25, 0.085, "coffee", verts=10)
    s.box(8.4, 3.55, 8.58, 3.7, 0.99, 1.1, "chrome")                                      # napkins
    s.cyl(5.7, 3.75, 0.99, 1.13, 0.1, "glass_lid", verts=12)
    for i in range(5):
        sx = 4.3 + i * 1.05
        s.cyl(sx, 4.85, 0.0, 0.55, 0.045, "chrome", verts=8)
        s.cyl(sx, 4.85, 0.55, 0.65, 0.2, "diner_red", verts=14)
        s.cyl(sx, 4.85, 0.0, 0.03, 0.14, "chrome", verts=10)
        s.set_solid(sx - 0.2, 4.65, sx + 0.2, 4.99)
    # booths along the west wall
    for i in range(2):
        y0 = 3.4 + i * 2.2
        y1 = y0 + 2.0
        s.box(0.1, y0, 0.75, y1, 0, 0.45, "diner_red")                                    # far bench (against wall)
        s.box(0.1, y0, 0.3, y1, 0.45, 1.1, "diner_red")
        s.box(0.1, y0 + 0.02, 0.32, y0 + 0.05, 0.6, 1.0, "diner_red")
        s.box(2.0, y0, 2.65, y1, 0, 0.45, "diner_red")                                    # near bench
        s.box(2.45, y0, 2.65, y1, 0.45, 0.95, "diner_red")
        s.box(0.95, y0 + 0.15, 1.85, y1 - 0.15, 0.7, 0.75, "goods_white")                 # table
        s.cyl(1.4, (y0 + y1) / 2, 0.0, 0.7, 0.07, "chrome", verts=8)
        s.box(1.15, y0 + 0.4, 1.3, y0 + 0.55, 0.75, 0.88, "goods_red")                    # ketchup & mustard
        s.box(1.35, y0 + 0.4, 1.5, y0 + 0.55, 0.75, 0.88, "goods_yellow")
        s.cyl(1.4, y1 - 0.5, 0.75, 0.83, 0.08, "goods_white", verts=10)
        s.set_solid(0.1, y0, 2.649, y1 - 0.001)
        s.occluder(0.1, y0, 2.65, y1, 1.1)
    window_x(s, 3.9, 5.5, 0.0, 1.4, 2.4, curtain=True)
    picture_x(s, 6.2, 7.2, 0.0, 1.5, 2.1, "poster_orange")
    picture_x(s, 7.8, 8.8, 0.0, 1.5, 2.1, "poster_yellow")
    # free table with chairs (south), a small one at the east wall
    for (tx, ty) in ((7.0, 7.6),):
        s.prop("house/Table_RoundSmall", tx, ty, h=0.66)
        s.prop("house/Chair_1", tx, ty - 1.3, rot=0, h=0.9, colours={"Wood": "#b8302c"})
        s.prop("house/Chair_1", tx, ty + 1.35, rot=180, h=0.9, colours={"Wood": "#b8302c"})
        s.box(tx - 0.2, ty - 0.2, tx - 0.05, ty - 0.05, 0.7, 0.8, "goods_red")
        s.box(tx + 0.05, ty - 0.2, tx + 0.2, ty - 0.05, 0.7, 0.8, "goods_yellow")
    potted_plant(s, 9.4, 6.6, "bay")
    for (lx, ly) in ((3, 5), (7, 5), (4, 8), (8, 8)):
        s.point_light(lx, ly, 2.8, 120, colour=(1.0, 0.9, 0.75))
    s.point_light(7.0, 1.2, 2.0, 80, colour=(1.0, 0.8, 0.5))
    return s


# ------------------------------------------------------------------ community centre
def community_centre():
    W, H = 18, 14
    s = std_room("community_centre", "Community centre", W, H, "floor_wood2", "wp_sage", "wood_dark", 0.95, 3.2,
                 (8, 11), "city_centre", 11.8, 19.6, mat_cols=("rug_navy", "rug_gold"))
    rnd = random.Random(8)
    rug(s, 5.0, 3.6, 15.0, 8.8, "carpet_blue", "rug_cream", "carpet_blue")                    # big reading-area rug
    rug(s, 0.5, 8.4, 5.9, 11.8, "rug_red", "rug_cream", "rug_green")                            # armchair nook rug
    # north wall: bookcases, notice board, computers
    bookcase(s, 0.9, 8.6, 0.05, 0.75, 2.2, 5, rnd)
    s.box(9.1, 0.0, 12.3, 0.05, 1.0, 2.5, "wood_dark")
    s.box(9.2, 0.05, 12.2, 0.09, 1.1, 2.4, "cork")
    fl = ["goods_red", "goods_yellow", "goods_blue", "goods_green", "goods_orange", "goods_pink", "goods_white"]
    for i in range(14):
        fx = 9.35 + (i % 7) * 0.4 + rnd.uniform(-0.03, 0.03)
        fz = 1.2 + (i // 7) * 0.65 + rnd.uniform(0, 0.1)
        fw, fh = rnd.uniform(0.22, 0.3), rnd.uniform(0.3, 0.5)
        s.box(fx, 0.09, fx + fw, 0.1, fz, fz + fh, fl[i % len(fl)])
        s.box(fx + fw / 2 - 0.02, 0.1, fx + fw / 2 + 0.02, 0.115, fz + fh - 0.06, fz + fh - 0.02, "tag_red")   # pin
    s.box(9.4, 0.0, 12.0, 0.08, 2.6, 3.0, "sign_blue")
    s.text("JOBS & NEWS", 10.7, 0.1, 2.8, 0.22, "sign_text", face="left")
    s.set_solid(9.1, 0.0, 12.299, 0.5)
    s.occluder(9.1, 0.0, 12.3, 0.3, 0.1)
    s.box(9.3, 0.3, 12.1, 0.8, 0, 0.8, "wood")                                                  # leaflet table under the board
    s.box(9.3, 0.3, 12.1, 0.8, 0.8, 0.84, "wood_dark")
    for i in range(4):
        s.box(9.5 + i * 0.65, 0.4, 10.0 + i * 0.65, 0.7, 0.84, 0.9, fl[i])
    s.set_solid(9.1, 0.0, 12.299, 0.8)
    s.occluder(9.1, 0.0, 12.3, 0.8, 0.9)
    # computer desk with 3 stations
    counter(s, 13.4, 0.05, 17.0, 0.9, 0.75, "wood", "wood_dark", solid=True)
    for i in range(3):
        cx = 14.2 + i * 1.2
        monitor_y(s, cx, 0.4, 0.8)
        s.box(cx - 0.2, 0.55, cx + 0.2, 0.75, 0.8, 0.83, "tv_body")                          # keyboard
        s.prop("house/OfficeChair", cx, 1.55, rot=180, h=0.9, solid=True)
    window_y(s, 14.0, 16.6, 0.0, 1.5, 2.6)
    # west wall: bookcase (swapped) + armchair nook
    sw = SwapProxy(s)
    bookcase(sw, 3.0, 7.6, 0.05, 0.75, 2.2, 5, rnd)
    wall_clock_x(s, 0.0, 9.6, 2.5, 0.26)
    s.prop("house/Couch_Small2", 1.3, 9.6, rot=90, scale=0.5)
    s.prop("house/Table_RoundSmall", 3.0, 9.6, h=0.45)
    s.prop("house/Couch_Small2", 4.7, 9.6, rot=270, scale=0.5)
    s.prop("house/Light_Floor1", 0.6, 11.4, h=1.6)
    window_x(s, 11.0, 12.6, 0.0, 1.5, 2.5, curtain=True)
    # reading tables with chairs
    for tx in (5.3, 11.3):
        s.box(tx, 5.0, tx + 3.0, 6.4, 0.7, 0.76, "wood")
        for lx, ly in ((tx + 0.1, 5.1), (tx + 2.8, 5.1), (tx + 0.1, 6.2), (tx + 2.8, 6.2)):
            s.box(lx, ly, lx + 0.1, ly + 0.1, 0, 0.7, "wood_dark")
        s.box(tx + 1.2, 5.4, tx + 1.8, 6.0, 0.76, 0.8, "rug_green")                          # table lamp / book pile
        s.box(tx + 0.3, 5.3, tx + 0.7, 5.6, 0.76, 0.82, "book_a")
        s.box(tx + 2.2, 5.6, tx + 2.55, 5.9, 0.76, 0.81, "book_d")
        s.set_solid(tx, 5.0, tx + 2.999, 6.399)
        s.occluder(tx, 5.0, tx + 3.0, 6.4, 0.85)
        for cx in (tx + 0.8, tx + 2.0):
            s.prop("house/Chair_1", cx, 4.35, rot=0, h=0.9)
            s.prop("house/Chair_1", cx, 7.1, rot=180, h=0.9)
    # help desk near the entrance
    counter(s, 12.0, 10.2, 16.99, 11.0, 0.95, "wood_blue", "wood_dark")
    monitor_y(s, 13.3, 10.5, 1.0)
    s.box(14.4, 10.4, 14.8, 10.7, 1.0, 1.06, "brass")
    s.box(15.4, 10.35, 16.1, 10.8, 1.0, 1.12, "paper_cream")
    s.box(12.2, 11.0, 16.8, 11.03, 0.45, 0.8, "sign_blue")
    s.text("HELP DESK", 14.5, 11.05, 0.62, 0.2, "sign_text", face="left")
    s.prop("house/OfficeChair", 13.5, 9.2, rot=0, h=0.9)
    potted_plant(s, 6.6, 12.4, "bay")
    potted_plant(s, 0.6, 12.4, "flowers")
    for (lx, ly) in ((3, 3), (9, 3), (14, 3), (3, 9), (9, 8), (15, 8)):
        s.point_light(lx, ly, 2.9, 130, colour=(1.0, 0.92, 0.78))
    return s


# ------------------------------------------------------------------ VaultTech lobby (cold)
def vaulttech_lobby():
    W, H = 18, 16
    s = std_room("vaulttech_lobby", "VaultTech lobby", W, H, "marble", "wall_panel_cold", "gold", 0.18, 3.9, (7, 11),
                 "city_centre", 63.0, 15.0, origin_y=116, mat_cols=("metal_dark", "gold"))
    s.world = (0.7, 0.8, 1.0)
    s.world_strength = 0.6
    s.fill = (0.82, 0.9, 1.0)
    s.fill_energy = 1.8
    # gold floor inlays: ring and a V
    s.cyl(6.2, 9.0, 0.0, 0.012, 2.3, "gold", layer="floor", verts=48)
    s.cyl(6.2, 9.0, 0.012, 0.02, 2.15, "marble", layer="floor", verts=48)
    s.poly([(4.9, 7.8, 0.03), (5.5, 7.8, 0.03), (6.5, 10.3, 0.03), (6.0, 10.3, 0.03)], "gold", layer="floor")
    s.poly([(7.5, 7.8, 0.03), (6.9, 7.8, 0.03), (6.0, 10.3, 0.03), (6.5, 10.3, 0.03)], "gold", layer="floor")
    s.box(0.0, 3.0, 18.0, 3.06, 0.0, 0.01, "gold", layer="floor")                      # gold line across the lobby
    # logo wall behind reception
    s.box(4.8, 0.0, 13.2, 0.12, 0.35, 3.45, "gold")
    s.box(4.95, 0.12, 13.05, 0.16, 0.5, 3.3, "metal_dark")
    for fx in (5.2, 6.6, 8.0, 9.4, 10.8, 12.2):
        s.box(fx, 0.16, fx + 0.12, 0.26, 0.5, 3.3, "gold_dark")
    s.text("VAULTTECH", 9.0, 0.3, 2.25, 0.95, "neon_gold", face="left", extrude=0.03)
    s.text("SMART CITY", 9.0, 0.3, 1.25, 0.32, "robot_white", face="left")
    s.box(8.0, 0.16, 10.0, 0.22, 1.7, 1.78, "neon_gold")
    # elevators (closed)
    s.box(13.6, 0.0, 17.2, 0.1, 0.0, 3.1, "gold")
    for i, ex in enumerate((13.9, 15.55)):
        s.box(ex, 0.1, ex + 1.5, 0.2, 0.05, 2.7, "steel")
        s.box(ex + 0.73, 0.2, ex + 0.77, 0.24, 0.05, 2.7, "metal_dark")
    s.box(14.2, 0.1, 16.9, 0.25, 2.8, 3.0, "metal_dark")
    s.text("L   1   2   3", 15.5, 0.27, 2.9, 0.14, "neon_red", face="left")
    s.box(13.65, 0.1, 13.85, 0.2, 1.0, 1.4, "metal_dark")
    s.box(13.68, 0.2, 13.82, 0.22, 1.15, 1.22, "neon_red")
    s.box(13.68, 0.2, 13.82, 0.22, 1.25, 1.3, "neon_blue")
    s.box(14.5, 0.25, 16.5, 0.28, 1.9, 2.3, "metal_dark")
    s.text("OUT OF SERVICE", 15.5, 0.3, 2.1, 0.12, "neon_red", face="left")
    s.set_solid(13.6, 0.0, 17.2, 0.5)
    # self-service terminals
    for i in range(3):
        tx = 1.0 + i * 1.3
        s.box(tx, 0.15, tx + 0.8, 0.75, 0.0, 0.9, "steel")
        s.box(tx - 0.02, 0.1, tx + 0.82, 0.8, 0.9, 1.0, "gold")
        s.box(tx + 0.1, 0.25, tx + 0.7, 0.65, 1.0, 1.6, "tv_body")
        s.box(tx + 0.14, 0.65, tx + 0.66, 0.67, 1.1, 1.55, "tv_screen")
        s.box(tx + 0.2, 0.65, tx + 0.6, 0.69, 0.75, 0.82, "neon_blue")
        s.set_solid(tx, 0.15, tx + 0.8 - 0.001, 0.75)
        s.occluder(tx, 0.1, tx + 0.8, 0.8, 1.7)
    # reception desk and robot receptionist
    counter(s, 5.5, 4.2, 12.5, 5.1, 1.0, "robot_white", "gold", trim="gold")
    s.box(5.5, 5.1, 12.5, 5.13, 0.1, 0.9, "marble")
    s.box(5.6, 5.13, 12.4, 5.16, 0.45, 0.5, "gold")
    s.text("WELCOME TO VAULTTECH", 9.0, 5.19, 0.7, 0.22, "metal_dark", face="left")
    monitor_y(s, 6.8, 4.5, 1.05, 0.55, 0.4, "neon_blue")
    monitor_y(s, 11.2, 4.5, 1.05, 0.55, 0.4, "neon_blue")
    s.box(8.2, 4.9, 9.8, 4.94, 1.05, 1.6, "glass_pane")
    # robot (stand-in): plinth, torso, shoulders, arms, head with visor, antenna
    rx, ry = 9.0, 3.2
    s.cyl(rx, ry, 0.0, 0.12, 0.5, "gold", verts=24)
    s.cyl(rx, ry, 0.12, 0.2, 0.4, "robot_white", verts=24)
    s.cyl(rx, ry, 0.2, 0.9, 0.26, "robot_white", verts=20, r2=0.32)
    s.cyl(rx, ry, 0.45, 0.5, 0.33, "robot_eye", verts=20)
    s.sphere(rx, ry, 1.0, 0.36, "robot_white", sz=0.55)
    s.sphere(rx - 0.28, ry + 0.02, 0.98, 0.1, "chrome")
    s.sphere(rx + 0.28, ry + 0.02, 0.98, 0.1, "chrome")
    s.tube([(rx - 0.3, ry, 0.95), (rx - 0.45, ry + 0.35, 0.8), (rx - 0.5, ry + 0.8, 1.1)], 0.045, "chrome")
    s.tube([(rx + 0.3, ry, 0.95), (rx + 0.45, ry + 0.35, 0.8), (rx + 0.5, ry + 0.8, 1.1)], 0.045, "chrome")
    s.sphere(rx, ry, 1.28, 0.2, "robot_white")
    s.box(rx - 0.16, ry + 0.12, rx + 0.16, ry + 0.2, 1.22, 1.34, "robot_eye")
    s.cyl(rx, ry, 1.45, 1.62, 0.015, "chrome", verts=6)
    s.sphere(rx, ry, 1.64, 0.04, "robot_eye")
    s.set_solid(rx - 0.4, ry - 0.4, rx + 0.4, ry + 0.4)
    s.occluder(rx - 0.5, ry - 0.5, rx + 0.5, ry + 0.5, 1.7)
    # glass wall (west) with benches and plants
    for (y0, y1) in ((1.8, 5.3), (5.7, 9.2), (9.6, 13.1)):
        s.box(0.0, y0 - 0.1, 0.1, y1 + 0.1, 0.2, 3.5, "gold_dark")
        s.box(0.02, y0, 0.12, y1, 0.3, 3.4, "glass_office")
        s.box(0.0, (y0 + y1) / 2 - 0.03, 0.15, (y0 + y1) / 2 + 0.03, 0.3, 3.4, "gold_dark")
    for (y0, y1) in ((3.0, 4.9), (7.0, 8.9)):
        bench(s, 0.25, y0, 0.95, y1, seat="robot_white", legs="gold", h=0.45)
    fake_plant(s, 0.7, 5.8)
    fake_plant(s, 0.6, 0.6)
    fake_plant(s, 0.6, 14.4)
    # waiting area east
    s.box(15.2, 8.2, 16.8, 11.3, 0, 0.42, "robot_white")
    s.box(16.4, 8.2, 16.8, 11.3, 0.42, 0.95, "robot_white")
    s.box(15.0, 8.2, 15.2, 11.3, 0, 0.3, "gold")
    s.set_solid(15.0, 8.2, 16.999, 11.299)
    s.occluder(15.0, 8.2, 17.0, 11.3, 1.0)
    s.box(10.0, 8.2, 10.8, 11.3, 0, 0.42, "robot_white")
    s.box(10.0, 8.2, 10.3, 11.3, 0.42, 0.95, "robot_white")
    s.box(10.8, 8.2, 10.88, 11.3, 0, 0.3, "gold")
    s.set_solid(10.0, 8.2, 10.879, 11.299)
    s.occluder(10.0, 8.2, 10.9, 11.3, 1.0)
    s.box(11.8, 8.9, 12.9, 10.5, 0.38, 0.42, "glass_pane")
    for (lx, ly) in ((11.9, 9.0), (12.8, 9.0), (11.9, 10.4), (12.8, 10.4)):
        s.box(lx - 0.03, ly - 0.03, lx + 0.03, ly + 0.03, 0.0, 0.38, "chrome")
    s.set_solid(11.8, 8.9, 12.899, 10.499)
    fake_plant(s, 16.4, 14.4)
    fake_plant(s, 11.4, 14.4)
    for (lx, ly) in ((3, 4), (9, 6), (14, 4), (4, 11), (10, 12), (15, 12)):
        s.point_light(lx, ly, 3.4, 190, colour=(0.82, 0.92, 1.0))
    s.point_light(9, 1.2, 2.8, 120, colour=(1.0, 0.85, 0.5))
    return s


def home_room():
    """First cheap rented room: shabby, nearly empty (furniture is bought later)."""
    W, H = 10, 12
    SY = 4.0
    s = Scene("home_room", "Rented room", W, H, origin_x=H * 16 + 24, origin_y=64,
              img_w=(W + H) * 16 + 48, img_h=64 + (W + H) * 8 + 36)
    s.sun = False
    WH = 2.9
    rnd = random.Random(21)
    cutaway_floor(s, 0, SY, W, H, "floor_bare")
    cutaway_floor(s, 5, 0, W, SY, "tile_floor_dirty")
    # stains and worn patches on the boards
    for (sx, sy, r) in ((2.6, 7.4, 0.7), (5.8, 9.0, 0.55), (7.5, 5.8, 0.4), (3.9, 5.4, 0.35)):
        s.cyl(sx, sy, 0.0, 0.004, r, "stain", layer="floor", verts=14)
    # cracked tiles in the bathroom: dark zig-zag cracks + a missing tile
    for (x0, y0, x1, y1) in ((6.0, 1.9, 6.45, 2.0), (6.45, 1.9, 6.5, 2.4), (6.5, 2.4, 7.1, 2.45), (7.1, 2.45, 7.15, 2.9),
                              (7.0, 0.9, 7.35, 0.94), (7.35, 0.9, 7.4, 1.3), (8.1, 1.6, 8.6, 1.65), (8.6, 1.65, 8.65, 2.2)):
        s.box(x0, y0, x1, y1, 0.0, 0.006, "metal_dark", layer="floor")
    s.box(7.5, 2.2, 7.9, 2.6, 0.0, 0.004, "stain", layer="floor")
    # walls: peeling wallpaper over bare plaster, chipped skirting
    wall_y(s, -0.4, 4.6, SY, WH, paper="wp_shabby", wains="plaster_bare", wain_h=0.8, trim="wood_dark")
    wall_x(s, SY, H - 0.4, 0.0, WH, paper="wp_shabby", wains="plaster_bare", wain_h=0.8, trim="wood_dark")
    wall_x(s, 0.0, SY, 5.0, WH, paper="wp_shabby_blue", wains="tile_dirty", wain_h=1.2, trim="wood_dark")
    wall_y(s, 4.6, W, 0.0, WH, paper="wp_shabby_blue", wains="tile_dirty", wain_h=1.2, trim="wood_dark")
    wall_stub_y(s, 0, 3.0, H, mat="wp_shabby")
    wall_stub_y(s, 6.0, W, H, mat="wp_shabby")
    wall_stub_x(s, 0, H, W, mat="wp_shabby")
    wall_stub_y(s, 5.0, 6.0, SY, mat="wp_shabby_blue")
    wall_stub_y(s, 8.0, W - 0.4, SY, mat="wp_shabby_blue")
    s.set_solid(0, 0, 5, SY - 0.001)
    s.set_solid(5, 3, 6, 4)
    s.set_solid(8, 3, W, 4)
    s.set_solid(W - 1, 0, W, H)
    s.set_solid(0, H - 1, 3, H)
    s.set_solid(6, H - 1, W, H)
    s.occluder(-0.4, SY - 0.4, 4.6, SY + 0.1, WH)
    s.occluder(-0.4, SY, 0.1, H, WH)
    # peeling wallpaper: curling strips, bare patches, water stains, damp
    for (x0, x1, z0, z1) in ((0.6, 0.95, 1.0, 2.3), (2.9, 3.2, 1.7, 2.7), (3.4, 4.2, 0.9, 1.5)):
        s.box(x0, SY, x1, SY + 0.012, z0, z1, "plaster_bare")
        s.box(x0 - 0.04, SY + 0.012, x0 + 0.08, SY + 0.07, z1 - 0.35, z1, "wp_shabby")      # the curl
    for (y0, y1, z0, z1) in ((5.2, 5.7, 1.2, 2.4), (8.3, 9.2, 1.6, 2.6)):
        s.box(0.0, y0, 0.012, y1, z0, z1, "plaster_bare")
        s.box(0.012, y0 - 0.02, 0.07, y0 + 0.1, z1 - 0.4, z1, "wp_shabby")
    s.box(1.8, SY, 2.9, SY + 0.01, 2.0, 2.85, "stain")
    s.box(0.0, 6.3, 0.01, 7.4, 2.3, 2.85, "stain")
    # small window (bare, with a torn blind)
    window_y(s, 3.3, 4.2, SY, 1.35, 2.15)
    s.box(3.3, SY, 3.9, SY + 0.12, 1.85, 2.2, "paper_cream")
    s.box(3.3, SY, 3.5, SY + 0.12, 1.55, 1.85, "paper_cream")
    # bare bulb on a cord
    s.tube([(2.6, SY + 0.06, 2.75), (2.6, SY + 0.5, 2.8), (2.6, SY + 0.9, 2.55)], 0.012, "cord_black")
    s.sphere(2.6, SY + 0.9, 2.42, 0.09, "bulb", sz=1.2)
    s.cyl(2.6, SY + 0.9, 2.5, 2.6, 0.04, "metal_dark")
    # fridge (tiny, old) + crate with hot plate + sink on the north wall
    s.prop("house/Kitchen_Fridge", 0.85, SY + 0.6, rot=0, h=1.0, colours={"White": "#d6cea0"})
    s.box(1.5, SY + 0.1, 2.3, SY + 0.7, 0, 0.6, "crate")
    s.box(1.55, SY + 0.15, 2.25, SY + 0.65, 0.6, 0.66, "wood_dark")
    s.box(1.65, SY + 0.2, 2.15, SY + 0.6, 0.66, 0.72, "hotplate")
    s.cyl(1.82, SY + 0.4, 0.72, 0.735, 0.1, "coil_hot", verts=14)
    s.cyl(2.0, SY + 0.4, 0.72, 0.735, 0.08, "coil_hot", verts=14)
    s.cyl(1.9, SY + 0.55, 0.735, 0.85, 0.055, "metal_light", verts=10)                        # a dented kettle/pot
    s.set_solid(1.5, SY + 0.1, 2.299, SY + 0.699)
    s.occluder(1.5, SY + 0.1, 2.3, SY + 0.7, 0.8)
    s.prop("house/Bathroom_Sink", 3.75, SY + 0.5, scale=0.48, colours={"White": "#cfc8b4"})
    s.box(3.65, SY + 0.04, 3.7, SY + 0.09, 0.7, 1.2, "rust")                                  # pipe
    s.prop("house/Trashcan_Cylindric", 4.45, SY + 0.35, h=0.5, solid=False, occlude=False)
    # mattress on the floor, one old chair, a crate used as bedside
    s.box(0.2, 5.1, 1.55, 7.9, 0.0, 0.16, "mattress")
    s.box(0.2, 5.1, 1.55, 5.5, 0.16, 0.2, "paper_cream")                                     # flat pillow
    s.box(0.3, 5.9, 1.45, 7.6, 0.16, 0.24, "blanket_old")                                    # crumpled blanket
    s.box(0.5, 6.3, 1.3, 6.7, 0.24, 0.28, "blanket_old")
    s.set_solid(0.2, 5.1, 1.549, 7.899)
    s.occluder(0.2, 5.1, 1.55, 7.9, 0.3)
    s.box(0.25, 8.3, 0.85, 8.9, 0.0, 0.45, "crate")
    s.cyl(0.55, 8.6, 0.45, 0.62, 0.05, "metal_dark", verts=8)                                 # candle stub / bottle
    s.set_solid(0.25, 8.3, 0.849, 8.899)
    s.occluder(0.25, 8.3, 0.85, 8.9, 0.7)
    s.prop("house/Chair_1", 4.6, 7.3, rot=240 if False else 270, h=0.85, colours={"Wood": "#6a5038"})
    # a few cardboard boxes by the door and a bag
    cardboard_box(s, 7.6, 9.6, 0.9, 0.8, 0.5)
    cardboard_box(s, 7.7, 9.65, 0.7, 0.6, 0.4, z=0.5)
    cardboard_box(s, 6.8, 10.0, 0.6, 0.55, 0.35)
    s.set_solid(7.6, 9.6, 8.499, 10.399)
    s.set_solid(6.8, 10.0, 7.399, 10.549)
    s.occluder(6.8, 9.6, 8.5, 10.5, 1.0)
    # bathroom: toilet, small shower, sink
    s.prop("house/Bathroom_Shower1", 5.75, 0.85, rot=0, h=1.55, colours={"Couch_Blue": "#7a8a8a"})
    s.prop("house/Bathroom_Toilet", 8.0, 0.5, rot=0, scale=0.42, colours={"White": "#d8d4c4"})
    s.prop("house/Bathroom_Sink", 5.45, 2.5, rot=90, scale=0.45, colours={"White": "#cfc8b4"})
    s.box(5.1, 1.9, 5.16, 3.1, 1.15, 1.9, "plaster_bare")                                       # mirror gone: bare patch
    s.box(8.4, 0.05, 8.5, 0.12, 0.9, 1.5, "rust")                                              # pipe
    # lights (single warm bulb feel) and exit
    s.point_light(2.6, SY + 0.9, 2.4, 200, colour=(1.0, 0.8, 0.5), radius=0.1)
    s.point_light(7.0, 1.5, 2.2, 60, colour=(0.9, 0.95, 1.0))
    s.point_light(4.0, 9.0, 2.4, 45, colour=(1.0, 0.85, 0.6))
    # worn door mat
    s.box(3.5, 10.4, 5.5, 12.0, 0.0, 0.02, "mat_red", layer="floor")
    s.box(3.6, 10.5, 5.4, 12.0, 0.02, 0.025, "stain", layer="floor")
    s.warp(3.5, 11.0, 5.5, H, "city_centre", 44.0, 19.0, "down")
    return s

def public_toilet():
    """Tiny park toilet: one open WC (half wall), one sink with a mirror, paper towels, a bin; a bit grimy."""
    W, H = 6, 6
    s = std_room("public_toilet", "Public toilet", W, H, "tile_floor_dirty", "plaster_bare", "tile_dirty", 1.7, 3.0, (2, 5),
                 "city_centre", 3.0, 40.9, mat_cols=("metal_dark", "stain"))
    # open WC stall: half wall on the right, toilet against the back wall
    s.box(2.15, 0.0, 2.25, 1.95, 0.2, 1.15, "stall_panel")
    s.box(2.15, 0.0, 2.25, 1.95, 1.15, 1.2, "chrome")
    s.set_solid(2.1, 0.0, 2.299, 1.95)
    s.occluder(2.1, 0.0, 2.3, 1.95, 1.2)
    s.prop("house/Bathroom_Toilet", 1.2, 0.47, scale=0.44, colours={"White": "#d8d4c4"})
    s.tube([(0.1, 0.5, 0.8), (0.1, 1.4, 0.8)], 0.025, "chrome")                      # grab rail
    # sink with mirror, paper towels and a bin on the west wall
    s.prop("house/Bathroom_Sink", 0.5, 3.4, rot=90, scale=0.5, colours={"White": "#cfc8b4"})
    s.prop("house/Bathroom_Mirror1", 0.1, 3.4, rot=90, scale=0.7, z=1.3, solid=False, occlude=False)
    s.box(0.05, 4.1, 0.35, 4.5, 1.0, 1.6, "robot_white")                              # paper towel dispenser
    s.box(0.35, 4.15, 0.4, 4.45, 1.2, 1.3, "metal_dark")
    s.set_solid(0.0, 4.0, 0.399, 4.6)
    s.cyl(0.95, 4.65, 0.0, 0.7, 0.25, "bin_green", verts=12)                           # litter bin
    s.cyl(0.95, 4.65, 0.7, 0.74, 0.27, "metal_dark", verts=12)
    s.set_solid(0.7, 4.4, 1.199, 4.899)
    s.occluder(0.0, 3.0, 0.7, 4.6, 1.7)
    # signs and window on the back wall
    s.box(0.5, 0.0, 2.0, 0.06, 2.25, 2.85, "sign_blue")
    s.text("WC", 1.25, 0.09, 2.55, 0.5, "robot_white", face="left")
    window_y(s, 3.4, 4.8, 0.0, 1.7, 2.6)
    for bx in (3.75, 4.1, 4.45):
        s.box(bx - 0.015, 0.0, bx + 0.015, 0.12, 1.7, 2.6, "metal_dark")
    # grime: stained wall streaks, a cracked floor tile (no puddles)
    for (gx, gz0, gz1) in ((2.7, 0.15, 1.4), (3.05, 0.15, 0.7), (5.2, 0.15, 1.1), (1.6, 1.1, 1.65)):
        s.box(gx, 0.0, gx + 0.1, 0.045, gz0, gz1, "stain")
    for (sy0, sy1, z) in ((2.0, 2.35, 1.2), (3.2, 3.55, 0.9)):
        s.box(0.0, sy0, 0.045, sy1, z - 0.9, z + 0.3, "stain")
    for (x0, y0, x1, y1) in ((3.6, 2.9, 3.8, 2.93), (3.78, 2.9, 3.81, 3.1), (3.6, 3.08, 3.8, 3.11),
                             (3.45, 3.0, 3.6, 3.03), (3.8, 3.1, 4.0, 3.13)):
        s.box(x0, y0, x1, y1, 0.0, 0.008, "metal_dark", layer="floor")
    s.point_light(2.5, 2.5, 2.6, 85, colour=(0.9, 0.98, 1.0))
    s.point_light(4.5, 4.0, 2.6, 60, colour=(0.9, 0.98, 1.0))
    return s


SCENES = [city_centre, market_v2, diner, community_centre, vaulttech_lobby, public_toilet]
