#include "tl_player.h"

#include "bn_keypad.h"
#include "bn_blending.h"
#include "bn_sprite_items_player.h"
#include "bn_sprite_items_shadow.h"

namespace tl
{
    namespace
    {
        constexpr int hitbox_radius = 4;        // world units around the feet

        // player.bmp: 32x64 frames rendered from the 3D character, 5 per facing (idle + 4 walk frames),
        // facings in the order down, right, up, left. The feet are at (16, 58) inside each frame.
        constexpr int frames_per_facing = 5;
        constexpr int anim_wait = 7;            // game frames per animation step
        constexpr int feet_offset_y = 58 - 32;  // feet relative to the sprite centre
        constexpr int sprite_half_width = 10;   // body size used for the depth test
        constexpr int sprite_height = 50;
    }

    player::player() :
        _shadow(bn::sprite_items::shadow.create_sprite(0, 0)),
        _sprite(bn::sprite_items::player.create_sprite(0, 0))
    {
        // Soft shadow under the feet: a dark ellipse drawn with 50% alpha blending, behind the player.
        bn::blending::set_transparency_alpha(0.5);
        _shadow.set_blending_enabled(true);
        _shadow.set_z_order(1);
    }

    void player::place(const map_info& map, int x, int y, direction facing)
    {
        _map = &map;
        _x = x;
        _y = y;
        _direction = facing;
        _anim_counter = 0;
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

        _update_graphics(moving);
    }

    void player::update_sprite(int cam_x, int cam_y)
    {
        int image_x = _map->to_image_x(_x, _y);
        int image_y = _map->to_image_y(_x, _y);

        // Screen coordinates are relative to the screen centre.
        int screen_x = image_x - cam_x - 120;
        int screen_y = image_y - cam_y - 80;
        _sprite.set_position(screen_x, screen_y - feet_offset_y);
        _shadow.set_position(screen_x, screen_y - 1);

        // Behind a building/tree: draw below the objects layer (priority 2), otherwise above it.
        int priority = _map->player_hidden(_x, _y, sprite_half_width, sprite_height) ? 3 : 2;
        _sprite.set_bg_priority(priority);
        _shadow.set_bg_priority(priority);
    }

    void player::_update_graphics(bool moving)
    {
        int facing_index = 0;

        switch(_direction)
        {

        case direction::down:
            facing_index = 0;
            break;

        case direction::right:
            facing_index = 1;
            break;

        case direction::up:
            facing_index = 2;
            break;

        case direction::left:
            facing_index = 3;
            break;

        default:
            break;
        }

        int frame = moving ? 1 + ((_anim_counter / anim_wait) % 4) : 0;
        _sprite.set_tiles(bn::sprite_items::player.tiles_item(), (facing_index * frames_per_facing) + frame);
    }
}
