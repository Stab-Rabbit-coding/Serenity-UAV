#!/usr/bin/env python3
"""nozzle64_f1_drive.py -- F1 nozzle drive: CM07, horn, link, bellcrank, push rod, ring ear.

WHY THIS EXISTS
---------------
Owner decision F1 (2026-11-22, `docs/THEME_N_DECISION_BRIEFS.md` brief F) moves the nozzle hinge to
the canonical petal root: the unison ring's ear moves to Z 164.25 mm and the closed gas load at the
ear rises x 1.28.  Owner direction with it: "add a bell crank or gear to the servo linkage to
provide more mechanical advantage".  A gear is a fixed ratio (at most 120 / 23.75 = 5.05:1,
~130 N per N.m at the ear) and a meshed gear holds the ring if the servo seizes (breaks KTD3
fail-open); a bellcrank phased near toggle reaches the ~400 N per N.m the CM07 needs to hold closed
on its continuous rating and keeps the push-only rod into the open cup.  This tool records and
checks the chosen bellcrank design, F1-B.

DESIGN PROVENANCE
-----------------
F1-B was found on 2026-11-22 by a two-stage search (output side: bellcrank pivot, axis, output arm
and phase, accepted when the rod follows the ear and pushes it toward closed (transmission
<= 60 deg) and stays >= 10 deg from dead centre; servo side: input arm and phase, horn length and
index, servo position) followed by a penalised hill climb requiring >= 20 deg from dead centre at
every joint and hardware-size clearance to the CM07 case.  The constants below are its result;
this tool re-solves the whole chain from them in closed form and re-checks every constraint.
Mesh-level verification
against the F1 assembly (pod, nozzle, ESC, leads, screws, A1 bays) is recorded in brief F's F1-B
section.

METHOD
  * Nacelle-local frame, starboard (duct axis +Z from the intake, az 270 = top).  Ring ear ball r 39
    at Z 164.25 (F1 pocket face 160.25 + 4.0), psi 292.5 (closed) -> 268.75 (open).
  * Each loop solved in closed form: |C + L (cos t u + sin t v) - P| = l is A cos t + B sin t = K.
  * Mechanical advantage by virtual work, F_ear / T_servo = |d theta / d psi| / r_ear.
  * Load: F1 design gas load at the ear (nozzle64_hinge_root_brief.loads(), calibrated 1-D model)
    + 2.0 N fail-open spring, x 1.5.  CM07: continuous 0.45 kgf.cm (7.4 V chart), stall 1.80 kgf.cm
    at 6.0 V, travel +/-60 deg (KST technical specification 2026-05, open-servo-core-secure
    hardware/CM07_Technical_Specifcation.pdf; not yet in REFERENCES.md, plan 2026-11-16-001 U2).
  * Envelope: every part inside the outer mould line (canonical shell + resized dorsal shroud, made
    from nacelle_nozzle_servo_64mm.scad nsv_outer()) less the 1.6 mm cover and 1.0 mm, outside the
    36.4 mm pocket floor, forward of the nozzle housing face (only the rod enters the ear window).

Usage:  /usr/bin/python3 tools/nozzle64_f1_drive.py [--json PATH] [--fig PATH]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding) -- owner direction.
AI note: Design and tool by Claude (Claude Opus 5.5, Anthropic), 2026-11-22, per AGENTS.md sec. 3.
         ENGINEERING REVIEW REQUIRED before any result is applied to hardware.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nozzle64_hinge_root_brief as hrb  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
FIG = REPO / "docs" / "figures"
LBF = 4.448222
OZIN = 0.141612  # ozf.in per mN.m

# ── F1 geometry ────────────────────────────────────────────────────────────────────────────────
Z0N = 160.25  # F1 nozzle pocket face (hinge 175.25 - 15)
BR, BZ = 39.0, Z0N + 4.0
PSI_C, PSI_O = 292.5, 268.75
FLOOR, COVER, CLR = 36.4, 1.6, 1.0
CM07 = {
    "L": 20.5,
    "W": 7.5,
    "H": 19.0,
    "stub": 4.5,
}  # axial, radial, tangential; shaft 4.5 from aft end
T_CONT, T_STALL6 = 0.45 * 0.0980665, 1.80 * 0.0980665  # N.m
SPRING, FS = 2.0, 1.5
F1_FLAP_L = 46.6

# ── F1-B (2026-11-22) ─────────────────────────────────────────────────────────────────────────
DESIGN = {
    "pivot_az_deg": 268.20952,
    "pivot_z_mm": 146.00417,
    "pivot_r_mm": 42.493217,  # radial pivot axis
    "out_arm_mm": 9.841518,
    "out_phase_rad": 4.225571,  # output arm angle at closed
    "in_arm_mm": 10.82719,
    "in_offset_rad": -1.304943,  # input arm angle = output + offset
    "horn_mm": 7.506528,
    "horn_closed_rad": -1.132008,  # horn angle at closed, in (e_r, e_z)
    "servo_az_deg": 275.871839,
    "servo_shaft_z_mm": 137.348098,
}
N = 97


def er(az: float) -> np.ndarray:
    a = math.radians(az)
    return np.array([math.cos(a), math.sin(a), 0.0])


def et(az: float) -> np.ndarray:
    a = math.radians(az)
    return np.array([-math.sin(a), math.cos(a), 0.0])


EZ = np.array([0.0, 0.0, 1.0])


def solve_circle(C, u, v, L, P, lr, t0):
    d = C[None, :] - P
    A, B = d @ u, d @ v
    K = (lr**2 - np.sum(d * d, 1) - L**2) / (2 * L)
    R = np.hypot(A, B)
    if np.any(np.abs(K) > R):
        raise ValueError("loop does not close over the stroke")
    base, ac = np.arctan2(B, A), np.arccos(np.clip(K / R, -1, 1))
    w = lambda x: (x + math.pi) % (2 * math.pi) - math.pi  # noqa: E731
    br = base + ac if abs(w(base[0] + ac[0] - t0)) < abs(w(base[0] - ac[0] - t0)) else base - ac
    t = np.unwrap(br)
    return t - (t[0] - t0)


def gam(vel, d):
    """Angle between a joint's velocity and the link force line (90 deg = dead centre)."""
    vel = vel / np.linalg.norm(vel, axis=1)[:, None]
    d = d / np.linalg.norm(d, axis=1)[:, None]
    return np.degrees(np.arccos(np.clip(np.abs(np.sum(vel * d, 1)), 0, 1)))


def oml_grid() -> dict[str, np.ndarray]:
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "oml.scad"
        f.write_text(
            f"use <{REPO}/airframe/openscad/nacelles/nacelle_nozzle_servo_64mm.scad>\n"
            "nsv_outer();\n"
        )
        out = Path(td) / "oml.stl"
        subprocess.run(
            ["openscad", "--backend=manifold", "-o", str(out), str(f)],
            check=True,
            capture_output=True,
        )
        m = trimesh.load_mesh(out)
    azs, zs = np.arange(200, 341, 1.0), np.arange(120, 200.1, 1.0)
    R = np.full((len(azs), len(zs)), np.nan)
    for j, az in enumerate(azs):
        a = math.radians(az)
        org = np.array([[90 * math.cos(a), 90 * math.sin(a), z] for z in zs])
        loc, ri, _ = m.ray.intersects_location(
            org, np.tile([-math.cos(a), -math.sin(a), 0.0], (len(zs), 1)), multiple_hits=False
        )
        for p, i in zip(loc, ri):
            R[j, i] = math.hypot(p[0], p[1])
    return {"azs": azs, "zs": zs, "R": R}


def solve(d: dict[str, float]) -> dict[str, Any]:
    psis = np.linspace(PSI_C, PSI_O, N)
    pr = np.radians(psis)
    B = np.stack([BR * np.cos(pr), BR * np.sin(pr), np.full(N, BZ)], 1)
    TC = np.stack([-np.sin(pr), np.cos(pr), np.zeros(N)], 1)
    C = d["pivot_r_mm"] * er(d["pivot_az_deg"]) + d["pivot_z_mm"] * EZ
    ax = er(d["pivot_az_deg"])  # radial pivot pin
    u = np.cross(ax, EZ)
    u /= np.linalg.norm(u)
    v = np.cross(ax, u)
    Lo, Li = d["out_arm_mm"], d["in_arm_mm"]
    p0 = d["out_phase_rad"]
    O0 = C + Lo * (math.cos(p0) * u + math.sin(p0) * v)
    l_rod = float(np.linalg.norm(O0 - B[0]))
    ph = solve_circle(C, u, v, Lo, B, l_rod, p0)
    Op = C + Lo * (np.cos(ph)[:, None] * u + np.sin(ph)[:, None] * v)
    off = d["in_offset_rad"]
    Ip = C + Li * (np.cos(ph + off)[:, None] * u + np.sin(ph + off)[:, None] * v)
    e_r = er(d["servo_az_deg"])
    S0 = (FLOOR + CM07["W"] / 2) * e_r + d["servo_shaft_z_mm"] * EZ
    h, t0 = d["horn_mm"], d["horn_closed_rad"]
    Hc = S0 + h * (math.cos(t0) * e_r + math.sin(t0) * EZ)
    l_link = float(np.linalg.norm(Ip[0] - Hc))
    th = solve_circle(S0, e_r, EZ, h, Ip, l_link, t0)
    H = S0 + h * (np.cos(th)[:, None] * e_r + np.sin(th)[:, None] * EZ)
    dth = np.gradient(th, pr)
    MA = np.abs(dth) / (BR / 1000)
    ur = (B - Op) / np.linalg.norm(B - Op, axis=1)[:, None]
    vO = -np.sin(ph)[:, None] * u + np.cos(ph)[:, None] * v
    vI = -np.sin(ph + off)[:, None] * u + np.cos(ph + off)[:, None] * v
    vH = -np.sin(th)[:, None] * e_r + np.cos(th)[:, None] * EZ
    return {
        "psis": psis,
        "ring": PSI_C - psis,
        "B": B,
        "TC": TC,
        "C": C,
        "ax": ax,
        "u": u,
        "v": v,
        "O": Op,
        "I": Ip,
        "H": H,
        "S0": S0,
        "th": th,
        "ph": ph,
        "MA": MA,
        "l_rod": l_rod,
        "l_link": l_link,
        "ur": ur,
        "monotonic": bool(np.all(dth > 0) or np.all(dth < 0)),
        "servo_sweep_deg": abs(math.degrees(th[-1] - th[0])),
        "bellcrank_sweep_deg": abs(math.degrees(ph[-1] - ph[0])),
        "ear_tx_deg": np.degrees(np.arccos(np.clip(np.sum(ur * TC, 1), -1, 1))),
        "dc_out": 90 - gam(vO, ur),
        "dc_in": 90 - gam(vI, H - Ip),
        "dc_horn": 90 - gam(vH, Ip - H),
    }


def loads(ring: np.ndarray) -> np.ndarray:
    ld = hrb.loads()
    f1 = ld["case"](F1_FLAP_L)
    th = np.array([s["theta"] for s in f1["stroke"]])
    fe = np.array([s["F_ear"] for s in f1["stroke"]]) * ld["cal_F"]
    return np.interp(ring, th, fe)


def in_box(p, S0, az_s, clr):
    r0 = math.hypot(S0[0], S0[1])
    x, y, z = p @ er(az_s), p @ et(az_s), p[..., 2]
    zs = S0[2]
    return (
        (x > r0 - CM07["W"] / 2 - clr)
        & (x < r0 + CM07["W"] / 2 + clr)
        & (y > -(1.5 + CM07["H"]) - clr)
        & (y < -1.5 + clr)
        & (z > zs - (CM07["L"] - CM07["stub"]) - clr)
        & (z < zs + CM07["stub"] + clr)
    )


def seg(a, b, n=8):
    t = np.linspace(0, 1, n)[:, None, None]
    return (a[None] + t * (b - a)[None]).reshape(-1, 3)


def checks(k: dict[str, Any], grid: dict[str, np.ndarray], d: dict[str, float]) -> dict[str, Any]:
    def oml(p):
        az = np.degrees(np.arctan2(p[:, 1], p[:, 0])) % 360
        i = np.clip(np.round(az - grid["azs"][0]).astype(int), 0, len(grid["azs"]) - 1)
        j = np.clip(np.round(p[:, 2] - grid["zs"][0]).astype(int), 0, len(grid["zs"]) - 1)
        return grid["R"][i, j]

    C = np.repeat(k["C"][None], N, 0)
    body = np.concatenate([seg(C, k["O"]), seg(C, k["I"]), seg(k["H"], k["I"])])
    rod = seg(k["O"], k["B"] - 1.8 * k["ur"], 10)
    r_b, r_r = np.hypot(body[:, 0], body[:, 1]), np.hypot(rod[:, 0], rod[:, 1])
    in_win = rod[:, 2] > Z0N - 0.5
    raz = np.degrees(np.arctan2(rod[:, 1], rod[:, 0])) % 360
    off_t = et(d["servo_az_deg"])
    tt = np.linspace(0.15, 0.85, 6)[:, None, None]
    link = ((k["H"] + 1.2 * off_t)[None] * (1 - tt) + k["I"][None] * tt).reshape(-1, 3)
    groups = {
        "link rod (r 0.8 + 0.6)": (link, 1.4),
        "input ball link (2.3 + 0.6)": (k["I"], 2.9),
        "output ball link (2.3 + 0.6)": (k["O"], 2.9),
        "push rod (1.0 + 0.6)": (rod, 1.6),
        "bellcrank arms (2.1 + 0.6)": (np.concatenate([seg(C, k["O"]), seg(C, k["I"])]), 2.7),
        "pivot boss (2.5 + 0.6)": (k["C"][None], 3.1),
    }
    case = {
        g: int(np.sum(in_box(p, k["S0"], d["servo_az_deg"], c))) for g, (p, c) in groups.items()
    }
    return {
        "inside_skin_and_cover": bool(
            np.all(r_b <= oml(body) - COVER - CLR) and np.all(r_r <= oml(rod) - COVER - CLR)
        ),
        "outside_pocket_floor": bool(np.all(r_b >= FLOOR + 0.2) and np.all(r_r >= FLOOR + 0.2)),
        "forward_of_housing": bool(np.all(body[:, 2] <= Z0N - 1.75)),
        "rod_only_in_ear_window": bool(
            not np.any(in_win & ((raz < PSI_O - 8) | (raz > PSI_C + 8) | (r_r > 42.0)))
        ),
        "servo_aft_face_to_housing_mm": float(Z0N - (k["S0"][2] + CM07["stub"])),
        "case_clearance_violations": case,
        "push_only": bool(np.all(np.sum(k["ur"] * k["TC"], 1) > 0)),
        "min_skin_margin_mm": float(
            min(np.min(oml(body) - COVER - r_b), np.min(oml(rod) - COVER - r_r))
        ),
    }


def forces(k: dict[str, Any], gas: np.ndarray) -> dict[str, np.ndarray]:
    """Design-load forces through the chain (no 1.5 factor), statics by moment arms."""
    F_ear = SPRING + gas
    cos_ear = np.sum(k["ur"] * k["TC"], 1)
    F_rod = F_ear / cos_ear
    arm = lambda P, d_, C, a: np.abs(np.sum(np.cross(P - C, d_) * a, 1))  # noqa: E731
    M_bc = F_rod * arm(k["O"], k["ur"], k["C"], k["ax"])
    ul = (k["I"] - k["H"]) / np.linalg.norm(k["I"] - k["H"], axis=1)[:, None]
    F_link = M_bc / arm(k["I"], ul, k["C"], k["ax"])
    T = F_ear / k["MA"]
    return {"F_ear": F_ear, "F_rod": F_rod, "F_link": F_link, "M_bc_Nmm": M_bc, "T_Nm": T}


def figure(k, f, gas, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(1, 3, figsize=(19, 5.8))
    a = axs[0]
    for i, (ls, lab) in ((0, ("-", "closed")), (N - 1, ("--", "open"))):
        pts = [
            ("servo shaft", k["S0"]),
            ("horn", k["H"][i]),
            ("link", k["I"][i]),
            ("pivot", k["C"]),
            ("arm", k["O"][i]),
            ("ear ball", k["B"][i]),
        ]
        zz = [p[1][2] for p in pts]
        ss = [
            math.radians(math.degrees(math.atan2(p[1][1], p[1][0])) % 360) * 40.0 for p in pts
        ]  # arc at r 40
        a.plot(zz, ss, ls, color="k", lw=2, marker="o", label=f"chain, {lab}")
    a.plot(
        k["B"][:, 2],
        np.radians(k["psis"]) * 40.0,
        color="tab:blue",
        lw=3,
        alpha=0.5,
        label="ear path",
    )
    i = 0
    for P, Q, nm, col, F in (
        (k["O"][i], k["B"][i], "rod", "tab:blue", f["F_rod"][i]),
        (k["H"][i], k["I"][i], "link", "tab:green", f["F_link"][i]),
    ):
        d_ = (Q - P) / np.linalg.norm(Q - P)
        s0 = math.radians(math.degrees(math.atan2(Q[1], Q[0])) % 360) * 40.0
        s1 = math.radians(math.degrees(math.atan2(Q[1] + d_[1], Q[0] + d_[0])) % 360) * 40.0
        sc = 0.15 * F
        a.annotate(
            "",
            xy=(Q[2] + sc * d_[2], s0 + sc * (s1 - s0)),
            xytext=(Q[2], s0),
            arrowprops=dict(arrowstyle="-|>", color=col, lw=2),
        )
        a.text(
            Q[2] + sc * d_[2],
            s0 + sc * (s1 - s0),
            f" {nm} {F / LBF:.2f} lbf ({F:.1f} N)",
            color=col,
            fontsize=8,
        )
    a.axvline(Z0N, color="0.5", ls=":")
    a.text(Z0N + 0.3, 182, "nozzle housing face", fontsize=7, rotation=90)
    a.set_xlabel("Z (mm) from the intake face")
    a.set_ylabel("circumferential position at r 40 mm (mm of arc from az 0)")
    a.set_title(
        "Chain, top view unrolled: closed (solid), open (dashed);\nforces at closed, design load",
        fontsize=10,
        loc="left",
    )
    a.legend(fontsize=8)
    a.grid(alpha=0.3)
    b = axs[1]
    sv = np.degrees(np.abs(k["th"] - k["th"][0]))
    need_c = FS * (SPRING + gas) / T_CONT
    need_s = FS * (SPRING + gas) / T_STALL6
    b.semilogy(sv, k["MA"], color="tab:red", lw=2, label="F1-B advantage (virtual work)")
    b.semilogy(sv, need_c, "k--", label="needed, CM07 continuous (x1.5)")
    b.semilogy(sv, need_s, color="0.5", ls="-.", label="needed, CM07 stall 6 V (x1.5)")
    b.set_xlabel("servo rotation from the closed command (deg)")
    b.set_ylabel("ear force per servo torque (N per N.m)")
    b.set_title("Mechanical advantage along the stroke", fontsize=10, loc="left")
    b.grid(alpha=0.3, which="both")
    b.legend(fontsize=8)
    c = axs[2]
    c.plot(
        sv, f["T_Nm"] * 1000 * OZIN * FS, color="tab:red", lw=2, label="servo torque needed x1.5"
    )
    c.axhline(T_CONT * 1000 * OZIN, color="k", ls="--", label="CM07 continuous 0.45 kgf.cm")
    c.axhline(T_STALL6 * 1000 * OZIN, color="0.5", ls="-.", label="CM07 stall 1.80 kgf.cm, 6.0 V")
    c2 = c.twinx()
    for key, col, lab in (
        ("F_link", "tab:green", "link"),
        ("F_rod", "tab:blue", "rod"),
        ("F_ear", "k", "ear push"),
    ):
        c2.plot(sv, f[key] / LBF, color=col, lw=1, alpha=0.7, label=f"{lab} force (lbf)")
    c.set_xlabel("servo rotation from the closed command (deg)")
    c.set_ylabel("torque (ozf.in)")
    c2.set_ylabel("force (lbf)")
    c.set_title(
        "Servo torque and chain forces (design load, full throttle, V_NE)", fontsize=10, loc="left"
    )
    c.legend(fontsize=8, loc="upper left")
    c2.legend(fontsize=8, loc="upper right")
    c.grid(alpha=0.3)
    fig.suptitle(
        "F1-B nozzle drive: KST CM07 + radial-pin bellcrank + push rod into the open cup "
        "(starboard; analytical, unreviewed)",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path, dpi=105)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path)
    ap.add_argument("--fig", type=Path, default=FIG / "nozzle64_f1_drive.png")
    a = ap.parse_args(argv)
    k = solve(DESIGN)
    gas = loads(k["ring"])
    req = FS * (SPRING + gas)
    cont, stall = k["MA"] * T_CONT / req, k["MA"] * T_STALL6 / req
    f = forces(k, gas)
    ck = checks(k, oml_grid(), DESIGN)
    j = int(np.argmax(cont < 1.0)) if np.any(cont < 1.0) else N - 1
    res = {
        "design": DESIGN,
        "rod_mm": k["l_rod"],
        "link_mm": k["l_link"],
        "servo_sweep_deg": k["servo_sweep_deg"],
        "bellcrank_sweep_deg": k["bellcrank_sweep_deg"],
        "monotonic": k["monotonic"],
        "MA_closed": float(k["MA"][0]),
        "MA_min": float(k["MA"].min()),
        "MA_open": float(k["MA"][-1]),
        "cont_margin_closed": float(cont[0]),
        "cont_margin_open": float(cont[-1]),
        "cont_margin_min": float(cont.min()),
        "stall6_margin_min": float(stall.min()),
        "continuous_hold_to_ring_deg": float(k["ring"][j]),
        "continuous_window_servo_deg": float(abs(math.degrees(k["th"][j] - k["th"][0]))),
        "dead_centre_margin_deg": {
            "output arm": float(k["dc_out"].min()),
            "input arm": float(k["dc_in"].min()),
            "horn": float(k["dc_horn"].min()),
        },
        "ear_transmission_max_deg": float(k["ear_tx_deg"].max()),
        "forces_closed": {kk: float(v[0]) for kk, v in f.items()},
        "forces_peak": {kk: float(np.max(v)) for kk, v in f.items()},
        "checks": ck,
    }
    figure(k, f, gas, a.fig)
    if a.json:
        a.json.write_text(json.dumps(res, indent=1))
    print(
        f"F1-B: rod {k['l_rod']:.2f} mm, link {k['l_link']:.2f} mm, "
        f"servo sweep {k['servo_sweep_deg']:.1f} deg "
        f"(bellcrank {k['bellcrank_sweep_deg']:.1f}), monotonic {k['monotonic']}"
    )
    print(
        f"MA closed {res['MA_closed']:.0f} / min {res['MA_min']:.0f} / "
        f"open {res['MA_open']:.0f} N per N.m"
    )
    print(
        f"continuous margin over x1.5: closed {cont[0]:.2f}, open {cont[-1]:.2f}, "
        f"worst {cont.min():.2f} "
        f"(holds to ring {res['continuous_hold_to_ring_deg']:.1f} deg = servo "
        f"{res['continuous_window_servo_deg']:.0f} deg); 6 V stall worst {stall.min():.2f}"
    )
    print(
        "dead-centre margins (deg):",
        {kk: round(v, 1) for kk, v in res["dead_centre_margin_deg"].items()},
        f"ear transmission max {res['ear_transmission_max_deg']:.1f} deg",
    )
    print("forces closed:", {kk: round(v, 3) for kk, v in res["forces_closed"].items()})
    print("forces peak:", {kk: round(v, 3) for kk, v in res["forces_peak"].items()})
    print("checks:", ck)
    ok = (
        k["monotonic"]
        and k["servo_sweep_deg"] <= 115.0
        and cont[0] >= 1
        and cont[-1] >= 1
        and stall.min() >= 1
        and min(res["dead_centre_margin_deg"].values()) >= 20.0
        and res["ear_transmission_max_deg"] <= 60.0
        and ck["inside_skin_and_cover"]
        and ck["outside_pocket_floor"]
        and ck["forward_of_housing"]
        and ck["rod_only_in_ear_window"]
        and ck["push_only"]
        and not any(ck["case_clearance_violations"].values())
        and ck["servo_aft_face_to_housing_mm"] >= 2.0
    )
    print(f"wrote {a.fig} -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
