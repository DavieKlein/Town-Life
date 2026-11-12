"""Blender entry for the s77 sewer proposal: renders the REAL tools/blender_render.py pipeline on the proposal scenes.
  blender -b -noaudio --python render.py -- <ident> <floor|objects> OUT.png SCALE SAMPLES [x0,y0,x1,y1]
ident = a real scene (city_centre, old_block) or a proposal scene from sewer.py (sewer, cc_a, cc_b, ob_open, ob_closed).
Nothing in the game is changed: materials and scenes are registered in-process only."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import blender_render as br  # noqa: E402
import scene as scn  # noqa: E402
import sewer  # noqa: E402
br.MATERIALS.update(sewer.NEW_MATERIALS)
ident = sys.argv[sys.argv.index("--") + 1]
if ident in sewer.FUNCS:
    scn.SCENES[:] = [sewer.FUNCS[ident]]      # only this scene (the renderer builds scenes until it finds the ident)
br.main()
