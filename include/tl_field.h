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
#include "tl_map_sprites.h"
#include "tl_collect.h"
#include "tl_phone.h"
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

        // ---- black box / bug reporter (tl_blackbox.h)
        // Free-walking state with nothing open: a snapshot taken now restores faithfully.
        [[nodiscard]] bool blackbox_calm() const
        {
            return _state == state::playing && _pause_mode == pause_mode::none && ! _menu.is_open() && ! _conversation.active() &&
                   ! _script.active && ! _act.active && ! _phone_open && ! _minigame_pending && ! _accident_pending;
        }

        // The report panel needs a lot of sprites: close the pause screen / an open interaction menu first (the player reopens them).
        void blackbox_make_room()
        {
            if(_pause_mode != pause_mode::none)
            {
                _close_pause();
            }
            else if(_menu.is_open())
            {
                _menu.close();
            }

            _npcs.focus_none();             // s81: everything optional goes (the caller runs bn::core::update() afterwards)
            _make_room(true, false);
        }

        // Cheap live values for the black box (map index, feet position, day, minutes, money, 1 = free play state).
        void blackbox_live(uint32_t out[7]) const
        {
            out[0] = uint32_t(_map - &get_map(map_id(0)));
            out[1] = uint32_t(_player.x());
            out[2] = uint32_t(_player.y());
            out[3] = uint32_t(_day);
            out[4] = uint32_t(_minutes);
            out[5] = uint32_t(_money);
            out[6] = _state == state::playing ? 1 : 0;
        }

        void rng_state(uint32_t out[3]) const
        {
            static_assert(sizeof(bn::random) == 12, "bn::random layout");
            __builtin_memcpy(static_cast<void*>(out), static_cast<const void*>(&_rng), 12);
        }

        void set_rng_state(const uint32_t in[3])
        {
            __builtin_memcpy(static_cast<void*>(&_rng), static_cast<const void*>(in), 12);
        }

        // Replay mode: skip the fade-in after Continue so the first frame is already playable.
        void skip_fade_in()
        {
            if(_state == state::fading_in)
            {
                _fade_counter = 0;
                _set_fade(0);
                _state = state::playing;
            }
        }

    private:
        enum class state
        {
            fading_in,
            playing,
            fading_out,
            loading,
            climbing        // s77: ladder climb in the sewer (up: before the fade out, down: after the fade in)
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
        int _cue_faced = -1;                // what the player was last turned towards while standing still (see _update_cue)
        player _player;
        critters _critters;
        npcs _npcs;
        deposit _deposit;
        map_sprites _map_sprites;
        collectibles _collect;
        menu _menu;
        needs _needs;
        bn::vector<bn::sprite_ptr, needs::count + 1> _bar_sprites;
        bn::vector<bn::sprite_ptr, needs::count + 1> _pm_sprites;   // HUD +/- markers (s72)
        int _bar_levels[needs::count + 1] = { -1, -1, -1, -1, -1, -1 };
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
            gifts,          // gift list of a shop
            kiosk,          // scratch cards / newspaper at the newspaper boxes
            clinic,         // City Clinic reception (s64)
            shower,         // $1 shower in the public toilet (s64)
            board,          // the community centre notice board: odd jobs (s71)
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
        bn::fixed _lead_x;              // smooth camera lead in the walking direction (screen pixels)
        bn::fixed _lead_y;
        int _minutes = 8 * 60;          // time of day in minutes (prototype clock)
        int _day = 1;                   // day counter, +1 at midnight
        int _minute_frames = 0;
        int _money = 20;
        int _audio_money = 0;
        bool _audio_money_valid = false;
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
            int collectible = -1;               // collectible item found at the end (s64)
            int odd_bit = 0;                    // odd job done flag set when the activity finishes (s71)
            int climb_dest = 0;                 // s77: 1 = crouch at a manhole, then climb down into the sewer (see _begin_descent)
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
            sleep_save,     // "Slept well. Save game?" after a night in the bed
            collection      // the collection screen (s64)
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
        collection_screen _collection;
        dialog _dialog;
        pause_mode _pause_mode = pause_mode::none;
        bn::string<48> _objective = "Explore the city";
        bool _objective_override = false;

        // Conversations with the cast and story events (tl_dialogue.h, tl_story.h).
        conversation _conversation;
        bn::string<200> _story_text;
        bool _story_check_due = true;
        bool _hud_hidden = false;
        bool _optional_freed = false;

        // ---- s64: sickness, fainting, the clinic bill, the phone (tl_field_health.cpp)
        phone _phone;
        bool _phone_open = false;
        int _zero_min[4] = {};              // game minutes Hunger / Energy / Hygiene / Social have been empty
        int _red_min = 0;                   // game minutes two or more needs were red
        int _sick_rest = 0;                 // minutes slept while sick
        int _cough_min = 0;
        bool _sick = false;
        bool _faint_pending = false;
        bool _sick_msg_pending = false;
        int _debt = 0;
        int _debt_day = 0;
        int _faints = 0;
        uint16_t _msg_seen = 0;
        uint16_t _msg_read = 0;
        uint8_t _call_day[8] = {};
        int _delivery_item = -1;
        int _delivery_due = 0;
        int _mail_blink = 0;
        bn::optional<bn::sprite_ptr> _mail_icon;
        bn::optional<bn::sprite_ptr> _sick_icon;
        int _faint_paid = 0;
        void _update_health_minute();
        void _cure_sickness();
        void _open_phone();
        void _update_audio_sfx();           // s78: activity sounds (tl_field_audio.cpp)
        void _update_phone();
        void _update_hud_icons();
        void _update_pm();
        void _try_delivery();
        void _check_bill_reminder();
        void _clinic_care(int kind);
        void _open_clinic_menu(const interactable& target);
        void _clinic_choice(int choice);
        void _use_shower(const interactable& target);
        void _pick_collectible(int index);
        void _collectible_found(int index);

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
        int _win_top = 0;               // applied window bars (s81)
        int _win_bottom = 0;
        ui::label _card_label[1];
        int _gate_cooldown = 0;
        warp _redirect_warp = {};

        // s77 sewer route (tl_field_sewer.cpp)
        warp _climb_warp = {};
        int _climb_arrive = 0;          // 1 = after the next map load play the climb down, 2 = arrive at a manhole (Hygiene -3)
        int _climb_t = 0;
        bool _climb_go = false;
        bool _climb_up = false;
        int _climb_from_x = 0;          // player position when the climb starts / lands (world units)
        int _climb_from_y = 0;
        int _climb_ladder_x = 0;        // the ladder's foot (world units)
        int _climb_ladder_y = 0;
        bn::optional<bn::sprite_ptr> _climb_sprite;
        const interactable* _climb_manhole = nullptr;

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
        int _shop_talk_index = -1;          // option index of "Talk to ..." in the shop menu
        int _shop_gift_index = -1;          // option index of "Gifts"
        int _gift_ids[4] = {};              // gifts offered by the open gift list
        int _gift_offer = 0;
        bn::string<24> _gift_labels[5];
        void _open_gift_shop(const interactable& target);
        void _buy_gift(const interactable& target, int choice);
        void _open_kiosk(const interactable& target);
        void _kiosk_choice(const interactable& target, int choice);
        void _scratch_card(const interactable& target);
        int _hint_cooldown = 0;

        // ---- s71: odd jobs, "Feeling great", toast (tl_field_jobs.cpp)
        uint8_t _odd_day = 0;               // day (mod 256) _odd_mask belongs to (saved in save_data::spare[0..1])
        uint8_t _odd_mask = 0;              // done / taken bits of the three odd jobs + flyer spots visited
        bool _great = false;
        ui::label _toast_label;
        bn::string<32> _toast_text;
        int _toast_frames = 0;
        bool _toast_wait = false;
        [[nodiscard]] int _job_pay(int base) const;
        void _odd_refresh();
        void _toast(const char* text);
        void _toast_clear();
        void _update_toast();
        void _update_great(bool announce);
        void _open_board(const interactable& target);
        void _board_choice(int choice);
        void _update_flyers();
        void _start_crates();
        bool _odd_objective();
        [[nodiscard]] bool _crates_open() const;

        [[nodiscard]] bool _cond_ok(const cs_cond& cond) const;
        void _check_triggers();
        void _early_pan();
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
        void _make_room(bool scenery, bool wait = true);       // s81: free every optional sprite (critters, pickups, collectibles, light pools, map sprites) before a big UI opens
        void _sync_optional();               // s81: brings them back when no big UI is open
        void _begin_message(const char* text);      // s81: system message page; NPC sprites are dropped meanwhile (VRAM)
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
        [[nodiscard]] bool _shop_open(map_id target) const;
        void _show_closed(map_id target);
        void _update_zzz();
        void _finish_sleep();
        void _show_notes();
        void _show_window();
        void _use_old_block(const interactable& target);      // tl_field_oldblock.cpp
        void _update_gates();
        void _use_sewer(const interactable& target);                  // tl_field_sewer.cpp: manhole / ladder menus
        void _sewer_choice(const interactable& target, int choice);
        void _begin_descent(const interactable& manhole);             // after the crouch at a manhole: fade, then climb down
        void _begin_climb_up(const interactable& ladder);
        void _begin_climb_down();
        void _update_climb();
        void _end_climb();
        [[nodiscard]] bool _route_open() const;
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
