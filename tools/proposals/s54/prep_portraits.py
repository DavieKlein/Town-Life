import sys, os; sys.path.insert(0,'/tmp/claude-0/s54/keep')
from quant import *
OUT="/tmp/claude-0/s54/out/portraits"; os.makedirs(OUT,exist_ok=True)
def q(path):
    fr=[sprite_frame(path,4,64,64)]
    # portraits: one palette per portrait, 14 colours + outline (as write_sprite_sheet does)
    pal,idx=quantize_sheet(fr)
    return to_image(idx[0],pal)
for c in ["player","mia","rosa","victor"]:
    for o in ["base","A","C1"]:
        d=f"/tmp/claude-0/s54/r/{c}_{o}"
        for e in ["neutral","happy","angry","sad"]:
            p=f"{d}/portrait_{e}.png"
            if os.path.exists(p): q(p).save(f"{OUT}/{c}_{o}_{e}.png")
print(len(os.listdir(OUT)))
