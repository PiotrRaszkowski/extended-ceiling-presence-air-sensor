// Ceiling-mounted enclosure for an ESP32 presence + air-quality sensor.
// OpenSCAD port of hardware/source/enclosure.py (CadQuery, v13). One file, two sizes (Ø80 / Ø100).
//
// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Piotr Raszkowski
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
// associated documentation files (the "Software"), to deal in the Software without restriction,
// including without limitation the rights to use, copy, modify, merge, publish, distribute,
// sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions: The above copyright notice and this
// permission notice shall be included in all copies or substantial portions of the Software.
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
//
// Parts:
//   housing               - Ø80/Ø100 x 30 mm "can": face, module seats, ENS160 chamber, bayonet pins
//   ceiling_base          - screwed to the ceiling, ring with 3 blind bayonet grooves + detents
//   chamber_lid           - press-fit into the ENS160 chamber (printed plate down, plug up)
//   print_plate           - housing + ceiling base + chamber lid side by side
//   seat_test_fit         - bottom 9 mm of the housing (quick test-fit of the modules)
//   press_fit_calibration - 4 ESP32-S3-Zero seats with rib interference 0.1 / 0.2 / 0.3 / 0.4
//   radar_window_samples  - 0.8 / 1.6 / 3.7 mm tiles (1 / 2 / 3 notches)
//
// Housing coordinates: z = 0 is the face (room side), z = h is the rim at the ceiling.
// "Inside view" = looking down from the ceiling onto the face; x/y of the modules are given in it.
// All seat geometry (walls, ribs, ledges, windows) is derived from the measured board size +
// clr + rib_interf, so a slightly different module only needs its caliper dimensions typed in.
// Works in OpenSCAD 2021.01 and newer (newer + Manifold backend renders much faster).

/* [Part] */
// Housing diameter (mm): selects the module layout
size = 80; // [80, 100]
// Part to render
part = "housing"; // [housing, ceiling_base, chamber_lid, print_plate, seat_test_fit, press_fit_calibration, radar_window_samples]
// Facets per full circle (higher = smoother, slower)
resolution = 128; // [32:8:512]

/* [General fit] */
// Crush rib reach into the board outline, per side (mm); 0.1 = calibration variant 1
rib_interf = 0.1; // [0:0.05:0.5]
// Total wall/post clearance around a board (mm, 0.4 per side); only the ribs hold the board
clr = 0.8;
// Crush rib base width (mm, > 2x nozzle line width)
rib_w = 2.4;
// Crush rib flat top width (mm)
rib_top = 0.8;
// Crush rib height above the board underside (mm)
rib_h = 2.0;
// Seat wall and post thickness (mm)
seat_t = 1.2;
// How far posts/walls rise above the board underside (mm)
post_h = 2.5;
// Width of the support rails under the boards (mm)
rail_w = 1.5;
// Housing side wall thickness (mm)
wall = 2.0;
// Face thickness (mm)
face = 1.6;
// Housing height, face to ceiling (mm)
h = 30.0;
// Chamfer on the face edge (mm)
edge_chamfer = 1.5;

/* [Bayonet & base] */
// Base plate thickness (mm)
base_plate_t = 2.5;
// How deep the base ring reaches into the housing (mm)
ring_depth = 10.0;
// Base ring wall thickness (mm)
ring_t = 3.0;
// Radial gap between base ring and housing inner wall (mm)
ring_clr = 0.4;
// Pin centre distance below the housing rim (mm)
pin_depth = 6.0;
// Pin width, tangential (mm)
pin_w = 5.0;
// Pin height, axial (mm)
pin_hgt = 3.0;
// How far a pin sticks out of the housing inner wall (mm)
pin_protrude = 1.8;
// Bayonet groove depth into the ring (mm)
groove_depth = 1.8;
// Groove clearance above the pin, ceiling side (mm)
slot_clr_top = 0.3;
// Groove clearance below the pin, load-bearing side (mm)
slot_clr_bot = 0.8;
// Bayonet twist angle (deg)
lock_angle = 25.0;
// Detent bump height (mm)
detent_h = 0.6;
// Detent flank angle (deg)
detent_flank = 45.0;
// Pin angles (deg); keep +x (ENS160 chamber) free
pin_angles = [60.0, 180.0, 300.0];
// Screw spacing (mm, 60 = standard Ø60 junction box)
screw_spacing = 60.0;
// Screw hole diameter (mm)
screw_d = 4.2;
// Countersink diameter (mm, 90 deg countersink on the room side)
csk_d = 8.6;
// Cable hole diameter in the base centre (mm)
cable_hole_d = 12.0;

/* [ENS160 chamber] */
// Inner chamber wall position x, Ø80 layout (mm)
ch_x_80 = 12.0;
// Inner chamber wall position x, Ø100 layout (mm)
ch_x_100 = 21.0;
// Top of the chamber walls = underside of the lid (mm from the face's outside)
ch_top = 23.0;
// I2C cable pass-through width (mm)
wire_w = 5.0;
// I2C cable pass-through depth from the wall top (mm)
wire_d = 2.5;
// Lid plate thickness (mm)
lid_t = 1.5;
// Lid plug height (mm)
plug_h = 2.0;
// Clearance between lid plug and chamber walls, per side (mm)
lid_plug_clr = 0.25;
// Gap kept between the chamber top part and the base ring, radial and axial (mm)
step_clr = 0.5;

/* [Radar (LD2410B)] */
// Board size x, short side (mm)
radar_x = 7.0;
// Board size y, long side (mm)
radar_y = 35.06;
// Board centre, Ø80 layout [x, y] (mm)
radar_pos_80 = [4.6, -5.0];
// Board centre, Ø100 layout [x, y] (mm)
radar_pos_100 = [0.0, 4.0];
// Plastic in front of the antenna (mm)
radar_win_t = 3.7;
// Recess under the board, above the window (mm)
radar_gap = 2.0;
// Ledge width under each long edge (mm)
radar_ledge = 0.7;
// Ledge segments [from, to, from, to] in mm from the end without the connector (-y)
radar_ledge_segments = [1.0, 15.0, 25.0, 30.0];
// Rib positions along the long walls, from the board centre (mm)
radar_rib_y = [-11.0, 0.0, 11.0];
// Extra rib interference for this seat (mm)
radar_rib_extra = 0.0;

/* [PIR (HC-SR602)] */
// Board diameter (mm)
pir_d = 15.89;
// Width across the two board notches (mm)
pir_notch_w = 13.65;
// Lens hole diameter (lens Ø + 0.3, mm)
pir_lens_d = 10.3;
// Header direction, Ø80 layout (deg)
pir_hdr_angle_80 = 180.0;
// Header direction, Ø100 layout (deg)
pir_hdr_angle_100 = 270.0;
// Board centre, Ø80 layout [x, y] (mm)
pir_pos_80 = [15.0, 24.0];
// Board centre, Ø100 layout [x, y] (mm)
pir_pos_100 = [-22.0, 18.0];
// Width of the keys in the board notches (mm)
pir_key_w = 1.6;
// Board underside above the face (mm)
pir_standoff = 2.2;
// Extra opening of the 45 deg cone on the room side (mm)
pir_cone = 3.2;
// Angular gap in the support ring for the header pin ends (deg)
pir_hdr_gap = 70.0;
// Outer radius of the support ring around the lens (mm)
pir_boss_r = 6.3;
// Radial clearance of the round seat (mm)
pir_seat_clr = 0.15;
// Crush rib base width on the arcs (mm)
pir_rib_w = 2.0;
// Extra rib interference for this seat (mm)
pir_rib_extra = 0.0;

/* [BH1750 (GY-302)] */
// Board size x (mm)
bh_x = 14.05;
// Board size y, pins on -y (mm)
bh_y = 18.53;
// Board centre, Ø80 layout [x, y] (mm)
bh_pos_80 = [-9.93, 22.27];
// Board centre, Ø100 layout [x, y] (mm)
bh_pos_100 = [-26.0, -8.5];
// Board underside above the face (mm)
bh_standoff = 2.5;
// Ledge width under each long edge (mm)
bh_ledge = 0.8;
// Sensor IC offset from the board centre towards the holes, +y (mm)
bh_chip_dy = 2.5;
// Light window size x (mm)
bh_win_x = 4.0;
// Light window size y (mm)
bh_win_y = 6.0;
// Rib positions on the x walls, from the board centre (mm)
bh_rib_y = [-5.0, 5.0];
// Extra rib interference, Ø80 layout (mm; v13 print came out loose)
bh_rib_extra_80 = 0.05;
// Extra rib interference, Ø100 layout (mm)
bh_rib_extra_100 = 0.0;

/* [ESP32-S3-Zero] */
// Board size x (mm)
esp_x = 23.69;
// Board size y (mm)
esp_y = 17.98;
// Board centre, Ø80 layout [x, y] (mm)
esp_pos_80 = [-14.75, 0.0];
// Board centre, Ø100 layout [x, y] (mm)
esp_pos_100 = [-8.0, -31.0];
// Rail height = board underside above the face (mm)
esp_rail_h = 3.0;
// Rail offset from the board centre line, +-y (mm)
esp_rail_y = 4.0;
// Rail start, in from the -x short edge (pads) (mm)
esp_rail_in_l = 3.0;
// Rail end, in from the +x short edge (mm)
esp_rail_in_r = 1.0;
// Corner post leg length (mm)
esp_post_leg = 4.4;
// Rib distance in from the (rounded) board corners (mm)
esp_rib_in = 3.0;
// Extra rib interference for this seat (mm; not applied to the calibration print)
esp_rib_extra = 0.0;

/* [Buck (S09)] */
// Board size x (mm)
buck_x = 18.75;
// Board size y (mm)
buck_y = 13.95;
// Board centre, Ø80 layout [x, y] (mm)
buck_pos_80 = [-12.28, -19.98];
// Board centre, Ø100 layout [x, y] (mm)
buck_pos_100 = [2.0, 34.0];
// Rail height = board underside above the face (mm)
buck_rail_h = 3.0;
// Rail offset from the board centre line, +-y (mm)
buck_rail_y = 3.5;
// Rail length (mm)
buck_rail_len = 10.0;
// Post positions on the long (y) walls, from the board centre (mm)
buck_post_x = [-4.0, 4.0];
// Post width on the long walls (mm)
buck_post_w = 3.0;
// Post width on the short (x) walls (mm)
buck_end_post_w = 2.5;
// Rib positions on the long walls, from the board centre (mm)
buck_rib_x = [-4.0, 4.0];
// Extra rib interference for this seat (mm)
buck_rib_extra = 0.05;

/* [ENS160+AHT21] */
// Board size x, pin edge to housing wall (mm)
ens_x = 19.29;
// Board size y (mm)
ens_y = 24.20;
// Rail height = board underside above the face (mm)
ens_rail_h = 3.0;
// Rail positions, mm from the pin edge (AHT21 cutout spans ~8.5-16.2)
ens_rails = [4.5, 18.0];
// Rib positions on the chamber side walls, mm from the pin edge
ens_rib_x = [5.0, 14.5];
// Rib positions on the inner chamber wall, +-y (mm)
ens_wall_rib_y = 6.5;
// End stop positions, +-y (mm)
ens_stop_y = 8.0;
// Face vent slot positions, mm from the pin edge
ens_vent_dx = [7.2, 10.0, 12.8, 15.6];
// Extra rib interference for this seat (mm)
ens_rib_extra = 0.0;

/* [Test prints] */
// Rib interference variants of the press-fit calibration print (mm)
cal_values = [0.1, 0.2, 0.3, 0.4];
// Height of the seat test fit (mm)
fit_z_cut = 9.0;
// Radar window sample thicknesses (mm)
radar_samples = [0.8, 1.6, 3.7];

/* [Hidden] */
$fn = resolution;
eps = 0.01;

// ---------------------------------------------------------------------------------------------
// Derived values (names follow the Python source)
// ---------------------------------------------------------------------------------------------
r_out = size / 2;                  // outer radius
r_in = r_out - wall;               // inner radius
ring_r_out = r_in - ring_clr;
ring_r_in = ring_r_out - ring_t;
ring_r_groove = ring_r_out - groove_depth;   // bayonet groove bottom
z_lo = pin_depth - pin_hgt / 2 - slot_clr_top;   // groove edge on the ceiling side
z_hi = pin_depth + pin_hgt / 2 + slot_clr_bot;   // load-bearing groove edge

ch_x = size == 80 ? ch_x_80 : ch_x_100;
z_step = h - ring_depth - step_clr;            // highest point of the chamber next to the housing wall
r_up = r_in - ring_clr - ring_t - step_clr;    // outer face of the chamber wall above z_step
tall = ch_top > z_step;

radar_pos = size == 80 ? radar_pos_80 : radar_pos_100;
pir_pos = size == 80 ? pir_pos_80 : pir_pos_100;
pir_hdr_angle = size == 80 ? pir_hdr_angle_80 : pir_hdr_angle_100;
pir_arcs = [[65.0, 115.0], [210.0, 232.0], [308.0, 330.0]];   // retaining arcs (deg, header at 270)
bh_pos = size == 80 ? bh_pos_80 : bh_pos_100;
bh_rib_extra = size == 80 ? bh_rib_extra_80 : bh_rib_extra_100;
esp_pos = size == 80 ? esp_pos_80 : esp_pos_100;
buck_pos = size == 80 ? buck_pos_80 : buck_pos_100;

radar_seat_z = radar_win_t + radar_gap;
bh_seat_z = face + bh_standoff;
esp_seat_z = face + esp_rail_h;
buck_seat_z = face + buck_rail_h;
ens_x0 = ch_x + seat_t + clr / 2;              // ENS160 board edge on the pass-through side
ens_seat_z = face + ens_rail_h;
ens_hy = (ens_y + clr) / 2 + 0.05;             // half of the chamber interior along y

lid_far = 49.0;                                // lid stock reaches past any chamber radius

// ---------------------------------------------------------------------------------------------
// Helpers (same semantics as the Python helpers)
// ---------------------------------------------------------------------------------------------
module box(cx, cy, z0, sx, sy, sz) { translate([cx - sx / 2, cy - sy / 2, z0]) cube([sx, sy, sz]); }

module cyl(r, z0, hh, cx = 0, cy = 0) { translate([cx, cy, z0]) cylinder(r = r, h = hh); }

module ring(ri, ro, z0, hh) { translate([0, 0, z0]) linear_extrude(hh) difference() { circle(ro); circle(ri); } }

// wedge (sector) polygon from a0 to a1 [deg], 24 straight steps at r = 80 (as in the Python)
function wedge_pts(a0, a1, r = 80.0, steps = 24) =
    concat([[0, 0]], [for (i = [0:steps]) let(a = a0 + (a1 - a0) * i / steps) [r * cos(a), r * sin(a)]]);

module sector(ri, ro, a0, a1, z0, hh, cx = 0, cy = 0) {
    translate([cx, cy, z0]) linear_extrude(hh) intersection() {
        difference() { circle(ro); circle(ri); }
        polygon(wedge_pts(a0, a1));
    }
}

module rect_walls(cx, cy, ix, iy, z0, hh, t = seat_t) {
    difference() { box(cx, cy, z0, ix + 2 * t, iy + 2 * t, hh); box(cx, cy, z0 - 1, ix, iy, hh + 2); }
}

// box that removes part of one seat wall: side = "+x", "-x", "+y", "-y"
module open_side_cut(cx, cy, ix, iy, z0, hh, side, frac = 0.7, t = seat_t) {
    sgn = side[0] == "+" ? 1 : -1;
    if (side[1] == "x") box(cx + sgn * (ix / 2 + t / 2), cy, z0 - 1, t + 1, iy * frac, hh + 2);
    else box(cx, cy + sgn * (iy / 2 + t / 2), z0 - 1, ix * frac, t + 1, hh + 2);
}

module corner_posts(cx, cy, ix, iy, z0, hh, leg = 2.2, t = seat_t) {
    difference() {
        for (sx = [-1, 1], sy = [-1, 1])
            box(cx + sx * (ix / 2 + t - (leg + t) / 2), cy + sy * (iy / 2 + t - (leg + t) / 2), z0, leg + t, leg + t, hh);
        box(cx, cy, z0 - 1, ix, iy, hh + 2);
    }
}

module side_posts(cx, cy, ix, iy, z0, hh, side, offsets, w, t = seat_t) {
    sgn = side[0] == "+" ? 1 : -1;
    for (o = offsets)
        if (side[1] == "y") box(cx + o, cy + sgn * (iy / 2 + t / 2), z0, w, t, hh);
        else box(cx + sgn * (ix / 2 + t / 2), cy + o, z0, t, w, hh);
}

// Trapezoid crush rib: base on the wall plane at (px, py), flat top offset by p in direction
// (nx, ny) towards the seat centre. Default p = clr/2 + rib_interf.
module rib(px, py, nx, ny, z0, hh = rib_h, p, w = rib_w) {
    pp = is_undef(p) ? clr / 2 + rib_interf : p;
    tx = -ny; ty = nx;
    back = 0.3;          // overlap into the wall
    tw = rib_top / 2;
    translate([0, 0, z0]) linear_extrude(hh) polygon([
        [px + tx * w / 2 - nx * back, py + ty * w / 2 - ny * back],
        [px - tx * w / 2 - nx * back, py - ty * w / 2 - ny * back],
        [px - tx * w / 2, py - ty * w / 2],
        [px - tx * tw + nx * pp, py - ty * tw + ny * pp],
        [px + tx * tw + nx * pp, py + ty * tw + ny * pp],
        [px + tx * w / 2, py + ty * w / 2]]);
}

// Crush ribs on the walls of a rectangular ix x iy seat. xs: positions (dx) on the +-y walls,
// ys: positions (dy) on the +-x walls; ends_x / ends_y limit the walls (e.g. ends_y = [1]).
module ribs_rect(cx, cy, ix, iy, z0, xs = [], ys = [], ends_x = [-1, 1], ends_y = [-1, 1], hh = rib_h, p) {
    for (sy = ends_y, dx = xs) rib(cx + dx, cy + sy * iy / 2, 0, -sy, z0, hh, p);
    for (sx = ends_x, dy = ys) rib(cx + sx * ix / 2, cy + dy, -sx, 0, z0, hh, p);
}

module radial_slots(angles, z0, hh, width = 2.0, r = r_out - wall / 2) {
    for (a = angles) rotate([0, 0, a]) box(r, 0, z0, wall + 2, width, hh);
}

// Note: the three CadQuery cones (PIR lens cone, chamber 45 deg step, countersinks) are built as
// revolved (r, z) profiles merged with the cylinders they touch, so that no separate cone and
// cylinder meet along a shared circle (that produced sliver/non-manifold edges in STL export).

// ---------------------------------------------------------------------------------------------
// Module seats. Each module takes the body built so far as children() and applies its
// unions/cuts in the same order as the Python function.
// ---------------------------------------------------------------------------------------------
module seat_radar() {
    cx = radar_pos[0]; cy = radar_pos[1];
    ix = radar_x + clr; iy = radar_y + clr;
    y_end = cy - radar_y / 2;                       // end without the connector
    lw = ix / 2 - (radar_x / 2 - radar_ledge);      // ledge from (board edge - ledge) to the wall
    segs = radar_ledge_segments;
    union() {
        difference() {
            union() {
                children();
                box(cx, cy, face - eps, ix + 2 * seat_t, iy + 2 * seat_t, radar_seat_z - face + eps);   // pedestal
            }
            box(cx, cy, radar_win_t, ix, iy, radar_seat_z - radar_win_t + eps);   // recess under the board
        }
        for (i = [0:2:len(segs) - 2], sx = [-1, 1])
            box(cx + sx * (ix / 2 - lw / 2), y_end + (segs[i] + segs[i + 1]) / 2, radar_win_t - eps,
                lw, segs[i + 1] - segs[i], radar_seat_z - radar_win_t + eps);
        rect_walls(cx, cy, ix, iy, radar_seat_z - eps, post_h + eps);
        ribs_rect(cx, cy, ix, iy, radar_seat_z, xs = [0.0], ys = radar_rib_y, p = clr / 2 + rib_interf + radar_rib_extra);
    }
}

module seat_pir() {
    cx = pir_pos[0]; cy = pir_pos[1];
    r_b = pir_d / 2 + pir_seat_clr;                 // seat radius (board is located by the keys)
    z_seat = face + pir_standoff;
    h_top = pir_standoff + 1.2 + 1.5;               // wall height above the face
    ro = pir_hdr_angle - 270.0;                     // rotation vs the base layout (header at 270 deg)
    r_key = pir_notch_w / 2 + 0.1;
    r_cone = pir_lens_d / 2 + pir_cone / 2;
    difference() {
        union() {
            children();
            // support ring around the lens, recess for the header pin ends
            sector(pir_lens_d / 2 + 0.2, pir_boss_r, pir_hdr_angle + pir_hdr_gap / 2,
                   pir_hdr_angle - pir_hdr_gap / 2 + 360, face - eps, pir_standoff + eps, cx, cy);
            // keys in the board notches
            for (a = [ro, 180.0 + ro]) translate([cx, cy, 0]) rotate([0, 0, a])
                box((r_key + r_b + seat_t) / 2, 0, face - eps, r_b + seat_t - r_key, pir_key_w, h_top + eps);
            // retaining arcs with a crush rib in the middle of each
            for (arc = pir_arcs) {
                a0 = arc[0] + ro; a1 = arc[1] + ro; a = (a0 + a1) / 2;
                sector(r_b, r_b + seat_t, a0, a1, face - eps, h_top + eps, cx, cy);
                rib(cx + r_b * cos(a), cy + r_b * sin(a), -cos(a), -sin(a), z_seat,
                    p = (r_b - pir_d / 2) + rib_interf + pir_rib_extra, w = pir_rib_w);
            }
        }
        // lens hole (z -1 .. face + 1) + 45 deg outward cone (from r_cone + 0.5 at z = -0.5 up to the
        // lens radius), as one revolved profile (the cone tip ends exactly on the face plane)
        lr = pir_lens_d / 2; rc = r_cone + 0.5; zc = -0.5 + (rc - lr); ztop = max(face + 1, zc);
        translate([cx, cy, 0]) rotate_extrude() polygon(concat(
            [[0, -1], [lr, -1], [lr, -0.5], [rc, -0.5]],
            zc < ztop ? [[lr, zc]] : [],
            [[lr, ztop], [0, ztop]]));
    }
}

module seat_bh() {
    cx = bh_pos[0]; cy = bh_pos[1];
    ix = bh_x + clr; iy = bh_y + clr;
    lw = ix / 2 - (bh_x / 2 - bh_ledge);
    difference() {
        union() {
            children();
            for (sx = [-1, 1]) box(cx + sx * (ix / 2 - lw / 2), cy, face - eps, lw, iy, bh_standoff + eps);   // ledges
            difference() {   // walls, open on -y (pins)
                rect_walls(cx, cy, ix, iy, face - eps, bh_standoff + post_h + eps);
                open_side_cut(cx, cy, ix, iy, face, bh_standoff + post_h, "-y");
            }
            ribs_rect(cx, cy, ix, iy, bh_seat_z, xs = [0.0], ys = bh_rib_y, ends_y = [1],
                      p = clr / 2 + rib_interf + bh_rib_extra);
        }
        box(cx, cy + bh_chip_dy, -1, bh_win_x, bh_win_y, face + 2);   // light window
    }
}

module seat_esp(interf = rib_interf, extra = esp_rib_extra) {
    cx = esp_pos[0]; cy = esp_pos[1];
    ix = esp_x + clr; iy = esp_y + clr;
    x0 = cx - esp_x / 2 + esp_rail_in_l; x1 = cx + esp_x / 2 - esp_rail_in_r;
    union() {
        children();
        for (sy = [-1, 1]) box((x0 + x1) / 2, cy + sy * esp_rail_y, face - eps, x1 - x0, rail_w, esp_rail_h + eps);
        corner_posts(cx, cy, ix, iy, face - eps, esp_rail_h + post_h + eps, leg = esp_post_leg);
        ribs_rect(cx, cy, ix, iy, esp_seat_z, xs = [-(ix / 2 - esp_rib_in), ix / 2 - esp_rib_in],
                  ys = [-(iy / 2 - esp_rib_in), iy / 2 - esp_rib_in], p = clr / 2 + interf + extra);
    }
}

module seat_buck() {
    cx = buck_pos[0]; cy = buck_pos[1];
    ix = buck_x + clr; iy = buck_y + clr;
    hh = buck_rail_h + post_h + eps;
    union() {
        children();
        for (sy = [-1, 1]) box(cx, cy + sy * buck_rail_y, face - eps, buck_rail_len, rail_w, buck_rail_h + eps);
        side_posts(cx, cy, ix, iy, face - eps, hh, "+y", buck_post_x, buck_post_w);
        side_posts(cx, cy, ix, iy, face - eps, hh, "-y", buck_post_x, buck_post_w);
        side_posts(cx, cy, ix, iy, face - eps, hh, "+x", [0.0], buck_end_post_w);   // pin corners stay clear
        side_posts(cx, cy, ix, iy, face - eps, hh, "-x", [0.0], buck_end_post_w);
        ribs_rect(cx, cy, ix, iy, buck_seat_z, xs = buck_rib_x, ys = [0.0], p = clr / 2 + rib_interf + buck_rib_extra);
    }
}

// Closed ENS160 chamber: inner wall + two side walls + the housing wall.
module chamber_walls() {
    hy = ens_hy;
    union() {
        intersection() {
            union() {
                box(ch_x + seat_t / 2, 0, face - eps, seat_t, 2 * (hy + seat_t), ch_top - face + eps);
                for (sy = [-1, 1])
                    box((ch_x + r_in + 1) / 2, sy * (hy + seat_t / 2), face - eps, r_in + 1 - ch_x, seat_t, ch_top - face + eps);
            }
            // clip: above z_step the chamber must stay inside the base ring
            if (tall) union() { cyl(r_in + 0.5, 0, z_step); cyl(r_up, z_step - eps, h - z_step + eps); }
            else cyl(r_in + 0.5, 0, h);
        }
        // tall chamber: 45 deg step from the housing wall in to the upper outer wall (prints without
        // support) + the upper wall ring. Python: (cyl - cone) U ring, cut to the chamber footprint;
        // built here as ONE revolved (r, z) profile so no coincident cone/cylinder faces reach the
        // CSG kernel. It lies inside the clip, so clipping it is a no-op.
        if (tall) intersection() {
            dz = r_in + 0.2 - (r_up - seat_t);
            rotate_extrude() polygon([
                [r_in + 0.2, z_step - dz], [r_in + 0.5, z_step - dz], [r_in + 0.5, z_step],
                [r_up, z_step], [r_up, ch_top], [r_up - seat_t, ch_top],
                [r_up - seat_t, z_step - eps], [r_up - seat_t + eps, z_step - eps]]);
            box((ch_x + r_in + 1) / 2, 0, 0, r_in + 1 - ch_x, 2 * (hy + seat_t), h);   // chamber footprint
        }
    }
}

module chamber_body() {
    hy = ens_hy;
    ix_face_in = ch_x + seat_t;                    // inner wall plane
    x_stop = ens_x0 + ens_x + clr / 2;             // end stop plane
    p_y = hy - ens_y / 2 + rib_interf + ens_rib_extra;
    union() {
        difference() {
            union() {
                difference() {
                    union() { children(); chamber_walls(); }
                    // cable pass-through (middle of the inner wall, from the top)
                    box(ch_x + seat_t / 2, 0, ch_top - wire_d, seat_t + 2, wire_w, wire_d + 0.5);
                }
                // rails under the flat board underside
                for (dx = ens_rails) box(ens_x0 + dx, 0, face - eps, rail_w, 2 * hy - 1.0, ens_rail_h + eps);
                // end stops on the housing-wall side
                for (sy = [-1, 1]) box(x_stop + 0.6, sy * ens_stop_y, face - eps, 1.2, 3.0, ens_rail_h + 1.6 + 1.5);
            }
            // vent slots in the face between the rails, behind the board, and in the housing wall
            for (dx = ens_vent_dx) box(ens_x0 + dx, 0, -1, 1.6, 2 * hy - 5.0, face + 1.01);
            box(ens_x0 + ens_x + 2.6, 0, -1, 1.6, 2 * hy - 9.0, face + 1.01);
            radial_slots([-10.0, -3.4, 3.4, 10.0], 3.5, 4.5);   // lower band
            radial_slots([-10.0, -3.4, 3.4, 10.0], 9.0, 3.0);   // upper band under the lid (outlet)
        }
        // crush ribs: chamber side walls (+-y), inner wall and end stops (x)
        for (sy = [-1, 1]) {
            for (dx = ens_rib_x) rib(ens_x0 + dx, sy * hy, 0, -sy, ens_seat_z, p = p_y);
            rib(ix_face_in, sy * ens_wall_rib_y, 1, 0, ens_seat_z, p = ens_x0 - ix_face_in + rib_interf + ens_rib_extra);
            rib(x_stop, sy * ens_stop_y, -1, 0, ens_seat_z, p = clr / 2 + rib_interf + ens_rib_extra);
        }
    }
}

// ---------------------------------------------------------------------------------------------
// Housing
// ---------------------------------------------------------------------------------------------
module housing_shell() {
    difference() {
        rotate_extrude() polygon([[0, 0], [r_out - edge_chamfer, 0], [r_out, edge_chamfer], [r_out, h], [0, h]]);
        cyl(r_in, face, h);
    }
}

module housing() {
    z_pin = h - pin_depth - pin_hgt / 2;
    difference() {
        union() {
            difference() {
                seat_pir() chamber_body() seat_buck() seat_esp() seat_bh() seat_radar() housing_shell();
                // electronics ventilation: side wall opposite the chamber
                radial_slots([148:8:212], 3.5, 5.0);    // inlet (low)
                radial_slots([148:8:212], 12.5, 5.5);   // outlet (high)
            }
            // bayonet pins
            for (a = pin_angles) rotate([0, 0, a])
                box(r_in - pin_protrude / 2 + 0.25, 0, z_pin, pin_protrude + 0.5, pin_w, pin_hgt);
        }
        // alignment marks on the rim
        for (a = pin_angles) rotate([0, 0, a]) box(r_out, 0, h - 3.0, 1.6, 1.4, 4.0);
    }
}

// ---------------------------------------------------------------------------------------------
// Chamber lid (print orientation: plate on the bed, plug up)
// ---------------------------------------------------------------------------------------------
module chamber_lid() {
    hy = ens_hy;
    c = lid_plug_clr;
    r_plate = tall ? r_up : r_in - 0.4;
    r_plug = tall ? r_up - seat_t - c : r_in - 0.45;
    x_plug = ch_x + seat_t + c;
    union() {
        intersection() {
            box((ch_x + lid_far) / 2, 0, 0, lid_far - ch_x, 2 * (hy + seat_t), lid_t);
            cyl(r_plate, -1, 10);
        }
        difference() {
            intersection() {
                box((x_plug + lid_far) / 2, 0, lid_t - eps, lid_far - x_plug, 2 * (hy - c), plug_h + eps);
                cyl(r_plug, -1, 10);
            }
            box((x_plug + lid_far) / 2, 0, lid_t - 1, lid_far, 2 * (hy - c - 1.2), plug_h + 3);   // hollow plug
            box(ch_x + seat_t + 2, 0, lid_t - 1, 6, wire_w + 0.5, plug_h + 3);   // notch above the pass-through
        }
        // crush ribs on the outside of the plug (press against the chamber side walls)
        for (sy = [-1, 1], xx = tall ? [ch_x + 6.0, ch_x + 15.0] : [ch_x + 8.0, ch_x + 20.0])
            rib(xx, sy * (hy - c), 0, sy, lid_t - eps, hh = plug_h, p = c + rib_interf);
    }
}

// ---------------------------------------------------------------------------------------------
// Ceiling base (z = 0 is the ceiling side; print ceiling side down)
// ---------------------------------------------------------------------------------------------
module detent(angle) {
    hb = detent_h / tan(detent_flank);
    rotate([0, 0, angle]) translate([ring_r_groove - 0.2, 0, 0])
        rotate([90, 0, 90]) linear_extrude(ring_r_out - ring_r_groove + 0.2)   // profile in (y, z), extruded along +x
            polygon([[-hb, z_hi + 0.3], [hb, z_hi + 0.3], [hb, z_hi], [0.0, z_hi - detent_h], [-hb, z_hi]]);
}

module ceiling_base() {
    r_g = (ring_r_groove + ring_r_out) / 2;
    half_w = ((pin_w + 0.6) / 2) / r_g * 180 / PI;
    pin_half = (pin_w / 2) / r_g * 180 / PI;
    hb = detent_h / tan(detent_flank);
    csk_h = (csk_d - screw_d) / 2;
    screws = [[screw_spacing / 2, 0], [-screw_spacing / 2, 0], [0, screw_spacing / 2], [0, -screw_spacing / 2]];
    difference() {
        union() {
            difference() {
                union() { cyl(ring_r_out, 0, base_plate_t); ring(ring_r_in, ring_r_out, 0, ring_depth); }
                for (a = pin_angles) {
                    // groove NOT through, cut from outside: vertical entry + horizontal channel
                    sector(ring_r_groove, ring_r_out + 1, a - half_w, a + half_w, z_lo, ring_depth + 1 - z_lo);
                    sector(ring_r_groove, ring_r_out + 1, a - half_w, a + lock_angle + half_w, z_lo, z_hi - z_lo);
                }
            }
            // triangular detent on the load-bearing edge
            for (a = pin_angles) detent(a + lock_angle - pin_half - (hb + 0.4) / r_g * 180 / PI);
        }
        cyl(cable_hole_d / 2, -1, base_plate_t + 2);   // cable hole
        // screw holes, 90 deg countersink on the room side (z = base_plate_t); Python: cylinder +
        // cone + cylinder above the plate, built here as one revolved profile
        for (s = screws) translate([s[0], s[1], 0]) rotate_extrude() polygon([
            [0, -1], [screw_d / 2, -1], [screw_d / 2, base_plate_t - csk_h], [csk_d / 2, base_plate_t],
            [csk_d / 2, base_plate_t + 2], [0, base_plate_t + 2]]);
    }
}

// ---------------------------------------------------------------------------------------------
// Test prints
// ---------------------------------------------------------------------------------------------
module radar_window_samples() {
    for (i = [0:len(radar_samples) - 1]) {
        t = radar_samples[i];
        difference() {
            box(i * 20.0, 0, 0, 16.0, 44.0, t);
            for (k = [0:i]) box(i * 20.0 - 4 + k * 4, 22.0, -1, 1.5, 3.0, t + 2);
        }
    }
}

// ESP32-S3-Zero seats with different rib interference (1-4 notches on the edge = variant number)
module press_fit_calibration() {
    cx = esp_pos[0]; cy = esp_pos[1];
    pw = esp_x + clr + 2 * seat_t + 6; ph = esp_y + clr + 2 * seat_t + 6;
    for (i = [0:len(cal_values) - 1]) {
        col = i % 2; row = floor(i / 2);
        translate([-cx + col * (pw + 4), -cy - row * (ph + 4), 0]) difference() {
            seat_esp(interf = cal_values[i], extra = 0) box(cx, cy, 0, pw, ph, face);
            for (k = [0:i]) box(cx - pw / 2 + 3 + k * 2.5, cy + ph / 2, -1, 1.2, 3.0, face + 2);
        }
    }
}

module seat_test_fit() { intersection() { housing(); cyl(r_out + 1, -1, fit_z_cut + 1); } }

module print_plate() {
    housing();
    translate([r_out + ring_r_out + 8.4, 0, 0]) ceiling_base();
    translate([25.0, r_out + 22.0, 0]) chamber_lid();
}

// ---------------------------------------------------------------------------------------------
assert(size == 80 || size == 100, "size must be 80 or 100");
if (part == "housing") housing();
else if (part == "ceiling_base") ceiling_base();
else if (part == "chamber_lid") chamber_lid();
else if (part == "print_plate") print_plate();
else if (part == "seat_test_fit") seat_test_fit();
else if (part == "press_fit_calibration") press_fit_calibration();
else if (part == "radar_window_samples") radar_window_samples();
