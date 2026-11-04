#ifndef TL_NPCS_H
#define TL_NPCS_H

#include "bn_vector.h"
#include "bn_sprite_ptr.h"

#include "tl_world.h"
#include "tl_cast_data.h"
#include "tl_lighting.h"
#include "tl_player.h"

namespace tl
{
    // Standing NPCs of the story cast (looks and placements: tools/cast.py -> include/tl_cast_data.h). Who stands where
    // depends on the map, the day and the time of day (npc_placements). They are drawn like the player: above the objects
    // layer, or below it when an occluder (e.g. the checkout counter) is in front of them. They block the player and can be
    // talked to (A). Interiors are not lit by the day/night cycle, so their palettes stay as built.
    class npcs
    {

    public:
        static constexpr int max_npcs = 6;

        // Places everybody who is on this map at that time.
        void load(const map_info& map, map_id id, int day, int minutes);
        void clear();

        // Call every game minute: changes who is present when a schedule entry starts or ends.
        void refresh(int day, int minutes);

        // Camera top-left in image pixels.
        void update(int cam_x, int cam_y);
        void set_lighting(const light_params& params);

        // The nearest NPC within `reach` world units of (x, y), or -1; d2 = squared distance.
        [[nodiscard]] int find(int x, int y, int reach, int& d2) const;

        [[nodiscard]] int count() const
        {
            return _npcs.size();
        }

        [[nodiscard]] npc_id id_of(int index) const
        {
            return _npcs[index].who;
        }

        [[nodiscard]] int x_of(int index) const
        {
            return _npcs[index].x;
        }

        [[nodiscard]] int y_of(int index) const
        {
            return _npcs[index].y;
        }

        // Turns an NPC towards a world point.
        void face_towards(int index, int target_x, int target_y);

        // Back to the placement's own facing (after a conversation).
        void reset_facings();

        // Feet positions for player collision.
        [[nodiscard]] const player::blocker* blockers() const
        {
            return _blockers;
        }

    private:
        struct npc
        {
            bn::sprite_ptr sprite;
            npc_id who;
            int x;
            int y;
            int facing;
            int placement;      // index in npc_placements
        };

        bn::vector<npc, max_npcs> _npcs;
        player::blocker _blockers[max_npcs];
        const map_info* _map = nullptr;
        map_id _map_id = map_id(0);
        light_params _light;
        int _last_cam_x = 0;
        int _last_cam_y = 0;

        void _build(int day, int minutes);
        void _apply_palettes();
    };
}

#endif
