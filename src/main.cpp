/*
 * Town Life - a story-driven isometric life-sim for the Game Boy Advance.
 * Built with Butano (https://github.com/GValiente/butano).
 */

#include "bn_core.h"

#include "tl_field.h"

int main()
{
    bn::core::init();

    // Start on the sidewalk in front of Corner Market.
    tl::field field(tl::map_id::city_centre, 6 * tl::cell_size + 8, 3 * tl::cell_size + 10, tl::direction::down);

    while(true)
    {
        field.update();
        bn::core::update();
    }
}
