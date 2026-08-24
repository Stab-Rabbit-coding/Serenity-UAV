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
aperture and into the bay.  The wing spar crosses the bay laterally at the
Rev S1b station, so the payload's vertical path is obstructed unless it can
pass either under the spar or entirely forward/aft of it.  This tool measures
all three clearances and fails if none admits the payload.

A second finding this tool reports: the cargo shell and the wing disagree on the
spar DIAMETER.  `airframe/openscad/wings/wings_s1223_revo.scad` (Rev R2,
2026-07-18) states "the 12 mm fixed CF tube is retired" and carries
`SPAR_BORE_OD = 8.3` for an 8 mm rotating AISI 4130 tilt-spar that is both the
wing structural spar and the nacelle tilt axis.  `merge_cargo_interior.py` still
cuts `WING_SPAR_BORE_D = 12.3` with Ø22 bearing bosses, and `bom_revS.csv` still
lists `CF-TUBE-12MM`.  Rev S1b reconciled the spar STATION across those two
files but not its diameter, so the same class of defect remains open.  The
payload gate below is evaluated against the wing's 8 mm spar, which is the
larger clearance of the two and therefore the generous case.

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
SHELL_BORE_D = mci.WING_SPAR_BORE_D  # 12.3 mm, as the cargo shell still cuts it

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


def payload_gate(floor_z, spar_od):
    """Check every path the mission payload could take into the bay.

    `spar_od` is the wing's rotating tilt-spar outside diameter -- the generous
    case, since the cargo shell's stale bore is wider still.

    Returns (ok, findings) where `findings` is a list of printable lines.
    """
    spar_under = SPAR_Z - spar_od / 2.0
    spar_fwd = SPAR_Y - spar_od / 2.0
    spar_aft = SPAR_Y + spar_od / 2.0

    under_h = spar_under - floor_z
    fwd_span = spar_fwd - APERTURE[2]
    aft_span = APERTURE[3] - spar_aft

    # The payload may present either 76.2 mm face to the spar, but never less.
    smallest = min(PAYLOAD_W, PAYLOAD_H)

    findings = [
        f"  bay floor (closed doors)      Z {floor_z:+7.2f}",
        f"  wing spar axis                Y {SPAR_Y:+7.2f}   Z {SPAR_Z:+7.2f}"
        f"   spar OD {spar_od:.1f} (wing SCAD)",
        f"  spar underside                Z {spar_under:+7.2f}",
        "",
        f"  path 1 - under the spar       {under_h:6.1f} mm clear "
        f"({under_h / 25.4:.2f} in)   need {smallest:.1f} mm",
        f"  path 2 - forward of the spar  {fwd_span:6.1f} mm clear "
        f"({fwd_span / 25.4:.2f} in)   need {smallest:.1f} mm",
        f"  path 3 - aft of the spar      {aft_span:6.1f} mm clear "
        f"({aft_span / 25.4:.2f} in)   need {smallest:.1f} mm",
    ]
    ok = max(under_h, fwd_span, aft_span) >= smallest
    if not ok:
        shortfall = smallest - max(under_h, fwd_span, aft_span)
        findings += [
            "",
            f"  BLOCKED - best path is {shortfall:.1f} mm short.  The "
            f"{PAYLOAD_L:.1f} x {PAYLOAD_W:.1f} x {PAYLOAD_H:.1f} mm payload",
            "  (README.md mission steps 6 and 9) cannot be winched into the bay",
            "  past the wing spar in any orientation.",
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
    print("\nMission payload gate (README.md steps 6, 9)")
    ok, findings = payload_gate(floor_z, spar_od)
    for line in findings:
        print(line)

    print()
    if not ok:
        print("  RESULT: FAIL - cargo payload path obstructed by the wing spar")
        sys.exit(1)
    print("  RESULT: PASS - the payload has a clear path into the bay")


if __name__ == "__main__":
    main()
