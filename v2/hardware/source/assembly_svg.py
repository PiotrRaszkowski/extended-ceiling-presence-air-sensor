"""
Assembly drawing of the v2 carrier PCB, generated from layout.py and the routed board.

    python assembly_svg.py ../../docs/images/v2-assembly-bottom.svg bottom
    python assembly_svg.py ../../docs/images/v2-assembly-top.svg top

"bottom" = the side the modules plug into, drawn as you see it when you hold the board
with that side towards you (mirrored compared with the ceiling view).
"""
import math
import sys

import pcbnew

import layout as L

S = 9.0          # px per mm
PAD = 70
W = H = int(2 * L.R_PCB * S + 2 * PAD)
COL = {"RADAR": "#1565c0", "ESP": "#263238", "PIR": "#8d6e63", "BH": "#0d47a1", "ENS": "#7b1fa2", "SCD": "#00838f"}
out = []
e = out.append


def main(path, side):
    mir = -1 if side == "bottom" else 1

    def P(x, y):
        return W / 2 + mir * x * S, H / 2 - y * S

    def t(x, y, s, size=13, anchor="middle", weight="600", col="#263238"):
        e(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{col}" '
          f'font-family="system-ui,Segoe UI,sans-serif" paint-order="stroke" stroke="#ffffff" stroke-width="3">{s}</text>')

    e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H + 60}" viewBox="0 0 {W} {H + 60}">')
    e(f'<rect width="{W}" height="{H + 60}" fill="#ffffff"/>')
    cx, cy = P(0, 0)
    e(f'<circle cx="{cx}" cy="{cy}" r="{L.R_PCB * S}" fill="#e8f5e9" stroke="#2e7d32" stroke-width="3"/>')
    title = ("Underside (modules plug in here), seen from below" if side == "bottom"
             else "Top side (towards the ceiling), seen from above")
    t(W / 2, 32, title, 18, weight="700")

    # chamber
    ch = L.CHAMBER
    x0, y0 = P(ch["x0"] - 1.2, ch["y_half"] + 1.2)
    x1, y1 = P(math.sqrt(L.R_PCB ** 2 - (ch["y_half"] + 1.2) ** 2), -ch["y_half"] - 1.2)
    e(f'<rect x="{min(x0, x1)}" y="{y0}" width="{abs(x1 - x0)}" height="{y1 - y0}" fill="none" stroke="#9e9e9e" '
      f'stroke-width="2" stroke-dasharray="8 5"/>')
    lx, ly = P(ch["x0"] + 12, ch["y_half"] - 1.5)
    t(lx, ly, "air chamber walls (housing)", 12, col="#757575", weight="500")

    b = pcbnew.LoadBoard("../pcb/carrier.kicad_pcb")
    fps = {f.GetReference(): f for f in b.GetFootprints()}

    if side == "bottom":
        for k, m in L.MODULES.items():
            pts = [P(x, y) for x, y in L.module_outline(m)]
            c = COL[k]
            if m.get("round"):
                mx, my = P(m["cx"], m["cy"])
                e(f'<circle cx="{mx}" cy="{my}" r="{m["body"][0] / 2 * S}" fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-width="2.5"/>')
            else:
                e('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="{c}" fill-opacity="0.12" '
                  f'stroke="{c}" stroke-width="2.5"/>')
            mx, my = P(m["cx"], m["cy"])
            t(mx, my - 4, f'{m["ref"]} {m["label"]}', 14, col=c, weight="700")
            for (kk, row, i, n, x, y, net) in L.all_pins():
                if kk != k:
                    continue
                px, py = P(x, y)
                e(f'<rect x="{px - 6}" y="{py - 6}" width="12" height="12" rx="2" fill="#212121"/>')
                e(f'<circle cx="{px}" cy="{py}" r="2.6" fill="#ffd54f"/>')
                dx, dy = px - mx, py - my
                d = math.hypot(dx, dy) or 1
                t(px + 15 * dx / d, py + 15 * dy / d + 4, n, 10.5, col="#37474f")
        hint = {"U1": "square pad = pin 1 = VIN", "D1": "stripe = cathode", "D2": "stripe = cathode",
                "C1": "+ marked pad", "C2": "+ marked pad", "C3": "+ (only with SCD4x)", "J2": "not fitted"}
        for ref, d in L.PARTS.items():
            if d["side"] != "B":
                continue
            f = fps[ref]
            pads = [(pcbnew.ToMM(p.GetPosition().x) - 100, 100 - pcbnew.ToMM(p.GetPosition().y), p.GetNumber()) for p in f.Pads()]
            for (x, y, num) in pads:
                px, py = P(x, y)
                sq = num == "1"
                e(f'<{"rect" if sq else "circle"} ' + (f'x="{px - 7}" y="{py - 7}" width="14" height="14"' if sq else
                                                     f'cx="{px}" cy="{py}" r="7"') + ' fill="#bdbdbd" stroke="#424242" stroke-width="1.5"/>')
            ax = sum(p[0] for p in pads) / len(pads)
            ay = sum(p[1] for p in pads) / len(pads)
            px, py = P(ax, ay)
            short = d["value"].split(" (")[0].split(" /")[0]
            t(px, py - 12, f"{ref} {short}", 12, col="#bf360c", weight="700")
            if ref in hint:
                t(px, py + 22, hint[ref], 10.5, col="#6d4c41", weight="500")
            if ref in ("D1", "D2"):   # cathode bar next to pad 1
                x1p, y1p = P(*pads[0][:2])
                e(f'<rect x="{x1p + mir * 10 - 3}" y="{y1p - 9}" width="6" height="18" fill="#424242"/>')
    else:
        j1 = L.PARTS["J1"]
        f = fps["J1"]
        for p in f.Pads():
            x, y = pcbnew.ToMM(p.GetPosition().x) - 100, 100 - pcbnew.ToMM(p.GetPosition().y)
            px, py = P(x, y)
            e(f'<circle cx="{px}" cy="{py}" r="7" fill="#bdbdbd" stroke="#424242"/>')
            t(px - 14, py + 5, "+12V" if p.GetNumber() == "1" else "GND", 13, anchor="end",
              col="#b71c1c" if p.GetNumber() == "1" else "#212121")
        for ref in ("JP1", "JP2"):
            fj = fps[ref]
            xy = [(pcbnew.ToMM(q.GetPosition().x) - 100, 100 - pcbnew.ToMM(q.GetPosition().y)) for q in fj.Pads()]
            for (x, y) in xy:
                px, py = P(x, y)
                e(f'<circle cx="{px}" cy="{py}" r="7" fill="#ffd54f" stroke="#424242"/>')
            px, py = P(sum(q[0] for q in xy) / 2, sum(q[1] for q in xy) / 2)
            t(px + 60, py + 4, f"{ref} " + ("ADD" if ref == "JP1" else "CS") + " strap (open)", 11, col="#6d4c41", anchor="start")
        bb = f.GetBoundingBox(False, False)
        x0, y0 = P(pcbnew.ToMM(bb.GetLeft()) - 100, 100 - pcbnew.ToMM(bb.GetTop()))
        x1, y1 = P(pcbnew.ToMM(bb.GetRight()) - 100, 100 - pcbnew.ToMM(bb.GetBottom()))
        e(f'<rect x="{min(x0, x1)}" y="{min(y0, y1)}" width="{abs(x1 - x0)}" height="{abs(y1 - y0)}" fill="#fafafa" '
          f'fill-opacity="0.6" stroke="#616161" stroke-width="2"/>')
        ax0, ay0 = P(j1["x"] + 10.5, j1["y"] + 1.25)
        ax1, ay1 = P(j1["x"] + 18.0, j1["y"] + 1.25)
        e(f'<line x1="{ax1}" y1="{ay1}" x2="{ax0 + 8}" y2="{ay0}" stroke="#bf360c" stroke-width="3"/>'
          f'<path d="M{ax0} {ay0} l12 -7 v14 z" fill="#bf360c"/>')
        px, py = P(j1["x"] + 4.5, j1["y"] + 7.5)
        t(px, py, "J1 JST-XH, plug goes in from the right", 13, col="#bf360c", weight="700")
        t(W / 2, H / 2 + 200, "Only J1 goes on this side. Everything else is soldered here", 13, col="#455a64", weight="500")
        t(W / 2, H / 2 + 218, "but sits on the underside. Trim the pin ends to about 1.5 mm.", 13, col="#455a64", weight="500")
    for i, (hx, hy) in enumerate(L.HOLES, 1):
        px, py = P(hx, hy)
        e(f'<circle cx="{px}" cy="{py}" r="{L.BOSS_D / 2 * S}" fill="none" stroke="#9e9e9e" stroke-width="2" stroke-dasharray="4 3"/>')
        e(f'<circle cx="{px}" cy="{py}" r="{L.HOLE_D / 2 * S}" fill="#ffffff" stroke="#212121" stroke-width="2"/>')
        t(px, py + L.BOSS_D / 2 * S + 16, f"M2 screw", 11, col="#616161", weight="500")
    t(W / 2, H + 40, "Generated from v2/hardware/source/layout.py and pcb/carrier.kicad_pcb.", 12, col="#90a4ae", weight="400")
    e("</svg>")
    open(path, "w").write("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "bottom")
