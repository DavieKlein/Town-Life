#ifndef TL_CUTSCENE_H
#define TL_CUTSCENE_H

#include <stdint.h>

#include "tl_map_id.h"
#include "tl_cast_data.h"

// Cutscene scripts: data (tools/cutscenes_src.txt compiled by tools/cutscene_data.py into src/tl_cutscene_data.cpp) and the
// structures the script runner in src/tl_field_script.cpp reads. See the format description at the top of cutscene_data.py.
namespace tl
{
    enum class cs_op : uint8_t
    {
        fade_out, fade_in, black, flash, wait, card, warp, player_at, player_face, face_to, walk, scene_begin, scene_end, spawn,
        despawn, swap, move, actor_face, actor_face_player, wait_moves, say, info, flag, mission, done, money, money_rank, objective,
        objective_clear, minigame, letterbox, pan, pan_player, time, next_day, needs, eat, lie_bed, get_up, hook, vaultmart_swap,
        jump, ifflag, end, car_spawn, car_move, car_remove, clinic_care
    };

    struct cs_step
    {
        cs_op op;
        int a;
        int b;
        int c;
        int d;
        int e;
        const char* text;
    };

    struct cs_script
    {
        int first;
        int count;
    };

    enum class cs_cond_kind : uint8_t
    {
        map,            // a = map
        flag,           // a = flag set
        noflag,         // a = flag clear
        flag_ge,        // a = flag, b = minimum value
        day_eq,         // a = day
        day_ge,         // a = day
        time_ge,        // a = minute of the day
        time_lt,
        mission         // a = current mission id
    };

    struct cs_cond
    {
        cs_cond_kind kind;
        int a;
        int b;
    };

    struct cs_trigger
    {
        int script;
        int first_cond;
        int cond_count;
    };

    const cs_step* cutscene_steps();
    const cs_script* cutscene_scripts();
    const cs_cond* cutscene_conds();
    const cs_trigger* cutscene_triggers();
    int cutscene_triggers_count();
}

#endif
