#ifndef TL_PLAYER_H
#define TL_PLAYER_H

#include "bn_sprite_ptr.h"
#include "bn_camera_ptr.h"

#include "tl_world.h"

namespace tl
{
    class player
    {

    public:
        player(const bn::camera_ptr& camera);

        // Places the player on a map. map_x / map_y: centre of the sprite in map pixels.
        void place(const map_info& map, int map_x, int map_y, direction facing);

        // Reads input, moves and animates the player.
        void update();

        [[nodiscard]] int map_x() const
        {
            return _map_x;
        }

        [[nodiscard]] int map_y() const
        {
            return _map_y;
        }

        // Point used for triggers such as warps (around the feet).
        [[nodiscard]] int feet_x() const
        {
            return _map_x;
        }

        [[nodiscard]] int feet_y() const
        {
            return _map_y + 5;
        }

        [[nodiscard]] direction facing() const
        {
            return _direction;
        }

        void set_visible(bool visible)
        {
            _sprite.set_visible(visible);
        }

    private:
        bn::sprite_ptr _sprite;
        const map_info* _map = nullptr;
        int _map_x = 0;
        int _map_y = 0;
        direction _direction = direction::down;
        int _anim_counter = 0;

        [[nodiscard]] bool _can_move_to(int map_x, int map_y) const;
        void _update_sprite_position();
        void _update_graphics(bool moving);
    };
}

#endif
