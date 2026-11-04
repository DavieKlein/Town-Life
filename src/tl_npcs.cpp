#include "tl_npcs.h"

#include "bn_sprite_items_npc_mia.h"

namespace tl
{
    namespace
    {
        constexpr int feet_offset_y = 54 - 32;  // feet relative to the sprite centre (32x64 frames)
    }

    void npcs::clear()
    {
        _npcs.clear();
        _map = nullptr;
    }

    void npcs::load(const map_info& map)
    {
        clear();
        _map = &map;

        for(int index = 0; index < map.npcs_count && ! _npcs.full(); ++index)
        {
            const npc_spawn& spawn = map.npcs[index];
            bn::sprite_ptr sprite = bn::sprite_items::npc_mia.create_sprite(0, 0, spawn.facing);
            sprite.set_bg_priority(map.player_hidden(spawn.x, spawn.y, 12, 56) ? 3 : 2);
            _npcs.push_back(npc{ bn::move(sprite), &spawn });
        }
    }

    void npcs::update(int cam_x, int cam_y)
    {
        for(npc& n : _npcs)
        {
            int screen_x = _map->to_image_x(n.spawn->x, n.spawn->y) - cam_x - 120;
            int screen_y = _map->to_image_y(n.spawn->x, n.spawn->y) - cam_y - 80;
            n.sprite.set_position(screen_x, screen_y - feet_offset_y);
        }
    }
}
