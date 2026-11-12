"""Fully synthesised 8-bit instrument samples for the Town Life music tools (numpy only, nothing sampled).

Pitch handling: every melodic Sample is generated at an arbitrary content rate R and is "rooted" at a MIDI note.
`root_sample()` computes the XM relative-note + finetune so that playing the root note reproduces the intended pitch.
XM note n sounds at 8363 * 2**((n + rel + ft/128 - 49)/12) Hz; MIDI note m = XM note n + 11.
"""
import math
import numpy as np
from xm import Sample, Instrument

BASE = 8363.0
RNG = np.random.default_rng(1234)  # deterministic noise


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def shift_for(rate, root_midi):
    """semitones to add (rel + ft/128) so playing the root note plays the data at `rate` Hz."""
    n0 = root_midi - 11
    base = BASE * 2 ** ((n0 - 49) / 12)
    return 12 * math.log2(rate / base)


def root_sample(data, rate, root_midi, loop=None, vol=64, name=""):
    s = shift_for(rate, root_midi)
    rel = math.floor(s)
    ft = int(round((s - rel) * 128))
    if ft > 127:
        rel, ft = rel + 1, ft - 128
    return Sample(data, rel, ft, loop, vol, name)


def norm(x, peak=0.95):
    x = np.asarray(x, float)
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def fade_out(x, n):
    x = x.copy()
    n = min(n, len(x))
    x[-n:] *= np.linspace(1, 0, n)
    return x


def ramp_in(x, n):
    x = x.copy()
    n = min(n, len(x))
    x[:n] *= np.linspace(0, 1, n)
    return x


# ---------------------------------------------------------------- filters (simple, numpy)
def lowpass(x, a):
    """one-pole low-pass; a = 0..1 (higher = brighter)"""
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def highpass(x, a):
    return x - lowpass(x, a)


def noise(n):
    return RNG.uniform(-1, 1, n)


# ---------------------------------------------------------------- looped additive voices
def additive_loop(root_midi, P, partials, attack_periods=2, reps=1, detune_k=None, vol=64, name=""):
    """Stationary harmonic voice, P samples per period, loop = reps periods (or detune_k periods when a
    second slightly sharp reed (ratio (k+1)/k) is mixed in, giving a musette beat).
    partials: [(harmonic, amp)]. First `attack_periods` periods fade in (before the loop start)."""
    R = mtof(root_midi) * P
    loop_len = P * (detune_k if detune_k else reps)
    A = P * attack_periods
    i = np.arange(A + loop_len)
    x = np.zeros(len(i))
    for h, a in partials:
        x += a * np.sin(2 * math.pi * h * i / P)
        if detune_k:
            x += a * 0.9 * np.sin(2 * math.pi * h * i * (detune_k + 1) / (detune_k * P) + 0.7)
    x[:A] *= np.linspace(0, 1, A) ** 1.5
    x = norm(x)
    return root_sample(x, R, root_midi, loop=(A, loop_len), vol=vol, name=name)


def plucked_loop(root_midi, P, partials, T_loop=0.35, vol=64, name=""):
    """Additive pluck: each partial = (harmonic, amp, sustain_fraction, tau). Loop = steady state (1 period)."""
    R = mtof(root_midi) * P
    Ltr = int(math.ceil(T_loop * R / P)) * P
    n = Ltr + P
    i = np.arange(n)
    t = i / R
    x = np.zeros(n)
    for h, a, sus, tau in partials:
        env = sus + (1 - sus) * np.exp(-t / tau)
        env[Ltr:] = sus
        x += a * env * np.sin(2 * math.pi * h * i / P)
    x = ramp_in(x, 24)
    x = norm(x)
    return root_sample(x, R, root_midi, loop=(Ltr, P), vol=vol, name=name)


# ---------------------------------------------------------------- one-shot melodic voices
def epiano_sample(root_midi, R=12000, dur=0.8, bright=2.5):
    f = mtof(root_midi)
    n = int(R * dur)
    t = np.arange(n) / R
    idx = 1.4 * bright * np.exp(-t / 0.22) + 0.22
    mod = np.sin(2 * math.pi * f * t)
    x = np.sin(2 * math.pi * f * t + idx * mod)
    # tine / bell partial on the attack
    x += 0.30 * bright * np.exp(-t / 0.045) * np.sin(2 * math.pi * f * 7.0 * t + 0.4)
    x += 0.12 * np.exp(-t / 0.5) * np.sin(2 * math.pi * f * 2.0 * t)
    x *= np.exp(-t / 0.55)
    x = ramp_in(x, int(R * 0.004))
    x = fade_out(x, int(n * 0.35))
    return root_sample(norm(x), R, root_midi, name="epiano")


def marimba_sample(root_midi, R=12000, dur=0.55):
    f = mtof(root_midi)
    n = int(R * dur)
    t = np.arange(n) / R
    x = (np.sin(2 * math.pi * f * t) * np.exp(-t / 0.28)
         + 0.9 * np.sin(2 * math.pi * f * 3.97 * t) * np.exp(-t / 0.07)
         + 0.35 * np.sin(2 * math.pi * f * 9.9 * t) * np.exp(-t / 0.03))
    x = ramp_in(x, int(R * 0.002))
    x = fade_out(x, int(n * 0.3))
    return root_sample(norm(x), R, root_midi, name="marimba")


def vibes_sample(root_midi, R=12000, dur=1.1):
    f = mtof(root_midi)
    n = int(R * dur)
    t = np.arange(n) / R
    x = (np.sin(2 * math.pi * f * t) * np.exp(-t / 0.9)
         + 0.22 * np.sin(2 * math.pi * f * 4.0 * t) * np.exp(-t / 0.25)
         + 0.07 * np.sin(2 * math.pi * f * 10.0 * t) * np.exp(-t / 0.06))
    x *= 1 + 0.12 * np.sin(2 * math.pi * 5.2 * t) * np.minimum(t * 4, 1)  # motor tremolo
    x = ramp_in(x, int(R * 0.002))
    x = fade_out(x, int(n * 0.3))
    return root_sample(norm(x), R, root_midi, name="vibes")


def glock_sample(root_midi, R=14000, dur=0.7):
    f = mtof(root_midi)
    n = int(R * dur)
    t = np.arange(n) / R
    x = (np.sin(2 * math.pi * f * t) * np.exp(-t / 0.4)
         + 0.35 * np.sin(2 * math.pi * f * 2.76 * t) * np.exp(-t / 0.18)
         + 0.2 * np.sin(2 * math.pi * f * 5.4 * t) * np.exp(-t / 0.07))
    x = ramp_in(x, int(R * 0.001))
    x = fade_out(x, int(n * 0.3))
    return root_sample(norm(x), R, root_midi, name="glock")


def ks_sample(root_midi, P=64, dur=0.9, damp=0.5, decay=0.9965, bright=0.75, seed=7):
    """Karplus-Strong pluck (guitar / mandolin). Delay line P samples; effective period P+0.5."""
    rng = np.random.default_rng(seed)
    f = mtof(root_midi)
    R = f * (P + 0.5)
    n = int(R * dur)
    buf = rng.uniform(-1, 1, P)
    # soften the initial burst
    for _ in range(int(2 + (1 - bright) * 6)):
        buf = 0.5 * (buf + np.roll(buf, 1))
    out = np.empty(n)
    idx = 0
    prev = 0.0
    for k in range(n):
        v = buf[idx]
        nxt = decay * ((1 - damp) * v + damp * 0.5 * (v + prev))
        prev = v
        buf[idx] = nxt
        out[k] = v
        idx = (idx + 1) % P
    out = fade_out(out, int(n * 0.25))
    return root_sample(norm(out), R, root_midi, name="pluck")


def clav_sample(root_midi, P=40, dur=0.28):
    f = mtof(root_midi)
    R = f * P
    n = int(R * dur)
    t = np.arange(n) / R
    x = np.zeros(n)
    for h in range(1, min(14, P // 2)):
        x += (1.0 / h ** 0.8) * np.exp(-t / (0.16 / h ** 0.55)) * np.sin(2 * math.pi * h * f * t * (1 + 0.0004 * h))
    x = ramp_in(x, 20)
    x = fade_out(x, int(n * 0.25))
    return root_sample(norm(x), R, root_midi, name="clav")


# ---------------------------------------------------------------- drums (one-shot, recorded at 16 kHz and played at C-4)
DR = 16000


def drum(data, name):
    x = norm(data, 0.97)
    s = shift_for(DR, 60)
    rel = math.floor(s)
    ft = int(round((s - rel) * 128))
    return Instrument(name, [Sample(x, rel, ft, None, 64, name)])


def kick():
    n = int(DR * 0.26)
    t = np.arange(n) / DR
    f = 48 + 105 * np.exp(-t / 0.022)
    ph = 2 * math.pi * np.cumsum(f) / DR
    x = np.sin(ph) * np.exp(-t / 0.11)
    x += 0.25 * lowpass(noise(n), 0.35) * np.exp(-t / 0.006)
    x = fade_out(ramp_in(x, 10), 400)
    return drum(x, "kick")


def snare_brush():
    n = int(DR * 0.24)
    t = np.arange(n) / DR
    nz = highpass(lowpass(noise(n), 0.5), 0.05)
    env = np.minimum(t / 0.012, 1) * np.exp(-t / 0.065)
    body = np.sin(2 * math.pi * 185 * t) * np.exp(-t / 0.035) * 0.35
    return drum(fade_out(nz * env + body, 500), "snare")


def rim():
    n = int(DR * 0.07)
    t = np.arange(n) / DR
    x = (np.sin(2 * math.pi * 1750 * t) + 0.6 * np.sin(2 * math.pi * 930 * t)) * np.exp(-t / 0.008)
    x += 0.25 * highpass(noise(n), 0.2) * np.exp(-t / 0.004)
    return drum(fade_out(x, 200), "rim")


def hat_closed():
    n = int(DR * 0.07)
    t = np.arange(n) / DR
    x = highpass(highpass(noise(n), 0.6), 0.6) * np.exp(-t / 0.016)
    return drum(fade_out(x, 150), "hat")


def hat_open():
    n = int(DR * 0.3)
    t = np.arange(n) / DR
    x = highpass(noise(n), 0.55) * np.exp(-t / 0.085)
    return drum(fade_out(x, 800), "ohat")


def shaker():
    n = int(DR * 0.11)
    t = np.arange(n) / DR
    x = highpass(noise(n), 0.45) * np.minimum(t / 0.008, 1) * np.exp(-t / 0.03)
    return drum(fade_out(x, 200), "shaker")


def brush_swish():
    n = int(DR * 0.34)
    t = np.arange(n) / DR
    x = highpass(lowpass(noise(n), 0.45), 0.08) * np.sin(math.pi * t / (n / DR)) ** 2
    return drum(x, "swish")


def clave():
    n = int(DR * 0.06)
    t = np.arange(n) / DR
    x = np.sin(2 * math.pi * 2300 * t) * np.exp(-t / 0.011)
    return drum(fade_out(x, 150), "clave")


def woodblock():
    n = int(DR * 0.09)
    t = np.arange(n) / DR
    x = np.sin(2 * math.pi * 1050 * t) * np.exp(-t / 0.018) + 0.4 * np.sin(2 * math.pi * 1620 * t) * np.exp(-t / 0.01)
    return drum(fade_out(x, 200), "wood")


# ---------------------------------------------------------------- instruments (melodic) ready for songs
def split(midi):
    return [0 if n + 12 < midi else 1 for n in range(96)]


ENV_SHORT = [(0, 64), (3, 0)]       # key-off releases in 3 ticks
ENV_MED = [(0, 64), (5, 0)]


def inst_epiano():
    lo = epiano_sample(53)           # F3
    hi = epiano_sample(65)           # F4
    km = split(59)
    return Instrument("epiano", [lo, hi], km, env=ENV_SHORT)


def inst_marimba():
    lo = marimba_sample(69)          # A4
    hi = marimba_sample(81)          # A5
    km = split(76)
    return Instrument("marimba", [lo, hi], km, env=ENV_SHORT)


def inst_vibes():
    lo = vibes_sample(65)
    hi = vibes_sample(77)
    km = split(72)
    return Instrument("vibes", [lo, hi], km, env=ENV_MED)


def inst_glock():
    return Instrument("glock", [glock_sample(84)], env=ENV_SHORT)


def zoned_additive(name, zones, parts, attack_periods, detune_k=None, reps=1, env=None, vib=None):
    """Band-limited looped voice: one sample per key zone (lo_midi, hi_midi, root_midi). The period length P is chosen
    so that the highest note of the zone plays at <= 1 sample step per mixer sample (no decimation aliasing) and only
    harmonics below the mixer Nyquist are kept."""
    samples, km = [], [0] * 96
    for zi, (lo, hi, root) in enumerate(zones):
        P = max(10, int(15768 / mtof(hi)))
        kept = [(h, a) for h, a in parts if h < P / 2 and h * mtof(hi) < 7200]
        samples.append(additive_loop(root, P, kept, attack_periods=attack_periods, reps=reps,
                                     detune_k=detune_k, name=name))
    for idx in range(96):
        m = idx + 12
        km[idx] = max(i for i, z in enumerate(zones) if z[0] <= m)
    return Instrument(name, samples, km, env=env or ENV_SHORT, vib=vib)


def inst_whistle():
    return zoned_additive("whistle", [(0, 74, 70), (75, 108, 80)],
                          [(1, 1.0), (2, 0.3), (3, 0.15), (4, 0.07)], attack_periods=14, reps=6, vib=(28, 2, 22))


def inst_accordion():
    parts = [(1, 1.0), (2, 0.8), (3, 0.55), (4, 0.42), (5, 0.28), (6, 0.2), (7, 0.1), (8, 0.08)]
    return zoned_additive("accordion", [(0, 69, 66), (70, 76, 73), (77, 108, 80)], parts, attack_periods=12, detune_k=60)


def inst_bass(upright=False):
    P = 112
    if upright:
        parts = [(1, 1.0, 0.75, 0.30), (2, 0.55, 0.25, 0.09), (3, 0.30, 0.08, 0.06), (4, 0.15, 0.03, 0.04)]
    else:
        parts = [(1, 1.0, 0.85, 0.30), (2, 0.7, 0.35, 0.10), (3, 0.45, 0.15, 0.08), (4, 0.28, 0.06, 0.06),
                 (5, 0.16, 0.02, 0.05), (6, 0.1, 0.0, 0.04)]
    lo = plucked_loop(36, P, parts, T_loop=0.32, name="bass")
    hi = plucked_loop(48, P // 2, parts, T_loop=0.32, name="bass")
    return Instrument("bass_up" if upright else "bass", [lo, hi], split(48), env=ENV_SHORT)


def inst_tuba():
    P = 100
    s = additive_loop(36, P, [(1, 1.0), (2, 0.85), (3, 0.6), (4, 0.3), (5, 0.18), (6, 0.08)], attack_periods=2, reps=1, name="tuba")
    return Instrument("tuba", [s], env=ENV_SHORT)


def inst_guitar():
    lo = ks_sample(52, P=96)          # E3
    hi = ks_sample(64, P=64)          # E4
    km = split(59)
    return Instrument("guitar", [lo, hi], km, env=ENV_SHORT)


def inst_mandolin():
    s = ks_sample(71, P=40, dur=0.5, decay=0.992, bright=1.0, damp=0.45)
    return Instrument("mandolin", [s], env=ENV_SHORT)


def inst_clav():
    return Instrument("clav", [clav_sample(60)], env=ENV_SHORT)


def drum_kit():
    return {"kick": kick(), "snare": snare_brush(), "rim": rim(), "hat": hat_closed(), "ohat": hat_open(),
            "shaker": shaker(), "swish": brush_swish(), "clave": clave(), "wood": woodblock()}
