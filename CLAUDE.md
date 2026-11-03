# Town Life — projectgids voor Claude

Game Boy Advance-game in C++ met de [Butano](https://github.com/GValiente/butano)-engine.
Top-down stadsgame met Sims-achtige elementen (behoeftes, baantjes, reputatie, spullen kopen).
Geïnspireerd op het *genre* van The Urbz (GBA), maar met **uitsluitend eigen personages, namen,
graphics en muziek** — niets overnemen uit The Urbz of andere bestaande games.

## Belangrijk voor elke sessie

- De eigenaar kan **niets lokaal installeren** en test op een Samsung-telefoon in **Lemuroid**.
  De ROM wordt dus altijd gebouwd door GitHub Actions; elke push naar `main` publiceert een nieuwe
  release `latest` met `town-life.gba`:
  https://github.com/DavieKlein/Town-Life/releases/tag/latest
- Na elke push: controleer of de workflow "Build ROM" groen is en los fouten op tot hij slaagt.
- In de Claude-cloudcontainer kun je vaak lokaal testen met Docker (start eerst `dockerd &`):
  `docker run --rm -v "$PWD":/src -w /src devkitpro/devkitarm make -j8`
  (Docker Hub geeft soms 429 rate limits; dan opnieuw proberen of op CI vertrouwen.)
  Ruim daarna `build/`, `*.gba` en `*.elf` op (staan ook in `.gitignore`).
- Taal van de game-teksten: nog niet vastgelegd (vraag de eigenaar; Nederlands ligt voor de hand).

## Spelconcept

De speler is nieuw in een klein stadje ("Town Life"). Je loopt vrij rond door straten, een park en
woonwijken. Je moet je **behoeftes** (honger, energie, hygiëne, plezier) op peil houden, **geld
verdienen** met baantjes (minigames), **reputatie** opbouwen bij verschillende groepen inwoners,
met **NPC's** praten en je **huis inrichten** met spullen uit de winkel. Voortgang wordt opgeslagen
in SRAM.

## Mapstructuur

```
.
├── .github/workflows/build.yml  CI: bouwt ROM in devkitpro/devkitarm, publiceert release "latest"
├── butano/                      git submodule: Butano-engine (vastgezet op tag 21.9.0)
├── Makefile                     Butano-projectmakefile (TARGET=town-life, ROMTITLE=TOWN LIFE)
├── src/                         C++ bronbestanden
│   ├── main.cpp                 init, camera, hoofdloop
│   └── tl_player.cpp            speler: input, beweging, botsing, loopanimatie
├── include/                     headers
│   ├── tl_player.h
│   ├── tl_town_map.h            botsingsfuncties (solid_at / solid_rect) op metatile-niveau
│   └── town_map_data.h          GEGENEREERD: botsingsdata per 16x16 metatile
├── graphics/                    Butano-assets (.bmp + .json); town.* en player.* zijn GEGENEREERD
├── audio/  dmg_audio/           (leeg) voor muziek/geluid later
└── tools/gen_graphics.py        genereert placeholder-graphics + town_map_data.h (pure Python 3)
```

Code-conventies: namespace `tl`, bestanden met prefix `tl_`, Butano-stijl (snake_case, `_member`).

## Hoe de build werkt

1. `make` (Butano's `butano.mak`) verwerkt `graphics/*.bmp` + `.json` naar headers zoals
   `bn_regular_bg_items_town.h` en `bn_sprite_items_player.h` in `build/`.
2. Compileert `src/*.cpp` en linkt naar `town-life.gba` (header gefixt met ROM-titel `TOWN LIFE`).
3. GitHub Actions (`build.yml`): job `build` draait in container `devkitpro/devkitarm`, checkt
   de submodule mee uit, bouwt en uploadt een artifact. Job `release` (alleen op `main`) verwijdert
   de oude release/tag `latest` en maakt een nieuwe met `town-life.gba`.
4. Butano bijwerken: `cd butano && git fetch --tags && git checkout <tag>`, dan de submodule
   committen. Let op API-wijzigingen.

### Graphics aanpassen

De placeholder-graphics komen uit `tools/gen_graphics.py`:
- Palet: 16 kleuren (index 0 = transparant), gedeeld door achtergrond en sprite.
- Stad: 32x32 metatiles van 16x16 px = 512x512 px regular background (4bpp).
  Metatile-tekens (`.` gras, `R/h/v` weg, `s` stoep, `T/W/D` huis, `t` boom, `~` water, ...)
  staan in `TILES` met per teken of het "solid" is. De layout wordt opgebouwd in `build_layout()`.
- Speler: `player.bmp` 16x144, 9 frames van 16x16 (0-2 omlaag, 3-5 omhoog, 6-8 zijwaarts/rechts;
  links = horizontaal gespiegeld).
- Na wijzigen: `python3 tools/gen_graphics.py` en de gegenereerde bestanden committen
  (CI draait het script niet).
- BMP-eisen van Butano: geïndexeerd, ongecomprimeerd; regular bg-afmetingen veelvoud van 256 px.

### Coördinaten

- Spelerpositie staat in **map-pixels** (0..511), midden van de sprite.
- Butano-wereldcoördinaat = map-pixel − 256 (de bg is gecentreerd op 0,0).
- Camera volgt de speler en wordt geclampt zodat de rand van de stad niet voorbij scrollt.
- Botsing: hitbox rond de voeten (10x6 px), per as apart gecontroleerd zodat je langs muren glijdt.

## Besturing (huidig)

- D-pad: lopen · B ingedrukt houden: rennen

## Stappenplan / status

Werk de checkboxes bij aan het eind van elke sessie.

### 0. Basis — AF
- [x] Butano-project (submodule op 21.9.0), Makefile, `.gitignore`
- [x] GitHub Actions: build in devkitarm-container + release `latest` met `town-life.gba`
- [x] Stad als tilemap 512x512 (wegen, stoepen, 8 huizen, park met fontein en vijver)
- [x] Speler met d-pad, loopanimatie in 4 richtingen, botsing, meebewegende camera, rennen met B

### a. Behoeftes + HUD — TODO
- [ ] Struct `needs` met honger, energie, hygiëne, plezier (0–100), dalen over tijd (frame-teller)
- [ ] HUD: 4 kleine balkjes/iconen (sprites of een tweede bg-laag met hoge prioriteit)
- [ ] Spelklok (dag/tijd) tonen; START opent een pauzemenu met de exacte waardes
- [ ] Interactie met objecten (A-knop voor je): bijv. bankje = energie, fontein = hygiëne-lite
- [ ] Tip: gebruik `bn::sprite_text_generator` met een eigen font (zie butano/common) voor tekst

### b. NPC's met dialogen — TODO
- [ ] NPC-klasse (sprite, positie, eenvoudig rondlooppatroon, botsing met speler)
- [ ] Dialoogvenster onderin (bg-laag of sprites) met tekst, A = volgende
- [ ] Een paar eigen personages met naam en persoonlijkheid

### c. Baantje met minigame — TODO
- [ ] Geld-variabele + tonen in HUD
- [ ] Eerste baan (bijv. pizza bezorgen of ijsjes verkopen) als aparte scene met minigame
- [ ] Beloning in geld, kost energie

### d. Reputatie — TODO
- [ ] Meerdere groepen in de stad (eigen bedenksels, bijv. "Skaters", "Buurtcomité", "Kunstenaars")
- [ ] Reputatie per groep, beïnvloed door dialoogkeuzes en baantjes; NPC's reageren erop

### e. Winkel + spullen voor je huis — TODO
- [ ] Huis van de speler betreedbaar (deur = scene-overgang naar interieur)
- [ ] Winkel-scene met lijst items en prijzen
- [ ] Gekochte meubels plaatsen in huis; meubels vullen behoeftes aan (bed, douche, koelkast, tv)

### f. Opslaan en laden — TODO
- [ ] Save-struct met versienummer, `bn::sram::write/read` (zie butano/examples/sram)
- [ ] Titelscherm: Nieuw spel / Doorgaan
- [ ] Lemuroid: SRAM-saves werken met de standaard Butano-SRAM-instelling

### g. Betere graphics en muziek — TODO
- [ ] Echte pixel-art tileset en personages (eigen ontwerp), meerdere paletten
- [ ] Objecten die over de speler heen getekend worden (boomkruinen, daken) via 2e bg-laag
- [ ] Muziek (.mod/.xm/.s3m in `audio/`, maxmod) en geluidseffecten

## Volgende sessie: begin hier

Start met stap **a** (behoeftes + HUD). Splits `main.cpp` op in scenes zodra er een tweede
scene komt (bijv. `tl_scene.h` met een enum en per scene een klasse met `update()`).
