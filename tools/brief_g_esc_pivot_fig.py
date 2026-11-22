#!/usr/bin/env python3
"""brief_g_esc_pivot_fig.py -- six-check figure for Owner Decision Brief G (ESC fit, pivot, F1).

WHY THIS EXISTS
---------------
docs/DOC_TEMPLATES.md "Owner Decision Briefs" requires each option to be shown against six checks,
each with a picture and vectors.  This tool draws that sheet for brief G from the numbers from
tools/esc_f1_pivot_iter.py (G1 z_min 49.41, G2 z_min 75.85), esc_f1_pivot_iter.run() at a held pivot
of 118.86 (G3), tools/nozzle64_hinge_root_brief.py --json (weight block, off-axis basis) and
tools/nozzle64_f1_drive.py (chain loads).  The numbers are copied into DATA below with their source,
so the figure is reproducible without re-running the mesh tools; re-run those tools and update DATA
if any input changes.

Usage:  /usr/bin/python3 tools/brief_g_esc_pivot_fig.py [--out PATH]
Requires: matplotlib, numpy.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding) -- owner direction.
AI note: Figure tool by Claude (Claude Opus 5.5, Anthropic), 2026-11-22, per AGENTS.md sec. 3.
         Analytical; ENGINEERING REVIEW REQUIRED before any result is applied.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import argparse
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
IN = 25.4
G_PER_LBM = 453.59237

# Source of every number: see the module docstring.  Margins are mm of logic-section length
# (negative = short); the pivot is the off-axis CG (mm from the intake face, nacelle-local Z).
DATA: dict[str, Any] = {
    "today_pivot": 118.86,
    "f1_pivot_no_move": 111.68,  # F1 with today's ESC bays (hinge_root_brief weight.cg1)
    "opts": {
        "G1": dict(
            label="G1  forward to the Z 47.9 web",
            z_min=49.41,
            pivot=109.73,
            a=-0.94,
            b=-15.74,
            ballast=0.0,
        ),
        "G2": dict(
            label="G2  today's forward limit (Z 74.3 web)",
            z_min=75.85,
            pivot=110.19,
            a=-14.31,
            b=-15.74,
            ballast=0.0,
        ),
        "G3": dict(
            label="G3  hold the pivot at 118.86 with ballast",
            z_min=49.41,
            pivot=118.86,
            a=-4.73,
            b=-25.74,
            ballast=86.1,
        ),
    },
    "tip_open_f1": 221.82,  # open-nozzle tip station, F1 (arm1 + cg1)
    "clr_ref": dict(pivot=111.68, c15=-5.19, c30=36.71),
    "walls": [
        ("F1 flaps", 2.5),
        ("bellcrank bosses (as drawn)", 1.1),
        ("CM07 pocket to liner", 1.33),
        ("bellcrank bosses, dia 6 mm (proposed)", 2.0),
    ],
    "clash": [
        ("A1 bay B80 x F1 housing", 2938),
        ("lead slot x F1 housing", 411),
        ("F1 flaps x unison ring", 115),
        ("flaps x throat (TABBOSS, existing)", 1875),
    ],
    "chain": dict(gas_N=10.3, rod_N=14.6, pin_N=19.3, servo_mNm=16.1),
}


def clearance(pivot):
    """Hover tip clearance (mm) for both gear heights; the arm grows 1:1 as the pivot moves fwd."""
    d = DATA["clr_ref"]["pivot"] - pivot
    return DATA["clr_ref"]["c15"] - d, DATA["clr_ref"]["c30"] - d


def figure(out: Path) -> None:
    o = DATA["opts"]
    names = list(o)
    col = {"G1": "#2a6fdb", "G2": "#8a8a8a", "G3": "#c05a00"}
    fig, ax = plt.subplots(2, 3, figsize=(19, 11.5))

    # 1 Statics and dynamics: nacelle FBD on the tilt pivot, hover, nozzle open
    a = ax[0, 0]
    a.plot([0, 240], [0, 0], "k-", lw=6, alpha=0.25)
    for n in names:
        p = o[n]["pivot"]
        a.annotate("", (p, -40), (p, 0), arrowprops=dict(arrowstyle="-|>", color=col[n], lw=2))
        a.annotate(
            "", (p, 45), (p, 5), arrowprops=dict(arrowstyle="-|>", color=col[n], lw=1.2, ls="--")
        )
        a.text(
            p + 1.5,
            -46 - 7 * names.index(n),
            f"{n}: W at CG = pivot {p / IN:.2f} in ({p:.1f})",
            color=col[n],
            fontsize=8.5,
        )
    a.plot(DATA["today_pivot"], 0, "kx", ms=10)
    a.text(DATA["today_pivot"] + 2, 6, "today 4.68 in (118.9)", fontsize=8)
    c = DATA["chain"]
    a.annotate("", (214, 0), (214, 28), arrowprops=dict(arrowstyle="-|>", color="r", lw=2))
    a.text(
        128,
        50,
        f"gas load at ear {c['gas_N'] / 4.448:.2f} lbf ({c['gas_N']} N)\n"
        f"rod {c['rod_N'] / 4.448:.2f} lbf ({c['rod_N']} N) C, pin {c['pin_N'] / 4.448:.2f} lbf"
        f" ({c['pin_N']} N)",
        fontsize=8,
        color="r",
    )
    a.set_xlim(0, 240)
    a.set_ylim(-75, 66)
    a.set_title(
        "1  Statics and dynamics - weight at the off-axis CG, pivot reaction (dashed)\n"
        "zero tilt moment by construction; nozzle chain loads unchanged by G",
        loc="left",
        fontsize=10,
    )
    a.set_xlabel("nacelle Z, mm (intake face = 0)")
    a.set_yticks([])

    # 2 Function: ESC logic-section length margin per option
    a = ax[0, 1]
    w = 0.35
    for i, n in enumerate(names):
        a.bar(i - w / 2, o[n]["a"], w, color=col[n], alpha=0.55)
        a.bar(i + w / 2, o[n]["b"], w, color=col[n])
        a.text(i - w / 2, o[n]["a"] - 1.6, f"A {o[n]['a']:.1f}", ha="center", fontsize=8)
        a.text(i + w / 2, o[n]["b"] - 1.6, f"B {o[n]['b']:.1f}", ha="center", fontsize=8)
    a.axhline(0, color="k")
    a.set_xticks(range(3), names)
    a.set_ylim(-30, 4)
    a.set_ylabel("logic-section length margin, mm (0.039 in/mm)")
    a.set_title(
        "2  Function - does the 70 A ESC fit? (light = ESC A, dark = ESC B)\n"
        "no option fits today's board; G1 needs the least shrink",
        loc="left",
        fontsize=10,
    )

    # 3 Structural integrity: walls vs the 2.0 mm SLS PA CF rule
    a = ax[0, 2]
    lab = [w_[0] for w_ in DATA["walls"]]
    val = [w_[1] for w_ in DATA["walls"]]
    a.barh(range(len(val)), val, color=["#3a9a5a" if v >= 2.0 else "#d03030" for v in val])
    a.axvline(2.0, color="k", ls="--")
    a.text(2.03, len(val) - 0.6, "AGENTS.md s7 min 0.079 in (2.0)", fontsize=8)
    a.set_yticks(range(len(val)), lab, fontsize=8.5)
    a.set_xlabel("wall, mm")
    a.set_title(
        "3  Structural integrity - F1 / F1-B walls (same for all G options)",
        loc="left",
        fontsize=10,
    )

    # 4 Mechanism and component interactions: interference volumes
    a = ax[1, 0]
    lab = [c_[0] for c_ in DATA["clash"]]
    val = [c_[1] for c_ in DATA["clash"]]
    a.barh(range(len(val)), val, color="#c0007a")
    for i, v in enumerate(val):
        a.text(v + 30, i, f"{v / 16387:.3f} in3 ({v:,} mm3)", va="center", fontsize=8)
    a.set_yticks(range(len(val)), lab, fontsize=8.5)
    a.set_xlim(0, 3000 * 1.45)
    a.set_title(
        "4  Mechanism - open clashes to close (G moves the bays forward,\n"
        "clearing B80 and the lead slot once the shorter board exists)",
        loc="left",
        fontsize=10,
    )

    # 5 Weight and balance: pivot, ballast, hover clearance
    a = ax[1, 1]
    for i, n in enumerate(names):
        c15, c30 = clearance(o[n]["pivot"])
        a.bar(i - w / 2, c15, w, color=col[n], alpha=0.55)
        a.bar(i + w / 2, c30, w, color=col[n])
        a.text(
            i - w / 2,
            c15 - 3,
            f"{c15 / IN:+.2f} in\n({c15:+.1f})",
            ha="center",
            fontsize=8,
            va="top",
        )
        a.text(i + w / 2, c30 + 1, f"{c30 / IN:+.2f} in\n({c30:+.1f})", ha="center", fontsize=8)
        if o[n]["ballast"]:
            a.text(
                i - 0.55,
                55,
                f"+{2 * o[n]['ballast'] / G_PER_LBM:.2f} lbm\n({2 * o[n]['ballast']:.0f} g) AUW",
                ha="center",
                fontsize=8.5,
                color=col[n],
            )
    a.axhline(0, color="k")
    a.set_xticks(range(3), names)
    a.set_ylim(-22, 66)
    a.set_ylabel("hover nozzle-tip ground clearance, mm")
    a.set_title(
        "5  Weight and balance - hover clearance (light = 1.5 in gear, dark = 3.0 in gear)",
        loc="left",
        fontsize=10,
    )

    # 6 Canonical shape
    a = ax[1, 2]
    a.axis("off")
    a.text(0, 0.95, "6  Canonical shape", fontsize=10, va="top", fontweight="bold")
    a.text(
        0,
        0.82,
        "The nacelle OML is the F1 shell already decided\n(brief F); the bays move inside it.\n\n"
        "The pivot is fixed on the wing spar, so moving it\n"
        "0.36 in (9.1 mm) forward in the nacelle (G1;\n"
        "0.34 in / 8.7 mm in G2) sits the whole nacelle that\n"
        "much further AFT relative to the wing.\n"
        "Check against the canonical nacelle placement:\nREQUIRES VERIFICATION.\n\n"
        "G3: pivot and nacelle placement unchanged;\ninternal ballast at Z 200; no OML change.",
        fontsize=9,
        va="top",
    )
    fig.suptitle(
        "Brief G - 70 A ESC fit and the tilt pivot under F1 "
        "(starboard 64 mm nacelle; port mirrors)."
        "  Analytical, unreviewed - ENGINEERING REVIEW REQUIRED",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out, dpi=90)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Six-check figure for Owner Decision Brief G.")
    ap.add_argument("--out", type=Path, default=REPO / "docs/figures/brief_g_esc_pivot.png")
    a = ap.parse_args(argv)
    figure(a.out)
    print(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
