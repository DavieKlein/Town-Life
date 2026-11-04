"""
Town Life - NPCs are now described in tools/cast.py (looks + placements per time of day, generated into
include/tl_cast_data.h). The per-map spawn list below stays empty (kept so build_assets.py still emits the
`npcs` / `npcs_count` fields of map_info as nullptr / 0).
"""

NPCS = {}
LOOKS = {}
FACINGS = ["s", "sw", "w", "nw", "n", "ne", "e", "se"]
