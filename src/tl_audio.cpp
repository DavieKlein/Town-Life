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
        constexpr bn::fixed sfx_volume = 1;

        track _playing = track::none;       // what the sound hardware currently plays
        track _wanted = track::none;
        bn::fixed _base = 1;                // base volume of the wanted track
        bn::fixed _current = 0;             // volume actually applied
        bool _night = false;
        bool _ducked = false;
        int _jingle_frames = 0;
        bn::fixed _jingle_factor = 1;
        int _received_cooldown = 0;
        int _frame = 0;
        int _last_reaction = -100;
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

            if(_jingle_frames > 0)
            {
                v *= _jingle_factor;
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

            case track::victor:
                bn::music_items::victor.play(0);
                break;

            case track::sad:
                bn::music_items::sad.play(0);
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
#ifdef TL_DEBUG_AUDIOLOG
        // Debug build only: a log of every sfx started (read from a savestate by tools/music/audiolog.py, magic "TLAU")
        struct audio_log
        {
            char magic[4] = { 'T', 'L', 'A', 'U' };
            unsigned count = 0;
            unsigned frame[96];
            unsigned id[96];
            unsigned track = 0;
            unsigned voices = 0;
            unsigned reactions = 0;
        };

        audio_log _audio_log;
#endif

        bn::optional<bn::sound_handle> play_handle(sfx s)
        {
#ifdef TL_DEBUG_AUDIOLOG
            if(s != sfx::none && s != sfx::click && _audio_log.count < 96)
            {
                _audio_log.frame[_audio_log.count] = unsigned(_frame);
                _audio_log.id[_audio_log.count] = unsigned(s);
                ++_audio_log.count;
            }
#endif
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
            case sfx::mission: jingle_duck(210, 25); return mission_complete.play(1);
            case sfx::water: return water.play(0.8);
            case sfx::shower: return shower.play(0.7);
            case sfx::munch: return munch.play(1);
            case sfx::gulp: return gulp.play(0.9);
            case sfx::flush: return flush.play(0.8);
            case sfx::page: return page.play(1);
            case sfx::rustle: return rustle.play(0.9);
            case sfx::clink: return clink.play(1);
            case sfx::whirr: return whirr.play(0.85);
            case sfx::snore: return snore.play(0.6);
            case sfx::thud: return thud.play(1);
            case sfx::door: return door.play(0.85);
            case sfx::beep: return beep.play(0.85);
            case sfx::scratch: return scratch.play(0.9);
            case sfx::ladder: return ladder.play(1);
            case sfx::manhole: return manhole.play(1);
            case sfx::mg_good: return mg_good.play(0.9);
            case sfx::mg_bad: return mg_bad.play(0.9);
            case sfx::mg_clink: return mg_clink.play(1);
            case sfx::click: return click.play(0.7);
            case sfx::received: return bn::sound_items::received.play(1);
            case sfx::car_arrive: return car_arrive.play(0.9);
            case sfx::car_brake: return car_brake.play(0.9);
            case sfx::car_door: return car_door.play(1);
            case sfx::car_leave: return car_leave.play(0.9);
            case sfx::flash: return flash.play(1);
            case sfx::newspaper: return newspaper.play(1);
            case sfx::phone_ring: return phone_ring.play(0.9);
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

    namespace
    {
        // timbres: 0 soft, 1 warm, 2 bright, 3 pomp, 4 robot
        struct voice_info
        {
            int timbre;
            bn::fixed speed;
        };

        voice_info voice_of(int speaker)
        {
            switch(speaker)
            {
            case 0: return { 0, 1.15 };      // mia
            case 1: return { 2, 0.95 };      // rosa
            case 2: return { 2, 1.25 };      // dex
            case 3: return { 1, 0.9 };       // pimm
            case 4: return { 1, 0.72 };      // lou
            case 5: return { 1, 0.8 };       // halloran
            case 6: return { 0, 0.85 };      // okafor
            case 7: return { 3, 1.15 };      // dex (VaultMart)
            case 8: return { 3, 0.82 };      // victor
            case 9: return { 4, 1.0 };       // the Valet (robot)
            case 10: return { 2, 1.05 };     // ines
            case 11: return { 2, 1.35 };     // teo
            case 12: return { 1, 0.68 };     // grigor
            case 13: return { 1, 0.8 };      // valdez
            case 14: return { 3, 0.95 };     // pruitt
            case 15: return { 0, 1.3 };      // nella
            case 16: return { 3, 0.9 };      // kessler
            case 17: return { 4, 0.75 };     // trench-e
            case 18: return { 0, 0.95 };     // the duchess
            case 19: return { 3, 1.0 };      // the captain
            case 253: return { 0, 1.0 };     // the player
            default: return { -1, 1 };
            }
        }
    }

    void voice(int speaker, int letter_index)
    {
#ifdef TL_AUDIO_OFF
        return;
#endif
        const voice_info v = voice_of(speaker);

        if(v.timbre < 0)
        {
            return;
        }
#ifdef TL_DEBUG_AUDIOLOG
        ++_audio_log.voices;
#endif

        // a little pitch wobble per syllable so it sounds like gibberish speech, two vowel shapes per voice
        const bn::fixed speed = v.speed * (bn::fixed(1) + bn::fixed((letter_index * 7) % 5 - 2) / 25);
        const bool b = ((letter_index * 5) % 3) == 0;
        const bn::fixed vol = 0.55;
        using namespace bn::sound_items;

        switch(v.timbre)
        {
        case 0: (b ? voice_soft_b : voice_soft_a).play(vol, speed, 0); break;
        case 1: (b ? voice_warm_b : voice_warm_a).play(vol, speed, 0); break;
        case 2: (b ? voice_bright_b : voice_bright_a).play(vol, speed, 0); break;
        case 3: (b ? voice_pomp_b : voice_pomp_a).play(vol, speed, 0); break;
        default: (b ? voice_robot_b : voice_robot_a).play(vol, speed, 0); break;
        }
    }

    void reaction(int speaker, bool positive)
    {
#ifdef TL_AUDIO_OFF
        return;
#endif
        const voice_info v = voice_of(speaker);

        if(v.timbre < 0 || _frame - _last_reaction < 40)
        {
            return;
        }

        _last_reaction = _frame;
#ifdef TL_DEBUG_AUDIOLOG
        ++_audio_log.reactions;
#endif
        const bn::fixed vol = 0.85;
        using namespace bn::sound_items;

        switch(v.timbre)
        {
        case 0: (positive ? pos_soft : neg_soft).play(vol, v.speed, 0); break;
        case 1: (positive ? pos_warm : neg_warm).play(vol, v.speed, 0); break;
        case 2: (positive ? pos_bright : neg_bright).play(vol, v.speed, 0); break;
        case 3: (positive ? pos_pomp : neg_pomp).play(vol, v.speed, 0); break;
        default: (positive ? pos_robot : neg_robot).play(vol, v.speed, 0); break;
        }
    }

    void received()
    {
        play(sfx::received);
        _received_cooldown = 150;
        jingle_duck(70, 55);
    }

    void play_money(bool up)
    {
        if(up && _received_cooldown > 0)
        {
            return;         // the "received" jingle already told the player
        }

        play(up ? sfx::coin : sfx::cash);
    }

    void jingle_duck(int frames, int percent)
    {
        _jingle_frames = frames;
        _jingle_factor = bn::fixed(percent) / 100;
    }

    void restore()
    {
        _has_map = false;
    }

    void set_loop(sfx s)
    {
        _loop = s;
    }

    void update()
    {
#ifdef TL_DEBUG_AUDIOLOG
        _audio_log.track = unsigned(_playing);
#endif
#ifdef TL_AUDIO_OFF
        return;
#endif
        ++_frame;

        if(_jingle_frames > 0)
        {
            --_jingle_frames;
        }

        if(_received_cooldown > 0)
        {
            --_received_cooldown;
        }

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
