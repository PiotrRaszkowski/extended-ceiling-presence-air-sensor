"""Dupont hub layout (SVG): 6 x 5 holes of 2.54 mm perfboard, male headers on the 4 middle columns.

Pins of the same net are bridged with solder on the back. Front = header side (faces into the
housing), back = solder side (faces the chamber wall), mirrored left to right.
Usage: python hub_layout.py dupont-hub.svg
"""
import sys

COLS, ROWS = 6, 5
# nets of the 4 middle columns, top row first, as seen from the FRONT (header side)
GRID = [["GND", "GND", "GND", "GND"],
        ["GND", "GND", "5V", "5V"],
        ["5V", "5V", "5V", "SDA"],
        ["SCL", "SCL", "SDA", "SDA"],
        ["SCL", None, None, None]]
COL = {"GND": "#212121", "5V": "#ef6c00", "SDA": "#1565c0", "SCL": "#b8860b"}
WHO = {"GND": "S09 OUT-, ESP GND, radar GND, PIR -, BH1750 GND, ENS160 GND (6)",
       "5V": "S09 OUT+, ESP 5V, radar VCC, PIR +, ENS160 VIN (5)",
       "SDA": "ESP GP1, BH1750 SDA, ENS160 SDA (3)",
       "SCL": "ESP GP2, BH1750 SCL, ENS160 SCL (3)"}
P = 46                       # px per 2.54 mm
W, HGT = 1500, 600
out = []
e = out.append


def text(x, y, s, size=15, anchor="middle", weight="400", col="#263238"):
    e(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{col}">{s}</text>')


def board(ox, oy, mirrored, title, sub):
    bw, bh = COLS * P, ROWS * P
    text(ox + bw / 2, oy - 46, title, 20, weight="700")
    text(ox + bw / 2, oy - 24, sub, 13, col="#607d8b")
    e(f'<rect x="{ox}" y="{oy}" width="{bw}" height="{bh}" rx="4" fill="#2e7d32"/>')
    # channel grip zones (outer columns)
    for cx in (ox, ox + bw - P):
        e(f'<rect x="{cx}" y="{oy}" width="{P}" height="{bh}" fill="#ffffff" fill-opacity="0.18"/>')
    pos = {}
    for r in range(ROWS):
        for c in range(COLS):
            x = ox + (c + 0.5) * P
            y = oy + (r + 0.5) * P
            net = None
            if 1 <= c <= 4:
                gc = c - 1 if not mirrored else 4 - c
                net = GRID[r][gc]
            pos[(r, c)] = (x, y, net)
    if mirrored:   # solder bridges on the back: link neighbours of the same net
        for (r, c), (x, y, net) in pos.items():
            if not net:
                continue
            for dr, dc in ((0, 1), (1, 0)):
                n2 = pos.get((r + dr, c + dc))
                if n2 and n2[2] == net:
                    e(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{n2[0]:.1f}" y2="{n2[1]:.1f}" stroke="{COL[net]}" stroke-width="16" stroke-linecap="round"/>')
    for (r, c), (x, y, net) in pos.items():
        e(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#d7ccc8" stroke="#bcaaa4"/>')
        e(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#3e2723"/>')
        if net:
            if not mirrored:
                e(f'<rect x="{x - P / 2 + 3:.1f}" y="{y - P / 2 + 3:.1f}" width="{P - 6}" height="{P - 6}" rx="4" fill="{COL[net]}" fill-opacity="0.92"/>')
                e(f'<rect x="{x - 4:.1f}" y="{y - 4:.1f}" width="8" height="8" fill="#ffd54f"/>')
                text(x, y + P / 2 - 7, net, 10, weight="700", col="#ffffff")
            else:
                e(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="{COL[net]}"/>')
    # edge labels
    text(ox + P / 2, oy + bh + 22, "grip", 12, col="#607d8b")
    text(ox + bw - P / 2, oy + bh + 22, "grip", 12, col="#607d8b")


e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HGT}" viewBox="0 0 {W} {HGT}" font-family="Inter, Segoe UI, Helvetica, Arial, sans-serif">')
e(f'<rect width="{W}" height="{HGT}" fill="#ffffff"/>')
text(W / 2, 40, "Dupont hub: 6 x 5 holes of perfboard, male headers on the 4 middle columns", 22, weight="700")
text(W / 2, 64, "board about 15.2 x 12.7 mm (cut through the next row/column of holes); the empty outer columns slide into the channels", 14, col="#607d8b")
board(150, 170, False, "Front: header side", "faces into the housing; plug the jumpers here")
board(640, 170, True, "Back: solder side (mirrored)", "faces the chamber wall; bridge same-colour pads with solder")
# legend
lx, ly = 1060, 190
text(lx, ly - 30, "Net -> what plugs in", 16, anchor="start", weight="700")
for i, net in enumerate(("GND", "5V", "SDA", "SCL")):
    y = ly + i * 64
    e(f'<rect x="{lx}" y="{y - 16}" width="56" height="26" rx="5" fill="{COL[net]}"/>')
    text(lx + 28, y + 2, net, 14, weight="700", col="#ffffff")
    words = WHO[net].split(", ")
    text(lx + 68, y - 2, ", ".join(words[:3]) + ("," if len(words) > 3 else ""), 13, anchor="start")
    if len(words) > 3:
        text(lx + 68, y + 16, ", ".join(words[3:]), 13, anchor="start")
notes = ["3V3 does not go through the hub: one jumper straight from the ESP 3V3 pin to BH1750 VCC.",
         "The top row points up when the board sits in the housing. Test every net for shorts to its neighbours with a meter before plugging in.",
         "One female-female Dupont jumper per module and net: GND 6, 5V 5, SDA 3, SCL 3 pins. The 3 empty holes are spare."]
for i, n in enumerate(notes):
    text(W / 2, HGT - 110 + i * 26, n, 14, col="#455a64")
e("</svg>")
open(sys.argv[1] if len(sys.argv) > 1 else "dupont-hub.svg", "w").write("\n".join(out))
print("ok")
