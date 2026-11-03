#ifndef TL_TOWN_MAP_H
#define TL_TOWN_MAP_H

#include "town_map_data.h"

namespace tl::town_map
{
    // Map size in pixels.
    constexpr int pixel_width = town_map_data::width * town_map_data::metatile_size;
    constexpr int pixel_height = town_map_data::height * town_map_data::metatile_size;

    // Returns true if the given map pixel is blocked (outside the map counts as blocked).
    [[nodiscard]] constexpr bool solid_at(int x, int y)
    {
        if(x < 0 || y < 0 || x >= pixel_width || y >= pixel_height)
        {
            return true;
        }

        int mx = x / town_map_data::metatile_size;
        int my = y / town_map_data::metatile_size;
        return town_map_data::solid[(my * town_map_data::width) + mx] != 0;
    }

    // Returns true if any pixel of the given rectangle (map pixels, inclusive) is blocked.
    [[nodiscard]] constexpr bool solid_rect(int left, int top, int right, int bottom)
    {
        // Checking corners and the middle points is enough because metatiles (16px) are larger than the hitbox.
        int mid_x = (left + right) / 2;
        int mid_y = (top + bottom) / 2;
        return solid_at(left, top) || solid_at(right, top) || solid_at(left, bottom) || solid_at(right, bottom) ||
                solid_at(mid_x, top) || solid_at(mid_x, bottom) || solid_at(left, mid_y) || solid_at(right, mid_y);
    }
}

#endif
