# Town Life - Chapter 2 "Get By": Story, Missions and Text

Status: writing proposal for the owner. Nothing here is implemented. Conventions as in `docs/story_chapter1.md` section 0 (dialogue pages:
`SPEAKER| line / line / line`, max 3 lines x 28 characters, `{NAME}` counts as 8). Mission ids continue after Chapter 1 (M17).
Anything marked **NEEDS PROPOSAL** needs new art or a new map (owner rule: show a design first, no ROM until approved).
Overview of the whole game: `docs/story_overview.md`.

## 1. At a glance

| | |
|---|---|
| **Theme** | Getting by is not the same as getting ahead. You learn to ask for help, to take it, and to give it back. |
| **Days** | Day 8 (Mon) - Day 30 (Tue). About 3 game weeks; 2.5-3 hours of play. |
| **Districts** | **Docks** (Grafters, opens at the end of Ch.1) and **Old Factory** (Makers, opens in M24). Old Block is fully open. |
| **Big moment** | **A key in the door** (M30): the first place of your own, a back room behind Ines's laundromat that she lets you use. |
| **Housing step** | Bench / Mia's couch -> **the lent back room** (bare walls, mattress, crates, hot plate). See section 6. |
| **Careers** | Grafters: Dock hand -> **Forklift driver** (promotion M20). Makers: **Street musician** (M25), first mural (M26). |
| **Minigames** | BOX CLEVER (stacking boxes), LIFT & LOAD (forklift driving), BEAT STREET (rhythm), BIG WALL (drawing). |
| **Events** | Saturday market (weekly, from Ch.1), **the "Bread Not Barcodes" march** (M28), **Block Party** (M29). |
| **Reputation** | Grafters 1 -> 2 stars, Makers 0 -> 2 stars. First time the rival rule can show (see 8). City Coins perks are introduced. |
| **Villain move** | VaultTech's **AutoPort** (robot cranes and trucks) to replace the dockers, a higher bridge levy, and a fence round the Old Factory ("DataVault"). |
| **Rival (Dex)** | Promoted to **Regional Manager**. Brings AutoPort to the Docks. Covers for the player's crew once. His doubts grow. |

## 2. New characters

Chapter 1 characters (Rosa, Mia, Dex, Pimm, Lou, Halloran, Ines, Teo, Okafor, Kessler, Valet, Vault) all return. Their small-talk tables
are in Chapter 1 section 5.6; new topic answers for Ines and Teo are in section 9 below. All new faces need portraits and sprites
(**NEEDS PROPOSAL**; sprites are 32x64, portraits from `tools/portraits`).

### 2.1 Bo-Ra Han - crane and forklift operator (Grafters teacher)
- **Role:** Teaches the player to drive the forklift. Halloran's best operator and the only one who ever makes her laugh.
- **Look:** 30, short black hair under a hard hat with stickers, orange vest, a thermos, fingerless gloves, a gap-toothed grin.
- **Personality:** Cheerful, reckless on paper and careful in practice. Names every machine ("Gerald" the forklift, "Beyonce" the crane).
- **Likes:** Music, Joke, Sports. **Neutral:** Weather, Work, Compliment. **Dislikes:** Gossip, Complain. **Mood:** Good (base).
- **Gift favourite:** Hot sauce (+10). **Whereabouts:** Docks 6:00-18:00, lunch on the quay bench 12:00.
- **Small talk lines:** Music| "Radio on max. Gerald / dances when the bass / drops." Work| "Lift with the legs, / steer with the heart." Joke| "Why did the crane cross / the dock? To reach the / other side. Hah!" Gossip (D)| "Not my cup of tea. / Tea is for people who / don't drive cranes."

### 2.2 Stitch - old docker (Stanislaw Kowal)
- **Role:** The Docks' memory. Mends nets, knows every rumour, loves a story more than a crate. Cameo in Ch.1 (M16).
- **Look:** 58, huge grey moustache, knitted cap, thumbless gloves, a pipe he never lights.
- **Personality:** Warm gossip with a good heart. Tells every story three ways. Always the first to cry at a bridge.
- **Likes:** Gossip, Weather, Complain (he enjoys a good moan). **Dislikes:** Sports, Joke ("Everything's a joke to the young").
- **Gift favourite:** Newspaper (+10). **Whereabouts:** Docks netting bench 6:00-17:00; Grigor's chess table Fridays.

### 2.3 Little Sal - dock apprentice (Salome Reyes)
- **Role:** 17, drops out of school for the Docks, shy and sharp. Shows the player the ropes. Becomes the player's **first employee** in Chapter 3.
- **Look:** Tall, thin, big headphones round the neck, patched jacket, bitten nails. Always sketching crates in a notebook.
- **Personality:** Hungry for a future, afraid of ending up like the older ones. Idolises Bo-Ra. Likes Music, Work; dislikes Compliment (squirms).
- **Gift favourite:** Chocolate. **Whereabouts:** Docks 6:00-16:00; sketches on the quay; evenings at the Old Factory fence (listening to Wren's band).

### 2.4 Wren Adeyemi - Makers' mentor
- **Role:** Sculptor, welder and band leader, runs "The Boiler Room", a hidden studio in the **Old Factory**. Teaches street music and murals.
- **Look:** 52, silver locks wrapped in a rainbow scarf, paint-splattered overalls over a band T-shirt, safety goggles on her forehead, a half-built bell on her shoulder.
- **Personality:** Loud, theatrical, then suddenly gentle. Believes everybody can make something. Calls the player "darling" or "artist" (even when they are not).
- **Likes:** Music, Compliment (genuine), Joke. **Neutral:** Weather, Gossip, Complain. **Dislikes:** Work ("Work is what you do for others. Art is what you do despite them."), Sports.
- **Gift favourite:** Chocolate (+10). **Flower:** hates flowers ("They die so politely.") (-3).
- **Small talk lines:** Music| "Listen. That hum? / The old turbine. It's / the bass line." Compliment| "Oh, don't stop. I'm / made of compliments / and solder." Work (D)| "Work is a leash. Art / is a dog off the leash." Joke| "A welder walks into a / bar. Sparks fly. I'm / here all week."
- **Whereabouts:** Boiler Room 9:00-23:00; Old Block Saturday market 10:00-14:00.
- **Her band** (extras at the studio): **the Rust Choir**, five Makers (drummer Kofi, singer Jo, tuba Pavel, two kids on pans). Anonymous flavour.

### 2.5 Nella Bellini - Rosa's sister (cameo)
- 70, sharper than Rosa. Runs the bakery next to the laundromat, takes in strays, whispers gossip. She is where Rosa sleeps.
- She appears once (M30) when she hands the player a key. No small talk.

### 2.6 Existing characters with a changed role
- **Dex Corbin:** Regional Manager (VaultTech, Docks + Old Block). New outfit: sharper blazer, a gold tie pin shaped like a V. Still calls you "buddy".
- **Ines:** talkable (needs a small-talk slot). **Teo:** talkable. **Kessler:** moved to the Old Factory fence, even more miserable.
- **Pimm:** hosts "bridge talks" on Fridays at the library (Chapter 3+).

## 3. Mission chain

IDs M18-M30. "Earliest" days are guides; the story waits for the player. Each row also lists the phone text that nudges it.

| ID | Day | Title | Log text | Done when | Rewards | Next |
|----|-----|-------|----------|-----------|---------|------|
| M18 | 8 | Monday on the Dock | Work your first full week at the Docks (0/3 shifts). | `ch2_shifts_3` | Halloran +5, Stitch/Bo-Ra intro | M19 |
| M19 | 8-10 | Box Clever | Pass Halloran's stacking test (rank B or better). | `boxclever_b` | Strength +3, Grafters +1 point | M20 |
| M20 | 10-13 | Forklift Fever | Learn to drive Gerald the forklift with Bo-Ra. | `forklift_licence` | **Forklift driver** (pay $9/h), Grafters 2 stars | M21 |
| M21 | 14 | Couch Expires | Find somewhere to sleep. Mia's cousin is coming. | `bench_again` | Mia +3, Okafor check-up offer | M22 |
| M22 | 15-17 | The Robot on Pier 4 | See what Dex is bringing to the Docks. | `autoport_seen` | `dex_doubt` +1 | M23 |
| M23 | 17-19 | Race the Machine | Beat the AutoPort crane with Halloran's crew. | `race_won` | Docks warm, Grafters +, Bo-Ra +10 | M24 |
| M24 | 18-20 | A Light in the Factory | Find where the night music comes from (Old Factory). | `factory_entered` | Old Factory opens | M25 |
| M25 | 20-22 | Busker | Play for tips on Wren's steps (BEAT STREET). | `busker_done` | Makers 1 star, +$8-20 tips | M26 |
| M26 | 22-24 | Big Wall | Paint a mural over the VaultTech billboard (BIG WALL). | `mural_done` | Makers 2 stars, Creativity +4 | M27 |
| M27 | 24-25 | Two Wheels | Get a bike (Teo says he knows a guy). | `has_bike` | Bike (faster), Teo +10 | M28 |
| M28 | 26 Sat | Bread Not Barcodes | March on VaultMart with Old Block. | `march_done` | Old Block warm, Rosa +10 | M29 |
| M29 | 27 Sun | Block Party | Help set up the Block Party. | `blockparty_done` | **City Coins perks** shop opens, Social +30 | M30 |
| M30 | 28-30 | A Key in the Door | Move into the back room behind the laundromat. | `home_1` | **First home**, chapter end | Chapter 3 |

Side threads (log "Also"): **S7 Pimm's Fridays** (talk to Pimm Fridays, Logic +1 each), **S8 The Debt** (pay the clinic bill if you owe it),
**S9 Rust Choir Fan** (give Wren's band chocolate x2 for a rare "shout-out" line), **S10 Ines's Boxes** (Old Block odd jobs).

## 4. Key scenes

### M18 Monday on the Dock (Day 8) - NEEDS PROPOSAL (Docks map)
*The Docks, 6:00. Grey water, orange cranes, the smell of diesel and fish. The bridge behind you is open; the levy booth blinks.*
- HALLORAN| You're early. Good. / Start with the pallets. / Stitch will show you.
- STITCH| Pallets! Ah, yes. Let / me tell you about the / pallets of '98.
- HALLORAN| Stitch. / Work now. Tales later.
- STITCH| Tales are work. Tales / are how we remember where / the crates go.
- *A forklift beeps past. Bo-Ra waves from the cab.* BO-RA| Gerald says hi! / He also says move.
- *Tutorial prompt:* SYSTEM| Shifts pay $6 an hour. / Needs matter: eat before / you start.
- **Shift mechanics:** the plain Dock hand shift (6 h, $36) plus the new minigame **BOX CLEVER** each day (optional; rank adds a bonus, see 5).
- **Rewards after 3 shifts:** Halloran +5, `ch2_shifts_3`. Phone: "halloran_week" (section 7).

### M19 Box Clever (Day 8-10) - the stacking test
- HALLORAN| Test. Stack twelve / crates on the truck. No / drops. No tilts.
- *Minigame result pages:*
  - Rank S| HALLORAN| ...Huh. Fast. Neat. / You stacked like you / meant it.
  - Rank A/B| HALLORAN| Acceptable. Come back / tomorrow. Same time.
  - Rank C| HALLORAN| Again. Slower. Crates / don't care about speed. / They care about tilt.
- **Rewards:** Strength +3; the Docks now offer BOX CLEVER as a repeat job. Stitch tells the "pallets of '98" story as a one-off small-talk bonus.

### M20 Forklift Fever (Day 10-13) - LIFT & LOAD
- *Bo-Ra introduces Gerald, a yellow forklift with a sticker on the mast reading "I LIFT YOU UP".*
- BO-RA| Gerald, meet {NAME}. / {NAME}, meet Gerald. / He likes slow hands.
- BO-RA| Two rules. Never / carry people. Never / race Beyonce.
- {NAME}| Who's Beyonce?
- BO-RA| The crane. She's / sensitive.
- *Training: three runs (forks under pallet, lift, turn, set down). Pass = no pallet dropped, under 90 s each.*
- On pass:
  - BO-RA| Licensed! You are now / dangerous. Responsibly.
  - HALLORAN| Forklift driver. Nine / an hour. Don't make me / regret nine.
- **Rewards:** `forklift_licence`, pay $9/h (6 h shift = $54), Grafters 2 stars (+20 rep), Fitness +2.
- **Note:** Halloran does not praise people. She raises the pay and says "Don't be late." That is praise.

### M21 Couch Expires (Day 14) - the low point
*Mia's flat. Mia is on the phone, hanging up. She does not look happy.*
- MIA| That was my cousin. / Dina. She's coming for / a month. Tomorrow.
- MIA| The couch is hers. / ...I'm so sorry, {NAME}. / I wish the flat had a room.
- *Choice:*
  - OPT| It's OK. I'll manage.  (Mia -0, `bench_again`, "You always say that.")
  - OPT| Can I sleep on the floor?  (Mia +2, "Dina snores like Gerald.")
  - OPT| I'll find something.  (Mia +3, "Ask. People help here. Even Rosa.")
- MIA| Promise me you'll ask / someone. Not just walk / past a bench again.
- *The player takes the bag, walks out. The camera lingers on the door. Quiet music. It starts to rain.* (Weather proposal, optional; the scene works without rain.)
- *Night: park bench. The pigeons are there. One sits on your knee.*
- {NAME}| Well. Bench again. / Old friend.
- {NAME}| ...I can't keep / sleeping here. Eventually / someone has to say yes.
- **Mechanics:** `bench_again`. Okafor texts the next day ("okafor_cold": "It's getting cold. Sleep indoors if you can. - Dr. O."). A short *sick* risk is real this week (the clinic can fix it).
- **Alternatives:** If the player already has $40+ and asks Lou, Lou offers the diner couch for 3 nights ("Don't tell Health & Safety, hah!"), cheaper than rent, no home yet.

### M22 The Robot on Pier 4 (Day 15-17) - Dex returns
*The Docks, 10:00. A sleek white truck arrives. A pole of gold flags. Banner: "AUTOPORT: LOADING THE FUTURE".*
- DEX| Buddy! Look at you! / Forklift licence! / Fast learner. Scary.
- DEX| I am Regional Manager / now. Docks, Old Block, / and nearly Narnia.
- {NAME}| What's that?
- DEX| That is AutoPort. Four / arms. Zero lunch breaks. / Zero Stitch.
- STITCH| I have a name, boy.
- *Valet rolls out of the truck, scanning the crew.*
- VALET| Dock staff: forty-one. / Projected redundancy: / forty-one.
- HALLORAN| (flat) Is that a threat?
- VALET| It is a forecast.
- *Dex looks at his shoes. For two seconds.* DEX| (low) It's only a trial. / Two weeks. I swear.
- **Beats:** The crew's hours are cut from 6 h to 3 h (the player's shift pays $27 / $18 (forklift) for the trial period).
  Stitch: STITCH| That's what they said / about the pier lights.
- **Choice with Dex (after the speeches, behind the truck):**
  - OPT| Don't do this, Dex.  (Dex +1, `dex_doubt` +1: DEX| I'm not the boss of / this. I'm the... face.)
  - OPT| Do you sleep at all?  (Dex +3: DEX| In my car. Don't tell / Bert.)
  - OPT| You're a traitor.  (Dex -3: DEX| I'm a manager. Say it / with me.)

### M23 Race the Machine (Day 17-19) - the human crew vs AutoPort
- *Halloran, arms crossed, in front of the whole crew:* HALLORAN| Mr. Corbin. A bet. / Our crew against your / machine. One truck.
- DEX| And if the machine wins?
- HALLORAN| We leave. All forty- / one. Quietly.
- DEX| And if you win?
- HALLORAN| Your machine goes / back in the box. / Politely.
- DEX| ...Done. Valet, log / the bet.
- VALET| Bet logged. Stakes: / forty-one jobs. Probability / of human win: eleven.
- *The race:* a timed BOX CLEVER + LIFT & LOAD relay. The player is the final leg (fork a pallet onto the truck). Rank S/A = win.
  The machine glitches in the last 20 seconds on purpose-built bad luck: a sensor error. *If the player is Dex-friendly (>= 25):*
  Dex is seen sliding a pallet marker 10 cm so the arm misreads. (Never shown directly; Stitch mutters: "Funny. The arm blinked.")
- **If won:**
  - VALET| Error 77: crate not / found. Recommended / action: recalibrate.
  - DEX| (too loud) Sensor dust! / ...Totally sensor dust. / Two weeks, Bert!
  - *Halloran extends a hand to Dex. He stares. Shakes it. Quick.* HALLORAN| Fair race. Thanks.
  - STITCH| Tell the pier lights / we said hello.
- **If lost (Strength/Logic too low, the player may choose to retry once per day):** the crew works at half hours, wages drop 25 % for a week, but the race
  can be run again after 3 days; the story continues (no hard fail). Dex does not smirk.
- **Rewards:** `race_won`, Docks district turns **warm** (flag `docks_warm`: ships' lamps, laundry on the cranes, bunting), Grafters +10 rep, Bo-Ra +10, Halloran +10.
  Phone: Stitch "stitch_tale", Dex "dex_sensor" (section 7).

### M24 A Light in the Factory (Day 18-20) - Old Factory opens
- *Night, 22:00, on the quay. Faint bass and bells float across the water. A glow behind a high fence. Teo is sitting on the pier with his legs dangling.*
- TEO| Boss! You hear that? / Music from the factory! / Nobody's allowed in!
- {NAME}| So why is it playing?
- TEO| Because it's alive. / Obviously.
- *They walk to the fence. Kessler is on guard with a thermos, looking at the stars.*
- KESSLER| Not one word. I'm / looking at the moon. / Which is not a gate.
- KESSLER| Behind the red barrels / there is a hole in the / fence. I know nothing.
- *Through the hole: a courtyard of rusted turbines, string lights, a bonfire in a drum, a band rehearsing. The band stops. Wren spots you.*
- WREN| An audience! Darling, / you've been *heard.*
- WREN| Nobody comes in. Not / VaultTech, not police, / not Kessler's mum.
- KESSLER| (outside) I heard that.
- WREN| I'm Wren. This is the / Boiler Room. VaultTech / calls it DataVault.
- WREN| They want to turn it / into a server farm. / For silence.
- {NAME}| Silence?
- WREN| The sound of a number / being bored. Come back / Sundays. Bring ears.
- **Rewards:** `factory_entered`, Old Factory opens (a map: **NEEDS PROPOSAL**), Wren +5 friendship, Makers intro, first `Rust Choir` rehearsal listened.
- **Warm/cold:** the Factory is "cold outside the fence" (grey fence, DataVault signs) and "warm inside" (string lights). Both states exist from the start.

### M25 Busker (Day 20-22) - BEAT STREET
- WREN| Everyone starts on the / steps. Rhythm first. / Feel it in your knees.
- *She gives the player a battered tambourine and a cardboard sign: "TIPS KEEP US LOUD".*
- *Minigame:* four-lane rhythm on the factory steps and then the Old Block fountain; tips from passers-by (A/B/L/R). Rank adds tips; busking costs Energy -10 and Fun +8.
- **Tips:** C = $8, B = $12, A = $16, S = $20 (plus a "cheering crowd" line: TEO| Encore! Encore! / ...please).
- After:
  - WREN| That wasn't music. / It was *intention.* / Perfect. Do it again.
  - *Makers reputation 1 star.*
- **Rewards:** `busker_done`, Makers 1 star, Creativity +3, Charm +1. Street music becomes a repeatable job ("Busker").

### M26 Big Wall (Day 22-24) - the mural over the billboard
- *Old Block, the entrance arch. A huge VaultTech billboard: "OLD BLOCK? OLD NEWS."*
- WREN| That wall. Tonight. / We paint over every / letter.
- INES| (leaning out of her window) / I'll bring the soup. / The ladder is Teo's.
- TEO| It's not my ladder. / It's... community property.
- *Minigame BIG WALL: pick a colour, paint within the outline on a grid, matching Wren's sketch (timed). The player's mural is a loaf of bread with wings and a bridge behind it.*
- *Result: dawn, the billboard is a mural. Passersby stop. Mrs. Valdez weeps. Captain shouts "BEAUTIFUL!"*
- WREN| Look at that. Warm / enough to toast bread.
- **Rewards:** `mural_done`, Makers 2 stars, Creativity +4, Old Block warm (flag `ob_arch_warm`), Rosa +3, a newspaper headline ("BILLBOARD BECOMES BREAD").
- **Cost:** VaultTech notices the mural (Dex receives the report, files it under "weather").

### M27 Two Wheels (Day 24-25) - the bike
- TEO| Boss, I know a guy. / The guy is my cousin. / The bike is... borrowed.
- *Choice:* OPT| Where is it from?  /  OPT| Is it stolen?  /  OPT| How much?
  - Truth: the bike belonged to Grigor's son. Grigor sells it for $45 with a sigh ("The sea is faster, but fine"). If the player asks "Where from?" Teo admits it and takes the player to Grigor.
  - If the player takes it from Teo for free, a gossip rule (Grigor -4) triggers; the "good" path is to pay Grigor.
- **Reward:** `has_bike` (+30 % walking speed, new cue in the pause screen), $45 spent, Grigor +8, Teo +10, **Fitness +2**.

### M28 Bread Not Barcodes (Day 26, Saturday) - the march
- *Saturday market in Old Block turns into a march. Teo's drum, Wren's band, Ines with a soup pot on wheels, Rosa in front with the cart.*
- ROSA| Forty years. And here / I am marching. With / oranges.
- MIA| I made signs. I spelled / "BARCODES" right on / the third try.
- PIMM| I'll supervise. At the / back. With a stool.
- *They walk down the avenue to VaultMart. Dex in the doorway with a tablet.*
- DEX| This is an unlicensed / gathering! Please disperse! / (...please?)
- ROSA| Mr. Corbin. We're here / to shop. Does your shop / sell bread?
- DEX| Rye is discontinued... / ...but I have a nutrient / loaf.
- ROSA| We brought bread. Share it.
- *Rosa hands Dex a warm roll. He looks at it. It smells of the old shop.*
- *Choice (Dex):* OPT| Eat it, Dex.  (Dex eats; flag `dex_ate_bread`, Dex +4) /  OPT| Just take a bite.  (+2) /  OPT| (say nothing)  (0).
- *If Dex ate:* DEX| ...that's... Rosa. / That's the shop. That's / the smell.
- *Valet rolls in:* VALET| Manager Corbin. Smile / level: 12 percent. Please / increase.
- DEX| (to the crowd) ...Please / disperse. Thank you. / (and, quietly) Thank you.
- **Rewards:** `march_done`, Old Block turns fully warm (flag `old_block_warm`), Rosa +10, Mia +5, Dex +/- as above, Techies -1 rep (VaultTech notes the player).
- **Consequence:** VaultTech decrees a "noise curfew" in Old Block after 22:00 for a week (flavour: Teo's drum is hidden under a bed).

### M29 Block Party (Day 27, Sunday) - the first big event
- *Setup:* the player, Mia, Lou (grill), Ines (soup), Wren (stage), Bo-Ra (crane lights, Docks sends a truck of crates for the stage), Okafor (first-aid tent with cookies).
- Mini-tasks (free order, each 20-40 game minutes): carry crates (Strength), hang lights (Creativity), cook for Lou (Hunger bonus), tune the stage (Logic).
- *The party, 18:00-24:00:* all friends present, music from the Rust Choir. Big dialogue-light scene; the player talks to everyone (extra Social +30).
- **Scene beats:**
  - ROSA| To Old Block! To the / people who stayed!
  - GRIGOR| To the sea! Which / would have left anyway.
  - LOU| To the grill! Hah!
  - MIA| To {NAME}! Who sleeps / on a bench and still / does the dishes.
  - *Everyone laughs. Then a quiet moment: Ines taps her glass.*
  - INES| I have a back room / behind the laundromat. / Four walls. A door. A bed.
  - INES| Empty since my husband. / It needs a person who / snores quietly.
  - {NAME}| Ines... I can't pay.
  - INES| Nobody pays for / kindness. Rosa's rule. / You work. We trade.
- *Fade out.* The trigger for M30 is Ines's offer, accepted or **deferred** (one can say "Not yet" - the offer stays 7 days).
- **Rewards:** `blockparty_done`, City Coins perks shop opens (section 8), Social +30, Fun +20, a Polaroid (collectible #1 of a new set: Party Photos, later).

### M30 A Key in the Door (Day 28-30) - the big moment
- *The back lot behind the laundromat. A door the colour of an old tea bag. Ines gives the player a brass key on a loaf-shaped keyring.*
- INES| Home sweet... beige.
- *Inside (NEEDS PROPOSAL, see section 6): bare walls, a stained mattress on a pallet, three crates, a hot plate on a milk crate, one bulb. A pipe hums.*
- {NAME}| It's... it's mine.
- INES| It's loaned. But yes.
- *The player stands in the middle of the room. Slow zoom. The old key turns in the lock.*
- {NAME}| A door. A lock. / A light that I switch / on myself.
- *Mia appears in the doorway with a plant (a sad cactus).* MIA| Housewarming. It's / dying. Like me before / coffee.
- *Rosa behind her:* ROSA| A bed. A roof. A door. / Now you can start / from somewhere.
- *Nella (cameo), handing over a pie:* NELLA| For the new tenant. / Don't let her cook / for you.
- *Text card:* CARD| First place of your own.
- **Mechanics:** `home_1` set; sleep energy +0.6; the bed is `bed_basic` (new catalog item). First **envelope** (section 6).
- **Chapter end card:** CARD| CHAPTER 2: GET BY / complete.  CARD| Chapter 3: BUILD UP.
- **Epilogue stinger (Vault):** Vault in his tower, polishing the glass of a model city.
  - VAULT| AutoPort is back in / its box?! The dockers / WON?!
  - VALET| Correct. Error 77. / Probability of recurrence: / eleven percent.
  - VAULT| Eleven percent is / more than zero. Station / Quarter. Now.
  - *The model city: a new red-lit district lights up: STATION QUARTER, with a tiny VaultTech sign planted on it.*

## 5. Minigames in Chapter 2 (designs for proposal, not approved yet)

| Name | Where | Idea | Rules | Pay/skill |
|------|-------|------|-------|-----------|
| **BOX CLEVER** | Docks | A crane drops crates onto a flat-bed; you slide left/right and press A to set each crate on the stack, balance matters | 12 crates, tilt meter, 60 s, combo for perfectly aligned crates | Rank S/A/B/C = +$6/+4/+2/0 on a shift; Strength +1 |
| **LIFT & LOAD** | Docks | Top-down forklift: fork under pallet (A), drive, lift (Up/Down), set down | 3 pallets, no collisions, par time 90 s | Pay +$6/+3/0, Fitness +1, licence |
| **BEAT STREET** | Old Factory steps, Old Block | 4-lane rhythm, notes fall onto tambourine hits (A, B, L, R) | 60 s, combo x2/x3/x4 at 5/10/20, miss resets | Tips $8/12/16/20; Creativity +1 |
| **BIG WALL** | Old Block arch, Factory wall | Fill a shape on a pixel grid with the correct colours, limited paint | Sketch shown 3 s, then paint from memory + guide | Makers rep +, Creativity +2 |

Shared rule: all four follow the established pattern: scene-in-a-loop, `minigame_request`, result applies money, needs, clock and flags.

## 6. Housing: the lent back room (step 1 of the new ladder)

**Owner ladder:** room above Corner Market (Day 1 only) -> park bench -> **a small space in a commercial building that someone lets you use** -> studio -> loft -> apartment -> penthouse.

- **Who lends it:** **Ines Okoro.** The back room behind her laundromat (the crates of M10 stand in its back lot). She says it was her late husband's repair workshop. She "trades" it: an hour of help a week (the co-op way, a Chapter 1 coin echo) plus $10 a week for the washing-machine electricity.
- **Why Ines:** a warm, loud, generous character who can take a person under her wing; thematically the exact opposite of VaultTech; the laundromat hums all night (white noise, not silence).
- **Inside look (NEEDS PROPOSAL):** 4x4 cells, bare cream plaster with a damp patch, one tiny window onto the back lot, a concrete floor with a threadbare rug off-cut, a mattress on two pallets, three crates (table, seat, storage), a hot plate on a milk crate, one hanging bulb, a sink in the corner with a cold tap, and no bathroom: the back lot has a shared outside WC, with a note on the door in Ines's handwriting: "KNOCK. SING IF OCCUPIED."
- **Interactions:** Sleep (Energy +0.6/min), Cook on the hot plate (bread toast = Hunger +10; instant noodles at the laundromat's vending machine), Wash at the sink (Hygiene +15), Sit on the crates (Fun +), the **envelope** by the door.
- **Furniture rule (owner):** nothing is drawn ad hoc. The back room uses catalog entries: `bed_basic` (mattress on pallets, $0 supplied, "Pallet bed"), `crate_table` ("Crate table", $5), `crate_stool` ($3), `hotplate` ($12, new interaction kind `cook`), `lamp_bulb` ($4), `rug_offcut` ($6). All need catalog entries and a drawing proposal. The pieces the player may *buy later* are the same ones other shops sell (Dockside Salvage in the Docks, "second-hand crates").
- **Decorating:** the player brings the room up bit by bit (Mia's cactus, Rosa's jar, Teo's poster). Each gift item is also a catalog piece.
- **Envelope at the entrance:** from the day after move-in, an envelope lies on the mat each Monday. A on it opens a short page:
  - *Ines's note (first, hand-written):* NOTE| $10 for power. / An hour of help. / Soup on Tuesday. - I.
  - Pay at the laundromat counter (menu "Pay the week"). Late: Ines does not fine, she raises an eyebrow, and Social -3 for the shame. This is the *warm bill*, contrasted with the VaultTech Utilities bills of the studio in Chapter 3.
- **Housing sleep rule:** lent room +0.6 Energy/min (see Chapter 1, 4.6).

## 7. Phone messages for Chapter 2 (new; <= 90 characters each)

| id | Sender | Condition | Text |
|----|--------|-----------|------|
| halloran_week | Halloran | after M18 | Good week. Same time Monday. Don't think it means I like you. |
| boracheer | Bo-Ra | M19 done | Gerald asked about you. I said you're nice. He didn't believe me. |
| mia_cousin | Mia | Day 13 | Dina lands tomorrow. I'm so sorry. Ask someone for help? Please. |
| okafor_cold | Okafor | `bench_again` | It's getting cold. Sleep indoors if you can. Also socks. - Dr. O. |
| lou_couch | Lou | `bench_again` | The diner has a couch. Three nights. Hah! Don't tell the inspector. |
| stitch_tale | Stitch | M22 | Come to the netting bench. I have a tale about robots. It ends badly. |
| dex_sensor | Dex | M23 done | Sensor dust. That's all I'll say. Don't thank me. - D. |
| wren_band | Wren | M24 done | Sunday, Boiler Room, bring ears. Also snacks. Also ears. - Wren |
| teo_bike | Teo | M26 done | boss i have a guy for a bike dont ask where from |
| rosa_march | Rosa | M27 done | Saturday. March. Wear sturdy shoes and a warm heart. Oranges provided. |
| ines_room | Ines | `blockparty_done` | The back room is empty. The key is on the hook. Think about it. |
| kessler_moon | Kessler | M24 done | If asked: I was looking at the moon. I am always looking at the moon. |
| vault_spam3 | VaultTech | Day 20 | New: AutoPort. Your cargo, our arms. Opt out? (There is no opt out.) |
| nella_pie | Nella | `home_1` | Pie is in the oven. Collect at six. Bring a fork and good manners. |

## 8. Systems introduced in Chapter 2

- **City Coins perks** (shop at Ines's laundromat counter "Coin Box", opens at M29): Strong Back (+10 % pay, 8 coins), Light Sleeper (Energy decay -10 %, 6), Quick Feet (+10 % walking, 5), Thick Skin (Hygiene decay -15 %, 6), Early Bird (daily pay bonus $1, 10), Good Neighbour (+1 friendship on the first daily talk, 12), Hot Meal (staff meal +10 %, 9). Prices 5-15 as in Chapter 1 (4.5). Lore: "A token, pay later." (see 3B.5).
- **Skills and reputation:** full display in the pause menu (Strength, Creativity, Logic, Charm, Fitness; five type stars). Rival rule (half speed while the rival type is higher) is active and explained by Stitch in M22: "The owners laugh at us dockers. Remember: they pay for the dock, we run it." Posh and Grafters is the first pair that matters; it triggers when the player later meets Posh in Ch.5.
- **Warm/cold:** Docks start cold (levy booth, gates, grey cranes), turn warm at M23; Old Factory is cold outside the fence and warm inside; Old Block arch warm at M26; Old Block fully warm at M28.
- **Events:** the Saturday market continues every week (Days 13, 20, 27); Block Party (Day 27 evening); march (Day 26).
- **Bike:** +30 % walking speed, slower Fun decay? No: only speed. Shown as a new player sprite (**NEEDS PROPOSAL**: bike sprite 8 facings).

## 9. Small-talk additions

**Ines** (likes Gossip, Music, Compliment (L); neutral Weather, Work, Joke, Complain; dislikes Sports (D))
- Weather (N)| Rain on the roof, soap / in the machines. A good / day for laundry!
- Work (N)| Hands in hot water, / always. My skin is a / raisin. A happy raisin.
- Music (L)| Oh, I sing while the / machines spin. The drum / is my rhythm.
- Sports (D)| Men in shorts chasing / balls. My husband did / it. Never found one.
- Gossip (L)| Sit! Let me tell you / what Mrs. Valdez said / about the parrot.
- Compliment (L)| Aww. Two dollars off / your laundry. Today / only.
- Joke (N)| Why did the sock go / missing? Ha! It joined / a better pair.
- Complain (N)| Complain? I shout, then / I make soup. Soup fixes / half the world.

**Teo** (likes Joke, Sports (L); neutral Weather, Music, Compliment, Gossip; dislikes Work, Complain (D))
- Joke (L)| Haha! That was dumb. / ...Tell it again. / For the gang.
- Sports (L)| I can do an ollie! / Almost. In my head. / It works.
- Work (D)| W-word. We don't say / that here. It's like / homework.
- Complain (D)| Complaining? That's what / mums are for. Not me.
- Gossip (N)| I know everything about / everyone. And their / oranges.

## 10. Rival arc: Dex in Chapter 2

| Beat | When | What happens | Result |
|------|------|--------------|--------|
| D6 | M22 | Brings AutoPort. "It's only a trial." | doubt +1 |
| D7 | M23 | Sensor dust: he quietly saves the crew (even if the player does not know). | `dex_helped_docks` |
| D8 | M28 | Eats Rosa's bread (or refuses). | bread = warmth, he's closer |
| D9 | end of chapter | Valet files "Manager Corbin: reliability 62 %". Dex hides the report in a drawer. | Chapter 3 pressure |

Dex remains the villain's public face. Nobody forgives him yet, but a "hidden decency" counter (`dex_decency`) starts here (0-5), used in Chapter 4.

## 11. Balance

| Item | Value |
|------|-------|
| Days | 8-30 (23 days) |
| Dock hand shift (6 h) | $36 (till M20), forklift $54 |
| AutoPort trial (M22-M23) | shifts shortened to 3 h ($27 / $27 forklift) for up to 6 days |
| Busker tips | $8-20 per 60 s act (Energy -10) |
| Bike | $45 |
| Rent (lent room) | $10 / week + 1 hour of help |
| Expected money at the end | ~$220 (start ~$110 from Chapter 1 end) |
| Reputation | Grafters 2 stars, Makers 2 stars, others 0 |
| Skills | Strength ~25, Fitness ~15, Creativity ~14, Charm ~10, Logic ~12 |
| Needs hints | Social drops quickly in the dock grind; party and shared meals pay it back. |

## 12. Gossip rules (new, 8; total after Chapters 1-2: 24 - raise the cap in code)

| id | Trigger | Hearer | Effect |
|----|---------|--------|--------|
| bike_grigor | take bike for free | Grigor | Grigor -4 |
| bike_paid | pay Grigor | Teo | Teo +3 |
| race_stitch | M23 won | Stitch | Stitch +5 |
| sensor_halloran | Dex sensor beat | Halloran | Halloran +2 for Dex (`dex_decency` +1) |
| mural_ines | M26 done | Ines | Ines +4 |
| mural_wren | choice "I painted the loaf" | Wren | Wren +3 |
| bread_dex | `dex_ate_bread` | Mia | Mia +2 ("You made him eat? Legend.") |
| march_pimm | M28 done | Pimm | Pimm +3 |

## 13. NEEDS PROPOSAL list for Chapter 2

1. **Docks map** (quay, cranes, netting bench, levy booth, truck bay, bridge end) and its warm state.
2. **Old Factory map** (courtyard, turbines, hidden studio "Boiler Room", fence with the hole, stage steps).
3. **Back room** interior (and the shared WC note) + catalog items listed in section 6 (pallet bed, crate table/stool, hot plate, bulb lamp, rug off-cut).
4. Character sprites and portraits: Bo-Ra, Stitch, Little Sal, Wren, Nella; Dex's Regional Manager look; Ines, Teo, Grigor (Chapter 1 list).
5. **Gerald** the forklift, **AutoPort** (four-arm crane truck), bike and the player on a bike sprite.
6. **BEAT STREET, BIG WALL, BOX CLEVER, LIFT & LOAD** art (mock-ups first, like STOCK IT! / PLATE RUSH).
7. Block Party props (stage, string lights, tents).
8. Mural art over the billboard (painted wall layer; Makers' first piece).

## 14. Chapter-end checklist

- Flags: `ch2_done`, `home_1`, `docks_warm`, `old_block_warm`, `forklift_licence`, `busker_done`, `mural_done`, `has_bike`, `race_won`, `march_done`, `blockparty_done`, `dex_decency` (0-5).
- Items: Mia's cactus, Rosa's jar, Wren's tambourine, Pimm's first-edition "Bridges of the World" (Fridays).
- Save prompt after M30.
