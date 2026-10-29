# Bill of materials

The enclosure is built around the exact modules below. Seats are modelled from caliper measurements of these boards, and the boards are held by 0.1 mm crush ribs, so a "compatible" module that is a millimetre bigger will not go in, and one that is smaller will rattle. Buy the same board types, then print [`11_seat_test_fit.stl`](../hardware/stl/11_seat_test_fit.stl) before the full housing to confirm they fit.

Prices are in PLN and were checked in October 2026. AliExpress prices move every week, so treat them as a rough guide.

## Modules

| # | Part | Measured size | Allegro (PL, one seller) | AliExpress | Notes |
|---|---|---|---|---|---|
| 1 | Waveshare ESP32-S3-Zero (ESP32-S3FH4R2, 4 MB flash, 2 MB PSRAM, WS2812 LED on GPIO21) | 23.69 × 17.98 mm, rounded corners | [elektroweb, 42.20 zł](https://allegro.pl/oferta/18479170722) | [PiShare Store, ~34 zł](https://pl.aliexpress.com/item/1005012733231291.html) | Get the genuine Waveshare board. Cheap "ESP32-S3-Zero" clones (TENSTAR and others, ~15 zł) look the same but I haven't checked their size or LED pin. Buy the version without soldered headers. |
| 2 | Hi-Link HLK-LD2410B 24 GHz mmWave radar | 35.06 × 7.0 mm | [elektroweb, 34.90 zł](https://allegro.pl/oferta/18803533204) | [Shenzhen Hi-Link store, ~16-20 zł](https://pl.aliexpress.com/item/1005007198006311.html), pick variant HLK-LD2410B | Not LD2410C (bigger, 2.54 mm header) and not LD2410B-P (with pins). The B has 1.27 mm pads; you solder thin wires straight to them. |
| 3 | HC-SR602 mini PIR | Ø15.89 mm round board, 13.65 mm across the two flats | [elektroweb, 6.50 zł](https://allegro.pl/oferta/18910728297) | [TENSTAR ROBOT Store, ~6 zł](https://pl.aliexpress.com/item/1005006039243790.html), pick variant HC-SR602 | The two flats on the board edge key it into the seat. |
| 4 | GY-302 BH1750 light sensor | 18.53 × 14.05 mm | [elektroweb, 8.20 zł](https://allegro.pl/oferta/18910743667) | [~7.5 zł](https://pl.aliexpress.com/item/1005010707054088.html) | The common blue GY-302 board with two mounting holes. |
| 5 | ENS160 + AHT21 air quality + temperature/humidity combo | 24.20 × 19.29 mm | [elektroweb, 49.90 zł](https://allegro.pl/oferta/17311708107) | [~30 zł](https://pl.aliexpress.com/item/1005006982502131.html) | The purple combo board with a milled slot around the AHT21 (thermal isolation from the ENS160 heater). Listings say "24 × 20 mm". |
| 6 | S09 buck-boost converter, fixed 5 V out (3-15 V in, 0.6 A, EN pin) | 18.75 × 13.95 mm | [elektroweb, 10.60 zł](https://allegro.pl/oferta/18910729409) | [~5 zł](https://pl.aliexpress.com/item/1005003203974721.html), pick the 5 V output variant | Fixed output on purpose: there is no trimmer you could accidentally turn up to 12 V. Bridge EN to VIN+ (see [wiring](wiring.md)). |

Allegro total with shipping from one seller: about 160 zł. AliExpress total: about 100 zł, plus waiting.

You can leave out the PIR. The firmware then runs presence on the radar alone, and the pull-down input simply reports "no motion". Nothing in the YAML needs to change.

## Small parts

| Part | Qty | Notes |
|---|---|---|
| Electrolytic capacitor 220 µF, ≥10 V | 1 | On the S09 output |
| Stranded wire AWG 26-28 | ~1 m | Silicone wire is easiest to route |
| Stripboard 2.54 mm | ~18 × 20 mm | Junction for 5V / GND / SDA / SCL / 3V3, one strip per net |
| Heat shrink tube 1.5-3 mm | a few cm | Insulating the stripboard and wire joints |
| Wago 221 or JST connector | 1 | 12 V input inside the box, with strain relief |
| Hot glue | | A dot on the board ends if a seat ever loosens |
| Foam strip ~1 mm | ~25 cm | Optional, on the housing rim against the ceiling |
| Plasticine / putty | a pinch | Seals the cable pass-through of the air chamber |

## Power and mounting

| Part | Notes |
|---|---|
| 12 V DC supply, ≥0.5 A | The sensor should draw about 0.15 A at 12 V (estimate). The S09 accepts 3-15 V, so a 5 V or 9 V supply also works. |
| 2-4 countersunk wood screws, head ≤ 8.6 mm | The base hole spacing is 60 mm, so it screws onto a standard Ø60 flush box. The screw heads clear the bayonet ring by only 0.3 mm, so pan-head screws will not fit. |

## Filament

Roughly 50 g of PETG for the full set (housing, base, chamber lid); the walls are thin, so the parts print nearly solid either way. White looks best on a ceiling. Do not use metal-filled or carbon-filled filament: the face has to let 24 GHz through. See [printing](printing.md).
