"""
Town Life - interactable objects per map (kept out of scene.py so editing them never forces a
Blender re-render). Positions in cells. The player must stand within reach of the point
(benches 26 units, fountain radius + 32, everything else 28 units = 1.75 cells).

  ("bench", seat_x, seat_y)       a bench along x with its backrest towards -y; you sit facing +y
                                   (screen down-left). Options: Sit, Sleep.
  ("fountain", centre_x, centre_y, radius)   Options: Wash face, Drink water.
  ("deposit", x, y)               RETURN & EARN machine (cans $0.50, bottles $1.00): Return all / Check credit / Leave.
  ("bin", x, y)                   trash can: Search the bin (random find, once per game hour per bin).

Optional 5th element = quality 1..3 (activities: toilet = speed of emptying the bladder, bookshelf =
how fast Fun fills); the 4th element (radius) is 0 for everything but the fountain.
  ("shop_market", x, y)           Corner Market checkout: shop menu (Bread, Apple, Ready meal, Soda).
  ("shop_diner", x, y)            diner counter: Coffee, Pancakes, Burger.
  ("toilet", x, y)                Use toilet.
  ("sink", x, y)                  Wash hands.
  ("bookshelf", x, y)             Read a book (30 game minutes).
  ("noticeboard", x, y)           info: no jobs posted yet.
  ("reception", x, y)             info: VaultTech access denied.
  ("bed", x, y, reach)            the player's bed (room above the Corner Market): Sleep (a night, Energy +1/min, clock 8x, ends with
                                   "Slept well. Save game?") / Take a nap (1 h, Energy +20). 4th element = extra reach in cells.
  ("desk", x, y, reach)           Read (like a bookshelf, quality 1) / Check notes (current objective).
  ("window", x, y, reach)         look outside: flavour text by time of day.
  ("wardrobe", x, y, reach)       info text.
  The room's entries are generated from the furniture catalog (tools/furniture.py, scene.ROOM_FURNITURE + use_point()).
  ("crate", x, y)                 storeroom crate: "Take the rye loaf" while Mr. Pimm waits (story).
  ("kiosk", x, y)                 newspaper boxes at the bus stop: scratch cards ($1, 3 a day) and newspapers (gift).
  ("shower", x, y)                public toilet shower: $1 coin slot, Hygiene to ~100 over 6 s (B cancels).
  ("clinic", x, y)                City Clinic reception: Check-up / Pay the bill / Talk to the doctor.
  ("couch", x, y, reach)          the exam couch (info text); fainting patients wake up here (script op lie_bed falls back to it).
  ("gate", x, y)                  VaultTech staff gate in front of the stairs (only usable after the firing): info text.
  ("seat", x, y, reach)           indoor chair / sofa / booth bench; you sit facing +y (screen down-left).
  ("seat_x", x, y, reach)         same but facing +x (screen down-right: the sit sprite is mirrored).
                                   (x, y) = where the player's seat is drawn (centre of the seat); `reach` = extra
                                   reach in cells on top of 1.75, because the player usually stands beside the
                                   (solid) furniture. Standing up returns to the spot where he sat down.
"""

def _room_things():
    import furniture
    from scene import ROOM_FURNITURE
    out = []
    for fid, x, y, rot in ROOM_FURNITURE:
        f = furniture.FURNITURE[fid]
        if f.get("kind") and "use" in f:
            ux, uy, reach = furniture.use_point(fid, x, y, rot)
            out.append((f["kind"], round(ux, 2), round(uy, 2), reach, f["quality"]))
    out.append(("window", 2.55, 0.45, 0.6))         # the big window above the window seat
    return out


INTERACTABLES = {
    "city_centre": [
        # City Park
        ("bench", 15.3, 39.4),
        ("deposit", 6.2, 37.9),         # RETURN & EARN machine against the east wall of the toilet hut
        # fountain square
        ("bench", 48.3, 38.0), ("bench", 57.7, 38.0), ("bench", 48.3, 45.0), ("bench", 57.7, 45.0),
        ("fountain", 53.0, 41.0, 2.2),
        # trash cans along the avenue (scene.py city_centre)
        ("kiosk", 45.5, 32.4),          # the two newspaper boxes at the bus stop
        ("bin", 5.0, 21.1), ("bin", 17.0, 21.1), ("bin", 53.0, 21.1), ("bin", 68.0, 21.1), ("bin", 38.5, 31.0),
    ],
    "corner_market": [
        ("shop_market", 12.2, 15.0), ("shop_market", 13.9, 15.0), ("shop_market", 15.2, 15.0),
        ("crate", 12.6, 3.1),               # the rye loaf crate in the storeroom (Day 1, Pimm's errand)
        # (the foot of the storeroom stairs is a warp up to "player_room")
    ],
    "vaultmart": [
        # self-checkout kiosks (VaultMart prices, robot voice) and the staff gate in front of the storeroom stairs
        ("shop_market", 11.6, 14.3), ("shop_market", 13.2, 14.3), ("shop_market", 14.8, 14.3),
        ("gate", 15.6, 4.7),
    ],
    "diner": [
        ("shop_diner", 4.6, 4.5), ("shop_diner", 6.4, 4.5), ("shop_diner", 8.2, 4.5),
        # booth benches on the west wall (facing the table) and the north chair of the free table
        ("seat_x", 0.75, 4.4, 1.2), ("seat_x", 0.75, 6.6, 1.2), ("seat", 7.0, 6.6, 1.0),
    ],
    "community_centre": [
        ("bookshelf", 2.5, 1.0, 0, 2), ("bookshelf", 4.7, 1.0, 0, 2), ("bookshelf", 6.9, 1.0, 0, 2),
        ("bookshelf", 1.0, 4.0, 0, 2), ("bookshelf", 1.0, 6.5, 0, 2),
        ("noticeboard", 10.7, 1.0),
        # armchair nook sofa and two reading-table chairs
        ("seat_x", 1.6, 9.6, 1.2), ("seat", 6.1, 4.7, 1.0), ("seat", 13.3, 4.7, 1.0),
    ],
    "vaulttech_lobby": [
        ("reception", 7.2, 5.5), ("reception", 9.0, 5.5), ("reception", 10.8, 5.5),
        # glass-wall benches (west) and the waiting sofa, all facing into the lobby
        ("seat_x", 0.9, 3.95, 1.0), ("seat_x", 0.9, 7.95, 1.0), ("seat_x", 10.85, 9.75, 1.0),
    ],
    "public_toilet": [
        ("toilet", 2.3, 1.5, 0, 1), ("sink", 0.5, 3.5), ("bin", 0.75, 1.0),
        ("shower", 4.55, 1.1),          # s64: the cubicle in the back-right corner (stand in the tray)
    ],
    "clinic": [
        ("clinic", 6.3, 4.45), ("clinic", 7.5, 4.45), ("clinic", 8.7, 4.45),      # reception counter (y 3.1..4.0); the doctor stands behind it
        ("couch", 11.85, 2.1, 0.6),                                                # exam couch along the back wall
        ("seat", 1.2, 1.15, 1.0), ("seat", 2.35, 1.15, 1.0), ("seat", 3.5, 1.15, 1.0),     # waiting chairs (face +y)
        ("seat_x", 1.65, 5.2, 1.2),                                                # the sofa on the west wall (faces +x)
        ("bin", 9.4, 5.0),
    ],
    "player_room": _room_things(),
}
