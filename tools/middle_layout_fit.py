#!/usr/bin/env python3
"""middle_layout_fit.py -- Rev T6 middle-section equipment layout and the
power / data harness corridors that connect it to the cargo section, proved
against the PUBLISHED shells.

What is placed (hull frame: X = +port, Y = +aft, Z = +dorsal)
------------------------------------------------------------
* Kaylee's room -- the Flight Engineer power-distribution board (PDB) in its
  shielded can, inside the middle section's inner neck.
* Simon's med bay -- the aft flight-control / comms node pair CN4 (XO cape)
  + FC4 (Pilot cape), pouch-wrapped, in the same neck aft of Kaylee.
* The ventral hatch that both are serviced through (the section joints are
  epoxy-bonded double-lap collars, so nothing comes out any other way).
* Three SMA bulkhead stations on the horseshoe crown for CN4's antennas.
* The harness corridors -- battery lead, ESC feeders, 5 V / 6 V buses, tilt
  feeds, bus backbone -- from Kaylee forward through the cargo/middle splice
  collar into the Rev T5e cargo layout (tools/cargo_layout_fit.py), which is
  imported here so the SAME envelopes gate both sections.

Why the layout looks the way it does (measured 2026-09-17, not assumed)
-----------------------------------------------------------------------
* The inner neck is a ~O125 bore (X -234..-106, Z 13..142) and the section is
  only 71 mm long; the two splice collars are 2 mm sleeves 8 mm deep at each
  end, so the free bore is Y 139..194 (55 mm) plus the sleeve zones.
* FlightEngineer.md's 115 x 95 x 55 enclosure cannot fit that bore in any
  orientation (diagonal 149 mm).  The 90 x 65 board does (diagonal 111).
  Portrait (65 wide x 90 tall) is chosen: the can is 75 x 96 and leaves
  25 mm cable trunks either side at mid-height instead of 12.5.
* The neck's floor and roof skins are directly exposed only at Y 132..147 and
  162..172 (ventral) / 132..147, 165..171, 186..202 (dorsal) -- the horseshoe
  legs double the skin at Y 148..160 and 174..184 -- so the hatch has to cut
  the leg skins too.  Between Y 160 and 176 the ring's hollow and the neck
  are ONE cavity: a foam pour would flood the neck (void former, SS VOID).
* Y budget: sleeve end 139 | Kaylee unit 36 (bushing plate 8 + can 28) | 2 |
  pouch pair 22 | to 200 (rear cone begins 203.6 and is Phase-11 reserved).
  That caps Kaylee's component height at 16 mm above the board -- an ICD
  requirement on the pending Flight Engineer PCB respin (FlightEngineer.md
  SS Rev T6 mechanical ICD), not something this tool can relax.
* Phase 11 turns the neck into the aft-EDF intake: the tool reports the free
  bore area at every station against the 3,090 mm^2 scoop capture figure
  (airframe/fuselage-mid/WBS.md SS1.1.1.3) so the scoop station can be
  chosen aft of Kaylee.

Run:
    /usr/bin/python3 tools/middle_layout_fit.py              # report
    /usr/bin/python3 tools/middle_layout_fit.py --plot       # + section PNGs
    /usr/bin/python3 tools/middle_layout_fit.py --write-scad # params include

Use `/usr/bin/python3`: the repository `.venv` hides the system `trimesh`,
`shapely` and `manifold3d`, and `pip` is not permitted in this environment.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the
author's direction, 2026-09-17, per `AGENTS.md` SS3 AI attribution.
License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
"""

import argparse
import os
import sys

import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import cargo_layout_fit as cargo  # noqa: E402  (single-source cargo envelopes)

from cargo_layout_fit import GAP_MM, X_CL, box, cyl, dilate, mirror_x, to_man  # noqa: E402

MIDDLE_SHELL = os.path.join(REPO, "airframe", "stls", "fuselage", "middle_shell24_2mm_repaired.stl")
FLANGE_PORT = os.path.join(REPO, "airframe", "stls", "fuselage", "wing_root_flange_port.stl")
FLANGE_STBD = os.path.join(REPO, "airframe", "stls", "fuselage", "wing_root_flange_stbd.stl")
LG_LEGS = os.path.join(
    REPO, "airframe", "stls", "fuselage", "landing-gear", "lg_r6_1_5in_hull_legs.stl"
)
STATIC_GAP = 2.0  # static part against the fixed hull (cargo_layout_fit convention)

# ---------------------------------------------------------------------------
# Middle section datum (measured from the baked shell, 2026-09-17)
# ---------------------------------------------------------------------------
MID_Y0, MID_Y1 = 130.4, 203.6  # section faces (HULL_FRAME_REFERENCE.md)
NECK_ZC = 77.8  # bore centre Z at Y 140 (drifts to ~80.5 by Y 198)
NECK_R = 62.5  # nominal bore radius (129 x 129.5 at Y 140; 120 x 125 at Y 198)
FWD_SLEEVE_Y1 = 139.0  # cargo/middle collar sleeve reaches Y 121..139
AFT_SLEEVE_Y0 = 194.3  # middle/rear collar sleeve reaches Y 194.3..212.3
REAR_RESERVED_Y = MID_Y1  # nothing of this layout may pass the rear face (Phase 11)

# ---------------------------------------------------------------------------
# Kaylee's room -- Flight Engineer PDB, Rev T6 can
# ---------------------------------------------------------------------------
# Board 90 x 65 (FlightEngineer.kicad_pcb Edge.Cuts), M3 holes on an 82 x 57
# pattern 4 mm in from each corner.  PORTRAIT in the bore: 65 along X, 90
# along Z; component side AFT (into the can), the forward face is the cable
# entry plate.  The Rev T6 can replaces the 115 x 95 x 55 box in
# FlightEngineer.md, which does not fit (see module docstring).
FE_BOARD_X, FE_BOARD_Z = 65.0, 90.0
FE_HOLE_DX, FE_HOLE_DZ = 57.0 / 2, 82.0 / 2  # +-28.5 x +-41 from the board centre
FE_CAN_X, FE_CAN_Z, FE_CAN_Y = 75.0, 94.0, 28.0  # external; 1.0 mm 6061-T6, R12 Y-parallel edges
FE_CAN_R = 12.0
FE_WALL = 1.0
FE_STANDOFF = 4.0
FE_PCB_T = 1.6
FE_COMP_MAX = 16.0  # ICD: tallest component above the board top face
FE_CLEAR = FE_CAN_Y - 2 * FE_WALL - FE_STANDOFF - FE_PCB_T - FE_COMP_MAX  # 3.4 mm to the lid
FE_PLATE_Y = 8.0  # EMC cable-entry plate + bushing protrusion, forward of the can
FE_UNIT_Y0 = FWD_SLEEVE_Y1 + 1.0  # 140.0 -- 1 mm clear of the bonded sleeve
FE_PLATE_Y0, FE_PLATE_Y1 = FE_UNIT_Y0, FE_UNIT_Y0 + FE_PLATE_Y  # 140..148
FE_CAN_Y0, FE_CAN_Y1 = FE_PLATE_Y1, FE_PLATE_Y1 + FE_CAN_Y  # 148..176
FE_XC = X_CL
FE_ZC = NECK_ZC + 1.0  # 78.8: lifted 1 mm so the bottom corners clear the floor skin
FE_CAN_Z0, FE_CAN_Z1 = FE_ZC - FE_CAN_Z / 2, FE_ZC + FE_CAN_Z / 2  # 30.8..126.8
FE_CAN_X0, FE_CAN_X1 = FE_XC - FE_CAN_X / 2, FE_XC + FE_CAN_X / 2
# plate footprint = board + 2 mm each side; bushings only inside this
FE_PLATE_X, FE_PLATE_Z = FE_BOARD_X + 4.0, FE_BOARD_Z + 4.0
# Can-to-cover mounting: 4 x M3 inserts in the can floor (its -Z face), on a
# 56 x 20 pattern so the cover's pillars land on the flat of the skin patch.
FE_FOOT_DX, FE_FOOT_DY = 28.0, 10.0
FE_FOOT_YC = (FE_CAN_Y0 + FE_CAN_Y1) / 2  # 162.0

# ---------------------------------------------------------------------------
# Simon's med bay -- CN4 (XO) + FC4 (Pilot), pouch-wrapped, stacked
# ---------------------------------------------------------------------------
# Same node envelope as the cargo pairs (cargo_layout_fit.NODE_*): PB2I +
# cape in a foil pouch, 58 x 37 x 22 (stack height VERIFY at first article),
# 10 mm cable zone on the connector edge.  Standing transverse, board plane
# X-Z, stacked in Z: CN4 low, FC4 high (FC4 is the bus-end terminator; its
# cape carries the 120 ohm / 78 ohm terminations).  Cable zones both to PORT
# so one trunk serves both.
NODE_L, NODE_H, NODE_T, NODE_CABLE = cargo.NODE_L, cargo.NODE_H, cargo.NODE_T, cargo.NODE_CABLE
SIMON_Y0 = FE_CAN_Y1 + 2.0  # 178.0 (both static -> 2 mm, cargo convention)
SIMON_Y1 = SIMON_Y0 + NODE_T  # 200.0 < 203.6 rear face
SIMON_XC = X_CL
SIMON_ZC = 80.5  # aft-neck bore centre
SIMON_STACK_GAP = 3.0
SIMON_STACK_H = 2 * NODE_H + SIMON_STACK_GAP  # 77
SIMON_Z0 = SIMON_ZC - SIMON_STACK_H / 2  # 42.0
CN4_Z0, CN4_Z1 = SIMON_Z0, SIMON_Z0 + NODE_H  # 42..79
FC4_Z0, FC4_Z1 = CN4_Z1 + SIMON_STACK_GAP, CN4_Z1 + SIMON_STACK_GAP + NODE_H  # 82..119
SIMON_X0, SIMON_X1 = SIMON_XC - NODE_L / 2, SIMON_XC + NODE_L / 2  # -198.85..-140.85
SIMON_CABLE_X1 = SIMON_X1 + NODE_CABLE  # -130.85 (port cable zone)
# Saddle: floor-standing slotted block, 4 x M3 heat-set floor bosses
SADDLE_T = 2.4
SADDLE_BOSS = ((SIMON_XC - 22.0, 182.0), (SIMON_XC + 22.0, 182.0),
               (SIMON_XC - 22.0, 196.0), (SIMON_XC + 22.0, 196.0))  # (X, Y)

# ---------------------------------------------------------------------------
# Ventral hatch -- the ONLY service opening (joints are bonded)
# ---------------------------------------------------------------------------
# Cut footprint: can width + 4.5 mm each side, Y from 1 mm aft of the fwd
# sleeve to 1 mm aft of the can.  Everything of the shell below Z HATCH_ZCUT
# inside the footprint is removed (neck floor AND the horseshoe-leg skins it
# crosses); the cover is that skin patch re-printed with a lip and the
# Kaylee cradle on its inner face.  Simon's pouches slide forward into the
# hatch zone once Kaylee is lowered.
HATCH_X0, HATCH_X1 = FE_CAN_X0 - 4.5, FE_CAN_X1 + 4.5  # 84 wide
HATCH_Y0, HATCH_Y1 = FE_UNIT_Y0, FE_CAN_Y1 + 1.0  # 140..177
HATCH_ZCUT = 47.0  # above the bore wall at the cut's X edges (Z 31.5 at |dX| 42)
HATCH_LIP = 5.0  # cover shoulder lip riding on the OML
HATCH_SCREWS = ((HATCH_X0 - 4.0, 143.0), (HATCH_X0 - 4.0, 158.5), (HATCH_X0 - 4.0, 174.0),
                (HATCH_X1 + 4.0, 143.0), (HATCH_X1 + 4.0, 158.5), (HATCH_X1 + 4.0, 174.0))
# Hatch cut removes roughly 97 deg of the O125 tube over 37 mm: the cover is a
# structural doubler (SS LOAD open item, see the layout doc).

# ---------------------------------------------------------------------------
# SMA bulkheads for CN4 on the horseshoe crown (Y 168 is the highest skin of
# the section, Z ~166 at X_CL, and directly over the merged cavity so the
# coax drops straight to the pouch).  60 mm apart: SiK/LoRa need >= 50
# (AVIONICS_PB2_REDESIGN.md SS3.4 note).
# ---------------------------------------------------------------------------
SMA_Y = 168.0
SMA_XS = {"SMA-49 (Commo whip)": X_CL, "SMA-915-SIK": X_CL + 30.0, "SMA-WIFI": X_CL - 30.0}
SMA_BORE_D = 6.5

# ---------------------------------------------------------------------------
# Harness corridors (envelopes the cables must live inside).  Port side
# given, 'mirror' makes the starboard twin.  Cable ODs: 4 AWG silicone O8.7
# + braid/jacket -> O11 (ASSUMED, no OD recorded in the BOM -- measure the
# procured wire); 10 AWG O5.5 (WING_ATTACH_INTERFACE.md SS2.3 assumption);
# a shielded 10 AWG twisted pair is an oval ~12.5 x 7.
# ---------------------------------------------------------------------------
BATT_OD = 11.0
ESC_PAIR_W, ESC_PAIR_T = 12.5, 7.0
# B -- battery lead: pack aft face (Y 84) -> over the cradle's aft wall ->
# roof crest above the aft nodes N2/N4 (Z 124 tops) -> collar bore -> plate.
# 20 wide x 12.5 tall: the channel between the aft nodes' cable zones (X xc +-20,
# cargo_layout_fit) -- batt O11 + 5 V O8 side by side, 6 V O6 and the STPs above
CREST_X0, CREST_X1 = X_CL - 10.0, X_CL + 10.0
CREST_Z0, CREST_Z1 = 124.5, 137.0
CREST_Y0, CREST_Y1 = 86.5, 131.5
# E -- ESC feeders (2 shielded pairs per side).  E1: the flange-face slab
# where the pairs leave the spar wire bore (O16.3 at Y 21 / Z 66.85; flange
# face X -118.9 port).  The worm wheel (X -127.75..-122.75, Y 25.6..67.6,
# Z 48..90) shadows the bore's aft 3.5 mm, so the pairs turn DOWN and FORWARD
# inside the flange thickness (a flared mouth -- CARGO change request T6-CR1)
# and drop along the flange face forward of the wheel.
FLANGE_FACE_X = -118.9
E1 = (FLANGE_FACE_X - ESC_PAIR_T, FLANGE_FACE_X, 5.0, 25.6, 27.0, 75.0)
# E1a: the shadowed slab -- wires exiting aft of Y 25.6 have 3.85 mm before
# the wheel rim.  Reported for the record; gap 0.
E1A = (-122.75, FLANGE_FACE_X, 25.6, 29.15, 58.7, 75.0)
# E3: trough under the wheel along the lower flank (wall is at X -86..-100
# here; the payload face is -131.75).  Two pairs side by side + tilt feed.
E3 = (-129.5, -110.0, 25.6, 85.0, 32.5, 44.5)
# E3->E4 transition: rise from the trough to the Observer-side slot
E34 = (-130.0, -122.2, 85.0, 99.0, 30.0, 83.0)
# E4: slot between the standing cargo Observer tray (X -131.45, Y 108.5..128.5,
# Z 14.2..85) and the inward-sloping aft flank; pairs stacked in Z.
E4 = (-129.2, -122.2, 99.0, 131.5, 58.0, 83.0)
# E5: fan-out inside the fwd collar sleeve zone to the plate's port third
E5 = (-137.5, -122.0, 131.5, FE_UNIT_Y0, 50.0, 106.0)
# T -- tilt-controller VBAT feeds (16 AWG pair, fused 3 A) share E3 and rise
# in the shoulder pocket outboard of the bracket web plane to just under the
# board's lower edge (board X -117.75..-110.75, Y 55..97.9, Z 83..119.5);
# the last 2 mm to the board connector is the board's own cable-tie zone.
T1 = (-117.0, -104.0, 85.0, 99.0, 46.0, 81.0)
# S -- Simon trunk: 5 V + buses from the plate's port edge aft past the can
S1 = (FE_CAN_X1 + 2.0, FE_CAN_X1 + 16.0, FE_PLATE_Y0, SIMON_Y0, 56.0, 100.0)

# Phase 11 scoop capture (55 mm EDF, 1.3x duct match), WBS SS1.1.1.3
PHASE11_CAPTURE_MM2 = 3090.0

# Masses for the ledger (g).  Kaylee PCB assembly per FlightEngineer.md
# "Estimated Mass" (158 g; POWER_DISTRIBUTION.md SS14 says 198 -- flagged);
# can 1.0 mm 6061 (computed below); nodes per airframe/README.md mass table
# (PB2-I 13 g, Pilot 31 g, TACCO 40 g) + 5 g pouch each.
M_FE_PCB = 158.0
M_FE_PLATE = 25.0  # brass plate + EMC bushings (ASSUMED)
M_FE_HW = 10.0
M_CN4 = 13.0 + 40.0 + 5.0
M_FC4 = 13.0 + 31.0 + 5.0
TILT_AXIS_Y = cargo.SHAFT_Y  # 46.6 -- hover thrust line (D-T5-1)
AUW_G = 3911.0  # airframe/README.md Phase 5-10


def can_mass():
    a = 2 * (FE_CAN_X * FE_CAN_Z + FE_CAN_X * FE_CAN_Y + FE_CAN_Z * FE_CAN_Y)
    return a * FE_WALL * 2.70e-3  # g, 6061-T6 2.70 g/cm^3


def rounded_box(x0, x1, y0, y1, z0, z1, r):
    """Box with its four Y-parallel edges rounded to radius r."""
    from shapely.geometry import box as sbox

    # polygon in (X, -Z) so that Rx(-90 deg) -- (x, y, z) -> (x, z, -y) -- lands
    # the extrusion axis on hull +Y and the polygon's second axis on hull +Z
    poly = sbox(x0 + r, -z1 + r, x1 - r, -z0 - r).buffer(r, resolution=16)
    m = trimesh.creation.extrude_polygon(poly, y1 - y0)  # extruded along +Z
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
    m.apply_translation([0, y0, 0])
    b = m.bounds
    assert abs(b[0][1] - y0) < 1e-3 and abs(b[0][2] - z0) < 1e-3, f"rounded_box frame error {b}"
    return m


def layout_t6():
    L = {}
    L["Kaylee can"] = dict(
        solid=rounded_box(
            FE_CAN_X0, FE_CAN_X1, FE_CAN_Y0, FE_CAN_Y1, FE_CAN_Z0, FE_CAN_Z1, FE_CAN_R
        ),
        gap=STATIC_GAP,
        section="middle",
    )
    L["Kaylee entry plate"] = dict(
        solid=box(FE_XC - FE_PLATE_X / 2, FE_XC + FE_PLATE_X / 2, FE_PLATE_Y0, FE_PLATE_Y1,
                  FE_ZC - FE_PLATE_Z / 2, FE_ZC + FE_PLATE_Z / 2),
        gap=STATIC_GAP,
        section="middle",
        mates=("Kaylee can",),
    )
    L["CN4 (XO) pouch"] = dict(
        solid=box(SIMON_X0, SIMON_X1, SIMON_Y0, SIMON_Y1, CN4_Z0, CN4_Z1), gap=STATIC_GAP,
        section="middle",
    )
    L["FC4 (Pilot) pouch"] = dict(
        solid=box(SIMON_X0, SIMON_X1, SIMON_Y0, SIMON_Y1, FC4_Z0, FC4_Z1), gap=STATIC_GAP,
        section="middle",
    )
    L["Simon cable zone"] = dict(
        solid=box(SIMON_X1, SIMON_CABLE_X1, SIMON_Y0, SIMON_Y1, CN4_Z0, FC4_Z1), gap=STATIC_GAP,
        section="middle",
        mates=("CN4 (XO) pouch", "FC4 (Pilot) pouch", "Simon trunk"),
    )
    # saddle: from the floor skin up to the pouch bottoms (seats on skin)
    L["Simon saddle"] = dict(
        solid=box(SIMON_X0 - 4.0, SIMON_X1 + 4.0, SIMON_Y0, SIMON_Y1 + 2.0, 5.0, CN4_Z0),
        skin_seat=True,
        section="middle",
        mates=("CN4 (XO) pouch",),
    )
    L["hatch cut"] = dict(
        solid=box(HATCH_X0, HATCH_X1, HATCH_Y0, HATCH_Y1, -5.0, HATCH_ZCUT),
        skin_seat=True,
        section="middle",
        mates=("Kaylee can", "Kaylee entry plate", "Kaylee cradle pillars"),
    )
    for i, (fx, fy) in enumerate(
        (
            (FE_XC - FE_FOOT_DX, FE_FOOT_YC - FE_FOOT_DY),
            (FE_XC + FE_FOOT_DX, FE_FOOT_YC - FE_FOOT_DY),
            (FE_XC - FE_FOOT_DX, FE_FOOT_YC + FE_FOOT_DY),
            (FE_XC + FE_FOOT_DX, FE_FOOT_YC + FE_FOOT_DY),
        )
    ):
        L[f"Kaylee cradle pillar {i}"] = dict(
            solid=box(fx - 5.0, fx + 5.0, fy - 5.0, fy + 5.0, 5.0, FE_CAN_Z0),
            skin_seat=True,
            section="middle",
            mates=("Kaylee can", "hatch cut"),
        )
    for name, sx in SMA_XS.items():
        L[name] = dict(
            solid=cyl("z", sx, SMA_Y, 150.0, 175.0, SMA_BORE_D / 2),
            skin_seat=True,
            section="middle",
        )
    # middle-side trunks
    L["Simon trunk"] = dict(solid=box(*S1), gap=0.0, section="middle",
                            mates=("Simon cable zone",))
    L["fan-out E5"] = dict(solid=box(*E5), gap=0.0, section="middle", mirror=True)
    L["crest B2 (middle)"] = dict(
        solid=box(CREST_X0, CREST_X1, CREST_Y1, FE_UNIT_Y0, 112.0, CREST_Z1), gap=0.0,
        section="middle", mates=("Kaylee entry plate",),
    )
    # cargo-side corridors (checked against the cargo shell + Rev T5e layout)
    L["ESC E1 flange-face drop"] = dict(
        solid=box(*E1), gap=STATIC_GAP, section="cargo", mirror=True
    )
    L["ESC E1a wheel-shadow slab"] = dict(solid=box(*E1A), gap=0.0, section="cargo", mirror=True,
                                          record_only=True)
    L["ESC E3 under-wheel trough"] = dict(
        solid=box(*E3),
        gap=STATIC_GAP,
        section="cargo",
        mirror=True,
        mates=("ESC E1 flange-face drop", "ESC E34 rise", "tilt feed T1"),
    )
    L["ESC E34 rise"] = dict(solid=box(*E34), gap=STATIC_GAP, section="cargo", mirror=True,
                             mates=("ESC E4 Observer slot",))
    L["ESC E4 Observer slot"] = dict(solid=box(*E4), gap=STATIC_GAP, section="cargo", mirror=True)
    L["tilt feed T1"] = dict(solid=box(*T1), gap=STATIC_GAP, section="cargo", mirror=True,
                             mates=("ESC E3 under-wheel trough",))
    L["crest B1 (cargo)"] = dict(
        solid=box(CREST_X0, CREST_X1, CREST_Y0, CREST_Y1, CREST_Z0, CREST_Z1), gap=STATIC_GAP,
        section="cargo",
    )
    return L


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def load_middle():
    m = trimesh.load(MIDDLE_SHELL, process=True)
    assert m.is_watertight, "published middle shell is not watertight"
    return m


def load_cargo():
    m = trimesh.load(cargo.SHELL, process=True)
    assert m.is_watertight, "published cargo shell is not watertight"
    m = cargo.shell_after_merge(m)
    extras = []
    for p in (FLANGE_PORT, FLANGE_STBD, LG_LEGS):
        if os.path.exists(p):
            extras.append(trimesh.load(p, process=True))
    return m, extras


def check_section(L, shell_tm, extras, section, cargo_solids=None):
    shell = to_man(shell_tm)
    obst = [to_man(e) for e in extras if e.is_watertight]
    print(f"\n=== {section.upper()} section: {len(shell_tm.faces):,} faces, "
          f"{len(obst)} extra obstacle mesh(es) ===")
    print(f"{'envelope':32s} {'hit mm3':>9s} {'<gap mm3':>9s} {'extra':>7s}  note")
    solids = {}
    for name, e in list(L.items()):
        if e["section"] != section:
            continue
        solids[name] = e["solid"]
        if e.get("mirror"):
            solids[name + " (stbd)"] = mirror_x(e["solid"])
            L[name + " (stbd)"] = dict(e, solid=solids[name + " (stbd)"])
    fails = 0
    for name, tm in solids.items():
        e = L[name]
        m = to_man(tm)
        hit = (m ^ shell).volume()
        gap = e.get("gap", GAP_MM)
        near = (to_man(dilate(tm, gap)) ^ shell).volume() if gap > 0 else hit
        extra = sum((m ^ o).volume() for o in obst)
        note = ""
        if e.get("skin_seat"):
            note = "seats on / cuts skin (hit expected)"
            bad = False
        elif e.get("record_only"):
            note = "RECORD ONLY (accepted, see doc)"
            bad = False
        else:
            bad = hit > 1.0 or near > 1.0 or extra > 1.0
        if bad:
            fails += 1
            b = tm.bounds
            note += (f" FAIL (gap {gap})  box X{b[0][0]:.0f}..{b[1][0]:.0f} "
                     f"Y{b[0][1]:.0f}..{b[1][1]:.0f} Z{b[0][2]:.0f}..{b[1][2]:.0f}")
        print(f"{name:32s} {hit:9.0f} {near:9.0f} {extra:7.0f}  {note}")
    # pairwise, within the section and (cargo) against the Rev T5e layout
    print("pairwise interference (raw overlap, mm3):")
    others = dict(solids)
    if cargo_solids:
        others.update(cargo_solids)
    names = list(solids)
    bad_pairs = 0
    seen = set()
    for a in names:
        for b_ in others:
            if a == b_ or (b_, a) in seen:
                continue
            seen.add((a, b_))
            ma, mb = L[a].get("mates", ()), L.get(b_, {}).get("mates", ())
            if b_ in ma or a in mb or b_.replace(" (stbd)", "") in ma:
                continue
            v = (to_man(solids[a]) ^ to_man(others[b_])).volume()
            if v > 1.0:
                bad_pairs += 1
                print(f"  {a:30s} x {b_:30s} {v:9.0f}  OVERLAP")
    if bad_pairs == 0:
        print("  none")
    return fails, bad_pairs, solids


def neck_void(shell_tm, y):
    """Largest interior void polygon of the section at Y (hull X/Z)."""
    s = shell_tm.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    if s is None:
        return None
    p, T = s.to_2D()
    best = None
    for q in p.polygons_full:
        for ring in q.interiors:
            pts = np.array(ring.coords)
            w = (T @ np.c_[pts, np.zeros(len(pts)), np.ones(len(pts))].T).T[:, :3]
            poly = Polygon(np.c_[w[:, 0], w[:, 2]])
            if best is None or poly.area > best.area:
                best = poly
    return best


def airflow_report(shell_tm, solids):
    print("\nPhase 11 free bore area (neck void minus equipment) vs scoop capture "
          f"{PHASE11_CAPTURE_MM2:.0f} mm^2:")
    for y in (135, 145, 155, 165, 175, 185, 195, 201):
        v = neck_void(shell_tm, y)
        if v is None:
            continue
        cuts = []
        for name, tm in solids.items():
            sec = tm.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
            if sec is None:
                continue
            p, T = sec.to_2D()
            for q in p.polygons_full:
                pts = np.array(q.exterior.coords)
                w = (T @ np.c_[pts, np.zeros(len(pts)), np.ones(len(pts))].T).T[:, :3]
                cuts.append(Polygon(np.c_[w[:, 0], w[:, 2]]))
        blocked = unary_union(cuts).intersection(v).area if cuts else 0.0
        free = v.area - blocked
        flag = "ok" if free >= PHASE11_CAPTURE_MM2 else "SHORT"
        print(
            f"  Y={y:3d}: void {v.area:8.0f}  blocked {blocked:7.0f}  "
            f"free {free:8.0f} mm^2  {flag}"
        )


def cg_ledger():
    m_can = can_mass()
    rows = [
        ("Flight Engineer PCB assembly", M_FE_PCB, (FE_CAN_Y0 + FE_CAN_Y1) / 2),
        (f"Kaylee can ({FE_WALL:.1f} mm 6061)", m_can, (FE_CAN_Y0 + FE_CAN_Y1) / 2),
        ("entry plate + EMC bushings", M_FE_PLATE, (FE_PLATE_Y0 + FE_PLATE_Y1) / 2),
        ("Kaylee hardware", M_FE_HW, FE_FOOT_YC),
        ("CN4 XO node + pouch", M_CN4, (SIMON_Y0 + SIMON_Y1) / 2),
        ("FC4 Pilot node + pouch", M_FC4, (SIMON_Y0 + SIMON_Y1) / 2),
    ]
    print("\nMass / CG ledger (hull-frame Y; moment about the tilt axis Y "
          f"{TILT_AXIS_Y}, + = nose-up-heavy aft):")
    tm = tmom = 0.0
    for n, m, y in rows:
        mom = m * (y - TILT_AXIS_Y)
        tm += m
        tmom += mom
        print(f"  {n:34s} {m:7.1f} g  Y {y:6.1f}  {mom:9.0f} g*mm")
    print(f"  {'TOTAL middle-section equipment':34s} {tm:7.1f} g  "
          f"Y {TILT_AXIS_Y + tmom / tm:6.1f}  {tmom:9.0f} g*mm")
    print(f"  -> CG shift of the {AUW_G:.0f} g aircraft: {tmom / AUW_G:+.1f} mm (aft) "
          f"vs the same aircraft without these items")
    print(f"  (battery, for scale: 750 g at Y {cargo.BATT_Y0 + cargo.BATT_L / 2:.0f} -> "
          f"{750 * (cargo.BATT_Y0 + cargo.BATT_L / 2 - TILT_AXIS_Y):.0f} g*mm)")
    print(f"  masses: {tm:.0f} g = {tm / 453.592:.3f} lbm")


def write_scad(path):
    lines = [
        "// middle_layout_t6_params.scad -- GENERATED by tools/middle_layout_fit.py",
        "// --write-scad.  Do not edit: change the Python constants and regenerate.",
        "// Hull frame: X = +port, Y = +aft, Z = +dorsal (mm).",
        f"X_CL = {X_CL};",
        f"NECK_ZC = {NECK_ZC};",
        f"NECK_R = {NECK_R};",
        f"FE_CAN_X = {FE_CAN_X}; FE_CAN_Z = {FE_CAN_Z}; "
        f"FE_CAN_Y = {FE_CAN_Y}; FE_CAN_R = {FE_CAN_R};",
        f"FE_XC = {FE_XC}; FE_ZC = {FE_ZC};",
        f"FE_CAN_Y0 = {FE_CAN_Y0}; FE_CAN_Y1 = {FE_CAN_Y1};",
        f"FE_CAN_Z0 = {FE_CAN_Z0}; FE_CAN_Z1 = {FE_CAN_Z1};",
        f"FE_PLATE_Y0 = {FE_PLATE_Y0}; FE_PLATE_Y1 = {FE_PLATE_Y1};",
        f"FE_PLATE_X = {FE_PLATE_X}; FE_PLATE_Z = {FE_PLATE_Z};",
        f"FE_BOARD_X = {FE_BOARD_X}; FE_BOARD_Z = {FE_BOARD_Z};",
        f"FE_HOLE_DX = {FE_HOLE_DX}; FE_HOLE_DZ = {FE_HOLE_DZ};",
        f"FE_FOOT_DX = {FE_FOOT_DX}; FE_FOOT_DY = {FE_FOOT_DY}; FE_FOOT_YC = {FE_FOOT_YC};",
        f"HATCH_X0 = {HATCH_X0}; HATCH_X1 = {HATCH_X1}; "
        f"HATCH_Y0 = {HATCH_Y0}; HATCH_Y1 = {HATCH_Y1};",
        f"HATCH_ZCUT = {HATCH_ZCUT}; HATCH_LIP = {HATCH_LIP};",
        "HATCH_SCREWS = [" + ", ".join(f"[{x}, {y}]" for x, y in HATCH_SCREWS) + "];",
        f"NODE_L = {NODE_L}; NODE_H = {NODE_H}; NODE_T = {NODE_T}; NODE_CABLE = {NODE_CABLE};",
        f"SIMON_Y0 = {SIMON_Y0}; SIMON_Y1 = {SIMON_Y1}; "
        f"SIMON_XC = {SIMON_XC}; SIMON_ZC = {SIMON_ZC};",
        f"SIMON_X0 = {SIMON_X0}; SIMON_X1 = {SIMON_X1}; SIMON_CABLE_X1 = {SIMON_CABLE_X1};",
        f"CN4_Z0 = {CN4_Z0}; CN4_Z1 = {CN4_Z1}; FC4_Z0 = {FC4_Z0}; FC4_Z1 = {FC4_Z1};",
        f"SIMON_STACK_GAP = {SIMON_STACK_GAP}; SADDLE_T = {SADDLE_T};",
        "SADDLE_BOSS = [" + ", ".join(f"[{x}, {y}]" for x, y in SADDLE_BOSS) + "];",
        f"SMA_Y = {SMA_Y}; SMA_BORE_D = {SMA_BORE_D};",
        "SMA_XS = [" + ", ".join(str(v) for v in SMA_XS.values()) + "];",
        f"CREST_X0 = {CREST_X0}; CREST_X1 = {CREST_X1}; "
        f"CREST_Z0 = {CREST_Z0}; CREST_Z1 = {CREST_Z1};",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _plot(mid_tm, cargo_tm, solids_mid, solids_cargo, cargo_solids):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = os.path.join(REPO, "docs", "img")
    os.makedirs(out, exist_ok=True)
    fig, axs = plt.subplots(2, 4, figsize=(28, 13))
    cuts = [(mid_tm, solids_mid, {}, y) for y in (144, 162, 175, 190)] + [
        (cargo_tm, solids_cargo, cargo_solids, y) for y in (18, 50, 92, 118)
    ]
    for ax, (shell, sol, ctx, y) in zip(axs.ravel(), cuts):
        n = [0, 1, 0]
        s = shell.section(plane_origin=[0, y, 0], plane_normal=n)
        if s is not None:
            for ent in s.entities:
                p = s.vertices[ent.points]
                ax.plot(p[:, 0], p[:, 2], "k-", lw=0.5)
        for name, tm in ctx.items():
            sec = tm.section(plane_origin=[0, y, 0], plane_normal=n)
            if sec is None:
                continue
            for ent in sec.entities:
                p = sec.vertices[ent.points]
                ax.plot(p[:, 0], p[:, 2], lw=0.8, color="0.6")
        for name, tm in sol.items():
            sec = tm.section(plane_origin=[0, y, 0], plane_normal=n)
            if sec is None:
                continue
            for ent in sec.entities:
                p = sec.vertices[ent.points]
                ax.plot(p[:, 0], p[:, 2], lw=1.4, label=name)
        ax.set_title(f"XZ at Y={y}  ({'middle' if shell is mid_tm else 'cargo, T5e grey'})")
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-280, -60)
        ax.set_ylim(-5, 175)
        ax.legend(fontsize=6, loc="lower left")
    fig.tight_layout()
    png = os.path.join(out, "middle_layout_t6_sections.png")
    fig.savefig(png, dpi=80)
    print(f"wrote {os.path.relpath(png, REPO)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plot", action="store_true")
    ap.add_argument("--write-scad", action="store_true",
                    help="regenerate airframe/openscad/fuselage/middle_layout_t6_params.scad")
    ap.add_argument("--skip-cargo", action="store_true", help="middle section only (fast)")
    a = ap.parse_args()
    if a.write_scad:
        p = os.path.join(REPO, "airframe", "openscad", "fuselage", "middle_layout_t6_params.scad")
        write_scad(p)
        print("wrote", os.path.relpath(p, REPO))
    print(f"Kaylee can: {FE_CAN_X} x {FE_CAN_Z} x {FE_CAN_Y} mm ext, {can_mass():.0f} g at "
          f"{FE_WALL} mm; lid clearance over a {FE_COMP_MAX} mm component = {FE_CLEAR:.1f} mm")
    print(f"Y budget: sleeve {FWD_SLEEVE_Y1} | plate {FE_PLATE_Y0}..{FE_PLATE_Y1} | can "
          f"{FE_CAN_Y0}..{FE_CAN_Y1} | pouches {SIMON_Y0}..{SIMON_Y1} | "
          f"rear face {REAR_RESERVED_Y}")
    assert SIMON_Y1 <= REAR_RESERVED_Y, "layout crosses into the Phase-11 rear cone"
    L = layout_t6()
    mid = load_middle()
    f1, p1, sol_mid = check_section(L, mid, [], "middle")
    airflow_report(mid, {k: v for k, v in sol_mid.items()
                         if not L[k].get("skin_seat") and "trunk" not in k
                         and "E5" not in k and "B2" not in k})
    f2 = p2 = 0
    sol_cargo, cargo_solids, cargo_tm = {}, {}, None
    if not a.skip_cargo:
        cargo_tm, extras = load_cargo()
        cl = cargo.layout_t5()
        for n, e in cl.items():
            cargo_solids[n] = e["solid"]
            if e.get("mirror"):
                cargo_solids[n + " (stbd)"] = mirror_x(e["solid"])
        f2, p2, sol_cargo = check_section(L, cargo_tm, extras, "cargo", cargo_solids)
    cg_ledger()
    ok = f1 + f2 == 0 and p1 + p2 == 0
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'} ({f1 + f2} envelope(s) foul a shell/gap, "
          f"{p1 + p2} pair overlap(s))")
    if a.plot:
        _plot(mid, cargo_tm, sol_mid, sol_cargo, cargo_solids)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
