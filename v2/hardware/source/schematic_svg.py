"""
Schematic of the v2 carrier PCB as an SVG, generated from layout.py (the same data the
PCB is built from, so the picture cannot drift from the board).

    python schematic_svg.py ../../docs/images/v2-schematic.svg
"""
import sys

import layout as L

NET_COL = {"GND": "#212121", "+5V": "#ef6c00", "ESP_5V": "#f9a825", "+3V3": "#c2185b", "VIN": "#b71c1c",
           "VIN_RAW": "#b71c1c", "SDA": "#1565c0", "SCL": "#b8860b", "RADAR_TX": "#2e7d32",
           "RADAR_RX": "#6a1b9a", "PIR_OUT": "#795548", "RADAR_OUT": "#00838f"}
NET_TXT = {"VIN_RAW": "+12V IN", "VIN": "+12V (after D1)", "ESP_5V": "ESP 5V (after D2)", "ENS_3V3": "ENS 3V3 out",
           "ENS_ADD": "ENS ADD", "ENS_CS": "ENS CS"}

out = []
e = out.append


def t(x, y, s, size=14, anchor="start", weight="400", col="#263238"):
    e(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
      f'fill="{col}" font-family="system-ui,Segoe UI,sans-serif">{s}</text>')


def label(x, y, net, right=True):
    """Net label (flag) at the end of a pin stub."""
    if net is None:
        t(x + (6 if right else -6), y + 5, "n.c.", 12, "start" if right else "end", col="#90a4ae")
        return
    col = NET_COL.get(net, "#455a64")
    s = NET_TXT.get(net, net)
    w = 9 + 7.6 * len(s)
    if right:
        e(f'<path d="M{x} {y} l8 -10 h{w} v20 h-{w} z" fill="{col}"/>')
        t(x + 11, y + 5, s, 12.5, weight="700", col="#fff")
    else:
        e(f'<path d="M{x} {y} l-8 -10 h-{w} v20 h{w} z" fill="{col}"/>')
        t(x - 11, y + 5, s, 12.5, "end", weight="700", col="#fff")


def block(x, y, title, sub, pins_left, pins_right, w=150):
    """pins_*: [(pin name, net)]"""
    n = max(len(pins_left), len(pins_right))
    h = 36 + n * 24 + 10
    e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#eceff1" stroke="#455a64" stroke-width="2"/>')
    t(x + w / 2, y - 22, title, 16, "middle", "700")
    t(x + w / 2, y - 6, sub, 12, "middle", col="#607d8b")
    for i, (p, net) in enumerate(pins_left):
        yy = y + 36 + i * 24
        e(f'<line x1="{x - 26}" y1="{yy}" x2="{x}" y2="{yy}" stroke="#455a64" stroke-width="2"/>')
        t(x + 8, yy + 5, p, 13, weight="600")
        label(x - 26, yy, net, right=False)
    for i, (p, net) in enumerate(pins_right):
        yy = y + 36 + i * 24
        e(f'<line x1="{x + w}" y1="{yy}" x2="{x + w + 26}" y2="{yy}" stroke="#455a64" stroke-width="2"/>')
        t(x + w - 8, yy + 5, p, 13, "end", weight="600")
        label(x + w + 26, yy, net, right=True)
    return h


def pins_of(key, row=None):
    m = L.MODULES[key]
    res = []
    for ref, pins in m["rows"]:
        if row is None or ref == row:
            res += [(n, net) for (n, _, _, net) in pins]
    return res


def two_pin(x, y, ref, val, net1, net2, kind):
    """Small vertical two-terminal symbol between two labels."""
    e(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + 70}" stroke="#455a64" stroke-width="2"/>')
    if kind == "C":
        e(f'<rect x="{x - 16}" y="{y + 30}" width="32" height="10" fill="#fff" stroke="none"/>')
        e(f'<line x1="{x - 15}" y1="{y + 30}" x2="{x + 15}" y2="{y + 30}" stroke="#455a64" stroke-width="3"/>')
        e(f'<path d="M{x - 15} {y + 42} q15 -8 30 0" fill="none" stroke="#455a64" stroke-width="3"/>')
        t(x - 22, y + 30, "+", 13, "end", "700")
    else:   # diode, cathode at the bottom
        e(f'<path d="M{x - 11} {y + 26} h22 l-11 16 z" fill="#455a64"/>')
        e(f'<line x1="{x - 11}" y1="{y + 43}" x2="{x + 11}" y2="{y + 43}" stroke="#455a64" stroke-width="3"/>')
    t(x + 18, y + 33, ref, 13, weight="700")
    t(x + 18, y + 49, val, 12, col="#607d8b")
    e(f'<circle cx="{x}" cy="{y}" r="3" fill="#455a64"/><circle cx="{x}" cy="{y + 70}" r="3" fill="#455a64"/>')
    label(x, y, net1)
    label(x, y + 70, net2)


def main(path):
    W, H = 1620, 1080
    e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    e(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    t(30, 40, "Ceiling sensor v2 - carrier PCB schematic", 24, weight="700")
    t(30, 64, "Generated from v2/hardware/source/layout.py. Pin names as printed on each module (the order in a box"
              " is not the physical order); items marked * must be checked against your boards (docs/verify.md).", 13, col="#607d8b")

    # power path
    t(30, 110, "Power", 18, weight="700")
    block(60, 150, "J1", "JST-XH, 12 V in", [], [("1", "VIN_RAW"), ("2", "GND")], w=110)
    two_pin(380, 140, "D1", "1N5819 (reverse polarity)", "VIN_RAW", "VIN", "D")
    block(170, 300, "U1", "K7805-1000R3 / R-78E5.0-1.0", [("VIN", "VIN"), ("GND", "GND")], [("VOUT", "+5V")], w=170)
    two_pin(720, 140, "C1", "10 µF 25 V", "VIN", "GND", "C")
    two_pin(720, 280, "C2", "220 µF 10 V", "+5V", "GND", "C")
    two_pin(430, 430, "D2", "1N5819 (USB + 12 V safe)", "+5V", "ESP_5V", "D")
    two_pin(720, 420, "C3", "47 µF 10 V (fit with SCD4x)", "+3V3", "GND", "C")

    # ESP
    esp_l = pins_of("ESP", "U2B")
    esp_r = pins_of("ESP", "U2A")
    block(1000, 140, "U2  ESP32-S3-Zero", "two 1x9 sockets", esp_l, esp_r, w=170)

    # modules
    block(180, 560, "U3  HLK-LD2412 *", "1x4 + 1x3 sockets", pins_of("RADAR", "U3A"), pins_of("RADAR", "U3B"), w=150)
    block(560, 560, "U4  HC-SR602 PIR *", "1x3 socket", [], pins_of("PIR"), w=150)
    block(1000, 560, "U5  GY-302 BH1750", "1x5 socket", [], pins_of("BH"), w=150)
    block(120, 790, "U6  ENS160 + AHT21 *", "1x8 socket, in the air chamber", [], pins_of("ENS"), w=150)
    block(560, 790, "U7  SCD40 / SCD41 *", "1x4 socket, optional", [], pins_of("SCD"), w=150)
    block(1000, 790, "J2  I2C expansion", "1x4 header, not fitted", [], [("1", "+3V3"), ("2", "GND"), ("3", "SDA"), ("4", "SCL")], w=150)
    block(1290, 820, "U8  GY-SHT40", "1x4 socket, room T/RH", [], pins_of("SHT"), w=150)
    block(1290, 560, "JP1", "ADD strap, open", [], [("1", "ENS_3V3"), ("2", "ENS_ADD")], w=70)
    block(1290, 700, "JP2", "CS strap, open", [], [("1", "ENS_3V3"), ("2", "ENS_CS")], w=70)

    t(30, H - 40, "Same-name labels are connected. n.c. = not connected. Radar 3V3 stays open: the LD2412 is fed"
                  " from 5 V only (5 V or 3V3, never both). I2C pull-ups are on the modules.", 13, col="#455a64")
    e("</svg>")
    open(path, "w").write("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "schematic.svg")
