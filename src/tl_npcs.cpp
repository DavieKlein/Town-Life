#include "tl_npcs.h"

#include "bn_sprite_palette_ptr.h"
#include "bn_sprite_items_npc_mia.h"
#include "bn_sprite_items_npc_rosa.h"
#include "bn_sprite_items_npc_dex.h"
#include "bn_sprite_items_npc_pimm.h"
#include "bn_sprite_items_npc_lou.h"
#include "bn_sprite_items_npc_dex_vault.h"
#include "bn_sprite_items_npc_victor.h"
#include "bn_sprite_items_npc_robot.h"

namespace tl
{
    namespace
    {
        constexpr int feet_offset_y = 54 - 32;  // feet relative to the sprite centre (32x64 frames)

        [[nodiscard]] const bn::sprite_item* item_of(npc_id who)
        {
            switch(who)
            {
            case npc_id::mia:
                return &bn::sprite_items::npc_mia;
            case npc_id::rosa:
                return &bn::sprite_items::npc_rosa;
            case npc_id::dex:
                return &bn::sprite_items::npc_dex;
            case npc_id::pimm:
                return &bn::sprite_items::npc_pimm;
            case npc_id::lou:
                return &bn::sprite_items::npc_lou;
            case npc_id::dex_vault:
                return &bn::sprite_items::npc_dex_vault;
            case npc_id::victor:
                return &bn::sprite_items::npc_victor;
            case npc_id::robot:
                return &bn::sprite_items::npc_robot;
            default:
                return nullptr;     // Halloran has no look yet
            }
        }

        [[nodiscard]] bool present(const npc_placement& p, map_id id, int day, int minutes)
        {
            return p.map == id && day >= p.day_min && day <= p.day_max && minutes >= p.from_minute && minutes < p.to_minute;
        }

        BN_DATA_EWRAM_BSS bn::color lit_colours[npcs::max_npcs][16];
    }

    void npcs::clear()
    {
        _npcs.clear();
        _map = nullptr;
    }

    void npcs::load(const map_info& map, map_id id, int day, int minutes)
    {
        clear();
        _map = &map;
        _map_id = id;
        _build(day, minutes);
    }

    void npcs::_build(int day, int minutes)
    {
        _npcs.clear();

        for(int index = 0; index < npc_placements_count && ! _npcs.full(); ++index)
        {
            const npc_placement& p = npc_placements[index];

            if(! present(p, _map_id, day, minutes))
            {
                continue;
            }

            const bn::sprite_item* item = item_of(p.who);

            if(! item)
            {
                continue;
            }

            bn::sprite_ptr sprite = item->create_sprite(0, 0, p.facing);
            sprite.set_bg_priority(_map->player_hidden(p.x, p.y, 12, 56) ? 3 : 2);
            _npcs.push_back(npc{ bn::move(sprite), p.who, p.x, p.y, p.facing, index });
            _blockers[_npcs.size() - 1] = { p.x, p.y };
        }

        _apply_palettes();
        update(_last_cam_x, _last_cam_y);
    }

    void npcs::refresh(int day, int minutes)
    {
        if(! _map)
        {
            return;
        }

        // rebuild only when the set of present placements changed
        bool same = true;
        int found = 0;

        for(int index = 0; index < npc_placements_count; ++index)
        {
            const npc_placement& p = npc_placements[index];

            if(present(p, _map_id, day, minutes) && item_of(p.who))
            {
                if(found >= _npcs.size() || _npcs[found].placement != index)
                {
                    same = false;
                    break;
                }

                ++found;
            }
        }

        if(same && found == _npcs.size())
        {
            return;
        }

        _build(day, minutes);
    }

    void npcs::set_lighting(const light_params& params)
    {
        _light = params;
        _apply_palettes();
    }

    void npcs::_apply_palettes()
    {
        for(int index = 0; index < _npcs.size(); ++index)
        {
            const bn::sprite_item* item = item_of(_npcs[index].who);
            light_colours(item->palette_item().colors_ref().data(), lit_colours[index], 16, _light);
            bn::sprite_palette_ptr palette = _npcs[index].sprite.palette();
            palette.set_colors(bn::span<const bn::color>(lit_colours[index], 16));
        }
    }

    void npcs::update(int cam_x, int cam_y)
    {
        _last_cam_x = cam_x;
        _last_cam_y = cam_y;

        for(npc& n : _npcs)
        {
            int screen_x = _map->to_image_x(n.x, n.y) - cam_x - 120;
            int screen_y = _map->to_image_y(n.x, n.y) - cam_y - 80;
            n.sprite.set_position(screen_x, screen_y - feet_offset_y);
        }
    }

    int npcs::find(int x, int y, int reach, int& d2) const
    {
        int best = -1;
        int best_d2 = 0;

        for(int index = 0; index < _npcs.size(); ++index)
        {
            int dx = x - _npcs[index].x;
            int dy = y - _npcs[index].y;
            int distance = (dx * dx) + (dy * dy);

            if(distance <= reach * reach && (best < 0 || distance < best_d2))
            {
                best = index;
                best_d2 = distance;
            }
        }

        d2 = best_d2;
        return best;
    }

    void npcs::face_towards(int index, int target_x, int target_y)
    {
        // world delta -> screen direction -> facing (s, sw, w, nw, n, ne, e, se), like the player
        int dx = target_x - _npcs[index].x;
        int dy = target_y - _npcs[index].y;
        int sx = dx - dy;           // screen x
        int sy = (dx + dy) / 2;     // screen y
        int ax = sx < 0 ? -sx : sx;
        int ay = sy < 0 ? -sy : sy;
        int facing;

        if(ax * 2 < ay)
        {
            facing = sy > 0 ? 0 : 4;
        }
        else if(ay * 2 < ax)
        {
            facing = sx > 0 ? 6 : 2;
        }
        else if(sx > 0)
        {
            facing = sy > 0 ? 7 : 5;
        }
        else
        {
            facing = sy > 0 ? 1 : 3;
        }

        _npcs[index].facing = facing;
        _npcs[index].sprite.set_tiles(item_of(_npcs[index].who)->tiles_item(), facing);
    }

    void npcs::reset_facings()
    {
        for(npc& n : _npcs)
        {
            int facing = npc_placements[n.placement].facing;

            if(facing != n.facing)
            {
                n.facing = facing;
                n.sprite.set_tiles(item_of(n.who)->tiles_item(), facing);
            }
        }
    }
}
