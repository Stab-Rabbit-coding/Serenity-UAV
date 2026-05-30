#!/usr/bin/env python3
"""
generate_cargo_mounts.py
Generate STL files for all Serenity UAV cargo handling equipment mounts.

Components generated (all to thingverse-serenity/files-hollowed-18in/):
    cargo_winch_motor_mount.stl     -- N20 motor clamp bracket (CF-PETG, print 1)
    cargo_winch_spool.stl           -- Dyneema SK75 winding drum (PETG, print 1)
    cargo_door_servo_bracket.stl    -- SG90 bracket, clamshell door actuator (CF-PETG, print 1)
    cargo_release_servo_bracket.stl -- SG90 bracket, payload release (CF-PETG, print 1)
    cargo_drv8833_tray.stl          -- DRV8833 H-bridge PCB tray (PETG, print 1)
    cargo_cradle_autolatch.stl      -- Payload auto-latch retrieval cradle (PETG, print 1)
    cargo_gps_retention_ring.stl    -- GPS antenna retention ring (PETG, print 2)
    cargo_fpv_bezel.stl             -- FPV camera retention bezel (PETG, print 1)

Print specifications (CLAUDE.md fabrication standards):
    CF-PETG structural: 0.15 mm layer height, 4 perimeters, >= 40 % infill
    PETG non-structural: 0.15 mm layer height, 4 perimeters, 25 % infill

Design references:
    N20 300:1 gearmotor: body 10 mm OD x 24 mm OAL, 3 mm D-shaft, 4 mm shaft length
    SG90 servo: 22.8 x 12.2 x 23.0 mm body, 27.9 mm mount hole c/c, M2 mount holes
    DRV8833 carrier PCB: 26 x 23 mm nominal (generic breakout or SparkFun ROB-14450)
    Dyneema SK75 0.5 mm braid: OD 0.5 mm, min break load >= 100 N (Lankhorst Euronete)
    u-blox ANN-MB-00 GPS patch antenna: 35 mm OD circular (data sheet rev 1.0)
    Cargo shell GPS mount params (s_cargo_sect_shell24.scad):
        GPS_M2_BC_R = 22.0 mm, GPS_RECESS_D = 36.0 mm, GPS_M2_D = 2.4 mm
    Cargo shell FPV mount params (s_cargo_sect_shell24.scad):
        FPV_BEZ_W = 29.0 mm, FPV_APER_D = 16.0 mm, FPV_M2_S = 14.0 mm
    Ruthex RX-M3x5.7 heat-set insert: bore 4.0 mm, OD 5.7 mm (reference only)
    DIN 7991 M2 flathead countersink: 90 deg included angle, OD 4.5 mm at M2

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
Year:    2026

Run:
    python3 serenity/stl/generate_cargo_mounts.py
Verify Z-range and dimensions in console output before committing STLs.
"""

import math
import os
import sys

import numpy as np
import trimesh
import trimesh.transformations as tft

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
OUT_DIR = os.path.join(PROJECT_ROOT, "thingverse-serenity", "files-hollowed-18in")

# ---------------------------------------------------------------------------
# Transform helpers
# ---------------------------------------------------------------------------

def _T(dx=0.0, dy=0.0, dz=0.0):
    """4x4 translation matrix."""
    m = np.eye(4)
    m[0, 3] = dx
    m[1, 3] = dy
    m[2, 3] = dz
    return m


def _Rx(deg):
    """4x4 rotation about X axis."""
    return tft.rotation_matrix(math.radians(deg), [1, 0, 0])


def _Ry(deg):
    """4x4 rotation about Y axis."""
    return tft.rotation_matrix(math.radians(deg), [0, 1, 0])


def _Rz(deg):
    """4x4 rotation about Z axis."""
    return tft.rotation_matrix(math.radians(deg), [0, 0, 1])


def moved(mesh, *transforms):
    """Return a copy of mesh with each transform applied in sequence."""
    m = mesh.copy()
    for t in transforms:
        m.apply_transform(t)
    return m


# ---------------------------------------------------------------------------
# Geometry primitives (all centered at origin unless otherwise noted)
# ---------------------------------------------------------------------------

def box(lx, ly, lz):
    """Axis-aligned box, centered at origin."""
    return trimesh.creation.box([lx, ly, lz])


def cyl(r, h, sections=64):
    """Cylinder along Z, centered at origin (Z = -h/2 .. h/2)."""
    return trimesh.creation.cylinder(r, h, sections=sections)


def cyl_x(r, h, sections=64):
    """Cylinder along X axis, centered at origin (X = -h/2 .. h/2)."""
    return moved(cyl(r, h, sections), _Ry(90))


def cyl_y(r, h, sections=64):
    """Cylinder along Y axis, centered at origin (Y = -h/2 .. h/2)."""
    return moved(cyl(r, h, sections), _Rx(90))


def bsub(base, *cutters):
    """Boolean difference: base minus each cutter in sequence."""
    result = base
    for c in cutters:
        result = trimesh.boolean.difference([result, c], engine="manifold")
    return result


def bunion(*meshes):
    """Boolean union of all meshes."""
    if len(meshes) == 1:
        return meshes[0]
    result = meshes[0]
    for m in meshes[1:]:
        result = trimesh.boolean.union([result, m], engine="manifold")
    return result


def intersect(a, b):
    """Boolean intersection of two meshes."""
    return trimesh.boolean.intersection([a, b], engine="manifold")


# ---------------------------------------------------------------------------
# Output helper
# ---------------------------------------------------------------------------

def save(mesh, filename):
    """Export mesh to OUT_DIR and print verification data."""
    path = os.path.join(OUT_DIR, filename)
    mesh.export(path)
    b = mesh.bounds
    dims = b[1] - b[0]
    print(
        f"  {filename}: "
        f"{dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm  "
        f"Z = {b[0][2]:.2f} .. {b[1][2]:.2f}  "
        f"faces = {len(mesh.faces)}  "
        f"watertight = {mesh.is_watertight}"
    )


# ===========================================================================
# Part generators
# ===========================================================================

def make_motor_mount():
    """
    N20 winch motor mount bracket.

    U-channel bracket that holds the N20 gearmotor (10 mm OD x 24 mm OAL)
    horizontally against the gondola dorsal interior ceiling.  Motor axis
    runs parallel to gondola Z (lateral / port-stbd direction).  Spool on
    motor output shaft hangs into gondola interior below the bracket.

    Retention: four 3.5 mm dia zip-tie pass-through holes in the channel
    floor let two zip-ties loop around the motor body.  Four M2 self-tap
    pilot holes anchor the bracket to the gondola dorsal interior shell
    (2 mm PETG skin -- M2 x 6 mm pan-head self-tap).

    Print orientation: channel open face UP (away from build plate).
    Flip for installation: mounting face against gondola ceiling.

    External dims: 36 x 28 x 15 mm.
    Material: CF-PETG.  Print: 0.15 mm layers, 4 perimeters, 40 % infill.
    """
    BW = 36.0     # bracket width (X), perpendicular to motor axis
    BL = 28.0     # bracket length (Y), along motor axis; must exceed motor OAL 24 mm
    BASE_H = 3.0  # base plate thickness (Z = 0 .. BASE_H)
    CW = 16.0     # channel interior width (X): motor 10 mm + 3 mm clearance each side
    CH = 12.0     # channel wall height above base plate (Z = BASE_H .. BASE_H+CH)
    TH = BASE_H + CH  # total bracket height = 15 mm

    M2_R = 1.1    # M2 self-tap pilot hole radius (2.2 mm dia)
    CX = BW / 2 - 5.0   # M2 hole X offset from centre (5 mm from outer edge)
    CY = BL / 2 - 5.0   # M2 hole Y offset from centre (5 mm from end)

    ZT_R = 1.75   # zip-tie hole radius (3.5 mm dia; passes 2.5 mm zip-tie)
    ZT_X = 4.0    # zip-tie holes at +/-4 mm from channel centre (within 16 mm channel)
    ZT_Y = 7.0    # zip-tie holes at +/-7 mm along motor axis

    # Full solid block
    solid = moved(box(BW, BL, TH), _T(0, 0, TH / 2))

    # Channel cut from top (leaves BASE_H base plate, opens both Y ends)
    chan = moved(box(CW + 0.1, BL + 0.2, CH + 0.1), _T(0, 0, BASE_H + CH / 2 + 0.05))

    # Four M2 self-tap pilot holes (through full bracket height)
    m2s = [
        moved(cyl(M2_R, TH + 0.2), _T(sx * CX, sy * CY, TH / 2))
        for sx in (-1, 1)
        for sy in (-1, 1)
    ]

    # Four zip-tie pass-through holes in channel floor (base plate Z = 0 .. BASE_H)
    zts = [
        moved(cyl(ZT_R, BASE_H + 0.2), _T(sx * ZT_X, sy * ZT_Y, BASE_H / 2))
        for sx in (-1, 1)
        for sy in (-1, 1)
    ]

    return bsub(solid, chan, *m2s, *zts)


def make_winch_spool():
    """
    Dyneema SK75 winch spool, press-fit on N20 3 mm D-shaft.

    Core OD 20 mm, usable drum width 18 mm (between flanges), flanges OD 26 mm
    x 2 mm thick.  Single-layer capacity at core OD:
        circumference = pi x 20 = 62.8 mm; 1500 mm / 62.8 mm ~= 24 turns;
        24 turns x 0.55 mm pitch = 13.2 mm -- fits within 18 mm usable width.

    D-shaft bore: 3.15 mm dia (0.15 mm diametric clearance), flat at x = 1.0 mm
    from centre on +X face (N20 standard 0.5 mm flat depth from OD).
    M2 set-screw tap hole (1.7 mm dia, 6 mm deep) from -Y OD toward shaft.
    Dyneema anchor slot: 2 mm wide x 4 mm deep, tangential in -Z flange face.

    Spool axis = Z.  Total dims: 26 mm OD x 22 mm wide.
    Material: PETG.  Print: 0.15 mm layers, 4 perimeters, 25 % infill.
    Reference: Lankhorst Euronete Dyneema SK75 0.5 mm spec sheet.
    """
    CORE_R = 10.0    # spool core radius (OD 20 mm)
    CORE_W = 18.0    # usable drum width (between flanges)
    FL_R = 13.0      # flange radius (OD 26 mm)
    FL_T = 2.0       # flange thickness
    TOT_W = CORE_W + 2 * FL_T   # 22 mm total

    # N20 D-shaft bore parameters
    SHAFT_D = 3.0
    SHAFT_CL = 0.15   # diametric clearance (press-fit)
    SHAFT_R = SHAFT_D / 2 + SHAFT_CL / 2   # = 1.575 mm bore radius
    FLAT_DEPTH = 0.5  # shaft flat depth from OD
    FLAT_X = SHAFT_D / 2 - FLAT_DEPTH      # = 1.0 mm (flat face x from centre)

    SET_R = 1.7 / 2   # M2 tap drill radius (1.7 mm dia)
    SET_L = 6.0       # set-screw hole depth (from spool OD inward)

    ANCHOR_W = 2.0    # Dyneema anchor slot width (mm)
    ANCHOR_D = 4.0    # Dyneema anchor slot depth (mm, radially inward from flange OD)

    # --- Solid core and flanges ---
    core = cyl(CORE_R, CORE_W)
    fl_lo = moved(cyl(FL_R, FL_T), _T(0, 0, -(CORE_W / 2 + FL_T / 2)))
    fl_hi = moved(cyl(FL_R, FL_T), _T(0, 0, +(CORE_W / 2 + FL_T / 2)))
    solid = bunion(core, fl_lo, fl_hi)

    # --- D-shaft bore (D-shaped cross-section) ---
    # Bore cutter = intersection of full cylinder and half-space x <= FLAT_X
    bore_cyl = cyl(SHAFT_R, TOT_W + 0.2)
    # Half-space: box from x = -(SHAFT_R+eps) to x = FLAT_X+eps
    eps = 0.01
    hs_w = SHAFT_R + eps + FLAT_X + eps   # spans left edge to flat line
    hs_cx = (-SHAFT_R - eps + FLAT_X + eps) / 2
    half_space = moved(box(hs_w, (SHAFT_R + 0.1) * 2, TOT_W + 0.4), _T(hs_cx, 0, 0))
    d_bore = intersect(bore_cyl, half_space)

    # --- M2 set-screw tap hole from -Y OD toward shaft centre ---
    # Hole centre at y = -(CORE_R - SET_L/2), z = 0
    set_screw = moved(cyl_y(SET_R, SET_L + 0.1), _T(0, -(CORE_R - SET_L / 2), 0))

    # --- Dyneema anchor slot in low flange (-Z face), at -Y (nadir side) ---
    # Slot: 2 mm wide (X) x 4 mm deep (radial, into flange from OD) x FL_T thick (Z)
    # Slot centre: x=0, y=-(FL_R - ANCHOR_D/2), z=-(CORE_W/2 + FL_T/2)
    anchor = moved(
        box(ANCHOR_W + 0.1, ANCHOR_D + 0.1, FL_T + 0.1),
        _T(0, -(FL_R - ANCHOR_D / 2), -(CORE_W / 2 + FL_T / 2))
    )

    return bsub(solid, d_bore, set_screw, anchor)


def make_servo_bracket():
    """
    SG90 servo mounting bracket for cargo bay.  Print 2x:
      -- cargo_door_servo_bracket.stl  (clamshell door actuator)
      -- cargo_release_servo_bracket.stl (payload release / DRV8833 direction)
    Both brackets are geometrically identical; installation orientation differs.

    Flat CF-PETG plate with SG90 body pocket on front face.
    Four M2.5 self-tap pilot holes anchor bracket to gondola interior wall.
    Two M2 clearance holes at 27.9 mm span retain SG90 via its mounting tabs.

    SG90 fits flush in pocket (zero external protrusion from bracket face).
    Bell-crank / pushrod hardware attaches directly to SG90 output horn.

    Dims: 44 x 28 x 5 mm.
    Material: CF-PETG.  Print: 0.15 mm layers, 4 perimeters, 40 % infill.
    Reference: SG90 servo data sheet (Tower Pro or compatible).
    """
    PL = 44.0    # plate length (X)
    PW = 28.0    # plate width (Y)
    PT = 5.0     # plate thickness (Z)

    SK_L = 23.2  # SG90 body pocket length (X): 22.8 mm + 0.4 mm clearance
    SK_W = 12.6  # SG90 body pocket width (Y): 12.2 mm + 0.4 mm clearance
    SK_D = 4.0   # SG90 body pocket depth (Z): servo seated half-depth in plate

    M2_SPAN = 27.9   # SG90 mount hole centre-to-centre (X)
    M2_R = 2.2 / 2   # M2 clearance hole radius
    M25_R = 2.8 / 2  # M2.5 self-tap pilot hole radius
    M25_X = PL / 2 - 5.0   # 5 mm from plate edge
    M25_Y = PW / 2 - 5.0   # 5 mm from plate end

    # Main plate (base at Z=0)
    plate = moved(box(PL, PW, PT), _T(0, 0, PT / 2))

    # SG90 body pocket in top face (Z = PT - SK_D .. PT)
    pocket = moved(box(SK_L + 0.1, SK_W + 0.1, SK_D + 0.1), _T(0, 0, PT - SK_D / 2 + 0.05))

    # 2x M2 servo tab holes (through full plate Z)
    m2s = [moved(cyl(M2_R, PT + 0.2), _T(sx * M2_SPAN / 2, 0, PT / 2)) for sx in (-1, 1)]

    # 4x M2.5 self-tap pilot holes at corners (through full plate Z)
    m25s = [
        moved(cyl(M25_R, PT + 0.2), _T(sx * M25_X, sy * M25_Y, PT / 2))
        for sx in (-1, 1)
        for sy in (-1, 1)
    ]

    return bsub(plate, pocket, *m2s, *m25s)


def make_drv8833_tray():
    """
    PCB mounting tray for DRV8833 dual H-bridge motor driver breakout board.

    Base plate with four M2 standoff posts that mate with PCB corner holes.
    PCB (26 x 23 mm) sits on posts at 4 mm above tray base; solder joints
    and SMD components clear the tray floor.  Four M2.5 self-tap pilot holes
    at tray corners anchor tray to gondola interior wall.

    PCB corner holes assumed at 2.5 mm from each PCB edge:
        x = +/- (26/2 - 2.5) = +/- 10.5 mm
        y = +/- (23/2 - 2.5) = +/-  9.0 mm

    Dims: 36 x 33 x 6 mm (base 2 mm + posts 4 mm).
    Material: PETG.  Print: 0.15 mm layers, 4 perimeters, 25 % infill.
    Reference: SparkFun ROB-14450 DRV8833 carrier PCB mechanical drawing.
    """
    TRAY_L = 36.0    # tray length (X): PCB 26 mm + 5 mm margin each side
    TRAY_W = 33.0    # tray width  (Y): PCB 23 mm + 5 mm margin each side
    BASE_T = 2.0     # base plate thickness (Z = 0 .. 2)

    POST_OD = 4.0    # standoff post outer diameter
    POST_H = 4.0     # standoff post height (PCB stands 4 mm above tray base)
    POST_R = POST_OD / 2
    POST_BORE_R = 2.2 / 2   # M2 clearance bore in post top

    PCB_HX = 10.5    # PCB hole X offset from tray centre
    PCB_HY = 9.0     # PCB hole Y offset from tray centre

    M25_R = 2.8 / 2  # M2.5 self-tap pilot hole radius
    M25_X = TRAY_L / 2 - 4.0
    M25_Y = TRAY_W / 2 - 4.0

    # Base plate
    base = moved(box(TRAY_L, TRAY_W, BASE_T), _T(0, 0, BASE_T / 2))

    # Four standoff posts (union onto base)
    posts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            post_solid = moved(cyl(POST_R, POST_H), _T(sx * PCB_HX, sy * PCB_HY, BASE_T + POST_H / 2))
            post_bore = moved(cyl(POST_BORE_R, POST_H + 0.2), _T(sx * PCB_HX, sy * PCB_HY, BASE_T + POST_H / 2))
            posts.append(bsub(post_solid, post_bore))

    # Four M2.5 self-tap holes in base plate
    m25s = [
        moved(cyl(M25_R, BASE_T + 0.2), _T(sx * M25_X, sy * M25_Y, BASE_T / 2))
        for sx in (-1, 1)
        for sy in (-1, 1)
    ]

    result = bunion(base, *posts)
    return bsub(result, *m25s)


def make_autolatch_cradle():
    """
    Payload auto-latch retrieval cradle for Serenity UAV cargo delivery system.

    Hangs from Dyneema SK75 (0.5 mm) via tie-off boss at top centre.
    Rated: 250 g payload (2.45 N tension), safety factor ~2.5 in PETG.

    Auto-latch mechanism: four corner flex tabs (2 mm wall PETG, 10 mm tall)
    with 2 mm inward hooks that snap over matching 3 mm catch lips on the
    gondola clamshell door inner frame edge.  VERIFY catch lip geometry and
    add to s_cargo_sect_shell24.scad clamshell door frame before first flight.

    Dyneema tie-off boss (12 mm OD, 12 mm tall): 2 mm slot for line passage;
    5 mm central bore for double-bowline knot seating below boss.

    Outer dims: 110 x 80 x 80 mm (frame 60 mm + boss 12 mm + tabs 8 mm above top).
    Material: PETG.  Print: 0.15 mm layers, 4 perimeters, 25 % infill.
    Reference: Serenity UAV PHASED_BUILD_GUIDE.md Phase 6 cargo system.
    """
    OL = 110.0    # outer frame length (X)
    OW = 80.0     # outer frame width  (Y)
    OH = 60.0     # outer frame height (Z, floor to top rim)
    WT = 2.5      # wall and base thickness

    TAB_W = 5.0   # latch tab plan width (square, X and Y)
    TAB_T = 2.0   # latch tab wall thickness (flex element)
    TAB_H = 8.0   # latch tab height above frame top rim
    HOOK_D = 2.0  # hook notch depth (inward from tab outer face)
    HOOK_H = 3.0  # hook notch height (at tab tip)

    BOSS_R = 6.0    # Dyneema boss radius (OD 12 mm)
    BOSS_H = 12.0   # Dyneema boss height above frame top
    BOSS_SL = 2.0   # Dyneema line slot width
    BOSS_BR = 2.5   # central bore radius for knot seating (5 mm dia)

    # --- Hollow frame (solid outer - solid inner) ---
    outer = moved(box(OL, OW, OH), _T(0, 0, OH / 2))
    # Inner void: walls WT, open top, solid base WT thick
    inner = moved(
        box(OL - 2 * WT, OW - 2 * WT, OH - WT + 0.1),
        _T(0, 0, WT + (OH - WT) / 2 + 0.05)
    )
    frame = bsub(outer, inner)

    # --- Corner flex-latch tabs (at frame top rim corners) ---
    tabs = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            tcx = sx * (OL / 2 - TAB_W / 2)
            tcy = sy * (OW / 2 - TAB_W / 2)
            tab_solid = moved(box(TAB_W, TAB_W, TAB_H), _T(tcx, tcy, OH + TAB_H / 2))

            # Hook notch on outer X face of tab
            hx_cut = moved(
                box(HOOK_D + 0.1, TAB_W + 0.2, HOOK_H + 0.1),
                _T(tcx + sx * (TAB_W / 2 - HOOK_D / 2 + 0.05), tcy, OH + TAB_H - HOOK_H / 2 + 0.05)
            )
            # Hook notch on outer Y face of tab
            hy_cut = moved(
                box(TAB_W + 0.2, HOOK_D + 0.1, HOOK_H + 0.1),
                _T(tcx, tcy + sy * (TAB_W / 2 - HOOK_D / 2 + 0.05), OH + TAB_H - HOOK_H / 2 + 0.05)
            )
            tabs.append(bsub(tab_solid, hx_cut, hy_cut))

    # --- Dyneema tie-off boss at top centre ---
    boss_solid = moved(cyl(BOSS_R, BOSS_H), _T(0, 0, OH + BOSS_H / 2))
    # 2 mm line slot (X direction, full boss height) for Dyneema passage
    boss_slot = moved(box(BOSS_SL + 0.1, BOSS_R * 2 + 0.2, BOSS_H + 0.2), _T(0, 0, OH + BOSS_H / 2))
    # 5 mm central bore for double-bowline knot seating (lower half of boss)
    boss_bore = moved(cyl(BOSS_BR, BOSS_H / 2 + 0.1), _T(0, 0, OH + BOSS_H / 4 - 0.05))
    boss = bsub(boss_solid, boss_slot, boss_bore)

    return bunion(frame, *tabs, boss)


def make_gps_retention_ring():
    """
    GPS antenna retention ring for cargo gondola dorsal mounts.  Print 2x:
      -- one for GPS-PORT mount (Z = CZ + 30 mm, FC/Sensor Cape 1 / primary GPS)
      -- one for GPS-STBD mount (Z = CZ - 30 mm, FC/Sensor Cape 2 / redundant GPS)

    Clamps u-blox ANN-MB-00 35 mm circular patch GPS antenna into the flush
    receptacle cut by gps_mount_cut() in s_cargo_sect_shell24.scad.
    Four M2 DIN 7991 flathead screws at 44 mm bolt circle (22 mm radius) pull
    the ring down onto the antenna body, seating it in the 36 mm x 6 mm recess.

    Parameters match cargo shell SCAD exactly:
        GPS_RECESS_D = 36 mm (shell recess diameter)
        GPS_M2_BC_R  = 22 mm (bolt circle radius)
        GPS_M2_D     = 2.4 mm (clearance hole dia in shell)
    Ring clearance holes are 2.4 mm to align with shell holes.

    Dims: 50 mm OD x 35 mm ID x 2.5 mm thick.
    Material: PETG.  Print: 0.15 mm layers, 4 perimeters, 25 % infill.
    Reference: u-blox ANN-MB-00 data sheet rev 1.0; s_cargo_sect_shell24.scad.
    """
    RING_OD = 50.0    # outer diameter: bolt circle 44 mm + 3 mm margin each side
    RING_ID = 35.0    # inner diameter: matches 35 mm GPS antenna OD exactly
    RING_T = 2.5      # ring thickness

    BC_R = 22.0       # bolt circle radius (GPS_M2_BC_R from shell SCAD)
    M2_R = 2.4 / 2    # M2 clearance hole radius (GPS_M2_D from shell SCAD)
    CSK_R = 4.5 / 2   # DIN 7991 M2 flathead countersink radius (90 deg)
    CSK_D = 1.2       # countersink depth

    # Annular ring body
    outer_disk = cyl(RING_OD / 2, RING_T)
    inner_bore = cyl(RING_ID / 2, RING_T + 0.2)
    ring = bsub(outer_disk, inner_bore)

    # 4x M2 countersunk holes at 45 / 135 / 225 / 315 deg on bolt circle
    # Matches gps_mount_cut() 45-deg hole pattern in s_cargo_sect_shell24.scad
    cutters = []
    for angle_deg in (45, 135, 225, 315):
        ang = math.radians(angle_deg)
        cx = BC_R * math.cos(ang)
        cy = BC_R * math.sin(ang)
        # Through bore
        cutters.append(moved(cyl(M2_R, RING_T + 0.2), _T(cx, cy, 0)))
        # Flat-bottomed countersink pocket on top face (screw head seats here)
        cutters.append(moved(cyl(CSK_R, CSK_D + 0.1), _T(cx, cy, RING_T / 2 - CSK_D / 2 + 0.05)))

    return bsub(ring, *cutters)


def make_fpv_bezel():
    """
    FPV camera retention bezel for cargo gondola nadir (belly) mount.

    Clamps 28 mm standard FPV camera body in the flush aperture cut by
    fpv_cut() in s_cargo_sect_shell24.scad.  Camera face sits flush with
    gondola belly skin; bezel presses camera body from below.
    Four M2 DIN 7991 flathead screws at 14 x 14 mm grid retain bezel.

    Parameters match cargo shell SCAD exactly:
        FPV_BEZ_W = 29 mm  (shell SCAD -- outer square recess size)
        FPV_APER_D = 16 mm (shell SCAD -- lens aperture bore dia)
        FPV_M2_S   = 14 mm (shell SCAD -- M2 hole grid spacing)
        FPV_M2_D   = 2.2 mm (shell SCAD -- M2 clearance dia)

    Dims: 29 x 29 x 2.5 mm.
    Material: PETG.  Print: 0.15 mm layers, 4 perimeters, 25 % infill.
    Reference: s_cargo_sect_shell24.scad fpv_cut() module.
    """
    BEZ_W = 29.0    # outer square side (FPV_BEZ_W from shell SCAD)
    APER_R = 8.0    # lens aperture radius (FPV_APER_D / 2 = 8 mm)
    BEZ_T = 2.5     # bezel thickness
    GRID = 14.0     # M2 hole grid spacing (FPV_M2_S from shell SCAD)
    M2_R = 2.2 / 2  # M2 clearance radius (FPV_M2_D from shell SCAD)
    CSK_R = 4.5 / 2 # DIN 7991 M2 flathead CSK radius (90 deg)
    CSK_D = 1.2     # countersink depth

    # Square bezel body
    bezel = moved(box(BEZ_W, BEZ_W, BEZ_T), _T(0, 0, BEZ_T / 2))

    # Lens aperture bore (centred)
    aperture = cyl(APER_R, BEZ_T + 0.2)

    # 4x M2 countersunk holes at +/-(GRID/2) in both X and Y
    cutters = [aperture]
    for dx in (-GRID / 2, GRID / 2):
        for dy in (-GRID / 2, GRID / 2):
            cutters.append(moved(cyl(M2_R, BEZ_T + 0.2), _T(dx, dy, BEZ_T / 2)))
            cutters.append(moved(cyl(CSK_R, CSK_D + 0.1), _T(dx, dy, BEZ_T - CSK_D / 2 + 0.05)))

    return bsub(bezel, *cutters)


# ===========================================================================
# Main
# ===========================================================================

def main():
    print("=" * 60)
    print("Serenity UAV -- Cargo Equipment Mount STL Generator")
    print(f"Output directory: {OUT_DIR}")
    print("=" * 60)

    parts = [
        ("cargo_winch_motor_mount.stl",     make_motor_mount),
        ("cargo_winch_spool.stl",           make_winch_spool),
        ("cargo_door_servo_bracket.stl",    make_servo_bracket),
        ("cargo_release_servo_bracket.stl", make_servo_bracket),
        ("cargo_drv8833_tray.stl",          make_drv8833_tray),
        ("cargo_cradle_autolatch.stl",      make_autolatch_cradle),
        ("cargo_gps_retention_ring.stl",    make_gps_retention_ring),
        ("cargo_fpv_bezel.stl",             make_fpv_bezel),
    ]

    errors = []
    for filename, fn in parts:
        print(f"\nGenerating {filename} ...")
        try:
            mesh = fn()
            save(mesh, filename)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR: {exc}")
            errors.append((filename, exc))

    print()
    if errors:
        print(f"FAILED ({len(errors)} errors):")
        for name, exc in errors:
            print(f"  {name}: {exc}")
        sys.exit(1)
    else:
        print("All cargo mount STLs generated successfully.")
        print("Verify Z-range and dimensions above before committing.")


if __name__ == "__main__":
    main()
