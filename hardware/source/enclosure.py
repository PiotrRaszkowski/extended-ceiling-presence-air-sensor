"""
Ceiling-mounted enclosure for an ESP32 presence + air-quality sensor.
Parametric CadQuery model -> STEP + STL.

Parts:
  1. ceiling base    - screwed to the ceiling (60 mm screw spacing = standard Ø60
                       junction box), ring with 3 bayonet grooves
  2. housing         - Ø80 (or Ø100) x 30 mm "can": face towards the room, module seats,
                       closed ENS160+AHT21 air chamber with its own vents, 3 bayonet pins
  3. chamber lid     - press-fit into the ENS160 chamber from above
  4. radar window samples (0.8 / 1.6 / 3.7 mm)
  5. seat test fit   - bottom 9 mm of the housing: quick print to test-fit the modules
  6. press-fit calibration - ESP32 seats with different crush-rib interference

Two sizes share this file: Ø80 (default) and Ø100, with different module layouts.
    python enclosure.py        -> Ø80,  files in out/
    python enclosure.py 100    -> Ø100, files in out/ with a _d100 suffix

Housing coordinates: z = 0 is the face (room side), z = H is the edge at the
ceiling. "Inside view" = looking down from the ceiling onto the face.

History:
  v2  - bayonet groove not through, detent with play, 3.7 mm radar window, PIR cone, face chamfer.
  v3  - real module dimensions (caliper); radar/BH1750 on ledges, sealed ENS160 chamber, pins moved off the chamber.
  v4  - all boards on ledges (room for pin ends underneath); round PIR seat with keys in the board notches.
  v5  - 0.3 mm clearance; radar ledges only where the edge is free; upper chamber vents (outlet under the lid).
  v6  - press-fit: walls/posts with clearance + crush ribs.
  v7  - printable trapezoid ribs (2.4 mm base, 0.8 mm flat top); added press-fit calibration print.
  v8  - RIB_INTERF = 0.1 mm per calibration print (0.2 would not go in).
  v9  - lid without through pry slot; smaller I2C cable pass-through (5 x 2.5 mm), lid notch above it.
  v10 - after full print: ESP ribs 3 mm from rounded corners, taller posts, 3 PIR ribs, lid ribs outside the plug, buck +0.05 mm.
  v11 - Ø80 mm (was Ø100): new interior layout; seats, ribs and interference unchanged.
  v12 - both sizes from one file; ENS160 chamber 10 mm taller (CH_TOP 13 -> 23) for pin headers with push-on jumper wires;
        above the base ring the outer chamber wall steps in (45 deg) to clear the ring.
  v13 - Ø80: BH1750 seat +0.05 mm interference (printed loose; Ø100 fit fine).
  v14 - seat for a Dupont "hub" (perfboard with male headers, one row per net) standing on the
        outside of the chamber inner wall; ENS160 cable pass-through moved to the +y side wall.
  v15 - radar window 0.8 mm (was 3.7 mm): the thick window made the radar see noise on every gate.
        New quick print 13_radar_seat_test to check the radar before printing the whole housing.
  v16 - radar on six posts (like the S09) instead of in a walled pocket, 6.2 mm (half a wavelength)
        above the 0.8 mm window; small tabs under the board only at the long-side posts.
        ENS160 cable pass-through 8 x 4 mm (was 5 x 2.5): four jumper wires did not fit.
        RIB_INTERF 0.13 (was 0.1): the Ø100 print held every board, but a touch loosely.
"""
import math
import os
import sys

import cadquery as cq

OUT_DIR = "out"   # export directory, relative to the current working directory
SIZE = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 80   # housing Ø: 80 or 100
assert SIZE in (80, 100), "size must be 80 or 100"
SUFFIX = "" if SIZE == 80 else "_d100"

# ----------------------------------------------------------------------------
# GENERAL PARAMETERS
# ----------------------------------------------------------------------------
R_OUT = SIZE / 2      # outer radius (40 for Ø80, 50 for Ø100)
WALL = 2.0            # side wall thickness
R_IN = R_OUT - WALL   # 38 / 48
H = 30.0              # housing height (face to ceiling)
FACE = 1.6            # face thickness
EDGE_CHAMFER = 1.5    # chamfer on the face edge
CLR = 0.8             # wall/post clearance (total, 0.4 per side) - only the crush ribs hold the board
RIB_INTERF = 0.13     # how far a crush rib reaches into the board outline (per side); v16: 0.13 (0.1 held, but a little loose)
RIB_W = 2.4           # crush rib base width (must be > 2x nozzle line width)
RIB_TOP = 0.8         # crush rib flat top width
RIB_H = 2.0           # crush rib height above the board underside
T = 1.2               # seat wall and post thickness
POST_H = 2.5          # how far posts/walls rise above the board underside

# Bayonet
BASE_PLATE_T = 2.5
RING_DEPTH = 10.0
RING_T = 3.0
RING_R_OUT = R_IN - 0.4
RING_R_IN = RING_R_OUT - RING_T
PIN_DEPTH = 6.0
PIN_W = 5.0
PIN_HGT = 3.0
PIN_PROTRUDE = 1.8
GROOVE_DEPTH = 1.8
SLOT_CLR_TOP = 0.3
SLOT_CLR_BOT = 0.8
LOCK_ANGLE = 25.0
DETENT_H = 0.6
DETENT_FLANK = 45.0
PIN_ANGLES = (60.0, 180.0, 300.0)   # no pin above the ENS160 chamber (+x axis)

# Base screws
SCREW_SPACING = 60.0
SCREW_D = 4.2
CSK_D = 8.6
CABLE_HOLE_D = 12.0

# ----------------------------------------------------------------------------
# MODULES - caliper-measured; x/y in the inside view, cx/cy = board center
# ----------------------------------------------------------------------------
# HLK-LD2410B: 35.06 x 7.0. The antenna side (towards the face) carries the radar IC,
# LED and pin solder joints, so the board rests on two ledges along its long edges
# over a recess (gap). win_t of plastic stays in front of the antenna (half wave).
# v15: the 3.7 mm window with the board 2 mm above it raised the empty-room move energy to 40-60 on
# every gate (1-9 with the radar out of the housing). The window is now 0.8 mm (thinner than 1/8 of
# a wavelength in PETG, which Hi-Link allows when half a wavelength can't be met), over the board
# footprint plus win_mx / win_my on each side.
# v16: the board is no longer in a pocket. It stands on six posts like the S09 (two on each long
# side, one at each end), with a small tab under the board edge only at the long-side posts, and
# sits gap = 6.2 mm (half a wavelength in air) above the thin window.
RADAR = dict(x=7.0, y=35.06, cx=4.6 if SIZE == 80 else 0.0, cy=-5.0 if SIZE == 80 else 4.0, win_t=0.8, gap=6.2, ledge=0.7,
             win_mx=3.0, win_my=1.5,
             post_t=1.6, post_w=3.0, end_w=2.5,
             post_y=(6.5, 27.5),   # long-side posts, centre in mm from the end without the connector
             # ledge segments [from, to] in mm from the end WITHOUT the connector (-y); components at the edges elsewhere
             ledge_segments=((1.0, 15.0), (25.0, 30.0)))
# HC-SR602: round board Ø15.89, two opposite notches (13.65 across), 3-pin header
# 90 deg from the notch axis; pin ends stick out on the lens side.
# The board rests on a ring around the lens (standoff above the face), the notches sit on
# keys, the header points to hdr_angle over a recess in the ring.
PIR = dict(cx=15.0, cy=24.0, d=15.89, notch_w=13.65, key_w=1.6, standoff=2.2,
           lens_d=10.3, cone=3.2, hdr_angle=180.0, hdr_gap=70.0) if SIZE == 80 else \
      dict(cx=-22.0, cy=18.0, d=15.89, notch_w=13.65, key_w=1.6, standoff=2.2,
           lens_d=10.3, cone=3.2, hdr_angle=270.0, hdr_gap=70.0)   # lens_d = lens Ø + 0.3; header towards -x
# GY-302 (BH1750): 14.05 x 18.53, components towards the face -> ledges along the long
# edges; pins on the -y edge (open side of the seat), mounting holes on +y.
BH = dict(x=14.05, y=18.53, cx=-9.93 if SIZE == 80 else -26.0, cy=22.27 if SIZE == 80 else -8.5, standoff=2.5, ledge=0.8,
          chip_dy=2.5, win_x=4.0, win_y=6.0,          # chip_dy: sensor IC offset from board center towards the holes
          rib_extra=0.05 if SIZE == 80 else 0.0)      # Ø80 print came out loose (Ø100 fine): +0.05 interference
# Waveshare ESP32-S3-Zero: 23.69 x 17.98, pads/pins along the long edges and the left short edge.
# Rails under the middle of the board, clear of the pin rows; rail_h clears the pin ends (<= 2.5 mm).
ESP = dict(x=23.69, y=17.98, cx=-14.75 if SIZE == 80 else -8.0, cy=0.0 if SIZE == 80 else -31.0, rail_h=3.0, rail_y=4.0,
           post_leg=4.4, rib_in=3.0)   # board corners are rounded: ribs 3 mm in from the corners
# S09 buck converter: 18.75 x 13.95, pads in the corners of the short edges.
BUCK = dict(x=18.75, y=13.95, cx=-12.28 if SIZE == 80 else 2.0, cy=-19.98 if SIZE == 80 else 34.0, rail_h=3.0, rail_y=3.5, rail_len=10.0,
            rib_extra=0.05)   # slightly tighter than the rest (0.15 interference)
# ENS160+AHT21: 19.29 (x) x 24.20 (y), COMPONENTS UP, flat underside on rails,
# pin row next to the inner chamber wall (cable pass-through side).
ENS = dict(x=19.29, y=24.20, rail_h=3.0,
           rails=(4.5, 18.0))   # rail positions [mm from the pin edge]; AHT21 cutout spans ~8.5-16.2

# ENS160 chamber (closed box against the side wall, +x axis)
CH_X = 12.0 if SIZE == 80 else 21.0   # inner chamber wall (x)
CH_TOP = 23.0         # top of the chamber walls = underside of the lid (room for headers + jumper plugs)
LID_T = 1.5
WIRE_W, WIRE_D = 8.0, 4.0   # cable pass-through for 4 jumper wires (width x depth from the wall top)
WIRE_SIDE = 1               # pass-through in the +y (1) or -y (-1) chamber side wall, next to the inner wall
WIRE_XC = CH_X + T + 4.5    # its centre along x
PLUG_H = 2.0          # lid plug that goes into the chamber
# The base ring reaches RING_DEPTH into the housing along the outer wall. If the chamber
# is taller than that, its outer wall steps in (45 deg) to R_UP above Z_STEP.
Z_STEP = H - RING_DEPTH - 0.5          # highest point of the chamber next to the housing wall
R_UP = R_IN - 0.4 - RING_T - 0.5       # outer face of the chamber wall above Z_STEP (ring inner radius - 0.5)
TALL = CH_TOP > Z_STEP

# Dupont hub: a piece of 2.54 mm perfboard standing upright against the outside of the
# chamber inner wall, male headers pointing into the housing (-x), jumper plugs horizontal.
# cols x rows = holes of the cut board; the outer column on each side stays empty and is
# what the two side channels grip, so only cols-2 columns carry pins.
HUB = dict(cols=6, rows=5, t=1.6, back_gap=3.5, slack=0.8, plug_len=16.5, z_min=9.2)


# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------
def box(cx, cy, z0, sx, sy, sz):
    return cq.Workplane("XY").box(sx, sy, sz, centered=(True, True, False)).translate((cx, cy, z0))


def cyl(r, z0, h, cx=0.0, cy=0.0):
    return cq.Workplane("XY").circle(r).extrude(h).translate((cx, cy, z0))


def ring(r_in, r_out, z0, h):
    return cq.Workplane("XY").circle(r_out).circle(r_in).extrude(h).translate((0, 0, z0))


def wedge(a0, a1, z0, h, r=80.0, steps=24):
    """Wedge (sector) from angle a0 to a1 [deg], used to cut rings."""
    pts = [(0.0, 0.0)]
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return cq.Workplane("XY").polyline(pts).close().extrude(h).translate((0, 0, z0))


def sector(r_in, r_out, a0, a1, z0, h):
    return ring(r_in, r_out, z0, h).intersect(wedge(a0, a1, z0, h))


def rect_walls(cx, cy, ix, iy, z0, h, t=T):
    return box(cx, cy, z0, ix + 2 * t, iy + 2 * t, h).cut(box(cx, cy, z0 - 1, ix, iy, h + 2))


def open_side(solid, cx, cy, ix, iy, z0, h, side, frac=0.7, t=T):
    """Cut an opening in one seat wall: side = '+x', '-x', '+y', '-y'."""
    sgn = 1 if side[0] == "+" else -1
    if side[1] == "x":
        return solid.cut(box(cx + sgn * (ix / 2 + t / 2), cy, z0 - 1, t + 1, iy * frac, h + 2))
    return solid.cut(box(cx, cy + sgn * (iy / 2 + t / 2), z0 - 1, ix * frac, t + 1, h + 2))


def corner_posts(cx, cy, ix, iy, z0, h, leg=2.2, t=T):
    s = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            b = box(cx + sx * (ix / 2 + t - (leg + t) / 2), cy + sy * (iy / 2 + t - (leg + t) / 2), z0, leg + t, leg + t, h)
            s = b if s is None else s.union(b)
    return s.cut(box(cx, cy, z0 - 1, ix, iy, h + 2))


def side_posts(cx, cy, ix, iy, z0, h, side, offsets, w, t=T):
    s = None
    sgn = 1 if side[0] == "+" else -1
    for o in offsets:
        if side[1] == "y":
            b = box(cx + o, cy + sgn * (iy / 2 + t / 2), z0, w, t, h)
        else:
            b = box(cx + sgn * (ix / 2 + t / 2), cy + o, z0, t, w, h)
        s = b if s is None else s.union(b)
    return s


def rib(px, py, nx, ny, z0, h=RIB_H, p=None, w=RIB_W):
    """Trapezoid crush rib: base on the wall plane at (px, py),
    flat top offset by p in direction (nx, ny) - towards the seat center."""
    p = CLR / 2 + RIB_INTERF if p is None else p
    tx, ty = -ny, nx
    back = 0.3   # overlap into the wall
    tw = RIB_TOP / 2
    pts = [(px + tx * w / 2 - nx * back, py + ty * w / 2 - ny * back),
           (px - tx * w / 2 - nx * back, py - ty * w / 2 - ny * back),
           (px - tx * w / 2, py - ty * w / 2),
           (px - tx * tw + nx * p, py - ty * tw + ny * p),
           (px + tx * tw + nx * p, py + ty * tw + ny * p),
           (px + tx * w / 2, py + ty * w / 2)]
    return cq.Workplane("XY").polyline(pts).close().extrude(h).translate((0, 0, z0))


def ribs_rect(cx, cy, ix, iy, z0, xs=(), ys=(), ends_x=(), ends_y=(), sides="xy", h=RIB_H, p=None):
    """Crush ribs on the walls of a rectangular ix x iy seat.
    xs: rib positions (dx) on the +-y walls; ys: positions (dy) on the +-x walls.
    ends_x / ends_y: limit to selected walls, e.g. ends_y=(1,) = +y wall only."""
    s = None
    for sy in (ends_y or (-1, 1)):
        for dx in xs:
            r = rib(cx + dx, cy + sy * iy / 2, 0, -sy, z0, h, p)
            s = r if s is None else s.union(r)
    for sx in (ends_x or (-1, 1)):
        for dy in ys:
            r = rib(cx + sx * ix / 2, cy + dy, -sx, 0, z0, h, p)
            s = r if s is None else s.union(r)
    return s


def radial_slots(angles, z0, h, width=2.0, r=R_OUT - WALL / 2):
    s = None
    for a in angles:
        b = box(r, 0, z0, WALL + 2, width, h).rotate((0, 0, 0), (0, 0, 1), a)
        s = b if s is None else s.union(b)
    return s


# ----------------------------------------------------------------------------
# MODULE SEATS
# ----------------------------------------------------------------------------
RADAR_SEAT_Z = RADAR["win_t"] + RADAR["gap"]        # height at which the radar board rests
BH_SEAT_Z = FACE + BH["standoff"]
ENS_X0 = CH_X + T + CLR / 2                              # ENS160 board edge on the pass-through side
ENS_SEAT_Z = FACE + ENS["rail_h"]


def seat_radar(c):
    m = RADAR
    ix, iy = m["x"] + CLR, m["y"] + CLR
    pt, z0 = m["post_t"], m["win_t"] - 0.01
    if m["win_t"] < FACE:   # thin window: thin the face under the seat and a margin around it
        c = c.cut(box(m["cx"], m["cy"], m["win_t"], ix + 2 * pt + 2 * m["win_mx"], iy + 2 * pt + 2 * m["win_my"],
                      FACE - m["win_t"] + 0.01))
    h_post = RADAR_SEAT_Z + POST_H - m["win_t"] + 0.01
    y_end = m["cy"] - m["y"] / 2                     # end without the connector
    lw = ix / 2 - (m["x"] / 2 - m["ledge"])          # tab from (board edge - ledge) to the post face
    # long sides: posts with a small tab under the board edge (no other support under the board)
    for d in m["post_y"]:
        yy = y_end + d
        for sx in (-1, 1):
            c = c.union(box(m["cx"] + sx * (ix / 2 + pt / 2), yy, z0, pt, m["post_w"], h_post))
            c = c.union(box(m["cx"] + sx * (ix / 2 - lw / 2), yy, z0, lw + 0.01, m["post_w"], RADAR_SEAT_Z - m["win_t"] + 0.01))
            c = c.union(rib(m["cx"] + sx * ix / 2, yy, -sx, 0, RADAR_SEAT_Z))
    # ends: one post each, no tab (the connector end has its wires right at the edge)
    for sy in (-1, 1):
        c = c.union(box(m["cx"], m["cy"] + sy * (iy / 2 + pt / 2), z0, m["end_w"], pt, h_post))
        c = c.union(rib(m["cx"], m["cy"] + sy * iy / 2, 0, -sy, RADAR_SEAT_Z, w=m["end_w"]))
    return c


def _ring_sector(cx, cy, r_in, r_out, a0, a1, z0, h):
    return ring(r_in, r_out, z0, h).intersect(wedge(a0, a1, z0, h)).translate((cx, cy, 0))


def seat_pir(c):
    m = PIR
    r_b = m["d"] / 2 + 0.15                     # seat radius (PIR is located by the keys)
    z_seat = FACE + m["standoff"]
    h_top = m["standoff"] + 1.2 + 1.5           # wall height above the face
    # support ring around the lens, with a recess for the header pin ends
    boss = _ring_sector(m["cx"], m["cy"], m["lens_d"] / 2 + 0.2, 6.3, m["hdr_angle"] + m["hdr_gap"] / 2,
                        m["hdr_angle"] - m["hdr_gap"] / 2 + 360, FACE - 0.01, m["standoff"] + 0.01)
    c = c.union(boss)
    # keys that engage the board notches
    ro = m["hdr_angle"] - 270.0                 # rotation of the whole seat vs. the base layout (header at 270 deg)
    r_key = m["notch_w"] / 2 + 0.1
    for a in (0.0 + ro, 180.0 + ro):
        key = box((r_key + r_b + T) / 2, 0, FACE - 0.01, r_b + T - r_key, m["key_w"], h_top + 0.01)
        c = c.union(key.rotate((0, 0, 0), (0, 0, 1), a).translate((m["cx"], m["cy"], 0)))
    # retaining arcs: opposite the header and on both sides of it
    for a0, a1 in ((65.0 + ro, 115.0 + ro), (210.0 + ro, 232.0 + ro), (308.0 + ro, 330.0 + ro)):
        c = c.union(_ring_sector(m["cx"], m["cy"], r_b, r_b + T, a0, a1, FACE - 0.01, h_top + 0.01))
        a = math.radians((a0 + a1) / 2)   # crush rib in the middle of the arc
        c = c.union(rib(m["cx"] + r_b * math.cos(a), m["cy"] + r_b * math.sin(a), -math.cos(a), -math.sin(a),
                        z_seat, p=(r_b - m["d"] / 2) + RIB_INTERF, w=2.0))
    # lens hole + 45 deg outward cone
    c = c.cut(cyl(m["lens_d"] / 2, -1, FACE + 2, m["cx"], m["cy"]))
    r_cone = m["lens_d"] / 2 + m["cone"] / 2
    c = c.cut(cq.Workplane("XY").add(cq.Solid.makeCone(
        r_cone + 0.5, m["lens_d"] / 2, (r_cone + 0.5) - m["lens_d"] / 2,
        pnt=cq.Vector(m["cx"], m["cy"], -0.5), dir=cq.Vector(0, 0, 1))))
    return c


def seat_bh(c):
    m = BH
    ix, iy = m["x"] + CLR, m["y"] + CLR
    for sx in (-1, 1):   # ledges under the long edges
        lw = ix / 2 - (m["x"] / 2 - m["ledge"])
        c = c.union(box(m["cx"] + sx * (ix / 2 - lw / 2), m["cy"], FACE - 0.01, lw, iy, m["standoff"] + 0.01))
    walls = rect_walls(m["cx"], m["cy"], ix, iy, FACE - 0.01, m["standoff"] + POST_H + 0.01)
    walls = open_side(walls, m["cx"], m["cy"], ix, iy, FACE, m["standoff"] + POST_H, "-y")   # pins
    c = c.union(walls)
    c = c.union(ribs_rect(m["cx"], m["cy"], ix, iy, BH_SEAT_Z, xs=(0.0,), ys=(-5.0, 5.0), ends_y=(1,),
                          p=CLR / 2 + RIB_INTERF + m["rib_extra"]))
    c = c.cut(box(m["cx"], m["cy"] + m["chip_dy"], -1, m["win_x"], m["win_y"], FACE + 2))
    return c


ESP_SEAT_Z = FACE + ESP["rail_h"]
BUCK_SEAT_Z = FACE + BUCK["rail_h"]


def seat_esp(c):
    m = ESP
    ix, iy = m["x"] + CLR, m["y"] + CLR
    # rails along the board, under the middle (pin rows along the long edges stay clear);
    # 3 mm clear from the left short edge (pads)
    x0, x1 = m["cx"] - m["x"] / 2 + 3.0, m["cx"] + m["x"] / 2 - 1.0
    for sy in (-1, 1):
        c = c.union(box((x0 + x1) / 2, m["cy"] + sy * m["rail_y"], FACE - 0.01, x1 - x0, 1.5, m["rail_h"] + 0.01))
    c = c.union(corner_posts(m["cx"], m["cy"], ix, iy, FACE - 0.01, m["rail_h"] + POST_H + 0.01, leg=m["post_leg"]))
    c = c.union(ribs_rect(m["cx"], m["cy"], ix, iy, ESP_SEAT_Z,
                          xs=(-(ix / 2 - m["rib_in"]), ix / 2 - m["rib_in"]), ys=(-(iy / 2 - m["rib_in"]), iy / 2 - m["rib_in"])))
    return c


def seat_buck(c):
    m = BUCK
    ix, iy = m["x"] + CLR, m["y"] + CLR
    # rails in the middle section (pads/pins are in the corners)
    for sy in (-1, 1):
        c = c.union(box(m["cx"], m["cy"] + sy * m["rail_y"], FACE - 0.01, m["rail_len"], 1.5, m["rail_h"] + 0.01))
    h = m["rail_h"] + POST_H + 0.01
    for side in ("+y", "-y"):
        c = c.union(side_posts(m["cx"], m["cy"], ix, iy, FACE - 0.01, h, side, (-4.0, 4.0), 3.0))
    for side in ("+x", "-x"):   # middle of the short edges, pin corners stay clear
        c = c.union(side_posts(m["cx"], m["cy"], ix, iy, FACE - 0.01, h, side, (0.0,), 2.5))
    c = c.union(ribs_rect(m["cx"], m["cy"], ix, iy, BUCK_SEAT_Z, xs=(-4.0, 4.0), ys=(0.0,),
                          p=CLR / 2 + RIB_INTERF + m["rib_extra"]))
    return c


def chamber_body(c):
    """Closed ENS160 chamber: inner wall + two side walls + the housing wall."""
    hy = (ENS["y"] + CLR) / 2 + 0.05          # half of the interior along y
    clip = cyl(R_IN + 0.5, 0, H)
    if TALL:   # above Z_STEP the chamber must stay inside the base ring
        clip = cyl(R_IN + 0.5, 0, Z_STEP).union(cyl(R_UP, Z_STEP - 0.01, H - Z_STEP + 0.01))
    walls = box(CH_X + T / 2, 0, FACE - 0.01, T, 2 * (hy + T), CH_TOP - FACE + 0.01)
    for sy in (-1, 1):
        walls = walls.union(box((CH_X + R_IN + 1) / 2, sy * (hy + T / 2), FACE - 0.01, R_IN + 1 - CH_X, T, CH_TOP - FACE + 0.01))
    if TALL:
        foot = box((CH_X + R_IN + 1) / 2, 0, 0, R_IN + 1 - CH_X, 2 * (hy + T), H)   # chamber footprint
        # 45 deg step from the housing wall in to the upper wall (prints without support)
        dz = R_IN + 0.2 - (R_UP - T)
        step = cq.Workplane("XY").add(cq.Solid.makeCone(R_IN + 0.2, R_UP - T, dz, pnt=cq.Vector(0, 0, Z_STEP - dz)))
        step = cyl(R_IN + 0.5, Z_STEP - dz, dz).cut(step)
        upper = ring(R_UP - T, R_UP, Z_STEP - 0.01, CH_TOP - Z_STEP + 0.01)
        walls = walls.union(step.union(upper).intersect(foot))
    c = c.union(walls.intersect(clip))
    # cable pass-through (side wall next to the inner wall, from the top): four jumper wires.
    # Not in the inner wall: the Dupont hub stands in front of it.
    c = c.cut(box(WIRE_XC, WIRE_SIDE * (hy + T / 2), CH_TOP - WIRE_D, WIRE_W, T + 2, WIRE_D + 0.5))
    # rails under the flat board underside (clear of the pin row and the edges)
    for dx in ENS["rails"]:
        c = c.union(box(ENS_X0 + dx, 0, FACE - 0.01, 1.5, 2 * hy - 1.0, ENS["rail_h"] + 0.01))
    # end stops on the housing-wall side
    for sy in (-1, 1):
        c = c.union(box(ENS_X0 + ENS["x"] + CLR / 2 + 0.6, sy * 8.0, FACE - 0.01, 1.2, 3.0, ENS["rail_h"] + 1.6 + 1.5))
    # vent slots in the face between the rails and in the housing wall
    for dx in (7.2, 10.0, 12.8, 15.6):
        c = c.cut(box(ENS_X0 + dx, 0, -1, 1.6, 2 * hy - 5.0, FACE + 1.01))
    c = c.cut(box(ENS_X0 + ENS["x"] + 2.6, 0, -1, 1.6, 2 * hy - 9.0, FACE + 1.01))   # behind the board
    c = c.cut(radial_slots((-10.0, -3.4, 3.4, 10.0), 3.5, 4.5))       # lower band
    c = c.cut(radial_slots((-10.0, -3.4, 3.4, 10.0), 9.0, 3.0))       # upper band under the lid (outlet)
    # crush ribs: chamber side walls (+-y), inner wall and end stops (x)
    ix_face_in = CH_X + T                                 # inner wall plane
    x_stop = ENS_X0 + ENS["x"] + CLR / 2                  # end stop plane
    p_y = hy - ENS["y"] / 2 + RIB_INTERF
    for sy in (-1, 1):
        for xx in (ENS_X0 + 5.0, ENS_X0 + 14.5):
            c = c.union(rib(xx, sy * hy, 0, -sy, ENS_SEAT_Z, p=p_y))
        c = c.union(rib(ix_face_in, sy * 6.5, 1, 0, ENS_SEAT_Z, p=ENS_X0 - ix_face_in + RIB_INTERF))
        c = c.union(rib(x_stop, sy * 8.0, -1, 0, ENS_SEAT_Z, p=CLR / 2 + RIB_INTERF))
    return c, hy


def hub_geometry():
    """Positions of the Dupont hub (board planes, heights) shared by the seat and the dummies."""
    m = HUB
    w, h = m["cols"] * 2.54, m["rows"] * 2.54          # board size (cut through hole centres)
    y_pins = (m["cols"] - 2) * 2.54 / 2                # header plastic / plugs reach +-y_pins
    xb = CH_X - m["back_gap"]                          # board back face (solder side)
    xf = xb - m["t"]                                   # board front face (header side)
    # anything lower in the way of the channels or the plugs: the radar seat
    rx_hi = RADAR["cx"] + (RADAR["x"] + CLR) / 2 + RADAR["post_t"]
    ry_lo = RADAR["cy"] - (RADAR["y"] + CLR) / 2 - RADAR["post_t"]
    ry_hi = RADAR["cy"] + (RADAR["y"] + CLR) / 2 + RADAR["post_t"]
    r_top = RADAR_SEAT_Z + POST_H
    y_out = w / 2 + m["slack"] + T
    x_lo = xf - 0.3 - 1.2
    wedge = rx_hi > x_lo and ry_hi > -y_out and ry_lo < y_out
    z0 = m["z_min"]
    if wedge:   # the channel floor above the radar seat is a 45 deg overhang; the slot must sit above it
        z0 = max(z0, r_top + 0.4 + (rx_hi + 0.3 - (xf - 0.3)) + 0.6)
    assert z0 + h <= H - BASE_PLATE_T - 0.5, "hub too tall for the housing"
    return dict(w=w, h=h, y_pins=y_pins, xb=xb, xf=xf, z0=z0, x_lo=x_lo, y_out=y_out,
                wedge=wedge, rx_hi=rx_hi, r_top=r_top)


def seat_hub(c):
    """Two vertical channels on the outside of the chamber inner wall that hold the hub
    board by its empty outer columns; the board stands on the channel floors."""
    m, g = HUB, hub_geometry()
    w, h, xb, xf, z0 = g["w"], g["h"], g["xb"], g["xf"], g["z0"]
    y_in = g["y_pins"] + 0.25                          # channels start just outside the header plastic
    for sy in (-1, 1):
        y0, y1 = sorted((sy * y_in, sy * g["y_out"]))
        ch = box((g["x_lo"] + CH_X - 0.3) / 2, (y0 + y1) / 2, FACE - 0.01, CH_X - 0.3 - g["x_lo"], y1 - y0, z0 + h - FACE + 0.01)
        ch = ch.union(box(CH_X - 0.15, (y0 + y1) / 2, FACE - 0.01, 0.32, y1 - y0, CH_TOP - FACE))   # tie to the wall
        if g["wedge"]:   # clear the radar seat with a printable 45 deg overhang
            xr = g["rx_hi"] + 0.3
            zr = g["r_top"] + 0.4
            x_far = g["x_lo"] - 1.0
            pts = [(x_far, -1.0), (xr, -1.0), (xr, zr), (x_far, zr + (xr - x_far))]
            wedge = cq.Workplane("XZ", origin=(0, y1 + 1.0, 0)).polyline(pts).close().extrude(y1 - y0 + 2.0)
            ch = ch.cut(wedge)
        ys0, ys1 = sorted((sy * (y_in - 1.0), sy * (w / 2 + m["slack"])))
        ch = ch.cut(box((xf - 0.3 + xb + 0.3) / 2, (ys0 + ys1) / 2, z0, xb - xf + 0.6, ys1 - ys0, h + 1.0))   # slot
        # crush rib on the front face of the slot, pressing the board against the back face
        ch = ch.union(rib(xf - 0.3, sy * (y_in + (w / 2 - y_in) / 2), 1, 0, z0 + 2.0, h=h - 4.0, p=0.3 + RIB_INTERF, w=1.4))
        c = c.union(ch)
    return c


# ----------------------------------------------------------------------------
# 2. HOUSING
# ----------------------------------------------------------------------------
def make_housing():
    c = cq.Workplane("XY").circle(R_OUT).extrude(H)
    c = c.faces("<Z").edges().chamfer(EDGE_CHAMFER)
    c = c.cut(cyl(R_IN, FACE, H))

    c = seat_radar(c)
    c = seat_bh(c)
    c = seat_esp(c)
    c = seat_buck(c)
    c, _ = chamber_body(c)
    c = seat_hub(c)
    c = seat_pir(c)          # last: cuts the hole through the face

    # electronics ventilation: side wall opposite the chamber
    c = c.cut(radial_slots(range(148, 213, 8), 3.5, 5.0))    # inlet (low)
    c = c.cut(radial_slots(range(148, 213, 8), 12.5, 5.5))   # outlet (high)

    # bayonet pins + alignment marks on the rim
    z_pin = H - PIN_DEPTH - PIN_HGT / 2
    for a in PIN_ANGLES:
        pin = box(R_IN - PIN_PROTRUDE / 2 + 0.25, 0, z_pin, PIN_PROTRUDE + 0.5, PIN_W, PIN_HGT)
        c = c.union(pin.rotate((0, 0, 0), (0, 0, 1), a))
        mark = box(R_OUT, 0, H - 3.0, 1.6, 1.4, 4.0)
        c = c.cut(mark.rotate((0, 0, 0), (0, 0, 1), a))
    return c


# ----------------------------------------------------------------------------
# 3. CHAMBER LID (print orientation: plate on the bed, plug up;
#    flipped plug-down when installed in the housing)
# ----------------------------------------------------------------------------
def make_lid():
    hy = (ENS["y"] + CLR) / 2 + 0.05
    r_plate, r_plug = (R_UP, R_UP - T - 0.25) if TALL else (R_IN - 0.4, R_IN - 0.45)
    plate = box((CH_X + 49) / 2, 0, 0, 49 - CH_X, 2 * (hy + T), LID_T).intersect(cyl(r_plate, -1, 10))
    plug = box((CH_X + T + 0.25 + 49) / 2, 0, LID_T - 0.01, 49 - (CH_X + T + 0.25), 2 * (hy - 0.25), PLUG_H + 0.01)
    plug = plug.intersect(cyl(r_plug, -1, 10))
    plug = plug.cut(box((CH_X + T + 0.25 + 49) / 2, 0, LID_T - 1, 49, 2 * (hy - 0.25 - 1.2), PLUG_H + 3))  # hollow plug
    # notch above the pass-through (the lid is flipped about x when installed, so y changes sign)
    plug = plug.cut(box(WIRE_XC, -WIRE_SIDE * (hy - 0.25 - 0.6), LID_T - 1, WIRE_W + 0.5, 3.0, PLUG_H + 3))
    lid = plate.union(plug)
    # crush ribs on the outside of the plug (press against the chamber side walls)
    for sy in (-1, 1):
        for xx in ((CH_X + 9.0, CH_X + 17.0) if TALL else (CH_X + 8.0, CH_X + 20.0)):
            lid = lid.union(rib(xx, sy * (hy - 0.25), 0, sy, LID_T - 0.01, h=PLUG_H, p=0.25 + RIB_INTERF))
    return lid


def lid_in_housing(lid):
    """Lid in its installed position (for collision checks / rendering)."""
    return lid.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, CH_TOP + LID_T))


# ----------------------------------------------------------------------------
# 1. CEILING BASE  (z = 0 is the ceiling side; print ceiling side down)
# ----------------------------------------------------------------------------
RING_R_GROOVE = RING_R_OUT - GROOVE_DEPTH     # bayonet groove bottom
Z_LO = PIN_DEPTH - PIN_HGT / 2 - SLOT_CLR_TOP  # channel edge on the ceiling side
Z_HI = PIN_DEPTH + PIN_HGT / 2 + SLOT_CLR_BOT  # load-bearing edge (room side)


def detent(angle, r_mid):
    hb = DETENT_H / math.tan(math.radians(DETENT_FLANK))
    prof = [(-hb, Z_HI + 0.3), (hb, Z_HI + 0.3), (hb, Z_HI), (0.0, Z_HI - DETENT_H), (-hb, Z_HI)]
    t = cq.Workplane("YZ").polyline(prof).close().extrude(RING_R_OUT - RING_R_GROOVE + 0.2)
    return t.translate((RING_R_GROOVE - 0.2, 0, 0)).rotate((0, 0, 0), (0, 0, 1), angle), hb


def make_base():
    b = cyl(RING_R_OUT, 0, BASE_PLATE_T)
    b = b.union(ring(RING_R_IN, RING_R_OUT, 0, RING_DEPTH))

    r_g = (RING_R_GROOVE + RING_R_OUT) / 2
    half_w = math.degrees(((PIN_W + 0.6) / 2) / r_g)
    pin_half = math.degrees((PIN_W / 2) / r_g)
    for a in PIN_ANGLES:
        # groove NOT through, cut from outside: vertical entry + horizontal channel
        b = b.cut(sector(RING_R_GROOVE, RING_R_OUT + 1, a - half_w, a + half_w, Z_LO, RING_DEPTH + 1 - Z_LO))
        b = b.cut(sector(RING_R_GROOVE, RING_R_OUT + 1, a - half_w, a + LOCK_ANGLE + half_w, Z_LO, Z_HI - Z_LO))
        # triangular detent on the load-bearing edge
        hb = DETENT_H / math.tan(math.radians(DETENT_FLANK))
        d_center = a + LOCK_ANGLE - pin_half - math.degrees((hb + 0.4) / r_g)
        t, _ = detent(d_center, r_g)
        b = b.union(t)

    # 12 V cable hole
    b = b.cut(cyl(CABLE_HOLE_D / 2, -1, BASE_PLATE_T + 2))
    # screw holes, countersink on the room side (z = BASE_PLATE_T)
    csk_h = (CSK_D - SCREW_D) / 2
    for (sx, sy) in ((SCREW_SPACING / 2, 0), (-SCREW_SPACING / 2, 0),
                     (0, SCREW_SPACING / 2), (0, -SCREW_SPACING / 2)):
        b = b.cut(cyl(SCREW_D / 2, -1, BASE_PLATE_T + 2, sx, sy))
        cone = cq.Workplane("XY").add(cq.Solid.makeCone(
            SCREW_D / 2, CSK_D / 2, csk_h,
            pnt=cq.Vector(sx, sy, BASE_PLATE_T - csk_h), dir=cq.Vector(0, 0, 1)))
        b = b.cut(cone).cut(cyl(CSK_D / 2, BASE_PLATE_T, 2, sx, sy))
    return b


# ----------------------------------------------------------------------------
# 4. RADAR WINDOW SAMPLES: three tiles 0.8 / 1.6 / 3.7 mm (1, 2, 3 notches)
# ----------------------------------------------------------------------------
def make_radar_test():
    out = None
    for i, t in enumerate((0.8, 1.6, 3.7)):
        tile = box(i * 20.0, 0, 0, 16.0, 44.0, t)
        for k in range(i + 1):
            tile = tile.cut(box(i * 20.0 - 4 + k * 4, 22.0, -1, 1.5, 3.0, t + 2))
        out = tile if out is None else out.union(tile)
    return out


def make_radar_seat_test(housing=None):
    """The radar seat cut out of the housing with the face around it: a 15-minute print that holds
    the radar exactly as the housing does, to compare empty-room gate energies before a full print."""
    housing = housing if housing is not None else make_housing()
    m = RADAR
    sx = m["x"] + CLR + 2 * m["post_t"] + 2 * m["win_mx"] + 8.0
    sy = m["y"] + CLR + 2 * m["post_t"] + 2 * m["win_my"] + 2.0
    return housing.intersect(box(m["cx"], m["cy"], -1, sx, sy, RADAR_SEAT_Z + POST_H + 2.0))


# ----------------------------------------------------------------------------
# 6. PRESS-FIT CALIBRATION: 4 ESP32-S3-Zero seats with RIB_INTERF 0.1 / 0.2 / 0.3 / 0.4
#    (1-4 notches on the edge). Pick the one where the board is tight but can still be pressed in.
# ----------------------------------------------------------------------------
CAL_VALUES = (0.1, 0.2, 0.3, 0.4)


def make_rib_test():
    global RIB_INTERF
    keep = RIB_INTERF
    out = None
    m = ESP
    pw, ph = m["x"] + CLR + 2 * T + 6, m["y"] + CLR + 2 * T + 6
    try:
        for i, v in enumerate(CAL_VALUES):
            RIB_INTERF = v
            plate = box(m["cx"], m["cy"], 0, pw, ph, FACE)
            t = seat_esp(plate)
            for k in range(i + 1):   # notches = variant number
                t = t.cut(box(m["cx"] - pw / 2 + 3 + k * 2.5, m["cy"] + ph / 2, -1, 1.2, 3.0, FACE + 2))
            col, row = i % 2, i // 2
            t = t.translate((-m["cx"] + col * (pw + 4), -m["cy"] - row * (ph + 4), 0))
            out = t if out is None else out.union(t)
    finally:
        RIB_INTERF = keep
    return out


# ----------------------------------------------------------------------------
# 5. SEAT TEST FIT: bottom 9 mm of the housing (quick print to test-fit the modules)
# ----------------------------------------------------------------------------
def make_fit_test(housing=None, z_cut=9.0):
    housing = housing if housing is not None else make_housing()
    return housing.intersect(cyl(R_OUT + 1, -1, z_cut + 1))


# ----------------------------------------------------------------------------
# 0. PRINT PLATE: housing + ceiling base + chamber lid laid out side by side
# ----------------------------------------------------------------------------
def make_print_plate(housing, base, lid):
    return housing.union(base.translate((R_OUT + RING_R_OUT + 8.4, 0, 0))).union(lid.translate((25.0, R_OUT + 22.0, 0)))


def section(shape):
    """Quarter section (keeps x >= 0, y <= 0) for previewing the chamber."""
    return shape.intersect(box(50.0, -50.0, -10.0, 100.0, 100.0, 60.0))


# ----------------------------------------------------------------------------
# Module dummies (preview + collision checks; "_parts" = component zone under the board)
# ----------------------------------------------------------------------------
def dummies():
    """Boards + zones under them ("_parts": components / pin ends), for collision checks."""
    d = {}
    r = RADAR
    d["radar"] = box(r["cx"], r["cy"], RADAR_SEAT_Z, r["x"], r["y"], 1.0)
    y_end = r["cy"] - r["y"] / 2
    zone = box(r["cx"], r["cy"], RADAR_SEAT_Z - 1.8, r["x"] - 2 * r["ledge"] - 0.4, r["y"] - 0.6, 1.8)
    for (l0, l1) in ((15.5, 24.5), (30.5, 35.0)):     # components right at the edges
        zone = zone.union(box(r["cx"], y_end + (l0 + l1) / 2, RADAR_SEAT_Z - 1.2, r["x"], l1 - l0, 1.2))
    d["radar_parts"] = zone
    # components on the back of the radar (IC, crystal: up to ~1.2 mm) and the wires leaving the
    # connector end upwards
    d["radar_back"] = box(r["cx"], r["cy"], RADAR_SEAT_Z + 1.0, r["x"], r["y"], 1.2).union(
        box(r["cx"], r["cy"] + r["y"] / 2 - 2.0, RADAR_SEAT_Z + 1.0, r["x"], 4.0, 4.0))
    p = PIR
    zp = FACE + p["standoff"]
    disk = cyl(p["d"] / 2, zp, 1.2, p["cx"], p["cy"])
    ka = math.radians(p["hdr_angle"] + 90.0)     # notch axis (90 deg from the header)
    for sx in (-1, 1):   # board notches
        cut = box(p["notch_w"] / 2 + 2, 0, zp - 1, 4.0, 2.4, 3).rotate((0, 0, 0), (0, 0, 1), math.degrees(ka) + (0 if sx > 0 else 180))
        disk = disk.cut(cut.translate((p["cx"], p["cy"], 0)))
    d["pir"] = disk.union(cyl(p["lens_d"] / 2 - 0.15, FACE - 4.0, p["standoff"] + 4.0, p["cx"], p["cy"]))
    d["pir_parts"] = box(6.6, 0, zp - 1.8, 2.0, 7.6, 1.8).rotate((0, 0, 0), (0, 0, 1), p["hdr_angle"]).translate((p["cx"], p["cy"], 0))   # header pin ends
    b = BH
    d["bh1750"] = box(b["cx"], b["cy"], BH_SEAT_Z, b["x"], b["y"], 1.6)
    d["bh1750_parts"] = box(b["cx"], b["cy"], BH_SEAT_Z - 2.2, b["x"] - 2 * b["ledge"] - 0.4, b["y"] - 0.6, 2.2)
    e = ESP
    d["esp"] = box(e["cx"], e["cy"], ESP_SEAT_Z, e["x"], e["y"], 1.0).union(
        box(e["cx"], e["cy"], ESP_SEAT_Z + 1.0, e["x"] - 4, e["y"] - 3, 3.2))
    pins = None
    for sy in (-1, 1):   # pin rows along the long edges
        rp = box(e["cx"], e["cy"] + sy * (e["y"] / 2 - 1.3), ESP_SEAT_Z - 2.5, e["x"] - 1, 1.8, 2.5)
        pins = rp if pins is None else pins.union(rp)
    d["esp_parts"] = pins.union(box(e["cx"] - e["x"] / 2 + 1.3, e["cy"], ESP_SEAT_Z - 2.5, 1.8, e["y"] - 4, 2.5))
    u = BUCK
    d["buck"] = box(u["cx"], u["cy"], BUCK_SEAT_Z, u["x"], u["y"], 1.0).union(
        box(u["cx"], u["cy"], BUCK_SEAT_Z + 1.0, u["x"] - 4, u["y"] - 2, 4.0))
    pins = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            pp = box(u["cx"] + sx * (u["x"] / 2 - 1.5), u["cy"] + sy * (u["y"] / 2 - 2.0), BUCK_SEAT_Z - 2.5, 2.4, 3.5, 2.5)
            pins = pp if pins is None else pins.union(pp)
    d["buck_parts"] = pins
    d["ens160"] = box(ENS_X0 + ENS["x"] / 2, 0, ENS_SEAT_Z, ENS["x"], ENS["y"], 1.6).union(
        box(ENS_X0 + ENS["x"] / 2, 0, ENS_SEAT_Z + 1.6, ENS["x"] - 2, ENS["y"] - 2, 1.5))
    d["ens160_parts"] = box(ENS_X0 + 1.3, 0, ENS_SEAT_Z - 2.5, 1.8, ENS["y"] - 2, 2.5)
    # Dupont hub: board, header plastic + horizontal plugs (front), pin stubs + solder (back)
    g = hub_geometry()
    d["hub"] = box((g["xf"] + g["xb"]) / 2, 0, g["z0"], HUB["t"], g["w"], g["h"])
    d["hub_parts"] = box(g["xf"] - HUB["plug_len"] / 2, 0, g["z0"], HUB["plug_len"], 2 * g["y_pins"], g["h"]).union(
        box(g["xb"] + 1.5, 0, g["z0"] + 0.5, 3.0, 2 * (g["y_pins"] - 0.8), g["h"] - 1.0))
    # Dupont plugs standing on the ESP headers (both long edges), for clearance checks
    pr = None
    for sy in (-1, 1):
        b2 = box(e["cx"], e["cy"] + sy * (e["y"] / 2 - 1.27), ESP_SEAT_Z + 1.0, e["x"] - 1, 2.54, 2.5 + 14.0)
        pr = b2 if pr is None else pr.union(b2)
    d["esp_plugs"] = pr
    # tongue around the AHT21 (8.5-16.2 mm from the pins): nothing may support it
    d["ens160_tongue"] = box(ENS_X0 + 12.35, 0, ENS_SEAT_Z - 2.9, 7.7, ENS["y"] - 2, 2.9)
    return d


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    housing = make_housing()
    base = make_base()
    lid = make_lid()
    parts = {"00_print_plate_all_parts": make_print_plate(housing, base, lid),
             "01_housing": housing, "02_ceiling_base": base, "03_chamber_lid": lid,
             "10_press_fit_calibration": make_rib_test(), "11_seat_test_fit": make_fit_test(housing),
             "12_radar_window_samples": make_radar_test(), "13_radar_seat_test": make_radar_seat_test(housing)}
    for name, p in parts.items():
        cq.exporters.export(p, os.path.join(OUT_DIR, f"{name}{SUFFIX}.stl"), tolerance=0.02, angularTolerance=0.15)
        cq.exporters.export(p, os.path.join(OUT_DIR, f"{name}{SUFFIX}.step"))
        bb = p.val().BoundingBox()
        print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, vol {p.val().Volume()/1000:.1f} cm3, valid={p.val().isValid()}")
    dm = dummies()
    for name, p in dm.items():
        cq.exporters.export(p, os.path.join(OUT_DIR, f"_dummy_{name}{SUFFIX}.stl"))
    # quarter sections of the chamber area (preview only)
    sections = {"housing": section(housing), "lid": section(lid_in_housing(lid)), "ens160": section(dm["ens160"])}
    for name, p in sections.items():
        cq.exporters.export(p, os.path.join(OUT_DIR, f"_section_{name}{SUFFIX}.stl"))
