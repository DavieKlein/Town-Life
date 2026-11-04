#ifndef TL_PORTRAIT_H
#define TL_PORTRAIT_H

#include "bn_sprite_item.h"

namespace tl
{
    // Dialogue portraits (tools/portraits, generated table in src/tl_portrait_data.cpp). Each graphic has 5 frames = expressions.
    enum expression : int
    {
        expr_neutral,
        expr_happy,
        expr_angry,
        expr_sad,
        expr_surprised
    };

    struct portrait_set
    {
        const bn::sprite_item* big[4];      // 128 px (layout 1): quarters TL, TR, BL, BR, each 64x64
        const bn::sprite_item* small[4];    // 96 px (layout 2): pieces 64x64, 32x64, 64x32, 32x32
    };

    // speaker = npc_id or speaker_player; nullptr when there is no portrait (e.g. Halloran).
    [[nodiscard]] const portrait_set* portrait_for(int speaker);
}

#endif
