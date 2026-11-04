import sys
from PIL import Image
pre, chars_, exs, sc, out = sys.argv[1], sys.argv[2].split(','), sys.argv[3].split(','), int(sys.argv[4]), sys.argv[5]
s=128*sc if '128' in pre else 96*sc
m=Image.new('RGB',(s*len(exs),s*len(chars_)),(236,226,200))
for j,c in enumerate(chars_):
    for i,e in enumerate(exs):
        im=Image.open(f'por/{pre}_{c}_{e}.png'); bg=Image.new('RGBA',im.size,(236,226,200,255)); bg.alpha_composite(im)
        m.paste(bg.resize((s,s),Image.NEAREST).convert('RGB'),(i*s,j*s))
m.save(out)
