"""
Town Life - walk / run / idle cycle sampling for the character renderers (runs INSIDE Blender; used by blender_actor.py
and blender_cast.py).

Cycles are sampled evenly over one full loop of the Quaternius action (sub-frame accurate), starting at the PASSING POSE
(left foot planted, right foot swinging past it): the sprite sheets then start and end close to the upright idle pose, so
idle -> walk and walk -> idle need no extra art, and walk <-> run keep the same foot phase when the game switches.
"""
import bpy

WALK_FRAMES = 12            # sprites per walk cycle and facing
RUN_FRAMES = 12             # sprites per run cycle and facing
IDLE_FRAMES = 6             # sprites per idle (breathing) loop and facing


def action_named(suffix):
    for a in bpy.data.actions:
        if a.name.endswith(suffix):
            return a
    raise RuntimeError("action not found: " + suffix)


def set_frame(frame):
    bpy.context.scene.frame_set(int(frame // 1), subframe=frame % 1)


def _feet(arm, frame):
    set_frame(frame)
    bpy.context.view_layer.update()
    l, r = arm.pose.bones["Foot.L"], arm.pose.bones["Foot.R"]
    return l.head.y, r.head.y, l.head.z, r.head.z


def passing_frame(arm, action):
    """Action frame (float) where the swinging right foot passes the planted left foot (left foot lower)."""
    arm.animation_data.action = action
    f0, f1 = action.frame_range
    best, best_d = f0, 1e9
    for k in range(int((f1 - f0) * 4)):
        f = f0 + k / 4.0
        ly, ry, lz, rz = _feet(arm, f)
        d = abs(ly - ry) + (0 if lz < rz else 10)
        if d < best_d:
            best, best_d = f, d
    return best


def cycle_frames(action, start, n):
    """n action frames spread evenly over one loop, beginning at `start` (wrapping inside the action range)."""
    f0, f1 = action.frame_range
    cycle = f1 - f0                    # the last frame repeats the first one
    return [f0 + ((start - f0 + i * cycle / n) % cycle) for i in range(n)]
