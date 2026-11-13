#include "tl_story.h"
#include "tl_audio.h"

#include "tl_story_ids.h"

namespace tl
{
    namespace
    {
        constexpr const char* weekdays[7] = { "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" };
        constexpr const char* weekdays_short[7] = { "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" };

        [[nodiscard]] uint32_t mix(uint32_t value)
        {
            value ^= value >> 15;
            value *= 0x2C1B3C6Du;
            value ^= value >> 12;
            value *= 0x297A2D39u;
            value ^= value >> 15;
            return value;
        }

        [[nodiscard]] int clamp_percent(int value)
        {
            return value < 0 ? 0 : (value > 100 ? 100 : value);
        }
    }

    const char* weekday_name(int day)
    {
        return weekdays[((day < 1 ? 1 : day) - 1) % 7];
    }

    const char* weekday_short(int day)
    {
        return weekdays_short[((day < 1 ? 1 : day) - 1) % 7];
    }

    story_state& story()
    {
        static story_state instance;
        return instance;
    }

    story_state::story_state()
    {
        new_game("Sam");
    }

    void story_state::new_game(const char* player_name)
    {
        for(char& c : _name)
        {
            c = 0;
        }

        for(int index = 0; index < save_data::name_size - 1 && player_name[index]; ++index)
        {
            _name[index] = player_name[index];
        }

        for(uint8_t& f : _flags)
        {
            f = 0;
        }

        for(int npc = 0; npc < save_data::npc_slots; ++npc)
        {
            _friendship[npc] = npc < npc_count ? npc_infos[npc].start_friendship : 0;
        }

        for(int npc = 0; npc < save_data::talk_slots; ++npc)
        {
            for(uint8_t& m : _topic_mem[npc])
            {
                m = 0;
            }

            _talk_day[npc] = 0;
            _gain_day[npc] = 0;
            _gained[npc] = 0;
            _coin_day[npc] = 0;
            _gift_day[npc] = 0;
        }

        for(uint8_t& item : _items)
        {
            item = 0;
        }

        for(uint8_t& g : _gossip)
        {
            g = 0;
        }

        _scratch_day = 0;
        _scratch_count = 0;
        _social_delta = 0;
        _coin70 = 0;
        _coins = 0;
        _done_mask = 0;
        _money_delta = 0;
        _completed = 0;
        _started = 0;
        _mission = mission_id::start;
    }

    void story_state::set_flag(int id, int value)
    {
        if(id >= 0 && id < max_flags)
        {
            _flags[id] = uint8_t(value < 0 ? 0 : (value > 255 ? 255 : value));
        }
    }

    void story_state::add_friendship(int npc, int delta)
    {
        if(npc >= 0 && npc < save_data::npc_slots)
        {
            _friendship[npc] = uint8_t(clamp_percent(_friendship[npc] + delta));
        }
    }

    npc_mood story_state::mood(int npc, int day, int minutes) const
    {
        // a random roll per day and NPC (Good 30 %, Neutral 50 %, Grumpy 20 %), shifted by the NPC's base mood
        int roll = int(mix(uint32_t(day) * 7919u + uint32_t(npc) * 104729u + 13u) % 100u);
        npc_mood base = npc_infos[npc].base_mood;

        if(base == npc_mood::good)
        {
            roll -= 20;
        }
        else if(base == npc_mood::grumpy)
        {
            roll += 20;
        }

        npc_mood result = roll < 30 ? npc_mood::good : (roll < 80 ? npc_mood::neutral : npc_mood::grumpy);

        if(npc == int(npc_id::mia))
        {
            // good in the morning, neutral after 14:00
            if(minutes < 11 * 60 && result == npc_mood::neutral)
            {
                result = npc_mood::good;
            }
            else if(minutes >= 14 * 60 && result == npc_mood::good)
            {
                result = npc_mood::neutral;
            }
        }
        else if(npc == int(npc_id::lou) && minutes < 11 * 60 && result == npc_mood::neutral)
        {
            result = npc_mood::good;      // good before 11:00
        }

        return result;
    }

    int story_state::topic_uses(int npc, int topic, int day) const
    {
        if(npc >= save_data::talk_slots)
        {
            return 0;
        }

        int memory = _topic_mem[npc][topic];
        int when = memory >> 2;
        int age = (day - when) & 63;
        return (memory & 3) && age <= 3 ? (memory & 3) : 0;
    }

    void story_state::note_topic(int npc, int topic, int day)
    {
        if(npc < save_data::talk_slots)
        {
            int uses = topic_uses(npc, topic, day);
            uses = uses < 3 ? uses + 1 : 3;
            _topic_mem[npc][topic] = uint8_t(((day & 63) << 2) | uses);
        }
    }

    bool story_state::first_talk_today(int npc, int day) const
    {
        return npc >= save_data::talk_slots || _talk_day[npc] != uint8_t(day & 255) || day == 0;
    }

    void story_state::note_talk(int npc, int day)
    {
        if(npc < save_data::talk_slots)
        {
            _talk_day[npc] = uint8_t(day & 255);
        }
    }

    int story_state::gained_today(int npc, int day) const
    {
        return (npc < save_data::talk_slots && _gain_day[npc] == uint8_t(day & 255)) ? _gained[npc] : 0;
    }

    void story_state::note_gain(int npc, int day, int points)
    {
        if(npc < save_data::talk_slots)
        {
            if(_gain_day[npc] != uint8_t(day & 255))
            {
                _gain_day[npc] = uint8_t(day & 255);
                _gained[npc] = 0;
            }

            int total = _gained[npc] + points;
            _gained[npc] = uint8_t(total > 255 ? 255 : total);
        }
    }

    int story_state::check_coin_reward(int npc, int day, bool first_talk_today)
    {
        if(npc >= save_data::talk_slots || _friendship[npc] < 70)
        {
            return 0;
        }

        int bit = 1 << npc;
        int amount = 0;

        if(! (_coin70 & bit))
        {
            _coin70 = _coin70 | uint32_t(bit);
            amount = 3;
        }
        else if(first_talk_today && ((day - _coin_day[npc]) & 255) >= 3)
        {
            amount = 1;
        }

        if(amount)
        {
            _coin_day[npc] = uint8_t(day & 255);
            _coins = uint16_t(_coins + amount);
        }

        return amount;
    }

    void story_state::apply_effect(const dlg_effect& effect)
    {
        switch(effect.op)
        {

        case dlg_op::friend_delta:
            add_friendship(effect.a, effect.b);
            break;

        case dlg_op::money:
            _money_delta += effect.b;

            if(effect.b > 0)
            {
                audio::received();
            }

            break;

        case dlg_op::set_flag:
            set_flag(effect.a, effect.b);

            if(effect.a == story_flag::has_coffee_voucher && effect.b > 0)
            {
                audio::received();      // Mia hands over the coffee voucher
            }

            break;

        case dlg_op::start_mission:
            start_mission(effect.b);
            break;

        case dlg_op::finish_mission:
            finish_mission(effect.b);
            break;

        case dlg_op::coins:
            _coins = uint16_t(_coins + effect.b);

            if(effect.b > 0)
            {
                audio::received();
            }

            break;

        default:
            break;
        }
    }

    void story_state::start_mission(int id)
    {
        if(id > 0 && id <= mission_count)
        {
            _mission = uint16_t(id);
            _started = id;
        }
    }

    void story_state::finish_mission(int id)
    {
        if(id <= 0 || id > mission_count)
        {
            return;
        }

        _done_mask |= (1u << (id - 1));
        _money_delta += mission_defs[id - 1].reward_money;
        _completed = id;

        if(_mission == id)
        {
            int next = mission_defs[id - 1].next;
            _mission = uint16_t(next);
            _started = next;
        }
    }

    int story_state::check_mission(const story_context& context)
    {
        if(! _mission)
        {
            return 0;
        }

        const mission_def& def = mission_defs[_mission - 1];
        bool done = false;

        switch(def.cond)
        {

        case mission_cond::talk:
            done = context.talked_npc == def.a;
            break;

        case mission_cond::enter_map:
            done = context.map == def.a;
            break;

        case mission_cond::money:
            done = context.money >= def.b;
            break;

        case mission_cond::flag:
            done = flag(def.a) >= def.b;
            break;

        case mission_cond::day:
            done = context.day >= def.a;
            break;

        case mission_cond::time:
            done = context.day > def.a || (context.day == def.a && context.minutes >= def.b);
            break;

        default:
            break;
        }

        if(! done)
        {
            return 0;
        }

        int id = _mission;
        finish_mission(id);
        return id;
    }

    const char* story_state::objective() const
    {
        return _mission ? mission_defs[_mission - 1].objective : "Explore the city";
    }

    void story_state::fill_save(save_data& out) const
    {
        for(int index = 0; index < save_data::name_size; ++index)
        {
            out.player_name[index] = _name[index];
        }

        for(int index = 0; index < max_flags; ++index)
        {
            out.story_flags[index] = _flags[index];
        }

        for(int index = 0; index < save_data::npc_slots; ++index)
        {
            out.friendship[index] = _friendship[index];
        }

        for(int npc = 0; npc < save_data::talk_slots; ++npc)
        {
            for(int topic = 0; topic < topic_count; ++topic)
            {
                out.topic_mem[npc][topic] = _topic_mem[npc][topic];
            }

            out.talk_day[npc] = _talk_day[npc];
            out.gain_day[npc] = _gain_day[npc];
            out.gained[npc] = _gained[npc];
            out.coin_day[npc] = _coin_day[npc];
        }

        for(int gift = 0; gift < gift_count; ++gift)
        {
            out.items[gift] = _items[gift];
        }

        for(int npc = 0; npc < save_data::talk_slots; ++npc)
        {
            out.gift_day[npc] = _gift_day[npc];
        }

        for(int rule = 0; rule < gossip_count; ++rule)
        {
            out.gossip[rule] = _gossip[rule];
        }

        out.scratch_day = _scratch_day;
        out.scratch_count = _scratch_count;
        out.coin70 = uint16_t(_coin70 & 0xFFFF);
        out.coin70_hi = uint16_t(_coin70 >> 16);
        out.coins = _coins;
        out.mission_id = _mission;
        out.missions_done = _done_mask;
    }

    void story_state::apply_save(const save_data& in)
    {
        for(int index = 0; index < save_data::name_size; ++index)
        {
            _name[index] = in.player_name[index];
        }

        _name[save_data::name_size - 1] = 0;

        if(! _name[0])
        {
            _name[0] = 'S';
            _name[1] = 'a';
            _name[2] = 'm';
            _name[3] = 0;
        }

        for(int index = 0; index < max_flags; ++index)
        {
            _flags[index] = in.story_flags[index];
        }

        for(int index = 0; index < save_data::npc_slots; ++index)
        {
            _friendship[index] = uint8_t(clamp_percent(in.friendship[index]));
        }

        for(int npc = 0; npc < save_data::talk_slots; ++npc)
        {
            for(int topic = 0; topic < topic_count; ++topic)
            {
                _topic_mem[npc][topic] = in.topic_mem[npc][topic];
            }

            _talk_day[npc] = in.talk_day[npc];
            _gain_day[npc] = in.gain_day[npc];
            _gained[npc] = in.gained[npc];
            _coin_day[npc] = in.coin_day[npc];
        }

        for(int gift = 0; gift < gift_count; ++gift)
        {
            _items[gift] = in.items[gift] > 9 ? 9 : in.items[gift];
        }

        for(int npc = 0; npc < save_data::talk_slots; ++npc)
        {
            _gift_day[npc] = in.gift_day[npc];
        }

        for(int rule = 0; rule < gossip_count; ++rule)
        {
            _gossip[rule] = in.gossip[rule];
        }

        _scratch_day = in.scratch_day;
        _scratch_count = in.scratch_count > 3 ? 3 : in.scratch_count;
        _social_delta = 0;
        _coin70 = uint32_t(in.coin70) | (uint32_t(in.coin70_hi) << 16);
        _coins = in.coins;
        _mission = in.mission_id <= mission_count ? in.mission_id : 0;
        _done_mask = in.missions_done;
        _money_delta = 0;
        _completed = 0;
        _started = 0;
    }

    // ---------------------------------------------------------------------------------------------------- gifts, gossip, scratch cards
    namespace
    {
        [[nodiscard]] uint8_t day_marker(int day)
        {
            return uint8_t((day % 250) + 1);
        }
    }

    int story_state::items_total() const
    {
        int total = 0;

        for(int gift = 0; gift < gift_count; ++gift)
        {
            total += _items[gift];
        }

        return total;
    }

    void story_state::add_item(int gift, int count)
    {
        int value = _items[gift] + count;
        _items[gift] = uint8_t(value > 9 ? 9 : value);
    }

    bool story_state::take_item(int gift)
    {
        if(! _items[gift])
        {
            return false;
        }

        --_items[gift];
        return true;
    }

    bool story_state::gift_given_today(int npc, int day) const
    {
        return npc < save_data::talk_slots && _gift_day[npc] == uint8_t(day & 255) && day != 0;
    }

    void story_state::note_gift(int npc, int day)
    {
        if(npc < save_data::talk_slots)
        {
            _gift_day[npc] = uint8_t(day & 255);
        }
    }

    void story_state::note_gossip_topic(int npc, int topic, int day)
    {
        for(int rule = 0; rule < gossip_count; ++rule)
        {
            const gossip_rule& r = gossip_rules[rule];

            if(r.kind == 0 && r.npc == npc && r.arg == topic && ! _gossip[rule])
            {
                _gossip[rule] = day_marker(day);
            }
        }
    }

    void story_state::note_gossip_gift(int npc, int gift, int day)
    {
        for(int rule = 0; rule < gossip_count; ++rule)
        {
            const gossip_rule& r = gossip_rules[rule];

            if(r.kind == 1 && r.npc == npc && r.arg == gift && ! _gossip[rule])
            {
                _gossip[rule] = day_marker(day);
            }
        }
    }

    int story_state::pending_gossip(int hearer, int day) const
    {
        for(int rule = 0; rule < gossip_count; ++rule)
        {
            if(gossip_rules[rule].hearer == hearer && _gossip[rule] && _gossip[rule] != 255 && _gossip[rule] != day_marker(day))
            {
                return rule;
            }
        }

        return -1;
    }

    void story_state::gossip_told(int rule)
    {
        _gossip[rule] = 255;
    }

    int story_state::scratch_left(int day) const
    {
        return _scratch_day == uint8_t(day & 255) ? 3 - _scratch_count : 3;
    }

    void story_state::note_scratch(int day)
    {
        if(_scratch_day != uint8_t(day & 255))
        {
            _scratch_day = uint8_t(day & 255);
            _scratch_count = 0;
        }

        ++_scratch_count;
    }
}
