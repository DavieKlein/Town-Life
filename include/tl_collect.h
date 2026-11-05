#ifndef TL_COLLECT_H
#define TL_COLLECT_H

#include "bn_vector.h"
#include "bn_sprite_ptr.h"

#include "tl_world.h"
#include "tl_lighting.h"

namespace tl
{
    // s64: the three collectible sets of district 1 (old city coins, lost postcards, VaultTech flyers), 4 items each, fixed spots in
    // the City Centre (tools/collectibles.py). Real 3D props rendered by Blender (graphics/collectibles.bmp), 2-frame twinkle like
    // the deposit pickups. Found items stay gone; the mask is saved.
    class collectibles
    {

    public:
        static constexpr int count = 12;
        static constexpr int set_count = 3;

        uint16_t mask = 0;              // bit per item found (set * 4 + item)
        uint8_t paid = 0;               // bit per set whose reward was paid

        void load(const map_info& map);
        void clear();
        void set_lighting(const light_params& params);

        // Nearest item not yet found within `reach` world units on the City Centre, or -1; d2 gets the squared distance.
        [[nodiscard]] int find(int x, int y, int reach, int& d2) const;

        // Marks the item as found; returns the number of items of its set now found.
        int collect(int index);

        [[nodiscard]] int found_in_set(int set) const;
        [[nodiscard]] bool found(int index) const
        {
            return (mask >> index) & 1;
        }

        void update(const map_info& map, int cam_x, int cam_y);

    private:
        bn::vector<bn::sprite_ptr, 12> _sprites;
        bn::vector<int, 12> _sprite_item;
        light_params _light;
        int _frame = 0;
        bool _city = false;

        void _rebuild();
    };
}

#endif
