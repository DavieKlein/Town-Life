#ifndef TL_PAUSE_H
#define TL_PAUSE_H

#include "bn_vector.h"
#include "bn_sprite_ptr.h"
#include "bn_string_view.h"
#include "bn_sprite_text_generator.h"

namespace tl
{
    // A dark panel (the menu panel sprites, tiled) at screen position (x, y) = top-left, centre of the screen
    // is (0, 0). Width 96..222, height 64 (rows = 1) or 127 (rows = 2).
    class panel
    {

    public:
        void open(int x, int y, int width, int rows);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return ! _sprites.empty();
        }

    private:
        bn::vector<bn::sprite_ptr, 10> _sprites;
    };

    // A message with up to 3 text lines and 1-2 options (Yes/No, OK), centred in the play area.
    class dialog
    {

    public:
        static constexpr int cancelled = -2;
        static constexpr int open_still = -1;

        explicit dialog(bn::sprite_text_generator& text_generator);

        // `lines` and `options` must stay valid while the dialog is open (use static constexpr arrays).
        // `centre_y` is the vertical middle of the box in screen coordinates.
        void open(const bn::string_view* lines, int lines_count, const bn::string_view* options,
                  int options_count, int centre_y = -16);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return _panel.is_open();
        }

        // Returns the chosen option, cancelled (B) or open_still.
        [[nodiscard]] int update();

    private:
        bn::sprite_text_generator& _text_generator;
        panel _panel;
        bn::vector<bn::sprite_ptr, 80> _text;
        bn::vector<bn::sprite_ptr, 2> _cursor;
        const bn::string_view* _options = nullptr;
        int _options_count = 0;
        int _selected = 0;
        int _x = 0;
        int _options_y = 0;

        void _place_cursor();
    };

    // What the pause screen shows.
    struct pause_info
    {
        int day = 1;
        int minutes = 0;                // time of day
        int money = 0;
        int need_values[5] = {};        // Hunger, Energy, Hygiene, Fun, Bladder, 0..100
        const char* objective = "";
    };

    // The START screen: stats on the left, options on the right.
    class pause_screen
    {

    public:
        static constexpr int resume = 0;
        static constexpr int save = 1;
        static constexpr int quit = 2;
        static constexpr int open_still = -1;

        explicit pause_screen(bn::sprite_text_generator& text_generator);

        void open(const pause_info& info);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return _panel.is_open();
        }

        // Returns resume / save / quit, or open_still. B or START give resume.
        [[nodiscard]] int update();

    private:
        bn::sprite_text_generator& _text_generator;
        panel _panel;
        bn::vector<bn::sprite_ptr, 104> _text;
        bn::vector<bn::sprite_ptr, 2> _cursor;
        int _selected = 0;

        void _place_cursor();
    };
}

#endif
