# Bug reports and the black box

The owner plays on a phone (Lemuroid) and has no PC, so the game carries its own bug reporter. Press **L + R together** at any time
(walking, pause menu, menus, dialogue, cutscenes, minigames), pick what went wrong, and the game files a report in its save memory. The
report holds the last ~15-30 seconds of play, so we can replay it headlessly and see what the owner saw.

Code: `include/tl_blackbox.h`, `src/tl_blackbox.cpp` (+ small hooks in `src/main.cpp`, `include/tl_field.h`, `src/tl_save.cpp`).
Tool: `tools/bug_report.py`.

## How it works in the game

- **Trigger:** L and R held at the same moment (the second key going down while the first is held, or both in the same frame). It is
  disabled in `-DTL_DEBUG_TELEPORT` builds (they use L/R). It is not active on the title screen, in the intro cards or in name entry
  (name entry uses L/R for upper/lower case) because the black box only starts once a field exists.
- **Panel "Report a bug":** Game froze / stuck, Graphics glitch, Text problem, Can't do objective, Other, Cancel. A = choose, B = cancel.
  Then "Bug report saved (#n). Thanks!" and the game carries on exactly where it was.
- **Busy screens:** the panel needs about 380 sprite tiles and 34 sprites. The pause screen (and an open shop/interaction menu) is
  closed first to make room (press START again afterwards). A dialogue with a portrait leaves just enough. If there is still not enough
  room (for example inside a minigame: STOCK IT! / PLATE RUSH use almost every tile) the report is filed immediately as "Other" and a
  one-line note "Bug report saved (#n)." shows for 2 seconds. Nothing is ever lost.
- **If the game is really frozen** (a dead lock with no `bn::core::update()` any more) the trigger cannot run. A stuck menu, dialogue,
  cutscene wait or minigame still runs the main loop, so L+R normally still works there; only a hard hang (crash screen, endless loop
  without frames) cannot be reported. In that case write down what you did and send the save as it is.

## The black box (always running)

A `bn::core` update callback (`blackbox::on_update`) runs once per frame, whatever scene is active (field, menus, dialogue, minigames),
and costs a few dozen instructions:

- records the **keypad state of every frame**, run-length encoded (u16 = 10 key bits | (frames - 1) << 10), ring of 2048 entries (4 KB)
  in EWRAM. Idle/held keys cost one entry per 64 frames, so 30 s of normal play is 30-300 entries;
- every **15 s** (900 frames) takes a snapshot of the **full `save_data`** (what "Save game" would write, ~1 KB) plus the `bn::random`
  state of the field. Two slots, so one is always 15-30 s old. A snapshot waits up to 10 s for a calm moment (free walking, nothing
  open: `field::blackbox_calm()`), then is taken anyway (flag "not calm" in the report);
- keeps a frame counter and a few markers: minigame started, field rebuilt after a minigame, report filed. After a minigame the field is
  rebuilt, so a new snapshot is taken at once and the older one is dropped (a replay can only start after the scene change).
- EWRAM use: about 14 KB (log 4 KB, report buffer 5.2 KB, snapshots 2 KB, state). `field` in `main.cpp` was moved to EWRAM
  (`BN_DATA_EWRAM_BSS static bn::optional<tl::field>`): it is ~14 KB and sat on the 32 KB IWRAM stack, which left no room for the panel
  and any other growth (with extra static data the game hung at start). Keep large objects out of the IWRAM stack.

## Where reports live (SRAM)

```
0      .. 4095       the normal save (save_data, ~1 KB; static_assert in tl_save.h keeps it <= 4096 bytes)
4096   .. 4159       region header "TLBR": version, number of the next report, replay request (flag + rng), checksum
4160   .. 25119      4 report slots of 5240 bytes (ring: report n goes to slot (n-1) % 4), each "TLBX" + checksum
25120  .. 32767      free
```

The `static_assert` in `tl_blackbox.h` fails the build if the region would not fit in the 32 KB of SRAM (shrink `log_capacity` then).
A report has: category, flags (snapshot usable / not calm / in a minigame / no snapshot), map, position, day, time, money at the time of
the report, frame counters, markers, the build string (`__DATE__ __TIME__`, the same text as on the title screen), the random state, the
snapshot (`save_data`, finalised so it is a valid normal save) and the input log from the snapshot until the report (<= 4 KB).
Normal saving/loading only touches offset 0..sizeof(save_data), reports only touch 4096 and up, so they never disturb each other and the
save version did not change. Bad checksums are skipped by the tool; an empty/garbage region is initialised on boot.

## Sending a report (owner)

Where the file is: Lemuroid saves the game memory ("SRAM") as a `.srm` file named after the ROM, i.e. `town-life.srm`, in its **saves**
folder. I could not verify this on a device, so this is the most likely layout; if it is different, look for the file named
`town-life.srm` (or `Town Life.srm`):

1. In Lemuroid open **Settings** and look at *Advanced* / *Storage* for the *Lemuroid folder* (default: the app's own storage
   `Android/data/com.swordfish.lemuroid/files/`; if you picked a folder yourself (for example `Documents/Lemuroid`), it is that one).
2. Inside it there is a folder `saves` with `town-life.srm` (other folders there: `roms`, `states`, `states-previews`).
3. Open it with an Android file manager (the "Files" app by Google, or Samsung "My Files"; on Android 11+ the `Android/data` folder is
   hidden from most file managers, which is another reason to pick a normal folder like `Documents/Lemuroid` as Lemuroid's folder
   in the Lemuroid settings once; the save is moved/kept by Lemuroid when you do that - make a copy first).
4. Share / send the `.srm` file to the developer (messaging app, mail, Drive...).

Important: Lemuroid writes the game memory to the `.srm` when you **leave the game** (back button -> quit game) or when the app goes to
the background. After pressing L+R and seeing "Bug report saved", leave the game once with the menu **Quit** in Lemuroid, then copy the
file. A normal "Save game" in the pause menu is not needed (and does not remove the reports).

### Korte uitleg (Nederlands)

1. Gebeurt er iets geks in het spel (vastgelopen, rare plaatjes, tekst klopt niet, je kunt een opdracht niet doen)? Druk dan op
   **L en R tegelijk**.
2. Kies wat er mis is (bijv. "Graphics glitch") met omhoog/omlaag en druk op **A**. Je ziet "Bug report saved (#1). Thanks!" en het spel
   gaat gewoon door. Lukt het menu niet te openen (bijv. in een minigame), dan komt er onderin alleen "Bug report saved" te staan: ook goed.
3. Sluit het spel daarna netjes af in Lemuroid (terugknop, dan het spel afsluiten), zodat Lemuroid de opslag wegschrijft.
4. Zoek het bestand **town-life.srm** in de map `saves` van Lemuroid (zie Lemuroid > Instellingen voor de Lemuroid-map; vaak
   `Android/data/com.swordfish.lemuroid/files/saves/` of de map die je zelf hebt gekozen). Weet je het niet zeker? Zoek in de
   bestandsbeheer-app op `town-life`.
5. Stuur dat ene bestand naar mij (WhatsApp, mail, Drive). Schrijf er kort bij wat je deed. Er passen 4 meldingen in; de oudste wordt
   overschreven. Je normale opgeslagen spel blijft gewoon werken.

## Replaying a report (developer)

```
apt-get install -y libretro-mgba               # once; Pillow is already installed
python3 tools/bug_report.py list   town-life.srm
python3 tools/bug_report.py replay town-life.srm 2 --rom town-life.gba --out /tmp/replay2 [--png-every 30] [--gif-every 6]
python3 tools/bug_report.py dump   town-life.srm 2 /tmp/snapshot.sav      # the snapshot as a normal save (headless_run.py loadsram)
```

Use the ROM of the **same build** as the report (the tool compares the build string and warns). `replay`:

1. builds an SRAM image with the report's snapshot as the normal save, plus a replay request in the region header (the field's random
   state at the snapshot);
2. boots the ROM in the libretro mGBA core (same core as Lemuroid), presses A on "Continue"; `main.cpp` sees the replay request,
   restores the random state, skips the fade-in and starts the black box counter at 0;
3. feeds the recorded keypad states **in step with the game's own frame counter** (read from the emulator state: the libretro core does
   not expose work RAM, so the tool serialises the state and finds the magic `TLBB`). L and R are masked (the chord that opened the panel
   must not open it again). Frame n of the log is applied to the game's n-th logic frame; the first log entry is lost (the game's first
   frame is polled before the counter exists);
4. writes `frames/frame_NNNNN.png` every N frames, `replay.gif` (2x, key overlay), `final.png`, and `summary.txt` with the report details
   and a comparison of the final map / position / day / time / money of the replay with the values stored in the report.

### Determinism

What is restored exactly: everything in `save_data` (needs, money, time, flags, missions, bins, deposits, items ...), the position, the
random state of the field, and the input of every frame. Test results (headless, 20-25 s windows: one plain walk and three runs of random key mashing with A presses, menus and a map
change, normal build): 3 of 4 replays ended in exactly the same map / position / time / money, one ended 0.06 cells (1 px) away. What is **not** restored: positions and states of animals and NPC walking, pigeons/squirrels, toasts, an open menu /
conversation / cutscene at the snapshot moment (the replay starts in free walking; if the snapshot was "not calm" the tool says so), a
timed activity in progress, the minigame rng, hardware timing (a frame the real phone missed is one update with 2 vblanks in both the
original and the replay, because input is applied per update, but background sprite timing can differ). So a replay shows the same
situation and usually the same events; when it differs, the report details (category, time, map, build) and the markers still help.
Reports filed inside a minigame have no field snapshot after the minigame start: only the details are available.

## Updating

- Adding fields to `save_data` changes `sizeof(save_data)` and thereby the report slot size: old reports in a `.srm` then fail the
  `size` check and are skipped; bump `format_version` in `tl_blackbox.cpp` and the tool if the report layout changes.
- `tools/make_save.py`'s `Save` ctypes struct is used by the tool: keep it in step with `tl_save.h` (the build of the tool fails
  loudly on a size mismatch).
