> **Owner decision (s82):** approved WITHOUT the workshop and WITHOUT the cinema; yes to everything else (market square, corner shop,
> barber, cafe terrace, loop streets, playground + allotments, garden stays). Not built yet: build later when the owner says so.

# Old Block REV 3 - proposal (s82, nothing built, waiting for the owner)

Files (scratchpad `ob_rev3/`): `layout_plan.png` (current plan with 9 numbered problems | proposed plan), `layout_plan_current_iso.png` (the real current
map at 0.5x with the same numbers), `shots/A_market_square.png`, `B_north_row_west.png`, `C_cinema_east.png`, `D_orchard_row.png` (real renderer, 3x zoom, real
grade + quantizer; also `*_1x.png` = what the GBA would show). Scene: `tools/proposals/s82/rev3.py`; crops: `shots.py`; plans: `plan.py`.

## 1. What feels off today (numbers = markers on `layout_plan.png`)

1. **The pocket square is hidden.** Basin, benches and Mia's poster wall sit behind row house 4: in this projection anything stands in front of what is NW of it, so
   the district's only plaza is not seen from the street. (Found by `tools/interact_audit.py`: the fountain / poster-wall markers lie on the house wall.)
2. **The "park" (pond park + meadow) is a lawn with benches at odd spots** (39, 36.4 is a bench on bare grass): nothing to do there, no reason to go.
3. **Alleys and the yard are dead ends.** After the s81 fix they are gated, so Teo's den, the annex and the yard crates are scenery behind fences.
4. **The north row has no rhythm:** building - 4.5 cell gap - building - yard - building - square - building - alley - building. The street wall keeps breaking.
5. **The garden sits in the far SW corner** behind one small gate, 12 cells from anything else.
6. **Baker's Lane dead-ends at the map edge** (y 62): you walk down and walk back.
7. **The east end is leftover:** orchard + court + second orchard are three green rectangles.
8. **Street clutter:** lamp, pole, cloth line, bunting, bin, pot per few cells, they overlap in the typical camera view (seen in the phone shots).
9. **The cold works zone fills the whole entry** (x 0..16), nothing to see before the arch.

## 2. The proposal (see `layout_plan.png`, right)

Hard rule of the projection (kept): shopfronts only on the NORTH side of an E-W street (facade towards +y) and on the WEST side of an N-S street; everything on the
south side is low. A tall object hides ground NW of it by 3.26 cells (x + y) per metre of height, so nothing above ~2.5 m may stand at the south edge of Cobble Street.

* **A continuous main street.** North row, west to east, no gaps: arch | Valdez house | **Ruiz corner shop** (new, newsagent) | **Ines' Laundromat** | **Figaro barber**
  (new, barber pole) | **Bellini Bakery** | **Cafe Aurora with a deck terrace** (new, tables + parasol on the pavement) | row house 4 with stoop | **THE ROXY cinema**
  (new, red marquee, blade sign, poster cases) | **workshop** (new, roller door) | site fence. 9 frontages instead of 5 + 4 gaps. The terrace and the cinema
  marquee are the "eye-catchers" at the two thirds of the street.
* **A real focal point instead of the second park: Market Square** (south side of the street, x 33.5..49): paved plaza, a **covered market hall** (open on all sides, low
  roof 2.5 m, 10 x 5 cells, stalls with produce under it; Rosa's stall can move in), a **bandstand** at the west end, the stone basin from the pocket square in the middle,
  Grigor's chess table under the plane tree (east), benches in a ring. The hall is set back (y 29..34) so its roof only hides pavement, not the street.
* **Loops, no dead ends:** Cobble Street -> **Mill Lane** (new, x 30.5..33, between garden and square) -> **Orchard Row** (new E-W, y 55.5..59.5, two cottages on its
  north side) -> **Baker's Lane** (cottages + Lane Grocery on its west side) -> back to Cobble Street. The garden gets a gate on the street pavement and one on Mill Lane.
  The alleys disappear (no gates, no dead ends); the annex / "Teo's den" move to the back of Mill Lane in a later pass (or go).
* **East end with a purpose:** a **playground** (swings, slide, spring rider, sandpit) next to the basketball cage, and **allotments** with coloured sheds (the
  orchard becomes 15 low beds + 3 sheds: much cheaper in tiles than trees).
* **Less clutter:** one lamp per frontage joint (5 instead of 8), no poles / cloth lines over the street (bunting only between laundromat and barber).
* Entry: unchanged story props (barrier, trench, TRENCH-E, Pruitt, sewer manhole, arch). The cold zone keeps its size but gets a second, warm glimpse through the barrier gap
  (Valdez balcony and the corner shop awning are visible from the avenue).

Kept as built: laundromat (+ Mia's flat), bakery, Lane Grocery, Rosa's stall (may move into the hall), cable works + sewer manhole, Grigor's chess table, Valdez's
balcony and Captain, the community garden, demolition site. Moved: pocket-square basin (-> market square), chess (-> square), pond park (removed), annex (later).

## 3. What each preview shows

* **A_market_square:** hall, bandstand, plaza, plane tree, garden gate and the north row seen from the square.
* **B_north_row_west:** corner shop, laundromat, barber, bakery, cafe terrace in one view: the continuous frontage.
* **C_cinema_east:** cafe terrace, row house, cinema marquee + blade sign, workshop, site fence, playground swings.
* **D_orchard_row:** Mill Lane / Orchard Row corner with two cottages, the hedge edge and the meadow (rough sketch: cottage models from the Quaternius pack as today).

## 4. Tile budget (honest)

Now (full quality, s81 build): old_block floor 14771 unique tiles (worst 31x21 window 651), objects 7342 (worst 549); the engine window is 31 x 18 cells and the cache has
624 slots. The south zone I would replace (pond park, meadow, orchard, thicket remnants) is flat grass = cheap; the north row becomes denser: +5 frontages (about 350
unique object tiles each, like the bakery) = roughly +1700 objects tiles (+25 %) and a worst street window that is likely 30..90 tiles above today. That is the risk:
the street window is already the maximum (651 of ~720 allowed in the 31x21 measure). Mitigations: same window / awning rhythm on every `shopfront` (de-duplicates), signs with
2-3 words, no per-frontage drainpipe detail, plaza_stone and cobble are repetitive (cheap). I would measure the real full-quality number before building and cut the
workshop or the terrace if the window goes over. The crop renders here are 48 spp: noise makes every cell unique, so `tilecount.py` saturates at 558 (= 31 x 18) in every crop and tells nothing; a real number needs a full-quality (192 spp) render of the street, about 25 min per layer.

## 5. Cost / what has to change in the game if approved

* Re-render Old Block (floor + objects, about 55 min each on 4 cores) + the ID / depth passes; no new interiors needed yet (new shops are facades; the cinema, cafe,
  corner shop and barber become enterable in later rounds; opening hours table already exists).
* `scene_oldblock.old_block()` rewrite from `rev3.py`, new solids / gates (barrier, bridge unchanged), warps for the new doors later.
* `interactions.py`: move fountain, chess, benches, poster wall; add market stall / hall interactions (buy produce), playground (Fun), cafe terrace seats.
* `cast.py`: re-place Grigor (chess), Rosa (hall), Teo's route (Cobble Street -> Mill Lane loop), Duchess; `critters.py` pigeons into the square.
* Estimate: 1 session for scene + data, 1 for interiors of the new shops.

## 6. Questions for the owner

1. Market square (covered hall + bandstand) instead of the pond park: yes / different idea (pub terrace, canal quay)?
2. Which new frontages do you want: corner shop, barber, cafe terrace, cinema, workshop (any can be dropped to save tiles)?
3. Playground + allotments for the east end OK?
4. Should the community garden stay in the SW corner (with the new Mill Lane gate) or move behind the houses as allotments only?
5. The annex / "Teo's den" alley props: drop them or give them a place on Mill Lane?
