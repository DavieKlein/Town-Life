"""
s75 proposal: build table for the NEW Old Block residents (data only; importable without Blender).
Same format as tools/char_build.py (see its docstring). `inject()` adds the entries to char_build.B, cast.CHARS and face_cfg.FACE
IN MEMORY so the real tools (char72, blender_cast, face_pass) can render them without touching any game file.

Mesh units: the 1.78 m body is 4.84 units tall (1 unit = 0.37 m); head local coords: x +left, y -front/+back, z up (head z 4.12-4.84).
Props are in metres for a 1.78 m body (scaled by height/1.78), facing -y, x = character's left.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TOOLS)

B = {}
FACE = {}
LABEL = {}

# --- Ines Okoro: laundromat owner, 50s. Short, round, big smile, curler scarf, yellow rubber gloves, blue apron.
B["ines"] = dict(
    model="Female_Casual", height=1.62,
    colours={"Shirt": "#e2982c", "Pants": "#5a4a78", "Hair": "#1c1410", "HairBase": "#1c1410", "Skin": "#8a5836", "Shoes": "#2e2a32", "Socks": "#f2efe6"},
    props=[("box", (0, -0.19, 0.98), (0.31, 0.03, 0.50), "#3b6fb0"),                      # blue laundry apron over the belly
           ("box", (0, -0.158, 1.32), (0.17, 0.03, 0.12), "#3b6fb0"),                       # bib
           ("box", (0.0, -0.208, 1.0), (0.12, 0.01, 0.09), "#f4f0e4"),                      # pocket
           ("sphere", (0.0, -0.01, 1.77), (0.172, 0.178, 0.115), "#c8327a"),                # magenta head scarf
           ("torus", (0.0, -0.05, 1.70), (0.168, 0.172, 0.022), "#f6d24a"),                 # yellow band
           ("sphere", (0.0, -0.14, 1.865), (0.055, 0.05, 0.045), "#c8327a"),                # knot
           ("cyl", (-0.075, -0.168, 1.80), (0.026, 0.026, 0.085), "#f08ab8", (90, 0, 0)),   # curlers peeking out
           ("cyl", (0.0, -0.172, 1.805), (0.026, 0.026, 0.085), "#8ad0e8", (90, 0, 0)),
           ("cyl", (0.075, -0.168, 1.80), (0.026, 0.026, 0.085), "#f08ab8", (90, 0, 0))],
    gloves="#f4d020",
    head=1.30, hand=1.14, shoulder=1.04, chest=1.10, belly=0.24, bellyx=0.16, bust=0.14, hips=0.16, girth=(1.22, 1.20, 1.14), lean=(-2, -1, 1, 0),
    face=dict(nose=(1.15, 1.0), jaw=1.15, brow_w=1.0, brow_tilt=2, smile=0.95, age=1),
    hair=[("sphere", (0.28, 0.10, 4.45), (0.05, 0.10, 0.12), "#1c1410"), ("sphere", (-0.28, 0.10, 4.45), (0.05, 0.10, 0.12), "#1c1410")],
    extras=[])
FACE["ines"] = dict(iris="#2a1a0e", brow="#140c08", lips="#8a3a42", plips="#7c343c", female=True, hair="#1c1410", glasses=None)
LABEL["ines"] = "Ines"

# --- Teo: 10-year-old messenger. Small, big head, oversize cap, skateboard strapped to his back.
B["teo"] = dict(
    model="Male_Casual", height=1.30,
    colours={"Shirt": "#3f9a6a", "Pants": "#6e7f98", "Hair": "#1c1410", "Skin": "#c28a5e", "Shoes": "#d8402e", "Socks": "#f2efe6"},
    props=[("sphere", (0.0, -0.02, 1.80), (0.172, 0.176, 0.112), "#e8742a"),                # oversize orange cap
           ("box", (0, -0.17, 1.80), (0.20, 0.11, 0.016), "#c85a1c", (6, 0, 0)),            # brim
           ("cyl", (0.0, -0.02, 1.915), (0.018, 0.018, 0.02), "#c85a1c"),                    # cap button
           ("box", (0.0, 0.17, 1.00), (0.24, 0.045, 0.50), "#c9a064", (0, 0, 0)),           # skateboard strapped on his back (deck)
           ("cyl", (0.09, 0.20, 1.20), (0.040, 0.040, 0.03), "#f0f0e8", (0, 90, 0)),        # wheels
           ("cyl", (-0.09, 0.20, 1.20), (0.040, 0.040, 0.03), "#f0f0e8", (0, 90, 0)),
           ("cyl", (0.09, 0.20, 0.82), (0.040, 0.040, 0.03), "#f0f0e8", (0, 90, 0)),
           ("cyl", (-0.09, 0.20, 0.82), (0.040, 0.040, 0.03), "#f0f0e8", (0, 90, 0)),
           ("box", (0.0, 0.21, 1.00), (0.20, 0.012, 0.30), "#3a7ac8"),                      # board graphic
           ("sphere", (0.14, -0.19, 0.93), (0.045, 0.04, 0.04), "#f08a1e")],                 # a "borrowed" orange in the pocket
    head=1.52, hand=1.18, shoulder=0.80, chest=0.86, belly=0.0, girth=(0.80, 0.86, 0.82), lean=(3, 5, 3, -2), arms_len=0.92,
    face=dict(nose=(0.7, 0.75), jaw=0.78, brow_w=0.9, brow_tilt=-2, smile=0.85, age=0),
    hair=[("sphere", (0.27, 0.12, 4.40), (0.05, 0.09, 0.10), "#1c1410"), ("sphere", (-0.27, 0.12, 4.40), (0.05, 0.09, 0.10), "#1c1410")],
    extras=[])
FACE["teo"] = dict(iris="#2a1a0e", brow="#1c1410", lips="#b0584c", plips="#a2504a", female=False, hair="#1c1410", glasses=None)
LABEL["teo"] = "Teo"

# --- Grigor: retired ferry captain, 70. Broad, upright, white beard, white captain's cap, navy fisherman's sweater.
B["grigor"] = dict(
    model="Male_LongSleeve", height=1.76,
    colours={"Shirt": "#27384f", "Pants": "#3a3f46", "Hair": "#e8e8ee", "Skin": "#d79b78", "Shoes": "#2a2420", "Socks": "#d8d8d0", "Eyes": "#2a2420"},
    props=[("cyl", (0.0, -0.01, 1.745), (0.150, 0.155, 0.045), "#14161c"),                  # cap band
           ("sphere", (0.0, -0.01, 1.80), (0.150, 0.155, 0.105), "#f4f6fa"),                 # white crown
           ("box", (0.0, -0.17, 1.775), (0.15, 0.09, 0.014), "#14161c", (8, 0, 0)),          # peak
           ("cyl", (0.0, -0.16, 1.82), (0.034, 0.034, 0.012), "#e2b53a", (90, 0, 0)),        # gold anchor badge
           ("box", (0.0, -0.118, 1.04), (0.30, 0.03, 0.40), "#1f2c40"),                      # heavy sweater band
           ("box", (0.0, -0.140, 1.34), (0.06, 0.012, 0.05), "#c8ccd4")],                     # collar button
    head=1.22, hand=1.12, shoulder=1.12, chest=1.10, belly=0.12, bellyx=0.05, girth=(1.12, 1.04, 1.10), lean=(-1, -3, 2, -4),
    face=dict(nose=(1.25, 1.2), jaw=1.05, brow_w=1.5, brow_tilt=-3, smile=0.2, age=3, moustache=True),
    hair=[("sphere", (0.0, -0.17, 4.22), (0.22, 0.13, 0.15), "#e8e8ee"),                    # full white beard
          ("sphere", (0.17, -0.12, 4.32), (0.10, 0.14, 0.17), "#e8e8ee"),
          ("sphere", (-0.17, -0.12, 4.32), (0.10, 0.14, 0.17), "#e8e8ee"),
          ("sphere", (0.0, -0.22, 4.13), (0.14, 0.10, 0.13), "#e8e8ee"),
          ("sphere", (0.28, 0.14, 4.46), (0.05, 0.09, 0.12), "#e8e8ee"), ("sphere", (-0.28, 0.14, 4.46), (0.05, 0.09, 0.12), "#e8e8ee")],
    extras=[])
FACE["grigor"] = dict(iris="#3a5a78", brow="#d8d8e0", lips="#b0685c", plips="#a2605a", female=False, hair="#e8e8ee", glasses=None)
LABEL["grigor"] = "Grigor"

# --- Mrs. Valdez: balcony neighbour, 60s. Small, round-shouldered, purple shawl, giant gold hoop earrings, silver-streaked updo.
B["valdez"] = dict(
    model="Female_Dress", height=1.57,
    colours={"Dress": "#d86a70", "Hair": "#3a3036", "Skin": "#c98e6a", "Shoes": "#4a2a3a"},
    props=[("torus", (0.093, 0.0, 1.575), (0.052, 0.052, 0.008), "#f2c94c", (0, 90, 0)),     # giant hoop earrings
           ("torus", (-0.093, 0.0, 1.575), (0.052, 0.052, 0.008), "#f2c94c", (0, 90, 0)),
           ("torus", (0.0, -0.035, 1.43), (0.062, 0.062, 0.008), "#f6e6c0")],                 # shell necklace
    head=1.30, hand=1.10, shoulder=0.98, chest=1.04, belly=0.10, bellyx=0.04, bust=0.12, hips=0.10, girth=(1.08, 1.08, 1.0), lean=(4, 6, 6, -5),
    face=dict(nose=(1.0, 1.1), jaw=0.95, brow_w=1.0, brow_tilt=1, smile=0.45, age=2),
    hair=[("sphere", (0.0, 0.10, 4.98), (0.17, 0.17, 0.17), "#3a3036"),                       # tall updo
          ("sphere", (0.0, 0.14, 4.82), (0.30, 0.25, 0.13), "#3a3036"),
          ("sphere", (0.12, -0.14, 4.90), (0.06, 0.14, 0.06), "#cfc8d4", (0, 20, 0)),          # silver streak
          ("sphere", (0.29, 0.06, 4.52), (0.08, 0.12, 0.13), "#3a3036"), ("sphere", (-0.29, 0.06, 4.52), (0.08, 0.12, 0.13), "#3a3036")],
    extras=[("Torso", "sphere", (0.0, 0.02, 3.55), (0.66, 0.36, 0.26), "#6a3a9a"),            # purple shawl: soft shoulder cape
            ("Torso", "sphere", (0.0, -0.10, 3.10), (0.20, 0.20, 0.44), "#8a56c0"),            # V of the shawl hanging in front
            ("Torso", "sphere", (0.46, -0.02, 3.18), (0.16, 0.26, 0.36), "#6a3a9a"),           # side lobes
            ("Torso", "sphere", (-0.46, -0.02, 3.18), (0.16, 0.26, 0.36), "#6a3a9a")])
FACE["valdez"] = dict(iris="#2a1a0e", brow="#3a3036", lips="#a8404e", plips="#9a3a48", female=True, hair="#3a3036", glasses=None)
LABEL["valdez"] = "Mrs. Valdez"

# --- Guard Pruitt: VaultTech guard, bored, soft, oversized cap, grey-blue uniform, crossword on a clipboard. Lou's diner regular.
B["pruitt"] = dict(
    model="Male_Shirt", height=1.76,
    colours={"Shirt": "#8f98a6", "Shirt2": "#eef0f3", "Pants": "#3a404c", "Hair": "#3a281c", "Hair2": "#3a281c", "Skin": "#e2b08a",
             "Shoes": "#25252b", "Socks": "#222222", "Eyes": "#202020"},
    props=[("sphere", (0.0, -0.01, 1.82), (0.178, 0.182, 0.118), "#5e6676"),                 # OVERSIZED peaked cap, too big
           ("cyl", (0.0, -0.01, 1.745), (0.176, 0.18, 0.040), "#3a404c"),
           ("box", (0.0, -0.19, 1.78), (0.22, 0.13, 0.016), "#2a2f3a", (14, 0, 0)),           # long peak pulled low
           ("cyl", (0.0, -0.17, 1.835), (0.036, 0.036, 0.012), "#e2b53a", (90, 0, 0)),        # gold V badge on the cap
           ("cyl", (0.12, -0.14, 1.20), (0.040, 0.040, 0.012), "#e2b53a", (90, 0, 0)),        # oversize chest badge
           ("box", (0.0, -0.13, 1.12), (0.02, 0.02, 0.30), "#e2b53a"),                         # gold tie
           ("box", (-0.17, -0.22, 1.00), (0.17, 0.014, 0.22), "#f4f2e8", (0, 0, -10)),         # crossword on a clipboard
           ("box", (-0.17, -0.232, 1.00), (0.15, 0.004, 0.20), "#6a6e78", (0, 0, -10))],       # (grid)
    head=1.26, hand=1.12, shoulder=0.96, chest=1.04, belly=0.18, bellyx=0.08, girth=(1.12, 1.0, 1.06), lean=(5, 9, 9, -6),
    face=dict(nose=(1.0, 1.0), jaw=1.0, brow_w=1.0, brow_tilt=-3, smile=-0.1, age=1, stubble=True),
    hair=[("sphere", (0.28, 0.10, 4.48), (0.05, 0.10, 0.13), "#3a281c"), ("sphere", (-0.28, 0.10, 4.48), (0.05, 0.10, 0.13), "#3a281c"),
          ("sphere", (0.0, 0.30, 4.55), (0.22, 0.08, 0.12), "#3a281c")],
    extras=[])
FACE["pruitt"] = dict(iris="#3a2a1c", brow="#3a281c", lips="#b0685c", plips="#a2605a", female=False, hair="#3a281c", glasses=None)
LABEL["pruitt"] = "Guard Pruitt"

# --- Kessler: VaultTech bridge guard (M15). Tall, thin, stiff as a rule book, oversized badge, worried.
B["kessler"] = dict(
    model="Male_Suit", height=1.90,
    colours={"Shirt": "#9aa3ad", "Pants": "#59616e", "Details": "#e2b53a", "TieTexture": "#e6e9ee", "Hair": "#9a7440", "Skin": "#f0c4a4",
             "Eyes": "#202024", "Shoes": "#1c1f26"},
    props=[("cyl", (0.0, -0.01, 1.745), (0.150, 0.155, 0.05), "#59616e"),                      # stiff cap, tall front
           ("sphere", (0.0, -0.01, 1.80), (0.150, 0.155, 0.10), "#7a8392"),
           ("box", (0.0, -0.17, 1.765), (0.15, 0.09, 0.014), "#1c1f26", (4, 0, 0)),
           ("cyl", (0.0, -0.16, 1.80), (0.034, 0.034, 0.012), "#e2b53a", (90, 0, 0)),
           ("cyl", (0.12, -0.15, 1.22), (0.058, 0.058, 0.012), "#e2b53a", (90, 0, 0)),         # OVERSIZED badge
           ("box", (0.12, -0.158, 1.22), (0.025, 0.004, 0.025), "#59616e")],
    head=1.12, hand=1.12, shoulder=0.92, chest=0.90, belly=0.0, girth=(0.88, 0.92, 0.88), lean=(-3, -6, -3, -6), arms_len=1.06,
    face=dict(nose=(0.9, 1.25), jaw=0.88, brow_w=0.9, brow_tilt=6, smile=-0.25, age=0),
    hair=[("sphere", (0.28, 0.12, 4.46), (0.05, 0.09, 0.11), "#9a7440"), ("sphere", (-0.28, 0.12, 4.46), (0.05, 0.09, 0.11), "#9a7440")],
    extras=[])
FACE["kessler"] = dict(iris="#4a6a88", brow="#9a7440", lips="#b0685c", plips="#a2605a", female=False, hair="#9a7440", glasses=None)
LABEL["kessler"] = "Kessler"

# --- Nella Bellini: Rosa's younger sister, runs the bakery counter (docs: cameo in Ch2/5; proposed here so the bakery has a face).
B["nella"] = dict(
    model="Female_Casual", height=1.66,
    colours={"Shirt": "#8fb59a", "Pants": "#4a5266", "Hair": "#4a3a34", "HairBase": "#4a3a34", "Skin": "#e2b490", "Shoes": "#5a3a2a", "Socks": "#f2efe6"},
    props=[("box", (0, -0.125, 0.98), (0.30, 0.03, 0.56), "#f1e4c2"),                          # floury baker's apron
           ("box", (0, -0.115, 1.30), (0.17, 0.03, 0.11), "#f1e4c2"),
           ("box", (0.05, -0.145, 0.90), (0.08, 0.004, 0.07), "#e8dcc4"),                       # flour handprint
           ("sphere", (0.0, 0.005, 1.775), (0.155, 0.162, 0.105), "#c75a48"),                   # terracotta bandana
           ("sphere", (0.0, 0.17, 1.70), (0.05, 0.05, 0.045), "#c75a48")],                      # bandana knot at the back
    head=1.30, hand=1.12, shoulder=0.98, chest=1.0, belly=0.06, bust=0.08, hips=0.12, girth=(1.02, 1.04, 1.12), lean=(0, 0, 0, 0),
    face=dict(nose=(0.95, 1.0), jaw=0.95, brow_w=1.0, brow_tilt=2, smile=0.6, age=1),
    hair=[("sphere", (0.0, 0.18, 4.60), (0.30, 0.20, 0.22), "#4a3a34"), ("sphere", (0.12, -0.12, 4.86), (0.05, 0.14, 0.05), "#b8b0b8", (0, 20, 0)),
          ("sphere", (0.29, 0.10, 4.45), (0.07, 0.11, 0.15), "#4a3a34"), ("sphere", (-0.29, 0.10, 4.45), (0.07, 0.11, 0.15), "#4a3a34")],
    extras=[])
FACE["nella"] = dict(iris="#4a3020", brow="#4a3a34", lips="#b0505a", plips="#a84850", female=True, hair="#4a3a34", glasses=None)
LABEL["nella"] = "Nella"

ORDER = ["ines", "teo", "grigor", "valdez", "pruitt", "kessler", "nella"]


def inject():
    """Register the new entries in the real modules (memory only)."""
    import char_build
    import cast
    import face_cfg
    for n in ORDER:
        char_build.B[n] = B[n]
        cast.CHARS[n] = dict(label=LABEL[n], model=B[n]["model"], height=B[n]["height"], colours=B[n]["colours"], props=[])
        face_cfg.FACE[n] = FACE[n]
