#!/usr/bin/env python3
"""nozzle64_linkage_ma.py -- 64 mm nozzle servo linkage mechanical advantage, by virtual work.

WHY THIS EXISTS
---------------
The nozzle load study (docs/NOZZLE_64MM_LOAD_STUDY.md) found that the KST CM07 cannot hold the
cruise-closed nozzle on its continuous rating.  The owner directed (2026-11-21) "explore applying a
mechanical linkage to give the servo an advantage" with the flap hinges kept at the root of the
canonical petals.  This tool measures the drive's real mechanical advantage along the stroke and
searches the servo-side phasing for a progressive (near-toggle at closed) linkage.

METHOD
  * Ring side as adopted: ring ear ball, bellcrank pivot, output arm and rod are read from the
    generated airframe/openscad/nacelles/nozzle_servo_linkage_64_params.scad and re-solved along the
    ring stroke with tools/nozzle_servo_linkage_64.py's geometry (branch-tracked).
  * Servo side free: horn length, horn angle at closed, bellcrank input-arm length and its phase
    relative to the output arm.  The link length is fixed at the closed pose; the horn angle along
    the stroke is solved in closed form (horn tip circle against the link sphere).
  * Mechanical advantage by virtual work, rigid and frictionless:
        F_ear / T_servo = |d theta_servo / d psi_ring| / r_ear          [N per N.m]
    This is exact for the chain; the generator's force chain multiplies the worst cosine of each
    joint taken at DIFFERENT stroke points (50.4 N/N.m) and understates the drive 1.7-2.5 x.
  * Requirement along the stroke: spring 2.0 N + design gas load (nozzle64_flap_loads.py, constant
    thrust at V_NE), x 1.5; CM07 (KST technical specification 2026-05, open-servo-core-secure
    hardware/CM07_Technical_Specifcation.pdf; not yet in REFERENCES.md, plan 2026-11-16-001 U2)
    continuous 0.45 kgf.cm (chart, 7.4 V),
    stall 1.80 kgf.cm at 6.0 V, travel +/-60 deg.
  * Fail-open is NOT a constraint on the toggle: KTD3's ring cup is open (push-only rod), so a dead
    or seized servo releases the ball wherever the linkage sits (plan 2026-09-28-001 KTD3).
  * Envelope screen (not a fit check): horn tip r 38.0-44.0 mm (bore-wall floor / today's maximum),
    input-arm tip r <= 43.1 mm and z 184-196.5 mm, link 15-45 mm, servo sweep <= 115 deg, and at
    least 10 deg from dead centre at every joint pair checked (link-to-horn).  The adopted drive's
    shroud crest shall be re-run (dorsal_shroud_resize_64.py --eval-only) before any change.

Usage:  /usr/bin/python3 tools/nozzle64_linkage_ma.py [--loads JSON] [--fig PNG] [--json PATH]

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
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nozzle_servo_linkage_64 as nsl  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PARAMS = REPO / "airframe/openscad/nacelles/nozzle_servo_linkage_64_params.scad"
LOADS = REPO / "docs/figures/nozzle64_flap_loads.json"
KGFCM = 0.0980665  # N.m per kgf.cm
T_CONT, T_STALL6 = 0.45 * KGFCM, 1.80 * KGFCM
SPRING_N, FS = 2.0, 1.5
TRAVEL = 120.0
# Adopted-envelope screen (see docstring)
HORN_R = (38.0, 44.0)
IN_R_MAX, IN_Z = 43.1, (184.0, 196.5)


def _params() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in PARAMS.read_text().splitlines():
        for part in line.split(";"):
            part = part.strip()
            if part.startswith("NSL_") and "=" in part:
                k, v = part.split("=", 1)
                out[k.strip()] = v.strip()
    return out


def _vec(s: str) -> np.ndarray:
    return np.array([float(x) for x in s.strip("[] ").split(",")])


class Drive:
    """Ring side as adopted; servo side parameterised."""

    def __init__(self, n: int = 97) -> None:
        p = _params()
        self.p = p
        self.l_rod = float(p["NSL_L_ROD"])
        self.off0 = math.radians(float(p["NSL_ARM_OFFSET"]))
        self.l_in0 = float(p["NSL_L_IN"])
        self.horn0 = float(p["NSL_HORN"])
        self.thc0 = float(p["NSL_TH_CLOSED"])
        self.shaft = _vec(p["NSL_SHAFT"])
        self.er = nsl.er(float(p["NSL_SHAFT_AZ"]))
        self.ez = np.array([0.0, 0.0, 1.0])
        self.psis = np.linspace(nsl.PSI_CLOSED, nsl.PSI_OPEN, n)
        self.ring = nsl.PSI_CLOSED - self.psis  # ring rotation from closed, deg
        phis, g = [], math.radians(float(p["NSL_PHI_CLOSED"]))
        ds = np.radians(np.arange(-5, 5.0001, 0.005))
        for psi in self.psis:  # branch-tracked bellcrank solve
            b = nsl.ball(psi)
            e = [abs(np.linalg.norm(nsl.arm(g + d, nsl.L_OUT) - b) - self.l_rod) for d in ds]
            g = g + ds[int(np.argmin(e))]
            phis.append(g)
        self.phis = np.array(phis)

    def tips(self, l_in: float, off: float) -> np.ndarray:
        a = self.phis + off
        return nsl.C[None, :] + l_in * (np.cos(a)[:, None] * nsl.U + np.sin(a)[:, None] * nsl.V)

    def solve(self, horn: float, l_in: float, off: float, thc: float) -> dict[str, Any] | None:
        tips = self.tips(l_in, off)
        d = tips - self.shaft
        a, b = d @ self.er, d @ self.ez
        h0 = horn * (math.cos(thc) * self.er + math.sin(thc) * self.ez)
        link = float(np.linalg.norm(d[0] - h0))
        c = (np.sum(d * d, 1) + horn**2 - link**2) / (2 * horn)
        rad = np.hypot(a, b)
        if np.any(np.abs(c) > rad):
            return None
        base, ac = np.arctan2(b, a), np.arccos(c / rad)
        sgn = 1 if abs(((base[0] + ac[0]) - thc + math.pi) % (2 * math.pi) - math.pi) < 1e-6 else -1
        ths = np.unwrap(base + sgn * ac)
        ths = ths - (ths[0] - thc)
        dth = np.gradient(ths, np.radians(self.psis))
        if not (np.all(dth > 0) or np.all(dth < 0)):
            return None
        ma = np.abs(dth) / (nsl.B_R / 1000.0)
        hv = -np.sin(ths)[:, None] * self.er + np.cos(ths)[:, None] * self.ez
        hp = self.shaft + horn * (np.cos(ths)[:, None] * self.er + np.sin(ths)[:, None] * self.ez)
        lk = tips - hp
        lk /= np.linalg.norm(lk, axis=1)[:, None]
        tr = np.degrees(np.arccos(np.clip(np.abs(np.sum(lk * hv, 1)), 0, 1)))
        return {
            "horn": horn, "l_in": l_in, "off_deg": math.degrees(off), "thc_deg": math.degrees(thc),
            "link": link, "sweep": abs(math.degrees(ths[-1] - ths[0])), "ths": ths, "ma": ma,
            "tr": tr, "horn_tip": hp, "in_tip": tips,
        }


def margins(r: dict[str, Any], req: np.ndarray) -> dict[str, np.ndarray]:
    return {"cont": r["ma"] * T_CONT / (FS * req), "stall": r["ma"] * T_STALL6 / (FS * req)}


def search(dr: Drive, req: np.ndarray) -> list[tuple[float, dict[str, Any]]]:
    rr = lambda p: np.hypot(p[:, 0], p[:, 1])  # noqa: E731
    out = []
    for horn in (3.0, 3.5, 4.0, 4.5, 5.0):
        for l_in in (4.485, 5.0, 5.5, 6.0, 7.0):
            for doff in range(-90, 91, 5):
                off = dr.off0 + math.radians(doff)
                tp = dr.tips(l_in, off)
                z0, z1 = tp[:, 2].min(), tp[:, 2].max()
                if rr(tp).max() > IN_R_MAX or not IN_Z[0] <= z0 <= z1 <= IN_Z[1]:
                    continue
                for thc_d in range(-180, 180, 2):
                    r = dr.solve(horn, l_in, off, math.radians(thc_d))
                    if r is None or not 20 <= r["sweep"] <= 115 or r["tr"].max() > 80:
                        continue
                    if not 15 <= r["link"] <= 45:
                        continue
                    hr = rr(r["horn_tip"])
                    if hr.min() < HORN_R[0] or hr.max() > HORN_R[1]:
                        continue
                    m = margins(r, req)
                    score = min(m["cont"][0], m["cont"][-1], 2 * m["stall"].min())
                    out.append((score, r))
    out.sort(key=lambda x: -x[0])
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--loads", type=Path, default=LOADS, help="nozzle64_flap_loads.py --json")
    ap.add_argument("--fig", type=Path, default=REPO / "docs/figures/nozzle64_linkage_ma.png")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args(argv)
    rows = [x for x in json.loads(a.loads.read_text())["rows"]
            if x["model"] == "const_thrust" and x["flight"] == "V_NE"]
    rows.sort(key=lambda x: x["theta_ring"])
    dr = Drive()
    gas = np.interp(dr.ring, [x["theta_ring"] for x in rows], [x["F_ear_N"] for x in rows])
    req = SPRING_N + gas

    base = dr.solve(dr.horn0, dr.l_in0, dr.off0, math.radians(dr.thc0))
    assert base is not None
    found = search(dr, req)
    print(f"{len(found)} servo-side geometries pass the envelope screen")
    # L1: best that keeps today's 4.0 mm horn
    l1 = next(r for s, r in found if r["horn"] == dr.horn0)
    best = found[0][1]
    report: dict[str, Any] = {}
    for name, r in (("baseline", base), ("L1", l1), ("best", best)):
        m = margins(r, req)
        k = int(np.argmax(m["cont"] < 1.0)) if np.any(m["cont"] < 1.0) else len(dr.ring) - 1
        rr = np.hypot(r["horn_tip"][:, 0], r["horn_tip"][:, 1])
        t_closed = req[0] / r["ma"][0]
        link_f = t_closed / (r["horn"] / 1000 * math.cos(math.radians(r["tr"][0])))
        rec = {
            "horn_mm": r["horn"], "l_in_mm": r["l_in"],
            "input_phase_change_deg": r["off_deg"] - math.degrees(dr.off0),
            "horn_closed_deg": r["thc_deg"], "link_mm": r["link"], "servo_sweep_deg": r["sweep"],
            "ma_closed": float(r["ma"][0]),
            "ma_min": float(r["ma"].min()),
            "ma_open": float(r["ma"][-1]),
            "cont_closed": float(m["cont"][0]), "cont_open": float(m["cont"][-1]),
            "cont_min": float(m["cont"].min()), "stall6_min": float(m["stall"].min()),
            "cont_holds_to_ring_deg": float(dr.ring[k]),
            "cont_window_servo_deg": float(abs(math.degrees(r["ths"][k] - r["ths"][0]))),
            "dead_centre_margin_deg": float(90 - r["tr"].max()),
            "horn_tip_r_mm": [float(rr.min()), float(rr.max())],
            "servo_torque_closed_mNm": 1000 * t_closed, "link_force_closed_N": link_f,
        }
        report[name] = rec
        print(f"{name:8s} horn {r['horn']:.1f} L_in {r['l_in']:.2f} input phase "
              f"{rec['input_phase_change_deg']:+.0f} deg horn@closed {r['thc_deg']:+.0f} link "
              f"{r['link']:.1f} | sweep {r['sweep']:.0f} deg | MA closed {r['ma'][0]:.0f} min "
              f"{r['ma'].min():.0f} open {r['ma'][-1]:.0f} N/N.m | continuous "
              f"x{m['cont'][0]:.2f} closed,"
              f" x{m['cont'][-1]:.2f} open, holds to ring {dr.ring[k]:.2f} deg | stall6 min "
              f"x{m['stall'].min():.2f} | dead-centre margin {90 - r['tr'].max():.0f} deg")
    if a.json:
        a.json.write_text(json.dumps(report, indent=1))
    _figure(a.fig, dr, req, base, l1)
    print(f"wrote {a.fig}")
    return 0


def _figure(
    path: Path, dr: Drive, req: np.ndarray, base: dict[str, Any], l1: dict[str, Any]
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    need_c, need_s = FS * req / T_CONT, FS * req / T_STALL6
    a = ax[0]
    a.plot(dr.ring, base["ma"], color="#4a6fa5", lw=2, label="adopted drive (virtual work)")
    a.plot(dr.ring, l1["ma"], color="#c0504d", lw=2, label="L1 near-toggle phasing")
    a.axhline(50.4, color="#4a6fa5", ls=":", lw=1, label="generator's worst-cosine figure 50.4")
    a.plot(dr.ring, need_c, color="k", lw=1.2, ls="--", label="needed, CM07 continuous (x1.5)")
    a.plot(dr.ring, need_s, color="0.5", lw=1.2, ls="-.", label="needed, CM07 stall 6 V (x1.5)")
    a.set_yscale("log")
    a.set_xlabel("ring rotation from CLOSED (deg)  ->  open")
    a.set_ylabel("ear force per servo torque (N per N.m)")
    a.set_title("Mechanical advantage along the stroke")
    a.grid(alpha=0.3, which="both")
    a.legend(fontsize=7.5)
    b = ax[1]
    for r, col, lab in ((base, "#4a6fa5", "adopted"), (l1, "#c0504d", "L1")):
        th = np.degrees(r["ths"] - r["ths"][0]) * np.sign(r["ths"][-1] - r["ths"][0])
        b.plot(th, dr.ring, color=col, lw=2, label=f"{lab}: sweep {r['sweep']:.0f} deg")
    b.axvline(TRAVEL, color="k", lw=1, ls=":", label="CM07 travel 120 deg")
    b.set_xlabel("servo rotation from the closed command (deg)")
    b.set_ylabel("ring rotation from CLOSED (deg)")
    b.set_title("Servo-to-ring schedule (flat start = toggle hold)")
    b.grid(alpha=0.3)
    b.legend(fontsize=8)
    fig.suptitle("64 mm nozzle drive, KST CM07, hinge fixed at the canonical petal root "
                 "(ANALYTICAL, UNREVIEWED)", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    sys.exit(main())
