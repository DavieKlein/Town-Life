# Features backlog (owner-approved list, s63)

Own designs only: never copy The Sims / The Urbz screens, objects or wording. Numbers refer to the owner's list.
Status: **now** = built in s63 (code/text only), **proposal** = mock-up made in s63, waiting for approval (no ROM art before that),
**later** = recorded, not started.

| # | Feature | District 1? | Status |
|---|---------|-------------|--------|
| 1 | **Social** need | yes | **built s64** (HUD variant A: six slim slots, Social = two speech bubbles) |
| 2 | **Showers** (Hygiene; sink hands + fountain face exist) | yes | **built s64** (public toilet cubicle, $1) |
| 3 | **Sickness** + doctor's practice + hospital + bills by post | practice yes, hospital later | **built s64** (City Clinic, faint, sick, debt); bills by post + hospital pending |
| 4 | **Clothing / outfits** in the wardrobe, NPC reactions, dress codes | later (needs sprite variants) | later |
| 5 | **NPCs walk around** with routines | yes | **now** (routes, idle frames sliding); walk frames later |
| 5b | **Pets** (buyable, placed in your home) | no | later (with homes / Old Block) |
| 6 | **Gifts**, per-NPC favourites | yes | **now** |
| 7 | **Phone** (calls/texts, meet-ups, odd jobs, food delivery) | yes | **built s64** (SELECT; contacts, messages, order food); odd jobs by text later |
| 8 | **Gossip** between NPCs | yes | **now** |
| 9 | **Furniture store + online ordering** (catalog `tools/furniture.py`) | later | later (needs a home first) |
| 10 | **Collectibles** (sets with rewards) | yes | **built s64** (3 sets x 4, real 3D props, collection screen) |
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
  -> pay within N days or a penalty (late fee, then collection). Needs the housing ladder first (ladder: lent back room -> studio -> loft -> apartment -> penthouse; an envelope at every home's entrance; see docs/story_overview.md).
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

## Built in s64 (needs owner approval of the new art before main)

- **HUD variant A**: six slim slots (Hunger, Energy, Hygiene, Fun, Bladder, Social), 28 px wide at pitch 30 from bg x 62, 20 px bars
  (`graphics/hud_bar.bmp`, `hud_sprites.build_hud_bar`). Social is a real bar (decay and gains from s63). Clock / money panel unchanged.
  Small icons at the top right: a blinking envelope (unread phone message) and a green sick face (while sick).
- **Phone** (`tl_phone.h/.cpp`): **SELECT** while walking opens it (there is no pause-menu entry: the pause menu is full at 5 rows and
  SELECT was free). The handset slides up from the bottom right (112 x 120 px panel, Paper / Night style, bold 9 px font):
  - **Contacts**: everybody you have met (Mia, Rosa, Dex, Pimm, Lou, Dr. Okafor). A call shows a meet-up line (morning / afternoon),
    friendship +1 and Social +2 once per person per day.
  - **Messages**: 8 texts (Mia, Lou, Pimm, Rosa, Dex, a VaultTech spam message, two from the clinic: advice after your first faint and an
    open bill). Delivered when their condition is true after 8:00; unread ones have a `*` and the envelope blinks on the HUD.
  - **Order food**: Pizza slice $8 (Hunger +35 Energy +5 Fun +3), Burger menu $10 (+50 / +10 / +5, Bladder -3), Salad box $7 (+28 / +6 / +2),
    Iced tea $5 (Energy +12 Fun +4 Bladder -8). Pay now, it arrives 30 game minutes later wherever you are and you eat it on the spot
    (shops are cheaper: Ready meal $5, Burger $6). One order at a time; saved (`delivery_item`, `delivery_due`).
- **Collectibles** (`tl_collect.h/.cpp`, `tools/collectibles.py`, `tools/blender_props.py`): 12 props rendered in Blender (same camera, sun and
  sharp style as everything else): Old City Coins (copper penny, silver crown, brass ring coin, pewter token), Lost Postcards (mountain
  lake, sunset beach, night skyline, lighthouse), VaultTech Flyers (gold header, black header, crumpled, folded). 16x16 game sprites with a
  twinkle (one sparkle pixel / small plus every 30 frames), 32x32 icons on the collection screen. Fixed spots in the City Centre (park,
  fountain square, river walk, pavement ends, plaza, road works); picking up reuses the 1.2 s bend-down animation and the "A" cue. Found
  items stay gone. **Pause menu > Collection**: one page per set (left / right), icons dark until found.
  Set rewards (paid when the 4th item is found): Coins $10 + Mr. Pimm +6 friendship; Postcards $5 + 1 City Coin + Mia +5; Flyers $8 +
  Rosa +6. Saved (`collect_mask`, `collect_paid`).
- **Shower** in the public toilet (replaces the mop / bucket / broom corner, one bin, sink and WC stay): cubicle with glass pane, curtain,
  chrome head, valve and a coin box. A at it: "Take a shower ($1)": Hygiene to 98 over 6 s (B cancels, partial gain stays), Fun +2.
  Animation `player_shower` (64x64, 8 facings x 4, blender_acts `shower_pose`: hands scrubbing the hair, water streaks).
- **City Clinic** (new building on the brick lot north of the avenue, x 34.7..38.9, facade y 18; interior map `clinic` 13 x 9): waiting
  chairs and sofa, reception counter (Dr. Okafor behind it 8:00-20:00), medicine cabinet, exam corner (couch, basin, scale, screen).
  Reception menu: **Check-up ($8, $13 with medicine when sick)**, **Pay the bill**, Talk to the doctor, Leave. **Dr. Okafor** is a new
  original character (cast sprite, portrait with 5 expressions, face pass, small talk, favourite gift: cookies).
- **Sickness**:
  - A need that stays at 0 (Hunger, Energy, Hygiene or Social) for **60 game minutes** (not while asleep) makes you **faint**: fade out,
    card "You fainted...", you wake on the clinic's exam couch two hours later (needs patched up: Hunger +45, Energy +45, Hygiene +12,
    Fun +6, Social +10, Bladder +10), Dr. Okafor explains, the **care fee is $20**: taken from your pocket if you have it, otherwise a
    **debt** (shown in the pause screen as "Owe $20", a once-a-day reminder after 8:00 and a phone message). Pay at the reception desk.
  - Two or more needs below 15 for **180 game minutes** make you **sick** (HUD sick icon, "SICK" on the pause screen): walking at 80 %,
    Energy -0.05 more per minute, a cough message every ~150 game minutes. Cured by a check-up with medicine ($13), a faint treatment, or
    **8 hours of sleep** (bench or bed).
  - **Bills by post (pending)**: once the player has a home an envelope should lie at its entrance; until then the bill is paid at the
    reception desk and reminded by message / pop-up.

## Progression, secrets, free play (s68, docs only)

Design in **docs/progression.md**: tiered upgrades (skills I-V, 13 City Coin perks, type-star passives, buffs, caps), skill sweets from the sewer seller Mothball (secret 1 of 12), free play after the credits
(exclusive shops, vintage vehicles, Legend title, daily errands, the penthouse showcase), the pause-menu Status screen (reputation, skills, People with friendship and bios, perks, Doors) and skill gates.
Nothing is built; all new art/UI is NEEDS PROPOSAL. Also new in s68: the VaultLink cable works at the Old Block arch (`docs/story_chapter1.md` 3B.2a) and the story-driven Demolition Countdown (`docs/story_overview.md` decision 13).

## Owner notes to record (s68, not built)

### 1. Vehicles ladder (small vehicles gained through the story)

Owner list: kick scooter -> skateboard -> fatbike/bike -> motor scooter -> hoverboard. The old "car" idea is out of the story; it survives only as a post-game luxury (`docs/progression.md` 3.1, "Greenie").
Speed bonuses are relative to base walking speed, are a mounted speed of their own (they do not stack with the +25 % walking cap, the best owned vehicle counts) and replace the old plan of "bike -> scooter -> car".

| # | Vehicle | Story placement | How you get it | Speed | Notes |
|---|---------|-----------------|----------------|-------|-------|
| 1 | **Kick scooter (step)** | Chapter 2, after M19 Box Clever | Bo-Ra lends you the Docks' battered kick scooter ("Gerald's little brother") as a work tool; it becomes yours when you finish M20 | +15 % | the Docks are big; also used on the avenue |
| 2 | **Skateboard** | Chapter 2, M26 Big Wall reward | Teo gives you a board he re-glued, "boss, don't skate on the mural" | +20 % | Teo's ramp door is the same door as Teo's Bridge; a few trick animations as joke only |
| 3 | **Fatbike / bike** | Chapter 2, M27 Two Wheels | Teo's guy sells it for $45 (existing plan) | +30 % | the existing bike sprite proposal becomes the fatbike |
| 4 | **Motor scooter "Bella"** | Chapter 4, after M49 Truce (Sal fixes it at the Docks bike shed with Gus's ex-club funds) | buy for $120 (or free for Techies star 3 + Ballers star 2); sells again if the player wants | +45 % | the vintage scooter of the earlier free-play idea is this one now |
| 5 | **Hoverboard** | Chapter 5, after M63 Four Keys (Nadia and Pip build it for the Gala getaway), or Techies star 4 | reward, not for sale | +60 % | hovers 4 cm, silent, pigeons are suspicious; the top of the ladder |

Rules: **cannot ride indoors** (auto-dismount at every door; the vehicle waits outside), nor on the bush sneak path, stairs, crowded events (Saturday market, march, Block Party: walk only), in the sewer, on the Docks' narrow
planks and during cutscenes. Vehicles are shown as a rider sprite per facing (NEEDS PROPOSAL for each: 5 vehicles x 8 facings, riding idle + ride cycle; one shared palette per vehicle). A quick-switch (hold L) picks the vehicle if more than one is owned.
Energy: riding costs 30 % less Energy per distance than walking (a reward for getting one); the hoverboard 50 % less. Running (B) still works on top: ride speed x run factor. The earlier Chapter 2 note "Bike: +30 %" stands.

### 2. Needs the owner wants on the HUD (recorded as given)

Owner list: **Hunger (food), Energy (shown with a bed icon), Hygiene / showering, Social, Fun, and a new need "Home" (being at home / comfort).**
Current game: Hunger, Energy, Hygiene, Fun, **Bladder**, plus Social (not a bar yet; HUD variant A shows six slots). The owner's list mentions both "showering" and "hygiene" (read here as one need: Hygiene, icon = shower head) and does not mention Bladder.
**Open question for the owner (the main session asks):** does **Bladder stay** as a need (toilet, accident, park WC, drink penalties are built and tied to story/clinic text), or does it go and become hidden (only an occasional "need to go" nudge)?
HUD budget: seven bars do not fit the 240 px bar (variant A uses 28 px slots at pitch 30); options: keep six slots (Hunger, Energy-bed, Hygiene, Fun, Social, Home) and fold Bladder in as a hidden need with a warning icon, or shrink the slots to 26 px / two thin rows. NEEDS PROPOSAL (HUD mock-up) before building.

**How a "Home" need could work (design idea):**
- 0-100 like the others (100 = fine). It measures "I have a place that is mine". Decays slowly **away from home** (about -0.08 per game minute, roughly 38 points in 8 hours), faster at night away from any bed.
- **Fills at home** at a rate that depends on **comfort**: `comfort = home step (bench 0, Mia's couch 1, lent room 2, studio 3, loft 4, apartment 5, penthouse 6) + sum of furniture quality of the pieces in the room (each 1-3, only pieces with a use point count once)`;
  rate = 0.10 + 0.05 x comfort per game minute, capped at 0.6 (an empty lent room barely holds the need, a furnished penthouse fills it fast). Sleeping and sitting at home fill it at x2.
- The **park bench** gives almost nothing (+0.02/min while sitting), a friend's couch a little (+0.1), a hotel-like place none. Visiting a friend's home (invite in free play) gives a small boost.
- Effects: **Home < 25**: Fun gains halved and Social decays faster ("You miss your own walls."); **Home > 80**: buff "Cosy" (Fun gains +10 %, Energy +5 % faster when sleeping at home). Never causes a faint or debt.
- Story use: the prologue room above the shop gives a first taste (full Home), the bench makes it fall (gentle push to find a home, M30), bills by post and decoration have a feeling reward. It also gives furniture a clear job: better furniture raises the fill rate, shown on the Status screen.
- Save: one `u8` in the spare bytes. Pause screen: one more line. Balance: it never blocks anything; it nudges.

### 3. To-do: NPC walk animations

NPCs currently **slide with idle frames** (`npcs::wander` uses the idle sheet with a 1 px bob; script `move_to` also slides). To do: render **proper walk cycles for the cast** (Mia, Rosa, Dex, Pimm, Lou, Okafor, Ines, Teo, later mentors; 8 facings x 4-6 frames each),
through `blender_cast.py` like the player walk. Budget: each NPC sheet is 8 facings x 32x64 = 8 x 8 tiles... with walk frames about 6x as many tiles in ROM; sprite VRAM allows only about three NPC sprites on screen at once during talks, so load walk
frames per NPC only while that NPC moves (stream the frame like the player) and keep idle-only sheets for standing NPCs. Also needed for scripted moves in cutscenes and for the Old Block residents who wander. Priority: Mia, Rosa, Dex (most moves in the cutscenes). Not built.

### 2a. Owner answer on the needs list (s68, final)

"Showering" and "hygiene" are the **same** need: **Hygiene, shown with a clear shower icon**. **Bladder (WC) stays.** The planned HUD therefore has **seven needs**:
Hunger (food icon), Energy (bed or "Zzz" icon), Hygiene (shower icon), Bladder (toilet icon), Social, Fun, and the new **Home** (house/cosy icon). The earlier "does Bladder stay?" question is closed.
- **HUD budget:** seven slots do not fit variant A (28 px slots, pitch 30, 6 slots). Needs a HUD proposal: 7 slots at about 26 px pitch 28 (bars thin, icons larger), or two compact rows; decide with a mock-up in a real screenshot. The Home need design above stands.
- **Icon redesign (future proposal):** all need icons must be **clearer and more readable** than the current ones: sleep = bed or Zzz, Hygiene = shower head with drops, Bladder = toilet, Hunger = a recognisable food item (bread or fork and plate), Fun = smiley or ball, Social = two speech bubbles or two heads, Home = a small house. Test them at real GBA size (16x16 or 14x14) on the phone-size screenshot; keep the green/orange/red bar colours.
  Same icon set later feeds the Status screen, the phone and hint texts. NEEDS PROPOSAL (show the redesigned set in an in-game screenshot before building).

## s69 (docs only): the Late Tram time machine

Main-story arc M54a-M54e (s70) and the Egypt Pyramid Yard service (Cells, deben rings, Sun-star reputation, Egyptian residents, Menkhet furniture set, Tomb Honey, secret 13): `docs/story_chapters3-5.md` section 4.6 and `docs/progression.md` section 2.2. Needs new systems when built: relic/deben inventory, per-NPC Egypt friendship, Sun points, Cell stock, a yard-time gauge, `tools/egypt.py` dig spots (like `deposit.py`), furniture catalog entries ("Menkhet Collection"), collectible set S5.
