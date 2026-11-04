"""
Town Life - the FURNITURE CATALOG (owner rule): every piece of furniture in a place where you live (also temporarily) must later be
buyable in a furniture store or online; some furniture in commercial buildings is for sale too. So furniture is not drawn ad hoc inside
scenes: each piece is a named catalog entry with a builder, and scenes call place(). A future shop / home editor lists FURNITURE
(id, display name, price, category), checks `size`, and places the same builder at the owner's chosen spot.

Entry fields
  name       display name in the shop
  price      placeholder price in $ (final economy numbers come with the shop)
  category   bed, storage, desk, seating, lighting, decor, rug, plant, bathroom, kitchen
  size       footprint (w, d) in cells, rot 0 (w along the wall, d out from the wall)
  kind       interaction kind of tools/interactions.py (bed, wardrobe, desk, window, bookshelf, seat, toilet, sink, bin ...) or None
  quality    1..3: speed / strength of what it does (bed = Energy per hour, bookshelf = Fun, toilet = speed)
  use        (a, b, extra_reach) interaction point in the piece's local frame (cells), for interactions.py / use_point()
  build      builder(s, ...) drawing the piece in its LOCAL frame (rot 0 = back against the -y wall, front towards +y, origin at the
             top-left corner of the footprint). place() rotates it: rot 0 back wall (-y), 90 west wall (front faces +x),
             180 faces -y, 270 east wall (front faces -x).  anchor "centre" pieces (chairs, plants) are placed by their centre.
  native     True: the builder is an older helper that draws in WORLD coordinates (no rotation); place() just calls it.

Use: place(s, "bed_cosy", x, y, rot=0)   (x, y = top-left corner of the rotated footprint, cells; or the centre for anchor "centre")
"""
import scene as scn

# ------------------------------------------------------------------------------------------------------------------------------
# local-frame proxy
# ------------------------------------------------------------------------------------------------------------------------------


class Local:
    """Wraps a Scene: coordinates given to it are in the piece's local frame (a = along the wall, b = out from the wall)."""

    def __init__(self, s, x, y, w, d, rot):
        self.s, self.x, self.y, self.w, self.d, self.rot = s, x, y, w, d, rot % 360

    def pt(self, a, b):
        r = self.rot
        if r == 0:
            return self.x + a, self.y + b
        if r == 90:
            return self.x + b, self.y + self.w - a
        if r == 180:
            return self.x + self.w - a, self.y + self.d - b
        return self.x + self.d - b, self.y + a       # 270

    def rect(self, a0, b0, a1, b1):
        p, q = self.pt(a0, b0), self.pt(a1, b1)
        return min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1])

    def box(self, a0, b0, a1, b1, z0, z1, mat, layer="objects", bevel=0.0):
        x0, y0, x1, y1 = self.rect(a0, b0, a1, b1)
        self.s.box(x0, y0, x1, y1, z0, z1, mat, layer=layer, bevel=bevel)

    def cyl(self, a, b, z0, z1, r, mat, layer="objects", verts=16, r2=None):
        x, y = self.pt(a, b)
        self.s.cyl(x, y, z0, z1, r, mat, layer=layer, verts=verts, r2=r2)

    def sphere(self, a, b, z, r, mat, layer="objects", sz=1.0, sx=1.0, sy=1.0):
        x, y = self.pt(a, b)
        if self.rot in (90, 270):
            sx, sy = sy, sx
        self.s.sphere(x, y, z, r, mat, layer=layer, sz=sz, sx=sx, sy=sy)

    def tube(self, pts, r, mat, layer="objects"):
        self.s.tube([(*self.pt(p[0], p[1]), p[2]) for p in pts], r, mat, layer=layer)

    def point_light(self, a, b, z, energy, colour=(1.0, 0.85, 0.6), radius=0.3):
        x, y = self.pt(a, b)
        self.s.point_light(x, y, z, energy, colour=colour, radius=radius)

    def set_solid(self, a0, b0, a1, b1, value=True):
        self.s.set_solid(*self.rect(a0, b0, a1, b1), value=value)

    def occluder(self, a0, b0, a1, b1, h):
        self.s.occluder(*self.rect(a0, b0, a1, b1), h)

    def prop(self, name, a, b, rot=0, **k):
        x, y = self.pt(a, b)
        return self.s.prop(name, x, y, rot=(rot - self.rot) % 360, **k)


# ------------------------------------------------------------------------------------------------------------------------------
# builders (local frames)
# ------------------------------------------------------------------------------------------------------------------------------
def _bed_cosy(s):
    """Calm bed, long axis along the wall, headboard at the west end: oak frame with a tall panelled headboard, cream mattress, ONE
    dusty-blue duvet with a turned-back cream sheet, ONE soft round pillow, no footboard (the sleeper lies on top)."""
    x0, y0, length, width = 0.15, 0.05, 2.95, 1.45
    x1, y1 = x0 + length, y0 + width
    s.box(x0, y0, x1, y1, 0.1, 0.4, "wood")
    s.box(x0 - 0.12, y0 - 0.02, x0 + 0.05, y1 + 0.02, 0.1, 1.2, "wood_dark")
    s.box(x0 - 0.04, y0 + 0.1, x0 + 0.06, y1 - 0.1, 0.5, 1.08, "wood")
    s.box(x0 - 0.15, y0 - 0.05, x0 + 0.08, y1 + 0.05, 1.2, 1.28, "wood")
    # rounded, soft: bevelled mattress, puffy duvet hanging a little over the sides, turned-back sheet, round pillow
    # (no footboard, no foot blanket: the sleeper lies on top of the duvet, legs towards the foot end)
    s.box(x0 + 0.06, y0 + 0.02, x1 - 0.02, y1 - 0.02, 0.4, 0.55, "pillow_white", bevel=0.06)
    s.box(x0 + 0.95, y0 - 0.07, x1 - 0.06, y1 + 0.07, 0.43, 0.68, "duvet_blue", bevel=0.1)
    s.box(x0 + 0.78, y0 - 0.03, x0 + 1.12, y1 + 0.03, 0.5, 0.72, "pillow_white", bevel=0.06)
    s.sphere(x0 + 0.4, (y0 + y1) / 2, 0.6, 0.3, "pillow_white", sz=0.3, sx=0.67, sy=1.0)
    s.set_solid(x0 - 0.12, y0 - 0.02, x1 - 0.001, y1 - 0.001)
    s.occluder(x0 - 0.12, y0 - 0.02, x1, y1, 1.3)


def _bedside_lamp(s):
    s.box(0.0, 0.0, 0.48, 0.5, 0, 0.5, "wood")
    s.cyl(0.24, 0.25, 0.5, 0.58, 0.09, "brass")
    s.cyl(0.24, 0.25, 0.58, 0.95, 0.15, "lamp_shade", r2=0.1)
    s.set_solid(0.0, 0.0, 0.479, 0.499)
    s.point_light(0.24, 0.25, 0.9, 50, colour=(1.0, 0.78, 0.45), radius=0.12)


def _wardrobe_two_door(s):
    """Two-door oak wardrobe with a cornice, brass handles; opens towards the room."""
    x0, x1, wh = 0.0, 1.7, 2.2
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


def _desk_laptop(s):
    """Desk against a wall (long side along the wall, user sits in front): top, two slab legs, a drawer, laptop, lamp, mug.
    Lamp at the low-a end, laptop at the high-a end."""
    def B(b0, a0, b1, a1, z0, z1, mat):          # boxes written depth-first (b = out from the wall, a = along the wall)
        s.box(a0, b0, a1, b1, z0, z1, mat)
    B(0.0, 0.0, 0.72, 1.7, 0.7, 0.76, "wood")
    for (a0, a1) in ((0.0, 0.1), (1.6, 1.7)):
        B(0.04, a0, 0.68, a1, 0.0, 0.7, "wood_dark")
    B(0.12, 0.1, 0.6, 1.6, 0.5, 0.7, "wood_dark")
    B(0.72, 0.8, 0.74, 1.4, 0.52, 0.66, "wood")
    B(0.74, 1.05, 0.77, 1.15, 0.57, 0.6, "brass")
    B(0.2, 0.96, 0.58, 1.48, 0.76, 0.8, "metal_light")
    B(0.2, 0.96, 0.24, 1.48, 0.8, 1.08, "metal_dark")
    B(0.24, 1.01, 0.25, 1.43, 0.84, 1.04, "tv_screen")
    s.cyl(0.22, 0.3, 0.76, 0.82, 0.12, "brass")
    s.cyl(0.22, 0.3, 0.82, 1.2, 0.025, "brass")
    s.cyl(0.22, 0.3, 1.05, 1.35, 0.17, "lamp_shade", r2=0.1)
    s.point_light(0.22, 0.3, 1.3, 60, colour=(1.0, 0.8, 0.5), radius=0.12)
    s.cyl(0.8, 0.55, 0.76, 0.9, 0.06, "pot")
    s.set_solid(0.0, 0.0, 1.699, 0.719)
    s.occluder(0.0, 0.0, 1.7, 0.72, 1.0)


def _chair_wood(s):
    """Plain wooden chair (Quaternius CC0 Chair_1) facing the wall (-b). Centre anchored."""
    s.prop("house/Chair_1", 0.3, 0.3, rot=0, h=0.9, colours={"Wood": "#9a6a3a"}, solid=True)


def _window_seat(s):
    """Window seat: oak box with ONE long mustard cushion and ONE teal pillow."""
    s.box(0.0, 0.0, 3.6, 0.73, 0.0, 0.42, "wood")
    s.box(0.0, 0.73, 3.6, 0.77, 0.05, 0.38, "wood_dark")
    s.box(0.07, 0.05, 3.53, 0.71, 0.42, 0.54, "blanket_mustard")
    s.box(0.25, 0.11, 0.87, 0.53, 0.54, 0.7, "rug_teal")
    s.set_solid(0.0, 0.0, 3.599, 0.73)
    s.occluder(0.0, 0.0, 3.6, 0.73, 0.6)


def _wall_shelf_radio(s):
    """Wall shelf (plank) with a little radio and a stack of books. Mounted on the wall, nothing solid."""
    s.box(0.0, 0.0, 1.4, 0.35, 1.55, 1.6, "wood")
    s.box(0.95, 0.05, 1.35, 0.32, 1.6, 1.88, "metal_dark")
    s.cyl(1.15, 0.18, 1.88, 1.93, 0.05, "metal_light")
    s.box(0.15, 0.05, 0.75, 0.3, 1.6, 1.86, "book_d")
    s.box(0.2, 0.07, 0.7, 0.28, 1.86, 1.93, "paper_cream")


def _rug_terracotta(s):
    """Terracotta rug with a cream border (floor decoration, walkable)."""
    s.box(0.0, 0.0, 2.2, 2.5, 0.0, 0.012, "rug_cream", layer="floor")
    s.box(0.18, 0.18, 2.02, 2.32, 0.012, 0.02, "rug_terra", layer="floor")


def _plant_flowers(s, x, y):
    scn.potted_plant(s, x, y, "flowers")


def _plant_bay(s, x, y):
    scn.potted_plant(s, x, y, "bay")


def _chair_diner_red(s):
    s.prop("house/Chair_1", 0.3, 0.3, rot=0, h=1.05, colours={"Wood": "#e04030"})


def _chair_library_oak(s):
    s.prop("house/Chair_1", 0.3, 0.3, rot=0, h=0.9, colours={"Wood": "#e6b866"})


def _sofa_small(s):
    s.prop("house/Couch_Small2", 0.4, 0.8, rot=0, scale=0.5)


FURNITURE = {
    "bed_cosy": dict(name="Cosy oak bed", price=180, category="bed", size=(3.1, 1.55), kind="bed", quality=3, use=(1.6, 0.8, 1.2), build=_bed_cosy),
    "bedside_lamp": dict(name="Bedside table with lamp", price=45, category="lighting", size=(0.48, 0.5), kind=None, quality=1, build=_bedside_lamp),
    "wardrobe_oak": dict(name="Oak wardrobe", price=140, category="storage", size=(1.7, 1.04), kind="wardrobe", quality=1, use=(0.85, 0.5, 1.3), build=_wardrobe_two_door),
    "desk_laptop": dict(name="Writing desk", price=95, category="desk", size=(1.7, 0.77), kind="desk", quality=1, use=(0.85, 0.4, 1.3), build=_desk_laptop),
    "chair_wood": dict(name="Wooden chair", price=25, category="seating", size=(0.6, 0.6), kind=None, quality=1, anchor="centre", build=_chair_wood),
    "window_seat": dict(name="Window seat with cushions", price=120, category="seating", size=(3.6, 0.77), kind=None, quality=1, build=_window_seat),
    "wall_shelf_radio": dict(name="Wall shelf with radio", price=35, category="decor", size=(1.4, 0.35), kind="bookshelf", quality=1, use=(0.7, 0.17, 1.3), build=_wall_shelf_radio),
    "rug_terracotta": dict(name="Terracotta rug", price=40, category="rug", size=(2.2, 2.5), kind=None, quality=1, build=_rug_terracotta),
    "plant_flowers": dict(name="Flowers in a pot", price=12, category="plant", size=(0.5, 0.5), kind=None, quality=1, anchor="centre", native=True, build=_plant_flowers),
    "plant_bay": dict(name="Bay tree in a pot", price=30, category="plant", size=(0.5, 0.5), kind=None, quality=1, anchor="centre", native=True, build=_plant_bay),
    # furniture that already stands in the city's interiors (commercial buildings: diner, library, lobby)
    "chair_diner_red": dict(name="Diner chair (red)", price=35, category="seating", size=(0.6, 0.6), kind="seat", quality=1, anchor="centre", build=_chair_diner_red),
    "chair_library_oak": dict(name="Reading chair (oak)", price=30, category="seating", size=(0.6, 0.6), kind="seat", quality=1, anchor="centre", build=_chair_library_oak),
    "sofa_small": dict(name="Small sofa", price=220, category="seating", size=(1.7, 1.6), kind="seat", quality=2, anchor="centre", build=_sofa_small),
    "toilet_white": dict(name="White toilet", price=150, category="bathroom", size=(1.0, 1.0), kind="toilet", quality=1, native=True, build=scn.toilet_unit),
    "sink_pedestal": dict(name="Pedestal sink with mirror", price=110, category="bathroom", size=(1.4, 0.7), kind="sink", quality=1, native=True, build=scn.sink_unit),
    "bin_pedal": dict(name="Pedal bin", price=15, category="bathroom", size=(0.5, 0.5), kind="bin", quality=1, native=True, build=scn.indoor_bin),
}


def place(s, fid, x, y, rot=0):
    """Draws catalog piece fid. (x, y) = top-left corner of the footprint after rotation (centre for anchor 'centre' pieces)."""
    f = FURNITURE[fid]
    if not hasattr(s, "furniture"):
        s.furniture = []
    s.furniture.append((fid, x, y, rot))
    if f.get("native"):
        f["build"](s, x, y)
        return
    w, d = f["size"]
    if f.get("anchor") == "centre":
        L = Local(s, x - w / 2, y - d / 2, w, d, rot) if rot % 180 == 0 else Local(s, x - d / 2, y - w / 2, w, d, rot)
    else:
        L = Local(s, x, y, w, d, rot)
    f["build"](L)


def use_point(fid, x, y, rot=0):
    """World (x, y, extra_reach) of the catalog piece's interaction point, for tools/interactions.py."""
    f = FURNITURE[fid]
    w, d = f["size"]
    a, b, r = f["use"]
    return (*Local(None, x, y, w, d, rot).pt(a, b), r)
