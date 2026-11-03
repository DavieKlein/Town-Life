#include "tl_field.h"

#include "bn_color.h"
#include "bn_string.h"
#include "bn_regular_bg_item.h"
#include "bn_bg_palettes.h"
#include "bn_sprite_palettes.h"

#include "bn_regular_bg_items_hud.h"
#include "common_variable_8x8_sprite_font.h"

namespace tl
{
    namespace
    {
        constexpr int fade_frames = 12;
        constexpr int frames_per_game_minute = 60;     // 1 real second = 1 game minute

        // Bg priorities: HUD 0, (player when in front: 2), objects 2, (player when behind: 3), floor 3.
        constexpr int floor_priority = 3;
        constexpr int objects_priority = 2;
        constexpr int hud_priority = 0;

        // Visible play area is the screen minus the 32 px HUD bar at the bottom.
        constexpr int hud_height = 32;

        [[nodiscard]] constexpr int clamp(int value, int min_value, int max_value)
        {
            return value < min_value ? min_value : (value > max_value ? max_value : value);
        }
    }

    field::field(map_id start_map, int start_x, int start_y, direction facing) :
        _camera(bn::camera_ptr::create(0, 0)),
        _hud_bg(bn::regular_bg_items::hud.create_bg(0, 0)),
        _text_generator(common::variable_8x8_sprite_font),
        _player(_camera)
    {
        _hud_bg.set_priority(hud_priority);
        _text_generator.set_bg_priority(hud_priority);
        _set_fade(fade_frames);
        _load_map(start_map, start_x, start_y, facing);
        _redraw_hud_text();
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

        // Release the old layers first so their tiles don't have to coexist with the new ones.
        _objects_bg.reset();
        _floor_bg.reset();
        _floor_bg = _map->floor_item->create_bg(0, 0);
        _floor_bg->set_priority(floor_priority);
        _floor_bg->set_camera(_camera);
        _objects_bg = _map->objects_item->create_bg(0, 0);
        _objects_bg->set_priority(objects_priority);
        _objects_bg->set_camera(_camera);

        _player.place(*_map, x, y, facing);
        _update_camera();
    }

    void field::_update_camera()
    {
        // Centre the player in the visible area above the HUD, but stay inside the map's view bounds.
        int target_x = _map->to_bg_x(_player.x(), _player.y());
        int target_y = _map->to_bg_y(_player.x(), _player.y()) - 15 + (hud_height / 2);

        int min_x = _map->view_x0 + 120;
        int max_x = _map->view_x1 - 120;
        int min_y = _map->view_y0 + 80;
        int max_y = _map->view_y1 - 80 + hud_height;
        int x = min_x <= max_x ? clamp(target_x, min_x, max_x) : (min_x + max_x) / 2;
        int y = min_y <= max_y ? clamp(target_y, min_y, max_y) : (min_y + max_y) / 2;
        _camera.set_position(x - (_map->bg_width / 2), y - (_map->bg_height / 2));
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
        if(++_minute_frames >= frames_per_game_minute)
        {
            _minute_frames = 0;
            _minutes = (_minutes + 1) % (24 * 60);
            _redraw_hud_text();
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
            _player.update();
            _update_camera();
            _update_clock();
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
