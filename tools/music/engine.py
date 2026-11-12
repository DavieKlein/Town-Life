"""Tiny pattern engine on top of xm.py: songs are described bar by bar and written as 64-row XM patterns."""
import os
import re
import xm

NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
ROWS_BAR = 16
PAT_ROWS = 64


def n(name):
    """'F#4' -> MIDI number (C4 = 60)."""
    m = re.fullmatch(r"([A-G])([#b]?)(-?\d)", name)
    pc = NAMES[m.group(1)] + {"#": 1, "b": -1, "": 0}[m.group(2)]
    return (int(m.group(3)) + 1) * 12 + pc


class Song:
    def __init__(self, title, bpm, bars, nch, insts, swing=0):
        self.title, self.bpm, self.bars, self.nch = title, bpm, bars, nch
        self.insts = insts                      # ordered list of xm.Instrument
        self.idx = {i.name: k + 1 for k, i in enumerate(insts)}
        self.rows = bars * ROWS_BAR
        self.swing = swing                      # ticks of delay for swung 8th off-beats (row % 4 == 2)
        self.gain = {}                          # per-instrument volume multiplier
        self.master = 1.0
        self.grid = [[None] * nch for _ in range(self.rows)]
        self.log = []                           # (ch, abs_row, midi, len, inst) for analysis

    def put(self, ch, bar, row, midi, inst, vol, length=None, swing=True, delay=0):
        r = bar * ROWS_BAR + row
        if r >= self.rows:
            return
        note = midi - 11 if midi is not None else 49
        assert 1 <= note <= 96, (midi, inst)
        fx, fxp = 0, 0
        d = delay + (self.swing if (swing and row % 4 == 2) else 0)
        if d:
            fx, fxp = 0x0E, 0xD0 | d
        vol = vol * self.gain.get(inst, 1.0) * self.master
        self.grid[r][ch] = (note, self.idx[inst], 0x10 + max(1, min(64, int(round(vol)))), fx, fxp)
        self.log.append((ch, r, midi, length, inst))
        if length:
            e = r + length
            if e < self.rows and self.grid[e][ch] is None:
                self.grid[e][ch] = (xm.NOTE_OFF, 0, 0, 0, 0)
            elif e >= self.rows and self.grid[0][ch] is None:
                # wrap: release on the first row of the loop (keeps the loop clean)
                self.grid[0][ch] = (xm.NOTE_OFF, 0, 0, 0, 0)

    def drum_line(self, ch, bar, text, inst, vols, swing=True):
        """text: 16 chars per bar ('.' = none, anything else = hit; vols maps char -> volume)."""
        for i, c in enumerate(text):
            if c != ".":
                self.put(ch, bar + i // 16, i % 16, 60, inst, vols[c], None, swing)

    def build(self, path):
        keep = os.environ.get("MUSIC_CH")  # debug: comma list of channels to keep (stem rendering)
        if keep:
            ks = {int(c) for c in keep.split(",")}
            self.grid = [[c if i in ks else None for i, c in enumerate(row)] for row in self.grid]
        pats, order = [], []
        for p in range(self.rows // PAT_ROWS):
            pat = []
            for r in range(p * PAT_ROWS, (p + 1) * PAT_ROWS):
                pat.append([c if c else (0, 0, 0, 0, 0) for c in self.grid[r]])
            pats.append(pat)
            order.append(p)
        return xm.write_xm(path, self.title, self.nch, pats, order, self.insts, self.bpm)


# ---------------------------------------------------------------- analysis helpers
def check_melody(song, ch, chords, scale_pcs, label):
    """chords: list of (bar, row_start, row_end, set_of_pitch_classes). Reports strong-beat non-chord tones."""
    bad = 0
    for (c, r, m, ln, inst) in song.log:
        if c != ch or m is None:
            continue
        bar, row = divmod(r, ROWS_BAR)
        pc = m % 12
        ch_set = None
        for (b, r0, r1, pcs) in chords:
            if b == bar and r0 <= row < r1:
                ch_set = pcs
        if ch_set is None:
            print(f"  [{label}] no chord for bar {bar+1} row {row}")
            continue
        strong = row % 4 == 0
        if pc not in ch_set and (strong or pc not in scale_pcs):
            print(f"  [{label}] bar {bar+1} row {row}: note {m} pc {pc} not in chord {sorted(ch_set)}"
                  f"{' (strong beat)' if strong else ''}")
            bad += 1
    return bad
