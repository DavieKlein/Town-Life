#include "tl_title.h"
#include "tl_audio.h"

#include "bn_core.h"
#include "bn_color.h"
#include "bn_keypad.h"
#include "bn_vector.h"
#include "bn_bg_palettes.h"
#include "bn_sprite_palettes.h"
#include "bn_sprite_text_generator.h"
#include "bn_sprite_palette_item.h"

#include "common_variable_16x16_sprite_font.h"

#include "tl_save.h"
#include "tl_pause.h"
#include "tl_ui.h"

namespace tl
{
    namespace
    {
        constexpr int menu_x = 64;
        constexpr int menu_w = 112;

        // "TOWN LIFE" in gold (the common 16x16 font: 14 = letters, 12 = outline).
        constexpr bn::color gold_colours[16] = {
            bn::color(0, 0, 0), bn::color(0, 0, 0), bn::color(0, 0, 0), bn::color(0, 0, 0), bn::color(0, 0, 0),
            bn::color(0, 0, 0), bn::color(0, 0, 0), bn::color(0, 0, 0), bn::color(0, 0, 0), bn::color(0, 0, 0),
            bn::color(0, 0, 0), bn::color(0, 0, 0), bn::color(2, 1, 4), bn::color(0, 0, 0), bn::color(31, 26, 11),
            bn::color(0, 0, 0)
        };

        constexpr bn::sprite_palette_item gold_palette(bn::span<const bn::color>(gold_colours), bn::bpp_mode::BPP_4);
    }

    bool run_title()
    {
        bn::bg_palettes::set_fade(bn::color(0, 0, 0), 0);
        bn::sprite_palettes::set_fade(bn::color(0, 0, 0), 0);
        bn::bg_palettes::set_transparent_color(bn::color(3, 4, 8));
        ui::set_night(true);       // the title screen always uses the Night style

        bn::sprite_text_generator big_text(common::variable_16x16_sprite_font);
        big_text.set_bg_priority(0);
        big_text.set_center_alignment();
        big_text.set_palette_item(gold_palette);

        bn::vector<bn::sprite_ptr, 16> big_sprites;
        big_text.generate(0, -50, "TOWN LIFE", big_sprites);
        ui::label subtitle;
        ui::label version;
        subtitle.set_centre(ui::font9, 120, 56, "A story of the city", ui::role::hud_clock);
        version.set_centre(ui::font9, 120, 150, "build " __DATE__ " " __TIME__, ui::role::hint);

        save_data existing;
        bool has_save = save_read(existing);

        static constexpr bn::string_view both[] = { "Continue", "New Game" };
        static constexpr bn::string_view only_new[] = { "New Game" };
        const bn::string_view* options = has_save ? both : only_new;
        int options_count = has_save ? 2 : 1;

        ui::panel box;
        ui::bar highlight;
        ui::label option_labels[2];
        dialog confirm;
        int selected = 0;
        bool confirming = false;
        int box_y = 78;
        int box_h = 16 + (options_count * 15) < 36 ? 36 : 16 + (options_count * 15);

        auto draw = [&]()
        {
            for(int index = 0; index < options_count; ++index)
            {
                option_labels[index].set(ui::font9, menu_x + 5 + 12, box_y + 5 + (index * 15) + 10, options[index],
                                         index == selected ? ui::role::selected : ui::role::text);
            }

            highlight.set(menu_x + 5, box_y + 5 + (selected * 15), menu_w - 10);
        };

        auto close_box = [&]()
        {
            box.close();
            highlight.clear();

            for(ui::label& label : option_labels)
            {
                label.clear();
            }
        };

        box.open(menu_x, box_y, menu_w, box_h, false);
        draw();
        bn::core::update();

        while(true)
        {
            if(confirming)
            {
                int choice = confirm.update();

                if(choice != dialog::open_still)
                {
                    confirming = false;

                    if(choice == 0)
                    {
                        break;      // New Game confirmed
                    }

                    box.open(menu_x, box_y, menu_w, box_h, false);
                    subtitle.set_centre(ui::font9, 120, 56, "A story of the city", ui::role::hud_clock);
                    draw();
                }
            }
            else
            {
                if(bn::keypad::up_pressed() && selected > 0)
                {
                    --selected;
                    audio::play(audio::sfx::blip);
                    draw();
                }
                else if(bn::keypad::down_pressed() && selected < options_count - 1)
                {
                    ++selected;
                    audio::play(audio::sfx::blip);
                    draw();
                }

                if(bn::keypad::a_pressed() || bn::keypad::start_pressed())
                {
                    if(has_save && selected == 0)
                    {
                        bn::bg_palettes::set_transparent_color(bn::color(0, 0, 0));
                        return true;
                    }

                    if(has_save)
                    {
                        static constexpr bn::string_view lines[] = {
                            "Start a new game?", "Your saved game stays", "until you save again." };
                        static constexpr bn::string_view yes_no[] = { "Yes", "No" };
                        close_box();
                        subtitle.clear();
                        confirm.open("New game", lines, 3, yes_no, 2, 40);
                        confirming = true;
                    }
                    else
                    {
                        break;
                    }
                }
            }

            bn::core::update();
        }

        bn::bg_palettes::set_transparent_color(bn::color(0, 0, 0));
        return false;
    }

    void run_intro_cards()
    {
        static constexpr const char* cards[][3] = {
            { "Corner Market.", "40 years of bread,", "gossip and good mornings." },
            { "You work here.", "You live upstairs.", "" },
            { "Today is a normal day.", "", "" },
            { "(It is not.)", "", "" },
        };

        ui::set_night(true);
        bn::bg_palettes::set_fade(bn::color(0, 0, 0), 1);

        for(const auto& card : cards)
        {
            ui::label lines[3];
            int count = card[2][0] ? 3 : (card[1][0] ? 2 : 1);
            int top = 80 - (count * 7);

            for(int index = 0; index < count; ++index)
            {
                lines[index].set_centre(ui::font11, 120, top + 11 + (index * 14), card[index], ui::role::hud_clock);
            }

            bool skipped = false;

            for(int frame = 0; frame < 12 + 130 + 12 && ! skipped; ++frame)
            {
                int fade = frame < 12 ? 12 - frame : (frame >= 142 ? frame - 142 : 0);
                bn::sprite_palettes::set_fade(bn::color(0, 0, 0), bn::fixed(fade) / 12);
                skipped = frame > 20 && (bn::keypad::a_pressed() || bn::keypad::b_pressed() || bn::keypad::start_pressed());
                bn::core::update();
            }

            for(ui::label& line : lines)
            {
                line.clear();
            }

            bn::core::update();
        }

        bn::sprite_palettes::set_fade(bn::color(0, 0, 0), 0);
        bn::bg_palettes::set_fade(bn::color(0, 0, 0), 0);
    }
}
