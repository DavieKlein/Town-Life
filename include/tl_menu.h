#ifndef TL_MENU_H
#define TL_MENU_H

#include "bn_vector.h"
#include "bn_optional.h"
#include "bn_sprite_ptr.h"
#include "bn_string_view.h"
#include "bn_sprite_text_generator.h"

namespace tl
{
    // Small pop-up menu (title + 3 visible options, longer lists scroll) in the HUD style: up/down
    // choose, A confirms, B cancels. open_info() shows up to 3 lines of text instead of options.
    class menu
    {

    public:
        static constexpr int max_options = 3;
        static constexpr int cancelled = -2;
        static constexpr int open_still = -1;

        explicit menu(bn::sprite_text_generator& text_generator);

        // The options array (and the strings) must stay valid while the menu is open.
        void open(const bn::string_view& title, const bn::string_view* options, int options_count);

        // Info message: title + lines, closed with A or B (update() returns 0 or cancelled).
        void open_info(const bn::string_view& title, const bn::string_view* lines, int lines_count);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return _open;
        }

        // Returns the chosen option index, cancelled, or open_still.
        [[nodiscard]] int update();

    private:
        bn::sprite_text_generator& _text_generator;
        bn::optional<bn::sprite_ptr> _left;
        bn::optional<bn::sprite_ptr> _right;
        bn::optional<bn::sprite_ptr> _highlight;
        bn::optional<bn::sprite_ptr> _highlight_right;
        bn::vector<bn::sprite_ptr, 24> _text_sprites;
        bn::vector<bn::sprite_ptr, 2> _cursor_sprites;
        bn::vector<bn::sprite_ptr, 2> _arrow_sprites;
        const bn::string_view* _options = nullptr;
        bn::string_view _title;
        int _options_count = 0;
        int _selected = 0;
        int _top = 0;
        bool _open = false;
        bool _info = false;

        void _open_panel();
        void _draw_options();
        void _place_cursor();
    };
}

#endif
