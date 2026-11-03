#ifndef TL_PLAYER_H
#define TL_PLAYER_H

#include "bn_fixed.h"
#include "bn_sprite_ptr.h"

#include "tl_world.h"

namespace tl
{
    class player
    {

    public:
        player();

        // Places the player on a map at world position (x, y) = the feet.
        void place(const map_info& map, int x, int y, direction facing);

        // Reads input, moves and animates the player.
        void update();

        // Positions the sprite for a camera whose top-left corner is (cam_x, cam_y) in image pixels.
        void update_sprite(int cam_x, int cam_y);

        [[nodiscard]] int x() const
        {
            return _x.floor_integer();
        }

        [[nodiscard]] int y() const
        {
            return _y.floor_integer();
        }

        // Point the camera should follow (image pixels): roughly the middle of the body.
        [[nodiscard]] int focus_x() const
        {
            return image_x();
        }

        [[nodiscard]] int focus_y() const
        {
            return image_y() - 22;
        }

        // Feet position in image pixels, computed from the sub-pixel world position (no jitter).
        [[nodiscard]] int image_x() const
        {
            return _map->origin_x + (_x - _y).round_integer();
        }

        [[nodiscard]] int image_y() const
        {
            return _map->origin_y + ((_x + _y) / 2).round_integer();
        }

    private:
        bn::sprite_ptr _shadow;
        bn::sprite_ptr _sprite;
        const map_info* _map = nullptr;
        bn::fixed _x;
        bn::fixed _y;
        bn::fixed _vx;              // world units per frame
        bn::fixed _vy;
        int _facing = 0;            // 0..7: s, sw, w, nw, n, ne, e, se (clockwise screen directions)
        bn::fixed _anim_distance;   // screen pixels walked, drives the walk cycle
        int _anim_frame = 0;

        void _update_graphics();
    };
}

#endif
