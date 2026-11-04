#include "tl_title.h"

#include "bn_core.h"
#include "bn_color.h"
#include "bn_keypad.h"
#include "bn_vector.h"
#include "bn_bg_palettes.h"
#include "bn_sprite_palettes.h"
#include "bn_sprite_text_generator.h"

#include "common_variable_8x8_sprite_font.h"
#include "common_variable_16x16_sprite_font.h"

#include "tl_save.h"
#include "tl_pause.h"

namespace tl
{
    namespace
    {
        constexpr int options_x = -48;
        constexpr int options_y = -2;       // panel top
    }

    bool run_title()
    {
        bn::bg_palettes::set_fade(bn::color(0, 0, 0), 0);
        bn::sprite_palettes::set_fade(bn::color(0, 0, 0), 0);
        bn::bg_palettes::set_transparent_color(bn::color(3, 4, 8));

        bn::sprite_text_generator text(common::variable_8x8_sprite_font);
        bn::sprite_text_generator big_text(common::variable_16x16_sprite_font);
        text.set_bg_priority(0);
        big_text.set_bg_priority(0);
        big_text.set_center_alignment();
        text.set_center_alignment();

        bn::vector<bn::sprite_ptr, 40> labels;
        big_text.generate(0, -50, "TOWN LIFE", labels);
        text.generate(0, -28, "A story of the city", labels);
        text.generate(0, 66, "build " __DATE__ " " __TIME__, labels);

        save_data existing;
        bool has_save = save_read(existing);

        static constexpr bn::string_view both[] = { "Continue", "New Game" };
        static constexpr bn::string_view only_new[] = { "New Game" };
        const bn::string_view* options = has_save ? both : only_new;
        int options_count = has_save ? 2 : 1;

        panel box;
        bn::vector<bn::sprite_ptr, 24> option_sprites;
        bn::vector<bn::sprite_ptr, 2> cursor;
        dialog confirm(text);
        int selected = 0;
        bool confirming = false;

        auto draw = [&]()
        {
            option_sprites.clear();
            cursor.clear();
            text.set_left_alignment();

            for(int index = 0; index < options_count; ++index)
            {
                text.generate(options_x + 22, options_y + 20 + (index * 14), options[index], option_sprites);
            }

            text.generate(options_x + 10, options_y + 20 + (selected * 14), ">", cursor);
            text.set_center_alignment();
        };

        box.open(options_x, options_y, 96, 1);
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

                    box.open(options_x, options_y, 96, 1);
                    draw();
                }
            }
            else
            {
                if(bn::keypad::up_pressed() && selected > 0)
                {
                    --selected;
                    draw();
                }
                else if(bn::keypad::down_pressed() && selected < options_count - 1)
                {
                    ++selected;
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
                        box.close();
                        option_sprites.clear();
                        cursor.clear();
                        confirm.open(lines, 3, yes_no, 2, 20);
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
}
