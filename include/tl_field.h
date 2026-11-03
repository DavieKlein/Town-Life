#ifndef TL_FIELD_H
#define TL_FIELD_H

#include "bn_optional.h"
#include "bn_camera_ptr.h"
#include "bn_regular_bg_ptr.h"

#include "tl_player.h"

namespace tl
{
    // The "overworld" scene: the current map, the player, the camera and map transitions.
    class field
    {

    public:
        field(map_id start_map, int start_x, int start_y, direction facing);

        void update();

    private:
        enum class state
        {
            fading_in,
            playing,
            fading_out
        };

        bn::camera_ptr _camera;
        bn::optional<bn::regular_bg_ptr> _bg;
        player _player;
        const map_info* _map = nullptr;
        const warp* _pending_warp = nullptr;
        state _state = state::fading_in;
        int _fade_counter = 0;

        void _load_map(map_id id, int x, int y, direction facing);
        void _update_camera();
        static void _set_fade(int counter);
    };
}

#endif
