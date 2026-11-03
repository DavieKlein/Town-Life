#ifndef TL_STREAMED_BG_H
#define TL_STREAMED_BG_H

#include "bn_optional.h"
#include "bn_bg_palette_ptr.h"
#include "bn_regular_bg_ptr.h"
#include "bn_regular_bg_map_ptr.h"
#include "bn_regular_bg_tiles_ptr.h"

#include "tl_world.h"

namespace tl
{
    // A regular BG showing a big pre-rendered layer (thousands of unique 4bpp tiles) through a
    // 32x32 hardware map that wraps around. Only the tiles of the cells inside the visible window are
    // kept in VRAM (reference counted tile cache); new cells are streamed in as the camera moves.
    class streamed_bg
    {

    public:
        static constexpr int window_columns = 31;   // 240 px + 1 partial cell
        static constexpr int window_rows = 18;      // 128 px play area above the HUD + 1 partial cell
        static constexpr int cache_slots = 624;     // window cells + cells released during one frame
        static constexpr int max_tiles = 8192;      // unique tiles per layer

        // storage_index: 0 or 1 (each streamed_bg alive at the same time needs its own storage).
        streamed_bg(int storage_index, const layer_data& data, int image_width, int image_height, int priority);

        ~streamed_bg();

        streamed_bg(const streamed_bg&) = delete;
        streamed_bg& operator=(const streamed_bg&) = delete;

        // Shows the image area whose top-left corner is (cam_x, cam_y) at the top-left of the screen.
        void set_view(int cam_x, int cam_y);

        struct storage;

    private:
        storage& _storage;
        const layer_data& _data;
        int _columns;
        int _rows;
        bn::optional<bn::regular_bg_tiles_ptr> _tiles;
        bn::optional<bn::bg_palette_ptr> _palette;
        bn::optional<bn::regular_bg_map_ptr> _map;
        bn::optional<bn::regular_bg_ptr> _bg;
        uint16_t* _map_vram = nullptr;
        int _palette_bank = 0;
        int _window_x = 0;
        int _window_y = 0;
        bool _window_valid = false;

        void _flush_pending();
        [[nodiscard]] int _acquire_slot(int tile_id);
        void _show_cell(int cx, int cy);
        void _hide_cell(int cx, int cy);
    };
}

#endif
