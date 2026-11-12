#include "tl_field.h"

#include "bn_string_view.h"
#include "bn_sprite_items_player_climb.h"

#include "tl_story.h"
#include "tl_story_ids.h"

// s77: the secret route through the sewer. Road manholes in the City Centre (east end of the avenue) and in Old Block (Cobble Street)
// lead down to the sewer map; its two shaft ladders lead back up. Open once the flag sneak_route is set (see _update_gates).
namespace tl
{
    namespace
    {
        constexpr bn::string_view manhole_options[] = { "Climb down" };
        constexpr bn::string_view ladder_options[] = { "Climb up" };

        constexpr int fade_frames = 12;         // same as the field's fade
        constexpr int climb_total = 52;         // frames of a ladder climb
        constexpr int climb_rise = 84;          // pixels the climber rises (he leaves the screen at the top)
        constexpr int ground_blend = 10;        // frames in which he moves between the floor spot and the ladder
        constexpr int ladder_y = -18;           // the ladder stands against the back wall of the shaft (world units, y < 0)
        constexpr int landing_y = 15;           // where the player stands after climbing down

        constexpr int city_exit_x = 1062;       // City Centre manhole (66.4, 27.6): the player comes out just south of it
        constexpr int city_exit_y = 462;
        constexpr int ob_exit_x = 310;          // Old Block manhole (19.4, 22.6)
        constexpr int ob_exit_y = 386;
    }

    bool field::_route_open() const
    {
        return story().flag(story_flag::sneak_route) != 0;
    }

    void field::_use_sewer(const interactable& target)
    {
        if(target.kind == interactable_kind::manhole)
        {
            if(! _route_open())
            {
                _menu_mode = menu_mode::none;
                _menu_target = nullptr;
                _show_info("Manhole", "The cover is stuck.", "Someone chalked an", "arrow beside it.");
            }
            else
            {
                _menu.open("Manhole", manhole_options, 1);
            }
        }
        else
        {
            _menu.open("Ladder", ladder_options, 1);
        }
    }

    void field::_sewer_choice(const interactable& target, int choice)
    {
        if(choice != 0)
        {
            return;
        }

        if(target.kind == interactable_kind::manhole)
        {
            // crouch at the cover (the pick-up animation), then the fade and the climb down
            _climb_manhole = &target;
            _begin_activity(60);
            _act.climb_dest = 1;
            _player.approach(target.x, target.y, 12);
            _player.start_action(player::action_kind::pickup, target.x, target.y, _act.frames);
        }
        else
        {
            _begin_climb_up(target);
        }
    }

    void field::_begin_descent(const interactable&)
    {
        // down from the City Centre = the west ladder, down from Old Block = the east ladder
        int ladder_x = _map_id == map_id::old_block ? 438 : 38;
        _climb_warp = warp();
        _climb_warp.target = map_id::sewer;
        _climb_warp.target_x = ladder_x;
        _climb_warp.target_y = landing_y;
        _climb_warp.facing = direction::down;
        _climb_arrive = 1;
        _climb_manhole = nullptr;
        _act.climb_dest = 0;
        _climb_go = true;       // field::update turns this into the warp (it recomputes _pending_warp every frame)
    }

    void field::_begin_climb_up(const interactable& ladder)
    {
        bool west = ladder.quality == 0;
        _climb_warp = warp();
        _climb_warp.target = west ? map_id::city_centre : map_id::old_block;
        _climb_warp.target_x = west ? city_exit_x : ob_exit_x;
        _climb_warp.target_y = west ? city_exit_y : ob_exit_y;
        _climb_warp.facing = direction::up;
        _climb_arrive = 2;
        _climb_up = true;
        _climb_t = 0;
        _climb_from_x = _player.x();
        _climb_from_y = _player.y();
        _climb_ladder_x = ladder.x;
        _climb_ladder_y = ladder_y;
        _cue.reset();
        _player.set_visible(false);
        _climb_sprite = bn::sprite_items::player_climb.create_sprite(0, 0, 0);
        _climb_sprite->set_bg_priority(2);
        _climb_sprite->set_visible(false);
        _state = state::climbing;
    }

    void field::_begin_climb_down()
    {
        _climb_up = false;
        _climb_t = 0;
        _climb_from_x = _player.x();
        _climb_from_y = _player.y();
        _climb_ladder_x = _climb_from_x;
        _climb_ladder_y = ladder_y;
        _cue.reset();
        _player.set_visible(false);
        _climb_sprite = bn::sprite_items::player_climb.create_sprite(0, 0, 0);
        _climb_sprite->set_bg_priority(2);
        _climb_sprite->set_visible(false);
        _fade_counter = fade_frames;
        _set_fade(fade_frames);
        _state = state::climbing;
    }

    void field::_update_climb()
    {
        ++_climb_t;
        int t = _climb_t;
        int p = _climb_up ? t : climb_total - t;            // 0 = at the foot of the ladder, climb_total = at the top
        p = p < 0 ? 0 : p;
        int h = climb_rise * p / climb_total;
        int blend = p >= ground_blend ? ground_blend : p;   // near the floor he moves between the landing spot and the ladder
        int wx = _climb_from_x + (_climb_ladder_x - _climb_from_x) * blend / ground_blend;
        int wy = _climb_from_y + (_climb_ladder_y - _climb_from_y) * blend / ground_blend;
        int sx = _map->to_image_x(wx, wy) - _cam_x;
        int sy = _map->to_image_y(wx, wy) - _cam_y;

        if(_climb_sprite)
        {
            _climb_sprite->set_tiles(bn::sprite_items::player_climb.tiles_item(), (t / 6) & 3);
            _climb_sprite->set_position(sx - 120, sy - 80 - 26 - h);
            _climb_sprite->set_visible(sy - h > -20);
        }

        if(_climb_up)
        {
            if(t > climb_total - fade_frames)
            {
                _set_fade(t - (climb_total - fade_frames));
            }

            if(t >= climb_total)
            {
                _climb_sprite.reset();
                _pending_warp = &_climb_warp;
                _state = state::fading_out;
                _fade_counter = fade_frames - 1;
            }
        }
        else
        {
            _set_fade(t < fade_frames ? fade_frames - t : 0);

            if(t >= climb_total)
            {
                _end_climb();
            }
        }
    }

    void field::_end_climb()
    {
        _climb_sprite.reset();
        _player.set_visible(true);
        _fade_counter = 0;
        _set_fade(0);
        _state = state::playing;
    }
}
