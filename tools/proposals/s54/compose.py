import sys, os, json
sys.path.insert(0,'/tmp/claude-0/s54/keep')
from PIL import Image, ImageDraw, ImageFont
import numpy as np
S="/tmp/claude-0/s54/out/sprites"; P="/tmp/claude-0/s54/out/portraits"; O="/tmp/claude-0/s54/out"
BG=(24,28,56); PANEL=(40,48,88); GOLD=(248,208,96); WHITE=(240,240,248); GREY=(170,178,210); GRASS=(104,150,90); CREAM=(240,232,208)
F=lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", n)
FR=lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", n)
W=1080
CH=["player","mia","rosa","victor"]; NAME={"player":"You","mia":"Mia","rosa":"Rosa","victor":"Victor Vault"}
OPT=["base","A","B","C1","C2"]; OPTN={"base":"Now","A":"A","B":"B","C1":"C1","C2":"C2"}
def spr(c,k,n):
    p=f"{S}/{c}_{k}/{n}.png"
    return Image.open(p).convert("RGBA") if os.path.exists(p) else None
def up(im,k): return im.resize((im.width*k,im.height*k),Image.NEAREST)
def canvas(h,bg=BG): return Image.new("RGB",(W,h),bg)
def text(d,xy,t,f,fill=WHITE,anchor="la"): d.text(xy,t,font=f,fill=fill,anchor=anchor)
def wrap(d,t,f,maxw):
    lines=[];cur=""
    for w in t.split(" "):
        n=(cur+" "+w).strip()
        if d.textlength(n,font=f)<=maxw: cur=n
        else: lines.append(cur);cur=w
    lines.append(cur);return lines
def para(d,x,y,t,f,maxw,fill=WHITE,lh=None):
    lh=lh or int(f.size*1.35)
    for l in wrap(d,t,f,maxw): d.text((x,y),l,font=f,fill=fill); y+=lh
    return y

# ----------------------------------------------------------------------------- 0 header + options
def fig_header():
    im=canvas(1000); d=ImageDraw.Draw(im)
    text(d,(30,24),"Town Life: faces proposal",F(44),GOLD)
    y=para(d,30,84,"The Quaternius heads are faceless low-poly blobs: at 46 px tall the whole face is about 7 x 8 pixels. Below: what each option gives, rendered through the real pipeline (Blender, 4x supersample, the build_assets quantizer, 15 colours + outline).",FR(25),W-60,GREY)
    rows=[("Now","current look: head 1.0x, no face features. Face = skin blob."),
          ("A","V2 proportions (head 1.28x, hands 1.38x) + modelled face (eye whites, iris, pupil, highlight, lashes, brows, nose shading, lips, inner ears, blush, hair strands + sheen). Pure Blender change; at sprite size the features blur away, the portrait gains a lot."),
          ("B","A + pixel pass after quantization: 1x2 eyes with a white corner, brow, mouth, blush, nose shade, hair highlight; positions come from 3D anchors projected per frame, so the face follows the walk bob. Needs 3 palette slots."),
          ("C1","Head 1.45x (chibi-ish, still natural) + B. Faces read best, body looks more cartoon."),
          ("C2","Characters 10 % taller (about 52 px, head 1.28x) + B. Fits the 32x64 frame; the world is built at 0.75 m per cell, so people become about 1.95 m.")]
    y+=14
    for k,t in rows:
        d.rounded_rectangle([30,y,W-30,y+20+len(wrap(d,t,FR(23),W-190))*32],radius=12,fill=PANEL)
        text(d,(46,y+10),k,F(34),GOLD)
        yy=para(d,150,y+12,t,FR(23),W-190,WHITE,32)
        y=yy+22
    im=im.crop((0,0,W,y+10)); return im

# ----------------------------------------------------------------------------- 1 actual size
def fig_actual():
    sc=3
    cwid=32*sc
    im=canvas(60+2*(64*sc+110)); d=ImageDraw.Draw(im)
    text(d,(30,14),"1. Actual size (shown 3x), idle facing the camera",F(30),GOLD)
    for ci,c in enumerate(CH):
        bx=24+(ci%2)*(W//2); by=70+(ci//2)*(64*sc+110)
        d.rectangle([bx,by,bx+W//2-30,by+64*sc+90],fill=(30,36,70))
        text(d,(bx+10,by+6),NAME[c],F(26),GOLD)
        for i,k in enumerate(OPT):
            s_=spr(c,k,"s_0")
            cell=Image.new("RGBA",(32,64),GRASS+(255,)); cell.alpha_composite(s_)
            x=bx+8+i*(cwid+6)
            im.paste(up(cell,sc).convert("RGB"),(x,by+44))
            text(d,(x+cwid//2,by+44+64*sc+6),OPTN[k],F(22),WHITE,"ma")
    return im

# ----------------------------------------------------------------------------- 2 close-up blocks
def fig_block(c, rows=("s_0","sw_0","se_0"), sc=5, crop=(0,0,32,36)):
    cw=(crop[2]-crop[0])*sc; ch=(crop[3]-crop[1])*sc
    pad=10
    im=canvas(60+len(rows)*(ch+pad)+20); d=ImageDraw.Draw(im)
    text(d,(30,12),f"2. Close-up (5x): {NAME[c]}   facings: front, 3/4 left, 3/4 right",F(30),GOLD)
    x0=(W-len(OPT)*(cw+pad))//2
    for i,k in enumerate(OPT):
        text(d,(x0+i*(cw+pad)+cw//2,52),OPTN[k],F(26),WHITE,"ma")
    for r,n in enumerate(rows):
        for i,k in enumerate(OPT):
            s=spr(c,k,n)
            if s is None: continue
            cell=Image.new("RGBA",(32,64),GRASS+(255,)); cell.alpha_composite(s)
            cell=cell.crop(crop)
            im.paste(up(cell,sc).convert("RGB"),(x0+i*(cw+pad),84+r*(ch+pad)))
    return im.crop((0,0,W,84+len(rows)*(ch+pad)+10))

# ----------------------------------------------------------------------------- 3 walk
def fig_walk(c="player"):
    sc=3
    fr=[1,3,5,7]
    rows=["s","sw","se"]
    cw,ch=32*sc,52*sc
    im=canvas(130+len(rows)*(ch+8)); d=ImageDraw.Draw(im)
    text(d,(30,14),"3. Walk cycle (frames 1,3,5,7 of 8, 3x)",F(30),GOLD)
    y=100
    for r,f in enumerate(rows):
        for oi,k in enumerate(["A","B"]):
            ox=24+oi*(W//2)
            if r==0: text(d,(ox,y-34),"A: 3D only" if k=="A" else "B: 3D + pixel pass",F(24),WHITE)
            for j,n in enumerate(fr):
                s_=spr(c,k,f"{f}_{n}")
                cell=Image.new("RGBA",(32,64),GRASS+(255,)); cell.alpha_composite(s_); cell=cell.crop((0,0,32,52))
                im.paste(up(cell,sc).convert("RGB"),(ox+j*(cw+6),y))
        y+=ch+8
    return im.crop((0,0,W,y+10))

# ----------------------------------------------------------------------------- 4 portraits
def pgrid(cols, title, sc=3, bg=CREAM, labels=None):
    pw=64*sc; pad=14
    im=canvas(80+len(CH)*(pw+pad+34)+10); d=ImageDraw.Draw(im)
    text(d,(30,14),title,F(30),GOLD)
    x0=(W-len(cols)*(pw+pad))//2
    for i,(o,e) in enumerate(cols):
        text(d,(x0+i*(pw+pad)+pw//2,58),(labels[i] if labels else f"{OPTN.get(o,o)} {e}"),F(22),WHITE,"ma")
    for r,c in enumerate(CH):
        for i,(o,e) in enumerate(cols):
            p=f"{P}/{c}_{o}_{e}.png"
            if not os.path.exists(p): continue
            cell=Image.new("RGBA",(64,64),CREAM+(255,)); cell.alpha_composite(Image.open(p).convert("RGBA"))
            im.paste(up(cell,sc).convert("RGB"),(x0+i*(pw+pad),90+r*(pw+pad+34)))
        text(d,(x0,90+r*(pw+pad+34)+pw+6),NAME[c],F(22),GREY)
    return im.crop((0,0,W,90+len(CH)*(pw+pad+34)+4))

# ----------------------------------------------------------------------------- 5 dialogue shots
def dialogue_strip(shot, name_txt, port_path, out_note):
    base=Image.open(shot).convert("RGB")
    a=np.array(base)
    ref=np.array(Image.open("/tmp/claude-0/s53/z2.png").convert("RGB"))     # same scene without dialogue (rows above the panel)
    # clear old portrait area (x 5..70, y 96..160): scene rows above the panel (< 120) from ref, panel rows from a clean panel column
    a[96:120,5:75]=ref[96:120,5:75]
    for y in range(120,159): a[y,5:74]=a[y,76-3]
    im=Image.fromarray(a).convert("RGBA")
    por=Image.open(port_path).convert("RGBA")
    im.alpha_composite(por,(5,96))
    # the panel bottom border is overdrawn by the 64 px portrait: re-clip at y=160
    return im.convert("RGB").crop((0,60,240,160))

def fig_dialogue():
    shots=[("/tmp/claude-0/s53/y6.png","Mia",f"{P}/mia_A_neutral.png","Mia: neutral"),
           ("/tmp/claude-0/s53/y6.png","Mia",f"{P}/mia_A_happy.png","Mia: happy"),
           ("/tmp/claude-0/s53/y6.png","Mia",f"{P}/mia_A_angry.png","Mia: angry"),
           ("/tmp/claude-0/s53/y3.png","Sam",f"{P}/player_A_sad.png","You: sad")]
    sc=4; h=100*sc
    im=canvas(70+len(shots)*(h+50)); d=ImageDraw.Draw(im)
    text(d,(30,14),"5. In the real dialogue box (option A portraits, 4x)",F(30),GOLD)
    for i,(s,n,p,lab) in enumerate(shots):
        t=dialogue_strip(s,n,p,lab)
        im.paste(up(t.convert("RGBA"),sc).convert("RGB").crop((0,0,W,h)) if t.width*sc>W else up(t.convert("RGBA"),sc).convert("RGB"),(max(0,(W-t.width*sc)//2),60+i*(h+50)+30))
        text(d,(40,60+i*(h+50)),lab,F(24),WHITE)
    return im

# ----------------------------------------------------------------------------- 6 in-game group
def put(base,c,k,n,x,y):
    s=spr(c,k,n)
    sh=Image.new("RGBA",base.size,(0,0,0,0)); ImageDraw.Draw(sh).ellipse([x-8,y-3,x+8,y+3],fill=(10,20,10,90)); base.alpha_composite(sh)
    base.alpha_composite(s,(x-16,y-54))
def fig_ingame(key, title):
    bg=Image.open("/tmp/claude-0/s50/w3.png").convert("RGB"); a=np.array(bg)
    for y in range(0,12): a[y,:150]=a[12,:150]
    base=Image.fromarray(a).convert("RGBA")
    cast=[("mia","sw_0",76,72),("rosa","s_0",154,72),("victor","s_0",196,92)]
    if key!="base": cast.append(("player","s_0",104,100))
    else: cast=[(c,f,x,y) for c,f,x,y in cast]
    k=key
    for c,f,x,y in sorted(cast,key=lambda t:t[3]):
        s=spr(c,k if spr(c,k,f) is not None else "B",f)
        put(base,c,k if spr(c,k,f) is not None else "B",f,x,y)
    return base.convert("RGB")
def fig_ingame_all():
    keys=[("base","Now (old player stands in the middle)"),("B","B"),("C1","C1"),("C2","C2")]
    sc=4
    crop=(30,18,230,128)
    h=(crop[3]-crop[1])*sc
    im=canvas(70+len(keys)*(h+56)); d=ImageDraw.Draw(im)
    text(d,(30,14),"6. In the game (4x): You, Mia, Rosa, Victor on the park path",F(30),GOLD)
    for i,(k,lab) in enumerate(keys):
        g=fig_ingame(k,lab).crop(crop)
        y=70+i*(h+56)
        text(d,(30,y),lab,F(26),WHITE)
        im.paste(up(g.convert("RGBA"),sc).convert("RGB").resize((W-60,h)) if False else up(g.convert("RGBA"),sc).convert("RGB"),(30,y+36))
    return im

if __name__=="__main__":
    figs={}
    figs["0_header"]=fig_header()
    figs["1_actual"]=fig_actual()
    for c in CH: figs["2_closeup_"+c]=fig_block(c)
    figs["3_walk"]=fig_walk()
    figs["4a_portraits_A"]=pgrid([("base","neutral"),("A","neutral"),("A","happy"),("A","angry"),("A","sad")],"4. Portraits 64x64 (3x): now / A neutral, happy, angry, sad",3)
    figs["4b_portraits_C1"]=pgrid([("base","neutral"),("A","neutral"),("C1","neutral"),("C1","happy")],"4b. Head 1.28x (A) vs 1.45x (C1) portraits",3)
    figs["5_dialogue"]=fig_dialogue()
    figs["6_ingame"]=fig_ingame_all()
    for k,v in figs.items(): v.save(f"{O}/fig_{k}.png")
    tot=sum(v.height for v in figs.values())
    full=Image.new("RGB",(W,tot),BG); y=0
    for k in figs: full.paste(figs[k],(0,y)); y+=figs[k].height
    full.save("/tmp/claude-0/s54/faces_proposal.png"); print(full.size)
