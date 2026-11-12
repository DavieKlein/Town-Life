"""
Town Life - per-character BODY BUILDS (owner-approved s72 proposal; data only, no Blender needed to import).
Used by blender_cast.py, blender_actor.py / blender_acts.py (player) through tools/char72.py and by face_pass.py (face parameters).

Units: `height` metres; mesh-space numbers are in Quaternius mesh units (the 1.78 m body is 4.84 units tall, so 1 unit = 0.37 m).

  model     Quaternius rig (male bases Male_*, female bases Female_*)
  height    final body height (m)
  head,hand head / hand scale on the Head / Palm bones (game player = 1.28 / 1.12 since s75)
  shoulder  Torso x scale (chest + shoulder width; player V2 = 1.14)
  chest     Torso y scale (chest depth)
  belly     forward bulge of the belly (mesh units, z 2.2-3.1), bellyx = side growth of the belly band
  bust      chest bulge (z ~3.35)
  hips      pelvis / butt width growth (fraction)
  girth     (torso, legs, arms) radial growth around the bone axis
  lean      degrees forward (+) / backward (-) on Abdomen, Torso, Neck, Head
  arms_len  extra arm length (UpperArm bone y scale)
  face      nose size, jaw, age cues, brow shape (see s72_face.py)
  hair      list of hair volume pieces (head-local mesh coords: x +left of character, y -front / +back, z up; head is z 4.12-4.84)
  extras    clothing silhouettes as (bone, kind, loc, size, colour[, rot degrees]) in mesh coords
  props     cast.py-style props in metres for the 1.78 m body (replace the cast.py list when given)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cast as cdef  # noqa: E402

PLAYER_COLOURS = {"Shirt": "#2c5fb8", "Pants": "#a98655", "Hair": "#4a2a18", "Skin": "#f0c09a",
                  "Shoes": "#3a2a22", "Socks": "#f2efe6"}

B = {}

B["player"] = dict(
    model="Male_LongSleeve", height=1.78, colours=PLAYER_COLOURS, props=[], v2=True,
    head=1.28, hand=1.12, shoulder=1.14, chest=1.0, belly=0.0, girth=(1.0, 1.0, 1.0), lean=(1, 2, 1, -2),
    face=dict(nose=(1.0, 1.0), jaw=1.0, brow_w=1.0, brow_tilt=0, smile=0.25, age=0),
    hair=[("sphere", (0.0, -0.05, 4.82), (0.27, 0.31, 0.12), "#4a2a18"),                  # a bit of volume on top
          ("sphere", (0.10, -0.24, 4.78), (0.17, 0.09, 0.07), "#4a2a18", (0, 20, 0))],    # side-swept fringe
    extras=[])

B["mia"] = dict(
    model="Female_Casual", height=1.66,
    colours={"Shirt": "#2a9a96", "Pants": "#3c4a66", "Hair": "#c8622a", "HairBase": "#c8622a", "Skin": "#f2c8a4", "Shoes": "#3a2a22",
             "Socks": "#f2efe6"},
    props=[],
    head=1.30, hand=1.10, shoulder=0.93, chest=0.95, belly=0.0, bust=0.05, hips=0.10, girth=(0.96, 0.98, 0.9), lean=(0, 0, 1, -1),
    face=dict(nose=(0.8, 0.8), jaw=0.9, brow_w=0.9, brow_tilt=4, smile=0.5, age=0),
    hair=[("sphere", (0.0, 0.16, 4.72), (0.30, 0.20, 0.17), "#c8622a"),                    # back volume
          ("sphere", (0.0, 0.40, 4.55), (0.12, 0.12, 0.12), "#c8622a"),                    # ponytail root
          ("sphere", (0.0, 0.50, 4.30), (0.11, 0.12, 0.26), "#c8622a"),                    # ponytail
          ("sphere", (0.0, 0.52, 4.06), (0.08, 0.09, 0.14), "#c8622a"),
          ("sphere", (0.0, 0.40, 4.58), (0.075, 0.075, 0.05), "#e8b038"),                  # hair tie
          ("sphere", (-0.12, -0.25, 4.80), (0.20, 0.09, 0.075), "#c8622a", (0, -20, 0))],  # side bangs
    extras=[])

B["rosa"] = dict(
    model="Female_Dress", height=1.54,
    colours={"Dress": "#7a2236", "Hair": "#c4c4cc", "Skin": "#eabf9c", "Shoes": "#2e2420"},
    props=[("torus", (0, -0.035, 1.40), (0.075, 0.075, 0.009), "#f4f0e8")],               # pearls (glasses are fitted by the face kit)
    head=1.32, hand=1.10, shoulder=1.0, chest=1.12, belly=0.16, bellyx=0.06, bust=0.10, hips=0.10, girth=(1.16, 1.18, 1.08), lean=(2, 4, 4, -3),
    face=dict(nose=(1.0, 1.1), jaw=1.0, brow_w=1.0, brow_tilt=-2, smile=0.3, age=2),
    hair=[("sphere", (0.0, 0.18, 4.95), (0.12, 0.12, 0.11), "#c4c4cc"),                    # grey bun
          ("sphere", (0.0, 0.14, 4.80), (0.30, 0.24, 0.12), "#c4c4cc"),
          ("sphere", (0.29, 0.05, 4.50), (0.08, 0.12, 0.13), "#c4c4cc"),                   # side curls
          ("sphere", (-0.29, 0.05, 4.50), (0.08, 0.12, 0.13), "#c4c4cc")],
    extras=[("Torso", "sphere", (0.0, -0.1, 3.60), (0.40, 0.25, 0.20), "#7a2236")])         # fuller bosom under the dress

B["dex"] = dict(
    model="Male_Shirt", height=1.72,
    colours=dict(cdef.CHARS["dex"]["colours"]),
    props=[("box", (0, -0.118, 1.02), (0.25, 0.03, 0.42), "#2f7a45"),                       # green apron (narrow, he is thin)
           ("box", (0.09, -0.139, 1.15), (0.07, 0.01, 0.04), "#f0e0a0")],
    head=1.24, hand=1.12, shoulder=0.90, chest=0.88, belly=0.0, girth=(0.84, 0.88, 0.86), lean=(4, 7, 8, -6), arms_len=1.10,
    face=dict(nose=(0.9, 1.15), jaw=0.85, brow_w=1.0, brow_tilt=-4, smile=0.1, age=0, stubble=True),
    hair=[("sphere", (0.0, -0.14, 4.98), (0.22, 0.22, 0.13), "#2a1c18", (-25, 0, 0)),     # tall messy quiff
          ("sphere", (0.12, -0.08, 5.02), (0.13, 0.15, 0.09), "#2a1c18"),
          ("sphere", (0.0, 0.05, 4.80), (0.29, 0.30, 0.11), "#2a1c18")],
    extras=[])

B["dex_vault"] = dict(B["dex"])
B["dex_vault"].update(colours=dict(cdef.CHARS["dex_vault"]["colours"]),
                      props=[("box", (0, -0.125, 1.20), (0.05, 0.02, 0.34), "#e2b53a"), ("box", (0.10, -0.128, 1.30), (0.07, 0.01, 0.04), "#e2b53a")])

B["pimm"] = dict(
    model="Male_LongSleeve", height=1.62,
    colours={"Shirt": "#a98d5c", "Pants": "#4a4036", "Hair": "#f2f2ee", "Skin": "#efb7a0", "Shoes": "#3d3026", "Socks": "#e8e8e0", "Eyes": "#202020"},
    props=[("sphere", (0.0, -0.03, 1.80), (0.158, 0.162, 0.105), "#5a3f26"),             # flat cap
           ("box", (0, -0.15, 1.83), (0.19, 0.10, 0.016), "#41301d", (8, 0, 0)),
           ("torus", (0, -0.02, 1.455), (0.09, 0.09, 0.03), "#a8312f"),                    # red scarf
           ("cyl", (-0.30, -0.10, 0.40), (0.012, 0.012, 0.80), "#5a3d22")],               # walking stick
    head=1.24, hand=1.10, shoulder=0.88, chest=0.92, belly=0.07, girth=(0.92, 0.84, 0.84), lean=(9, 14, 20, -24),
    face=dict(nose=(1.1, 1.2), jaw=0.9, brow_w=1.25, brow_tilt=-3, smile=-0.1, age=3),
    hair=[("sphere", (0.29, 0.17, 4.40), (0.045, 0.07, 0.07), "#f2f2ee"),                  # white tufts below the cap
          ("sphere", (-0.29, 0.17, 4.40), (0.045, 0.07, 0.07), "#f2f2ee"),
          ("sphere", (0.0, 0.33, 4.45), (0.22, 0.08, 0.09), "#f2f2ee")],
    extras=[("Torso", "tcone", (0, 0.02, 2.55), (0.70, 0.58, 0.75), "#a98d5c"),            # baggy cardigan hem
            ("Hips", "tcone", (0, 0.0, 1.0), (0.45, 0.45, 1.0), "#4a4036")])                 # trousers hang loose... (hidden if not used)
B["pimm"]["extras"] = []

B["lou"] = dict(
    model="Male_Casual", height=1.72,
    colours={"Shirt": "#f4f1ea", "Pants": "#566074", "Hair": "#3a2a1e", "Skin": "#e6b48a", "Shoes": "#2d2d2d", "Socks": "#eeeeee"},
    props=[("box", (0, -0.245, 1.00), (0.38, 0.03, 0.46), "#b83a32"),                      # red apron, flat plane over the belly
           ("box", (0, -0.20, 1.30), (0.20, 0.03, 0.11), "#b83a32"),                       # bib
           ("cyl", (0, 0.01, 1.765), (0.112, 0.112, 0.09), "#fbfbfb"),                     # chef hat band
           ("sphere", (0, 0.01, 1.865), (0.155, 0.155, 0.105), "#fbfbfb")],                # puffy top
    head=1.20, hand=1.18, shoulder=1.20, chest=1.12, belly=0.30, bellyx=0.15, hips=0.06, girth=(1.38, 1.26, 1.32), lean=(-4, -3, 3, 0),
    face=dict(nose=(1.35, 1.0), jaw=1.25, brow_w=1.15, brow_tilt=2, smile=0.8, age=1, moustache=True, jowls=True),
    hair=[("sphere", (0.28, 0.10, 4.50), (0.06, 0.11, 0.14), "#3a2a1e"),                  # short sides under the hat
          ("sphere", (-0.28, 0.10, 4.50), (0.06, 0.11, 0.14), "#3a2a1e")],
    extras=[])

B["victor"] = dict(
    model="Male_Suit", height=1.80,
    colours=dict(cdef.CHARS["victor"]["colours"], Skin="#b9774a"),       # deeper tan: the face stands out from the gold coat at 1x
    props=[("torus", (0, -0.07, 1.395), (0.125, 0.125, 0.014), "#f6d874", (62, 0, 0)),     # gold chain
           ("cyl", (0, -0.150, 1.27), (0.042, 0.042, 0.012), "#f6d874", (90, 0, 0)),
           ("cyl", (0.32, -0.08, 0.42), (0.014, 0.014, 0.84), "#f2c94c"),                  # gold cane
           ("sphere", (0.32, -0.08, 0.86), (0.04, 0.04, 0.04), "#f2c94c")],
    head=1.16, hand=1.12, shoulder=1.22, chest=1.12, belly=0.10, bust=0.10, girth=(1.12, 1.0, 1.12), lean=(-3, -9, 3, -6),
    face=dict(nose=(1.1, 1.35), jaw=1.15, brow_w=1.0, brow_tilt=5, smile=0.5, age=1, smirk=True),
    hair=[("sphere", (0.0, 0.06, 4.93), (0.27, 0.31, 0.15), "#f1ead4"),                   # swept-back volume
          ("sphere", (0.0, 0.32, 4.60), (0.22, 0.10, 0.17), "#f1ead4"),
          ("sphere", (0.26, 0.14, 4.66), (0.05, 0.10, 0.10), "#f1ead4"),
          ("sphere", (-0.26, 0.14, 4.66), (0.05, 0.10, 0.10), "#f1ead4")],
    extras=[("Torso", "sphere", (0.64, 0.0, 3.74), (0.20, 0.22, 0.12), "#d9ab36"),         # shoulder pads
            ("Torso", "sphere", (-0.64, 0.0, 3.74), (0.20, 0.22, 0.12), "#d9ab36")])

B["okafor"] = dict(
    model="Female_Alternative", height=1.70,
    colours=dict(cdef.CHARS["okafor"]["colours"]),
    props=[("torus", (0, -0.035, 1.43), (0.085, 0.085, 0.012), "#2a2a34"),                  # stethoscope
           ("cyl", (0.0, -0.14, 1.22), (0.03, 0.03, 0.012), "#c8d0d8", (90, 0, 0)),
           ("torus", (0.043, -0.125, 1.64), (0.036, 0.036, 0.005), "#2a2630", (90, 0, 0)),
           ("torus", (-0.043, -0.125, 1.64), (0.036, 0.036, 0.005), "#2a2630", (90, 0, 0)),
           ("box", (0, -0.125, 1.645), (0.03, 0.008, 0.008), "#2a2630")],
    head=1.24, hand=1.10, shoulder=1.0, chest=1.0, belly=0.0, bust=0.04, hips=0.07, girth=(1.0, 1.04, 0.95), lean=(-1, -3, -2, 1),
    face=dict(nose=(0.95, 0.95), jaw=0.95, brow_w=0.95, brow_tilt=2, smile=0.35, age=1),
    hair=[("sphere", (0.0, 0.06, 4.93), (0.20, 0.20, 0.13), "#1c1410"),                    # natural curls: cluster of puffs
          ("sphere", (0.17, 0.06, 4.84), (0.15, 0.17, 0.13), "#1c1410"),
          ("sphere", (-0.17, 0.06, 4.84), (0.15, 0.17, 0.13), "#1c1410"),
          ("sphere", (0.0, 0.22, 4.78), (0.25, 0.15, 0.17), "#1c1410"),
          ("sphere", (0.23, 0.14, 4.62), (0.10, 0.13, 0.15), "#1c1410"),
          ("sphere", (-0.23, 0.14, 4.62), (0.10, 0.13, 0.15), "#1c1410")],
    extras=[("Hips", "tcone", (0, 0.0, 2.25), (0.62, 0.52, 1.35), "#f6f8f6")])              # long white coat flaring over the hips
# long open lab coat: two front panels over the thighs + a back panel, to the knee, teal top / trousers show in the gap
B["okafor"]["extras"] = [("Hips", "box", (0.30, -0.01, 1.98), (0.20, 0.17, 0.60), "#f6f8f6", (0, 0, -4)),
                         ("Hips", "box", (-0.30, -0.01, 1.98), (0.20, 0.17, 0.60), "#f6f8f6", (0, 0, 4)),
                         ("Hips", "box", (0.0, 0.11, 2.0), (0.50, 0.12, 0.58), "#e6eeea")]


# ---------------------------------------------------------------------------------------------------- Old Block residents (s76)
# Owner-approved looks from tools/proposals/s75 (res_build.py). Ines has `gloves` (yellow rubber gloves, char72.dress).
# Human cast ids: ines, teo, grigor, valdez, pruitt, kessler, nella (cast.py CHARS/IDS, face_cfg.FACE).
# --- Ines Okoro: laundromat owner, 50s. Short, round, big smile, curler scarf, yellow rubber gloves, blue apron.
B["ines"] = dict(
    model="Female_Casual", height=1.62,
    colours={"Shirt": "#e2982c", "Pants": "#5a4a78", "Hair": "#1c1410", "HairBase": "#1c1410", "Skin": "#8a5836", "Shoes": "#2e2a32", "Socks": "#f2efe6"},
    props=[("sphere", (0, -0.150, 0.98), (0.165, 0.085, 0.27), "#3b6fb0"),                  # blue laundry apron over the belly (a real bulge, s76)
           ("box", (0, -0.190, 0.735), (0.30, 0.05, 0.045), "#274f86"),                     # darker hem band (shading reads at 1x)
           ("box", (0, -0.170, 1.135), (0.31, 0.055, 0.04), "#274f86"),                     # waist tie
           ("sphere", (0.14, -0.175, 1.12), (0.045, 0.03, 0.045), "#274f86"),               # tie bow
           ("box", (0, -0.158, 1.32), (0.17, 0.04, 0.12), "#3b6fb0"),                       # bib
           ("cyl", (0.075, -0.13, 1.45), (0.013, 0.013, 0.16), "#274f86"),                  # neck / shoulder straps
           ("cyl", (-0.075, -0.13, 1.45), (0.013, 0.013, 0.16), "#274f86"),
           ("box", (0.0, -0.208, 0.97), (0.12, 0.02, 0.09), "#f4f0e4"),                     # pocket
           ("box", (0.0, -0.212, 1.015), (0.12, 0.022, 0.012), "#274f86"),                  # pocket top seam
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

# --- Kessler: VaultTech bridge guard (M15). Tall, thin, stiff as a rule book, oversized badge, worried.
B["kessler"] = dict(
    model="Male_Suit", height=1.84,
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

# --- Nella Bellini: Rosa's younger sister, runs the bakery counter (docs: cameo in Ch2/5; proposed here so the bakery has a face).
B["nella"] = dict(
    model="Female_Casual", height=1.66,
    colours={"Shirt": "#8fb59a", "Pants": "#4a5266", "Hair": "#4a3a34", "HairBase": "#4a3a34", "Skin": "#e2b490", "Shoes": "#5a3a2a", "Socks": "#f2efe6"},
    props=[("sphere", (0, -0.105, 0.97), (0.158, 0.07, 0.29), "#f1e4c2"),                  # floury baker's apron with volume (s76)
           ("box", (0, -0.150, 0.70), (0.29, 0.045, 0.04), "#d6c398"),                      # hem band, a shade darker
           ("box", (0, -0.130, 1.10), (0.30, 0.05, 0.035), "#c9b585"),                      # waist tie
           ("box", (0, -0.118, 1.30), (0.17, 0.035, 0.11), "#f1e4c2"),                      # bib
           ("cyl", (0.07, -0.10, 1.43), (0.012, 0.012, 0.16), "#c9b585"),                   # straps
           ("cyl", (-0.07, -0.10, 1.43), (0.012, 0.012, 0.16), "#c9b585"),
           ("box", (0.05, -0.172, 0.88), (0.09, 0.012, 0.08), "#fbf6ea"),                   # flour handprint
           ("box", (-0.06, -0.170, 1.02), (0.07, 0.01, 0.05), "#fbf6ea"),                   # flour smear
           ("sphere", (0.0, 0.005, 1.775), (0.155, 0.162, 0.105), "#c75a48"),                   # terracotta bandana
           ("sphere", (0.0, 0.17, 1.70), (0.05, 0.05, 0.045), "#c75a48")],                      # bandana knot at the back
    head=1.30, hand=1.12, shoulder=0.98, chest=1.0, belly=0.06, bust=0.08, hips=0.12, girth=(1.02, 1.04, 1.12), lean=(0, 0, 0, 0),
    face=dict(nose=(0.95, 1.0), jaw=0.95, brow_w=1.0, brow_tilt=2, smile=0.6, age=1),
    hair=[("sphere", (0.0, 0.18, 4.60), (0.30, 0.20, 0.22), "#4a3a34"), ("sphere", (0.12, -0.12, 4.86), (0.05, 0.14, 0.05), "#b8b0b8", (0, 20, 0)),
          ("sphere", (0.29, 0.10, 4.45), (0.07, 0.11, 0.15), "#4a3a34"), ("sphere", (-0.29, 0.10, 4.45), (0.07, 0.11, 0.15), "#4a3a34")],
    extras=[])

ORDER = ["player", "mia", "rosa", "dex", "pimm", "lou", "victor", "okafor", "ines", "teo", "grigor", "valdez", "pruitt", "kessler", "nella"]
