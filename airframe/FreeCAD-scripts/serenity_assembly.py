"""
serenity_assembly.py — Serenity UAV full-airframe FreeCAD assembly.
Revision: Q2 (2026-06-10)

Imports all printed airframe STL components, applies coordinate transforms,
and saves a single Serenity-Assembled.FCStd for review in FreeCAD.

Run headlessly (no GUI required):
    /usr/bin/freecad --background --python serenity_assembly.py

Or from the Makefile:
    make assembly   (from airframe/FreeCAD-scripts/)

Output: <repo>/airframe/Serenity-Assembled.FCStd
        (overwrites any existing file)

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0

Coordinate system — 24"-scaled STL world space (hull frame):
    X  positive toward nose (forward)
    Y  positive dorsal (up)
    Z  positive port (left)

Placement data for the eight primary airframe components (four fuselage
sections, port/stbd wings, port/stbd nacelles) was validated by manual
positioning in FreeCAD and extracted from
airframe/freecad/assembly/SerenityAssembly.FCStd (2026-06-10).
Minor joint alignment fine-tuning (fractions of mm / degree) is expected.

All other component placements (cargo accessories, battery tray,
EDF sleeves, nozzles, pylons, tip caps) are approximations and carry
a VERIFY marker indicating they require confirmation in FreeCAD.

Quaternion convention (FreeCAD App.Rotation): (Qx, Qy, Qz, Qw)
    Identity    : (0,   0,  0,  +1)
    90° about −X: (−√½, 0,  0,  +√½)  — Middle_Shell, Rear_Shell
    180° about +Z: (0,  0, +1,   0)   — Cargo_Shell
    270° about +X: (+√½, 0, 0, −√½)  — Nacelles (forward flight / cruise)

References:
    [1] airframe/freecad/assembly/SerenityAssembly.FCStd — validated positions
    [2] airframe/openscad/fuselage/s_head_shell24.scad — hull coordinate def.
    [3] airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad
    [4] CLAUDE.md — project standards.
"""

import os
import sys

import FreeCAD as App
import Mesh

# ---------------------------------------------------------------------------
# Path setup — resolved relative to this script file so the script works
# regardless of the current working directory.
# ---------------------------------------------------------------------------
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
AIRFRAME    = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
STL_DIR     = os.path.join(AIRFRAME, "stls")
OUTPUT      = os.path.join(AIRFRAME, "Serenity-Assembled.FCStd")


# ---------------------------------------------------------------------------
# Validated placement constants — extracted from SerenityAssembly.FCStd,
# manually positioned 2026-06-10.
#
# Tuple format: (Px, Py, Pz, Qx, Qy, Qz, Qw)
#   Position in mm (FreeCAD world space).
#   Rotation as unit quaternion; Qw is the scalar.
#
# _SQ2 = 1/√2 ≈ 0.7071068, shared by all 90°-family rotations.
# ---------------------------------------------------------------------------

_SQ2 = 0.7071067811865476

# -- Fuselage sections -------------------------------------------------------
# Head: no rotation — STL axes already match hull frame.
PL_HEAD_SHELL   = (-331.9993360,  -17.9999640,   60.9998780,    0.0,  0.0,  0.0,   +1.0)

# Cargo: 180° about +Z to flip the section into the hull-forward orientation.
PL_CARGO_SHELL  = (-274.4000100, -282.8000440,    0.0,           0.0,  0.0, +1.0,    0.0)

# Middle / Rear: 90° about −X to rotate the SCAD section axis into hull +Y.
PL_MIDDLE_SHELL = (-350.9992980,  130.4001963,   10.0174324,  -_SQ2,  0.0,  0.0,  +_SQ2)
PL_REAR_SHELL   = (   0.0,        203.1999999,  -31.9999360,  -_SQ2,  0.0,  0.0,  +_SQ2)

# -- Wings -------------------------------------------------------------------
# Identity rotation: port and stbd wing SCAD output axes already align with
# the hull frame for these STLs — no rotation is required.
PL_WING_PORT    = ( -80.9998380,   -6.9999860,   57.9998840,    0.0,  0.0,  0.0,   +1.0)
PL_WING_STBD    = (-261.9994760,  -11.9999760,   57.9998840,    0.0,  0.0,  0.0,   +1.0)

# -- Nacelles (forward-flight / cruise configuration) -----------------------
# 270° about +X places nacelles in cruise attitude (validated in FCStd).
# Hover attitude requires a different rotation.
PL_NACELLE_PORT = (-385.0960040,  -69.9998600,   64.9719300,  +_SQ2,  0.0,  0.0,  -_SQ2)
PL_NACELLE_STBD = (  46.9999060,  -63.9998720,   62.9998740,  +_SQ2,  0.0,  0.0,  -_SQ2)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stl(rel_path):
    """Return absolute path under STL_DIR."""
    return os.path.join(STL_DIR, rel_path)


def add_mesh(doc, stl_path, label):
    """
    Import an STL as a Mesh::Feature in doc.

    Returns the new document object, or None if the file is missing.
    The mesh is imported at the origin with identity orientation; call
    place_mesh() afterwards to position it in the hull frame.
    """
    if not os.path.exists(stl_path):
        print(f"[WARN] STL missing, skipping: {stl_path}", flush=True)
        return None
    mesh_data = Mesh.Mesh(stl_path)
    obj = doc.addObject("Mesh::Feature", label)
    obj.Mesh = mesh_data
    obj.Label = label
    return obj


def place_mesh(obj, placement):
    """
    Apply a validated placement tuple to a Mesh::Feature object.

    placement: (Px, Py, Pz, Qx, Qy, Qz, Qw) — position in mm plus unit
    quaternion (Qx, Qy, Qz, Qw) where Qw is the scalar component.
    Does nothing if obj is None (graceful missing-file handling).
    """
    if obj is None:
        return
    px, py, pz, qx, qy, qz, qw = placement
    obj.Placement = App.Placement(
        App.Vector(px, py, pz),
        App.Rotation(qx, qy, qz, qw)
    )


def transform_mesh(obj, rows):
    """
    Apply a 4×4 transform matrix directly to the mesh geometry of obj.

    rows: 3-tuple or 4-tuple of 4-element rows:
        ( [r0c0, r0c1, r0c2, r0c3],
          [r1c0, r1c1, r1c2, r1c3],
          [r2c0, r2c1, r2c2, r2c3] )
    The fourth row [0,0,0,1] is appended automatically.

    Uses Mesh.Mesh.transform() which supports det = ±1 matrices (improper
    rotations / reflections).  Retained for VERIFY items that require
    matrix-based fine-positioning; prefer place_mesh() for validated parts.
    """
    if obj is None:
        return
    r = [list(row) for row in rows]
    if len(r) == 3:
        r.append([0.0, 0.0, 0.0, 1.0])
    flat = [v for row in r for v in row]
    m = App.Matrix(*flat)
    obj.Mesh.transform(m)


# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------

def assemble():
    """Build the Serenity UAV full-airframe assembly document."""

    print("[assembly] Creating FreeCAD document ...", flush=True)
    doc = App.newDocument("SerenityAssembly")

    # -------------------------------------------------------------------
    # FUSELAGE SECTIONS
    # Placements validated against SerenityAssembly.FCStd (2026-06-10).
    # All four sections are placed as Mesh::Feature objects; they tile
    # into the complete hull without additional offsets.
    # -------------------------------------------------------------------
    print("[assembly] Fuselage sections ...", flush=True)

    head = add_mesh(doc, _stl("fuselage/s_head_shell24_2mm_repaired.stl"), "Head_Shell")
    place_mesh(head, PL_HEAD_SHELL)

    cargo = add_mesh(doc, _stl("fuselage/cargo/s_cargo_sect_shell24_2mm_repaired.stl"), "Cargo_Shell")
    place_mesh(cargo, PL_CARGO_SHELL)

    middle = add_mesh(doc, _stl("fuselage/s_middle_shell24_2mm_repaired.stl"), "Middle_Shell")
    place_mesh(middle, PL_MIDDLE_SHELL)

    # Prefer compiled rear shell; fall back to the repaired 2mm mesh.
    rear_stl = _stl("fuselage/s_rear_shell24.stl")
    if not os.path.exists(rear_stl):
        rear_stl = _stl("fuselage/s_rear_shell24_2mm_repaired.stl")
    rear = add_mesh(doc, rear_stl, "Rear_Shell")
    place_mesh(rear, PL_REAR_SHELL)

    # Landing gear (scaled Thingiverse parts; identity placement)
    add_mesh(doc, _stl("fuselage/s_feet_x_4_scaled24.stl"), "Landing_Feet")
    add_mesh(doc, _stl("fuselage/s_legs_scaled24.stl"),     "Landing_Legs")

    # -------------------------------------------------------------------
    # CARGO BAY SUB-ASSEMBLY
    # These STLs are generated in cargo-section local coordinates; they
    # do not require an additional transform once the Cargo_Shell is placed.
    # VERIFY: confirm alignment against PL_CARGO_SHELL after hull joints
    # are finalised.
    # -------------------------------------------------------------------
    print("[assembly] Cargo bay ...", flush=True)

    cargo_stls = [
        ("fuselage/cargo/cargo_door_port.stl",             "Cargo_Door_Port"),
        ("fuselage/cargo/cargo_door_stbd.stl",             "Cargo_Door_Stbd"),
        ("fuselage/cargo/cargo_cradle_autolatch.stl",      "Cargo_Cradle"),
        ("fuselage/cargo/cargo_fpv_bezel.stl",             "Cargo_FPV_Bezel"),
        ("fuselage/cargo/cargo_gps_retention_ring.stl",    "Cargo_GPS_Ring"),
        ("fuselage/cargo/cargo_winch_motor_mount.stl",     "Cargo_Winch_Mount"),
        ("fuselage/cargo/cargo_winch_spool.stl",           "Cargo_Winch_Spool"),
        ("fuselage/cargo/cargo_drv8833_tray.stl",          "Cargo_DRV8833_Tray"),
        ("fuselage/cargo/cargo_door_servo_bracket.stl",    "Cargo_Door_Servo_Bracket"),
        ("fuselage/cargo/cargo_release_servo_bracket.stl", "Cargo_Release_Servo_Bracket"),
    ]
    for rel, label in cargo_stls:
        add_mesh(doc, _stl(rel), label)

    # -------------------------------------------------------------------
    # FUSELAGE ACCESSORIES (battery tray and belly panel)
    # VERIFY: slide tray along keel until battery CG aligns with FCOG.
    # Translation values below are initial estimates; measure cross-
    # sections in slicer / FreeCAD to confirm before committing.
    # -------------------------------------------------------------------
    print("[assembly] Battery tray and belly panel ...", flush=True)

    tray = add_mesh(doc, _stl("fuselage/battery_tray.stl"), "Battery_Tray")
    if tray:
        transform_mesh(tray, [
            [1, 0, 0,  172.0],   # VERIFY: X offset (fore edge at station 112 mm)
            [0, 1, 0, -263.0],   # VERIFY: Y (keel underside, ≈ CY_head - TRAY_H)
            [0, 0, 1,   41.0],   # VERIFY: Z (centred: CZ_hull - TRAY_W/2)
        ])

    panel = add_mesh(doc, _stl("fuselage/belly_panel.stl"), "Belly_Panel")
    if panel:
        transform_mesh(panel, [
            [1, 0, 0,  172.0],   # VERIFY: aligns with tray opening
            [0, 1, 0, -267.0],   # VERIFY: flush with belly skin
            [0, 0, 1,   41.0],   # VERIFY: centred under tray
        ])

    # -------------------------------------------------------------------
    # WINGS
    # Placements validated against SerenityAssembly.FCStd (2026-06-10).
    # Both wing STLs use identity rotation; the SCAD output axes already
    # align with the hull frame for s_wing_{port,stbd}_s1223_revo.stl.
    # -------------------------------------------------------------------
    print("[assembly] Wings ...", flush=True)

    port_wing = add_mesh(doc, _stl("wings/s_wing_port_s1223_revo.stl"), "Wing_Port")
    place_mesh(port_wing, PL_WING_PORT)

    stbd_wing = add_mesh(doc, _stl("wings/s_wing_stbd_s1223_revo.stl"), "Wing_Stbd")
    place_mesh(stbd_wing, PL_WING_STBD)

    # -------------------------------------------------------------------
    # NACELLE TILT PYLONS
    # VERIFY: pylon placements have not been validated in FreeCAD.
    # Pylons mount at the wing root; place_mesh() calls will be added
    # once the pylon STL axes are confirmed against the wing geometry.
    # -------------------------------------------------------------------
    print("[assembly] Nacelle tilt pylons ...", flush=True)

    add_mesh(doc, _stl("wings/s_wing_nacelle_pylon_revo.stl"), "Pylon_Port")
    add_mesh(doc, _stl("wings/s_wing_nacelle_pylon_revo.stl"), "Pylon_Stbd")

    # -------------------------------------------------------------------
    # NACELLE PODS (forward-flight / cruise configuration)
    # Placements validated against SerenityAssembly.FCStd (2026-06-10).
    # Rev Q nacelle STLs (nacelle_port/stbd_revq.stl).
    # 270° about +X is the cruise attitude; hover requires a different rotation.
    # -------------------------------------------------------------------
    print("[assembly] Nacelle pods ...", flush=True)

    port_nac = add_mesh(doc, _stl("nacelles/nacelle_port_revq.stl"), "Nacelle_Port")
    place_mesh(port_nac, PL_NACELLE_PORT)

    stbd_nac = add_mesh(doc, _stl("nacelles/nacelle_stbd_revq.stl"), "Nacelle_Stbd")
    place_mesh(stbd_nac, PL_NACELLE_STBD)

    # -------------------------------------------------------------------
    # NACELLE INTERNAL COMPONENTS (EDF sleeves, nozzles, gear train)
    # VERIFY: sub-component placements not yet validated in FreeCAD.
    # These parts are coaxial with the nacelle pod; world-space placements
    # are derived by composing PL_NACELLE_PORT/STBD with each component's
    # axial Z offset.  Add place_mesh() calls here once nacelle Z offsets
    # are confirmed against the printed nacelle geometry.
    #
    # Parts pending placement:
    #   nacelles/edf_stator_sleeve.stl      (Z_centre ≈ 106.25 mm)
    #   nacelles/edf_aft_spider_sleeve.stl  (Z_centre ≈ 144.375 mm)
    #   nacelles/nozzles/nacelle_nozzle_iris.stl  (Z_boss ≈ 166.25 mm)
    #   nacelles/nacelle_bevel_housing.stl
    #   nacelles/nacelle_bevel_pair.stl
    #   nacelles/nacelle_tip_cap_port.stl
    #   nacelles/nacelle_tip_cap_stbd.stl
    # -------------------------------------------------------------------

    # -------------------------------------------------------------------
    # DORSAL ANTENNA FIN
    # VERIFY: position not yet validated in FreeCAD.
    # -------------------------------------------------------------------
    add_mesh(doc, _stl("fuselage/dorsal_antenna_fin.stl"), "Dorsal_Antenna_Fin")

    # -------------------------------------------------------------------
    # Recompute and save
    # -------------------------------------------------------------------
    print("[assembly] Recomputing ...", flush=True)
    doc.recompute()

    print(f"[assembly] Saving → {OUTPUT}", flush=True)
    doc.save(OUTPUT)
    print("[assembly] Complete.", flush=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    assemble()
