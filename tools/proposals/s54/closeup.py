import bpy, sys, math
from mathutils import Vector
name=sys.argv[sys.argv.index("--")+1]; out=sys.argv[sys.argv.index("--")+2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath="/home/user/Town-Life/art_source/quaternius_characters/%s.fbx"%name)
sc=bpy.context.scene
sc.render.engine="CYCLES"; sc.cycles.samples=24; sc.cycles.use_denoising=False; sc.render.resolution_x=sc.render.resolution_y=400
sc.render.film_transparent=False
for m in bpy.data.materials:
    if m.use_nodes:
        b=m.node_tree.nodes["Principled BSDF"]; b.inputs["Alpha"].default_value=1
arm=next(o for o in sc.objects if o.type=="ARMATURE")
arm.data.pose_position="REST"
w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True; w.node_tree.nodes["Background"].inputs["Strength"].default_value=1.0
sun=bpy.data.lights.new("s","SUN"); sun.energy=3; so=bpy.data.objects.new("s",sun); sc.collection.objects.link(so); so.rotation_euler=(0.8,0,0.5)
cam=bpy.data.cameras.new("c"); cam.type="ORTHO"; cam.ortho_scale=1.0
co=bpy.data.objects.new("c",cam); sc.collection.objects.link(co); sc.camera=co
for i,yaw in enumerate([0,40,90]):
    r=4
    co.location=(r*math.sin(math.radians(-yaw)),-r*math.cos(math.radians(yaw)),4.45)
    co.rotation_euler=(math.radians(90),0,math.radians(-yaw))
    sc.render.filepath=f"{out}_{i}.png"; bpy.ops.render.render(write_still=True)
