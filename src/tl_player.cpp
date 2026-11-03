#include "tl_player.h"

#include "bn_keypad.h"
#include "bn_sprite_items_player.h"

#include "tl_town_map.h"

namespace tl
{
    namespace
    {
        // Hitbox around the feet, relative to the sprite centre (16x16 sprite).
        constexpr int hitbox_left = -5;
        constexpr int hitbox_right = 4;
        constexpr int hitbox_top = 2;
        constexpr int hitbox_bottom = 7;

        // Frames in player.bmp: 0-2 down, 3-5 up, 6-8 side (facing right).
        constexpr int frames_per_direction = 3;
        constexpr int anim_wait = 8;    // game frames per animation step

        // Walking cycle: stand, step A, stand, step B.
        constexpr int walk_cycle[] = { 0, 1, 0, 2 };
    }

    player::player(int map_x, int map_y, const bn::camera_ptr& camera) :
        _sprite(bn::sprite_items::player.create_sprite(0, 0)),
        _map_x(map_x),
        _map_y(map_y)
    {
        _sprite.set_camera(camera);
        _sprite.set_position(_map_x - (town_map::pixel_width / 2), _map_y - (town_map::pixel_height / 2));
    }

    bool player::_can_move_to(int map_x, int map_y) const
    {
        return ! town_map::solid_rect(map_x + hitbox_left, map_y + hitbox_top,
                                      map_x + hitbox_right, map_y + hitbox_bottom);
    }

    void player::update()
    {
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
            // Facing: horizontal wins when moving diagonally only if there was no vertical input before.
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
                if(dx != 0 && _can_move_to(_map_x + dx, _map_y))
                {
                    _map_x += dx;
                }

                if(dy != 0 && _can_move_to(_map_x, _map_y + dy))
                {
                    _map_y += dy;
                }
            }

            _anim_counter += steps;
        }
        else
        {
            _anim_counter = 0;
        }

        _sprite.set_position(_map_x - (town_map::pixel_width / 2), _map_y - (town_map::pixel_height / 2));
        _update_graphics(moving);
    }

    void player::_update_graphics(bool moving)
    {
        int base_frame = 0;
        bool flip = false;

        switch(_direction)
        {

        case direction::down:
            base_frame = 0;
            break;

        case direction::up:
            base_frame = frames_per_direction;
            break;

        case direction::left:
            base_frame = frames_per_direction * 2;
            flip = true;
            break;

        case direction::right:
            base_frame = frames_per_direction * 2;
            break;
        }

        int step = 0;

        if(moving)
        {
            step = walk_cycle[(_anim_counter / anim_wait) % 4];
        }

        _sprite.set_tiles(bn::sprite_items::player.tiles_item(), base_frame + step);
        _sprite.set_horizontal_flip(flip);
    }
}
