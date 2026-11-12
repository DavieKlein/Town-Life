"""NPC visibility audit (s79, run from the repo root): python3 tools/npc_audit.py ROM OUTDIR TAG [npc_id]
ROM must be built with -DTL_DEBUG_POS (any USERCXXFLAGS build works). For every row of cast.PLACEMENTS a save is made with the player
2.2 cells east of the NPC at a time when he is present, the game is booted and a screenshot is taken; OUTDIR/TAG_pageNN.png are
contact sheets (6 shots per page) to check for NPCs chopped by counters / poles / edges. Rows with a flag_on get that flag set.
"""
import sys,os,subprocess
sys.path.insert(0,'tools')
import cast
from PIL import Image, ImageDraw
ROM=sys.argv[1]; SP=sys.argv[2]; tag=sys.argv[3]; only=sys.argv[4] if len(sys.argv)>4 else None
OFF=[(2.2,0.3)]
def tm(s):
    h,m=s.split(':');return int(h)*60+int(m)
shots=[]
for i,p in enumerate(cast.PLACEMENTS):
    npc,mp,x,y,face,f,t,d0,d1=p[:9]
    fon=p[9] if len(p)>9 else None
    if only and npc!=only: continue
    flags=[fon] if fon else []
    if mp=='old_block': flags.append('old_block_open')
    fl=','.join(flags)
    for k,(dx,dy) in enumerate(OFF):
        sav='%s/c.sav'%SP
        args=['python3','tools/make_save.py',sav,mp,str(x+dx),str(y+dy),'--minutes',str(tm(f)+8 if not (tm(f)<=720<tm(t)) else 720),'--day',str(d0),'--needs','80,80,80,80,80']
        if fl: args+=['--flag',fl]
        subprocess.run(args,check=True,capture_output=True)
        out='%s/%s_%02d_%s_%s_%d.png'%(SP,tag,i,npc,mp,k)
        r=subprocess.run(['python3','tools/playtest_driver.py',ROM,'loadsram %s; reset; wait 150; press a; wait 240; shot %s'%(sav,out)],capture_output=True,text=True)
        shots.append((out,'%d %s %s %.1f,%.1f %s %s'%(i,npc,mp,x,y,f,fl)))
# mosaic 2 cols x 3 rows per page, 2x
per=6
for pg in range(0,len(shots),per):
    chunk=shots[pg:pg+per]
    im=Image.new('RGB',(2*480,3*340),(30,30,30)); d=ImageDraw.Draw(im)
    for j,(f,lab) in enumerate(chunk):
        try: s=Image.open(f).convert('RGB').resize((480,320),Image.NEAREST)
        except Exception as e: continue
        x=(j%2)*480;y=(j//2)*340
        im.paste(s,(x,y+20)); d.text((x+4,y+4),lab,fill=(255,255,0))
    im.save('%s/%s_page%02d.png'%(SP,tag,pg//per))
print(len(shots))
