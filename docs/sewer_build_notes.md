# s77 sewer route: build and playtest notes

Design: docs/old_block_design.md section 10, CLAUDE.md "s77". Proposal: tools/proposals/s77/proposal.md.

## What was built
- Map `sewer` (id 14): `tools/scene_sewer.py`; render with `python3 tools/build_assets.py --only sewer --no-actors` (about 12 min at 192 spp). Floor 1250 + objects 1548 unique tiles, worst window 511 / 460.
- `manhole` / `ladder` interactables, `src/tl_field_sewer.cpp`, `state::climbing`, `player_climb` sheet (`tools/blender_climb.py`), map sprites frames 3-6, route flag `sneak_route`
  (set by the sandbox mission X1 in `_update_gates`), Hygiene -3 on arriving at a manhole. `gate_id::sneak` and the flap interaction text are gone.
- Not in the game: M09 cutscene (Mia leads, Teo pops out), sound effects, Mothball (nook empty, CLOSED sign; keep x 22.0..24.4 / y 1.0..2.4 free for a stall and (23.2, 0.9) for him).

## Playtest (headless mGBA, `-DTL_DEBUG_POS` build; screenshots in the session scratchpad `sewer_built/`)
- Closed state (flag not set): City Centre (`01_closed_a/b.png`) and Old Block (`50_ob_closed*.png`): closed cover, cone + chalk arrow, info "The cover is stuck."
- City Centre -> open manhole (`02_open.png`, `02_menu.png`) -> crouch (`03_crouch*.png`) -> fade -> climb down (`sheet_down.png`) -> west ladder foot (2.38, 0.94).
- Whole tunnel walked with `goto`: back walkway, bridge 1, front walkway, bridge 2, back walkway, nook, east ladder (`sheet_walk1.png`, `20_nook.png`, `21_east_cue.png`); the collapse and channel block, no goto timeouts on the route.
- East ladder -> climb up (`24_up*.png`) -> Old Block manhole (19.38, 24.12), Hygiene 79 -> 76 with the red "-" HUD marker (`25_ob_arrive.png`).
- Old Block manhole -> crouch -> east ladder foot (`sheet_ob.png`); B during the crouch cancels (stays in Old Block, nothing consumed).
- Night (22:00) at both manholes: sprites follow the day/night palette (`sheet_night.png`).
- CPU build: peak sprite tiles 434 used / 590 free, average CPU 18-31 %, 3 missed frames at the map load, 0 while walking in the sewer.

## Not verified
- On a real phone / Lemuroid, the GitHub Actions build, and a full New Game run through the prologue to X1 (the saves were made with `tools/make_save.py`).
- No click / clank sound; the climb is silent.
- The sewer was only seen at the sizes of the real game screen; the shaft interiors are mostly off screen (camera clamp), the beam of light on the shaft wall is only partly visible.
