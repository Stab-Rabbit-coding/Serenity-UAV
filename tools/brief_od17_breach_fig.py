#!/usr/bin/env python3
"""brief_od17_breach_fig.py -- figures for the Owner Decision Brief on NAC-64-OD17-BREACH.

WHY THIS EXISTS
---------------
The four OD-17 10 AWG wire channels (`od17_wire_channels()`, paths from
tools/nacelle64_optD_concept.pod_side_path) run just under the 64 mm pod's inboard skin from the
bend chamber to the disconnect bay.  This tool measures, along every wire, the skin left between the
channel (dia 6.5 mm) and the pod's outer surface, on no-cavity / no-channel renders at two pivots
(today's 118.2 mm and the decided H1 109.27 mm), sizes a local pad that restores a 2.0 mm skin, and
draws the brief's figures.

METHOD
  Per wire: densify the path; drop samples inside the bend chamber (dia 42.6 about the spar axis,
  X > 36.8) and inside the disconnect bay (Z < 64.6); drop samples where the pod's own outer surface
  is below r 40 mm (the bay's designed open mouth).  Skin over channel = outermost pod hit along the
  radial ray at the sample - (sample radius + 3.25 mm).  Pad thickening = max(0, 2.0 - skin); pad
  volume = thickening x (channel 6.5 + 2 x 2.0 mm) x path length (ESTIMATE, a strip model).

Usage:  /usr/bin/python3 tools/brief_od17_breach_fig.py --pod118 NOCH_118.stl --pod109 NOCH_109.stl
            [--json OUT] [--outdir docs/figures]
        NOCH_*.stl: the pod rendered with hollow_cavity() and od17_wire_channels() commented out,
        default frame (left shell, inboard +X), at PIVOT_Z_64 118.2 / 109.27.
Requires: numpy, trimesh, matplotlib; the decision-brief skill's scripts/brief_fig.py (SecureControllers).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding) -- owner direction.
AI note: Tool by Claude (Claude Opus 5.5, Anthropic), 2026-11-23, per AGENTS.md sec. 3.
         Analytical; ENGINEERING REVIEW REQUIRED before any result is applied.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh

import nacelle64_hollow_skin_check as hs
import nacelle64_optD_concept as d
import sls_min_wall as smw

REPO = Path(__file__).resolve().parents[1]
CH_R = 3.25  # channel radius (OD17_CH_D 6.5 / 2)
TARGET = 2.0  # pad target skin, mm
STUDY_FLOOR = smw.T_PROC  # 1.5 mm, docs/SLS_MIN_WALL_THICKNESS.md
MOUTH_R = 40.0  # pod surface below this radius = the bay's designed open mouth
PAD_W = 2 * CH_R + 2 * TARGET
sys.path.insert(0, str(REPO.parent / "SecureControllers/.claude/skills/decision-brief/scripts"))


def skin_along(pod: trimesh.Trimesh, pz: float) -> dict:
    d.PZ = pz
    out = {}
    for off in d.OFFS:
        pts, _, _ = d.pod_side_path(off, 0.0)
        p = np.vstack(
            [np.linspace(pts[i], pts[i + 1], 8, endpoint=False) for i in range(len(pts) - 1)]
            + [pts[-1:]]
        )
        r = np.hypot(p[:, 0], p[:, 1])
        az = np.arctan2(p[:, 1], p[:, 0])
        sel = ~((np.hypot(p[:, 1], p[:, 2] - pz) < 21.3) & (p[:, 0] > 36.8)) & (p[:, 2] >= 64.6)
        hits = hs.radial_hits_many(pod, [(float(q[2]), float(a)) for q, a in zip(p, az)])
        sk = np.array([h[-1] if len(h) else np.nan for h in hits])
        live = sel & (sk >= MOUTH_R)
        m = np.where(live, sk - (r + CH_R), np.nan)
        ds = np.r_[0.0, np.linalg.norm(np.diff(p, axis=0), axis=1)]
        add = np.nan_to_num(np.clip(TARGET - m, 0, None))
        k = int(np.nanargmin(m))
        out[d.NAMES[off]] = {
            "z": p[:, 2].tolist(),
            "skin_mm": m.tolist(),
            "min_mm": float(m[k]),
            "z_at_min": float(p[k, 2]),
            "pad_max_mm": float(add.max()),
            "pad_mm3": float((add * ds * PAD_W).sum()),
        }
    return out


def figures(res: dict, study: dict, outdir: Path) -> list:
    import brief_fig as bf
    import matplotlib.pyplot as plt

    files = []
    # 1 skin over channel vs Z, both pivots
    fig, ax = plt.subplots(1, 2, figsize=(15, 5.6), sharey=True)
    col = {"ESC A +": "#c0392b", "ESC A -": "#2a6fdb", "ESC B +": "#e08a00", "ESC B -": "#8e44ad"}
    for a, (pz, rows) in zip(ax, res.items()):
        for n, v in rows.items():
            a.plot(v["z"], v["skin_mm"], ".-", ms=3, color=col[n], label=f"{n} (min {v['min_mm']:.2f})")
        a.axhline(0, color="k")
        a.axhline(STUDY_FLOOR, color="g", ls="--")
        a.axhline(TARGET, color="k", ls=":")
        a.text(92, STUDY_FLOOR + 0.05, "SLS study floor 0.059 in (1.5 mm)", color="g", fontsize=8)
        a.text(92, TARGET + 0.05, "pad target 0.079 in (2.0 mm)", fontsize=8)
        a.axvspan(64.6, 77.0, color="0.85", zorder=0)
        a.text(65, -1.3, "bay mouth\n(designed open)", fontsize=8)
        a.set_xlim(62, 112)
        a.set_ylim(-1.5, 6)
        a.set_xlabel("Z from intake face, mm (0.0394 in/mm)")
        a.set_title(f"pivot Z {float(pz):.2f} mm" + (" (decided, H1)" if float(pz) < 115 else
                                                       " (today's render)"), loc="left")
        a.legend(fontsize=8, loc="upper right")
    ax[0].set_ylabel("skin left over the wire channel, mm (< 0 = channel open to air)")
    fig.suptitle("NAC-64-OD17-BREACH: skin over each OD-17 channel along its run.  "
                 "Analytical - ENGINEERING REVIEW REQUIRED", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    f = outdir / "brief_od17_breach_skin.png"
    fig.savefig(f, dpi=90)
    plt.close(fig)
    files.append(f)

    # 2 six-check sheet
    h1 = res["109.27"]
    fig, ax = bf.sheet("Brief OD17-B - close the OD-17 skin breach (X0 accept at H1 / X1 pad / "
                       "X2 service cover)")
    a = ax[0, 0]  # statics: skin strip over the channel under the study's handling load
    a.plot([0, 6.5], [0, 0], "k-", lw=6, alpha=0.35)
    a.plot([-2, 0], [0, 0], "k-", lw=10, alpha=0.6)
    a.plot([6.5, 8.5], [0, 0], "k-", lw=10, alpha=0.6)
    bf.force(a, (3.25, 3.0), (0, -2.6), 44.5, "handling (study)")
    bf.force(a, (0.0, -2.6), (0, 2.2), 22.2, "R")
    bf.force(a, (6.5, -2.6), (0, 2.2), 22.2, "R")
    a.text(-1.8, -3.9, f"span 6.5 mm: study needs {study['nlb_any']['rupture']:.2f} mm (rupture) / "
           f"{study['nlb_any']['defl']:.2f} mm (deflection) -> 1.5 mm floor governs", fontsize=8)
    a.set_xlim(-2.5, 9.5)
    a.set_ylim(-4.5, 4.5)
    a.set_yticks([])
    a.set_xlabel("across the channel, mm")
    a = ax[0, 1]  # function: wire runs, plan of the inboard face
    for n, v in h1.items():
        a.plot(np.array(v["z"]), np.array(v["skin_mm"]) * 0 + list(col).index(n), "-", color=col[n],
               lw=5, alpha=0.5)
    a.set_yticks(range(4), list(col))
    a.axvspan(64.6, 77.0, color="0.85", zorder=0)
    a.set_xlabel("Z, mm (channels run forward to the disconnect bay at Z 61)")
    a.set_xlim(60, 112)
    a.text(78, 3.4, "all options keep the drawn route, bend R >= 3 x OD,\nand the stud landing",
           fontsize=8)
    names = list(col)
    x0 = [round(h1[n]["min_mm"], 2) for n in names]
    bf.margins(ax[0, 2], [f"{n} X0" for n in names] + ["all X1 (pad)", "X2 (cover)"],
               x0 + [TARGET, 1.5], STUDY_FLOOR, limit_label="SLS study floor")
    a = ax[1, 0]  # mechanism: nearest wing-fixed part
    a.barh([0, 1], [81.31 - 48.1, 81.31 - 46.6], color="#3a9a5a")
    a.set_yticks([0, 1], ["X1 pad outer X 48.1 to wing tip face X 81.3",
                          "X0 / X2 skin X 46.6 to wing tip face"], fontsize=8)
    a.set_xlabel("gap to the wing-fixed fairing face, mm (pod rotates; gap constant)")
    a = ax[1, 1]  # weight
    pad_g = sum(v["pad_mm3"] for v in h1.values()) / 1000 * 1.11
    a.bar(["X0", "X1 pad", "X2 cover + 2 screws"], [0, pad_g, 1.2 + 0.6], color=["0.6", "#2a6fdb",
                                                                               "#c05a00"])
    a.set_ylabel("added mass per nacelle, g (ESTIMATE)")
    for i, v in enumerate([0, pad_g, 1.8]):
        a.text(i, v + 0.03, f"{v / 453.6:.4f} lbm\n({v:.2f} g)", ha="center", fontsize=8)
    a = ax[1, 2]  # canonical shape: pad proud height along Z
    for n, v in h1.items():
        z = np.array(v["z"])
        add = np.nan_to_num(np.clip(TARGET - np.array(v["skin_mm"], float), 0, None))
        a.plot(z, add, color=col[n], label=n)
    a.set_xlim(62, 92)
    a.set_xlabel("Z, mm")
    a.set_ylabel("X1 pad: outward departure from the pod surface, mm")
    a.legend(fontsize=8)
    f = outdir / "brief_od17_breach_six_checks.png"
    bf.save(fig, f)
    files.append(f)
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Figures for the NAC-64-OD17-BREACH brief.")
    ap.add_argument("--pod118", type=Path, required=True)
    ap.add_argument("--pod109", type=Path, required=True)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--outdir", type=Path, default=REPO / "docs/figures")
    a = ap.parse_args(argv)
    res = {
        "118.2": skin_along(trimesh.load(a.pod118), 118.2),
        "109.27": skin_along(trimesh.load(a.pod109), 109.27),
    }
    study = {}
    for key, fos in (("nlb", smw.FOS_NLB), ("lb", smw.FOS_LB)):
        e, s = smw.props("any")
        r = smw.case_free(6.5 / smw.MM_IN, e, s, fos)
        study[f"{key}_any"] = {"rupture": r["t_rupture_mm"], "defl": r["t_defl_mm"]}
    for pz, rows in res.items():
        for n, v in rows.items():
            print(f"pivot {pz} {n}: min skin {v['min_mm']:+.2f} mm at Z {v['z_at_min']:.1f}; "
                  f"pad max {v['pad_max_mm']:.2f} mm, {v['pad_mm3']:.0f} mm3")
    if a.json:
        a.json.write_text(json.dumps({"skin": res, "study": study}, indent=1))
    for f in figures(res, study, a.outdir):
        print(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
