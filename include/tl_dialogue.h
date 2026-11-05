#ifndef TL_DIALOGUE_H
#define TL_DIALOGUE_H

#include "bn_vector.h"
#include "bn_random.h"
#include "bn_string.h"
#include "bn_optional.h"
#include "bn_sprite_ptr.h"
#include "bn_string_view.h"

#include "tl_ui.h"
#include "tl_story.h"
#include "tl_portrait.h"

namespace tl
{
    // The dialogue box (owner-approved s55 layouts, Paper by day / Night at night):
    //  layout 1 (normal talk): the speaker's 128 px portrait stands at the bottom left in front of a 50 px box, the gold name tag and
    //    four lines of text (typed out; A completes the page, then goes on) to its right, the friendship meter at the right edge,
    //    a blinking A button when the page is complete.
    //  layout 2 (choices): the NPC's 96 px portrait, mirrored, at the lower right, a tall meter, the last page as the question and
    //    the options as highlight rows on the left.
    //  system pages (no portrait): the old 40 px box with three lines.
    // Portraits have five expressions (expression enum in tl_portrait.h) chosen per page.
    class dialogue_box
    {

    public:
        // text areas per layout
        static constexpr int text_x = 116;          // layout 1
        static constexpr int text_width = 104;
        static constexpr int plain_text_x = 14;     // no portrait (system pages, speakers without one)
        static constexpr int plain_text_width = 196;

        // speaker: npc_id, speaker_player or speaker_system (no portrait, no name tag). partner = the NPC shown in the choice layout.
        void open(int speaker, bool show_meter, int friendship, int partner = -1);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return _open;
        }

        // Changes the speaker (portrait, expression, name tag); returns to layout 1 from the choice layout.
        void set_speaker(int speaker, int expr = 0);

        // Changes only the expression of the current portrait.
        void set_expression(int expr);

        // Shows a text (the {NAME} placeholder is replaced) and types it out.
        void say(const char* text);

        // Returns true when the player has gone past the last page of the text.
        [[nodiscard]] bool update_text();

        // Choices (2-4 options, the strings must stay valid while shown): switches to layout 2. update_choice() returns the index or -1.
        void choose(const bn::string_view* options, int count);
        [[nodiscard]] int update_choice();

        [[nodiscard]] bool choosing() const
        {
            return _choosing;
        }

        // The meter moves to the new friendship value (about 3 frames per point) and shows the change next to it.
        void set_friendship(int value);
        void update_meter();

        [[nodiscard]] bool page_complete() const
        {
            return _shown >= _total;
        }

    private:
        enum class layout : uint8_t
        {
            none,
            plain,
            one,
            two
        };

        ui::panel _panel;
        ui::label _lines[4];
        ui::label _question[3];
        ui::label _tag_label;
        ui::label _meter_label;
        ui::label _delta_label;
        bn::vector<bn::sprite_ptr, 8> _tag_sprites;
        bn::vector<bn::sprite_ptr, 4> _pic;
        bn::vector<bn::sprite_ptr, 3> _tall;
        bn::optional<bn::sprite_ptr> _meter;
        bn::optional<bn::sprite_ptr> _a_icon;
        bn::string<64> _line_text[4];
        bn::string<224> _text;
        bn::string<224> _last_page;
        layout _layout = layout::none;
        int _max_lines = 3;
        int _line_count = 0;
        int _pos = 0;
        int _shown = 0;
        int _total = 0;
        int _drawn[4] = { -1, -1, -1, -1 };
        int _blink = 0;
        int _speaker = -1;
        int _partner = -1;
        int _expr = 0;
        int _text_x = plain_text_x;
        int _text_w = plain_text_width;
        bool _open = false;
        bool _with_meter = false;
        bool _choosing = false;
        int _meter_value = 0;           // number shown
        int _meter_target = 0;
        int _meter_frame = -1;
        int _meter_delay = 0;
        int _delta_timer = 0;
        int _tall_frames[3] = { -1, -1, -1 };

        // choices
        ui::bar _choice_bar;
        bn::vector<ui::label, 4> _choice_labels;
        const bn::string_view* _options = nullptr;
        int _options_count = 0;
        int _selected = 0;
        int _rows_top = 0;

        bool _next_page();
        void _draw_lines(bool force);
        void _draw_choices();
        void _draw_meter();
        void _build_tag(int x, int y);
        void _build_layout(layout l, int speaker, int partner_height = 0);
        void _build_portrait(int speaker, bool small);
        void _build_meter(bool tall);
    };

    // Plays dialogue nodes and runs small talk with an NPC on a dialogue_box, applying the story effects.
    class conversation
    {

    public:
        // Small talk with an NPC (greeting, topics, friendship moves). The first talk ever plays the NPC's intro node first.
        void start_talk(int npc, int day, int minutes);

        // Plays a script from a dialogue node (speaker pages, choices, effects).
        void start_script(int node, int npc = -1);

        // A one-page system message (no portrait), e.g. "Mission complete". The text is copied.
        void start_message(const char* text);

        [[nodiscard]] bool is_message() const
        {
            return _message;
        }

        [[nodiscard]] bool active() const
        {
            return _step != step::idle;
        }

        // The NPC the finished conversation was with (-1 for scripts without a partner); valid until the next start.
        [[nodiscard]] int partner() const
        {
            return _npc;
        }

        // Call once per frame while active; returns true on the frame the conversation ends.
        [[nodiscard]] bool update();

        [[nodiscard]] dialogue_box& box()
        {
            return _box;
        }

    private:
        enum class step
        {
            idle,
            page,               // a page is being shown
            choice,             // choices of a page
            topic_menu,         // small talk: pick a topic
            gift_pick,          // small talk: pick a gift to give
            end
        };

        enum class phase
        {
            script,             // a plain script (or the intro of small talk)
            greeting,
            opener,             // the player's line
            answer,             // the NPC's answer
            leave,              // farewell
            coins,
            gift_ask,           // "Which gift?"
            gift_react,         // the NPC's reaction to a gift
            tail
        };

        dialogue_box _box;
        bn::random _rng;
        bn::string<24> _topic_labels[4];
        bn::string_view _topic_views[4];
        int _topic_ids[3] = {};
        step _step = step::idle;
        phase _phase = phase::script;
        bool _small_talk = false;
        bool _message = false;
        int _npc = -1;
        int _node = -1;
        int _day = 1;
        int _minutes = 0;
        int _topics_done = 0;
        int _dislikes = 0;
        int _topic = 0;
        int _used_mask = 0;
        int _menu_topics = 0;
        int _story_node = -1;
        int _pending_leave = 0;     // 0 = continue, 1 = enough, 2 = annoyed
        bool _first_today = false;
        bool _after_script_talk = false;
        int _coin_node = -1;
        int _story_row = -1;        // option index of the story question in the topic menu (-1 = none)
        int _gift_row = -1;         // option index of "Give a gift" (-1 = not offered)
        int _gift_page = 0;
        int _gift_ids[3] = {};
        int _gift_shown = 0;
        bool _gossip_done = false;
        bn::string<24> _gift_labels[4];
        bn::string_view _gift_views[4];
        int _answer_expr = -1;      // expression of the NPC's answer page (set from the topic result)

        void _show_node(int node);
        void _apply_effects(const dlg_node& node);
        void _apply_choice_effects(const dlg_choice& choice);
        void _after_page();
        void _start_greeting();
        void _open_topic_menu();
        void _open_gift_menu();
        void _give_gift(int gift);
        [[nodiscard]] bool _try_gossip();
        void _begin_topic(int topic);
        void _begin_answer();
        void _finish_small_talk();
        [[nodiscard]] int _resolve_speaker(int speaker) const;
        void _end();
    };
}

#endif
