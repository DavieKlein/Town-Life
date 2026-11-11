# s74 proposal: OLD BLOCK (design + visual proposal, nothing added to the game)

Design doc: `docs/old_block_design.md`. Previews: `previews/` (plan, 3 isometric key spots, in-game mock at 1x / 3x).
No game data, `SCENES`, `blender_render.py` or `build_assets.py` was changed: `render.py` imports the real renderer and registers the proposal scene and
its extra materials **in-process only**.

| File | What |
|------|------|
| `oldblock.py` | scene `old_block` (60 x 48 cells) built with the real `scene.py` helpers + new ones; `LAYOUT` / `LANE_CELLS` / `NEW_MATERIALS` |
| `data.py` | interactables, warps, NPC spots and mission hooks (shared by the plan and the doc) |
| `render.py` | Blender entry: `blender -b -noaudio --python render.py -- old_block <floor\|objects> OUT.png SCALE SAMPLES [x0,y0,x1,y1]` |
| `crop.py` | renders both layers of a crop in parallel and composes them like the game (grade, 5-bit colour): `python3 crop.py OUTPREFIX x0,y0,x1,y1 [samples]` |
| `plan.py` | top-down plan PNG with labels, interactables, NPCs, warps, mission hooks: `python3 plan.py OUT.png` |
| `mock.py` | 240x160 in-game mock (viewport + real HUD strip + real player sprite + stand-in resident) at 1x and 3x: `python3 mock.py --window px py` prints the crop box |
| `tilecount.py` | full-map render + the REAL quantizer (`build_assets.convert_layer`) to count unique tiles and the worst 31x21 window |

Image coordinates: `ix = 784 + (x - y) * 16`, `iy = 175 + (x + y) * 8 - z * 26.1`.
Needs `blender`, `python3-numpy`, Pillow; the worktree needs `butano/` present (build_assets imports its font).

## Open questions for the owner

Listed in the proposal report and at the end of `docs/old_block_design.md` section 14.
