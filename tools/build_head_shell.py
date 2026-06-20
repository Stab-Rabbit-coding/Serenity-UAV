#!/usr/bin/env python3
"""
build_head_shell.py — apply head-shell features (bosses + aperture cuts) to
the canonical 24in Blender shell using manifold3d boolean operations.

Why this exists
----------------
head_shell24.scad models the same geometry as a CSG tree of OpenSCAD
primitives, importing the 790K-facet Blender-hollowed shell and running
union/difference against it via OpenSCAD's CGAL backend.  CGAL booleans
on a mesh this size are impractical (observed: 20+ minutes, 8+ GB RAM,
no completion) because CGAL's exact-kernel arithmetic does not scale to
high-facet-count meshes.  manifold3d performs the identical boolean
algebra on the same mesh in well under a second, using a different
(floating-point, mesh-simplifying) algorithm.

This script is therefore the canonical generator for
airframe/stls/fuselage/head_shell24.stl (pre-bake / part-local frame —
run tools/bake_hull_frame.py Head_Shell after regenerating to publish
the hull-frame STL).  head_shell24.scad remains the human-readable
single source of truth for every constant and position below; every
position and rotation here is transcribed directly from that file and
must be kept in sync with it by hand.  Re-read head_shell24.scad after
any edit to its position constants and update the matching constant
here.

Coordinate / rotation convention
---------------------------------
Matches OpenSCAD exactly (verified empirically): translate() is a
simple vector add; rotate([rx, 0, 0]) with rx=+90 maps a manifold's
local +Z axis to global -Y.  Transform order replicates SCAD's nested
translate(pos) / rotate(rot) / translate(local_offset) structure:
operations are applied to the locally-built primitive in the same
inside-out order they appear in the SCAD source.

Run:
    python3 tools/build_head_shell.py
Then:
    python3 tools/bake_hull_frame.py Head_Shell

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
"""

import math
import os
import time

import manifold3d as m3d
import numpy as np
import trimesh

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SHELL_SRC = os.path.join(
    REPO_ROOT, "airframe", "blender-scripts", "files-hollowed-24in",
    "head_shell24_2mm_repaired.stl")
OUT_PATH = os.path.join(
    REPO_ROOT, "airframe", "stls", "fuselage", "head_shell24.stl")

FN = 64  # circular_segments, matches SCAD $fn = 64

# ---------------------------------------------------------------------------
# Constants transcribed from head_shell24.scad (Rev S2, 2026-06-16)
# ---------------------------------------------------------------------------
CX = 161.33
CY = -148.57
CZ = 69.08

WALL_T = 3.5

BOSS_OD = 8.0
BOSS_H = 6.0
BOSS_BORE_D = 4.1

VAPER_D = 11.0
VRING_OD = 14.0
VRING_DEP = 0.5
VM16_D = 1.7
VM16_R = 7.0
VCSK16_OD = 3.5
VCSK16_D = 1.0
VRECESS_W = 14.0
VRECESS_D = 3.0

FPV_APER_D = 16.0
FPV_BEZ_W = 29.0
FPV_BEZ_DEP = 1.0
FPV_M2_D = 2.2
FPV_M2_S = 14.0
FPV_CSK2_OD = 4.5
FPV_CSK2_D = 1.2
FPV_BOARD_W = 20.0
FPV_BOARD_D = 5.0

FWD_ROT = [90, 0, 0]

S1A_POS = [CX + 15.0, -280.0, CZ - 5.0]
S1B_POS = [CX + 15.0, -268.0, CZ - 5.0]
FPV_POS = [CX - 15.0, -280.0, CZ - 5.0]

BOSS_AFT_ROT = [0, 90, 0]
BOSS_AFT_POSITIONS = [
    [99, CY + 75, CZ],
    [99, CY + 38, CZ + 52],
    [99, CY - 38, CZ + 52],
    [99, CY - 100, CZ],
    [99, CY - 38, CZ - 52],
    [99, CY + 38, CZ - 52],
]

CAPE_PCB_X = 55.0
CAPE_PCB_Z = 35.0

FARADAY_ENC_X = 60.0
FARADAY_ENC_Z = 40.0

BOOK_DORSAL_Y = CY + 94.0
BOOK_BOSS_ROT = [90, 0, 0]
BOOK_X_CEN = CX
BOOK_Z_CEN = CZ
BOOK_BOSS_DX = 25.0
BOOK_BOSS_DZ = 15.0
BOOK_PANEL_X = 62.0
BOOK_PANEL_Z = 42.0
WALL_MM = 2.0


# ---------------------------------------------------------------------------
# manifold3d helpers — small wrappers matching SCAD primitive semantics
# ---------------------------------------------------------------------------

def cyl(hght, d, fn=FN):
    """Cylinder along +Z from z=0, matching SCAD cylinder(h, d)."""
    return m3d.Manifold.cylinder(hght=hght, radius_low=d / 2.0, circular_segments=fn)


def cube_corner(size):
    """Cube with corner at origin, matching SCAD cube(size)."""
    return m3d.Manifold.cube(size)


def apply_trs(manifold, local_offset=None, rot=None, pos=None):
    """
    Apply SCAD's translate(pos) / rotate(rot) / translate(local_offset)
    nesting, in that inside-out order, to a manifold built in local frame.
    """
    m = manifold
    if local_offset is not None:
        m = m.translate(local_offset)
    if rot is not None:
        m = m.rotate(rot)
    if pos is not None:
        m = m.translate(pos)
    return m


# ---------------------------------------------------------------------------
# Feature builders — transcribed from head_shell24.scad modules
# ---------------------------------------------------------------------------

def m3_boss(pos, rot):
    """SCAD module m3_boss: 8mm OD x 6mm boss post with M3 insert bore."""
    outer = cyl(BOSS_H, BOSS_OD)
    bore = cyl(BOSS_H + 0.1, BOSS_BORE_D)
    boss = outer - bore
    return apply_trs(boss, rot=rot, pos=pos)


def book_dorsal_boss(x_pos, z_pos):
    """SCAD module book_dorsal_boss."""
    outer = cyl(BOSS_H, BOSS_OD)
    bore = cyl(BOSS_H + 0.1, BOSS_BORE_D)
    boss = outer - bore
    return apply_trs(boss, rot=BOOK_BOSS_ROT, pos=[x_pos, BOOK_DORSAL_Y, z_pos])


def book_dorsal_panel_cut():
    """SCAD module book_dorsal_panel_cut."""
    box = cube_corner([BOOK_PANEL_X, WALL_MM + 2.0, BOOK_PANEL_Z])
    return box.translate([
        BOOK_X_CEN - BOOK_PANEL_X / 2,
        BOOK_DORSAL_Y - 1.0,
        BOOK_Z_CEN - BOOK_PANEL_Z / 2,
    ])


def vlsensor_cut(pos, rot):
    """SCAD module vlsensor_cut: VL53L5CX flush-mount cutter."""
    parts = []

    # PMMA aperture bore through full wall
    parts.append(cyl(WALL_T + 2, VAPER_D))

    # Seat ring: 0.5mm recess at exterior face
    seat = cyl(VRING_DEP + 1, VRING_OD).translate([0, 0, WALL_T + 1 - VRING_DEP])
    parts.append(seat)

    # 4x M1.6 countersunk through-holes at 45/135/225/315 deg
    for a in (45, 135, 225, 315):
        rad = math.radians(a)
        dx = VM16_R * math.cos(rad)
        dy = VM16_R * math.sin(rad)
        shaft = cyl(WALL_T + 2, VM16_D).translate([dx, dy, 0])
        parts.append(shaft)
        csk = m3d.Manifold.cylinder(
            height=VCSK16_D + 1, radius_low=VM16_D / 2.0,
            radius_high=VCSK16_OD / 2.0, circular_segments=FN
        ).translate([dx, dy, WALL_T + 1 - VCSK16_D])
        parts.append(csk)

    # Carrier board recess on interior face
    recess = cube_corner([VRECESS_W, VRECESS_W, VRECESS_D + 1]).translate(
        [-VRECESS_W / 2, -VRECESS_W / 2, 0])
    parts.append(recess)

    cutter = parts[0]
    for p in parts[1:]:
        cutter = cutter + p

    return apply_trs(cutter, local_offset=[0, 0, -(WALL_T + 1)], rot=rot, pos=pos)


def fpv_cut(pos, rot):
    """SCAD module fpv_cut: 28mm FPV camera flush-recess cutter."""
    parts = []

    # Lens aperture bore
    parts.append(cyl(WALL_T + 2, FPV_APER_D))

    # Bezel seating recess: 1mm deep at exterior, 29x29mm
    bezel = cube_corner([FPV_BEZ_W, FPV_BEZ_W, FPV_BEZ_DEP + 1]).translate(
        [-FPV_BEZ_W / 2, -FPV_BEZ_W / 2, WALL_T + 1 - FPV_BEZ_DEP])
    parts.append(bezel)

    # 4x M2 countersunk mount holes (14x14mm grid)
    for dx in (-FPV_M2_S / 2, FPV_M2_S / 2):
        for dy in (-FPV_M2_S / 2, FPV_M2_S / 2):
            shaft = cyl(WALL_T + 2, FPV_M2_D).translate([dx, dy, 0])
            parts.append(shaft)
            csk = m3d.Manifold.cylinder(
                height=FPV_CSK2_D + 1, radius_low=FPV_M2_D / 2.0,
                radius_high=FPV_CSK2_OD / 2.0, circular_segments=FN
            ).translate([dx, dy, WALL_T + 1 - FPV_CSK2_D])
            parts.append(csk)

    # Camera body pocket on interior face
    pocket = cube_corner([FPV_BOARD_W, FPV_BOARD_W, FPV_BOARD_D + 1]).translate(
        [-FPV_BOARD_W / 2, -FPV_BOARD_W / 2, 0])
    parts.append(pocket)

    cutter = parts[0]
    for p in parts[1:]:
        cutter = cutter + p

    return apply_trs(cutter, local_offset=[0, 0, -(WALL_T + 1)], rot=rot, pos=pos)


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def manifold_from_stl(path):
    mesh = trimesh.load_mesh(path, force="mesh")
    if not mesh.is_watertight:
        raise RuntimeError(f"{path}: not watertight after force='mesh' load")
    return m3d.Manifold(m3d.Mesh(
        vert_properties=np.array(mesh.vertices, dtype=np.float32),
        tri_verts=np.array(mesh.faces, dtype=np.uint32),
    ))


def manifold_to_stl(manifold, path):
    mesh = manifold.to_mesh()
    verts = np.array(mesh.vert_properties)[:, :3]
    faces = np.array(mesh.tri_verts)
    out = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
    out.export(path)


def main():
    t0 = time.time()
    print(f"Loading shell source: {SHELL_SRC}")
    shell = manifold_from_stl(SHELL_SRC)
    print(f"  loaded + converted in {time.time() - t0:.1f}s, "
          f"status={shell.status()}, volume={shell.volume():.1f} mm^3")

    # ---- Positive material: bosses ----
    t0 = time.time()
    additions = []
    for dx in (-BOOK_BOSS_DX, BOOK_BOSS_DX):
        for dz in (-BOOK_BOSS_DZ, BOOK_BOSS_DZ):
            additions.append(book_dorsal_boss(BOOK_X_CEN + dx, BOOK_Z_CEN + dz))
    for pos in BOSS_AFT_POSITIONS:
        additions.append(m3_boss(pos, BOSS_AFT_ROT))

    built = shell
    for a in additions:
        built = built + a
    print(f"  added {len(additions)} bosses in {time.time() - t0:.1f}s, "
          f"status={built.status()}")

    # ---- Negative material: aperture cuts ----
    t0 = time.time()
    cutters = [
        vlsensor_cut(S1A_POS, FWD_ROT),
        vlsensor_cut(S1B_POS, FWD_ROT),
        fpv_cut(FPV_POS, FWD_ROT),
        book_dorsal_panel_cut(),
    ]
    for c in cutters:
        built = built - c
    print(f"  applied {len(cutters)} cuts in {time.time() - t0:.1f}s, "
          f"status={built.status()}, volume={built.volume():.1f} mm^3")

    if built.status() != m3d.Error.NoError:
        raise RuntimeError(f"final manifold status: {built.status()}")

    bb = built.bounding_box()
    print(f"  final bounds: X[{bb[0]:.2f}..{bb[3]:.2f}] "
          f"Y[{bb[1]:.2f}..{bb[4]:.2f}] Z[{bb[2]:.2f}..{bb[5]:.2f}]")

    manifold_to_stl(built, OUT_PATH)
    print(f"Wrote {OUT_PATH}")
    print("This is the printable head_shell24.stl (bosses + aperture cuts "
          "applied); it is a separate artifact from "
          "airframe/stls/fuselage/head_shell24_2mm_repaired.stl, which is "
          "the bare shell baked into hull frame by tools/bake_hull_frame.py "
          "for the FreeCAD assembly.  Do not run bake_hull_frame.py on this "
          "output -- it is not in the COMPONENTS table.")


if __name__ == "__main__":
    main()
