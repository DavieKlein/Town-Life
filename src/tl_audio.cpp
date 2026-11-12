#include "tl_audio.h"

#include "bn_fixed.h"
#include "bn_music.h"
#include "bn_optional.h"
#include "bn_sound_handle.h"
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

            case track::stock_it:
                bn::music_items::stock_it.play(0);
                break;

            case track::plate_rush:
                bn::music_items::plate_rush.play(0);
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

        if(_has_map)
        {
            if(id == map_id::sewer)
            {
                play(sfx::manhole);
                play(sfx::ladder);
            }
            else if(_last_map == map_id::sewer)
            {
                play(sfx::ladder);
            }
            else if(is_outdoor(_last_map) && has_door_bell(id))
            {
                play(sfx::door_bell);        // shops ring the bell (plus the door)
                play(sfx::door);
            }
            else
            {
                play(sfx::door);
            }
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

    namespace
    {
        bn::optional<bn::sound_handle> play_handle(sfx s)
        {
            using namespace bn::sound_items;
            const bn::fixed v = sfx_volume;

            switch(s)
            {
            case sfx::blip: return menu_blip.play(v);
            case sfx::confirm: return confirm.play(v);
            case sfx::back: return menu_back.play(v);
            case sfx::coin: return coin.play(v);
            case sfx::cash: return cash.play(v);
            case sfx::door_bell: return door_bell.play(v);
            case sfx::mission: return mission_complete.play(1);
            case sfx::water: return water.play(0.5);
            case sfx::shower: return shower.play(0.45);
            case sfx::munch: return munch.play(0.7);
            case sfx::gulp: return gulp.play(0.6);
            case sfx::flush: return flush.play(0.55);
            case sfx::page: return page.play(0.6);
            case sfx::rustle: return rustle.play(0.55);
            case sfx::clink: return clink.play(0.7);
            case sfx::whirr: return whirr.play(0.6);
            case sfx::snore: return snore.play(0.35);
            case sfx::thud: return thud.play(0.6);
            case sfx::door: return door.play(0.6);
            case sfx::beep: return beep.play(0.6);
            case sfx::scratch: return scratch.play(0.6);
            case sfx::ladder: return ladder.play(0.7);
            case sfx::manhole: return manhole.play(0.7);
            case sfx::mg_good: return mg_good.play(0.6);
            case sfx::mg_bad: return mg_bad.play(0.6);
            case sfx::mg_clink: return mg_clink.play(0.6);
            default: break;
            }

            return bn::nullopt;
        }

        sfx _loop = sfx::none;
        bn::optional<bn::sound_handle> _loop_handle;
    }

    void play(sfx s)
    {
#ifdef TL_AUDIO_OFF
        return;
#endif
        play_handle(s);
    }

    void set_loop(sfx s)
    {
        _loop = s;
    }

    void update()
    {
#ifdef TL_AUDIO_OFF
        return;
#endif
        // looping activity sound: restart the clip when it ended, stop it as soon as it is not wanted any more
        if(_loop == sfx::none)
        {
            if(_loop_handle)
            {
                _loop_handle->stop();
                _loop_handle.reset();
            }
        }
        else if(! _loop_handle || ! _loop_handle->active())
        {
            _loop_handle = play_handle(_loop);
        }

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
