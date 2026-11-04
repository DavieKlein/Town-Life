import sys; sys.path.insert(0,'/tmp/claude-0/s54/keep')
from quant import *
import glob
from PIL import Image
c,o=sys.argv[1],sys.argv[2]
names=["s_0","sw_0","se_0","e_0"]
fr=[sprite_frame(f"/tmp/claude-0/s54/r/{c}_{o}/{n}.png",4,32,64) for n in names]
pal,idx=quantize_sheet(fr)
ims=[to_image(i,pal).crop((0,0,32,28)) for i in idx]
s=Image.new("RGBA",(32*4,28),(110,150,90,255))
for i,im in enumerate(ims): s.alpha_composite(im,(i*32,0))
s.resize((s.width*8,s.height*8),Image.NEAREST).save(sys.argv[3])
