#include "tl_dialogue.h"

#include "bn_keypad.h"
#include "bn_sprite_items_ui_tag.h"
#include "bn_sprite_items_ui_meter.h"
#include "bn_sprite_items_ui_mt_top.h"
#include "bn_sprite_items_ui_mt_mid.h"
#include "bn_sprite_items_ui_mt_bot.h"

#include "tl_story_ids.h"

namespace tl
{
#ifdef TL_DEBUG_AUTO_TALK
    // headless tests: dialogue pages and choices advance by themselves every 30 frames
    namespace { int auto_frame = 0; bool auto_a() { return (++auto_frame % 30) == 0; } }
#define TL_A_PRESSED() auto_a()
#else
#define TL_A_PRESSED() bn::keypad::a_pressed()
#endif
    namespace
    {
        // system pages (old 40 px box)
        constexpr int sys_box_y = 120;
        constexpr int sys_box_h = 40;
        constexpr int sys_baseline = 132;
        // layout 1
        constexpr int box1_y = 106;
        constexpr int box1_h = 50;
        constexpr int baseline1 = 119;
        constexpr int tag1_x = 118;
        constexpr int meter_x = 222;
        constexpr int meter_y = 114;
        constexpr int meter_frames = 28;            // fill frames (ui_meter has meter_frames + 1)
        constexpr int line_pitch = 10;
        // layout 2
        constexpr int box_bottom = 156;
        constexpr int rows_x = 7;
        constexpr int rows_w = 122;
        constexpr int row_pitch = 14;
        constexpr int tall_x = 132;
        constexpr int tall_y = 64;
        constexpr int tall_frames = 76;
        constexpr int small_x = 142;
        constexpr int small_y = 60;

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

    void dialogue_box::open(int speaker, bool show_meter, int friendship, int partner)
    {
        close();
        _open = true;
        _with_meter = show_meter;
        _partner = partner;
        _speaker = -1;
        _blink = 0;
        _meter_value = friendship;
        _meter_target = friendship;
        _meter_frame = -1;
        set_speaker(speaker, 0);
    }

    void dialogue_box::close()
    {
        _open = false;
        _panel.close();
        _choice_bar.clear();
        _choice_labels.clear();

        for(ui::label& l : _lines)
        {
            l.clear();
        }

        for(ui::label& l : _question)
        {
            l.clear();
        }

        _tag_label.clear();
        _meter_label.clear();
        _delta_label.clear();
        _tag_sprites.clear();
        _pic.clear();
        _tall.clear();
        _meter.reset();
        _a_icon.reset();
        _text.clear();
        _last_page.clear();
        _line_count = 0;
        _shown = 0;
        _total = 0;
        _speaker = -1;
        _with_meter = false;
        _choosing = false;
        _layout = layout::none;
        _options = nullptr;
        _options_count = 0;

        for(int& d : _drawn)
        {
            d = -1;
        }

        for(int& f : _tall_frames)
        {
            f = -1;
        }
    }

    void dialogue_box::_build_tag(int x, int y)
    {
        bn::string<16> name;

        if(_speaker == speaker_player)
        {
            name = story().name();
        }
        else if(_speaker >= 0 && _speaker < npc_count)
        {
            name = npc_infos[_speaker].name;
        }

        _tag_sprites.clear();
        _tag_label.clear();
        int width = ui::text_width(ui::font9, name) + 18;
        int pieces = (width + 15) / 16;
        pieces = pieces < 2 ? 2 : pieces;
        _tag_sprites.push_back(ui::make_piece(bn::sprite_items::ui_tag, x, y, 0, false, 5));

        for(int index = 1; index < pieces - 1; ++index)
        {
            _tag_sprites.push_back(ui::make_piece(bn::sprite_items::ui_tag, x + (index * 16), y, 1, false, 5));
        }

        _tag_sprites.push_back(ui::make_piece(bn::sprite_items::ui_tag, x + ((pieces - 1) * 16), y, 0, true, 5));
        _tag_label.set_centre(ui::font9, x + (pieces * 8), y + 11, name, ui::role::name_tag);
    }

    void dialogue_box::_build_portrait(int speaker, bool small)
    {
        _pic.clear();
        const portrait_set* set = portrait_for(speaker);

        if(! set)
        {
            return;
        }

        if(! small)
        {
            // 128 px portrait standing at the bottom left (14 px cut off at the screen edge), quarters TL TR BL BR
            static constexpr int qx[4] = { -14, 50, -14, 50 };
            static constexpr int qy[4] = { 30, 30, 94, 94 };

            for(int i = 0; i < 4; ++i)
            {
                bn::sprite_ptr p = set->big[i]->create_sprite(qx[i] + 32 - 120, qy[i] + 32 - 80, _expr);
                p.set_bg_priority(0);
                p.set_z_order(10);
                _pic.push_back(p);
            }
        }
        else
        {
            // 96 px portrait, mirrored: piece widths 64, 32, 64, 32 (heights 64, 64, 32, 32); the flip swaps the columns
            static constexpr int pw[4] = { 64, 32, 64, 32 };
            static constexpr int ph[4] = { 64, 64, 32, 32 };
            static constexpr int ox[4] = { 32, 0, 32, 0 };
            static constexpr int oy[4] = { 0, 0, 64, 64 };

            for(int i = 0; i < 4; ++i)
            {
                bn::sprite_ptr p = set->small[i]->create_sprite(small_x + ox[i] + pw[i] / 2 - 120, small_y + oy[i] + ph[i] / 2 - 80, _expr);
                p.set_horizontal_flip(true);
                p.set_bg_priority(0);
                p.set_z_order(10);
                _pic.push_back(p);
            }
        }
    }

    void dialogue_box::_build_meter(bool tall)
    {
        _meter.reset();
        _tall.clear();
        _meter_frame = -1;
        _meter_label.clear();

        for(int& f : _tall_frames)
        {
            f = -1;
        }

        if(! _with_meter)
        {
            return;
        }

        if(! tall)
        {
            _meter = bn::sprite_items::ui_meter.create_sprite(meter_x + 8 - 120, meter_y + 16 - 80, 0);
            _meter->set_bg_priority(0);
            _meter->set_z_order(8);
        }
        else
        {
            bn::sprite_ptr a = bn::sprite_items::ui_mt_top.create_sprite(tall_x + 8 - 120, tall_y + 16 - 80, 0);
            bn::sprite_ptr b = bn::sprite_items::ui_mt_mid.create_sprite(tall_x + 8 - 120, tall_y + 32 + 16 - 80, 0);
            bn::sprite_ptr c = bn::sprite_items::ui_mt_bot.create_sprite(tall_x + 8 - 120, tall_y + 64 + 8 - 80, 0);
            a.set_bg_priority(0); b.set_bg_priority(0); c.set_bg_priority(0);
            a.set_z_order(8); b.set_z_order(8); c.set_z_order(8);
            _tall.push_back(a);
            _tall.push_back(b);
            _tall.push_back(c);
        }

        _draw_meter();
    }

    void dialogue_box::_build_layout(layout l, int speaker, int rows_height)
    {
        _panel.close();
        _a_icon.reset();
        _tag_sprites.clear();
        _tag_label.clear();
        _delta_label.clear();

        for(ui::label& line : _lines)
        {
            line.clear();
        }

        for(ui::label& line : _question)
        {
            line.clear();
        }

        _layout = l;

        for(int& d : _drawn)
        {
            d = -1;
        }

        if(l == layout::plain)
        {
            _panel.open(0, sys_box_y, 240, sys_box_h, false);
            _pic.clear();
            _build_meter(false);

            if(speaker != speaker_system)
            {
                _build_tag(plain_text_x, sys_box_y - 10);
            }
        }
        else if(l == layout::one)
        {
            _panel.open(0, box1_y, 240, box1_h, false);
            _build_portrait(speaker, false);
            _build_meter(false);
            _build_tag(tag1_x, box1_y - 10);
        }
        else
        {
            int bh = rows_height;
            int by = box_bottom - bh;
            _panel.open(0, by, 240, bh, false);
            _build_portrait(_partner >= 0 ? _partner : speaker, true);
            _build_meter(true);
            _build_tag(8, by - 10);
        }
    }

    void dialogue_box::set_speaker(int speaker, int expr)
    {
        layout wanted = layout::plain;

        if(speaker != speaker_system && portrait_for(speaker))
        {
            wanted = layout::one;
        }

        if(speaker == _speaker && wanted == _layout)
        {
            set_expression(expr);
            return;
        }

        _speaker = speaker;
        _expr = expr;
        _choosing = false;
        _choice_bar.clear();
        _choice_labels.clear();
        _text_x = wanted == layout::one ? text_x : plain_text_x;
        _text_w = wanted == layout::one ? text_width : plain_text_width;
        _max_lines = wanted == layout::one ? 4 : 3;
        _build_layout(wanted, speaker);
    }

    void dialogue_box::set_expression(int expr)
    {
        if(expr == _expr)
        {
            return;
        }

        _expr = expr;
        const portrait_set* set = portrait_for(_layout == layout::two && _partner >= 0 ? _partner : _speaker);

        if(set && ! _pic.empty())
        {
            for(int i = 0; i < _pic.size(); ++i)
            {
                const bn::sprite_item* item = _layout == layout::two ? set->small[i] : set->big[i];
                _pic[i].set_tiles(item->tiles_item(), _expr);
            }
        }
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
        _last_page.clear();

        for(int& d : _drawn)
        {
            d = -1;
        }

        for(bn::string<64>& line : _line_text)
        {
            line.clear();
        }

        while(_line_count < _max_lines && _pos < length)
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

            if(! _last_page.empty() && ! _last_page.full())
            {
                _last_page.push_back(' ');
            }

            _last_page.append(line.c_str());
            ++_line_count;
        }

        _draw_lines(true);
        return true;
    }

    void dialogue_box::_draw_lines(bool force)
    {
        int remaining = _shown;
        int baseline = _layout == layout::one ? baseline1 : sys_baseline;

        for(int index = 0; index < _max_lines; ++index)
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
                        _lines[index].set(ui::font9, _text_x, baseline + (index * line_pitch),
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
            if(TL_A_PRESSED() || bn::keypad::b_pressed())
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
            _a_icon = _layout == layout::one ? ui::make_button(0, 226, 146) : ui::make_button(0, 220, 144);
            _blink = 0;
        }

        _a_icon->set_visible(((_blink / 24) & 1) == 0);

        if(TL_A_PRESSED() || bn::keypad::b_pressed())
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

        // the last page becomes the question (wrapped to the rows' width, at most three lines)
        bn::string<64> q[3];
        int qn = 0;
        {
            int pos = 0;
            int length = _last_page.size();

            while(pos < length && qn < 3)
            {
                bn::string<64>& line = q[qn];

                while(pos < length)
                {
                    int end = pos;

                    while(end < length && _last_page[end] != ' ')
                    {
                        ++end;
                    }

                    bn::string<64> candidate = line;

                    if(! candidate.empty())
                    {
                        candidate.push_back(' ');
                    }

                    for(int k = pos; k < end && ! candidate.full(); ++k)
                    {
                        candidate.push_back(_last_page[k]);
                    }

                    if(line.empty() || ui::text_width(ui::font9, candidate) <= rows_w - 6)
                    {
                        line = candidate;
                        pos = end;

                        while(pos < length && _last_page[pos] == ' ')
                        {
                            ++pos;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                ++qn;
            }
        }

        int bh = 9 + (10 * qn) + (row_pitch * count) + 5;
        bh = (bh >= 65 && bh <= 71) ? 72 : bh;
        int by = box_bottom - bh;
        _rows_top = by + 9 + (10 * qn);
        _choosing = true;

        if(_speaker == speaker_system && _partner >= 0)
        {
            _speaker = _partner;        // the name tag of the person you are talking to
        }

        _build_layout(layout::two, _speaker, bh);

        for(int i = 0; i < qn; ++i)
        {
            _question[i].set(ui::font9, 9, by + 13 + (i * 10), q[i], ui::role::text);
        }

        _choice_labels.clear();

        for(int index = 0; index < count; ++index)
        {
            _choice_labels.emplace_back();
        }

        _draw_choices();
    }

    void dialogue_box::_draw_choices()
    {
        for(int index = 0; index < _options_count; ++index)
        {
            _choice_labels[index].set(ui::font9, rows_x + 12, _rows_top + (index * row_pitch) + 10, _options[index],
                                      index == _selected ? ui::role::selected : ui::role::text);
        }

        _choice_bar.set(rows_x, _rows_top + (_selected * row_pitch), rows_w);
    }

    int dialogue_box::update_choice()
    {
        if(! _choosing)
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

        if(TL_A_PRESSED())
        {
            int chosen = _selected;
#ifdef TL_DEBUG_AUTO_TALK
            for(int index = 0; index < _options_count; ++index)
            {
                if(_options[index] == "Ask about work")
                {
                    chosen = index;     // headless tests take the job offer
                }
            }
#endif
            _choosing = false;
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

            if(_layout == layout::two)
            {
                _delta_label.set_right(ui::font9, tall_x - 3, tall_y - 4, text, ui::role::name_tag);
            }
            else
            {
                _delta_label.set_right(ui::font9, meter_x - 3, meter_y - 2, text, ui::role::name_tag);
            }

            _delta_timer = 100;
        }
    }

    void dialogue_box::_draw_meter()
    {
        if(! _meter && _tall.empty())
        {
            return;
        }

        bn::string<8> number = bn::to_string<8>(_meter_value);

        if(_meter)
        {
            int frame = ((_meter_value * meter_frames) + 50) / 100;

            if(frame != _meter_frame)
            {
                _meter_frame = frame;
                _meter->set_tiles(bn::sprite_items::ui_meter.tiles_item(), frame);
            }

            _meter_label.set_centre(ui::font9, meter_x + 8, meter_y - 2, number, ui::role::hud_clock);
        }
        else
        {
            int n = ((_meter_value * tall_frames) + 50) / 100;
            int top = n > 46 ? n - 46 : 0;
            int mid = n > 14 ? (n - 14 > 32 ? 32 : n - 14) : 0;
            int bot = n > 14 ? 14 : n;
            top = top > 30 ? 30 : top;

            if(_tall_frames[0] != top)
            {
                _tall_frames[0] = top;
                _tall[0].set_tiles(bn::sprite_items::ui_mt_top.tiles_item(), top);
            }

            if(_tall_frames[1] != mid)
            {
                _tall_frames[1] = mid;
                _tall[1].set_tiles(bn::sprite_items::ui_mt_mid.tiles_item(), mid);
            }

            if(_tall_frames[2] != bot)
            {
                _tall_frames[2] = bot;
                _tall[2].set_tiles(bn::sprite_items::ui_mt_bot.tiles_item(), bot);
            }

            _meter_label.set_centre(ui::font9, tall_x + 8, tall_y - 2, number, ui::role::hud_clock);
        }
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
        _box.open(speaker_system, false, 0, -1);
        _box.say(text);
        _step = step::page;
    }

    void conversation::start_script(int node, int npc)
    {
        _message = false;
        _small_talk = false;
        _npc = npc;
        bool meter = npc >= 0 && npc < npc_count && npc_infos[npc].talks;
        _box.open(speaker_system, meter, meter ? story().friendship(npc) : 0, npc);
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
        _box.open(npc, true, story().friendship(npc), npc);
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
        int expr = n.expr;

        // pages without an explicit expression: the NPC's mood in the greeting, the topic's result in the answer
        if(expr == 0 && n.speaker == speaker_npc)
        {
            if(_phase == phase::greeting)
            {
                npc_mood m = story().mood(_npc, _day, _minutes);
                expr = m == npc_mood::good ? expr_happy : (m == npc_mood::grumpy ? expr_angry : 0);
            }
            else if(_phase == phase::answer && _answer_expr >= 0)
            {
                expr = _answer_expr;
            }
        }

        _box.set_speaker(_resolve_speaker(n.speaker), expr);
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
            else if(n.cond_flag >= 0 && ((story().flag(n.cond_flag) != 0) != (n.cond_negated != 0)))
            {
                _show_node(n.cond_next);
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

        // a persistent story question (never lost after small talk): Lou's job offer until it was asked
        _story_node = -1;
        int topic_limit = 3;

        if(_npc == int(npc_id::lou) && ! story().flag(story_flag::asked_lou_job))
        {
            _story_node = dlg::ask_lou_work;
            topic_limit = 2;
        }

        while(chosen < topic_limit)
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

        int rows = chosen;

        if(_story_node >= 0)
        {
            _topic_labels[rows] = "Ask about work";
            _topic_views[rows] = _topic_labels[rows];
            ++rows;
        }

        _topic_labels[rows] = "Bye";
        _topic_views[rows] = _topic_labels[rows];
        _box.choose(_topic_views, rows + 1);
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

        _answer_expr = kind == 'D' ? (delta <= -6 ? int(expr_angry) : int(expr_sad)) : (delta >= 4 ? int(expr_happy) : 0);
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
                    if(_story_node >= 0 && choice == _menu_topics)
                    {
                        _phase = phase::script;
                        _after_script_talk = true;
                        _show_node(_story_node);
                    }
                    else if(choice >= _menu_topics)
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
