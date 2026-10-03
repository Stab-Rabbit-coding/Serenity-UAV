#!/usr/bin/env python3
"""
nacelle_axial_fit.py — U9 axial-fit gate for the 64 mm QX-Motor tandem nacelle.

WHAT THIS GUARDS
----------------
Plan docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md R11 / KTD8
holds the nacelle at its CURRENT axial length (NACELLE_L) and its current intake
and nozzle stations, and requires two complete QX-Motor 64 mm EDF stages, an
interstage stator, the motor mounts and the nozzle to fit inside that envelope.
A failed fit is a STOP for owner adjudication — this tool reports the shortfall,
it never proposes a longer nacelle.

The nacelle stations are read from the SOURCE
(airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad), not restated.  The
propulsion dimensions come from the user-supplied QX-Motor drawings in
docs/references/qx-motor 64mm edf/ (8-4.jpg motor drawing, 7-2.jpg manual) and
are PROVISIONAL until measured on a physical unit (plan U9 step 3, R13).

STACK MODEL
-----------
Per the owner clarification of 2026-10-01 (airframe/wings-nacelles/WBS.md
§1.1.4, NAC-64-SERVO-01) the QX shroud is discarded; the printed nacelle tube is
the rotor flow boundary.  Each stage, fore to aft, is:

    rotor hub on the shaft  |  motor mount (spider or stator front plate)  |
    motor body hanging AFT of the mount face

The QF2822 drawing (8-4.jpg) puts the 4 x M3 / 16 mm bolt-circle face on the
shaft end of a 58.0 mm body; the shaft stands 68.7 - 58.0 = 10.7 mm proud of
that face.  The rotor therefore sits FORWARD of the mount and the whole 58.0 mm
body sits aft of it.  Stator vanes may overlap the motor body radially (the body
is the stator hub), so the stator itself costs no axial length beyond the motor;
the motor body, not the stator, sets the stage length.  The stage-2 motor tail
must clear the nozzle ring pocket (NOZZLE_RING_Z) so the variable nozzle sees an
open bore, not a plug.

Two cases are reported:
  CURRENT  — present architecture: separate 8 mm spider arms per stage, rotor
             hub length taken as the drawing's 18.50 mm feature (datum unknown).
  BEST     — most favourable reading: the stator front plate IS the mount
             (3 mm plate, no separate spider), rotor hub only as long as the
             10.7 mm shaft protrusion, 1 mm running gaps.
  ADOPTED  — owner adjudication 2026-10-03 (Steve Griffing): the BEST stack
             (stator front plate as the motor mount) with the intake bell
             trimmed by INTAKE_TRIM, moving EDF1_Z_ENTRY forward.  Nacelle
             length and NOZZLE_RING_Z stay fixed.
CURRENT and BEST are measured against the SCAD's present EDF1_Z_ENTRY and
reported for the record.  The exit code follows ADOPTED.  Its margin is thin
on drawing values, so it remains VERIFY until a physical QF2822 and rotor are
measured (WBS NAC-64-FIT-02).

Usage:
    /usr/bin/python3 tools/nacelle_axial_fit.py [--json]

Exit 0 = ADOPTED case fits.  Exit 2 = it does not (STOP, R11).

References (see REFERENCES.md): [REF-EDF-003]
    QX-Motor 64 mm EDF instruction manual and QF2822 dimension drawing,
    user-supplied images, docs/references/qx-motor 64mm edf/ — requires
    verification against a catalogued manufacturer source (plan U7).

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding) —
owner decisions and stack constraints.
Tool and analysis by Claude (Claude Opus 5.5, Anthropic) under the author's
direction, per AGENTS.md AI attribution.
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

# Repository root and the nacelle SCAD that owns the axial stations.
REPO = Path(__file__).resolve().parent.parent
POD_SCAD = REPO / "airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad"

# Millimetres per inch, for imperial-primary reporting (AGENTS.md units rule).
MM_PER_IN = 25.4

# ── QX-Motor QF2822 dimensions from 8-4.jpg (PROVISIONAL — VERIFY, plan U9) ──
QF2822_BODY_TO_MOUNT_FACE = 58.0   # [mm] rear cap to bolt face (drawing "58.0")
QF2822_OVERALL_WITH_SHAFT = 68.7   # [mm] rear cap to shaft tip (drawing "68.7")
QF2822_CAN_D = 27.8                # [mm] can diameter (drawing "ø27.80")
QF2822_BOLT_CIRCLE_D = 16.0        # [mm] 4 x M3 bolt circle (drawing "ø16.00")
SHAFT_PROTRUSION = QF2822_OVERALL_WITH_SHAFT - QF2822_BODY_TO_MOUNT_FACE

# ── QX EDF manual 7-2.jpg feature whose datum is not identified (VERIFY) ──
QX_EDF_SHROUD_AXIAL = 41.53        # [mm] shroud length — shroud is DISCARDED
QX_DRAWING_18_50 = 18.50           # [mm] unlabelled feature, read as rotor hub


@dataclass(frozen=True)
class StackCase:
    """One reading of the per-stage axial stack, all lengths in mm."""

    name: str
    rotor_hub_l: float     # rotor hub axial length, forward of the mount face
    rotor_gap: float       # running gap, rotor hub aft face to mount front face
    mount_l: float         # spider arm or stator front-plate axial thickness
    interstage_gap: float  # motor-1 tail to rotor-2 hub front face


# The cases described in the module docstring.
CASES = (
    StackCase("CURRENT", QX_DRAWING_18_50, 1.0, 8.0, 2.0),
    StackCase("BEST", SHAFT_PROTRUSION, 1.0, 3.0, 1.0),
    StackCase("ADOPTED", SHAFT_PROTRUSION, 1.0, 3.0, 1.0),
)

# Intake-bell trim for the ADOPTED case [mm] — owner adjudication 2026-10-03,
# "stator-as-mount + shorter intake" (about 8 mm).
INTAKE_TRIM = 8.0


def scad_param(text: str, name: str) -> float:
    """Return the numeric literal assigned to `name` in the SCAD source.

    Only plain `NAME = <number>;` assignments are accepted so a refactor that
    turns a station into an expression fails loudly instead of being misread.
    """
    match = re.search(rf"^{name}\s*=\s*(-?[0-9.]+)\s*;", text, re.MULTILINE)
    if match is None:
        raise ValueError(f"{name} not found as a numeric literal in {POD_SCAD}")
    return float(match.group(1))


def stations() -> dict[str, float]:
    """Read the fixed axial stations (R11) from the nacelle pod SCAD."""
    text = POD_SCAD.read_text(encoding="utf-8")
    return {
        "NACELLE_L": scad_param(text, "NACELLE_L"),
        "EDF1_Z_ENTRY": scad_param(text, "EDF1_Z_ENTRY"),
        "NOZZLE_RING_Z": scad_param(text, "NOZZLE_RING_Z"),
    }


def stage_length(case: StackCase) -> float:
    """Axial length of one stage: rotor hub, gap, mount, then motor body."""
    return (case.rotor_hub_l + case.rotor_gap + case.mount_l
            + QF2822_BODY_TO_MOUNT_FACE)


def evaluate(case: StackCase, st: dict[str, float]) -> dict[str, float | str]:
    """Lay the two stages from the intake station aft and compare to the nozzle.

    The stack starts at EDF1_Z_ENTRY (the intake bell is preserved, R11) and
    must end, with the stage-2 motor tail, at or before NOZZLE_RING_Z.
    """
    stage = stage_length(case)
    # ADOPTED moves the stack start forward by the owner-approved trim.
    entry = st["EDF1_Z_ENTRY"] - (INTAKE_TRIM if case.name == "ADOPTED" else 0.0)
    tail_z = entry + 2.0 * stage + case.interstage_gap
    available = st["NOZZLE_RING_Z"] - entry
    required = tail_z - entry
    return {
        **asdict(case),
        "entry_z": entry,
        "stage_l": stage,
        "motor2_tail_z": tail_z,
        "available": available,
        "required": required,
        "margin": available - required,
        "verdict": "PASS" if tail_z <= st["NOZZLE_RING_Z"] else "FAIL",
    }


def fmt(mm: float) -> str:
    """Imperial-primary length with metric in parentheses."""
    return f"{mm / MM_PER_IN:.2f} in ({mm:.1f} mm)"


def main(argv: list[str] | None = None) -> int:
    """Run both cases, print the report, and return the gate exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    st = stations()
    results = [evaluate(case, st) for case in CASES]
    gate = next(r for r in results if r["name"] == "ADOPTED")

    if args.json:
        print(json.dumps({"stations": st, "results": results}, indent=4))
    else:
        print("U9 axial fit — two QX QF2822 stages in the fixed nacelle (R11)")
        print(f"  NACELLE_L      {fmt(st['NACELLE_L'])}")
        print(f"  EDF1_Z_ENTRY   {fmt(st['EDF1_Z_ENTRY'])}  (intake preserved)")
        print(f"  NOZZLE_RING_Z  {fmt(st['NOZZLE_RING_Z'])}  (stage-2 tail limit)")
        print(f"  QF2822 body to mount face {fmt(QF2822_BODY_TO_MOUNT_FACE)}; "
              f"shaft protrusion {fmt(SHAFT_PROTRUSION)}  [VERIFY]")
        for r in results:
            print(f"\n  {r['name']}: stage {fmt(r['stage_l'])}, "
                  f"required {fmt(r['required'])}, "
                  f"available {fmt(r['available'])}")
            print(f"    motor-2 tail at Z {fmt(r['motor2_tail_z'])} -> "
                  f"margin {fmt(r['margin'])}  {r['verdict']}")
        print(f"\n  ADOPTED intake trim {fmt(INTAKE_TRIM)} -> EDF1 entry "
              f"Z {fmt(gate['entry_z'])}; margin is VERIFY (drawing values)")
        if gate["verdict"] == "FAIL":
            print("\nSTOP (plan Goal Capsule / R11): the adopted stack does "
                  "not fit the fixed axial envelope. Owner adjudication "
                  "required; do not lengthen the nacelle here.")
    return 0 if gate["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
