#!/usr/bin/env python3
"""tail_strike_requirement.py -- 4 ft drop tail strike on the aft skids, and the
landing-gear material re-check in SLS PA11 / PA12 / PA12-CF (DuraForm PA CF).

Part 1, tail strike (same method as tools/landing_gear_r6_sizing.py two_point_case):
  - Geometry from the published meshes in aircraft datum R2: aft feet on the ground
    plane at Y_FOOT_AFT; middle and rear shell vertices aft of the feet.
  - Tip-back angle = the nose-up pitch about the aft-foot line at which the first
    hull or skid vertex reaches the ground.
  - Skid-first drop (attitude above tip-back): one vertical contact at the skid point,
    m_eff = m k^2 / (k^2 + d^2) [REF-NCEES-009 rigid-body plane motion, as in the gear
    tool]; first-contact energy E = 1/2 m_eff v^2, v = sqrt(2 g h), h = 4 ft (LG-17).
  - Plateau force for an available stroke s: F = E / s; skid-point deceleration F/m_eff.
  - Masses: the ledger (FDM CF-PETG at the 1.05 g/cc ledger density), the ledger
    re-priced at the 1.28 g/cc solid density, and the same with SLS PA CF printed parts.

Part 2, gear materials: the gear tool's demands at the 4 ft schedule (thigh moment,
bay-boss wire load, bay-bolt bearing) are checked against each material's allowable on
the tool's own convention (allowable = strength / 2).  The SLS materials publish no
yield for PA CF, so ultimate / 2 is used for all three.  Bearing is taken as 1.27 x
tensile ultimate, the ratio the gear tool uses for CF-PETG (70 / 55 MPa) [ASSUMED for
the SLS nylons: no bearing data in the datasheets].

Sources: 3DS-30108A DuraForm PA CF [REF-MAT-011]; 3D Systems DuraForm PA12 Black and
PA11 Black datasheets (owner-supplied PDFs, 2025); REF-MAT-002 CF-PETG; gear tool.

Run:  /usr/bin/python3 tools/tail_strike_requirement.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction, 2026-10-31.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import json
import math
import os

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
STL = os.path.join(ROOT, "airframe", "stls", "fuselage")
G = 9.80665
H_DROP = 4 * 0.3048
V = math.sqrt(2 * G * H_DROP)
Y_FOOT_AFT, GROUND_Z = 440.7, 0.0          # tools/landing_gear_r6_sizing.py (R2)

# (name, density g/cc, tensile ult MPa, flex modulus MPa, elongation %)
MATS = [
    ("CF-PETG FDM (REF-MAT-002)", 1.28, 55.0, 6670, 2.1),
    ("PA12-CF = DuraForm PA CF", 1.11, 84.0, 7000, 3.8),
    ("PA12 Black", 1.00, 45.0, 1500, 13.7),
    ("PA11 Black", 1.03, 51.0, 1500, 52.6),
]
# Gear-tool demands at the 4 ft schedule (13.0 lbm design mass) -- printed output
# of tools/landing_gear_r6_sizing.py, 2026-10-31.
DESIGN_KG = 13.0 * 0.45359237
THIGH_M = 91.9e3        # N.mm
THIGH_Z = 1925.0        # mm^3 (2 x 14 mm cylinders, 6 mm bore, + web)
THIGH_Z_SOLID = 2219.0
BOSS_P = 7655.0         # N wire load on the bay boss
BOSS_CAP_PETG = 6300.0  # N bay boss bearing capacity in CF-PETG
BOLT_R = 734.0          # N per bay bolt, resultant
BOLT_CAP_PETG = 2100.0  # N, wall + boss + 3 mm plate, CF-PETG
LEG_FRAME_CM3 = 40.64   # 3.0 in leg frame volume, LANDING_GEAR_ANALYSIS.md 11.1
FOS_IMPACT = 4.0
S_SKID_AVAIL = 7.0   # mm, skid protrusion below the hull today [MESH, docs/TAIL_STRIKE §1]


def print_subtotal():
    """Ledger PRINT subtotal (g) at the ledger's 1.05 g/cc."""
    with open(os.path.join(ROOT, "current-specification", "auw_ledger.json")) as f:
        return json.load(f)["subtotals_hover_g"]["PRINT"]


def ledger():
    """Ledger configurations: (name, AUW g, CG Y, CG Z, k_pitch mm)."""
    with open(os.path.join(ROOT, "current-specification", "auw_ledger.json")) as f:
        d = json.load(f)
    out = []
    for name, c in d["configs"].items():
        out.append((name, c["mass_g"], c["cg"][1], c["cg"][2], c["k_pitch_mm"]))
    return out


def tip_back():
    """Nose-up pitch (deg) about the aft-foot line at which the first aft vertex
    touches the ground, and that vertex (Y, Z) at level attitude."""
    best = (90.0, None)
    for f in ("middle_shell24_2mm_repaired.stl", "rear_shell24_2mm_repaired.stl"):
        v = trimesh.load(os.path.join(STL, f)).vertices
        v = v[v[:, 1] > Y_FOOT_AFT + 1.0]
        th = np.degrees(np.arctan2(v[:, 2] - GROUND_Z, v[:, 1] - Y_FOOT_AFT))
        i = int(np.argmin(th))
        if th[i] < best[0]:
            best = (float(th[i]), (float(v[i, 1]), float(v[i, 2])), f)
    return best


def rot(p, th):
    """Rotate a level-attitude (Y, Z) point nose-up by th about the aft foot."""
    y, z = p[0] - Y_FOOT_AFT, p[1] - GROUND_Z
    c, s = math.cos(th), math.sin(th)
    # nose-up: the tail goes down, i.e. points aft of the foot lose height
    return (Y_FOOT_AFT + y * c + z * s, GROUND_Z - y * s + z * c)


def part1():
    th0, pt, f = tip_back()
    print(f"Tip-back: first aft contact at {th0:.1f} deg nose-up about the aft feet "
          f"(Y {Y_FOOT_AFT}); vertex Y {pt[0]:.1f} Z {pt[1]:.1f} in {f}")
    print(f"4 ft drop: v = {V:.2f} m/s ({V / 0.3048:.1f} ft/s, {V * 1.94384:.1f} kt)\n")
    cfgs = ledger()
    nm, auw, cy, cz, k = max(cfgs, key=lambda c: c[1])
    masses = [
        ("ledger, FDM at 1.05 g/cc", auw),
        ("FDM re-priced at solid 1.28 g/cc", auw + print_subtotal() * (1.28 / 1.05 - 1)),
        ("SLS PA CF printed parts (1.11)", auw + print_subtotal() * (1.11 / 1.05 - 1)),
    ]
    print(f"Design configuration: {nm}, CG Y {cy:.1f} Z {cz:.1f}, k_pitch {k:.1f} mm")
    for lab, m in masses:
        print(f"  {lab:34s} AUW {m:6.0f} g ({m / 453.592:5.2f} lbm), "
              f"{m / 1000 / DESIGN_KG:.3f}x the gear's 13.0 lbm design mass")
    print("\nSkid-first strike (attitude just above tip-back and steeper):")
    print(f"  {'attitude':>8s} {'arm d':>7s} {'m_eff/m':>7s} {'E (FDM 1.28)':>12s} "
          f"{'F @10mm':>9s} {'F @20mm':>9s} {'F @30mm':>9s}")
    m = masses[1][1] / 1000
    rows = []
    for th in (th0, th0 + 5, th0 + 10, th0 + 15, th0 + 25, th0 + 35):
        t = math.radians(th)
        cg = rot((cy, cz), t)
        sp = rot(pt, t)
        d = abs(cg[0] - sp[0])
        r = k * k / (k * k + d * d)
        e = 0.5 * r * m * V * V
        rows.append((th, d, r, e))
        f10, f20, f30 = (e / s * 1000 for s in (10, 20, 30))
        print(f"  {th:7.1f}d {d:6.1f}mm {r:7.3f} {e:9.1f} J  {f10:7.0f} N {f20:7.0f} N {f30:7.0f} N")
    emax = max(r[3] for r in rows[:4])
    print(f"  full-KE limit (CG over the skid point): {0.5 * m * V * V:.1f} J")
    # Simultaneous aft gear + tail at tip-back: the aft-gear pair is the contact
    # nearest under the CG; its arm decides how much of the KE it must take.
    t = math.radians(th0)
    cgf = rot((cy, cz), t)
    dg = abs(cgf[0] - Y_FOOT_AFT)
    rg = k * k / (k * k + dg * dg)
    eg = 0.5 * rg * m * V * V
    print(f"\nSimultaneous aft gear + tail at tip-back ({th0:.1f} deg): CG arm to the aft feet "
          f"{dg:.1f} mm, m_eff/m {rg:.3f}; aft pair {eg:.1f} J = {eg / 2:.1f} J per leg "
          f"(gear schedule: 35.3 J per leg at 13.0 lbm)")
    print(f"  gear forces scale with mass at a fixed stroke: x{m / DESIGN_KG:.3f} -> "
          f"F_leg {1148.3 * m / DESIGN_KG:.0f} N vs the 1148 N schedule")
    print(f"\n  REQUIREMENT (worst attitude): skid pair absorbs {emax:.1f} J "
          f"({emax / 1.35582:.1f} ft.lbf) in first contact")
    return emax, m


def co_strike(m, k, d1, d2, f_gear, f_skid, h=H_DROP, dt=1e-6):
    """Aft gear pair + skid pair striking together (plan 2026-10-31-002 U1, KTD4).

    Planar rigid body, mass m (kg), pitch radius of gyration k (m), falling at
    v0 = sqrt(2 g h) with no initial rotation.  Two upward constant-force
    (plateau) absorbers act at horizontal arms d1 (aft feet) and d2 (skid tips)
    aft of the CG (m).  Both forces pitch the nose down, which lifts the aft
    points, so each contact releases when its own downward speed reaches zero.
    Gravity is kept.  This extends the single-contact effective-mass method of
    tools/landing_gear_r6_sizing.py [REF-NCEES-009, rigid-body plane motion].

    Returns energies (J), strokes (mm) and the residual state for the
    slap-down onto the fore gear.
    """
    if d1 < 0 or d2 < 0:
        raise ValueError("co-strike contacts must lie aft of the CG (arms >= 0)")
    i_g = m * k * k
    v0 = math.sqrt(2 * G * h)
    v, w = v0, 0.0                      # CG down-speed, nose-down rate
    s1 = s2 = s_cg = e1 = e2 = 0.0
    on1 = on2 = True
    t = 0.0
    while (on1 or on2) and t < 1.0:
        f1 = f_gear if on1 else 0.0
        f2 = f_skid if on2 else 0.0
        v += (G - (f1 + f2) / m) * dt
        w += (f1 * d1 + f2 * d2) / i_g * dt
        s_cg += v * dt
        u1, u2 = v - w * d1, v - w * d2
        if on1:
            if u1 <= 0:
                on1 = False
            else:
                s1 += u1 * dt
                e1 += f1 * u1 * dt
        if on2:
            if u2 <= 0:
                on2 = False
            else:
                s2 += u2 * dt
                e2 += f2 * u2 * dt
        t += dt
    ke_rot = 0.5 * i_g * w * w
    ke_tr = 0.5 * m * v * v
    return {"ke0": 0.5 * m * v0 * v0, "w_gravity": m * G * s_cg,
            "e_gear": e1, "s_gear_mm": s1 * 1000, "e_skid": e2, "s_skid_mm": s2 * 1000,
            "ke_rot": ke_rot, "ke_tr": ke_tr, "ke_res": ke_rot + ke_tr}


def slap_down_per_leg(ke_res, w_gravity_drop):
    """Energy per fore leg when the nose rotates down onto the fore pair (U2).

    The residual kinetic energy left after the co-strike, plus the work of
    gravity as the CG settles from the tip-back attitude to level, is taken
    entirely by the two fore legs -- conservative: no share returns to the aft
    pair.
    """
    if ke_res < 0 or w_gravity_drop < 0:
        raise ValueError("energies must be non-negative")
    return 0.5 * (ke_res + w_gravity_drop)


def part3():
    """Co-strike report at the interim SLS design mass (plan 002 U1-U2)."""
    import landing_gear_r6_sizing as lg
    th0, pt, _f = tip_back()
    _nm, auw, cy, cz, k = max(ledger(), key=lambda c: c[1])
    m = (auw + print_subtotal() * (1.11 / 1.05 - 1)) / 1000   # SLS PA CF parts
    lg.set_design_auw(m / 0.45359237)
    sched = lg.wire_schedule()
    lg.set_design_auw(13.0)
    t = math.radians(th0)
    cgr, spr = rot((cy, cz), t), rot(pt, t)
    d1, d2 = (Y_FOOT_AFT - cgr[0]) / 1000, (spr[0] - cgr[0]) / 1000   # aft of the CG
    f_gear = 2 * sched["f_leg_n"]
    settle_max = lg.CLEARANCE_COMPACT - lg.RESIDUAL_MIN
    print(f"\nCO-STRIKE (owner 2026-10-31): aft feet + skid tips together at {th0:.1f} deg")
    print(f"  design mass {m:.3f} kg ({m / 0.45359237:.2f} lbm, SLS interim, LG-15 final); "
          f"arms: feet {d1 * 1000:.1f} mm, skid {d2 * 1000:.1f} mm aft of CG; k {k:.1f} mm")
    print(f"  re-sized gear at this mass: F_leg {sched['f_leg_n']:.0f} N, ductile d "
          f"{sched['ductile_d_mm']:.2f} mm, spring d {sched['spring_d_mm']:.2f} mm, "
          f"thigh M {sched['thigh_m_nmm'] / 1000:.1f} N.m")
    print(f"  {'F_skid pair':>11s} {'gear J':>7s} {'gear mm':>8s} {'skid J':>7s} "
          f"{'skid mm':>8s} {'slap J/leg':>10s}")
    drop = G * m * max(0.0, (cgr[1] - cz) / 1000)
    band = []
    for fs in (0, 250, 500, 750, 1000, 1250, 1500):
        r = co_strike(m, k / 1000, d1, d2, f_gear, float(fs))
        sl = slap_down_per_leg(r["ke_res"], drop)
        ok = r["s_gear_mm"] <= settle_max and 0 < r["s_skid_mm"] <= S_SKID_AVAIL
        if ok:
            band.append(fs)
        print(f"  {fs:9.0f} N {r['e_gear']:7.1f} {r['s_gear_mm']:8.1f} {r['e_skid']:7.1f} "
              f"{r['s_skid_mm']:8.1f} {sl:10.1f}{'  <- meets R2/R3' if ok else ''}")
    print(f"  R2/R3 band (gear <= {settle_max:.1f} mm, skid <= {S_SKID_AVAIL:.0f} mm available): "
          + (f"{min(band)}-{max(band)} N pair" if band else "NONE -- more skid stroke needed (U4)"))
    cap = m * G * H_DROP * 0.5
    print(f"  fore-leg capacity (shared wire schedule, re-sized at this mass): {cap:.1f} J/leg tail-down")


def part2():
    print("\nLanding-gear material re-check (gear tool 4 ft demands, allowable = ult/2)")
    print(f"  {'material':28s} {'leg g':>6s} {'thigh M':>8s} {'thigh solid':>11s} "
          f"{'boss':>6s} {'bolt FOS':>8s} {'stiff':>6s} {'elong':>6s}")
    for name, rho, su, ef, el in MATS:
        allow = su / 2
        thigh = allow / (THIGH_M / THIGH_Z)
        thigh_s = allow / (THIGH_M / THIGH_Z_SOLID)
        boss = BOSS_CAP_PETG * (su / 55.0) / BOSS_P
        bolt = BOLT_CAP_PETG * (su / 55.0) / BOLT_R
        print(f"  {name:28s} {LEG_FRAME_CM3 * rho:6.1f} {thigh:7.2f}x {thigh_s:10.2f}x "
              f"{boss:5.2f}x {bolt:7.2f} {ef / 6670:5.2f}x {el:5.1f}%")
    print(f"  (pass = 1.00x on thigh and boss; bolt bearing target FOS {FOS_IMPACT})")
    print("  thigh Z needed: " + ", ".join(
        f"{n.split()[0]} {THIGH_M / (s / 2):.0f} mm^3 (d x{(THIGH_M / (s / 2) / THIGH_Z_SOLID) ** (1 / 3):.2f})"
        for n, _r, s, _e, _l in MATS))


if __name__ == "__main__":
    part1()
    part2()
    part3()
