import sys, os, json; sys.path.insert(0,'/tmp/claude-0/s54/keep')
from bpass import *
CH=["player","mia","rosa","victor"]
FAC=["s","sw","w","nw","n","ne","e","se"]
NAMES=[f"{f}_0" for f in FAC]+[f"{f}_{i}" for f in ["s","sw","se","e"] for i in range(1,9)]
OUT="/tmp/claude-0/s54/out/sprites"
def save(c,key,pal,idx):
    d=f"{OUT}/{c}_{key}"; os.makedirs(d,exist_ok=True)
    for n,i in zip(NAMES,idx): to_image(i,pal).save(f"{d}/{n}.png")
for c in CH:
    for key,src,face in [("base","base",False),("A","A",False),("B","A",True),("C1","C1",True),("C2","C2",True)]:
        if not os.path.exists(f"/tmp/claude-0/s54/r/{c}_{src}/se_8.png"): print("missing",c,src); continue
        if face:
            pal,idx=build_B(c,src,NAMES)
        else:
            fr=[sprite_frame(f"/tmp/claude-0/s54/r/{c}_{src}/{n}.png",4,32,64) for n in NAMES]
            pal,idx=quantize_sheet(fr)
        save(c,key,pal,idx); print("ok",c,key,flush=True)
