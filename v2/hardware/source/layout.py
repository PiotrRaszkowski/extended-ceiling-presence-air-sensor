"""
v2 layout: one source of truth for the carrier PCB (pcb_build.py) and the housing
(enclosure_v2.py).

Coordinates: millimetres, origin = housing axis, "ceiling view" = looking down from the
ceiling onto the face (same as the v1 CadQuery model). x to the right, y up.
z = 0 is the outside of the face (room side), z grows towards the ceiling.

Every module hangs under the PCB on a 2.54 mm pin header that is pushed all the way
into a female socket soldered to the PCB underside. Its height is therefore fixed by
the PCB height and the header/socket dimensions below, not by the housing.

Pin positions are given in each module's own frame, seen from the ceiling (that is,
from the side where its header pins come out), then rotated by `rot` degrees (CCW)
and moved to (cx, cy).

Items marked VERIFY are taken from product photos and listings, not from a caliper.
Check them against your own boards before ordering PCBs (docs: v2/docs/verify.md).
"""
import math

# --- stack-up -----------------------------------------------------------------
FACE = 1.6            # face thickness (as v1)
H = 30.0              # housing height (as v1, same ceiling base)
SOCKET_H = 8.5        # female 2.54 mm socket body height (standard "8.5 mm" type)
HEADER_PLASTIC = 2.5  # plastic spacer of a standard male header
PCB_T = 1.6
RADAR_FRONT_Z = 5.7   # radar board front: 3.7 mm PETG window + 2.0 mm air (as v1)
RADAR_T = 1.0         # LD2412 board thickness (VERIFY)
# module back plane (where the header plastic sits on the module board)
Z_BACK = RADAR_FRONT_Z + RADAR_T
PCB_BOT = Z_BACK + HEADER_PLASTIC + SOCKET_H      # 17.7
PCB_TOP = PCB_BOT + PCB_T                         # 19.3
SOCKET_FACE = PCB_BOT - SOCKET_H                  # 9.2: mating face of all sockets

R_PCB = 45.6          # PCB radius: housing wall at 48.0, but the bayonet pins reach in to 46.2 and the
                      # board has to pass them on the way in (0.6 mm, fab outline tolerance is +-0.2)
R_RING_IN = 44.6      # the ceiling base ring reaches down to z = 20.0 (0.7 mm above the PCB) for r >= 44.6
R_KEEP_TOP = 43.6     # screw heads, pin tails and parts on the PCB top must stay inside this radius

P = 2.54

# --- modules --------------------------------------------------------------------
# kind: "socket" = module plugs into female sockets on the PCB underside.
# body: (sx, sy) board outline in the module frame; extra keys describe what the housing needs.
MODULES = {
    # HLK-LD2412, 11 x 28 mm, antenna side (with the chip) towards the face.
    # Front view: OUT/GND/+5V on the left end, TX/RX/GND/3V3 on the right end (top to bottom).
    # Seen from the back the ends swap. 3V3 pin stays unconnected (5 V OR 3V3, never both).
    "RADAR": dict(
        ref="U3", label="LD2412", cx=6.0, cy=4.0, rot=90.0, body=(28.0, 11.0),
        rows=[  # (row name, [(pin, lx, ly, net)])
            ("U3A", [("TX", -12.73, 3.81, "RADAR_TX"), ("RX", -12.73, 1.27, "RADAR_RX"),
                     ("GND", -12.73, -1.27, "GND"), ("3V3", -12.73, -3.81, None)]),
            ("U3B", [("OUT", 12.73, 2.54, "RADAR_OUT"), ("GND", 12.73, 0.0, "GND"),
                     ("+5V", 12.73, -2.54, "+5V")]),
        ],
        front_z=RADAR_FRONT_Z, thick=RADAR_T, verify=True),

    # Waveshare ESP32-S3-Zero, 17.98 x 23.69, rows 15.24 apart (Waveshare FAQ), hanging
    # component side down (LED and USB-C towards the face). Seen from the ceiling = bottom view.
    "ESP": dict(
        ref="U2", label="ESP32-S3-Zero", cx=-8.0, cy=-29.5, rot=0.0, body=(17.98, 23.69),
        usb_end=+1,   # USB-C at +ly (towards the housing centre)
        rows=[
            ("U2A", [(n, -7.62, 10.16 - i * P, net) for i, (n, net) in enumerate([
                ("TX", None), ("RX", None), ("GP13", None), ("GP12", None), ("GP11", None),
                ("GP10", None), ("GP9", None), ("GP8", None), ("GP7", "RADAR_OUT")])]),
            ("U2B", [(n, 7.62, 10.16 - i * P, net) for i, (n, net) in enumerate([
                ("5V", "ESP_5V"), ("GND", "GND"), ("3V3", "+3V3"), ("GP1", "SDA"), ("GP2", "SCL"),
                ("GP3", None), ("GP4", "RADAR_RX"), ("GP5", "RADAR_TX"), ("GP6", "PIR_OUT")])]),
        ],
        led=(0.0, 3.4),   # WS2812 position in the module frame (approx., VERIFY)
        antenna=6.0,      # ceramic antenna: the last ~6 mm at the end away from USB-C (no copper pour above it)
        thick=1.0, below=3.4),   # USB-C is the tallest part under the board

    # HC-SR602 (HW-438 board), round Ø15.89, lens towards the face, 3-pin header near the edge.
    # Silkscreen on the lens side, along the pin column: OUT, +, -  (+ in the MIDDLE; checked on the
    # prototype's board, 2026-10-30). Only the middle pin matters: turning the module by 180 deg
    # swaps the two outer ones.
    "PIR": dict(
        ref="U4", label="HC-SR602", cx=-22.0, cy=19.0, rot=0.0, body=(15.89, 15.89), round=True,
        rows=[("U4", [("OUT", -P, -5.4, "PIR_OUT"), ("+", 0.0, -5.4, "+5V"), ("-", P, -5.4, "GND")])],
        lens_d=10.3, thick=1.0, verify=True),

    # GY-302 (BH1750), 14.05 x 18.53, components (sensor) towards the face.
    # Front: VCC GND SCL SDA ADDR left to right with the pins at the bottom; mirrored from the back.
    "BH": dict(
        ref="U5", label="GY-302 BH1750", cx=-27.0, cy=-6.0, rot=0.0, body=(14.05, 18.53),
        rows=[("U5", [("ADDR", -5.08, -7.97, None), ("SDA", -2.54, -7.97, "SDA"), ("SCL", 0.0, -7.97, "SCL"),
                      ("GND", 2.54, -7.97, "GND"), ("VCC", 5.08, -7.97, "+3V3")])],
        chip=(0.0, 2.5), thick=1.6),

    # ENS160 + AHT21 (purple), 19.29 x 24.20, COMPONENTS UP (towards the PCB), in the closed chamber.
    # Pin order VERIFY.
    "ENS": dict(
        ref="U6", label="ENS160+AHT21", cx=33.0, cy=0.0, rot=0.0, body=(19.29, 24.20),
        rows=[("U6", [(n, -8.35, 8.89 - i * P, net) for i, (n, net) in enumerate([
            ("VIN", "+5V"), ("3V3", "ENS_3V3"), ("GND", "GND"), ("SCL", "SCL"), ("SDA", "SDA"),
            ("ADD", "ENS_ADD"), ("CS", "ENS_CS"), ("INT", None)])])],
        thick=1.6, components_up=True, verify=True),

    # SCD40 / SCD41 module (optional), ~23 x 13 (VERIFY), SENSOR UP (towards the PCB), header
    # soldered from the sensor side. Pins GND VDD SCL SDA along the short edge.
    "SCD": dict(
        ref="U7", label="SCD40/SCD41 (option)", cx=3.0, cy=34.0, rot=0.0, body=(23.0, 13.0),
        rows=[("U7", [("GND", -10.2, 3.81, "GND"), ("VDD", -10.2, 1.27, "+3V3"),
                      ("SCL", -10.2, -1.27, "SCL"), ("SDA", -10.2, -3.81, "SDA")])],
        sensor=(3.0, 0.0, 10.1, 6.5), thick=1.6, components_up=True, optional=True, verify=True),
}

# --- power and other parts (not modules) -----------------------------------------
# side: "B" = underside (same side as the modules), "T" = top (ceiling side)
PARTS = {
    "J1": dict(fp="Connector_JST:JST_XH_S2B-XH-A_1x02_P2.50mm_Horizontal", side="T", x=-25.0, y=-7.0, rot=90.0,
               value="12V IN (JST-XH)", pads={"1": "VIN_RAW", "2": "GND"}),
    "D1": dict(fp="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", side="B", x=-18.0, y=7.0, rot=0.0,
               value="1N5819", pads={"1": "VIN", "2": "VIN_RAW"}),      # pad 1 = cathode
    "C1": dict(fp="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", side="B", x=-4.5, y=7.0, rot=0.0,
               value="10uF 25V", pads={"1": "VIN", "2": "GND"}),
    "U1": dict(fp="Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT", side="B", x=-15.5, y=1.0, rot=0.0,
               value="K7805-1000R3 / R-78E5.0-1.0", pads={"1": "VIN", "2": "GND", "3": "+5V"}),
    "C2": dict(fp="Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", side="B", x=-5.0, y=-9.3, rot=0.0,
               value="220uF 10V", pads={"1": "+5V", "2": "GND"}),
    "D2": dict(fp="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", side="B", x=-16.0, y=-15.0, rot=0.0,
               value="1N5819", pads={"1": "ESP_5V", "2": "+5V"}),
    "C3": dict(fp="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", side="B", x=-8.0, y=16.0, rot=0.0,
               value="47uF 10V (with SCD4x)", pads={"1": "+3V3", "2": "GND"}),
    "J2": dict(fp="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", side="B", x=-36.0, y=8.0, rot=0.0,
               value="I2C expansion (not fitted)", pads={"1": "+3V3", "2": "GND", "3": "SDA", "4": "SCL"}),
    # ENS160 ADD / CS straps: open by default (the combo boards pull both up themselves). Bridge with a
    # blob of solder only if your ENS160 does not answer at 0x53. Pad 1 = the module's own 3V3 output.
    "JP1": dict(fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", side="T", x=31.0, y=-3.81, rot=-90.0,
                value="ADD strap", pads={"1": "ENS_3V3", "2": "ENS_ADD"}),
    "JP2": dict(fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", side="T", x=31.0, y=-7.6, rot=-90.0,
                value="CS strap", pads={"1": "ENS_3V3", "2": "ENS_CS"}),
}

# M2 mounting holes (PCB) = screw bosses (housing)
HOLES = [(-35.0, 21.0), (-32.0, -25.0), (35.0, -21.0)]   # r <= 41.5: pan heads (Ø4.2) clear the base ring
HOLE_D = 2.2
BOSS_D = 6.0

# ENS160 chamber (closed box under the PCB, against the +x wall)
CHAMBER = dict(x0=22.6, y_half=14.2)   # inner wall x and half width of the inside

SCREW_HEAD_D = 4.2    # M2 pan head
HEADER_TAIL = 3.0     # short end of a standard male header (below the module board)


def place(m, lx, ly):
    a = math.radians(m["rot"])
    return (m["cx"] + lx * math.cos(a) - ly * math.sin(a), m["cy"] + lx * math.sin(a) + ly * math.cos(a))


def module_outline(m, grow=0.0):
    """Corners of the module board outline (ceiling view)."""
    sx, sy = m["body"]
    return [place(m, x, y) for x, y in ((-sx / 2 - grow, -sy / 2 - grow), (sx / 2 + grow, -sy / 2 - grow),
                                        (sx / 2 + grow, sy / 2 + grow), (-sx / 2 - grow, sy / 2 + grow))]


def all_pins():
    """[(module key, row ref, pin index (1-based), pin name, x, y, net)]"""
    out = []
    for k, m in MODULES.items():
        for row_ref, pins in m["rows"]:
            for i, (n, lx, ly, net) in enumerate(pins, 1):
                x, y = place(m, lx, ly)
                out.append((k, row_ref, i, n, x, y, net))
    return out


def module_z(m):
    """(board underside z, board top z) of a module hanging under the PCB."""
    if m.get("components_up"):
        top = SOCKET_FACE - HEADER_PLASTIC
        return top - m["thick"], top
    back = SOCKET_FACE - HEADER_PLASTIC
    return back - m["thick"], back


if __name__ == "__main__":
    print(f"PCB underside z={PCB_BOT:.2f}, top z={PCB_TOP:.2f}, socket face z={SOCKET_FACE:.2f}")
    for k, m in MODULES.items():
        z0, z1 = module_z(m)
        print(f"{k:6s} board z {z0:5.2f}..{z1:5.2f}  outline {[(round(x,1), round(y,1)) for x, y in module_outline(m)]}")
    for p in all_pins():
        print(p)
