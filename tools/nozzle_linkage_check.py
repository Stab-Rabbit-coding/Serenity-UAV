#!/usr/bin/env python3
"""Nozzle pushrod (RSSR) linkage reachability check.

Closes OQ2 / plan `docs/plans/2026-08-29-005-nacelle-mould-line-conformance-
plan.md`, Unit U2: "the RSSR pushrod linkage (nacelle_nozzle_pushrod.scad)
stays monotonic and non-locking across the 0-90 deg tilt range".  That file's
own header (lines 49-64, as of this writing) flags the crank/pushrod/ring
geometry as first-pass, VERIFY, "do NOT print for flight hardware until
closed" -- this script is the reusable, re-runnable closure the plan's
session-settled decision calls for (a script, not a one-off manual FreeCAD
pass; see the plan's Planning Contract, "RSSR linkage re-verification").

THE LINKAGE (spatial RSSR: revolute-spherical-spherical-revolute)
------------------------------------------------------------------
As the nacelle tilts theta = 0 -> 90 deg about the fixed spar axis (nacelle-
local X, which stays hull X under bake -- see
`tools/landing_gear_ground_clearance.py` T_BAKE comment: "hull_x = x_local"),
a crank clamped to that same spar carries a ball stud at radius CRANK_R.  A
pushrod of fixed length PUSHROD_LEN connects that crank ball to a ball on the
unison_ring()'s lever ear, at radius RING_LEVER_R and azimuth RING_LEVER_AZ
(measured about the ring's own rotation axis, nacelle-local Z, i.e. the duct
axis) plus the ring's own extra rotation psi.  psi is exactly what the ring's
cam mechanism uses to sweep the flaps between NOZZLE_CLOSED_R and
NOZZLE_OPEN_R (nacelle_nozzle_iris.scad).

For every tilt angle theta this script root-finds the ring angle psi that
makes the crank-ball-to-ring-ball distance equal PUSHROD_LEN (the pushrod is
rigid), then checks, marching theta from 0 to 90 deg:
  1. REACHABILITY -- a real root for psi exists at every sampled theta
     (no root = the rod cannot bridge the two balls at that tilt = locking).
  2. MONOTONICITY -- psi(theta) does not reverse direction (a reversal means
     the ring would have to un-rotate partway through the tilt sweep, which
     the ring's own one-way cam/flap kinematics cannot follow).
  3. SPAN -- the psi range actually swept lands close to the ring's required
     0 -> THETA_RING_REF_OPEN (23.75 deg) design target (nacelle_nozzle_
     iris.scad THETA_RING_REF_OPEN) within SPAN_TOL_DEG.

COORDINATE MODEL (see the plan's U2 section, "What solving the linkage
means", for the full derivation this implements)
------------------------------------------------------------------------
Work in a hull-frame-oriented basis centred on the pivot, reusing the tilt
convention already established by `tools/landing_gear_ground_clearance.py`
(T_BAKE comment) and `tools/nacelle_mass_cg.py` (`tip_reach()` /
`nozzle_tips()`): nacelle-local X is the (unrotated) spar/tilt axis; at
theta = 0 (the baked/cruise reference pose) nacelle-local Z (the duct axis)
maps to hull +Y and nacelle-local Y maps to hull -Z.  Tilting by theta is a
rotation about hull X that carries local Z (Y=0,Z=+1) to hull
(0, cos(theta), -sin(theta)) at theta = 90 deg giving hull -Z ("the tip lies
directly below the pivot", `nozzle_tips()` docstring) -- consistent with
that script's simplified 90 deg-only case, generalised here to all theta.

  duct axis (local Z) in hull frame:      (0,  cos(theta), -sin(theta))
  local Y axis in hull frame:             (0, -sin(theta), -cos(theta))
  local X axis (spar/tilt axis) in hull frame:  (1, 0, 0)  -- unrotated

Ring ball (nacelle-body-fixed ring lever, offset AXIAL_OFFSET along the duct
axis from the pivot, RING_LEVER_R radially at azimuth RING_LEVER_AZ + psi in
the plane perpendicular to the duct axis -- i.e. spanned by local X and
local Y):

  hull_ring = AXIAL_OFFSET * duct_axis(theta)
            + RING_LEVER_R * cos(az + psi) * local_X
            + RING_LEVER_R * sin(az + psi) * local_Y(theta)

Crank ball: clamped directly to the spar, so its angular position in the
hull frame IS the tilt angle plus a fixed mounting phase (CRANK_PHASE_DEG):
it is a point at radius CRANK_R in the hull Y-Z plane (the plane
perpendicular to the spar axis), at angle (theta + CRANK_PHASE_DEG), and at
some fixed axial (hull-X) station CRANK_AXIAL_X along the spar:

  hull_crank = (CRANK_AXIAL_X,
                CRANK_R * cos(theta + CRANK_PHASE_DEG),
                CRANK_R * sin(theta + CRANK_PHASE_DEG))

ASSUMPTIONS (explicit, per the plan's instruction to state these rather than
invent them silently)
------------------------------------------------------------------------
* CRANK_PHASE_DEG (the crank's mounting angle on the spar at theta = 0) and
  CRANK_AXIAL_X (where along the spar the crank sits) are NOT pinned by any
  source file -- `nacelle_nozzle_pushrod.scad` gives the crank's own
  part-local print frame but not its placement relative to the ring, and
  says the "EXACT crank radius, ball 3-D positions, and rod length ... MUST
  be solved with a kinematic study" (its own header).  This script therefore
  treats both as free ASSEMBLY parameters and grid-searches them (a coarse
  synthesis pass), exactly the kind of check the plan's session-settled
  decision asks for -- it does NOT adjust CRANK_R or PUSHROD_LEN themselves,
  which are the pinned SCAD constants under test.
* FLAP_LENGTH does not enter this model.  `nacelle_nozzle_iris.scad` fixes
  THETA_RING_REF_OPEN = 23.75 deg as a hard constant (line ~410, "ring stroke
  over 0->90 deg tilt (linkage-set)") independent of FLAP_LENGTH -- the cam
  follower geometry (TAB_X/TAB_Z, solved from PIN_R_REF_CLOSED/OPEN, which
  are also FLAP_LENGTH-independent) re-solves so that whatever flap length is
  chosen, the SAME ring stroke 0 -> 23.75 deg still produces the required
  NOZZLE_CLOSED_R/OPEN_R exit radii.  So the pushrod-to-ring reachability
  problem this script solves is, by the source geometry's own design,
  identical for FLAP_LENGTH = 30 and FLAP_LENGTH = 40 -- the `--flap-length`
  flag is retained (per the unit spec) to report the derived PHI_CLOSED/
  PHI_OPEN for context and to keep the CLI symmetrical with the rest of the
  U1/U2 pipeline, but it is not wired into the psi solve.  This is verified,
  not assumed -- see the header derivation above and nacelle_nozzle_iris.scad
  lines 403-410.  Because of this, the synthetic-failure demonstration this
  script's own test harness needs (proving the check can actually fail, not
  just always pass) uses `--pushrod-len` instead of an unrealistic flap
  length, per the unit spec's explicit alternative ("or an unrealistic
  PUSHROD_LEN").

Source-of-truth constants (each copied here, not re-derived, per this
repo's `tools/landing_gear_ground_clearance.py` provenance-comment
convention):
  CRANK_R              airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad:89
  PUSHROD_LEN          airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad:97
  RING_LEVER_AZ        airframe/openscad/nacelles/nacelle_nozzle_iris.scad:499
  RING_LEVER_R         airframe/openscad/nacelles/nacelle_nozzle_iris.scad:501
  RING_H               airframe/openscad/nacelles/nacelle_nozzle_iris.scad:489
                       (ring ball Z = RING_H / 2, unison_ring() ball socket,
                       ~line 705: translate([RING_LEVER_R, 0, RING_H / 2]))
  THETA_RING_REF_OPEN  airframe/openscad/nacelles/nacelle_nozzle_iris.scad:410
  R_HINGE / NOZZLE_*_R airframe/openscad/nacelles/nacelle_nozzle_iris.scad:307-310
  NOZZLE_RING_Z        airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad:347
  PIVOT_Z              airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad:437

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CEH
License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
Date:    2026-09-08
AI contribution: Claude (Sonnet 5, Anthropic), directed by Steve Griffing.
"""

from __future__ import annotations

import argparse
import math
import sys

# ── Source-of-truth constants (see module docstring for file:line) ─────────
CRANK_R = 8.5                    # [mm] nacelle_nozzle_pushrod.scad:89
PUSHROD_LEN_NOMINAL = 45.0       # [mm] nacelle_nozzle_pushrod.scad:97

RING_LEVER_AZ_DEG = 22.5         # [deg] nacelle_nozzle_iris.scad:499
RING_LEVER_R = 32.0              # [mm] nacelle_nozzle_iris.scad:501
RING_H = 8.0                     # [mm] nacelle_nozzle_iris.scad:489
RING_BALL_Z = RING_H / 2.0       # [mm] unison_ring() ball socket, ~line 705

THETA_RING_REF_OPEN_DEG = 23.75  # [deg] nacelle_nozzle_iris.scad:410 -- FIXED
                                  #   ring-stroke target, independent of
                                  #   FLAP_LENGTH (see module docstring).

R_HINGE = 27.5                   # [mm] nacelle_nozzle_iris.scad THROAT_OUTER_R
NOZZLE_CLOSED_R = 18.75          # [mm] nacelle_nozzle_iris.scad:309
NOZZLE_OPEN_R = 26.25            # [mm] nacelle_nozzle_iris.scad:310

NOZZLE_RING_Z = 166.25           # [mm] nacelle_pod_50mm_tandem.scad:347
PIVOT_Z = 107.5                  # [mm] nacelle_pod_50mm_tandem.scad:437

# Axial offset of the ring ball from the pivot, along the (pre-tilt) duct
# axis: the ring's own local Z = 0 lands at the pod's NOZZLE_RING_Z station
# (unison_ring() is instantiated with no additional Z translate in the
# "asm" render path, nacelle_nozzle_iris.scad ~line 847), and the ball sits
# RING_BALL_Z further along the ring's own axis.
AXIAL_OFFSET = (NOZZLE_RING_Z + RING_BALL_Z) - PIVOT_Z   # [mm] = 62.75

# ── Free assembly parameters (NOT pinned by source -- see ASSUMPTIONS) ─────
# Grid searched, not fudged: these represent where/how the crank is clamped
# on the spar, a synthesis choice this script makes explicit rather than
# inventing a single unjustified number.
CRANK_PHASE_GRID_DEG = [i * 5.0 for i in range(0, 360, 5)]   # 0..355 step 5
CRANK_AXIAL_X_GRID = [0.0, 20.0, 40.0]        # [mm] candidate spar stations

SPAN_TOL_DEG = 5.0        # [deg] allowed deviation of psi(0)/psi(90) from
                           # the 0 / THETA_RING_REF_OPEN design target before
                           # a reachable, monotonic solution is still marked
                           # a span mismatch.
PSI_SEARCH_LO_DEG = -90.0
PSI_SEARCH_HI_DEG = 90.0
PSI_SCAN_STEPS = 360       # coarse bracket scan resolution (0.5 deg/step)
BISECT_ITERS = 50


def phi_closed_open_deg(flap_length: float) -> tuple[float, float]:
    """Derived flap swing angles for context/reporting only (see ASSUMPTIONS:
    not used in the pushrod/ring reachability solve).

    phi(exit_r) = asin((R_HINGE - exit_r) / FLAP_LENGTH) --
    nacelle_nozzle_iris.scad line ~337.
    """
    phi_closed = math.degrees(math.asin((R_HINGE - NOZZLE_CLOSED_R) / flap_length))
    phi_open = math.degrees(math.asin((R_HINGE - NOZZLE_OPEN_R) / flap_length))
    return phi_closed, phi_open


def crank_ball(theta_deg: float, phase_deg: float, axial_x: float) -> tuple[float, float, float]:
    """Hull-frame position of the crank ball, relative to the pivot."""
    ang = math.radians(theta_deg + phase_deg)
    return (axial_x, CRANK_R * math.cos(ang), CRANK_R * math.sin(ang))


def ring_ball(theta_deg: float, psi_deg: float) -> tuple[float, float, float]:
    """Hull-frame position of the ring lever ball, relative to the pivot."""
    theta = math.radians(theta_deg)
    az = math.radians(RING_LEVER_AZ_DEG + psi_deg)
    cos_a, sin_a = math.cos(az), math.sin(az)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    x = RING_LEVER_R * cos_a
    y = AXIAL_OFFSET * cos_t - RING_LEVER_R * sin_a * sin_t
    z = -AXIAL_OFFSET * sin_t - RING_LEVER_R * sin_a * cos_t
    return (x, y, z)


def rod_len(theta_deg: float, psi_deg: float, phase_deg: float, axial_x: float) -> float:
    cx, cy, cz = crank_ball(theta_deg, phase_deg, axial_x)
    rx, ry, rz = ring_ball(theta_deg, psi_deg)
    return math.sqrt((rx - cx) ** 2 + (ry - cy) ** 2 + (rz - cz) ** 2)


def solve_psi(theta_deg: float, phase_deg: float, axial_x: float,
              pushrod_len: float, psi_prev: float | None) -> float | None:
    """Root-find psi such that rod_len(theta, psi) == pushrod_len.

    Scans PSI_SCAN_STEPS brackets over [PSI_SEARCH_LO_DEG, PSI_SEARCH_HI_DEG]
    for sign changes, bisects each to convergence, then returns the root
    closest to `psi_prev` (continuity tracking) or, if this is the first
    theta sample, the root closest to 0.  Returns None if no root exists
    anywhere in the search range (the rod cannot bridge the two balls at
    this tilt -- a locking condition).
    """
    def f(psi: float) -> float:
        return rod_len(theta_deg, psi, phase_deg, axial_x) - pushrod_len

    lo, hi = PSI_SEARCH_LO_DEG, PSI_SEARCH_HI_DEG
    n = PSI_SCAN_STEPS
    step = (hi - lo) / n
    psis = [lo + i * step for i in range(n + 1)]
    vals = [f(p) for p in psis]

    roots: list[float] = []
    for i in range(n):
        fa, fb = vals[i], vals[i + 1]
        if fa == 0.0:
            roots.append(psis[i])
            continue
        if fa * fb < 0.0:
            a, b = psis[i], psis[i + 1]
            fa_b = fa
            for _ in range(BISECT_ITERS):
                m = (a + b) / 2.0
                fm = f(m)
                if fa_b * fm <= 0.0:
                    b = m
                else:
                    a, fa_b = m, fm
            roots.append((a + b) / 2.0)
    if vals[-1] == 0.0:
        roots.append(psis[-1])

    if not roots:
        return None
    target = psi_prev if psi_prev is not None else 0.0
    return min(roots, key=lambda r: abs(r - target))


def sweep(phase_deg: float, axial_x: float, pushrod_len: float,
          theta_step_deg: float = 1.0) -> dict:
    """Sweep tilt 0 -> 90 deg, solving psi(theta) at each step.

    Returns a report dict: reachable (bool), monotonic (bool),
    span_ok (bool), thetas, psis, and (on failure) the offending tilt angle.
    """
    n_steps = int(round(90.0 / theta_step_deg))
    thetas = [i * theta_step_deg for i in range(n_steps + 1)]
    psis: list[float] = []
    psi_prev: float | None = None

    for theta in thetas:
        psi = solve_psi(theta, phase_deg, axial_x, pushrod_len, psi_prev)
        if psi is None:
            return {
                "reachable": False, "monotonic": None, "span_ok": None,
                "ok": False, "fail_theta": theta,
                "thetas": thetas, "psis": psis,
            }
        psis.append(psi)
        psi_prev = psi

    direction = 1.0 if psis[-1] >= psis[0] else -1.0
    monotonic = True
    bad_theta = None
    for i in range(len(psis) - 1):
        d = psis[i + 1] - psis[i]
        if direction * d < -1e-4:
            monotonic = False
            bad_theta = thetas[i + 1]
            break

    span_lo_err = abs(psis[0] - 0.0)
    span_hi_err = abs(psis[-1] - THETA_RING_REF_OPEN_DEG)
    span_ok = span_lo_err <= SPAN_TOL_DEG and span_hi_err <= SPAN_TOL_DEG

    return {
        "reachable": True, "monotonic": monotonic, "span_ok": span_ok,
        "ok": monotonic and span_ok, "fail_theta": bad_theta,
        "thetas": thetas, "psis": psis,
        "span_lo_err": span_lo_err, "span_hi_err": span_hi_err,
    }


def synthesize(pushrod_len: float, theta_step_deg: float = 1.0) -> tuple[dict, float, float]:
    """Grid-search CRANK_PHASE_GRID_DEG x CRANK_AXIAL_X_GRID for the best
    (or first fully-passing) assembly phase/axial-station combination.

    Returns (best_result, best_phase_deg, best_axial_x).
    """
    best_result = None
    best_phase = None
    best_axial = None
    best_score = None

    for axial_x in CRANK_AXIAL_X_GRID:
        for phase in CRANK_PHASE_GRID_DEG:
            result = sweep(phase, axial_x, pushrod_len, theta_step_deg)
            if result["ok"]:
                return result, phase, axial_x
            # Score non-passing candidates so we can report the closest miss.
            if not result["reachable"]:
                score = 1e6 - result["fail_theta"]  # prefer failing later
            elif not result["monotonic"]:
                score = 1e4 - (result["fail_theta"] or 0.0)
            else:
                score = result["span_lo_err"] + result["span_hi_err"]
            if best_score is None or score < best_score:
                best_score = score
                best_result = result
                best_phase = phase
                best_axial = axial_x

    return best_result, best_phase, best_axial


def report(flap_length: float, pushrod_len: float, label: str) -> bool:
    """Run the search for one (flap_length, pushrod_len) case and print a
    report.  Returns True on PASS."""
    phi_closed, phi_open = phi_closed_open_deg(flap_length)
    result, phase, axial_x = synthesize(pushrod_len)

    print(f"\n=== {label}: FLAP_LENGTH={flap_length:.1f} mm, "
          f"PUSHROD_LEN={pushrod_len:.2f} mm ===")
    print(f"  (context only, not used in the solve) "
          f"PHI_CLOSED={phi_closed:.2f} deg, PHI_OPEN={phi_open:.2f} deg")
    print(f"  best assembly phase found: CRANK_PHASE={phase:.1f} deg, "
          f"CRANK_AXIAL_X={axial_x:.1f} mm")

    if not result["reachable"]:
        print(f"  FAIL: rod cannot reach at tilt {result['fail_theta']:.1f} deg "
              f"(no real root for psi over the full {PSI_SEARCH_LO_DEG:.0f}.."
              f"{PSI_SEARCH_HI_DEG:.0f} deg search range, for every "
              f"phase/axial-station candidate tried) -- LOCKING.")
        return False

    if not result["monotonic"]:
        print(f"  FAIL: psi(theta) reverses direction at tilt "
              f"{result['fail_theta']:.1f} deg (non-monotonic ring map) "
              f"for every phase/axial-station candidate tried.")
        return False

    psis = result["psis"]
    print(f"  reachable at all {len(result['thetas'])} sampled tilt angles "
          f"(0..90 deg, {result['thetas'][1] - result['thetas'][0]:.1f} deg step)")
    print(f"  monotonic: yes ({'increasing' if psis[-1] >= psis[0] else 'decreasing'})")
    print(f"  psi(0 deg)  = {psis[0]:+7.3f} deg  (target   0.00 deg, "
          f"err {result['span_lo_err']:.3f} deg)")
    print(f"  psi(90 deg) = {psis[-1]:+7.3f} deg  (target {THETA_RING_REF_OPEN_DEG:6.2f} deg, "
          f"err {result['span_hi_err']:.3f} deg)")

    if result["span_ok"]:
        print(f"  PASS: reachable, monotonic, span within +/-{SPAN_TOL_DEG:.1f} deg "
              f"of the 0..{THETA_RING_REF_OPEN_DEG:.2f} deg design target.")
        return True

    print(f"  FAIL: reachable and monotonic, but psi span misses the "
          f"0..{THETA_RING_REF_OPEN_DEG:.2f} deg design target by more than "
          f"+/-{SPAN_TOL_DEG:.1f} deg on at least one end -- the ring would "
          f"not reach one of NOZZLE_CLOSED_R/NOZZLE_OPEN_R.")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--flap-length", type=float, default=30.0,
                         help="[mm] FLAP_LENGTH, for report context only -- "
                              "does not affect the pushrod/ring solve; see "
                              "module docstring ASSUMPTIONS (default: 30.0, "
                              "the plan 005 R1 target).")
    parser.add_argument("--pushrod-len", type=float, default=PUSHROD_LEN_NOMINAL,
                         help="[mm] override PUSHROD_LEN for a synthetic "
                              "failure demonstration; NOT for tuning the "
                              "real result (default: the nominal SCAD value, "
                              f"{PUSHROD_LEN_NOMINAL:.1f} mm).")
    parser.add_argument("--label", type=str, default="run",
                         help="label for the printed report section.")
    args = parser.parse_args()

    ok = report(args.flap_length, args.pushrod_len, args.label)
    print(f"\n{'PASS' if ok else 'FAIL'}: {args.label} "
          f"(FLAP_LENGTH={args.flap_length:.1f}, PUSHROD_LEN={args.pushrod_len:.2f})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
