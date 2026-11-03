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
    // World units: 1 unit = 1 screen pixel horizontally; one map cell is 16x16 units.
    // Isometric projection (2:1): +x goes down-right on screen, +y goes down-left.
    //   bg_x = origin_x + x - y
    //   bg_y = origin_y + (x + y) / 2
    constexpr int cell_size = 16;

    enum class direction
    {
        down,   // +y, screen down-left
        up,     // -y, screen up-right
        left,   // -x, screen up-left
        right   // +x, screen down-right
    };

    // A trigger rectangle (world units) that moves the player to another map.
    struct warp
    {
        int x;
        int y;
        int width;
        int height;
        map_id target;
        int target_x;   // world units
        int target_y;   // world units
        direction facing;

        [[nodiscard]] constexpr bool contains(int px, int py) const
        {
            return px >= x && py >= y && px < x + width && py < y + height;
        }
    };

    // Something on the objects layer that can hide the player when the player stands behind it.
    struct occluder
    {
        int x0, y0, x1, y1;         // world footprint
        int sx0, sy0, sx1, sy1;     // screen bounding box (bg pixels)

        // Iso depth test for disjoint boxes: the player is in front if past the far edge on either axis.
        [[nodiscard]] constexpr bool hides(int px, int py, int bg_x, int bg_y) const
        {
            bool overlaps = bg_x + 8 > sx0 && bg_x - 8 < sx1 && bg_y > sy0 && bg_y - 32 < sy1;
            return overlaps && px < x1 && py < y1;
        }
    };

    struct map_info
    {
        const char* name;
        const bn::regular_bg_item* floor_item;
        const bn::regular_bg_item* objects_item;
        int width;      // cells
        int height;     // cells
        int origin_x;   // bg pixel of world (0, 0)
        int origin_y;
        int bg_width;
        int bg_height;
        int view_x0, view_y0, view_x1, view_y1;     // area the camera may show (bg pixels)
        const uint8_t* solid;
        const warp* warps;
        int warps_count;
        const occluder* occluders;
        int occluders_count;

        [[nodiscard]] constexpr int to_bg_x(int x, int y) const
        {
            return origin_x + x - y;
        }

        [[nodiscard]] constexpr int to_bg_y(int x, int y) const
        {
            return origin_y + ((x + y) / 2);
        }

        // Returns true if the given world point is blocked (outside the map counts as blocked).
        [[nodiscard]] constexpr bool solid_at(int x, int y) const
        {
            if(x < 0 || y < 0 || x >= width * cell_size || y >= height * cell_size)
            {
                return true;
            }

            return solid[((y / cell_size) * width) + (x / cell_size)] != 0;
        }

        // Returns true if any corner of the square around (x, y) is blocked.
        [[nodiscard]] constexpr bool solid_around(int x, int y, int radius) const
        {
            return solid_at(x - radius, y - radius) || solid_at(x + radius, y - radius) ||
                    solid_at(x - radius, y + radius) || solid_at(x + radius, y + radius);
        }

        [[nodiscard]] constexpr const warp* warp_at(int x, int y) const
        {
            for(int index = 0; index < warps_count; ++index)
            {
                if(warps[index].contains(x, y))
                {
                    return warps + index;
                }
            }

            return nullptr;
        }

        // Returns true if the player at world (x, y) should be drawn behind the objects layer.
        [[nodiscard]] constexpr bool player_hidden(int x, int y) const
        {
            int bg_x = to_bg_x(x, y);
            int bg_y = to_bg_y(x, y);

            for(int index = 0; index < occluders_count; ++index)
            {
                if(occluders[index].hides(x, y, bg_x, bg_y))
                {
                    return true;
                }
            }

            return false;
        }
    };

    [[nodiscard]] const map_info& get_map(map_id id);
}

#endif
