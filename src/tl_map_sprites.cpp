#include "tl_map_sprites.h"

#include "bn_sprite_palette_ptr.h"
#include "bn_sprite_items_map_sprites.h"

#include "tl_map_sprite_data.h"
#include "tl_story.h"

namespace tl
{
    void map_sprites::load(const map_info& map)
    {
        clear();
        int id = int(&map - &get_map(map_id(0)));

        for(int index = 0; index < map_sprite_count && ! _sprites.full(); ++index)
        {
            if(int(map_sprite_table[index].map) == id)
            {
                bn::sprite_ptr sprite = bn::sprite_items::map_sprites.create_sprite(0, 0, map_sprite_table[index].frame);
                sprite.set_bg_priority(3);          // behind the objects layer, in front of the floor (like the pickups)
                sprite.set_z_order(3);
                sprite.set_visible(false);
                _sprites.push_back(bn::move(sprite));
                _entry.push_back(index);
            }
        }

        set_lighting(_light);
    }

    void map_sprites::clear()
    {
        _sprites.clear();
        _entry.clear();
    }

    void map_sprites::set_lighting(const light_params& params)
    {
        _light = params;

        if(! _sprites.empty())
        {
            bn::color colours[16];
            light_colours(bn::sprite_items::map_sprites.palette_item().colors_ref().data(), colours, 16, _light);
            bn::sprite_palette_ptr palette = _sprites[0].palette();
            palette.set_colors(bn::span<const bn::color>(colours, 16));
        }
    }

    void map_sprites::update(const map_info& map, int cam_x, int cam_y)
    {
        for(int i = 0; i < _sprites.size(); ++i)
        {
            const map_sprite& entry = map_sprite_table[_entry[i]];
            bool shown = (entry.flag_on < 0 || story().flag(entry.flag_on)) && (entry.flag_off < 0 || ! story().flag(entry.flag_off));
            int sx = map.to_image_x(entry.x, entry.y) - cam_x;
            int sy = map.to_image_y(entry.x, entry.y) - cam_y;
            bool visible = shown && sx > -40 && sx < 300 && sy > -40 && sy < 200;
            bn::sprite_ptr& sprite = _sprites[i];
            sprite.set_visible(visible);

            if(visible)
            {
                // the frame's anchor point lies at (anchor_x, anchor_y) inside the 64x32 frame
                sprite.set_position(sx - entry.anchor_x + 32 - 120, sy - entry.anchor_y + 16 - 80);
            }
        }
    }
}
