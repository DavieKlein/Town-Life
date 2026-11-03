/*
 * Town Life - a story-driven top-down life-sim for the Game Boy Advance.
 * Built with Butano (https://github.com/GValiente/butano).
 */

#include "bn_core.h"

#include "tl_field.h"

int main()
{
    bn::core::init();

    // Start on the sidewalk in front of Corner Market.
    tl::field field(tl::map_id::city_centre, 14 * tl::metatile_size + 8, 13 * tl::metatile_size + 6,
                    tl::direction::down);

    while(true)
    {
        field.update();
        bn::core::update();
    }
}
