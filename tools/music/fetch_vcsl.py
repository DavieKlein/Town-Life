"""Downloads the few VCSL samples the music uses (CC0, https://github.com/sgossner/VCSL, see art_source/audio/SOURCES.md)
into art_source/audio/vcsl/ (original files, untouched). Usage: python3 tools/music/fetch_vcsl.py [DEST]"""
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://raw.githubusercontent.com/sgossner/VCSL/master/"
TX = "Electrophones/TX81Z/FM Piano/"
VB = "Idiophones/Struck Idiophones/Vibraphone/Soft Mallets/"
MA = "Idiophones/Struck Idiophones/Marimba/"
HA = "Aerophones/Free Aerophones/Harmonica-Hohner-Super64/Sustains/Normal/"
ST = "Chordophones/Composite Chordophones/Strumstick/Finger/"
SI = "Idiophones/Struck Idiophones/"
ME = "Membranophones/Struck Membranophones/"

FILES = (
    [TX + f"FMPiano_{n}_vl2.wav" for n in ("C2", "C3", "C4", "C5", "C6")]
    + [VB + f"Vibes_soft_{n}.wav" for n in ("C3_v1_rr2_Main", "G3_v1_rr1_Main", "D4_v1_rr1_Main", "A4_v1_rr1_Main", "C5_v1_rr1_Main")]
    + [MA + f"Marimba_hit_Outrigger_{n}_med_01.wav" for n in ("F3", "C4", "G4", "F5", "C6")]
    + [HA + f"Hohner-Super64_Normal _{n}.wav" for n in ("C3", "G3", "C4", "G4", "C5", "G5")]
    + [ST + f"Strumstick_Finger_{n}_vl2_rr1.wav" for n in ("Str1_Main_D2", "Str2_Main_A2", "Str2_Main_D3", "Str3_Main_A3", "Str3_Main_D4", "Str3_Main_A4")]
    + [SI + "Hi-Hat Cymbal/HiHat_Close_rr1_Mid.wav", SI + "Hi-Hat Cymbal/HiHat_HitO_rr1_Mid.wav",
       SI + "Shaker, Small/Mid_ShakerDouble_Down_rr1.wav", SI + "Claves/Claves1_Hit_v2_rr1_Mid.wav",
       SI + "Tambourine 1/Tamb1_Hit_v1_rr1_Mid.wav", SI + "Woodblock/wood_click_mp.wav", SI + "Cajon/Cajon_hit1_mp_rr1.wav",
       ME + "Snare Drum, Modern 1/Snare2_HitSN_v3_rr1_Mid.wav", ME + "Bass Drum 1/BDrumNew_hit_v2_rr1_Sum.wav",
       ME + "Conga/Conga_HitN_v1_rr1_Sum.wav", "LICENSE"]
)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    dest = argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "art_source", "audio", "vcsl")
    os.makedirs(dest, exist_ok=True)
    for f in FILES:
        out = os.path.join(dest, os.path.basename(f) if f != "LICENSE" else "LICENSE-VCSL-CC0.txt")
        if os.path.exists(out):
            continue
        url = BASE + urllib.parse.quote(f)
        with urllib.request.urlopen(url, timeout=120) as r:
            data = r.read()
        open(out, "wb").write(data)
        print(f"{os.path.basename(out)} {len(data)} bytes")


if __name__ == "__main__":
    main()
