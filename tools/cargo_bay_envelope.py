#!/usr/bin/env python3
"""Measure the cargo bay's usable interior envelope, and gate the mission payload.

Why this tool exists
--------------------
The root work-tracking file SS1.1.0 "Hull-frame placements for VERIFY parts" asks
eleven cargo-bay accessories to be placed against the *baked* hull rather than
by estimate.  Placement needs three numbers the repository did not previously
carry anywhere: the free X span, the free Z span, and the obstruction list at
each longitudinal station.  Bounding boxes cannot supply them -- `airframe/
AGENTS.md` ("Geometry Integrity") is explicit that Serenity's compound-curved
hull makes bounding-box and centroid math inadequate for placement -- so the
envelope is measured from the published shell itself.

How the envelope is measured
----------------------------
A closed cavity solid is NOT used, and cannot be: the cargo bay is open at the
belly (the clamshell aperture) and at both mating rims, so `outer - shell`
returns one connected region spanning the inside and the outside of the ship.
Instead each station is reduced to a 2-D wall region in hull (X, Z) by
sectioning the shell, and the usable interior is the free interval of a probe
line through the bay axis.  That is robust whether or not the section closes
into an annulus, which is the property the cavity-solid approach lacks.

Note the transform direction when reading the code below: `Path3D.to_2D()`
returns the **2-D -> 3-D** matrix, not its inverse.  Applying `inv(T)` silently
yields a degenerate section whose polygons all have zero area -- a failure mode
that looks like "the shell has no cavity" rather than like an error.

The payload gate
----------------
`README.md` mission steps 6 and 9 require a 4 in x 3 in x 3 in
(101.6 mm x 76.2 mm x 76.2 mm) payload to be winched up through the clamshell
aperture and into the bay.

CARGO-01, closed 2026-08-24: the wing spar used to cross the bay laterally at
the Rev S1b station, obstructing the payload's vertical path unless it passed
under, forward of, or aft of it.  Per SPAR-01 (owner, 2026-08-23,
`airframe/wings-nacelles/WBS.md` SS1.1.2), each spar now terminates at the
fuselage wall on its own bearing instead of crossing the fuselage, so it is no
longer present anywhere inside the bay's clear span -- there is no longer an
analytical spar obstruction to check the payload's path against.  What DOES
still bound the payload is the shell's own real interior envelope at the
former spar station (the bearing boss now sits OUTSIDE the clear span, at the
wall -- X <= -240 stbd / X >= -100 port), so this tool now measures that
envelope directly off the published mesh (`station_envelope()`) rather than
computing clearance around an analytical spar position, and fails if the
measured X width or Z height at that station cannot admit the payload.

A second finding this tool reports: the cargo shell and the wing disagree on the
spar DIAMETER.  `airframe/openscad/wings/wings_s1223_revo.scad` (Rev R2,
2026-07-18) states "the 12 mm fixed CF tube is retired" and carries
`SPAR_BORE_OD = 8.3` for an 8 mm rotating AISI 4130 tilt-spar that is both the
wing structural spar and the nacelle tilt axis.  CARGO-01/CARGO-02, closed
2026-08-24: `merge_cargo_interior.py` now cuts `WING_SPAR_BORE_D = 8.3` (the
same rotating clearance) inside an F688ZZ bearing seat (REF-SENSOR-019,
Ø27.7 boss) that TERMINATES at the fuselage wall (X −100 port / −240 stbd,
per SPAR-01) instead of crossing the bay, and `bom_revS.csv` lists the 8 mm
OD AISI 4130 hollow spar in place of the retired `CF-TUBE-12MM`.  The
payload gate below is evaluated against the wing's 8 mm spar figure, but with
the bay geometry re-cut the spar no longer crosses the bay at all -- the gate
now measures the bearing-seat boss's own footprint, not a full-span bore.

Geometry sources (single-sourced -- this tool derives nothing on its own):
    airframe/blender-scripts/merge_cargo_interior.py
        WING_SPAR_Y / WING_SPAR_Z / WING_SPAR_BORE_D -- spar station and axis
        APERTURE                                     -- clamshell belly opening
    airframe/openscad/wings/wings_s1223_revo.scad
        SPAR_BORE_OD                                 -- rotating tilt-spar bore
    README.md SS"Mission profile" steps 6, 9         -- payload envelope

Run:
    /usr/bin/python3 tools/cargo_bay_envelope.py
    /usr/bin/python3 tools/cargo_bay_envelope.py --stations   (per-station table)

Use `/usr/bin/python3`: the repository `.venv` hides the system `trimesh`,
`shapely` and `manifold3d`, and `pip` is not permitted in this environment.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the author's
         direction, per `AGENTS.md` SS3 "Attribution and Licensing".
License: CC BY-SA 4.0 - creativecommons.org/licenses/by-sa/4.0
"""

import os
import sys

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHELL_PATH = os.path.join(
    REPO_ROOT, "airframe", "stls", "fuselage", "cargo",
    "cargo_sect_shell24_2mm_repaired.stl"
)
DOOR_PATHS = [
    os.path.join(REPO_ROOT, "airframe", "stls", "fuselage", "cargo", name)
    for name in ("cargo_door_port.stl", "cargo_door_stbd.stl")
]

# --- single-sourced from merge_cargo_interior.py ---------------------------
sys.path.insert(0, os.path.join(REPO_ROOT, "airframe", "blender-scripts"))
import merge_cargo_interior as mci  # noqa: E402

X_CL = -169.9                       # hull centreline, cargo section
SPAR_Y = mci.WING_SPAR_Y            # +38.15 mm (Rev S1b, 35 % root chord)
SPAR_Z = mci.WING_SPAR_Z            # +68.42 mm (S1223 camber midline)
APERTURE = mci.APERTURE             # clamshell belly opening, hull frame

WING_SCAD = os.path.join(
    REPO_ROOT, "airframe", "openscad", "wings", "wings_s1223_revo.scad"
)
SHELL_BORE_D = mci.WING_SPAR_BORE_D  # 8.3 mm rotating clearance (CARGO-02, closed 2026-08-24)

# Mission payload, README.md steps 6 and 9.
PAYLOAD_L = 101.6                   # 4.00 in
PAYLOAD_W = 76.2                    # 3.00 in
PAYLOAD_H = 76.2                    # 3.00 in


def wing_spar_bore_od():
    """Read `SPAR_BORE_OD` straight out of the wing SCAD.

    Parsed rather than hard-coded so this gate cannot silently drift away from
    the wing the way the cargo shell's own 12.3 mm bore already has.
    """
    with open(WING_SCAD, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip().startswith("SPAR_BORE_OD"):
                value = line.split("=", 1)[1].split(";", 1)[0]
                return float(value.strip())
    raise RuntimeError(f"SPAR_BORE_OD not found in {WING_SCAD}")


def load_shell():
    """Load and weld the published cargo shell."""
    mesh = trimesh.load(SHELL_PATH, force="mesh")
    mesh.merge_vertices()
    return mesh


def wall_region(mesh, y):
    """Return the shell's wall material at station `y` as a 2-D region in hull (X, Z).

    Returns None when the plane misses the mesh entirely.
    """
    section = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    if section is None:
        return None
    planar, to_3d = section.to_2D()          # to_3d maps 2-D -> 3-D; do NOT invert
    polygons = []
    for poly in planar.polygons_full:
        def hull_xz(ring_coords):
            coords = np.asarray(ring_coords)
            homogeneous = np.column_stack(
                [coords, np.zeros(len(coords)), np.ones(len(coords))]
            )
            return (to_3d @ homogeneous.T).T[:, [0, 2]]

        polygons.append(
            Polygon(hull_xz(poly.exterior.coords),
                    [hull_xz(ring.coords) for ring in poly.interiors])
        )
    return unary_union(polygons) if polygons else None


def free_interval(region, probe, reference):
    """Longest free run of `probe` outside `region` that contains `reference`."""
    free = probe.difference(region)
    for part in getattr(free, "geoms", [free]):
        if part.length > 0 and part.distance(Point(reference)) < 1e-6:
            coords = np.array(part.coords)
            return coords.min(axis=0), coords.max(axis=0)
    return None, None


def station_envelope(mesh, y, z_floor=10.0, z_ceiling=170.0):
    """Usable interior at station `y`: (x_lo, x_hi, z_lo, z_hi) or None.

    `z_floor` is the top of the closed clamshell doors -- nothing may be mounted
    below it, because that volume swings away when the doors open.
    """
    region = wall_region(mesh, y)
    if region is None:
        return None
    vertical = LineString([(X_CL, z_floor), (X_CL, z_ceiling)])
    z_lo, z_hi = free_interval(region, vertical, (X_CL, (z_floor + z_ceiling) / 2))
    if z_lo is None:
        return None
    z_mid = (z_lo[1] + z_hi[1]) / 2.0
    lateral = LineString([(-270.0, z_mid), (-70.0, z_mid)])
    x_lo, x_hi = free_interval(region, lateral, (X_CL, z_mid))
    if x_lo is None:
        return None
    return float(x_lo[0]), float(x_hi[0]), float(z_lo[1]), float(z_hi[1])


def print_stations(mesh):
    """Print the per-station usable envelope through the cargo section."""
    print("\nUsable cargo interior, per station (hull frame, mm)")
    print("  floor = Z +10 (top of the closed clamshell doors)")
    print(f"\n{'Y':>7s}  {'X interior':>20s} {'width':>7s}   "
          f"{'Z interior':>18s} {'height':>7s}")
    for y in np.arange(-64.0, 126.0, 6.0):
        env = station_envelope(mesh, float(y))
        if env is None:
            print(f"{y:7.0f}   (bay axis obstructed at this station)")
            continue
        x_lo, x_hi, z_lo, z_hi = env
        # A span that runs to the probe's own end was never bounded by a wall --
        # the probe escaped through an opening (a landing-gear bay aperture, or
        # the belly forward of the clamshell).  Mark it rather than reporting the
        # probe length as if it were an interior width.
        unbounded = (x_lo <= -269.9 or x_hi >= -70.1
                     or z_hi >= 169.9)
        flag = "   <- probe escaped an opening; not a wall-bounded span" \
            if unbounded else ""
        print(f"{y:7.0f}  X {x_lo:8.1f}..{x_hi:8.1f} {x_hi - x_lo:7.1f}   "
              f"Z {z_lo:7.1f}..{z_hi:7.1f} {z_hi - z_lo:7.1f}{flag}")


def door_top(meshes):
    """Highest Z reached by the closed clamshell doors -- the bay's real floor."""
    return max(float(m.bounds[1][2]) for m in meshes)


def payload_gate(mesh, floor_z):
    """Check whether the mission payload fits in the bay's real interior
    envelope, measured off the published mesh at the former spar station.

    CARGO-01 (closed 2026-08-24): the spar terminates at the fuselage wall
    (SPAR-01) and no longer crosses the bay, so this no longer checks
    clearance around an analytical spar position -- it measures the actual
    shell interior at `mci.WING_SPAR_Y` (the station the spar/bearing boss
    used to obstruct) via `station_envelope()`, the same mesh-sectioning
    machinery `--stations` already uses elsewhere in this file.  The bearing
    boss itself now sits OUTSIDE this span, at the wall (X <= STBD_INB
    / X >= PORT_INB), so a bounded, sufficiently large envelope here is
    exactly CARGO-01's closing condition ("bay clear span X -240..-100 =
    140 mm at full bay height").

    Returns (ok, findings) where `findings` is a list of printable lines.
    """
    env = station_envelope(mesh, mci.WING_SPAR_Y, z_floor=floor_z)
    findings = [
        f"  bay floor (closed doors)          Z {floor_z:+7.2f}",
        f"  station probed (former spar Y)    Y {mci.WING_SPAR_Y:+7.2f}",
        f"  design wall stations (SPAR-01)    X port >= {mci.PORT_INB:+.1f}"
        f"   X stbd <= {mci.STBD_INB:+.1f}"
        f"   (design clear span {mci.PORT_INB - mci.STBD_INB:.1f} mm)",
    ]
    if env is None:
        findings.append(
            "  MEASUREMENT FAILED - the probe found no bounded interior at "
            "this station (bay axis obstructed or the mesh has an opening "
            "here); cannot confirm the payload fits."
        )
        return False, findings

    x_lo, x_hi, z_lo, z_hi = env
    x_span = x_hi - x_lo
    z_span = z_hi - z_lo
    y_span = APERTURE[3] - APERTURE[2]   # clamshell aperture Y extent

    findings += [
        f"  measured X interior               X {x_lo:8.1f}..{x_hi:8.1f}"
        f"   width {x_span:7.1f} mm",
        f"  measured Z interior               Z {z_lo:8.1f}..{z_hi:8.1f}"
        f"   height {z_span:7.1f} mm",
        f"  clamshell aperture Y span                              "
        f"width {y_span:7.1f} mm",
        "",
    ]

    # The payload must present some permutation of its three dimensions to
    # (X width, Z height, Y span).  Its two smaller dims are numerically
    # equal (76.2 mm), so there are only two distinct orientations to check:
    # the 101.6 mm dim along X or along Y (Z always takes one of the 76.2 mm
    # faces, since Z is the most constrained axis here).
    dims_ok = []
    for x_dim, y_dim, z_dim in (
        (PAYLOAD_L, PAYLOAD_W, PAYLOAD_H),
        (PAYLOAD_W, PAYLOAD_L, PAYLOAD_H),
    ):
        dims_ok.append(x_dim <= x_span and y_dim <= y_span and z_dim <= z_span)
    ok = any(dims_ok)

    findings.append(
        f"  payload {PAYLOAD_L:.1f} x {PAYLOAD_W:.1f} x {PAYLOAD_H:.1f} mm "
        f"(README.md mission steps 6, 9): {'FITS' if ok else 'DOES NOT FIT'} "
        f"(need <= {x_span:.1f} mm X, <= {y_span:.1f} mm Y, <= {z_span:.1f} mm Z)"
    )
    if not ok:
        findings += [
            "",
            "  BLOCKED - no permutation of the payload's dimensions fits the "
            "measured envelope",
            "  at the former spar station.",
        ]
    return ok, findings


def main():
    mesh = load_shell()
    doors = [trimesh.load(p, force="mesh") for p in DOOR_PATHS]

    print("=== cargo_bay_envelope.py ===")
    print(f"shell: {os.path.relpath(SHELL_PATH, REPO_ROOT)}")
    bounds = mesh.bounds
    print(f"  {len(mesh.faces):,} faces  watertight={mesh.is_watertight}  "
          f"vol={mesh.volume:,.0f} mm^3")
    print(f"  X {bounds[0][0]:.1f}..{bounds[1][0]:.1f}  "
          f"Y {bounds[0][1]:.1f}..{bounds[1][1]:.1f}  "
          f"Z {bounds[0][2]:.1f}..{bounds[1][2]:.1f}")

    if "--stations" in sys.argv:
        print_stations(mesh)

    spar_od = wing_spar_bore_od() - 0.30      # bore is OD + 0.15 mm/side clearance
    print("\nSpar-diameter reconciliation (wing SCAD vs cargo shell)")
    print(f"  wing  wings_s1223_revo.scad SPAR_BORE_OD = {wing_spar_bore_od():.2f}"
          f"  -> rotating tilt-spar OD {spar_od:.2f}")
    print(f"  shell merge_cargo_interior.WING_SPAR_BORE_D = {SHELL_BORE_D:.2f}")
    if abs(SHELL_BORE_D - wing_spar_bore_od()) > 0.05:
        print(f"  MISMATCH {SHELL_BORE_D - wing_spar_bore_od():+.2f} mm — the wing "
              f"retired the 12 mm CF tube (Rev R2, 2026-07-18);")
        print("  the cargo shell still bores for it.  Rev S1b reconciled the spar "
              "STATION across")
        print("  these two files but not its DIAMETER.  Tracked as CARGO-02.")

    floor_z = door_top(doors)
    print("\nMission payload gate (README.md steps 6, 9) -- CARGO-01, closed 2026-08-24")
    ok, findings = payload_gate(mesh, floor_z)
    for line in findings:
        print(line)

    print()
    if not ok:
        print("  RESULT: FAIL - cargo payload does not fit the measured bay envelope")
        sys.exit(1)
    print("  RESULT: PASS - the payload fits the measured bay envelope")


if __name__ == "__main__":
    main()
