# Town Life - Progression: upgrades, secrets and free play

Status: writing proposal for the owner (docs only, nothing built). Own design; no system is copied from any other game.
Conventions as in `docs/story_chapter1.md` section 0. **NEEDS PROPOSAL** = new art/map: show the owner a design first (owner rule).
Related: `docs/story_overview.md` (story), `docs/features_backlog.md` (systems), `docs/story_chapter2.md` section 8 (City Coins perks).

Five parts: (1) one coherent **upgrade ladder**, (2) **secrets** (incl. the Midnight Sweets that raise skills), (3) **free play after the credits**, (4) the **Status screen** in the pause menu, (5) **skill gates** (doors that need a skill or a type star).

---

## 1. Upgrades: one ladder, four sources

Everything that makes {NAME} permanently or temporarily better belongs to one of four sources. Each has its own currency (so the player
always knows how to get more) and its own cap (so nothing breaks the economy).

| Source | You get it by | Lasts | Where it shows |
|--------|---------------|-------|----------------|
| **Skills** (5) | doing: working, practising, reading | permanent | pause > Upgrades > Skills |
| **Perks** (City Coins) | friendships (70+), talks, collectible sets | permanent | pause > Upgrades > Perks, bought at the Coin Box |
| **Stars** (type reputation) | jobs and missions of a type | permanent | pause > Upgrades > Stars |
| **Buffs** | food, drink, sleep, sewer sweets, wishing fountain | minutes to 2 days | small icons beside the HUD + Buffs page |

### 1.1 Skills (Strength, Creativity, Logic, Charm, Fitness)

Points 0-100 as already planned (Chapter 1 target about 6-12 points per skill). **Ranks** I-V at **10 / 25 / 45 / 70 / 100** points.
A rank-up shows a one-line toast ("Charm II: people listen a little closer."). Each rank gives a small passive; the effect of rank V is the cap.

| Skill | Trained by | Per rank | Rank III bonus | Rank V bonus |
|-------|------------|----------|----------------|--------------|
| **Strength** | crates, shelves, Docks, sofa jobs | Grafters/hauling pay +4 % (cap +20 %) | deposit bag +2 slots | bag +4 slots, crate carrying 20 % faster |
| **Creativity** | murals, busking, lamp painting, reading art books | Makers pay and tips +4 % (cap +20 %) | furniture can be re-coloured (2 tints) | sell own murals at the Factory ($30/week) |
| **Logic** | archive, reading, Techies minigames, puzzles | minigame timers +0.5 s (cap +2.5 s) | prices in shop menus show "usual price" | reading gives +50 % Fun |
| **Charm** | talks, waiter job, negotiating | friendship gains +4 % (cap +20 %) | first small-talk topic of a day always liked | tips +1 $ per shift |
| **Fitness** | running, Ballers, dog walks | walk and run speed +2 % (cap +10 %); job Energy cost -3 % (cap -15 %) | Hunger decay while running halved | no Energy loss from running |

Normal training is the main road: about 1-3 points per day in the skill you work at. The expensive **skill sweets** of secret 1 (2.1) are a shortcut worth at most 15 points per skill. Rule: skills never decay. Training has diminishing returns per day (first 3 gains of the day full, then half) so no one grinds a skill in a day.

### 1.2 Perks: the Coin Box (City Coins)

City Coins come from friendships (3 at friendship 70, then 1 per first talk every third game day) and from collectible sets (S2/S3/S4: 1 coin each,
later sets as listed in the backlog). The shop is the **Coin Box** on Ines's laundromat counter (opens at M29, see Chapter 2 section 8).
All perks have **tiers**; buying tier N needs tier N-1. Prices 4-15 coins as agreed; all tier IIIs together cost about **150 coins**, more than the
story pays out (about 60-80 by the ending), so the player has to choose, and free play (part 3) keeps earning coins.

| Perk | Tier I | Tier II | Tier III | Effect type |
|------|--------|---------|----------|-------------|
| **Quick Feet** | 5 c, walk/run +5 % | 8 c, +10 % | 12 c, +15 % | speed |
| **Strong Back** | 8 c, all job pay +5 % | 11 c, +10 % | 15 c, +15 % | money |
| **Light Sleeper** | 4 c, Energy decay -5 % | 6 c, -10 % | 9 c, -15 % | needs |
| **Thick Skin** | 4 c, Hygiene decay -8 % | 6 c, -15 % | 9 c, -22 % | needs |
| **Iron Stomach** | 5 c, Hunger decay -5 % | 8 c, -10 % | 12 c, -15 % | needs |
| **Night Owl** | 6 c, Energy decay -20 % from 22:00 to 6:00 while awake | 10 c, and night jobs pay +10 % | - | needs / money |
| **Silver Tongue** | 6 c, friendship gains +10 % | 9 c, +20 % | 13 c, +30 % | people |
| **Good Neighbour** | 12 c, +1 friendship on the first daily talk with each NPC | - | - | people |
| **Early Bird** | 10 c, +$1 on the first shift each morning (before 10:00) | 12 c, +$2 | 15 c, +$3 | money |
| **Hot Meal** | 5 c, staff meals +10 % | 9 c, +20 % | 13 c, +30 % | food |
| **Bargain Hunter** | 6 c, shop prices -3 % | 10 c, -6 % | 14 c, -10 % | money |
| **Lucky Hand** | 5 c, scratch cards: nothing 70 % -> 65 %, bins +5 % finds | 9 c, nothing 60 %, bins +10 % | - | luck |
| **Deep Pockets** | 5 c, deposit bag 10 -> 14 | 8 c, bag 20 | - | storage |

**Hard caps (so numbers stay sane):**
- Vehicles (kick scooter +15 %, skateboard +20 %, fatbike +30 %, motor scooter +45 %, hoverboard +60 %, post-game car +60 % on roads; see `docs/features_backlog.md`) are a mounted speed of their own, the best owned counts, and they do not stack with the walking cap.
- Walk/run speed from skills + perks + stars: **+25 %** at most (Fitness 10 + Quick Feet 15 = the full cap; type stars add speed only through Fitness).
  Temporary buffs may exceed the cap by up to +25 % (see 1.4), so the absolute maximum is +50 % while a sweet is active.
- Pay bonuses (Strength/Creativity/Charm tips, Strong Back, Early Bird, Overtime) add up; the total job-pay bonus is capped at **+35 %**.
- Shop discounts (Bargain Hunter) cap at **-10 %**; Logic III only shows prices, it does not discount. Rent, bills and debts are never discounted.
- Need decay reductions from perks and buffs together never go below **-40 %** of the base rate (a need can always run down).

Coin Box UI: the menu holds 6 rows, so the first page lists four categories (Body: Quick Feet / Light Sleeper / Thick Skin / Iron Stomach / Night Owl;
Money: Strong Back / Early Bird / Bargain Hunter / Lucky Hand; People: Silver Tongue / Good Neighbour / Hot Meal; Bags: Deep Pockets) and the second page
shows 3-5 perks with their next tier, price and effect in one line. Buying shows a toast and a short Ines line.

### 1.3 Stars: type reputation unlocks

Stars (0-5 per type) already unlock jobs, clothes, places and characters. They also give each type **one passive per star level 2 and 3**, free:

| Type | Star 2 | Star 3 | Star 5 title |
|------|--------|--------|--------------|
| Grafters | **Steady Hands**: stacking and stocking minigames forgive the first mistake | **Overtime**: shift pay +10 % (counts toward the +35 % cap) | "Foreman" |
| Makers | **Free Spirit**: Fun decay -10 % | **Street Cred**: busking tips +25 % | "Maestro" |
| Techies | **Quick Fix**: repair and code minigames start with +3 s | **Debug**: minigames show a hint once per round | "Architect" |
| Ballers | **Second Wind**: running Energy cost -25 % | **Stamina**: Energy decay -5 % all day | "Captain" |
| Posh | **Good Manners**: Social decay -15 % | **Old Money**: selling items pays +10 % | "Host" |

Star 1 = access (jobs, places), star 4 = a clothing set of the type, star 5 = the title shown in the pause header and one exclusive furniture piece (free play, part 3).
The half-speed rivalry rule is unchanged.

### 1.4 Buffs (temporary)

Rules: at most **3 active buffs**; two buffs of the same kind do not stack (the stronger one counts, the timer of the longer one stays); sleeping
does not pause a buff; buffs are saved. Each buff has an icon (16x16, `ui_icons` row, NEEDS PROPOSAL for the icon set) shown beside the HUD and a line on the Buffs page with minutes left.

| Source | Buff | Effect | Time |
|--------|------|--------|------|
| Coffee | Wired | Energy decay -20 %, then a small crash (Energy -5) | 90 min |
| Hearty meal (Burger, staff meal) | Full | Hunger decay -25 % | 180 min |
| Good sleep in a home (Energy 100 and >= 6 h) | Rested | skill gains +10 % | until midnight |
| Shower | Fresh | Charm +1 rank effect in talks | 120 min |
| Party / Block Party | Buzz | Social decay halved | 1 game day |
| Wishing fountain (secret 8) | Lucky | Lucky Hand II effect | 1 game day |
| Midnight Sweets (secret 1) | see 2.1 | speed, hunger, talks (cheap sweets); skill sweets are permanent and expensive | 1-2 game days / permanent |

Food buffs are the same as the existing meal tables (no new numbers needed there except the buff tag).

### 1.5 Where it shows

All of this lives on the new **Status** screen of the pause menu (section 4: Overview, Skills, People, Perks and Buffs, Doors). The main pause screen gets one extra line
("Bonuses: walk +20 %, pay +17 %") once any bonus exists, and active buffs show as small icons beside the HUD.

### 1.6 Data and economy notes

- Skills: five `u8` already planned. Perks: 13 perks x 2 bits = 26 bits, one `u32` in `save_data` (new fields at the end, save version bump when built).
  Buffs: 3 slots x (kind `u8`, minutes left `u16`) = 9 bytes. Stars: five `u8` (planned).
- Chapter 1 money stays about $100 at the end. Nothing in Chapter 1 depends on a perk; the first coins arrive at friendship 70 (Mia, Rosa, Lou),
  so the first perk (Quick Feet I, 5 coins) is realistic around the end of Chapter 2, right when the Coin Box opens.
- Perks are applied through one function per effect type (`speed_mult()`, `pay_mult()`, `decay_mult(need)`, `price_mult()`), so every system reads the totals in one place and the caps in 1.2 are enforced there.

---

## 2. Secrets (13)

Secrets are found by exploring, gossip and phone rumours; none blocks the story. A "Secrets found x/13" line appears in the Collection page once the
first one is found (the entries stay hidden until then: "???"). Each secret is a one-time discovery with a small reward plus (where listed) a repeatable service.

| # | Secret | How you find it | Reward | Art |
|---|--------|-----------------|--------|-----|
| 1 | **Mothball's Midnight Sweets** (sewer, 00:00) | loose manhole + rumours (see 2.1) | buff sweets and (expensive) permanent skill points, one per night | NEEDS PROPOSAL (sewer room, character, portrait) |
| 2 | **Lou's secret menu: "The Usual"** | friendship with Lou 40+, order "the usual" at the counter | Burger Deluxe $8: Hunger +55, Energy +10, Fun +5, buff Full | none (menu row + text) |
| 3 | **Rooftop of the community centre** | fire-escape ladder in the back alley (a rumour from Pimm: "the best view in town") | sit on the roof at night: Fun +20 over 10 s, Social +5, a collectible "Skyline" | NEEDS PROPOSAL (ladder, roof scene) |
| 4 | **Ivo, the night chess hustler** | under the fountain-square lamp 1:00-4:00 only | plays "pigeon chess" for $2 stakes (a coin toss with banter), sells 1 gossip tip per night ($1) that sets a rumour flag | NEEDS PROPOSAL (sprite, portrait) |
| 5 | **The code 1931** | the Old Block arch says "EST. 1931"; the VaultMart staff gate keypad (variant B shutter) accepts it | the gate opens: you can climb to the warm room above (Rosa's radio plays, a postcard from the old days, collectible) | none (interactable `gate` gets a code option) |
| 6 | **Singing self-checkout** | scan "nothing" at a VaultMart kiosk 7 times in a row | the kiosk sings a 4-bar jingle, prints a free Nutrient loaf coupon; Fun +10 | none (jingle needs maxmod later) |
| 7 | **The Golden Pigeon** | 1 in 20 pigeon spawns is gold; feed it bread (Bread in the bag) | it drops a City Coin (once per week) | NEEDS PROPOSAL (palette-tinted pigeon, tiny) |
| 8 | **Wishing fountain** | throw $1 into the fountain 7 times in one day (menu row "Make a wish") | buff Lucky for one game day; the 7th wish shows a pigeon winking | none |
| 9 | **Message in a bottle** | about 1 in 200 bottles in RETURN & EARN holds a note ("Pier 4, under the third plank") | a hidden stash of $15 on the Docks (once) and Mia's grandpa's second postcard | NEEDS PROPOSAL (bottle sprite variant, tiny) |
| 10 | **Duchess vs the kiosk** | walk Duchess (dog job) past a VaultMart kiosk | she barks, the kiosk shows OUT OF ORDER for a game day, staff cheer; Duchess +friendship | needs the corgi (already a proposal) |
| 11 | **Trench-E's poem** | talk to the cable-works robot 5 times (after the door bridge) | it recites a poem about holes; after the ending it is dug in as a flower-bed robot that waves | NEEDS PROPOSAL (robot sprite is already part of the cable works) |
| 12 | **The Co-op coin that is not there** | after S2 (4 coins) examine Pimm's empty coin frame in the library | a fifth coin, hidden behind the Corner Market sign (post-game collectible) | none |
| 13 | **The Sealed Annex** (Pyramid Yard, Egypt; added s69) | after the time-machine arc (M54a-M54e): Logic 35 and three star-marked clay clues dug up at the yard | the Builders' Pact tablet, a free Throne of Reasonable Hours, the oldest shopping list; Legacy +2 (see 2.2) | NEEDS PROPOSAL (`pyramid_annex`) |

### 2.1 Mothball and the Midnight Sweets (secret 1, details)

**Character: Mothball** (original). A small, round, very polite sewer-dweller in a patched yellow raincoat, a miner's lantern on a string of fairy lights, a tray
of paper-wrapped sweets hung round the neck. Speaks in whispers, apologises to the rats, calls the player "dear customer". Never says where he came from
("Down. Mostly down."). He likes Joke and Weather, dislikes Gossip ("The pipes carry everything."). He is not a small-talk NPC; he has a shop menu and 4 scripted chats.

**Finding the entrance:**
- The loose **manhole** in the fountain square (one of the existing manholes; its lid sits a little crooked and has a chalk smiley, visible from the start but inert).
- The **rumour chain**: Pimm (gossip rule `sweets_pimm`: "I hear the drains... smell of toffee after midnight. A civil engineer notices.") -> Teo's text
  ("boss theres a man in the sewer who sells candy. i didnt see him. ok i saw him. 2 oranges.") -> an anonymous phone message once the player is awake at 00:00 and
  has heard one rumour: "Sweets for the sleepless. Fountain square. Mind the lid."
- **Opening rule:** only from **00:00 to 00:30**, press A on the manhole ("Climb down?"). At 00:30 the lid thumps shut by itself ("Closing time, dear customer.")
  and the player is back on the square. Outside that window the lid does not move ("It's locked from below.").

**Shop:** the sewer room (about 8x6 cells: pipes, a bench made from a bathtub, fairy lights, a hammock). Limits: **one sweet per night** (a night = the 00:00-00:30 window), and **only one
temporary sweet effect active at a time** (a new one replaces the old one, Mothball warns: "Digestion is a single-file queue."). Prices in whole dollars. Every sweet has a funny side effect.
Two shelves: the cheap **buff sweets** (temporary) and the expensive **skill sweets** (permanent skill points, the owner's request).

*Buff sweets (temporary, $5-15):*

| Sweet | Price | Effect | Time | Side effect |
|-------|-------|--------|------|-------------|
| **Lemon Zinger** | $6 | run and walk speed +25 % (over the cap) | 1 game day | hiccups: every ~15 min a short "hic" bounce; Bladder decay x2 |
| **Moon Mint** | $9 | **no Hunger decay** | 2 game days | Energy decay +20 %; the player yawns at lamp posts |
| **Honey Drop** | $7 | next 3 conversations: friendship gains x2 | until used (max 1 day) | sticky: Hygiene -10 and "You stick to the sofa." line when sitting |
| **Fizz Bomb** | $5 | Energy +30 at once, Bladder -20 | instant | burp, 2 s freeze, pigeons scatter |
| **Pocket Fog** | $8 | Social does not decay and Fun gains +25 % | 1 game day | the player's name tag in talks reads "???" (cosmetic joke) |

*Skill sweets (permanent, expensive):* one sweet gives **+3 skill points** in its skill (roughly one to two days of normal training) plus a side effect for one game day.

| Sweet | Skill | Side effect (one game day, humour first) |
|-------|-------|-------------------------------------------|
| **Iron Jawbreaker** | Strength | Hunger decay x1.5; you try to lift benches ("Not now, {NAME}.") |
| **Paintbox Fudge** | Creativity | everything tastes loud; random doodles appear on the pause screen |
| **Brain Bonbon** | Logic | you overthink: every menu waits 1 s before it opens; the player mutters "hm" |
| **Silver Toffee** | Charm | you cannot stop complimenting: a random compliment page may open any talk (friendship +1 if it lands) |
| **Springy Gumdrop** | Fitness | bouncy walk (cosmetic), Energy decay +15 %, sitting down takes two tries |

**Price rule:** the n-th skill sweet ever eaten costs **$40 + $10 x n**, capped at **$150** (n = 0 is the first: $40, the 12th and every later one: $150). The price is the same for all five sweets.
**Cap:** sweets can raise a skill by at most **15 points** in total (five sweets per skill) and never past rank III (45 points); everything above must come from real training.
Total for all 25 sweets: about $3,100, spread over the whole game and free play, so a sweet is a deliberate purchase (one to three days of wages), never the only way. A player who never finds the sewer loses nothing the story needs.

Free play (part 3) adds **Legend Licorice** ($30, a buff sweet): every buff sweet at half strength at once, one per night; money sink for the late game.
Story link: Mothball hears everything in the pipes. After M42 he sells the player, for free, a single "Pipe Whisper" (a one-line clue about the cable trench, see
`docs/story_chapter1.md` section 3B.2a); in Chapter 5 his pipes lead to the AURUM relay (optional clue, no puzzle).

### 2.2 The Late Tram and the Pyramid Yard (secret 13, repeatable service; owner request s69)

After the story arc **M54a-M54e** (`docs/story_chapters3-5.md` section 4.6) the time machine in the Quarter Lab runs **only to ancient Egypt**: the forecast core is cut out and a noodle
keeps the year dial stuck on 4,500. The stop is the **Pyramid Yard**, the building site of Pharaoh Menkhet's very large tomb. Own design, original characters. Everything visual is **NEEDS PROPOSAL**.
Secret 13 inside it is the **Sealed Annex** (Ledger Room, below).

**Rules and costs**

| Rule | Value |
|------|-------|
| Where / when | Quarter Lab, Quill & Solder, 9:00-19:00; Pip works the lever (Nadia's shop hours). Menu: "Egypt (season ticket)" and "Ticket Book". |
| Limit | **One trip per game day** (resets at 6:00). The main throttle. |
| Fuel | **1 Quarter Cell** per trip. $35 from Pip, or free from **6 dead phone batteries** (items: WIRE IT repairs give 1, the Repair Café jar 2 per Sunday, bins 4 %). At most 5 Cells in stock. |
| Body cost | Energy >= 50 and Hunger >= 20 to board (Pip: "You'll faint in the sun."). In the yard Energy and Hygiene decay 1.5x; a free well gives water (Bladder -). On return **Tram-lag**: Energy decay x1.25 for 3 hours. |
| Time | The yard lasts up to **180 game minutes** ("yard time", 3 real minutes; a Cell gauge in the HUD slot). The world clock is frozen; you return **5 minutes** after you left, with your needs as if the yard time had passed. NPC schedules, the clock, the Demolition Countdown and the day's events are untouched. |
| Bag | Relic slots **4 + Strength rank** (max 9). Tallies are kept in Seshi's bank (cap 999; they never leave Egypt). |
| Not for sale | Egyptian goods carry Seshi's "NOT FOR EXPORT" stamp: shops and the Docks Salvage refuse them (their "museum problem"). They can be placed at home, put on the collection wall, or **given as gifts** (daily gift rule). No cash loop. |
| Pip's upgrades | **Long Ticket** $150 (+60 yard minutes), **Roomier Satchel** $200 (+4 relic slots), **Sun Panel** $300 (the lab roof makes 1 free Cell every 3 game days). |
| Caught | Walking into Menkhet's Treasury tent: SESHI| I will have to write / this down. The Tram yanks you back and the Cell is spent; what you already carry is kept. A joke, never a punishment. |

**The map `pyramid_yard` (NEEDS PROPOSAL, ~52x44 cells, bright desert day, no night):** the mud-brick **Sun Gate shrine** where the Late Tram appears; the **half-built pyramid** (it grows in 10 layers, see below) with a long
**ramp and sledge track**; the **workers' village edge** with **Hetepet's bread tent** and a brewery shed; **Seshi's Ledger Tent** (the bank, the barter desk and the Builders' Pact tablet; interior); the **Tally Market** (four stalls, rotates stock every 2 game days);
**Menkhet's Pavilion** (shade, a cat, a sunshade, always lounging); the Nile bank with ducks and gulls (Everything Library animals, CC BY 4.0, credited in the README) and a palm grove; 20 **dune dig spots** marked by pegs; the **Sealed Annex** (a small stone door in the pyramid's flank, `pyramid_annex`).
People (all original, NEEDS PROPOSAL sprites + portraits): **Seshi** (scribe-accountant; bank, barter and audits; friendship NPC), **Hetepet** (baker; recipes, bread swap, honey and lotus stall), **Khenti** (foreman; chores, a gruff Halloran type), **Pharaoh Menkhet** (vain, loud, funny; the
"Decree of the Day" gag, 12 rotating decrees), **Miu** (the temple cat; pat for Fun +3 once per day; a future pet when pets are built). Egyptian friendships work like any NPC's (0-100, City Coin at 70) and appear on a "Yard" tab of the People list.

**What you do there**
- **Chores** (each pays tallies, max 2 per kind per trip; each adds pyramid blocks): *Sledge Run* (BOX CLEVER variant) 8-12 tallies, 3 blocks; *Flatbread* (knead timing) 6-10, 1 block; *Hieroglyph painting* (BIG WALL variant) 10-15, 1 block; *Fix Seshi's abacus* (WIRE IT variant, Techies) 12, 1 block; *Mirror polish* 5, 1 block.
  A full trip pays about **30-45 tallies** and 5-8 blocks.
- **Dig** (the dune pegs, 4 s, Energy -1, Hygiene -1, like the bin search; B cancels): 12 of the 20 spots are active each visit. Results by chance: pottery shard 38 % (flavour, a gift worth N +1), tallies 22 % (2-6), food 14 % (dates Hunger +10), **scarab** 10 % (the next missing item of the collectible set; spares become gifts), faience beads 8 % (gift, decor material), **Tomb Honey 2 %**, nothing 6 %. A dug spot refills after **3 game days** (checked at 6:00 like RETURN & EARN). Unique finds appear once ever.
- **Barter** (Seshi takes up to 3 goods per trip): Rosa's rye loaf -> 4 tallies, Coffee -> 3, Hot sauce -> 10 (he is a spice man), a newspaper -> 2 ("Fake papyrus. Wonderful.").
- **Food** (Hetepet): Flatbread 4 tallies (Hunger +30, Energy +8), Lotus tea 6 (Fun +10), **Tomb Honey** 40 tallies (limit 1 per trip), **Blue Lotus petals** 25 tallies (limit 1 per trip).
- **Bread swap:** bring Rosa's bread to Hetepet once; she gives the Papyrus slip (collectible) and a recipe gift for Rosa (Rosa +6, a laugh).

**Tally Market (furniture and decor; each is a furniture catalog entry, `tools/furniture.py`, category "Menkhet Collection", priced in tallies)**

| Piece | Tallies | Kind |
|-------|---------|------|
| Reed Mat (rug) | 70 | decor, floor |
| Reed Chair | 60 | seat (sit facing +y), quality 1 |
| Lotus Lamp | 80 | lamp; Fun +3 once per visit to the room |
| Alabaster Jars (pair) | 90 | decor |
| Scarab Wall Tiles (3) | 100 | wall decor |
| Sandstone Bench | 120 | seat, quality 2 |
| Temple Cat "Miu" (statue) | 250 | decor; pat for Fun +3 once per day |
| Sun Disc | 300 | wall centrepiece |
| **Throne of Reasonable Hours** | 400 (or free, Annex) | seat, quality 3, the best nap seat in the game (Energy +) |
| Mini Obelisk | 500 | floor centrepiece (needs Strength rank II to carry) |

All ten cost 1,970 tallies (about **40-45 trips** with the usual 40 tallies per trip, about $1,500 in Cells: a long tail, one trip a day). Free play allows 12 furniture slots; the loft and penthouse show the set. Also on sale: a **Pharaoh headcloth** (a gag hat, 150 tallies; for the clothing system later).

**The Pyramid grows (a long goal, not a chore):** each chore adds blocks; **12 blocks = 1 layer, 10 layers = 120 blocks (about 20 trips)**. Each layer is visible on the map. At 100 % the **Capstone Day**: Menkhet's speech
(MENKHET| It is BEAUTIFUL. I / am beautiful. Seshi, / write beautiful.), the golden capstone, a feast. Rewards: the **Golden Capstone Lamp** (penthouse centrepiece), a **Red-Foot statuette** (a minor god in red sneakers, "weekends only"), the title
"Honorary Minor God" on the Ticket Book page, Legacy +5. Afterwards **every 10th trip is a Festival** (tallies x2). Menkhet: "Now a bigger one." Seshi: "No."

**The Sealed Annex (secret 13, one time):** a stone door that needs **Logic 35** and the three **clay clues** (found by digging at the pegs marked with a star, one per clue; the clues are rebus pictures: bread, beer, a sandal). Inside: **the Builders' Pact tablet** (collectible), the free **Throne of Reasonable Hours**, and a hidden joke tablet: the oldest recorded shopping list ("bread; more bread; ask Seshi about bread").
Seshi weeps: SESHI| Nobody found the Pact / in forty years. Well. / In forty-five centuries. Legacy +2.

**Collectible set S5 "Sands of Time" (6 pieces):** scarab seal (dig), beer-jug shard with the brewery stamp (dig), abacus bead (Seshi's chore), the papyrus order slip "3 loaves, 1 beer, 0 complaints" (bread swap), the Builders' Pact tablet (Annex), and Menkhet's sandal strap (10th trip). Reward: 1 City Coin, Legacy +5, a frame on the collection wall.

**Sweet ingredients (Mothball, secret 1):** **Tomb Honey** and **Blue Lotus** are ingredients: Mothball turns one into a sweet for $20 (one buff sweet at a time, as always): **Honey Scarab** (training gains +25 % for 24 game hours, side effect: you hum in a very old key) and **Lotus Lozenge** (Fun +25, Bladder decay halved for 3 hours, side effect: you speak slowly and wisely for a minute).
MOTHBALL| Honey from a tomb? It / never spoils. I have / notes. Stand back. These sweets give **no permanent skill points**, so the sweet cap (2.1) is not touched.

**How it fits the economy**
- Cash cost is small ($35 a trip, or batteries) next to free-play income ($400-800 a day); the real cost is the **one-trip-a-day** limit and the yard minutes. It is a time sink with a visible reward ladder, not a money machine.
- Nothing from Egypt can be sold, so nobody can farm it for cash. The only money-adjacent outputs are gifts (friendship maintenance) and buff sweets (a bit more skill training).
- City Coins: S5 (1) + up to 4 Egyptian friendships at 70 (3 each, once). Perks stay capped, so the extra coins only speed up the top tier a little.
- Legacy points: S5 5, Capstone 5, Annex 2, Egyptian friendships 3 each (12): about 24 on top of the ~150 needed for Legend; a real contributor but not required.
- The Ticket Book page lives in the Collection screen (3 stamps: FORECAST, 45 YEARS AGO, EGYPT; plus "Trips: N" and "Pyramid x/10"). The Status > Doors page lists "Quarter Lab: Logic 25 (soft gate: Pip's Riddle Door)".


---

## 3. Free play after the credits

The story ends at M70 "One Year Later" with the credits. Then the game **saves a "Legend" file flag** (`epilogue`) and continues. The world stays as left
(warm Old Block, the penthouse, the library tower). Nothing is lost and no mission is pending; the log shows "Free play: make Town Life yours."

### 3.1 What unlocks

- **Exclusive shops:**
  - *Marchand Atelier* (Hilltop): the **Marchand Collection**, a luxury furniture line (quality 3, about 3x the price of normal pieces): velvet sofa $450,
    marble bath $600, grand piano $1,800, chandelier $350, library wall $900, aquarium $520. Each is a catalog entry with a use point like all furniture.
  - *Co-op Market Hall*: stalls with seasonal goods and **clothes sets** per type (star 4 sets, star 5 exclusive hats), prices $40-$250.
  - *Vintage garage* (Docks): the story's small-vehicle ladder (kick scooter, skateboard, fatbike, motor scooter "Bella", hoverboard; `docs/features_backlog.md` "Vehicles ladder") is earned in the story. Free play adds only cosmetics for them (paint, stripes, bells, $30-$120) and
    the one big luxury, the **car "Greenie"**: Vault's repossessed golden car, bought back at auction and repainted ($6,000, +60 % speed on roads, roads only). The car's SW/NE facings are a NEEDS PROPOSAL.
  - *Legend Licorice* in the sewer (see 2.1).
- **Titles ("Legend" ladder)**: a **Legacy** score shown in the pause header as a title: Newcomer -> Local -> Neighbour -> Pillar -> **Legend**.
  Legacy points come from: friendship 70+ with each NPC (3 each), type stars (2 per star), collectible sets (5 each), secrets (2 each), Co-op fund projects (see below, 5 each).
  Legend needs about 150 points (more than a normal story run gives), so free play has a visible goal. The title appears in the penthouse guest book.
- **New events** (all optional, repeating):
  - *Grand Market* every Saturday (bigger Saturday market with guests from every district, new stalls, a gift raffle).
  - *Lantern Night* monthly (the Old Factory street party, Social +30, Fun +20, collectible photo).
  - *Star Night* (a movie on the library wall, Fun +25, free popcorn buff Buzz), on the first Friday of each in-game month.
  - *Rovers Cup* (Ballers: a short tournament, trophy for the penthouse shelf, 3 games to enter).
- **The Late Tram to the Pyramid Yard** (Quarter Lab, after the time-machine arc): one trip a day for a Cell, tallies, the Menkhet furniture set, the growing pyramid, Tomb Honey and Blue Lotus for Mothball, collectible set S5; the pyramid's Capstone Day is a free-play goal (section 2.2).
- **Daily errands board** (in the Co-op Hall): three random small tasks per day (deliver a parcel, repair a phone, serve a table, walk a dog, sort books),
  $15-40 each and 1 City Coin for every third finished errand; a **streak bonus** (+10 % per day in a row, cap +50 %) that only counts while the player keeps playing; missing a day just resets it.
- **Max-out goals**: every type to 5 stars (top job of each: transport company, gallery, startup, club, property empire, each with passive daily income that
  feeds the sinks below), all skills to rank V, all 13 perks to the top tier, all collectibles and secrets, friendship 70+ with everyone, Legend title.

### 3.2 Money sinks (so money always has a use)

| Sink | Price range | Notes |
|------|-------------|-------|
| Luxury furniture (Marchand Collection) | $350-$1,800 | penthouse slots, see 3.3 |
| Clothes sets and hats | $40-$250 | per type, seasonal stock changes every month |
| Vehicles | $900 / $6,000 | one of each; upkeep is none (humane) |
| Co-op fund projects (Old Block upgrades) | $200-$1,500 | visible changes: new street lamps, a bigger fountain, murals, library wing, a bike lane, a playground with Teo's ramp; each gives Legacy points and a ribbon-cutting scene |
| Gifts | $3-$60 | friendship maintenance; Posh gifts are the expensive ones |
| Legend Licorice and fine dining (Gilded Spoon tasting menu $80: Hunger +60, buffs Full and Buzz) | $30-$80 | repeatable |
| Cells for the Late Tram ($35 each) and Pip's upgrades ($150 / $200 / $300) | $35-$300 | one trip a day; relics cannot be sold (section 2.2) |
| Business investments (stock deals, shop expansions) | $100-$2,000 | each raises passive income, so late money is a loop, not a wall |

Balance idea: free-play income is about $400-$800 per in-game day for a maxed player (businesses + errands), so a luxury piece is a few days of play, a vehicle a few weeks, the Legend title the longest goal.

### 3.3 The penthouse as the showcase

The penthouse is the player's **private home** (owner s67) atop the rebuilt Co-op Hall. It becomes the place that shows everything the player has done:
- **12 furniture slots** in free play (6 in the story), the Marchand pieces only fit here and in the loft.
- **Collection wall**: collectibles (coins, postcards, flyers, party photos, skyline, secrets) appear as framed items as sets are completed.
- **Trophy shelf**: Rovers Cup, mural miniatures, star-5 items, the Legend plaque.
- **Guest book**: signed by every NPC who visits; friends with 70+ can be invited ("Come over") and visit for an evening (Social +, a short chat, a gift sometimes).
- **Window view**: a day/night panorama with changes for every Co-op fund project (a bridge, new lamps, lights in Old Block), so the room visibly grows with the player's deeds.
- **Relic corner**: the Menkhet Collection pieces, the Golden Capstone Lamp, the Red-Foot statuette and the framed Ticket Book page (from the Pyramid Yard, section 2.2) fit the penthouse and the loft.
- **Garage door** (if a vehicle is owned): the owned vehicles are parked at the Hall; Bella, the hoverboard and Greenie appear in the scene.
All penthouse pieces use the furniture catalog rule; the room itself NEEDS PROPOSAL (already planned for the epilogue).

### 3.4 What stays out

No new bills or debts in free play (a gentle ending: bills by post become optional "Co-op dues" the player may pay for Legacy points). The countdown is gone
after the downfall; Victor Vault stocks shelves at the warm Corner Market (a running gag: he gets a name tag "Victor, trainee" and a new line every few days).

---

## 4. The Status screen (pause menu) - NEEDS PROPOSAL (UI)

Our own design (owner asked for a status page with reputation, skills and a list of the people you have met; any similar screen in other games is only a reference for the
kind of information, never for layout, names or art). It is a new row **Status** in the pause menu (between "Mission log" and "Collection"), built with the existing Paper (day) / Night
UI toolkit (`ui::panel`, `ui::bar`, `ui::label`, the 232x120 pause panel at (4, 4)). **L/R switch between five pages**, a page strip with five small tabs shows where you are; B goes back.

| Page | Shows | Layout |
|------|-------|--------|
| **1 Overview** | name, title (Newcomer ... Legend), money, Legacy points, active buffs as icons, bonus summary ("Walk +20 %  Pay +17 %  Prices -6 %"), and the **five type reputations**: Grafters, Makers, Techies, Ballers, Posh | one row per type: a small emblem, name, **five star pips** (gold = earned) and a thin bar to the next star; a red "half speed" marker on the type that is held back by its rival; the passive unlocked at star 2 and 3 as a tiny icon |
| **2 Skills** | Strength, Creativity, Logic, Charm, Fitness | one row per skill: icon, name, rank in Roman numerals (I-V), a bar 0-100 with ticks at 10 / 25 / 45 / 70, the points "27/100"; the selected row shows the next rank bonus on one line and the "sweet points" in a different colour (so the player sees what came from candy) |
| **3 People** | everyone met so far | list of 4 rows (scroll with Up/Down): a 24x24 head icon (neutral portrait, one palette), name, a friendship bar 0-100 with the number and a gold tick at 70, a mood face (good / neutral / grumpy). **Detail strip for the selected person:** one-line bio ("Runs the laundromat. Adopts people."), Likes (topics found by playing; undiscovered ones show "?"), the favourite gift once found (liked twice), a City Coin badge when the 70 reward was paid, the type they belong to. Sorted by friendship, then by name; unmet NPCs do not appear |
| **4 Perks** | the 13 City Coin perks and your coins; buffs below | tier pips per perk (I-III), cost of the next tier, effect in one line; the coin count in the corner; active buffs with minutes left |
| **5 Doors** | every locked door you have met (section 5) | "Neon Pigeon: Charm II (you: I)" with a tick when you can enter; shows what the door gives |

- **Data:** reputation (five `u8`), skills (five `u8` points plus five `u8` sweet points), friendship (16 `u8`, exists), likes discovered (16 bytes of topic bit masks, new), favourite gift discovered
  (16 `u8`, new), met flag per NPC (16 bits, new), doors discovered (a 16-bit mask, new). All carved out of the end of `save_data` when built (save version bump then).
- **Sprites:** the pause screen frees the HUD text; the People page needs 4 head icons plus bars and about 40 text sprites, within the 128-sprite budget. Head icons are cropped from the
  existing portraits by `tools/portraits` (a new "icon" output, 24x24, 15 colours each).
- **Art to propose:** the type emblems (five 16x16), star pips, rank pips, the five skill icons, mood faces, tab strip, the 16 head icons. Mock-up first (owner rule).

---

## 5. Skill gates: doors that need a skill, a star or both

Some places, jobs and people check a skill rank or a type star. The doorman, foreman or guard says a funny refusal line, the requirement is written to the mission log / "Doors" page ("Neon Pigeon: needs Charm II, you have I"),
and the player can always do something about it: train the skill, ask a trainer, or come back later. **Rules:**
1. **The critical path never hard-locks.** Every gate on the main story (M-missions) asks for at most about 70 % of the skill the chapter normally gives (chapter targets: Chapter 1 end Strength 12 / Fitness 8 / Logic 7 / Charm 6 / Creativity 4; Chapter 2 end 25 / 15 / 12 / 10 / 14; later chapters add 8-12 per skill),
   and each has a **catch-up route**: a named **trainer** who gives a 1-hour lesson (+1 point, $5-10, once per day per skill, only up to the gate level) so nobody gets stuck; a "Train: Strength (Halloran's crate drill)" line appears in the log as soon as a gate refuses.
2. **Harder gates are optional content**, secrets or post-game (clubs, labs, galleries, top jobs). They give extras, never story.
3. Type-star gates use the existing stars (a gate may ask for a star instead of a skill).
4. Skill sweets (2.1) may help clear a gate but never are needed for one.

| Where (chapter) | Who checks | Requirement | What you get | Refusal line | How you learn it | Path |
|-----------------|------------|-------------|--------------|--------------|------------------|------|
| Archive in the library (Ch1, M14) | Pimm | Logic 4 | the three archive boxes, the Co-op ledger | PIMM: "The archive is for those who can read a catalogue. Read one. Then come back." | Pimm says it; log line | main; trainer: library books (Logic +1 each) |
| Docks trial (Ch1, M16) | Halloran | Strength 6 (and the $12 levy) | steady job, Grafters star 1 | HALLORAN: "Those arms carry sandwiches. Come back with muscle." | Halloran states it, log shows "Strength 6 (you: 4)" | main; trainer: Halloran's crate drill, Mia's "Box Mover" odd job |
| Forklift licence (Ch2, M20) | Bo-Ra | Strength 14 and Logic 6 | licence, forklift pay | BO-RA: "Gerald is shy. He only likes people who can lift AND read a sign." | log line from M19 | main; trainer: Bo-Ra's walk-through (Logic), pallet drills (Strength) |
| Busker's stage (Ch2, M25) | Wren | Creativity 8 | BEAT STREET tips | WREN: "You hum like a fridge. A nice fridge. Not yet." | Wren's text "wren_band" | main; trainer: Wren's bell lesson |
| Sports Park trials (Ch4, M46-M47) | Coach Gus | Fitness 12 (already ~15 by Ch2 end) | FIT-O-METER, penalty training | GUS: "Run to the fence and back. Slowly is fine. ...Not that slowly." | Gus states it | main; trainer: Zoe's 6am drills |
| Waiter test (Ch5, M57) | Odette / Benedict | Charm 16 | the Gilded Spoon job, Hilltop pass | ODETTE: "Your shoes are cheerful. Your posture is a crime." | Benedict hints | main; trainer: Benedict's etiquette lesson ($10) |
| **Neon Pigeon club** (Ch3, Station Quarter) | doorman Bruno | **Charm 12** (rank II) | dance minigame, Social +40, Fun +30, gossip hub, a rare topic | BRUNO: "Your vibe is... laundromat. Come back with sparkle." | the flyer on the wall, Bruno's refusal, the log + Doors page | optional |
| **Quarter Lab** (Ch3, Nadia's back lab; holds the Late Tram time machine from M54a) | Nadia / Pip | **Logic 25** (rank III) | prototypes: tool perks, Techies top job path, the Late Tram (story arc M54a-M54e, then Pyramid Yard trips) | PIP: "The lab needs a brain. Not a bad one, a trained one. Sorry. Hi." | Nadia's remark after M34; the tarp "NOT A SHOWER" | optional; **soft gate:** Pip's Riddle Door (one CODE PATTERN) lets you in below 25; trainer: Nadia's puzzle hour |
| **Sealed Annex** (Pyramid Yard, Egypt) | Seshi | **Logic 35** and three clay clues | the Builders' Pact, the free Throne of Reasonable Hours (secret 13) | SESHI: "Stone door. Stone head. Needs both to be sharp." | the star-marked pegs | secret |
| Rooftop of the community centre (secret 3) | the ladder | Fitness 14 | the roof, a collectible, Fun +20 | "Too high for those knees." | Pimm's rumour | secret |
| Gallery opening at the Boiler Room (Ch4) | Wren | **Creativity 30** and Makers star 3 | exhibit your own mural, Makers top job "own gallery" | WREN: "Lovely! No. Come back when your colours have opinions." | Wren's invitation card on the wall | optional |
| Crane cabin (Docks, Ch4+) | Halloran | Strength 30, Logic 15, Grafters star 3 | crane operator job, +$14/h, own transport company path | HALLORAN: "Cranes have feelings. They don't like noodle arms." | Halloran's board | optional |
| The Gold Room (Hilltop, Ch5) | doorman | Charm 25 and Posh star 3 | rare gossip, Posh investor path | DOORMAN: "Sir, this is a private party. You are a very public person." | Odette's remark | optional |
| Code Night hackathon (Station Quarter, Ch5) | Pip | Logic 35 and Techies star 3 | the tech top job, a unique perk token | PIP: "Lovely brain. Needs a few more floors." | Nadia's flyer | optional |
| **Legend's Table** (Gilded Spoon, free play) | Benedict | Legend title and all skills rank IV | the tasting menu, Legend plaque | BENEDICT: "Sir. Madam. Not yet. But very nearly." | the plaque on the wall | post-game |

NEEDS PROPOSAL for the places that do not exist yet (Neon Pigeon, Quarter Lab, Gold Room, crane cabin, roof, gallery). Doormen (Bruno, the Gold Room man) are barks-only characters with a sprite.
