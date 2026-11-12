#include "tl_menu.h"
#include "tl_audio.h"

#include "bn_keypad.h"

namespace tl
{
    namespace
    {
        constexpr int panel_w = 120;
        constexpr int panel_x = 240 - panel_w - 4;
        constexpr int panel_y = 5;
        constexpr int title_height = 17;
        constexpr int row_pitch = 14;
        constexpr int hint_height = 19;
    }

    void menu::_open_panel(const bn::string_view& title, int rows)
    {
        close();
        _open = true;
        _selected = 0;
        _labels.clear();

        for(int index = 0; index < rows; ++index)
        {
            _labels.emplace_back();
        }

        int height = title_height + (rows * row_pitch) + hint_height;
        _panel.open(panel_x, panel_y, panel_w, height, true);
        _title_label.set(ui::font9, panel_x + 7, panel_y + 12, title, ui::role::title);
    }

    void menu::open(const bn::string_view& title, const bn::string_view* options, int options_count)
    {
        BN_ASSERT(options_count <= max_options, "Too many menu options: ", options_count);
        _info = false;
        _options = options;
        _options_count = options_count;
        _open_panel(title, options_count);
        _hint.open(panel_x + 7, panel_y + title_height + 2 + (options_count * row_pitch) + 3, true);
        _draw_rows();
    }

    void menu::open_info(const bn::string_view& title, const bn::string_view* lines, int lines_count)
    {
        _info = true;
        _options = lines;
        _options_count = lines_count < 3 ? lines_count : 3;
        _open_panel(title, _options_count);
        _hint.open(panel_x + 7, panel_y + title_height + 2 + (_options_count * row_pitch) + 3, false);
        _draw_rows();
    }

    void menu::_draw_rows()
    {
        int top = panel_y + title_height;

        for(int index = 0; index < _options_count; ++index)
        {
            if(_info)
            {
                _labels[index].set(ui::font9, panel_x + 8, top + 11 + (index * row_pitch), _options[index],
                                   ui::role::text);
            }
            else
            {
                bool selected = index == _selected;
                _labels[index].set(ui::font9, panel_x + 17, top + 2 + (index * row_pitch) + 10, _options[index],
                                   selected ? ui::role::selected : ui::role::text);
            }
        }

        if(! _info)
        {
            _bar.set(panel_x + 5, top + 2 + (_selected * row_pitch), panel_w - 10);
        }
    }

    void menu::close()
    {
        _open = false;
        _panel.close();
        _bar.clear();
        _title_label.clear();
        _labels.clear();
        _hint.close();
    }

    int menu::update()
    {
        if(! _open)
        {
            return cancelled;
        }

        if(_info)
        {
            if(bn::keypad::a_pressed() || bn::keypad::b_pressed())
            {
                close();
                return 0;
            }

            return open_still;
        }

        if(bn::keypad::up_pressed() && _selected > 0)
        {
            --_selected;
            audio::play(audio::sfx::blip);
            _draw_rows();
        }
        else if(bn::keypad::down_pressed() && _selected < _options_count - 1)
        {
            ++_selected;
            audio::play(audio::sfx::blip);
            _draw_rows();
        }

        if(bn::keypad::a_pressed())
        {
            audio::play(audio::sfx::confirm);
            int chosen = _selected;
            close();
            return chosen;
        }

        if(bn::keypad::b_pressed())
        {
            audio::play(audio::sfx::back);
            close();
            return cancelled;
        }

        return open_still;
    }
}
