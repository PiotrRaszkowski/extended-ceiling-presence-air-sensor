# Check before you order PCBs

The board places every socket from numbers in [`layout.py`](../hardware/source/layout.py). Some of those numbers come from product photos and listings, not from a caliper. A PCB is cheap, but a second order costs another two weeks, so check these against the boards you actually have.

## 1. Pin order on each module

Read the silkscreen next to the pins and compare it with the table. The order is as printed on the module, looking at the side named in the last column.

| Module | Expected order | Read it on |
|---|---|---|
| HLK-LD2412 | one end: OUT, GND, +5V; other end: TX, RX, GND, 3V3 | antenna side (with the chip), long edge horizontal |
| HC-SR602 (HW-438 board) | OUT, +, − along the pin column, **+ in the middle** (checked on the prototype) | lens side |
| ENS160 + AHT21 | VIN, 3V3, GND, SCL, SDA, ADD, CS, INT | component side |
| GY-302 | VCC, GND, SCL, SDA, ADDR | component side |
| SCD40/41 module | GND, VDD, SCL, SDA | sensor side |
| GY-SHT40 | VIN, GND, SCL, SDA | sensor side |
| ESP32-S3-Zero | 5V, GND, 3V3, GP1 … GP6 / TX, RX, GP13 … GP7 | component side, USB-C up |

Also measure the PIR's OUT with the PIR on 5 V while you wave at it: it must stay at or below 3.3 V, because it goes straight to GPIO6. The HC-SR602 has its own 3.3 V regulator, but clones vary.

The PIR is the one to be careful with: the order differs between HC-SR602 clones, and wiring it wrong makes the board hot (it happened on the v1 prototype). For the socket only the middle pin matters, because turning the module round swaps the outer two.

## 2. Dimensions

| Module | Value in layout.py | What to measure |
|---|---|---|
| HLK-LD2412 | 11 × 28 mm, board 1.0 mm thick, pin columns 1.27 mm in from each short edge | outline, thickness, pin positions |
| HC-SR602 | pin row 5.4 mm from the lens centre | distance from the lens centre to the line through the three pins |
| ENS160 + AHT21 | 19.29 × 24.20 mm (as v1), pin row 1.3 mm from the edge | pin row position |
| SCD4x module | ~23 × 13 mm, pin column 1.3 mm from the short edge, sensor centre 3 mm right of the board centre | outline, pin column, sensor position |
| GY-SHT40 | 13 × 10 mm, pin column 1.3 mm from the left edge, sensor 4.5 mm right of the centre | outline, pin column, sensor position |
| ESP32-S3-Zero | rows 15.24 mm apart, 9 pins centred on the 23.69 mm length, antenna in the last 6 mm away from USB-C | first pin's distance from the USB end; where the antenna is |

## 3. Which side the pins come out

All modules hang under the PCB with their pins pointing **up** into the sockets:

- ESP32-S3-Zero, LD2412, HC-SR602, GY-302, GY-SHT40: pins on the side **away from** the parts that face the room (chip, antenna, lens, light sensor, SHT40).
- ENS160 + AHT21 and SCD4x: pins on the **component / sensor** side (these two sit face up).

## 4. Fit test with the printed template

1. Print `01_housing_v2.stl` and `20_pcb_fit_template.stl` (the template is the PCB outline with a hole at every socket pin and the three screw holes).
2. Push the female sockets through the template from the bottom so their pins stick out on top, and plug the modules into the sockets.
3. Put the template on the three bosses in the housing (it stands in for the PCB) and look at the face: the PIR lens should be centred in its hole, the BH1750 chip above its window, nothing should touch the face or the chamber walls.

## If something differs

Change the numbers in `v2/hardware/source/layout.py` and rebuild everything:

```bash
cd v2/hardware/source
python pcb_build.py place        # KiCad's Python (import pcbnew), KiCad 7 or newer
python router.py                 # routes the board (about a minute)
python pcb_build.py finish       # GND pour + DRC -> ../pcb/carrier.kicad_pcb
python enclosure_v2.py           # CadQuery: housing, template, collision check
python schematic_svg.py ../../docs/images/v2-schematic.svg
python assembly_svg.py ../../docs/images/v2-assembly-bottom.svg bottom
```

`pcb_build.py finish` prints the DRC summary; it has to say 0 unconnected pads and no clearance or courtyard errors. `enclosure_v2.py` exits with an error if any module, socket or part collides with the housing or the ceiling base. Then export new Gerbers ([pcb.md](pcb.md)).
