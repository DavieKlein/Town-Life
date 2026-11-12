"""
s75: TRENCH-E 3 (VaultTech trench robot), Duchess (corgi) and Captain (parrot), built from primitives, rendered with the same
sprite camera and V1 Soft light as the cast. Nothing in the game is touched.

  blender -b -noaudio --python tools/proposals/s75/res_props.py -- <robot|duchess|captain> <outdir> <ss> <samples>

robot:   64x64 frames, feet (32, 50); facings s, se, e; frames idle, dig_up, dig_down  -> <facing>_<frame>.png
duchess: 32x32 frames facing right (e), feet (16, 23); frames stand, walkA, walkB, sit
captain: 32x32 frame facing right, feet (16, 23); frames perch, flap
"""
import bpy, sys, os, math
from mathutils import Vector

TOOLS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, TOOLS)
from blender_render import rgb

CELL_M = 0.75
FACINGS = {"s": 45, "se": 90, "e": 135}
which, out_dir, ss, samples = sys.argv[sys.argv.index("--") + 1:][:4]
ss, samples = int(ss), int(samples)
os.makedirs(out_dir, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = samples; sc.cycles.use_denoising = False
sc.render.film_transparent = True; sc.render.filter_size = 1.4
sc.view_settings.view_transform = "Standard"
sc.render.image_settings.color_mode = "RGBA"


def mat(col, rough=0.6, emit=0.0, metal=0.0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(col); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = rgb(col); b.inputs["Emission Strength"].default_value = emit
    return m


def prim(kind, pos, size, col, parent, rot=(0, 0, 0), rough=0.6, emit=0.0, metal=0.0):
    if kind == "box": bpy.ops.mesh.primitive_cube_add(size=1)
    elif kind == "cyl": bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, vertices=32)
    elif kind == "cone": bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=1, vertices=32)
    elif kind == "sphere": bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16)
    o = bpy.context.active_object
    o.scale = size; o.location = pos; o.rotation_euler = [math.radians(a) for a in rot]
    if kind != "box":
        bpy.ops.object.shade_smooth()
    else:
        bev = o.modifiers.new("b", "BEVEL"); bev.width = min(size) * 0.18; bev.segments = 2
    o.data.materials.append(mat(col, rough, emit, metal)); o.parent = parent
    return o


def empty(parent, loc=(0, 0, 0)):
    e = bpy.data.objects.new("e", None); sc.collection.objects.link(e); e.parent = parent; e.location = loc
    return e


WHITE, GREY, DARK, GOLD, HAZ = "#eceff2", "#9aa3ad", "#3c424c", "#e2b53a", "#f2c21c"


def build_robot(parent, dig):
    """small tracked trench digger, ~0.95 m tall, 1.1 m long, front = -y."""
    for sx in (-1, 1):
        prim("box", (sx * 0.30, 0, 0.14), (0.22, 1.05, 0.28), DARK, parent, rough=0.9)                      # tracks
        prim("cyl", (sx * 0.30, -0.50, 0.14), (0.14, 0.14, 0.23), DARK, parent, rot=(0, 90, 0), rough=0.9)  # track ends (rounded)
        prim("cyl", (sx * 0.30, 0.50, 0.14), (0.14, 0.14, 0.23), DARK, parent, rot=(0, 90, 0), rough=0.9)
        prim("cyl", (sx * 0.30, -0.30, 0.14), (0.07, 0.07, 0.24), GREY, parent, rot=(0, 90, 0))              # road wheels
        prim("cyl", (sx * 0.30, 0.10, 0.14), (0.07, 0.07, 0.24), GREY, parent, rot=(0, 90, 0))
        prim("cyl", (sx * 0.30, 0.38, 0.14), (0.07, 0.07, 0.24), GREY, parent, rot=(0, 90, 0))
    prim("box", (0, 0.02, 0.36), (0.62, 0.90, 0.26), WHITE, parent)                                         # chassis
    prim("box", (0, -0.47, 0.40), (0.50, 0.04, 0.12), HAZ, parent)                                          # hazard bumper
    prim("box", (0, 0.10, 0.60), (0.50, 0.62, 0.30), WHITE, parent)                                         # body
    prim("box", (0, 0.10, 0.47), (0.52, 0.64, 0.05), GOLD, parent)                                          # gold stripe
    prim("box", (0, 0.43, 0.62), (0.40, 0.04, 0.20), GREY, parent)                                          # engine grille
    prim("sphere", (0, -0.10, 0.82), (0.24, 0.26, 0.15), WHITE, parent)                                     # sensor dome
    prim("cyl", (0, -0.31, 0.83), (0.075, 0.075, 0.03), "#10202c", parent, rot=(90, 0, 0), rough=0.2)        # camera eye
    prim("cyl", (0, -0.328, 0.83), (0.045, 0.045, 0.012), "#35d6ff", parent, rot=(90, 0, 0), emit=2.0)
    prim("cyl", (0.17, 0.30, 0.82), (0.012, 0.012, 0.34), DARK, parent)                                     # antenna
    prim("sphere", (0.17, 0.30, 1.00), (0.04, 0.04, 0.04), "#ff9a1a", parent, emit=2.5)                      # amber lamp
    prim("box", (0.0, -0.40, 0.66), (0.20, 0.02, 0.07), "#10202c", parent)                                   # chest panel "TRENCH-E 3"
    prim("box", (0.0, -0.412, 0.66), (0.14, 0.005, 0.012), "#35d6ff", parent, emit=1.5)
    # boom + bucket arm (front); rotation about the shoulder
    sh = empty(parent, (0.0, -0.30, 0.66)); sh.rotation_euler = (math.radians(-dig), 0, 0)
    prim("box", (0.0, -0.25, 0.10), (0.10, 0.40, 0.09), HAZ, sh, rot=(-18, 0, 0))                            # boom
    el = empty(sh, (0.0, -0.50, 0.02)); el.rotation_euler = (math.radians(dig * 1.2 + 25), 0, 0)
    prim("box", (0.0, -0.17, -0.07), (0.08, 0.30, 0.08), GOLD, el, rot=(-35, 0, 0))                          # stick
    prim("box", (0.0, -0.36, -0.20), (0.26, 0.20, 0.14), GREY, el, rot=(-35, 0, 0), metal=0.6, rough=0.4)    # bucket
    prim("box", (0.0, -0.45, -0.25), (0.26, 0.03, 0.04), GOLD, el, rot=(-35, 0, 0))                          # teeth bar


def build_duchess(parent, pose):
    """corgi ~0.33 m high, fawn with white chest/legs, big upright ears. front = -y."""
    F, W, D = "#d9954a", "#f6ede0", "#3a2a1e"
    sit = pose == "sit"
    if sit:
        prim("sphere", (0, 0.10, 0.20), (0.17, 0.26, 0.20), F, parent, rot=(-35, 0, 0))
        prim("sphere", (0, -0.05, 0.19), (0.12, 0.12, 0.18), W, parent)
        for sx in (-1, 1): prim("cyl", (sx * 0.06, -0.12, 0.08), (0.04, 0.04, 0.16), W, parent)
        hz, hy = 0.42, -0.10
    else:
        prim("sphere", (0, 0.02, 0.27), (0.15, 0.30, 0.15), F, parent)                             # long round body
        prim("sphere", (0, -0.14, 0.23), (0.12, 0.16, 0.12), W, parent)                            # white chest
        prim("sphere", (0, 0.04, 0.17), (0.13, 0.24, 0.07), W, parent)                             # white belly
        prim("sphere", (0, 0.32, 0.28), (0.06, 0.05, 0.06), F, parent)                             # tail nub
        a = {"stand": (0, 0, 0, 0), "walkA": (28, -28, -28, 28), "walkB": (-28, 28, 28, -28)}[pose]
        for (sx, py, ang) in ((-1, -0.15, a[0]), (1, -0.15, a[1]), (-1, 0.20, a[2]), (1, 0.20, a[3])):
            pv = empty(parent, (sx * 0.075, py, 0.19)); pv.rotation_euler = (math.radians(ang), 0, 0)
            prim("cyl", (0, 0, -0.095), (0.036, 0.036, 0.19), W if py < 0 else F, pv)
            prim("sphere", (0, -0.015, -0.19), (0.045, 0.06, 0.03), W, pv)
        hz, hy = 0.38, -0.30
    prim("sphere", (0, hy, hz), (0.115, 0.125, 0.11), F, parent)                                  # head
    prim("sphere", (0, hy - 0.10, hz - 0.035), (0.062, 0.095, 0.055), W, parent)                   # muzzle
    prim("sphere", (0, hy - 0.185, hz - 0.015), (0.03, 0.025, 0.025), D, parent)                   # nose
    for sx in (-1, 1):
        prim("cone", (sx * 0.075, hy + 0.01, hz + 0.15), (0.06, 0.03, 0.15), F, parent, rot=(0, sx * 12, 0))     # big ears
        prim("cone", (sx * 0.075, hy - 0.005, hz + 0.145), (0.035, 0.012, 0.11), "#f0b4a0", parent, rot=(0, sx * 12, 0))
        prim("sphere", (sx * 0.055, hy - 0.095, hz + 0.045), (0.022, 0.018, 0.022), D, parent)    # eyes
    prim("box", (0, hy - 0.04, hz + 0.01), (0.03, 0.12, 0.012), W, parent)                        # white blaze
    prim("torus" if False else "cyl", (0, hy + 0.10, hz - 0.075), (0.10, 0.10, 0.025), "#c8327a", parent, rot=(75, 0, 0))   # magenta collar (Ines's colours)


def build_captain(parent, flap):
    """green parrot on a perch (~0.32 m). front = -y."""
    G, R, Y = "#2fa84a", "#d8352a", "#f2c21c"
    prim("cyl", (0, 0, 0.02), (0.012, 0.18, 0.012), "#6a4a2a", parent, rot=(0, 0, 90))            # perch bar (along x)
    prim("cyl", (0, 0, 0.0), (0.01, 0.01, 0.04), "#6a4a2a", parent)
    prim("sphere", (0, 0.02, 0.17), (0.075, 0.09, 0.13), G, parent, rot=(-12, 0, 0))              # body
    prim("sphere", (0, -0.06, 0.15), (0.05, 0.05, 0.08), "#e8f0a0", parent)                       # pale chest
    prim("cone", (0, 0.11, 0.07), (0.05, 0.02, 0.2), "#2a7ac8", parent, rot=(165, 0, 0))          # long blue tail
    prim("sphere", (0, -0.03, 0.30), (0.062, 0.062, 0.062), R, parent)                            # red head
    prim("sphere", (0, -0.085, 0.285), (0.03, 0.04, 0.04), Y, parent, rot=(20, 0, 0))             # beak
    for sx in (-1, 1):
        prim("sphere", (sx * 0.04, -0.07, 0.315), (0.014, 0.012, 0.014), "#ffffff", parent)
        prim("sphere", (sx * 0.044, -0.077, 0.315), (0.008, 0.006, 0.008), "#101010", parent)
        if flap:
            prim("sphere", (sx * 0.11, 0.03, 0.22), (0.015, 0.07, 0.10), G, parent, rot=(0, sx * 55, sx * 10))
        else:
            prim("sphere", (sx * 0.07, 0.03, 0.16), (0.018, 0.08, 0.11), "#238a3a", parent, rot=(-10, 0, 0))


def cam(fw, fh, fx, fy):
    sc.render.resolution_x = fw * ss; sc.render.resolution_y = fh * ss
    c = bpy.data.cameras.new("cam"); c.type = "ORTHO"; c.sensor_fit = "HORIZONTAL"
    co = bpy.data.objects.new("cam", c); sc.collection.objects.link(co); sc.camera = co
    c.ortho_scale = fw * math.cos(math.radians(45)) * CELL_M / 16
    co.rotation_euler = (math.radians(60), 0, math.radians(45))
    a = fw / 2 - fx; b = fh / 2 - fy
    ux, uy = b + a / 2, b - a / 2
    target = Vector((ux / 16 * CELL_M, -uy / 16 * CELL_M, 0))
    fwd = Vector((-math.sin(math.radians(45)) * math.sin(math.radians(60)), math.cos(math.radians(45)) * math.sin(math.radians(60)), -0.5))
    co.location = target - fwd * 40


world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.66, 0.8, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.5
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.0; sun.angle = math.radians(30)
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
so.rotation_euler = Vector((-0.25, 0.7, -0.65)).normalized().to_track_quat("-Z", "Y").to_euler()

pivot = empty(None)
if which == "robot":
    cam(64, 64, 32, 50)
    for fr, dig in (("idle", 8), ("dig_up", 28), ("dig_down", -12)):
        for o in list(pivot.children_recursive):
            bpy.data.objects.remove(o)
        build_robot(pivot, dig)
        for f, ang in FACINGS.items():
            pivot.rotation_euler = (0, 0, math.radians(ang))
            sc.render.filepath = os.path.join(out_dir, f"{f}_{fr}.png"); bpy.ops.render.render(write_still=True)
elif which == "duchess":
    cam(32, 32, 16, 23)
    for fr in ("stand", "walkA", "walkB", "sit"):
        for o in list(pivot.children_recursive):
            bpy.data.objects.remove(o)
        build_duchess(pivot, fr)
        pivot.rotation_euler = (0, 0, math.radians(135))
        sc.render.filepath = os.path.join(out_dir, f"e_{fr}.png"); bpy.ops.render.render(write_still=True)
else:
    cam(32, 32, 16, 23)
    for fr, fl in (("perch", False), ("flap", True)):
        for o in list(pivot.children_recursive):
            bpy.data.objects.remove(o)
        build_captain(pivot, fl)
        pivot.rotation_euler = (0, 0, math.radians(135))
        sc.render.filepath = os.path.join(out_dir, f"e_{fr}.png"); bpy.ops.render.render(write_still=True)
