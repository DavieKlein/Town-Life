# Town Life — project guide for Claude

Game Boy Advance game in C++ using the [Butano](https://github.com/GValiente/butano) engine.
A story-driven top-down adventure/life-sim: mission-based progression, a villain, needs,
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

- **Needs:** Hunger, Energy, Hygiene, Fun (0–100). They decay over time and are shown in a HUD.
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

## Current state of the code

District 1 maps exist: **City Centre**, **Old Block** and the **Corner Market** interior, with
transitions (fade to black) between them. No text, needs or NPCs yet.

- **City Centre** (512x512): Corner Market (door → interior), Victor Vault's golden VaultTech
  tower with plaza, apartments, offices, a cafe with bus stop, a fountain square, the City Park
  (benches, pond — the player's future "home" bench is here), the river along the south with the
  **closed bridge to the Docks** (barrier + "CLOSED" sign), and road works blocking the main street
  to the north (future district). The avenue continues east into Old Block.
- **Old Block** (512x512): cobbled streets, row houses, community garden, graffiti wall,
  laundromat, bakery, basketball court, river, and the fenced **VaultTech demolition site** with
  a crane, bulldozer and a "SMART CITY — COMING SOON" billboard. West edge leads back to the City Centre.
- **Corner Market interior** (256x256): wooden floor, shelves, fridge, counter with register;
  the door mat leads back outside.
- Start position: on the sidewalk in front of Corner Market.

### Folder structure

```
.
├── .github/workflows/build.yml  CI: builds ROM in devkitpro/devkitarm, publishes release "latest"
├── butano/                      git submodule: Butano engine (pinned to tag 21.9.0)
├── Makefile                     Butano project makefile (TARGET=town-life, ROMTITLE=TOWN LIFE)
├── src/
│   ├── main.cpp                 init + main loop (creates the field scene)
│   ├── tl_field.cpp             field scene: current map bg, camera, player, warps with fades
│   ├── tl_player.cpp            player: input, movement, collision, walk animation
│   └── tl_world.cpp             map table lookup (includes the generated tl_world_data.h)
├── include/
│   ├── tl_world.h               map_info / warp / direction types, collision helpers
│   ├── tl_field.h, tl_player.h
│   ├── tl_map_id.h              GENERATED: enum map_id
│   └── tl_world_data.h          GENERATED: per-map collision, warps and the map table
├── graphics/                    Butano assets (.bmp + .json); all current ones are GENERATED
├── audio/  dmg_audio/           (empty) for music/sound later
└── tools/
    ├── gen_graphics.py          generates maps, sprite sheet and the generated headers
    └── headless_run.py          headless emulator test runner (screenshots + scripted input)
```

Code conventions: namespace `tl`, files prefixed `tl_`, Butano style (snake_case, `_member`).

### How the build works

1. `make` (Butano's `butano.mak`) converts `graphics/*.bmp` + `.json` into headers such as
   `bn_regular_bg_items_city_centre.h` and `bn_sprite_items_player.h` in `build/`.
2. Compiles `src/*.cpp` and links `town-life.gba` (header fixed with ROM title `TOWN LIFE`).
3. GitHub Actions (`build.yml`): job `build` runs in the `devkitpro/devkitarm` container, checks
   out the submodule, builds and uploads an artifact. Job `release` (only on `main`) deletes the
   old `latest` release/tag and creates a new one with `town-life.gba`.
4. Updating Butano: `cd butano && git fetch --tags && git checkout <tag>`, then commit the
   submodule. Watch out for API changes.

### Maps and graphics (tools/gen_graphics.py)

Python is the single source of truth for maps. Run `python3 tools/gen_graphics.py` after any
change and commit the generated files (CI does not run the script).
`python3 tools/gen_graphics.py --preview <dir>` also writes PNG previews (needs Pillow).

- Backgrounds are **8bpp** regular BGs sharing one palette (`BG_COLOURS`, named colours,
  index 0 = black backdrop). Map sizes must be multiples of 256 px (≤ 512 for normal BGs).
  The generator asserts ≤ 800 unique 8x8 tiles per map (VRAM budget, 8bpp tiles are 64 bytes).
  Keep textures periodic per 8/16 px so tiles deduplicate.
- A map is a grid of 16x16 **metatiles**. Each cell has a terrain character from `TERRAIN`
  (painter function + solid flag), e.g. `s` sidewalk, `P` plaza, `R/h/v` road, `Z/z` zebra
  crossing, `c` cobbles, `o` old sidewalk, `~` water, `E` embankment, `X` barrier, `t` tree,
  `q` planter tree, `b/B/n` benches, `l/L` lamps, `H` hedge, `F` wood fence, `C` site fence,
  `w` wood floor, `W/Y` interior walls, `m` door mat, ` ` void.
- **Stamps** draw large objects in pixels (`tower`, `corner_market`, `apartment`, `office`,
  `cafe`, `laundromat`, `bakery`, `fountain`, `billboard`, `crane`, `shelf`, ...) and make their
  footprint solid, except cells passed as `walkable` (doors).
- **Warps**: `m.warp(mx, my, w, h, target, tx, ty, facing)` — trigger rect in metatiles, target
  position in pixels (`None` keeps the current coordinate, used for edge transitions). The player
  triggers a warp with the point at their feet; place the arrival point outside the target's
  own warp rects.
- A small 3x5 pixel font (`_GLYPHS`) is available for signs: `cv.text(...)`.
- Player sprite: `player.bmp` 16x144, 4bpp with its own 16-colour palette, 9 frames of 16x16
  (0-2 down, 3-5 up, 6-8 side/right; left = horizontally flipped).

### Coordinates

- Player position is in **map pixels**, centre of the sprite.
- Butano world coordinate = map pixel − (map size / 2) (each bg is centred on 0,0).
- The camera follows the player and is clamped to the map edges.
- Collision: hitbox around the feet (10x6 px), checked per axis so the player slides along walls.

### Headless testing

```
apt-get install -y libretro-mgba          # once per container; Pillow is already installed
docker run --rm -v "$PWD":/src -w /src devkitpro/devkitarm make -j8
python3 tools/headless_run.py town-life.gba "wait 60; shot /tmp/a.png; hold up 30; wait 30; shot /tmp/b.png"
```
Commands: `wait N`, `hold KEYS N` (e.g. `right+b`), `press KEYS`, `shot FILE`. Look at the PNGs.

### Controls (current)

- D-pad: walk · hold B: run

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

1.1 Real map — DONE (awaiting owner feedback)
- [x] Replace the placeholder town with City Centre + Old Block (two connected 512x512 maps)
- [x] Landmarks: Victor Vault's golden VaultTech tower, Corner Market, the park benches, Old Block streets,
      VaultTech demolition site with "SMART CITY — COMING SOON" billboard
- [x] Visible blocked route to the Docks (closed bridge with barrier + "CLOSED" sign)
- [x] Map transitions with fade (district edge City Centre ↔ Old Block, door into Corner Market interior)
- [x] Headless test runner (`tools/headless_run.py`)

1.2 Needs + HUD + clock — TODO
- [ ] `needs` struct: Hunger, Energy, Hygiene, Fun (0–100), decaying over time
- [ ] HUD: 4 small bars/icons (sprites or a high-priority second bg layer)
- [ ] Game clock (day/time); START opens a pause menu with exact values
- [ ] Interact with objects (A in front of you): park bench = sleep/Energy, fountain = Hygiene, etc.
- [ ] Text: `bn::sprite_text_generator` with a font (see `butano/common`)
- [ ] Split `main.cpp` into scenes (`tl_scene.h` with an enum, one class per scene with `update()`)

1.3 Dialogue + NPCs — TODO
- [ ] NPC class (sprite, position, simple wander pattern, collision with player)
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

1.6 Save/load — TODO (moved forward: needed to play a whole district on the phone)
- [ ] Versioned save struct with `bn::sram::write/read` (see `butano/examples/sram`)
- [ ] Title screen: New Game / Continue
- [ ] Verify SRAM saves work in Lemuroid

1.7 Polish — TODO
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

Step 1.1 (real map) is done; apply any feedback from the owner on the maps first. Then continue
with **District 1, step 1.2 (Needs + HUD + clock)**, including splitting `main.cpp` into scenes
(the field scene already lives in `tl_field.cpp`).
