"""
s75: renders one NEW resident with the REAL tools/blender_cast.py pipeline (char72 builds, V1 Soft look, s75 hands).
Nothing in the game is touched: the build table from res_build.py is injected in memory, then blender_cast.py runs unchanged.

  blender -b -noaudio --python tools/proposals/s75/res_char.py -- <name> <outdir> <ss> <samples>

Env: TL_FACINGS=s,se,e (default here), RES_WALK=<index 0..11> renders only that one walk frame (written as <facing>_w0.png).
"""
import os
import sys
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import res_build  # noqa: E402

res_build.inject()
os.environ.setdefault("TL_FACINGS", "s,se,e")

import actor_cycles as cyc  # noqa: E402
import char72  # noqa: E402

_cf = cyc.cycle_frames
WALK_IDX = int(os.environ.get("RES_WALK", "3"))


def one_walk_frame(*a, **k):
    fr = _cf(*a, **k)
    return [fr[WALK_IDX % len(fr)]]


cyc.cycle_frames = one_walk_frame

_dress = char72.dress


def dress_with_gloves(L, sc):
    face = _dress(L, sc)
    BD = L["BD"]
    if BD.get("gloves"):
        import bpy
        from mathutils import Vector
        arm = L["arm"]
        arm.data.pose_position = "REST"
        bpy.context.view_layer.update()
        for sd in "LR":
            pal = arm.data.bones["Palm." + sd]
            tip = arm.data.bones["Fingers.%s_end" % sd]
            mid = (Vector(pal.head_local) + Vector(tip.tail_local)) / 2
            char72.add_extra(arm, "Palm." + sd, "sphere", tuple(mid), (0.125, 0.125, 0.125), BD["gloves"])
            char72.add_extra(arm, "Palm." + sd, "sphere", tuple(Vector(pal.head_local)), (0.105, 0.105, 0.105), BD["gloves"])
        arm.data.pose_position = "POSE"
        bpy.context.view_layer.update()
    return face


char72.dress = dress_with_gloves

argv = sys.argv[sys.argv.index("--") + 1:]
sys.argv = sys.argv[:sys.argv.index("--") + 1] + argv[:4] + ["sprites"]
runpy.run_path(os.path.join(TOOLS, "blender_cast.py"), run_name="__blender_cast__")
