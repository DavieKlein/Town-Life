/*
 * Town Life - a small top-down town life game for the Game Boy Advance.
 * Built with Butano (https://github.com/GValiente/butano).
 */

#include "bn_core.h"
#include "bn_camera_ptr.h"
#include "bn_regular_bg_ptr.h"

#include "bn_regular_bg_items_town.h"

#include "tl_player.h"
#include "tl_town_map.h"

namespace
{
    constexpr int screen_half_width = 120;
    constexpr int screen_half_height = 80;

    [[nodiscard]] constexpr int clamp(int value, int min_value, int max_value)
    {
        return value < min_value ? min_value : (value > max_value ? max_value : value);
    }

    // Keeps the camera inside the town so no empty space is shown at the edges.
    void update_camera(bn::camera_ptr& camera, const tl::player& player)
    {
        constexpr int half_w = tl::town_map::pixel_width / 2;
        constexpr int half_h = tl::town_map::pixel_height / 2;
        constexpr int max_x = half_w - screen_half_width;
        constexpr int max_y = half_h - screen_half_height;

        int x = clamp(player.map_x() - half_w, -max_x, max_x);
        int y = clamp(player.map_y() - half_h, -max_y, max_y);
        camera.set_position(x, y);
    }
}

int main()
{
    bn::core::init();

    bn::camera_ptr camera = bn::camera_ptr::create(0, 0);

    bn::regular_bg_ptr town_bg = bn::regular_bg_items::town.create_bg(0, 0);
    town_bg.set_camera(camera);

    // Start on the sidewalk just above the central park.
    tl::player player(16 * 16 + 8, 12 * 16 + 4, camera);
    update_camera(camera, player);

    while(true)
    {
        player.update();
        update_camera(camera, player);
        bn::core::update();
    }
}
