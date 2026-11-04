#!/usr/bin/env python3
"""bins.png and toilet_hut.png from the preview renders in /tmp/claude-0/s49/pr (see rend.sh)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import lib
from PIL import Image
PR = "/tmp/claude-0/s49/pr/"
a, b = lib.compose(PR + "street_cur"), lib.compose(PR + "street_bin2")
lab = lib.compose(PR + "lab")
tc, tn = lib.compose(PR + "toilet_cur"), lib.compose(PR + "toilet3")


def stack(parts):
    w = max(p.width for p in parts)
    o = Image.new("RGB", (w, sum(p.height for p in parts)), (28, 30, 38))
    y = 0
    for p in parts:
        o.paste(p, (0, y)); y += p.height
    return o


box = (50, 14, 200, 124)
t1 = lib.labelled([(a.crop(box), "STREET: current bin"), (b.crop(box), "STREET: proposed steel bin")], n=3, cols=2,
                  title="Outdoor street bins, in the City Centre (game colours, 3x)")
t2 = lib.labelled([(lab.crop((135, 120, 235, 205)), "new street | current | indoor pedal"),
                   (tc.crop((60, 50, 160, 130)), "WC bin now (= street bin)"),
                   (tn.crop((60, 50, 160, 130)), "WC bin proposed (indoor)")], n=3, cols=3,
                  title="Street bin vs indoor bin: different shape, size, colour, materials")
stack([t1, t2]).save("/tmp/claude-0/s49/bins.png")
full = (14, 20, 234, 150)
s1 = lib.labelled([(tc.crop(full), "CURRENT: sign in front of WC, flat sink"), (tn.crop(full), "PROPOSED: sign by the mop, new sink + bin")],
                  n=3, cols=2, title="Public toilet (render preview, game colours, 3x)")
s2 = lib.labelled([(tc.crop((18, 36, 98, 112)), "sink now"), (tn.crop((18, 36, 98, 112)), "sink proposed"),
                   (tn.crop((18, 36, 98, 112)).transpose(Image.FLIP_LEFT_RIGHT), "(mirror image check)")][:2], n=4, cols=2,
                  title="Sink close-up (dark bowl, chrome mixer tap, round mirror)")
stack([s1, s2]).save("/tmp/claude-0/s49/toilet_hut.png")
