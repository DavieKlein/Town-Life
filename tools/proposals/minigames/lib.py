from PIL import Image, ImageDraw
import random, math
W,H=240,160
FONT=Image.open("/home/user/Town-Life/butano/common/graphics/common_fixed_8x8_font.bmp")
import numpy as np
FA=np.array(FONT)
def glyph(c,col):
    i=ord(c)-33
    g=Image.new("RGBA",(8,8),(0,0,0,0))
    if i<0 or i>=110: return g
    px=g.load()
    for y in range(8):
        for x in range(8):
            v=FA[i*8+y,x]
            if v==1: px[x,y]=tuple(col[:3])+(255,)
            elif v==2: px[x,y]=(0,0,0,255)
    return g
def text(img,s,x,y,col=(255,255,255),scale=1,shadow=False):
    for ch in s:
        g=glyph(ch,col)
        if scale>1: g=g.resize((8*scale,8*scale),0)
        img.alpha_composite(g,(x,y)) if True else 0
        x+=7*scale if False else 8*scale
    return x
def tw(s,scale=1): return 8*len(s)*scale
def ctext(img,s,cx,y,col=(255,255,255),scale=1):
    text(img,s,cx-tw(s,scale)//2,y,col,scale)
def new(col=(0,0,0,255)): return Image.new("RGBA",(W,H),col)
def R(img,x,y,w,h,c):
    ImageDraw.Draw(img).rectangle([x,y,x+w-1,y+h-1],fill=c)
def RO(img,x,y,w,h,c,o=(30,18,14,255)):
    d=ImageDraw.Draw(img); d.rectangle([x,y,x+w-1,y+h-1],fill=o); d.rectangle([x+1,y+1,x+w-2,y+h-2],fill=c)
def P(img,x,y,c):
    if 0<=x<img.width and 0<=y<img.height: img.putpixel((x,y),c)
def paste(img,spr,x,y):
    img.alpha_composite(spr,(x,y))
def sprite_sheet_frame(path,i,w,h,key=(255,0,255)):
    im=Image.open(path).convert("RGBA")
    f=im.crop((0,i*h,w,i*h+h))
    px=f.load()
    for yy in range(h):
        for xx in range(w):
            if px[xx,yy][:3]==key: px[xx,yy]=(0,0,0,0)
    return f
def portrait(name,size=64):
    p=Image.open(f"/tmp/claude-0/s42/portraits/{name}.png").convert("RGBA")
    if size!=64: p=p.resize((size,size),Image.BOX)
    return p
def save(img,name):
    img.convert("RGB").save(f"/tmp/claude-0/s45/{name}.png")
    img.convert("RGB").resize((W*3,H*3),0).save(f"/tmp/claude-0/s45/{name}_3x.png")
# colours
OL=(30,18,14,255)
CREAM=(241,228,195,255); WOODD=(90,58,34,255); WOODM=(138,90,48,255); WOODL=(185,128,72,255)
RED=(200,55,45,255); YEL=(240,192,64,255); BLUE=(58,111,192,255); GRN=(47,125,70,255)
NAVY=(24,30,60,255); GOLD=(240,200,80,255); WHITE=(255,255,255,255)
def box9(img,x,y,w,h,fill=(24,30,60,255),border=(120,130,190,255)):
    R(img,x,y,w,h,border); R(img,x+1,y+1,w-2,h-2,(0,0,0,255)); R(img,x+2,y+2,w-4,h-4,fill)
def btn(img,x,y,label,col):
    d=ImageDraw.Draw(img)
    d.ellipse([x,y,x+10,y+10],fill=OL); d.ellipse([x+1,y+1,x+9,y+9],fill=col)
    if label=="UP":
        d.polygon([(x+5,y+2),(x+8,y+7),(x+2,y+7)],fill=(255,255,255,255))
    elif label=="L": d.polygon([(x+2,y+5),(x+7,y+2),(x+7,y+8)],fill=WHITE)
    elif label=="R": d.polygon([(x+8,y+5),(x+3,y+2),(x+3,y+8)],fill=WHITE)
    else:
        g=glyph(label,(255,255,255)); 
        # recolor black outline to transparent for small icon
        px=g.load()
        for yy in range(8):
            for xx in range(8):
                if px[xx,yy][:3]==(0,0,0): px[xx,yy]=(0,0,0,0)
        img.alpha_composite(g,(x+1,y+1))
# --- products 16x16 ---
def milk(img,x,y):
    d=ImageDraw.Draw(img)
    d.polygon([(x+4,y+4),(x+8,y),(x+12,y+4)],fill=OL)
    R(img,x+3,y+3,10,13,OL)
    d.polygon([(x+5,y+4),(x+8,y+1),(x+11,y+4)],fill=(220,232,250,255))
    R(img,x+4,y+4,8,11,(245,248,255,255)); R(img,x+4,y+8,8,4,BLUE); R(img,x+6,y+9,4,2,WHITE)
    R(img,x+4,y+4,2,11,(215,225,245,255)) if False else 0
def can(img,x,y):
    R(img,x+3,y+2,10,13,OL); R(img,x+4,y+3,8,11,(200,200,210,255)); R(img,x+4,y+5,8,7,RED)
    R(img,x+4,y+7,8,3,CREAM); R(img,x+7,y+8,2,1,RED); R(img,x+4,y+5,1,7,(225,90,80,255))
    R(img,x+3,y+2,10,1,(120,120,135,255)); R(img,x+3,y+14,10,1,(120,120,135,255))
def cereal(img,x,y):
    R(img,x+2,y+0,12,16,OL); R(img,x+3,y+1,10,14,YEL); R(img,x+3,y+1,2,14,(250,215,110,255))
    d=ImageDraw.Draw(img); d.ellipse([x+5,y+6,x+11,y+11],fill=(200,110,40,255)); d.ellipse([x+6,y+7,x+10,y+9],fill=(250,240,230,255))
    R(img,x+3,y+2,10,2,RED)
ITEMS={"milk":milk,"can":can,"cereal":cereal}
def apple(img,x,y):
    d=ImageDraw.Draw(img); d.ellipse([x+2,y+4,x+13,y+15],fill=OL); d.ellipse([x+3,y+5,x+12,y+14],fill=RED); R(img,x+7,y+1,2,4,OL); R(img,x+9,y+2,3,2,GRN)
