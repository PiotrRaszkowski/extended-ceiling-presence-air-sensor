# Extended ceiling presence + air sensor

A small ceiling-mounted sensor for Home Assistant, about the size of a smoke detector (Ø80 × 30 mm, or Ø100 if you want more room inside). One per room. It tells you whether someone is in the room, even if they're sitting still, and how the air is doing.

![Housing](docs/images/hero.png)

It combines:

- 24 GHz mmWave radar (HLK-LD2410B) for presence, including people who aren't moving
- PIR (HC-SR602) for fast motion detection when someone walks in
- ENS160 + AHT21 for air quality (eCO2, TVOC, AQI), temperature and humidity, in a separate ventilated chamber so the electronics don't heat the sensors
- BH1750 light sensor, so lights only come on when it's actually dark
- ESP32-S3-Zero running [ESPHome](https://esphome.io), powered from 12 V

Parts cost about 100 zł (~€24) from AliExpress or about 160 zł (~€38) from a single seller on Allegro in Poland. The enclosure prints in PETG without supports and every board is held by press-fit crush ribs, so there are no screws inside and glue shouldn't be needed.

## Project status

| Part | Status |
|---|---|
| Firmware | Validates and compiles with ESPHome 2026.10.0. Not yet confirmed on a finished unit. |
| Electronics | Wiring designed around these modules. Do the bench test from [assembly](docs/assembly.md) before closing the box. |
| Enclosure Ø100 (v17, [`hardware/d100/`](hardware/d100/)) | The Ø100 prototype was printed in PETG and installed in a kitchen. In it the radar saw noise on every gate ([why](docs/printing.md#the-radar-window)), so v15/v16 thin the window to 0.8 mm and put the radar on posts 6.2 mm above it. v16 also widens the ENS160 pass-through and tightens the crush ribs a little; v17 adds snap lips that hold the radar down. |
| Enclosure Ø80 (v17, current) | v12 was printed in PETG and every module went into its seat (photos below). v13 tightens the BH1750 seat by 0.05 mm; v14 adds a seat for the [Dupont hub](docs/wiring.md#dupont-hub) and moves the ENS160 pass-through; v16 puts the radar on posts above a 0.8 mm window, as in Ø100. Print `11_seat_test_fit.stl` first anyway, since fit depends on your printer. |

Issues and photos of your build are welcome.

**Next version:** [v2](v2/) replaces the jumpers and the hub with a round carrier PCB that every module plugs into, switches to the HLK-LD2412 radar (2.54 mm pins) and adds an optional SCD40/SCD41 for real CO2. It is designed but not built yet.

## Documentation

1. [Bill of materials](docs/bom.md): modules with Allegro and AliExpress links, passives, screws
2. [Wiring](docs/wiring.md): diagram, pin map, power notes
3. [Printing](docs/printing.md): filament, slicer settings, print order, fit calibration
4. [Firmware and Home Assistant](docs/firmware.md): flashing ESPHome, adding the device, entity list
5. [Assembly](docs/assembly.md): modules into seats, ceiling mount
6. [Tuning and automations](docs/tuning.md): radar range, temperature offset, example automations
7. [Enclosure source](docs/enclosure-source.md): OpenSCAD Customizer for other module sizes, CadQuery model, parameters, measured sizes

## Quick start

1. Buy the parts from the [BOM](docs/bom.md). Stick to the exact module types, because the seats are sized to them.
2. Print `10_press_fit_calibration.stl` and `11_seat_test_fit.stl` from [`hardware/stl/`](hardware/stl/), check the fit, then print `00_print_plate_all_parts.stl`.
3. Flash [`firmware/ceiling-sensor.yaml`](firmware/ceiling-sensor.yaml) over USB and wire everything on the bench.
4. Check in Home Assistant that every sensor reports, then assemble and mount it.
5. Tune the radar range and the temperature offset.

A printed Ø80 housing (v12) with every module pressed into its seat, seen from the ceiling side:

| | |
|---|---|
| ![All modules seated in a printed Ø80 housing, top view](docs/images/photos/d80-modules-top.jpg) | ![The same housing from an angle](docs/images/photos/d80-modules-angle.jpg) |

![What goes where](docs/images/what-goes-where.png)

![Wiring](docs/images/wiring.png)

## Repository layout

```
firmware/        ESPHome config + secrets template
hardware/stl/    printable parts, Ø80
hardware/step/   the same parts as STEP
hardware/source/ CadQuery model, the same model for OpenSCAD (Customizer), wiring diagram generator
hardware/d100/   printable parts, Ø100 (STL + STEP)
v2/              next version: carrier PCB, LD2412, optional SCD4x (designed, not built yet)
homeassistant/   example automations
docs/            documentation and images
```

## Limitations

- eCO2 from the ENS160 is **estimated from VOCs**, not measured. It's fine for "the room is stuffy, open a window", not for exact ppm. If you need real CO2, add an SCD40 or MH-Z19C.
- There is no particulate (PM2.5) sensor.
- The radar sees through thin walls. Limit its range in Home Assistant, see [tuning](docs/tuning.md).

## License

[MIT](LICENSE): firmware, CAD source, models and docs.
