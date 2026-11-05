#!/usr/bin/env python3
"""Writes a Town Life save file (SRAM image, save version 2) for headless tests (tools/headless_run.py):

  python3 tools/make_save.py OUT.sav MAP X Y [--facing 0..7] [--minutes 480] [--day 1] [--money 20] [--bladder 50]
         [--name Sam] [--mission M03] [--needs 70,85,70,60,55] [--friend mia=40,lou=10] [--flag met_pimm,...] [--done P1,P2]
  python3 tools/headless_run.py town-life.gba "loadsram OUT.sav; reset; wait 120; press a; ..."

Maps: city_centre corner_market diner community_centre vaulttech_lobby public_toilet. X, Y in cells (feet).
The layout and the checksum mirror include/tl_save.h / src/tl_save.cpp."""
import argparse
import ctypes as ct
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cast  # noqa: E402
import story_data  # noqa: E402

MAPS = ["city_centre", "corner_market", "diner", "community_centre", "vaulttech_lobby", "public_toilet", "player_room", "vaultmart", "clinic"]


class Save(ct.Structure):
    _fields_ = [("magic", ct.c_uint32), ("version", ct.c_uint16), ("size", ct.c_uint16), ("checksum", ct.c_uint32),
                ("map", ct.c_uint8), ("facing", ct.c_uint8), ("x", ct.c_int16), ("y", ct.c_int16),
                ("day", ct.c_uint16), ("minutes", ct.c_uint16), ("minute_frames", ct.c_uint16),
                ("pad_world", ct.c_uint16), ("total_minutes", ct.c_int32), ("money", ct.c_int32),
                ("need_raw", ct.c_int32 * 5), ("bladder_boost", ct.c_int16), ("pad_needs", ct.c_uint16),
                ("bin_emptied", ct.c_int32 * 160), ("player_name", ct.c_char * 12),
                ("story_flags", ct.c_uint8 * 64), ("mission_id", ct.c_uint16), ("pad_mission", ct.c_uint16),
                ("friendship", ct.c_uint8 * 16),
                ("deposit_init", ct.c_uint8), ("deposit_cans", ct.c_uint8), ("deposit_bottles", ct.c_uint8),
                ("deposit_credit", ct.c_uint8), ("deposit_spot", ct.c_uint8 * 32), ("social_valid", ct.c_uint8), ("social", ct.c_uint8), ("items", ct.c_uint8 * 5),
                ("gift_day", ct.c_uint8 * 8), ("gossip", ct.c_uint8 * 8), ("scratch_day", ct.c_uint8), ("scratch_count", ct.c_uint8),
                ("spare", ct.c_uint8 * 3),
                ("topic_mem", (ct.c_uint8 * 8) * 8), ("talk_day", ct.c_uint8 * 8), ("gain_day", ct.c_uint8 * 8),
                ("gained", ct.c_uint8 * 8), ("coin_day", ct.c_uint8 * 8), ("coin70", ct.c_uint8),
                ("pad_story", ct.c_uint8), ("coins", ct.c_uint16), ("missions_done", ct.c_uint32),
                ("collect_mask", ct.c_uint16), ("collect_paid", ct.c_uint8), ("sick", ct.c_uint8), ("zero_min", ct.c_uint16 * 4),
                ("red_min", ct.c_uint16), ("sick_rest", ct.c_uint16), ("debt", ct.c_int16), ("debt_day", ct.c_uint8), ("faints", ct.c_uint8),
                ("msg_seen", ct.c_uint16), ("msg_read", ct.c_uint16), ("call_day", ct.c_uint8 * 8), ("delivery_item", ct.c_int8),
                ("pad_s64", ct.c_uint8), ("delivery_due", ct.c_int32)]


def make(path, a):
    s = Save()
    s.magic = 0x56534C54
    s.version = 3
    s.size = ct.sizeof(Save)
    s.map = MAPS.index(a.map)
    s.facing = a.facing
    s.x = int(a.x * 16)
    s.y = int(a.y * 16)
    s.day = a.day
    s.minutes = a.minutes
    s.money = a.money
    for i, v in enumerate(a.needs):
        s.need_raw[i] = int(v * 4096)         # bn::fixed: 12 fractional bits
    s.player_name = a.name.encode()[:11]
    codes = [m[0] for m in story_data.MISSIONS]
    s.mission_id = codes.index(a.mission) + 1 if a.mission else 0
    for f in filter(None, a.flag.split(",")):
        name, _, value = f.partition("=")
        s.story_flags[story_data.FLAGS.index(name)] = int(value) if value else 1
    mask = 0
    for c in filter(None, a.done.split(",")):
        mask |= 1 << codes.index(c)
    s.missions_done = mask
    for i, n in enumerate(cast.IDS):
        s.friendship[i] = story_data.NPC_INFO[n][3]
    for kv in filter(None, a.friend.split(",")):
        k, v = kv.split("=")
        s.friendship[cast.IDS.index(k)] = int(v)
    s.social_valid = 1
    s.social = a.social
    for i, v in enumerate(filter(None, a.items.split(","))):
        s.items[i] = int(v)
    for kv in filter(None, a.gossip.split(",")):       # rule index=day marker (1..250), e.g. 0=1
        k, v = kv.split("=")
        s.gossip[int(k)] = int(v)
    s.collect_mask = a.collect
    s.collect_paid = a.collect_paid
    s.sick = 1 if a.sick else 0
    for i, v in enumerate(a.zero):
        s.zero_min[i] = v
    s.red_min = a.red
    s.debt = a.debt
    s.msg_seen = a.msg_seen
    s.msg_read = a.msg_read
    s.delivery_item = a.delivery_item
    s.delivery_due = a.delivery_due
    raw = bytes(s)
    x, y = 1, 0
    for byte in raw[12:]:
        x = (x + byte) % 65521
        y = (y + x) % 65521
    s.checksum = (y << 16) | x
    open(path, "wb").write(bytes(s))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("map")
    p.add_argument("x", type=float)
    p.add_argument("y", type=float)
    p.add_argument("--facing", type=int, default=0)
    p.add_argument("--minutes", type=int, default=480)
    p.add_argument("--day", type=int, default=1)
    p.add_argument("--money", type=int, default=20)
    p.add_argument("--bladder", type=int, default=50)
    p.add_argument("--needs", default="", help="hunger,energy,hygiene,fun,bladder (default 50,50,50,50,--bladder)")
    p.add_argument("--name", default="Sam")
    p.add_argument("--mission", default="P1")
    p.add_argument("--friend", default="")
    p.add_argument("--flag", default="")
    p.add_argument("--done", default="")
    p.add_argument("--social", type=int, default=60)
    p.add_argument("--items", default="", help="gift counts: flowers,chocolate,hot sauce,cookies,newspaper")
    p.add_argument("--gossip", default="", help="rule=day marker, e.g. 0=1 (rule 0 noted on day 1)")
    p.add_argument("--collect", type=lambda v: int(v, 0), default=0, help="found collectibles bit mask (12 bits)")
    p.add_argument("--collect-paid", type=int, default=0)
    p.add_argument("--sick", action="store_true")
    p.add_argument("--zero", default="0,0,0,0", help="minutes a need was empty: hunger,energy,hygiene,social")
    p.add_argument("--red", type=int, default=0)
    p.add_argument("--debt", type=int, default=0)
    p.add_argument("--msg-seen", type=lambda v: int(v, 0), default=0)
    p.add_argument("--msg-read", type=lambda v: int(v, 0), default=0)
    p.add_argument("--delivery-item", type=int, default=-1)
    p.add_argument("--delivery-due", type=int, default=0)
    a = p.parse_args()
    a.zero = [int(v) for v in a.zero.split(",")]
    a.needs = [int(v) for v in a.needs.split(",")] if a.needs else [50, 50, 50, 50, a.bladder]
    make(a.out, a)
