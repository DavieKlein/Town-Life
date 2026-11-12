# Old Block build notes (s75 helper handover)

Status: phase A (engine) committed (6ca5303). Phase B code is written but NOT yet integrated into tools/scene.py / blender_render.py
(a City Centre render was running; those files must not change while Blender runs).

## Done (committed)
- 80 story flags (+sneak_route, barrier_moved, door_bridge), save v4 (max_maps 16, 64 deposit spots), per-map deposit spots
  (`pickup_spot::map`), gated solids (`gate_rect`, `gate_open[]`, `map_info::gates`, `field::_update_gates` in src/tl_field_oldblock.cpp;
  sneak gate also opens while mission X1 is current), shop-set table in tl_field.cpp (market, vaultmart, diner, bakery, lane, stall),
  flag-driven sprites (`tl_map_sprites`, art tools/map_sprites.py, 4 barrier pieces + laundry variants + door bridge),
  new interactable kinds (sign/flap/hatch/shop_*/chess/garden/hoop/washer/oven).

## Written, uncommitted / not integrated
- tools/scene_oldblock.py (Old Block + 4 interiors, OB_FURNITURE, NEW_MATERIALS), tools/furniture.py (new catalog pieces),
  tools/interactions.py (old_block + interiors), tools/deposit.py (24 OB spots), tools/critters.py, tools/scene.py (CC edits + `Scene.gates`).
- Integration patch (apply when no render runs): scratchpad patch75.py does: `Scene.gate()` in scene.py, append
  `import scene_oldblock; scene_oldblock.register(SCENES)` at the end of scene.py, and in blender_render.py one line
  `MATERIALS.update(__import__('scene_oldblock').NEW_MATERIALS)  # s75-materials` before `def main()`.
- Checks: scratchpad check75.py (flood fill: sneak gate opens the whole map; barrier+bridge opens the front; all warps land on free cells).

## TODO
Render old_block + 4 interiors, run build_assets (writes world data incl. gate tables), ROM build, headless tests, CLAUDE.md update, push.
