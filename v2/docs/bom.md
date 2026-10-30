# v2 bill of materials

Prices in PLN, checked in October 2026. Modules that are the same as in v1 link to the v1 [BOM](../../docs/bom.md).

## Modules

| Ref | Part | Where | Notes |
|---|---|---|---|
| U2 | Waveshare ESP32-S3-Zero | as v1 | Get the **ESP32-S3-Zero-M** variant (headers already soldered), or solder the headers yourself on the side **without** components. |
| U3 | Hi-Link HLK-LD2412 radar, 11 × 28 mm | [Allegro, ~25 zł](https://allegro.pl/oferta/16441330303); AliExpress: Hi-Link's own store, search "HLK-LD2412" | Take the version **with pins**. The pins must come out of the back (the side without the antenna patches and the chip). Check before soldering anything, see [verify.md](verify.md). |
| U4 | HC-SR602 PIR | as v1 | Header pins out of the back (away from the lens), as in v1. |
| U5 | GY-302 BH1750 | as v1 | Header pins out of the side without the sensor chip, as in v1. |
| U6 | ENS160 + AHT21 combo | as v1 | Header on the **component** side this time: the board sits components up. If your v1 board has the header on the other side, desolder it and fit a new one. |
| U8 | GY-SHT40 temperature/humidity module (purple, VIN/GND/SCL/SDA, ~13 × 10 mm) | [AliExpress, ~17 zł](https://pl.aliexpress.com/item/1005013050830731.html) | Room temperature and humidity. Header on the side **without** the sensor (the sensor faces the room). SHT41 boards with the same layout work too. |
| U7 | SCD40 or SCD41 module (optional) | [AliExpress, ~62 zł](https://pl.aliexpress.com/item/1005011652313734.html), the GND/VDD/SCL/SDA board | Solder the header on the **sensor** side. SCD41 has the wider calibrated range (up to 5000 ppm); for a kitchen or living room SCD40 is enough. |

## Parts on the PCB

| Ref | Part | Qty | Notes |
|---|---|---|---|
| U1 | Switching regulator 5 V 1 A, 3-pin 7805 replacement (Mornsun K7805-1000R3, RECOM R-78E5.0-1.0, or a generic one such as [this Allegro offer, ~3 zł](https://allegro.pl/oferta/18597276546)) | 1 | Pinout must be 1 = VIN, 2 = GND, 3 = 5 V (same as an LM7805). Max 15 mm tall when standing. Not a linear 7805: that would burn ~1.4 W inside the box. |
| D1, D2 | 1N5819 Schottky diode (DO-41) | 2 | D1: reverse polarity protection. D2: lets you plug USB-C into the ESP while 12 V is connected. |
| C1 | Electrolytic 10 µF 25 V, Ø5 mm, 2 mm pitch | 1 | Regulator input. 35 V or 50 V is fine too. |
| C2 | Electrolytic 220 µF 10 V (or 16 V), Ø6.3 mm, 2.5 mm pitch | 1 | 5 V rail; the same capacitor as in v1. |
| C3 | Electrolytic 47 µF 10 V, Ø5 mm, 2 mm pitch | 1 | Only with the SCD4x (it draws up to ~200 mA peaks from 3.3 V). |
| J1 | JST-XH 2-pin header, **right angle** (S2B-XH-A) + a 2-pin XH plug with wires | 1 | Pre-crimped "JST XH 2pin" leads are cheap on Allegro and AliExpress. A straight (vertical) header will not fit under the ceiling base. |
| | Female pin header 2.54 mm, 1 × 40, 8.5 mm tall | 2 strips | Cut into 2 × 9, 1 × 8, 1 × 5, 2 × 4, 2 × 3 (45 pins; you lose one pin per cut). |
| | M2 × 6 self-tapping screw for plastics (PT / "wkręt do tworzyw") | 3 | Holds the PCB on the bosses. |
| | PCB | 1 | [pcb.md](pcb.md): 5 boards from JLCPCB, ~4 USD + shipping. |

Everything else (ceiling base screws, 12 V supply, PETG) is the same as v1.

## What you no longer need from v1

S09 converter, perfboard hub, Dupont jumpers, Wago connector, the LD2410B and its cable.
