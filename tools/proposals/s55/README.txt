s55 proposal scripts (work dir /tmp/claude-0/s55, tools/ = copy of the s52 tools + patches).
 rooms55.py            scenes market_gate_a, market_gate_b (staff gate variants + red STAFF ONLY sign), room_b2 (calm furniture). Replaces rooms52.py
                       (add "import rooms55" at the end of tools/scene.py; scene.py patch: Scene.text(..., bold=False)).
 blender_render_s55.patch  new materials (duvet_blue, blanket_mustard, pillow_white, rug_terra, sign_red, sign_white, shutter_grey, hazard_black)
                       + bold text (DejaVu Sans Bold, offset, letter spacing) for text prims with bold=True.
 full_check.py         real renderer + quantizer crops (unchanged from s50/s52).
 mock55_room.py        in-game mocks of the room (arrive / bed / window).
 Portraits: pt.py (painting toolkit), chars.py (face/eye/mouth/brow model + 5 expressions), parts_<char>.py (hair, clothes, accessories per
 character), hairlib.py, bodies.py, build_all.py (render + quantize: 2 palettes x 15 colours or 1 palette x 15 colours, 128 and 96 px),
 sheets55.py (sheets + tile stats), mock55.py (dialogue layouts 1 and 2). Run: cd keep; python3 build_all.py; python3 sheets55.py; python3 mock55.py
