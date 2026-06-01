#!/usr/bin/env python3
"""
generate_cargo_doors.py
Generate clamshell cargo-bay door STL files for the Serenity UAV gondola.

Two mirrored halves split at the gondola lateral centreline (Z = 81.61 mm):
  * cargo_door_port.stl   — port half  (Z = Z_HINGE..163.22 mm)
  * cargo_door_stbd.stl   — stbd half  (Z = 0..Z_HINGE mm)

The exterior of each door exactly matches the canonical Rev-O gondola belly
profile, extracted from s_cargo_sect_shell24_2mm_repaired.stl via face-normal
filtering and bilinear SciPy interpolation.  No boolean intersection is used
(the shell STL is not watertight).

Door geometry:
  * Exterior surface  — interpolated from gondola belly faces
  * Interior surface  — exterior + 2 mm offset (uniform wall thickness)
  * Four hinge knuckles per door (CF-PETG, 6 mm OD, 12 mm long, 3.3 mm bore
    for 3 mm CF pin + 0.15 mm radial clearance)
  * Knuckles for port and stbd halves are longitudinally interleaved so the
    eight barrels form one continuous piano-hinge along Z = Z_HINGE

Hinge hardware:
  * CF rod: 3 mm OD × gondola-belly-width long (163.22 mm + 4 mm end stops)
  * Knuckle bore: 3.15 mm (3 mm + 2 × 0.075 mm clearance each side)
  * Pin seats in M3 grub-screw blocks epoxied to gondola inner shell wall

Material: CF-PETG (door body and knuckles)
Print: 0.15 mm layers, 4 perimeters, ≥ 40 % infill

References:
  * PHASED_BUILD_GUIDE.md §Phase 6 Cargo System
  * s_cargo_sect_shell24.scad Rev O gondola-belly geometry
  * Serenity-UAV TODO.md cargo handling equipment mounts (completed)

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0
"""

import os
import sys

import numpy as np
import trimesh
import trimesh.transformations as tft
from scipy.interpolate import griddata

# ── Output directory ───────────────────────────────────────────────────────────
OUT_DIR = "thingverse-serenity/files-hollowed-18in"
SHELL_STL = os.path.join(OUT_DIR, "s_cargo_sect_shell24_2mm_repaired.stl")

# ── Gondola shell geometry (from bounds / belly-face analysis) ─────────────────
# Shell bounds: X = -201.53..-7.42, Y = -414.81..-211.27, Z = 0..163.22 mm
Z_SHELL_MIN = 0.0       # stbd extremity
Z_SHELL_MAX = 163.22    # port extremity
Z_HINGE = Z_SHELL_MAX / 2.0    # = 81.61 mm — symmetric hinge centreline

# Nominal exterior belly Y in the flat nadir zone (Z ≈ 10..150 mm)
Y_BELLY_EXT = -413.6    # mm
Y_BELLY_INT = Y_BELLY_EXT + 2.0    # interior surface (2 mm wall) = -411.6 mm

# Cargo-bay opening longitudinal span, centred on the gondola (X ≈ -102 mm)
X_BAY_LEN = 106.0       # mm — slightly wider than 4 in (101.6 mm) for frame
X_BAY_CEN = -102.0      # mm
X_BAY_AFT = X_BAY_CEN - X_BAY_LEN / 2.0   # = -155.0 mm
X_BAY_FWD = X_BAY_CEN + X_BAY_LEN / 2.0   # = -49.0 mm

# Grid resolution for belly-surface sampling
GRID_DX = 3.0   # mm step in X
GRID_DZ = 3.0   # mm step in Z

# Wall thickness
WALL_T = 2.0    # mm

# ── Hinge hardware parameters ──────────────────────────────────────────────────
PIN_D = 3.0             # mm, CF rod OD
PIN_CL = 0.075          # mm, radial clearance (each side)
PIN_BORE_R = (PIN_D / 2.0) + PIN_CL    # = 1.575 mm bore radius
KNUCKLE_OD = 6.0        # mm
KNUCKLE_R = KNUCKLE_OD / 2.0           # = 3.0 mm
KNUCKLE_LEN = 12.0      # mm, barrel length per knuckle
KNUCKLE_SEP = 1.0       # mm, axial gap between adjacent knuckles
KNUCKLE_SECTIONS = 36   # polygon approximation

# Knuckle X-positions (four per door, interleaved port / stbd)
# Spaced 22 mm apart within the 106 mm bay; interleaved so gap = 11 mm
KNUCKLE_X_PORT = [-65.0, -98.0, -131.0, -142.0 - KNUCKLE_LEN / 2.0]
KNUCKLE_X_STBD = [-57.0 + KNUCKLE_LEN / 2.0, -79.0, -112.0, -145.0]

# Recalculate to proper interleaved positions
# 4 port + 4 stbd knuckles, alternating, total span ≈ 106 mm
# 8 knuckles total (4 port + 4 stbd), alternating along the hinge line.
# Pitch P = centre-to-centre distance between adjacent knuckles (one per side).
# Total span from first centre to last = 7 P, and the first/last centres sit
# L/2 inboard from the bay ends, so:  7P = X_BAY_LEN - KNUCKLE_LEN  →  P ≈ 13.4 mm
# Gap between adjacent knuckles = P - L ≈ 1.4 mm (adequate clearance).
_PITCH  = (X_BAY_LEN - KNUCKLE_LEN) / 7.0          # ≈ 13.43 mm (adjacent pitch)
_X_START = X_BAY_AFT + KNUCKLE_LEN / 2.0            # = -149.0 mm (slot-0 centre)

# Port knuckles occupy even slots (0, 2, 4, 6); spacing = 2 × pitch
KNUCKLE_X_PORT = [_X_START + 2 * k * _PITCH for k in range(4)]
# Stbd knuckles occupy odd slots (1, 3, 5, 7); start one pitch offset from PORT
KNUCKLE_X_STBD = [_X_START + (2 * k + 1) * _PITCH for k in range(4)]

# Hinge pin centre: sits just inside the exterior belly surface so knuckle
# barrel outer edge is flush with the belly.  Pin centre at:
#   Y = Y_BELLY_EXT + KNUCKLE_R  (barrel tangent to exterior belly face)
#   Z = Z_HINGE
KNUCKLE_Y = Y_BELLY_EXT + KNUCKLE_R    # = -413.6 + 3.0 = -410.6 mm
KNUCKLE_Z = Z_HINGE                     # = 81.61 mm


# ── Helper: load shell and build belly-surface interpolator ───────────────────

def build_belly_interpolator(shell_stl: str):
    """
    Load the gondola shell STL, filter belly-facing triangles, and return a
    callable  belly_y(X_arr, Z_arr) → Y_arr  using bilinear SciPy griddata.

    The shell STL is not watertight so boolean operations are avoided.
    Face centroids with face_normal[Y] < -0.5 AND centroid[Y] < -370 mm are
    classified as belly faces; their (X, Z, Y) triples feed the interpolator.

    Parameters
    ----------
    shell_stl : str
        Path to the gondola shell STL.

    Returns
    -------
    belly_y : callable
        belly_y(x_2d, z_2d) → y_2d  (same shape as inputs).
    """
    print(f"[belly] loading {shell_stl} …")
    shell = trimesh.load(shell_stl, process=False)
    fc = shell.triangles_center    # shape (F, 3)
    fn = shell.face_normals        # shape (F, 3)

    # Select belly-facing faces (downward normal, below Y=-370)
    mask = (fn[:, 1] < -0.5) & (fc[:, 1] < -370.0)
    belly = fc[mask]
    print(f"[belly] {mask.sum()} belly faces extracted "
          f"Z={belly[:,2].min():.1f}..{belly[:,2].max():.1f}  "
          f"Y={belly[:,1].min():.2f}..{belly[:,1].max():.2f}")

    bx = belly[:, 0]
    bz = belly[:, 2]
    by = belly[:, 1]   # exterior Y values

    def belly_y(x2d, z2d):
        """Interpolate exterior belly Y at 2-D arrays of (X, Z) positions."""
        pts = np.column_stack([x2d.ravel(), z2d.ravel()])
        y = griddata((bx, bz), by, pts, method="linear",
                     fill_value=Y_BELLY_EXT)
        return y.reshape(x2d.shape)

    return belly_y


# ── Helper: build closed solid mesh from exterior belly surface grid ───────────

def build_panel_mesh(x_grid: np.ndarray, z_grid: np.ndarray,
                     y_ext: np.ndarray, wall_t: float = WALL_T) -> trimesh.Trimesh:
    """
    Construct a closed, manifold-intended triangular mesh representing a door
    panel whose exterior surface follows y_ext(X, Z) and whose interior surface
    is offset by wall_t in the +Y direction.

    Parameters
    ----------
    x_grid : 1-D array, length M
    z_grid : 1-D array, length N
    y_ext  : 2-D array (M, N), exterior Y at each (x_grid[i], z_grid[j])
    wall_t : float, mm — inward offset for interior surface

    Returns
    -------
    trimesh.Trimesh
    """
    M, N = len(x_grid), len(z_grid)
    y_int = y_ext + wall_t    # interior Y (closer to +Y / inward)

    # ── Vertex arrays ──────────────────────────────────────────────────────────
    # Exterior vertices: index = i*N + j  (0 .. M*N-1)
    # Interior vertices: index = M*N + i*N + j
    ev = np.zeros((M * N, 3), dtype=float)
    iv = np.zeros((M * N, 3), dtype=float)
    for i in range(M):
        for j in range(N):
            k = i * N + j
            ev[k] = [x_grid[i], y_ext[i, j], z_grid[j]]
            iv[k] = [x_grid[i], y_int[i, j], z_grid[j]]

    verts = np.vstack([ev, iv])

    def ei(i, j): return i * N + j           # exterior index
    def ii(i, j): return M * N + i * N + j   # interior index

    faces = []

    # ── Exterior surface — normal → -Y (downward / outward) ──────────────────
    # For quad (i,j)(i+1,j)(i+1,j+1)(i,j+1):
    #   (a,b,c): (b-a)×(c-a) = (dx,0,0)×(dx,0,dz) → (0,-dx·dz,0) → -Y ✓
    #   (a,c,d): same orientation ✓
    for i in range(M - 1):
        for j in range(N - 1):
            a, b = ei(i, j),   ei(i+1, j)
            c, d = ei(i+1, j+1), ei(i, j+1)
            faces.append([a, b, c])
            faces.append([a, c, d])

    # ── Interior surface — normal → +Y (upward / inward) — reversed order ────
    for i in range(M - 1):
        for j in range(N - 1):
            a, b = ii(i, j),   ii(i+1, j)
            c, d = ii(i+1, j+1), ii(i, j+1)
            faces.append([a, c, b])
            faces.append([a, d, c])

    # ── X_MIN edge (i=0) — normal → -X (aft face) ────────────────────────────
    # Quad: ext(0,j), ext(0,j+1), int(0,j+1), int(0,j)
    # (a,b,c): (b-a)×(c-a) = (0,0,dz)×(0,wt,dz) → (-dz·wt,0,0) → -X ✓
    for j in range(N - 1):
        a, b = ei(0, j),   ei(0, j+1)
        c, d = ii(0, j+1), ii(0, j)
        faces.append([a, b, c])
        faces.append([a, c, d])

    # ── X_MAX edge (i=M-1) — normal → +X (fwd face) — reversed ──────────────
    for j in range(N - 1):
        a, b = ei(M-1, j),   ei(M-1, j+1)
        c, d = ii(M-1, j+1), ii(M-1, j)
        faces.append([a, c, b])
        faces.append([a, d, c])

    # ── Z_MIN edge (j=0) — normal → -Z (stbd / outer / hinge edge) ──────────
    # Quad: ext(i,0), int(i,0), int(i+1,0), ext(i+1,0)
    # (a,d,c): (d-a)×(c-a) = (0,wt,0)×(dx,wt,0) → (0,0,-dx·wt) → -Z ✓
    for i in range(M - 1):
        a, b = ei(i, 0),   ei(i+1, 0)
        c, d = ii(i+1, 0), ii(i, 0)
        faces.append([a, d, c])
        faces.append([a, c, b])

    # ── Z_MAX edge (j=N-1) — normal → +Z (port / outer / hinge edge) ─────────
    # (a,b,c): (b-a)×(c-a) = (dx,0,0)×(dx,wt,0) → (0,0,dx·wt) → +Z ✓
    for i in range(M - 1):
        a, b = ei(i, N-1),   ei(i+1, N-1)
        c, d = ii(i+1, N-1), ii(i, N-1)
        faces.append([a, b, c])
        faces.append([a, c, d])

    faces = np.array(faces, dtype=np.int64)
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fill_holes(mesh)
    return mesh


# ── Helper: build a single hinge knuckle solid ────────────────────────────────

def make_knuckle(x_centre: float) -> trimesh.Trimesh:
    """
    Build a hinge-knuckle barrel: a cylinder (KNUCKLE_OD × KNUCKLE_LEN) with a
    coaxial bore (PIN_BORE_R × KNUCKLE_LEN + 2 mm).  Axis runs in X; knuckle
    centre at (x_centre, KNUCKLE_Y, KNUCKLE_Z).

    Returns
    -------
    trimesh.Trimesh — manifold knuckle solid
    """
    # Outer barrel — cylinder with axis along Z, then rotate to X
    barrel = trimesh.creation.cylinder(
        radius=KNUCKLE_R, height=KNUCKLE_LEN, sections=KNUCKLE_SECTIONS
    )
    # Rotate so cylinder axis aligns with X
    barrel.apply_transform(tft.rotation_matrix(np.pi / 2, [0, 1, 0]))

    # Pin bore — slightly longer to ensure clean cut-through
    bore = trimesh.creation.cylinder(
        radius=PIN_BORE_R, height=KNUCKLE_LEN + 2.0, sections=KNUCKLE_SECTIONS
    )
    bore.apply_transform(tft.rotation_matrix(np.pi / 2, [0, 1, 0]))

    knuckle = trimesh.boolean.difference([barrel, bore], engine="manifold")

    # Translate to final position
    knuckle.apply_transform(
        tft.translation_matrix([x_centre, KNUCKLE_Y, KNUCKLE_Z])
    )
    return knuckle


# ── Door generators ────────────────────────────────────────────────────────────

def make_door(side: str, belly_y_fn) -> trimesh.Trimesh:
    """
    Build one clamshell door half.

    Parameters
    ----------
    side : str — "port" or "stbd"
    belly_y_fn : callable — belly_y(x2d, z2d) → y_ext_2d

    Returns
    -------
    trimesh.Trimesh — closed door solid
    """
    assert side in ("port", "stbd"), "side must be 'port' or 'stbd'"

    # Z extents for this door half
    if side == "port":
        z_min = Z_HINGE
        z_max = Z_SHELL_MAX
        knuckle_x_list = KNUCKLE_X_PORT
    else:
        z_min = Z_SHELL_MIN
        z_max = Z_HINGE
        knuckle_x_list = KNUCKLE_X_STBD

    # Sample grid
    x_grid = np.arange(X_BAY_AFT, X_BAY_FWD + GRID_DX, GRID_DX)
    z_grid = np.arange(z_min, z_max + GRID_DZ, GRID_DZ)

    xg, zg = np.meshgrid(x_grid, z_grid, indexing="ij")   # shape (M, N)
    y_ext = belly_y_fn(xg, zg)                             # exterior belly Y

    print(f"[{side}] grid {xg.shape}  "
          f"X={x_grid[0]:.1f}..{x_grid[-1]:.1f}  "
          f"Z={z_grid[0]:.1f}..{z_grid[-1]:.1f}  "
          f"Y_ext={y_ext.min():.2f}..{y_ext.max():.2f}")

    # Build door panel mesh
    panel = build_panel_mesh(x_grid, z_grid, y_ext, wall_t=WALL_T)
    print(f"[{side}] panel verts={len(panel.vertices)} "
          f"faces={len(panel.faces)} watertight={panel.is_watertight}")

    # Build and union knuckle barrels
    knuckles = [make_knuckle(xc) for xc in knuckle_x_list]

    print(f"[{side}] unioning {len(knuckles)} knuckles …")
    try:
        door = trimesh.boolean.union([panel] + knuckles, engine="manifold")
    except Exception as exc:
        print(f"[{side}] WARNING: union failed ({exc}), concatenating meshes")
        # Fallback: concatenate as a multi-body (still valid STL for slicing)
        door = trimesh.util.concatenate([panel] + knuckles)

    print(f"[{side}] door verts={len(door.vertices)} "
          f"faces={len(door.faces)} watertight={door.is_watertight}")
    return door


# ── Save helper ────────────────────────────────────────────────────────────────

def save(mesh: trimesh.Trimesh, name: str) -> None:
    """Export mesh to STL and print a summary."""
    path = os.path.join(OUT_DIR, name)
    mesh.export(path)
    b = mesh.bounds
    dims = b[1] - b[0]
    print(f"[save] {name}: "
          f"{dims[0]:.1f}×{dims[1]:.1f}×{dims[2]:.1f} mm  "
          f"Z={b[0,2]:.2f}..{b[1,2]:.2f}  "
          f"faces={len(mesh.faces)}  watertight={mesh.is_watertight}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    """Generate port and stbd clamshell door STLs."""
    if not os.path.isfile(SHELL_STL):
        print(f"ERROR: shell STL not found: {SHELL_STL}", file=sys.stderr)
        return 1
    if not os.path.isdir(OUT_DIR):
        print(f"ERROR: output directory not found: {OUT_DIR}", file=sys.stderr)
        return 1

    print("=== Cargo clamshell door generation ===")
    print(f"Hinge Z = {Z_HINGE:.2f} mm")
    print(f"Knuckle Y centre = {KNUCKLE_Y:.2f} mm  (barrel flush with belly exterior)")
    print(f"Pin bore radius = {PIN_BORE_R:.3f} mm  (3 mm CF rod + {PIN_CL*2:.2f} mm dia clearance)")
    print(f"Cargo bay X span: {X_BAY_AFT:.1f} to {X_BAY_FWD:.1f} mm "
          f"(length = {X_BAY_LEN:.1f} mm)")
    print()

    # Build belly-surface interpolator once (shared by both doors)
    belly_y = build_belly_interpolator(SHELL_STL)
    print()

    # Port door
    port_door = make_door("port", belly_y)
    save(port_door, "cargo_door_port.stl")
    print()

    # Stbd door
    stbd_door = make_door("stbd", belly_y)
    save(stbd_door, "cargo_door_stbd.stl")
    print()

    print("=== Done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
