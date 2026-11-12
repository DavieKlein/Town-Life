"""The three proposal tracks. Run: python3 tools/music/songs.py OUTDIR  -> writes city_day.xm, old_block.xm, market.xm.

The shared "Town motif" (scale degrees 3 5 8 | b7 5, as in "A C F | Eb C" in F) opens every warm track,
so the warm city is recognisable everywhere (see docs/music_plan.md section 2).
"""
import sys
import os
from engine import Song, n, check_melody
import synth as S


def pcs(*names):
    return {n(x + "4") % 12 for x in names}


# chord: (bass root midi, dyad (lo, hi) midi, pitch-class set for checking melody)
def C(root, lo, hi, tones):
    return {"root": n(root), "dy": (n(lo), n(hi)), "pcs": pcs(*tones.split())}


def bass_line(song, ch, bar, tmpl, ch_here, ch_next, vol, inst="bass"):
    for (row, k, ln) in tmpl:
        r = ch_here["root"]
        if k == "r": m = r
        elif k == "5": m = r + 7
        elif k == "o": m = r + 12
        elif k == "b7": m = r + 10
        elif k == "M7": m = r + 11
        elif k == "3": m = r + 4
        elif k == "m3": m = r + 3
        elif k == "ap":
            nr = ch_next["root"]
            m = nr - 1 if nr >= r else nr + 1
        v = vol * (0.78 if (row % 4) else 1.0)
        song.put(ch, bar, row, m, inst, v, ln)


def comp(song, chs, bar, chord, rhythm, vol, inst, row0=0, dy_shift=0, vol_scale=1.0):
    lo, hi = chord["dy"]
    for (row, ln, acc) in rhythm:
        v = vol * acc * vol_scale
        song.put(chs[0], bar, row0 + row, lo + dy_shift, inst, v, ln)
        song.put(chs[1], bar, row0 + row, hi + dy_shift, inst, v * 0.95, ln)


def melody(song, ch, bar, notes, inst, vol, shift=0):
    for (row, name, ln) in notes:
        song.put(ch, bar, row, n(name) + shift, inst, vol * (1.0 if row % 4 == 0 else 0.88), ln)


# ===================================================================================================
def city_day(out):
    insts = [S.inst_epiano(), S.inst_bass(), S.inst_marimba(), S.inst_vibes(), S.inst_whistle(), S.inst_clav()]
    kit = S.drum_kit()
    insts += [kit[k] for k in ("kick", "snare", "rim", "hat", "ohat", "shaker")]
    song = Song("City Centre day", 104, 24, 8, insts, swing=2)
    song.master = 1.1
    song.gain = {"epiano": 1.5, "shaker": 2.6, "clav": 2.2, "vibes": 1.5, "kick": 1.1, "snare": 1.5, "hat": 2.6, "rim": 1.6,
                 "ohat": 2.2, "bass": 0.75, "whistle": 1.35, "marimba": 1.15}

    F9 = C("F2", "A3", "Eb4", "F A C Eb G")
    Bb9 = C("Bb2", "Ab3", "D4", "Bb D F Ab C")
    F9b = F9
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
    Dm7b = Dm7

    # bar -> list of (row_start, row_end, chord)
    prog = []
    A1 = [[(0, 16, F9)], [(0, 16, Bb9)], [(0, 16, F9)], [(0, 8, Gm7), (8, 16, C9)]]
    A2 = [[(0, 16, F9)], [(0, 16, Bb9)], [(0, 8, Am7), (8, 16, D7)], [(0, 8, Gm7lo), (8, 16, C9lo)]]
    B1 = [[(0, 16, Dm7)], [(0, 16, Gm7lo)], [(0, 16, C9lo)], [(0, 16, Fm7)]]
    B2 = [[(0, 16, Dm7)], [(0, 16, Gm7lo)], [(0, 8, C7s), (8, 16, C9lo)], [(0, 16, F9lo)]]
    prog = A1 + A1 + A2 + B1 + B2 + A1
    # section 2 (bars 9-12) uses A2 variation; keep order: P0 A1, P1 A1, P2 A2, P3 B1, P4 B2, P5 A1
    spans = [(b, r0, r1, ch) for b, bar in enumerate(prog) for (r0, r1, ch) in bar]
    chord_at = {}
    for (b, r0, r1, ch) in spans:
        for r in range(r0, r1):
            chord_at[(b, r)] = ch

    def nextc(b, r1):
        if r1 >= 16:
            return chord_at.get(((b + 1) % 24, 0))
        return chord_at.get((b, r1))

    # ---------------- drums (ch 0 kick/snare/rim, ch 1 shaker/hat)
    kicks = ["x......x..x.....", "x.....x...x....x"]
    snr_a = "....s.......s..."
    snr_b = "....s..g....s..."
    shake = "AcbcAcbcAcbcAcbc"
    for b in range(24):
        sect = b // 4
        d = song.drum_line
        if sect == 0:   # intro: soft kick + rim + shaker
            d(0, b, kicks[b % 2].replace("x", "k"), "kick", {"k": 50})
            d(0, b, "....r.......r...", "rim", {"r": 30}) if b >= 2 else None
            d(1, b, shake, "shaker", {"A": 26, "b": 19, "c": 13})
        elif sect in (1, 2, 5):
            d(0, b, kicks[b % 2], "kick", {"x": 58})
            d(0, b, snr_a if b % 2 == 0 else snr_b, "snare", {"s": 42, "g": 15})
            d(1, b, shake, "shaker", {"A": 34, "b": 26, "c": 18})
            for rr in (2, 6, 10, 14):
                song.put(1, b, rr, 60, "hat", 30, None)
        else:           # B: lighter, hats on 8ths, kick on 1 and 3-and
            d(0, b, "x.....x...x.....", "kick", {"x": 52})
            d(0, b, "............s...", "rim", {"s": 30}) if b % 2 else None
            d(0, b, "....r.......r...", "rim", {"r": 34}) if b % 2 == 0 else None
            d(1, b, "h.h.h.h.h.h.h.h.", "hat", {"h": 26})
        if b % 4 == 3 and sect in (1, 2, 4, 5):  # fill
            fill = "............" + "ssss"
            d(0, b, "................", "snare", {})
            for i, vv in zip(range(12, 16), (24, 30, 36, 44)):
                song.put(0, b, i, 60, "snare", vv, None, False)
            d(1, b, "..............o.", "ohat", {"o": 24})
    # ---------------- bass (ch 2)
    sparse = [(0, "r", 5), (6, "r", 2), (8, "5", 3), (12, "b7", 2), (14, "ap", 2)]
    funk = [(0, "r", 3), (3, "r", 1), (6, "o", 2), (8, "b7", 2), (10, "5", 2), (12, "r", 2), (14, "ap", 2)]
    walk = [(0, "r", 3), (4, "5", 3), (8, "o", 3), (12, "5", 2), (14, "ap", 2)]
    half1 = [(0, "r", 3), (4, "5", 2), (6, "r", 2)]
    half2 = [(0, "r", 3), (4, "5", 2), (6, "ap", 2)]
    for b in range(24):
        sect = b // 4
        segs = prog[b]
        if len(segs) == 2:
            for k, (r0, r1, chd) in enumerate(segs):
                tm = [(r0 + rr, kk, ll) for (rr, kk, ll) in (half1 if k == 0 else half2)]
                bass_line(song, 2, b, tm, chd, nextc(b, r1), 54)
        else:
            tm = sparse if sect == 0 else (walk if sect in (3, 4) else funk)
            bass_line(song, 2, b, tm, segs[0][2], nextc(b, 16), 54)
    # ---------------- e-piano comp (ch 3, 4)
    rh_sparse = [(0, 3, 1.0), (10, 3, 0.85)]
    rh_full = [(0, 3, 1.0), (3, 2, 0.7), (6, 3, 0.9), (10, 2, 0.9), (13, 2, 0.7)]
    rh_push = [(0, 3, 1.0), (3, 2, 0.7), (6, 3, 0.9), (9, 1, 0.6), (10, 2, 0.9), (13, 2, 0.75)]
    rh_pad = [(0, 8, 0.85), (8, 8, 0.8)]
    rh_half1 = [(0, 3, 1.0), (6, 2, 0.8)]
    for b in range(24):
        sect = b // 4
        segs = prog[b]
        rh = {0: rh_sparse, 1: rh_full, 2: rh_push, 3: rh_pad, 4: rh_full, 5: rh_push}[sect]
        if len(segs) == 2:
            for k, (r0, r1, chd) in enumerate(segs):
                comp(song, (3, 4), b, chd, [(rw, ln, a) for (rw, ln, a) in rh_half1], 34, "epiano", row0=r0)
        else:
            comp(song, (3, 4), b, segs[0][2], rh, 34, "epiano")
    # ---------------- clav stabs (ch 7) in sections 2 and 5
    for b in list(range(8, 12)) + list(range(20, 24)):
        segs = prog[b % 24]
        for (r0, r1, chd) in segs:
            hi = chd["dy"][1] + 12
            rows = [2, 7, 11, 14] if r1 - r0 == 16 else [2, 6] if r0 == 0 else [10, 14]
            for rr in rows:
                if r0 <= rr < r1:
                    song.put(7, b, rr, hi, "clav", 30 if rr % 4 == 2 else 22, 1)
    # ---------------- lead (ch 5 hook / melody), vibes (ch 6)
    hookA = [
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 5), (10, "Eb5", 2), (12, "C5", 4)],
        [(0, "Bb4", 2), (2, "D5", 2), (4, "F5", 4), (8, "D5", 2), (10, "C5", 2), (12, "Bb4", 4)],
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 4), (8, "G5", 2), (10, "A5", 2), (12, "G5", 4)],
        [(0, "G5", 3), (4, "D5", 4), (8, "G5", 2), (10, "E5", 2), (12, "C5", 4)],
    ]
    hookB = [
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 5), (10, "Eb5", 2), (12, "F5", 2), (14, "G5", 2)],
        [(0, "D5", 2), (2, "F5", 2), (4, "F5", 4), (8, "Ab5", 2), (10, "F5", 2), (12, "D5", 4)],
        [(0, "E5", 3), (4, "C5", 2), (6, "A4", 2), (8, "F#5", 2), (10, "A5", 2), (12, "F#5", 2), (14, "D5", 2)],
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
    for i in range(4):
        melody(song, 5, 4 + i, hookA[i], "marimba", 50)        # P1
        melody(song, 5, 8 + i, hookB[i], "marimba", 50)        # P2
        melody(song, 5, 12 + i, bm1[i], "whistle", 42)         # P3
        melody(song, 5, 16 + i, bm2[i], "whistle", 42)         # P4
        melody(song, 5, 20 + i, hookA[i], "marimba", 52)       # P5
    # intro: marimba plays only the first hook bar as a teaser in the last bar of P0? -> keep P0 for groove
    # vibes (ch 6): sustained 9th/5th colour under the B section and an octave double of the hook in P5
    pad_notes = {0: "G5", 1: "A5"}
    colour = {id(F9): "C5", id(Bb9): "F5", id(Gm7): "D5", id(C9): "G4", id(Dm7): "A4", id(Gm7lo): "D5", id(C9lo): "G4",
              id(Fm7): "C5", id(Am7): "E5", id(D7): "A4", id(C7s): "G4", id(F9lo): "C5"}  # chord fifths: safe under the lead
    for b in range(12, 20):
        for (r0, r1, chd) in prog[b]:
            song.put(6, b, r0, n(colour[id(chd)]), "vibes", 26, r1 - r0)
    for i in range(4):
        melody(song, 6, 20 + i, hookA[i], "vibes", 26, shift=0)

    # ---------------- checks
    cl = [(b, r0, r1, ch["pcs"]) for b, bar in enumerate(prog) for (r0, r1, ch) in bar]
    sc = {5, 7, 9, 10, 0, 2, 3, 4}
    print("city_day melody check:")
    check_melody(song, 5, cl, sc, "lead")
    return song.build(os.path.join(out, "city_day.xm"))


# ===================================================================================================
def old_block(out):
    insts = [S.inst_guitar(), S.inst_bass(upright=True), S.inst_accordion(), S.inst_mandolin(), S.inst_tuba()]
    kit = S.drum_kit()
    insts += [kit[k] for k in ("kick", "snare", "swish", "shaker", "clave")]
    song = Song("Old Block street", 96, 24, 8, insts, swing=2)
    song.master = 1.3
    song.gain = {"guitar": 1.9, "mandolin": 1.7, "tuba": 1.4, "bass_up": 0.75, "kick": 0.9, "snare": 1.4, "shaker": 1.6, "swish": 1.6}

    D = C("D2", "A3", "F#4", "D F# A")
    G = C("G2", "B3", "G4", "G B D")
    Em7 = C("E2", "G3", "D4", "E G B D")
    A7 = C("A2", "C#4", "G4", "A C# E G")
    Bm = C("B2", "B3", "F#4", "B D F#")
    A = C("A2", "C#4", "E4", "A C# E")
    A7s = C("A2", "D4", "G4", "A D E G")
    # bass roots: oom-pah octave for guitar-friendly register
    for ch in (D, G, Em7, A7, Bm, A, A7s):
        ch["root"] += 12   # an octave up: phone speakers lose < 150 Hz
    prog = []
    P1 = [[(0, 16, D)], [(0, 16, G)], [(0, 16, D)], [(0, 8, Em7), (8, 16, A7)]]
    P2 = [[(0, 16, D)], [(0, 16, G)], [(0, 16, Bm)], [(0, 8, Em7), (8, 16, A7)]]
    P3 = [[(0, 16, Bm)], [(0, 16, Em7)], [(0, 16, A)], [(0, 16, D)]]
    P4 = [[(0, 16, Bm)], [(0, 16, Em7)], [(0, 8, A7s), (8, 16, A7)], [(0, 16, D)]]
    prog = P1 + P1 + P2 + P3 + P4 + P1
    chord_at = {(b, r): ch for b, bar in enumerate(prog) for (r0, r1, ch) in bar for r in range(r0, r1)}

    # drums: brush on 2 and 4 + shaker 8ths; light kick on 1 and 3
    for b in range(24):
        sect = b // 4
        d = song.drum_line
        d(0, b, "k.......k.......", "kick", {"k": 46})
        if sect >= 1:
            d(0, b, "....s.......s...", "snare", {"s": 28})
        d(1, b, "s.s.s.s.s.s.s.s." if sect != 3 else "w.s.w.s.w.s.w.s.", "shaker" if sect != 3 else "swish", {"s": 22, "w": 20})
        if b % 4 == 3 and sect >= 1:
            for i, vv in zip(range(12, 16), (20, 26, 32, 40)):
                song.put(0, b, i, 60, "snare", vv, None, False)
    # bass oom-pah
    for b in range(24):
        sect = b // 4
        for (r0, r1, chd) in prog[b]:
            r = chd["root"]
            fifth = r + 7
            if r1 - r0 == 16:
                song.put(2, b, r0 + 0, r, "bass_up", 54, 3)
                song.put(2, b, r0 + 8, fifth, "bass_up", 50, 3)
                if sect >= 1:
                    song.put(2, b, r0 + 12, r + 12 if r + 12 < 54 else r, "bass_up", 36, 2)
                nxt = chord_at.get(((b + 1) % 24, 0))
                if sect >= 2 and nxt is not None:
                    app = nxt["root"] - 1 if nxt["root"] >= r else nxt["root"] + 1
                    song.put(2, b, 14, app, "bass_up", 40, 2)
            else:
                song.put(2, b, r0, r, "bass_up", 52, 3)
                song.put(2, b, r0 + 4, fifth, "bass_up", 46, 3)
    # guitar strums on 2 and 4 (ch 3 + 4, second string 1 tick later) and a light pick on 1
    for b in range(24):
        sect = b // 4
        for (r0, r1, chd) in prog[b]:
            lo, hi = chd["dy"]
            hits = [4, 12] if r1 - r0 == 16 else [r0 + 4]
            if r1 - r0 == 8 and r0 == 8:
                hits = [12]
            if sect >= 3 or b % 4 in (1, 3):
                hits = hits + ([r0 + 7] if r1 - r0 == 16 else [])
            for rr in hits:
                if rr > 15:
                    continue
                song.put(3, b, rr, lo, "guitar", 34 if rr % 8 == 4 else 22, 3)
                song.put(4, b, rr, hi, "guitar", 32 if rr % 8 == 4 else 20, 3, delay=1)
    # mandolin tremolo-ish repeated notes on the chord 3rd (P1.. soft) - quarter-note pattern in 16ths
    for b in range(4, 24):
        if b // 4 == 3:
            continue
        for (r0, r1, chd) in prog[b]:
            top = chd["dy"][1] + 12 if chd["dy"][1] < 66 else chd["dy"][1]
            for rr in range(r0, r1, 2):
                if rr % 4 in (0, 2):
                    song.put(7, b, rr, top, "mandolin", 17 if rr % 4 == 2 else 22, 1, swing=True)

    # lead
    hookP1 = [
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 5), (10, "C5", 2), (12, "A4", 4)],
        [(0, "G4", 2), (2, "B4", 2), (4, "D5", 4), (8, "B4", 2), (10, "A4", 2), (12, "G4", 4)],
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 4), (8, "E5", 2), (10, "F#5", 2), (12, "E5", 4)],
        [(0, "E5", 3), (4, "B4", 4), (8, "C#5", 2), (10, "E5", 2), (12, "A4", 4)],
    ]
    hookP2 = [
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 5), (10, "C5", 2), (12, "D5", 2), (14, "E5", 2)],
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
        [(0, "F#4", 2), (2, "A4", 2), (4, "D5", 5), (10, "C5", 2), (12, "A4", 4)],
    ]
    for i in range(4):
        melody(song, 5, 4 + i, hookP1[i], "accordion", 46)
        melody(song, 5, 8 + i, hookP2[i], "accordion", 46)
        melody(song, 5, 12 + i, bm1[i], "accordion", 44)
        melody(song, 5, 16 + i, bm2[i], "accordion", 44)
        melody(song, 5, 20 + i, hookP1[i], "accordion", 48)
        # teaser: the motif on the mandolin in the intro (soft)
    # P0: hook on guitar-ish mandolin channel 7 (instead of tremolo comp)
    for i in range(4):
        melody(song, 7, i, hookP1[i], "mandolin", 36)
    # tuba "brass wink" punches (ch 6) at the end of phrases
    for b in (7, 11, 15, 19, 23):
        chd = chord_at[(b, 0)] if len(prog[b]) == 1 else chord_at[(b, 8)]
        r = chd["root"]
        song.put(6, b, 12, r, "tuba", 36, 1)
        song.put(6, b, 14, r + 7, "tuba", 36, 1)
    for b in (3, 9, 22):
        pass
    # tuba doubles the bass root on 1 in P4/P5
    for b in range(16, 24):
        for (r0, r1, chd) in prog[b]:
            if b % 4 != 3:
                song.put(6, b, r0, chd["root"], "tuba", 30, 3)

    cl = [(b, r0, r1, ch["pcs"]) for b, bar in enumerate(prog) for (r0, r1, ch) in bar]
    sc = {2, 4, 6, 7, 9, 11, 0, 1}
    print("old_block melody check:")
    check_melody(song, 5, cl, sc, "lead")
    return song.build(os.path.join(out, "old_block.xm"))


# ===================================================================================================
def market(out):
    insts = [S.inst_epiano(), S.inst_bass(), S.inst_whistle(), S.inst_vibes()]
    kit = S.drum_kit()
    insts += [kit[k] for k in ("kick", "rim", "shaker", "swish")]
    song = Song("Corner Market", 108, 16, 7, insts, swing=2)
    song.master = 1.25
    song.gain = {"epiano": 1.5, "vibes": 1.5, "shaker": 1.7, "kick": 1.3, "rim": 1.3, "swish": 1.6, "whistle": 0.8, "bass": 0.9}

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
    chord_at = {(b, r): ch for b, bar in enumerate(prog) for (r0, r1, ch) in bar for r in range(r0, r1)}
    for b in range(16):
        d = song.drum_line
        d(0, b, "k.....k...k.....", "kick", {"k": 40})
        d(0, b, "....r.......r...", "rim", {"r": 26})
        d(1, b, "s.s.s.s.s.s.s.s.", "shaker", {"s": 20})
        if b % 4 == 3:
            d(1, b, "............w...", "swish", {"w": 16})
    # bass
    for b in range(16):
        for (r0, r1, chd) in prog[b]:
            r = chd["root"]
            nx = chord_at[((b + 1) % 16, 0)]["root"]
            ap = nx - 1 if nx >= r else nx + 1
            if r1 - r0 >= 12:
                tm = [(0, r, 3), (4, r + 7, 2), (6, r, 2), (8, r + 12, 2), (10, r + 7, 2), (12, r, 2)]
                for (rr, m, ln) in tm:
                    song.put(2, b, r0 + rr, m, "bass", 46 if rr % 4 == 0 else 36, ln)
                song.put(2, b, 14, ap, "bass", 34, 2) if r1 == 16 and r1 - r0 == 16 else None
            else:
                song.put(2, b, r0, r, "bass", 46, 3)
                song.put(2, b, r0 + 4, r + 7, "bass", 36, 2)
                if r1 == 16:
                    song.put(2, b, 14, ap, "bass", 34, 2)
    # e-piano comp (ch 3, 4)
    rh = [(0, 3, 1.0), (6, 2, 0.8), (10, 3, 0.9)]
    rh2 = [(0, 4, 1.0), (8, 4, 0.85)]
    for b in range(16):
        for (r0, r1, chd) in prog[b]:
            if r1 - r0 >= 12:
                comp(song, (3, 4), b, chd, rh if b % 4 != 3 else rh2, 30, "epiano", row0=r0)
            else:
                comp(song, (3, 4), b, chd, [(0, 3, 1.0)], 30, "epiano", row0=r0)
    # whistle lead (ch 5)
    mel = [
        [(0, "E4", 2), (2, "G4", 2), (4, "C5", 5), (10, "Bb4", 2), (12, "G4", 4)],
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 4), (8, "E5", 2), (10, "C5", 2), (12, "A4", 4)],
        [(0, "E4", 2), (2, "G4", 2), (4, "C5", 4), (8, "D5", 2), (10, "E5", 2), (12, "G5", 4)],
        [(0, "F5", 2), (2, "E5", 2), (4, "D5", 4), (8, "B4", 2), (10, "D5", 2), (12, "G4", 4)],
        [(0, "G5", 4), (4, "E5", 4), (8, "B4", 4), (12, "D5", 4)],
        [(0, "C5", 4), (4, "E5", 4), (8, "A4", 4), (12, "E5", 4)],
        [(0, "D5", 4), (4, "F5", 4), (8, "A4", 4), (12, "C5", 4)],
        [(0, "D5", 4), (4, "C5", 4), (8, "B4", 4), (12, "D5", 4)],
        [(0, "E4", 2), (2, "G4", 2), (4, "C5", 5), (10, "Bb4", 2), (12, "G4", 2), (14, "A4", 2)],
        [(0, "A4", 2), (2, "C5", 2), (4, "F5", 4), (8, "D5", 2), (10, "C5", 2), (12, "A4", 4)],
        [(0, "G4", 2), (2, "B4", 2), (4, "E5", 4), (8, "C#5", 2), (10, "E5", 2), (12, "A4", 4)],
        [(0, "F5", 2), (2, "D5", 2), (4, "A4", 4), (8, "B4", 2), (10, "D5", 2), (12, "F5", 4)],
        [(0, "E5", 4), (4, "C5", 4), (8, "A4", 4), (12, "C5", 4)],
        [(0, "F#5", 4), (4, "E5", 4), (8, "C5", 4), (12, "A4", 4)],
        [(0, "F5", 4), (4, "D5", 4), (8, "D5", 2), (10, "B4", 2), (12, "G4", 4)],
        [(0, "C5", 2), (2, "E5", 2), (4, "G5", 4), (8, "E5", 4), (12, "D5", 2), (14, "B4", 2)],
    ]
    for b in range(16):
        melody(song, 5, b, mel[b], "whistle", 40)
    # vibes: sparse high chord colour on bar starts in the second half
    colour = {id(Em7): "B4", id(Am7): "E5", id(Dm7): "A4", id(C6): "G4", id(F6): "C5", id(D9): "A4", id(A7): "E5"}
    for b in range(8, 16):
        for (r0, r1, chd) in prog[b]:
            if id(chd) in colour and r1 - r0 >= 8:
                song.put(6, b, r0 + 8 if r1 - r0 >= 12 else r0, n(colour[id(chd)]), "vibes", 22, 6)
    cl = [(b, r0, r1, ch["pcs"]) for b, bar in enumerate(prog) for (r0, r1, ch) in bar]
    sc = {0, 2, 4, 5, 7, 9, 11, 10}
    print("market melody check:")
    check_melody(song, 5, cl, sc, "lead")
    return song.build(os.path.join(out, "market.xm"))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for fn in (city_day, old_block, market):
        print(fn.__name__, fn(out), "bytes")
