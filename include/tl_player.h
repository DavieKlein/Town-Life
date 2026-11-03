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
        explicit player(const bn::camera_ptr& camera);

        // Places the player on a map at world position (x, y) = the feet.
        void place(const map_info& map, int x, int y, direction facing);

        // Reads input, moves and animates the player.
        void update();

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
        bn::sprite_ptr _sprite;
        const map_info* _map = nullptr;
        int _x = 0;
        int _y = 0;
        direction _direction = direction::down;
        int _anim_counter = 0;

        void _update_sprite();
        void _update_graphics(bool moving);
    };
}

#endif
