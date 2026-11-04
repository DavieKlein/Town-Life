# Approved design proposals (scratch scripts)

Kept so the approved looks can be ported into the real pipeline.

- `cast/`: character proposal renders (Rosa, Dex shop/VaultMart, Mr. Pimm, Big Lou, Victor Vault, robot Valet). Colours and props per character in `cdef.py`; `render.py` renders idle sprites, portraits via `dm.py`/`dm_lib.py`. `scene_stairs_room.py` is a copy of tools/scene.py with `market_stairs`, `stairs_up`, `room_upstairs` (stairs in the Corner Market storeroom, the room above the shop). Paths inside point to /tmp/claude-0/s42 and need adjusting.
- `minigames/`: PIL mock-ups of "STOCK IT!" and "PLATE RUSH" (see docs/story_chapter1.md section 6).
