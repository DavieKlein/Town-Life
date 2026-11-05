# Features backlog (owner-approved list, s63)

Own designs only: never copy The Sims / The Urbz screens, objects or wording. Numbers refer to the owner's list.
Status: **now** = built in s63 (code/text only), **proposal** = mock-up made in s63, waiting for approval (no ROM art before that),
**later** = recorded, not started.

| # | Feature | District 1? | Status |
|---|---------|-------------|--------|
| 1 | **Social** need | yes | logic **now** (`needs::social`, saved, pause line); HUD 6th slot = **proposal** |
| 2 | **Showers** (Hygiene; sink hands + fountain face exist) | yes | **proposal** (placement); build after approval |
| 3 | **Sickness** + doctor's practice + hospital + bills by post | practice yes, hospital later | **proposal** (doctor plan); logic later |
| 4 | **Clothing / outfits** in the wardrobe, NPC reactions, dress codes | later (needs sprite variants) | later |
| 5 | **NPCs walk around** with routines | yes | **now** (routes, idle frames sliding); walk frames later |
| 5b | **Pets** (buyable, placed in your home) | no | later (with homes / Old Block) |
| 6 | **Gifts**, per-NPC favourites | yes | **now** |
| 7 | **Phone** (calls/texts, meet-ups, odd jobs, food delivery) | yes | **proposal** (UI) |
| 8 | **Gossip** between NPCs | yes | **now** |
| 9 | **Furniture store + online ordering** (catalog `tools/furniture.py`) | later | later (needs a home first) |
| 10 | **Collectibles** (sets with rewards) | yes | **proposal** (3 sets, sprites, collection screen) |
| 12 | **Scratch cards / lottery** at a kiosk | yes | **now** |
| 13 | **Weather** (rain, puddles, umbrellas, Fun -) | later | later |
| 16 | **Events** (Saturday market in Old Block, street party, protest against VaultTech) | Old Block | later (with Old Block) |

## Built in s63

- **Social** (`tl_needs.h`): 0..100, starts 60, -0.05 per game minute. Small talk +3 (liked topic +5, disliked +1), first hello of
  the day +2, gifts +5 (favourite +8). Below 20 ("lonely") Fun gains from activities are halved. Not a HUD bar yet: the pause screen
  has a sixth line. Saved in `save_data` (carved out of the spare bytes, version unchanged; old saves start at 60).
- **Gifts**: Flowers $3, Chocolate $2, Hot sauce $2, Cookies $2, Newspaper $1 (`GIFTS` in `tools/story_data.py`). Sold under the
  "Gifts" row of the Corner Market (Flowers, Chocolate, Cookies, Newspaper) and the diner (Hot sauce, Cookies); the newspaper boxes
  at the bus stop sell Newspaper too. The VaultMart kiosks do not sell gifts (robot voice only). Inventory: 5 counters, max 9 each.
  In small talk the menu shows **Give a gift** (while you carry one and have not given this NPC one today): pick an item (3 per page,
  "More..." / "Never mind"). Reaction per NPC (`NPC_INFO`, one letter per gift): favourite +10, likes +4, neutral +1, dislikes -3
  friendship, portrait expression, once per NPC and day. Favourites: Mia chocolate, Rosa flowers, Dex cookies, Pimm newspaper,
  Lou hot sauce.
- **Gossip** (`GOSSIP` in `tools/story_data.py`, lines in `tools/dialogue_src.txt` `gossip_*`): a small-talk topic or a gift is noted;
  one game day later the hearer brings it up right after the greeting (a dialogue node with a friendship effect), once per rule.
  8 rules: complain to Mia -> Lou (-3), compliment Mia -> Rosa (+3), joke to Lou -> Mia (+2), gossip with Pimm -> Rosa (+1), flowers
  to Rosa -> Mia (+3), chocolate to Mia -> Pimm (+2), music with Rosa -> Lou (+2), work with Lou -> Pimm (+2).
- **Wandering** (`cast.py` `ROUTES`, 12th element of a placement): Pimm paces round the pond path (park) and between the library
  shelves, Mia along the diner's east wall. They use the idle frames (a 1 px bob) because the NPC sheets have no walk frames; walk
  frames need an actor render per NPC (8 facings x 8 frames) and VRAM, later. They wait 3-8 s at each point, stop for the player and
  during talks, menus and cutscenes. Cross-map routines (walking to work) are later.
- **Scratch cards**: interactable `kiosk` at the newspaper boxes (45.5, 32.4) in the City Centre: $1, 70 % nothing, 20 % $2, 8 % $5,
  2 % $20, three symbols shown in an info panel, max 3 per day (RTP 0.60).

## Decisions and design notes for the later features

- **Sickness (3)**: if two or more needs stay red (below 15) for too long (a few game hours) you get ill: cough, slower walking,
  faster Energy decay. Cure: rest (bed / bench) plus medicine from the doctor or pharmacy. **Doctor's practice in district 1** (small,
  Old Block when it exists, else a City Centre building: see the s63 proposal); a **hospital in the city** later for serious cases.
  Treatment costs money. **Bills by post**: once you have a home, an **envelope lies inside at the entrance**; A opens it -> bill
  -> pay within N days or a penalty (late fee, then collection). Needs the housing ladder first.
- **Clothing (4)**: outfits in the wardrobe (sprite variants of the player, same palette tricks as the V2 look), NPCs comment, some jobs
  need a dress code (e.g. the diner apron, a clean shirt for the notice-board jobs).
- **Pets (5b)**: NOT now. Later buyable and placeable in the player's home (and visible in the furniture catalog style).
- **Phone (7)**: friends call/text for meet-ups and odd jobs; order food delivery. UI proposal in s63.
- **Furniture store / online (9)**: the catalog `tools/furniture.py` already has price, category, quality and footprint; a shop UI and
  delivery come with the first home.
- **Collectibles (10)**: sets with a reward when complete; 3 sets planned for district 1 (old city coins, lost postcards, VaultTech flyers
  to tear down). They twinkle like the can pickups; collection screen in the pause menu. Proposal in s63.
- **Weather (13)**: rain (palette dimming + particles), puddles, umbrellas, Fun -; later, after the day/night work is done on the phone.
- **Events (16)**: Saturday market in Old Block, street party, protest against VaultTech: with Old Block and the chapter scripts.
