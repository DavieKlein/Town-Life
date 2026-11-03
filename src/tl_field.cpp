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
#include "common_variable_8x8_sprite_font.h"

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

        // Effects per game minute while resting.
        constexpr bn::fixed sit_fun = 0.35;
        constexpr bn::fixed sit_energy = 0.15;
        constexpr bn::fixed sleep_energy = 0.5;
        constexpr bn::fixed wash_hygiene = 35;

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

    field::field(map_id start_map, int start_x, int start_y, direction facing) :
        _text_generator(common::variable_8x8_sprite_font),
        _menu(_text_generator)
    {
        _text_generator.set_bg_priority(hud_priority);
        _set_fade(fade_frames);

        // Create the big streamed layers before the HUD so they get the charblock-aligned VRAM.
        _load_map(start_map, start_x, start_y, facing);
        _hud_bg = bn::regular_bg_items::hud.create_bg(0, 0);
        _hud_bg->set_priority(hud_priority);
        _redraw_hud_text();

        // Need bars: one sprite per need over the dark bar slots of the HUD background.
        for(int need = 0; need < needs::count; ++need)
        {
            bn::sprite_ptr bar = bn::sprite_items::need_bar.create_sprite(77 + (need * 42) + 16 - 120, 151 + 4 - 80);
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
        int hours = (_minutes / 60) % 24;
        int minutes = _minutes % 60;
        bool pm = hours >= 12;
        int display_hours = hours % 12 == 0 ? 12 : hours % 12;

        bn::string<16> clock;
        clock.append(bn::to_string<4>(display_hours));
        clock.append(':');

        if(minutes < 10)
        {
            clock.append('0');
        }

        clock.append(bn::to_string<4>(minutes));
        clock.append(pm ? " pm" : " am");

        bn::string<16> money("$");
        money.append(bn::to_string<10>(_money));

        _clock_sprites.clear();
        _money_sprites.clear();
        _text_generator.set_left_alignment();
        _text_generator.generate(-112, 56, clock, _clock_sprites);
        _text_generator.generate(-112, 71, money, _money_sprites);
    }

    void field::_update_clock()
    {
        player::activity act = _player.current_activity();
        int frames_per_minute = act == player::activity::sleeping ? frames_per_game_minute_asleep :
                                                                    frames_per_game_minute;

        if(++_minute_frames >= frames_per_minute)
        {
            _minute_frames = 0;
            _minutes = (_minutes + 1) % (24 * 60);
            _needs.minute_passed();

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

    void field::_update_bars()
    {
        for(int need = 0; need < needs::count; ++need)
        {
            int level = (_needs.values[need] * (bar_levels - 1) / 100).round_integer();
            _bar_sprites[need].set_tiles(bn::sprite_items::need_bar.tiles_item(), level);
        }
    }

    void field::_open_interaction_menu()
    {
        // nearest usable object in reach of the player's feet
        const interactable* best = nullptr;
        int best_distance = 0;
        int px = _player.x();
        int py = _player.y();

        for(int index = 0; index < _map->interactables_count; ++index)
        {
            const interactable& it = _map->interactables[index];
            int reach = it.kind == interactable_kind::fountain ? it.radius + fountain_reach : interact_reach;
            int d2 = distance2(px, py, it.x, it.y);

            if(d2 <= reach * reach && (! best || d2 < best_distance))
            {
                best = &it;
                best_distance = d2;
            }
        }

        if(! best)
        {
            return;
        }

        _menu_target = best;

        if(best->kind == interactable_kind::bench)
        {
            constexpr bn::string_view options[] = { "Sit", "Sleep" };
            _menu.open("Park Bench", options, 2);
        }
        else
        {
            constexpr bn::string_view options[] = { "Wash face" };
            _menu.open("Fountain", options, 1);
        }
    }

    void field::_handle_menu_choice(int choice)
    {
        const interactable* target = _menu_target;
        _menu_target = nullptr;

        if(! target || choice < 0)
        {
            return;
        }

        if(target->kind == interactable_kind::bench)
        {
            _rest_target = target;

            if(choice == 0)
            {
                _player.sit_on(target->x, target->y);
            }
            else
            {
                _player.sleep_on(target->x, target->y);
            }
        }
        else
        {
            _player.start_washing(target->x, target->y);
        }
    }

    void field::_update_zzz()
    {
        if(_player.current_activity() != player::activity::sleeping || ! _rest_target)
        {
            _zzz_sprites.clear();
            return;
        }

        static int phase = 0;
        ++phase;

        if(_zzz_sprites.empty() || phase % 40 == 0)
        {
            _zzz_sprites.clear();
            int sx = _map->to_image_x(_rest_target->x, _rest_target->y) - _cam_x - 120;
            int sy = _map->to_image_y(_rest_target->x, _rest_target->y) - _cam_y - 80;
            int rise = (phase / 40) % 3;
            _text_generator.set_left_alignment();
            _text_generator.generate(sx - 18, sy - 34 - (rise * 3), rise == 0 ? "z" : (rise == 1 ? "zZ" : "zZz"),
                                     _zzz_sprites);
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
            if(_menu.is_open())
            {
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

            if(_player.current_activity() == player::activity::walking && bn::keypad::a_pressed())
            {
                _open_interaction_menu();

                if(_menu.is_open())
                {
                    break;
                }
            }

            _player.update();

            if(_player.washing_finished())
            {
                _needs.add(needs::hygiene, wash_hygiene);
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
            _pending_warp = _map->warp_at(_player.x(), _player.y());

            if(_pending_warp)
            {
                _state = state::fading_out;
                _fade_counter = 0;
            }
            break;

        case state::fading_out:
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
