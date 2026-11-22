#!/usr/bin/env python3
"""nozzle64_hinge_root_brief.py -- Owner Decision Brief F: nozzle hinge at the canonical petal root.

Owner direction 2026-11-21: "There was supposed to be a change in the nozzle petals to be lengthened
so that the hinge is aligned with the canonical roots of the exhaust petals, which can be seen on
the sides and ventral surface of the nacelle, below the cowl that extends aft on the dorsal
surface."  Owner choices the same day: petal tips at the CANONICAL tip; decision brief first.

Options compared (starboard 64 mm nacelle, nacelle-local frame, duct axis +Z from the intake):
  F0  as built: hinge at Z 214.13 (nozzle pocket 199.13 + 15), 36 mm flaps, tips past the shell.
  F1  hinge at the canonical petal root (measured here), flaps to the canonical tip.

Every number is computed here from the repository's meshes and tools:
  * canonical shell  airframe/stls/nacelles/eng_right_shell24_50mm_repaired.stl, placed as
    nacelle_nozzle_servo_64mm.scad nsv_shell() places it (x P64_K, P64_A), ray-probed every 5 deg;
  * gas loads        docs/figures/nozzle64_flap_loads.json (measured F0) and the same 1-D model on a
    flat flap, calibrated to F0, for F1 (ratio method);
  * pod              the published starboard pod mapped back to nacelle-local;
  * A1 bays          theme_n_od_briefs.od3_layout() (OD-3 layout, port frame -> stbd a -> 180 - a);
  * mass and pivot   nacelle_mass_cg_64.roll_up() and current-specification/auw_ledger.json.

Usage:  /usr/bin/python3 tools/nozzle64_hinge_root_brief.py [--json PATH]
Writes docs/figures/odb_theme_n_f.png.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding) -- owner direction.
AI note: Analysis and tool by Claude (Claude Opus 5.5, Anthropic), 2026-11-21, per AGENTS.md
         section 3.  ENGINEERING REVIEW REQUIRED before any result is applied to hardware.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import manifold3d as mf  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nacelle_64_scale as ns  # noqa: E402
import nacelle_mass_cg_64 as nac64  # noqa: E402
import theme_n_od_briefs as tb  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
FIG = REPO / "docs" / "figures"
IN = 25.4
LBF = 4.448222
K, A = ns.get("P64_K"), ns.get("P64_A")
Z_NOZ = ns.get("P64_Z_NOZ")  # 199.13: today's nozzle pocket station
PIVOT = ns.pivot_z()
BORE = 32.0
R_H, T_FLAP = 34.5, 2.5  # hinge circle and flap thickness (iris SCAD)
HINGE_OFF = 15.0  # nozzle frame: ring pocket face -> hinge line
HOUSING_OD_R = 42.6  # today's housing outer radius
RING_EAR_R, RING_STROKE = 39.0, 23.75
EXIT_CLOSED, EXIT_OPEN = 0.75 * BORE, 1.05 * BORE
F0_L = 36.0
DORSAL = (230.0, 310.0)  # the dorsal cowl tongue sector (canonical, measured)
SPRING_N = 2.0
KGFCM = 0.0980665
CM07_CONT = 0.45 * KGFCM
SIGMA_PA_CF = 84.0  # MPa, allowables.json SLS-PA-CF tensile
FLAP_ROOT_W = 26.0  # mm, flap root width (load study, structure)
TAB_ARM = 7.8  # mm, cam follower tab arm (load study)
RHO = tb.RHO_PA_CF


def _man(t: trimesh.Trimesh) -> mf.Manifold:
    return mf.Manifold(
        mf.Mesh(
            vert_properties=np.asarray(t.vertices, np.float32),
            tri_verts=np.asarray(t.faces, np.uint32),
        )
    )


def _tm(x: mf.Manifold) -> trimesh.Trimesh:
    q = x.to_mesh()
    return trimesh.Trimesh(np.asarray(q.vert_properties)[:, :3], np.asarray(q.tri_verts))


def _cz(x: mf.Manifold) -> float:
    return float(_tm(x).center_mass[2])


def _sector(r0, r1, a0, a1, z0, z1) -> mf.Manifold:
    a = np.radians(np.linspace(a0, a1, 60))
    pts = [(r1 * math.cos(t), r1 * math.sin(t)) for t in a]
    pts += [(r0 * math.cos(t), r0 * math.sin(t)) for t in a[::-1]]
    return mf.Manifold.extrude(mf.CrossSection([pts]), z1 - z0).translate([0, 0, z0])


def _ring(r0, r1, z0, z1) -> mf.Manifold:
    return (
        mf.Manifold.cylinder(z1 - z0, r1, r1, 180)
        - mf.Manifold.cylinder(z1 - z0 + 2, r0, r0, 180).translate([0, 0, -1])
    ).translate([0, 0, z0])


# ── canonical shell ─────────────────────────────────────────────────────────────────────────────
def canonical() -> dict[str, Any]:
    m = trimesh.load_mesh(
        REPO / "airframe/stls/nacelles/eng_right_shell24_50mm_repaired.stl", force="mesh"
    )
    m.apply_translation([-155.02, 190.79, 0])
    m.vertices *= [K, K, A]
    zs = np.arange(140.0, 222.01, 0.25)
    azs = np.arange(0, 360, 5)
    R = np.full((len(azs), len(zs)), np.nan)
    for j, az in enumerate(azs):
        a = math.radians(az)
        d = np.array([-math.cos(a), -math.sin(a), 0.0])
        org = np.array([[90 * math.cos(a), 90 * math.sin(a), z] for z in zs])
        loc, ri, _ = m.ray.intersects_location(org, np.tile(d, (len(zs), 1)), multiple_hits=False)
        for p, i in zip(loc, ri):
            R[j, i] = math.hypot(p[0], p[1])
    w = (zs[:-1] >= 165) & (zs[:-1] <= 212)
    root, tip = [], []
    for j in range(len(azs)):
        dr = np.diff(R[j]) / 0.25
        k = int(np.argmin(np.where(w & np.isfinite(dr), dr, 0)))
        root.append(zs[k])
        tip.append(zs[np.where(np.isfinite(R[j]))[0].max()])
    root_a, tip_a = np.array(root), np.array(tip)
    side = ~((azs >= DORSAL[0]) & (azs <= DORSAL[1]))
    return {
        "R": R,
        "zs": zs,
        "azs": azs,
        "root": root_a,
        "tip": tip_a,
        "z_root": float(np.mean(root_a[side])),
        "z_root_range": (float(root_a[side].min()), float(root_a[side].max())),
        "z_tip": float(np.mean(tip_a)),
        "z_dorsal_end": float(root_a[~side].max()),
    }


# ── flap geometry and gas load (1-D, calibrated to the measured F0) ─────────────────────────────
def phi_for(L: float, r_exit: float) -> float:
    a, b = -0.5, 0.6
    f = lambda p: R_H - L * math.sin(p) - T_FLAP * math.cos(p) - r_exit  # noqa: E731
    for _ in range(80):
        c = 0.5 * (a + b)
        if f(a) * f(c) <= 0:
            b = c
        else:
            a = c
    return 0.5 * (a + b)


def loads() -> dict[str, Any]:
    rows = sorted(
        [
            r
            for r in json.loads((FIG / "nozzle64_flap_loads.json").read_text())["rows"]
            if r["model"] == "const_thrust" and r["flight"] == "V_NE"
        ],
        key=lambda r: r["r_exit_mm"],
    )
    re_q = [r["r_exit_mm"] for r in rows]
    qq = [r["q_e_Pa"] for r in rows]
    meas = {"M": [r["M_Nm"] for r in rows][0], "F_ear": [r["F_ear_N"] for r in rows][0]}

    def case(L: float) -> dict[str, Any]:
        pc, po = phi_for(L, EXIT_CLOSED), phi_for(L, EXIT_OPEN)
        dpdt = (pc - po) / math.radians(RING_STROKE)
        th = np.linspace(0, RING_STROKE, 13)
        out = []
        for t in th:
            p = pc + (po - pc) * t / RING_STROKE
            s = np.linspace(0, L, 400)
            r = R_H - T_FLAP * math.cos(p) - s * math.sin(p)
            qe = float(np.interp(r[-1], re_q, qq))
            dp = qe * (1 - (r[-1] / r) ** 4)
            M = float(np.trapezoid(dp * 2 * math.pi * r * s, s) * 1e-9)
            out.append(
                {
                    "theta": float(t),
                    "phi": math.degrees(p),
                    "r_exit": float(r[-1]),
                    "q_e": qe,
                    "M": M,
                    "F_ear": M * dpdt / (RING_EAR_R / 1000),
                }
            )
        tip_z = L * math.cos(pc)
        return {
            "L": L,
            "phi_closed": math.degrees(pc),
            "phi_open": math.degrees(po),
            "dphi_dtheta": dpdt,
            "stroke": out,
            "tip_dz_closed": tip_z,
            "tip_dz_open": L * math.cos(po),
        }

    f0 = case(F0_L)
    cal_M = meas["M"] / f0["stroke"][0]["M"]
    cal_F = meas["F_ear"] / f0["stroke"][0]["F_ear"]
    return {"f0": f0, "cal_M": cal_M, "cal_F": cal_F, "meas": meas, "case": case}


# ── main computation ───────────────────────────────────────────────────────────────────────────
def compute() -> dict[str, Any]:
    can = canonical()
    zr = round(can["z_root"] * 4) / 4  # hinge station, 0.25 mm grid
    ld = loads()
    # F1 flap length: closed tip on the canonical tip station
    L1 = 0.0
    for L in np.arange(40.0, 56.0, 0.05):
        if zr + L * math.cos(phi_for(L, EXIT_CLOSED)) >= can["z_tip"]:
            L1 = round(float(L), 1)
            break
    f1 = ld["case"](L1)
    f0 = ld["f0"]
    for c in (f0, f1):
        for s in c["stroke"]:
            s["M_cal"] = s["M"] * ld["cal_M"]
            s["F_ear_cal"] = s["F_ear"] * ld["cal_F"]
    hinge0 = Z_NOZ + HINGE_OFF
    res: dict[str, Any] = {
        "canonical": {k: v for k, v in can.items() if k not in ("R", "zs", "azs", "root", "tip")},
        "hinge_z": {"F0": hinge0, "F1": zr},
        "L": {"F0": F0_L, "F1": L1},
        "phi": {"F0": [f0["phi_closed"], f0["phi_open"]], "F1": [f1["phi_closed"], f1["phi_open"]]},
        "tip_z_open": {"F0": hinge0 + f0["tip_dz_open"], "F1": zr + f1["tip_dz_open"]},
        "calibration": {"M": ld["cal_M"], "F_ear": ld["cal_F"]},
    }
    # statics
    st = {}
    for name, c in (("F0", f0), ("F1", f1)):
        M = c["stroke"][0]["M_cal"]
        F = c["stroke"][0]["F_ear_cal"]
        Mf = M / 8 * 1000  # N.mm per flap
        st[name] = {
            "M_Nm": M,
            "F_ear_N": F,
            "hold_N": SPRING_N + F,
            "hold_x15_N": 1.5 * (SPRING_N + F),
            "MA_needed_cont": 1.5 * (SPRING_N + F) / CM07_CONT,
            "pin_N": Mf / TAB_ARM,
            "sigma_root_MPa": 6 * Mf / (FLAP_ROOT_W * T_FLAP**2),
            "ear_profile": [(s["theta"], s["F_ear_cal"]) for s in c["stroke"]],
        }
    res["statics"] = st
    # mechanism: F1 nozzle envelope against the pod's neighbours
    z0n = zr - HINGE_OFF
    house = _ring(BORE, HOUSING_OD_R, z0n, zr)
    rings: list[mf.Manifold] = []
    for ph in np.linspace(f1["phi_closed"], f1["phi_open"], 9):
        p = math.radians(ph)
        pts = [
            (R_H, 0.0),
            (R_H - T_FLAP * math.cos(p), T_FLAP * math.sin(p)),
            (
                R_H - L1 * math.sin(p) - T_FLAP * math.cos(p),
                L1 * math.cos(p) + T_FLAP * math.sin(p),
            ),
            (R_H - L1 * math.sin(p), L1 * math.cos(p)),
        ]
        cs = mf.CrossSection([pts])
        if cs.area() <= 0:
            cs = mf.CrossSection([pts[::-1]])
        rings.append(mf.Manifold.revolve(cs, 96).translate([0, 0, zr]))
    fl = rings[0]
    for x in rings[1:]:
        fl = fl + x
    lay = tb.od3_layout()
    near: dict[str, Any] = {}
    oml_bays = {}
    for nm, b in lay["bays"].items():
        a0, a1 = tb.stbd_az(*b["az"])
        if a1 < a0:
            a1 += 360.0
        oml_bays[nm] = (a0, a1, b["z"][0], b["z"][1])
        sec = _sector(34.8, 60.0, a0, a1, b["z"][0], b["z"][1])
        near[f"A1 bay {nm}"] = (house.min_gap(sec, 30), (house ^ sec).volume(), fl.min_gap(sec, 30))
    prm = {}
    for line in (
        (REPO / "airframe/openscad/nacelles/nozzle_servo_linkage_64_params.scad")
        .read_text()
        .splitlines()
    ):
        for part in line.split(";"):
            part = part.strip()
            if part.startswith("NSL_") and "=" in part:
                k, v = part.split("=", 1)
                prm[k.strip()] = v.strip()
    shaft = [float(x) for x in prm["NSL_SHAFT"].strip("[] ").split(",")]
    r_s = math.hypot(shaft[0], shaft[1])
    cm07 = (
        mf.Manifold.cube([7.5, 19.0, 20.5])
        .translate([r_s - 3.75, -20.5, shaft[2] - 16.0])
        .rotate([0, 0, float(prm["NSL_SHAFT_AZ"])])
    )
    near["KST CM07 (today's position)"] = (
        house.min_gap(cm07, 30),
        (house ^ cm07).volume(),
        fl.min_gap(cm07, 30),
    )
    cart = trimesh.load_mesh(
        REPO / "airframe/stls/nacelles/edf_motor_mount_64mm_stage2_stbd.stl", force="mesh"
    )
    cart.apply_translation([0, 0, 103.7])
    cm = _man(cart)
    near["stage-2 cartridge liner"] = (
        house.min_gap(cm, 30),
        (house ^ cm).volume(),
        fl.min_gap(cm, 30),
    )
    can2 = mf.Manifold.cylinder(58.0, 13.9, 13.9, 64).translate([0, 0, 118.9])
    near["motor-2 can (QF2822)"] = (
        house.min_gap(can2, 30),
        (house ^ can2).volume(),
        fl.min_gap(can2, 30),
    )
    slot = _sector(34.7, 39.5, 248 - 4.2, 248 + 4.2, 119.0, Z_NOZ + 1.0)
    near["motor-2 lead slot (az 248)"] = (
        house.min_gap(slot, 30),
        (house ^ slot).volume(),
        fl.min_gap(slot, 30),
    )
    res["interactions"] = {
        k: {
            "housing_gap_mm": float(v[0]),
            "housing_overlap_mm3": float(v[1]),
            "flap_gap_mm": float(v[2]),
        }
        for k, v in near.items()
    }
    res["bays_stbd"] = oml_bays
    res["servo_end_z"] = shaft[2] + 4.5
    # canonical shape: housing OD against the canonical OML at the two stations
    R, zs = can["R"], can["zs"]
    for name, za, zb in (("F0", Z_NOZ, Z_NOZ + 18.0), ("F1", z0n, zr - 1.0)):
        w = (zs >= za) & (zs <= zb)
        if not w.any():
            continue
        rmin = np.nanmin(np.where(np.isfinite(R[:, w]), R[:, w], 99), axis=1)
        pr = HOUSING_OD_R - rmin
        res.setdefault("canonical_check", {})[name] = {
            "housing_proud_azimuths_of_72": int((pr > 0).sum()),
            "housing_proud_max_mm": float(pr.max()),
            "oml_min_r_mm": float(rmin.min()),
        }
    res["canonical_check"]["F0"]["flaps_beyond_canonical_tail_mm"] = float(
        res["tip_z_open"]["F0"] - can["z_tip"]
    )
    res["canonical_check"]["F1"]["flaps_beyond_canonical_tail_mm"] = float(
        res["tip_z_open"]["F1"] - can["z_tip"]
    )
    # weight and balance
    pod = tb.pod_local("stbd")
    pm = _man(pod)
    rho_pod = 1.0
    with tempfile.TemporaryDirectory() as td:
        pp = Path(td) / "pod.stl"
        pod.export(pp)
        ru = nac64.roll_up(pp)
    rows = {r[0]: (r[1], r[2]) for r in ru["rows"]}
    pod_row = next(v for k, v in rows.items() if k.startswith("Pod shell"))
    rho_pod = pod_row[0] / pm.volume()
    big = mf.Manifold.cylinder(60.0, 80, 80, 96).translate([0, 0, zr])
    tongue = _sector(0, 80, 250, 290, z0n, 200)
    rem_aft = (pm ^ big) - tongue
    rem_pkt = pm ^ mf.Manifold.cylinder(HINGE_OFF, 42.9, 42.9, 180).translate([0, 0, z0n])
    crm = cm ^ mf.Manifold.cylinder(60.0, 80, 80, 96).translate([0, 0, z0n])
    rho_c = next(v for k, v in rows.items() if k.startswith("Stage-2"))[0] / cm.volume()
    get = lambda pre: next(v for k, v in rows.items() if k.startswith(pre))  # noqa: E731
    thr, rng, flp, drv = (
        get("Nozzle throat"),
        get("Unison ring"),
        get("8 x nozzle flap"),
        get("Nozzle servo drive"),
    )
    dz = zr - hinge0
    blade = 2.6 / 3.21  # blade share of a flap's mass (36 x 26 x 2.5 mm)
    fscale = 1 + blade * (L1 / F0_L - 1)
    deltas = [
        ("throat + housing", thr[0], thr[1], thr[0], thr[1] + dz),
        ("unison ring", rng[0], rng[1], rng[0], rng[1] + dz),
        (
            f"8 flaps ({F0_L:.0f} -> {L1:.1f} mm)",
            flp[0],
            flp[1],
            flp[0] * fscale,
            zr + (flp[1] - hinge0) * L1 / F0_L,
        ),
        ("servo drive (bellcrank -> short link)", drv[0], drv[1], drv[0] - 1.5, shaft[2] - 3.7),
        (
            "pod skin aft of the hinge (not the dorsal tongue)",
            rem_aft.volume() * rho_pod,
            _cz(rem_aft),
            0.0,
            0.0,
        ),
        (
            "pod material in the new housing pocket",
            rem_pkt.volume() * rho_pod,
            _cz(rem_pkt),
            0.0,
            0.0,
        ),
        ("cartridge liner aft of the housing face", crm.volume() * rho_c, _cz(crm), 0.0, 0.0),
    ]
    # The pivot is the CG of the OFF-axis mass only (roll_up: on-axis items cannot move it), so
    # the moment balance uses the off-axis mass; the AUW delta is unchanged.
    M0, Z0 = sum(r[1] for r in ru["rows"]), ru["cg_z"]
    dM = sum(r[3] - r[1] for r in deltas)
    dMz = sum(r[3] * r[4] - r[1] * r[2] for r in deltas)
    M1 = M0 + dM
    Z1 = (M0 * Z0 + dMz) / M1
    base = nac64.base
    arm0 = res["tip_z_open"]["F0"] - Z0
    arm1 = res["tip_z_open"]["F1"] - Z1
    g30 = base.GROUND_PLANES[base.GEAR_3IN]  # 3.0 in flight gear, the only configuration
    res["weight"] = {
        "rows": deltas,
        "M0_g": M0,
        "M1_g": M1,
        "cg0": Z0,
        "cg1": Z1,
        "pivot_shift_mm": Z1 - Z0,
        "dM_g": dM,
        "dMz_gmm": dMz,
        "auw_delta_g": 2 * dM,
        "arm0": arm0,
        "arm1": arm1,
        "clear_3_F0": base.WING_SPAR_HULL_Z - arm0 - g30,
        "clear_3_F1": base.WING_SPAR_HULL_Z - arm1 - g30,
        "ballast_to_hold_pivot_g_at_z200": M1 * (Z0 - Z1) / (200.0 - Z0),
    }
    res["_plot"] = {"can": can, "f0": f0, "f1": f1}
    return res


# ── figure ─────────────────────────────────────────────────────────────────────────────────────
SHORT = {"pod material in the new housing pocket": "pod, housing pocket",
         "pod skin aft of the hinge (not the dorsal tongue)": "pod skin aft",
         "cartridge liner aft of the housing face": "cartridge liner"}


def flap_line(hz: float, L: float, phi: float, outer: bool = True):
    p = math.radians(phi)
    s = np.array([0.0, L])
    r = R_H - s * math.sin(p) - (0 if outer else T_FLAP * math.cos(p))
    z = hz + s * math.cos(p) + (0 if outer else T_FLAP * math.sin(p))
    return z, r


def figure(res: dict[str, Any]) -> Path:
    P = res["_plot"]
    can, f1 = P["can"], P["f1"]
    h0, h1 = res["hinge_z"]["F0"], res["hinge_z"]["F1"]
    L0, L1 = res["L"]["F0"], res["L"]["F1"]
    st, wb, it = res["statics"], res["weight"], res["interactions"]
    fig, axs = plt.subplots(2, 3, figsize=(19, 11.5))
    i2 = lambda v: v / IN  # noqa: E731

    # (1) statics: FBD of one F1 flap, closed, design load
    ax = axs[0, 0]
    p = math.radians(f1["phi_closed"])
    z, r = flap_line(h1, L1, f1["phi_closed"], outer=False)
    ax.plot(i2(z), i2(r), color="0.3", lw=6, solid_capstyle="butt")
    s = np.linspace(1, L1 - 1, 9)
    rr = R_H - T_FLAP * math.cos(p) - s * math.sin(p)
    dp = 1 - (rr[-1] / rr) ** 4
    nvec = np.array([math.sin(p), math.cos(p)])  # (z, r) outward normal of the inner face
    for si, ri, di in zip(s, rr, dp):
        zz = h1 + si * math.cos(p)
        ax.annotate(
            "",
            xy=(i2(zz), i2(ri)),
            xytext=(i2(zz - 8 * di * nvec[0]), i2(ri - 8 * di * nvec[1])),
            arrowprops=dict(arrowstyle="-|>", color="darkorange", lw=1.2),
        )
    tb.arrow(ax, i2(h1), i2(R_H + 5), 0, -i2(4.5), "tab:blue", "hinge reaction")
    tb.arrow(
        ax,
        i2(h1 + 14),
        i2(R_H + 4),
        0,
        -i2(4.5),
        "tab:green",
        f"cam pin (tab) {st['F1']['pin_N'] / LBF:.2f} lbf ({st['F1']['pin_N']:.1f} N)",
    )
    ax.text(
        i2(h1 + 6),
        i2(26),
        "gas pressure on the inner face (pushes OPEN)",
        color="darkorange",
        fontsize=7,
    )
    txt = (
        f"Design load (full throttle, V_NE, constant-thrust fan; calibrated to the measured F0):\n"
        f"  hinge moment, 8 flaps  F0 {st['F0']['M_Nm'] * 8.8507:.2f} lbf.in "
        f"({st['F0']['M_Nm']:.3f} N.m)"
        f"   F1 {st['F1']['M_Nm'] * 8.8507:.2f} lbf.in ({st['F1']['M_Nm']:.3f} N.m)\n"
        f"  gas at ring ear   F0 {st['F0']['F_ear_N'] / LBF:.2f} lbf ({st['F0']['F_ear_N']:.1f} N)"
        f"   F1 {st['F1']['F_ear_N'] / LBF:.2f} lbf ({st['F1']['F_ear_N']:.1f} N)\n"
        f"  hold x1.5 at ear  F0 {st['F0']['hold_x15_N']:.1f} N   F1 {st['F1']['hold_x15_N']:.1f} N"
        f"  -> CM07 needs MA >= {st['F1']['MA_needed_cont']:.0f} N/N.m at closed\n"
        f"  root bending      F0 {st['F0']['sigma_root_MPa'] * 145.04:.0f} psi   F1 "
        f"{st['F1']['sigma_root_MPa'] * 145.04:.0f} psi ({st['F1']['sigma_root_MPa']:.1f} "
        f"MPa) vs 12,180 psi"
    )
    ax.text(
        0.01,
        0.01,
        txt,
        transform=ax.transAxes,
        fontsize=6.6,
        family="monospace",
        va="bottom",
        bbox=dict(fc="w", alpha=0.9, lw=0),
    )
    ax.set_title("1  Statics — one F1 flap, closed, design load", fontsize=10, loc="left")
    ax.set_xlabel("Z (in) from the intake face")
    ax.set_ylabel("r (in)")
    ax.set_aspect("equal")
    ax.set_ylim(i2(-4), i2(42))
    tb.sec_in(ax, "x")

    # (2) function: exit schedule, both options, section
    ax = axs[0, 1]
    for h, L, ph, col, nm in (
        (h0, L0, res["phi"]["F0"], "0.55", "F0"),
        (h1, L1, res["phi"]["F1"], "tab:red", "F1"),
    ):
        for k, phi in enumerate(ph):
            z, r = flap_line(h, L, phi, outer=False)
            ax.plot(
                i2(z),
                i2(r),
                color=col,
                lw=2.2 if k == 0 else 1.2,
                ls="-" if k == 0 else "--",
                label=f"{nm} {'closed' if k == 0 else 'open'} (inner face)",
            )
    ax.axhline(i2(BORE), color="tab:blue", lw=0.8)
    ax.axhline(i2(EXIT_CLOSED), color="k", lw=0.6, ls=":")
    ax.axhline(i2(EXIT_OPEN), color="k", lw=0.6, ls=":")
    ax.text(i2(150), i2(EXIT_CLOSED) + 0.02, "75 % exit", fontsize=7)
    ax.text(i2(150), i2(EXIT_OPEN) + 0.02, "105 % exit", fontsize=7)
    ax.add_patch(plt.Rectangle((i2(118.9), 0), i2(58.0), i2(13.9), color="0.35", alpha=0.5))
    ax.text(i2(122), i2(6), "motor-2 can", fontsize=7, color="w")
    for zz in (150, 190, 230):
        tb.arrow(ax, i2(zz), i2(18), i2(14), 0, "tab:blue")
    ax.text(i2(150), i2(20.5), "flow", color="tab:blue", fontsize=7)
    ax.set_xlim(i2(110), i2(258))
    ax.set_ylim(0, i2(40))
    ax.set_title(
        f"2  Function — exit schedule met by both; F1 hinge Z {i2(h1):.2f} in, "
        f"flaps {i2(L1):.2f} in",
        fontsize=10,
        loc="left",
    )
    ax.set_xlabel("Z (in)")
    ax.set_ylabel("r (in)")
    ax.legend(fontsize=7, loc="lower right")
    tb.sec_in(ax, "x")

    # (3) structure: radial budget at the F1 housing station
    ax = axs[0, 2]
    cc = res["canonical_check"]
    stack = [
        ("throat wall", BORE, R_H),
        ("unison ring + cam", R_H, 40.1),
        ("housing", 40.6, HOUSING_OD_R),
    ]
    for k, (nm, a, b) in enumerate(stack):
        ax.barh(0, b - a, left=a, color=["0.6", "tab:blue", "0.8"][k], edgecolor="k")
        ax.text((a + b) / 2, 0.0, nm, ha="center", va="center", fontsize=7, rotation=90)
    ax.axvline(cc["F1"]["oml_min_r_mm"], color="tab:red", lw=2)
    ax.text(
        cc["F1"]["oml_min_r_mm"] + 0.1,
        0.42,
        f"canonical OML, min r\n{cc['F1']['oml_min_r_mm']:.2f} mm",
        color="tab:red",
        fontsize=7,
    )
    ax.axvline(BORE, color="tab:blue")
    ax.annotate(
        "",
        xy=(HOUSING_OD_R, -0.5),
        xytext=(cc["F1"]["oml_min_r_mm"], -0.5),
        arrowprops=dict(arrowstyle="<->", color="tab:red"),
    )
    ax.text(
        41.0,
        -0.62,
        f"proud {cc['F1']['housing_proud_max_mm']:.1f} mm at "
        f"{cc['F1']['housing_proud_azimuths_of_72']} of 72 az",
        fontsize=7,
        color="tab:red",
    )
    for y, lab in ((0.25, "pin load"), (-0.25, "ring -> housing -> pod")):
        tb.arrow(ax, 36.0, y, 2.5, 0, "tab:green", lab)
    ax.set_xlim(31, 44)
    ax.set_ylim(-0.8, 0.8)
    ax.set_yticks([])
    ax.set_xlabel("r (mm) at the F1 housing station")
    ax.set_title(
        f"3  Structure — radial room {cc['F1']['oml_min_r_mm'] - BORE:.1f} mm vs today's "
        f"{HOUSING_OD_R - BORE:.1f} mm stack",
        fontsize=10,
        loc="left",
    )
    ax.text(
        31.2,
        0.62,
        f"F1 flap root {st['F1']['sigma_root_MPa'] * 145.04:.0f} psi "
        f"({st['F1']['sigma_root_MPa']:.1f} MPa) of 12,180 psi;\ncam pin {st['F1']['pin_N']:.1f} N "
        f"(F0 {st['F0']['pin_N']:.1f} N), bearing requires verification",
        fontsize=7,
    )

    # (4) mechanism: unrolled azimuth x Z map, starboard
    ax = axs[1, 0]
    for nm, (a0, a1, z0, z1) in res["bays_stbd"].items():
        ax.add_patch(plt.Rectangle((z0, a0), z1 - z0, a1 - a0, color="tab:purple", alpha=0.25))
        ax.text(z0 + 1, (a0 + a1) / 2, f"A1 {nm}", fontsize=7, color="purple")
    ax.add_patch(plt.Rectangle((h1 - HINGE_OFF, 0), HINGE_OFF, 360, color="tab:red", alpha=0.25))
    ax.add_patch(plt.Rectangle((h1, 0), L1, 360, color="tab:red", alpha=0.08))
    ax.add_patch(plt.Rectangle((Z_NOZ, 0), 18.0, 360, color="0.5", alpha=0.25))
    ax.add_patch(plt.Rectangle((h0, 0), L0, 360, color="0.5", alpha=0.08))
    ax.text(h1 - 14, 345, "F1 ring + housing", fontsize=7, color="tab:red")
    ax.text(h1 + 2, 330, "F1 petals", fontsize=7, color="tab:red")
    ax.text(Z_NOZ + 1, 345, "F0 housing", fontsize=7)
    ax.add_patch(
        plt.Rectangle((res["servo_end_z"] - 20.5, 253), 20.5, 27, color="tab:red", alpha=0.7)
    )
    ax.text(res["servo_end_z"] - 20, 283, "CM07", fontsize=7, color="darkred")
    ax.add_patch(plt.Rectangle((119.0, 244), Z_NOZ - 119.0, 8.4, color="tab:orange", alpha=0.6))
    ax.text(121, 236, "motor-2 lead slot", fontsize=7, color="tab:orange")
    ax.add_patch(
        plt.Rectangle(
            (h1 - HINGE_OFF, 250), 197 - (h1 - HINGE_OFF), 40, fill=False, ls="--", color="k"
        )
    )
    ax.text(185, 292, "dorsal cowl tongue", fontsize=7)
    # ring motion vector (F1 ear)
    ax.annotate(
        "",
        xy=(h1 - HINGE_OFF + 4, 292.5 - RING_STROKE),
        xytext=(h1 - HINGE_OFF + 4, 292.5),
        arrowprops=dict(arrowstyle="-|>", color="tab:blue", lw=1.8),
    )
    ax.text(
        h1 - HINGE_OFF + 5, 280, "ring ear stroke\n(closed -> open)", fontsize=7, color="tab:blue"
    )
    lines = []
    for k, v in it.items():
        flag = (
            "CLASH"
            if v["housing_overlap_mm3"] > 0.5
            else ("tight" if min(v["housing_gap_mm"], v["flap_gap_mm"]) < 2.0 else "clear")
        )
        ov = v["housing_overlap_mm3"]
        ovs = f" / {ov:,.0f} mm3" if ov > 0.5 else ""
        lines.append(
            f"{k:28s} housing {v['housing_gap_mm']:5.2f} mm{ovs}"
            f"  petals {v['flap_gap_mm']:5.2f} mm  {flag}"
        )
    ax.text(
        0.01,
        0.01,
        "\n".join(lines),
        transform=ax.transAxes,
        fontsize=6.3,
        family="monospace",
        va="bottom",
        bbox=dict(fc="w", alpha=0.85, lw=0),
    )
    ax.set_xlim(85, 262)
    ax.set_ylim(0, 360)
    ax.set_xlabel("Z (mm)")
    ax.set_ylabel("azimuth (deg, starboard; 90 ventral, 270 top)")
    ax.set_title("4  Mechanism — unrolled map of the aft pod, F1 vs F0", fontsize=10, loc="left")

    # (5) weight and balance
    ax = axs[1, 1]
    ax.axhline(0, color="k", lw=0.8)
    for nm, m0, z0, m1, z1 in wb["rows"]:
        if m0 > 0:
            ax.annotate(
                "",
                xy=(i2(z0), -m0),
                xytext=(i2(z0), 0),
                arrowprops=dict(arrowstyle="-|>", color="0.5", lw=1.3),
            )
        if m1 > 0:
            ax.annotate(
                "",
                xy=(i2(z1), m1),
                xytext=(i2(z1), 0),
                arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=1.3),
            )
    ax.annotate(
        "",
        xy=(i2(wb["cg1"]), 40),
        xytext=(i2(wb["cg0"]), 40),
        arrowprops=dict(arrowstyle="-|>", color="k", lw=2),
    )
    ax.text(i2(wb["cg1"]) - 0.4, 44, f"CG / pivot {wb['pivot_shift_mm']:+.1f} mm", fontsize=8)
    ax.text(
        0.01,
        0.02,
        f"tilting group {wb['M0_g'] / 453.6:.3f} -> {wb['M1_g'] / 453.6:.3f} lbm "
        f"({wb['M0_g']:.0f} -> {wb['M1_g']:.0f} g); AUW {wb['auw_delta_g'] / 453.6:+.3f} lbm "
        f"({wb['auw_delta_g']:+.0f} g, both nacelles)\n"
        f"pivot re-converges {i2(wb['pivot_shift_mm']):+.3f} in ({wb['pivot_shift_mm']:+.1f} "
        f"mm); holding it "
        f"needs {wb['ballast_to_hold_pivot_g_at_z200']:.0f} g ballast at Z 200 per nacelle\n"
        f"hover reach pivot -> open tip {wb['arm0']:.1f} -> {wb['arm1']:.1f} mm; clearance, "
        f"3.0 in gear "
        f"{i2(wb['clear_3_F0']):+.2f} -> {i2(wb['clear_3_F1']):+.2f} in",
        transform=ax.transAxes,
        fontsize=7,
        va="bottom",
    )
    ax.set_xlabel("Z (in)")
    ax.set_ylabel("mass (g): grey = removed / moved from, red = moved to")
    ax.set_ylim(-60, 60)
    ax.set_xlim(i2(105), i2(240))
    for nm, m0, z0, m1, z1 in wb["rows"]:
        ax.text(
            i2(z0 if m0 > 0 else z1),
            (-m0 - 4) if m0 > 0 else (m1 + 2),
            SHORT.get(nm, nm.split(" (")[0]),
            fontsize=6,
            rotation=90,
            ha="center",
            va="top" if m0 > 0 else "bottom",
            color="0.3",
        )
    ax.set_title("5  Weight and balance — per nacelle", fontsize=10, loc="left")
    tb.sec_in(ax, "x")

    # (6) canonical shape: profiles at three azimuths
    ax = axs[1, 2]
    R, zs, azs = can["R"], can["zs"], can["azs"]
    for az, col in ((90, "tab:green"), (0, "tab:blue"), (270, "tab:purple")):
        j = int(np.where(azs == az)[0][0])
        ax.plot(i2(zs), i2(R[j]), color=col, lw=1.5, label=f"canonical, az {az}")
    for h, L, ph, col, nm in (
        (h0, L0, res["phi"]["F0"], "0.45", "F0"),
        (h1, L1, res["phi"]["F1"], "tab:red", "F1"),
    ):
        for k, phi in enumerate(ph):
            z, r = flap_line(h, L, phi)
            ax.plot(
                i2(z),
                i2(r),
                color=col,
                lw=2 if k == 1 else 1,
                ls="-" if k == 1 else ":",
                label=f"{nm} petal outer, {'open' if k == 1 else 'closed'}",
            )
    ax.add_patch(plt.Rectangle((i2(Z_NOZ), i2(40.6)), i2(18), i2(2.0), color="0.45", alpha=0.6))
    ax.add_patch(
        plt.Rectangle((i2(h1 - HINGE_OFF), i2(40.6)), i2(15), i2(2.0), color="tab:red", alpha=0.6)
    )
    ax.text(
        i2(Z_NOZ),
        i2(43.3),
        f"F0 housing proud {cc['F0']['housing_proud_max_mm']:.1f} mm max",
        fontsize=7,
    )
    ax.text(
        i2(h1 - 15),
        i2(44.6),
        f"F1 housing proud {cc['F1']['housing_proud_max_mm']:.1f} mm max",
        fontsize=7,
        color="tab:red",
    )
    ax.axvline(i2(can["z_root"]), color="k", lw=0.6, ls="--")
    ax.axvline(i2(can["z_tip"]), color="k", lw=0.6, ls="--")
    ax.text(i2(can["z_root"]) + 0.03, i2(30), "canonical\npetal root", fontsize=7)
    ax.text(i2(can["z_tip"]) + 0.03, i2(30), "canonical\ntail", fontsize=7)
    ax.set_xlim(i2(150), i2(258))
    ax.set_ylim(i2(28), i2(51))
    ax.set_xlabel("Z (in)")
    ax.set_ylabel("r (in)")
    ax.legend(fontsize=6.5, loc="upper right", ncol=2)
    ax.set_title(
        f"6  Canonical shape — F0 petals run {cc['F0']['flaps_beyond_canonical_tail_mm']:.0f} mm "
        f"past the tail; F1 {cc['F1']['flaps_beyond_canonical_tail_mm']:+.1f} mm",
        fontsize=10,
        loc="left",
    )
    tb.sec_in(ax, "x")

    fig.suptitle(
        "Brief F — Nozzle hinge at the canonical petal root, petals to the canonical tip "
        "(starboard 64 mm nacelle; analytical, unreviewed)",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = FIG / "odb_theme_n_f.png"
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path)
    ap.add_argument(
        "--pod-local",
        type=Path,
        help="rendered starboard pod, nacelle-local (default: the published pod, un-baked)",
    )
    ap.add_argument("--no-figure", action="store_true", help="do not rewrite the brief F figure")
    a = ap.parse_args(argv)
    if a.pod_local:
        tb._LOCAL["stbd"] = trimesh.load_mesh(a.pod_local, force="mesh")
    res = compute()
    out = figure(res) if not a.no_figure else None
    pub = {k: v for k, v in res.items() if k != "_plot"}
    txt = json.dumps(pub, indent=1, default=float)
    if a.json:
        a.json.write_text(txt)
    c = res["canonical"]
    print(
        f"canonical petal root Z {c['z_root']:.2f} mm "
        f"({c['z_root_range'][0]:.1f}..{c['z_root_range'][1]:.1f}), "
        f"tail Z {c['z_tip']:.2f}, dorsal cowl to Z {c['z_dorsal_end']:.1f}"
    )
    print(
        f"F1 hinge Z {res['hinge_z']['F1']:.2f} (F0 {res['hinge_z']['F0']:.2f}); flap "
        f"{res['L']['F1']:.1f} mm; "
        f"phi {res['phi']['F1'][0]:.2f}/{res['phi']['F1'][1]:.2f} deg; open tip Z "
        f"{res['tip_z_open']['F1']:.1f} "
        f"(F0 {res['tip_z_open']['F0']:.1f})"
    )
    for k in ("F0", "F1"):
        s = res["statics"][k]
        print(
            f"{k}: M {s['M_Nm']:.3f} N.m  ear {s['F_ear_N']:.2f} N  hold x1.5 "
            f"{s['hold_x15_N']:.1f} N  "
            f"MA needed {s['MA_needed_cont']:.0f}  pin {s['pin_N']:.1f} N  root "
            f"{s['sigma_root_MPa']:.2f} MPa"
        )
    for k, v in res["interactions"].items():
        print(f"  {k:30s} {v}")
    print("canonical check", res["canonical_check"])
    w = res["weight"]
    print(
        f"mass {w['M0_g']:.1f} -> {w['M1_g']:.1f} g, CG {w['cg0']:.2f} -> {w['cg1']:.2f}, "
        f"AUW {w['auw_delta_g']:+.0f} g,"
        f" arm {w['arm0']:.1f} -> {w['arm1']:.1f}, clear 3.0 in gear {w['clear_3_F0']:.1f} -> "
        f"{w['clear_3_F1']:.1f} mm,"
        f" ballast {w['ballast_to_hold_pivot_g_at_z200']:.0f} g"
    )
    for r in w["rows"]:
        print("   %-48s %6.1f g @ %6.1f -> %6.1f g @ %6.1f" % r)
    if out:
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
