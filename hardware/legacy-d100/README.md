# Ø100 version (v10)

The previous, larger version of the housing: Ø100 × 30 mm, same modules, same wiring, same firmware. It has more room inside, which makes wiring easier, and it covers a bigger ceiling patch.

v9 of this size was printed in PETG and test-fitted. v10 (these files) adds the fixes from that print but hasn't been reprinted: ESP ribs moved away from its rounded corners, a firmer PIR seat, a tighter chamber lid and a slightly tighter buck converter seat. v11 then shrank the design to Ø80 with the same seats.

Only STL files are kept here. The parametric source in [`../source/enclosure.py`](../source/enclosure.py) generates the current Ø80 layout.

| File | Part |
|---|---|
| `00_print_plate_all_parts_d100.stl` | housing + base + lid on one plate (204 × 134 mm) |
| `01_housing_d100.stl` | housing |
| `02_ceiling_base_d100.stl` | ceiling base (60 mm screw spacing) |
| `03_chamber_lid_d100.stl` | ENS160 chamber lid |
| `11_seat_test_fit_d100.stl` | bottom 9 mm for a test fit |

Print settings and assembly are the same as for the current version, see [printing](../../docs/printing.md) and [assembly](../../docs/assembly.md). The module layout inside is different from the Ø80 pictures.
