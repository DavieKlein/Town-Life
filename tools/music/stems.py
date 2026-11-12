"""Render per-channel stems of a song and print levels: python3 stems.py city_day|old_block|market OUTDIR"""
import os
import sys
import songs
import render

name, out = sys.argv[1], sys.argv[2]
fn = getattr(songs, name)
d = os.path.join(out, "stem")
os.makedirs(d, exist_ok=True)
for ch in range(7):
    os.environ["MUSIC_CH"] = str(ch)
    fn(d)
    f = os.path.join(d, {"city_day": "city_day", "old_block": "old_block", "market": "market"}[name] + ".xm")
    print("channel", ch, end=": ")
    render.render(f, os.path.join(d, f"s{ch}.mp3"), 1)
