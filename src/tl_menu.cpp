#include "tl_menu.h"

#include "bn_keypad.h"
#include "bn_sprite_items_menu_left.h"
#include "bn_sprite_items_menu_right.h"
#include "bn_sprite_items_menu_highlight.h"

namespace tl
{
    namespace
    {
        // Panel 96x64, top-right of the play area (screen coordinates, centre = 0, 0).
        constexpr int panel_x = 120 - 96 - 6;           // left edge
        constexpr int panel_y = -80 + 6;                // top edge
        constexpr int first_option_y = panel_y + 19;
        constexpr int option_step = 12;
    }

    menu::menu(bn::sprite_text_generator& text_generator) :
        _text_generator(text_generator)
    {
    }

    void menu::_open_panel()
    {
        close();
        _open = true;
        _selected = 0;
        _top = 0;

        _left = bn::sprite_items::menu_left.create_sprite(panel_x + 32, panel_y + 32);
        _right = bn::sprite_items::menu_right.create_sprite(panel_x + 64 + 16, panel_y + 32);
        _highlight = bn::sprite_items::menu_highlight.create_sprite(0, 0, 0);
        _highlight_right = bn::sprite_items::menu_highlight.create_sprite(0, 0, 1);

        for(bn::sprite_ptr* sprite : { &*_left, &*_right, &*_highlight, &*_highlight_right })
        {
            sprite->set_bg_priority(0);
            sprite->set_z_order(2);
        }

        _highlight->set_z_order(1);
        _highlight_right->set_z_order(1);
    }

    void menu::open(const bn::string_view& title, const bn::string_view* options, int options_count)
    {
        _open_panel();
        _info = false;
        _options = options;
        _title = title;
        _options_count = options_count;
        _draw_options();
    }

    void menu::open_info(const bn::string_view& title, const bn::string_view* lines, int lines_count)
    {
        _open_panel();
        _info = true;
        _options = lines;
        _title = title;
        _options_count = lines_count < max_options ? lines_count : max_options;
        _highlight->set_visible(false);
        _highlight_right->set_visible(false);
        _draw_options();
    }

    void menu::_draw_options()
    {
        _text_sprites.clear();
        _arrow_sprites.clear();
        _text_generator.set_left_alignment();
        _text_generator.generate(panel_x + 6, panel_y + 7, _title, _text_sprites);
        int visible = _options_count < max_options ? _options_count : max_options;

        for(int index = 0; index < visible; ++index)
        {
            _text_generator.generate(panel_x + (_info ? 6 : 16), first_option_y + (index * option_step),
                                     _options[_top + index], _text_sprites);
        }

        _text_generator.generate(panel_x + 6, panel_y + 56, _info ? "A:ok" : "A:ok  B:back", _text_sprites);

        if(! _info)
        {
            if(_top > 0)
            {
                _text_generator.generate(panel_x + 84, first_option_y - 8, "^", _arrow_sprites);
            }

            if(_top + max_options < _options_count)
            {
                _text_generator.generate(panel_x + 84, first_option_y + (max_options * option_step) - 8, "v",
                                         _arrow_sprites);
            }

            _place_cursor();
        }
    }

    void menu::close()
    {
        _open = false;
        _left.reset();
        _right.reset();
        _highlight.reset();
        _highlight_right.reset();
        _text_sprites.clear();
        _cursor_sprites.clear();
        _arrow_sprites.clear();
    }

    void menu::_place_cursor()
    {
        int y = first_option_y + ((_selected - _top) * option_step);
        _highlight->set_position(panel_x + 3 + 16, y + 6);
        _highlight_right->set_position(panel_x + 3 + 48, y + 6);
        _cursor_sprites.clear();
        _text_generator.generate(panel_x + 7, y, ">", _cursor_sprites);
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

            if(_selected < _top)
            {
                _top = _selected;
            }

            _draw_options();
        }
        else if(bn::keypad::down_pressed() && _selected < _options_count - 1)
        {
            ++_selected;

            if(_selected >= _top + max_options)
            {
                _top = _selected - max_options + 1;
            }

            _draw_options();
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
}
