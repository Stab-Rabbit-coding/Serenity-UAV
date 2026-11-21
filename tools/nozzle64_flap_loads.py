#!/usr/bin/env python3
"""nozzle64_flap_loads.py -- exhaust gas load on the 64 mm iris nozzle flaps, carried to the servo.

WHY THIS EXISTS
---------------
The nozzle drive (plan 2026-09-28-001 KTD3; WBS NAC-64-SERVO-01) was fit-closed against a fail-open
spring of 0.45 lbf (2.0 N) at the ring ear and an ASSUMED flap-load allowance of 0.38 lbf (1.7 N),
"PENDING-U8" bench measurement.  No document computed the gas load.  This tool does, from first
principles, so the servo, the spring and the nozzle geometry can be checked before the bench.

METHOD (owner request 2026-11-21: "resolve the load calculations to ensure the nozzles do their jobs
and the servos do as well")
  1. Geometry is MEASURED: the eight flaps (4 master + 4 seal) are rendered from
     airframe/openscad/nacelles/nacelle_nozzle_iris_64mm.scad at each flap angle phi, and the wetted
     inner radius r(z) is sliced from the mesh.  The design targets (75 % / 105 % of the 32.0 mm
     bore) are defined on the hinge line in the SCAD; the flow sees the inner face.
  2. Internal flow is 1-D incompressible (duct M 0.21, NACELLE_64MM_VERIFICATION.md): the exit
     static
     pressure is ambient (subsonic free jet) and the static pressure at a station of area A is
         p(A) - p_amb = q_e * (1 - (A_e / A)^2),   q_e = 1/2 rho V_e^2  (Bernoulli, lossless).
     The exit dynamic pressure q_e is bounded by three fan models, per nacelle (two fans in series,
     23.24 N each at full throttle, REF-EDF-003; stock exit area ASSUMED = the 64 mm bore):
         constant pressure rise   q_e = q_0 = T_0 / (2 A_0)                    (lower bound)
         constant jet power       q_e from P = 1/2 rho A_e V_e^3 = T_0 V_0 / 2  (nominal)
         constant thrust          q_e = T_0 / (2 A_e)                           (upper bound)
     plus ram: the free-stream dynamic pressure at V_NE 87 kt (flight_limits.json) adds to the duct
     total pressure in forward flight.  A real fan's pressure rises as the nozzle closes, toward its
     shutoff pressure; the constant-thrust bound is used as the design limit for that reason.
  3. Hinge moment: the net pressure acts normal to the flap's inner face, outward (OPENING);
     summed over all flaps about their own tangential hinges,  M = sum( dp * 2 pi r * s * ds ),
     s = distance along the face from the hinge station.  Outer faces see ambient.
  4. Through the spiral cam (pin radius linear in ring angle, SCAD PIN_R_REF_*, TAB_X/TAB_Z) by
     virtual work:  T_ring = M * |d phi / d theta|,  and at the ring ear (ball, r 39.0 mm):
     F_ear = T_ring / r_ear.  Frictionless mechanism: friction is a bench item (KTD3 U8).
  5. Servo capability at the ear: tools/nozzle_servo_linkage_64.py force chain at its WORST
     transmission point, 50.4 N per N.m of servo torque (CM07 linkage re-solve 2026-11-21).
  6. Balanced-hinge study: moving the hinge aft by s_h along the flap turns M into
     sum( dp * 2 pi r * (s - s_h) * ds ); the centre of pressure is where it reaches zero.

Usage:  /usr/bin/python3 tools/nozzle64_flap_loads.py [--json PATH] [--fig PATH]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding) -- owner direction.
AI note: Analysis and tool by Claude (Claude Opus 5.5, Anthropic), 2026-11-21, per AGENTS.md
         section 3.  ENGINEERING REVIEW REQUIRED before any result is applied to hardware.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

REPO = Path(__file__).resolve().parent.parent
SCAD_DIR = REPO / "airframe/openscad/nacelles"
RHO = 1.225                    # kg/m3, ISA sea level
LBF = 4.448222
IN = 25.4
G = 9.80665
# Iris geometry (nacelle_nozzle_iris_64mm.scad, values in effect)
R_HINGE, HINGE_Z, FLAP_L, BORE_R = 34.5, 15.0, 36.0, 32.0
CLOSED_R, OPEN_R = 24.0, 33.6
PIN_C, PIN_O, THETA_OPEN = 36.0, 38.0, 23.75
R_EAR = 39.0                   # ring ear / ball cup radius (nozzle_servo_linkage_64.py B_R)
SPRING_EAR_N = 2.0             # KTD3 fail-open spring at the ball (nozzle_servo_linkage_64.py)
# Fan: QX QF2822-2300KV, 23.24 N (2,370 gf) per fan at full throttle, 24 V (REF-EDF-003);
# two fans in series per nacelle.  Stock exit area ASSUMED equal to the 64 mm bore.
T0 = 2 * 2370.0 * G / 1000.0
A0 = math.pi * (BORE_R / 1000.0) ** 2
V_NE = 87.0 * 0.514444         # m/s, current-specification/flight_limits.json v_ne_kt
EAR_PER_NM = 8.9 / 0.1765      # N at the ear per N.m of servo torque (linkage tool, CM07, worst pt)
KGFCM = 0.0980665
# KST CM07 Technical Specification 2026-05 (continuous zone read off its 7.4 V chart)
CM07: dict[str, Any] = {"stall_kgfcm": {6.0: 1.80, 7.4: 2.10, 8.4: 2.40}, "cont_kgfcm": 0.45}


def phi_closed() -> float:
    return math.degrees(math.asin((R_HINGE - CLOSED_R) / FLAP_L))


def phi_open() -> float:
    return math.degrees(math.asin((R_HINGE - OPEN_R) / FLAP_L))


def tab() -> tuple[float, float]:
    """TAB_X, TAB_Z exactly as the SCAD derives them (pin radius at both reference points)."""
    pc, po = math.radians(phi_closed()), math.radians(phi_open())
    tz = ((PIN_O - R_HINGE) - (PIN_C - R_HINGE) * math.cos(po) / math.cos(pc)) / (
        math.sin(pc) * math.cos(po) / math.cos(pc) - math.sin(po))
    tx = ((PIN_C - R_HINGE) + tz * math.sin(pc)) / math.cos(pc)
    return tx, tz


def dphi_dtheta(phi_deg: float) -> float:
    """|d phi / d theta_ring| at a flap angle (cam: pin radius linear in ring angle)."""
    tx, tz = tab()
    p = math.radians(phi_deg)
    dpin_dphi = abs(-tx * math.sin(p) - tz * math.cos(p))          # mm / rad
    dpin_dtheta = (PIN_O - PIN_C) / math.radians(THETA_OPEN)        # mm / rad
    return dpin_dtheta / dpin_dphi


def theta_of_phi(phi_deg: float) -> float:
    tx, tz = tab()
    p = math.radians(phi_deg)
    pin = R_HINGE + tx * math.cos(p) - tz * math.sin(p)
    return (pin - PIN_C) / (PIN_O - PIN_C) * THETA_OPEN


def flap_profile(phi_deg: float, cache: Path) -> dict:
    """Render the eight flaps at phi and slice the wetted inner radius r(z)."""
    stl = cache / f"flaps_{phi_deg:.3f}.stl"
    if not stl.exists():
        scad = SCAD_DIR / f"_flaps_tmp_{phi_deg:.3f}.scad"
        scad.write_text("use <nacelle_nozzle_iris_64mm.scad>\n"
                        "for (i = [0:7]) rotate([0, 0, i * 45])\n"
                        f"    translate([{R_HINGE}, 0, {HINGE_Z}])\n"
                        f"    rotate([0, -{phi_deg}, 0]) nozzle_flap(seal = (i % 2) == 1);\n")
        try:
            subprocess.run(["openscad", "--backend=manifold", "-o", str(stl), str(scad)],
                           check=True, capture_output=True)
        finally:
            scad.unlink(missing_ok=True)
    m = trimesh.load_mesh(stl, force="mesh")
    zs, rs = [], []
    for z in np.arange(HINGE_Z, m.bounds[1][2], 0.5):
        sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if sec is None:
            continue
        v = np.asarray(sec.vertices)
        zs.append(float(z))
        rs.append(float(np.hypot(v[:, 0], v[:, 1]).min()))
    z, r = np.array(zs), np.array(rs)
    k = int(np.argmin(r))            # the effective exit is the minimum area (no diverging lip)
    return {"z": z[: k + 1], "r": r[: k + 1], "r_exit": float(r[k]), "z_exit": float(z[k])}


def q_exit(a_e: float, model: str, ram: float) -> float:
    """Exit dynamic pressure, Pa, per nacelle, for a fan model plus ram (Pa)."""
    q0 = T0 / (2 * A0)
    if model == "const_dp":
        return q0 + ram
    if model == "const_power":
        v0 = math.sqrt(T0 / (RHO * A0))
        p_jet = 0.5 * T0 * v0
        ve = (2 * p_jet / (RHO * a_e)) ** (1 / 3)
        return 0.5 * RHO * ve ** 2 + ram
    if model == "const_thrust":
        return T0 / (2 * a_e) + ram
    raise ValueError(model)


def hinge_moment(prof: dict, q_e: float, s_hinge: float = 0.0) -> dict:
    """Total opening hinge moment (N.m) of all flaps, and the radial force (N)."""
    z, r = prof["z"] / 1000.0, prof["r"] / 1000.0
    a = math.pi * r ** 2
    a_e = a[-1]
    dp = q_e * (1.0 - (a_e / a) ** 2)
    ds = np.hypot(np.diff(z), np.diff(r))
    s = np.concatenate([[0.0], np.cumsum(ds)])
    w = 2 * math.pi * r
    f = dp * w
    fm = 0.5 * (f[1:] + f[:-1])
    sm = 0.5 * (s[1:] + s[:-1])
    force = float(np.sum(fm * ds))
    mom = float(np.sum(fm * (sm - s_hinge / 1000.0) * ds))
    s_cp = float(np.sum(fm * sm * ds) / force) * 1000.0 if force > 0 else 0.0
    return {"M_Nm": mom, "F_N": force, "s_cp_mm": s_cp, "s_len_mm": float(s[-1] * 1000.0),
            "dp_hinge_Pa": float(dp[0])}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path)
    ap.add_argument("--fig", type=Path, default=REPO / "docs/figures/nozzle64_flap_loads.png")
    a = ap.parse_args(argv)
    cache = Path(tempfile.gettempdir()) / "nozzle64_flap_loads"
    cache.mkdir(exist_ok=True)
    pc, po = phi_closed(), phi_open()
    phis = list(np.linspace(po, pc, 7))
    res: dict[str, Any] = {"phi_closed": pc, "phi_open": po, "tab": tab(), "cases": {}}
    print(f"flap angle open {po:.2f} deg .. closed {pc:.2f} deg; cam tab X/Z {tab()[0]:.3f}/"
          f"{tab()[1]:.3f} mm")
    print(f"per-nacelle static thrust {T0 / LBF:.2f} lbf ({T0:.1f} N); "
          f"q0 (stock exit = bore) {T0 / (2 * A0):.0f} Pa; "
          f"ram at V_NE {0.5 * RHO * V_NE ** 2:.0f} Pa")
    rows = []
    for phi in phis:
        prof = flap_profile(phi, cache)
        a_e = math.pi * (prof["r_exit"] / 1000.0) ** 2
        th = theta_of_phi(phi)
        k = dphi_dtheta(phi)
        for model in ("const_dp", "const_power", "const_thrust"):
            for flight, ram in (("static", 0.0), ("V_NE", 0.5 * RHO * V_NE ** 2)):
                q = q_exit(a_e, model, ram)
                hm = hinge_moment(prof, q)
                f_ear = hm["M_Nm"] * k / (R_EAR / 1000.0)
                rows.append({"phi": phi, "theta_ring": th, "r_exit_mm": prof["r_exit"],
                             "exit_pct_bore": 100 * prof["r_exit"] / BORE_R, "model": model,
                             "flight": flight, "q_e_Pa": q, **hm, "dphi_dtheta": k,
                             "F_ear_N": f_ear})
    res["rows"] = rows
    closed = [r for r in rows if abs(r["phi"] - pc) < 1e-6]
    print("\nCLOSED (cruise setting): measured flow exit r %.2f mm = %.1f %% of bore (target 75 %%)"
          % (closed[0]["r_exit_mm"], closed[0]["exit_pct_bore"]))
    for r in closed:
        print(f"  {r['model']:13s} {r['flight']:6s} q_e {r['q_e_Pa']:7.0f} Pa  radial "
              f"{r['F_N'] / LBF:6.2f} lbf  hinge M {r['M_Nm'] / 0.112985:6.2f} lbf.in "
              f"({r['M_Nm']:.3f} N.m)  ear {r['F_ear_N'] / LBF:5.2f} lbf ({r['F_ear_N']:5.1f} N)")
    openr = [r for r in rows if abs(r["phi"] - po) < 1e-6]
    print("OPEN (hover): flow exit r %.2f mm = %.1f %% of bore (target 105 %%)"
          % (openr[0]["r_exit_mm"], openr[0]["exit_pct_bore"]))
    # servo capability at the ear
    cap = {v: {"stall_N": s * KGFCM * EAR_PER_NM, "cont_N": CM07["cont_kgfcm"] * KGFCM * EAR_PER_NM}
           for v, s in CM07["stall_kgfcm"].items()}
    res["cm07_at_ear"] = cap
    design = max((r for r in closed if r["model"] == "const_thrust"), key=lambda r: r["F_ear_N"])
    nominal = [r for r in closed if r["model"] == "const_power" and r["flight"] == "V_NE"][0]
    need_hold = SPRING_EAR_N + design["F_ear_N"]
    res["need"] = {"hold_design_N": need_hold, "hold_nominal_N": SPRING_EAR_N + nominal["F_ear_N"],
                   "gas_design_N": design["F_ear_N"], "gas_nominal_N": nominal["F_ear_N"]}
    print(f"\nservo must HOLD closed (continuous), design: spring {SPRING_EAR_N} + gas "
          f"{design['F_ear_N']:.1f} = {need_hold:.1f} N ({need_hold / LBF:.2f} lbf) at the ear")
    for v, c in cap.items():
        print(f"  CM07 {v} V: stall {c['stall_N']:.1f} N, "
              f"continuous {c['cont_N']:.2f} N at the ear")
    # balanced hinge
    prof_c = flap_profile(pc, cache)
    a_e = math.pi * (prof_c["r_exit"] / 1000.0) ** 2
    q_d = q_exit(a_e, "const_thrust", 0.5 * RHO * V_NE ** 2)
    bal = []
    for sh in np.arange(0.0, 26.0, 1.0):
        hm = hinge_moment(prof_c, q_d, sh)
        bal.append({"s_hinge_mm": float(sh), "M_Nm": hm["M_Nm"],
                    "F_ear_N": hm["M_Nm"] * dphi_dtheta(pc) / (R_EAR / 1000.0)})
    res["balance"] = bal
    res["s_cp_mm_closed_design"] = hinge_moment(prof_c, q_d)["s_cp_mm"]
    print(f"centre of pressure, closed, design load: s_cp {res['s_cp_mm_closed_design']:.1f} mm "
          f"along the {hinge_moment(prof_c, q_d)['s_len_mm']:.1f} mm wetted face")
    if a.fig:
        figure(res, a.fig, prof_c, cache)
    if a.json:
        a.json.write_text(json.dumps(res, indent=1, default=float))
    return 0


def figure(res: dict, path: Path, prof_c: dict, cache: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = res["rows"]
    fig, axs = plt.subplots(2, 3, figsize=(17, 10))
    # 1 geometry + pressure vectors, closed
    ax = axs[0, 0]
    z, r = prof_c["z"], prof_c["r"]
    ax.plot(z / IN, r / IN, "k", lw=2, label="flap inner face, closed (measured)")
    po = flap_profile(res["phi_open"], cache)
    ax.plot(po["z"] / IN, po["r"] / IN, "0.6", lw=2, label="open")
    ax.axhline(0.75 * BORE_R / IN, color="C2", ls="--", lw=0.8, label="75 % target")
    ax.axhline(1.05 * BORE_R / IN, color="C1", ls="--", lw=0.8, label="105 % target")
    ax.plot([HINGE_Z / IN], [R_HINGE / IN], "o", color="C3", label="hinge")
    a_e = math.pi * (prof_c["r_exit"] / 1000) ** 2
    q = q_exit(a_e, "const_thrust", 0.5 * RHO * V_NE ** 2)
    aa = math.pi * (r / 1000) ** 2
    dp = q * (1 - (a_e / aa) ** 2)
    for i in range(0, len(z), 6):
        ax.annotate("", xy=(z[i] / IN, (r[i] + dp[i] / 2500) / IN), xytext=(z[i] / IN, r[i] / IN),
                    arrowprops=dict(arrowstyle="-|>", color="C0"))
    ax.set_xlabel("nozzle station z, in")
    ax.set_ylabel("radius, in")
    ax.set_title("Statics: gas pressure on the closed flaps pushes them OPEN (blue)\n"
                 "measured wetted face vs the 75 / 105 % targets", fontsize=9)
    ax.legend(fontsize=7)
    # 2 ear force vs flap angle per model (V_NE)
    ax = axs[0, 1]
    for model, c in (("const_dp", "C2"), ("const_power", "C0"), ("const_thrust", "C3")):
        rr = [x for x in rows if x["model"] == model and x["flight"] == "V_NE"]
        ax.plot([x["phi"] for x in rr], [x["F_ear_N"] / LBF for x in rr], "o-", color=c,
                label=model)
    for v, cc in res["cm07_at_ear"].items():
        ax.axhline(cc["stall_N"] / LBF, color="k", lw=0.6, ls=":")
        ax.text(1.5, cc["stall_N"] / LBF, f"CM07 stall {v} V", fontsize=7, va="bottom")
    cont = list(res["cm07_at_ear"].values())[0]["cont_N"]
    ax.axhline((cont - SPRING_EAR_N) / LBF, color="C1", ls="--",
               label="CM07 continuous less spring")
    ax.set_xlabel("flap angle phi, deg (open 1.4 .. closed 17.0)")
    ax.set_ylabel("gas load at the ring ear, lbf")
    ax.set_title("Function: gas load the servo must overcome, full throttle at V_NE", fontsize=9)
    ax.legend(fontsize=7)
    # 3 balance
    ax = axs[0, 2]
    b = res["balance"]
    ax.plot([x["s_hinge_mm"] / IN for x in b], [x["F_ear_N"] / LBF for x in b], "k")
    ax.axhline(0, color="0.5", lw=0.6)
    ax.axhline((cont - SPRING_EAR_N) / LBF, color="C1", ls="--",
               label="CM07 continuous less spring")
    ax.axvline(res["s_cp_mm_closed_design"] / IN, color="C3", ls=":", label="centre of pressure")
    ax.set_xlabel("hinge moved aft along the flap, in")
    ax.set_ylabel("closed-position gas load at the ear, lbf (+ opens)")
    ax.set_title("Balanced-hinge study (design load, closed)", fontsize=9)
    ax.legend(fontsize=7)
    # 4 requirement vs capability per resolution path (continuous hold, closed, design load)
    ax = axs[1, 0]
    bal = {round(x["s_hinge_mm"]): x["F_ear_N"] for x in res["balance"]}
    fs = 1.5
    paths = [("as designed\n(hinge at 0)", SPRING_EAR_N, bal[0]),
             ("R1 balanced\nhinge 10 mm", SPRING_EAR_N, bal[10]),
             ("R2 balanced 11 mm\n+ spring 0.75 N", 0.75, bal[11])]
    xs = np.arange(len(paths))
    ax.bar(xs, [fs * (sp + g) / LBF for _, sp, g in paths], color="C3", alpha=0.7,
           label="required x 1.5 (spring + gas)")
    ax.bar(xs, [sp / LBF for _, sp, _ in paths], color="C1", width=0.4, label="spring part")
    ax.axhline(cont / LBF, color="k", ls="--", label="CM07 continuous at the ear")
    ax.axhline(list(res["cm07_at_ear"].values())[0]["stall_N"] / LBF, color="0.5", ls=":",
               label="CM07 stall at 6 V")
    ax.set_xticks(xs, [p_[0] for p_ in paths], fontsize=8)
    ax.set_ylabel("continuous force at the ear, lbf")
    ax.set_title("Servo: continuous hold required (x1.5) vs CM07, closed, design load", fontsize=9)
    ax.legend(fontsize=7)
    # 5 flap structural FBD: one flap, pressure resultant, hinge and cam-pin reactions
    ax = axs[1, 1]
    m1 = max(r["M_Nm"] for r in res["rows"]) / 8.0
    tx, tz = res["tab"]
    arm = math.hypot(tx, tz)
    f_pin = m1 / (arm / 1000.0)
    ax.plot([0, 36], [0, -10.5], "k", lw=4)
    ax.plot([0], [0], "o", color="C3", ms=9)
    ax.annotate("", xy=(12.6, -3.7 + 6), xytext=(12.6, -3.7),
                arrowprops=dict(arrowstyle="-|>", color="C0", lw=2))
    f_flap = max(r["F_N"] for r in res["rows"]) / 8 / LBF
    ax.text(13, 2.5, f"gas resultant {f_flap:.2f} lbf / flap\n"
            f"at s_cp 12.6 mm", fontsize=7, color="C0")
    ax.annotate("", xy=(-6.9, -3.7 - 5), xytext=(-6.9, -3.7),
                arrowprops=dict(arrowstyle="-|>", color="C3", lw=2))
    ax.text(-14, -11, f"cam pin {f_pin / LBF:.2f} lbf\n({f_pin:.1f} N)", fontsize=7, color="C3")
    ax.set_xlim(-16, 40)
    ax.set_ylim(-14, 8)
    ax.set_aspect("equal")
    sig = m1 * 1000 / (26.0 * 2.5 ** 2 / 6.0)
    ax.set_title(f"Structural: one flap, design load. Root bending {sig:.1f} MPa "
                 f"({sig * 145.04:.0f} psi)\nvs 84 MPa (12,180 psi) PA CF; pin bearing UNVERIFIED",
                 fontsize=9)
    ax.set_xlabel("mm along the flap (hinge at 0)")
    # 6 exit radius vs target
    ax = axs[1, 2]
    rr = [x for x in res["rows"] if x["model"] == "const_thrust" and x["flight"] == "V_NE"]
    ax.plot([x["phi"] for x in rr], [x["exit_pct_bore"] for x in rr], "ko-",
            label="measured flow exit (inner face)")
    hl = [100 * (R_HINGE - FLAP_L * math.sin(math.radians(x["phi"]))) / BORE_R for x in rr]
    ax.plot([x["phi"] for x in rr], hl, "C0--", label="hinge-line radius (what the SCAD targets)")
    ax.axhline(75, color="C2", lw=0.8)
    ax.axhline(105, color="C1", lw=0.8)
    ax.text(10, 75.5, "75 % requirement", fontsize=7, color="C2")
    ax.text(2, 105.5, "105 % requirement", fontsize=7, color="C1")
    ax.set_xlabel("flap angle phi, deg")
    ax.set_ylabel("exit radius, % of the 2.52 in (64 mm) bore")
    ax.set_title("Nozzle function: the flow exit misses both targets by the flap thickness",
                 fontsize=9)
    ax.legend(fontsize=7)
    fig.suptitle("64 mm iris nozzle: gas load on the flaps at full throttle, carried to the servo "
                 "(tools/nozzle64_flap_loads.py)", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    sys.exit(main())
