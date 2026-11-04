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

ROBOT = dict(label="Valet", model="ROBOT", height=1.34, colours={}, props=[], pcam=(0.90, 1.40))


CHARS["robot"]=ROBOT


# Sprite sheets / portraits built by build_assets.py (graphics/npc_<id>.bmp, graphics/portrait_<id>.bmp).
PORTRAIT_ONLY = ["player"]       # the player only needs a portrait (his sprites are rendered by blender_actor.py)
ORDER = ["player", "mia", "rosa", "dex", "pimm", "lou", "dex_vault", "victor", "robot"]

# Every NPC id of the game (index = npc_id in C++ = friendship slot in the save). Halloran has no look yet (Docks).
IDS = ["mia", "rosa", "dex", "pimm", "lou", "halloran", "dex_vault", "victor", "robot"]

# Placements: (npc, map, x, y, facing, from, to, first day, last day) - cells, 24 h clock, days 1..255.
# Daily whereabouts follow docs/story_chapter1.md section 1.11. Rosa, Dex, Victor and Valet only appear in story scenes
# later, so they are not placed freely yet. Facing names: s, sw, w, nw, n, ne, e, se ("sw" looks towards +y).
PLACEMENTS = [
    ("mia", "corner_market", 13.9, 13.4, "sw", "7:00", "14:30", 1, 1),     # checkout on Day 1 (the old shop)
    ("mia", "diner", 9.2, 6.6, "w", "7:00", "12:00", 2, 255),              # waitress shift
    ("mia", "city_centre", 46.6, 38.4, "e", "12:00", "12:30", 2, 255),     # lunch break at the fountain square bench
    ("mia", "diner", 9.2, 6.6, "w", "12:30", "15:00", 2, 255),
    ("lou", "diner", 6.4, 3.4, "sw", "6:00", "22:00", 1, 255),             # behind the counter
    ("pimm", "community_centre", 6.1, 6.2, "n", "10:00", "15:30", 1, 255),  # library reading table
    ("pimm", "city_centre", 20.0, 42.2, "ne", "16:00", "18:00", 1, 255),   # City Park pond, feeding the pigeons
]
