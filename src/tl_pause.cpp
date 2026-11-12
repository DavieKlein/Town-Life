#include "tl_pause.h"

#include "bn_keypad.h"
#include "tl_story.h"
#include "bn_string.h"
#include "bn_sprite_items_need_bar.h"
#include "bn_sprite_items_collect_icons.h"

#include "tl_cast_data.h"
#include "tl_collect_spots.h"

namespace tl
{
    namespace
    {
        constexpr bn::string_view need_names[] = { "Hunger", "Energy", "Hygiene", "Fun", "Bladder", "Social" };
        constexpr bn::string_view pause_options[] = { "Resume", "Mission log", "Collection", "Save game", "Quit to title" };

        constexpr int dialog_w = 212;
        constexpr int dialog_x = (240 - dialog_w) / 2;
        constexpr int bar_levels = 16;      // frames of need_bar.bmp

        [[nodiscard]] bn::string<16> clock_text(int total_minutes)
        {
            int hours = (total_minutes / 60) % 24;
            int minutes = total_minutes % 60;
            bn::string<16> text;
            text.append(bn::to_string<4>(hours % 12 == 0 ? 12 : hours % 12));
            text.append(':');

            if(minutes < 10)
            {
                text.append('0');
            }

            text.append(bn::to_string<4>(minutes));
            text.append(hours >= 12 ? " pm" : " am");
            return text;
        }
    }

    // ---------------------------------------------------------------------------------------------------------

    void dialog::open(const bn::string_view& title, const bn::string_view* lines, int lines_count,
                      const bn::string_view* options, int options_count, int top)
    {
        close();
        _options = options;
        _options_count = options_count;
        _selected = 0;
        int height = 17 + 12 + ((lines_count - 1) * 11) + 8 + (options_count * 15) + 4;

        if(options_count == 1)
        {
            height += 15;       // room for the hint row instead of a second option
        }

        if(top < 0)
        {
            top = (128 - height) / 2;
        }

        _panel.open(dialog_x, top, dialog_w, height, true);
        _title.set(ui::font9, dialog_x + 7, top + 12, title, ui::role::title);
        _lines.clear();

        for(int index = 0; index < lines_count; ++index)
        {
            _lines.emplace_back();
            _lines.back().set(ui::font9, dialog_x + 8, top + 17 + 12 + (index * 11), lines[index], ui::role::text);
        }

        _options_y = top + 17 + 12 + ((lines_count - 1) * 11) + 8;
        _option_labels.clear();

        for(int index = 0; index < options_count; ++index)
        {
            _option_labels.emplace_back();
        }

        _hint.open(dialog_x + dialog_w - 100, top + height - 17, options_count > 1);
        _draw_options();
    }

    void dialog::_draw_options()
    {
        for(int index = 0; index < _options_count; ++index)
        {
            _option_labels[index].set(ui::font9, dialog_x + 8 + 12, _options_y + (index * 15) + 10, _options[index],
                                      index == _selected ? ui::role::selected : ui::role::text);
        }

        _bar.set(dialog_x + 8, _options_y + (_selected * 15), 90);
    }

    void dialog::close()
    {
        _panel.close();
        _bar.clear();
        _title.clear();
        _lines.clear();
        _option_labels.clear();
        _hint.close();
    }

    int dialog::update()
    {
        if(! is_open())
        {
            return cancelled;
        }

        if(bn::keypad::up_pressed() && _selected > 0)
        {
            --_selected;
            _draw_options();
        }
        else if(bn::keypad::down_pressed() && _selected < _options_count - 1)
        {
            ++_selected;
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

    // ---------------------------------------------------------------------------------------------------------

    void pause_screen::open(const pause_info& info)
    {
        close();
        _selected = 0;
        _panel.open(4, 4, 232, 120, false);
        _labels.clear();

        auto add = [&](const ui::font_data& font, int x, int baseline, const bn::string_view& text, ui::role r)
        {
            _labels.emplace_back();
            _labels.back().set(font, x, baseline, text, r);
        };

        bn::string<24> day((info.sick || info.debt > 0) ? weekday_short(info.day) : weekday_name(info.day));
        day.append(", day ");
        day.append(bn::to_string<8>(info.day));
        add(ui::font11, 12, 21, day, ui::role::text);
        add(ui::font9, 12 + ui::text_width(ui::font11, day) + 8, 20, clock_text(info.minutes), ui::role::text);
        bn::string<16> money("$");
        money.append(bn::to_string<12>(info.money));
        _labels.emplace_back();
        _labels.back().set_right(ui::font11, 228, 21, money, ui::role::money);

        if(info.sick || info.debt > 0 || info.great)
        {
            bn::string<16> status("Owe $");

            if(info.sick)
            {
                status = "SICK";
            }
            else if(info.debt <= 0)
            {
                status = "GREAT!";
            }
            else
            {
                status.append(bn::to_string<8>(info.debt));
            }

            add(ui::font9, 12 + ui::text_width(ui::font11, day) + 8 + ui::text_width(ui::font9, clock_text(info.minutes)) + 8, 20, status, ui::role::money);
        }

        for(int need = 0; need < 6; ++need)
        {
            int row = 31 + (need * 11);
            int value = need < 5 ? info.need_values[need] : info.social;
            add(ui::font9, 12, row + 8, need_names[need], ui::role::text);
            _labels.emplace_back();
            _labels.back().set_right(ui::font9, 128, row + 8, bn::to_string<8>(value),
                                     ui::role::text);
            int level = value * (bar_levels - 1) / 100;
            bn::sprite_ptr bar = bn::sprite_items::need_bar.create_sprite(70 + 16 - 120, row + 1 + 4 - 80, level);
            bar.set_bg_priority(0);
            _bars.push_back(bn::move(bar));
        }

        // objective, wrapped at the panel width (up to 2 lines)
        bn::string_view objective(info.objective);
        bn::string<64> goal("Goal: ");
        goal.append(objective);
        bn::string_view text(goal);
        int lines_used = 0;
        int pos = 0;
        int length = text.size();

        for(int line = 0; line < 2 && pos < length; ++line)
        {
            int end = length;

            while(end > pos + 1 && ui::text_width(ui::font9, text.substr(pos, end - pos)) > 214)
            {
                --end;
            }

            if(end < length)
            {
                int cut = end;

                while(cut > pos && text[cut] != ' ')
                {
                    --cut;
                }

                if(cut > pos)
                {
                    end = cut;
                }
            }

            add(ui::font9, 12, 104 + (line * 10), text.substr(pos, end - pos), ui::role::hint);
            lines_used = line + 1;
            pos = end;

            while(pos < length && text[pos] == ' ')
            {
                ++pos;
            }
        }

        if(lines_used < 2)
        {
            bn::string<32> bag("Bag ");
            bag.append(bn::to_string<8>(info.bag));
            bag.append("/10   Coins ");
            bag.append(bn::to_string<8>(info.coins));

            if(info.debt > 0)
            {
                bag.append(" Owe $");
                bag.append(bn::to_string<8>(info.debt));
            }

            add(ui::font9, 12, 116, bag, ui::role::hint);
        }

        _draw_options();
    }

    void pause_screen::_draw_options()
    {
        for(int option = 0; option < options_count; ++option)
        {
            _option_labels[option].set(ui::font9, 138 + 12, 28 + (option * 14) + 10, pause_options[option],
                                       option == _selected ? ui::role::selected : ui::role::text);
        }

        _bar.set(138, 28 + (_selected * 14), 92);
    }

    void pause_screen::close()
    {
        _panel.close();
        _bar.clear();
        _labels.clear();
        _bars.clear();
        _hint.close();

        for(ui::label& label : _option_labels)
        {
            label.clear();
        }
    }

    int pause_screen::update()
    {
        if(! is_open())
        {
            return resume;
        }

        if(bn::keypad::up_pressed() && _selected > 0)
        {
            --_selected;
            _draw_options();
        }
        else if(bn::keypad::down_pressed() && _selected < options_count - 1)
        {
            ++_selected;
            _draw_options();
        }

        if(bn::keypad::a_pressed())
        {
            return _selected;
        }

        if(bn::keypad::b_pressed() || bn::keypad::start_pressed())
        {
            return resume;
        }

        return open_still;
    }

    // ---------------------------------------------------------------------------------------------------------

    void log_screen::open(const log_info& info)
    {
        close();
        _info = info;
        _scroll = 0;
        _panel.open(4, 4, 232, 120, false);
        _labels.emplace_back();
        _labels.back().set(ui::font11, 12, 21, "Mission log", ui::role::text);
        bn::string<24> coins("City Coins ");
        coins.append(bn::to_string<8>(info.coins));
        _labels.emplace_back();
        _labels.back().set_right(ui::font9, 228, 20, coins, ui::role::money);

        // current mission: title and the objective wrapped to two lines
        bn::string<48> now("Now: ");
        now.append(info.current_title[0] ? info.current_title : "Explore the city");
        _labels.emplace_back();
        _labels.back().set(ui::font9, 12, 36, now, ui::role::text);
        bn::string_view text(info.current_objective);
        int pos = 0;
        int length = text.size();

        for(int line = 0; line < 2 && pos < length; ++line)
        {
            int end = length;

            while(end > pos + 1 && ui::text_width(ui::font9, text.substr(pos, end - pos)) > 212)
            {
                --end;
            }

            if(end < length)
            {
                int cut = end;

                while(cut > pos && text[cut] != ' ')
                {
                    --cut;
                }

                if(cut > pos)
                {
                    end = cut;
                }
            }

            _labels.emplace_back();
            _labels.back().set(ui::font9, 12, 47 + (line * 10), text.substr(pos, end - pos), ui::role::hint);
            pos = end;

            while(pos < length && text[pos] == ' ')
            {
                ++pos;
            }
        }

        bn::string<24> done("Done (");
        done.append(bn::to_string<8>(info.done_count));
        done.append(")");
        _labels.emplace_back();
        _labels.back().set(ui::font9, 12, 74, done, ui::role::text);

        for(int index = 0; index < visible_rows; ++index)
        {
            _rows.emplace_back();
        }

        _draw_rows();
        _hint.open(142, 108, false, "Back");
    }

    void log_screen::_draw_rows()
    {
        for(int index = 0; index < visible_rows; ++index)
        {
            int entry = _scroll + index;

            if(entry < _info.done_count)
            {
                bn::string<40> row("- ");
                row.append(_info.done_titles[entry]);
                _rows[index].set(ui::font9, 16, 85 + (index * 10), row, ui::role::hint);
            }
            else
            {
                _rows[index].clear();
            }
        }
    }

    void log_screen::close()
    {
        _panel.close();
        _labels.clear();
        _rows.clear();
        _hint.close();
    }

    bool log_screen::update()
    {
        if(! is_open())
        {
            return true;
        }

        if(bn::keypad::up_pressed() && _scroll > 0)
        {
            --_scroll;
            _draw_rows();
        }
        else if(bn::keypad::down_pressed() && _scroll + visible_rows < _info.done_count)
        {
            ++_scroll;
            _draw_rows();
        }

        if(bn::keypad::a_pressed() || bn::keypad::b_pressed() || bn::keypad::start_pressed())
        {
            close();
            return true;
        }

        return false;
    }

    // ---------------------------------------------------------------------------------------------------------

    void collection_screen::open(uint16_t mask, uint8_t paid)
    {
        close();
        _mask = mask;
        _paid = paid;
        _set = 0;
        _item = 0;
        _panel.open(4, 4, 232, 120, false);
        _hint.open(190, 104, false, "OK");
        _draw();
    }

    void collection_screen::_draw()
    {
        _labels.clear();
        _icons.clear();
        const collect_set& set = collect_sets[_set];
        int found = 0;

        for(int item = 0; item < 4; ++item)
        {
            found += (_mask >> ((_set * 4) + item)) & 1;
        }

        auto add = [&](const ui::font_data& font, int x, int baseline, const bn::string_view& text, ui::role r, bool right = false)
        {
            _labels.emplace_back();

            if(right)
            {
                _labels.back().set_right(font, x, baseline, text, r);
            }
            else
            {
                _labels.back().set(font, x, baseline, text, r);
            }
        };

        add(ui::font11, 12, 21, "Collection", ui::role::text);
        bn::string<32> page("< ");
        page.append(bn::to_string<4>(_set + 1));
        page.append("/3 >");
        add(ui::font9, 228, 20, page, ui::role::hint, true);
        bn::string<40> title(set.name);
        title.append("  ");
        title.append(bn::to_string<4>(found));
        title.append("/4");
        add(ui::font9, 12, 38, title, ui::role::text);

        for(int item = 0; item < 4; ++item)
        {
            bool have = (_mask >> ((_set * 4) + item)) & 1;
            bn::sprite_ptr icon = bn::sprite_items::collect_icons.create_sprite(32 + (item * 48) + 16 - 120, 44 + 16 - 80,
                                                                                have ? (_set * 4) + item : 12);
            icon.set_bg_priority(0);
            icon.set_z_order(-5);
            _icons.push_back(bn::move(icon));
        }

        add(ui::font9, 32 + (_item * 48) + 12, 87, "^", ui::role::text);
        _bar.set(10, 90, 130);
        bool have = (_mask >> ((_set * 4) + _item)) & 1;
        bn::string<40> name(have ? collect_item_names[(_set * 4) + _item] : "???");
        add(ui::font9, 10 + 17, 90 + 10, name, ui::role::selected);

        if((_paid >> _set) & 1)
        {
            add(ui::font9, 12, 114, "Set complete. Reward collected.", ui::role::hint);
        }
        else
        {
            bn::string<48> reward("Reward: $");
            reward.append(bn::to_string<6>(set.money));

            if(set.coins)
            {
                reward.append(" + City Coin");
            }

            reward.append(" + ");
            reward.append(npc_infos[set.friend_npc].name);
            add(ui::font9, 12, 114, reward, ui::role::hint);
        }
    }

    void collection_screen::close()
    {
        _panel.close();
        _labels.clear();
        _icons.clear();
        _bar.clear();
        _hint.close();
    }

    bool collection_screen::update()
    {
        if(! is_open())
        {
            return true;
        }

        if(bn::keypad::left_pressed())
        {
            _set = (_set + 2) % 3;
            _draw();
        }
        else if(bn::keypad::right_pressed())
        {
            _set = (_set + 1) % 3;
            _draw();
        }
        else if(bn::keypad::up_pressed() && _item > 0)
        {
            --_item;
            _draw();
        }
        else if(bn::keypad::down_pressed() && _item < 3)
        {
            ++_item;
            _draw();
        }

        if(bn::keypad::a_pressed() || bn::keypad::b_pressed() || bn::keypad::start_pressed())
        {
            close();
            return true;
        }

        return false;
    }
}
