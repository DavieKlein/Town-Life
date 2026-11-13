"""Door audit (s81): python3 tools/door_audit.py [scene ids]  - lists every prop / solid cell in the approach corridor of every
exterior door warp (door x range +-0.3, 3 cells in front of the wall). Props within 0.25 of the wall (frames, mats) are ignored."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as sc


def bbox(p):
    t = p["type"]
    if t == "box":
        return p["x0"], p["y0"], p["x1"], p["y1"], p["z0"], p["z1"]
    if t == "cyl":
        return p["x"] - p["r"], p["y"] - p["r"], p["x"] + p["r"], p["y"] + p["r"], p["z0"], (p["z1"] if p.get("axis", "z") == "z" else p["z0"] + p["r"])
    if t == "sphere":
        return p["x"] - p["r"], p["y"] - p["r"], p["x"] + p["r"], p["y"] + p["r"], p["z"] - p["r"], p["z"] + p["r"]
    if t == "wedge":
        return p["x0"], p["y0"], p["x1"], p["y1"], p["z_bottom"], p["z_top"]
    if t == "model":
        return (*p["fp"], 0, 9)
    if t == "kit":
        return p["x"] - 1, p["y"] - 1, p["x"] + 1, p["y"] + 1, 0, 9
    return None


def run(only=None):
    bad = 0
    for fn in sc.SCENES:
        s = fn()
        if only and s.ident not in only:
            continue
        if not s.sun:
            continue
        for w in s.warps:
            x0, y0, x1, y1, tgt = w[:5]
            if tgt in ("city_centre", "old_block", "sewer") and x0 < 3:
                continue
            wall = y1 if (y1 - y0) < 1.5 else y1
            if tgt == "lane_shop":
                continue
            cx0, cx1, cy0, cy1 = x0 - 0.3, x1 + 0.3, wall + 0.25, wall + 3.0
            hits = []
            for p in s.prims:
                if p.get("layer") == "floor":
                    continue
                b = bbox(p)
                if not b:
                    continue
                if b[0] < cx1 and b[2] > cx0 and b[1] < cy1 and b[3] > cy0 and b[4] < 2.2:
                    hits.append((p["type"], p.get("mat", p.get("name")), tuple(round(v, 2) for v in b[:4])))
            sol = []
            r = sc.SOLID_RES
            for sy in range(int(cy0 * r), int(cy1 * r)):
                for sx in range(int(cx0 * r), int(cx1 * r)):
                    if 0 <= sy < len(s.solid) and 0 <= sx < len(s.solid[0]) and s.solid[sy][sx]:
                        sol.append((sx / r, sy / r))
            if hits or sol:
                bad += 1
                print("%s door -> %s rect %s wall y=%.2f" % (s.ident, tgt, tuple(round(v, 2) for v in w[:4]), wall))
                for h in hits:
                    print("    prop", h)
                if sol:
                    print("    solid subcells:", len(sol), "e.g.", sol[:4])
    print("doors with obstacles:", bad)


if __name__ == "__main__":
    run(sys.argv[1:] or None)
