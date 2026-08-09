#!/usr/bin/env python3
"""Solve the common Rev R6 landing-gear bay MOUNTING-PAD plane (LG-10 / LG-02).

Purpose
-------
The Rev R6 bay plate is a single shared part bolted to the cargo-shell flank at
four canonical stations (docs/LANDING_GEAR_ANALYSIS.md Rev R6 SS2.2).  Measuring
the baked outer skin shows the as-designed surface-mount assumption does not
hold:

  * the plate back face floats 14-17 mm OUTBOARD of the skin at hip height;
  * `BAY_CANT = 22` leans the plate INBOARD at the top, but the real flank
    leans OUTBOARD going up (half-width grows from ~66 mm at Z=18 to ~82 mm at
    Z=94 at the aft stations) -- the cant sign is inverted;
  * the flank is doubly curved: best-fit-plane deviation over the 82 x 40 mm
    footprint is 15-17 mm peak-to-peak aft and up to 42 mm at fore-port;
  * the fore and aft stations are DIFFERENT surfaces (fore sits on the flat
    door-frame wall plus a knuckle above Z=40; aft is a smooth flaring turn),
    so no single flat back face can conform to all four.

The accepted fix (owner decision, 2026-08-08) is to THICKEN the shell locally at
each station.  A FLAT pad face was evaluated first and rejected on mass: because
the pad would have to fill 9-30 mm of hull curvature, the four pads came to
228.6 cm^3 = 240 g -- more than the entire 436 g gear system it serves, against
an open mass-reduction item (LG-18).  Intermediate topologies were no better
(8 mm picture frame 113 g; five Ø18 island pads 61 g, but islands abandon the
canonical continuous recessed bay).

The pad is therefore HULL-CONFORMING (owner direction, 2026-08-09): it follows
the real skin at constant thickness rather than filling out to a plane, and the
bay plate's back face is curved to match.  Both sides then hold the canonical
recessed flank bay of [REF-CAD-003] Sheet 5 / [REF-CAD-002].  Cost at the
82 x 40 mm footprint (true surface area ~5.3 x 10^3 mm^2 per station):

    +3 mm thickening   63.4 cm^3    66.6 g      <- baseline
    +4 mm thickening   84.6 cm^3    88.8 g
    +5 mm thickening  105.7 cm^3   111.0 g

Consequence for the BOM: the fore and aft flanks are different surfaces, so a
conforming back face cannot be one shared part.  The bay becomes TWO unique
geometries (fore, aft), each printed as a mirrored pair -- SS11.4's
"shared BOM both variants" claim must be amended.  The mirror pairs do match:
aft-port and aft-stbd agree to ~0.5 mm.

This tool reports both: the flat-plane fit (the evidence that the as-designed
surface mount cannot work) and the conforming-pad sizing that supersedes it.

Method
------
Each station's shell vertices are pulled once into that corner's leg-local frame
(via the corner's hip + swing-azimuth transform).  For a candidate (back_x,
cant) the pad plane is built in that frame and every skin vertex is projected
onto it: the in-plane coordinates select the footprint, and the signed normal
distance is the pad thickness.  The footprint is binned and the MOST OUTBOARD
skin point in each bin is kept, which is what discards the inner wall of the
2 mm shell without a separate body-splitting pass.

For a fixed cant the thickness field is affine in back_x, so a single
projection per corner fixes the whole back_x family analytically and the sweep
only has to scan cant.

Outputs the per-corner pad thickness statistics, the solved plane, and the
resulting pad volume/mass so the LG-18 mass ledger can be updated.

Coordinate frames
-----------------
Hull frame  : X = +port, Y = +aft, Z = +dorsal; cargo belly Z = 0;
              centreline X = -169.9 (airframe/AGENTS.md).
Leg-local   : hip pin at origin, +X outboard along the swing azimuth,
              pin axis = local Y, +Z dorsal
              (airframe/openscad/fuselage/canonical_leg_r6_1_5in.scad header).

References (REFERENCES.md)
--------------------------
  [REF-CAD-003] QMx "Official Serenity Blueprints Reference Pack" (2007),
                Sheet 5 "Ventral Surface Plan View" -- canonical bay stations.
  [REF-CAD-002] Nick Henning reference renders -- recessed flank bay detail.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-08, per AGENTS.md AI attribution.
License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>

Run: python3 tools/landing_gear_bay_pad_fit.py
"""

import os

import numpy as np
import trimesh

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SHELL_STL = os.path.join(
    REPO_ROOT,
    "airframe",
    "stls",
    "fuselage",
    "cargo",
    "cargo_sect_shell24_2mm_repaired.stl",
)

# ---------------------------------------------------------------------------
# Rev R6 canonical corner stations (docs/LANDING_GEAR_ANALYSIS.md SS2.2).
#   (label, hip_x, hip_y, hip_z, swing_azimuth_deg)
# Swing azimuth: direction of the foot from the hip in plan, deg from hull +X.
# ---------------------------------------------------------------------------
CORNERS = [
    ("fore-port", -90.0, -7.0, 38.0, -22.4),
    ("fore-stbd", -249.8, -7.0, 38.0, -157.6),
    ("aft-port", -79.0, 107.0, 38.0, 28.0),
    ("aft-stbd", -260.8, 107.0, 38.0, 152.0),
]

# Bay plate footprint, leg-local (canonical_leg_r6_*.scad bay()):
#   plate origin at [BAY_BACK_X, 0, PLATE_Z0], rotated -cant about local Y,
#   then spanning PLATE_S0..PLATE_S1 up the canted plane and +/-W/2 along the
#   pin axis.
PLATE_Z0 = 12.0  # plate frame origin height above the hip
PLATE_S0 = -34.0  # bottom of the plate, along the canted plane
PLATE_S1 = 48.0  # top of the plate  (82 mm total = BAY_PLATE_L)
PLATE_W = 40.0  # BAY_PLATE_W, along the pin axis

# Pad design rules.
PAD_MIN = 1.5  # mm, minimum pad standoff so the pad always fuses to the skin
PAD_MARGIN = 3.0  # mm, pad footprint grown beyond the plate edge (fillet room)
NS_CELLS = 17  # footprint bins along the canted plane
NW_CELLS = 9  # footprint bins along the pin axis
BAND = 45.0  # mm, normal-direction band about the plane for skin candidates
PAD_THICKNESSES = (3.0, 4.0, 5.0)  # candidate conforming-pad thickenings, mm
RHO_PRINT = 1.05e-3  # g/mm^3, CF-PETG at print density (merge_cargo_interior)
FACING_MIN = 0.30  # min cos(angle) between vertex normal and the plane normal

# Search grid for the common plane.  Coarse sweep then a local refine -- a
# 0.5 deg sweep over the whole range would re-cast every ray 141 times for no
# extra resolution in the answer.
CANT_COARSE = np.arange(-45.0, 30.01, 2.5)  # +ve = leans inboard at the top
CANT_REFINE_HALFWIDTH = 3.0
CANT_REFINE_STEP = 0.25


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


def corner_rotation(az_deg):
    """Leg-local -> hull rotation for a corner at swing azimuth az_deg."""
    a = np.radians(az_deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def pad_plane_local(back_x, cant_deg, margin=0.0):
    """Return (origin, e_s, e_w, normal) of the pad plane in the leg frame.

    e_s runs up the canted plane, e_w along the pin axis, normal points
    outboard (away from the hull).
    """
    t = np.radians(cant_deg)
    # Rotating by -cant about local Y maps plate +z to (-sin t, 0, cos t).
    e_s = np.array([-np.sin(t), 0.0, np.cos(t)])
    e_w = np.array([0.0, 1.0, 0.0])
    # Operand order matters: cross(e_s, e_w) is (-cos t, 0, -sin t), which
    # points INBOARD and silently negates every standoff.  cross(e_w, e_s)
    # gives the outboard face normal (cos t, 0, sin t) the plate actually has.
    normal = np.cross(e_w, e_s)
    normal = normal / np.linalg.norm(normal)
    origin = np.array([back_x, 0.0, PLATE_Z0])
    return origin, e_s, e_w, normal


def skin_points(mesh, corner, reach=85.0):
    """Outward-facing shell vertices near a station, in the LEG-LOCAL frame.

    Returns (points, normals), both in the corner's leg-local frame.

    Projection against this point set replaces ray casting.  A Moller-Trumbore
    sweep was tried first and is the wrong tool here: neither rtree nor embree
    is installed, so every candidate plane would re-test ~10^5 faces against
    ~10^2 rays, and the (rays x faces x 3) intermediates ran to multiple GB.
    Vertex spacing on this mesh is well under 1 mm, far finer than the
    pad-thickness decision needs.

    The vertex normals come back with the points because a bare (s, w)
    footprint window is an infinite prism along the plane normal: without a
    facing test it also captures the dorsal deck and the opposite flank, whose
    points then win the per-cell "most outboard" reduction and produce
    nonsense standoffs (-85 mm was observed).  Callers must filter on facing.
    """
    _, hx, hy, hz, az = corner
    c = np.array([hx, hy, hz])
    v = mesh.vertices
    near = np.all((v >= c - reach) & (v <= c + reach), axis=1)
    R = corner_rotation(az)
    pts = (R.T @ (v[near] - c).T).T
    nrm = (R.T @ mesh.vertex_normals[near].T).T
    return pts, nrm


# ---------------------------------------------------------------------------
# Standoff measurement
# ---------------------------------------------------------------------------


def conforming_pad(mesh, corner, back_x, cant_deg, margin=PAD_MARGIN):
    """True surface area of the skin patch under the bay footprint.

    The conforming pad is a constant-thickness thickening of this patch, so its
    volume is (area x thickness).  Uses face centroids and real face areas, not
    the projected footprint, because the flank is doubly curved and the
    projected area understates it.
    """
    _, hx, hy, hz, az = corner
    c = np.array([hx, hy, hz])
    R = corner_rotation(az)
    origin, e_s, e_w, normal = pad_plane_local(back_x, cant_deg)

    v = mesh.vertices
    near = np.all((v >= c - 85.0) & (v <= c + 85.0), axis=1)
    fidx = np.where(near[mesh.faces].all(axis=1))[0]
    if len(fidx) == 0:
        return 0.0

    cen = (R.T @ (mesh.triangles[fidx].mean(axis=1) - c).T).T
    fnrm = (R.T @ mesh.face_normals[fidx].T).T
    rel = cen - origin
    s, w, d = rel @ e_s, rel @ e_w, rel @ normal

    s0, s1 = PLATE_S0 - margin, PLATE_S1 + margin
    w0, w1 = -PLATE_W / 2 - margin, PLATE_W / 2 + margin
    keep = (
        (s >= s0)
        & (s <= s1)
        & (w >= w0)
        & (w <= w1)
        & (np.abs(d) <= BAND)
        & ((fnrm @ normal) >= FACING_MIN)
    )
    return float(mesh.area_faces[fidx][keep].sum())


def corner_standoff(skin, back_x, cant_deg, margin=PAD_MARGIN,
                    ns=NS_CELLS, nw=NW_CELLS):
    """Pad thickness over the footprint, from leg-local skin points.

    `skin` is the (points, normals) pair from skin_points().  Candidates are
    restricted to outward-facing vertices inside a normal-direction band about
    the plane, then binned into ns x nw footprint cells; the MOST OUTBOARD
    survivor in each cell sets that cell's pad thickness.  The facing test
    rejects the dorsal deck and the far flank; the max-per-cell reduction then
    discards the inner wall of the 2 mm shell.

    Returns the per-cell pad thickness (positive = skin lies inboard of the
    plane, so the pad has that much material to make up).  Cells with no
    qualifying skin under them are dropped.
    """
    pts_l, nrm_l = skin
    origin, e_s, e_w, normal = pad_plane_local(back_x, cant_deg)
    rel = pts_l - origin
    s = rel @ e_s
    w = rel @ e_w
    d = rel @ normal  # +ve = outboard of the plane

    s0, s1 = PLATE_S0 - margin, PLATE_S1 + margin
    w0, w1 = -PLATE_W / 2 - margin, PLATE_W / 2 + margin
    keep = (
        (s >= s0)
        & (s <= s1)
        & (w >= w0)
        & (w <= w1)
        & (np.abs(d) <= BAND)
        & ((nrm_l @ normal) >= FACING_MIN)
    )
    if not keep.any():
        return np.array([])
    s, w, d = s[keep], w[keep], d[keep]

    si = np.clip(((s - s0) / (s1 - s0) * ns).astype(int), 0, ns - 1)
    wi = np.clip(((w - w0) / (w1 - w0) * nw).astype(int), 0, nw - 1)
    flat = si * nw + wi
    out = np.full(ns * nw, -np.inf)
    np.maximum.at(out, flat, d)
    return -out[np.isfinite(out)]


def main():
    print(f"Loading {os.path.relpath(SHELL_STL, REPO_ROOT)} ...", flush=True)
    mesh = trimesh.load(SHELL_STL)
    print(
        f"  {len(mesh.faces):,} faces  watertight={mesh.is_watertight}  "
        f"bounds={np.round(mesh.bounds, 1).tolist()}",
        flush=True,
    )

    # ------------------------------------------------------------------
    # Report the AS-DESIGNED plane first (BAY_BACK_X = -8, BAY_CANT = 22)
    # so the defect this tool fixes is on the record.
    # ------------------------------------------------------------------
    print("  gathering skin points around each station ...", flush=True)
    skins = {c[0]: skin_points(mesh, c) for c in CORNERS}
    for label, (p, _) in skins.items():
        print(f"    {label:10s} {len(p):,} vertices", flush=True)

    print("\n=== AS-DESIGNED plane: BAY_BACK_X = -8.0, BAY_CANT = +22 ===")
    for corner in CORNERS:
        th = corner_standoff(skins[corner[0]], -8.0, 22.0)
        if len(th) == 0:
            print(f"  {corner[0]:10s}: NO SKIN under the footprint")
            continue
        print(
            f"  {corner[0]:10s}: standoff min {th.min():+7.2f}  "
            f"max {th.max():+7.2f}  mean {th.mean():+7.2f} mm  "
            f"({len(th)} cells on skin)"
        )
    print(
        "  (negative standoff = the hull skin pokes THROUGH the plate's back\n"
        "   face -- the plate and the hull interfere there)"
    )

    # ------------------------------------------------------------------
    # Solve the common pad plane.
    # ------------------------------------------------------------------
    print("\n=== solving common pad plane (minimise worst-case pad thickness) ===")

    def evaluate(cant):
        """Best (worst-case thickness, back_x, per-corner thicknesses) at cant.

        For a fixed cant the thickness field is affine in back_x: the plane
        origin moves along hull +X, and the plane normal is (cos t, 0, sin t),
        so shifting BAY_BACK_X by d shifts every thickness by d*cos(t).  One
        projection per corner therefore fixes the whole back_x family.
        """
        per_corner = []
        for corner in CORNERS:
            th = corner_standoff(skins[corner[0]], 0.0, cant)
            if len(th) < 0.5 * NS_CELLS * NW_CELLS:
                return None
            per_corner.append(th)
        allv = np.concatenate(per_corner)
        ct = np.cos(np.radians(cant))
        if ct < 0.2:  # plane nearly edge-on to hull X -- back_x loses authority
            return None
        back_x = (PAD_MIN - allv.min()) / ct  # min thickness >= PAD_MIN
        shift = back_x * ct
        return (
            allv.max() + shift,
            cant,
            back_x,
            [c + shift for c in per_corner],
        )

    best = None
    for cant in CANT_COARSE:
        r = evaluate(cant)
        if r is not None and (best is None or r[0] < best[0]):
            best = r
        print(
            f"    cant {cant:+6.1f}: "
            + ("no coverage" if r is None else f"worst pad {r[0]:6.2f} mm"),
            flush=True,
        )

    if best is None:
        raise SystemExit("No candidate plane covered all four stations.")

    lo = best[1] - CANT_REFINE_HALFWIDTH
    hi = best[1] + CANT_REFINE_HALFWIDTH
    print(f"  refining {lo:+.1f}..{hi:+.1f} deg at {CANT_REFINE_STEP} deg ...")
    for cant in np.arange(lo, hi + 1e-9, CANT_REFINE_STEP):
        r = evaluate(cant)
        if r is not None and r[0] < best[0]:
            best = r

    worst, cant, back_x, per_corner = best
    print(f"  BAY_CANT   = {cant:+.1f} deg   (as-designed +22 -> inverted sign)")
    print(f"  BAY_BACK_X = {back_x:+.2f} mm  (as-designed -8.00)")
    print(f"  worst-case pad thickness = {worst:.2f} mm")

    print("\n  per-corner pad thickness (mm):")
    total_vol = 0.0
    slab_vol = 0.0
    area = (PLATE_S1 - PLATE_S0 + 2 * PAD_MARGIN) * (PLATE_W + 2 * PAD_MARGIN)
    for (label, *_), th in zip(CORNERS, per_corner):
        vol = th.mean() * area
        total_vol += vol
        slab_vol += vol
        print(
            f"    {label:10s} min {th.min():5.2f}  max {th.max():6.2f}  "
            f"mean {th.mean():5.2f}   pad vol ~{vol / 1000.0:6.2f} cm^3"
        )

    print(
        f"\n  total added pad volume ~{total_vol / 1000.0:.2f} cm^3  "
        f"-> ~{total_vol * RHO_PRINT:.1f} g added to the cargo shell"
    )

    print(
        "\n  ^ REJECTED on mass: a flat pad must fill the hull's curvature.\n"
        "    Retained above only as the evidence that the as-designed flat\n"
        "    surface mount cannot seat.  The build uses the conforming pad."
    )

    # ------------------------------------------------------------------
    # Conforming pad (the adopted design).
    # ------------------------------------------------------------------
    print("\n=== CONFORMING pad — constant thickening that follows the skin ===")
    print("  station      surface area    +3 mm      +4 mm      +5 mm")
    totals = {t: 0.0 for t in PAD_THICKNESSES}
    for corner in CORNERS:
        area = conforming_pad(mesh, corner, back_x, cant)
        row = f"  {corner[0]:10s}  {area:8.0f} mm^2"
        for t in PAD_THICKNESSES:
            totals[t] += area * t
            row += f"  {area * t / 1000.0:6.2f} cm^3"
        print(row)

    print()
    for t in PAD_THICKNESSES:
        v = totals[t]
        print(
            f"  +{t} mm pad total: {v / 1000.0:6.2f} cm^3 -> {v * RHO_PRINT:5.1f} g"
            f"   (flat slab: {slab_vol / 1000.0:.1f} cm^3 / "
            f"{slab_vol * RHO_PRINT:.1f} g)"
        )
    print(
        "\n  Adopted: +3 mm (2 mm wall -> 5 mm local) = "
        f"{totals[3.0] * RHO_PRINT:.1f} g on the cargo shell.\n"
        "  BOM consequence: fore and aft flanks differ, so the conforming back\n"
        "  face makes the bay TWO unique geometries (fore, aft), each a\n"
        "  mirrored pair -- amend LANDING_GEAR_ANALYSIS.md SS11.4."
    )


if __name__ == "__main__":
    main()
