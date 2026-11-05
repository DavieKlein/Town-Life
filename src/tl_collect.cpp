#include "tl_collect.h"

#include "bn_sprite_palette_ptr.h"
#include "bn_sprite_items_collectibles.h"

#include "tl_collect_spots.h"

namespace tl
{
    namespace
    {
        constexpr int twinkle_frames = 30;
    }

    void collectibles::load(const map_info& map)
    {
        clear();
        _city = &map == &get_map(map_id::city_centre);

        if(_city)
        {
            _rebuild();
        }
    }

    void collectibles::clear()
    {
        _sprites.clear();
        _sprite_item.clear();
        _city = false;
    }

    void collectibles::set_lighting(const light_params& params)
    {
        _light = params;

        if(! _sprites.empty())
        {
            bn::color colours[16];
            light_colours(bn::sprite_items::collectibles.palette_item().colors_ref().data(), colours, 16, _light);
            bn::sprite_palette_ptr palette = _sprites[0].palette();
            palette.set_colors(bn::span<const bn::color>(colours, 16));
        }
    }

    void collectibles::_rebuild()
    {
        _sprites.clear();
        _sprite_item.clear();

        for(int index = 0; index < count; ++index)
        {
            if(! found(index))
            {
                bn::sprite_ptr sprite = bn::sprite_items::collectibles.create_sprite(0, 0);
                sprite.set_bg_priority(3);          // behind the objects layer, above the floor (like the deposit pickups)
                sprite.set_z_order(3);
                sprite.set_visible(false);
                _sprites.push_back(bn::move(sprite));
                _sprite_item.push_back(index);
            }
        }

        set_lighting(_light);
    }

    int collectibles::found_in_set(int set) const
    {
        int n = 0;

        for(int item = 0; item < 4; ++item)
        {
            n += found((set * 4) + item) ? 1 : 0;
        }

        return n;
    }

    int collectibles::find(int x, int y, int reach, int& d2) const
    {
        int best = -1;
        int best_d2 = reach * reach + 1;

        if(! _city)
        {
            return -1;
        }

        for(int index = 0; index < count; ++index)
        {
            if(! found(index))
            {
                int dx = collect_spots[index].x - x;
                int dy = collect_spots[index].y - y;
                int distance = (dx * dx) + (dy * dy);

                if(distance < best_d2)
                {
                    best_d2 = distance;
                    best = index;
                }
            }
        }

        d2 = best_d2;
        return best;
    }

    int collectibles::collect(int index)
    {
        if(index < 0 || index >= count || found(index))
        {
            return 0;
        }

        mask = uint16_t(mask | (1 << index));

        if(_city)
        {
            _rebuild();
        }

        return found_in_set(index / 4);
    }

    void collectibles::update(const map_info& map, int cam_x, int cam_y)
    {
        ++_frame;

        for(int i = 0; i < _sprites.size(); ++i)
        {
            int index = _sprite_item[i];
            const collect_spot& place = collect_spots[index];
            int sx = map.to_image_x(place.x, place.y) - cam_x;
            int sy = map.to_image_y(place.x, place.y) - cam_y;
            bool visible = sx > -16 && sx < 256 && sy > -8 && sy < 128 + 16;
            bn::sprite_ptr& sprite = _sprites[i];
            sprite.set_visible(visible);

            if(visible)
            {
                int twinkle = ((_frame + (index * 11)) / twinkle_frames) % 2;
                sprite.set_position(sx - 120, sy - 80);
                sprite.set_tiles(bn::sprite_items::collectibles.tiles_item(), (index * 2) + twinkle);
            }
        }
    }
}
