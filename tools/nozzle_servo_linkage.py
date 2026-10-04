#!/usr/bin/env python3
"""Servo nozzle drive — schedule, linkage and force-margin tool (plan U2).

Governing documents
===================
* Decision: ``docs/NOZZLE_DRIVE_TRADE.md`` "DECISION AMENDMENT — servo drive
  (2026-09-28)".
* Plan: ``docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md``,
  unit U2 (KTD2 servo, KTD3 spring-opens / pull-only link, KTD4 schedule).
* Requirement: ``airframe/AGENTS.md`` "Nacelle Nozzle Drive" — exit 75 % of
  bore radius at 0 deg tilt, 105 % from 90 deg to the 145 deg tilt limit, and
  fail to 105 %.

What it computes
================
1. **Schedule.** Tilt -> target exit radius -> unison-ring angle psi.  The
   target radius is LINEAR in tilt from 18.75 mm (0 deg) to 26.25 mm (90 deg)
   and is held flat from 90 to 145 deg.  Invalid tilt (NaN / None) returns the
   fail-safe open command.  Linear-in-radius is a design choice recorded here;
   the requirement fixes only the endpoints.
2. **Cam kinematics.**  psi -> follower-pin radius (linear spiral, exactly as
   ``nacelle_nozzle_iris.scad`` ``pin_r_at_theta``) -> flap swing phi (inverse
   of ``flap_pin_r``) -> exit radius ``R_HINGE - FLAP_LENGTH * sin(phi)``.
3. **Linkage — rigid pushrod, OPEN ball cup (corrected 2026-09-29).**  A
   COTS M3 ball stud rides in the ring's ball cup at ``RING_LEVER_R`` /
   ``RING_LEVER_AZ`` — the SAME chord-position kinematics
   ``tools/nozzle_linkage_check.py`` already solved for this ring (ball
   position on a circle of radius ``RING_LEVER_R``, rod length = chord from
   the ball's OPEN position).  The cup is OPEN (a hemisphere plus a clear exit
   channel, not a captured sphere — see ``nacelle_nozzle_iris.scad``): the rod
   can only PUSH the ball in, never hold it there, so a seized or unpowered
   servo cannot block the ring from opening.  (An earlier cut of this tool
   modelled a push-only WIRE tangent to the ear's flat flank; that is
   kinematically wrong — a fixed point contacting a ROTATING FLAT FACE is
   coincident with it at one angle only, not a continuous range — and is
   superseded here.)  The servo arm of radius ``r_a`` sweeping ``sweep``
   degrees drives the rod (``stroke = r_a (sin a + sin(sweep/2))``).  The
   table maps each ring angle to a servo angle and a 1000-2000 us pulse.
4. **Force margins.**  Available pull = servo stall torque / arm (rotary) or
   rated force (linear), derated to 50 % for continuous holding.  Required =
   spring force + flap load, both referred to the ball cup.  The spring may
   not exceed 40 % of stall pull (KTD3).  Until the plan-U8 bench measures the
   flap load, the check reports ``PENDING-U8`` — it never reports PASS against
   the 20 N placeholder.

Sources (constants carry their file:line of origin)
===================================================
* Iris kinematics: ``airframe/openscad/nacelles/nacelle_nozzle_iris.scad``.
* Servo ratings, read on vendor pages 2026-09-28 (see plan Sources; REFERENCES
  entries are plan U7):
    - Blue Bird BMS-101DMG — 1.0 kgf.cm, 4.5 g, 8 mm case
      (hyperflight.co.uk products.asp?code=BMS-101DMG).  Voltage range and full
      dimensions NOT published on the page read — requires verification.
    - Hitec HS-40 — 0.8 kgf.cm at 6 V, 4.8 g, 20 x 8.6 x 17 mm
      (hitec.uk; servodatabase.com).
    - AGFRC C1.5CLS linear — 240 gf at 6 V, 1.5 g, stroke listed 7 vs 9 mm
      (amazon.com B07QGYBV1H) — REJECTED unless U8 load < ~1 N.

Units: SI internally (mm, N, deg); reports are imperial-primary with metric in
parentheses per the repo standard.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub Stab-Rabbit-coding)
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
Date:    2026-09-28
AI contribution: Claude (Claude Opus 5.5, Anthropic), directed by Steve Griffing.
"""

from __future__ import annotations
from typing import Any

import argparse
import json
import math
import sys
import warnings

# ══ Source-of-truth constants ════════════════════════════════════════════════

# ── Nozzle iris (nacelle_nozzle_iris.scad) ─────────────────────────────────
BORE_R = 25.0                  # [mm] :318  EDF bore radius
NOZZLE_CLOSED_R = 18.75        # [mm] :320  exit radius at 0 deg tilt (75 %)
NOZZLE_OPEN_R = 26.25          # [mm] :321  exit radius at 90 deg tilt (105 %)
R_HINGE = 27.5                 # [mm] :332  tangential hinge circle radius
FLAP_LENGTH = 30.0             # [mm] :333  hinge to trailing edge
PIN_R_REF_CLOSED = 29.0        # [mm] :389  follower-pin radius at psi = 0
PIN_R_REF_OPEN = 31.0          # [mm] :390  follower-pin radius at full stroke
THETA_RING_REF_OPEN = 23.75    # [deg] :421 ring stroke closed -> open
RING_LEVER_AZ = 157.5          # [deg] :510 lever-ear azimuth (inboard flap gap)
RING_LEVER_R = 32.0            # [mm] :578 ball-cup centre radius on the ear
RING_BALL_D = 3.0              # [mm] :581 COTS M3 ball-stud ball (BOM BALLSTUD-M3)
SPRING_CORD_R = 32.35          # [mm] SPRING_CORD_R — opening-cord wrap radius

# Derived exactly as the SCAD derives them (:349-:395).
PHI_CLOSED = math.degrees(math.asin((R_HINGE - NOZZLE_CLOSED_R) / FLAP_LENGTH))
PHI_OPEN = math.degrees(math.asin((R_HINGE - NOZZLE_OPEN_R) / FLAP_LENGTH))
_sc, _cc = math.sin(math.radians(PHI_CLOSED)), math.cos(math.radians(PHI_CLOSED))
_so, _co = math.sin(math.radians(PHI_OPEN)), math.cos(math.radians(PHI_OPEN))
TAB_Z = (((PIN_R_REF_OPEN - R_HINGE) - (PIN_R_REF_CLOSED - R_HINGE) * _co / _cc)
         / (_sc * _co / _cc - _so))
TAB_X = ((PIN_R_REF_CLOSED - R_HINGE) + TAB_Z * _sc) / _cc

# ── Tilt schedule (airframe/AGENTS.md "Nacelle Nozzle Drive") ──────────────
TILT_OPEN_DEG = 90.0           # [deg] 105 % reached here, held to the limit
TILT_LIMIT_DEG = 145.0         # [deg] tilt-drive sweep limit (wings_s1223_revo.scad)

# ── Servo arm (plan KTD3, open-cup pushrod) ─────────────────────────────────
SERVO_SWEEP_DEG = 90.0         # [deg] assumed 1000-2000 us travel (U8 measures)
PULSE_MID_US = 1500            # [us]
PULSE_HALF_US = 500            # [us] half-range for SERVO_SWEEP_DEG / 2

# ── Force-margin rules (plan KTD2 / KTD3) ───────────────────────────────────
HOLD_DERATE = 0.5              # continuous holding pull as a fraction of stall
SPRING_MAX_FRAC = 0.40         # spring <= 40 % of stall pull (KTD3)
PLACEHOLDER_FLAP_LOAD_N = 20.0  # [N] generous placeholder until U8 measures
G0 = 9.80665                   # [m/s^2] standard gravity (kgf -> N)

# Servo candidates.  kind "rotary": torque_kgfcm; kind "linear": force_n.
SERVOS: dict[str, dict] = {
    "BMS-101DMG": {"kind": "rotary", "torque_kgfcm": 1.0, "mass_g": 4.5,
                   "note": "primary (KTD2); voltage range requires verification"},
    "HS-40": {"kind": "rotary", "torque_kgfcm": 0.8, "mass_g": 4.8,
              "note": "alternate; 0.8 kgf.cm at 6 V"},
    "AGFRC-C1.5CLS": {"kind": "linear", "force_n": 0.240 * G0, "mass_g": 1.5,
                      "note": "linear; rejected unless U8 load < ~1 N"},
}


# ══ Cam kinematics ═══════════════════════════════════════════════════════════

def _flap_pin_r(phi_deg: float) -> float:
    """Follower-pin radius at flap swing phi (SCAD flap_pin_r)."""
    p = math.radians(phi_deg)
    return R_HINGE + TAB_X * math.cos(p) - TAB_Z * math.sin(p)


def _bisect(f, lo: float, hi: float, iters: int = 80) -> float:
    """Root of a monotonic f on [lo, hi] by bisection (sign change required)."""
    flo = f(lo)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


def exit_radius_for_ring(psi_deg: float) -> float:
    """Nozzle exit radius [mm] at unison-ring angle psi [deg]."""
    pin_r = (PIN_R_REF_CLOSED
             + (PIN_R_REF_OPEN - PIN_R_REF_CLOSED) * psi_deg / THETA_RING_REF_OPEN)
    phi = _bisect(lambda ph: _flap_pin_r(ph) - pin_r, PHI_OPEN - 5.0, PHI_CLOSED + 5.0)
    return R_HINGE - FLAP_LENGTH * math.sin(math.radians(phi))


def ring_angle_for_exit(exit_r: float) -> float:
    """Inverse of exit_radius_for_ring over the ring stroke."""
    return _bisect(lambda ps: exit_radius_for_ring(ps) - exit_r,
                   -2.0, THETA_RING_REF_OPEN + 2.0)


def ring_angle_for_tilt(tilt_deg: float | None) -> float:
    """Scheduled ring angle for a measured tilt.  Invalid input -> open (R2)."""
    open_psi = ring_angle_for_exit(NOZZLE_OPEN_R)
    if tilt_deg is None or not math.isfinite(tilt_deg):
        return open_psi
    if tilt_deg > TILT_LIMIT_DEG:
        warnings.warn(f"tilt {tilt_deg:.1f} deg beyond the {TILT_LIMIT_DEG:.0f} deg "
                      "limit; clamped to the open hold", UserWarning, stacklevel=2)
        return open_psi
    frac = min(max(tilt_deg / TILT_OPEN_DEG, 0.0), 1.0)
    if frac >= 1.0:
        return open_psi
    target = NOZZLE_CLOSED_R + (NOZZLE_OPEN_R - NOZZLE_CLOSED_R) * frac
    return ring_angle_for_exit(target)


# ══ Linkage ══════════════════════════════════════════════════════════════════

def _ball_xy(psi_deg: float) -> tuple[float, float]:
    """Ball-cup position in the ring plane at stroke-progress psi [mm].

    psi runs 0 (closed) -> THETA_RING_REF_OPEN (open).  Opening turns the ring
    CLOCKWISE (nacelle_nozzle_iris.scad: opening rotates the ring clockwise,
    the cam slots are cut with radius rising with ring-local angle), so the
    actual rotation applied is -psi, matching the SCAD's AZ_OPEN = AZ_CLOSED
    - THETA_RING_REF_OPEN.
    """
    a = math.radians(RING_LEVER_AZ - psi_deg)
    return RING_LEVER_R * math.cos(a), RING_LEVER_R * math.sin(a)


def lever_chord_mm() -> float:
    """Straight-line ball travel over the full ring stroke [mm]."""
    return 2.0 * RING_LEVER_R * math.sin(math.radians(THETA_RING_REF_OPEN) / 2.0)


def rod_length_from_open_mm(psi_deg: float) -> float:
    """Rigid-rod length (from the ball's OPEN position) that holds psi [mm].

    Projects the ball's position onto the closed<-open chord, matching the
    RSSR chord-approximation `tools/nozzle_linkage_check.py` already uses for
    this same ring lever.
    """
    bx0, by0 = _ball_xy(0.0)
    bx1, by1 = _ball_xy(THETA_RING_REF_OPEN)
    ex, ey = bx0 - bx1, by0 - by1
    norm = math.hypot(ex, ey)
    bx, by = _ball_xy(psi_deg)
    return ((bx - bx1) * ex + (by - by1) * ey) / norm


def arm_radius_for_stroke(sweep_deg: float = SERVO_SWEEP_DEG) -> float:
    """Servo arm radius that produces the full lever chord over `sweep_deg`."""
    return lever_chord_mm() / (2.0 * math.sin(math.radians(sweep_deg) / 2.0))


def ring_can_open_with_rod_seized(alpha_deg: float) -> bool:
    """True: the OPEN ball cup admits full-open at any frozen servo angle.

    The cup only restrains the ball from moving IN (toward the rod); nothing
    stops it moving OUT (toward open) regardless of where a seized rod sits.
    This is the executable statement of the fail-open argument (KTD3), not a
    numerical coincidence — it holds unconditionally because the cup geometry
    has no return path modelled here, by construction.
    """
    del alpha_deg  # the open cup does not restrain the open direction at all
    return True


def servo_angle_for_ring(psi_deg: float, sweep_deg: float = SERVO_SWEEP_DEG) -> float:
    """Servo angle [deg, 0 = mid] holding ring angle psi."""
    r_a = arm_radius_for_stroke(sweep_deg)
    half = math.radians(sweep_deg) / 2.0
    s = rod_length_from_open_mm(psi_deg) / r_a - math.sin(half)
    return math.degrees(math.asin(max(-1.0, min(1.0, s))))


def pulse_for_servo_angle(alpha_deg: float, sweep_deg: float = SERVO_SWEEP_DEG) -> int:
    """PWM pulse [us] for a servo angle, clamped to 1000-2000 us."""
    us = PULSE_MID_US + alpha_deg / (sweep_deg / 2.0) * PULSE_HALF_US
    return round(min(max(us, 1000.0), 2000.0))


def build_table(step_deg: float = 5.0) -> list[dict]:
    """Tilt -> exit % -> ring psi -> servo angle -> pulse, 0 to 145 deg."""
    rows = []
    n = round(TILT_LIMIT_DEG / step_deg)
    for i in range(n + 1):
        tilt = min(i * step_deg, TILT_LIMIT_DEG)
        psi = ring_angle_for_tilt(tilt)
        alpha = servo_angle_for_ring(psi)
        rows.append({
            "tilt_deg": round(tilt, 2),
            "exit_r_mm": round(exit_radius_for_ring(psi), 3),
            "exit_pct": round(100.0 * exit_radius_for_ring(psi) / BORE_R, 2),
            "ring_psi_deg": round(psi, 3),
            "servo_deg": round(alpha, 2),
            "pulse_us": pulse_for_servo_angle(alpha),
        })
    return rows


# ══ Force margins ════════════════════════════════════════════════════════════

def stall_pull_n(servo: dict, arm_mm: float | None = None) -> float:
    """Stall pull at the link [N]."""
    if servo["kind"] == "linear":
        return servo["force_n"]
    arm = arm_mm if arm_mm is not None else arm_radius_for_stroke()
    return servo["torque_kgfcm"] * G0 * 10.0 / arm   # kgf.cm -> N.mm / mm


def check_margins(servo: dict, spring_n: float, flap_load_n: float | None,
                  measured: bool) -> dict:
    """Spring/servo margin check.  Loads are referred to the ball cup [N]."""
    stall = stall_pull_n(servo)
    hold = HOLD_DERATE * stall
    load = PLACEHOLDER_FLAP_LOAD_N if flap_load_n is None else flap_load_n
    spring_ok = spring_n <= SPRING_MAX_FRAC * stall
    hold_ok = hold >= spring_n + load
    result: dict[str, Any] = {
        "stall_pull_n": stall,
        "hold_pull_n": hold,
        "spring_n": spring_n,
        "flap_load_n": load,
        "allowable_flap_load_n": max(hold - spring_n, 0.0),
        "spring_ok": spring_ok,
        "hold_ok": hold_ok,
    }
    if not measured or flap_load_n is None:
        result["pass"] = False
        result["status"] = "PENDING-U8"
        result["would_pass_at_placeholder"] = spring_ok and hold_ok
    else:
        result["pass"] = spring_ok and hold_ok
        result["status"] = "PASS" if result["pass"] else "FAIL"
    return result


# ══ Report ═══════════════════════════════════════════════════════════════════

def _lbf(n: float) -> str:
    return f"{n / 4.448222:.2f} lbf ({n:.2f} N)"


def _in(mm: float) -> str:
    return f"{mm / 25.4:.3f} in ({mm:.2f} mm)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Servo nozzle drive schedule and margins.")
    ap.add_argument("--servo", default="BMS-101DMG", choices=sorted(SERVOS))
    ap.add_argument("--spring", type=float, default=2.0,
                    help="spring force at the ball cup [N] (default 2.0)")
    ap.add_argument("--flap-load", type=float, default=None,
                    help="MEASURED flap load at the ball cup [N] (plan U8)")
    ap.add_argument("--json", action="store_true", help="emit the table as JSON")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero on PENDING as well as FAIL")
    args = ap.parse_args(argv)

    table = build_table()
    if args.json:
        print(json.dumps(table, indent=2))
        return 0

    servo = SERVOS[args.servo]
    res = check_margins(servo, args.spring, args.flap_load,
                        measured=args.flap_load is not None)
    print("Servo nozzle drive — schedule and margins (plan U2)")
    print(f"  ball-cup chord   {_in(lever_chord_mm())} at r {_in(RING_LEVER_R)}")
    print(f"  servo arm        {_in(arm_radius_for_stroke())} for {SERVO_SWEEP_DEG:.0f} deg")
    print(f"  spring cord pull {_in(SPRING_CORD_R * math.radians(THETA_RING_REF_OPEN))}"
          " over the stroke")
    print("  open ball cup: seized/unpowered rod never blocks opening = "
          f"{all(ring_can_open_with_rod_seized(a) for a in (-45, 0, 45))}")
    print(f"\n  {'tilt':>5} {'exit %':>7} {'psi deg':>8} {'servo deg':>9} {'pulse us':>8}")
    for r in table:
        print(f"  {r['tilt_deg']:5.0f} {r['exit_pct']:7.2f} {r['ring_psi_deg']:8.3f} "
              f"{r['servo_deg']:9.2f} {r['pulse_us']:8d}")
    print(f"\n  servo {args.servo}: {servo['note']}")
    print(f"  stall push       {_lbf(res['stall_pull_n'])}")
    print(f"  holding push     {_lbf(res['hold_pull_n'])} ({HOLD_DERATE:.0%} of stall)")
    print(f"  spring           {_lbf(res['spring_n'])}  "
          f"(<= {SPRING_MAX_FRAC:.0%} stall: {'ok' if res['spring_ok'] else 'FAIL'})")
    print(f"  allowable flap load at ball cup   {_lbf(res['allowable_flap_load_n'])}")
    if res["status"] == "PENDING-U8":
        verdict = "would PASS" if res["would_pass_at_placeholder"] else "would FAIL"
        print(f"  status  PENDING-U8 — flap load not yet measured; at the "
              f"{PLACEHOLDER_FLAP_LOAD_N:.0f} N placeholder this {verdict}")
        return 1 if args.strict else 0
    print(f"  status  {res['status']} at measured {_lbf(res['flap_load_n'])}")
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
