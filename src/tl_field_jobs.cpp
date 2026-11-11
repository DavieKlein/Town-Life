// s71: odd jobs from the community-centre notice board, the "Feeling great" state and the on-screen toast.
// Design numbers: docs/reference_sims_handhelds.md recommendations 1 and 2, CLAUDE.md "s71".
#include "tl_field.h"

#include "bn_keypad.h"
#include "bn_string.h"
#include "tl_story_ids.h"

namespace tl
{
    namespace
    {
        // Odd jobs: base pay in dollars (a "Feeling great" player gets +10 %, rounded up), once per day each.
        constexpr int flyers_pay = 5;       // walk to three places in the City Centre
        constexpr int books_pay = 4;        // 5 s of sorting library books at the board shelves
        constexpr int crates_pay = 6;       // Lou's crates: take the job at the board, then ask Lou at the diner

        constexpr int bit_flyers_done = 1;
        constexpr int bit_books_done = 2;
        constexpr int bit_crates_done = 4;
        constexpr int bit_crates_taken = 8;
        constexpr int bit_flyers_taken = 16;
        constexpr int bit_spot0 = 32;       // 32, 64, 128: flyer spots visited

        constexpr int flyer_reach = 26;     // world units

        struct flyer_spot
        {
            int x;          // cells x 16
            int y;
        };

        // Bus stop (newspaper boxes), fountain square (under a bench), City Park (beside the bench): all free floor cells.
        constexpr flyer_spot flyer_spots[3] = { { 755, 530 }, { 803, 600 }, { 214, 640 } };

        constexpr int books_frames = 300;
        constexpr int crates_frames = 420;

        int count_spots(int mask)
        {
            int count = 0;

            for(int k = 0; k < 3; ++k)
            {
                count += (mask & (bit_spot0 << k)) ? 1 : 0;
            }

            return count;
        }
    }

    int field::_job_pay(int base) const
    {
        return _great ? (base * 11 + 9) / 10 : base;
    }

    void field::_odd_refresh()
    {
        if(_odd_day != (_day & 255))
        {
            _odd_day = uint8_t(_day & 255);
            _odd_mask = 0;
        }
    }

    // ---------------------------------------------------------------------------------------------------- toast
    void field::_toast(const char* text)
    {
        _toast_text = text;
        _toast_wait = true;
    }

    void field::_toast_clear()
    {
        _toast_label.clear();
        _toast_frames = 0;
        _toast_wait = false;
    }

    void field::_update_toast()
    {
        if(_toast_frames > 0)
        {
            if(--_toast_frames == 0)
            {
                _toast_label.clear();
            }
        }
        else if(_toast_wait && ! _menu.is_open() && ! _conversation.active() && ! _act.active)
        {
            _toast_wait = false;
            _toast_label.set_centre(ui::font9, 120, 30, _toast_text, ui::role::hud_money);
            _toast_frames = 170;
        }
    }

    // ---------------------------------------------------------------------------------------------------- Feeling great
    void field::_update_great(bool announce)
    {
        bool great = _needs.all_at_least(_great ? needs::great_exit : needs::great_enter);

        if(great != _great)
        {
            _great = great;
            story().set_great(great);

            if(great && announce)
            {
                _toast("Feeling great! Pay +10%");
            }
        }
    }

    // ---------------------------------------------------------------------------------------------------- notice board
    void field::_open_board(const interactable& target)
    {
        _odd_refresh();
        static bn::string<24> labels[4];
        static bn::string_view options[4];
        static constexpr const char* names[3] = { "Flyers", "Sort books", "Lou's crates" };
        static constexpr int pays[3] = { flyers_pay, books_pay, crates_pay };
        static constexpr int dones[3] = { bit_flyers_done, bit_books_done, bit_crates_done };

        for(int index = 0; index < 3; ++index)
        {
            labels[index] = names[index];

            if(_odd_mask & dones[index])
            {
                labels[index].append(" (done)");
            }
            else
            {
                labels[index].append(" $");
                labels[index].append(bn::to_string<4>(_job_pay(pays[index])));
            }

            options[index] = labels[index];
        }

        labels[3] = "Leave";
        options[3] = labels[3];
        _menu_target = &target;
        _menu_mode = menu_mode::board;
        _menu.open("Odd jobs", options, 4);
    }

    void field::_board_choice(int choice)
    {
        _odd_refresh();

        if(choice == 0)
        {
            if(_odd_mask & bit_flyers_done)
            {
                _show_info("Flyers", "All handed out today.", "Back tomorrow!", "");
            }
            else if(_odd_mask & bit_flyers_taken)
            {
                _show_info("Flyers", "Hand them out at the", "bus stop, the fountain", "and the park.");
            }
            else
            {
                _odd_mask |= bit_flyers_taken;
                _show_info("Flyers", "Take a stack. Walk to", "the bus stop, fountain", "and the park.");
                _sync_objective();
            }
        }
        else if(choice == 1)
        {
            if(_odd_mask & bit_books_done)
            {
                _show_info("Library books", "All sorted for today.", "Back tomorrow!", "");
            }
            else if(_needs.values[needs::energy] < 15)
            {
                _show_info("Library books", "You are too tired.", "Rest first.", "");
            }
            else
            {
                int pay = _job_pay(books_pay);
                _begin_activity(books_frames);
                _act.gain[needs::energy] = -4;
                _act.gain[needs::hygiene] = -2;
                _act.gain[needs::fun] = -3;
                _act.money = pay;
                _act.odd_bit = bit_books_done;
                _act.message = true;
                _act.title = "Library books";
                _info_line_a = "Books sorted!";
                _info_line_b = "The librarian pays";
                _info_line_c = "$";
                _info_line_c.append(bn::to_string<4>(pay));
                _info_line_c.append(".");
                _player.start_action(player::action_kind::search, 169, 16, _act.frames);
            }
        }
        else if(choice == 2)
        {
            if(_odd_mask & bit_crates_done)
            {
                _show_info("Lou's crates", "Lou has everything", "he needs today.", "");
            }
            else if(_odd_mask & bit_crates_taken)
            {
                _show_info("Lou's crates", "Ask Lou at the diner:", "\"Carry the crates\".", "");
            }
            else
            {
                _odd_mask |= bit_crates_taken;
                _show_info("Lou's crates", "Lou needs hands at", "the diner. Talk to him.", "");
                _sync_objective();
            }
        }
    }

    // Hand out flyers: walking close to each of the three places counts one.
    void field::_update_flyers()
    {
        if(_map_id != map_id::city_centre || ! (_odd_mask & bit_flyers_taken) || (_odd_mask & bit_flyers_done) ||
           _player.current_activity() != player::activity::walking)
        {
            return;
        }

        for(int index = 0; index < 3; ++index)
        {
            int bit = bit_spot0 << index;

            if(_odd_mask & bit)
            {
                continue;
            }

            int dx = _player.x() - flyer_spots[index].x;
            int dy = _player.y() - flyer_spots[index].y;

            if(dx * dx + dy * dy > flyer_reach * flyer_reach)
            {
                continue;
            }

            _odd_mask |= uint8_t(bit);
            int count = count_spots(_odd_mask);

            if(count >= 3)
            {
                int pay = _job_pay(flyers_pay);
                _odd_mask = uint8_t((_odd_mask & (bit_crates_taken | bit_books_done | bit_crates_done)) | bit_flyers_done);
                _money += pay;
                _needs.add(needs::energy, -6);
                _needs.add(needs::hygiene, -3);
                _needs.add(needs::fun, -2);
                bn::string<32> text("Flyers done! +$");
                text.append(bn::to_string<4>(pay));
                _toast(text.c_str());
                _redraw_hud_text();
                _update_bars();
            }
            else
            {
                bn::string<32> text("Flyer ");
                text.append(bn::to_string<4>(count));
                text.append("/3 handed out");
                _toast(text.c_str());
            }

            _sync_objective();
            return;
        }
    }

    // Lou's crates (after "Carry the crates" in his conversation): a timed haul behind the diner counter.
    void field::_start_crates()
    {
        _odd_refresh();

        if(_odd_mask & bit_crates_done)
        {
            return;
        }

        int pay = _job_pay(crates_pay);
        _begin_activity(crates_frames);
        _act.gain[needs::energy] = -8;
        _act.gain[needs::hygiene] = -4;
        _act.gain[needs::hunger] = -3;
        _act.gain[needs::fun] = -3;
        _act.money = pay;
        _act.odd_bit = bit_crates_done;
        _act.message = true;
        _act.title = "Lou's crates";
        _info_line_a = "Twelve crates stacked.";
        _info_line_b = "Lou pays $";
        _info_line_b.append(bn::to_string<4>(pay));
        _info_line_b.append(".");
        _info_line_c = "";
        _player.start_action(player::action_kind::pickup, 102, 42, _act.frames);
    }

    // Objective line while an odd job is open (used by _sync_objective_dynamic).
    bool field::_odd_objective()
    {
        _odd_refresh();

        if((_odd_mask & bit_flyers_taken) && ! (_odd_mask & bit_flyers_done))
        {
            _objective = "Flyers ";
            _objective.append(bn::to_string<4>(count_spots(_odd_mask)));
            _objective.append("/3: bus stop, fountain, park");
            return true;
        }

        if((_odd_mask & bit_crates_taken) && ! (_odd_mask & bit_crates_done))
        {
            _objective = "Ask Lou about the crates (diner)";
            return true;
        }

        return false;
    }

    bool field::_crates_open() const
    {
        return (_odd_day == (_day & 255)) && (_odd_mask & bit_crates_taken) && ! (_odd_mask & bit_crates_done);
    }
}
