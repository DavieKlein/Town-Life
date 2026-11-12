#ifndef TL_AUDIO_H
#define TL_AUDIO_H

#include "tl_map_id.h"

namespace tl::audio
{
    // Music tracks (modules written by tools/music/build_audio.py into audio/).
    enum class track
    {
        none,
        city,           // City Centre streets
        old_block,      // Old Block streets
        market,         // shops / interiors loop
        stock_it,       // minigame STOCK IT!
        plate_rush      // minigame PLATE RUSH
    };

    enum class sfx
    {
        blip,           // menu cursor
        confirm,
        back,
        coin,           // money in
        cash,           // money out
        door_bell,
        mission,
        // activity sounds (round 3): looping ones are driven by set_loop, the others are one-shots
        water,          // sink / fountain washing (loop)
        shower,         // loop
        munch,          // eating (loop)
        gulp,           // drinking (loop)
        flush,
        page,           // reading (loop)
        rustle,         // bin search (loop)
        clink,          // can / bottle pickup
        whirr,          // deposit machine
        snore,          // sleeping (loop, subtle)
        thud,           // sitting down
        door,
        beep,           // phone
        scratch,        // scratch card
        ladder,
        manhole,
        mg_good,        // minigames
        mg_bad,
        mg_clink,
        none
    };

    // Which track plays where (see docs/music_plan.md "s78 status"), and how loud (0..100).
    [[nodiscard]] track track_for(map_id id);
    [[nodiscard]] int volume_for(map_id id);

    // The field calls this when a warp starts and when a map is loaded: fades to the new map's track
    // (same track = no restart, only a volume change) and rings the shop bell when a shop is entered from the street.
    void set_map(map_id id);

    // Outdoor tracks are quieter at night (called every game minute).
    void set_night(bool night);

    // Explicit control (cutscene ops, minigames). instant = hard cut instead of a fade.
    void set_track(track t, int volume_percent, bool instant);
    void stop(bool instant);

    // Music ducks while a dialogue, menu, pause screen or phone is open.
    void duck(bool on);

    void play(sfx s);

    // The looping activity sound that should be heard right now (sfx::none = silence). The clip is replayed back to back while it is
    // wanted and stops at once when it is not (activity over or cancelled with B).
    void set_loop(sfx s);

    // Called every frame by the field (and not during blocking loops: set_track(..., true) is used there).
    void update();
}

#endif
