import sys; sys.path.insert(0,"/tmp/claude-0/s45")
from lib import *
random.seed(4)
SEC=[("MILK","milk",BLUE),("CANS","can",RED),("CEREAL","cereal",(230,160,40,255))]
CX=[40,120,200]
PL="/home/user/Town-Life/graphics/player.bmp"
def bg(img):
    # wall: warm wood panelling + cream wallpaper top
    R(img,0,14,240,58,(226,196,150,255))
    for x in range(0,240,16): R(img,x,14,1,58,(214,182,134,255))
    R(img,0,56,240,16,(150,100,56,255))  # wainscot behind lower shelf
    for x in range(0,240,10): R(img,x,56,1,16,(128,84,46,255))
    # floor planks
    for y in range(72,144,8):
        R(img,0,y,240,8,(176,120,66,255) if (y//8)%2 else (166,110,60,255))
        R(img,0,y,240,1,(120,78,40,255))
        off=(y//8*37)%40
        for x in range(off,240,40): R(img,x,y,1,8,(120,78,40,255))
    # darker back corner shading under shelf
    R(img,0,72,240,3,(110,72,38,255))
def shelf_unit(img,fills,sel=None,flash=None):
    for i,(nm,it,col) in enumerate(SEC):
        sx=i*80
        # uprights
        R(img,sx,14,4,58,WOODD); R(img,sx+1,14,1,58,WOODM)
        # back panel inside
        R(img,sx+4,26,72,45,(120,80,44,255) if flash!=i else (170,50,40,255))
        # boards
        for by in (45,67):
            R(img,sx+4,by,72,4,WOODL); R(img,sx+4,by+3,72,1,WOODD); R(img,sx+4,by,72,1,(215,160,100,255))
        # sign
        sc=col
        R(img,sx+10,15,60,11,OL); R(img,sx+11,16,58,9,sc)
        ctext(img,nm,sx+40,17,(255,255,255))
        # items
        n=fills[i]
        for k in range(n):
            row=k//4; c=k%4
            ITEMS[it](img,sx+8+c*16,(29 if row==0 else 51)+0)
    R(img,236,14,4,58,WOODD)
def hud(img,t,score,pay,combo,mult_pips,penalty=False):
    R(img,0,0,240,14,(58,36,22,255)); R(img,0,13,240,1,OL); R(img,0,12,240,1,WOODM)
    d=ImageDraw.Draw(img); d.ellipse([4,2,14,12],fill=(240,230,200,255),outline=OL); d.line([9,7,9,4],fill=OL); d.line([9,7,12,7],fill=OL)
    text(img,t,16,3,(255,120,100) if penalty else (255,255,255))
    text(img,"SCORE "+str(score),66,3,(255,255,255))
    text(img,"$"+str(pay),142,3,GOLD)
    text(img,"x"+str(combo),176,3,GOLD if combo>1 else (180,180,180))
    for i in range(4):
        R(img,194+i*10,4,8,6,OL); R(img,195+i*10,5,6,4,GOLD if i<mult_pips else (70,50,36,255))
def belt(img,queue,t=0):
    R(img,0,144,240,16,(60,62,70,255)); R(img,0,144,240,2,(120,124,136,255)); R(img,0,158,240,2,(30,30,36,255))
    for x in range((-t)%12,240,12): R(img,x,148,2,8,(80,82,92,255))
    R(img,0,144,46,16,(42,28,18,255)); text(img,"NEXT",4,148,(255,225,150))
    for i,it in enumerate(queue):
        ITEMS[it](img,50+i*22,143)
    d=ImageDraw.Draw(img); d.polygon([(46,147),(46,157),(51,152)],fill=GOLD) if False else 0
def player(img,col,carry=None,t=0):
    cx=CX[col]
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).ellipse([cx-11,136,cx+11,143],fill=(0,0,0,110)); img.alpha_composite(sh)
    if carry:
        f=sprite_sheet_frame("/home/user/Town-Life/graphics/player_wash.bmp",18,32,64)
    else: f=sprite_sheet_frame("/home/user/Town-Life/graphics/player_wash.bmp",16,32,64)
    paste(img,f,cx-16,86)
    if carry: ITEMS[carry](img,cx-8,72)
def marker(img,col,t=0):
    cx=CX[col]; y=28+ (t%2)
    d=ImageDraw.Draw(img)
    # selection bracket on sign + floor
    R(img,col*80+8,13,64,1,GOLD) if False else 0
    d.polygon([(cx-5,y+0),(cx+5,y),(cx,y+6)],fill=GOLD,outline=OL) if False else 0
    # floor bracket
    for dx in (-14,12): R(img,cx+dx,142,3,3,GOLD)
def sparkle(img,x,y,c=(255,245,170,255)):
    for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(0,2),(0,-2),(2,0),(-2,0)]: P(img,x+dx,y+dy,c)
def sel_frame(img,col):
    sx=col*80; 
    for (x,y,w,h) in [(sx+3,14,1,58),(sx+76,14,1,58)]: R(img,x,y,w,h,GOLD)
    R(img,sx+3,14,74,1,GOLD)
# ---- frames ----
def frame_mistake():
    img=new(); bg(img); shelf_unit(img,[5,3,2],flash=0)
    # wrong can sitting on milk shelf row 2 slot (k=5 -> row1,c=1 ... ) show X overlay
    can(img,sx:=8+0*80+16*1,51+0) if False else 0
    can(img,8+16*1,51)
    d=ImageDraw.Draw(img)
    for k in range(3): d.line([8+16+1+k,52+0,8+16+13+k,64],fill=(255,60,50,255)); d.line([8+16+13+k,52,8+16+1+k,64],fill=(255,60,50,255))
    sel_frame(img,0)
    belt(img,["milk","cereal","can","milk"],3)
    player(img,0,None)
    hud(img,"0:31",340,19,1,0,penalty=True)
    text(img,"-2s",44,16,(255,90,80)) if False else 0
    # rosa bubble
    box9(img,72,78,164,44,(250,240,215,255),OL)
    pr=portrait("rosa",32); paste(img,pr,76,84)
    text(img,"Cans go on",112,83,(60,30,20)) 
    text(img,"the CANS shelf!",112,93,(180,40,30))
    text(img,"Combo lost, -2s",112,106,(90,60,40))
    ctext(img,"OOPS",120,63,(255,255,255)) if False else 0
    return img
def frame_combo():
    img=new(); bg(img); shelf_unit(img,[8,6,4])
    sel_frame(img,2)
    belt(img,["cereal","can","milk","cereal"],0)
    player(img,2,"cereal")
    hud(img,"0:19",890,20,4,4)
    # section complete sparkles on milk shelf (full)
    for (x,y) in [(14,32),(34,50),(58,30),(70,60),(24,66),(48,38)]: sparkle(img,x,y)
    # banner
    box9(img,6,100,100,34,(28,50,40,255),GOLD)
    ctext(img,"SECTION",56,105,GOLD); ctext(img,"DONE! +50",56,117,(255,255,255))
    ctext(img,"COMBO x4!",120,118,(255,230,90),2) if False else 0
    # big combo label (16x16 font in game) 
    s=Image.new("RGBA",(W,H),(0,0,0,0)); text(s,"COMBO x4!",0,0,(255,215,70),2)
    bb=s.crop((0,0,tw("COMBO x4!",2),16)); img.alpha_composite(bb,(34,78))
    return img
def title_card():
    img=new(); bg(img)
    shelf_unit(img,[4,2,3])
    img.alpha_composite(Image.new("RGBA",(W,H),(20,10,5,150)))
    box9(img,40,14,160,28,(120,40,30,255),GOLD)
    ctext(img,"STOCK IT!",120,20,(255,230,120),2)
    for i,(nm,it,col) in enumerate(SEC):
        x=30+i*68
        box9(img,x-2,46,56,32,(60,36,22,255),(160,120,70,255))
        ITEMS[it](img,x+16,49)
        ctext(img,nm,x+26,67,(255,255,255))
    btn(img,78,84,"L",(90,90,110,255)); btn(img,90,84,"R",(90,90,110,255)); text(img,"Walk",106,85,(255,255,255))
    btn(img,78,96,"A",(200,60,60,255)); text(img,"Put item away",94,97,(255,255,255))
    btn(img,78,108,"B",(200,160,40,255)); text(img,"Swap (-2 s)",94,109,(255,255,255))
    box9(img,0,122,240,38,NAVY,(120,130,190,255))
    paste(img,portrait("rosa",64),6,96)
    R(img,76,123,50,10,(60,50,110,255)); text(img,"Rosa",80,124,GOLD)
    text(img,"Right item, right",76,135,(255,255,255)); text(img,"shelf. Be quick!",76,145,(255,255,255))
    text(img,"A",222,148,(255,255,255))
    return img
def result():
    img=new(); bg(img); shelf_unit(img,[8,8,8]); img.alpha_composite(Image.new("RGBA",(W,H),(20,10,5,170)))
    box9(img,52,6,184,112,NAVY,(120,130,190,255))
    ctext(img,"SHIFT DONE!",144,12,GOLD)
    rows=[("Stocked","31"),("Mistakes","2"),("Best combo","x6"),("Score","740")]
    for i,(a,b) in enumerate(rows):
        text(img,a,62,28+i*12,(255,255,255)); text(img,b,236-10-tw(b),28+i*12,(255,255,255))
    R(img,60,76,168,1,(120,130,190,255))
    text(img,"Rank",62,82,(255,255,255))
    # rank stamp
    R(img,104,78,18,18,OL); R(img,105,79,16,16,(200,60,50,255)); text(img,"A",109,83,(255,255,255))
    text(img,"Pay $18 + $2",62,102,(255,255,255)) if False else 0
    text(img,"Pay",150,82,(255,255,255)); text(img,"$20",186,82,GOLD)
    text(img,"$18 wage + $2 bonus",62,98,(200,210,255))
    # dialogue strip
    box9(img,0,118,240,42,NAVY,(120,130,190,255))
    pr=portrait("rosa",64); paste(img,pr,6,98)
    R(img,76,119,70,10,(60,50,110,255)); text(img,"Rosa",80,120,GOLD)
    text(img,"Not bad, kid.",76,133,(255,255,255)); text(img,"Not bad at all.",76,143,(255,255,255)); text(img,"A",222,148,(255,255,255))
    # side: portrait of player? small envelope
    d=ImageDraw.Draw(img); R(img,10,52,34,22,OL); R(img,11,53,32,20,(240,230,205,255)); d.line([11,53,27,64,43,53],fill=(190,170,130,255)); text(img,"$",23,60,(0,0,0)) if False else 0
    return img
if __name__=="__main__":
    for n,f in [("shelf_1_title",title_card),("shelf_2_mistake",frame_mistake),("shelf_3_combo",frame_combo),("shelf_4_result",result)]:
        save(f(),n)
