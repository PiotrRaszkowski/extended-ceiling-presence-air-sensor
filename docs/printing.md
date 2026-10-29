# Printing

All parts print without supports. The Ø80 files are in [`hardware/stl/`](../hardware/stl/) (STEP in [`hardware/step/`](../hardware/step/)); the Ø100 set is in [`hardware/d100/`](../hardware/d100/) with a `_d100` suffix. Calibration and radar window prints are shared by both sizes.

## Filament

PETG. White looks best on a ceiling.

Avoid anything with metal or carbon fibre in it. The radar looks through the face of the housing, and conductive fillers block 24 GHz. PLA works mechanically, but PETG handles the warm air under a ceiling better and the press-fit ribs were tuned in PETG.

## Settings

The default **0.16 mm** profile of QIDI Studio / Orca Slicer for PETG works fine, which is what the reference prints used. If you set it up by hand:

| Setting | Value |
|---|---|
| Layer height | 0.16 mm (0.2 mm also works) |
| Walls / perimeters | 3 |
| Infill | 15-20 %, any pattern |
| Supports | off |
| Brim | not needed; add one if your PETG lifts at the corners |
| **X-Y hole compensation / X-Y contour compensation** | **0** |

The last row matters. The seats rely on crush ribs that overlap the board outline by only 0.1 mm. Any slicer-side XY compensation changes that overlap and the boards end up either loose or impossible to push in.

## What to print, in order

| File | What it is | Orientation |
|---|---|---|
| `10_press_fit_calibration.stl` | Four ESP32-S3-Zero seats with 0.1 / 0.2 / 0.3 / 0.4 mm rib interference (1-4 notches on the edge) | flat, as exported |
| `11_seat_test_fit.stl` | The bottom 9 mm of the housing with every seat, for a test fit of all modules | face down |
| `00_print_plate_all_parts.stl` | Housing + ceiling base + chamber lid laid out on one plate (164 × 116 mm) | as exported |
| `01_housing.stl` | Housing: face, module seats, closed ENS160 chamber, three bayonet pins | face down |
| `02_ceiling_base.stl` | Ceiling base: 4 screw holes on a 60 mm spacing, Ø12 hole for the 12 V cable, bayonet ring | ceiling side down |
| `03_chamber_lid.stl` | Lid for the ENS160 chamber, pressed in from the top | plate down, collar up |
| `12_radar_window_samples.stl` | Three plates 0.8 / 1.6 / 3.7 mm (1/2/3 notches) for the radar window test below | flat |

1. Calibration first. Push an ESP32-S3-Zero into each of the four seats of `10_press_fit_calibration`. Pick the one where the board holds firmly but still goes in with a thumb, without shaving the ribs. On the reference printer (QIDI, PETG, 0.16 mm) that was **0.1 mm**, which is what the STLs use. If yours prefers 0.2, regenerate the parts with `RIB_INTERF = 0.2` (see [enclosure source](enclosure-source.md)).
2. Seat test. Print `11_seat_test_fit` and put every module in. Check that the radar's edge components fall between the ledges, that you can see the black BH1750 chip through its window from the outside, and that the PIR notches sit on the two keys.
3. Full set. Print the plate, or the three parts separately.

![Press-fit calibration print](images/press-fit-calibration.png)

![Seat test fit](images/seat-test-fit.png)

## Why the face is 3.7 mm in front of the radar

Most of the face is 1.6 mm. In front of the radar antenna it is 3.7 mm, which is half a wavelength of 24 GHz inside PETG (εr ≈ 2.8). A window that is a whole number of half-wavelengths thick should pass the signal with the least loss; other thicknesses can reduce range.

If you want to check it with your own filament, print `12_radar_window_samples.stl`. Lay the radar on each plate in turn, and once with nothing in front, switch on `Radar engineering mode` in Home Assistant (and enable the per-gate energy entities), stand 3-4 m away and compare `Radar g4 move energy` and `Radar g5 move energy`. If 3.7 mm comes out clearly worse than bare, set `RADAR["win_t"]` to the thickness that won and regenerate.
