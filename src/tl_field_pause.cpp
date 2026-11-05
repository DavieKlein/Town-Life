// Pause menu (START) and save/load for the field scene. Kept apart from tl_field.cpp.

#include "tl_field.h"

#include "bn_core.h"
#include "bn_keypad.h"

namespace tl
{
    namespace
    {
        constexpr int bin_slots = save_data::max_maps * save_data::bins_per_map;
    }

    field::field(const save_data& save) :
        field(map_id(save.map), save.x, save.y, direction::down)
    {
        _apply_save(save);
    }

    bool field::_can_pause() const
    {
        return _state == state::playing && ! _menu.is_open() && ! _phone_open && ! _act.active && ! _accident_pending &&
               _player.current_activity() == player::activity::walking;
    }

    void field::_open_pause()
    {
        // Free the HUD text sprites while the pause screen is up (the sprite budget is 128).
        _clock_label.clear();
        _clock_small_label.clear();
        _money_label.clear();
        _day_label.clear();
        _version_label.clear();
        _version_frames = 0;

        pause_info info;
        info.day = _day;
        info.minutes = _minutes;
        info.money = _money;

        for(int need = 0; need < needs::count; ++need)
        {
            info.need_values[need] = _needs.values[need].round_integer();
        }

        info.social = _needs.social.round_integer();
        info.bag = _deposit.bag_total();
        info.credit = _deposit.credit;
        info.coins = story().coins();
        _sync_objective();
        info.objective = _objective.c_str();
        info.sick = _sick;
        info.debt = _debt;
        ui::set_night(is_night(_minutes));
        _pause.open(info);
        _pause_mode = pause_mode::main;
    }

    void field::_open_log()
    {
        static log_info info;
        info = log_info();
        int current = story().mission();
        info.current_title = current ? mission_defs[current - 1].title : "";
        info.current_objective = current ? _objective.c_str() : "";
        info.coins = story().coins();

        for(int id = mission_count; id >= 1 && info.done_count < 24; --id)
        {
            if(story().mission_done(id))
            {
                info.done_titles[info.done_count++] = mission_defs[id - 1].title;
            }
        }

        _pause.close();
        ui::set_night(is_night(_minutes));
        _log.open(info);
        _pause_mode = pause_mode::log;
    }

    void field::_close_pause()
    {
        _pause.close();
        _log.close();
        _collection.close();
        _dialog.close();
        _pause_mode = pause_mode::none;
        _redraw_hud_text();
    }

    void field::_open_dialog(int which)
    {
        static constexpr bn::string_view overwrite_lines[] = { "Overwrite saved game?" };
        static constexpr bn::string_view quit_lines[] = { "Go back to the title?", "Unsaved progress will", "be lost." };
        static constexpr bn::string_view saved_lines[] = { "Your progress is saved." };
        static constexpr bn::string_view slept_lines[] = { "Save game?" };
        static constexpr bn::string_view yes_no[] = { "Yes", "No" };
        static constexpr bn::string_view ok[] = { "OK" };

        _pause.close();

        switch(which)
        {

        case 0:
            _dialog.open("Save game", overwrite_lines, 1, yes_no, 2);
            _pause_mode = pause_mode::confirm_save;
            break;

        case 1:
            _dialog.open("Game saved", saved_lines, 1, ok, 1);
            _pause_mode = pause_mode::saved;
            break;

        case 3:
            _dialog.open("Slept well.", slept_lines, 1, yes_no, 2);
            _pause_mode = pause_mode::sleep_save;
            break;

        default:
            _dialog.open("Quit to title", quit_lines, 3, yes_no, 2);
            _pause_mode = pause_mode::confirm_quit;
            break;
        }
    }

    void field::_update_pause()
    {
        switch(_pause_mode)
        {

        case pause_mode::main:
            {
                int choice = _pause.update();

                if(choice == pause_screen::open_still)
                {
                    break;
                }

                if(choice == pause_screen::resume)
                {
                    _close_pause();
                }
                else if(choice == pause_screen::log)
                {
                    _open_log();
                }
                else if(choice == pause_screen::collection)
                {
                    _pause.close();
                    ui::set_night(is_night(_minutes));
                    _collection.open(_collect.mask, _collect.paid);
                    _pause_mode = pause_mode::collection;
                }
                else if(choice == pause_screen::save)
                {
                    save_data existing;

                    if(save_read(existing))
                    {
                        _open_dialog(0);
                    }
                    else
                    {
                        _save_game();
                    }
                }
                else
                {
                    _open_dialog(2);
                }
            }
            break;

        case pause_mode::log:
            if(_log.update())
            {
                _open_pause();
            }
            break;

        case pause_mode::collection:
            if(_collection.update())
            {
                _open_pause();
            }
            break;

        case pause_mode::confirm_save:
            {
                int choice = _dialog.update();

                if(choice == dialog::open_still)
                {
                    break;
                }

                if(choice == 0)
                {
                    _save_game();
                }
                else
                {
                    _open_pause();
                }
            }
            break;

        case pause_mode::sleep_save:
            {
                int choice = _dialog.update();

                if(choice == dialog::open_still)
                {
                    break;
                }

                if(choice == 0)
                {
                    _save_after_sleep = true;
                    _save_game();
                }
                else
                {
                    _close_pause();
                }
            }
            break;

        case pause_mode::saved:
            if(_dialog.update() != dialog::open_still)
            {
                if(_save_after_sleep)
                {
                    _save_after_sleep = false;
                    _close_pause();
                }
                else
                {
                    _open_pause();
                }
            }
            break;

        case pause_mode::confirm_quit:
            {
                int choice = _dialog.update();

                if(choice == dialog::open_still)
                {
                    break;
                }

                if(choice == 0)
                {
                    bn::core::reset();      // back to the title screen
                }
                else
                {
                    _open_pause();
                }
            }
            break;

        default:
            break;
        }
    }

    void field::_save_game()
    {
        static save_data data;      // big: keep it off the stack
        data = save_data();
        _fill_save(data);
        save_write(data);
        _open_dialog(1);
    }

    void field::_fill_save(save_data& out) const
    {
        out.map = uint8_t(_map - &get_map(map_id(0)));
        out.facing = uint8_t(_player.facing_index());
        out.x = int16_t(_player.x());
        out.y = int16_t(_player.y());
        out.day = uint16_t(_day);
        out.minutes = uint16_t(_minutes);
        out.minute_frames = uint16_t(_minute_frames);
        out.total_minutes = _total_minutes;
        out.money = _money;

        for(int need = 0; need < needs::count; ++need)
        {
            out.need_raw[need] = _needs.values[need].data();
        }

        out.bladder_boost = int16_t(_needs.bladder_boost);
        out.social_valid = 1;
        out.social = uint8_t(_needs.social.round_integer());

        for(int index = 0; index < bin_slots && index < maps_count * 16; ++index)
        {
            out.bin_emptied[index] = _bin_emptied[index];
        }

        story().fill_save(out);
        out.deposit_init = 1;
        out.deposit_cans = uint8_t(_deposit.bag_cans);
        out.deposit_bottles = uint8_t(_deposit.bag_bottles);
        out.deposit_credit = uint8_t(_deposit.credit);

        for(int index = 0; index < deposit::max_spots; ++index)
        {
            out.deposit_spot[index] = _deposit.spot[index];
        }

        // s64
        out.collect_mask = _collect.mask;
        out.collect_paid = _collect.paid;
        out.sick = _sick ? 1 : 0;

        for(int i = 0; i < 4; ++i)
        {
            out.zero_min[i] = uint16_t(_zero_min[i]);
        }

        out.red_min = uint16_t(_red_min);
        out.sick_rest = uint16_t(_sick_rest);
        out.debt = int16_t(_debt);
        out.debt_day = uint8_t(_debt_day);
        out.faints = uint8_t(_faints);
        out.msg_seen = _msg_seen;
        out.msg_read = _msg_read;

        for(int i = 0; i < 8; ++i)
        {
            out.call_day[i] = _call_day[i];
        }

        out.delivery_item = int8_t(_delivery_item);
        out.delivery_due = _delivery_due;
    }

    void field::_apply_save(const save_data& in)
    {
        story().apply_save(in);
        _sync_objective();
        _day = in.day;
        _minutes = in.minutes;
        _minute_frames = in.minute_frames;
        _total_minutes = in.total_minutes;
        _money = in.money;

        for(int need = 0; need < needs::count; ++need)
        {
            bn::fixed value = bn::fixed::from_data(in.need_raw[need]);
            _needs.values[need] = value < 0 ? bn::fixed(0) : (value > 100 ? bn::fixed(100) : value);
        }

        _needs.bladder_boost = in.bladder_boost;
        _needs.social = in.social_valid ? bn::fixed(in.social > 100 ? 100 : in.social) : bn::fixed(60);

        for(int index = 0; index < maps_count * 16; ++index)
        {
            _bin_emptied[index] = in.bin_emptied[index];
        }

        if(in.deposit_init)
        {
            int cans = in.deposit_cans > deposit::bag_max ? deposit::bag_max : in.deposit_cans;
            int bottles = in.deposit_bottles > deposit::bag_max - cans ? deposit::bag_max - cans : in.deposit_bottles;
            _deposit.bag_cans = cans;
            _deposit.bag_bottles = bottles;
            _deposit.credit = in.deposit_credit ? 1 : 0;

            for(int index = 0; index < deposit::max_spots; ++index)
            {
                _deposit.spot[index] = in.deposit_spot[index] & 0x0F;
            }

            _deposit.load(*_map);
        }

        _collect.mask = in.collect_mask & 0x0FFF;
        _collect.paid = in.collect_paid & 7;
        _collect.load(*_map);
        _sick = in.sick != 0;
        _player.set_speed_scale(_sick ? bn::fixed(0.8) : bn::fixed(1));

        for(int i = 0; i < 4; ++i)
        {
            _zero_min[i] = in.zero_min[i];
        }

        _red_min = in.red_min;
        _sick_rest = in.sick_rest;
        _debt = in.debt;
        _debt_day = in.debt_day;
        _faints = in.faints;
        _msg_seen = in.msg_seen;
        _msg_read = in.msg_read;

        for(int i = 0; i < 8; ++i)
        {
            _call_day[i] = in.call_day[i];
        }

        _delivery_item = in.delivery_item >= 0 && in.delivery_item < phone_food_count ? in.delivery_item : -1;
        _delivery_due = in.delivery_due;
        _player.set_facing_index(in.facing);
        _npcs.load(*_map, _map_id, _day, _minutes);
        _player.set_blockers(_npcs.blockers(), _npcs.count());
        _redraw_hud_text();
        _update_bars();
        _map_story_state();         // gate / cold palette depend on the story flags applied above
        _update_lighting(true);
        _update_camera();
    }
}
