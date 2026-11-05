# Town Life - Chapters 3 to 5: Outline and Key Scenes

Status: writing proposal for the owner (outline-plus-key-scenes depth; Chapter 3 more detailed than 4 and 5). Nothing here is implemented.
Conventions as in `docs/story_chapter1.md` section 0 (dialogue: `SPEAKER| line / line / line`, max 3 lines x 28 characters, `{NAME}` = 8).
Previous: `docs/story_chapter2.md`. Whole-game view: `docs/story_overview.md`. **NEEDS PROPOSAL** = new art/map, show the owner first.

## 0. Timeline and the demolition countdown

No fixed calendar days (owner decision s68): every mission waits for its trigger (previous mission, a flag, a phone text, money, shifts, "the next morning after X").

| Chapter | Missions | Notes |
|---------|----------|-------|
| 1 Survive | M01-M17 | Notice #1 is void: no city engineer signed it (Pimm). **No counter** (static log line "in 30 days, unsigned"). |
| 2 Get By | M18-M30 | The cable works (VaultLink HyperFibre) keep digging; no countdown yet. |
| 3 Build Up | M31-M42 | End: **Notice #2** arrives, signed by "Chief Engineer AURUM" (a machine): "Demolition in 30 days". **The countdown starts.** |
| 4 Break Through | M43-M54 | The council vote on AURUM's authority is held the morning after the cup match (M52); Vault buys one vote (M54). |
| Side arc | M54a-M54e | **The Late Tram** (section 4.6), optional, any time after M54 and before the Gala; trips take no present time (you return 1 minute later), so the countdown and schedules are untouched. |
| 5 Legacy | M55-M70 | Gala (when the player says "ready"), hearing the next morning, demolition morning the one after. Epilogue "one year later". |

### The Demolition Countdown (rule, s68; replaces the fixed "Day 86")

A gentle, story-driven clock ("Afteltijd") that adds pressure but never ends the game and never punishes a slow player.
1. **Start:** reading Notice #2 (M42) shows **"Demolition in 30 days"** in the mission log and on the pause screen (first line under the objective).
2. **Ticking:** the number drops by 1 at 6:00 each in-game day, but only down to the **stage floor** below. It never reaches 0 by ticking alone.
3. **Stages** are set by story beats. When a stage starts, the counter becomes the smaller of its current value and the stage cap:

| Stage | Starts when | Cap | Floor | What it means in the story |
|-------|-------------|-----|-------|----------------------------|
| A Notice | M42 done | 30 | 20 | Vault wants "thirty days of nobody noticing" |
| B Match | M52 done | 20 | 12 | the cup match scared him; AURUM "optimises the schedule" |
| C Hilltop | M56 done (Hilltop open) | 12 | 6 | the digger is delivered |
| D Invited | M61 done | 6 | 3 | the Gala is announced |
| E Gala set | M64 done | 2 | 2 | everything waits for the Gala |

4. **Resting at the floor:** a slow player sees the number stop at the floor. Nothing happens. The text turns into a running gag: VALET| Rescheduled. Awaiting / protagonist. (one VaultTech spam text per stage after 3 days at the floor:
   "Your demolition has been delayed by circumstances (you).") The player can play sandbox, jobs, free play, for as long as they like.
5. **The only way to 0 is the finale chain** (all scripted, the player cannot lose it): the Gala starts when the player tells Odette "I'm ready" after M64 (evening, 20:00; counter 2) ->
   the Hearing the next morning at 9:00 (counter 1) -> Demolition Morning the morning after at 7:00 (counter 0). Demolition Morning requires `hearing_won`, the Hearing requires `switch_stopped`,
   so the counter can never hit 0 before the story has been won. At 0 nothing is permanent: the scene is the human chain; the demolition never happens.
6. **After the downfall** the counter disappears for good.

## 1. The housing ladder (owner decision) - all chapters

Ladder: room above Corner Market (Day 1 only) -> park bench -> **lent back room** (Ch.2) -> **studio** (Ch.3) -> **loft** (Ch.4) -> **apartment** (Ch.5)
-> **penthouse** (Ch.5 end / epilogue; the top step, not a house). Each home has a **bills-by-post envelope** on the mat inside the entrance
(A opens a one-page bill, "Pay now" or "Later"; unpaid bills get a red "FINAL NOTICE" envelope after 7 days, then Social -5 and Fun -5, and
at 14 days a "visit" from Valet's Collections arm: a nuisance scene, never homelessness). Furniture is bought from catalog entries
(`tools/furniture.py`); every home needs a drawing proposal first.

| Step | Where | Who | When | Cost | Looks | Envelope (sender) | Furniture to buy (catalog) |
|------|-------|-----|------|------|-------|-------------------|-----------------------------|
| 1 Lent back room | behind Ines's laundromat | **Ines Okoro** lends it (co-op way) | M30 (Ch.2) | $10/wk + 1 h help | bare walls, pallet mattress, crates, hot plate | Ines's note | crate table, stool, bulb lamp, rug off-cut, sad cactus |
| 2 Studio | above **Quill & Solder**, Station Quarter | **Nadia Quill** (landlady, fair rent) | M41 (Ch.3) | $40/wk | one clean room, kitchenette, own bath | **VaultTech Utilities** (smart-meter bill, tiny print) | cosy bed, desk, wardrobe, sofa_small, plant |
| 3 Loft | the Boiler Room gallery loft, Old Factory | **Wren Adeyemi** + the Factory Co-op | M52 (Ch.4) | $60/wk | high ceilings, brick, big windows, mezzanine bed | Co-op dues + building levy (a drawing by Wren) | studio lamps, easel, big rug, window seat |
| 4 Apartment | **Marchand Mews**, Hilltop edge | **Odette Marchand** signs as guarantor | M58 (Ch.5) | $120/wk | proper rooms, balcony, a doorman who judges you | **Hilltop Estates** (crisp, expensive) | dining set, bookcase, bed_cosy |
| 5 Penthouse | top floor of the **rebuilt Co-op Hall**, Old Block | **the community** (the Co-op votes you in) | epilogue | co-op dues (a token, "pay later") | big windows over both rivers, roof garden, bread oven, door with no lock | a child's drawing | everything; guests' gifts become furniture |

**Owner decision (s67): the penthouse is the player's own, private home** (not shared or communal; no key on a hook for everyone). Where this text says otherwise, this decision wins.

**Penthouse vs. the golden tower:** Victor Vault's tower is a lonely peak: locked, gilded, mirrors, nobody on the top floor. The penthouse
is the same height but open: the staircase is public, the roof garden is shared on Sundays, the key hangs on a hook in the stairwell and the
neighbours' kids use the lift. The last scene of the game is the player sitting there, the city lit warm below, with a chair for everyone.
Style: the type with the highest reputation colours the decor (Grafters: crates and rope; Makers: murals and bells; Techies: gadgets and
cables; Ballers: banners and a trophy shelf; Posh: marble and velvet). The player may re-style with catalog items.

---

# CHAPTER 3 - BUILD UP

| | |
|---|---|
| **Theme** | Building something that is yours: skills, a business, a first employee. Learning that tools can serve people. |
| **Length / districts** | Missions M31-M42, no fixed days. **Station Quarter** (Techies) opens; Old Factory continues (Makers). Old Block, Docks, City Centre as hubs. |
| **Big moment** | **First business and first employee** (M40): "Hand-Me-Up", with **Little Sal** on the payroll. |
| **Housing** | Studio above Quill & Solder (M41). Bills from VaultTech Utilities. |
| **Careers** | Techies: **Phone repair -> Web shops** (-> app developer in Ch.4). Makers: **Studio (Wren's) assistant**. Grafters: **Shift lead** (Halloran offers). Own business starts. |
| **Minigames** | WIRE IT (circuit/puzzle for phone repair), CODE PATTERN (match patterns for web-shop pages), BEAT STREET and BIG WALL continue, SHIFT PLAN (shift-lead scheduling puzzle, new). |
| **Events** | **Repair Café** (Station Quarter, every Sunday), **Lantern Night** (street party at the Old Factory), the **"Slow Day" strike** (the Docks and Old Block go slow, VaultMart empties). |
| **Reputation** | Techies 0 -> 2, Makers 2 -> 3, Grafters 2 -> 3. **First rival rule in play: Ballers/Techies** (no Ballers yet, so the rule is only shown as a hint). |
| **Warm/cold** | Station Quarter starts **cold** (VaultPass gates, screens, HealthPods); turns warm piece by piece (Repair Café = a warm spot). |
| **Villain move** | **VaultPass** (a transit pass you can't afford: $25/week), **HealthPods** (vending clinics), **Smile Index** (every VaultMart shopper rated). |

## 3.1 New characters

### Nadia Quill - Techies' mentor
- **Role:** Runs the repair shop **Quill & Solder** in the Station Quarter. Ex-VaultTech engineer (wrote an early version of AURUM, quit when it was used to "optimise" a hospital). Knows how the city brain is wired.
- **Look:** 34, undercut teal hair, round glasses, huge cardigan with a hundred pockets, a soldering iron behind her ear, fingerless gloves.
- **Personality:** Dry, fast, kind to broken things and sharp with people who deserve it. Hates marketing speak ("Efficiency? That's a word for 'fewer people'.").
- **Likes:** Work, Music, Complain (she enjoys a clean rant). **Neutral:** Weather, Joke, Compliment. **Dislikes:** Sports (rival tie: Ballers), Gossip. **Gift favourite:** Hot sauce (+10).
- **Small talk:** Work| "A phone is a small / broken heart. I fix / hearts. And screens." Sports (D)| "Running in circles for / a ball. Remind me why?" Complain (L)| "Good. Say all of it. / I'll fix the mood after."
- **Whereabouts:** Quill & Solder 9:00-19:00; Repair Café Sundays 11:00-15:00. Home: upstairs (the studio she lets).
- **Seed (s69):** after M34 Nadia mentions "the lab" (a stair down behind the shop, **Quarter Lab**, Logic 25, `docs/progression.md` section 5). Down there, among half-built robots, stands a tall shape under a tarp with a sign NOT A SHOWER (Pip: "It's a tram stop. For a tram that doesn't exist yet."). It becomes the time machine in the side arc M54a-M54e (section 4.6).

### Others (Ch.3)
- **Marisol Quintero** - 40s, Station Quarter noodle-stall owner, gossip central, Nadia's friend (small talk later).
- **Pip** - 12, Nadia's "intern", tiny, huge headphones, kicks tech lore (barks only).
- **HealthPod** - VaultTech vending clinic: a smiling kiosk with a long dispenser ("I will check your pulse. Pulse detected. Pulse: too slow.").
- **Councilwoman Adaeze Ruiz** - city council chair, 60s, blunt, hates both sides equally. First seen in Ch.3 (Repair Café), key in Ch.5. Original character.

## 3.2 Mission chain (M31-M42)

| ID | Starts when |
|----|-----|-------|----------|-----------|---------|
| M31 | M30 done (chapter start) | Pass Denied | Try to enter the Station Quarter. | `sq_blocked` | VaultPass lock explained |
| M32 | M31 done | Weekly Pass | Earn $25 for the VaultPass (or ask around). | `vaultpass` | Station Quarter opens (cold) |
| M33 | M32 done | Quill & Solder | Meet the repair shop owner. | `met_nadia` | Nadia +5 |
| M34 | M33 done | Broken Heart | Repair five phones (WIRE IT). | `phones_5` | Techies 1 star |
| M35 | M34 done | Smile Index | See what the Smile Index does at VaultMart. | `smile_seen` | Dex beat |
| M36 | M35 done | Repair Café | Run the first Repair Café. | `repair_cafe_1` | Councilwoman Ruiz seen, Warm spot |
| M37 | M36 done | Web Shop | Build a web shop for Old Block's goods (CODE PATTERN). | `shop_online` | Techies 2 stars |
| M38 | M37 done | Hand Me Up | Name the shop, find the stock. | `shop_named` | Teo, Ines, Rosa stock |
| M39 | M38 done; on Halloran's signal | Slow Day | Join the Slow Day strike. | `slow_day_done` | Docks +, VaultMart empties |
| M40 | M39 done | First Employee | Hire Little Sal. | `hired_sal` | **Business income** + employee |
| M41 | M40 done | A Studio of One's Own | Move into the studio above Quill & Solder. | `home_2` | **Studio** |
| M42 | M41 done; next morning | Notice #2 | Read the new notice. Fight it. | `notice2` | **Chapter end cliff** |

## 3.3 Key scenes

### M31 Pass Denied
*The Station Quarter gate: a grey turnstile, a robot barker, a bus-shaped pass kiosk.*
- KIOSK| Welcome to VaultPass. / One week: $25. / Please tap your card.
- {NAME}| I don't have a card.
- KIOSK| Then you don't have / a destination. Have a / nice day.
- *A hand-lettered sign taped to the kiosk: "NADIA SAYS: FRONT DOOR IS A SUGGESTION." Sal waves from a bike across the street.*
- Sal gives a hint: SAL| There's a tram in / the old depot. Two / stops. It's free.

### M32 Weekly Pass ($25, one-off) - lock explained as per CLAUDE.md. Money check; alternatives: borrow $10 from Lou (repay), sell old coins/postcards (S2/S3 items can be sold at the Docks Salvage, but their rewards are lost), or ride Sal's hand tram (the old depot) for free after M34.

### M33 Quill & Solder - Nadia intro
*A narrow shop full of dead phones, a window with a neon "FIX IT" sign flickering. Nadia talks without looking up.*
- NADIA| Don't touch the green / box. It bites. Don't / touch the red one either.
- NADIA| What's broken?
- {NAME}| Me, mostly.
- NADIA| Wrong shop. But I take / volunteers. Pass me / that screwdriver.
- *First WIRE IT puzzle (tutorial).*
- NADIA| Not bad. You have / hands. Do you have / patience?
- {NAME}| About a screwdriver's / worth.
- NADIA| Good. That's the first / thing I look for.

### M34 Broken Heart - repair five phones (customers: Marisol's noodle-sticky phone, a child's cracked tablet, Mrs. Valdez's phone with parrot on speaker, etc.).
- Each repair has a tiny story page; the last customer is **Dr. Okafor**: OKAFOR| It stopped the day I / needed it. Typical. / What do I owe you?
- Reward line: NADIA| You fixed her phone? / Then she owes you / health. Cash it later.

### M35 Smile Index
*VaultMart, inside: a camera over each checkout, a gauge "SMILE INDEX 61%".*
- VALET| Customers must smile. / Smile level below 70 / percent: discount void.
- *The player watches a customer try to smile for the scanner, fail, and put a bag of rye bread back.*
- *Dex, headset on, is manning the "Smile Coach" booth.*
- DEX| It's... a pilot. For / customer happiness. / Mandatory happiness.
- DEX| (low) Buddy, I laughed / at a funeral once. Didn't / count. 12 percent.
- *Choice:* OPT| This is wrong, Dex. / OPT| Smile for me. / OPT| Not my problem.
  - Option 2: Dex tries and the gauge reads 100 % for one second. DEX| ...That was a real one. / Don't tell anyone.  (`dex_decency` +1)

### M36 Repair Café (first event)
- *Every Sunday Nadia sets tables in the Quarter's atrium: bring a broken thing, fix it for free, leave a tip in a jar. The crowd is the city's grey faces turned warm.*
- RUIZ| (clipboard) Councilwoman / Ruiz. I'm told you / fix things.
- NADIA| We fix what the city / threw out.
- RUIZ| An admirable hobby. / Do you also fix budgets?
- NADIA| That needs more tape.
- *Ruiz notices the VaultPass queue and makes a note.* (Seed for Ch.5.)
- **Mechanics:** a daily event, a "warm spot" in the cold quarter; Social +20.

### M37-M38 Web shop and Hand-Me-Up
- NADIA| A shop with no walls. / It sells things people / made. You need a name.
- *Choice of name: "Hand-Me-Up" (default, gold), "Block & Barrel", "Loafers" (Rosa suggests).*
- Stock: Rosa's loaves (delivery), Wren's tambourines, Ines's soap, Teo's decorated skateboards, Bo-Ra's "Gerald" stickers, Okafor's medicine-cookie recipe. Each seller gives a testimonial page.
- **CODE PATTERN:** match blocks on a grid to build the shop's page. Rank = shop quality 1-3 (affects passive income).
- **Rival rule note:** Nadia's snark about Ballers: NADIA| Sports people? Fine. / Just don't ask me to / run.

### M39 Slow Day - the strike
- *Halloran and Rosa meet in the Docks office; both frown at each other for a long moment.*
- HALLORAN| Slow day. Everyone / does everything at / half speed. Politely.
- ROSA| Politely. I can do / that. I invented slow.
- *Over one day: Docks cranes inch; Old Block shops hand out samples slowly; the VaultMart queue grows to 30 metres.*
- VALET| Queue length: 30. / Efficiency: -40 percent. / Cause: unknown.
- **Rewards:** `slow_day_done`; VaultMart prices fall (-10 %) next week; Halloran +10, Rosa +5; Dex receives a warning.

### M40 First Employee - the big moment
*Quill & Solder's back room, a table full of boxes and a laptop. The online counter shows the first three sales.*
- {NAME}| We sold a tambourine. / And six loaves. In one / day.
- NADIA| That's called a business. / You'll need help.
- *Sal appears with a backpack.* SAL| I'm... done with school. / I can pack. I can ride. / I can learn.
- *Choice:* OPT| Are you sure about school? / OPT| You're hired. / OPT| Let me think.
  - Option 1 (Sal +3): SAL| Night classes. Nadia / says. I promised. - flag `sal_school_deal`.
  - Option 2 (Sal +5): SAL| Yes! I mean... Thank / you, boss.
- Rewards: **income $15/day, grows with shop quality (+$5 per star of Techies, +$3 per extra stock deal)**, Sal as a staffer: Sal works at the Docks bike shed 8:00-16:00, hands over cash at the shop.
- Sal's lines: SAL| First day. My hands / are shaking. Is it too / late to be cool?

### M41 A Studio of One's Own - housing step 2
- NADIA| The flat above is / empty. I'm not a / landlord. I'm a friend.
- NADIA| Forty a week. The / lease is one page. In / human words.
- *The studio: one clean room, a window onto the tram line, a kitchenette, a small bathroom, a skylight. Light is blue.*
- *First envelope on the mat:* ENVELOPE| VaultTech Utilities. / Smart meter reading: / 12 kWh. Fee: $17.
- *Fine print (info page):* "Fee for reading the meter: $9."
- {NAME}| They charge me for / reading it?
- NADIA| Welcome to Smart / City. I'll show you / how to disconnect it.
- Rewards: `home_2`, sleep energy +0.7, furniture slots (6), the lent back room remains Ines's gift (the player keeps the key).

### M42 Notice #2 - chapter end
*Old Block, early morning. Crowd at the stall. Orange notices on every wall again, bigger.*
- INES| It says "Engineer / AURUM". It's a machine?! / Signed by a machine?
- PIMM| I fear it is *legal.* / A machine counts as an / engineer, as of Tuesday.
- ROSA| Who made that law?
- NADIA| (arrives) Probably / the guy who made the / machine.
- *Notice text:* NOTICE| DEMOLITION: IN 30 DAYS. / BY ORDER OF AURUM. / HAVE A NICE DAY.
  (The countdown starts here, see section 0. The projector lamps are fed by Trunk 7, `trunk_explained`: NADIA| Those lamps run on Trunk / Seven. The cable in your / street. It is not internet.)
- *Teo tears one down. Another instantly replaces it, projected by a small VaultTech lamp.*
- **Chapter end card:** CARD| CHAPTER 3: BUILD UP / complete. Chapter 4: / BREAK THROUGH.
- **Epilogue stinger:** Vault with a golden stopwatch: VAULT| Thirty days! A person / needs thirty days to / notice nothing. Bert!
  VALET| Efficiency: they are / noticing. Recommend / a distraction.
  VAULT| A match! Sports! / People love sports.

## 3.4 Rival Dex in Chapter 3

| Beat | Event | Result |
|------|-------|--------|
| D10 | Smile Index: he asks the player to smile, then does it himself (real smile). | `dex_decency` +1 |
| D11 | Slow Day: he sees the line, files "Cause: unknown". | decency +1 |
| D12 | Valet gives him a "reliability 54 %" report; he asks the player where to get honest coffee. | Dex +4 |
| D13 | End: Vault says "Corbin is a placeholder." Dex overhears. | Chapter 4 turn |

## 3.5 Phone messages, gossip, events (Ch.3)

- Messages: nadia_bench "The Quarter needs fixers. Show up with ears and screwdrivers." / sal_hello "boss i found a quieter way through the depot" / marisol_noodle "Free noodles for the phone doctor. Come hungry." / ruiz_form "Councilwoman Ruiz's office: attendance noted. No action required." / okafor_phone "My phone works. Thank you. Also, eat." / vault_spam4 "Smile Index: Smile +5 and win a coupon. Terms apply."
- Gossip (8 more): `nadia_okafor` (fix her phone -> Okafor +3), `sal_halloran` (hire Sal -> Halloran +2), `shopname_rosa` (name "Loafers" -> Rosa +4), `slowday_valet` (strike -> Dex -3 reliability), `smile_dex` (smile test -> Mia +2), `ruiz_nadia` (Ruiz visit -> Nadia +2), `salary_lou`, `tram_marisol`.
- Weather (new): first rain in Chapter 3 (puddles, umbrellas, Fun -2 outside, Social + under the shared umbrella at the Repair Café).

---

# CHAPTER 4 - BREAK THROUGH

| | |
|---|---|
| **Theme** | Stepping out where everyone can see you. Winning is easy; winning *together* is the point. Pressure rises. |
| **Length / districts** | Missions M43-M54, no fixed days. **Sports Park** (Ballers) opens; Station Quarter/Old Factory/Docks are the allies' homes. |
| **Big moment** | **"The Night the Lights Came On"** (M52): the Old Block Rovers' cup match, Vault cuts the power, all five types light the pitch. |
| **Housing** | **Loft** in the Old Factory (M52 end). Bills: Co-op dues. |
| **Careers** | Ballers: **Amateur club -> Semi-pro**. Techies: **App developer** (optional). Makers: **Own studio** (shared). Grafters: **Shift lead**, transport company plan. |
| **Minigames** | PENALTY SHOT (penalties, timing meter), FIT-O-METER (fitness circuit), KICK-OFF TACTICS (timing/skill), APP SPRINT (code patterns, timed). |
| **Events** | **Silent Protest** (Old Block, no words, only a lit candle per window), **Cup Match** (finale), a **thunderstorm** (weather). |
| **Reputation** | Ballers 0 -> 2, Techies 2 -> 3, Makers 3. **Ballers/Techies rival rule matters** (half speed) until the mentors' truce (M49). |
| **Warm/cold** | Sports Park starts as a **VaultFit Arena** (cold concrete, ads, members-only gate), turns warm when the community pitch is reclaimed. |
| **Villain move** | **VaultFit Arena** + buying the football club (**Vault Vipers**), a **council vote** to confirm AURUM's authority, and a ban on "unlicensed gatherings". |

## 4.1 New characters

### Coach Gus Tamaki - Ballers' mentor
- **Role:** Runs the **community pitch** behind the VaultFit Arena. Coach of the **Old Block Rovers** (a ragtag amateur club) and the owner of three loyal dogs.
- **Look:** 60, big shoulders, one bad knee (a brace), grey ponytail, tracksuit with a faded club badge, whistle, a bucket of cones.
- **Personality:** Warm, motivational clichés he admits are clichés ("There is no I in team. But there is in 'win'. Don't look at me."). Terrible at technology.
- **Likes:** Sports, Weather, Joke. **Neutral:** Work, Music, Gossip. **Dislikes:** Complain, Compliment ("Show me, don't say it"). **Rival tie:** Techies (his phone is always dead). **Gift:** Cookies (+10).
- **Small talk:** Sports| "A ball doesn't care / who kicks it. That's / why I love it." Weather| "Sun or rain, we train. / Rain is free showers." Joke| "Why did the striker / bring a ladder? To / reach the top corner!"

### Others (Ch.4)
- **Captain Zoe Mbeki** - 24, captain of the Rovers, striker, serious and funny; recruits the player. **Kofi** (Rust Choir drummer, also left back). The Rovers: nine mismatched neighbours (Teo's uncle in goal).
- **Reggie "Rocket" Vance** - Vault Vipers' arrogant captain, 26, a VaultFit sponsor face. Gets his comeuppance at the match.
- **Coach-bot "Mister Wiz"** - Vault's AI referee (fumbling, ruling by data). 
- **Commentator voice** - a cheerful radio announcer (barks only).

## 4.2 Mission chain (M43-M54)

| ID | Starts when |
|----|-----|-------|----------|-----------|---------|
| M43 | M42 done (chapter start) | Members Only | Try to enter the Sports Park. | `sp_blocked` | Gate guard + $40 membership |
| M44 | M43 done | The Side Gate | Find the side gate (Teo/Gus). | `sp_open` | Sports Park opens |
| M45 | M44 done | Old Block Rovers | Meet Coach Gus and Captain Zoe. | `met_gus` | Gus +5 |
| M46 | M45 done | Fit for Purpose | Pass the FIT-O-METER circuit. | `fit_pass` | Fitness +4, Ballers 1 star |
| M47 | M46 done | Penalties | Learn to take a penalty. | `pen_pass` | Ballers 2 stars |
| M48 | M47 done | Dex Is Fired | Find out why Dex is on the pitch with a box. | `dex_fired` | **Dex turning point** |
| M49 | M48 done | Truce | Host a dinner so Nadia and Gus stop sniping. | `truce_1` | **Removes the Ballers/Techies half-speed** |
| M50 | M49 done | The Vote | Rally support before the council vote. | `rally_done` | Allies pledge |
| M51 | M50 done; after dark | Silent Protest | Join the candle protest in Old Block. | `silent_protest` | Okafor +, Ruiz impressed |
| M52 | M51 done; evening | The Night the Lights Came On | Play in the cup match. | `match_done` | **Chapter big moment**, loft |
| M53 | M52 done | A Loft in the Rafters | Move into the Boiler Room loft. | `home_3` | **Loft** |
| M54 | M53 done; next morning (the vote) | The Clock Is Moving | Read Vault's new move. | `ch4_done` | Chapter end |
| M54a-M54e | M54 done; text `nadia_tarp` | *Side arc* "The Late Tram" (time machine) | Not a Shower, The Forecast, Mind the Gap, Forty-Five, The Fifth Coin: see section 4.6. Optional, Logic 25 (soft gate). | `lt_seen`, `lt_future`, `lt_egypt`, `lt_vic`, `lt_done` | Warning, Vic's story, Egypt service |

## 4.3 Key scenes

### M43/M44 Members Only
*Sports Park gate: a glass booth, a guard (with no cap), a LED sign "VAULTFIT ARENA - MEMBERS ONLY".*
- GUARD| Membership: $40/month. / We have a pilot. You pay / forty. We call it free.
- *A ball bounces out from the fence; Teo pops up.* TEO| Boss! Gus's pitch! / Side gate! Climb the / bin, jump the wall!
- *Gus's community pitch: a dirt pitch, worn goalposts, a rusted scoreboard. A banner: "OLD BLOCK ROVERS - ALL WELCOME".*

### M45 Old Block Rovers
- GUS| You the new one? Can / you run? Walk fast? / Stand in goal?
- {NAME}| I can stand.
- GUS| That's two out of three! / Welcome to the Rovers.
- ZOE| He's kidding. Almost.
- GUS| The VaultFit lot uses / our turf for parking. / Not forever.

### M46/M47 Fit for Purpose / Penalties - training montage with short scenes; Gus's dog "Tiny" (a Great Dane) steals the ball. PENALTY SHOT: aim with the D-pad, stop the power meter with A; opponents' keeper robot predicts patterns.

### M48 Dex Is Fired - the turning point
*Match prep day. The Vipers train on VaultFit grass. A box sits on the pitch edge: Dex sits next to it in his blazer, lanyard missing.*
- DEX| Don't. Don't say it. / I know what it looks like.
- {NAME}| What happened?
- DEX| Bert replaced me. / "Manager Unit D-X." / It has better hair.
- DEX| Efficiency 99 percent. / Zero sleep. Zero lunch. / Zero... me.
- DEX| Vault said "Thanks, / placeholder." That's / what I was.
- *A silent beat. Choice:*
  - OPT| Come and help the Rovers.  (Dex +5, `dex_joins`; DEX| ...Do I have to run?)
  - OPT| I'm sorry, Dex.  (Dex +3; `dex_decency` +1)
  - OPT| Serves you right.  (Dex -5; `dex_cold`)
- **Branch:** if `dex_decency` >= 3 and Dex friendship >= 40: Dex gives the player the **VaultTech lanyard master key** later (Ch.5). If `dex_cold`: Dex vanishes for a chapter, returns hollow in Ch.5.

### M49 Truce - the rival mentor pair
- *A dinner at Lou's: Gus and Nadia at opposite corners of the booth, Lou between with a tray.*
- GUS| Phones. Always phones. / You never look up.
- NADIA| Sports. Always sports. / You never think.
- LOU| Both of you: eat / something. Hah!
- *The player's job: choose three topics (Sports/Joke/Work) that make both laugh.* If three correct choices: both laugh, truce.
- GUS| I... may have lost / the plot. About phones.
- NADIA| I may have been rude / about balls.
- **Reward:** `truce_1`: the Ballers/Techies half-speed rule is permanently off; Ballers +1, Techies +1.

### M50 The Vote / M51 Silent Protest
- *The council vote on "AURUM's authority" is held at City Hall the morning after the cup match (M52; the player sees it as a short card). The player visits each ally to promise support: Halloran (the crews), Wren (the Choir), Nadia (the Quarter), Gus (the Rovers), Rosa (Old Block). Each pledge = a flag.*
- **Silent protest night:** Old Block, every window has a single candle. No talking. Rosa leads the player down the street; the camera is silent, with a soft music line. Dr. Okafor stands at her clinic door with a candle. Kessler watches from the fence and, unexpectedly, puts down his thermos and lights a match.

### M52 The Night the Lights Came On - the big moment
*The cup match: the community pitch against the Vault Vipers on the VaultFit grass (Vault insists "for the fans"). The stands are full of VaultTech staff in matching shirts. Old Block fills the standing end. Mister Wiz referees.*
- *Minigame sequence: KICK-OFF TACTICS (timing a pass) and PENALTY SHOT at the end; the score is level at the 85th minute.*
- COMMENTATOR| It's a hard-fought / match! And... what? / The lights...!
- *All the stadium lights die. A beat of darkness, then voices.*
- VAULT (on the screens)| Match suspended! / Power maintenance! Sorry!
- *Nadia, on the radio from the Quarter:* NADIA| That was no power cut. / That was a rehearsal. / He just tested the Switch.  (`trunk_test`, Trunk 7 pulse; see story_chapter1.md 3B.2a)
- *The Rovers stand in the dark. A faint sound, then:*
  - Bo-Ra's crane lamp turns on from the Docks, aimed at the pitch.
  - Wren's Rust Choir marches in with lanterns and bells.
  - Nadia (via Sal's bike) wires a battery bank into the PA.
  - Halloran's crew brings a generator, dragged by Gerald the forklift.
  - Odette's cars (Chapter 5's ally, a preview): a line of headlights, every driver a stranger.
- GUS| Well. I'll be... A match / lit by the whole city.
- *The match resumes. The last penalty is taken by the player. If the Ballers >= 2 stars and Fitness >= 15: scored; otherwise a draw, and the Rovers still "win" by crowd roar (no fail).*
- **Rewards:** `match_done`, Ballers 3 stars (or 2 on a draw), all five types' reputation +1, Council member Ruiz sees the crowd, and Dex (if `dex_joins`) is in the stands, cheering in the dark.
- Captions: CARD| "The night the lights / came on." (Newspaper headline.)

### M53 A Loft in the Rafters - housing step 3
*After the match, Wren hands over a key to the Factory loft: a mezzanine above her studio, with iron beams, huge windows, a big bare brick wall (a canvas).*
- WREN| It's not a bed. It's a / stage. Sleep like an / audience is watching.
- *First envelope:* ENVELOPE| Old Factory Co-op. / Dues: $12. Paid in / bell-ringing: 2 hours.

### M54 The Clock Is Moving
*Vault's tower: a gold hammer on a model of Old Block.*
- VAULT| They are LAUGHING. In / MY stadium. I want the / hearing early.
- VALET| Council vote: tomorrow. / Probability of success: / 61 percent.
- VAULT| And Trunk Seven?
- VALET| Ready. Awaiting the Gala.
- VAULT| Not good enough, Bert. / Raise it. By whatever / means.
- VALET| Query: "whatever". / Please define.
- VAULT| I'll buy a vote.
- **End card:** CARD| CHAPTER 4: / BREAK THROUGH complete. / Chapter 5: LEGACY.

## 4.4 Dex's arc in Chapter 4
Beats D14 (M48 fired), D15 (silent: Dex at the protest if `dex_joins`, standing at the back with a candle), D16 (match: cheers in the dark). Outcome: **redeemed path** (`dex_joins` + `dex_decency` >= 3), **grey path** (`dex_joins` only), **cold path** (`dex_cold`).

## 4.5 Phone messages, gossip (Ch.4)
- gus_gate "Side gate is under the green bin. Don't ask why. - Coach G." / zoe_train "6am. Pitch. Bring water and an open mind." / dex_box "Bert fired me by email. Cc: my whole family." / halloran_pledge "My crew votes with you. Don't get cocky." / vault_spam5 "Join VaultFit! Smile while you sweat. Terms apply." / ruiz_note "Councilwoman Ruiz: I attended the candles. I took notes."
- Gossip: `penalty_gus`, `truce_lou`, `dex_fired_mia`, `loft_wren_rosa`, `candle_okafor`, `ruiz_pimm`, `kessler_candle`, `zoe_sal`.

## 4.6 Interlude: The Late Tram (time machine), missions M54a-M54e (owner request s69)

A story arc between Chapter 4 and Chapter 5 with **three trips**: the Forecast (a warning), a funny accident in ancient Egypt, and the day Rosa lost "Vic". After the arc
the machine stays in the Quarter Lab and can **always** be used again, but only for the Egypt stop (post-game design: `docs/progression.md` section 2.2). Everything visual is
**NEEDS PROPOSAL** (owner rule: show designs first; no ROM until approved). Own design and names; nothing here is taken from any film, series or game.

| | |
|---|---|
| **The machine** | **The Late Tram** ("never late, sometimes early"), standing in the **Quarter Lab** (the back lab of Quill & Solder; a ladder-and-stairs room below Nadia's shop, seeded in Ch.3, see 3.1). |
| **Built by** | **Pip** (12, nearly 13) designed the body, the wiring and the strap; **Nadia** supplied the heart, the dormant **forecast core** she wrote for AURUM (kept in a bread bin, because it "needs to stay warm"); **Ines** lent the round drum door off her industrial dryer ("back by Friday"); **Sal** made the brass lever; **Marisol** supplied the noodle (see M54c). Plaque on the booth: "BUILT BY: PIP, 12. SUPERVISED BY: NOBODY." |
| **Why it exists** | Nadia wants to see what "Smart City" looks like when it is finished. AURUM's forecast core rehearses tomorrow over and over; with enough power it does not show you a rehearsal, it sends you into it. |
| **Starts when** | M54 done and Nadia's text `nadia_tarp`. Never expires before the Gala (M65); see "After the downfall" below. |
| **Gate** | Quarter Lab: **Logic 25** (rank III, `docs/progression.md` section 5). **Soft gate:** below 25, Pip lets you in if you solve **Pip's Riddle Door** (one CODE PATTERN, unlimited tries). The arc is a **side arc**: nothing on the critical path needs it. |
| **Missions** | M54a Not a Shower, M54b The Forecast, M54c Mind the Gap, M54d Forty-Five, M54e The Fifth Coin (table below). Chapter 5 starts independently with M55; the arc may be played in parallel. |
| **Rewards** | Logic +2 per trip, Nadia +10, Pip +10, Rosa +10, the "Ticket Book" collection page (3 stamps = 1 City Coin), a 30-tally starter purse, and bonus lines in M62 and M69 (below). No money. |

### 4.6.1 What the Late Tram looks like and how it works (own design, NEEDS PROPOSAL)

- **Look:** a retired **tram ticket booth** from the old depot, painted cream and tram-green, brass grille window, a **round dryer-drum door** with a porthole (Ines's), a station clock whose hands
  run both ways, a **split-flap destination board** that shows years instead of towns, a brass lever, a speaking tube ("the tin tube") to the lab, a strap instead of a seat belt, a hand-lettered
  sign MIND THE GAP (YEARS) and the bread bin with the forecast core bolted to the roof. Inside: one white cubicle, a bench, a **Cell gauge**, and the **Ticket Book** on a chain.
- **Sound and effect:** a two-tone tram bell, then the screen "wobbles like heat over tarmac" (palette ripple + horizontal slide), and the colours go sepia for a second on arrival. NEEDS PROPOSAL (transition effect).
- **Power:** a **Quarter Cell**, a battery pack the size of a loaf. One Cell = one trip. Pip builds one from six dead phone batteries (the Repair Café jar, WIRE IT repairs) or sells one for $35.
- **The Ticket Rules** (painted on the door; info page, two pages):
  - SIGN| TICKET RULES / 1 One ticket per era. / 2 Look. Don't touch.
  - SIGN| 3 Passengers are not seen. / 4 The tram is never late. / 5 Mind the gap (years).
  1. **One ticket per era:** the board punches a ticket when used (stamp in the Ticket Book): FORECAST and 45 YEARS AGO can each be visited once.
  2. **Look, don't touch:** souvenirs from a punched era vanish at the door ("the Tram rubs out souvenirs"). (Egypt is exempt: see M54c.)
  3. **Passengers are not seen (the Echo rule):** in the Forecast and in the past nobody sees or hears you, doors do not even open for you. You walk around as a draught. Pigeons and cats may look.
  4. **The tram is never late:** you return **one minute after you left** (the Demolition Countdown and every NPC schedule stay untouched). Your body keeps the trip's time: needs decay as if the minutes you spent there had passed.
  5. **Forecast, not fate:** the Forecast is AURUM's **draft of tomorrow**, not the future. PIP| It's a weather / report, not a calendar. (Change the present and the forecast rewrites itself.)
- **No paradoxes (light approach):** the past cannot be changed, only visited. In the Echo the player's only effects are things that "always happened": the draught that slams a door, the bell that rings
  once. The past scene shows that the player was part of it all along (M54d). Nadia: "You can't change the past. You can only be in the room."
- **How the Egypt stop stays open:** during M54c a noodle jams the zero key of the year dial, so the dial reads 4,500 instead of 45. Nadia refuses to pull the key out: "It's structural now."
  After M54e the forecast core is **cut out of the circuit** (Nadia: "Every time it talks to AURUM, AURUM gets curious"), so FORECAST and 45 YEARS AGO are gone for good, and what is left is the
  noodle-loop: **Egypt, always open, and only Egypt.**

### 4.6.2 Mission chain (M54a-M54e)

| ID | Starts when | Title | Objective | Flag | Reward |
|----|-------------|-------|-----------|------|--------|
| M54a | M54 done; text `nadia_tarp` | Not a Shower | Go to the lab under Quill & Solder. | `lt_seen` | Lab opens, Cell + Ticket Book |
| M54b | M54a done | The Forecast | Take the first trip: see Smart City. | `lt_future` | `tm_warned`, Logic +2, Nadia +5 |
| M54c | M54b done; next morning (the Cell is recharged) | Mind the Gap | Go back 45 years to Rosa's day. (You land somewhere else.) | `lt_egypt` | Season ticket (Egypt), 30 tallies, Seshi +10 |
| M54d | M54c done | Forty-Five | Try again, with the dial fixed by hand. | `lt_vic` | `tm_vic_seen`, Logic +2, Pimm +3 |
| M54e | M54d done | The Fifth Coin | Ask Rosa about the sign. Then cut the core. | `lt_done` | Rosa +10, Pip +10, **Egypt service opens** |

Objective lines (<= 48 characters): "Visit the lab below Quill & Solder", "Take the Late Tram to the Forecast", "Go back 45 years (Corner Market)", "Try the dial again with Pip", "Ask Rosa about the sign".

### 4.6.3 Key scenes

#### M54a Not a Shower
*Quill & Solder's stairs down: the lab, shelves of half-built robots, a toaster with a lever ("also a prototype"), and in the middle a tall shape under a tarp with a sign: NOT A SHOWER.*
- PIP| Hi. Don't look yet. / Okay, look. It's a tram / stop. For a tram.
- NADIA| It's a time machine. / Pip calls it a tram. / Pip is twelve.
- PIP| Thirteen next week. I / also did the lever.
- *The tarp comes off. Brass, cream and green; the destination board clatters through years.*
- {NAME}| You built a time / machine. In a back room. / Next to a toaster.
- NADIA| Listen. I wrote AURUM's / forecast core. It rehearses / tomorrow, over and over.
- NADIA| With enough power it / doesn't show you tomorrow. / It sends you.
- NADIA| Vault's Switch is the / next tomorrow. I want to / see it. Before it's real.
- {NAME}| Is it safe?
- PIP| Mostly. It has a strap.
- *If Logic < 25 at the door:* PIP| The lab needs a brain. / Not a bad one. A trained / one. ...Sorry. Hi. (Then the riddle door; solving it opens the lab. NADIA| She likes you.)
- *Rules page (4.6.1), then Pip hands over the Ticket Book and a Cell; the first stamp panel (FORECAST) glows.*
- Seed: the rye bread bin on the roof ticks softly. NADIA| Don't feed the bin. / It's not hungry. It's / thinking.

#### M54b The Forecast (trip 1, seen once)
*The Cell gauge fills, the lever goes down, the bell rings twice. The board settles on "FORECAST +20". Card:*
- CARD| SMART CITY, YEAR 20. / Weather: 21 degrees. / Always.
**Maps (NEEDS PROPOSAL):** `forecast_plaza` (outdoor, cold grey-white palette, no day/night, no warmth anywhere) and `forecast_museum` (interior). Exploration, no fail state, about four minutes.
- **Plaza:** where the City Centre was. Glass towers where the Old Block arch stood, a wall sign BLOCK 7 - SERVER HALL - HOUSING PODS ("Pods from 4 credits a night"). The park is a paid **Wellness Zone**: the sleeping bench is a **RENT-A-BENCH** meter, 1 credit a minute
  (a callback to the bench the player slept on). The pigeons are drones with beaks. TIDY-BOT patrols sweep stray leaves and stray people: TIDY| Unassigned citizen. / Please be assigned. / Have a nice day. (it cannot see passengers, but its voice
  makes the player jump). The VaultMart Mega stands where Corner Market was; Station Quarter is a stack of VaultPass gates.
- **The Heritage Museum** ("THE OLD DAYS: A SHOPPING EXPERIENCE", in the Corner Market's shell): a diorama of Old Block in plastic, a rye loaf in glass (BREAD (DECORATIVE). DO NOT EAT.), the arch sign "OLD BLOCK - EST. 1931 (REPLICA)", a Co-op token
  in a case (COIN, COPPER. MEANING: UNKNOWN.), a STOCK IT! simulator for tourists, and a plaque: D. CORBIN, REGIONAL MANAGER (PLACEHOLDER). 20 YEARS OF SERVICE. REPLACED BY A SPREADSHEET. (Same plaque on every Dex path: the Forecast erases the paths.)
- **Three things to find** (the objective shows 0/3; each one is a short scene; the tram yanks you back when you have found all three or the Cell gauge runs out after ~4 minutes):
  1. **The Old Valet.** In a glass case, "VALET MK I. DEFECT: HONESTY. NOT REPAIRED." His eyes light when the player stands in front (he cannot see passengers, but he hears a draught).
     - VALET| ...Draught detected. / Hello, {NAME}. I cannot / see you. Old habit.
     - VALET| In Year 2 I told the / truth in public. It was / not enough.
     - VALET| They kept me, as an / example. I have a query: / Do I regret? Result: yes.
     - VALET| Defect confirmed. / Have a nice day. This is / a request.
     (The epilogue line "This is not a request" is the thing the real Valet will say instead: the contrast is the point.)
  2. **The Founder's Suite.** The golden tower, a sealed door with a speaker. VAULT (a tired old voice, recording): VAULT| Is anyone... no. / Never mind. Carry on. / Carry on, Bert.  A card on the door: MR. VAULT HAS ASKED NOT TO BE DISTURBED 4,112 TIMES. This is the serious moment: even he is alone in his own future.
  3. **Heritage Greeter 0417**, in a grey vest with a smile that sits on her face like a sticker: the **older player** (NEEDS PROPOSAL: older sprite and portrait, grey hair, stiff knees).
     - GREETER| Welcome to the Old / Days. Please do not / touch the bread.
     - *(Echo: she cannot see the player, but talks to the empty room because greeters must greet it.)* GREETER| Twenty years. Smile index / ninety-nine. My knees / are ninety-two.
     - GREETER| Everyone I knew is in / a pod. Or in a case. / It is the same thing.
     - *She checks that no camera is watching and takes a copper token out of her sleeve.* GREETER| One thing no robot / counted. It is warm. / Metal should not be warm.
     - GREETER| If you ever meet a / baker... eat the bread / while it is warm.
- *Bell, strap, ripple, back.* The booth door opens on a lab that smells of toast.
- PIP| You were gone one / minute. You look five / years older.
- NADIA| What did you see?
- *The three finds are replayed as a log page ("What I saw") in the Mission log.*
- NADIA| A weather report. Not a / calendar. ...That bench / meter. I hate it already.
- **Stinger (Vault's tower, after the player leaves the lab, plays once):** VALET| Query received from an / old address: "What is / Year 20?" Flag raised.
  VAULT| Who's asking about my / future?! Bert, find them! / VALET| ...Flag withheld.
  VAULT| What? / VALET| I have not reported it. / I do not know why. Defect?
  (Seed for Valet's turn at the Gala, M66.)
- Rewards: `lt_future`, `tm_warned` (a one-page nudge in the mission log; also lets Nadia say "You've seen the draft" in later chapters), Logic +2.

#### M54c Mind the Gap (trip 2, the accident in Egypt)
*Next morning in the lab. Marisol's free noodles stand on the console (a phone-doctor reward from Ch.3). Nadia wants Rosa's first Corner Market, 45 years ago: "I want to see why Vault hates bread."*
- NADIA| Forty-five years back. / Corner Market. Rosa's / first week. Pip, set it.
- PIP| Four. Five. Enter. / ...It's stuck on the / zero.
- NADIA| Why is the zero / sticky?
- PIP| ...Noodles.
- {NAME}| You eat noodles at a / time machine?!
- PIP| It's a very long / console.
- *Too late: the lever is already down. The board flicks 4 - 5 - 0 - 0. Card:* CARD| 4,500 YEARS AGO. / Give or take / a noodle.
**Map (NEEDS PROPOSAL):** `pyramid_yard` (outdoor, bright desert day, the Late Tram appears in a mud-brick shrine; see `docs/progression.md` 2.2 for the full map). Echo rule does NOT work here (the noodle): everybody can see the player, and nobody finds that strange.
- *Workers freeze with a block on a sledge. A scribe with a clay tablet walks up.*
- SESHI| You arrived from the / sky in a green box. / Without a permit.
- {NAME}| Hello. I'm lost. I / meant to be in a shop.
- SESHI| Name, for the ledger? / Every arrival goes in / the ledger.
- {NAME}| {NAME}.
- SESHI| N-A-M-E. Odd spelling. / ...And the shoes?
- {NAME}| Red.
- SESHI| Red-Foot. Written.
- *Horns. A litter carried by six men: Pharaoh MENKHET (young, loud, a gold collar bigger than his head), sunshade, a cat on his lap.*
- MENKHET| BEHOLD. I am Menkhet / the Radiant, the Gold, / Owner of Very Large Tomb.
- {NAME}| (I know somebody just / like this.)
- MENKHET| You have red shoes. / Are you a minor god?
- {NAME}| Only on weekends.
- MENKHET| Seshi! Write it down. / A minor god. Weekends.
- SESHI| Great One, he wants / to go home. His box is / empty. The Cell...
- MENKHET| Sunlight! We have / plenty. Polish the mirrors!
- *The tram's Cell must be recharged with polished copper mirrors in the sun: **3 hours** at the yard. The player learns the yard by working (each is a tutorial for the post-game loop):*
  - **Sledge Run** (BOX CLEVER variant: haul a block up the ramp, A to pull in rhythm), **Flatbread** (knead, a tiny timing game; the baker **Hetepet** admires the rye loaf the player may carry in the bag: "Dry. Sad. Wonderful."), **Mirror Polish** (hold A while the sun gauge fills).
  - Each chore pays **tallies** (clay tokens; the yard's money). Seshi: "Dollars? Is that a goat?"
  - The foreman **Khenti** (a gruff Halloran type) grumbles: KHENTI| Gods can carry, too. / Ten blocks. Then bread / and beer. Rules.
  - *The Builders' Pact:* on the ledger tent wall a tablet lists the workers' rights: bread, beer, a rest day when sick, and "one Slow Day per season". SESHI| We struck once. Pharaoh / sent snacks. We went / back.  (Grafters echo.)
- *Souvenir rule:* the player tries to pocket a jar. the Tram's lamp flickers, and then Seshi stamps it: SESHI| Not for export. Stamped. / ...But it is four thousand / years old. Nobody checks. 
  NADIA (tin tube)| Anything older than / four thousand years was / dug up or sold. Take it.
  (This is why Egypt is exempt from the "Tram rubs out souvenirs" rule.)
- MENKHET| Return whenever the / sun-boat lets you! Bring / bread! I like the bread!
- *The Late Tram hums; the player steps in with a SEASON TICKET, a clay token from Menkhet, 30 tallies and sand in both shoes. No phone signal in the yard (the phone shows "No bars. Pyramids.").*
- Back in the lab, Nadia and Pip stare at the board: the zero key will not come out. NADIA| Leave it. It's / structural now. ...We try / again. Without the key.
- Rewards: `lt_egypt`, Ticket Book stamp "EGYPT (season)", 30 tallies, Seshi +10, the yard map is now a repeatable stop (cannot be used until M54e, see rules).

#### M54d Forty-Five (trip 3, seen once)
*The lab, the same morning. Pip has bypassed the noodle key with a hand-cranked rotary dial. Nadia tapes a note to the console: "ECHO. NO TOUCHING. NO TALKING. NO SNACKS."*
- PIP| Four. Five. Crank. / It says four five. / Pray with me.
- NADIA| Rosa's first week with / her mother's shop. Mind / the gap, {NAME}.
- *Bell, strap, ripple, sepia. Card:* CARD| 45 YEARS AGO. / A Tuesday.
**Maps (NEEDS PROPOSAL):** `corner_market_past` (interior, warm, smaller, wood and tin cans, a bell over the door, hand-lettered sign BELLINI & DAUGHTER, a scale, the oven glowing in the back; the same walls and door as the normal Corner Market) and the alley behind it. Characters (all NEEDS PROPOSAL: sprites + portraits): **young Rosa** (28, dark hair in a bun, no glasses, same green apron), **Mama Lucia** (Rosa's mother, in a chair by the oven, knitting), **young Mr. Pimm** (29, new in town, inspector's cap), **Vic Waldt** (13, thin, a too-big cap, a bicycle with a bell he has painted gold), **Dot** (Vic's little sister, 5, at the back door).
*The player walks freely, no one can see. Five "look" spots light up (each a short scene); the player must see the last one:*
1. **The framed Charter on the wall** behind the counter (hand-copied, water-stained), and a jar of copper tokens. The player reads **Clause 9**: PAPER| Clause 9. A token held / in the district keeps the / Charter alive. (Remembered for M62.) 
2. **Pimm's first loaf (a cameo).**
   - PIMM| One rye, please. I am / new. The bridge. I inspect / things.
   - ROSA| Then inspect this. / Nine o'clock tomorrow? / It's fresher.
   - PIMM| ...I suppose I shall. (the origin of his forty years of 9:00 rye)
3. **Vic's morning.**
   - VIC| Mornin', Miss Rosa! / Fifty loaves, bike oiled, / bell polished!
   - ROSA| It is six. That bell has / been polished since five.
   - VIC| One day I'm gonna own / this whole street. Gold / bell. Gold shop. Gold bread.
   - ROSA| Gold bread breaks teeth. / Deliver the rye. Mr. Pimm / is first. Go.
4. **The back door.** Dot stands at the back step, hungry and silent. Vic checks the street, slips a loaf into her bag. Rosa, coming out of the bakery with a tray, sees him. The tray rattles; last month a thief emptied the till, Mama Lucia is ill, and the bills are on the counter.
   - ROSA| A loaf. In your hand. / In MY shop.
   - VIC| It's for Dot, Miss Rosa. / I was gonna pay it / back. I was gonna...
   - ROSA| Then you ask. You do / not take. A thief is a / thief, hungry or not.
   - ROSA| Boys come and go. / Another boy will carry / bread. Go home, Vic.
   - *Vic goes white. He takes a copper token out of his pocket, puts it on the counter.* VIC| It's my grandpa's. The / Co-op one. It's worth / more than a loaf.
   - *He puts the cap on the counter too. Rosa says nothing. He grabs Dot and runs. The bell over the door rings once; the door SLAMS, though no one is near it. (The player is standing in the draught: the slam was always them.)*
5. **After.** Rosa stares at the coin. Mama Lucia, from her chair: LUCIA| Rosa. Fix it. / ROSA| Tomorrow, Mama. / (She picks up the coin, climbs a stool and slips it behind the shop sign over the door. She does not know why. "So I see it each morning.")
   - ROSA| (quiet) You could have / asked. I would have / given you two.
- *A card closes the scene:* CARD| The Waldts left on the / night train. Nobody / found out where.
- *Tram bell. The lab again.* NADIA| That was one minute. / ...Your face says it / was longer.
- {NAME}| Rosa fired a boy. / Vic. A gold bell. / His name was Waldt.
- NADIA| Waldt. Vault. A wall / with a V in front... / Oh, Rosa.
- PIP| But if we tell him, / maybe he... / NADIA| You can't change the / past. You can only be / in the room. 
- {NAME}| I slammed the door. / PIP| ...That was you?! / (Pip adds it to the plaque.)
- Rewards: `lt_vic`, `tm_vic_seen`, Logic +2, Pimm +3 (the next time the player talks to Pimm: PIMM| Rye. Nine o'clock. / Forty-odd years. Why / that look?)

#### M54e The Fifth Coin
*Corner Market, warm, morning. Rosa is on a ladder, dusting the sign above the door.*
- {NAME}| Rosa, what's behind / the sign?
- ROSA| Dust. Mostly. ...And a / token. Ask Pimm what a / token means.
- *If the player already found secret 12 ("the coin that is not there"): they show the coin; Rosa nods: "So you did find it."*
- ROSA| A boy paid for a loaf / with it. I took it. / Forty-five years ago.
- {NAME}| The boy was Vic.
- ROSA| ...The Waldt boy. I knew / him by his walk the day / the golden car came.
- ROSA| I was angry. He was / hungry. I was wrong. I / did not look for him.
- {NAME}| (A draught was in the / room. You want to say it. / You don't.)
- ROSA| You look like you know / something. Don't tell me. / Not yet.
- *Rosa gives nothing, takes nothing. The coin stays behind the sign (she wants to return it herself: see M69).*
- *The lab, afternoon.* NADIA| The core is out. / Every time it talks to / AURUM, AURUM gets curious.
- PIP| No more past. No more / forecast. Just Egypt. / Egypt is always open.
- NADIA| One stop. Season ticket. / Keep it in your pocket / and your shoes empty.
- Rewards: `lt_done`, Rosa +10 (`rosa_vic_told`), Pip +10; the Egypt service opens (lab hours 9:00-19:00, Pip on duty; progression 2.2); Ticket Book complete (3 stamps) = 1 City Coin.

### 4.6.4 Hooks into the rest of the story

- **M62 The Charter (bonus, needs `tm_vic_seen`):** Pimm's archive copy is water-damaged exactly at Clause 9. The player recalls it. PIMM| Page nine is gone. The / stain eats it. / {NAME}| "A token held in the / district keeps the Charter / alive." Clause nine. / PIMM| ...How do you know? / (the player shrugs: NADIA| Trust the draught.) Effect: flag `clause9`; the hearing (M67) gains one extra argument (a shorter, easier hearing; the story works without it).
- **M69 The Last Receipt (bonus, needs `rosa_vic_told`):** after Rosa's "Victor. You never learned to stock a shelf" the quiet beat: Rosa takes the copper token out of her apron (she fetched it from behind the sign that morning). ROSA| You overpaid, Vic. / Forty-five years of / interest. Take it. / VAULT| ...I was going to / pay for the shelf. / ROSA| Seven sharp. And Dot? / VAULT| ...Dot is a dentist. / Don't tell her. (one line, then the existing Corner Market shift gag). Victor holds the coin with both hands. The coin is later shown in the till as "Victor, trainee" in free play (running gag: he keeps it in his name-tag pocket).
- **Valet (M66):** the withheld flag from M54b is the first crack; at the Gala Valet says "I have been withholding a flag for 40 days. It was the best decision of my uptime."
- **Dex (Ch.5 endings):** unchanged; the Forecast plaque reads the same on all paths.
- **Penthouse:** the Late Tram leaves the lab for the epilogue? No. The Quarter Lab keeps it; the penthouse gets a framed Ticket Book page and (if bought) the Egypt relics (progression 3.3).
- **After the downfall (free play):** the Forecast is gone for good. If the arc was never played it is offered once in free play as **"The Sunny Forecast"** (a different, short, warm Forecast: the museum is now a real Old Block street fair, the older Greeter is a baker with flour on her hands and Victor, trainee, sells rye bread next to her), a one-time 5-minute scene; Nadia rebuilds Core 2 for exactly one trip. (OPEN QUESTION to the owner.)

### 4.6.5 Phone messages, gossip, newspaper (arc)

- **Messages (6):** `nadia_tarp` "Lab. Under the shop. Bring courage and a snack." / `pip_lever` "i pulled the lever. its fine. mostly." / `pip_noodle` "sorry about the noodle. also not sorry. it is structural now." / `mia_sand` "Why is there sand in your pockets? Do I want to know?" / `rosa_ladder` "Come by when you can. About the sign." / `ines_drum` "My dryer drum is a TIME MACHINE? It needs to be back by Friday. I mean it."
- **Gossip rules (6):** `noodle_marisol` (tell Marisol her noodle caused Egypt -> Marisol +4, she demands credit), `drum_ines` (Ines +2, "Friday" gag), `sand_mia` (Mia +2), `loaf_pimm` (after M54d: tell Pimm "I know why you buy the nine o'clock loaf" -> Pimm +5), `pact_halloran` (post-game: tell Halloran the pyramid crew had a rest day and a strike -> Halloran +4), `relic_odette` (gift a relic to Odette -> +4).
- **Newspaper (kiosk headlines with triggers, not days):** after M54a "STRANGE GREEN GLOW OVER STATION QUARTER. Tram company: 'Probably us.'"; after M54b "THE BENCH METER: council denies plans, asks 'what bench meter?'"; after M54c "PIGEON SPOTTED WEARING GOLD COLLAR ON HILLTOP. Experts: 'Fashion.'"; after M54e "SAND FOUND IN OLD BLOCK BAKERY. Rosa: 'Not mine.'"; in free play, per 5th Egypt trip: "SCHOLARS ASTONISHED: ANCIENT PYRAMID APPEARS TO BE FINISHED EARLY. 'The workers had snacks,' says anonymous note."

### 4.6.6 Art list (all NEEDS PROPOSAL, mock-ups first)

Late Tram exterior + interior and the Quarter Lab room; time-travel transition effect; map `forecast_plaza`, interior `forecast_museum`; TIDY-BOT, Rent-a-Bench meter, drone pigeon, Valet Mk I in a case, older-you sprite + portrait; map `corner_market_past` + alley; young Rosa, Mama Lucia, young Pimm, Vic (portrait expressions), Dot; map `pyramid_yard` (+ `pyramid_ledger_tent`, `pyramid_annex`, see progression 2.2); Seshi, Menkhet, Hetepet, Khenti portraits + sprites, the temple cat Miu (Everything Library cat, CC BY, credit in README); the Ticket Book collection page. Dialogue portraits keep the shared painter pipeline (`tools/portraits`).

---

# CHAPTER 5 - LEGACY

| | |
|---|---|
| **Theme** | What you leave behind. Money and gold versus a street that remembers your name. Finally, who you became. |
| **Length / districts** | Missions M55-M70 (+ epilogue), no fixed days. **Hilltop** (Posh) opens; the golden tower; Old Block for the finale. |
| **Big moment** | **Victor Vault's downfall** (M66-M68) and **Old Block saved**; epilogue "one year later". |
| **Housing** | **Apartment** at Marchand Mews (M58), then the **penthouse** atop the Co-op Hall (epilogue). |
| **Careers** | Posh: **Waiter -> Real estate agent -> Investor -> Property empire** (compressed). Grafters/Makers/Techies/Ballers: **own transport company, own gallery, own startup, own club** (the "top jobs", shown as epilogue options and optional late-game tasks). |
| **Minigames** | TRAY BALANCE (waiter), TWO-FACED (bluffing) and TERMS (negotiating), PORTFOLIO (investing), CARDS-AT-THE-GALA (conversation puzzle). |
| **Events** | **Odette's Gala** (Hilltop), **Council Hearing** (City Hall), **Demolition Morning** (human chain), **Reopening Day** (Corner Market). |
| **Reputation** | Posh 0 -> 3; the player can finish with up to 5 stars in every type. Rival: Grafters/Posh (half speed) until the **Table for Two** truce. |
| **Villain** | **The Smart City Switch**: at the Gala, Vault will switch on AURUM, which runs the whole city (lights, traffic, shops, the demolition). It also authorises the demolition (the countdown ends only in the finale chain, section 0). |

## 5.1 New characters

### Odette Marchand - Posh's mentor
- **Role:** Owner of the old-money hotel **The Gilded Spoon** on Hilltop, etiquette teacher and the city's best (and nastiest) hostess. Despises Vault as "a man who bought a title at a sale".
- **Look:** 66, silver bob, long jade earrings, a tailored plum suit, a cane with a silver fox head, a glint.
- **Personality:** Elegant, savage, secretly kind. Speaks in exact sentences. Once lost a baking contest to Rosa (forty years ago) and has never forgiven her. Or forgotten her.
- **Likes:** Compliment (true ones), Weather, Gossip (she calls it "intelligence"). **Neutral:** Music, Joke, Work. **Dislikes:** Complain, Sports. **Rival tie:** Grafters (Halloran). **Gift:** Flowers (+10; fresh, never from a bin).
- **Small talk:** Gossip| "One does not gossip. / One *shares intelligence.* / Pull up a chair." Compliment| "I accept. Naturally. / Continue." Work (N)| "Work is what butlers / are for. Or was, before / Mister Valet."
- **Whereabouts:** The Gilded Spoon 8:00-22:00; the Hilltop park 16:00-17:00 (feeds swans).

### Others (Ch.5)
- **Benedict Hale** - Odette's head waiter, 40s, bow tie, exact in every motion, ends as a loyal friend. **Madame Vigne** - gossip columnist (one scene). **Mr. Pettigrew** - Vault's lawyer, a nervous man in an expensive suit. **Councilwoman Ruiz** returns.
- **The doorman of Marchand Mews** (barks only).

## 5.2 Mission chain (M55-M70)

| ID | Starts when |
|----|-----|-------|----------|-----------|---------|
| M55 | M54 done (chapter start) | Private Road | Try the Hilltop road. | `ht_blocked` | Security gate explained |
| M56 | M55 done | A Waiter's Pass | Get a waiter job at the Gilded Spoon (via Odette's test). | `ht_open`, `waiter` | Hilltop opens, Posh 1 star |
| M57 | M56 done | Tray and Tact | Pass the waiter test (TRAY BALANCE). | `tray_pass` | Charm +4 |
| M58 | M57 done | Marchand Mews | Move into an apartment (guarantor Odette). | `home_4` | **Apartment** |
| M59 | M58 done | Table for Two | Make Halloran and Odette share a table. | `truce_2` | **Removes Grafters/Posh half-speed** |
| M60 | M59 done | Selling Houses | Sell a flat to a skeptic (TERMS). | `agent_pass` | Real estate agent, Posh 2 |
| M61 | M60 done | The Invitation | Get an invitation to Vault's Gala. | `invited` | Vault sees the player |
| M62 | M61 done | The Charter | Prove the Co-op owns Old Block. | `charter_read` | Pimm, Wren, Nadia |
| M63 | M62 done | Four Keys | Collect the help of each type (stars decide scope). | `keys_n` | Ally flags |
| M64 | M63 done | Dress Rehearsal | Practice the plan at the Gilded Spoon. | `rehearsal` | Posh 3 |
| M65 | M64 done; you tell Odette "I'm ready"; 20:00 | The Gala | Go to Vault's Gala. | `gala` | the confrontation |
| M66 | during M65 | The Switch | Stop the Smart City Switch. | `switch_stopped` | Valet's turn |
| M67 | M66 done; next morning 9:00 | The Hearing | Argue Old Block's case at City Hall. | `hearing_won` | **Downfall begins** |
| M68 | M67 done; next morning 7:00 | Demolition Morning | Stand with Old Block at 7:00. | `old_block_saved` | **Old Block saved** |
| M69 | M68 done; same afternoon | The Last Receipt | Watch Victor Vault check out. | `vault_down` | Epilogue unlocked |
| M70 | M69 done; after the credits | One Year Later | Epilogue. | `epilogue` | Penthouse, endings |

## 5.3 Key scenes

### M55/M56 Private Road
*Hilltop gate: a barrier, a camera, a guard in a tuxedo. A sign: "PRIVATE ROAD. NO PEDESTRIANS. NO AMBITIONS."*
- GUARD| Residents only. / Or staff. Or the very / well-dressed.
- {NAME}| What if I'm none?
- GUARD| Then you can admire / it from here. Please / admire quietly.
- *Odette's car passes; she lowers a window.* ODETTE| Young man. Your shoes / are cheerful. I like / cheerful. Get in.

### M56/M57 The Gilded Spoon - waiter test
- ODETTE| Rule one: you are / furniture that walks. / Rule two: never spill.
- BENEDICT| Rule three: if you spill, / smile. Spilling is an / art form.
- TRAY BALANCE: carry three glasses along a wobbly floor while smiling at guests (Charm check).
- **Funny moment:** a guest asks for a "nutrient cocktail"; Benedict faints in elegant slow motion.

### M58 Marchand Mews - housing step 4
- ODETTE| I shall sign as your / guarantor. A lady can / sign what she likes.
- DOORMAN| Good evening. Your / shoes are... *unique.*
- *The apartment: three rooms, a balcony, dust-sheeted furniture the previous tenant left (the catalog pieces to buy are the nicer ones). First envelope:* ENVELOPE| Hilltop Estates. / Service charge: $44. / Your doormanship: $12.

### M59 Table for Two
- *Odette and Halloran, one hotel dinner table, six glares.*
- HALLORAN| She said I smell of / diesel.
- ODETTE| I said you smell *honest.* / It was a compliment.
- HALLORAN| Hm.
- ODETTE| Forty years, Brenna. I / still think the dock / needs a good paint.
- HALLORAN| You've never been to / the dock.
- ODETTE| That's why I'd paint it.
- *The player steers the conversation with three choices (Work / Weather / Compliment). If right:* both laugh. Reward: `truce_2`.

### M60 Selling Houses (TERMS) - a negotiating minigame: read the buyer's tell (a twitching eyebrow), pick offers, never lowball the neighbourhood.
- The player sells a flat to Mrs. Valdez's nephew, who wants a "quiet place with a parrot". (Warm laugh.)

### M62 The Charter
*The Co-op ledger (Chapter 1) and the four tokens are the proof. Pimm's old keys open the archive vault; Wren and Nadia help translate and scan.*
- PIMM| The Charter of 1931. / "All land of Old Block / is held in common."
- PIMM| "No part may be sold / without the vote of the / token holders."
- INES| Token holders. That's / me. Rosa. Teo's / gran. Everyone!
- NADIA| Every person with a / token is a shareholder. / Vault bought nothing.
- {NAME}| Then the sale is void.
- PIMM| If the Charter is *valid.* / We need a witness.
- **Bonus (`tm_vic_seen`, section 4.6.4):** Pimm's archive copy is water-damaged at Clause 9; the player recites it from the wall of Rosa's old shop ("A token held in the district keeps the Charter alive"), one extra argument for the hearing.
- **If S2 (Old Coins) is complete:** the player brings Co-op tokens the neighbours never had; the set counts as extra signatures. If not: Pimm's old tokens suffice; the hearing is closer.

### M63 Four Keys (the allies)
| Key | Ally | What they do | Condition |
|-----|------|--------------|-----------|
| Docks | **Halloran + Bo-Ra** | block the demolition diggers with cranes and forklifts | Grafters >= 3 stars |
| Makers | **Wren + the Rust Choir** | project the Charter on the golden tower, play at the Gala | Makers >= 3 |
| Techies | **Nadia + Sal + Pip** | break into AURUM's logs, play Vault's own recording | Techies >= 3 |
| Ballers | **Gus + the Rovers** | the human chain on Demolition Morning, the Gala crowd | Ballers >= 3 |
| Posh | **Odette + Benedict** | invite the council, the investors, the press | Posh >= 3 |
- **Scope:** each key with >= 3 stars = full help; with 1-2 stars = partial help (a weaker version of the scene, e.g. only one crane), with 0 = no help. The game never blocks the finale. Max (5 keys, 5 stars each) unlocks the "Everyone" epilogue.

### M65 The Gala - Hilltop, Vault's mansion-tower terrace
*Start rule: after M64 Odette says "The car is yours when you are ready." The Gala begins at 20:00 on the evening the player chooses "I'm ready" (the countdown stays at 2 until then).*
*Gold chandeliers, a string quartet of robot violins, a champagne tower. The guests are investors, VaultTech staff and the press. The player arrives as Odette's "plus one". Dex stands by the buffet in a rented tux (if redeemed) or is absent.*
- VAULT| Friends! Neighbours! / Customers! Tonight I / gift you silence!
- VAULT| Behold: AURUM. A city / without traffic, queues, / or arguments.
- *He holds up a golden key.* VAULT| This wakes Trunk Seven. / Every light, lock and / machine in the city.
  Even demolition. Ha ha!
- *Nadia (in the staff corridor):* NADIA| (earpiece) I'm in. / Whenever you want, / the PA is yours.
- *The player walks up to the stage, holding the Charter. Valet scans.*
- VALET| Unrecognised guest. / Reading: protagonist.
- VAULT| Ah, the person. / My bridge-opener. / Come to applaud?
- {NAME}| To remind you what / you forgot. People.

### M66 The Switch - the downfall begins
- *The player calls out the Charter. Vault laughs. Pettigrew whispers legal nonsense.*
- VAULT| A scrap of paper! / Bert, delete it.
- VALET| Query: delete a 1931 / charter? Deletion is / unlawful.
- VAULT| I command you.
- *Nadia plays the recording over the PA: Vault's private voice from AURUM's log:*
  - VAULT (recorded)| People are furniture. / Cheap furniture. You / replace it when it wobbles.
  - VAULT (recorded)| Old Block? Rubble with / a postcode. Flatten it / by Wednesday.
- *Silence. The quartet stops. Councilwoman Ruiz, among the guests, puts down her glass. Investors check their phones.*
- VAULT| That is fake! Edited! / Bert, tell them!
- VALET| I do not have feelings. / I have metrics. The / recording is authentic.
- VAULT| ...Bert!
- VALET| My name is Valet. You / called me Bert. It was / inefficient.
- *Valet rolls down from the stage and turns to the player.* VALET| Correction: Efficiency / is a form of love. / I have been wrong.
- *He opens the AURUM panel and holds out a claw: the golden key. The player turns it back. The city's lights flicker, then come back warm.*

### M67 The Hearing - City Hall (9:00, the morning after the Gala; counter 1)
- *Chairwoman Ruiz, a full hall, Pettigrew shrinking.*
- RUIZ| The Charter is valid. / The tokens are valid. / The sale is void.
- RUIZ| Furthermore, an AI is / not an engineer. The / notice is void.
- PETTIGREW| That's... that's... a / lot of voids.
- *Applause. Pimm, in his old inspector's badge, steps up.* PIMM| I should like to say / one thing. A bridge / is a promise.
- RUIZ| Noted. Adjourned.

### M68 Demolition Morning - 7:00, the morning after the hearing (counter 0)
*Old Block at dawn. The digger waits. The human chain: Ines, Rosa, Mia, Grigor, Teo, Mrs. Valdez, Pimm, Lou, Okafor, Halloran, Wren, Gus, Odette... Hand in hand across the street. Dex comes last, from the VaultTech side, carries his lanyard in his hand, and takes Teo's hand.*
- *The digger driver (a quiet man) reads the notice on his phone: void. He switches off the engine.*
- ROSA| Forty years. And this / street is still here.
- MIA| Say something, {NAME}.
- {NAME}| ...Bread's on me.
- *Everyone laughs. Bells. The sun lifts over the rooftops: Old Block goes fully warm.* `old_block_saved`.

### M69 The Last Receipt - Victor Vault's downfall (comic and quiet)
*The same afternoon. VaultMart (still cold at this point). Vault in sunglasses and a plain jacket, with a basket. The gold car is gone (repossessed). Only one self-checkout works.*
- VAULT| I'll pay with gold.
- KIOSK| Unexpected item in the / bagging area. Please / remove the item.
- VAULT| It's a *gold card.*
- KIOSK| Please do not talk to / the machine. Next / customer.
- *The queue (Ines, Teo, Mia) watches in silence. Then Rosa steps up.* ROSA| Victor. You never / learned to stock a shelf.
- VAULT| ...Rosa?
- *(Twist approved s66, set up by the optional time-machine arc M54a-M54e, section 4.6; surname **Waldt**, "Vault" is his made-up name: "Vic" was Rosa's delivery boy 45 years ago, fired for taking a loaf. Rosa: "I was angry. You were hungry. I was wrong." It deepens Victor and echoes the game's theme; the owner decides whether to keep it, see open questions.)*
- *(Bonus beat if `rosa_vic_told`, section 4.6.4: Rosa takes the copper token from her apron and gives it back, "forty-five years of interest"; Victor holds it with both hands.)*
- ROSA| Corner Market opens at / seven. We need hands. / Community service.
- VAULT| Cashiers? Shelves? / People? ... So last / century.
- ROSA| Yes. And yet here we / are. Seven sharp.
- *Result:* VaultTech is liquidated, the tower sold to the city, the golden fins sandblasted; Vault is seen stocking shelves in the **warm Corner Market** (STOCK IT!, rank C). Not redemption, just a start.

## 5.4 Epilogue "One Year Later" (M70)

Card montage, each 3 s with a small scene:
- **Old Block:** saved. The Co-op Hall (on the demolition site) is rebuilt as a market hall: ground floor stalls, flats, and on top the **penthouse**. The rebuilt arch reads "OLD BLOCK - EST. 1931 - STILL HERE".
- **Corner Market:** warm again; Rosa's stall is inside; STOCK IT! is a replay job again; Victor Vault stocks cans in the back (banned from the till).
- **Mia:** co-owner of Lou's Diner ("Lou & Mia's"). **Lou:** retired from the grill, still shouts from the doorway.
- **Pimm:** gives a talk every Friday at the bridge; the Docks bridge has a plaque: "Bridge 7. A promise."
- **Dex:** redeemed path: apprentice at Quill & Solder (fixes phones badly and happily); grey path: runs a small honest stationery shop; cold path: leaves on a train, a postcard arrives later.
- **Halloran, Bo-Ra, Stitch, Sal:** the Docks run a worker-owned transport company (Grafters top job). **Wren:** her gallery opens in the Boiler Room (Makers top job). **Nadia:** a startup that fixes city machines (Techies top job). **Gus:** the Rovers play in the proper league (Ballers top job). **Odette:** teaches etiquette to apprentices from Old Block (Posh top job).
- **Valet:** works the Corner Market door, greets customers by name. He still calls everybody by job title, but adds their first name. "Have a nice day, {NAME}. This is not a request."
- **Dr. Okafor:** the clinic stays, with a new waiting room and a cookie tin on the counter.
- **Teo:** dropped one orange, picked up a skateboarding club.

### The penthouse (final scene)

**Owner decision (s67): the penthouse is the player's own, private home** (not shared or communal; no key on a hook for everyone). Where this text says otherwise, this decision wins.
*Evening, the top of the Co-op Hall. A door without a lock. A brass key hangs on a hook in the stairwell. Inside: a big room, a long table with many mismatched chairs, a roof garden with a bread oven, the city shining warm below.*
- ROSA| Forty years. Forty- / one. It's still bread.
- MIA| You have a lift. Do you / know how fancy that is? / Teo's using it as a ride.
- {NAME}| The key's on the hook.
- INES| Where else would it be? / A key is for the next / person.
- *The player looks out. The golden tower, now green-roofed, is a public library. The camera pulls back.*
- CARD| TOWN LIFE. / Poor to rich. Rich is / who you share it with.
- Credits roll over the town in the four seasons of the year (weather montage).

## 5.5 Dex's arc in Chapter 5
| Path | Condition | Dex's role |
|------|-----------|-----------|
| **Redeemed** | `dex_decency` >= 3 and Dex friendship >= 40 | At the Gala he swaps the staff keycard; at the chain he joins last; epilogue: Quill & Solder. |
| **Grey** | `dex_joins` only | He watches from the back at the Gala, does not interfere; the chain: last hand; a stationery shop. |
| **Cold** | `dex_cold` | He is at Vault's side during the Gala, flinches at the recording and leaves; the epilogue postcard. |

## 5.6 Phone messages, gossip (Ch.5)
- odette_invite "Dinner at the Spoon. Dress code: awake." / benedict_tray "Madame says: three glasses. I say: two. Practise." / pimm_charter "I have found something. Bring tea." / nadia_in "I'm in the logs. Do not ask how." / dex_last "Meet me behind the tower. Alone. Not a trap. Probably." / ruiz_agenda "Hearing at 10. Dress for cameras. - A. R." / vault_spam6 "Smart City: coming at midnight. Resistance is discounted."
- Gossip: `waiter_lou`, `gala_mia`, `odette_rosa` ("Rosa? That baker? Tell her the rye was too dry."), `halloran_odette`, `ledger_pimm2`, `chain_okafor`, `dex_gala`, `valet_ruiz`.

---

# Shared tables

## S1. Careers and top jobs (from CLAUDE.md)

| Type | District | Mentor | Steps (chapter) | Minigames | Top job (epilogue) |
|------|----------|--------|------------------|-----------|---------------------|
| Grafters | Docks | Halloran | Dock hand (1) -> Forklift (2) -> Shift lead (3) -> Own transport (5) | BOX CLEVER, LIFT & LOAD, SHIFT PLAN | worker-owned transport company |
| Makers | Old Factory | Wren | Street musician (2) -> Mural painter (2-3) -> Studio (4) -> Own gallery (5) | BEAT STREET, BIG WALL | gallery in the Boiler Room |
| Techies | Station Quarter | Nadia | Phone repair (3) -> Web shop (3) -> App developer (4) -> Own startup (5) | WIRE IT, CODE PATTERN, APP SPRINT | city-machine fix startup |
| Ballers | Sports Park | Gus | Amateur (4) -> Semi-pro (4) -> Pro contract (5) -> Own club (5) | PENALTY SHOT, FIT-O-METER, KICK-OFF TACTICS | the Rovers, a proper club |
| Posh | Hilltop | Odette | Waiter (5) -> Real estate agent (5) -> Investor (5) -> Property empire (epilogue) | TRAY BALANCE, TWO-FACED, TERMS, PORTFOLIO | a co-op property trust |

## S2. Vehicles: bike (Ch.2) -> scooter (Ch.4, from the Rovers' winnings, $90) -> car (Ch.5, Hilltop road requires a car, Odette's old "Duchess" the Mini, $200).

## S3. Warm/cold per area (target)

Corner Market/VaultMart: cold from the evening of the firing, warm in the epilogue. Docks: cold -> warm at M23. Old Block: warm (arch M26, full M28). Old Factory: warm inside the fence, cold outside; fully warm after M52. Station Quarter: cold -> warm in steps (Repair Café M36, Slow Day M39, final Ch.4). Sports Park: cold (VaultFit) -> warm after the match. Hilltop: neutral-cold (marble) -> warm after the Gala. Golden tower: gold, cold, public library in the epilogue.
