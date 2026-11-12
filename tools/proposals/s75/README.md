# s75 proposal: new Old Block residents (looks only; nothing added to the game)

Characters (docs: `docs/story_chapter1.md` Residents table + 3B.2a, `docs/old_block_design.md` section 6):
Ines Okoro, Teo, Grigor, Mrs. Valdez, Guard Pruitt, Kessler, Nella Bellini (humans, unique `char_build`-style builds in `res_build.py`),
TRENCH-E 3 (64x64 robot), Duchess (corgi, 32x32), Captain (parrot, 32x32).

| File | What |
|------|------|
| `res_build.py` | build table (height, head/hand, girth, lean, face, hair, props) + `inject()` (adds entries to `char_build.B`, `cast.CHARS`, `face_cfg.FACE` in memory only) |
| `res_char.py` | Blender: renders a human with the REAL `blender_cast.py` (V1 Soft, s75 hands); facings s/se/e, idle + one walk frame; yellow rubber gloves for Ines |
| `res_props.py` | Blender: TRENCH-E 3, Duchess, Captain from primitives, same sprite camera and light |
| `res_post.py` | quantize (real face pass for humans), lineup at 3x, in-game mock (needs an s74 `crop.py` window: `python3 ../s74/mock.py --window 31 22`) |
| `parts_res.py`, `res_portraits.py` | 128 px portraits (neutral + happy) with the real `tools/portraits` painter; one parts module, dispatch on `kind` |

Run: `blender -b -noaudio --python res_char.py -- ines OUT/r_ines 4 24`, `... res_props.py -- robot OUT/r_robot 8 24`, `python3 res_post.py OUT sprites|lineup|mock CROP`, `python3 res_portraits.py OUT/portraits.png`.
Doc conflicts: Teo is a 10-year-old skateboarder in the docs (no wheelchair; "door ramp" = his skateboard ramp / bridge made from a door). Nella is only a cameo in the docs.
