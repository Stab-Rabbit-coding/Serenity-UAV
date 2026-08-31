#!/usr/bin/env python3
"""
nacelle_hollow_profile.py — generate the nacelle pod's internal cavity surface.

WHY THIS EXISTS
---------------
The nacelle pods were the heaviest printed parts on the aircraft — 285 g each —
for one reason: `nacelle_pod_50mm_tandem.scad` imports the SOLID canonical
Serenity nacelle shell and subtracts only the duct.  The four fuselage shells
were put through this repo's hollowing pipeline
(`blender_shells_2mm_solidify.py` -> `hollow_manifold.py`); the nacelle shells
never were.  So the "annular space between the duct wall and the outer skin"
that three planning documents route wiring through was solid CF-PETG.

That pipeline is not usable here.  It produces 40-66 MB voxel-remeshed meshes,
and the pod is an OpenSCAD part whose CGAL booleans already take ~4 minutes
against a 3.3 MB import.  So instead of offsetting the mesh, this tool MEASURES
the shell's true outer skin by ray-casting and emits the cavity as an explicit
`polyhedron()` — text, diffable, regenerable, and small enough that OpenSCAD can
still difference it.

WHY THE WALL IS NOT UNIFORM  (owner direction, 2026-08-31)
-----------------------------------------------------------
"Take more from the forward end instead of the aft end to adjust CG and nacelle
ground clearance."

The tilt pivot sits at the rotating assembly's CG, so removing mass FORWARD of
the CG moves the pivot AFT, which shortens the pivot-to-nozzle-tip arm one for
one and lifts the nozzle in hover.  With the pod solid, that tip sits 10.5 mm
BELOW the ground plane on the active 1.5 in gear.

Measured, the trade is:

    schedule                              saved/pod   PIVOT_Z   clearance
    solid (as built)                          0 g      105.9      -10.47
    uniform 2.5 mm                        180.1 g      113.7       -1.31
    fwd 2.5 -> aft 8.0, ramp Z 100-140    144.4 g      115.4       +0.18

The bias costs about 22 g per millimetre of clearance, which is a poor exchange
rate in isolation — but it is what carries the 1.5 in gear from STRIKES to
CLEARS on the flaps as built, and it restores roughly the owner-accepted +9.8 mm
margin once plan 005's 40 -> 30 mm flap trim lands (+9.00 mm).

The ramp also has a structural reason to be where it is, not just a mass one:
it thickens the wall across Z 100-140, which is exactly where the trunnion
collar (Z 105.8) feeds the tilt-joint moment into the pod, and where the EDF2
mount, the aft sleeve zone and the nozzle housing loads live.

MEASUREMENT NOTE — why ray-casting and not section radii
---------------------------------------------------------
An earlier pass sampled the skin as the minimum section-vertex radius per
azimuth bin.  That is wrong on this shell: the canonical mesh carries an
INTERNAL forward intake pocket, so sections at Z < ~58 return TWO loops and the
minimum picks the inner one.  It under-reported the outer skin by up to 25 mm
and hid roughly half the removable volume (96 g reported vs 180 g actual).  A
ray cast inward from outside the bounding box returns the outermost surface
unambiguously, which is the only thing a wall offset can be measured from.

Usage:
    /usr/bin/python3 tools/nacelle_hollow_profile.py            # trade table
    /usr/bin/python3 tools/nacelle_hollow_profile.py --emit     # write the .scad

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
Analysis and tool by Claude (Claude Opus 5, Anthropic) under the author's
direction, per AGENTS.md S3 "Attribution and Licensing".
License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

try:
    import trimesh
except ImportError:  # pragma: no cover - environment guard
    print("Missing dependency 'trimesh'. Install requirements-dev.txt first.")
    raise

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "airframe/openscad/nacelles/nacelle_hollow_profile.scad"

#: Bore-centring offsets, mirrored from nacelle_pod_50mm_tandem.scad.
SHELLS = {
    "PORT": ("eng_left_shell24_50mm_repaired.stl", 42.72),
    "STBD": ("eng_right_shell24_50mm_repaired.stl", 155.02),
}
BORE_CY = 190.79

#: Cavity sampling grid.  3 mm axially and 7.5 deg circumferentially: the wall
#: error a 7.5 deg chord introduces on a 40 mm radius is 0.09 mm, and the
#: sampling is conservative anyway (see `skin_grid`).
DZ = 3.0
N_AZ = 48
Z_START = 21.0    # forward end of the cavity - clear of the intake lip
Z_END = 163.0     # aft end - clear of the nozzle ring pocket at 166.25

#: Wall schedule (owner-directed forward bias).  Skin thickness in mm vs the
#: nacelle-local Z station.
WALL_FWD = 2.5    # 4 perimeters at a 0.6 mm nozzle - the repo minimum wall
WALL_AFT = 8.0
RAMP_Z0 = 100.0
RAMP_Z1 = 140.0

#: Inner bound of the cavity: the duct wall.  Mirrors the pod's own bore
#: schedule plus one minimum wall.
DUCT_WALL = 2.5
RHO_PRINT = 1.05e-3


def wall(z: float) -> float:
    """Skin thickness at station z — forward-biased, linearly ramped."""
    if z <= RAMP_Z0:
        return WALL_FWD
    if z >= RAMP_Z1:
        return WALL_AFT
    return WALL_FWD + (WALL_AFT - WALL_FWD) * (z - RAMP_Z0) / (RAMP_Z1 - RAMP_Z0)


def bore_r(z: float) -> float:
    """Duct radius at station z, including the cosine bell-mouth flare."""
    if z < 27.5:
        return 25.0 + 3.0 * (1.0 - z / 27.5)
    if z < 90.0:
        return 25.0
    return 27.7


def skin_grid(side: str, dz: float = DZ, n_az: int = N_AZ):
    """Ray-cast the outer skin radius on a (Z, azimuth) grid.

    Conservative by construction: each grid cell takes the MINIMUM outer radius
    over a 3x3 sub-sample of the cell, so the emitted cavity never sits closer
    to the skin than the wall schedule allows, even between samples.
    """
    name, cx = SHELLS[side]
    mesh = trimesh.load_mesh(REPO / "airframe/stls/nacelles" / name, force="mesh")
    mesh.apply_translation([-cx, BORE_CY, 0.0])

    zs = np.arange(Z_START, Z_END + dz / 2, dz)
    az = np.arange(n_az) * 360.0 / n_az
    sub_dz = [-dz / 3, 0.0, dz / 3]
    sub_da = [-360.0 / n_az / 3, 0.0, 360.0 / n_az / 3]

    origins, dirs = [], []
    for z in zs:
        for a in az:
            for ddz in sub_dz:
                for dda in sub_da:
                    t = np.radians(a + dda)
                    origins.append([200.0 * np.cos(t), 200.0 * np.sin(t), z + ddz])
                    dirs.append([-np.cos(t), -np.sin(t), 0.0])
    origins = np.asarray(origins)
    dirs = np.asarray(dirs)
    loc, ray_idx, _ = mesh.ray.intersects_location(origins, dirs, multiple_hits=True)

    outer = np.zeros(len(origins))
    radii = np.hypot(loc[:, 0], loc[:, 1])
    np.maximum.at(outer, ray_idx, radii)
    if (outer == 0).any():
        raise ValueError(f"{side}: {(outer == 0).sum()} rays missed the shell")
    outer = outer.reshape(len(zs), n_az, 9).min(axis=2)
    return zs, az, outer


#: Where the wall schedule leaves less than this much cavity, the ring is pushed
#: fully INSIDE the duct-wall solid instead of being clamped flush to it.  Clamping
#: flush produced coincident surfaces at the aft closure, which exported as four
#: sub-mm INVERTED bodies — the same class of defect as the old shaft-conduit void,
#: just smaller.  Burying the ring lets the duct-wall subtraction remove it cleanly.
MIN_CAVITY = 1.0


def cavity_radii(zs, outer):
    """Outer cavity radius per (Z, azimuth).

    Rings that would be thinner than MIN_CAVITY are moved inside the duct wall
    rather than clamped to it, so the boolean has nothing degenerate to resolve.
    """
    out = np.empty_like(outer)
    closed = False
    for k, z in enumerate(zs):
        inner = bore_r(float(z)) + DUCT_WALL
        r = outer[k] - wall(float(z))
        open_frac = float((r >= inner + MIN_CAVITY).mean())
        # Closure is MONOTONIC aft of the first mostly-closed station.  Letting
        # individual azimuths open and shut again makes the cavity surface graze
        # the duct-wall solid repeatedly, and CGAL resolves each near-tangency
        # into a sub-mm inverted sliver — one such body (-0.006 mm3 at local
        # Z 139, r 30.1, right at the end of the wall ramp) failed gate M1 before
        # this rule was added.  One clean crossing instead of many grazes.
        if closed or open_frac < 0.5:
            closed = True
            out[k] = inner - 4.0
        else:
            out[k] = np.where(r >= inner + MIN_CAVITY, r, inner - 4.0)
    return out


def mass_removed(zs, rc):
    """Mass and centroid of the material the cavity removes."""
    dz = float(zs[1] - zs[0])
    dth = 2 * np.pi / rc.shape[1]
    vol = mom = 0.0
    for k, z in enumerate(zs):
        inner = bore_r(float(z)) + DUCT_WALL
        a = float((0.5 * np.maximum(rc[k] ** 2 - inner ** 2, 0.0) * dth).sum())  # noqa: E501
        vol += a * dz
        mom += a * dz * float(z)
    return vol * RHO_PRINT, (mom / vol if vol else 0.0)


def emit(zs, az, grids) -> str:
    """Render the generated OpenSCAD source."""
    lines = [
        "// =============================================================================",
        "// nacelle_hollow_profile.scad — GENERATED FILE, DO NOT EDIT BY HAND",
        "// =============================================================================",
        "//",
        "// Regenerate with:  /usr/bin/python3 tools/nacelle_hollow_profile.py --emit",
        "//",
        "// The internal cavity surface of the nacelle pod, measured off the canonical",
        "// shell by ray-casting and offset inward by a FORWARD-BIASED wall schedule:",
        f"//     wall = {WALL_FWD} mm for Z <= {RAMP_Z0:.0f}, ramping to {WALL_AFT} mm by "
        f"Z {RAMP_Z1:.0f}",
        "// Removing more from the forward end moves the rotating-assembly CG AFT, which",
        "// is where the tilt pivot sits, which shortens the pivot-to-nozzle arm and",
        "// lifts the nozzle in hover.  See the tool's header for the measured trade.",
        "//",
        "// This file supplies ONLY the outer cavity surface as a ring grid.  The duct",
        "// wall, the structural ribs and the trunnion keep-out are subtracted in",
        "// nacelle_pod_50mm_tandem.scad, so the pod's own bore parameters stay",
        "// authoritative and none of them is restated here.",
        "//",
        "// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP",
        "// Generated by Claude (Claude Opus 5, Anthropic) under the author's direction,",
        "// per AGENTS.md S3 'Attribution and Licensing'.",
        "// License: CC BY 4.0 - creativecommons.org/licenses/by/4.0",
        "// =============================================================================",
        "",
        f"HOLLOW_N_AZ = {len(az)};",
        f"HOLLOW_Z_START = {zs[0]:.2f};",
        f"HOLLOW_Z_END   = {zs[-1]:.2f};",
        "HOLLOW_Z = [" + ", ".join(f"{z:.2f}" for z in zs) + "];",
    ]
    for side, rc in grids.items():
        lines.append(f"HOLLOW_R_{side} = [")
        for row in rc:
            lines.append("  [" + ",".join(f"{v:.2f}" for v in row) + "],")
        lines.append("];")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--emit", action="store_true",
                    help="write airframe/openscad/nacelles/nacelle_hollow_profile.scad")
    args = ap.parse_args()

    grids = {}
    report = {}
    for side in SHELLS:
        zs, az, outer = skin_grid(side)
        rc = cavity_radii(zs, outer)
        grids[side] = rc
        report[side] = mass_removed(zs, rc)

    print("Nacelle pod hollowing — forward-biased wall schedule")
    print(f"  wall {WALL_FWD} mm to Z {RAMP_Z0:.0f}, ramping to {WALL_AFT} mm "
          f"by Z {RAMP_Z1:.0f}; duct wall {DUCT_WALL} mm")
    print(f"  cavity Z {Z_START:.0f}..{Z_END:.0f}, grid {len(zs)} x {N_AZ}\n")
    print(f"  {'side':<6}{'removed g':>11}{'centroid Z':>13}{'pod after g':>14}")
    for side, (m, c) in report.items():
        print(f"  {side:<6}{m:11.1f}{c:13.1f}{285.0 - m:14.1f}")
    pair = sum(m for m, _ in report.values())
    print(f"\n  pair saving {pair:.1f} g")

    if args.emit:
        OUT.write_text(emit(zs, az, grids), encoding="utf-8")
        print(f"\n  wrote {OUT.relative_to(REPO)} "
              f"({OUT.stat().st_size / 1024:.0f} KB)")
    else:
        print("\n  (dry run — pass --emit to write the .scad)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
