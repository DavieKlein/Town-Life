#include "tl_streamed_bg.h"

#include "bn_tile.h"
#include "bn_size.h"
#include "bn_color.h"
#include "bn_memory.h"
#include "bn_span.h"
#include "bn_bg_palette_item.h"

namespace tl
{
    struct streamed_bg::storage
    {
        // Open-addressing hash table: tile id -> cache slot (key 0 = empty; tile 0 is never cached).
        uint16_t hash_keys[hash_size];
        uint16_t hash_slots[hash_size];
        uint16_t tile_of_slot[cache_slots];
        uint16_t references[cache_slots];
        uint16_t free_slots[cache_slots];
        uint16_t pending_slots[cache_slots];
        int free_count;
        int pending_count;
    };

    namespace
    {
        alignas(4) BN_DATA_EWRAM_BSS uint8_t storage_memory[2][sizeof(streamed_bg::storage)];
        constexpr int hw_map_size = 32;

        [[nodiscard]] constexpr unsigned hash_of(unsigned tile_id)
        {
            return (tile_id * 2654435761u) >> (32 - streamed_bg::hash_bits);
        }
    }

    int streamed_bg::_find(int tile_id) const
    {
        unsigned index = hash_of(unsigned(tile_id));

        while(true)
        {
            unsigned key = _storage.hash_keys[index];

            if(key == unsigned(tile_id))
            {
                return _storage.hash_slots[index];
            }

            if(key == 0)
            {
                return 0;
            }

            index = (index + 1) & (hash_size - 1);
        }
    }

    void streamed_bg::_insert(int tile_id, int slot)
    {
        unsigned index = hash_of(unsigned(tile_id));

        while(_storage.hash_keys[index])
        {
            index = (index + 1) & (hash_size - 1);
        }

        _storage.hash_keys[index] = uint16_t(tile_id);
        _storage.hash_slots[index] = uint16_t(slot);
    }

    void streamed_bg::_erase(int tile_id)
    {
        unsigned index = hash_of(unsigned(tile_id));

        while(_storage.hash_keys[index] != unsigned(tile_id))
        {
            index = (index + 1) & (hash_size - 1);
        }

        // Backward-shift deletion keeps the probe sequences intact without tombstones.
        unsigned hole = index;
        unsigned next = (index + 1) & (hash_size - 1);

        while(_storage.hash_keys[next])
        {
            unsigned home = hash_of(_storage.hash_keys[next]);
            bool movable = hole <= next ? (home <= hole || home > next) : (home <= hole && home > next);

            if(movable)
            {
                _storage.hash_keys[hole] = _storage.hash_keys[next];
                _storage.hash_slots[hole] = _storage.hash_slots[next];
                hole = next;
            }

            next = (next + 1) & (hash_size - 1);
        }

        _storage.hash_keys[hole] = 0;
    }

    streamed_bg::streamed_bg(int storage_index, const layer_data& data, int image_width, int image_height,
                             int priority, int front_priority) :
        _storage(*reinterpret_cast<storage*>(storage_memory[storage_index])),
        _data(data),
        _columns(image_width / 8),
        _rows(image_height / 8)
    {
        BN_ASSERT(data.tiles_count <= 65535, "Too many tiles: ", data.tiles_count);

        // Reset the cache: slot 0 holds the empty tile and is never freed.
        bn::memory::clear(hash_size, _storage.hash_keys[0]);
        _storage.free_count = 0;
        _storage.pending_count = 0;

        for(int slot = cache_slots - 1; slot > 0; --slot)
        {
            _storage.free_slots[_storage.free_count++] = uint16_t(slot);
            _storage.references[slot] = 0;
        }

        bool front = front_priority >= 0 && data.depth;
        _tiles = bn::regular_bg_tiles_ptr::allocate(cache_slots + (front ? mask_slots * 2 : 0), bn::bpp_mode::BPP_4,
                                                    false);
        bn::bg_palette_item palette_item(bn::span<const bn::color>(data.palette, data.banks * 16),
                                         bn::bpp_mode::BPP_4);
        _palette = bn::bg_palette_ptr::create(palette_item);
        _palette_bank = _palette->id();
        _map = bn::regular_bg_map_ptr::allocate(bn::size(hw_map_size, hw_map_size), *_tiles, *_palette);
        _map_vram = _map->vram()->data();
        bn::memory::clear(hw_map_size * hw_map_size, _map_vram[0]);

        bn::tile* tiles_vram = _tiles->vram()->data();
        bn::memory::clear(1, tiles_vram[0]);

        _bg = bn::regular_bg_ptr::create(*_map);
        _bg->set_priority(priority);

        if(front)
        {
            _front_map = bn::regular_bg_map_ptr::allocate(bn::size(hw_map_size, hw_map_size), *_tiles, *_palette);
            _front_vram = _front_map->vram()->data();
            bn::memory::clear(hw_map_size * hw_map_size, _front_vram[0]);
            _front_bg = bn::regular_bg_ptr::create(*_front_map);
            _front_bg->set_priority(front_priority);
        }
    }

    void streamed_bg::set_palette_colours(const bn::color* colours)
    {
        _palette->set_colors(bn::span<const bn::color>(colours, _data.banks * 16));
    }

    void streamed_bg::clear_front()
    {
        if(! _front_vram)
        {
            return;
        }

        for(int index = 0; index < _front_written_count; ++index)
        {
            _front_vram[_front_written[index]] = 0;
        }

        _front_written_count = 0;
        _front_key_valid = false;
    }

    void streamed_bg::update_front(int x0, int y0, int x1, int y1, int depth)
    {
        if(! _front_vram)
        {
            return;
        }

        // Nothing moved since the last redraw (standing still, dialogue, menus): the front layer in VRAM is still right.
        if(_front_key_valid && _front_key[0] == x0 && _front_key[1] == y0 && _front_key[2] == x1 && _front_key[3] == y1 &&
           _front_key[4] == depth && _front_key[5] == _window_x && _front_key[6] == _window_y)
        {
            return;
        }

        clear_front();
        _front_key[0] = x0;
        _front_key[1] = y0;
        _front_key[2] = x1;
        _front_key[3] = y1;
        _front_key[4] = depth;
        _front_key[5] = _window_x;
        _front_key[6] = _window_y;
        _front_key_valid = true;

        int cx0 = x0 < 0 ? 0 : x0 >> 3;
        int cy0 = y0 < 0 ? 0 : y0 >> 3;
        int cx1 = (x1 + 7) >> 3;
        int cy1 = (y1 + 7) >> 3;
        cx1 = cx1 > _columns ? _columns : cx1;
        cy1 = cy1 > _rows ? _rows : cy1;

        // only cells inside the streamed window have their tiles in VRAM
        cx0 = cx0 < _window_x ? _window_x : cx0;
        cy0 = cy0 < _window_y ? _window_y : cy0;
        cx1 = cx1 > _window_x + window_columns ? _window_x + window_columns : cx1;
        cy1 = cy1 > _window_y + window_rows ? _window_y + window_rows : cy1;

        _front_parity ^= 1;
        int mask_base = cache_slots + (_front_parity * mask_slots);
        int mask_used = 0;
        bn::tile* tiles_vram = _tiles->vram()->data();

        for(int cy = cy0; cy < cy1; ++cy)
        {
            for(int cx = cx0; cx < cx1; ++cx)
            {
                int cell_index = (cy * _columns) + cx;
                uint32_t cell = _data.cells[cell_index];
                int tile_id = int(cell & 0xFFFF);

                if(! tile_id)
                {
                    continue;
                }

                uint32_t info = _data.depth[cell_index];
                int base = int(info & 0xFFF);
                int max_offset = int((info >> 12) & 0xF) * 17;     // upper bound of the per-pixel offsets
                int block = int(info >> 16);
                int map_index = ((cy & (hw_map_size - 1)) * hw_map_size) + (cx & (hw_map_size - 1));

                if(block == 0xFFFF || base > depth)
                {
                    // one depth for the whole cell, or every pixel of it is in front of the player: no mask needed
                    if(base > depth && _front_written_count < front_cells)
                    {
                        _front_vram[map_index] = _map_vram[map_index];
                        _front_written[_front_written_count++] = uint16_t(map_index);
                    }

                    continue;
                }

                if(base + max_offset <= depth || mask_used == mask_slots || _front_written_count == front_cells)
                {
                    continue;
                }

                // Mixed depths in this cell: build a tile with only the pixels in front.
                const uint8_t* offsets = _data.depth_pixels + (block * 64);
                const uint32_t* source = _data.tiles + (tile_id * 8);
                bool hflip = (cell >> 16) & 1;
                bool vflip = (cell >> 17) & 1;
                int threshold = depth - base;     // pixel in front if offset > threshold
                uint32_t rows[8];
                uint32_t any = 0;

                for(int row = 0; row < 8; ++row)
                {
                    uint32_t word = source[vflip ? 7 - row : row];
                    const uint8_t* row_offsets = offsets + (row * 8);
                    uint32_t out = 0;

                    for(int col = 0; col < 8; ++col)
                    {
                        int offset = row_offsets[col];

                        if(offset != 255 && offset > threshold)
                        {
                            int source_col = hflip ? 7 - col : col;
                            out |= ((word >> (source_col * 4)) & 0xF) << (col * 4);
                        }
                    }

                    rows[row] = out;
                    any |= out;
                }

                if(! any)
                {
                    continue;
                }

                int slot = mask_base + mask_used;
                ++mask_used;

                for(int row = 0; row < 8; ++row)
                {
                    tiles_vram[slot].data[row] = rows[row];
                }

                int bank = _palette_bank + int((cell >> 20) & 0xF);
                _front_vram[map_index] = uint16_t(slot | (bank << 12));
                _front_written[_front_written_count++] = uint16_t(map_index);
            }
        }
    }

    streamed_bg::~streamed_bg() = default;

    void streamed_bg::_flush_pending()
    {
        for(int index = 0; index < _storage.pending_count; ++index)
        {
            int slot = _storage.pending_slots[index];

            if(_storage.references[slot] == 0)
            {
                _erase(_storage.tile_of_slot[slot]);
                _storage.free_slots[_storage.free_count++] = uint16_t(slot);
            }
        }

        _storage.pending_count = 0;
    }

    int streamed_bg::_acquire_slot(int tile_id)
    {
        int slot = _find(tile_id);

        if(slot)
        {
            ++_storage.references[slot];
            return slot;
        }

        if(! _storage.free_count)
        {
            // Should not happen with the current window size; recycle released slots right away.
            _flush_pending();

            if(! _storage.free_count)
            {
                return 0;
            }
        }

        slot = _storage.free_slots[--_storage.free_count];
        _insert(tile_id, slot);
        _storage.tile_of_slot[slot] = uint16_t(tile_id);
        _storage.references[slot] = 1;

        const uint32_t* source = _data.tiles + (tile_id * 8);
        bn::tile& destination = _tiles->vram()->data()[slot];

        for(int word = 0; word < 8; ++word)
        {
            destination.data[word] = source[word];
        }

        return slot;
    }

    void streamed_bg::_show_cell(int cx, int cy)
    {
        uint16_t entry = 0;

        if(cx >= 0 && cy >= 0 && cx < _columns && cy < _rows)
        {
            uint32_t cell = _data.cells[(cy * _columns) + cx];
            int tile_id = int(cell & 0xFFFF);

            if(tile_id)
            {
                int slot = _acquire_slot(tile_id);
                int bank = _palette_bank + int((cell >> 20) & 0xF);
                entry = uint16_t(slot | (((cell >> 16) & 1) << 10) | (((cell >> 17) & 1) << 11) | (bank << 12));
            }
        }

        _map_vram[((cy & (hw_map_size - 1)) * hw_map_size) + (cx & (hw_map_size - 1))] = entry;
    }

    void streamed_bg::_hide_cell(int cx, int cy)
    {
        if(cx >= 0 && cy >= 0 && cx < _columns && cy < _rows)
        {
            int tile_id = int(_data.cells[(cy * _columns) + cx] & 0xFFFF);

            if(tile_id)
            {
                int slot = _find(tile_id);

                if(slot && --_storage.references[slot] == 0)
                {
                    _storage.pending_slots[_storage.pending_count++] = uint16_t(slot);
                }
            }
        }
    }

    void streamed_bg::set_view(int cam_x, int cam_y)
    {
        // Slots released during the previous frame are no longer on screen now: recycle them.
        _flush_pending();

        int window_x = cam_x >> 3;
        int window_y = cam_y >> 3;

        if(! _window_valid || window_x != _window_x || window_y != _window_y)
        {
            int old_x = _window_x;
            int old_y = _window_y;
            bool old_valid = _window_valid;

            if(old_valid)
            {
                // Only the cells that left the window are hidden and only the new ones are shown: walk the strips that differ
                // (the old window minus the new one, and the other way round) instead of testing every cell of both windows.
                for(int cy = old_y; cy < old_y + window_rows; ++cy)
                {
                    bool row_inside = cy >= window_y && cy < window_y + window_rows;
                    int first = old_x;
                    int last = old_x + window_columns;

                    if(row_inside)
                    {
                        // left strip [old_x, window_x) and right strip [window_x + columns, old_x + columns)
                        int left_end = window_x < last ? window_x : last;
                        int right_begin = window_x + window_columns > first ? window_x + window_columns : first;

                        for(int cx = first; cx < left_end; ++cx)
                        {
                            _hide_cell(cx, cy);
                        }

                        for(int cx = right_begin; cx < last; ++cx)
                        {
                            _hide_cell(cx, cy);
                        }
                    }
                    else
                    {
                        for(int cx = first; cx < last; ++cx)
                        {
                            _hide_cell(cx, cy);
                        }
                    }
                }

                for(int cy = window_y; cy < window_y + window_rows; ++cy)
                {
                    bool row_inside = cy >= old_y && cy < old_y + window_rows;
                    int first = window_x;
                    int last = window_x + window_columns;

                    if(row_inside)
                    {
                        int left_end = old_x < last ? old_x : last;
                        int right_begin = old_x + window_columns > first ? old_x + window_columns : first;

                        for(int cx = first; cx < left_end; ++cx)
                        {
                            _show_cell(cx, cy);
                        }

                        for(int cx = right_begin; cx < last; ++cx)
                        {
                            _show_cell(cx, cy);
                        }
                    }
                    else
                    {
                        for(int cx = first; cx < last; ++cx)
                        {
                            _show_cell(cx, cy);
                        }
                    }
                }
            }
            else
            {
                for(int cy = window_y; cy < window_y + window_rows; ++cy)
                {
                    for(int cx = window_x; cx < window_x + window_columns; ++cx)
                    {
                        _show_cell(cx, cy);
                    }
                }
            }

            _window_x = window_x;
            _window_y = window_y;
            _window_valid = true;
        }

        // Hardware map wraps every 256 px. Butano places the centre of a 256x256 BG at the screen centre.
        _bg->set_position(8 - (cam_x & 255), 48 - (cam_y & 255));

        if(_front_bg)
        {
            _front_bg->set_position(8 - (cam_x & 255), 48 - (cam_y & 255));
        }
    }
}
