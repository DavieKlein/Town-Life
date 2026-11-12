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
#include "bn_sprite_items_npc_ines.h"
#include "bn_sprite_items_npc_teo.h"
#include "bn_sprite_items_npc_grigor.h"
#include "bn_sprite_items_npc_valdez.h"
#include "bn_sprite_items_npc_pruitt.h"
#include "bn_sprite_items_npc_kessler.h"
#include "bn_sprite_items_npc_nella.h"
#include "bn_sprite_items_npc_trench_e.h"
#include "bn_sprite_items_npc_duchess.h"
#include "bn_sprite_items_npc_captain.h"

namespace tl
{
    namespace
    {
        constexpr int feet_offset_y = 54 - 32;  // feet relative to the sprite centre (32x64 frames)

        // Sprite sheets: humans have 13 frames per facing (idle + 12 walk frames, same cycle as the player); the hovering robot only the idle one.
        // s76: TRENCH-E 3 is a 64x64 tracked robot (3 frames per facing: idle, dig up, dig down); Duchess and Captain are 32x32 animals drawn
        // facing right (mirrored for left facings; 4 / 2 frames in total, no facings).
        [[nodiscard]] bool is_prop(npc_id who)
        {
            return who == npc_id::trench_e || who == npc_id::duchess || who == npc_id::captain;
        }

        [[nodiscard]] int frames_per_facing(npc_id who)
        {
            return who == npc_id::robot ? 1 : who == npc_id::trench_e ? 3 : who == npc_id::duchess ? 4 : who == npc_id::captain ? 2 : 13;
        }

        // feet relative to the sprite centre, sprite height, and the first graphic of a facing / frame
        [[nodiscard]] int feet_of(npc_id who)
        {
            return who == npc_id::trench_e ? 50 - 32 : (who == npc_id::duchess || who == npc_id::captain) ? 23 - 16 : feet_offset_y;
        }

        [[nodiscard]] int height_of(npc_id who)
        {
            return who == npc_id::trench_e ? 50 : (who == npc_id::duchess || who == npc_id::captain) ? 20 : 56;
        }

        [[nodiscard]] int graphic_of(npc_id who, int facing, int frame)
        {
            if(who == npc_id::duchess || who == npc_id::captain)
            {
                return frame;
            }

            int per = frames_per_facing(who);
            return (facing * per) + (per > 1 ? frame : 0);
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
            case npc_id::ines:
                return &bn::sprite_items::npc_ines;
            case npc_id::teo:
                return &bn::sprite_items::npc_teo;
            case npc_id::grigor:
                return &bn::sprite_items::npc_grigor;
            case npc_id::valdez:
                return &bn::sprite_items::npc_valdez;
            case npc_id::pruitt:
                return &bn::sprite_items::npc_pruitt;
            case npc_id::kessler:
                return &bn::sprite_items::npc_kessler;
            case npc_id::nella:
                return &bn::sprite_items::npc_nella;
            case npc_id::trench_e:
                return &bn::sprite_items::npc_trench_e;
            case npc_id::duchess:
                return &bn::sprite_items::npc_duchess;
            case npc_id::captain:
                return &bn::sprite_items::npc_captain;
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
        _have_pos = false;
        _build(day, minutes);
    }

    // s76: only NPCs near the screen get sprites (the 16 sprite palettes cannot hold every resident of a busy map). `_build` clears the
    // set and remembers which placements are present at this time; `_cull` (every few frames while the player walks free) adds the
    // present placements that came near and removes those that left, with hysteresis.
    namespace
    {
        [[nodiscard]] bool near_screen(int x, int y, int px, int py, int margin_x, int margin_y)
        {
            int sx = (x - px) - (y - py);
            int sy = ((x - px) + (y - py)) / 2;
            sx = sx < 0 ? -sx : sx;
            sy = sy < 0 ? -sy : sy;
            return sx < margin_x && sy < margin_y;
        }
    }

    unsigned npcs::_present_hash(int day, int minutes) const
    {
        unsigned h = 17;

        for(int index = 0; index < npc_placements_count; ++index)
        {
            if(present(npc_placements[index], _map_id, day, minutes) && item_of(npc_placements[index].who))
            {
                h = (h * 31u) + unsigned(index) + 1u;
            }
        }

        return h;
    }

    void npcs::_spawn_placement(int index)
    {
        const npc_placement& p = npc_placements[index];
        const bn::sprite_item* item = item_of(p.who);

        if(! item || _npcs.full())
        {
            return;
        }

        bn::sprite_ptr sprite = item->create_sprite(0, 0, graphic_of(p.who, p.facing, 0));
        _npcs.push_back(npc{ bn::move(sprite), p.who, p.x, p.y, p.facing, index, 0, 0, 0, 0, bn::fixed(p.x), bn::fixed(p.y), p.route, 0,
                             120 + int(index * 37 % 90), false });
        _blockers[_npcs.size() - 1] = { p.x, p.y };
        _set_frame(_npcs.back());
        _set_priority(_npcs.back());
    }

    void npcs::_build(int day, int minutes)
    {
        _npcs.clear();
        _day = day;
        _minutes = minutes;
        _present = _present_hash(day, minutes);

        if(_have_pos && ! _suppress)
        {
            for(int index = 0; index < npc_placements_count && ! _npcs.full(); ++index)
            {
                const npc_placement& p = npc_placements[index];

                if(present(p, _map_id, day, minutes) && near_screen(p.x, p.y, _pos_x, _pos_y, 140, 104))
                {
                    _spawn_placement(index);
                }
            }
        }

        _apply_palettes();
        update(_last_cam_x, _last_cam_y);
    }

    void npcs::focus(int index)
    {
        // s76: during a conversation only the partner keeps a sprite (VRAM is needed for the portrait pieces and the choice layout)
        if(_scripted || index < 0 || index >= _npcs.size())
        {
            return;
        }

        bn::vector<npc, max_npcs> keep;
        keep.push_back(bn::move(_npcs[index]));
        _npcs = bn::move(keep);
        _blockers[0] = { _npcs[0].x, _npcs[0].y };
        _focused = true;
        _apply_palettes();
    }

    void npcs::unfocus()
    {
        if(! _focused)
        {
            return;
        }

        _focused = false;

        for(int pass = 0; pass < max_npcs; ++pass)
        {
            int before = _npcs.size();
            _cull(_pos_x, _pos_y);

            if(_npcs.size() <= before)
            {
                break;
            }
        }
    }

    void npcs::_cull(int px, int py)
    {
        if(_focused)
        {
            return;
        }

        _pos_x = px;
        _pos_y = py;

        if(! _have_pos)
        {
            _have_pos = true;
            _build(_day, _minutes);
            return;
        }

        bool changed = false;

        // remove placed NPCs that are far away (keep the order of the others: the blockers array follows it)
        for(int index = 0; index < _npcs.size(); ++index)
        {
            const npc& n = _npcs[index];

            if(n.placement >= 0 && ! n.walking && ! near_screen(n.x, n.y, px, py, 200, 150))
            {
                bn::vector<npc, max_npcs> keep;

                for(int other = 0; other < _npcs.size(); ++other)
                {
                    if(other != index)
                    {
                        keep.push_back(bn::move(_npcs[other]));
                    }
                }

                _npcs = bn::move(keep);
                changed = true;
                break;      // one per call is enough (called every few frames)
            }
        }

        if(! changed)
        {
            for(int index = 0; index < npc_placements_count && ! _npcs.full(); ++index)
            {
                const npc_placement& p = npc_placements[index];

                if(! present(p, _map_id, _day, _minutes) || ! near_screen(p.x, p.y, px, py, 140, 104))
                {
                    continue;
                }

                bool exists = false;

                for(const npc& n : _npcs)
                {
                    exists = exists || n.placement == index;
                }

                if(! exists && item_of(p.who))
                {
                    // a wandering NPC that left its spot is not respawned on top of the player
                    _spawn_placement(index);
                    changed = true;
                    break;
                }
            }
        }

        if(changed)
        {
            for(int other = 0; other < _npcs.size(); ++other)
            {
                _blockers[other] = { _npcs[other].x, _npcs[other].y };
            }

            _apply_palettes();
            update(_last_cam_x, _last_cam_y);
        }
    }

    void npcs::refresh(int day, int minutes)
    {
        if(! _map || _scripted || _suppress || _focused)
        {
            return;
        }

        _day = day;
        _minutes = minutes;

        // rebuild only when the set of present placements changed
        if(_present_hash(day, minutes) == _present)
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
            int sprite_y = screen_y - feet_of(n.who) - (n.who == npc_id::robot ? (n.bob / 6) % 2 : 0);
            n.sprite.set_position(screen_x, sprite_y);
        }

        // s80: one bitmap recompute per frame (it walks the objects cells); rebuilding the tiles of a changed frame is cheap
        int budget = 1;

        for(npc& n : _npcs)
        {
            if(n.mask_dirty && budget > 0)
            {
                _compute_mask(n);
                --budget;
                n.tiles_dirty = true;
            }

            if(n.tiles_dirty)
            {
                _refresh_tiles(n);
            }
        }
    }

    int npcs::find(int x, int y, int reach, int& d2) const
    {
        int best = -1;
        int best_d2 = 0;

        for(int index = 0; index < _npcs.size(); ++index)
        {
            if(is_prop(_npcs[index].who))
            {
                continue;       // TRENCH-E 3, Duchess and Captain cannot be talked to
            }

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
        bool flip = false;

        if(n.who == npc_id::duchess || n.who == npc_id::captain)
        {
            flip = n.facing >= 1 && n.facing <= 3;      // the art faces right; sw, w, nw look left
            n.sprite.set_horizontal_flip(flip);
        }

        if(flip != n.mask_flip)
        {
            n.mask_dirty = true;
        }

        n.tiles_dirty = true;
    }

    // s80: per-pixel depth for NPCs (replaces the s73 two-part counter hack). The sprite always stands at bg priority 2 (in front of the
    // objects layer); its own copy of the frame loses every pixel that lies under an opaque objects pixel whose iso depth (x + y) is
    // greater than the NPC's feet depth, i.e. objects in front of him cover him, objects behind him do not. Same depth data as the
    // player's front layer (streamed_bg::update_front). The hidden pixels are a bitmap per NPC kind (computed when he moved 6+ units),
    // applied to every new frame (cheap).
    void npcs::_set_priority(npc& n)
    {
        n.sprite.set_bg_priority(2);
        int moved = (n.x > n.mask_x ? n.x - n.mask_x : n.mask_x - n.x) + (n.y > n.mask_y ? n.y - n.mask_y : n.mask_y - n.y);

        if(moved >= 6)
        {
            n.mask_dirty = true;
        }

        if(! n.own_tiles)
        {
            _compute_mask(n);           // first time: at once (no frame with wrong tiles)
            _refresh_tiles(n);
        }
    }

    namespace
    {
        constexpr int hide_words = 128;                 // 64 rows x up to 2 words (64 px wide TRENCH-E)
        BN_DATA_EWRAM_BSS uint32_t npc_hide[int(npc_id::count)][hide_words];
        BN_DATA_EWRAM_BSS uint32_t nibble_mask[256];     // 8 hidden-pixel bits -> 8 nibbles of 0xF
        bool nibble_mask_ready = false;
    }

    void npcs::_compute_mask(npc& n)
    {
        const bn::sprite_item* item = item_of(n.who);
        int w = item->shape_size().width();
        int h = item->shape_size().height();
        uint32_t* hide = npc_hide[int(n.who)];

        for(int index = 0; index < hide_words; ++index)
        {
            hide[index] = 0;
        }

        n.mask_dirty = false;
        n.mask_x = n.x;
        n.mask_y = n.y;
        const layer_data& layer = _map->objects;
        bool flip = n.who == npc_id::duchess || n.who == npc_id::captain ? (n.facing >= 1 && n.facing <= 3) : false;
        n.mask_flip = flip;

        if(! layer.depth)
        {
            return;
        }

        int row_words = w >> 5 ? w >> 5 : 1;
        // TRENCH-E's placeholder model is still baked into the Old Block map under his sprite (x - 0.7..x + 1.5, y +- 0.5 cells): his own
        // depth is moved in front of it so the old geometry does not eat his pixels (remove the baked model with the next Old Block re-render).
        int depth = n.x + n.y + (n.who == npc_id::trench_e ? 40 : 0);
        int left = _map->to_image_x(n.x, n.y) - (w / 2);                        // image coordinates of sprite column 0 / row 0
        int top = _map->to_image_y(n.x, n.y) - (h / 2) - feet_of(n.who);
        int columns = _map->image_width >> 3;
        int rows = _map->image_height >> 3;
        int cx0 = left < 0 ? 0 : left >> 3;
        int cy0 = top < 0 ? 0 : top >> 3;
        int cx1 = (left + w + 7) >> 3;
        int cy1 = (top + h + 7) >> 3;
        cx1 = cx1 > columns ? columns : cx1;
        cy1 = cy1 > rows ? rows : cy1;

        for(int cy = cy0; cy < cy1; ++cy)
        {
            for(int cx = cx0; cx < cx1; ++cx)
            {
                int cell_index = (cy * columns) + cx;
                uint32_t cell = layer.cells[cell_index];
                int tile_id = int(cell & 0xFFFF);

                if(! tile_id)
                {
                    continue;
                }

                uint32_t info = layer.depth[cell_index];
                int base = int(info & 0xFFF);
                int max_offset = int((info >> 12) & 0xF) * 17;
                int block = int(info >> 16);
                bool uniform = block == 0xFFFF;

                if(uniform ? base <= depth : base + max_offset <= depth)
                {
                    continue;           // nothing of this cell is nearer than the NPC
                }

                const uint8_t* offsets = uniform ? nullptr : layer.depth_pixels + (block * 64);
                const uint32_t* source = layer.tiles + (tile_id * 8);
                bool hflip = (cell >> 16) & 1;
                bool vflip = (cell >> 17) & 1;
                int threshold = depth - base;

                for(int row = 0; row < 8; ++row)
                {
                    int sprite_row = (cy * 8) + row - top;

                    if(sprite_row < 0 || sprite_row >= h)
                    {
                        continue;
                    }

                    uint32_t word = source[vflip ? 7 - row : row];

                    if(! word)
                    {
                        continue;
                    }

                    for(int col = 0; col < 8; ++col)
                    {
                        int sprite_col = (cx * 8) + col - left;

                        if(sprite_col < 0 || sprite_col >= w)
                        {
                            continue;
                        }

                        if(((word >> ((hflip ? 7 - col : col) * 4)) & 0xF) == 0)
                        {
                            continue;       // transparent object pixel
                        }

                        if(offsets)
                        {
                            int offset = offsets[(row * 8) + col];

                            if(offset == 255 || offset <= threshold)
                            {
                                continue;   // no pixel, or not nearer than the NPC
                            }
                        }

                        int target_col = flip ? w - 1 - sprite_col : sprite_col;
                        hide[(sprite_row * row_words) + (target_col >> 5)] |= uint32_t(1) << (target_col & 31);
                    }
                }
            }
        }
    }

    void npcs::_refresh_tiles(npc& n)
    {
        const bn::sprite_item* item = item_of(n.who);
        int graphic = graphic_of(n.who, n.facing, n.frame);
        bn::span<const bn::tile> src = item->tiles_item().graphics_tiles_ref(graphic);
        int count = int(src.size());
        int w = item->shape_size().width();
        int tiles_per_row = w >> 3;
        int row_words = w >> 5 ? w >> 5 : 1;

        if(! n.own_tiles)
        {
            n.own_tiles = bn::sprite_tiles_ptr::allocate(count, bn::bpp_mode::BPP_4);
            n.sprite.set_tiles(*n.own_tiles);
        }

        if(! nibble_mask_ready)
        {
            for(int bits = 0; bits < 256; ++bits)
            {
                uint32_t value = 0;

                for(int bit = 0; bit < 8; ++bit)
                {
                    if(bits & (1 << bit))
                    {
                        value |= uint32_t(0xF) << (bit * 4);
                    }
                }

                nibble_mask[bits] = value;
            }

            nibble_mask_ready = true;
        }

        bn::span<bn::tile> dst = *n.own_tiles->vram();
        const uint32_t* hide = npc_hide[int(n.who)];

        for(int index = 0; index < count; ++index)
        {
            int tile_row = index / tiles_per_row;
            int tile_col = index % tiles_per_row;
            int shift = (tile_col & 3) * 8;

            for(int word = 0; word < 8; ++word)
            {
                uint32_t bits = (hide[(((tile_row * 8) + word) * row_words) + (tile_col >> 2)] >> shift) & 0xFF;
                dst[index].data[word] = src[index].data[word] & ~nibble_mask[bits];
            }
        }

        n.tiles_dirty = false;
    }

    void npcs::_walked(npc& n, bn::fixed distance)
    {
        // walk animation driven by the distance walked: frames 1..12, the idle frame 0 when standing
        if(frames_per_facing(n.who) == 1 || n.who == npc_id::trench_e || n.who == npc_id::captain)
        {
            return;
        }

        if(n.who == npc_id::duchess)
        {
            n.anim += distance;
            int dframe = 1 + (n.anim / 5).floor_integer() % 2;     // walkA, walkB

            if(dframe != n.frame)
            {
                n.frame = dframe;
                _set_frame(n);
            }

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

        if(! _have_pos || ++_cull_tick >= 8)
        {
            _cull_tick = 0;
            _cull(player_x, player_y);
        }

        bool moved = false;

        for(int index = 0; index < _npcs.size(); ++index)
        {
            npc& n = _npcs[index];
            _ambient(n);

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

    // s76: idle loops of the props. TRENCH-E 3 digs (idle, up, idle, down); Duchess sits down now and then; Captain flaps his wings.
    void npcs::_ambient(npc& n)
    {
        if(! is_prop(n.who) || n.walking)
        {
            return;
        }

        ++n.tick;
        int frame = n.frame;

        if(n.who == npc_id::trench_e)
        {
            static constexpr int cycle[] = { 0, 1, 1, 0, 2, 2 };
            frame = cycle[(n.tick / 24) % 6];
        }
        else if(n.who == npc_id::duchess)
        {
            frame = ((n.tick + n.placement * 97) / 300) % 3 == 2 ? 3 : 0;      // stands, then sits for a while
        }
        else
        {
            frame = (n.tick % 360) < 10 ? 1 : 0;                                    // a short wing flap every six seconds
        }

        if(frame != n.frame)
        {
            n.frame = frame;
            _set_frame(n);
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

        bn::sprite_ptr sprite = item->create_sprite(0, 0, graphic_of(who, facing, 0));
        _npcs.push_back(npc{ bn::move(sprite), who, x, y, facing, -1, x, y, 0, 0, bn::fixed(x), bn::fixed(y), -1, 0, 0, false });
        _blockers[_npcs.size() - 1] = { x, y };
        _set_frame(_npcs.back());
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
