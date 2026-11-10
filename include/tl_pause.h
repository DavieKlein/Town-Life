#ifndef TL_PAUSE_H
#define TL_PAUSE_H

#include "bn_vector.h"
#include "bn_sprite_ptr.h"
#include "bn_string_view.h"

#include "tl_ui.h"

namespace tl
{
    // A titled message box with up to 3 text lines and 1-2 options (Yes/No, OK), centred in the play area
    // (day/night style, see tl_ui.h).
    class dialog
    {

    public:
        static constexpr int cancelled = -2;
        static constexpr int open_still = -1;

        // `lines` and `options` must stay valid while the dialog is open (use static constexpr arrays).
        // `top` is the y of the panel top; -1 centres it in the 128 px play area.
        void open(const bn::string_view& title, const bn::string_view* lines, int lines_count,
                  const bn::string_view* options, int options_count, int top = -1);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return _panel.is_open();
        }

        // Returns the chosen option, cancelled (B) or open_still.
        [[nodiscard]] int update();

    private:
        ui::panel _panel;
        ui::bar _bar;
        ui::label _title;
        bn::vector<ui::label, 3> _lines;
        bn::vector<ui::label, 2> _option_labels;
        ui::hint_row _hint;
        const bn::string_view* _options = nullptr;
        int _options_count = 0;
        int _selected = 0;
        int _options_y = 0;

        void _draw_options();
    };

    // What the pause screen shows.
    struct pause_info
    {
        int day = 1;
        int minutes = 0;                // time of day
        int money = 0;
        int need_values[5] = {};        // Hunger, Energy, Hygiene, Fun, Bladder, 0..100
        int social = 0;                 // Social need 0..100 (6th line)
        int bag = 0;                    // cans + bottles in the bag (max 10)
        int credit = 0;                 // deposit credit 0 or 1 (of 2)
        int coins = 0;                  // City Coins
        const char* objective = "";
        bool great = false;             // s71: "Feeling great" (all needs high)
        bool sick = false;              // s64: "Sick" next to the clock line
        int debt = 0;                   // open clinic bill ($)
    };

    // The START screen: stats on the left, options on the right.
    class pause_screen
    {

    public:
        static constexpr int resume = 0;
        static constexpr int log = 1;
        static constexpr int collection = 2;
        static constexpr int save = 3;
        static constexpr int quit = 4;
        static constexpr int options_count = 5;
        static constexpr int open_still = -1;

        void open(const pause_info& info);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return _panel.is_open();
        }

        // Returns resume / save / quit, or open_still. B or START give resume.
        [[nodiscard]] int update();

    private:
        ui::panel _panel;
        ui::bar _bar;
        bn::vector<ui::label, 20> _labels;
        ui::label _option_labels[options_count];
        bn::vector<bn::sprite_ptr, 6> _bars;
        ui::hint_row _hint;
        int _selected = 0;

        void _draw_options();
    };

    // s64: the collection screen (pause menu): one page per set (left / right), four 32x32 icons rendered from the real 3D props
    // (found ones in colour, missing ones as dark slots), the name of the selected item (up / down moves the cursor over the icons
    // is not needed: left / right change the set, up / down pick an item) and the set reward.
    class collection_screen
    {

    public:
        void open(uint16_t mask, uint8_t paid);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return _panel.is_open();
        }

        // True when closed (A, B or START).
        [[nodiscard]] bool update();

    private:
        ui::panel _panel;
        bn::vector<ui::label, 8> _labels;
        bn::vector<bn::sprite_ptr, 4> _icons;
        ui::hint_row _hint;
        ui::bar _bar;
        uint16_t _mask = 0;
        uint8_t _paid = 0;
        int _set = 0;
        int _item = 0;

        void _draw();
    };

    // What the mission log shows: the current mission and the finished ones (most recent / highest first).
    struct log_info
    {
        const char* current_title = "";
        const char* current_objective = "";
        int coins = 0;
        int done_count = 0;
        const char* done_titles[24] = {};
    };

    // The mission log screen (opened from the pause screen): up/down scroll the list of finished missions, B closes.
    class log_screen
    {

    public:
        void open(const log_info& info);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return _panel.is_open();
        }

        // Returns true when the screen was closed (A, B or START).
        [[nodiscard]] bool update();

    private:
        static constexpr int visible_rows = 4;

        ui::panel _panel;
        bn::vector<ui::label, 14> _labels;
        bn::vector<ui::label, visible_rows> _rows;
        ui::hint_row _hint;
        log_info _info;
        int _scroll = 0;

        void _draw_rows();
    };
}

#endif
