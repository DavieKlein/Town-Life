#ifndef TL_TITLE_H
#define TL_TITLE_H

namespace tl
{
    // Title screen. Returns true for Continue (a valid save exists) and false for New Game.
    [[nodiscard]] bool run_title();
}

#endif
