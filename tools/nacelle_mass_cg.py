#!/usr/bin/env python3
"""
nacelle_mass_cg.py — rotating-assembly mass and CG for one Serenity nacelle.

WHY THIS EXISTS
---------------
`PIVOT_Z` in `airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad` is not a
chosen number: the repo's standing decision (plan 003 KTD7) is that the tilt
pivot sits at the CG of everything that tilts, so that gravity produces no
tilt-servo torque.  That makes `PIVOT_Z` an OUTPUT of a mass roll-up, and until
now the roll-up lived only as a hand-maintained comment table in the SCAD
header.  Three separate revisions re-derived it by hand (103.75 -> 104.5 ->
111.5) and the table's printed-part masses were estimates, not measurements.

This tool replaces that table.  Every printed part is measured FROM ITS OWN STL
at the repo's bulk printed density; COTS items carry a cited mass and a source.
Running it is how `PIVOT_Z` is set, and re-running it is how a geometry change
is checked against the pivot it assumed.

WHAT CHANGED AT REV T4 (2026-08-30)
-----------------------------------
1. The rotating Ø8 mm steel tilt spar (19.2 g) and its crank (1.4 g) are GONE —
   the spar is fixed to the wing and stops outside the duct.  Both sat ON the
   pivot, so they barely moved the CG, but they were 5.2 % of the rotating mass.
2. The trunnion, its bearing pair and the ring magnet are ADDED, also on the
   pivot.
3. ESC1 relocates aft alongside ESC2 (plan 003 KTD8, session-settled,
   user-directed).  This is the only item that moves the CG appreciably.
4. The pod shell is MEASURED, not estimated.  The header table carried 130 g for
   "shell + stator + aft sleeve + cowl skin"; the three meshes measure far more.
   That correction dominates everything else in this tool.

DENSITY
-------
RHO_PRINT is the repo's calibrated BULK printed density (see
`docs/MASS_AUDIT_CARGO_WING_ROOT.md` §5 and `merge_cargo_interior.py`).  Do NOT
re-derive it as solid density x infill: below ~6 mm of thickness a printed part
is nearly all perimeter and infill barely moves the mass.  That mistake halved a
BOM row once already.

Usage:
    /usr/bin/python3 tools/nacelle_mass_cg.py [--json]

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
Analysis and tool by Claude (Claude Opus 5, Anthropic) under the author's
direction, per AGENTS.md §3 "Attribution and Licensing".
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import trimesh
except ImportError:  # pragma: no cover - environment guard
    print("Missing dependency 'trimesh'. Install requirements-dev.txt first.")
    raise

REPO = Path(__file__).resolve().parent.parent

#: Calibrated bulk density of a printed CF-PETG part, g/mm^3.
RHO_PRINT = 1.05e-3
#: NdFeB sintered magnet, g/mm^3 (K&J Magnetics material data, N42).
RHO_NDFEB = 7.5e-3

#: Printed parts, each with the frame its published STL is stored in.
#:
#: This has to be explicit.  An earlier draft guessed the duct axis as the mesh's
#: longest bounding-box extent, which is wrong three different ways here: the pod
#: is BAKED to hull frame (its longest extent is hull Y), and both sleeves and the
#: trunnion are wider than they are long, so the guess picked a radial axis and
#: returned half the diameter as a station.  Frames:
#:
#:   ("hull", component)  the STL is baked; invert tools/bake_hull_frame.py's own
#:                        recorded placement to recover nacelle-local coordinates
#:   ("local", z0)        part-local with the duct axis on +Z; add z0 to reach the
#:                        nacelle-local station
PRINTED = [
    ("Pod shell (measured)", "airframe/stls/nacelles/nacelle_port_revs.stl",
     ("hull", "Nacelle_Port")),
    ("Stator sleeve", "airframe/stls/nacelles/edf_stator_sleeve.stl",
     ("local", 90.0)),      # STATOR_SLV_Z_START
    ("Aft spider sleeve", "airframe/stls/nacelles/edf_aft_spider_sleeve.stl",
     ("local", 122.5)),     # AFT_SLV_Z_START
]

#: Everything the meshes cannot supply: (label, mass g, CG_Z mm, source note).
#: CG_Z is nacelle-local, measured from the intake face along the duct axis.
FIXED = [
    ("EDF1 (upstream)", 70.0, 59.4,
     "Xfly Galaxy X5 50 mm 6S, REFERENCES.md REF-EDF-001"),
    ("EDF2 (downstream)", 70.0, 150.6,
     "Xfly Galaxy X5 50 mm 6S, REFERENCES.md REF-EDF-001"),
    ("ESC1 (relocated aft)", 25.0, 150.6,
     "plan 003 KTD8 — session-settled, user-directed; was 59.4"),
    ("ESC2", 25.0, 150.6, "Open-Secure-ESC 6S/50A board"),
    ("Nozzle throat + housing", 21.4, 174.8, "nacelle_nozzle_iris.scad Rev T"),
    ("Unison ring (cam-only)", 6.7, 169.9, "nacelle_nozzle_iris.scad Rev T"),
    ("8 x nozzle flap (40 mm)", 21.1, 198.2,
     "PETG; plan 005 R1 proposes 30 mm — see --flap30"),
    ("Pushrod (COTS + links)", 3.6, 140.8, "nacelle_nozzle_pushrod.scad"),
]

#: In-nacelle HARNESS.  Added 2026-08-31 — it was missing from every previous
#: version of this roll-up, including the hand-maintained table in the SCAD
#: header that three revisions of `PIVOT_Z` were derived from.  It is not a
#: rounding item: 10 AWG silicone is heavy, and all of it lives AFT of the pivot,
#: so omitting it biased the CG FORWARD and made the hover-clearance picture look
#: worse than it is.
#:
#: Masses are derived from this repo's own BOM rows rather than from a datasheet,
#: because `WING_ATTACH_INTERFACE.md` OI-1 records that `WIRE-10AWG` has no
#: published OD or linear density. Linear densities back-computed from the rows:
#:   WIRE-10AWG      80 g / 2 m  = 40.0 g/m   (row: "red/black 1 m each")
#:   WIRE-16AWG      40 g / 3 m  = 13.3 g/m   (row: "3 m assorted")
#:   WIRE-28AWG-NAC   8 g / 1 m  =  8.0 g/m
#:   WIRE-28AWG-STP  20 g / 5 m  =  4.0 g/m
#: Run lengths are geometric, from the station each cable connects between plus a
#: service loop; they are FIRST-PASS and should be replaced by measured harness
#: lengths at first article.
HARNESS = [
    ("4 x 10 AWG feed, trunnion->ESCs", 4 * 0.080 * 40.0, 132.0,
     "trunnion Z 105.8 -> ESC Z 150.6, + service loop at the rotating joint"),
    ("6 x 16 AWG EDF phase leads", 6 * 0.100 * 13.3, 150.0,
     "2 ESCs x 3 phases, ESC to motor"),
    ("Signal + gateway pairs, 28 AWG STP", 0.30 * 4.0, 120.0,
     "ESC telemetry + CAN-FD/RS-485 to the wing interface pocket"),
    ("Nav 3-core, 28 AWG", 0.11 * 8.0, 88.0,
     "trunnion crossing -> nav light at Z 70"),
]

#: Items that sit ON the tilt axis.  Their CG_Z is PIVOT_Z by construction, so
#: they are resolved after the first pass rather than carrying a fixed station.
ON_AXIS = [
    ("Trunnion (Rev T4, printed)", 7.9,
     "nacelle_trunnion.stl measured; its axis IS the tilt axis"),
    ("2 x 6704ZZ trunnion bearing", 2 * 4.9,
     "20x27x4 steel deep-groove; volume x 7.85 g/cm3 x 0.6 fill"),
    ("Ring magnet ID26/OD41.2x2.0", 1604.0 * RHO_NDFEB,
     ("NdFeB N42 diametric, WA-R9; thinned 2.5->2.0 when the stub lost 1.5 mm "
      "to the sleeve bound — flux re-validation is now load-bearing")),
    ("3 x M3 brass screw + inserts", 2.4, "non-ferrous, EMI keep-out"),
]

#: Hover ground clearance — the reason `PIVOT_Z` is not just bookkeeping.
#:
#: In hover the duct axis is vertical and the nozzle swings DOWN, so the
#: governing dimension is the pivot-to-nozzle-tip arm.  Moving the pivot FORWARD
#: (smaller `PIVOT_Z`) lengthens that arm one-for-one and drops the tip.
#:
#: The model reproduces plan 003's published row EXACTLY when fed the spar height
#: that row used: at `PIVOT_Z` 111.5 the arm is 109.8 mm and, with the then-current
#: `SPAR_Z` = 68.42, the tip lands at hull Z −41.38 against its −41.39.  So the
#: arithmetic is the same arithmetic the clearance decisions were made with.
#:
#: What has changed underneath it is the spar: Rev T1c BUILT the socket at
#: **66.851**, 1.57 mm lower than the 68.42 that table assumed.  That 1.57 mm is
#: spent, not recoverable, and it comes off the clearance before `PIVOT_Z` is even
#: considered.
ROT_ASSY_TIP_Z = 221.3   # [mm] nacelle-local reach of the rotating assembly AT
                         #      THE BUILT 40 mm FLAP (iris seats at
                         #      NOZZLE_RING_Z 166.25, its STL runs to +55.1) —
                         #      measured, plan 003 R12.  Trimming the flap moves
                         #      this one-for-one; see `tip_reach()`.
BUILT_FLAP_LEN = 40.0    # [mm] the flap length ROT_ASSY_TIP_Z was measured at


def tip_reach(flap_len: float) -> float:
    """Rotating-assembly reach for a given flap length.

    The flap hangs aft of a fixed hinge line, so shortening it shortens the reach
    by the same amount.  This is the whole of plan 005 R1's clearance argument and
    it must not be left out of `--flap`: an earlier version of this tool applied
    the flap trim to the flap's MASS and CG only, which made a 30 mm flap look
    WORSE than a 40 mm one — the mass moves forward, and without the matching
    reach change that reads as a clearance loss instead of a 10 mm gain.
    """
    return ROT_ASSY_TIP_Z - (BUILT_FLAP_LEN - flap_len)
WING_SPAR_HULL_Z = 66.851  # [mm] built spar height (merge_cargo_interior.py
                           #      WING_SPAR_Z, Rev T1c station 28)
GROUND_PLANES = {"1.5 in gear (ACTIVE default)": -38.1,
                 "3.0 in gear (kept, not wired in)": -80.0}

#: Deleted at Rev T4, kept so the delta is legible rather than implied.
DELETED = [
    ("Rotating Ø8 tilt-spar span", 19.2, 111.5, "spar is now fixed to the wing"),
    ("Spar crank", 1.4, 111.5, "nozzle drive re-datums to the fixed trunnion"),
]


def measure(rel: str, frame: tuple) -> tuple[float, float]:
    """Return (mass_g, nacelle-local CG_Z mm) for a printed STL.

    Raises with a reason rather than guessing, because a wrong station here
    silently moves `PIVOT_Z`, and `PIVOT_Z` is cut into two parts.
    """
    path = REPO / rel
    if not path.exists():
        raise FileNotFoundError(
            f"{rel} is not published yet — render it before trusting this roll-up"
        )
    mesh = trimesh.load_mesh(path, force="mesh")
    if mesh.is_empty:
        raise ValueError(f"{rel} loaded empty")

    kind = frame[0]
    if kind == "local":
        cg = float(mesh.center_mass[2]) + float(frame[1])
    elif kind == "hull":
        # Invert the placement tools/bake_hull_frame.py recorded for this
        # component — reusing that table rather than restating the transform, so
        # the two can never drift apart.
        sys.path.insert(0, str(REPO / "tools"))
        import bake_hull_frame as bake

        _, placement = bake.COMPONENTS[frame[1]]
        px, py, pz, qx, qy, qz, qw = placement
        rot = bake.quat_to_matrix(qx, qy, qz, qw)
        local = rot.T @ (mesh.center_mass - [px, py, pz])
        cg = float(local[2])
    else:  # pragma: no cover - guarded by the table above
        raise ValueError(f"unknown frame kind {kind!r}")
    return float(mesh.volume * RHO_PRINT), cg


def roll_up(flap_len: float = 40.0) -> dict:
    """Compute total mass and CG, iterating the on-axis items to a fixed point."""
    rows: list[tuple[str, float, float, str]] = []
    problems: list[str] = []

    for label, rel, frame in PRINTED:
        try:
            mass, cg = measure(rel, frame)
        except (FileNotFoundError, ValueError, KeyError) as exc:
            problems.append(f"{rel}: {exc}")
            continue
        rows.append((label, mass, cg, rel))

    for label, mass, cg, note in FIXED + HARNESS:
        if label.startswith("8 x nozzle flap") and flap_len != 40.0:
            # Flap mass scales with length; its CG moves forward by half the
            # trim, because the flap hangs aft of a fixed hinge line.
            scale = flap_len / BUILT_FLAP_LEN
            mass = mass * scale
            cg = cg - (BUILT_FLAP_LEN - flap_len) / 2.0
            note = f"trimmed to {flap_len:.0f} mm (plan 005 R1)"
            label = f"8 x nozzle flap ({flap_len:.0f} mm)"
        rows.append((label, mass, cg, note))

    on_axis_mass = sum(m for _, m, _ in ON_AXIS)

    # Fixed-point iteration: on-axis items sit at the CG, so adding them cannot
    # move it — but they do change the total.  Two passes are provably enough
    # (the second is only a confirmation), and it is asserted rather than
    # assumed.
    off_mass = sum(r[1] for r in rows)
    off_moment = sum(r[1] * r[2] for r in rows)
    cg_z = off_moment / off_mass
    total = off_mass + on_axis_mass
    check = (off_moment + on_axis_mass * cg_z) / total
    assert abs(check - cg_z) < 1e-9, "on-axis items must not move the CG"

    return {
        "rows": rows,
        "on_axis": ON_AXIS,
        "on_axis_mass_g": on_axis_mass,
        "off_axis_mass_g": off_mass,
        "total_mass_g": total,
        "cg_z_mm": cg_z,
        "pivot_z_mm": round(cg_z, 1),
        "problems": problems,
        "flap_len_mm": flap_len,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--flap", type=float, default=40.0,
                    help="nozzle flap length in mm (plan 005 R1 proposes 30)")
    args = ap.parse_args()

    result = roll_up(args.flap)

    if args.json:
        print(json.dumps(
            {k: v for k, v in result.items() if k not in ("rows", "on_axis")}
            | {"rows": [list(r) for r in result["rows"]]},
            indent=2))
        return 2 if result["problems"] else 0

    print("Serenity nacelle — rotating-assembly mass and CG (Rev T4)")
    print(f"flap length {result['flap_len_mm']:.0f} mm\n")
    print(f"{'Item':<34}{'Mass g':>9}{'lbm':>8}{'CG_Z mm':>10}{'in':>7}"
          f"{'Moment':>11}")
    print("-" * 79)
    for label, mass, cg, _ in result["rows"]:
        print(f"{label:<34}{mass:9.1f}{mass/453.592:8.3f}{cg:10.1f}"
              f"{cg/25.4:7.2f}{mass*cg:11.0f}")
    print(f"{'-- on the tilt axis (CG by construction) --':<34}")
    for label, mass, note in result["on_axis"]:
        print(f"{label:<34}{mass:9.1f}{mass/453.592:8.3f}"
              f"{result['cg_z_mm']:10.1f}{result['cg_z_mm']/25.4:7.2f}"
              f"{mass*result['cg_z_mm']:11.0f}")
    print("-" * 79)
    tot = result["total_mass_g"]
    print(f"{'TOTAL':<34}{tot:9.1f}{tot/453.592:8.3f}"
          f"{result['cg_z_mm']:10.1f}{result['cg_z_mm']/25.4:7.2f}")
    print(f"\n=> PIVOT_Z = {result['pivot_z_mm']:.1f} mm "
          f"({result['pivot_z_mm']/25.4:.2f} in) from the intake face")
    # ---- fixed-point convergence against the SCAD ---------------------------
    # PIVOT_Z is self-referential: it is an input to the pod geometry and an
    # output of the pod's own measured CG.  So it is iterated, and the iteration
    # has to be declared converged somewhere.  0.25 mm is the bar, because that
    # is the scale at which the printed features this number places (the trunnion
    # collar and its Ø34 H7 register) have any meaning — FDM positional tolerance
    # on a 185 mm part is not better than ±0.2 mm.
    # Only meaningful for the AS-BUILT flap length: a `--flap` what-if deliberately
    # models geometry the SCAD does not have, so its CG is not supposed to match.
    pod_scad = (REPO / "airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad")
    m = re.search(r"^PIVOT_Z\s*=\s*([0-9.]+)\s*;", pod_scad.read_text(), re.MULTILINE)
    if m and result["flap_len_mm"] == BUILT_FLAP_LEN:
        built = float(m.group(1))
        delta = result["cg_z_mm"] - built
        state = "CONVERGED" if abs(delta) <= 0.25 else "NOT CONVERGED — re-render"
        print(f"\nFixed point: SCAD PIVOT_Z = {built:.1f}, measured CG = "
              f"{result['cg_z_mm']:.2f}, residual {delta:+.2f} mm -> {state}")
    elif m:
        print(f"\nFixed point not checked: --flap {result['flap_len_mm']:.0f} is a "
              f"what-if, and the SCAD is built at {BUILT_FLAP_LEN:.0f} mm.")

    # ---- hover ground clearance -------------------------------------------
    pivot = result["cg_z_mm"]
    arm = tip_reach(result["flap_len_mm"]) - pivot
    tip_hull_z = WING_SPAR_HULL_Z - arm
    print("\nHover ground clearance (nacelles vertical, worst case at 90 deg)")
    print(f"  rotating-assembly reach {tip_reach(result['flap_len_mm']):.1f} mm "
          f"local ({result['flap_len_mm']:.0f} mm flap), pivot {pivot:.1f}"
          f"  ->  arm {arm:.1f} mm")
    print(f"  spar at hull Z {WING_SPAR_HULL_Z:+.2f}  ->  nozzle tip at hull Z "
          f"{tip_hull_z:+.2f}")
    worst = None
    for name, ground in GROUND_PLANES.items():
        clr = tip_hull_z - ground
        verdict = "CLEARS" if clr > 0 else "*** STRIKES ***"
        print(f"    vs {name:<34} {clr:+7.2f} mm   {verdict}")
        if worst is None or clr < worst:
            worst = clr

    harness = sum(m for _, m, _, _ in HARNESS)
    print(f"\nIn-nacelle harness included above: {harness:.1f} g "
          f"({harness / 453.592:.3f} lbm), all of it AFT of the pivot. "
          f"First-pass lengths; see HARNESS in this file.")

    print("\nDeleted at Rev T4 (for the record):")
    for label, mass, cg, note in DELETED:
        print(f"  - {label:<32}{mass:6.1f} g @ {cg:.1f} mm   {note}")

    if result["problems"]:
        print("\nUNRESOLVED — this roll-up is INCOMPLETE:")
        for p in result["problems"]:
            print(f"  ! {p}")
        return 2
    if worst is not None and worst <= 0:
        print("\nGROUND CLEARANCE FAILS on at least one gear variant — see above.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
