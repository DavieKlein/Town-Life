#ifndef TL_FIELD_H
#define TL_FIELD_H

#include "bn_vector.h"
#include "bn_optional.h"
#include "bn_sprite_ptr.h"
#include "bn_regular_bg_ptr.h"
#include "bn_sprite_text_generator.h"

#include "tl_menu.h"
#include "tl_needs.h"
#include "tl_player.h"
#include "tl_critters.h"
#include "tl_streamed_bg.h"
#include "tl_lighting.h"

namespace tl
{
    // The "overworld" scene: streamed map layers, the player, the camera, map transitions and the HUD.
    class field
    {

    public:
        field(map_id start_map, int start_x, int start_y, direction facing);

        void update();

    private:
        enum class state
        {
            fading_in,
            playing,
            fading_out,
            loading
        };

        bn::optional<streamed_bg> _floor_bg;
        bn::optional<streamed_bg> _objects_bg;
        bn::optional<bn::regular_bg_ptr> _hud_bg;
        bn::sprite_text_generator _text_generator;
        bn::vector<bn::sprite_ptr, 8> _clock_sprites;
        bn::vector<bn::sprite_ptr, 8> _money_sprites;
        player _player;
        critters _critters;
        menu _menu;
        needs _needs;
        bn::vector<bn::sprite_ptr, needs::count> _bar_sprites;
        bn::vector<bn::sprite_ptr, 4> _zzz_sprites;
        bn::vector<bn::sprite_ptr, 6> _pool_sprites;
        light_params _light;
        int _light_minutes = -1;
        int _water_phase = 0;
        bool _lamps_on = false;
        const interactable* _menu_target = nullptr;
        const interactable* _rest_target = nullptr;
        const map_info* _map = nullptr;
        const warp* _pending_warp = nullptr;
        state _state = state::fading_in;
        int _fade_counter = 0;
        int _cam_x = 0;
        int _cam_y = 0;
        int _minutes = 8 * 60;          // time of day in minutes (prototype clock)
        int _minute_frames = 0;
        int _money = 20;

        void _load_map(map_id id, int x, int y, direction facing);
        void _update_camera();
        void _update_clock();
        void _redraw_hud_text();
        void _update_bars();
        void _open_interaction_menu();
        void _handle_menu_choice(int choice);
        void _update_zzz();
        void _update_lighting(bool force);
        void _update_lamps();
        static void _set_fade(int counter);
    };
}

#endif
