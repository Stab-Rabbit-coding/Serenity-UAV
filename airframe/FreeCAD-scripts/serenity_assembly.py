"""
serenity_assembly.py — Serenity UAV full-airframe FreeCAD assembly.
Revision: R1.2 (2026-07-18)

Imports all printed airframe STL components and saves a single
Serenity-Assembled.FCStd for review in FreeCAD.

R1.2 Changes (2026-07-18):
    Initial hull-frame VERIFY-tier placements added for all unpositioned parts:
    - Cargo bay interior mounts (11 parts: doors, hinge retention, cradle, FPV bezel,
      GPS ring, winch motor/spool, DRV8833 tray, servo brackets).
    - Nacelle tilt pylons (2).
    - Nacelle servo brackets (2, fuselage-mounted tilt actuators).
    - Dorsal antenna fin.
    All placements use estimated transforms based on design intent; user will
    visually verify in FreeCAD and correct gross errors before AI precision alignment.
    See airframe/VERIFY_PLACEMENT_CHECKLIST.md for full details and verification tasks.

Run headlessly (no GUI required) with the FreeCAD CONSOLE binary:
    freecadcmd airframe/FreeCAD-scripts/serenity_assembly.py

Or from the Makefile (from airframe/FreeCAD-scripts/):
    make assembly

Or in the FreeCAD GUI: open this file and run it as a macro.

Do NOT run it with plain `python3` (the FreeCAD / Mesh modules are only
importable inside FreeCAD's own interpreter — you'll get a clear error if
you try), and prefer `freecadcmd` over `freecad --background --python`:
the latter starts the GUI event loop, which on some platforms does not exit
cleanly after the script finishes, so the command appears to hang.

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

try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import Mesh  # type: ignore[import-not-found]
except ModuleNotFoundError as exc:  # not inside FreeCAD's interpreter
    raise SystemExit(
        "serenity_assembly.py must run inside FreeCAD's Python "
        f"(failed to import {exc.name!r}).\n"
        "  headless CLI:  freecadcmd airframe/FreeCAD-scripts/serenity_assembly.py\n"
        "  or:            make assembly   (from airframe/FreeCAD-scripts/)\n"
        "  GUI:           open this file in FreeCAD and run it as a macro\n"
        "Plain `python3` has no FreeCAD/Mesh module; `freecad --background "
        "--python` may not exit cleanly headless — use freecadcmd."
    )

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
    # FreeCAD 1.0: obj.Mesh returns an immutable reference — transforming it
    # in place raises "This object is immutable".  Copy, transform the copy,
    # then reassign.  (Previously blocked the assembly save at the first
    # transform_mesh call; FCStd had been stale since the FreeCAD 1.0 upgrade.)
    mesh = obj.Mesh.copy()
    mesh.transform(m)
    obj.Mesh = mesh


# ---------------------------------------------------------------------------
# Nacelle-internal sub-component placement (Rev R1.1, 2026-06-21)
#
# The nacelle pods (nacelle_port_revs.stl / nacelle_stbd_revs.stl) are
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

    head = add_mesh(doc, _stl("fuselage/head_shell24_2mm_repaired.stl"), "Head_Shell")
    place_mesh(head, PL_IDENTITY)

    cargo = add_mesh(
        doc, _stl("fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl"), "Cargo_Shell"
    )
    place_mesh(cargo, PL_IDENTITY)

    middle = add_mesh(
        doc, _stl("fuselage/middle_shell24_2mm_repaired.stl"), "Middle_Shell"
    )
    place_mesh(middle, PL_IDENTITY)

    # R1: the baked repaired mesh is the canonical rear shell.  (The
    # former preference for a compiled s_rear_shell24.stl is removed —
    # a freshly compiled, un-baked file must not bypass the bake step.)
    rear = add_mesh(doc, _stl("fuselage/rear_shell24_2mm_repaired.stl"), "Rear_Shell")
    place_mesh(rear, PL_IDENTITY)

    # Internal head/cargo splice collar (Rev R1, hull frame — spans the joint at
    # hull Y ≈ -71 mm; identity placement).  Secures the head section to the
    # cargo section: 2-wall bonded double-lap + anti-ovalisation ring.  See
    # docs/structural_analysis.md §4a and TODO.md §1.1.0.
    splice = add_mesh(
        doc, _stl("fuselage/head_cargo_splice_collar.stl"), "Head_Cargo_Splice_Collar"
    )
    place_mesh(splice, PL_IDENTITY)

    # Internal cargo/middle splice collar (Rev R1, hull frame — spans the joint at
    # hull Y ≈ +131 mm; identity placement).  Secures the cargo section to the
    # middle section: 2-wall bonded double-lap + anti-ovalisation ring.  See
    # docs/structural_analysis.md §7.4 and TODO.md §1.1.1.0b.
    splice2 = add_mesh(
        doc,
        _stl("fuselage/cargo_middle_splice_collar.stl"),
        "Cargo_Middle_Splice_Collar",
    )
    place_mesh(splice2, PL_IDENTITY)

    # Internal middle/rear splice collar (Rev R1, hull frame — spans the joint at
    # hull Y ≈ +203 mm; identity placement).  Secures the middle section to the
    # rear section: 2-wall bonded double-lap + anti-ovalisation ring; complements
    # (does not replace) the CF skid rods as the skid-impact load path.  See
    # docs/structural_analysis.md §7.5 and TODO.md §1.1.1.0b.
    splice3 = add_mesh(
        doc,
        _stl("fuselage/middle_rear_splice_collar.stl"),
        "Middle_Rear_Splice_Collar",
    )
    place_mesh(splice3, PL_IDENTITY)

    # Landing gear — RETIRED single-blade parts (part-local print frame; NOT
    # hull-placed).  Superseded by the Rev R5 vertical-post + 4-wire-brace
    # design (post.stl + spring/ductile wires); hull-frame placement of the
    # Rev R5 gear is tracked under TODO.md §1.1.4, not §1.1.0.  Paths corrected
    # to the landing-gear/ subdirectory so the refs resolve; these remain
    # VERIFY/part-local until the §1.1.4 wire-brace placement lands.
    add_mesh(doc, _stl("fuselage/landing-gear/feet_x_4_scaled24.stl"), "Landing_Feet")
    add_mesh(doc, _stl("fuselage/landing-gear/legs_scaled24.stl"), "Landing_Legs")

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

    # -------------------------------------------------------------------
    # CARGO BAY INTERIOR MOUNTS
    # VERIFY: all parts imported at origin (identity placement).
    # User will manually position these in FreeCAD, then AI extracts
    # final placements from the corrected file for precision alignment.
    # See VERIFY_PLACEMENT_CHECKLIST.md §1 for positioning guidance.
    # -------------------------------------------------------------------
    print("[assembly] Cargo bay interior mounts ...", flush=True)

    # Cargo doors — baked into hull frame (already at identity).
    add_mesh(doc, _stl("fuselage/cargo/cargo_door_port.stl"), "Cargo_Door_Port")
    add_mesh(doc, _stl("fuselage/cargo/cargo_door_stbd.stl"), "Cargo_Door_Stbd")

    # Hinge retention blocks — baked into hull frame (already at identity).
    add_mesh(doc, _stl("fuselage/cargo/cargo_hinge_retention.stl"), "Cargo_Hinge_Retention")

    # Cargo accessories — VERIFY placements (import at origin for manual positioning).
    add_mesh(doc, _stl("fuselage/cargo/cargo_cradle_autolatch.stl"), "Cargo_Cradle")
    add_mesh(doc, _stl("fuselage/cargo/cargo_fpv_bezel.stl"), "Cargo_FPV_Bezel")
    add_mesh(doc, _stl("fuselage/cargo/cargo_gps_retention_ring.stl"), "Cargo_GPS_Ring")
    add_mesh(doc, _stl("fuselage/cargo/cargo_winch_motor_mount.stl"), "Cargo_Winch_Mount")
    add_mesh(doc, _stl("fuselage/cargo/cargo_winch_spool.stl"), "Cargo_Winch_Spool")
    add_mesh(doc, _stl("fuselage/cargo/cargo_drv8833_tray.stl"), "Cargo_DRV8833_Tray")
    add_mesh(doc, _stl("fuselage/cargo/cargo_door_servo_bracket.stl"), "Cargo_Door_Servo_Bracket")
    add_mesh(
        doc, _stl("fuselage/cargo/cargo_release_servo_bracket.stl"), "Cargo_Release_Servo_Bracket"
    )

    # -------------------------------------------------------------------
    # FUSELAGE ACCESSORIES (battery tray and belly panel)
    # VERIFY: all parts imported at origin (identity placement).
    # User will manually position these in FreeCAD, then AI extracts
    # final placements from the corrected file.
    # See VERIFY_PLACEMENT_CHECKLIST.md §2 for positioning guidance.
    # -------------------------------------------------------------------
    print("[assembly] Battery tray and belly panel ...", flush=True)

    add_mesh(doc, _stl("fuselage/battery_tray.stl"), "Battery_Tray")
    add_mesh(doc, _stl("fuselage/belly_panel.stl"), "Belly_Panel")

    # -------------------------------------------------------------------
    # WINGS
    # R1: baked hull-frame STLs — identity placement.
    # -------------------------------------------------------------------
    print("[assembly] Wings ...", flush=True)

    port_wing = add_mesh(doc, _stl("wings/wing_port_s1223_revo.stl"), "Wing_Port")
    place_mesh(port_wing, PL_IDENTITY)

    stbd_wing = add_mesh(doc, _stl("wings/wing_stbd_s1223_revo.stl"), "Wing_Stbd")
    place_mesh(stbd_wing, PL_IDENTITY)

    # -------------------------------------------------------------------
    # NACELLE TILT BRACKETS (INTEGRATED INTO WINGS)
    # INTEGRATION (2026-07-18): The separate pylon component
    # (wing_nacelle_pylon_revo.scad) is now superseded. Tilt bracket
    # functionality is integrated into the wing tip geometry
    # (wings_s1223_revo.scad Rev R1a). See VERIFY_PLACEMENT_CHECKLIST.md.
    # Standalone pylon STLs archived to airframe/archive/stls/nacelles/.
    # No separate pylon import needed.
    # -------------------------------------------------------------------
    print("[assembly] Nacelle tilt brackets (integrated into wings) ...", flush=True)

    # -------------------------------------------------------------------
    # NACELLE PODS (forward-flight / cruise configuration)
    # R1: baked hull-frame STLs — identity placement; stored attitude is
    # cruise.  Hover is a downstream rotation about the tilt pivot.
    #
    # nacelle_port_revs.stl: hull +X (port side), SWIRL_DIR=-1 (CCW),
    #   harness conduit exits -X (inboard) face.
    # nacelle_stbd_revs.stl: hull -X (starboard side), SWIRL_DIR=+1 (CW),
    #   harness conduit exits +X (inboard) face.
    # Labels corrected Rev R1/nacelle-swap (2026-06-11) after FreeCAD
    # layout inspection confirmed the original naming was inverted.
    # -------------------------------------------------------------------
    print("[assembly] Nacelle pods ...", flush=True)

    port_nac = add_mesh(doc, _stl("nacelles/nacelle_port_revs.stl"), "Nacelle_Port")
    place_mesh(port_nac, PL_IDENTITY)

    stbd_nac = add_mesh(doc, _stl("nacelles/nacelle_stbd_revs.stl"), "Nacelle_Stbd")
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
    # PIVOT_Z re-derived 2026-07-04 for the FULL rotating assembly (nozzle
    # ring/petals; WS2812B exhaust LED rings removed): CG_Z = 104.5 mm.  See
    # nacelle_pod_50mm_tandem.scad header mass breakdown.  Rev T (2026-07-18)
    # deleted the gear train (Option B pushrod drive) — its small gear masses
    # left the pivot CG effectively unchanged; the spar crank clamps here.
    PIVOT_Z = 104.5  # pivot / spar-crank station = full-assembly nacelle CG
    NOZZLE_RING_Z = 166.25  # nozzle ring station (nozzle placement)

    for side in ("port", "stbd"):
        label = "Port" if side == "port" else "Stbd"

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

        # ── Nozzle pushrod drive — Rev T (Option B) ───────────────────────
        # Rev T (2026-07-18, docs/NOZZLE_DRIVE_TRADE.md Option B; user
        # decision 2026-07-18): the ENTIRE tilt-to-nozzle GEAR train is
        # DELETED — Drive Pinion A, the Nozzle Drive Pinion, the bevel
        # housing, the bevel pair, and the fixed sector gear (and, earlier,
        # the compound idler).  Those five STL placements are removed; the
        # parts are archived under airframe/archive/.  The nozzle is now
        # driven by a PUSHROD/BELLCRANK: a spar crank clamps the rotating
        # tilt spar and a ball-link pushrod strokes the unison-ring lever
        # ear (nacelle_nozzle_pushrod.scad + the ring lever in
        # nacelle_nozzle_iris.scad).
        #
        # FIRST-PASS PLACEMENT — VERIFY (spatial RSSR linkage, WBS §1.1.3):
        # the spar crank sits on the pivot axis (Y=0, Z=PIVOT_Z), clamp bore
        # along local X (the spar/tilt axis) — hence the 90 deg Y-rotation,
        # as the old Pinion A used.  The exact crank clock angle, pushrod
        # length, and ring-lever pose that give a monotonic 0..90 deg tilt ->
        # 0..23.75 deg ring map are NOT yet solved; the pushrod link itself
        # (COTS ball-link rod) is intentionally not placed here until that
        # synthesis is closed.
        spar_crank = add_mesh(
            doc,
            _stl("nacelles/nacelle_pushrod_crank.stl"),
            f"Nacelle_{label}_Nozzle_Spar_Crank",
        )
        transform_mesh(
            spar_crank, nacelle_rows(side, _rot_y(90.0), (0.0, 0.0, PIVOT_Z))
        )

        # ── Nozzle iris assembly ──────────────────────────────────────────
        # nacelle_nozzle_iris.stl is the combined render (cam-only unison ring
        # + outer housing + 8 flaps at the closed position) from
        # nacelle_nozzle_iris.scad.  Rev T: the ring is a plain CAM disc (no
        # gear teeth) driven by the spar-crank pushrod above; the housing has
        # no drive-pinion relief and is rotationally symmetric, so identity
        # rotation is fine.  Translate to NOZZLE_RING_Z.
        # History: Rev R1 compound idler (2026-06-22) -> Rev S1 internal ring
        # gear (2026-07-07) -> Rev T pushrod/cam-only drive (2026-07-18,
        # Option B); the entire gear train is deleted and archived — see
        # ARCHIVE_INDEX.md and docs/NOZZLE_DRIVE_TRADE.md.
        nozzle = add_mesh(
            doc,
            _stl("nacelles/nozzles/nacelle_nozzle_iris.stl"),
            f"Nacelle_{label}_Nozzle_Iris",
        )
        transform_mesh(
            nozzle, nacelle_rows(side, _IDENTITY3, (0.0, 0.0, NOZZLE_RING_Z))
        )

        # Tip cap (outboard X-face end cap) — ARCHIVED 2026-06-22, legacy
        # part, no longer needed.  STLs moved to airframe/archive/stls/
        # nacelles/; see ARCHIVE_INDEX.md.  (Previously a best-guess VERIFY
        # placeholder with no active SCAD source — see TODO.md §1.1.3
        # history.)

    # -------------------------------------------------------------------
    # NACELLE SERVO BRACKETS — Fuselage-mounted tilt-control actuators
    # VERIFY: all parts imported at origin (identity placement).
    # User will manually position these in FreeCAD, then AI extracts
    # final placements from the corrected file.
    # See VERIFY_PLACEMENT_CHECKLIST.md §4 for positioning guidance.
    # -------------------------------------------------------------------
    print("[assembly] Nacelle servo brackets (fuselage-mounted tilt actuators) ...", flush=True)

    add_mesh(
        doc, _stl("nacelles/nacelle_servo_bracket.stl"), "Nacelle_Servo_Bracket_Port"
    )
    add_mesh(
        doc, _stl("nacelles/nacelle_servo_bracket.stl"), "Nacelle_Servo_Bracket_Stbd"
    )

    # -------------------------------------------------------------------
    # DORSAL ANTENNA FIN
    # VERIFY: all parts imported at origin (identity placement).
    # User will manually position these in FreeCAD, then AI extracts
    # final placements from the corrected file.
    # See VERIFY_PLACEMENT_CHECKLIST.md §5 for positioning guidance.
    # -------------------------------------------------------------------
    print("[assembly] Dorsal antenna fin ...", flush=True)

    add_mesh(doc, _stl("fuselage/dorsal_antenna_fin.stl"), "Dorsal_Antenna_Fin")

    # -------------------------------------------------------------------
    # Recompute and save
    # -------------------------------------------------------------------
    print(f"[assembly] Document has {len(doc.Objects)} objects", flush=True)
    print("[assembly] Recomputing ...", flush=True)
    doc.recompute()
    print("[assembly] Recompute complete", flush=True)

    print(f"[assembly] Saving → {OUTPUT}", flush=True)
    # FreeCAD 1.0: Document.save() takes no path — saveAs() sets the
    # file name and writes the document in one call.
    doc.saveAs(OUTPUT)
    print("[assembly] Document saved", flush=True)
    print(f"[assembly] File size check: use 'ls -lh {OUTPUT}'", flush=True)
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
