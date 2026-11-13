#include "tl_ui.h"

#include "bn_color.h"
#include "bn_sprite_ptr.h"
#include "bn_sprite_tiles_ptr.h"
#include "bn_sprite_palette_ptr.h"
#include "bn_sprite_palettes.h"
#include "bn_sprites.h"
#include "bn_optional.h"
#include "bn_sprite_palette_item.h"
#include "bn_sprite_items_ui_pan_te.h"
#include "bn_sprite_items_ui_pan_tm.h"
#include "bn_sprite_items_ui_pan_ne.h"
#include "bn_sprite_items_ui_pan_nm.h"
#include "bn_sprite_items_ui_pan_be.h"
#include "bn_sprite_items_ui_pan_bm.h"
#include "bn_sprite_items_ui_pan_de.h"
#include "bn_sprite_items_ui_pan_dm.h"
#include "bn_sprite_items_ui_bar_l.h"
#include "bn_sprite_items_ui_bar_m.h"
#include "bn_sprite_items_ui_bar_r.h"
#include "bn_sprite_items_ui_icons.h"

namespace tl::ui
{
    namespace
    {
        // Palette indices (tools/ui_assets.py).
        enum : int
        {
            i_transp, i_panel, i_border, i_edge, i_title_bg, i_title_out, i_text, i_bar, i_bar_edge, i_bar_text,
            i_hint, i_text_out, i_white, i_gold, i_money, i_navy
        };

        constexpr bn::color rgb(int r, int g, int b)
        {
            return bn::color(r >> 3, g >> 3, b >> 3);
        }

        // Variant A "Paper" (day).
        constexpr bn::color paper_colours[16] = {
            rgb(255, 0, 255), rgb(244, 232, 200), rgb(70, 46, 34), rgb(255, 250, 232), rgb(200, 76, 52),
            rgb(96, 28, 20), rgb(50, 34, 30), rgb(250, 200, 64), rgb(110, 66, 24), rgb(50, 34, 30),
            rgb(110, 90, 80), rgb(244, 232, 200), rgb(255, 255, 255), rgb(255, 214, 92), rgb(150, 100, 10),
            rgb(10, 12, 30)
        };

        // Variant B "Night".
        constexpr bn::color night_colours[16] = {
            rgb(255, 0, 255), rgb(24, 30, 62), rgb(150, 176, 230), rgb(60, 72, 130), rgb(14, 18, 40),
            rgb(14, 18, 40), rgb(255, 255, 255), rgb(46, 196, 182), rgb(190, 255, 246), rgb(8, 24, 44),
            rgb(170, 186, 230), rgb(10, 12, 30), rgb(255, 255, 255), rgb(255, 214, 92), rgb(255, 214, 92),
            rgb(10, 12, 30)
        };

        constexpr bn::sprite_palette_item paper_item(bn::span<const bn::color>(paper_colours), bn::bpp_mode::BPP_4);
        constexpr bn::sprite_palette_item night_item(bn::span<const bn::color>(night_colours), bn::bpp_mode::BPP_4);

        bool night_style = false;

        [[nodiscard]] bn::sprite_palette_ptr style_palette()
        {
            return bn::sprite_palette_ptr::create(night_style ? night_item : paper_item);
        }

        struct role_colours
        {
            uint8_t fill;
            uint8_t outline;
        };

        [[nodiscard]] role_colours colours_of(role r)
        {
            switch(r)
            {
            case role::selected:
                return { i_bar_text, i_bar };
            case role::title:
                return night_style ? role_colours{ i_gold, i_title_bg } : role_colours{ i_white, i_title_out };
            case role::hint:
                return { i_hint, i_text_out };
            case role::money:
                return { i_money, i_text_out };
            case role::hud_clock:
                return { i_white, i_navy };
            case role::hud_money:
                return { i_gold, i_navy };
            case role::name_tag:
                return { i_gold, night_style ? i_title_bg : i_title_out };
            default:
                return { i_text, i_text_out };
            }
        }

        constexpr int cell_margin = 2;          // ink starts at column 2 of a glyph cell
        constexpr int max_buffer_width = 256;

        BN_DATA_EWRAM_BSS uint8_t line_buffer[16 * max_buffer_width];

        [[nodiscard]] int glyph_index(char c)
        {
            int code = uint8_t(c);
            return (code < 32 || code > 126) ? ('?' - 32) : (code - 32);
        }

        // s81: every UI piece is optional: when VRAM / OAM is short the piece is simply not drawn (never a crash)
        [[nodiscard]] bn::optional<bn::sprite_ptr> place(const bn::sprite_item& item, int x, int y, int graphics, bool hflip, int z)
        {
            bn::optional<bn::sprite_tiles_ptr> tiles = item.tiles_item().create_tiles_optional(graphics);

            if(! tiles)
            {
                return bn::nullopt;
            }

            bn::optional<bn::sprite_ptr> sprite = bn::sprite_ptr::create_optional(
                    x + (item.shape_size().width() / 2) - 120, y + (item.shape_size().height() / 2) - 80,
                    item.shape_size(), bn::move(*tiles), style_palette());

            if(sprite)
            {
                sprite->set_bg_priority(0);
                sprite->set_z_order(z);
                sprite->set_horizontal_flip(hflip);
            }

            return sprite;
        }

        void add(bn::ivector<bn::sprite_ptr>& list, bn::optional<bn::sprite_ptr>&& sprite)
        {
            if(sprite && ! list.full())
            {
                list.push_back(bn::move(*sprite));
            }
        }
    }

    void black_card_palette()
    {
        bn::sprite_palettes::set_fade(bn::color(0, 0, 0), 1);
        bn::sprite_palette_ptr palette = style_palette();
        palette.set_fade(bn::color(0, 0, 0), 0);
    }

    void set_night(bool value)
    {
        night_style = value;
    }

    bool night()
    {
        return night_style;
    }

    int text_width(const font_data& font, const bn::string_view& text)
    {
        int width = 0;

        for(char c : text)
        {
            width += font.widths[glyph_index(c)];
        }

        return width;
    }

    // ---------------------------------------------------------------------------------------------------------

    void label::set(const font_data& font, int x, int baseline_y, const bn::string_view& text, role r, int z_order)
    {
        _sprites.clear();
        int width = text_width(font, text) + 4;

        if(text.empty())
        {
            return;
        }

        if(width > max_buffer_width)
        {
            width = max_buffer_width;
        }

        int chunks = (width + 31) / 32;
        int stride = chunks * 32;

        for(int index = 0; index < 16 * stride; ++index)
        {
            line_buffer[index] = 0;
        }

        role_colours colours = colours_of(r);
        int pen = 0;

        for(char c : text)
        {
            int glyph = glyph_index(c);
            const uint32_t* rows = font.rows + (glyph * 16);

            for(int row = 0; row < 16; ++row)
            {
                uint32_t bits = rows[row];

                if(! bits)
                {
                    continue;
                }

                uint8_t* line = line_buffer + (row * stride) + pen;

                for(int col = 0; col < 16; ++col)
                {
                    int value = (bits >> (2 * col)) & 3;

                    if(! value || pen + col >= stride)
                    {
                        continue;
                    }

                    if(value == 1)
                    {
                        line[col] = colours.fill;
                    }
                    else if(! line[col])
                    {
                        line[col] = colours.outline;
                    }
                }
            }

            pen += font.widths[glyph];
        }

        int top = baseline_y - font.baseline;
        bn::sprite_palette_ptr palette = style_palette();

        for(int chunk = 0; chunk < chunks && ! _sprites.full(); ++chunk)
        {
            bool empty = true;

            for(int row = 0; row < 16 && empty; ++row)
            {
                const uint8_t* line = line_buffer + (row * stride) + (chunk * 32);

                for(int col = 0; col < 32; ++col)
                {
                    if(line[col])
                    {
                        empty = false;
                        break;
                    }
                }
            }

            if(empty)
            {
                continue;
            }

            // s81: optional text must never crash the game: when VRAM / OAM is short this piece of the text is simply not drawn
            bn::optional<bn::sprite_tiles_ptr> maybe_tiles = bn::sprite_tiles_ptr::allocate_optional(8, bn::bpp_mode::BPP_4);

            if(! maybe_tiles || bn::sprites::available_items_count() < 1)
            {
                continue;
            }

            bn::sprite_tiles_ptr tiles = *maybe_tiles;
            maybe_tiles.reset();
            bn::span<bn::tile> vram = *tiles.vram();

            for(int ty = 0; ty < 2; ++ty)
            {
                for(int tx = 0; tx < 4; ++tx)
                {
                    bn::tile& tile = vram[(ty * 4) + tx];

                    for(int row = 0; row < 8; ++row)
                    {
                        const uint8_t* line = line_buffer + (((ty * 8) + row) * stride) + (chunk * 32) + (tx * 8);
                        uint32_t word = 0;

                        for(int px = 0; px < 8; ++px)
                        {
                            word |= uint32_t(line[px]) << (4 * px);
                        }

                        tile.data[row] = word;
                    }
                }
            }

            int left = x - cell_margin + (chunk * 32);
            bn::sprite_ptr sprite = bn::sprite_ptr::create(left + 16 - 120, top + 8 - 80, bn::sprite_shape_size(32, 16),
                                                           bn::move(tiles), palette);
            sprite.set_bg_priority(0);
            sprite.set_z_order(z_order);
            _sprites.push_back(bn::move(sprite));
        }
    }

    void label::set_right(const font_data& font, int right_x, int baseline_y, const bn::string_view& text, role r)
    {
        set(font, right_x - text_width(font, text), baseline_y, text, r);
    }

    void label::set_centre(const font_data& font, int centre_x, int baseline_y, const bn::string_view& text, role r)
    {
        set(font, centre_x - (text_width(font, text) / 2), baseline_y, text, r);
    }

    // ---------------------------------------------------------------------------------------------------------

    void panel::open(int x, int y, int w, int h, bool titled)
    {
        close();

        if(h > 64 && h < 72)
        {
            h = 72;         // the body pieces are 64 high: heights in between would leak into the rounded corners
        }

        if(h < (titled ? 49 : 36))
        {
            h = titled ? 49 : 36;      // the bottom pieces must not cover the top border / title band
        }

        const bn::sprite_item& top_e = titled ? bn::sprite_items::ui_pan_te : bn::sprite_items::ui_pan_ne;
        const bn::sprite_item& top_m = titled ? bn::sprite_items::ui_pan_tm : bn::sprite_items::ui_pan_nm;

        // One row of pieces: both ends (the right one flipped) in front, middle pieces behind them. Middle pieces
        // stay clear of the rounded corners (start >= 4, end <= w - 4).
        auto row = [&](const bn::sprite_item& end_item, const bn::sprite_item& mid_item, int ry, int z)
        {
            add(_sprites, place(end_item, x, ry, 0, false, z));
            add(_sprites, place(end_item, x + w - 64, ry, 0, true, z));

            if(w > 128)
            {
                int count = ((w - 128) + 63) / 64;

                for(int index = 0; index < count; ++index)
                {
                    int sx = 64 + (index * 64);

                    if(sx > w - 68)
                    {
                        sx = w - 68;
                    }

                    add(_sprites, place(mid_item, x + sx, ry, 0, false, z + 1));
                }
            }
        };

        row(top_e, top_m, y, 20);
        row(bn::sprite_items::ui_pan_be, bn::sprite_items::ui_pan_bm, y + h - 32, 20);

        if(h > 64)
        {
            // body pieces are 32 high (the interior is vertically uniform): two per 64 px keeps the sprite VRAM low
            int count = ((h - 64) + 31) / 32;

            for(int index = 0; index < count; ++index)
            {
                int sy = 32 + (index * 32);

                if(sy > h - 36)
                {
                    sy = h - 36;
                }

                row(bn::sprite_items::ui_pan_de, bn::sprite_items::ui_pan_dm, y + sy, 23);
            }
        }
    }

    // ---------------------------------------------------------------------------------------------------------

    void bar::set(int x, int y, int w)
    {
        if(w == _width && ! _sprites.empty())
        {
            int dx = x - _x;
            int dy = y - _y;

            if(dx || dy)
            {
                for(bn::sprite_ptr& sprite : _sprites)
                {
                    sprite.set_position(sprite.x() + dx, sprite.y() + dy);
                }
            }

            _x = x;
            _y = y;
            return;
        }

        _sprites.clear();
        _width = w;
        _x = x;
        _y = y;
        int top = y - 9;        // the bar is drawn on rows 9..21 of its 32-row pieces
        add(_sprites, place(bn::sprite_items::ui_bar_l, x, top, 0, false, 10));
        add(_sprites, place(bn::sprite_items::ui_bar_r, x + w - 16, top, 0, false, 10));
        int count = ((w - 32) + 63) / 64;

        for(int index = 0; index < count; ++index)
        {
            int sx = 16 + (index * 64);

            if(sx > w - 67)
            {
                sx = w - 67;
            }

            add(_sprites, place(bn::sprite_items::ui_bar_m, x + sx, top, 0, false, 11));
        }
    }

    // ---------------------------------------------------------------------------------------------------------

    void add_piece(bn::ivector<bn::sprite_ptr>& list, const bn::sprite_item& item, int x, int y, int frame, bool hflip, int z_order)
    {
        add(list, place(item, x, y, frame, hflip, z_order));
    }

    bn::optional<bn::sprite_ptr> make_button(int frame, int x, int y)
    {
        // The icon circle sits at (3, 3) of its 16 x 16 frame.
        bn::optional<bn::sprite_ptr> sprite = bn::sprite_items::ui_icons.create_sprite_optional(x - 3 + 8 - 120, y - 3 + 8 - 80, frame);

        if(sprite)
        {
            sprite->set_bg_priority(0);
            sprite->set_z_order(0);
        }

        return sprite;
    }

    void hint_row::open(int x, int y, bool with_back, const char* ok_text)
    {
        close();
        _a = make_button(0, x, y);
        const char* ok = ok_text ? ok_text : (with_back ? "Choose" : "OK");
        _ok.set(font9, x + 12, y + 8, ok, role::hint);

        if(with_back)
        {
            int bx = x + 12 + text_width(font9, ok) + 9;
            _b = make_button(1, bx, y);
            _back.set(font9, bx + 12, y + 8, "Back", role::hint);
        }
    }

    void hint_row::close()
    {
        _a.reset();
        _b.reset();
        _ok.clear();
        _back.clear();
    }

    bn::optional<bn::sprite_ptr> make_cue(int x, int y)
    {
        bn::optional<bn::sprite_ptr> sprite = bn::sprite_items::ui_icons.create_sprite_optional(0, 0, 2);

        if(sprite)
        {
            sprite->set_bg_priority(0);
            sprite->set_z_order(0);
            place_cue(*sprite, x, y);
        }

        return sprite;
    }

    void place_cue(bn::sprite_ptr& cue, int tip_x, int tip_y)
    {
        // the bubble's tail tip is at (7, 15) of the 16 x 16 frame
        cue.set_position(tip_x - 7 + 8 - 120, tip_y - 15 + 8 - 80);
    }
}
