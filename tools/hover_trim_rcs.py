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
JET_Y = 633.0  # S43 / plan exhaust station (plan KD20: "from about Y 632")
JET_R = 43.4  # S43 skin radius (the plan's Y 628 figure); measured jets carry their own
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
    az_deg: float  # azimuth of the exhaust about the tail axis, 270 = straight down, 90 = up
    cant_deg: float  # aft cant of the exhaust
    y: float = JET_Y  # exhaust station, mm
    r: float = JET_R  # outer skin radius at the exhaust, mm (from the tail axis)
    scoop: float = 1.0  # this scoop's share of the duct total pressure, relative (ASSUMED)
    swirl_deg: float = 0.0  # tangential turn of the exhaust (rotor-exit swirl), ASSUMED 0


# S43 used the plan's jets: 245/295 deg at Y 633 on a 43.4 mm radius.  TEDF-05 (2026-11-17)
# found that pair strikes the skid pods and overhangs the crossbar: the clear ventral pair is
# 255/285 deg at Y 635 or aft.  Skin radii measured on the aft hull (rear_cone_layout_fit.py):
# 39.3 mm at Y 638 (255/285), 42.5 mm at Y 632 (45/135).
SCOOP_Y_MM = 628.0  # KD20 scoop station
PLAN_JETS: tuple[Jet, ...] = (Jet(245.0, 25.0), Jet(295.0, 25.0), Jet(45.0, 0.0), Jet(135.0, 0.0))
DEFAULT_JETS: tuple[Jet, ...] = (
    Jet(255.0, 25.0, 638.0, 39.3), Jet(285.0, 25.0, 638.0, 39.3),
    Jet(45.0, 0.0, 632.0, 42.5), Jet(135.0, 0.0, 632.0, 42.5))
VENTRAL, UPPER = (0, 1), (2, 3)


def unit_force(jet: Jet) -> tuple[float, float, float]:
    """Force on the aircraft per newton of jet thrust: minus the exhaust direction, with the
    exhaust turned tangentially by the jet's swirl angle (X port, Y aft, Z up)."""
    az, cant = math.radians(jet.az_deg + jet.swirl_deg), math.radians(jet.cant_deg)
    e = (math.cos(cant) * math.cos(az), math.sin(cant), math.cos(cant) * math.sin(az))
    return (-e[0], -e[1], -e[2])


def jet_moments(case: Case, jet: Jet, force: float) -> dict[str, float]:
    """Pitch-up, yaw (about +Z) and roll (about +Y) moments, N m, of one jet at `force` N."""
    fx, fy, fz = (force * c for c in unit_force(jet))
    a = math.radians(jet.az_deg)
    x = jet.r * math.cos(a) / 1e3
    y = (jet.y - case.cg_y) / 1e3
    z = (TAIL_Z + jet.r * math.sin(a) - case.cg_z) / 1e3
    return {"pitch": z * fy - y * fz, "yaw": x * fy - y * fx, "roll": z * fx - x * fz}


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
    m = jet_moments(case, jet, force)
    return m["pitch"], m["yaw"]


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
    forces = [inp.rho * su.jm.area * v * v * su.jets[i].scoop for i in pair]  # v^2 ~ scoop share
    ms = [jet_moments(case, su.jets[i], f) for i, f in zip(pair, forces)]
    return {"force": max(forces), "pitch": sum(m["pitch"] for m in ms),
            "yaw": max(abs(m["yaw"]) for m in ms), "pair_yaw": sum(m["yaw"] for m in ms),
            "pair_roll": sum(m["roll"] for m in ms),
            "mach": v * math.sqrt(max(su.jets[i].scoop for i in pair)) / inp.a_sound,
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


def rcs_comparison(case: Case, flow: tf.Inputs) -> None:
    """S43 jets (the plan's) against the TEDF-05 jets, and the swirl / scoop sensitivities."""
    print("\nRCS jets, S43 (plan) against TEDF-05 (force on the aircraft per N of jet thrust; X "
          "port, Y aft, Z up; moments per N about the CG, nose-up / +Z / +Y positive):")
    for label, jets in (("S43 plan", PLAN_JETS), ("TEDF-05", DEFAULT_JETS)):
        for j in jets:
            f = unit_force(j)
            m = jet_moments(case, j, 1.0)
            print(f"  {label:8} az {j.az_deg:5.1f} cant {j.cant_deg:4.1f} Y {j.y:5.1f} r "
                  f"{j.r:4.1f}: F ({f[0]:+.3f}, {f[1]:+.3f}, {f[2]:+.3f})  pitch "
                  f"{m['pitch'] * 1e3:+6.1f}  yaw {m['yaw'] * 1e3:+6.1f}  roll "
                  f"{m['roll'] * 1e3:+6.1f} mm")
    for label, jets in (("S43 plan", PLAN_JETS), ("TEDF-05", DEFAULT_JETS)):
        su = Setup(flow, JetModel(), jets)
        dn = -pair_capacity(case, su, 1.0, VENTRAL)["pitch"]
        up = pair_capacity(case, su, 1.0, UPPER)["pitch"]
        print(f"  {label}: full-throttle capacity nose-down {lbf_in(dn)}, nose-up {lbf_in(up)}")
    print("  sensitivities (TEDF-05 jets, full throttle; ASSUMED magnitudes, no stator yet):")
    for label, mod in (("rotor-exit swirl turns every exhaust +15 deg",
                        {"swirl_deg": 15.0}),
                       ("port scoop recovers 80 % of the starboard",
                        {"scoop_port": 0.8})):
        port = mod.get("scoop_port", 1.0)
        mod_jets = tuple(replace(j, swirl_deg=mod.get("swirl_deg", 0.0),
                                 scoop=port if math.cos(math.radians(j.az_deg)) > 0 else 1.0)
                         for j in DEFAULT_JETS)
        su = Setup(flow, JetModel(), mod_jets)
        v = pair_capacity(case, su, 1.0, VENTRAL)
        u = pair_capacity(case, su, 1.0, UPPER)
        print(f"    {label}: nose-down {lbf_in(-v['pitch'])}, nose-up {lbf_in(u['pitch'])}; "
              f"ventral pair leaves yaw {lbf_in(v['pair_yaw'])} and roll "
              f"{lbf_in(v['pair_roll'])}; upper pair yaw {lbf_in(u['pair_yaw'])} roll "
              f"{lbf_in(u['pair_roll'])}")


def plot_vectors(case: Case, path: str) -> None:
    """Diagram of the four RCS jets: a 3D view and three orthographic views (aft, side, plan).
    Exit points on the skin; red = exhaust direction, blue = force on the aircraft; TEDF-05
    jets in colour, the S43 (plan) jets in grey dashes.  Arrows 25 mm per unit force."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    scale = 25.0
    sets = ((PLAN_JETS, "0.55", "--", "0.55", "S43 plan"),
            (DEFAULT_JETS, "C3", "-", "C0", "TEDF-05"))

    def pts(j: Jet) -> tuple[float, float, float]:
        a = math.radians(j.az_deg)
        return (j.r * math.cos(a), j.y, TAIL_Z + j.r * math.sin(a))

    fig = plt.figure(figsize=(12, 10))
    ax3 = fig.add_subplot(2, 2, 1, projection="3d")
    th = np.linspace(0, 2 * math.pi, 73)
    for y, r in ((628.0, 44.0), (638.0, 39.3)):
        ax3.plot(r * np.cos(th), np.full_like(th, y), TAIL_Z + r * np.sin(th), color="0.8",
                 lw=0.8)
    ax3.plot([0, 0], [600, 665], [TAIL_Z, TAIL_Z], "k-.", lw=1)
    for jets, ec, ls, fc, tag in sets:
        for j in jets:
            p, f = pts(j), unit_force(j)
            ax3.quiver(*p, *(-c * scale for c in f), color=ec, linestyle=ls, lw=1.2,
                       arrow_length_ratio=0.25)
            ax3.quiver(*p, *(c * scale for c in f), color=fc, linestyle=ls, lw=2.0,
                       arrow_length_ratio=0.3)
            ax3.text(*p, f" {j.az_deg:.0f}", fontsize=7, color=ec)
    ax3.set_box_aspect((90, 65, 90))
    ax3.set_xlim(-45, 45)
    ax3.set_ylim(600, 665)
    ax3.set_zlim(TAIL_Z - 45, TAIL_Z + 45)
    ax3.set_xlabel("X port + (mm)")
    ax3.set_ylabel("Y aft + (mm)")
    ax3.set_zlabel("Z up + (mm)")
    ax3.view_init(elev=20, azim=-35)
    ax3.set_title("3D, from aft-starboard-above")
    views = ((2, "", 0, 2),
             (3, "side view from starboard (Y aft right, Z up)", 1, 2),
             (4, "plan view from above (Y aft right, X port up)", 1, 0))
    for n, title, u, v in views:
        ax = fig.add_subplot(2, 2, n)
        if (u, v) == (0, 2):
            title = "aft view, looking FORWARD from behind (port on the left)"
            ax.plot(44 * np.cos(th), TAIL_Z + 44 * np.sin(th), color="0.8", lw=0.8)
            ax.plot(39.3 * np.cos(th), TAIL_Z + 39.3 * np.sin(th), color="0.8", lw=0.8)
            ax.plot([0], [TAIL_Z], "k+")
        else:
            ax.axhline(TAIL_Z if v == 2 else 0.0, color="k", ls="-.", lw=0.8)
            ax.axvline(SCOOP_Y_MM, color="0.6", ls=":", lw=0.8)
            ax.text(SCOOP_Y_MM, (TAIL_Z if v == 2 else 0.0) + 50.0, "scoops Y 628 ",
                    ha="right", va="top", fontsize=7, color="0.4")
        for jets, ec, ls, fc, tag in sets:
            for j in jets:
                p, f = pts(j), unit_force(j)
                ax.annotate("", xy=(p[u] - f[u] * scale, p[v] - f[v] * scale), xytext=(p[u], p[v]),
                            arrowprops=dict(arrowstyle="->", color=ec, ls=ls, lw=1.2))
                ax.annotate("", xy=(p[u] + f[u] * scale, p[v] + f[v] * scale), xytext=(p[u], p[v]),
                            arrowprops=dict(arrowstyle="-|>", color=fc, ls=ls, lw=2.0))
                ax.plot(p[u], p[v], "o", color=ec, ms=3)
                ax.text(p[u], p[v], f" {j.az_deg:.0f}", fontsize=7, color=ec)
        lims = {0: (-55.0, 55.0), 1: (595.0, 675.0), 2: (TAIL_Z - 68.0, TAIL_Z + 55.0)}
        ax.set_xlim(*lims[u])
        ax.set_ylim(*lims[v])
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=9)
        ax.grid(alpha=0.3)
        lab = {0: "X port + (mm)", 1: "Y aft + (mm)", 2: "Z up + (mm)"}
        ax.set_xlabel(lab[u])
        ax.set_ylabel(lab[v])
    ax2 = fig.axes[1]
    ax2.set_xlim(55, -55)  # looking forward from behind: port (+X) on the viewer's right
    fig.legend(handles=[
        matplotlib.lines.Line2D([], [], color="C3", label="TEDF-05 exhaust direction"),
        matplotlib.lines.Line2D([], [], color="C0", lw=2, label="TEDF-05 force on the aircraft"),
        matplotlib.lines.Line2D([], [], color="0.55", ls="--",
                                label="S43 plan jets (245/295 deg at Y 633)"),
        matplotlib.lines.Line2D([], [], color="k", ls="-.", label="tail axis, Z 165.2")],
        loc="lower center", ncol=4, fontsize=8)
    fig.suptitle("RCS jets on the tail cone, 25 mm per unit force; case "
                 f"{case.name}, CG at Y {case.cg_y:.0f} Z {case.cg_z:.0f} (forward, out of view)")
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    fig.savefig(path, dpi=150)
    plt.close(fig)


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
          f"{su.jets[1].az_deg:.0f} deg canted {su.jets[0].cant_deg:.0f} deg aft at Y "
          f"{su.jets[0].y:.0f} r {su.jets[0].r:.1f} mm; upper {su.jets[2].az_deg:.0f}/"
          f"{su.jets[3].az_deg:.0f} deg normal to the axis at Y {su.jets[2].y:.0f} r "
          f"{su.jets[2].r:.1f} mm")
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
    ap.add_argument("--jets", choices=("tedf05", "plan"), default="tedf05",
                    help="tedf05: 255/285 at Y 638 (clear pair, TEDF-05); plan: 245/295 at Y 633")
    ap.add_argument("--plot", help="write the 3D jet-vector diagram to this PNG/SVG path")
    a = ap.parse_args(argv)
    if a.case == "plan":
        case = plan_case()
    elif a.case == "projected":
        case = projected_case()
    else:
        case = ledger_case()
    flow = tf.Inputs(k_louvre=a.louvre_k)
    if a.plot:
        plot_vectors(case, a.plot)
    rc = report(case, Setup(flow, JetModel(), DEFAULT_JETS if a.jets == "tedf05" else PLAN_JETS))
    rcs_comparison(case, flow)
    return rc


if __name__ == "__main__":
    sys.exit(main())
