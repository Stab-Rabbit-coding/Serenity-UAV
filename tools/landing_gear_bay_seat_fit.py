#!/usr/bin/env python3
"""Verify the printed Rev R6 bay actually seats on the hull it bolts to.

LG-10.6 was originally written as "generate per-station hull patches and set
`BAY_CONFORM = true` so the bay back face is cut to the real surface".  That
instrument is obsolete, and this tool is what replaced it.

Why the conforming back face is no longer the answer
----------------------------------------------------
It was specified when the bay was a flat plate surface-mounted on the raw,
doubly-curved cargo flank -- a plate cannot sit on a compound curve, so the
plate had to take the curve.  Since LG-10.3/LG-10.4 the hull no longer offers
a raw flank: `merge_cargo_interior.lg_bay_features()` cuts a **flange rebate**
(a flat trapezoidal pocket, `BAY_PLATE_T` deep and 12 mm into the skin) and
adds a **seat collar** under it.  The rebate is deep enough to shave the whole
footprint -- `tools/landing_gear_wing_clearance.py --proud` reports "none" --
so the hull already presents a FLAT seat, machined normal to the bolt axis by
construction.  Cutting the printed part to a curve it no longer meets would
re-introduce the very mismatch it was meant to remove, and would split the bay
into four unshared geometries for nothing.

What actually needed fixing
---------------------------
The datum.  The hull's pocket floor is placed by `seat_offset()`, measured in
the plate's OWN frame; the printed bay is placed by `BAY_STANDOFF` in
`canonical_leg_r6_*.scad`, which still carried 12.6 / 5.4 mm -- the older
figure measured along the SS2.4a panel normal, a different frame.  The two
disagreed by 3.5-7.7 mm, so every bolt would have clamped across an air gap.
This tool gates that pair, and fails on drift.

Checks
------
  1. **Datum drift** -- both leg variants must declare the same
     `BAY_STANDOFF`, and each must equal
     `merge_cargo_interior.BAY_STANDOFF[station] + station_x0[station]`
     re-measured live from the hollowed source shell.
  2. **Interference** -- the printed plate's own 5 mm envelope, placed where
     the SCAD declares it, must not run into the published hull.  A plate that
     interferes cannot be pulled down onto its seat.
  3. **Shim gap** -- one datum per station means the shallower corner of each
     pair sits slightly proud of its pocket floor.  Reported per corner and
     capped by `SHIM_BUDGET_MM`; anything under it is a feeler-gauge shim at
     assembly, not a geometry defect.

Method note: the seat datum is re-measured from `BLENDER_SRC` (the pre-cut
hollowed shell) through `merge_cargo_interior.station_seat_data()` -- the same
call the production merge makes -- so this tool cannot drift from the geometry
it certifies.  Measuring it on the PUBLISHED shell instead would be circular:
the rebate has already been cut there, which moves the outboard skin inboard.

Exit status is non-zero on any drift or interference, so this can gate a
commit.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-17, per AGENTS.md AI attribution.
License : CC BY-SA 4.0  <https://creativecommons.org/licenses/by-sa/4.0/>

Run: /usr/bin/python3 tools/landing_gear_bay_seat_fit.py
     (system python -- the repo .venv hides manifold3d)
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
MERGE_DIR = os.path.join(REPO_ROOT, "airframe", "blender-scripts")
SCAD_DIR = os.path.join(REPO_ROOT, "airframe", "openscad", "fuselage")
VARIANTS = ("canonical_leg_r6_1_5in.scad", "canonical_leg_r6_3_0in.scad")

sys.path.insert(0, MERGE_DIR)

# Datum agreement tolerance.  The seat is measured to 0.01 mm; 0.05 mm is five
# times that and still an order below the 0.4 mm assembly clearance the rebate
# already carries, so a real re-datum cannot slip through.
DATUM_TOL_MM = 0.05
# Boolean-residue floor -- the plate prism and the shell are both boolean
# results, so a face pair in contact leaves sub-micron slivers.
EPS_MM3 = 1e-3
# Largest shim a corner may need because its station shares one datum.
# Measured worst at adoption (2026-08-17): 1.14 mm at fore-port.
SHIM_BUDGET_MM = 1.5

try:
    import trimesh  # noqa: E402
except ImportError:
    sys.exit("trimesh unavailable -- run with /usr/bin/python3, "
             "not the .venv")

import merge_cargo_interior as mci  # noqa: E402

# BAY_STANDOFF = (BAY_STATION == "fore") ? <fore> : <aft>;
STANDOFF_RE = re.compile(
    r'BAY_STANDOFF\s*=\s*\(\s*BAY_STATION\s*==\s*"fore"\s*\)\s*\?\s*'
    r'([-\d.]+)\s*:\s*([-\d.]+)\s*;')


def scad_standoffs(path):
    """Read the declared {station: standoff} out of one leg SCAD variant."""
    with open(path, encoding="utf-8") as fh:
        hit = STANDOFF_RE.search(fh.read())
    if hit is None:
        sys.exit(f"could not find BAY_STANDOFF in {path}")
    return {"fore": float(hit.group(1)), "aft": float(hit.group(2))}


def main():
    print("LG-10.6 bay seat fit -- printed bay datum vs the hull it bolts to")

    # --- declared: what the printed part believes -------------------------
    declared = {}
    for name in VARIANTS:
        got = scad_standoffs(os.path.join(SCAD_DIR, name))
        print(f"  {name}: BAY_STANDOFF fore {got['fore']} / aft {got['aft']}")
        declared[name] = got
    variants = list(declared.values())
    if variants[0] != variants[1]:
        print("\n  FAIL -- the two leg variants declare different standoffs; "
              "the bay is shared hardware and must not fork")
        sys.exit(1)
    scad = variants[0]

    # --- required: what the hull was actually cut to ----------------------
    src = trimesh.load(mci.BLENDER_SRC, process=False)
    src.merge_vertices()
    shell_src = mci.bake(src)
    seats, station_x0 = mci.station_seat_data(shell_src)
    print(f"  source shell: {len(shell_src.faces):,} faces, "
          f"watertight={shell_src.is_watertight}")

    print("\n1. datum drift (SCAD BAY_STANDOFF vs the measured hull seat)")
    drift_fail = []
    for station in sorted(station_x0):
        need = mci.BAY_STANDOFF[station] + station_x0[station]
        have = scad[station]
        drift = have - need
        flag = "ok" if abs(drift) <= DATUM_TOL_MM else "DRIFT"
        print(f"  {station:4s}: hull datum x0 {station_x0[station]:+6.2f}  "
              f"required {need:6.2f}  declared {have:6.2f}  "
              f"drift {drift:+6.2f} mm  -- {flag}")
        if abs(drift) > DATUM_TOL_MM:
            drift_fail.append(station)

    # --- 2/3: place the plate where the SCAD says, against the real hull ---
    shell = trimesh.load(mci.OUT_PATH, process=False)
    shell.merge_vertices()
    print(f"\n  published shell: {len(shell.faces):,} faces, "
          f"watertight={shell.is_watertight}")

    print("\n2. printed plate vs published hull (must not interfere)")
    zb1 = mci.BAY_PLATE_ZB0 + mci.BAY_PLATE_L
    shell_man = mci.to_man(shell)
    worst_v, hits = 0.0, []
    shims = []
    for label, hx, hy, hz, az, station in mci.LG_CORNERS:
        org, ex, ey, ez = mci._plate_frame(hx, hy, hz, az, station)
        # where the SCAD's declared standoff puts the plate's back face, in the
        # same plate frame the hull features were cut in
        back = scad[station] - mci.BAY_STANDOFF[station]
        plate = mci._plate_trap(org, ex, ey, ez,
                                mci.BAY_PLATE_WB, mci.BAY_PLATE_W,
                                mci.BAY_PLATE_ZB0, zb1,
                                back, back + mci.BAY_PLATE_T)
        got = mci.from_man(mci.to_man(plate) ^ shell_man)
        vol = abs(got.volume) if len(got.faces) else 0.0
        worst_v = max(worst_v, vol)
        if vol > EPS_MM3:
            hits.append((label, vol))
        print(f"  {label:10s} {station}: plate back x {back:+6.2f}  "
              f"interference {vol:9.3f} mm^3")
        if label in seats:
            shims.append((label, seats[label][1] - station_x0[station]))

    print("\n3. shim gap from sharing one datum per station "
          f"(budget {SHIM_BUDGET_MM} mm)")
    shim_fail = [(lab, g) for lab, g in shims if g > SHIM_BUDGET_MM]
    for label, gap in shims:
        print(f"  {label:10s}: {gap:5.2f} mm"
              f"{'  -- OVER BUDGET' if gap > SHIM_BUDGET_MM else ''}")

    print()
    if drift_fail:
        print(f"  DRIFT -- {', '.join(drift_fail)} station(s): update "
              f"BAY_STANDOFF in both canonical_leg_r6_*.scad, or re-run the "
              f"cargo merge if the hull moved")
    if hits:
        print(f"  INTERFERES -- {len(hits)} corner(s), worst "
              f"{worst_v:.3f} mm^3; the bay cannot be pulled onto its seat")
    if shim_fail:
        print(f"  SHIM OVER BUDGET -- {len(shim_fail)} corner(s), worst "
              f"{max(g for _l, g in shim_fail):.2f} mm")
    if drift_fail or hits or shim_fail:
        sys.exit(1)
    print("  CLEAR -- LG-10.6 bay seats on the hull at every corner")


if __name__ == "__main__":
    main()
