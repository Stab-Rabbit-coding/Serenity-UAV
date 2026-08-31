#!/usr/bin/env python3
"""Size a hollow spar bore against the conductor bundle it has to swallow.

WHY THIS EXISTS
---------------
The Rev T tilt-spar was sized for TORQUE (8 mm OD x 1.5 mm wall AISI 4130,
`docs/TILT_SPAR_ANALYSIS.md` SS3) and its 5 mm bore carried nothing heavier
than the WS2812C nav-light 3-core.  The unified-spar architecture
(`docs/plans/2026-08-29-003-feat-unified-20mm-spar-trunnion-belt-drive-plan.md`)
moves the four 10 AWG ESC feeds ONTO the tilt axis, which makes the bore a
WIRE-VOLUME problem instead of a torque problem.

Two independent sources got the number wrong before this tool existed:

  * the owner's draft (`docs/plans/2026-08-27-nacelle-wiring-plan.md`) proposed
    `SPAR_BORE_D = 11.0` for 4 conductors, and
  * the external source conversation quoted 13.3 mm in prose and then wrote
    11.0 into its own plan.

Neither leaves ANY clearance, and 11.0 does not fit at all.  The failure mode
is not subtle -- it is a 6-hour print and a procured CF tube that cannot be
threaded -- so the packing arithmetic gets its own fail-closed tool rather than
living in a comment.

THE ARITHMETIC
--------------
For `n` equal circles of diameter `d` packed inside the smallest enclosing
circle, the enclosing diameter is `d * K(n)` where `K` is the exact,
published optimal-packing ratio.  Only the small-n cases this airframe can
actually present are tabulated; anything outside the table is refused rather
than interpolated (an interpolated packing ratio is a fabricated constant).

  n = 1  K = 1                exact
  n = 2  K = 2                exact
  n = 3  K = 1 + 2/sqrt(3)    exact  (= 2.15470...)
  n = 4  K = 1 + sqrt(2)      exact  (= 2.41421...)
  n = 5  K = 1 + sqrt(2(1 + 1/sqrt(5)))  exact (= 2.70130...)
  n = 6  K = 3                exact
  n = 7  K = 3                exact  (hexagonal + centre)

Reference for the K(n) values: Melissen, J.B.M. (1997), "Packing and Covering
with Circles", PhD thesis, Utrecht University -- the n <= 7 cases are proven
optimal there and are reproduced in the standard circle-packing literature.
Catalogued as REF-MATH-001 in REFERENCES.md.

`K(n) * d` is a ZERO-CLEARANCE floor: the wires touch each other and the bore
wall simultaneously.  A buildable bore adds a radial clearance so the bundle
can be pulled through and, on this aircraft, so it can TWIST -- the nacelle
sweeps -5..+140 deg and the bundle absorbs that as distributed torsion along
the captive length instead of a swept arc at a fixed port.

  bore_min = K(n) * d + 2 * radial_clearance
  tube_OD  = bore_min + 2 * wall

CAVEAT CARRIED FORWARD (plan 003 DEP-2 / OQ4)
---------------------------------------------
`current-specification/bom_revS.csv` records NO outside diameter for
`WIRE-10AWG` (generically sourced, "10AWG silicone wire red/black").  The
default 5.5 mm here is the upper end of the typical 10 AWG silicone range and
is an ASSUMPTION, not a measured or cited figure.  The tool prints that
caveat on every run and `--wire-od` exists so the real figure can be
substituted the moment it is measured.  Do not quote this tool's output as
verified until that happens.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-29, per AGENTS.md AI attribution.
License : CC BY-SA 4.0  <https://creativecommons.org/licenses/by/4.0/>

Run: /usr/bin/python3 tools/spar_bundle_fit.py
     /usr/bin/python3 tools/spar_bundle_fit.py --tube 20x16.3 --tube 16x14
"""

import argparse
import math
import sys

# ---------------------------------------------------------------------------
# Exact optimal enclosing-circle ratios, n circles of unit diameter.
# See the module docstring for the citation.  DO NOT interpolate this table.
# ---------------------------------------------------------------------------
PACKING_K = {
    1: 1.0,
    2: 2.0,
    3: 1.0 + 2.0 / math.sqrt(3.0),
    4: 1.0 + math.sqrt(2.0),
    5: 1.0 + math.sqrt(2.0 * (1.0 + 1.0 / math.sqrt(5.0))),
    6: 3.0,
    7: 3.0,
}

# Design defaults for the Serenity unified spar.
DEFAULT_N = 4               # 2 ESCs x (B+ / B-)
DEFAULT_WIRE_OD = 5.5       # [mm] ASSUMED -- see the docstring caveat
DEFAULT_CLEARANCE = 1.5     # [mm] radial, plan 003 R1
DEFAULT_TUBES = ["16x12", "16x13", "16x14", "20x16", "20x16.3", "20x18"]


def packing_k(n):
    """Exact enclosing-circle ratio for n equal circles, or refuse."""
    if n not in PACKING_K:
        sys.exit(f"no exact packing ratio tabulated for n = {n}; "
                 f"tabulated: {sorted(PACKING_K)}.  Refusing to interpolate "
                 f"-- an interpolated packing constant is a fabricated one.")
    return PACKING_K[n]


def parse_tube(spec):
    """Parse an 'ODxID' tube spec (e.g. '20x16.3') into (od, id, wall)."""
    try:
        od_s, id_s = spec.lower().split("x", 1)
        od, bore = float(od_s), float(id_s)
    except ValueError:
        sys.exit(f"could not parse tube spec {spec!r}; expected e.g. 20x16.3")
    if bore >= od:
        sys.exit(f"tube {spec}: bore {bore} is not smaller than OD {od}")
    return od, bore, (od - bore) / 2.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wires", type=int, default=DEFAULT_N,
                    help=f"conductor count (default {DEFAULT_N})")
    ap.add_argument("--wire-od", type=float, default=DEFAULT_WIRE_OD,
                    help=f"single conductor OD, mm (default "
                         f"{DEFAULT_WIRE_OD} -- ASSUMED, see docstring)")
    ap.add_argument("--clearance", type=float, default=DEFAULT_CLEARANCE,
                    help=f"required RADIAL clearance around the bundle, mm "
                         f"(default {DEFAULT_CLEARANCE}, plan 003 R1)")
    ap.add_argument("--tube", action="append", default=None,
                    metavar="ODxID",
                    help="candidate tube to PASS/FAIL (repeatable); "
                         f"default set: {' '.join(DEFAULT_TUBES)}")
    args = ap.parse_args()

    n, d, clr = args.wires, args.wire_od, args.clearance
    k = packing_k(n)
    circumscribed = k * d
    bore_min = circumscribed + 2.0 * clr

    print("spar bundle fit -- circle packing inside a round bore")
    print(f"  conductors           {n} x D{d:.2f} mm")
    print(f"  packing ratio K({n})   {k:.5f}  (exact, tabulated -- "
          f"not interpolated)")
    print(f"  circumscribed bundle D{circumscribed:.2f} mm  "
          f"(ZERO clearance: wires touch bore wall)")
    print(f"  required radial clr   {clr:.2f} mm")
    print(f"  => minimum bore      D{bore_min:.2f} mm")
    print()
    print("  ASSUMPTION: WIRE-10AWG has no recorded OD in "
          "current-specification/bom_revS.csv.")
    print("  The default 5.5 mm is the upper end of the typical 10 AWG "
          "silicone range and is")
    print("  NOT a measured or cited figure (plan 003 DEP-2 / OQ4).  "
          "Re-run with --wire-od")
    print("  once the procured wire is measured before quoting any of "
          "this as verified.")

    # Zero-clearance reference table across the plausible OD range, so the
    # sensitivity to the unverified wire OD is visible rather than implied.
    print(f"\nzero-clearance floor vs. wire OD (n = {n}):")
    print("  wire OD    bundle D    bore @ "
          f"{clr:.1f} mm radial    tube OD @ 2.0 mm wall")
    for wod in (4.5, 5.0, 5.5, 6.0):
        b = k * wod
        bm = b + 2.0 * clr
        print(f"   {wod:5.2f}      {b:6.2f}         {bm:6.2f}"
              f"                  {bm + 4.0:6.2f}")

    print(f"\ncandidate tubes (bundle D{circumscribed:.2f}, "
          f"target radial clearance {clr:.2f} mm):")
    print("  tube        wall   bore   radial clr   verdict")
    worst_fail = False
    for spec in (args.tube or DEFAULT_TUBES):
        od, bore, wall = parse_tube(spec)
        radial = (bore - circumscribed) / 2.0
        if radial < 0.0:
            verdict = "FAIL  bundle does not fit at all"
            worst_fail = True
        elif radial < clr:
            verdict = f"MARGINAL  {clr - radial:.2f} mm under target"
        else:
            verdict = "PASS"
        print(f"  {spec:<10} {wall:4.2f}  {bore:5.2f}      "
              f"{radial:+5.2f}      {verdict}")

    print("\n  MARGINAL is not automatically a rejection: a bundle that fits "
          "but cannot freely")
    print("  twist is a fatigue problem, not a fit problem, and this "
          "aircraft's bundle must")
    print("  absorb the -5..+140 deg sweep as distributed torsion "
          "(plan 003 R1/R2).")
    if worst_fail:
        print("\n  At least one candidate FAILS outright.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
