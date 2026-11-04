#!/usr/bin/env python3
"""seats.png: before/after of the indoor seats (headless shots from base.gba = HEAD and v2.gba = seat fix)."""
import sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
import lib
from PIL import Image

S = "/tmp/claude-0/s49/seat/"
BOX = (50, 18, 190, 108)
rows = [
    ("Library chair", ["chair_0", "chair_1", "chair2_1"]),
    ("Library sofa", ["couch_0", "couch_1", "couch2_1"]),
    ("Diner chair", [None, "diner_chair_base", "diner_chair_v2"]),
    ("Diner booth", [None, "diner_booth_base", "diner_booth_v2"]),
    ("Lobby bench", [None, "lobby_bench_base", "lobby_bench_v2"]),
    ("Lobby sofa", [None, "lobby_sofa_base", "lobby_sofa_v2"]),
]
labels = ["before sitting", "sitting: BEFORE fix", "sitting: AFTER fix"]
tiles = []
for name, files in rows:
    for lab, f in zip(labels, files):
        if f is None:
            tiles.append((Image.new("RGB", (BOX[2] - BOX[0], BOX[3] - BOX[1]), (40, 42, 50)), f"{name}: -"))
        else:
            tiles.append((Image.open(S + f + ".png").convert("RGB").crop(BOX), f"{name}: {lab}"))
lib.labelled(tiles, n=2, cols=3, title="Indoor seats: seat point moved so the pelvis lands on the seat").save("/tmp/claude-0/s49/seats.png")
