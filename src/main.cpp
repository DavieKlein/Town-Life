/*
 * Town Life - a story-driven isometric life-sim for the Game Boy Advance.
 * Built with Butano (https://github.com/GValiente/butano).
 */

#include "bn_core.h"
#include "bn_optional.h"

#include "tl_field.h"
#include "tl_title.h"
#include "tl_story.h"
#include "tl_name_entry.h"
#include "tl_minigame.h"

#ifdef TL_DEBUG_CPU
#include "bn_core.h"
#include "bn_string.h"
#include "bn_sprite_tiles.h"
#include "tl_ui.h"
#endif

int main()
{
    bn::core::init();

#ifdef TL_DEBUG_MINIGAME
    // Debug build only: starts a minigame straight away (1 = STOCK IT!, 2 = PLATE RUSH) with a bot (TL_DEBUG_BOT) for headless tests.
    {
        tl::minigame_request request;
        request.kind = TL_DEBUG_MINIGAME == 1 ? tl::minigame_kind::stock_it : tl::minigame_kind::plate_rush;
        request.start_minutes = TL_DEBUG_MINIGAME == 1 ? 7 * 60 + 30 : 11 * 60;
#ifdef TL_DEBUG_BOT
        request.bot = TL_DEBUG_BOT;
#endif
        tl::run_minigame(request);

        while(true)
        {
            bn::core::update();
        }
    }
#endif

    // Title screen first; "Quit to title" in the pause menu soft-resets back to here.
    bool continue_game = tl::run_title();
    bn::core::update();     // lets Butano release the title screen's VRAM
    bn::optional<tl::field> field;

    if(continue_game)
    {
        tl::save_data save;

        if(tl::save_read(save))
        {
            tl::story().apply_save(save);
            field.emplace(save);
        }
    }

    if(! field)
    {
        // New game: the four narrator cards, then ask for the player's name.
        tl::run_intro_cards();
        char name[12];
        tl::run_name_entry(name);
        bn::core::update();     // lets Butano release the name entry's VRAM
        tl::story().new_game(name);

        // The prologue starts in the room above Corner Market at 7:00 on Monday with $0 (docs/story_chapter1.md 4.1); the first cutscene
        // (wake_up in tools/cutscenes_src.txt) lets the player lie in bed and fades in.
        tl::save_data start;
        start.map = uint8_t(tl::map_id::player_room);
        start.x = int16_t(5.2 * tl::cell_size);
        start.y = int16_t(3.0 * tl::cell_size);
        start.facing = 0;
        start.day = 1;
        start.minutes = 7 * 60;
        start.money = 0;
        static constexpr int new_game_needs[5] = { 70, 85, 70, 60, 80 };     // Bladder 80 (doc: 55): the room has no bathroom

        for(int need = 0; need < 5; ++need)
        {
            start.need_raw[need] = bn::fixed(new_game_needs[need]).data();
        }

        tl::story().fill_save(start);
        field.emplace(start);
        field->begin_black();
    }

#ifdef TL_DEBUG_CPU
    // Debug build only: stats readable by tools/headless_run.py (command `stats`), found in EWRAM by the magic number.
    static volatile unsigned dbg_stats[8 + 256] __attribute__((section(".ewram"))) = { 0x544C4350, 0, 0, 0, 0, 0, 0, 0 };   // [6] = peak used sprite tiles, [7] = lowest available; [8..] = 1024 byte ring of per-frame cpu %
    // Debug build only: worst CPU usage (percent) and missed frames of the last second, top left.
    tl::ui::label cpu_label;
    int worst = 0;
    int missed = 0;
    int frame = 0;
#endif

    while(true)
    {
        field->update();

        if(field->minigame_pending())
        {
            // A minigame is its own scene: the field is destroyed (freeing the VRAM), the minigame runs, then the field is rebuilt
            // from a snapshot with the result applied (money, needs, clock, story flags).
            tl::minigame_request request = field->minigame();
            tl::save_data snapshot;
            field->snapshot(snapshot);
            field.reset();
            bn::core::update();
            tl::minigame_result result = tl::run_minigame(request);
            tl::apply_minigame_result(snapshot, request, result);
            bn::core::update();
            field.emplace(snapshot);
        }

        bn::core::update();
#ifdef TL_DEBUG_CPU
        int usage = (bn::core::last_cpu_usage() * 100).round_integer();
        worst = usage > worst ? usage : worst;
        missed += bn::core::last_missed_frames();
        reinterpret_cast<volatile unsigned char*>(dbg_stats + 8)[dbg_stats[1] & 1023] = (unsigned char)(usage > 255 ? 255 : usage);
        dbg_stats[1] = dbg_stats[1] + 1;                        // frames
        dbg_stats[2] = dbg_stats[2] + bn::core::last_missed_frames();
        dbg_stats[3] = usage > int(dbg_stats[3]) ? usage : dbg_stats[3];   // peak cpu %
        dbg_stats[4] = dbg_stats[4] + usage;                    // sum of cpu %
        dbg_stats[5] = usage > 85 ? dbg_stats[5] + 1 : dbg_stats[5];
        {
            unsigned used = bn::sprite_tiles::used_tiles_count();
            unsigned avail = bn::sprite_tiles::available_tiles_count();
            dbg_stats[6] = used > dbg_stats[6] ? used : dbg_stats[6];                      // peak used sprite tiles
            dbg_stats[7] = dbg_stats[7] == 0 || avail < dbg_stats[7] ? avail : dbg_stats[7];   // lowest available sprite tiles
        }

        if(++frame % 30 == 0)
        {
            bn::string<40> text("c");
            text.append(bn::to_string<8>(worst));
            text.append(" m");
            text.append(bn::to_string<8>(missed));
            text.append(" u");
            text.append(bn::to_string<8>(bn::sprite_tiles::used_tiles_count()));
            text.append(" a");
            text.append(bn::to_string<8>(bn::sprite_tiles::available_tiles_count()));
            cpu_label.set(tl::ui::font9, 60, 11, text, tl::ui::role::hud_clock);
            worst = 0;
        }
#endif
    }
}
