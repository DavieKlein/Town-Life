#include "tl_phone.h"
#include "tl_audio.h"

#include "bn_keypad.h"

#include "tl_story.h"
#include "tl_story_ids.h"

namespace tl
{
    const phone_food phone_foods[phone_food_count] = {
        { "Pizza slice", 8, 2, 35, 5, 3, 0 },
        { "Burger menu", 10, 3, 50, 10, 5, -3 },
        { "Salad box", 7, 2, 28, 6, 2, 0 },
        { "Iced tea", 5, 2, 0, 12, 4, -8 },
    };

    namespace
    {
        constexpr int phone_x = 124;
        constexpr int phone_y = 4;
        constexpr int phone_w = 112;
        constexpr int phone_h = 120;
        constexpr int title_h = 17;
        constexpr int row_pitch = 14;
        constexpr int slide_frames = 7;
        constexpr int text_x = phone_x + 8;
        constexpr int text_width_px = 96;

        struct message_def
        {
            int npc;                // npc_id index, -1 = VaultTech
            const char* text;
        };

        constexpr message_def messages[phone_message_count] = {
            { int(npc_id::mia), "Morning! Lou is short of hands at the diner. Ask him about work. - Mia" },
            { int(npc_id::lou), "Shift is on! Wash up first, hah! Plates wait for nobody." },
            { int(npc_id::pimm), "The pigeons gather at the pond at four. Bring crumbs, if you have any." },
            { int(npc_id::rosa), "Eat something warm, dear. Old Block looks after its own. - Rosa" },
            { int(npc_id::dex), "Bro. VaultMart pays me in badges. Send help. Or a burger." },
            { -1, "Welcome to Smart City! Your convenience is our priority. Have a nice day." },
            { int(npc_id::okafor), "City Clinic: eat, drink, sleep, wash. Doctor's orders. - Dr. O." },
            { int(npc_id::okafor), "City Clinic: you have an open bill. Pay at the reception desk when you can." },
        };

        [[nodiscard]] bool message_ready(int i, int day, int minutes, int debt)
        {
            story_state& s = story();

            if(minutes < 8 * 60)
            {
                return false;
            }

            switch(i)
            {
            case 0:
                return day >= 2 && s.flag(story_flag::met_mia) && ! s.flag(story_flag::diner_job);
            case 1:
                return s.flag(story_flag::diner_job);
            case 2:
                return day >= 2 && s.flag(story_flag::met_pimm);
            case 3:
                return day >= 2 && s.flag(story_flag::vault_scene) && s.flag(story_flag::met_rosa);
            case 4:
                return day >= 3 && s.flag(story_flag::met_dex);
            case 5:
                return day >= 3;
            case 6:
                return s.flag(story_flag::faint_told);
            default:
                return debt > 0;
            }
        }

        struct contact_def
        {
            int npc;
            int flag;
            const char* morning;
            const char* afternoon;
        };

        const contact_def contacts[] = {
            { int(npc_id::mia), story_flag::met_mia, "I'm at the diner till three. Come by for a coffee!",
              "Fountain bench at noon is my favourite. Join me tomorrow?" },
            { int(npc_id::rosa), story_flag::met_rosa, "Busy with the stall. Eat first, talk later, dear.",
              "Come to Old Block when it opens. There is soup." },
            { int(npc_id::dex), story_flag::met_dex, "Can't talk. Mr. Vault is watching the cameras.",
              "Meet me by the fountain? Not in uniform. Obviously." },
            { int(npc_id::pimm), story_flag::met_pimm, "The library opens at eight. Quiet there. Mostly.",
              "Pond at four. The pigeons expect us." },
            { int(npc_id::lou), story_flag::met_lou, "Pancakes are on! Diner, all day. Hah!",
              "Dinner rush soon. Hungry? Come over, I'll save a stool." },
            { int(npc_id::okafor), story_flag::met_okafor, "Clinic is open from eight. Do not wait until you collapse.",
              "Still open till eight. Eat something, please." },
        };
        constexpr int contacts_total = int(sizeof(contacts) / sizeof(contacts[0]));

        // Word-wraps `text` to `width` pixels into at most `max` lines; returns the line count.
        int wrap(const char* text, int width, bn::string<40>* out, int max)
        {
            int count = 0;
            bn::string<40> line;
            bn::string<24> word;

            auto flush_word = [&]()
            {
                if(word.empty())
                {
                    return;
                }

                bn::string<40> trial = line;

                if(! trial.empty())
                {
                    trial.append(' ');
                }

                trial.append(word);

                if(! line.empty() && ui::text_width(ui::font9, trial) > width)
                {
                    if(count < max)
                    {
                        out[count++] = line;
                    }

                    line = word;
                }
                else
                {
                    line = trial;
                }

                word.clear();
            };

            for(const char* c = text; *c; ++c)
            {
                if(*c == ' ')
                {
                    flush_word();
                }
                else if(word.size() < word.max_size())
                {
                    word.append(*c);
                }
            }

            flush_word();

            if(! line.empty() && count < max)
            {
                out[count++] = line;
            }

            return count;
        }

        [[nodiscard]] bn::string<12> clock_string(int minutes)
        {
            int hours = (minutes / 60) % 24;
            int mins = minutes % 60;
            bn::string<12> text;
            text.append(bn::to_string<4>(hours % 12 == 0 ? 12 : hours % 12));
            text.append(':');

            if(mins < 10)
            {
                text.append('0');
            }

            text.append(bn::to_string<4>(mins));
            text.append(hours >= 12 ? "p" : "a");
            return text;
        }
    }

    int phone::deliver(uint16_t& seen, int day, int minutes, int debt)
    {
        int arrived = 0;

        for(int i = 0; i < phone_message_count; ++i)
        {
            if(! ((seen >> i) & 1) && message_ready(i, day, minutes, debt))
            {
                seen = uint16_t(seen | (1 << i));
                ++arrived;
            }
        }

        return arrived;
    }

    void phone::open(const io& data)
    {
        _io = data;
        _io.order = -1;
        _state = state::sliding_in;
        _slide = 0;
        _sel = 0;
        _top = 0;
        _build_panel(160);
    }

    void phone::close()
    {
        _clear_content();
        _panel.close();
        _hint.close();
        _state = state::closed;
    }

    void phone::_build_panel(int y)
    {
        _panel.close();
        _panel.open(phone_x, y, phone_w, phone_h, true);
    }

    void phone::_clear_content()
    {
        _bar.clear();
        _title.clear();
        _clock.clear();
        _hint.close();

        for(ui::label& label : _rows)
        {
            label.clear();
        }

        for(ui::label& label : _body)
        {
            label.clear();
        }
    }

    void phone::_title_text(const char* text)
    {
        _title.set(ui::font9, phone_x + 7, phone_y + 12, text, ui::role::title);
        _clock.set_right(ui::font9, phone_x + phone_w - 7, phone_y + 12, clock_string(_io.minutes), ui::role::title);
    }

    int phone::_contacts_fill()
    {
        _ids.clear();

        for(int i = 0; i < contacts_total; ++i)
        {
            if(story().flag(contacts[i].flag))
            {
                _row_text[_ids.size()] = npc_infos[contacts[i].npc].name;
                _ids.push_back(i);
            }
        }

        return _ids.size();
    }

    int phone::_messages_fill()
    {
        _ids.clear();

        for(int i = phone_message_count - 1; i >= 0; --i)
        {
            if((_io.msg_seen >> i) & 1)
            {
                bn::string<24> row;
                row.append(((_io.msg_read >> i) & 1) ? "  " : "* ");
                row.append(messages[i].npc < 0 ? "VaultTech" : npc_infos[messages[i].npc].name);
                _row_text[_ids.size()] = row;
                _ids.push_back(i);
            }
        }

        return _ids.size();
    }

    void phone::_go(state next)
    {
        int keep_home = (_state == state::home) ? _sel : -1;
        _clear_content();
        _state = next;
        _sel = 0;
        _top = 0;
        _hint_back = true;
        (void)keep_home;

        switch(next)
        {
        case state::home:
            {
                _title_text("Phone");
                _count = 4;
                _row_text[0] = "Contacts";
                _row_text[1] = "Messages";

                if(has_unread(_io.msg_seen, _io.msg_read))
                {
                    int unread = 0;

                    for(int i = 0; i < phone_message_count; ++i)
                    {
                        unread += (((_io.msg_seen & ~_io.msg_read) >> i) & 1);
                    }

                    _row_text[1].append(" (");
                    _row_text[1].append(bn::to_string<4>(unread));
                    _row_text[1].append(")");
                }

                _row_text[2] = "Order food";
                _row_text[3] = "Close";
                _sel = _arg;
                _hint.open(phone_x + 7, phone_y + phone_h - 17, false, "OK");
                _draw_list();
            }
            break;

        case state::contacts:
            _title_text("Contacts");
            _count = _contacts_fill();
            _hint.open(phone_x + 7, phone_y + phone_h - 17, true, "Call");
            _draw_list();
            break;

        case state::messages:
            _title_text("Messages");
            _count = _messages_fill();
            _hint.open(phone_x + 7, phone_y + phone_h - 17, true, "Read");
            _draw_list();
            break;

        case state::food:
            {
                _title_text("Order food");
                _count = phone_food_count;

                for(int i = 0; i < phone_food_count; ++i)
                {
                    _row_text[i] = phone_foods[i].name;
                    _row_text[i].append(" $");
                    _row_text[i].append(bn::to_string<6>(phone_foods[i].price));
                }

                _hint.open(phone_x + 7, phone_y + phone_h - 17, true, "Pick");
                _draw_list();
            }
            break;

        default:
            break;
        }
    }

    void phone::_draw_list()
    {
        int top = phone_y + title_h;

        for(int row = 0; row < rows_visible; ++row)
        {
            int index = _top + row;

            if(index < _count)
            {
                _rows[row].set(ui::font9, phone_x + 17, top + 2 + (row * row_pitch) + 10, _row_text[index],
                               index == _sel ? ui::role::selected : ui::role::text);
            }
            else
            {
                _rows[row].clear();
            }
        }

        if(_count > 0)
        {
            _bar.set(phone_x + 5, top + 2 + ((_sel - _top) * row_pitch), phone_w - 10);
        }
        else
        {
            _bar.clear();
            _body[0].set(ui::font9, text_x, top + 14, "Nobody yet.", ui::role::text);
        }
    }

    void phone::_draw_body(const char* text, int first_line, int max_lines)
    {
        bn::string<40> lines[8];
        int count = wrap(text, text_width_px, lines, max_lines);

        for(int i = 0; i < count && first_line + i < 8; ++i)
        {
            _body[first_line + i].set(ui::font9, text_x, phone_y + title_h + 11 + ((first_line + i) * 11), lines[i], ui::role::text);
        }
    }

    void phone::_make_call()
    {
        const contact_def& c = contacts[_ids[_sel]];
        story_state& s = story();
        bool morning = _io.minutes < 13 * 60;
        _clear_content();
        _state = state::call;
        _title_text("Calling...");
        bn::string<24> name(npc_infos[c.npc].name);
        _body[0].set(ui::font9, text_x, phone_y + title_h + 11, name, ui::role::money);
        _draw_body(morning ? c.morning : c.afternoon, 1, 4);
        int slot = c.npc;
        bool first = slot >= 8 || _io.call_day[slot] != uint8_t(_io.day);
        bn::string<40> result;
        bn::string<40> result2;

        if(first)
        {
            if(slot < 8)
            {
                _io.call_day[slot] = uint8_t(_io.day);
            }

            s.add_friendship(c.npc, 1);
            s.add_social(2);
            result = "Friendship +1";
            result2 = "Social +2";
        }
        else
        {
            result = "You called already";
            result2 = "today.";
        }

        _body[5].set(ui::font9, text_x, phone_y + title_h + 11 + (5 * 11), result, ui::role::hint);
        _body[6].set(ui::font9, text_x, phone_y + title_h + 11 + (6 * 11), result2, ui::role::hint);
        _hint.open(phone_x + 7, phone_y + phone_h - 17, false, "OK");
    }

    void phone::_view_message()
    {
        int i = _ids[_sel];
        _io.msg_read = uint16_t(_io.msg_read | (1 << i));
        _clear_content();
        _state = state::message_view;
        _title_text("Message");
        bn::string<24> from(messages[i].npc < 0 ? "VaultTech" : npc_infos[messages[i].npc].name);
        _body[0].set(ui::font9, text_x, phone_y + title_h + 11, from, ui::role::money);
        _draw_body(messages[i].text, 1, 7);
        _hint.open(phone_x + 7, phone_y + phone_h - 17, false, "OK");
    }

    bool phone::update()
    {
        switch(_state)
        {

        case state::closed:
            return true;

        case state::sliding_in:
            {
                ++_slide;
                int t = _slide * 256 / slide_frames;
                int ease = 256 - (((256 - t) * (256 - t)) >> 8);        // fast start, soft landing
                _build_panel(160 + (((phone_y - 160) * ease) >> 8));

                if(_slide >= slide_frames)
                {
                    _build_panel(phone_y);
                    _arg = 0;
                    _go(state::home);
                }
            }
            break;

        case state::sliding_out:
            {
                ++_slide;
                int t = _slide * 256 / slide_frames;
                _build_panel(phone_y + (((160 - phone_y) * ((t * t) >> 8)) >> 8));

                if(_slide >= slide_frames)
                {
                    close();
                    return true;
                }
            }
            break;

        case state::home:
        case state::contacts:
        case state::messages:
        case state::food:
            {
                bool moved = false;

                if(bn::keypad::up_pressed() && _sel > 0)
                {
                    --_sel;
                    moved = true;
                    audio::play(audio::sfx::blip);
                }
                else if(bn::keypad::down_pressed() && _sel < _count - 1)
                {
                    ++_sel;
                    moved = true;
                    audio::play(audio::sfx::blip);
                }

                if(moved)
                {
                    if(_sel < _top)
                    {
                        _top = _sel;
                    }
                    else if(_sel >= _top + rows_visible)
                    {
                        _top = _sel - rows_visible + 1;
                    }

                    _draw_list();
                }

                bool back = bn::keypad::b_pressed() || bn::keypad::select_pressed();

                if(back || bn::keypad::a_pressed())
                {
                    audio::play(back ? audio::sfx::back : audio::sfx::confirm);
                }

                if(_state == state::home)
                {
                    if(back || (bn::keypad::a_pressed() && _sel == 3))
                    {
                        _clear_content();
                        _state = state::sliding_out;
                        _slide = 0;
                    }
                    else if(bn::keypad::a_pressed())
                    {
                        _arg = _sel;
                        _go(_sel == 0 ? state::contacts : (_sel == 1 ? state::messages : state::food));
                    }
                }
                else if(back)
                {
                    _arg = _state == state::contacts ? 0 : (_state == state::messages ? 1 : 2);
                    _go(state::home);
                }
                else if(bn::keypad::a_pressed() && _count > 0)
                {
                    if(_state == state::contacts)
                    {
                        _make_call();
                    }
                    else if(_state == state::messages)
                    {
                        _view_message();
                    }
                    else
                    {
                        // food: confirmation page
                        int item = _sel;
                        _arg = item;
                        _clear_content();
                        _state = state::food_confirm;
                        _title_text("Order food");
                        const phone_food& f = phone_foods[item];
                        bn::string<32> name(f.name);
                        name.append(" $");
                        name.append(bn::to_string<6>(f.price));
                        _body[0].set(ui::font9, text_x, phone_y + title_h + 11, name, ui::role::money);

                        if(! _io.can_order)
                        {
                            _draw_body("You ordered already. Wait for the delivery.", 1, 5);
                        }
                        else if(_io.money < f.price)
                        {
                            _draw_body("Not enough money.", 1, 5);
                        }
                        else
                        {
                            _draw_body("Pay now. It arrives in 30 minutes, right where you stand.", 1, 6);
                        }

                        _hint.open(phone_x + 7, phone_y + phone_h - 17, true, (_io.can_order && _io.money >= f.price) ? "Order" : "OK");
                    }
                }
            }
            break;

        case state::call:
        case state::message_view:
            if(bn::keypad::a_pressed() || bn::keypad::b_pressed())
            {
                bool call = _state == state::call;
                _go(call ? state::contacts : state::messages);
            }
            break;

        case state::ordered:
            if(bn::keypad::a_pressed() || bn::keypad::b_pressed())
            {
                _clear_content();
                _state = state::sliding_out;
                _slide = 0;
            }
            break;

        case state::food_confirm:
            {
                const phone_food& f = phone_foods[_arg];
                bool ok = _io.can_order && _io.money >= f.price;

                if(bn::keypad::a_pressed() && ok)
                {
                    _io.money -= f.price;
                    _io.order = _arg;
                    _io.can_order = false;
                    _clear_content();
                    _state = state::ordered;
                    _title_text("Ordered!");
                    _draw_body("Thank you! Your food is on its way (30 minutes).", 0, 6);
                    _hint.open(phone_x + 7, phone_y + phone_h - 17, false, "OK");
                    _arg = 0;
                    _count = 0;
                }
                else if(bn::keypad::b_pressed() || bn::keypad::a_pressed())
                {
                    _go(state::food);
                }
            }
            break;
        default:
            break;
        }

        return false;
    }
}
