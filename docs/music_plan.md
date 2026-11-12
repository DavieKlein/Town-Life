# Town Life - music and sound plan (s71, docs only, nothing built)

**Status s78: phase 1 + 2 built** (see CLAUDE.md "s78: music and sound"): 3 tracks (City Centre, Old Block, market/interior loop) + 7 SFX are generated
by `tools/music/build_audio.py` into `audio/`, played by `tl_audio` (map tracks with fades, ducking, SFX hooks, cutscene ops). Measured (headless mGBA,
`-DTL_DEBUG_CPU`, City Centre): avg CPU idle 23 -> 30 %, walk 30 -> 38 %, run 33 -> 41 % with music at 16 kHz / 8 channels; missed frames over 2400
running frames 10 (no music) vs 13 (16 kHz) vs 18 (13 kHz) vs 13 (10 kHz), i.e. not measurably different, so the rate stays 16 kHz (best quality;
maxmod allows neither mono nor dynamic mixing). Still open: title / minigame / Victor tracks, night variants, volume options, real-device check in Lemuroid.

(Original text below.) Status: PROPOSAL. No audio exists yet (`audio/` and `dmg_audio/` are empty; the Makefile already has `AUDIOBACKEND := maxmod`,
`DMGAUDIOBACKEND := default`). All music is **fully original**: we describe the *approach* of earlier life-sims, never reuse a melody,
chord hook, sample or sound from them.

## 1. Reference analysis (approach only)

What the GBA/DS life-sims (The Urbz GBA/DS, The Sims Bustin' Out GBA, The Sims 2 GBA/DS) do, from general knowledge:

- **One loop per location.** Each lot/district/interior has its own looping track; entering a building cuts to a different track. The
  street theme is the "identity" of a district, interiors are quieter, simpler variants of the same style.
- **Style.** Funky / jazzy / lounge (electric piano, slap-style bass, wah guitar stabs, brass hits, bongos and shakers) for the Sims
  titles; Urbz leans to hip-hop / urban (boom-bap drums, scratch-like stabs, sub bass, sparse melodic hook). Moods are upbeat, a little
  tongue-in-cheek, never epic.
- **Loops.** Typically 16-32 bars at 90-120 BPM = about 30-60 s, looping seamlessly; made to be heard for many minutes, so low melodic
  density and a short, hum-able hook.
- **GBA hardware.** Sample-based tracker-style playback (4-8 software channels mixed at 13-21 kHz): short looped instrument samples
  (8-bit, often 4-8 kB each), 1-2 percussion samples, simple bass. Sounds thin and crunchy on purpose; arrangements are 4-6 voices.
  DS versions use the same ideas with cleaner samples and more channels.
- **Conversation / minigames / menus.** Conversations mostly keep the location music (maybe lowered) with short voice-like "blips" per
  character; minigames get their own faster, busier loop plus win/lose stingers; menus are a quiet loop or silence; important events
  (mission done, level up) get a 1-3 s jingle that interrupts the music.
- **Ambient and day/night.** Little real ambience on GBA (SFX channels are scarce): footstep-free movement, UI blips, door sounds, a few
  environmental loops (water, traffic). Day/night is mostly a visual palette change; music sometimes has a calmer night variant.

Takeaways for us: one loop per place, shared style per district, tiny interior variants, short stingers, few channels, no ambience bed.

## 2. Our musical identity

- **Warm city:** acoustic-feeling small band - Rhodes-style electric piano, upright/finger bass, brushed kit, nylon guitar, marimba/
  vibraphone, a little accordion in Old Block. Major/mixolydian, swing-light, friendly, 80-105 BPM.
- **Cold city (VaultTech/VaultMart):** the same motif played by synth-pad, FM bell, square-wave arps, drum-machine hats, quantised
  (no swing), minor or whole-tone colouring, 120 BPM metronome feel. Victor's theme: pompous brass-synth fanfare in a major key that
  is slightly "wrong" (b6 / tritone), a booming gated snare.
- **One shared 4-bar motif ("the Town motif")** appears in every warm track, in a distorted/robotic form in cold tracks, and resolves
  warmly in the finale. This is how the warm/cold idea is carried musically (see 2.4).

### 2.1 Track list, district 1 (priority: P1 needed for a releasable audio build, P2 soon after, P3 polish)

| Track | Mood | BPM / key | Key instruments | Loop | Pri |
|---|---|---|---|---|---|
| Title screen | hopeful underdog, a little melancholy, motif stated | 84, C major | e-piano, nylon guitar, soft kit, vibraphone | 24 bars ~65 s | P1 |
| Name entry | light, playful, calm | 96, G major | marimba, pizzicato bass | 8 bars ~20 s | P3 (reuse title) |
| City Centre, day | busy, friendly, relaxed funk-jazz | 100, F mixolydian | e-piano comp, finger bass, brush kit, wah-ish guitar stabs, shaker | 32 bars ~77 s | P1 |
| City Centre, night | same chords, half-time, sparse, lamp-lit | 72, F mixolydian | vibraphone, soft pad, upright bass, brushes | 16 bars ~53 s | P1 |
| City Centre, dusk/dawn | none: cross-fade by clock (see 4.4) | | | | |
| Park bench night (sleeping) | very quiet lullaby, crickets via SFX | 60, A minor/major | music box, soft pad | 8 bars ~32 s | P2 |
| Old Block (street) | poorer but proud: accordion, brass-band wink, washing-line cosy | 92, D mixolydian | accordion, tuba-ish bass, snare rolls, mandolin | 32 bars ~83 s | P2 (district not built) |
| Corner Market (warm, Day 1) | cheerful shop radio | 108, C major | e-piano, bass, light drums, whistle lead | 16 bars ~35 s | P1 |
| VaultMart (cold) | sterile, fluorescent, shop-muzak with robotic skew | 120, C whole-tone/minor | FM bell, square arp, 808 hats, robot "next customer" voice SFX | 16 bars ~32 s | P1 |
| Diner | jukebox swing, greasy and cosy | 112, Bb major | e-piano, walking bass, brushes, clarinet-ish lead | 16 bars ~34 s | P1 |
| Library / community centre | calm, thoughtful, almost no drums | 76, Eb major | glockenspiel, soft strings, clarinet | 16 bars ~51 s | P2 |
| VaultTech lobby | marble and gold, cold luxury, Victor's world | 90, D minor | brass-synth pad, harp-like pluck, slow kick | 12 bars ~32 s | P2 |
| Public toilet | echoey, comedic, near-silence: dripping drone, one bassoon-ish note motif | 70 | muted pad + SFX drips | 8 bars | P3 (can be silence + SFX) |
| Clinic | clean, reassuring | 80, E major | soft e-piano, flute pad | 12 bars ~36 s | P2 |
| Player room | private, warm, lo-fi | 78, Ab major | e-piano, tape-wobble guitar, soft kick, radio static SFX | 16 bars ~49 s | P1 |
| Conversation | light: no extra track; location music ducks to ~50 %. Mood cues (stingers 1-2 s): happy, angry, sad, surprised | | glock/pluck | | P2 |
| Victor's theme | pompous, boastful, slightly wrong | 104, Eb major w/ tritone | brass-synth, gated snare, timpani | 16 bars ~37 s | P1 (firing) |
| Cutscene: the firing | warm shop track stops, silence, Victor's theme enters, then sad solo piano on Mia's goodbye | | | cue-based | P1 |
| Cutscene: car arrival | engine SFX + 4-bar brass fanfare | | | stinger 8 s | P1 |
| Evening after firing ("Four hours later") | lonely, motif on solo e-piano | 66, A minor | e-piano, pad | 16 bars | P2 |
| Minigame STOCK IT! | fast, cheerful, conveyor-belt groove, tempo rises with combo | 128, G major | bouncy bass, marimba, snare, claps | 16 bars ~30 s | P1 |
| Minigame PLATE RUSH | frantic kitchen swing, clattery percussion | 140, D major | upright bass, brushes, woodblock, muted trumpet | 16 bars ~27 s | P1 |
| Minigame result: win S/A, B/C, lose | jingles 2-4 s | | | | P1 |
| Mission complete jingle | 4 notes up on the motif, 2 s | | glock + chord | | P1 |
| Pause menu | no track; music low-pass / volume 40 % | | | | P1 |
| Phone, Mission log, collection | same ducking as pause | | | | P2 |

Budget: about 10-12 loops in district 1 (title, centre day/night, market, vaultmart, diner, room, 2 minigames, Victor, 1-2 more) plus
~8 stingers.

### 2.2 Later districts (one loop each, outdoor; interiors reuse variants)

| District | Idea | BPM |
|---|---|---|
| Docks (Grafters) | work-chant groove, steel-drum + tuba, crane clanks as percussion | 96 |
| Old Factory (Makers) | rhythm-lab: found-sound percussion, pentatonic marimba, busker guitar | 104 |
| Station Quarter (Techies) | chiptune-ish synthwave, square arps, tram bell SFX | 124 |
| Sports Park (Ballers) | upbeat brass-band/pep funk, snare marching | 116 |
| Hilltop (Posh) | harpsichord/string-pad "polite" chamber jazz, cold-ish but elegant | 88 |
| Egypt (time machine arc) | modal (Phrygian dominant), frame drum, reed flute, sistrum shaker; warm and sunny | 90 |
| Finale / Gala / Demolition morning | motif in full orchestration, cold -> warm resolution | varies |

### 2.3 Day/night

Outdoor City Centre and Old Block have a day and a night track sharing key and chords (so a cross-fade at ~19:40 / ~6:15, the same
times the UI switches style, sounds natural). Interiors have one track each (no night variant).

### 2.4 Warm/cold in music

Each location has a `warmth` (the planned per-area state). Music data per place: `warm_track`, optional `cold_track`. Cold variants are
**the same song re-instrumented** (same patterns, different instruments/samples and no swing), so it costs only sample sets plus one
more pattern order (in a tracker: copy module, swap instruments). VaultMart/VaultTech lobby only exist in cold form; Corner Market
before the firing is warm, VaultMart is the cold remix of it (same chords, robotic). Winning missions in an area swaps cold to warm via
a cross-fade; the first warm return of the motif is a story beat.

## 3. Sound effects

Prefer **DMG (Game Boy sound chip) SFX** for short UI sounds (free, zero mixing cost) and maxmod samples for anything that needs realism.

| Group | Sounds | Engine |
|---|---|---|
| UI | cursor move, confirm, back, error, menu open/close, dialogue text blip (per speaker pitch), page turn, choice | DMG |
| Story | mission complete (jingle), new message ping, phone ring, friendship up/down tick, City Coin | maxmod (short) |
| Money | coin, cash register "cha-ching", kiosk beep, scratch-card scrape, denied buzz | DMG / maxmod |
| Movement | footsteps by surface: asphalt/stone, grass, wood floor, tile, metal (VaultMart); 2 variants each, tied to the walk-frame advance; quieter than music | maxmod 8-bit, 1-2 kB each (or DMG noise tick) |
| Doors | shop bell, wooden door, glass double door (VaultTech), automatic door hiss, stairs | maxmod |
| Needs | eat crunch/munch, drink gulp, wash splash, shower, toilet flush, accident, bladder-warning, sick cough, snore (sleep), faint | maxmod / DMG |
| Objects | bench sit, seat creak, bed, bin rummage, fridge, sink tap, fountain loop, deposit machine (can drop, whirr, coin payout, full beep), can pickup, collectible sparkle | maxmod |
| City ambience (optional, P3) | pigeon coo/flap, distant traffic, water, crickets at night; one looping ambient on the spare channel only outdoors | maxmod loop |
| VaultMart | robot voice phrases ("Have a nice day. Next customer.") - 3-4 short 4-bit phrases or DMG-synth chirps; restock arm servo, kiosk boop | maxmod |
| Minigames | item thrown/placed, wrong shelf buzz, combo up, plate scrub/rinse/stack, plate break, timer low, rank reveal | DMG + maxmod |

## 4. Technical plan (Butano 21.9.0 / maxmod)

- **Assets.** Music: `audio/*.mod|.xm|.s3m|.it` (+ `.json` for volume if needed), built by Butano's `mmutil` into a soundbank; accessed as
  `bn::music_items::<name>.play(volume)`. Sound effects as `.wav` (8-bit mono, 11-16 kHz) in `audio/` become `bn::sound_items::<name>`.
  Butano's DMG backend ("default"): `dmg_audio/*.vgm|.s3m` etc. -> `bn::dmg_music_items`, plus `bn::dmg_sound`-style SFX are not available
  from sound effects; use `bn::dmg_music` for Game Boy chip tunes (one at a time) - decide in the proof of concept whether UI blips are
  better as short maxmod samples (simplest, one pipeline). **Default decision: all audio through maxmod, DMG unused**, unless CPU needs it.
- **Mixing.** `bn::audio::` sets the mixing rate via the `.json`/Makefile (maxmod default 10.5 kHz, 16 channels). Proposal: **13.1 kHz,
  8-10 channels** (music 5-6 + SFX 3-4). Mixing costs CPU every frame: current idle ~70 % (CLAUDE.md), typing pages costs missed frames,
  so measure with `-DTL_DEBUG_CPU` after the proof of concept; fall back to 10.5 kHz / 6 channels if `m` (missed) grows.
- **ROM/RAM.** GBA ROM 32 MB; our maps already use ~1-2 MB, so audio of 1-3 MB total is fine. Maxmod keeps the module + samples in ROM
  and streams the mixing buffer in IWRAM/EWRAM; RAM cost is small (about 4-8 KB mixing + a few KB channel state). The soundbank is all in
  ROM. Aim: <= 150 kB per loop (8-bit samples, <= 8 kB each, trim loops), total <= 2.5 MB. Ladder: tracker patterns are tiny, samples are
  what costs; reuse the same sample set across tracks of a district.
- **Switching music (location manager).** A `tl_audio` module with `set_scene_music(map, time, warmth)` that maps (map_id, day/night,
  warm/cold) to a track id (a small generated table beside `map_info`, e.g. field `map_info::music`). Rules: same track on the new map =
  keep playing (no restart); different = fade out 20-30 frames in step with the screen fade (warps already fade out/in), start new
  track at fade-in; `bn::music::set_volume` per frame for fades. Day/night: re-evaluate once per game minute, cross-fade at the boundary
  (maxmod plays one module at a time, so a "cross-fade" = quick fade-out of A then fade-in of B over ~60 frames; same key keeps it
  musical; position carries over if both modules are structured identically: `bn::music::set_position` / `position`).
- **Ducking in dialogue.** Dialogue/menu open: tween music volume to ~40-50 % over 10 frames, back on close; pause menu 40 % (optionally
  nothing else). Text blips use a spare SFX channel at fixed volume.
- **Jingles.** `bn::sound_items::<jingle>` on an SFX channel while music ducks 100 -> 30 % for 2 s; for cutscene stingers (firing) stop
  the loop (`bn::music::stop()`), play the one-shot module, and resume on cue (cutscene script ops: `music <track>`, `music_stop`,
  `music_duck`, `sfx <id>`; to be added to `tools/cutscenes_src.txt` format).
- **Minigames.** `run_minigame` already destroys the field; start the minigame track at its start and resume the location track when
  the field is rebuilt. STOCK IT! may raise the tempo with the combo via `bn::music::set_tempo` (maxmod speed/tempo) if the module is
  written to allow it.
- **Save/settings.** Add music/sfx volume to the pause menu later (needs save version bump; keep the old save unchanged until then).
- **Emulation check.** Headless mGBA (libretro) already runs the same core: `tools/headless_run.py` can record audio? Likely not;
  proof of concept should dump the module through `ffmpeg`/`openmpt123` offline for listening, and the owner tests in Lemuroid.

## 5. Production workflow (no local installs for the owner)

The owner cannot install software; **all music is produced in the Claude container** and committed as files.

1. **Format: write tracker modules programmatically.** A Python tool `tools/make_music.py` (numpy only) takes a compact song description
   (patterns as text, instruments = our own synthesized samples) and writes a valid **.xm or .it/.s3m** file. S3M is the simplest
   format to write by hand (PCM samples, 64-row patterns); IT/XM give more channels/effects. Samples are **synthesized by script**
   (additive/FM/subtractive synth, noise drums) - so they are original and copyright-free by construction (our own work).
2. **Preview/listen:** the container cannot play audio, but we can render WAV/MP3 offline (`ffmpeg` is installed; `openmpt123` or
   `libopenmpt` via apt; or our own numpy renderer) and check the waveform, loop point, levels, clipping and spectrum; the owner listens
   via the phone by downloading the MP3 previews as release assets or by testing the ROM. (A web preview artifact with Web Audio
   rendering the pattern data is possible for approvals: "propose before build" rule.)
3. **Optional free sample sources:** CC0 only: Freesound CC0 filter, Kenney.nl audio packs, OpenGameArt CC0, sonniss free packs
   (check licence), Quaternius has none. Rules: **only CC0 or CC BY with credit in README**; nothing ripped, nothing from the reference
   games, no "free" packs of unclear origin, no AI-music generators with unclear licence unless the terms are checked. Log each sample's
   source + licence in `art_source/audio/SOURCES.md`.
4. **Commissioning (optional, <= ~EUR 50 budget):** a composer from itch.io/Fiverr could write 2-3 key tracks (title, City Centre, Victor)
   as tracker modules; licence must allow a public repo/game and credits. Our programmatic pipeline remains the default.
5. **Approval flow (owner's rule):** audio is "not visual" but still follows propose-first: make 30-60 s MP3 previews of each new
   track, collect them, get approval, then one build and release.

### Proof of concept (later, one session)

- Deliverable: **"City Centre, day" 32-bar loop (~75 s)**, made with `tools/make_music.py` as `audio/city_day.xm` (or `.s3m`), plus 5
  SFX (menu blip, confirm, coin, door bell, footstep) as `.wav`.
- Steps: (1) tool + synthesized samples; (2) render preview MP3 and check the loop; (3) add `tl_audio` with `play`/`fade`/`duck` and a
  title -> field switch, build in Docker, check CPU with `-DTL_DEBUG_CPU`; (4) owner test in Lemuroid (volume, loop click, battery);
  (5) decide mixing rate and channel count from the measurements, then scale to P1 tracks.
- Risks: Butano's mmutil must accept the module (known to work with .xm/.it/.s3m/.mod); CPU at 13 kHz; loop clicks from badly trimmed
  samples; Lemuroid audio latency (SFX timing); EWRAM use if samples are copied (maxmod reads from ROM).
