"""Runs a scripted headless session (tools/playtest_driver.py commands) and records the REAL mGBA audio of the whole run to an MP3.

  python3 tools/music/capture_run.py OUT.mp3 ROM "loadsram x.sav; reset; wait 200; press a; wait 3000"

Typical use: the Victor Vault cutscene (ROM built with -DTL_DEBUG_POS -DTL_DEBUG_AUTO_TALK so dialogue advances by itself, a save made with
tools/make_save.py --day 1 --minutes 845 --flag lunch_given). Prints a loudness timeline (one character per 0.5 s)."""
import atexit
import ctypes as ct
import os
import runpy
import subprocess
import sys
import wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, "..")
sys.path.insert(0, TOOLS)
import headless_run as H  # noqa: E402

out_mp3 = sys.argv[1]
chunks = []


def cap(data, n):
    if n:
        chunks.append(np.ctypeslib.as_array(ct.cast(data, ct.POINTER(ct.c_int16)), shape=(n * 2,)).copy())
    return n


runners = []
_init = H.Runner.__init__


def _init_wrap(self, *a, **k):
    _init(self, *a, **k)
    runners.append(self)


H.Runner.__init__ = _init_wrap
orig = H.AUDIO_BATCH_CB
H.AUDIO_BATCH_CB = lambda fn: orig(cap)


def audio_log():
    """with a ROM built with -DTL_DEBUG_AUDIOLOG: prints every sound effect that was started (frame, id) and the playing track"""
    import struct
    r = runners[0]
    r.core.retro_serialize_size.restype = ct.c_size_t
    n = r.core.retro_serialize_size()
    buf = ct.create_string_buffer(n)
    r.core.retro_serialize(buf, ct.c_size_t(n))
    pos = buf.raw.find(b"TLAU")
    if pos < 0:
        return
    count = struct.unpack_from("<I", buf.raw, pos + 4)[0]
    frames = struct.unpack_from("<96I", buf.raw, pos + 8)
    ids = struct.unpack_from("<96I", buf.raw, pos + 8 + 384)
    voices, reactions = struct.unpack_from("<2I", buf.raw, pos + 8 + 768 + 4)
    print("AUDIOLOG voice blips played:", voices, " reactions played:", reactions)
    print("AUDIOLOG sfx started (audio frame, sfx id):", [(frames[i], ids[i]) for i in range(min(count, 96))])


def done():
    audio_log()
    if not chunks:
        print("no audio captured")
        return
    x = np.concatenate(chunks).astype(np.float64).reshape(-1, 2).mean(axis=1) / 32768
    wav = out_mp3.replace(".mp3", ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(32768)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "160k", out_mp3], check=True)
    hop = 16384
    line = "".join(" .:-=+*#%@"[min(9, int(np.sqrt(np.mean(x[i:i + hop] ** 2)) * 28))] for i in range(0, len(x) - hop, hop))
    print("AUDIO %.1f s peak %.1f dBFS" % (len(x) / 32768, 20 * np.log10(np.max(np.abs(x)) + 1e-9)))
    print("AUDIO", line)


atexit.register(done)
sys.argv = [os.path.join(TOOLS, "playtest_driver.py")] + sys.argv[2:]
runpy.run_path(os.path.join(TOOLS, "playtest_driver.py"), run_name="__main__")
