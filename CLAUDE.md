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
- **Housing ladder:** park bench → rented room → studio → apartment → house in your chosen
  type's style.
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
2. **Get By** — Grafters/Docks and Makers/Old Factory. Big moment: first own home (rented room).
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
  grimy). **Public toilet layout (6x6):** open white WC on the back wall at (2.9, 1.5) (`toilet_unit`, lid up, nothing in
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
  - **"A" cue:** `field::_update_cue` draws a bobbing gold bubble (`ui_icons` frame 2, bob 0/1/2/1 px per 8 frames)
    above the nearest interactable in reach (same reach rules as the menu, `field::_find_target`) while walking;
    hidden during menus, activities, pause and fades. Per-kind height offsets (bench 22, seat 26, fountain 36,
    bin/sink/reception 40, shelf/notice board 46, rest 38 px) are in `_update_cue`.
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
│   ├── tl_save.cpp, tl_title.cpp, tl_pause.cpp, tl_field_pause.cpp   save format, title screen, pause screen
│   └── tl_world_data.cpp        GENERATED: palettes per layer, collision, warps, occluders, map table
├── data/                        GENERATED binary layer data (Butano DATA rule): <map>_<layer>_tiles.bin
│                                (8 words per 4bpp tile) and <map>_<layer>_cells.bin (uint32 per 8x8 cell)
├── include/
│   ├── tl_world.h               map_info / layer_data / warp / occluder / direction + helpers
│   ├── tl_field.h, tl_player.h, tl_streamed_bg.h
│   └── tl_map_id.h              GENERATED: enum map_id
├── graphics/                    GENERATED Butano assets: hud, player (32x64 x 72 frames), shadow
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
    ├── blender_critter.py       poses + renders the animal models into sprite frames
    └── headless_run.py          headless emulator test runner (screenshots + scripted input)
```

Code conventions: namespace `tl`, files prefixed `tl_`, Butano style (snake_case, `_member`).

### How the build works

1. **Art (only when scenes change, in the Claude container):**
   `apt-get install -y blender python3-numpy` (once per container; numpy is needed by Blender's
   FBX importer), then `python3 tools/build_assets.py`
   (~10 min at full quality; `--fast` for quick low-quality tests; `--preview DIR` writes PNGs of the
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
  **Style pass** (`stylize()` in blender_render.py, always on): Freestyle outlines (silhouette,
  border, crease; only on the layer being rendered, via the `tl_visible` collection) and
  `add_grime()` which multiplies every material's base colour with an ambient-occlusion term
  (dark, slightly purple corners). Worn ground materials: kinds `asphalt_grit` / `paving_grit`
  (materials `asphalt`, `paving`, `slabs`) with grain, dirt patches, Voronoi cracks and weeds.
  `grade()` in build_assets.py adds saturation, contrast and cool shadows before quantization.
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
  quantizes to one 15-colour palette. Frame 32x64, feet at (16, 54); sheet = 72 frames.

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
- START (while walking): pause menu (freezes the game): day, time, money, the five needs with exact values,
  objective line, Resume / Save game / Quit to title. B or START resumes.

---

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

1.3 Dialogue + NPCs — TODO
- [x] Static NPC sprites (`tl_npcs`, Mia at the checkout)
- [ ] NPC class (simple wander pattern, collision with player, talking)
- [ ] Dialogue box at the bottom with text paging (A = next) and simple choices
- [ ] Dialogue data in a compact table format (speaker, lines, choices, effects)
- [ ] Original NPCs: Corner Market coworkers, regular customers, Old Block residents

1.4 Missions + mission log — TODO
- [ ] Mission data: id, objective text, conditions (talk to X, go to Y, earn $Z), rewards
- [ ] Story flags + current chapter/mission state
- [ ] Mission log in the pause menu showing the current objective
- [ ] District lock system driven by flags (the Docks blocker)

1.5 Chapter 1 story — TODO
- [ ] Working at Corner Market (warm palette)
- [ ] Cutscene: Victor Vault buys the store and fires everyone
- [ ] VaultMart transformation (cold palette, self-checkouts, robot voice)
- [ ] Start state: $20, park bench as home; money in HUD
- [ ] First odd jobs paying small amounts
- [ ] Introduce the rival character
- [ ] Chapter end: unlock the Docks

1.6 Save/load — IN PROGRESS (moved forward: needed to play a whole district on the phone)
- [x] Versioned save struct with `bn::sram::write/read` (`tl_save.h/.cpp`), manual saving only (owner: no autosave)
- [x] Title screen: Continue (only with a valid save) / New Game (`tl_title.cpp`)
- [x] Pause menu (`tl_pause.cpp`, `tl_field_pause.cpp`)
- [x] Headless: save, reset, Continue restores map/position/time (mGBA reports 32 KB SRAM)
- [ ] Verify SRAM saves work in Lemuroid on the phone

Save/pause notes: `save_data` (tl_save.h) is one packed struct at SRAM offset 0 (732 bytes): magic "TLSV", version,
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
- [ ] Housing ladder step: rented room (Chapter 2 big moment) + first shop/furniture
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
- [ ] Minigames: bluffing, negotiating; investing; car; house in chosen type's style
- [ ] Finale: Victor Vault's downfall, Old Block saved
- [ ] Polish + owner approval

## Next session: start here

**Milestone done (owner: "put everything on main; finish the district now, fine-tuning later"):**
five enterable buildings, shops, fixtures, Mia, fine collision, fountain with water in the basin.
**Postponed fine-tuning (do when the owner asks):** water is now realistic with sparse glints (see
Day/night lighting; check it on the phone), fountain detail, eye-level street details (commit `c3aaccc`),
the shabby first home entrance (`home_room`), the player V2 look, and a tree in City Park at
(4.0, 45.5) that covers the player on the path in front of the toilet. Next big steps: dialogue
box with portraits + friendship meter, missions, Old Block.

**Eye-level street details proposal (parked, "details later"):** the scene.py and
blender_render.py code is in commit `c3aaccc` (WIP). It adds projecting shop signs, bikes, wall
lamps, a café table, a mailbox, etc. It was reverted from main until the owner wants details.

**Owner decisions (latest):**
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
- **Dialogue box:** variant 2. A 40 px box at the bottom with the speaker's 64x64 portrait
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
