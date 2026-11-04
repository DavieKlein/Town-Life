#ifndef TL_NAME_ENTRY_H
#define TL_NAME_ENTRY_H

namespace tl
{
    // "What is your name?" at the start of a new game: an on-screen keyboard in the UI style (Night). D-pad moves, A types
    // the key, B deletes, START confirms. Up to 10 letters, the first letter and the one after a space are capitals
    // (SELECT switches the case by hand). Blocks until the player confirmed the name; `out` must hold 12 chars.
    void run_name_entry(char* out);
}

#endif
