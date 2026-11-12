# Playtest s75 (headless, Old Block + whole-dollar deposit)

Tools: `tools/playtest_driver.py` with a `-DTL_DEBUG_POS` ROM, a `-DTL_DEBUG_AUTO_TALK -DTL_DEBUG_BOT=1` story ROM, a `-DTL_DEBUG_CPU` ROM. Screenshots: session scratchpad `oldblock_built/`.

Tested OK: City Centre -> Old Block (east avenue edge, all 4 warp bands) -> works zone -> hedge pocket -> flap -> lane -> exit inside the arch -> Cobble Street ->
back through the lane and flap -> west edge -> City Centre. State C (flags barrier_moved + door_bridge): gap and bridge walkable, barrier sprites move.
All 4 interiors enter / leave cleanly (laundromat <-> Mia's flat stairs, bakery, Lane Grocery); shops work (bakery croissant, grocery menu, Rosa's stall menu);
RETURN & EARN: bag 2 cans + 3 bottles -> "You get $5."; pause line "Bag 0/10   Coins 0". Night lighting and lamp pools fine. New Game prologue starts, no crash.
CPU (`TL_DEBUG_CPU`): idle ~29 %, walking ~29 %, running 24-29 %, sprite tiles peak 346 / 1024. Tile windows: Old Block objects 579 (< 624), floor saturated like the City Centre.

Fixed during the test: stairs warp unreachable (solid ended where the warp began), alleys / pocket square closed by a 1-sub-row rounding bug, bakery door blocked by a flower pot,
bakery arrival blocked by furniture, 2 deposit spots on solid cells, court centre circle rendered black (coplanar faces, floor re-rendered).

Open / known: the flower pot at (45.6, 19.1) still STANDS in the bakery doorway visually (collision removed with `set_solid(..., False)`; move the pot at the next objects re-render);
`playtest_driver goto` often fails to path through the lane (use manual `hold`); the arch hides the trench area from the entry camera angle; no residents / Rosa at the stall yet
(no sprites approved); lane half-speed + leaf particles not built; barrier sprites are drawn behind the player (bg priority 3), fine because the player only passes through the gap;
Old Block missions M08+ do not exist yet, the sneak gate opens while mission X1 is current (temporary rule in `field::_update_gates`).
