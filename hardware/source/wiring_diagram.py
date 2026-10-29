"""Wiring diagram generator (SVG) for the extended ceiling presence + air sensor.

Usage: python wiring_diagram.py wiring.svg"""
import sys

W, HGT = 1560, 1000
C = dict(v12="#d32f2f", v5="#ef6c00", v33="#c2185b", gnd="#212121", sda="#1565c0", scl="#b8860b",
         tx="#2e7d32", rx="#6a1b9a", pir="#795548", box="#fafafa", line="#455a64", txt="#263238", nc="#9e9e9e")
RAIL = {"5V": 110, "3V3": 140, "GND": 170, "SDA": 205, "SCL": 235}
RAIL_COL = {"5V": C["v5"], "3V3": C["v33"], "GND": C["gnd"], "SDA": C["sda"], "SCL": C["scl"]}
RAIL_LBL = {"5V": "5 V (from S09)", "3V3": "3.3 V (from ESP)", "GND": "GND", "SDA": "I2C SDA", "SCL": "I2C SCL"}
TOP, BH = 290, 150          # block top, height
BOT = TOP + BH
LANES = {"TX": 505, "RX": 530, "PIR": 555}
LANE_COL = {"TX": C["tx"], "RX": C["rx"], "PIR": C["pir"]}

out = []
def e(s): out.append(s)
def text(x, y, s, size=13, anchor="middle", weight="400", col=None, italic=False):
    st = ' font-style="italic"' if italic else ""
    e(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{col or C["txt"]}"{st}>{s}</text>')
def line(x1, y1, x2, y2, col, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    e(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}/>')
def dot(x, y, col):
    e(f'<circle cx="{x}" cy="{y}" r="4.2" fill="{col}"/>')
def block(x, w, title, sub, y=TOP, h=BH, fill=None):
    e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill or C["box"]}" stroke="{C["line"]}" stroke-width="1.6"/>')
    text(x + w / 2, y + h / 2 + 2, title, 15, weight="700")
    for i, s in enumerate(sub):
        text(x + w / 2, y + h / 2 + 22 + i * 16, s, 11.5, col="#546e7a")

# ---------------------------------------------------------------- blocks
blocks = {
    "esp":  dict(x=300, w=230, title="ESP32-S3-Zero", sub=["Waveshare", "RGB LED: GPIO21 (on board)"]),
    "ld":   dict(x=590, w=170, title="HLK-LD2410B", sub=["radar 24 GHz", "antennas face down"]),
    "pir":  dict(x=800, w=140, title="HC-SR602", sub=["PIR mini", "OUT = 3.3 V (measure!)"]),
    "bh":   dict(x=985, w=175, title="BH1750", sub=["GY-302", "address 0x23"]),
    "ens":  dict(x=1200, w=200, title="ENS160 + AHT21", sub=["0x53 / 0x38", "3V3·ADD·CS·INT: leave open"]),
    "buck": dict(x=50, w=170, title="S09 converter", sub=["12 V → 5 V fixed", "EN bridged to IN+"]),
}
# top pins: (pin label, net); bottom pins: (label, signal lane)
top_pins = {
    "buck": [("OUT+", "5V"), ("OUT−", "GND")],
    "esp":  [("5V", "5V"), ("GND", "GND"), ("3V3", "3V3"), ("1", "SDA"), ("2", "SCL")],
    "ld":   [("VCC", "5V"), ("GND", "GND")],
    "pir":  [("+", "5V"), ("−", "GND")],
    "bh":   [("VCC", "3V3"), ("GND", "GND"), ("SCL", "SCL"), ("SDA", "SDA")],
    "ens":  [("VIN", "5V"), ("GND", "GND"), ("SCL", "SCL"), ("SDA", "SDA")],
}
bot_pins = {
    "esp": [("4", "TX"), ("5", "RX"), ("6", "PIR")],
    "ld":  [("RX", "TX"), ("TX", "RX"), ("OUT", None)],
    "pir": [("OUT", "PIR")],
}

def pin_xs(b, n):
    x, w = blocks[b]["x"], blocks[b]["w"]
    step = min(36, (w - 30) / max(n - 1, 1)) if n > 1 else 0
    start = x + w / 2 - step * (n - 1) / 2
    return [start + i * step for i in range(n)]

e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HGT}" viewBox="0 0 {W} {HGT}" font-family="Inter, Segoe UI, Helvetica, Arial, sans-serif">')
e(f'<rect width="{W}" height="{HGT}" fill="#ffffff"/>')
text(W / 2, 42, "Extended ceiling presence + air sensor: wiring diagram", 22, weight="700")
text(W / 2, 66, "all logic signals are 3.3 V · numbers on the ESP = GPIO (as printed on the board) · dot = connection, crossing without a dot = no connection", 12.5, col="#607d8b")

# ---------------------------------------------------------------- rails: x ranges
net_x = {k: [] for k in RAIL}
RAIL_LBL_X = 1425
pinpos = {}
for b, pins in top_pins.items():
    for (lbl, net), x in zip(pins, pin_xs(b, len(pins))):
        net_x[net].append(x); pinpos[(b, lbl)] = x
for net, y in RAIL.items():
    xs = net_x[net]
    x0, x1 = min(xs), max(xs)
    line(x0 - (0 if net in ("5V", "GND") else 0), y, x1, y, RAIL_COL[net], 3.2)
    text(RAIL_LBL_X, y + 4.5, RAIL_LBL[net], 12.5, anchor="start", weight="600", col=RAIL_COL[net])

# vertical drops from pins to rails
for b, pins in top_pins.items():
    for (lbl, net), x in zip(pins, pin_xs(b, len(pins))):
        y = RAIL[net]
        line(x, TOP, x, y, RAIL_COL[net], 2.4)
        xs = net_x[net]
        if len(xs) > 1:
            dot(x, y, RAIL_COL[net])
        text(x, TOP + 16, lbl, 11.5, weight="700")

# ---------------------------------------------------------------- signal lanes below
lane_x = {k: [] for k in LANES}
LANE_LBL_X = 900
for b, pins in bot_pins.items():
    for (lbl, ln), x in zip(pins, pin_xs(b, len(pins))):
        text(x, BOT - 7, lbl, 11.5, weight="700")
        if ln is None:
            line(x, BOT, x, BOT + 22, C["nc"], 2, dash="3 3")
            text(x, BOT + 36, "n.c.", 11, col=C["nc"], italic=True)
            continue
        line(x, BOT, x, LANES[ln], LANE_COL[ln], 2.4)
        lane_x[ln].append(x)
lane_lbl = {"TX": "UART: GPIO4 (TX) → radar RX", "RX": "UART: radar TX → GPIO5 (RX), 256000 baud",
            "PIR": "PIR OUT → GPIO6"}
for ln, y in LANES.items():
    xs = lane_x[ln]
    line(min(xs), y, max(xs), y, LANE_COL[ln], 2.4)
    for x in xs: dot(x, y, LANE_COL[ln])
    text(LANE_LBL_X, y + 4.5, lane_lbl[ln], 12, anchor="start", weight="600", col=LANE_COL[ln])

# ---------------------------------------------------------------- blocks (drawn on top)
for k, b in blocks.items():
    block(b["x"], b["w"], b["title"], b["sub"], fill="#fff8e1" if k == "buck" else None)
# pin labels again, so they sit above the blocks
for b, pins in top_pins.items():
    for (lbl, net), x in zip(pins, pin_xs(b, len(pins))):
        dot(x, TOP, RAIL_COL[net]); text(x, TOP + 16, lbl, 11.5, weight="700")
for b, pins in bot_pins.items():
    for (lbl, ln), x in zip(pins, pin_xs(b, len(pins))):
        dot(x, BOT, LANE_COL[ln] if ln else C["nc"]); text(x, BOT - 7, lbl, 11.5, weight="700")

# ---------------------------------------------------------------- discrete parts
def wipe(x, y0, y1):
    e(f'<rect x="{x-7}" y="{y0}" width="14" height="{y1-y0}" fill="#ffffff"/>')
def diode_down(x, y, lbl):
    wipe(x, y - 14, y + 14)
    line(x, y - 16, x, y - 9, C["v5"], 2.4); line(x, y + 9, x, y + 16, C["v5"], 2.4)
    e(f'<polygon points="{x-8},{y-8} {x+8},{y-8} {x},{y+7}" fill="{C["v5"]}"/>')
    line(x - 9, y + 8, x + 9, y + 8, C["v5"], 2.6)
    text(x - 13, y + 5, lbl, 11.5, anchor="end", weight="700", col=C["v5"])
def resistor(x, y, lbl):
    wipe(x, y - 14, y + 14)
    line(x, y - 16, x, y - 11, C["v5"], 2.4); line(x, y + 11, x, y + 16, C["v5"], 2.4)
    e(f'<rect x="{x-5}" y="{y-11}" width="10" height="22" fill="#fff" stroke="{C["v5"]}" stroke-width="2"/>')
    text(x - 10, y + 4, lbl, 11.5, anchor="end", weight="700", col=C["v5"])
def cap_between(xa, xb, y, lbl, col_a, col_b):
    xm = (xa + xb) / 2
    line(xa, y, xm - 3.5, y, col_a, 2); line(xm + 3.5, y, xb, y, col_b, 2)
    line(xm - 3.5, y - 8, xm - 3.5, y + 8, C["txt"], 2.4); line(xm + 3.5, y - 8, xm + 3.5, y + 8, C["txt"], 2.4)
    dot(xa, y, col_a); dot(xb, y, col_b)
    text(xb + 9, y + 4, lbl, 11.5, anchor="start", weight="700")
xe = pinpos[("esp", "5V")]
xp, xpg = pinpos[("pir", "+")], pinpos[("pir", "−")]
xo, xog = pinpos[("buck", "OUT+")], pinpos[("buck", "OUT−")]
cap_between(xo, xog, 262, "220 µF", C["v5"], C["gnd"])

# ---------------------------------------------------------------- 12 V supply -> buck
bx, bw = blocks["buck"]["x"], blocks["buck"]["w"]
e(f'<rect x="{bx}" y="640" width="{bw}" height="80" rx="10" fill="#ffebee" stroke="{C["v12"]}" stroke-width="1.6"/>')
text(bx + bw / 2, 676, "12 V DC supply", 15, weight="700")
text(bx + bw / 2, 696, "≥ 0.5 A (~0.15 A estimated)", 11.5, col="#546e7a")
xin, xgnd = bx + bw / 2 - 30, bx + bw / 2 + 30
line(xin, BOT, xin, 640, C["v12"], 3); line(xgnd, BOT, xgnd, 640, C["gnd"], 3)
dot(xin, BOT, C["v12"]); dot(xgnd, BOT, C["gnd"])
text(xin, BOT - 7, "IN+", 11.5, weight="700"); text(xgnd, BOT - 7, "IN−", 11.5, weight="700")
text(xin - 8, 560, "+12 V", 12, anchor="end", weight="600", col=C["v12"])
text(xgnd + 8, 560, "GND", 12, anchor="start", weight="600", col=C["gnd"])

# ---------------------------------------------------------------- notes
notes = [
    ("⚠", "Never plug USB-C into the ESP while 12 V is connected: its 5V pin is tied straight to USB VBUS. Flash over USB before wiring, then use OTA."),
    ("⚠", "ENS160+AHT21: power goes to VIN (5 V). The 3V3 pin of this board is the OUTPUT of its regulator, leave it unconnected."),
    ("⚠", "PIR runs from 5 V. MEASURE its OUT (while it detects motion) before wiring it to GPIO6:"),
    (" ", "it should be ~3.3 V. Above 3.4 V, power the PIR from the board 3V3 instead (the ESP32-S3 is not 5 V tolerant)."),
    ("•", "Radar: 5 V only. Some listings say 5-12 V; the datasheet says 5 V. Its UART is 3.3 V logic, no level shifter needed."),
    ("•", "I2C: the modules have their own pull-ups (check that SDA/SCL idle at 3.3 V). Addresses: BH1750 0x23, AHT21 0x38, ENS160 0x53."),
    ("•", "220 µF on the S09 output (Wi-Fi peaks ~0.5 A, the module is rated 0.6 A). All grounds are common."),
    ("•", "Wire: stranded AWG 26-28. The radar has 1.27 mm pitch, solder straight to the pads. Splices: a small stripboard, one strip per net."),
]
ny = 620
e(f'<rect x="300" y="{ny}" width="1100" height="{len(notes) * 26 + 46}" rx="10" fill="#f5f7f8" stroke="#cfd8dc"/>')
text(320, ny + 26, "Notes", 15, anchor="start", weight="700")
for i, (m, s) in enumerate(notes):
    y = ny + 52 + i * 26
    text(322, y, m, 14, anchor="start", weight="700", col=C["v12"] if m == "⚠" else C["txt"])
    text(345, y, s, 13, anchor="start")

# colour legend
lx, ly = 50, 920
leg = [("12 V", C["v12"]), ("5 V", C["v5"]), ("3.3 V", C["v33"]), ("GND", C["gnd"]), ("SDA", C["sda"]),
       ("SCL", C["scl"]), ("ESP TX → radar", C["tx"]), ("radar → ESP RX", C["rx"]), ("PIR", C["pir"])]
text(lx, ly, "Suggested wire colours:", 13, anchor="start", weight="700")
x = lx + 210
for name, col in leg:
    line(x, ly - 4.5, x + 26, ly - 4.5, col, 4)
    text(x + 32, ly, name, 12.5, anchor="start")
    x += 40 + len(name) * 7.4 + 10
text(lx, ly + 34, "Firmware: firmware/ceiling-sensor.yaml · enclosure: hardware/", 12, anchor="start", col="#78909c")
e("</svg>")

open(sys.argv[1] if len(sys.argv) > 1 else "wiring.svg", "w").write("\n".join(out))
print("ok")
