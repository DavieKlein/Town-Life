"""Builds every preview of the s77 sewer proposal.   python3 shots.py OUTDIR [name ...]     (env S77_SPP = samples, default 96)
Names: cc_a cc_b ob_open ob_closed sewer (sewer_* game screens + full map) climb (transition mock frames) sheets (contact sheets)."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compose as c  # noqa: E402
import sewer as sw  # noqa: E402

out = sys.argv[1]
want = sys.argv[2:] or ["cc_a", "cc_b", "ob_open", "ob_closed", "sewer", "climb", "sheets"]
os.makedirs(out, exist_ok=True)
MX, MY = sw.EXIT_OB
A = c.actor
FONT = c.FONT

# ---- City Centre ----------------------------------------------------------------------------------------------------
if "cc_a" in want:
    c.shot(f"{out}/cc_a", "cc_a", 64.9, 28.4, [A("player", 64.9, 28.4, "e")], cue_at=(66.7, 27.8))
if "cc_b" in want:
    c.shot(f"{out}/cc_b", "cc_b", 61.2, 49.6, [A("player", 61.2, 49.6, "w")], cue_at=(58.5, 49.9))
# ---- Old Block exit -----------------------------------------------------------------------------------------------------
if "ob_open" in want:
    c.shot(f"{out}/ob_open", "ob_open", MX + 1.5, MY + 0.9, [A("player", MX + 1.5, MY + 0.9, "sw"), A("teo", MX + 2.9, MY - 1.3, "sw")])
if "ob_closed" in want:
    c.shot(f"{out}/ob_closed", "ob_closed", MX + 1.5, MY + 0.9, [A("player", MX + 1.5, MY + 0.9, "w")], cue_at=(MX, MY))
# ---- Sewer ---------------------------------------------------------------------------------------------------------------
if "sewer" in want:
    q = c.sewer_full(out)
    S = lambda name, px, py, acts, **kw: c.shot_sewer(f"{out}/sewer_{name}", px, py, acts, out, **kw)
    S("west", 2.4, 0.9, [A("player", 2.4, 0.9, "n", idx=0)], cue_at=(sw.WEST_SHAFT, -0.9))
    S("bridge", 11.3, 3.8, [A("player", 11.3, 3.8, "e", idx=9)])
    S("collapse", 14.2, 3.4, [A("player", 12.0, 3.7, "e", idx=8)])
    S("nook", 22.6, 2.0, [A("player", 22.6, 2.0, "n")])
    S("east", 26.0, 1.9, [A("player", 26.0, 1.9, "e")], cue_at=(sw.EAST_SHAFT, -0.7))
    S("front", 8.0, 7.0, [A("player", 8.0, 7.0, "e", idx=7)])
