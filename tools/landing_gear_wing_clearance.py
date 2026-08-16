#!/usr/bin/env python3
"""Verify the Rev R6 gear bay clears the wing structure it shares a station with.

LG-10.4 requires the sponson attachment to be hollowed and reinforced for the
bay **without touching the wing**.  That is not a small margin: the sponson
spans the wing-root station, so the bay's aperture, flange rebate and 16 M3
bores are cut into the same block of hull that carries the Ø12.3 spar bore,
the Ø22 spar bearing bosses coaxial with it, and the two wing-root mortises.
A bay that eats into a spar boss looks perfectly clean in isolation and
destroys the wing mount.

Every station is read live from `merge_cargo_interior` and echoed in the run
header -- deliberately NOT repeated here, because the spar has already moved
once (30 % -> 35 % root chord, Rev S1b 2026-08-16) and any figure hardcoded
in this docstring went stale the moment it did.

Two independent failure modes are checked, because they fail in opposite
directions and either one alone would pass a naive test:

  1. **Bay negatives vs wing positives** -- the bay's cuts removing material
     the wing bearing needs (spar bosses, nacelle-servo pads).
  2. **Bay positives vs wing negatives** -- the bay's seat collar intruding
     into the spar bore or a mortise, blocking the spar rod or the wing-root
     tenon at assembly.

Method
------
The bay solids are taken from `merge_cargo_interior.lg_bay_features()` -- the
same call the production merge makes, seated on the same measured skin -- so
this tool cannot drift from the geometry it certifies.  The wing solids are
rebuilt from that module's own constants.  Every pair is intersected with
manifold3d and the intersection volume reported.

Tolerances
----------
The bay solids are themselves boolean results (they are trimmed against the
keep-outs), so a subtracted face pair leaves sub-micron slivers behind.
`EPS_MM3` is that residue floor -- 1e-3 mm^3 is a cube 0.1 mm on a side, four
orders of magnitude below the smallest defect this tool has ever found
(2.7 mm^3), so nothing real hides under it.

One overlap is ACCEPTED rather than eliminated: the bay's 16 M3 bolt bores are
deliberately not trimmed, because a blocked bolt bore is a hard assembly
failure while a nicked pad edge is not.  Four of them clip a nacelle-servo pad
edge (7.7-14.5 mm^3).  That allowance is budgeted by `BORE_PAD_BUDGET_MM3` and
still gated two ways: the budget caps how far it may grow, and the bores are
checked against the servo M3 PILOT bores with no allowance at all, since a
bore breaking into a pilot would ruin the servo mount.

Exit status is non-zero on any unbudgeted interference, so this can gate a
commit.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-16, per AGENTS.md AI attribution.
License : CC BY-SA 4.0  <https://creativecommons.org/licenses/by-sa/4.0/>

Run: /usr/bin/python3 tools/landing_gear_wing_clearance.py
     (system python -- the repo .venv hides manifold3d)
"""

import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
MERGE_DIR = os.path.join(REPO_ROOT, "airframe", "blender-scripts")
CARGO_STL = os.path.join(
    REPO_ROOT, "airframe", "stls", "fuselage", "cargo",
    "cargo_sect_shell24_2mm_repaired.stl",
)

sys.path.insert(0, MERGE_DIR)

# Boolean-residue floor -- see "Tolerances" above.
EPS_MM3 = 1e-3
# Accepted nick a single bay bolt bore may take out of a servo pad edge.
# Measured worst at adoption (2026-08-16): 14.482 mm^3.
BORE_PAD_BUDGET_MM3 = 20.0

try:
    import numpy as np  # noqa: E402
    import trimesh  # noqa: E402
except ImportError:
    sys.exit("trimesh/numpy unavailable -- run with /usr/bin/python3, "
             "not the .venv")

import merge_cargo_interior as mci  # noqa: E402


# The keep-out solids come from the merge module itself (LG-10.4), so this
# tool certifies the geometry the hull is actually built with.  Rebuilding
# them here would let the check and the part drift apart silently -- which is
# exactly the failure this tool exists to catch.
#
# wing_keepout_positives() MUST be given the envelope: the raw solids are deep
# features that only become material where they meet the skin.
wing_negatives = mci.wing_keepout_negatives


def intersect_volume(a, b):
    """Intersection volume of two solids, in mm^3 (0.0 when disjoint)."""
    # Cheap AABB reject first: manifold booleans on 48-section cylinders are
    # not free, and most of this matrix is trivially disjoint.
    amin, amax = a.bounds
    bmin, bmax = b.bounds
    if (amin > bmax).any() or (bmin > amax).any():
        return 0.0
    res = mci.to_man(a) ^ mci.to_man(b)
    mesh = mci.from_man(res)
    if len(mesh.faces) == 0:
        return 0.0
    # A degenerate sliver has zero volume and makes trimesh's inertia
    # calculation divide by it; ask for the raw volume only.
    with np.errstate(divide="ignore", invalid="ignore"):
        vol = abs(float(mesh.volume))
    return 0.0 if vol < EPS_MM3 else vol


def report(title, group_a, group_b, budget=None):
    """Intersect every pair across two groups.

    `budget` (mm^3 per pair, or None) marks an overlap the design accepts:
    it is reported but only fails when it exceeds the allowance.
    Returns (worst_volume, failures, accepted).
    """
    print(f"\n{title}")
    worst, failures, accepted = 0.0, [], []
    for la, sa in group_a:
        for lb, sb in group_b:
            vol = intersect_volume(sa, sb)
            if vol <= 0.0:
                continue
            worst = max(worst, vol)
            if budget is not None and vol <= budget:
                accepted.append(f"{la} x {lb}: {vol:.3f} mm^3")
                print(f"  ok    {la:<28} x {lb:<16} {vol:12.3f} mm^3 "
                      f"(within {budget:.0f} budget)")
            else:
                failures.append(f"{la} x {lb}: {vol:.3f} mm^3")
                print(f"  FOUL  {la:<28} x {lb:<16} {vol:12.3f} mm^3")
    if not failures and not accepted:
        print(f"  clear -- {len(group_a) * len(group_b)} pairs, no intersection")
    return worst, failures, accepted


def proud_report(shell, envelope):
    """Report wing material left standing proud inside each flange rebate.

    Protecting a keep-out on the hull means the rebate no longer shaves the
    skin there, so that material stands proud of the seat plane and the
    printed frame has to clear it.  This prints how far proud, and where the
    affected patch sits in the bay's own PLATE FRAME (u along ey, v along ez)
    so a cut-back can be written against `canonical_leg_r6_*.scad` in the
    coordinates that file actually uses.

    Port and starboard mirror in u, so |u| is reported and one rule covers
    both sides.
    """
    keep = mci.wing_keepout_positives(envelope)
    zb1 = mci.BAY_PLATE_ZB0 + mci.BAY_PLATE_L
    print("\nproud wing material inside the flange rebate (plate frame)")
    print(f"  footprint v {mci.BAY_PLATE_ZB0:.0f}..{zb1:.0f}, half-width "
          f"{mci.BAY_PLATE_WB / 2:.1f}..{mci.BAY_PLATE_W / 2:.1f}, "
          f"frame {mci.BAY_PLATE_T:.0f} mm thick")
    print(f"  upper bolt centres at |u| = {mci.BAY_BOLT_YB[1]:.1f}, "
          f"M3 clearance D{mci.LG_M3_D}")
    umin, vmin, worst = [], [], 0.0
    for label, hx, hy, hz, az, station in mci.LG_CORNERS:
        org, ex, ey, ez = mci._plate_frame(hx, hy, hz, az, station)
        meas = mci.seat_offset(shell, org, ex, ey, ez)
        if meas is None:
            continue
        org = org + ex * meas[1]
        rebate = mci._plate_trap(
            org, ex, ey, ez,
            mci.BAY_PLATE_WB + 2 * mci.LG_FIT_CLR,
            mci.BAY_PLATE_W + 2 * mci.LG_FIT_CLR,
            mci.BAY_PLATE_ZB0 - mci.LG_FIT_CLR, zb1 + mci.LG_FIT_CLR,
            0.0, 12.0)
        for klabel, k in keep:
            if ((rebate.bounds[0] > k.bounds[1]).any()
                    or (k.bounds[0] > rebate.bounds[1]).any()):
                continue
            inter = mci.from_man(mci.to_man(rebate) ^ mci.to_man(k))
            if len(inter.faces) == 0:
                continue
            d = inter.vertices - org
            u, v = np.abs(d @ ey), d @ ez
            with np.errstate(divide="ignore", invalid="ignore"):
                vol = abs(float(inter.volume))
            depth = float((d @ ex).max())
            worst = max(worst, depth)
            umin.append(float(u.min()))
            vmin.append(float(v.min()))
            print(f"  {label:<10} x {klabel:<16} proud {depth:6.3f} mm  "
                  f"vol {vol:7.2f} mm^3  |u| {u.min():.2f}..{u.max():.2f}  "
                  f"v {v.min():+.2f}..{v.max():+.2f}")
    if not umin:
        print("  none -- the rebate shaves the whole footprint")
        return
    print(f"\n  worst proud {worst:.3f} mm vs {mci.BAY_PLATE_T:.0f} mm frame "
          f"thickness -> a pocket cannot absorb it")
    print(f"  affected patch starts at |u| {min(umin):.2f}, v {min(vmin):+.2f}")
    if min(umin) < mci.BAY_BOLT_YB[1] + mci.LG_M3_D / 2.0:
        print(f"  WARNING: that reaches inboard of the upper bolt hole edge "
              f"(|u| {mci.BAY_BOLT_YB[1] + mci.LG_M3_D / 2.0:.2f}), so a flange "
              f"cut-back here would cost upper-bolt bearing")


def servo_pilot_bores():
    """The nacelle-servo M3 heat-set pilots, which nothing may break into."""
    out = []
    spans = ((mci.PORT_INB, mci.PORT_INB + 8.0),
             (mci.STBD_INB, mci.STBD_INB - 8.0))
    for n, (x_in, x_out) in enumerate(spans):
        for dy in (-mci.NSVMT_HOLE_S_Y, mci.NSVMT_HOLE_S_Y):
            for dz in (-mci.NSVMT_HOLE_S_Z, mci.NSVMT_HOLE_S_Z):
                side = "port" if n == 0 else "stbd"
                out.append((f"pilot {side} {dy:+.0f},{dz:+.0f}", mci.x_cylinder(
                    mci.NSVMT_Y + dy, mci.NSVMT_Z + dz,
                    min(x_in, x_out), max(x_in, x_out), mci.NSVMT_M3_D / 2.0)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--shell", default=CARGO_STL,
                    help="cargo shell STL the bays are seated on")
    ap.add_argument("--proud", action="store_true",
                    help="also report wing material left proud in the rebate")
    ap.add_argument("--spar-station", type=float, default=None,
                    help="try a candidate spar station, mm aft of the root LE "
                         "(WING_LE_ROOT_Y); overrides the module's 30%% chord")
    args = ap.parse_args()

    if not os.path.exists(args.shell):
        sys.exit(f"missing cargo shell: {args.shell}")

    if args.spar_station is not None:
        # Candidate-station sweep for the wings SS1.1.2 spar-interface blocker.
        # The bore, both bearing bosses and the keep-outs all derive from
        # WING_SPAR_Y, so moving it here moves every dependent solid coherently.
        was = mci.WING_SPAR_Y
        mci.WING_SPAR_Y = mci.WING_LE_ROOT_Y + args.spar_station
        print(f"  CANDIDATE spar station {args.spar_station:.2f} mm aft of LE "
              f"({args.spar_station / 129.0:.1%} root chord): "
              f"WING_SPAR_Y {was:+.2f} -> {mci.WING_SPAR_Y:+.2f}")

    print("LG-10.4 wing clearance -- Rev R6 gear bay vs wing-root structure")
    print(f"  shell   : {os.path.relpath(args.shell, REPO_ROOT)}")
    # The spar rides the camber midline (WING_SPAR_Z); WING_ROOT_Z is the
    # mortise height and is NOT where the spar sits -- they were the same
    # number before Rev S1b, which is exactly how the two got conflated.
    print(f"  spar    : bore D{mci.WING_SPAR_BORE_D} / boss D"
          f"{mci.WING_SPAR_BOSS_OD} at Y {mci.WING_SPAR_Y:+.1f}, "
          f"Z {mci.WING_SPAR_Z:.2f}")
    print(f"  mortise : {mci.MORT_W} x {mci.MORT_H} at Y "
          f"{mci.WING_MORT_Y:+.1f}, Z {mci.WING_ROOT_Z:.1f}")

    shell = trimesh.load(args.shell)
    envelope = mci.extract_envelope(shell)
    print(f"  envelope: {len(envelope.faces):,} faces, "
          f"watertight={envelope.is_watertight}")

    def wing_positives():
        return mci.wing_keepout_positives(envelope)

    pos, neg, note = mci.lg_bay_features(shell, envelope)
    print(f"  bay     : {note.splitlines()[0]}")
    if not pos and not neg:
        sys.exit("lg_bay_features returned nothing -- is LG_BAY_ENABLED False?")

    # lg_bay_features emits, per corner in LG_CORNERS order: 1 seat collar,
    # then the aperture, the flange rebate and 4 M3 bores.
    corners = [c[0] for c in mci.LG_CORNERS]
    per_corner = len(neg) // len(corners)
    bay_pos = [(f"collar {corners[i]}", s) for i, s in enumerate(pos)]
    bay_cuts, bay_bores = [], []
    for i, s in enumerate(neg):
        c, k = divmod(i, per_corner)
        if k == 0:
            bay_cuts.append((f"{corners[c]} aperture", s))
        elif k == 1:
            bay_cuts.append((f"{corners[c]} rebate", s))
        else:
            bay_bores.append((f"{corners[c]} bolt{k - 1}", s))

    w1, f1, _ = report(
        "1. bay aperture/rebate vs wing material (bay eating the wing mount)",
        bay_cuts, wing_positives())
    w2, f2, _ = report(
        "2. bay material vs wing voids (bay blocking the spar rod / root tenon)",
        bay_pos, wing_negatives())
    w3, f3, acc = report(
        "3. bay bolt bores vs wing material (accepted pad nick, budgeted)",
        bay_bores, wing_positives(), budget=BORE_PAD_BUDGET_MM3)
    w4, f4, _ = report(
        "4. bay bolt bores vs servo M3 pilot bores (no allowance)",
        bay_bores, servo_pilot_bores())

    if args.proud:
        proud_report(shell, envelope)

    print()
    failures = f1 + f2 + f3 + f4
    if acc:
        print(f"  {len(acc)} accepted pad nick(s), worst {w3:.3f} mm^3 "
              f"of the {BORE_PAD_BUDGET_MM3:.0f} mm^3 budget")
    if failures:
        print(f"  INTERFERES -- {len(failures)} fouling pair(s), "
              f"worst {max(w1, w2, w3, w4):.3f} mm^3")
        sys.exit(1)
    print("  CLEAR -- LG-10.4 wing clearance satisfied")


if __name__ == "__main__":
    main()
