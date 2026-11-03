#ifndef TL_CRITTERS_H
#define TL_CRITTERS_H

#include "bn_fixed.h"
#include "bn_random.h"
#include "bn_vector.h"
#include "bn_sprite_ptr.h"

#include "tl_world.h"

namespace tl
{
    // Ambient animals: pigeons that peck around and fly off when the player comes close (and land
    // again later), squirrels that sit in the park and flee up a tree.
    class critters
    {

    public:
        static constexpr int max_critters = 16;

        void load(const map_info& map);
        void clear();

        // player_x / player_y in world units; camera top-left in image pixels.
        void update(int player_x, int player_y, int cam_x, int cam_y);

    private:
        enum class state : uint8_t
        {
            idle,
            fleeing,    // pigeon: flying away, squirrel: running to its tree / away
            climbing,   // squirrel going up the trunk
            gone,       // out of sight, waiting to come back
            returning   // pigeon landing on its spot
        };

        struct critter
        {
            bn::sprite_ptr sprite;
            const critter_spawn* spawn;
            bn::fixed x;
            bn::fixed y;
            bn::fixed z;        // height above the ground in screen pixels
            bn::fixed vx;
            bn::fixed vy;
            bn::fixed vz;
            int timer = 0;
            int frame = 0;
            int anim = 0;
            state current = state::idle;
            bool flip = false;
        };

        const map_info* _map = nullptr;
        bn::vector<critter, max_critters> _critters;
        bn::random _random;

        void _update_pigeon(critter& c, int player_x, int player_y);
        void _update_squirrel(critter& c, int player_x, int player_y);
        void _place_sprite(critter& c, int cam_x, int cam_y);
        [[nodiscard]] int _random_int(int limit)
        {
            return _random.get_int(limit);
        }
    };
}

#endif
