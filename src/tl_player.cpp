#include "tl_player.h"

#include "bn_math.h"
#include "bn_keypad.h"
#include "bn_blending.h"
#include "bn_sprite_palette_ptr.h"
#include "bn_sprite_items_player.h"
#include "bn_sprite_items_player_run.h"
#include "bn_sprite_items_shadow.h"
#include "bn_sprite_items_player_rest.h"
#include "bn_sprite_items_player_wash.h"
#include "bn_sprite_items_player_eat.h"
#include "bn_sprite_items_player_drink.h"
#include "bn_sprite_items_player_read.h"
#include "bn_sprite_items_player_search.h"
#include "bn_sprite_items_player_pickup.h"
#include "bn_sprite_items_player_shower.h"

namespace tl
{
    namespace
    {
        constexpr int hitbox_radius = 4;        // world units around the feet

        // player.bmp: 32x64 frames rendered from the 3D character, 18 per facing: 6 idle (breathing loop) and 12 walk
        // frames (tools/actor_cycles.py), 8 facings in clockwise screen order (s, sw, w, nw, n, ne, e, se). Feet at (16, 54).
        // player_run.bmp: 64x64 frames (the long running stride does not fit 32 px), 12 per facing, feet at (32, 54), shown
        // by a separate sprite only while running. Walk and run both start at the passing pose (left foot planted, right
        // foot swinging past it) and stay in the same foot phase, so switching between them keeps the legs in step.
        constexpr int idle_frames = 6;
        constexpr int walk_frames = 12;
        constexpr int run_frames = 12;
        constexpr int walk_base = idle_frames;
        constexpr int frames_per_facing = idle_frames + walk_frames;
        constexpr int idle_hold = 28;               // game frames per idle frame (6 frames = a 2.8 s breathing loop)
        constexpr int turn_hold = 2;                // game frames per in-between facing while turning
        constexpr bn::fixed settle_speed = 0.5;     // walk frames per game frame while the feet come to rest
        constexpr int feet_offset_y = 54 - 32;  // feet relative to the sprite centre

        constexpr bn::fixed walk_speed = 1.25;  // screen pixels per frame
        constexpr bn::fixed run_speed = 2.95;   // s73 phone test: was 2.25, felt too slow
        constexpr bn::fixed acceleration = 0.38; // fraction of the speed difference applied per frame
        constexpr bn::fixed deceleration = 0.45;
        constexpr bn::fixed start_kick = 0.45;   // fraction of the target speed reached in the first frame from standstill

        // Planted feet: one cycle of the Quaternius Walk action moves the body 1.36 m (stance-foot speed x cycle length),
        // one Run cycle 2.8 m (measured in tools; see CLAUDE.md "Smooth motion"). The screen distance of 1 m depends on the
        // facing (iso projection, the d-pad moves equal screen pixels in every direction): 15.08 px/m for s/n, 23.85 px/m
        // for the street diagonals sw/nw/ne/se, 30.16 px/m for w/e. So the screen pixels per animation frame differ per facing.
        // Index = facing (s, sw, w, nw, n, ne, e, se). Multiply every entry to tune sliding vs. cadence.
        constexpr bn::fixed walk_step[8] = { 1.71, 2.71, 3.42, 2.71, 1.71, 2.71, 3.42, 2.71 };   // px per frame, 1.36 m / 12
        constexpr bn::fixed run_step[8] = { 3.52, 5.57, 7.04, 5.57, 3.52, 5.57, 7.04, 5.57 };    // px per animation frame, 2.8 m / 12: a function of the stride, not of the speed, so planted feet stay planted when run_speed changes (cadence scales)

        // player_rest.bmp: 64x64, frames 0-3 sitting (facing down-left), 4 sleeping on the side; the
        // seat point is at (32, 44). player_wash.bmp: 64x64, 8 facings x 4 frames, feet at (32, 54).
        constexpr int rest_origin_y = 44 - 32;
        constexpr int sleep_frame = 4;
        constexpr int bed_frame = 5;               // on the back in the player's bed (head towards -x, on the pillow)
        constexpr int rest_mirror_shift = 6;       // the seated figure is ~3 px right of the frame centre: mirroring moves it

        constexpr int act_frames_per_facing = 4;

        // Frames each animation step lasts, per action_kind.
        constexpr int act_step[7] = { 6, 16, 18, 36, 14, 18, 10 };      // wash, eat, drink, read, search, pickup, shower

        [[nodiscard]] const bn::sprite_item& action_item(player::action_kind kind)
        {
            switch(kind)
            {
            case player::action_kind::eat:
                return bn::sprite_items::player_eat;

            case player::action_kind::drink:
                return bn::sprite_items::player_drink;

            case player::action_kind::read:
                return bn::sprite_items::player_read;

            case player::action_kind::search:
                return bn::sprite_items::player_search;

            case player::action_kind::pickup:
                return bn::sprite_items::player_pickup;

            case player::action_kind::shower:
                return bn::sprite_items::player_shower;

            default:
                return bn::sprite_items::player_wash;
            }
        }

        [[nodiscard]] int facing_towards(int dx, int dy)
        {
            // world delta -> screen direction -> one of the 8 facings (s, sw, w, nw, n, ne, e, se)
            int sx = dx - dy;
            int sy = (dx + dy) / 2;
            int ax = sx < 0 ? -sx : sx;
            int ay = sy < 0 ? -sy : sy;
            int hx = ax * 2 > ay ? (sx > 0 ? 1 : -1) : 0;
            int hy = ay * 2 > ax ? (sy > 0 ? 1 : -1) : 0;
            constexpr int table[3][3] = { { 3, 4, 5 }, { 2, 0, 6 }, { 1, 0, 7 } };   // [hy + 1][hx + 1]
            return table[hy + 1][hx + 1];
        }

        // World velocity for one screen pixel per frame, per facing. Up/down/left/right on the d-pad move
        // straight across the screen; diagonals follow the isometric streets.
        //   screen_dx = vx - vy, screen_dy = (vx + vy) / 2
        struct world_dir
        {
            bn::fixed x;
            bn::fixed y;
        };

        constexpr world_dir directions[8] = {
            { 1, 1 },               // s:  screen down
            { 0, 0.894 },           // sw: +y (iso street)
            { -0.5, 0.5 },          // w:  screen left
            { -0.894, 0 },          // nw: -x (iso street)
            { -1, -1 },             // n:  screen up
            { 0, -0.894 },          // ne: -y (iso street)
            { 0.5, -0.5 },          // e:  screen right
            { 0.894, 0 },           // se: +x (iso street)
        };

        [[nodiscard]] int facing_from_direction(direction facing)
        {
            switch(facing)
            {

            case direction::down:
                return 1;

            case direction::left:
                return 3;

            case direction::up:
                return 5;

            case direction::right:
                return 7;

            default:
                return 0;
            }
        }

        // Returns the facing (0..7) for the pressed d-pad keys, or -1 if no direction is pressed.
        [[nodiscard]] int input_facing()
        {
            int dx = bn::keypad::right_held() ? 1 : (bn::keypad::left_held() ? -1 : 0);
            int dy = bn::keypad::down_held() ? 1 : (bn::keypad::up_held() ? -1 : 0);

            if(dx == 0 && dy == 1)
            {
                return 0;
            }

            if(dx == -1 && dy == 1)
            {
                return 1;
            }

            if(dx == -1 && dy == 0)
            {
                return 2;
            }

            if(dx == -1 && dy == -1)
            {
                return 3;
            }

            if(dx == 0 && dy == -1)
            {
                return 4;
            }

            if(dx == 1 && dy == -1)
            {
                return 5;
            }

            if(dx == 1 && dy == 0)
            {
                return 6;
            }

            if(dx == 1 && dy == 1)
            {
                return 7;
            }

            return -1;
        }
    }

    player::player() :
        _shadow(bn::sprite_items::shadow.create_sprite(0, 0)),
        _sprite(bn::sprite_items::player.create_sprite(0, 0))
    {
        // Soft shadow under the feet: a dark ellipse drawn with 50% alpha blending, behind the player.
        bn::blending::set_transparency_alpha(0.5);
        _shadow.set_blending_enabled(true);
        _shadow.set_z_order(1);
    }

    void player::place(const map_info& map, int x, int y, direction facing)
    {
        _map = &map;
        _x = x;
        _y = y;
        _vx = 0;
        _vy = 0;
        _input_facing = -1;
        _raw_facing = -1;
        _facing = facing_from_direction(facing);
        _reset_anim();
        _update_graphics();
    }

    void player::face_towards(int target_x, int target_y)
    {
        if(_activity == activity::walking && (target_x != x() || target_y != y()))
        {
            _facing = facing_towards(target_x - x(), target_y - y());
        }

        _vx = 0;
        _vy = 0;
        _reset_anim();
        _update_graphics();
    }

    void player::set_visible(bool visible)
    {
        _visible = visible;
        _sprite.set_visible(visible && ! _run_sprite);

        if(_run_sprite)
        {
            _run_sprite->set_visible(visible);
        }

        _shadow.set_visible(visible);
    }

    bool player::_blocked(int nx, int ny) const
    {
        if(_rect[2] > _rect[0] && nx + hitbox_radius > _rect[0] && nx - hitbox_radius < _rect[2] &&
           ny + hitbox_radius > _rect[1] && ny - hitbox_radius < _rect[3])
        {
            bool inside = x() + hitbox_radius > _rect[0] && x() - hitbox_radius < _rect[2] &&
                    y() + hitbox_radius > _rect[1] && y() - hitbox_radius < _rect[3];

            if(! inside)
            {
                return true;
            }
        }

        // NPCs are solid discs of radius 7 (plus the hitbox); moving away from one is always allowed
        constexpr int radius = 7 + hitbox_radius;

        for(int index = 0; index < _blockers_count; ++index)
        {
            int dx = nx - _blockers[index].x;
            int dy = ny - _blockers[index].y;
            int ox = x() - _blockers[index].x;
            int oy = y() - _blockers[index].y;

            if(((dx * dx) + (dy * dy)) < radius * radius && ((dx * dx) + (dy * dy)) < ((ox * ox) + (oy * oy)))
            {
                return true;
            }
        }

        return false;
    }

    void player::set_facing_index(int facing)
    {
        _facing = facing & 7;
        _shown_facing = _facing;
        _update_graphics();
    }

    void player::sit_on(int seat_x, int seat_y, bool mirrored)
    {
        _seat_mirrored = mirrored;
        _rest_lift = 0;
        _activity = activity::sitting;
        _seat_x = seat_x;
        _seat_y = seat_y;
        _activity_timer = 0;
        _vx = 0;
        _vy = 0;
        _run_sprite.reset();
        _rest_sprite = bn::sprite_items::player_rest.create_sprite(0, 0);
        _rest_sprite->set_bg_priority(2);
        _rest_sprite->set_horizontal_flip(mirrored);
        _apply_lighting();
        _sprite.set_visible(false);
        _shadow.set_visible(false);
    }

    void player::sleep_on(int seat_x, int seat_y, int lift)
    {
        sit_on(seat_x, seat_y);
        _rest_lift = lift;
        _activity = activity::sleeping;
    }

    void player::sit_for(int seat_x, int seat_y, int frames)
    {
        sit_on(seat_x, seat_y);
        _sit_frames = frames;
    }

    void player::start_action(action_kind kind, int target_x, int target_y, int frames)
    {
        _activity = activity::acting;
        _activity_timer = 0;
        _act_kind = kind;
        _act_frames = frames;
        _vx = 0;
        _vy = 0;

        if(target_x != x() || target_y != y())
        {
            _facing = facing_towards(target_x - x(), target_y - y());
        }

        const bn::sprite_item& item = action_item(kind);
        _act_item = &item;
        _run_sprite.reset();
        _act_sprite = item.create_sprite(0, 0, _facing * act_frames_per_facing);
        _act_sprite->set_bg_priority(2);
        _apply_lighting();
        _sprite.set_visible(false);
        update_sprite(_last_cam_x, _last_cam_y);
    }

    void player::approach(int target_x, int target_y, int distance)
    {
        int dx = x() - target_x;
        int dy = y() - target_y;
        int len2 = (dx * dx) + (dy * dy);

        if(len2 == 0)
        {
            return;
        }

        int len = bn::sqrt(len2);

        // the closest free spot on the line, at least `distance` from the target and not further away than now
        for(int d = distance; d < len; d += 2)
        {
            int nx = target_x + (dx * d / len);
            int ny = target_y + (dy * d / len);

            if(! _map->solid_around(nx, ny, hitbox_radius))
            {
                _x = nx;
                _y = ny;
                return;
            }
        }
    }

    void player::_stand_up()
    {
        if(_activity == activity::sitting || _activity == activity::sleeping)
        {
            // stand up where the player was before sitting down (always a free spot; the cell in
            // front of a bench can be solid, which used to trap the player)
            _facing = 1;
            _rest_sprite.reset();
            _sprite.set_visible(true);
            _shadow.set_visible(true);
        }

        if(_activity == activity::acting)
        {
            _act_sprite.reset();
            _sprite.set_visible(true);
        }

        _sit_frames = 0;
        _activity = activity::walking;
        _reset_anim();
        _update_graphics();

        _apply_lighting();
    }

    void player::_update_activity()
    {
        ++_activity_timer;

        if(_activity == activity::acting)
        {
            int frame = (_activity_timer / act_step[int(_act_kind)]) % act_frames_per_facing;

            if(_activity_timer % act_step[int(_act_kind)] == 0)
            {
                _act_sprite->set_tiles(_act_item->tiles_item(), (_facing * act_frames_per_facing) + frame);
            }

            if(_activity_timer >= _act_frames)
            {
                _action_finished = true;
                _stand_up();
            }
            else if(bn::keypad::b_pressed() && _script_facing == -2)
            {
                _stand_up();        // interrupted: the field keeps the part of the gains done so far
            }

            return;
        }

        if(_sit_frames > 0 && _activity_timer >= _sit_frames)
        {
            _action_finished = true;
            _stand_up();
            return;
        }

        // sitting / sleeping: any direction or B gets up again
        if(_script_facing == -2 && (bn::keypad::b_pressed() || bn::keypad::left_pressed() || bn::keypad::right_pressed() ||
           bn::keypad::up_pressed() || bn::keypad::down_pressed()))
        {
            _stand_up();
            return;
        }

        int frame = _activity == activity::sleeping ? (_rest_lift > 0 ? bed_frame : sleep_frame) : (_activity_timer / 20) % 4;
        _rest_sprite->set_tiles(bn::sprite_items::player_rest.tiles_item(), frame);
    }

    void player::update()
    {
        _action_finished = false;

        if(_activity != activity::walking)
        {
            _update_activity();
            return;
        }

        int facing = _script_facing;

        if(facing == -2)
        {
            // d-pad: a changed direction must be held for a few frames before it counts, so pressing or releasing two keys
            // a frame apart does not flicker through an in-between facing (and slide the feet that way)
            int raw = input_facing();
            _raw_count = raw == _raw_facing ? _raw_count + 1 : 0;
            _raw_facing = raw;
            int needed = raw < 0 ? 0 : (_input_facing < 0 ? 1 : 2);

            if(raw != _input_facing && _raw_count >= needed)
            {
                _input_facing = raw;
            }

            facing = _input_facing;
        }

        bn::fixed target_vx;
        bn::fixed target_vy;

        if(facing >= 0)
        {
            _facing = facing;

            // Hold B to run.
            bn::fixed speed = ((_script_facing == -2 ? bn::keypad::b_held() : _script_run) ? run_speed : walk_speed) * _speed_scale;
            target_vx = directions[facing].x * speed;
            target_vy = directions[facing].y * speed;

            if(bn::abs(_vx) + bn::abs(_vy) < bn::fixed(0.1))
            {
                _vx = target_vx * start_kick;       // quick first step instead of a slow ramp
                _vy = target_vy * start_kick;
            }

            _vx += (target_vx - _vx) * acceleration;
            _vy += (target_vy - _vy) * acceleration;
        }
        else
        {
            _vx -= _vx * deceleration;
            _vy -= _vy * deceleration;

            if(bn::abs(_vx) < bn::fixed(0.05) && bn::abs(_vy) < bn::fixed(0.05))
            {
                _vx = 0;
                _vy = 0;
            }
        }

        // Move each axis separately so the player slides along walls.
        bn::fixed old_x = _x;
        bn::fixed old_y = _y;
        bn::fixed new_x = _x + _vx;

        if(! _map->solid_around(new_x.floor_integer(), _y.floor_integer(), hitbox_radius) &&
           ! _blocked(new_x.floor_integer(), _y.floor_integer()))
        {
            _x = new_x;
        }
        else
        {
            _vx = 0;
        }

        bn::fixed new_y = _y + _vy;

        if(! _map->solid_around(_x.floor_integer(), new_y.floor_integer(), hitbox_radius) &&
           ! _blocked(_x.floor_integer(), new_y.floor_integer()))
        {
            _y = new_y;
        }
        else
        {
            _vy = 0;
        }

        // Walk / run animation driven by the distance moved on screen (planted feet), idle breathing when standing.
        bn::fixed moved_x = bn::abs((_x - old_x) - (_y - old_y));
        bn::fixed moved_y = bn::abs((_x - old_x) + (_y - old_y)) / 2;
        bn::fixed moved = moved_x > moved_y ? moved_x + (moved_y / 2) : moved_y + (moved_x / 2);

        if(moved > bn::fixed(0.1))
        {
            bool running = _script_facing == -2 ? bn::keypad::b_held() : _script_run;
            int gait = running ? 2 : 1;

            if(_gait == 0)
            {
                _phase = 0;                         // first step starts at the passing pose
            }

            _gait = gait;
            _phase += moved / (running ? run_step[_facing] : walk_step[_facing]);

            while(_phase >= walk_frames)
            {
                _phase -= walk_frames;
            }
        }
        else if(_gait != 0)
        {
            // come to rest: finish the stride up to the nearest passing pose (frame 0 or 6), then breathe
            bn::fixed half = walk_frames / 2;
            bn::fixed in_half = _phase;

            while(in_half >= half)
            {
                in_half -= half;
            }

            if(in_half < settle_speed || in_half >= half - settle_speed)
            {
                _gait = 0;
                _phase = 0;
                _idle_timer = 0;
            }
            else
            {
                _phase += in_half < half / 2 ? -settle_speed : settle_speed;
            }
        }
        else
        {
            ++_idle_timer;
        }

        _update_graphics();
    }

    void player::update_sprite(int cam_x, int cam_y)
    {
        _last_cam_x = cam_x;
        _last_cam_y = cam_y;

        if(_act_sprite)
        {
            _act_sprite->set_position(image_x() - cam_x - 120, image_y() - cam_y - 80 - feet_offset_y);
            _shadow.set_position(image_x() - cam_x - 120, image_y() - cam_y - 80 - 1);
            _act_sprite->set_bg_priority(2);
            _shadow.set_bg_priority(3);
            return;
        }

        if(_rest_sprite)
        {
            int seat_image_x = _map->to_image_x(_seat_x, _seat_y);
            int seat_image_y = _map->to_image_y(_seat_x, _seat_y);
            _rest_sprite->set_position(seat_image_x - cam_x - 120 + (_seat_mirrored ? rest_mirror_shift : 0), seat_image_y - cam_y - 80 - rest_origin_y - _rest_lift);
            _rest_sprite->set_bg_priority(2);       // on top of the bench
            return;
        }

        // Screen coordinates are relative to the screen centre.
        int screen_x = image_x() - cam_x - 120;
        int screen_y = image_y() - cam_y - 80;
        _sprite.set_position(screen_x, screen_y - feet_offset_y);

        if(_run_sprite)
        {
            _run_sprite->set_position(screen_x, screen_y - feet_offset_y);
            _run_sprite->set_bg_priority(2);
        }

        _shadow.set_position(screen_x, screen_y - 1);

        // Always above the objects layer; the front layer redraws the map pixels that are in front.
        // The shadow lies on the ground, below the objects layer.
        _sprite.set_bg_priority(2);
        _shadow.set_bg_priority(3);
    }

    void player::mask_area(int& x0, int& y0, int& x1, int& y1, int& depth) const
    {
        if(_rest_sprite)
        {
            int sx = _map->to_image_x(_seat_x, _seat_y);
            int sy = _map->to_image_y(_seat_x, _seat_y);
            x0 = sx - 32;
            x1 = sx + 32;
            y0 = sy - rest_origin_y - 32 - _rest_lift;
            y1 = sy - rest_origin_y + 32 - _rest_lift;
            // a bit in front of the seat: the bench stays behind. In bed (_rest_lift > 0) the sleeper lies ON the duvet: his depth is
            // beyond every bed pixel (bed spans about +-48 units around the use point), so he is drawn in front of the whole bed.
            depth = _rest_lift > 0 ? _seat_x + _seat_y + 90 : _seat_x + _seat_y + 12;
            return;
        }

        int ix = image_x();
        int iy = image_y();
        // (kept narrow even for the wide activity sprites: a wider front-layer redraw makes the game lag)
        x0 = ix - 16;
        x1 = ix + 16;
        y0 = iy - 54;
        y1 = iy + 10;
        depth = x() + y();
    }

    void player::set_lighting(const light_params& params)
    {
        _light = params;
        _apply_lighting();
    }

    void player::_apply_lighting()
    {
        bn::color colours[16];
        light_colours(bn::sprite_items::player.palette_item().colors_ref().data(), colours, 16, _light);
        bn::sprite_palette_ptr palette = _sprite.palette();
        palette.set_colors(bn::span<const bn::color>(colours, 16));

        if(_run_sprite)
        {
            light_colours(bn::sprite_items::player_run.palette_item().colors_ref().data(), colours, 16, _light);
            bn::sprite_palette_ptr run_palette = _run_sprite->palette();
            run_palette.set_colors(bn::span<const bn::color>(colours, 16));
        }

        if(_act_sprite)
        {
            light_colours(_act_item->palette_item().colors_ref().data(), colours, 16, _light);
            bn::sprite_palette_ptr act_palette = _act_sprite->palette();
            act_palette.set_colors(bn::span<const bn::color>(colours, 16));
        }

        if(_rest_sprite)
        {
            light_colours(bn::sprite_items::player_rest.palette_item().colors_ref().data(), colours, 16, _light);
            bn::sprite_palette_ptr rest_palette = _rest_sprite->palette();
            rest_palette.set_colors(bn::span<const bn::color>(colours, 16));
        }
    }

    void player::_reset_anim()
    {
        _gait = 0;
        _phase = 0;
        _idle_timer = 0;
        _shown_facing = _facing;
        _turn_timer = 0;
    }

    void player::_update_graphics()
    {
        // turning: the shown facing steps through the in-between facings (1 frame each + turn_hold) instead of snapping
        if(_shown_facing != _facing)
        {
            if(_turn_timer > 0)
            {
                --_turn_timer;
            }
            else
            {
                int diff = (_facing - _shown_facing) & 7;
                _shown_facing = (_shown_facing + (diff <= 4 ? 1 : 7)) & 7;
                _turn_timer = turn_hold - 1;
            }
        }
        else
        {
            _turn_timer = 0;
        }

        int frame;

        if(_gait == 0)
        {
            frame = (_idle_timer / idle_hold) % idle_frames;
        }
        else
        {
            frame = walk_base + _phase.floor_integer();
        }

        bool want_run = _gait == 2 && _activity == activity::walking;

        if(want_run)
        {
            int run_frame = (_shown_facing * run_frames) + _phase.floor_integer();

            if(! _run_sprite)
            {
                _run_sprite = bn::sprite_items::player_run.create_sprite(0, 0, run_frame);
                _run_sprite->set_bg_priority(2);
                _run_sprite->set_visible(_visible);
                _sprite.set_visible(false);
                _apply_lighting();
                update_sprite(_last_cam_x, _last_cam_y);
            }
            else
            {
                _run_sprite->set_tiles(bn::sprite_items::player_run.tiles_item(), run_frame);
            }

            return;
        }

        if(_run_sprite)
        {
            _run_sprite.reset();
            _sprite.set_visible(_visible);
        }

        _sprite.set_tiles(bn::sprite_items::player.tiles_item(), (_shown_facing * frames_per_facing) + frame);
    }
}
