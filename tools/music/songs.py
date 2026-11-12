"""The five Town Life tracks (v3: real CC0 VCSL samples, smoother arrangements).
Run: python3 tools/music/songs.py OUTDIR  -> city_day.xm, old_block.xm, market.xm, stock_it.xm, plate_rush.xm

The shared "Town motif" (scale degrees 3 5 8 | b7 5, as in "A C F | Eb C" in F) opens every warm track,
so the warm city is recognisable everywhere (see docs/music_plan.md section 2).
v3 changes (owner: "too coarse / not smooth"): recorded instruments instead of synth timbres, fewer simultaneous parts, long legato
notes with soft releases, quiet shaker/cajon instead of snare/hat clatter, a baked-in echo (same notes, 3 rows later, much quieter) on a
spare channel, gentle dynamics.
"""
import os
import sys
from engine import Song, n, check_melody
import synth as S
import sampler as P


def pcs(*names):
    return {n(x + "4") % 12 for x in names}


def C(root, lo, hi, tones):
    return {"root": n(root), "dy": (n(lo), n(hi)), "pcs": pcs(*tones.split())}


def bass_line(song, ch, bar, tmpl, ch_here, ch_next, vol, inst="bass"):
    for (row, k, ln) in tmpl:
        r = ch_here["root"]
        m = {"r": r, "5": r + 7, "o": r + 12, "b7": r + 10, "M7": r + 11, "3": r + 4, "m3": r + 3}.get(k)
        if k == "ap":
            nr = ch_next["root"]
            m = nr - 1 if nr >= r else nr + 1
        song.put(ch, bar, row, m, inst, vol * (0.8 if (row % 4) else 1.0), ln)


def comp(song, chs, bar, chord, rhythm, vol, inst, row0=0):
    lo, hi = chord["dy"]
    for (row, ln, acc) in rhythm:
        v = vol * acc
        song.put(chs[0], bar, row0 + row, lo, inst, v, ln)
        song.put(chs[1], bar, row0 + row, hi, inst, v * 0.95, ln)


def melody(song, ch, bar, notes, inst, vol, echo=None):
    """echo = (channel, delay_rows, instrument, volume scale): the same notes again, quieter and later (baked-in echo)"""
    for (row, name, ln) in notes:
        v = vol * (1.0 if row % 4 == 0 else 0.88)
        song.put(ch, bar, row, n(name), inst, v, ln)
        if echo:
            ech, delay, einst, scale = echo
            r = row + delay
            b = bar + r // 16
            song.put(ech, b, r % 16, n(name), einst, v * scale, max(1, min(ln, 4)))


def chord_pcs(prog):
    return [(b, r0, r1, ch["pcs"]) for b, bar in enumerate(prog) for (r0, r1, ch) in bar]


def index_chords(prog):
    return {(b, r): ch for b, bar in enumerate(prog) for (r0, r1, ch) in bar for r in range(r0, r1)}


# =============================================================================================== City Centre
def city_day(out):
    insts = [P.inst_epiano(), S.inst_bass(), P.inst_vibes(), P.inst_marimba(), P.inst_harmonica()]
    kit = P.drum_kit()
    insts += [kit[k] for k in ("kick", "cajon", "shaker", "hat")]
    song = Song("City Centre day", 104, 24, 7, insts, swing=2)
    song.master = 1.5
    song.gain = {"bass": 0.55, "bass_up": 0.55, "epiano": 1.4, "kick": 1.6, "cajon": 1.6, "shaker": 1.8, "hat": 1.8, "wood": 1.5, "clave": 1.5, "conga": 1.5}

    F9 = C("F2", "A3", "Eb4", "F A C Eb G")
    Bb9 = C("Bb2", "Ab3", "D4", "Bb D F Ab C")
    Gm7 = C("G2", "Bb3", "F4", "G Bb D F A")
    C9 = C("C3", "Bb3", "E4", "C E G Bb D")
    Dm7 = C("D3", "F3", "C4", "D F A C E")
    Gm7lo = C("G2", "F3", "Bb3", "G Bb D F A")
    C9lo = C("C3", "E3", "Bb3", "C E G Bb D")
    Fm7 = C("F2", "E3", "A3", "F A C E G D")
    Am7 = C("A2", "G3", "C4", "A C E G")
    D7 = C("D3", "Gb3", "C4", "D F# A C E")
    C7s = C("C3", "F3", "Bb3", "C F G Bb")
    F9lo = C("F2", "Eb3", "A3", "F A C Eb G")
    A1 = [[(0, 16, F9)], [(0, 16, Bb9)], [(0, 16, F9)], [(0, 8, Gm7), (8, 16, C9)]]
    A2 = [[(0, 16, F9)], [(0, 16, Bb9)], [(0, 8, Am7), (8, 16, D7)], [(0, 8, Gm7lo), (8, 16, C9lo)]]
    B1 = [[(0, 16, Dm7)], [(0, 16, Gm7lo)], [(0, 16, C9lo)], [(0, 16, Fm7)]]
    B2 = [[(0, 16, Dm7)], [(0, 16, Gm7lo)], [(0, 8, C7s), (8, 16, C9lo)], [(0, 16, F9lo)]]
    prog = A1 + A1 + A2 + B1 + B2 + A1
    chord_at = index_chords(prog)

    def nextc(b, r1):
        return chord_at.get(((b + 1) % 24, 0)) if r1 >= 16 else chord_at.get((b, r1))

    # ---- drums: soft. ch0 kick / cajon backbeat, ch1 shaker (+ a few closed hats)
    for b in range(24):
        sect = b // 4
        d = song.drum_line
        if sect == 0:
            d(0, b, "x.......x.......", "kick", {"x": 34})
            d(1, b, "s...s...s...s...", "shaker", {"s": 14})
        elif sect in (1, 2, 5):
            d(0, b, "x.......x..x....", "kick", {"x": 38})
            d(0, b, "....c.......c...", "cajon", {"c": 26})
            d(1, b, "s.s.s.s.s.s.s.s.", "shaker", {"s": 16})
            song.put(1, b, 14, 60, "hat", 14, None)
        else:
            d(0, b, "x.......x.......", "kick", {"x": 32})
            d(0, b, "............c...", "cajon", {"c": 18})
            d(1, b, "s...s...s...s...", "shaker", {"s": 14})
    # ---- bass (ch 2): long soft notes
    sparse = [(0, "r", 6), (8, "5", 4), (12, "b7", 2), (14, "ap", 2)]
    easy = [(0, "r", 5), (6, "r", 2), (8, "5", 3), (11, "b7", 2), (14, "ap", 2)]
    walk = [(0, "r", 4), (4, "5", 4), (8, "o", 4), (12, "5", 2), (14, "ap", 2)]
    half1 = [(0, "r", 4), (4, "5", 3)]
    half2 = [(0, "r", 4), (4, "ap", 3)]
    for b in range(24):
        sect = b // 4
        segs = prog[b]
        if len(segs) == 2:
            for k, (r0, r1, chd) in enumerate(segs):
                tm = [(r0 + rr, kk, ll) for (rr, kk, ll) in (half1 if k == 0 else half2)]
                bass_line(song, 2, b, tm, chd, nextc(b, r1), 56)
        else:
            tm = sparse if sect == 0 else (walk if sect in (3, 4) else easy)
            bass_line(song, 2, b, tm, segs[0][2], nextc(b, 16), 56)
    # ---- electric piano (ch 3, 4): sparse, legato dyads
    rh_intro = [(0, 8, 0.9), (10, 6, 0.8)]
    rh_main = [(0, 6, 1.0), (6, 4, 0.75), (10, 6, 0.85)]
    rh_pad = [(0, 8, 0.85), (8, 8, 0.8)]
    for b in range(24):
        sect = b // 4
        rh = {0: rh_intro, 1: rh_main, 2: rh_main, 3: rh_pad, 4: rh_main, 5: rh_main}[sect]
        for (r0, r1, chd) in prog[b]:
            if r1 - r0 == 16:
                comp(song, (3, 4), b, chd, rh, 40, "epiano")
            else:
                comp(song, (3, 4), b, chd, [(0, 4, 1.0), (4, 4, 0.7)], 40, "epiano", row0=r0)
    # ---- lead: vibraphone hook (ch 5) with marimba echo (ch 6); harmonica sings the B section
    hookA = [
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 6), (10, "Eb5", 2), (12, "C5", 4)],
        [(0, "Bb4", 2), (2, "D5", 2), (4, "F5", 4), (8, "D5", 2), (10, "C5", 2), (12, "Bb4", 4)],
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 4), (8, "G5", 2), (10, "A5", 2), (12, "G5", 4)],
        [(0, "G5", 4), (4, "D5", 4), (8, "G5", 2), (10, "E5", 2), (12, "C5", 4)],
    ]
    hookB = [
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 6), (10, "Eb5", 2), (12, "F5", 2), (14, "G5", 2)],
        [(0, "D5", 2), (2, "F5", 2), (4, "F5", 4), (8, "Ab5", 2), (10, "F5", 2), (12, "D5", 4)],
        [(0, "E5", 4), (4, "C5", 2), (6, "A4", 2), (8, "F#5", 2), (10, "A5", 2), (12, "F#5", 2), (14, "D5", 2)],
        [(0, "G5", 2), (2, "F5", 2), (4, "D5", 4), (8, "E5", 2), (10, "G5", 2), (12, "E5", 4)],
    ]
    bm1 = [
        [(0, "F5", 6), (6, "E5", 2), (8, "D5", 4), (12, "A4", 4)],
        [(0, "Bb4", 4), (4, "D5", 4), (8, "F5", 6), (14, "D5", 2)],
        [(0, "E5", 4), (4, "G5", 4), (8, "G5", 4), (12, "E5", 2), (14, "D5", 2)],
        [(0, "C5", 4), (4, "E5", 4), (8, "F5", 8)],
    ]
    bm2 = [
        [(0, "A4", 2), (2, "D5", 2), (4, "F5", 4), (8, "E5", 4), (12, "D5", 4)],
        [(0, "Bb4", 2), (2, "D5", 2), (4, "F5", 4), (8, "G5", 4), (12, "F5", 2), (14, "D5", 2)],
        [(0, "F5", 4), (4, "G5", 4), (8, "E5", 4), (12, "C5", 4)],
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 6), (10, "Eb5", 2), (12, "C5", 2), (14, "A4", 2)],
    ]
    echo = (6, 3, "marimba", 0.30)
    for i in range(4):
        melody(song, 5, 4 + i, hookA[i], "vibes", 46, echo)
        melody(song, 5, 8 + i, hookB[i], "vibes", 46, echo)
        melody(song, 5, 12 + i, bm1[i], "harmonica", 34, (6, 3, "vibes", 0.25))
        melody(song, 5, 16 + i, bm2[i], "harmonica", 34, (6, 3, "vibes", 0.25))
        melody(song, 5, 20 + i, hookA[i], "vibes", 50, echo)
    cl = chord_pcs(prog)
    print("city_day melody check:")
    check_melody(song, 5, cl, {5, 7, 9, 10, 0, 2, 3, 4}, "lead")
    return song.build(os.path.join(out, "city_day.xm"))


# =============================================================================================== Old Block
def old_block(out):
    insts = [P.inst_strum(), S.inst_bass(upright=True), P.inst_harmonica(), P.inst_marimba(), P.inst_vibes()]
    kit = P.drum_kit()
    insts += [kit[k] for k in ("kick", "cajon", "shaker", "conga")]
    song = Song("Old Block street", 96, 24, 7, insts, swing=2)
    song.master = 1.5
    song.gain = {"bass": 0.55, "bass_up": 0.55, "epiano": 1.4, "kick": 1.6, "cajon": 1.6, "shaker": 1.8, "hat": 1.8, "wood": 1.5, "clave": 1.5, "conga": 1.5}

    D = C("D2", "A3", "F#4", "D F# A")
    G = C("G2", "B3", "G4", "G B D")
    Em7 = C("E2", "G3", "D4", "E G B D")
    A7 = C("A2", "C#4", "G4", "A C# E G")
    Bm = C("B2", "B3", "F#4", "B D F#")
    A = C("A2", "C#4", "E4", "A C# E")
    A7s = C("A2", "D4", "G4", "A D E G")
    for ch in (D, G, Em7, A7, Bm, A, A7s):
        ch["root"] += 12      # octave up: phone speakers lose < 150 Hz
    P1 = [[(0, 16, D)], [(0, 16, G)], [(0, 16, D)], [(0, 8, Em7), (8, 16, A7)]]
    P2 = [[(0, 16, D)], [(0, 16, G)], [(0, 16, Bm)], [(0, 8, Em7), (8, 16, A7)]]
    P3 = [[(0, 16, Bm)], [(0, 16, Em7)], [(0, 16, A)], [(0, 16, D)]]
    P4 = [[(0, 16, Bm)], [(0, 16, Em7)], [(0, 8, A7s), (8, 16, A7)], [(0, 16, D)]]
    prog = P1 + P1 + P2 + P3 + P4 + P1
    chord_at = index_chords(prog)

    for b in range(24):
        sect = b // 4
        d = song.drum_line
        d(0, b, "k.......k.......", "kick", {"k": 30})
        if sect >= 1:
            d(0, b, "....c.......c...", "cajon", {"c": 22})
        d(1, b, "s...s...s...s..." if sect != 3 else "s.......s.......", "shaker", {"s": 15})
        if sect in (2, 4, 5) and b % 2 == 1:
            song.put(1, b, 15, 60, "conga", 16, None)
    # bass: oom-pah, long soft notes
    for b in range(24):
        sect = b // 4
        for (r0, r1, chd) in prog[b]:
            r, fifth = chd["root"], chd["root"] + 7
            if r1 - r0 == 16:
                song.put(2, b, r0, r, "bass_up", 56, 5)
                song.put(2, b, r0 + 8, fifth, "bass_up", 50, 5)
                nxt = chd["root"]
                if sect >= 2:
                    nc = chord_at.get(((b + 1) % 24, 0))
                    nr = nc["root"]
                    song.put(2, b, 14, nr - 1 if nr >= r else nr + 1, "bass_up", 38, 2)
            else:
                song.put(2, b, r0, r, "bass_up", 54, 3)
                song.put(2, b, r0 + 4, fifth, "bass_up", 46, 3)
    # guitar (strumstick) dyads on beats 2 and 4, second string 1 tick later (a soft strum), long notes
    for b in range(24):
        sect = b // 4
        for (r0, r1, chd) in prog[b]:
            lo, hi = chd["dy"]
            hits = [4, 12] if r1 - r0 == 16 else ([r0 + 4] if r0 == 0 else [12])
            for rr in hits:
                song.put(3, b, rr, lo, "strum", 40 if rr % 8 == 4 else 30, 6)
                song.put(4, b, rr, hi, "strum", 38 if rr % 8 == 4 else 28, 6, delay=1)
    hookP1 = [
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 6), (10, "C5", 2), (12, "A4", 4)],
        [(0, "G4", 2), (2, "B4", 2), (4, "D5", 4), (8, "B4", 2), (10, "A4", 2), (12, "G4", 4)],
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 4), (8, "E5", 2), (10, "F#5", 2), (12, "E5", 4)],
        [(0, "E5", 4), (4, "B4", 4), (8, "C#5", 2), (10, "E5", 2), (12, "A4", 4)],
    ]
    hookP2 = [
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 6), (10, "C5", 2), (12, "D5", 2), (14, "E5", 2)],
        [(0, "B4", 2), (2, "D5", 2), (4, "G5", 4), (8, "F#5", 2), (10, "D5", 2), (12, "B4", 4)],
        [(0, "F#5", 4), (4, "D5", 4), (8, "B4", 4), (12, "D5", 2), (14, "C#5", 2)],
        [(0, "G5", 2), (2, "E5", 2), (4, "B4", 4), (8, "C#5", 2), (10, "E5", 2), (12, "G5", 2), (14, "F#5", 2)],
    ]
    bm1 = [
        [(0, "D5", 6), (6, "C#5", 2), (8, "B4", 4), (12, "F#4", 4)],
        [(0, "E5", 4), (4, "G5", 4), (8, "B4", 6), (14, "A4", 2)],
        [(0, "C#5", 4), (4, "E5", 4), (8, "A5", 4), (12, "E5", 2), (14, "C#5", 2)],
        [(0, "A4", 4), (4, "D5", 4), (8, "D5", 8)],
    ]
    bm2 = [
        [(0, "F#4", 2), (2, "B4", 2), (4, "D5", 4), (8, "F#5", 4), (12, "D5", 4)],
        [(0, "B4", 2), (2, "E5", 2), (4, "G5", 4), (8, "F#5", 4), (12, "E5", 4)],
        [(0, "D5", 4), (4, "E5", 4), (8, "C#5", 4), (12, "A4", 4)],
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 6), (10, "C5", 2), (12, "A4", 4)],
    ]
    echo = (6, 3, "vibes", 0.22)
    for i in range(4):
        melody(song, 5, i, hookP1[i], "marimba", 38)                         # intro: the motif on a soft marimba
        melody(song, 5, 4 + i, hookP1[i], "harmonica", 36, echo)             # harmonica = the accordion voice of Old Block
        melody(song, 5, 8 + i, hookP2[i], "harmonica", 36, echo)
        melody(song, 5, 12 + i, bm1[i], "harmonica", 34, echo)
        melody(song, 5, 16 + i, bm2[i], "harmonica", 34, echo)
        melody(song, 5, 20 + i, hookP1[i], "harmonica", 38, echo)
    cl = chord_pcs(prog)
    print("old_block melody check:")
    check_melody(song, 5, cl, {2, 4, 6, 7, 9, 11, 0, 1}, "lead")
    return song.build(os.path.join(out, "old_block.xm"))


# =============================================================================================== Market (interiors)
def market(out):
    insts = [P.inst_epiano(), S.inst_bass(), P.inst_marimba(), P.inst_vibes()]
    kit = P.drum_kit()
    insts += [kit[k] for k in ("kick", "cajon", "shaker")]
    song = Song("Corner Market", 108, 16, 7, insts, swing=2)
    song.master = 1.5
    song.gain = {"bass": 0.55, "bass_up": 0.55, "epiano": 1.4, "kick": 1.6, "cajon": 1.6, "shaker": 1.8, "hat": 1.8, "wood": 1.5, "clave": 1.5, "conga": 1.5}

    C6 = C("C3", "E4", "A4", "C E G A")
    Fm7 = C("F2", "E4", "A4", "F A C E G")
    Dm7 = C("D3", "C4", "F4", "D F A C E")
    G7 = C("G2", "B3", "F4", "G B D F")
    G7s = C("G2", "C4", "F4", "G C D F")
    Em7 = C("E3", "D4", "G4", "E G B D")
    Am7 = C("A2", "C4", "G4", "A C E G")
    F6 = C("F2", "A3", "D4", "F A C D")
    A7 = C("A2", "C#4", "G4", "A C# E G")
    D9 = C("D3", "C4", "F#4", "D F# A C E")
    prog = [
        [(0, 16, C6)], [(0, 16, Fm7)], [(0, 16, C6)], [(0, 8, Dm7), (8, 16, G7)],
        [(0, 16, Em7)], [(0, 16, Am7)], [(0, 16, Dm7)], [(0, 8, G7s), (8, 16, G7)],
        [(0, 16, C6)], [(0, 16, F6)], [(0, 8, Em7), (8, 16, A7)], [(0, 8, Dm7), (8, 16, G7)],
        [(0, 16, Am7)], [(0, 16, D9)], [(0, 8, Dm7), (8, 16, G7)], [(0, 12, C6), (12, 16, G7)],
    ]
    chord_at = index_chords(prog)
    for b in range(16):
        d = song.drum_line
        d(0, b, "k.......k.......", "kick", {"k": 28})
        d(0, b, "............c...", "cajon", {"c": 16}) if b % 2 else None
        d(1, b, "s...s...s...s...", "shaker", {"s": 13})
    for b in range(16):
        for (r0, r1, chd) in prog[b]:
            r = chd["root"]
            nx = chord_at[((b + 1) % 16, 0)]["root"]
            ap = nx - 1 if nx >= r else nx + 1
            if r1 - r0 >= 12:
                for (rr, m, ln) in [(0, r, 5), (6, r + 7, 2), (8, r + 12, 4), (12, r + 7, 2)]:
                    song.put(2, b, r0 + rr, m, "bass", 50 if rr % 4 == 0 else 40, ln)
                if r1 == 16:
                    song.put(2, b, 14, ap, "bass", 36, 2)
            else:
                song.put(2, b, r0, r, "bass", 50, 4)
                song.put(2, b, r0 + 4, r + 7, "bass", 40, 3)
    for b in range(16):
        for (r0, r1, chd) in prog[b]:
            if r1 - r0 >= 12:
                comp(song, (3, 4), b, chd, [(0, 6, 1.0), (8, 8, 0.8)], 36, "epiano", row0=r0)
            else:
                comp(song, (3, 4), b, chd, [(0, 6, 1.0)], 36, "epiano", row0=r0)
    mel = [
        [(0, "E4", 2), (2, "G4", 2), (4, "C5", 6), (10, "Bb4", 2), (12, "G4", 4)],
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 4), (8, "E5", 2), (10, "C5", 2), (12, "A4", 4)],
        [(0, "E4", 2), (2, "G4", 2), (4, "C5", 4), (8, "D5", 2), (10, "E5", 2), (12, "G5", 4)],
        [(0, "F5", 2), (2, "E5", 2), (4, "D5", 4), (8, "B4", 2), (10, "D5", 2), (12, "G4", 4)],
        [(0, "G5", 4), (4, "E5", 4), (8, "B4", 4), (12, "D5", 4)],
        [(0, "C5", 4), (4, "E5", 4), (8, "A4", 4), (12, "E5", 4)],
        [(0, "D5", 4), (4, "F5", 4), (8, "A4", 4), (12, "C5", 4)],
        [(0, "D5", 4), (4, "C5", 4), (8, "B4", 4), (12, "D5", 4)],
        [(0, "E4", 2), (2, "G4", 2), (4, "C5", 6), (10, "Bb4", 2), (12, "G4", 2), (14, "A4", 2)],
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 4), (8, "D5", 2), (10, "C5", 2), (12, "A4", 4)],
        [(0, "G4", 2), (2, "B4", 2), (4, "E5", 4), (8, "C#5", 2), (10, "E5", 2), (12, "A4", 4)],
        [(0, "F5", 2), (2, "D5", 2), (4, "A4", 4), (8, "B4", 2), (10, "D5", 2), (12, "F5", 4)],
        [(0, "E5", 4), (4, "C5", 4), (8, "A4", 4), (12, "C5", 4)],
        [(0, "F#5", 4), (4, "E5", 4), (8, "C5", 4), (12, "A4", 4)],
        [(0, "F5", 4), (4, "D5", 4), (8, "D5", 2), (10, "B4", 2), (12, "G4", 4)],
        [(0, "C5", 2), (2, "E5", 2), (4, "G5", 4), (8, "E5", 4), (12, "D5", 2), (14, "B4", 2)],
    ]
    for b in range(16):
        melody(song, 5, b, mel[b], "marimba", 46, (6, 3, "vibes", 0.25))
    cl = chord_pcs(prog)
    print("market melody check:")
    check_melody(song, 5, cl, {0, 2, 4, 5, 7, 9, 11, 10}, "lead")
    return song.build(os.path.join(out, "market.xm"))


# =============================================================================================== STOCK IT! minigame
def stock_it(out):
    """G major, 128 BPM, straight: a bouncy sorting groove. Lead: marimba (bars 1-8) then vibraphone with marimba echo."""
    insts = [P.inst_epiano(), S.inst_bass(), P.inst_marimba(), P.inst_vibes()]
    kit = P.drum_kit()
    insts += [kit[k] for k in ("kick", "cajon", "shaker", "clave", "hat")]
    song = Song("STOCK IT", 128, 16, 7, insts, swing=0)
    song.master = 1.5
    song.gain = {"bass": 0.55, "bass_up": 0.55, "epiano": 1.4, "kick": 1.6, "cajon": 1.6, "shaker": 1.8, "hat": 1.8, "wood": 1.5, "clave": 1.5, "conga": 1.5}
    G6 = C("G2", "B3", "E4", "G B D E")
    C6 = C("C3", "E4", "A4", "C E G A")
    D7 = C("D3", "F#4", "C5", "D F# A C")
    Em7 = C("E3", "D4", "G4", "E G B D")
    Am7 = C("A2", "C4", "G4", "A C E G")
    D7b = C("D3", "F#3", "C4", "D F# A C")
    prog = [[(0, 16, G6)], [(0, 16, C6)], [(0, 16, G6)], [(0, 16, D7)],
            [(0, 16, Em7)], [(0, 16, C6)], [(0, 8, Am7), (8, 16, D7b)], [(0, 16, G6)]]
    prog = prog + prog[:6] + [[(0, 8, C6), (8, 16, D7)], [(0, 16, G6)]]
    chord_at = index_chords(prog)
    for b in range(16):
        d = song.drum_line
        d(0, b, "x.......x.x.....", "kick", {"x": 42})
        d(0, b, "....c.......c...", "cajon", {"c": 34})
        d(1, b, "s.s.s.s.s.s.s.s.", "shaker", {"s": 20})
        if b % 2 == 1:
            song.put(1, b, 15, 60, "hat", 22, None)
    for b in range(16):
        for (r0, r1, chd) in prog[b]:
            r = chd["root"]
            nr = chord_at[((b + 1) % 16, 0)]["root"]
            if r1 - r0 == 16:
                for (rr, m, ln) in [(0, r, 2), (3, r + 12, 1), (4, r, 2), (6, r + 7, 2), (8, r, 2), (11, r + 12, 1), (12, r + 7, 2), (14, nr - 1 if nr >= r else nr + 1, 2)]:
                    song.put(2, b, r0 + rr, m, "bass", 52 if rr % 4 == 0 else 42, ln)
            else:
                song.put(2, b, r0, r, "bass", 52, 2)
                song.put(2, b, r0 + 3, r + 12, "bass", 40, 1)
                song.put(2, b, r0 + 4, r + 7, "bass", 44, 2)
    for b in range(16):
        for (r0, r1, chd) in prog[b]:
            rows = [(2, 2, 1.0), (6, 2, 0.8), (10, 2, 0.9), (14, 2, 0.7)] if r1 - r0 == 16 else ([(2, 2, 1.0), (6, 2, 0.8)])
            comp(song, (3, 4), b, chd, rows, 36, "epiano", row0=r0)
    mel = [
        [(0, "B4", 2), (2, "D5", 2), (4, "G5", 4), (8, "F5", 2), (10, "D5", 2), (12, "B4", 4)],
        [(0, "C5", 2), (2, "E5", 2), (4, "G5", 4), (8, "E5", 2), (10, "C5", 2), (12, "G4", 4)],
        [(0, "B4", 2), (2, "D5", 2), (4, "G5", 4), (8, "A5", 2), (10, "G5", 2), (12, "D5", 4)],
        [(0, "F#5", 4), (4, "A5", 2), (6, "F#5", 2), (8, "D5", 4), (12, "A4", 4)],
        [(0, "G5", 4), (4, "E5", 4), (8, "B4", 4), (12, "E5", 4)],
        [(0, "E5", 4), (4, "G5", 4), (8, "E5", 4), (12, "C5", 4)],
        [(0, "A4", 2), (2, "C5", 2), (4, "E5", 4), (8, "F#5", 2), (10, "A5", 2), (12, "D5", 4)],
        [(0, "B4", 2), (2, "D5", 2), (4, "G5", 8), (12, "D5", 4)],
        [(0, "B4", 2), (2, "D5", 2), (4, "G5", 4), (8, "F5", 2), (10, "D5", 2), (12, "B4", 4)],
        [(0, "C5", 2), (2, "E5", 2), (4, "G5", 4), (8, "E5", 2), (10, "C5", 2), (12, "G4", 4)],
        [(0, "B4", 2), (2, "D5", 2), (4, "G5", 4), (8, "A5", 2), (10, "G5", 2), (12, "D5", 4)],
        [(0, "F#5", 4), (4, "A5", 2), (6, "F#5", 2), (8, "D5", 4), (12, "A4", 4)],
        [(0, "G5", 4), (4, "E5", 4), (8, "B4", 4), (12, "E5", 4)],
        [(0, "E5", 4), (4, "G5", 4), (8, "E5", 4), (12, "C5", 4)],
        [(0, "G5", 4), (4, "E5", 2), (6, "C5", 2), (8, "F#5", 4), (12, "A5", 4)],
        [(0, "G5", 6), (8, "D5", 4), (12, "B4", 4)],
    ]
    for b in range(16):
        inst = "marimba" if b < 8 else "vibes"
        melody(song, 5, b, mel[b], inst, 46, (6, 3, "marimba" if b >= 8 else "vibes", 0.25))
    for b in range(16):
        if b % 4 == 3:
            song.put(0, b, 15, 60, "clave", 30, None)
    cl = chord_pcs(prog)
    print("stock_it melody check:")
    check_melody(song, 5, cl, {7, 9, 11, 0, 2, 4, 5, 6}, "lead")
    return song.build(os.path.join(out, "stock_it.xm"))


# =============================================================================================== PLATE RUSH minigame
def plate_rush(out):
    """D major, 136 BPM, swung: a busy-but-friendly kitchen. Walking upright bass, wood-block ticks, cajon backbeat, marimba lead."""
    insts = [P.inst_epiano(), S.inst_bass(upright=True), P.inst_marimba(), P.inst_vibes()]
    kit = P.drum_kit()
    insts += [kit[k] for k in ("kick", "cajon", "shaker", "wood", "hat")]
    song = Song("PLATE RUSH", 136, 16, 7, insts, swing=2)
    song.master = 1.5
    song.gain = {"bass": 0.55, "bass_up": 0.55, "epiano": 1.4, "kick": 1.6, "cajon": 1.6, "shaker": 1.8, "hat": 1.8, "wood": 1.5, "clave": 1.5, "conga": 1.5}
    D9 = C("D3", "F#3", "C4", "D F# A C E")
    G9 = C("G2", "B3", "F4", "G B D F A")
    A7 = C("A2", "C#4", "G4", "A C# E G")
    Bm7 = C("B2", "A3", "D4", "B D F# A")
    E9 = C("E3", "G#3", "D4", "E G# B D F#")
    Em7 = C("E3", "D4", "G4", "E G B D")
    D6 = C("D3", "F#3", "B3", "D F# A B")
    prog = [[(0, 16, D9)], [(0, 16, G9)], [(0, 16, D9)], [(0, 16, A7)],
            [(0, 16, Bm7)], [(0, 16, E9)], [(0, 8, Em7), (8, 16, A7)], [(0, 16, D6)],
            [(0, 16, G9)], [(0, 16, G9)], [(0, 16, D9)], [(0, 16, Bm7)],
            [(0, 16, E9)], [(0, 16, A7)], [(0, 8, Em7), (8, 16, A7)], [(0, 16, D9)]]
    chord_at = index_chords(prog)
    for b in range(16):
        d = song.drum_line
        d(0, b, "x.......x..x....", "kick", {"x": 36})
        d(0, b, "....c.......c..c", "cajon", {"c": 30})
        d(1, b, "s.s.s.s.s.s.s.s.", "shaker", {"s": 17})
        if b % 2 == 0:
            song.put(1, b, 7, 60, "wood", 20, None)
            song.put(1, b, 13, 60, "wood", 16, None)
    # walking bass: quarter notes root - 3rd/5th - octave - approach
    for b in range(16):
        for (r0, r1, chd) in prog[b]:
            r = chd["root"]
            nr = chord_at[((b + 1) % 16, 0)]["root"]
            ap = nr - 1 if nr >= r else nr + 1
            if r1 - r0 == 16:
                steps = [(0, r), (4, r + 7), (8, r + 12), (12, ap if nr != r else r + 10)]
            else:
                steps = [(0, r), (4, r + 7)] if r0 == 0 else [(0, r), (4, ap)]
            for (rr, m) in steps:
                song.put(2, b, r0 + rr, m, "bass_up", 54, 3)
    for b in range(16):
        for (r0, r1, chd) in prog[b]:
            rows = [(0, 3, 1.0), (6, 2, 0.8), (10, 3, 0.9), (14, 2, 0.7)] if r1 - r0 == 16 else [(0, 3, 1.0), (6, 2, 0.8)]
            comp(song, (3, 4), b, chd, rows, 36, "epiano", row0=r0)
    mel = [
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 4), (8, "C5", 2), (10, "A4", 2), (12, "F#4", 4)],
        [(0, "G4", 2), (2, "B4", 2), (4, "D5", 4), (8, "F5", 2), (10, "D5", 2), (12, "B4", 4)],
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 4), (8, "E5", 2), (10, "F#5", 2), (12, "E5", 4)],
        [(0, "E5", 2), (2, "C#5", 2), (4, "A4", 4), (8, "C#5", 2), (10, "E5", 2), (12, "G5", 4)],
        [(0, "F#5", 4), (4, "D5", 4), (8, "B4", 4), (12, "D5", 4)],
        [(0, "G#4", 2), (2, "B4", 2), (4, "E5", 4), (8, "D5", 2), (10, "B4", 2), (12, "G#4", 4)],
        [(0, "G5", 2), (2, "E5", 2), (4, "B4", 4), (8, "C#5", 2), (10, "E5", 2), (12, "A5", 4)],
        [(0, "F#5", 4), (4, "D5", 4), (8, "A4", 4), (12, "D5", 4)],
        [(0, "B4", 2), (2, "D5", 2), (4, "G5", 4), (8, "F5", 2), (10, "D5", 2), (12, "B4", 4)],
        [(0, "A4", 2), (2, "B4", 2), (4, "D5", 4), (8, "G5", 2), (10, "F5", 2), (12, "D5", 4)],
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 4), (8, "C5", 2), (10, "A4", 2), (12, "F#4", 4)],
        [(0, "D5", 4), (4, "B4", 4), (8, "F#5", 4), (12, "D5", 4)],
        [(0, "E5", 4), (4, "G#5", 4), (8, "B4", 4), (12, "D5", 4)],
        [(0, "E5", 2), (2, "A4", 2), (4, "C#5", 4), (8, "E5", 4), (12, "A4", 4)],
        [(0, "G5", 2), (2, "E5", 2), (4, "B4", 4), (8, "C#5", 2), (10, "E5", 2), (12, "G5", 4)],
        [(0, "F#5", 4), (4, "D5", 4), (8, "A4", 4), (12, "F#4", 4)],
    ]
    for b in range(16):
        melody(song, 5, b, mel[b], "marimba" if b < 8 else "vibes", 46, (6, 3, "vibes" if b < 8 else "marimba", 0.25))
    cl = chord_pcs(prog)
    print("plate_rush melody check:")
    check_melody(song, 5, cl, {2, 4, 6, 7, 9, 11, 0, 1}, "lead")
    return song.build(os.path.join(out, "plate_rush.xm"))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for fn in (city_day, old_block, market, stock_it, plate_rush):
        print(fn.__name__, fn(out), "bytes")
