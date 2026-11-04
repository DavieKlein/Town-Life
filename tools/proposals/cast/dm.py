import sys; sys.path.insert(0,'/tmp/claude-0/s42')
from dm_lib import *
from PIL import Image, ImageDraw
import scene_comp as sc
def v2img(base, name, msg, port, out, on=True, scale=3):
    img = base.convert('RGB'); d = ImageDraw.Draw(img)
    y0 = 120
    box(d, 0, y0, 239, 159)
    paste(img, Image.open(port).convert('RGBA'), 5, 96)
    nw = tw(name) + 10
    d.rectangle([76, y0 - 8, 76 + nw, y0 + 3], fill=DARK); d.rectangle([77, y0 - 7, 75 + nw, y0 + 2], fill=LIGHT)
    text(img, 81, y0 - 6, name, GOLD)
    for i, l in enumerate(wrap(msg, 156)): text(img, 76, y0 + 8 + i * 10, l)
    arrow(img, 224, 148, on)
    img.resize((240 * scale, 160 * scale), Image.NEAREST).save(out)
base = Image.open('/tmp/claude-0/s31/start.png').convert('RGBA')
sc.put(base, 'robot', 'ne', 104, 106)
sc.put(base, 'victor', 'ne', 82, 96)
# draw robot after victor? robot is lower on screen (y 106 > 96) so it is in front: re-sort
base = Image.open('/tmp/claude-0/s31/start.png').convert('RGBA')
for n, f, x, y in sorted([('victor', 'ne', 72, 96), ('robot', 'ne', 95, 108)], key=lambda c: c[3]): sc.put(base, n, f, x, y)
base.convert('RGB').save('shots/victor_scene.png')
v2img(base, "Victor Vault", "Cashiers? Shelves? People? So last century.", 'portraits/victor.png', 'dialogue_mock.png')
# bonus: Rosa in the shop
b2 = sc.load('shots/m4.png')
for n, f, x, y in sorted([('rosa', 'sw', 94, 50), ('dex', 'ne', 58, 70)], key=lambda c: c[3]): sc.put(b2, n, f, x, y)
v2img(b2, "Rosa", "Forty years behind this counter, Dex. Don't you tell me how to run it.", 'portraits/rosa.png', 'dialogue_mock_rosa.png')
