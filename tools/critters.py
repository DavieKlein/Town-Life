"""
Town Life - ambient animals: spawn points per map.

Kept out of scene.py on purpose: scene.py is part of the render cache key, so adding or moving
animals here never forces a (slow) Blender re-render.

Sprites are rendered from 3D models by tools/blender_critter.py (32x32 frames facing RIGHT on
screen, the game mirrors them for left, feet at (16, 23)):
  pigeon.bmp:   0 stand, 1 peck, 2 wings up, 3 wings mid, 4 wings down
  squirrel.bmp: 0 sit, 1 run A, 2 run B, 3 climb
"""

# Spawn points per map: (kind, x, y) in cells. "squirrel" spawns can give a tree to climb:
# (kind, x, y, tree_x, tree_y).
SPAWNS = {
    "city_centre": [
        # pigeons on the fountain square and the avenue sidewalks
        ("pigeon", 50.5, 37.0), ("pigeon", 51.4, 37.6), ("pigeon", 50.2, 38.2),
        ("pigeon", 56.0, 44.2), ("pigeon", 56.8, 43.6),
        ("pigeon", 8.5, 32.0), ("pigeon", 9.3, 32.6),
        ("pigeon", 60.0, 16.6), ("pigeon", 61.0, 16.0),
        # squirrels in City Park, each next to a tree it flees up into
        ("squirrel", 6.0, 37.5, 3.5, 36.5), ("squirrel", 17.2, 36.9, 19.5, 36.5),
        ("squirrel", 6.5, 45.0, 7.5, 46.0),
    ],
    # s75 Old Block: pigeons at the arch, the stall and the chess plaza; squirrels in the orchard
    "old_block": [
        # s82: two rats near the yard bin and the north alley gate; the "hole" (tree_x / tree_y) is the foot of the fence / wall
        ("rat", 35.4, 16.4, 35.8, 14.8), ("rat", 21.9, 16.9, 22.6, 14.9),
        ("pigeon", 16.0, 23.0), ("pigeon", 16.8, 23.6), ("pigeon", 62.0, 25.2), ("pigeon", 61.2, 25.6),
        ("pigeon", 31.0, 30.6), ("pigeon", 33.4, 31.2),
        ("squirrel", 59.6, 44.2, 58.0, 43.0), ("squirrel", 72.8, 50.8, 74.0, 49.0),
    ],
    # s82: rats in the sewer; each runs into the nearest drain (tools/scene_sewer.py DRAINS) when the player comes close
    "sewer": [
        ("rat", 5.6, 1.6, 7.0, 1.3), ("rat", 9.0, 1.9, 7.0, 1.3), ("rat", 18.4, 1.5, 19.8, 1.3),
        ("rat", 8.2, 6.8, 5.0, 7.4), ("rat", 11.6, 7.6, 14.0, 7.3), ("rat", 17.0, 7.0, 14.0, 7.3), ("rat", 25.4, 6.4, 27.0, 7.4),
    ],
}
