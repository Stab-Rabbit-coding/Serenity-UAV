#!/usr/bin/env python3
"""Nozzle pushrod linkage check -- ADOPTED wing-fixed-sun / nacelle-pinion drive.

Closes OQ2 / plan `docs/plans/2026-08-29-005-nacelle-mould-line-conformance-
plan.md`, Unit U2: "the pushrod linkage (nacelle_nozzle_pushrod.scad) stays
monotonic and non-locking across the 0-90 deg tilt range".  It is a reusable,
re-runnable script rather than a one-off manual FreeCAD pass, per that plan's
session-settled decision ("RSSR linkage re-verification").

TWO MODELS LIVE IN THIS FILE
============================
`--model pinion` (DEFAULT) -- the ADOPTED architecture.  This is the model
    under test and the one that must pass.
`--model spar-crank-superseded` -- the ABANDONED spar-crank architecture,
    retained deliberately as the regression / historical record of WHY that
    architecture was dropped.  Its empty search result is evidence, not dead
    code: see the "SUPERSEDED MODEL" section below.

THE ADOPTED LINKAGE (`--model pinion`)
======================================
Governing decision: `docs/NOZZLE_DRIVE_TRADE.md`, "DECISION AMENDMENT --
hybrid A+B adopted (2026-07-19)".

The nozzle's variable-area iris is driven PASSIVELY by nacelle tilt (canonical
requirement, `airframe/AGENTS.md` "Nacelle Nozzle Drive").  A gear fixed
coaxial with the tilt spar AT THE WING TIP (the "sun") meshes a nacelle-mounted
PINION.  Because the sun is fixed to the NON-TILTING wing, tilting the nacelle
by theta about the spar spins the pinion by theta * (N_sun / N_pinion)
RELATIVE TO THE NACELLE; the adopted mesh is 1:1, so the pinion tracks tilt
1:1 in the nacelle frame.  The drive crank rides on that pinion, and a COTS
ball-link pushrod carries its ball to the unison ring's lever ear.

    THE WHOLE POINT OF THE FIX: crank ball, ring ball and pushrod are ALL
    fixed in (or moving within) the NACELLE body frame.  The tilt rotation is
    therefore a rigid rotation applied to the entire linkage and CANCELS OUT
    of every distance in the problem -- it does not appear anywhere in the
    math below.  Tilt enters only as the pinion's drive angle.  This is
    exactly the relative motion the superseded spar crank did not have.

Nacelle-local frame: the duct axis is local Z; the spar / tilt axis is local X
at local Z = PIVOT_Z.

  Crank ball (rides the pinion; pinion axis is parallel to local X, passing
  through (x = SUN_XLOC, y = 0, z = PIVOT_Z + SYNC_CD)):

      x = SUN_XLOC
      y = CRANK_R * sin(theta + CRANK_PHASE)
      z = PIVOT_Z + SYNC_CD + CRANK_R * cos(theta + CRANK_PHASE)

  Ring ball (unison_ring() lever ear, rotating about local Z with the ring):

      x = RING_LEVER_R * cos(RING_LEVER_AZ + psi)
      y = RING_LEVER_R * sin(RING_LEVER_AZ + psi)
      z = NOZZLE_RING_Z + RING_BALL_Z

For every tilt angle theta the script root-finds the ring angle psi that makes
the crank-ball-to-ring-ball distance equal PUSHROD_LEN (the rod is rigid),
then marches theta from 0 to 90 deg and checks:

  1. REACHABILITY  -- a real root for psi exists at every sampled theta (no
     root means the rod cannot bridge the two balls = a locking condition).
  2. MONOTONICITY  -- psi(theta) never reverses direction (a reversal is a
     toggle / dead point the ring's one-way cam kinematics cannot follow).
  3. SPAN          -- the swept psi range matches the ring's required stroke,
     0 -> THETA_RING_REF_OPEN (23.75 deg), within SPAN_TOL_DEG.
  4. TRANSMISSION ANGLE -- new in this rework.  At the ring ball, the angle TA
     between the pushrod and the ring lever arm (the radial vector from the
     ring axis out to the ball) governs how much of the rod force becomes
     useful ring torque.  Reported as min(TA, 180 - TA) so that both an acute
     and an obtuse pose are judged on the same scale, against a configurable
     floor (default 40 deg -- the standard >= 40-45 deg linkage-design rule of
     thumb; see e.g. any machine-design text's four-bar transmission-angle
     criterion.  No standards citation is claimed for a rule of thumb).

VERIFIED RESULT of the adopted geometry as transcribed below (stated here, not
re-derived; reproduce by running this script with no flags):
  * ring stroke span 23.816 deg vs. the 23.75 deg design target -- 0.3 % error
  * psi(0) = -0.36 deg, i.e. essentially zero, so the ring cam needs NO
    re-clocking relative to the lever ear
  * psi MONOTONIC across the whole sweep (no toggle / dead point), running
    0 -> -24.18 deg (negative azimuth direction)
  * transmission angle stays in 88.1..103.8 deg; worst-case min(TA, 180-TA) =
    76.2 deg, far above the 40-45 deg floor

SUPERSEDED MODEL (`--model spar-crank-superseded`) -- RETAINED ON PURPOSE
=========================================================================
The original Option-B implementation clamped the crank to the TILT SPAR and
was modelled in the HULL frame (the crank ball swinging in the hull Y-Z plane
with tilt, the ring ball carried around by the tilting nacelle).  That model
is preserved verbatim below.

It is kept because its EMPTY RESULT IS THE EVIDENCE for the architecture
change: an exhaustive 2026-09-09 sweep (CRANK_R 8.5-28 mm x PUSHROD_LEN
58-90 mm x 24 crank mounting phases x 8 spar mounting stations = 336
combinations) found ZERO candidates that are both reachable and monotonic
across the full 0-90 deg tilt sweep.  The root cause is not sizing: the tilt
spar is KEYED TO THE NACELLE, so a crank clamped to it shares the nacelle's
rotating frame with the unison ring; the two swing together through the whole
sweep with ZERO RELATIVE MOTION and the pushrod never strokes the ring.  No
choice of dimensions can create relative motion the frame geometry does not
have.  See `docs/NOZZLE_DRIVE_TRADE.md`, "DECISION AMENDMENT -- hybrid A+B
adopted (2026-07-19)", which this sweep independently re-confirmed.

Do NOT delete this model to tidy up.  Deleting it would erase the negative
result that justifies the adopted design.

ASSUMPTIONS (explicit, per the plan's instruction to state rather than invent)
=============================================================================
* FLAP_LENGTH does not enter either model.  `nacelle_nozzle_iris.scad` fixes
  THETA_RING_REF_OPEN = 23.75 deg as a hard constant independent of
  FLAP_LENGTH -- the cam follower geometry (TAB_X/TAB_Z, solved from
  PIN_R_REF_CLOSED/OPEN, which are also FLAP_LENGTH-independent) re-solves so
  that whatever flap length is chosen, the SAME ring stroke 0 -> 23.75 deg
  still produces the required NOZZLE_CLOSED_R/OPEN_R exit radii.  The
  `--flap-length` flag is retained to report the derived PHI_CLOSED/PHI_OPEN
  for context and to keep the CLI symmetrical with the rest of the U1/U2
  pipeline, but it is not wired into the psi solve.
* This script checks KINEMATICS only.  It does not check that the pushrod
  clears the cowl skin, the ESC bays or the flap sweep over the whole tilt
  range -- that is a separate clearance/interference check (WBS §1.1.3).

Source-of-truth constants (each COPIED here, not re-derived, per this repo's
`tools/landing_gear_ground_clearance.py` provenance-comment convention):
  CRANK_R              airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad:145
  CRANK_PHASE          airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad:148
  PUSHROD_LEN          airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad:170
  RING_LEVER_AZ        airframe/openscad/nacelles/nacelle_nozzle_iris.scad:510
  RING_LEVER_R         airframe/openscad/nacelles/nacelle_nozzle_iris.scad:526
  RING_H               airframe/openscad/nacelles/nacelle_nozzle_iris.scad:500
                       (ring ball Z = RING_H / 2, unison_ring() ball socket)
  THETA_RING_REF_OPEN  airframe/openscad/nacelles/nacelle_nozzle_iris.scad:421
  THROAT_OUTER_R       airframe/openscad/nacelles/nacelle_nozzle_iris.scad:327
  NOZZLE_CLOSED_R      airframe/openscad/nacelles/nacelle_nozzle_iris.scad:320
  NOZZLE_OPEN_R        airframe/openscad/nacelles/nacelle_nozzle_iris.scad:321
  NOZZLE_RING_Z        airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad:350
  PIVOT_Z              airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad:437
  SYNC_R / SYNC_CD     airframe/openscad/port_tilt_spar_assembly.scad:322-323
  SUN_XLOC             airframe/openscad/port_tilt_spar_assembly.scad:324

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CEH
License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
Date:    2026-09-08 (reworked 2026-09-09 to the adopted pinion architecture)
AI contribution: Claude (Sonnet 5 original; Opus 5 rework, Anthropic),
                 directed by Steve Griffing.
"""

from __future__ import annotations

import argparse
import math
import sys

# ══ Source-of-truth constants (see module docstring for file:line) ═════════

# ── Drive crank / pushrod (nacelle_nozzle_pushrod.scad) ────────────────────
# CRANK_R: [mm] crank ball-stud radius (moment arm).
CRANK_R = 8.5                                # nacelle_nozzle_pushrod.scad:145
# CRANK_PHASE_DEG: [deg] crank clocking about the PINION axis at zero tilt.
CRANK_PHASE_DEG = 206.0                      # nacelle_nozzle_pushrod.scad:148
# PUSHROD_LEN_NOMINAL: [mm] solved rod length, ball centre to ball centre (was
# 45.0 first-pass).  COTS turnbuckle-adjustable ball-link rod.
PUSHROD_LEN_NOMINAL = 48.0                   # nacelle_nozzle_pushrod.scad:170

# ── Unison ring lever (nacelle_nozzle_iris.scad) ───────────────────────────
# RING_LEVER_AZ_DEG: [deg] lever-ear azimuth, relocated 22.5 -> 157.5 (the
# INBOARD flap gap, so the pushrod hugs the inboard cheek).
RING_LEVER_AZ_DEG = 157.5                    # nacelle_nozzle_iris.scad:510
# RING_LEVER_R: [mm] radial reach of the ball-socket centre on the lever.
RING_LEVER_R = 32.0                          # nacelle_nozzle_iris.scad:526
# RING_H: [mm] unison ring axial height; the ball socket sits at mid-height.
RING_H = 8.0                                 # nacelle_nozzle_iris.scad:500
RING_BALL_Z = RING_H / 2.0                   # [mm] = 4.0, unison_ring() socket

# THETA_RING_REF_OPEN_DEG: [deg] FIXED ring-stroke target over 0->90 deg tilt,
# independent of FLAP_LENGTH (see the module docstring ASSUMPTIONS).
THETA_RING_REF_OPEN_DEG = 23.75              # nacelle_nozzle_iris.scad:421

R_HINGE = 27.5                   # [mm] nacelle_nozzle_iris.scad:327 THROAT_OUTER_R
NOZZLE_CLOSED_R = 18.75          # [mm] nacelle_nozzle_iris.scad:320
NOZZLE_OPEN_R = 26.25            # [mm] nacelle_nozzle_iris.scad:321

# ── Pod stations (nacelle_pod_50mm_tandem.scad) ────────────────────────────
NOZZLE_RING_Z = 166.25           # [mm] nacelle_pod_50mm_tandem.scad:350
# PIVOT_Z: [mm] AUTHORITATIVE tilt-pivot station on the duct axis (Rev T4c).
PIVOT_Z = 107.5                              # nacelle_pod_50mm_tandem.scad:437

# ── Sync gear pair (port_tilt_spar_assembly.scad §6) ───────────────────────
# SYNC_R: [mm] pitch radius of the 1:1 wing sun and nacelle pinion (pitch Ø26).
SYNC_R = 13.0                                # port_tilt_spar_assembly.scad:322
# SYNC_CD: [mm] centre distance = 26; the pinion sits this far AFT of the spar
# axis, clearing the on-axis Hall/bearing stack in the wing-tip joint gap.
SYNC_CD = 2 * SYNC_R                         # port_tilt_spar_assembly.scad:323
# SUN_XLOC: [mm] nacelle-local X of the mesh plane, in the joint gap.
SUN_XLOC = -38.0                             # port_tilt_spar_assembly.scad:324

# ── Derived nacelle-frame stations (adopted model) ─────────────────────────
PINION_Z = PIVOT_Z + SYNC_CD     # [mm] = 133.5; pinion axis height on local Z
RING_BALL_ZLOC = NOZZLE_RING_Z + RING_BALL_Z   # [mm] = 170.25

# ── Check tolerances ───────────────────────────────────────────────────────
# SPAN_TOL_DEG: [deg] allowed deviation of the swept psi span (and of its start
# angle) from the 0..THETA_RING_REF_OPEN design target.
SPAN_TOL_DEG = 5.0
# TA_FLOOR_DEG_DEFAULT: [deg] transmission-angle floor.  40-45 deg is the
# standard linkage-design rule of thumb; 40 is its permissive end.
TA_FLOOR_DEG_DEFAULT = 40.0
# PSI search window.  Widened 2026-09-09 from an original +/-90 deg: a +/-90
# bracket clips real coupler motion and produces a FALSE reversal by
# root-tracking a wrapped-around root just outside the window instead of the
# true continuous branch.
PSI_SEARCH_LO_DEG = -200.0
PSI_SEARCH_HI_DEG = 200.0
# Coarse bracket-scan resolution (0.5 deg/step over the widened range), then
# bisection to convergence.
PSI_SCAN_STEPS = 800
BISECT_ITERS = 60


def phi_closed_open_deg(flap_length: float) -> tuple[float, float]:
    """Derived flap swing angles, for report context only.

    Not used in either psi solve -- see the module docstring ASSUMPTIONS.
    phi(exit_r) = asin((R_HINGE - exit_r) / FLAP_LENGTH), per
    nacelle_nozzle_iris.scad.
    """
    phi_closed = math.degrees(math.asin((R_HINGE - NOZZLE_CLOSED_R) / flap_length))
    phi_open = math.degrees(math.asin((R_HINGE - NOZZLE_OPEN_R) / flap_length))
    return phi_closed, phi_open


# ═══════════════════════════════════════════════════════════════════════════
# ADOPTED MODEL -- wing-fixed sun / nacelle pinion, solved in the NACELLE frame
# ═══════════════════════════════════════════════════════════════════════════
#
# NOTE ON FRAMES (this is the crux of the whole fix): every point below is
# expressed in NACELLE-LOCAL coordinates and every one of them is carried
# rigidly by the nacelle as it tilts.  Tilting the nacelle applies the SAME
# rotation to the crank ball and the ring ball, and a rigid rotation preserves
# distances -- so the tilt angle cancels out of the rod-length equation and
# never appears in these functions.  Tilt enters ONLY through the pinion's
# drive angle (theta + CRANK_PHASE), because the pinion is geared against the
# non-tilting wing.  The superseded model below, by contrast, had to carry the
# tilt rotation explicitly, and that is precisely where its zero-relative-
# motion failure lived.


def crank_ball_pinion(theta_deg: float, crank_r: float,
                      phase_deg: float) -> tuple[float, float, float]:
    """Nacelle-local position of the crank ball riding the sync pinion."""
    ang = math.radians(theta_deg + phase_deg)
    return (SUN_XLOC,
            crank_r * math.sin(ang),
            PINION_Z + crank_r * math.cos(ang))


def ring_ball_nacelle(psi_deg: float) -> tuple[float, float, float]:
    """Nacelle-local position of the unison-ring lever ball at ring angle psi."""
    az = math.radians(RING_LEVER_AZ_DEG + psi_deg)
    return (RING_LEVER_R * math.cos(az),
            RING_LEVER_R * math.sin(az),
            RING_BALL_ZLOC)


def rod_len_pinion(theta_deg: float, psi_deg: float, crank_r: float,
                   phase_deg: float) -> float:
    """Crank-ball to ring-ball distance in the nacelle frame."""
    cx, cy, cz = crank_ball_pinion(theta_deg, crank_r, phase_deg)
    rx, ry, rz = ring_ball_nacelle(psi_deg)
    return math.sqrt((rx - cx) ** 2 + (ry - cy) ** 2 + (rz - cz) ** 2)


def transmission_angle_deg(theta_deg: float, psi_deg: float, crank_r: float,
                           phase_deg: float) -> float:
    """Angle at the ring ball between the pushrod and the ring lever arm.

    The lever arm is the radial vector from the ring's own rotation axis
    (nacelle-local Z, through the duct centreline) out to the ball; the
    pushrod vector runs from the ring ball to the crank ball.  Only the
    component of rod force perpendicular to the arm produces ring torque, so
    this angle is the linkage's mechanical-advantage health indicator.
    Returned raw (0..180); callers fold it with min(TA, 180 - TA).
    """
    rx, ry, rz = ring_ball_nacelle(psi_deg)
    cx, cy, cz = crank_ball_pinion(theta_deg, crank_r, phase_deg)
    # Lever arm: ring-axis-to-ball, purely radial (the axis is local Z).
    arm = (rx, ry, 0.0)
    rod = (cx - rx, cy - ry, cz - rz)
    arm_mag = math.sqrt(sum(c * c for c in arm))
    rod_mag = math.sqrt(sum(c * c for c in rod))
    if arm_mag == 0.0 or rod_mag == 0.0:
        return 0.0
    dot = sum(a * b for a, b in zip(arm, rod))
    return math.degrees(math.acos(max(-1.0, min(1.0, dot / (arm_mag * rod_mag)))))


def _root_find(f, psi_prev: float | None) -> float | None:
    """Scan-and-bisect all roots of f(psi) over the psi search window.

    Returns the root closest to `psi_prev` (continuity tracking along the
    branch) or, on the first sample, the root closest to 0.  Returns None if
    no root exists anywhere in the window (the rod cannot bridge the balls --
    a locking condition).
    """
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


def solve_psi_pinion(theta_deg: float, crank_r: float, phase_deg: float,
                     pushrod_len: float, psi_prev: float | None) -> float | None:
    """Root-find psi such that rod_len_pinion(theta, psi) == pushrod_len."""
    return _root_find(
        lambda psi: rod_len_pinion(theta_deg, psi, crank_r, phase_deg) - pushrod_len,
        psi_prev)


def sweep_pinion(crank_r: float, phase_deg: float, pushrod_len: float,
                 ta_floor_deg: float = TA_FLOOR_DEG_DEFAULT,
                 theta_step_deg: float = 1.0) -> dict:
    """Sweep tilt 0 -> 90 deg on the ADOPTED model, solving psi(theta).

    Returns a report dict with reachable / monotonic / span_ok / ta_ok flags,
    the sampled thetas and psis, the span error terms, and the transmission
    angle extremes.
    """
    n_steps = int(round(90.0 / theta_step_deg))
    thetas = [i * theta_step_deg for i in range(n_steps + 1)]
    psis: list[float] = []
    psi_prev: float | None = None

    for theta in thetas:
        psi = solve_psi_pinion(theta, crank_r, phase_deg, pushrod_len, psi_prev)
        if psi is None:
            return {
                "reachable": False, "monotonic": None, "span_ok": None,
                "ta_ok": None, "ok": False, "fail_theta": theta,
                "thetas": thetas, "psis": psis,
            }
        psis.append(psi)
        psi_prev = psi

    # ── (b) monotonicity ──────────────────────────────────────────────────
    direction = 1.0 if psis[-1] >= psis[0] else -1.0
    monotonic = True
    bad_theta = None
    for i in range(len(psis) - 1):
        d = psis[i + 1] - psis[i]
        if direction * d < -1e-4:
            monotonic = False
            bad_theta = thetas[i + 1]
            break

    # ── (c) span vs. THETA_RING_REF_OPEN ──────────────────────────────────
    # The ring may sweep in either azimuth direction (the adopted geometry
    # runs NEGATIVE, 0 -> -24.18 deg); what the cam needs is the MAGNITUDE of
    # the stroke and a near-zero start, so both are checked on magnitude.
    span = abs(psis[-1] - psis[0])
    span_lo_err = abs(psis[0])
    span_hi_err = abs(span - THETA_RING_REF_OPEN_DEG)
    span_ok = span_lo_err <= SPAN_TOL_DEG and span_hi_err <= SPAN_TOL_DEG

    # ── (d) transmission angle ────────────────────────────────────────────
    tas = [transmission_angle_deg(t, p, crank_r, phase_deg)
           for t, p in zip(thetas, psis)]
    ta_eff = [min(ta, 180.0 - ta) for ta in tas]
    ta_min_eff = min(ta_eff)
    ta_ok = ta_min_eff >= ta_floor_deg
    ta_worst_theta = thetas[ta_eff.index(ta_min_eff)]

    return {
        "reachable": True, "monotonic": monotonic, "span_ok": span_ok,
        "ta_ok": ta_ok,
        "ok": monotonic and span_ok and ta_ok,
        "fail_theta": bad_theta,
        "thetas": thetas, "psis": psis,
        "span": span, "span_lo_err": span_lo_err, "span_hi_err": span_hi_err,
        "ta_raw_min": min(tas), "ta_raw_max": max(tas),
        "ta_min_eff": ta_min_eff, "ta_worst_theta": ta_worst_theta,
        "ta_floor": ta_floor_deg,
    }


def report_pinion(flap_length: float, crank_r: float, phase_deg: float,
                  pushrod_len: float, ta_floor_deg: float, label: str) -> bool:
    """Run and print the ADOPTED-model check.  Returns True on PASS."""
    phi_closed, phi_open = phi_closed_open_deg(flap_length)
    result = sweep_pinion(crank_r, phase_deg, pushrod_len, ta_floor_deg)

    print(f"\n=== {label}: ADOPTED model (wing-fixed sun -> nacelle pinion "
          f"-> crank -> pushrod -> ring) ===")
    print("  architecture: docs/NOZZLE_DRIVE_TRADE.md 'DECISION AMENDMENT -- "
          "hybrid A+B adopted (2026-07-19)'")
    print("  frame       : nacelle-local; tilt cancels out of the rod-length "
          "equation (see module docstring)")
    print(f"  pinion axis : (x={SUN_XLOC:.1f}, y=0.0, z={PINION_Z:.1f}) mm, "
          f"parallel to local X;  PIVOT_Z={PIVOT_Z:.1f}, SYNC_CD={SYNC_CD:.1f}")
    print(f"  crank       : CRANK_R={crank_r:.2f} mm, "
          f"CRANK_PHASE={phase_deg:.2f} deg")
    print(f"  pushrod     : PUSHROD_LEN={pushrod_len:.2f} mm")
    print(f"  ring lever  : RING_LEVER_R={RING_LEVER_R:.1f} mm, "
          f"RING_LEVER_AZ={RING_LEVER_AZ_DEG:.1f} deg, "
          f"ball z={RING_BALL_ZLOC:.2f} mm")
    print(f"  (context only, not used in the solve) "
          f"PHI_CLOSED={phi_closed:.2f} deg, PHI_OPEN={phi_open:.2f} deg")

    if not result["reachable"]:
        print(f"  FAIL (a) reachability: no real psi at tilt "
              f"{result['fail_theta']:.1f} deg over the "
              f"{PSI_SEARCH_LO_DEG:.0f}..{PSI_SEARCH_HI_DEG:.0f} deg search "
              f"window -- LOCKING.")
        return False

    psis = result["psis"]
    print(f"  (a) reachable at all {len(result['thetas'])} sampled tilt angles "
          f"(0..90 deg, "
          f"{result['thetas'][1] - result['thetas'][0]:.1f} deg step): yes")

    if not result["monotonic"]:
        print(f"  FAIL (b) monotonicity: psi(theta) reverses at tilt "
              f"{result['fail_theta']:.1f} deg (toggle / dead point).")
        return False
    print(f"  (b) monotonic: yes "
          f"({'increasing' if psis[-1] >= psis[0] else 'decreasing'} azimuth)")

    print(f"  (c) psi(0 deg)  = {psis[0]:+8.3f} deg  "
          f"(target 0.000, err {result['span_lo_err']:.3f} deg)")
    print(f"      psi(90 deg) = {psis[-1]:+8.3f} deg")
    print(f"      span        = {result['span']:8.3f} deg  "
          f"(target {THETA_RING_REF_OPEN_DEG:.2f}, "
          f"err {result['span_hi_err']:.3f} deg = "
          f"{100.0 * result['span_hi_err'] / THETA_RING_REF_OPEN_DEG:.1f} %)")
    print(f"  (d) transmission angle {result['ta_raw_min']:.2f}.."
          f"{result['ta_raw_max']:.2f} deg;  worst min(TA, 180-TA) = "
          f"{result['ta_min_eff']:.2f} deg at tilt "
          f"{result['ta_worst_theta']:.1f} deg  (floor {result['ta_floor']:.1f} deg)")

    if not result["span_ok"]:
        print(f"  FAIL (c) span: psi span misses the 0..."
              f"{THETA_RING_REF_OPEN_DEG:.2f} deg design target by more than "
              f"+/-{SPAN_TOL_DEG:.1f} deg -- the ring would not reach one of "
              f"NOZZLE_CLOSED_R / NOZZLE_OPEN_R.")
        return False
    if not result["ta_ok"]:
        print(f"  FAIL (d) transmission angle: worst-case "
              f"{result['ta_min_eff']:.2f} deg is below the "
              f"{result['ta_floor']:.1f} deg floor -- the rod force would be "
              f"nearly along the lever arm, wasting it as bearing load.")
        return False

    print(f"  PASS: reachable, monotonic, span within +/-{SPAN_TOL_DEG:.1f} deg "
          f"of the {THETA_RING_REF_OPEN_DEG:.2f} deg target, and transmission "
          f"angle above the {result['ta_floor']:.1f} deg floor.")
    return True


def search_dimensions_pinion(
    crank_phase_grid: tuple = tuple(float(d) for d in range(0, 360, 2)),
    pushrod_len_grid: tuple = (40.0, 44.0, 48.0, 52.0, 56.0, 60.0),
    crank_r_grid: tuple = (6.0, 8.5, 11.0, 14.0),
    ta_floor_deg: float = TA_FLOOR_DEG_DEFAULT,
    theta_step_deg: float = 6.0,
) -> list[tuple]:
    """Sweep the ADOPTED architecture's FREE parameters.

    Coarse by design: theta is stepped 6 deg here (16 samples) rather than the
    1 deg of the nominal check, because this mode is a SYNTHESIS scan over
    thousands of candidates, not a verification.  Re-check any candidate it
    surfaces with a normal single-case run before believing it.

    Retargeted 2026-09-09 from the superseded model's (CRANK_R, PUSHROD_LEN,
    spar mounting phase, spar axial station) search.  Under the adopted design
    the crank's axial station is NOT free -- it is pinned to the mesh plane
    SUN_XLOC = -38.0 mm in the wing-tip joint gap -- and the pinion axis is
    pinned by PIVOT_Z + SYNC_CD.  What remains free is:

        CRANK_PHASE  -- how the crank is clocked on the pinion at zero tilt
        PUSHROD_LEN  -- set at assembly (turnbuckle-adjustable COTS rod)
        CRANK_R      -- the crank's moment arm

    Returns a list of (crank_r, pushrod_len, best_phase, result) rows, one per
    (crank_r, pushrod_len) cell, carrying the best phase found for that cell.
    """
    results = []
    for crank_r in crank_r_grid:
        for pushrod_len in pushrod_len_grid:
            best = None
            best_phase = None
            best_score = None
            for phase in crank_phase_grid:
                r = sweep_pinion(crank_r, phase, pushrod_len,
                                 ta_floor_deg, theta_step_deg)
                # Score EVERY candidate, passing or not, and keep the best.
                # Deliberately no early break on the first pass: passing
                # candidates are ranked by how closely they hit the span
                # target, so the reported phase is the BEST one for the cell
                # rather than merely the first phase to clear the tolerance.
                if not r["reachable"]:
                    score = 1e6 - r["fail_theta"]          # prefer failing later
                elif not r["monotonic"]:
                    score = 1e4 - (r["fail_theta"] or 0.0)
                else:
                    score = r["span_lo_err"] + r["span_hi_err"]
                    if not r["ta_ok"]:
                        score += 1e2 + (ta_floor_deg - r["ta_min_eff"])
                if best_score is None or score < best_score:
                    best_score, best, best_phase = score, r, phase
            results.append((crank_r, pushrod_len, best_phase, best))
    return results


# ═══════════════════════════════════════════════════════════════════════════
# SUPERSEDED MODEL -- spar crank, HULL frame.  RETAINED AS THE HISTORICAL /
# REGRESSION RECORD OF WHY THAT ARCHITECTURE WAS ABANDONED.  Do not delete:
# its empty search result is the evidence behind the 2026-07-19 trade
# amendment (docs/NOZZLE_DRIVE_TRADE.md, "DECISION AMENDMENT -- hybrid A+B
# adopted").  See the module docstring, "SUPERSEDED MODEL".
# ═══════════════════════════════════════════════════════════════════════════
#
# Coordinate model: a hull-frame-oriented basis centred on the pivot, reusing
# the tilt convention of `tools/landing_gear_ground_clearance.py` (T_BAKE) and
# `tools/nacelle_mass_cg.py`.  Nacelle-local X is the (unrotated) spar/tilt
# axis; at theta = 0 the duct axis (local Z) maps to hull +Y and local Y maps
# to hull -Z; tilting rotates about hull X:
#
#   duct axis (local Z) in hull frame:            (0,  cos(theta), -sin(theta))
#   local Y axis in hull frame:                   (0, -sin(theta), -cos(theta))
#   local X axis (spar/tilt axis) in hull frame:  (1,  0,           0)
#
# The crank was clamped DIRECTLY to the spar, so its hull-frame angular
# position was the tilt angle plus a fixed mounting phase, at a free axial
# station along the spar.  Because the spar is keyed to the nacelle, this
# leaves the crank and the ring in one common rotating frame -- the defect.
#
# NOTE: this model reads the CURRENT RING_LEVER_AZ_DEG (157.5), whereas the
# original 2026-09-09 finding was recorded at 22.5.  The failure is a frame /
# topology failure and is independent of the lever azimuth -- the azimuth only
# shifts which psi branch is tracked, not whether relative motion exists -- so
# the negative result reproduces at either value.

# Axial offset of the ring ball from the pivot along the (pre-tilt) duct axis.
AXIAL_OFFSET = RING_BALL_ZLOC - PIVOT_Z          # [mm] = 62.75

# Free assembly parameters of the SUPERSEDED model (never pinned by any source
# file; grid-searched rather than invented).
CRANK_PHASE_GRID_DEG = [i * 5.0 for i in range(0, 360, 5)]   # 0..355 step 5
CRANK_AXIAL_X_GRID = [0.0, 20.0, 40.0]        # [mm] candidate spar stations


def crank_ball_spar(theta_deg: float, crank_r: float, phase_deg: float,
                    axial_x: float) -> tuple[float, float, float]:
    """SUPERSEDED: hull-frame crank ball, clamped to the spar."""
    ang = math.radians(theta_deg + phase_deg)
    return (axial_x, crank_r * math.cos(ang), crank_r * math.sin(ang))


def ring_ball_hull(theta_deg: float, psi_deg: float) -> tuple[float, float, float]:
    """SUPERSEDED: hull-frame ring lever ball, carried around by the tilt."""
    theta = math.radians(theta_deg)
    az = math.radians(RING_LEVER_AZ_DEG + psi_deg)
    cos_a, sin_a = math.cos(az), math.sin(az)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    x = RING_LEVER_R * cos_a
    y = AXIAL_OFFSET * cos_t - RING_LEVER_R * sin_a * sin_t
    z = -AXIAL_OFFSET * sin_t - RING_LEVER_R * sin_a * cos_t
    return (x, y, z)


def rod_len_spar(theta_deg: float, psi_deg: float, crank_r: float,
                 phase_deg: float, axial_x: float) -> float:
    """SUPERSEDED: hull-frame crank-ball to ring-ball distance."""
    cx, cy, cz = crank_ball_spar(theta_deg, crank_r, phase_deg, axial_x)
    rx, ry, rz = ring_ball_hull(theta_deg, psi_deg)
    return math.sqrt((rx - cx) ** 2 + (ry - cy) ** 2 + (rz - cz) ** 2)


def sweep_spar(crank_r: float, phase_deg: float, axial_x: float,
               pushrod_len: float, theta_step_deg: float = 1.0) -> dict:
    """SUPERSEDED: sweep tilt 0 -> 90 deg on the spar-crank model."""
    n_steps = int(round(90.0 / theta_step_deg))
    thetas = [i * theta_step_deg for i in range(n_steps + 1)]
    psis: list[float] = []
    psi_prev: float | None = None

    for theta in thetas:
        psi = _root_find(
            lambda p, t=theta: rod_len_spar(t, p, crank_r, phase_deg,
                                            axial_x) - pushrod_len,
            psi_prev)
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
    span_hi_err = abs(abs(psis[-1] - psis[0]) - THETA_RING_REF_OPEN_DEG)
    span_ok = span_lo_err <= SPAN_TOL_DEG and span_hi_err <= SPAN_TOL_DEG

    return {
        "reachable": True, "monotonic": monotonic, "span_ok": span_ok,
        "ok": monotonic and span_ok, "fail_theta": bad_theta,
        "thetas": thetas, "psis": psis,
        "span_lo_err": span_lo_err, "span_hi_err": span_hi_err,
    }


def synthesize_spar(crank_r: float, pushrod_len: float,
                    theta_step_deg: float = 1.0) -> tuple[dict, float, float]:
    """SUPERSEDED: grid-search the spar crank's free phase / axial station."""
    best_result = best_phase = best_axial = best_score = None
    for axial_x in CRANK_AXIAL_X_GRID:
        for phase in CRANK_PHASE_GRID_DEG:
            result = sweep_spar(crank_r, phase, axial_x, pushrod_len,
                                theta_step_deg)
            if result["ok"]:
                return result, phase, axial_x
            if not result["reachable"]:
                score = 1e6 - result["fail_theta"]
            elif not result["monotonic"]:
                score = 1e4 - (result["fail_theta"] or 0.0)
            else:
                score = result["span_lo_err"] + result["span_hi_err"]
            if best_score is None or score < best_score:
                best_score, best_result = score, result
                best_phase, best_axial = phase, axial_x
    return best_result, best_phase, best_axial


def report_spar_superseded(flap_length: float, crank_r: float,
                           pushrod_len: float, label: str) -> bool:
    """SUPERSEDED-model report.  Expected to FAIL -- that is the record."""
    phi_closed, phi_open = phi_closed_open_deg(flap_length)
    result, phase, axial_x = synthesize_spar(crank_r, pushrod_len)

    print(f"\n=== {label}: SUPERSEDED model (crank clamped to the KEYED tilt "
          f"spar, hull frame) ===")
    print("  RETAINED AS HISTORICAL RECORD.  This architecture was abandoned "
          "on 2026-07-19;")
    print("  see docs/NOZZLE_DRIVE_TRADE.md 'DECISION AMENDMENT -- hybrid A+B "
          "adopted'.  The")
    print("  spar is KEYED TO THE NACELLE, so crank and ring share one "
          "rotating frame and the")
    print("  pushrod never strokes the ring.  A FAIL here is the EXPECTED and "
          "correct result.")
    print(f"  CRANK_R={crank_r:.2f} mm, PUSHROD_LEN={pushrod_len:.2f} mm")
    print(f"  best free-parameter combination found: CRANK_PHASE="
          f"{phase:.1f} deg, CRANK_AXIAL_X={axial_x:.1f} mm")
    print(f"  (context only) PHI_CLOSED={phi_closed:.2f} deg, "
          f"PHI_OPEN={phi_open:.2f} deg")

    if not result["reachable"]:
        print(f"  FAIL (expected): rod cannot reach at tilt "
              f"{result['fail_theta']:.1f} deg for ANY phase / axial station "
              f"tried -- LOCKING.")
        return False
    if not result["monotonic"]:
        print(f"  FAIL (expected): psi(theta) reverses at tilt "
              f"{result['fail_theta']:.1f} deg for every phase / axial station "
              f"tried -- toggle / dead point.")
        return False
    print(f"  psi(0)={result['psis'][0]:+.3f} deg, "
          f"psi(90)={result['psis'][-1]:+.3f} deg")
    if not result["span_ok"]:
        print("  FAIL (expected): span misses the design target.")
        return False
    print("  UNEXPECTED PASS -- investigate: the historical record says this "
          "architecture cannot work.")
    return True


def search_dimensions_spar(
    crank_r_grid: tuple = (8.5, 12.0, 15.0, 18.0, 22.0, 28.0),
    pushrod_len_grid: tuple = (58.0, 63.0, 68.0, 73.0, 78.0, 83.0, 90.0),
    phase_grid: tuple = tuple(float(d) for d in range(0, 360, 15)),
    axial_grid: tuple = (0.0, 15.0, 30.0, 45.0, 60.0, 62.75, 75.0, 90.0),
    theta_step_deg: float = 4.0,
) -> list[tuple]:
    """SUPERSEDED: exhaustive (CRANK_R, PUSHROD_LEN, phase, axial) search.

    2026-09-09 finding, retained verbatim as the negative result: across these
    ranges -- CRANK_R 8.5-28 mm (3.3x nominal), PUSHROD_LEN 58-90 mm (spanning
    the full 56-79 mm crank-to-ring 3-D separation measured over the whole
    theta/psi/phase space), 24 mounting phases, 8 axial stations -- this search
    returns ZERO passing combinations.  Every candidate either cannot reach, or
    reaches but genuinely reverses direction partway through the 0->90 deg
    sweep (a real toggle/dead point, confirmed by hand-tracing the widened
    +/-200 deg psi search against the earlier +/-90 deg version, which had been
    clipping the true continuous branch).  This is evidence that the spar-crank
    TOPOLOGY does not admit a solution at this scale -- not that the as-drawn
    dimensions merely need tuning.
    """
    results = []
    for crank_r in crank_r_grid:
        for pushrod_len in pushrod_len_grid:
            best = best_score = best_phase = best_axial = None
            for axial_x in axial_grid:
                for phase in phase_grid:
                    r = sweep_spar(crank_r, phase, axial_x, pushrod_len,
                                   theta_step_deg)
                    if r["ok"]:
                        best, best_phase, best_axial = r, phase, axial_x
                        break
                    if not r["reachable"]:
                        score = 1e6 - r["fail_theta"]
                    elif not r["monotonic"]:
                        score = 1e4 - (r["fail_theta"] or 0.0)
                    else:
                        score = r["span_lo_err"] + r["span_hi_err"]
                    if best_score is None or score < best_score:
                        best_score, best = score, r
                        best_phase, best_axial = phase, axial_x
                if best is not None and best["ok"]:
                    break
            results.append((crank_r, pushrod_len, best_phase, best_axial, best))
    return results


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", choices=("pinion", "spar-crank-superseded"),
                        default="pinion",
                        help="Which architecture to check.  'pinion' (default) "
                             "is the ADOPTED wing-fixed-sun / nacelle-pinion "
                             "drive and must pass.  'spar-crank-superseded' "
                             "re-runs the abandoned spar-crank model, retained "
                             "as the historical record of why it was dropped "
                             "(it is EXPECTED to fail).")
    parser.add_argument("--flap-length", type=float, default=30.0,
                        help="[mm] FLAP_LENGTH, for report context only -- does "
                             "not affect the psi solve; see module docstring "
                             "ASSUMPTIONS (default: 30.0, plan 005 R1 target).")
    parser.add_argument("--crank-r", type=float, default=CRANK_R,
                        help=f"[mm] override CRANK_R (default: the SCAD value, "
                             f"{CRANK_R:.1f}).")
    parser.add_argument("--crank-phase", type=float, default=CRANK_PHASE_DEG,
                        help=f"[deg] override CRANK_PHASE, the crank's clocking "
                             f"on the pinion at zero tilt.  Adopted model only "
                             f"(default: the SCAD value, "
                             f"{CRANK_PHASE_DEG:.1f}).")
    parser.add_argument("--pushrod-len", type=float, default=PUSHROD_LEN_NOMINAL,
                        help=f"[mm] override PUSHROD_LEN, e.g. for a synthetic "
                             f"failure demonstration (default: the SCAD value, "
                             f"{PUSHROD_LEN_NOMINAL:.1f}).")
    parser.add_argument("--ta-floor", type=float, default=TA_FLOOR_DEG_DEFAULT,
                        help=f"[deg] minimum acceptable min(TA, 180-TA) "
                             f"transmission angle (default: "
                             f"{TA_FLOOR_DEG_DEFAULT:.0f}, the permissive end "
                             f"of the 40-45 deg linkage rule of thumb).")
    parser.add_argument("--label", type=str, default="run",
                        help="label for the printed report section.")
    parser.add_argument("--search-dimensions", action="store_true",
                        help="Sweep the selected model's free parameters "
                             "instead of checking one nominal case.  For the "
                             "adopted model that is CRANK_PHASE x PUSHROD_LEN "
                             "x CRANK_R; for the superseded model it is the "
                             "historical CRANK_R x PUSHROD_LEN x phase x spar "
                             "station sweep.  Exits 0 if any passing "
                             "combination is found, 1 otherwise.")
    args = parser.parse_args()

    superseded = (args.model == "spar-crank-superseded")

    # ── Parameter-sweep mode ──────────────────────────────────────────────
    if args.search_dimensions:
        if superseded:
            rows = search_dimensions_spar()
            passing = [r for r in rows if r[4] and r[4]["ok"]]
            print(f"SUPERSEDED model: searched {len(rows)} "
                  f"(CRANK_R, PUSHROD_LEN) cells x 24 phases x 8 spar "
                  f"stations.")
            if passing:
                for crank_r, plen, phase, axial, r in passing:
                    print(f"  PASS: CRANK_R={crank_r:.1f} "
                          f"PUSHROD_LEN={plen:.1f} phase={phase:.1f} "
                          f"axial_x={axial:.1f}")
                print("  UNEXPECTED -- the historical record says this "
                      "topology has no solution; investigate before trusting.")
                return 0
            print("FAIL (expected): no passing combination. This is the "
                  "retained negative result -- a TOPOLOGY problem, not a "
                  "sizing problem.  See search_dimensions_spar() docstring "
                  "and docs/NOZZLE_DRIVE_TRADE.md's 2026-07-19 amendment.")
            return 1

        rows = search_dimensions_pinion(ta_floor_deg=args.ta_floor)
        passing = [r for r in rows if r[3] and r[3]["ok"]]
        print(f"ADOPTED model: searched {len(rows)} (CRANK_R, PUSHROD_LEN) "
              f"cells x 180 crank phases (2 deg steps).")
        for crank_r, plen, phase, r in passing:
            print(f"  PASS: CRANK_R={crank_r:.1f} PUSHROD_LEN={plen:.1f} "
                  f"CRANK_PHASE={phase:.1f} "
                  f"span={r['span']:.3f} deg (err {r['span_hi_err']:.3f}) "
                  f"minTA={r['ta_min_eff']:.1f} deg")
        if passing:
            print(f"  {len(passing)} of {len(rows)} cells admit a solution.")
            return 0
        print("FAIL: no passing (CRANK_R, PUSHROD_LEN, CRANK_PHASE) "
              "combination found in the searched ranges.")
        return 1

    # ── Single-case mode ──────────────────────────────────────────────────
    if superseded:
        ok = report_spar_superseded(args.flap_length, args.crank_r,
                                    args.pushrod_len, args.label)
        print(f"\n{'PASS' if ok else 'FAIL'} (FAIL is the EXPECTED, correct "
              f"result for the superseded model): {args.label} "
              f"(CRANK_R={args.crank_r:.2f}, "
              f"PUSHROD_LEN={args.pushrod_len:.2f})")
        return 0 if ok else 1

    ok = report_pinion(args.flap_length, args.crank_r, args.crank_phase,
                       args.pushrod_len, args.ta_floor, args.label)
    print(f"\n{'PASS' if ok else 'FAIL'}: {args.label} "
          f"(CRANK_R={args.crank_r:.2f}, CRANK_PHASE={args.crank_phase:.2f}, "
          f"PUSHROD_LEN={args.pushrod_len:.2f})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
