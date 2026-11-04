#ifndef TL_MENU_H
#define TL_MENU_H

#include "bn_vector.h"
#include "bn_string_view.h"

#include "tl_ui.h"

namespace tl
{
    // Pop-up menu at the top right (see tl_ui.h for the two day/night styles): title band, up to 5 option rows with a
    // rounded highlight bar, "A Choose / B Back" hint. up/down choose, A confirms, B cancels. open_info() shows up to
    // 3 lines of text instead of options (A or B closes).
    class menu
    {

    public:
        static constexpr int max_options = 5;
        static constexpr int cancelled = -2;
        static constexpr int open_still = -1;

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
        ui::panel _panel;
        ui::bar _bar;
        ui::label _title_label;
        bn::vector<ui::label, max_options> _labels;
        ui::hint_row _hint;
        const bn::string_view* _options = nullptr;
        int _options_count = 0;
        int _selected = 0;
        bool _open = false;
        bool _info = false;

        void _open_panel(const bn::string_view& title, int rows);
        void _draw_rows();
    };
}

#endif
