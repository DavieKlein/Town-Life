"""Captures the REAL audio output of the GBA mGBA core (the one Lemuroid uses) from a headless run and analyses it.

  python3 tools/music/capture.py ROM OUT_PREFIX TRACK[,TRACK...] [loops=2]
  ROM must be built with -DTL_DEBUG_MUSIC=1 (src/main.cpp: plays tracks 1..5 = city, old_block, market, stock_it, plate_rush; the A button
  switches to the next track). Writes OUT_PREFIX_<track>.mp3 (+ .wav) and prints level / spectrum metrics.
Needs: apt-get install libretro-mgba, ffmpeg, numpy."""
import ctypes as ct
import os
import subprocess
import sys
import wave
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import headless_run as H  # noqa: E402

NAMES = {1: "city", 2: "old_block", 3: "market", 4: "stock_it", 5: "plate_rush", 6: "victor", 7: "sad"}
LOOP_SECONDS = {1: 55.4, 2: 60.0, 3: 35.6, 4: 30.0, 5: 28.2, 6: 37.0, 7: 43.7}
RATE = 32768
FPS = 59.7275


class Capture:
    def __init__(self, rom):
        self.chunks = []
        orig = H.AUDIO_BATCH_CB

        def cap(data, n):
            if n:
                self.chunks.append(np.ctypeslib.as_array(ct.cast(data, ct.POINTER(ct.c_int16)), shape=(n * 2,)).copy())
            return n

        H.AUDIO_BATCH_CB = lambda fn: orig(cap)
        self.r = H.Runner(rom)
        H.AUDIO_BATCH_CB = orig

    def press(self, key):
        self.r.held = {H.KEYS[key]}
        self.r.run(2)
        self.r.held = set()
        self.r.run(2)

    def record(self, seconds):
        self.chunks = []
        self.r.run(int(seconds * FPS))
        a = np.concatenate(self.chunks).astype(np.float64) / 32768.0
        return a.reshape(-1, 2).mean(axis=1)


def metrics(x):
    n = len(x)
    seg = x[int(0.5 * RATE):]
    peak = np.max(np.abs(seg))
    rms = np.sqrt(np.mean(seg ** 2))
    n2 = 1 << int(np.floor(np.log2(len(seg))))
    sp = np.abs(np.fft.rfft(seg[:n2] * np.hanning(n2))) ** 2
    fr = np.fft.rfftfreq(n2, 1 / RATE)
    tot = sp.sum()
    bands = [(0, 150), (150, 500), (500, 2000), (2000, 4000), (4000, 8000), (8000, 16384)]
    pct = [100 * sp[(fr >= a) & (fr < b)].sum() / tot for a, b in bands]
    # "grit": energy above 8 kHz (nearest-neighbour images / aliases / quantisation hiss) relative to the 2-8 kHz music band
    grit_db = 10 * np.log10(sp[(fr >= 8000)].sum() / max(sp[(fr >= 2000) & (fr < 8000)].sum(), 1e-20))
    # short-time noise floor: 10th percentile of the 8-16 kHz energy per 50 ms frame, relative to the frame RMS (dB)
    hop = int(0.05 * RATE)
    fl = []
    for i in range(0, len(seg) - hop, hop):
        f = seg[i:i + hop] * np.hanning(hop)
        s = np.abs(np.fft.rfft(f)) ** 2
        fq = np.fft.rfftfreq(hop, 1 / RATE)
        e = s.sum()
        if e > 1e-8:
            fl.append(10 * np.log10(s[fq >= 8000].sum() / e + 1e-12))
    return dict(peak_db=20 * np.log10(peak + 1e-9), rms_db=20 * np.log10(rms + 1e-9), bands=pct, grit_db=grit_db,
                hf_floor_db=float(np.percentile(fl, 10)) if fl else 0.0, hf_median_db=float(np.median(fl)) if fl else 0.0)


def fmt(m):
    b = m["bands"]
    return ("peak %.1f dBFS rms %.1f dBFS | <150 %.1f%% 150-500 %.1f%% 0.5-2k %.1f%% 2-4k %.1f%% 4-8k %.1f%% >8k %.2f%% | "
            ">8k vs 2-8k %.1f dB, quiet-frame >8k floor %.1f dB (median %.1f)" % (m["peak_db"], m["rms_db"], b[0], b[1], b[2], b[3], b[4], b[5],
                                                                                 m["grit_db"], m["hf_floor_db"], m["hf_median_db"]))


def main():
    rom, prefix, tracks = sys.argv[1], sys.argv[2], [int(t) for t in sys.argv[3].split(",")]
    loops = float(sys.argv[4]) if len(sys.argv) > 4 else 2
    cap = Capture(rom)
    cap.r.run(30)
    cur = 1
    for t in tracks:
        while cur != t:
            cap.press("a")
            cur = cur % 7 + 1
        cap.r.run(10)
        x = cap.record(LOOP_SECONDS[t] * loops)
        wav = f"{prefix}_{NAMES[t]}.wav"
        with wave.open(wav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "160k", f"{prefix}_{NAMES[t]}.mp3"], check=True)
        print(f"{os.path.basename(prefix)}_{NAMES[t]}: {len(x)/RATE:.1f} s |", fmt(metrics(x)))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
