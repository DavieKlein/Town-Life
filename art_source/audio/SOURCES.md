# Audio sources

All music and sound effects in Town Life are original compositions / synthesis. The only third-party audio material are the
instrument and percussion recordings below, which are turned into small 8-bit samples by `tools/music/sampler.py`.

## Versilian Community Sample Library (VCSL)

- Author: Versilian Studios LLC (Samuel Gossner and contributors)
- URL: https://github.com/sgossner/VCSL
- Licence: **CC0 1.0 Universal** (public domain dedication; the repository `LICENSE` file was read on 2026-11-12 and is saved next to the
  downloaded files as `art_source/audio/vcsl/LICENSE-VCSL-CC0.txt` by `tools/music/fetch_vcsl.py`). README: "Essentially it's Public Domain -
  you can do whatever you want with these sounds (even make commercial software), no royalties, no credit, no special terms."
- Credit is not required but is given in the README anyway.
- The original WAV files (about 35 MB) are NOT committed: `python3 tools/music/fetch_vcsl.py` (run by `build_audio.py`) downloads exactly these
  files into `art_source/audio/vcsl/` (git-ignored). The generated `audio/*.xm` modules contain the derived 8-bit samples (committed).

Files used (path inside the repository):

| Use | File |
|---|---|
| Electric piano (Yamaha TX81Z "FM Piano" patch sampled from hardware by the VCSL authors; part of the CC0 repository) | `Electrophones/TX81Z/FM Piano/FMPiano_C3|C4|C5|C6_vl2.wav` |
| Vibraphone, soft mallets | `Idiophones/Struck Idiophones/Vibraphone/Soft Mallets/Vibes_soft_C3_v1_rr2_Main, G3_v1_rr1, D4_v1_rr1, A4_v1_rr1, C5_v1_rr1` |
| Marimba | `Idiophones/Struck Idiophones/Marimba/Marimba_hit_Outrigger_F3|C4|G4|F5_med_01.wav` |
| Harmonica (accordion voice of Old Block, city B section) | `Aerophones/Free Aerophones/Harmonica-Hohner-Super64/Sustains/Normal/Hohner-Super64_Normal _C3|G3|C4|G4|C5|G5.wav` |
| Strumstick (the "acoustic guitar" of Old Block) | `Chordophones/Composite Chordophones/Strumstick/Finger/Strumstick_Finger_Str1_Main_D2, Str2_Main_A2, Str2_Main_D3, Str3_Main_A3, Str3_Main_D4, Str3_Main_A4 (vl2_rr1)` |
| Drums and percussion | `Idiophones/Struck Idiophones/` Hi-Hat Cymbal (HiHat_Close_rr1_Mid, HiHat_HitO_rr1_Mid), Shaker, Small (Mid_ShakerDouble_Down_rr1), Claves (Claves1_Hit_v2_rr1_Mid), Tambourine 1 (Tamb1_Hit_v1_rr1_Mid), Woodblock (wood_click_mp), Cajon (Cajon_hit1_mp_rr1); `Membranophones/Struck Membranophones/` Snare Drum, Modern 1 (Snare2_HitSN_v3_rr1_Mid), Bass Drum 1 (BDrumNew_hit_v2_rr1_Sum), Conga (Conga_HitN_v1_rr1_Sum) |

The bass is synthesised, as are all sound effects (`tools/music/synth.py`, `tools/music/sfx.py`).
