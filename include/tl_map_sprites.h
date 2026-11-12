#ifndef TL_MAP_SPRITES_H
#define TL_MAP_SPRITES_H

#include "bn_vector.h"
#include "bn_sprite_ptr.h"

#include "tl_world.h"
#include "tl_lighting.h"

namespace tl
{
    // Flag-driven map sprites (s75): the movable cable-works barriers and Teo's door bridge in Old Block. Placements come from
    // tools/map_sprites.py (generated include/tl_map_sprite_data.h); a sprite shows while its flag_on is set (or -1) and its
    // flag_off is not set (or -1). The art is drawn by tools/map_sprites.py, 64x32 frames, shared palette.
    class map_sprites
    {

    public:
        void load(const map_info& map);
        void clear();
        void set_lighting(const light_params& params);
        void update(const map_info& map, int cam_x, int cam_y);

    private:
        bn::vector<bn::sprite_ptr, 10> _sprites;
        bn::vector<int, 10> _entry;
        light_params _light;
    };
}

#endif
