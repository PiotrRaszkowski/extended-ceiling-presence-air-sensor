# Firmware and Home Assistant

The firmware is a single ESPHome config: [`firmware/ceiling-sensor.yaml`](../firmware/ceiling-sensor.yaml). It needs ESPHome 2026.10.0 or newer, because the encrypted OTA block inherits the API key and older versions don't support that.

## 1. Get ESPHome

The easiest route is the ESPHome Device Builder app in Home Assistant: Settings → Apps (Add-ons in versions before 2026.2) → install ESPHome Device Builder from the store, then open its web UI. You can also use the CLI (`pip install esphome`).

## 2. Create the device

1. In the Device Builder click **+ New device**, give it any name, skip the wizard, then **Edit** the new file and replace its contents with [`ceiling-sensor.yaml`](../firmware/ceiling-sensor.yaml).
2. Change the two substitutions at the top. `name` becomes the hostname (lowercase, dashes, max 31 characters), `friendly_name` becomes the device name in Home Assistant and the prefix of every entity ID.

   ```yaml
   substitutions:
     name: ceiling-sensor-bedroom
     friendly_name: Bedroom sensor
   ```

3. Make sure your ESPHome Secrets (top right in the Device Builder) contain the four keys from [`secrets.yaml.example`](../firmware/secrets.yaml.example): `wifi_ssid`, `wifi_password`, `api_encryption_key` and `ap_password`. Generate the API key with `openssl rand -base64 32`, or copy the one the wizard created for the new device.

For a second room, copy the file and change only the substitutions.

## 3. First flash over USB

Do this on the bench, before the ESP's 5V wire is connected to the S09. The 5V pin is tied straight to USB, so never have USB and 12 V connected at the same time (see [wiring](wiring.md)).

1. Connect the ESP32-S3-Zero to your computer with a USB-C **data** cable. It doesn't need the 12 V supply for this.
2. In the Device Builder: **Install → Plug into this computer** (needs Chrome or Edge, it uses Web Serial). Alternatively **Install → Manual download → Factory format** and flash the `.bin` with [web.esphome.io](https://web.esphome.io).
3. If the port doesn't show up, hold the **BOOT** button on the board while plugging the cable in, flash, then press **RESET**.

With the CLI: `esphome run ceiling-sensor.yaml` and pick the USB port.

After the first flash every update goes over Wi-Fi (**Install → Wirelessly**). If the board can't reach your Wi-Fi it opens a fallback hotspot named after the device, protected by `ap_password`; connect to it to enter new credentials.

## 4. Add it to Home Assistant

Home Assistant discovers the device on its own: Settings → Devices & services → **ESPHome, Discovered → Add**. If it asks for the encryption key, paste the `api_encryption_key` value. Then assign the device to its area.

The LD2410B ships with Bluetooth switched on, and anyone nearby with the HLKRadarTool app can change its settings. Turn the `Radar Bluetooth` switch off once the device is up.

## Entities

With `friendly_name: Living room sensor`:

| Entity | What it is |
|---|---|
| `binary_sensor.living_room_sensor_occupancy` | Fused PIR + radar presence. Use this one in automations. |
| `binary_sensor.living_room_sensor_pir_motion` | Raw PIR |
| `binary_sensor.living_room_sensor_radar_presence` / `_radar_moving_target` / `_radar_still_target` | Raw radar states |
| `sensor.living_room_sensor_temperature` | °C, corrected for self-heating |
| `sensor.living_room_sensor_humidity` | %, recalculated for the corrected temperature |
| `sensor.living_room_sensor_eco2` | Estimated CO2 in ppm (see below) |
| `sensor.living_room_sensor_tvoc` | Volatile organic compounds, ppb |
| `sensor.living_room_sensor_aqi` | ENS160 AQI-UBA index, 1 (excellent) to 5 (unhealthy) |
| `sensor.living_room_sensor_air_quality` | Same index as text: Excellent / Good / Moderate / Poor / Unhealthy |
| `sensor.living_room_sensor_illuminance` | lx |
| `sensor.living_room_sensor_radar_*_distance`, `_radar_*_energy` | Radar distances and per-target energy |
| `sensor.living_room_sensor_radar_g0_move_energy` … `g8_still_energy` | Per-gate energies for tuning. Disabled by default; they only update in engineering mode. |
| `number.living_room_sensor_presence_hold_time` | Extra seconds occupancy stays on after the sensors report nothing (default 15 s), on top of the radar's own `Radar timeout` |
| `number.living_room_sensor_temperature_offset` | Temperature correction (default −2.5 °C) |
| `number.living_room_sensor_radar_g0_move_threshold` … `g8` | Per-gate radar thresholds |
| `switch.living_room_sensor_radar_engineering_mode` | Makes the radar report per-gate energies, for tuning |
| `switch.living_room_sensor_radar_bluetooth` | Radar Bluetooth, for the HLKRadarTool phone app. Keep it off. |
| `switch.living_room_sensor_air_quality_led` | On-board LED showing air quality: green / orange / red |

## How presence is decided

```
ON    ← PIR motion  OR  radar moving target
HOLD  ← any radar target, including a still one
OFF   ← nothing detected for "Radar timeout" + "Presence hold time"
```

A still radar target alone can't switch occupancy on. That keeps the usual radar ghosts (a curtain, a plant, a fan) from turning the lights on in an empty room. Once someone walked in, a still target keeps occupancy on, so a person reading on the sofa doesn't end up in the dark.

## What the air sensor can and can't do

- eCO2 is an estimate derived from VOCs, not a CO2 measurement. People exhale VOCs along with CO2, so eCO2 does rise when a room gets stuffy. It also rises from cooking, perfume and cleaning products. Good enough for "open a window" or "boost the ventilation", not for real ppm numbers.
- AQI and TVOC are useful for spotting sudden changes in the air.
- There's no particulate matter (PM2.5) measurement. That needs a separate sensor.
- The ENS160 needs about 3 minutes of warm-up after each power-up. After the very first power-on it runs an initial start-up of about an hour, and its baseline keeps settling over the first day of continuous operation. Until then eCO2, TVOC and AQI are empty or jumpy.

## Trying the LD2412 in the v1 housing

The [v2](../v2/) radar, the HLK-LD2412, can be tested in the v1 Ø100 housing before the v2 PCB exists:

- **Housing.** Print the `_d100_ld2412` files from [`hardware/d100/`](../hardware/d100/), starting with `13_radar_seat_test_d100_ld2412.stl`. The board is taken as 11 × 28 × 1.0 mm from the datasheet; check yours with a caliper first and change `RADAR.update(...)` in `enclosure.py` if it differs (`python enclosure.py 100 ld2412`). The seat has four posts with snap lips and none at the ends, because both pin columns are at the ends.
- **Wiring.** Same as the LD2410B: +5V (not 3V3), GND, radar TX to GPIO5, radar RX to GPIO4. OUT stays unconnected.
- **Firmware.** [`firmware/ceiling-sensor-ld2412.yaml`](../firmware/ceiling-sensor-ld2412.yaml) is `ceiling-sensor.yaml` with the radar swapped: UART at 115200 baud, `gate_N` instead of `gN`, one `Radar max gate` instead of separate moving/still gates, and a `Radar learn empty room` button. Keep your own substitutions and Wi-Fi settings when you copy it.
