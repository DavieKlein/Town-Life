"""
Town Life - interactable objects per map (kept out of scene.py so editing them never forces a
Blender re-render). Positions in cells.

  ("bench", seat_x, seat_y)       a bench along x with its backrest towards -y; you sit facing +y
                                   (screen down-left). Options: Sit, Sleep.
  ("fountain", centre_x, centre_y, radius)   Options: Wash face.
"""

INTERACTABLES = {
    "city_centre": [
        # City Park
        ("bench", 7.3, 39.4), ("bench", 15.3, 39.4),
        # fountain square
        ("bench", 48.3, 38.0), ("bench", 57.7, 38.0), ("bench", 48.3, 45.0), ("bench", 57.7, 45.0),
        ("fountain", 53.0, 41.0, 2.2),
    ],
}
