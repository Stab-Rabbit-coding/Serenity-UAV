#!/usr/bin/env python3
"""Verify the Rev R6 gear stands on its feet -- LG-10.8.

The item reads "Z-leveling: align all 4 feet to the most negative Z", and the
four feet were never the problem: all four corners share hip Z +38 and one leg
geometry, so they sit at an identical Z to the last digit.  What was wrong is
that the most negative Z of the assembly was **not the sole**.

Measured 2026-08-17, before the fix:

  * 1.5in -- the ankle spigot ran 2.9 mm THROUGH the foot's sole.  The aircraft
    would have parked on four 8 mm CF-PETG spigot tips instead of the TPU
    treads, and the corner could not be assembled at all: 743.9 mm^3 of leg
    frame sat inside the foot, because the ankle disc also gouged the hub.
  * 3.0in -- the same hardcoded spigot bottomed out 0.6 mm (38.4 mm^3) on the
    socket floor, so the foot would have sat proud of its own seating face.

Both came from one hardcoded cube (`ANKLE[2] - 9.75`, 9.5 tall) that predated
the shared canonical foot.  The stack-up is now derived, and this tool gates
the three rules it has to satisfy:

  1. **Disc rim on the hub top.** `FOOT_HUB_H`'s own comment states the
     contract -- "top face meets the ankle disc rim" -- so
     `ANKLE[2] - ANKLE_DISC_D/2` must equal `GROUND_Z + FOOT_HUB_H`.  The
     3.0in leg satisfied it exactly; the 1.5in leg was 6.4 mm out, which is
     the whole defect above.
  2. **Spigot indexes, it does not carry.** The joint closes on the hub top
     face, so the spigot tip must clear the socket floor and must never reach
     the sole.
  3. **Belly clearance is what the variant is named for** -- the sole must sit
     the advertised distance below the cargo belly (hull Z 0).

Then, on the exported `hull_legs` STL: the four feet must share one Z, and the
lowest point of the whole corner compound must BE that sole plane.

Exit status is non-zero on any violation, so this can gate a commit.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-17, per AGENTS.md AI attribution.
License : CC BY-SA 4.0  <https://creativecommons.org/licenses/by-sa/4.0/>

Run: /usr/bin/python3 tools/landing_gear_foot_stance.py
     (system python -- the repo .venv hides trimesh)
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SCAD_DIR = os.path.join(REPO_ROOT, "airframe", "openscad", "fuselage")
STL_DIR = os.path.join(REPO_ROOT, "airframe", "stls", "fuselage", "landing-gear")

# variant -> advertised belly clearance (mm) below hull Z 0.
# 1.5 in = 38.1 mm; 3.0 in = 76.2 mm nominal, built at 80.0 (see
# docs/LANDING_GEAR_ANALYSIS.md SS4.7 -- the extended leg is sized on the
# 80 mm figure, not on the round inch).
BELLY_MM = {"1_5in": 38.1, "3_0in": 80.0}
HIP_Z = 38.0                # hull-frame Z of every hip station (LG-10.2)

# Geometry tolerance.  The SCAD constants are written to 0.1 mm, so 0.05 mm is
# half the last declared digit -- tight enough that a real re-datum trips it.
TOL_MM = 0.05
# Feet must agree far more closely than that: they are one geometry placed four
# times, so anything above export round-off is a placement bug.
LEVEL_TOL_MM = 1e-3

CORNERS_XY = {"fore-port": (-103.87, -1.28), "fore-stbd": (-235.93, -1.28),
              "aft-port": (-92.24, 99.96), "aft-stbd": (-247.56, 99.96)}

try:
    import numpy as np  # noqa: E402
    import trimesh  # noqa: E402
except ImportError:
    sys.exit("trimesh/numpy unavailable -- run with /usr/bin/python3, "
             "not the .venv")


def scad_scalar(text, name):
    """Read `NAME = <number>;` out of a SCAD source."""
    hit = re.search(rf'^{name}\s*=\s*(-?[\d.]+)\s*;', text, re.M)
    if hit is None:
        sys.exit(f"could not read {name}")
    return float(hit.group(1))


def scad_vec3(text, name):
    """Read `NAME = [a, b, c];` out of a SCAD source."""
    hit = re.search(rf'^{name}\s*=\s*\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*,'
                    rf'\s*(-?[\d.]+)\s*\]\s*;', text, re.M)
    if hit is None:
        sys.exit(f"could not read {name}")
    return tuple(float(g) for g in hit.groups())


def check_variant(variant):
    """Return a list of failure strings for one leg variant."""
    path = os.path.join(SCAD_DIR, f"canonical_leg_r6_{variant}.scad")
    with open(path, encoding="utf-8") as fh:
        src = fh.read()

    ankle_z = scad_vec3(src, "ANKLE")[2]
    ground = scad_scalar(src, "GROUND_Z")
    disc_d = scad_scalar(src, "ANKLE_DISC_D")
    hub_h = scad_scalar(src, "FOOT_HUB_H")
    spig_h = scad_scalar(src, "FOOT_SPIG_H")
    clr = scad_scalar(src, "SPIG_FLOOR_CLR")

    sock_floor = ground + hub_h - spig_h + 0.1
    spig_tip = sock_floor + clr
    hub_top = ground + hub_h
    rim = ankle_z - disc_d / 2.0

    print(f"\n=== canonical_leg_r6_{variant}.scad ===")
    print(f"  ankle Z {ankle_z:8.2f}   disc rim {rim:8.2f}")
    print(f"  hub top {hub_top:8.2f}   socket floor {sock_floor:8.2f}")
    print(f"  spigot tip {spig_tip:8.2f}   sole {ground:8.2f}")

    fails = []
    # 1. disc rim lands on the hub top face
    off = rim - hub_top
    ok = abs(off) <= TOL_MM
    print(f"  1. disc rim on hub top face      : {off:+6.2f} mm  "
          f"-- {'ok' if ok else 'FAIL'}")
    if not ok:
        fails.append(f"{variant}: disc rim {off:+.2f} mm off the hub top "
                     f"(set ANKLE[2] = {hub_top + disc_d / 2.0:.2f})")

    # 2. spigot clears the socket floor and never reaches the sole
    ok = spig_tip > sock_floor - 1e-9 and spig_tip > ground + TOL_MM
    print(f"  2. spigot clears floor / sole    : "
          f"{spig_tip - sock_floor:+6.2f} / {spig_tip - ground:+6.2f} mm  "
          f"-- {'ok' if ok else 'FAIL'}")
    if not ok:
        fails.append(f"{variant}: spigot tip at {spig_tip:.2f} bottoms out "
                     f"(socket floor {sock_floor:.2f}, sole {ground:.2f})")

    # 3. belly clearance is what the variant is named for.  The hip sits at
    # hull Z +38 and GROUND_Z is leg-local, so the sole lands at HIP_Z +
    # GROUND_Z and the clearance below the cargo belly (hull Z 0) is its
    # negation.
    belly = -(HIP_Z + ground)
    want = BELLY_MM[variant]
    ok = abs(belly - want) <= TOL_MM
    print(f"  3. belly clearance               : {belly:6.2f} mm "
          f"(want {want}) -- {'ok' if ok else 'FAIL'}")
    if not ok:
        fails.append(f"{variant}: belly clearance {belly:.2f} != {want}")

    # 4. the exported compound: four level feet, lowest point = the sole
    stl = os.path.join(STL_DIR, f"lg_r6_{variant}_hull_legs.stl")
    if not os.path.exists(stl):
        fails.append(f"{variant}: {os.path.basename(stl)} not exported")
        return fails
    v = trimesh.load(stl, process=False).vertices
    zmins = {}
    for label, (cx, cy) in CORNERS_XY.items():
        d = np.hypot(v[:, 0] - cx, v[:, 1] - cy)
        other = np.array([np.hypot(v[:, 0] - ox, v[:, 1] - oy)
                          for l2, (ox, oy) in CORNERS_XY.items() if l2 != label])
        zmins[label] = float(v[other.min(axis=0) > d, 2].min())
    spread = max(zmins.values()) - min(zmins.values())
    sole_hull = HIP_Z + ground
    low = min(zmins.values())
    feet = "  ".join(f"{k.split('-')[0][0]}{k.split('-')[1][0]} {z:.3f}"
                     for k, z in zmins.items())
    print(f"  4. exported feet: {feet}")
    ok_level = spread <= LEVEL_TOL_MM
    print(f"     spread {spread:.4f} mm -- {'ok' if ok_level else 'FAIL'}")
    if not ok_level:
        fails.append(f"{variant}: feet differ by {spread:.4f} mm")
    ok_sole = abs(low - sole_hull) <= TOL_MM
    print(f"     lowest point {low:.3f} vs sole plane {sole_hull:.3f} "
          f"-- {'ok' if ok_sole else 'FAIL'}")
    if not ok_sole:
        fails.append(f"{variant}: lowest point {low:.3f} is "
                     f"{sole_hull - low:.3f} mm below the sole -- the gear "
                     f"does not stand on its treads")
    return fails


def main():
    print("LG-10.8 foot stance -- the gear must stand on its treads")
    fails = []
    for variant in ("1_5in", "3_0in"):
        fails += check_variant(variant)
    print()
    if fails:
        for f in fails:
            print(f"  FAIL  {f}")
        sys.exit(1)
    print("  CLEAR -- LG-10.8 satisfied on both variants")


if __name__ == "__main__":
    main()
