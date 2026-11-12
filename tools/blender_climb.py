"""
Town Life - the ladder climb of the player (s77, runs INSIDE Blender, called by build_assets.build_player_climb).

  blender -b -noaudio --python tools/blender_climb.py -- <fbx> <out_dir> <supersample> <samples> <colours_json>

4 frames of 64x64, player seen from BEHIND (facing 'n'), hands alternating up the rungs, knees alternately lifted:
  <out_dir>/climb_<i>.png     (feet at (32, 58))
Reuses the helpers (Rig, setup_camera) of tools/blender_acts.py by executing the part of that file before `def main`, so
blender_acts.py itself stays untouched (its art cache key is a hash of the file)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
src = open(os.path.join(HERE, "blender_acts.py")).read()
exec(compile(src[:src.index("def main():")], os.path.join(HERE, "blender_acts.py"), "exec"), globals())

FEET_Y2 = 58


def climb_pose(i):
    # (high arm, left/right) per frame: R up, both mid, L up, both mid; the knee of the opposite leg lifts
    hi_r = [1, 0, 0, 0][i]
    hi_l = [0, 0, 1, 0][i]
    knee_l = [1, 0, 0, 0][i] * 0.0 + [0.9, 0.3, 0.0, 0.3][i]
    knee_r = [0.0, 0.3, 0.9, 0.3][i]
    ops = [("Torso", "X", -6), ("Head", "X", -6)]
    for side, hi, knee in (("R", hi_r, knee_r), ("L", hi_l, knee_l)):
        sgn = -1 if side == "R" else 1
        ops += [("UpperArm." + side, "X", -100 - 70 * hi), ("UpperArm." + side, "Z", -sgn * 10),
                ("LowerArm." + side, "X", -12 - 10 * (1 - hi)),
                ("UpperLeg." + side, "X", -45 * knee), ("LowerLeg." + side, "X", 130 * knee), ("Foot." + side, "X", -20 * knee)]
    return ops


def main2():
    argv = sys.argv[sys.argv.index("--") + 1:]
    fbx, out_dir = argv[0], argv[1]
    global SS
    SS = int(argv[2])
    samples = int(argv[3])
    colours = json.loads(argv[4])
    os.makedirs(out_dir, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.render.film_transparent = True
    sc.render.filter_size = 1.0
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.color_mode = "RGBA"
    char72.soft_render(sc)
    L = char72.load(sc, "player", fbx, colours)
    BD = L["BD"]
    arm, root, idle = L["arm"], L["root"], L["idle"]
    char72.dress(L, sc)
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()
    setup_camera(FRAME_W, FRAME_H, FEET_X, FEET_Y2)
    world = bpy.data.worlds.new("world")
    sc.world = world
    world.use_nodes = True
    char72.soft_world(world)
    char72.soft_sun(sc)
    arm.animation_data.action = idle
    sc.frame_set(1)
    char72.tweak(arm, BD)
    bpy.context.view_layer.update()
    arm.animation_data.action = None
    rig = Rig(arm)
    root.rotation_euler = (0, 0, math.radians(FACINGS["n"]))
    for i in range(4):
        rig.pose(climb_pose(i))
        sc.render.filepath = os.path.join(out_dir, f"climb_{i}.png")
        bpy.ops.render.render(write_still=True)


main2()
