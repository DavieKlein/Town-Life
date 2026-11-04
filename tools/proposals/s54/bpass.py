import sys, json; sys.path.insert(0,'/tmp/claude-0/s54/keep')
from quant import *
sys.path.insert(0,'/tmp/claude-0/s54/keep'); import cast_snapshot as cs
def hx(h): h=h.lstrip('#'); return [int(h[i:i+2],16) for i in (0,2,4)]
LIPS={"player":"#a8584e","mia":"#b8484e","rosa":"#a84850","victor":"#9a5440"}
HAIR={"player":"#5a3420","mia":"#c8622a","rosa":"#c4c4cc","victor":"#f1ead4"}
def reserved(c):
    skin=np.array(hx(cs.CHARS[c]["colours"]["Skin"]),float)
    blush=skin*0.78+np.array([255,110,120])*0.22
    return [[246,242,238], hx(LIPS[c]), blush]
def make_ctx(pal,c):
    # reserved entries sit right after the free ones: 1+11 .. 
    nfree=11
    ctx=dict(out=15, eyew=1+nfree, mouth=2+nfree, blush=3+nfree)
    # (palette order: free..., reserved..., outline) -> outline index = 1+14
    skin=np.array(hx(cs.CHARS[c]["colours"]["Skin"]),float)
    ctx["skin_shade"]=nearest(pal, skin*0.80+np.array([40,0,20])*0.2, 1, 1+nfree)
    hair=np.array(hx(HAIR[c]),float)
    ctx["brow"]=nearest(pal, hair*0.62, 1, 1+nfree)
    ctx["hair_hi"]=nearest(pal, hair*0.5+np.array([255,255,255])*0.5 if c!="victor" else hair*1.0, 1, 1+nfree)
    pf=pal[:1+nfree]
    ctx["skin_set"]={i for i in range(1,1+nfree) if skin_class(pal[i])}
    ctx["lum"]=[0.3*p[0]+0.59*p[1]+0.11*p[2] for p in pal]
    return ctx
def build_B(c, opt, names, ss=4, popt=None):
    anc=json.load(open(f"/tmp/claude-0/s54/r/{c}_{opt}/anchors.json"))
    fr=[sprite_frame(f"/tmp/claude-0/s54/r/{c}_{opt}/{n}.png",ss,32,64) for n in names]
    pal,idx=quantize_sheet(fr,reserved(c))
    ctx=make_ctx(pal,c)
    out=[]
    for n,i in zip(names,idx):
        out.append(paint_face(i.copy(),anc[n],ctx,popt or {},n.split('_')[0]))
    return pal,out
if __name__=="__main__":
    c,o=sys.argv[1],sys.argv[2]
    names=["s_0","sw_0","se_0","e_0"]
    pal,idx=build_B(c,o,names)
    ims=[to_image(i,pal).crop((0,0,32,28)) for i in idx]
    s=Image.new("RGBA",(32*4,28),(110,150,90,255))
    for i,im in enumerate(ims): s.alpha_composite(im,(i*32,0))
    s.resize((s.width*8,s.height*8),Image.NEAREST).save(sys.argv[3])
    a=json.load(open(f"/tmp/claude-0/s54/r/{c}_{o}/anchors.json"))
    for n in names: print(n,{k:v for k,v in a[n].items() if k in("eyeP","eyeM","mouth","nose")})
