"""
Town Life - ambient animals: pixel-art sprites + spawn points per map.

Kept out of scene.py on purpose: scene.py is part of the render cache key, so adding or moving
animals here never forces a (slow) Blender re-render.

Sprites are 16x16 frames drawn facing RIGHT on screen (the game flips them for left).
  pigeon.bmp:   0 stand, 1 peck, 2 hop, 3 fly (wings up), 4 fly (wings down)
  squirrel.bmp: 0 sit, 1 run A, 2 run B, 3 climb
Feet / bottom of the animal at y = 13 in each frame.
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

PIGEON_PAL = [
    (255, 0, 255),      # 0 transparent
    (34, 30, 40),       # 1 outline
    (138, 140, 152),    # 2 body grey
    (182, 184, 196),    # 3 light grey
    (98, 100, 114),     # 4 dark grey (wing)
    (84, 128, 112),     # 5 neck green
    (126, 92, 140),     # 6 neck purple
    (228, 126, 70),     # 7 feet / beak
    (240, 236, 226),    # 8 white
    (20, 18, 22),       # 9 eye
]
P = {".": 0, "o": 1, "g": 2, "l": 3, "d": 4, "n": 5, "p": 6, "f": 7, "w": 8, "e": 9}

PIGEON = [
    [  # 0 stand
        "................",
        "................",
        "................",
        "................",
        "................",
        "..........oo....",
        ".........ognoo..",
        ".........onef...",
        "....oooo.opno...",
        "...ogggoopno....",
        "..ogglllggo.....",
        "..oddddlgggo....",
        "...odddgggo.....",
        "....oooooo......",
        "......f.f.......",
        "................",
    ],
    [  # 1 peck (head down)
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "....oooo........",
        "...ogggoo.......",
        "..ogglllgooo....",
        "..oddddlgpnno...",
        "...odddggpnef...",
        "....ooooooon....",
        "......f.f.......",
        "................",
        "................",
    ],
    [  # 2 hop (body up, feet tucked)
        "................",
        "................",
        "................",
        "................",
        "..........oo....",
        ".........ognoo..",
        ".........onef...",
        "....oooo.opno...",
        "...ogggoopno....",
        "..ogglllggo.....",
        "..oddddlgggo....",
        "...odddgggo.....",
        "....oooooo......",
        ".......ff.......",
        "................",
        "................",
    ],
    [  # 3 fly, wings up
        "................",
        "...o.......o....",
        "..odo.....odo...",
        "..oddo...oddo...",
        "...oddo.oddo....",
        "....oddoddo..oo.",
        ".....oddgo..ogno",
        "..ooogggggoonef.",
        ".ogglllllggppno.",
        "..oogggggggoo...",
        "....ooooooo.....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    [  # 4 fly, wings down
        "................",
        "................",
        "................",
        "................",
        ".............oo.",
        "............ogno",
        "..ooooooooo.onef",
        ".ogglllllggopno.",
        "..oggdddddggoo..",
        "...oddddddo.....",
        "....oddddo......",
        ".....oddo.......",
        "......oo........",
        "................",
        "................",
        "................",
    ],
]

SQUIRREL_PAL = [
    (255, 0, 255),      # 0 transparent
    (36, 24, 20),       # 1 outline
    (164, 92, 48),      # 2 fur
    (204, 132, 76),     # 3 light fur
    (112, 60, 32),      # 4 dark fur
    (236, 204, 160),    # 5 belly
    (20, 16, 14),       # 6 eye
]
Q = {".": 0, "o": 1, "f": 2, "l": 3, "d": 4, "b": 5, "e": 6}

SQUIRREL = [
    [  # 0 sit, bushy tail curled up behind
        "................",
        "................",
        "..oooo..........",
        ".ollllo.........",
        "olfffflo........",
        "offddfflo..oo...",
        "offo.offo.offo..",
        ".oo..offooffeo..",
        ".....offofffffo.",
        "......offffbfo..",
        "......offfbbfo..",
        ".....offffbbfo..",
        ".....offfffffo..",
        "......oo..oo....",
        "................",
        "................",
    ],
    [  # 1 run A (stretched, tail streaming)
        "................",
        "................",
        "................",
        "................",
        "................",
        ".oooo...........",
        "olllfoo.........",
        "offdddfo....oo..",
        ".ooodddoooooffo.",
        "....offfffffffeo",
        "....ofbbbbbfffo.",
        ".....ooo..oooo..",
        "....oo.......oo.",
        "................",
        "................",
        "................",
    ],
    [  # 2 run B (legs gathered)
        "................",
        "................",
        "................",
        "................",
        "..oooo..........",
        ".olllfo.........",
        ".offddfo........",
        "..oo.offoooooo..",
        ".....offffffffo.",
        ".....ofbbbbfffeo",
        "......offfffffo.",
        ".......oo.ooo...",
        "........o.o.....",
        "................",
        "................",
        "................",
    ],
    [  # 3 climb (vertical, head up)
        "................",
        ".......oo.......",
        "......offo......",
        "......ofeo......",
        ".....offffo.....",
        ".....ofbbfo.....",
        "....oofbbfoo....",
        ".....ofbbfo.....",
        ".....offffo.....",
        "....oofffoo.....",
        ".....offfo......",
        "....olfffo......",
        "...olllfo.......",
        "...offdo........",
        "....ooo.........",
        "................",
    ],
]


def frames_to_pixels(frames, mapping):
    pixels = []
    for f in frames:
        assert len(f) == 16, len(f)
        for row in f:
            assert len(row) == 16, row
            pixels.append([mapping[c] for c in row])
    return pixels
