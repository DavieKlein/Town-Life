"""Proposal scenes/helpers (public_toilet_v2, sink_unit, toilet_unit, litter_bin, dumpster, bed, shower_cabin,
ref_sheet). Append to a scratch copy of tools/scene.py (after the helpers, before SCENES) and add the scene
functions to SCENES, then render with blender_render.py + preview.py. Not used by the game."""

# ---------------------------------------------------------------- PROPOSALS (scratch, not in the repo scenes)
def sink_unit(s, x, y, k=1.2):
    """Obvious wash basin on the back wall (faces +y): big white basin on a pedestal, chrome tap and spout, soap
    dispenser, mirror with a light frame above it. k = overall size factor (exaggerated for readability)."""
    X = lambda d: x + d * k
    Y = lambda d: y + d * k
    Z = lambda d: d * k
    s.box(X(-0.34), Y(0.0), X(0.34), Y(0.12), 0.0, Z(1.0), "robot_white")             # pedestal against the wall
    s.box(X(-0.46), Y(0), X(0.46), Y(0.5), Z(0.84), Z(0.94), "robot_white")             # basin rim
    s.box(X(-0.36), Y(0.06), X(0.36), Y(0.44), Z(0.9), Z(0.96), "tile_bath")            # basin dip
    s.cyl(x, Y(0.14), Z(0.94), Z(1.12), 0.035 * k, "chrome", verts=10)                   # tap column
    s.tube([(x, Y(0.14), Z(1.1)), (x, Y(0.2), Z(1.17)), (x, Y(0.3), Z(1.1))], 0.03 * k, "chrome")   # spout
    s.box(X(-0.2), Y(0.1), X(-0.1), Y(0.18), Z(0.94), Z(1.06), "chrome")                # tap handles
    s.box(X(0.1), Y(0.1), X(0.2), Y(0.18), Z(0.94), Z(1.06), "chrome")
    s.cyl(X(0.5), Y(0.12), Z(0.94), Z(1.1), 0.06 * k, "goods_green", verts=10)           # soap
    s.box(X(-0.5), Y(0.0), X(0.5), Y(0.07), Z(1.3), Z(2.0), "robot_white")               # mirror frame
    s.box(X(-0.44), Y(0.07), X(0.44), Y(0.09), Z(1.36), Z(1.94), "steel")                # mirror (silver, not window-blue)
    s.set_solid(X(-0.5), y, X(0.5), Y(0.55))
    s.occluder(X(-0.5), y, X(0.5), Y(0.55), Z(1.1))


def toilet_unit(s, x, y):
    """White WC with lid up, tank, flush button, roll holder: nothing in front of it."""
    s.prop("house/Bathroom_Toilet", x, y + 0.45, rot=0, scale=0.52, colours={"White": "#f6f6f0"}, solid=True)
    s.box(x + 0.75, y + 0.0, x + 0.88, y + 0.15, 0.85, 0.97, "robot_white")               # paper roll holder
    s.cyl(x + 0.82, y + 0.16, 0.9, 1.0, 0.07, "paper_cream", axis="y", verts=12)


def litter_bin(s, x, y, tint="bin_green"):
    """Bigger, brighter bin: flared body, white band, dark lid with a flap, litter."""
    s.cyl(x, y, 0.0, 0.8, 0.27, tint, verts=14, r2=0.32)
    s.cyl(x, y, 0.45, 0.58, 0.3, "robot_white", verts=14)                                  # band
    s.cyl(x, y, 0.8, 0.9, 0.35, "metal_dark", verts=14)
    s.box(x - 0.18, y + 0.2, x + 0.18, y + 0.3, 0.9, 1.02, "goods_yellow")                # bag/litter on top
    s.set_solid(x - 0.3, y - 0.3, x + 0.3, y + 0.3)
    s.occluder(x - 0.4, y - 0.4, x + 0.4, y + 0.4, 1.0)


def public_toilet_v2():
    W, H = 6, 6
    s = std_room("public_toilet", "Public toilet", W, H, "tile_floor_dirty", "plaster_bare", "tile_dirty", 1.7, 3.0, (2, 5),
                 "city_centre", 3.0, 40.9, mat_cols=("metal_dark", "stain"))
    # open WC on the back wall: nothing stands in front of it any more
    toilet_unit(s, 2.9, 0.0)
    s.box(2.2, 0.0, 3.7, 0.06, 2.3, 2.9, "sign_blue")
    s.text("WC", 2.95, 0.09, 2.6, 0.5, "robot_white", face="left")
    s.tube([(2.15, 0.12, 0.85), (2.15, 0.9, 0.85)], 0.025, "chrome") if False else None
    # west wall: window, sink with big mirror, hand dryer
    window_x(s, 1.0, 2.4, 0.0, 1.5, 2.5)
    sw = SwapProxy(s)
    sink_unit(sw, 3.5, 0.0)
    s.box(0.0, 4.4, 0.3, 4.9, 1.1, 1.5, "chrome")                                            # hand dryer
    s.box(0.3, 4.5, 0.34, 4.8, 1.2, 1.4, "metal_dark")
    # back wall left: notice + shelf with toilet rolls
    s.box(0.4, 0.0, 1.7, 0.05, 1.7, 2.5, "paper_cream")
    s.text("PLEASE KEEP", 1.05, 0.08, 2.3, 0.15, "metal_dark", face="left")
    s.text("CLEAN", 1.05, 0.08, 2.05, 0.15, "metal_dark", face="left")
    s.box(0.4, 0.0, 1.7, 0.3, 1.0, 1.05, "wood_dark")
    for i in range(4):
        s.cyl(0.65 + i * 0.28, 0.14, 1.05, 1.23, 0.1, "robot_white", verts=12)
    # bins: one by the west wall, a second on the right
    litter_bin(s, 0.75, 1.0)
    litter_bin(s, 4.55, 3.4)
    # mop + bucket + broom in the back-right corner
    s.cyl(4.55, 0.55, 0.0, 0.38, 0.22, "bucket_yellow", verts=14, r2=0.27)
    s.cyl(4.55, 0.55, 0.36, 0.38, 0.19, "stain", verts=14)
    s.tube([(4.5, 0.5, 0.3), (4.18, 0.2, 1.45)], 0.022, "wood")
    s.sphere(4.5, 0.5, 0.3, 0.1, "robot_white", sz=0.6)
    s.tube([(4.9, 0.18, 0.05), (4.78, 0.15, 1.45)], 0.022, "wood")
    s.box(4.72, 0.12, 4.98, 0.34, 0.0, 0.12, "goods_yellow")
    s.box(4.2, 0.0, 4.75, 0.05, 1.7, 2.3, "poster_yellow")                                    # hygiene poster
    s.box(4.3, 0.05, 4.65, 0.07, 1.95, 2.05, "metal_dark")
    s.box(4.3, 0.05, 4.55, 0.07, 1.8, 1.88, "metal_dark")
    # wet floor A-frame sign
    s.box(3.8, 1.9, 4.3, 2.0, 0.0, 0.6, "goods_yellow")
    s.box(3.8, 2.05, 4.3, 2.15, 0.0, 0.6, "goods_yellow")
    s.set_solid(3.8, 1.9, 4.3, 2.15)
    for (gx, gz0, gz1) in ((1.9, 0.15, 1.4), (4.1, 0.15, 1.1)):
        s.box(gx, 0.0, gx + 0.1, 0.045, gz0, gz1, "stain")
    s.point_light(2.5, 2.5, 2.6, 85, colour=(0.9, 0.98, 1.0))
    s.point_light(4.5, 4.0, 2.6, 60, colour=(0.9, 0.98, 1.0))
    return s


def dumpster(s, x, y):
    """Street container with a hinged lid, ribs, wheels and a reflective stripe; faces +y."""
    w, d = 2.6, 1.5
    s.box(x, y, x + w, y + d, 0.18, 1.15, "locker_green")
    s.box(x - 0.04, y - 0.04, x + w + 0.04, y + d + 0.04, 1.15, 1.22, "metal_dark")           # rim
    s.box(x - 0.06, y - 0.06, x + w + 0.06, y + d * 0.55, 1.22, 1.3, "metal_dark")             # lid flap (back half)
    s.box(x - 0.06, y + d * 0.55 + 0.05, x + w + 0.06, y + d + 0.06, 1.2, 1.26, "metal_dark")   # lid flap (front, lower)
    s.box(x + 0.12, y + d, x + 0.26, y + d + 0.04, 0.36, 1.15, "metal_dark")                  # ribs (front)
    s.box(x + w - 0.26, y + d, x + w - 0.12, y + d + 0.04, 0.36, 1.15, "metal_dark")
    s.box(x, y + d, x + w, y + d + 0.03, 0.22, 0.34, "goods_yellow")                          # stripe
    s.box(x + w / 2 - 0.45, y + d, x + w / 2 + 0.45, y + d + 0.05, 0.5, 0.95, "robot_white")    # label plate
    s.box(x + w / 2 - 0.3, y + d + 0.05, x + w / 2 + 0.3, y + d + 0.07, 0.62, 0.68, "stain")      # bin pictogram: slot
    s.box(x + w / 2 - 0.22, y + d + 0.05, x + w / 2 + 0.22, y + d + 0.07, 0.72, 0.84, "stain")
    s.box(x - 0.1, y + 0.3, x, y + d - 0.3, 0.7, 0.78, "metal_dark")                            # side handle
    for wx in (x + 0.25, x + w - 0.25):
        s.cyl(wx, y + d - 0.2, 0.0, 0.2, 0.12, "metal_dark", axis="y", verts=10)
    s.set_solid(x, y, x + w, y + d)
    s.occluder(x - 0.1, y - 0.1, x + w + 0.1, y + d + 0.1, 1.35)


def bed(s, x, y):
    """Single bed, head against the back wall (y = 0)... head at low y, running along +y."""
    w, l = 1.4, 2.7
    s.box(x, y, x + w, y + l, 0.2, 0.34, "wood_dark")                                         # frame
    for (bx, by) in ((x, y), (x + w - 0.1, y), (x, y + l - 0.1), (x + w - 0.1, y + l - 0.1)):
        s.box(bx, by, bx + 0.1, by + 0.1, 0.0, 0.2, "wood_dark")
    s.box(x - 0.02, y - 0.02, x + w + 0.02, y + 0.1, 0.2, 1.1, "wood")                         # headboard
    s.box(x + 0.05, y + 0.1, x + w - 0.05, y + l - 0.05, 0.34, 0.52, "mattress")
    s.box(x + 0.1, y + 0.15, x + w - 0.1, y + 0.7, 0.52, 0.64, "robot_white")                  # pillow
    s.box(x + 0.05, y + 0.85, x + w - 0.05, y + l - 0.05, 0.52, 0.64, "goods_blue")            # blanket
    s.box(x + 0.05, y + 0.85, x + w - 0.05, y + 1.05, 0.64, 0.68, "robot_white")               # folded-over sheet
    s.set_solid(x, y, x + w, y + l)
    s.occluder(x, y, x + w, y + l, 1.1)


def shower_cabin(s, x, y):
    """Corner shower: white tray, glass screens with chrome frame, chrome head with water streaks, mixer knob."""
    w = 1.5
    s.box(x, y, x + w, y + w, 0.0, 0.14, "robot_white")                                        # tray
    s.box(x + 0.15, y + 0.15, x + w - 0.15, y + w - 0.15, 0.14, 0.16, "tile_bath")             # drain area (dark blue-grey)
    s.cyl(x + w / 2, y + w / 2, 0.16, 0.18, 0.07, "metal_dark", verts=10)
    for (px, py) in ((x + w - 0.05, y + w - 0.05), (x + w - 0.05, y + 0.0), (x, y + w - 0.05)):
        s.box(px, py, px + 0.05, py + 0.05, 0.14, 2.1, "chrome")                                # frame posts
    s.box(x, y + w - 0.05, x + w, y + w, 2.05, 2.1, "chrome")                                   # top rails
    s.box(x + w - 0.05, y, x + w, y + w, 2.05, 2.1, "chrome")
    s.box(x + 0.02, y + w - 0.03, x + 0.75, y + w - 0.01, 0.3, 2.0, "sign_blue")                  # curtain, half drawn
    for i in range(5):
        s.cyl(x + 0.08 + i * 0.15, y + w - 0.02, 2.0, 2.06, 0.03, "chrome", verts=8)            # rings
    s.box(x + w - 0.03, y + 0.05, x + w - 0.01, y + w - 0.05, 0.3, 2.0, "glass_pane") if False else None
    s.tube([(x + w / 2, y + 0.04, 1.2), (x + w / 2, y + 0.04, 2.0), (x + w / 2, y + 0.4, 2.15)], 0.03, "chrome")
    s.cyl(x + w / 2, y + 0.5, 2.1, 2.16, 0.16, "chrome", verts=14)                              # rain head
    for i in range(7):
        a = i - 3
        s.box(x + w / 2 + a * 0.09 - 0.008, y + 0.5 + abs(a) * 0.05 - 0.008, 0.25, 2.1, "window_sky") if False else None
        s.box(x + w / 2 + a * 0.08 - 0.01, y + 0.5 + abs(a) * 0.02 - 0.01, x + w / 2 + a * 0.08 + 0.01,
              y + 0.5 + abs(a) * 0.02 + 0.01, 0.3, 2.08, "window_sky") if False else \
            s.box(x + w / 2 + a * 0.08 - 0.012, y + 0.5 - 0.012, x + w / 2 + a * 0.08 + 0.012, y + 0.5 + 0.012,
                  0.3, 2.08, "window_sky")
    s.box(x + 0.25, y + 0.03, x + 0.45, y + 0.12, 1.05, 1.2, "chrome")                          # mixer knob
    s.set_solid(x, y, x + w, y + w)
    s.occluder(x, y, x + w, y + w, 2.1)



def ref_sheet():
    W, H = 22, 5
    s = std_room("ref_sheet", "Reference objects", W, H, "tile_floor_dirty", "plaster_bare", "tile_dirty", 1.7, 3.0,
                 (2, 5), "city_centre", 3.0, 40.9, mat_cols=("metal_dark", "stain"))
    toilet_unit(s, 1.2, 0.0)
    sink_unit(s, 3.8, 0.0)
    shower_cabin(s, 6.4, 0.1)
    bed(s, 9.7, 0.2)
    dumpster(s, 12.6, 0.3)
    trash_can(s, 16.6, 1.2)
    litter_bin(s, 19.4, 1.2)
    return s

