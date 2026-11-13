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
    fx.update(make_activity())
    fx.update(make_scene_sfx())
    fx.update(make_voices())
    # round 4: the mission jingle must be clearly audible: fuller, longer, soft-saturated for a higher average level
    fx["mission_complete"] = finish(sat(make_mission_jingle()), 0.95)
    return fx


# ---------------------------------------------------------------------------------------------- activity sounds (s78 round 3)
# Soft, short, mixed under the music. Looping ones are cross-faded so the repeat has no click.
def lp(x, a):
    return S.lowpass(x, a)


def hp(x, a):
    return S.highpass(x, a)


def make_loop(x, fade_s=0.08):
    f = int(R * fade_s)
    t = np.linspace(0, 1, f)
    y = x[:len(x) - f].copy()
    y[:f] = x[:f] * np.sqrt(t) + x[len(x) - f:] * np.sqrt(1 - t)
    return y


def slow_noise(n, hz):
    """smooth random envelope 0..1"""
    k = max(2, int(R / hz))
    pts = S.RNG.uniform(0, 1, n // k + 3)
    return np.interp(np.arange(n), np.arange(len(pts)) * k, pts)


def burst(d, a_low, a_high, decay, attack=0.004):
    t = t_(d)
    x = hp(lp(S.noise(len(t)), a_low), a_high)
    return x * np.exp(-t / decay) * np.minimum(t / attack, 1)


def make_activity():
    fx = {}
    # washing: soft splashing, bubbling water
    n = int(R * 1.0)
    x = hp(lp(S.noise(n), 0.30), 0.03) * (0.35 + 0.65 * slow_noise(n, 14) ** 1.5)
    fx["water"] = finish(make_loop(x), 0.8)
    # shower: broad soft hiss, gentle movement
    n = int(R * 1.4)
    x = hp(lp(S.noise(n), 0.55), 0.10) * (0.7 + 0.3 * slow_noise(n, 6))
    fx["shower"] = finish(make_loop(x, 0.12), 0.8)
    # eating: three soft crunches
    parts = [(0.00, burst(0.09, 0.45, 0.05, 0.022), 1.0), (0.25, burst(0.09, 0.40, 0.05, 0.020), 0.8), (0.50, burst(0.09, 0.45, 0.05, 0.022), 0.9)]
    for at in (0.0, 0.25, 0.5):
        t = t_(0.06)
        parts.append((at, np.sin(2 * math.pi * 140 * t) * np.exp(-t / 0.02), 0.5))
    fx["munch"] = finish(place(parts, 0.75), 0.8)
    # drinking: two gulps (falling pitch blips with a little water)
    def gulp(d=0.16):
        t = t_(d)
        f = 260 - 120 * (t / d)
        ph = 2 * math.pi * np.cumsum(f) / R
        return np.sin(ph) * np.sin(math.pi * t / d) ** 2 + 0.25 * lp(S.noise(len(t)), 0.25) * np.sin(math.pi * t / d)
    fx["gulp"] = finish(place([(0.0, gulp(), 1.0), (0.32, gulp(0.18), 0.85)], 0.65), 0.8)
    # toilet flush: swell of water, then a gurgling decay
    n = int(R * 2.2)
    t = t_(2.2)
    env = np.minimum(t / 0.35, 1) * np.exp(-np.maximum(t - 0.5, 0) / 0.9)
    x = hp(lp(S.noise(n), 0.5), 0.04) * env * (0.7 + 0.3 * slow_noise(n, 9))
    x += 0.4 * np.sin(2 * math.pi * (120 + 60 * np.sin(2 * math.pi * 2.3 * t)) * t) * np.exp(-np.maximum(t - 1.0, 0) / 0.5) * (t > 1.0)
    fx["flush"] = finish(x, 0.85)
    # reading: a soft page turn
    t = t_(0.18)
    sw = hp(lp(S.noise(len(t)), 0.6), 0.12) * np.sin(math.pi * t / 0.18) ** 2
    flap = burst(0.03, 0.5, 0.2, 0.01)
    fx["page"] = finish(place([(0.05, sw, 1.0), (0.22, flap, 0.5)], 1.5), 0.6)
    # bin search: rustling, crackling paper
    n = int(R * 0.9)
    crack = np.zeros(n)
    for _ in range(26):
        at = int(S.RNG.uniform(0, n - 500))
        b = burst(0.03, 0.55, 0.15, 0.008)
        crack[at:at + len(b)] += b * S.RNG.uniform(0.3, 1.0)
    x = crack + 0.35 * hp(lp(S.noise(n), 0.5), 0.1) * slow_noise(n, 12)
    fx["rustle"] = finish(make_loop(x, 0.06), 0.75)
    # can / bottle pickup: a little clink
    t = t_(0.4)
    x = (np.sin(2 * math.pi * 2350 * t) * np.exp(-t / 0.09) + 0.6 * np.sin(2 * math.pi * 3620 * t) * np.exp(-t / 0.05)
         + 0.35 * np.sin(2 * math.pi * 5100 * t) * np.exp(-t / 0.03))
    fx["clink"] = finish(x, 0.8)
    # deposit machine: motor whirr, rattle, clunk
    t = t_(1.3)
    f = 70 + 55 * np.minimum(t / 0.9, 1)
    ph = 2 * math.pi * np.cumsum(f) / R
    saw = (2 * ((ph / (2 * math.pi)) % 1) - 1)
    x = lp(saw, 0.25) * np.minimum(t / 0.1, 1) * (1 - 0.6 * (t > 1.0)) + 0.2 * hp(lp(S.noise(len(t)), 0.4), 0.1) * np.sin(2 * math.pi * 17 * t) ** 2
    x[int(R * 1.05):] *= np.exp(-(np.arange(len(x) - int(R * 1.05))) / (R * 0.05))
    clunk = np.sin(2 * math.pi * 95 * t_(0.12)) * np.exp(-t_(0.12) / 0.03)
    fx["whirr"] = finish(place([(0, x, 1.0), (1.1, clunk, 1.4)], 1.3), 0.8)
    # sleeping: slow, soft breathing (subtle)
    t = t_(3.2)
    cyc = (np.sin(math.pi * np.clip(t / 1.4, 0, 1)) ** 2) * (t < 1.4) + 0.8 * (np.sin(math.pi * np.clip((t - 1.6) / 1.4, 0, 1)) ** 2) * (t >= 1.6)
    n = len(t)
    x = lp(S.noise(n), 0.09) * cyc + 0.5 * np.sin(2 * math.pi * 62 * t) * cyc * (1 + 0.5 * np.sin(2 * math.pi * 24 * t))
    fx["snore"] = finish(make_loop(x, 0.15), 0.6)
    # sitting down: a soft thud
    t = t_(0.16)
    fx["thud"] = finish(np.sin(2 * math.pi * (95 - 30 * t / 0.16) * t) * np.exp(-t / 0.04) + 0.3 * lp(S.noise(len(t)), 0.2) * np.exp(-t / 0.02), 0.8)
    # door: latch click + soft swish
    t = t_(0.55)
    sw = hp(lp(S.noise(len(t)), 0.3), 0.04) * np.sin(math.pi * np.clip((t - 0.05) / 0.45, 0, 1)) ** 2 * 0.5
    fx["door"] = finish(place([(0, burst(0.03, 0.5, 0.12, 0.006), 1.0), (0.0, sw, 1.0), (0.46, burst(0.03, 0.4, 0.1, 0.008), 0.8)], 0.55), 0.7)
    # phone: two soft beeps
    fx["beep"] = finish(place([(0, tone(1320, 0.07, "sin", 0.05, 0.004), 1.0), (0.09, tone(1760, 0.09, "sin", 0.06, 0.004), 1.0)], 0.2), 0.8)
    # scratch card
    n = int(R * 0.6)
    t = t_(0.6)
    x = hp(lp(S.noise(n), 0.65), 0.2) * (np.sin(2 * math.pi * 38 * t) ** 2) * np.minimum(t / 0.03, 1) * np.exp(-t / 0.6)
    fx["scratch"] = finish(x, 0.7)
    # metal ladder: three dull clangs
    def clang(f, d=0.35):
        t = t_(d)
        return (np.sin(2 * math.pi * f * t) * np.exp(-t / 0.12) + 0.5 * np.sin(2 * math.pi * f * 2.32 * t) * np.exp(-t / 0.07)
                + 0.25 * np.sin(2 * math.pi * f * 4.1 * t) * np.exp(-t / 0.04))
    fx["ladder"] = finish(place([(0.0, clang(610), 1.0), (0.26, clang(760), 0.85), (0.55, clang(540), 0.9)], 0.95), 0.8)
    # manhole cover scraping
    t = t_(0.8)
    f = 110 + 60 * np.sin(math.pi * np.clip(t / 0.7, 0, 1))
    ph = 2 * math.pi * np.cumsum(f) / R
    x = (lp(S.noise(len(t)), 0.25) * 0.8 + 0.3 * np.sin(ph)) * np.sin(math.pi * np.clip(t / 0.7, 0, 1)) ** 1.2
    clunk = np.sin(2 * math.pi * 80 * t_(0.14)) * np.exp(-t_(0.14) / 0.04)
    fx["manhole"] = finish(place([(0, x, 1.0), (0.66, clunk, 1.2)], 0.8), 0.8)
    # minigame sounds: good item, mistake, plate clink
    fx["mg_good"] = finish(place([(0, tone(880, 0.08, "sin", 0.05, 0.003), 1.0), (0.06, tone(1319, 0.12, "sin", 0.07, 0.003), 1.0)], 0.2), 0.7)
    t = t_(0.22)
    saw = 2 * ((140 * t) % 1) - 1
    fx["mg_bad"] = finish(lp(saw, 0.16) * np.exp(-t / 0.12) * np.minimum(t / 0.006, 1), 0.7)
    t = t_(0.3)
    fx["mg_clink"] = finish(np.sin(2 * math.pi * 3100 * t) * np.exp(-t / 0.07) + 0.5 * np.sin(2 * math.pi * 4700 * t) * np.exp(-t / 0.04), 0.7)
    return fx


# ---------------------------------------------------------------------------------------------- round 4: scene sounds, voices, jingles
def sat(x, k=2.2):
    return np.tanh(k * x / max(np.max(np.abs(x)), 1e-9)) / math.tanh(k)


def make_mission_jingle():
    def gl(m, d):
        f = S.mtof(m)
        t = t_(d)
        return (np.sin(2 * math.pi * f * t) * np.exp(-t / 0.7) + 0.35 * np.sin(2 * math.pi * f * 2.76 * t) * np.exp(-t / 0.25)
                + 0.15 * np.sin(2 * math.pi * f * 5.4 * t) * np.exp(-t / 0.1)) * np.minimum(t / 0.002, 1)

    def pad(m, d):
        f = S.mtof(m)
        t = t_(d)
        env = np.minimum(t / 0.06, 1) * np.exp(-t / 1.6)
        return (np.sin(2 * math.pi * f * t) + 0.4 * np.sin(2 * math.pi * 2 * f * t) + 0.2 * np.sin(2 * math.pi * 3 * f * t)) * env

    parts = []
    for i, m in enumerate((72, 76, 79, 84)):                # C5 E5 G5 C6 arpeggio (the motif's 3-5-8 shape)
        parts.append((0.14 * i, gl(m, 1.0), 0.9))
    for i, m in enumerate((88, 91, 96)):                    # a sparkle on top
        parts.append((0.62 + 0.09 * i, gl(m, 1.0), 0.55))
    for m, g in ((48, 0.7), (60, 0.6), (64, 0.55), (67, 0.55), (72, 0.5)):
        parts.append((0.6, pad(m, 2.6), g))
    parts.append((0.6, gl(84, 2.0), 0.8))
    return place(parts, 3.2)


def make_scene_sfx():
    fx = {}
    # soft click for every dialogue page
    t = t_(0.06)
    click = np.sin(2 * math.pi * 1700 * t) * np.exp(-t / 0.012) + 0.4 * hp(S.noise(len(t)), 0.3) * np.exp(-t / 0.004)
    fx["click"] = finish(place([(0.0, click, 1.0)], 0.2), 0.8)      # padded: very short samples are not reliably played by maxmod

    # "received": a bright three-note pluck run (distinct from the coin)
    def pluck(m, d=0.7):
        f = S.mtof(m)
        t = t_(d)
        return (np.sin(2 * math.pi * f * t) * np.exp(-t / 0.18) + 0.4 * np.sin(2 * math.pi * 2 * f * t) * np.exp(-t / 0.1)
                + 0.2 * np.sin(2 * math.pi * 3 * f * t) * np.exp(-t / 0.05)) * np.minimum(t / 0.002, 1)
    fx["received"] = finish(sat(place([(0.0, pluck(79), 0.8), (0.1, pluck(83), 0.85), (0.2, pluck(86), 0.9), (0.32, pluck(91, 0.9), 1.0)], 1.2)), 0.9)

    def engine(f_curve, amp_curve, d, noise_amp=0.3):
        t = t_(d)
        f = f_curve(t)
        ph = 2 * math.pi * np.cumsum(f) / R
        saw = np.zeros(len(t))
        for h in range(1, 9):
            saw += np.sin(h * ph) / h ** 0.9
        saw = lp(saw, 0.18) * (1 + 0.25 * np.sin(2 * math.pi * 13 * t))
        road = lp(S.noise(len(t)), 0.12)
        return (saw + noise_amp * road) * amp_curve(t)
    # golden car approaches (a smooth luxury purr, rising then easing off)
    d = 2.6
    fx["car_arrive"] = finish(engine(lambda t: 52 + 38 * np.sin(math.pi * np.clip(t / d, 0, 1) * 0.9),
                                     lambda t: np.minimum(t / 1.7, 1) ** 1.5 * (1 - 0.35 * np.clip((t - 1.8) / 0.8, 0, 1)), d), 0.8)
    # brake: soft squeal + hiss + engine settling
    t = t_(0.9)
    squeal = np.sin(2 * math.pi * np.cumsum(2300 - 700 * t / 0.9) / R) * np.sin(math.pi * np.clip(t / 0.6, 0, 1)) ** 2 * 0.35
    hiss = hp(lp(S.noise(len(t)), 0.5), 0.08) * np.exp(-t / 0.35) * 0.6
    fx["car_brake"] = finish(squeal + hiss + 0.5 * engine(lambda t: 46 + 0 * t, lambda t: np.exp(-t / 0.6), 0.9, 0.1), 0.75)

    # door open + close
    def thunk(d=0.2):
        t = t_(d)
        return np.sin(2 * math.pi * (115 - 40 * t / d) * t) * np.exp(-t / 0.05) + 0.4 * lp(S.noise(len(t)), 0.15) * np.exp(-t / 0.03)
    fx["car_door"] = finish(place([(0.0, burst(0.025, 0.5, 0.15, 0.1, 0.002), 0.7), (0.02, thunk(), 0.9), (0.7, thunk(), 1.0),
                                   (0.69, burst(0.02, 0.5, 0.2, 0.01), 0.6)], 1.0), 0.8)
    d = 2.8
    fx["car_leave"] = finish(engine(lambda t: 44 + 70 * np.clip(t / 1.2, 0, 1) ** 0.8 - 20 * np.clip((t - 1.8) / 1.0, 0, 1),
                                    lambda t: np.minimum(t / 0.5, 1) * np.exp(-np.maximum(t - 1.0, 0) / 0.9), d, 0.35), 0.8)
    # VaultMart swap: a cold electric whoosh
    t = t_(0.5)
    sweep = np.sin(2 * math.pi * np.cumsum(2400 * np.exp(-t / 0.18) + 300) / R) * np.exp(-t / 0.2)
    fx["flash"] = finish(0.7 * sweep + hp(lp(S.noise(len(t)), 0.7), 0.1) * np.exp(-t / 0.15) * 0.6, 0.8)
    # newspaper: big paper rustle
    n = int(R * 1.1)
    crack = np.zeros(n)
    for _ in range(14):
        at = int(S.RNG.uniform(0, n - 1500))
        b = burst(0.08, 0.5, 0.1, 0.03, 0.01)
        crack[at:at + len(b)] += b * S.RNG.uniform(0.4, 1.0)
    fx["newspaper"] = finish(crack + 0.4 * hp(lp(S.noise(n), 0.4), 0.06) * slow_noise(n, 8), 0.75)

    # phone ring: two rings
    def ring():
        t = t_(0.42)
        return ((np.sin(2 * math.pi * 1040 * t) + np.sin(2 * math.pi * 1340 * t)) * (0.5 + 0.5 * np.sin(2 * math.pi * 24 * t))
                * np.minimum(t / 0.01, 1) * np.minimum((0.42 - t) / 0.01, 1))
    fx["phone_ring"] = finish(place([(0.0, ring(), 1.0), (0.6, ring(), 1.0)], 1.1), 0.7)
    return fx


# character voices: short vowel blips (gibberish "syllables"), played every few letters at a per-character speed (pitch)
def vowel_blip(f0, d, formants, glide=0.0, saw=False, tilt=1.0):
    t = t_(d)
    f = f0 * (1 + glide * t / d)
    ph = 2 * math.pi * np.cumsum(f) / R
    x = np.zeros(len(t))
    for h in range(1, 24):
        if f0 * h > 6500:
            break
        w = 0.0
        for (fc, a, bw) in formants:
            w += a * math.exp(-(((h * f0) - fc) / bw) ** 2)
        x += (w / h ** (0.6 if saw else tilt)) * np.sin(h * ph)
    env = np.minimum(t / 0.006, 1) * np.sin(math.pi * np.clip(t / d, 0, 1)) ** 0.6
    return x * env


def robot_blip(freqs, d=0.03):
    parts = []
    for i, f in enumerate(freqs):
        t = t_(d)
        sqr = np.where(np.sin(2 * math.pi * f * t) > 0, 1.0, -1.0)
        parts.append((i * d * 1.2, lp(sqr, 0.3) * np.minimum(t / 0.003, 1) * np.minimum((d - t) / 0.004, 1), 1.0))
    return place(parts, len(freqs) * d * 1.2 + 0.01)


TIMBRES = {
    "soft": dict(f0=330, fm=[(520, 1.0, 250), (1100, 0.4, 300)], fmb=[(400, 1.0, 220), (900, 0.4, 260)], d=0.07, saw=False),
    "warm": dict(f0=170, fm=[(700, 1.0, 300), (1200, 0.5, 300)], fmb=[(500, 1.0, 250), (900, 0.5, 200)], d=0.09, saw=False),
    "bright": dict(f0=400, fm=[(700, 1.0, 250), (2100, 0.7, 350)], fmb=[(450, 1.0, 250), (2300, 0.7, 300)], d=0.06, saw=False),
    "pomp": dict(f0=140, fm=[(600, 1.0, 500), (1500, 0.8, 600)], fmb=[(450, 1.0, 400), (1300, 0.9, 500)], d=0.10, saw=True),
}


def make_voices():
    fx = {}
    for name, p in TIMBRES.items():
        fx[f"voice_{name}_a"] = finish(vowel_blip(p["f0"], p["d"], p["fm"], -0.05 if name == "pomp" else 0.04, p["saw"]), 0.7)
        fx[f"voice_{name}_b"] = finish(vowel_blip(p["f0"] * (1.15 if name == "pomp" else 0.84), p["d"] * 1.1, p["fmb"], 0.0, p["saw"]), 0.7)
        # reactions: positive = a happy rising hum, negative = a falling groan
        pos = vowel_blip(p["f0"] * 0.95, 0.24, p["fm"], 0.55, p["saw"])
        neg = vowel_blip(p["f0"] * 1.1, 0.32, p["fmb"], -0.42, p["saw"])
        if name == "pomp":
            pos = place([(0.0, vowel_blip(p["f0"] * 1.1, 0.09, p["fm"], 0.0, True), 1.0),
                         (0.13, vowel_blip(p["f0"] * 1.3, 0.1, p["fm"], 0.0, True), 1.0)], 0.28)
        fx[f"pos_{name}"] = finish(pos, 0.75)
        fx[f"neg_{name}"] = finish(neg, 0.75)
    fx["voice_robot_a"] = finish(robot_blip([440, 587]), 0.6)
    fx["voice_robot_b"] = finish(robot_blip([523, 392]), 0.6)
    fx["pos_robot"] = finish(robot_blip([523, 659, 784], 0.045), 0.6)
    fx["neg_robot"] = finish(robot_blip([196, 147], 0.09), 0.6)
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
    order = list(fx.keys())
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
