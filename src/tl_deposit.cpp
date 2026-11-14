#include "tl_palette.h"
#include "tl_deposit.h"

#include "bn_sprite_palette_ptr.h"
#include "bn_sprite_items_pickups.h"

#include "tl_deposit_spots.h"

namespace tl
{
    namespace
    {
        static_assert(pickup_spots_count <= deposit::max_spots);

        constexpr int twinkle_frames = 24;
        constexpr int centre_offset = 3;        // the 16x16 frame is drawn 3 px above the spot, so the item lies on it
    }

    void deposit::load(const map_info& map)
    {
        clear();
        _map = int(&map - &get_map(map_id(0)));
        _city = true;       // any map may hold spots; _rebuild only shows those of the current map
        _rebuild();
    }

    void deposit::clear()
    {
        _sprites.clear();
        _sprite_spot.clear();
        _city = false;
        _map = -1;
    }

    void deposit::set_lighting(const light_params& params)
    {
        _light = params;

        if(! _sprites.empty())
        {
            bn::color colours[16];
            light_colours(bn::sprite_items::pickups.palette_item().colors_ref().data(), colours, 16, _light);
            bn::sprite_palette_ptr palette = _sprites[0].palette();
            palette.set_colors(bn::span<const bn::color>(colours, 16));
        }
    }

    void deposit::_rebuild()
    {
        _sprites.clear();
        _sprite_spot.clear();

        for(int index = 0; index < pickup_spots_count && ! _sprites.full(); ++index)
        {
            if(spot[index] && int(pickup_spots[index].map) == _map)
            {
                bn::optional<bn::sprite_ptr> sprite = palette_room(2) ? bn::sprite_items::pickups.create_sprite_optional(0, 0) : bn::optional<bn::sprite_ptr>();

                if(! sprite)
                {
                    break;          // s83: no palette / tiles free: no pickups for now
                }

                sprite->set_bg_priority(3);          // behind the objects layer (under benches), above the floor
                sprite->set_z_order(3);
                sprite->set_visible(false);
                _sprites.push_back(bn::move(*sprite));
                _sprite_spot.push_back(index);
            }
        }

        set_lighting(_light);
    }

    int deposit::loose_credits() const
    {
        int total = 0;

        for(int index = 0; index < pickup_spots_count; ++index)
        {
            if(spot[index])
            {
                ++total;        // every can and every bottle is worth exactly $1
            }
        }

        return total;
    }

    int deposit::loose_on_map(int map) const
    {
        int total = 0;

        for(int index = 0; index < pickup_spots_count; ++index)
        {
            if(spot[index] && int(pickup_spots[index].map) == map)
            {
                ++total;
            }
        }

        return total;
    }

    void deposit::top_up(bn::random& rng)
    {
        // at most max_loose_per_map items lie around on each map
        for(int attempt = 0; attempt < 160; ++attempt)
        {
            int index = rng.get_unbiased_int(pickup_spots_count);

            if(spot[index] || loose_on_map(int(pickup_spots[index].map)) >= max_loose_per_map)
            {
                continue;
            }

            const pickup_spot& place = pickup_spots[index];
            bool bottle = rng.get_unbiased_int(100) < 40;

            if(bottle && ! place.bottle_ok)
            {
                bottle = false;
            }

            if(! bottle && ! place.can_ok)
            {
                if(place.bottle_ok)
                {
                    bottle = true;
                }
                else
                {
                    continue;
                }
            }

            spot[index] = uint8_t((bottle ? 2 : 1) | (rng.get_unbiased_int(3) << 2));
        }

        if(_city)
        {
            _rebuild();
        }
    }

    int deposit::find(int x, int y, int reach, int& d2) const
    {
        int best = -1;
        int best_d2 = reach * reach + 1;

        if(! _city)
        {
            return -1;
        }

        for(int index = 0; index < pickup_spots_count; ++index)
        {
            if(spot[index] && int(pickup_spots[index].map) == _map)
            {
                int dx = pickup_spots[index].x - x;
                int dy = pickup_spots[index].y - y;
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

    void deposit::collect(int index)
    {
        if(index < 0 || index >= pickup_spots_count || ! spot[index])
        {
            return;
        }

        if((spot[index] & 3) == 2)
        {
            ++bag_bottles;
        }
        else
        {
            ++bag_cans;
        }

        spot[index] = 0;

        if(_city)
        {
            _rebuild();
        }
    }

    int deposit::return_all()
    {
        int dollars = bag_total();
        bag_cans = 0;
        bag_bottles = 0;
        credit = 0;
        return dollars;
    }

    void deposit::update(const map_info& map, int cam_x, int cam_y)
    {
        ++_frame;

        for(int i = 0; i < _sprites.size(); ++i)
        {
            int index = _sprite_spot[i];
            const pickup_spot& place = pickup_spots[index];
            int sx = map.to_image_x(place.x, place.y) - cam_x;
            int sy = map.to_image_y(place.x, place.y) - cam_y;
            bool visible = sx > -16 && sx < 256 && sy > -8 && sy < 128 + 16;
            bn::sprite_ptr& sprite = _sprites[i];
            sprite.set_visible(visible);

            if(visible)
            {
                int item = ((spot[index] & 3) == 2 ? 3 : 0) + ((spot[index] >> 2) % 3);
                int twinkle = ((_frame + (index * 7)) / twinkle_frames) % 2;
                sprite.set_position(sx - 120, sy - centre_offset - 80);
                sprite.set_tiles(bn::sprite_items::pickups.tiles_item(), (item * 2) + twinkle);
            }
        }
    }
}
