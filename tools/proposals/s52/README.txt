s52 room above Corner Market (proposal). Scene code: rooms52.py (scenes market_stairs, market_stairs_gate, room_attic = A, room_plain = B).
Use: copy rooms52.py to tools/, add "import rooms52" at the END of tools/scene.py (registers the scenes in SCENES), full_check.py -> tools/proposals/s50/.
Render check: python3 tools/proposals/s50/full_check.py OUT name:scene:all  (crop box x0,y0,x1,y1 for part of a scene).
Stairs patch: market_stairs is built by patching the source of scene.market_v2 (staff table moved, poster removed, stairs added); when approved,
apply the same edits directly inside market_v2 (storeroom block) and drop the _patched_market hack.
