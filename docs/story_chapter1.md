# Town Life - Chapter 1 "Survive": Story, Missions, Balance and Text

Status: writing proposal for the owner. Nothing here is implemented. It is meant to be turned into game data later
(dialogue table, mission table, shop tables, text lists). Canon decisions from the owner are marked as such.

## 0. Conventions used in this document

- All in-game text is English. `{NAME}` = the name the player typed (max 8 characters, default "ALEX").
- **Dialogue format.** One bullet = one dialogue page. `SPEAKER| line / line / line`. A page has at most 3 lines of
  at most 28 characters (8x8 font, ~230 px). ` / ` marks a line break inside a page. Consecutive bullets = page breaks (A = next).
  `OPT|` = a choice option (max 28 characters). `{NAME}` counts as 8 characters when checking the width.
- *Italic lines* are stage directions (not shown in game).
- `(flag: name)` = a story flag set. Flags are booleans unless a number is given.
- Time: 1 real second = 1 game minute, so 1 game day = 24 real minutes. One awake day (7:00-23:00) is about 16 real minutes.
- Money in whole dollars. Friendship 0-100 per NPC. Reputation 0-5 stars per type (1 star = 20 reputation points).
- Day names are only used in this document; the game shows "Day 1, Day 2 ..." and the clock. Day 1 = Monday.

---

## 1. Cast

Mood system for the small-talk meter (see Balance, section 4.5): every NPC has a **base mood** and the mood changes per day.
`Good` = gains x1.5 (round down, min +1), `Neutral` = x1, `Grumpy` = x0.5 (round down, min +1 for likes, dislike penalties
unchanged). Topics: Weather, Work, Music, Sports, Gossip, Compliment, Joke, Complain.

### 1.1 {NAME} (player)
- Fired shop assistant, early 20s. Starts with a room and a job, ends Day 1 with $20 and a bench.
- Voice in the game: short inner thoughts, dry humour, never whiny. The player is never forced to be nice, but being decent
  pays off (friendship, City Coins).

### 1.2 Rosa Bellini - owner of Corner Market (canon)
- **Role:** Runs Corner Market for 40 years. Warm but strict. Gives the player a job and a room above the shop.
  After the firing she gets a cart and later a **market stall in Old Block** (sells bread, oranges).
- **Personality:** Proud, practical, hates waste, loves "her people". Says "Forty years" a lot. Hides sorrow behind orders.
- **Looks:** Short, grey bun, apron over a green cardigan, reading glasses on a chain.
- **Base mood:** Neutral. Grumpy if the player is late or smells (Hygiene < 30). Good after a gift of bread.
- **Likes:** Work, Music (opera on her radio), Compliment (only genuine ones; she answers "Hmph. Thank you.").
  **Neutral:** Weather, Joke, Gossip. **Dislikes:** Complain ("Complaining never stacked a shelf"), Sports ("Men shouting at a ball").
- **Whereabouts:** Day 1: shop 7:00-14:30, then leaves east. Day 2: cart in front of the closed shop 8:00-10:00 (arguing with a
  lawyer robot), then walks to Old Block. From Day 3 (after mission M10): stall in Old Block 8:00-17:00, 17:00-20:00 on a stool
  next to the laundromat, sleeps at her sister's flat (never shown).
- **Gift:** Bread (+8). Ready meal (+3, "I can cook better").

### 1.3 Mia Ferro - coworker and friend (canon)
- **Role:** Cashier at Corner Market. After the firing: waitress at **Lou's Diner**. Lives in Old Block (flat above the laundromat).
  Ends Chapter 1 giving the player her couch. Sometimes found on the street (lunch break on a fountain square bench, walking home).
- **Personality:** Quick, sarcastic, huge heart. Loud laugh. Can't keep a secret but keeps promises.
- **Looks:** Ginger hair, teal top (the existing in-game Mia).
- **Base mood:** Good in the morning, Neutral after 14:00, Grumpy after a double shift (> 8 h worked that day).
- **Likes:** Music, Gossip, Joke. **Neutral:** Weather, Sports, Complain ("Ha! Same."). **Dislikes:** Work ("I just clocked out"),
  Compliment ("Is this a line? It sounds like a line.").
- **Whereabouts:** Day 1 checkout 7:00-14:30. From Day 2: diner 7:00-15:00 (shift), fountain square bench 12:00-12:30 (break, if she
  works that day), Old Block 16:00-20:00 (helping Rosa), flat after 20:00.
- **Gift:** Coffee (+5), Pancakes (+6).

### 1.4 Dex Corbin - coworker and rival (canon)
- **Role:** Ambitious stock clerk with a big mouth. Joins Victor Vault, becomes **manager of VaultMart**. Plays the rival who
  climbs next to the player. Can later doubt (seeds in M11, M14, M15).
- **Personality:** Brags, name-drops, narrates his own life like a sports commentator. Secretly scared of being a nobody.
  Calls the player "buddy". Hates the robot Valet, who audits him.
- **Looks:** Gelled hair, too-big grey blazer, VaultTech lanyard, headset.
- **Base mood:** Good when watched by Vault, Grumpy when Valet reports a low efficiency score (random 30 % of days).
- **Likes:** Work, Compliment, Sports. **Neutral:** Weather, Gossip, Joke. **Dislikes:** Complain, Music ("Noise. Pure noise.").
- **Whereabouts:** Day 1 shop. From Day 2: VaultMart 8:00-20:00 (patrols the aisles), 13:00-13:30 on the VaultTech plaza (eats a
  protein bar), 20:00-22:00 in front of the tower (practises his speeches).
- **Gift:** Coffee (+4, he says "Fuel!").

### 1.5 Mr. Pimm (Albert Pimm) - the old regular (canon)
- **Role:** Retired bridge inspector, 74. Buys one rye loaf every day at 9:00 for forty years. Often in the library
  (community centre) or in City Park. Key to the bridge plot: he inspected the Docks bridge and knows it is sound.
- **Personality:** Gentle, polite, forgetful about names but never about bridges. Dry jokes. Feeds the pigeons.
- **Looks:** Tweed jacket, flat cap, walking stick, round glasses.
- **Base mood:** Neutral. Good at the pond (pigeons). Grumpy if the rye loaf is unavailable.
- **Likes:** Weather, Work (bridges!), Joke (dry). **Neutral:** Music, Compliment, Sports. **Dislikes:** Gossip, Complain.
- **Whereabouts:** Day 1: shop at 9:00. Later: market/VaultMart never; library 10:00-15:30; City Park pond bench 16:00-18:00
  (feeding pigeons); Old Block (home) otherwise.
- **Gift:** Rye loaf (+10, only from Rosa's stall; the VaultMart does not sell it).

### 1.6 Victor Vault - villain (canon)
- **Role:** Billionaire owner of VaultTech, golden tower, plan "Smart City". Original character, not based on any real person.
- **Personality:** Boastful, laughs at his own jokes before the punch line, loves numbers and mirrors, treats people like furniture.
- **Looks:** Tall, tanned, white hair, gold-rimmed sunglasses, gold suit, golden car.
- **Appears:** Cutscenes only in Chapter 1 (Day 1 firing; short cameo on the bridge poster/hologram). No small talk.
- **Key line (canon):** "Cashiers? Shelves? People? So last century."

### 1.7 Valet - Vault's robot assistant (new, no drones)
- **Name:** Valet. White robot on a hover base with a gold ring and stripe, round head with a screen face (cyan smiley),
  gold ear discs, antenna, bow tie, little claws. Cheerful, literal, bureaucratic. Calls everyone by their job title or number.
- **Appears:** Day 1 cutscene, the bridge (M15), VaultMart (in the background, audits Dex).
- **Hangs out:** VaultMart storeroom door, the tower plaza. No small talk. Idle barks only.

### 1.8 Big Lou - owner of Lou's Diner (new)
- **Role:** Runs the diner (the purple house). Hires the player as dish washer. Round, booming, soft-hearted, hates waste and
  hates silence.
- **Personality:** Loud greeter, terrible puns, writes the daily special on a chalkboard, feeds anybody hungry once.
- **Looks:** Big, white apron, moustache, paper hat, always holding a spatula.
- **Base mood:** Good before 11:00, Neutral at rush hour (12:00-14:00), Grumpy if a plate is dropped.
- **Likes:** Sports, Gossip, Work. **Neutral:** Weather, Joke, Compliment, Music. **Dislikes:** Complain ("Complaints go in the grease bin").
- **Whereabouts:** Diner 6:00-22:00 (behind the counter / grill).
- **Gift:** Burger (+3, "I own a diner"), Coffee (+2).

### 1.9 Foreman Brenna Halloran - Docks foreman (new)
- **Role:** Runs the freight crews at the Docks. Seen across the closed bridge from M13 on; hires the player in M16.
  Mentor of the Grafters type.
- **Personality:** Terse, fair, hates talk. Respects people who show up. Hand shake like a vice.
- **Looks:** Hard hat, orange vest, sleeves rolled up, clipboard.
- **Base mood:** Neutral. Good after a punctual delivery.
- **Likes:** Work, Weather (tides), Sports. **Neutral:** Music, Joke. **Dislikes:** Complain, Compliment ("Save it"), Gossip.
- **Whereabouts:** 6:00-18:00 at the Docks gate/bridge end. (Not talkable before M13.)

### 1.10 Minor characters (barks, errands, no small talk)
- **Kessler** - VaultTech security guard at the bridge barrier. Stiff, loves rules, afraid of Valet.
- **Ines Okoro** - runs the Old Block laundromat, shouts in two languages, always has a spare basket to carry.
- **Teo** - 10-year-old on a skateboard in Old Block, delivers notes, steals nothing but oranges.
- **Old Block residents** (anonymous): a man with a chess table, a woman with a parrot (flavour only).
- **Duchess** - Ines's corgi (odd job: dog walking).

### 1.11 Daily whereabouts summary (Days 2-7, unless a mission says otherwise)

| Time | Rosa | Mia | Dex | Pimm | Lou | Halloran |
|------|------|-----|-----|------|--------|----------|
| 6-8 | cart (Day 2), then Old Block | home | home | home | diner | Docks gate |
| 8-11 | Old Block stall | diner (shift) | VaultMart | library 10:00 | diner | Docks gate |
| 11-13 | stall | diner / break on fountain square bench 12:00 | VaultMart | library | diner (rush) | Docks gate |
| 13-15 | stall | diner until 15:00 | plaza bench 13:00 | library | diner | Docks gate |
| 15-18 | stall until 17:00, stool at laundromat | Old Block (helps Rosa) | VaultMart | City Park pond 16:00 | diner | Docks gate until 18:00 |
| 18-22 | home (not visible) | Old Block / flat | tower plaza 20:00 | home | diner until 22:00 | home |
| 22-6 | - | flat | - | - | - | - |

---

## 2. Prologue and Day 1 script ("Monday")

Start state of the game (new game): clock 7:00, money $0 (pocket change; the $20 comes from Rosa at the firing), needs
Hunger 70 / Energy 85 / Hygiene 70 / Fun 60 / Bladder 55. Corner Market is **warm** (Corner Market palette). Only City Centre is open.

### Scene 0 - Title and name entry
- Title screen: TOWN LIFE logo, New Game / Continue (Continue only if a save exists; **no autosave**, saving is in the pause menu).
- *Black screen. A narrator card fades in, one line at a time (3 s each):*
  - CARD| "Corner Market." / "40 years of bread, / gossip and good mornings."
  - CARD| "You work here." / "You live upstairs."
  - CARD| "Today is a normal day."
  - CARD| "(It is not.)"
- *Name entry screen:* "What is your name?" - D-pad letter grid, 8 characters, A = letter, B = delete, START = done. Default "ALEX".
  Confirm box: "{NAME}? Is that right?" Yes / No.

### Scene 1 - Wake up (7:00), room above the shop
*Map: reuse the approved shabby `home_room` as "your room above Corner Market" (single bed, crate, tiny fridge, hot plate, tiny
bathroom). Camera fades in from black. Player sits up in bed, then is free to walk. The only exit is the door to the stairs.*
- {NAME}| Ugh... 7 o'clock. / Already?
- {NAME}| Five more minutes. / No. Rosa's rule: / "Late is rude."
- SYSTEM| Walk with the D-pad. / Hold B to run. / Press A near things.
- *Objective shown: "Get ready for work."* Optional (no pressure): the sink (Wash hands, Hygiene +15), the hot plate (info: "Not
  now. Breakfast is Mia's job on shift days."). The toilet in the tiny bathroom works as in the public WC (Bladder is 55, so the
  player can use it: a free tutorial).
- On the bed (A): "Not now." (the bed is for sleeping at 22:00+; at that point on Day 1 it is gone).
- *Fridge (A):* "Two eggs and a note from Rosa: 'Don't touch my cheese.'"
- Door to stairs: fade, arrive in the storeroom behind the checkout.

### Scene 2 - Morning briefing (7:30)
*Storeroom to shop floor. Rosa stands at the checkout, Mia is counting coins, Dex leans on a gondola with a phone.*
- ROSA| Good morning, {NAME}! / Forty years I open this / shop at 7:30 sharp.
- ROSA| Today the shelves need / stocking. Three of them: / milk, cans and cereal.
- ROSA| Walk up, press A. / I'm watching you. / Kindly.
- MIA| Don't worry. She is / always watching. She has / eyes in the bread.
- ROSA| I heard that, Mia.
- *Objective (M02): "Stock three shelves (0/3)."* Three gondolas get a yellow arrow marker.

### Scene 3 - Stocking shelves (tutorial task)
- Each marked gondola: A = "Stock shelf" (2.5 s animation, Strength +1 skill point). Message after each: "Shelf stocked (1/3)."
- If the player talks to Dex mid-task:
  - DEX| Three shelves? Pfft. / I did five before / breakfast.
  - MIA| You did zero. You ate / three donuts.
  - DEX| Donuts are fuel, Mia. / Fuel for greatness.
- After 3/3 (objective complete, Rosa friendship +5):
  - ROSA| Three for three. / Not bad, {NAME}. / Not bad at all.
  - ROSA| That is the highest / praise you will get / from me this week.
- *Free time until 9:00. The player may talk to Mia / Dex / Rosa (small talk tutorial appears on the first conversation, see
  Scene 4).* Interface hint on first conversation: SYSTEM| "A = talk. Pick a topic. / People like different / things!"

### Scene 4 - Mr. Pimm's rye loaf (9:00, mission M03)
*A bell rings. Mr. Pimm enters, flat cap, stick. He walks to the bread shelf, stops, frowns.*
- PIMM| Good morning, my dear. / One rye loaf, please. / Same as yesterday.
- MIA| Same as the last / 14,000 days, Mr. Pimm. / ...Oh. The shelf is bare.
- ROSA| {NAME}, the rye is in / the storeroom. Second / crate on the left.
- *Objective: "Fetch the rye loaf from the storeroom."* Interactable: storeroom crate (A: "Take the rye loaf", info
  "You carry the rye loaf.") then talk to Mr. Pimm.
- PIMM| Splendid. A good loaf / is like a good bridge. / Solid. Honest. Rye.
- PIMM| Do you have a minute? / I rarely get to chat / these days.
- *First small-talk menu opens (tutorial): three random topics out of eight.* SYSTEM| "The bar shows how he / feels about you. Red is bad. / Green is good."
- After one topic (any):
  - PIMM| Thank you, {NAME}. Come / see me at the library / some afternoon.
- Reward: Pimm friendship +5 (on top of the topic result). (flag: met_pimm)

### Scene 5 - Staff lunch (12:00, part of M03)
- MIA| Lunch break! Rosa says / eat. Bread is on / the house today.
- *Info: "Mia gave you Bread."* Hunger +15 (eat animation, free). Optional: the player may also buy an Apple ($1) with the
  $0 pocket... not possible (money is $0): info "Not enough money." (teaches the shop menu without the player being stuck).
- MIA| Bread isn't a meal. / It's a hint of a meal.
- *Free time until 14:00.* The clock keeps running; no more scripted tasks. Dex and Mia chat if talked to (extra small talk).

### Scene 6 - Victor Vault arrives (14:00, trigger: clock 14:00 in the shop, mission M04)
*Time freezes at 14:00. Letterbox bars (top/bottom 16 px) slide in. Camera pans from the checkout to the shop door.*

*Beats:*
1. Outside the window, a long **golden car** glides in from the east and stops at the door (scripted sprite, gold sparkle).
2. The door chime rings. **Valet** rolls in first, scans the shop with a blue beam.
3. **Victor Vault** enters, takes off his sunglasses slowly, looks at the ceiling and laughs. Everyone freezes.

- Valet| Scanning... Obsolete / retail unit detected. / Logged.
- VAULT| Hahaha! Look at it, / Bert! Wooden shelves! / A bell on the door!
- VAULT| I am Victor Vault. / You have heard of me. / Everybody has. Billboards.
- ROSA| Mr. Vault. This is a / shop. Are you here to / buy something?
- VAULT| Yes! This shop. And / the building. Bert, the / paperwork!
- Valet| Building purchased at / 09:14 today. New rent: / triple. Effective now.
- ROSA| That is not possible. / I have a lease. / Forty years!
- Valet| Lease terminated. See / clause 94b. Printed in / font size two.
- *Rosa grips the counter. Mia steps forward.*
- MIA| People here know every / customer by name. Mr. Pimm / has his own loaf!
- VAULT| Names. How quaint. / My machines know / everyone by number.
- VAULT| Smart City, my dear. / Self-checkouts. Robot arms. / No queues, no chatter.
- VAULT| Cashiers? Shelves? / People? / So last century.
- *Dex steps out from behind a gondola, straightening his collar.*
- DEX| Mr. Vault, sir! Dex / Corbin. I always said / this place needed...
- DEX| ...modernising! I have / ideas. Spreadsheets. / I am very efficient.
- VAULT| You. Loud one. / You are my manager.
- DEX| Manager?! Me? Sir, / yes sir, thank you / sir!
- Valet| Remaining staff: three. / Recommended action: / dismiss.
- VAULT| Dismissed, Bert. / Everybody else: fired! / Congratulations, you're free!
- *Camera on {NAME}.*
- {NAME}| Fired? But my room / is upstairs! 
- Valet| Upstairs unit is now / VaultTech property. / Access: denied.
- *A VaultTech worker-bot (two small grey boxes on treads) rolls to the stairs door and puts up a **laser gate**. Red bars flicker
  across the doorway.*
- *Rosa walks to {NAME} and presses an envelope into the player's hand.* Money +$20 (HUD shows $20, ding).
- ROSA| Your last pay. Twenty. / It should be more. / It should be so much more.
- ROSA| I'm sorry. I couldn't / keep the shop. Or your / room.
- *Choice menu (3 options, shown with the dialogue):*
  - OPT| It's not your fault.
  - OPT| I'll get it back, Rosa.
  - OPT| ...
- Reply to option 1 (Rosa friendship +5, flag: rosa_comforted):
  - ROSA| You are a good kid. / Don't let anyone / tell you otherwise.
- Reply to option 2 (Rosa friendship +3, flag: vowed):
  - ROSA| Don't promise me. / Promise yourself. And / eat something first.
- Reply to option 3 (no change):
  - ROSA| Say nothing, then. / Silence is honest. / Sometimes it's best.
- *Vault waves a gold-gloved hand.*
- VAULT| By next week this is / VaultMart! Clean, cold, / efficient. Bert, car!
- *Vault and Valet leave. Dex trots behind, then stops at the door and looks back.*
- DEX| Sorry, guys. / Business is business!
- MIA| Business is a bad / friend, Dex.
- *Dex shrugs, hurries to the golden car. The car glides off to the east (VaultTech tower). Fade out.*
- Player objective: "Leave the shop." The player may walk freely, but the shop door is the only usable exit; the stairs gate
  says (info) "Locked. VaultTech property." The exit warp fires after everyone has left (Rosa, Mia exit with the player).

### Scene 7 - Mia's goodbye (14:40, on the pavement outside)
*Mia and {NAME} stand in front of the shop. Rosa walks off east along the avenue pushing a cart with a crate of oranges on it, then turns
right to Old Block (disappears off screen). Mr. Pimm is not present.*
- MIA| Well. That happened.
- MIA| Rosa will be fine. She / has a sister in Old Block. / Stubborn runs in families.
- {NAME}| What about you?
- MIA| I know Lou, he runs / Lou's Diner. Purple house. / He owes me a favour.
- MIA| Here. A coffee voucher. / On Lou. Eat, wash, / and sleep somewhere warm.
- *Info: "Mia gave you a Coffee voucher." (flag: has_coffee_voucher; usable once at the diner counter as a free Coffee.)*
- {NAME}| Where do I sleep?
- MIA| ...Honestly? The park / bench is free. I'm sorry. / I'll find you tomorrow.
- *Choice (affects Mia friendship):*
  - OPT| Thanks, Mia. For all.   (+4 friendship)
  - OPT| I'm fine. Really.         (+1)
  - OPT| Dex is a traitor.         (+2, Mia: "Dex is an idiot with a plan. Worse.")
- MIA| Be tough. See you / tomorrow, {NAME}.
- *Mia walks toward the purple diner. Camera holds on {NAME}.*
- {NAME}| $20, a bench, no job. / Great. Just great.
- *The Corner Market sign over the door is already crooked.*

### Scene 8 - VaultMart transformation (time-skip to 18:00)
*Fade to black on the pavement at 14:50. Text card (3 s): "Four hours later..."  The clock jumps to 18:00 (needs drop by the
elapsed time: Hunger -17, Energy -12, Hygiene -10, Fun -14, Bladder -24). Fade in on the street, dusk.*
- *The shop front is now a different world:* wooden facade replaced by white panels, flower boxes gone, the warm awning swapped for
  a grey one, a huge sign being lowered by a robot arm: **VAULTMART**. Fluorescent flicker. The **area palette snaps to cold**
  (grey/blue, desaturated) in one step with a short white flash and a "bzzt" (flag: corner_market_cold; the city centre
  map stays warm elsewhere except around the shop and the tower plaza - see 'warmth' in CLAUDE.md).
- *The door opens by itself; a speaker plays:*
- SIGN| Welcome to VaultMart. / Have a nice day. / Next customer.
- *Through the window: Dex in a grey blazer paces the aisles, talking into his headset. A self-checkout blinks "OUT OF ORDER".*
- {NAME}| That was fast. / Forty years gone in / four hours.
- {NAME}| OK. Think. Hungry, / dirty, tired. And $20. / Let's survive tonight.
- *Objective (M05): "Survive the night."* Sub-objectives appear one at a time (see Scene 9).

### Scene 9 - First evening: survival tutorial (18:00-23:00, mission M05)
The player is free to roam City Centre. Pop-up hints show when a need goes under 40 (once per need):
- Hunger < 40: SYSTEM| "Your stomach growls. / Eat at the diner or the / shop. Or... check a bin."
- Hygiene < 40: SYSTEM| "You feel grimy. / A fountain or sink / helps."
- Energy < 30: SYSTEM| "You're exhausted. / A bench is a bed. / Sort of."
- Bladder < 25: SYSTEM| "Nature calls. / The park has a public / toilet."
- Fun < 30: SYSTEM| "You're bored. Try a / book at the community / centre."
Checklist in the mission log: **[ ] Eat something  [ ] Freshen up  [ ] Sleep on the bench**.
- **Eat**: diner (open until 22:00; Lou is behind the counter, Mia is not there on Day 1, she starts tomorrow). On the first
  visit: LOU| "New face! Hungry? / I'm Big Lou. / Coffee's on Mia." (the voucher: first Coffee free). VaultMart sells bread
  at $3 (see prices). Bin search is available (bins along the avenue) with a flavour line.
- **Freshen up**: fountain (Wash face, +35 Hygiene) or the sink in the public toilet (+15).
- **Sleep**: bench in City Park (7.3, 39.4) or fountain square. Sit/Sleep menu as now. Sleeping at night on the bench has the
  changed gains from Balance 4.6.
- If the player stays up past 23:00 without sleeping, Energy-based hints repeat; at Energy 0 the player collapses on the nearest
  bench (forced sleep, Fun -5, "You pass out on the nearest bench.").
- Completion: when the player starts sleeping on a bench after having eaten and washed, the mission completes (rewards: none;
  the story moves on). If the player sleeps before eating/washing: mission still completes but wakes up "hungry and grimy" with
  the Hunger/Hygiene penalties applied naturally; no extra text.

### Scene 10 - First night and morning (sleep, Day 2 around 6:00-7:00)
*Sleeping fades to black with "zZz". Optional dream beat (1 page, random 1 of 3):*
- DREAM| A giant golden hand / is rearranging the city / like toy blocks.
- DREAM| Rosa's loaf is bigger / than the tower. It's / warm. It smells of home.
- DREAM| Your alarm rings. Only / it's a pigeon. Standing / on your face.
*Wake: the bench. Hunger/Energy per the sleep rules. A pigeon pecks a newspaper on the ground.*
- {NAME}| Cold bench. Stiff back. / Rock bottom, then.
- {NAME}| Only one direction / from here. Up.
- *A page of **yesterday's newspaper** lies under the bench (auto-read, then mission M06 starts):*
- PAPER| SMART CITY: OLD BLOCK / TO BE "REIMAGINED" / Glass towers and a gym.

---

## 3. Chapter 1 missions

### 3.1 Mission table

| ID | Day | Title | Log text (short) | Trigger | Key rewards | Next |
|----|-----|-------|------------------|---------|-------------|------|
| M01 | 1 Mon | Open Up | Get ready for work. | New game | Wash/toilet tutorial | M02 |
| M02 | 1 | Stock the Shelves | Stock three shelves (0/3). | Talk to Rosa (auto at 7:30) | Rosa +5, Strength +1 | M03 |
| M03 | 1 | The Regular | Fetch Mr. Pimm's rye loaf. | 9:00 | Pimm +5, free lunch | M04 |
| M04 | 1 | Vault Day | Leave the shop. | Clock 14:00 | +$20, Rosa/Mia choices | M05 |
| M05 | 1 | Survive the Night | Eat, freshen up, sleep on the bench. | After M04 (18:00) | none | M06 |
| M06 | 2 Tue | Yesterday's News | Find out what Smart City means. | Wake up | newspaper read | M07 |
| M07 | 2 | Plate Spinner | Get a job at Lou's Diner. | Talk to Lou (Hygiene >= 40) | Diner job, Lou +10, Mia +5 | M08 |
| M08 | 2-3 | Odd Jobs | Do three odd jobs (0/3). | Notice board | +$5 bonus, jobs unlocked | M09 |
| M09 | 3 Wed | Old Block Calling | Follow Mia to Old Block. | 1st diner shift done + Mia chat | Old Block opens, Mia +5 | M10 |
| M10 | 3 | Rosa's Stall | Carry three crates to Rosa's stall (0/3). | Talk to Rosa in Old Block | +$10, Rosa +10, Rosa's stall shop | M11 |
| M11 | 4 Thu | Cold Shelves | Visit VaultMart and see how Dex is doing. | Day >= 4 or M10 done | Dex seeds, VaultMart prices known | M12 |
| M12 | 4 | Old Friends | Find Mr. Pimm in the library. | M11 done, Pimm friend >= 30 | Pimm +8, bridge story | M13 |
| M13 | 5 Fri | Notice Served | Attend Rosa's meeting in Old Block. | Day >= 5 morning (auto notice) | Old Block full, flag | M14 |
| M14 | 5 | Paper Trail | Find the bridge certificate in the library archive. | After M13 and M12 | Pimm +8, Dex doubt +1 | M15 |
| M15 | 6 Sat | Open Sesame | Show the certificate at the bridge. | Have certificate, 14:00-18:00 | Bridge opens, docks flag, Pimm +5 | M16 |
| M16 | 7 Sun | Dock Hand | Meet Foreman Halloran at the Docks (pass $12). | Bridge open | Docks open, steady job, Grafters 1 star, +$12 refund | M17 |
| M17 | 7 | A Roof for the Night | Meet Mia at the bridge after your shift. | Shift done | First night off the bench, chapter end | Chapter 2 |

M05 and M06 are connected: sleeping on any bench completes M05, and the next wake-up starts M06 (Day 2). If the player stays awake
past 24:00 the day counter still advances on the next sleep; M06 starts after the first night's sleep. Missions M07-M08 can be done
in either order, M11/M12 and M13/M14 are semi-parallel (M14 requires both M12 and M13). The mission log shows one **main**
objective at a time; side tasks (odd jobs, small talk goals) are not listed.

### 3.2 M01-M05 (Day 1)
Scripted in section 2. Summary of data: M01 ends when the player leaves the room; M02 ends 3/3 shelves; M03 ends after talking to Pimm
(rye loaf fetched) and eating the staff lunch (12:00-13:30); M04 ends when the player leaves the shop; M05 ends on first bench sleep.

### 3.3 M06 - Yesterday's News (Day 2)
- **Trigger:** Wake up on the bench (first sleep). **Objective:** "Find out what Smart City means."
- **Scene:** auto-read newspaper (headline #1, section 5.2). Then the player is free; the log points to Lou's Diner (purple house).
- **Dialogue (player thoughts after reading):**
  - {NAME}| "Reimagined." / That's a nice word for / "bulldozed".
  - {NAME}| Old Block. That's where / Rosa and Mia live. I / should see them.
- **Reward:** none. (flag: read_paper_1). **Next:** M07.

### 3.4 M07 - Plate Spinner (Day 2)
- **Trigger:** Talk to Lou at the diner (counter). The player wants a job; Lou checks Hygiene.
- **Objective:** "Get a job at Lou's Diner."
- If Hygiene < 40 (gate message):
  - LOU| Whoa, friend. You smell / like a bench. Wash up / first. Then we talk.
- If Hygiene >= 40:
  - LOU| Mia said you'd come. / She talks about you. / Mostly good things.
  - LOU| I need a dish washer. / Four hours, lunch shift. / Sixteen dollars. Deal?
  - OPT| Deal.
  - OPT| Can I eat on shift?
  - OPT| Is there more money?
  - Option 2: LOU| Staff meal is free. / Eat as much as you / can carry. (flag: staff_meal)
  - Option 3: LOU| Plates don't clean / themselves. I add tips / when you're fast. ($0-3 tip)
  - After any option: LOU| Apron's on the hook. / Wash, rinse, repeat. / Welcome to Lou's!
- **First shift** (also the tutorial for the job activity): lunch shift **11:00-15:00** (4 h), pays **$16 + tip $0-3**,
  Energy -10, Hygiene -12, Hunger -6, Fun -8 over the shift, Charm +0, Fitness +1. 8 "plate rushes" (press A when the prompt
  appears; each hit adds to the tip, max $3). If the activity is skipped the base wage is still paid.
  - After shift: LOU| Not bad, {NAME}! / Staff meal's on the / house. Sit down.
  - Staff meal: Hunger +30, Energy +5, Fun +3, free, one per shift (flag: staff_meal needed; first shift always gives it).
  - Mia (on shift) greets: MIA| You came! Lou, I / told you. Best dish / washer in town.
- Other shifts available: lunch 11-15 and dinner 17-21 (dinner pays the same). One shift per day (max).
- **Voucher:** the Coffee voucher (from Mia) works at the counter once as a free Coffee (price $0).
- **Rewards:** wage, Lou +10 (first time), Mia +5. (flags: job_diner, met_barney). **Next:** M08.

### 3.5 M08 - Odd Jobs (Days 2-3)
- **Trigger/Where:** Notice board in the community centre. **Objective:** "Do three odd jobs (0/3)."
- The board shows 4-5 jobs per day out of the pool in section 5.1 (random but seeded per day). A job is 45-120 game minutes with a
  short animation and a message. Each job can be done once every 3 days.
- First time at the board (info pages):
  - NOTICE| JOBS WANTED. / Take a card. / Do the work. Get paid.
- First time in the library, if Pimm is in: PIMM| Ah, {NAME}. The notice / board. A good place / for honest work.
- **Rewards:** wages of the three jobs + **$5 bonus** (Library Clerk: "Community bonus, three jobs!").
  Skill points per job as listed. (flag: odd_jobs_done). **Next:** M09.

### 3.6 M09 - Old Block Calling (Day 3)
- **Trigger:** First diner shift done and Mia talked to at the diner, or morning of Day 3 (whichever first).
  **Objective:** "Follow Mia to Old Block."
- MIA| Hey, {NAME}. Shift's / over. Come with me. / I want you to see this.
- *Fade. Mia walks ahead along the avenue; the camera follows. At the east end of the avenue the city-centre map transitions
  to Old Block (warm, crowded, patched). Scene: row houses, laundromat, Ines in a window, Teo on a skateboard, a chess table.*
- MIA| Old Block. Cracked / pavement, loud neighbours, / best people in town.
- MIA| That's Ines. She does / your laundry and your / life advice.
- INES| Hello, new face! Your / shirt needs me. Badly. / Two dollars!
- *Teo whizzes past on a skateboard, a stolen orange in hand.*
- TEO| Sorry, Ines! Not sorry!
- MIA| Rosa is at the end of / the street. Come on.
- *Map note: Old Block must have, at minimum for Chapter 1: the avenue entrance, a main street with row houses, the laundromat,
  Rosa's stall spot, Mia's block (exterior only), a chess table, and the **demolition site** entrance (fenced, with VaultTech
  notices). Interiors are not needed in Chapter 1 (Mia's flat is a cutscene).*
- **Rewards:** Old Block opens (flag: old_block_open), Mia +5, Ines/Teo introduced (no friendship tracking). **Next:** M10.

### 3.7 M10 - Rosa's Stall (Day 3)
- **Trigger:** Talk to Rosa at the end of the Old Block street (an old cart with a sun-faded awning).
  **Objective:** "Carry three crates to Rosa's stall (0/3)."
- ROSA| {NAME}! You came. / Look. My new shop: / four wheels and an awning.
- ROSA| A stall isn't a shop. / But bread is bread. And / people still need bread.
- ROSA| The crates are behind / Ines's laundromat. Three. / Bread, oranges, rye.
- *Task:* walk to the laundromat back lot, A on each crate (carry animation, Strength +1 each); walk back to the stall (A to
  put down). 2.5 s per crate plus walking; Energy -4 per crate.
- On completion:
  - ROSA| Strong arms. Good. / You'll be useful, / {NAME}.
  - ROSA| Take ten dollars. And / this is my rule: / nobody pays for kindness.
- **Rewards:** +$10, Rosa +10 (flag: rosa_stall_open), the stall shop opens (items in section 4.2). Rosa now tells her "Forty years"
  story in small talk if asked (Work topic).
- **Next:** M11. (Rosa also says: ROSA| Mr. Pimm asks about you. / He's in the library most / afternoons. Visit him.)

### 3.8 M11 - Cold Shelves (Day 4)
- **Trigger:** Day >= 4 or M10 done, whichever first. **Objective:** "Visit VaultMart and see how Dex is doing."
- *Entering VaultMart (the old Corner Market interior in cold palette, all warm props replaced): white shelves, a floor-cleaning
  robot, 4 self-checkouts (two "OUT OF ORDER"), a pre-recorded announcement at the door.*
- SIGN| Welcome to VaultMart. / Please scan your / VaultCard.
- {NAME}| I don't have a / VaultCard.
- SIGN| Please proceed to the / machine. Have a nice day. / Next customer.
- *Dex walks over, headset on, Valet hovering in the back with a clipboard.*
- DEX| Buddy! Look at this! / Zero queues, zero chat. / Efficiency up 40 %!
- DEX| We sell bread now with / a barcode. And nutrient / loaf. It's grey. Ha!
- {NAME}| Where's the rye?
- DEX| Rye? Discontinued. / The data says nobody / wants rye.
- {NAME}| Mr. Pimm wants rye.
- DEX| Mr. Who? Never heard / of him. Oh... the old / guy. Whatever.
- *Valet rolls up behind Dex.*
- Valet| Manager Corbin. Your / efficiency is 94 percent. / Target: 100.
- DEX| Yes, Bert. Working on / it, Bert.
- Valet| Staff are reminded: / smiling is mandatory. / Smile level: 61 percent.
- *Dex forces a smile. For a second he looks tired.*
- DEX| ...It's fine. It's / great. It's what I / wanted.
- *Choice (Dex friendship):*
  - OPT| Good for you, Dex.   (+3, "I know, right?")
  - OPT| You look tired.        (+2, flag: dex_doubt_seed; "I'm fine!")
  - OPT| You sold us out.      (-3; "I got promoted!")
- If the player has $3+: the self-checkout sells Bread for $3 (see prices); the robot voice speaks the lines in 5.3. Otherwise
  nothing happens.
- **Rewards:** flags: visited_vaultmart, dex_seed (if choice 2). Fun -3 (the cold shop is depressing). **Next:** M12.

### 3.9 M12 - Old Friends (Day 4)
- **Trigger:** M11 done and Pimm friendship >= 30 (Day 1 gave +5 plus small talk +; if lower, the log says "Chat with Mr. Pimm to
  get to know him better", i.e. go to the library and talk). **Objective:** "Find Mr. Pimm in the library."
- *Library, afternoon. Pimm at a reading table in the corner, a stack of old books on bridges.*
- PIMM| {NAME}! How good to / see you. Sit down, / sit down.
- PIMM| I heard about Rosa. A / shame. Forty years. Like / a bridge, that shop.
- {NAME}| You like bridges?
- PIMM| Like them? I was the / Chief Bridge Inspector / for 38 years.
- PIMM| Hmm... The bridge to / the Docks. Solid as a / rock. I signed it myself.
- PIMM| And yet the paper says / "closed for inspection". / By VaultTech's own men.
- PIMM| No inspector ever came. / I would know. I am the / inspector.
- {NAME}| Can we prove it?
- PIMM| My certificate is in / the library archive. Third / box. If I remember.
- PIMM| Come back to me when / the dust settles. We'll / look together.
- **Rewards:** Pimm +8 (flag: pimm_bridge). Library Reading Fun is available as usual. **Next:** M13.

### 3.10 M13 - Notice Served (Day 5, morning)
- **Trigger:** First time entering Old Block on Day 5 or later; or auto at 9:00 if M12 is done. **Objective:** "Attend Rosa's
  meeting in Old Block."
- *Old Block, morning. Orange VaultTech notices are glued to every wall (poster set in 5.6). People gather round Rosa's stall:
  Mia, Ines, Teo, a man with the chess table, Mr. Pimm leaning on his stick.*
- INES| "Demolition notice. In / thirty days." Thirty / days! My laundromat!
- TEO| They said it'll be / glass towers. With a / gym. I hate gyms.
- ROSA| Quiet, all. First the / facts. Mia?
- MIA| The notice says the / city agreed. It also says / "for the greater good".
- ROSA| Greater good is what / people say when they want / your house.
- PIMM| Allow me. This isn't / legal until it's signed / by the city engineer.
- PIMM| There isn't one. They / fired him. I'm the last / retired one.
- ROSA| So Vault is bluffing? / ...Or hurrying.
- MIA| He's hurrying. And the / Docks are cut off by a / closed bridge.
- MIA| Closed bridge, no / dockers. No dockers, / nobody to back us.
- ROSA| Then we open the bridge.
- ROSA| {NAME}. You're the only / one without a job to / lose. Help us.
- *Choice (Rosa friendship):*
  - OPT| I'm in.                  (+5)
  - OPT| What do I get out of it?  (+0, Rosa: "A reason to wake up.")
  - OPT| It's too big for us.      (-2, Rosa: "Big things start small.")
- Any option: flag: committed (always; the player cannot refuse the main story, just choose the tone).
- **Rewards:** flag: demolition_known. Old Block fully visible with demolition site. The closed bridge shows a distant figure
  (Halloran, waving across the river). **Next:** M14.

### 3.11 M14 - Paper Trail (Day 5)
- **Trigger:** M13 done and M12 done. **Objective:** "Find the bridge certificate in the library archive."
- *Library. Pimm hands the player an old brass key.*
- PIMM| The archive is behind / the librarian's desk. / Three boxes. Careful.
- *Task:* Three archive boxes in the community centre (new interactable `archive`, 3 spots). Each search = 30 game minutes, Logic +1,
  "You sift through old papers." Boxes 1 and 2 are empty (flavour: "Tax forms from 1974.", "Photos of a duck."). Box 3 holds the
  certificate. (Random order is fixed: box 3.)
- On the third box:
  - {NAME}| "Bridge 7, Docks. / Inspected: A. Pimm. / Condition: excellent."
  - {NAME}| That's it! Signed / and stamped. VaultTech / has no case.
- *The player brings the certificate to Pimm.* PIMM| Stamped by the city. / A good piece of paper. / Take it. I'll follow.
- **Dex encounter (mandatory, 15:00-16:00 while the player is in the library):** *Dex walks in with a VaultTech tablet, sent to
  measure the library for "repurposing".*
  - DEX| Buddy? What are you / doing here? Reading / now?
  - OPT| Just reading.     (Dex: "Boring. Fine.", flag: hid_cert)
  - OPT| A bridge certificate.   (Dex friendship +3, flag: dex_saw_cert)
  - If dex_saw_cert: DEX| ...Don't show that to / Bert. I didn't see it. / I mean it.
  - If hid_cert: DEX| Fine. Don't strain / your eyes. I have / a library to scan.
  - Either way: *Dex stays a moment too long beside the shelf, then leaves.* (flag: dex_doubt = 1)
- **Rewards:** Pimm +8, certificate item (flag: has_certificate), Logic +3 total. **Next:** M15.

### 3.12 M15 - Open Sesame (Day 6)
- **Trigger:** has_certificate and clock between 14:00 and 18:00 (Pimm walks slowly, he arrives at the bridge at 15:00 if the
  player waits for him in the park or goes there first). **Objective:** "Show the certificate at the bridge."
- *South of the City Centre, riverside walk. The closed barrier with a CLOSED sign. Guard **Kessler** stands in front. On the other
  bank, Halloran leans on a crane, arms crossed.*
- KESSLER| Bridge is closed. / Inspection. Move along.
- {NAME}| I have a certificate. / It says the bridge is / sound.
- KESSLER| Not authorised. / Authorised persons only. / That's me. Not you.
- *Pimm arrives with his stick, in a suit jacket with a dusty badge pinned on it.*
- PIMM| Young man. I am Albert / Pimm, Chief Inspector, / retired. Stand aside.
- KESSLER| Sir, uh... only Mr. / Vault's engineer can / certify a bridge.
- PIMM| Then show me his / certificate. I'll wait.
- KESSLER| I... don't have it, / sir. I'll call Bert.
- *Close-up of a small speaker on Kessler's belt.*
- Valet| Guard Kessler. State / your request.
- KESSLER| An old man claims the / bridge is safe, Bert.
- Valet| Checking records... / Certificate valid. / Closure order invalid.
- Valet| Contacting Mr. Vault. / ...Mr. Vault is playing / golf. Please hold.
- *Hold music plays for two bars (the in-game jingle). Kessler looks at the sky.*
- KESSLER| ...The order has no / signature. I'm not paid / enough for this.
- *Kessler lifts the barrier. The CLOSED sign is removed, cones disappear (flag: bridge_open). Halloran across the bridge nods once.*
- PIMM| Thank you, young man. / Remember: a bridge is / a promise. Keep it.
- **Rewards:** bridge opens, Pimm +5, Halloran noticed the player (flag: halloran_aware), Charm +1. **Next:** M16.
- *The Docks gate (VaultTech levy):* a small booth at the Docks end of the bridge charges a **Dock Access Levy of $12** per person
  per day (flag: levy_known). Without $12 the info reads: "Docks gate: Access levy $12." If money < 12: Halloran at the gate says
  "Come back with the levy. Or earn it. I don't hire beggars." (soft lock until the player has $12.)

### 3.13 M16 - Dock Hand (Day 6-7)
- **Trigger:** bridge_open. **Objective:** "Meet Foreman Halloran at the Docks (pass $12)."
- *At the gate: levy booth (info: "Pay the levy?" Yes / No, $12). Then Halloran on the dock.*
- HALLORAN| You. The certificate / kid. Name?
- {NAME}| {NAME}.
- HALLORAN| I need hands. Heavy / ones. Four crates in / sixty seconds. Go.
- *Trial task (short stacking test): carry crates from a pile to the truck. Strength skill matters; 4 crates in 90 s is a pass,
  otherwise she lets the player retry once per day. Placeholder for the real "stacking boxes" minigame in Chapter 2.*
- On pass:
  - HALLORAN| Not bad. You show up. / You work. You don't talk / too much. Hired.
  - HALLORAN| Six hours a day, $6 / an hour. Start at six / sharp. Late is rude.
  - {NAME}| (Rosa's rule!)
  - HALLORAN| The levy? Refunded. / The Docks don't charge / the ones who work here.
- **First shift:** *Immediately after hiring, a first 6-hour shift starts at the current time if it is before 14:00; otherwise next morning at 6:00.* Shift: Energy -25, Hunger -15, Hygiene -15, Fun -10, pays **$36**. (flag: job_docks)
- **Rewards:** +$12 refund, steady job (Docks hand, $6/h), Halloran +10, Grafters reputation +20 (1 star), Strength +2. **Next:** M17.

### 3.14 M17 - A Roof for the Night (Day 7)
- **Trigger:** First Docks shift done (or Day 7, 17:00 if the player prefers). **Objective:** "Meet Mia at the bridge after your shift."
- *Evening at the bridge. Mia waits with a paper bag of Lou's leftovers. Sunset, warm palette.*
- MIA| There you are! Smells / like fish and diesel.
- MIA| Lou sent leftovers. / And Rosa says you / need a real bed.
- {NAME}| I have a bench.
- MIA| You have a bench. I have / a couch, a blanket, and / one condition.
- {NAME}| What?
- MIA| No singing in the shower.
- *Choice:*
  - OPT| Deal.                      (Mia +5)
  - OPT| What if I'm good?          (Mia +3, "You won't be.")
  - OPT| I can't take your couch.   (Mia +2, "It's not charity. It's Mia.")
- MIA| Come on. Old Block is / lovely at night. And / noisy.
- *Fade to Old Block at night (warm, lit windows). The player ends the walk in front of Mia's laundromat door. Cut to Mia's
  flat (cutscene only, no map): a couch, a lamp, a plant. Mia hands over a blanket.*
- {NAME}| Thanks, Mia. For / everything.
- MIA| Sleep. It's a big / day tomorrow.
- *Fade. Text card: "Day 7, 23:30. First night not on the bench."* Needs: energy and hunger refill with "couch" rules (as a rented
  room later: sleep_energy 0.5, hygiene unaffected).
- *Chapter end card (scrolling):*
  - CARD| CHAPTER 1: SURVIVE / complete.
  - CARD| The Docks are open. / Chapter 2: GET BY
  - SYSTEM| "Save your game in the / pause menu."
- *Epilogue beat (post-fade, a short cutscene stinger, 3 pages):* Vault in his tower watches a screen with the bridge open.
  - VAULT| Open? Who opened my / bridge?! Bert!
  - Valet| Unknown. A retired / inspector and a person.
  - VAULT| Find the person. / Smart City does not / wait for people.
- **Rewards:** flags: night_off_bench, ch1_done, docks_open. Mia +5. Unlocks Chapter 2 (Docks, Grafters, rented room).

---

## 4. Balance sheet

Guiding rules: (1) the player starts poor but never has to starve: $20 buys about 4 days of cheap food; (2) work pays less per
hour than odd jobs but is reliable and feeds you; (3) every job costs needs so the HUD matters; (4) Chapter 1 takes **7 in-game
days (6-8)**, roughly 2 hours of real play including the sleeping fast-forward.

### 4.1 Start values (new game, 7:00, Day 1)

| Item | Value | Why |
|------|-------|-----|
| Money | $0 (becomes $20 at the firing) | The $20 is Rosa's "last pay" - the story beat |
| Hunger / Energy / Hygiene / Fun / Bladder | 70 / 85 / 70 / 60 / 55 | Fresh from a real bed; a toilet visit is a natural first tutorial |
| Clock | 7:00 | Wake-up scene |
| Skills (Strength, Creativity, Logic, Charm, Fitness) | 3 / 2 / 3 / 2 / 3 | Small non-zero numbers so gains are visible |
| Reputation | 0 stars for all five types | Docks hire gives the first star |
| Friendship (start) | Mia 40, Rosa 30, Pimm 25, Dex 5, Lou 0, Halloran 0 | Coworkers already know you |

Checked: at 14:00 Day 1 the needs would be about Hunger 41 (before the free lunch), Energy 65, Hygiene 57; at 18:00 (after
the time-skip) Hunger ~39, Energy ~52, Hygiene ~44, Fun ~35. This matches the tutorial hints (Hunger < 40, Hygiene < 40).

### 4.2 Prices and items

Existing items (kept unless marked): shops use `market_items` / `diner_items` (price, quality, Hunger, Energy, Fun, Bladder).

| Seller | Item | Price | Q | Hunger | Energy | Fun | Bladder | Change |
|--------|------|-------|---|--------|--------|-----|---------|--------|
| Corner Market (warm, Day 1 only) | Bread | $2 | 1 | +15 | +3 | 0 | 0 | kept (free via Mia on Day 1) |
| Corner Market | Apple | $1 | 1 | +6 | +1 | 0 | 0 | kept |
| Corner Market | Ready meal | $5 | 2 | +35 | +8 | 0 | 0 | kept |
| Corner Market | Soda | $1 | 1 | +4 | +3 | +4 | -8 | kept |
| **VaultMart (cold, from Day 1 evening)** | Bread | **$3** | 1 | +15 | +3 | 0 | 0 | **+$1** |
| VaultMart | Apple | **$2** | 1 | +6 | +1 | 0 | 0 | **+$1** |
| VaultMart | Ready meal | **$7** | 2 | +35 | +8 | 0 | 0 | **+$2** |
| VaultMart | Soda | **$2** | 1 | +4 | +3 | +4 | -8 | **+$1** |
| VaultMart | Nutrient loaf (new, grey) | $2 | 1 | +12 | +2 | -3 | 0 | **new** |
| Diner | Coffee | $2 | 2 | 0 | +15 | +5 | -10 | kept |
| Diner | Pancakes | $4 | 2 | +25 | +8 | 0 | 0 | kept |
| Diner | Burger | $6 | 3 | +40 | +12 | 0 | 0 | kept |
| Diner | Soup of the day | $3 | 2 | +22 | +5 | 0 | 0 | **new** |
| Diner staff meal (free, after a shift) | Staff meal | free | 2 | +30 | +5 | +3 | 0 | **new** |
| Rosa's stall (Old Block, from M10) | Rosa's loaf | $2 | 2 | +18 | +4 | +2 | 0 | **new** |
| Rosa's stall | Orange | $1 | 1 | +7 | +2 | +1 | 0 | **new** |
| Rosa's stall | Rye loaf | $3 | 2 | +16 | +3 | +1 | 0 | **new** (Pimm gift) |

Rationale: the diner is the best value for Hunger per dollar for a full meal (Burger +40 for $6), bread is cheapest per hunger
point in the warm market and at Rosa's stall ($1 per ~9 points); VaultMart is deliberately ~50 % worse so the player feels
the cold shop.

### 4.3 Jobs and wages

| Job | Hours | Pay | Per hour | Needs per shift | Skills | Notes |
|-----|-------|-----|----------|-----------------|--------|-------|
| Dish washer (Lou's Diner) | 4 (11-15 or 17-21) | **$16 + tip $0-3** | $4 + tip | Energy -10, Hygiene -12, Hunger -6, Fun -8 | Fitness +1 | + free staff meal; once per day; Hygiene >= 40 to start |
| Odd jobs (notice board) | 0.75-4 | $7-16 (avg $9/h) | ~$9 | per job, see 5.1 | per job | board refreshes daily; each job once per 3 days; no job if Energy < 20 |
| Rosa's crates (M10) | ~0.5 | $10 | - | Energy -12 | Strength +3 | story reward |
| Library Clerk bonus (M08) | - | $5 | - | - | - | after 3 odd jobs |
| Dock hand (Docks, from M16) | 6 (6:00-12:00 or 12:00-18:00) | **$36** | $6 | Energy -25, Hunger -15, Hygiene -15, Fun -10 | Strength +2, Fitness +1 | steady job; first star Grafters |
| Dock levy | - | -$12, refunded when hired | - | - | - | one lump sum so the player needs $12 |

Why: odd jobs pay more per hour but are random and cost a lot of Energy; the diner is lower but safe, pays in food, and builds
friendship with Mia and Lou. Docks pay best and give reputation (a reason to move on to Chapter 2).

### 4.4 Needs

Decay per game minute stays as in `tl_needs.h`: Hunger -0.07, Energy -0.05, Hygiene -0.04, Fun -0.06, Bladder -0.10
(per hour: -4.2, -3.0, -2.4, -3.6, -6.0). A day awake (16 h) costs about Hunger -67, Energy -48, Hygiene -38, Fun -58.
Keeping the bar over 50 needs about **$4-6 of food per day** (less on diner shift days).
- Needs high bonus (from CLAUDE.md): if all five needs >= 60 when starting a work shift, wage +10 % (rounded up) and skill gains x1.5.
- Needs low penalty (**new**): any need <= 15 gives -25 % wage; Hunger = 0 doubles Energy decay and shows "You're starving."
- Accident (Bladder 0): unchanged (Hygiene -30, Fun -10, Bladder 60).
- Activities: unchanged reading (+Fun, 30 game minutes), toilet speeds, fountain gains.

### 4.5 Friendship and small talk

- **Small talk:** pick a topic (3 random topics offered out of 8 per round, always including at least one the NPC likes on
  the first conversation of a day). Result before mood: **Like +6, Neutral +2, Dislike -4.** Mood Good x1.5 (likes +9, neutral +3),
  Grumpy x0.5 (likes +3, neutral +1). Dislike is not softened by mood. Friendship never drops below 0.
- **Repeat falloff** (per NPC and topic, memory of 3 game days): 2nd time x0.5, 3rd time and later 0 ("We just talked about
  that."). Repeated dislike: -6.
- **Conversation length:** up to 3 topics; ends early after 2 dislikes ("I should go.").
- **Daily cap:** at most +12 friendship per NPC per day from small talk. Story choices and tasks are not capped.
- **First talk of the day:** +1 (just for saying hi).
- **Treats (gifts):** buy an item for an NPC at their place (Mia: Coffee/Pancakes, Rosa: Bread, Pimm: Rye loaf, Lou: Coffee,
  Dex: Coffee). Favourite +6 to +8, other food +2. Not usable with bin food.
- **Story choices:** +2 to +5 for kind, +0 for neutral, -2 to -3 for rude (see missions). Mission completions: +5 to +10.
- **City Coins at 70+:** reaching 70 the first time gives **3 City Coins**; afterwards **1 coin** on the first conversation of
  every third game day. Prices of perks are chapter 2 business (suggest 5-15 coins).
- **Expected end of Chapter 1 (normal play):** Mia ~75, Rosa ~72, Pimm ~68, Lou ~35, Dex ~12 (up to 25 if kind), Halloran ~20.
- Moods per day: random roll at 6:00 (Good 30 %, Neutral 50 %, Grumpy 20 %) shifted by the NPC's base mood and recent events.

### 4.6 Sleep

| Place | Energy per game minute asleep | Other |
|-------|-------------------------------|-------|
| Park bench (changed) | **+0.3** (was +0.5) | Hygiene extra -0.03/min, Hunger decay halves (as now), after 5 h asleep Fun -10 ("stiff back") |
| Mia's couch (M17) | +0.5 | no penalties |
| Rented room (Chapter 2) | +0.6 | Hygiene normal |

Sleep ends when Energy reaches 100, or at 7:30, whichever comes first, but never before 4 hours (so a short nap needs the "Sit"
option). Asleep time runs at 4 frames per game minute (15 min per real second, as now). Example: sleeping from 22:30 with Energy 35
needs 217 game minutes = about 14 real seconds.

### 4.7 Bins

Cooldown 60 game minutes per bin (unchanged). Result odds (**changed**: still 35 % useful food-or-money, but with variety and a rare find):

| Result | Odds | Effect |
|--------|------|--------|
| Food scraps | 30 % (was 35 %) | 60 % half sandwich (Hunger +12, Hygiene -12), 25 % stale roll (+8, -8), 15 % bruised apple (+5, -5) |
| Coins | 20 % (unchanged) | $1-3 (uniform), Hygiene -5 |
| Rare find | 5 % (**new**) | lost coin purse $5, Hygiene -5 |
| Nothing | 45 % | "Nothing useful." Hygiene -5 |

Expected value per search: about $0.65 plus ~2.7 Hunger, at the cost of ~7 Hygiene. A search is not a way to get rich, only to
bridge a bad evening (Day 1).

### 4.7a Can and bottle deposit (RETURN & EARN)

A small side income that is always available in the City Centre, built (approved) after the bins. **Owner-approved numbers:**

| Item | Credit | Value |
|------|--------|-------|
| Can | 1 credit | $0.50 |
| Bottle | 2 credits | $1.00 |

- The money stays in whole dollars: **2 credits pay $1**, the remainder (0 or 1 credit) stays on the machine as credit.
- **At most $3.50 worth of loose cans and bottles lie in the district at once** (7 credits; 26 spawn spots in the City Centre).
  The pickups are topped up at **6:00 every day** (only up to the cap, so uncollected ones are not doubled), mix about 60 % cans / 40 % bottles.
- The bag holds **10 items**; "Bag full" until the player returns them at the machine (against the east wall of the park toilet).
- Cost per pick-up (~1.2 s bend-down): **Energy -0.5, Hygiene -1** (-2 in bushes and hedges). B cancels.
- Daily value: the cap is $3.50, so a full sweep plus return takes about 40 game minutes and earns up to $3.50 (only the first day
  after a long break; on a normal day roughly $2-3). Comparable to one cheap meal, never a replacement for a job (odd jobs ~$9/h).
- **Story hook (owner-approved):** Mia explains the RETURN & EARN machine to the player (after the first night).
- Story hook (earlier idea): Mr. Pimm grumbles that "the park machine pays more than your cousin's allowance"; Mia (Day 2) shows the player how it
  works as an optional tip ("Cans are fifty cents. The green machine by the toilets."). It is a bridge on bad evenings, like the bins.

### 4.8 Skills and reputation

- Skills 0-100 points. Chapter 1 targets by Day 7: Strength ~12, Fitness ~8, Logic ~7, Charm ~6, Creativity ~4.
- Gains: shelf stocking +1 Strength each; crates +1 Strength each; odd jobs per table; reading +1 Logic per 3 books; talking
  (any like-topic) +0.5 Charm (round at end of day).
- Reputation: 20 points per star. Sources in Chapter 1: odd jobs of a type +2 points each, Docks hire +20 (Grafters 1 star).
  Makers: lamp painting, murals +2. Ballers: dog walking, paper round +1. Techies: tablet jobs +1. Posh: none.
- Rival rule is not active yet in Chapter 1 (nobody has more than 1 star); keep the code ready: gain at half speed while the
  rival type's reputation is higher.

### 4.9 Day plan and money projection (typical play, ~7 days)

| Day | Story | Typical income | Typical spending | Money at end of day |
|-----|-------|----------------|------------------|---------------------|
| 1 Mon | Firing, VaultMart, bench | $20 (last pay) | $6 (diner meal) | $14 |
| 2 Tue | Newspaper, diner job, first odd jobs | $19 shift + $8 job | $6 | $35 |
| 3 Wed | Old Block, Rosa's stall | $19 shift + $10 Rosa | $7 | $57 |
| 4 Thu | VaultMart, library | $9 job + $8 job | $6 | $68 |
| 5 Fri | Notice, archive | $19 shift + $9 job (+ $5 bonus) | $7 | $89 |
| 6 Sat | Bridge | - | $6 food + $12 levy | $71 |
| 7 Sun | Docks, Mia's couch | $36 wage + $12 refund | $5 | $114 |

Target at the end of Chapter 1: **~$100** (range $50 sloppy to $140 frugal). The first rented room in Chapter 2 should cost about
$60 deposit + $30/week, so $100 makes it a stretch rather than a gift.

### 4.10 Changes to current code (checklist for the programmer)

1. **Starting clock** 8:00 -> **7:00**.
2. **Starting money** $20 -> **$0**; +$20 granted at M04 (story event).
3. **Starting needs** 70/60/50/60/80 -> **70/85/70/60/55** (new game only).
4. **Bench sleep** `sleep_energy` 0.5 -> **0.3** (bench) with extra Hygiene decay -0.03/min asleep outdoors and a "stiff back" Fun -10
   after 5 h; wake rules (Energy 100 or 7:30, min 4 h). Room/couch uses 0.5/0.6.
5. **Bin odds**: sandwich-only 35 % -> 30 % mixed food (half sandwich / stale roll / bruised apple), coins 20 % unchanged,
   **new** rare $5 purse 5 %, nothing 45 %.
6. **VaultMart prices** (replace `market_items` after M04): Bread 3, Apple 2, Ready meal 7, Soda 2, **new** Nutrient loaf $2
   (Hunger +12, Energy +2, Fun -3). The warm Corner Market table is only used on Day 1 (free bread via Mia).
7. **New shop tables**: diner **Soup of the day** $3; **Rosa's stall** items (Rosa's loaf, Orange, Rye loaf); diner **staff meal** (free).
8. **Notice board** `noticeboard` changes from the info message "no jobs posted yet" to a job list (section 5.1). New kinds:
   `archive` (3 boxes), `newspaper` (bench pick-up), `gate_levy`, `crate_pickup`, `stall` (Rosa).
9. **Work activities** (dish washing, odd jobs, dock shift) - new activity type with wage payout and need costs per hour (4.3).
10. **Needs bonus/penalty** at shift start (4.4): +10 % wage when all needs >= 60; -25 % when any need <= 15; Hunger = 0 doubles Energy decay.
11. **Friendship, mood, topic memory** (4.5) and City Coins: new save data per NPC (value, last-talk day, topic memory, mood).
12. **Dialogue system**, story flags, mission state, **save/load** (pause menu "Save", no autosave) - needed before Day 1.
13. **Town flags**: `old_block_open`, `bridge_open`, `docks_open`, `corner_market_cold`; the warm/cold palette per area needed
    at Scene 8 (Corner Market exterior + interior to cold, plus the avenue sign).
14. **Map work**: Old Block (minimal list in M09), the room above the shop (reuse `home_room`), storeroom stairs gate, golden car sprite,
    Valet sprite, levy booth at the Docks end of the bridge, demolition notice props.

---

## 5. Text lists

### 5.1 Notice board odd jobs (community centre)

The board shows 5 cards per day out of this pool. A card text on the board = Title + Description (max 3 lines). Duration in game minutes.
Needs are totals for the whole job (E = Energy, Hy = Hygiene, Hu = Hunger, F = Fun). Skill/rep gains in points. Requirement: Energy >= 20 unless noted.

| # | Title | Description (board text) | Place | Pay | Min | Needs | Skills / rep |
|---|-------|--------------------------|-------|-----|-----|-------|--------------|
| 1 | Dog Walker | Duchess the corgi needs a walk. She pulls. | Old Block -> Park | $8 | 60 | E-8, F+5 | Fitness +2, Ballers +1 |
| 2 | Flyer Hand-out | Hand out Lou's Diner flyers. Smile. | Avenue | $9 | 90 | E-10, Hu-5, F-5 | Charm +2 |
| 3 | Box Mover | Ines needs boxes moved. Bring muscles. | Old Block | $12 | 90 | E-15, Hy-10 | Strength +3, Grafters +2 |
| 4 | Window Cleaner | Library windows. Many windows. | Community centre | $10 | 60 | E-8, Hy-8 | Fitness +1 |
| 5 | Paper Round | Deliver 10 newspapers. Beware of dogs. | City Centre | $11 | 75 | E-10 | Fitness +2, Ballers +1 |
| 6 | Pigeon Patrol | Scrub the fountain square benches. Ew. | Fountain square | $7 | 45 | E-6, Hy-15 | Strength +1 |
| 7 | Recycling Duty | Sort bottles at the community centre. | Community centre | $8 | 60 | E-6, Hy-6 | Logic +1 |
| 8 | Book Sorter | Sort donated books by author. | Library | $9 | 60 | E-5, F+3 | Logic +2 |
| 9 | Take-away Runner | Carry Lou's boxes to Old Block. | Avenue -> Old Block | $10 | 60 | E-9 | Fitness +1, Charm +1 |
| 10 | Lamp Painter | Repaint the park lamp posts. Steady hand. | City Park | $13 | 120 | E-12, Hy-8 | Creativity +2, Makers +2 |
| 11 | Sofa Carrier | Teo's family is moving. Heavy sofa. | Old Block | $15 | 120 | E-20, Hy-12 | Strength +3, Grafters +2 |
| 12 | Night Watch | Guard the fountain square works. 22:00-2:00. Energy >= 50. | Fountain square | $16 | 240 | E-25, F-10 | Logic +1 |
| 13 | Tulip Planter | Plant tulips in City Park. | City Park | $9 | 60 | E-6, Hy-6 | Creativity +1, Makers +1 |
| 14 | Find Biscuit | A cat is missing. Reward $14. Look in the park. | City Park | $14 | 90 | E-8 | Logic +2 (one-time) |
| 15 | VaultMart Tester | "Be misread by our machines." Easy $20. (Warning: VaultTech.) | VaultMart | $20 | 60 | F-12, E-5 | Techies +2; Mia -5, Rosa -3, Dex +5 |

Notes: #15 appears from Day 4 and is the only job with a story consequence (the owner may cut it); it does not block progress.
#12 only appears after dark. #14 appears once (Day 2-6) and the cat is found by A at three park spots (bushes, pond edge, tree).

### 5.2 Newspaper headlines ("The Daily Ledger")

Shown as an info message (up to 3 lines) from the newspaper under the bench and from newspaper boxes. Format: headline lines (max 28) | subline.

1. SMART CITY: OLD BLOCK / TO BE "REIMAGINED" | Vault Developments promises glass towers and a gym. (Day 2)
2. CORNER MARKET SHUT; / VAULTMART OPENS | "Next customer," says robot. (Day 2)
3. VAULT: "PEOPLE ARE SO / LAST CENTURY" | Billionaire arrives in golden car. (Day 2)
4. DOCKS BRIDGE CLOSED / "FOR INSPECTION" | No inspector seen. Dockers wait. (Day 3)
5. BAKER'S CART DRAWS / A CROWD | Rosa Bellini sells 40 loaves in Old Block. (Day 4)
6. PIGEON STEALS LUNCH / IN FOUNTAIN SQUARE | Witnesses: "He was fast." (Day 3)
7. DEMOLITION NOTICES / IN OLD BLOCK | Residents given 30 days. (Day 5)
8. VAULTMART: "EFFICIENCY / UP 40 PERCENT" | Manager Dex Corbin: "Zero chat." (Day 4)
9. RETIRED INSPECTOR: / BRIDGE IS SOUND | Albert Pimm, 74: "I would know." (Day 6)
10. ROBOT CASHIER FREEZES; / QUEUE HITS 30 METRES | VaultMart apologises by voice. (Day 4)
11. VAULTTECH TOWER TO / GROW 20 FLOORS | Taller. Shinier. Bossier. (Day 3)
12. BRIDGE REOPENS; / DOCKS BREATHE AGAIN | Who gave the order? Nobody knows. (Day 7)
13. MISSING: BISCUIT, / A GINGER CAT | Last seen in City Park. (Day 2-5)
14. WEATHER: SUNNY, WITH / A CHANCE OF BILLBOARDS | Vault ads up 400 percent. (any)
15. LOCAL MAN FEEDS / PIGEONS FOR 40 YEARS | "They never complain," he says. (any)

### 5.3 VaultMart robot / announcement lines

Spoken by the door speaker, self-checkouts and Valet. Max 3 lines of 28.
1. Welcome to VaultMart. / Have a nice day. / Next customer.
2. Unexpected item in the / bagging area. Please / remove the item. (the item is you)
3. Please scan your / VaultCard.
4. Item not recognised. / A human has been / alerted. (Dex sighs)
5. Please do not talk to / the machine.
6. Queue length: 3. Please / reduce your presence.
7. Thank you for shopping / efficiently.
8. Prices are now 14 percent / more motivating.
9. Loitering is not / efficient. Move along.
10. Cleaning in aisle 4. / Cleaning in aisle 4. / Cleaning in aisle 4.
11. Smile level: 61 percent. / Please increase.
12. Your receipt has been / emailed to nobody.
13. Rye bread discontinued. / Please try nutrient loaf.
14. Have a nice day. / This is not a request.
Valet-only: "I do not have feelings. I have metrics." / "Smart City does not wait for people." / "Efficiency is a form of love." / "Please hold. Your call is important to a machine."

### 5.4 Bin-search flavour lines

Shown as info lines (2 lines, then the effect). "[F]" = food, "[$]" = coins, "[R]" = rare, "[-]" = nothing.
- [F] Half a sandwich. Still / mostly sandwich.
- [F] A stale roll. A rock / with hope.
- [F] A bruised apple. / Bruises build character.
- [F] A pretzel. Slightly / salty. Slightly used.
- [F] A sandwich in foil. / Someone forgot lunch.
- [$] Coins in a paper cup. / Somebody's loss.
- [$] A crumpled dollar in a / coat pocket.
- [$] Loose change under a / newspaper.
- [R] A lost coin purse! / Finders keepers. $5!
- [-] Nothing useful.
- [-] Only wrappers. Of other / people's good days.
- [-] One shoe. Just one.
- [-] Cold coffee grounds. / Hard pass.
- [-] A broken umbrella.
- [-] Old newspapers. Mostly / bad news.
- [-] A pigeon glares at you / from the lid.
- [-] Gum. So much gum.
- [-] Something moved. You / close the lid. Fast.
- [-] Fish bones. Someone had / a better day than you.

### 5.5 NPC idle barks (shown above the NPC as a speech bubble; 2 lines)

**Rosa**
- "Forty years. And now / a cart. Hmph."
- "Fresh bread! Still / warm, nearly!"
- "Eat something, / {NAME}. You're thin."
- "Never leave the / oranges in the sun."
- (stall) "Good bread needs / no barcode."

**Mia**
- "Order up! Hot plates, / cold stares."
- "I'm not tired. I'm / resting my eyes."
- "Lou sings again. / Help."
- "Old Block is the / best block."
- (street) "Ran into Dex. / Ugh. Needs coffee."

**Dex**
- "Efficiency is the / new black."
- "Bert says I'm at 94. / Bert is a snitch."
- "I'm a manager. / Say it with me."
- "Smile! Mandatory!"
- (doubt, after M14) "...Is this what I / wanted?"

**Mr. Pimm**
- "Ah, the pigeons are / early today."
- "A good loaf is like / a good bridge."
- "I never forget a / bridge. Names, yes."
- "Shh. Library voice."

**Lou**
- "Special today: eat it / or wear it!"
- "Who ordered the / mystery pancake?"
- "Plates! Plates are / life!"
- "Hah! Hello, hello!"

**Halloran**
- "Crane's down. Hands / up."
- "Late is rude. / Late is also fired."
- "Tide waits for no / one."
- "Four crates. Sixty / seconds."

**Kessler (guard)**
- "Move along. / Please."
- "Rules are rules. / Terrible, but rules."

**Ines**
- "Clean shirts, clean / souls! Two dollars!"
- "Teo! Not the / washing machine!"

**Teo**
- "Wanna see a trick? / Look. A trick."
- "Oranges? What / oranges?"

**Valet**
- "Beep. Everything is / fine. Beep."
- "Efficiency: 94 percent. / Disappointing."

### 5.6 Small-talk responses

Player's opener (max 26 chars): Weather "Nice weather today." / Work "How's work going?" / Music "Heard any good music?" / Sports "Did you see the game?" / Gossip "Heard anything juicy?" / Compliment "You look great today." / Joke "Want to hear a joke?" / Complain "Can I complain a bit?"
(L) = likes, (N) = neutral, (D) = dislikes. Each response is one page; the friendship meter moves while it is shown.

**Rosa**
- Weather (N)| Rain tomorrow. My knee / says so. Knees are / never wrong.
- Work (L)| Work is the only thing / that never lets you / down. Good question.
- Music (L)| Puccini on the radio. / Every morning. It keeps / my heart young.
- Sports (D)| Men running after a / ball. I would rather / bake.
- Gossip (N)| I never gossip. / ...Is it about Dex?
- Compliment (L)| Hmph. Thank you. / Flattery works. A / little.
- Joke (N)| Ha. Don't quit your / day job. ...Sorry. / Too soon.
- Complain (D)| Complaining never / stacked a shelf. Pick / up a crate.

**Mia**
- Weather (N)| It's weather. Wet or / dry, I serve the same / coffee.
- Work (D)| Please. I just clocked / out. Ask me on Monday.
- Music (L)| Oh yes! I dance in the / kitchen. Do NOT tell / Lou.
- Sports (N)| Ball goes in the net. / Everyone shouts. I get / it.
- Gossip (L)| Sit down. You will / not believe what Ines / said...
- Compliment (D)| Is this a line? It / sounds like a line.
- Joke (L)| Ha! I'm stealing that. / Lou will pay me in / pancakes.
- Complain (N)| Ha! Same. Life is / hard. We do it anyway.

**Dex**
- Weather (N)| Weather doesn't matter / when you're winning. / Fact.
- Work (L)| Efficiency up 40 %! Do / you know what that does / for a career?
- Music (D)| Noise. Pure noise. I / run on silence and / spreadsheets.
- Sports (L)| Sports! Winners and / losers! Clear scores. / I love it.
- Gossip (N)| I don't gossip. I / network. ...What did / you hear?
- Compliment (L)| Finally someone with / taste. Keep talking.
- Joke (N)| Ha. Wait. Let me / write that down. For / later.
- Complain (D)| Complaints go to Bert. / Bert files them under / "noise".

**Mr. Pimm**
- Weather (L)| A fine day for a / bridge. Clear sky. No / wind. Lovely.
- Work (L)| I inspected 214 / bridges. Each one has / a personality.
- Music (N)| A brass band played / at the opening of / Bridge 7. Fondly.
- Sports (N)| I played bowls. Slowly. / Winning wasn't quick / either.
- Gossip (D)| I prefer facts, my / dear. Facts are / sturdy.
- Compliment (N)| How kind. I shall try / to deserve it.
- Joke (L)| Ha! Very good. I will / tell the pigeons.
- Complain (D)| Complaining is rust on / a bridge. It eats / everything.

**Lou**
- Weather (N)| Rain means soup. Sun / means ice cream. I'm / happy either way.
- Work (L)| The grill never / sleeps. Neither do I! / Hah!
- Music (N)| Radio on all day. I / sing when nobody / listens. Don't tell.
- Sports (L)| The game last night! / Did you see that goal? / Fantastic!
- Gossip (L)| You didn't hear it / from me, but... pull / up a stool.
- Compliment (N)| Ha ha, thank you! The / pancakes say thanks / too.
- Joke (N)| Why is the grill / happy? It's on fire. / Hah!
- Complain (D)| Complaints go in the / grease bin. Eat a / pancake instead.

**Foreman Halloran** (available after M16)
- Weather (L)| Tide's out. Wind from / the west. Good day for / cranes.
- Work (L)| Crates don't lift / themselves. Show up. / Do it.
- Music (N)| Radio on the crane. / Only the news.
- Sports (L)| Tug of war every / Friday on the dock. / Winner gets lunch.
- Gossip (D)| Don't talk behind / backs. Say it to a / face.
- Compliment (D)| Save it. Pay me with / a good shift.
- Joke (N)| ...Hm. That was almost / funny. Almost.
- Complain (D)| Complain to the sea. / It doesn't care. / Neither do I.

### 5.7 Info messages (system)

| Situation | Text (max 3 lines of 28) |
|-----------|--------------------------|
| Too tired for a job | You are too tired. / Rest first. |
| Too hungry to work | Too hungry to work. / Eat something. |
| Too dirty for the diner | Lou says: wash up. / Then come back. |
| Can't afford | Not enough money. |
| VaultTech gate (stairs) | Locked. / VaultTech property. |
| VaultTech lobby | Access denied. / VaultTech staff only. |
| Docks bridge (before M15) | Closed "for inspection". / No inspector in sight. |
| Docks gate | Docks gate: / Access levy $12. |
| Levy can't pay | You need $12 / for the Docks levy. |
| Old Block before M09 | You don't know the way. / Mia can show you. |
| Job already done | You did this one. / Try again in 3 days. |
| Board empty | No more cards today. / Come back tomorrow. |
| Night job only | Night job. / Come back after dark. |
| Shift paid | Shift done! / Wage: $XX. Tip: $X. |
| Staff meal | Staff meal! / Eat up. |
| Voucher used | Coffee voucher used. / Compliments of Lou. |
| Diner closed | The diner is closed. / Open 6:00 to 22:00. |
| Bench at night | Cold, but yours. / For tonight. |
| Collapse | You pass out on the / nearest bench. |
| Starving | You are starving. / Find something. Anything. |
| Saved | Game saved. |
| Chapter end hint | Save your game in the / pause menu. |
| Cat found | You found Biscuit! / He bites. Gently. |
| Certificate found | Bridge 7 inspection / certificate. Stamped! |
| Archive box empty | Only old tax forms. |
| Dex gives way | Dex ignores you. / On purpose. |
| Mia not at work | Mia is not working / today. |

### 5.8 Victor Vault ad slogans and posters

Posters on walls (City Centre, Old Block notices, VaultMart). Max 2 lines of 28 per poster. Colour: gold on black, or white on grey.
1. SMART CITY. SMARTER YOU.
2. VAULTTECH: NO QUEUES. / NO CHAT.
3. WHY WAIT FOR A HUMAN?
4. GOLD STANDARD. / EVERY DAY.
5. THE FUTURE HAS / NO CASHIERS.
6. OLD BLOCK? OLD NEWS.
7. VAULTMART: / NEXT CUSTOMER!
8. BE EFFICIENT. / BE VAULT.
9. VICTOR VAULT: HE BUILT / IT. HE OWNS IT.
10. SHOP. SCAN. SMILE.
11. DEMOLITION IS THE NEW / CONSTRUCTION.
12. YOUR NAME IS A NUMBER. / BE PROUD OF IT.
13. VAULT: FINALLY, / SILENCE.
Demolition notice (orange, Old Block): "NOTICE OF DEMOLITION / In 30 days. VaultTech / Developments."
Counter-posters (Old Block, hand-made after M13): "SAVE OLD BLOCK", "OLD BLOCK HAS NAMES", "BREAD NOT BARCODES".

---

## 6. Owner decisions (answers to the open questions)

- **All proposals in this document are approved** (names Big Lou, Valet, Brenna Halloran, Ines, Teo, Duchess;
  `home_room` as start room; pay level ~$100 at chapter end; slower bench sleep; needs bonus/penalty; the rest as written).
- **Docks gate levy: $12 stays.**
- **Weekdays:** show weekday names (Day 1 = Monday): HUD/pause menu show e.g. "Mon 8:05 am", pause menu "Monday, day 1".
- **Dish-washing minigame at Lou's Diner: yes** (build it instead of a plain wage activity).
- **New: shelf-stocking minigame at Corner Market.** The prologue's tutorial shift is a real minigame; its result
  earns the final pay (the $20 the player has after the firing; a good score can add a small bonus, but the
  story start stays around $20). The same minigame becomes **replayable later as a job once Corner Market is
  warm/normal again** (after VaultTech is beaten there).
- Minigame visuals (screens, sprites) follow the owner's rule: show a design proposal before building.
- **Minigame designs APPROVED** (mock-ups in /tmp/claude-0/s45, generator scripts lib.py/shelf.py/dishes.py):
  - **"STOCK IT!"** (Corner Market, Rosa): 3 sections MILK/CANS/CEREAL, belt with the next 4 items; Left/Right walk,
    A put away, B swap (-2 s); 45 s; 10 pts x combo (x2 at 3, x3 at 6, x4 at 10 in a row); wrong shelf = combo reset,
    -2 s, Rosa's hint; full section +50. Rank C/B/A/S (<400 / 400+ / 700+ / 1000+ or 0 mistakes) pays $18/$19/$20/$22
    in the prologue (Rosa's envelope at the firing). Replay job when the store is warm again: 3 rounds, $4-7 per round,
    4th section (fruit), faster belt, heavy crates (hold A 0.5 s), "Rosa's order" cards; trains Strength.
  - **"PLATE RUSH"** (Lou's Diner): plates ride the counter through SCRUB (A), RINSE (B), STACK (Up); press while the
    plate is inside the [ ] brackets (PERFECT centre / GOOD); greasy pan = mash A x5; a missed step breaks the plate.
    8 rushes of ~5 plates. Wage $16 always; tip $0-3 by PERFECT share (85 %+ with <=1 break $3, 60 % $2, 35 % $1),
    -$1 tip per broken plate (floor $0); **3 broken plates end the shift early (owner decision), wage still paid**;
    free staff meal. Dinner shift +30 % tempo and more pans; fragile glasses (B only) after day 3.

<!-- Previous open questions kept below for reference. -->

## 7. Open questions for the owner (answered in section 6)

1. **Names:** OK with Big Lou (diner), Foreman Brenna Halloran (Docks), Valet (Vault's robot), Ines and Teo (Old Block)?
2. **Moral side job (#15 VaultMart Tester):** keep it as a tempting option with friendship consequences, or cut it?
3. **Old Block scope:** is a minimal Chapter 1 version (avenue entrance, main street, laundromat, stall spot, demolition site, no
   interiors) enough, or should Mia's flat be an enterable map for the last scene?
4. **Room above the shop:** may we reuse the approved shabby `home_room` as the player's start room (it already exists unused)?
5. **Golden car and Valet:** these need sprites. Proposal first (owner rule) - shall we prepare previews of both, plus the VaultMart
   cold look of the shop interior and exterior?
6. **Dock Access Levy ($12) soft lock:** fine as the "pass you can't afford" lock, or do you prefer a free pass from the foreman?
7. **Pay and prices:** are $4/h diner, $6/h docks, VaultMart ~50 % more expensive, and ~$100 at the end of the chapter right,
   or should the game feel tighter (e.g. $60) or looser?
8. **Needs bonuses/penalties** at shift start (+10 % / -25 %) and "Hunger 0 doubles Energy decay": keep, or too punishing?
9. **Bench sleep** now slower (+0.3) with a stiff back: is that the right "rock bottom" feeling or too harsh for a phone game?
10. **Dish-washing minigame (plate rush, press A):** build a small version in Chapter 1, or only the plain wage activity first?
11. **City Coin perk prices** (suggested 5-15 coins): decide in Chapter 2?
12. **Day-of-week names** (Monday ...) shown in the game, or only "Day 1, 2, 3"?
