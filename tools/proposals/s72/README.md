# s72 proposal: unique body builds + more realistic faces (proposal only, no game asset changed)

- `s72_build.py`  per-character build table (height, head/hand size, shoulders, belly/bust/hips, limb girth, lean/posture, hair volume pieces, clothing silhouettes)
- `s72_char.py`   Blender renderer (copies blender_cast/blender_actor/face_kit logic, V1 Soft light + smooth + 1 subdivision, walk frames from tools/actor_cycles.py)
- `s72_post.py`   quantization with the real face_pass (+ small additions: lashes, bags, lower lip, smile creases), lineup / face sheet / walk sheet, diner mock
- `run.py OUT render|sprites|compose [names] [--ss=4 --samples=48]`
Frames stay 32x64 (feet at 16,54); each sheet keeps 11 free colours + 3 reserved face colours + outline.
