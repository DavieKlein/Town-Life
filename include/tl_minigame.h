#ifndef TL_MINIGAME_H
#define TL_MINIGAME_H

#include <stdint.h>

namespace tl
{
    // The two job minigames. Each one is its own scene: it owns the whole screen (a full-screen background and its own sprites)
    // and runs a blocking loop (bn::core::update() inside), like the title screen. The field is destroyed before a minigame
    // starts and rebuilt from a snapshot afterwards (see main.cpp), so a minigame only hands back a result struct.
    //   STOCK IT!  (Corner Market, Rosa): put groceries on the right shelf, 45 s, combo, rank C/B/A/S.
    //   PLATE RUSH (Lou's Diner): scrub / rinse / stack the plates, 8 rushes, wage + tip, 3 broken plates end the shift.
    enum class minigame_kind : uint8_t
    {
        stock_it,
        plate_rush
    };

    struct minigame_request
    {
        minigame_kind kind = minigame_kind::stock_it;
        int day = 1;
        int start_minutes = 7 * 60;     // time of day when the minigame starts (UI style, clock shown by PLATE RUSH)
        bool replay = false;            // STOCK IT! as a replayable job (3 rounds; the 4th section "fruit" is not built yet)
        int tempo_percent = 100;        // PLATE RUSH: dinner shift = 130
        int pan_percent = 12;           // PLATE RUSH: chance that a plate is a greasy pan (from rush 3 on)
        int special = 0;                // PLATE RUSH: daily special index (plate_special_for_day), shown on the start card
        int extra_plates = 0;           // special: +n plates in every rush
        int tip_bonus = 0;              // special: +$n on the tip before breakage is subtracted
        int vip_bonus = 0;              // special: +$n when no plate breaks (a VIP guest eats today)
        int bot = 0;                    // debug: 0 = human, 1 = perfect, 2 = sloppy, 3 = terrible (headless tests only)
    };

    struct minigame_result
    {
        bool completed = false;
        bool early_end = false;         // PLATE RUSH: three broken plates
        int rank = 0;                   // STOCK IT!: 0 C, 1 B, 2 A, 3 S
        int score = 0;
        int count = 0;                  // items stocked / plates washed
        int mistakes = 0;               // wrong shelves / missed steps
        int best_combo = 0;
        int perfect = 0;                // PLATE RUSH: PERFECT steps
        int broken = 0;
        int wage = 0;                   // money earned now (PLATE RUSH wage + tip; STOCK IT! pays later, at the firing)
        int tip = 0;
        int pay_preview = 0;            // STOCK IT!: the money Rosa hands over later (18 / 19 / 20 / 22)
        int minutes = 0;                // game minutes the shift took
    };

    // PLATE RUSH daily specials (s71, against repetition): one per weekday (day 1 = Monday). Fills the tempo / pan / plates / tip fields
    // of the request (tempo_percent and pan_percent are changed relative to what the caller already set).
    void apply_plate_special(minigame_request& request, int day);
    [[nodiscard]] const char* plate_special_name(int special);

    // STOCK IT! pay by rank (the prologue's last pay).
    [[nodiscard]] int stock_pay_for_rank(int rank);

    minigame_result run_stock_it(const minigame_request& request);
    minigame_result run_plate_rush(const minigame_request& request);
    minigame_result run_minigame(const minigame_request& request);
}

#endif
