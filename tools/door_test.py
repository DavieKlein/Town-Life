"""Door test (s81, run from the repo root): python3 tools/door_test.py ROM OUTDIR
ROM must be built with -DTL_DEBUG_POS. For every exterior door a save is made 2.5 cells in front of the door, the player walks into it
and two shots are taken (just before the fade ends, and inside). Prints the map reached. Hours matter: noon opens everything, 3:00 closes."""
import sys, subprocess
ROM, OUT = sys.argv[1], sys.argv[2]
DOORS = [  # (name, map, x, y, key, expected map or CLOSED)
    ("cc_corner", "city_centre", 44.0, 20.6, "up+right", "corner_market"),
    ("cc_diner", "city_centre", 53.0, 20.6, "up+right", "diner"),
    ("cc_clinic", "city_centre", 37.6, 20.6, "up+right", "clinic"),
    ("cc_library", "city_centre", 11.8, 21.2, "up+right", "community_centre"),
    ("cc_lobby", "city_centre", 63.0, 16.6, "up+right", "vaulttech_lobby"),
    ("cc_toilet", "city_centre", 3.1, 42.2, "up+right", "public_toilet"),
    ("ob_laundromat", "old_block", 32.45, 20.6, "up+right", "laundromat"),
    ("ob_bakery", "old_block", 45.5, 20.6, "up+right", "bakery"),
    ("ob_lane", "old_block", 52.2, 52.5, "up+left", "lane_shop"),
]
for hour, tag in ((720, "open"), (180, "closed")):
    for name, mp, x, y, key, exp in DOORS:
        if tag == "closed" and name in ("cc_toilet", "cc_clinic", "cc_corner"):
            continue
        sav = "%s/d.sav" % OUT
        args = ["python3", "tools/make_save.py", sav, mp, str(x), str(y), "--minutes", str(hour), "--day", "3", "--needs", "80,80,80,80,80"]
        if mp == "old_block":
            args += ["--flag", "old_block_open"]
        subprocess.run(args, check=True, capture_output=True)
        cmds = "loadsram %s; reset; wait 150; press a; wait 240; hold %s 70; shot %s/%s_%s_a.png; wait 80; shot %s/%s_%s_b.png; state" % (sav, key, OUT, name, tag, OUT, name, tag)
        r = subprocess.run(["python3", "tools/playtest_driver.py", ROM, cmds], capture_output=True, text=True)
        print(tag, name, "expected", exp, "->", [l for l in r.stdout.splitlines() if "map" in l.lower()][-1:] or r.stdout[-200:])
