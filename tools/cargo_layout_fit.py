#!/usr/bin/env python3
"""cargo_layout_fit.py -- measure a proposed cargo-section equipment layout
against the PUBLISHED cargo shell and against itself.

Why this tool exists
--------------------
Rev T5 (2026-09-15) puts real equipment inside the cargo section for the
first time -- the nacelle-tilt actuator brackets, the flight battery cradle,
the Inara avionics tray, the winch reservation and the foam void formers --
and every one of them competes for the same roof band above the mission
payload envelope.  `airframe/AGENTS.md` ("Geometry Integrity") is explicit
that bounding-box reasoning is inadequate for Serenity's compound-curved hull,
so each envelope is checked by BOOLEAN against the published shell mesh, not
by eye.  Two numbers are reported per envelope:

  * hit  -- intersection volume with the shell at zero offset (must be 0);
  * near -- intersection volume after dilating the envelope by GAP_MM
            (the repo's 3.0 mm clearance budget); non-zero means the envelope
            is closer than the budget somewhere, and the report says where.

Pairwise equipment interference is reported the same way (raw overlap), so a
layout that "fits the hull" but stacks the battery on the actuator is caught.

The layout itself is a plain dict at the bottom of this file (LAYOUT_T5) so
that `merge_cargo_interior.py`, the bracket / cradle SCAD files and the void
formers can all import the SAME numbers (single-sourcing, per the repo
convention used by cargo_bay_envelope.py).

Run:
    /usr/bin/python3 tools/cargo_layout_fit.py            # report
    /usr/bin/python3 tools/cargo_layout_fit.py --plot     # + section PNGs

Use `/usr/bin/python3`: the repository `.venv` hides the system `trimesh`
and `manifold3d`, and `pip` is not permitted in this environment.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the
author's direction, 2026-09-15, per `AGENTS.md` §3 AI attribution.
License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
"""

import argparse
import os
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
SHELL = os.path.join(
    REPO,
    "airframe",
    "stls",
    "fuselage",
    "cargo",
    "cargo_sect_shell24_2mm_repaired.stl",
)
GAP_MM = 3.0  # repo clearance budget to a moving / adjacent part
X_CL = -169.85  # hull centreline (merge_cargo_interior.py X_CL)


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------
def to_man(tm):
    return Manifold(
        Mesh(vert_properties=tm.vertices.astype(np.float32), tri_verts=tm.faces.astype(np.uint32))
    )


def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return b


def cyl(axis, c1, c2, t0, t1, r, sections=48):
    """Cylinder along hull axis 'x'|'y'|'z'; (c1, c2) are the other two
    coordinates in hull order (yz / xz / xy)."""
    c = trimesh.creation.cylinder(radius=r, height=t1 - t0, sections=sections)
    if axis == "x":
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
        c.apply_translation([(t0 + t1) / 2, c1, c2])
    elif axis == "y":
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
        c.apply_translation([c1, (t0 + t1) / 2, c2])
    else:
        c.apply_translation([c1, c2, (t0 + t1) / 2])
    return c


def mirror_x(tm):
    m = tm.copy()
    m.apply_transform(np.array([[-1, 0, 0, 2 * X_CL], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]]))
    return m


def dilate(tm, d):
    """Cheap dilation: scale about the centroid so every face moves out by
    >= d (exact for boxes/cylinders used here, conservative otherwise)."""
    ext = tm.bounds[1] - tm.bounds[0]
    s = 1.0 + 2.0 * d / np.maximum(ext, 1e-6)
    m = tm.copy()
    c = tm.bounds.mean(axis=0)
    m.apply_translation(-c)
    m.apply_scale(s)
    m.apply_translation(c)
    return m


# ---------------------------------------------------------------------------
# Rev T5 layout (hull frame, mm).  Port side given; 'mirror': True makes a
# starboard twin about X_CL.  THESE ARE THE SINGLE-SOURCE NUMBERS -- the
# bracket / cradle / void-former SCAD files read them from the generated
# include `cargo_layout_t5_params.scad` (--write-scad), and
# merge_cargo_interior.py imports this module.
# ---------------------------------------------------------------------------
# Drive shaft (WING_SHAFT_Y / WING_SHAFT_Z in merge_cargo_interior.py)
SHAFT_Y, SHAFT_Z = 46.60, 69.09
# Worm stage -- Rev T5e (2026-09-16), supersedes the Rev T5b/T5c/T5d numbers.
# m1 40T wheel on the drive shaft driven by a SIX-start O26 worm on a Pololu
# 20D 25:1 CB 6 V gearmotor (#3712, REF-ACT-001): 6.667:1 here, 23.8:1 overall
# with the 14T/50T tip stage -> 144 deg/s at the nacelle no-load (570 rpm),
# lead angle atan(6/26) = 13.0 deg, NOT self-locking (never was the design
# basis) -- the hold is the pin brake (tilt_brake.scad, BRK-1..3).
# WHY THE 25D WENT (T5d-1, found 2026-09-16): for a motor coaxial with the
# worm, the motor-to-wheel-tip gap is (WORM_PD/2 - MOTOR_D/2 - m), independent
# of C and of the worm's angle on the wheel -- rotating the worm (the first
# T5e idea) does not change it, and a worm swung >= 5 deg aft lands on the
# port hoist line at Y 55.5.  With the worm's inboard reach capped by the
# battery cradle (WORM_PD <= 26 at WORM_X -125.25) the motor is capped at
# O20 for a 2 mm gap.  The 20D's 41 mm body (+6 mm rear shaft) also ends the
# chin-flank problem (forward end now Y -7.9), which is moot anyway: the two
# remaining avionics nodes
# now lie FLAT on the chin floor under the battery nose (N_CHIN_*).
# The single-start 40:1 option (24 deg/s) is kept under --option 1 for the
# trade record (tools/tilt_actuator_options.py).
GEAR_MODULE = 1.0
WHEEL_N = 40
WORM_STARTS = 6
WHEEL_PD = GEAR_MODULE * WHEEL_N  # 40.0
WORM_PD = 26.0
STAGE_C = (WHEEL_PD + WORM_PD) / 2  # 33.0 mm centre distance
STAGE_RATIO = WHEEL_N / WORM_STARTS  # 6.667:1
WORM_Z = SHAFT_Z + STAGE_C  # 102.09 -- worm axis ABOVE shaft
# Wheel outboard face.  The lower sidewall at the shaft station is at X -115
# (ray-probed 2026-09-15, Y 46.6 / Z 62), so the bonded root flange's inner
# face is at -120 there.  Rev T5e moves the plane 1 mm outboard (-122.75 vs
# -123.75: 2.75 mm to the flange face, a static bonded part) so the O26 worm's
# inboard tip stays at X -139.25 -- 3.2 mm off the battery cradle's port face.
GEAR_X_OUT = -122.75
WHEEL_FACE = 5.0
WORM_X = GEAR_X_OUT - WHEEL_FACE / 2  # -125.25 wheel/worm mid-plane
WORM_LEN = 10.0  # >= 2*m*sqrt(z2/2+1) = 8.2 mm
MOTOR_D = 20.0  # Pololu 20D (REF-ACT-001)
MOTOR_BODY_L = 41.0  # #3712 "20Dx41L": gearbox + motor, no shafts
# #3712 carries a 6 x 2 mm EXTENDED REAR SHAFT (O2); modelled at the full
# body diameter as a conservative envelope.  No encoder is fitted: the inner-
# loop sensor is the LibreServo AEAT-8800 reading a magnet in the worm's
# brake collar (SENSOR_*), so the controller change request stays TC-2.
MOTOR_ENC_L = 6.0
MOTOR_L = MOTOR_BODY_L + MOTOR_ENC_L
MOTOR_SHAFT_L = 18.0  # O4 D output shaft (20D: 18 mm)
WORM_HUB_L = 2.5  # hub, face plate to worm
# Rev T5e: the worm is CENTRED on the wheel (the T5d +2.5 mm aft offset was
# for the chin flank, no longer needed); its aft end at Y 51.6 leaves 3.9 mm
# to the port hoist line at Y 55.5 (was 1.4).
WORM_OFFSET = 0.0
WORM_YC = SHAFT_Y + WORM_OFFSET  # 46.6 worm centre
# 39.1; motor body Y -7.9..39.1 (the 2.5 mm hub turns inside the bracket's 2.5 mm face plate)
MOTOR_FACE_Y = WORM_YC - WORM_LEN / 2 - WORM_HUB_L
MOTOR_HOLE_S = 15.0  # 2 x M2.5 face-plate holes (20D: 15 mm -- VERIFY on the drawing)
# Brake (BRK-1..3): spring-applied AXIAL pin into a 12-slot face-castellated
# collar on the worm's aft stub -- on the 18 mm shaft: 2.5 hub + 10 worm +
# 0.5 + 4 collar = 17.0, so the collar seats on the D-flat itself.  The pull
# solenoid sits aft of the collar, its axis 1.5 mm INBOARD of the worm axis
# so the O12 coil clears the bracket web plane (X -119.75) by 1.0 mm; the pin
# is at the slot circle's top and is pulled through a yoke.  Coaxial-aft is
# the only placement that clears the winch axle (Z 139-143) above and the
# payload crown (Z 85) below.  Envelope only here; part in tilt_brake.scad.
BRAKE_COLLAR_D, BRAKE_COLLAR_L = 14.0, 4.0
BRAKE_Y = WORM_YC + WORM_LEN / 2 + BRAKE_COLLAR_L / 2 + 0.5  # 54.1 collar centre
BRAKE_SOL_D, BRAKE_SOL_L = 12.0, 24.0  # solenoid envelope (VERIFY part: BOM SOL-TILT-BRAKE)
BRAKE_SOL_X = WORM_X - 1.5  # -126.75
SENSOR_PCB_T = 3.0  # AEAT-8800 carrier (part of the brake guide block face)
# 62.1: 1 mm gap + 5 mm guide block (pin, sensor), then the coil to 86.1
BRAKE_SOL_Y0 = BRAKE_Y + BRAKE_COLLAR_L / 2 + 3.0 + SENSOR_PCB_T
# Tilt CONTROLLER board (LibreServo_v4.1-TC, 36.5 x 42.9, card-edge rails on
# the bracket).  Rev T5b put it on the web's INBOARD face at Y 38..81 / Z
# 93..129.5 -- straight through the worm (T5d-2, found 2026-09-16: the board
# was never an envelope here).  Rev T5e: on the web's OUTBOARD face, in the
# shoulder pocket, clear of the motor's and worm's reach past the web plane
# (motor to X -115.25, worm tip to -111.25).  7.4 mm = rails 4 (component
# side toward the web) + board 1.6 + 2 x 0.3 + 1.2 rail lip; the bare back
# faces the skin.
BOARD_L, BOARD_W, BOARD_T = 42.9, 36.5, 7.4  # Y, Z, X
# Position: AFT of the worm's reach (Y > 54.6) so the board can sit right on
# the web (X -117.75..-110.75); Z 88..124.5 above foot 2 and under the
# shoulder's curve-in; Y 55..97.9 overlaps the aft node N2's Y band, so N2's
# outboard face moved to X -113.85 (N_AFT_XC).  Grid-searched 2026-09-16: no
# position forward of the worm clears the wall at Y < 12 / Z > 108 by 2 mm.
BOARD_X0 = GEAR_X_OUT + 5.0  # -117.75, the web's outboard face
BOARD_Y0, BOARD_Z0 = 55.0, 83.0
# Old NSVMT DS3225 pads, still IN the published shell -- subtracted here so
# the check reflects the shell AFTER this rev's merge (they are gated off).
NSVMT_PAD_PORT = (-160.0, -94.0, 15.0, 78.0, 84.0, 114.0)
# Battery (BATTERY_MOUNT.md SS1, Tattu 6S 4000 class) -- LONGITUDINAL in the
# roof band, on the centreline.
BATT_L, BATT_W, BATT_H = 142.0, 50.0, 38.0
# centred (a 1.5 mm port shift was tried for the chin nodes on 2026-09-16 and reverted)
BATT_XC = X_CL
BATT_X0, BATT_X1 = BATT_XC - BATT_W / 2, BATT_XC + BATT_W / 2
BATT_Y0 = -58.0  # head/cargo collar ends at -61.5
BATT_Y1 = BATT_Y0 + BATT_L  # +84.0
BATT_Z0 = 90.0  # payload crown 84.92 + cradle + gap
BATT_Z1 = BATT_Z0 + BATT_H  # 128.0
CRADLE_T = 2.4
# The cradle is an INVERTED U hung from the roof: the battery is pushed up
# into it from the open belly (doors open, winch not yet fitted) and held by
# two cam straps under it -- field exchange needs neither roof access nor
# winch removal (docs/BATTERY_MOUNT.md Rev T5 SS3).
CRADLE_FWD_BOSS_Y = -50.0  # roof hangers, chin roof (Z ~143)
CRADLE_AFT_BOSS_Y = 80.0  # roof hangers (roof Z ~161)
CRADLE_BOSS_DX = 18.0  # +/- from cradle centreline
CRADLE_TOP_Z = BATT_Z1 + CRADLE_T  # ceiling plate top, 130.4
# Dorsal-notch relief: the roof dips to Z ~131 over Y -20..+2, so the
# ceiling plate is cut away there across the full width and the side rails
# step down to CRADLE_RELIEF_Z -- the battery's own top (128) is then the
# highest thing under the notch, 3 mm below the skin.
CRADLE_RELIEF_Y = (-20.0, 2.0)
CRADLE_RELIEF_Z = BATT_Z1 - 1.0  # 127.0, rail top through the relief
CRADLE_XC = BATT_XC
# Avionics nodes -- Rev T5c (owner, 2026-09-15): all FOUR control nodes stay
# in the cargo section, any orientation, in a Faraday POUCH (foil, ~1 mm)
# rather than the 55-deep rigid tray, with room for signal/power cables.
# Node = PB2I (56 x 35) + cape (55 x 35) stacked on 0.1" headers, ~20 mm;
# with the pouch: 58 x 37 x 22 (VERIFY the stack height at first article).
# Placement (proved below against the shell and every other envelope):
#   N1 CN2 (Inara)  CHIN FLOOR, port half, lying flat under the battery nose
#   N3 CN3 (River)  chin floor, stbd half, mirror of N1
#   N2 FC2 (Inara)  aft strip behind the battery, port half, transverse
#   N4 FC3 (River)  aft strip, stbd half
# Each node keeps a 10 mm CABLE ZONE along its connector edge.
# HISTORY of the chin pair: standing on edge in the chin FLANKS beside the
# battery nose was measured 0.2-0.5 mm short on 2026-09-15 (Y window to the
# motor's forward end; the lower-forward wall fillet) and again on 2026-09-16
# after the worm offset and a 1.5 mm cradle shift (port touches the bay
# sidewall at X -117, stbd interferes ~1 mm along its outboard face -- the
# hull is 2.7 mm asymmetric there).  The shoulder pockets outboard of the
# tilt brackets were measured first and rejected (55 x 31 mm window vs the
# 35 mm board).  Rev T5e (2026-09-16): the pair lies FLAT on the chin floor
# under the battery nose, Y -58..0 (head/cargo collar ring ends at -53.5,
# payload box starts at 4.7), Z 66..88 (2 mm under the battery), 37 mm wide
# each with a shared 10 mm cable channel on the centreline -- zero hit and
# zero 2 mm-near volume on both sides, first try.  They sit on a printed
# CHIN SHELF (chin_node_shelf.scad) on four floor bosses; the shelf's two
# inboard lips (1.6 x 4 mm) stand at the cable channel's floor.
NODE_L, NODE_H, NODE_T = 58.0, 37.0, 22.0  # pouch-inclusive: board length, board height, stack
NODE_CABLE = 10.0  # connector-edge clearance
# chin floor nodes: X = board height (37), Y = board length (58), Z = stack (22)
N_CHIN_Y0, N_CHIN_Y1 = -58.0, 0.0
N_CHIN_Z1 = BATT_Z0 - 2.0  # 88.0: 2 mm static gap under the battery
N_CHIN_Z0 = N_CHIN_Z1 - NODE_T  # 66.0
N_CHIN_X_IN = X_CL + NODE_CABLE / 2  # port node inner face (-164.85); stbd mirrored
# aft strip nodes: X = board length (58), Y = stack (22), Z = board height (37)
# Rev T5e: the aft pair moved 8.5 mm aft (91 -> 99.5) so the tilt-controller
# boards (Y 55..97.9, on the brackets' outboard faces) clear them by 1.6 mm
# in Y -- board and node are both static, and they are also 3.9 mm apart in
# X; the nodes' aft faces at Y 121.5 reach 0.5 mm into the middle-section
# splice collar's ring zone (Y 121..129), checked at 4.5 mm below.
N_AFT_Y0 = 99.5
N_AFT_Z0 = 87.0  # payload crown 84.92 + 2 (static gap); keeps the top under the wall's curve-in
# port / stbd centres (3 mm apart; the pair sits 0.5 mm stbd of centre -- the
# port shoulder curves in earlier); GPS cups (Z >= 139) are above
N_AFT_XC = (X_CL + 30.0, X_CL - 31.0)
CHIN_NODES = True
# Chin shelf: 2.4 mm plate under the two chin nodes on four M3 floor bosses --
# forward pair on the chin floor (Z ~60 at Y -49), aft pair on the ramp
# fairing's inner face (Z ~44 at Y -33).  SHELF_Z0 is the plate's underside.
SHELF_T = 2.4
SHELF_Z0 = N_CHIN_Z0 - SHELF_T  # 63.6
# plate: clear of the head/cargo splice collar ring (Y -61.5..-53.5) and the
# payload (4.7); the pouches overhang it 6 mm forward
SHELF_Y0, SHELF_Y1 = -52.0, 1.6
SHELF_SILL_Y1 = -45.0  # forward of this the plate lies on the floor
SHELF_BOSS = (
    (X_CL - 30.0, -49.0),
    (X_CL + 30.0, -49.0),
    (X_CL - 20.0, -33.0),
    (X_CL + 20.0, -33.0),
)  # (X, Y)
# Cargo-bay OBSERVER board (cargo_vera_faraday.scad Rev S1: 69.85 x 58 board,
# tray 76.8 x 70.8 x ~20 + lid/vents) and its 28 mm nadir camera -- NOT
# PLACED in Rev T5 (found 2026-09-16 on owner question).  Rev T5e: STANDING
# in the aft belly strip behind the payload box, tray face transverse,
# Y 108.5..128.5 (payload aft face 106.3 + 2.2; the middle-section splice
# collar's 8 mm ring, Y 121..129, is 2 mm wall on the shell and the tray
# clears the shell by > 4.5 mm there), Z 14.2..85.0 -- 2 mm under the aft
# nodes' bottom (87).  The camera looks FORWARD-DOWN through the clamshell
# aperture (Y 2..108) from the tray's top edge: a hoist monitor, no belly
# window.  Four M2.5 belly bosses (floor Z ~1-2 there).
OBSERVER_L, OBSERVER_W, OBSERVER_T = 76.8, 70.8, 20.0
OBSERVER_Y0 = 108.5
OBSERVER_Z0 = 14.2
OBSERVER_PLACED = True
OBSERVER_BOSS = (
    (-30.0, 4.0, 4.0),
    (30.0, 4.0, 4.0),
    (-30.0, 8.5, 3.5),
    (30.0, 8.5, 3.5),
)  # (dX, dY, half-size)
WALL_SLICES = False  # the rejected shoulder-pocket option, kept for the record
SLICE_T, SLICE_L, SLICE_H, SLICE_Z0, SLICE_Y0 = 20.0, 55.0, 31.0, 81.0, 52.0
SLICE_X_IN = GEAR_X_OUT + 5.0 + GAP_MM
# Legacy dorsal-tray constants (retired at Rev T5; kept for the record)
TRAY_X, TRAY_Y, TRAY_D = 40.0, 60.0, 55.0
INARA_XC, INARA_YC = -132.0, 86.0
INARA_BOSS_DX, INARA_BOSS_DY = 15.0, 25.0
TRAYS_IN_CARGO = False
# Mission payload (cargo_bay_envelope.py gate) + TWIN-LINE bridle hoist.
# The box goes up long-side along Y (101.6 in the 106 mm aperture); the two
# lines straddle the battery, GAP_MM outboard of the cradle walls.
PAYLOAD = (76.2, 101.6, 76.2)  # X, Y, Z
# The box is a hoisted soft load, not a moving machine part: its lateral
# margin to the wheels is 3.0 mm and its Y margin in the aperture 2.2 mm.
HOIST_Y = 55.5  # box Y 4.7..106.3 in the 2..108 aperture
LINE_R = 0.5  # 1 mm Dyneema
HOIST_DX = BATT_W / 2 + CRADLE_T + GAP_MM + LINE_R  # 30.9 from the battery centre
HOIST_XS = (BATT_XC - HOIST_DX, BATT_XC + HOIST_DX)
DOOR_CROWN_Z = 8.72
DRUM_D, DRUM_L = 16.0, 12.0
SPOOL_Z0 = BATT_Z1 + CRADLE_T + GAP_MM  # 133.4, above the cradle ceiling
# Canonical forward cargo-ramp fairing: opening measured by ray map
RAMP_X0, RAMP_X1 = -194.0, -142.0
RAMP_Z0, RAMP_Z1 = 8.0, 44.0
RAMP_OVERLAP = 6.0  # fuse margin onto the flanks


def layout_t5():
    L = {}
    # --- tilt actuator, port (mirror for stbd) ------------------------------
    L["worm wheel"] = dict(
        mirror=True,
        solid=cyl(
            "x", SHAFT_Y, SHAFT_Z, GEAR_X_OUT - WHEEL_FACE, GEAR_X_OUT, WHEEL_PD / 2 + GEAR_MODULE
        ),
    )
    L["worm"] = dict(
        mirror=True,
        solid=cyl(
            "y",
            WORM_X,
            WORM_Z,
            WORM_YC - WORM_LEN / 2,
            WORM_YC + WORM_LEN / 2,
            WORM_PD / 2 + GEAR_MODULE,
        ),
        mates=("worm wheel", "worm wheel (stbd)"),
    )
    # motor body FORWARD of the worm: face plate at MOTOR_FACE_Y, body toward -Y
    # T5e: O20 body at C 33 sits 2.0 mm above the O42 wheel tip (T5d-1 closed);
    # both are bracket-located, so 2 mm is accepted in place of GAP_MM
    L["motor"] = dict(
        mirror=True,
        solid=cyl("y", WORM_X, WORM_Z, MOTOR_FACE_Y - MOTOR_L, MOTOR_FACE_Y, MOTOR_D / 2),
    )
    L["tilt controller board"] = dict(
        mirror=True,
        solid=box(
            BOARD_X0, BOARD_X0 + BOARD_T, BOARD_Y0, BOARD_Y0 + BOARD_L, BOARD_Z0, BOARD_Z0 + BOARD_W
        ),
        gap=2.0,
    )
    L["brake collar"] = dict(
        mirror=True,
        solid=cyl(
            "y",
            WORM_X,
            WORM_Z,
            BRAKE_Y - BRAKE_COLLAR_L / 2,
            BRAKE_Y + BRAKE_COLLAR_L / 2,
            BRAKE_COLLAR_D / 2,
        ),
        mates=("worm", "worm (stbd)"),
    )
    L["brake solenoid"] = dict(
        mirror=True,
        solid=cyl(
            "y", BRAKE_SOL_X, WORM_Z, BRAKE_SOL_Y0, BRAKE_SOL_Y0 + BRAKE_SOL_L, BRAKE_SOL_D / 2
        ),
        mates=("brake collar", "brake collar (stbd)"),
    )
    # feet reach OUTBOARD to the skin: (Y, Z) stations, X from the foot face
    for i, (fy, fz) in enumerate(BRACKET_FEET):
        L[f"bracket foot {i}"] = dict(
            mirror=True,
            solid=box(GEAR_X_OUT + 4.0, -60.0, fy - 6.0, fy + 6.0, fz - 6.0, fz + 6.0),
            skin_seat=True,
        )
    # --- battery: LONGITUDINAL, roof band, printed cradle --------------------
    # Battery and payload are static (or soft) bodies against the fixed hull:
    # they carry a 2.0 mm skin gap, not the 3.0 mm moving-part budget.  The
    # battery's only sub-3 mm point is the dorsal notch at Y -9..-4 (roof
    # dips to Z ~131 over the battery's Z 128 top).
    L["battery"] = dict(solid=box(BATT_X0, BATT_X1, BATT_Y0, BATT_Y1, BATT_Z0, BATT_Z1), gap=2.0)
    cr = box(
        BATT_X0 - CRADLE_T,
        BATT_X1 + CRADLE_T,
        BATT_Y0 - CRADLE_T,
        BATT_Y1 + CRADLE_T,
        BATT_Z0,
        CRADLE_TOP_Z,
    )
    win = box(
        BATT_X0 - CRADLE_T - 1.0,
        BATT_X1 + CRADLE_T + 1.0,
        CRADLE_RELIEF_Y[0],
        CRADLE_RELIEF_Y[1],
        CRADLE_RELIEF_Z,
        CRADLE_TOP_Z + 1.0,
    )
    crm = to_man(cr) - to_man(win)
    msh = crm.to_mesh()
    cr_tm = trimesh.Trimesh(
        np.asarray(msh.vert_properties)[:, :3], np.asarray(msh.tri_verts), process=False
    )
    L["battery cradle"] = dict(solid=cr_tm, mates=("battery",))
    for i, dx in enumerate((-CRADLE_BOSS_DX, CRADLE_BOSS_DX)):
        for tag, by in (("fwd", CRADLE_FWD_BOSS_Y), ("aft", CRADLE_AFT_BOSS_Y)):
            L[f"cradle {tag} hanger {i}"] = dict(
                solid=box(
                    CRADLE_XC + dx - 5.0,
                    CRADLE_XC + dx + 5.0,
                    by - 5.0,
                    by + 5.0,
                    CRADLE_TOP_Z,
                    175.0,
                ),
                skin_seat=True,
                mates=("battery cradle",),
            )
    if TRAYS_IN_CARGO:
        L["Inara tray"] = dict(
            solid=box(
                INARA_XC - TRAY_X / 2,
                INARA_XC + TRAY_X / 2,
                INARA_YC - TRAY_Y / 2,
                INARA_YC + TRAY_Y / 2,
                163.0 - TRAY_D,
                163.0,
            ),
            skin_seat=True,
        )
    if WALL_SLICES:  # measured negative -- see the WALL_SLICES note above
        L["avionics slice (port)"] = dict(
            solid=box(
                SLICE_X_IN,
                SLICE_X_IN + SLICE_T,
                SLICE_Y0,
                SLICE_Y0 + SLICE_L,
                SLICE_Z0,
                SLICE_Z0 + SLICE_H,
            ),
            gap=1.0,
        )
        L["avionics slice (stbd)"] = dict(
            solid=mirror_x(L["avionics slice (port)"]["solid"]), gap=1.0
        )
    # Rev T5c avionics nodes (static equipment: 2.0 mm skin gap, like the battery)
    if CHIN_NODES:
        # flat on the chin floor, port half; the 10 mm cable channel between
        # the pair (X_CL +/- 5) is shared, connector edges inboard
        n1 = box(N_CHIN_X_IN, N_CHIN_X_IN + NODE_H, N_CHIN_Y0, N_CHIN_Y1, N_CHIN_Z0, N_CHIN_Z1)
        L["node N1 CN2 (port chin)"] = dict(solid=n1, gap=2.0)
        L["node N3 CN3 (stbd chin)"] = dict(solid=mirror_x(n1), gap=2.0)
        L["chin cable channel"] = dict(
            solid=box(
                X_CL - NODE_CABLE / 2,
                X_CL + NODE_CABLE / 2,
                N_CHIN_Y0,
                N_CHIN_Y1,
                N_CHIN_Z0,
                N_CHIN_Z1,
            ),
            gap=2.0,
            mates=("node N1 CN2 (port chin)", "node N3 CN3 (stbd chin)"),
        )
        # the plate's forward 13 mm is a SILL that lies on the chin floor
        # (Z 60-62.4 there, rising forward), bolted through the two forward
        # bosses; aft of Y -45 the floor falls away and the plate is clear
        sx1 = N_CHIN_X_IN + NODE_H  # port node outboard face (-127.85)
        sx0 = 2 * X_CL - sx1  # stbd mirror (-211.85)
        L["chin shelf"] = dict(
            solid=box(sx0, sx1, SHELF_SILL_Y1, SHELF_Y1, SHELF_Z0, SHELF_Z0 + SHELF_T),
            gap=2.0,
            mates=("node N1 CN2 (port chin)", "node N3 CN3 (stbd chin)", "chin cable channel"),
        )
        L["chin shelf sill"] = dict(
            solid=box(sx0, sx1, SHELF_Y0, SHELF_SILL_Y1, SHELF_Z0, SHELF_Z0 + SHELF_T),
            skin_seat=True,
            mates=(
                "node N1 CN2 (port chin)",
                "node N3 CN3 (stbd chin)",
                "chin cable channel",
                "chin shelf",
            ),
        )
        for i, (bx, by) in enumerate(SHELF_BOSS):
            L[f"shelf boss {i}"] = dict(
                solid=box(bx - 5.0, bx + 5.0, by - 5.0, by + 5.0, 0.0, SHELF_Z0 + 0.5),
                skin_seat=True,
                mates=("chin shelf", "chin shelf sill", "ramp fairing"),
            )
    if OBSERVER_PLACED:
        L["observer tray"] = dict(
            solid=box(
                X_CL - OBSERVER_L / 2,
                X_CL + OBSERVER_L / 2,
                OBSERVER_Y0,
                OBSERVER_Y0 + OBSERVER_T,
                OBSERVER_Z0,
                OBSERVER_Z0 + OBSERVER_W,
            ),
            gap=2.0,
        )
        # four floor bosses; the aft row stays forward of the splice collar
        # ring zone (Y >= 121) -- OBSERVER_BOSS is (dX, dY from OBSERVER_Y0, half-size)
        for i, (dx, dy, h) in enumerate(OBSERVER_BOSS):
            L[f"observer boss {i}"] = dict(
                solid=box(
                    X_CL + dx - h,
                    X_CL + dx + h,
                    OBSERVER_Y0 + dy - h,
                    OBSERVER_Y0 + dy + h,
                    -5.0,
                    OBSERVER_Z0 + 0.5,
                ),
                skin_seat=True,
                mates=("observer tray",) + tuple(f"observer boss {j}" for j in range(4)),
            )
    for tag, xc, outb in (
        ("N2 FC2 (aft port)", N_AFT_XC[0], +1),
        ("N4 FC3 (aft stbd)", N_AFT_XC[1], -1),
    ):
        nb = box(
            xc - NODE_L / 2,
            xc + NODE_L / 2,
            N_AFT_Y0,
            N_AFT_Y0 + NODE_T,
            N_AFT_Z0,
            N_AFT_Z0 + NODE_H,
        )
        # the outboard-top edge of each aft node meets the shoulder's curve-in
        # 1.5 mm short of the 2 mm static gap: the pouch's fold there is a 5 mm
        # 45-degree chamfer (the PCB corner inside is 2 mm inboard of the pouch)
        xe = xc + outb * NODE_L / 2
        # keep the half of the wedge below the 45-degree line: approximate the
        # chamfer by a 2-step stair (2.5 mm x 2.5 mm) -- conservative
        st1 = box(
            min(xe, xe - outb * 5.0),
            max(xe, xe - outb * 5.0),
            N_AFT_Y0 - 1,
            N_AFT_Y0 + NODE_T + 1,
            N_AFT_Z0 + NODE_H - 2.5,
            N_AFT_Z0 + NODE_H + 1,
        )
        st2 = box(
            min(xe, xe - outb * 2.5),
            max(xe, xe - outb * 2.5),
            N_AFT_Y0 - 1,
            N_AFT_Y0 + NODE_T + 1,
            N_AFT_Z0 + NODE_H - 5.0,
            N_AFT_Z0 + NODE_H + 1,
        )
        nm = to_man(nb) - to_man(st1) - to_man(st2)
        msh = nm.to_mesh()
        L[f"node {tag}"] = dict(
            solid=trimesh.Trimesh(
                np.asarray(msh.vert_properties)[:, :3], np.asarray(msh.tri_verts), process=False
            ),
            gap=2.0,
        )
        L[f"node {tag} cable zone"] = dict(
            solid=box(
                xc - 20.0,
                xc + 20.0,
                N_AFT_Y0,
                N_AFT_Y0 + NODE_T,
                N_AFT_Z0 + NODE_H,
                N_AFT_Z0 + NODE_H + NODE_CABLE,
            ),
            gap=2.0,
            mates=(f"node {tag}",),
        )
    # --- mission payload + twin-line bridle hoist (Phase 7 reserve) ----------
    L["payload"] = dict(
        solid=box(
            BATT_XC - PAYLOAD[0] / 2,
            BATT_XC + PAYLOAD[0] / 2,
            HOIST_Y - PAYLOAD[1] / 2,
            HOIST_Y + PAYLOAD[1] / 2,
            DOOR_CROWN_Z,
            DOOR_CROWN_Z + PAYLOAD[2],
        ),
        keepout=True,
        gap=2.0,
    )
    for i, hx in enumerate(HOIST_XS):
        L[f"hoist line {i}"] = dict(
            solid=cyl("z", hx, HOIST_Y, DOOR_CROWN_Z + PAYLOAD[2], SPOOL_Z0 + DRUM_D / 2, LINE_R),
            keepout=True,
            mates=("payload",),
        )
        L[f"winch drum {i} (Phase 7)"] = dict(
            solid=cyl(
                "x", HOIST_Y, SPOOL_Z0 + DRUM_D / 2, hx - DRUM_L / 2, hx + DRUM_L / 2, DRUM_D / 2
            ),
            keepout=True,
            mates=(f"hoist line {i}",),
        )
    L["winch axle (Phase 7)"] = dict(
        solid=cyl("x", HOIST_Y, SPOOL_Z0 + DRUM_D / 2, HOIST_XS[0] - 14.0, HOIST_XS[1] + 14.0, 2.0),
        keepout=True,
        mates=("winch drum 0 (Phase 7)", "winch drum 1 (Phase 7)", "hoist line 0", "hoist line 1"),
    )
    # --- ramp fairing (fused skin plate; expected to sit ON the flank skin) --
    L["ramp fairing"] = dict(
        solid=box(
            RAMP_X0 - RAMP_OVERLAP,
            RAMP_X1 + RAMP_OVERLAP,
            -40.0,
            -14.0,
            RAMP_Z0 - RAMP_OVERLAP,
            RAMP_Z1 + RAMP_OVERLAP,
        ),
        skin_seat=True,
    )
    return L


# Bracket feet (Y, Z) -- three, outboard to the skin.  Clear of the root
# flange (Y -9..51, Z 27..107), the LG bays (Y -16..20 / 80..110, Z < 83)
# and the harness bores (Z 62..69).
# Foot 2 sits above the mortise (Z 52..73) and forward of the aft LG bay's
# upper bolt bores (Y >= 72.6, Z <= 80.1; feet at Y 74 and 66 fouled bolt3/bolt4
# in tools/landing_gear_wing_clearance.py --proud, 2026-09-15).
# Bracket feet (Y, Z) -- three, outboard to the skin.  Clear of the root
# flange (Y -9..51, Z 27..107), the LG bays (Y -16..20 / 80..110, Z < 83)
# and the harness bores (Z 62..69).  Foot 2 sits above the mortise (Z 52..73)
# and forward of the aft LG bay's upper bolt bores (Y >= 72.6, Z <= 80.1;
# feet at Y 74 and 66 fouled bolt3/bolt4 in tools/landing_gear_wing_clearance.py
# --proud, 2026-09-15).  A top-row-only arrangement was tried on 2026-09-15 to
# free the shoulder pocket for avionics slices and reverted: the pocket does
# not take a 35 mm node anyway (see WALL_SLICES).
# Rev T5e feet: 0 and 1 in the top row (Z 124.09) forward of the controller
# board, foot 2 low at (Y 64, Z 77) -- 2 mm above the harness bores (Z <= 69),
# fusing into the mortise block (Z <= 72.9, boss on boss), 2.6 mm forward of
# the aft LG bay's bolt3 bores (Y >= 72.6) and 2 mm under the board (Z 85).
BRACKET_FEET = (
    (SHAFT_Y - 36.0, WORM_Z + 22.0),
    (SHAFT_Y - 6.6, WORM_Z + 22.0),
    (SHAFT_Y + 17.4, SHAFT_Z + 7.91),
)
# Feet of the LAST PUBLISHED shell, subtracted in shell_after_merge so the
# check does not see bosses a re-layout moves.  Update when re-merging
# (Rev T5e shell published 2026-09-16 with BRACKET_FEET above; the Rev T5d
# feet were (10.6, 123.09), (68.6, 123.09), (62.0, 86.0) at X -119.75).
PUBLISHED_FEET = BRACKET_FEET
PUBLISHED_FOOT_X = GEAR_X_OUT + 4.0


def shell_after_merge(shell_tm):
    """Published shell minus the retired DS3225 pads (both sides) and minus
    this layout's OWN bosses (cradle hangers, winch pedestals), so the
    equipment that bolts to those bosses is not reported as 'near' them."""
    m = to_man(shell_tm)
    pad = box(*NSVMT_PAD_PORT)
    m = m - to_man(pad) - to_man(mirror_x(pad))
    for fy, fz in PUBLISHED_FEET:
        fb = box(PUBLISHED_FOOT_X, -60.0, fy - 6.5, fy + 6.5, fz - 6.5, fz + 6.5)
        m = m - to_man(fb) - to_man(mirror_x(fb))
    for dx in (-CRADLE_BOSS_DX, CRADLE_BOSS_DX):
        for by in (CRADLE_FWD_BOSS_Y, CRADLE_AFT_BOSS_Y):
            m = m - to_man(
                box(
                    CRADLE_XC + dx - 5.5,
                    CRADLE_XC + dx + 5.5,
                    by - 5.5,
                    by + 5.5,
                    CRADLE_TOP_Z - 0.5,
                    170.0,
                )
            )
    if CHIN_NODES:
        for bx, by in SHELF_BOSS:
            m = m - to_man(box(bx - 5.5, bx + 5.5, by - 5.5, by + 5.5, 2.0, SHELF_Z0 + 0.5))
    if OBSERVER_PLACED:
        for dx, dy, h in OBSERVER_BOSS:
            m = m - to_man(
                box(
                    X_CL + dx - h - 0.5,
                    X_CL + dx + h + 0.5,
                    OBSERVER_Y0 + dy - h - 0.5,
                    OBSERVER_Y0 + dy + h + 0.5,
                    2.5,
                    OBSERVER_Z0 + 0.5,
                )
            )
    for hx in HOIST_XS:
        px = hx - DRUM_L / 2 - 5.0 if hx < X_CL else hx + DRUM_L / 2 + 5.0
        m = m - to_man(
            box(
                px - 5.5, px + 5.5, HOIST_Y - 5.5, HOIST_Y + 5.5, SPOOL_Z0 + DRUM_D / 2 - 6.5, 170.0
            )
        )
    msh = m.to_mesh()
    return trimesh.Trimesh(
        np.asarray(msh.vert_properties)[:, :3], np.asarray(msh.tri_verts), process=False
    )


def write_scad(path):
    names = [
        "SHAFT_Y",
        "SHAFT_Z",
        "GEAR_MODULE",
        "WHEEL_N",
        "WORM_STARTS",
        "WHEEL_PD",
        "WORM_PD",
        "STAGE_C",
        "WORM_Z",
        "GEAR_X_OUT",
        "WHEEL_FACE",
        "WORM_X",
        "WORM_LEN",
        "MOTOR_D",
        "MOTOR_BODY_L",
        "MOTOR_ENC_L",
        "MOTOR_SHAFT_L",
        "MOTOR_FACE_Y",
        "MOTOR_HOLE_S",
        "BATT_L",
        "BATT_W",
        "BATT_H",
        "BATT_X0",
        "BATT_X1",
        "BATT_Y0",
        "BATT_Y1",
        "BATT_Z0",
        "BATT_Z1",
        "CRADLE_T",
        "CRADLE_FWD_BOSS_Y",
        "CRADLE_AFT_BOSS_Y",
        "CRADLE_BOSS_DX",
        "CRADLE_XC",
        "CRADLE_TOP_Z",
        "CRADLE_RELIEF_Z",
        "TRAY_X",
        "TRAY_Y",
        "TRAY_D",
        "INARA_XC",
        "INARA_YC",
        "INARA_BOSS_DX",
        "INARA_BOSS_DY",
        "NODE_L",
        "NODE_H",
        "NODE_T",
        "NODE_CABLE",
        "N_CHIN_X_IN",
        "N_CHIN_Y0",
        "N_CHIN_Z0",
        "N_AFT_Y0",
        "N_AFT_Z0",
        "HOIST_Y",
        "HOIST_DX",
        "LINE_R",
        "WORM_HUB_L",
        "WORM_OFFSET",
        "WORM_YC",
        "BRAKE_COLLAR_D",
        "BRAKE_COLLAR_L",
        "BRAKE_Y",
        "BRAKE_SOL_D",
        "BRAKE_SOL_L",
        "BRAKE_SOL_Y0",
        "SENSOR_PCB_T",
        "STAGE_RATIO",
        "DRUM_D",
        "DRUM_L",
        "SPOOL_Z0",
        "BATT_XC",
        "RAMP_X0",
        "RAMP_X1",
        "RAMP_Z0",
        "RAMP_Z1",
        "RAMP_OVERLAP",
        "X_CL",
        "GAP_MM",
        "BRAKE_SOL_X",
        "BOARD_L",
        "BOARD_W",
        "BOARD_T",
        "BOARD_X0",
        "BOARD_Y0",
        "BOARD_Z0",
        "N_CHIN_Y1",
        "N_CHIN_Z1",
        "SHELF_T",
        "SHELF_Z0",
        "SHELF_Y0",
        "SHELF_Y1",
        "SHELF_SILL_Y1",
        "OBSERVER_L",
        "OBSERVER_W",
        "OBSERVER_T",
        "OBSERVER_Y0",
        "OBSERVER_Z0",
    ]
    g = globals()
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(
            "// cargo_layout_t5_params.scad -- GENERATED by tools/cargo_layout_fit.py\n"
            "// --write-scad.  Do not edit: change the Python constants and regenerate.\n"
            "// Hull frame, mm (X=+port, Y=+aft, Z=+dorsal).  Rev T5e, 2026-09-16.\n"
            "// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0\n"
        )
        for n in names:
            fh.write(f"{n} = {float(g[n]):.4f};\n")
        fh.write("N_AFT_XC = [" + ", ".join(f"{x:.2f}" for x in N_AFT_XC) + "];\n")
        fh.write(f"CRADLE_RELIEF_Y = [{CRADLE_RELIEF_Y[0]:.2f}, {CRADLE_RELIEF_Y[1]:.2f}];\n")
        fh.write(
            "BRACKET_FEET = [" + ", ".join(f"[{y:.2f}, {z:.2f}]" for y, z in BRACKET_FEET) + "];\n"
        )
        fh.write(
            "SHELF_BOSS = [" + ", ".join(f"[{x:.2f}, {y:.2f}]" for x, y in SHELF_BOSS) + "];\n"
        )
        fh.write(
            "OBSERVER_BOSS = ["
            + ", ".join(f"[{x:.2f}, {y:.2f}, {h:.2f}]" for x, y, h in OBSERVER_BOSS)
            + "];\n"
        )


# ---------------------------------------------------------------------------
def report(L, shell_tm, plot=False):
    shell = to_man(shell_tm)
    solids = {}
    for name, e in list(L.items()):
        solids[name] = e["solid"]
        if e.get("mirror"):
            solids[name + " (stbd)"] = mirror_x(e["solid"])
            L[name + " (stbd)"] = dict(e, solid=solids[name + " (stbd)"])
    print(f"shell {os.path.relpath(SHELL, REPO)}  faces={len(shell_tm.faces):,}")
    print(f"clearance budget {GAP_MM} mm\n")
    print(
        f"{'envelope':28s} {'hit mm3':>10s} {'<gap mm3':>10s}  note   "
        f"(gap = {GAP_MM} mm unless the envelope declares its own)"
    )
    worst = 0
    for name, tm in solids.items():
        e = L[name]
        m = to_man(tm)
        hit = (m ^ shell).volume()
        gap = e.get("gap", GAP_MM)
        near = (to_man(dilate(tm, gap)) ^ shell).volume()
        note = ""
        if e.get("skin_seat"):
            note = "seats on skin (hit expected: it is a boss)"
            hit_flag = False
        else:
            hit_flag = hit > 1.0
        if hit_flag or (near > 1.0 and not e.get("skin_seat")):
            worst += 1
            b = tm.bounds
            note += (
                f" FAIL (gap {gap})  box X{b[0][0]:.0f}..{b[1][0]:.0f} "
                f"Y{b[0][1]:.0f}..{b[1][1]:.0f} Z{b[0][2]:.0f}..{b[1][2]:.0f}"
            )
        print(f"{name:28s} {hit:10.0f} {near:10.0f}  {note}")
    print("\npairwise interference (raw overlap, mm3; blank = 0):")
    names = list(solids)
    bad = 0
    for i, a in enumerate(names):
        for b_ in names[i + 1:]:
            if b_ in L[a].get("mates", ()) or a in L[b_].get("mates", ()):
                continue
            v = (to_man(solids[a]) ^ to_man(solids[b_])).volume()
            if v > 1.0:
                bad += 1
                print(f"  {a:26s} x {b_:26s} {v:10.0f}  OVERLAP")
    if bad == 0:
        print("  none")
    print(
        f"\nRESULT: {'PASS' if worst == 0 and bad == 0 else 'FAIL'} "
        f"({worst} envelope(s) foul the shell/gap, {bad} pair overlap(s))"
    )
    if plot:
        _plot(shell_tm, solids)
    return worst == 0 and bad == 0


def _plot(shell_tm, solids):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = os.path.join(REPO, "docs", "img")
    os.makedirs(out, exist_ok=True)
    cuts = [("y", v) for v in (-50, -10, 20, 46.6, 55, 80)]
    fig, axs = plt.subplots(2, 3, figsize=(21, 12))
    for ax, (axis, v) in zip(axs.ravel(), cuts):
        n = {"y": [0, 1, 0]}[axis]
        s = shell_tm.section(plane_origin=[0, v, 0], plane_normal=n)
        if s is not None:
            for ent in s.entities:
                p = s.vertices[ent.points]
                ax.plot(p[:, 0], p[:, 2], "k-", lw=0.5)
        for name, tm in solids.items():
            sec = tm.section(plane_origin=[0, v, 0], plane_normal=n)
            if sec is None:
                continue
            for ent in sec.entities:
                p = sec.vertices[ent.points]
                ax.plot(p[:, 0], p[:, 2], lw=1.2, label=name)
        ax.set_title(f"XZ at Y={v}")
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-280, -60)
        ax.set_ylim(-5, 170)
    h, lbl = axs[0][0].get_legend_handles_labels()
    fig.legend(h, lbl, loc="lower center", ncol=6, fontsize=8)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    png = os.path.join(out, "cargo_layout_t5_sections.png")
    fig.savefig(png, dpi=80)
    print(f"wrote {os.path.relpath(png, REPO)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plot", action="store_true")
    ap.add_argument(
        "--option",
        type=int,
        default=2,
        choices=(1, 2),
        help="tilt actuator option to check (2 = baseline 25D HP four-start "
        "worm + brake; 1 = the 20D single-start trade option)",
    )
    ap.add_argument(
        "--write-scad",
        action="store_true",
        help="regenerate airframe/openscad/fuselage/cargo/cargo_layout_t5_params.scad",
    )
    a = ap.parse_args()
    if a.option == 1:
        # Option 1 envelope (trade record only): O20 body, worm PD 18 (C 29),
        # 43.2 + 6 mm long, 18 mm shaft, no brake.
        global MOTOR_D, WORM_PD, STAGE_C, WORM_Z, MOTOR_BODY_L, MOTOR_ENC_L, MOTOR_L
        MOTOR_D, WORM_PD = 20.0, 18.0
        STAGE_C = (WHEEL_PD + WORM_PD) / 2
        WORM_Z = SHAFT_Z + STAGE_C
        MOTOR_BODY_L, MOTOR_ENC_L = 43.2, 6.0
        MOTOR_L = MOTOR_BODY_L + MOTOR_ENC_L
        print("checking OPTION 1 envelope (20D, worm PD 18, C 29, single-start)")
    if a.write_scad:
        p = os.path.join(
            REPO, "airframe", "openscad", "fuselage", "cargo", "cargo_layout_t5_params.scad"
        )
        write_scad(p)
        print("wrote", os.path.relpath(p, REPO))
    # process=True merges the STL's duplicated vertices; without it manifold3d
    # rejects the shell as NotManifold and every intersection reads 0.
    shell_tm = trimesh.load(SHELL, process=True)
    assert shell_tm.is_watertight, "published cargo shell is not watertight"
    shell_tm = shell_after_merge(shell_tm)
    ok = report(layout_t5(), shell_tm, plot=a.plot)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
