#ifndef TL_PLAYER_H
#define TL_PLAYER_H

#include "bn_fixed.h"
#include "bn_optional.h"
#include "bn_sprite_ptr.h"
#include "bn_sprite_item.h"

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
            acting      // a timed activity with its own animation (see action_kind)
        };

        enum class action_kind
        {
            wash,       // hands at the sink, face at the fountain
            eat,
            drink,      // scooping water with both hands
            read,
            search,     // rummaging through a trash bin
            pickup      // bending down to grab a can or bottle
        };

        player();

        // Interactions (positions in world units).
        void sit_on(int seat_x, int seat_y, bool mirrored = false);   // mirrored: faces +x instead of +y
        void sleep_on(int seat_x, int seat_y);
        void sit_for(int seat_x, int seat_y, int frames);     // sits on a toilet, stands up after `frames`

        // Plays an animation for `frames` frames, turned towards (target_x, target_y) (or keeping the facing
        // when the target is the player's own position).
        void start_action(action_kind kind, int target_x, int target_y, int frames);

        // Turns the (walking) player towards a world point and stops him (conversations).
        void face_towards(int target_x, int target_y);

        // Standing NPCs the player cannot walk through (world units, feet positions); only the pointer is kept.
        struct blocker
        {
            int x;
            int y;
        };

        void set_blockers(const blocker* list, int count)
        {
            _blockers = list;
            _blockers_count = count;
        }

        // Slides the player (if free) to `distance` units from a point, on the line through the player.
        void approach(int target_x, int target_y, int distance);

        [[nodiscard]] activity current_activity() const
        {
            return _activity;
        }

        // True during the frame a timed activity (action or toilet) ends by itself.
        [[nodiscard]] bool action_finished() const
        {
            return _action_finished;
        }

        [[nodiscard]] int facing_index() const
        {
            return _facing;
        }

        // Restores a saved facing (0..7) after place().
        void set_facing_index(int facing);

        // Applies day/night lighting to the player's sprite palettes.
        void set_lighting(const light_params& params);

        // Image rectangle covered by the player's sprites and the iso depth to test the map against
        // (for the front layer: map pixels in front of the player are drawn over it).
#ifdef TL_DEBUG_TELEPORT
        void debug_toggle() { _sprite.set_visible(! _sprite.visible()); }
        void debug_toggle2() { _shadow.set_visible(! _shadow.visible()); }
#endif
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
        bn::optional<bn::sprite_ptr> _act_sprite;      // eat / drink / read / search / wash animation
        const bn::sprite_item* _act_item = nullptr;
        action_kind _act_kind = action_kind::wash;
        int _act_frames = 0;                           // duration of the current action
        int _last_cam_x = 0;
        int _last_cam_y = 0;
        int _sit_frames = 0;                           // > 0: auto stand up (toilet)
        activity _activity = activity::walking;
        int _activity_timer = 0;
        light_params _light;
        int _seat_x = 0;
        int _seat_y = 0;
        bool _seat_mirrored = false;
        bool _action_finished = false;
        const map_info* _map = nullptr;
        const blocker* _blockers = nullptr;
        int _blockers_count = 0;
        bn::fixed _x;
        bn::fixed _y;
        bn::fixed _vx;              // world units per frame
        bn::fixed _vy;
        int _facing = 0;            // 0..7: s, sw, w, nw, n, ne, e, se (clockwise screen directions)
        bn::fixed _anim_distance;   // screen pixels walked, drives the walk cycle
        int _anim_frame = 0;

        [[nodiscard]] bool _blocked(int nx, int ny) const;
        void _update_graphics();
        void _apply_lighting();
        void _stand_up();
        void _update_activity();
    };
}

#endif
