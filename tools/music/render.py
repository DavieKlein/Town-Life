"""Preview renderer: XM -> WAV (libopenmpt, GBA-like: mono, 15768 Hz, no interpolation) -> MP3, plus level stats.
Usage: python3 render.py in.xm out.mp3 [loops=2] [gain_db=0]
"""
import os
import subprocess
import sys
import wave
import numpy as np

RATE = 15768  # one of the maxmod GBA mixing rates


def render(xm, mp3, loops=2, gain=0.0):
    base = os.path.splitext(mp3)[0]
    wav = base + "_raw.wav"
    subprocess.run(["openmpt123", "--render", "--samplerate", str(RATE), "--channels", "1", "--filter", "1",
                    "--repeat", str(loops - 1), "--gain", str(gain), "--force", "--output-type", "wav", xm], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.replace(xm + ".wav", wav)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", wav, "-f", "f32le", "-ac", "1", "-"],
                         check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(float)
    # GBA output is 8-bit: quantise
    q = np.round(x * 127) / 127
    out = (np.clip(q, -1, 1) * 32767).astype(np.int16)
    w8 = base + "_8bit.wav"
    with wave.open(w8, "wb") as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(RATE); o.writeframes(out.tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w8, "-ar", "44100", "-b:a", "128k", mp3], check=True)
    peak = np.max(np.abs(x))
    rms = np.sqrt(np.mean(x ** 2))
    print(f"{os.path.basename(mp3)}: {len(x)/RATE:.1f} s, peak {20*np.log10(peak+1e-9):.1f} dBFS, rms {20*np.log10(rms+1e-9):.1f} dBFS, "
          f"clipped samples {int(np.sum(np.abs(x) > 0.999))}")
    return x


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2,
           float(sys.argv[4]) if len(sys.argv) > 4 else 0.0)
