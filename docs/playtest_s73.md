# Playtest s73 (headless, branch `claude/intelligent-hawking-y0vl2t`)

Goal: get the ROM ready for the owner's first full phone test. Everything below was played in the mGBA libretro core (the Lemuroid core)
with scripted input; screenshots and the new state dump were checked by eye and by script. Tool: `tools/playtest_driver.py`
(see its header; build with `-DTL_DEBUG_POS`, never combine `-DTL_DEBUG_CPU` with story runs that start a minigame, see "Not fixed").

## What was tested

**Normal (non-debug) build**: title -> New Game -> intro cards -> name entry (Sama) -> confirm -> wake up in the room (dialogue pages, hint
page, bed menu) -> stairs -> briefing (Rosa/Dex/Mia) -> STOCK IT! with real key input; "What's next?" in Rosa's talk menu skips to 9:00
(Pimm arrives) and its Bye ends the talk. Pause screen, Save game, reset, Continue restores map/position/time/needs/flags.

**Debug builds (AUTO_TALK + BOT + POS) - the whole prologue, New Game to mission X1**: wake_up -> briefing -> STOCK IT! (rank S, $22) ->
stock_react -> 9:00 pimm_arrives -> crate "Take the rye loaf" -> give it to Pimm -> pimm_leaves -> staff_lunch (12:00, "Two hours later",
14:00) -> vault_day (golden car, Valet, Dex, firing, Rosa's pay $22, Mia's goodbye, voucher) -> 18:15 outside, objective checklist
"Eat [ ] Wash [ ] Sleep on a bench" -> pancakes at the diner, fountain "Wash face" (flags `ate_evening`, `washed_evening`) -> bench
Sleep (woke at Energy 100, `slept_on_bench`) -> news_day2 (flag `read_newspaper`) -> accident popup at 0:40 (Bladder 0) -> public toilet
(toilet, shower $1, sink) -> Day 2 7:15 diner: mia_tip (RETURN & EARN) -> Lou "Ask about work" (Hygiene >= 40) -> mission X1 at 7:41 ->
"Work a shift" at 10:30 -> PLATE RUSH "Pan Tuesday" (daily special) -> wage paid ($11 -> $25), needs reduced. Every objective was completable
by doing what it says; all mission objectives are <= 48 chars (script-checked), dynamic ones (rye loaf, checklist, flyers, crates) are <= 38.

**Systems (each in the real map, via make_save states + the driver):**
- Interactables: every entry of `tools/interactions.py` in diner, community centre, VaultTech lobby, public toilet, VaultMart, clinic
  (scan: each one opens its menu/dialogue from the arrival point); notice board odd jobs: flyers (3 spots, +$5, toasts), sort books
  (+$4), Lou's crates taken at the board; kiosk scratch card ($1), bins, sinks, shower, toilet, fountain, bench Sit/Sleep, seats.
- RETURN & EARN: pickups from the real loose spots (can/bottle), bag counter, machine "Return all" pays exactly ($4 for 3 cans + 2 bottles +
  1 credit), "Check credit", credit saved. Collectibles: pick up, "Found" panel, Collection screen.
- Phone (SELECT): contacts, messages (Rosa), order food (pizza, delivery after 30 min, money taken). Gifts: Lou small talk, friendship
  meter +/-; gossip/gifts rules read only (no new test). Pause screen, mission log line, save/continue, bed save dialog ("Slept well. Save game?").
- Health: Feeling great state, red/green HUD markers, sick icon, faint (zero counter 58 -> 60 min) -> clinic -> Dr. Okafor -> debt text,
  clinic check-up ($8).
- Day rollover 23:51 -> 00:01 day 3 ("Wednesday"), night lighting, lamp pools, lit windows, dusk palette; Pimm walks his park route
  (16:00-19:30), walking behind the bus shelter/objects (per-pixel depth) with the V1 maps; VaultMart kiosks (robot voice, prices) and
  the staff gate text.
- Random-input soak: 12 saves x 1500 random inputs and 6 New Games x 2500 random inputs (D-pad, A/B, START, SELECT, run): no hang, no
  crash, the field frame counter advanced all the time.
- Performance (`-DTL_DEBUG_CPU`, City Centre): walking 30.6-32.7 % average CPU, running 32.7 %, idle 24 %, pause 9 %; 0-1 missed frames
  per 300 walking frames; map load / boot / pause open miss ~6 frames once (as before).

## Bugs found and fixed

1. **Flyers info panel text was cut off** ("the founta..."): the line "the bus stop, the fountain" is 26 characters, the panel shows about 23.
   Now "the bus stop, fountain". (`src/tl_field_jobs.cpp`)
2. **Hint/message while a menu is open (the Hunger-40 freeze)**: root cause analysis: the clock stops whenever `_conversation.active()`
   is true, and the conversation branch of `field::update` runs before the menu branch, so a conversation that starts while a menu is
   open freezes the world with the menu still on screen. All hint/message paths (`_check_need_hints`, bill reminder, cough, sick intro,
   delivery, mission-complete pages, pending messages) sit behind `_can_pause()` (no menu, no activity), so I could NOT reproduce it on the
   current build: a sweep of the A press over every frame offset around the first decay tick (Hunger exactly 40, diner counter, VaultMart
   kiosk) always ended either with the hint waiting for A (legal) or with the shop menu open and the clock running; after the menu closes
   the hint appears. To make the freeze impossible anyway, `field::update` now closes an open menu when a conversation becomes active
   (it can never sit frozen under a message). (`src/tl_field.cpp`)
3. Tools: `tools/make_save.py --bag cans,bottles[,credit]` (test the machine without walking), `-DTL_DEBUG_POS` state dump,
   `tools/playtest_driver.py` (see header).

## Follow-up fixes (same session)

- Script op `time` (staff_lunch, skip_lunch, skip_pimm) only advances the clock, never rewinds it (`tl_field_script.cpp`).
- HUD clock: clock/money shifted 3 px left, digits and am/pm/weekday now leave a ~2 px gap to the Hunger icon (`tl_field.cpp`).
- The "What's next?" row is hidden for the rest of a talk once it was used (`conversation::_skip_used`); the step flags hide it afterwards.
  (These three items below are therefore resolved: the rewind edge case, the HUD overlap and the lingering row.)

## Not fixed / observations (none blocks the phone test)

- `-DTL_DEBUG_CPU` + a minigame started from the story = black screen for the whole minigame (the normal ROM and the BOT-only / AUTO_TALK builds
  are fine). Debug-only: do not combine them.
- Making a save with the player on a solid cell (e.g. city_centre 47.4/33.9 or 6.2/39.4) traps him: not a game bug, only a test-save caveat.
- `staff_lunch` sets the clock to 14:00 ("Two hours later"); entering the shop after 14:00 on Day 1 (rye delivered, no lunch yet) would rewind to
  14:00. Edge case only. `skip_lunch` ("What's next?") sets 12:00 and has the same property if used after noon.
- The "What's next?" row stays in the talk menu after use (harmless; choosing Bye starts the skip).
- Walking out of the diner/other rooms requires standing on the door mat (down-left from the arrival point); the exit is easy to find but
  the bottom edge of the mat is narrow.
- HUD: the clock text "pm / Tue" touches the Hunger icon (readable, cosmetic).
- Not exercised (code paths only read): gossip delivery on the next day, Pimm gifts, scratch card jackpots, the crates job at Lou's
  (ask Lou "Carry the crates" after taking it at the board), cough messages, clinic "Pay the bill", `skip_lunch` after the rye loaf.
- The headless runner only sees the video; sound does not exist yet.

## Checklist for the owner's phone test (Lemuroid)

1. Title: New Game, type a name (D-pad, A type, START done). Read the intro, wake up, go down the stairs (down-left, the stair foot).
2. Briefing -> STOCK IT! Left/Right walk, A put away, B swap. Try to get rank S and a combo.
3. Wait for 9:00 (or ask Rosa "What's next?"), fetch the rye loaf from the storeroom crate, give it to Mr. Pimm (he sits at the bakery table).
4. Noon lunch, then Victor Vault's visit at 14:00. Check the golden car, the dialogues and the portraits.
5. Evening: objective line shows Eat / Wash / Sleep. Eat at the diner, wash at the fountain, sleep on a fountain-square bench.
6. Next morning: the newspaper scene, Mia in the diner at 7:00 (RETURN & EARN tip), Lou's job (wash up first: Hygiene >= 40), PLATE RUSH at 11:00
   or 17:00 (daily special on the intro card).
7. Free play: notice board (flyers / books / crates), RETURN & EARN machine, collectibles (Collection in the pause menu), kiosk scratch card,
   SELECT = phone (contacts, messages, order food), clinic, park shower ($1), bins, benches.
8. Pause menu: Save game, quit to title, Continue. Sleep in the room only on Day 1 (the room is closed after the firing).
9. Look for: freezes (note what menu/dialogue was open and the in-game time), text that is cut off, objectives that cannot be completed,
   anything that hides the player wrongly (depth), slow-downs.

## Phone test round 1 (owner, Lemuroid) - fixes

1. **Crash opening the Mission log** ("Sprite tiles allocate failed. Tiles count: 8"). Cause: `field::_open_log` closed the pause panel and opened
   the log in the same frame; Butano releases sprite tiles only at the next `core::update`, so the old pause panel (~500 tiles) and the new log
   (~400) coexisted on top of the field's own tiles (up to ~280 at night with pigeons, light pools and pickups). Reproduced headless with a save at the
   fountain square at 22:00 with a bag (`make_save.py ... city_centre 52 40 --minutes 1320 --bag 5,3`, pause -> Mission log). Fix: a
   `bn::core::update()` between closing one pause-family screen and opening the next (log, collection, dialogs, back to the pause screen), see
   `tl_field_pause.cpp`. Measured with the new `-DTL_DEBUG_CPU` tile readout (`stats` prints "sprite tiles peak used / lowest free"): pause screen
   peaks at ~780 of 1024 tiles in the worst case (242 free), log / collection / phone / dialogue with portrait (506) stay below that.
   The log itself already shows only 4 finished-mission rows (scroll, max 24 entries), so no paging was needed.
2. **Run speed** 2.25 -> 2.95 px/frame (`run_speed`, tl_player.cpp). `run_step[]` is the stride length per animation frame (a property of the
   Run cycle, 2.8 m / 12), so planted feet stay planted and the cadence scales with the speed (vertical runs now ~4 cycles/s). Walk unchanged.
3. **NPCs behind counters** (Lou, Mia at the checkout). The objects layer has a single priority; the occluder rule "something taller than the
   sprite overlaps -> stay in front" (the room's back wall) always won for NPCs, so they were drawn completely in front of the counter. Now
   `map_info::player_hidden(..., ignore_taller)` is used for NPCs and when an NPC stands behind a low occluder but a taller one overlaps, the NPC is
   drawn in two parts (`npcs::_set_priority`): the full sprite at priority 3 (legs hidden by the counter) plus a 32x32 upper half (own 16 tiles,
   copied from the ROM frame) at priority 2. Proof 3x: `.../phonefix/lou3.png` (before), `lou3c.png`, `mia1-3x.png` (after); VaultMart Dex
   (`dex1-3x.png`) and the diner waitress Mia are in front of the furniture and unchanged.
4. **"Half of Mia and Rosa at the loading screen"**: the briefing starts with a camera pan to the checkout, but scripts only start after the
   fade-in, so the fade showed the cast cut off at the left screen edge. New script op `pan_now x y` (camera jumps) and
   `field::_early_pan()` (first fade-in frame: if a trigger's script reaches `pan_now` before its first wait/dialogue, the camera is already
   there). Used by `briefing`. Proof: `esheet.png` (12 fade-in frames).
5. **Tree on the path** (no re-render done, scene.py unchanged). Candidates (3x screenshots in `.../phonefix/`):
   - A `treeA-3x.png`: park tree at (21.0, 41.0) stands ON the east end of the dirt path (y 40..42, x 12..22), trunk and solid block the
     path. Proposed: move it to (21.0, 43.6) or drop it (`for (x, y, sc) in (...)` in `city_centre`, park block).
   - B `treeB-3x.png` / `treeB2-3x.png`: park tree (4.0, 45.5, scale 1.05) with the conifer (1.8, 46.4), tree (7.5, 46.0) and planter (6.0, 43.5) crowd
     the path in front of the toilet door: the canopy covers the area left/below the door and hides the player on the grass around (6, 44).
     Proposed: remove (4.0, 45.5) (the conifer and the (7.5, 46.0) tree keep the park dense).
   - C `treeC-3x.png`: street tree (34.7, 20.8) at the avenue corner next to the hydrant: on the sidewalk in a grate, canopy over the zebra
     end, acceptable; no change proposed.
   Any of these means a City Centre re-render (~45 min), to be batched with the next map change.
