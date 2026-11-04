# Proposed entries for tools/interactions.py (kind, x, y[, radius][, quality]) - map "room_attic" (variant A) / "room_plain" (variant B)
# (coordinates in cells, same convention as the other maps)
ROOM_A = [
    ("bed",      0.8, 2.5, 1.6, 3),     # Sleep (quality 3) / Take a nap
    ("wardrobe", 6.0, 1.4, 1.2, 1),     # Look inside (info now, change clothes later)
    ("desk",     3.5, 1.35, 1.2, 1),    # Read / Check the shift plan
    ("window",   3.5, 0.9, 1.3, 1),     # Look outside (info text, depends on story state)
    ("shelf",    0.9, 5.8, 1.2, 1),     # Read a book (like bookshelf, quality 1)
]
ROOM_B = [
    ("bed",      6.2, 1.5, 1.6, 3),
    ("wardrobe", 1.4, 2.2, 1.2, 1),
    ("desk",     1.2, 4.1, 1.2, 1),
    ("window",   2.5, 1.0, 1.6, 1),
    ("shelf",    0.9, 6.2, 1.2, 1),
]
