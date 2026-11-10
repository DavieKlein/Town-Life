#!/usr/bin/env python3
"""
Headless GBA test runner for Town Life (development tool, not part of the build).

Runs the ROM in the mGBA libretro core (the same core Lemuroid uses), feeds scripted input
and saves screenshots, so you can check a build without a phone.

Setup (Debian/Ubuntu container):   apt-get install -y libretro-mgba   (and Pillow for PNGs)

Usage:
  python3 tools/headless_run.py town-life.gba "wait 60; shot start.png; hold right 90; shot r.png"

Commands (separated by ';'):
  wait N               run N frames without input
  hold KEYS N          hold keys (e.g. right, up+b) for N frames
  press KEYS           hold keys for 2 frames, then release for 2 frames
  shot FILE            save the current frame as a PNG
  dumpsram FILE        write the cartridge save RAM to FILE
  loadsram FILE        load FILE into the cartridge save RAM (use before the game reads it, e.g. as the
                       first command, followed by `reset`)
  clearsram            fill the save RAM with 0xFF (an empty cartridge)
  reset                reset the console (back to the title screen), keeping the save RAM
Keys: a b select start up down left right l r
"""

import ctypes as ct
import sys

CORE = "/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so"
KEYS = {"b": 0, "y": 1, "select": 2, "start": 3, "up": 4, "down": 5, "left": 6, "right": 7,
        "a": 8, "x": 9, "l": 10, "r": 11}

ENV_CB = ct.CFUNCTYPE(ct.c_bool, ct.c_uint, ct.c_void_p)
VIDEO_CB = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_uint, ct.c_uint, ct.c_size_t)
AUDIO_CB = ct.CFUNCTYPE(None, ct.c_int16, ct.c_int16)
AUDIO_BATCH_CB = ct.CFUNCTYPE(ct.c_size_t, ct.c_void_p, ct.c_size_t)
POLL_CB = ct.CFUNCTYPE(None)
STATE_CB = ct.CFUNCTYPE(ct.c_int16, ct.c_uint, ct.c_uint, ct.c_uint, ct.c_uint)


class GameInfo(ct.Structure):
    _fields_ = [("path", ct.c_char_p), ("data", ct.c_void_p), ("size", ct.c_size_t), ("meta", ct.c_char_p)]


class Runner:
    def __init__(self, rom_path):
        self.core = ct.CDLL(CORE)
        self.pixel_format = 0
        self.frame = None
        self.held = set()
        self._dir = ct.c_char_p(b"/tmp")

        def env(cmd, data):
            if cmd == 10:          # SET_PIXEL_FORMAT
                self.pixel_format = ct.cast(data, ct.POINTER(ct.c_int))[0]
                return True
            if cmd in (9, 31):     # GET_SYSTEM_DIRECTORY / GET_SAVE_DIRECTORY
                ct.cast(data, ct.POINTER(ct.c_char_p))[0] = self._dir.value
                return True
            return False

        def video(data, w, h, pitch):
            if data:
                self.frame = (ct.string_at(data, pitch * h), w, h, pitch)

        def state(port, device, index, ident):
            return 1 if (port == 0 and device == 1 and ident in self.held) else 0

        self._cbs = [ENV_CB(env), VIDEO_CB(video), AUDIO_CB(lambda l, r: None),
                     AUDIO_BATCH_CB(lambda d, n: n), POLL_CB(lambda: None), STATE_CB(state)]
        self.core.retro_set_environment(self._cbs[0])
        self.core.retro_set_video_refresh(self._cbs[1])
        self.core.retro_set_audio_sample(self._cbs[2])
        self.core.retro_set_audio_sample_batch(self._cbs[3])
        self.core.retro_set_input_poll(self._cbs[4])
        self.core.retro_set_input_state(self._cbs[5])
        self.core.retro_init()
        rom = open(rom_path, "rb").read()
        self._rom = ct.create_string_buffer(rom, len(rom))
        info = GameInfo(rom_path.encode(), ct.cast(self._rom, ct.c_void_p), len(rom), None)
        if not self.core.retro_load_game(ct.byref(info)):
            raise RuntimeError("retro_load_game failed")

    def run(self, frames):
        for _ in range(frames):
            self.core.retro_run()

    def _sram(self):
        self.core.retro_get_memory_data.restype = ct.c_void_p
        self.core.retro_get_memory_size.restype = ct.c_size_t
        ptr = self.core.retro_get_memory_data(0)       # RETRO_MEMORY_SAVE_RAM
        size = self.core.retro_get_memory_size(0)
        if not ptr or not size:
            raise RuntimeError("no save RAM exposed by the core (SRAM not detected?)")
        return ptr, size

    def dump_sram(self, path):
        ptr, size = self._sram()
        open(path, "wb").write(ct.string_at(ptr, size))
        print("sram", size, "bytes ->", path)

    def load_sram(self, path):
        ptr, size = self._sram()
        data = open(path, "rb").read()[:size]
        ct.memmove(ptr, data, len(data))

    def clear_sram(self):
        ptr, size = self._sram()
        ct.memset(ptr, 0xFF, size)

    def reset(self):
        self.core.retro_reset()

    def screenshot(self, path):
        from PIL import Image
        data, w, h, pitch = self.frame
        img = Image.new("RGB", (w, h))
        px = []
        for y in range(h):
            row = data[y * pitch:(y + 1) * pitch]
            for x in range(w):
                if self.pixel_format == 1:      # XRGB8888
                    b, g, r = row[x * 4], row[x * 4 + 1], row[x * 4 + 2]
                else:                           # RGB565
                    v = row[x * 2] | (row[x * 2 + 1] << 8)
                    r, g, b = (v >> 11) << 3, ((v >> 5) & 63) << 2, (v & 31) << 3
                px.append((r, g, b))
        img.putdata(px)
        img.save(path)


def main():
    runner = Runner(sys.argv[1])
    for cmd in sys.argv[2].split(";"):
        parts = cmd.split()
        if not parts:
            continue
        op = parts[0]
        if op == "wait":
            runner.held = set()
            runner.run(int(parts[1]))
        elif op == "hold":
            runner.held = {KEYS[k] for k in parts[1].split("+")}
            runner.run(int(parts[2]))
            runner.held = set()
        elif op == "press":
            runner.held = {KEYS[k] for k in parts[1].split("+")}
            runner.run(2)
            runner.held = set()
            runner.run(2)
        elif op == "shot":
            runner.screenshot(parts[1])
            print("saved", parts[1])
        elif op == "dumpsram":
            runner.dump_sram(parts[1])
        elif op == "loadsram":
            runner.load_sram(parts[1])
        elif op == "clearsram":
            runner.clear_sram()
        elif op == "reset":
            runner.reset()
        else:
            raise ValueError("unknown command: " + op)


if __name__ == "__main__":
    main()
