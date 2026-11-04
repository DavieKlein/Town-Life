"""
Town Life - can & bottle deposit ("RETURN & EARN"): pickup spots in the City Centre (cells). Kept out of scene.py, so
editing them never forces a Blender re-render. build_assets writes include/tl_deposit_spots.h from SPOTS.

Each spot: (x, y, kinds, bush, place). kinds: c = a can may lie there, b = a bottle may lie there. bush = 1 when the
spot is in or next to bushes / hedges / flower beds (picking up costs Hygiene -2 instead of -1).
Game rules (src/tl_deposit.cpp): can = 1 credit ($0.50), bottle = 2 credits ($1.00); the district never holds more than
7 credits ($3.50) of loose pickups; top-up at 6:00 every day; the bag holds 10 items.

check(): every spot must be on a free (non-solid) fine-grid cell:  python3 tools/deposit.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SPOTS = [
    # City Park (south-west)
    (5.4, 40.3, "cb", 0, "on the path near the machine"), (13.4, 40.0, "cb", 0, "beside the park bench"),
    (1.4, 40.6, "cb", 0, "against the toilet hut"), (8.3, 37.2, "c", 0, "under the oak"),
    (11.9, 42.7, "cb", 1, "by the flower bed"), (6.9, 44.2, "cb", 1, "behind the planter"),
    (13.9, 45.2, "b", 0, "at the pond edge"), (5.2, 46.7, "cb", 1, "in front of the hedge"), (11.0, 41.0, "c", 0, "path junction"),
    # avenue, north pavement (by the bins)
    (5.8, 21.7, "cb", 0, "next to a bin"), (16.4, 21.7, "cb", 0, "next to a bin"), (52.4, 21.7, "cb", 0, "next to a bin"),
    (67.4, 21.7, "cb", 0, "next to a bin"), (41.4, 19.5, "c", 0, "by the market crates"),
    # avenue, south pavement
    (39.4, 31.5, "cb", 0, "next to a bin"), (47.2, 33.1, "c", 0, "by the newspaper boxes"),
    (42.0, 34.0, "cb", 0, "under the bus shelter bench"),
    # fountain square
    (50.2, 37.5, "cb", 0, "under a bench"), (58.0, 38.7, "cb", 0, "under a bench"), (49.0, 45.6, "cb", 0, "under a bench"),
    (57.0, 44.4, "cb", 0, "under a bench"), (53.0, 43.9, "b", 0, "on the fountain rim"),
    # river walk
    (10.0, 50.6, "cb", 0, "by the railing"), (24.0, 50.6, "cb", 0, "by the railing"), (47.0, 50.6, "cb", 0, "by the railing"),
    (62.0, 50.6, "cb", 0, "by the railing"),
]
assert len(SPOTS) == 26

MACHINE = (6.2, 37.9)          # the RETURN & EARN machine (interaction point, cells)


def check():
    import scene as scn
    s = scn.city_centre()
    R = scn.SOLID_RES
    bad = 0
    for (x, y, kinds, bush, place) in SPOTS:
        solid = s.solid[int(y * R)][int(x * R)]
        # also the cell the player would stand on 0.4 cells towards the avenue / machine side
        bad += solid
        print(f"{x:5.1f} {y:5.1f} {'SOLID' if solid else 'ok   '} {place}")
    print(len(SPOTS), "spots,", bad, "on solid cells")
    return bad


if __name__ == "__main__":
    sys.exit(1 if check() else 0)
