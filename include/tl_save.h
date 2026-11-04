#ifndef TL_SAVE_H
#define TL_SAVE_H

#include <stdint.h>

#include "tl_map_id.h"

namespace tl
{
    // The save file in cartridge SRAM (written only when the player picks "Save game", never automatically).
    // Everything is fixed-width and packed into one struct at SRAM offset 0. The reserved fields (name, story
    // flags, mission, friendship, spare bytes) exist so the format does not need to change soon; unused ones
    // stay zero. Change `save_version` when the layout changes (old saves are then ignored).
    struct save_data
    {
        static constexpr uint32_t magic_value = 0x56534C54;     // "TLSV"
        static constexpr uint16_t save_version = 2;
        static constexpr int max_maps = 8;                      // bin cooldown slots reserved per map index
        static constexpr int bins_per_map = 16;
        static constexpr int needs_count = 5;
        static constexpr int name_size = 12;
        static constexpr int npc_slots = 16;
        static constexpr int talk_slots = 8;        // NPCs with small-talk memory

        // header
        uint32_t magic = magic_value;
        uint16_t version = save_version;
        uint16_t size = 0;
        uint32_t checksum = 0;          // over every byte after the header

        // world
        uint8_t map = 0;                // map_id
        uint8_t facing = 0;             // player facing index 0..7
        int16_t x = 0;                  // feet position, world units
        int16_t y = 0;
        uint16_t day = 1;
        uint16_t minutes = 8 * 60;      // time of day
        uint16_t minute_frames = 0;
        uint16_t pad_world = 0;
        int32_t total_minutes = 0;
        int32_t money = 20;

        // needs (bn::fixed raw data) and drink timer
        int32_t need_raw[needs_count] = {};
        int16_t bladder_boost = 0;
        uint16_t pad_needs = 0;

        // bin cooldown state: total_minutes + 1 when last searched, 0 = never
        int32_t bin_emptied[max_maps * bins_per_map] = {};

        // reserved for the future
        char player_name[name_size] = {};
        uint8_t story_flags[64] = {};
        uint16_t mission_id = 0;
        uint16_t pad_mission = 0;
        uint8_t friendship[npc_slots] = {};
        // can & bottle deposit (carved out of the former spare bytes, so the layout size is unchanged)
        uint8_t deposit_init = 0;               // 1 once the pickup state below is valid (else the field tops up)
        uint8_t deposit_cans = 0;               // bag
        uint8_t deposit_bottles = 0;
        uint8_t deposit_credit = 0;             // 0 or 1
        uint8_t deposit_spot[32] = {};          // per pickup spot: 0 = none, kind (1 can, 2 bottle) | variant << 2
        uint8_t spare[28] = {};
        // story (version 2): small talk memory per NPC (per topic: day mod 64 << 2 | uses), last talk day, daily gain,
        // City Coins, finished missions
        uint8_t topic_mem[talk_slots][8] = {};
        uint8_t talk_day[talk_slots] = {};      // day (mod 256) of the last conversation, 0 = never
        uint8_t gain_day[talk_slots] = {};      // day (mod 256) `gained` belongs to
        uint8_t gained[talk_slots] = {};
        uint8_t coin_day[talk_slots] = {};
        uint8_t coin70 = 0;                     // bit per NPC: friendship reached 70 once
        uint8_t pad_story = 0;
        uint16_t coins = 0;
        uint32_t missions_done = 0;
    };

    static_assert(maps_count <= save_data::max_maps, "raise save_data::max_maps (and the save version)");

    // True if SRAM holds a valid save (magic, version, size, checksum and ranges all fine); fills `out`.
    [[nodiscard]] bool save_read(save_data& out);

    // Writes the save (fills magic, version, size and checksum).
    void save_write(save_data& data);
}

#endif
