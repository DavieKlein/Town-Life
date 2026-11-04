#include "tl_dialogue.h"

#include "bn_keypad.h"
#include "bn_sprite_items_ui_tag.h"
#include "bn_sprite_items_ui_meter.h"
#include "bn_sprite_items_portrait_mia.h"
#include "bn_sprite_items_portrait_rosa.h"
#include "bn_sprite_items_portrait_dex.h"
#include "bn_sprite_items_portrait_pimm.h"
#include "bn_sprite_items_portrait_lou.h"
#include "bn_sprite_items_portrait_dex_vault.h"
#include "bn_sprite_items_portrait_victor.h"
#include "bn_sprite_items_portrait_robot.h"
#include "bn_sprite_items_portrait_player.h"

#include "tl_story_ids.h"

namespace tl
{
    namespace
    {
        constexpr int box_y = 120;
        constexpr int box_h = 40;
        constexpr int line_baseline = 132;
        constexpr int line_pitch = 10;
        constexpr int tag_y = 110;                  // top of the 16 px tag sprites (the tag itself is rows 2..13)
        constexpr int meter_x = 222;
        constexpr int meter_y = 86;
        constexpr int meter_frames = 28;            // fill frames (ui_meter has meter_frames + 1)
        constexpr int choice_x = 76;
        constexpr int choice_w = 140;
        constexpr int choice_bottom = 109;
        constexpr int choice_pitch = 14;

        [[nodiscard]] const bn::sprite_item* portrait_item(int speaker)
        {
            switch(speaker)
            {
            case int(npc_id::mia):
                return &bn::sprite_items::portrait_mia;
            case int(npc_id::rosa):
                return &bn::sprite_items::portrait_rosa;
            case int(npc_id::dex):
                return &bn::sprite_items::portrait_dex;
            case int(npc_id::pimm):
                return &bn::sprite_items::portrait_pimm;
            case int(npc_id::lou):
                return &bn::sprite_items::portrait_lou;
            case int(npc_id::dex_vault):
                return &bn::sprite_items::portrait_dex_vault;
            case int(npc_id::victor):
                return &bn::sprite_items::portrait_victor;
            case int(npc_id::robot):
                return &bn::sprite_items::portrait_robot;
            case speaker_player:
                return &bn::sprite_items::portrait_player;
            default:
                return nullptr;
            }
        }

        [[nodiscard]] int met_flag(int npc)
        {
            switch(npc)
            {
            case int(npc_id::mia):
                return story_flag::met_mia;
            case int(npc_id::rosa):
                return story_flag::met_rosa;
            case int(npc_id::dex):
                return story_flag::met_dex;
            case int(npc_id::pimm):
                return story_flag::met_pimm;
            case int(npc_id::lou):
                return story_flag::met_lou;
            case int(npc_id::halloran):
                return story_flag::met_halloran;
            default:
                return -1;
            }
        }
    }

    // ---------------------------------------------------------------------------------------------------------

    void dialogue_box::open(int speaker, bool show_meter, int friendship)
    {
        close();
        _open = true;
        _panel.open(0, box_y, 240, box_h, false);
        _with_meter = show_meter;
        _speaker = -1;
        _blink = 0;

        if(show_meter)
        {
            _meter_value = friendship;
            _meter_target = friendship;
            _meter_frame = -1;
            _meter = bn::sprite_items::ui_meter.create_sprite(meter_x + 8 - 120, meter_y + 16 - 80, 0);
            _meter->set_bg_priority(0);
            _meter->set_z_order(8);
            _draw_meter();
        }

        set_speaker(speaker);
    }

    void dialogue_box::close()
    {
        _open = false;
        _panel.close();
        _choice_panel.close();
        _choice_bar.clear();
        _choice_labels.clear();

        for(ui::label& l : _lines)
        {
            l.clear();
        }

        _tag_label.clear();
        _meter_label.clear();
        _delta_label.clear();
        _tag_sprites.clear();
        _portrait.reset();
        _meter.reset();
        _a_icon.reset();
        _text.clear();
        _line_count = 0;
        _shown = 0;
        _total = 0;
        _speaker = -1;
        _with_meter = false;
        _options = nullptr;
        _options_count = 0;

        for(int& d : _drawn)
        {
            d = -1;
        }
    }

    void dialogue_box::set_speaker(int speaker)
    {
        if(speaker == _speaker)
        {
            return;
        }

        _speaker = speaker;
        _text_x = speaker == speaker_system ? system_text_x : text_x;
        _text_w = speaker == speaker_system ? system_text_width : text_width;
        _portrait.reset();
        _tag_sprites.clear();
        _tag_label.clear();
        const bn::sprite_item* item = portrait_item(speaker);

        if(item)
        {
            _portrait = item->create_sprite(5 + 32 - 120, 96 + 32 - 80);
            _portrait->set_bg_priority(0);
            _portrait->set_z_order(10);
        }

        if(speaker == speaker_system)
        {
            return;
        }

        bn::string<16> name;

        if(speaker == speaker_player)
        {
            name = story().name();
        }
        else if(speaker >= 0 && speaker < npc_count)
        {
            name = npc_infos[speaker].name;
        }

        int width = ui::text_width(ui::font9, name) + 18;
        int pieces = (width + 15) / 16;
        pieces = pieces < 2 ? 2 : pieces;
        int tag_x = text_x;
        _tag_sprites.push_back(ui::make_piece(bn::sprite_items::ui_tag, tag_x, tag_y, 0, false, 5));

        for(int index = 1; index < pieces - 1; ++index)
        {
            _tag_sprites.push_back(ui::make_piece(bn::sprite_items::ui_tag, tag_x + (index * 16), tag_y, 1, false, 5));
        }

        _tag_sprites.push_back(ui::make_piece(bn::sprite_items::ui_tag, tag_x + ((pieces - 1) * 16), tag_y, 0, true, 5));
        _tag_label.set_centre(ui::font9, tag_x + (pieces * 8), tag_y + 11, name, ui::role::name_tag);
    }

    void dialogue_box::say(const char* text)
    {
        _text.clear();
        const char* name = story().name();

        for(const char* c = text; *c; ++c)
        {
            if(c[0] == '{' && c[1] == 'N' && c[2] == 'A' && c[3] == 'M' && c[4] == 'E' && c[5] == '}')
            {
                _text.append(name);
                c += 5;
            }
            else if(! _text.full())
            {
                _text.push_back(*c);
            }
        }

        _pos = 0;
        _a_icon.reset();
        _next_page();
    }

    bool dialogue_box::_next_page()
    {
        int length = _text.size();

        while(_pos < length && _text[_pos] == ' ')
        {
            ++_pos;
        }

        if(_pos >= length)
        {
            return false;
        }

        _line_count = 0;
        _total = 0;
        _shown = 0;

        for(int& d : _drawn)
        {
            d = -1;
        }

        for(bn::string<64>& line : _line_text)
        {
            line.clear();
        }

        while(_line_count < 3 && _pos < length)
        {
            bn::string<64>& line = _line_text[_line_count];

            while(_pos < length)
            {
                int end = _pos;

                while(end < length && _text[end] != ' ')
                {
                    ++end;
                }

                bn::string<64> candidate = line;

                if(! candidate.empty() && ! candidate.full())
                {
                    candidate.push_back(' ');
                }

                for(int index = _pos; index < end && ! candidate.full(); ++index)
                {
                    candidate.push_back(_text[index]);
                }

                if(ui::text_width(ui::font9, candidate) <= _text_w || line.empty())
                {
                    if(ui::text_width(ui::font9, candidate) > _text_w)
                    {
                        // a single word wider than the line: cut it
                        candidate.clear();
                        int index = _pos;

                        while(index < end && ui::text_width(ui::font9, candidate) < _text_w - 8 && ! candidate.full())
                        {
                            candidate.push_back(_text[index++]);
                        }

                        line = candidate;
                        _pos = index;
                        break;
                    }

                    line = candidate;
                    _pos = end;

                    while(_pos < length && _text[_pos] == ' ')
                    {
                        ++_pos;
                    }
                }
                else
                {
                    break;
                }
            }

            _total += line.size();
            ++_line_count;
        }

        _draw_lines(true);
        return true;
    }

    void dialogue_box::_draw_lines(bool force)
    {
        int remaining = _shown;

        for(int index = 0; index < 3; ++index)
        {
            int length = index < _line_count ? _line_text[index].size() : 0;
            int count = remaining < length ? remaining : length;
            remaining -= count;

            if(count < 0)
            {
                count = 0;
            }

            if(force || count != _drawn[index])
            {
                if(count != _drawn[index])
                {
                    _drawn[index] = count;

                    if(count == 0)
                    {
                        _lines[index].clear();
                    }
                    else
                    {
                        _lines[index].set(ui::font9, _text_x, line_baseline + (index * line_pitch),
                                          bn::string_view(_line_text[index].data(), count), ui::role::text);
                    }
                }
            }
        }
    }

    bool dialogue_box::update_text()
    {
        if(_shown < _total)
        {
            if(bn::keypad::a_pressed() || bn::keypad::b_pressed())
            {
                _shown = _total;
                _draw_lines(false);
            }
            else
            {
                _shown += bn::keypad::b_held() ? 3 : 1;

                if(_shown > _total)
                {
                    _shown = _total;
                }

                if((_shown & 1) == 0 || _shown >= _total)
                {
                    _draw_lines(false);
                }
            }

            return false;
        }

        // page complete: blinking A button, wait for A / B
        ++_blink;

        if(! _a_icon)
        {
            _a_icon = ui::make_button(0, 220, 144);
            _blink = 0;
        }

        _a_icon->set_visible(((_blink / 24) & 1) == 0);

        if(bn::keypad::a_pressed() || bn::keypad::b_pressed())
        {
            _a_icon.reset();

            if(_next_page())
            {
                return false;
            }

            return true;
        }

        return false;
    }

    // ---------------------------------------------------------------------------------------------------------

    void dialogue_box::choose(const bn::string_view* options, int count)
    {
        _options = options;
        _options_count = count;
        _selected = 0;
        _a_icon.reset();
        int height = 10 + (count * choice_pitch);

        if(height < 38)
        {
            height = 38;
        }

        int top = choice_bottom - height;
        _choice_panel.open(choice_x, top, choice_w, height, false);
        _choice_labels.clear();

        for(int index = 0; index < count; ++index)
        {
            _choice_labels.emplace_back();
        }

        _draw_choices();
    }

    void dialogue_box::_draw_choices()
    {
        int height = 10 + (_options_count * choice_pitch);
        height = height < 38 ? 38 : height;
        int top = choice_bottom - height + 5;

        for(int index = 0; index < _options_count; ++index)
        {
            _choice_labels[index].set(ui::font9, choice_x + 17, top + (index * choice_pitch) + 10, _options[index],
                                      index == _selected ? ui::role::selected : ui::role::text);
        }

        _choice_bar.set(choice_x + 5, top + (_selected * choice_pitch), choice_w - 10);
    }

    int dialogue_box::update_choice()
    {
        if(! _choice_panel.is_open())
        {
            return -1;
        }

        if(bn::keypad::up_pressed() && _selected > 0)
        {
            --_selected;
            _draw_choices();
        }
        else if(bn::keypad::down_pressed() && _selected < _options_count - 1)
        {
            ++_selected;
            _draw_choices();
        }

        if(bn::keypad::a_pressed())
        {
            int chosen = _selected;
            _choice_panel.close();
            _choice_bar.clear();
            _choice_labels.clear();
            return chosen;
        }

        return -1;
    }

    // ---------------------------------------------------------------------------------------------------------

    void dialogue_box::set_friendship(int value)
    {
        if(! _with_meter)
        {
            return;
        }

        int delta = value - _meter_target;
        _meter_target = value;

        if(delta)
        {
            bn::string<8> text;
            text.append(delta > 0 ? "+" : "-");
            text.append(bn::to_string<4>(delta > 0 ? delta : -delta));
            _delta_label.set_right(ui::font9, meter_x - 3, meter_y - 3, text, ui::role::name_tag);
            _delta_timer = 100;
        }
    }

    void dialogue_box::_draw_meter()
    {
        if(! _meter)
        {
            return;
        }

        int frame = ((_meter_value * meter_frames) + 50) / 100;

        if(frame != _meter_frame)
        {
            _meter_frame = frame;
            _meter->set_tiles(bn::sprite_items::ui_meter.tiles_item(), frame);
        }

        bn::string<8> number = bn::to_string<8>(_meter_value);
        _meter_label.set_centre(ui::font9, meter_x + 8, meter_y - 3, number, ui::role::hud_clock);
    }

    void dialogue_box::update_meter()
    {
        if(! _with_meter)
        {
            return;
        }

        if(_meter_value != _meter_target && --_meter_delay <= 0)
        {
            _meter_delay = 3;
            _meter_value += _meter_target > _meter_value ? 1 : -1;
            _draw_meter();
        }

        if(_delta_timer > 0 && --_delta_timer == 0)
        {
            _delta_label.clear();
        }
    }

    // =========================================================================================================
    // conversation

    int conversation::_resolve_speaker(int speaker) const
    {
        return speaker == speaker_npc ? (_npc >= 0 ? _npc : speaker_system) : speaker;
    }

    void conversation::start_message(const char* text)
    {
        _small_talk = false;
        _message = true;
        _npc = -1;
        _node = -1;
        _phase = phase::tail;
        _box.open(speaker_system, false, 0);
        _box.say(text);
        _step = step::page;
    }

    void conversation::start_script(int node, int npc)
    {
        _message = false;
        _small_talk = false;
        _npc = npc;
        bool meter = npc >= 0 && npc < npc_count && npc_infos[npc].talks;
        _box.open(speaker_system, meter, meter ? story().friendship(npc) : 0);
        _phase = phase::script;
        _after_script_talk = false;
        _show_node(node);
    }

    void conversation::start_talk(int npc, int day, int minutes)
    {
        _small_talk = true;
        _message = false;
        _npc = npc;
        _day = day;
        _minutes = minutes;
        _topics_done = 0;
        _dislikes = 0;
        _used_mask = 0;
        _pending_leave = 0;
        _first_today = story().first_talk_today(npc, day);
        _box.open(npc, true, story().friendship(npc));
        story().note_talk(npc, day);
        int flag = met_flag(npc);
        bool intro = dialogue_intro_nodes[npc] >= 0 && flag >= 0 && ! story().flag(flag);

        if(flag >= 0)
        {
            story().set_flag(flag, 1);
        }

        if(_first_today)
        {
            story().add_friendship(npc, 1);       // just for saying hi
            _box.set_friendship(story().friendship(npc));
        }

        if(intro)
        {
            _phase = phase::script;
            _after_script_talk = true;
            _show_node(dialogue_intro_nodes[npc]);
        }
        else
        {
            _start_greeting();
        }
    }

    void conversation::_start_greeting()
    {
        npc_mood m = story().mood(_npc, _day, _minutes);
        int node = dialogue_greet_nodes[_npc][int(m)];
        _phase = phase::greeting;

        if(node < 0)
        {
            _open_topic_menu();
            return;
        }

        _show_node(node);
    }

    void conversation::_show_node(int node)
    {
        const dlg_node& n = dialogue_nodes()[node];
        _node = node;
        _box.set_speaker(_resolve_speaker(n.speaker));
        _apply_effects(n);

        if(node == dlg::hint_talk)
        {
            story().set_flag(story_flag::hint_talk_seen, 1);
        }

        _box.say(n.text);
        _step = step::page;
    }

    void conversation::_apply_effects(const dlg_node& node)
    {
        for(int index = 0; index < node.effects_count; ++index)
        {
            story().apply_effect(dialogue_effects()[node.effects_first + index]);
        }

        if(_npc >= 0 && _npc < npc_count)
        {
            _box.set_friendship(story().friendship(_npc));
        }
    }

    void conversation::_apply_choice_effects(const dlg_choice& choice)
    {
        for(int index = 0; index < choice.effects_count; ++index)
        {
            story().apply_effect(dialogue_effects()[choice.effects_first + index]);
        }

        if(_npc >= 0 && _npc < npc_count)
        {
            _box.set_friendship(story().friendship(_npc));
        }
    }

    void conversation::_after_page()
    {
        if(_node < 0)
        {
            _end();
            return;
        }

        const dlg_node& n = dialogue_nodes()[_node];

        switch(_phase)
        {

        case phase::script:
            if(n.choices_count)
            {
                const dlg_choice* choices = dialogue_choices() + n.choices_first;

                for(int index = 0; index < n.choices_count && index < 4; ++index)
                {
                    _topic_views[index] = choices[index].text;
                }

                _box.choose(_topic_views, n.choices_count);
                _step = step::choice;
            }
            else if(n.next >= 0 && ! (n.next == dlg::hint_talk && story().flag(story_flag::hint_talk_seen)))
            {
                _show_node(n.next);
            }
            else if(_small_talk && _after_script_talk)
            {
                _after_script_talk = false;
                _open_topic_menu();
            }
            else
            {
                _end();
            }
            break;

        case phase::greeting:
            _open_topic_menu();
            break;

        case phase::opener:
            _begin_answer();
            break;

        case phase::answer:
            if(_dislikes >= 2)
            {
                _phase = phase::leave;
                _show_node(dlg::talk_annoyed_leave);
            }
            else if(_topics_done >= 3)
            {
                _phase = phase::leave;
                _show_node(dlg::talk_enough);
            }
            else
            {
                _open_topic_menu();
            }
            break;

        case phase::leave:
            _finish_small_talk();
            break;

        default:
            _end();
            break;
        }
    }

    void conversation::_open_topic_menu()
    {
        // three random topics out of eight (not the ones already used in this talk); at the first talk of the day one of
        // them is something the NPC likes
        const char* likes = npc_infos[_npc].likes;
        int chosen = 0;
        int mask = _used_mask;

        auto pick = [&](bool liked_only)
        {
            int candidates[topic_count];
            int count = 0;

            for(int topic = 0; topic < topic_count; ++topic)
            {
                if(! (mask & (1 << topic)) && (! liked_only || likes[topic] == 'L'))
                {
                    candidates[count++] = topic;
                }
            }

            if(! count)
            {
                return -1;
            }

            int topic = candidates[_rng.get_unbiased_int(count)];
            mask |= 1 << topic;
            return topic;
        };

        if(_first_today && _topics_done == 0)
        {
            int liked = pick(true);

            if(liked >= 0)
            {
                _topic_ids[chosen++] = liked;
            }
        }

        while(chosen < 3)
        {
            int topic = pick(false);

            if(topic < 0)
            {
                break;
            }

            _topic_ids[chosen++] = topic;
        }

        // shuffle a little so the liked topic is not always first
        if(chosen > 1)
        {
            int swap = _rng.get_unbiased_int(chosen);
            int first = _topic_ids[0];
            _topic_ids[0] = _topic_ids[swap];
            _topic_ids[swap] = first;
        }

        _menu_topics = chosen;

        for(int index = 0; index < chosen; ++index)
        {
            _topic_labels[index] = topic_names[_topic_ids[index]];
            _topic_views[index] = _topic_labels[index];
        }

        _topic_labels[chosen] = "Bye";
        _topic_views[chosen] = _topic_labels[chosen];
        _box.choose(_topic_views, chosen + 1);
        _step = step::topic_menu;
    }

    void conversation::_begin_topic(int topic)
    {
        _topic = topic;
        _used_mask |= 1 << topic;
        _phase = phase::opener;
        _box.set_speaker(speaker_player);
        _box.say(topic_openers[topic]);
        _step = step::page;
    }

    void conversation::_begin_answer()
    {
        story_state& s = story();
        char kind = npc_infos[_npc].likes[_topic];
        int uses = s.topic_uses(_npc, _topic, _day);
        npc_mood m = s.mood(_npc, _day, _minutes);
        int delta;
        int node = dialogue_talk_nodes[_npc][_topic];

        if(kind == 'D')
        {
            delta = uses >= 1 ? -6 : -4;
            ++_dislikes;
        }
        else
        {
            delta = kind == 'L' ? 6 : 2;

            if(m == npc_mood::good)
            {
                delta = (delta * 3) / 2;
            }
            else if(m == npc_mood::grumpy)
            {
                delta = delta / 2;
            }

            delta = delta < 1 ? 1 : delta;

            if(uses == 1)
            {
                delta = delta / 2;
                delta = delta < 1 ? 1 : delta;
            }
            else if(uses >= 2)
            {
                delta = 0;
                node = dlg::talk_repeat;
            }

            int room = story_state::daily_talk_cap - s.gained_today(_npc, _day);
            room = room < 0 ? 0 : room;
            delta = delta > room ? room : delta;
            s.note_gain(_npc, _day, delta);
        }

        s.note_topic(_npc, _topic, _day);
        ++_topics_done;
        s.add_friendship(_npc, delta);
        _phase = phase::answer;

        if(node < 0)
        {
            node = dlg::talk_repeat;
        }

        _show_node(node);        // also moves the meter to the new friendship
    }

    void conversation::_finish_small_talk()
    {
        int coins = story().check_coin_reward(_npc, _day, _first_today);

        if(coins > 0)
        {
            _phase = phase::coins;
            _box.set_speaker(speaker_system);
            _show_node(coins >= 3 ? dlg::coins_first : dlg::coins_again);
            return;
        }

        _end();
    }

    void conversation::_end()
    {
        _box.close();
        _step = step::end;
    }

    bool conversation::update()
    {
        if(_step == step::idle)
        {
            return false;
        }

        _rng.update();
        _box.update_meter();

        switch(_step)
        {

        case step::page:
            if(_box.update_text())
            {
                _after_page();
            }
            break;

        case step::choice:
            {
                int choice = _box.update_choice();

                if(choice >= 0)
                {
                    const dlg_node& n = dialogue_nodes()[_node];
                    const dlg_choice& c = dialogue_choices()[n.choices_first + choice];
                    _apply_choice_effects(c);

                    if(c.next >= 0)
                    {
                        _show_node(c.next);
                    }
                    else
                    {
                        _end();
                    }
                }
            }
            break;

        case step::topic_menu:
            {
                int choice = _box.update_choice();

                if(choice >= 0)
                {
                    if(choice >= _menu_topics)
                    {
                        _phase = phase::leave;
                        int bye = dialogue_bye_nodes[_npc];

                        if(bye >= 0)
                        {
                            _show_node(bye);
                        }
                        else
                        {
                            _finish_small_talk();
                        }
                    }
                    else
                    {
                        _begin_topic(_topic_ids[choice]);
                    }
                }
            }
            break;

        default:
            break;
        }

        if(_step == step::end)
        {
            _step = step::idle;
            return true;
        }

        return false;
    }
}
