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
        ("squirrel", 6.0, 37.5, 3.5, 36.5), ("squirrel", 17.5, 38.0, 19.5, 36.5),
        ("squirrel", 6.5, 45.0, 4.0, 45.5),
    ],
}
