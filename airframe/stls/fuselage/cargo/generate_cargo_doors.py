#!/usr/bin/env python3
# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
#   Hull frame (canonical for ALL design artifacts): X = +port (left),
#   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
#   world origin.  Primary-component STLs published to airframe/stls/
#   are stored directly in hull frame, baked by tools/bake_hull_frame.py.
#
#   This file (Rev R1a, 2026-06-16):
#     Generates cargo bay clamshell doors from the baked hull-frame cargo
#     shell (cargo_sect_shell24_2mm_repaired.stl).
#
#     Coordinate conventions used throughout:
#       X = lateral (port = +X, stbd = -X); ship CL at X ≈ -170 mm
#       Y = longitudinal fore-aft (+Y = aft); bay spans Y ≈ +2 to +108 mm
#       Z = dorsal-ventral (+Z = up); belly at Z ≈ 0
#
#     Hinge line: runs along Y at X = X_HINGE (ship CL), Z = belly exterior Z
#     Port door:  X from X_HINGE to X_MAX (hull +X / port half)
#     Stbd door:  X from X_MIN  to X_HINGE (hull -X / stbd half)
#
#     The script reads belly-facing triangles (normal Z < 0, centroid Z < 10 mm)
#     from the baked shell and builds a bilinear SciPy interpolator
#     belly_z(x2d, y2d) -> Z_ext.  Each door panel's exterior surface follows
#     that contour; the interior is offset +2 mm in +Z.  Four piano-hinge
#     knuckles per door, interleaved port/stbd, axis along Y.
#
#   Previous revision (pre-R1 / 2026-06-01): used a pre-bake shell in a
#   different coordinate frame (Y = vertical, Z = lateral).  Those STLs are
#   superseded by this revision; see TODO.md §1.1.1.2.1 (now resolved).
# ============================================================================
"""
generate_cargo_doors.py — Rev R1a (2026-06-16)
Generate clamshell cargo-bay door STL files in hull-frame coordinates.

Two mirrored halves split at the ship lateral centreline (X = X_HINGE ≈ -170 mm):
  * cargo_door_port.stl   — port half  (X = X_HINGE .. X_MAX)
  * cargo_door_stbd.stl   — stbd half  (X = X_MIN   .. X_HINGE)

Door geometry (hull frame):
  * Exterior surface  — interpolated from cargo belly faces (Z ≈ 0, normal = -Z)
  * Interior surface  — exterior + WALL_T mm offset in +Z
  * Four hinge knuckles per door (CF-PETG, 6 mm OD, 12 mm long, 3.15 mm bore
    for 3 mm CF pin + 0.15 mm radial clearance per side)
  * Knuckles for port and stbd halves are interleaved along Y so the eight
    barrels form one continuous piano-hinge running along Y at X = X_HINGE

Hinge hardware:
  * CF rod: 3 mm OD × bay-width long (Y_BAY_LEN + 4 mm end stops)
  * Knuckle bore: 3.15 mm (3 mm + 2 × 0.075 mm clearance each side)
  * Pin retained by M3 grub-screw blocks epoxied to shell inner wall

Material: CF-PETG (door body and knuckles)
Print: 0.15 mm layers, 4 perimeters, ≥ 40 % infill

References:
  * docs/LANDING_GEAR_ANALYSIS.md — leg/boss attachment positions confirm bay Y span
  * airframe/openscad/fuselage/cargo/cargo_sect_shell24.scad — belly geometry
  * CLAUDE.md §Hull-Frame Coordinate Standard (Rev R1)

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

import os
import sys

import numpy as np
import trimesh
import trimesh.transformations as tft
from scipy.interpolate import griddata

# ---------------------------------------------------------------------------
# Paths — resolved relative to this script file
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHELL_STL  = os.path.join(SCRIPT_DIR, "cargo_sect_shell24_2mm_repaired.stl")
OUT_DIR    = SCRIPT_DIR

# ---------------------------------------------------------------------------
# Hull-frame cargo shell geometry (from CLAUDE.md validated baked extents)
#   Cargo_Shell: X -267.0..-72.7,  Y -71.5..+132.0,  Z 0.0..163.2  (mm)
# ---------------------------------------------------------------------------
X_SHELL_MIN = -267.0    # stbd extremity (hull -X)
X_SHELL_MAX =  -72.7    # port extremity (hull +X)
X_HINGE = (X_SHELL_MIN + X_SHELL_MAX) / 2.0   # ship lateral CL ≈ -169.85 mm

# Cargo bay opening: longitudinal span centred between leg attach points.
# Landing-gear HULL_ATTACH_POS Y rows: 25 mm and 100 mm.  Bay spans Y=2..108.
Y_BAY_LEN = 106.0       # mm — longitudinal door span
Y_BAY_CEN  = 55.0       # mm — Y centre of bay opening
Y_BAY_FWD  = Y_BAY_CEN - Y_BAY_LEN / 2.0   # =  2.0 mm
Y_BAY_AFT  = Y_BAY_CEN + Y_BAY_LEN / 2.0   # = 108.0 mm

# Fall-back exterior belly Z (used when interpolator misses a point)
Z_BELLY_FALLBACK = 0.5  # mm

# Wall thickness (door body, interior offset in +Z direction)
WALL_T = 2.0            # mm

# Grid resolution for belly-surface sampling
GRID_DX = 3.0           # mm step in X
GRID_DY = 3.0           # mm step in Y

# ---------------------------------------------------------------------------
# Hinge knuckle parameters (axis along Y, barrel tangent to belly exterior)
# ---------------------------------------------------------------------------
PIN_D        = 3.0              # mm — CF rod OD
PIN_CL       = 0.075            # mm — radial clearance per side
PIN_BORE_R   = PIN_D / 2.0 + PIN_CL    # 1.575 mm bore radius
KNUCKLE_OD   = 6.0              # mm
KNUCKLE_R    = KNUCKLE_OD / 2.0
KNUCKLE_LEN  = 12.0             # mm — barrel axial length
KNUCKLE_SECTIONS = 36           # polygon approximation

# Knuckle Y-positions: 4 per door, interleaved port/stbd along Y
# Total 8 knuckles, pitch P = (Y_BAY_LEN - KNUCKLE_LEN) / 7
_PITCH   = (Y_BAY_LEN - KNUCKLE_LEN) / 7.0         # ≈ 13.43 mm
_Y_START = Y_BAY_FWD + KNUCKLE_LEN / 2.0            # first knuckle centre Y

# Port knuckles at even slots (0, 2, 4, 6) along Y
KNUCKLE_Y_PORT = [_Y_START + 2 * k * _PITCH for k in range(4)]
# Stbd knuckles at odd slots (1, 3, 5, 7) along Y
KNUCKLE_Y_STBD = [_Y_START + (2 * k + 1) * _PITCH for k in range(4)]

# Knuckle centre: hinge line at X = X_HINGE; Z tangent to belly exterior
KNUCKLE_X = X_HINGE                         # lateral position (hinge line)
KNUCKLE_Z = Z_BELLY_FALLBACK + KNUCKLE_R    # ≈ 3.5 mm (tangent to belly)


# ---------------------------------------------------------------------------
# Helper: load shell and build belly-surface Z interpolator
# ---------------------------------------------------------------------------

def build_belly_interpolator(shell_stl: str):
    """
    Load the baked hull-frame cargo shell STL and return a callable
    belly_z(x2d, y2d) -> Z_ext that gives the exterior belly Z-coordinate at
    any (X, Y) position over the cargo bay opening.

    Belly faces are identified by:
      * Face normal Z component < -0.5  (pointing downward / ventral)
      * Face centroid Z < 10 mm         (near the bottom of the shell)

    Parameters
    ----------
    shell_stl : str
        Path to the baked hull-frame cargo shell STL.

    Returns
    -------
    belly_z : callable  belly_z(x_2d, y_2d) -> z_2d  (same shape as inputs).
    """
    print(f"[belly] loading {shell_stl} …")
    shell = trimesh.load(shell_stl, process=False)
    fc = shell.triangles_center    # (F, 3) — face centroids
    fn = shell.face_normals        # (F, 3) — face normals

    # Select ventral-facing faces (normal pointing -Z, near bottom of shell)
    mask = (fn[:, 2] < -0.5) & (fc[:, 2] < 10.0)
    belly = fc[mask]
    if mask.sum() == 0:
        print("[belly] WARNING: no belly faces found — using flat fallback")

        def belly_z(x2d, y2d):
            return np.full_like(x2d, Z_BELLY_FALLBACK, dtype=float)
        return belly_z

    bx = belly[:, 0]   # X positions of belly face centroids
    by = belly[:, 1]   # Y positions
    bz = belly[:, 2]   # Z positions (exterior surface)

    print(f"[belly] {mask.sum()} belly faces extracted "
          f"X={bx.min():.1f}..{bx.max():.1f}  "
          f"Y={by.min():.1f}..{by.max():.1f}  "
          f"Z={bz.min():.2f}..{bz.max():.2f}")

    def belly_z(x2d, y2d):
        """Interpolate exterior belly Z at 2-D arrays of (X, Y) positions."""
        pts = np.column_stack([x2d.ravel(), y2d.ravel()])
        z = griddata((bx, by), bz, pts, method="linear",
                     fill_value=Z_BELLY_FALLBACK)
        return z.reshape(x2d.shape)

    return belly_z


# ---------------------------------------------------------------------------
# Helper: build closed door panel mesh from belly Z surface grid
# ---------------------------------------------------------------------------

def build_panel_mesh(x_grid: np.ndarray, y_grid: np.ndarray,
                     z_ext: np.ndarray, wall_t: float = WALL_T) -> trimesh.Trimesh:
    """
    Construct a closed triangular mesh for one door panel half.

    Exterior surface follows z_ext(X, Y); interior is offset by wall_t in +Z.

    Parameters
    ----------
    x_grid : 1-D array, length M — lateral X positions (port or stbd half)
    y_grid : 1-D array, length N — longitudinal Y positions (bay span)
    z_ext  : 2-D array (M, N) — exterior belly Z at each (x_grid[i], y_grid[j])
    wall_t : float, mm — inward (+Z) offset for interior surface

    Returns
    -------
    trimesh.Trimesh
    """
    M, N = len(x_grid), len(y_grid)
    z_int = z_ext + wall_t    # interior Z (+Z / inward toward hull)

    # Exterior vertices index = i*N + j  (range 0 .. M*N-1)
    # Interior vertices index = M*N + i*N + j
    ev = np.zeros((M * N, 3), dtype=float)
    iv = np.zeros((M * N, 3), dtype=float)
    for i in range(M):
        for j in range(N):
            k = i * N + j
            ev[k] = [x_grid[i], y_grid[j], z_ext[i, j]]
            iv[k] = [x_grid[i], y_grid[j], z_int[i, j]]

    verts = np.vstack([ev, iv])

    def ei(i, j): return i * N + j           # exterior vertex index
    def ii(i, j): return M * N + i * N + j   # interior vertex index

    faces = []

    # Exterior surface — normal → -Z (ventral / downward)
    # For quad (i,j)(i+1,j)(i+1,j+1)(i,j+1) in hull frame (X=lateral, Y=fore-aft):
    # With vertices (a,b,c): b-a ≈ (dx,0,0), c-a ≈ (dx,dy,0)
    # → (b-a)×(c-a) ≈ (0, 0, +dx·dy) → +Z normal.
    # Reverse winding [a,c,b] to get -Z (exterior belly faces ventral):
    for i in range(M - 1):
        for j in range(N - 1):
            a, b = ei(i, j),     ei(i + 1, j)
            c, d = ei(i + 1, j + 1), ei(i, j + 1)
            faces.append([a, c, b])    # reversed → -Z
            faces.append([a, d, c])    # reversed

    # Interior surface — normal → +Z (dorsal / inward) — forward winding
    for i in range(M - 1):
        for j in range(N - 1):
            a, b = ii(i, j),     ii(i + 1, j)
            c, d = ii(i + 1, j + 1), ii(i, j + 1)
            faces.append([a, b, c])    # forward → +Z
            faces.append([a, c, d])

    # X_MIN edge (i=0) — normal → -X (outboard or hinge edge)
    # Quad: ext(0,j), ext(0,j+1), int(0,j+1), int(0,j)
    # (a,b,c): b-a=(0,dy,0), c-a=(0,dy,wt) → cross=(dy·wt, 0, 0) → +X
    # Reverse to get -X:
    for j in range(N - 1):
        a, b = ei(0, j),     ei(0, j + 1)
        c, d = ii(0, j + 1), ii(0, j)
        faces.append([a, c, b])
        faces.append([a, d, c])

    # X_MAX edge (i=M-1) — normal → +X (outboard or hinge edge) — forward winding
    for j in range(N - 1):
        a, b = ei(M - 1, j),     ei(M - 1, j + 1)
        c, d = ii(M - 1, j + 1), ii(M - 1, j)
        faces.append([a, b, c])
        faces.append([a, c, d])

    # Y_MIN edge (j=0) — normal → -Y (forward edge of bay)
    # Quad: ext(i,0), int(i,0), int(i+1,0), ext(i+1,0)
    # Need -Y normal: (d-a)=(dx,0,0), (c-a)=(dx,0,wt) → cross=(0,-dx·wt,0) → -Y ✓
    for i in range(M - 1):
        a, b = ei(i, 0),     ei(i + 1, 0)
        c, d = ii(i + 1, 0), ii(i, 0)
        faces.append([a, b, c])
        faces.append([a, c, d])

    # Y_MAX edge (j=N-1) — normal → +Y (aft edge of bay) — reversed winding
    for i in range(M - 1):
        a, b = ei(i, N - 1),     ei(i + 1, N - 1)
        c, d = ii(i + 1, N - 1), ii(i, N - 1)
        faces.append([a, c, b])
        faces.append([a, d, c])

    faces = np.array(faces, dtype=np.int64)
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fill_holes(mesh)
    return mesh


# ---------------------------------------------------------------------------
# Helper: build a single hinge knuckle (axis along Y)
# ---------------------------------------------------------------------------

def make_knuckle(y_centre: float) -> trimesh.Trimesh:
    """
    Build one hinge-knuckle barrel: cylinder (KNUCKLE_OD × KNUCKLE_LEN) with a
    coaxial bore (PIN_BORE_R × KNUCKLE_LEN + 2 mm).  Axis runs along Y (fore-aft);
    knuckle centre at (KNUCKLE_X, y_centre, KNUCKLE_Z).

    Returns
    -------
    trimesh.Trimesh — manifold knuckle solid
    """
    # Build cylinder with default axis along Z, then rotate so axis aligns with Y.
    # Rotation -90° about X maps Z → +Y: (x,y,z) → (x, z, -y).
    rot_z_to_y = tft.rotation_matrix(-np.pi / 2, [1, 0, 0])

    barrel = trimesh.creation.cylinder(
        radius=KNUCKLE_R, height=KNUCKLE_LEN, sections=KNUCKLE_SECTIONS
    )
    barrel.apply_transform(rot_z_to_y)

    bore = trimesh.creation.cylinder(
        radius=PIN_BORE_R, height=KNUCKLE_LEN + 2.0, sections=KNUCKLE_SECTIONS
    )
    bore.apply_transform(rot_z_to_y)

    knuckle = trimesh.boolean.difference([barrel, bore], engine="manifold")

    # Translate to hinge-line position
    knuckle.apply_transform(
        tft.translation_matrix([KNUCKLE_X, y_centre, KNUCKLE_Z])
    )
    return knuckle


# ---------------------------------------------------------------------------
# Door generators
# ---------------------------------------------------------------------------

def make_door(side: str, belly_z_fn) -> trimesh.Trimesh:
    """
    Build one clamshell door half in hull-frame coordinates.

    Parameters
    ----------
    side : str — "port" or "stbd"
    belly_z_fn : callable — belly_z(x2d, y2d) -> Z_ext_2d

    Returns
    -------
    trimesh.Trimesh — closed door solid
    """
    assert side in ("port", "stbd"), "side must be 'port' or 'stbd'"

    # X extents and knuckle positions for this half
    if side == "port":
        x_min = X_HINGE
        x_max = X_SHELL_MAX
        knuckle_y_list = KNUCKLE_Y_PORT
    else:
        x_min = X_SHELL_MIN
        x_max = X_HINGE
        knuckle_y_list = KNUCKLE_Y_STBD

    # Sample grid over the door panel
    x_grid = np.arange(x_min, x_max + GRID_DX, GRID_DX)
    y_grid = np.arange(Y_BAY_FWD, Y_BAY_AFT + GRID_DY, GRID_DY)

    xg, yg = np.meshgrid(x_grid, y_grid, indexing="ij")   # shape (M, N)
    z_ext  = belly_z_fn(xg, yg)                            # exterior belly Z

    print(f"[{side}] grid {xg.shape}  "
          f"X={x_grid[0]:.1f}..{x_grid[-1]:.1f}  "
          f"Y={y_grid[0]:.1f}..{y_grid[-1]:.1f}  "
          f"Z_ext={z_ext.min():.2f}..{z_ext.max():.2f}")

    # Build door panel mesh
    panel = build_panel_mesh(x_grid, y_grid, z_ext, wall_t=WALL_T)
    print(f"[{side}] panel verts={len(panel.vertices)} "
          f"faces={len(panel.faces)} watertight={panel.is_watertight}")

    # Build and union hinge knuckle barrels
    knuckles = [make_knuckle(yc) for yc in knuckle_y_list]

    print(f"[{side}] unioning {len(knuckles)} knuckles …")
    try:
        door = trimesh.boolean.union([panel] + knuckles, engine="manifold")
    except Exception as exc:
        print(f"[{side}] WARNING: union failed ({exc}), concatenating meshes")
        door = trimesh.util.concatenate([panel] + knuckles)

    print(f"[{side}] door verts={len(door.vertices)} "
          f"faces={len(door.faces)} watertight={door.is_watertight}")
    return door


# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------

def save(mesh: trimesh.Trimesh, name: str) -> None:
    """Export mesh to STL and print a summary."""
    path = os.path.join(OUT_DIR, name)
    mesh.export(path)
    b = mesh.bounds
    dims = b[1] - b[0]
    print(f"[save] {name}: "
          f"{dims[0]:.1f}×{dims[1]:.1f}×{dims[2]:.1f} mm  "
          f"X={b[0, 0]:.2f}..{b[1, 0]:.2f}  "
          f"Y={b[0, 1]:.2f}..{b[1, 1]:.2f}  "
          f"Z={b[0, 2]:.2f}..{b[1, 2]:.2f}  "
          f"faces={len(mesh.faces)}  watertight={mesh.is_watertight}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Generate port and stbd clamshell door STLs in hull-frame coordinates."""
    if not os.path.isfile(SHELL_STL):
        print(f"ERROR: hull-frame cargo shell STL not found: {SHELL_STL}",
              file=sys.stderr)
        return 1

    print("=== Cargo clamshell door generation — Rev R1a (hull frame) ===")
    print(f"Hull-frame convention: X=+port, Y=+aft, Z=+dorsal")
    print(f"Cargo shell:  X={X_SHELL_MIN:.1f}..{X_SHELL_MAX:.1f}  "
          f"Ship CL X_HINGE={X_HINGE:.2f} mm")
    print(f"Bay span:     Y={Y_BAY_FWD:.1f}..{Y_BAY_AFT:.1f} mm "
          f"(length={Y_BAY_LEN:.1f} mm)")
    print(f"Hinge knuckle Z centre = {KNUCKLE_Z:.2f} mm  "
          f"(barrel tangent to belly at Z≈{Z_BELLY_FALLBACK:.1f})")
    print(f"Knuckle bore radius = {PIN_BORE_R:.3f} mm  "
          f"(3 mm CF rod + {PIN_CL*2:.2f} mm dia clearance)")
    print()

    belly_z = build_belly_interpolator(SHELL_STL)
    print()

    port_door = make_door("port", belly_z)
    save(port_door, "cargo_door_port.stl")
    print()

    stbd_door = make_door("stbd", belly_z)
    save(stbd_door, "cargo_door_stbd.stl")
    print()

    print("=== Done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
