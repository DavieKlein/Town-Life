#ifndef TL_MENU_H
#define TL_MENU_H

#include "bn_vector.h"
#include "bn_optional.h"
#include "bn_sprite_ptr.h"
#include "bn_string_view.h"
#include "bn_sprite_text_generator.h"

namespace tl
{
    // Small pop-up menu (title + up to 3 options) in the HUD style: up/down choose, A confirms,
    // B cancels.
    class menu
    {

    public:
        static constexpr int max_options = 3;
        static constexpr int cancelled = -2;
        static constexpr int open_still = -1;

        explicit menu(bn::sprite_text_generator& text_generator);

        void open(const bn::string_view& title, const bn::string_view* options, int options_count);
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
        int _options_count = 0;
        int _selected = 0;
        bool _open = false;

        void _place_cursor();
    };
}

#endif
