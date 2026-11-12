#ifndef TL_WORLD_H
#define TL_WORLD_H

#include <cstdint>

#include "tl_map_id.h"

namespace bn
{
    class color;
}

namespace tl
{
    // World units: 1 unit = 1 screen pixel horizontally; one map cell is 16x16 units.
    // Isometric projection (2:1): +x goes down-right on screen, +y goes down-left.
    //   image_x = origin_x + x - y
    //   image_y = origin_y + (x + y) / 2
    // "Image" coordinates are pixels of the pre-rendered map image (top-left = 0, 0).
    constexpr int cell_size = 16;
    constexpr int solid_res = 4;                     // collision sub-cells per map cell (per axis)
    constexpr int solid_cell = cell_size / solid_res; // world units per collision sub-cell

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
        int sx0, sy0, sx1, sy1;     // screen bounding box (image pixels)

        // Iso depth test for disjoint boxes: the player is in front if past the far edge on either axis.
        [[nodiscard]] constexpr bool hides(int px, int py, int image_x, int image_y, int half_width,
                                           int height) const
        {
            bool overlaps = image_x + half_width > sx0 && image_x - half_width < sx1 && image_y > sy0 &&
                    image_y - height < sy1;
            return overlaps && px < x1 && py < y1;
        }
    };

    // Ambient animals (see tools/critters.py).
    enum class critter_kind : uint8_t
    {
        pigeon,
        squirrel
    };

    struct critter_spawn
    {
        critter_kind kind;
        int x;          // world units
        int y;
        int tree_x;     // squirrels: tree to flee up into (world units), -1 = none
        int tree_y;
    };

    // Objects the player can use with A (see tools/interactions.py).
    enum class interactable_kind : uint8_t
    {
        bench,
        fountain,
        shop_market,
        shop_diner,
        toilet,
        sink,
        bookshelf,
        noticeboard,
        reception,
        bin,
        seat,           // chair / sofa / booth bench: sit facing +y (screen down-left)
        seat_x,         // same, facing +x (screen down-right, the sit sprite mirrored)
        deposit,        // RETURN & EARN machine
        bed,            // the player's bed: Sleep / Take a nap
        desk,           // Read / Check notes (shows the current objective)
        window,         // look outside (info text)
        wardrobe,       // info text
        gate,           // VaultTech staff gate at the foot of the storeroom stairs (after the firing)
        crate,          // storeroom crate with Mr. Pimm's rye loaf (Day 1)
        kiosk,          // newspaper boxes at the bus stop: scratch cards and newspapers (s63)
        shower,         // s64: shower cubicle of the public toilet ($1 coin slot)
        clinic,         // s64: City Clinic reception desk (check-up, pay the bill, talk to the doctor)
        couch,          // s64: the exam couch (info text; fainting patients wake up here)
        // s75 Old Block (quality = index of the text in the field's info table where noted)
        shop_bakery,    // Bellini Bakery counter
        shop_lane,      // Baker's Lane corner grocery counter
        shop_stall,     // Rosa's market stall on Cobble Street
        sign,           // info page, quality = text index
        flap,           // fence flap of the sneak route (before sneak_route: just a fence)
        hatch,          // NODE 7 hatch at the demolition site
        chess,          // watch the chess game
        garden,         // water the community garden
        hoop,           // shoot hoops on the court
        washer,         // laundromat washing machine
        oven            // bakery oven (warm up)
    };

    struct interactable
    {
        interactable_kind kind;
        int x;          // world units: bench = seat centre, fountain = centre
        int y;
        int radius;     // fountain radius (world units), 0 for benches
        int quality;    // 1..3 (toilet, bookshelf), 0 = not used
    };

    // Standing NPCs (see tools/npcs.py): one idle sprite, facing is an index into the 8-frame sheet.
    enum class npc_kind : uint8_t
    {
        mia
    };

    struct npc_spawn
    {
        npc_kind kind;
        int x;          // world units (feet)
        int y;
        int facing;     // 0..7: s, sw, w, nw, n, ne, e, se
    };

    // One pre-rendered layer, split into 4bpp 8x8 tiles.
    struct layer_data
    {
        const uint32_t* tiles;      // 8 words per tile; tile 0 is empty
        int tiles_count;
        const uint32_t* cells;      // per 8x8 cell: bits 0-15 tile, bit 16 hflip, bit 17 vflip, bits 20-23 bank
        const bn::color* palette;   // 16 colours per bank
        int banks;
        // objects layer only (else nullptr): per cell u32: bits 0-11 = min iso depth (x + y, world
        // units), bits 12-15 = ceil(max offset / 17), bits 16-31 = 0xFFFF when the whole cell has that depth,
        // else the index of a 64-byte block in depth_pixels (per pixel depth - min, 255 = no pixel).
        const uint32_t* depth;
        const uint8_t* depth_pixels;
        // special palette entries (see tools/build_assets.py): water (palette cycling) in the banks of
        // water_banks (bit mask), window glass (2 entries, lit at night), lamp glass (bright at night).
        int water_banks;
        int water_first;
        int water_count;
        int glass_first;    // 0 = none
        int lamp_index;     // 0 = none
    };

    // A street lamp: centre of its light pool on the ground at night (world units).
    struct lamp
    {
        int x;
        int y;
    };

    // Gated solids (Old Block): sub-cell aligned rectangles that are solid in the ROM collision grid (closed state) and
    // walkable while `gate_open[gate]` is true (field::_update_gates sets it from story flags).
    enum class gate_id : uint8_t
    {
        sneak,          // fence flap + bush lane (flag sneak_route)
        barrier,        // gap in the barrier line (flag barrier_moved)
        bridge          // Teo's door bridge over the trench (flag door_bridge)
    };

    constexpr int max_gates = 8;
    inline bool gate_open[max_gates] = {};

    struct gate_rect
    {
        int x0;         // world units, half-open [x0, x1) x [y0, y1)
        int y0;
        int x1;
        int y1;
        gate_id gate;
    };

    struct map_info
    {
        const char* name;
        layer_data floor;
        layer_data objects;
        int width;      // map cells (16 world units)
        int height;
        int origin_x;   // image pixel of world (0, 0)
        int origin_y;
        int image_width;
        int image_height;
        int view_x0, view_y0, view_x1, view_y1;     // area the camera may show (image pixels)
        const uint8_t* solid;
        const warp* warps;
        int warps_count;
        const occluder* occluders;
        int occluders_count;
        const critter_spawn* critters;
        int critters_count;
        const interactable* interactables;
        int interactables_count;
        const npc_spawn* npcs;
        int npcs_count;
        const lamp* lamps;
        int lamps_count;
        bool outdoor;   // day/night lighting applies
        const gate_rect* gates;
        int gates_count;

        [[nodiscard]] constexpr int to_image_x(int x, int y) const
        {
            return origin_x + x - y;
        }

        [[nodiscard]] constexpr int to_image_y(int x, int y) const
        {
            return origin_y + ((x + y) / 2);
        }

        // Returns true if the given world point is blocked (outside the map counts as blocked).
        // The collision grid has solid_res sub-cells per map cell (row-major, width * solid_res columns).
        [[nodiscard]] bool solid_at(int x, int y) const
        {
            if(x < 0 || y < 0 || x >= width * cell_size || y >= height * cell_size)
            {
                return true;
            }

            if(solid[((y / solid_cell) * (width * solid_res)) + (x / solid_cell)] == 0)
            {
                return false;
            }

            for(int index = 0; index < gates_count; ++index)
            {
                const gate_rect& g = gates[index];

                if(gate_open[int(g.gate)] && x >= g.x0 && x < g.x1 && y >= g.y0 && y < g.y1)
                {
                    return false;
                }
            }

            return true;
        }

        // Returns true if any sub-cell touched by the square around (x, y) is blocked.
        [[nodiscard]] bool solid_around(int x, int y, int radius) const
        {
            for(int sy = y - radius; ; sy += solid_cell)
            {
                if(sy > y + radius)
                {
                    sy = y + radius;
                }

                for(int sx = x - radius; ; sx += solid_cell)
                {
                    if(sx > x + radius)
                    {
                        sx = x + radius;
                    }

                    if(solid_at(sx, sy))
                    {
                        return true;
                    }

                    if(sx == x + radius)
                    {
                        break;
                    }
                }

                if(sy == y + radius)
                {
                    break;
                }
            }

            return false;
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
        // The whole layer shares one priority, so when the player stands behind a small object but in
        // front of a large one that also overlaps the sprite (e.g. a bollard in front of a tower), the
        // large one wins and the player stays in front: otherwise the player would vanish.
        [[nodiscard]] constexpr bool player_hidden(int x, int y, int half_width, int sprite_height, bool ignore_taller = false) const
        {
            int image_x = to_image_x(x, y);
            int image_y = to_image_y(x, y);
            bool behind = false;

            for(int index = 0; index < occluders_count; ++index)
            {
                const occluder& o = occluders[index];
                bool overlaps = image_x + half_width > o.sx0 && image_x - half_width < o.sx1 && image_y > o.sy0 &&
                        image_y - sprite_height < o.sy1;

                if(overlaps)
                {
                    if(x < o.x1 && y < o.y1)
                    {
                        behind = true;
                    }
                    else if(! ignore_taller && o.sy0 < image_y - sprite_height)
                    {
                        return false;   // in front of something taller than the player
                    }
                }
            }

            return behind;
        }
    };

    [[nodiscard]] const map_info& get_map(map_id id);
}

#endif
