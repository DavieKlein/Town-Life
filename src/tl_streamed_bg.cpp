#include "tl_streamed_bg.h"

#include "bn_tile.h"
#include "bn_size.h"
#include "bn_color.h"
#include "bn_memory.h"
#include "bn_bg_palette_item.h"

namespace tl
{
    struct streamed_bg::storage
    {
        uint16_t slot_of_tile[max_tiles];   // 0 = not loaded
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
    }

    streamed_bg::streamed_bg(int storage_index, const layer_data& data, int image_width, int image_height,
                             int priority) :
        _storage(*reinterpret_cast<storage*>(storage_memory[storage_index])),
        _data(data),
        _columns(image_width / 8),
        _rows(image_height / 8)
    {
        BN_ASSERT(data.tiles_count <= max_tiles, "Too many tiles: ", data.tiles_count);

        // Reset the cache: slot 0 holds the empty tile and is never freed.
        bn::memory::clear(max_tiles, _storage.slot_of_tile[0]);
        _storage.free_count = 0;
        _storage.pending_count = 0;

        for(int slot = cache_slots - 1; slot > 0; --slot)
        {
            _storage.free_slots[_storage.free_count++] = uint16_t(slot);
            _storage.references[slot] = 0;
        }

        _tiles = bn::regular_bg_tiles_ptr::allocate(cache_slots, bn::bpp_mode::BPP_4, false);
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
    }

    streamed_bg::~streamed_bg() = default;

    void streamed_bg::_flush_pending()
    {
        for(int index = 0; index < _storage.pending_count; ++index)
        {
            int slot = _storage.pending_slots[index];

            if(_storage.references[slot] == 0)
            {
                _storage.slot_of_tile[_storage.tile_of_slot[slot]] = 0;
                _storage.free_slots[_storage.free_count++] = uint16_t(slot);
            }
        }

        _storage.pending_count = 0;
    }

    int streamed_bg::_acquire_slot(int tile_id)
    {
        int slot = _storage.slot_of_tile[tile_id];

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
        _storage.slot_of_tile[tile_id] = uint16_t(slot);
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
                int slot = _storage.slot_of_tile[tile_id];

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
                for(int cy = old_y; cy < old_y + window_rows; ++cy)
                {
                    bool row_inside = cy >= window_y && cy < window_y + window_rows;

                    for(int cx = old_x; cx < old_x + window_columns; ++cx)
                    {
                        if(! row_inside || cx < window_x || cx >= window_x + window_columns)
                        {
                            _hide_cell(cx, cy);
                        }
                    }
                }
            }

            for(int cy = window_y; cy < window_y + window_rows; ++cy)
            {
                bool row_inside = old_valid && cy >= old_y && cy < old_y + window_rows;

                for(int cx = window_x; cx < window_x + window_columns; ++cx)
                {
                    if(! row_inside || cx < old_x || cx >= old_x + window_columns)
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
    }
}
