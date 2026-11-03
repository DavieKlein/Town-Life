#include "tl_field.h"

#include "bn_color.h"
#include "bn_regular_bg_item.h"
#include "bn_bg_palettes.h"
#include "bn_sprite_palettes.h"

namespace tl
{
    namespace
    {
        constexpr int screen_half_width = 120;
        constexpr int screen_half_height = 80;
        constexpr int fade_frames = 12;

        [[nodiscard]] constexpr int clamp(int value, int min_value, int max_value)
        {
            return value < min_value ? min_value : (value > max_value ? max_value : value);
        }
    }

    field::field(map_id start_map, int start_x, int start_y, direction facing) :
        _camera(bn::camera_ptr::create(0, 0)),
        _player(_camera)
    {
        _set_fade(fade_frames);
        _load_map(start_map, start_x, start_y, facing);
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

        // Release the old background first so its tiles/palette don't have to coexist with the new one.
        _bg.reset();
        _bg = _map->bg_item->create_bg(0, 0);
        _bg->set_camera(_camera);

        _player.place(*_map, x, y, facing);
        _update_camera();
    }

    void field::_update_camera()
    {
        // Keep the camera inside the map so no empty space is shown at the edges.
        int half_w = _map->pixel_width() / 2;
        int half_h = _map->pixel_height() / 2;
        int max_x = half_w - screen_half_width;
        int max_y = half_h - screen_half_height;

        if(max_x < 0)
        {
            max_x = 0;
        }

        if(max_y < 0)
        {
            max_y = 0;
        }

        int x = clamp(_player.map_x() - half_w, -max_x, max_x);
        int y = clamp(_player.map_y() - half_h, -max_y, max_y);
        _camera.set_position(x, y);
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
            _pending_warp = _map->warp_at(_player.feet_x(), _player.feet_y());

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
                const warp& w = *_pending_warp;
                int x = w.target_x == keep_coordinate ? _player.map_x() : w.target_x;
                int y = w.target_y == keep_coordinate ? _player.map_y() : w.target_y;
                _pending_warp = nullptr;
                _load_map(w.target, x, y, w.facing);
                _state = state::fading_in;
            }
            break;

        default:
            break;
        }
    }
}
