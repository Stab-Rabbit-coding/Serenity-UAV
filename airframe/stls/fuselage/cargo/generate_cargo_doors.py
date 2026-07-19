#!/usr/bin/env python3
# ============================================================================
# HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
#   Hull frame (canonical for ALL design artifacts): X = +port (left),
#   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
#   world origin.  Primary-component STLs published to airframe/stls/
#   are stored directly in hull frame, baked by tools/bake_hull_frame.py.
#
#   This file (Rev R1b, 2026-06-22):
#     Generates cargo bay clamshell doors from the baked hull-frame cargo
#     shell (cargo_sect_shell24_2mm_repaired.stl).
#
#     Coordinate conventions used throughout:
#       X = lateral (port = +X, stbd = -X); ship CL at X ≈ -170 mm
#       Y = longitudinal fore-aft (+Y = aft); bay spans Y ≈ +2 to +108 mm
#       Z = dorsal-ventral (+Z = up); belly at Z ≈ 0
#
#     Hinge lines run along Y at the OUTBOARD flank/belly edge of each door —
#     X = X_MIN (stbd side) and X = X_MAX (port side), Z = belly exterior Z
#     at that flank.  The two free edges meet at the ship centreline X_CL
#     when closed.  Each door is its own independent piano hinge pinned to
#     the fuselage (NOT a shared centreline hinge joining the two panels):
#     swinging open, each door rotates about its own outboard pin and drops
#     DOWN AND OUT from the aircraft, through a 180 deg range of motion,
#     opening the bottom of the cargo bay between the two hinge lines.
#     Port door:  X from X_CL to X_MAX (hull +X / port half), hinge at X_MAX
#     Stbd door:  X from X_MIN  to X_CL (hull -X / stbd half), hinge at X_MIN
#
#     The script reads belly-facing triangles (normal Z < 0, centroid Z < 10 mm)
#     from the baked shell and builds a bilinear SciPy interpolator
#     belly_z(x2d, y2d) -> Z_ext.  Each door panel's exterior surface follows
#     that contour; the interior is offset +2 mm in +Z.  Four piano-hinge
#     knuckles per door, evenly spaced along that door's own outboard hinge
#     line, axis along Y.
#
#   Rev R1a (2026-06-16) incorrectly placed both doors' hinge knuckles at the
#   centreline X_CL with the free edges at the hull sides — backwards from
#   the door behaviour already assumed everywhere else in the repo (see
#   TODO.md §1.4.2 and rcrs49_wire_post.scad, both of which describe the
#   doors hinging at the outboard flank/belly edge and swinging up to 180 deg
#   — that text was written assuming the corrected geometry below).  Rev R1b
#   corrects the hinge location; *(corrected 2026-06-22, with user)*.
#
#   Previous revision (pre-R1 / 2026-06-01): used a pre-bake shell in a
#   different coordinate frame (Y = vertical, Z = lateral).  Those STLs are
#   superseded by this revision; see TODO.md §1.1.1.2.1 (now resolved).
# ============================================================================
"""
generate_cargo_doors.py — Rev R1b (2026-06-22)
Generate clamshell cargo-bay door STL files in hull-frame coordinates.

Two mirrored halves split at the ship lateral centreline (X = X_CL ≈ -170 mm),
each hinged independently at its own OUTBOARD flank/belly edge:
  * cargo_door_port.stl   — port half  (X = X_CL .. X_MAX), hinge at X_MAX
  * cargo_door_stbd.stl   — stbd half  (X = X_MIN   .. X_CL), hinge at X_MIN

The free (non-hinged) edge of each door sits at the centreline X_CL and the
two doors meet there when closed.  Opening, each door swings on its own
outboard pin DOWN AND OUT from the aircraft through a 180 deg range of
motion, clearing the full belly opening between the two hinge lines.

Door geometry (hull frame):
  * Exterior surface  — interpolated from cargo belly faces (Z ≈ 0, normal = -Z)
  * Interior surface  — exterior + WALL_T mm offset in +Z
  * Four hinge knuckles per door (CF-PETG, 6 mm OD, 12 mm long, 3.15 mm bore
    for 3 mm CF pin + 0.15 mm radial clearance per side), evenly spaced along
    that door's own outboard hinge line (no interleaving — port and stbd
    hinges are mechanically independent, each pinned to the fuselage, not to
    each other)

Hinge hardware (one independent piano hinge per door):
  * CF rod: 3 mm OD × bay-width long (Y_BAY_LEN + 4 mm end stops), one per side
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
SHELL_STL = os.path.join(SCRIPT_DIR, "cargo_sect_shell24_2mm_repaired.stl")
OUT_DIR = SCRIPT_DIR

# ---------------------------------------------------------------------------
# Hull-frame cargo shell geometry (from CLAUDE.md validated baked extents)
#   Cargo_Shell: X -267.0..-72.7,  Y -71.5..+132.0,  Z 0.0..163.2  (mm)
# ---------------------------------------------------------------------------
X_SHELL_MIN = -267.0  # stbd extremity (hull -X)
X_SHELL_MAX = -72.7  # port extremity (hull +X)
X_CL = (X_SHELL_MIN + X_SHELL_MAX) / 2.0  # ship lateral CL ≈ -169.85 mm

# Cargo bay opening: longitudinal span centred between leg attach points.
# Landing-gear HULL_ATTACH_POS Y rows: 25 mm and 100 mm.  Bay spans Y=2..108.
Y_BAY_LEN = 106.0  # mm — longitudinal door span
Y_BAY_CEN = 55.0  # mm — Y centre of bay opening
Y_BAY_FWD = Y_BAY_CEN - Y_BAY_LEN / 2.0  # =  2.0 mm
Y_BAY_AFT = Y_BAY_CEN + Y_BAY_LEN / 2.0  # = 108.0 mm

# Fall-back exterior belly Z (used when interpolator misses a point)
Z_BELLY_FALLBACK = 0.5  # mm

# Wall thickness (door body, interior offset in +Z direction)
WALL_T = 2.0  # mm

# Grid resolution for belly-surface sampling
GRID_DX = 3.0  # mm step in X
GRID_DY = 3.0  # mm step in Y

# ---------------------------------------------------------------------------
# Hinge knuckle parameters (axis along Y, barrel tangent to belly exterior)
# ---------------------------------------------------------------------------
PIN_D = 3.0  # mm — CF rod OD
PIN_CL = 0.075  # mm — radial clearance per side
PIN_BORE_R = PIN_D / 2.0 + PIN_CL  # 1.575 mm bore radius
KNUCKLE_OD = 6.0  # mm
KNUCKLE_R = KNUCKLE_OD / 2.0
KNUCKLE_LEN = 12.0  # mm — barrel axial length
KNUCKLE_SECTIONS = 36  # polygon approximation

# A real CF rod is rigid and straight, so all 4 knuckles on one door MUST
# share one constant (X, Z) — only Y may vary along the hinge line.  But the
# belly exterior the door panel follows is contoured (it rises and falls by
# several mm along Y even at the hinge edge), so a straight hinge line
# generally will NOT sit flush against the panel at every knuckle position.
# Each knuckle gets its own GUSSET — a small solid bridging block — to
# positively connect the straight-axis knuckle to the contoured panel edge
# at that knuckle's actual Y, regardless of the local mismatch.  Without
# this, knuckles whose local panel Z differs from the chosen hinge Z by more
# than KNUCKLE_R simply float, disconnected from the rest of the door solid.
GUSSET_DEPTH = 6.0  # mm — inboard reach into the panel from the hinge edge
GUSSET_PAD = 0.5  # mm — extra margin on the bridging box's Z span

# Knuckle Y-positions: 4 per door, evenly spaced along that door's OWN
# outboard hinge line.  Port and stbd hinges are independent piano hinges
# (each door pinned to the fuselage on its own flank) — NOT interleaved onto
# a shared pin, since the hinge lines are no longer coincident.
_PITCH = (Y_BAY_LEN - KNUCKLE_LEN) / 3.0  # ≈ 31.33 mm, 4 evenly spaced
_Y_START = Y_BAY_FWD + KNUCKLE_LEN / 2.0  # first knuckle centre Y

KNUCKLE_Y_PORT = [_Y_START + k * _PITCH for k in range(4)]
KNUCKLE_Y_STBD = [_Y_START + k * _PITCH for k in range(4)]

# Knuckle hinge-line X: OUTBOARD flank/belly edge of each door, not the
# centreline.  This is NOT X_SHELL_MIN/MAX — those are the full cargo-section
# bounding-box extremes (the widest point of the hull cross-section, e.g. at
# the wing-root flare), which lie well outside the flat ventral belly panel
# the doors actually need to cover.  Using the bbox extremes (Rev R1a/early
# R1b) produced door grids that ran ~45 mm past the real belly-mesh data into
# the curved side wall, where the interpolator's flat fallback plane met the
# real contour in a visible crease roughly halfway across each door.
# The correct hinge line is the actual detected edge of the belly mesh,
# computed at runtime in main() from the baked shell via
# build_belly_interpolator()'s returned (x_min, x_max) — that is where the
# flat belly genuinely transitions into the curved flank, matching the
# "outboard flank/belly edge" language used elsewhere in the repo.  See
# main() / make_door() — hinge_x is passed in explicitly, not read as a
# module-level constant.


# ---------------------------------------------------------------------------
# Helper: load shell and build belly-surface Z interpolator
# ---------------------------------------------------------------------------


def build_belly_interpolator(shell_stl: str, y_min: float, y_max: float):
    """
    Load the baked hull-frame cargo shell STL and return a callable
    belly_z(x2d, y2d) -> Z_ext that gives the exterior belly Z-coordinate at
    any (X, Y) position over the cargo bay opening, plus the actual detected
    X extent of the belly mesh within the bay's Y span.

    Belly faces are identified by:
      * Face normal Z component < -0.5  (pointing downward / ventral)
      * Face centroid Z < 10 mm         (near the bottom of the shell)

    The returned (x_min, x_max) is the real edge of that ventral surface —
    where the flat belly transitions into the curved side wall — restricted
    to y_min..y_max.  Door panels and hinge lines MUST be built from this,
    not from the cargo section's overall bounding box: the bounding box
    extends well past the belly into the side wall, and sampling the
    interpolator out there falls back to a flat plane, producing a visible
    crease where the real contour ends.

    Parameters
    ----------
    shell_stl : str
        Path to the baked hull-frame cargo shell STL.
    y_min, y_max : float
        Bay longitudinal span (mm) used to restrict the belly-edge search.

    Returns
    -------
    belly_z : callable  belly_z(x_2d, y_2d) -> z_2d  (same shape as inputs).
    x_min, x_max : float  — detected belly mesh X extent within y_min..y_max.
    """
    print(f"[belly] loading {shell_stl} …")
    shell = trimesh.load(shell_stl, process=False)
    fc = shell.triangles_center  # (F, 3) — face centroids
    fn = shell.face_normals  # (F, 3) — face normals

    # Select ventral-facing faces (normal pointing -Z, near bottom of shell)
    mask = (fn[:, 2] < -0.5) & (fc[:, 2] < 10.0)
    belly = fc[mask]
    if mask.sum() == 0:
        print("[belly] WARNING: no belly faces found — using flat fallback")

        def belly_z_fallback(x2d, y2d):
            return np.full_like(x2d, Z_BELLY_FALLBACK, dtype=float)

        return belly_z_fallback, X_CL - 50.0, X_CL + 50.0

    bx = belly[:, 0]  # X positions of belly face centroids
    by = belly[:, 1]  # Y positions
    bz = belly[:, 2]  # Z positions (exterior surface)

    print(
        f"[belly] {mask.sum()} belly faces extracted "
        f"X={bx.min():.1f}..{bx.max():.1f}  "
        f"Y={by.min():.1f}..{by.max():.1f}  "
        f"Z={bz.min():.2f}..{bz.max():.2f}"
    )

    # The belly is doubly curved, so its detected edge is NOT a constant X
    # across Y — it wanders in/out by several mm row to row.  Taking the
    # single most-outward X found anywhere in the bay (the naive global
    # min/max) would put the hinge line outside the real data for most other
    # Y rows, and griddata silently falls back to a flat Z there — a
    # discontinuity at every row except the one row that actually reaches
    # that far.  Instead, bin by Y (bin width = GRID_DY, matching the door's
    # own sampling grid) and take the WORST CASE across rows: the innermost
    # of each row's outward reach.  That guarantees every sampled grid point,
    # at every Y, lands on real belly data.
    bay_mask = (by >= y_min) & (by <= y_max)
    bx_bay, by_bay = bx[bay_mask], by[bay_mask]
    row_bins = np.arange(y_min, y_max + GRID_DY, GRID_DY)
    row_max_x, row_min_x = [], []
    for lo, hi in zip(row_bins[:-1], row_bins[1:]):
        row_sel = (by_bay >= lo) & (by_bay < hi)
        if row_sel.sum() == 0:
            continue
        row_max_x.append(bx_bay[row_sel].max())
        row_min_x.append(bx_bay[row_sel].min())
    x_min_bay = float(max(row_min_x))  # safe stbd hinge line
    x_max_bay = float(min(row_max_x))  # safe port hinge line
    print(
        f"[belly] safe belly-mesh X extent within bay Y={y_min:.1f}..{y_max:.1f} "
        f"(worst-case across {len(row_max_x)} Y-rows, real data on every row): "
        f"X={x_min_bay:.2f}..{x_max_bay:.2f}  (door grids/hinges use this, "
        f"not the cargo-section bounding box)"
    )

    def belly_z(x2d, y2d):
        """Interpolate exterior belly Z at 2-D arrays of (X, Y) positions."""
        pts = np.column_stack([x2d.ravel(), y2d.ravel()])
        z = griddata((bx, by), bz, pts, method="linear", fill_value=Z_BELLY_FALLBACK)
        return z.reshape(x2d.shape)

    return belly_z, x_min_bay, x_max_bay


# Max per-grid-step Z change accepted as genuine belly curvature.  The clean
# centre of the belly never exceeds ~0.5 mm per GRID_DX/GRID_DY step (see
# DESPIKE_MAX_STEP discussion below); anything bigger is the height-field
# breaking down where the hull curves toward vertical, not real contour.
DESPIKE_MAX_STEP = 1.0  # mm


def despike_grid(
    z: np.ndarray, max_step: float = DESPIKE_MAX_STEP, iterations: int = 3
) -> np.ndarray:
    """
    Suppress height-field artifacts near the aft/outboard corner of the bay,
    where the cargo shell's belly curves so sharply toward the side wall and
    aft bulkhead that a single-valued Z(X, Y) sample breaks down (two
    triangles at nearly the same X, Y can have very different real Z — see
    TODO.md §1.1.1.2 corner-curvature note).  Without this, griddata's
    nearest scattered points there alias into multi-mm spikes that show up
    as a visible crack/step in the printed door.

    Walks each row and column of the grid outward from the free edge and
    clamps any step exceeding max_step to the previous (inboard) value,
    holding the surface flat past the point where real belly data becomes
    unreliable.  Iterated a few passes, alternating X/Y axes, to converge —
    a clamp applied along one axis can introduce a new step along the other.

    This is a print-safety net, not a substitute for the corner geometry
    being verified in FreeCAD before fabrication (see TODO.md §1.1.1.2).
    """
    z2 = z.copy()
    for _ in range(iterations):
        # X axis (rows)
        for i in range(1, z2.shape[0]):
            bad = np.abs(z2[i] - z2[i - 1]) > max_step
            z2[i][bad] = z2[i - 1][bad]
        # Y axis (columns)
        for j in range(1, z2.shape[1]):
            bad = np.abs(z2[:, j] - z2[:, j - 1]) > max_step
            z2[:, j][bad] = z2[:, j - 1][bad]
    return z2


# ---------------------------------------------------------------------------
# Helper: build closed door panel mesh from belly Z surface grid
# ---------------------------------------------------------------------------


def build_panel_mesh(
    x_grid: np.ndarray, y_grid: np.ndarray, z_ext: np.ndarray, wall_t: float = WALL_T
) -> trimesh.Trimesh:
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
    z_int = z_ext + wall_t  # interior Z (+Z / inward toward hull)

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

    def ei(i, j):
        return i * N + j  # exterior vertex index

    def ii(i, j):
        return M * N + i * N + j  # interior vertex index

    faces = []

    # Exterior surface — normal → -Z (ventral / downward)
    # For quad (i,j)(i+1,j)(i+1,j+1)(i,j+1) in hull frame (X=lateral, Y=fore-aft):
    # With vertices (a,b,c): b-a ≈ (dx,0,0), c-a ≈ (dx,dy,0)
    # → (b-a)×(c-a) ≈ (0, 0, +dx·dy) → +Z normal.
    # Reverse winding [a,c,b] to get -Z (exterior belly faces ventral):
    for i in range(M - 1):
        for j in range(N - 1):
            a, b = ei(i, j), ei(i + 1, j)
            c, d = ei(i + 1, j + 1), ei(i, j + 1)
            faces.append([a, c, b])  # reversed → -Z
            faces.append([a, d, c])  # reversed

    # Interior surface — normal → +Z (dorsal / inward) — forward winding
    for i in range(M - 1):
        for j in range(N - 1):
            a, b = ii(i, j), ii(i + 1, j)
            c, d = ii(i + 1, j + 1), ii(i, j + 1)
            faces.append([a, b, c])  # forward → +Z
            faces.append([a, c, d])

    # X_MIN edge (i=0) — normal → -X (outboard or hinge edge)
    # Quad: ext(0,j), ext(0,j+1), int(0,j+1), int(0,j)
    # (a,b,c): b-a=(0,dy,0), c-a=(0,dy,wt) → cross=(dy·wt, 0, 0) → +X
    # Reverse to get -X:
    for j in range(N - 1):
        a, b = ei(0, j), ei(0, j + 1)
        c, d = ii(0, j + 1), ii(0, j)
        faces.append([a, c, b])
        faces.append([a, d, c])

    # X_MAX edge (i=M-1) — normal → +X (outboard or hinge edge) — forward winding
    for j in range(N - 1):
        a, b = ei(M - 1, j), ei(M - 1, j + 1)
        c, d = ii(M - 1, j + 1), ii(M - 1, j)
        faces.append([a, b, c])
        faces.append([a, c, d])

    # Y_MIN edge (j=0) — normal → -Y (forward edge of bay)
    # Quad: ext(i,0), int(i,0), int(i+1,0), ext(i+1,0)
    # Need -Y normal: (d-a)=(dx,0,0), (c-a)=(dx,0,wt) → cross=(0,-dx·wt,0) → -Y ✓
    for i in range(M - 1):
        a, b = ei(i, 0), ei(i + 1, 0)
        c, d = ii(i + 1, 0), ii(i, 0)
        faces.append([a, b, c])
        faces.append([a, c, d])

    # Y_MAX edge (j=N-1) — normal → +Y (aft edge of bay) — reversed winding
    for i in range(M - 1):
        a, b = ei(i, N - 1), ei(i + 1, N - 1)
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


def make_knuckle(x_centre: float, y_centre: float, z_centre: float) -> trimesh.Trimesh:
    """
    Build one hinge-knuckle barrel: cylinder (KNUCKLE_OD × KNUCKLE_LEN) with a
    coaxial bore (PIN_BORE_R × KNUCKLE_LEN + 2 mm).  Axis runs along Y (fore-aft);
    knuckle centre at (x_centre, y_centre, z_centre) — the door's own outboard
    hinge line, NOT the ship centreline.

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
    knuckle.apply_transform(tft.translation_matrix([x_centre, y_centre, z_centre]))
    return knuckle


def make_knuckle_gusset(
    hinge_x: float, y_centre: float, z_hinge: float, local_panel_z: float, side: str
) -> trimesh.Trimesh:
    """
    Build a small bridging block that positively connects one knuckle
    (on the door's straight hinge axis, at z_hinge) to the door panel's
    actual contoured exterior surface at this knuckle's Y (local_panel_z) —
    see GUSSET_DEPTH/GUSSET_PAD comment above KNUCKLE_OD for why this is
    needed: the hinge axis is straight but the panel surface it attaches to
    is not, so the two don't generally touch on their own.

    The block spans this knuckle's Y length, reaches GUSSET_DEPTH inboard
    from the hinge edge into the panel body (side determines which X
    direction is "inboard"), and spans Z from below the lower of
    {knuckle, local panel} to above the higher of the two, so it always
    overlaps both solids regardless of which one is locally higher.

    Parameters
    ----------
    hinge_x : float — this door's hinge-line X (same for every knuckle)
    y_centre : float — this knuckle's Y centre
    z_hinge : float — this door's single straight-axis hinge Z (same for
        every knuckle on this door)
    local_panel_z : float — the door panel's actual exterior Z at
        (hinge_x, y_centre), sampled from the (despiked) panel grid
    side : str — "port" or "stbd"; selects which X direction is inboard

    Returns
    -------
    trimesh.Trimesh — manifold gusset block
    """
    z_lo = min(local_panel_z, z_hinge - KNUCKLE_R) - GUSSET_PAD
    z_hi = max(local_panel_z + WALL_T, z_hinge + KNUCKLE_R) + GUSSET_PAD
    if side == "port":
        x_lo, x_hi = hinge_x - GUSSET_DEPTH, hinge_x + KNUCKLE_R
    else:
        x_lo, x_hi = hinge_x - KNUCKLE_R, hinge_x + GUSSET_DEPTH

    extents = [x_hi - x_lo, KNUCKLE_LEN, z_hi - z_lo]
    centre = [(x_lo + x_hi) / 2.0, y_centre, (z_lo + z_hi) / 2.0]
    gusset = trimesh.creation.box(extents=extents)
    gusset.apply_transform(tft.translation_matrix(centre))
    return gusset


# ---------------------------------------------------------------------------
# Door generators
# ---------------------------------------------------------------------------


def make_door(
    side: str, belly_z_fn, free_edge_x: float, hinge_x: float, knuckle_y_list
) -> trimesh.Trimesh:
    """
    Build one clamshell door half in hull-frame coordinates.

    Parameters
    ----------
    side : str — "port" or "stbd"
    belly_z_fn : callable — belly_z(x2d, y2d) -> Z_ext_2d
    free_edge_x : float — X of the edge that meets the other door (= X_CL)
    hinge_x : float — X of this door's own outboard hinge line, taken from
        the belly mesh's real detected edge (NOT the cargo-section bounding
        box — see build_belly_interpolator)
    knuckle_y_list : sequence of float — Y centres of this door's 4 knuckles

    Returns
    -------
    trimesh.Trimesh — closed door solid
    """
    assert side in ("port", "stbd"), "side must be 'port' or 'stbd'"

    # Door panel spans from the free edge (meets the other door, at X_CL) to
    # this door's own outboard hinge line.  Both bounds come from real belly
    # mesh data, so the whole panel is sampled within the interpolator's
    # convex hull — no flat-fallback region, no discontinuity.
    #
    # Use linspace (not arange) so the grid's outer edge lands EXACTLY on
    # hinge_x rather than one step past it.  arange(x_min, x_max + GRID_DX,
    # GRID_DX) can overshoot x_max by up to one step depending on float
    # rounding — that overshoot point falls just outside the real belly-mesh
    # data and griddata silently returns the flat fallback there, producing
    # a small but real step right at the hinge line.
    x_min, x_max = sorted([free_edge_x, hinge_x])
    n_x = max(2, round((x_max - x_min) / GRID_DX) + 1)
    n_y = max(2, round((Y_BAY_AFT - Y_BAY_FWD) / GRID_DY) + 1)
    x_grid = np.linspace(x_min, x_max, n_x)
    y_grid = np.linspace(Y_BAY_FWD, Y_BAY_AFT, n_y)

    xg, yg = np.meshgrid(x_grid, y_grid, indexing="ij")  # shape (M, N)
    z_ext = belly_z_fn(xg, yg)  # exterior belly Z

    # despike_grid() anchors its X-axis walk at row index 0 and propagates
    # outward, trusting that end as real data.  x_grid is always sorted
    # ascending (low to high X), so row 0 is the free edge (X_CL) only for
    # the port door (free_edge_x < hinge_x there); for the stbd door the
    # free edge is at the HIGH end (row -1).  Flip so the trusted free edge
    # is always at row 0 before despiking, then flip back.
    free_edge_at_low_x = free_edge_x <= hinge_x
    z_for_despike = z_ext if free_edge_at_low_x else z_ext[::-1, :]
    z_ext = despike_grid(z_for_despike)
    z_ext = z_ext if free_edge_at_low_x else z_ext[::-1, :]

    print(
        f"[{side}] grid {xg.shape}  "
        f"X={x_grid[0]:.1f}..{x_grid[-1]:.1f}  "
        f"Y={y_grid[0]:.1f}..{y_grid[-1]:.1f}  "
        f"Z_ext={z_ext.min():.2f}..{z_ext.max():.2f}"
    )

    # Build door panel mesh
    panel = build_panel_mesh(x_grid, y_grid, z_ext, wall_t=WALL_T)
    print(
        f"[{side}] panel verts={len(panel.vertices)} "
        f"faces={len(panel.faces)} watertight={panel.is_watertight}"
    )

    # Hinge axis: a real CF rod is rigid and straight, so ALL knuckles on
    # this door share ONE (X, Z) — only Y varies.  X is hinge_x already;
    # Z is the mean of the panel's actual exterior contour at the 4 knuckle
    # Y positions (sampled from the despiked panel edge column itself, so it
    # tracks whatever the panel really is, not the raw/spiky belly data).
    edge_col = z_ext[-1, :] if free_edge_at_low_x else z_ext[0, :]
    local_panel_z_at_knuckles = np.interp(knuckle_y_list, y_grid, edge_col)
    z_hinge = float(local_panel_z_at_knuckles.mean()) + KNUCKLE_R
    print(
        f"[{side}] straight hinge axis: X={hinge_x:.2f}  Z={z_hinge:.2f} mm  "
        f"(local panel Z at knuckles: "
        f"{np.array2string(local_panel_z_at_knuckles, precision=2)})"
    )

    knuckles = [make_knuckle(hinge_x, yc, z_hinge) for yc in knuckle_y_list]

    # Each knuckle sits on the straight hinge axis, but the panel surface it
    # must bond to is contoured — bridge the gap with a per-knuckle gusset
    # (see make_knuckle_gusset) so every knuckle is positively connected,
    # not just floating near the panel.
    gussets = [
        make_knuckle_gusset(hinge_x, yc, z_hinge, lz, side)
        for yc, lz in zip(knuckle_y_list, local_panel_z_at_knuckles)
    ]

    print(f"[{side}] unioning {len(knuckles)} knuckles + {len(gussets)} gussets …")
    try:
        door = trimesh.boolean.union([panel] + knuckles + gussets, engine="manifold")
    except Exception as exc:
        print(f"[{side}] WARNING: union failed ({exc}), concatenating meshes")
        door = trimesh.util.concatenate([panel] + knuckles + gussets)

    print(
        f"[{side}] door verts={len(door.vertices)} "
        f"faces={len(door.faces)} watertight={door.is_watertight}"
    )
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
    print(
        f"[save] {name}: "
        f"{dims[0]:.1f}×{dims[1]:.1f}×{dims[2]:.1f} mm  "
        f"X={b[0, 0]:.2f}..{b[1, 0]:.2f}  "
        f"Y={b[0, 1]:.2f}..{b[1, 1]:.2f}  "
        f"Z={b[0, 2]:.2f}..{b[1, 2]:.2f}  "
        f"faces={len(mesh.faces)}  watertight={mesh.is_watertight}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Generate port and stbd clamshell door STLs in hull-frame coordinates."""
    if not os.path.isfile(SHELL_STL):
        print(
            f"ERROR: hull-frame cargo shell STL not found: {SHELL_STL}", file=sys.stderr
        )
        return 1

    print("=== Cargo clamshell door generation — Rev R1b (hull frame) ===")
    print("Hull-frame convention: X=+port, Y=+aft, Z=+dorsal")
    print(
        f"Cargo shell bounding box: X={X_SHELL_MIN:.1f}..{X_SHELL_MAX:.1f}  "
        f"Ship CL X_CL={X_CL:.2f} mm"
    )
    print(
        f"Bay span:     Y={Y_BAY_FWD:.1f}..{Y_BAY_AFT:.1f} mm "
        f"(length={Y_BAY_LEN:.1f} mm)"
    )
    print(
        f"Knuckle bore radius = {PIN_BORE_R:.3f} mm  "
        f"(3 mm CF rod + {PIN_CL*2:.2f} mm dia clearance)"
    )
    print()

    belly_z, belly_x_min, belly_x_max = build_belly_interpolator(
        SHELL_STL, Y_BAY_FWD, Y_BAY_AFT
    )
    print()

    # Hinge lines are the REAL detected edges of the belly mesh — port door
    # hinges at the port-side edge, stbd door at the stbd-side edge.  Free
    # edges (both doors) meet at X_CL when closed.
    hinge_x_port = belly_x_max
    hinge_x_stbd = belly_x_min
    print(
        f"Port hinge line: X={hinge_x_port:.2f} mm (outboard belly edge, NOT centreline)"
    )
    print(
        f"Stbd hinge line: X={hinge_x_stbd:.2f} mm (outboard belly edge, NOT centreline)"
    )
    print(
        f"Free edges meet at X_CL={X_CL:.2f} mm when closed; each door "
        f"swings down/out 180 deg about its own outboard pin"
    )
    print()

    port_door = make_door("port", belly_z, X_CL, hinge_x_port, KNUCKLE_Y_PORT)
    save(port_door, "cargo_door_port.stl")
    print()

    stbd_door = make_door("stbd", belly_z, X_CL, hinge_x_stbd, KNUCKLE_Y_STBD)
    save(stbd_door, "cargo_door_stbd.stl")
    print()

    print("=== Done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
