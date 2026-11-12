"""Captures every sound effect from the real mGBA output: python3 tools/music/capture_sfx.py ROM OUT.mp3
ROM must be built with -DTL_DEBUG_SFX (src/main.cpp: each A press plays the next effect in tl::audio::sfx order, loops are held 3 s).
Prints the peak / RMS of every effect and writes one montage MP3 (0.4 s of silence between effects)."""
import os
import subprocess
import sys
import wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capture as C  # noqa: E402

NAMES = ["menu_blip", "confirm", "menu_back", "coin", "cash", "door_bell", "mission_complete", "water(loop)", "shower(loop)", "munch(loop)",
         "gulp(loop)", "flush", "page(loop)", "rustle(loop)", "clink", "whirr", "snore(loop)", "thud", "door", "beep", "scratch", "ladder",
         "manhole", "mg_good", "mg_bad", "mg_clink"]
LOOPS = {"water(loop)", "shower(loop)", "munch(loop)", "gulp(loop)", "page(loop)", "rustle(loop)", "snore(loop)"}


def main():
    cap = C.Capture(sys.argv[1])
    cap.r.run(30)
    pieces = []
    for name in NAMES:
        cap.press("a")
        x = cap.record(3.4 if name in LOOPS else (2.8 if name in ("mission_complete", "flush") else 1.8))
        # trim trailing silence
        idx = np.where(np.abs(x) > 0.004)[0]
        x = x[:idx[-1] + int(0.2 * C.RATE)] if len(idx) else x[:int(0.2 * C.RATE)]
        print("%-18s %.2f s peak %.1f dBFS rms %.1f dBFS" % (name, len(x) / C.RATE, 20 * np.log10(np.max(np.abs(x)) + 1e-9),
                                                              20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)))
        pieces += [x, np.zeros(int(0.4 * C.RATE))]
    allx = np.concatenate(pieces)
    wav = sys.argv[2].replace(".mp3", ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(C.RATE)
        w.writeframes((np.clip(allx, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "160k", sys.argv[2]], check=True)


if __name__ == "__main__":
    main()
