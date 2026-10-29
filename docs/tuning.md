# Tuning and automations

## Radar range

The LD2410B splits its range into gates of 0.75 m (g0 = 0-0.75 m, g1 = 0.75-1.5 m and so on). Mounted on a 2.5-2.7 m ceiling and looking down, the floor is in gate 3, and the far corners of a big room are in gate 4-5.

1. Set `Radar max moving gate` and `Radar max still gate` to cover the room and no further. For a typical living room that's 4-5. The radar sees through drywall and doors, so anything larger starts picking up the hallway or the neighbour's room.
2. In Home Assistant, enable the disabled `Radar gN move energy` / `Radar gN still energy` entities. With the room empty, switch on `Radar engineering mode` and watch them for a minute or two.
3. Set each gate's move and still thresholds roughly 10-15 above the noise you saw. Gates with fans, curtains or plants need more margin.
4. Switch engineering mode off again afterwards. It makes the radar send a stream of extra updates.

Alternatively, switch on `Radar Bluetooth` and tune it with the HLKRadarTool app on a phone. Switch Bluetooth off when you're done, otherwise anyone nearby can change the radar settings.

## Presence hold time

`Presence hold time` (default 15 s) is added on top of the radar's own `Radar timeout`: occupancy turns off only after the radar has stopped reporting a target and then the hold time has passed. Raise it for rooms where people sit very still (an office, a reading corner), lower it for a corridor.

## Temperature offset

The AHT21 sits next to the ENS160 heater, the ESP is a few centimetres away, and air under the ceiling is often warmer than at head height. The default `Temperature offset` is −2.5 °C, which is a starting point, not a measured value. Expect to adjust it.

To calibrate it, put a reference thermometer at about 1.5 m for a day, compare the readings once things have settled, and adjust the offset. Humidity is recalculated automatically for the corrected temperature, so you don't need a second correction for it.

## PIR false triggers

Mini PIRs are sensitive to the ESP's own 2.4 GHz transmissions. If `PIR motion` fires in an empty room, uncomment `output_power: 8.5dB` in the `wifi:` block. If that isn't enough, add the optional 100 Ω + 47 µF filter from [wiring](wiring.md#optional-parts).

## Status LED

The ESP's WS2812 LED shows air quality: green for AQI 1-2, orange for 3, red for 4-5. There is no window for it in the face, so at most a little light gets out through the side vents. Turn it off with the `Air quality LED` switch if it bothers you. If it shows red when it should be green, change `channel_colors: RGB` to `GRB` in the YAML.

## Automation examples

Full file: [`homeassistant/automations.yaml`](../homeassistant/automations.yaml). Replace the entity IDs with yours.

Lights follow presence, but only when it's dark:

```yaml
- alias: Living room - lights follow presence
  mode: restart
  triggers:
    - trigger: state
      entity_id: binary_sensor.living_room_sensor_occupancy
  actions:
    - choose:
        - conditions:
            - condition: state
              entity_id: binary_sensor.living_room_sensor_occupancy
              state: "on"
            - condition: numeric_state
              entity_id: sensor.living_room_sensor_illuminance
              below: 30
          sequence:
            - action: light.turn_on
              target: {entity_id: light.living_room}
        - conditions:
            - condition: state
              entity_id: binary_sensor.living_room_sensor_occupancy
              state: "off"
          sequence:
            - action: light.turn_off
              target: {entity_id: light.living_room}
```

Boost the ventilation when the air gets stuffy and someone is in the room:

```yaml
- alias: Living room - ventilation boost on high eCO2
  triggers:
    - trigger: numeric_state
      entity_id: sensor.living_room_sensor_eco2
      above: 1100
      for: "00:10:00"
  conditions:
    - condition: state
      entity_id: binary_sensor.living_room_sensor_occupancy
      state: "on"
  actions:
    - action: fan.set_preset_mode
      target: {entity_id: fan.ventilation}
      data: {preset_mode: boost}
```

Keep the 10-minute `for:` on the eCO2 trigger. Without it, a short VOC spike from frying something sets off the boost.
