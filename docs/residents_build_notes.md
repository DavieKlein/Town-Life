# Old Block residents: build notes (s76)

Built: see CLAUDE.md "s76". Test shots are not in git (session scratchpad).

Open points / ideas:
- Duchess (animal) and Captain, TRENCH-E 3 have no interaction yet (no bark). A later `bark_*` page or info message could be added through `field::_start_conversation`; `npcs::find` currently skips props.
- Teo's M09 "waits at the lane exit" placement, Pruitt's after-M13 position (11, 20.5) with tea, Ines + Valdez + Grigor at the M13 meeting and Rosa's Saturday market are not placed (story scripts later).
- Captain stands on a perch on the pavement (no balcony elevation in the NPC system).
- Teo has no walk-by barks; Pruitt/Kessler are talkable only with small talk (no mission dialogue yet).
- Small talk gossip rules still use 8 rules, none involve the new residents.
- TRENCH-E's bucket can be cut off at the bottom of the 64x64 frame in the south facing (dig arm is large).
- Phone contacts (tl_phone) only cover talk slot < 8 for call memory; calling the new residents is not enabled.
