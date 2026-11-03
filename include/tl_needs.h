#ifndef TL_NEEDS_H
#define TL_NEEDS_H

#include "bn_fixed.h"

namespace tl
{
    // The four needs (0..100). They decay every game minute; activities raise them.
    struct needs
    {
        enum index
        {
            hunger,
            energy,
            hygiene,
            fun,
            count
        };

        bn::fixed values[count] = { 70, 60, 50, 60 };

        // Change per game minute when just walking around (tunable).
        static constexpr bn::fixed decay[count] = { -0.07, -0.05, -0.04, -0.06 };

        void add(int need, bn::fixed amount)
        {
            bn::fixed v = values[need] + amount;
            values[need] = v < 0 ? bn::fixed(0) : (v > 100 ? bn::fixed(100) : v);
        }

        void minute_passed()
        {
            for(int need = 0; need < count; ++need)
            {
                add(need, decay[need]);
            }
        }
    };
}

#endif
