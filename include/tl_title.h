#ifndef TL_TITLE_H
#define TL_TITLE_H

namespace tl
{
    // Title screen. Returns true for Continue (a valid save exists) and false for New Game.
    [[nodiscard]] bool run_title();

    // The four narrator cards of a new game (black screen, one card at a time, A skips) before the name entry.
    void run_intro_cards();
}

#endif
