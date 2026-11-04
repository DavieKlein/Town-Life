import bpy, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
for name in ["Male_LongSleeve","Female_Casual","Female_Alternative","Male_Suit"]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath="/home/user/Town-Life/art_source/quaternius_characters/%s.fbx"%name)
    sc=bpy.context.scene
    arm=next(o for o in sc.objects if o.type=="ARMATURE")
    arm.data.pose_position="REST"; bpy.context.view_layer.update()
    o=next(o for o in sc.objects if o.type=="MESH" and o.name in("BaseHuman","Female"))
    me=o.data
    print("==",name,"mesh matrix",[round(x,3) for x in o.matrix_world.to_scale()], o.matrix_world.translation[:])
    vg={g.name:g.index for g in o.vertex_groups}; hi=vg["Head"]
    eyes={}
    for p in me.polygons:
        if me.materials[p.material_index].name.split(".")[0]=="Eyes" and p.center.z>3:
            s=1 if p.center.x>0 else -1
            eyes.setdefault(s,[]).append(p.center)
    for s,l in eyes.items():
        c=sum(l,Vector())/len(l); print(" eye",s,tuple(round(v,3) for v in c),"n",len(l),"rad",round(max((v-c).length for v in l),3))
    bv=BVHTree.FromPolygons([v.co[:] for v in me.vertices],[p.vertices[:] for p in me.polygons])
    for z in (4.2,4.3,4.4,4.5,4.6):
        h=bv.ray_cast(Vector((0,-3,z)),Vector((0,1,0)))
        print("  front y at x=0 z=%.1f:"%z, h[0] and round(h[0].y,3), "mat", h[2] and me.materials[me.polygons[h[2]].material_index].name)
    # head bone info
    b=arm.data.bones["Head"]; print(" head bone head",tuple(round(v,2) for v in b.head_local),"tail",tuple(round(v,2) for v in b.tail_local))
    # scale keys on Head
    for a in bpy.data.actions:
        if a.name.endswith("_Idle") or a.name.endswith("_Walk"):
            ks=[fc for fc in a.fcurves if fc.data_path=='pose.bones["Head"].scale']
            print(" ",a.name,"head scale curves",len(ks), [round(kp.co[1],2) for kp in ks[0].keyframe_points][:3] if ks else "")
