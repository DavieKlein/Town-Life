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

namespace tl
{
    // The dialogue box (approved design "variant 2", Paper by day / Night at night): a 40 px box at the bottom of the screen,
    // the speaker's 64x64 portrait standing on it at the left, a name tag above the box, three lines of text typed out one
    // character at a time (A completes the page, then goes on; B does the same), a blinking A button when the page is
    // complete, an optional choice list above the box and the vertical friendship meter (red at the bottom, green at the
    // top, with its number) at the right edge. Long texts are word-wrapped and split into pages of three lines.
    class dialogue_box
    {

    public:
        static constexpr int text_x = 76;           // with a portrait
        static constexpr int text_width = 140;      // pixels per line
        static constexpr int system_text_x = 14;    // system pages (no portrait)
        static constexpr int system_text_width = 196;

        // speaker: npc_id, speaker_player or speaker_system (no portrait, no name tag).
        void open(int speaker, bool show_meter, int friendship);
        void close();

        [[nodiscard]] bool is_open() const
        {
            return _open;
        }

        // Changes the speaker (portrait, name tag).
        void set_speaker(int speaker);

        // Shows a text (the {NAME} placeholder is replaced) and types it out.
        void say(const char* text);

        // Returns true when the player has gone past the last page of the text.
        [[nodiscard]] bool update_text();

        // Choices (2-4 options, the strings must stay valid while shown). update_choice() returns the index or -1.
        void choose(const bn::string_view* options, int count);
        [[nodiscard]] int update_choice();

        [[nodiscard]] bool choosing() const
        {
            return _choice_panel.is_open();
        }

        // The meter moves to the new friendship value (about 3 frames per point) and shows the change next to it.
        void set_friendship(int value);
        void update_meter();

        [[nodiscard]] bool page_complete() const
        {
            return _shown >= _total;
        }

    private:
        ui::panel _panel;
        ui::label _lines[3];
        ui::label _tag_label;
        ui::label _meter_label;
        ui::label _delta_label;
        bn::vector<bn::sprite_ptr, 8> _tag_sprites;
        bn::optional<bn::sprite_ptr> _portrait;
        bn::optional<bn::sprite_ptr> _meter;
        bn::optional<bn::sprite_ptr> _a_icon;
        bn::string<64> _line_text[3];
        bn::string<224> _text;
        int _line_count = 0;
        int _pos = 0;
        int _shown = 0;
        int _total = 0;
        int _drawn[3] = { -1, -1, -1 };
        int _blink = 0;
        int _speaker = -1;
        int _text_x = text_x;
        int _text_w = text_width;
        bool _open = false;
        bool _with_meter = false;
        int _meter_value = 0;           // number shown
        int _meter_target = 0;
        int _meter_frame = -1;
        int _meter_delay = 0;
        int _delta_timer = 0;

        // choices
        ui::panel _choice_panel;
        ui::bar _choice_bar;
        bn::vector<ui::label, 4> _choice_labels;
        const bn::string_view* _options = nullptr;
        int _options_count = 0;
        int _selected = 0;

        bool _next_page();
        void _draw_lines(bool force);
        void _draw_choices();
        void _draw_meter();
        void _build_tag();
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
        int _pending_leave = 0;     // 0 = continue, 1 = enough, 2 = annoyed
        bool _first_today = false;
        bool _after_script_talk = false;
        int _coin_node = -1;

        void _show_node(int node);
        void _apply_effects(const dlg_node& node);
        void _apply_choice_effects(const dlg_choice& choice);
        void _after_page();
        void _start_greeting();
        void _open_topic_menu();
        void _begin_topic(int topic);
        void _begin_answer();
        void _finish_small_talk();
        [[nodiscard]] int _resolve_speaker(int speaker) const;
        void _end();
    };
}

#endif
