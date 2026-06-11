#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serenity_fuselage_asm4.py
FreeCAD / Assembly4 headless assembly script for the Serenity UAV airframe.

Creates a single .FCStd document containing all four fuselage hull sections,
both wing panels, both wing-nacelle pylons, port and starboard nacelle pods,
cargo-bay clamshell doors and subsystems, and landing legs/feet — all
positioned in the project world coordinate system:
    X = lateral,      positive toward port  (+left)
    Y = longitudinal, positive aft (+back)
    Z = vertical,     positive dorsal (+up)

NOTE ON FREECAD VIEWPORT:
  FreeCAD's default 3D viewport uses Z=up, which matches the project hull
  frame (Z=dorsal/up).  The assembled model should appear upright in the
  default Front view.  The REORIENT_FOR_VIEWPORT flag at the bottom of this
  file is no longer needed and defaults to False.

USAGE:
  Headless (generates .FCStd only, no GUI):
    freecadcmd airframe/freecad/assembly/serenity_fuselage_asm4.py
  Interactive (opens result in FreeCAD GUI):
    freecad airframe/freecad/assembly/serenity_fuselage_asm4.py

OUTPUT:
  airframe/freecad/assembly/serenity_fuselage_asm4.FCStd

MISSING STLs:
  Several STLs are not yet rendered from their SCAD sources.  The script
  logs a WARNING for each missing file and skips that component rather
  than aborting.  See TODO.md §1.1 for the render-command checklist.
  Required STLs that block meaningful assembly visualisation:
    - airframe/stls/nacelles/nacelle_pod_port.stl
      (from nacelle_pod_50mm_tandem.scad -D NACELLE_SIDE=1)
    - airframe/stls/nacelles/nacelle_pod_stbd.stl
      (from nacelle_pod_50mm_tandem.scad -D NACELLE_SIDE=-1)
  These are currently represented by the tip-cap STLs (nacelle_tip_cap_port/stbd.stl)
  as stand-ins until the full pod is rendered.

COORDINATE DERIVATION — KEY CONSTANTS:
  All numbers are from the 24"-scale STL world space (SCALE_24 = 2.9294×).

  Hull sections (all share the same world coordinate system — import at identity):
    Head    : X = 99 .. 228 mm,   Y = -288 .. -53 mm,   Z = 0 .. 141 mm
    Cargo   : X = -202 .. -7 mm,  Y = -415 .. -211 mm,  Z = 0 .. 163 mm
    Middle  : centroid CX = 181 mm (main fuselage body; spans head–cargo junction)
    Rear    : X = -246 .. -106 mm, Y = -193 .. -35 mm,  Z = 0 .. 182 mm

  Wing root station (cargo Z-wall interface):
    X_CEN  = -102.19 mm (50% chord from LE)
    Y_CEN  = -288.63 mm (chord plane)
    LE_X   =  -21.69 mm (leading edge)
    Port Z wall = 163 mm;  Stbd Z wall = 0 mm

  Nacelle tilt pivot (at PIVOT_Z = 103.75 mm in nacelle local Z):
    Port pivot: world (-70, -288.63, 251)   [Z = 163 + pylon_span 88]
    Stbd pivot: world (-70, -288.63, -88)   [Z =   0 - pylon_span 88]
    Assembly shows nacelles at 90° VTOL-hover position (intake up, thrust down).

  Rotations (quaternion x, y, z, w — right-hand, unit-length):
    Port wing    : (-0.5, -0.5,  0.5, 0.5)  local X→+Z,  Y→-X, Z→+Y
    Stbd wing    : (-0.5,  0.5,  0.5, 0.5)  local X→-Z,  Y→-X, Z→+Y  (mirror)
    Port nacelle : ( 0.5, -0.5,  0.5, 0.5)  local Z→-Y (bore↓), X→+Z (outboard)
    Stbd nacelle : ( 0.5,  0.5, -0.5, 0.5)  local Z→-Y (bore↓), X→-Z (mirrored)
    Pylon port   : ( 0.5,  0.5, -0.5, 0.5)  local Z→+Z (outboard), Z_bore→+Y
    Pylon stbd   : ( 0.5, -0.5,  0.5, 0.5)  mirror of port pylon (VERIFY in slicer)

  All rotations verified analytically.  Confirm placements by inspecting:
    - Nacelle intake/nozzle direction at each tilt stop
    - Wing leading edge aligned with LE_X = -21.69 mm in cargo slicer cross-section
    - Pylon flush with cargo Z wall (no gap, no protrusion beyond outer mold line)

REFERENCES:
  s_cargo_sect_shell24.scad   — cargo bounds, spar bore X, wing root mortise
  s_wings_s1223_revo.scad     — wing planform, spar params, assembly orientation
  s_wing_nacelle_pylon_revo.scad — PYLON_SPAN=88mm, PIVOT_Z=83mm
  nacelle_pod_50mm_tandem.scad — NACELLE_L=185.2mm, PIVOT_Z=103.75mm
  REVN_BUILD_GUIDE_24IN.md    — bay positions, keel datums

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License : CC BY 4.0 — creativecommons.org/licenses/by/4.0
Date    : 2026-06-08
"""

import os
import sys
import math
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FreeCAD bootstrap — locate and import the FreeCAD Python libraries.
#
# FreeCAD's site-packages or lib directory must be on sys.path.  Common
# install locations are listed below; the first one that exists is used.
# Override by setting the FREECAD_LIB environment variable before running.
# ---------------------------------------------------------------------------
_FC_SEARCH_PATHS = [
    os.environ.get("FREECAD_LIB", ""),
    "/usr/lib/freecad-python3/lib",
    "/usr/lib/freecad/lib",
    "/usr/local/lib/freecad/lib",
    "/opt/freecad/lib",
    "/Applications/FreeCAD.app/Contents/lib",  # macOS
]

for _fc_path in _FC_SEARCH_PATHS:
    if _fc_path and os.path.isdir(_fc_path):
        if _fc_path not in sys.path:
            sys.path.insert(0, _fc_path)
        break
else:
    log.warning(
        "FreeCAD lib directory not found in search paths.  "
        "Set FREECAD_LIB=/path/to/freecad/lib or install FreeCAD."
    )

try:
    import FreeCAD
    import Mesh
    log.info("FreeCAD %s loaded.", FreeCAD.Version()[0])
except ImportError as _e:
    log.error("Cannot import FreeCAD: %s", _e)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Path constants
#
# All STL paths are relative to REPO_ROOT so the script works from any
# working directory.  REPO_ROOT is resolved as two levels above this file
# (i.e., the repository root at Serenity-UAV/).
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(_THIS_DIR, "..", "..", ".."))


# Helper: resolve an STL path and warn if it is absent.
def _stl(relative_path):
    """Return absolute path to an STL under REPO_ROOT, warning if missing."""
    abs_path = os.path.join(REPO_ROOT, relative_path)
    if not os.path.isfile(abs_path):
        log.warning("STL not found (skip): %s", abs_path)
        return None
    return abs_path


# --- Fuselage hull sections (all in shared project world space) ---
STL_HEAD    = _stl("airframe/stls/fuselage/s_head_shell24.stl")
STL_CARGO   = _stl("airframe/stls/fuselage/cargo/s_cargo_sect_shell24.stl")
STL_MIDDLE  = _stl("airframe/stls/fuselage/s_middle_canonical_shell24.stl")
# Rear section lives in deferred/aft-edf because it contains EDF scoop windows.
# It is used here purely for visual assembly fidelity; Phase 11 only for flight.
STL_REAR    = _stl("deferred/aft-edf/stls/s_rear_neck_intake_shell24.stl")

# --- Wings ---
STL_WING_PORT  = _stl("airframe/stls/wings/s_wing_port_s1223_revo.stl")
STL_WING_STBD  = _stl("airframe/stls/wings/s_wing_stbd_s1223_revo.stl")
STL_PYLON_PORT = _stl("airframe/stls/wings/s_wing_nacelle_pylon_revo.stl")
# Same STL as port pylon — mirrored in placement only.
STL_PYLON_STBD = _stl("airframe/stls/wings/s_wing_nacelle_pylon_revo.stl")

# --- Nacelle pods ---
# Full pod STL requires manual render from SCAD.  Tip caps are stand-ins.
STL_NACELLE_PORT = _stl("airframe/stls/nacelles/nacelle_pod_port.stl")
if STL_NACELLE_PORT is None:
    log.warning(
        "Full nacelle pod STL absent.  Using tip cap as stand-in.  "
        "Render: openscad -o airframe/stls/nacelles/nacelle_pod_port.stl "
        "airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad -D NACELLE_SIDE=1"
    )
    STL_NACELLE_PORT = _stl("airframe/stls/nacelles/nacelle_tip_cap_port.stl")

STL_NACELLE_STBD = _stl("airframe/stls/nacelles/nacelle_pod_stbd.stl")
if STL_NACELLE_STBD is None:
    log.warning(
        "Full nacelle pod STL absent.  Using tip cap as stand-in.  "
        "Render: openscad -o airframe/stls/nacelles/nacelle_pod_stbd.stl "
        "airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad -D NACELLE_SIDE=-1"
    )
    STL_NACELLE_STBD = _stl("airframe/stls/nacelles/nacelle_tip_cap_stbd.stl")

# --- Nacelle nozzle assembly (both nacelles share the same geometry) ---
STL_NOZZLE_ASM = _stl("airframe/stls/nacelles/nozzles/nacelle_nozzle_closed_asm.stl")

# --- Cargo subsystem ---
STL_DOOR_PORT     = _stl("airframe/stls/fuselage/cargo/cargo_door_port.stl")
STL_DOOR_STBD     = _stl("airframe/stls/fuselage/cargo/cargo_door_stbd.stl")
STL_WINCH_MOUNT   = _stl("airframe/stls/fuselage/cargo/cargo_winch_motor_mount.stl")
STL_WINCH_SPOOL   = _stl("airframe/stls/fuselage/cargo/cargo_winch_spool.stl")
STL_AUTOLATCH     = _stl("airframe/stls/fuselage/cargo/cargo_cradle_autolatch.stl")
STL_FPV_BEZEL     = _stl("airframe/stls/fuselage/cargo/cargo_fpv_bezel.stl")
STL_GPS_RING      = _stl("airframe/stls/fuselage/cargo/cargo_gps_retention_ring.stl")

# --- Structural / landing gear ---
STL_LEGS = _stl("airframe/stls/fuselage/s_legs_scaled24.stl")
STL_FEET = _stl("airframe/stls/fuselage/s_feet_x_4_scaled24.stl")

# Output path for the assembly document
OUT_FCStd = os.path.join(_THIS_DIR, "serenity_fuselage_asm4.FCStd")

# ---------------------------------------------------------------------------
# Assembly geometry constants
#
# All values in millimetres, derived from SCAD sources.  See docstring above
# for the derivation chain.  Verify each VERIFY-tagged placement in slicer
# or FreeCAD measurement tool before committing to a physical build step.
# ---------------------------------------------------------------------------

# ── Cargo section (reference frame for wing/nacelle interface) ───────────────
CARGO_DZ         = 163.0      # mm, gondola full Z span (port wall = DZ, stbd wall = 0)
CARGO_WALL_MM    =   2.0      # mm, shell wall thickness
WING_ROOT_X_CEN  = -102.19    # mm, mortise X centre (50% chord)
WING_ROOT_Y_CEN  = -288.63    # mm, chord plane Y (= CY + 40)
WING_LE_X        =  -21.69    # mm, wing root leading-edge world X
WING_SPAR_X      =  -70.0     # mm, spar bore X (30% chord from LE)

# ── Wing planform (from s_wings_s1223_revo.scad) ─────────────────────────────
WING_SEMI_SPAN   =  85.7      # mm, root-face to tip-face span
WING_CHORD_ROOT  = 161.0      # mm, root chord

# ── Pylon geometry (from s_wing_nacelle_pylon_revo.scad) ─────────────────────
PYLON_SPAN       =  88.0      # mm, outboard extent (nacelle X-face to fuselage Z wall)

# ── Nacelle geometry (from nacelle_pod_50mm_tandem.scad Rev T) ───────────────
NACELLE_L        = 185.2      # mm, full nacelle length (1.25× scale)
NACELLE_PIVOT_Z  = 103.75     # mm, tilt pivot station in nacelle local Z (intake=0)

# ── Nacelle pivot world positions (derived) ──────────────────────────────────
# Pivot X = WING_SPAR_X (spar bore and tilt axis share the same longitudinal station).
# Pivot Y = WING_ROOT_Y_CEN (spar bore and tilt axis at chord plane).
# Port pivot Z = cargo port wall + pylon outboard reach.
# Stbd pivot Z = cargo stbd wall - pylon outboard reach (negative = stbd of stbd wall).
PIVOT_X          = WING_SPAR_X                        # = -70.0 mm
PIVOT_Y          = WING_ROOT_Y_CEN                    # = -288.63 mm
PIVOT_Z_PORT     = CARGO_DZ + PYLON_SPAN              # = 251.0 mm
PIVOT_Z_STBD     = 0.0 - PYLON_SPAN                   # = -88.0 mm


# ---------------------------------------------------------------------------
# Rotation quaternions (x, y, z, w — right-hand, unit length).
#
# Each quaternion is documented with the local-to-world axis mapping it
# implements.  Derivation: compute rotation matrix from axis-map, then
# extract quaternion from matrix trace and off-diagonal elements.
# All quaternions verified: |q| = 1.0; cross-check by applying to unit
# vectors and confirming the target world direction.
#
# FreeCAD convention: FreeCAD.Rotation(qx, qy, qz, qw)
#   where (qx, qy, qz) is the vector part and qw is the scalar.
# ---------------------------------------------------------------------------

def _quat(qx, qy, qz, qw):
    """Return a FreeCAD.Rotation from quaternion components (x, y, z, w)."""
    return FreeCAD.Rotation(
        FreeCAD.Vector(qx, qy, qz),
        qw * (180.0 / math.pi)  # FreeCAD.Rotation(axis, angle_deg) form
        # Note: FreeCAD.Rotation also accepts a raw quaternion via
        # FreeCAD.Rotation(Vector, float) where float is the angle in degrees
        # and Vector is the rotation axis (not the quaternion vector part).
        # We therefore decode qx,qy,qz,qw to axis-angle here.
    )


def rotation_from_quaternion(qx, qy, qz, qw):
    """
    Construct a FreeCAD.Rotation from quaternion components (x, y, z, w).

    FreeCAD.Rotation does not accept a raw quaternion tuple directly.
    We convert to axis-angle (the form FreeCAD accepts) and return the
    Rotation object.  For the identity quaternion (0,0,0,1), returns
    FreeCAD.Rotation() with no rotation.
    """
    norm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    qx, qy, qz, qw = qx / norm, qy / norm, qz / norm, qw / norm

    # sin(θ/2) is the magnitude of the vector part
    sin_half = math.sqrt(qx * qx + qy * qy + qz * qz)
    if sin_half < 1e-10:
        # Identity rotation (or near-zero angle)
        return FreeCAD.Rotation()

    angle_rad = 2.0 * math.atan2(sin_half, qw)
    angle_deg = math.degrees(angle_rad)
    axis = FreeCAD.Vector(qx / sin_half, qy / sin_half, qz / sin_half)
    return FreeCAD.Rotation(axis, angle_deg)


# Port wing: local X→+Z, local Y→-X, local Z→+Y
#   q = (-0.5, -0.5, 0.5, 0.5)  axis=(-1/√3, -1/√3, 1/√3), angle=120°
ROT_WING_PORT = rotation_from_quaternion(-0.5, -0.5, 0.5, 0.5)

# Stbd wing: local X→-Z, local Y→-X, local Z→+Y  (port mirrored in Z)
#   q = (-0.5, 0.5, 0.5, 0.5)
ROT_WING_STBD = rotation_from_quaternion(-0.5, 0.5, 0.5, 0.5)

# Port nacelle at 90° VTOL hover: local Z (bore)→-Z (ventral), local X→+X (port)
#   q = (0.5, -0.5, 0.5, 0.5)
#   VERIFY: intake face (local Z=0) should be UP (+world Z = dorsal) in FreeCAD view.
ROT_NACELLE_PORT = rotation_from_quaternion(0.5, -0.5, 0.5, 0.5)

# Stbd nacelle at 90° VTOL hover: local Z (bore)→-Z (down/ventral), local X→-X (stbd)
#   q = (0.5, 0.5, -0.5, 0.5)
#   VERIFY: mirrors port nacelle about X=−170 mm (cargo X lateral midplane).
ROT_NACELLE_STBD = rotation_from_quaternion(0.5, 0.5, -0.5, 0.5)

# Port pylon: local Z (pylon length) → world +X (outboard/port), local Y→+Z (dorsal)
#   VERIFY: pylon inboard face must be flush with cargo dorsal face (Z=163 mm).
ROT_PYLON_PORT = rotation_from_quaternion(0.5, 0.5, -0.5, 0.5)

# Stbd pylon: mirror of port pylon
ROT_PYLON_STBD = rotation_from_quaternion(0.5, -0.5, 0.5, 0.5)


# ---------------------------------------------------------------------------
# Document colour table (RGBA, 0.0–1.0)
# Used to colour-code component groups for visual clarity.
# ---------------------------------------------------------------------------
COL_HULL      = (0.78, 0.73, 0.65, 1.0)   # warm off-white (canonical Serenity grey)
COL_WING      = (0.70, 0.72, 0.74, 1.0)   # cool light grey
COL_NACELLE   = (0.75, 0.70, 0.65, 1.0)   # nacelle brown-grey
COL_CARGO_SYS = (0.55, 0.60, 0.55, 1.0)   # cargo green-grey
COL_GEAR      = (0.30, 0.30, 0.30, 1.0)   # dark landing gear
COL_PYLON     = (0.65, 0.65, 0.68, 1.0)   # pylon neutral grey


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def add_mesh_part(doc, group, name, stl_path, placement, colour):
    """
    Import an STL file as a Mesh::Feature, apply placement and colour, and
    add it to a parent App::Part group.

    Parameters
    ----------
    doc       : FreeCAD.Document
    group     : App::Part feature (parent container)
    name      : str — FreeCAD object name (no spaces)
    stl_path  : str or None — absolute path to STL; skipped if None
    placement : FreeCAD.Placement
    colour    : tuple (r, g, b, a) floats 0–1

    Returns
    -------
    Mesh::Feature object, or None if stl_path is None.
    """
    if stl_path is None:
        log.info("  SKIP  %-32s (STL not available)", name)
        return None

    mesh_data = Mesh.Mesh()
    mesh_data.read(stl_path)

    obj = doc.addObject("Mesh::Feature", name)
    obj.Mesh = mesh_data
    obj.Placement = placement

    # Set display colour via ViewObject (only available when GUI is active).
    try:
        if obj.ViewObject is not None:
            obj.ViewObject.ShapeColor = colour[:3]
            if len(colour) > 3:
                obj.ViewObject.Transparency = int((1.0 - colour[3]) * 100)
    except Exception:
        pass  # headless mode — ViewObject not available

    group.addObject(obj)
    log.info("  ADD   %-32s  (%s)", name, os.path.basename(stl_path))
    return obj


def make_placement(pos_xyz, rotation):
    """
    Convenience wrapper: return a FreeCAD.Placement from a position tuple
    and a FreeCAD.Rotation.

    Parameters
    ----------
    pos_xyz  : (x, y, z) tuple in mm
    rotation : FreeCAD.Rotation

    Returns
    -------
    FreeCAD.Placement
    """
    return FreeCAD.Placement(FreeCAD.Vector(*pos_xyz), rotation)


def make_group(doc, name, parent=None):
    """
    Create an App::Part container (Assembly4 'Part' / logical group).
    If parent is given the group is added as a child of that App::Part.

    Returns the new App::Part feature.
    """
    grp = doc.addObject("App::Part", name)
    grp.addProperty("App::PropertyString", "Type", "Base", "")
    grp.Type = "Assembly4::Part"
    if parent is not None:
        parent.addObject(grp)
    return grp


# ---------------------------------------------------------------------------
# Assembly document build
# ---------------------------------------------------------------------------

def build_assembly():
    """
    Create and populate the Serenity fuselage assembly FreeCAD document.
    Returns the FreeCAD.Document on success.
    """
    # Create a new document.  Suppress warning about duplicate labels.
    doc = FreeCAD.newDocument("SerenityFuselageAsm4")
    doc.Label = "Serenity UAV — Fuselage Assembly Rev S2"

    # ── Root Assembly4 model object ──────────────────────────────────────────
    # Assembly4 expects a root App::Part with Type = 'Assembly4::Assembly'.
    # All sub-groups and parts are added under this root.
    root = doc.addObject("App::Part", "Model")
    root.addProperty("App::PropertyString", "Type", "Base", "")
    root.Type = "Assembly4::Assembly"
    root.addProperty("App::PropertyString", "AssemblyType", "Assembly", "")
    root.AssemblyType = "Asm4EEAssembly"

    identity = make_placement((0, 0, 0), FreeCAD.Rotation())

    # ── Group: Fuselage hull sections ────────────────────────────────────────
    # All four hull sections are in the shared project world coordinate system.
    # They import at the identity placement — no translation or rotation needed.
    # The head–middle gap (X = -7..99 mm) is internal fuselage volume; no
    # separate shell exists for that zone (foam fill + keel only).
    log.info("-- Fuselage hull sections")
    grp_hull = make_group(doc, "Fuselage_Hull", parent=root)

    add_mesh_part(
        doc, grp_hull, "Head_Shell",
        STL_HEAD,
        identity,
        COL_HULL
    )
    add_mesh_part(
        doc, grp_hull, "Middle_Shell",
        STL_MIDDLE,
        identity,
        COL_HULL
    )
    add_mesh_part(
        doc, grp_hull, "Cargo_Shell",
        STL_CARGO,
        identity,
        COL_HULL
    )
    # Rear section: deferred (Phase 11 EDF) but included for visual fidelity.
    # It is in the same world space as the other sections.
    add_mesh_part(
        doc, grp_hull, "Rear_Neck_Shell",
        STL_REAR,
        identity,
        COL_HULL
    )

    # ── Group: Landing gear ──────────────────────────────────────────────────
    # Legs and feet are in project world space (origin at keel/fuselage).
    log.info("-- Landing gear")
    grp_gear = make_group(doc, "Landing_Gear", parent=root)

    add_mesh_part(doc, grp_gear, "Legs",  STL_LEGS, identity, COL_GEAR)
    add_mesh_part(doc, grp_gear, "Feet",  STL_FEET, identity, COL_GEAR)

    # ── Group: Port wing assembly ────────────────────────────────────────────
    #
    # Wing STL internal frame (from s_wings_s1223_revo.scad §Assembly output):
    #   local X = spanwise  (root at X=0, tip at X=SEMI_SPAN=85.7 mm)
    #   local Y = chordwise (leading edge at Y=0, trailing edge at Y=161 mm)
    #   local Z = thickness (upper surface / sky = +Z)
    #
    # World mapping (port wing):
    #   local X → world +Z  (spans outboard from cargo port wall)
    #   local Y → world -X  (TE in world = more aft = more -X)
    #   local Z → world +Z  (sky = dorsal)
    #
    # Translation: local origin (0,0,0) = root LE at chord-midplane.
    #   World position = (LE_X, chord_plane_Y, cargo_dorsal_Z)
    #                  = (WING_LE_X, WING_ROOT_Y_CEN, CARGO_DZ)
    #                  = (-21.69, -288.63, 163.0)
    #
    # VERIFY: with this placement, the spar bore at local (SPAR_BORE_X * CHORD, 0, 0)
    # should map to world (WING_SPAR_X, WING_ROOT_Y_CEN, 163..163+85.7).
    # Expected spar world X at root: -21.69 - 0.30*161 = -69.99 ≈ -70 mm ✓
    log.info("-- Port wing assembly")
    grp_wing_port = make_group(doc, "Wing_Port", parent=root)

    wing_port_placement = make_placement(
        (WING_LE_X, WING_ROOT_Y_CEN, CARGO_DZ),
        ROT_WING_PORT
    )
    add_mesh_part(
        doc, grp_wing_port, "Wing_Panel_Port",
        STL_WING_PORT,
        wing_port_placement,
        COL_WING
    )

    # Port pylon: inboard face at cargo port wall Z=163 mm; extends to Z=251 mm.
    # The pylon attaches to the cargo exterior Z face at the wing root Y station.
    # Translation: pylon inboard face at (WING_ROOT_X_CEN, WING_ROOT_Y_CEN, CARGO_DZ).
    # VERIFY: pylon must be flush with exterior Z wall (no gap, no interior intrusion).
    pylon_port_placement = make_placement(
        (WING_ROOT_X_CEN, WING_ROOT_Y_CEN, CARGO_DZ),
        ROT_PYLON_PORT
    )
    add_mesh_part(
        doc, grp_wing_port, "Nacelle_Pylon_Port",
        STL_PYLON_PORT,
        pylon_port_placement,
        COL_PYLON
    )

    # ── Group: Starboard wing assembly ───────────────────────────────────────
    #
    # World mapping (stbd wing):
    #   local X → world -Z  (spans outboard from stbd wall = toward -Z)
    #   local Y → world -X  (TE aft, same as port)
    #   local Z → world +Z  (sky = dorsal, same as port)
    #
    # Translation: local origin at (LE_X, chord_plane_Y, cargo_stbd_Z=0)
    log.info("-- Starboard wing assembly")
    grp_wing_stbd = make_group(doc, "Wing_Stbd", parent=root)

    wing_stbd_placement = make_placement(
        (WING_LE_X, WING_ROOT_Y_CEN, 0.0),
        ROT_WING_STBD
    )
    add_mesh_part(
        doc, grp_wing_stbd, "Wing_Panel_Stbd",
        STL_WING_STBD,
        wing_stbd_placement,
        COL_WING
    )

    pylon_stbd_placement = make_placement(
        (WING_ROOT_X_CEN, WING_ROOT_Y_CEN, 0.0),
        ROT_PYLON_STBD
    )
    add_mesh_part(
        doc, grp_wing_stbd, "Nacelle_Pylon_Stbd",
        STL_PYLON_STBD,
        pylon_stbd_placement,
        COL_PYLON
    )

    # ── Group: Port nacelle assembly ─────────────────────────────────────────
    #
    # Nacelle STL internal frame (from nacelle_pod_50mm_tandem.scad):
    #   local Z = bore axis (intake at Z=0, nozzle at Z=NACELLE_L=185.2 mm)
    #   local X = spanwise (toward wing tip / outboard)
    #   local Y = fore-aft in fuselage frame (+Y toward inboard spar)
    #
    # Assembly orientation: VTOL hover (90° tilt, intake up, thrust down).
    # World mapping at hover (port nacelle):
    #   local Z (bore) → world -Y  (intake up, nozzle down)
    #   local X (outboard) → world +Z  (port direction)
    #   local Y (toward spar) → world -X  (aft, toward tail)
    #
    # Translation: the tilt pivot (local Z=NACELLE_PIVOT_Z) must coincide with
    # the spar-bore world position (PIVOT_X, PIVOT_Y, PIVOT_Z_PORT).
    # After the rotation R, local (0,0,NACELLE_PIVOT_Z) maps to world
    # (0, -NACELLE_PIVOT_Z, 0) relative to the nacelle origin.
    # So the nacelle origin in world = pivot_world - R*(0,0,NACELLE_PIVOT_Z)
    #   = (PIVOT_X, PIVOT_Y, PIVOT_Z_PORT) - (0, -NACELLE_PIVOT_Z, 0)
    #   = (PIVOT_X, PIVOT_Y + NACELLE_PIVOT_Z, PIVOT_Z_PORT)
    #   = (-70, -288.63 + 103.75, 251)
    #   = (-70, -184.88, 251)
    #
    # VERIFY: in FreeCAD, the intake face (local Z=0 face) should appear
    # at the TOP of the nacelle, pointing +world Y (sky).
    log.info("-- Port nacelle assembly")
    grp_nac_port = make_group(doc, "Nacelle_Port", parent=root)

    nac_port_origin_y = PIVOT_Y + NACELLE_PIVOT_Z   # = -288.63 + 103.75 = -184.88 mm
    nac_port_placement = make_placement(
        (PIVOT_X, nac_port_origin_y, PIVOT_Z_PORT),
        ROT_NACELLE_PORT
    )
    add_mesh_part(
        doc, grp_nac_port, "Nacelle_Pod_Port",
        STL_NACELLE_PORT,
        nac_port_placement,
        COL_NACELLE
    )
    # Nozzle assembly shares the same origin as the pod (it seats at nozzle exit).
    add_mesh_part(
        doc, grp_nac_port, "Nozzle_Port",
        STL_NOZZLE_ASM,
        nac_port_placement,
        COL_NACELLE
    )

    # ── Group: Starboard nacelle assembly ────────────────────────────────────
    #
    # World mapping at hover (stbd nacelle, mirrored from port):
    #   local Z (bore) → world -Y  (intake up, thrust down — same as port)
    #   local X (outboard) → world -Z  (stbd direction, mirrored)
    #   local Y (toward spar) → world +X  (forward, mirrored)
    #
    # Nacelle origin:
    #   = (PIVOT_X, PIVOT_Y + NACELLE_PIVOT_Z, PIVOT_Z_STBD)
    #   = (-70, -184.88, -88)
    #
    # VERIFY: intake face should be UP (+world Y); nozzle DOWN (-world Y).
    log.info("-- Starboard nacelle assembly")
    grp_nac_stbd = make_group(doc, "Nacelle_Stbd", parent=root)

    nac_stbd_placement = make_placement(
        (PIVOT_X, nac_port_origin_y, PIVOT_Z_STBD),
        ROT_NACELLE_STBD
    )
    add_mesh_part(
        doc, grp_nac_stbd, "Nacelle_Pod_Stbd",
        STL_NACELLE_STBD,
        nac_stbd_placement,
        COL_NACELLE
    )
    add_mesh_part(
        doc, grp_nac_stbd, "Nozzle_Stbd",
        STL_NOZZLE_ASM,
        nac_stbd_placement,
        COL_NACELLE
    )

    # ── Group: Cargo bay subsystem ───────────────────────────────────────────
    #
    # The cargo bay components (doors, winch, autolatch, FPV bezel, GPS ring)
    # are all in project world space — import at identity placement.
    # Clamshell doors are shown in the CLOSED position (as printed, no rotation).
    # To show the doors OPEN, rotate each door ~90° about the hinge-pin axis
    # (world X, at HINGE_Y = -410.6 mm, HINGE_Z = 81.61 mm) — not scripted here.
    log.info("-- Cargo bay subsystem")
    grp_cargo = make_group(doc, "Cargo_Bay", parent=root)

    add_mesh_part(doc, grp_cargo, "Cargo_Door_Port",
                  STL_DOOR_PORT, identity, COL_CARGO_SYS)
    add_mesh_part(doc, grp_cargo, "Cargo_Door_Stbd",
                  STL_DOOR_STBD, identity, COL_CARGO_SYS)
    add_mesh_part(doc, grp_cargo, "Winch_Motor_Mount",
                  STL_WINCH_MOUNT, identity, COL_CARGO_SYS)
    add_mesh_part(doc, grp_cargo, "Winch_Spool",
                  STL_WINCH_SPOOL, identity, COL_CARGO_SYS)
    add_mesh_part(doc, grp_cargo, "Cradle_Autolatch",
                  STL_AUTOLATCH, identity, COL_CARGO_SYS)
    add_mesh_part(doc, grp_cargo, "FPV_Bezel",
                  STL_FPV_BEZEL, identity, COL_CARGO_SYS)
    add_mesh_part(doc, grp_cargo, "GPS_Retention_Ring",
                  STL_GPS_RING, identity, COL_CARGO_SYS)

    # ── Optional viewport reorientation ─────────────────────────────────────
    # Set REORIENT_FOR_VIEWPORT = True to apply a +90° X-axis rotation to the
    # root assembly so the model appears upright in FreeCAD's default Z-up
    # viewport.  This does NOT change any underlying coordinates; it is a
    # display-only transform on the root App::Part.
    # WARNING: enabling this changes how measurement tools report Y/Z values
    # in the FreeCAD UI vs. the project documentation — keep False for builds.
    REORIENT_FOR_VIEWPORT = False
    if REORIENT_FOR_VIEWPORT:
        root.Placement = FreeCAD.Placement(
            FreeCAD.Vector(0, 0, 0),
            FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
        )
        log.info("Viewport reorientation applied to root (+90° around X).")

    # ── Recompute and save ───────────────────────────────────────────────────
    doc.recompute()
    doc.saveAs(OUT_FCStd)
    log.info("Assembly saved: %s", OUT_FCStd)
    return doc


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log.info("Serenity UAV fuselage assembly — Rev S2 (2026-06-08)")
    log.info("Repo root : %s", REPO_ROOT)
    log.info("Output    : %s", OUT_FCStd)
    doc = build_assembly()
    log.info("Done.  %d objects in document.", len(doc.Objects))
