"""Blender entry point: renders the proposal scene with the REAL tools/blender_render.py (not edited).
  blender -b -noaudio --python render.py -- old_block <floor|objects> OUT.png SCALE SAMPLES [x0,y0,x1,y1] [id]
Registers the new materials and the scene in-process only."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import blender_render as br  # noqa: E402
import scene as scn  # noqa: E402
import oldblock  # noqa: E402
br.MATERIALS.update(oldblock.NEW_MATERIALS)
scn.SCENES.insert(0, oldblock.old_block)
br.main()
