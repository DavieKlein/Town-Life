import re, numpy as np
from PIL import Image, ImageDraw
B='/home/user/Town-Life/butano/'
font=Image.open(B+'common/graphics/common_variable_8x8_font.bmp'); pal=font.getpalette(); fa=np.array(font)
t=open(B+'common/include/common_variable_8x8_sprite_font.h').read()
W=[int(x) for x in re.findall(r'^\s*(\d+),',re.search(r'character_widths\[\] = \{(.*?)\};',t,re.S).group(1),re.M)]
def P(i):return tuple(pal[i*3:i*3+3])
def text(img,x,y,s,main=None):
    for ch in s:
        g=ord(ch)-32
        if g==0:
            x+=W[0];continue
        tile=fa[(g-1)*8:(g-1)*8+8]
        for j in range(8):
            for i in range(8):
                v=tile[j,i]
                if v==0: continue
                c=P(v)
                if v==14 and main: c=main
                if 0<=x+i<img.width: img.putpixel((x+i,y+j),c)
        x+=W[g]
    return x
def tw(s):return sum(W[ord(c)-32] for c in s)
def wrap(s,maxw):
    lines=[];cur=''
    for w in s.split(' '):
        n=(cur+' '+w) if cur else w
        if tw(n)<=maxw:cur=n
        else:lines.append(cur);cur=w
    lines.append(cur);return lines
NAVY=(24,28,56);MID=(40,48,88);LIGHT=(72,84,136);DARK=(16,16,24);GOLD=(248,208,96)
def box(d,x0,y0,x1,y1):  # inclusive; rounded outline like HUD panels
    d.rectangle([x0,y0,x1,y1],fill=DARK)
    d.rectangle([x0+1,y0+1,x1-1,y1-1],fill=LIGHT)
    d.rectangle([x0+2,y0+2,x1-2,y1-2],fill=NAVY)
    d.line([x0+2,y0+2,x1-2,y0+2],fill=MID)
    for (cx,cy) in((x0,y0),(x1,y0),(x0,y1),(x1,y1)):
        pass
def arrow(img,x,y,on):
    if not on:return
    d=ImageDraw.Draw(img)
    d.rectangle([x,y,x+10,y+8],fill=DARK);d.rectangle([x+1,y+1,x+9,y+7],fill=LIGHT)
    text(img,x+2,y,"A")
def paste(img,im,x,y):
    img.paste(im,(x,y),im)
SP=Image.open
def v1(name,msg,port,out,on=True):
    img=SP('/tmp/claude-0/s31/start.png').convert('RGB');d=ImageDraw.Draw(img)
    y0=112
    box(d,0,y0,239,159)
    # portrait window
    d.rectangle([3,y0+3,51,159],fill=DARK);d.rectangle([4,y0+4,50,159],fill=MID)
    d.rectangle([4,y0+4,50,159],outline=None)
    d.line([4,y0+4,50,y0+4],fill=LIGHT)
    paste(img,Image.open(port),3,y0+1+1)   # 48x48, bottom flush with the screen
    # name tag
    nw=tw(name)+10
    d.rectangle([58,y0+3,58+nw,y0+14],fill=DARK);d.rectangle([59,y0+4,57+nw,y0+13],fill=LIGHT)
    text(img,63,y0+5,name,GOLD)
    for i,l in enumerate(wrap(msg,172)):text(img,58,y0+17+i*10,l)
    arrow(img,224,148,on)
    img.resize((720,480),Image.NEAREST).save(out);return img
def v2(name,msg,port,out,on=True):
    img=SP('/tmp/claude-0/s31/start.png').convert('RGB');d=ImageDraw.Draw(img)
    y0=120
    box(d,0,y0,239,159)
    paste(img,Image.open(port),5,96)
    nw=tw(name)+10
    d.rectangle([76,y0-8,76+nw,y0+3],fill=DARK);d.rectangle([77,y0-7,75+nw,y0+2],fill=LIGHT)
    text(img,81,y0-6,name,GOLD)
    for i,l in enumerate(wrap(msg,156)):text(img,76,y0+8+i*10,l)
    arrow(img,224,148,on)
    img.resize((720,480),Image.NEAREST).save(out);return img
