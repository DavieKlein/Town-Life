#ifndef TL_WORLD_H
#define TL_WORLD_H

#include <cstdint>

#include "tl_map_id.h"

namespace bn
{
    class regular_bg_item;
}

namespace tl
{
    constexpr int metatile_size = 16;

    enum class direction
    {
        down,
        up,
        left,
        right
    };

    // Used in warps: keep the player's current x or y coordinate.
    constexpr int keep_coordinate = -1;

    // A trigger rectangle (map pixels) that moves the player to another map.
    struct warp
    {
        int x;
        int y;
        int width;
        int height;
        map_id target;
        int target_x;   // map pixels, or keep_coordinate
        int target_y;   // map pixels, or keep_coordinate
        direction facing;

        [[nodiscard]] constexpr bool contains(int px, int py) const
        {
            return px >= x && py >= y && px < x + width && py < y + height;
        }
    };

    struct map_info
    {
        const char* name;
        const bn::regular_bg_item* bg_item;
        int width;      // metatiles
        int height;     // metatiles
        const uint8_t* solid;
        const warp* warps;
        int warps_count;

        [[nodiscard]] constexpr int pixel_width() const
        {
            return width * metatile_size;
        }

        [[nodiscard]] constexpr int pixel_height() const
        {
            return height * metatile_size;
        }

        // Returns true if the given map pixel is blocked (outside the map counts as blocked).
        [[nodiscard]] constexpr bool solid_at(int px, int py) const
        {
            if(px < 0 || py < 0 || px >= pixel_width() || py >= pixel_height())
            {
                return true;
            }

            return solid[((py / metatile_size) * width) + (px / metatile_size)] != 0;
        }

        // Returns true if any pixel of the given rectangle (map pixels, inclusive) is blocked.
        // Checking corners and middle points is enough because metatiles are larger than the hitbox.
        [[nodiscard]] constexpr bool solid_rect(int left, int top, int right, int bottom) const
        {
            int mid_x = (left + right) / 2;
            int mid_y = (top + bottom) / 2;
            return solid_at(left, top) || solid_at(right, top) || solid_at(left, bottom) ||
                    solid_at(right, bottom) || solid_at(mid_x, top) || solid_at(mid_x, bottom) ||
                    solid_at(left, mid_y) || solid_at(right, mid_y);
        }

        // Returns the warp containing the given map pixel, or nullptr.
        [[nodiscard]] constexpr const warp* warp_at(int px, int py) const
        {
            for(int index = 0; index < warps_count; ++index)
            {
                if(warps[index].contains(px, py))
                {
                    return warps + index;
                }
            }

            return nullptr;
        }
    };

    [[nodiscard]] const map_info& get_map(map_id id);
}

#endif
