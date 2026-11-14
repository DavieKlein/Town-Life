#ifndef TL_PALETTE_H
#define TL_PALETTE_H

#include "bn_sprite_palettes.h"

// s83: the GBA has 16 sprite palettes (16 colours each) for everything. Budget (see CLAUDE.md "Sprite palette budget"): ~7 are always used (player, shadow,
// HUD bars, ui icons, UI style palette, ...), the rest is shared by NPCs (1 each), critters (1 per kind), pickups, collectibles, map sprites, light pools, portraits
// and the player's activity sheets. Every optional sprite checks `palettes_free(n)` first and is simply skipped when the room is short:
// reserves = palettes that must stay free AFTER the new one (NPC 4, critter 3, pickups / collectibles 2, map sprites / light pools 1).
namespace tl
{
    [[nodiscard]] inline int palettes_free()
    {
        return bn::sprite_palettes::available_colors_count() / 16;
    }

    [[nodiscard]] inline bool palette_room(int reserve)
    {
        return palettes_free() > reserve;
    }
}

#endif
