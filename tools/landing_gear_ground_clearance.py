#!/usr/bin/env python3
"""Serenity UAV -- minimum safe landing-gear leg length, and the gate that holds it.

WHAT THIS GUARDS
================
The nacelles tilt to vertical for every takeoff and landing.  In that attitude
the nozzle stack hangs BELOW the hull belly datum, and the landing gear is the
only thing holding it off the ground.  Three separate subsystems can move that
number without anyone noticing:

  * the nacelle mass roll-up (``tools/nacelle_mass_cg.py``) -- the tilt pivot IS
    the rotating-assembly CG, so every gram added or moved inside the pod
    lengthens or shortens the pivot-to-nozzle-tip arm one for one.  ``PIVOT_Z``
    has already moved 111.5 -> 105.8 -> 113.8 -> 107.5 across four corrections;
  * the nozzle stack itself (flap length, stator/inter-stage compression);
  * the landing gear (leg-frame length -> belly clearance).

``nacelle_mass_cg.py`` already reports the STATIC hover clearance and exits
non-zero when a variant strikes.  It is not enough, and that is why this tool
exists: a landing is not static.  This tool adds the four things a static
number leaves out --

  1. touchdown attitude / uneven ground (the nozzle sits OUTBOARD of the foot
     track, so roll costs clearance while pitch does not -- see ``worst_case``);
  2. the energy-absorption stroke (the hull settles into the gear on landing);
  3. robustness reserve against further ``PIVOT_Z`` movement;
  4. build and foot-compression tolerance,

-- and solves for the belly clearance, i.e. the LEG LENGTH, that keeps all four
positive at once.  It exits non-zero when the gear variant wired into
``airframe/FreeCAD-scripts/serenity_assembly.py`` does not meet it.

WHY LEG LENGTH IS THE FREE VARIABLE HERE
========================================
Since the 2026-08-09 LG-10.2 hip recess and the canonical-foot-spread
correction, BOTH leg variants run the same hip->foot moment arm
``R_H_BUILT = 80 mm`` (``tools/landing_gear_r6_sizing.py``).  The crash
dynamics -- wire schedule, plateau force, hull settle, peak deceleration, hip
moment, bay-bolt loads -- are therefore IDENTICAL in both, and in any
intermediate length built the same way.  Leg length buys belly clearance and
costs only printed leg-frame mass.  This tool asserts that invariant on import;
if a future revision re-couples ``R_H`` to leg length, the assertion fires and
the load-path conclusions in ``docs/LANDING_GEAR_ANALYSIS.md`` must be re-derived
per variant before this tool's answer means anything.

THE ATTITUDE MODEL
==================
Exact rigid-body treatment, not a hand-waved allowance.  For a ground plane
tilted by ``theta`` with horizontal downhill direction ``psi``, the plane's unit
normal is ``n = (-sin(theta)cos(psi), -sin(theta)sin(psi), cos(theta))``.  The
airframe rests on whichever foot minimises ``p . n`` (first contact); every other
point's clearance is ``(p - p_contact) . n``.  Sweeping ``psi`` over the full
circle finds the worst case without assuming which way the aircraft is leaning.

Two consequences fall out of the station table rather than out of a judgement
call, and both are worth stating because neither is obvious:

  * a ground SLOPE with all four feet planted costs nothing -- the feet define
    the plane and the airframe is rigid.  What costs is a tilt taken about a
    subset of the feet: touchdown on one corner first, or one foot in a hollow;
  * PITCH never costs nozzle clearance on this airframe.  Both nozzles project
    inside the wheelbase (hull Y 43.4 / 37.4, between feet at -31.8 and +137.5),
    so a nose-down or tail-down tilt puts them on the UPHILL side.  ROLL is the
    whole of the attitude penalty, because the nozzles sit ~73 mm OUTBOARD of
    the foot track.  Cost is ~1.30 mm per degree of roll.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-09-06, for plan
          docs/plans/2026-09-06-001-fix-minimum-safe-landing-gear-length-plan.md.
          Per repository AGENTS.md section 3 AI-attribution policy.
License : CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>

Design references (see REFERENCES.md):
  REF-CAD-003  QMx Official Serenity Blueprints Reference Pack (2007), Sheet 5
               "Ventral Surface Plan View" -- canonical bay/foot stations.
  REF-FAA-004  14 CFR Part 23 -- adopted engineering baseline only, NOT a
               compliance claim.  NOTE: the touchdown-attitude and limit
               descent-velocity cases below are PROJECT ASSUMPTIONS.  The Part 23
               ground-load section that would substantiate them is NOT yet
               verified to a section number, so none is asserted here
               (AGENTS.md section 4: never guess a section number).  Tracked as
               LG-27 in docs/LANDING_GEAR_ANALYSIS.md section 15.
"""

import argparse
import re
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import landing_gear_r6_sizing as lg      # noqa: E402
import nacelle_mass_cg as nac            # noqa: E402

# ---------------------------------------------------------------------------
# Invariants this tool's reasoning rests on.  Assert them rather than restate
# them, so a change upstream fails loudly instead of silently invalidating the
# answer.
# ---------------------------------------------------------------------------
assert lg.R_H_BUILT == 80.0, (
    "R_H_BUILT moved: the hip->foot arm is no longer shared between leg "
    "variants, so leg length now changes the crash dynamics and the "
    "'clearance is free' conclusion in this tool's docstring is void.  "
    "Re-derive docs/LANDING_GEAR_ANALYSIS.md section 4.7 per variant first.")
assert set(lg.LEG_VARIANTS) == {"1.5in", "3.0in"}, (
    "leg variant catalogue changed; update CATALOGUE below")

# ---------------------------------------------------------------------------
# Geometry -- hull frame (mm).  Belly datum Z = 0; ground plane at Z = -C for a
# leg of belly clearance C.
# ---------------------------------------------------------------------------

#: Canonical foot stations, docs/LANDING_GEAR_ANALYSIS.md section 2.2
#: (from [REF-CAD-003] Sheet 5, unified to one leg part per corner).
FEET_XY = {
    "fore-port": (-30.4, -31.8),
    "aft-port": (-21.6, 137.5),
    "fore-stbd": (-309.4, -31.8),
    "aft-stbd": (-318.2, 137.5),
}

#: Nacelle bake translation, copied from
#: airframe/FreeCAD-scripts/serenity_assembly.py T_BAKE (itself copied from
#: tools/bake_hull_frame.py, the single source of truth).  The bake rotation is
#: hull_x = x_local, hull_y = z_local, hull_z = -y_local, so a point on the duct
#: axis at nacelle-local Z maps to hull (T[0], Z + T[1], T[2]).
T_BAKE = {
    "port": (46.9999060, -63.9998720, 62.9998740),
    "stbd": (-385.0960040, -69.9998600, 64.9719300),
}

#: Stance, docs/LANDING_GEAR_ANALYSIS.md section 2.2 -- reported for the
#: tip-over check, not used in the clearance solve.
TRACK_MM = 288.0
WHEELBASE_MM = 170.0

#: The belly clearance of each printed leg variant.
CATALOGUE = {"1.5 in": 38.1, "3.0 in": 80.0}


def _active_variant() -> str:
    """Read which leg the assembly actually wires in, rather than restate it.

    This was a hard-coded constant with a comment pointing at
    `serenity_assembly.py`.  A gate whose input is a copy of the fact it is
    guarding does not guard anything: it goes on passing (or failing) after the
    assembly changes underneath it.  This project has been bitten by exactly that
    twice in one day — a cover built from a duplicated shell selector, and ESC
    parameters held in two files — so the fact is read from its source.
    """
    src = (HERE.parent / "airframe/FreeCAD-scripts/serenity_assembly.py"
           ).read_text(encoding="utf-8")
    found = set(re.findall(r"lg_r6_(\d_\din)_hull_legs\.stl", src))
    mapping = {"1_5in": "1.5 in", "3_0in": "3.0 in"}
    wired = {mapping[f] for f in found if f in mapping}
    if len(wired) != 1:
        raise RuntimeError(
            "serenity_assembly.py wires "
            f"{len(wired)} landing-gear variants ({sorted(wired) or 'none'}); "
            "this gate cannot tell which one is active")
    return wired.pop()


ACTIVE_VARIANT = _active_variant()

# ---------------------------------------------------------------------------
# The reserve budget.  Each term is a separate, named, arguable number -- that
# is the point.  A single lumped "margin" is what let a +0.07 mm result be
# reported as a pass.
# ---------------------------------------------------------------------------

#: Touchdown attitude / uneven-ground case, degrees.  PROJECT ASSUMPTION, owner
#: to confirm (LG-27).  Note this is deliberately NOT the gear's structural
#: +/-15 deg lateral case (docs/LANDING_GEAR_ANALYSIS.md section 1 requirement
#: 2): +/-15 deg costs 19.6 mm of nozzle clearance and no leg in the family can
#: pay it.  The two cases are different requirements on the same event -- the
#: gear must SURVIVE +/-15 deg; the nozzle must not be STRUCK at the attitude
#: the flight-control system is allowed to touch down at.  Splitting them is a
#: decision the owner has to make; 5 deg is this tool's default, not a finding.
ATTITUDE_DEG = 5.0

#: Hull settle at the spring pair's elastic limit -- the stroke an ORDINARY
#: landing actually uses, 3.51 J/leg at 350 N/leg on the shared R_H 80 lever
#: (tools/landing_gear_r6_sizing.py main(), SPRING schedule block).  Recomputed
#: here from those two numbers rather than copied, so it tracks them.
U_SPRING_LEG_J = 3.51
F_LEG_ELASTIC_N = 350.0
SETTLE_ELASTIC_MM = U_SPRING_LEG_J * 1000.0 / F_LEG_ELASTIC_N

#: Hull settle at FULL ductile-fuse stroke -- the survival case, reported but
#: NOT used to size the leg (see report()).  4 ft schedule, the adopted one.
SETTLE_DUCTILE_MM = 30.7

#: Reserve against further PIVOT_Z movement.  Sized from the observed history,
#: not invented: PIVOT_Z has been 111.5, 105.8, 113.8 and 107.5 -- a measured
#: swing of 8.0 mm across four corrections, every one of which was a correction
#: rather than a design change.  The arm moves one-for-one with the pivot, so
#: 8.0 mm of pivot uncertainty is 8.0 mm of clearance.
PIVOT_DRIFT_MM = 8.0

#: Build tolerance: print/assembly stack across bay, leg and foot, plus static
#: compression of the TPU 95A tread under stance load.  PROJECT ASSUMPTION
#: (LG-27) -- no coupon measurement exists for the tread yet.
BUILD_TOL_MM = 3.0


def reserve_mm() -> float:
    """Non-attitude reserve the nozzle tip must hold at first contact."""
    return SETTLE_ELASTIC_MM + PIVOT_DRIFT_MM + BUILD_TOL_MM


def nozzle_tips(pivot_z: float, flap_len: float) -> dict:
    """Hull-frame (x, y, z) of each nozzle tip with the nacelles VERTICAL.

    At 90 deg of tilt the rotating assembly has swung so the tip lies directly
    below the pivot: it keeps the pivot's hull x and y, and drops to the spar
    height less the pivot-to-tip arm.  90 deg is the worst tilt angle -- by
    140 deg the tip has risen to 0.643x the arm (plan 003 R12).
    """
    arm = nac.tip_reach(flap_len) - pivot_z
    out = {}
    for side, t in T_BAKE.items():
        out[side] = (t[0], pivot_z + t[1], nac.WING_SPAR_HULL_Z - arm)
    return out


def worst_case(clearance_mm: float, tips: dict, theta_deg: float,
               steps: int = 720) -> tuple:
    """Worst nozzle clearance over every touchdown-attitude azimuth.

    Returns (clearance_mm, azimuth_deg, side, first_contact_foot).  Exact rigid-
    body model -- see the module docstring.  A full azimuth sweep is used rather
    than assuming pure roll, because which foot touches first is itself a
    function of azimuth and hard-coding it is how a case gets missed.
    """
    th = math.radians(theta_deg)
    sin_t, cos_t = math.sin(th), math.cos(th)
    worst = None
    for i in range(steps):
        psi = 2.0 * math.pi * i / steps
        n = (-sin_t * math.cos(psi), -sin_t * math.sin(psi), cos_t)
        contact = min(
            ((x * n[0] + y * n[1] + (-clearance_mm) * n[2], name)
             for name, (x, y) in FEET_XY.items()),
            key=lambda pair: pair[0])
        for side, (x, y, z) in tips.items():
            clr = x * n[0] + y * n[1] + z * n[2] - contact[0]
            if worst is None or clr < worst[0]:
                worst = (clr, math.degrees(psi), side, contact[1])
    return worst


def solve_min_clearance(tips: dict, theta_deg: float, target_mm: float,
                        lo: float = 0.0, hi: float = 400.0) -> float:
    """Smallest belly clearance whose worst-case nozzle clearance >= target.

    Bisection rather than algebra: ``worst_case`` is a min over a sweep, and
    solving it in closed form would mean assuming which foot and which azimuth
    govern.  The function is monotonic in clearance (the ground only moves
    down), so bisection is exact to the tolerance below.
    """
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if worst_case(mid, tips, theta_deg, steps=180)[0] < target_mm:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-4:
            break
    return hi


def report(flap_len: float, theta_deg: float) -> int:
    """Print the budget and return a process exit status."""
    roll = nac.roll_up(flap_len)
    if roll["problems"]:
        print("Nacelle mass roll-up is INCOMPLETE -- clearance cannot be "
              "trusted:", file=sys.stderr)
        for p in roll["problems"]:
            print(f"  ! {p}", file=sys.stderr)
        return 2
    pivot = roll["cg_z_mm"]
    tips = nozzle_tips(pivot, flap_len)
    depth = -tips["port"][2]
    res = reserve_mm()

    print("=" * 78)
    print("Serenity UAV -- minimum safe landing-gear leg length "
          "(hover nozzle clearance)")
    print("=" * 78)
    print(f"Nacelles VERTICAL (90 deg, worst tilt).  Flap length {flap_len:.0f} mm, "
          f"PIVOT_Z {pivot:.2f} mm")
    print(f"Pivot-to-tip arm {nac.tip_reach(flap_len) - pivot:.1f} mm; spar at "
          f"hull Z {nac.WING_SPAR_HULL_Z:+.2f}")
    print(f"Nozzle tip hull Z {tips['port'][2]:+.2f} -> hangs {depth:.2f} mm "
          f"below the belly datum")
    print(f"Nozzle ground projections: port ({tips['port'][0]:.1f}, "
          f"{tips['port'][1]:.1f}), stbd ({tips['stbd'][0]:.1f}, "
          f"{tips['stbd'][1]:.1f})")
    print(f"Stance: track {TRACK_MM:.0f} mm, wheelbase {WHEELBASE_MM:.0f} mm; "
          f"nozzles lie INSIDE the wheelbase and ~73 mm OUTBOARD of the track")

    print("\n--- Reserve budget (what the tip must still hold at first contact) ---")
    print(f"  hull settle, spring elastic limit ({U_SPRING_LEG_J:.2f} J/leg at "
          f"{F_LEG_ELASTIC_N:.0f} N/leg)   {SETTLE_ELASTIC_MM:6.2f} mm")
    print(f"  PIVOT_Z drift reserve (observed 111.5/105.8/113.8/107.5)      "
          f"{PIVOT_DRIFT_MM:6.2f} mm")
    print(f"  build + TPU tread compression tolerance                       "
          f"{BUILD_TOL_MM:6.2f} mm")
    print(f"  {'':62s}{'-' * 9}")
    print(f"  reserve required                                              "
          f"{res:6.2f} mm")
    print(f"  touchdown attitude / uneven ground                            "
          f"{theta_deg:6.2f} deg")

    c_min = solve_min_clearance(tips, theta_deg, res)
    print(f"\n=> MINIMUM SAFE BELLY CLEARANCE  {c_min:.2f} mm "
          f"({c_min / 25.4:.2f} in)")
    print(f"   Static-only (attitude 0, no reserve) would read "
          f"{depth:.2f} mm -- {c_min - depth:.2f} mm optimistic.")

    print("\n--- Leg catalogue ---")
    status = 0
    for name, c in sorted(CATALOGUE.items(), key=lambda kv: kv[1]):
        static = worst_case(c, tips, 0.0)[0]
        w, psi, side, foot = worst_case(c, tips, theta_deg)
        surplus = w - res
        tag = "ACTIVE" if name == ACTIVE_VARIANT else "      "
        verdict = "MEETS MINIMUM" if surplus >= 0.0 else "*** BELOW MINIMUM ***"
        if surplus < 0.0 and name == ACTIVE_VARIANT:
            status = 2
        print(f"  {name:8s} {tag}  C {c:5.1f} mm: static {static:+7.2f}, "
              f"at {theta_deg:.0f} deg {w:+7.2f} "
              f"(worst az {psi:5.1f} deg, {side}, first contact {foot})")
        print(f"  {'':24s}surplus over reserve {surplus:+7.2f} mm  {verdict}")

    print("\n--- Attitude sensitivity (cost of roll, at each catalogue leg) ---")
    hdr = "  theta deg  " + "".join(f"{n:>12s}" for n, _ in
                                    sorted(CATALOGUE.items(), key=lambda kv: kv[1]))
    print(hdr)
    for t in (0.0, 2.0, 5.0, 8.0, 10.0, 15.0):
        row = f"  {t:9.1f}  "
        for _, c in sorted(CATALOGUE.items(), key=lambda kv: kv[1]):
            row += f"{worst_case(c, tips, t)[0] - res:12.2f}"
        print(row)
    print("  (surplus over the reserve budget, mm.  15 deg is the gear's "
          "STRUCTURAL lateral case,")
    print("   not a nozzle-clearance case -- see ATTITUDE_DEG in this file.)")

    print("\n--- Survival case (NOT a sizing case) ---")
    c_full = solve_min_clearance(tips, theta_deg, res - SETTLE_ELASTIC_MM
                                 + SETTLE_DUCTILE_MM)
    print(f"  A full ductile-fuse arrest settles the hull {SETTLE_DUCTILE_MM:.1f} mm "
          f"(4 ft schedule, both variants).")
    print(f"  Clearing the nozzle through that stroke as well would need "
          f"{c_full:.2f} mm ({c_full / 25.4:.2f} in).")
    print("  This is a crash case: the fuse has fired and the wires are "
          "scrap.  Sizing the leg to it")
    print("  is an owner decision (LG-28); the flaps are sacrificial and "
          "cheaper than the leg.")

    if status:
        print(f"\nFAIL: the ACTIVE gear variant ({ACTIVE_VARIANT}) is below the "
              f"minimum safe length.")
    else:
        print(f"\nPASS: the ACTIVE gear variant ({ACTIVE_VARIANT}) meets the "
              f"minimum safe length.")
    return status


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--flap", type=float, default=nac.BUILT_FLAP_LEN,
                    help="nozzle flap length mm (built: "
                         f"{nac.BUILT_FLAP_LEN:.0f}; plan 005 R1 proposes 30)")
    ap.add_argument("--attitude", type=float, default=ATTITUDE_DEG,
                    help="touchdown attitude / uneven-ground case, degrees "
                         f"(default {ATTITUDE_DEG:.0f})")
    args = ap.parse_args()
    return report(args.flap, args.attitude)


if __name__ == "__main__":
    sys.exit(main())
