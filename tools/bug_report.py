#!/usr/bin/env python3
"""Town Life bug reports (development tool): list the in-game bug reports of a save file and replay one headlessly.

The game (src/tl_blackbox.cpp, docs/bug_reports.md) writes up to 4 reports into SRAM after the normal save (offset 4096..). Lemuroid's
.srm file is that SRAM. Usage:

  python3 tools/bug_report.py list  GAME.srm
  python3 tools/bug_report.py replay GAME.srm [N] --rom town-life.gba --out OUTDIR [--png-every 30] [--gif-every 6] [--tail-frames 120]
  python3 tools/bug_report.py dump  GAME.srm N OUT.sav     (the report's snapshot as a normal save file)

`replay` loads the report's snapshot as the save (Continue), restores the random state, then feeds the recorded keypad states frame by
frame (synchronised with the game's own frame counter, read from the emulator state), saving a PNG every N frames, an animated GIF and a
text summary (summary.txt) in OUTDIR. It needs the libretro mGBA core (apt-get install libretro-mgba) and Pillow. Use the ROM of the same
build as the report (the build date is printed and checked against the ROM).

How faithful is a replay? See docs/bug_reports.md ("Determinism"): the snapshot restores the whole save_data and the bn::random state, and
the inputs are fed per game frame, so usually the same thing happens; anything not in the save (animal / NPC positions, toasts, cutscene
progress, a menu that was open) can differ, and the end of the summary compares the final position / time / money with the report.
"""
import argparse
import ctypes as ct
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

REGION = 4096
SLOTS = 4
LOG_CAP = 2048
CATEGORIES = {0: "(none)", 1: "Game froze / stuck", 2: "Graphics glitch", 3: "Text problem", 4: "Can't do objective", 5: "Other"}
FLAG_TEXT = [(1, "snapshot usable for replay"), (2, "snapshot taken while not calm (menu/dialogue/script open)"),
             (4, "reported inside a minigame"), (8, "NO usable snapshot (log trimmed): cannot replay")]
MARKER_TEXT = {1: "minigame started", 2: "field rebuilt after a minigame / scene change", 3: "report filed"}
# keypad bits used by the black box (src/tl_blackbox.cpp read_keys) -> headless_run key names
KEY_BITS = [(1, "a"), (2, "b"), (4, "select"), (8, "start"), (16, "right"), (32, "left"), (64, "up"), (128, "down"), (256, "r"), (512, "l")]


def load_save_struct():
    import make_save
    return make_save.Save


def map_names():
    names = []
    path = os.path.join(ROOT, "include", "tl_map_id.h")
    try:
        text = open(path).read()
        body = re.search(r"enum class map_id[^{]*\{(.*?)\}", text, re.S).group(1)
        names = [n.strip().split("=")[0].strip() for n in body.split(",") if n.strip()]
    except Exception:
        pass
    return [n for n in names if n != "count"] or ["map%d" % i for i in range(16)]


class Marker(ct.Structure):
    _fields_ = [("frame", ct.c_uint32), ("kind", ct.c_uint32)]


def report_struct():
    Save = load_save_struct()

    class Report(ct.Structure):
        _fields_ = [("magic", ct.c_uint32), ("version", ct.c_uint16), ("size", ct.c_uint16), ("checksum", ct.c_uint32),
                    ("number", ct.c_uint32), ("category", ct.c_uint8), ("flags", ct.c_uint8), ("map", ct.c_uint8),
                    ("marker_count", ct.c_uint8), ("day", ct.c_uint16), ("minutes", ct.c_uint16), ("x", ct.c_int16),
                    ("y", ct.c_int16), ("money", ct.c_int32), ("frame_now", ct.c_uint32), ("snap_frame", ct.c_uint32),
                    ("log_frames", ct.c_uint32), ("log_entries", ct.c_uint16), ("pad", ct.c_uint16), ("rng", ct.c_uint32 * 3),
                    ("markers", Marker * 6), ("build", ct.c_char * 32), ("snap", Save), ("log", ct.c_uint16 * LOG_CAP)]
    return Report


def fletcher(data):
    a, b = 1, 0
    for byte in data:
        a = (a + byte) % 65521
        b = (b + a) % 65521
    return (b << 16) | a


# region header: magic u32, version u16, slots u16, next_number u32, replay_flag u32, replay_rng u32[3], checksum u32, reserved u32[8]
HEADER = struct.Struct("<IHHII3II8I")
HEADER_CHECKED = 28


def read_reports(srm):
    Report = report_struct()
    size = ct.sizeof(Report)
    out = []
    if len(srm) < REGION + 64 + SLOTS * size:
        raise SystemExit("file too small for the report region (%d bytes): is this a Town Life .srm?" % len(srm))
    for index in range(SLOTS):
        off = REGION + 64 + index * size
        raw = srm[off:off + size]
        r = Report.from_buffer_copy(raw)
        if r.magic != 0x58424C54 or r.version != 1 or r.size != size:
            continue
        if r.checksum != fletcher(raw[12:]):
            print("slot %d: checksum mismatch (damaged), skipped" % index, file=sys.stderr)
            continue
        out.append(r)
    out.sort(key=lambda r: r.number)
    return out


def expand_log(r):
    """Per-frame key bitmasks for the frames after the snapshot."""
    frames = []
    for i in range(r.log_entries):
        entry = r.log[i]
        frames.extend([entry & 0x3FF] * ((entry >> 10) + 1))
    return frames


def keys_of(mask):
    # L and R are masked: the recorded chord that opened the report panel must not open it again in the replay
    return {name for bit, name in KEY_BITS if mask & bit and name not in ("l", "r")}


def time_text(minutes):
    return "%02d:%02d" % (minutes // 60, minutes % 60)


def describe(r, names):
    lines = []
    lines.append("Report #%d  [%s]" % (r.number, CATEGORIES.get(r.category, r.category)))
    lines.append("  build      : %s" % r.build.decode(errors="replace"))
    lines.append("  when       : day %d %s   map %s   position %.1f, %.1f   money $%d" % (
        r.day, time_text(r.minutes), names[r.map] if r.map < len(names) else r.map, r.x / 16, r.y / 16, r.money))
    lines.append("  game frames: report at %d, snapshot at %d, log covers %d frames (%.1f s), %d RLE entries" % (
        r.frame_now, r.snap_frame, r.log_frames, r.log_frames / 60, r.log_entries))
    flags = [text for bit, text in FLAG_TEXT if r.flags & bit]
    lines.append("  flags      : %s" % ("; ".join(flags) or "-"))
    for i in range(r.marker_count):
        m = r.markers[i]
        lines.append("  marker     : frame %d (%+d vs. snapshot): %s" % (m.frame, m.frame - r.snap_frame, MARKER_TEXT.get(m.kind, m.kind)))
    if r.flags & 1:
        s = r.snap
        lines.append("  snapshot   : map %s at %.1f, %.1f  day %d %s  money $%d  mission %d" % (
            names[s.map] if s.map < len(names) else s.map, s.x / 16, s.y / 16, s.day, time_text(s.minutes), s.money, s.mission_id))
    return lines


def cmd_list(args):
    srm = open(args.srm, "rb").read()
    names = map_names()
    reports = read_reports(srm)
    print("%s: %d bytes, %d report(s)" % (args.srm, len(srm), len(reports)))
    for r in reports:
        print("\n".join(describe(r, names)))
        print()


def pick(reports, number):
    if not reports:
        raise SystemExit("no bug reports in this file")
    if number is None:
        return reports[-1]
    for r in reports:
        if r.number == number:
            return r
    raise SystemExit("no report #%d (have: %s)" % (number, ", ".join(str(r.number) for r in reports)))


def cmd_dump(args):
    r = pick(read_reports(open(args.srm, "rb").read()), args.number)
    open(args.out, "wb").write(bytes(r.snap))
    print("snapshot of report #%d written as a save file: %s (load it with headless_run.py loadsram)" % (r.number, args.out))


# ------------------------------------------------------------------------------------------------------- replay

class Ewram:
    """The black box state in EWRAM (src/tl_blackbox.cpp struct visible), read out of an emulator savestate by its magic
    (the libretro mGBA core does not expose work RAM)."""
    MAGIC = b"TLBB"
    WORDS = 18      # magic, frame, active, reports, live[7] (map, x, y, day, minutes, money, playing), in_panel, snapshots, tiles_free, items_free

    def __init__(self, runner):
        self.core = runner.core
        self.core.retro_serialize_size.restype = ct.c_size_t
        self.size = self.core.retro_serialize_size()
        self.buf = ct.create_string_buffer(self.size)
        self.addr = None

    def state(self):
        self.core.retro_serialize(self.buf, ct.c_size_t(self.size))
        return self.buf.raw

    def read(self):
        data = self.state()
        if self.addr is None or data[self.addr:self.addr + 4] != self.MAGIC:
            self.addr = data.find(self.MAGIC)
            if self.addr < 0:
                self.addr = None
                return (0,) * self.WORDS
        return struct.unpack_from("<%dI" % self.WORDS, data, self.addr)


def frame_image(runner):
    from PIL import Image
    data, w, h, pitch = runner.frame
    if runner.pixel_format == 1:
        return Image.frombuffer("RGB", (w, h), data, "raw", "BGRX", pitch, 1)
    img = Image.new("RGB", (w, h))
    px = []
    for y in range(h):
        row = data[y * pitch:(y + 1) * pitch]
        for x in range(w):
            v = row[x * 2] | (row[x * 2 + 1] << 8)
            px.append(((v >> 11) << 3, ((v >> 5) & 63) << 2, (v & 31) << 3))
    img.putdata(px)
    return img


def cmd_replay(args):
    import headless_run as H
    from PIL import Image, ImageDraw
    srm = bytearray(open(args.srm, "rb").read())
    names = map_names()
    r = pick(read_reports(bytes(srm)), args.number)
    lines = describe(r, names)
    print("\n".join(lines))
    os.makedirs(args.out, exist_ok=True)
    summary = list(lines)

    if not (r.flags & 1):
        summary.append("")
        summary.append("This report has no usable snapshot, so it cannot be replayed (only the details above are available).")
        open(os.path.join(args.out, "summary.txt"), "w").write("\n".join(summary) + "\n")
        print("no replay possible")
        return

    rom = open(args.rom, "rb").read()
    build = r.build.decode(errors="replace")
    if build.encode() not in rom:
        warn = "WARNING: the ROM does not contain the report's build string '%s': it is another build, the replay may not match." % build
        print(warn)
        summary += ["", warn]
    if r.flags & 4:
        note = "NOTE: this report was filed inside a minigame; the replay can only show the field before it (see docs/bug_reports.md)."
        print(note)
        summary += ["", note]

    # SRAM image: the report's snapshot as the normal save, replay request (random state) in the region header
    sram = bytearray(max(32768, len(srm)))
    sram[:len(srm)] = srm
    snap = bytes(r.snap)
    sram[:len(snap)] = snap
    fields = list(HEADER.unpack_from(sram, REGION))
    if fields[0] != 0x52424C54:
        fields = [0x52424C54, 1, SLOTS, 1, 0, 0, 0, 0, 0] + [0] * 8
    fields[4] = 1
    fields[5:8] = list(r.rng)
    packed = bytearray(HEADER.pack(*fields))
    fields[8] = fletcher(packed[:HEADER_CHECKED])
    HEADER.pack_into(sram, REGION, *fields)
    sram_path = os.path.join(args.out, "replay.sram")
    open(sram_path, "wb").write(sram)

    runner = H.Runner(args.rom)
    runner.load_sram(sram_path)
    runner.reset()
    ew = Ewram(runner)
    runner.run(200)                                      # logo / title
    runner.held = {H.KEYS["a"]}                          # Continue
    runner.run(4)
    runner.held = set()
    started = False
    for _ in range(1500):
        runner.run(1)
        if ew.read()[2] == 1:
            started = True
            break
    if not started:
        raise SystemExit("the game did not start (Continue failed?): is this the right ROM?")

    log = expand_log(r)
    total = len(log) if args.max_frames is None else min(len(log), args.max_frames)
    png_dir = os.path.join(args.out, "frames")
    os.makedirs(png_dir, exist_ok=True)
    gif_frames = []
    start_state = ew.read()
    summary.append("")
    summary.append("Replay: game restarted from the snapshot at map %s, %d frames of input to feed (log[0] is lost: see docs)." % (
        names[start_state[4]] if start_state[4] < len(names) else start_state[4], total))
    last_frame = -1

    def capture(index):
        img = frame_image(runner)
        if index % args.png_every == 0:
            img.save(os.path.join(png_dir, "frame_%05d.png" % index))
        if index % args.gif_every == 0:
            big = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
            keys = "+".join(sorted(keys_of(log[index]))) if index < len(log) else ""
            ImageDraw.Draw(big).text((4, 4), "f%d  %s" % (index, keys), fill=(255, 255, 0))
            gif_frames.append(big.convert("P", palette=Image.ADAPTIVE, colors=64))

    guard = 0
    while guard < total * 4 + 600:
        guard += 1
        frame = ew.read()[1]
        if frame >= total:
            break
        if frame != last_frame:
            capture(frame)
        last_frame = frame
        # the key state set now is what the game polls next, i.e. the log entry with the frame counter's value
        runner.held = {H.KEYS[k] for k in keys_of(log[frame])} if frame >= 1 else set()
        runner.run(1)
    runner.held = set()
    final = ew.read()
    capture(total)
    for index in range(args.tail_frames):
        runner.run(1)
        if index % args.gif_every == 0:
            big = frame_image(runner).resize((480, 320), Image.NEAREST)
            gif_frames.append(big.convert("P", palette=Image.ADAPTIVE, colors=64))
    frame_image(runner).save(os.path.join(png_dir, "final.png"))

    gif_path = os.path.join(args.out, "replay.gif")
    if gif_frames:
        gif_frames[0].save(gif_path, save_all=True, append_images=gif_frames[1:], duration=max(20, int(args.gif_every * 1000 / 60)),
                           loop=0, optimize=False)

    live = final[4:11]
    summary.append("Final state of the replay vs. the report (determinism check):")
    rows = [("map", live[0], r.map), ("x (cells)", live[1] / 16, r.x / 16), ("y (cells)", live[2] / 16, r.y / 16),
            ("day", live[3], r.day), ("minutes", live[4], r.minutes), ("money", live[5], r.money)]
    same = True
    for name, got, want in rows:
        flag = "ok" if abs(got - want) < 1e-6 else "DIFFERENT"
        same = same and flag == "ok"
        summary.append("  %-10s replay %-8s report %-8s %s" % (name, got, want, flag))
    dist = ((live[1] - r.x) ** 2 + (live[2] - r.y) ** 2) ** 0.5 / 16
    summary.append("  => %s (position distance %.2f cells)" % ("IDENTICAL end state" if same else "end state differs", dist))
    summary.append("Output: %s (replay.gif, frames/*.png, final.png, summary.txt)" % args.out)
    open(os.path.join(args.out, "summary.txt"), "w").write("\n".join(summary) + "\n")
    print("\n".join(summary[len(lines):]))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("list")
    a.add_argument("srm")
    a.set_defaults(func=cmd_list)
    d = sub.add_parser("dump")
    d.add_argument("srm")
    d.add_argument("number", type=int)
    d.add_argument("out")
    d.set_defaults(func=cmd_dump)
    b = sub.add_parser("replay")
    b.add_argument("srm")
    b.add_argument("number", type=int, nargs="?", default=None, help="report number (default: the newest)")
    b.add_argument("--rom", default=os.path.join(ROOT, "town-life.gba"))
    b.add_argument("--out", required=True)
    b.add_argument("--png-every", type=int, default=30)
    b.add_argument("--gif-every", type=int, default=6)
    b.add_argument("--tail-frames", type=int, default=0, help="extra frames to run after the log ends")
    b.add_argument("--max-frames", type=int, default=None)
    b.set_defaults(func=cmd_replay)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
