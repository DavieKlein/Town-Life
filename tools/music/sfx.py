"""Synthesised SFX (8-bit unsigned mono WAV, 16 kHz). Usage: python3 sfx.py OUTDIR  -> *.wav + sfx_montage.mp3"""
import math
import os
import subprocess
import sys
import wave
import numpy as np
import synth as S

R = 16000


def t_(d):
    return np.arange(int(R * d)) / R


def sq(f, t, duty=0.5):
    return np.where((f * t) % 1.0 < duty, 1.0, -1.0)


def tone(f, d, wave_="sin", decay=0.1, attack=0.002, vib=0):
    t = t_(d)
    ph = 2 * math.pi * f * t + (vib * np.sin(2 * math.pi * 6 * t) if vib else 0)
    w = np.sin(ph) if wave_ == "sin" else sq(f, t, 0.5) * 0.6 + np.sin(ph) * 0.4
    env = np.exp(-t / decay) * np.minimum(t / attack, 1)
    return w * env


def bell(f, d, decay=0.5, ratios=(1, 2.76, 5.4, 8.9), amps=(1, 0.5, 0.25, 0.1)):
    t = t_(d)
    x = np.zeros_like(t)
    for r, a in zip(ratios, amps):
        x += a * np.sin(2 * math.pi * f * r * t) * np.exp(-t / (decay / (1 + 0.6 * (r - 1) ** 0.5)))
    return x * np.minimum(t / 0.001, 1)


def place(parts, total):
    out = np.zeros(int(R * total))
    for at, x, g in parts:
        i = int(R * at)
        n = min(len(x), len(out) - i)
        out[i:i + n] += x[:n] * g
    return out


def finish(x, peak=0.9):
    x = x / np.max(np.abs(x)) * peak
    n = min(160, len(x))
    x[-n:] *= np.linspace(1, 0, n)
    return x


def make():
    fx = {}
    fx["menu_blip"] = finish(tone(1568, 0.045, "sq", 0.03))
    fx["menu_back"] = finish(tone(988, 0.07, "sq", 0.05))
    fx["confirm"] = finish(place([(0, tone(880, 0.10, "sq", 0.06), 0.8), (0.07, tone(1319, 0.2, "sq", 0.1), 1.0)], 0.3))
    fx["coin"] = finish(place([(0, tone(1976, 0.05, "sin", 0.1) + 0.3 * bell(1976, 0.05, 0.05), 0.7),
                               (0.055, bell(2637, 0.45, 0.22, (1, 3.01, 5.0), (1, 0.3, 0.12)), 1.0)], 0.55))
    # cash register: mechanical ka (noise burst + low thunk) then a bright bell ching
    t = t_(0.09)
    ka = S.highpass(S.lowpass(S.noise(len(t)), 0.6), 0.1) * np.exp(-t / 0.02) + 0.6 * np.sin(2 * math.pi * 170 * t) * np.exp(-t / 0.03)
    fx["cash"] = finish(place([(0, ka, 0.9), (0.10, bell(1760, 0.8, 0.45, (1, 2.4, 4.1, 6.3), (1, 0.55, 0.3, 0.12)), 0.8),
                               (0.17, bell(2349, 0.6, 0.35, (1, 2.4, 4.1), (1, 0.4, 0.2)), 0.7)], 0.85))
    # shop door bell: bright two-tone chime, ding (E6) - dong (C6), slow ring
    fx["door_bell"] = finish(place([(0, bell(1319, 1.0, 0.55, (1, 2.0, 3.0, 4.2), (1, 0.4, 0.2, 0.08)), 1.0),
                                    (0.28, bell(1047, 1.2, 0.7, (1, 2.0, 3.0, 4.2), (1, 0.4, 0.2, 0.08)), 0.9)], 1.5))
    # mission complete: motif shape 3-5-8 + high 10 on glockenspiel, then a warm major chord swell (C major, 2.4 s)
    def gl(m, d):
        f = S.mtof(m)
        t = t_(d)
        return (np.sin(2 * math.pi * f * t) * np.exp(-t / 0.5) + 0.3 * np.sin(2 * math.pi * f * 2.76 * t) * np.exp(-t / 0.2)
                + 0.12 * np.sin(2 * math.pi * f * 5.4 * t) * np.exp(-t / 0.08))
    def pad(m, d):
        f = S.mtof(m)
        t = t_(d)
        env = np.minimum(t / 0.08, 1) * np.exp(-t / 1.2)
        return (np.sin(2 * math.pi * f * t) + 0.3 * np.sin(2 * math.pi * 2 * f * t) + 0.15 * np.sin(2 * math.pi * 3 * f * t)) * env
    parts = [(0.00, gl(76, 0.8), 0.8), (0.16, gl(79, 0.8), 0.8), (0.32, gl(84, 0.9), 0.85), (0.56, gl(88, 1.6), 1.0)]
    for m, g in ((60, 0.55), (64, 0.45), (67, 0.45), (72, 0.4)):
        parts.append((0.56, pad(m, 1.9), g))
    parts.append((0.56, gl(96, 1.2), 0.25))
    fx["mission_complete"] = finish(place(parts, 2.5))
    return fx


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 127 + 128).astype(np.uint8)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(R)
        w.writeframes(pcm.tobytes())
    return len(pcm)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    fx = make()
    order = ["menu_blip", "menu_back", "confirm", "coin", "cash", "door_bell", "mission_complete"]
    seq = []
    for k in order:
        n = write_wav(os.path.join(out, k + ".wav"), fx[k])
        print(f"{k}.wav {n} bytes ({n / R:.2f} s)")
        seq += [fx[k], np.zeros(int(R * 0.7))]
    mont = np.concatenate(seq)
    tmp = os.path.join(out, "sfx_montage.wav")
    write_wav(tmp, mont)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-ar", "44100", "-b:a", "128k",
                    os.path.join(out, "sfx_montage.mp3")], check=True)
    os.remove(tmp)
