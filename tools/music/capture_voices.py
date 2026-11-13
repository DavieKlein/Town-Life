"""Captures the character voices from the real mGBA output: python3 tools/music/capture_voices.py ROM OUT.mp3
ROM must be built with -DTL_DEBUG_VOICES (src/main.cpp: every character says 12 syllables, then a happy and an unhappy reaction; 230 frames each).
Order: mia rosa dex pimm lou halloran okafor dex_vault victor robot ines teo grigor valdez pruitt nella kessler trench_e duchess captain player."""
import os
import subprocess
import sys
import wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capture as C  # noqa: E402

cap = C.Capture(sys.argv[1])
x = cap.record(21 * 230 / C.FPS + 1.0)
wav = sys.argv[2].replace(".mp3", ".wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(C.RATE)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "160k", sys.argv[2]], check=True)
print("voices: %.1f s, peak %.1f dBFS, rms %.1f dBFS" % (len(x) / C.RATE, 20 * np.log10(np.max(np.abs(x)) + 1e-9), 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)))
