import sys
sys.path.insert(0,'/tmp/claude-0/s42')
import q2
from PIL import Image
names=sys.argv[1:]
S=6
W=Image.new('RGBA',(len(names)*(3*32+64+40)*S//1 //1,64*S+0),(120,130,120,255)) if False else None
sheet=Image.new('RGBA',(len(names)*(32*3+70)*4,64*4+20),(122,132,122,255))
x=0
for n in names:
    sp=q2.sprites(n,2)
    for f in ('s','sw','se'):
        sheet.alpha_composite(sp[f].resize((128,256),Image.NEAREST),(x,10)); x+=128
    pt=q2.portrait(n,64).resize((256,256),Image.NEAREST) if False else None
sheet.convert('RGB').save('quick.png')
