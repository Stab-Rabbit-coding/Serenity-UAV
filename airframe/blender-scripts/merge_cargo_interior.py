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
  * Wing spar F688ZZ bearing seat (Ø15.95 press-fit + Ø18.0 flange counterbore,
    REF-SENSOR-019) + Ø8.3 rotating-spar clearance, PER SIDE, terminating at
    the fuselage wall station (X −100 port / −240 stbd) instead of a full
    lateral-span bore -- CARGO-01/CARGO-02, closed 2026-08-24 per SPAR-01
    (airframe/wings-nacelles/WBS.md §1.1.2) -- + 2 wing-root mortises (through
    each lateral wall), at the RE-DERIVED chord stations (129 mm root chord, LE
    root hull Y=−7: spar 35% → Y=+38.15 at Z=68.42 (camber midline, Rev S1b);
    mortise 50% → Y=+57.5 at Z=62.5).
  * M3 heat-set bores in the nacelle-servo pads.

POSITIVE (added, envelope-clipped so they conform + fuse to the curved wall):
  * 4 clamshell hinge-pin retention blocks (from generate_cargo_hinge_retention).
  * 2 wing-spar bearing bosses (Ø27.7, coaxial with the spar bore -- re-derived
    2026-08-24 from the F688ZZ flange OD, REF-SENSOR-019, not the retired
    Ø22 press-fit figure).
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

# Mating-aperture allowlist (2026-09-05): the final defence against this
# pipeline's own repair passes re-capping cargo_fwd/cargo_aft. See
# tools/open_mating_faces.py's module docstring for why this is necessary —
# fill_holes()-style repair cannot tell an intentional open bore from a
# genuine defect, so every hull-shell pipeline must re-assert its known
# apertures are open as the LAST step before writing, not rely on getting
# there cleanly through repair.
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import open_mating_faces as omf  # noqa: E402

# Reuse the Rev R1c hull-frame hinge retention blocks verbatim
sys.path.insert(0, CARGO_DIR)
import generate_cargo_hinge_retention as hinge  # noqa: E402

# Reuse the wing SCAD's own S1223 table parser so this file's camber-midline
# figures are DERIVED, not hand-copied.  U6 (2026-08-25) root cause: the
# WING_*_MIDLINE constants below used to be one-time hand-computed snapshots
# ("midline_frac(45.15/129) * 129, from the wing SCAD") taken against the
# PRE-U1 S1223 table.  When U1 replaced that table with validated UIUC
# coordinates the wing's actual camber line moved (up to ~1.3 mm at some
# stations) but these constants were never refreshed, so the cargo shell's
# harness entry ports and spar bore were cut ~0.3-1.3 mm off the wing's real
# conduit centrelines -- tools/wing_root_deconflict.py caught this as
# "published cargo shell blocks <route>" and "spar bore does not penetrate
# the bulkhead".  Computing the midline here the same way
# tools/wing_root_deconflict.py does (via wing_spar_station_fit.surf_y()
# against the live SCAD table) makes drift like this structurally impossible.
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
sys.path.insert(0, TOOLS_DIR)
import wing_spar_station_fit as wsf  # noqa: E402


def _wing_midline_mm(chord_fraction):
    """S1223 camber midline (mm, at WING_ROOT_CHORD) at a chord fraction.

    Parsed live from wings_s1223_revo.scad's S1223_UPPER/S1223_LOWER tables,
    so this file and tools/wing_root_deconflict.py can never disagree about
    where the wing's own airfoil puts a station -- see note above.
    """
    with open(wsf.WING_SCAD, encoding="utf-8") as fh:
        src = fh.read()
    upper = wsf.scad_points(src, "S1223_UPPER")
    lower = wsf.scad_points(src, "S1223_LOWER")
    mid = (wsf.surf_y(upper, chord_fraction) + wsf.surf_y(lower, chord_fraction)) / 2.0
    return mid * WING_ROOT_CHORD

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

# REV T1 (2026-08-29): spar station 45.15 -> 28.00 mm aft of LE, and the spar
# itself changes KIND.  Through Rev S1b it was an 8 mm rotating drive shaft that
# the wing rode on; under Rev T1 it is a FIXED 20 x 16.3 mm CF tube bonded
# through the wing over its full span, and it is the wing's primary bending
# member (docs/WING_ATTACH_INTERFACE.md SS1).  The station is set by the wing,
# which moved to 28.00 mm to keep the O20.4 bore inside a skinnable section
# (wings_s1223_revo.scad SPAR_BORE_STATION); this file follows it.
#
# Keep WING_SPAR_STATION in step with SPAR_BORE_STATION in
# airframe/openscad/wings/wings_s1223_revo.scad -- they are the same physical
# tube and there is no other link between the two files.
WING_SPAR_STATION = 28.00                              # [mm] aft of the LE
WING_SPAR_Y = WING_LE_ROOT_Y + WING_SPAR_STATION       # = +21.00
WING_MORT_Y = WING_LE_ROOT_Y + 0.50 * WING_ROOT_CHORD  # = +57.5

# Mortise / nacelle-servo reference height.  NOT the spar height -- see below.

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

# CARGO-03b (2026-08-24): the wing root joint now has ONE datum.
# The tenon (`fuselage_root_tab()`) is centred on the wing CHORD LINE; this
# constant used to sit at 62.5, so the mortise was cut 4.49 mm above the tenon
# that enters it -- against a 0.4 mm/side design clearance, which put the tenon's
# lower 4.09 mm onto solid wall.  Both halves are now driven from the chord line.
# Only the mortise reads this (the spar and the servo pad are spar-relative), so
# moving it does not disturb anything else.
WING_ROOT_Z = WING_CHORD_LINE_Z
# U6 (2026-08-25): was a hand-copied snapshot (10.41 mm) taken against the
# pre-U1 S1223 table; now derived live from the SCAD's own table via
# _wing_midline_mm() so it tracks the corrected airfoil automatically -- see
# the note above _wing_midline_mm's definition.
# WA-R1: the spar rides the UNSCALED camber midline.  s1223_section() opens the
# thickness envelope ABOUT the camber line, so THICKNESS_SCALE does not move the
# bore centre -- applying it here would lift the socket 4.07 mm above the spar
# it is supposed to receive (docs/WING_ATTACH_INTERFACE.md SS3.2).
WING_SPAR_MIDLINE = _wing_midline_mm(WING_SPAR_STATION / WING_ROOT_CHORD)  # = 8.841
WING_SPAR_Z = WING_CHORD_LINE_Z + WING_SPAR_MIDLINE  # = +66.851

# WA-R1/WA-R2 (Rev T1, 2026-08-29): the socket is a BONDED/CLAMPED SEAT for a
# FIXED O20 CF tube, not a bearing seat for a rotating shaft.  The F688ZZ root
# bearing (ROOT_BRG_*) is DELETED, and deleting it is not a tidy-up: a bearing
# here would let the fixed spar spin under the tilt pinion's gear reaction,
# which is the one thing this joint must not allow
# (docs/WING_ATTACH_INTERFACE.md SS4.3b, WA-R2).
#
# The joint SPLITS BY LOAD TYPE (SS3.3), because the cargo bay caps socket depth
# at 18.67 mm and a socket's moment capacity goes as 1/L^2:
#   * SHEAR  -> this socket.  sigma = 115.1 N / (20 x 18.5) = 0.31 MPa, FOS 16.
#   * MOMENT -> the bonded root flange below (ROOT_FLANGE_*), FOS 29.2.
# Bore = 20.0 mm OD + 0.2 mm/side epoxy gap, matching the wing's own
# SPAR_BORE_OD / TILT_SPAR_BORE_CLEAR exactly -- same tube, same bond-gap law.
WING_SPAR_BORE_D = 20.4     # mm, bonded-socket bore = 20.0 OD + 0.2 mm/side

# Socket reach inboard of the wall.  BOUNDED, not chosen: the cargo bay's clear
# span begins at hull X -100 and the wall skin sits at X -81.33, so 18.67 mm is
# all there is; 18.5 is built (SS3.3).  The PORT_INB/STBD_INB wall brackets
# below already land at -100/-240, i.e. exactly this reach.
SPAR_SOCKET_REACH = 18.5    # mm, spanwise, inboard of the wall -- SHEAR only

# The four 10 AWG ESC feeds enter the spar's own hollow bore at the socket and
# must keep running inboard past the socket's end into the bay (SS2.3: four
# O5.5 conductors circumscribe 13.28 mm, the exact 1+sqrt(2) four-circle packing
# ratio, REF-MATH-001).  Continue the bore at the spar ID so the corridor the
# wires actually occupy is the corridor that is cut.
SPAR_WIRE_BORE_D = 16.3     # mm, = spar ID; carries the 13.28 mm bundle

# WA-R1b: bonded root flange on the INNER face of the sidewall, concentric with
# the socket -- the MOMENT path.  Triangular bearing pressure over height h with
# arm 2h/3 gives F = 3M/(2h); at h = 80 mm against the 14.60 N.m ultimate root
# moment that is 274 N over 1,600 mm^2 = 0.17 MPa, FOS 29.2 on the 5 MPa
# bond-limited CF-PETG figure (docs/structural_analysis.md SS7.3).  It reacts
# over wall AREA, so it needs NO inboard reach -- it protrudes only its own
# thickness, to X ~ -86, against a bay edge at -100.  That is what closes WA-R5.
ROOT_FLANGE_H = 80.0        # mm, hull Z extent
ROOT_FLANGE_W = 60.0        # mm, hull Y extent
ROOT_FLANGE_T = 5.0         # mm, protrusion inboard of the wall inner face

# Sidewall skin stations at the wing-root joint, measured 2026-08-29 against the
# published shell (docs/WING_ATTACH_INTERFACE.md SS3.3).  Every Rev T1 wing-root
# feature that has to reference "the wall" rather than a deep-embed bracket uses
# these, so one measured fact drives all of them.
WALL_SKIN_X_PORT = -81.33
WALL_SKIN_X_STBD = -258.37      # = 2 * X_CL - WALL_SKIN_X_PORT, X_CL = -169.85
WALL_INNER_X_PORT = WALL_SKIN_X_PORT - ROOT_FLANGE_T    # = -86.33
WALL_INNER_X_STBD = WALL_SKIN_X_STBD + ROOT_FLANGE_T    # = -253.37

# Boss OD carries the SAME 4.85 mm radial wall margin every wing-root boss in
# this file uses ((22.0-12.3)/2 at Rev S1), now over the O20.4 socket bore:
# 20.4 + 2*4.85 = 30.1 mm.  That also lands the boss on the ~O30 outside
# diameter WA-R3 specifies for the split-collar pinch clamp that grips the spar
# at this station, so the printed boss and the clamp share one envelope.
WING_SPAR_BOSS_OD = 30.1

# ---------------------------------------------------------------------------
# Wing root tie-rod couple — RETIRED at Rev T1 (2026-08-29)
# ---------------------------------------------------------------------------
# The two bonded CF tie rods (fwd O8.2 at station 14, aft O6.2 at station 62)
# existed only because a spar on bearings cannot react a moment, so the couple
# had to be closed by something else (U5/KTD1, FOS 4.14).  Under Rev T1 the spar
# is bonded and fixed, so it carries its own moment into the root flange, and
# the rods have no remaining job.  They are also no longer BUILDABLE: the wing
# gates them off (wings_s1223_revo.scad TENON_LOAD_PATH = "spar_carrythrough",
# whose comment records that the forward rod now intersects the O20.4 spar bore
# outright).  Keeping fuselage-side bosses and bores for rods the wing does not
# drill would leave four blind holes in the bulkhead and four keep-outs the
# landing-gear bay must respect for nothing.
#
# ROD_FWD_* / ROD_AFT_* constants, bosses and bores removed here; the design
# record stays in the wing SCAD's TENON_LOAD_PATH block and in
# airframe/fuselage-mid/WBS.md CARGO-03c / U5.

# Wing harness entry ports — Rev T1 bore set (WA-R6, 2026-08-29)
#
# The Rev S1c set (two O7 EDF "double-D" conduits at stations 22.75/32.25 plus
# one encoder lead at 54.0) is RETIRED.  Three things replaced it, and each is a
# consequence of the fixed spar rather than a preference:
#
#   1. The four 10 AWG ESC feeds no longer need their own wall ports at all.
#      They ride INSIDE the spar bore, on the tilt axis (SS1, SS2.3), and enter
#      the fuselage through the socket itself -- which is why SPAR_WIRE_BORE_D
#      exists above.  A O7 conduit could never have carried 10 AWG anyway; that
#      mismatch is what started the Rev T revision.
#   2. The nav 3-core moved out of the spar (the bore is now full of power) into
#      its own leading-edge conduit at station 8.0.
#   3. The AK7455 lead moved 54.0 -> 44.5 to make chordwise room at the wingtip,
#      and a THIRD spanwise bore appeared that never existed before: the tilt
#      drive shaft at station 53.6.
#
# Stations come from wings_s1223_revo.scad and MUST be kept in step with it --
# there is no other link between the two files, exactly as for WING_SPAR_STATION:
#   NAV_BORE_STATION    8.0   O3.2   nav 3-core
#   HALL_CABLE_STATION 44.5   O6.5   AK7455 shielded SPI
#   SHAFT_BORE_STATION 53.6   O4.4   tilt drive shaft
# Heights use the same unscaled-camber-midline rule as the spar, so all four
# wing-root penetrations are derived one way.
WING_NAV_STATION = 8.0
WING_ENC_STATION = 44.5
WING_SHAFT_STATION = 53.6

WING_NAV_MIDLINE = _wing_midline_mm(WING_NAV_STATION / WING_ROOT_CHORD)
WING_ENC_MIDLINE = _wing_midline_mm(WING_ENC_STATION / WING_ROOT_CHORD)
WING_SHAFT_MIDLINE = _wing_midline_mm(WING_SHAFT_STATION / WING_ROOT_CHORD)

WING_NAV_Y = WING_LE_ROOT_Y + WING_NAV_STATION       # = +1.00
WING_ENC_Y = WING_LE_ROOT_Y + WING_ENC_STATION       # = +37.50
WING_SHAFT_Y = WING_LE_ROOT_Y + WING_SHAFT_STATION   # = +46.60

# Wire ports are the wing conduit + 1.0 mm.  The oversize is deliberate and
# unchanged from Rev S1c: the root joint carries assembly tolerance in Y and Z,
# and a port that is merely flush leaves the wire pinched on the skin edge at
# the transition.  It costs nothing structurally -- these are through-skin holes
# in a 2 mm shell, not load paths.
#
# The DRIVE SHAFT bore is the exception and is NOT oversized: it is a running
# fit for a O4 steel shaft carried on bushings at both ribs, so it holds the
# wing's own O4.4 (O4 + 0.2 mm/side) figure.  Opening it "for tolerance" would
# put the shaft's own alignment into the skin, and shaft misalignment is what
# the bushings exist to prevent.
WING_NAV_ENTRY_D = 4.2     # wing conduit O3.2 + 1.0
WING_ENC_ENTRY_D = 7.5     # wing conduit O6.5 + 1.0
WING_SHAFT_ENTRY_D = 4.4   # = wings_s1223_revo.scad SHAFT_BORE_D, running fit

# Inboard end of the harness bores.  The lateral wall brackets used for the
# spar boss (PORT_INB -100 / STBD_INB -240) are NOT deep enough here: ray-tracing
# the merged shell showed a ~2.2 mm internal wall immediately inboard of them,
# whose outboard face sits at exactly -100.0 / -240.0 on the EDF-forward line and
# at -113.1 / -223.2 on the encoder line.  A bore that stops flush against that
# wall passes the skin and then dead-ends, which is the same failure this whole
# feature exists to remove -- just moved 17 mm inboard where it is harder to see.
#
# These values carry each bore past the deepest observed obstruction with margin,
# into open cargo cavity.  The spar bore already crosses the same region (it spans
# the full -270..-70 lateral run, because it is a continuous rod), so punching a
# harness bore through it is not a new intrusion into that wall.
WING_HARNESS_INB_PORT = -125.0   # past the -115.2 encoder-line wall
WING_HARNESS_INB_STBD = -213.0   # past the -225.2 encoder-line wall (stbd inboard is +X)

# Entry heights — same unscaled camber-midline rule as the spar.
WING_NAV_Z = WING_CHORD_LINE_Z + WING_NAV_MIDLINE       # = +61.974
WING_ENC_Z = WING_CHORD_LINE_Z + WING_ENC_MIDLINE       # = +68.689
WING_SHAFT_Z = WING_CHORD_LINE_Z + WING_SHAFT_MIDLINE   # = +69.090

# WA-R4 (Rev T1): mortise Y span 30.8 -> 12.8.  The tenon is a LOCATING feature
# at 12 x 20 x 8 mm now that the spar carries the moment
# (wings_s1223_revo.scad TENON_LOAD_PATH = "spar_carrythrough",
# WING_ROOT_TAB_W_LOCATING = 12.0); a 30.8 mm mortise is oversize for it by
# 18 mm and would let the wing rock in the one axis the tenon exists to fix.
# 0.4 mm/side clearance, unchanged -- that is the figure the CARGO-03b datum fix
# established and the tenon-fit check in tools/wing_root_deconflict.py asserts.
MORT_W = 12.8  # mortise Y span = 12.0 tenon + 0.4 mm/side
MORT_H = 20.8  # mortise Z span = 20.0 tenon + 0.4 mm/side

# Lateral-wall X reference bands (deep-embed spans; the outboard end is clipped
# to the real skin by the envelope, so only rough bracketing is needed).
PORT_OUTB, PORT_INB = -60.0, -100.0  # port wall bracket (skin ≈ −83..−90)
STBD_OUTB, STBD_INB = -278.0, -240.0  # stbd wall bracket (skin ≈ −250..−255)

# Nacelle-tilt actuator mount pads.
#
# WHAT CHANGED AT REV T1, AND WHY IT IS NOT A TWEAK
# -------------------------------------------------
# Through Rev S1d the actuator was a LIMITED-ROTATION servo whose horn drove a
# pushrod to a crank clamped on the ROTATING spar, so the pad was positioned
# relative to the SPAR and the linkage throw was the thing that had to be
# preserved.  Under Rev T1 the spar does not rotate, there is no crank and no
# pushrod: tilt torque leaves the fuselage on its own O4 shaft at chord station
# 53.6 (docs/WING_ATTACH_INTERFACE.md SS4.3b).  The pad is therefore re-datumed
# from the spar to the DRIVE SHAFT, and the linkage is a gear pair.
#
# THE ACTUATOR IS ALSO A DIFFERENT KIND OF DEVICE (WA-R15).
# The tip stage is a REDUCTION -- 14T pinion into a 50T ring, i = 3.571 -- so
# the shaft must turn 1.389 REVOLUTIONS for 140 deg of nacelle.  A limited-
# rotation servo cannot do that at any horn radius.  The actuator is a
# MULTI-TURN unit: a DS3225 body carrying the LibreServo_v4 board with the
# rotation-limit pin removed, commanded on the RS-485 bus and closed on the
# AK7455's absolute nacelle angle rather than on its own internal travel.  The
# BODY is unchanged, so this pad's footprint, bolt pattern and mass are
# unchanged -- which is the useful part: the Rev S1d datasheet work survives the
# architecture change intact.
#
# WHY THERE IS A GEAR PAIR HERE AT ALL, RATHER THAN A DIRECT COUPLING
# ------------------------------------------------------------------
# A coaxial coupling would be simpler and was tried first.  It does not fit: put
# the DS3225 body on the drive-shaft axis (Y +46.60, Z +69.09) and it overlaps
# the O30.1 spar socket boss by 13.5 mm in Y and the full 20 mm in Z, at EITHER
# orientation of the output shaft along the 40 mm body (the shaft sits 24 mm
# from one end, so the two choices are Y +22.6..+62.6 and Y +30.6..+70.6, and
# both eat the boss).  Relieving the boss to clear it would cut into the O20.4
# socket bore itself, so there is no version of coaxial that survives.
#
# Both axes run along hull X, so a plain SPUR pair is legal here with no
# right-angle stage -- the same kinematic argument that selected the tip stage
# (docs/plans/2026-08-29-004-... KTD1), applied at the other end of the shaft.
# Inside the fuselage there is no airfoil to pay for it.
#
# THE OFFSET IS SET BY THE LANDING-GEAR BAYS, NOT CHOSEN.
# The Rev R6 bay seats top out at Z +82.39 and the pad overlaps both bays in Y,
# so Z separation is the entire margin and the 3.0 mm clearance budget is a
# floor on the pad's bottom edge (Z >= +85.39).  With the 27.0 mm pad that puts
# the actuator axis at Z >= +98.89, i.e. a centre distance of at least 29.80 mm
# above the shaft.  At module 0.8 the next integer 1:1 pair above that is
# 38T/38T (PD 30.4, C = 30.40), which lands the pad bottom at +85.99 -- 3.60 mm
# of bay clearance, 0.60 mm better than the budget.  36T would give only 2.00 mm
# and 37T only 2.80 mm; both are under it.
#
# THE STAGE IS 1:1 ON PURPOSE.
# A step-UP here would trade surplus torque for slew rate -- the actuator has
# 2.402 N.m stall against 0.050 N.m at the shaft, a 48x margin, so the torque is
# genuinely there.  It is rejected because it would pull the ACTUATOR back below
# one revolution (500 deg of shaft / 1.923 = 260 deg), re-opening the 180-vs-270
# limited-rotation question that Rev T1 exists to close, and re-coupling the
# drive to a servo's internal travel.  1:1 keeps the actuator multi-turn at
# 1.389 rev, which is the whole point of WA-R15.
#
# CONSEQUENCE TO CARRY INTO FIRMWARE: an external spur pair REVERSES sense.
# Actuator-positive is nacelle-negative.  Declare it, do not discover it.
TILT_STAGE_MODULE = 0.8    # mm, module -- same as the tip stage (WA-R8)
TILT_STAGE_N = 38          # teeth, BOTH gears (1:1)
TILT_STAGE_PD = TILT_STAGE_MODULE * TILT_STAGE_N       # = 30.40 mm
TILT_STAGE_C = TILT_STAGE_PD                           # = 30.40 mm, 1:1 pair
TILT_STAGE_OD = TILT_STAGE_PD + 2 * TILT_STAGE_MODULE  # = 32.00 mm tip diameter
# Gear plane, spanwise -- and it is FORCED, not chosen.  Two solids share the
# shaft's X band at the wall and the shaft gear clears neither:
#
#   * the O30.1 spar socket boss (X -100..-60).  Shaft and spar axes are only
#     25.70 mm apart, so a shaft gear may have a tip radius of at most
#     25.70 - 15.05 - 1.0 = 9.65 mm to clear it.
#   * the wing root TENON (X -100..-108, Y +51.50..+63.50).  The tenon's forward
#     face is 4.90 mm from the shaft axis, so clearing it in Y needs a tip radius
#     under 3.90 mm -- PD 7.8, i.e. under 10 teeth at module 0.8, which undercuts
#     savagely and cannot carry the mesh.
#
# The second bound is the killer and it does not yield to gear sizing: NO gear
# that can transmit at this centre distance clears the tenon in Y.  It has to be
# cleared AXIALLY instead, so the mesh plane goes INBOARD of the tenon's inboard
# face (X -108 / -232), with 1 mm in hand.
#
# That is what forces the actuator standoff below, and it is the single largest
# packaging cost in the Rev T1 fuselage rework.  It is recorded here rather than
# buried in the pad constant because the causal chain -- tenon depth -> gear
# plane -> actuator standoff -> bay intrusion -- is not recoverable from the
# numbers alone.
TILT_STAGE_PLANE_DX = 11.0  # mm inboard of PORT_INB/STBD_INB: tenon ends at 8,
                            # + the repo's 3.0 mm GAP_BUDGET to a moving part
TILT_STAGE_FACE_W = 6.0    # mm, gear face width

# Drive-shaft wall bushing.  The shaft is supported at the root rib (this wall)
# and at the tip rib; this is the fuselage half of that pair.
#
# It gets NO boss of its own, and that is a finding rather than an omission.
# The boss-margin rule (bore + 2 x 4.85) would want O17.75, i.e. 8.88 mm of
# radius, but the root mortise's forward face sits at Y +51.10 -- only 4.50 mm
# from the shaft axis -- so any boss obeying the rule is cut in half by the
# mortise it has to sit beside.  Shrinking the boss to fit leaves 0.48 mm of
# wall, well under this repo's 1.16 mm floor.
#
# The bonded root flange (ROOT_FLANGE_*) solves it for free: it is 5 mm of solid
# material on the inner wall face spanning Y -9..+51 and Z +26.9..+106.9, and
# the shaft axis (Y +46.60, Z +69.09) lies inside it.  Seat the bushing THERE,
# through the flange and the skin behind it -- 7 mm of bearing length, more than
# a boss would have given, in material that is already there for the moment path.
SHAFT_BUSH_OD = 8.0        # mm, flanged bronze sleeve bushing, O4 bore
SHAFT_BUSH_SEAT_D = 8.05   # mm, slip-fit seat, bonded (West System 105/206)
SHAFT_BUSH_SEAT_L = 7.0    # mm, seat depth = 5 mm flange + 2 mm skin

NSVMT_BODY_L = 40.0     # servo body length, datasheet SS2-1 -> hull Y
NSVMT_BODY_W = 20.0     # servo body width,  datasheet SS2-1 -> hull Z
NSVMT_BODY_H = 40.5     # servo body height, datasheet SS2-1 -> hull X (inboard)
NSVMT_EAR_SPAN = 54.5   # flange overall length, datasheet drawing -> hull Y
NSVMT_FLANGE_H = 27.7   # flange face above the body base, datasheet drawing
NSVMT_MARGIN = 3.5      # pad relief all round the flange footprint

# Actuator standoff, spanwise.  The mounting face can no longer sit on the wall
# bracket at PORT_INB/STBD_INB: the output shaft protrudes OUTBOARD of the
# flange and carries the gear, and the gear plane is pinned inboard of the tenon
# (TILT_STAGE_PLANE_DX above).  So the face steps inboard by
#     gear plane offset 11.0 + gear face 6.0 + 1.0 shaft/hub clearance = 18.0 mm
# and the DS3225 body follows it, reaching X -158.5 (port) / -221.5 (stbd)
# instead of -140.5 / -239.5.
#
# COST, STATED PLAINLY: 18 mm per side of extra reach into the cargo bay, in the
# Z band +85.99..+112.99.  That band is ABOVE the bay's working floor -- the pad
# is datumed to the Rev R6 landing-gear bay tops (+82.39) plus the 3.0 mm
# clearance budget, and the CARGO-01 payload envelope is measured from the
# closed-door crown at Z +8.72 upward -- so what is lost is roof volume, not
# floor footprint.  It is still a real loss and it is tracked, not absorbed:
# see airframe/fuselage-mid/WBS.md WA-R15.
NSVMT_STANDOFF = 18.0   # mm, mounting face inboard of PORT_INB / STBD_INB

# Pad centre.  SHAFT-RELATIVE at Rev T1 (was spar-relative at Rev S1b, for a
# linkage that no longer exists).  The actuator axis sits directly ABOVE the
# drive shaft -- pure hull-Z offset -- so the gear centre distance is one number
# and a shaft move carries the actuator and the mesh with it.
NSVMT_DY = 0.0    # pad centre, chordwise offset from the shaft axis: none
# Rev S1d: the floor is datumed off the Rev R6 landing-gear bay seats, which top
# out at Z +82.39 -- 2.97 mm ABOVE the spar boss crown at Z +79.42 -- and the pad
# overlaps both bays in Y, so Z separation is the entire margin.  Floor set to the
# bay tops + the 3.0 mm clearance budget = Z +85.39; with the datasheet flange
# footprint (27.0 mm tall pad) that puts the centre at Z +98.89.
NSVMT_DZ = TILT_STAGE_C   # pad centre above the shaft = the gear centre distance
NSVMT_Y = WING_SHAFT_Y + NSVMT_DY   # = +46.60
NSVMT_Z = WING_SHAFT_Z + NSVMT_DZ   # = +99.49
NSVMT_PAD_W = NSVMT_EAR_SPAN + 2 * NSVMT_MARGIN   # = 61.5, Y span
NSVMT_PAD_H = NSVMT_BODY_W + 2 * NSVMT_MARGIN     # = 27.0, Z span

# Mounting-ear bolt pattern -- now datasheet-backed, so the bores are LIVE.
# 49.5 mm along the body length (hull Y) x 10 mm across its width (hull Z),
# DS3218 datasheet drawing.  This replaces the 35 x 16 mm pattern inherited from
# a servo the BOM had already replaced, which matched nothing.
NSVMT_HOLES_ENABLED = True
NSVMT_HOLE_S_Y = 49.5 / 2.0   # = 24.75, datasheet
NSVMT_HOLE_S_Z = 10.0 / 2.0   # =  5.00, datasheet
NSVMT_M3_D = 4.1

# SPAR-01/U4 (2026-08-25): the Y=+30 ring's own bottom chord is cut away by
# the clamshell aperture (WBS.md SPAR-01 finding 3, a three-sided frame, not
# a ring), so it never closed the wing-spar couple it was sized for. The two
# CF thwarts (fore Y-40, aft Y+118 -- see asf.RING_POCKETS) replace it as the
# couple closure; this gate gets flipped False only once a real geometry
# alternative reopens the Y=+30 station, not on a whim.
RING_Y30_ENABLED = False

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
        ("actuator pad port", box(
            PORT_INB - NSVMT_STANDOFF, PORT_OUTB,
            NSVMT_Y - NSVMT_PAD_W / 2, NSVMT_Y + NSVMT_PAD_W / 2,
            NSVMT_Z - NSVMT_PAD_H / 2, NSVMT_Z + NSVMT_PAD_H / 2)),
        ("actuator pad stbd", box(
            STBD_OUTB, STBD_INB + NSVMT_STANDOFF,
            NSVMT_Y - NSVMT_PAD_W / 2, NSVMT_Y + NSVMT_PAD_W / 2,
            NSVMT_Z - NSVMT_PAD_H / 2, NSVMT_Z + NSVMT_PAD_H / 2)),
        # WA-R1b (Rev T1): the bonded root flange -- the MOMENT path.
        #
        # THIS IS A KEEP-OUT, NOT PRINTED HULL MATERIAL, and that distinction was
        # arrived at by measurement.  The flange footprint is 80 (Z) x 60 (Y),
        # and the sidewall skin moves through **34.3 mm (port) / 37.0 mm (stbd)**
        # of hull X across it (ray-cast on a 13 x 17 grid, 221/221 hits,
        # 2026-08-30).  So:
        #   * "internal thickening to a plane", the idiom every other positive
        #     here uses, would make the flange up to 34 mm thick -- hundreds of
        #     grams for a plate whose specified 5 mm already gives FOS 29.2; and
        #   * a plane at the nominal inner face is TANGENT to the skin inside the
        #     footprint, which is a knife edge.  Measured on the first rebuild:
        #     a 0.46 mm non-manifold edge with 4 incident faces at
        #     (-86.33, +8.6, +52.2) plus a zero-area sliver body.  Subtracting a
        #     translated envelope to get a conforming plate instead was WORSE --
        #     a near-coincident boolean over 4,800 mm^2 of a 900k-face mesh left
        #     4 boundary edges, 2 non-manifold edges and 4 bodies.
        #
        # The flange is therefore a SEPARATE BONDED PART, exactly like the CF
        # thwarts (asf.RING_POCKETS) and the splice collars: generated to the
        # real skin curvature by
        # airframe/stls/fuselage/generate_wing_root_flange.py, bonded in with
        # West System 105/206.  The shell contributes nothing to it but the
        # obligation not to have the landing-gear bay grow into its volume --
        # which is what this entry is.
        ("root flange port", box(
            WALL_INNER_X_PORT, WALL_SKIN_X_PORT,
            WING_SPAR_Y - ROOT_FLANGE_W / 2, WING_SPAR_Y + ROOT_FLANGE_W / 2,
            WING_SPAR_Z - ROOT_FLANGE_H / 2, WING_SPAR_Z + ROOT_FLANGE_H / 2)),
        ("root flange stbd", box(
            WALL_SKIN_X_STBD, WALL_INNER_X_STBD,
            WING_SPAR_Y - ROOT_FLANGE_W / 2, WING_SPAR_Y + ROOT_FLANGE_W / 2,
            WING_SPAR_Z - ROOT_FLANGE_H / 2, WING_SPAR_Z + ROOT_FLANGE_H / 2)),
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


def wing_harness_ports():
    """Wing harness entry bores through each lateral wall.  (label, solid).

    Rev T1 (WA-R6).  Three per side, each coaxial with the matching spanwise
    bore in wings_s1223_revo.scad so the wire -- or, for the third one, the
    shaft -- runs straight from the wing into the cargo cavity instead of
    dead-ending on the skin:

        nav 3-core         station  8.0   O4.2   (wing conduit O3.2 + 1.0)
        AK7455 SPI pair    station 44.5   O7.5   (wing conduit O6.5 + 1.0)
        tilt drive shaft   station 53.6   O4.4   (running fit, NOT oversized)

    The two Rev S1c O8.0 EDF ports are gone: the four 10 AWG feeds now enter
    through the spar's own bore at the socket (SPAR_WIRE_BORE_D), which is the
    whole point of a hollow fixed spar on the tilt axis.

    These are cut through the same wall brackets the spar socket uses, so the
    outboard end is clipped to the real skin by the envelope exactly as the
    socket is.
    """
    return [
        ("nav entry", x_cylinder(
            WING_NAV_Y, WING_NAV_Z, WING_HARNESS_INB_PORT, PORT_OUTB,
            WING_NAV_ENTRY_D / 2.0)),
        ("encoder entry", x_cylinder(
            WING_ENC_Y, WING_ENC_Z, WING_HARNESS_INB_PORT, PORT_OUTB,
            WING_ENC_ENTRY_D / 2.0)),
        ("tilt shaft entry", x_cylinder(
            WING_SHAFT_Y, WING_SHAFT_Z, WING_HARNESS_INB_PORT, PORT_OUTB,
            WING_SHAFT_ENTRY_D / 2.0)),
        ("nav entry stbd", x_cylinder(
            WING_NAV_Y, WING_NAV_Z, STBD_OUTB, WING_HARNESS_INB_STBD,
            WING_NAV_ENTRY_D / 2.0)),
        ("encoder entry stbd", x_cylinder(
            WING_ENC_Y, WING_ENC_Z, STBD_OUTB, WING_HARNESS_INB_STBD,
            WING_ENC_ENTRY_D / 2.0)),
        ("tilt shaft entry stbd", x_cylinder(
            WING_SHAFT_Y, WING_SHAFT_Z, STBD_OUTB, WING_HARNESS_INB_STBD,
            WING_SHAFT_ENTRY_D / 2.0)),
        # Bushing seat, counterbored into the root flange + skin (see
        # SHAFT_BUSH_* above for why it does not get a boss of its own).
        ("tilt shaft bushing seat", x_cylinder(
            WING_SHAFT_Y, WING_SHAFT_Z,
            WALL_INNER_X_PORT, WALL_INNER_X_PORT + SHAFT_BUSH_SEAT_L,
            SHAFT_BUSH_SEAT_D / 2.0)),
        ("tilt shaft bushing seat stbd", x_cylinder(
            WING_SHAFT_Y, WING_SHAFT_Z,
            WALL_INNER_X_STBD - SHAFT_BUSH_SEAT_L, WALL_INNER_X_STBD,
            SHAFT_BUSH_SEAT_D / 2.0)),
    ]


def spar_socket_cuts(outb_x, inb_x, label, harness_inb=None):
    """One side's bonded spar socket (WA-R1/WA-R2, Rev T1).

    `outb_x` is the wing-facing (outboard) end of the boss; `inb_x` is the
    bay-facing end, which is ALSO the socket's inboard limit -- the cargo bay's
    clear span begins there (X -100 port / -240 stbd) and the owner ruling is
    that it stays clear.  Against a wall skin at X -81.33 that is
    SPAR_SOCKET_REACH = 18.5 mm of depth, and 18.67 mm is the most the bay
    allows at all.

    Two coaxial cylinders, outboard to inboard:
      1. socket bore (WING_SPAR_BORE_D = O20.4) from the boss face to `inb_x` --
         the bonded/clamped seat for the FIXED CF spar.  sigma = 0.31 MPa on
         projected bearing area, FOS 16, and shear never needed depth.
      2. wire continuation (SPAR_WIRE_BORE_D = O16.3, the spar's own ID) from
         `inb_x` to `harness_inb`.  The spar stops at the socket; the four
         10 AWG conductors inside it do not, and they have to reach the same
         deep interior wall the encoder/nav ports are cut through.  Omitting
         this is what left 7.4 mm^3 of uncut material on the stbd side at Rev
         S1c -- see the U6 note in git history for that finding.

    WHAT IS NOT HERE ANY MORE: the F688ZZ flange counterbore and bearing seat.
    A bearing at this station would let the fixed spar rotate under the tilt
    pinion's gear reaction, so it is not merely redundant, it is wrong (WA-R2).

    Returns a list of (label, solid) tuples, matching the module's convention.
    """
    span = abs(outb_x - inb_x)
    assert span >= SPAR_SOCKET_REACH - 1e-6, (
        f"{label}: boss span {span:.2f} mm is shorter than the "
        f"{SPAR_SOCKET_REACH} mm socket reach WA-R1 requires"
    )
    cuts = [
        (f"{label} spar socket", x_cylinder(
            WING_SPAR_Y, WING_SPAR_Z, min(outb_x, inb_x), max(outb_x, inb_x),
            WING_SPAR_BORE_D / 2.0)),
    ]
    if harness_inb is not None and abs(harness_inb - inb_x) > 0.01:
        cuts.append((f"{label} 10 AWG bundle exit", x_cylinder(
            WING_SPAR_Y, WING_SPAR_Z, min(inb_x, harness_inb),
            max(inb_x, harness_inb), SPAR_WIRE_BORE_D / 2.0)))
    return cuts


def wing_keepout_negatives():
    """Wing voids the gear bay's added material must not intrude into."""
    my0, my1 = WING_MORT_Y - MORT_W / 2, WING_MORT_Y + MORT_W / 2
    mz0, mz1 = WING_ROOT_Z - MORT_H / 2, WING_ROOT_Z + MORT_H / 2
    return [
        *spar_socket_cuts(PORT_OUTB, PORT_INB, "port",
                          harness_inb=WING_HARNESS_INB_PORT),
        *spar_socket_cuts(STBD_OUTB, STBD_INB, "stbd",
                          harness_inb=WING_HARNESS_INB_STBD),
        # CARGO-03 (2026-08-24): these used to span PORT_INB+1 .. PORT_OUTB-10
        # (X -99..-70), described as cutting "through each wall".  They did not:
        # at the mortise station the wall lies at X -115..-99, so the cut began
        # exactly where the wall ENDS and removed only free air outboard of it,
        # leaving ~1700 mm^3 of uncut wall behind on each side.  The wing tenon
        # could not enter.  PORT_INB/PORT_OUTB are deep-embed spans for BOSSES,
        # never the wall, and treating them as the wall is what caused this.
        #
        # They now use the same inboard references the Rev S1c harness ports
        # derived for this exact wall ("past the -115.2 encoder-line wall"),
        # so one measured fact drives every wing-root penetration.
        ("mortise port", box(
            WING_HARNESS_INB_PORT, PORT_OUTB, my0, my1, mz0, mz1)),
        ("mortise stbd", box(
            STBD_OUTB, WING_HARNESS_INB_STBD, my0, my1, mz0, mz1)),
        # Rev S1c: the harness entries join the keep-out set for the same
        # reason the spar bore is in it -- "on the HULL the wing always wins".
        # A gear-bay flange that plugs a harness port is the same class of
        # failure as one that plugs the spar bore: it is found at assembly,
        # with the wire in hand, and it cannot be relieved from outside.
    ] + wing_harness_ports()


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
    if RING_Y30_ENABLED:
        for xm, xx, zm, zx, ym, yx in asf.RING_POCKETS["cargo_Y30"]:
            cutters.append(box(xm, xx, ym, yx, zm, zx))
        notes.append("ring pocket Y=30")
    else:
        notes.append("ring pocket Y=30 GATED OFF -- superseded by the U4 "
                     "CF thwart pair (SPAR-01); see RING_Y30_ENABLED")

    # SPAR-01/U4: CF thwart pair (fore Y-40, aft Y+118) closing the wing-spar
    # couple that the retired Y=+30 ring never closed (its bottom chord was
    # cut away by the clamshell aperture -- see WBS.md SPAR-01 finding 3).
    # Same locating-groove pattern as the existing ring frames: a 2 mm
    # CF-PLATE-2MM part bonds into a shallow perimeter pocket, not a printed
    # solid, so only the pocket is a Blender/hull-frame feature here.
    for xm, xx, zm, zx, ym, yx in asf.RING_POCKETS["cargo_Yn40"]:
        cutters.append(box(xm, xx, ym, yx, zm, zx))
    for xm, xx, zm, zx, ym, yx in asf.RING_POCKETS["cargo_Y118"]:
        cutters.append(box(xm, xx, ym, yx, zm, zx))
    notes.append("CF thwart pockets Y=-40 (fore) / Y=+118 (aft), U4/SPAR-01")

    # Wing spar bonded socket + 10 AWG bundle exit (per side, terminating at
    # the bay edge -- WA-R1/WA-R2) + 2 root mortises (through each wall).
    # Built by wing_keepout_negatives() so the solids the gear bay is trimmed
    # against are the SAME solids the hull is actually cut with (LG-10.4).
    for label, solid in wing_keepout_negatives():
        cutters.append(solid)
        notes.append(f"wing {label}")

    # Nacelle-servo M3 heat-set pilot bores (into the cavity face of each pad).
    if NSVMT_HOLES_ENABLED:
        face_port = PORT_INB - NSVMT_STANDOFF
        face_stbd = STBD_INB + NSVMT_STANDOFF
        for x_in, x_out in ((face_port, face_port + 8.0),
                            (face_stbd, face_stbd - 8.0)):
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
    else:
        notes.append("servo M3 pilot bores GATED OFF "
                     "(ear pattern unverified -- Rev S1d; see NSVMT_HOLES_ENABLED)")

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

    # Wing-spar socket bosses (Ø30.1, coaxial with the spar), the two
    # nacelle-tilt actuator mount pads, and (WA-R1b) the two bonded wing-root
    # flanges -- deep boxes/cylinders, envelope-clipped.  Built by
    # wing_keepout_positives() so the solids the gear bay is trimmed against
    # are the SAME solids the hull actually carries (LG-10.4).
    # The root flanges are in the keep-out set but are NOT built here: they are
    # separate bonded parts (see wing_keepout_positives), so the shell must
    # reserve their volume without printing it.
    for _label, solid in wing_keepout_positives():  # raw: main() clips
        if _label.startswith("root flange"):
            continue
        feats.append(solid)
    notes.append("2 wing-spar socket bosses (O30.1, Rev T1)")
    notes.append("2 nacelle-tilt actuator mount pads")
    notes.append("root flanges RESERVED, not printed -- separate bonded parts "
                 "(generate_wing_root_flange.py)")

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


DEGENERATE_EDGE_MM = 0.05   # mm; see collapse_degenerate_edges() -- far below
                            # any FDM manufacturing tolerance (~0.1-0.2 mm), so
                            # collapsing an edge this short cannot be a real
                            # design feature.


def collapse_degenerate_edges(mesh, max_len=DEGENERATE_EDGE_MM):
    """Collapse near-zero-length NON-MANIFOLD edges (>2 incident faces).

    U5/KTD1 (2026-08-24): the wing-root tie-rod bosses (ROD_FWD_*/ROD_AFT_*)
    graze the fore landing-gear bay's aperture/rebate cutters by a genuinely
    tiny amount (< 0.004 mm^3 measured) -- well below any manufacturing
    tolerance, but manifold3d's boolean kernel can leave a near-duplicate
    vertex pair at exactly that graze instead of merging it, producing an
    edge so short (~0.001-0.002 mm observed) that it is a mesh-processing
    artifact, not a real feature -- yet it is NON-MANIFOLD (3+ incident
    faces), which `close_zero_area_slits()` above does not touch (that
    targets boundary LOOPS, not this).

    A GLOBAL coarser `merge_vertices(digits_vertex=...)` pass was tried and
    rejected: at 0.01 mm resolution it merges unrelated, legitimately close
    (but distinct) vertices elsewhere in this ~900k-face shell, trading one
    non-manifold edge for dozens more.  This is deliberately LOCAL instead:
    it only touches edges that are BOTH non-manifold AND shorter than
    `max_len`, so it cannot affect any edge that is a real design feature at
    printable scale.  Verified 2026-08-24: collapses the one edge found,
    volume unchanged to 5 significant figures, 0 new defects.
    """
    ec = np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique))
    nonman = np.where(ec > 2)[0]
    if not len(nonman):
        return mesh, 0
    remap = np.arange(len(mesh.vertices))
    collapsed = 0
    for i in nonman:
        v0, v1 = mesh.edges_unique[i]
        d = np.linalg.norm(mesh.vertices[v0] - mesh.vertices[v1])
        if d < max_len:
            remap[remap == remap[v1]] = remap[v0]
            collapsed += 1
    if not collapsed:
        return mesh, 0
    out = trimesh.Trimesh(vertices=mesh.vertices.copy(),
                          faces=remap[mesh.faces], process=False)
    out.update_faces(out.nondegenerate_faces())
    out.update_faces(out.unique_faces())
    out.remove_unreferenced_vertices()
    return out, collapsed


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
    # U5/KTD1: a residual NON-MANIFOLD (not boundary) edge -- e.g. the wing-
    # root tie-rod boss grazing an LG-bay cutter by a sub-manufacturing-
    # tolerance sliver -- is neither a hole (close_zero_area_slits) nor
    # something fill_holes touches (it only adds faces to open boundary
    # loops).  Try collapsing it before falling back to fill_holes.
    if not mesh.is_watertight:
        mesh, n_collapsed = collapse_degenerate_edges(mesh)
        if n_collapsed:
            print(f"  finalize: collapsed {n_collapsed} degenerate "
                  f"(< {DEGENERATE_EDGE_MM} mm) non-manifold edge(s)")
    if not mesh.is_watertight:
        trimesh.repair.fill_holes(mesh)
    trimesh.repair.fix_normals(mesh)
    # Rev T1c: sweep slivers ONE LAST TIME.  The body drop above happens before
    # close_zero_area_slits(), and that pass can leave a fresh zero-area
    # fragment behind -- observed as a 2-face, 0.0 mm^3 body at
    # (-84.0, +7.7, +64.4) surviving to the published STL, which reads as
    # "bodies=2" in every downstream check even though the shell is watertight.
    # A trailing sweep costs one split() and removes the false signal.
    mesh = drop_slivers(mesh)
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

    # Allowlist enforcement (2026-09-05): finalize_watertight()'s fill_holes()
    # fallback cannot tell the cargo_fwd/cargo_aft mating apertures apart from
    # a genuine defect, so it will happily reseal them if the float32 round-trip
    # left them as a boundary loop. Re-assert both are open, unconditionally,
    # as the LAST step before this function's own write — see
    # tools/open_mating_faces.py for why this must be enforced here rather
    # than trusted to survive the repair pass above.
    for aperture in ("cargo_fwd", "cargo_aft"):
        m, changed, note = omf.ensure_open(m, aperture)
        print(f"  {note}")
        if changed:
            m.merge_vertices()

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
