from PIL import Image, ImageDraw, ImageFont
import os, shutil
O="/tmp/claude-0/s55"
F=lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", n)
DARK=(24,28,56); GOLD=(248,208,96); WHITE=(240,240,248); GREY=(170,178,210)
os.makedirs(f"{O}/individual",exist_ok=True)
# room
room=Image.open(f"{O}/out55/room_b2_q.png").convert("RGB")
mocks=[Image.open(f"{O}/mock_tmp/mock_b2_{n}.png") for n in ("arrive","bed","window")]
for n,m in zip(("arrive","bed","window"),mocks): m.resize((720,480),Image.NEAREST).save(f"{O}/individual/room_B2_mock_{n}.png")
room.resize((room.width*4,room.height*4),Image.NEAREST).save(f"{O}/individual/room_B2_render.png")
W=1100; sc=3
rz=room.resize((room.width*3,room.height*3),Image.NEAREST)
H=60+rz.height+30+ (160*2+20)*1 + 40
im=Image.new("RGB",(W,H),DARK); d=ImageDraw.Draw(im)
d.text((20,14),"Room above the shop, variant B2 (calmer furniture)",font=F(26),fill=GOLD)
im.paste(rz,((W-rz.width)//2,60))
y=60+rz.height+10
d.text((20,y),"In game (240x160, 2x): arrive from the stairs / bed menu / window",font=F(18),fill=WHITE)
for i,m in enumerate(mocks):
    im.paste(m.resize((480,320),Image.NEAREST).crop((0,0,480,320)).resize((350,233),Image.NEAREST),(20+i*360,y+30))
im=im.crop((0,0,W,y+30+233+20)); im.save(f"{O}/room_B2.png")
# gates
a=Image.open(f"{O}/out55/gate_a_q.png").convert("RGB"); b=Image.open(f"{O}/out55g/gate_b_q.png").convert("RGB")
z=4
g=Image.new("RGB",(a.width*z*2+60,a.height*z+110),DARK); d=ImageDraw.Draw(g)
d.text((20,10),"VaultTech staff gate at the foot of the stairs (4x, real renderer + quantizer)",font=F(24),fill=GOLD)
g.paste(a.resize((a.width*z,a.height*z),Image.NEAREST),(20,80)); g.paste(b.resize((b.width*z,b.height*z),Image.NEAREST),(40+a.width*z,80))
d.text((20,50),"Variant A: sturdy steel bar gate, gold V plate, card reader",font=F(17),fill=WHITE)
d.text((40+a.width*z,50),"Variant B: roll-down shutter in a steel frame, gold V",font=F(17),fill=WHITE)
g.save(f"{O}/gate.png")
a.resize((a.width*z,a.height*z),Image.NEAREST).save(f"{O}/individual/gate_A.png"); b.resize((b.width*z,b.height*z),Image.NEAREST).save(f"{O}/individual/gate_B.png")
# gate 1x in the 240x160 view
for n,q in (("A",a),("B",b)):
    scr=Image.new("RGB",(240,160),(6,6,12)); scr.paste(q.crop((0,0,192,128)),(24,0)); scr.resize((720,480),Image.NEAREST).save(f"{O}/individual/gate_{n}_1x_view.png")
print("ok")
