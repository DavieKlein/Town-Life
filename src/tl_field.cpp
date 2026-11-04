#include "tl_field.h"

#include "bn_color.h"
#include "bn_string.h"
#include "bn_bg_palettes.h"
#include "bn_sprite_palettes.h"

#include "bn_keypad.h"
#include "bn_regular_bg_items_hud.h"
#include "bn_blending.h"
#include "bn_sprite_items_need_bar.h"
#include "bn_sprite_items_light_pool.h"

#include "tl_deposit_spots.h"

namespace tl
{
    namespace
    {
        constexpr int fade_frames = 12;
        constexpr int frames_per_game_minute = 60;     // 1 real second = 1 game minute
        constexpr int frames_per_game_minute_asleep = 4;   // time flies while sleeping
        constexpr int bar_levels = 16;                 // frames in need_bar.bmp
        constexpr int interact_reach = 26;             // world units from a bench seat
        constexpr int fountain_reach = 32;             // world units beyond the fountain radius
        constexpr int fixture_reach = 28;              // counters, toilets, sinks, shelves, ...
        constexpr int pickup_reach = 20;               // cans and bottles lying on the ground
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
        constexpr bn::string_view diner_labels[] = { "Coffee $2", "Pancakes $4", "Burger $6" };
        constexpr shop_item diner_items[] = {
            { 2, 2, 0, 15, 5, -10 }, { 4, 2, 25, 8, 0, 0 }, { 6, 3, 40, 12, 0, 0 } };
        constexpr bn::string_view toilet_options[] = { "Use toilet" };
        constexpr bn::string_view bin_options[] = { "Search the bin" };
        constexpr bn::string_view sink_options[] = { "Wash hands" };
        constexpr bn::string_view book_options[] = { "Read a book" };
        constexpr bn::string_view seat_options[] = { "Sit down" };

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
        constexpr bn::fixed sleep_energy = 0.5;
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
        _redraw_hud_text();

        // Build date at the top left for a few seconds, so the owner can check which ROM is running.
        _version_label.set(ui::font9, 4, 11, "build " __DATE__ " " __TIME__, ui::role::hud_clock);

        // Need bars: one sprite per need over the dark bar slots of the HUD background.
        for(int need = 0; need < needs::count; ++need)
        {
            bn::sprite_ptr bar = bn::sprite_items::need_bar.create_sprite(-48 + (need * 37), 151 + 4 - 80);
            bar.set_bg_priority(0);
            _bar_sprites.push_back(bn::move(bar));
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
        _player.place(*_map, x, y, facing);
        _critters.load(*_map);
        _npcs.load(*_map);
        _deposit.load(*_map);
        _pool_sprites.clear();
        _update_lighting(true);
        _update_camera();
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
        int target_x = _player.focus_x() - (view_width / 2);
        int target_y = _player.focus_y() - (view_height / 2);
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
        _player.update_sprite(_cam_x, _cam_y);
        _critters.update(_player.x(), _player.y(), _cam_x, _cam_y);
        _npcs.update(_cam_x, _cam_y);
        _deposit.update(*_map, _cam_x, _cam_y);

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
            _critters.set_lighting(_light);
            _deposit.set_lighting(_light);

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
        const ui::font_data& clock_font = ui::text_width(ui::font11, clock_digits) + 2 +
                ui::text_width(ui::font9, "am") > 47 ? ui::font9 : ui::font11;
        _clock_label.set(clock_font, 13, 141, clock_digits, ui::role::hud_clock);
        _clock_small_label.set(ui::font9, 13 + ui::text_width(clock_font, clock_digits) + 2, 141, pm ? "pm" : "am",
                               ui::role::hud_clock);
        _money_label.set(ui::font11, 13, 156, money, ui::role::hud_money);
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
        int frames_per_minute = act == player::activity::sleeping ? frames_per_game_minute_asleep :
                                                                    frames_per_game_minute;

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
                _needs.add(needs::energy, sleep_energy - needs::decay[needs::energy]);
                _needs.add(needs::hunger, -needs::decay[needs::hunger] / 2);    // hunger slows down asleep
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
                _needs.add(need, target - _act.applied[need]);
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

            if(finished && _act.pickup >= 0)
            {
                _deposit.collect(_act.pickup);
            }

            if(finished && _act.message)
            {
                _menu_mode = menu_mode::none;
                _show_info(_act.title, _info_line_a.c_str(), _info_line_b.c_str(), _info_line_c.c_str());
            }
        }
    }

    void field::_update_bars()
    {
        for(int need = 0; need < needs::count; ++need)
        {
            int level = (_needs.values[need] * (bar_levels - 1) / 100).round_integer();

            if(level != _bar_levels[need])
            {
                _bar_levels[need] = level;
                _bar_sprites[need].set_tiles(bn::sprite_items::need_bar.tiles_item(), level);
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

            if(it.kind == interactable_kind::fountain)
            {
                reach = it.radius + fountain_reach;
            }
            else if(it.kind == interactable_kind::seat || it.kind == interactable_kind::seat_x)
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

    int field::_find_pickup(int& d2) const
    {
        return _deposit.find(_player.x(), _player.y(), pickup_reach, d2);
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

        if(! target && pickup < 0)
        {
            _cue.reset();
            return;
        }

        int height;
        int cue_x = 0;
        int cue_y = 0;

        if(pickup >= 0)
        {
            height = 12;
            cue_x = pickup_spots[pickup].x;
            cue_y = pickup_spots[pickup].y;
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
                height = 46;
                break;

            case interactable_kind::bin:
            case interactable_kind::sink:
            case interactable_kind::reception:
                height = 40;
                break;

            case interactable_kind::deposit:
                height = 54;
                break;

            default:      // toilet, shop counters
                height = 38;
                break;
            }
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
            _open_shop(*best);
            break;

        case interactable_kind::seat:
        case interactable_kind::seat_x:
            _menu.open("Seat", seat_options, 1);
            break;

        case interactable_kind::toilet:
            _menu.open("Toilet", toilet_options, 1);
            break;

        case interactable_kind::sink:
            _menu.open("Sink", sink_options, 1);
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
            _menu_mode = menu_mode::none;
            _menu_target = nullptr;
            _show_info("Notice board", "No jobs posted", "yet. Check", "back soon!");
            break;

        case interactable_kind::reception:
            _menu_mode = menu_mode::none;
            _menu_target = nullptr;
            _show_info("VaultTech", "Access denied.", "Have a nice day.", "");
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

        if(target.kind == interactable_kind::shop_market)
        {
            _menu.open("Corner Market", market_labels, 4);
        }
        else
        {
            _menu.open("Diner", diner_labels, 3);
        }
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

    void field::_buy(const interactable& target, int choice)
    {
        bool market = target.kind == interactable_kind::shop_market;
        const shop_item& item = market ? market_items[choice] : diner_items[choice];

        if(_money < item.price)
        {
            _shop_return = &target;
            _show_info("Shop", "Not enough", "money.", "");
            return;
        }

        // Pay, then eat right away: the needs fill gradually during the eating animation.
        _money -= item.price;
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

        if(roll < 35)
        {
            _act.gain[needs::hunger] = 12;
            _act.gain[needs::hygiene] = -12;
            _info_line_a = "You found half a";
            _info_line_b = "sandwich.";
        }
        else if(roll < 55)
        {
            int amount = 1 + _rng.get_unbiased_int(3);
            _act.money = amount;
            _act.gain[needs::hygiene] = -5;
            _info_line_a = "You found $";
            _info_line_a.append(bn::to_string<4>(amount));
            _info_line_a.append('!');
            _info_line_b = "";
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
        // "$2" or "$2.50" for a number of credits (2 credits = $1).
        void append_dollars(bn::string<24>& text, int credits)
        {
            text.append('$');
            text.append(bn::to_string<8>(credits / 2));

            if(credits % 2)
            {
                text.append(".50");
            }
            else if(credits == 0)
            {
                text.append(".00");
            }
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
        _player.start_action(player::action_kind::search, place.x, place.y, _act.frames);
    }

    void field::_open_deposit_menu()
    {
        static bn::string_view options[3];
        _deposit_label = "Return all (";
        _deposit_label.append(bn::to_string<4>(_deposit.bag_total()));
        _deposit_label.append(")");
        options[0] = _deposit_label;
        options[1] = "Check credit";
        options[2] = "Leave";
        _menu.open("Return & Earn", options, 3);
    }

    void field::_deposit_choice(int choice)
    {
        if(choice == 0)
        {
            if(_deposit.bag_total() == 0 && _deposit.credit == 0)
            {
                _show_info("Return & Earn", "Your bag is empty.", "Collect cans and", "bottles around town.");
                return;
            }

            int cans = _deposit.bag_cans;
            int bottles = _deposit.bag_bottles;
            int credits = _deposit.bag_credits() + _deposit.credit;
            int paid = _deposit.return_all();
            _money += paid;
            _redraw_hud_text();
            _info_line_a = "";
            append_items(_info_line_a, cans, bottles);
            _info_line_a.append(":");
            _info_line_b = "";

            if(credits % 2)
            {
                append_dollars(_info_line_b, credits);
                _info_line_b.append(" -> $");
                _info_line_b.append(bn::to_string<8>(paid));
                _info_line_b.append(" paid,");
                _info_line_c = "credit 1/2. Thanks!";
            }
            else
            {
                _info_line_b.append("$");
                _info_line_b.append(bn::to_string<8>(paid));
                _info_line_b.append(" paid.");
                _info_line_c = "Thanks!";
            }

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
            _info_line_c = "Credit saved: ";
            _info_line_c.append(bn::to_string<4>(_deposit.credit));
            _info_line_c.append("/2");
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

        if(! target || choice < 0)
        {
            return;
        }

        if(mode == menu_mode::shop)
        {
            _buy(*target, choice);
            return;
        }

        if(target->kind == interactable_kind::deposit)
        {
            _deposit_choice(choice);
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
                _player.sleep_on(target->x, target->y);
            }
            break;

        case interactable_kind::seat:
        case interactable_kind::seat_x:
            _rest_target = target;
            _player.sit_on(target->x, target->y, target->kind == interactable_kind::seat_x);
            break;

        case interactable_kind::fountain:
            _player.approach(target->x, target->y, target->radius + 6);

            if(choice == 0)
            {
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
            _begin_activity(wash_hands_frames);
            _act.gain[needs::hygiene] = wash_hands_hygiene;
            _player.start_action(player::action_kind::wash, target->x, target->y, _act.frames);
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

    void field::update()
    {
        switch(_state)
        {

        case state::fading_in:
            --_fade_counter;
            _set_fade(_fade_counter);

            if(_fade_counter <= 0)
            {
                _state = state::playing;
            }
            break;

        case state::playing:
            _rng.update();      // the outcome of random events depends on when the player acts

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

            if(bn::keypad::start_pressed() && _can_pause())
            {
                _cue.reset();
                _open_pause();
                break;
            }

            if(_player.current_activity() == player::activity::walking && bn::keypad::a_pressed())
            {
                _open_interaction_menu();

                if(_menu.is_open())
                {
                    _cue.reset();
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
            }
            break;

        default:
            break;
        }
    }
}
