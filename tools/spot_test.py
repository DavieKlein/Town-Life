"""Spot shots (s81): python3 tools/spot_test.py ROM OUTDIR - screenshots of the new toilet nooks (+ A menu), the garden and the alleys."""
import sys, subprocess
ROM, OUT = sys.argv[1], sys.argv[2]
SPOTS = [  # name, map, x, y, commands after boot
    ("diner_nook", "diner", 10.3, 2.0, "hold right 30; wait 20; shot {o}"),
    ("diner_wc_menu", "diner", 11.9, 2.8, "wait 20; press a; wait 30; shot {o}"),
    ("diner_sink_menu", "diner", 13.4, 2.2, "wait 20; press a; wait 30; shot {o}"),
    ("bakery_nook", "bakery", 9.5, 2.0, "hold right 30; wait 20; shot {o}"),
    ("bakery_wc_menu", "bakery", 11.2, 2.8, "wait 20; press a; wait 30; shot {o}"),
    ("garden_gate", "old_block", 22.2, 25.8, "hold up+right 30; wait 20; shot {o}"),
    ("garden_mid", "old_block", 22.2, 33.0, "wait 20; shot {o}"),
    ("alley_north", "old_block", 23.2, 19.5, "hold up+right 90; wait 20; shot {o}"),
    ("alley_east", "old_block", 59.2, 19.5, "hold up+right 90; wait 20; shot {o}"),
    ("yard", "old_block", 36.9, 19.5, "hold up+right 90; wait 20; shot {o}"),
    ("valdez_door", "old_block", 19.5, 21.5, "wait 20; shot {o}"),
    ("trench", "old_block", 9.0, 22.5, "wait 20; shot {o}"),
]
for name, mp, x, y, cmds in SPOTS:
    sav = "%s/s.sav" % OUT
    args = ["python3", "tools/make_save.py", sav, mp, str(x), str(y), "--minutes", "780", "--day", "3", "--needs", "40,80,80,40,30"]
    if mp == "old_block":
        args += ["--flag", "old_block_open"]
    subprocess.run(args, check=True, capture_output=True)
    out = "%s/%s.png" % (OUT, name)
    r = subprocess.run(["python3", "tools/playtest_driver.py", ROM, "loadsram %s; reset; wait 150; press a; wait 240; %s" % (sav, cmds.format(o=out))], capture_output=True, text=True)
    print(name, r.returncode, r.stderr[-120:])
