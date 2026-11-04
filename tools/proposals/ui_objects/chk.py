import subprocess, sys, json
from PIL import Image
import numpy as np
CASES = [
 ("Park bench", "city_centre", 7.3, 39.4, 7.3, 41.0),
 ("Square bench", "city_centre", 48.3, 38.0, 48.3, 39.4),
 ("Fountain", "city_centre", 53.0, 41.0, 53.0, 44.4),
 ("Street bin", "city_centre", 5.0, 21.1, 5.0, 22.4),
 ("Market checkout", "corner_market", 13.9, 15.0, 13.9, 16.4),
 ("Diner counter", "diner", 6.4, 4.5, 6.4, 5.8),
 ("Diner booth", "diner", 0.45, 4.4, 1.4, 3.0),
 ("Diner chair", "diner", 7.0, 6.3, 7.0, 5.4),
 ("Bookshelf", "community_centre", 4.7, 1.0, 4.7, 2.3),
 ("Notice board", "community_centre", 10.7, 1.0, 10.7, 2.3),
 ("Library sofa", "community_centre", 1.3, 9.6, 2.2, 9.0),
 ("Library chair", "community_centre", 6.1, 4.4, 6.1, 3.5),
 ("Reception", "vaulttech_lobby", 9.0, 5.5, 9.0, 6.7),
 ("Lobby bench", "vaulttech_lobby", 0.6, 3.95, 1.6, 4.0),
 ("Lobby sofa", "vaulttech_lobby", 10.55, 9.75, 11.3, 9.7),
 ("Public WC", "public_toilet", 1.2, 1.5, 1.4, 2.2),
 ("Public sink", "public_toilet", 1.0, 3.4, 1.9, 3.4),
 ("Toilet bin", "public_toilet", 0.95, 4.65, 1.9, 4.7),
]
sys.path.insert(0,'/home/user/Town-Life/tools')
import scene as scn
SC={}
for f in scn.SCENES:
    sc=f(); SC[sc.ident]=sc
def free(sc,x,y,r=0.3):
    if x<0.3 or y<0.3 or x>sc.w-0.3 or y>sc.h-0.3: return False
    for ax in (-r,0,r):
        for ay in (-r,0,r):
            if sc.solid[int((y+ay)*4)][int((x+ax)*4)]: return False
    return True
def pick(m,ox,oy):
    sc=SC[m]
    for k in (1.5,1.9,2.3,1.1):
        for (dx,dy) in ((-1,1),(1,-1),(0,1),(1,0),(-1,0),(0,-1),(-1,-1),(1,1)):
            n=(dx*dx+dy*dy)**.5
            x,y=ox+dx*k/n*1.0,oy+dy*k/n*1.0
            if free(sc,x,y): return round(x,2),round(y,2)
    return None
rom = sys.argv[1]; outdir = sys.argv[2]
for i, (name, m, ox, oy, px, py) in enumerate(CASES):
    pp = pick(m, ox, oy)
    if pp: px, py = pp
    print(name, px, py)
    sav = f"/tmp/claude-0/s47/chk/{i}.sav"
    subprocess.run(["python3", "/home/user/Town-Life/tools/proposals/ui_objects/make_save.py", sav, m, str(px), str(py), "0", "480", "50"])
    shot = f"{outdir}/{i:02d}.png"
    subprocess.run(["python3", "/home/user/Town-Life/tools/headless_run.py", rom,
        f"loadsram {sav}; reset; wait 100; press a; wait 330; shot {shot}"], stdout=subprocess.DEVNULL, cwd="/home/user/Town-Life")
    im = Image.open(shot).convert("RGB"); a = np.asarray(im).astype(int)
    # find the player: sweater blue
    mask = np.zeros(a.shape[:2], bool)
    for c in ((80,120,216),(72,112,200),(64,96,176),(56,80,152)):
        mask |= (a == np.array(c)).all(2)
    mask[128:] = False
    c = np.cumsum(np.cumsum(mask.astype(int), 0), 1); c = np.pad(c, ((1,0),(1,0)))
    dens = c[24:, 24:] - c[:-24, 24:] - c[24:, :-24] + c[:-24, :-24]
    dens = np.pad(dens, ((12,12),(12,12)))
    cy, cx = np.unravel_index(dens.argmax(), dens.shape)
    sub = mask[max(0,cy-14):cy+15, max(0,cx-14):cx+15]
    ys, xs = np.nonzero(sub); ys = ys + max(0,cy-14); xs = xs + max(0,cx-14)
    fx, fy = (int(xs.mean()), int(ys.min()) + 40) if len(xs) else (120, 86)
    dxw = (ox - px) * 16; dyw = (oy - py) * 16
    sx = fx + (dxw - dyw); sy = fy + (dxw + dyw) / 2 - 12
    json.dump(dict(name=name, sx=sx, sy=sy, fx=fx, fy=fy), open(f"{outdir}/{i:02d}.json", "w"))
    print(i, name, int(sx), int(sy), len(xs))
