// s64: sickness, fainting, the City Clinic (reception, bill), the shower, collectibles and the phone for the field scene.
// Kept apart from tl_field.cpp. See docs/features_backlog.md "Built in s64".

#include "tl_field.h"
#include "tl_audio.h"

#include "bn_keypad.h"
#include "bn_sprite_items_ui_icons.h"

#include "tl_story_ids.h"
#include "tl_cutscene_ids.h"
#include "tl_collect_spots.h"

namespace tl
{
    namespace
    {
        constexpr int faint_minutes = 60;               // an empty need this long makes you faint
        constexpr int red_level = 15;                   // "red" need
        constexpr int sick_after_red = 180;             // minutes with two or more red needs until you are sick
        constexpr int sick_rest_cure = 480;             // minutes asleep that cure a cold on their own
        constexpr int cough_every = 150;                // game minutes between cough messages
        constexpr int faint_fee = 20;
        constexpr int checkup_fee = 8;
        constexpr int medicine_fee = 5;
        constexpr int shower_frames = 360;              // 6 s
        constexpr int collect_frames = 72;
        constexpr bn::fixed sick_speed = 0.8;
        constexpr bn::fixed sick_energy_drain = 0.05;

        constexpr bn::string_view shower_options[] = { "Take a shower ($1)", "Leave" };
        constexpr bn::string_view clinic_options[] = { "Check-up ($8)", "Pay the bill", "Talk to the doctor", "Leave" };
    }

    // ---------------------------------------------------------------------------------------------------- sickness
    void field::_update_health_minute()
    {
        bool asleep = _player.current_activity() == player::activity::sleeping;
        const bn::fixed values[4] = { _needs.values[needs::hunger], _needs.values[needs::energy], _needs.values[needs::hygiene],
                                      _needs.social };

        for(int i = 0; i < 4; ++i)
        {
            if(values[i] < bn::fixed(0.5))
            {
                if(! asleep && ++_zero_min[i] >= faint_minutes)
                {
                    _faint_pending = true;
                }
            }
            else if(values[i] > 8)
            {
                _zero_min[i] = 0;
            }
        }

        int red = 0;
        red += _needs.values[needs::hunger] < red_level ? 1 : 0;
        red += _needs.values[needs::energy] < red_level ? 1 : 0;
        red += _needs.values[needs::hygiene] < red_level ? 1 : 0;
        red += _needs.values[needs::fun] < red_level ? 1 : 0;
        red += _needs.social < red_level ? 1 : 0;

        if(! _sick)
        {
            if(red >= 2)
            {
                if(++_red_min >= sick_after_red)
                {
                    _sick = true;
                    _red_min = 0;
                    _sick_rest = 0;
                    _cough_min = 0;
                    _sick_msg_pending = true;
                }
            }
            else if(_red_min > 0)
            {
                --_red_min;
            }
        }
        else
        {
            _needs.add(needs::energy, -sick_energy_drain);
            ++_cough_min;

            if(asleep && ++_sick_rest >= sick_rest_cure)
            {
                _cure_sickness();
            }
        }

        _player.set_speed_scale(_sick ? sick_speed : bn::fixed(1));

        // phone: new messages, food delivery
        if(phone::deliver(_msg_seen, _day, _minutes, _debt) > 0)
        {
            _mail_blink = 0;
        }
    }

    void field::_cure_sickness()
    {
        _sick = false;
        _sick_rest = 0;
        _red_min = 0;
        _cough_min = 0;
        _player.set_speed_scale(1);
        _sick_icon.reset();
    }

    void field::_update_hud_icons()
    {
        bool show_mail = ! _hud_hidden && phone::has_unread(_msg_seen, _msg_read) && ((_mail_blink++ / 30) % 2 == 0);
        bool show_sick = ! _hud_hidden && _sick;

        if(show_mail && ! _mail_icon)
        {
            bn::sprite_ptr icon = bn::sprite_items::ui_icons.create_sprite(224 - 120 + 8, 4 - 80 + 8, 3);
            icon.set_bg_priority(0);
            icon.set_z_order(40);
            _mail_icon = bn::move(icon);
        }
        else if(! show_mail)
        {
            _mail_icon.reset();
        }

        if(show_sick && ! _sick_icon)
        {
            bn::sprite_ptr icon = bn::sprite_items::ui_icons.create_sprite(206 - 120 + 8, 4 - 80 + 8, 4);
            icon.set_bg_priority(0);
            icon.set_z_order(40);
            _sick_icon = bn::move(icon);
        }
        else if(! show_sick)
        {
            _sick_icon.reset();
        }
    }

    void field::_check_bill_reminder()
    {
        // first free moment of a day (after 8:00) with an open clinic bill
        if(_debt > 0 && _debt_day != _day && _minutes >= 8 * 60)
        {
            _debt_day = _day;
            _story_text = "Clinic bill: you owe $";
            _story_text.append(bn::to_string<8>(_debt));
            _story_text.append(". Pay at the City Clinic reception desk when you can.");
            _set_hud_hidden(true);
            ui::set_night(is_night(_minutes));
            _conversation.start_message(_story_text.c_str());
        }
        else if(_sick && _cough_min >= cough_every)
        {
            _cough_min = 0;
            _set_hud_hidden(true);
            ui::set_night(is_night(_minutes));
            _conversation.start_message("*cough cough* You feel sick. Rest, or see Dr. Okafor at the City Clinic.");
        }
    }

    // What happens in the clinic after a faint (script op `clinic_care 0`): two hours pass, the needs are patched up, the fee is
    // taken or noted as debt. Flag `clinic_paid` tells the script which way it went. Bills by post need a home (pending).
    void field::_clinic_care(int kind)
    {
        if(kind != 0)
        {
            return;
        }

        for(int i = 0; i < 120; ++i)
        {
            _tick_minute();
        }

        _needs.add(needs::hunger, 45);
        _needs.add(needs::energy, 45);
        _needs.add(needs::hygiene, 12);
        _needs.add(needs::fun, 6);
        _needs.add_social(10);
        _needs.add(needs::bladder, 10);
        _faint_pending = false;
        _faints++;

        for(int& z : _zero_min)
        {
            z = 0;
        }

        _cure_sickness();

        if(_money >= faint_fee)
        {
            _money -= faint_fee;
            story().set_flag(story_flag::clinic_paid, 1);
        }
        else
        {
            _debt += faint_fee;
            story().set_flag(story_flag::clinic_paid, 0);
        }

        _debt_day = _day;
        _redraw_hud_text();
        _update_bars();
    }

    // ---------------------------------------------------------------------------------------------------- clinic reception
    void field::_open_clinic_menu(const interactable&)
    {
        _menu.open("City Clinic", clinic_options, 4);
    }

    void field::_clinic_choice(int choice)
    {
        int doctor = _npc_index(npc_id::okafor);

        if(choice >= 0 && choice <= 2 && doctor < 0)
        {
            _show_info("City Clinic", "The doctor is out.", "Open 8 am to 8 pm.", "");
            return;
        }

        if(choice == 0)
        {
            int fee = checkup_fee + (_sick ? medicine_fee : 0);

            if(_money < fee)
            {
                _info_line_a = "A check-up costs $8";
                _info_line_b = "($13 with medicine).";
                _info_line_c = "You can't pay yet.";
                _show_info("City Clinic", _info_line_a.c_str(), _info_line_b.c_str(), _info_line_c.c_str());
                return;
            }

            _money -= fee;
            bool was_sick = _sick;
            int node = dlg::checkup_ok;

            if(was_sick)
            {
                _cure_sickness();
                _needs.add(needs::energy, 10);
                node = dlg::checkup_sick;
            }
            else if(_needs.values[needs::energy] < 35 || _needs.values[needs::hunger] < 30)
            {
                node = dlg::checkup_tired;
                _needs.add(needs::energy, 6);
            }

            _redraw_hud_text();
            _update_bars();
            _set_hud_hidden(true);
            ui::set_night(is_night(_minutes));
            _conversation.start_script(node, doctor >= 0 ? int(npc_id::okafor) : -1);
        }
        else if(choice == 1)
        {
            if(_debt <= 0)
            {
                _show_info("City Clinic", "Nothing to pay.", "Take care of", "yourself!");
                return;
            }

            if(_money < _debt)
            {
                _info_line_a = "You owe $";
                _info_line_a.append(bn::to_string<8>(_debt));
                _info_line_b = "and have $";
                _info_line_b.append(bn::to_string<8>(_money));
                _info_line_b.append(".");
                _info_line_c = "Come back with more.";
                _show_info("City Clinic", _info_line_a.c_str(), _info_line_b.c_str(), _info_line_c.c_str());
                return;
            }

            _money -= _debt;
            _debt = 0;
            _redraw_hud_text();
            _set_hud_hidden(true);
            ui::set_night(is_night(_minutes));
            _conversation.start_script(dlg::faint_paid, doctor >= 0 ? int(npc_id::okafor) : -1);
        }
        else if(choice == 2 && doctor >= 0)
        {
            _start_conversation(doctor);
        }
    }

    // ---------------------------------------------------------------------------------------------------- shower
    void field::_use_shower(const interactable& target)
    {
        if(_money < 1)
        {
            _show_info("Shower", "The coin slot wants", "$1. You have none.", "");
            return;
        }

        if(_needs.values[needs::hygiene] > 92)
        {
            _show_info("Shower", "You're clean", "already.", "");
            return;
        }

        _money -= 1;
        _note_evening(false, true);
        _redraw_hud_text();
        _player.approach(target.x + 3, target.y - 4, 2);          // step into the tray, east side
        _begin_activity(shower_frames);
        _act.gain[needs::hygiene] = bn::fixed(98) - _needs.values[needs::hygiene];
        _act.gain[needs::fun] = 2;
        _player.start_action(player::action_kind::shower, _player.x(), _player.y() + 32, _act.frames);
    }

    // ---------------------------------------------------------------------------------------------------- collectibles
    void field::_pick_collectible(int index)
    {
        const collect_spot& place = collect_spots[index];
        _player.approach(place.x, place.y, 10);
        _begin_activity(collect_frames);
        _act.collectible = index;
        _act.gain[needs::energy] = bn::fixed(-0.3);
        _act.message = true;
        _act.title = "Found";
        _info_line_a = "Found: ";
        _info_line_a.append(collect_item_names[index]);
        _info_line_b = collect_sets[index / 4].name;
        _info_line_b.append(" ");
        _info_line_b.append(bn::to_string<4>(_collect.found_in_set(index / 4) + 1));
        _info_line_b.append("/4");
        _info_line_c = "";
        _player.start_action(player::action_kind::pickup, place.x, place.y, _act.frames);
    }

    void field::_collectible_found(int index)
    {
        int set = index / 4;
        int found = _collect.collect(index);

        if(found >= 4 && ! ((_collect.paid >> set) & 1))
        {
            const collect_set& reward = collect_sets[set];
            _collect.paid = uint8_t(_collect.paid | (1 << set));
            _money += reward.money;

            if(reward.coins)
            {
                story().apply_effect({ dlg_op::coins, 0, int16_t(reward.coins) });
            }

            story().add_friendship(reward.friend_npc, reward.friend_gain);
            _act.message = false;
            _story_text = reward.name;
            audio::play(audio::sfx::mission);
            _story_text.append(" complete! Reward: $");
            _story_text.append(bn::to_string<6>(reward.money));

            if(reward.coins)
            {
                _story_text.append(" and ");
                _story_text.append(bn::to_string<4>(reward.coins));
                _story_text.append(" City Coin");
            }

            _story_text.append(". ");
            _story_text.append(npc_infos[reward.friend_npc].name);
            _story_text.append(" will be glad (friendship +");
            _story_text.append(bn::to_string<4>(reward.friend_gain));
            _story_text.append(").");
            _redraw_hud_text();
            _set_hud_hidden(true);
            ui::set_night(is_night(_minutes));
            _conversation.start_message(_story_text.c_str());
        }
    }

    // ---------------------------------------------------------------------------------------------------- phone
    void field::_open_phone()
    {
        audio::play(audio::sfx::beep);
        phone::io data;
        data.day = _day;
        data.minutes = _minutes;
        data.money = _money;
        data.msg_seen = _msg_seen;
        data.msg_read = _msg_read;

        for(int i = 0; i < 8; ++i)
        {
            data.call_day[i] = _call_day[i];
        }

        data.can_order = _delivery_item < 0;
        _cue.reset();
        ui::set_night(is_night(_minutes));
        _phone.open(data);
        _phone_open = true;
    }

    void field::_update_phone()
    {
        if(_phone.update())
        {
            const phone::io& data = _phone.data();
            _money = data.money;
            _msg_seen = data.msg_seen;
            _msg_read = data.msg_read;

            for(int i = 0; i < 8; ++i)
            {
                _call_day[i] = data.call_day[i];
            }

            if(data.order >= 0)
            {
                _delivery_item = data.order;
                _delivery_due = _total_minutes + phone_delivery_minutes;
            }

            _needs.add_social(story().take_social());
            _phone_open = false;
            _redraw_hud_text();
            _update_bars();
        }
    }

    void field::_try_delivery()
    {
        if(_delivery_item < 0 || _total_minutes < _delivery_due)
        {
            return;
        }

        const phone_food& item = phone_foods[_delivery_item];
        _delivery_item = -1;
        int frames = 100 + (5 * (item.hunger + item.energy)) + (20 * item.quality);
        _begin_activity(frames > 360 ? 360 : frames);
        _act.gain[needs::hunger] = item.hunger;
        _act.gain[needs::energy] = item.energy;
        _act.gain[needs::fun] = item.fun;
        _act.gain[needs::bladder] = item.bladder;

        if(item.bladder < 0)
        {
            _needs.bladder_boost = 90;
        }

        _act.message = true;
        _act.title = "Delivery";
        _info_line_a = item.name;
        _info_line_a.append(" arrived.");
        _info_line_b = "Delicious!";
        _info_line_c = "";
        _note_evening(true, false);
        _player.start_action(player::action_kind::eat, _player.x(), _player.y(), _act.frames);
    }
}
