"""Checks a board file against layout.py: every module pad at its position with its net.
    python check_board.py [board.kicad_pcb]   (default: out/carrier_unrouted.kicad_pcb)"""
import pcbnew, layout as L, sys
b = pcbnew.LoadBoard(sys.argv[1] if len(sys.argv)>1 else "out/carrier_unrouted.kicad_pcb")
fps = {f.GetReference(): f for f in b.GetFootprints()}
bad = 0
for k, m in L.MODULES.items():
    f = fps[m["ref"]]
    pads = sorted(f.Pads(), key=lambda p: int(p.GetNumber()))
    exp = [(x, y, n, net) for (kk, r, i, n, x, y, net) in L.all_pins() if kk == k]
    for p, (x, y, n, net) in zip(pads, exp):
        px, py = pcbnew.ToMM(p.GetPosition().x) - 100, 100 - pcbnew.ToMM(p.GetPosition().y)
        if abs(px - x) > 1e-3 or abs(py - y) > 1e-3 or (p.GetNetname() or None) != (net or None) and not (net is None and p.GetNetname()==""):
            bad += 1; print("MISMATCH", k, n, (px, py), (x, y), p.GetNetname(), net)
print("module pads checked, mismatches:", bad, " flipped:", {r: f.IsFlipped() for r, f in fps.items()})
for ref in L.PARTS:
    f = fps[ref]
    print(ref, f.IsFlipped(), [(p.GetNumber(), round(pcbnew.ToMM(p.GetPosition().x)-100,2), round(100-pcbnew.ToMM(p.GetPosition().y),2), p.GetNetname()) for p in f.Pads()])
pcbnew.WriteDRCReport(b, "out/drc_place.rpt", pcbnew.EDA_UNITS_MILLIMETRES, True)
import re
t = open("out/drc_place.rpt").read()
print(re.findall(r"\*\* Found \d+ [^\n]*", t))
for l in t.splitlines():
    if "courtyard" in l.lower() or "Courtyard" in l: print(l)
