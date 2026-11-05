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
#include "tl_story.h"
#include "tl_dialogue.h"
#include "tl_minigame.h"
#include "tl_cutscene.h"

namespace tl
{
    // The "overworld" scene: streamed map layers, the player, the camera, map transitions and the HUD.
    class field
    {

    public:
        field(map_id start_map, int start_x, int start_y, direction facing);

        // Continue: starts from a saved game.
        explicit field(const save_data& save);

        // Overrides the objective line of the pause menu (normally the current mission's objective, see tl_story.h).
        void set_objective(const bn::string_view& text)
        {
            _objective = text;
            _objective_override = true;
        }

        void update();

        // ---- hand-off to main.cpp: minigames run outside the field (it is destroyed first and rebuilt from this snapshot)
        void snapshot(save_data& out) const
        {
            _fill_save(out);
        }

        // True when a minigame should start now (not while a message or menu is still open).
        [[nodiscard]] bool minigame_pending() const
        {
            return _minigame_pending && ! _conversation.active() && ! _menu.is_open();
        }

        [[nodiscard]] const minigame_request& minigame() const
        {
            return _minigame_req;
        }

        // New game: the screen stays black until the first cutscene fades in.
        void begin_black();

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
        ui::label _day_label;           // weekday above the clock
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
        map_id _map_id = map_id::city_centre;
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
        bn::string<24> _talk_label;
        int _shop_npc = -1;

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
            log,
            confirm_save,
            saved,
            confirm_quit,
            sleep_save      // "Slept well. Save game?" after a night in the bed
        };

        // Sleeping in the player's bed (see tl_field.cpp): a night's sleep or a one-hour nap.
        enum class sleep_kind
        {
            none,
            bench,
            night,
            nap
        };

        sleep_kind _sleep = sleep_kind::none;
        int _sleep_minutes = 0;
        bool _save_after_sleep = false;

        pause_screen _pause;
        log_screen _log;
        dialog _dialog;
        pause_mode _pause_mode = pause_mode::none;
        bn::string<48> _objective = "Explore the city";
        bool _objective_override = false;

        // Conversations with the cast and story events (tl_dialogue.h, tl_story.h).
        conversation _conversation;
        bn::string<200> _story_text;
        bool _story_check_due = true;
        bool _hud_hidden = false;

        // ---- cutscenes (tl_field_script.cpp)
        struct script_state
        {
            enum class wait_kind
            {
                none,
                frames,
                fade,
                moves,
                card,
                load,
                action,
                dialogue,
                hook
            };

            bool active = false;
            int id = -1;
            int pc = 0;
            int end = 0;
            wait_kind wait = wait_kind::none;
            int counter = 0;
            int fade_slow = 1;
            int fade_tick = 0;
            int hook_stage = 0;
            int flash = 0;
            bool walking = false;
            int walk_x = 0;
            int walk_y = 0;
            int walk_frames = 0;
            bool walk_run = false;
            map_id warp_map = map_id::city_centre;
            int warp_x = 0;
            int warp_y = 0;
            direction warp_facing = direction::down;
        };

        script_state _script;
        bool _minigame_pending = false;
        minigame_request _minigame_req;
        int _focus_x = 0;               // camera focus (image pixels); follows the player unless a script pans
        int _focus_y = 0;
        int _pan_mode = 0;              // 0 follow, 1 looking at (_pan_x, _pan_y), 2 returning to the player
        int _pan_x = 0;
        int _pan_y = 0;
        int _fade_target = 0;
        int _letter = 0;                // letterbox bars (pixels)
        int _letter_target = 0;
        ui::label _card_label[1];
        int _gate_cooldown = 0;
        warp _redirect_warp = {};

        // Victor Vault's golden car (cutscene actor, see tl_car_data.h): 32x32 sprite pieces + blended shadow blobs
        bn::vector<bn::sprite_ptr, 12> _car;
        bn::vector<bn::sprite_ptr, 6> _car_shadow;
        bool _car_on = false;
        int _car_heading = 7;                   // 7 = se (+x), 3 = nw (-x)
        bn::fixed _car_x;
        bn::fixed _car_y;
        int _car_from_x = 0;
        int _car_from_y = 0;
        int _car_to_x = 0;
        int _car_to_y = 0;
        int _car_frames = 0;
        int _car_done = 0;
        int _car_mode = 0;
        bool _shop_has_shift = false;
        int _shop_items = 4;
        int _hint_cooldown = 0;

        [[nodiscard]] bool _cond_ok(const cs_cond& cond) const;
        void _check_triggers();
        void _start_script(int id);
        void _end_script();
        void _update_script();
        [[nodiscard]] bool _run_step(const cs_step& step);
        void _script_arrived_check();
        void _script_dialogue_done();
        void _set_letterbox(int target);
        void _update_letterbox();
        void _update_focus();
        void _map_story_state();
        void _car_build(int x, int y, int heading);
        void _car_update();
        void _car_tick();
        void _car_clear();
        void _sync_objective_dynamic();
        void _note_evening(bool ate, bool washed);
        void _check_need_hints();
        void _try_start_shift();
        [[nodiscard]] const interactable* _find_kind(interactable_kind kind) const;
        [[nodiscard]] int _npc_index(npc_id who) const;

        [[nodiscard]] bool _can_pause() const;
        void _open_pause();
        void _close_pause();
        void _update_pause();
        void _save_game();
        void _fill_save(save_data& out) const;
        void _apply_save(const save_data& in);
        void _open_dialog(int which);
        void _open_log();

        // Conversations
        [[nodiscard]] int _find_npc(int& d2) const;
        void _start_conversation(int npc_index);
        void _end_conversation();
        void _set_hud_hidden(bool hidden);
        void _handle_story_events(int talked_npc);
        void _sync_objective();

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
        void _finish_sleep();
        void _show_notes();
        void _show_window();
        void _update_lighting(bool force);
        void _update_lamps();
        static void _set_fade(int counter);
    };

    // Applies a finished minigame to the snapshot the field is rebuilt from: money, needs, the clock, story flags (tl_field_script.cpp).
    void apply_minigame_result(save_data& snapshot, const minigame_request& request, const minigame_result& result);

    // A system message the finished minigame wants shown (e.g. "Shift done! Wage $17..."), or nullptr; cleared by taking it.
    const char* take_pending_message();
}

#endif
