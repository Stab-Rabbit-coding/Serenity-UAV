#!/usr/bin/env python3
"""hover_trim_rcs.py -- hover pitch trim, RCS jet authority, CG window and the tilt-vectoring
degraded mode of the tail-EDF aircraft (plan 002 U4, TEDF-04; R8, R23, R24, R29-R33, R39,
R40; KTD2, KTD8, KTD9, KTD15).  PROVISIONAL: every thrust, loss and geometry figure rests on
tools/tail_edf_flow.py (itself a planning model) and on ASSUMED values labelled on every run.

FREE-BODY DIAGRAM (pitch plane; Y aft, Z up, hull frame mm; pitch-up positive).  Isolated:
the whole aircraft in hover.  Forces: weight W at the CG; nacelle thrust T at the tilt pivot
(Y 339.4, Z 146.9), tilted aft of vertical by delta; tail-EDF thrust F_t forward along the tail
axis (Z 165.2); four RCS jets at Y 633.  With r = (y, z) from the CG to the point of
application and F = (F_y, F_z), the nose-up moment is  M = z F_y - y F_z.
  nacelles: d = CG aft of pivot, h_p = CG above pivot:  M = d T cos(delta) - h_p T sin(delta)
  tail EDF: h_t = tail axis above CG:                   M = - h_t F_t
  vertical balance T cos(delta) = W gives the moment balance
       W d - W h_p tan(delta) - h_t F_t = 0   (the plan writes sin(delta) with T = W).
  With the nacelles cancelling the tail thrust (T sin(delta) = F_t) the untrimmed moment is
       M0 = W d - F_t (h_t + h_p)      the couple arm h_t + h_p = z_tail - z_pivot (18.3 mm)
  does not depend on the CG height.  Unknowns 2 (delta, jets) against 2 equations in the
  plane: statically determinate for the trim point.  Jets: force on the aircraft is -F e with
  exhaust direction e = (cos(cant) cos(az), sin(cant), cos(cant) sin(az)) in (X, Y, Z).
CONTROL RESERVE (plan definition): trim use = |M0| / the one-sided jet moment that opposes it;
reserve = (jet moment -/+ |M0|) / I.  R30: trim use <= 50 %.
INERTIA is the ONE pitch inertia of current-specification/auw_ledger.json (`pitch_inertia`).
Momentum and jet speeds come from tail_edf_flow.py: each jet is fed from the duct total
pressure through a scoop (recovery fraction ASSUMED 1.0) with path loss K (ASSUMED 1.0); open
jets add exit area and lower the nozzle speed.

CASES: `ledger` (default) takes mass, CG and inertia from the ledger as it stands, with the plan's
forward and aft moves NOT yet applied (their masses are not in the ledger); `projected` applies
the plan's own CG deltas to the ledger (table values, not recomputed); `plan` is the plan's
planning scenario (6,840 g, CG 2.3 mm aft of the pivot, inertia 225 lbm.in^2) for regression.

One limits list (`limits()`) drives the printout and the exit code.

Run:
    /usr/bin/python3 tools/hover_trim_rcs.py [--case ledger|plan] [--louvre-k 1.0]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Sonnet 5.5, Anthropic) under the author's
direction, 2026-11-17, per `AGENTS.md` section 3 AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tail_edf_flow as tf  # noqa: E402

LEDGER = os.path.join(os.path.dirname(HERE), "current-specification", "auw_ledger.json")
G = 9.80665
LBF_N, LBM_KG, IN_M = 4.44822, 0.45359237, 0.0254
# Geometry, hull frame mm (plan "Hover trim and control limits"; rear-cone fit).
PIVOT_Y, PIVOT_Z = 339.4, 146.9
TAIL_Z = 165.2
JET_Y = 633.0  # exhausts leave the skin from about Y 632 (plan KD20)
JET_R = 43.4  # skin radius at Y 628, mm
FAIRLEAD_Z = 84.0  # ASSUMED belly plane under the pivot (R14)
NACELLE_X = 230.4  # mm, ledger row "Nacelle port rotating assembly"
HOVER_THROTTLE = 0.8
R30_USE_MAX = 0.5  # R30: trim uses no more than 50 % of the pitch control moment


@dataclass(frozen=True)
class Case:
    name: str
    mass_g: float
    cg_y: float
    cg_z: float
    inertia: float  # kg m^2 about the CG, hull X
    source: str

    @property
    def w(self) -> float:
        return self.mass_g * G / 1000.0

    @property
    def d(self) -> float:  # m, CG aft of the pivot (positive aft)
        return (self.cg_y - PIVOT_Y) / 1e3

    @property
    def h_p(self) -> float:  # m, CG above the pivot
        return (self.cg_z - PIVOT_Z) / 1e3

    @property
    def h_t(self) -> float:  # m, tail axis above the CG
        return (TAIL_Z - self.cg_z) / 1e3

    @property
    def arm(self) -> float:  # m, trim couple arm: independent of the CG height
        return (TAIL_Z - PIVOT_Z) / 1e3


def ht_pivot() -> float:
    return PIVOT_Y


def ledger_case() -> Case:
    with open(LEDGER, encoding="utf-8") as fh:
        led = json.load(fh)
    c = led["configs"]["hover_twin_2200"]
    return Case("ledger hover_twin_2200", c["mass_g"], c["cg"][1], c["cg"][2],
                led["pitch_inertia"]["I_kg_m2"],
                "auw_ledger.json; plan moves not applied; nose parts ESTIMATE")


# The plan's own CG chain (plan 002 "Corrected mass baseline"): baseline 0.8 mm aft of the pivot,
# QX unit + speed controller + RCS servos 8.4 mm aft, plus the Flight Engineer box forward 2.3 mm
# aft; mass 6,572 g -> 6,840 g.  The deltas are TAKEN FROM THAT TABLE, not recomputed.
PLAN_ADDS_DELTA_MM = 8.4 - 0.8
PLAN_FE_DELTA_MM = 2.3 - 8.4
PLAN_ADDS_G = 6840.0 - 6572.3


def projected_case(fe_fraction: float = 1.0) -> Case:
    """The corrected ledger with the plan's own deltas applied (fe_fraction of the FE-box move).
    Inertia is the ledger's single value, the moves not priced (flagged, ASSUMED)."""
    base = ledger_case()
    return replace(base, name=f"ledger + plan deltas (FE box move {fe_fraction:.0%})",
                   mass_g=base.mass_g + PLAN_ADDS_G,
                   cg_y=base.cg_y + PLAN_ADDS_DELTA_MM + PLAN_FE_DELTA_MM * fe_fraction,
                   source="ledger with the plan's own CG deltas (table values, not recomputed)")


def plan_case() -> Case:
    cg_z = PIVOT_Z + 10.3  # plan: pivot 0.41 in below the CG
    return Case("plan scenario", 6840.0, PIVOT_Y + 2.3, cg_z, 225.0 * LBM_KG * IN_M ** 2,
                "plan 002 planning estimate; inertia ASSUMED 225 lbm.in^2")


@dataclass(frozen=True)
class Jet:
    az_deg: float  # azimuth about the tail axis, 270 = straight down, 90 = up
    cant_deg: float  # aft cant of the exhaust


DEFAULT_JETS = (Jet(245.0, 25.0), Jet(295.0, 25.0), Jet(45.0, 0.0), Jet(135.0, 0.0))
VENTRAL, UPPER = (0, 1), (2, 3)


@dataclass(frozen=True)
class JetModel:
    bore_m: float = 0.71 * IN_M  # plan: four jets of 0.71 in bore
    k_path: float = 1.0  # ASSUMED scoop + passage + exhaust loss
    scoop_fraction: float = 1.0  # ASSUMED share of the duct total pressure at the scoop

    @property
    def area(self) -> float:
        return math.pi / 4.0 * self.bore_m ** 2

    def a_eff(self, n_open: int) -> float:
        return n_open * self.area / math.sqrt(1.0 + self.k_path)

    def speed(self, p_duct: float, rho: float) -> float:
        return math.sqrt(2.0 * self.scoop_fraction * p_duct / (rho * (1.0 + self.k_path)))


def jet_wrench(case: Case, jet: Jet, force: float) -> tuple[float, float]:
    """(pitch-up moment, yaw moment about Z) in N m of one jet at thrust `force` N."""
    az, cant = math.radians(jet.az_deg), math.radians(jet.cant_deg)
    e = (math.cos(cant) * math.cos(az), math.sin(cant), math.cos(cant) * math.sin(az))
    fx, fy, fz = (-force * c for c in e)
    x = JET_R * math.cos(az) / 1e3
    y = (JET_Y - case.cg_y) / 1e3
    z = (TAIL_Z + JET_R * math.sin(az) - case.cg_z) / 1e3
    return z * fy - y * fz, x * fy - y * fx


@dataclass(frozen=True)
class Setup:
    flow: tf.Inputs
    jm: JetModel = JetModel()
    jets: tuple[Jet, ...] = DEFAULT_JETS


def tail_thrust(su: Setup, theta: float) -> float:
    return tf.operate(su.flow, theta).thrust_n


def pair_capacity(case: Case, su: Setup, theta: float, pair: tuple[int, ...]) -> dict[str, float]:
    """Jets of `pair` open at throttle theta: total pitch moment, yaw per jet, jet speed, Mach."""
    inp = replace(su.flow, a_jets_eff=su.jm.a_eff(len(pair)))
    r = tf.operate(inp, theta)
    v = su.jm.speed(r.p_duct_pa, inp.rho)
    f = inp.rho * su.jm.area * v * v
    m_pitch = sum(jet_wrench(case, su.jets[i], f)[0] for i in pair)
    yaw = max(abs(jet_wrench(case, su.jets[i], f)[1]) for i in pair)
    return {"force": f, "pitch": m_pitch, "yaw": yaw, "mach": v / inp.a_sound,
            "tail_thrust": r.thrust_n}


def untrimmed(case: Case, f_tail: float) -> float:
    """M0 = W d - F_t (h_t + h_p), N m, nose-up positive (nacelles cancel the tail thrust)."""
    return case.w * case.d - f_tail * case.arm


def trim_point(case: Case, su: Setup, theta: float) -> dict[str, float]:
    f_t = tail_thrust(su, theta)
    m0 = untrimmed(case, f_t)
    dn = -pair_capacity(case, su, theta, VENTRAL)["pitch"]  # nose-down capacity, positive
    up = pair_capacity(case, su, theta, UPPER)["pitch"]
    use = abs(m0) / (up if m0 < 0 else dn)
    return {"theta": theta, "f_tail": f_t, "m0": m0, "use": use, "cap_dn": dn, "cap_up": up,
            "res_dn": (dn - m0 if m0 > 0 else dn + abs(m0)) / case.inertia,
            "res_up": (up - abs(m0) if m0 < 0 else up + m0) / case.inertia,
            "yaw_one_upper": pair_capacity(case, su, theta, UPPER)["yaw"]}


def required_tail_thrust(case: Case) -> float:
    """The tail thrust at which the couple alone trims: F_t* = W d / (h_t + h_p)."""
    return case.w * case.d / case.arm


def throttle_for_thrust(su: Setup, f_req: float) -> float:
    """Throttle that gives tail thrust f_req; inf if even 100 % falls short, 0 if f_req <= 0."""
    if f_req <= 0.0:
        return 0.0
    if tail_thrust(su, 1.0) < f_req:
        return math.inf
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if tail_thrust(su, max(mid, 1e-6)) < f_req else (lo, mid)
    return 0.5 * (lo + hi)


def cg_window(case: Case, su: Setup, th_lo: float, th_hi: float,
              use_max: float = R30_USE_MAX) -> tuple[float, float]:
    """(d_min, d_max) m, CG aft of the pivot, that holds trim use <= use_max over the range."""
    lo, hi = -math.inf, math.inf
    for i in range(41):
        th = th_lo + (th_hi - th_lo) * i / 40.0
        f_t = tail_thrust(su, th)
        up = pair_capacity(case, su, th, UPPER)["pitch"]
        dn = -pair_capacity(case, su, th, VENTRAL)["pitch"]
        lo = max(lo, (f_t * case.arm - use_max * up) / case.w)
        hi = min(hi, (f_t * case.arm + use_max * dn) / case.w)
    return lo, hi


def tilt_deg(case: Case, f_tail: float) -> float:
    """Exact moment-balance tilt aft of vertical, deg: tan(delta) = (W d - F_t h_t)/(W h_p)."""
    return math.degrees(math.atan((case.w * case.d - f_tail * case.h_t) / (case.w * case.h_p)))


def tilt_deg_plan_form(case: Case, f_tail: float) -> float:
    """The plan's schedule form, delta = asin((W d - F_t h_t)/(T h_p)) with T = W."""
    return math.degrees(math.asin((case.w * case.d - f_tail * case.h_t) / (case.w * case.h_p)))


def degraded_attitude_deg(case: Case, f_tail: float) -> float:
    """Nose-down body attitude at which the tilted thrust line is vertical: delta - asin(F_t/T)."""
    d = math.radians(tilt_deg(case, f_tail))
    t = case.w / math.cos(d)
    return math.degrees(d - math.asin(min(1.0, f_tail / t)))


def latency_budget_s(case: Case, f_before: float, rate_dps: float,
                     sensor: float = 0.010, bus: float = 0.005, logic: float = 0.010) -> float:
    """Sensor + bus + logic + the tilt move from the schedule at f_before to zero tail thrust."""
    move = abs(tilt_deg(case, 0.0) - tilt_deg(case, f_before))
    return sensor + bus + logic + move / rate_dps


def transient(case: Case, f_tail0: float, t_detect: float, rate_dps: float,
              t_end: float = 2.0, dt: float = 1e-3) -> dict[str, float]:
    """Tail thrust lost at t = 0 with the nacelles held until t_detect, then moved to the zero-
    tail-thrust schedule at rate_dps.  Open loop (no attitude loop): the attitude loop is U17.
    dM = h_t F_t0 - h_p W (tan d(t) - tan d0);  dF_aft = W (tan d(t) - tan d0) + F_t0."""
    d0 = math.radians(tilt_deg(case, f_tail0))
    d1 = math.radians(tilt_deg(case, 0.0))
    t_done = t_detect + abs(d1 - d0) / math.radians(rate_dps)
    phi = om = u = x = z_loss = vz = 0.0
    out: dict[str, float] = {"t_done": t_done}
    t = 0.0
    snap_detect = snap_done = False
    while t < t_end:
        if t < t_detect:
            dl = d0
        elif t < t_done:
            dl = d0 + math.copysign(math.radians(rate_dps) * (t - t_detect), d1 - d0)
        else:
            dl = d1
        dtan = math.tan(dl) - math.tan(d0)
        m = case.h_t * f_tail0 - case.h_p * case.w * dtan
        f_aft = case.w * dtan + f_tail0
        om += m / case.inertia * dt
        phi += om * dt
        u += f_aft / (case.mass_g / 1000.0) * dt
        x += u * dt
        az = G * (math.cos(dl + phi) / math.cos(d0) - 1.0)  # vertical thrust change, up positive
        vz += az * dt
        z_loss -= vz * dt
        t += dt
        if not snap_detect and t >= t_detect:
            snap_detect = True
            out.update(phi_detect_deg=math.degrees(phi), rate_detect_dps=math.degrees(om),
                       u_detect=u, x_detect=x)
        if not snap_done and t >= t_done:
            snap_done = True
            out.update(phi_done_deg=math.degrees(phi), rate_done_dps=math.degrees(om),
                       u_done=u, x_done=x, drop_done=z_loss)
    return out


def sling(case: Case, load_g: float, y: float = PIVOT_Y, z: float = FAIRLEAD_Z,
          swing_deg: float = 0.0) -> tuple[Case, float]:
    """Case with a slung load at the fairlead; returns (new case, extra swing moment N m).
    Swing: the load's horizontal force W_L tan(angle) acts at the fairlead height below the CG."""
    m = case.mass_g + load_g
    cgy = (case.mass_g * case.cg_y + load_g * y) / m
    cgz = (case.mass_g * case.cg_z + load_g * z) / m
    i = (case.inertia + (case.mass_g / 1000.0) * (((case.cg_y - cgy) / 1e3) ** 2
                                                  + ((case.cg_z - cgz) / 1e3) ** 2)
         + (load_g / 1000.0) * (((y - cgy) / 1e3) ** 2 + ((z - cgz) / 1e3) ** 2))
    new = replace(case, name=case.name + f" + {load_g:.0f} g sling", mass_g=m, cg_y=cgy,
                  cg_z=cgz, inertia=i)
    swing = load_g * G / 1000.0 * math.tan(math.radians(swing_deg)) * (cgz - z) / 1e3
    return new, swing


def voltage_inputs(base: tf.Inputs, volts: float, v_ref: float = 24.0) -> tf.Inputs:
    """Free-air thrust and the stall pressure scale with rotor speed squared, i.e. with V^2
    (KV x V; the maker's figures are at 24 V [REF-EDF-003]); flow power then follows V^3."""
    s = (volts / v_ref) ** 2
    return replace(base, t_free_n=base.t_free_n * s, p_stall_full_pa=base.p_stall_full_pa * s)


VOLTAGES = (("full pack 25.2 V", 25.2), ("nominal 22.2 V", 22.2),
            ("end of hover 19.8 V (3.3 V/cell, ASSUMED)", 19.8))


def limits(case: Case, su: Setup) -> list[tuple[str, float, float, bool, str]]:
    """THE limits list: (name, value, limit, ok, unit).  Printout and exit code use it."""
    out: list[tuple[str, float, float, bool, str]] = []
    for th in (HOVER_THROTTLE, 1.0):
        u = trim_point(case, su, th)["use"]
        out.append((f"R30 trim use at {th:.0%} throttle", u, R30_USE_MAX, u <= R30_USE_MAX, ""))
    lo, hi = cg_window(case, su, HOVER_THROTTLE, 1.0)
    d_mm = case.d * 1e3
    out.append(("R23 CG margin to the nearer window edge (negative = outside)",
                min(d_mm - lo * 1e3, hi * 1e3 - d_mm), 0.0,
                lo <= case.d <= hi, "mm"))
    for label, v in VOLTAGES:
        sv = Setup(voltage_inputs(su.flow, v), su.jm, su.jets)
        f_req = required_tail_thrust(case)
        # A CG at or forward of the pivot needs no tail thrust and none can trim it: unreachable.
        th = throttle_for_thrust(sv, f_req) if f_req > 0.0 else math.inf
        out.append((f"throttle for the couple trim, {label}", th, 1.0, th <= 1.0, ""))
        use = trim_point(case, sv, min(th, 1.0))["use"] if math.isfinite(th) else math.inf
        out.append((f"R30 trim use at that throttle, {label}", use, R30_USE_MAX,
                    use <= R30_USE_MAX, ""))
    for name, pair in (("ventral", VENTRAL), ("upper", UPPER)):
        mach = pair_capacity(case, su, 1.0, pair)["mach"]
        out.append((f"{name} jet exit Mach, full throttle", mach, su.flow.mach_limit,
                    mach <= su.flow.mach_limit, ""))
    out += [row for row in tf.limits(su.flow)]
    return out


def lbf_in(nm: float) -> str:
    return f"{nm / LBF_N / IN_M:6.2f} lbf.in ({nm:6.3f} N.m)"


def report(case: Case, su: Setup) -> int:
    print("hover_trim_rcs -- hover trim, RCS authority, CG window, degraded tilt mode")
    print("PROVISIONAL: rests on tail_edf_flow.py (planning model) and ASSUMED jet losses.")
    print(f"Case: {case.name} -- {case.source}")
    print(f"  mass {case.mass_g / 1000.0 / LBM_KG:.2f} lbm ({case.mass_g:.0f} g), CG "
          f"{case.d / IN_M:+.3f} in ({case.d * 1e3:+.1f} mm) aft of the pivot, pivot "
          f"{case.h_p / IN_M:.2f} in below the CG, tail axis {case.h_t / IN_M:.2f} in above; "
          f"couple arm {case.arm / IN_M:.2f} in ({case.arm * 1e3:.1f} mm)")
    print(f"  pitch inertia {case.inertia / (LBM_KG * IN_M ** 2):.0f} lbm.in^2 "
          f"({case.inertia:.4f} kg.m^2), the ledger's single value")
    print(f"  jets: {su.jm.bore_m / IN_M:.2f} in bore, path loss K {su.jm.k_path} ASSUMED, scoop "
          f"fraction {su.jm.scoop_fraction} ASSUMED; ventral {su.jets[0].az_deg:.0f}/"
          f"{su.jets[1].az_deg:.0f} deg canted {su.jets[0].cant_deg:.0f} deg aft; upper "
          f"{su.jets[2].az_deg:.0f}/{su.jets[3].az_deg:.0f} deg radial")
    print("\nTrim by throttle (tail thrust with jets closed; nacelles cancel it):")
    print("  throttle  tail thrust            untrimmed moment            trim use  "
          "reserve dn / up rad/s2   yaw, one upper jet")
    for th in (0.6, 0.8, 1.0):
        t = trim_point(case, su, th)
        print(f"  {th:6.0%}   {tf.lbf(t['f_tail'])}  {lbf_in(t['m0'])} "
              f"{'nose-up' if t['m0'] > 0 else 'nose-dn'}  {t['use']:6.0%}   "
              f"{t['res_dn']:5.1f} / {t['res_up']:5.1f}        {lbf_in(t['yaw_one_upper'])}")
    f_star = required_tail_thrust(case)
    print(f"\nCouple trim point: required tail thrust F_t* = W d / (h_t + h_p) = "
          f"{tf.lbf(f_star)}" + ("  (CG forward of the pivot: no tail thrust trims it)"
                                 if f_star <= 0 else ""))
    for label, v in VOLTAGES:
        sv = Setup(voltage_inputs(su.flow, v), su.jm, su.jets)
        th = throttle_for_thrust(sv, f_star) if f_star > 0.0 else math.inf
        why = "no tail thrust trims a CG at or forward of the pivot" if f_star <= 0.0 \
            else "unreachable (>100 %)"
        print(f"  {label}: throttle {why if math.isinf(th) else f'{th:.0%}'}")
    lo, hi = cg_window(case, su, HOVER_THROTTLE, 1.0)
    lo6, hi6 = cg_window(case, su, 0.6, 1.0)
    print(f"CG window for trim use <= {R30_USE_MAX:.0%}: {lo / IN_M:+.2f} to {hi / IN_M:+.2f} in "
          f"({lo * 1e3:+.1f} to {hi * 1e3:+.1f} mm) aft of the pivot at 80 to 100 % throttle; "
          f"{lo6 / IN_M:+.2f} to {hi6 / IN_M:+.2f} in at 60 to 100 %.")
    print("\nDegraded mode (tail EDF lost; independent monitor and trim logic, R39 R40):")
    print("  tail thrust before loss   moment-balance tilt (exact | plan form)   body attitude")
    for f in (tail_thrust(su, 1.0), tail_thrust(su, HOVER_THROTTLE), 0.5 * tail_thrust(
            su, HOVER_THROTTLE), 0.0):
        print(f"  {tf.lbf(f)}   {tilt_deg(case, f):6.2f} deg | {tilt_deg_plan_form(case, f):6.2f}"
              f" deg    {degraded_attitude_deg(case, f):6.2f} deg nose-down")
    w_ = case.w
    print(f"  at level attitude with zero tail thrust the moment balance needs "
          f"{tilt_deg(case, 0.0):.1f} deg of tilt but the force balance needs 0: tilt alone "
          f"cannot trim an aft CG level; the aircraft drifts aft at "
          f"{math.tan(math.radians(tilt_deg(case, 0.0))):.2f} g until it pitches nose-down "
          f"{degraded_attitude_deg(case, 0.0):.1f} deg.")
    t_hover = tail_thrust(su, HOVER_THROTTLE)
    dm = -w_ * case.h_p
    print(f"  tilt per unit pitch moment {math.degrees(1.0 / (-dm)) * LBF_N * IN_M:5.2f} deg per "
          f"lbf.in; required tilt range {tilt_deg(case, tail_thrust(su, 1.0)):.1f} to "
          f"{tilt_deg(case, 0.0):.1f} deg inside the drive's -5 to +140 deg "
          f"(docs/TILT_DRIVE_CONTROL_SPEC.md)")
    rate = 120.0
    print(f"  latency: sensor 10 ms + bus 5 ms + logic 10 ms (ASSUMED) + move at {rate:.0f} deg/s "
          f"(TILT-CTL-07 requirement) = {latency_budget_s(case, t_hover, rate) * 1e3:.0f} ms; "
          "servo lag, dead time and backlash are UNMEASURED (spec section 7), so no dead-band "
          "check is claimed")
    print("  transient after loss at hover throttle, open loop (attitude loop is U17), "
          "ground effect not modelled (0):")
    print("  detect s | pitch, rate at detection | tilt done s | aft speed, travel, drop")
    for td in (0.1, 0.3, 0.6, 1.0):
        r = transient(case, t_hover, td, rate)
        print(f"   {td:4.1f}    | {r['phi_detect_deg']:5.1f} deg, {r['rate_detect_dps']:5.1f} deg/s"
              f"   | {r['t_done']:5.2f}       | {r['u_done']:4.2f} m/s, {r['x_done']:5.2f} m, "
              f"{r['drop_done']:5.2f} m")
    print("  minimum credited hover height: needs the closed-loop recovery of U17; the drop "
          "above is open loop to the end of the tilt move only.")
    print("  pitch-excursion limit (owner, OQ11, not yet set): detection + tilt time allowed:")
    alpha = case.h_t * t_hover / case.inertia
    for lim in (2.0, 5.0, 10.0):
        print(f"    limit {lim:4.1f} deg -> {math.sqrt(2 * math.radians(lim) / alpha) * 1e3:5.0f}"
              " ms before compensation takes effect")
    dyaw = pair_capacity(case, su, HOVER_THROTTLE, UPPER)["yaw"]
    dtilt = math.degrees(dyaw / (2.0 * (case.w / 2.0) * NACELLE_X / 1e3))
    print(f"\nDegraded yaw (jets lost with the tail EDF): differential nacelle tilt (port +s, "
          f"stbd -s) gives {2.0 * (case.w / 2.0) * NACELLE_X / 1e3 * math.radians(1.0):.3f} N.m "
          f"per deg of s (arm {NACELLE_X:.1f} mm each side); one upper jet's yaw moment "
          f"({lbf_in(dyaw)}) needs s = {dtilt:.2f} deg each side: input to TILT-CTL-02. The tail "
          "rotor's reaction torque acts about the longitudinal axis (roll, not yaw) and drops "
          "away at spin-down; its size needs the rotor speed, which is unmeasured.")
    print("\nDisturbance budget (ASSUMED allowances), sling 100 g at the fairlead:")
    swung, mswing = sling(case, 100.0, swing_deg=10.0)
    print(f"  sling swing 10 deg at the fairlead, {(swung.cg_z - FAIRLEAD_Z):.0f} mm below the "
          f"CG: {lbf_in(mswing)}; slung-load CG {swung.d * 1e3:+.1f} mm from the pivot")
    print(f"  gust + ground effect allowance 0.020 N.m ASSUMED; valve/spool lag 50 ms costs "
          f"{math.degrees(0.020 / case.inertia * 0.05):.1f} deg/s of rate error")
    if case.name == "plan scenario":
        print("\nPlan regression notes (NOT pass criteria; the plan table is the plain screened "
              "ramp, so run with --louvre-k 0): trim use at 100 / 80 / 60 % plan 25 / 0 / 55 %,"
              " this tool "
              + " / ".join(f"{trim_point(case, su, t)['use']:.0%}" for t in (1.0, 0.8, 0.6))
              + "; window plan +1.0 to +3.9 mm, this tool "
              f"{lo * 1e3:+.1f} to {hi * 1e3:+.1f} mm; tilt schedule plan 4.1 / 7.2 / 9.7 / 11.5 /"
              " 12.9 deg at 2.92 / 1.89 / 1.06 / 0.47 / 0 lbf.")
    else:
        print("\nRun --case plan --louvre-k 0 to compare with the plan's trim table.")
    if case.name.startswith("ledger + plan deltas"):
        lo_mm = lo * 1e3
        base = ledger_case()
        frac = (base.cg_y - ht_pivot() + PLAN_ADDS_DELTA_MM - lo_mm) / -PLAN_FE_DELTA_MM
        short = lo_mm - case.d * 1e3
        print(f"  CG shortfall to the window's lower edge: {short:+.1f} mm. Limiting "
              f"the Flight Engineer box move to about {max(0.0, min(1.0, frac)):.0%} of the plan's "
              "reaches that edge (linear, ESTIMATE; owner/G1 decision).")
    print("\nLimits (one list; the exit code uses it):")
    ok_all = True
    for name, val, lim, ok, unit in limits(case, su):
        ok_all &= ok
        print(f"  {'OK  ' if ok else 'FAIL'} {name}: {val:.4g} vs limit {lim:.4g} {unit}")
    print("RESULT: " + ("PASS (provisional)" if ok_all else "FAIL"))
    return 0 if ok_all else 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--case", choices=("ledger", "plan", "projected"), default="ledger")
    ap.add_argument("--louvre-k", type=float, default=tf.Inputs.k_louvre)
    a = ap.parse_args(argv)
    case = {"plan": plan_case, "projected": projected_case}.get(a.case, ledger_case)()
    return report(case, Setup(tf.Inputs(k_louvre=a.louvre_k)))


if __name__ == "__main__":
    sys.exit(main())
