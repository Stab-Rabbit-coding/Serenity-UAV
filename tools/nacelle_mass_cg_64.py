#!/usr/bin/env python3
"""
nacelle_mass_cg_64.py — rotating-assembly mass, CG and PIVOT_Z for the 64 mm
QX-Motor tandem nacelle (plan 2026-09-28-001 U5; WBS NAC-64-GEOM-05).

WHY A SEPARATE TOOL
-------------------
tools/nacelle_mass_cg.py is the authority for the 50 mm pod and stays so.  The
64 mm pod is a parameter override of the same SCAD
(airframe/openscad/nacelles/nacelle_pod_64mm_tandem.scad), so this tool reuses
that tool's measuring function, density, on-axis items and clearance model,
and replaces only the rows the 64 mm stack changes.  The tilt pivot sits at
the CG of everything that tilts (plan 003 KTD7), so PIVOT_Z is an OUTPUT here.

ROW PROVENANCE — every row is one of:
  MEASURED  a printed part measured from its own STL at RHO_PRINT;
  SHEET     a manufacturer figure [REF-EDF-003];
  SCALED    a measured 50 mm part scaled to the 64 mm geometry, est.;
  ASSUMED   no source exists yet — stated basis and a VERIFY flag.
No row is TBD (AGENTS.md engineering requirements).

STATIONS (nacelle-local Z from the intake face, mm) mirror
nacelle_pod_64mm_tandem.scad: proportion-trade pick (radial 1.21, axial
1.13, L 209.3), elliptical lip + straight duct, rotor-1 hub 30.5-41.2,
motor 1 45.2-103.2, rotor-2 hub 104.2-114.9, motor 2 118.9-176.9, nozzle
pocket 187.86.

Usage:
    /usr/bin/python3 tools/nacelle_mass_cg_64.py --pod-stl PATH [--json]

--pod-stl is the rendered 64 mm pod (nacelle-local frame, not hull-baked).
Exit 0 = rolled up and the 3.0 in gear clears in hover.

References (REFERENCES.md): [REF-EDF-003] QF2822 motor mass 135 g.

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding) —
owner direction to recompute CG and re-site the pivot trunnion (2026-10-03).
Tool and analysis by Claude (Claude Opus 5.5, Anthropic) under the author's
direction, per AGENTS.md AI attribution.  Derivative of nacelle_mass_cg.py.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nacelle_mass_cg as base  # noqa: E402 sibling tool; path set above

import nacelle_64_scale  # noqa: E402  single-source shell scale (x1.06 on 2026-10-05)
K = nacelle_64_scale.get("P64_K")    # radial scale
A = nacelle_64_scale.get("P64_A")    # axial scale
ROTOR_Z = 30.5           # rotor-1 hub face, behind the elliptical lip + duct
STAGE = 72.7             # shaft 10.7 + gap 1 + plate 3 + body 58.0
NOZ_Z = 166.25 * A       # nozzle pocket rides on the stretched shell
LBM_PER_G = 1.0 / 453.592

# Adopted stack stations [mm] — mirror nacelle_pod_64mm_tandem.scad.
ROTOR1 = (ROTOR_Z, ROTOR_Z + 10.7)
MOTOR1 = (ROTOR_Z + 14.7, ROTOR_Z + STAGE)
ROTOR2 = (ROTOR_Z + STAGE + 1.0, ROTOR_Z + STAGE + 11.7)
MOTOR2 = (ROTOR_Z + STAGE + 15.7, ROTOR_Z + 2 * STAGE + 1.0)
STATOR_SLV = (ROTOR_Z + 11.7, ROTOR_Z + STAGE + 0.5)
AFT_SLV = (ROTOR_Z + STAGE + 0.5, NOZ_Z)
ESC_BAY_CG = 95.0 * A    # bays centred with the stretched shell
DISC_BAY_Z = 51.0 * A    # 10 AWG disconnect bay (wrapper ESC_DISC_Z)
PIVOT_Z_SET = nacelle_64_scale.pivot_z()   # PIVOT_Z currently set in the 64 mm wrapper
NOZ_REACH = 221.3 - 166.25   # iris reach aft of its pocket, 40 mm flaps


def mid(span: tuple[float, float]) -> float:
    """Midpoint of a station span."""
    return 0.5 * (span[0] + span[1])


def scaled_sleeve(rel: str, z0_50: float, l_50: float,
                  span64: tuple[float, float]) -> tuple[float, float, str]:
    """Scale a measured 50 mm sleeve: mass x K (radius) x length ratio.

    A thin-walled sleeve's volume goes with radius x length; its CG is placed
    at the same FRACTION of its length it measured at in 50 mm form.
    """
    mass50, cg50 = base.measure(rel, ("local", z0_50))
    l64 = span64[1] - span64[0]
    frac = (cg50 - z0_50) / l_50
    note = (f"SCALED est.: {mass50:.1f} g x {K:.2f} x {l64:.1f}/{l_50:.1f} "
            f"from {rel}; stator-as-mount sleeve not yet drawn (NAC-64-GEOM-01)")
    return mass50 * K * l64 / l_50, span64[0] + frac * l64, note


# Items ON the tilt axis for the 64 mm joint (CG at PIVOT_Z by construction).
# 2 x 6704-ZZ (9.8 g) -> 2 x 6804-ZZ, 18 g each [REF-BRG-002]; the trunnion is
# nacelle_trunnion_64mm.stl measured (9.1 g at RHO_PRINT, 2026-10-03).
ON_AXIS_64 = [
    ("Trunnion 64 mm (printed, measured)", 9.1,
     "nacelle_trunnion_64mm.scad render, 2026-10-03"),
    ("2 x 6804-ZZ trunnion bearing", 2 * 18.0, "JTEKT 6804-ZZ [REF-BRG-002]"),
    *[r for r in base.ON_AXIS if not r[0].startswith(("Trunnion", "2 x 6704"))],
]


def rows_64(pod_stl: Path) -> list[tuple[str, float, float, str]]:
    """Every off-axis row of the 64 mm rotating assembly."""
    mesh = base.trimesh.load_mesh(pod_stl, force="mesh")
    pod = (float(mesh.volume * base.RHO_PRINT), float(mesh.center_mass[2]))
    # NAC-64-GEOM-01 drawn 2026-10-03 (edf_motor_mount_64mm.scad): MEASURE
    # the cartridges (cartridge-local z from 0, placed at their forward face).
    # Stage 1 is INTEGRAL with the pod (owner 2026-10-03), so its plate and
    # vanes are already inside the measured pod shell row above.
    af_m, af_cg = base.measure(
        "airframe/stls/nacelles/edf_motor_mount_64mm_stage2_stbd.stl",
        ("local", AFT_SLV[0]))
    aft = (af_m, af_cg, "MEASURED edf_motor_mount_64mm.scad STAGE=2")
    harness_50 = {r[0]: r for r in base.HARNESS}
    phase = harness_50["6 x 16 AWG EDF phase leads"]
    return [
        ("Pod shell, 64 mm (MEASURED)", pod[0], pod[1], str(pod_stl)),
        ("Stage-2 cartridge (sleeve + stator + plate)", aft[0], aft[1], aft[2]),
        ("QF2822 motor 1", 135.0, mid(MOTOR1),
         "SHEET 135 g [REF-EDF-003]; CG at body midpoint, ASSUMED uniform"),
        ("QF2822 motor 2", 135.0, mid(MOTOR2),
         "SHEET 135 g [REF-EDF-003]; CG at body midpoint, ASSUMED uniform"),
        ("Rotor 1 (12-blade + spinner)", 20.0, mid(ROTOR1),
         "ASSUMED 20 g +/-10 g — QX publishes no rotor mass; WEIGH (FIT-02)"),
        ("Rotor 2 (12-blade + spinner)", 20.0, mid(ROTOR2),
         "ASSUMED 20 g +/-10 g — QX publishes no rotor mass; WEIGH (FIT-02)"),
        ("ESC A (70 A, fwd motor, 2 bays)", 52.7, 125.4,
         ("ESTIMATE: tools/esc80_cooptimize.py on tools/esc70_design.json "
          "(Open-Secure-ESC 70 A, two hinged bays); centre from the bay fit")),
        ("ESC B (70 A, aft motor, 2 bays)", 52.7, 136.4,
         ("ESTIMATE: tools/esc80_cooptimize.py on tools/esc70_design.json; "
          "centre from the bay fit")),
        ("4 x ESC access cover", 2 * 4 * 6.99 / 2 * K, 0.5 * (125.4 + 136.4),
         "SCALED est.: 50 mm covers measured x K, two per ESC (four bays)"),
        ("Nozzle throat + housing", 21.4 * K, NOZ_Z + 8.55,
         "SCALED est.: 50 mm iris x K (thin shell); U11 re-sizes"),
        ("Unison ring", 6.7 * K, NOZ_Z + 3.65, "SCALED est.: x K; U11 re-sizes"),
        ("8 x nozzle flap (40 mm)", 21.1 * K, NOZ_Z + 31.95,
         "SCALED est.: flap width x K, length unchanged; U11"),
        ("Nozzle servo drive (KST X06 + bellcrank)", 6.0 + 1.0 + 1.0 + 1.5,
         0.5 * (NOZ_Z - 43.86 + NOZ_Z - 8.86),
         ("KST X06 6 g [REF-ACT-005] + link 1 + spring 1 + bellcrank/pins 1.5 g "
          "(ASSUMED); station midway servo shaft (Z_NOZ - 43.86) .. bellcrank "
          "(Z_NOZ - 8.86), nozzle_servo_linkage_64.py")),
        ("4 x 10 AWG feed",
         4 * (0.060 + (PIVOT_Z_SET - DISC_BAY_Z - 29.5) / 1000.0) * 40.0,
         0.5 * (PIVOT_Z_SET + DISC_BAY_Z),
         ("SCALED est.: 50 mm row (4 x 0.060 m x 40 g/m, 29.5 mm route) "
          "lengthened by the trunnion-to-bay run; CG midway")),
        ("6 x 14 AWG phase leads", phase[1] * 2.08 / 1.31,
         0.5 * (ESC_BAY_CG + 0.5 * (mid(MOTOR1) + mid(MOTOR2))),
         ("SCALED est.: 16 AWG row x copper-area ratio 14/16 AWG for 57 A "
         "candidate current (U10 sizes the conductor)")),
        (*base.HARNESS[2][:3], "unchanged"),
        (*base.HARNESS[3][:3], "unchanged"),
    ]


def roll_up(pod_stl: Path) -> dict:
    """Total mass and CG; on-axis items cannot move the CG (fixed point)."""
    rows = rows_64(pod_stl)
    off_m = sum(r[1] for r in rows)
    cg = sum(r[1] * r[2] for r in rows) / off_m
    on_m = sum(m for _, m, _ in ON_AXIS_64)
    total = off_m + on_m
    assert abs((cg * off_m + cg * on_m) / total - cg) < 1e-9
    arm = NOZ_Z + NOZ_REACH - cg
    tip = base.WING_SPAR_HULL_Z - arm
    return {"rows": rows, "total_g": total, "cg_z": cg,
            "pivot_z": round(cg, 1), "arm": arm, "tip_hull_z": tip,
            "clear_3in": tip - base.GROUND_PLANES[
                "3.0 in gear (kept, not wired in)"],
            "clear_1p5in": tip - base.GROUND_PLANES[
                "1.5 in gear (ACTIVE default)"]}


def main(argv: list[str] | None = None) -> int:
    """Print the roll-up, imperial-primary, and return the gate code."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--pod-stl", type=Path, required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = roll_up(args.pod_stl)
    if args.json:
        print(json.dumps({k: v for k, v in res.items() if k != "rows"},
                         indent=4))
        return 0 if res["clear_3in"] > 0 else 2
    print("Serenity 64 mm nacelle — rotating-assembly mass and CG")
    print(f"{'Item':<34}{'lbm':>7}{'(g)':>8}{'CG in':>7}{'(mm)':>8}")
    for label, m, z, _ in res["rows"]:
        print(f"{label:<34}{m * LBM_PER_G:7.3f}{m:8.1f}{z / 25.4:7.2f}"
              f"{z:8.1f}")
    for label, m, _ in ON_AXIS_64:
        print(f"{label + ' (on axis)':<34}{m * LBM_PER_G:7.3f}{m:8.1f}"
              f"{res['cg_z'] / 25.4:7.2f}{res['cg_z']:8.1f}")
    t = res["total_g"]
    print(f"{'TOTAL':<34}{t * LBM_PER_G:7.3f}{t:8.1f}"
          f"{res['cg_z'] / 25.4:7.2f}{res['cg_z']:8.1f}")
    print(f"\n=> PIVOT_Z = {res['pivot_z'] / 25.4:.2f} in "
          f"({res['pivot_z']:.1f} mm) from the intake face")
    delta = res["cg_z"] - PIVOT_Z_SET
    state = "CONVERGED" if abs(delta) <= 0.25 else "NOT CONVERGED — re-render"
    print(f"Fixed point: wrapper PIVOT_Z {PIVOT_Z_SET:.1f}, measured CG "
          f"{res['cg_z']:.2f}, residual {delta:+.2f} mm -> {state}")
    print(f"Hover: arm {res['arm']:.1f} mm, nozzle tip at hull Z "
          f"{res['tip_hull_z']:+.1f} mm; clearance 3.0 in gear "
          f"{res['clear_3in'] / 25.4:+.2f} in ({res['clear_3in']:+.1f} mm), "
          f"1.5 in gear {res['clear_1p5in'] / 25.4:+.2f} in "
          f"({res['clear_1p5in']:+.1f} mm)")
    return 0 if res["clear_3in"] > 0 else 2


if __name__ == "__main__":
    sys.exit(main())
