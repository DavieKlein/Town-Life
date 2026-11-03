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

Right now the game is a single placeholder town map with a walking player (no text yet).
That map will later be replaced/split into the real districts (City Centre, Old Block, ...).

### Folder structure

```
.
├── .github/workflows/build.yml  CI: builds ROM in devkitpro/devkitarm, publishes release "latest"
├── butano/                      git submodule: Butano engine (pinned to tag 21.9.0)
├── Makefile                     Butano project makefile (TARGET=town-life, ROMTITLE=TOWN LIFE)
├── src/                         C++ sources
│   ├── main.cpp                 init, camera, main loop
│   └── tl_player.cpp            player: input, movement, collision, walk animation
├── include/                     headers
│   ├── tl_player.h
│   ├── tl_town_map.h            collision helpers (solid_at / solid_rect) at metatile level
│   └── town_map_data.h          GENERATED: collision data per 16x16 metatile
├── graphics/                    Butano assets (.bmp + .json); town.* and player.* are GENERATED
├── audio/  dmg_audio/           (empty) for music/sound later
└── tools/gen_graphics.py        generates placeholder graphics + town_map_data.h (pure Python 3)
```

Code conventions: namespace `tl`, files prefixed `tl_`, Butano style (snake_case, `_member`).

### How the build works

1. `make` (Butano's `butano.mak`) converts `graphics/*.bmp` + `.json` into headers such as
   `bn_regular_bg_items_town.h` and `bn_sprite_items_player.h` in `build/`.
2. Compiles `src/*.cpp` and links `town-life.gba` (header fixed with ROM title `TOWN LIFE`).
3. GitHub Actions (`build.yml`): job `build` runs in the `devkitpro/devkitarm` container, checks
   out the submodule, builds and uploads an artifact. Job `release` (only on `main`) deletes the
   old `latest` release/tag and creates a new one with `town-life.gba`.
4. Updating Butano: `cd butano && git fetch --tags && git checkout <tag>`, then commit the
   submodule. Watch out for API changes.

### Editing graphics

Placeholder graphics come from `tools/gen_graphics.py`:
- Palette: 16 colours (index 0 = transparent), shared by background and sprite.
- Town: 32x32 metatiles of 16x16 px = 512x512 px regular background (4bpp).
  Metatile characters (`.` grass, `R/h/v` road, `s` sidewalk, `T/W/D` house, `t` tree, `~` water, ...)
  are defined in `TILES`, each with a "solid" flag. The layout is built in `build_layout()`.
- Player: `player.bmp` 16x144, 9 frames of 16x16 (0-2 down, 3-5 up, 6-8 side/right;
  left = horizontally flipped).
- After changes: run `python3 tools/gen_graphics.py` and commit the generated files
  (CI does not run the script).
- Butano BMP requirements: indexed, uncompressed; regular bg dimensions multiples of 256 px.

### Coordinates

- Player position is in **map pixels** (0..511), centre of the sprite.
- Butano world coordinate = map pixel − 256 (the bg is centred on 0,0).
- The camera follows the player and is clamped so it never scrolls past the edge of the map.
- Collision: hitbox around the feet (10x6 px), checked per axis so the player slides along walls.

### Controls (current)

- D-pad: walk · hold B: run

---

## Roadmap / status

Something must be playable after every step. Update the checkboxes at the end of each session.

### 0. Foundation — DONE
- [x] Butano project (submodule at 21.9.0), Makefile, `.gitignore`
- [x] GitHub Actions: build in devkitarm container + release `latest` with `town-life.gba`
- [x] Placeholder town tilemap 512x512 (roads, sidewalks, 8 houses, park with fountain and pond)
- [x] Player with d-pad, 4-direction walk animation, collision, following camera, run with B
- [x] Design document (this file) with full game design

### 1. Needs + HUD — TODO
- [ ] `needs` struct: Hunger, Energy, Hygiene, Fun (0–100), decaying over time
- [ ] HUD: 4 small bars/icons (sprites or a high-priority second bg layer)
- [ ] Game clock (day/time); START opens a pause menu with exact values
- [ ] Interact with objects (A in front of you): park bench = sleep/Energy, fountain = Hygiene, etc.
- [ ] Text: `bn::sprite_text_generator` with a font (see `butano/common`)
- [ ] Split `main.cpp` into scenes (`tl_scene.h` with an enum, one class per scene with `update()`)

### 2. Dialogue system + NPCs — TODO
- [ ] NPC class (sprite, position, simple wander pattern, collision with player)
- [ ] Dialogue box at the bottom with text paging (A = next) and simple choices
- [ ] Dialogue data in a compact table format (speaker, lines, choices, effects)
- [ ] A few original NPCs in the City Centre / Old Block

### 3. Mission system + mission log + district locks — TODO
- [ ] Mission data: id, objective text, conditions (talk to X, go to Y, earn $Z), rewards
- [ ] Story flags + current chapter/mission state
- [ ] Mission log in the pause menu showing the current objective
- [ ] District lock system: locked districts with visible in-world blockers that open via flags
- [ ] Map transitions between districts (separate maps per district)

### 4. Opening chapter (Chapter 1: Survive) — TODO
- [ ] Corner Market interior (warm palette), coworkers and regular customers
- [ ] Cutscene: Victor Vault buys the store and fires everyone
- [ ] VaultMart transformation (cold palette, self-checkouts, robot voice)
- [ ] Start state: $20, park bench as home, only City Centre + Old Block open
- [ ] Money variable + HUD; first odd jobs paying small amounts
- [ ] Introduce the rival character
- [ ] Warm/cold palette state per area
- [ ] Chapter end: unlock the Docks

### 5. First full type: Grafters (Docks) — TODO
- [ ] Docks district map
- [ ] Mentor NPC + Grafters mission chain
- [ ] Career path jobs (shelf stacker → forklift driver → shift lead → own transport company)
- [ ] Minigames: stacking boxes, driving
- [ ] Skills (Strength, Creativity, Logic, Charm, Fitness) + reputation stars, incl. rival half-speed rule

### 6. Friendship + City Coins perks — TODO
- [ ] Friendship per NPC (0–100), raised by talking, gifts, helping
- [ ] City Coins at 70+ friendship; perk shop (higher pay, slower need decay, faster walking)

### 7. Housing ladder + shop — TODO
- [ ] Housing ladder: park bench → rented room → studio → apartment → house in chosen type's style
- [ ] Enterable homes; shop scene with items and prices
- [ ] Furniture that refills needs (bed, shower, fridge, TV)
- [ ] Vehicles as rewards: bike → scooter → car

### 8. Save/load — TODO
- [ ] Versioned save struct with `bn::sram::write/read` (see `butano/examples/sram`)
- [ ] Title screen: New Game / Continue
- [ ] Verify SRAM saves work in Lemuroid

### 9. Remaining districts, types and chapters (in unlock order) — TODO
- [ ] Makers / Old Factory (Chapter 2: Get By) — rhythm and drawing minigames
- [ ] Techies / Station Quarter (Chapter 3: Build Up) — puzzle and code-pattern minigames
- [ ] Ballers / Sports Park (Chapter 3–4: Break Through) — penalties, timing, fitness minigames
- [ ] Posh / Hilltop (Chapter 4–5: Legacy) — bluffing and negotiating minigames
- [ ] Own businesses with passive daily income; investing
- [ ] Finale: Victor Vault's downfall, Old Block saved

### 10. Better graphics and music — TODO
- [ ] Real pixel-art tilesets and characters (original designs), multiple palettes
- [ ] Objects drawn over the player (tree tops, roofs) via a second bg layer
- [ ] Music (.mod/.xm/.s3m in `audio/`, maxmod) and sound effects; warm vs. cold music

## Next session: start here

Start with roadmap step **1** (Needs + HUD). Split `main.cpp` into scenes as part of that step.
