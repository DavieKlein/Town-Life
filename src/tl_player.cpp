#include "tl_player.h"

#include "bn_math.h"
#include "bn_keypad.h"
#include "bn_blending.h"
#include "bn_sprite_items_player.h"
#include "bn_sprite_items_shadow.h"

namespace tl
{
    namespace
    {
        constexpr int hitbox_radius = 4;        // world units around the feet

        // player.bmp: 32x64 frames rendered from the 3D character, 9 per facing (idle + 8 walk frames),
        // 8 facings in clockwise screen order (s, sw, w, nw, n, ne, e, se). Feet at (16, 54) in each frame.
        constexpr int frames_per_facing = 9;
        constexpr int walk_frames = 8;
        constexpr int feet_offset_y = 54 - 32;  // feet relative to the sprite centre
        constexpr int sprite_half_width = 10;   // body size used for the depth test
        constexpr int sprite_height = 50;

        constexpr bn::fixed walk_speed = 1.25;  // screen pixels per frame
        constexpr bn::fixed run_speed = 2.25;
        constexpr bn::fixed acceleration = 0.25; // fraction of the speed difference applied per frame
        constexpr bn::fixed deceleration = 0.4;
        constexpr bn::fixed step_length = 4;    // screen pixels per walk animation frame

        // World velocity for one screen pixel per frame, per facing. Up/down/left/right on the d-pad move
        // straight across the screen; diagonals follow the isometric streets.
        //   screen_dx = vx - vy, screen_dy = (vx + vy) / 2
        struct world_dir
        {
            bn::fixed x;
            bn::fixed y;
        };

        constexpr world_dir directions[8] = {
            { 1, 1 },               // s:  screen down
            { 0, 0.894 },           // sw: +y (iso street)
            { -0.5, 0.5 },          // w:  screen left
            { -0.894, 0 },          // nw: -x (iso street)
            { -1, -1 },             // n:  screen up
            { 0, -0.894 },          // ne: -y (iso street)
            { 0.5, -0.5 },          // e:  screen right
            { 0.894, 0 },           // se: +x (iso street)
        };

        [[nodiscard]] int facing_from_direction(direction facing)
        {
            switch(facing)
            {

            case direction::down:
                return 1;

            case direction::left:
                return 3;

            case direction::up:
                return 5;

            case direction::right:
                return 7;

            default:
                return 0;
            }
        }

        // Returns the facing (0..7) for the pressed d-pad keys, or -1 if no direction is pressed.
        [[nodiscard]] int input_facing()
        {
            int dx = bn::keypad::right_held() ? 1 : (bn::keypad::left_held() ? -1 : 0);
            int dy = bn::keypad::down_held() ? 1 : (bn::keypad::up_held() ? -1 : 0);

            if(dx == 0 && dy == 1)
            {
                return 0;
            }

            if(dx == -1 && dy == 1)
            {
                return 1;
            }

            if(dx == -1 && dy == 0)
            {
                return 2;
            }

            if(dx == -1 && dy == -1)
            {
                return 3;
            }

            if(dx == 0 && dy == -1)
            {
                return 4;
            }

            if(dx == 1 && dy == -1)
            {
                return 5;
            }

            if(dx == 1 && dy == 0)
            {
                return 6;
            }

            if(dx == 1 && dy == 1)
            {
                return 7;
            }

            return -1;
        }
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
        _vx = 0;
        _vy = 0;
        _facing = facing_from_direction(facing);
        _anim_distance = 0;
        _anim_frame = 0;
        _update_graphics();
    }

    void player::update()
    {
        int facing = input_facing();
        bn::fixed target_vx;
        bn::fixed target_vy;

        if(facing >= 0)
        {
            _facing = facing;

            // Hold B to run.
            bn::fixed speed = bn::keypad::b_held() ? run_speed : walk_speed;
            target_vx = directions[facing].x * speed;
            target_vy = directions[facing].y * speed;
            _vx += (target_vx - _vx) * acceleration;
            _vy += (target_vy - _vy) * acceleration;
        }
        else
        {
            _vx -= _vx * deceleration;
            _vy -= _vy * deceleration;

            if(bn::abs(_vx) < bn::fixed(0.05) && bn::abs(_vy) < bn::fixed(0.05))
            {
                _vx = 0;
                _vy = 0;
            }
        }

        // Move each axis separately so the player slides along walls.
        bn::fixed old_x = _x;
        bn::fixed old_y = _y;
        bn::fixed new_x = _x + _vx;

        if(! _map->solid_around(new_x.floor_integer(), _y.floor_integer(), hitbox_radius))
        {
            _x = new_x;
        }
        else
        {
            _vx = 0;
        }

        bn::fixed new_y = _y + _vy;

        if(! _map->solid_around(_x.floor_integer(), new_y.floor_integer(), hitbox_radius))
        {
            _y = new_y;
        }
        else
        {
            _vy = 0;
        }

        // Walk animation driven by the distance moved on screen.
        bn::fixed moved_x = bn::abs((_x - old_x) - (_y - old_y));
        bn::fixed moved_y = bn::abs((_x - old_x) + (_y - old_y)) / 2;
        bn::fixed moved = moved_x > moved_y ? moved_x + (moved_y / 2) : moved_y + (moved_x / 2);

        if(moved > bn::fixed(0.1))
        {
            _anim_distance += moved;

            if(_anim_distance >= step_length)
            {
                _anim_distance -= step_length;
                _anim_frame = (_anim_frame % walk_frames) + 1;
            }

            if(_anim_frame == 0)
            {
                _anim_frame = 1;
            }
        }
        else
        {
            _anim_frame = 0;
            _anim_distance = 0;
        }

        _update_graphics();
    }

    void player::update_sprite(int cam_x, int cam_y)
    {
        // Screen coordinates are relative to the screen centre.
        int screen_x = image_x() - cam_x - 120;
        int screen_y = image_y() - cam_y - 80;
        _sprite.set_position(screen_x, screen_y - feet_offset_y);
        _shadow.set_position(screen_x, screen_y - 1);

        // Behind a building/tree: draw below the objects layer (priority 2), otherwise above it.
        int priority = _map->player_hidden(x(), y(), sprite_half_width, sprite_height) ? 3 : 2;
        _sprite.set_bg_priority(priority);
        _shadow.set_bg_priority(priority);
    }

    void player::_update_graphics()
    {
        _sprite.set_tiles(bn::sprite_items::player.tiles_item(), (_facing * frames_per_facing) + _anim_frame);
    }
}
