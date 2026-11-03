#ifndef TL_PLAYER_H
#define TL_PLAYER_H

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

        // Point the camera should follow (image pixels): roughly the middle of the body.
        [[nodiscard]] int focus_x() const
        {
            return _map->to_image_x(_x, _y);
        }

        [[nodiscard]] int focus_y() const
        {
            return _map->to_image_y(_x, _y) - 22;
        }

        [[nodiscard]] int x() const
        {
            return _x;
        }

        [[nodiscard]] int y() const
        {
            return _y;
        }

        [[nodiscard]] direction facing() const
        {
            return _direction;
        }

    private:
        bn::sprite_ptr _shadow;
        bn::sprite_ptr _sprite;
        const map_info* _map = nullptr;
        int _x = 0;
        int _y = 0;
        direction _direction = direction::down;
        int _anim_counter = 0;

        void _update_graphics(bool moving);
    };
}

#endif
