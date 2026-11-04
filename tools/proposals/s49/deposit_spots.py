"""Pickup spawn spots for cans and bottles in the City Centre (cells; proposal).
Each spot: (x, y, place, kinds) - `place` is the mood of the spot, kinds = which items fit (c = can, b = bottle).
check(): every spot must be on a free (non-solid) fine-grid cell; run `python3 deposit_spots.py`."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

SPOTS = [
    # City Park (south-west)
    (5.4, 39.9, "beside the park bench", "cb"), (13.4, 39.9, "beside the park bench", "cb"),
    (1.4, 38.4, "against the toilet hut", "cb"), (8.3, 37.0, "under the oak", "c"),
    (11.9, 42.7, "by the flower bed", "cb"), (6.9, 44.2, "behind the planter", "cb"),
    (13.9, 45.2, "at the pond edge", "b"), (5.2, 46.7, "in front of the hedge", "cb"), (11.0, 41.0, "path junction", "c"),
    # avenue, north pavement (by the bins)
    (5.8, 21.7, "next to a bin", "cb"), (16.4, 21.7, "next to a bin", "cb"), (52.4, 21.7, "next to a bin", "cb"),
    (67.4, 21.7, "next to a bin", "cb"), (41.4, 19.5, "by the market crates", "c"),
    # avenue, south pavement
    (39.4, 31.5, "next to a bin", "cb"), (47.2, 33.1, "by the newspaper boxes", "c"),
    (42.0, 34.0, "under the bus shelter bench", "cb"),
    # fountain square
    (50.2, 37.5, "under a bench", "cb"), (58.0, 38.7, "under a bench", "cb"), (49.0, 45.6, "under a bench", "cb"),
    (57.0, 44.4, "under a bench", "cb"), (53.0, 43.9, "on the fountain rim", "b"),
    # river walk
    (10.0, 50.6, "by the railing", "cb"), (24.0, 50.6, "by the railing", "cb"), (47.0, 50.6, "by the railing", "cb"),
    (62.0, 50.6, "by the railing", "cb"),
]

if __name__ == "__main__":
    import scene as scn
    s = scn.city_centre()
    R = scn.SOLID_RES
    bad = 0
    for (x, y, place, kinds) in SPOTS:
        cx, cy = int(x * R), int(y * R)
        solid = s.solid[cy][cx]
        bad += solid
        print(f"{x:5.1f} {y:5.1f} {'SOLID' if solid else 'ok   '} {place}")
    print(len(SPOTS), "spots,", bad, "on solid cells")
