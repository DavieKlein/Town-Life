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

#ifdef TL_DEBUG_CPU
#include "bn_core.h"
#include "bn_string.h"
#include "tl_ui.h"
#endif

int main()
{
    bn::core::init();

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
        // New game: ask for the player's name first.
        char name[12];
        tl::run_name_entry(name);
        bn::core::update();     // lets Butano release the name entry's VRAM
        tl::story().new_game(name);

        // Start on the sidewalk in front of Corner Market.
        field.emplace(tl::map_id::city_centre, 44 * tl::cell_size, 19 * tl::cell_size, tl::direction::down);
    }

#ifdef TL_DEBUG_CPU
    // Debug build only: worst CPU usage (percent) and missed frames of the last second, top left.
    tl::ui::label cpu_label;
    int worst = 0;
    int missed = 0;
    int frame = 0;
#endif

    while(true)
    {
        field->update();
        bn::core::update();
#ifdef TL_DEBUG_CPU
        int usage = (bn::core::last_cpu_usage() * 100).round_integer();
        worst = usage > worst ? usage : worst;
        missed += bn::core::last_missed_frames();

        if(++frame % 30 == 0)
        {
            bn::string<24> text("cpu ");
            text.append(bn::to_string<8>(worst));
            text.append(" miss ");
            text.append(bn::to_string<8>(missed));
            cpu_label.set(tl::ui::font9, 100, 11, text, tl::ui::role::hud_clock);
            worst = 0;
        }
#endif
    }
}
