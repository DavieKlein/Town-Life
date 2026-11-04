#include "tl_name_entry.h"

#include "bn_core.h"
#include "bn_keypad.h"
#include "bn_string.h"
#include "bn_vector.h"
#include "bn_sprite_items_ui_key.h"

#include "tl_ui.h"
#include "tl_pause.h"
#include "tl_story.h"

namespace tl
{
    namespace
    {
        constexpr int max_name = story_state::name_max;
        constexpr int cell = 18;
        constexpr int grid_x = 39;
        constexpr int grid_y = 50;
        constexpr int row_pitch = 17;
        constexpr int rows = 4;

        // Row 3 is Space (3 cells), Del (2 cells), OK (2 cells); rows 0-2 are the 26 letters.
        constexpr int row_cells[rows] = { 9, 9, 8, 7 };

        struct key
        {
            int row;
            int first;      // first cell
            int cells;
            char letter;    // 'A'..'Z', or ' ', '<' (delete), '=' (OK)
        };

        constexpr int keys_count = 26 + 3;

        void build_keys(key* keys)
        {
            int count = 0;

            for(int index = 0; index < 26; ++index)
            {
                int row = index < 9 ? 0 : (index < 18 ? 1 : 2);
                int first = row == 0 ? 0 : (row == 1 ? 9 : 18);
                keys[count++] = { row, index - first, 1, char('A' + index) };
            }

            keys[count++] = { 3, 0, 3, ' ' };
            keys[count++] = { 3, 3, 2, '<' };
            keys[count++] = { 3, 5, 2, '=' };
        }

        [[nodiscard]] int key_x(const key& k)
        {
            int row_width = row_cells[k.row] * cell;
            int left = grid_x + ((9 * cell) - row_width) / 2;
            return left + (k.first * cell);
        }

        [[nodiscard]] int key_y(const key& k)
        {
            return grid_y + (k.row * row_pitch);
        }
    }

    void run_name_entry(char* out)
    {
        ui::set_night(true);
        key keys[keys_count];
        build_keys(keys);

        bn::string<12> name("Sam");
        bool shift = false;         // false = capital next (start of a name), manual toggle with SELECT
        bool capital_next = false;
        int selected = 0;
        bool lower_forced = false;

        ui::panel panel;
        ui::label title;
        ui::label name_label;
        ui::label hint_text;
        bn::vector<ui::label, keys_count> key_labels;
        bn::vector<bn::sprite_ptr, 4> key_bg;
        ui::hint_row hint;
        dialog confirm;
        bool confirming = false;
        (void)shift;
        (void)lower_forced;

        auto uppercase_now = [&]()
        {
            return capital_next || name.empty() || name.back() == ' ';
        };

        auto draw_name = [&]()
        {
            bn::string<16> text(name);
            text.append('_');
            name_label.set_centre(ui::font11, 120, 42, text, ui::role::hud_money);
        };

        auto draw_keys = [&]()
        {
            bool upper = uppercase_now();
            key_bg.clear();
            key_labels.clear();

            for(int index = 0; index < keys_count; ++index)
            {
                const key& k = keys[index];
                int x = key_x(k);
                int y = key_y(k);
                bool is_sel = index == selected;

                if(is_sel)
                {
                    for(int c = 0; c < k.cells; ++c)
                    {
                        key_bg.push_back(ui::make_piece(bn::sprite_items::ui_key, x + (c * cell) + 1, y, 0, false, 11));
                    }
                }

                bn::string<8> text;

                if(k.letter >= 'A' && k.letter <= 'Z')
                {
                    text.push_back(upper ? k.letter : char(k.letter + 32));
                }
                else if(k.letter == ' ')
                {
                    text = "Space";
                }
                else if(k.letter == '<')
                {
                    text = "Del";
                }
                else
                {
                    text = "OK";
                }

                key_labels.emplace_back();
                key_labels.back().set_centre(ui::font9, x + 1 + ((k.cells * cell) - 2) / 2, y + 11, text,
                                             is_sel ? ui::role::selected : ui::role::text);
            }
        };

        auto move = [&](int dx, int dy)
        {
            const key& cur = keys[selected];
            int row = cur.row + dy;
            row = row < 0 ? 0 : (row >= rows ? rows - 1 : row);
            int cx = cur.first + (cur.cells / 2);      // centre cell of the current key

            if(dx)
            {
                // next / previous key in the row
                int best = selected;

                for(int index = 0; index < keys_count; ++index)
                {
                    if(keys[index].row == cur.row)
                    {
                        if(dx > 0 && keys[index].first == cur.first + cur.cells)
                        {
                            best = index;
                        }
                        else if(dx < 0 && keys[index].first + keys[index].cells == cur.first)
                        {
                            best = index;
                        }
                    }
                }

                selected = best;
                return;
            }

            if(row == cur.row)
            {
                return;
            }

            // same visual column in the other row
            int cur_x = key_x(cur) + ((cur.cells * cell) / 2);
            int best = selected;
            int best_d = 100000;

            for(int index = 0; index < keys_count; ++index)
            {
                if(keys[index].row == row)
                {
                    int kx = key_x(keys[index]) + ((keys[index].cells * cell) / 2);
                    int d = kx > cur_x ? kx - cur_x : cur_x - kx;

                    if(d < best_d)
                    {
                        best_d = d;
                        best = index;
                    }
                }
            }

            (void)cx;
            selected = best;
        };

        panel.open(20, 4, 200, 124 + 20, false);
        title.set_centre(ui::font11, 120, 22, "What is your name?", ui::role::text);
        hint.open(40, 132, true, "Type");
        hint_text.set(ui::font9, 140, 140, "START: done", ui::role::hint);
        draw_name();
        draw_keys();
        bn::core::update();

        static bn::string<24> confirm_line;

        while(true)
        {
            if(confirming)
            {
                int choice = confirm.update();

                if(choice != dialog::open_still)
                {
                    confirming = false;

                    if(choice == 0)
                    {
                        break;
                    }

                    panel.open(20, 4, 200, 144, false);
                    title.set_centre(ui::font11, 120, 22, "What is your name?", ui::role::text);
                    hint.open(40, 132, true, "Type");
                    hint_text.set(ui::font9, 140, 140, "START: done", ui::role::hint);
                    draw_name();
                    draw_keys();
                }

                bn::core::update();
                continue;
            }

            bool changed = false;

            if(bn::keypad::left_pressed())
            {
                move(-1, 0);
                changed = true;
            }
            else if(bn::keypad::right_pressed())
            {
                move(1, 0);
                changed = true;
            }
            else if(bn::keypad::up_pressed())
            {
                move(0, -1);
                changed = true;
            }
            else if(bn::keypad::down_pressed())
            {
                move(0, 1);
                changed = true;
            }

            bool done = bn::keypad::start_pressed();

            if(bn::keypad::select_pressed() || bn::keypad::l_pressed() || bn::keypad::r_pressed())
            {
                capital_next = ! capital_next;
                changed = true;
            }

            if(bn::keypad::b_pressed() && ! name.empty())
            {
                name.pop_back();
                capital_next = false;
                changed = true;
                draw_name();
            }

            if(bn::keypad::a_pressed())
            {
                char letter = keys[selected].letter;

                if(letter >= 'A' && letter <= 'Z')
                {
                    if(name.size() < max_name)
                    {
                        name.push_back(uppercase_now() ? letter : char(letter + 32));
                        capital_next = false;
                    }

                    changed = true;
                    draw_name();
                }
                else if(letter == ' ')
                {
                    if(! name.empty() && name.back() != ' ' && name.size() < max_name)
                    {
                        name.push_back(' ');
                        changed = true;
                        draw_name();
                    }
                }
                else if(letter == '<')
                {
                    if(! name.empty())
                    {
                        name.pop_back();
                        capital_next = false;
                        changed = true;
                        draw_name();
                    }
                }
                else
                {
                    done = true;
                }
            }

            if(done && ! name.empty())
            {
                static constexpr bn::string_view yes_no[] = { "Yes", "No" };
                confirm_line = name;
                confirm_line.append("? Is that right?");
                static bn::string_view lines[1];
                lines[0] = confirm_line;
                panel.close();
                title.clear();
                name_label.clear();
                hint_text.clear();
                key_labels.clear();
                key_bg.clear();
                hint.close();
                confirm.open("Your name", lines, 1, yes_no, 2, 40);
                confirming = true;
            }
            else if(changed)
            {
                draw_keys();
            }

            bn::core::update();
        }

        for(int index = 0; index < 12; ++index)
        {
            out[index] = index < name.size() ? name[index] : 0;
        }

        out[11] = 0;
    }
}
