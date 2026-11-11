"""s74 proposal data (revision 2: 80 x 64 cells) shared by plan.py and mock.py (positions in cells of the proposed `old_block` map)."""
# (kind, x, y, extra_reach_cells, label)   kinds in the tools/interactions.py style; NEW kinds marked *
INTERACTABLES = [
    ("sign*", 10.2, 21.0, 0.0, "barrier notice"),
    ("flap*", 9.3, 30.7, 0.0, "fence flap (gated: sneak_route)"),
    ("sign*", 14.0, 22.0, 0.0, "arch sign / posters"),
    ("hatch*", 69.0, 22.5, 1.5, "NODE 7 hatch"),
    ("sign*", 67.3, 22.0, 0.0, "demolition gate notice"),
    ("shop_stall*", 63.2, 23.6, 0.0, "Rosa's stall"),
    ("chess*", 32.2, 28.9, 0.0, "chess table"),
    ("garden*", 23.0, 30.0, 1.0, "garden beds: water the plants"),
    ("bench", 22.4, 36.6, 0.0, "garden bench"),
    ("hoop*", 57.4, 33.5, 0.0, "shoot hoops"),
    ("hoop*", 65.6, 33.5, 0.0, "shoot hoops"),
    ("bench", 59.0, 28.1, 0.0, "court bench"),
    ("bench", 64.0, 28.1, 0.0, "court bench"),
    ("bench", 39.0, 36.4, 0.0, "pond bench"),
    ("bench", 62.0, 46.5, 0.0, "orchard bench"),
    ("fountain", 50.0, 14.5, 0.0, "square basin: wash face / drink"),
    ("bin", 28.0, 26.2, 0.0, "street bin"),
    ("bin", 44.0, 25.8, 0.0, "street bin"),
    ("bin", 35.0, 11.2, 0.0, "yard bin"),
    ("bin", 61.0, 28.1, 0.0, "court bin"),
    ("kiosk", 17.4, 25.6, 0.0, "newspaper box / scratch cards"),
    ("crate", 38.8, 11.5, 0.0, "M10 crates (yard)"),
    ("noticeboard", 52.5, 13.2, 0.0, "poster wall (Mia, from M13)"),
]
# warps: (x0, y0, x1, y1, target, label)
WARPS = [
    (0.0, 14.6, 1.0, 34.0, "city_centre", "west edge -> City Centre avenue east end"),
    (31.7, 17.0, 33.2, 18.0, "laundromat", "laundromat door"),
    (44.9, 17.0, 46.1, 18.0, "bakery", "bakery door"),
    (37.5, 11.6, 38.4, 12.8, "back_room", "back room door (Chapter 2)"),
]
# NPC placements: (id, x, y, label, when)
NPCS = [
    ("pruitt", 8.6, 19.9, "Guard Pruitt (crossword)", "until M13; then 11.0, 20.5 with tea"),
    ("trench_e", 12.3, 21.3, "TRENCH-E 3", "always"),
    ("ines", 32.9, 19.3, "Ines (door, then inside)", "7:00-21:00"),
    ("teo", 15.5, 26.5, "Teo (wanders the whole map)", "10:00-19:00"),
    ("duchess", 35.8, 16.0, "Duchess (yard)", "always"),
    ("grigor", 33.1, 28.2, "Grigor (chess)", "10:00-18:00"),
    ("valdez", 18.5, 18.8, "Mrs. Valdez + Captain (balcony)", "always"),
    ("rosa", 65.0, 21.6, "Rosa (stall)", "M10+ 8:00-17:00"),
]
# mission hooks: (id, x, y, label)
HOOKS = [
    ("M09", 9.3, 30.7, "sneak route start"),
    ("M09", 15.2, 22.0, "arch: sign tilt"),
    ("M09", 19.2, 21.0, "Valdez balcony"),
    ("M09", 28.5, 20.5, "Mia points up"),
    ("M09", 31.0, 27.0, "chess"),
    ("M10", 38.8, 12.3, "crates"),
    ("M10", 63.0, 22.8, "Rosa's stall"),
    ("M13", 61.5, 22.0, "meeting (crowd)"),
    ("M13", 12.2, 22.0, "barriers moved, Teo's bridge"),
    ("M15", 45.0, 22.0, "Saturday market"),
    ("M17", 32.4, 18.0, "Mia's flat (via laundromat)"),
]
