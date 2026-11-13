"""Reachability check (s81): python3 tools/reach_check.py [scene id ...]
Flood-fills the collision grid (player = square of radius 0.25 cell = 1 sub-cell, gated solids treated as closed unless the gate is
listed in OPEN) from the map's arrival spots and reports warp rects, interactable points and NPC placements that cannot be reached."""
import sys, os
from collections import deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as sc
import interactions as I
import cast

OPEN = {"old_block": ("barrier", "bridge")}


def free_grid(s, open_gates=()):
    r = sc.SOLID_RES
    g = [row[:] for row in s.solid]
    for (name, x0, y0, x1, y1) in s.gates:
        if name in open_gates:
            for sy in range(int(y0 * r), int(y1 * r)):
                for sx in range(int(x0 * r), int(x1 * r)):
                    g[sy][sx] = False
    return g


def ok(g, sx, sy):
    h, w = len(g), len(g[0])
    for dy in (-1, 0):
        for dx in (-1, 0):
            x, y = sx + dx, sy + dy
            if x < 0 or y < 0 or x >= w or y >= h or g[y][x]:
                return False
    return True


def flood(g, starts):
    seen = set()
    dq = deque()
    for st in starts:
        if ok(g, *st):
            seen.add(st)
            dq.append(st)
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and ok(g, *n):
                seen.add(n)
                dq.append(n)
    return seen


def main(only):
    r = sc.SOLID_RES
    arrivals = {}
    for fn in sc.SCENES:
        s = fn()
        for w in s.warps:
            arrivals.setdefault(w[4], []).append((int(w[5] * r), int(w[6] * r)))
    bad = 0
    for fn in sc.SCENES:
        s = fn()
        if only and s.ident not in only:
            continue
        g = free_grid(s, OPEN.get(s.ident, ()))
        starts = arrivals.get(s.ident, [])
        seen = flood(g, starts)
        if not seen:
            print(s.ident, "no reachable start", starts)
            bad += 1
            continue
        for w in s.warps:
            x0, y0, x1, y1 = w[:4]
            hit = any(x0 * r <= sx < x1 * r and y0 * r <= sy < y1 * r for (sx, sy) in seen)
            if not hit:
                print("%s: warp to %s at %s UNREACHABLE" % (s.ident, w[4], w[:4]))
                bad += 1
        for it in I.INTERACTABLES.get(s.ident, []):
            kind, x, y = it[0], it[1], it[2]
            if kind in ("manhole", "ladder", "hatch"):
                continue
            reach = 1.75 + (it[3] if len(it) > 3 and isinstance(it[3], (int, float)) else 0)
            if kind == "fountain":
                reach += 2
            if not any(((sx / r - x) ** 2 + (sy / r - y) ** 2) ** 0.5 <= reach for (sx, sy) in seen):
                print("%s: interactable %s unreachable" % (s.ident, it))
                bad += 1
        for p in cast.PLACEMENTS:
            if p[1] == s.ident:
                nx, ny = p[2], p[3]
                if not any(((sx / r - nx) ** 2 + (sy / r - ny) ** 2) ** 0.5 <= 1.2 for (sx, sy) in seen):
                    print("%s: NPC %s at (%s,%s) has no reachable cell within 1.2" % (s.ident, p[0], nx, ny))
                    bad += 1
        # exit targets must be free
    for fn in sc.SCENES:
        s = fn()
        for w in s.warps:
            tgt = [f for f in sc.SCENES if f.__name__ and True]
    print("problems:", bad)


if __name__ == "__main__":
    main(set(sys.argv[1:]))
