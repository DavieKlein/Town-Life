"""
Town Life - the story cast (owner-approved looks, ported from tools/proposals/cast/cdef.py) and where they stand.

CHARS: look of every cast member, rendered by tools/blender_cast.py (idle sprite, 8 facings, 32x64, plus a 64x64 portrait):
  model    Quaternius character FBX (art_source/quaternius_characters) or "ROBOT" (built from primitives)
  height   body height in metres (the 1.78 m model is scaled), widen/depth = extra body width / depth factor
  colours  material name -> colour; props = extra primitives: (kind, (x, y, z) metres, size, colour[, rot degrees])
  pcam     (view width, top) of the portrait camera
Coordinates in metres for a 1.78 m body, facing -Y, x = character's left (+x).

SCHEDULE (placements, further down) says where each NPC stands at which time. Kept out of scene.py so moving an NPC never
triggers a map re-render. build_assets.py generates include/tl_cast_data.h from it.
"""
CHARS = {
 "player": dict(label="You", model="Male_LongSleeve", height=1.78,
    colours={"Shirt":"#2f5aa8","Pants":"#c8a46a","Hair":"#5a3420","Skin":"#f0c09a","Shoes":"#3a2a22","Socks":"#f2efe6"}, props=[]),
 "mia": dict(label="Mia", model="Female_Casual", height=1.78,
    colours={"Shirt":"#2a9a96","Pants":"#3c4a66","Hair":"#c8622a","HairBase":"#c8622a","Skin":"#f2c8a4","Shoes":"#3a2a22","Socks":"#f2efe6"}, props=[]),
 "rosa": dict(label="Rosa Bellini", model="Female_Alternative", height=1.56,
    colours={"Jacket":"#7a2236","LightJacket":"#8e2d44","Shirt":"#efe6cc","Pants":"#34303a","Hair":"#c4c4cc","HairBase":"#c4c4cc","Skin":"#eabf9c","Shoes":"#2e2420","Socks":"#e9e2d0"},
    props=[("sphere",(0,0.09,1.71),(0.075,0.075,0.07),"#c4c4cc"),            # grey bun
           ("torus",(0.043,-0.125,1.665),(0.034,0.034,0.006),"#2a2a30",(90,0,0)),   # round glasses
           ("torus",(-0.043,-0.125,1.665),(0.034,0.034,0.006),"#2a2a30",(90,0,0)),
           ("box",(0,-0.125,1.67),(0.03,0.008,0.008),"#2a2a30"),
           ("torus",(0,-0.035,1.435),(0.075,0.075,0.009),"#f4f0e8")]),       # pearls
 "dex": dict(label="Dex (shop)", model="Male_Shirt", height=1.78,
    colours={"Shirt":"#d8662a","Shirt2":"#e8dcc0","Pants":"#3a4f7a","Hair":"#2a1c18","Hair2":"#2a1c18","Skin":"#dfa676","Shoes":"#f0f0f0","Socks":"#f4f4f4","Eyes":"#202020"},
    props=[("box",(0,-0.118,1.02),(0.27,0.03,0.42),"#2f7a45"),             # green Corner Market apron
           ("box",(0.09,-0.139,1.15),(0.07,0.01,0.04),"#f0e0a0")]),        # name tag
 "dex_vault": dict(label="Dex (VaultMart)", model="Male_Shirt", height=1.78,
    colours={"Shirt":"#a3a9b2","Shirt2":"#eef0f3","Pants":"#8c9199","Hair":"#241814","Hair2":"#241814","Skin":"#dfa676","Shoes":"#25252b","Socks":"#222222","Eyes":"#202020"},
    props=[("box",(0,-0.125,1.20),(0.05,0.02,0.34),"#e2b53a"),             # slick gold tie
           ("box",(0.10,-0.128,1.30),(0.07,0.01,0.04),"#e2b53a"),          # badge
           ]),
 "victor": dict(label="Victor Vault", model="Male_Suit", height=1.84, widen=1.06,
    colours={"Shirt":"#d9ab36","Pants":"#efe2bc","Details":"#f6d874","TieTexture":"#16110e","Hair":"#f1ead4","Skin":"#d49a68","Eyes":"#2a1a10","Shoes":"#2a1a10"},
    props=[("box",(0,-0.115,1.64),(0.205,0.03,0.05),"#0c0c10"),             # sunglasses
           ("torus",(0,-0.07,1.395),(0.125,0.125,0.014),"#f6d874",(62,0,0)),
           ("cyl",(0,-0.145,1.27),(0.042,0.042,0.012),"#f6d874",(90,0,0)),            # gold chain
           ("cyl",(0.255,-0.06,0.42),(0.014,0.014,0.84),"#f2c94c"),        # gold cane
           ("sphere",(0.255,-0.06,0.86),(0.04,0.04,0.04),"#f2c94c")]),
 "pimm": dict(label="Mr. Pimm", model="Male_LongSleeve", height=1.62,
    colours={"Shirt":"#a98d5c","Pants":"#4a4036","Hair":"#f2f2ee","Skin":"#e9bf9c","Shoes":"#3d3026","Socks":"#e8e8e0","Eyes":"#202020"},
    props=[("sphere",(0.0,-0.035,1.70),(0.128,0.132,0.085),"#8b6b45"),            # flat cap
           ("box",(0,-0.13,1.712),(0.17,0.1,0.014),"#6e5236",(8,0,0)),           # cap brim
           ("torus",(0,-0.02,1.46),(0.095,0.095,0.03),"#a8312f"),         # red scarf
           ("cyl",(-0.255,-0.05,0.42),(0.012,0.012,0.84),"#5a3d22")]),     # walking stick
 "lou": dict(label="Big Lou", model="Male_Casual", height=1.66, widen=1.32, depth=1.15,
    colours={"Shirt":"#f4f1ea","Pants":"#566074","Hair":"#3a2a1e","Skin":"#e6b48a","Shoes":"#2d2d2d","Socks":"#eeeeee"},
    props=[("box",(0,-0.125,1.00),(0.30,0.03,0.52),"#b83a32"),             # red diner apron
           ("box",(0,-0.115,1.31),(0.15,0.02,0.07),"#b83a32"),
           ("cyl",(0,0,1.765),(0.108,0.108,0.09),"#fbfbfb"),                # chef hat band
           ("sphere",(0,0,1.86),(0.15,0.15,0.1),"#fbfbfb"),                # puffy top
           ("box",(0,-0.1,1.626),(0.10,0.03,0.022),"#2b1d14")],           # moustache
    pcam=(0.80,1.96)),
}

CHARS["okafor"] = dict(label="Dr. Okafor", model="Female_Alternative", height=1.70,
    colours={"Jacket":"#f6f8f6","LightJacket":"#e6eeea","Shirt":"#1f9a94","Pants":"#2c3a4c","Hair":"#1c1410","HairBase":"#1c1410","Skin":"#b07850","Shoes":"#eeeeee","Socks":"#eeeeee"},
    props=[("torus",(0,-0.035,1.43),(0.085,0.085,0.012),"#2a2a34"),             # stethoscope round the neck
           ("cyl",(0.0,-0.14,1.22),(0.03,0.03,0.012),"#c8d0d8",(90,0,0)),          # chest piece
           ("torus",(0.043,-0.125,1.64),(0.036,0.036,0.005),"#2a2630",(90,0,0)),   # glasses
           ("torus",(-0.043,-0.125,1.64),(0.036,0.036,0.005),"#2a2630",(90,0,0)),
           ("box",(0,-0.125,1.645),(0.03,0.008,0.008),"#2a2630")])

ROBOT = dict(label="Valet", model="ROBOT", height=1.34, colours={}, props=[], pcam=(0.90, 1.40))


CHARS["robot"]=ROBOT

# s76: Old Block residents. Looks are in char_build.B (unique builds), faces in face_cfg.FACE; these rows give label/model/skin/colours
# for the sprite pipeline (blender_cast.py / build_assets.build_cast). TRENCH-E 3, Duchess and Captain are not rigged humans: they are
# sprite-only props rendered by tools/blender_residents.py (RESIDENT_PROPS below).
def _res(label, model, height, colours):
    return dict(label=label, model=model, height=height, colours=colours, props=[])
CHARS["ines"] = _res("Ines Okoro", "Female_Casual", 1.62, {"Shirt": "#e2982c", "Pants": "#5a4a78", "Hair": "#1c1410", "HairBase": "#1c1410", "Skin": "#8a5836", "Shoes": "#2e2a32", "Socks": "#f2efe6"})
CHARS["teo"] = _res("Teo", "Male_Casual", 1.30, {"Shirt": "#3f9a6a", "Pants": "#6e7f98", "Hair": "#1c1410", "Skin": "#c28a5e", "Shoes": "#d8402e", "Socks": "#f2efe6"})
CHARS["grigor"] = _res("Grigor", "Male_LongSleeve", 1.76, {"Shirt": "#27384f", "Pants": "#3a3f46", "Hair": "#e8e8ee", "Skin": "#d79b78", "Shoes": "#2a2420", "Socks": "#d8d8d0", "Eyes": "#2a2420"})
CHARS["valdez"] = _res("Mrs. Valdez", "Female_Dress", 1.57, {"Dress": "#d86a70", "Hair": "#3a3036", "Skin": "#c98e6a", "Shoes": "#4a2a3a"})
CHARS["pruitt"] = _res("Guard Pruitt", "Male_Shirt", 1.76, {"Shirt": "#8f98a6", "Shirt2": "#eef0f3", "Pants": "#3a404c", "Hair": "#3a281c", "Hair2": "#3a281c", "Skin": "#e2b08a", "Shoes": "#25252b", "Socks": "#222222", "Eyes": "#202020"})
CHARS["kessler"] = _res("Kessler", "Male_Suit", 1.90, {"Shirt": "#9aa3ad", "Pants": "#59616e", "Details": "#e2b53a", "TieTexture": "#e6e9ee", "Hair": "#9a7440", "Skin": "#f0c4a4", "Eyes": "#202024", "Shoes": "#1c1f26"})
CHARS["nella"] = _res("Nella Bellini", "Female_Casual", 1.66, {"Shirt": "#8fb59a", "Pants": "#4a5266", "Hair": "#4a3a34", "HairBase": "#4a3a34", "Skin": "#e2b490", "Shoes": "#5a3a2a", "Socks": "#f2efe6"})
# sprite-only residents (name -> (sheet width, sheet height, frames per facing or total, facings used)); see build_assets.build_resident_props
RESIDENT_PROPS = ["trench_e", "duchess", "captain"]
HUMAN_RESIDENTS = ["ines", "teo", "grigor", "valdez", "pruitt", "kessler", "nella"]


# Sprite sheets / portraits built by build_assets.py (graphics/npc_<id>.bmp, graphics/portrait_<id>.bmp).
PORTRAIT_ONLY = ["player"]       # the player only needs a portrait (his sprites are rendered by blender_actor.py)
ORDER = ["player", "mia", "rosa", "dex", "pimm", "lou", "dex_vault", "victor", "robot", "okafor"] + HUMAN_RESIDENTS

# Every NPC id of the game (index = npc_id in C++ = friendship slot in the save). Halloran has no look yet (Docks).
IDS = ["mia", "rosa", "dex", "pimm", "lou", "halloran", "okafor", "dex_vault", "victor", "robot",
       "ines", "teo", "grigor", "valdez", "pruitt", "nella", "kessler", "trench_e", "duchess", "captain"]   # s76: 20 ids (talk slots 20)

# Placements: (npc, map, x, y, facing, from, to, first day, last day) - cells, 24 h clock, days 1..255.
# Daily whereabouts follow docs/story_chapter1.md section 1.11. Rosa, Dex, Victor and Valet only appear in story scenes
# later, so they are not placed freely yet. Facing names: s, sw, w, nw, n, ne, e, se ("sw" looks towards +y).
# Wander routes (s63): an NPC with a route paces between these points (cells, up to 4, looping) while the placement is active, waiting
# a few seconds at each; it stops when you talk to it and waits for the player to pass. Points must be walkable (checked at runtime).
ROUTES = {
    "pimm_pond": [(20.0, 42.2), (24.0, 42.2), (24.0, 40.2), (18.5, 40.2)],       # City Park, round the pond path
    "pimm_library": [(4.9, 7.4), (4.9, 4.4), (3.2, 4.4), (3.2, 7.4)],            # community centre, between the shelves
    "mia_diner": [(9.3, 4.7), (9.3, 7.6)],                                       # diner, along the east wall of the dining room
    # s76: Old Block (docs/old_block_design.md section 6). Points must be walkable on the street (y 19.5..24.5).
    "teo_round": [(20.5, 22.0), (36.0, 22.5), (56.0, 22.0), (36.0, 21.5)],        # Cobble Street, west to east and back
    "duchess_walk": [(36.0, 21.5), (41.0, 22.6)],                                # the corgi's lunchtime walk on the street
}

PLACEMENTS = [
    # Day 1 at the old Corner Market: Rosa and Mia work from 7:00 once the player is awake, until the firing (flag vault_scene).
    # Dex is only placed by the cutscenes (briefing, firing): sprite VRAM allows only ~2 extra actors beside a 128 px dialogue portrait.
    ("mia", "corner_market", 13.9, 13.4, "sw", "7:00", "14:30", 1, 1, None, "vault_scene"),     # checkout on Day 1 (the old shop)
    ("rosa", "corner_market", 12.4, 13.4, "sw", "7:00", "14:30", 1, 1, "woke_up", "vault_scene"),
    # Mr. Pimm waits at the bakery table for his rye loaf (placed after his arrival scene, leaves in the pimm_leaves scene)
    ("pimm", "corner_market", 7.0, 6.9, "ne", "9:00", "13:00", 1, 1, "pimm_scene", "pimm_left"),
    # VaultMart: Dex in the grey blazer paces the aisles (a static figure for now), nobody at the checkout
    ("dex_vault", "vaultmart", 9.6, 11.4, "sw", "6:00", "22:00", 1, 255, "vault_scene", None),
    ("mia", "diner", 9.3, 4.7, "sw", "7:00", "12:00", 2, 255, None, None, "mia_diner"),              # waitress shift
    ("mia", "city_centre", 50.4, 38.9, "w", "12:00", "12:30", 2, 255),     # lunch break at the fountain square bench
    ("mia", "diner", 9.3, 4.7, "sw", "12:30", "15:00", 2, 255, None, None, "mia_diner"),
    ("lou", "diner", 6.4, 2.6, "sw", "6:00", "22:00", 1, 255),             # behind the counter (counter y 3.2..4.1)
    ("pimm", "community_centre", 4.9, 7.4, "ne", "13:00", "16:00", 1, 1, None, None, "pimm_library"),   # library, beside the reading table (Day 1 after the shop)
    ("pimm", "community_centre", 4.9, 7.4, "ne", "8:00", "16:00", 2, 255, None, None, "pimm_library"),
    ("okafor", "clinic", 7.2, 2.5, "sw", "8:00", "20:00", 1, 255),           # behind the reception counter (counter y 3.1..4.0)
    ("pimm", "city_centre", 20.0, 42.2, "ne", "16:00", "19:30", 1, 255, None, None, "pimm_pond"),   # City Park pond, feeding the pigeons

    # ---- s76: Old Block residents (map old_block, cells; the bakery / laundromat interiors) ----
    ("pruitt", "old_block", 8.6, 19.9, "se", "0:00", "23:59", 1, 255),                # folding chair on a drum at the VaultLink cable works
    ("trench_e", "old_block", 12.3, 21.3, "sw", "0:00", "23:59", 1, 255),             # digging in the trench
    ("valdez", "old_block", 18.5, 18.9, "sw", "8:00", "21:00", 1, 255),               # under her balcony (house 16.5..21)
    ("captain", "old_block", 19.8, 18.9, "sw", "8:00", "21:00", 1, 255),              # parrot on his perch next to her
    ("teo", "old_block", 20.5, 22.0, "se", "10:00", "19:00", 1, 255, None, None, "teo_round"),
    ("grigor", "old_block", 33.1, 28.2, "sw", "10:00", "18:00", 1, 255),              # stool at the chess table
    ("ines", "old_block", 34.2, 19.5, "sw", "7:00", "12:00", 1, 255),                 # outside the laundromat door
    ("ines", "laundromat", 6.8, 3.6, "sw", "12:00", "14:00", 1, 255),
    ("ines", "old_block", 34.2, 19.5, "sw", "14:00", "17:00", 1, 255),
    ("ines", "laundromat", 6.8, 3.6, "sw", "17:00", "21:00", 1, 255),
    ("duchess", "old_block", 35.8, 16.0, "e", "7:00", "12:00", 1, 255),               # her bed in the laundromat yard
    ("duchess", "old_block", 36.0, 21.5, "e", "12:00", "13:00", 1, 255, None, None, "duchess_walk"),
    ("duchess", "old_block", 35.8, 16.0, "e", "13:00", "22:00", 1, 255),
    ("nella", "bakery", 4.9, 1.8, "sw", "6:00", "18:00", 1, 255),                     # behind the counter (counter y 2.2..3.1)
    ("rosa", "old_block", 65.0, 21.6, "sw", "8:00", "17:00", 1, 255, "old_block_open", None),   # her stall at the street end
    ("kessler", "city_centre", 30.0, 49.4, "sw", "6:00", "22:00", 1, 255, None, "bridge_open"),   # in front of the closed bridge barrier
]
