#!/usr/bin/python3
"""Landing-gear side-hit failure modes: one-pair landings and gear + nacelle co-strikes.

Owner 2026-11-02: "For the side hit failure modes, do the full combined
analysis and record it in the documents.  Right now I'm not planning to change
the landing gear, but I need to know how and when to expect a failure.  Do a
landing on one pair of landing gear, and with a simultaneous landing gear and
nacelle strike.  Repeat the analysis with the nacelle at 0, 45, 90, and 135 deg
tilt."  Results: docs/LG_SIDE_HIT_FAILURE_MODES.md.

Cases (port side; starboard is the exact mirror):
  A  ONE-PAIR landing: the aircraft lands banked port-down at bank phi on the
     two port feet only.
  B  CO-STRIKE: the bank at which the port feet and the port nacelle touch
     together, found from the real nacelle mesh rotated to each tilt about the
     spar axis.  The gear pair and the nacelle then share the impact.

Model (extends the repo's existing method, nothing new):
  * Two-contact planar rigid body with constant-force (plateau) gear:
    tail_strike_requirement.co_strike() [plan 2026-10-31-002 KTD4,
    REF-NCEES-009 rigid-body plane motion], here in the ROLL plane about the
    port feet line.  The nacelle is an ELASTIC contact (skid_k), swept over a
    stiffness range because no nacelle crush stiffness exists.
  * Gear forces from landing_gear_r6_sizing.wire_schedule() at the heaviest
    ledger AUW: ductile plateau F_leg (crash, LG-17, 4 ft) and the spring-row
    elastic limit F_leg x P_spring/P_wire (ordinary, LG-06, 1.5 ft).
  * Leg stress at the thigh root, per leg, from the ground reaction R (normal to
    the ground) resolved into the body frame at bank phi:
      in-plane   M_in  = R cos(phi) x R_H                (sizing-tool basis)
      lateral    F_lat = R sin(phi), out-of-swing-plane share |sin(az)|
      M_out = F_lat_out x h_hip; bending share cos(48.2 deg), torsion sin(48.2 deg)
      sigma = M_in/Z_in + M_out_b/Z_out;  tau = (T/2) r / J (one cylinder,
      conservative); sigma_vm = sqrt(sigma^2 + 3 tau^2).
    The in-plane relief of the inboard lateral force is ignored (conservative).
  * Strength: PA 602-CF UTS 85 MPa (XY, datasheet; no Z value -- a Z-loaded
    print may fail lower).  The sizing tool's impact allowable 27.5 MPa
    (CF-PETG yield/2) is shown for reference.
  * Roll inertia: 2 x 937 g nacelle (nacelle_mass_cg_64) at X 228.5 plus the
    rest at k 55 mm (ESTIMATE; +/-30 % sensitivity reported).

Run:  /usr/bin/python3 tools/lg_side_hit_study.py [--json OUT]

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import hull_datums as hd  # noqa: E402
import landing_gear_r6_sizing as lg  # noqa: E402
import lg_corners  # noqa: E402
import tail_strike_requirement as ts  # noqa: E402

G = 9.80665
R_H = 80.0                 # mm, hip -> foot horizontal arm (canonical_leg R_H)
H_HIP = 118.0              # mm, hip above the sole plane (LG_CORNERS z)
THIGH_ANG = math.degrees(math.atan2(66, 59))   # 48.2 deg below horizontal
Z_IN = 1925.0              # mm^3, in-plane section modulus (tail_strike THIGH_Z)
D_CYL, D_BORE = 14.0, 6.0  # mm, baseline twin thigh cylinders + LG-18 bore
UTS = 85.0                 # MPa, PA 602-CF XY [airframe/datasheets/PA-602-CF-Data-Sheet-2021.pdf]
ALLOW = lg.SIGMA_ALLOW_PETG  # MPa, sizing-tool impact allowable (CF-PETG)
PIN_CAP = 4241.2           # N, M3 SS hip pin double shear (sizing tool)
NAC_G = 936.98             # g per tilting nacelle (nacelle_mass_cg_64 --pod-stl)
NAC_X = 228.5              # mm, nacelle axis span (mesh bounds centre)
K_REST = 55.0              # mm, roll radius of gyration of the non-nacelle mass (ESTIMATE)
TILTS = (0.0, 45.0, 90.0, 135.0)
DROPS_FT = {"ordinary 1.5 ft (LG-06)": 1.5, "crash 4 ft (LG-17)": 4.0}
NAC_K = (100.0, 300.0, 1000.0)   # N/mm, nacelle contact stiffness sweep (no data)
NAC_STL = os.path.join(REPO, "airframe", "stls", "nacelles", "nacelle_port_64mm.stl")

S_OUT = 2 * math.pi * (D_CYL ** 4 - D_BORE ** 4) / (32 * D_CYL)   # 520.6 mm^3
J_CYL = math.pi * (D_CYL ** 4 - D_BORE ** 4) / 32                  # one cylinder


def ledger():
    cfg = json.load(open(lg.LEDGER))["configs"][lg.LEDGER_CONFIG]
    return cfg["mass_g"] / 1000.0, np.array(cfg["cg"], float)


def gear_forces(mass_kg):
    lg.set_design_auw(mass_kg / 0.45359237)
    s = lg.wire_schedule()
    return {"crash": s["f_leg_n"], "ordinary": s["f_leg_n"] * s["p_spring_n"] / s["p_wire_n"]}


def k_roll(mass_kg):
    i = 2 * NAC_G * NAC_X ** 2 + (mass_kg * 1000 - 2 * NAC_G) * K_REST ** 2
    return math.sqrt(i / (mass_kg * 1000)) / 1000.0           # m


def feet():
    c = lg_corners.corners()
    out = {}
    for n in ("fore-port", "aft-port"):
        x, y, _z, az, _h = c[n]
        out[n] = (np.array([x + R_H * math.cos(math.radians(az)),
                            y + R_H * math.sin(math.radians(az)), 0.0]), az)
    return out


def rot_axis(p, a, u, ang):
    """Rotate points p about the line through a with unit direction u (Rodrigues)."""
    q = p - a
    c, s = math.cos(ang), math.sin(ang)
    return a + q * c + np.cross(u, q) * s + np.outer(q @ u, u) * (1 - c)


def tilted_nacelle(v, tilt):
    """Nacelle mesh (baked at tilt 0, nozzle aft) rotated `tilt` deg about the
    spar axis (X through SPAR_Y, SPAR_Z); positive tilt swings the nozzle DOWN
    (90 = nozzle below the pivot, landing_gear_ground_clearance convention)."""
    a = -math.radians(tilt)
    y, z = v[:, 1] - hd.SPAR_Y, v[:, 2] - hd.SPAR_Z
    out = v.copy()
    out[:, 1] = hd.SPAR_Y + y * math.cos(a) - z * math.sin(a)
    out[:, 2] = hd.SPAR_Z + y * math.sin(a) + z * math.cos(a)
    return out


def bank_frame(ft):
    a = ft["fore-port"][0]
    u = ft["aft-port"][0] - a
    u /= np.linalg.norm(u)
    # sign: an outboard (port, +X) point must go DOWN for a port-down bank
    test = rot_axis(np.array([[300.0, a[1], 100.0]]), a, u, 0.1)[0]
    sgn = 1.0 if test[2] < 100.0 else -1.0
    return a, u, sgn


def co_strike_bank(nac_v, ft):
    """Bank (deg) at which the port nacelle's lowest point reaches the ground
    while the port feet are on it, and that contact point (banked frame)."""
    a, u, sgn = bank_frame(ft)
    lo, hi = 0.0, math.radians(89.0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if rot_axis(nac_v, a, u, sgn * mid)[:, 2].min() > 0:
            lo = mid
        else:
            hi = mid
    pts = rot_axis(nac_v, a, u, sgn * hi)
    return math.degrees(hi), pts[np.argmin(pts[:, 2])]


def arm(p, a, u, ref):
    """Horizontal distance from ref to point p, perpendicular to the feet line."""
    d = (p - a) - ((p - a) @ u) * u
    d2 = (ref - a) - ((ref - a) @ u) * u
    return abs(np.hypot(d[0], d[1]) * np.sign(d[0]) - np.hypot(d2[0], d2[1]) * np.sign(d2[0]))


def leg_stress(r, phi_deg, az_deg):
    phi = math.radians(phi_deg)
    m_in = r * math.cos(phi) * R_H
    f_out = r * math.sin(phi) * abs(math.sin(math.radians(az_deg)))
    m_out = f_out * H_HIP
    th = math.radians(THIGH_ANG)
    s_in, s_out = m_in / Z_IN, m_out * math.cos(th) / S_OUT
    tau = (m_out * math.sin(th) / 2) * (D_CYL / 2) / J_CYL
    s = s_in + s_out
    return {"sigma_in": s_in, "sigma_out": s_out, "tau": tau,
            "vm": math.sqrt(s * s + 3 * tau * tau), "pin_n": r}


def phi_crit(r, az_deg, limit):
    lo, hi = 0.0, 89.0
    if leg_stress(r, hi, az_deg)["vm"] < limit:
        return None
    if leg_stress(r, lo, az_deg)["vm"] >= limit:
        return 0.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if leg_stress(r, mid, az_deg)["vm"] < limit:
            lo = mid
        else:
            hi = mid
    return hi


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a_ = ap.parse_args(argv)
    m, cg = ledger()
    fg = gear_forces(m)
    kr = k_roll(m)
    ft = feet()
    a, u, sgn = bank_frame(ft)
    nac = np.asarray(trimesh.load(NAC_STL).vertices)
    res = {"mass_kg": m, "cg": cg.tolist(), "f_leg": fg, "k_roll_m": kr, "cases": []}
    print(f"AUW {m:.3f} kg ({m / 0.45359237:.2f} lbm), CG {np.round(cg, 1).tolist()}, "
          f"k_roll {kr * 1000:.0f} mm (estimate)")
    print(f"F_leg: ordinary (spring limit) {fg['ordinary']:.0f} N, crash (ductile plateau) "
          f"{fg['crash']:.0f} N")
    print("feet: " + ", ".join(
        f"{n} {np.round(p, 1).tolist()} az {az}" for n, (p, az) in ft.items()))

    print("\n== Critical bank (thigh root, per leg; force-limited, "
          "so independent of drop height) ==")
    for case in ("ordinary", "crash"):
        for n, (_p, az) in ft.items():
            pc_u = phi_crit(fg[case], az, UTS)
            pc_a = phi_crit(fg[case], az, ALLOW)
            lvl = leg_stress(fg[case], 0.0, az)["vm"]
            print(f"  {case:8s} {n:9s} az {az:6.1f}: level vm {lvl:5.1f} MPa; "
                  f"exceeds 27.5 MPa at bank {pc_a if pc_a is None else round(pc_a, 1)} deg; "
                  f"reaches UTS 85 at bank {pc_u if pc_u is None else round(pc_u, 1)} deg")
            res["cases"].append({"kind": "phi_crit", "load": case, "leg": n,
                                 "phi_allow": pc_a, "phi_uts": pc_u, "vm_level": lvl})

    print("\n== Case B: co-strike geometry and dynamics (port feet + port nacelle) ==")
    for tilt in TILTS:
        nv = tilted_nacelle(nac, tilt)
        phi, cp = co_strike_bank(nv, ft)
        cg_b = rot_axis(cg[None, :], a, u, sgn * math.radians(phi))[0]
        d1 = arm(a, a, u, cg_b)                 # feet line
        d2 = arm(cp, a, u, cg_b)                # nacelle contact
        print(f"\n tilt {tilt:5.1f} deg: co-strike bank {phi:5.1f} deg; nacelle contact "
              f"{np.round(cp, 1).tolist()}; arms gear {d1:.0f} mm, nacelle {d2:.0f} mm")
        for dl, hft in DROPS_FT.items():
            load = "crash" if hft >= 4 else "ordinary"
            for kn in NAC_K:
                r = ts.co_strike(m, kr, d1 / 1000, d2 / 1000, 2 * fg[load], 0.0,
                                 h=hft * 0.3048, skid_k=kn)
                ls = {n: leg_stress(fg[load], phi, az) for n, (_p, az) in ft.items()}
                worst = max(ls.items(), key=lambda kv: kv[1]["vm"])
                print(f"   {dl:24s} k_nac {kn:6.0f} N/mm: nacelle peak {r['f_skid_peak']:6.0f} N "
                      f"({r['e_skid_peak']:.1f} J, {r['s_skid_max_mm']:.1f} mm); gear pair "
                      f"{r['e_gear']:.1f} J / {r['s_gear_mm']:.1f} mm; worst leg {worst[0]} vm "
                      f"{worst[1]['vm']:.1f} MPa ({worst[1]['vm'] / UTS:.2f} of UTS)")
                res["cases"].append({"kind": "co_strike", "tilt": tilt, "phi": phi,
                                     "contact": cp.tolist(), "d_gear": d1, "d_nac": d2,
                                     "drop": dl, "k_nac": kn, "dyn": r,
                                     "legs": ls})
    print("\n== Case A: one-pair landing (port feet only), crash plateau, by bank ==")
    for phi in (5, 10, 15, 20, 25, 30):
        ls = {n: leg_stress(fg["crash"], phi, az) for n, (_p, az) in ft.items()}
        print(f"  bank {phi:2d} deg: " + "; ".join(
            f"{n} vm {v['vm']:.1f} MPa (in {v['sigma_in']:.1f}, out {v['sigma_out']:.1f}, "
            f"tau {v['tau']:.1f})" for n, v in ls.items()))
        res["cases"].append({"kind": "one_pair", "phi": phi, "legs": ls})
    print(f"\nk_roll sensitivity: +/-30 % k changes the co-strike nacelle peak; rerun with "
          f"K_REST / NAC_X edits.  Hip pin capacity {PIN_CAP:.0f} N vs F_leg crash "
          f"{fg['crash']:.0f} N (resultant <= F_leg here).")
    if a_.json:
        with open(a_.json, "w") as fh:
            json.dump(res, fh, indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
