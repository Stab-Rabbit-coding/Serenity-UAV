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

import math
import os

import FreeCAD as App
import Mesh

# ---------------------------------------------------------------------------
# Path setup — resolved relative to this script file so the script works
# regardless of the current working directory.
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AIRFRAME = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
STL_DIR = os.path.join(AIRFRAME, "stls")
OUTPUT = os.path.join(AIRFRAME, "Serenity-Assembled.FCStd")


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
    obj.Placement = App.Placement(App.Vector(px, py, pz), App.Rotation(qx, qy, qz, qw))


def transform_mesh(obj, rows):
    """
    Apply a 4×4 transform matrix directly to the mesh geometry of obj.

    rows: 3-tuple or 4-tuple of 4-element rows:
        [r0c0, r0c1, r0c2, r0c3]
        [r1c0, r1c1, r1c2, r1c3]
        [r2c0, r2c1, r2c2, r2c3]
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
# Nacelle-internal sub-component placement (Rev R1.1, 2026-06-21)
#
# The nacelle pods (nacelle_port_revq.stl / nacelle_stbd_revq.stl) are
# generated from airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad in
# a part-local frame: local +Z is the duct/bore axis (intake at Z = 0,
# nozzle exit at Z = NACELLE_L = 185.2 mm), local X is the spanwise/pylon
# axis, and local Y is the third (mesh-offset) axis.  This is exactly the
# STL vertex frame that tools/bake_hull_frame.py bakes via
# COMPONENTS['Nacelle_Port'] / ['Nacelle_Stbd'].  Every internal mechanism
# part below (gears, sleeves, nozzle, etc.) is modelled in SCAD using this
# SAME nacelle-local frame, so each part's hull-frame placement is the
# nacelle's own bake transform applied to the part's local offset:
#
#     T_hull = T_nacelle_bake  o  T_subcomponent_local
#
# Both nacelles share one bake rotation quaternion — only the translation
# differs (tools/bake_hull_frame.py COMPONENTS).  Expanding that
# quaternion (Qx, Qy, Qz, Qw) = (+SQ2, 0, 0, -SQ2) with the same
# quat_to_matrix() expansion bake_hull_frame.py uses gives the fixed
# rotation R_BAKE below:
#     hull_x =  x_local
#     hull_y =  z_local
#     hull_z = -y_local
# None of the placements built from this composition have been visually
# validated in FreeCAD — every entry uses transform_mesh() (the VERIFY-
# tier helper), never place_mesh().
# ---------------------------------------------------------------------------

# Fixed nacelle bake rotation — identical for port and stbd (see derivation
# above).  hull = R_BAKE @ local + T_BAKE[side].
R_BAKE = (
    (1.0, 0.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, -1.0, 0.0),
)

# Per-side bake translation, copied as plain numbers from
# tools/bake_hull_frame.py COMPONENTS['Nacelle_Port'] / ['Nacelle_Stbd']
# (that file remains the single source of truth for the primary nacelle
# placement; these values are not re-derived here).
T_BAKE = {
    "port": (46.9999060, -63.9998720, 62.9998740),
    "stbd": (-385.0960040, -69.9998600, 64.9719300),
}

# Nacelle pylon-side sign, matching nacelle_pod_50mm_tandem.scad's
# PYLON_SIDE override table (Rev R1/nacelle-swap, 2026-06-11):
#   Port nacelle (hull +X): PYLON_SIDE = -1 (inboard/pylon face at local X = -34)
#   Stbd nacelle (hull -X): PYLON_SIDE = +1 (inboard/pylon face at local X = +34)
PYLON_SIDE = {"port": -1.0, "stbd": +1.0}

_IDENTITY3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def _mat3_mul(a, b):
    """Return the 3x3 product a @ b (nested tuples)."""
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
        for i in range(3)
    )


def _mat3_vec(a, v):
    """Return the 3-vector product a @ v."""
    return tuple(sum(a[i][k] * v[k] for k in range(3)) for i in range(3))


def _rot_y(deg):
    """3x3 rotation about Y by deg, matching OpenSCAD's rotate([0, deg, 0])."""
    rad = math.radians(deg)
    c, s = math.cos(rad), math.sin(rad)
    return (
        (c, 0.0, s),
        (0.0, 1.0, 0.0),
        (-s, 0.0, c),
    )


def nacelle_rows(side, r_local, t_local):
    """
    Compose a nacelle sub-component's local placement into transform_mesh()
    rows in hull frame.

    side: "port" or "stbd".
    r_local: 3x3 rotation (nested tuples) of the part within the nacelle's
        own local frame; use _IDENTITY3 if the part's modelled axes
        already align with the nacelle frame.
    t_local: (x, y, z) translation in mm of the part's origin within the
        nacelle's own local frame.
    """
    r_total = _mat3_mul(R_BAKE, r_local)
    t_rot = _mat3_vec(R_BAKE, t_local)
    t_bake = T_BAKE[side]
    t_total = tuple(t_rot[i] + t_bake[i] for i in range(3))
    return [
        [r_total[0][0], r_total[0][1], r_total[0][2], t_total[0]],
        [r_total[1][0], r_total[1][1], r_total[1][2], t_total[1]],
        [r_total[2][0], r_total[2][1], r_total[2][2], t_total[2]],
    ]


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

    cargo = add_mesh(
        doc, _stl("fuselage/cargo/s_cargo_sect_shell24_2mm_repaired.stl"), "Cargo_Shell"
    )
    place_mesh(cargo, PL_IDENTITY)

    middle = add_mesh(
        doc, _stl("fuselage/s_middle_shell24_2mm_repaired.stl"), "Middle_Shell"
    )
    place_mesh(middle, PL_IDENTITY)

    # R1: the baked repaired mesh is the canonical rear shell.  (The
    # former preference for a compiled s_rear_shell24.stl is removed —
    # a freshly compiled, un-baked file must not bypass the bake step.)
    rear = add_mesh(doc, _stl("fuselage/s_rear_shell24_2mm_repaired.stl"), "Rear_Shell")
    place_mesh(rear, PL_IDENTITY)

    # Landing gear (scaled Thingiverse parts; identity placement)
    add_mesh(doc, _stl("fuselage/feet_x_4_scaled24.stl"), "Landing_Feet")
    add_mesh(doc, _stl("fuselage/legs_scaled24.stl"), "Landing_Legs")

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
        ("fuselage/cargo/cargo_door_port.stl", "Cargo_Door_Port"),
        ("fuselage/cargo/cargo_door_stbd.stl", "Cargo_Door_Stbd"),
        ("fuselage/cargo/cargo_cradle_autolatch.stl", "Cargo_Cradle"),
        ("fuselage/cargo/cargo_fpv_bezel.stl", "Cargo_FPV_Bezel"),
        ("fuselage/cargo/cargo_gps_retention_ring.stl", "Cargo_GPS_Ring"),
        ("fuselage/cargo/cargo_winch_motor_mount.stl", "Cargo_Winch_Mount"),
        ("fuselage/cargo/cargo_winch_spool.stl", "Cargo_Winch_Spool"),
        ("fuselage/cargo/cargo_drv8833_tray.stl", "Cargo_DRV8833_Tray"),
        ("fuselage/cargo/cargo_door_servo_bracket.stl", "Cargo_Door_Servo_Bracket"),
        (
            "fuselage/cargo/cargo_release_servo_bracket.stl",
            "Cargo_Release_Servo_Bracket",
        ),
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
        transform_mesh(
            tray,
            [
                [1, 0, 0, 172.0],  # VERIFY: X offset (fore edge at station 112 mm)
                [0, 1, 0, -263.0],  # VERIFY: Y (keel underside, ≈ CY_head - TRAY_H)
                [0, 0, 1, 41.0],  # VERIFY: Z (centred: CZ_hull - TRAY_W/2)
            ],
        )

    panel = add_mesh(doc, _stl("fuselage/belly_panel.stl"), "Belly_Panel")
    if panel:
        transform_mesh(
            panel,
            [
                [1, 0, 0, 172.0],  # VERIFY: aligns with tray opening
                [0, 1, 0, -267.0],  # VERIFY: flush with belly skin
                [0, 0, 1, 41.0],  # VERIFY: centred under tray
            ],
        )

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
    # NACELLE INTERNAL COMPONENTS (gear train, nozzle iris, EDF sleeves)
    # VERIFY: none of these sub-component placements have been validated
    # in FreeCAD; every entry below uses transform_mesh() via the
    # nacelle_rows() helper (see derivation comment above add_mesh()).
    # Station constants are taken from
    # airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad — the
    # canonical gear-train + iris-nozzle nacelle variant (TODO.md §1.1.3
    # build-task list references only this variant; the parallel
    # no-gear-train "_simple"/"_straight" variant is not on the tracked
    # build path and is NOT placed here).
    # -------------------------------------------------------------------
    print(
        "[assembly] Nacelle internal components (gear train, nozzle, sleeves) ...",
        flush=True,
    )

    # Nacelle local-frame Z stations, mm (nacelle_pod_50mm_tandem.scad):
    #   intake Z=0 .. STATOR_SLV_Z_START=90.0 .. AFT_SLV_Z_START=122.5 ..
    #   NOZZLE_RING_Z(=CROWN_Z)=166.25 .. NACELLE_L=185.2 (nozzle exit).
    #   PIVOT_Z is the gear-train station, inside the sleeve span.
    STATOR_SLV_Z_START = 90.0
    AFT_SLV_Z_START = 122.5
    PIVOT_Z = 103.75  # gear-train station = nacelle CG
    PINION_A_Y = 28.0  # = sector R(22) + pinion R(6), mm
    CROWN_Z = 166.25  # = NOZZLE_RING_Z
    NACELLE_FACE_X_PYLON = 34.0  # mm, inboard (pylon-side) X face
    NACELLE_FACE_X_FAR = 38.0  # mm, outboard (tip) X face

    for side in ("port", "stbd"):
        label = "Port" if side == "port" else "Stbd"
        pylon = PYLON_SIDE[side]

        # ── EDF1/EDF2 inter-stage stator sleeve ──────────────────────────
        # edf_stator_sleeve.scad: part-local frame is coaxial with the
        # nacelle duct (own local +Z = nacelle local +Z; sleeve forward
        # face at its own Z = 0) — identity rotation, translate to the
        # sleeve's forward-face station.
        sleeve = add_mesh(
            doc,
            _stl("nacelles/edf_stator_sleeve.stl"),
            f"Nacelle_{label}_Stator_Sleeve",
        )
        transform_mesh(
            sleeve, nacelle_rows(side, _IDENTITY3, (0.0, 0.0, STATOR_SLV_Z_START))
        )

        # ── EDF2 aft spider sleeve ────────────────────────────────────────
        # edf_aft_spider_sleeve.scad: same coaxial convention, forward
        # face at nacelle Z = AFT_SLV_Z_START.
        aft_sleeve = add_mesh(
            doc,
            _stl("nacelles/edf_aft_spider_sleeve.stl"),
            f"Nacelle_{label}_Aft_Spider_Sleeve",
        )
        transform_mesh(
            aft_sleeve, nacelle_rows(side, _IDENTITY3, (0.0, 0.0, AFT_SLV_Z_START))
        )

        # ── Drive Pinion A (meshes the fixed sector gear) ────────────────
        # nacelle_pod_50mm_tandem.scad pinion_a_boss(): rotate([0,90,0])
        # then translate([0, PINION_A_Y, PIVOT_Z]) — bore axis along
        # local X (parallel to the pivot axis, matching the sector-gear
        # mesh).  nacelle_pinion.stl is modelled coaxial with its own
        # local Z by default (standard print orientation for a gear
        # blank), so the same Y-axis 90 deg rotation aligns it.
        pinion_a = add_mesh(
            doc, _stl("nacelles/nacelle_pinion.stl"), f"Nacelle_{label}_Drive_Pinion_A"
        )
        transform_mesh(
            pinion_a, nacelle_rows(side, _rot_y(90.0), (0.0, PINION_A_Y, PIVOT_Z))
        )

        # ── Crown Pinion (drives the nozzle-ring rack) ───────────────────
        # BUG FLAG (2026-06-21): nacelle_pod_50mm_tandem.scad's
        # crown_pinion_boss() copies pinion_a_boss()'s rotate([0,90,0])
        # X-axis-bore pattern verbatim.  Both nacelle_pinion.scad
        # ("mounted on the longitudinal shaft (nacelle Z-axis)") and
        # nacelle_bevel_housing.scad ("Longitudinal bore (Z-axis): houses
        # Bevel Gear B + longitudinal shaft") independently document the
        # Crown Pinion as Z-axis (no rotation).  Placed here with the
        # DOCUMENTED-CORRECT identity rotation, not the boss's coded
        # rotation — the boss code, not this placement, is what needs
        # fixing (TODO.md §1.1.3).
        crown_pinion = add_mesh(
            doc, _stl("nacelles/nacelle_pinion.stl"), f"Nacelle_{label}_Crown_Pinion"
        )
        transform_mesh(
            crown_pinion, nacelle_rows(side, _IDENTITY3, (0.0, PINION_A_Y, CROWN_Z))
        )

        # ── Bevel gear housing ────────────────────────────────────────────
        # nacelle_bevel_housing.scad: origin = block centroid = the point
        # where the transverse (X) and longitudinal (Z) bores intersect —
        # the same point as the Drive Pinion A shaft / sector-gear mesh
        # centre.  Housing header states its own axes already align with
        # the nacelle frame ("+Z = toward nozzle, +X = toward sector gear
        # / pinion A mesh side, +Y = outboard face") — identity rotation.
        housing = add_mesh(
            doc,
            _stl("nacelles/nacelle_bevel_housing.stl"),
            f"Nacelle_{label}_Bevel_Housing",
        )
        transform_mesh(
            housing, nacelle_rows(side, _IDENTITY3, (0.0, PINION_A_Y, PIVOT_Z))
        )

        # ── Bevel gear pair (A + B, pre-meshed single STL) ───────────────
        # Seats inside the housing at the same bore-intersection point.
        bevel_pair = add_mesh(
            doc, _stl("nacelles/nacelle_bevel_pair.stl"), f"Nacelle_{label}_Bevel_Pair"
        )
        transform_mesh(
            bevel_pair, nacelle_rows(side, _IDENTITY3, (0.0, PINION_A_Y, PIVOT_Z))
        )

        # ── Fixed sector gear ─────────────────────────────────────────────
        # Mounted to the fuselage/pylon tilt bracket, NOT the nacelle —
        # coaxial with the pivot axis, so it does not rotate with nacelle
        # tilt.  Approximated here at the pylon-side X face, on the pivot
        # axis (Y=0, Z=PIVOT_Z); no SCAD source for the tilt bracket
        # itself was found, so the exact standoff distance from the
        # nacelle face is unconfirmed — VERIFY against the bracket
        # geometry once it exists (TODO.md §1.1.3).  Same rotation as
        # Drive Pinion A (axis parallel to local X) since the two gears
        # mesh together.
        sector_x = pylon * NACELLE_FACE_X_PYLON
        sector_gear = add_mesh(
            doc,
            _stl("nacelles/nacelle_sector_gear.stl"),
            f"Nacelle_{label}_Sector_Gear",
        )
        transform_mesh(
            sector_gear, nacelle_rows(side, _rot_y(90.0), (sector_x, 0.0, PIVOT_Z))
        )

        # ── Nozzle iris assembly ──────────────────────────────────────────
        # nacelle_nozzle_iris.stl is the combined render (inner ring +
        # outer housing + 8 petals at the closed position) from
        # nacelle_nozzle_iris.scad; rotationally symmetric about the bore
        # axis, so identity rotation is a low-risk assumption.  Translate
        # to NOZZLE_RING_Z (= CROWN_Z).
        # SCRATCH-PAD FLAG (2026-06-21): nacelle_nozzle_iris.scad's own
        # comments (~lines 118-125) contain an unresolved author
        # scratch-pad computing three different candidate mesh radii
        # (28/37/31/38 mm) for the Crown-Pinion-to-rack distance, ending
        # mid-thought ("Wait —") with no value ever chosen.  This
        # placement uses the nacelle pod file's actual CODED Crown Pinion
        # offset (Y = 28 mm, shared with Pinion A for shaft-conduit
        # continuity) since that is what is physically built into the
        # printed parts; the nozzle_iris.scad radius math should be
        # reconciled against it (TODO.md §1.1.3).
        nozzle = add_mesh(
            doc,
            _stl("nacelles/nozzles/nacelle_nozzle_iris.stl"),
            f"Nacelle_{label}_Nozzle_Iris",
        )
        transform_mesh(nozzle, nacelle_rows(side, _IDENTITY3, (0.0, 0.0, CROWN_Z)))

        # ── Tip cap (outboard X-face end cap) ─────────────────────────────
        # NO ACTIVE SCAD SOURCE EXISTS for nacelle_tip_cap_port/stbd.stl
        # (confirmed via repo-wide search, 2026-06-21) — local-frame axis
        # convention is UNVALIDATED.  Placed at the outboard (far) X face
        # on the pivot Z station as a best-guess VERIFY placeholder;
        # confirm or replace once a source file or a manual FreeCAD
        # placement exists (TODO.md §1.1.3).
        tip_x = -pylon * NACELLE_FACE_X_FAR
        tip_cap = add_mesh(
            doc,
            _stl(f"nacelles/nacelle_tip_cap_{side}.stl"),
            f"Nacelle_{label}_Tip_Cap",
        )
        transform_mesh(tip_cap, nacelle_rows(side, _IDENTITY3, (tip_x, 0.0, PIVOT_Z)))

    # -------------------------------------------------------------------
    # NACELLE SERVO BRACKET — left UNPLACED pending manual resolution
    # (Rev R1.1 audit, 2026-06-21).
    #
    # nacelle_servo_bracket.stl mounts to the nacelle_servo_mount_block()
    # pad in cargo_sect_shell24.scad, NOT to the nacelle, so its placement
    # must compose with Cargo_Shell's bake transform, not the nacelle's.
    # Working through cargo_sect_shell24.scad's NSVMT_X_CEN / NSVMT_Y_CEN
    # / z_sign logic gives a pad centre of local (X=-147.59, Y=-288.63,
    # Z=157.2) for z_sign=+1 ("port wall" per that file's own comment) and
    # local (X=-147.59, Y=-288.63, Z=6.0) for z_sign=-1 ("stbd wall") —
    # i.e. the two pads differ ONLY in local Z, not in lateral position.
    # Cargo_Shell's validated bake transform leaves Z unchanged
    # (hull_Z = local_Z; see cargo_sect_shell24.scad header), so this
    # would place one pad near hull Z=157 mm and the other near hull
    # Z=6 mm — neither of which falls within either nacelle's validated
    # hull-Z span (Nacelle_Port +21.4..+104.7, Nacelle_Stbd +23.3..+106.6
    # per CLAUDE.md).  cargo_sect_shell24.scad's z_sign "port wall"/"stbd
    # wall" labelling therefore predates the hull-frame standard and does
    # NOT correspond to the validated hull Z axis — a confident placement
    # here would be actively wrong, not merely unvalidated.  Left
    # unplaced (add_mesh() only, origin/identity) pending the user doing
    # a manual placement in FreeCAD per CLAUDE.md; see TODO.md §1.1.3.
    # -------------------------------------------------------------------
    add_mesh(
        doc, _stl("nacelles/nacelle_servo_bracket.stl"), "Nacelle_Servo_Bracket_Port"
    )
    add_mesh(
        doc, _stl("nacelles/nacelle_servo_bracket.stl"), "Nacelle_Servo_Bracket_Stbd"
    )

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
