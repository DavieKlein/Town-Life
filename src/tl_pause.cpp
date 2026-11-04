#include "tl_pause.h"

#include "bn_keypad.h"
#include "bn_string.h"
#include "bn_sprite_items_menu_left.h"
#include "bn_sprite_items_menu_right.h"

namespace tl
{
    namespace
    {
        constexpr int panel_width = 222;
        constexpr int panel_x = -111;
        constexpr int pause_y = -78;
        constexpr int line_step = 11;

        constexpr bn::string_view need_names[] = { "Hunger", "Energy", "Hygiene", "Fun", "Bladder" };
        constexpr bn::string_view pause_options[] = { "Resume", "Save game", "Quit to title" };
    }

    void panel::open(int x, int y, int width, int rows)
    {
        close();

        // The menu sprites are 64 wide with a border only on their left edge (right piece: 32 wide, border on
        // the right). Left pieces overlap by one column, each lying behind the previous one, which hides its
        // border; rows overlap by one line for the same reason.
        int lefts = ((width - 96 + 62) / 63) + 1;      // widths 96 and 222 fit exactly

        for(int row = 0; row < rows; ++row)
        {
            int top = y + (row * 63);

            for(int index = 0; index < lefts; ++index)
            {
                bn::sprite_ptr sprite = bn::sprite_items::menu_left.create_sprite(x + (index * 63) + 32, top + 32);
                sprite.set_bg_priority(0);
                sprite.set_z_order(20 + index);
                sprite.set_vertical_flip(row > 0);      // keeps the gradient smooth at the seam
                _sprites.push_back(bn::move(sprite));
            }

            bn::sprite_ptr right = bn::sprite_items::menu_right.create_sprite(x + width - 16, top + 32);
            right.set_bg_priority(0);
            right.set_z_order(19);
            right.set_vertical_flip(row > 0);
            _sprites.push_back(bn::move(right));
        }
    }

    void panel::close()
    {
        _sprites.clear();
    }

    // ---------------------------------------------------------------------------------------------------------

    dialog::dialog(bn::sprite_text_generator& text_generator) :
        _text_generator(text_generator)
    {
    }

    void dialog::open(const bn::string_view* lines, int lines_count, const bn::string_view* options,
                      int options_count, int centre_y)
    {
        close();
        _options = options;
        _options_count = options_count;
        _selected = 0;
        _x = panel_x + 12;
        int top = centre_y - 32;
        _panel.open(panel_x, top, panel_width, 1);
        _text_generator.set_left_alignment();

        for(int index = 0; index < lines_count; ++index)
        {
            _text_generator.generate(_x, top + 9 + (index * 9), lines[index], _text);
        }

        _options_y = top + 9 + (lines_count * 9) + 4;

        for(int index = 0; index < options_count; ++index)
        {
            _text_generator.generate(_x + 12, _options_y + (index * 10), options[index], _text);
        }

        _place_cursor();
    }

    void dialog::close()
    {
        _panel.close();
        _text.clear();
        _cursor.clear();
    }

    void dialog::_place_cursor()
    {
        _cursor.clear();
        _text_generator.set_left_alignment();
        _text_generator.generate(_x, _options_y + (_selected * 10), ">", _cursor);
    }

    int dialog::update()
    {
        if(! is_open())
        {
            return cancelled;
        }

        if(bn::keypad::up_pressed() && _selected > 0)
        {
            --_selected;
            _place_cursor();
        }
        else if(bn::keypad::down_pressed() && _selected < _options_count - 1)
        {
            ++_selected;
            _place_cursor();
        }

        if(bn::keypad::a_pressed())
        {
            int chosen = _selected;
            close();
            return chosen;
        }

        if(bn::keypad::b_pressed())
        {
            close();
            return cancelled;
        }

        return open_still;
    }

    // ---------------------------------------------------------------------------------------------------------

    pause_screen::pause_screen(bn::sprite_text_generator& text_generator) :
        _text_generator(text_generator)
    {
    }

    void pause_screen::open(const pause_info& info)
    {
        close();
        _selected = 0;
        _panel.open(panel_x, pause_y, panel_width, 2);
        _text_generator.set_left_alignment();

        int left_x = panel_x + 10;
        int right_x = panel_x + 118;
        int y = pause_y + 8;

        bn::string<16> line("Day ");
        line.append(bn::to_string<8>(info.day));
        _text_generator.generate(left_x, y, line, _text);

        int hours = (info.minutes / 60) % 24;
        int minutes = info.minutes % 60;
        line = bn::string<16>();
        line.append(bn::to_string<4>(hours % 12 == 0 ? 12 : hours % 12));
        line.append(':');

        if(minutes < 10)
        {
            line.append('0');
        }

        line.append(bn::to_string<4>(minutes));
        line.append(hours >= 12 ? " pm" : " am");
        _text_generator.generate(left_x, y + line_step, line, _text);

        line = bn::string<16>("$");
        line.append(bn::to_string<12>(info.money));
        _text_generator.generate(left_x, y + (2 * line_step), line, _text);

        for(int need = 0; need < 5; ++need)
        {
            int ny = y + ((4 + need) * line_step);
            _text_generator.generate(left_x, ny, need_names[need], _text);
            line = bn::to_string<16>(info.need_values[need]);
            _text_generator.set_right_alignment();
            _text_generator.generate(left_x + 92, ny, line, _text);
            _text_generator.set_left_alignment();
        }

        for(int option = 0; option < 3; ++option)
        {
            _text_generator.generate(right_x + 10, y + (option * line_step), pause_options[option], _text);
        }

        // objective, wrapped at 11 characters, up to 3 lines
        _text_generator.generate(right_x, y + (4 * line_step), "Goal:", _text);
        bn::string_view objective(info.objective);
        int pos = 0;
        int length = objective.size();

        for(int row = 0; row < 3 && pos < length; ++row)
        {
            while(pos < length && objective[pos] == ' ')
            {
                ++pos;
            }

            int end = pos + 11 < length ? pos + 11 : length;

            if(end < length)
            {
                int cut = end;

                while(cut > pos && objective[cut] != ' ')
                {
                    --cut;
                }

                if(cut > pos)
                {
                    end = cut;
                }
            }

            if(end > pos)
            {
                _text_generator.generate(right_x, y + ((5 + row) * line_step),
                                         objective.substr(pos, end - pos), _text);
            }

            pos = end;
        }

        _place_cursor();
    }

    void pause_screen::close()
    {
        _panel.close();
        _text.clear();
        _cursor.clear();
    }

    void pause_screen::_place_cursor()
    {
        _cursor.clear();
        _text_generator.set_left_alignment();
        _text_generator.generate(panel_x + 118, pause_y + 8 + (_selected * line_step), ">", _cursor);
    }

    int pause_screen::update()
    {
        if(! is_open())
        {
            return resume;
        }

        if(bn::keypad::up_pressed() && _selected > 0)
        {
            --_selected;
            _place_cursor();
        }
        else if(bn::keypad::down_pressed() && _selected < 2)
        {
            ++_selected;
            _place_cursor();
        }

        if(bn::keypad::a_pressed())
        {
            return _selected;
        }

        if(bn::keypad::b_pressed() || bn::keypad::start_pressed())
        {
            return resume;
        }

        return open_still;
    }
}
