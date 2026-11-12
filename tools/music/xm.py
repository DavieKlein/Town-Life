"""Minimal FastTracker 2 .xm writer (8-bit samples, linear frequencies). numpy only."""
import struct
import numpy as np

NOTE_OFF = 97


class Sample:
    def __init__(self, data, rel=0, finetune=0, loop=None, vol=64, name=""):
        # data: float array -1..1 (quantised to 8 bit here); loop = (start, length) or None
        d = np.clip(np.round(np.asarray(data, float) * 127), -128, 127).astype(np.int8)
        self.data, self.rel, self.ft, self.loop, self.vol, self.name = d, int(rel), int(finetune), loop, vol, name


class Instrument:
    def __init__(self, name, samples, keymap=None, env=None, fadeout=0, vib=None):
        # samples: list of Sample; keymap: list of 96 sample indices (default all 0)
        # env: list of (tick, value) volume envelope points, sustain at point 0 (release after key-off)
        # vib: (sweep, depth, rate) auto-vibrato (sine)
        self.name, self.samples = name[:22], samples
        self.keymap = keymap or [0] * 96
        self.env, self.fadeout, self.vib = env, fadeout, vib


def _inst_bytes(ins):
    n = len(ins.samples)
    out = struct.pack("<I22sBH", 263 if n else 29, ins.name.encode().ljust(22, b"\0"), 0, n)
    if not n:
        return out
    out += struct.pack("<I", 40)
    out += bytes(ins.keymap)
    pts = ins.env or []
    venv = b"".join(struct.pack("<HH", x, y) for x, y in pts).ljust(48, b"\0")
    out += venv + b"\0" * 48
    vtype = 3 if pts else 0  # on + sustain (sustain point 0)
    sweep, depth, rate = ins.vib if ins.vib else (0, 0, 0)
    out += struct.pack("<BBBBBBBB", len(pts), 0, 0, 0, 0, 0, 0, 0)  # npts, npan, vsus, vls, vle, psus, pls, ple
    out += struct.pack("<BBBBBB", vtype, 0, 0, sweep, depth, rate)
    out += struct.pack("<H", ins.fadeout)
    out += b"\0" * 22
    for s in ins.samples:
        typ, ls, ll = 0, 0, 0
        if s.loop:
            typ, (ls, ll) = 1, s.loop
        out += struct.pack("<IIIBbBBbB22s", len(s.data), ls, ll, s.vol, s.ft, typ, 128, s.rel, 0,
                           s.name.encode()[:22].ljust(22, b"\0"))
    for s in ins.samples:
        d = s.data.astype(np.int16)
        delta = np.diff(np.concatenate([[0], d])).astype(np.int16)
        out += (delta & 0xFF).astype(np.uint8).tobytes()
    return out


def _pack_row(cell):
    note, inst, vol, fx, fxp = cell
    if not (note or inst or vol or fx or fxp):
        return b"\x80"
    f = 0x80
    b = b""
    if note:
        f |= 1; b += bytes([note])
    if inst:
        f |= 2; b += bytes([inst])
    if vol:
        f |= 4; b += bytes([vol])
    if fx or fxp:
        f |= 8 | 16; b += bytes([fx, fxp])
    return bytes([f]) + b


def write_xm(path, title, nch, patterns, order, instruments, bpm, speed=6, restart=0):
    """patterns: list of (rows x nch) lists of (note, inst, vol, fx, fxp); order: list of pattern indices."""
    out = b"Extended Module: " + title.encode()[:20].ljust(20) + b"\x1a" + b"town-life music".ljust(20) + struct.pack("<H", 0x0104)
    hdr = struct.pack("<HHHHHHHH", len(order), restart, nch, len(patterns), len(instruments), 1, speed, bpm)
    hdr += bytes(order).ljust(256, b"\0")
    out += struct.pack("<I", 4 + len(hdr)) + hdr
    for p in patterns:
        data = b"".join(_pack_row(c) for row in p for c in row)
        out += struct.pack("<IBHH", 9, 0, len(p), len(data)) + data
    for ins in instruments:
        out += _inst_bytes(ins)
    with open(path, "wb") as f:
        f.write(out)
    return len(out)
