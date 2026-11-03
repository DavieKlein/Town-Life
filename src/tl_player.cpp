#include "tl_player.h"

#include "bn_keypad.h"
#include "bn_sprite_items_player.h"

namespace tl
{
    namespace
    {
        constexpr int hitbox_radius = 4;        // world units around the feet

        // Frames in player.bmp (16x32): 0-2 front (facing down-left), 3-5 back (facing up-left).
        constexpr int back_frames = 3;
        constexpr int anim_wait = 8;            // game frames per animation step
        constexpr int walk_cycle[] = { 0, 1, 0, 2 };
    }

    player::player(const bn::camera_ptr& camera) :
        _sprite(bn::sprite_items::player.create_sprite(0, 0))
    {
        _sprite.set_camera(camera);
    }

    void player::place(const map_info& map, int x, int y, direction facing)
    {
        _map = &map;
        _x = x;
        _y = y;
        _direction = facing;
        _anim_counter = 0;
        _update_sprite();
        _update_graphics(false);
    }

    void player::update()
    {
        // D-pad follows the isometric axes: up = up-right, right = down-right, down = down-left,
        // left = up-left. Pressing two directions walks straight across the screen.
        int dx = 0;
        int dy = 0;

        if(bn::keypad::left_held())
        {
            dx = -1;
        }
        else if(bn::keypad::right_held())
        {
            dx = 1;
        }

        if(bn::keypad::up_held())
        {
            dy = -1;
        }
        else if(bn::keypad::down_held())
        {
            dy = 1;
        }

        bool moving = dx != 0 || dy != 0;

        if(moving)
        {
            if(dy > 0)
            {
                _direction = direction::down;
            }
            else if(dy < 0)
            {
                _direction = direction::up;
            }

            if(dx < 0)
            {
                _direction = direction::left;
            }
            else if(dx > 0)
            {
                _direction = direction::right;
            }

            // Hold B to run.
            int steps = bn::keypad::b_held() ? 2 : 1;

            for(int step = 0; step < steps; ++step)
            {
                // Move each axis separately so the player slides along walls.
                if(dx != 0 && ! _map->solid_around(_x + dx, _y, hitbox_radius))
                {
                    _x += dx;
                }

                if(dy != 0 && ! _map->solid_around(_x, _y + dy, hitbox_radius))
                {
                    _y += dy;
                }
            }

            _anim_counter += steps;
        }
        else
        {
            _anim_counter = 0;
        }

        _update_sprite();
        _update_graphics(moving);
    }

    void player::_update_sprite()
    {
        int bg_x = _map->to_bg_x(_x, _y);
        int bg_y = _map->to_bg_y(_x, _y);

        // Butano coordinates: the bg is centred on (0, 0). The sprite is 16x32 with the feet at the bottom.
        _sprite.set_position(bg_x - (_map->bg_width / 2), bg_y - (_map->bg_height / 2) - 15);

        // Behind a building/tree: draw below the objects layer (priority 2), otherwise above it.
        _sprite.set_bg_priority(_map->player_hidden(_x, _y) ? 3 : 2);
    }

    void player::_update_graphics(bool moving)
    {
        int base_frame = 0;
        bool flip = false;

        switch(_direction)
        {

        case direction::down:       // down-left: front view
            break;

        case direction::right:      // down-right: front view mirrored
            flip = true;
            break;

        case direction::left:       // up-left: back view
            base_frame = back_frames;
            break;

        case direction::up:         // up-right: back view mirrored
            base_frame = back_frames;
            flip = true;
            break;

        default:
            break;
        }

        int step = moving ? walk_cycle[(_anim_counter / anim_wait) % 4] : 0;
        _sprite.set_tiles(bn::sprite_items::player.tiles_item(), base_frame + step);
        _sprite.set_horizontal_flip(flip);
    }
}
