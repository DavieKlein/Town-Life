"""
Town Life - collectibles of district 1 (s64): three sets of four, lying around the City Centre. Kept out of scene.py so editing
the spots never forces a Blender re-render. build_assets writes include/tl_collect_spots.h from SPOTS / SETS and renders the props
with tools/blender_props.py (real 3D props, same camera and sharp style as everything else).

SPOTS: (x, y, set, item, place) in cells; index = set * 4 + item. Items are fixed (no respawn): once picked up they are gone and the
collection screen (pause menu) shows them. Completing a set pays its reward at once.
SETS: (name, short, reward $, City Coins, friend npc, friend +n, completion text lines)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SETS = [
    ("Old City Coins", "Coins", 10, 0, "pimm", 6, ("Old City Coins", "complete! $10 and", "Mr. Pimm will love this.")),
    ("Lost Postcards", "Postcards", 5, 1, "mia", 5, ("Lost Postcards", "complete! $5, 1 City", "Coin. Mia adores them.")),
    ("VaultTech Flyers", "Flyers", 8, 0, "rosa", 6, ("VaultTech Flyers", "complete! $8. Rosa", "wants to see them!")),
]
ITEM_NAMES = [
    ("Copper penny", "Silver crown", "Brass ring coin", "Pewter token"),
    ("Mountain lake", "Sunset beach", "Night skyline", "Lighthouse"),
    ("Gold header", "Black header", "Crumpled flyer", "Folded flyer"),
]
PROPS = ["coin_copper", "coin_silver", "coin_brass", "coin_token", "card_lake", "card_sunset", "card_skyline", "card_lighthouse",
         "flyer_gold", "flyer_black", "flyer_crumpled", "flyer_folded"]

SPOTS = [
    # old city coins: park and fountain square (where old money gets lost)
    (9.5, 38.6, 0, 0, "park path, under the oak"), (12.7, 44.6, 0, 1, "behind the flower bed"),
    (55.9, 39.0, 0, 2, "fountain square, by the basin"), (36.4, 48.6, 0, 3, "river walk, by the railing"),
    # lost postcards: corners and pavement ends
    (0.9, 29.6, 1, 0, "west end of the south pavement"), (70.6, 22.6, 1, 1, "east end of the north pavement"),
    (35.6, 19.8, 1, 2, "in front of the clinic"), (24.6, 33.6, 1, 3, "corner of the cross street"),
    # VaultTech flyers: plaza, bins and the road works
    (63.0, 18.8, 2, 0, "VaultTech plaza"), (47.4, 22.6, 2, 1, "by the diner"),
    (42.4, 22.2, 2, 2, "by the market"), (30.6, 4.0, 2, 3, "road works to the north"),
]
assert len(SPOTS) == 12 and all(s[2] * 4 + s[3] == i for i, s in enumerate(SPOTS))


def check():
    import scene as scn
    s = scn.city_centre()
    R = scn.SOLID_RES
    bad = 0
    for (x, y, st, it, place) in SPOTS:
        solid = s.solid[int(y * R)][int(x * R)]
        bad += solid
        print(f"{x:5.1f} {y:5.1f} {'SOLID' if solid else 'ok   '} set {st} item {it} {place}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if check() else 0)
