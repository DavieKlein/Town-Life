#ifndef TL_DEPOSIT_H
#define TL_DEPOSIT_H

#include "bn_vector.h"
#include "bn_random.h"
#include "bn_sprite_ptr.h"

#include "tl_world.h"
#include "tl_lighting.h"

namespace tl
{
    // Can & bottle deposit ("RETURN & EARN"): loose pickups in the City Centre (sprites with a 2-frame twinkle), the
    // bag. Rules (whole dollars only): every can and every bottle is worth $1, paid at the machine. A map never holds more
    // than max_loose_per_map loose items; the
    // field tops them up at 6:00 every day. The bag holds bag_max items.
    class deposit
    {

    public:
        static constexpr int bag_max = 10;
        static constexpr int max_spots = 64;
        static constexpr int max_loose_per_map = 4;         // loose items per map; every can and bottle is worth $1

        // The save keeps one byte per spot: 0 = nothing, else kind (1 can, 2 bottle) | variant << 2.
        uint8_t spot[max_spots] = {};
        int bag_cans = 0;
        int bag_bottles = 0;
        int credit = 0;                                      // 0 or 1 left over after paying out

        // Creates the sprites if `map` is the City Centre (else none).
        void load(const map_info& map);
        void clear();
        void set_lighting(const light_params& params);

        // Fills free spots with random cans / bottles until the loose total is as close to $3.50 as it gets.
        void top_up(bn::random& rng);

        [[nodiscard]] int loose_credits() const;
        [[nodiscard]] int loose_on_map(int map) const;
        [[nodiscard]] int bag_total() const
        {
            return bag_cans + bag_bottles;
        }

        [[nodiscard]] int bag_credits() const
        {
            return bag_cans + bag_bottles;
        }

        // Nearest pickup within `reach` world units of (x, y) on the loaded map, or -1; d2 gets the squared distance.
        [[nodiscard]] int find(int x, int y, int reach, int& d2) const;
        [[nodiscard]] bool is_bottle(int index) const
        {
            return (spot[index] & 3) == 2;
        }

        // Takes the pickup into the bag (the caller checked the bag is not full).
        void collect(int index);

        // Pays out everything in the bag + the credit: returns the whole dollars, updates the credit.
        int return_all();

        // Moves the sprites (call every frame; no-op when none).
        void update(const map_info& map, int cam_x, int cam_y);

    private:
        bn::vector<bn::sprite_ptr, 8> _sprites;
        bn::vector<int, 8> _sprite_spot;
        light_params _light;
        int _frame = 0;
        bool _city = false;
        int _map = -1;

        void _rebuild();
    };
}

#endif
