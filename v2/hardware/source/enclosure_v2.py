"""
v2 housing (Ø100) for the carrier PCB. Parametric CadQuery model -> STL + STEP.

    python enclosure_v2.py     -> files in out/

The modules hang under the carrier PCB (see layout.py); the PCB rests on three screw
bosses and is held by three M2 self-tapping screws. The housing only has to give every
module its window and keep the ENS160 chamber closed. The ceiling base and the bayonet
are the v1 Ø100 parts, unchanged (the base is taken straight from the v1 model).

Parts:
  01_housing_v2          face down on the bed, no supports
  02_ceiling_base        same as v1 Ø100 (re-exported here for convenience)
  20_pcb_fit_template    1.6 mm printed stand-in for the PCB: pin holes + screw holes, to check
                         the module positions in your housing before you order PCBs
"""
import math
import os
import sys

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "hardware", "source"))
_argv = sys.argv
sys.argv = [sys.argv[0], "100"]   # the v1 model reads the housing size from argv
import enclosure as v1            # noqa: E402
sys.argv = _argv
import layout as L                # noqa: E402

OUT_DIR = "out"
box, cyl = v1.box, v1.cyl
R_OUT, R_IN, H, FACE, T = v1.R_OUT, v1.R_IN, v1.H, v1.FACE, 1.2
assert abs(H - L.H) < 1e-9 and abs(FACE - L.FACE) < 1e-9

RADAR_WIN_T = 3.7          # PETG in front of the radar (half wavelength, as v1)
CH_GAP = 0.3               # chamber walls stop this far under the PCB
SLOT_W = 1.6


def rot_box(cx, cy, z0, sx, sy, sz, a):
    return box(0, 0, z0, sx, sy, sz).rotate((0, 0, 0), (0, 0, 1), a).translate((cx, cy, 0))


def face_slots(cx, cy, n, length, pitch=3.2, w=SLOT_W, a=0.0):
    s = None
    for i in range(n):
        o = (i - (n - 1) / 2) * pitch
        dx, dy = -o * math.sin(math.radians(a)), o * math.cos(math.radians(a))
        b = rot_box(cx + dx, cy + dy, -1, length, w, FACE + 2, a)
        s = b if s is None else s.union(b)
    return s


def make_housing():
    c = cq.Workplane("XY").circle(R_OUT).extrude(H)
    c = c.faces("<Z").edges().chamfer(v1.EDGE_CHAMFER)
    c = c.cut(cyl(R_IN, FACE, H))

    # --- radar window: the face is 3.7 mm thick in front of the antenna -------------
    r = L.MODULES["RADAR"]
    (x0, y0), (x1, y1) = L.module_outline(r)[0], L.module_outline(r)[2]
    c = c.union(box((x0 + x1) / 2, (y0 + y1) / 2, FACE - 0.01, abs(x1 - x0) + 2.0, abs(y1 - y0) + 2.0,
                    RADAR_WIN_T - FACE + 0.01))
    # pockets under the two pin rows: the header tails stick out of the radar's front by ~2 mm
    for row_ref, pins in r["rows"]:
        pts = [L.place(r, lx, ly) for (_, lx, ly, _) in pins]
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        c = c.cut(box((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, FACE,
                      max(xs) - min(xs) + 3.0, max(ys) - min(ys) + 3.0, RADAR_WIN_T))

    # --- ENS160 chamber: closed box under the PCB, inlet grille in the face, outlet in the wall
    ch = L.CHAMBER
    zt = L.PCB_BOT - CH_GAP
    xin = ch["x0"]
    yh = ch["y_half"]
    walls = box(xin - T / 2, 0, FACE - 0.01, T, 2 * (yh + T), zt - FACE + 0.01)
    for s in (-1, 1):
        walls = walls.union(box((xin + R_OUT) / 2, s * (yh + T / 2), FACE - 0.01, R_OUT - xin, T, zt - FACE + 0.01))
    c = c.union(walls.intersect(cyl(R_IN + 0.5, 0, H)))
    c = c.cut(face_slots((xin + 42.0) / 2 + 1.0, 0, 7, 13.0, a=90.0))          # inlet: under the board
    c = c.cut(v1.radial_slots(range(-12, 13, 6), 11.0, 4.5, width=1.5))        # outlet: high in the wall

    # --- PCB supports: three screw bosses (with a web to the wall) and small ledges -----
    for (hx, hy) in L.HOLES:
        boss = cyl(L.BOSS_D / 2, FACE - 0.01, L.PCB_BOT - FACE + 0.01, hx, hy)
        a = math.degrees(math.atan2(hy, hx))
        rr = math.hypot(hx, hy)
        web = box((rr + R_IN) / 2, 0, FACE - 0.01, R_IN - rr + 0.5, 1.6, L.PCB_BOT - 2.0 - FACE) \
            .rotate((0, 0, 0), (0, 0, 1), a)
        c = c.union(boss).union(web)
        c = c.cut(cyl(0.8, L.PCB_BOT - 9.0, 10.0, hx, hy))       # pilot hole for an M2 self-tapping screw
    for a in (100.0, 135.0, 215.0, 290.0, 320.0):
        led = box((L.R_PCB - 1.0 + R_IN + 0.3) / 2, 0, L.PCB_BOT - 4.0, R_IN + 0.3 - (L.R_PCB - 1.0), 3.0, 4.0)
        # 45 deg underside so the ledge prints without support
        cham = cq.Workplane("XZ").polyline([(L.R_PCB - 1.01, L.PCB_BOT - 4.01), (R_IN + 0.5, L.PCB_BOT - 4.01),
                                             (R_IN + 0.5, L.PCB_BOT - 4.0 - (R_IN + 0.5 - L.R_PCB + 1.0))]).close() \
            .extrude(1.5, both=True)
        c = c.union(led.cut(cham).rotate((0, 0, 0), (0, 0, 1), a))

    # --- PIR: lens hole with a chamfer on the room side ------------------------------
    p = L.MODULES["PIR"]
    hole_r = (p["lens_d"] + 1.0) / 2
    c = c.cut(cyl(hole_r, -1, 6.0, p["cx"], p["cy"]))
    cone = cq.Workplane("XY").add(cq.Solid.makeCone(hole_r + 1.6, hole_r, 1.6, pnt=cq.Vector(p["cx"], p["cy"], -0.001),
                                                    dir=cq.Vector(0, 0, 1)))
    c = c.cut(cone)

    # --- BH1750: window under the sensor chip -----------------------------------------
    bh = L.MODULES["BH"]
    bx, by = L.place(bh, *bh["chip"])
    c = c.cut(box(bx, by, -1, 4.0, 6.0, FACE + 2))

    # --- ESP32 RGB LED: face thinned to 0.6 mm so the light shows through --------------
    e = L.MODULES["ESP"]
    lx, ly = L.place(e, *e["led"])
    c = c.cut(cyl(2.5, 0.6, FACE, lx, ly))

    # --- SHT40 pocket: walls up to the PCB, grille in the face -----------------------------
    k = L.POCKET
    zt = L.PCB_BOT - CH_GAP
    outer = box(k["cx"], k["cy"], FACE - 0.01, k["ix"] + 2 * T, k["iy"] + 2 * T, zt - FACE + 0.01)
    inner = box(k["cx"], k["cy"], FACE - 1, k["ix"], k["iy"], zt + 2)
    c = c.union(outer.cut(inner))
    c = c.cut(face_slots(k["cx"], k["cy"], 4, k["iy"] - 3.0, a=90.0))

    # --- SCD4x (option): grille under it and slots in the wall next to it -----------------
    scd = L.MODULES["SCD"]
    c = c.cut(face_slots(scd["cx"] + 2.0, scd["cy"], 4, 9.0, a=0.0))
    c = c.cut(v1.radial_slots(range(70, 103, 8), 3.5, 4.0))
    c = c.cut(v1.radial_slots(range(70, 103, 8), 10.5, 4.0))

    # --- electronics: grille under the power parts, slots on the -x side ----------------
    c = c.cut(face_slots(-11.0, -4.0, 4, 8.0, a=0.0))
    c = c.cut(v1.radial_slots(range(150, 211, 8), 3.5, 4.5))
    c = c.cut(v1.radial_slots(range(150, 211, 8), 10.5, 4.5))

    # --- bayonet pins + alignment marks (as v1) ------------------------------------------
    z_pin = H - v1.PIN_DEPTH - v1.PIN_HGT / 2
    for a in v1.PIN_ANGLES:
        pin = box(R_IN - v1.PIN_PROTRUDE / 2 + 0.25, 0, z_pin, v1.PIN_PROTRUDE + 0.5, v1.PIN_W, v1.PIN_HGT)
        c = c.union(pin.rotate((0, 0, 0), (0, 0, 1), a))
        mark = box(R_OUT, 0, H - 3.0, 1.6, 1.4, 4.0)
        c = c.cut(mark.rotate((0, 0, 0), (0, 0, 1), a))
    return c


# ----------------------------------------------------------------------------
# PCB stand-in (fit template) and dummies for the collision check
# ----------------------------------------------------------------------------
def pcb_disc(z0=None, t=L.PCB_T):
    z0 = L.PCB_BOT if z0 is None else z0
    d = cyl(L.R_PCB, z0, t)
    for (hx, hy) in L.HOLES:
        d = d.cut(cyl(L.HOLE_D / 2, z0 - 1, t + 2, hx, hy))
    return d


def make_template():
    """Printed 1.6 mm disc with a 1.3 mm hole at every socket pin and the three screw holes.
    Print it flat; it is the PCB seen from the top (labels are on the real board)."""
    d = pcb_disc(0.0)
    for (k, row, i, n, x, y, net) in L.all_pins():
        d = d.cut(cyl(0.65, -1, 4, x, y))
    return d


def socket_dummies():
    s = None
    for k, m in L.MODULES.items():
        for row_ref, pins in m["rows"]:
            xs = [L.place(m, lx, ly) for (_, lx, ly, _) in pins]
            cx = sum(x for x, _ in xs) / len(xs)
            cy = sum(y for _, y in xs) / len(xs)
            (ax, ay), (bx, by) = xs[0], xs[-1]
            length = math.hypot(bx - ax, by - ay) + 2.54
            a = math.degrees(math.atan2(by - ay, bx - ax)) if len(xs) > 1 else 0.0
            b = rot_box(cx, cy, L.SOCKET_FACE, length, 2.54, L.SOCKET_H - 0.01, a)
            s = b if s is None else s.union(b)
    return s


def module_dummies():
    """Module boards + what sticks out of them (lens, USB-C, SCD4x sensor)."""
    out = {}
    for k, m in L.MODULES.items():
        z0, z1 = L.module_z(m)
        sx, sy = m["body"]
        if m.get("round"):
            body = cyl(sx / 2, z0, z1 - z0, m["cx"], m["cy"])
        else:
            body = rot_box(m["cx"], m["cy"], z0, sx, sy, z1 - z0, m["rot"])
        if k == "PIR":
            body = body.union(cyl(m["lens_d"] / 2 - 0.3, z0 - 4.0, 4.0, m["cx"], m["cy"]))
        if k == "ESP":
            ux, uy = L.place(m, 0.0, sy / 2 - 3.6)
            body = body.union(box(ux, uy, z0 - m["below"], 9.0, 7.3, m["below"]))
        if k == "SCD":
            sxl, syl, ss, sh = m["sensor"]
            px, py = L.place(m, sxl, syl)
            body = body.union(box(px, py, z1, ss, ss, sh))
        if k == "RADAR":
            body = body.union(rot_box(m["cx"], m["cy"], z0 - 0.9, 6.0, 6.0, 0.9, m["rot"]))   # radar chip
        if k in ("BH", "SHT"):
            px, py = L.place(m, *m["chip"])
            body = body.union(box(px, py, z0 - 1.0, 3.0, 3.0, 1.0))
        # header plastic (between module and socket) and the header tails on the other side
        for row_ref, pins in m["rows"]:
            for (_, lx, ly, _) in pins:
                px, py = L.place(m, lx, ly)
                body = body.union(box(px, py, L.SOCKET_FACE - L.HEADER_PLASTIC, 2.54, 2.54, L.HEADER_PLASTIC))
                tail = L.HEADER_TAIL - m["thick"]
                body = body.union(box(px, py, z0 - tail, 0.64, 0.64, tail))
        out[k] = body
    return out


def part_dummies():
    """Power parts under the PCB (approximate bodies)."""
    pb = L.PCB_BOT
    d = {}
    u1 = L.PARTS["U1"]
    d["U1"] = box(u1["x"] + 2.54, u1["y"] - 2.2, pb - 10.5, 11.6, 7.6, 10.5)          # SIP-3 converter, standing
    for ref, dia in (("C1", 5.0), ("C2", 6.3), ("C3", 5.0)):
        p = L.PARTS[ref]
        pitch = 2.0 if dia == 5.0 else 2.5
        d[ref] = cyl(dia / 2, pb - 12.0, 12.0, p["x"] + pitch / 2, p["y"])
    for ref in ("D1", "D2"):
        p = L.PARTS[ref]
        d[ref] = box(p["x"] + 5.08, p["y"], pb - 3.2, 5.6, 2.8, 3.2)                       # DO-41 lying flat
    j1 = L.PARTS["J1"]
    # on the top side: right-angle header (rotated 90 deg: opening towards +x) plus the mated plug
    assert j1["rot"] == 90.0
    d["J1"] = box(j1["x"] + 7.6, j1["y"] + 1.25, L.PCB_TOP, 20.8, 8.5, 6.2)
    # M2 pan heads on the top side
    heads = None
    for (hx, hy) in L.HOLES:
        h = cyl(L.SCREW_HEAD_D / 2, L.PCB_TOP, 1.6, hx, hy)
        heads = h if heads is None else heads.union(h)
    d["screw_heads"] = heads
    # solder joints and trimmed pin tails on the top side (1.5 mm) of every through-hole pad
    tails = None
    for (k, row, i, n, x, y, net) in L.all_pins():
        t = cyl(0.9, L.PCB_TOP, 1.5, x, y)
        tails = t if tails is None else tails.union(t)
    d["top_pin_tails"] = tails
    return d


def volume(s):
    try:
        return s.val().Volume()
    except Exception:
        return 0.0


def check(housing, base_in_place):
    pcb = pcb_disc()
    socks = socket_dummies()
    mods = module_dummies()
    parts = part_dummies()
    items = {"PCB": pcb, "sockets": socks, **{"mod_" + k: v for k, v in mods.items()}, **parts}
    bad = 0
    for name, solid in items.items():
        v = volume(housing.intersect(solid))
        if v > 1e-3:
            print(f"  COLLISION housing x {name}: {v:.3f} mm3")
            bad += 1
        vb = volume(base_in_place.intersect(solid))
        if vb > 1e-3:
            print(f"  COLLISION base x {name}: {vb:.3f} mm3")
            bad += 1
    names = list(items)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if "PCB" in (a, b) and ({a, b} & {"sockets", "J1", "screw_heads", "top_pin_tails"}):
                continue   # these sit on the PCB
            if {a, b} == {"sockets", "top_pin_tails"} or {a, b} == {"screw_heads", "top_pin_tails"}:
                continue
            v = volume(items[a].intersect(items[b]))
            if v > 1e-3:
                print(f"  COLLISION {a} x {b}: {v:.3f} mm3")
                bad += 1
    print("collisions:", bad)
    return bad, items


def base_in_housing(base, angle=0.0):
    """Base in its mounted position (ceiling side up), turned by `angle` degrees."""
    return base.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, H)).rotate((0, 0, 0), (0, 0, 1), angle)


def export(shape, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    cq.exporters.export(shape, os.path.join(OUT_DIR, name + ".stl"), tolerance=0.02, angularTolerance=0.1)
    cq.exporters.export(shape, os.path.join(OUT_DIR, name + ".step"))


if __name__ == "__main__":
    housing = make_housing()
    base = v1.make_base()
    template = make_template()
    export(housing, "01_housing_v2")
    export(base, "02_ceiling_base")
    export(template, "20_pcb_fit_template")
    bad = 0
    for ang in (0.0, v1.LOCK_ANGLE):
        print(f"base at {ang} deg:")
        b, items = check(housing, base_in_housing(base, ang))
        bad += b
    for k, v in items.items():
        cq.exporters.export(v, os.path.join(OUT_DIR, f"_dummy_{k}.stl"), tolerance=0.05)
    sys.exit(1 if bad else 0)
