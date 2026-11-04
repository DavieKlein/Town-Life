#ifndef TL_FIELD_H
#define TL_FIELD_H

#include "bn_vector.h"
#include "bn_random.h"
#include "bn_string.h"
#include "bn_optional.h"
#include "bn_sprite_ptr.h"
#include "bn_regular_bg_ptr.h"

#include "tl_ui.h"
#include "tl_menu.h"
#include "tl_save.h"
#include "tl_pause.h"
#include "tl_needs.h"
#include "tl_player.h"
#include "tl_critters.h"
#include "tl_npcs.h"
#include "tl_streamed_bg.h"
#include "tl_lighting.h"
#include "tl_deposit.h"

namespace tl
{
    // The "overworld" scene: streamed map layers, the player, the camera, map transitions and the HUD.
    class field
    {

    public:
        field(map_id start_map, int start_x, int start_y, direction facing);

        // Continue: starts from a saved game.
        explicit field(const save_data& save);

        // Text shown as the objective in the pause menu (a future mission system sets it).
        void set_objective(const bn::string_view& text)
        {
            _objective = text;
        }

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
        ui::label _clock_label;
        ui::label _clock_small_label;      // "am" / "pm"
        ui::label _money_label;
        ui::label _version_label;
        ui::label _zzz_label;
        bn::optional<bn::sprite_ptr> _cue;  // the bobbing "A" over the nearest object in reach
        int _cue_frame = 0;
        player _player;
        critters _critters;
        npcs _npcs;
        deposit _deposit;
        menu _menu;
        needs _needs;
        bn::vector<bn::sprite_ptr, needs::count> _bar_sprites;
        int _bar_levels[needs::count] = { -1, -1, -1, -1, -1 };
        bn::vector<bn::sprite_ptr, 6> _pool_sprites;
        int _version_frames = 300;     // the build date is shown for 5 seconds at start
        light_params _light;
        int _light_minutes = -1;
        int _water_phase = 0;
        bool _lamps_on = false;
        enum class menu_mode
        {
            none,
            interact,       // the object's own menu (bench, fountain, toilet, ...)
            shop,           // buying food
            info            // a message; reopens the shop afterwards if shop_return is set
        };

        menu_mode _menu_mode = menu_mode::none;
        const interactable* _shop_return = nullptr;
        const interactable* _menu_target = nullptr;
        const interactable* _rest_target = nullptr;
        const map_info* _map = nullptr;
        const warp* _pending_warp = nullptr;
        state _state = state::fading_in;
        int _fade_counter = 0;
        int _cam_x = 0;
        int _cam_y = 0;
        int _minutes = 8 * 60;          // time of day in minutes (prototype clock)
        int _day = 1;                   // day counter, +1 at midnight
        int _minute_frames = 0;
        int _money = 20;
        int _total_minutes = 0;         // game minutes since the start (bin cooldowns)
        bn::random _rng;
        bool _accident_pending = false;
        int _bin_emptied[maps_count * 16] = {};      // _total_minutes + 1 when a bin was last searched, 0 = never
        bn::string<24> _info_line_a;
        bn::string<24> _info_line_b;
        bn::string<24> _info_line_c;
        bn::string<24> _deposit_label;

        // The running timed activity: need gains are spread over its frames, bars fill gradually.
        struct activity_state
        {
            bool active = false;
            int frames = 0;
            int done = 0;
            bn::fixed gain[needs::count];       // total change per need
            bn::fixed applied[needs::count];    // part of it already applied
            int extra_minutes = 0;              // additional game minutes that pass during it (reading)
            int extra_done = 0;
            int money = 0;                      // found at the end (bins)
            bool message = false;               // show _info_line_a / _info_line_b at the end
            const char* title = "Trash bin";      // title of that message
            int pickup = -1;                    // deposit pickup spot collected at the end
        };

        activity_state _act;

        // Pause menu (START) and saving, see tl_field_pause.cpp.
        enum class pause_mode
        {
            none,
            main,
            confirm_save,
            saved,
            confirm_quit
        };

        pause_screen _pause;
        dialog _dialog;
        pause_mode _pause_mode = pause_mode::none;
        bn::string<48> _objective = "Explore the city";

        [[nodiscard]] bool _can_pause() const;
        void _open_pause();
        void _close_pause();
        void _update_pause();
        void _save_game();
        void _fill_save(save_data& out) const;
        void _apply_save(const save_data& in);
        void _open_dialog(int which);

        void _load_map(map_id id, int x, int y, direction facing);
        void _update_camera();
        void _update_clock();
        void _redraw_hud_text();
        void _update_bars();
        [[nodiscard]] const interactable* _find_target() const;
        [[nodiscard]] int _find_pickup(int& d2) const;
        void _update_cue();
        void _open_interaction_menu();
        void _handle_menu_choice(int choice);
        void _open_shop(const interactable& target);
        void _buy(const interactable& target, int choice);
        void _begin_activity(int frames);
        void _update_activity();
        void _tick_minute();
        void _use_toilet(const interactable& target);
        void _search_bin(const interactable& target);
        void _pick_up(int spot);
        void _open_deposit_menu();
        void _deposit_choice(int choice);
        void _topup_pickups();
        void _handle_accident();
        void _show_info(const char* title, const char* line_a, const char* line_b, const char* line_c);
        void _update_zzz();
        void _update_lighting(bool force);
        void _update_lamps();
        static void _set_fade(int counter);
    };
}

#endif
