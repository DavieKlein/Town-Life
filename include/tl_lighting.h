#ifndef TL_LIGHTING_H
#define TL_LIGHTING_H

#include "bn_color.h"

#include "tl_world.h"

namespace tl
{
    // Day/night lighting by palette transforms (approved design): every colour is desaturated,
    // multiplied and offset depending on the time of day. Special palette entries of the map layers
    // (see layer_data) are handled on top: water ripples are cycled, window glass and lamp glass light
    // up at night.
    struct light_params
    {
        int mul_r = 256;    // 1/256 units
        int mul_g = 256;
        int mul_b = 256;
        int add_r = 0;      // 5-bit colour units
        int add_g = 0;
        int add_b = 0;
        int sat = 256;      // 1/256 units
        int night = 0;      // 0 = day, 256 = full night (lamps and windows on from 128)
    };

    [[nodiscard]] light_params lighting_at(int minutes, bool outdoor);

    // The cold grey-blue look of VaultTech places (HOOK VAULTMART_SWAP: used for the Corner Market interior after the firing).
    [[nodiscard]] light_params cold_lighting();

    // True when the lamps are on (outdoor night from about 19:40 to 6:15); the UI switches to its Night style then.
    [[nodiscard]] bool is_night(int minutes);

    [[nodiscard]] bn::color light_colour(bn::color colour, const light_params& params);

    void light_colours(const bn::color* source, bn::color* destination, int count, const light_params& params);

    // Lights a whole map layer palette (layer.banks * 16 colours) including its special entries.
    // water_phase advances the ripple palette cycling.
    void light_layer(const layer_data& layer, bn::color* destination, const light_params& params, int water_phase);
}

#endif
