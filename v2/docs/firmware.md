# v2 firmware

[`firmware/ceiling-sensor-v2.yaml`](../firmware/ceiling-sensor-v2.yaml) is the v1 config with the radar changed to the LD2412. Flashing, secrets and adding it to Home Assistant work as in v1 ([firmware](../../docs/firmware.md)). It validates and compiles with ESPHome 2026.10.0 (with the SCD4x enabled: RAM 33.1 %, flash 50.5 %).

## What is different from v1

- `ld2412` instead of `ld2410`, UART at 115200 baud (the LD2412 default). GPIO4/5 stay the same.
- 14 distance gates instead of 9. One gate is still 0.75 m, so from a 2.6 m ceiling the floor is in gate 3, as before. Use **Radar max gate** to stop it looking through the floor or walls.
- **Radar learn empty room** (button): the LD2412 measures the background with nobody in the room and subtracts it afterwards. Press it once after mounting and leave the room until **Radar background correction running** turns off.
- The radar's OUT pin is wired to GPIO7. The config doesn't use it; it's there if you ever want a hardware presence line.
- The ENS160 is still expected at 0x53. If the I2C scan in the log doesn't show it, bridge JP1 on the PCB (ties ADD to the module's 3.3 V) and JP2 (CS), see [pcb.md](pcb.md#soldering).

## Optional SCD40 / SCD41

If you fitted the SCD4x (and C3), uncomment these lines near the top of the YAML:

```yaml
packages:
  scd4x: !include scd4x.yaml
```

and copy [`scd4x.yaml`](../firmware/scd4x.yaml) next to it. That adds a **CO2** sensor (real CO2 in ppm) and the SCD4x's own temperature and humidity as diagnostic entities. Automatic self-calibration is on: it assumes the room gets fresh air (around 400 ppm) at some point every few days, which is true for a kitchen with a window. If the room never gets aired, turn it off and calibrate by hand.

The ENS160 stays in: it's the VOC sensor (cooking, cleaning products), which the SCD4x doesn't measure.
