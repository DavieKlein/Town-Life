import sys
from PIL import Image
d=sys.argv[1]
p=[Image.open(f"{d}/portrait_{e}.png") for e in ["neutral","happy","angry","sad"]]
s=Image.new("RGBA",(1024,256),(36,40,80,255))
for i,im in enumerate(p): s.alpha_composite(im,(i*256,0))
s.save(sys.argv[2])
