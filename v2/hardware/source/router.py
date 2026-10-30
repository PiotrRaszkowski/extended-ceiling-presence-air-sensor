"""
Small two-layer grid router for the v2 carrier board (replaces an external autorouter).

    python router.py   -> reads out/carrier_unrouted.kicad_pcb, writes out/carrier_routed.kicad_pcb

Lee/A* search on a 0.25 mm grid, 8 directions, vias between F.Cu and B.Cu.
Every net is routed as a tree: each new pad connects to the nearest point of the
copper already laid for that net. Pads and finished tracks of other nets are inflated
by (clearance + half the track width) so that the result passes DRC with
TRACK_W / CLEARANCE below. If a net cannot be routed, the order is shuffled and the
whole board is tried again.
"""
import heapq
import math
import random
import sys

import numpy as np
import pcbnew

import layout as L

G = 0.25            # grid step [mm]
TRACK_W = 0.5
CLEARANCE = 0.25
VIA_D, VIA_DRILL = 0.8, 0.4
EDGE_CLR = 0.5      # copper to board edge
OX, OY = 100.0, 100.0
N = int(2 * (L.R_PCB + 1) / G) + 1
X0 = -(L.R_PCB + 1)

FREE, BLOCKED, SHARED = 0, -1, -2
DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
        (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
VIA_COST = 12.0
TURN_COST = 0.6


def to_idx(x, y):
    return int(round((x - X0) / G)), int(round((y - X0) / G))


def to_xy(i, j):
    return X0 + i * G, X0 + j * G


class Board:
    def __init__(self, path):
        self.b = pcbnew.LoadBoard(path)
        self.pads = []   # (x, y, r, netname)
        for fp in self.b.GetFootprints():
            for p in fp.Pads():
                pos = p.GetPosition()
                x, y = pcbnew.ToMM(pos.x) - OX, OY - pcbnew.ToMM(pos.y)
                s = p.GetSize()
                if p.GetShape() in (pcbnew.PAD_SHAPE_RECT, pcbnew.PAD_SHAPE_ROUNDRECT):
                    r = math.hypot(pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)) / 2   # corner of a rectangular pad
                else:
                    r = max(pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)) / 2
                self.pads.append((x, y, r, p.GetNetname() or "", fp.GetReference(), p.GetNumber(),
                                  p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH))
        self.nets = sorted({p[3] for p in self.pads if p[3]})
        self.net_id = {n: k + 1 for k, n in enumerate(self.nets)}

    def base_grid(self):
        occ = np.zeros((2, N, N), dtype=np.int32)
        ii, jj = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
        xx, yy = X0 + ii * G, X0 + jj * G
        rr = np.hypot(xx, yy)
        occ[:, rr > L.R_PCB - EDGE_CLR - TRACK_W / 2] = BLOCKED
        # chamber walls stand right under the PCB: no restriction for copper, only for parts
        for (x, y, r, net, ref, num, npth) in self.pads:
            nid = self.net_id.get(net, 0)
            infl = r + CLEARANCE + TRACK_W / 2
            mask = (xx - x) ** 2 + (yy - y) ** 2 <= infl ** 2
            for layer in (0, 1):
                cur = occ[layer]
                if nid == 0 or npth:
                    cur[mask] = BLOCKED
                else:
                    free = mask & (cur == FREE)
                    other = mask & (cur != FREE) & (cur != nid)
                    cur[free] = nid
                    cur[other] = SHARED
        # screw bosses press on the PCB underside: no copper under them (and none under the screw head)
        for (hx, hy) in L.HOLES:
            mask = (xx - hx) ** 2 + (yy - hy) ** 2 <= (L.BOSS_D / 2 + 0.3 + TRACK_W / 2) ** 2
            occ[:, mask] = BLOCKED
        # the pad centres themselves always belong to their net
        for (x, y, r, net, ref, num, npth) in self.pads:
            nid = self.net_id.get(net, 0)
            if nid:
                i, j = to_idx(x, y)
                core = int(math.ceil((r * 0.6) / G))
                for layer in (0, 1):
                    sl = occ[layer, i - core:i + core + 1, j - core:j + core + 1]
                    sl[(sl == SHARED)] = nid
                    occ[layer, i, j] = nid
        return occ


def mark_path(occ, cells, nid, vias):
    """Reserve copper of a finished path for its net (inflated by width + clearance)."""
    rad = TRACK_W + CLEARANCE
    k = int(math.ceil(rad / G))
    offs = [(di, dj) for di in range(-k, k + 1) for dj in range(-k, k + 1) if (di * G) ** 2 + (dj * G) ** 2 <= rad ** 2]
    vrad = VIA_D / 2 + CLEARANCE + TRACK_W / 2
    kv = int(math.ceil(vrad / G))
    voffs = [(di, dj) for di in range(-kv, kv + 1) for dj in range(-kv, kv + 1) if (di * G) ** 2 + (dj * G) ** 2 <= vrad ** 2]
    for (l, i, j) in cells:
        for di, dj in offs:
            a, b = i + di, j + dj
            if 0 <= a < N and 0 <= b < N:
                v = occ[l, a, b]
                if v == FREE:
                    occ[l, a, b] = nid
                elif v > 0 and v != nid:
                    occ[l, a, b] = SHARED
    for (i, j) in vias:
        for l in (0, 1):
            for di, dj in voffs:
                a, b = i + di, j + dj
                if 0 <= a < N and 0 <= b < N:
                    v = occ[l, a, b]
                    if v == FREE:
                        occ[l, a, b] = nid
                    elif v > 0 and v != nid:
                        occ[l, a, b] = SHARED


def via_ok(occ, i, j, nid):
    """A via needs its whole pad free (or own net) on both layers."""
    r = VIA_D / 2 - TRACK_W / 2   # the grid already holds the track inflation
    k = int(math.ceil(r / G))
    for l in (0, 1):
        sl = occ[l, max(0, i - k):i + k + 1, max(0, j - k):j + k + 1]
        if np.any((sl != FREE) & (sl != nid)):
            return False
    return True


def astar(occ, starts, goals, nid):
    """starts/goals: sets of (layer, i, j). Returns list of cells from a start to a goal."""
    gi = np.array([g[1] for g in goals])
    gj = np.array([g[2] for g in goals])

    def h(i, j):
        return float(np.min(np.hypot(gi - i, gj - j)))

    openh = []
    best = {}
    parent = {}
    for s in starts:
        state = (s[0], s[1], s[2], -1)
        best[state] = 0.0
        heapq.heappush(openh, (h(s[1], s[2]), 0.0, state))
    goalset = set(goals)
    hcache = {}
    while openh:
        f, g, st = heapq.heappop(openh)
        if best.get(st, 1e18) < g - 1e-9:
            continue
        l, i, j, d = st
        if (l, i, j) in goalset:
            path = [(l, i, j)]
            while st in parent:
                st = parent[st]
                path.append((st[0], st[1], st[2]))
            return path[::-1]
        for k, (di, dj, c) in enumerate(DIRS):
            a, b = i + di, j + dj
            if not (0 <= a < N and 0 <= b < N):
                continue
            v = occ[l, a, b]
            if v != FREE and v != nid:
                continue
            if di and dj:   # no corner cutting next to obstacles
                v1, v2 = occ[l, i + di, j], occ[l, i, j + dj]
                if (v1 != FREE and v1 != nid) or (v2 != FREE and v2 != nid):
                    continue
            ng = g + c + (TURN_COST if (d != -1 and d != k) else 0.0)
            ns = (l, a, b, k)
            if ng < best.get(ns, 1e18):
                best[ns] = ng
                parent[ns] = st
                key = (a, b)
                if key not in hcache:
                    hcache[key] = h(a, b)
                heapq.heappush(openh, (ng + hcache[key], ng, ns))
        # via
        ol = 1 - l
        if occ[ol, i, j] in (FREE, nid) and via_ok(occ, i, j, nid):
            ng = g + VIA_COST
            ns = (ol, i, j, -1)
            if ng < best.get(ns, 1e18):
                best[ns] = ng
                parent[ns] = st
                heapq.heappush(openh, (ng + hcache.get((i, j), h(i, j)), ng, ns))
    return None


def route_all(bd, order, seed):
    occ = bd.base_grid()
    result = {}   # net -> (cells list per connection, vias)
    for net in order:
        nid = bd.net_id[net]
        pads = [(x, y) for (x, y, r, n, ref, num, npth) in bd.pads if n == net]
        if len(pads) < 2:
            continue
        # connect pads in order of distance from the first one (Prim-like)
        remaining = pads[1:]
        tree_cells = set()
        i0, j0 = to_idx(*pads[0])
        tree_cells |= {(0, i0, j0), (1, i0, j0)}
        segs, vias = [], []
        while remaining:
            # nearest remaining pad to the tree
            tc = np.array([(c[1], c[2]) for c in tree_cells])
            dists = [np.min(np.hypot(tc[:, 0] - to_idx(*p)[0], tc[:, 1] - to_idx(*p)[1])) for p in remaining]
            k = int(np.argmin(dists))
            p = remaining.pop(k)
            i, j = to_idx(*p)
            path = astar(occ, {(0, i, j), (1, i, j)}, tree_cells, nid)
            if path is None:
                return None, net
            segs.append(path)
            for a, b in zip(path, path[1:]):
                if a[0] != b[0]:
                    vias.append((a[1], a[2]))
            tree_cells |= set(path)
            tree_cells |= {(0, i, j), (1, i, j)}
            mark_path(occ, path, nid, [v for v in vias])
        result[net] = (segs, vias)
    return result, None


def simplify(path):
    """Cells -> list of (layer, [(x, y), ...]) polylines with collinear points removed."""
    out = []
    cur_l, pts = path[0][0], [path[0][1:]]
    for c in path[1:]:
        if c[0] != cur_l:
            out.append((cur_l, pts))
            cur_l, pts = c[0], [c[1:]]
        else:
            pts.append(c[1:])
    out.append((cur_l, pts))
    res = []
    for l, p in out:
        if len(p) < 2:
            continue
        keep = [p[0]]
        for a, b, c in zip(p, p[1:], p[2:]):
            if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
                keep.append(b)
        keep.append(p[-1])
        res.append((l, keep))
    return res


def write(bd, result, out_path):
    b = bd.b
    nets = b.GetNetsByName()
    layer_of = {0: pcbnew.F_Cu, 1: pcbnew.B_Cu}
    pad_at = {to_idx(x, y): (x, y) for (x, y, r, n, ref, num, npth) in bd.pads}
    for net, (segs, vias) in result.items():
        ni = nets[net]
        for path in segs:
            for l, pts in simplify(path):
                xy = [to_xy(*q) for q in pts]
                # snap the ends onto the exact pad centres
                if tuple(pts[0]) in pad_at:
                    xy[0] = pad_at[tuple(pts[0])]
                if tuple(pts[-1]) in pad_at:
                    xy[-1] = pad_at[tuple(pts[-1])]
                for (x0, y0), (x1, y1) in zip(xy, xy[1:]):
                    t = pcbnew.PCB_TRACK(b)
                    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(OX + x0), pcbnew.FromMM(OY - y0)))
                    t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(OX + x1), pcbnew.FromMM(OY - y1)))
                    t.SetWidth(pcbnew.FromMM(TRACK_W))
                    t.SetLayer(layer_of[l])
                    t.SetNet(ni)
                    b.Add(t)
        for (i, j) in set(vias):
            x, y = to_xy(i, j)
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY - y)))
            v.SetWidth(pcbnew.FromMM(VIA_D))
            v.SetDrill(pcbnew.FromMM(VIA_DRILL))
            v.SetNet(ni)
            b.Add(v)
    ok = pcbnew.SaveBoard(out_path, b)
    print("saved", out_path, ok)


def main():
    bd = Board("out/carrier_unrouted.kicad_pcb")
    # signals first, then power, GND last (the pour then only adds copper)
    prio = ["SDA", "SCL", "RADAR_TX", "RADAR_RX", "PIR_OUT", "RADAR_OUT", "+3V3", "ESP_5V", "VIN_RAW", "VIN", "+5V", "GND"]
    order = [n for n in prio if n in bd.nets] + [n for n in bd.nets if n not in prio]
    rnd = random.Random(1)
    for attempt in range(30):
        result, failed = route_all(bd, order, attempt)
        if result is not None:
            print(f"routed all nets on attempt {attempt + 1}, order {order}")
            write(bd, result, "out/carrier_routed.kicad_pcb")
            return 0
        print(f"attempt {attempt + 1}: failed on {failed}")
        order.remove(failed)
        order.insert(0, failed)
        if attempt > 5:
            rest = order[1:]
            rnd.shuffle(rest)
            order = order[:1] + rest
    return 1


if __name__ == "__main__":
    sys.exit(main())
