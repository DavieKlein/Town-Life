#include "tl_field.h"

#include "tl_story.h"
#include "tl_story_ids.h"

// Old Block (s75): gated solids driven by story flags and the small interactable kinds of that district.
namespace tl
{
    namespace
    {
        struct sign_text
        {
            const char* title;
            const char* a;
            const char* b;
            const char* c;
        };

        // `sign` interactables use quality as the index into this table (tools/interactions.py)
        constexpr sign_text sign_texts[] = {
            { "Barrier", "SURVEY IN PROGRESS.", "VaultLink HyperFibre.", "Keep out." },
            { "Old Block", "OLD BLOCK - EST. 1931.", "Half covered by", "VaultTech posters." },
            { "Site gate", "NOTICE: this site is", "scheduled for", "redevelopment." },
            { "Notice", "Smart City is coming.", "Old Block will be", "modernised." },
            { "Poster wall", "Mia's flyers: SAVE", "THE CO-OP. Come to", "the meeting." },
            { "Bulletin", "Lost: one sock.", "Found: one sock.", "Ask Ines." },
        };
    }

    void field::_update_gates()
    {
        // s77: the sneak route is the sewer (tl_field_sewer.cpp). It opens with the flag sneak_route; until the Old Block missions
        // exist the sandbox mission X1 "Explore the city" sets that flag, so the district can be visited.
        if(story().mission() == mission_id::X1 && ! story().flag(story_flag::sneak_route))
        {
            story().set_flag(story_flag::sneak_route, 1);
        }

        gate_open[int(gate_id::barrier)] = story().flag(story_flag::barrier_moved) != 0;
        gate_open[int(gate_id::bridge)] = story().flag(story_flag::door_bridge) != 0;
    }

    void field::_use_old_block(const interactable& target)
    {
        auto begin = [this](int frames, player::action_kind anim, const interactable& at)
        {
            _begin_activity(frames);
            _player.approach(at.x, at.y, 14);
            _player.start_action(anim, at.x, at.y, _act.frames);
        };

        switch(target.kind)
        {
        case interactable_kind::sign:
            {
                const sign_text& t = sign_texts[target.quality % int(sizeof(sign_texts) / sizeof(sign_text))];
                _show_info(t.title, t.a, t.b, t.c);
            }
            break;

        case interactable_kind::flap:
            _show_info("Fence", "Just a fence.", "And a lot of bushes.", "");
            break;

        case interactable_kind::hatch:
            _show_info("Steel hatch", "NODE 7. It hums.", "It is warm. Warmer", "than the street.");
            break;

        case interactable_kind::oven:
            _show_info("Oven", "The bakery oven glows.", "It smells wonderful.", "");
            _act = activity_state();
            _needs.add(needs::fun, 2);
            break;

        case interactable_kind::chess:
            begin(240, player::action_kind::read, target);
            _act.gain[needs::fun] = 6;
            break;

        case interactable_kind::garden:
            begin(210, player::action_kind::search, target);
            _act.gain[needs::fun] = 4;
            _act.gain[needs::hygiene] = -3;
            break;

        case interactable_kind::hoop:
            begin(240, player::action_kind::pickup, target);
            _act.gain[needs::fun] = 8;
            _act.gain[needs::energy] = -4;
            _act.gain[needs::hygiene] = -3;
            break;

        case interactable_kind::washer:
            if(_money < 2)
            {
                _show_info("Washing machine", "Wash your clothes", "for $2.", "Not enough money.");
            }
            else
            {
                _money -= 2;
                _redraw_hud_text();
                begin(180, player::action_kind::wash, target);
                _act.gain[needs::hygiene] = 20;
            }
            break;

        default:
            break;
        }
    }
}
