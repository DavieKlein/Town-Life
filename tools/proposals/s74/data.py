"""s74 proposal data shared by plan.py and mock.py (positions in cells of the proposed `old_block` map, 60 x 48)."""
# (kind, x, y, extra_reach_cells, label)   kinds in the tools/interactions.py style; NEW kinds marked *
INTERACTABLES = [
    ("sign*", 10.2, 21.0, 0.0, "barrier notice"),
    ("flap*", 9.3, 30.7, 0.0, "fence flap (gated: sneak_route)"),
    ("sign*", 14.0, 22.0, 0.0, "arch sign / posters"),
    ("hatch*", 51.0, 22.5, 1.5, "NODE 7 hatch"),
    ("sign*", 49.3, 22.0, 0.0, "demolition gate notice"),
    ("shop_stall*", 47.2, 23.6, 0.0, "Rosa's stall"),
    ("chess*", 32.2, 28.7, 0.0, "chess table"),
    ("garden*", 23.0, 30.0, 1.0, "garden beds: water the plants"),
    ("bench", 22.4, 36.6, 0.0, "garden bench"),
    ("hoop*", 36.4, 33.7, 0.0, "shoot hoops"),
    ("hoop*", 46.6, 33.7, 0.0, "shoot hoops"),
    ("bench", 38.2, 28.6, 0.0, "court bench"),
    ("bench", 44.2, 28.6, 0.0, "court bench"),
    ("bin", 24.0, 26.2, 0.0, "street bin"),
    ("bin", 39.5, 25.8, 0.0, "street bin"),
    ("bin", 30.4, 11.2, 0.0, "yard bin"),
    ("bin", 39.5, 28.6, 0.0, "court bin"),
    ("kiosk", 17.4, 25.6, 0.0, "newspaper box / scratch cards"),
    ("crate", 33.7, 11.5, 0.0, "M10 crates (yard)"),
    ("noticeboard", 36.2, 24.9, 0.0, "poster wall (Mia, from M13)"),
]
# warps: (x0, y0, x1, y1, target, label)
WARPS = [
    (0.0, 14.6, 1.0, 34.0, "city_centre", "west edge -> City Centre avenue east end"),
    (27.3, 17.0, 28.7, 18.0, "laundromat", "laundromat door"),
    (39.4, 17.0, 40.6, 18.0, "bakery", "bakery door"),
    (33.0, 11.6, 34.0, 12.8, "back_room", "back room door (from M17 / Chapter 2)"),
]
# NPC placements: (id, x, y, label, when)
NPCS = [
    ("pruitt", 8.6, 19.9, "Guard Pruitt (crossword)", "until M13; then 11.0, 20.5 with tea"),
    ("trench_e", 12.3, 21.3, "TRENCH-E 3", "always"),
    ("ines", 28.4, 19.3, "Ines (in the door, then inside)", "7:00-21:00"),
    ("teo", 15.5, 26.5, "Teo (wanders the whole map)", "10:00-19:00"),
    ("duchess", 31.0, 16.0, "Duchess (yard)", "always"),
    ("grigor", 32.2, 29.0, "Grigor (chess)", "10:00-18:00"),
    ("valdez", 18.5, 18.8, "Mrs. Valdez + Captain (balcony)", "always"),
    ("rosa", 49.2, 21.6, "Rosa (stall)", "M10+ 8:00-17:00"),
]
# mission hooks: (id, x, y, label)
HOOKS = [
    ("M09", 9.3, 30.7, "sneak route start"),
    ("M09", 15.2, 22.0, "arch: sign tilt"),
    ("M09", 19.2, 21.0, "Valdez balcony"),
    ("M09", 24.0, 20.5, "Mia points up"),
    ("M09", 30.8, 26.8, "chess"),
    ("M10", 33.4, 12.3, "crates"),
    ("M10", 47.0, 22.8, "Rosa's stall"),
    ("M13", 45.5, 22.0, "meeting (crowd)"),
    ("M13", 12.2, 22.0, "barriers moved, Teo's bridge"),
    ("M15", 38.0, 22.0, "Saturday market"),
    ("M17", 28.0, 18.0, "Mia's flat (via laundromat)"),
]
