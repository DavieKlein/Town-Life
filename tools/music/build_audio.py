"""Generates the game's audio files into audio/ (modules + SFX WAVs). Deterministic: running it twice gives identical files.
Usage: python3 tools/music/build_audio.py [AUDIO_DIR]     (default: <repo>/audio; commit the result)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import songs  # noqa: E402
import sfx  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "audio")
os.makedirs(out, exist_ok=True)
for fn in (songs.city_day, songs.old_block, songs.market):
    print(fn.__name__, fn(out), "bytes")
for name, x in sfx.make().items():
    print(name, sfx.write_wav(os.path.join(out, name + ".wav"), x), "bytes")
