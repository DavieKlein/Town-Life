import bpy, sys
from mathutils import Vector
for name in ["Male_LongSleeve","Female_Casual","Female_Alternative","Male_Suit"]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath="/home/user/Town-Life/art_source/quaternius_characters/%s.fbx"%name)
    sc=bpy.context.scene
    arm=next(o for o in sc.objects if o.type=="ARMATURE")
    print("==",name,"arm scale",arm.matrix_world.to_scale(), [b.name for b in arm.data.bones if 'ead' in b.name or 'eck' in b.name])
    arm.data.pose_position="REST"; bpy.context.view_layer.update()
    for o in sc.objects:
        if o.type!="MESH": continue
        me=o.data
        print(" mesh",o.name,len(me.vertices),[m.name for m in me.materials], [vg.name for vg in o.vertex_groups][:3])
        vg={g.name:g.index for g in o.vertex_groups}
        if "Head" in vg:
            hi=vg["Head"]
            pts=[v.co for v in me.vertices if any(g.group==hi and g.weight>0.6 for g in v.groups)]
            if pts:
                print("  head bbox",[ (round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)) for i in range(3)])
            # material of head faces
            from collections import Counter
            c=Counter()
            for p in me.polygons:
                if all(any(g.group==hi and g.weight>0.6 for g in me.vertices[v].groups) for v in p.vertices):
                    c[me.materials[p.material_index].name]+=1
            print("  head face mats",c)
