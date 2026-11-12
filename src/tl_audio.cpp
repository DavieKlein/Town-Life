#include "tl_audio.h"

#include "bn_fixed.h"
#include "bn_music.h"
#include "bn_music_items.h"
#include "bn_sound_items.h"

namespace tl::audio
{
    namespace
    {
        constexpr bn::fixed duck_factor = 0.45;
        constexpr bn::fixed night_factor = 0.7;
        constexpr bn::fixed fade_down = 0.08;       // about 12 frames
        constexpr bn::fixed fade_up = 0.035;        // about 28 frames
        constexpr bn::fixed sfx_volume = 0.85;

        track _playing = track::none;       // what the sound hardware currently plays
        track _wanted = track::none;
        bn::fixed _base = 1;                // base volume of the wanted track
        bn::fixed _current = 0;             // volume actually applied
        bool _night = false;
        bool _ducked = false;
        bool _outdoor_wanted = false;
        bool _has_map = false;
        map_id _last_map = map_id::city_centre;

        bool is_outdoor(map_id id)
        {
            return id == map_id::city_centre || id == map_id::old_block;
        }

        bool has_door_bell(map_id id)
        {
            return id == map_id::corner_market || id == map_id::lane_shop || id == map_id::bakery ||
                   id == map_id::diner || id == map_id::laundromat;
        }

        bn::fixed target()
        {
            bn::fixed v = _base;

            if(_outdoor_wanted && _night)
            {
                v *= night_factor;
            }

            if(_ducked)
            {
                v *= duck_factor;
            }

            return v;
        }

        void start(track t)
        {
#ifdef TL_AUDIO_OFF
            _playing = t;       // CPU baseline builds: no music at all
            _current = 0;
            return;
#endif
            switch(t)
            {
            case track::city:
                bn::music_items::city_day.play(0);
                break;

            case track::old_block:
                bn::music_items::old_block.play(0);
                break;

            case track::market:
                bn::music_items::market.play(0);
                break;

            default:
                break;
            }

            _playing = t;
            _current = 0;
        }
    }

    track track_for(map_id id)
    {
        switch(id)
        {
        case map_id::city_centre:
            return track::city;

        case map_id::old_block:
            return track::old_block;

        case map_id::corner_market:
        case map_id::lane_shop:
        case map_id::bakery:
        case map_id::diner:
        case map_id::community_centre:
        case map_id::laundromat:
        case map_id::mia_flat:
        case map_id::player_room:
        case map_id::clinic:
            return track::market;

        default:
            // VaultMart / VaultTech lobby (cold: no music, the robot voice is enough), public toilet, sewer
            return track::none;
        }
    }

    int volume_for(map_id id)
    {
        switch(id)
        {
        case map_id::city_centre:
        case map_id::old_block:
            return 100;

        case map_id::corner_market:
        case map_id::lane_shop:
        case map_id::bakery:
        case map_id::diner:
            return 85;

        case map_id::community_centre:
        case map_id::laundromat:
        case map_id::mia_flat:
        case map_id::player_room:
        case map_id::clinic:
            return 35;      // quiet background in the other homes and public rooms

        default:
            return 0;
        }
    }

    void set_map(map_id id)
    {
        if(_has_map && id == _last_map)
        {
            return;
        }

        if(_has_map && is_outdoor(_last_map) && has_door_bell(id))
        {
            play(sfx::door_bell);
        }

        _has_map = true;
        _last_map = id;
        _wanted = track_for(id);
        _base = bn::fixed(volume_for(id)) / 100;
        _outdoor_wanted = is_outdoor(id);
    }

    void set_night(bool night)
    {
        _night = night;
    }

    void set_track(track t, int volume_percent, bool instant)
    {
        _wanted = t;
        _base = bn::fixed(volume_percent) / 100;
        _outdoor_wanted = false;
        _has_map = false;       // the next map change re-selects the track by place

        if(instant)
        {
            _ducked = false;        // instant calls come from blocking loops (minigames) where nothing ducks the music

            if(_playing != t)
            {
#ifndef TL_AUDIO_OFF
                if(_playing != track::none)
                {
                    bn::music::stop();
                    _playing = track::none;
                }

                if(t != track::none)
                {
                    start(t);
                }
#endif
            }

            _current = t == track::none ? bn::fixed(0) : target();

#ifndef TL_AUDIO_OFF
            if(_playing != track::none)
            {
                bn::music::set_volume(_current);
            }
#endif
        }
    }

    void stop(bool instant)
    {
        set_track(track::none, 0, instant);
    }

    void duck(bool on)
    {
        _ducked = on;
    }

    void play(sfx s)
    {
#ifdef TL_AUDIO_OFF
        return;
#endif
        switch(s)
        {
        case sfx::blip:
            bn::sound_items::menu_blip.play(sfx_volume);
            break;

        case sfx::confirm:
            bn::sound_items::confirm.play(sfx_volume);
            break;

        case sfx::back:
            bn::sound_items::menu_back.play(sfx_volume);
            break;

        case sfx::coin:
            bn::sound_items::coin.play(sfx_volume);
            break;

        case sfx::cash:
            bn::sound_items::cash.play(sfx_volume);
            break;

        case sfx::door_bell:
            bn::sound_items::door_bell.play(sfx_volume);
            break;

        case sfx::mission:
            bn::sound_items::mission_complete.play(1);
            break;

        default:
            break;
        }
    }

    void update()
    {
#ifdef TL_AUDIO_OFF
        return;
#endif
        if(_playing != _wanted)
        {
            // fade the old track out, then switch
            if(_current > 0)
            {
                _current -= fade_down;

                if(_current < 0)
                {
                    _current = 0;
                }

                bn::music::set_volume(_current);
                return;
            }

            if(_playing != track::none)
            {
                bn::music::stop();
                _playing = track::none;
            }

            if(_wanted != track::none)
            {
                start(_wanted);
            }
            else
            {
                return;
            }
        }

        if(_playing == track::none)
        {
            return;
        }

        bn::fixed t = target();

        if(_current != t)
        {
            if(_current < t)
            {
                _current += fade_up;

                if(_current > t)
                {
                    _current = t;
                }
            }
            else
            {
                _current -= fade_down;

                if(_current < t)
                {
                    _current = t;
                }
            }

            bn::music::set_volume(_current);
        }
    }
}
