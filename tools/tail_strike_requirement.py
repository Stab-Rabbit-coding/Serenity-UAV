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
import sls_auw_reconcile
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
THIGH_Z = 1925.0        # mm^3 (2 x 14 mm cylinders, 6 mm bore, + web)
THIGH_Z_SOLID = 2219.0
BOSS_CAP_PETG = 6300.0  # N bay boss bearing capacity in CF-PETG
BOLT_R_13LBM = 734.0    # N per bay bolt, resultant, at 13.0 lbm (gear tool lg02_bay_attachment)
BOLT_CAP_PETG = 2100.0  # N, wall + boss + 3 mm plate, CF-PETG
LEG_FRAME_CM3 = 40.64   # 3.0 in leg frame volume, LANDING_GEAR_ANALYSIS.md 11.1
FOS_IMPACT = 4.0
LBF = 4.44822           # N per lbf
# Printed-part re-pricing over the WHOLE aircraft (hull + both nacelles).  An earlier
# version re-priced the hull PRINT subtotal only and under-stated both cases.
D_SOLID, D_SLS = sls_auw_reconcile.deltas()
HULL_MARGIN_MM = 1.0  # mm, hull clearance kept below the skid stroke (CS-2) [ASSUMED, owner to confirm]
SHELLS = ("middle_shell24_2mm_repaired.stl", "rear_shell24_2mm_repaired.stl")


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
        ("FDM re-priced at solid 1.28 g/cc", auw + D_SOLID),
        ("SLS (PA CF, PA11 feet), hull + nacelles", auw + D_SLS),
    ]
    print(f"Design configuration: {nm}, CG Y {cy:.1f} Z {cz:.1f}, k_pitch {k:.1f} mm")
    for lab, m in masses:
        print(f"  {lab:34s} AUW {m:6.0f} g ({m / 453.592:5.2f} lbm), "
              f"{m / 1000 / DESIGN_KG:.3f}x the gear's 13.0 lbm design mass")
    print("\nSkid-first strike (attitude just above tip-back and steeper):")
    print(f"  {'attitude':>8s} {'arm d':>7s} {'m_eff/m':>7s} {'E (SLS)':>12s} "
          f"{'F @10mm':>9s} {'F @20mm':>9s} {'F @30mm':>9s}")
    m = masses[2][1] / 1000   # SLS design mass (heaviest = max hover AUW)
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


def co_strike(m, k, d1, d2, f_gear, f_skid, h=H_DROP, dt=1e-6, skid_k=None):
    """Aft gear pair + skid pair striking together (plan 2026-10-31-002 U1, KTD4).

    Planar rigid body, mass m (kg), pitch radius of gyration k (m), falling at
    v0 = sqrt(2 g h) with no initial rotation.  The aft gear pair is a constant-
    force (plateau) absorber at arm d1; it releases when its downward speed
    reaches zero (ductile wire: no rebound).  The skid pair at arm d2 is either
      * a plateau of f_skid (N), releasing like the gear, or
      * ELASTIC with pair stiffness skid_k (N/mm) when skid_k is given (owner
        decision 2026-10-31: PA12-CF leaf-spring U-frame).  Force = k * stroke; the
        contact persists through rebound and releases when the stroke returns to
        zero, so the stored energy is handed back to the airframe.
    Both forces pitch the nose down (they act aft of the CG).  Gravity is kept.
    Extends the single-contact effective-mass method of
    tools/landing_gear_r6_sizing.py [REF-NCEES-009, rigid-body plane motion].

    Returns energies (J), strokes (mm), peak skid force (N) and the residual state
    for the slap-down onto the fore gear.  'capped' is True if the 1 s limit was hit
    with a contact still active (the result is then not a completed event).
    """
    if d1 < 0 or d2 < 0:
        raise ValueError("co-strike contacts must lie aft of the CG (arms >= 0)")
    i_g = m * k * k
    v0 = math.sqrt(2 * G * h)
    v, w = v0, 0.0                      # CG down-speed, nose-down rate
    s1 = s2 = s_cg = e1 = e2 = 0.0
    s2_max = f2_max = e2_peak = 0.0
    on1 = on2 = True
    t = 0.0
    while (on1 or on2) and t < 1.0:
        f1 = f_gear if on1 else 0.0
        if not on2:
            f2 = 0.0
        elif skid_k is not None:
            f2 = skid_k * 1e3 * max(s2, 0.0)        # N/mm * mm -> N (s2 in m)
        else:
            f2 = f_skid
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
            if skid_k is not None:
                s2 += u2 * dt                       # rebound allowed
                e2 += f2 * u2 * dt
                if s2 > s2_max:
                    s2_max, f2_max, e2_peak = s2, f2, e2
                if s2 <= 0 and s2_max > 0:
                    on2 = False
            elif u2 <= 0:
                on2 = False
            else:
                s2 += u2 * dt
                e2 += f2 * u2 * dt
                s2_max, f2_max, e2_peak = s2, f2, e2
        t += dt
    ke_rot = 0.5 * i_g * w * w
    ke_tr = 0.5 * m * v * v
    return {"ke0": 0.5 * m * v0 * v0, "w_gravity": m * G * s_cg,
            "e_gear": e1, "s_gear_mm": s1 * 1000, "e_skid": e2, "s_skid_mm": s2_max * 1000,
            "s_skid_max_mm": s2_max * 1000, "f_skid_peak": f2_max, "e_skid_peak": e2_peak,
            "ke_rot": ke_rot, "ke_tr": ke_tr, "ke_res": ke_rot + ke_tr, "capped": t >= 1.0}


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


def gear_schedule_at(auw_kg):
    """Gear wire schedule at auw_kg without leaking the gear tool's module state.

    landing_gear_r6_sizing keeps its design mass in module globals; save and
    restore whatever value was set, even if the sizing raises.
    """
    import landing_gear_r6_sizing as lg
    prev = lg.DESIGN_AUW_LBM
    try:
        lg.set_design_auw(auw_kg / 0.45359237)
        return lg.wire_schedule(), lg.CLEARANCE_COMPACT - lg.RESIDUAL_MIN
    finally:
        lg.set_design_auw(prev)


def design_case():
    """Heaviest ledger configuration with SLS printed parts.

    VTOL: every sortie takes off and lands in hover, so the heaviest
    configuration (4000 mAh + 8 oz payload) IS the maximum hover AUW.
    """
    nm, auw, cy, cz, k = max(ledger(), key=lambda c: c[1])
    return nm, (auw + D_SLS) / 1000, cy, cz, k


def part3():
    """Co-strike report at the interim SLS design mass (plan 002 U1-U2)."""
    th0, pt, _f = tip_back()
    _nm, m, cy, cz, k = design_case()
    sched, settle_max = gear_schedule_at(m)
    t = math.radians(th0)
    cgr, spr = rot((cy, cz), t), rot(pt, t)
    d1, d2 = (Y_FOOT_AFT - cgr[0]) / 1000, (spr[0] - cgr[0]) / 1000   # aft of the CG
    f_gear = 2 * sched["f_leg_n"]
    chk0 = co_strike_mesh_check(stroke_mm=0.0, margin_mm=0.0)
    s_allow = chk0["tail_clear_mm"] - HULL_MARGIN_MM
    print(f"\nCO-STRIKE (owner 2026-10-31): aft feet + skid tips together at {th0:.1f} deg")
    print(f"  design mass {m:.3f} kg ({m / 0.45359237:.2f} lbm, SLS, heaviest = max hover AUW; LG-15 final); "
          f"arms: feet {d1 * 1000:.1f} mm, skid {d2 * 1000:.1f} mm aft of CG; k {k:.1f} mm")
    print(f"  re-sized gear at this mass: F_leg {sched['f_leg_n']:.0f} N, ductile d "
          f"{sched['ductile_d_mm']:.2f} mm, spring d {sched['spring_d_mm']:.2f} mm, "
          f"thigh M {sched['thigh_m_nmm'] / 1000:.1f} N.m")
    print(f"  measured hull clearance at skid contact {chk0['tail_clear_mm']:.1f} mm; "
          f"allowed skid stroke = clearance - {HULL_MARGIN_MM:.1f} mm margin = {s_allow:.1f} mm")
    print(f"  {'F_skid pair':>11s} {'gear J':>7s} {'gear mm':>8s} {'skid J':>7s} "
          f"{'skid mm':>8s} {'slap J/leg':>10s}")
    drop = G * m * max(0.0, (cgr[1] - cz) / 1000)
    band = []
    for fs in (0, 250, 500, 750, 1000, 1250, 1500, 2000):
        r = co_strike(m, k / 1000, d1, d2, f_gear, float(fs))
        sl = slap_down_per_leg(r["ke_res"], drop)
        ok = r["s_gear_mm"] <= settle_max and 0 < r["s_skid_mm"] <= s_allow
        if ok:
            band.append(fs)
        note = "  <- meets R2/R3" if ok else ("  (no absorber: hull penetration)" if fs == 0 else "")
        print(f"  {fs:9.0f} N {r['e_gear']:7.1f} {r['s_gear_mm']:8.1f} {r['e_skid']:7.1f} "
              f"{r['s_skid_mm']:8.1f} {sl:10.1f}{note}")
    import skid_mount_loads as sml
    k_skid = 1.0 / sml.solve(sml.E_RIB, *sml.i_of_y()[:2], sml.i_of_y()[3], sml.Y_PAD)[1][-1]
    r = co_strike(m, k / 1000, d1, d2, f_gear, 0.0, skid_k=2 * k_skid)
    sl = slap_down_per_leg(r["ke_res"], drop)
    ok = r["s_gear_mm"] <= settle_max and r["s_skid_max_mm"] <= s_allow
    print(f"  ELASTIC PA12-CF skid, k {k_skid:.1f} N/mm per skid (strut at Y {sml.Y_PAD:.0f}): gear "
          f"{r['e_gear']:.1f} J / {r['s_gear_mm']:.1f} mm; skid peak {r['f_skid_peak'] / 2:.0f} N per skid "
          f"({r['f_skid_peak'] / 2 / LBF:.0f} lbf) at {r['s_skid_max_mm']:.1f} mm, stores {r['e_skid_peak']:.1f} J, "
          f"returns it (net {r['e_skid']:+.2f} J); slap {sl:.1f} J/leg"
          f"{'  <- meets R2/R3' if ok else '  FAILS R2/R3'}{'  [CAPPED]' if r['capped'] else ''}")
    print(f"  R2/R3 band (gear <= {settle_max:.1f} mm, skid <= {s_allow:.1f} mm): "
          + (f"{min(band)}-{max(band)} N pair (of the forces tried)" if band else "NONE -- more skid stroke needed (U4)"))
    dem = m * G * H_DROP * 0.5
    print(f"  slap-down is compared with the tail-down per-leg DEMAND the shared wire is sized for "
          f"({dem:.1f} J/leg = m g h / 2), not an independent fore-leg capacity")
    for st in (5.2, 6.1):
        chk = co_strike_mesh_check(stroke_mm=st)
        print(f"  U4 mesh check ({st} mm skid stroke + {HULL_MARGIN_MM:.1f} mm margin): "
              f"{'PASS' if chk['pass'] else 'FAIL'} -- {chk['reason']}")


def skid_vertex_mask(v, y0=Y_FOOT_AFT, step=0.5, tol=0.6):
    """True where a vertex belongs to a skid tube, identified from geometry.

    At each station (every `step` mm) the skid tubes are their own small
    cross-section loops: outboard (|X| mean > 20 mm), narrow (< 40 mm), with
    their lower edge below Z 125 and top below Z 140 (the tubes rise toward the
    tip).  A vertex is skid when it lies inside such a loop's polygon, grown by
    `tol` mm, at its own station.  Point-in-polygon, not a bounding box: a box
    also caught the hull belly where it passes beside the tubes.
    """
    import shapely
    from shapely.geometry import Polygon
    mask = np.zeros(len(v), bool)
    for f in SHELLS:
        mesh = trimesh.load(os.path.join(STL, f))
        ys = np.arange(max(y0, mesh.bounds[0][1]) + step / 2, mesh.bounds[1][1] + step, step)
        for y in ys:
            yc = min(y, mesh.bounds[1][1] - 0.05)
            sec = mesh.section(plane_origin=[0, yc, 0], plane_normal=[0, 1, 0])
            if sec is None:
                continue
            near = np.where(np.abs(v[:, 1] - y) <= step / 2 + 1e-9)[0]
            if not len(near):
                continue
            for d in sec.discrete:
                if len(d) < 4:
                    continue
                xw, zt = np.ptp(d[:, 0]), d[:, 2].max()
                if abs(d[:, 0].mean()) > 20.0 and xw < 40.0 and d[:, 2].min() < 125.0 and zt < 140.0:
                    poly = Polygon(d[:, [0, 2]]).buffer(tol)
                    hit = shapely.contains_xy(poly, v[near, 0], v[near, 2])
                    mask[near[hit]] = True
        # Tube end caps: the tips curve inboard faster than the section loops
        # track over the last few mm.  The cross-sections show no hull below
        # Z 220 there (docs/TAIL_STRIKE §1), so outboard vertices below Z 140
        # in the last 6 mm of the part are skid end cap.
        if f.startswith("rear"):
            tip = (v[:, 1] > mesh.bounds[1][1] - 6.0) & (np.abs(v[:, 0]) > 20.0) & (v[:, 2] < 140.0)
            mask |= tip
    return mask


def co_strike_mesh_check(stroke_mm, margin_mm=None):
    """U4 acceptance check: at the co-strike the skid tips must be the first aft
    contact about the aft feet, and the hull (every middle+rear vertex that is
    not skid tube) must stay at least stroke + margin above the ground.
    """
    margin_mm = HULL_MARGIN_MM if margin_mm is None else margin_mm
    v = np.vstack([trimesh.load(os.path.join(STL, f)).vertices for f in SHELLS])
    v = v[v[:, 1] > Y_FOOT_AFT + 1.0]
    skid = skid_vertex_mask(v)
    ang = np.degrees(np.arctan2(v[:, 2] - GROUND_Z, v[:, 1] - Y_FOOT_AFT))
    skid_deg, tail_deg = float(ang[skid].min()), float(ang[~skid].min())
    t = math.radians(skid_deg)
    tail_h = float(min(rot((y, z), t)[1] for y, z in v[~skid][:, 1:3])) - GROUND_Z
    need = stroke_mm + margin_mm
    ok = bool(skid_deg < tail_deg and tail_h >= need)
    if skid_deg >= tail_deg:
        reason = f"hull touches first ({tail_deg:.2f} deg vs skids {skid_deg:.2f} deg)"
    elif tail_h < need:
        reason = f"hull only {tail_h:.1f} mm up at skid contact, needs {need:.1f} mm"
    else:
        reason = f"skids lead; hull {tail_h:.1f} mm clear (needs {need:.1f} mm)"
    return {"pass": ok, "skid_deg": skid_deg, "tail_deg": tail_deg,
            "tail_clear_mm": tail_h, "reason": reason}


def part2():
    _nm, m, *_ = design_case()
    sched, _ = gear_schedule_at(m)
    thigh_m = sched["thigh_m_nmm"]
    boss_p = sched["p_wire_n"]
    bolt_r = BOLT_R_13LBM * m / DESIGN_KG     # bolt resultant scales with the leg force
    print(f"\nLanding-gear material re-check at {m / 0.45359237:.2f} lbm (SLS design mass; "
          "gear tool demands; allowable = ult/2)")
    print(f"  {'material':28s} {'leg g':>6s} {'thigh M':>8s} {'thigh solid':>11s} "
          f"{'boss':>6s} {'bolt FOS':>8s} {'stiff':>6s} {'elong':>6s}")
    for name, rho, su, ef, el in MATS:
        allow = su / 2
        thigh = allow / (thigh_m / THIGH_Z)
        thigh_s = allow / (thigh_m / THIGH_Z_SOLID)
        boss = BOSS_CAP_PETG * (su / 55.0) / boss_p
        bolt = BOLT_CAP_PETG * (su / 55.0) / bolt_r
        print(f"  {name:28s} {LEG_FRAME_CM3 * rho:6.1f} {thigh:7.2f}x {thigh_s:10.2f}x "
              f"{boss:5.2f}x {bolt:7.2f} {ef / 6670:5.2f}x {el:5.1f}%")
    print(f"  (pass = 1.00x on thigh and boss; bolt bearing target FOS {FOS_IMPACT})")
    print("  thigh Z needed: " + ", ".join(
        f"{n.split()[0]} {thigh_m / (s / 2):.0f} mm^3 (d x{(thigh_m / (s / 2) / THIGH_Z_SOLID) ** (1 / 3):.2f})"
        for n, _r, s, _e, _l in MATS))


if __name__ == "__main__":
    part1()
    part2()
    part3()
