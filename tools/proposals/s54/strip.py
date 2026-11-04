import sys; from PIL import Image
c=sys.argv[1]; f=sys.argv[2]
keys=["base","A","B","C1","C2"]
import os
cells=[]
for k in keys:
    p=f"/tmp/claude-0/s54/out/sprites/{c}_{k}/{f}.png"
    if os.path.exists(p): cells.append(Image.open(p).convert("RGBA").crop((0,0,32,34)))
s=Image.new("RGBA",(32*len(cells),34),(110,150,90,255))
for i,im in enumerate(cells): s.alpha_composite(im,(i*32,0))
s.resize((s.width*6,s.height*6),Image.NEAREST).save(sys.argv[3])
