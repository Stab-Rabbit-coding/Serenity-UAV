"""
serenity_assembly.py — Serenity UAV full-airframe FreeCAD assembly.
Revision: Q (2026-06-08)

Imports all printed airframe STL components, applies coordinate transforms,
and saves a single Serenity-Assembled.FCStd for review in FreeCAD with
Assembly4 installed.

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
    Station mapping: X_stl = 284 - station_mm

All fuselage section STLs (head, middle, cargo, rear) share this world
space and are placed at the identity transform — they tile naturally.

Wings, nacelles, and pylons are rotated from their local SCAD output axes
into the hull frame via 4×4 matrices.  Matrices with det = -1 (improper
rotations) are applied via Mesh.transform(); det = +1 matrices use the same
path for consistency.  See per-component comments for derivations.

VERIFY markers: position values that require confirmation by rendering the
relevant SCAD file and measuring cross-sections in a slicer.

References:
    [1] airframe/openscad/fuselage/s_head_shell24.scad — hull coordinate def.
    [2] airframe/openscad/wings/s_wings_s1223_revo.scad — wing axis def.
    [3] airframe/openscad/nacelles/nacelle_pod_50mm_tandem_simple.scad
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
ARCHIVE_DIR = os.path.join(AIRFRAME, "archive", "stls")
OUTPUT      = os.path.join(AIRFRAME, "Serenity-Assembled.FCStd")


# ---------------------------------------------------------------------------
# Assembly placement constants — hull-frame coordinates (mm).
# All values are in 24"-scaled STL world space.
#
# Fuselage section measured bounds (from STL centroid scan):
#   Head  : X= 99..228,  Y=-288..-53,  Z=  0..141  CX=161.33 CY=-148.57 CZ= 69.08
#   Cargo : X=-202..-7,  Y=-415..-211, Z=  0..163  CX=-102.19 CY=-328.63 CZ= 74.70
#   Rear  : X=-246..-106,Y=-193..-35,  Z=  0..181  CX=-175.80 CY=-114.12 CZ= 90.36
#
# Joint-face positions derived from head-shell bounds:
#   Cargo port outer edge   Z ≈  163 mm
#   Cargo stbd outer edge   Z ≈    0 mm
#   Cargo top face          Y ≈ -211 mm
#   Cargo fore face         X ≈   -7 mm  (leading-edge reference for wings)
# ---------------------------------------------------------------------------

# ---- Wing attachment (cargo section outer edge, upper surface) -------------
# tx: wing leading-edge aligned with cargo fore face.
# ty: wing root at cargo section top (Z_top = -211 mm).
# tz_port / tz_stbd: wing root at cargo port/stbd outer edge.
TX_WING      = -7.0     # mm  VERIFY: cargo fore face X
TY_WING      = -211.0   # mm  VERIFY: cargo top face Y
TZ_PORT_WING =  163.0   # mm  VERIFY: cargo port outer edge Z
TZ_STBD_WING =    0.0   # mm  VERIFY: cargo stbd outer edge Z

# Wing chord WING_CHORD_ROOT = 161 mm → TE at X = TX_WING - 161 ≈ -168 mm.
# Wing semi-span WING_SEMI_SPAN = 85.7 mm.

# ---- Nacelle pivot hub in hull frame (hover config) -----------------------
# Nacelle PIVOT_Z = 103.75 mm in nacelle-local Z.
# In hover, nacelle.Z → hull.-Y, so pivot maps to hull.Y = TY_NAC - 103.75.
# Pylon mid-span adds ~74 mm spanwise from wing root:
#   NACELLE_OD_X/2 + PYLON_SPAN/2 = 30.25 + 44 = 74.25 mm
PIVOT_Z_NACELLE = 103.75   # mm  from nacelle_pod_50mm_tandem_simple.scad
PYLON_HUB_Z     =  74.25   # mm  spanwise offset from wing root to nacelle hub

TY_NAC       = TY_WING - PIVOT_Z_NACELLE   # ≈ -315 mm  VERIFY
TZ_PORT_NAC  = TZ_PORT_WING + PYLON_HUB_Z  # ≈  237 mm  VERIFY
TZ_STBD_NAC  = TZ_STBD_WING - PYLON_HUB_Z  # ≈  -74 mm  VERIFY
TX_NAC       = TX_WING                      # ≈   -7 mm  VERIFY


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stl(rel_path):
    """Return absolute path under STL_DIR."""
    return os.path.join(STL_DIR, rel_path)


def _archive(rel_path):
    """Return absolute path under ARCHIVE_DIR."""
    return os.path.join(ARCHIVE_DIR, rel_path)


def add_mesh(doc, stl_path, label):
    """
    Import an STL as a Mesh::Feature in doc.

    Returns the new document object, or None if the file is missing.
    The mesh is imported at the origin with identity orientation; call
    place_mesh() or transform_mesh() afterward to position it.
    """
    if not os.path.exists(stl_path):
        print(f"[WARN] STL missing, skipping: {stl_path}", flush=True)
        return None
    mesh_data = Mesh.Mesh(stl_path)
    obj = doc.addObject("Mesh::Feature", label)
    obj.Mesh = mesh_data
    obj.Label = label
    return obj


def transform_mesh(obj, rows):
    """
    Apply a 4×4 transform matrix to the mesh of obj.

    rows: 3-tuple or 4-tuple of 4-element rows:
        ( [r0c0, r0c1, r0c2, r0c3],
          [r1c0, r1c1, r1c2, r1c3],
          [r2c0, r2c1, r2c2, r2c3] )
    The fourth row [0,0,0,1] is appended automatically.

    Uses Mesh.Mesh.transform() which supports det = ±1 matrices
    (i.e., proper and improper rotations / reflections).  This is
    necessary because the port wing and stbd nacelle mappings into
    hull space have det = -1.
    """
    r = [list(row) for row in rows]
    if len(r) == 3:
        r.append([0.0, 0.0, 0.0, 1.0])
    flat = [v for row in r for v in row]
    m = App.Matrix(*flat)
    obj.Mesh.transform(m)


def compose_transform(parent_rows, child_z_offset):
    """
    Compose a nacelle-space Z offset with a parent 3×4 rotation+translation.

    For a component centred on the nacelle axis at nacelle.Z = z0, this
    returns new 3×4 rows with the translation adjusted so the component
    ends up at the correct hull position.

    parent_rows: 3 rows of 4 values (rotation | translation).
    child_z_offset: float, nacelle.Z of the component centre.

    Works because the nacelle components are coaxial (nacelle.X=Y=0 at
    their centres), so only the Z term contributes to the translation.
    """
    # Under the parent transform, point (0, 0, z0) in nacelle space maps to:
    # hull_vec = R * [0, 0, z0]^T + t
    # = col2 of R * z0 + t
    result = []
    for i, row in enumerate(parent_rows):
        r0, r1, r2, t = row
        new_t = r2 * child_z_offset + t
        result.append([r0, r1, r2, new_t])
    return result


# ---------------------------------------------------------------------------
# Component placement definitions
# ---------------------------------------------------------------------------

def _rows_port_wing(tx, ty, tz):
    """
    Port wing → hull rotation (det = -1; improper rotation).

    Wing output axes: X=spanwise(port), Y=chordwise(LE→TE), Z=thickness(up).
    Hull mapping:
        hull.X = -wing.Y + tx   (LE at Y=0 faces nose = hull.+X)
        hull.Y = +wing.Z + ty   (thickness up = hull up)
        hull.Z = +wing.X + tz   (span toward port = hull.+Z)
    """
    return [
        [ 0, -1,  0, tx],
        [ 0,  0,  1, ty],
        [ 1,  0,  0, tz],
    ]


def _rows_stbd_wing(tx, ty, tz):
    """
    Stbd wing → hull rotation (det = +1).

    Hull mapping:
        hull.X = -wing.Y + tx   (LE faces nose)
        hull.Y = +wing.Z + ty   (thickness up)
        hull.Z = -wing.X + tz   (span toward stbd = hull.-Z)
    """
    return [
        [ 0, -1,  0, tx],
        [ 0,  0,  1, ty],
        [-1,  0,  0, tz],
    ]


def _rows_port_nacelle_hover(tx, ty, tz):
    """
    Port nacelle → hull, hover config (EDFs fire downward; det = +1).

    Nacelle axes: Z=axial(intake→exhaust), X/Y=radial.
    Hull mapping (hover: exhaust points down, intake aft):
        hull.X = -nacelle.Y + tx   (aft orientation)
        hull.Y = -nacelle.Z + ty   (exhaust down: Z↑ → Y↓)
        hull.Z = +nacelle.X + tz   (radial toward port)

    Derivation: R_hover = R_tilt(+90° about hull.Z) × R_cruise_port.
    R_cruise_port = [[0,0,-1],[0,1,0],[1,0,0]] (det=+1).
    R_tilt_z_+90  = [[0,-1,0],[1,0,0],[0,0,1]].
    Product        = [[0,-1,0],[0,0,-1],[1,0,0]] (det=+1). ✓
    """
    return [
        [ 0, -1,  0, tx],
        [ 0,  0, -1, ty],
        [ 1,  0,  0, tz],
    ]


def _rows_stbd_nacelle_hover(tx, ty, tz):
    """
    Stbd nacelle → hull, hover config (det = -1; improper rotation).

    Hull mapping (stbd mirror of port hover):
        hull.X = -nacelle.Y + tx
        hull.Y = -nacelle.Z + ty
        hull.Z = -nacelle.X + tz   (radial toward stbd = -hull.Z)

    det = -1: the stbd nacelle is a mirror image of the port nacelle.
    For a cylindrical (symmetric) nacelle pod, the reflection is visually
    equivalent to the proper stbd placement.
    VERIFY: if pylon face appears on wrong side, negate the tz row sign.
    """
    return [
        [ 0, -1,  0, tx],
        [ 0,  0, -1, ty],
        [-1,  0,  0, tz],
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
    # All sections share the 24"-scaled STL world coordinate space.
    # Placed at identity (no transform needed) — they tile naturally.
    # -------------------------------------------------------------------
    print("[assembly] Fuselage sections ...", flush=True)

    add_mesh(doc, _stl("fuselage/s_head_shell24_2mm_repaired.stl"), "Head_Shell")
    add_mesh(doc, _stl("fuselage/cargo/s_cargo_sect_shell24_2mm_repaired.stl"), "Cargo_Shell")
    add_mesh(doc, _stl("fuselage/s_middle_shell24_2mm_repaired.stl"), "Middle_Shell")
    add_mesh(doc, _stl("fuselage/cargo/s_cargo_sect_shell24.stl"), "Cargo_Shell")

    # Rear shell: use compiled version if available, fall back to repaired 2mm.
    rear_stl = _stl("fuselage/s_rear_shell24.stl")
    if not os.path.exists(rear_stl):
        rear_stl = _stl("fuselage/s_rear_shell24_2mm_repaired.stl")
    add_mesh(doc, rear_stl, "Rear_Shell")

    # Landing gear (scaled Thingiverse parts, identity placement)
    add_mesh(doc, _stl("fuselage/s_feet_x_4_scaled24.stl"), "Landing_Feet")
    add_mesh(doc, _stl("fuselage/s_legs_scaled24.stl"),      "Landing_Legs")

    # -------------------------------------------------------------------
    # CARGO BAY SUB-ASSEMBLY (cargo section, identity placement)
    # All cargo STLs share the hull world coordinate space via the cargo
    # section — they are already positioned correctly at import.
    # -------------------------------------------------------------------
    print("[assembly] Cargo bay ...", flush=True)

    cargo_stls = [
        ("fuselage/cargo/cargo_door_port.stl",         "Cargo_Door_Port"),
        ("fuselage/cargo/cargo_door_stbd.stl",         "Cargo_Door_Stbd"),
        ("fuselage/cargo/cargo_cradle_autolatch.stl",  "Cargo_Cradle"),
        ("fuselage/cargo/cargo_fpv_bezel.stl",         "Cargo_FPV_Bezel"),
        ("fuselage/cargo/cargo_gps_retention_ring.stl","Cargo_GPS_Ring"),
        ("fuselage/cargo/cargo_winch_motor_mount.stl", "Cargo_Winch_Mount"),
        ("fuselage/cargo/cargo_winch_spool.stl",       "Cargo_Winch_Spool"),
        ("fuselage/cargo/cargo_drv8833_tray.stl",      "Cargo_DRV8833_Tray"),
        ("fuselage/cargo/cargo_door_servo_bracket.stl","Cargo_Door_Servo_Bracket"),
        ("fuselage/cargo/cargo_release_servo_bracket.stl", "Cargo_Release_Servo_Bracket"),
    ]
    for rel, label in cargo_stls:
        add_mesh(doc, _stl(rel), label)

    # -------------------------------------------------------------------
    # FUSELAGE ACCESSORIES (battery tray and belly panel)
    # Tray local axes: X=forward, Y=up, Z=port — same as hull frame.
    # Tray origin (front-interior corner) placed at estimated keel position.
    # Battery centroid target: hull station ≈ 84 mm from nose
    #   → X_stl = 284 - 84 = 200 mm; Y at keel (≈ hull.Y = -240 mm).
    # VERIFY: slide tray along keel until battery CG aligns with FCOG.
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
    # Wing SCAD output axes: X=spanwise(root→tip), Y=chordwise(LE→TE),
    #                         Z=thickness(up).
    # Hull attachment: wing root at cargo outer edge, top face.
    #   TX_WING = -7  mm  VERIFY (LE at cargo fore face)
    #   TY_WING = -211 mm  VERIFY (cargo top face Y)
    #   TZ_PORT_WING = +163 mm  VERIFY (cargo port edge Z)
    #   TZ_STBD_WING =   0  mm  VERIFY (cargo stbd edge Z)
    # -------------------------------------------------------------------
    print("[assembly] Wings ...", flush=True)

    port_wing = add_mesh(doc, _stl("wings/s_wing_port_s1223_revo.stl"), "Wing_Port")
    if port_wing:
        transform_mesh(port_wing,
                       _rows_port_wing(TX_WING, TY_WING, TZ_PORT_WING))

    stbd_wing = add_mesh(doc, _stl("wings/s_wing_stbd_s1223_revo.stl"), "Wing_Stbd")
    if stbd_wing:
        transform_mesh(stbd_wing,
                       _rows_stbd_wing(TX_WING, TY_WING, TZ_STBD_WING))

    # -------------------------------------------------------------------
    # NACELLE TILT PYLONS
    # Pylon mounts at wing root (same TX/TY/TZ as wings).
    # Pylon spans PYLON_SPAN = 88 mm in pylon X = wing spanwise direction.
    # Port: same det=-1 matrix as port wing.
    # Stbd: same det=+1 matrix as stbd wing.
    # -------------------------------------------------------------------
    print("[assembly] Nacelle tilt pylons ...", flush=True)

    port_pylon = add_mesh(doc, _stl("wings/s_wing_nacelle_pylon_revo.stl"),
                          "Pylon_Port")
    if port_pylon:
        transform_mesh(port_pylon,
                       _rows_port_wing(TX_WING, TY_WING, TZ_PORT_WING))

    stbd_pylon = add_mesh(doc, _stl("wings/s_wing_nacelle_pylon_revo.stl"),
                          "Pylon_Stbd")
    if stbd_pylon:
        transform_mesh(stbd_pylon,
                       _rows_stbd_wing(TX_WING, TY_WING, TZ_STBD_WING))

    # -------------------------------------------------------------------
    # NACELLE PODS (hover configuration)
    # Config: EDFs fire downward (hover).  Both nacelles shown in hover.
    # For cruise config, replace _rows_*_nacelle_hover() with cruise rows.
    #
    # Nacelle pod local axes (nacelle_pod_50mm_tandem_simple.scad):
    #   Z = axial (intake at Z=0, nozzle-end at Z=185.2 mm)
    #   X = radial (toward pylon face / fuselage side)
    #   Y = radial (tangential)
    #   NACELLE_L  = 185.2 mm
    #   PIVOT_Z    = 103.75 mm (tilt pivot on pylon)
    #
    # Hull-frame translation anchor = nacelle pivot hub:
    #   TY_NAC      = TY_WING - PIVOT_Z_NACELLE ≈ -315 mm  VERIFY
    #   TZ_PORT_NAC = TZ_PORT_WING + 74.25      ≈  237 mm  VERIFY
    #   TZ_STBD_NAC = TZ_STBD_WING - 74.25      ≈  -74 mm  VERIFY
    #   TX_NAC      = TX_WING                   ≈   -7 mm  VERIFY
    #
    # Primary STL: nacelles/nacelle_pod_50mm_tandem_simple.stl (Makefile).
    # Fall back to archive rev-T nacelle shells if not compiled yet.
    # -------------------------------------------------------------------
    print("[assembly] Nacelle pods ...", flush=True)

    pod_stl = _stl("nacelles/nacelle_pod_50mm_tandem_simple.stl")
    port_nac_stl = pod_stl if os.path.exists(pod_stl) else \
        _archive("nacelles/s_nacelle_port_revt.stl")
    stbd_nac_stl = pod_stl if os.path.exists(pod_stl) else \
        _archive("nacelles/s_nacelle_stbd_revt.stl")

    port_nac = add_mesh(doc, port_nac_stl, "Nacelle_Pod_Port")
    if port_nac:
        transform_mesh(port_nac,
                       _rows_port_nacelle_hover(TX_NAC, TY_NAC, TZ_PORT_NAC))

    stbd_nac = add_mesh(doc, stbd_nac_stl, "Nacelle_Pod_Stbd")
    if stbd_nac:
        # det = -1; stbd is mirror image — see _rows_stbd_nacelle_hover docstring.
        transform_mesh(stbd_nac,
                       _rows_stbd_nacelle_hover(TX_NAC, TY_NAC, TZ_STBD_NAC))

    # -------------------------------------------------------------------
    # NACELLE INTERNAL COMPONENTS (EDF sleeves + nozzles)
    # Components are coaxial with the nacelle Z axis.
    # compose_transform() adjusts the parent hover matrix for the local
    # nacelle-Z position of each component's centre.
    #
    # EDF sleeve Z positions (from edf_stator_sleeve.scad,
    #                          edf_aft_spider_sleeve.scad):
    #   Stator sleeve  : Z = 90.0 .. 122.5 mm  → centre Z = 106.25 mm
    #   Aft spider slv : Z = 122.5 .. 166.25 mm → centre Z = 144.375 mm
    #   Straight nozzle: boss at nacelle Z = 166.25 mm
    # -------------------------------------------------------------------
    print("[assembly] Nacelle sleeves and nozzles ...", flush=True)

    Z_STATOR   = 106.25    # mm  centre of stator sleeve in nacelle Z
    Z_SPIDER   = 144.375   # mm  centre of aft spider sleeve in nacelle Z
    Z_NOZZLE   = 166.25    # mm  nozzle boss start in nacelle Z

    stator_stl = _stl("nacelles/edf_stator_sleeve.stl")
    spider_stl = _stl("nacelles/edf_aft_spider_sleeve.stl")
    nozzle_stl = _stl("nacelles/nacelle_nozzle_straight.stl")

    # Port nacelle sleeves
    port_stator = add_mesh(doc, stator_stl, "Stator_Sleeve_Port")
    if port_stator:
        rows = compose_transform(
            _rows_port_nacelle_hover(TX_NAC, TY_NAC, TZ_PORT_NAC), Z_STATOR)
        transform_mesh(port_stator, rows)

    port_spider = add_mesh(doc, spider_stl, "Aft_Spider_Port")
    if port_spider:
        rows = compose_transform(
            _rows_port_nacelle_hover(TX_NAC, TY_NAC, TZ_PORT_NAC), Z_SPIDER)
        transform_mesh(port_spider, rows)

    port_nozzle = add_mesh(doc, nozzle_stl, "Nozzle_Port")
    if port_nozzle:
        rows = compose_transform(
            _rows_port_nacelle_hover(TX_NAC, TY_NAC, TZ_PORT_NAC), Z_NOZZLE)
        transform_mesh(port_nozzle, rows)

    # Stbd nacelle sleeves (same Z offsets, stbd hover parent transform)
    stbd_stator = add_mesh(doc, stator_stl, "Stator_Sleeve_Stbd")
    if stbd_stator:
        rows = compose_transform(
            _rows_stbd_nacelle_hover(TX_NAC, TY_NAC, TZ_STBD_NAC), Z_STATOR)
        transform_mesh(stbd_stator, rows)

    stbd_spider = add_mesh(doc, spider_stl, "Aft_Spider_Stbd")
    if stbd_spider:
        rows = compose_transform(
            _rows_stbd_nacelle_hover(TX_NAC, TY_NAC, TZ_STBD_NAC), Z_SPIDER)
        transform_mesh(stbd_spider, rows)

    stbd_nozzle = add_mesh(doc, nozzle_stl, "Nozzle_Stbd")
    if stbd_nozzle:
        rows = compose_transform(
            _rows_stbd_nacelle_hover(TX_NAC, TY_NAC, TZ_STBD_NAC), Z_NOZZLE)
        transform_mesh(stbd_nozzle, rows)

    # -------------------------------------------------------------------
    # NACELLE NOZZLE DRIVE COMPONENTS (gear train — Rev T full nacelle)
    # These are only present in nacelle_pod_50mm_tandem.scad (iris version).
    # Pinion and sector gear are at the nacelle nozzle end.
    # Placed at the nozzle Z position of each nacelle.
    # -------------------------------------------------------------------
    print("[assembly] Nozzle drive gears ...", flush=True)

    pinion_stl  = _stl("nacelles/nacelle_pinion.stl")
    sector_stl  = _stl("nacelles/nacelle_sector_gear.stl")
    bevel_h_stl = _stl("nacelles/nozzles/nacelle_bevel_housing.stl")
    bevel_p_stl = _stl("nacelles/nozzles/nacelle_bevel_pair.stl")
    iris_stl    = _stl("nacelles/nozzles/nacelle_nozzle_iris.stl")

    for side, hover_fn, tz_nac in (
            ("Port", _rows_port_nacelle_hover, TZ_PORT_NAC),
            ("Stbd", _rows_stbd_nacelle_hover, TZ_STBD_NAC),
    ):
        parent_rows = hover_fn(TX_NAC, TY_NAC, tz_nac)
        nozzle_rows = compose_transform(parent_rows, Z_NOZZLE)

        p = add_mesh(doc, pinion_stl,  f"Pinion_{side}")
        if p:
            transform_mesh(p, nozzle_rows)

        s = add_mesh(doc, sector_stl, f"SectorGear_{side}")
        if s:
            transform_mesh(s, nozzle_rows)

        bh = add_mesh(doc, bevel_h_stl, f"BevelHousing_{side}")
        if bh:
            transform_mesh(bh, nozzle_rows)

        bp = add_mesh(doc, bevel_p_stl, f"BevelPair_{side}")
        if bp:
            transform_mesh(bp, nozzle_rows)

        ir = add_mesh(doc, iris_stl, f"IrisNozzle_{side}")
        if ir:
            transform_mesh(ir, nozzle_rows)

    # -------------------------------------------------------------------
    # NACELLE TIP CAPS
    # Tip caps fit over the nacelle intake (Z=0 end) of each nacelle pod.
    # In hover, nacelle.Z=0 maps to hull.Y = TY_NAC (intake at pivot height).
    # -------------------------------------------------------------------
    print("[assembly] Nacelle tip caps ...", flush=True)

    port_cap = add_mesh(doc, _stl("nacelles/nacelle_tip_cap_port.stl"),
                        "TipCap_Port")
    if port_cap:
        # Z_intake = 0 → hull.Y offset = 0 from TY_NAC (pivot height)
        transform_mesh(port_cap,
                       _rows_port_nacelle_hover(TX_NAC, TY_NAC, TZ_PORT_NAC))

    stbd_cap = add_mesh(doc, _stl("nacelles/nacelle_tip_cap_stbd.stl"),
                        "TipCap_Stbd")
    if stbd_cap:
        transform_mesh(stbd_cap,
                       _rows_stbd_nacelle_hover(TX_NAC, TY_NAC, TZ_STBD_NAC))

    # -------------------------------------------------------------------
    # DORSAL ANTENNA FIN (fuselage dorsal, identity placement)
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
