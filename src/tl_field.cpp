#include "tl_field.h"

#include "bn_color.h"
#include "bn_string.h"
#include "bn_bg_palettes.h"
#include "bn_sprite_palettes.h"

#include "bn_keypad.h"
#include "bn_regular_bg_items_hud.h"
#include "bn_blending.h"
#include "bn_sprite_items_need_bar.h"
#include "bn_sprite_items_hud_bar.h"
#include "bn_sprite_items_ui_icons.h"
#include "tl_collect_spots.h"
#include "bn_sprite_items_light_pool.h"

#include "tl_deposit_spots.h"
#include "tl_story_ids.h"
#include "tl_cutscene_ids.h"

namespace tl
{
#ifdef TL_DEBUG_POS
    struct dbg_state_t
    {
        char magic[4];
        int x, y, map, day, minutes, money, mission, menu, conv, act, script, state, frame;
        unsigned char flags[80];
        int needs[5];
        int friends[20];
    };

    volatile dbg_state_t dbg_state;
#endif

    namespace
    {
        constexpr int fade_frames = 12;
        constexpr int frames_per_game_minute = 60;     // 1 real second = 1 game minute
        constexpr int frames_per_game_minute_asleep = 4;   // time flies while sleeping on a bench
        constexpr int frames_per_game_minute_bed = 8;      // in the bed the clock runs 8x
        constexpr int nap_minutes = 60;
        constexpr int bed_lift = 14;                       // the lying figure is raised onto the mattress (pixels)
        constexpr int hud_slots = needs::count + 1;   // five needs + Social
        constexpr int bar_levels = 16;                 // frames in need_bar.bmp
        constexpr int interact_reach = 26;             // world units from a bench seat
        constexpr int fountain_reach = 32;             // world units beyond the fountain radius
        constexpr int fixture_reach = 28;              // counters, toilets, sinks, shelves, ...
        constexpr int pickup_reach = 20;               // cans and bottles lying on the ground
        constexpr int npc_reach = 36;                  // world units to talk to somebody
        constexpr int pickup_frames = 72;              // ~1.2 s bend-down
        constexpr int topup_minute = 6 * 60;           // pickups are topped up at 6:00 every day

        // Food: price, quality (1-3), gains over the meal; the meal lasts 100 + 5 * (Hunger + Energy) + 20 * quality
        // frames (max 360): better food is both worth more and takes a bit longer.
        struct shop_item
        {
            int price;
            int quality;
            int hunger;
            int energy;
            int fun;
            int bladder;
        };

        constexpr bn::string_view market_labels[] = { "Bread $2", "Apple $1", "Ready meal $5", "Soda $1" };
        constexpr shop_item market_items[] = {
            { 2, 1, 15, 3, 0, 0 }, { 1, 1, 6, 1, 0, 0 }, { 5, 2, 35, 8, 0, 0 }, { 1, 1, 4, 3, 4, -8 } };
        // VaultMart (cold Corner Market from Day 1 evening): about 50 % dearer (docs/story_chapter1.md 4.2), plus the grey nutrient loaf
        constexpr bn::string_view cold_labels[] = { "Bread $3", "Apple $2", "Ready meal $7", "Soda $2", "Nutrient loaf $2" };
        constexpr shop_item cold_items[] = {
            { 3, 1, 15, 3, 0, 0 }, { 2, 1, 6, 1, 0, 0 }, { 7, 2, 35, 8, 0, 0 }, { 2, 1, 4, 3, 4, -8 }, { 2, 1, 12, 2, -3, 0 } };
        constexpr bn::string_view diner_labels[] = { "Coffee $2", "Pancakes $4", "Burger $6" };
        constexpr shop_item diner_items[] = {
            { 2, 2, 0, 15, 5, -10 }, { 4, 2, 25, 8, 0, 0 }, { 6, 3, 40, 12, 0, 0 } };
        // Bellini Bakery (Old Block): fresh and a bit dearer than the market, better quality
        constexpr bn::string_view bakery_labels[] = { "Fresh bread $3", "Croissant $2", "Cinnamon bun $3", "Coffee $2" };
        constexpr shop_item bakery_items[] = {
            { 3, 2, 22, 4, 0, 0 }, { 2, 2, 12, 5, 2, 0 }, { 3, 3, 15, 6, 5, 0 }, { 2, 2, 0, 15, 5, -10 } };
        // Baker's Lane corner grocery: cheap basics
        constexpr bn::string_view lane_labels[] = { "Apple $1", "Cheese roll $2", "Tea $1", "Sardine tin $2" };
        constexpr shop_item lane_items[] = {
            { 1, 1, 6, 1, 0, 0 }, { 2, 1, 14, 3, 0, 0 }, { 1, 1, 0, 8, 3, -5 }, { 2, 1, 16, 2, -2, 0 } };

        // Rosa's market stall on Cobble Street
        constexpr bn::string_view stall_labels[] = { "Rosa's loaf $2", "Orange $1", "Rye loaf $3" };
        constexpr shop_item stall_items[] = { { 2, 1, 15, 3, 0, 0 }, { 1, 1, 6, 1, 2, 0 }, { 3, 2, 20, 4, 0, 0 } };

        // One table row per shop: the menu title, labels, items and the gifts it sells (indices into gift_defs).
        struct shop_set
        {
            const char* title;
            const bn::string_view* labels;
            const shop_item* items;
            int count;
            const int* gifts;
            int gift_count;
            bool diner;                 // coffee voucher + "Work a shift" apply
        };

        constexpr int market_gifts[] = { 0, 1, 3, 4 };
        constexpr int diner_gifts[] = { 2, 3 };
        constexpr int bakery_gifts[] = { 1, 3 };
        constexpr int lane_gifts[] = { 0, 4 };
        constexpr shop_set market_set = { "Corner Market", market_labels, market_items, 4, market_gifts, 4, false };
        constexpr shop_set vaultmart_set = { "VaultMart", cold_labels, cold_items, 5, nullptr, 0, false };
        constexpr shop_set diner_set = { "Diner", diner_labels, diner_items, 3, diner_gifts, 2, true };
        constexpr shop_set bakery_set = { "Bellini Bakery", bakery_labels, bakery_items, 4, bakery_gifts, 2, false };
        constexpr int stall_gifts[] = { 0 };
        constexpr shop_set stall_set = { "Rosa's Stall", stall_labels, stall_items, 3, stall_gifts, 1, false };
        constexpr shop_set lane_set = { "Lane Grocery", lane_labels, lane_items, 4, lane_gifts, 2, false };

        [[nodiscard]] const shop_set& shop_for(interactable_kind kind, map_id map)
        {
            switch(kind)
            {
            case interactable_kind::shop_diner: return diner_set;
            case interactable_kind::shop_bakery: return bakery_set;
            case interactable_kind::shop_lane: return lane_set;
            case interactable_kind::shop_stall: return stall_set;
            default: return map == map_id::vaultmart ? vaultmart_set : market_set;
            }
        }

        constexpr bn::string_view toilet_options[] = { "Use toilet" };
        constexpr bn::string_view bin_options[] = { "Search the bin" };
        constexpr bn::string_view sink_options[] = { "Wash hands", "Drink water" };
        constexpr bn::string_view book_options[] = { "Read a book" };
        constexpr bn::string_view seat_options[] = { "Sit down" };
        constexpr bn::string_view bed_options[] = { "Sleep", "Take a nap", "Leave" };
        constexpr bn::string_view shower_menu_options[] = { "Take a shower ($1)", "Leave" };
        constexpr bn::string_view desk_options[] = { "Read", "Check notes" };

        // Activities (frames at 60 per second).
        constexpr int wash_hands_frames = 120;
        constexpr int wash_face_frames = 150;
        constexpr int drink_frames = 180;
        constexpr int read_frames = 300;
        constexpr int read_minutes = 30;                    // game minutes that pass while reading
        constexpr int search_frames = 210;
        constexpr int bin_cooldown = 60;                    // game minutes until a bin has something new
        constexpr int toilet_full_frames[3] = { 360, 240, 150 };   // empty to full, by toilet quality 1..3
        constexpr int read_fun[3] = { 10, 18, 30 };         // Fun gained by bookshelf quality 1..3
        constexpr int bladder_boost_minutes = 90;

        // Effects per game minute while resting.
        constexpr bn::fixed sit_fun = 0.35;
        constexpr bn::fixed sit_energy = 0.15;
        constexpr bn::fixed sleep_energy = 0.3;             // on a bench (docs/story_chapter1.md 4.6: slower, a stiff back)
        constexpr bn::fixed bed_energy = 1.0;               // a night in the bed
        constexpr bn::fixed nap_energy = bn::fixed(20) / 60;    // a nap: +20 Energy over its hour
        constexpr bn::fixed wash_face_hygiene = 35;
        constexpr bn::fixed wash_hands_hygiene = 15;

        [[nodiscard]] int distance2(int ax, int ay, int bx, int by)
        {
            return ((ax - bx) * (ax - bx)) + ((ay - by) * (ay - by));
        }

        // Bg priorities: HUD 0, front layer 1 (map pixels in front of the player), player sprite 2,
        // objects 2, shadow + light pools 3, floor 3.
        constexpr int floor_priority = 3;
        constexpr int objects_priority = 2;
        constexpr int front_priority = 1;
        constexpr int hud_priority = 0;

        constexpr int lighting_frames = 5;     // palettes are re-lit (and water cycled) this often

        BN_DATA_EWRAM_BSS bn::color lit_floor[16 * 16];
        BN_DATA_EWRAM_BSS bn::color lit_objects[16 * 16];

        // Visible play area is the screen minus the 32 px HUD bar at the bottom.
        constexpr int hud_height = 32;

        [[nodiscard]] bn::fixed clamp_fixed(bn::fixed value, int min_value, int max_value)
        {
            return value < min_value ? bn::fixed(min_value) : (value > max_value ? bn::fixed(max_value) : value);
        }

        [[nodiscard]] constexpr int clamp(int value, int min_value, int max_value)
        {
            return value < min_value ? min_value : (value > max_value ? max_value : value);
        }
    }

    field::field(map_id start_map, int start_x, int start_y, direction facing)
    {
        ui::set_night(is_night(_minutes));
        _set_fade(fade_frames);

        // Create the big streamed layers before the HUD so they get the charblock-aligned VRAM.
        _load_map(start_map, start_x, start_y, facing);
        _deposit.top_up(_rng);          // new game (Continue overwrites this from the save)
        _hud_bg = bn::regular_bg_items::hud.create_bg(0, 0);
        _hud_bg->set_priority(hud_priority);
        _sync_objective();
        _redraw_hud_text();

        // Build date at the top left for a few seconds, so the owner can check which ROM is running.
        _version_label.set(ui::font9, 4, 11, "build " __DATE__ " " __TIME__, ui::role::hud_clock);

        // Need bars: one sprite per need over the dark bar slots of the HUD background.
        for(int need = 0; need < hud_slots; ++need)
        {
            bn::sprite_ptr bar = bn::sprite_items::hud_bar.create_sprite(-46 + (need * 30), 151 + 4 - 80);
            bar.set_bg_priority(0);
            _bar_sprites.push_back(bn::move(bar));

            // "+" / "-" marker above the right end of the slot (shown by _update_pm)
            bn::sprite_ptr pm = bn::sprite_items::ui_icons.create_sprite(-46 + (need * 30) + 9, 128 - 80 - 1, 5);
            pm.set_bg_priority(0);
            pm.set_z_order(39);
            pm.set_visible(false);
            _pm_sprites.push_back(bn::move(pm));
        }

        _update_bars();
        _fade_counter = fade_frames;
        _state = state::fading_in;
    }

    void field::_set_fade(int counter)
    {
        bn::fixed intensity = bn::fixed(counter) / fade_frames;
        bn::bg_palettes::set_fade(bn::color(0, 0, 0), intensity);
        bn::sprite_palettes::set_fade(bn::color(0, 0, 0), intensity);
    }

    void field::_load_map(map_id id, int x, int y, direction facing)
    {
        _map = &get_map(id);
        _floor_bg.reset();
        _objects_bg.reset();
        _floor_bg.emplace(0, _map->floor, _map->image_width, _map->image_height, floor_priority);
        _objects_bg.emplace(1, _map->objects, _map->image_width, _map->image_height, objects_priority,
                            front_priority);
        _pan_mode = 0;
        _lead_x = 0;            // instant camera snap after a warp
        _lead_y = 0;
        _player.place(*_map, x, y, facing);
        _critters.load(*_map);
        _map_id = id;
        _npcs.load(*_map, id, _day, _minutes);
        _player.set_blockers(_npcs.blockers(), _npcs.count());
        _story_check_due = true;
        _update_gates();
        _deposit.load(*_map);
        _map_sprites.load(*_map);
        _collect.load(*_map);
        _pool_sprites.clear();
        _car_clear();
        _map_story_state();
        _update_lighting(true);
        _update_camera();
    }

    int field::_npc_index(npc_id who) const
    {
        for(int index = 0; index < _npcs.count(); ++index)
        {
            if(_npcs.id_of(index) == who)
            {
                return index;
            }
        }

        return -1;
    }

    void field::begin_black()
    {
        _state = state::playing;
        _fade_counter = fade_frames;
        _fade_target = fade_frames;
        _set_fade(fade_frames);
        _set_hud_hidden(true);
    }

    void field::_update_camera()
    {
        // Centre the player in the play area above the HUD, but stay inside the map's view bounds.
        constexpr int view_width = 240;
        constexpr int view_height = 160 - hud_height;
        int min_x = _map->view_x0;
        int max_x = _map->view_x1 - view_width;
        int min_y = _map->view_y0;
        int max_y = _map->view_y1 - view_height;
        _update_focus();

        // Smooth follow: the camera leads a little in the walking direction. The lead is an eased offset that is added
        // to the player's rounded position, so the player and the background always move in whole-pixel lockstep (no 1 px wobble).
        bn::fixed want_lead_x = 0;
        bn::fixed want_lead_y = 0;

        // Owner (s74): the moving camera lead was distracting, so it is off; the camera stays centred on the player.
        constexpr bool camera_lead = false;

        if(camera_lead && _pan_mode == 0)
        {
            want_lead_x = clamp_fixed(_player.screen_vx() * 9, -22, 22);
            want_lead_y = clamp_fixed(_player.screen_vy() * 9, -12, 12);
        }

        _lead_x += (want_lead_x - _lead_x) * bn::fixed(0.07);
        _lead_y += (want_lead_y - _lead_y) * bn::fixed(0.07);
        int target_x = _focus_x - (view_width / 2) + _lead_x.round_integer();
        int target_y = _focus_y - (view_height / 2) + _lead_y.round_integer();
        _cam_x = min_x <= max_x ? clamp(target_x, min_x, max_x) : (min_x + max_x) / 2;
        _cam_y = min_y <= max_y ? clamp(target_y, min_y, max_y) : (min_y + max_y) / 2;

        if(_cam_x < 0)
        {
            _cam_x = 0;
        }

        if(_cam_y < 0)
        {
            _cam_y = 0;
        }

        _floor_bg->set_view(_cam_x, _cam_y);
        _objects_bg->set_view(_cam_x, _cam_y);
        _car_update();
        _player.update_sprite(_cam_x, _cam_y);
        if(! _conversation.active())        // s76: the critters' frame changes churn sprite tile blocks; frozen during talks (VRAM fragmentation)
        {
            _critters.update(_player.x(), _player.y(), _cam_x, _cam_y);
        }

        _npcs.update(_cam_x, _cam_y);
        _deposit.update(*_map, _cam_x, _cam_y);
        _map_sprites.update(*_map, _cam_x, _cam_y);
        _collect.update(*_map, _cam_x, _cam_y);

        int x0, y0, x1, y1, depth;
        _player.mask_area(x0, y0, x1, y1, depth);
        _objects_bg->update_front(x0, y0, x1, y1, depth);
        _update_lamps();
    }

    void field::_update_lighting(bool force)
    {
        ++_water_phase;

        if(! force && (_water_phase % lighting_frames) != 0)
        {
            return;
        }

        if(force || _light_minutes != _minutes)
        {
            _light_minutes = _minutes;
            _light = lighting_at(_minutes, _map->outdoor);
            _player.set_lighting(_light);
            _npcs.set_lighting(_light);
            _critters.set_lighting(_light);
            _deposit.set_lighting(_light);
            _map_sprites.set_lighting(_light);
            _collect.set_lighting(_light);

            bool lamps_on = _map->outdoor && _light.night >= 128;

            if(force || lamps_on != _lamps_on)
            {
                _lamps_on = lamps_on;

                // Day: the player's shadow darkens the ground (50 % alpha). Night: semi-transparent
                // sprites add light (top weight 0.5, bottom 1): pools glow, shadows vanish.
                if(lamps_on)
                {
                    bn::blending::set_transparency_top_weight(0.55);
                    bn::blending::set_transparency_bottom_weight(1);
                }
                else
                {
                    bn::blending::set_transparency_alpha(0.5);
                    _pool_sprites.clear();
                }
            }
        }

        light_layer(_map->floor, lit_floor, _light, _water_phase);
        light_layer(_map->objects, lit_objects, _light, _water_phase);
        _floor_bg->set_palette_colours(lit_floor);
        _objects_bg->set_palette_colours(lit_objects);
    }

    void field::_update_lamps()
    {
        if(! _lamps_on)
        {
            return;
        }

        int used = 0;

        for(int index = 0; index < _map->lamps_count && used < _pool_sprites.max_size(); ++index)
        {
            const lamp& l = _map->lamps[index];
            int sx = _map->to_image_x(l.x, l.y) - _cam_x;
            int sy = _map->to_image_y(l.x, l.y) - _cam_y;

            if(sx < -40 || sx > 280 || sy < -24 || sy > 128 + 24)
            {
                continue;
            }

            if(used == _pool_sprites.size())
            {
                bn::sprite_ptr pool = bn::sprite_items::light_pool.create_sprite(0, 0);
                pool.set_bg_priority(3);
                pool.set_blending_enabled(true);
                pool.set_z_order(2);
                _pool_sprites.push_back(bn::move(pool));
            }

            _pool_sprites[used].set_position(sx - 120, sy - 80);
            ++used;
        }

        while(_pool_sprites.size() > used)
        {
            _pool_sprites.pop_back();
        }
    }

    void field::_redraw_hud_text()
    {
        if(_hud_hidden)
        {
            return;         // the HUD text stays away while a dialogue / cutscene covers it
        }

        ui::set_night(is_night(_minutes));
        int hours = (_minutes / 60) % 24;
        int minutes = _minutes % 60;
        bool pm = hours >= 12;
        int display_hours = hours % 12 == 0 ? 12 : hours % 12;

        bn::string<16> money("$");
        money.append(bn::to_string<10>(_money));

        // HUD panel: clock on the upper half, money (gold) on the lower half; bold 11 px digits, small am/pm
        bn::string<8> clock_digits;
        clock_digits.append(bn::to_string<4>(display_hours));
        clock_digits.append(':');

        if(minutes < 10)
        {
            clock_digits.append('0');
        }

        clock_digits.append(bn::to_string<4>(minutes));
        // two-digit hours do not fit the panel at 11 px: use the 9 px digits then
        // s73: the right-hand labels (am/pm, weekday) end at x 58 at the latest (the Hunger slot starts at 62)
        const char* day_text = weekday_short(_day);
        int side_width = bn::max(ui::text_width(ui::font9, pm ? "pm" : "am"), ui::text_width(ui::font9, day_text));
        const ui::font_data& clock_font = ui::text_width(ui::font11, clock_digits) + 1 + side_width > 40 ? ui::font9 : ui::font11;
        _clock_label.set(clock_font, 10, 141, clock_digits, ui::role::hud_clock);
        int small_x = 10 + ui::text_width(clock_font, clock_digits) + 1;
        _clock_small_label.set(ui::font9, small_x, 139, pm ? "pm" : "am", ui::role::hud_clock);
        _day_label.set(ui::font9, small_x, 148, day_text, ui::role::hud_clock);
        _money_label.set(ui::font11, 10, 156, money, ui::role::hud_money);
    }

    void field::_tick_minute()
    {
        _minutes = (_minutes + 1) % (24 * 60);

        if(_minutes == 0)
        {
            ++_day;
        }

        ++_total_minutes;
        _needs.minute_passed();
        _odd_refresh();
        _update_great(true);
        _update_health_minute();
        _npcs.refresh(_day, _minutes);
        _player.set_blockers(_npcs.blockers(), _npcs.count());
        _story_check_due = true;

        if(_minutes == topup_minute)
        {
            _topup_pickups();
        }

        if(_needs.values[needs::bladder] < 1 && ! _accident_pending)
        {
            _handle_accident();
        }
    }

    void field::_handle_accident()
    {
        _accident_pending = true;
        _needs.add(needs::hygiene, -30);
        _needs.add(needs::fun, -10);
        _needs.values[needs::bladder] = 60;
    }

    void field::_update_clock()
    {
        player::activity act = _player.current_activity();
        int frames_per_minute = frames_per_game_minute;

        if(act == player::activity::sleeping)
        {
            frames_per_minute = _sleep == sleep_kind::bench ? frames_per_game_minute_asleep : frames_per_game_minute_bed;
        }

        if(++_minute_frames >= frames_per_minute)
        {
            _minute_frames = 0;
            _tick_minute();

            if(act == player::activity::sitting)
            {
                _needs.add(needs::fun, sit_fun);
                _needs.add(needs::energy, sit_energy);
            }
            else if(act == player::activity::sleeping)
            {
                bn::fixed gain = _sleep == sleep_kind::night ? bed_energy :
                                 (_sleep == sleep_kind::nap ? nap_energy : sleep_energy);
                _needs.add(needs::energy, gain - needs::decay[needs::energy]);
                _needs.add(needs::hunger, -needs::decay[needs::hunger] / 2);    // hunger slows down asleep
                ++_sleep_minutes;

                if(_sleep == sleep_kind::bench)
                {
                    _needs.add(needs::hygiene, -0.03);          // a night outdoors
                    _needs.add(needs::fun, _sleep_minutes == 300 ? -10 : 0);        // "stiff back" after five hours

                    // the sleeper wakes at Energy 100 or at 7:30, but never before four hours
                    if(_sleep_minutes >= 240 && (_needs.values[needs::energy] >= 100 || _minutes == 7 * 60 + 30))
                    {
                        _player.wake();
                    }
                }

                if((_sleep == sleep_kind::night && _needs.values[needs::energy] >= 100) ||
                   (_sleep == sleep_kind::nap && _sleep_minutes >= nap_minutes))
                {
                    _player.wake();         // rested: _finish_sleep() runs on the next update
                }
            }

            _redraw_hud_text();
            _update_bars();
        }
    }

    void field::_begin_activity(int frames)
    {
        _act = activity_state();
        _act.active = true;
        _act.frames = frames;
    }

    void field::_update_activity()
    {
        if(! _act.active)
        {
            return;
        }

        bool finished = _player.action_finished();
        bool cancelled = ! finished && _player.current_activity() == player::activity::walking;
        _act.done = finished ? _act.frames : (_act.done + 1 < _act.frames ? _act.done + 1 : _act.frames);

        for(int need = 0; need < needs::count; ++need)
        {
            if(_act.gain[need] != 0)
            {
                bn::fixed target = _act.gain[need] * _act.done / _act.frames;
                bn::fixed change = target - _act.applied[need];

                if(need == needs::fun && change > 0 && _needs.social < 20)
                {
                    change /= 2;        // lonely: Fun comes slower
                }

                _needs.add(need, change);
                _act.applied[need] = target;
            }
        }

        if(_act.extra_minutes)
        {
            int due = _act.extra_minutes * _act.done / _act.frames;

            while(_act.extra_done < due)
            {
                ++_act.extra_done;
                _tick_minute();
            }

            _redraw_hud_text();
        }

        _update_bars();

        if(finished || cancelled)
        {
            _act.active = false;

            if(finished && _act.money)
            {
                _money += _act.money;
                _redraw_hud_text();
            }

            if(finished && _act.odd_bit)
            {
                _odd_mask |= uint8_t(_act.odd_bit);

                if(_act.odd_bit == 4)
                {
                    _odd_mask &= uint8_t(~8);       // crates taken -> done
                }

                _sync_objective();
            }

            if(finished && _act.pickup >= 0)
            {
                _deposit.collect(_act.pickup);
            }

            if(finished && _act.climb_dest && _climb_manhole)
            {
                _begin_descent(*_climb_manhole);
            }

            if(finished && _act.collectible >= 0)
            {
                _collectible_found(_act.collectible);
            }

            if(finished && _act.message)
            {
                _menu_mode = menu_mode::none;
                _show_info(_act.title, _info_line_a.c_str(), _info_line_b.c_str(), _info_line_c.c_str());
            }
        }
    }

    void field::_update_pm()
    {
        for(int slot = 0; slot < hud_slots; ++slot)
        {
            bn::sprite_ptr& pm = _pm_sprites[slot];
            int& timer = _needs.pm_timer[slot];

            if(timer > 0)
            {
                --timer;
            }

            if(timer <= 0 || _hud_hidden)
            {
                pm.set_visible(false);
                continue;
            }

            int bob = (timer / 6) % 2;        // 1 px bob
            pm.set_tiles(bn::sprite_items::ui_icons.tiles_item(), _needs.pm_sign[slot] > 0 ? 5 : 6);
            pm.set_y(128 - 80 - 1 - bob);
            pm.set_visible(true);
        }
    }

    void field::_update_bars()
    {
        for(int need = 0; need < hud_slots; ++need)
        {
            bn::fixed value = need < needs::count ? _needs.values[need] : _needs.social;
            int level = (value * (bar_levels - 1) / 100).round_integer();

            if(level != _bar_levels[need])
            {
                _bar_levels[need] = level;
                _bar_sprites[need].set_tiles(bn::sprite_items::hud_bar.tiles_item(), level);
            }
        }
    }

    const interactable* field::_find_target() const
    {
        // nearest usable object in reach of the player's feet
        const interactable* best = nullptr;
        int best_distance = 0;
        int px = _player.x();
        int py = _player.y();

        for(int index = 0; index < _map->interactables_count; ++index)
        {
            const interactable& it = _map->interactables[index];
            int reach = interact_reach;

            if((it.kind == interactable_kind::gate && ! story().flag(story_flag::vault_scene)) ||
               (it.kind == interactable_kind::crate && ! (story().flag(story_flag::pimm_scene) && ! story().flag(story_flag::has_rye) &&
                                                          ! story().flag(story_flag::rye_delivered))))
            {
                continue;
            }

            if(it.kind == interactable_kind::fountain)
            {
                reach = it.radius + fountain_reach;
            }
            else if(it.kind == interactable_kind::seat || it.kind == interactable_kind::seat_x ||
                    it.kind == interactable_kind::bed || it.kind == interactable_kind::desk ||
                    it.kind == interactable_kind::window || it.kind == interactable_kind::wardrobe)
            {
                reach = fixture_reach + it.radius;      // radius = extra reach (the player stands beside the seat)
            }
            else if(it.kind != interactable_kind::bench)
            {
                reach = fixture_reach;
            }

            int d2 = distance2(px, py, it.x, it.y);

            if(d2 <= reach * reach && (! best || d2 < best_distance))
            {
                best = &it;
                best_distance = d2;
            }
        }

        return best;
    }

    int field::_find_npc(int& d2) const
    {
        return _npcs.find(_player.x(), _player.y(), npc_reach, d2);
    }

    int field::_find_pickup(int& d2) const
    {
        int spot_d2 = 0;
        int spot = _deposit.find(_player.x(), _player.y(), pickup_reach, spot_d2);
        int item_d2 = 0;
        int item = _collect.find(_player.x(), _player.y(), pickup_reach, item_d2);

        if(item >= 0 && (spot < 0 || item_d2 <= spot_d2))
        {
            d2 = item_d2;
            return 100 + item;          // a collectible (s64)
        }

        d2 = spot_d2;
        return spot;
    }

    void field::_update_cue()
    {
        // The bobbing "A" bubble over the nearest object or pickup in reach (only while walking, no menu, no activity).
        const interactable* target = _find_target();
        int pickup_d2 = 0;
        int pickup = _find_pickup(pickup_d2);

        if(pickup >= 0 && target && distance2(_player.x(), _player.y(), target->x, target->y) <= pickup_d2)
        {
            pickup = -1;        // the fixture is closer
        }

        int npc_d2 = 0;
        int npc = _find_npc(npc_d2);

        if(npc >= 0 && ((target && distance2(_player.x(), _player.y(), target->x, target->y) < npc_d2) ||
                        (pickup >= 0 && pickup_d2 < npc_d2)))
        {
            npc = -1;       // something else is closer
        }

        if(npc >= 0)
        {
            target = nullptr;
            pickup = -1;
        }

        if(! target && pickup < 0 && npc < 0)
        {
            _cue.reset();
            _cue_faced = -1;
            return;
        }

        int height;
        int cue_x = 0;
        int cue_y = 0;

        if(npc >= 0)
        {
            height = 64;
            cue_x = _npcs.x_of(npc);
            cue_y = _npcs.y_of(npc);
        }
        else if(pickup >= 0)
        {
            height = 12;
            cue_x = pickup >= 100 ? collect_spots[pickup - 100].x : pickup_spots[pickup].x;
            cue_y = pickup >= 100 ? collect_spots[pickup - 100].y : pickup_spots[pickup].y;
        }
        else
        {
            cue_x = target->x;
            cue_y = target->y;
            height = 38;

            switch(target->kind)
            {
            case interactable_kind::bench:
                height = 22;
                break;

            case interactable_kind::seat:
            case interactable_kind::seat_x:
                height = 26;
                break;

            case interactable_kind::fountain:
                height = 36;
                break;

            case interactable_kind::bookshelf:
            case interactable_kind::noticeboard:
            case interactable_kind::window:
                height = 46;
                break;

            case interactable_kind::bed:
                height = 36;
                break;

            case interactable_kind::desk:
                height = 34;
                break;

            case interactable_kind::wardrobe:
                height = 66;
                break;

            case interactable_kind::bin:
            case interactable_kind::sink:
            case interactable_kind::reception:
                height = 40;
                break;

            case interactable_kind::deposit:
                height = 54;
                break;

            case interactable_kind::manhole:
                height = 22;
                break;

            case interactable_kind::ladder:
                height = 46;
                break;

            default:      // toilet, shop counters
                height = 38;
                break;
            }
        }

        // s71 control feel: standing still with the cue showing, the player turns to face what it points at (once per target).
        int face_key = npc >= 0 ? 10000 + npc : (pickup >= 0 ? 20000 + pickup : int(target - _map->interactables) + 1);

        if(face_key != _cue_faced && _player.standing_still())
        {
            _cue_faced = face_key;
            _player.face_towards(cue_x, cue_y);
        }

        static constexpr int bob[4] = { 0, 1, 2, 1 };
        ++_cue_frame;
        int sx = _map->to_image_x(cue_x, cue_y) - _cam_x;
        int sy = _map->to_image_y(cue_x, cue_y) - _cam_y - height - bob[(_cue_frame / 8) % 4];

        if(sy < 18)
        {
            sy = 18;
        }

        if(! _cue)
        {
            _cue = ui::make_cue(sx, sy);
        }
        else
        {
            ui::place_cue(*_cue, sx, sy);
        }
    }

    void field::_open_interaction_menu()
    {
        const interactable* best = _find_target();
        int pickup_d2 = 0;
        int pickup = _find_pickup(pickup_d2);

        int npc_d2 = 0;
        int npc = _find_npc(npc_d2);
        int best_d2 = best ? distance2(_player.x(), _player.y(), best->x, best->y) : 0x7FFFFFFF;

        if(pickup >= 0 && pickup_d2 < best_d2)
        {
            best_d2 = pickup_d2;
        }

        if(npc >= 0 && npc_d2 <= best_d2)
        {
            _start_conversation(npc);
            return;
        }

        if(pickup >= 0 && (! best || pickup_d2 < distance2(_player.x(), _player.y(), best->x, best->y)))
        {
            _pick_up(pickup);
            return;
        }

        if(! best)
        {
            return;
        }

        ui::set_night(is_night(_minutes));
        _menu_target = best;
        _menu_mode = menu_mode::interact;

        if(best->kind != interactable_kind::bench && best->kind != interactable_kind::seat &&
           best->kind != interactable_kind::seat_x && best->kind != interactable_kind::bed)
        {
            _player.face_towards(best->x, best->y);     // using something: look at it
        }

        switch(best->kind)
        {

        case interactable_kind::bench:
            {
                static constexpr bn::string_view options[] = { "Sit", "Sleep" };
                _menu.open("Park Bench", options, 2);
            }
            break;

        case interactable_kind::fountain:
            {
                static constexpr bn::string_view options[] = { "Wash face", "Drink water" };
                _menu.open("Fountain", options, 2);
            }
            break;

        case interactable_kind::shop_market:
        case interactable_kind::shop_diner:
        case interactable_kind::shop_bakery:
        case interactable_kind::shop_lane:
        case interactable_kind::shop_stall:
            if(best->kind == interactable_kind::shop_market && _map_id == map_id::vaultmart)
            {
                // the robot voice of the self-checkout kiosk
                _shop_return = best;
                _show_info("VaultMart", "Welcome to VaultMart.", "Have a nice day.", "Next customer.");
            }
            else
            {
                _open_shop(*best);
            }
            break;

        case interactable_kind::kiosk:
            _open_kiosk(*best);
            break;

        case interactable_kind::seat:
        case interactable_kind::seat_x:
            _menu.open("Seat", seat_options, 1);
            break;

        case interactable_kind::toilet:
            _menu.open("Toilet", toilet_options, 1);
            break;

        case interactable_kind::sink:
            _menu.open("Sink", sink_options, 2);
            break;

        case interactable_kind::bookshelf:
            _menu.open("Bookshelf", book_options, 1);
            break;

        case interactable_kind::bin:
            _menu.open("Trash bin", bin_options, 1);
            break;

        case interactable_kind::deposit:
            _open_deposit_menu();
            break;

        case interactable_kind::noticeboard:
            _open_board(*best);
            break;

        case interactable_kind::reception:
            _menu_mode = menu_mode::none;
            _menu_target = nullptr;
            _show_info("VaultTech", "Access denied.", "Have a nice day.", "");
            break;

        case interactable_kind::bed:
            _menu.open("Bed", bed_options, 3);
            break;

        case interactable_kind::shower:
            _menu.open("Shower", shower_menu_options, 2);
            break;

        case interactable_kind::clinic:
            _open_clinic_menu(*best);
            break;

        case interactable_kind::couch:
            _menu_mode = menu_mode::none;
            _menu_target = nullptr;
            _show_info("Exam couch", "Paper roll, fresh", "sheet. Dr. Okafor's", "patients rest here.");
            break;

        case interactable_kind::desk:
            _menu.open("Desk", desk_options, 2);
            break;

        case interactable_kind::window:
            _menu_mode = menu_mode::none;
            _menu_target = nullptr;
            _show_window();
            break;

        case interactable_kind::wardrobe:
            _menu_mode = menu_mode::none;
            _menu_target = nullptr;
            _show_info("Wardrobe", "Work shirts, jeans...", "and a green apron.", "");
            break;

        case interactable_kind::gate:
            _menu_mode = menu_mode::none;
            _menu_target = nullptr;
            _show_info("VaultTech", "STAFF ONLY.", "VaultMart property.", "");
            break;

        case interactable_kind::crate:
            _menu_mode = menu_mode::none;
            _menu_target = nullptr;
            story().set_flag(story_flag::has_rye, 1);
            _sync_objective();
            _show_info("Storeroom", "You carry the rye loaf.", "Take it to Mr. Pimm.", "");
            break;

        case interactable_kind::manhole:
        case interactable_kind::ladder:
            _use_sewer(*best);
            break;

        case interactable_kind::sign:
        case interactable_kind::flap:
        case interactable_kind::hatch:
        case interactable_kind::chess:
        case interactable_kind::garden:
        case interactable_kind::hoop:
        case interactable_kind::washer:
        case interactable_kind::oven:
            _menu_mode = menu_mode::none;
            _menu_target = nullptr;
            _use_old_block(*best);
            break;

        default:
            _menu_mode = menu_mode::none;
            _menu_target = nullptr;
            break;
        }
    }

    void field::_open_shop(const interactable& target)
    {
        _menu_target = &target;
        _menu_mode = menu_mode::shop;

        // The shop menu also offers a chat with the person behind the counter (if somebody is in reach), and at the diner the job.
        static bn::string_view options[menu::max_options];
        static bn::string_view voucher_label = "Coffee (voucher)";
        static bn::string_view shift_label = "Work a shift";
        const shop_set& set = shop_for(target.kind, _map_id);
        bool cold = set.gift_count == 0;
        int count = set.count;

        for(int index = 0; index < count; ++index)
        {
            options[index] = set.labels[index];
        }

        if(set.diner && story().flag(story_flag::has_coffee_voucher) && ! story().flag(story_flag::voucher_used))
        {
            options[0] = voucher_label;
        }

        _shop_has_shift = set.diner && story().flag(story_flag::diner_job);

        if(_shop_has_shift)
        {
            options[count++] = shift_label;
        }

        int d2 = 0;
        _shop_npc = _npcs.find(_player.x(), _player.y(), 48, d2);
        _shop_talk_index = -1;
        _shop_gift_index = -1;
        int limit = (cold ? menu::max_options : menu::max_options - 1);

        if(_shop_npc >= 0 && count < limit)
        {
            _talk_label = "Talk to ";
            _talk_label.append(npc_infos[int(_npcs.id_of(_shop_npc))].name);
            _shop_talk_index = count;
            options[count++] = _talk_label;
        }
        else
        {
            _shop_npc = -1;
        }

        if(! cold)
        {
            static bn::string_view gifts_label = "Gifts";
            _shop_gift_index = count;
            options[count++] = gifts_label;
        }

        _shop_items = set.count;
        _menu.open(set.title, options, count);
    }

    void field::_show_info(const char* title, const char* line_a, const char* line_b, const char* line_c)
    {
        // The message lines must outlive the open menu: keep them in static views.
        static bn::string_view lines[3];
        static bn::string_view heading;
        heading = title;
        lines[0] = line_a;
        lines[1] = line_b;
        lines[2] = line_c;
        int count = line_c[0] ? 3 : (line_b[0] ? 2 : 1);
        _menu.open_info(heading, lines, count);
        _menu_mode = menu_mode::info;
    }

    // Gifts sold per shop (docs/features_backlog.md): gift index into gift_defs (Flowers, Chocolate, Hot sauce, Cookies, Newspaper).
    void field::_open_gift_shop(const interactable& target)
    {
        static bn::string_view options[4];
        const shop_set& set = shop_for(target.kind, _map_id);
        const int* ids = set.gifts;
        _gift_offer = set.gift_count;

        for(int index = 0; index < _gift_offer; ++index)
        {
            _gift_ids[index] = ids[index];
            _gift_labels[index] = gift_defs[ids[index]].name;
            _gift_labels[index].append(" $");
            _gift_labels[index].append(bn::to_string<4>(gift_defs[ids[index]].price));
            options[index] = _gift_labels[index];
        }

        _menu_target = &target;
        _menu_mode = menu_mode::gifts;
        _menu.open("Gifts", options, _gift_offer);
    }

    void field::_buy_gift(const interactable& target, int choice)
    {
        _shop_return = &target;

        if(choice < 0 || choice >= _gift_offer)
        {
            _shop_return = nullptr;
            _open_shop(target);
            return;
        }

        int gift = _gift_ids[choice];

        if(_money < gift_defs[gift].price)
        {
            _show_info("Gifts", "Not enough", "money.", "");
            return;
        }

        if(story().item_count(gift) >= 9)
        {
            _show_info("Gifts", "You cannot carry", "any more of those.", "");
            return;
        }

        _money -= gift_defs[gift].price;
        story().add_item(gift);
        _redraw_hud_text();
        _info_line_a = "You bought ";
        _info_line_a.append(gift_defs[gift].name);
        _info_line_a.append(".");
        _show_info("Gifts", _info_line_a.c_str(), "Give it in a chat:", "\"Give a gift\".");
    }

    void field::_open_kiosk(const interactable& target)
    {
        static constexpr bn::string_view options[] = { "Scratch card $1", "Newspaper $1" };
        _menu_target = &target;
        _menu_mode = menu_mode::kiosk;
        _menu.open("Newsagent", options, 2);
    }

    void field::_kiosk_choice(const interactable& target, int choice)
    {
        _shop_return = nullptr;

        if(choice == 0)
        {
            _scratch_card(target);
        }
        else if(choice == 1)
        {
            if(_money < 1)
            {
                _show_info("Newsagent", "Not enough", "money.", "");
            }
            else if(story().item_count(4) >= 9)
            {
                _show_info("Newsagent", "You cannot carry", "any more papers.", "");
            }
            else
            {
                _money -= 1;
                story().add_item(4);
                _redraw_hud_text();
                _show_info("Newsagent", "You bought a", "newspaper.", "A gift for Mr. Pimm?");
            }
        }
    }

    // Scratch card: $1, three symbols; 70 % nothing, 20 % $2, 8 % $5, 2 % $20; at most 3 a day.
    void field::_scratch_card(const interactable&)
    {
        if(story().scratch_left(_day) <= 0)
        {
            _show_info("Scratch card", "Sold out for today.", "Come back tomorrow.", "");
            return;
        }

        if(_money < 1)
        {
            _show_info("Scratch card", "Not enough", "money.", "");
            return;
        }

        _money -= 1;
        story().note_scratch(_day);
        int roll = _rng.get_unbiased_int(100);
        int prize = roll < 70 ? 0 : (roll < 90 ? 2 : (roll < 98 ? 5 : 20));
        static constexpr char symbols[] = { '*', '$', '7', '#', '+' };
        int win_symbol = prize == 2 ? 0 : (prize == 5 ? 1 : 2);
        char s[3];

        if(prize)
        {
            s[0] = s[1] = s[2] = symbols[win_symbol];
        }
        else
        {
            s[0] = symbols[_rng.get_unbiased_int(5)];
            s[1] = symbols[_rng.get_unbiased_int(5)];
            s[2] = symbols[_rng.get_unbiased_int(5)];

            if(s[0] == s[1] && s[1] == s[2])
            {
                s[2] = symbols[(win_symbol + 3) % 5 == 0 ? 1 : 3];
            }
        }

        _info_line_a = "[ ";
        _info_line_a.append(s[0]);
        _info_line_a.append(" ]  [ ");
        _info_line_a.append(s[1]);
        _info_line_a.append(" ]  [ ");
        _info_line_a.append(s[2]);
        _info_line_a.append(" ]");

        if(prize)
        {
            _money += prize;
            _info_line_b = "Three of a kind!";
            _info_line_c = "You win $";
            _info_line_c.append(bn::to_string<4>(prize));
            _info_line_c.append("!");
        }
        else
        {
            _info_line_b = "No luck this time.";
            _info_line_c = "";
        }

        _redraw_hud_text();
        _show_info("Scratch card", _info_line_a.c_str(), _info_line_b.c_str(), _info_line_c.c_str());
    }

    void field::_buy(const interactable& target, int choice)
    {
        const shop_set& set = shop_for(target.kind, _map_id);
        shop_item item = set.items[choice];
        bool voucher = set.diner && choice == 0 && story().flag(story_flag::has_coffee_voucher) && ! story().flag(story_flag::voucher_used);

        if(voucher)
        {
            item.price = 0;
        }

        if(_money < item.price)
        {
            _shop_return = &target;
            _show_info("Shop", "Not enough", "money.", "");
            return;
        }

        // Pay, then eat right away: the needs fill gradually during the eating animation.
        _money -= item.price;

        if(voucher)
        {
            story().set_flag(story_flag::voucher_used, 1);
        }

        _note_evening(true, false);
        _redraw_hud_text();
        int frames = 100 + (5 * (item.hunger + item.energy)) + (20 * item.quality);
        _begin_activity(frames > 360 ? 360 : frames);
        _act.gain[needs::hunger] = item.hunger;
        _act.gain[needs::energy] = item.energy;
        _act.gain[needs::fun] = item.fun;
        _act.gain[needs::bladder] = item.bladder;

        if(item.bladder < 0)
        {
            _needs.bladder_boost = bladder_boost_minutes;
        }

        _player.start_action(player::action_kind::eat, _player.x(), _player.y(), _act.frames);
    }

    void field::_use_toilet(const interactable& target)
    {
        bn::fixed missing = 100 - _needs.values[needs::bladder];

        if(missing < 8)
        {
            _show_info("Toilet", "You don't need", "to go right now.", "");
            return;
        }

        int quality = target.quality < 1 ? 1 : (target.quality > 3 ? 3 : target.quality);
        int frames = (missing * toilet_full_frames[quality - 1] / 100).round_integer();
        _begin_activity(frames < 90 ? 90 : frames);
        _act.gain[needs::bladder] = missing;
        // the seat is a bit behind the spot where you stand (the toilet stands against the back wall)
        _player.sit_for(target.x, target.y - 14, _act.frames);
    }

    void field::_search_bin(const interactable& target)
    {
        int index = int(&target - _map->interactables);
        int slot = (int(_map - &get_map(map_id(0))) * 16) + (index & 15);

        if(_bin_emptied[slot] && _total_minutes + 1 - _bin_emptied[slot] < bin_cooldown)
        {
            _show_info("Trash bin", "Someone already", "emptied this bin.", "");
            return;
        }

        _bin_emptied[slot] = _total_minutes + 1;
        _info_line_c = "";
        _player.approach(target.x, target.y, 13);
        _begin_activity(search_frames);
        int roll = _rng.get_unbiased_int(100);

        if(roll < 30)
        {
            // food scraps (docs/story_chapter1.md 4.7): half a sandwich 60 %, a stale roll 25 %, a bruised apple 15 %
            int kind = _rng.get_unbiased_int(100);
            int hunger = kind < 60 ? 12 : (kind < 85 ? 8 : 5);
            _act.gain[needs::hunger] = hunger;
            _act.gain[needs::hygiene] = -hunger;
            _info_line_a = kind < 60 ? "You found half a" : (kind < 85 ? "You found a stale" : "You found a");
            _info_line_b = kind < 60 ? "sandwich." : (kind < 85 ? "roll." : "bruised apple.");
            _note_evening(true, false);
        }
        else if(roll < 50)
        {
            int amount = 1 + _rng.get_unbiased_int(3);
            _act.money = amount;
            _act.gain[needs::hygiene] = -5;
            _info_line_a = "You found $";
            _info_line_a.append(bn::to_string<4>(amount));
            _info_line_a.append('!');
            _info_line_b = "";
        }
        else if(roll < 55)
        {
            _act.money = 5;
            _act.gain[needs::hygiene] = -5;
            _info_line_a = "A lost coin purse!";
            _info_line_b = "$5 inside.";
        }
        else
        {
            _act.gain[needs::hygiene] = -5;
            _info_line_a = "Nothing useful.";
            _info_line_b = "";
        }

        _act.message = true;
        _player.start_action(player::action_kind::search, target.x, target.y, _act.frames);
    }

    namespace
    {
        // "$2" for a number of items (every can / bottle is worth exactly $1)
        void append_dollars(bn::string<24>& text, int dollars)
        {
            text.append('$');
            text.append(bn::to_string<8>(dollars));
        }

        void append_items(bn::string<24>& text, int cans, int bottles)
        {
            text.append(bn::to_string<4>(cans));
            text.append(cans == 1 ? " can, " : " cans, ");
            text.append(bn::to_string<4>(bottles));
            text.append(bottles == 1 ? " bottle" : " bottles");
        }
    }

    void field::_topup_pickups()
    {
        _deposit.top_up(_rng);
    }

    void field::_pick_up(int spot)
    {
        if(spot >= 100)
        {
            _pick_collectible(spot - 100);
            return;
        }

        if(_deposit.bag_total() >= deposit::bag_max)
        {
            _info_line_a = "You can't carry any";
            _info_line_b = "more (";
            _info_line_b.append(bn::to_string<4>(_deposit.bag_total()));
            _info_line_b.append("/");
            _info_line_b.append(bn::to_string<4>(deposit::bag_max));
            _info_line_b.append("). Take it");
            _info_line_c = "to the machine.";
            _show_info("Bag full", _info_line_a.c_str(), _info_line_b.c_str(), _info_line_c.c_str());
            return;
        }

        const pickup_spot& place = pickup_spots[spot];
        bool bottle = _deposit.is_bottle(spot);
        _player.approach(place.x, place.y, 12);
        _begin_activity(pickup_frames);
        _act.pickup = spot;
        _act.gain[needs::energy] = bn::fixed(-0.5);
        _act.gain[needs::hygiene] = place.bush ? -2 : -1;
        _act.message = true;
        _act.title = "Picked up";
        _info_line_a = bottle ? "Picked up a bottle." : "Picked up a can.";
        _info_line_b = "Bag ";
        _info_line_b.append(bn::to_string<4>(_deposit.bag_total() + 1));
        _info_line_b.append("/");
        _info_line_b.append(bn::to_string<4>(deposit::bag_max));
        _info_line_c = "";
        _player.start_action(player::action_kind::pickup, place.x, place.y, _act.frames);
    }

    void field::_open_deposit_menu()
    {
        static bn::string_view options[3];
        _deposit_label = "Return all (";
        _deposit_label.append(bn::to_string<4>(_deposit.bag_total()));
        _deposit_label.append(")");
        options[0] = _deposit_label;
        options[1] = "Check bag";
        options[2] = "Leave";
        _menu.open("Return & Earn", options, 3);
    }

    void field::_deposit_choice(int choice)
    {
        if(choice == 0)
        {
            if(_deposit.bag_total() == 0)
            {
                _show_info("Return & Earn", "Your bag is empty.", "Collect cans and", "bottles around town.");
                return;
            }

            int cans = _deposit.bag_cans;
            int bottles = _deposit.bag_bottles;
            int paid = _deposit.return_all();
            _money += paid;
            _redraw_hud_text();
            _info_line_a = "";
            append_items(_info_line_a, cans, bottles);
            _info_line_a.append(":");
            _info_line_b = "You get $";
            _info_line_b.append(bn::to_string<8>(paid));
            _info_line_b.append(".");
            _info_line_c = "Thanks!";

            _show_info("Return & Earn", _info_line_a.c_str(), _info_line_b.c_str(), _info_line_c.c_str());
        }
        else if(choice == 1)
        {
            _info_line_a = "In the bag: ";
            _info_line_a.append(bn::to_string<4>(_deposit.bag_total()));
            _info_line_a.append("/");
            _info_line_a.append(bn::to_string<4>(deposit::bag_max));
            _info_line_b = "Worth ";
            append_dollars(_info_line_b, _deposit.bag_credits());
            _info_line_c = "";
            _show_info("Return & Earn", _info_line_a.c_str(), _info_line_b.c_str(), _info_line_c.c_str());
        }
    }

    void field::_handle_menu_choice(int choice)
    {
        const interactable* target = _menu_target;
        menu_mode mode = _menu_mode;
        _menu_mode = menu_mode::none;

        if(mode == menu_mode::info)
        {
            const interactable* back = _shop_return;
            _shop_return = nullptr;
            _menu_target = nullptr;

            if(back)
            {
                _open_shop(*back);
            }

            return;
        }

        _menu_target = nullptr;

        if(target && choice < 0 && mode == menu_mode::gifts)
        {
            _open_shop(*target);        // B in the gift list goes back to the shop
            return;
        }

        if(! target || choice < 0)
        {
            return;
        }

        if(mode == menu_mode::gifts)
        {
            _buy_gift(*target, choice);
            return;
        }

        if(mode == menu_mode::kiosk)
        {
            _kiosk_choice(*target, choice);
            return;
        }

        if(mode == menu_mode::board)
        {
            if(choice < 3)
            {
                _board_choice(choice);
            }

            return;
        }

        if(mode == menu_mode::shop)
        {
            int items = _shop_items;

            if(_shop_has_shift && choice == items)
            {
                _try_start_shift();
                return;
            }

            if(choice == _shop_gift_index)
            {
                _open_gift_shop(*target);
                return;
            }

            if(choice >= items)
            {
                if(choice == _shop_talk_index && _shop_npc >= 0 && _shop_npc < _npcs.count())
                {
                    _start_conversation(_shop_npc);
                }

                return;
            }

            _buy(*target, choice);
            return;
        }

        if(target->kind == interactable_kind::deposit)
        {
            _deposit_choice(choice);
            return;
        }

        if(target->kind == interactable_kind::shower)
        {
            if(choice == 0)
            {
                _use_shower(*target);
            }

            return;
        }

        if(target->kind == interactable_kind::clinic)
        {
            _clinic_choice(choice);
            return;
        }

        if(target->kind == interactable_kind::manhole || target->kind == interactable_kind::ladder)
        {
            _sewer_choice(*target, choice);
            return;
        }

        switch(target->kind)
        {

        case interactable_kind::bench:
            _rest_target = target;

            if(choice == 0)
            {
                _player.sit_on(target->x, target->y);
            }
            else
            {
                _sleep = sleep_kind::bench;
                _sleep_minutes = 0;
                story().set_flag(story_flag::slept_on_bench, 1);
                _player.sleep_on(target->x, target->y);
            }
            break;

        case interactable_kind::seat:
        case interactable_kind::seat_x:
            _rest_target = target;
            _player.sit_on(target->x, target->y, target->kind == interactable_kind::seat_x);
            break;

        case interactable_kind::bed:
            if(choice > 1)
            {
                break;
            }

            if(_needs.values[needs::energy] >= 90)
            {
                _show_info("Bed", "You're not tired.", "", "");
                break;
            }

            _rest_target = target;
            _sleep = choice == 0 ? sleep_kind::night : sleep_kind::nap;
            _sleep_minutes = 0;
            _player.sleep_on(target->x, target->y, bed_lift);
            break;

        case interactable_kind::desk:
            if(choice == 0)
            {
                _begin_activity(read_frames);
                _act.gain[needs::fun] = read_fun[0];
                _act.extra_minutes = read_minutes;
                _player.start_action(player::action_kind::read, target->x, target->y, _act.frames);
            }
            else
            {
                _show_notes();
            }
            break;

        case interactable_kind::fountain:
            _player.approach(target->x, target->y, target->radius + 6);

            if(choice == 0)
            {
                _note_evening(false, true);
                _begin_activity(wash_face_frames);
                _act.gain[needs::hygiene] = wash_face_hygiene;
                _player.start_action(player::action_kind::wash, target->x, target->y, _act.frames);
            }
            else
            {
                _begin_activity(drink_frames);
                _act.gain[needs::hygiene] = -6;
                _act.gain[needs::energy] = 3;
                _act.gain[needs::bladder] = -15;
                _needs.bladder_boost = bladder_boost_minutes;
                _player.start_action(player::action_kind::drink, target->x, target->y, _act.frames);
            }
            break;

        case interactable_kind::toilet:
            _use_toilet(*target);
            break;

        case interactable_kind::sink:
            _player.approach(target->x, target->y, 12);        // stand at the basin, facing it

            if(choice == 0)
            {
                _note_evening(false, true);
                _begin_activity(wash_hands_frames);
                _act.gain[needs::hygiene] = wash_hands_hygiene;
                _player.start_action(player::action_kind::wash, target->x, target->y, _act.frames);
            }
            else
            {
                _begin_activity(drink_frames);
                _act.gain[needs::energy] = 3;
                _act.gain[needs::bladder] = -15;
                _needs.bladder_boost = bladder_boost_minutes;
                _player.start_action(player::action_kind::drink, target->x, target->y, _act.frames);
            }
            break;

        case interactable_kind::bookshelf:
            {
                int quality = target->quality < 1 ? 1 : (target->quality > 3 ? 3 : target->quality);
                _begin_activity(read_frames);
                _act.gain[needs::fun] = read_fun[quality - 1];
                _act.extra_minutes = read_minutes;
                _player.start_action(player::action_kind::read, target->x, target->y, _act.frames);
            }
            break;

        case interactable_kind::bin:
            _search_bin(*target);
            break;

        default:
            break;
        }
    }

    // The player got up (rested, or woke himself with B / D-pad): after a good night, offer to save.
    void field::_finish_sleep()
    {
        sleep_kind kind = _sleep;
        int minutes = _sleep_minutes;
        _sleep = sleep_kind::none;
        _sleep_minutes = 0;

        if(kind == sleep_kind::night && minutes >= 30)
        {
            ui::set_night(is_night(_minutes));
            _open_dialog(3);
        }
        else if(kind == sleep_kind::nap && minutes >= nap_minutes)
        {
            _show_info("Bed", "You feel refreshed.", "", "");
        }
        else if(kind == sleep_kind::bench && minutes >= 30 && ! story().flag(story_flag::read_newspaper))
        {
            story().set_flag(story_flag::news_due, 1);      // the newspaper scene (cutscenes_src.txt: news_day2)
        }
    }

    // "Check notes" on the desk: the current objective, word-wrapped into three short lines.
    void field::_show_notes()
    {
        _sync_objective();
        bn::string<24>* lines[3] = { &_info_line_a, &_info_line_b, &_info_line_c };

        for(bn::string<24>* line : lines)
        {
            line->clear();
        }

        int index = 0;
        const char* text = _objective.c_str();
        int length = int(_objective.size());
        int pos = 0;

        while(pos < length && index < 3)
        {
            int end = pos + 22;

            if(end >= length)
            {
                end = length;
            }
            else
            {
                while(end > pos && text[end] != ' ')
                {
                    --end;
                }

                if(end == pos)
                {
                    end = pos + 22;
                }
            }

            for(int k = pos; k < end; ++k)
            {
                lines[index]->push_back(text[k]);
            }

            pos = end;

            while(pos < length && text[pos] == ' ')
            {
                ++pos;
            }

            ++index;
        }

        _show_info("Notes", _info_line_a.c_str(), _info_line_b.c_str(), _info_line_c.c_str());
    }

    // Looking out of the window: depends on the time of day (later also on the story).
    void field::_show_window()
    {
        int hour = (_minutes / 60) % 24;

        if(hour >= 6 && hour < 11)
        {
            _show_info("Window", "Mia is opening the", "shutters down below.", "A new day.");
        }
        else if(hour >= 11 && hour < 18)
        {
            _show_info("Window", "People hurry along the", "avenue. The VaultTech", "tower glints.");
        }
        else if(hour >= 18 && hour < 22)
        {
            _show_info("Window", "The lamps come on", "along the avenue.", "Home, sweet home.");
        }
        else
        {
            _show_info("Window", "The city sleeps. Only", "the golden tower is", "still lit.");
        }
    }

    void field::_update_zzz()
    {
        if(_player.current_activity() != player::activity::sleeping || ! _rest_target)
        {
            _zzz_label.clear();
            return;
        }

        static int phase = 0;
        ++phase;

        if(_zzz_label.empty() || phase % 40 == 0)
        {
            int sx = _map->to_image_x(_rest_target->x, _rest_target->y) - _cam_x;
            int sy = _map->to_image_y(_rest_target->x, _rest_target->y) - _cam_y;
            int rise = (phase / 40) % 3;
            _zzz_label.set(ui::font9, sx - 18, sy - 30 - (rise * 3), rise == 0 ? "z" : (rise == 1 ? "zZ" : "zZz"),
                           ui::role::hud_clock);
        }
    }

    void field::_set_hud_hidden(bool hidden)
    {
        if(hidden == _hud_hidden)
        {
            return;
        }

        _hud_hidden = hidden;

        if(hidden)
        {
            // the dialogue box covers the HUD: free its text sprites (128 sprite budget) and hide the need bars
            _clock_label.clear();
            _clock_small_label.clear();
            _money_label.clear();
            _day_label.clear();
            _version_label.clear();
            _version_frames = 0;
        }

        for(bn::sprite_ptr& bar : _bar_sprites)
        {
            bar.set_visible(! hidden);
        }

        if(hidden)
        {
            _mail_icon.reset();
            _sick_icon.reset();
        }

        if(! hidden)
        {
            _redraw_hud_text();
        }
    }

    void field::_start_conversation(int npc_index)
    {
        int npc = int(_npcs.id_of(npc_index));
        int nx = _npcs.x_of(npc_index);
        int ny = _npcs.y_of(npc_index);
        _player.face_towards(nx, ny);
        _npcs.face_towards(npc_index, _player.x(), _player.y());
        _npcs.focus(npc_index);
        // s76: free every ambient world sprite while talking: the small-talk choice layout (96 px portrait, meter, options) needs a lot of
        // sprite VRAM in contiguous blocks, and Rosa's stall / Old Block ran out of it ("Sprite tiles allocate failed"). Restored in _end_conversation.
        _critters.clear();
        _deposit.clear();
        _collect.clear();
        _map_sprites.clear();
        _player.set_blockers(_npcs.blockers(), _npcs.count());
        npc_index = 0;
        story().set_crates_open(_crates_open());
        _set_hud_hidden(true);
        ui::set_night(is_night(_minutes));
        story().set_flag(story_flag::hyg_ok, _needs.values[needs::hygiene] >= 40 ? 1 : 0);   // Lou: "you smell like a bench"

        if(! npc_infos[npc].talks)
        {
            // cast members without small talk only bark one line
            int node = npc == int(npc_id::dex_vault) ? dlg::bark_dex_vault :
                    (npc == int(npc_id::victor) ? dlg::bark_victor : dlg::bark_robot);
            _conversation.start_script(node, -1);
        }
        else if(npc == int(npc_id::pimm) && story().flag(story_flag::has_rye) && ! story().flag(story_flag::rye_delivered))
        {
            _conversation.start_script(dlg::pro_pimm_deliver, npc);
        }
        else if(npc == int(npc_id::pimm) && story().flag(story_flag::pimm_scene) && ! story().flag(story_flag::rye_delivered))
        {
            _conversation.start_script(dlg::pro_pimm_wait, npc);
        }
        else
        {
            _conversation.start_talk(npc, _day, _minutes);
        }
    }

    void field::_end_conversation()
    {
        int npc = _conversation.partner();
        _npcs.reset_facings();
        _npcs.unfocus();
        _critters.load(*_map);
        _deposit.load(*_map);
        _collect.load(*_map);
        _map_sprites.load(*_map);
        _critters.set_lighting(_light);
        _deposit.set_lighting(_light);
        _collect.set_lighting(_light);
        _set_hud_hidden(false);
        _money += story().take_money();
        _needs.add_social(story().take_social());
        _redraw_hud_text();
        _npcs.refresh(_day, _minutes);
        _player.set_blockers(_npcs.blockers(), _npcs.count());
        _handle_story_events(npc);

        if(story().flag(story_flag::lou_shift_go))
        {
            story().set_flag(story_flag::lou_shift_go, 0);
            _try_start_shift();
        }

        if(story().flag(story_flag::crates_go))
        {
            story().set_flag(story_flag::crates_go, 0);
            _start_crates();
        }
    }

    void field::_sync_objective()
    {
        if(! _objective_override)
        {
            _objective = story().objective();
            _sync_objective_dynamic();
        }
    }

    // Checks the current mission and shows what changed (a system page in the dialogue box).
    void field::_handle_story_events(int talked_npc)
    {
        story_context context;
        context.day = _day;
        context.minutes = _minutes;
        context.money = _money;
        context.map = int(_map_id);
        context.talked_npc = talked_npc;
        int completed = 0;
        int reward = 0;

        for(int guard = 0; guard < 4; ++guard)
        {
            int id = story().check_mission(context);

            if(! id)
            {
                break;
            }

            completed = id;
            reward += mission_defs[id - 1].reward_money;
            context.talked_npc = -1;
        }

        int extra = story().take_completed();       // finished by a dialogue effect

        if(! completed)
        {
            completed = extra;
        }

        (void)story().take_started();
        int money = story().take_money();
        _money += money;
        _story_check_due = false;
        _sync_objective();

        if(money)
        {
            _redraw_hud_text();
        }

        if(! completed)
        {
            return;
        }

        _story_text = "Mission complete: ";
        _story_text.append(mission_defs[completed - 1].title);
        _story_text.append(".");

        if(reward > 0)
        {
            _story_text.append(" Reward: $");
            _story_text.append(bn::to_string<8>(reward));
            _story_text.append(".");
        }

        if(story().mission())
        {
            _story_text.append(" New goal: ");
            _story_text.append(mission_defs[story().mission() - 1].objective);
        }

        _set_hud_hidden(true);
        ui::set_night(is_night(_minutes));
        _conversation.start_message(_story_text.c_str());
    }

    void field::update()
    {
        switch(_state)
        {

        case state::fading_in:
            if(_fade_counter == fade_frames && ! _script.active && _pause_mode == pause_mode::none)
            {
                _early_pan();
            }

            --_fade_counter;
            _set_fade(_fade_counter);

            if(_fade_counter <= 0)
            {
                _state = state::playing;
            }
            break;

        case state::playing:
            _rng.update();      // the outcome of random events depends on when the player acts
            _update_gates();

            if(_version_frames > 0 && --_version_frames == 0)
            {
                _version_label.clear();
            }

            if(_pause_mode != pause_mode::none)
            {
                _cue.reset();
                _update_pause();
                break;
            }

            if(_conversation.active())
            {
                // s73: a pop-up message must never sit on top of an open menu (the menu would be frozen under it)
                if(_menu.is_open())
                {
                    _menu.close();
                }

                // the world stands still (also the clock) while somebody talks
                _cue.reset();
                _update_camera();
                _update_lighting(false);

                if(_conversation.update())
                {
                    if(_script.active)
                    {
                        _script_dialogue_done();
                    }
                    else if(_conversation.is_message())
                    {
                        _set_hud_hidden(false);
                    }
                    else
                    {
                        _end_conversation();
                    }
                }

                break;
            }

            if(_script.active)
            {
                _update_script();
                break;
            }

            if(_phone_open)
            {
                _cue.reset();
                _update_phone();
                _update_camera();
                _update_clock();
                _update_lighting(false);
                break;
            }

            if(_menu.is_open())
            {
                _cue.reset();
                int choice = _menu.update();

                if(choice != menu::open_still)
                {
                    _handle_menu_choice(choice);
                }

                _update_camera();
                _update_clock();
                _update_lighting(false);
                break;
            }

            if(_can_pause())
            {
                // cutscene triggers first, so a scene is not interrupted by "Mission complete" pages (they follow it)
                _check_triggers();

                if(_script.active)
                {
                    break;
                }

                if(_minigame_pending)
                {
                    break;
                }

                // s64: fainting (a need stayed empty for an hour), the first "you feel sick" message, deliveries, bill reminders
                if(_faint_pending)
                {
                    _faint_pending = false;
                    _start_script(script_id::faint);
                    break;
                }

                if(_sick_msg_pending)
                {
                    _sick_msg_pending = false;
                    _set_hud_hidden(true);
                    ui::set_night(is_night(_minutes));
                    _conversation.start_script(dlg::sick_intro, -1);
                    break;
                }

                _try_delivery();

                if(_act.active)
                {
                    break;
                }

                _check_bill_reminder();

                if(_conversation.active())
                {
                    break;
                }

                if(const char* text = take_pending_message())
                {
                    _set_hud_hidden(true);
                    ui::set_night(is_night(_minutes));
                    _conversation.start_message(text);
                    break;
                }

                if(_hint_cooldown > 0)
                {
                    --_hint_cooldown;
                }
                else
                {
                    _check_need_hints();

                    if(_conversation.active())
                    {
                        _hint_cooldown = 120;
                        break;
                    }
                }
            }

            if(_story_check_due && _can_pause())
            {
                _handle_story_events(-1);

                if(_conversation.active())
                {
                    break;
                }
            }

            _npcs.wander(_player.x(), _player.y(), -1);

            if(bn::keypad::start_pressed() && _can_pause())
            {
                _cue.reset();
                _toast_clear();
                _open_pause();
                break;
            }

            if(bn::keypad::select_pressed() && _can_pause())
            {
                _toast_clear();
                _open_phone();
                break;
            }

            _update_hud_icons();
            _update_pm();
            _update_flyers();
            _update_toast();

            if(_player.current_activity() == player::activity::walking && bn::keypad::a_pressed())
            {
                _open_interaction_menu();

                if(_menu.is_open() || _conversation.active())
                {
                    _cue.reset();
                    _toast_clear();
                    break;
                }
            }

#ifdef TL_DEBUG_TELEPORT
            if(bn::keypad::l_pressed())
            {
                _player.debug_toggle();
            }

            if(bn::keypad::r_pressed())
            {
                _player.debug_toggle2();
            }

            if(bn::keypad::select_pressed())
            {
                static int debug_index = 0;
                #include "tl_debug_points.h"
                constexpr int debug_count = sizeof(debug_points) / sizeof(debug_points[0]);
                const debug_point& point = debug_points[debug_index++ % debug_count];

                _player.place(*_map, int(point.x * cell_size), int(point.y * cell_size), direction::down);
            }
#endif
            _player.update();

            if(_sleep != sleep_kind::none && _player.current_activity() != player::activity::sleeping)
            {
                _finish_sleep();
            }

            _update_activity();

            if(_accident_pending && ! _act.active && ! _menu.is_open() &&
               _player.current_activity() == player::activity::walking)
            {
                _accident_pending = false;
                _show_info("Oops...", "You couldn't", "hold it.", "");
                _update_bars();
            }

            if(_player.current_activity() == player::activity::walking)
            {
                _rest_target = nullptr;
            }

            _update_zzz();
            _update_camera();
            _update_clock();
            _update_lighting(false);

            if(_player.current_activity() == player::activity::walking && ! _act.active && ! _menu.is_open())
            {
                _update_cue();
            }
            else
            {
                _cue.reset();
            }

            _pending_warp = _map->warp_at(_player.x(), _player.y());

            if(_climb_go)
            {
                // s77: the crouch at a manhole is over: go down into the sewer (_begin_descent)
                _climb_go = false;
                _pending_warp = &_climb_warp;
            }

            if(_pending_warp && _pending_warp->target == map_id::corner_market && story().flag(story_flag::vault_scene))
            {
                // after the firing the shop door leads into VaultMart (the cold, regimented Corner Market)
                _redirect_warp = *_pending_warp;
                _redirect_warp.target = map_id::vaultmart;
                _pending_warp = &_redirect_warp;
            }

            if(_pending_warp && _pending_warp->target == map_id::player_room && story().flag(story_flag::vault_scene))
            {
                // the room above the shop is VaultTech property now (the shutter gate is down)
                _pending_warp = nullptr;

                if(_gate_cooldown <= 0)
                {
                    _gate_cooldown = 150;
                    _show_info("VaultTech", "STAFF ONLY.", "VaultMart property.", "");
                }
            }

            if(_gate_cooldown > 0)
            {
                --_gate_cooldown;
            }

            if(_pending_warp)
            {
                _state = state::fading_out;
                _fade_counter = 0;
            }
            break;

        case state::fading_out:
            _cue.reset();
            ++_fade_counter;
            _set_fade(_fade_counter);

            if(_fade_counter >= fade_frames)
            {
                // Free the old layers now; Butano releases their VRAM during the next core update,
                // so the new map is created one frame later.
                _objects_bg.reset();
                _floor_bg.reset();
                _state = state::loading;
            }
            break;

        case state::loading:
            {
                const warp& w = *_pending_warp;
                _pending_warp = nullptr;
                _load_map(w.target, w.target_x, w.target_y, w.facing);
                _state = state::fading_in;

                if(_climb_arrive == 1)
                {
                    // arriving in the sewer: the player climbs down the ladder while the screen fades in
                    _climb_arrive = 0;
                    _begin_climb_down();
                }
                else if(_climb_arrive == 2)
                {
                    // climbed out of a manhole: the sewer leaves its mark
                    _climb_arrive = 0;
                    _player.set_visible(true);
                    _needs.add(needs::hygiene, -3);
                    _update_bars();
                }
            }
            break;

        case state::climbing:
            _update_climb();
            break;

        default:
            break;
        }

#ifdef TL_DEBUG_POS
        // s73 headless tests: a state dump that tools/drv.py finds in a savestate by its magic
        {
            dbg_state.magic[0] = 'T'; dbg_state.magic[1] = 'L'; dbg_state.magic[2] = 'D'; dbg_state.magic[3] = 'B';
            dbg_state.x = _player.x();
            dbg_state.y = _player.y();
            dbg_state.map = int(_map_id);
            dbg_state.day = _day;
            dbg_state.minutes = _minutes;
            dbg_state.money = _money;
            dbg_state.mission = story().mission();
            dbg_state.menu = _menu.is_open() ? 1 : 0;
            dbg_state.conv = _conversation.active() ? 1 : 0;
            dbg_state.act = _act.active ? 1 : 0;
            dbg_state.script = _script.active ? 1 : 0;
            dbg_state.state = int(_state);
            dbg_state.frame = dbg_state.frame + 1;

            for(int i = 0; i < 80; ++i)
            {
                dbg_state.flags[i] = (unsigned char)story().flag(i);
            }

            for(int i = 0; i < 5; ++i)
            {
                dbg_state.needs[i] = _needs.values[i].round_integer();
            }

            for(int i = 0; i < 20; ++i)
            {
                dbg_state.friends[i] = story().friendship(i);
            }
        }
#endif
    }
}
