#include "tl_blackbox.h"

#include <new>
#include <stddef.h>

#include "bn_core.h"
#include "bn_keypad.h"
#include "bn_sram.h"
#include "bn_sprites.h"
#include "bn_sprite_tiles.h"
#include "bn_string_view.h"

#include "tl_ui.h"
#include "tl_pause.h"

namespace tl::blackbox
{
    namespace
    {
        constexpr uint32_t ram_magic = 0x42424C54;          // "TLBB"
        constexpr uint32_t region_magic = 0x52424C54;       // "TLBR"
        constexpr uint32_t report_magic = 0x58424C54;       // "TLBX"
        constexpr uint16_t format_version = 1;
        constexpr uint32_t snapshot_period = 15 * 60;       // frames
        constexpr uint32_t snapshot_patience = 10 * 60;     // wait this long for a calm moment, then snapshot anyway
        constexpr int category_count = 5;

        // The fields the host tool reads out of EWRAM (found by the magic): keep the order.
        struct visible
        {
            uint32_t magic;
            uint32_t frame;         // key frames recorded so far
            uint32_t active;
            uint32_t reports;       // reports written since boot
            uint32_t live[7];       // map, x, y, day, minutes, money, playing
            uint32_t in_panel;
            uint32_t snapshots;
            uint32_t tiles_free;    // sprite tiles / OAM entries free when the last report was opened
            uint32_t items_free;
            uint32_t panel_tiles;   // free while the panel was open (measuring aid for the thresholds below)
            uint32_t panel_items;
        };

        struct snapshot_slot
        {
            save_data data;
            uint32_t frame;
            uint32_t rng[3];
            bool valid;
            bool calm;
        };

        // save_data has default member initialisers: keep it out of static constructors (raw storage, constructed on use)
        template<typename T>
        struct raw
        {
            alignas(T) uint8_t bytes[sizeof(T)];

            T& get()
            {
                return *reinterpret_cast<T*>(bytes);
            }
        };

        BN_DATA_EWRAM_BSS visible vis;
        BN_DATA_EWRAM_BSS raw<snapshot_slot> slots_raw[2];
        BN_DATA_EWRAM_BSS uint16_t ring[log_capacity];
        BN_DATA_EWRAM_BSS raw<report> work_raw;             // the report being written
        BN_DATA_EWRAM_BSS region_header header;
        BN_DATA_EWRAM_BSS marker markers[marker_capacity];

        const source* src = nullptr;
        int ring_count = 0;                 // entries in the ring
        int ring_head = 0;                  // index of the oldest entry
        uint32_t ring_first_frame = 0;      // frame index of the first frame covered by the oldest entry
        uint32_t marker_total = 0;
        uint32_t next_snapshot = snapshot_period;
        uint32_t last_report_frame = 0;
        bool enabled = false;
        bool in_panel = false;

        [[nodiscard]] uint32_t checksum_bytes(const void* data, int size)
        {
            const uint8_t* bytes = static_cast<const uint8_t*>(data);
            uint32_t a = 1;
            uint32_t b = 0;

            for(int index = 0; index < size; ++index)
            {
                a = (a + bytes[index]) % 65521;
                b = (b + a) % 65521;
            }

            return (b << 16) | a;
        }

        [[nodiscard]] uint16_t read_keys()
        {
            // GBA keypad bit order (A, B, Select, Start, Right, Left, Up, Down, R, L), bit set = held
            return uint16_t((bn::keypad::a_held() ? 1 : 0) | (bn::keypad::b_held() ? 2 : 0) | (bn::keypad::select_held() ? 4 : 0) |
                            (bn::keypad::start_held() ? 8 : 0) | (bn::keypad::right_held() ? 16 : 0) | (bn::keypad::left_held() ? 32 : 0) |
                            (bn::keypad::up_held() ? 64 : 0) | (bn::keypad::down_held() ? 128 : 0) | (bn::keypad::r_held() ? 256 : 0) |
                            (bn::keypad::l_held() ? 512 : 0));
        }

        void push_keys(uint16_t keys)
        {
            ++vis.frame;

            if(ring_count > 0)
            {
                uint16_t& last = ring[(ring_head + ring_count - 1) % log_capacity];

                if((last & 0x3FF) == keys && (last >> 10) < 63)
                {
                    last = uint16_t(last + (1 << 10));
                    return;
                }
            }

            if(ring_count == log_capacity)
            {
                ring_first_frame += uint32_t(ring[ring_head] >> 10) + 1;
                ring_head = (ring_head + 1) % log_capacity;
                --ring_count;
            }

            ring[(ring_head + ring_count) % log_capacity] = keys;
            ++ring_count;
        }

        void write_header()
        {
            header.checksum = checksum_bytes(&header, int(offsetof(region_header, checksum)));
            bn::sram::write_offset(header, region_offset);
        }

        void load_header()
        {
            bn::sram::read_offset(header, region_offset);

            if(header.magic == region_magic && header.version == format_version && header.slots == slot_count &&
               header.checksum == checksum_bytes(&header, int(offsetof(region_header, checksum))))
            {
                return;
            }

            // empty or damaged: start fresh
            __builtin_memset(&header, 0, sizeof(header));
            header.magic = region_magic;
            header.version = format_version;
            header.slots = slot_count;
            header.next_number = 1;
            write_header();
        }

        [[nodiscard]] int slot_offset(int index)
        {
            return region_offset + int(sizeof(region_header)) + index * int(sizeof(report));
        }

        void take_snapshot(bool calm)
        {
            if(! src || ! src->snapshot)
            {
                return;
            }

            // overwrite the older slot (an invalid one first)
            int target = 0;

            if(slots_raw[0].get().valid && slots_raw[1].get().valid)
            {
                target = slots_raw[0].get().frame <= slots_raw[1].get().frame ? 0 : 1;
            }
            else if(slots_raw[0].get().valid)
            {
                target = 1;
            }

            snapshot_slot& slot = slots_raw[target].get();
            new (&slot.data) save_data();       // constructed in place (a temporary would sit on the small stack)

            if(! src->snapshot(slot.data, slot.rng))
            {
                return;
            }

            save_finalize(slot.data);
            slot.frame = vis.frame;
            slot.valid = true;
            slot.calm = calm;
            ++vis.snapshots;
            next_snapshot = vis.frame + snapshot_period;
        }

        // ---------------------------------------------------------------- the report panel

        constexpr int panel_w = 164;
        constexpr int panel_x = (240 - panel_w) / 2;
        constexpr int panel_top = 3;
        constexpr int row_pitch = 14;
        constexpr uint32_t need_tiles = 400;
        constexpr uint32_t need_items = 40;

        void wait_released()
        {
            for(int frame = 0; frame < 90 && bn::keypad::any_held(); ++frame)
            {
                bn::core::update();
            }
        }

        constexpr const char* category_names[category_count + 1] =
        {
            "Game froze / stuck", "Graphics glitch", "Text problem", "Can't do objective", "Other", "Cancel"
        };

        // Returns 1..5 for a category, 0 for cancel.
        [[nodiscard]] int run_panel()
        {
            ui::panel panel;
            ui::bar bar;
            ui::label title;
            ui::label rows[category_count + 1];
            int selected = 0;
            int height = 17 + 3 + (category_count + 1) * row_pitch + 3 + 4;
            int rows_y = panel_top + 17 + 3;

            auto draw = [&]()
            {
                for(int index = 0; index <= category_count; ++index)
                {
                    rows[index].set(ui::font9, panel_x + 8 + 12, rows_y + index * row_pitch + 10, category_names[index],
                                    index == selected ? ui::role::selected : ui::role::text);
                }

                bar.set(panel_x + 8, rows_y + selected * row_pitch, panel_w - 16);
            };

            panel.open(panel_x, panel_top, panel_w, height, true);
            title.set(ui::font9, panel_x + 7, panel_top + 12, "Report a bug", ui::role::title);
            draw();
            bn::core::update();
            vis.panel_tiles = uint32_t(bn::sprite_tiles::available_tiles_count());
            vis.panel_items = uint32_t(bn::sprites::available_items_count());
            int result = 0;

            while(true)
            {
                if(bn::keypad::up_pressed() && selected > 0)
                {
                    --selected;
                    draw();
                }
                else if(bn::keypad::down_pressed() && selected < category_count)
                {
                    ++selected;
                    draw();
                }

                if(bn::keypad::a_pressed())
                {
                    result = selected < category_count ? selected + 1 : 0;
                    break;
                }

                if(bn::keypad::b_pressed())
                {
                    break;
                }

                bn::core::update();
            }

            bar.clear();
            title.clear();

            for(ui::label& label : rows)
            {
                label.clear();
            }

            panel.close();
            bn::core::update();
            return result;
        }

        void run_message(const bn::string_view& first, const bn::string_view& second)
        {
            static constexpr bn::string_view ok[] = { "OK" };
            bn::string_view lines[2] = { first, second };
            dialog box;
            box.open("Report a bug", lines, 2, ok, 1);
            bn::core::update();

            while(box.update() == dialog::open_still)
            {
                bn::core::update();
            }

            bn::core::update();
        }

        // ---------------------------------------------------------------- writing the report

        [[nodiscard]] int pick_slot()
        {
            int best = -1;

            for(int index = 0; index < 2; ++index)
            {
                const snapshot_slot& slot = slots_raw[index].get();

                // usable only if the log still covers every frame since the snapshot
                if(slot.valid && slot.frame >= ring_first_frame && (best < 0 || slot.frame < slots_raw[best].get().frame))
                {
                    best = index;
                }
            }

            return best;
        }

        uint32_t write_report(int category)
        {
            report& r = work_raw.get();
            __builtin_memset(static_cast<void*>(&r), 0, sizeof(report));
            r.magic = report_magic;
            r.version = format_version;
            r.size = sizeof(report);
            r.number = header.next_number;
            r.category = uint8_t(category);
            r.frame_now = vis.frame;
            r.marker_count = uint8_t(marker_total < marker_capacity ? marker_total : marker_capacity);

            for(int index = 0; index < r.marker_count; ++index)
            {
                r.markers[index] = markers[(marker_total - r.marker_count + index) % marker_capacity];
            }

            const char* build = __DATE__ " " __TIME__;

            for(int index = 0; index < 31 && build[index]; ++index)
            {
                r.build[index] = build[index];
            }

            r.map = uint8_t(vis.live[0]);
            r.x = int16_t(vis.live[1]);
            r.y = int16_t(vis.live[2]);
            r.day = uint16_t(vis.live[3]);
            r.minutes = uint16_t(vis.live[4]);
            r.money = int32_t(vis.live[5]);

            if(! src)
            {
                r.flags |= 4;       // no field right now: a minigame
            }

            int slot_index = pick_slot();
            r.snap_frame = vis.frame;

            if(slot_index >= 0)
            {
                const snapshot_slot& slot = slots_raw[slot_index].get();
                r.flags |= 1;
                r.flags |= slot.calm ? 0 : 2;
                r.snap_frame = slot.frame;
                r.snap = slot.data;
                r.rng[0] = slot.rng[0];
                r.rng[1] = slot.rng[1];
                r.rng[2] = slot.rng[2];
                r.log_frames = vis.frame - slot.frame;

                // copy the log entries that cover [slot.frame, vis.frame)
                uint32_t frame = ring_first_frame;

                for(int index = 0; index < ring_count; ++index)
                {
                    uint16_t entry = ring[(ring_head + index) % log_capacity];
                    uint32_t length = uint32_t(entry >> 10) + 1;
                    uint32_t end = frame + length;

                    if(end > slot.frame)
                    {
                        uint32_t kept = end - (frame > slot.frame ? frame : slot.frame);
                        r.log[r.log_entries++] = uint16_t((entry & 0x3FF) | ((kept - 1) << 10));
                    }

                    frame = end;
                }
            }
            else
            {
                r.flags |= 8;
            }

            r.checksum = checksum_bytes(reinterpret_cast<const uint8_t*>(&r) + 12, int(sizeof(report)) - 12);
            bn::sram::write_offset(r, slot_offset(int((r.number - 1) % slot_count)));
            ++header.next_number;
            write_header();
            ++vis.reports;
            return r.number;
        }

        void open_reporter()
        {
            // The panel runs its own frames from inside this callback (the game is paused, nothing is recorded meanwhile).
            // Sprite budget: if the screen is too busy for the panel, an "Other" report is saved without asking.
            in_panel = true;
            vis.in_panel = 1;
            bn::core::update_callback_type saved_callback = bn::core::update_callback();
            bn::core::set_update_callback(nullptr);

            if(src && src->live)
            {
                src->live(vis.live);
            }

            markers[marker_total++ % marker_capacity] = marker{ vis.frame, 3 };
            vis.tiles_free = uint32_t(bn::sprite_tiles::available_tiles_count());
            vis.items_free = uint32_t(bn::sprites::available_items_count());
            // measured: the panel needs about 420 sprite tiles and 40 sprites (docs/bug_reports.md); the confirmation dialog is bigger
            // in width but about the same. A busy screen (pause menu, dialogue) is cleared by the field first if it can.
            if((vis.tiles_free < need_tiles || vis.items_free < need_items) && src && src->make_room)
            {
                src->make_room();
                bn::core::update();
                vis.tiles_free = uint32_t(bn::sprite_tiles::available_tiles_count());
                vis.items_free = uint32_t(bn::sprites::available_items_count());
            }

            bool room = vis.tiles_free >= need_tiles && vis.items_free >= need_items;
            int category = room ? run_panel() : 5;

            if(category != 0)
            {
                uint32_t number = write_report(category);

                char text[32] = "Bug report saved (#";
                int length = 19;
                char digits[12];
                int count = 0;

                for(uint32_t value = number; value > 0 && count < 10; value /= 10)
                {
                    digits[count++] = char('0' + value % 10);
                }

                while(count > 0)
                {
                    text[length++] = digits[--count];
                }

                text[length++] = ')';
                text[length++] = '.';
                text[length] = 0;

                if(room)
                {
                    run_message(text, "Thanks!");
                }
                else
                {
                    // no room for the panel (minigame, busy dialogue): the report was filed as "Other"; a one-line note for 2 s
                    ui::label note;
                    note.set(ui::font9, 4, 12, bn::string_view(text, length - 1), ui::role::hud_clock);

                    for(int frame = 0; frame < 120; ++frame)
                    {
                        bn::core::update();
                    }

                    note.clear();
                    bn::core::update();
                }
            }

            wait_released();
            last_report_frame = vis.frame;
            vis.in_panel = 0;
            in_panel = false;
            bn::core::set_update_callback(saved_callback);
        }

        void on_update()
        {
            if(! enabled || in_panel)
            {
                return;
            }

            push_keys(read_keys());

            if(src && src->live)
            {
                src->live(vis.live);
            }

            if(src && vis.frame >= next_snapshot)
            {
                bool calm = src->calm && src->calm();

                if(calm || vis.frame >= next_snapshot + snapshot_patience)
                {
                    take_snapshot(calm);
                }
            }

#ifndef TL_DEBUG_TELEPORT
            // L+R together (edge: the second key goes down while the first is held, or both in the same frame)
            if(bn::keypad::l_held() && bn::keypad::r_held() && (bn::keypad::l_pressed() || bn::keypad::r_pressed()) &&
               vis.frame - last_report_frame > 30)
            {
                open_reporter();
            }
#endif
        }
    }

    void init()
    {
        __builtin_memset(&vis, 0, sizeof(vis));
        __builtin_memset(slots_raw, 0, sizeof(slots_raw));
        __builtin_memset(ring, 0, sizeof(ring));
        __builtin_memset(markers, 0, sizeof(markers));
        vis.magic = ram_magic;
        load_header();
        bn::core::set_update_callback(on_update);
    }

    void start(const source* source_in)
    {
        src = source_in;
        enabled = true;
        vis.active = 1;
        take_snapshot(true);
    }

    void set_source(const source* source_in)
    {
        src = source_in;
    }

    void note_scene(uint32_t kind)
    {
        markers[marker_total++ % marker_capacity] = marker{ vis.frame, kind };
    }

    void force_snapshot()
    {
        // the scene was rebuilt: replays can only start from here on
        slots_raw[0].get().valid = false;
        slots_raw[1].get().valid = false;
        take_snapshot(true);
    }

    bool take_replay(uint32_t rng_out[3])
    {
        if(header.replay_flag != 1)
        {
            return false;
        }

        rng_out[0] = header.replay_rng[0];
        rng_out[1] = header.replay_rng[1];
        rng_out[2] = header.replay_rng[2];
        header.replay_flag = 0;
        write_header();
        return true;
    }
}
