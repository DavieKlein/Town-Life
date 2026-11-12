"""Pitch self-test: plays every melodic instrument over its range and measures the fundamental with an FFT.
Usage: python3 selftest.py [tmpdir]   (needs openmpt123 + ffmpeg)"""
import math
import os
import subprocess
import sys
import numpy as np
import synth as S
from engine import Song

RATE = 48000


def measure(inst, notes, tmp):
    song = Song("t", 125, 4, 1, [inst], swing=0)
    # 8 rows per note (0.96 s)
    for i, m in enumerate(notes):
        r = i * 8
        song.put(0, r // 16, r % 16, m, inst.name, 60, 7, swing=False)
    path = os.path.join(tmp, "t.xm")
    song.build(path)
    subprocess.run(["openmpt123", "--render", "--samplerate", str(RATE), "--channels", "1", "--force",
                    "--output-type", "wav", path], check=True, capture_output=True)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path + ".wav", "-f", "f32le", "-ac", "1", "-"],
                         check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    out = []
    for i, m in enumerate(notes):
        a = int((i * 8 * 0.12 + 0.12) * RATE)
        seg = x[a:a + int(0.3 * RATE)] * np.hanning(int(0.3 * RATE))
        spec = np.abs(np.fft.rfft(seg, 1 << 17))
        fr = np.fft.rfftfreq(1 << 17, 1 / RATE)
        f0 = S.mtof(m)
        sel = (fr > f0 * 0.89) & (fr < f0 * 1.12)
        f = fr[sel][np.argmax(spec[sel])]
        out.append((m, f0, f, 1200 * math.log2(f / f0)))
    return out


if __name__ == "__main__":
    tmp = sys.argv[1] if len(sys.argv) > 1 else "/tmp"
    tests = [("epiano", S.inst_epiano(), [48, 55, 60, 67, 72, 76]),
             ("marimba", S.inst_marimba(), [64, 69, 76, 81, 84]),
             ("vibes", S.inst_vibes(), [60, 65, 72, 77, 84]),
             ("whistle", S.inst_whistle(), [64, 72, 76, 79, 84]),
             ("accordion", S.inst_accordion(), [62, 66, 74, 78, 81]),
             ("bass", S.inst_bass(), [38, 41, 46, 53]),
             ("bass_up", S.inst_bass(True), [38, 45, 50, 54]),
             ("tuba", S.inst_tuba(), [50, 57, 62]),
             ("guitar", S.inst_guitar(), [52, 57, 64, 69, 76]),
             ("mandolin", S.inst_mandolin(), [64, 71, 78]),
             ("clav", S.inst_clav(), [60, 66, 72, 78])]
    worst = 0
    for name, inst, notes in tests:
        res = measure(inst, notes, tmp)
        errs = " ".join(f"{m}:{c:+.0f}c" for m, f0, f, c in res)
        print(f"{name:10s} {errs}")
        worst = max(worst, max(abs(c) for *_, c in res))
    print("worst cents error:", round(worst))
