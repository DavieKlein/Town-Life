import sys
sys.argv = ["x","--","player","/tmp/claude-0/s54/r/dbg","2","8","A","none"]
exec(open("/tmp/claude-0/s54/keep/faces.py").read().split("# ---------------------------------------------------------------- camera / lights")[0])
build_face(EXPR["neutral"])
print("EX",EX,"EZ",EZ)
for o in FEATS[:40]:
    print(o.name, tuple(round(v,3) for v in (arm.matrix_world.inverted()@o.matrix_world.translation)), tuple(round(v,3) for v in o.scale))
