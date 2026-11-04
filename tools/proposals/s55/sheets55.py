import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
P="/tmp/claude-0/s55/keep/por"; O="/tmp/claude-0/s55"
F=lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", n)
BG=(236,226,200); DARK=(24,28,56); GOLD=(248,208,96); WHITE=(240,240,248)
CH=["player","mia","rosa","victor"]; NAME={"player":"You (Sam)","mia":"Mia","rosa":"Rosa","victor":"Victor Vault"}
EX=["neutral","happy","angry","sad","surprised"]
def load(pre,n,c,e):
    im=Image.open(f"{P}/{pre}_{n}_{c}_{e}.png").convert("RGBA"); bg=Image.new("RGBA",im.size,BG+(255,)); bg.alpha_composite(im); return bg.convert("RGB")
os.makedirs(f"{O}/individual",exist_ok=True)
# main sheet: 4 rows x 5 expressions, 2x (256px)
sc=2; s=128*sc; pad=10
W=pad+ (s+pad)*5 ; H=70+ (s+pad+26)*4
sh=Image.new("RGB",(W,H),DARK); d=ImageDraw.Draw(sh)
d.text((pad,12),"Portraits 128x128, own parametric painter, quantized to 2 x 15 colours per character (2x)",font=F(24),fill=GOLD)
for i,e in enumerate(EX): d.text((pad+i*(s+pad)+s//2,52),e,font=F(20),fill=WHITE,anchor="mm")
for j,c in enumerate(CH):
    y=70+j*(s+pad+26)
    for i,e in enumerate(EX):
        sh.paste(load("q2",128,c,e).resize((s,s),Image.NEAREST),(pad+i*(s+pad),y))
    d.text((pad,y+s+2),NAME[c],font=F(20),fill=GOLD)
sh.save(f"{O}/portraits.png")
for c in CH:
    for e in EX:
        load("q2",128,c,e).resize((512,512),Image.NEAREST).save(f"{O}/individual/portrait_{c}_{e}.png")
# comparison: old 64x64 (s54 option A) vs 96 vs 128, and 1 palette vs 2 palettes
old="/tmp/claude-0/s54/out/portraits"
cmp=Image.new("RGB",(1080,760),DARK); d=ImageDraw.Draw(cmp)
d.text((20,12),"Size and palette options (old shown 3x, others 2x; same character)",font=F(22),fill=GOLD)
x=20
cols=[("old 64x64 (s54, 15 col)",None),("96x96, 2 palettes","q2_96"),("128x128, 1 palette (15 col)","q1_128"),("128x128, 2 palettes (30 col)","q2_128")]
y0=50
for k,(lab,pre) in enumerate(cols):
    xx=20+k*265
    d.text((xx,y0),lab,font=F(13),fill=WHITE)
    for r,(c,e) in enumerate((("mia","neutral"),("victor","angry"))):
        if pre is None:
            im=Image.open(f"{old}/{c}_A_{e}.png").convert("RGBA"); bg=Image.new("RGBA",im.size,BG+(255,)); bg.alpha_composite(im); im=bg.convert("RGB"); z=3
            cmp.paste(im.resize((im.width*z,im.height*z),Image.NEAREST),(xx,y0+22+r*360))
        else:
            n=int(pre.split("_")[1]); a,b=pre.split("_"); im=load(a,n,c,e); z=2 if n==128 else 2
            z=2
            cmp.paste(im.resize((im.width*z,im.height*z),Image.NEAREST),(xx,y0+22+r*360))
cmp.save(f"{O}/portrait_options.png")
# stats: tiles
def tiles(im):
    a=np.asarray(im.convert("RGBA"))
    idx=a  # compare RGBA tiles
    T=[];
    for ty in range(16):
        for tx in range(16):
            T.append(a[ty*8:ty*8+8,tx*8:tx*8+8])
    return T
st={}
for c in CH:
    base=tiles(Image.open(f"{P}/q2_128_{c}_neutral.png"))
    uniq=set()
    for t in base:
        k=t.tobytes(); kf=t[:,::-1].tobytes(); kv=t[::-1].tobytes(); kb=t[::-1,::-1].tobytes()
        uniq.add(min(k,kf,kv,kb))
    d_={}
    for e in EX[1:]:
        cur=tiles(Image.open(f"{P}/q2_128_{c}_{e}.png"))
        d_[e]=sum(1 for a_,b_ in zip(base,cur) if a_.tobytes()!=b_.tobytes())
    empty=sum(1 for t in base if t[...,3].max()==0)
    st[c]=dict(unique_tiles_with_flips=len(uniq),empty=empty,changed_vs_neutral=d_)
print(json.dumps(st,indent=1))
json.dump(st,open(f"{O}/keep/tile_stats.json","w"),indent=1)
