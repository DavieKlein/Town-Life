#!/usr/bin/env python3
"""(s50 copy: knows the deposit fields.) Writes a Town Life save file (SRAM image) that starts the game on a chosen map and position, so headless
tests can skip the walk. Use with tools/headless_run.py:

  python3 make_save.py /tmp/s.sav diner 3.0 5.0 [facing 0..7] [minutes 480] [bladder 80]
  python3 tools/headless_run.py town-life.gba "loadsram /tmp/s.sav; reset; wait 120; press a(Continue); ..."

Maps: city_centre corner_market diner community_centre vaulttech_lobby public_toilet. x, y in cells (feet).
Layout and checksum mirror include/tl_save.h / src/tl_save.cpp (version 1)."""
import ctypes as ct
import sys

MAPS = ["city_centre", "corner_market", "diner", "community_centre", "vaulttech_lobby", "public_toilet"]


class Save(ct.Structure):
    _fields_ = [("magic", ct.c_uint32), ("version", ct.c_uint16), ("size", ct.c_uint16), ("checksum", ct.c_uint32),
                ("map", ct.c_uint8), ("facing", ct.c_uint8), ("x", ct.c_int16), ("y", ct.c_int16),
                ("day", ct.c_uint16), ("minutes", ct.c_uint16), ("minute_frames", ct.c_uint16),
                ("pad_world", ct.c_uint16), ("total_minutes", ct.c_int32), ("money", ct.c_int32),
                ("need_raw", ct.c_int32 * 5), ("bladder_boost", ct.c_int16), ("pad_needs", ct.c_uint16),
                ("bin_emptied", ct.c_int32 * 128), ("player_name", ct.c_char * 12),
                ("story_flags", ct.c_uint8 * 64), ("mission_id", ct.c_uint16), ("pad_mission", ct.c_uint16),
                ("friendship", ct.c_uint8 * 16), ("deposit_init", ct.c_uint8), ("deposit_cans", ct.c_uint8),
                ("deposit_bottles", ct.c_uint8), ("deposit_credit", ct.c_uint8), ("deposit_spot", ct.c_uint8 * 32),
                ("spare", ct.c_uint8 * 28)]


def make(path, map_name, x, y, facing=0, minutes=480, needs=(50, 50, 50, 50, 50), money=20, deposit=None):
    """deposit = (cans, bottles, credit, {spot: code}) writes the deposit state (code = kind 1 can / 2 bottle | variant << 2)."""
    s = Save()
    s.magic = 0x56534C54
    s.version = 1
    s.size = ct.sizeof(Save)
    s.map = MAPS.index(map_name)
    s.facing = facing
    s.x = int(x * 16)
    s.y = int(y * 16)
    s.day = 1
    s.minutes = minutes
    s.money = money
    for i, v in enumerate(needs):
        s.need_raw[i] = int(v * 4096)         # bn::fixed: 12 fractional bits
    if deposit:
        s.deposit_init = 1
        s.deposit_cans, s.deposit_bottles, s.deposit_credit = deposit[:3]
        for k, v in deposit[3].items():
            s.deposit_spot[k] = v
    raw = bytes(s)
    a, b = 1, 0
    for byte in raw[12:]:
        a = (a + byte) % 65521
        b = (b + a) % 65521
    s.checksum = (b << 16) | a
    open(path, "wb").write(bytes(s))


if __name__ == "__main__":
    a = sys.argv
    make(a[1], a[2], float(a[3]), float(a[4]), int(a[5]) if len(a) > 5 else 0, int(a[6]) if len(a) > 6 else 480,
         tuple([50, 50, 50, 50, int(a[7])]) if len(a) > 7 else (50, 50, 50, 50, 50))
