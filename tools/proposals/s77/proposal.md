# s77 proposal: the Old Block sneak route goes through the SEWER (design only, nothing added to the game)

Owner request: replace the fence flap + bush lane (M09) with a trip underground: manhole in the City Centre -> ladder down -> sewer tunnel -> ladder up -> manhole on the
Old Block road. All previews were made with the real renderer (`tools/blender_render.py`, V1 Soft), the real quantizer (`build_assets.convert_layer`, 8 floor / 7 object
banks, grade + sharpen), the real player / Teo sprites and the real HUD strip. Scripts: `sewer.py` (scenes + materials, registered in-process only), `compose.py`,
`shots.py`, `sheets.py`, `render.py`. Rebuild: `S77_SPP=192 python3 tools/proposals/s77/shots.py OUT && python3 tools/proposals/s77/sheets.py OUT`.

## 1. What the owner sees (images)

| Sheet | What |
|-------|------|
| `sheet1_entrances.png` | entrance variants A and B in the City Centre, player composited, cue bubble |
| `sheet2_sewer_map.png` | the whole sewer map at 1x and a 3x crop (nook, bridge, east ladder) |
| `sheet3_sewer_screens.png` | six real 240x128 game screens inside the sewer |
| `sheet4_transition.png` | 8 mock frames: manhole menu -> crouch -> fade -> sewer ladder -> climb -> white fade -> Old Block |
| `sheet5_exit.png` | the Old Block manhole, cover slid aside (Teo waits) and cover closed |

## 2. Entrance in the City Centre (two variants)

- **A - crooked road manhole at the east end of the avenue** (66.4, 27.6), south lane, 4 cells from the "OLD BLOCK >" sign. The cover sits a little crooked with a dark crescent,
  a traffic cone stands next to it and a chalk arrow on the asphalt points at it (Teo's work; he marks his routes with chalk). Before M09 the A menu only says
  "Just a manhole. Someone drew an arrow next to it." (the same trick as the old "Just a fence. And a lot of bushes."). After M09: "Lift the cover, climb down".
  Cheapest to build: the City Centre already has a manhole at (62, 27) (kit `Prop_ManholeCover`), so the cone + chalk arrow can be two small flag-driven sprites and the
  City Centre does **not** have to be re-rendered.
- **B - Water Board hatch on the river walk** (58.5, 49.9), between the fountain square and the railing, near the closed bridge. A rectangular steel hatch, lid swung up
  (west hinge), ladder rails and a cut padlock; a "WATER BOARD - AUTHORISED ONLY" sign. More hidden, a longer walk (about 55 cells from the avenue), and thematically
  it is a hook for the Docks later (the same water system). Needs a City Centre re-render (hatch + sign are baked).

**Recommendation: A** for M09 (it is on the way: Mia leads along the avenue east exactly like the fence route did, and the east end is where the player already looks at the
cable works). B stays a possible second entrance in Chapter 2 (the tunnel could get a third ladder towards the Docks).

## 3. The sewer map (`sewer`, 30 x 9 cells, indoor-style cutaway like our interiors)

- Back wall (y 0) in dark brick with corbelled springing of a barrel vault, pilasters, a green water pipe, a rust pipe, caged amber wall lamps, and the **orange VaultLink cable**
  (AURUM Trunk 7) running along the wall and up both shafts: it is the line the cable works are laying, so the player literally follows the story's cable.
  The west end wall is a cross-section of the vault (arched top edge); it is the cutaway: the camera cannot see the ceiling.
- Water channel (murky green-grey, the real `water` material family, calm), brick channel wall, walkways on both sides, two iron grate foot bridges.
  A **collapsed piece of back walkway** (brick pile, broken pipe, hazard tape) at x 13..16.4 forces a short detour: bridge 1 -> front walkway -> bridge 2, so the walk is
  not a straight corridor (about 10-12 s walking, about 6 s running).
- **Two round brick shafts** with an iron ladder, light falling down from the street, pool of light on the floor: west (2.4, 0) = entrance from the City Centre,
  east (27.4, 0) = exit to Old Block, painted "OLD BLOCK >>>" on the wall beside it. A "WATER BOARD No. 4 1931" brass plate (the year of the Co-op Charter).
- Details: rats (3, tiny dark blobs at GBA size), drips and an outfall pipe with a slime streak, puddles, foam on the water, a crate, a bucket, a coil of cable, daylight
  stripes from a street grate on the front walkway (that spot is where a Pruitt bark can fire: "(muffled, from above) I see nothing. I'm doing my crossword.").
- **Mothball's nook** (x 21.2..25.2, back walkway): brick niche with lintel and keystone, swept clean stones, two brass hooks, a dead string of fairy lights and a small hanging
  "CLOSED" sign with a moon. Empty for now; at 00:00-00:30 it becomes his stall (see 5).
- Collision plan: walkways, bridges, shaft floors walkable; channel, collapse, crate, bucket, walls solid. Warps: ladder foot (2.4, -0.3) -> City Centre manhole, (27.4, -0.3) -> Old Block manhole.

## 4. Exit in Old Block (Cobble Street, 4 cells inside the arch)

Manhole at (19.4, 22.6): open street between the arch and Valdez's house, nothing hides it, 20 cells west of Ines's laundromat. Open state: dark well, iron cover slid aside, ladder rails
poking out; closed state: cover with a lifting eye. In the game the cover/hole are two small sprites (closed cover baked or a sprite): the opening is cheap and needs no re-render.
Teo waits next to it (his M09 "waits at the lane exit" moves here, as does the Valdez / arch sequence that follows).

## 5. Transition (cheap) and Mothball

- **Tier 0 (no new art):** A -> "Lift the cover, climb down" -> player walks to the cover (`player::approach`) -> existing `pickup` crouch (about 25 frames) while two sprites swap
  (hole disc appears, cover sprite slides aside) -> existing fade to black -> sewer, standing at the ladder foot -> same in reverse at the east ladder: fade, arrive beside the open Old Block manhole.
  Mocked in `sheet4_transition.png` frames 1-3, 4, 8. A short clank sfx later.
- **Tier 1 (optional, tiny art):** a 4-frame back-view `player_climb` sheet (32x64, hands up alternately, about 1 KB) used on the ladder: the sprite rises 40 frames
  along the rungs while the screen fades to white (frames 5-6 use the n-walk frames as a stand-in; frame 7 = head and shoulders coming out of the hole, white fade).
- **Mothball:** progression.md has him in a shop room reached by the loose lid in the fountain square at 00:00-00:30. Proposal: the nook IS his shop (no extra room):
  he hangs the lights and sets up his tray (bathtub bench, hammock between the pilasters later), and the fountain-square lid at midnight is just another way down to the west ladder
  (then the player walks 20 cells to him: part of the fun). Outside 00:00-00:30 the niche is dark and the "CLOSED" sign hangs there ("Locked from below" becomes the sign).
  The sewer map is a natural place for his "Pipe Whisper" clue after M42 (the cable runs right past the nook). Needs the owner's yes (see questions).

## 6. How it fits M09 and the story

- **Who tells the player:** Mia leads (as now). New pages: at the cone: MIA| "Not that way. Follow me." / crouch: she lifts the cover: MIA| "It's a "survey gap". Teo surveys it every day." ->
  {NAME}| "That's a manhole." / MIA| "Ladies first. Mind the rats. Don't name them." In the tunnel she walks ahead (script, no input): a Pruitt bark through the street grate, TRENCH-E's
  rumble overhead, the cable on the wall ("That's Vault's cable. It goes all the way to the Hall."). At the east ladder TEO's head pops out of the open manhole:
  TEO| "Boss! Welcome to the secret entrance. It's secret. Don't say it." Then M09 continues unchanged (arch sign, Valdez, chess, walk to Rosa).
- **Before M09:** the manhole is inert (hint text only); Pimm's gossip rule `sweets_pimm` ("the drains smell of toffee after midnight") already hints at the sewer.
- **The old fence-hole / bush-lane route is removed**: no flap, no lane, no squeeze effect (it was never implemented in code). The chain-link fence and the thicket stay as plain
  solid scenery, so the Old Block map does **not** need a re-render for that; only the three `sneak` gate rects (`gate_id::sneak`) and the `flap` interactable go away.
  The `flap` text becomes plain "Just a fence." for good. The flag `sneak_route` is **reused** as the sewer flag (all 64 story flags are used); mission X1 (sandbox) opens the manhole too,
  like it opens the lane now.
- **Gating:** after M09 the sewer is usable any time of day, in both directions, and stays usable after M13 (the front opens), so it becomes a secret shortcut and the home of
  Mothball. Pruitt and TRENCH-E ignore it ("I never see anybody."). Optional flavour cost: Hygiene -3 on every climb out ("Ines washes leaves"; the old route had no cost) - owner call.
- **Replay / extras for later:** RETURN & EARN spots in the tunnel (same global credit cap), a collectible (lost ring), rats as non-interactive ambience, optional second ladder towards the Docks (B) in Chapter 2.

## 7. Technical notes (for the later build)

- New map `sewer` (map ids: 14 -> 15, `max_maps` 16 is enough, no save version change). Interactable kind `manhole` (menu: lift the cover / leave), warps in both directions.
  Own palettes (indoor; no day/night).
- Tile budget (real quantizer, `tilecount.py`): floor 1250 + objects 1543 unique tiles (about 90 KB of tile data, ROM about +0.15 MB with cells and depth), worst 31x18 window 465 / 446 of the 624-slot cache: comfortable. A 192 spp render of the map takes about 4-5 min.
- The City Centre variant A and the Old Block exit need no re-render if the cone, chalk arrow, hole and cover are sprites over the existing manholes / a baked ring; the previews here
  are fully baked for the look. Variant B and a baked Old Block manhole need one re-render of that map.
- `blender_render.py` / `scene.py` are unchanged; the proposal materials (`sw_*`, `water_sewer`) are registered in-process and would move into `scene_sewer.py` with a `# s78-materials` marker.

## 8. Decisions / questions for the owner

1. Entrance **A** (road manhole near the avenue end) or **B** (river-walk hatch)? (Recommendation A; B maybe later for the Docks.)
2. Is the **tunnel feel** right (cutaway tunnel with arched end wall, caged lamps, orange cable)? Wetter / greener / more rats, or cleaner?
3. Mothball: the **nook is his shop** and the fountain-square lid just leads down to the same tunnel - OK?
4. Hygiene -3 when climbing out of the sewer: yes / no?
5. Climb transition: **Tier 0** (fade only) or **Tier 1** (small climb animation)?
6. Keep the bush thicket and chain fence as plain scenery in Old Block (no re-render) - OK?

## 9. Weak spots (honest list)

- The vault is only *implied*: the camera cannot see a ceiling, so the barrel vault shows as corbelled springing on the back wall and as the arched cross-section of the west end wall.
- The two round shafts read a bit like silos beside the wall, their top band is nearly white, and the light pools are flat banded discs (no real beam; a translucent beam would need a sprite).
- Rats are 5-6 px dark blobs at game size; the CLOSED sign, brass plate and "OLD BLOCK >>>" paint are only readable at 3x. The cable and pipes read well.
- The front walkway is empty and the out-of-map corner is black, like every cutaway room.
- Old Block exit: the open state reads as "cover aside + dark well"; ladder rails are only 1-2 px. A baked-in ladder or a warm glow from below would help if the owner wants it clearer.
- Hatch B: the opening is dark on dark paving; the lid and rails make it readable but it is the less obvious of the two.
- Previews are quantized per crop (own palettes), the real map would share the whole-map palettes, so colours can shift slightly. The pop-up menu in sheet 4 and the hole/cover sprites are approximations (drawn with PIL), the climb frames reuse the n-walk frames as a stand-in for the Tier 1 climb animation.
