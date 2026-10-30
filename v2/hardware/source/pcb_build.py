"""
Builds the v2 carrier PCB (KiCad 7+ board file) from layout.py.

    python pcb_build.py place     -> out/carrier_unrouted.kicad_pcb (+ out/carrier.dsn for an external autorouter)
    python router.py              -> out/carrier_routed.kicad_pcb
    python pcb_build.py finish    -> pours GND on both layers, DRC, writes ../pcb/carrier.kicad_pcb

If you prefer Freerouting: route out/carrier.dsn, save out/carrier.ses and run
`python pcb_build.py finish ses` instead.
The board is placed on the KiCad canvas with the housing axis at (100, 100) mm;
KiCad's y axis points down, so y_kicad = 100 - y.
"""
import math
import os
import sys

import pcbnew

import layout as L

OX, OY = 100.0, 100.0
OUT = "out"
FPLIB = os.environ.get("KICAD_FOOTPRINTS", "/usr/share/kicad/footprints")


def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY - y))


def new_board():
    b = pcbnew.BOARD()
    ds = b.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    ds.m_TrackMinWidth = mm(0.2)
    ds.m_ViasMinSize = mm(0.6)
    ds.m_MinThroughDrill = mm(0.3)
    ds.m_MinClearance = mm(0.2)
    ds.m_CopperEdgeClearance = mm(0.4)
    nc = ds.m_NetSettings.m_DefaultNetClass
    nc.SetTrackWidth(mm(0.5))
    nc.SetClearance(mm(0.25))
    nc.SetViaDiameter(mm(0.8))
    nc.SetViaDrill(mm(0.4))
    return b


NETS = {}


def net(b, name):
    if name is None:
        return None
    if name not in NETS:
        n = pcbnew.NETINFO_ITEM(b, name)
        b.Add(n)
        NETS[name] = n
    return NETS[name]


def seg(fp, layer, x0, y0, x1, y1, w=0.12):
    s = pcbnew.FP_SHAPE(fp, pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(layer)
    s.SetWidth(mm(w))
    s.SetStart(pt(x0, y0))
    s.SetEnd(pt(x1, y1))
    s.SetLocalCoord()
    fp.Add(s)


def poly(fp, layer, pts, w=0.12):
    for i in range(len(pts)):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
        seg(fp, layer, x0, y0, x1, y1, w)


def circle(fp, layer, cx, cy, r, w=0.12):
    s = pcbnew.FP_SHAPE(fp, pcbnew.SHAPE_T_CIRCLE)
    s.SetLayer(layer)
    s.SetWidth(mm(w))
    s.SetStart(pt(cx, cy))
    s.SetEnd(pt(cx + r, cy))
    s.SetLocalCoord()
    fp.Add(s)


def text(fp, layer, s, x, y, size=0.8, mirrored=True, angle=0.0):
    t = pcbnew.FP_TEXT(fp)
    t.SetText(s)
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * 0.15))
    t.SetMirrored(mirrored)
    t.SetPosition(pt(x, y))
    t.SetTextAngle(pcbnew.EDA_ANGLE(angle, pcbnew.DEGREES_T))
    t.SetLocalCoord()
    fp.Add(t)


def module_fp(b, key, m):
    """Footprint for a plug-in module: its socket pads + the module outline on the bottom side."""
    fp = pcbnew.FOOTPRINT(b)
    fp.SetFPID(pcbnew.LIB_ID("ceiling_v2", "Module_" + key))
    fp.SetPosition(pt(m["cx"], m["cy"]))
    fp.SetLayer(pcbnew.B_Cu)
    fp.SetReference(m["ref"])
    fp.SetValue(m["label"])
    fp.Reference().SetLayer(pcbnew.B_SilkS)
    fp.Reference().SetMirrored(True)
    fp.Reference().SetVisible(False)
    fp.Value().SetLayer(pcbnew.B_Fab)
    fp.Value().SetMirrored(True)
    b.Add(fp)
    num = 0
    for row_ref, pins in m["rows"]:
        for i, (name, lx, ly, netname) in enumerate(pins):
            num += 1
            x, y = L.place(m, lx, ly)
            p = pcbnew.PAD(fp)
            p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            p.SetShape(pcbnew.PAD_SHAPE_RECT if i == 0 else pcbnew.PAD_SHAPE_CIRCLE)
            p.SetSize(pcbnew.VECTOR2I(mm(1.7), mm(1.7)))
            p.SetDrillSize(pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
            p.SetLayerSet(p.PTHMask())
            p.SetNumber(str(num))
            p.SetPinFunction(name)
            fp.Add(p)
            p.SetPosition(pt(x, y))
            p.SetLocalCoord()
            n = net(b, netname)
            if n is not None:
                p.SetNet(n)
            # pin name next to the pad (bottom silkscreen, readable from below)
            dx, dy = x - m["cx"], y - m["cy"]
            d = math.hypot(dx, dy) or 1.0
            text(fp, pcbnew.B_SilkS, name, x + 2.6 * dx / d, y + 2.6 * dy / d, size=0.8)
    # module outline: Fab = board, courtyard = board + 0.5 (module hangs below the sockets)
    if m.get("round"):
        r = m["body"][0] / 2
        circle(fp, pcbnew.B_Fab, m["cx"], m["cy"], r)
        circle(fp, pcbnew.B_CrtYd, m["cx"], m["cy"], r + 0.5, 0.05)
    else:
        poly(fp, pcbnew.B_Fab, L.module_outline(m))
        poly(fp, pcbnew.B_CrtYd, L.module_outline(m, 0.5), 0.05)
    lx, ly = (0.0, 0.0)
    text(fp, pcbnew.B_SilkS, m["label"], *L.place(m, lx, ly), size=1.0,
         angle=(m["rot"] if m["rot"] in (0.0, 90.0) else 0.0))
    return fp


def lib_fp(b, ref, d):
    lib, name = d["fp"].split(":")
    fp = pcbnew.FootprintLoad(os.path.join(FPLIB, lib + ".pretty"), name)
    fp.SetReference(ref)
    fp.SetValue(d["value"])
    b.Add(fp)
    fp.Reference().SetLayer(pcbnew.F_Fab)
    if d["side"] == "B":
        fp.Flip(fp.GetPosition(), False)
    fp.SetOrientationDegrees(d["rot"])
    fp.SetPosition(pt(d["x"], d["y"]))
    for p in fp.Pads():
        n = net(b, d["pads"].get(p.GetNumber()))
        if n is not None:
            p.SetNet(n)
    return fp


def hole_fp(b, i, x, y):
    fp = pcbnew.FootprintLoad(os.path.join(FPLIB, "MountingHole.pretty"), "MountingHole_2.2mm_M2")
    fp.SetReference(f"H{i}")
    fp.SetValue("M2 to housing boss")
    b.Add(fp)
    fp.SetPosition(pt(x, y))
    # the housing boss under the PCB: keep everything on the underside away from it
    circle(fp, pcbnew.B_CrtYd, x, y, L.BOSS_D / 2 + 0.3, 0.05)
    circle(fp, pcbnew.B_Fab, x, y, L.BOSS_D / 2)
    return fp


def chamber_fp(b):
    """Footprint that only marks the ENS160 chamber walls under the PCB (courtyard + fab)."""
    c = L.CHAMBER
    fp = pcbnew.FOOTPRINT(b)
    fp.SetFPID(pcbnew.LIB_ID("ceiling_v2", "ChamberWalls"))
    fp.SetPosition(pt(c["x0"], 0))
    fp.SetLayer(pcbnew.B_Cu)
    fp.SetReference("CH1")
    fp.SetValue("ENS160 chamber walls (housing)")
    fp.Reference().SetVisible(False)
    fp.Reference().SetLayer(pcbnew.B_Fab)
    fp.Value().SetLayer(pcbnew.B_Fab)
    b.Add(fp)
    t = 1.2 + 0.3
    yh = c["y_half"]
    xr = math.sqrt(L.R_PCB ** 2 - (yh + t) ** 2)
    # walls as one U-shaped courtyard (open towards the housing wall)
    x0 = c["x0"]
    poly(fp, pcbnew.B_CrtYd, [(x0 - t, -yh - t), (xr, -yh - t), (xr, -yh), (x0, -yh), (x0, yh), (xr, yh),
                              (xr, yh + t), (x0 - t, yh + t)], 0.05)
    poly(fp, pcbnew.B_Fab, [(c["x0"] - 1.2, -yh - 1.2), (xr, -yh - 1.2), (xr, yh + 1.2), (c["x0"] - 1.2, yh + 1.2)], 0.15)
    text(fp, pcbnew.B_SilkS, "AIR CHAMBER - no copper pour", c["x0"] + 10, yh - 2.0, size=0.8)
    return fp


def pocket_fp(b):
    """Marks the housing walls around the SHT40 pocket (courtyard + fab), like the chamber."""
    k = L.POCKET
    fp = pcbnew.FOOTPRINT(b)
    fp.SetFPID(pcbnew.LIB_ID("ceiling_v2", "PocketWalls"))
    fp.SetPosition(pt(k["cx"], k["cy"]))
    fp.SetLayer(pcbnew.B_Cu)
    fp.SetReference("CH2")
    fp.SetValue("SHT40 pocket walls (housing)")
    fp.Reference().SetVisible(False)
    fp.Reference().SetLayer(pcbnew.B_Fab)
    fp.Value().SetLayer(pcbnew.B_Fab)
    b.Add(fp)
    x0, x1 = k["cx"] - k["ix"] / 2, k["cx"] + k["ix"] / 2
    y0, y1 = k["cy"] - k["iy"] / 2, k["cy"] + k["iy"] / 2
    t = 1.5
    # four wall strips as separate closed courtyards
    for (a, bb, c, d) in ((x0 - t, y0 - t, x1 + t, y0), (x0 - t, y1, x1 + t, y1 + t),
                          (x0 - t, y0 + 0.1, x0, y1 - 0.1), (x1, y0 + 0.1, x1 + t, y1 - 0.1)):   # strips must not touch
        poly(fp, pcbnew.B_CrtYd, [(a, bb), (c, bb), (c, d), (a, d)], 0.05)
    poly(fp, pcbnew.B_Fab, [(x0 - 1.2, y0 - 1.2), (x1 + 1.2, y0 - 1.2), (x1 + 1.2, y1 + 1.2), (x0 - 1.2, y1 + 1.2)], 0.15)
    return fp


def outline(b):
    s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_CIRCLE)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    s.SetStart(pt(0, 0))
    s.SetEnd(pt(L.R_PCB, 0))
    b.Add(s)


def board_text(b, s, x, y, layer, size=1.2, mirrored=False):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s)
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * 0.15))
    t.SetMirrored(mirrored)
    t.SetPosition(pt(x, y))
    b.Add(t)


def zone(b, layer, netname=None, rule_area=False, pts=None, priority=0):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    if pts is None:   # circle approximated by a polygon
        pts = [(L.R_PCB * math.cos(2 * math.pi * i / 72), L.R_PCB * math.sin(2 * math.pi * i / 72)) for i in range(72)]
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(mm(OX + x), mm(OY - y))
    if rule_area:
        z.SetIsRuleArea(True)
        z.SetDoNotAllowCopperPour(True)
        z.SetDoNotAllowVias(False)
        z.SetDoNotAllowTracks(False)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
    else:
        z.SetNet(NETS[netname])
        z.SetLocalClearance(mm(0.3))
        z.SetMinThickness(mm(0.25))
        z.SetThermalReliefGap(mm(0.4))
        z.SetThermalReliefSpokeWidth(mm(0.5))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetAssignedPriority(priority)
    b.Add(z)
    return z


def place():
    os.makedirs(OUT, exist_ok=True)
    b = new_board()
    outline(b)
    for k, m in L.MODULES.items():
        module_fp(b, k, m)
    for ref, d in L.PARTS.items():
        lib_fp(b, ref, d)
    for i, (x, y) in enumerate(L.HOLES, 1):
        hole_fp(b, i, x, y)
    chamber_fp(b)
    pocket_fp(b)
    board_text(b, "CEILING SENSOR v2", 22.0, -27.0, pcbnew.F_SilkS, 1.5)
    board_text(b, "PCB rev A  2026-10", 22.0, -30.0, pcbnew.F_SilkS, 1.0)
    board_text(b, "modules plug in from this side", 18.0, -30.0, pcbnew.B_SilkS, 1.0, mirrored=True)
    j1 = L.PARTS["J1"]
    board_text(b, "+12V", j1["x"] - 4.2, j1["y"], pcbnew.F_SilkS, 1.0)
    board_text(b, "GND", j1["x"] - 4.0, j1["y"] + 2.5, pcbnew.F_SilkS, 1.0)
    pcbnew.SaveBoard(os.path.join(OUT, "carrier_unrouted.kicad_pcb"), b)
    pcbnew.ExportSpecctraDSN(b, os.path.join(OUT, "carrier.dsn"))
    return b


def finish(src="router"):
    if src == "ses":
        b = pcbnew.LoadBoard(os.path.join(OUT, "carrier_unrouted.kicad_pcb"))
        print("SES import:", pcbnew.ImportSpecctraSES(b, os.path.join(OUT, "carrier.ses")))
    else:
        b = pcbnew.LoadBoard(os.path.join(OUT, "carrier_routed.kicad_pcb"))
    for n in b.GetNetsByName().values():
        NETS[str(n.GetNetname())] = n
    zone(b, pcbnew.F_Cu, "GND", priority=0)
    zone(b, pcbnew.B_Cu, "GND", priority=0)
    c = L.CHAMBER
    pts = [(c["x0"] - 1.5, -c["y_half"] - 1.5), (L.R_PCB + 1, -c["y_half"] - 1.5),
           (L.R_PCB + 1, c["y_half"] + 1.5), (c["x0"] - 1.5, c["y_half"] + 1.5)]
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone(b, layer, rule_area=True, pts=pts)
    # no pour above the SHT40 pocket either: keeps the room sensor away from the board's warmth
    k = L.POCKET
    pk = [(k["cx"] - k["ix"] / 2 - 1.2, k["cy"] - k["iy"] / 2 - 1.2), (k["cx"] + k["ix"] / 2 + 1.2, k["cy"] - k["iy"] / 2 - 1.2),
          (k["cx"] + k["ix"] / 2 + 1.2, k["cy"] + k["iy"] / 2 + 1.2), (k["cx"] - k["ix"] / 2 - 1.2, k["cy"] + k["iy"] / 2 + 1.2)]
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone(b, layer, rule_area=True, pts=pk)
    # no pour above the ESP32-S3-Zero's antenna end (the board hangs ~11 mm below the PCB)
    e = L.MODULES["ESP"]
    sx, sy = e["body"]
    ant = [L.place(e, x, y) for x, y in ((-sx / 2 - 1, -sy / 2 - 1), (sx / 2 + 1, -sy / 2 - 1),
                                          (sx / 2 + 1, -sy / 2 + e["antenna"]), (-sx / 2 - 1, -sy / 2 + e["antenna"]))]
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone(b, layer, rule_area=True, pts=ant)
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    os.makedirs("../pcb", exist_ok=True)
    path = "../pcb/carrier.kicad_pcb"
    import re
    for _ in range(3):
        pcbnew.WriteDRCReport(b, os.path.join(OUT, "drc.rpt"), pcbnew.EDA_UNITS_MILLIMETRES, True)
        blocks = re.split(r"\n(?=\[)", open(os.path.join(OUT, "drc.rpt")).read())
        starved = [m.groups() for bl in blocks if bl.startswith("[starved_thermal]")
                   for m in [re.search(r"PTH pad (\S+) \[GND\] of (\S+)", bl)] if m]
        if not starved:
            break
        # a track blocks one spoke: connect that pad to the pour without a thermal relief
        for num, ref in starved:
            for p in b.FindFootprintByReference(ref).Pads():
                if p.GetNumber() == num:
                    p.SetZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
                    print("full zone connection:", ref, num)
        filler.Fill(b.Zones())
    pcbnew.SaveBoard(path, b)
    import collections
    import re
    rpt = open(os.path.join(OUT, "drc.rpt")).read()
    kinds = collections.Counter(re.findall(r"\n\[(\w+)\]", rpt))
    print(re.findall(r"\*\* Found \d+ [^\n]*", rpt), dict(kinds))


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "place"
    if step == "place":
        place()
    else:
        finish(sys.argv[2] if len(sys.argv) > 2 else "router")
