#!/usr/bin/env python3
"""
Town Life - story data compiler: dialogue (tools/dialogue_src.txt), story flags, missions and NPC talk profiles
-> include/tl_story_ids.h (constants) and src/tl_story_data.cpp (tables). Run by build_assets.py, or alone:
  python3 tools/story_data.py

The format of dialogue_src.txt is documented at the top of that file; flags / missions / NPC profiles are plain Python below.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cast  # noqa: E402

# ---------------------------------------------------------------------------------------------------- speakers
SPEAKER_IDS = {"MIA": "mia", "ROSA": "rosa", "DEX": "dex", "PIMM": "pimm", "LOU": "lou", "HALLORAN": "halloran",
               "DEXV": "dex_vault", "VICTOR": "victor", "VALET": "robot", "OKAFOR": "okafor"}
SP_PLAYER, SP_NPC, SP_SYSTEM = 253, 252, 254

TOPICS = ["weather", "work", "music", "sports", "gossip", "compliment", "joke", "complain"]
TOPIC_LABELS = ["Weather", "Work", "Music", "Sports", "Gossip", "Compliment", "Joke", "Complain"]
# what the player says (docs/story_chapter1.md 5.6)
TOPIC_OPENERS = ["Nice weather today.", "How's work going?", "Heard any good music?", "Did you see the game?",
                 "Heard anything juicy?", "You look great today.", "Want to hear a joke?", "Can I complain a bit?"]

# ---------------------------------------------------------------------------------------------------- NPC talk profiles
# id: (display name, base mood: neutral|good|grumpy, likes per topic: L like / N neutral / D dislike, start friendship)
NPC_INFO = {
    "mia": ("Mia", "neutral", "NDLNLDLN", 40, "NFDLN"),
    "rosa": ("Rosa", "neutral", "NLLDNLND", 30, "FLDLN"),
    "dex": ("Dex", "neutral", "NLDLNLND", 5, "NLLFN"),
    "pimm": ("Mr. Pimm", "neutral", "LLNNDNLD", 25, "LNDLF"),
    "lou": ("Big Lou", "neutral", "NLNLLNND", 0, "NLFLD"),
    "halloran": ("Halloran", "neutral", "LLNLDDND", 0, "NNNNN"),
    "dex_vault": ("Dex", "neutral", "NLDLNLND", 0, "NNNNN"),
    "victor": ("Victor Vault", "neutral", "NNNNNNNN", 0, "NNNNN"),
    "robot": ("Valet", "neutral", "NNNNNNNN", 0, "NNNNN"),
    "okafor": ("Dr. Okafor", "neutral", "LLNNDNLD", 0, "LLNFN"),
}
# Gifts (docs/features_backlog.md): name, price. The NPC string above has one letter per gift in this order:
# F favourite (+10 friendship), L likes (+4), N neutral (+1), D dislikes (-3). One gift per NPC and day.
GIFTS = [("Flowers", 3), ("Chocolate", 2), ("Hot sauce", 2), ("Cookies", 2), ("Newspaper", 1)]
# Gossip: what the player said or did is remembered and told to somebody else, one game day later.
# (id, trigger, hearer, dialogue node): trigger = ("topic", npc, topic) after that small-talk topic, or ("gift", npc, gift index)
GOSSIP = [
    ("complain_mia", ("topic", "mia", "complain"), "lou", "gossip_complain_mia"),
    ("compliment_mia", ("topic", "mia", "compliment"), "rosa", "gossip_compliment_mia"),
    ("joke_lou", ("topic", "lou", "joke"), "mia", "gossip_joke_lou"),
    ("gossip_pimm", ("topic", "pimm", "gossip"), "rosa", "gossip_gossip_pimm"),
    ("flowers_rosa", ("gift", "rosa", "Flowers"), "mia", "gossip_flowers_rosa"),
    ("choc_mia", ("gift", "mia", "Chocolate"), "pimm", "gossip_choc_mia"),
    ("music_rosa", ("topic", "rosa", "music"), "lou", "gossip_music_rosa"),
    ("work_lou", ("topic", "lou", "work"), "pimm", "gossip_work_lou"),
]
assert len(GOSSIP) <= 8
TALKERS = ["mia", "rosa", "dex", "pimm", "lou", "halloran", "okafor"]       # have small talk

# ---------------------------------------------------------------------------------------------------- story flags
FLAGS = ["lou_tip", "lou_asked", "met_pimm", "met_mia", "met_rosa", "met_dex", "met_lou", "met_halloran", "hint_talk_seen",
         "left_room", "shelves_stocked", "rye_delivered", "left_shop", "slept_on_bench", "read_newspaper", "diner_job",
         "odd_jobs_3", "old_block_open", "rosa_stall_done", "vaultmart_visited", "pimm_library_met", "meeting_attended",
         "certificate_found", "bridge_open", "docks_job", "first_night_off_bench", "prologue_started", "asked_lou_job",
         # prologue / Day 1-2 (cutscenes_src.txt, tl_field_script.cpp)
         "woke_up", "briefed", "stock_react_done", "pimm_scene", "has_rye", "pimm_left", "lunch_given", "vault_scene",
         "corner_market_cold", "has_coffee_voucher", "voucher_used", "ate_evening", "washed_evening", "news_due", "deposit_tip",
         "hint_hunger", "hint_hygiene", "hint_energy", "hint_bladder", "hint_fun", "lou_shift_go", "hyg_ok", "stock_rank",
         "skip_pimm", "skip_lunch", "lunch_hint", "diner_shift_day", "rosa_comforted", "vowed", "mia_goodbye", "gate_hint_seen",
         # s64: clinic
         "met_okafor", "faint_told", "sick_told", "clinic_paid",
         # s71: Lou's crates job (odd job from the community centre board)
         "crates_go",
         # s75: Old Block gates (sneak route, barrier gap after M13, Teo's door bridge)
         "sneak_route", "barrier_moved", "door_bridge"]
assert len(FLAGS) <= 80

# ---------------------------------------------------------------------------------------------------- missions
# cond: None (finished by a `done <id>` effect), ("talk", npc), ("map", map), ("money", n), ("flag", name),
#       ("day", n), ("time", day, minutes)
# The P* missions are interim ones for the sandbox (before the prologue exists); P5 ends the chain with no next mission,
# so the objective falls back to "Explore the city". Set `START_MISSION` to M01 once the prologue scenes are built.
MISSIONS = [
    ("P1", "Say hello", "Say hello to Mia.", ("talk", "mia"), "P2", 0),
    ("P2", "Find the library", "Find the library (the community centre).", ("map", "community_centre"), "P3", 0),
    ("P3", "The regular", "Talk to Mr. Pimm in the library.", ("talk", "pimm"), "P4", 0),
    ("P4", "Lunch at Lou's", "Talk to Big Lou at the diner.", ("talk", "lou"), "P5", 0),
    ("P5", "Pocket money", "Collect $30 for a rainy day.", ("money", 30), None, 0),
    ("M01", "Open Up", "Get ready for work.", ("flag", "left_room"), "M02", 0),
    ("M02", "Stock the Shelves", "Stock the shelves for Rosa.", ("flag", "shelves_stocked"), "M03", 0),
    ("M03", "The Regular", "Fetch Mr. Pimm's rye loaf (he comes at 9).", ("flag", "rye_delivered"), "M04", 0),
    ("M04", "Vault Day", "Help in the shop until lunch at noon.", ("flag", "left_shop"), "M05", 0),
    ("M05", "Survive the Night", "Eat, wash up, then sleep on the bench.", ("flag", "slept_on_bench"), "M06", 0),
    ("M06", "Yesterday's News", "Find out what Smart City means.", ("flag", "read_newspaper"), "M07", 0),
    ("M07", "Plate Spinner", "Get a job at Lou's Diner.", ("flag", "diner_job"), "X1", 0),
    # the chain stops here for now (Old Block, the notice board and the Docks are not built yet)
    ("X1", "Explore the city", "Explore the city (Old Block coming soon).", None, None, 0),
    ("M08", "Odd Jobs", "Do three odd jobs (0/3).", ("flag", "odd_jobs_3"), "M09", 5),
    ("M09", "Old Block Calling", "Follow Mia to Old Block.", ("flag", "old_block_open"), "M10", 0),
    ("M10", "Rosa's Stall", "Carry three crates to Rosa's stall (0/3).", ("flag", "rosa_stall_done"), "M11", 10),
    ("M11", "Cold Shelves", "Visit VaultMart and see how Dex is doing.", ("flag", "vaultmart_visited"), "M12", 0),
    ("M12", "Old Friends", "Find Mr. Pimm in the library.", ("flag", "pimm_library_met"), "M13", 0),
    ("M13", "Notice Served", "Attend Rosa's meeting in Old Block.", ("flag", "meeting_attended"), "M14", 0),
    ("M14", "Paper Trail", "Find the bridge certificate in the archive.", ("flag", "certificate_found"), "M15", 0),
    ("M15", "Open Sesame", "Show the certificate at the bridge.", ("flag", "bridge_open"), "M16", 0),
    ("M16", "Dock Hand", "Meet Foreman Halloran at the Docks.", ("flag", "docks_job"), "M17", 12),
    ("M17", "A Roof for the Night", "Meet Mia at the bridge after your shift.", ("flag", "first_night_off_bench"), None, 0),
]
START_MISSION = "M01"

COND_KINDS = {"talk": "talk", "map": "enter_map", "money": "money", "flag": "flag", "day": "day", "time": "time"}


def cstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ---------------------------------------------------------------------------------------------------- dialogue parser
class Page:
    def __init__(self, speaker, text, expr=0):
        self.speaker, self.text, self.expr = speaker, text, expr
        self.effects, self.choices, self.next = [], [], None   # next: node name or None (= following page / end)
        self.cond = None                                        # (flag, negated, node): jump after this page


EXPRESSIONS = {"neutral": 0, "happy": 1, "angry": 2, "sad": 3, "surprised": 4}


def parse_effects(text):
    out = []
    for part in [p.strip() for p in text.split(",") if p.strip()]:
        w = part.split()
        op = w[0]
        if op == "friend":
            out.append(("friend", cast.IDS.index(w[1]), int(w[2])))
        elif op == "money":
            out.append(("money", 0, int(w[1])))
        elif op == "flag":
            out.append(("flag", FLAGS.index(w[1]), int(w[2]) if len(w) > 2 else 1))
        elif op in ("mission", "done"):
            out.append((op, 0, [m[0] for m in MISSIONS].index(w[1]) + 1))
        elif op == "coins":
            out.append(("coins", 0, int(w[1])))
        else:
            raise ValueError("unknown effect " + part)
    return out


def parse_dialogue():
    nodes, order, cur = {}, [], None
    path = os.path.join(ROOT, "tools", "dialogue_src.txt")
    for ln, raw in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("node "):
            cur = line[5:].strip()
            assert cur not in nodes, "duplicate node " + cur
            nodes[cur] = []
            order.append(cur)
        elif line.startswith("goto "):
            nodes[cur][-1].next = line[5:].strip()
        elif line.startswith("if ") or line.startswith("ifnot "):
            m = re.match(r"(if|ifnot) (\S+) -> (\S+)$", line)
            assert m, f"line {ln}: bad condition"
            assert m.group(2) in FLAGS, f"line {ln}: unknown flag {m.group(2)}"
            nodes[cur][-1].cond = (m.group(2), m.group(1) == "ifnot", m.group(3))
        elif line.startswith("! "):
            nodes[cur][-1].effects += parse_effects(line[2:])
        elif line.startswith("? "):
            m = re.match(r"\? (.*?) -> (\S+)\s*(?:\|\s*(.*))?$", line)
            assert m, f"line {ln}: bad choice"
            assert len(m.group(1)) <= 26, f"line {ln}: choice too long"
            nodes[cur][-1].choices.append((m.group(1), m.group(2), parse_effects(m.group(3) or "")))
        else:
            m = re.match(r"([A-Z]+)(?::([a-z]+))?\|\s*(.*)$", line)
            assert m, f"line {ln}: cannot parse: {line}"
            sp = m.group(1)
            sid = SP_PLAYER if sp == "PLAYER" else SP_NPC if sp == "NPC" else SP_SYSTEM if sp == "SYSTEM" else cast.IDS.index(SPEAKER_IDS[sp])
            expr = EXPRESSIONS[m.group(2)] if m.group(2) else 0
            nodes[cur].append(Page(sid, m.group(3).replace(" / ", " "), expr))
    return nodes, order


def main():
    nodes, order = parse_dialogue()
    # flatten: every page is one entry; node name -> index of its first page
    first, flat = {}, []
    for name in order:
        first[name] = len(flat)
        flat += nodes[name]
    # page index of each page object for "next"
    idx = {id(p): i for i, p in enumerate(flat)}
    effects, choices_out = [], []
    node_rows = []
    for name in order:
        pages = nodes[name]
        for k, p in enumerate(pages):
            i = idx[id(p)]
            nxt = -1
            if p.next:
                nxt = first[p.next]
            elif k + 1 < len(pages) and not p.choices:
                nxt = idx[id(pages[k + 1])]
            e0 = len(effects)
            effects += p.effects
            c0 = len(choices_out)
            for (text, target, eff) in p.choices:
                ef0 = len(effects)
                effects += eff
                choices_out.append((text, -1 if target == "end" else first[target], ef0, len(eff)))
            cf, cn, cx = -1, 0, -1
            if p.cond:
                cf, cn, cx = FLAGS.index(p.cond[0]), 1 if p.cond[1] else 0, first[p.cond[2]]
            node_rows.append((p.speaker, p.text, e0, len(p.effects), nxt, c0, len(p.choices), p.expr, cf, cn, cx))
    # ---- ids header
    h = ["// Generated by tools/story_data.py - do not edit by hand.", "#ifndef TL_STORY_IDS_H", "#define TL_STORY_IDS_H", "",
         "namespace tl", "{", "    // story flags (story_state::flag / set_flag)", "    namespace story_flag", "    {"]
    h += [f"        constexpr int {f} = {i};" for i, f in enumerate(FLAGS)]
    h += [f"        constexpr int count = {len(FLAGS)};", "    }", "", "    // missions: index + 1 (0 = no mission)", "    namespace mission_id", "    {"]
    h += [f"        constexpr int {m[0]} = {i + 1};" for i, m in enumerate(MISSIONS)]
    h += [f"        constexpr int count = {len(MISSIONS)};", f"        constexpr int start = {[m[0] for m in MISSIONS].index(START_MISSION) + 1};", "    }", "",
          "    // dialogue pages (first page of every node)", "    namespace dlg", "    {"]
    h += [f"        constexpr int {n} = {first[n]};" for n in order]
    h += [f"        constexpr int count = {len(flat)};", "    }", "", "}", "", "#endif", ""]
    open(os.path.join(ROOT, "include", "tl_story_ids.h"), "w", newline="\n").write("\n".join(h))
    # ---- data
    c = ["// Generated by tools/story_data.py - do not edit by hand.", "", '#include "tl_story.h"', "", "namespace tl", "{"]
    c.append("    namespace")
    c.append("    {")
    c.append("        constexpr dlg_effect all_effects[] = {")
    opmap = {"friend": "dlg_op::friend_delta", "money": "dlg_op::money", "flag": "dlg_op::set_flag", "mission": "dlg_op::start_mission",
             "done": "dlg_op::finish_mission", "coins": "dlg_op::coins"}
    for (op, a, b) in effects or [("money", 0, 0)]:
        c.append(f"            {{ {opmap[op]}, {a}, {b} }},")
    c.append("        };")
    c.append("        constexpr dlg_choice all_choices[] = {")
    for (t, nx, e0, en) in choices_out or [("", -1, 0, 0)]:
        c.append(f"            {{ {cstr(t)}, {nx}, {e0}, {en} }},")
    c.append("        };")
    c.append("        constexpr dlg_node all_nodes[] = {")
    for (sp, text, e0, en, nx, c0, cn, ex, cf, cneg, cnext) in node_rows:
        c.append(f"            {{ {cstr(text)}, {sp}, {en}, {e0}, {nx}, {cn}, {c0}, {ex}, {cf}, {cneg}, {cnext} }},")
    c.append("        };")
    c.append("    }")
    c.append("")
    c.append("    const dlg_node* dialogue_nodes() { return all_nodes; }")
    c.append(f"    int dialogue_nodes_count() {{ return {len(flat)}; }}")
    c.append("    const dlg_effect* dialogue_effects() { return all_effects; }")
    c.append("    const dlg_choice* dialogue_choices() { return all_choices; }")
    c.append("")
    # lookup tables (-1 when a node does not exist)
    def look(name):
        return first.get(name, -1)
    c.append("    const int16_t dialogue_talk_nodes[npc_count][topic_count] = {")
    for n in cast.IDS:
        c.append("        { " + ", ".join(str(look(f"talk_{n}_{t}")) for t in TOPICS) + " },")
    c.append("    };")
    c.append("    const int16_t dialogue_greet_nodes[npc_count][3] = {")
    for n in cast.IDS:
        c.append("        { " + ", ".join(str(look(f"greet_{n}_{m}")) for m in ("good", "neutral", "grumpy")) + " },")
    c.append("    };")
    c.append("    const int16_t dialogue_bye_nodes[npc_count] = { " + ", ".join(str(look(f"bye_{n}")) for n in cast.IDS) + " };")
    c.append("    const int16_t dialogue_intro_nodes[npc_count] = { " + ", ".join(str(look(f"intro_{n}")) for n in cast.IDS) + " };")
    c.append("")
    c.append("    const npc_info npc_infos[npc_count] = {")
    for n in cast.IDS:
        name, mood, likes, friend, gifts = NPC_INFO[n]
        c.append(f"        {{ {cstr(name)}, npc_mood::{mood}, {cstr(likes)}, {friend}, {'true' if n in TALKERS else 'false'}, {cstr(gifts)} }},")
    c.append("    };")
    c.append("")
    c.append("    const char* const topic_names[topic_count] = { " + ", ".join(cstr(t) for t in TOPIC_LABELS) + " };")
    c.append("    const char* const topic_openers[topic_count] = { " + ", ".join(cstr(t) for t in TOPIC_OPENERS) + " };")
    c.append("")
    c.append("    const gift_def gift_defs[gift_count] = {")
    for (name, price) in GIFTS:
        c.append(f"        {{ {cstr(name)}, {price} }},")
    c.append("    };")
    c.append("    const int16_t dialogue_gift_fav_nodes[npc_count] = { " + ", ".join(str(look(f"gift_fav_{n}")) for n in cast.IDS) + " };")
    c.append("    const gossip_rule gossip_rules[gossip_count] = {")
    for (gid, trig, hearer, node) in GOSSIP:
        assert node in first, node
        kind, npc, arg = trig
        argi = TOPICS.index(arg) if kind == "topic" else [g[0] for g in GIFTS].index(arg)
        c.append(f"        {{ {0 if kind == 'topic' else 1}, {cast.IDS.index(npc)}, {argi}, {cast.IDS.index(hearer)}, {first[node]} }},")
    c.append("    };")
    c.append("")
    code_index = {m[0]: i + 1 for i, m in enumerate(MISSIONS)}
    c.append("    const mission_def mission_defs[mission_count] = {")
    for (code, title, obj, cond, nxt, reward) in MISSIONS:
        if cond is None:
            ck, a, b = "none", "0", "0"
        else:
            ck = COND_KINDS[cond[0]]
            if cond[0] == "talk":
                a, b = f"int(npc_id::{cond[1]})", "0"
            elif cond[0] == "map":
                a, b = f"int(map_id::{cond[1]})", "0"
            elif cond[0] == "money":
                a, b = "0", str(cond[1])
            elif cond[0] == "flag":
                a, b = f"story_flag::{cond[1]}", "1"
            elif cond[0] == "day":
                a, b = str(cond[1]), "0"
            else:
                a, b = str(cond[1]), str(cond[2])
        c.append(f"        {{ {cstr(code)}, {cstr(title)}, {cstr(obj)}, mission_cond::{ck}, {a}, {b}, {code_index[nxt] if nxt else 0}, {reward} }},")
    c.append("    };")
    c.append("}")
    c.append("")
    open(os.path.join(ROOT, "src", "tl_story_data.cpp"), "w", newline="\n").write(
        "\n".join(c).replace('#include "tl_story.h"', '#include "tl_story.h"\n#include "tl_story_ids.h"'))
    print(f"story data written: {len(flat)} dialogue pages, {len(choices_out)} choices, {len(effects)} effects, {len(MISSIONS)} missions")


if __name__ == "__main__":
    main()
