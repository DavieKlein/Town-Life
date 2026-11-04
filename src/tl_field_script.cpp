// Cutscene script runner of the field scene (data: tools/cutscenes_src.txt -> src/tl_cutscene_data.cpp), triggers, minigame hand-off,
// the VaultMart staff gate, the cold VaultMart palette and the Day 1-2 helper logic (need hints, evening checklist, diner shifts).

#include "tl_field.h"

#include "bn_core.h"
#include "bn_math.h"
#include "bn_keypad.h"
#include "bn_window.h"
#include "bn_rect_window.h"
#include "bn_bg_palettes.h"
#include "bn_sprite_palettes.h"
#include "bn_sprite_items_gate_b.h"

#include "tl_cutscene.h"
#include "tl_gate_data.h"
#include "tl_story_ids.h"
#include "tl_cutscene_ids.h"

namespace tl
{
    namespace
    {
        constexpr int fade_frames = 12;
        constexpr int pan_speed = 5;

        // facing index (s, sw, w, nw, n, ne, e, se) of a world-space delta, like the player's and the NPCs'
        [[nodiscard]] int facing_from_delta(int dx, int dy)
        {
            int sx = dx - dy;
            int sy = (dx + dy) / 2;
            int ax = sx < 0 ? -sx : sx;
            int ay = sy < 0 ? -sy : sy;

            if(ax * 2 < ay)
            {
                return sy > 0 ? 0 : 4;
            }

            if(ay * 2 < ax)
            {
                return sx > 0 ? 6 : 2;
            }

            if(sx > 0)
            {
                return sy > 0 ? 7 : 5;
            }

            return sy > 0 ? 1 : 3;
        }

        [[nodiscard]] direction direction_of(int index)
        {
            switch(index)
            {
            case 1:
                return direction::up;
            case 2:
                return direction::left;
            case 3:
                return direction::right;
            default:
                return direction::down;
            }
        }

        // The VaultTech staff gate at the foot of the storeroom stairs (graphics/gate_b.bmp from tools/gate_overlay.py): top-left of the
        // 2 x 2 block of 32x64 sprites in image pixels of the corner_market map.
        constexpr int gate_image_x = GATE_IMAGE_X;
        constexpr int gate_image_y = GATE_IMAGE_Y;
        constexpr int gate_rect[4] = { 237, 53, 262, 67 };      // solid footprint (world units)

        BN_DATA_EWRAM_BSS bn::string<200> pending_text;
    }

    // ---------------------------------------------------------------------------------------------------- hand-off to main.cpp
    void apply_minigame_result(save_data& snap, const minigame_request& request, const minigame_result& result)
    {
        story_state& s = story();
        int minutes = result.minutes;

        // natural decay of the game minutes that passed, plus the job's own costs
        auto add_need = [&](int need, bn::fixed delta)
        {
            bn::fixed v = bn::fixed::from_data(snap.need_raw[need]) + delta;
            v = v < 0 ? bn::fixed(0) : (v > 100 ? bn::fixed(100) : v);
            snap.need_raw[need] = v.data();
        };

        for(int need = 0; need < needs::count; ++need)
        {
            add_need(need, needs::decay[need] * minutes);
        }

        int day = snap.day;
        int clock = request.start_minutes + minutes;

        if(request.kind == minigame_kind::stock_it)
        {
            s.set_flag(story_flag::shelves_stocked, 1);
            s.set_flag(story_flag::stock_rank, result.rank + 1);
            add_need(needs::energy, -3);
            add_need(needs::fun, -2);

            if(request.replay)
            {
                snap.money += result.wage;
            }
        }
        else
        {
            // PLATE RUSH: wage + tip (needs bonus / penalty at the start of the shift are applied by the caller through request.pan...)
            int wage = result.wage + result.tip;
            bool all_good = true;
            bool any_low = false;

            for(int need = 0; need < needs::count; ++need)
            {
                int value = bn::fixed::from_data(snap.need_raw[need]).round_integer();
                all_good = all_good && value >= 60;
                any_low = any_low || value <= 15;
            }

            if(all_good)
            {
                wage = (wage * 11 + 9) / 10;
            }
            else if(any_low)
            {
                wage = (wage * 3) / 4;
            }

            snap.money += wage;
            int share = minutes * 100 / 240;
            add_need(needs::energy, -bn::fixed(10) * share / 100);
            add_need(needs::hygiene, -bn::fixed(12) * share / 100);
            add_need(needs::hunger, -bn::fixed(6) * share / 100);
            add_need(needs::fun, -bn::fixed(8) * share / 100);
            // the free staff meal
            add_need(needs::hunger, 30);
            add_need(needs::energy, 5);
            add_need(needs::fun, 3);
            s.set_flag(story_flag::diner_shift_day, day & 255);
            s.add_friendship(int(npc_id::lou), 3);
            pending_text = "Shift done! Wage $";
            pending_text.append(bn::to_string<8>(wage));
            pending_text.append(". Staff meal: eat up!");
        }

        while(clock >= 24 * 60)
        {
            clock -= 24 * 60;
            ++day;
        }

        snap.day = uint16_t(day);
        snap.minutes = uint16_t(clock);
        snap.minute_frames = 0;
        snap.total_minutes += minutes;
        s.fill_save(snap);
    }

    // ---------------------------------------------------------------------------------------------------- triggers
    bool field::_cond_ok(const cs_cond& c) const
    {
        switch(c.kind)
        {
        case cs_cond_kind::map:
            return int(_map_id) == c.a;
        case cs_cond_kind::flag:
            return story().flag(c.a) != 0;
        case cs_cond_kind::noflag:
            return story().flag(c.a) == 0;
        case cs_cond_kind::flag_ge:
            return story().flag(c.a) >= c.b;
        case cs_cond_kind::day_eq:
            return _day == c.a;
        case cs_cond_kind::day_ge:
            return _day >= c.a;
        case cs_cond_kind::time_ge:
            return _minutes >= c.a;
        case cs_cond_kind::time_lt:
            return _minutes < c.a;
        case cs_cond_kind::mission:
            return story().mission() == c.a;
        default:
            return false;
        }
    }

    void field::_check_triggers()
    {
        const cs_trigger* triggers = cutscene_triggers();
        const cs_cond* conds = cutscene_conds();

        for(int index = 0; index < cutscene_triggers_count(); ++index)
        {
            bool ok = true;

            for(int k = 0; k < triggers[index].cond_count && ok; ++k)
            {
                ok = _cond_ok(conds[triggers[index].first_cond + k]);
            }

            if(ok)
            {
                _start_script(triggers[index].script);
                return;
            }
        }
    }

    // ---------------------------------------------------------------------------------------------------- running a script
    void field::_start_script(int id)
    {
        const cs_script& script = cutscene_scripts()[id];
        _script = script_state();
        _script.active = true;
        _fade_target = _fade_counter;
        _script.id = id;
        _script.pc = script.first;
        _script.end = script.first + script.count;
        _cue.reset();
        _player.set_script_input(-1);
        _set_hud_hidden(true);
    }

    void field::_end_script()
    {
        _script = script_state();
        _player.set_script_input(-2);
        _pan_mode = _pan_mode == 0 ? 0 : 2;
        _set_letterbox(0);
        _npcs.release(_day, _minutes);
        _player.set_blockers(_npcs.blockers(), _npcs.count());
        _set_hud_hidden(false);
        _redraw_hud_text();
        _story_check_due = true;
        _update_bars();
    }

    void field::_set_letterbox(int target)
    {
        _letter_target = target;
    }

    void field::_update_letterbox()
    {
        if(_letter < _letter_target)
        {
            ++_letter;
        }
        else if(_letter > _letter_target)
        {
            --_letter;
        }
        else
        {
            return;
        }

        if(_letter == 0)
        {
            bn::window::outside().set_show_all();
            bn::rect_window::internal().set_boundaries(-80, -120, 80, 120);
        }
        else
        {
            bn::window::outside().set_show_nothing();
            bn::window::internal().set_show_all();
            bn::rect_window::internal().set_boundaries(-80 + _letter, -120, 80 - _letter, 120);
        }
    }

    // The player's own interactable of a kind on this map (the bed of the room).
    const interactable* field::_find_kind(interactable_kind kind) const
    {
        for(int index = 0; index < _map->interactables_count; ++index)
        {
            if(_map->interactables[index].kind == kind)
            {
                return _map->interactables + index;
            }
        }

        return nullptr;
    }

    void field::_script_arrived_check()
    {
        // the player's walk: stop when close, or give up after a while
        if(! _script.walking)
        {
            return;
        }

        int dx = _script.walk_x - _player.x();
        int dy = _script.walk_y - _player.y();

        if(dx * dx + dy * dy <= 3 * 3 || ++_script.walk_frames > 900)
        {
            _script.walking = false;
            _player.set_script_input(-1);
        }
        else
        {
            _player.set_script_input(facing_from_delta(dx, dy), _script.walk_run);
        }
    }

    void field::_script_dialogue_done()
    {
        _money += story().take_money();
        _redraw_hud_text();
        _npcs.reset_facings();
        _set_hud_hidden(true);          // stays hidden during the scene
        _script.wait = script_state::wait_kind::none;
    }

    void field::_update_script()
    {
        _rng.update();

        if(_script.wait == script_state::wait_kind::load)
        {
            // the old layers were freed one frame ago (Butano releases their VRAM in core::update): build the new map now
            _script.wait = script_state::wait_kind::none;
            _load_map(_script.warp_map, _script.warp_x, _script.warp_y, _script.warp_facing);
            _set_fade(_fade_counter);
            return;
        }

        _npcs.tick();
        _script_arrived_check();
        _player.update();
        _player.set_blockers(_npcs.blockers(), _npcs.count());
        _update_letterbox();
        _update_camera();
        _update_lighting(false);

        // fades driven by the script
        if(_fade_counter != _fade_target && ++_script.fade_tick >= _script.fade_slow)
        {
            _script.fade_tick = 0;
            _fade_counter += _fade_target > _fade_counter ? 1 : -1;

            if(_script.wait != script_state::wait_kind::card)
            {
                _set_fade(_fade_counter);
            }
        }

        if(_script.flash > 0)
        {
            --_script.flash;
            bn::bg_palettes::set_fade(bn::color(31, 31, 31), bn::fixed(_script.flash) / 8);
            bn::sprite_palettes::set_fade(bn::color(31, 31, 31), bn::fixed(_script.flash) / 8);

            if(_script.flash == 0)
            {
                _set_fade(_fade_counter);
            }
        }

        for(int guard = 0; guard < 64 && _script.active; ++guard)
        {
            // blocking waits
            switch(_script.wait)
            {

            case script_state::wait_kind::frames:
                if(--_script.counter > 0)
                {
                    return;
                }

                break;

            case script_state::wait_kind::fade:
                if(_fade_counter != _fade_target)
                {
                    return;
                }

                break;

            case script_state::wait_kind::moves:
                if(_npcs.moving() || _script.walking)
                {
                    return;
                }

                break;

            case script_state::wait_kind::card:
                _player.set_visible(false);

                if(--_script.counter > 0)
                {
                    return;
                }

                for(ui::label& label : _card_label)
                {
                    label.clear();
                }

                _player.set_visible(true);
                _set_fade(_fade_counter);
                break;

            case script_state::wait_kind::hook:
                // HOOK CAR_ARRIVAL stages: fade out, hold, fade in
                if(_script.hook_stage == 0)
                {
                    if(_fade_counter != _fade_target)
                    {
                        return;
                    }

                    _script.hook_stage = 1;
                    _script.counter = 24;
                    return;
                }

                if(_script.hook_stage == 1)
                {
                    if(--_script.counter > 0)
                    {
                        return;
                    }

                    _fade_target = 0;
                    _script.hook_stage = 2;
                    return;
                }

                if(_fade_counter != _fade_target)
                {
                    return;
                }

                break;

            case script_state::wait_kind::action:
                if(_act.active)
                {
                    _update_activity();
                    _update_clock();

                    if(_act.active)
                    {
                        return;
                    }
                }

                break;

            case script_state::wait_kind::dialogue:
                if(_conversation.active())
                {
                    return;
                }

                break;

            default:
                break;
            }

            _script.wait = script_state::wait_kind::none;

            if(_script.pc >= _script.end)
            {
                _end_script();
                return;
            }

            if(! _run_step(cutscene_steps()[_script.pc++]))
            {
                return;
            }
        }
    }

    // Executes one step; returns false when the script has handed over (ended / started a minigame).
    bool field::_run_step(const cs_step& step)
    {
        using wait_kind = script_state::wait_kind;
        story_state& s = story();

        switch(step.op)
        {

        case cs_op::fade_out:
            _fade_target = fade_frames;
            _script.fade_slow = step.a > 20 ? 3 : 1;
            _script.wait = wait_kind::fade;
            break;

        case cs_op::fade_in:
            _fade_target = 0;
            _script.fade_slow = step.a > 20 ? 3 : 1;
            _script.wait = wait_kind::fade;
            break;

        case cs_op::black:
            _fade_counter = fade_frames;
            _fade_target = fade_frames;
            _set_fade(_fade_counter);
            break;

        case cs_op::flash:
            _script.flash = 8;
            break;

        case cs_op::wait:
            _script.counter = step.a > 0 ? step.a : 1;
            _script.wait = wait_kind::frames;
            break;

        case cs_op::card:
            {
                // the screen is black (BG fade): sprites are un-faded for the text, the player's sprite is hidden meanwhile
                ui::set_night(true);
                _card_label[0].set_centre(ui::font11, 120, 84, step.text, ui::role::hud_clock);
                bn::sprite_palettes::set_fade(bn::color(0, 0, 0), 0);
                _script.counter = 150;
                _script.wait = wait_kind::card;
            }
            break;

        case cs_op::warp:
            _objects_bg.reset();
            _floor_bg.reset();
            _gate.clear();
            _script.warp_map = map_id(step.a);
            _script.warp_x = step.b;
            _script.warp_y = step.c;
            _script.warp_facing = direction_of(step.d);
            _script.wait = wait_kind::load;
            _script.counter = 1;
            _npcs.clear();
            // Butano frees the VRAM of the old layers during the next core update: build the new map one frame later
            return false;

        case cs_op::player_at:
            _player.place(*_map, step.a, step.b, direction_of(step.c));
            _script.walking = false;
            break;

        case cs_op::player_face:
            _player.set_facing_index(step.a);
            break;

        case cs_op::face_to:
            {
                int index = _npc_index(npc_id(step.a));

                if(index >= 0)
                {
                    _player.face_towards(_npcs.x_of(index), _npcs.y_of(index));
                }
            }
            break;

        case cs_op::walk:
            _script.walking = true;
            _script.walk_x = step.a;
            _script.walk_y = step.b;
            _script.walk_run = step.c != 0;
            _script.walk_frames = 0;
            break;

        case cs_op::scene_begin:
            _npcs.set_suppress(true);
            break;

        case cs_op::scene_end:
            _npcs.release(_day, _minutes);
            break;

        case cs_op::spawn:
            _npcs.spawn(npc_id(step.a), step.b, step.c, step.d);
            break;

        case cs_op::despawn:
            _npcs.despawn(npc_id(step.a));
            break;

        case cs_op::swap:
            _npcs.swap(npc_id(step.a), npc_id(step.b));
            break;

        case cs_op::move:
            _npcs.move_to(npc_id(step.a), step.b, step.c, step.d != 0);
            break;

        case cs_op::actor_face:
            _npcs.set_facing(npc_id(step.a), step.b);
            break;

        case cs_op::actor_face_player:
            _npcs.face_actor_towards(npc_id(step.a), _player.x(), _player.y());
            break;

        case cs_op::wait_moves:
            _script.wait = wait_kind::moves;
            break;

        case cs_op::say:
            ui::set_night(is_night(_minutes));
            _conversation.start_script(step.a, -1);
            _script.wait = wait_kind::dialogue;
            return true;

        case cs_op::info:
            ui::set_night(is_night(_minutes));
            _conversation.start_message(step.text);
            _script.wait = wait_kind::dialogue;
            return true;

        case cs_op::flag:
            s.set_flag(step.a, step.b);
            break;

        case cs_op::mission:
            s.start_mission(step.a);
            _sync_objective();
            break;

        case cs_op::done:
            s.finish_mission(step.a);
            _sync_objective();
            break;

        case cs_op::money:
            _money += step.a;
            _redraw_hud_text();
            break;

        case cs_op::money_rank:
            _money += stock_pay_for_rank(s.flag(story_flag::stock_rank) - 1);
            _redraw_hud_text();
            break;

        case cs_op::objective:
            _objective = step.text;
            _objective_override = true;
            break;

        case cs_op::objective_clear:
            _objective_override = false;
            _sync_objective();
            break;

        case cs_op::minigame:
            _minigame_req = minigame_request();
            _minigame_req.kind = step.a == 0 ? minigame_kind::stock_it : minigame_kind::plate_rush;
            _minigame_req.day = _day;
            _minigame_req.start_minutes = _minutes;
#ifdef TL_DEBUG_BOT
            _minigame_req.bot = TL_DEBUG_BOT;       // headless tests: a bot plays the minigame
#endif
            _minigame_pending = true;
            _script = script_state();
            _player.set_script_input(-2);
            return false;

        case cs_op::letterbox:
            _set_letterbox(step.a ? 16 : 0);
            break;

        case cs_op::pan:
            _pan_mode = 1;
            _pan_x = step.a;
            _pan_y = step.b;
            break;

        case cs_op::pan_player:
            _pan_mode = 2;
            break;

        case cs_op::time:
            _minutes = step.a * 60 + step.b;
            _minute_frames = 0;
            _light_minutes = -1;
            _update_lighting(true);
            _redraw_hud_text();
            break;

        case cs_op::next_day:
            ++_day;
            _minutes = step.a * 60 + step.b;
            _minute_frames = 0;
            _light_minutes = -1;
            _update_lighting(true);
            _redraw_hud_text();
            break;

        case cs_op::needs:
            _needs.add(needs::hunger, step.a);
            _needs.add(needs::energy, step.b);
            _needs.add(needs::hygiene, step.c);
            _needs.add(needs::fun, step.d);
            _needs.add(needs::bladder, step.e);
            _update_bars();
            break;

        case cs_op::eat:
            {
                _begin_activity(150);
                _act.gain[needs::hunger] = step.a;
                _act.gain[needs::energy] = step.b;
                _act.gain[needs::fun] = step.c;
                _player.start_action(player::action_kind::eat, _player.x(), _player.y(), _act.frames);
                _script.wait = wait_kind::action;
            }
            break;

        case cs_op::lie_bed:
            {
                const interactable* bed = _find_kind(interactable_kind::bed);

                if(bed)
                {
                    _rest_target = bed;
                    _player.sleep_on(bed->x, bed->y, 14);
                }
            }
            break;

        case cs_op::get_up:
            _rest_target = nullptr;
            _player.wake();
            break;

        case cs_op::hook:
            // HOOK CAR_ARRIVAL: Victor Vault's golden car glides up to the shop door here once its design is approved
            // (docs/story_chapter1.md scene 6, beat 1). For now: a short fade to black and back (see wait_kind::hook).
            _fade_target = fade_frames;
            _script.fade_slow = 1;
            _script.hook_stage = 0;
            _script.wait = wait_kind::hook;
            break;

        case cs_op::vaultmart_swap:
            // HOOK VAULTMART_SWAP: the cold VaultMart makeover of Corner Market (white panels, grey awning, self-checkouts, robot arm).
            // The design is pending, so for now only the cold grey palette of the interior (flag corner_market_cold) plus a flash.
            s.set_flag(story_flag::corner_market_cold, 1);
            _light_minutes = -1;
            _script.flash = 8;
            break;

        case cs_op::jump:
            _script.pc = step.a;
            break;

        case cs_op::ifflag:
            if(s.flag(step.a) >= step.b)
            {
                _script.pc = step.c;
            }
            break;

        case cs_op::end:
            _end_script();
            return false;

        default:
            break;
        }

        return true;
    }

    // ---------------------------------------------------------------------------------------------------- camera
    void field::_update_focus()
    {
        int want_x = _player.focus_x();
        int want_y = _player.focus_y();

        if(_pan_mode == 1)
        {
            want_x = _map->to_image_x(_pan_x, _pan_y);
            want_y = _map->to_image_y(_pan_x, _pan_y) - 22;
        }

        if(_pan_mode == 0)
        {
            _focus_x = want_x;
            _focus_y = want_y;
            return;
        }

        int dx = want_x - _focus_x;
        int dy = want_y - _focus_y;
        int adx = dx < 0 ? -dx : dx;
        int ady = dy < 0 ? -dy : dy;
        _focus_x += adx <= pan_speed ? dx : (dx < 0 ? -pan_speed : pan_speed);
        _focus_y += ady <= pan_speed ? dy : (dy < 0 ? -pan_speed : pan_speed);

        if(_pan_mode == 2 && _focus_x == want_x && _focus_y == want_y)
        {
            _pan_mode = 0;
        }
    }

    // ---------------------------------------------------------------------------------------------------- VaultMart gate and cold palette
    void field::_map_story_state()
    {
        _gate.clear();
        _player.set_blocked_rect(0, 0, 0, 0);
        _cold = _map_id == map_id::corner_market && story().flag(story_flag::corner_market_cold);

        if(_map_id == map_id::corner_market && story().flag(story_flag::vault_scene))
        {
            for(int index = 0; index < 4; ++index)
            {
                bn::sprite_ptr piece = bn::sprite_items::gate_b.create_sprite(0, 0, index);
                piece.set_bg_priority(2);
                piece.set_z_order(6);
                _gate.push_back(bn::move(piece));
            }

            _player.set_blocked_rect(gate_rect[0], gate_rect[1], gate_rect[2], gate_rect[3]);
            _update_gate_sprites();
        }

        _light_minutes = -1;
    }

    void field::_update_gate_sprites()
    {
        if(_gate.empty())
        {
            return;
        }

        for(int index = 0; index < 4; ++index)
        {
            int x = gate_image_x + ((index % 2) * 32) - _cam_x;
            int y = gate_image_y + ((index / 2) * 64) - _cam_y;
            _gate[index].set_position(x + 16 - 120, y + 32 - 80);
        }
    }

    // ---------------------------------------------------------------------------------------------------- Day 1 helpers
    void field::_sync_objective_dynamic()
    {
        int mission = story().mission();

        if(mission == mission_id::M03 && story().flag(story_flag::pimm_scene))
        {
            _objective = story().flag(story_flag::has_rye) ? "Give the rye loaf to Mr. Pimm." : "Fetch the rye loaf from the storeroom.";
        }
        else if(mission == mission_id::M05)
        {
            _objective = "Eat ";
            _objective.append(story().flag(story_flag::ate_evening) ? "[x]" : "[ ]");
            _objective.append("  Wash ");
            _objective.append(story().flag(story_flag::washed_evening) ? "[x]" : "[ ]");
            _objective.append("  Sleep on a bench");
        }
    }

    void field::_note_evening(bool ate, bool washed)
    {
        if(! story().flag(story_flag::vault_scene) || story().flag(story_flag::slept_on_bench))
        {
            return;
        }

        if(ate)
        {
            story().set_flag(story_flag::ate_evening, 1);
        }

        if(washed)
        {
            story().set_flag(story_flag::washed_evening, 1);
        }

        _sync_objective();
    }

    // One-time pop-up hints when a need runs low (docs/story_chapter1.md scene 9), after the firing.
    void field::_check_need_hints()
    {
        if(! story().flag(story_flag::vault_scene))
        {
            return;
        }

        struct hint
        {
            int need;
            int below;
            int flag;
            const char* text;
        };

        static constexpr hint hints[] = {
            { needs::hunger, 40, story_flag::hint_hunger, "Your stomach growls. Eat at the diner or the shop. Or... check a bin." },
            { needs::hygiene, 40, story_flag::hint_hygiene, "You feel grimy. A fountain or a sink helps." },
            { needs::energy, 30, story_flag::hint_energy, "You're exhausted. A bench is a bed. Sort of." },
            { needs::bladder, 25, story_flag::hint_bladder, "Nature calls. The park has a public toilet." },
            { needs::fun, 30, story_flag::hint_fun, "You're bored. Try a book at the community centre." },
        };

        for(const hint& h : hints)
        {
            if(! story().flag(h.flag) && _needs.values[h.need] < h.below)
            {
                story().set_flag(h.flag, 1);
                _set_hud_hidden(true);
                ui::set_night(is_night(_minutes));
                _conversation.start_message(h.text);
                return;
            }
        }
    }

    // Lou's dish washing job: lunch 11:00-15:00 (start between 10:30 and 12:00), dinner 17:00-21:00 (16:30-18:00, 30 % faster).
    void field::_try_start_shift()
    {
        story_state& s = story();

        if(! s.flag(story_flag::diner_job))
        {
            _show_info("Lou's Diner", "Ask Lou about work", "first.", "");
            return;
        }

        if(s.flag(story_flag::diner_shift_day) == (_day & 255))
        {
            _show_info("Lou's Diner", "One shift per day.", "Come back tomorrow!", "");
            return;
        }

        bool lunch = _minutes >= 10 * 60 + 30 && _minutes < 12 * 60;
        bool dinner = _minutes >= 16 * 60 + 30 && _minutes < 18 * 60;

        if(! lunch && ! dinner)
        {
            _show_info("Lou's Diner", "Shifts start at 11:00", "and at 17:00.", "");
            return;
        }

        if(_needs.values[needs::hygiene] < 40)
        {
            _show_info("Lou's Diner", "Lou says: wash up.", "Then come back.", "");
            return;
        }

        if(_needs.values[needs::energy] < 20)
        {
            _show_info("Lou's Diner", "You are too tired.", "Rest first.", "");
            return;
        }

        if(_needs.values[needs::hunger] < 10)
        {
            _show_info("Lou's Diner", "Too hungry to work.", "Eat something.", "");
            return;
        }

        _minigame_req = minigame_request();
        _minigame_req.kind = minigame_kind::plate_rush;
        _minigame_req.day = _day;
        _minigame_req.start_minutes = lunch ? (_minutes > 11 * 60 ? _minutes : 11 * 60) : (_minutes > 17 * 60 ? _minutes : 17 * 60);
        _minigame_req.tempo_percent = dinner ? 130 : 100;
        _minigame_req.pan_percent = dinner ? 25 : 12;
#ifdef TL_DEBUG_BOT
        _minigame_req.bot = TL_DEBUG_BOT;
#endif
        _minigame_pending = true;
    }

    const char* take_pending_message()
    {
        if(pending_text.empty())
        {
            return nullptr;
        }

        static bn::string<200> copy;
        copy = pending_text;
        pending_text.clear();
        return copy.c_str();
    }
}
