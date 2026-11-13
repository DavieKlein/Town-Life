#ifndef TL_UI_H
#define TL_UI_H

#include "bn_vector.h"
#include "bn_optional.h"
#include "bn_sprite_ptr.h"
#include "bn_sprite_item.h"
#include "bn_string_view.h"

#include "tl_ui_font.h"

// User interface drawing shared by the menus, dialogs, pause screen, title screen and HUD text.
//
// Two styles (approved proposal): "Paper" (cream panel, dark ink, red title band, gold highlight) by day and
// "Night" (navy panel, white outlined text, gold title, teal highlight) at night. Both use ONE 16-colour sprite
// palette (indices fixed, see tools/ui_assets.py); the style only swaps the colours. All coordinates are screen
// pixels with (0, 0) at the top-left corner.
//
// Text is rendered by software into sprite tiles (bold 9 px / 11 px fonts): one sprite per 32 pixels of text instead
// of one per character, which keeps the 128-sprite budget manageable.
namespace tl::ui
{
    enum class role : uint8_t
    {
        text,           // normal text on a panel
        selected,       // text on the highlight bar
        title,          // title band text
        hint,           // "Choose" / "Back"
        money,          // money on a panel
        hud_clock,      // HUD: white
        hud_money,      // HUD: gold
        name_tag        // gold on the dialogue name tag
    };

    // Night style when true (set from the game clock; the title screen always uses it).
    void set_night(bool night);

    // s81: black cards: the sprite palettes are faded to black (every actor / HUD sprite vanishes) except the UI style palette, so only UI text shows.
    void black_card_palette();
    [[nodiscard]] bool night();

    [[nodiscard]] int text_width(const font_data& font, const bn::string_view& text);

    // One line of text made of a few sprites.
    class label
    {

    public:
        // x = left edge of the first letter, baseline_y = text baseline.
        void set(const font_data& font, int x, int baseline_y, const bn::string_view& text, role r, int z_order = 0);
        void set_right(const font_data& font, int right_x, int baseline_y, const bn::string_view& text, role r);
        void set_centre(const font_data& font, int centre_x, int baseline_y, const bn::string_view& text, role r);
        void clear()
        {
            _sprites.clear();
        }

        [[nodiscard]] bool empty() const
        {
            return _sprites.empty();
        }

    private:
        bn::vector<bn::sprite_ptr, 8> _sprites;
    };

    // Rounded panel with border (and a title band when `titled`) at x, y, size w x h (w >= 112, h >= 32; titled
    // panels h >= 64). Built from a few pre-rendered pieces.
    class panel
    {

    public:
        void open(int x, int y, int w, int h, bool titled);
        void close()
        {
            _sprites.clear();
        }

        [[nodiscard]] bool is_open() const
        {
            return ! _sprites.empty();
        }

    private:
        bn::vector<bn::sprite_ptr, 24> _sprites;
    };

    // Highlight bar exactly fitting one row (13 px high, cursor triangle at the left); x, y = top-left, w >= 90.
    class bar
    {

    public:
        void set(int x, int y, int w);
        void clear()
        {
            _sprites.clear();
            _width = 0;
        }

    private:
        bn::vector<bn::sprite_ptr, 8> _sprites;
        int _width = 0;
        int _x = 0;
        int _y = 0;
    };

    // One sprite of a UI piece sheet in the current style palette (priority 0): x, y = top-left, `frame` = graphic index.
    // (s81: optional: nothing is added when VRAM / OAM is short)
    void add_piece(bn::ivector<bn::sprite_ptr>& list, const bn::sprite_item& item, int x, int y, int frame, bool hflip, int z_order);

    // Round A / B button icons (frame 0 = A, 1 = B), x, y = top-left of the 10 x 10 circle.
    [[nodiscard]] bn::optional<bn::sprite_ptr> make_button(int frame, int x, int y);

    // "A  Choose   B  Back" (both) or "A  OK" row; x, y = top-left of the row (icons 10 px high).
    class hint_row
    {

    public:
        void open(int x, int y, bool with_back, const char* ok_text = nullptr);
        void close();

    private:
        bn::optional<bn::sprite_ptr> _a;
        bn::optional<bn::sprite_ptr> _b;
        label _ok;
        label _back;
    };

    // The bobbing "A" cue above an interactable (tip of the bubble tail at x, y).
    [[nodiscard]] bn::optional<bn::sprite_ptr> make_cue(int x, int y);
    void place_cue(bn::sprite_ptr& cue, int tip_x, int tip_y);
}

#endif
