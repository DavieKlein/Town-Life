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
| Ultimate Food Pack (Oct 2019) | not yet | supermarket products |
| Furniture Pack (March 2019) | not yet | furniture to buy/place in homes |
| Ultimate House Interior Pack (June 2020) | not yet | home interiors, buyable furniture |
| Furniture Pack (Oct 2017) | not yet | **no licence file in the folder** — verify before use |
| David OReilly — Everything Library: Animals (Drive folder `EverythingLibrary_Animals_002`, ~240 static models incl. Crow, Gull, Cat, dogs, Rat, Duck, Raccoon) | `art_source/everything_library_animals/city_animals.glb` (GroundedPigeon, Pigeon, GraySquirrel only) + License.txt | **CC BY 4.0 (not CC0) — attribution required, credited in README.** Static models; colours are vertex colours; the GLB is in centimetres and lost the FBX up-axis rotation (blender_critter.py compensates: `UNIT`, `BASE_PITCH`, per-model `YAW`). |

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

**Full City Centre (awaiting owner feedback)** plus the Corner Market interior, a 3D-rendered
player and the HUD. History: top-down maps at commit `5af63a1`; hand-painted isometric prototype at
`786cc4c`; pre-rendered street corner at `99203ab`.

- City Centre (72x60 cells = 54x45 m, image 2144x1272 px): main avenue along x (y 22..30) and a
  cross street along y (x 26..34) with curbs, lane markings, zebra crossings and manholes.
  North-west: downtown apartment building (MegaKit). North-east: Corner Market (door → interior),
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
- HUD bar with a working clock (1 real second = 1 game minute, starts 8:00 am) and money ($20).
  Needs (`tl_needs.h`: Hunger, Energy, Hygiene, Fun, 0-100) decay per game minute and drive the
  four HUD bars (`need_bar` sprites, 16 fill levels, green/orange/red).
- Interactions: `tools/interactions.py` lists interactable objects per map (kind, x, y[, radius]),
  emitted as `map_info::interactables`. A (while walking) opens a menu (`tl_menu`: dark panel
  top-right, cursor, A ok / B back) for the nearest object in reach: **park bench** → Sit (Fun +,
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
- Start position: on the sidewalk in front of the Corner Market door (cell 44, 19).

### Folder structure

```
.
├── .github/workflows/build.yml  CI: builds ROM in devkitpro/devkitarm, publishes release "latest"
├── butano/                      git submodule: Butano engine (pinned to tag 21.9.0)
├── Makefile                     TARGET=town-life, ROMTITLE=TOWN LIFE; also uses butano/common
│                                (graphics + include) for the 8x8 sprite font
├── src/
│   ├── main.cpp                 init + main loop (creates the field scene)
│   ├── tl_field.cpp             field scene: camera, streamed layers, player, warps with fades, HUD text + clock
│   ├── tl_streamed_bg.cpp       tile-streaming regular BG (see "Engine")
│   ├── tl_player.cpp            player: iso movement, collision, depth priority, animation, shadow
│   ├── tl_critters.cpp          ambient pigeons + squirrels (behaviour, sprites, depth)
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
  `parking_meter`, `fence_wood`, `chain_link`, `poster`, `weeds`, `ivy`.
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
- **build_assets.py**: per layer, k-means picks 7 palettes of 15 colours (floor) / 7 (objects);
  each 8x8 tile uses the palette that fits best; tiles are deduplicated incl. flips (tile 0 = empty).
  Prints unique tile counts and the worst 31x21 window. Bank budget: floor 7 + objects 7 + HUD 1 ≤ 16.
  Work is done in chunks of tiles so big maps fit in memory. City Centre: ~15.6k floor + ~9.9k
  object tiles (~0.8 MB of tile data), full-quality build ~20 min.
- **blender_actor.py**: imports a rigged Quaternius character FBX, recolours its materials
  (Shirt, Pants, Hair, Skin, Shoes, Socks, Eyes; `PLAYER_COLOURS` in build_assets.py), scales it to
  1.78 m and renders the Idle pose + 8 frames of the Walk action for 8 facings (clockwise screen
  order s, sw, w, nw, n, ne, e, se), 4x supersampled; build_assets adds a 1 px dark outline and
  quantizes to one 15-colour palette. Frame 32x64, feet at (16, 54); sheet = 72 frames.

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
- [ ] Food pack in the supermarket (owner asked for this next)
- [ ] Furniture + House Interior packs (homes; later a buyable selection for the housing ladder/shop)
- [ ] Owner approves the look (feedback round)
- [ ] Full Old Block: row houses, garden, laundromat, bakery, court, demolition site
- [ ] Map transitions between City Centre and Old Block

1.2 Needs + HUD + clock — IN PROGRESS
- [x] `needs` struct: Hunger, Energy, Hygiene, Fun (0–100), decaying over time
- [x] HUD: 4 small bars/icons (sprites or a high-priority second bg layer)
- [ ] Game clock (day/time); START opens a pause menu with exact values
- [x] Interact with objects (A + option menu): park bench = sit/sleep, fountain = wash
- [ ] More interactions with furniture (shower, toilet, fridge, cooking, repairing) once homes exist
- [x] Text: `bn::sprite_text_generator` with a font (see `butano/common`)
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

**Graphics upgrade proposal (sent to the owner, awaiting approval):** "Urbz essence, modern
fidelity". Mock-ups were made from real emulator screenshots with GBA-legal operations only.
1. Light and atmosphere:
   - Cloud shadows on the free BG3, alpha-blended with the same EVA/EVB as the player shadow.
   - Day/night cycle by palette transforms driven by the clock.
   - Night lights: lamp pools as additive blending on BG3, and lit windows via reserved palette
     entries.
   - Blending is one global setting, so clouds (day) and lights (night) take turns.
2. Life: water and fountain ripples by palette cycling (4 reserved entries), flickering signs.
3. Depth:
   - Bake per-tile depth from Blender. The player sprite always draws over the map, and only the
     object tiles that are really in front are redrawn over it as small mask sprites (objects
     palettes copied into sprite palettes).
   - This replaces the whole-layer priority switch; an always-on-top layer for canopies and
     awnings is included.
4. Render fidelity: bevelled edges, the owner's own texture/graphics packs (to be uploaded to
   Drive; no Remote Control folder is connected), glossy water with reflections, denser props.

**New (owner, latest):** the owner added more packs to the Drive folder in the agreed
**isometric urban** style: commercial and residential buildings plus texture packs. List the
Drive folder first, check each licence, and propose (with preview renders) how to use them
(Old Block row houses, shops, ground textures) before building.

The owner asked for (1) the full City Centre — done, awaiting feedback — and then (2) the
**Ultimate Food Pack** in the Corner Market supermarket (replace the box products in `product()` /
`gondola()` with food models: download from the Drive folder, keep only what is used in
`art_source/quaternius_food/`). After that: Old Block (east end of the avenue) and step 1.2.
