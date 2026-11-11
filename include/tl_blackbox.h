#ifndef TL_BLACKBOX_H
#define TL_BLACKBOX_H

#include <stdint.h>

#include "tl_save.h"

// Black box + in-game bug reporter (docs/bug_reports.md).
//
// While the game runs, a core-update callback records the keypad state of every frame (run-length encoded) in EWRAM and takes a snapshot
// of the full save_data every ~15 s (two slots, so one is always 15-30 s old). Pressing L+R together opens the "Report a bug" panel
// (also inside menus, dialogue and minigames: the panel runs its own little loop from inside the callback) and writes a report to SRAM
// after the normal save area: category, game time, snapshot, input log. tools/bug_report.py reads the .srm file and replays a report headlessly.
namespace tl::blackbox
{
    // SRAM layout: the save is at offset 0 (<= 4096 bytes, static_assert in tl_save.h); the report region starts at region_offset.
    constexpr int region_offset = 4096;
    constexpr int slot_count = 4;
    constexpr int log_capacity = 2048;          // RLE entries (u16 = keys | (frames - 1) << 10), 4 KB
    constexpr int marker_capacity = 6;

    struct region_header
    {
        uint32_t magic;                 // 'TLBR'
        uint16_t version;
        uint16_t slots;
        uint32_t next_number;           // number of the next report (1-based)
        uint32_t replay_flag;           // set by tools/bug_report.py: the next Continue restores replay_rng and skips the fade-in
        uint32_t replay_rng[3];
        uint32_t checksum;              // over the bytes before it
        uint32_t reserved[8];
    };

    struct marker
    {
        uint32_t frame;
        uint32_t kind;                  // 1 = minigame started, 2 = field rebuilt, 3 = report
    };

    struct report
    {
        uint32_t magic;                 // 'TLBX'
        uint16_t version;
        uint16_t size;
        uint32_t checksum;              // over every byte after the header (offset 12)
        uint32_t number;
        uint8_t category;               // 1 froze/stuck, 2 graphics, 3 text, 4 objective, 5 other
        uint8_t flags;                  // 1 snapshot usable for replay, 2 snapshot not calm, 4 reported in a minigame, 8 no snapshot
        uint8_t map;                    // at report time
        uint8_t marker_count;
        uint16_t day;
        uint16_t minutes;
        int16_t x;
        int16_t y;
        int32_t money;
        uint32_t frame_now;             // black box frame counter at the report
        uint32_t snap_frame;            // ... at the snapshot
        uint32_t log_frames;            // frames covered by the log (= frame_now - snap_frame)
        uint16_t log_entries;
        uint16_t pad;
        uint32_t rng[3];                // bn::random state of the field at the snapshot
        marker markers[marker_capacity];
        char build[32];                 // "Nov 11 2026 12:00:00" (same text as the title screen)
        save_data snap;                 // finalised: usable as a normal save
        uint16_t log[log_capacity];
    };

    static_assert(region_offset + 64 + slot_count * sizeof(report) <= 32768, "bug report region does not fit in 32 KB SRAM");
    static_assert(sizeof(region_header) == 64, "region header size");

    // What the black box needs from the running field (registered by main.cpp; null while no field exists, e.g. in a minigame).
    struct source
    {
        bool (*snapshot)(save_data& out, uint32_t rng[3]);      // fills a full snapshot
        bool (*live)(uint32_t out[7]);                          // map, x, y, day, minutes, money, playing
        bool (*calm)();                                         // free walking, nothing open
        void (*make_room)();                                    // close the pause screen etc. so the panel fits on screen
    };

    void init();                        // once, after bn::core::init(): installs the update callback, loads the report region
    void start(const source* src);      // recording begins (a field exists); also the reporter is enabled
    void set_source(const source* src); // nullptr while the field is destroyed
    void note_scene(uint32_t kind);     // marker in the log: 1 = minigame started, 2 = field rebuilt
    void force_snapshot();              // right after the field was rebuilt: new snapshot, the older one is dropped

    // Replay mode (set by tools/bug_report.py in the SRAM header): returns true once and clears the flag.
    [[nodiscard]] bool take_replay(uint32_t rng_out[3]);
}

#endif
