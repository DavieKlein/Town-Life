#include "tl_npcs.h"

#include "tl_story.h"
#include "tl_story_ids.h"

#include "bn_math.h"
#include "bn_sprite_palette_ptr.h"
#include "bn_sprite_builder.h"
#include "bn_sprite_tiles_ptr.h"
#include "bn_sprite_tiles_item.h"
#include "bn_sprite_items_npc_mia.h"
#include "bn_sprite_items_npc_rosa.h"
#include "bn_sprite_items_npc_dex.h"
#include "bn_sprite_items_npc_pimm.h"
#include "bn_sprite_items_npc_lou.h"
#include "bn_sprite_items_npc_dex_vault.h"
#include "bn_sprite_items_npc_victor.h"
#include "bn_sprite_items_npc_robot.h"
#include "bn_sprite_items_npc_okafor.h"

namespace tl
{
    namespace
    {
        constexpr int feet_offset_y = 54 - 32;  // feet relative to the sprite centre (32x64 frames)

        // Sprite sheets: humans have 13 frames per facing (idle + 12 walk frames, same cycle as the player); the hovering robot only the idle one.
        [[nodiscard]] int frames_per_facing(npc_id who)
        {
            return who == npc_id::robot ? 1 : 13;
        }

        constexpr bn::fixed step_length = 2.42;     // world units walked per walk frame (1.36 m stride cycle = 29 units, 12 frames)

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
            case npc_id::okafor:
                return &bn::sprite_items::npc_okafor;
            default:
                return nullptr;     // Halloran has no look yet
            }
        }

        [[nodiscard]] bool present(const npc_placement& p, map_id id, int day, int minutes)
        {
            return p.map == id && day >= p.day_min && day <= p.day_max && minutes >= p.from_minute && minutes < p.to_minute &&
                   (p.flag_on < 0 || story().flag(p.flag_on)) && (p.flag_off < 0 || ! story().flag(p.flag_off));
        }

        BN_DATA_EWRAM_BSS bn::color lit_colours[npcs::max_npcs][16];
    }

    void npcs::clear()
    {
        _npcs.clear();
        _map = nullptr;
        _scripted = false;
        _suppress = false;
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

        for(int index = 0; index < npc_placements_count && ! _npcs.full() && ! _suppress; ++index)
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

            bn::sprite_ptr sprite = item->create_sprite(0, 0, p.facing * frames_per_facing(p.who));
            _npcs.push_back(npc{ bn::move(sprite), bn::optional<bn::sprite_ptr>(), p.who, p.x, p.y, p.facing, index, 0, 0, 0, 0, bn::fixed(p.x), bn::fixed(p.y), p.route, 0,
                                 120 + int(index * 37 % 90), false });
            _blockers[_npcs.size() - 1] = { p.x, p.y };
            _set_priority(_npcs.back());
        }

        _apply_palettes();
        update(_last_cam_x, _last_cam_y);
    }

    void npcs::refresh(int day, int minutes)
    {
        if(! _map || _scripted || _suppress)
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
            int sprite_y = screen_y - feet_offset_y - (frames_per_facing(n.who) == 1 ? (n.bob / 6) % 2 : 0);
            n.sprite.set_position(screen_x, sprite_y);

            if(n.upper)
            {
                n.upper->set_position(screen_x, sprite_y - 16);
            }
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
        _set_frame(_npcs[index]);
    }

    void npcs::_set_frame(npc& n)
    {
        int per = frames_per_facing(n.who);
        n.sprite.set_tiles(item_of(n.who)->tiles_item(), (n.facing * per) + (per > 1 ? n.frame : 0));

        if(n.upper)
        {
            _make_upper(n);
        }
    }

    // s73: the objects layer has ONE priority, so an NPC behind a counter used to be hidden completely (the back wall behind the
    // counter is taller than the NPC) or drawn in front of it entirely. When an NPC stands behind a low occluder but a taller one
    // overlaps his sprite, the legs (full sprite, priority 3) stay behind the counter and the top half (priority 2) is drawn over it.
    void npcs::_set_priority(npc& n)
    {
        bool behind = _map->player_hidden(n.x, n.y, 12, 56);
        bool split = ! behind && _map->player_hidden(n.x, n.y, 12, 56, true);
        n.sprite.set_bg_priority(behind || split ? 3 : 2);

        if(split)
        {
            if(! n.upper)
            {
                _make_upper(n);
                _apply_palettes();
            }
        }
        else
        {
            n.upper.reset();
        }
    }

    void npcs::_make_upper(npc& n)
    {
        const bn::sprite_item* item = item_of(n.who);
        int per = frames_per_facing(n.who);
        int graphic = (n.facing * per) + (per > 1 ? n.frame : 0);
        bn::span<const bn::tile> frame = item->tiles_item().graphics_tiles_ref(graphic);
        // allocated (not created from ROM data): the ROM frame is already registered as a 32-tile graphic
        bn::sprite_tiles_ptr tiles = n.upper ? n.upper->tiles() : bn::sprite_tiles_ptr::allocate(16, bn::bpp_mode::BPP_4);
        bn::span<bn::tile> vram = *tiles.vram();

        for(int index = 0; index < 16; ++index)
        {
            vram[index] = frame[index];
        }

        if(! n.upper)
        {
            bn::sprite_builder builder(bn::sprite_shape_size(bn::sprite_shape::SQUARE, bn::sprite_size::BIG), bn::move(tiles), n.sprite.palette());
            builder.set_bg_priority(2);
            builder.set_position(n.sprite.position().x(), n.sprite.position().y() - 16);
            n.upper = builder.release_build();
        }
    }

    void npcs::_walked(npc& n, bn::fixed distance)
    {
        // walk animation driven by the distance walked: frames 1..12, the idle frame 0 when standing
        if(frames_per_facing(n.who) == 1)
        {
            return;
        }

        n.anim += distance;
        int frame = 1 + (n.anim / step_length).floor_integer() % 12;

        if(frame != n.frame)
        {
            n.frame = frame;
            _set_frame(n);
        }
    }

    void npcs::_stopped(npc& n)
    {
        n.anim = 0;

        if(n.frame != 0)
        {
            n.frame = 0;
            _set_frame(n);
        }
    }

    void npcs::wander(int player_x, int player_y, int talk_index)
    {
        if(! _map || _scripted || _suppress)
        {
            return;
        }

        bool moved = false;

        for(int index = 0; index < _npcs.size(); ++index)
        {
            npc& n = _npcs[index];

            if(n.route < 0 || n.placement < 0 || index == talk_index)
            {
                if(index == talk_index && n.frame != 0)
                {
                    n.walking = false;
                    _stopped(n);
                }

                continue;
            }

            const npc_route& route = npc_routes[n.route];

            if(! n.walking)
            {
                if(n.wait > 0)
                {
                    --n.wait;
                    continue;
                }

                n.route_pos = (n.route_pos + 1) % route.count;
                n.target_x = route.x[n.route_pos];
                n.target_y = route.y[n.route_pos];
                n.walking = true;
                face_towards(index, n.target_x, n.target_y);
            }

            int dx = n.target_x - n.x;
            int dy = n.target_y - n.y;
            int length = bn::sqrt((dx * dx) + (dy * dy));
            bn::fixed step = bn::fixed(0.7);

            if(length <= step)
            {
                n.x = n.target_x;
                n.y = n.target_y;
                n.fx = n.x;
                n.fy = n.y;
                n.walking = false;
                n.bob = 0;
                _stopped(n);
                _wander_seed = (_wander_seed * 1103515245u) + 12345u;
                n.wait = 180 + int((_wander_seed >> 16) % 300);
                _blockers[index] = { n.x, n.y };
                moved = true;
                continue;
            }

            bn::fixed nfx = n.fx + (bn::fixed(dx) * step / length);
            bn::fixed nfy = n.fy + (bn::fixed(dy) * step / length);
            int nx = nfx.round_integer();
            int ny = nfy.round_integer();
            bool blocked = _map->solid_around(nx, ny, 4);
            int pdx = nx - player_x;
            int pdy = ny - player_y;

            if(pdx * pdx + pdy * pdy < 18 * 18)
            {
                // the player is in the way: wait (his position is checked against the NPC's next step)
                _stopped(n);
                continue;
            }

            for(int other = 0; other < _npcs.size() && ! blocked; ++other)
            {
                if(other != index)
                {
                    int odx = nx - _npcs[other].x;
                    int ody = ny - _npcs[other].y;
                    blocked = odx * odx + ody * ody < 14 * 14;
                }
            }

            if(blocked)
            {
                // give up on this leg: wait, then try the next point
                n.walking = false;
                n.wait = 90;
                _stopped(n);
                continue;
            }

            n.fx = nfx;
            n.fy = nfy;
            n.x = nx;
            n.y = ny;
            ++n.bob;
            _walked(n, step);
            _blockers[index] = { n.x, n.y };
            _set_priority(n);
            moved = true;
        }

        if(moved)
        {
            update(_last_cam_x, _last_cam_y);
        }
    }

    void npcs::reset_facings()
    {
        for(npc& n : _npcs)
        {
            if(n.placement < 0)
            {
                continue;
            }

            int facing = npc_placements[n.placement].facing;

            if(facing != n.facing)
            {
                n.facing = facing;
                _set_frame(n);
            }
        }
    }
}

namespace tl
{
    // ---------------------------------------------------------------------------------------------------- cutscene actors
    int npcs::_index_of(npc_id who) const
    {
        for(int index = 0; index < _npcs.size(); ++index)
        {
            if(_npcs[index].who == who)
            {
                return index;
            }
        }

        return -1;
    }

    void npcs::_add_actor(npc_id who, int x, int y, int facing)
    {
        const bn::sprite_item* item = item_of(who);

        if(! item || _npcs.full())
        {
            return;
        }

        bn::sprite_ptr sprite = item->create_sprite(0, 0, facing * frames_per_facing(who));
        _npcs.push_back(npc{ bn::move(sprite), bn::optional<bn::sprite_ptr>(), who, x, y, facing, -1, x, y, 0, 0, bn::fixed(x), bn::fixed(y), -1, 0, 0, false });
        _blockers[_npcs.size() - 1] = { x, y };
        _set_priority(_npcs.back());
        _apply_palettes();
        update(_last_cam_x, _last_cam_y);
    }

    void npcs::spawn(npc_id who, int x, int y, int facing)
    {
        _scripted = true;
        despawn(who);
        _add_actor(who, x, y, facing);
    }

    void npcs::despawn(npc_id who)
    {
        _scripted = true;
        int index = _index_of(who);

        if(index < 0)
        {
            return;
        }

        // keep the order of the others (the blockers array follows it)
        bn::vector<npc, max_npcs> keep;

        for(int other = 0; other < _npcs.size(); ++other)
        {
            if(other != index)
            {
                keep.push_back(bn::move(_npcs[other]));
            }
        }

        _npcs = bn::move(keep);

        for(int other = 0; other < _npcs.size(); ++other)
        {
            _blockers[other] = { _npcs[other].x, _npcs[other].y };
        }

        _apply_palettes();
    }

    void npcs::swap(npc_id from, npc_id to)
    {
        int index = _index_of(from);

        if(index < 0)
        {
            return;
        }

        int x = _npcs[index].x;
        int y = _npcs[index].y;
        int facing = _npcs[index].facing;
        spawn(to, x, y, facing);
    }

    void npcs::move_to(npc_id who, int x, int y, bool fast)
    {
        int index = _index_of(who);

        if(index < 0)
        {
            return;
        }

        _npcs[index].target_x = x;
        _npcs[index].target_y = y;
        _npcs[index].speed = fast ? 3 : 2;      // in half units per frame (1 and 1.5 units)
        face_towards(index, x, y);
    }

    void npcs::set_facing(npc_id who, int facing)
    {
        int index = _index_of(who);

        if(index >= 0)
        {
            _npcs[index].facing = facing;
            _set_frame(_npcs[index]);
        }
    }

    void npcs::face_actor_towards(npc_id who, int target_x, int target_y)
    {
        int index = _index_of(who);

        if(index >= 0)
        {
            face_towards(index, target_x, target_y);
        }
    }

    bool npcs::moving() const
    {
        for(const npc& n : _npcs)
        {
            if(n.speed)
            {
                return true;
            }
        }

        return false;
    }

    void npcs::tick()
    {
        for(int index = 0; index < _npcs.size(); ++index)
        {
            npc& n = _npcs[index];

            if(! n.speed)
            {
                continue;
            }

            int dx = n.target_x - n.x;
            int dy = n.target_y - n.y;
            int length = bn::sqrt((dx * dx) + (dy * dy));
            bn::fixed step = n.speed == 3 ? bn::fixed(1.5) : bn::fixed(1);

            if(length <= step)
            {
                n.x = n.target_x;
                n.y = n.target_y;
                n.fx = n.x;
                n.fy = n.y;
                n.speed = 0;
                n.bob = 0;
                _stopped(n);
            }
            else
            {
                n.fx += bn::fixed(dx) * step / length;
                n.fy += bn::fixed(dy) * step / length;
                n.x = n.fx.round_integer();
                n.y = n.fy.round_integer();
                ++n.bob;
                _walked(n, step);
            }

            _blockers[index] = { n.x, n.y };
            _set_priority(n);
        }

        update(_last_cam_x, _last_cam_y);
    }

    void npcs::set_suppress(bool suppress)
    {
        _suppress = suppress;
        _scripted = true;

        if(suppress)
        {
            _npcs.clear();
        }
    }

    void npcs::release(int day, int minutes)
    {
        _scripted = false;
        _suppress = false;
        _build(day, minutes);
    }
}
