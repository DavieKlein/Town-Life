#ifndef TL_PHONE_H
#define TL_PHONE_H

#include "bn_vector.h"
#include "bn_string.h"
#include "bn_sprite_ptr.h"

#include "tl_ui.h"

namespace tl
{
    // s64: food that can be ordered by phone (pricier than the shops; arrives 30 game minutes after paying).
    struct phone_food
    {
        const char* name;
        int price;
        int quality;
        int hunger;
        int energy;
        int fun;
        int bladder;
    };

    constexpr int phone_food_count = 4;
    extern const phone_food phone_foods[phone_food_count];
    constexpr int phone_delivery_minutes = 30;
    constexpr int phone_message_count = 8;

    // The phone: a handset that slides up from the bottom right (SELECT while walking). Screens: Contacts (call somebody you have met:
    // a short meet-up line, friendship +1 and Social +2 once a day per person), Messages (texts from the cast, a blinking envelope on
    // the HUD while one is unread) and Order food (pay now, delivered in 30 game minutes wherever you are). Bold 9 px UI font on the
    // Paper / Night panel (ui::set_night before open). Everything it needs from the field goes through `io`.
    class phone
    {

    public:
        struct io
        {
            int day = 1;
            int minutes = 0;
            int money = 0;                      // in: current money; out: money after an order
            uint16_t msg_seen = 0;              // in / out
            uint16_t msg_read = 0;              // in / out
            uint8_t call_day[8] = {};           // in / out: day (mod 256) of the last call to each NPC (talk slots)
            bool can_order = true;              // false while an earlier order is still on its way
            int order = -1;                     // out: phone_foods index ordered now, -1 = none
        };

        void open(const io& data);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return _state != state::closed;
        }

        // Runs the phone for one frame; true once it has slid back down (data() then holds the results).
        [[nodiscard]] bool update();

        [[nodiscard]] const io& data() const
        {
            return _io;
        }

        // New messages whose conditions hold now (called every game minute by the field): marks them seen, returns how many arrived.
        static int deliver(uint16_t& seen, int day, int minutes, int debt);

        [[nodiscard]] static bool has_unread(uint16_t seen, uint16_t read)
        {
            return (seen & ~read) != 0;
        }

    private:
        enum class state : uint8_t
        {
            closed,
            sliding_in,
            home,
            contacts,
            call,
            messages,
            message_view,
            food,
            food_confirm,
            ordered,
            sliding_out
        };

        static constexpr int rows_visible = 6;

        io _io;
        state _state = state::closed;
        int _slide = 0;
        int _sel = 0;
        int _top = 0;
        int _count = 0;
        int _arg = 0;
        bn::vector<int, 16> _ids;
        bn::string<24> _row_text[16];
        ui::panel _panel;
        ui::bar _bar;
        ui::label _title;
        ui::label _clock;
        ui::label _rows[rows_visible];
        ui::label _body[8];
        ui::hint_row _hint;
        bool _hint_back = true;

        void _build_panel(int y);
        void _go(state next);
        void _draw_list();
        void _draw_body(const char* text, int first_line, int max_lines);
        void _clear_content();
        void _title_text(const char* text);
        [[nodiscard]] int _contacts_fill();
        [[nodiscard]] int _messages_fill();
        void _make_call();
        void _view_message();
    };
}

#endif
