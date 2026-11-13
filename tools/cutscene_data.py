#!/usr/bin/env python3
"""
Town Life - cutscene script compiler: tools/cutscenes_src.txt -> src/tl_cutscene_data.cpp (tables read by the script runner in
src/tl_field_script.cpp, declared in include/tl_cutscene.h) + include/tl_cutscene_ids.h (script ids).
Run by build_assets.py, or alone:  python3 tools/cutscene_data.py

FORMAT of cutscenes_src.txt (one statement per line, '#' starts a comment, indentation is free):

  script <name>                 starts a script; its statements follow until the next `script` / `trigger`
  label <name>                  jump target (scripts only)
  trigger <script> [when <cond> ...]   starts <script> by itself when ALL conditions hold while the player is walking free
                                (checked every frame; the script must set a flag that makes its own conditions false)
    conditions:  map=<map>  flag=<flag>  !flag=<flag>  flag>=<flag>:<n>  day=<n>  day>=<n>  time>=<h:mm>  time<<h:mm>  mission=<M02>

  STATEMENTS ("cell" values are map cells and may be fractional; directions: down up left right; facings: s sw w nw n ne e se;
  who = mia rosa dex dex_vault pimm lou victor robot; node = a node of tools/dialogue_src.txt):
    fade_out [frames]          fade to black (default 12 frames); waits
    fade_in [frames]           fade in from black; waits
    black                      cut to black immediately
    flash                      short white flash
    wait <frames>
    card "<text>"              narrator card on black (3 s), waits
    warp <map> <x> <y> <dir>   load another map and put the player there (call it while the screen is black)
    player_at <x> <y> <dir>    put the player somewhere on this map
    player_face <facing>       turn the player
    face_to <who>              turn the player towards an NPC
    walk <x> <y> [run]         the player walks there by himself (does not wait: use wait_moves)
    scene_begin                placements of the cast are switched off: only spawned actors stand around (use with scene_end)
    scene_end                  script actors are removed, the cast is placed again by its schedule
    spawn <who> <x> <y> <facing>      put an actor on the map (in addition to the scheduled cast unless scene_begin was used)
    despawn <who>
    swap <who> <who2>          replace an actor by another one at the same spot
    move <who> <x> <y> [fast]  actor walks (glides) there, does not wait
    actor_face <who> <facing>  /  actor_face_player <who>
    wait_moves                 wait until every walk has arrived
    say <node>                 play a dialogue node (speakers, choices, effects) and wait
    info "<text>"              one system page (no portrait) and wait
    flag <flag> [value]        set a story flag
    mission <id> / done <id>   start / finish a mission
    money <n> / money_rank     pay the player / pay the STOCK IT! rank wage (18 / 19 / 20 / 22)
    objective "<text>" / objective_clear   override / restore the objective line of the pause menu
    minigame stock|dishes      ends the script and starts a minigame (the field is rebuilt afterwards, see main.cpp)
    letterbox on|off           cinema bars (top / bottom 16 px)
    pan <x> <y> / pan_player   camera looks at a point / back to the player
    pan_now <x> <y>            like pan, but the camera jumps there at once (no half-visible actors at the screen edge while it scrolls)
    time <h> <m>               set the clock (same day);  next_day <h> <m> = next day at that time
    needs <hunger> <energy> <hygiene> <fun> <bladder>     add to the needs (deltas)
    eat <hunger> <energy> <fun>        eating animation, needs fill gradually (staff bread, free)
    lie_bed / get_up           the player lies down on the bed of the room / gets up
    car_spawn <x> <y> <se|nw>  put the golden car on the street (se = heading +x, nw = heading -x)
    car_move <x> <y> <frames> <mode>   the car drives there (mode 0 linear, 1 slowing down to a stop, 2 speeding up); wait_moves waits
    car_remove
    hook car_arrival           (kept, unused: the car is real now)
    clinic_care <0>            s64: after a faint: 2 hours pass, needs are patched up, the $20 fee is paid (flag clinic_paid = 1) or becomes a debt (0)
    vaultmart_swap             HOOK: the cold VaultMart look of Corner Market (design pending) - for now a cold palette + flash
    music <city|old_block|market|none> [volume%]   s78: switch the music track (fades; the next map change picks the track by place again)
    music_stop                 fade the music out
    music_restore              back to the music of the place (after a cutscene track)
    sfx <blip|confirm|back|coin|cash|door_bell|mission>   play a sound effect
    jump <label> / ifflag <flag> <n> <label>      jump (always / when the flag value >= n)
    end                        end of the script
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import story_data  # noqa: E402

FACINGS = {"s": 0, "sw": 1, "w": 2, "nw": 3, "n": 4, "ne": 5, "e": 6, "se": 7}
DIRS = {"down": 0, "up": 1, "left": 2, "right": 3}
NPCS = ["mia", "rosa", "dex", "pimm", "lou", "halloran", "dex_vault", "victor", "robot", "okafor"]

# op -> argument kinds: n int, c cell (x16), d direction, f facing, m map, w who, N dialogue node, F flag, M mission,
#                       s string, b on/off, k minigame kind, L label, h hook name; a trailing '?' = optional
OPS = {
    "fade_out": "n?", "fade_in": "n?", "black": "", "flash": "", "wait": "n", "card": "s", "warp": "mccd", "player_at": "ccd",
    "player_face": "f", "face_to": "w", "walk": "ccn?", "scene_begin": "", "scene_end": "", "spawn": "wccf", "despawn": "w",
    "swap": "ww", "move": "wccn?", "actor_face": "wf", "actor_face_player": "w", "wait_moves": "", "say": "N", "info": "s",
    "flag": "Fn?", "mission": "M", "done": "M", "money": "n", "money_rank": "", "objective": "s", "objective_clear": "",
    "minigame": "k", "letterbox": "b", "pan": "cc", "pan_player": "", "time": "nn", "next_day": "nn", "needs": "nnnnn",
    "eat": "nnn", "lie_bed": "", "get_up": "", "hook": "h", "vaultmart_swap": "", "jump": "L", "ifflag": "FnL", "end": "",
    "label": "L", "music": "tn?", "music_stop": "", "music_restore": "", "sfx": "x", "car_spawn": "ccf", "car_move": "ccnn", "car_remove": "", "clinic_care": "n", "pan_now": "cc",
}
def _enum_names(block):
    """enumerator names of `enum class <block>` in include/tl_audio.h, in order (the index is the value the C++ side reads)"""
    text = open(os.path.join(ROOT, "include", "tl_audio.h")).read()
    body = text[text.index("enum class " + block):]
    body = body[body.index("{") + 1:body.index("};")]
    names = []
    for line in body.split("\n"):
        line = line.split("//")[0].strip().rstrip(",")
        if line:
            names.append(line)
    return {n: i for i, n in enumerate(names)}


AUDIO_TRACKS = _enum_names("track")
AUDIO_SFX = {k: v for k, v in _enum_names("sfx").items() if k != "none"}
COND_KINDS = ["map", "flag", "noflag", "flag_ge", "day_eq", "day_ge", "time_ge", "time_lt", "mission"]


def tokens(line):
    out = []
    for m in re.finditer(r'"([^"]*)"|(\S+)', line):
        out.append(m.group(1) if m.group(1) is not None else m.group(2))
    return out


def parse():
    scripts, order, cur, triggers = {}, [], None, []
    path = os.path.join(ROOT, "tools", "cutscenes_src.txt")
    for ln, raw in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        line = raw.split("#")[0].strip() if '"' not in raw else raw.strip()
        if '"' in raw and raw.strip().startswith("#"):
            continue
        if not line:
            continue
        t = tokens(line)
        if t[0] == "script":
            cur = t[1]
            assert cur not in scripts, f"line {ln}: duplicate script {cur}"
            scripts[cur] = []
            order.append(cur)
        elif t[0] == "trigger":
            conds = t[3:] if len(t) > 2 and t[2] == "when" else []
            triggers.append((t[1], conds, ln))
        else:
            assert cur, f"line {ln}: statement outside a script"
            assert t[0] in OPS, f"line {ln}: unknown statement {t[0]}"
            scripts[cur].append((t, ln))
    return scripts, order, triggers


def cell(v):
    return int(round(float(v) * 16))


def convert_args(op, args, ln):
    sig = OPS[op]
    kinds = []
    i = 0
    while i < len(sig):
        opt = i + 1 < len(sig) and sig[i + 1] == "?"
        kinds.append((sig[i], opt))
        i += 2 if opt else 1
    assert len(args) <= len(kinds) and len(args) >= len([k for k in kinds if not k[1]]), f"line {ln}: wrong argument count for {op}"
    vals = []
    s_val = "nullptr"
    for (kind, opt), a in zip(kinds, args):
        if kind == "n":
            vals.append("1" if a in ("run", "fast") else str(int(a)))
        elif kind == "c":
            vals.append(str(cell(a)))
        elif kind == "d":
            assert a in DIRS, f"line {ln}: direction {a}"
            vals.append(str(DIRS[a]))
        elif kind == "f":
            assert a in FACINGS, f"line {ln}: facing {a}"
            vals.append(str(FACINGS[a]))
        elif kind == "m":
            vals.append(f"int(map_id::{a})")
        elif kind == "w":
            assert a in NPCS, f"line {ln}: who {a}"
            vals.append(f"int(npc_id::{a})")
        elif kind == "N":
            vals.append(f"dlg::{a}")
        elif kind == "F":
            assert a in story_data.FLAGS, f"line {ln}: flag {a}"
            vals.append(f"story_flag::{a}")
        elif kind == "M":
            vals.append(f"mission_id::{a}")
        elif kind == "s":
            s_val = '"' + a.replace('"', '\\"') + '"'
        elif kind == "b":
            vals.append("1" if a == "on" else "0")
        elif kind == "k":
            vals.append({"stock": "0", "dishes": "1"}[a])
        elif kind == "t":
            assert a in AUDIO_TRACKS, f"line {ln}: track {a} (known: {', '.join(AUDIO_TRACKS)})"
            vals.append(str(AUDIO_TRACKS[a]))
        elif kind == "x":
            assert a in AUDIO_SFX, f"line {ln}: sfx {a} (known: {', '.join(AUDIO_SFX)})"
            vals.append(str(AUDIO_SFX[a]))
        elif kind == "h":
            vals.append({"car_arrival": "0"}[a])
        elif kind == "L":
            vals.append(f"LABEL:{a}")
    return vals, s_val


def main():
    scripts, order, triggers = parse()
    code_lines, script_rows = [], []
    for name in order:
        start = len(code_lines)
        labels = {}
        stmts = scripts[name]
        # first pass: labels (index of the next real statement)
        idx = 0
        for t, ln in stmts:
            if t[0] == "label":
                labels[t[1]] = idx
            else:
                idx += 1
        for t, ln in stmts:
            op, args = t[0], t[1:]
            if op == "label":
                continue
            vals, s_val = convert_args(op, args, ln)
            if op == "flag" and len(args) == 1:
                vals.append("1")
            vv = []
            for v in vals:
                if isinstance(v, str) and v.startswith("LABEL:"):
                    vv.append(str(start + labels[v[6:]]))
                else:
                    vv.append(v)
            while len(vv) < 5:
                vv.append("0")
            code_lines.append(f"        {{ cs_op::{op}, {', '.join(vv)}, {s_val} }},  // {name}")
        code_lines.append(f"        {{ cs_op::end, 0, 0, 0, 0, 0, nullptr }},  // {name}")
        script_rows.append((start, len(code_lines) - start))
    cond_rows, trig_rows = [], []
    for sname, conds, ln in triggers:
        assert sname in scripts, f"line {ln}: unknown script {sname}"
        first = len(cond_rows)
        for c in conds:
            m = re.match(r"(!?)(map|flag|day|time|mission)(>=|<|=)(.*)$", c)
            assert m, f"line {ln}: bad condition {c}"
            neg, key, cmp_, val = m.groups()
            if key == "map":
                cond_rows.append(("map", f"int(map_id::{val})", 0))
            elif key == "flag" and cmp_ == "=":
                assert val in story_data.FLAGS, f"line {ln}: flag {val}"
                cond_rows.append(("noflag" if neg else "flag", f"story_flag::{val}", 0))
            elif key == "flag" and cmp_ == ">=":
                fl, n = val.split(":")
                cond_rows.append(("flag_ge", f"story_flag::{fl}", int(n)))
            elif key == "day":
                cond_rows.append(("day_eq" if cmp_ == "=" else "day_ge", int(val), 0))
            elif key == "time":
                h, mi = val.split(":")
                cond_rows.append(("time_ge" if cmp_ == ">=" else "time_lt", int(h) * 60 + int(mi), 0))
            elif key == "mission":
                cond_rows.append(("mission", f"mission_id::{val}", 0))
        trig_rows.append((order.index(sname), first, len(conds)))
    h = ["// Generated by tools/cutscene_data.py - do not edit by hand.", "#ifndef TL_CUTSCENE_IDS_H", "#define TL_CUTSCENE_IDS_H", "",
         "namespace tl", "{", "    namespace script_id", "    {"]
    h += [f"        constexpr int {n} = {i};" for i, n in enumerate(order)]
    h += [f"        constexpr int count = {len(order)};", "    }", "}", "", "#endif", ""]
    open(os.path.join(ROOT, "include", "tl_cutscene_ids.h"), "w", newline="\n").write("\n".join(h))
    c = ["// Generated by tools/cutscene_data.py - do not edit by hand.", "", '#include "tl_cutscene.h"', '#include "tl_story_ids.h"',
         '#include "tl_cutscene_ids.h"', "", "namespace tl", "{", "    namespace", "    {", "        constexpr cs_step all_steps[] = {"]
    c += code_lines
    c += ["        };", "        constexpr cs_script all_scripts[] = {"]
    c += [f"            {{ {a}, {b} }}," for a, b in script_rows]
    c += ["        };", "        constexpr cs_cond all_conds[] = {"]
    c += [f"            {{ cs_cond_kind::{k}, {a}, {b} }}," for k, a, b in (cond_rows or [("map", 0, 0)])]
    c += ["        };", "        constexpr cs_trigger all_triggers[] = {"]
    c += [f"            {{ {s}, {f}, {n} }}," for s, f, n in trig_rows]
    c += ["        };", "    }", "", "    const cs_step* cutscene_steps() { return all_steps; }",
          "    const cs_script* cutscene_scripts() { return all_scripts; }",
          "    const cs_cond* cutscene_conds() { return all_conds; }",
          "    const cs_trigger* cutscene_triggers() { return all_triggers; }",
          f"    int cutscene_triggers_count() {{ return {len(trig_rows)}; }}", "}", ""]
    open(os.path.join(ROOT, "src", "tl_cutscene_data.cpp"), "w", newline="\n").write("\n".join(c))
    print(f"cutscenes written: {len(order)} scripts, {len(code_lines)} steps, {len(trig_rows)} triggers")


if __name__ == "__main__":
    main()
