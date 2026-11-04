import sys; sys.path.insert(0,"/tmp/claude-0/s45")
from lib import *
ZX=[96,146,196]
STEEL=(176,186,198,255); STEELD=(120,130,146,255); STEELL=(226,234,242,255)
TEAL=(46,140,140,255); PINK=(255,90,170,255); CYAN=(90,230,240,255)
DR=(190,48,56,255)
def bg(img):
    R(img,0,14,240,38,(246,226,170,255))      # upper wall butter yellow
    for x in range(0,240,24): R(img,x,14,1,38,(232,208,150,255))
    R(img,0,52,240,4,DR); R(img,0,56,240,1,WHITE)
    for r in range(3):
        for c in range(20):
            col=(30,30,38,255) if (r+c)%2==0 else (238,238,238,255)
            R(img,c*12,57+r*12,12,12,col)
    R(img,0,56,240,1,STEELD)
def neon(img):
    R(img,6,17,76,32,(24,20,40,255)); R(img,7,18,74,30,(40,26,64,255))
    # glow halo
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); d.rectangle([2,13,86,53],fill=(255,90,170,40)); img.alpha_composite(ov)
    s=Image.new("RGBA",(W,H),(0,0,0,0)); text(s,"LOU'S",0,0,PINK,2); img.alpha_composite(s.crop((0,0,80,16)),(10,21))
    R(img,12,41,64,2,CYAN); ctext(img,"DINER",44,34,CYAN) if False else 0
    text(img,"DINER",24,-0+37-0,CYAN) if False else 0
def window(img,who=("lou","mia")):
    R(img,116,16,118,36,STEEL); R(img,117,17,116,34,STEELD); R(img,119,19,112,30,(60,40,36,255))
    R(img,119,19,112,30,(120,78,50,255))
    xs=[124,182]
    for x,n in zip(xs,who): paste(img,portrait(n,32),x,19) if False else 0
    paste(img,portrait(who[0],32),126,19); paste(img,portrait(who[1],32),176,19)
    # order ticket rail
    R(img,116,48,118,4,STEEL); R(img,116,48,118,1,STEELL)
    for x in (160,168,208): R(img,x,41,5,7,(250,250,240,255)) if False else 0
def counter(img):
    R(img,0,92,240,18,STEEL)
    for y,c in [(93,STEELL),(98,(192,200,212,255)),(104,(168,178,192,255))]: R(img,0,y,240,1,c)
    R(img,0,106,240,2,STEELD)     # rail groove approx
    R(img,0,110,240,3,STEELL); R(img,0,113,240,1,STEELD)
    # front panel red vinyl with white diamond studs
    R(img,0,114,240,46,DR)
    for x in range(8,240,24):
        R(img,x,148,2,2,(240,200,200,255))
    R(img,0,114,240,1,(230,120,120,255))
    R(img,0,157,240,3,(110,24,32,255))
def sink(img):
    # basin behind the plate zone
    R(img,74,76,46,18,STEELD); R(img,75,77,44,16,(150,170,190,255)); R(img,75,77,44,4,(100,150,200,255))
    # suds
    for (x,y,r) in [(78,76,5),(86,73,6),(95,75,5),(103,72,6),(111,75,5),(92,70,4),(82,70,3),(108,69,3)]:
        d=ImageDraw.Draw(img); d.ellipse([x-r,y-r+2,x+r,y+r+2],fill=(248,252,255,255),outline=(170,200,230,255))
    # brush
    R(img,100,66,4,12,WOODM); R(img,98,76,8,4,YEL)
def tap(img):
    d=ImageDraw.Draw(img)
    R(img,138,64,5,26,STEEL); R(img,138,64,2,26,STEELL)
    R(img,138,64,16,4,STEEL); R(img,152,64,4,12,STEEL); R(img,150,76,8,3,STEELD)
    R(img,130,76,6,6,(200,60,50,255)); R(img,162,76,6,6,(60,90,200,255)) if False else 0
    for y in (80,85): R(img,153,y,2,3,(120,190,250,255))
def rack(img,n=4):
    # wire dish rack with clean plates standing
    R(img,174,84,50,10,STEELD); R(img,175,85,48,8,(100,108,122,255))
    for k in range(n):
        x=178+k*10
        R(img,x,66,3,22,OL); R(img,x+1,67,2,20,(244,248,252,255)); R(img,x+1,67,1,20,(200,226,248,255))
    R(img,174,84,50,2,STEELL)
def dirty_stack(img,n=4):
    R(img,40,90,36,3,STEELD)
    for k in range(n):
        y=88-k*3
        d=ImageDraw.Draw(img); d.ellipse([42,y-4,72,y+4],fill=OL); d.ellipse([43,y-3,71,y+3],fill=(236,226,200,255))
        if k%2==0: R(img,52+k*3,y-1,5,2,(150,60,30,255))
    R(img,56,78,6,2,(210,50,40,255))
def plate(img,cx,cy,state="dirty",w=24):
    d=ImageDraw.Draw(img); h=10
    d.ellipse([cx-w//2,cy-h//2,cx+w//2,cy+h//2],fill=OL)
    d.ellipse([cx-w//2+1,cy-h//2+1,cx+w//2-1,cy+h//2-1],fill=(246,246,242,255) if state!="dirty" else (232,222,196,255))
    d.ellipse([cx-w//2+4,cy-h//2+2,cx+w//2-4,cy+h//2-2],fill=(228,232,236,255) if state!="dirty" else (220,208,180,255))
    if state=="dirty":
        for (dx,dy,c) in [(-6,-1,(140,70,36,255)),(0,1,(190,50,40,255)),(5,-1,(120,150,60,255)),(-1,-2,(240,200,90,255)),(7,1,(140,70,36,255))]:
            R(img,cx+dx,cy+dy,3,2,c)
    elif state=="soap":
        for (dx,dy) in [(-7,0),(-2,-2),(3,1),(7,-1),(0,1)]:
            d.ellipse([cx+dx-2,cy+dy-2,cx+dx+2,cy+dy+2],fill=WHITE,outline=(170,200,230,255))
    elif state=="clean":
        for (dx,dy) in [(-6,-1),(6,0)]: sparkle(img,cx+dx,cy+dy-2,(255,255,200,255))
def sparkle(img,x,y,c=(255,245,170,255)):
    for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(0,2),(0,-2),(2,0),(-2,0)]: P(img,x+dx,y+dy,c)
def pan(img,cx,cy):
    d=ImageDraw.Draw(img)
    R(img,cx+13,cy-1,14,3,OL); R(img,cx+14,cy,12,1,(90,60,40,255))
    d.ellipse([cx-15,cy-6,cx+15,cy+6],fill=OL); d.ellipse([cx-14,cy-5,cx+14,cy+5],fill=(70,74,86,255)); d.ellipse([cx-10,cy-3,cx+10,cy+3],fill=(52,54,64,255))
    for (dx,dy,w) in [(-8,-1,6),(0,0,8),(5,-2,5),(-3,2,5)]: R(img,cx+dx,cy+dy,w,2,(176,120,40,255))
def hud(img,rush,tip,breaks,combo=1,clock="11:47"):
    R(img,0,0,240,14,(26,60,66,255)); R(img,0,12,240,1,STEEL); R(img,0,13,240,1,OL)
    text(img,clock,4,3,(255,255,255))
    text(img,"RUSH "+rush,52,3,CYAN)
    text(img,"TIP $%d"%tip,124,3,GOLD)
    text(img,"x%d"%combo,180,3,GOLD if combo>1 else (170,170,170))
    for i in range(3):
        cx=208+i*12; d=ImageDraw.Draw(img)
        d.ellipse([cx-5,3,cx+5,10],fill=OL)
        if i<breaks:
            d.ellipse([cx-4,4,cx+4,9],fill=(220,60,50,255)); R(img,cx-1,3,1,7,OL)
        else: d.ellipse([cx-4,4,cx+4,9],fill=(240,244,248,255))
def panel_labels(img,active=()):
    labs=[("DIRTY",50,None),("SCRUB",ZX[0],("A",(200,60,60,255))),("RINSE",ZX[1],("B",(200,160,40,255))),("STACK",ZX[2],("UP",(60,130,200,255)))]
    for nm,x,b in labs:
        ctext(img,nm,x,136,(255,235,225))
        if b:
            btn(img,x-5,120,b[0],b[1])
            if nm in active:
                d=ImageDraw.Draw(img); d.ellipse([x-8,117,x+8,133],outline=WHITE)
def zones(img,active=()):
    for i,x in enumerate(ZX):
        c=(255,255,255,255) if i in active else (255,255,255,120)
        d=ImageDraw.Draw(img)
        for dx in (-15,14): R(img,x+dx,96,1,10,c) 
def popup(img,s,x,y,col):
    s_=Image.new("RGBA",(W,H),(0,0,0,0)); text(s_,s,0,0,col)
    img.alpha_composite(s_.crop((0,0,tw(s),8)),(x-tw(s)//2,y))
def player(img,pose=0):
    # front view behind counter: wash frames facing s: 0 idle,1..3 arms forward ; sprite top
    f=sprite_sheet_frame("/home/user/Town-Life/graphics/player_wash.bmp",pose,32,64)
    paste(img,f,6,50)
    R(img,15,80,12,12,(250,250,250,255)); R(img,15,80,12,1,(200,200,205,255)); R(img,16,74,1,6,(250,250,250,255)); R(img,25,74,1,6,(250,250,250,255))
def base(active=(),pose=0):
    img=new(); bg(img); neon(img); window(img); sink(img); tap(img); rack(img,4); 
    player(img,pose); counter(img); dirty_stack(img); 
    return img
def frame_mid():
    img=base((0,),pose=1)
    plate(img,70,101,"dirty") if False else 0
    plate(img,62,100,"dirty")
    plate(img,ZX[0]+2,100,"dirty")
    plate(img,ZX[1]-1,100,"soap")
    plate(img,ZX[2]+3,100,"clean")
    zones(img,(0,1,2)); panel_labels(img,("SCRUB","RINSE","STACK"))
    popup(img,"PERFECT!",ZX[0],80-20,(255,235,90))
    popup(img,"GOOD",ZX[1],86,(180,240,255)) if False else 0
    sparkle(img,ZX[0]+10,70); sparkle(img,ZX[0]-10,66)
    hud(img,"3/8",1,0,3)
    return img
def frame_break():
    img=base((1,),pose=2)
    plate(img,62,100,"dirty"); pan(img,ZX[0],98)
    # mash prompt for pan
    popup(img,"MASH A!",ZX[0],77,(255,140,120))
    for i in range(5):
        R(img,ZX[0]-20+i*8,85,7,5,OL); R(img,ZX[0]-19+i*8,86,5,3,GOLD if i<2 else (70,50,36,255))
    # broken plate at rinse
    for (dx,dy,col) in [(-6,-1,WHITE),(-2,1,WHITE),(3,-2,WHITE),(7,1,WHITE)]:
        d=ImageDraw.Draw(img); cx=ZX[1]+dx; cy=100+dy
        d.polygon([(cx-3,cy+1),(cx+2,cy-2),(cx+3,cy+2)],fill=(246,246,242,255),outline=OL)
    for (x,y) in [(ZX[1]-12,86),(ZX[1]+10,82),(ZX[1]+2,90)]:
        d=ImageDraw.Draw(img); d.polygon([(x,y),(x+4,y-2),(x+3,y+3)],fill=(246,246,242,255),outline=OL)
    popup(img,"CRASH!",ZX[1]+14,80,(255,70,60))
    box9(img,64,54,172,20,(250,240,215,255),OL); text(img,"LOU:",70,60,(180,40,30)); text(img,"Mind the china!",106,60,(60,30,20))
    zones(img,(0,)); panel_labels(img,("SCRUB",))
    hud(img,"5/8",1,1)
    text(img,"-$1",132,3,(255,110,100)) if False else 0
    # Lou speech
    box9(img,60,16,0,0) if False else 0
    img2=img
    return img
def lou_bubble(img):
    box9(img,4,120,0,0) if False else 0
def title_card():
    img=base(); 
    img.alpha_composite(Image.new("RGBA",(W,H),(10,10,20,130)))
    box9(img,24,16,192,30,(24,60,66,255),CYAN)
    ctext(img,"PLATE RUSH",120,23,(255,235,150),2)
    # flow diagram: dirty -> A scrub -> B rinse -> UP stack
    xs=[36,92,148,204]
    for i,(x,lab) in enumerate(zip(xs,["DIRTY","SCRUB","RINSE","STACK"])):
        st=["dirty","soap","soap","clean"][i]
        plate(img,x+12,66,st)
        ctext(img,lab,x+12,78,WHITE)
        if i>0:
            b=[("A",(200,60,60,255)),("B",(200,160,40,255)),("UP",(60,130,200,255))][i-1]
            btn(img,x-3 if False else x+7,50,b[0],b[1])
        if i<3:
            d=ImageDraw.Draw(img); d.polygon([(x+32,62),(x+40,66),(x+32,70)],fill=GOLD)
    text(img,"Press the button as the plate",18,92,WHITE) if False else 0
    text(img,"Hit the button when",76,94,WHITE); text(img,"the plate is in [ ]",76,104,WHITE)
    # dialogue box
    box9(img,0,118,240,42,NAVY,(120,130,190,255))
    paste(img,portrait("lou",64),6,92)
    R(img,76,119,50,10,(60,50,110,255)); text(img,"Lou",80,120,GOLD)
    text(img,"Wash, rinse, repeat!",76,132,(255,255,255)); text(img,"Drop one, I cry.",76,142,(255,255,255))
    text(img,"A",222,148,(255,255,255))
    return img
def result():
    img=base()
    img.alpha_composite(Image.new("RGBA",(W,H),(10,10,20,170)))
    box9(img,52,4,184,112,NAVY,(120,130,190,255))
    ctext(img,"SHIFT DONE!",144,10,GOLD)
    rows=[("Plates","32"),("Perfect","24"),("Broken","1"),("Wage","$16"),("Tip","$2 -$1")]
    for i,(a,b) in enumerate(rows):
        text(img,a,62,24+i*11,WHITE); text(img,b,230-tw(b),24+i*11,WHITE if a!="Tip" else GOLD)
    R(img,60,82,168,1,(120,130,190,255))
    text(img,"Total",62,90,WHITE); text(img,"$17",230-24,90,GOLD)
    text(img,"+ staff meal!",62,102,(180,240,200))
    box9(img,0,118,240,42,NAVY,(120,130,190,255))
    paste(img,portrait("lou",64),6,92)
    R(img,76,119,50,10,(60,50,110,255)); text(img,"Lou",80,120,GOLD)
    text(img,"Not bad, kid!",76,132,WHITE); text(img,"Staff meal's free.",76,142,WHITE); text(img,"A",222,148,WHITE)
    return img
def mistake_final():
    img=frame_break()
    # Lou grumble bubble in window region lower left (over wall, left of counter)
    box9(img,40,16,0,0) if False else 0
    box9(img,6,56,0,0) if False else 0
    return img
if __name__=="__main__":
    for n,f in [("dishes_1_title",title_card),("dishes_2_mid",frame_mid),("dishes_3_break",frame_break),("dishes_4_result",result)]:
        save(f(),n)
