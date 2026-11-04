#include "tl_minigame.h"

#include "bn_core.h"
#include "bn_color.h"
#include "bn_fixed.h"
#include "bn_keypad.h"
#include "bn_random.h"
#include "bn_string.h"
#include "bn_vector.h"
#include "bn_optional.h"
#include "bn_blending.h"
#include "bn_bg_palettes.h"
#include "bn_regular_bg_ptr.h"
#include "bn_sprite_ptr.h"
#include "bn_sprite_palettes.h"
#include "bn_regular_bg_items_mg_stock_bg.h"
#include "bn_regular_bg_items_mg_dish_bg.h"
#include "bn_sprite_items_mg_items.h"
#include "bn_sprite_items_mg_fx.h"
#include "bn_sprite_items_mg_plate.h"
#include "bn_sprite_items_mg_pan.h"
#include "bn_sprite_items_mg_rack.h"
#include "bn_sprite_items_mg_vline.h"
#include "bn_sprite_items_mg_hline.h"
#include "bn_sprite_items_mg_cover_dish.h"
#include "bn_sprite_items_player_wash.h"
#include "bn_sprite_items_shadow.h"

#include "tl_ui.h"
#include "tl_dialogue.h"
#include "tl_lighting.h"
#include "tl_cast_data.h"

namespace tl
{
    namespace
    {
        // ------------------------------------------------------------------------------------------------ helpers
        void apply_fade(bn::fixed fade, bn::fixed dim)
        {
            bn::bg_palettes::set_fade(bn::color(0, 0, 0), fade + (dim * (1 - fade)));
            bn::sprite_palettes::set_fade(bn::color(0, 0, 0), fade);
        }

        void fade_in(bn::fixed dim)
        {
            for(int frame = 12; frame >= 0; --frame)
            {
                apply_fade(bn::fixed(frame) / 12, dim);
                bn::core::update();
            }
        }

        void fade_out(bn::fixed dim)
        {
            for(int frame = 0; frame <= 12; ++frame)
            {
                apply_fade(bn::fixed(frame) / 12, dim);
                bn::core::update();
            }
        }

        // Positions a sprite by its top-left corner in screen pixels.
        void put(bn::sprite_ptr& sprite, int left, int top, int width = 16, int height = 16)
        {
            sprite.set_position(left + (width / 2) - 120, top + (height / 2) - 80);
        }

        struct input
        {
            bool a = false;
            bool b = false;
            bool up = false;
            bool left = false;
            bool right = false;
        };

        [[nodiscard]] input read_keys()
        {
            input in;
            in.a = bn::keypad::a_pressed();
            in.b = bn::keypad::b_pressed();
            in.up = bn::keypad::up_pressed();
            in.left = bn::keypad::left_pressed();
            in.right = bn::keypad::right_pressed();
            return in;
        }

        [[nodiscard]] bn::string<12> money_text(int amount)
        {
            bn::string<12> text("$");
            text.append(bn::to_string<8>(amount));
            return text;
        }

        // Plays Rosa's / Lou's lines in the dialogue box (portrait + text) until the player has gone through all pages.
        void say(dialogue_box& box, const char* text, int expr = 0)
        {
            box.set_expression(expr);
            box.say(text);

            while(! box.update_text())
            {
                bn::core::update();
            }

            bn::core::update();
        }

        void say_auto(dialogue_box& box, const char* text, int expr, int bot)
        {
            if(! bot)
            {
                say(box, text, expr);
                return;
            }

            box.set_expression(expr);
            box.say(text);

            for(int frame = 0; frame < 150; ++frame)
            {
                (void)box.update_text();
                bn::core::update();
            }
        }

        // Result table row (label left, value right) on a panel.
        struct result_row
        {
            const char* name;
            bn::string<16> value;
            bool gold;
        };

        // One shared title / result screen: panel at the right (the portrait of the dialogue box stands at the left).
        class result_panel
        {

        public:
            void open(const char* title, const result_row* rows, int count)
            {
                constexpr int x = 104;
                constexpr int y = 4;
                constexpr int w = 132;
                int h = 24 + (count * 10) + 10;
                _panel.open(x, y, w, h < 64 ? 64 : h, true);
                _title.set_centre(ui::font9, x + (w / 2), y + 12, title, ui::role::title);

                for(int index = 0; index < count; ++index)
                {
                    int baseline = y + 29 + (index * 10);
                    _names[index].set(ui::font9, x + 9, baseline, rows[index].name, ui::role::text);
                    _values[index].set_right(ui::font9, x + w - 9, baseline, rows[index].value,
                                             rows[index].gold ? ui::role::money : ui::role::text);
                }
            }

            void close()
            {
                _panel.close();
                _title.clear();

                for(int index = 0; index < 7; ++index)
                {
                    _names[index].clear();
                    _values[index].clear();
                }
            }

        private:
            ui::panel _panel;
            ui::label _title;
            ui::label _names[7];
            ui::label _values[7];
        };

        constexpr int stock_columns = 3;

        // ------------------------------------------------------------------------------------------------ STOCK IT!
        constexpr int stock_cx[3] = { 40, 120, 200 };
        constexpr int stock_round_frames = 45 * 60;
        constexpr int shelf_capacity = 8;
        constexpr int shelf_pitch = 80;
        constexpr const char* stock_names[4] = { "MILK", "CANS", "CEREAL", "FRUIT" };
        constexpr const char* stock_item_plural[4] = { "Milk", "Cans", "Cereal", "Fruit" };

        [[nodiscard]] int combo_multiplier(int streak)
        {
            return streak >= 10 ? 4 : (streak >= 6 ? 3 : (streak >= 3 ? 2 : 1));
        }

        class stock_game
        {

        public:
            explicit stock_game(const minigame_request& request) :
                _req(request),
                _bg(bn::regular_bg_items::mg_stock_bg.create_bg(8, 48)),
                _player(bn::sprite_items::player_wash.create_sprite(0, 38, 18)),
                _shadow(bn::sprite_items::shadow.create_sprite(0, 0))
            {
                _shadow.set_blending_enabled(true);
                _shadow.set_z_order(2);
                _player.set_z_order(1);
                _rng.update();

                for(int index = 0; index < 4; ++index)
                {
                    _belt.push_back(bn::sprite_items::mg_items.create_sprite(0, 0, 0));
                    put(_belt.back(), 50 + (index * 22), 143);
                    _belt.back().set_visible(false);
                }

                for(int index = 0; index < 4; ++index)
                {
                    bn::sprite_ptr pip = bn::sprite_items::mg_fx.create_sprite(0, 0, 5);
                    put(pip, 192 + (index * 10), -1);
                    pip.set_visible(false);
                    _pips.push_back(bn::move(pip));
                }

                // selection frame of the shelf: 2 x 2 vertical pieces (8x32) + 3 horizontal pieces (32x8)
                for(int index = 0; index < 4; ++index)
                {
                    _frame.push_back(bn::sprite_items::mg_vline.create_sprite(0, 0));
                }

                for(int index = 0; index < 3; ++index)
                {
                    _frame.push_back(bn::sprite_items::mg_hline.create_sprite(0, 0));
                }
                _carried = bn::sprite_items::mg_items.create_sprite(0, 0, 0);
                _x_mark = bn::sprite_items::mg_fx.create_sprite(0, 0, 0);
                _x_mark->set_visible(false);
                _carried->set_z_order(0);
            }

            minigame_result run()
            {
                minigame_result result;
                fade_in(0);
                int rounds = _req.replay ? 3 : 1;
                int total_score = 0;
                int total_stocked = 0;
                int total_mistakes = 0;
                int best_combo = 0;
                int pay = 0;

                for(int round = 0; round < rounds; ++round)
                {
                    if(round == 0)
                    {
                        _title();
                    }

                    _play();
                    total_score += _score;
                    total_stocked += _stocked;
                    total_mistakes += _mistakes;
                    best_combo = _best_combo > best_combo ? _best_combo : best_combo;
                    pay += 4 + _rank();

                    if(round + 1 < rounds)
                    {
                        _banner.set_centre(ui::font11, 120, 80, "NEXT ROUND!", ui::role::hud_money);

                        for(int frame = 0; frame < 60; ++frame)
                        {
                            bn::core::update();
                        }

                        _banner.clear();
                    }
                }

                // rank of the last round (prologue: single round)
                result.rank = _rank();
                result.score = total_score;
                result.count = total_stocked;
                result.mistakes = total_mistakes;
                result.best_combo = best_combo;
                result.completed = true;
                result.minutes = 90;
                result.pay_preview = _req.replay ? pay : stock_pay_for_rank(result.rank);
                result.wage = _req.replay ? pay : 0;
                _result_screen(result);
                fade_out(0);
                return result;
            }

        private:
            minigame_request _req;
            bn::regular_bg_ptr _bg;
            bn::sprite_ptr _player;
            bn::sprite_ptr _shadow;
            bn::vector<bn::sprite_ptr, 4> _belt;
            bn::vector<bn::sprite_ptr, 4> _pips;
            bn::vector<bn::sprite_ptr, 10> _frame;
            bn::optional<bn::sprite_ptr> _carried;
            bn::optional<bn::sprite_ptr> _x_mark;
            bn::optional<bn::sprite_ptr> _slots[stock_columns][shelf_capacity];
            bn::vector<bn::sprite_ptr, 8> _sparkles;
            ui::label _clock;
            ui::label _score_label;
            ui::label _pay_label;
            ui::label _combo_label;
            ui::label _penalty;
            ui::label _banner;
            ui::label _hint[3];
            ui::panel _hint_panel;
            bn::random _rng;
            int _queue[5] = {};
            int _counts[stock_columns] = {};
            int _col = 1;
            int _x = 120;               // player column centre while sliding
            int _frames_left = stock_round_frames;
            int _score = 0;
            int _stocked = 0;
            int _mistakes = 0;
            int _streak = 0;
            int _best_combo = 0;
            int _hint_timer = 0;
            int _x_timer = 0;
            int _bounce = 0;
            int _hop = 0;
            int _penalty_timer = 0;
            int _banner_timer = 0;
            int _sparkle_timer = 0;
            int _pose_timer = 0;
            int _last_seconds = -1;
            int _last_score = -1;
            int _last_pips = -1;
            int _bot_wait = 0;
            int _bot_target = 0;

            [[nodiscard]] int _rank() const
            {
                int rank = _score >= 1000 ? 3 : (_score >= 700 ? 2 : (_score >= 400 ? 1 : 0));

                if(_mistakes == 0 && _stocked >= 12)
                {
                    rank = 3;
                }

                return rank;
            }

            [[nodiscard]] int _next_item()
            {
                _rng.update();
                int previous = _queue[4];
                int kind = _rng.get_int(stock_columns);

                if(kind == previous && _rng.get_int(3) == 0)
                {
                    kind = (kind + 1) % stock_columns;
                }

                return kind;
            }

            void _draw_queue()
            {
                for(int index = 0; index < 4; ++index)
                {
                    _belt[index].set_tiles(bn::sprite_items::mg_items.tiles_item(), _queue[index + 1]);
                    _belt[index].set_visible(true);
                }

                _carried->set_tiles(bn::sprite_items::mg_items.tiles_item(), _queue[0]);
            }

            void _place_player()
            {
                _player.set_position(_x - 120, 38);
                put(*_carried, _x - 8 + (_bounce ? ((_bounce / 3) % 2 ? 4 : -4) : 0), 72 - (_hop ? 4 : 0));
                put(_shadow, _x - 8, 137, 16, 8);
                int sx = _col * shelf_pitch;
                put(_frame[0], sx + 3, 14, 8, 32);
                put(_frame[1], sx + 3, 46, 8, 32);
                put(_frame[2], sx + 76 - 7, 14, 8, 32);
                put(_frame[3], sx + 76 - 7, 46, 8, 32);
                put(_frame[4], sx + 3, 11, 32, 8);
                put(_frame[5], sx + 35, 11, 32, 8);
                put(_frame[6], sx + 45, 11, 32, 8);
            }

            void _draw_hud(bool force)
            {
                int seconds = (_frames_left + 59) / 60;

                if(force || seconds != _last_seconds)
                {
                    _last_seconds = seconds;
                    bn::string<8> text;
                    text.append(bn::to_string<4>(seconds / 60));
                    text.append(':');

                    if(seconds % 60 < 10)
                    {
                        text.append('0');
                    }

                    text.append(bn::to_string<4>(seconds % 60));
                    _clock.set(ui::font9, 17, 10, text, seconds <= 10 ? ui::role::hud_money : ui::role::hud_clock);
                }

                if(force || _score != _last_score)
                {
                    _last_score = _score;
                    bn::string<20> text("SCORE ");
                    text.append(bn::to_string<8>(_score));
                    _score_label.set(ui::font9, 62, 10, text, ui::role::hud_clock);
                    _pay_label.set(ui::font9, 142, 10, money_text(stock_pay_for_rank(_rank())), ui::role::hud_money);
                }

                int mult = combo_multiplier(_streak);
                int pips = _streak >= 10 ? 4 : (_streak >= 6 ? 3 : (_streak >= 3 ? 2 : (_streak >= 1 ? 1 : 0)));
                int key = (mult * 16) + pips;

                if(force || key != _last_pips)
                {
                    _last_pips = key;
                    bn::string<8> text("x");
                    text.append(bn::to_string<4>(mult));
                    _combo_label.set(ui::font9, 176, 10, text, mult > 1 ? ui::role::hud_money : ui::role::hud_clock);

                    for(int index = 0; index < 4; ++index)
                    {
                        _pips[index].set_visible(index < pips);
                    }
                }
            }

            void _show_hint(int item, int section)
            {
                _hint_panel.open(70, 76, 164, 44, false);
                bn::string<24> line_a(stock_item_plural[item]);
                line_a.append(" go on");
                bn::string<24> line_b("the ");
                line_b.append(stock_names[section]);
                line_b.append(" shelf!");
                _hint[0].set(ui::font9, 78, 88, "ROSA:", ui::role::title);
                _hint[1].set(ui::font9, 118, 88, line_a, ui::role::text);
                _hint[2].set(ui::font9, 78, 100, line_b, ui::role::text);
                _hint_timer = 110;
            }

            void _clear_hint()
            {
                _hint_panel.close();

                for(ui::label& label : _hint)
                {
                    label.clear();
                }
            }

            void _sparkle_section(int section)
            {
                _sparkles.clear();

                for(int index = 0; index < 6; ++index)
                {
                    bn::sprite_ptr s = bn::sprite_items::mg_fx.create_sprite(0, 0, 1);
                    put(s, section * shelf_pitch + 6 + ((index * 29) % 66), 28 + ((index * 17) % 36));
                    _sparkles.push_back(bn::move(s));
                }

                _sparkle_timer = 30;
            }

            void _put_away(int section)
            {
                int item = _queue[0];
                int slot = _counts[section];

                if(item == section)
                {
                    ++_streak;
                    ++_stocked;
                    _best_combo = _streak > _best_combo ? _streak : _best_combo;
                    _score += 10 * combo_multiplier(_streak);
                    int sx = section * shelf_pitch;
                    bn::sprite_ptr s = bn::sprite_items::mg_items.create_sprite(0, 0, item);
                    put(s, sx + 8 + ((slot % 4) * 16), slot < 4 ? 29 : 51);
                    _slots[section][slot] = bn::move(s);
                    ++_counts[section];

                    if(_counts[section] >= shelf_capacity)
                    {
                        _score += 50;
                        _banner.set_centre(ui::font11, 120, 86, "SECTION DONE! +50", ui::role::hud_money);
                        _banner_timer = 70;
                        _sparkle_section(section);

                        for(int index = 0; index < shelf_capacity; ++index)
                        {
                            _slots[section][index].reset();
                        }

                        _counts[section] = 0;
                    }

                    _hop = 5;
                    _pose_timer = 6;
                }
                else
                {
                    ++_mistakes;
                    _streak = 0;
                    _frames_left -= 2 * 60;
                    _x_mark->set_visible(true);
                    put(*_x_mark, section * shelf_pitch + 8 + ((slot % 4) * 16), slot < 4 ? 29 : 51);
                    _x_timer = 40;
                    _bounce = 18;
                    _penalty.set(ui::font9, 40, 24, "-2s", ui::role::hud_money);
                    _penalty_timer = 40;
                    _show_hint(item, item);
                }

                if(item == section)
                {
                    for(int index = 0; index < 4; ++index)
                    {
                        _queue[index] = _queue[index + 1];
                    }

                    _queue[4] = _next_item();
                }

                _draw_queue();
            }

            void _swap()
            {
                int item = _queue[0];
                _queue[0] = _queue[1];
                _queue[1] = item;
                _frames_left -= 2 * 60;
                _penalty.set(ui::font9, 40, 24, "-2s", ui::role::hud_money);
                _penalty_timer = 40;
                _draw_queue();
            }

            [[nodiscard]] input _bot_input()
            {
                input in;

                if(_bot_wait > 0)
                {
                    --_bot_wait;
                    return in;
                }

                int target = _queue[0];

                if(_req.bot == 2 && _rng.get_int(5) == 0)
                {
                    target = _rng.get_int(stock_columns);       // sloppy: every fifth item on any shelf
                }
                else if(_req.bot == 3 && _rng.get_int(2) == 0)
                {
                    target = _rng.get_int(stock_columns);
                }

                if(_bot_target != target && _col == _bot_target)
                {
                    _bot_target = target;
                }

                _bot_target = target;

                if(_col < target)
                {
                    in.right = true;
                    _bot_wait = 4;
                }
                else if(_col > target)
                {
                    in.left = true;
                    _bot_wait = 4;
                }
                else
                {
                    in.a = true;
                    _bot_wait = _req.bot == 1 ? 26 : 40;
                }

                return in;
            }

            void _title()
            {
                apply_fade(0, bn::fixed(0.5));
                ui::set_night(is_night(_req.start_minutes));
                _carried->set_visible(false);
                _player.set_visible(false);
                _shadow.set_visible(false);

                for(bn::sprite_ptr& s : _frame)
                {
                    s.set_visible(false);
                }

                ui::panel banner;
                ui::label banner_title;
                ui::label names[3];
                ui::label help[4];
                bn::vector<bn::sprite_ptr, 3> icons;
                banner.open(112, 4, 124, 52, true);
                banner_title.set_centre(ui::font11, 174, 18, "STOCK IT!", ui::role::title);

                for(int index = 0; index < 3; ++index)
                {
                    bn::sprite_ptr icon = bn::sprite_items::mg_items.create_sprite(0, 0, index);
                    put(icon, 125 + (index * 38), 24);
                    icon.set_bg_priority(0);
                    icon.set_z_order(5);
                    icons.push_back(bn::move(icon));
                    names[index].set_centre(ui::font9, 133 + (index * 38), 50, stock_names[index], ui::role::text);
                }

                help[0].set(ui::font9, 128, 70, "Left / Right: walk", ui::role::hud_clock);
                help[1].set(ui::font9, 128, 82, "A: put item away", ui::role::hud_clock);
                help[2].set(ui::font9, 128, 94, "B: swap (-2 s)", ui::role::hud_clock);

                dialogue_box box;
                box.open(int(npc_id::rosa), false, 0);
                say_auto(box, "Right item, right shelf. Be quick!", 0, _req.bot);
                box.close();
                bn::core::update();
                apply_fade(0, 0);
                _carried->set_visible(true);
                _player.set_visible(true);
                _shadow.set_visible(true);

                for(bn::sprite_ptr& s : _frame)
                {
                    s.set_visible(true);
                }
            }

            void _reset_round()
            {
                for(int section = 0; section < stock_columns; ++section)
                {
                    for(int index = 0; index < shelf_capacity; ++index)
                    {
                        _slots[section][index].reset();
                    }

                    _counts[section] = 0;
                }

                _frames_left = stock_round_frames;
                _score = 0;
                _stocked = 0;
                _mistakes = 0;
                _streak = 0;
                _best_combo = 0;
                _col = 1;
                _x = stock_cx[1];
                _queue[4] = 0;

                for(int index = 0; index < 5; ++index)
                {
                    _queue[index] = _next_item();
                }
            }

            void _play()
            {
                _reset_round();
                _draw_queue();
                _draw_hud(true);
                _place_player();

                while(_frames_left > 0)
                {
                    input in = _req.bot ? _bot_input() : read_keys();

                    if(in.left && _col > 0)
                    {
                        --_col;
                    }

                    if(in.right && _col < stock_columns - 1)
                    {
                        ++_col;
                    }

                    if(in.a)
                    {
                        _put_away(_col);
                    }
                    else if(in.b)
                    {
                        _swap();
                    }

                    // slide the player to the column
                    int target = stock_cx[_col];

                    if(_x < target)
                    {
                        _x += (target - _x) > 8 ? 8 : (target - _x);
                    }
                    else if(_x > target)
                    {
                        _x -= (_x - target) > 8 ? 8 : (_x - target);
                    }

                    _player.set_tiles(bn::sprite_items::player_wash.tiles_item(), _pose_timer > 0 ? 16 : 18);

                    if(_pose_timer > 0)
                    {
                        --_pose_timer;
                    }

                    if(_hop > 0)
                    {
                        --_hop;
                    }

                    if(_bounce > 0)
                    {
                        --_bounce;
                    }

                    if(_x_timer > 0 && --_x_timer == 0)
                    {
                        _x_mark->set_visible(false);
                    }

                    if(_hint_timer > 0 && --_hint_timer == 0)
                    {
                        _clear_hint();
                    }

                    if(_penalty_timer > 0 && --_penalty_timer == 0)
                    {
                        _penalty.clear();
                    }

                    if(_banner_timer > 0 && --_banner_timer == 0)
                    {
                        _banner.clear();
                    }

                    if(_sparkle_timer > 0 && --_sparkle_timer == 0)
                    {
                        _sparkles.clear();
                    }

                    --_frames_left;
                    _draw_hud(false);
                    _place_player();
                    bn::core::update();
                }

                _frames_left = 0;
                _draw_hud(true);
                _clear_hint();
                _penalty.clear();
                _banner.clear();
                _sparkles.clear();
                _x_mark->set_visible(false);
                _banner.set_centre(ui::font11, 120, 86, "TIME!", ui::role::hud_money);

                for(int frame = 0; frame < 50; ++frame)
                {
                    bn::core::update();
                }

                _banner.clear();
            }

            void _result_screen(const minigame_result& result)
            {
                apply_fade(0, bn::fixed(0.55));
                ui::set_night(is_night(_req.start_minutes));
                _carried->set_visible(false);

                for(bn::sprite_ptr& s : _frame)
                {
                    s.set_visible(false);
                }

                static const char* const rank_letters[4] = { "C", "B", "A", "S" };
                result_row rows[6];
                int count = 0;
                bn::string<16> value;

                rows[count++] = { "Stocked", bn::string<16>(bn::to_string<8>(result.count)), false };
                rows[count++] = { "Mistakes", bn::string<16>(bn::to_string<8>(result.mistakes)), false };
                value = "x";
                value.append(bn::to_string<8>(result.best_combo > 0 ? combo_multiplier(result.best_combo) : 1));
                rows[count++] = { "Best combo", value, false };
                rows[count++] = { "Score", bn::string<16>(bn::to_string<8>(result.score)), false };
                rows[count++] = { "Rank", bn::string<16>(rank_letters[result.rank]), true };
                rows[count++] = { "Pay", money_text(result.pay_preview), true };
                result_panel panel;
                panel.open("SHIFT DONE!", rows, count);

                static const char* const rosa_lines[4] = {
                    "Hmm. The shelves are up. Mostly.", "Fair. A bit slow in the middle.", "Not bad, kid. Not bad at all.",
                    "Perfect. Forty years, and I never saw it done so clean." };
                static const int rosa_expr[4] = { 2, 0, 1, 1 };
                dialogue_box box;
                box.open(int(npc_id::rosa), false, 0);
                say_auto(box, rosa_lines[result.rank], rosa_expr[result.rank], _req.bot);
                box.close();
                panel.close();
            }
        };

        // ------------------------------------------------------------------------------------------------ PLATE RUSH
        constexpr int zone_x[3] = { 96, 146, 196 };
        constexpr int zone_left = -15;
        constexpr int zone_right = 14;
        constexpr int plate_y = 100;
        constexpr int rush_count = 8;
        constexpr int max_plates = 4;
        constexpr int start_x = 60;

        struct dish_plate
        {
            bool active = false;
            bool broken = false;
            bool pan = false;
            int stage = 0;              // 0 = needs scrub, 1 = rinse, 2 = stack
            int presses = 0;            // pan: A presses so far
            int timer = 0;              // broken: frames until it disappears
            bn::fixed x = start_x;
            bn::optional<bn::sprite_ptr> sprite;
        };

        class dish_game
        {

        public:
            explicit dish_game(const minigame_request& request) :
                _req(request),
                _bg(bn::regular_bg_items::mg_dish_bg.create_bg(8, 48)),
                _player(bn::sprite_items::player_wash.create_sprite(0, 0, 0)),
                _cover(bn::sprite_items::mg_cover_dish.create_sprite(0, 0))
            {
                put(_player, 6, 50, 32, 64);
                put(_cover, 6, 92, 32, 32);
                _player.set_z_order(2);
                _cover.set_z_order(1);
                _rng.update();

                for(int index = 0; index < 3; ++index)
                {
                    bn::sprite_ptr icon = bn::sprite_items::mg_fx.create_sprite(0, 0, 2);
                    put(icon, 202 + (index * 12), -1);
                    _icons.push_back(bn::move(icon));
                }

                for(int index = 0; index < 5; ++index)
                {
                    bn::sprite_ptr pip = bn::sprite_items::mg_fx.create_sprite(0, 0, 4);
                    pip.set_visible(false);
                    _pips.push_back(bn::move(pip));
                }
            }

            minigame_result run()
            {
                minigame_result result;
                fade_in(0);
                _title();
                _play();
                result = _finish();
                fade_out(0);
                return result;
            }

        private:
            minigame_request _req;
            bn::regular_bg_ptr _bg;
            bn::sprite_ptr _player;
            bn::sprite_ptr _cover;
            bn::vector<bn::sprite_ptr, 3> _icons;
            bn::vector<bn::sprite_ptr, 5> _pips;
            bn::vector<bn::sprite_ptr, 6> _rack;
            bn::vector<bn::sprite_ptr, 12> _shards;
            dish_plate _plates[max_plates];
            ui::label _clock;
            ui::label _rush_label;
            ui::label _tip_label;
            ui::label _combo_label;
            ui::label _popup[3];
            int _popup_timer[3] = {};
            ui::label _lou[3];
            ui::panel _lou_panel;
            int _lou_timer = 0;
            int _shard_timer = 0;
            bn::random _rng;
            int _rush = 0;                  // rushes started
            int _rush_plates_left = 0;      // plates still to spawn in the current rush
            int _spawn_wait = 60;
            int _frame = 0;
            int _total_frames = 1;
            int _washed = 0;
            int _perfect = 0;
            int _good = 0;
            int _broken = 0;
            int _misses = 0;
            int _streak = 0;
            int _pose = 0;
            int _pose_timer = 0;
            int _end_wait = -1;
            int _rack_count = 0;
            int _last_clock = -1;
            int _last_tip = -1;
            int _last_combo = -1;
            int _total_plates = 0;
            int _bot_hold = 0;
            bool _early = false;

            [[nodiscard]] bn::fixed _speed() const
            {
                return bn::fixed(0.72) * _req.tempo_percent / 100;
            }

            [[nodiscard]] int _spacing_frames() const
            {
                return 92 * 100 / _req.tempo_percent;
            }

            [[nodiscard]] int _plates_in_rush(int rush) const
            {
                return 4 + (rush >= 3 ? 1 : 0) + (rush >= 6 ? 1 : 0);      // 4, 4, 4, 5, 5, 5, 6, 6 (rush index 0..7)
            }

            [[nodiscard]] int _tip() const
            {
                int steps = _perfect + _good + _misses;
                int tip = 0;

                if(steps > 0)
                {
                    int share = (_perfect * 100) / steps;

                    if(share >= 85 && _broken <= 1)
                    {
                        tip = 3;
                    }
                    else if(share >= 60)
                    {
                        tip = 2;
                    }
                    else if(share >= 35)
                    {
                        tip = 1;
                    }
                }

                tip -= _broken;
                return tip < 0 ? 0 : tip;
            }

            void _set_popup(int index, const char* text, int x, int y, bool gold)
            {
                _popup[index].set_centre(ui::font9, x, y, text, gold ? ui::role::hud_money : ui::role::hud_clock);
                _popup_timer[index] = 36;
            }

            void _draw_hud(bool force)
            {
                // the shift runs from the start time to +4 h over the whole rush plan
                int total = _plates_total();
                int done = _washed + _broken;
                int minute = _req.start_minutes + ((done * 240) / (total > 0 ? total : 1));
                minute = minute > _req.start_minutes + 240 ? _req.start_minutes + 240 : minute;

                if(force || minute / 5 != _last_clock)
                {
                    _last_clock = minute / 5;
                    int hours = (minute / 60) % 24;
                    bn::string<8> text;
                    text.append(bn::to_string<4>(hours > 12 ? hours - 12 : hours));
                    text.append(':');

                    if(minute % 60 < 10)
                    {
                        text.append('0');
                    }

                    text.append(bn::to_string<4>(minute % 60));
                    _clock.set(ui::font9, 4, 10, text, ui::role::hud_clock);
                }

                int tip = _tip();

                if(force || tip != _last_tip)
                {
                    _last_tip = tip;
                    bn::string<16> text("TIP $");
                    text.append(bn::to_string<4>(tip));
                    _tip_label.set(ui::font9, 124, 10, text, ui::role::hud_money);
                }

                int combo = 1 + (_streak / 3);
                combo = combo > 9 ? 9 : combo;

                if(force || combo != _last_combo)
                {
                    _last_combo = combo;
                    bn::string<8> text("x");
                    text.append(bn::to_string<4>(combo));
                    _combo_label.set(ui::font9, 180, 10, text, combo > 1 ? ui::role::hud_money : ui::role::hud_clock);
                }
            }

            [[nodiscard]] int _plates_total() const
            {
                int total = 0;

                for(int rush = 0; rush < rush_count; ++rush)
                {
                    total += _plates_in_rush(rush);
                }

                return total;
            }

            void _update_rush_label()
            {
                bn::string<16> text("RUSH ");
                text.append(bn::to_string<4>(_rush));
                text.append('/');
                text.append(bn::to_string<4>(rush_count));
                _rush_label.set(ui::font9, 50, 10, text, ui::role::hud_clock);
            }

            void _title()
            {
                apply_fade(0, bn::fixed(0.5));
                ui::set_night(is_night(_req.start_minutes));
                ui::panel banner;
                ui::label banner_title;
                ui::label help[4];
                banner.open(112, 4, 124, 49, true);
                banner_title.set_centre(ui::font11, 174, 18, "PLATE RUSH", ui::role::title);
                help[0].set_centre(ui::font9, 174, 44, "Hit the key inside [ ]", ui::role::text);
                help[1].set(ui::font9, 118, 66, "A scrub   B rinse", ui::role::hud_clock);
                help[2].set(ui::font9, 118, 77, "Up stack  Pan: mash A", ui::role::hud_clock);
                help[3].set(ui::font9, 118, 88, "3 broken plates: over", ui::role::hud_clock);
                dialogue_box box;
                box.open(int(npc_id::lou), false, 0);
                say_auto(box, "Wash, rinse, repeat! Drop one, I cry.", 1, _req.bot);
                box.close();
                bn::core::update();
                apply_fade(0, 0);
            }

            void _spawn_plate()
            {
                for(dish_plate& p : _plates)
                {
                    if(p.active)
                    {
                        continue;
                    }

                    p = dish_plate();
                    p.active = true;
                    p.x = start_x;
                    _rng.update();
                    p.pan = _rush >= 3 && _rng.get_int(100) < _req.pan_percent;

                    if(p.pan)
                    {
                        p.sprite = bn::sprite_items::mg_pan.create_sprite(0, 0, 0);
                    }
                    else
                    {
                        p.sprite = bn::sprite_items::mg_plate.create_sprite(0, 0, 0);
                    }

                    p.sprite->set_z_order(3);
                    ++_total_plates;
                    return;
                }
            }

            void _place_plate(dish_plate& p)
            {
                if(p.pan)
                {
                    put(*p.sprite, p.x.round_integer() - 20, plate_y - 32, 64, 64);
                }
                else
                {
                    put(*p.sprite, p.x.round_integer() - 16, plate_y - 8, 32, 16);
                }
            }

            void _break(dish_plate& p, bool crash_text)
            {
                p.broken = true;
                p.timer = 36;
                ++_broken;
                ++_misses;
                _streak = 0;
                int x = p.x.round_integer();

                if(p.pan)
                {
                    p.pan = false;
                    p.sprite = bn::sprite_items::mg_plate.create_sprite(0, 0, 3);
                    p.sprite->set_z_order(3);
                }
                else
                {
                    p.sprite->set_tiles(bn::sprite_items::mg_plate.tiles_item(), 3);
                }

                if(crash_text)
                {
                    _set_popup(0, "CRASH!", x, 80, false);
                }

                for(int index = 0; index < _broken && index < 3; ++index)
                {
                    _icons[index].set_tiles(bn::sprite_items::mg_fx.tiles_item(), 3);
                }

                _lou_panel.open(60, 18, 168, 36, false);
                _lou[0].set(ui::font9, 68, 32, "LOU:", ui::role::title);
                _lou[1].set(ui::font9, 100, 32, _broken >= 3 ? "That's three! Sit down." : "Mind the china!", ui::role::text);
                _lou_timer = 90;

                if(_broken >= 3)
                {
                    _early = true;
                    _end_wait = 70;
                }
            }

            void _step_done(dish_plate& p, bool perfect, int zone)
            {
                if(perfect)
                {
                    ++_perfect;
                }
                else
                {
                    ++_good;
                }

                ++_streak;
                _set_popup(zone, perfect ? "PERFECT!" : "GOOD", p.x.round_integer(), 82, perfect);
                _pose = 1 + zone;
                _pose_timer = 9;
                ++p.stage;

                if(p.stage == 1)
                {
                    p.sprite = bn::sprite_items::mg_plate.create_sprite(0, 0, 1);
                    p.sprite->set_z_order(3);
                }
                else if(p.stage == 2)
                {
                    p.sprite->set_tiles(bn::sprite_items::mg_plate.tiles_item(), 2);
                }
                else
                {
                    // stacked into the rack
                    ++_washed;
                    p.active = false;
                    p.sprite.reset();

                    if(int(_rack.size()) >= 6)
                    {
                        _rack.clear();
                    }

                    bn::sprite_ptr s = bn::sprite_items::mg_rack.create_sprite(0, 0);
                    put(s, 176 + (int(_rack.size()) * 7), 60, 8, 32);
                    _rack.push_back(bn::move(s));
                }
            }

            // The plate in `zone` that still needs that step (or nullptr).
            [[nodiscard]] dish_plate* _plate_in_zone(int zone)
            {
                for(dish_plate& p : _plates)
                {
                    int x = p.x.round_integer();

                    if(p.active && ! p.broken && p.stage == zone && x >= zone_x[zone] + zone_left && x <= zone_x[zone] + zone_right)
                    {
                        return &p;
                    }
                }

                return nullptr;
            }

            void _press(int zone)
            {
                dish_plate* p = _plate_in_zone(zone);

                if(! p)
                {
                    return;
                }

                int offset = p->x.round_integer() - zone_x[zone];
                bool centred = offset >= -4 && offset <= 4;

                if(p->pan)
                {
                    // greasy pan: mash A five times inside the brackets
                    ++p->presses;

                    for(int index = 0; index < 5; ++index)
                    {
                        _pips[index].set_tiles(bn::sprite_items::mg_fx.tiles_item(), index < p->presses ? 5 : 4);
                    }

                    if(p->presses >= 5)
                    {
                        for(bn::sprite_ptr& pip : _pips)
                        {
                            pip.set_visible(false);
                        }

                        // the pan turns into a (soapy) plate that goes on to the rinse
                        _step_done(*p, offset <= 0, zone);
                        p->pan = false;
                    }

                    return;
                }

                _step_done(*p, centred, zone);
            }

            [[nodiscard]] input _bot_input()
            {
                input in;

                if(_bot_hold > 0)
                {
                    --_bot_hold;
                    return in;
                }

                _rng.update();

                for(int zone = 0; zone < 3; ++zone)
                {
                    dish_plate* p = _plate_in_zone(zone);

                    if(! p)
                    {
                        continue;
                    }

                    int offset = p->x.round_integer() - zone_x[zone];
                    int aim = _req.bot == 1 ? 0 : (_req.bot == 2 ? 8 : 14);

                    if(_req.bot == 3 && ! p->pan && _rng.get_int(2) == 0)
                    {
                        continue;       // terrible: often just watches the plate go by
                    }

                    if(p->pan)
                    {
                        in.a = true;
                        _bot_hold = _req.bot == 3 ? 9 : 3;
                        return in;
                    }

                    if(offset >= aim)
                    {
                        in.a = zone == 0;
                        in.b = zone == 1;
                        in.up = zone == 2;
                        return in;
                    }
                }

                return in;
            }

            void _play()
            {
                _draw_hud(true);
                _update_rush_label();
                _rush = 0;
                _spawn_wait = 50;
                bn::fixed speed = _speed();

                while(true)
                {
                    // spawning
                    if(_end_wait < 0)
                    {
                        if(_spawn_wait > 0)
                        {
                            --_spawn_wait;
                        }
                        else if(_rush_plates_left > 0)
                        {
                            _spawn_plate();
                            --_rush_plates_left;
                            _spawn_wait = _rush_plates_left > 0 ? _spawn_frames_between() : 170 * 100 / _req.tempo_percent;
                        }
                        else if(_rush < rush_count)
                        {
                            _rush_plates_left = _plates_in_rush(_rush);
                            ++_rush;
                            _update_rush_label();
                            _spawn_wait = 0;
                        }
                    }

                    input in = _req.bot ? _bot_input() : read_keys();

                    if(_end_wait < 0)
                    {
                        if(in.a)
                        {
                            _press(0);
                        }

                        if(in.b)
                        {
                            _press(1);
                        }

                        if(in.up)
                        {
                            _press(2);
                        }
                    }

                    // pan pips are shown while a pan is in the scrub zone
                    bool pan_visible = false;

                    for(dish_plate& p : _plates)
                    {
                        if(p.active && p.pan && ! p.broken && p.stage == 0)
                        {
                            pan_visible = true;
                            int x = p.x.round_integer();

                            for(int index = 0; index < 5; ++index)
                            {
                                put(_pips[index], x - 20 + (index * 8), 80, 16, 16);
                                _pips[index].set_visible(x >= zone_x[0] + zone_left - 10);
                            }
                        }
                    }

                    if(! pan_visible)
                    {
                        for(bn::sprite_ptr& pip : _pips)
                        {
                            pip.set_visible(false);
                        }
                    }

                    // movement and misses
                    bool any_active = false;

                    for(dish_plate& p : _plates)
                    {
                        if(! p.active)
                        {
                            continue;
                        }

                        any_active = true;

                        if(p.broken)
                        {
                            if(--p.timer <= 0)
                            {
                                p.active = false;
                                p.sprite.reset();
                            }

                            continue;
                        }

                        if(_end_wait < 0)
                        {
                            p.x += speed;
                        }

                        int x = p.x.round_integer();

                        if(p.stage < 3 && x > zone_x[p.stage] + zone_right && _end_wait < 0)
                        {
                            _break(p, true);        // missed step: the plate falls
                        }

                        _place_plate(p);
                    }

                    // effects
                    for(int index = 0; index < 3; ++index)
                    {
                        if(_popup_timer[index] > 0 && --_popup_timer[index] == 0)
                        {
                            _popup[index].clear();
                        }
                    }

                    if(_lou_timer > 0 && --_lou_timer == 0)
                    {
                        _lou_panel.close();

                        for(ui::label& label : _lou)
                        {
                            label.clear();
                        }
                    }

                    if(_pose_timer > 0)
                    {
                        --_pose_timer;
                    }

                    _player.set_tiles(bn::sprite_items::player_wash.tiles_item(), _pose_timer > 0 ? _pose : 0);
                    _draw_hud(false);
                    ++_frame;
                    bn::core::update();

                    if(_end_wait >= 0 && --_end_wait <= 0)
                    {
                        break;
                    }

                    if(_end_wait < 0 && _rush >= rush_count && _rush_plates_left == 0 && ! any_active)
                    {
                        break;
                    }
                }

                _lou_panel.close();

                for(ui::label& label : _lou)
                {
                    label.clear();
                }

                for(dish_plate& p : _plates)
                {
                    p.sprite.reset();
                }

                for(bn::sprite_ptr& pip : _pips)
                {
                    pip.set_visible(false);
                }

                for(ui::label& label : _popup)
                {
                    label.clear();
                }
            }

            [[nodiscard]] int _spawn_frames_between() const
            {
                return _spacing_frames();
            }

            minigame_result _finish()
            {
                minigame_result result;
                result.completed = true;
                result.early_end = _early;
                result.count = _washed;
                result.perfect = _perfect;
                result.broken = _broken;
                result.mistakes = _misses;
                result.wage = 16;
                result.tip = _tip();
                {
                    int total = _plates_total();
                    int minutes = (240 * (_washed + _broken)) / (total > 0 ? total : 1);
                    result.minutes = minutes < 60 ? 60 : (minutes > 240 ? 240 : minutes);
                }
                result.score = _perfect + _good;
                apply_fade(0, bn::fixed(0.55));
                ui::set_night(is_night(_req.start_minutes + 240));
                int steps = _perfect + _good + _misses;
                int share = steps > 0 ? (_perfect * 100) / steps : 0;
                result_row rows[7];
                int count = 0;
                rows[count++] = { "Plates", bn::string<16>(bn::to_string<8>(_washed)), false };
                bn::string<16> value(bn::to_string<8>(share));
                value.append('%');
                rows[count++] = { "Perfect", value, false };
                rows[count++] = { "Broken", bn::string<16>(bn::to_string<8>(_broken)), false };
                rows[count++] = { "Wage", money_text(16), false };
                bn::string<16> tip_text = money_text(_tip());

                if(_broken > 0)
                {
                    tip_text = money_text(_tip());
                    tip_text.append(" (-");
                    tip_text.append(bn::to_string<4>(_broken));
                    tip_text.append(")");
                }

                rows[count++] = { "Tip", tip_text, true };
                rows[count++] = { "Total", money_text(16 + _tip()), true };
                result_panel panel;
                _clock.clear();
                _rush_label.clear();
                _tip_label.clear();
                _combo_label.clear();
                panel.open(_early ? "SHIFT CUT SHORT" : "SHIFT DONE!", rows, count);
                dialogue_box box;
                box.open(int(npc_id::lou), false, 0);

                if(_early)
                {
                    say_auto(box, "Three plates... Take a breather, kid. Wage's on me.", 3, _req.bot);
                }
                else if(_broken == 0 && share >= 85)
                {
                    say_auto(box, "Spotless! Staff meal's free. Sit down, kid.", 1, _req.bot);
                }
                else
                {
                    say_auto(box, "Not bad, kid! Staff meal's free.", 1, _req.bot);
                }

                box.close();
                panel.close();
                return result;
            }
        };
    }

    int stock_pay_for_rank(int rank)
    {
        static constexpr int pay[4] = { 18, 19, 20, 22 };
        return pay[rank < 0 ? 0 : (rank > 3 ? 3 : rank)];
    }

    minigame_result run_stock_it(const minigame_request& request)
    {
        minigame_result result;
        {
            stock_game game(request);
            result = game.run();
        }

        apply_fade(1, 0);
        bn::core::update();
        return result;
    }

    minigame_result run_plate_rush(const minigame_request& request)
    {
        minigame_result result;
        {
            dish_game game(request);
            result = game.run();
        }

        apply_fade(1, 0);
        bn::core::update();
        return result;
    }

    minigame_result run_minigame(const minigame_request& request)
    {
        return request.kind == minigame_kind::stock_it ? run_stock_it(request) : run_plate_rush(request);
    }
}
