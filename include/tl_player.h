#ifndef TL_PLAYER_H
#define TL_PLAYER_H

#include "bn_sprite_ptr.h"
#include "bn_camera_ptr.h"

namespace tl
{
    class player
    {

    public:
        enum class direction
        {
            down,
            up,
            left,
            right
        };

        // map_x / map_y: starting position in map pixels (centre of the sprite).
        player(int map_x, int map_y, const bn::camera_ptr& camera);

        void update();

        [[nodiscard]] int map_x() const
        {
            return _map_x;
        }

        [[nodiscard]] int map_y() const
        {
            return _map_y;
        }

    private:
        bn::sprite_ptr _sprite;
        int _map_x;
        int _map_y;
        direction _direction = direction::down;
        int _anim_counter = 0;
        int _speed_counter = 0;

        [[nodiscard]] bool _can_move_to(int map_x, int map_y) const;
        void _update_graphics(bool moving);
    };
}

#endif
