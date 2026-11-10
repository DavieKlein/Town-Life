#ifndef TL_NEEDS_H
#define TL_NEEDS_H

#include "bn_fixed.h"

namespace tl
{
    // The five needs (0..100, 100 = fine). They decay every game minute; activities raise them.
    struct needs
    {
        enum index
        {
            hunger,
            energy,
            hygiene,
            fun,
            bladder,
            count
        };

        bn::fixed values[count] = { 70, 60, 50, 60, 80 };

        // Change per game minute when just walking around (tunable).
        static constexpr bn::fixed decay[count] = { -0.07, -0.05, -0.04, -0.06, -0.1 };

        // "Feeling great" (s71): entered when all five bar needs are >= great_enter, kept until one drops below great_exit
        // (hysteresis, so the toast does not flicker). Effect: +10 % pay (rounded up) and +1 friendship on every positive
        // small-talk / gift gain. Social is not part of it.
        static constexpr int great_enter = 70;
        static constexpr int great_exit = 65;

        [[nodiscard]] bool all_at_least(int limit) const
        {
            for(int need = 0; need < count; ++need)
            {
                if(values[need] < limit)
                {
                    return false;
                }
            }

            return true;
        }

        // Social (s63): talking, small talk and gifts fill it, it decays slowly. It is NOT one of the five HUD bars yet (a sixth slot
        // needs the approved HUD proposal): shown as a line in the pause screen. Below 20 (lonely) Fun gains are halved.
        bn::fixed social = 60;
        static constexpr bn::fixed social_decay = -0.05;

        // HUD "+" / "-" markers (s72): every action change (add / add_social) that really moves a value sets the sign (+1 / -1)
        // and a frame timer of pm_frames for that slot (0..4 = needs, 5 = Social). The slow natural decay (minute_passed) does not.
        static constexpr int pm_frames = 60;
        int pm_sign[count + 1] = { 0, 0, 0, 0, 0, 0 };
        int pm_timer[count + 1] = { 0, 0, 0, 0, 0, 0 };

        void mark_change(int slot, bn::fixed before, bn::fixed after)
        {
            if(after != before)
            {
                pm_sign[slot] = after > before ? 1 : -1;
                pm_timer[slot] = pm_frames;
            }
        }

        void add_social(bn::fixed amount)
        {
            bn::fixed before = social;
            _add_social_raw(amount);
            mark_change(count, before, social);
        }

        // After drinking the bladder fills faster for a while (game minutes left).
        int bladder_boost = 0;

        void add(int need, bn::fixed amount)
        {
            bn::fixed before = values[need];
            _add_raw(need, amount);
            mark_change(need, before, values[need]);
        }

        void minute_passed()
        {
            for(int need = 0; need < count; ++need)
            {
                bn::fixed change = decay[need];

                if(need == bladder && bladder_boost > 0)
                {
                    change *= 3;
                }

                _add_raw(need, change);
            }

            _add_social_raw(social_decay);

            if(bladder_boost > 0)
            {
                --bladder_boost;
            }
        }

    private:
        void _add_raw(int need, bn::fixed amount)
        {
            bn::fixed v = values[need] + amount;
            values[need] = v < 0 ? bn::fixed(0) : (v > 100 ? bn::fixed(100) : v);
        }

        void _add_social_raw(bn::fixed amount)
        {
            bn::fixed v = social + amount;
            social = v < 0 ? bn::fixed(0) : (v > 100 ? bn::fixed(100) : v);
        }
    };
}

#endif
