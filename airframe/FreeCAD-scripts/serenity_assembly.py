"""
serenity_assembly.py — Serenity UAV full-airframe FreeCAD assembly.
Revision: R1 (2026-06-11)

Imports all printed airframe STL components and saves a single
Serenity-Assembled.FCStd for review in FreeCAD.

Run headlessly (no GUI required):
    freecadcmd airframe/FreeCAD-scripts/serenity_assembly.py

Or from the Makefile:
    make assembly   (from airframe/FreeCAD-scripts/)

Output: <repo>/airframe/Serenity-Assembled.FCStd
        (overwrites any existing file)

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0

Coordinate system — hull frame (canonical, CLAUDE.md):
    X  positive port (left)
    Y  positive aft (back)
    Z  positive dorsal (up)
    Origin: SerenityAssembly.FCStd world origin.

R1 COORDINATE STANDARDISATION (2026-06-11):
    The validated placements for the eight primary airframe components
    (four fuselage sections, port/stbd wings, port/stbd nacelles) —
    manually positioned in FreeCAD and extracted from
    airframe/freecad/assembly/SerenityAssembly.FCStd on 2026-06-10 —
    are now BAKED INTO THE STL VERTEX DATA by tools/bake_hull_frame.py.
    Every primary STL in airframe/stls/ is therefore stored directly in
    hull-frame coordinates and is imported here with an IDENTITY
    placement.  The historical placement constants (the former PL_*
    tuples) live on as the single source of truth in
    tools/bake_hull_frame.py COMPONENTS; after regenerating any primary
    STL from its SCAD/Blender source, re-run that tool before use.
    Baked files carry the marker "SerenityUAV HULL-FRAME R1" in their
    binary STL header and are never double-transformed.

    Nacelle STLs are stored in cruise / forward-flight attitude (the
    validated assembly attitude).  Hover tilt is a rotation about the
    nacelle pivot applied downstream, not a stored orientation.

All other component placements (cargo accessories, battery tray,
EDF sleeves, nozzles, pylons, tip caps) are approximations and carry
a VERIFY marker indicating they require confirmation in FreeCAD.

References:
    [1] airframe/freecad/assembly/SerenityAssembly.FCStd — validated
        positions (pre-bake; placements now identity after R1).
    [2] tools/bake_hull_frame.py — canonical bake transforms.
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
# R1: The eight primary components import with IDENTITY placements.
#
# The validated placement tuples that previously lived here (PL_HEAD_SHELL,
# PL_CARGO_SHELL, PL_MIDDLE_SHELL, PL_REAR_SHELL, PL_WING_PORT, PL_WING_STBD,
# PL_NACELLE_PORT, PL_NACELLE_STBD) were baked into the STL vertex data on
# 2026-06-11 and now reside solely in tools/bake_hull_frame.py COMPONENTS.
# Do not reintroduce per-part transforms here; if a primary STL is
# regenerated from source, re-run tools/bake_hull_frame.py instead.
# ---------------------------------------------------------------------------

# Identity placement shared by all baked hull-frame components.
PL_IDENTITY = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)


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
    # R1: STL vertex data is already hull-frame (baked 2026-06-11 by
    # tools/bake_hull_frame.py); all four sections import at identity
    # and tile into the complete hull without additional offsets.
    # -------------------------------------------------------------------
    print("[assembly] Fuselage sections ...", flush=True)

    head = add_mesh(doc, _stl("fuselage/s_head_shell24_2mm_repaired.stl"), "Head_Shell")
    place_mesh(head, PL_IDENTITY)

    cargo = add_mesh(doc, _stl("fuselage/cargo/s_cargo_sect_shell24_2mm_repaired.stl"), "Cargo_Shell")
    place_mesh(cargo, PL_IDENTITY)

    middle = add_mesh(doc, _stl("fuselage/s_middle_shell24_2mm_repaired.stl"), "Middle_Shell")
    place_mesh(middle, PL_IDENTITY)

    # R1: the baked repaired mesh is the canonical rear shell.  (The
    # former preference for a compiled s_rear_shell24.stl is removed —
    # a freshly compiled, un-baked file must not bypass the bake step.)
    rear = add_mesh(doc, _stl("fuselage/s_rear_shell24_2mm_repaired.stl"), "Rear_Shell")
    place_mesh(rear, PL_IDENTITY)

    # Landing gear (scaled Thingiverse parts; identity placement)
    add_mesh(doc, _stl("fuselage/feet_x_4_scaled24.stl"), "Landing_Feet")
    add_mesh(doc, _stl("fuselage/legs_scaled24.stl"),     "Landing_Legs")

    # -------------------------------------------------------------------
    # CARGO BAY SUB-ASSEMBLY
    # R1 coordinate audit (2026-06-11):
    #   - cargo_door_port/stbd.stl were generated 2026-06-01 from the
    #     pre-repair Rev-O shell pose and do NOT align with the
    #     validated (now baked) Cargo_Shell orientation.  Regenerate
    #     them from the baked shell via generate_cargo_doors.py, then
    #     verify belly (−Z) orientation — tracked in TODO.md §1.1.1.2.1.
    #   - The eight cargo mounts are part-local prints centred on their
    #     own origins; they have never been positioned in hull frame.
    # VERIFY: all eleven accessories below require hull-frame placement
    # validation against the baked Cargo_Shell.
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
    # R1: baked hull-frame STLs — identity placement.
    # -------------------------------------------------------------------
    print("[assembly] Wings ...", flush=True)

    port_wing = add_mesh(doc, _stl("wings/s_wing_port_s1223_revo.stl"), "Wing_Port")
    place_mesh(port_wing, PL_IDENTITY)

    stbd_wing = add_mesh(doc, _stl("wings/s_wing_stbd_s1223_revo.stl"), "Wing_Stbd")
    place_mesh(stbd_wing, PL_IDENTITY)

    # -------------------------------------------------------------------
    # NACELLE TILT PYLONS
    # VERIFY: pylon placements have not been validated in FreeCAD.
    # Pylons mount at the wing root; place_mesh() calls will be added
    # once the pylon STL axes are confirmed against the wing geometry.
    # -------------------------------------------------------------------
    print("[assembly] Nacelle tilt pylons ...", flush=True)

    add_mesh(doc, _stl("wings/wing_nacelle_pylon_revo.stl"), "Pylon_Port")
    add_mesh(doc, _stl("wings/wing_nacelle_pylon_revo.stl"), "Pylon_Stbd")

    # -------------------------------------------------------------------
    # NACELLE PODS (forward-flight / cruise configuration)
    # R1: baked hull-frame STLs — identity placement; stored attitude is
    # cruise.  Hover is a downstream rotation about the tilt pivot.
    #
    # nacelle_port_revq.stl: hull +X (port side), SWIRL_DIR=-1 (CCW),
    #   harness conduit exits -X (inboard) face.
    # nacelle_stbd_revq.stl: hull -X (starboard side), SWIRL_DIR=+1 (CW),
    #   harness conduit exits +X (inboard) face.
    # Labels corrected Rev R1/nacelle-swap (2026-06-11) after FreeCAD
    # layout inspection confirmed the original naming was inverted.
    # -------------------------------------------------------------------
    print("[assembly] Nacelle pods ...", flush=True)

    port_nac = add_mesh(doc, _stl("nacelles/nacelle_port_revq.stl"), "Nacelle_Port")
    place_mesh(port_nac, PL_IDENTITY)

    stbd_nac = add_mesh(doc, _stl("nacelles/nacelle_stbd_revq.stl"), "Nacelle_Stbd")
    place_mesh(stbd_nac, PL_IDENTITY)

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
    # FreeCAD 1.0: Document.save() takes no path — saveAs() sets the
    # file name and writes the document in one call.
    doc.saveAs(OUTPUT)
    print("[assembly] Complete.", flush=True)


# ---------------------------------------------------------------------------
# Entry point
#
# Under "freecadcmd serenity_assembly.py" the executed module's __name__
# is the file stem ("serenity_assembly"), not "__main__" — accept both
# so the script runs in either invocation (verified FreeCAD 1.0.0,
# 2026-06-11).
# ---------------------------------------------------------------------------
if __name__ in ("__main__", "serenity_assembly"):
    assemble()
