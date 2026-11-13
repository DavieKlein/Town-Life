"""Real-sample instruments from the CC0 Versilian Community Sample Library (see art_source/audio/SOURCES.md).

The original recordings (44.1/48 kHz, 24 bit, stereo, 5-12 s) are fetched by fetch_vcsl.py into art_source/audio/vcsl/ and are turned here
into small, smooth 8-bit samples for the maxmod mixer:
  * resampled with ffmpeg (proper anti-alias filter) to the content rate MIX_RATE (the GBA mixing rate chosen in the Makefile),
    so a note is played with at most about one sample step per output sample (no skipping = no aliasing "grit");
  * the pitch of every sample is measured (autocorrelation) and corrected through the XM relative note / finetune;
  * trimmed, faded out (no hard end), normalised to full 8-bit scale (volume is applied by the channel / volume column);
  * sustained instruments (harmonica) get a cross-faded loop whose length is a whole number of periods.
"""
import math
import os
import subprocess
import numpy as np
from xm import Sample, Instrument
import synth as S

VCSL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "art_source", "audio", "vcsl")
MIX_RATE = 21024     # content rate = maxmod mixing rate (Makefile BN_CFG_AUDIO_MIXING_RATE)
ENV_SOFT = [(0, 64), (6, 0)]       # key-off: 6 ticks release (no clicks)
ENV_LONG = [(0, 64), (10, 0)]


def load(name, rate=MIX_RATE):
    f = os.path.join(VCSL, name)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", str(rate), "-af", "aresample=resampler=soxr:precision=28",
                          "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(float)


_f0_cache = {}


def measure_f0(name, expect_midi):
    """Fundamental of a recording by autocorrelation near the expected pitch (sub-cent accuracy is not needed, ~1 cent is)."""
    if name in _f0_cache:
        return _f0_cache[name]
    sr = 22050
    f = os.path.join(VCSL, name)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(float)
    a = int(0.25 * sr)
    seg = x[a:a + 16384]
    seg = seg - seg.mean()
    ac = np.correlate(seg, seg, "full")[len(seg) - 1:]
    ac /= ac[0] + 1e-12
    fe = S.mtof(expect_midi)
    lo, hi = int(sr / (fe * 1.06)), int(sr / (fe / 1.06))
    k = lo + int(np.argmax(ac[lo:hi]))
    y0, y1, y2 = ac[k - 1], ac[k], ac[k + 1]
    d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    r = sr / (k + d)
    _f0_cache[name] = r
    return r


def lowpass_fft(x, rate, hz):
    n = len(x)
    sp = np.fft.rfft(x)
    fr = np.fft.rfftfreq(n, 1 / rate)
    w = np.clip((hz * 1.15 - fr) / (hz * 0.3), 0, 1)       # smooth roll-off
    return np.fft.irfft(sp * w, n)


def room(x, rate, amount=0.12):
    """a touch of baked-in room: two soft early reflections plus a short noise tail"""
    out = x.copy()
    for d, g in ((0.043, 0.55), (0.071, 0.4), (0.113, 0.28), (0.167, 0.18)):
        k = int(d * rate)
        out[k:] += amount * g * x[:-k]
    return out


def trim_start(x, thresh=0.02):
    m = np.abs(x)
    i = int(np.argmax(m > thresh * m.max()))
    return x[max(0, i - 8):]


def one_shot(name, root_midi, dur, fade=0.25, lp=0.42, reverb=0.0, attack=0.002, gain=1.0):
    """(Sample) a trimmed one-shot of a recording; the note plays at its natural speed at root_midi."""
    x = load(name)
    x = trim_start(x)
    x = x[:int(dur * MIX_RATE)]
    if reverb:
        x = room(x, MIX_RATE, reverb)
    x = lowpass_fft(x, MIX_RATE, lp * MIX_RATE)
    n = len(x)
    x = S.fade_out(x, int(fade * MIX_RATE))
    x = S.ramp_in(x, int(attack * MIX_RATE))
    x = S.norm(x * gain, 0.98)
    f0 = measure_f0(name, root_midi)
    # playing note root_midi must give mtof(root_midi): playback rate = R * target / measured
    rate = MIX_RATE * S.mtof(root_midi) / f0
    return S.root_sample(x, rate, root_midi, name=os.path.splitext(name)[0][:22])


def looped(name, root_midi, attack_s=0.35, loop_s=0.6, lp=0.42, xfade_s=0.12, tail_s=0.0):
    """Sustained sample: attack part + a whole-periods loop with a cross-faded join."""
    f0 = measure_f0(name, root_midi)
    x = load(name)
    x = trim_start(x)
    period = MIX_RATE / f0
    nper = max(2, int(round(loop_s * f0)))
    L = int(round(nper * period))
    A = int(attack_s * MIX_RATE)
    X = int(round(max(2, round(xfade_s * f0)) * period))
    X = min(X, L // 2, A)
    seg = x[:A + L].copy()
    # the end of the loop blends into what precedes the loop start (a whole number of periods apart -> in phase)
    t = np.linspace(0, 1, X)
    pre = seg[A - X:A]
    seg[A + L - X:A + L] = seg[A + L - X:A + L] * (1 - t) + pre * t
    seg = lowpass_fft(seg, MIX_RATE, lp * MIX_RATE)
    seg = S.ramp_in(seg, int(0.004 * MIX_RATE))
    seg = S.norm(seg, 0.98)
    rate = MIX_RATE * S.mtof(root_midi) / f0
    return S.root_sample(seg, rate, root_midi, loop=(A, L), name=os.path.splitext(name)[0][:22])


def zoned(name, items, env=ENV_SOFT, vib=None):
    """items: list of (lo_midi, Sample); a note uses the zone with the highest lo <= note."""
    items = sorted(items, key=lambda t: t[0])
    km = [0] * 96
    for idx in range(96):
        m = idx + 12
        km[idx] = max(i for i, (lo, _) in enumerate(items) if lo <= m or i == 0)
    return Instrument(name, [s for _, s in items], km, env=env, vib=vib)


def zones_from_roots(roots, spread_down=3):
    """lo boundaries halfway between neighbouring roots"""
    roots = sorted(roots)
    los = [0]
    for a, b in zip(roots, roots[1:]):
        los.append((a + b + 1) // 2)
    return los


# ------------------------------------------------------------------------------------------------ instruments
def inst_epiano():
    files = [("FMPiano_C3_vl2.wav", 48, 1.5), ("FMPiano_C4_vl2.wav", 60, 1.3), ("FMPiano_C5_vl2.wav", 72, 1.0), ("FMPiano_C6_vl2.wav", 84, 0.7)]
    los = zones_from_roots([r for _, r, _ in files])
    return zoned("epiano", [(lo, one_shot(f, r, d, 0.3, 0.40, 0.10)) for lo, (f, r, d) in zip(los, files)], ENV_SOFT)


def inst_vibes():
    files = [("Vibes_soft_C3_v1_rr2_Main.wav", 60, 2.0), ("Vibes_soft_G3_v1_rr1_Main.wav", 67, 2.0), ("Vibes_soft_D4_v1_rr1_Main.wav", 74, 1.6),
             ("Vibes_soft_A4_v1_rr1_Main.wav", 81, 1.3), ("Vibes_soft_C5_v1_rr1_Main.wav", 84, 1.0)]
    los = zones_from_roots([r for _, r, _ in files])
    return zoned("vibes", [(lo, one_shot(f, r, d, 0.4, 0.42)) for lo, (f, r, d) in zip(los, files)], ENV_LONG)


def inst_marimba():
    files = [("Marimba_hit_Outrigger_F3_med_01.wav", 65, 0.9), ("Marimba_hit_Outrigger_C4_med_01.wav", 72, 0.8),
             ("Marimba_hit_Outrigger_G4_med_01.wav", 79, 0.7), ("Marimba_hit_Outrigger_F5_med_01.wav", 89, 0.6)]
    los = zones_from_roots([r for _, r, _ in files])
    return zoned("marimba", [(lo, one_shot(f, r, d, 0.2, 0.42, gain=1.0)) for lo, (f, r, d) in zip(los, files)], ENV_SOFT)


def inst_harmonica():
    files = [("Hohner-Super64_Normal _C3.wav", 60), ("Hohner-Super64_Normal _G3.wav", 67), ("Hohner-Super64_Normal _C4.wav", 72),
             ("Hohner-Super64_Normal _G4.wav", 79), ("Hohner-Super64_Normal _C5.wav", 84), ("Hohner-Super64_Normal _G5.wav", 91)]
    los = zones_from_roots([r for _, r in files])
    return zoned("harmonica", [(lo, looped(f, r, 0.30, 0.45, 0.20)) for lo, (f, r) in zip(los, files)], ENV_LONG, vib=(30, 2, 20))


def inst_strum():
    files = [("Strumstick_Finger_Str1_Main_D2_vl2_rr1.wav", 50, 1.4), ("Strumstick_Finger_Str2_Main_A2_vl2_rr1.wav", 57, 1.3),
             ("Strumstick_Finger_Str2_Main_D3_vl2_rr1.wav", 62, 1.2), ("Strumstick_Finger_Str3_Main_A3_vl2_rr1.wav", 69, 1.0),
             ("Strumstick_Finger_Str3_Main_D4_vl2_rr1.wav", 74, 0.9), ("Strumstick_Finger_Str3_Main_A4_vl2_rr1.wav", 81, 0.7)]
    los = zones_from_roots([r for _, r, _ in files])
    return zoned("strum", [(lo, one_shot(f, r, d, 0.3, 0.30)) for lo, (f, r, d) in zip(los, files)], ENV_SOFT)


# ---- drums: recorded samples, trimmed, played at C-4 (rate = content rate)
def drum_sample(name, dur, fade=0.05, lp=0.42, gain=1.0, attack=0.001):
    x = load(name)
    x = trim_start(x, 0.05)[:int(dur * MIX_RATE)]
    x = lowpass_fft(x, MIX_RATE, lp * MIX_RATE)
    x = S.fade_out(x, int(fade * MIX_RATE))
    x = S.ramp_in(x, int(attack * MIX_RATE))
    x = S.norm(x * gain, 0.98)
    s = S.shift_for(MIX_RATE, 60)
    rel = math.floor(s)
    ft = int(round((s - rel) * 128))
    return Instrument(os.path.splitext(name)[0][:20], [Sample_(x, rel, ft, name)], env=None)


def Sample_(x, rel, ft, name):
    from xm import Sample
    return Sample(x, rel, ft, None, 64, name[:22])


def drum_kit():
    k = {}
    k["kick"] = drum_sample("BDrumNew_hit_v2_rr1_Sum.wav", 0.45, 0.15, 0.20)
    k["snare"] = drum_sample("Snare2_HitSN_v3_rr1_Mid.wav", 0.30, 0.12, 0.40)
    k["cajon"] = drum_sample("Cajon_hit1_mp_rr1.wav", 0.25, 0.08, 0.40)
    k["hat"] = drum_sample("HiHat_Close_rr1_Mid.wav", 0.14, 0.06, 0.40)
    k["ohat"] = drum_sample("HiHat_HitO_rr1_Mid.wav", 0.35, 0.2, 0.40)
    k["shaker"] = drum_sample("Mid_ShakerDouble_Down_rr1.wav", 0.14, 0.06, 0.40)
    k["clave"] = drum_sample("Claves1_Hit_v2_rr1_Mid.wav", 0.15, 0.06, 0.40)
    k["tamb"] = drum_sample("Tamb1_Hit_v1_rr1_Mid.wav", 0.30, 0.15, 0.40)
    k["wood"] = drum_sample("wood_click_mp.wav", 0.20, 0.08, 0.40)
    k["conga"] = drum_sample("Conga_HitN_v1_rr1_Sum.wav", 0.30, 0.12, 0.36)
    for key, ins in k.items():
        ins.name = key
    return k


def gated_snare():
    """cold gated snare: the recorded snare cut hard after 0.11 s"""
    ins = drum_sample("Snare2_HitSN_v3_rr1_Mid.wav", 0.11, 0.012, 0.42)
    ins.name = "gsnare"
    return ins
