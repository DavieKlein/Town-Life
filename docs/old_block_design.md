# Old Block - design (s74, revision 2 after owner feedback; BUILT in s75: map + laundromat, bakery, Mia's flat, Lane Grocery interiors, gates, barrier sprites; see CLAUDE.md s75 and docs/playtest_s75.md)

Owner feedback: "All OK, warm neighbourhood. It may be BIGGER than the City Centre. More room to walk around. Buildings don't all have to stand next to each other."
Decisions: cable works inside the Old Block map; laundromat, bakery and Mia's flat enterable in Chapter 1, back room in Chapter 2; **no per-area palette blend** (warm
neighbourhood, props / posters swap by flag, VaultTech parts stay cold through their own materials); barrier gap built from sprites; garden and court open in Chapter 1.

Old Block is the poor, warm, close-knit district at the east end of the City Centre avenue; it completes district 1 (M08-M17). Original design, only the *genre* feel of
handheld life-sims is referenced. Story sources: `docs/story_chapter1.md` 3B.2 / 3B.2a / M09-M17, `docs/story_overview.md`, `docs/features_backlog.md`.
Proposal code + renders: `tools/proposals/s74/` (README there). Previews: `tools/proposals/s74/previews/` (revision 2: `r2_*.png`; revision 1 images kept as `1_..5_*.png`).

## 1. Design in one paragraph

You enter from the avenue and meet **cold** first: the VaultTech cable works (barriers, trench, drums, robot, guard, hoarding "SMART CITY COMING SOON"). Behind the **brick arch**
(OLD BLOCK - EST. 1931) the **warm** Cobble Street begins and the neighbourhood opens up: detached houses and shops with gaps, **an alley with Teo's den, a laundromat yard, a small
square with a basin**, a second street, **Baker's Lane**, running south past spaced-out cottages with front yards, a **pond park**, the **community garden**, a **chess plaza**, a **court**,
an **two orchard / allotment blocks** and a **meadow with footpaths**. The street ends at the **fenced demolition site** with the derelict Co-op Hall and the humming NODE 7 hatch. The way in
changes the feeling: first a fence flap and a bush lane (M09), later the front gate (M13).

## 2. Map facts

| Item | Value |
|------|-------|
| Map id | `old_block` "Old Block" (appended to `SCENES`, ids stay stable) |
| Size | **80 x 64 cells** = 60 x 48 m (City Centre 72 x 60 = 4320 cells, Old Block 5120: ~19 % bigger) |
| Image | 2336 x 1344 px (origin_x 1040, origin_y 175; City Centre 2144 x 1272) |
| Open ground | streets, squares, parks, orchards and meadow cover about two thirds of the map; buildings are 9 separate volumes with 3.5-6 cell gaps (City Centre blocks are continuous) |
| Camera rule | faces looking to +y / +x are visible. **Tall things (2-3 storeys) only on the north side of a walkway or west of a N-S walkway**; south / east of walkways only low things (<= 1 storey, hedges, fences, benches, orchard trees). A 6 m house hides ~10 cells of ground diagonally behind it |
| Streets | avenue stub (x 0..14.5, y 18.5..25.5), **Cobble Street** (x 15.7..68, y 19.5..24.5), **Baker's Lane** (x 50..55, y 24.5..62, N-S) |
| Entry from the City Centre | CC `x >= 70.5` strip (y 18..34) <-> OB `x <= 1` strip, y mapped by -4 / +4 |
| Collision | fine grid; **gated solids** (see 8) |

ASCII plan (1 char = 2 x 2 cells; the PNG plan has exact coordinates):

```
        0         10        20        30        40        50        60        70       80
  y 8   ..........  ...[VALD][ALLEY][ LAUNDRO ][YARD ][BAKERY][SQ ][H4]  [H5]   | CO-OP HALL
  y 18  =avenue====|b T A== C O B B L E   S T R E E T =========  [STALL]       |g  site (closed)
  y 28  ..FENCE.THICKET [GARDEN] chess [POND PARK]  ||LANE|| [COURT]            |
  y 40  ..............[ MEADOW,  trees, footpaths ]  [cottages] || [ORCHARD + allotments]
  y 62  ...........hedge....................................
        b = barriers (x 10.5)  T = trench  A = arch  g = closed site gate
```

## 3. Zones (cells)

| Zone | Area | What is there |
|------|------|---------------|
| **A. Cable works (cold)** | x 0..14.5, y 14..34 | hoarding (y 15) with VaultTech posters + gold V, portaloo, 3 + 4 cable drums, orange/white **barrier line x 10.5** with amber lamps + SURVEY IN PROGRESS board, **trench x 11.3..13.3** with a cable, TRENCH-E 3, Guard Pruitt on a chair on a drum (8.6, 19.9), camera pole, grey fence south to the map edge |
| **A2. Sneak route** | x 9..18, y 27..34 | hedge hides the **fence flap** (10.5, 30.2..31.2). Behind it the **bush thicket** with a one-cell lane (10.9 -> 17.0 at y 30.35..31.05, then north x 16.4..17.1 to y 27) that exits just inside the arch |
| **B. Arch** | x 14.5..15.7 | brick pillars + beam, iron sign "OLD BLOCK / EST. 1931" half covered by VaultTech posters (readable on the +x face) |
| **C. Cobble Street** | x 15.7..68, y 19.5..24.5 | 52 cells long (was 35), kerbs, 3 curved lamps (x 19 / 38 / 57), bins, hydrant, newspaper box, flower pots, 2 washing lines + bunting (sparse on purpose) |
| **D. North row, spaced** | facade y 18 | **Valdez house** (16.5..21, balcony + Captain) - **alley** (21..25.5, Teo's den lean-to, barrel) - **Ines's Laundromat** (25.5..34, 3 storeys) - **yard + back-room annex** (34..40.5) - **Bellini Bakery** (40.5..47, Okafor's flat above) - **pocket square** (47..53: stone basin, benches, poster wall) - **row house 4** (53..57.5) - **alley** (57.5..61) - **house 5** (61..65.5) |
| **E. Baker's Lane** | x 50..55, y 24.5..62 | cobbled N-S street, lamps, pavements. West side: **3 detached cottages** (facades +x, y 41 / 49.5 / 57, 1-2 storeys, CC0 Quaternius models, 3-4 cell gaps) with room for front gardens later |
| **F. South-west** | y 26..62 | **community garden** (17..29 x 27..40), **chess plaza** (29.5..35 x 26.5..32, plane tree kept south at (31, 36) so its canopy never hides the street), **pond park** (36..47 x 28..37), **meadow** (17..37 x 41..62: trees, benches, flower beds, footpaths to the cottages and the garden) |
| **G. East of the lane** | x 55.8..68 | **court** (56..67 x 28.5..37.5, two hoops), **orchard + allotments** (56..67 and 68..79 x 40..62: 12 fruit trees, 6 beds, benches, paths) |
| **H. Street end** | x 59.5..68 | **Rosa's stall** (63.2, 22.2), **Teo's door ramp** (60.2, 24.5), steel gate with NOTICE |
| **I. Demolition site** | x 68..80, y 4..34 | orange-railed fence with notices, derelict **Co-op Hall** (big bricks, boarded windows, chained arched door, lintel "OLD BLOCK CO-OPERATIVE 1931"), yellow digger, **NODE 7 hatch** (69, 22.5), rubble, floodlight. Whole site solid (opens in Chapter 5) |

Spaciousness: gaps between buildings are 3.5-6 cells, three E-W / N-S walkways, five open spaces (square, chess plaza, garden, pond park, court) and two green areas (meadow, orchard) to wander.
The rear zone behind the north row is closed except through the alleys, yard and square (their solids are re-opened explicitly).

## 4. Enterable buildings and interiors (cutaway rooms via `std_room`, furniture from the catalog)

| Interior | Size | Layout | Interactables | When |
|----------|------|--------|---------------|------|
| **Ines's Laundromat** (`laundromat`) | 14 x 10 | machines along the back wall, folding table, chairs, soap machine, lost-sock box, notice board, Duchess's bed, "TWO DOLLARS" board, stairs to Mia's flat and a door to the yard | `washer` (wash clothes $2), `seat` x4, `noticeboard` (Old Block odd jobs), soap machine, collectible spot, Ines (talk) | Ch.1 (M09, M17) |
| **Mia's flat** (`mia_flat`) | 7 x 6 | one room, one couch, kettle, window over the street, boxes | `couch` (sleep, M17), `window` | M17 |
| **Bellini Bakery** (`bakery`) | 10 x 8 | counter + display cases, ovens glowing, flour sacks, two tables, stairs (Okafor's flat, blocked) | `shop_bakery` (bread $3, pastries $2-4, coffee), `seat` x4, `oven` (Fun +2) | Ch.1 shop |
| **Back room** (`back_room`) | 6 x 5 | bare walls, mattress, crates, hot plate, bucket; bills envelope at the door | `bed`, `window` | **Chapter 2** (exterior now) |
| Valdez, house 4, house 5, cottages, Co-op Hall | later | - | - | Ch.2+ (Valdez / Biscuit), Ch.5 (Hall) |

## 5. Interactables (positions in `tools/proposals/s74/data.py`; `*` = new kind)

| Kind | Where | What |
|------|-------|------|
| `sign*` | barrier (10.2, 21), arch (14, 22), gate (67.3, 22) | info pages |
| `flap*` | (9.3, 30.7) | before `sneak_route`: "Just a fence. And a lot of bushes."; after: squeeze through |
| `hatch*` | (69, 22.5) reach +1.5 | "A steel hatch. It hums. It is warm. Warmer than the street." |
| `shop_stall*` | (63.2, 23.6) | Rosa's loaf, Orange, Rye loaf, Flowers $3 |
| `chess*`, `garden*`, `hoop*` x2 | (32.2, 28.9), (23, 30), (57.4 / 65.6, 33.5) | watch the game; water the plants (Fun +4, once a day friendship with Ines); shoot hoops (Fitness +, Fun +) |
| `fountain` (existing) | square basin (50, 14.5) | Wash face / Drink water |
| `bench` x4, `bin` x4, `kiosk`, `noticeboard`, `crate` | see `data.py` | existing kinds (garden, court, pond, orchard benches; street / yard / court bins; scratch cards; Mia's poster wall from M13; M10 crates (38.8, 11.5)) |
| RETURN & EARN spots | ~24 new spots (lane gutters, pond, meadow, orchard, court, thicket) | same global cap (7 loose credits) |
| collectibles | 6-8 new spots (Co-op penny in the garden, lost sock, Docks postcard, feather, ...) | `tools/collectibles.py` |

## 6. NPCs, schedules and routes

Cast slots: Ines, Teo, Grigor, Pruitt need talk slots (8 -> 12). Duchess, TRENCH-E, Mrs. Valdez + Captain are barks-only actors.

| Who | Spot / route | When |
|-----|--------------|------|
| Pruitt | chair (8.6, 19.9); after M13 (11, 20.5) with tea | always |
| TRENCH-E 3 | in the trench (12.3, 21.3) | always |
| Ines | laundromat door (32.9, 19.3), inside in the evening | 7:00-21:00 |
| Teo | `teo_round`: arch (15.5, 26.5) -> chess (31, 27) -> square (50, 19) -> stall (62, 24.8) -> yard (36, 17) -> garden gate (23, 26.8) -> court (60, 30) | 10:00-19:00 (waits at the lane exit in M09) |
| Duchess | yard bed (35.8, 16); walks the street 12:00-13:00 | always |
| Grigor | stool (33.1, 28.2) | 10:00-18:00 |
| Mrs. Valdez + Captain | balcony (18.5, 18.8) | always |
| Rosa | behind the stall (65, 21.6) | from M10, 8:00-17:00; Saturday market 9:00-15:00 |
| M13 crowd | Mia (60, 23), Ines (61, 21), Teo (63, 21), Grigor (59, 22), Valdez (58, 22.5), Pimm (60.5, 22) | 9:00 meeting |
| Dr. Okafor | lives above the bakery, never shown | - |

## 7. Mission hooks (M08 - M17)

| Mission | Old Block use |
|---------|---------------|
| M08 | laundromat notice board adds 2 odd jobs once `old_block_open` |
| **M09** | fence (x 9..10, y 26..30) -> flap (10.5, 30.7) -> lane -> exit (16.8, 27) where Teo waits -> arch sign (15.2, 22) -> Valdez balcony (19.2, 21) -> Mia points at her window (28.5, 20.5) -> chess (31, 27) -> walk to Rosa (long street: ~50 cells) |
| M10 | yard crates (38.8, 12.3); stall (63, 22.8) |
| M11 / M12 / M14 | only the walk to and from Old Block |
| **M13** | meeting at the stall (61.5, 22), notices on every wall (poster props swap by flag), barriers moved + Teo's bridge (state C) |
| M15 | optional Saturday market on Cobble Street + the square (stalls from x 40 to 60) |
| **M17** | Mia's flat via the laundromat stairs; back room promised for Chapter 2 |

## 8. The cable works in three states

| State | Flags | Barriers (x 10.5) | Trench | Flap | Lane | Front |
|-------|-------|-------------------|--------|------|------|-------|
| A (start) | - | solid | solid | solid | solid | closed |
| B (after M09 scene) | `old_block_open`, `sneak_route` | solid | solid | open | walkable, half speed, leaf particles | closed |
| C (after M13) | `barrier_moved`, `door_bridge` | middle pieces moved aside with laundry on them | door bridge walkable (x 11.3..13.3, y 21.3..22.7) | stays | walkable | open |

**Decision (owner): sprite-built barrier gap.** The barrier line is NOT part of the map tiles: it is 4 sprites (3 pieces + 1 for the moved state; laundry-draped variants), placed by flag,
so the gap is visible and no second render is needed. Teo's door bridge is one 32x16 sprite. The tile map stays state-A-free at the barrier line (the floor trench stays).
**Engine need (small): gated solids**: `{rect, flag, invert}` rows evaluated on map load and flag change (`field::_refresh_gates`) for lane, flap, hedge pocket, barrier gap, bridge.
**Squeeze effect:** half speed on lane cells, 4 drifting leaf sprites, 2 px camera sway, the player passes behind 3 taller bush clumps (the camera-side rows are kept low on purpose:
at 2:1 isometric anything 0.75 m tall hides about 2.5 cells of ground behind it).

## 9. Warm neighbourhood, cold VaultTech parts (decision: no palette blend)

- **Materials do the work:** warm = terracotta / ochre / rose / teal / blue plaster, red brick, wood, flowers, yellow awnings; cold = `vault_hoard` navy, `vault_cold` grey-blue, orange/white barriers, mesh fence, notices.
  The cold parts are only zone A, the site fence / site and the notices. No extra palette banks and no `warmth` save field (the earlier 2+2-bank idea is dropped).
- **Flag swaps:** posters / notices (M13: orange notices + Teo's counter-posters), laundry on barriers (state C), door bridge, a few props (market stalls, Saturday bunting). These are sprites or tile-free overlays.
- Day/night as usual: lit windows (laundromat, bakery, flats), lamp pools at 3 street lamps, 3 lane lamps, 2 pillar lamps, amber barrier lamps (blink via a palette entry).

## 10. Lived-in, gritty details

Patched cobbles, cracks, weeds, damp streaks, drainpipes, AC units, dishes, window boxes, shutters, stoops, washing lines + bunting, milk crates, chalkboard, hand-lettered signs, mural, scuffed court, scarecrow, rain barrel, door-ramp,
VaultTech posters on the arch, orange notices, mud heaps, tape, cables. Kept sparse on the main street for the tile budget. Later: stray cat, pigeons (arch, stall, chess), laundry sway, bakery smoke.

## 11. New art, props and characters (NEEDS PROPOSAL where visual)

- Scene helpers in `oldblock.py` (move to `scene.py`): `row_house`, `laundromat`, `bakery`, `arch`, `cable_works`, `trench_e`, `pruitt` (placeholder), `plane_tree`, `chess_table`, `rosas_stall`, `garden`, `pond_park`, `court`, `orchard`, `meadow`,
  `cottage` (Quaternius), `demolition_site`, `digger`, `backroom_annex`, `cloth_line`, `bunting`, `mural_east_wall`; ~45 new materials (`NEW_MATERIALS`, to be added with a `# s74-materials` marker so other scenes keep their render cache).
- Sprites: Ines, Teo, Grigor, Mrs. Valdez, Duchess, Pruitt, TRENCH-E 3, Captain, leaf particles, 4 barrier pieces, door bridge, bakery smoke. Portraits: Ines, Grigor, Pruitt (Teo from Ch.2).
- Interiors: laundromat, mia_flat, bakery (Ch.1), back_room (Ch.2). Audio later.

## 12. Cost estimates (revision 2)

Measured with the real quantizer (`tilecount.py`, full 80x64 map, 24 spp):

| Layer | Unique tiles | Data | Worst 31x21 window (cache 624) |
|-------|--------------|------|--------------------------------|
| floor (8 banks) | 15 800 | ~494 KB | 651 (saturated, see below) |
| objects (7 banks) | 8 517 | ~266 KB | **593** (target <= 600; the worst window is the Co-op Hall + fence + digger, 502 unique at 96 spp) |
| total | 24 317 (City Centre ~25.5k; revision 1: 17.5k on the 60x48 map) | ~0.75 MB + cells (~0.1 MB per layer) + depth maps | |

- **How the budget was met:** the first 80x64 draft had 28.4k tiles and object windows of 645. Big areas now use low-contrast materials (`grass_flat`, `slab_flat`, `paving_flat`, flat cobbles with large stones),
  the Co-op Hall wall is one flat brick colour (small bricks cost 643 -> 502 unique tiles in that window), the base slab exists only under the walkable part (not under the unreachable rear zone / east), the site fence mesh is flat, the Co-op Hall uses big bricks, ivy and roof weeds were removed,
  the street gets 2 washing lines instead of 4. Spacious open ground is cheap; dense detail (ivy, fine mesh, small bricks) is what fills the window.
- **Calibration warning:** the floor window saturates at 651/651 in this measurement for the real City Centre junction as well (checked with `windowcheck.py`: CC floor 651/651 at 96 spp, Old Block 647/651), because render noise defeats
  de-duplication in any shaded floor area. So the floor number is not discriminating at low spp; the objects number is (CC objects window: 37 unique, Old Block junction window: 122). Re-measure both layers at 192 spp before building.
- ROM ~2.0 MB for the map incl. depth data (CC ~2.3 MB), + ~0.2 MB per interior.
- Render time at 192 spp: ~1.2 x the City Centre (~25 min) for the map; the proposal's 24 spp full render takes ~7 min.
- 2350 primitives, 101 occluders (CC higher). Sprites on screen <= 3 actors + 4 leaves + barrier pieces (4) + lamp blink (palette).
- Save: `max_maps` 10 -> 16 (new maps `old_block`, `laundromat`, `back_room`, `bakery`, `mia_flat`), save version bump; no `warmth` field any more.

## 13. Build order (each step leaves the game playable)

1. Engine: gated solids, map table + `max_maps` 16 (save version), CC east-edge warp pair, barrier sprites.
2. Scene `old_block` exterior (state A) + CC warp; 192 spp render + tile check (trim detail if the objects window > 600). M09's route works; interiors closed.
3. Residents: cast entries (Ines, Teo, Grigor, Duchess, Pruitt, TRENCH-E), PLACEMENTS / ROUTES, barks, portraits; interactables (stall, chess, garden, hoops, basin).
4. Interiors: laundromat (+ stairs), Mia's flat, bakery; shop + odd-job notice board.
5. M09-M10 scripts, M13 state C (sprite overlays), Saturday market (M15), M17.
6. Cottages' interiors / back room (Chapter 2), polish, music.

## 14. Open questions for the owner

1. Cottages along Baker's Lane are closed shells in Chapter 1 (front gardens, no interiors). OK, or should one of them be a shop (e.g. a tool repair) already in Chapter 1?
2. The long street makes the walk Mia -> Rosa in M09 about 50 cells (~25 s). Fine, or add a bike/skate shortcut (Teo's ramp) later?
3. Do the meadow and orchard carry the RETURN & EARN cans (more spots, same global cap) or stay purely scenic?
