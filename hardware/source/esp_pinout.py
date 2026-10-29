"""ESP32-S3-Zero pinout for this project (SVG): top view and bottom view, used pins highlighted.

Pin order taken from Waveshare's ESP32-S3-Zero pinout (docs.waveshare.com/ESP32-S3-Zero).
Usage: python esp_pinout.py esp32-s3-zero-pinout.svg
"""
import sys

C = dict(v5="#ef6c00", v33="#c2185b", gnd="#212121", sda="#1565c0", scl="#b8860b", tx="#2e7d32",
         rx="#6a1b9a", pir="#795548", unused="#b0bec5", txt="#263238", sub="#607d8b", board="#1e4f9c",
         pad="#d4a017", usb="#cfd8dc")

# Long edges, top to bottom with USB-C at the top, looking at the component side.
LEFT = [("5V", "S09 5 V out", "v5"), ("GND", "GND", "gnd"), ("3V3", "BH1750 VCC", "v33"),
        ("GP1", "I2C SDA (BH1750, ENS160)", "sda"), ("GP2", "I2C SCL (BH1750, ENS160)", "scl"),
        ("GP3", "not used", None), ("GP4", "UART TX -> radar RX", "tx"),
        ("GP5", "UART RX <- radar TX", "rx"), ("GP6", "PIR OUT", "pir")]
RIGHT = [("TX", "GPIO43, not used", None), ("RX", "GPIO44, not used", None), ("GP13", "not used", None),
         ("GP12", "not used", None), ("GP11", "not used", None), ("GP10", "not used", None),
         ("GP9", "not used", None), ("GP8", "not used", None), ("GP7", "not used", None)]

S = 14.0                 # px per mm
BW, BH = 17.98 * S, 23.69 * S
PITCH = 2.54 * S
W, HGT = 1720, 700
out = []
e = out.append


def text(x, y, s, size=15, anchor="middle", weight="400", col=None):
    s = s.replace("<-", "←").replace("->", "→")
    e(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{col or C["txt"]}">{s}</text>')


def board(ox, oy, mirrored, title, subtitle):
    """ox, oy = top-left of the board outline. mirrored = bottom view (left/right swap)."""
    text(ox + BW / 2, oy - 92, title, 21, weight="700")
    text(ox + BW / 2, oy - 68, subtitle, 14, col=C["sub"])
    # USB-C
    e(f'<rect x="{ox + BW / 2 - 4.5 * S:.1f}" y="{oy - 1.2 * S:.1f}" width="{9 * S:.1f}" height="{7.3 * S:.1f}" rx="8" fill="{C["usb"]}" stroke="#90a4ae"/>')
    e(f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{BW:.1f}" height="{BH:.1f}" rx="10" fill="{C["board"]}"/>')
    e(f'<rect x="{ox + BW / 2 - 4.5 * S:.1f}" y="{oy - 1.2 * S:.1f}" width="{9 * S:.1f}" height="{7.3 * S:.1f}" rx="8" fill="{C["usb"]}" stroke="#90a4ae"/>')
    text(ox + BW / 2, oy + 3.4 * S, "USB-C", 13, weight="600", col="#455a64")
    if not mirrored:
        # chip, buttons, LED (component side)
        cx, cy = ox + BW / 2, oy + 16.6 * S
        e(f'<rect x="{cx - 2.6 * S:.1f}" y="{cy - 2.6 * S:.1f}" width="{5.2 * S:.1f}" height="{5.2 * S:.1f}" fill="#263238" transform="rotate(45 {cx:.1f} {cy:.1f})"/>')
        text(cx, cy + 4, "ESP32-S3", 11, weight="700", col="#eceff1")
        for bx, lbl in ((ox + 5.2 * S, "BOOT"), (ox + BW - 5.2 * S, "RESET")):
            e(f'<rect x="{bx - 1.6 * S:.1f}" y="{oy + 7.2 * S:.1f}" width="{3.2 * S:.1f}" height="{2.6 * S:.1f}" rx="3" fill="#eceff1"/>')
            text(bx, oy + 11.6 * S, lbl, 10, weight="700", col="#eceff1")
        e(f'<rect x="{ox + BW / 2 - 0.8 * S:.1f}" y="{oy + 7.6 * S:.1f}" width="{1.6 * S:.1f}" height="{1.6 * S:.1f}" fill="#fafafa" stroke="#ef5350" stroke-width="2"/>')
        text(ox + BW / 2, oy + 10.9 * S, "RGB LED", 10, weight="700", col="#eceff1")
    else:
        text(ox + BW / 2, oy + BH / 2, "bottom side", 15, weight="700", col="#eceff1")
        text(ox + BW / 2, oy + BH / 2 + 20, "(no components)", 12, col="#cfd8dc")
    left, right = (RIGHT, LEFT) if mirrored else (LEFT, RIGHT)
    y0 = oy + 2.0 * S
    for side, pins in (("L", left), ("R", right)):
        for i, (name, dest, col) in enumerate(pins):
            y = y0 + i * PITCH
            px = ox + 1.0 * S if side == "L" else ox + BW - 1.0 * S
            used = col is not None
            pc = C[col] if used else C["unused"]
            e(f'<circle cx="{px:.1f}" cy="{y:.1f}" r="{0.8 * S:.1f}" fill="{C["pad"]}" stroke="{pc}" stroke-width="{4 if used else 1.5}"/>')
            e(f'<circle cx="{px:.1f}" cy="{y:.1f}" r="{0.4 * S:.1f}" fill="#fff8e1"/>')
            # label box
            lw = 62
            if side == "L":
                lx = ox - 22 - lw
                e(f'<line x1="{px - 0.8 * S:.1f}" y1="{y:.1f}" x2="{lx + lw:.1f}" y2="{y:.1f}" stroke="{pc}" stroke-width="{3 if used else 1.5}"/>')
            else:
                lx = ox + BW + 22
                e(f'<line x1="{px + 0.8 * S:.1f}" y1="{y:.1f}" x2="{lx:.1f}" y2="{y:.1f}" stroke="{pc}" stroke-width="{3 if used else 1.5}"/>')
            e(f'<rect x="{lx:.1f}" y="{y - 12:.1f}" width="{lw}" height="24" rx="5" fill="{pc}"/>')
            text(lx + lw / 2, y + 5, name, 14, weight="700", col="#ffffff" if used else "#37474f")
            if side == "L":
                text(lx - 10, y + 5, dest, 14, anchor="end", weight="600" if used else "400", col=pc if used else "#90a4ae")
            else:
                text(lx + lw + 10, y + 5, dest, 14, anchor="start", weight="600" if used else "400", col=pc if used else "#90a4ae")


e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HGT}" viewBox="0 0 {W} {HGT}" font-family="Inter, Segoe UI, Helvetica, Arial, sans-serif">')
e(f'<rect width="{W}" height="{HGT}" fill="#ffffff"/>')
text(W / 2, 40, "Waveshare ESP32-S3-Zero: pins used by this sensor", 24, weight="700")
text(W / 2, 66, "all connections are on ONE long edge: 5V, GND, 3V3, GP1, GP2, GP4, GP5, GP6 (GP3 stays free)", 15, col=C["sub"])
board(330, 200, False, "Top view (component side)", "USB-C up, chip and buttons facing you")
board(1180, 200, True, "Bottom view (flipped left to right)", "USB-C up, the side that lies on the rails in the housing")
# notes
notes = ["GPIO21 drives the on-board RGB LED, nothing to wire.  GP14/15/16 are small pads on the top side, GP17/18/38-45 pads on the bottom: not used.",
         "Never have USB-C plugged in while the 5V pin is fed from the S09 (12 V on): the 5V pin is the USB VBUS line."]
for i, n in enumerate(notes):
    text(W / 2, HGT - 60 + i * 26, n, 14, col=C["sub"])
e("</svg>")
open(sys.argv[1] if len(sys.argv) > 1 else "esp32-s3-zero-pinout.svg", "w").write("\n".join(out))
print("ok")
