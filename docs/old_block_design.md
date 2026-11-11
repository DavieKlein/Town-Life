# Old Block - design proposal (s74, NEEDS OWNER APPROVAL, nothing built, nothing added to `SCENES`)

Old Block is the poor, warm, close-knit district at the east end of the City Centre avenue. It completes district 1 (Chapter 1, M08-M17).
Original design; the only reference is the *genre* feel of handheld life-sims (a crowded little neighbourhood you learn by walking it).
Story sources: `docs/story_chapter1.md` 3B.2 / 3B.2a / M09-M17, `docs/story_overview.md`, `docs/features_backlog.md`.
Proposal code + renders: `tools/proposals/s74/` (see its README). Previews: `tools/proposals/s74/previews/*.png`.

## 1. Design in one paragraph

You enter from the avenue and the first thing you meet is **cold**: a VaultTech cable works (barriers, a trench, drums, a robot, a bored guard, a hoarding
with "SMART CITY COMING SOON"). Behind a **brick arch** (OLD BLOCK - EST. 1931) glows the **warm** street: cobbles, terracotta / ochre / rose / blue plaster,
washing lines and bunting across the road, flower boxes, a laundromat with machines turning, a bakery, a corgi. Everything is built so that
**the way in changes the player's feeling**: first a sneak through a fence flap and a bush lane (M09), later the front door when the neighbours move the
barriers (M13). The street ends at a **fenced demolition site** with the derelict Co-op Hall and the humming NODE 7 hatch: the threat is always visible at the end of the street.

## 2. Map facts

| Item | Value |
|------|-------|
| Map id (proposed) | `old_block`, "Old Block" (new entry in `SCENES`, appended so ids stay stable) |
| Size | **60 x 48 cells** = 45 x 36 m (City Centre 72 x 60) |
| Image | 1760 x ~1020 px (origin_x = 48*16+16 = 784, origin_y = 175; City Centre 2144 x 1272) = ~0.62 of the City Centre area |
| Camera rule | faces that look towards +y and +x are visible: **every shopfront stands on the north side of the street**, everything south of the street is open or low |
| Streets | avenue stub (x 0..14.5, y 18.5..25.5, 8 cells = same width as the City Centre avenue) and **Cobble Street** (x 15.7..50, y 19.5..24.5, 5 cells wide) |
| Entry from the City Centre | the avenue's east end: CC `x >= 70.5` strip (y 18..34) warps to OB `(1.5, y - 4)`; OB `x <= 1` strip warps back to CC `(70.0, y + 4)` |
| Collision | fine grid as usual. New: **gated solids** (see 9) |

ASCII plan (1 char = 2 x 2 cells, `x` right / east, `y` down / south; the PNG plan has the exact coordinates):

```
        0         10        20        30        40        50        60
  y 8   ..........  ....[VALDEZ][  YARD  ][BAKERY ][ROW4 ]    |  CO-OP HALL (derelict)
  y 14  ..HOARDING..|b  [  LAUNDROMAT  ][bk-room]   .        |  site (fenced, closed)
  y 18  ===avenue===|T=A= C O B B L E   S T R E E T  =====STALL|  NODE 7 hatch, digger
  y 24  ===  stub ==|    (cobbles, lines, bunting)            |g
  y 28  ..FENCE.THICKET  [ GARDEN ] [chess] [   COURT   ]       |
  y 40  ..............hedges, trees (low only)..............     |
        b = barriers (x 10.5)  T = trench  A = arch  g = closed site gate  bk-room = Ines's back room
```

## 3. Zones (coordinates in cells)

| Zone | Area | What is there |
|------|------|---------------|
| **A. Cable works (cold)** | x 0..14.5, y 14..34 | hoarding wall (y 15) with VaultTech posters + gold "V", portaloo, 3 cable drums (north) + 4 (south), orange/white **barrier line at x 10.5** with 3 amber lamps and the SURVEY IN PROGRESS board, **trench x 11.3..13.3** (mud, tape, a cable laid in it), TRENCH-E 3 inside it, Guard Pruitt on a folding chair on a drum at (8.6, 19.9), a security camera on a pole, grey chain-link fence continuing south to the map edge |
| **A2. Sneak route** | x 9..18, y 27..34 | player side: a **hedge hides the flap** at fence (10.5, 30.2..31.2). Behind the fence: **bush thicket** with a **one-cell lane** (10.9 -> 17, y 30.35..31.05, then north x 16.4..17.1 up to y 27) that comes out at the south pavement just inside the arch. See 8 |
| **B. The arch** | x 14.5..15.7, y 18.5..25.5 | two brick pillars, beam, iron sign "OLD BLOCK / EST. 1931" half pasted over with VaultTech posters (readable face is the +x side, i.e. what the camera sees) |
| **C. Cobble Street (warm)** | x 15.7..50, y 19.5..24.5 + pavements | patched cobbles, kerbs, drains, weeds, 3 curved lamps, bins, hydrant, newspaper box, flower pots on stoops, **washing lines + bunting** between the north facades and 3 poles on the south pavement |
| **D. North row** | facade line y = 18 | Valdez house (x 16.5..21, 3 storeys, terracotta, balcony + Captain), **Ines's Laundromat** (21..29.5, 3 storeys, ochre, blue frame, yellow/white awning, Mia's window third floor), the **yard** (29.5..35, gate + wooden fence), **Bellini Bakery** (35..41.5, 2 storeys, rose, red/white awning, Dr. Okafor's flat above), row house 4 (41.5..46, blue, satellite dish) |
| **D2. Yard + back room** | x 29.5..35, y 6..18 | dirt/cobble yard, the **back room annex** (29.9..32.9 x 9.5..14.5, tin roof, door on its +x face with mat and "ROOM" plate = the future home), the M10 crate stack, a drying line, Duchess's bed, bin, laundromat east wall with a **sun + fish mural** |
| **E. South side** | y 26..42 | **community garden** (17..29 x 27..40: 8 raised beds with tomatoes, cabbages, sunflowers, beans, flowers; shed, rain barrel, compost, scarecrow, bench with a WATER ME sign, wooden fence with a gate), **chess plaza** (29.5..34 x 26.5..32: plane tree, stone table, two stools), **street court** (34.5..48.5 x 28..38.5: painted rust/green court, two hoops, low chain-link, benches, bin) |
| **F. Street end** | x 45.5..50 | **Rosa's stall** (handcart, striped awning, crates, scale, BREAD NOT BARCODES board), **Teo's door ramp** (a green door on bricks), the closed steel site gate with a NOTICE |
| **G. Demolition site** | x 50..60, y 4..34 | orange-railed fence with orange notices + Teo's counter-posters, the derelict **Co-op Hall** (brick, boarded windows, chained arched door, stone lintel "OLD BLOCK CO-OPERATIVE 1931", roof gaps with weeds), yellow digger "VAULTTECH", **NODE 7 hatch** at (51, 22.5) with orange cables, rubble, a floodlight. Whole site is solid (opens in Chapter 5) |

Low-only rule for the south edge (y 40..48) and the garden / court: tall objects there would hide the street. Trees south of the street are limited to the
chess plane tree; the player is hidden behind it by the per-pixel depth mask only on a short stretch of Cobble Street.

## 4. Enterable buildings and interiors (all cutaway rooms via `std_room`, furniture only from the catalog)

Chapter 1 needs only **exteriors plus the laundromat, bakery, back room and Mia's flat**. Valdez, row house 4 and the Co-op Hall stay closed.

| Interior | Size | Layout (summary) | Interactables | When |
|----------|------|------------------|---------------|------|
| **Ines's Laundromat** (`laundromat`) | 14 x 10 | front window wall with the street; row of 6 washers + 4 dryers along the back wall, folding table, plastic chairs (seats), soap vending machine, a lost-sock box, notice board (odd jobs), Duchess's bed, chalkboard "TWO DOLLARS", door at the back-right to the stairs (Mia's flat) and the back room | `washer` (Wash your clothes $2: sets a clean-clothes flag, small Hygiene/Fun), `seat` x4, `noticeboard` (Old Block odd jobs), `kiosk`-like soap machine (gift item), `lostsock` (collectible spot), Ines (talk) | Chapter 1 (M09 intro, M17) |
| **Back room** (`back_room`) | 6 x 5 | bare walls, mattress on the floor, crates, hot plate, bucket, one bulb, a window to the yard; bills-by-post envelope at the door; later filled from the furniture catalog | `bed` (mattress), `desk`/crate, `window`, envelope | Chapter 2 (big moment M17 -> "a key in the door"); exterior now |
| **Bellini Bakery** (`bakery`) | 10 x 8 | counter with display cases, ovens glowing at the back, flour sacks, two small tables with chairs, stairs up (Okafor's flat, blocked) | `shop_bakery` (Rosa's loaf is NOT here: bread $3, pastries $2-4, coffee), `seat` x4, `oven` (watch / warm-up: Fun +2), Nella (cameo Ch.2, 5) | Chapter 1 shop, Chapter 2+ talks |
| **Mia's flat** (`mia_flat`) | 7 x 6 | one room, one couch (Energy +0.5/min), kettle, window over the street, boxes | `couch` (sleep, M17), `window` | M17 |
| Valdez house, row house 4, Co-op Hall | later | - | - | Chapter 2 (Valdez, Biscuit quests), Chapter 5 (Hall) |

Cost: each interior ~ 1-2k tiles, comparable to `diner` / `community_centre` (cutaway rooms are small images).

## 5. Interactables (`tools/interactions.py` style; `*` = new kind that needs a small handler)

| Kind | Where | What |
|------|-------|------|
| `sign*` | barrier (10.2, 21), arch (14, 22), gate (49.3, 22) | info pages (survey notice; "Est. 1931 ..."; demolition notice) |
| `flap*` | (9.3, 30.7) | before `sneak_route`: "Just a fence. And a lot of bushes."; after: "Squeeze through" (starts the lane walk) |
| `hatch*` | (51, 22.5), extra reach 1.5 | "A steel hatch. It hums. It is warm. Warmer than the street." (sets nothing; `node7_seen` for later) |
| `shop_stall*` | Rosa's stall (47.2, 23.6) | Rosa's loaf, Orange, Rye loaf; Gifts (Flowers $3); M15: free orange per friendship 40+ |
| `chess*` | (32.2, 28.7) | "Watch the game" (Fun +2, Grigor hint lines), M13 chat |
| `garden*` | beds (23, 30) | "Water the plants" (Fun +4, Hygiene -1; Ines/gossip hook; once per day for +friendship with Ines) |
| `hoop*` | (36.4, 33.7), (46.6, 33.7) | "Shoot hoops" (Fitness +, Energy -, Fun +; 8 s animation; Ballers mini-game later) |
| `bench`, `bin`, `kiosk`, `noticeboard`, `crate` | see `tools/proposals/s74/data.py` | existing kinds (court bench, 4 bins, scratch-card box, Mia's poster wall from M13, M10 crates) |
| RETURN & EARN spots | ~14 new spots (gutters, garden, court, yard, thicket) | same global cap (7 credits loose in the world); machine stays in the City Centre |
| collectibles | 3-4 new spots (lost sock, Docks postcard, Co-op penny in the garden, a pigeon feather) | `tools/collectibles.py` |

## 6. NPCs, schedules and routes

Existing cast slots are tight (8 small-talk slots, ~3 NPC sprites on screen during a talk). Old Block adds **Ines, Teo, Grigor** as talkers (needs slots -> raise
the cast table to 12), and **Duchess, Pruitt, TRENCH-E, Mrs. Valdez + Captain** as barks-only actors.

| Who | Spot / route | When | Notes |
|-----|--------------|------|-------|
| **Pruitt** | chair at (8.6, 19.9) before M13; after M13 at (11, 20.5) with a cup of tea | always | bark + info; "I never see anybody" when the player uses the lane |
| **TRENCH-E 3** | in the trench (12.3, 21.3), idle bob; 4 facings only | always | after M13 it "classifies" the door bridge as furniture |
| **Ines** | laundromat door (28.4, 19.3) 7:00-21:00, inside at the counter in bad weather / evening | | shouts "Clean shirts, clean souls!" when the player passes |
| **Teo** | `ROUTES["teo_round"]`: arch (15.5, 26.5) -> chess (31, 25.5) -> stall (46, 24.8) -> yard (33, 17) -> garden gate (23, 26.8) | 10:00-19:00 | wanders (12 walk frames exist for cast); waits at the lane exit in M09 |
| **Duchess** | yard bed (31, 16); walks the street 12:00-13:00 | | placeholder blob in the render |
| **Grigor** | stool at the chess table (31.25, 27.6) | 10:00-18:00 | loses to the pigeon; M13 chat |
| **Mrs. Valdez + Captain** | balcony (18.5, 18.8) above the arch side | always | Captain barks "NEXT CUSTOMER!" when you pass below (M09 on) |
| **Rosa** | behind the stall (49.2, 21.6) | from M10, 8:00-17:00 (Saturday market 9:00-15:00) | |
| **M13 crowd** | Mia (44.3, 23), Ines (45.3, 20.8), Teo (47.5, 21), Grigor (46, 24), Valdez (43.5, 22), Pimm (44.8, 22.2) | 9:00 meeting | placements overridden by script flag |
| **Dr. Okafor** | lives above the bakery, never shown; evening beat in the clinic (CC) | | |

## 7. Mission hooks (M08 - M17)

| Mission | Old Block use |
|---------|---------------|
| M08 Odd Jobs | the laundromat notice board adds 2 odd jobs ("Carry the laundry" $6, "Water the garden" $4) once `old_block_open` |
| **M09 Old Block Calling** | Mia leads along the fence (x 9..10, y 26..30) -> flap (10.5, 30.7) -> lane -> **exits at (16.8, 27)** beside the arch where Teo waits -> camera tilts to the sign (15.2, 22) -> Valdez balcony (19.2, 21) -> chess (30.8, 26.8) -> Mia points at her window (24, 20.5) -> Rosa at the street end |
| M10 Rosa's Stall | crates in the yard (33.4, 12.3), the stall (47, 22.8), BREAD NOT BARCODES sign |
| M11 / M12 / M14 | only the walk to and from Old Block |
| **M13 Notice Served** | 9:00 meeting at the stall; orange notices on every wall (poster props swap), Teo's counter-posters; **after the meeting the barriers are dragged aside + Teo's door bridge** (state C, 8) |
| M15 Open Sesame | optional Saturday market (stalls along Cobble Street y 20..24, anonymous crowd reskins) |
| **M17 A Roof for the Night** | Mia's flat via the laundromat stairs; chapter end; back room promised (Chapter 2) |

## 8. The cable works in three states (collision + art variants)

| State | Flags | Barriers (x 10.5) | Trench | Flap | Lane (solids) | Front |
|-------|-------|-------------------|--------|------|---------------|-------|
| A (start) | - | solid | solid | solid (fence), hedge solid | solid | closed |
| B (after M09 scene) | `old_block_open`, `sneak_route` | solid | solid | open | **walkable, half speed, leaf particles** | closed |
| C (after M13) | `barrier_moved`, `door_bridge` | middle pieces (y 20..24) moved aside with laundry hung on them (art variant swaps via a second palette-free "overlay" of objects tiles or a small sprite set) | door bridge walkable (x 11.3..13.3 x y 21.3..22.7) | stays as Teo's shortcut | walkable | open |

**Engine need (small): "gated solids"**: a table of `{rect, flag, invert}` evaluated when a map loads and on flag changes (`field::_refresh_gates`). Used for the lane,
the flap, the hedge pocket, barrier gap and bridge. No new render per state if the barrier line is split into 2 pieces: the *moved-aside* variant is a
sprite overlay (3 sprites: laundry-draped barrier pieces) drawn over the unchanged tiles, and the bridge door is a sprite (32x16). The barrier gap itself is just
the solid being switched off: the painted barrier would stay drawn, so build the barrier as **sprites** (4 pieces) rather than tiles if the owner wants the gap to be visible.
Cheaper alternative: leave the barrier tiles, put the aside-pieces and bridge as sprites on top and accept the barrier "ghost" (not recommended).

**Squeeze effect** (as in 3B.2a): on lane cells half speed, a few leaf sprites drift (existing `critters`-style sprite pool, 4 leaves), tiny camera sway
(2 px), the front-layer mask hides the player behind the three taller bush clumps (the lane's camera-side rows are kept low on purpose: at 2:1 isometric anything
0.75 m tall hides ~2.5 cells of ground behind it, which would hide the whole lane).

## 9. Warm vs cold palette (VaultTech-taken parts colder)

- **Materials**: cold = `vault_hoard` navy, `vault_cold` grey-blue, orange/white barriers, grey chain-link, white notices; warm = terracotta / ochre / rose / teal / blue plaster,
  red brick, wood, flowers, yellow awnings.
- **Cold zones** are A (x < 15), the demolition fence + site (x >= 50) and the notice posters. Everything between is warm.
- **Engine idea (cheap, needs a build_assets change, not done here)**: reserve **2 of 8 floor banks and 2 of 7 object banks** for tiles that lie in a cold zone
  (a `cold_mask` rectangle list per map), build each of them twice (cold + warm variant, 2 x 16 colours) and let `tl_lighting` blend between the variants by
  a per-map `warmth` byte (save: `warmth_ob`, 0..100). When Chapter 1 ends or later missions "win" an area, the cold bank blends to warm, as the owner wants
  ("winning missions turns an area warm again"). Bank budget stays 16 (floor 8 + objects 7 + HUD 1).
- Day/night as usual (outdoor map): lit windows (laundromat window, bakery window, flats) and lamp pools at 3 street lamps + 2 pillar lamps + the amber barrier lamps (blink = palette entry).

## 10. Lived-in, gritty details (all in the proposal scene)

Patched cobbles + asphalt patches, cracks and stains, weeds in the joints, damp streaks under cornices, drainpipes, AC units, satellite dishes, window boxes, shutters,
stoops with iron rails, washing lines + bunting, milk crates, chalkboard, hand-lettered signs, mural, scuffed court, scarecrow, rain barrel, door-ramp, VaultTech posters pasted over the arch,
orange notices on the fence, mud heaps, tape, cables. To add later: stray cat (collectible spot), pigeons (critters: arch, stall, chess), laundry sway (palette-free: 2 frame sprite), smoke from the bakery chimney (sprite).

## 11. New art, props and characters needed (NEEDS PROPOSAL where visual)

- Scene helpers (in `oldblock.py`, would move to `scene.py`): `row_house`, `laundromat`, `bakery`, `arch`, `cable_works`, `cable_drum`, `trench_e`, `pruitt` (placeholder), `plane_tree`,
  `chess_table`, `rosas_stall`, `garden`, `court`, `hoop`, `demolition_site`, `digger`, `backroom_annex`, `cloth_line`, `bunting`, `mural_east_wall`. About 34 new materials (names in `NEW_MATERIALS`,
  they go to `MATERIALS` with a `# s74-materials` marker so other scenes keep their render cache).
- Sprites: Ines, Teo, Grigor, Mrs. Valdez, Duchess (corgi, 4 facings), Pruitt, TRENCH-E 3 (4 facings), Captain (parrot, 2 frames), leaf particles, laundry-aside barrier pieces, door bridge, bakery smoke.
- Portraits: Ines, Teo (barks only in Ch.1: no portrait yet), Grigor (1 scripted chat: needs a portrait), Pruitt (talks: portrait).
- Interiors: laundromat, back room, bakery, Mia's flat (catalog furniture + new: washer, dryer, soap machine, display case, oven, mattress).
- Audio (later): Old Block theme (warm, accordion / guitar), cable-works hum.

## 12. Cost estimates

**Measured with the real quantizer** (`tools/proposals/s74/tilecount.py`, full map, 24 spp, so render noise inflates it: treat as an UPPER bound; the real
192 spp build de-duplicates better):

| Layer | Unique tiles | Data | Worst 31x21 window (cache = 624 slots) |
|-------|--------------|------|----------------------------------------|
| floor (8 banks) | 10 776 | ~337 KB | **651** |
| objects (7 banks) | 6 695 | ~209 KB | **649** |
| total | 17 471 (City Centre ~25.5k) | ~545 KB + cells (~85 KB each layer) + depth maps (~0.4 MB) | |

- **Risk:** the worst window is slightly above the 624-slot VRAM cache at 24 spp (the dense stretch is Cobble Street with cobbles + washing lines + bunting). Mitigation before building:
  render at 192 spp and re-measure; if still > 600, flatten the cobble noise (bigger stones, fewer cracks), drop bunting on one block, thin the thicket spheres.
- ROM: ~1.3 MB for the map (CC ~2.3 MB) + ~4 interiors (~0.2 MB each) + sprites; far below 32 MB.
- Render time at full quality (192 spp): about 0.6 x the City Centre (~20 min) = ~13 min for the map + ~3 min per interior; the proposal renders at 24-40 spp took ~6 min for the full map.
- Collision: 2036 primitives, 78 occluders in the proposal (CC is higher). Sprites on screen: <= 3 actors + leaves (4) + amber lamp blink (palette).
- Save: `max_maps` 10 -> 16 (5 new maps: `old_block`, `laundromat`, `back_room`, `bakery`, `mia_flat`), new save fields `warmth_ob`, gated-state flags are story flags (no new space). Save version bump needed.

## 13. Build order (each step leaves the game playable)

1. Owner approves layout + look (this proposal); decide the open questions.
2. Engine: gated solids, map table + `max_maps` 10 -> 16 (save version bump), CC east-edge warp pair, `warmth` hook (optional).
3. Scene `old_block` exterior (street, buildings, arch, cable works, sneak lane) + CC warp; full render + tile check; **state A only** (barrier closed): M09's route works, Old Block is walkable but the interiors are still closed.
4. Residents: cast entries (Ines, Teo, Grigor, Duchess, Pruitt, TRENCH-E), PLACEMENTS/ROUTES, barks, portraits; interactables (stall, chess, garden, hoops).
5. Interiors: laundromat (+ stairs to Mia's flat), bakery; shop + odd jobs notice board.
6. M09-M10 scripts, then M13 state C (sprite overlays), Saturday market (M15), Mia's flat (M17).
7. Back room (Chapter 2), cold/warm palette banks, polish, music.

## 14. Open questions for the owner

1. **Where do the cable works live?** Proposed: inside the Old Block map (its west 15 cells), so the City Centre needs no re-render, only an edge warp. Alternative: build them into the CC east end (more faithful "you walk up to a blocked street", but re-renders the biggest map).
2. **Interiors in Chapter 1:** the earlier answer was "minimal, no interiors". Proposed: laundromat, bakery and Mia's flat (M17) enterable, back room only in Chapter 2. OK, or exteriors only first?
3. **Warm/cold:** reserve 2 floor + 2 object palette banks for a per-area warmth blend (needs a build_assets change), or only swap props / posters by flag?
4. **Barrier gap visuals (M13):** barrier built as 4 sprites (gap visible, small sprite cost) vs tiles with a ghost. Proposed: sprites.
5. **Scope of south side:** garden + court as built here (Ines's garden, Ballers court that Gus's "Old Block Rovers" reuse later) in Chapter 1, or leave them fenced / empty until Chapter 2-4? Also the cast table must grow 8 -> 12 for Ines, Teo, Grigor, Pruitt.
