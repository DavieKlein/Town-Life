// s78 (round 3): a sound for every object / activity the player uses. Kept apart from tl_field.cpp so the audio hooks stay in one place.
// Looping sounds follow the player's state each frame, so they stop by themselves when an activity ends or is cancelled with B.

#include "tl_field.h"
#include "tl_audio.h"

namespace tl
{
    void field::_update_audio_sfx()
    {
        using audio::sfx;
        static player::activity prev_activity = player::activity::walking;
        static bool prev_toilet = false;
        static bool prev_pickup = false;

        const player::activity now = _player.current_activity();
        const bool acting = now == player::activity::acting && _act.active;
        const bool toilet = _act.active && now != player::activity::acting && _act.gain[needs::bladder] > 0;
        const bool pickup = acting && _player.current_action_kind() == player::action_kind::pickup;
        sfx loop = sfx::none;

        if(acting)
        {
            switch(_player.current_action_kind())
            {
            case player::action_kind::wash:
                loop = sfx::water;
                break;

            case player::action_kind::eat:
                loop = sfx::munch;
                break;

            case player::action_kind::drink:
                loop = sfx::gulp;
                break;

            case player::action_kind::read:
                loop = sfx::page;
                break;

            case player::action_kind::search:
                loop = sfx::rustle;
                break;

            case player::action_kind::shower:
                loop = sfx::shower;
                break;

            default:
                break;
            }
        }
        else if(now == player::activity::sleeping)
        {
            loop = sfx::snore;
        }

        audio::set_loop(loop);

        if(prev_activity == player::activity::walking && (now == player::activity::sitting || now == player::activity::sleeping))
        {
            audio::play(sfx::thud);         // sat down on a bench / seat / toilet, lay down on a bed
        }

        if(prev_toilet && ! toilet)
        {
            audio::play(sfx::flush);        // the toilet is used up (or B got you up)
        }

        if(prev_pickup && ! pickup)
        {
            audio::play(sfx::clink);        // can / bottle in the bag
        }

        prev_activity = now;
        prev_toilet = toilet;
        prev_pickup = pickup;
    }
}
