#!/usr/bin/env python3
"""
merge_cargo_interior.py — Rev R1 (2026-06-30)

Build the FINAL canonical cargo-section shell by merging every cargo interior
feature into the Blender-canonical hull skin, in one robust manifold3d pass.
This is the definitive processor for the cargo section (TODO.md §1.1.1.0a); it
supersedes the cargo path of add_structural_features.py (the script that left
the MESH-01 fragmentation defect — 71 131 disconnected bodies, is_watertight=
False — on the published cargo STL).

Why it is robust (MESH-01 fix)
------------------------------
add_structural_features.py subtracted dozens of cutters one at a time with
trimesh.boolean.difference(engine="manifold") plus a per-step "repair" on a
1.4 M-face mesh; that fragile sequential round-trip is what fragmented the
shells.  This script instead starts from the KNOWN-CLEAN Blender source
(watertight 2-manifold, vol = 370 509 mm^3 = the structural_analysis.md
mass-budget figure), bakes it into the hull frame (same transform
tools/bake_hull_frame.py records for Cargo_Shell), and evaluates
`(shell + positives) − negatives` as a single manifold3d expression.  Boolean
of closed manifolds is closed by construction ⇒ guaranteed watertight out.

Two design essentials handled correctly
---------------------------------------
1. OPEN JOINT FACES.  The four fuselage sections are open-ended tubes joined by
   internal splice collars (CLAUDE.md: "mating surfaces between the four
   fuselage sections will be open").  The Blender source is CLOSED-capped at the
   fwd (head/cargo, hull Y≈−71.5) and aft (cargo/middle, hull Y≈+132) faces, so
   this script removes each end cap with a cavity-shaped plug — leaving a
   watertight OPEN "pipe" end (the 2 mm wall wraps the rim), prepped for the
   splice collars.  (Subtracting a solid plug keeps the mesh a closed
   2-manifold; an open-ended thick tube is watertight like a length of pipe.)

2. WALL-CONFORMING INTERIOR FEATURES.  Serenity's hull walls curve continuously,
   so a flat-faced boss/pad butted against them contacts only at a tangent and
   floats off elsewhere ("orphaned sockets").  Every positive interior feature
   is therefore modelled DEEP (extending past the exterior skin), then clipped
   with the section's own OUTER-SKIN ENVELOPE (∩ envelope).  The intersection
   trims the outboard end exactly to the curved skin surface, so each feature
   seats flush against — and fuses fully into — the real wall, with zero
   exterior protrusion and nothing floating in mid-cavity.

Features merged (hull frame, X=+port, Y=+aft, Z=+dorsal)
-------------------------------------------------------
NEGATIVE (removed):
  * Interior-wall removal — the cargo-bay floor "duct" the Blender hollowing
    left inside the cavity (a ~54×38 mm box blister on the belly, hull
    X −196..−142, Y −15..+102, Z 6..44), confirmed by section + render.
  * Clamshell belly aperture — hull X[−222.5..−117.6] × Y[+2..+108].
  * OPEN fwd + aft joint faces (cavity-plug cap removal).
  * Boss-pin bores (Joint 1 + Joint 2 — collar alignment dowels), keel channel,
    Y=+30 ring-frame pocket — single-sourced from add_structural_features.py.
  * Wing spar bore (Ø12.3, full lateral span) + 2 wing-root mortises (through
    each lateral wall), at the RE-DERIVED chord stations (129 mm root chord, LE
    root hull Y=−7: spar 35% → Y=+38.15 at Z=68.42 (camber midline, Rev S1b);
    mortise 50% → Y=+57.5 at Z=62.5).
  * M3 heat-set bores in the nacelle-servo pads.

POSITIVE (added, envelope-clipped so they conform + fuse to the curved wall):
  * 4 clamshell hinge-pin retention blocks (from generate_cargo_hinge_retention).
  * 2 wing-spar bearing bosses (Ø22, coaxial with the spar bore).
  * 2 nacelle-servo mount pads (one per lateral wall).
  * Inara avionics-bay standoff bosses (4, dorsal port).  The dorsal Faraday
    access-panel CUT and the River (stbd) bay are DEFERRED (SCAD avionics
    modules are still in the pre-R1 legacy Y-as-dorsal frame; TODO.md §1.1.3.3).

Deferred (documented, NOT cut — legacy-frame re-derivation needed):
  * Inara/River dorsal Faraday access-panel cuts; River (stbd) avionics bay.
  * GPS×2 + FPV flush skin recesses; door-servo pads; latch-catch lips.
  * Landing-gear leg-mount bosses (Rev R5 wire-brace) — TODO.md §1.1.4; a
    keep-out check reports whether merged geometry intrudes on those zones.

References
    docs/structural_analysis.md (Rev R1) — joint / wing / ring-frame design.
    airframe/blender-scripts/add_structural_features.py — joint-feature source.
    airframe/stls/fuselage/cargo/generate_cargo_hinge_retention.py — Rev R1c.
    airframe/stls/fuselage/cargo/generate_cargo_doors.py — Rev R1b door geometry.
    airframe/openscad/fuselage/cargo/cargo_sect_shell24.scad — interior-feature
        design intent (legacy-frame constants; superseded here where re-derived).
    tools/bake_hull_frame.py — Cargo_Shell bake transform.

Run (no Blender needed):
    python3 airframe/blender-scripts/merge_cargo_interior.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

import os
import struct
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
BLENDER_SRC = os.path.join(
    SCRIPT_DIR, "files-hollowed-24in", "cargo_sect_shell24_2mm_repaired.stl"
)
OUT_PATH = os.environ.get("CARGO_MERGE_OUT") or os.path.join(
    REPO_ROOT,
    "airframe",
    "stls",
    "fuselage",
    "cargo",
    "cargo_sect_shell24_2mm_repaired.stl",
)
CARGO_DIR = os.path.join(REPO_ROOT, "airframe", "stls", "fuselage", "cargo")

# Reuse the single-sourced joint-feature design from add_structural_features.py
sys.path.insert(0, SCRIPT_DIR)
import add_structural_features as asf  # noqa: E402

# Reuse the Rev R1c hull-frame hinge retention blocks verbatim
sys.path.insert(0, CARGO_DIR)
import generate_cargo_hinge_retention as hinge  # noqa: E402

MARKER = b"SerenityUAV HULL-FRAME R1"

# Cargo_Shell bake transform — MUST match tools/bake_hull_frame.py COMPONENTS.
#   180 deg about +Z → (x,y,z)→(−x,−y,z);  T = (−274.4, −282.8, 0)
BAKE_T = np.array([-274.4000100, -282.8000440, 0.0])

WALL_MM = 2.0  # 2 mm foam-fill wall (Blender hollowing pitch / SCAD)

# A boundary loop flatter than this (width away from its best-fit line) is a
# zero-area boolean-seam slit, not a hole -- see close_zero_area_slits().
# 1e-3 mm is a micron: four orders below the 0.1 mm print resolution, so no
# real feature can hide under it.
SLIT_FLAT_MM = 1e-3

# CF-PETG mass reporting: as-printed (4 perimeters + ≥40% infill) ~1.05 g/cm^3;
# fully dense CF-PETG ~1.28 g/cm^3.  These bracket the true printed mass.
RHO_PRINT = 1.05e-3  # g/mm^3
RHO_SOLID = 1.28e-3  # g/mm^3


# ---------------------------------------------------------------------------
# manifold3d helpers
# ---------------------------------------------------------------------------


def to_man(tm):
    """trimesh.Trimesh -> manifold3d.Manifold (float32, as manifold3d uses)."""
    return Manifold(
        Mesh(
            vert_properties=tm.vertices.astype(np.float32),
            tri_verts=tm.faces.astype(np.uint32),
        )
    )


def from_man(man):
    """manifold3d.Manifold -> trimesh.Trimesh (float64 vertices)."""
    msh = man.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(msh.vert_properties, dtype=np.float64)[:, :3],
        faces=np.asarray(msh.tri_verts, dtype=np.int64),
        process=False,
    )


def union_all(meshes):
    """Union a list of trimesh solids into one Manifold (None if empty)."""
    acc = None
    for m in meshes:
        mm = to_man(m)
        acc = mm if acc is None else (acc + mm)
    return acc


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from hull-frame corner coordinates."""
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0])
    return b


def x_cylinder(y_cen, z_cen, x0, x1, radius, sections=48):
    """Cylinder whose axis is hull X (lateral), spanning x0..x1."""
    cyl = trimesh.creation.cylinder(radius=radius, height=(x1 - x0), sections=sections)
    cyl.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [0, 1, 0]))
    cyl.apply_translation([(x0 + x1) / 2.0, y_cen, z_cen])
    return cyl


def z_cylinder(x_cen, y_cen, z0, z1, radius, sections=48):
    """Cylinder whose axis is hull Z (dorsal), spanning z0..z1."""
    cyl = trimesh.creation.cylinder(radius=radius, height=(z1 - z0), sections=sections)
    cyl.apply_translation([x_cen, y_cen, (z0 + z1) / 2.0])
    return cyl


def y_pin(x_cen, z_cen, y0, y1, radius, sections=32):
    """Y-axis boss-pin bore (matches asf._y_cylinder geometry)."""
    cyl = trimesh.creation.cylinder(radius=radius, height=(y1 - y0), sections=sections)
    cyl.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [1, 0, 0]))
    cyl.apply_translation([x_cen, (y0 + y1) / 2.0, z_cen])
    return cyl


def axis_cylinder(center, direction, t0, t1, radius, sections=32):
    """Cylinder on an ARBITRARY axis, spanning t0..t1 along `direction`
    measured from `center`.  The landing-gear bay bolts run normal to the
    canted bay plate, so none of the axis-aligned helpers above fit them."""
    d = np.asarray(direction, dtype=float)
    d = d / np.linalg.norm(d)
    c = np.asarray(center, dtype=float)
    cyl = trimesh.creation.cylinder(radius=radius, height=(t1 - t0),
                                    sections=sections)
    cyl.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], d))
    cyl.apply_translation(c + d * ((t0 + t1) / 2.0))
    return cyl


# ---------------------------------------------------------------------------
# Outer-skin envelope (for wall-conforming feature clipping)
# ---------------------------------------------------------------------------


def extract_envelope(shell_tm):
    """Return the section's OUTER-skin closed solid (the exterior envelope).

    The hollow shell is two nested closed surfaces (outer skin + inner cavity
    wall); the outer one — the larger bounding box — is the exterior envelope.
    Intersecting a deep feature with this trims its outboard end exactly to the
    curved skin, so bosses/pads seat flush against the real wall."""
    comps = trimesh.graph.connected_components(
        shell_tm.face_adjacency, nodes=np.arange(len(shell_tm.faces))
    )
    best, best_v = None, -1.0
    for c in comps:
        sub = shell_tm.submesh([c], append=True)
        e = sub.extents
        v = float(e[0] * e[1] * e[2])
        if v > best_v:
            best, best_v = sub, v
    return best


# ---------------------------------------------------------------------------
# Joint-face opening
# ---------------------------------------------------------------------------
# The fwd (head/cargo) and aft (cargo/middle) mating faces are cut FLAT at their
# mating planes (asf._flat_face_cutter with asf.MATING_PLANES["cargo_fwd"] /
# ["cargo_aft"]) in build_negatives(), removing the rounded closure caps and
# leaving clean flat OPEN tubes the conforming splice collars slip into.
# History (JOINT-01/JOINT-02, 2026-07-06): the original single-station
# open_face_plug() bit the fwd dorsal skin and left ragged rim fragments; the
# lofted _bore_open_cutter() that replaced it cleaned the rim but never removed
# the closure cap, so the collar still passed through solid plastic — the flat
# half-space cut here fixes both (a plane leaves no jaggies and does remove the
# cap).  The section end profiles no longer taper into a rounded cap, so the
# splice collar is now a CONFORMING lofted sleeve (generate_conforming_collars.py).


# ---------------------------------------------------------------------------
# Feature geometry (hull frame, mm)
# ---------------------------------------------------------------------------

# Interior-wall (cargo-bay floor "duct") removal — box engulfs the duct walls
# above the belly skin; the door aperture below clears the rest.  Bottom held
# at Z=8 so belly skin FWD of the bay is untouched (a <=2 mm foam-filled curb
# is left where the duct met the floor).
DUCT_CUT = (-201.0, -137.0, -20.0, 107.0, 8.0, 48.0)  # x0,x1,y0,y1,z0,z1

# Clamshell belly aperture — between the two door hinge lines (stbd −222.5,
# port −117.6), bay Y +2..+108, Z −3..+9 removes only the belly skin.
APERTURE = (-222.5, -117.6, 2.0, 108.0, -3.0, 9.0)

# Wing subsystem — RE-DERIVED chordwise stations (hull frame).
WING_LE_ROOT_Y = -7.0
WING_ROOT_CHORD = 129.0

# REV S1b (2026-08-16): spar station 30 % -> 35 % of root chord, by owner
# decision.  This is the fuselage half of the wings SS1.1.2 spar-interface
# blocker: the wing sat at the 22.0 mm station (hull Y +15) and this shell cut
# at 38.7 mm (Y +31.7), so the spar could not pass through both parts.  Both
# are now on 45.15 mm.  Keep in step with SPAR_BORE_STATION in
# airframe/openscad/wings/wings_s1223_revo.scad -- they are the same physical
# rod and there is no other link between the two files.
WING_SPAR_Y = WING_LE_ROOT_Y + 0.35 * WING_ROOT_CHORD  # = +38.15
WING_MORT_Y = WING_LE_ROOT_Y + 0.50 * WING_ROOT_CHORD  # = +57.5

# Mortise / nacelle-servo reference height.  NOT the spar height -- see below.
WING_ROOT_Z = 62.5

# Spar axis height, hull frame.  The bore is centred on the S1223 CAMBER
# MIDLINE, not on the chord line, so moving the station chordwise also moves it
# vertically: midline 8.523 mm at the old 22.0 mm station, 10.410 mm at 45.15.
#
# WING_CHORD_LINE_Z is where the wing's chord line sits in the hull frame.
# 58.01 is confirmed two independent ways: airframe/openscad/port_tilt_spar_-
# assembly.scad states SPAR_Z = "camber midline + 58", and solving the wing
# SCAD's own recorded baked bound (Z max +76.99) against the root section's
# top (+18.99 mm above the chord line) gives 58.01.
#
# This SUPERSEDES the "root ≈ hull Z ≈ +71 (~8 mm up)" figure in the
# wings-nacelles WBS SS1.1.2 blocker text, which was a prose estimate: the same
# derivation puts the OLD station at 66.52, not 71.  AGENTS.md SS11.4 -- actual
# model state outranks stale documentation.
#
# Previously the spar bore and bosses were cut at WING_ROOT_Z (62.5), i.e. on
# the mortise height rather than on the camber midline, which is why they never
# lined up with the wing.
WING_CHORD_LINE_Z = 58.01
WING_SPAR_MIDLINE = 10.41   # midline_frac(45.15/129) * 129, from the wing SCAD
WING_SPAR_Z = WING_CHORD_LINE_Z + WING_SPAR_MIDLINE  # = 68.42
WING_SPAR_BORE_D = 12.3
WING_SPAR_BOSS_OD = 22.0
MORT_W = 30.8  # mortise Y span
MORT_H = 20.8  # mortise Z span

# Lateral-wall X reference bands (deep-embed spans; the outboard end is clipped
# to the real skin by the envelope, so only rough bracketing is needed).
PORT_OUTB, PORT_INB = -60.0, -100.0  # port wall bracket (skin ≈ −83..−90)
STBD_OUTB, STBD_INB = -278.0, -240.0  # stbd wall bracket (skin ≈ −250..−255)

# Nacelle-servo mount pads.
# Nacelle-servo mount pads.  The servo DRIVES the rotating tilt-spar (horn ->
# pushrod -> spar crank), so its mount is positioned RELATIVE TO THE SPAR, not
# in absolute hull coordinates: move the spar and the servo must move with it
# or the linkage throw is detuned and the pushrod needs re-sizing (root WBS.md
# SS1.1.3 -- Nacelles, "Tune servo->spar horn/pushrod linkage throw
# (-5..140 deg)").  Rev S1b makes that dependency explicit in the code, because
# holding NSVMT_Y/Z absolute through the spar move silently broke it.
#
# The offsets below are exactly those in force before the move
# (spar Y 31.7 -> pad Y 45.0; spar Z 62.5 -> pad Z 93.0), so the linkage
# geometry is carried across unchanged.
NSVMT_DY = 13.3   # pad centre, chordwise aft of the spar axis
NSVMT_DZ = 30.5   # pad centre, above the spar axis
NSVMT_Y = WING_SPAR_Y + NSVMT_DY   # = 51.45
NSVMT_PAD_W = 52.0  # Y span
NSVMT_PAD_H = 30.0  # Z span
# = 98.92.  Tracking the spar also restores the spar-boss clearance the old
# absolute value had: boss top is Z 79.42 and the pad now starts at 83.92,
# a 4.5 mm gap (the pre-move design intent was ~4 mm).
NSVMT_Z = WING_SPAR_Z + NSVMT_DZ
NSVMT_HOLE_S_Y = 17.5
NSVMT_HOLE_S_Z = 8.0
NSVMT_M3_D = 4.1

# Inara avionics-bay standoff bosses (dorsal port half, additive only).
INARA_X = -135.0
INARA_Y = 90.0
INARA_BOSS_DX = 25.0
INARA_BOSS_DY = 15.0
BOSS_OD = 8.0
BOSS_BORE_D = 4.1
DORSAL_Z_TOP = 172.0  # above the dorsal skin (Z_max ≈ 163); clipped by envelope
DORSAL_Z_INB = 145.0  # boss reaches this far into the cavity

# ---------------------------------------------------------------------------
# Rev R6 landing-gear bay integration (LG-02 / LG-10, 2026-08-09)
#
# Canonical corner stations, docs/LANDING_GEAR_ANALYSIS.md SS2.2:
#   (label, hip_x, hip_y, hip_z, swing_azimuth_deg)
# These SUPERSEDE the Rev R5 keep-out boxes that used to live here, which were
# at the wrong stations entirely (fwd Y 15..35 vs the real fore hip at Y = -7,
# and X -130..-95 vs the real port hips at X -79 / -90).
#
# What the hull carries: bolt bosses ONLY.  The bay's recess depth is carried
# on the printed bay plate as a cowl (canonical_leg_r6_*.scad bay_cowl), not on
# the airframe -- a full flat pad on the hull costs 240 g because it must fill
# 9-30 mm of flank curvature, and the footprint's interior is already occupied
# by the wing-spar boss, wing-root mortise and nacelle-servo pad, so it cannot
# be sunk inward either.  These bosses are internal thickening: modelled deep
# and clipped by the outer-skin envelope, so each conforms to the real curved
# wall and fuses to it (same treatment as the nacelle-servo pads above).
#
# NOTE the third sentence above: the footprint's interior is occupied by the
# wing-spar boss, the wing-root mortise and the nacelle-servo pad.  That was
# recorded here as prose in 2026-08-09 but never enforced geometrically, and
# measurement in 2026-08-16 showed all three conflicts were real -- see
# wing_keepout_*() below and tools/landing_gear_wing_clearance.py.
#
# The corner table that used to sit here (hips at Y -7 / +107, a 5-tuple) was
# DEAD CODE: the LG-10.2 table below rebinds LG_CORNERS before any read, so
# editing this copy changed nothing.  Removed 2026-08-16; the live table is
# the recessed one under "Corner stations" below.  Do not reintroduce a second
# binding of this name.

# --- LG-10.3/10.4: the gear bay seat, aperture and bolt bosses --------------
#
# WHY THIS IS BUILT IN THE BAY'S PLATE FRAME, NOT ON THE PANEL NORMAL
# ------------------------------------------------------------------
# SS2.4a says to aim the bay bolts normal to the sponson's trapezoidal flat.
# That is not achievable, and the measurement says so plainly.  The bay's
# orientation is fixed by the leg: the hip pin axis is leg-local Y and the
# corner's swing azimuth is fixed by the CANONICAL FOOT STATIONS.  The panel
# normal is fixed by the sponson's shape.  Those two disagree by a YAW of
# 21-24 deg at every corner, and no value of BAY_CANT removes it -- a cant is
# a rotation about Y and the residual is about Z:
#
#     BAY_CANT -11.5   bolt axis 26.2 deg (fore) / 29.2 deg (aft) off normal
#     BAY_CANT -25.66  bolt axis 21.1 deg (fore) / 24.4 deg (aft) off normal
#
# Yawing the leg to close it moves the feet 32 mm off their canonical stations,
# which is the one thing SS2.2 will not trade.  So the hull gives the bay a
# printed SEAT instead: a flange-shaped collar whose face is normal to the bolt
# axis by construction, recessed into the sponson.  The bolts are then normal
# to their own bearing face -- which is what bolt bearing, head seating and
# boss depth actually require -- and the panel normal is used only to LOCATE
# the opening, never to orient the mount.  This is the "hollow/reinforce the
# sponson for the attachment" of LG-10.4.
#
# Everything below is a CONTRACT with canonical_leg_r6_*.scad.  Change one,
# change both; the aperture here must match the liner there exactly or the leg
# will not pass through its own bay.
X_CL_HULL = -169.9          # hull centreline
BAY_APER_W_BOT = 25.0       # mm, aperture width at the mouth
BAY_APER_W_TOP = 34.0       # mm, aperture width at the head
BAY_APER_L = 58.0           # mm, aperture length up the canted plane
BAY_APER_ZB0 = -38.0        # mm, aperture bottom edge, plate frame
BAY_FLANGE = 10.0           # mm, bolt flange width all round the aperture
BAY_PLATE_W = BAY_APER_W_TOP + 2 * BAY_FLANGE      # 54
BAY_PLATE_WB = BAY_APER_W_BOT + 2 * BAY_FLANGE     # 45
BAY_PLATE_L = BAY_APER_L + 2 * BAY_FLANGE          # 78
BAY_PLATE_ZB0 = BAY_APER_ZB0 - BAY_FLANGE          # -48
BAY_BOLT_ZB = (BAY_PLATE_ZB0 + BAY_FLANGE / 2.0,
               BAY_PLATE_ZB0 + BAY_PLATE_L - BAY_FLANGE / 2.0)     # -43, +25
BAY_BOLT_YB = ((BAY_APER_W_BOT + BAY_FLANGE) / 2.0,
               (BAY_APER_W_TOP + BAY_FLANGE) / 2.0)                # 17.5, 22
BAY_PLATE_T = 5.0           # frame thickness (depth of the flange rebate)
COWL_H = 7.0                # liner depth inboard of the frame
BAY_CANT = -11.5            # deg
LG_PLATE_Z0 = 12.0          # plate origin above the hip, leg-local
BAY_STANDOFF = {"fore": 12.6, "aft": 5.4}   # skin standoff, post-recess

LG_SEAT_D = 8.0             # mm, collar depth inboard of the flange (bolt bite)
LG_FIT_CLR = 0.4            # mm, assembly clearance on the rebate and aperture
LG_M3_D = 3.4               # M3 clearance through-bore

# Measured sponson panel (tools/landing_gear_opening_fit.py).  Retained ONLY to
# locate/report the opening -- it no longer orients anything.
# NOTE the starboard sign: mirroring across the centreline flips X and leaves Y
# alone.  This table previously negated BOTH, which is a 180 deg rotation about
# Z, not a mirror, and it broke the port/stbd symmetry of every derived yaw.
LG_PANEL_N = {"port": np.array([0.901, 0.015, -0.433]),
              "stbd": np.array([-0.901, 0.015, -0.433])}

# Corner stations, RECESSED 15 mm along each corner's own swing axis (LG-10.2).
# (label, hip_x, hip_y, hip_z, swing_azimuth_deg, station)
LG_CORNERS = [
    ("fore-port", -103.87, -1.28, 38.0, -22.4, "fore"),
    ("fore-stbd", -235.93, -1.28, 38.0, -157.6, "fore"),
    ("aft-port", -92.24, 99.96, 38.0, 28.0, "aft"),
    ("aft-stbd", -247.56, 99.96, 38.0, 152.0, "aft"),
]

# Retained as an informational clearance check.
LEG_ZONES = [
    (label, (hx - 25.0, hx + 25.0, hy - 30.0, hy + 30.0, 10.0, 60.0))
    for label, hx, hy, _hz, _az, _st in LG_CORNERS
]

LG_BAY_ENABLED = True


# --- LG-10.4: the wing keep-outs the bay must respect ----------------------
#
# The sponson spans the wing-root station, so a bay footprint and the wing
# mount compete for the same block of hull.  Measured 2026-08-16
# (tools/landing_gear_wing_clearance.py) before any of this was enforced:
#
#   fore rebate  x spar boss    45 / 105 mm^3, 2.26-3.14 mm radially
#                               -> bearing wall 4.85 -> 2.59 mm over ~7 mm
#   fore rebate  x servo pad    52 / 89 mm^3, 3.44-4.29 mm deep
#   aft collar   x mortise      347 / 349 mm^3, 4.13 mm across the FULL
#                               20.8 mm mortise height -- the wing-root tenon
#                               would not enter at assembly
#   fore collar  x spar bore    2.7 mm^3, 0.84 mm -- the spar rod would not
#                               slide through
#
# Resolution: on the HULL the wing always wins.  The bay's cuts stop at wing
# material and the bay's added material stops at wing voids.  The residual fit
# error is taken on the PRINTED bay frame instead (a local relief pocket in
# canonical_leg_r6_*.scad), because relieving a 5 mm printed flange is free and
# thinning a spar bearing is not.
#
# Bay BOLT BORES are deliberately NOT trimmed: a blocked M3 bore is a hard
# assembly failure, and the bores were verified to miss every nacelle-servo M3
# pilot bore by construction (0.000 mm^3 overlap).  They clip the servo pad
# edge by 7.7-14.5 mm^3, which is accepted and recorded here.


def wing_keepout_positives(envelope_tm=None):
    """Wing material the gear bay's cuts must not remove.  (label, solid).

    Pass `envelope_tm` -- main() already has it.  These are DEEP features that
    only become real where they meet the skin (main() adds them as
    `positives ^ envelope`), so an unclipped solid runs far outboard of the
    hull into open air.  Protecting the raw box measured 9-11 mm of phantom
    proud material under the fore flanges; clipped, the real figure is what
    the flange must actually clear.  Unclipped is for reporting only.
    """
    raw = [
        ("spar boss port", x_cylinder(
            WING_SPAR_Y, WING_SPAR_Z, PORT_INB, PORT_OUTB,
            WING_SPAR_BOSS_OD / 2.0)),
        ("spar boss stbd", x_cylinder(
            WING_SPAR_Y, WING_SPAR_Z, STBD_OUTB, STBD_INB,
            WING_SPAR_BOSS_OD / 2.0)),
        ("servo pad port", box(
            PORT_INB, PORT_OUTB,
            NSVMT_Y - NSVMT_PAD_W / 2, NSVMT_Y + NSVMT_PAD_W / 2,
            NSVMT_Z - NSVMT_PAD_H / 2, NSVMT_Z + NSVMT_PAD_H / 2)),
        ("servo pad stbd", box(
            STBD_OUTB, STBD_INB,
            NSVMT_Y - NSVMT_PAD_W / 2, NSVMT_Y + NSVMT_PAD_W / 2,
            NSVMT_Z - NSVMT_PAD_H / 2, NSVMT_Z + NSVMT_PAD_H / 2)),
    ]
    if envelope_tm is None:
        return raw
    env = to_man(envelope_tm)
    clipped = []
    for label, solid in raw:
        got = from_man(to_man(solid) ^ env)
        if len(got.faces):
            clipped.append((label, got))
    return clipped


def wing_keepout_negatives():
    """Wing voids the gear bay's added material must not intrude into."""
    my0, my1 = WING_MORT_Y - MORT_W / 2, WING_MORT_Y + MORT_W / 2
    mz0, mz1 = WING_ROOT_Z - MORT_H / 2, WING_ROOT_Z + MORT_H / 2
    return [
        ("spar bore", x_cylinder(
            WING_SPAR_Y, WING_SPAR_Z, -270.0, -70.0, WING_SPAR_BORE_D / 2.0)),
        ("mortise port", box(
            PORT_INB + 1.0, PORT_OUTB - 10.0, my0, my1, mz0, mz1)),
        ("mortise stbd", box(
            STBD_OUTB + 8.0, STBD_INB - 1.0, my0, my1, mz0, mz1)),
    ]


def _subtract_all(solid, keepouts):
    """solid minus every keep-out, as a trimesh.  Returns (mesh, removed_mm3).

    Returns the ORIGINAL solid untouched when nothing intersects, so the
    common case costs one AABB test per keep-out and no boolean at all.
    """
    smin, smax = solid.bounds
    hits = [k for _lbl, k in keepouts
            if not ((smin > k.bounds[1]).any() or (k.bounds[0] > smax).any())]
    if not hits:
        return solid, 0.0
    acc = to_man(solid)
    before = abs(solid.volume)
    for k in hits:
        acc = acc - to_man(k)
    trimmed = from_man(acc)
    if len(trimmed.faces) == 0:
        return solid, 0.0
    return trimmed, before - abs(trimmed.volume)


def _plate_frame(hx, hy, hz, az_deg, station):
    """(origin, e_x, e_y, e_z) of one bay's plate frame, in HULL coords.

    Mirrors the OpenSCAD construction exactly:
        translate([BAY_BACK_X, 0, LG_PLATE_Z0]) rotate([0, -BAY_CANT, 0])
    then the corner's own rotate([0, 0, az]) and translate to the hip.
    OpenSCAD's rotate([0, a, 0]) maps x -> (cos a, 0, -sin a).
    """
    a = np.radians(-BAY_CANT)
    ex_l = np.array([np.cos(a), 0.0, -np.sin(a)])
    ey_l = np.array([0.0, 1.0, 0.0])
    ez_l = np.array([np.sin(a), 0.0, np.cos(a)])
    p0_l = np.array([BAY_STANDOFF[station] - BAY_PLATE_T, 0.0, LG_PLATE_Z0])

    t = np.radians(az_deg)
    rz = np.array([[np.cos(t), -np.sin(t), 0.0],
                   [np.sin(t), np.cos(t), 0.0],
                   [0.0, 0.0, 1.0]])
    hip = np.array([hx, hy, hz])
    return rz @ p0_l + hip, rz @ ex_l, rz @ ey_l, rz @ ez_l


def seat_offset(shell_tm, org, ex, ey, ez):
    """Plate-frame x at which the real skin sits under a bay's flange footprint.

    BAY_STANDOFF was measured along the SS2.4a PANEL NORMAL, but the plate's own
    axis e_x is 21-24 deg off that normal (see the yaw note above), so applying
    the standoff along e_x overshoots and leaves the seat hanging outside the
    hull -- it lands only 11-15% inside the envelope.  Measure it in the frame
    that actually places the part instead of deriving it in a different one.

    Returns (x_median, x_p10, x_p90).  The spread is the footprint's real
    curvature: a FLAT seat can only be justified while it stays small, and it is
    what LG-10.6's conforming patch removes.
    """
    v = shell_tm.vertices - org
    u = v @ ey
    w = v @ ez
    x = v @ ex
    zb1 = BAY_PLATE_ZB0 + BAY_PLATE_L
    # inside the trapezoid, with the half-width interpolated along its run
    frac = np.clip((w - BAY_PLATE_ZB0) / BAY_PLATE_L, 0.0, 1.0)
    half = (BAY_PLATE_WB + frac * (BAY_PLATE_W - BAY_PLATE_WB)) / 2.0
    sel = (w > BAY_PLATE_ZB0) & (w < zb1) & (np.abs(u) < half) & (np.abs(x) < 60.0)
    if sel.sum() < 20:
        return None
    xs = x[sel]
    # the OUTBOARD skin is the far side of the distribution; the near cluster is
    # the opposite wall of the shell
    outer = xs[xs > np.median(xs)]
    return (float(np.median(outer)), float(np.percentile(outer, 10)),
            float(np.percentile(outer, 90)))


def station_seat_data(shell_tm):
    """Measure every bay's seat, and reduce it to ONE datum per station.

    Returns ``(seats, station_x0)``:
      * ``seats[label]``  -> the raw ``seat_offset()`` triple for that corner
        (median, p10, p90) in that corner's own plate frame.  Corners with no
        skin under the flange footprint are absent.
      * ``station_x0[station]`` -> the plate-frame x the hull's seat face and
        flange-rebate floor are cut to, for BOTH corners of that station: the
        p10 of the DEEPER of the two.

    Single-sourced here because two things must agree on it and they live in
    different files: this module cuts the hull to it, and
    ``canonical_leg_r6_*.scad`` places the printed bay against it via
    ``BAY_STANDOFF``.  ``tools/landing_gear_bay_seat_fit.py`` gates the pair.
    The required SCAD value is ``BAY_STANDOFF[station] + station_x0[station]``.
    """
    seats = {}
    for label, hx, hy, hz, az, station in LG_CORNERS:
        got = seat_offset(shell_tm, *_plate_frame(hx, hy, hz, az, station))
        if got is not None:
            seats[label] = got
    station_x0 = {}
    for label, _hx, _hy, _hz, _az, station in LG_CORNERS:
        if label in seats:
            lo = seats[label][1]
            station_x0[station] = min(station_x0.get(station, lo), lo)
    return seats, station_x0


def _plate_trap(org, ex, ey, ez, w_bot, w_top, zb0, zb1, x0, x1):
    """Trapezoidal prism in a bay's plate frame (widths along ey, run along ez,
    extruded x0..x1 along ex)."""
    quad = [(-w_bot / 2.0, zb0), (w_bot / 2.0, zb0),
            (w_top / 2.0, zb1), (-w_top / 2.0, zb1)]
    pts = [org + ey * u + ez * v + ex * xx
           for xx in (x0, x1) for u, v in quad]
    return trimesh.convex.convex_hull(trimesh.PointCloud(np.array(pts)))


def lg_bay_features(shell_tm, envelope_tm=None):
    """Return (positives, negatives, note) for the four landing-gear bays.

    positives: one seat collar per corner, sunk inboard of the flange rebate.
               Envelope-clipped by main(), so it conforms to the real wall.
    negatives: the aperture (through), the flange rebate (so the frame sits
               flush with the skin), and 4 M3 bores per corner.

    `envelope_tm` clips the LG-10.4 wing keep-outs to material that really
    exists.  Without it the deep spar-boss/servo-pad solids reach far outboard
    of the skin and would protect open air, leaving the flange footprint
    9-11 mm proud instead of the true figure.
    """
    if not LG_BAY_ENABLED:
        return [], [], "landing-gear bays DISABLED"
    keep_pos = wing_keepout_positives(envelope_tm)
    keep_neg = wing_keepout_negatives()
    pos, neg, report = [], [], []

    # --- LG-10.6: ONE seat datum per station -------------------------------
    #
    # Seat the frame on the MEASURED skin, not on a standoff carried over from
    # a different frame.  Seat at the MOST INBOARD decile of the skin over the
    # footprint, not at its median: the footprint is doubly curved (10.2-10.8
    # mm of relief across it, more than the seat's own 8 mm depth), so seating
    # on the median leaves most of the collar hanging outboard of the skin --
    # it kept only 11-17% of its volume inside the envelope.  Seating on the
    # inboard decile buries the collar and lets the flange rebate cut away the
    # skin that stands proud, which is the "hollow the sponson for the
    # attachment" half of LG-10.4.
    #
    # The datum is taken PER STATION (the deepest of that station's two
    # corners), not per corner.  Per-corner seating gave the two fore pockets
    # floors 1.14 mm apart, and the printed bay is ONE part per station -- so
    # it could seat on at most one of them and the other kept a gap.  Cutting
    # both fore pockets to the deeper of the two costs 1.14 mm of extra hull
    # relief at fore-port (the rebate already cuts ~15 mm at the proud corner)
    # and buys a bay that seats on both sides.  This is what keeps the SS11.4
    # shared-BOM claim true: fore part + aft part, each a mirrored pair.
    seats, station_x0 = station_seat_data(shell_tm)
    for label, _hx, _hy, _hz, _az, _station in LG_CORNERS:
        if label not in seats:
            report.append(f"{label}: NO SKIN under the flange footprint")
    for station, x0 in sorted(station_x0.items()):
        report.append(
            f"{station} station datum x0 {x0:+.2f} mm  ->  "
            f"canonical_leg_r6_*.scad BAY_STANDOFF[{station}] must be "
            f"{BAY_STANDOFF[station] + x0:.2f} "
            f"(declared {BAY_STANDOFF[station]:.1f})")

    for label, hx, hy, hz, az, station in LG_CORNERS:
        if label not in seats:
            continue
        org, ex, ey, ez = _plate_frame(hx, hy, hz, az, station)
        zb1 = BAY_PLATE_ZB0 + BAY_PLATE_L

        x_med, lo, hi = seats[label]
        x0 = station_x0[station]
        org = org + ex * x0
        report.append(f"{label} {station}: seat x {x0:+.1f} mm "
                      f"(median {x_med:+.1f}), footprint relief {hi - lo:.1f} mm, "
                      f"rebate cuts {hi - x0 + BAY_PLATE_T:.1f} mm at the "
                      f"proud corner, over-relief {lo - x0:.2f} mm")

        # Seat collar: the bolts' bearing material, inboard of the flange.
        # LG-10.4: trimmed clear of the spar bore and the wing-root mortises,
        # so the collar can never block the spar rod or the root tenon.
        collar, cut_v = _subtract_all(
            _plate_trap(org, ex, ey, ez,
                        BAY_PLATE_WB, BAY_PLATE_W,
                        BAY_PLATE_ZB0, zb1,
                        -LG_SEAT_D, 0.0),
            keep_neg)
        pos.append(collar)
        if cut_v > 0.0:
            report.append(f"{label}: collar relieved {cut_v:.1f} mm^3 "
                          f"around the wing void")

        # Aperture, straight through -- the liner runs COWL_H inboard.
        # LG-10.4: stops at wing material rather than eating into it.
        aper, aper_v = _subtract_all(
            _plate_trap(org, ex, ey, ez,
                        BAY_APER_W_BOT + 2 * LG_FIT_CLR,
                        BAY_APER_W_TOP + 2 * LG_FIT_CLR,
                        BAY_APER_ZB0 - LG_FIT_CLR, zb1 + LG_FIT_CLR,
                        -(COWL_H + 6.0), 12.0),
            keep_pos)
        neg.append(aper)

        # Flange rebate: BAY_PLATE_T deep, so the frame finishes flush.
        # LG-10.4: likewise stops at wing material.  Where it does, the skin
        # is left proud and the PRINTED frame carries the relief instead.
        rebate, reb_v = _subtract_all(
            _plate_trap(org, ex, ey, ez,
                        BAY_PLATE_WB + 2 * LG_FIT_CLR,
                        BAY_PLATE_W + 2 * LG_FIT_CLR,
                        BAY_PLATE_ZB0 - LG_FIT_CLR, zb1 + LG_FIT_CLR,
                        0.0, 12.0),
            keep_pos)
        neg.append(rebate)
        if aper_v + reb_v > 0.0:
            report.append(f"{label}: {aper_v + reb_v:.1f} mm^3 of wing "
                          f"material protected from the bay cuts")

        # 4x M3, on the flange centreline, following the trapezoid.
        for i in (0, 1):
            for s in (-1.0, 1.0):
                pt = (org + ey * (s * BAY_BOLT_YB[i])
                      + ez * BAY_BOLT_ZB[i])
                neg.append(axis_cylinder(pt, ex, -LG_SEAT_D - 8.0, 12.0,
                                         LG_M3_D / 2.0))

    note = (f"{len(pos)} bay seat collars + {len(neg)} cuts "
            f"(aperture, flange rebate, 16 M3 bores)")
    for line in report:
        note += f"\n        {line}"
    return pos, neg, note


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def bake(mesh):
    """Apply the Cargo_Shell hull-frame bake transform (180° about Z + T)."""
    v = mesh.vertices.copy()
    v[:, 0] = -v[:, 0] + BAKE_T[0]
    v[:, 1] = -v[:, 1] + BAKE_T[1]
    v[:, 2] = v[:, 2] + BAKE_T[2]
    return trimesh.Trimesh(vertices=v, faces=mesh.faces, process=False)


def build_negatives(shell_tm, envelope_tm=None):
    """Return (cutters, notes)."""
    cutters, notes = [], []

    cutters.append(box(*DUCT_CUT))
    notes.append("interior-wall duct removal")
    cutters.append(box(*APERTURE))
    notes.append("clamshell belly aperture")

    # Open the fwd + aft mating faces with a FLAT half-space cut at each mating
    # plane (asf._flat_face_cutter): it removes the rounded closure cap the
    # hollowing left, leaving a clean flat OPEN tube the splice collar slips into
    # — no ragged fragments and no dorsal bite (a plane can't make them), and the
    # bore stays genuinely open (JOINT-01 fix superseded 2026-07-06: the lofted
    # bore-open cutter cleaned the rim but never removed the cap, so the collar
    # still passed through solid plastic — see TODO.md).
    cutters.append(asf._flat_face_cutter(shell_tm, "cargo_fwd"))
    notes.append("flat OPEN fwd mating face (head/cargo)")
    cutters.append(asf._flat_face_cutter(shell_tm, "cargo_aft"))
    notes.append("flat OPEN aft mating face (cargo/middle)")

    # Joint 1 + Joint 2 boss-pin bores REMOVED 2026-07-06 (user directive):
    # the head/cargo and cargo/middle splice collars now secure AND align these
    # joints, so no dowel bores are cut into the cargo shell (see
    # add_structural_features.py module docstring, and docs/structural_analysis.md
    # §7.3 — the pins had already been re-roled from load-bearing to alignment-only
    # when the collars were introduced).

    # Keel locating channel + Y=+30 ring-frame pocket.
    kc = asf.KEEL_CHANNEL["cargo"]
    cutters.append(
        box(
            kc["x_range"][0],
            kc["x_range"][1],
            kc["y_range"][0],
            kc["y_range"][1],
            kc["z_range"][0],
            kc["z_range"][1],
        )
    )
    notes.append("keel channel")
    for xm, xx, zm, zx, ym, yx in asf.RING_POCKETS["cargo_Y30"]:
        cutters.append(box(xm, xx, ym, yx, zm, zx))
    notes.append("ring pocket Y=30")

    # Wing spar bore (full lateral span) + 2 root mortises (through each wall).
    # Built by wing_keepout_negatives() so the solids the gear bay is trimmed
    # against are the SAME solids the hull is actually cut with (LG-10.4).
    for label, solid in wing_keepout_negatives():
        cutters.append(solid)
        notes.append(f"wing {label}")

    # Nacelle-servo M3 heat-set pilot bores (into the cavity face of each pad).
    for x_in, x_out in ((PORT_INB, PORT_INB + 8.0), (STBD_INB, STBD_INB - 8.0)):
        for dy in (-NSVMT_HOLE_S_Y, NSVMT_HOLE_S_Y):
            for dz in (-NSVMT_HOLE_S_Z, NSVMT_HOLE_S_Z):
                cutters.append(
                    x_cylinder(
                        NSVMT_Y + dy,
                        NSVMT_Z + dz,
                        min(x_in, x_out),
                        max(x_in, x_out),
                        NSVMT_M3_D / 2.0,
                    )
                )
    notes.append("servo M3 pilot bores")

    _lg_pos, lg_neg, lg_note = lg_bay_features(shell_tm, envelope_tm)
    cutters.extend(lg_neg)
    notes.append(lg_note)

    return cutters, notes


def build_positives(shell_tm, envelope_tm=None):
    """Return (raw deep features, notes).  Clipped to the envelope in main()."""
    feats, notes = [], []

    for side in ("port", "stbd"):
        for station in ("fwd", "aft"):
            feats.append(hinge._block(side, station))
    notes.append("4 hinge retention blocks")

    # Wing-spar bearing bosses (Ø22, coaxial with the spar) and the two
    # nacelle-servo mount pads -- deep boxes/cylinders, envelope-clipped.
    # Built by wing_keepout_positives() so the solids the gear bay is trimmed
    # against are the SAME solids the hull actually carries (LG-10.4).
    for _label, solid in wing_keepout_positives():  # raw: main() clips
        feats.append(solid)
    notes.append("2 wing-spar bearing bosses")
    notes.append("2 nacelle-servo mount pads")

    # Inara avionics-bay standoff bosses (dorsal port, deep Z-cyl, clipped).
    n = 0
    for dx in (-INARA_BOSS_DX, INARA_BOSS_DX):
        for dy in (-INARA_BOSS_DY, INARA_BOSS_DY):
            body = z_cylinder(
                INARA_X + dx, INARA_Y + dy, DORSAL_Z_INB, DORSAL_Z_TOP, BOSS_OD / 2.0
            )
            bore = z_cylinder(
                INARA_X + dx,
                INARA_Y + dy,
                DORSAL_Z_INB - 0.1,
                DORSAL_Z_TOP + 0.1,
                BOSS_BORE_D / 2.0,
            )
            feats.append(from_man(to_man(body) - to_man(bore)))
            n += 1
    notes.append(f"Inara avionics bosses ({n})")

    lg_pos, _lg_neg, lg_note = lg_bay_features(shell_tm, envelope_tm)
    feats.extend(lg_pos)
    notes.append(lg_note)

    return feats, notes


def stamp_export(mesh, out_path):
    """Write binary STL with the HULL-FRAME R1 marker in the 80-byte header."""
    count = len(mesh.faces)
    tris = mesh.vertices[mesh.faces]
    e1 = tris[:, 1, :] - tris[:, 0, :]
    e2 = tris[:, 2, :] - tris[:, 0, :]
    normals = np.cross(e1, e2)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    safe = np.where(lengths > 0.0, lengths, 1.0)
    normals = np.where(lengths > 0.0, normals / safe, 0.0)
    rec_dtype = np.dtype([("data", "<f4", (12,)), ("attr", "<u2")])
    rec = np.zeros(count, dtype=rec_dtype)
    rec["data"][:, 0:3] = normals.astype("<f4")
    rec["data"][:, 3:12] = tris.reshape(count, 9).astype("<f4")
    header = (MARKER + b" Cargo_Shell interior-merge 2026-06-30")[:80].ljust(80, b"\0")
    with open(out_path, "wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", count))
        fh.write(rec.tobytes())


def check_leg_clearance(mesh):
    """Report whether merged geometry intrudes into the deferred leg-mount
    keep-out zones (informational — leg bosses are Rev R5 future work)."""
    print("\n--- landing-gear leg-mount clearance (deferred; keep-out check) ---")
    v = mesh.vertices
    for name, (x0, x1, y0, y1, z0, z1) in LEG_ZONES:
        inside = (
            (v[:, 0] >= x0)
            & (v[:, 0] <= x1)
            & (v[:, 1] >= y0)
            & (v[:, 1] <= y1)
            & (v[:, 2] >= z0)
            & (v[:, 2] <= z1)
        )
        n = int(inside.sum())
        tag = "clear (skin only)" if n < 4000 else "REVIEW: dense geometry"
        print(
            f"  {name:9s} X[{x0:.0f},{x1:.0f}] Y[{y0:.0f},{y1:.0f}] "
            f"Z[{z0:.0f},{z1:.0f}]: {n} shell verts — {tag}"
        )


def drop_slivers(mesh, min_faces=64):
    """Drop the tiny (1–2 face, zero-area) degenerate components manifold3d can
    leave at cut intersections, so the result is a single clean solid body."""
    comps = trimesh.graph.connected_components(
        mesh.face_adjacency, nodes=np.arange(len(mesh.faces))
    )
    keep = [c for c in comps if len(c) >= min_faces]
    dropped = len(comps) - len(keep)
    if dropped:
        idx = np.concatenate(keep)
        mesh = mesh.submesh([idx], append=True)
        print(
            f"  dropped {dropped} zero-area sliver fragment(s) "
            f"→ {len(keep)} body/bodies"
        )
    return mesh


def verify(mesh):
    ec = np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique))
    boundary = int((ec == 1).sum())
    nonman = int((ec > 2).sum())
    wt = mesh.is_watertight
    wind = mesh.is_winding_consistent
    vol = mesh.volume
    bodies = len(
        trimesh.graph.connected_components(
            mesh.face_adjacency, nodes=np.arange(len(mesh.faces))
        )
    )
    print("\n=== verify (final cargo shell) ===")
    print(
        f"  faces={len(mesh.faces):,}  bodies={bodies}  "
        f"watertight={wt}  winding={wind}"
    )
    print(f"  boundary_edges={boundary}  nonmanifold_edges={nonman}")
    print(
        f"  volume={vol:.0f} mm^3  "
        f"mass={vol * RHO_PRINT:.1f} g (as-printed) .. "
        f"{vol * RHO_SOLID:.1f} g (solid CF-PETG)"
    )
    ok = wt and wind and boundary == 0 and nonman == 0 and vol > 0
    print(f"  RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def close_zero_area_slits(mesh, flat_mm=SLIT_FLAT_MM):
    """Close boundary loops that enclose no area, and report how many.

    manifold3d can leave a T-junction on a nearly-coplanar boolean seam: the
    seam vertex splits one edge of a neighbouring triangle, that triangle
    strips out as degenerate, and what is left is a SLIT -- a boundary loop
    whose vertices are exactly collinear.  Geometrically the surface is still
    closed (the slit has zero width); topologically it is a hole, and
    `tools/validate_stls.py` fails it.

    `trimesh.repair.fill_holes` cannot close one, because the triangle it would
    have to add has zero area and is rejected.  Collapsing the loop to a single
    vertex does close it, and removes no material: the faces that vanish are
    exactly the zero-area ones.

    Only loops flatter than `flat_mm` are touched -- measured as the SECOND
    singular value of the loop's vertices, i.e. its width away from the
    best-fit line.  A real hole has width and is left open, so it still fails
    loudly in verify() instead of being silently papered over.
    """
    uniq, cnt = np.unique(mesh.edges_sorted, axis=0, return_counts=True)
    bnd = uniq[cnt == 1]
    if not len(bnd):
        return mesh, 0
    remap = np.arange(len(mesh.vertices))
    closed = 0
    for vids in trimesh.graph.connected_components(bnd):
        if len(vids) < 3:
            continue
        pts = mesh.vertices[vids]
        # singular values of the centred loop: s[1] is its off-line width
        sv = np.linalg.svd(pts - pts.mean(axis=0), compute_uv=False)
        if len(sv) > 1 and sv[1] > flat_mm:
            continue
        remap[vids] = vids[0]
        closed += 1
    if not closed:
        return mesh, 0
    out = trimesh.Trimesh(vertices=mesh.vertices.copy(),
                          faces=remap[mesh.faces], process=False)
    out.update_faces(out.nondegenerate_faces())
    out.update_faces(out.unique_faces())
    out.remove_unreferenced_vertices()
    return out, closed


def finalize_watertight(mesh):
    """Weld float32-coincident boolean-seam vertices, strip the resulting
    degenerate/duplicate faces, and keep the single largest body — so the mesh
    stays a clean watertight 2-manifold AFTER the binary-STL round-trip.

    Ordering matters: WELD (merge_vertices) FIRST, then strip degenerate faces.
    An earlier revision skipped this and noted that nondegenerate_faces() alone
    "opens ~120 boundary holes"; that is true only when the coincident
    boolean-seam vertices have NOT been welded first — the faces bordering them
    are not yet zero-area, so stripping them tears the surface.  After a weld
    pass those seam duplicates collapse to true zero-area faces that strip
    cleanly, closing the ~48 non-manifold seam edges the float32 export
    otherwise leaves.  Verified 2026-07-21: watertight=True, 1 body, volume and
    bounds identical to the pre-finalize mesh (only zero-area junk removed)."""
    mesh.merge_vertices()
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    # ALWAYS rebuild from the largest split body — trimesh's submesh() re-welds
    # coincident vertices, which closes the tiny (≤3-edge) seams the degenerate
    # strip opens AND drops the zero-area sliver bodies, in one step.  (Returning
    # the un-split mesh when there is a single body leaves those seams open;
    # verified 2026-07-21.)  Do NOT add a trailing merge_vertices() — a second
    # weld pass reopens a seam.
    bodies = mesh.split(only_watertight=False)
    if bodies:
        big = max(bodies, key=lambda b: len(b.faces))
        if len(bodies) > 1:
            print(
                f"  finalize: kept largest of {len(bodies)} bodies "
                f"({len(big.faces):,} faces); dropped {len(bodies) - 1} "
                f"zero-area sliver body/bodies"
            )
        mesh = big
    # Insurance: close any residual small holes so the result is a true 2-manifold.
    # Zero-area slits FIRST -- fill_holes cannot close those (see the helper),
    # and leaving one open fails the CI watertight gate.
    if not mesh.is_watertight:
        mesh, n_slit = close_zero_area_slits(mesh)
        if n_slit:
            print(f"  finalize: closed {n_slit} zero-area collinear slit(s)")
    if not mesh.is_watertight:
        trimesh.repair.fill_holes(mesh)
    trimesh.repair.fix_normals(mesh)
    return mesh


def repair_exported(out_path):
    """Reload the exported cargo STL, weld+clean it to a watertight single body,
    and re-stamp the HULL-FRAME marker.  Runs WITHOUT Blender, so it serves both
    as the tail of the full merge (guaranteeing the ON-DISK file is clean, not
    just the in-memory float64 result) and as a standalone ``--repair-only``
    pass on an already-published cargo STL."""
    print(f"\n=== repair_exported (float32 round-trip finalize): {out_path} ===")
    m = trimesh.load(out_path, process=False)
    m.merge_vertices()
    print(f"  reloaded+welded: watertight={m.is_watertight} faces={len(m.faces):,}")
    m = finalize_watertight(m)
    verify(m)  # in-memory result
    stamp_export(m, out_path)
    print(f"  re-stamped -> {out_path}")

    # Definitive check: reload the WRITTEN file exactly the way tools/validate_stls.py
    # (CI) does — process=True merges coincident float32 vertices on load — and
    # confirm the on-disk artifact is a valid watertight 2-manifold.
    chk = trimesh.load(out_path, force="mesh")
    bodies = chk.split(only_watertight=False)
    ci_ok = chk.is_watertight or (bodies and all(b.is_watertight for b in bodies))
    print(
        f"  on-disk CI-style reload: watertight={chk.is_watertight} "
        f"bodies={len(bodies)}  CI_valid={bool(ci_ok)}"
    )
    return bool(ci_ok)


def main():
    # Blender-free finalization: reload the published cargo STL and weld+clean it
    # to a watertight single body (MESH-01 float32 round-trip fix).  No re-merge.
    if "--repair-only" in sys.argv:
        ok = repair_exported(OUT_PATH)
        sys.exit(0 if ok else 1)

    print("=== merge_cargo_interior.py  Rev R2  2026-07-21 ===")
    print(f"source: {BLENDER_SRC}")
    src = trimesh.load(BLENDER_SRC, process=False)
    src.merge_vertices()
    print(
        f"  loaded {len(src.faces):,} faces  watertight={src.is_watertight}  "
        f"vol={src.volume:.0f} mm^3 (part-local)"
    )

    shell_tm = bake(src)
    b = shell_tm.bounds
    print(
        f"  baked hull frame: X {b[0][0]:.1f}..{b[1][0]:.1f}  "
        f"Y {b[0][1]:.1f}..{b[1][1]:.1f}  Z {b[0][2]:.1f}..{b[1][2]:.1f}"
    )

    envelope_tm = extract_envelope(shell_tm)
    eb = envelope_tm.bounds
    print(
        f"  outer-skin envelope: {len(envelope_tm.faces):,} faces  "
        f"watertight={envelope_tm.is_watertight}  "
        f"X {eb[0][0]:.1f}..{eb[1][0]:.1f}"
    )

    negs, nnotes = build_negatives(shell_tm, envelope_tm)
    poss, pnotes = build_positives(shell_tm, envelope_tm)
    print(f"\n  negatives ({len(negs)} cutters):")
    for n in nnotes:
        print(f"    - {n}")
    print(f"  positives ({len(poss)} features, envelope-clipped):")
    for n in pnotes:
        print(f"    - {n}")

    print("\n  evaluating (shell + (positives ∩ envelope)) − negatives …")
    shell_man = to_man(shell_tm)
    env_man = to_man(envelope_tm)
    pos_man = union_all(poss)
    neg_man = union_all(negs)
    result = shell_man
    if pos_man is not None:
        result = result + (pos_man ^ env_man)  # ^ = intersection in manifold3d
    if neg_man is not None:
        result = result - neg_man
    out = from_man(result)
    out = drop_slivers(out)

    # The in-memory float64 result is a clean watertight single body here, but
    # binary STL stores per-face vertices: the float32 export splits the
    # coincident boolean-seam vertices apart, so the RELOADED file fragments into
    # ~36 bodies with ~48 non-manifold seam edges and FAILS tools/validate_stls.py
    # (the CI watertight check).  This was previously mislabelled a "benign"
    # artifact; it is a real MESH-01 defect on the published STL.  We therefore
    # write the file, then reload + weld + clean it (repair_exported below) so the
    # ON-DISK artifact — not merely the in-memory mesh — is a watertight 2-manifold.
    verify(out)
    check_leg_clearance(out)

    stamp_export(out, OUT_PATH)
    print(f"\n  written -> {OUT_PATH}")
    print("  (already in hull frame + HULL-FRAME R1 marker; do NOT re-bake)")

    # Weld/clean the exported float32 file so the published STL passes CI.
    ok = repair_exported(OUT_PATH)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
