#!/usr/bin/env python3
"""Serenity UAV -- bottom-up all-up-weight, CG, pitch inertia and hover T/W.

This is the single mass ledger the first-flight plan asks for (plan
2026-09-15-001 unit A0; root WBS MA-1 / MA-7).  Every installed item is one
row with a mass, a hull-frame station and the source of both:

* PRINTED parts are MEASURED: STL volume x RHO_PRINT (1.05e-3 g/mm^3, the
  audited as-printed bulk density of docs/MASS_AUDIT_CARGO_WING_ROOT.md SS1).
  Hull-frame (baked/generated) STLs give their own CG and inertia tensor;
  part-local STLs give mass only and take an ESTIMATED station.
* The two NACELLE rotating assemblies come from tools/nacelle_mass_cg_64.py
  (the 64 mm pod is the adopted nacelle), placed at the hull-frame tilt pivot
  that airframe/FreeCAD-scripts/serenity_assembly.py uses (pivot = nacelle CG
  by construction), with the tilt-axis inertia of
  docs/NACELLE_64MM_VERIFICATION.md SS5b.
* Every other row is a BOM row of current-specification/bom_revT.csv with its
  installed quantity and a station read from the layout tools
  (tools/cargo_layout_fit.py, tools/middle_layout_fit.py) where one exists.

The BOM mass column cannot be summed: it mixes installed parts, superseded
rows still at Qty > 0, kit/stock masses and tooling.  So every airborne BOM
row with Qty > 0 must appear exactly once below -- INSTALLED, NACELLE (counted
inside the nacelle roll-up) or EXCLUDED with its reason -- and the run FAILS
(exit 2) on any unclassified row.  That is the MA-7 "Installed" flag, kept
here beside the stations that need it rather than as a BOM column.

Rows with no BOM line at all (coverage gaps found while building this) are
listed as GAP rows with a stated estimate, and reported as their own subtotal.

Outputs: a table, three configurations (hover / cargo mission / heaviest),
CG, pitch radius of gyration about the CG, and hover T/W against the owner
thrust requirement of 2135 gf per fan [REF-EDF-003].  --write stores the
result in current-specification/auw_ledger.json, which
tools/landing_gear_r6_sizing.py reads; --check fails if that file is stale.

Method: rigid-body mass properties -- parallel-axis theorem for the pitch
moment of inertia [REF-NCEES-009, "Dynamics", mass moment of inertia].

Run: /usr/bin/python3 tools/auw_ledger.py [--write | --check]

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding)
AI note : Written by Claude (Claude Opus 5.5, Anthropic) under the author's
          direction, 2026-10-19, per AGENTS.md AI attribution.
License : MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import cargo_layout_fit as clf  # noqa: E402  (sibling tool, path set above)
import middle_layout_fit as mlf  # noqa: E402
import nacelle_mass_cg_64 as nac64  # noqa: E402

BOM = REPO / "current-specification" / "bom_revT.csv"
OUT_JSON = REPO / "current-specification" / "auw_ledger.json"
STL = REPO / "airframe" / "stls"

RHO_PRINT = 1.05e-3       # g/mm^3, MASS_AUDIT SS1 (bulk, 4 perimeters + >=40 %)
LBM_PER_G = 1.0 / 453.592
X_CL = clf.X_CL

# Hull-frame tilt pivot, serenity_assembly.py nacelle_pivot_hull() for the
# 64 mm pod (local (0, 0, PIVOT_Z 109.7) through R_BAKE/T_BAKE): port
# (60.54, 21.0, 66.851), stbd (-399.02, 21.0, 66.851).  Y/Z equal the wing spar
# (merge_cargo_interior.py WING_SPAR_Y 21.00, cargo_bulkhead_context SPAR_Z).
import bake_hull_frame as bhf  # noqa: E402  pivot X from the bake table
import hull_datums as hd  # noqa: E402  aircraft datum R2 (2026-10-19)
PIVOT = {s: (bhf.COMPONENTS[f"Nacelle64_{s.capitalize()}"][1][0], hd.SPAR_Y, hd.SPAR_Z)
         for s in ("port", "stbd")}
# Nacelle tilt-axis inertia about its own CG (= pivot), 64 mm, adopted:
# docs/NACELLE_64MM_VERIFICATION.md SS5b (tools/nacelle_tilt_dynamics.py).
I_NACELLE_KGM2 = 2.74e-3

# Thrust requirement per fan, owner (WBS NAC-64-ESC-80A.m): 2135 gf, which is
# the QF2822-2400KV row at 22.2 V of the QX manual sheet [REF-EDF-003].
THRUST_PER_FAN_GF = 2135.0
N_FANS = 4
PAYLOAD_G = 226.8         # 8.0 oz mission payload, README.md "Payload capacity"
T_W_FLOOR = 1.2           # WA-R18 hover floor; owner D4 still to confirm one number

SPOOL_Z = clf.SPOOL_Z0 + 10.0
NODE_POUCH_G = 5.0        # foil pouch per node, middle_layout_fit.py convention

# Node stations (hull frame, centre of each node envelope).
NODE_ST = {
    "A": ((X_CL, 45.7, 200.0), "ESTIMATE: Bay A, head sta 0-91 mm "
          "(docs/AVIONICS_PB2_REDESIGN.md) -> hull Y -305.7..-214.7"),
    "chin": ((X_CL, 0.5 * (clf.N_CHIN_Y0 + clf.N_CHIN_Y1),
              0.5 * (clf.N_CHIN_Z0 + clf.N_CHIN_Z1)),
             "cargo_layout_fit N_CHIN_* (CN2/CN3)"),
    "aft": ((X_CL, clf.N_AFT_Y0 + clf.NODE_T / 2, clf.N_AFT_Z0 + clf.NODE_L / 2 * 0.64),
            "cargo_layout_fit N_AFT_* (FC2/FC3)"),
    "simon": ((mlf.SIMON_XC, 0.5 * (mlf.SIMON_Y0 + mlf.SIMON_Y1), mlf.SIMON_ZC),
              "middle_layout_fit SIMON_* (CN4/FC4)"),
}
FE_ST = ((mlf.FE_XC, mlf.FE_FOOT_YC, mlf.FE_ZC), "middle_layout_fit FE_CAN_*")
BATT_ST = ((clf.BATT_XC, clf.BATT_Y0 + clf.BATT_L / 2,
            0.5 * (clf.BATT_Z0 + clf.BATT_Z1)), "cargo_layout_fit BATT_*")
WINCH_ST = ((X_CL, clf.HOIST_Y, SPOOL_Z), "cargo_layout_fit HOIST_Y / SPOOL_Z0")
PAYLOAD_ST = ((X_CL, clf.HOIST_Y, clf.DOOR_CROWN_Z + 38.1),
              "cargo_layout_fit HOIST_Y, payload box on the closed-door crown")
TILT_ST = {"port": ((45.85, 353.3, 181.0), "tilt bracket centroid (placed STL)"),
           "stbd": ((-45.15, 353.3, 181.0), "tilt bracket centroid (placed STL)")}  # R2
SHAFT_ST = ((X_CL, clf.SHAFT_Y, clf.SHAFT_Z), "cargo_layout_fit SHAFT_Y/Z")
SPAR_ST = ((X_CL, hd.SPAR_Y, hd.SPAR_Z), "wing spar station, both sides (sym)")
DOOR_ST = ((X_CL, 360.7, 88.0), "clamshell door aperture Y 2..108")
GW_DOOR_ST = ((X_CL, 305.7, 90.0), "ESTIMATE: fwd belly slab (CARGO_DOOR_GATEWAY_SPEC)")
WIRE_ST = ((X_CL, 395.7, 160.0), "ESTIMATE: battery (Y 13) -> FE (Y 162) -> nacelles")
KEEL_ST = ((X_CL, 345.7, 82.0), "ESTIMATE: keel bar mid-length")
NAV_POST_F = ((X_CL, 155.7, 285.0), "ESTIMATE: fwd 49 MHz post, head dorsal")
NAV_POST_A = ((X_CL, 685.7, 240.0), "ESTIMATE: aft post, rear nozzle top")

# ---------------------------------------------------------------------------
# Printed parts.  (BOM ref, STL, qty, placement)
#   "hull"      the STL is hull-frame -- CG and inertia from the mesh
#   ("st", P)   part-local STL -- mass from the mesh, station P (ESTIMATE)
#   ("mirror",) hull-frame port STL, starboard = mirror about X_CL
# ---------------------------------------------------------------------------
PRINTED = [
    ("PRINT-HEAD-SHELL", "fuselage/head_shell24_2mm_repaired.stl", 1, "hull"),
    ("PRINT-CARGO-SECT", "fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl", 1, "hull"),
    ("PRINT-MIDDLE-CANONICAL", "fuselage/middle_shell24_2mm_repaired.stl", 1, "hull"),
    ("PRINT-REAR-NECK-INTAKE", "fuselage/rear_shell24_2mm_repaired.stl", 1, "hull"),
    ("PRINT-HEAD-CARGO-COLLAR", "fuselage/head_cargo_splice_collar.stl", 1, "hull"),
    ("PRINT-CARGO-MIDDLE-COLLAR", "fuselage/cargo_middle_splice_collar.stl", 1, "hull"),
    ("PRINT-MIDDLE-REAR-COLLAR", "fuselage/middle_rear_splice_collar.stl", 1, "hull"),
    ("PRINT-WINGS-S1223", "wings/wing_port_s1223_revo.stl", 1, "hull"),
    ("PRINT-WINGS-S1223", "wings/wing_stbd_s1223_revo.stl", 1, "hull"),
    ("PRINT-WING-ROOT-FLANGE", "fuselage/wing_root_flange_port.stl", 1, "hull"),
    ("PRINT-WING-ROOT-FLANGE", "fuselage/wing_root_flange_stbd.stl", 1, "hull"),
    ("PRINT-CARGO-DOOR-PORT", "fuselage/cargo/cargo_door_port.stl", 1, "hull"),
    ("PRINT-CARGO-DOOR-STBD", "fuselage/cargo/cargo_door_stbd.stl", 1, "hull"),
    ("(hinge retention, merged-in part)", "fuselage/cargo/cargo_hinge_retention.stl", 1, "hull"),
    ("PRINT-TILT-BRACKET", "fuselage/cargo/tilt_actuator_bracket_port.stl", 1, "hull"),
    ("PRINT-TILT-BRACKET", "fuselage/cargo/tilt_actuator_bracket_stbd.stl", 1, "hull"),
    ("PRINT-TILT-WORM", "fuselage/cargo/tilt_actuator_worm.stl", 1, "hull"),
    ("PRINT-TILT-WORM", "fuselage/cargo/tilt_actuator_worm.stl", 1, ("dx", -89.2)),
    ("PRINT-TILT-WHEEL", "fuselage/cargo/tilt_actuator_wheel.stl", 1, "hull"),
    ("PRINT-TILT-WHEEL", "fuselage/cargo/tilt_actuator_wheel.stl", 1, ("dx", -89.2)),
    ("PRINT-TILT-BRAKE-GUIDE", "fuselage/cargo/tilt_brake_guide.stl", 1, "hull"),
    ("PRINT-TILT-BRAKE-GUIDE", "fuselage/cargo/tilt_brake_guide_stbd.stl", 1, "hull"),
    ("(wing tilt pinion)", "wings/wing_tilt_pinion_port.stl", 1, "hull"),
    ("(wing tilt pinion)", "wings/wing_tilt_pinion_stbd.stl", 1, "hull"),
    ("PRINT-BATT-CRADLE", "fuselage/cargo/battery_cradle.stl", 1, "hull"),
    ("PRINT-CHIN-SHELF", "fuselage/cargo/chin_node_shelf.stl", 1, "hull"),
    # The INSTALLED (baked, aircraft-frame) bay meshes, not the *_print.stl bed
    # copies: those are part-local, so measuring them "hull" put all four bays at
    # the datum origin (CG Y -4.8 mm in R2; also wrong, by less, in R1).
    ("PRINT-LG-BAY-PLATE", "fuselage/landing-gear/lg_r6_3_0in_bay_fore-port.stl", 1, "hull"),
    ("PRINT-LG-BAY-PLATE", "fuselage/landing-gear/lg_r6_3_0in_bay_fore-stbd.stl", 1, "hull"),
    ("PRINT-LG-BAY-PLATE", "fuselage/landing-gear/lg_r6_3_0in_bay_aft-port.stl", 1, "hull"),
    ("PRINT-LG-BAY-PLATE", "fuselage/landing-gear/lg_r6_3_0in_bay_aft-stbd.stl", 1, "hull"),
    # Leg frames and feet: part-local; placed midway hip->foot / at the foot.
    ("PRINT-LG-LEG-FRAME-3.0IN", "fuselage/landing-gear/lg_r6_3_0in_leg_frame.stl", 2,
     ("st", (X_CL, 274.7, 80.0), "ESTIMATE: fore legs, midway hip Y -16 -> foot Y -46.5")),
    ("PRINT-LG-LEG-FRAME-3.0IN", "fuselage/landing-gear/lg_r6_3_0in_leg_frame.stl", 2,
     ("st", (X_CL, 422.7, 80.0), "ESTIMATE: aft legs, midway hip Y 100 -> foot Y 135")),
    ("PRINT-LG-FOOT", "fuselage/landing-gear/lg_r6_common_foot.stl", 2,
     ("st", (X_CL, 259.2, 2.0), "foot station Y_FOOT_FORE (landing_gear_r6_sizing)")),
    ("PRINT-LG-FOOT", "fuselage/landing-gear/lg_r6_common_foot.stl", 2,
     ("st", (X_CL, 440.7, 2.0), "foot station Y_FOOT_AFT (landing_gear_r6_sizing)")),
    ("PRINT-GPS-RETENTION", "fuselage/cargo/cargo_gps_retention_ring.stl", 1,
     ("st", (X_CL, 415.7, 225.0), "ESTIMATE: GPS cups Z >= 139 over the aft strip")),
    ("PRINT-FPV-BEZEL", "fuselage/cargo/cargo_fpv_bezel.stl", 1,
     ("st", (X_CL, 245.7, 140.0), "ESTIMATE: forward cargo")),
    ("PRINT-CARGO-DOOR-SERVO-BKT", "fuselage/cargo/cargo_door_servo_bracket.stl", 1,
     ("st", DOOR_ST[0], "ESTIMATE: " + DOOR_ST[1])),
    ("PRINT-CARGO-RELEASE-BKT", "fuselage/cargo/cargo_release_servo_bracket.stl", 1,
     ("st", (X_CL, clf.HOIST_Y, hd.BELLY_Z + 120.0), "ESTIMATE: release at the hoist")),  # R1 Z 120
    ("PRINT-GW-DOOR-TRAY", "fuselage/cargo/gateway_door_tray.stl", 1,
     ("st", GW_DOOR_ST[0], GW_DOOR_ST[1])),
    # DOOR-REWORK (2026-10-26): brackets and cranks are rendered at their installed
    # position (aircraft frame, FRAME_MARKER), so they are measured, not estimated.
    ("PRINT-DOOR-LATCH-BRACKET", "fuselage/cargo/door_latch_bracket_port.stl", 1, "hull"),
    ("PRINT-DOOR-LATCH-BRACKET", "fuselage/cargo/door_latch_bracket_stbd.stl", 1, "hull"),
    ("PRINT-DOOR-LATCH-CRANK", "fuselage/cargo/door_latch_crank_port.stl", 1, "hull"),
    ("PRINT-DOOR-LATCH-CRANK", "fuselage/cargo/door_latch_crank_stbd.stl", 1, "hull"),
    ("PRINT-DOOR-HORN", "fuselage/cargo/door_horn.stl", 2,
     ("st", DOOR_ST[0], DOOR_ST[1])),
    ("PRINT-DORSAL-ANTENNA-FIN", "fuselage/dorsal_antenna_fin.stl", 1,
     ("st", (X_CL, 305.7, 250.0), "ESTIMATE: dorsal, cargo")),
]

# Non-printed installed rows: ref -> (qty, station, source).  A station of
# "pivot" splits the quantity evenly across both nacelle pivots.
INSTALLED = {
    "SERVO-CARGO": (3, DOOR_ST),
    "CAN-PERIPH-GW-DOOR": (1, GW_DOOR_ST),
    "PIN-3X18": (16, "pivot"),     # nozzle flap pins; not in the 64 mm roll-up
    "PIN-2X4": (16, "pivot"),
    "PB2-I-FC": (4, "nodes"),
    "PB2-I-CN": (4, "nodes"),
    "Pilot": (4, "nodes"),
    "TACCO": (4, "nodes"),
    "Commo": (2, ((X_CL, 355.7, 180.0), "ESTIMATE: Commo sub-modules, cargo")),
    "MICROSD-LOG": (4, "nodes"),
    "WIRE-49MHZ": (1, ((X_CL, 345.7, 252.0), "ESTIMATE: dorsal spine mid-length")),
    "POST-FWD-49": (1, NAV_POST_F),
    "POST-AFT-49": (1, NAV_POST_A),
    "Flight Engineer": (1, FE_ST),
    "FUSE-MAIN-150A": (1, FE_ST),
    "FUSE-ESC-40A": (4, FE_ST),
    "SHUNT-1MOHM": (5, FE_ST),
    "SPT5425LV-WINCH-LS2": (1, WINCH_ST),
    "SOL-CATCH-5V": (1, WINCH_ST),
    "BRG-MR84ZZ": (2, WINCH_ST),
    "SHAFT-SS-4MM": (1, WINCH_ST),
    "SPRING-PAWL": (1, WINCH_ST),
    "DOWEL-M2-10": (1, WINCH_ST),
    "SLEEVE-HUB-STEEL": (1, WINCH_ST),
    "CLIP-EXT-4MM": (2, WINCH_ST),
    "KEEPER-WINCH": (1, WINCH_ST),
    "PLATE-PEDESTAL": (2, WINCH_ST),
    "ENC-AK7455-SPOOL": (1, WINCH_ST),
    "FET-AO3400": (1, WINCH_ST),
    "DIODE-SS34": (1, WINCH_ST),
    "HX711-LC": (1, WINCH_ST),
    "DYNEEMA-SK75": (1, WINCH_ST),
    "PRINT-CARGO-WINCH-PEDESTAL-PORT": (1, WINCH_ST),   # no STL in tree: BOM mass
    "PRINT-CARGO-WINCH-PEDESTAL-STBD": (1, WINCH_ST),
    "PRINT-CARGO-WINCH-SPOOL-R2": (1, WINCH_ST),
    "PRINT-CARGO-WINCH-PAWL": (1, WINCH_ST),
    "PRINT-CARGO-WINCH-DOG-COUPLER": (1, WINCH_ST),
    "PRINT-CARGO-WINCH-FAIRLEAD": (1, WINCH_ST),
    "PRINT-NODE-SADDLE": (2, NODE_ST["aft"]),           # SCAD only, no STL yet
    "PRINT-HALL-HUB": (2, "pivot"),                     # no STL in tree: BOM mass
    "FOAM-GASKET-CARGO": (1, DOOR_ST),
    "PIN-3X10": (2, DOOR_ST),
    "CF-BAR-6X3": (1, KEEL_ST),
    "WIRE-6AWG": (1, WIRE_ST),
    "WIRE-10AWG": (1, WIRE_ST),
    "WIRE-28AWG-STP": (1, ((X_CL, 345.7, 170.0), "ESTIMATE: full-length signal run")),
    "CONDUIT-PTFE": (1, ((X_CL, 345.7, 170.0), "ESTIMATE: full-hull-length conduit")),
    "LED-WS2812C-NAC": (4, "pivot"),
    "INSERT-M3-WING": (8, SPAR_ST),
    "LG-SPRING-WIRE": (8, ((X_CL, 355.7, 110.0), "gear bays, 4 corners (sym)")),
    "LG-DUCTILE-WIRE": (8, ((X_CL, 355.7, 110.0), "gear bays, 4 corners (sym)")),
    "LG-HARDWARE-MISC": (1, ((X_CL, 355.7, 110.0), "gear bays, 4 corners (sym)")),
    "LG-SAFETY-CORD": (4, ((X_CL, 355.7, 80.0), "gear, 4 corners (sym)")),
    "BATT-STRAP-CAM": (2, BATT_ST),
    "BATT-FOAM-SILICONE": (1, BATT_ST),
    "MESH-VENT-SS": (1, BATT_ST),
    "FAR-BOND-STRAP": (4, "nodes"),                     # one per node-stack pouch
    "FAR-FERRITE-4MM": (16, ((X_CL, 365.7, 170.0), "ESTIMATE: cable exits, all nodes")),
    "SKIPPER-TILT-ENC-PCB": (2, "pivot"),
    "HALL-SCR-M2-BRASS": (8, "pivot"),
    "GM-TILT-20D": (2, "tilt"),
    "OSESC-TILT-TC": (2, "tilt"),
    "SOL-TILT-BRAKE": (2, "tilt"),
    "PIN-2X22": (2, "tilt"),
    "FUSE-TILT-3A": (2, "tilt"),
    "MAG-6X2.5-DIA": (2, "tilt"),
    "SPAR-CF-20X16": (2, SPAR_ST),
    "SHAFT-TILT-4MM": (2, SHAFT_ST),
    "BUSH-TILT-4MM": (4, SHAFT_ST),
    "GEAR-TILT-FUS-38T": (4, SHAFT_ST),
    "STUD-M3-BRASS": (8, "pivot"),
    "SCREW-M3-BUTTON-8": (24, "pivot"),
    "MESH-FOD-NOSEEUM": (4, "pivot"),
}

# BOM mass overrides with the measurement behind them.
MASS_OVERRIDE = {
    "FOAM-PU-2LB": (22.0, "installed foam, MASS_AUDIT SS4.2 (MA-3); BOM carries the kit"),
}
INSTALLED["FOAM-PU-2LB"] = (1, ((X_CL, 305.7, 180.0), "ESTIMATE: chin/head/flank pours"))

# Counted inside tools/nacelle_mass_cg_64.py's rotating assembly.
NACELLE = {
    "EDF-50-6S": "64 mm QF2822 motors + rotors are in the nacelle roll-up",
    "ESC-40A-6S": "70 A ESCs are in the nacelle roll-up",
    "PRINT-NACELLE-PORT": "64 mm pod shell measured in the nacelle roll-up",
    "PRINT-NACELLE-STBD": "64 mm pod shell measured in the nacelle roll-up",
    "PRINT-NACELLE-FLAP-MASTER": "nozzle flaps (scaled) in the nacelle roll-up",
    "PRINT-NACELLE-FLAP-SEAL": "nozzle flaps (scaled) in the nacelle roll-up",
    "PRINT-NACELLE-THROAT": "throat + housing in the nacelle roll-up",
    "PRINT-NACELLE-RING": "unison ring in the nacelle roll-up",
    "PRINT-NACELLE-ESC-COVER": "4 x ESC covers in the nacelle roll-up",
    "PRINT-NACELLE-TRUNNION": "64 mm trunnion (measured) in the nacelle roll-up",
    "BRG-6704ZZ": "2 x 6804-ZZ per nacelle in the nacelle roll-up",
    "WIRE-16AWG": "phase leads (14 AWG) in the nacelle roll-up",
    "WIRE-28AWG-NAC": "nav 3-core in the nacelle roll-up",
    "HALL-RING-MAG": "ring magnet on the tilt axis in the nacelle roll-up",
}

EXCLUDED = {
    "CF-PLATE-2MM": "procurement sheet mass; installed thwarts + ring are GAP-style rows "
                    "(CF_PLATE_PARTS)",
    "BATT-6S-2800": "alternate pack; the configurations pick ONE battery",
    "BATT-6S-4000": "the configurations pick ONE battery",
    "BRG-MF104ZZ": "50 mm pivot bearing, superseded by the trunnion (Rev T4)",
    "CF-ROD-4MM": "50 mm pivot rod, superseded by the trunnion (Rev T4)",
    "SPAR-TILT-CF4": "rotating tilt spar, superseded by the fixed CF spar (Rev T1)",
    "SPAR-TILT-4130": "rotating 4130 spar, retired Rev S1g (MASS_AUDIT SS7)",
    "BRG-F688ZZ": "rotating-spar bearing, retired Rev S1g (MASS_AUDIT SS7)",
    "CF-TUBE-12MM": "12 mm spar tube, superseded by SPAR-CF-20X16 (Rev T1)",
    "PRINT-PYLON": "Rev O pylon, superseded by the Rev T1 fixed spar + trunnion; "
                   "no source in tree",
    "PRINT-NECK-INTAKE-FRAME": "Phase 11 rear-EDF intake (deferred/aft-edf)",
    "PRINT-PUSHROD-CRANK": "Option B nozzle crank, retired Rev S1g (MASS_AUDIT SS7)",
    "PUSHROD-BALL-M3": "Option B nozzle pushrod, superseded by the KST X06 servo drive",
    "BALLSTUD-M3": "Option B nozzle pushrod, superseded by the KST X06 servo drive",
    "PRINT-NACELLE-IDLER": "50 mm gear-train nozzle drive, deleted (build-guide A9)",
    "PRINT-NACELLE-IDLER-BKT": "50 mm gear-train nozzle drive, deleted",
    "SECTOR-M1-R22": "tilt gear train, deleted (trunnion + worm drive)",
    "PINION-A-M1-12T": "tilt gear train, deleted",
    "BEVEL-M1-14T": "tilt gear train, deleted",
    "CROWN-M1-12T": "nozzle gear train, deleted",
    "BEVEL-HOUSING": "tilt gear train, deleted",
    "SHAFT-CF-3MM": "gear-train shafts, deleted",
    "BRG-MR63ZZ": "gear-train bearings, deleted",
    "PTFE-SLEEVE-4MM": "gear-train shaft sleeve, deleted",
    "INSERT-M25-BRASS": "sector-gear mount inserts, deleted with the gear train",
    "PRINT-VOID-FORMER-CARGO": "PLA foam-pour tooling, removed after cure",
}

# CF-PLATE-2MM installed parts (docs/structural_analysis.md SS5.6: the cargo Y +30
# ring retired 2026-08-25 for two thwarts, fore Y -40 / aft Y +118, 2 x 25 mm
# (tools/wing_spar_carrythrough.py THWART_T/H) across ~170 mm; the rear Y +290
# ring stays, ~10 mm band on the 397 mm inner profile).  CF laminate 1.6e-3
# g/mm^3 ESTIMATE.  The BOM row carries two whole 200 x 300 sheets (114 g).
RHO_CF = 1.6e-3
CF_PLATE_PARTS = [
    ("CF thwart fore (CF-PLATE-2MM)", 2.0 * 25.0 * 170.0 * RHO_CF, ((X_CL, 265.7, 160.0),
     "structural_analysis SS5.6, thwart Y -40")),
    ("CF thwart aft (CF-PLATE-2MM)", 2.0 * 25.0 * 170.0 * RHO_CF, ((X_CL, 423.7, 160.0),
     "structural_analysis SS5.6, thwart Y +118")),
    ("CF ring frame rear Y +290 (CF-PLATE-2MM)", 397.0 * 10.0 * 2.0 * RHO_CF,
     ((X_CL, 595.7, 162.0), "structural_analysis SS5.2, ~10 mm band ESTIMATE")),
]

# Coverage gaps: installed items with no BOM row.  Stated estimates.
GAPS = [
    ("Node foil pouches x8", 8 * NODE_POUCH_G, "nodes",
     "middle_layout_fit.py M_CN4/M_FC4 convention"),
    ("FE can (1.0 mm 6061) + entry plate + hardware",
     mlf.can_mass() + mlf.M_FE_PLATE + mlf.M_FE_HW, FE_ST,
     "middle_layout_fit.py can_mass(), M_FE_PLATE, M_FE_HW"),
    ("Cargo Observer node (vision/ToF/laser)", 60.0,
     ((X_CL, clf.OBSERVER_Y0 + clf.OBSERVER_T / 2, clf.OBSERVER_Z0 + clf.OBSERVER_W / 2),
      "cargo_layout_fit OBSERVER_*"),  # was a typed R1 Z 50 (below the R2 belly)
     "ESTIMATE 60 g -- no BOM row; envelope 76.8 x 70.8 x 20 mm"),
    ("CAN-PERIPH-GW-1 gateways x2 (winch, tilt encoders)", 12.0, WINCH_ST,
     "ESTIMATE 6 g each, as CAN-PERIPH-GW-DOOR -- no BOM rows"),
    ("Structural epoxy (West System 105/206 + 406), bonded joints", 40.0,
     ((X_CL, 345.7, 160.0), "ESTIMATE: spar sockets, flanges, collars, keel"),
     "ESTIMATE -- no installed-mass row (kit row is stock)"),
]

AIRBORNE_SKIP_CATEGORIES = {"GCS", "Filament"}


def load(rel: str) -> trimesh.Trimesh:
    path = STL / rel
    if not path.exists():
        sys.exit(f"[auw_ledger] missing STL {path}")
    return trimesh.load_mesh(path, force="mesh", process=True)


def bom_rows() -> dict[str, dict]:
    with open(BOM, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = {}
    for r in rows:
        if r["Category"] in AIRBORNE_SKIP_CATEGORIES:
            continue
        try:
            qty = float(r["Qty"] or 0)
        except ValueError:
            qty = 0.0
        if qty <= 0:
            continue
        out.setdefault(r["Ref"], r)
    return out


class Item:
    """One ledger row: mass g, CG (x, y, z) mm, own inertia tensor g.mm^2."""

    def __init__(self, name, ref, m, cg, inertia=None, src="", kind="BOM"):
        self.name, self.ref, self.m = name, ref, float(m)
        self.cg = np.asarray(cg, dtype=float)
        self.i = np.zeros((3, 3)) if inertia is None else np.asarray(inertia, float)
        self.src, self.kind = src, kind


def printed_items() -> list[Item]:
    items = []
    for ref, rel, qty, place in PRINTED:
        mesh = load(rel)
        m1 = float(mesh.volume) * RHO_PRINT
        if place == "hull" or (isinstance(place, tuple) and place[0] == "dx"):
            cg = np.array(mesh.center_mass, float)
            inertia = np.array(mesh.moment_inertia, float) * RHO_PRINT
            src = "MEASURED mesh (hull frame)"
            if isinstance(place, tuple):
                cg = cg + np.array([place[1], 0.0, 0.0])
                src = f"MEASURED mesh, starboard copy translated dX {place[1]} " \
                      "(serenity_assembly.py T5_STBD_DX)"
        else:
            cg, inertia, src = np.array(place[1], float), None, \
                f"MEASURED mass; station {place[2]}"
        items.append(Item(Path(rel).stem, ref, m1 * qty, cg, None if inertia is None
                          else inertia * qty, src, "PRINT"))
    return items


def nacelle_items() -> list[Item]:
    items = []
    pod = REPO / "airframe/stls/nacelles/nacelle_stbd_64mm.stl"
    total = nac64.roll_up(pod)["total_g"]
    i_own = I_NACELLE_KGM2 * 1e9                       # g.mm^2, tilt (X) axis
    for side, p in PIVOT.items():
        inertia = np.diag([i_own, i_own, i_own])       # pitch term is the one used
        items.append(Item(f"Nacelle {side} rotating assembly (64 mm)", "NACELLE",
                          total, p, inertia,
                          "tools/nacelle_mass_cg_64.py roll-up at the hull pivot",
                          "NACELLE"))
    return items


def station_items(bom: dict[str, dict]) -> list[Item]:
    items = []
    for ref, (qty, st) in INSTALLED.items():
        row = bom.get(ref)
        if row is None:
            continue
        unit = MASS_OVERRIDE.get(ref, (float(row["Unit_Mass_g"] or 0), ""))[0]
        msrc = MASS_OVERRIDE.get(ref, (0, "BOM Unit_Mass_g"))[1]
        if st == "pivot":
            for side, p in PIVOT.items():
                items.append(Item(f"{ref} ({side})", ref, unit * qty / 2, p, None,
                                  f"{msrc}; at the {side} nacelle pivot", "BOM"))
        elif st == "tilt":
            for side, (p, s) in TILT_ST.items():
                items.append(Item(f"{ref} ({side})", ref, unit * qty / 2, p, None,
                                  f"{msrc}; {s}", "BOM"))
        elif st == "nodes":
            for site, (p, s) in NODE_ST.items():
                items.append(Item(f"{ref} (node {site})", ref, unit * qty / 4, p,
                                  None, f"{msrc}; {s}", "BOM"))
        else:
            p, s = st
            items.append(Item(ref, ref, unit * qty, p, None, f"{msrc}; {s}", "BOM"))
    return items


def gap_items() -> list[Item]:
    items = [Item(n, "CF-PLATE-2MM", m, st[0], None, f"ESTIMATE; {st[1]}", "BOM")
             for n, m, st in CF_PLATE_PARTS]
    for name, m, st, src in GAPS:
        if st == "nodes":
            for site, (p, _s) in NODE_ST.items():
                items.append(Item(f"{name} (node {site})", "GAP", m / 4, p, None,
                                  src, "GAP"))
        else:
            items.append(Item(name, "GAP", m, st[0], None, f"{src}; {st[1]}", "GAP"))
    return items


def classify(bom: dict[str, dict]) -> list[str]:
    """Every airborne BOM row must be accounted for exactly once."""
    printed_refs = {p[0] for p in PRINTED}
    known = printed_refs | set(INSTALLED) | set(NACELLE) | set(EXCLUDED)
    return sorted(r for r in bom if r not in known)


def properties(items: list[Item]) -> dict:
    m = sum(i.m for i in items)
    cg = sum(i.m * i.cg for i in items) / m
    i_cg = np.zeros((3, 3))
    for it in items:
        d = it.cg - cg
        i_cg += it.i + it.m * (np.dot(d, d) * np.eye(3) - np.outer(d, d))
    ixx = i_cg[0, 0]                               # pitch: about hull X (lateral)
    return {"mass_g": m, "cg": cg.tolist(), "I_pitch_gmm2": float(ixx),
            "k_pitch_mm": math.sqrt(ixx / m)}


def battery_item(ref: str, bom: dict[str, dict]) -> Item:
    row = bom[ref]
    m = float(row["Unit_Mass_g"])
    (x, y, z), s = BATT_ST
    l, w, h = clf.BATT_L, clf.BATT_W, clf.BATT_H
    inertia = m / 12.0 * np.diag([l * l + h * h, w * w + h * h, w * w + l * l])
    return Item(ref, ref, m, (x, y, z), inertia, f"BOM; {s}; solid box", "BOM")


def build() -> dict:
    bom = bom_rows()
    missing = classify(bom)
    base = printed_items() + nacelle_items() + station_items(bom) + gap_items()
    payload = Item("Mission payload 8 oz", "PAYLOAD", PAYLOAD_G, PAYLOAD_ST[0], None,
                   PAYLOAD_ST[1], "PAYLOAD")
    configs = {
        "hover_4000": base + [battery_item("BATT-6S-4000", bom)],
        "cargo_2800_payload": base + [battery_item("BATT-6S-2800", bom), payload],
        "heaviest_4000_payload": base + [battery_item("BATT-6S-4000", bom), payload],
    }
    thrust = THRUST_PER_FAN_GF * N_FANS
    result = {"unclassified": missing, "thrust_gf": thrust, "configs": {}}
    for name, items in configs.items():
        p = properties(items)
        p["T_W"] = thrust / p["mass_g"]
        result["configs"][name] = p
    by_kind = {}
    for it in configs["hover_4000"]:
        by_kind[it.kind] = by_kind.get(it.kind, 0.0) + it.m
    result["subtotals_hover_g"] = by_kind
    result["rows_hover"] = [
        {"name": i.name, "ref": i.ref, "kind": i.kind, "mass_g": round(i.m, 2),
         "cg": [round(c, 1) for c in i.cg], "source": i.src}
        for i in configs["hover_4000"]]
    return result


def report(r: dict) -> None:
    print("Serenity UAV -- bottom-up AUW / CG / pitch inertia ledger")
    print(f"{'Item':52} {'g':>8} {'Y mm':>7} {'Z mm':>6}  source")
    for row in sorted(r["rows_hover"], key=lambda x: -x["mass_g"]):
        print(f"{row['name'][:52]:52} {row['mass_g']:8.1f} {row['cg'][1]:7.1f} "
              f"{row['cg'][2]:6.1f}  {row['source'][:70]}")
    print("\nSubtotals (hover config):")
    for k, v in sorted(r["subtotals_hover_g"].items(), key=lambda kv: -kv[1]):
        print(f"  {k:8} {v:8.1f} g  ({v * LBM_PER_G:5.2f} lbm)")
    print(f"\nThrust requirement: {N_FANS} x {THRUST_PER_FAN_GF:.0f} gf = "
          f"{r['thrust_gf']:.0f} gf ({r['thrust_gf'] * LBM_PER_G:.2f} lbf) [REF-EDF-003]")
    for name, p in r["configs"].items():
        x, y, z = p["cg"]
        print(f"  {name:24} AUW {p['mass_g']:7.0f} g ({p['mass_g'] * LBM_PER_G:5.2f} lbm)  "
              f"CG X {x:7.1f} Y {y:+6.1f} Z {z:5.1f} mm  k_pitch {p['k_pitch_mm']:5.1f} mm "
              f"({p['k_pitch_mm'] / 25.4:4.2f} in)  T/W {p['T_W']:.2f}"
              f"{'' if p['T_W'] >= T_W_FLOOR else '  ** BELOW ' + str(T_W_FLOOR) + ' **'}")
    print(f"  hover thrust line (tilt pivot) Y +{PIVOT['port'][1]:.1f} mm; "
          f"CG offset {r['configs']['hover_4000']['cg'][1] - PIVOT['port'][1]:+.1f} mm")
    if r["unclassified"]:
        print("\nUNCLASSIFIED airborne BOM rows (Qty > 0):")
        for ref in r["unclassified"]:
            print("  ", ref)


def strip(r: dict) -> dict:
    return {k: v for k, v in r.items() if k != "rows_hover"} | {
        "rows_hover": r["rows_hover"]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true", help=f"store {OUT_JSON.name}")
    g.add_argument("--check", action="store_true", help="fail if the stored file is stale")
    args = ap.parse_args(argv)
    os.chdir(REPO)
    r = build()
    report(r)
    if r["unclassified"]:
        print("\nRESULT: FAIL -- classify every airborne BOM row first")
        return 2
    text = json.dumps(strip(r), indent=1, sort_keys=True) + "\n"
    if args.write:
        OUT_JSON.write_text(text, encoding="utf-8")
        print(f"\nwrote {OUT_JSON.relative_to(REPO)}")
    elif args.check:
        if not OUT_JSON.exists() or OUT_JSON.read_text(encoding="utf-8") != text:
            print(f"\nRESULT: FAIL -- {OUT_JSON.relative_to(REPO)} is stale; run --write")
            return 2
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
