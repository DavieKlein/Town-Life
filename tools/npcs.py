"""
Town Life - NPCs per map: (npc, x, y, facing) in cells, standing still (idle frame only).
Kept out of scene.py so moving an NPC never forces a (slow) Blender re-render.

npc: id of a sprite sheet graphics/npc_<id>.bmp (8 frames, one per facing in clockwise screen order
s, sw, w, nw, n, ne, e, se; rendered by tools/blender_actor.py mode "idle").
facing: one of those 8 names. "sw" looks towards +y (down-left on screen).
"""

NPCS = {
    "corner_market": [
        ("mia", 13.9, 13.4, "sw"),     # the shopkeeper, behind the checkout counter
    ],
}

# Look of each NPC sprite: Quaternius model + our own colours.
LOOKS = {
    "mia": dict(model="Female_Casual",
                colours={"Shirt": "#2a9a96", "Pants": "#3c4a66", "Hair": "#c8622a", "HairBase": "#c8622a",
                         "Skin": "#f2c8a4", "Shoes": "#3a2a22", "Socks": "#f2efe6"}),
}
FACINGS = ["s", "sw", "w", "nw", "n", "ne", "e", "se"]
