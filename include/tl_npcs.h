#ifndef TL_NPCS_H
#define TL_NPCS_H

#include "bn_vector.h"
#include "bn_sprite_ptr.h"

#include "tl_world.h"

namespace tl
{
    // Standing NPCs (idle frame only, see tools/npcs.py). They are drawn like the player: above the
    // objects layer, or below it when an occluder (e.g. the checkout counter) is in front of them.
    // Interiors are not lit by the day/night cycle, so their palettes stay as built.
    class npcs
    {

    public:
        static constexpr int max_npcs = 8;

        void load(const map_info& map);
        void clear();

        // Camera top-left in image pixels.
        void update(int cam_x, int cam_y);

    private:
        struct npc
        {
            bn::sprite_ptr sprite;
            const npc_spawn* spawn;
        };

        bn::vector<npc, max_npcs> _npcs;
        const map_info* _map = nullptr;
    };
}

#endif
