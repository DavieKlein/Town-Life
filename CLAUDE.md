# Town Life — project guide for Claude

Game Boy Advance game in C++ using the [Butano](https://github.com/GValiente/butano) engine.
A story-driven isometric adventure/life-sim: mission-based progression, a villain, needs,
friendships, job minigames and perks. Inspired by the *genre* of The Urbz (GBA/DS), but using
**only original characters, names, graphics and music** — never copy anything from The Urbz or
other existing games.

## Important for every session

- The owner **cannot install anything locally** and tests on a Samsung phone in **Lemuroid**.
  The ROM is always built by GitHub Actions; every push to `main` publishes a new release
  `latest` containing `town-life.gba`:
  https://github.com/DavieKlein/Town-Life/releases/tag/latest
  Direct download: https://github.com/DavieKlein/Town-Life/releases/download/latest/town-life.gba
- After every push: check that the "Build ROM" workflow is green and fix errors until it passes.
- In the Claude cloud container you can usually build locally with Docker (start `dockerd &` first):
  `docker run --rm -v "$PWD":/src -w /src devkitpro/devkitarm make -j8`
  (Docker Hub sometimes returns 429 rate limits; retry or rely on CI.)
  Clean up `build/`, `*.gba` and `*.elf` afterwards (they are in `.gitignore`).
- **Language:** all in-game text, names, menus and dialogue are in **English**. This file is in English too.
- Every playable step of the roadmap must leave the game in a playable state.
- **Propose designs first (owner's rule):** before building anything visual (new graphics,
  characters, animals, buildings, UI), show the owner a design proposal (mock-up / preview
  renders, ideally placed in an in-game screenshot) and wait for approval. Only then implement.
  The owner also wants **no new ROM until all pending proposals are approved**: collect
  proposals, get approval, then do one build and release.
- **Test the ROM headlessly before pushing** (see "Headless testing" below): it runs the same mGBA
  core as Lemuroid and saves screenshots, so you can verify maps, movement and transitions.

---

## Game design

### Concept

"Town Life" is a story-driven adventure/life-sim. You start at rock bottom and work your way up.

- **Core theme: poor to riches, with strong character development.** Getting rich is not the goal
  in itself; who you become along the way is. Over time the player gets more and better chances
  to earn money (odd jobs → steady jobs → own business → investing).
- **Second theme: a warm, human city vs. cold automation.** People, craft and community versus
  supercomputers, robots and self-checkouts.

### Villain: Victor Vault

- Boastful billionaire property developer, owner of **VaultTech**, lives and works in a
  **golden tower** in the City Centre. Original character, not based on any real person.
- His plan **"Smart City"**: automate everything with supercomputers, robots and self-checkouts,
  and demolish the poor district **Old Block** to build expensive glass towers.
- The story ends with his downfall.

### Opening (Chapter 1)

1. The player works at **Corner Market**: warm colours, wooden shelves, friendly coworkers,
   regular customers who know you by name.
2. Victor Vault buys the store and **fires everyone on day one**.
3. The store becomes **VaultMart**: white/grey palette, fluorescent light, self-checkouts,
   robot arms, a robotic voice ("Have a nice day. Next customer."). Deliberately cold.
4. The player starts with **$20**, sleeping on a **park bench**. Only the **City Centre** and
   **Old Block** are open.

### Districts and unlocking

Districts start locked and open one by one through story missions. Every lock has an in-world
reason, and the player can see the blocked route (a closed bridge, a VaultTech gate, a guard,
a bus pass you can't afford yet). Once a district is open it stays open.

| # | District | Type | Opens | Example lock |
|---|----------|------|-------|--------------|
| 1 | City Centre + Old Block | — | Start | — |
| 2 | Docks | Grafters | After the opening missions of Chapter 1 | Closed bridge / dock gate |
| 3 | Old Factory | Makers | Chapter 2 | VaultTech fence around the factory |
| 4 | Station Quarter | Techies | Chapter 3 | Bus/train pass you can't afford yet |
| 5 | Sports Park | Ballers | Chapter 3–4 | Guard at the gate, members only |
| 6 | Hilltop | Posh | Chapter 4–5 (last) | Private road with security; closest to Victor Vault's world |

### Warm/cold city

Areas taken over by VaultTech get a **cold grey palette** (and cold music/sounds). Winning
missions turns an area **warm and colourful** again. Track a warm/cold state per area
(e.g. a `bool` or 0–100 "warmth" per area in the save data) and swap palettes accordingly
(Butano palette swaps / `bn::bg_palettes` fades are cheap on GBA).

### The five types (allies against Smart City)

Each type has its own district, career path, minigames and mentor. Once a district is unlocked
the player can work there and eventually reach the top job of every type.

| Type | District | Career path | Minigames |
|------|----------|-------------|-----------|
| Grafters | Docks | Shelf stacker → Forklift driver → Shift lead → Own transport company | Stacking boxes, driving |
| Makers | Old Factory | Street musician → Mural painter → Studio → Own gallery | Rhythm, drawing |
| Techies | Station Quarter | Phone repair → Web shops → App developer → Own startup | Puzzles, code patterns |
| Ballers | Sports Park | Amateur club → Semi-pro → Pro contract → Own club | Penalties, timing, fitness |
| Posh | Hilltop | Waiter → Real estate agent → Investor → Property empire | Bluffing, negotiating |

Mentors (one per type) and other named characters are still to be designed; keep them original.

### Systems

- **Needs:** Hunger, Energy, Hygiene, Fun, Bladder (0–100, 100 = fine). They decay over time and are shown in a HUD.
  Keeping them balanced is rewarded (e.g. better job performance / skill gain when all are high).
- **Skills:** Strength, Creativity, Logic, Charm, Fitness. Required for better jobs; trained by
  working, practicing and reading.
- **Reputation:** 0–5 stars per type. Stars unlock jobs, clothes, places and characters.
  - **Soft rivalries:** reputation is never lost, but reputation with a type is gained at
    **half speed** while you have **higher** reputation with its rival type.
  - Rival pairs:
    - **Grafters ↔ Posh** (workers vs. owners)
    - **Ballers ↔ Techies** (outdoors and muscle vs. screens and brains)
    - **Makers** have no rival: artists get along with everyone. This keeps the middle of the
      game a bit friendlier and makes Makers a natural "bridge" type. (Tunable later.)
  - Maxing every type is possible but takes much longer.
- **Friendship:** per NPC, 0–100. At **70+** an NPC gives you **City Coins**, spent on
  permanent perks (higher pay, slower need decay, faster walking, ...).
- **Housing ladder (owner decision):** room above Corner Market (only briefly, Day 1) → park bench → **a back room / storeroom in a commercial
  building that someone lets you use** (cheap inside: bare walls, mattress, crates, hot plate; story: Ines's laundromat back room, Chapter 2) →
  **studio** → **loft** → **apartment** → **penthouse** (the top step; NOT a house; the player's own **private** home - owner s67; it still sits atop the rebuilt Co-op Hall).
  Each home has a bills-by-post envelope at its entrance and is furnished from the furniture catalog. Plan: docs/story_overview.md.
- **Furniture rule (owner):** all furniture in rooms where you live (also temporarily) must later be buyable in a furniture store
  or online; some furniture in commercial buildings is for sale too. So furniture is never drawn ad hoc: it is a named piece of the
  **furniture catalog** (`tools/furniture.py`, `FURNITURE`: id, display name, placeholder price, category, footprint, interaction kind,
  quality 1-3, `use` point, builder). Scenes call `furniture.place(s, id, x, y, rot)` (rot 0 = back against the -y wall, 90 = west wall,
  180, 270 = east wall; chairs/plants are placed by their centre). `Local` rotates the piece's local drawing; `use_point()` gives the
  interaction point so `tools/interactions.py` derives the interactables from the placement list (`scene.ROOM_FURNITURE`). No shop yet.
  The diner / library chairs, sofa, toilet, sink and pedal bin are catalog entries too, but the existing scenes keep their inline calls
  with identical parameters (switching would change float rounding and force a re-render); use `place()` for all new furniture.
- **Income ladder:** odd jobs → steady job → promotion → own business (passive daily income) →
  investing.
- **Vehicles as rewards:** bike → scooter → car (faster movement around town).
- **Rival character:** one recurring rival who was fired on day one just like you and climbs
  alongside you (original character, to be designed).
- **Mission log** in the pause menu showing the current objective.

### Chapters

Each chapter is a mission chain with NPC objectives, mostly set in one type's district, and
unlocks the next district. Each chapter ends with a big moment.

1. **Survive** — Corner Market, fired, VaultMart, park bench, first odd jobs. Unlocks the Docks.
   Big moment: e.g. first steady job / first night not on the bench.
2. **Get By** — Grafters/Docks and Makers/Old Factory. Big moment: first own place (a lent back room).
3. **Build Up** — Makers/Techies, Station Quarter. Big moment: first employee / first business.
4. **Break Through** — Techies/Ballers, Sports Park, pressure on VaultTech grows.
5. **Legacy** — Hilltop/Posh, confront Victor Vault, his downfall, Old Block saved.

---

## Third-party assets

Only assets with a licence that allows use in a public repository and game. Never use assets ripped
from commercial games (sprite/model rip sites), even as a base. Credit authors in the README.

All packs below are by **Quaternius**, licence **CC0 1.0** (public domain), supplied by the owner in
Google Drive folder "town life art": https://drive.google.com/drive/folders/1dluGjvUV_Rs1_jEeuwdHr3roaKVz6-Il
(list a folder: `https://drive.google.com/embeddedfolderview?id=<folder id>`; download a file:
`https://drive.usercontent.google.com/download?id=<file id>&export=download&confirm=t`; needs
drive.google.com, drive.usercontent.google.com and docs.google.com in the allowed domains).

| Pack | In repo | Use |
|------|---------|-----|
| Ultimate Textured Building Pack (Dec 2019) | `art_source/quaternius_buildings/` (26 FBX "Models with Materials") | buildings via `s.model()` |
| Animated Men + Women Characters (Feb 2019) | `art_source/quaternius_characters/` (8 FBX, rigged: Idle, Walk, Run, Sitting, Clapping, Jump, ...) | player (Male_LongSleeve, own colours) + future NPCs |
| Downtown City MegaKit [Standard, free] | `art_source/quaternius_downtown/` (glTF + .bin of the used models, base-colour textures downscaled to 512 px; normal/ORM maps left out) | City Centre: downtown building, planters, bollards, manholes via `s.kit()` |
| Ultimate Food Pack (Oct 2019) | `art_source/quaternius_food/` (12 FBX: Apple, Bread, Carrot, Lettuce, Orange, Tomato, sauce bottles, jars, soda) + License.txt | supermarket products via `s.prop('food/Name', ...)` |
| Furniture Pack (March 2019) | not yet | furniture to buy/place in homes |
| Ultimate House Interior Pack (June 2020) | `art_source/quaternius_house/` (11 FBX: toilet, sink, mirror, shower, chairs, couch, fridge, lamp, table, bin) + License.txt | interiors via `s.prop('house/Name', ...)`; more models can be copied from Drive when needed |
| Furniture Pack (Oct 2017) | not yet | **no licence file in the folder** — verify before use |
| David OReilly — Everything Library: Animals (Drive folder `EverythingLibrary_Animals_002`, ~240 static models incl. Crow, Gull, Cat, dogs, Rat, Duck, Raccoon) | `art_source/everything_library_animals/city_animals.glb` (GroundedPigeon, Pigeon, GraySquirrel only) + License.txt | **CC BY 4.0 (not CC0) — attribution required, credited in README.** Static models; colours are vertex colours; the GLB is in centimetres and lost the FBX up-axis rotation (blender_critter.py compensates: `UNIT`, `BASE_PITCH`, per-model `YAW`). |

**Owner's own packs (made by the owner, free to use):** Drive folders `commercial_part_1..3` and
`house_part_1..2`. These are pre-rendered 2D isometric building sprites, one building per lot
(e.g. `1x1_commercial_26_florist`, ...).
- Lots come in sizes 8..128 px, with sun/studio/flat lighting and palette variants (24bit,
  16bit, voyager, dither).
- Each sheet has 8 columns x 4 rows. Column 5 is the 2:1 isometric view; the 4 rows are the 4
  sides.
- `heightmap/` and `normals/` folders exist in the commercial packs; they could give per-pixel
  depth: `x + y = 2 * (image_y + z_px - origin_y)`.
- Scale issue: at 128 px a lot is only 4 cells, so houses look doll-sized next to the 46 px
  player. 256 px exports would match. Waiting for the owner's choice.

**Do NOT use the Drive folder "Homemade inspired by URBZ".** Its files are ripped sprites from
The Urbz / The Sims Bustin' Out: the images carry "Ripped by SuperFlorian12" (The Spriters
Resource) and use the original character and object names. They are not usable as assets or as a
base, and must not be copied.

The SBS packs (Screaming Brain Studios: iso floor tiles, wall textures) still need a licence check.

Formats in Drive: FBX/OBJ/Blend per model (MegaKit: FBX + glTF). Blender needs `python3-numpy`
for the FBX importer. Quaternius FBX materials import with alpha 0 — the render scripts set it to 1.

## Visual style

**Pre-rendered 3D in isometric 2:1, like the GBA life-sims of that era**: scenes are modelled as
simple 3D geometry in Blender, rendered with sunlight, soft shadows and real materials, and then
converted to GBA tiles. Zoomed in: the player is ~46 px tall (1 map cell = 0.75 m). HUD bar at the
bottom (clock + money panel, need icons with green/red bars). Own designs only — never copy
graphics from existing games. **Lived-in, gritty city mood** (owner feedback): worn
surfaces (cracked asphalt and slabs, weeds in joints, dirt patches), white curb lines, dark
outlines on every object, darker corners, slightly saturated colours with cool shadows, and lots
of small street details (bins, newspaper boxes, parking meters, curved lamps, fences, posters,
ivy, weeds). Budget: free tools only; the owner might spend at most ~€50 later
(e.g. a character asset pack) if the scripted 3D characters are not good enough.

## Current state of the code

**Full City Centre (awaiting owner feedback)** with **five enterable buildings and their interiors**
(Corner Market, diner, community centre / library, VaultTech lobby, park public toilet), shops and
fixtures you can use, the shopkeeper Mia, fine collision, a 3D-rendered player and the HUD. History: top-down maps at commit `5af63a1`; hand-painted isometric prototype at
`786cc4c`; pre-rendered street corner at `99203ab`.

- City Centre (72x60 cells = 54x45 m, image 2144x1272 px): main avenue along x (y 22..30) and a
  cross street along y (x 26..34) with curbs, lane markings, zebra crossings and manholes.
  North-west: downtown apartment building (MegaKit). North-east: Corner Market (door → interior; two
  storeys with flower boxes, slate roof and chimney, produce crates, bay trees and a chalkboard sign),
  purple slim house (Quaternius) and Victor Vault's golden **VaultTech tower** (34 m, gold fins,
  "VAULTTECH" sign) on a gold-checkered plaza with planters and bollards. South-west: **City Park**
  (grass, paths, trees, benches — the bench where the player will sleep — pond). South-east:
  fountain square with benches, trees and lamps. Bus stop on the avenue. North end of the cross
  street: road works barrier + cones (future Station Quarter). South: riverside walk with railing,
  river, and the **closed bridge to the Docks** (barrier with a CLOSED sign + cones). The east end
  of the avenue is where Old Block will connect (not built yet).
- Corner Market interior (12x9 cells), a small supermarket: open shelving (`gondola()`) with
  yellow price strips and groceries (`product()`: milk cartons with a printed band, cereal boxes,
  cans with labels, bottles, jars — sizes exaggerated so they read at GBA resolution), fruit &
  vegetable crates with a "FRESH FRUIT" sign, lit "DAIRY" fridge with milk and bottles, checkout
  with conveyor belt and register, basket stack, plant, door mat (exit).
- Player: rigged CC0 character (Quaternius Male_LongSleeve in our own colours: blue sweater,
  khaki trousers, brown hair), idle + 8-frame walk in 8 facings, with a blended shadow.
- HUD bar with a working clock (1 real second = 1 game minute, starts 8:00 am) and money ($20): bold 11 px digits,
  gold money (see "UI style system").
  Needs (`tl_needs.h`: Hunger, Energy, Hygiene, Fun, Bladder, 0-100) decay per game minute and drive the
  five HUD bars (`need_bar` sprites, 16 fill levels, green/orange/red). HUD layout (`hud_sprites.py
  build_hud`): clock/money panel x 10..60, five slots of 35 px at pitch 37 starting at x 62 (bg coords);
  `tl_field.cpp` places the bar sprites at x = -48 + 37 * need. The Bladder icon is a toilet.
- **Enterable buildings (district 1 milestone):** each has a door warp in `city_centre` and a
  door-mat exit warp in its interior (all interiors are cutaway rooms made with `std_room()` /
  `wall_y` / `wall_x` / stubs in scene.py, not outdoor-lit): Corner Market (door x 43-45, y 17-18;
  17x18 L-shaped shop v2), diner (the purple slim house, door on the left of its facade, neon
  "DINER" sign), community centre (NW downtown building, arched door at x 11.2-12.4, "COMMUNITY
  CENTRE" sign; bookcases, notice board), VaultTech lobby (south door of the golden tower, marble
  and gold, reception desk), public toilet (small brick building in City Park at 1.6..4.6 x
  36.8..39.8, door onto the park path; 6x6 room with one open WC, a sink, paper towels, bin, a bit
  grimy). **Public toilet layout (6x6):** open white WC on the back wall at (2.3, 1.5) (moved left in s65, WC sign above at 1.7..3.0, notice + roll shelf 0.3..1.55) (`toilet_unit`, lid up, nothing in
  front of it), big basin with tap, soap and mirror on the west wall at (0.5, 3.5) (`sink_unit`), the ONLY bin at
  (0.75, 1.0), hand dryer, toilet-roll shelf, "PLEASE KEEP CLEAN" notice, mop + bucket + broom, wet-floor sign and
  a hygiene poster. `home_room()` (shabby first flat, approved) stays in scene.py but is NOT in `SCENES` yet
  (no entrance). The scene list is `SCENES` at the end of scene.py; interior props come from
  `s.prop('house/Name' | 'food/Name', ...)` (Quaternius CC0 FBX in `art_source/quaternius_house|food`,
  sizes in `PROP_DIMS`). All flood-fill checked (every door reachable from the start, every free
  interior cell reachable, every exit target free).
- **Interactions** (`tools/interactions.py` kinds, `include/tl_world.h` `interactable_kind`,
  `tl_field.cpp`): reach 28 units for fixtures. An interactable has an optional **quality** 1..3
  (5th tuple element in interactions.py, `interactable::quality`).
  - **Timed activities with animation** (`field::_begin_activity` + `activity_state`): every action
    lasts ~2.5-6 s, plays an animation (`player::start_action(kind, target, frames)`) and spreads its
    need gains evenly over the frames, so the HUD bars fill gradually. **B interrupts every timed activity**
    (wash, eat, drink, read, bin search; B/D-pad also gets up from the toilet, bench and seats); partial
    gains stay (a cancelled bin search finds nothing but the bin's cooldown is still used). Time runs normally during activities (reading adds 30 game
    minutes).
  - **Food** (market checkout / Mia, diner counter): buying pays and the player eats at once (eat
    animation). Table `market_items` / `diner_items` in tl_field.cpp (price, quality 1-3, Hunger, Energy,
    Fun, Bladder); the meal lasts `100 + 5 * (Hunger + Energy) + 20 * quality` frames (max 360).
    Bread $2 q1 Hunger +15 Energy +3; Apple $1 q1 +6/+1; Ready meal $5 q2 +35/+8; Soda $1 q1 Hunger +4
    Fun +4 Energy +3 Bladder -8; Coffee $2 q2 Energy +15 Fun +5 Bladder -10; Pancakes $4 q2 +25/+8;
    Burger $6 q3 +40/+12. Drinks drain the bladder and speed its decay for 90 game minutes.
  - **Bladder** (5th need, starts 80, -0.1/min, x3 right after drinking). Toilet (`toilet`, quality =
    speed: `toilet_full_frames` 6 s / 4 s / 2.5 s from empty to full; the public park WC is quality 1):
    the player sits on the WC (reuses the `player_rest` sit frames at `toilet y - 14` units) and the
    bladder fills over the sitting time. "You don't need to go right now." when nearly full. At 0 an
    **accident** happens: Hygiene -30, Fun -10, Bladder back to 60, info "Oops... You couldn't hold it."
  - **Reading** (`bookshelf`, quality = Fun gained over the 5 s: 10 / 18 / 30; community centre
    shelves are quality 2, a future luxury library should be 3). Sink = wash hands (Hygiene +15,
    2 s), fountain = Wash face (+35, 2.5 s) or Drink water (Hygiene -6, Energy +3, Bladder -15, 3 s).
    The player slides to the fountain rim / bin first (`player::approach`).
  - **Indoor seats** (`seat` = sit facing +y, `seat_x` = facing +x with the sit sprite mirrored; 4th tuple
    element = extra reach in cells because the player stands beside solid furniture): diner booth benches
    + a chair, community-centre sofa + two reading chairs, VaultTech lobby benches + sofa. One option "Sit down"
    (Fun + small Energy +, like the park bench); D-pad or B stands up where he sat down. Not every chair is a
    seat: only ones that face +y or +x (the sit pose has a single facing).
  - **Trash bins** (`bin`, every `trash_can()` in the City Centre plus the public toilet bin): "Search
    the bin", 3.5 s rummaging, random result (`bn::random` mixed with frame timing): 35 % half a
    sandwich (Hunger +12, Hygiene -12), 20 % $1-3 (Hygiene -5), else "Nothing useful." (Hygiene -5).
    A bin gives something once per 60 game minutes ("Someone already emptied this bin.";
    `_bin_emptied[map * 16 + index]`).
  - Notice board and VaultTech reception show info messages. `tl_menu` shows up to 5 option rows (no scrolling) and
    has `open_info()` (up to 3 text lines). Option arrays handed to `tl_menu` must be
    `static constexpr` (the menu keeps the pointer; a stack array crashed the game).
  - **Clearer objects (owner feedback):** `trash_can()` is the flared green bin with a white band, dark lid and litter
    (street bins and the toilet bin); `sink_unit`, `toilet_unit` in scene.py; library chairs are light oak
    (`#e6b866`), diner chairs bigger (h 1.05) and bright red (`#e04030`).
  - **Bins (owner-approved, s50):** street bins are `street_bin_v2` (`trash_can()` in scene.py: dark-green perforated steel
    drum, galvanised bands, yellow band, domed lid with a dark mouth); indoor bins are `indoor_bin` (small white pedal bin with
    a blue lid; the public toilet has one at (0.75, 1.15)). Interactions unchanged (`bin`).
  - **Public toilet (s50):** `sink_unit` is now the v3 design (white pedestal, chrome mixer tap, round chrome-framed mirror,
    dark bowl inside, built through `SwapFix` because it stands on the west wall). The wet-floor sign stands in the mop corner
    (back-right) so the WC has free floor. The hut is dirtier (dull dirty-tile patches, rust streaks, mould under the ceiling,
    dirt blobs in corners, old stains) and has one small natural puddle near the mop (`puddle` material, overlapping flat
    discs with different heights, **never coplanar**). Floor-layer details must have distinct tops (coplanar faces render black).
  - **Can & bottle deposit "RETURN & EARN" (s50, owner-approved):** `tl_deposit.h/.cpp` (`deposit`), spawn spots in
    `tools/deposit.py` (26 spots, generated into `include/tl_deposit_spots.h` by build_assets), art `tools/pickups.py`
    (6 items x 2 twinkle frames, 16x16, `graphics/pickups.bmp`). The machine (`deposit_machine()` in scene.py, green steel,
    round rubber port, lit sign) stands against the east wall of the park toilet; interactable kind `deposit` at (6.2, 37.9).
    **The park bench next to the hut was removed** (it stood where the machine is); the sleeping bench is the one at
    (15.3, 39.4) (plus the four fountain-square benches).
    Rules: can = 1 credit ($0.50), bottle = 2 credits ($1.00); 2 credits pay $1, the remainder (0/1) stays as credit.
    **Loose pickups in the district never exceed 7 credits ($3.50)**; `deposit::top_up` fills free spots (about 40 % bottles)
    at game start and at 6:00 each day (`field::_tick_minute`). Bag max 10 items. A on a pickup (reach 20 units, the nearest
    object or pickup wins): ~1.2 s bend-down (`search` action, B cancels, partial need change stays), Energy -0.5, Hygiene -1
    (-2 at spots flagged `bush`), toast "Picked up a can. / Bag 5/10"; full bag: "Bag full" info. Machine menu: Return all (N) /
    Check credit / Leave; result text shows the exact value and the new credit. Pickup sprites use bg priority 3 (under the
    objects layer) and the day/night palette transform. A cue over pickups (12 px) and the machine (54 px). Pause screen line
    "Bag N/10   Credit x/2". Save: `deposit_init/cans/bottles/credit/spot[32]` carved out of `spare` (size unchanged, version
    unchanged; a save without `deposit_init` gets a fresh top-up). Numbers: docs/story_chapter1.md section 4.7a.
  - **"A" cue:** `field::_update_cue` draws a bobbing gold bubble (`ui_icons` frame 2, bob 0/1/2/1 px per 8 frames)
    above the nearest interactable in reach (same reach rules as the menu, `field::_find_target`) while walking;
    hidden during menus, activities, pause and fades. Per-kind height offsets (bench 22, seat 26, fountain 36,
    bin/sink/reception 40, shelf/notice board 46, rest 38 px) are in `_update_cue`.
  - **Pick-up animation:** `player_pickup` (64x64, 8 facings x 4 frames: reach down, crouch + grab a can, rise, hold it) from `blender_acts.py` (`pickup_pose`, legs bent + root lowered); used by `field::_pick_up` via `action_kind::pickup` (RETURN & EARN cans/bottles; B cancels). Story: Mia explains the machine after the first night (docs/story_chapter1.md).
- Activity animations: `player_wash` (32x64, 8 facings x 4) and the new 64x64 sheets `player_eat`,
    `player_drink`, `player_read`, `player_search` (8 facings x 4 frames, feet at (32, 54), own
    15-colour palette each, shown as a separate `_act_sprite` while the normal player sprite is
    hidden). They are rendered by `tools/blender_acts.py`: poses are made procedurally on the
    Quaternius Male_LongSleeve rig (the Idle pose bent bone by bone, `Rig.rot`) with small prop meshes
    (bread roll, book with a page flip, water in the hands) placed at the hands; the art cache key
    hashes only blender_acts.py + colours. Wide frames are needed because the bent poses stick out of
    32 px. Keep the front-layer mask (`player::mask_area`) 32 px wide: a wider mask makes the game lag.
- **Feedback round (diner/doors/water/depth):** the diner exterior is bigger (49.2..57.4 x, door cells
  52..54) and its interior is somewhat smaller. Doors are more realistic; the VaultTech entrance is a glass
  double door. Wash animation (sink, fountain "Wash face"): the player approaches the basin (`player::approach`),
  hands in the water, face bent down (`blender_acts.py`). Fountain and park-pond water is calm like the river.
  Depth: the per-pixel depth cell word is now bits 0-11 min depth, 12-15 ceil(max offset / 17), 16-31 block
  (`tl_streamed_bg.cpp`; `mask_slots` 56), so the player is hidden behind the toilet hut and trees only when
  behind them. `-DTL_DEBUG_TELEPORT` (USERCXXFLAGS) enables L/R/SELECT debug teleports using
  `include/tl_debug_points.h` (never in normal builds). Not done: VaultTech door does not slide open.
- **NPCs** (`tools/npcs.py`, `tl_npcs`): static idle sprites per map, rendered by `blender_actor.py`
  mode `idle` (8 facings, 32x64, feet (16, 54)). Mia (Quaternius Female_Casual, ginger hair, teal
  top) stands behind the Corner Market checkout; her priority follows `map_info::player_hidden` so
  the counter covers her legs. The render cache key (`scene_hash`) now hashes the scene content, not
  scene.py, so editing one scene does not re-render the others.
- **Collision** is a fine grid (`SOLID_RES` = 4 sub-cells per cell, `solid_res` in tl_world.h);
  `set_solid` rounds outward to sub-cells.
- Interactions (older notes): `tools/interactions.py` lists interactable objects per map (kind, x, y[, radius]),
  emitted as `map_info::interactables`. A (while walking) opens a menu (`tl_menu`: panel
  top-right, highlight bar, A Choose / B Back) for the nearest object in reach: **park bench** → Sit (Fun +,
  small Energy +; seated pose, 4 frames) or Sleep (side-lying pose, zZz text, clock runs 4x faster,
  Energy +); **fountain** → Wash face (8-facing washing animation, Hygiene +35). D-pad or B gets up.
  Player poses come from `blender_actor.py` mode `actions` (`player_rest.bmp` 64x64: 0-3 sit,
  4 lie; `player_wash.bmp` 32x64, 8 facings x 4; the wash sheet has its own palette).
- Ambient animals (`tl_critters`), rendered from the CC BY Everything Library models by
  `tools/blender_critter.py` (32x32 frames facing right, mirrored for left, feet at (16, 23);
  pigeon: stand, peck, wings up/mid/down — wing beats made by bending the wings; squirrel: sit,
  run A/B, climb — made by tilting the body): pigeon groups (fountain square, avenue, VaultTech plaza) peck,
  hop and turn around; when the player comes within 56 units they fly off over the rooftops and
  land again later once the player is 150+ units away. Squirrels in City Park sit and look around;
  within 60 units they dash to their tree, climb it and vanish into the canopy, then come back
  later. Spawn points live in `tools/critters.py` (NOT in scene.py, so moving animals never
  triggers a map re-render); build_assets renders the frames (cached), writes
  `graphics/pigeon|squirrel.bmp` and the spawn table (`critter_spawn`, `map_info::critters`).
- **Day/night lighting** (`tl_lighting`): the time of day sets a palette transform (saturation,
  multiply, offset; keyframes for night, dawn, day, golden hour and dusk) applied to the map layer
  palettes and the player and animal sprite palettes. It applies only to outdoor maps
  (`map_info::outdoor` = `Scene.sun`).
  - Special palette entries per layer (`layer_data`): window glass (objects entries 13-14) blends to
    warm lit colours at night; lamp glass (15) glows.
  - **Water** is rendered realistically in Blender (`water_material` in blender_render.py: depth
    colour ramp, darker mid-river / lighter near the banks via `ymid`/`yhalf`, bump waves stretched
    along the flow, sky reflection; materials `water` river, `water_pond` murkier green,
    `water_fountain` clear blue; any material name containing "water" becomes ID class 2) and quantized
    like normal pixels (calm, no pattern). Only ~1.2 % of the water pixels (`pick_glints` in
    build_assets.py: bright local maxima, >= 7 px apart, where the local colour is close to the typical
    water colour) are special: floor banks 6-7 entries 12-14 / objects bank 6 entries 10-11 are sun
    glint colours and the LAST water entry (15 / 12) is the surrounding water colour. `tl_lighting.cpp`
    fades every glint entry between its highlight and that base colour with `glint_profile` at
    different phases (they twinkle), under the day/night transform.
  - At night, `light_pool` sprites (64x32, priority 3, semi-transparent) lie under every lamp in
    `Scene.lamps`. Blending is top 0.55 / bottom 1, so it is additive and the player's shadow
    vanishes. By day the blending is 50 % alpha for the shadow.
- **Per-pixel depth (front layer)**: the objects `streamed_bg` owns a second 32x32 map at
  priority 1 that shares its tiles and palettes. Each frame it redraws only the objects pixels
  around the player whose iso depth (x + y of the surface, world units) is greater than the
  player's.
  - Uniform cells copy the main map entry. Mixed cells get a masked tile built into one of
    2x40 extra VRAM slots.
  - Depth comes from the ID pass (`blender_render.py ... id`: emission material encoding the depth
    in R/G and the material class in B, 1 sample, Raw view). `build_depth` writes
    `data/<map>_objects_depth.bin` and `_depthpx.bin`.
  - The player is always priority 2 and the shadow priority 3. Occluders are now only used for
    the critters.
- Start position: on the sidewalk in front of the Corner Market door (cell 44, 19).

### Folder structure

```
.
├── .github/workflows/build.yml  CI: builds ROM in devkitpro/devkitarm, publishes release "latest"
├── butano/                      git submodule: Butano engine (pinned to tag 21.9.0)
├── Makefile                     TARGET=town-life, ROMTITLE=TOWN LIFE; also uses butano/common
│                                (graphics + include) for the 16x16 font of the title
├── src/
│   ├── main.cpp                 init + main loop (creates the field scene)
│   ├── tl_field.cpp             field scene: camera, streamed layers, player, warps with fades, HUD text + clock
│   ├── tl_streamed_bg.cpp       tile-streaming regular BG (see "Engine")
│   ├── tl_player.cpp            player: iso movement, collision, depth priority, animation, shadow
│   ├── tl_critters.cpp          ambient pigeons + squirrels (behaviour, sprites, depth)
│   ├── tl_npcs.cpp              standing NPCs (Mia), tl_menu.cpp pop-up menu, tl_ui.cpp UI toolkit
│   ├── tl_deposit.cpp           can & bottle pickups, bag, credit (RETURN & EARN)
│   ├── tl_save.cpp, tl_title.cpp, tl_pause.cpp, tl_field_pause.cpp   save format, title screen, pause screen
│   └── tl_world_data.cpp        GENERATED: palettes per layer, collision, warps, occluders, map table
├── data/                        GENERATED binary layer data (Butano DATA rule): <map>_<layer>_tiles.bin
│                                (8 words per 4bpp tile) and <map>_<layer>_cells.bin (uint32 per 8x8 cell)
├── include/
│   ├── tl_world.h               map_info / layer_data / warp / occluder / direction + helpers
│   ├── tl_field.h, tl_player.h, tl_streamed_bg.h
│   └── tl_map_id.h              GENERATED: enum map_id
├── graphics/                    GENERATED Butano assets: hud, player (32x64 x 144 frames, 64x64 run sheet), shadow
├── audio/  dmg_audio/           (empty) for music/sound later
├── art_cache/                   (git-ignored) cached Blender renders
├── art_source/
│   ├── quaternius_buildings/    26 CC0 low-poly buildings (FBX) by Quaternius + License.txt
│   ├── quaternius_characters/   8 CC0 rigged, animated characters (FBX) by Quaternius + License.txt
│   ├── quaternius_downtown/     CC0 Downtown City MegaKit models used (glTF) + textures + License.txt
│   └── everything_library_animals/  CC BY 4.0 animal models (pigeon, squirrel) + License.txt
└── tools/
    ├── scene.py                 scene descriptions: 3D primitives + collision + warps + occluders
    ├── blender_render.py        renders a scene layer in Blender (run by build_assets.py)
    ├── blender_actor.py         renders a rigged character (idle + walk, 8 facings; run by build_assets.py)
    ├── build_assets.py          renders, converts to 4bpp tiles, writes generated files
    ├── hud_sprites.py           HUD bar drawing (pixel art)
    ├── critters.py              animal spawn points per map
    ├── npcs.py                  NPC spawn points + looks per map (Mia)
    ├── interactions.py          interactable objects per map
    ├── deposit.py, pickups.py   can & bottle pickup spots + sprite art (RETURN & EARN)
    ├── blender_critter.py       poses + renders the animal models into sprite frames
    └── headless_run.py          headless emulator test runner (screenshots + scripted input)
```

Code conventions: namespace `tl`, files prefixed `tl_`, Butano style (snake_case, `_member`).

### How the build works

1. **Art (only when scenes change, in the Claude container):**
   `apt-get install -y blender python3-numpy` (once per container; numpy is needed by Blender's
   FBX importer), then `python3 tools/build_assets.py`
   (~45 min at full quality (192 spp); `--fast` for quick low-quality tests; `--preview DIR` writes PNGs of the
   converted layers; `--rerender` ignores the cache). Commit the generated files:
   `src/tl_world_data.cpp`, `data/*.bin`, `include/tl_map_id.h`, `graphics/*.bmp|json`.
2. `make` (Butano) converts `graphics/` (+ butano/common fonts) and compiles `src/` into `town-life.gba`.
3. GitHub Actions (`build.yml`): job `build` runs in the `devkitpro/devkitarm` container, checks
   out the submodule, builds and uploads an artifact. Job `release` (only on `main`) deletes the
   old `latest` release/tag and creates a new one with `town-life.gba`. CI never needs Blender.
4. Updating Butano: `cd butano && git fetch --tags && git checkout <tag>`, then commit the
   submodule. Watch out for API changes.

### Art pipeline (tools/)

- **scene.py**: x, y in map cells (floats, 1 cell = 0.75 m = 16 world units), z in metres.
  `s.box(...)`, `s.cyl(...)`, `s.sphere(...)`, `s.wedge(...)` (awning), `s.text(...)` (signs),
  `s.point_light(...)`; each primitive has a material name (see `MATERIALS` in blender_render.py:
  brick/noise/checker procedural materials) and a layer: `floor` (ground, below the player) or
  `objects` (everything that can stand in front of the player). Gameplay: `s.set_solid(...)`,
  `s.occluder(x0, y0, x1, y1, height_m)`, `s.warp(x0, y0, x1, y1, target, tx, ty, facing)` (cells).
  Helpers: `window_left/right`, `door_left/right`, `flat_roof`, `tree`, `lamp_post`, `planter`,
  `bench_along_x`, `hydrant`, `window_left_shop`. Add a scene function to `SCENES`.
  Avoid coplanar overlapping faces (they render black in Cycles).
  `s.model(name, x, y, front, colours)` places a Quaternius building from `art_source/` at a fixed
  realistic scale (2.1 ≈ 3 m per storey): front `left` = facade faces +y (x = left edge, y =
  facade line), `right` = facade faces +x (x = facade line, y = top edge). Footprint, collision and
  occluder are derived from `MODEL_DIMS` (bounding boxes at scale 1). Colour schemes (`SCHEMES` in
  blender_render.py: red, cream, blue, mint, purple, orange, grey) recolour the materials Main,
  Bricks, Light and Dark. The FBX materials import with alpha 0; blender_render fixes that.
  `s.kit(name, x, y, rot, layer)` places a Downtown City MegaKit model (real-world metres, origin
  at the facade, facade facing +y at rot 0); footprint/collision/occluder from `KIT_DIMS`.
  blender_render's `fix_kit_material` drops the kit's vertex-colour wear mask (it showed as red
  smears) and the missing normal/ORM maps, and makes glass a glossy blue.
  City helpers: `corner_market_building(s, x0, facade_y)`, `vaulttech_tower`, `fountain`,
  `barrier(..., closed_sign)`, `cone`, `bus_stop`, `lamp_curved`, `newspaper_box`, `trash_can`,
  `parking_meter`, `fence_wood`, `chain_link`, `poster`, `weeds`, `ivy`. `s.tube(pts, r, mat)` is a
  smooth round tube along points (curved lamp arms). Lamp helpers add their light pool spot to
  `s.lamps`.
  - `s.poly(pts, mat)` is a flat polygon, e.g. a gable end. `s.cyl(..., r2=)` makes a cone.
  - "Lived-in" detail helpers, inspired by the owner's building packs (approved): `flower_box`,
    `potted_plant` (bay / bush / flowers), `conifer`, `shrub`, `flower_bed`, `hedge`,
    `produce_display`, `a_frame_sign`, `street_tree`.
  - Keep door cells and the paths around interactables walkable: `set_solid` rounds to whole
    cells.
  **Style pass** (`stylize()` in blender_render.py, always on) = **"V1 Soft" (owner-approved s71, applied to ALL maps s72; replaces sharp variant C)**:
  Cycles 192 samples, pixel filter 0.5 (`RENDER_SAMPLES`), softer sun (outdoor 9 deg, indoor fill 32 deg), boxes that are furniture-sized
  (`box_bevel()`: z0 >= 0, smallest side >= 0.06 m, longest <= 4 m, height <= 2.6 m) get a 3-segment bevel (radius min(0.07, 0.3 x smallest)), cylinders
  and spheres have 32 segments (`SOFT_SEGS`), and every generated mesh gets smooth shading + a Weighted Normal modifier (`soften_object()`).
  **Speed:** bmesh ops (bevel, cone, uvsphere) must run in a tiny temporary bmesh and be copied over (`_copy_into`); inside the big shared bmesh
  they are quadratic (scene build 8+ min instead of 5 s). Then `sharpen()` amount 0.55 and `grade()` (**s73: saturation 1.28, contrast 1.20, shadow tint 0.15**; was 1.15 / 1.08 / 0.12 and looked washed out; module constants
  `GRADE_SAT/CON/SHADOW` in build_assets.py), both before quantization. **Bench blotches (s73):** the `wood` / `fence_wood` / `cardboard` materials were cloud noise whose
  tiny colour variation quantized into orange diamond blotches; they are flat colours now, and `soften_object` smooths only non-axis-aligned faces (bevel strips, round parts), big planar faces stay flat. **The real cause of the diamond patchwork** was the per-tile bank choice in `convert_layer`: neighbouring tiles of one flat surface flipped between
  banks with slightly different oranges. A bank-smoothing pass (`BANK_SMOOTH` 0.6: a tile only leaves its neighbours' bank if that is clearly worse; checkerboard sweeps) fixed it
  (+1 % unique tiles; the 31x21 'worst window' print is still 651 for the city, the engine shows 31x18 = 558 cells). Note: a full `build_assets.py` run ends with a Blender crash in `build_cast` in this container (maps are written before that). Freestyle outlines are thin and light: objects layer 1.7 px-units (0.85 px final) alpha 0.85 near-black, thin
  lineset 0.8 / 0.8 in the material's darkened colour, floor layer 1.1 / alpha 0.55. (The 31x21 "worst window" printed by build_assets is
  conservative: the engine shows 31x18 = 558 cells, below the 624-slot cache.) **Outline rules for thin parts:** a thick black line swallows rods and legs (the library
  chairs and tables turned black in the first test). `build()` therefore splits primitives per material into thin and normal
  mesh objects (`prim_thin`: box/cyl with the two smaller dimensions < 0.12 m or the smallest < 0.045 m, thin tubes/spheres,
  text) and imported props whose name contains Chair / Table / Stool / Light_ (`THIN_PROPS`). Thin objects go into a second
  lineset: silhouette + border only (no crease), 0.5 px, outline colour = **the material's own colour darkened** (material
  `diffuse_color` = base colour x 0.5, Freestyle "Material" colour modifier). Keep new thin furniture readable by building it
  from separate thin primitives (or add the prop name to `THIN_PROPS`). Check new furniture with
  `python3 tools/proposals/s50/crop_check.py OUTDIR name:scene:x0,y0,x1,y1 ...` (renders crops with the real renderer and
  runs the real quantizer; 4x zoom PNGs). Actors (player, NPCs, animals) keep their own outline style.

  Quick look at a small area: `blender -b --python tools/blender_render.py -- <scene> <layer>
  <out.png> 2 32 "x0,y0,x1,y1"` (crop in image pixels). Tall buildings are simply cut off at the image
  top (the camera never shows more than `origin_y` px above the back corner), like the classic games.
- **blender_render.py**: orthographic camera at 60°/45° with `sensor_fit = HORIZONTAL`;
  `ortho_scale = img_w * cos45 * CELL_M / 16` makes 1 cell = a 32x16 px diamond, exactly the
  engine projection. Floor pass: objects invisible to the camera but casting shadows. Objects pass:
  transparent background. Rendered at 2x and box-downscaled.
- **build_assets.py**: per layer, k-means picks 8 palettes of 15 colours (floor) / 7 (objects), minus reserved special entries (see Day/night lighting);
  each 8x8 tile uses the palette that fits best; tiles are deduplicated incl. flips (tile 0 = empty).
  Prints unique tile counts and the worst 31x21 window. Bank budget: floor 8 + objects 7 + HUD 1 = 16 (full). The ID pass (1x, 1 sample) gives material classes and per-pixel depth; tiles with special pixels may only use banks that reserve those entries.
  Work is done in chunks of tiles so big maps fit in memory. City Centre: ~15.6k floor + ~9.9k
  object tiles (~0.8 MB of tile data), full-quality build ~20 min.
- **blender_actor.py**: imports a rigged Quaternius character FBX, recolours its materials
  (Shirt, Pants, Hair, Skin, Shoes, Socks, Eyes; `PLAYER_COLOURS` in build_assets.py), scales it to
  1.78 m and renders the Idle pose + 8 frames of the Walk action for 8 facings (clockwise screen
  order s, sw, w, nw, n, ne, e, se), 4x supersampled; build_assets adds a 1 px dark outline and
  quantizes to one 15-colour palette. Frame 32x64, feet at (16, 54); sheet = 18 frames per facing (see "Smooth motion").

### Character faces (option B, owner-approved) and the player V2 look

- **Proportions:** head 1.28x and hands 1.38x on every character sprite (`face_kit.apply_proportions()` scales the keyframes of the
  `Head` / `Palm.L/R` bones - the actions key them, so pose-bone scale alone is overwritten); the player also gets broader shoulders
  (`player_pose_tweaks`, Torso scale 1.14, must be re-applied after every `frame_set`). Head props from `cast.py` (z > 1.55 m: caps, hats,
  bun, glasses) are glued to the Head bone so they scale with the head; Rosa's / Victor's glasses are replaced by fitted ones.
- **Blender side** (`tools/face_kit.py`, `tools/face_cfg.py` = per-character iris / brow / lips / hair colours): small 3D features
  (eyes, brows, nose shade, mouth, blush, hair strands) glued to the Head bone, plus anchor empties (eyes, brows, mouth, nose, cheeks,
  crown) projected per frame with the sprite camera and a ray visibility test -> `anchors.json` next to the PNGs
  (`{frame: {anchor: [x, y, visible]}}`). Used by `blender_actor.py` (player idle + walk + sit/lie), `blender_acts.py` (eat, drink, read,
  search, wash, pickup; props set `hide_viewport` too so the visibility test ignores hidden ones) and `blender_cast.py`.
- **Cast:** `build_cast` runs `blender_cast.py` twice per member: `portrait` (unchanged look, portraits are NOT touched until a new portrait
  proposal is approved) and `sprites` (faces). The Valet robot has no face.
- **Pixel pass** (`tools/face_pass.py`, `write_face_sheet` in build_assets.py): sprite sheets use 11 free k-means colours + 3 RESERVED
  entries (12 eye white, 13 mouth, 14 blush) + 15 outline; the reserved colours are never used by normal quantisation. After
  quantisation `paint_face` draws, per frame, from the anchors: eye 1x2 dark + white corner (front / 3/4 views), brow, 1-2 px mouth,
  blush, a nose-shade pixel (3/4) and a hair highlight; only for facings s, sw, se (both eyes) and e, w (profile eye); frames whose eyes
  are not visible (bent over the sink, back views, lying) are left alone; sunglasses pixels are not overpainted.
  New characters need an entry in `face_cfg.FACE`.
- **Player V2 look** (`tools/player_look.py`, done): cream collar / cuffs / zip, belt with gold buckle, chunky red sneakers with white
  soles (the FBX "Eyes" material below knee height is the shoes). `PLAYER_COLOURS` now #2c5fb8 sweater, #a98655 trousers, #4a2a18 hair.
  The cast.py player entry (portrait only) still has the old colours.
- Proposal scripts: `tools/proposals/s54/`.

### The player's room above the Corner Market (s55 variant B2, approved; built s57)

Scene `player_room` (8x7 cells, indoor, `scene.player_room()`, furniture only from the catalog): butter-yellow walls, big street window
with a window seat, bed, bedside lamp, wardrobe, desk + chair, wall shelf with radio, rug, plant, backpack, sneakers. The storeroom stairs
foot in `corner_market` is a warp (x 14.25-16.25, y 3.5-4.0, the foot corridor is only one hitbox high: walk down+right) to the room
(arrive 5.2, 3.0); the stairwell's top steps warp back down to (13.6, 3.75) (must stay OUTSIDE the stair warp rect).
Interactions (kinds `bed`, `desk`, `window`, `wardrobe` + the shelf as `bookshelf` q1; the 4th tuple element is extra reach in cells):
- **bed**: Sleep (lying pose = `player_rest` frame 4 raised 10 px onto the mattress, clock 8x, Energy +1.0/min, wakes at Energy 100 or
  with D-pad/B; after >= 30 min asleep a "Slept well. Save game?" Yes/No dialog uses the pause-menu save flow, `pause_mode::sleep_save`),
  Take a nap (1 h, Energy +20, "You feel refreshed."), Leave; "You're not tired." at Energy >= 90.
- **desk**: Read (bookshelf q1, +30 min) / Check notes (current objective, word-wrapped info). **window**: flavour text by time of day
  (story flags can refine it later). **wardrobe**: "Work shirts, jeans... and a green apron."
Render cache note: `scene_hash` ignores `blender_render.py` lines marked `# s57-materials` and the `furniture` attribute, so adding the
room's materials did not re-render the city.

### Corner Market storeroom stairs (s52, approved)

14-step wooden flight with handrail and PRIVATE plaque along the east wall of the storeroom (x 15.0-16.25, y 4.0 up to 0.9; `stairs_flight`
in scene.py, applied inside `market_v2`; staff table moved to (13.4, 2.4), red poster removed). The flight is solid; the foot (15.0-16.25 x
3.5-4.0) is walkable and is the warp up to the room. The room above is built (see above). After the firing the stairs are behind the staff gate (variant B) inside the `vaultmart` map (see "Minigames, cutscenes and the prologue").

### UI style system (tl_ui, tools/ui_assets.py)

- **Two styles, switched by the game clock** (`ui::set_night(is_night(minutes))`, `is_night` = lamps-on time
  19:40..6:15; indoors too): **Paper** by day (cream panel, dark ink text, red title band, gold highlight bar) and
  **Night** (navy panel, white outlined text, gold title, teal highlight bar with dark text). The title screen is
  always Night. The style is read when a panel/label is built (menus, pause, dialogs) and refreshed every game minute
  for the HUD.
- **Palette:** all panels, bars and text share ONE 16-colour sprite palette (fixed indices, enum in tl_ui.cpp and
  tools/ui_assets.py; `paper_colours` / `night_colours` hold the two colour sets). Text roles (`ui::role`) pick fill and
  outline palette indices when the text is rendered, so no extra palettes are needed (the 16-palette sprite budget
  is tight). `ui_icons` (A button, B button, "A" cue) has its own palette.
- **Fonts:** DejaVu Sans Bold, rasterised by `tools/ui_assets.py` into `src/tl_ui_font_data.cpp` (GENERATED; 9 px
  `ui::font9` for menus, 11 px `ui::font11` for HUD clock/money and "Day N"): 95 glyphs, 16x16 cells, 2 bits per pixel
  (fill + 1 px outline). Licence: `art_source/fonts/LICENSE-DejaVu.txt` (Bitstream Vera/DejaVu, free), credited in the README.
- **Text rendering:** `ui::label::set(font, x, baseline_y, text, role)` composes the string into a RAM line buffer and
  copies it into `bn::sprite_tiles_ptr::allocate()`d tiles: one 32x16 sprite per 32 px of text (not one per letter),
  so a full pause screen needs ~50 sprites. All coordinates are screen pixels, top-left origin. Changing the
  selected row just re-sets its label with `role::selected`.
- **Panels:** `ui::panel::open(x, y, w, h, titled)` assembles `ui_pan_*` pieces (64x32 top/bottom, 64x64 body; the right
  end is the left end flipped; middle pieces fill wider panels). Min size: w >= 112, h >= 36 (49 titled); heights
  between 65 and 71 are bumped to 72. `ui::bar` = rounded highlight bar exactly fitting a 13 px row (caps + mid
  pieces), `ui::hint_row` = A/B icons + "Choose"/"Back"/"OK". Layout metrics follow the approved mock-up
  (`tools/proposals/ui_objects/ui_mock.py`): menu width 120 at (116, 5), title band 17 px, rows pitch 14, hint row 19 px;
  pause panel 232x120 at (4, 4); dialog width 212.
- Sprite z order: text 0, highlight bar 10-11, panel 20-24 (lower = in front).

- **HUD +/- markers (s72, owner request):** a small green "+" / red "-" disc (`ui_icons` frames 5 / 6, built in `tools/ui_assets.py`) bobs above the
  right end of a HUD slot while its need rises / falls because of an action. `needs::add` / `add_social` set `pm_sign` / `pm_timer` (60 frames,
  refreshed by every change, so timed activities show it throughout); `minute_passed` decay uses the private `_add_raw` and never marks.
  `field::_update_pm` (called next to `_update_hud_icons`) shows / hides the 6 `_pm_sprites` (hidden with the HUD). Direct writes to
  `_needs.values` (pause debug, accident reset) do not mark.

### Engine

- **World units**: 1 cell = 16 units; +x goes down-right, +y goes down-left on screen.
  Image (pre-rendered map) coordinates: `image_x = origin_x + x - y`, `image_y = origin_y + (x + y) / 2`.
- **Streamed BGs** (`tl_streamed_bg`): each layer (floor priority 3, objects priority 2) has
  thousands of unique tiles in ROM. A 32x32 hardware map wraps around; only cells inside the
  visible window (31x18 cells = play area above the HUD) are mapped. Tiles live in a reference
  counted VRAM cache of 624 slots (4bpp), looked up through an open-addressing hash table (tile id →
  slot, backward-shift deletion), so a layer may have up to 65535 unique tiles; slots released in a
  frame are recycled the next frame
  (they may still be on screen until the next vblank). The layers are created before the HUD so they
  get charblock-aligned VRAM (tiles allocated without offset). Storage for the caches is in EWRAM.
- **Camera**: top-left corner in image pixels, centred on the player above the 32 px HUD and
  clamped to the map's view bounds. Sprites use screen coordinates (no Butano camera).
- **Depth**: player sprite priority 2 (in front of the objects layer) or 3 (behind it). Each
  occluder = world footprint + screen bbox; the player is behind it when overlapping and not past
  its far edge (`x >= x1 || y >= y1` means in front). One priority for the whole layer, so if the
  player is behind a small object but in front of a taller one overlapping the sprite (bollard in
  front of a tower), the taller one wins and the player stays in front.
- **Collision**: per cell (`solid[]`), hitbox = square of radius 4 units around the feet.
- **Movement** (`tl_player`): sub-pixel position (`bn::fixed`) with smooth acceleration and
  braking. D-pad up/down/left/right walk straight across the screen; diagonals follow the
  isometric streets (up+right = −y, down+right = +x, ...). Speeds are equal on screen (walk 1.25,
  run 2.25 px/frame with B). 8 facings; the walk animation advances per 4 screen pixels moved.
  The GBA has no analog stick, so a joystick is not possible in the game itself.
- **Warps**: trigger rect (feet point), target position + facing. Map change: fade out → free the
  layers → wait one frame (Butano frees VRAM in `core::update`) → create new layers → fade in.

### Headless testing

```
apt-get install -y libretro-mgba          # once per container; Pillow is already installed
docker run --rm -v "$PWD":/src -w /src devkitpro/devkitarm make -j8
python3 tools/headless_run.py town-life.gba "wait 60; shot /tmp/a.png; hold up 30; wait 30; shot /tmp/b.png"
```
Commands: `wait N`, `hold KEYS N` (e.g. `right+b`), `press KEYS`, `shot FILE`. Look at the PNGs.

### Controls (current)

- D-pad: walk (straight on screen; diagonals follow the streets) · hold B: run
- A: interact (menu) · in menus: up/down, A ok, B back · while sitting/sleeping: D-pad or B gets up
- START (while walking): pause menu (freezes the game): day, time, money, the six needs with exact values (Social too),
  objective line, Resume / Mission log / Collection / Save game / Quit to title. B or START resumes. "SICK" and "Owe $N" show there.
- **SELECT (while walking): the phone** (s64): Contacts / Messages / Order food, B or SELECT closes. (`TL_DEBUG_TELEPORT` builds use SELECT
  for teleporting instead: never test the phone with them.)

---

## Dialogue portraits and layouts (s57, owner-approved s55)

- **Painter**: `tools/portraits/` (own parametric 2D painter, no Blender): `pt.py` toolkit, `chars.py` face model + 5 expressions (neutral,
  happy, angry, sad, surprised) + character table `CH`, `parts_<char>.py` (hair, clothes, accessories), `robot.py` (Valet: screen face),
  `portraits.py` (render + ONE shared 15-colour palette per character, cached in `art_cache/portraits_<hash>.pkl`; run alone:
  `python3 tools/portraits/portraits.py OUTDIR [chars]` writes a contact sheet). Characters: player (V2 colours), mia, rosa, dex,
  dex_vault, pimm, lou, victor, robot. New speakers need an entry in `chars.CH` and a `parts_<id>.py`.
- **Assets** (`build_assets.build_portraits`): per character `graphics/pt_<id>_a..d` (128 px as four 64x64 quarters TL TR BL BR) and
  `pq_<id>_a..d` (96 px pieces 64x64 / 32x64 / 64x32 / 32x32), each with 5 frames = expressions; generated table
  `src/tl_portrait_data.cpp` (`portrait_for(speaker)`, header `include/tl_portrait.h`, `expression` enum). The old 64 px Blender portraits
  are gone (`build_cast` only renders sprites; the player is no longer a cast render).
- **Layout 1** (normal talk): panel 240x50 at y 106, the 128 px portrait stands at the bottom left (x -14, y 30) in front of the box,
  gold tag at (118, 96), four text lines (x 116, 104 px wide, baseline 119 + 10 n), small meter at (222, 114), A icon (226, 146).
  **Layout 2** (choices, `dialogue_box::choose`): the last page becomes the question (up to 3 lines), options as highlight rows (x 7, w 122,
  pitch 14), the 96 px NPC portrait mirrored at (142, 60), the tall 76 px meter (`ui_mt_top/mid/bot`, three stacked sprites) at (132, 64);
  the box grows with the content (bottom fixed at 156). System pages and speakers without a portrait (Halloran) keep the 40 px box.
  Expressions swap by `set_tiles(frame)`; sprites: 4 portrait + meter, one portrait palette.
- **Expressions in dialogue**: `SPEAKER:expression| text` in `tools/dialogue_src.txt` (default neutral; `dlg_node::expr`). Pages without one
  use the NPC's mood in greetings (good = happy, grumpy = angry) and the topic result in small-talk answers (liked = happy, disliked = sad /
  angry).

## Story systems (dialogue, missions, cast) - built in session s53

- **Dialogue box** (`tl_dialogue.h/.cpp`, class `dialogue_box`): SUPERSEDED by the layouts in "Dialogue portraits and layouts" above (old text: 40 px box at the
  bottom (covers the HUD while open; HUD text is freed and the need bars hidden), the speaker's 64x64 portrait standing on it at
  the left, gold name tag (`ui_tag` pieces), text typed out (A completes the page, then next; B same), word-wrapped to 3 lines
  (140 px, 196 px for system pages without portrait) and split into pages, blinking A button, choices (2-4) in a panel above the
  box, vertical friendship meter (`ui_meter`, red bottom to green top, gold tick at 70, number + "+6"/"-4" delta) at the right
  edge, animating about 3 frames per point). The clock is frozen during conversations.
- **`conversation`** (same files): plays dialogue nodes (pages, choices, effects) and runs **small talk**: greeting by mood, 3 random
  topics out of 8 (+ Bye; first talk of a day always offers a liked topic), player opener, NPC answer, friendship per
  docs/story_chapter1.md 4.5 (like +6, neutral +2, dislike -4, mood x1.5/x0.5, repeat falloff over 3 days, daily cap +12, +1 for
  the first hello, 3 topics max, 2 dislikes end it), City Coins (3 at 70, then 1 per first talk, every 3rd day). First ever talk plays
  `intro_<npc>` first. `start_message(text)` shows a one-page system message (mission complete).
- **Dialogue data**: source `tools/dialogue_src.txt` (format documented at its top: `node name`, `SPEAKER| text`, `! effects`,
  `? choice -> node | effects`, `goto node`; effects: `friend npc +n`, `money n`, `flag name [v]`, `mission id`, `done id`, `coins n`).
  `tools/story_data.py` (also holds FLAGS, MISSIONS, NPC_INFO likes/mood/start friendship, topics) generates
  `src/tl_story_data.cpp` + `include/tl_story_ids.h` (`dlg::`, `story_flag::`, `mission_id::` constants); run it alone with
  `python3 tools/story_data.py` (build_assets.py calls it too). Name conventions looked up by the game: `greet_<npc>_<good|neutral|grumpy>`,
  `talk_<npc>_<topic>`, `bye_<npc>`, `intro_<npc>`. `mission_count` in tl_story.h must match MISSIONS.
- **Story state** (`tl_story.h/.cpp`, `story()` singleton): player name, 64 flags (u8), friendship[16], small-talk memory, City Coins,
  current mission + finished mask, pending money. Saved in `save_data` (**save version 2**: old saves are ignored), `story_state::fill_save/apply_save`.
- **Missions**: MISSIONS table (code, title, objective, condition talk/map/money/flag/day/time or manual `done` effect, next, reward $).
  Interim sandbox chain P1 Say hello (talk Mia) -> P2 Find the library (enter map) -> P3 talk Pimm -> P4 talk Lou -> P5 have $30 -> "Explore the
  city"; M01-M17 (Chapter 1) are in the table but wait for flags the prologue will set (`START_MISSION` in story_data.py switches the start to M01).
  `field::_handle_story_events` checks the mission after conversations, every game minute and on map entry and shows a system page.
  Pause screen: "Monday, day 1" header, objective from the mission, new option **Mission log** (`log_screen`: current + finished list).
- **Cast NPCs**: looks and PLACEMENTS in `tools/cast.py` (Mia, Rosa, Dex, Dex VaultMart, Pimm, Lou, Victor, Valet + player portrait), rendered by
  `tools/blender_cast.py` via `build_assets.build_cast` into `graphics/npc_<id>.bmp` (8 facings 32x64); portraits now come from tools/portraits (old: `portrait_<id>.bmp` 64x64, 15
  colours), plus generated `include/tl_cast_data.h` (npc_id enum, `npc_placements` by map/day/time). Placed now: Mia (market checkout Day 1
  7:00-14:30; diner 7-15 from Day 2; fountain bench 12:00-12:30), Lou (diner 6-22), Pimm (library 10-15:30, park pond 16-18). Rosa/Dex/Victor/Valet
  only in later story scenes. `tl_npcs` rebuilds the present set each game minute, NPCs block the player (`player::set_blockers`), are lit like
  the player outdoors, turn towards you. Talk with A (reach 36 units; the shop menus at the market/diner counter get a "Talk to X" option).
- **Name entry** (`tl_name_entry.cpp`): New Game -> on-screen keyboard (D-pad, A type, B delete, START done, SELECT/L/R case), max 10, default "Sam",
  confirm dialog, `{NAME}` in dialogue.
- **Weekdays**: Day 1 = Monday. HUD shows "am/pm" and "Mon" stacked next to the clock; pause "Monday, day 1" (`weekday_name/short`).
- **Tools**: `tools/make_save.py` writes version-2 saves for headless tests (`--mission --friend --flag --done --day --minutes ...`);
  debug CPU readout: build with `make USERCXXFLAGS="-DTL_DEBUG_CPU"` (top label "cpu % miss N"). Typing a page costs a few missed frames, idle is ~70 %.
- Roadmap 1.3 / 1.4: dialogue, NPC talking, friendship meter, mission data, flags, mission log are done; still to do: NPC wandering, gifts, barks,
  prologue scenes, the Chapter 1 mission scripts, Old Block NPCs.

- **s60 fixes:** Lou stands behind the diner counter at (6.4, 2.6) (counter covers his legs; "Talk to Big Lou" still in the counter menu).
  Sinks have "Wash hands" / "Drink water" (Energy +3, Bladder -15, no hygiene loss). Pimm: library 8:00-16:00 at (4.9, 7.4), park pond
  16:00-19:30; P3 objective names the library. Talk menu has a persistent story row (`conversation::_story_node`, now Lou's
  "Ask about work" -> node `ask_lou_work`, sets `asked_lou_job`, shown until asked; with it only 2 small-talk topics). After editing
  `cast.py` placements without Blender runs: `cd tools; python3 -c "import build_assets as b; b.write_cast_header()"`.

## Minigames, cutscenes and the prologue (s61-s62)

- **Minigames** (`tl_minigame.h/.cpp`, art `tools/minigame_art.py`): each is its own scene with a blocking loop. `main.cpp` destroys the `field`
  (frees sprite VRAM), runs `run_minigame(request)`, applies the result to a `save_data` snapshot (`apply_minigame_result` in
  tl_field_script.cpp: money, natural need decay + job costs, clock, story flags) and rebuilds the field from it. Backgrounds are 8bpp
  256x256 `regular_bg` (240x160 art, `create_bg(8, 48)`, palette entry 0 unused), moving parts are small sprite sheets (`mg_*`).
  - **STOCK IT!** (Rosa): 3 sections MILK/CANS/CEREAL, belt shows the next 4 items, Left/Right snap, A put away, B swap (-2 s), 45 s, combo
    x2/x3/x4 at 3/6/10, wrong shelf = bounce + X + combo reset + -2 s + Rosa hint, full section +50 and refill, rank C/B/A/S (<400 / 400 /
    700 / 1000 or no mistake with 12+ items) = $18/19/20/22; the pay is handed over at the firing (flag value `stock_rank`, op `money_rank`).
    `minigame_request::replay` = replay job stub (3 rounds, $4-7 per round; the 4th "fruit" section is not built).
  - **PLATE RUSH** (Lou): 8 rushes (4-6 plates), SCRUB (A) / RINSE (B) / STACK (Up) inside the [ ] brackets (PERFECT in the centre), greasy pans
    (from rush 3) = mash A x5, a missed step breaks the plate, 3 broken plates end the shift (wage still paid), wage $16 + tip $0-3 by PERFECT
    share minus $1 per break, +10 % wage if all needs >= 60 / -25 % if a need <= 15, free staff meal (Hunger +30, Energy +5, Fun +3).
    Lunch 11:00-15:00, dinner 17:00-21:00 (`tempo_percent` 130, more pans); one shift per day (`diner_shift_day`), started from the diner counter
    ("Work a shift") or right after Lou's job talk. Fragile glasses (B only, after day 3) are not built.
  - Debug (all via USERCXXFLAGS, `BUILD=build_dbg` keeps the normal build dir clean): `-DTL_DEBUG_MINIGAME=1|2 -DTL_DEBUG_BOT=1..3` runs a minigame straight away with a bot; `-DTL_DEBUG_AUTO_TALK` auto-advances dialogue pages (and picks "Ask about work"); `-DTL_DEBUG_BOT=n` alone makes minigames started
    from the story play by bot (headless tests). VRAM is tight: keep choice questions short (<= 2 lines) and at most ~3 NPC sprites on screen
    during talks (`-DTL_DEBUG_CPU` shows `c`pu, `m`issed frames, `u`sed / `a`vailable sprite tiles).
- **Cutscene scripts**: source `tools/cutscenes_src.txt` (format at the top of `tools/cutscene_data.py`) -> `src/tl_cutscene_data.cpp` +
  `include/tl_cutscene_ids.h` (run by build_assets or alone). Steps: fade/black/flash/card, warp/player_at/walk, spawn/move/swap/despawn actors,
  say (dialogue node), info, flag/mission/money, minigame, letterbox, pan, time/needs/eat, lie_bed/get_up, car_spawn/car_move, jump/ifflag.
  `trigger <script> when <conds>` lines start scripts while the player walks free (checked every frame in `field::update`; a script sets a
  flag that makes its own conditions false, so Continue works anywhere). Runner: `tl_field_script.cpp` (`field::_run_step`), actors in
  `tl_npcs` (`spawn/move_to/despawn`, schedule frozen until `release`), player auto-walk (`player::set_script_input`), letterbox (window),
  camera pan (`_pan_mode`). Cast placements can depend on flags (`cast.py` PLACEMENTS 10th/11th element = flag_on / flag_off).
  Dialogue source supports `if <flag> -> node` / `ifnot <flag> -> node` after a page.
- **Prologue flow** (New Game: intro cards, name entry, start in `player_room` 7:00, $0, needs 70/85/70/60/80 - Bladder 80 instead of the doc's 55 because the room has no bathroom): wake_up -> stairs -> `briefing`
  (Rosa, Mia, Dex) -> STOCK IT! -> `stock_react` -> 9:00 `pimm_arrives` (fetch the rye loaf from the storeroom crate, give it to Pimm, he leaves) ->
  12:00 `staff_lunch` -> 14:00 `vault_day`: the golden car drives in, Valet + Victor enter, the firing, Rosa's pay, Vault/Valet/Dex leave and drive
  off, Mia's goodbye ($ coffee voucher), "Four hours later..." -> evening (checklist objective Eat/Wash/Sleep, one-time need hints, bench sleep
  rules: +0.3 Energy/min, wake at Energy 100 or 7:30 but not before 4 h) -> `news_day2` -> Mia's RETURN & EARN tip in the diner -> Lou's job
  ("Ask about work", needs Hygiene >= 40) -> PLATE RUSH shifts. The chain stops at mission X1 "Explore the city (Old Block coming soon)".
- **VaultMart** (s62 variant A, real map `vaultmart`, scene.py `vaultmart()`): after the firing flag `vault_scene` the Corner Market door warps to
  `vaultmart` (redirect in `field::update`). Regimented shelf rows, kiosk bank (the three kiosks are `shop_market` interactables: robot voice
  "Welcome to VaultMart. Have a nice day. Next customer.", prices Bread $3, Apple $2, Ready meal $7, Soda $2, Nutrient loaf $2), restock arm,
  cold palette, storeroom stairs behind the staff gate B (interactable `gate`: "STAFF ONLY. VaultMart property."); the warm room upstairs is
  unreachable. Dex in the grey blazer stands in the aisle (placement). `vaultmart_swap` script op = white flash + flag.
- **Golden car** (s62, compact 0.75x): `tools/blender_car.py` + `tools/car_sprites.py` (renders), `tools/car_sprites_build.py` cuts
  `tools/proposals/s62/car75/*` into 32x32 sprite pieces (`graphics/car_se|nw.bmp`, `include/tl_car_data.h`, 12 pieces / 192 tiles per facing),
  blended shadow blobs; bg priority 3 so the kerb lamp post stays in front. Script ops `car_spawn x y se|nw`, `car_move x y frames mode`.
  SW/NE facings are not built (the car only drives along the avenue).
- Hooks `CAR_ARRIVAL` (`hook car_arrival`, unused fade) and `VAULTMART_SWAP` are now real (see above).

## Feature backlog and s63 systems (gifts, gossip, wandering, scratch cards, Social)

Owner-approved feature list with district-1 / later status: **docs/features_backlog.md** (Social need, showers, sickness + doctor +
bills by post, clothing, wandering NPCs, pets later, gifts, phone, gossip, furniture store/online, collectibles, scratch cards, weather,
events). Visual parts (HUD with 6 needs, phone UI, collectibles, shower, doctor's practice) are PROPOSALS only (mock-ups in
/tmp/claude-0/s63/proposals.png; no art built, no ROM release until the owner approves). Built in s63 (code/text only):
- **Social** (`needs::social`, not a HUD bar; `social_valid/social` in `save_data`, carved from the spare bytes; pause screen 6th line).
  Small talk +3/+5/+1, hello +2, gifts +5/+8 (`story().add_social`, applied in `field::_end_conversation`); < 20: Fun gains halved.
- **Gifts**: `GIFTS`/`NPC_INFO[..][4]` in tools/story_data.py (F +10, L +4, N +1, D -3, once per NPC per day), inventory in `story_state`
  (`item_count/add_item/take_item`, saved in `save_data::items/gift_day`), "Gifts" row in the market/diner shop menu (`field::_open_gift_shop`;
  `menu::max_options` is now 6), "Give a gift" row in the small-talk menu (`conversation::_open_gift_menu/_give_gift`).
- **Gossip**: `GOSSIP` rules (8) in story_data.py, pages `gossip_*` in dialogue_src.txt; noted in `_begin_answer` / `_give_gift`, told one day
  later after the greeting (`conversation::_try_gossip`), state in `save_data::gossip`.
- **Wandering**: `cast.ROUTES` + 12th element of a PLACEMENTS row -> `npc_routes`; `npcs::wander` (idle frames, 1 px bob; no walk frames yet).
- **Scratch cards**: interactable kind `kiosk` (tools/interactions.py, newspaper boxes at the bus stop): $1, 70/20/8/2 % (nothing/$2/$5/$20),
  max 3 per day (`save_data::scratch_*`); the kiosk also sells newspapers (gift).
- Test helpers: `tools/make_save.py --items --social --gossip`; debug flag `-DTL_DEBUG_AUTO_GIFT` (auto-picks "Give a gift" like AUTO_TALK).

## s64: HUD with Social, phone, collectibles, shower, City Clinic (branch `claude/intelligent-hawking-y0vl2t`, NOT on main until the owner approves the art)

Details and numbers: **docs/features_backlog.md "Built in s64"**. Pointers for the code:
- **HUD variant A**: `hud_sprites.build_hud` (28 px slots, pitch 30 from bg x 62, bar sprites `hud_bar` centred at x = -46 + 30 * slot in
  `tl_field.cpp`; slot 5 = Social). Top-right icons (`ui_icons` frames 3 = envelope, 4 = sick face) from `field::_update_hud_icons`.
- **Phone**: `tl_phone.h/.cpp` (`phone`, data `phone_foods`, messages, contacts), opened with SELECT in `field::update`, glue in
  `tl_field_health.cpp` (`_open_phone`, `_update_phone`, `_try_delivery`). Saved: `msg_seen/read`, `call_day`, `delivery_item/due`.
- **Collectibles**: `tl_collect.h/.cpp`, spots / set texts in `tools/collectibles.py` (-> `include/tl_collect_spots.h`), 3D props in
  `tools/blender_props.py` (cache `art_cache/props_*`, `build_assets.build_collectibles`), `collection_screen` in `tl_pause.cpp`.
  `_find_pickup` returns 100 + index for a collectible (cue, A and the bend-down animation reuse the deposit code paths).
- **Shower**: scene.py `shower_cubicle` (in `public_toilet`), interactable `shower`, `player_shower` sheet (`blender_acts.shower_pose`).
- **City Clinic**: scene.py `clinic_building` (exterior, called from `city_centre`) + `clinic()` (interior, map `clinic`, appended to SCENES so
  map ids stay stable), interactables `clinic` / `couch`, Dr. Okafor = cast id `okafor` (IDS index 6: small-talk slots are 8), portrait
  `portraits/parts_okafor.py`, dialogue nodes `*_okafor`, `faint_*`, `checkup_*`, `sick_intro` in dialogue_src.txt.
- **Sickness / faint / debt** (`tl_field_health.cpp`): `_update_health_minute` (zero counters, red counter, sick drain), cutscene `faint`
  (cutscenes_src.txt, op `clinic_care`), `_clinic_choice`, `_check_bill_reminder`. Constants at the top of that file.
- **Save version 3** (old saves are ignored): new fields at the end of `save_data` (collect, sick, zero_min, debt, phone). `tools/make_save.py`
  has `--collect --sick --zero --red --debt --msg-seen --msg-read --delivery-item --delivery-due`.
- **Owner decisions pending**: approve the clinic (exterior + interior), the shower, the collectible props, the doctor's portrait and the
  HUD before this branch goes to main. Bills by post (envelope at the home entrance) wait for the housing ladder.

## Movement feel and performance pass (s71, branch `claude/intelligent-hawking-y0vl2t`)

- **Measuring:** a `-DTL_DEBUG_CPU` build keeps stats in EWRAM; `python3 tools/headless_run.py ROM "...; stats LABEL"` prints frames, missed
  frames, >85 % frames and average CPU since the last `stats` (a label containing `hist` also dumps the per-frame CPU %).
- **Dropped frames fixed:** `streamed_bg::set_view` scanned both 31x18 windows (~1100 cells) on every 8 px camera step; it now walks only the
  strips that changed. `update_front` (per-pixel depth mask) is skipped when player area, depth and window are unchanged. Walking/running
  average CPU 33-42 % -> 20-34 %, missed frames per ~500 walking frames 4-10 -> 0-3 (boot / map load still misses ~6, pause open ~6, collection open ~11, once).
- **Player:** acceleration 0.38 (was 0.25) with a first-frame kick (45 % of target speed), braking 0.45; a changed d-pad direction must hold 2 frames
  (1 from standstill) so two keys pressed/released a frame apart no longer flicker through an in-between facing; (old stride notes superseded by "Smooth motion" below).
- **Camera:** OFF since s74 (owner: the moving camera was distracting; `camera_lead = false` in `field::_update_camera`, camera stays centred). Was: smooth lead (`field::_update_camera`): an eased offset (`_lead_x/_y`, 7 % per frame, 9 px per px/frame of speed, max 22 x 12 px) added to the
  player's rounded position, so player and BG stay in whole-pixel lockstep (no wobble); instant snap (lead 0) on map load, off while a script pans.
- **NPC walk cycles:** `tools/blender_cast.py` renders the Walk action (12 frames, see "Smooth motion") for humans (the robot stays idle-only); `build_cast` writes
  13 frames per facing (idle + 12 walk; `frames_per_facing` in tl_npcs.cpp); `tl_npcs` plays them by distance walked (wander and cutscene
  `move_to`). ROM +0.5 MB, no extra VRAM (one frame is resident). Re-render only the cast with `cd tools; python3 -c "import build_assets as b; b.build_cast(False, False)"` (~3 min).

- **Smooth motion (s71, `tools/actor_cycles.py`):** player sheets: `player.bmp` 32x64, 18 frames per facing = 6 idle (slow breathing loop from the Idle
  action, 28 game frames each) + 12 walk; `player_run.bmp` 64x64, 12 run frames per facing (the Run stride is wider than 32 px), shown by a second
  sprite `_run_sprite` only while B is held (the 32x64 sprite is hidden then). Cycles are sampled sub-frame evenly over the Quaternius Walk (25 frames) /
  Run (21 frames) loop starting at the PASSING POSE (`passing_frame`: left foot planted, right foot swinging past), so idle -> walk starts at an almost
  upright pose and walk <-> run keep the same foot phase (`_phase` 0..12 is kept when switching). Frame names `<facing>_<i|w|r><n>`. NPCs: idle + 12 walk
  (same sampling, `<facing>_0`, `<facing>_w<n>`).
  **Planted feet:** the animation advances per screen pixel walked with a per-facing step (`walk_step[]` / `run_step[]` in tl_player.cpp): one Walk cycle moves
  the body 1.36 m, one Run cycle ~2.8 m (stance-foot speed x cycle length, measured on the rig); 1 m is 15.1 px (s/n), 23.9 px (diagonals) or 30.2 px (w/e) on
  screen, so steps differ per facing. Because the d-pad moves equal screen pixels in every direction, cadence is higher for vertical moves (walk s/n
  ~3.6 cycles/s, w/e ~1.8) - a design trade-off (slower vertical speed would even it out). NPCs use 2.42 world units per frame.
  Stopping: the stride finishes up to the nearest passing pose (`settle_speed`), then idle; turning: `_shown_facing` steps through in-between facings
  (1 + 2 game frames each) when the facing changes by more than 45 degrees.
  Re-render player only: `python3 -c "import sys; sys.path.insert(0,'tools'); import build_assets as b; b.build_player(False, False)"` (~1.5 min), cast ~3 min.
  CPU in headless tests (TL_DEBUG_CPU): idle ~26 %, walk ~30 %, run ~29-34 %; no extra missed frames beyond map streaming.

## s71: variety, "Feeling great", control feel (branch `claude/intelligent-hawking-y0vl2t`)

- **PLATE RUSH daily specials** (`apply_plate_special`, `plate_special_name` in tl_minigame.cpp; weekday = (day-1) % 7, shown as a gold line on the start card and in Lou's
  intro line): Mon Quiet (tempo -10 %), Tue Pan (+20 % pans), Wed Rush (tempo +15 %), Thu Tip (+$2 tip), Fri Full House (+1 plate per rush), Sat VIP (+$3 if no plate
  breaks, own result row), Sun Brunch (tempo +10 %, +$1 tip). Fields `special / extra_plates / tip_bonus / vip_bonus` in `minigame_request`.
- **Odd jobs** (notice board in the community centre, `tl_field_jobs.cpp`, menu "Odd jobs", once per day each, state `_odd_day/_odd_mask` saved in `save_data::spare[0..1]`
  (size unchanged), mask bits in the .cpp): Flyers $5 (walk within 26 units of bus stop, fountain square, City Park: toast per spot, objective line shows n/3),
  Sort books $4 (5 s `search` animation at the board), Lou's crates $6 (take it at the board, then Lou's talk menu gets the story row "Carry the crates" ->
  dialogue node `ask_lou_crates`, effect flag `crates_go` (last free story flag, 64/64 used), 7 s `pickup` animation in `_end_conversation`). Flags/state reset at midnight.
- **Feeling great** (`needs::great_enter` 70 / `great_exit` 65 with hysteresis, `field::_update_great`, `story().feeling_great()`): all five bar needs high. Effects: +10 % pay
  (rounded up, `_job_pay` for odd jobs; PLATE RUSH wage judged on the needs at shift start, before the shift decay), +1 friendship on every positive small-talk / gift gain.
  Toast "Feeling great! Pay +10%" (`_toast`, non-modal label at the top, 170 frames, waits while a menu/dialogue/activity is open), "GREAT!" next to the clock on the pause screen.
  The Social need is not part of it. Need decay per game minute (unchanged): Hunger -0.07, Energy -0.05, Hygiene -0.04, Fun -0.06, Bladder -0.1, Social -0.05.
- **Control feel**: standing still while the A cue shows, the player turns to face its target once (`player::standing_still`, `field::_cue_faced`); opening an interaction menu
  also faces the object (not for benches / seats / beds, which set their own pose).
- `tools/make_save.py --odd day,mask` for odd-job tests. Mock-up for need-effect icons in menus (proposal only, not built): see the session scratchpad `icons/`.

## s73 playtest (headless, details: docs/playtest_s73.md)

- The prologue plays from New Game to mission X1 and all systems were exercised headlessly; fixes: flyers info line cut off, an open menu is now
  closed when a conversation starts (no message can freeze the world over a menu). The Hunger-40 freeze could not be reproduced on this build.
- **Playtest tools:** `tools/playtest_driver.py` (scripted play: `goto X Y`, `state`, savestates, shots; needs a ROM built with
  `-DTL_DEBUG_POS`, which makes `field::update` write a state dump found by the magic "TLDB"), `tools/make_save.py --bag`. Build recipe for
  fast story runs: `-DTL_DEBUG_AUTO_TALK -DTL_DEBUG_BOT=1 -DTL_DEBUG_POS` (dialogue + minigames by themselves). **Never combine
  `-DTL_DEBUG_CPU` with story runs that reach a minigame** (black screen); use a separate build for `stats`.

## Roadmap / status

**Development is district by district.** We finish one district (map, systems, story, polish)
until the owner is happy with it, and only then move on to the next one. Every step below must
produce a playable ROM so the owner can test it on the phone. Systems (needs, dialogue,
missions, save) are built the first time a district needs them and reused afterwards.
Update the checkboxes at the end of each session.

### 0. Foundation — DONE
- [x] Butano project (submodule at 21.9.0), Makefile, `.gitignore`
- [x] GitHub Actions: build in devkitarm container + release `latest` with `town-life.gba`
- [x] Placeholder town tilemap 512x512 (roads, sidewalks, 8 houses, park with fountain and pond)
- [x] Player with d-pad, 4-direction walk animation, collision, following camera, run with B
- [x] Design document (this file) with full game design

### District 1: City Centre + Old Block (Chapter 1: Survive) — IN PROGRESS

1.1 Real map — IN PROGRESS (pre-rendered isometric)
- [x] Top-down City Centre + Old Block + Corner Market interior (commit `5af63a1`, superseded)
- [x] Hand-painted isometric prototype (commit `786cc4c`, superseded)
- [x] Blender pipeline: scenes in Python → Cycles renders → 4bpp multi-palette tiles
- [x] Tile-streaming engine (big pre-rendered maps), depth via occluders, warps with fades
- [x] Prototype: street corner with Corner Market + interior, 3D-rendered player with shadow, HUD
- [x] Supermarket interior, smooth 8-direction movement, CC0 Quaternius buildings + animated player
- [x] Downtown City MegaKit used in City Centre (building, planters, bollards, manholes)
- [x] Full City Centre: VaultTech golden tower, park with benches, fountain square, river with the
      closed bridge to the Docks, road works to the north, bus stop
- [x] Food pack in the supermarket (food props on the shelves and in the crates)
- [x] House Interior pack used in the interiors; [ ] shabby first home (`home_room`, no entrance yet) and buyable furniture
- [x] Enterable City Centre buildings: Corner Market, diner, community centre, VaultTech lobby, park public toilet
- [ ] Owner approves the look (feedback round)
- [ ] Full Old Block: row houses, garden, laundromat, bakery, court, demolition site
- [ ] Map transitions between City Centre and Old Block

1.2 Needs + HUD + clock — IN PROGRESS
- [x] `needs` struct: Hunger, Energy, Hygiene, Fun, Bladder (0–100), decaying over time; timed activities with animations, gradual bars
- [x] HUD: 4 small bars/icons (sprites or a high-priority second bg layer)
- [x] Game clock with day counter (+1 at midnight); START opens a pause menu with exact values
- [x] Interact with objects (A + option menu): park bench = sit/sleep, fountain = wash
- [x] Interactions in the interiors: shops (market, diner), toilet, sink, bookshelf, notice board, reception
- [x] Eating / drinking / reading / bin searching / toilet with animations and quality levels; trash bins; fountain drink; Bladder need + accident
- [ ] More interactions with furniture (shower, fridge, cooking, repairing) once homes exist
- [x] Text: software-rendered bold pixel fonts (`tl_ui`, see "UI style system"); the title uses `bn::sprite_text_generator`
      with the 16x16 common font
- [ ] Split `main.cpp` into scenes (`tl_scene.h` with an enum, one class per scene with `update()`)

1.3 Dialogue + NPCs — IN PROGRESS
- [x] Static NPC sprites (`tl_npcs`, Mia at the checkout)
- [ ] NPC class (simple wander pattern, collision with player, talking)
- [x] Dialogue box at the bottom with text paging (A = next) and simple choices (+ friendship meter, small talk)
- [x] Dialogue data in a compact table format (tools/dialogue_src.txt)
- [ ] Original NPCs: Corner Market coworkers, regular customers, Old Block residents

1.4 Missions + mission log — IN PROGRESS
- [x] Mission data: id, objective text, conditions (talk to X, go to Y, earn $Z), rewards
- [x] Story flags + current chapter/mission state
- [x] Mission log in the pause menu showing the current objective
- [ ] District lock system driven by flags (the Docks blocker)

1.5 Chapter 1 story — TODO
- [x] Working at Corner Market (warm palette): briefing, STOCK IT! shift, Mr. Pimm's rye loaf, staff lunch
- [x] Cutscene: Victor Vault buys the store and fires everyone (golden car, Valet, expressions)
- [x] VaultMart transformation (own cold map, self-checkout kiosks, robot voice, staff gate)
- [x] Start state: $0 -> last pay $18-22, park bench as home; evening survival checklist
- [x] PLATE RUSH diner job (daily shifts); [ ] odd jobs (notice board), Old Block missions M08+
- [ ] Introduce the rival character
- [ ] Chapter end: unlock the Docks

1.6 Save/load — IN PROGRESS (moved forward: needed to play a whole district on the phone)
- [x] Versioned save struct with `bn::sram::write/read` (`tl_save.h/.cpp`), manual saving only (owner: no autosave)
- [x] Title screen: Continue (only with a valid save) / New Game (`tl_title.cpp`)
- [x] Pause menu (`tl_pause.cpp`, `tl_field_pause.cpp`)
- [x] Headless: save, reset, Continue restores map/position/time (mGBA reports 32 KB SRAM)
- [ ] Verify SRAM saves work in Lemuroid on the phone

Save/pause notes (s64: save version 3, new fields appended): `save_data` (tl_save.h) is one packed struct at SRAM offset 0 (732 bytes before s64): magic "TLSV", version,
size, Fletcher checksum over everything after the header; map, facing, x, y, day, minutes, minute frames,
total minutes, money, the five needs (bn::fixed raw), bladder boost, bin cooldowns (8 maps x 16 bins), plus
reserved fields: player name char[12], story flags u8[64], mission id, friendship u8[16], 64 spare bytes. A save
with a wrong magic/version/size/checksum is ignored (title shows only New Game). Changing the layout means
bumping `save_version`. `field::_fill_save/_apply_save` map the field state to and from it; new state that must
survive needs a field in the struct. Pause screen: `pause_screen` and `dialog` (title + up to 3 lines + Yes/No) in tl_pause.cpp (built on `ui::panel`); `field::set_objective(text)` sets the objective
line for a future mission system. The pause screen frees the HUD text sprites while open (128-sprite budget; with line-wise text sprites it uses
about 50).
"Quit to title" uses `bn::core::reset()`. `tools/headless_run.py` has `dumpsram`, `loadsram`, `clearsram`
and `reset` commands for save tests.

1.7 Polish — TODO
- [x] Day/night lighting, lamp light pools, lit windows, water palette cycling, per-pixel depth
- [ ] Better pixel art for this district (original designs), warm/cold palette per area
- [ ] Objects drawn over the player (tree tops, roofs) via a second bg layer
- [ ] Music + sound effects for this district (maxmod, `audio/`)
- [ ] Owner approves the district → move on

### District 2: Docks (Grafters, Chapter 1 end / Chapter 2) — TODO
- [ ] Docks map, mentor NPC, Grafters mission chain
- [ ] Career path (shelf stacker → forklift driver → shift lead → own transport company)
- [ ] Minigames: stacking boxes, driving
- [ ] Skills (Strength, Creativity, Logic, Charm, Fitness) + reputation stars, incl. rival half-speed rule
- [ ] Friendship per NPC + City Coins perks (introduced here)
- [ ] Housing ladder step: lent back room (Chapter 2 big moment) + first shop/furniture
- [ ] Polish + owner approval

### District 3: Old Factory (Makers, Chapter 2: Get By) — TODO
- [ ] Map, mentor, missions; career path street musician → own gallery
- [ ] Minigames: rhythm, drawing; first vehicle (bike)
- [ ] Polish + owner approval

### District 4: Station Quarter (Techies, Chapter 3: Build Up) — TODO
- [ ] Map, mentor, missions; career path phone repair → own startup
- [ ] Minigames: puzzles, code patterns; own business with passive daily income
- [ ] Polish + owner approval

### District 5: Sports Park (Ballers, Chapter 3–4: Break Through) — TODO
- [ ] Map, mentor, missions; career path amateur club → own club
- [ ] Minigames: penalties, timing, fitness; scooter
- [ ] Polish + owner approval

### District 6: Hilltop (Posh, Chapter 4–5: Legacy) — TODO
- [ ] Map, mentor, missions; career path waiter → property empire
- [ ] Minigames: bluffing, negotiating; investing; car; apartment, then penthouse (style of the chosen type)
- [ ] Finale: Victor Vault's downfall, Old Block saved
- [ ] Polish + owner approval

## Next session: start here

**Milestone done (owner: "put everything on main; finish the district now, fine-tuning later"):**
five enterable buildings, shops, fixtures, Mia, fine collision, fountain with water in the basin.
**Postponed fine-tuning (do when the owner asks):** water is now realistic with sparse glints (see
Day/night lighting; check it on the phone), fountain detail, eye-level street details (commit `c3aaccc`),
the shabby first home entrance (`home_room`), and a tree in City Park at
(4.0, 45.5) that covers the player on the path in front of the toilet. Next big steps: dialogue
box with portraits + friendship meter, missions, Old Block.

**Eye-level street details proposal (parked, "details later"):** the scene.py and
blender_render.py code is in commit `c3aaccc` (WIP). It adds projecting shop signs, bikes, wall
lamps, a café table, a mailbox, etc. It was reverted from main until the owner wants details.

**Owner decisions (latest):**
- **Story answers (s66, details in docs/story_overview.md):** lent space = Ines's laundromat back room; Co-op Hall + penthouse as planned; Co-op Charter of 1931 as
  the legal key; Victor = Rosa's fired delivery boy "Vic" (fate: stocking shelves at Corner Market); Valet turns good at the Gala; odd job "The Tester" stays;
  mentors Bo-Ra, Wren, Nadia, Gus, Odette approved as characters (looks need proposals); soft demolition countdown (Day 86) kept; later raise gossip
  rules to ~48 and phone messages to ~60 (32-bit mask, NOT built yet); Dex's endings: three endings (redeemed / grey / cold) approved (s67); the penthouse is the player's private home (s67).
- **s68 decisions (details: docs/story_overview.md, docs/story_chapter1.md 3B.2a, docs/progression.md):** (1) Old Block is closed at first by VaultTech's **VaultLink HyperFibre cable works** (barriers, trench, robot TRENCH-E 3, guard Pruitt; really AURUM Trunk 7); the player gets in by a **sneak route** (fence hole + path between bushes, M09), the front opens after M13 (neighbours move the barriers, Teo's door bridge). (2) **No fixed story days:** missions use triggers (flags, missions, shifts, "next morning after X", times of day); only the prologue is Day 1. The demolition countdown starts at Notice #2 (30 days), ticks per day down to a story-stage floor, never ends the game; only the Gala -> Hearing -> Demolition Morning chain takes it to 0. (3) Progression (upgrades/perks/skill gates, secrets incl. the sewer sweet seller Mothball at 00:00, free play after the ending, Status screen): docs/progression.md. (4) Recorded in docs/features_backlog.md, not built: vehicles ladder (kick scooter -> skateboard -> fatbike -> motor scooter -> hoverboard, no indoor riding), owner's needs list (Hunger, Energy with bed icon, Hygiene, Fun, Social, new "Home" need; open question: does Bladder stay?), and the to-do for proper NPC walk cycles. **Needs answer (final):** Hygiene and showering are one need (shower icon); **Bladder stays**; the HUD plans **7 needs**: Hunger, Energy (bed/Zzz icon), Hygiene (shower), Bladder (toilet), Social, Fun, Home; all need icons must be redesigned to be clearer (proposal first).
- **Time machine (s69/s70, docs only, owner request):** "The Late Tram" arc M54a-M54e (Quarter Lab; Forecast, accidental Egypt, Rosa and young Vic 45 years ago) is now **main story**, the final act of Chapter 4 (M54 -> M54a..e -> M55), with a soft Logic gate (Pip's Riddle Door) and required payoffs (Valet's doubt, Clause 9 in M62/M67, Rosa's token in M69). Afterwards **Egypt is always open**: one trip a day (Cells), named residents (Seshi, Hetepet, Khenti, Menkhet, Nebet, Ankhu, Bek and Nofret) with friendship, Sun-star reputation (0-5), **deben rings** as currency (Egypt only, not for dollars) for the Menkhet furniture set, plus a one-time free-play "Sunny Forecast": `docs/story_chapters3-5.md` 4.6, `docs/progression.md` 2.2, `docs/story_overview.md` decisions 15-16. Nothing built; all art NEEDS PROPOSAL.
- **Prologue pacing (s66):** every objective must be completable by doing what it says. After the rye loaf the objective is "Help in the shop until lunch at noon";
  Rosa/Mia get a story row "What's next?" (`ask_skip_pimm` / `ask_skip_lunch`, flags `skip_pimm` / `skip_lunch`) that skips the clock to 9:00 / 12:00 ("Later..." card).
  Outside after noon, `back_for_lunch` tells you to return. `staff_lunch` ends with "Two hours later..." (14:00) and `vault_day` starts at once (trigger needs `lunch_given`).
  Objective strings must be <= 48 characters (bn::string crash otherwise).
- **VaultTech staff gate = variant B** (roll-down shutter with a big red STAFF ONLY sign): built into the `vaultmart` map (s62).
- **VaultMart = variant A, golden car = compact 0.75x (owner, s62):** built (see "Minigames, cutscenes and the prologue"); proposal sources in `tools/proposals/s62/`.
- **Player bed (s58, s59):** `bed_cosy` is soft: bevelled mattress, puffy duvet (hangs 0.07 over the sides), turned-back sheet, ONE round pillow, no
  footboard, no foot blanket. `s.box(..., bevel=r)` now works (blender_render `add_box`, rounded 3 segments, smooth faces; lines marked
  `# s57-materials` keep other scenes' cache). The sleeper uses `player_rest` frame 5 (`bed_0`, on the back, head towards -x, face pass off), lifted
  `bed_lift` 14 px; he lies ON the duvet: the front-layer mask depth is `seat sum + 90` (beyond all bed pixels), so he is drawn fully in front of the bed.
- **Corner Market v2 interior: APPROVED.** It is bigger and L-shaped, with 2-cell aisles, wall
  shelves, 2 gondolas, a freezer, a fridge, crates, a checkout and a storeroom. The proposal
  scene code is in /tmp/claude-0/s36/tools (scratch). Still to add: Mia at the checkout and buying
  food (menu with prices: money down, Hunger up).
- **First home:** must be smaller, cheap/shabby and mostly empty when you move in (mattress, crate,
  tiny fridge, hot plate, small bathroom). Furniture is bought later. A new proposal is pending.
- **Interior proposals APPROVED:** shabby first home, diner, community centre, VaultTech
  lobby (proposal code in /tmp/claude-0/s36/tools; uses the CC0 Quaternius House Interior and
  Food packs, which go to `art_source/quaternius_house/` and `art_source/quaternius_food/`). The
  park building is a small **public toilet** (a few WCs and sinks, no showers); a new proposal is
  pending.
- **Enterable City Centre buildings (all 5 approved as concept):**
  Corner Market, park bathhouse (showers/toilets), diner in the purple house, community centre /
  library with a job notice board (NW building), VaultTech lobby.
- Pending proposals: finer collision (4 sub-cells per cell), water in the fountain basin, and a
  more natural water texture.
- **Dialogue box (superseded by layouts 1/2, see "Dialogue portraits and layouts"):** variant 2. A 40 px box at the bottom with the speaker's 64x64 portrait
  standing on it at the left, overlapping the view. The name tag is gold, there are 3 text lines
  in the 8x8 font and an "A" button. It must also offer **choice options**. Mock-up scripts are in
  /tmp/claude-0/s34 (scratch, may be gone): `portrait.py` renders the head-and-shoulders portrait
  in Blender, 4x, rim light, 15 colours.
- **Relationship meter in conversations (owner request):** during a conversation, show a
  vertical friendship meter for that NPC next to the portrait, with its number. The bar is red at
  the bottom and green at the top.
  - It moves up or down live depending on the player's answers and small talk.
  - Small talk is a choice menu of topics (e.g. weather, work, music, sports, gossip, compliment,
    joke, complain). Each NPC has likes and dislikes and a mood, and repeating a topic gives less.
  - It feeds the existing friendship system (0-100 per NPC; 70+ gives City Coins) and reputation
    with the NPC's type.
  - Use our own layout: dialogue variant 2 plus the meter on the right edge of the box. Do not
    copy any existing game's screen.
- **Player:** variant V2 chosen by the owner (head 1.28x, hands 1.38x, cream collar and cuffs, belt, red
  sneakers with white soles, eyes). Note that the head and palm scales must be set on the Idle/Walk
  keyframes, and the FBX's "Eyes" material is actually the shoes.
- The owner said: don't spend much time on these details now. **Focus on building the world**
  (Old Block, walkable interiors). Details come later.

**Street details across the City Centre (owner approved the before/after proposal):** the
Corner Market got an upper storey and roof, and there are more plants, flowers, trees and hedges
everywhere. The same style is planned for Old Block.

**Graphics upgrade (owner approved everything except cloud shadows, which looked odd):**
day/night lighting, night lamp pools and lit windows, water palette cycling, per-pixel depth
(front layer). Still to do: render-fidelity upgrades with the owner's own packs once they are in
Drive. No Remote Control folder is connected.

**New (owner, latest):** the owner added more packs to the Drive folder in the agreed
**isometric urban** style: commercial and residential buildings plus texture packs. List the
Drive folder first, check each licence, and propose (with preview renders) how to use them
(Old Block row houses, shops, ground textures) before building.

The owner asked for (1) the full City Centre — done, awaiting feedback — and then (2) the
**Ultimate Food Pack** in the Corner Market supermarket (replace the box products in `product()` /
`gondola()` with food models: download from the Drive folder, keep only what is used in
`art_source/quaternius_food/`). After that: Old Block (east end of the avenue) and step 1.2.

## s72: unique character builds + realistic faces (owner-approved, built)

- **Per-character builds:** `tools/char_build.py` (`B[name]`: height, head/hand scale, shoulder/chest, belly/bust/hips, limb girth, lean, face params, hair volume pieces, clothing extras, props)
  is the single source for all actor renders; the Blender side is `tools/char72.py` (`load`, `dress`, `tweak(arm, BD)` after every `frame_set`, `Face72`, V1 Soft helpers).
  Used by `blender_cast.py` (NPCs, `USE72`; debug env `TL_FACINGS=s,se TL_NOWALK=1`), `blender_actor.py` and `blender_acts.py` (the player, all sheets). Old `cast.py` looks stay only for the robot.
- **V1 Soft actor look:** pixel filter 1.4, sky strength 1.5, sun 3.0 W with 30 degree angle, smooth shading + 1 subdivision on the bodies. Frame layout, feet (16, 54) and anchors are unchanged.
- **Face pass additions** (`face_pass.extra_paint`, parameters from `char_build.B[who]['face']`): lash flick (women), under-eye bag (age >= 1), heavy brow, lower lip, smile creases.
- Fixes: Okafor = open knee-length lab coat (3 box panels on the Hips bone), Lou's apron a flat plane, Victor smaller pads + deeper tan skin (#b9774a), Pimm darker cap. New characters need an entry in `char_build.B` AND `face_cfg.FACE`.
- Preview tip: render with `TL_FACINGS`/`TL_NOWALK`, quantize with `face_pass.quantize_sheet` + `paint_face` (see git history of this section for the idea). Cast re-render ~15 min, player + acts ~10 min.
