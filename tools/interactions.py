"""
Town Life - interactable objects per map (kept out of scene.py so editing them never forces a
Blender re-render). Positions in cells. The player must stand within reach of the point
(benches 26 units, fountain radius + 32, everything else 28 units = 1.75 cells).

  ("bench", seat_x, seat_y)       a bench along x with its backrest towards -y; you sit facing +y
                                   (screen down-left). Options: Sit, Sleep.
  ("fountain", centre_x, centre_y, radius)   Options: Wash face.
  ("shop_market", x, y)           Corner Market checkout: shop menu (Bread, Apple, Ready meal, Soda).
  ("shop_diner", x, y)            diner counter: Coffee, Pancakes, Burger.
  ("toilet", x, y)                Use toilet.
  ("sink", x, y)                  Wash hands.
  ("bookshelf", x, y)             Read a book (30 game minutes).
  ("noticeboard", x, y)           info: no jobs posted yet.
  ("reception", x, y)             info: VaultTech access denied.
"""

INTERACTABLES = {
    "city_centre": [
        # City Park
        ("bench", 7.3, 39.4), ("bench", 15.3, 39.4),
        # fountain square
        ("bench", 48.3, 38.0), ("bench", 57.7, 38.0), ("bench", 48.3, 45.0), ("bench", 57.7, 45.0),
        ("fountain", 53.0, 41.0, 2.2),
    ],
    "corner_market": [
        ("shop_market", 12.2, 15.0), ("shop_market", 13.9, 15.0), ("shop_market", 15.2, 15.0),
    ],
    "diner": [
        ("shop_diner", 6.5, 4.5), ("shop_diner", 8.8, 4.5), ("shop_diner", 11.0, 4.5),
    ],
    "community_centre": [
        ("bookshelf", 2.5, 1.0), ("bookshelf", 4.7, 1.0), ("bookshelf", 6.9, 1.0),
        ("bookshelf", 1.0, 4.0), ("bookshelf", 1.0, 6.5),
        ("noticeboard", 10.7, 1.0),
    ],
    "vaulttech_lobby": [
        ("reception", 7.2, 5.5), ("reception", 9.0, 5.5), ("reception", 10.8, 5.5),
    ],
    "public_toilet": [
        ("toilet", 1.2, 1.5), ("sink", 1.0, 3.4),
    ],
}
