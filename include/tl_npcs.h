#ifndef TL_NPCS_H
#define TL_NPCS_H

#include "bn_vector.h"
#include "bn_fixed.h"
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

        // ---- cutscene actors (tl_field_script.cpp). While actors exist, hidden NPCs stay hidden and the schedule is not applied
        // (refresh() does nothing) until release().
        void spawn(npc_id who, int x, int y, int facing);      // replaces a placed or spawned NPC of that id
        void despawn(npc_id who);
        void swap(npc_id from, npc_id to);
        void move_to(npc_id who, int x, int y, bool fast);
        void set_facing(npc_id who, int facing);
        void face_actor_towards(npc_id who, int target_x, int target_y);
        [[nodiscard]] bool moving() const;
        void tick();                                            // advances walks (call every frame while a script runs)
        void set_suppress(bool suppress);                       // true: the scheduled cast is not placed (scene_begin)
        void release(int day, int minutes);                     // scene_end: remove actors, place the schedule again
        [[nodiscard]] bool scripted() const
        {
            return _scripted;
        }

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
            int placement;      // index in npc_placements, -1 for a cutscene actor
            int target_x = 0;
            int target_y = 0;
            int speed = 0;      // 0 = not walking, 2 = walk, 3 = fast
            int bob = 0;
            bn::fixed fx = 0;
            bn::fixed fy = 0;
        };

        bn::vector<npc, max_npcs> _npcs;
        player::blocker _blockers[max_npcs];
        const map_info* _map = nullptr;
        map_id _map_id = map_id(0);
        light_params _light;
        int _last_cam_x = 0;
        int _last_cam_y = 0;
        bool _scripted = false;         // actors exist / NPCs were hidden: the schedule is frozen
        bool _suppress = false;

        [[nodiscard]] int _index_of(npc_id who) const;
        void _add_actor(npc_id who, int x, int y, int facing);
        void _build(int day, int minutes);
        void _apply_palettes();
    };
}

#endif
