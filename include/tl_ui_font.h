#ifndef TL_UI_FONT_H
#define TL_UI_FONT_H

#include <stdint.h>

namespace tl::ui
{
    // A bitmap font baked by tools/ui_assets.py: 95 glyphs (ASCII 32..126), each a 16 x 16 cell stored as 16 rows of
    // 16 pixels at 2 bits (0 none, 1 fill, 2 outline); ink starts at column 2 of the cell, `baseline` is the row of
    // the text baseline. widths = advance in pixels.
    struct font_data
    {
        const uint32_t* rows;
        const uint8_t* widths;
        int baseline;
    };

    extern const font_data font9;     // DejaVu Sans Bold 9 px: menus, dialogs, pause screen
    extern const font_data font11;    // DejaVu Sans Bold 11 px: HUD clock and money, day counter
}

#endif
