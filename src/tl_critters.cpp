#include "tl_critters.h"

#include "bn_math.h"
#include "bn_sprite_items_pigeon.h"
#include "bn_sprite_items_squirrel.h"

namespace tl
{
    namespace
    {
        // Sprite frames (see tools/critters.py)
        constexpr int pigeon_stand = 0;
        constexpr int pigeon_peck = 1;
        constexpr int pigeon_hop = 2;
        constexpr int pigeon_fly_up = 3;
        constexpr int pigeon_fly_down = 4;
        constexpr int squirrel_sit = 0;
        constexpr int squirrel_run_a = 1;
        constexpr int squirrel_climb = 3;

        constexpr int pigeon_scare_distance = 56;     // world units
        constexpr int squirrel_scare_distance = 60;
        constexpr int return_distance = 150;          // player must be this far away before animals come back
        constexpr int feet_y = 13 - 8;                 // feet inside the 16x16 frame, relative to its centre

        [[nodiscard]] int distance2(bn::fixed ax, bn::fixed ay, int bx, int by)
        {
            int dx = ax.integer() - bx;
            int dy = ay.integer() - by;
            return (dx * dx) + (dy * dy);
        }

        // Direction (unit-ish vector) from the player to (x, y).
        void away_from(bn::fixed x, bn::fixed y, int px, int py, bn::fixed& out_x, bn::fixed& out_y)
        {
            bn::fixed dx = x - px;
            bn::fixed dy = y - py;
            bn::fixed len = bn::abs(dx) + bn::abs(dy);

            if(len < 1)
            {
                dx = 1;
                dy = 0;
                len = 1;
            }

            out_x = dx / len;
            out_y = dy / len;
        }
    }

    void critters::clear()
    {
        _critters.clear();
        _map = nullptr;
    }

    void critters::load(const map_info& map)
    {
        clear();
        _map = &map;

        for(int index = 0; index < map.critters_count && ! _critters.full(); ++index)
        {
            const critter_spawn& spawn = map.critters[index];
            bn::sprite_ptr sprite = spawn.kind == critter_kind::pigeon ?
                        bn::sprite_items::pigeon.create_sprite(0, 0) :
                        bn::sprite_items::squirrel.create_sprite(0, 0);
            sprite.set_visible(false);
            critter c { bn::move(sprite), &spawn, spawn.x, spawn.y, 0, 0, 0, 0 };
            c.timer = _random_int(90);
            c.flip = _random_int(2) == 0;
            _critters.push_back(bn::move(c));
        }
    }

    void critters::update(int player_x, int player_y, int cam_x, int cam_y)
    {
        for(critter& c : _critters)
        {
            if(c.spawn->kind == critter_kind::pigeon)
            {
                _update_pigeon(c, player_x, player_y);
            }
            else
            {
                _update_squirrel(c, player_x, player_y);
            }

            _place_sprite(c, cam_x, cam_y);
        }
    }

    void critters::_update_pigeon(critter& c, int player_x, int player_y)
    {
        switch(c.current)
        {

        case state::idle:
            if(distance2(c.x, c.y, player_x, player_y) < pigeon_scare_distance * pigeon_scare_distance)
            {
                // Take off: away from the player and up into the sky.
                away_from(c.x, c.y, player_x, player_y, c.vx, c.vy);
                c.vx = c.vx * bn::fixed(1.6) + bn::fixed(_random_int(40) - 20) / 100;
                c.vy = c.vy * bn::fixed(1.6) + bn::fixed(_random_int(40) - 20) / 100;
                c.vz = bn::fixed(0.6) + bn::fixed(_random_int(40)) / 100;
                c.current = state::fleeing;
                c.anim = 0;
                break;
            }

            if(--c.timer <= 0)
            {
                // Random little behaviours: peck, hop a bit, turn around.
                int action = _random_int(4);
                c.timer = 30 + _random_int(80);

                if(action == 0)
                {
                    c.frame = pigeon_peck;
                    c.anim = 12;
                }
                else if(action == 1)
                {
                    c.flip = ! c.flip;
                }
                else
                {
                    bn::fixed hop = c.flip ? -3 : 3;
                    bn::fixed nx = c.x + hop / 2;
                    bn::fixed ny = c.y - hop / 2;

                    // stay close to the home spot and off solid cells
                    if(bn::abs(nx - c.spawn->x) < 20 && bn::abs(ny - c.spawn->y) < 20 &&
                       ! _map->solid_at(nx.integer(), ny.integer()))
                    {
                        c.x = nx;
                        c.y = ny;
                    }

                    c.frame = pigeon_hop;
                    c.anim = 6;
                }
            }

            if(c.anim > 0 && --c.anim == 0)
            {
                c.frame = pigeon_stand;
            }
            break;

        case state::fleeing:
            c.x += c.vx;
            c.y += c.vy;
            c.z += c.vz;
            c.vz += bn::fixed(0.04);
            c.flip = (c.vx - c.vy) < 0;     // screen-x direction
            c.frame = ((++c.anim / 3) % 2) ? pigeon_fly_up : pigeon_fly_down;

            if(c.z > 170)
            {
                c.current = state::gone;
                c.timer = 300 + _random_int(400);
            }
            break;

        case state::gone:
            if(--c.timer <= 0 &&
               distance2(bn::fixed(c.spawn->x), bn::fixed(c.spawn->y), player_x, player_y) >
               return_distance * return_distance)
            {
                // Land back on the home spot, coming down from the sky.
                c.x = c.spawn->x + _random_int(16) - 8;
                c.y = c.spawn->y + _random_int(16) - 8;
                c.z = 110;
                c.current = state::returning;
            }
            break;

        case state::returning:
            c.z -= bn::fixed(1.4);
            c.frame = ((++c.anim / 3) % 2) ? pigeon_fly_up : pigeon_fly_down;

            if(c.z <= 0)
            {
                c.z = 0;
                c.frame = pigeon_stand;
                c.current = state::idle;
                c.timer = 40 + _random_int(60);
            }
            break;

        default:
            break;
        }
    }

    void critters::_update_squirrel(critter& c, int player_x, int player_y)
    {
        switch(c.current)
        {

        case state::idle:
            c.frame = squirrel_sit;

            if(distance2(c.x, c.y, player_x, player_y) < squirrel_scare_distance * squirrel_scare_distance)
            {
                if(c.spawn->tree_x >= 0)
                {
                    // Dash to the tree.
                    bn::fixed dx = c.spawn->tree_x - c.x;
                    bn::fixed dy = c.spawn->tree_y - c.y;
                    bn::fixed len = bn::abs(dx) + bn::abs(dy);

                    if(len < 1)
                    {
                        len = 1;
                    }

                    c.vx = dx * bn::fixed(2.4) / len;
                    c.vy = dy * bn::fixed(2.4) / len;
                }
                else
                {
                    away_from(c.x, c.y, player_x, player_y, c.vx, c.vy);
                    c.vx *= bn::fixed(2.4);
                    c.vy *= bn::fixed(2.4);
                }

                c.current = state::fleeing;
                c.timer = 90;
                break;
            }

            if(--c.timer <= 0)
            {
                c.flip = ! c.flip;      // look around
                c.timer = 60 + _random_int(120);
            }
            break;

        case state::fleeing:
            {
                bn::fixed nx = c.x + c.vx;
                bn::fixed ny = c.y + c.vy;
                c.flip = (c.vx - c.vy) < 0;
                c.frame = squirrel_run_a + ((++c.anim / 3) % 2);

                bool at_tree = c.spawn->tree_x >= 0 && bn::abs(c.x - c.spawn->tree_x) < 4 &&
                        bn::abs(c.y - c.spawn->tree_y) < 4;

                if(at_tree)
                {
                    c.x = c.spawn->tree_x;
                    c.y = c.spawn->tree_y + 1;
                    c.current = state::climbing;
                }
                else if(--c.timer <= 0 || (c.spawn->tree_x < 0 && _map->solid_at(nx.integer(), ny.integer())))
                {
                    c.current = state::gone;      // vanished into the bushes
                    c.timer = 400 + _random_int(400);
                }
                else
                {
                    c.x = nx;
                    c.y = ny;
                }
            }
            break;

        case state::climbing:
            c.frame = squirrel_climb;
            c.z += bn::fixed(1.5);

            if(c.z > 62)                        // up into the canopy
            {
                c.current = state::gone;
                c.timer = 400 + _random_int(400);
            }
            break;

        case state::gone:
            if(--c.timer <= 0 &&
               distance2(bn::fixed(c.spawn->x), bn::fixed(c.spawn->y), player_x, player_y) >
               return_distance * return_distance)
            {
                c.x = c.spawn->x;
                c.y = c.spawn->y;
                c.z = 0;
                c.current = state::idle;
                c.timer = 60;
            }
            break;

        default:
            break;
        }
    }

    void critters::_place_sprite(critter& c, int cam_x, int cam_y)
    {
        if(c.current == state::gone)
        {
            c.sprite.set_visible(false);
            return;
        }

        int image_x = _map->origin_x + (c.x - c.y).round_integer();
        int image_y = _map->origin_y + ((c.x + c.y) / 2).round_integer() - c.z.round_integer();
        int screen_x = image_x - cam_x - 120;
        int screen_y = image_y - cam_y - 80;

        // Off screen (with margin) or behind the HUD bar: hide.
        bool visible = screen_x > -136 && screen_x < 136 && screen_y > -96 && screen_y < 52;
        c.sprite.set_visible(visible);

        if(! visible)
        {
            return;
        }

        c.sprite.set_position(screen_x, screen_y - feet_y);
        c.sprite.set_horizontal_flip(! c.flip);
        bn::sprite_tiles_item tiles = c.spawn->kind == critter_kind::pigeon ?
                    bn::sprite_items::pigeon.tiles_item() : bn::sprite_items::squirrel.tiles_item();
        c.sprite.set_tiles(tiles, c.frame);

        // Flying birds above everything except the HUD; on the ground the same depth rule as the player.
        if(c.z > 24 && c.current != state::climbing)
        {
            c.sprite.set_bg_priority(1);
        }
        else
        {
            int ground_x = c.x.integer();
            int ground_y = c.y.integer();
            c.sprite.set_bg_priority(_map->player_hidden(ground_x, ground_y, 5, 12) ? 3 : 2);
        }
    }
}
