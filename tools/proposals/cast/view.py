import sys
sys.path.insert(0,'/tmp/claude-0/s42')
import q2
from PIL import Image
names=sys.argv[1:]
sheet=Image.new('RGBA',(len(names)*340,330),(122,132,122,255))
for i,n in enumerate(names):
    sp=q2.sprites(n,4)
    sheet.alpha_composite(sp['s'].resize((96,192),Image.NEAREST),(i*340+0,60))
    sheet.alpha_composite(sp['se'].resize((96,192),Image.NEAREST),(i*340+90,60))
    sheet.alpha_composite(q2.portrait(n).resize((128,128),Image.NEAREST),(i*340+200,0))
    sheet.alpha_composite(Image.open(f'r/{n}/portrait.png').convert('RGBA').resize((128,128),Image.LANCZOS),(i*340+200,140))
sheet.convert('RGB').save('view.png')
