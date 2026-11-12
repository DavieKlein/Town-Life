"""Town Life playtest driver (s73, development tool): scripted headless play on top of tools/headless_run.py.

  python3 tools/playtest_driver.py ROM "cmd; cmd; ..."

ROM must be built with -DTL_DEBUG_POS (USERCXXFLAGS) for `state` and `goto` (the field then writes a state dump that is found in a
savestate by its magic "TLDB": map, position, day, time, money, mission, menu/conversation/activity/script flags, story flags, needs,
friendships). Do NOT combine -DTL_DEBUG_CPU with story runs that start a minigame (the screen stays black); use a separate build.
Commands: wait N, hold KEYS N, press KEYS [times], spam KEY FRAMES (press every 8 frames), walk up:30 right:20, goto X Y [tol]
(walks to a map cell with obstacle sidestepping, closes menus), gotow (walk instead of run), shot FILE, ss FILE / ls FILE (savestate),
state, stats LABEL (-DTL_DEBUG_CPU), loadsram F, dumpsram F, reset.
Typical start: python3 tools/make_save.py /tmp/x.sav diner 5.6 5.4 --flag ... ; commands "loadsram /tmp/x.sav; reset; wait 150; press a; wait 150; state"
"""
import sys, ctypes as ct
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import headless_run as H
# usage: drv.py ROM "cmds"   cmds: ';' separated; extra: ss F, ls F, spam KEY N, shot F, wait N, hold K N, press K, walk up:30 right:20
rom=sys.argv[1] if len(sys.argv)>1 else None
r=H.Runner(rom) if rom else None
def press(k):
    r.held={H.KEYS[x] for x in k.split('+')}; r.run(2); r.held=set(); r.run(2)
def ss(f):
    r.core.retro_serialize_size.restype=ct.c_size_t
    n=r.core.retro_serialize_size(); b=ct.create_string_buffer(n)
    r.core.retro_serialize(b,ct.c_size_t(n)); open(f,'wb').write(b.raw)
def ls(f):
    d=open(f,'rb').read(); b=ct.create_string_buffer(d,len(d))
    r.core.retro_unserialize(b,ct.c_size_t(len(d)))
import struct
def getstate():
    r.core.retro_serialize_size.restype=ct.c_size_t
    n=r.core.retro_serialize_size(); b=ct.create_string_buffer(n)
    r.core.retro_serialize(b,ct.c_size_t(n)); d=b.raw
    i=d.find(b'TLDB')
    if i<0: return None
    return struct.unpack_from('<4s13i80B5i20i',d,i)
DIRS=[((1,0),'down+right'),((-1,0),'up+left'),((0,1),'down+left'),((0,-1),'up+right'),((1,-1),'right'),((-1,1),'left'),((1,1),'down'),((-1,-1),'up')]
def goto(tx,ty,tol=0.35,maxit=160,run=True):
    import math, random
    hist=[]
    for it in range(maxit):
        v=getstate()
        if v is None: r.run(5); continue
        x,y=v[1]/16,v[2]/16
        if v[12]==1 and v[8] and not v[10]: press('b'); r.run(6); continue
        if v[12]!=1 or v[10] or v[9] or v[8] or v[11]: r.run(5); continue
        dx,dy=tx-x,ty-y; d=math.hypot(dx,dy)
        if d<tol: return True
        hist.append((x,y))
        ranked=sorted(DIRS,key=lambda q:-(q[0][0]*dx+q[0][1]*dy)/math.hypot(*q[0]))
        pick=0
        if len(hist)>=4 and math.hypot(hist[-1][0]-hist[-4][0],hist[-1][1]-hist[-4][1])<0.25:
            pick=random.choice([1,2,3])
        best=ranked[pick]
        n=max(2,min(14,int(d*5))) if run else max(2,min(14,int(d*8)))
        if pick: n=10
        k=best[1]+('+b' if run and d>2.5 else '')
        r.held={H.KEYS[z] for z in k.split('+')}; r.run(n); r.held=set(); r.run(1)
    print('goto timeout at',x,y,'target',tx,ty); return False
def state():
    r.core.retro_serialize_size.restype=ct.c_size_t
    n=r.core.retro_serialize_size(); b=ct.create_string_buffer(n)
    r.core.retro_serialize(b,ct.c_size_t(n)); d=b.raw
    i=d.find(b'TLDB')
    if i<0: print('STATE: none'); return
    v=struct.unpack_from('<4s13i80B5i20i',d,i)
    import story_data as sd
    x,y,mp,day,mn,money,mis,menu,conv,act,scr,st,frm=v[1:14]
    fl=v[14:94]; needs=v[94:99]; fr=v[99:119]
    names=[sd.FLAGS[k] if k<len(sd.FLAGS) else 'f%d'%k for k in range(80)]
    on=[names[k]+('=%d'%fl[k] if fl[k]>1 else '') for k in range(80) if fl[k]]
    mname=sd.MISSIONS[mis-1][0] if 0<mis<=len(sd.MISSIONS) else str(mis)
    print('STATE map%d pos(%.2f,%.2f) day%d %02d:%02d $%d mission %s menu%d conv%d act%d script%d st%d needs%s fr%s'%(mp,x/16,y/16,day,mn//60,mn%60,money,mname,menu,conv,act,scr,st,list(needs),list(fr)))
    print('  flags:',' '.join(on))
def runcmds(cmds):
  for cmd in cmds.split(';'):
      p=cmd.split()
      if not p: continue
      o=p[0]
      if o=='wait': r.held=set(); r.run(int(p[1]))
      elif o=='hold': r.held={H.KEYS[x] for x in p[1].split('+')}; r.run(int(p[2])); r.held=set()
      elif o=='press':
          for _ in range(int(p[2]) if len(p)>2 else 1): press(p[1])
      elif o=='spam':   # spam KEY N frames  (press every 8 frames)
          for _ in range(int(p[2])//8): press(p[1]); r.run(4)
      elif o=='shot': r.screenshot(p[1])
      elif o=='ss': ss(p[1])
      elif o=='state': state()
      elif o=='goto': goto(float(p[1]),float(p[2]),float(p[3]) if len(p)>3 else 0.35)
      elif o=='gotow': goto(float(p[1]),float(p[2]),float(p[3]) if len(p)>3 else 0.35,run=False)
      elif o=='ls': ls(p[1])
      elif o=='stats': r.stats(' '.join(p[1:]))
      elif o=='loadsram': r.load_sram(p[1])
      elif o=='dumpsram': r.dump_sram(p[1])
      elif o=='reset': r.reset()
      elif o=='walk':
          for seg in p[1:]:
              k,n=seg.split(':'); r.held={H.KEYS[x] for x in k.split('+')}; r.run(int(n)); r.held=set()
      else: raise SystemExit('bad '+o)

if __name__=='__main__': runcmds(sys.argv[2])
