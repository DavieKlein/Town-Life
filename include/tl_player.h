#ifndef TL_PLAYER_H
#define TL_PLAYER_H

#include "bn_fixed.h"
#include "bn_optional.h"
#include "bn_sprite_ptr.h"

#include "tl_world.h"
#include "tl_lighting.h"

namespace tl
{
    class player
    {

    public:
        enum class activity
        {
            walking,
            sitting,    // on a bench
            sleeping,   // lying on a bench
            washing     // at the fountain
        };

        player();

        // Interactions (positions in world units).
        void sit_on(int seat_x, int seat_y);
        void sleep_on(int seat_x, int seat_y);
        void start_washing(int target_x, int target_y);

        [[nodiscard]] activity current_activity() const
        {
            return _activity;
        }

        // True during the frame a washing animation finishes.
        [[nodiscard]] bool washing_finished() const
        {
            return _washing_finished;
        }

        [[nodiscard]] int facing_index() const
        {
            return _facing;
        }

        // Applies day/night lighting to the player's sprite palettes.
        void set_lighting(const light_params& params);

        // Image rectangle covered by the player's sprites and the iso depth to test the map against
        // (for the front layer: map pixels in front of the player are drawn over it).
        void mask_area(int& x0, int& y0, int& x1, int& y1, int& depth) const;

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
        bn::optional<bn::sprite_ptr> _rest_sprite;     // 64x64 sitting / sleeping sprite
        activity _activity = activity::walking;
        int _activity_timer = 0;
        light_params _light;
        int _seat_x = 0;
        int _seat_y = 0;
        bool _washing_finished = false;
        const map_info* _map = nullptr;
        bn::fixed _x;
        bn::fixed _y;
        bn::fixed _vx;              // world units per frame
        bn::fixed _vy;
        int _facing = 0;            // 0..7: s, sw, w, nw, n, ne, e, se (clockwise screen directions)
        bn::fixed _anim_distance;   // screen pixels walked, drives the walk cycle
        int _anim_frame = 0;

        void _update_graphics();
        void _apply_lighting();
        void _stand_up();
        void _update_activity();
    };
}

#endif
