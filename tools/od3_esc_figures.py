#!/usr/bin/env python3
"""od3_esc_figures.py -- figures for the OD-3 Owner Decision Brief (70 A vs 80 A Open-Secure-ESC).

Writes four PNGs to docs/figures/ for docs/ESC_RATING_OD3_BRIEF.md:

  od3_esc_current.png    current demand of the QF2822-2300KV against the two ratings, and the
                         current-time envelope the ESC limit must hold (statics and dynamics)
  od3_esc_path.png       the power path, pack to motor, with each element's limit (function)
  od3_esc_thermal.png    modelled FET channel temperature against current at three ambients
  od3_esc_fit_mass.png   bay-fit margins and ESC mass / CG shift, 70 A vs 80 A (interactions,
                         weight and balance)

Inputs (no new analysis is done here; every number is traced):
  * Motor: QX-Motor QF2822-2300KV sheet, REF-EDF-003: 57.0 A at 24 V full throttle,
    60 A / 10 s.  25.2 V peak 57 x (25.2/24)^2 = 62.8 A and the 44 A worst-loaded-fan hover
    current are ESTIMATES (reports/UAV ESC wire market survey.md; owner design current 2026-11-11).
  * Thermal: tools/esc80_cooptimize.py on tools/esc70_design.json (2026-11-12): channel 68.1 C at
    70 A and its 25 C design ambient, i.e. a 43.1 K rise; the rise scales with I^2 (conduction
    only, hot max R_DS(on)).  Switching loss is NOT included.  Limit 125 C (declared judgement).
  * Fit and mass: the same tool on esc70_design.json and on esc80_design_m2.json re-based to the
    70 A file's nacelle scale 1.06 and exclusions (as designed, and with the 70 A 14 mm signal
    width).

Usage:  python3 tools/od3_esc_figures.py [--out docs/figures]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-12.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# palette: reference categorical slots 1-3 (validated light mode), text and surface tokens
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
CRIT = "#d03b3b"

I_HOVER_MEAN = 38.0      # A, mean per fan, 21.0 V late pack (ESTIMATE)
I_HOVER_DESIGN = 44.0    # A, worst-loaded fan, owner design current 2026-11-11 (ESTIMATE)
I_FULL_24V = 57.0        # A, REF-EDF-003
I_MOTOR_10S = 60.0       # A for 10 s, REF-EDF-003
I_FULL_252V = 57.0 * (25.2 / 24.0) ** 2   # 62.8 A (ESTIMATE)
I_WIRE = 48.0            # A, 10 AWG feed continuous on paper, option A (wire report; to be tested)
RISE_70 = 68.1 - 25.0    # K at 70 A, esc80_cooptimize.py on esc70_design.json
T_LIMIT_C = 125.0

FIT = {  # bay fit margin, mm (positive = fits); A and B are the two ESCs per nacelle
    "70 A\n(esc70_design)": (3.2, 18.1),
    "80 A as designed\n(scale 1.06)": (-24.5, 19.2),
    "80 A, 14 mm\nsignal width": (-11.0, -7.6),
}
MASS = {  # ESC mass estimate g, CG shift of the rotating assembly mm
    "70 A\n(esc70_design)": (52.7, 3.7),
    "80 A as designed\n(scale 1.06)": (51.5, 4.0),
    "80 A, 14 mm\nsignal width": (55.2, 4.5),
}


def f_of_c(c: float) -> float:
    return c * 9.0 / 5.0 + 32.0


def style(ax: plt.Axes) -> None:
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)


def fig_current(out: Path) -> None:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6), dpi=150,
                                 gridspec_kw={"width_ratios": [1, 1.25]})
    fig.patch.set_facecolor(SURF)
    style(a1)
    cases = [("Hover, mean, 21.0 V", I_HOVER_MEAN), ("Hover, worst fan (design)", I_HOVER_DESIGN),
             ("Full throttle, 24 V", I_FULL_24V), ("Motor limit, 10 s", I_MOTOR_10S),
             ("Full throttle, 25.2 V", I_FULL_252V)]
    y = np.arange(len(cases))[::-1]
    a1.barh(y, [c[1] for c in cases], height=0.55, color=BLUE, zorder=3)
    for yi, (lab, v) in zip(y, cases):
        a1.text(v - 1, yi, f"{v:.0f} A", va="center", ha="right", fontsize=9, color=SURF,
                fontweight="bold")
    a1.set_yticks(y, [c[0] for c in cases], fontsize=9, color=INK)
    for x, lab, ls in ((70, "70 A board (chosen)", "-"), (80, "80 A board / maker's figure", "--")):
        a1.axvline(x, color=INK2, lw=1.4, ls=ls, zorder=4)
        a1.text(x, len(cases) - 0.35, lab, rotation=90, va="top", ha="right", fontsize=8,
                color=INK2)
    a1.set_xlim(0, 88)
    a1.set_xlabel("DC current per ESC, A", color=INK2, fontsize=9)
    a1.set_title("Demand against rating", loc="left", fontsize=11, color=INK)

    style(a2)
    a2.plot([0, 10, 10, 40], [I_MOTOR_10S, I_MOTOR_10S, I_WIRE, I_WIRE], color=ORANGE,
            lw=2.2, zorder=4)
    a2.text(19, I_WIRE + 1.2, "required I²t limit: fold back to the qualified\n"
            "wire rating (about 48 A on paper)", fontsize=8, color=INK)
    a2.text(1.6, I_MOTOR_10S + 1.2, "up to 60 A for at most 10 s (motor limit)", fontsize=8,
            color=INK)
    a2.axhline(70, color=INK2, lw=1.4, zorder=3)
    a2.text(39.5, 71, "70 A board rating", ha="right", fontsize=8, color=INK2)
    a2.axhline(I_HOVER_DESIGN, color=BLUE, lw=2, ls=(0, (4, 2)), zorder=3)
    a2.text(39.5, I_HOVER_DESIGN - 3.2, "44 A sustained design current", ha="right", fontsize=8,
            color=INK)
    a2.annotate("", xy=(1, I_FULL_252V), xytext=(1, I_HOVER_DESIGN),
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
    a2.text(1.6, 49, "demand steps\n44 → 63 A;\nlimit holds 60 A", fontsize=8,
            color=INK)
    a2.set_xlim(0, 40)
    a2.set_ylim(0, 80)
    a2.set_xlabel("time at current, s", color=INK2, fontsize=9)
    a2.set_ylabel("A", color=INK2, fontsize=9)
    a2.set_title("Current-time envelope the ESC limit must hold", loc="left", fontsize=11,
                 color=INK)
    fig.suptitle("OD-3: QF2822-2300KV current demand (REF-EDF-003; 25.2 V and 44 A are ESTIMATES)",
                 x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout()
    fig.savefig(out / "od3_esc_current.png", facecolor=SURF)
    plt.close(fig)


def fig_path(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 2.4), dpi=150)
    fig.patch.set_facecolor(SURF)
    ax.set_xlim(0, 12)
    ax.set_ylim(0.7, 3)
    ax.axis("off")
    blocks = [
        ("6S pack\n25.2-21.0 V", "upstream fuse"),
        ("Branch fuse\n(NAC-64-FUSE-COORD)", "carry 44 A cont.,\n57-63 A for 10 s"),
        ("4 x 10 AWG feed\nin the CF spar", "about 33-48 A on paper;\nthermal test decides"),
        ("Open-Secure-ESC\n70 A (OD-3)", "I²t limit: 60 A / 10 s,\nthen wire rating"),
        ("3 x 12 AWG phase\n200 C", "about 38 A RMS at 44 A;\nload-bank test"),
        ("QF2822-2300KV\nmotor", "57 A at 24 V;\n60 A / 10 s"),
    ]
    xs = np.linspace(1.0, 11.0, len(blocks))
    for i, (x, (name, lim)) in enumerate(zip(xs, blocks)):
        col = ORANGE if i == 3 else BLUE
        ax.add_patch(FancyBboxPatch((x - 0.78, 1.55), 1.56, 0.95, boxstyle="round,pad=0.02",
                                    fc=SURF, ec=col, lw=2.2 if i == 3 else 1.4))
        ax.text(x, 2.02, name, ha="center", va="center", fontsize=8.5, color=INK)
        ax.text(x, 1.05, lim, ha="center", va="center", fontsize=7.5, color=INK2)
        if i < len(blocks) - 1:
            ax.add_patch(FancyArrowPatch((x + 0.8, 2.02), (xs[i + 1] - 0.8, 2.02),
                                         arrowstyle="-|>", mutation_scale=12, color=INK, lw=1.2))
    ax.text(0.1, 2.85, "Power path, pack to motor: current flows left to right; each box gives "
            "the element's limit", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(out / "od3_esc_path.png", facecolor=SURF)
    plt.close(fig)


def fig_thermal(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    fig.patch.set_facecolor(SURF)
    style(ax)
    i = np.linspace(20, 75, 200)
    rise = RISE_70 * (i / 70.0) ** 2
    for amb, col, ls in ((25.0, BLUE, "-"), (40.0, ORANGE, "--"), (80.0, AQUA, "-.")):
        tc = amb + rise
        ax.plot(i, f_of_c(tc), color=col, lw=2, ls=ls, zorder=3)
        ax.text(75.5, f_of_c(tc[-1]), f"{f_of_c(amb):.0f} °F ({amb:.0f} °C) ambient",
                va="center", fontsize=8, color=INK)
        t44 = amb + RISE_70 * (I_HOVER_DESIGN / 70.0) ** 2
        ax.plot([I_HOVER_DESIGN], [f_of_c(t44)], "o", ms=7, color=col, mec=SURF, mew=2, zorder=4)
    ax.axhline(f_of_c(T_LIMIT_C), color=CRIT, lw=1.4, zorder=2)
    ax.text(21, f_of_c(T_LIMIT_C) + 3, "design limit 257 °F (125 °C)", fontsize=8,
            color=INK)
    ax.axvline(I_HOVER_DESIGN, color=INK2, lw=1, ls=":")
    ax.text(I_HOVER_DESIGN + 0.6, 92, "44 A sustained", fontsize=8, color=INK2)
    ax.axvline(70, color=INK2, lw=1, ls=":")
    ax.text(70.6, 92, "70 A rating", fontsize=8, color=INK2)
    ax.set_xlim(20, 90)
    ax.set_ylim(80, 280)
    ax.set_xticks(range(20, 80, 10))
    ticks = list(range(100, 281, 40))
    ax.set_yticks(ticks, [f"{t} °F ({(t - 32) * 5 / 9:.0f} °C)" for t in ticks])
    ax.set_xlabel("continuous current per ESC, A", color=INK2, fontsize=9)
    ax.set_title("70 A board: modelled FET channel temperature (conduction only; switching loss "
                 "not included)", loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(out / "od3_esc_thermal.png", facecolor=SURF)
    plt.close(fig)


def fig_fit_mass(out: Path) -> None:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4), dpi=150)
    fig.patch.set_facecolor(SURF)
    names = list(FIT)
    x = np.arange(len(names))
    w = 0.36
    style(a1)
    for k, (col, lab) in enumerate(((BLUE, "ESC A bay"), (ORANGE, "ESC B bay"))):
        vals = [FIT[n][k] for n in names]
        a1.bar(x + (k - 0.5) * (w + 0.02), vals, width=w, color=col, zorder=3, label=lab)
        for xi, v in zip(x, vals):
            a1.text(xi + (k - 0.5) * (w + 0.02), v + (1 if v >= 0 else -1), f"{v:+.1f}",
                    ha="center", va="bottom" if v >= 0 else "top", fontsize=8, color=INK)
    a1.axhline(0, color=INK, lw=1.2, zorder=4)
    a1.text(2.55, 1.0, "fits above 0", ha="right", fontsize=8, color=INK2)
    a1.set_xticks(x, names, fontsize=8.5, color=INK)
    a1.set_ylabel("bay fit margin, mm", color=INK2, fontsize=9)
    a1.set_ylim(-30, 26)
    a1.legend(frameon=False, fontsize=8, loc="lower left")
    a1.set_title("Fit in the 64 mm nacelle bays (scale 1.06)", loc="left", fontsize=11, color=INK)

    style(a2)
    m = [MASS[n][0] for n in names]
    a2.bar(x, m, width=0.5, color=BLUE, zorder=3)
    for xi, v, n in zip(x, m, names):
        a2.text(xi, v + 0.8, f"{v:.1f} g ({v / 453.592:.3f} lbm)\nCG shift {MASS[n][1]:.1f} mm",
                ha="center", va="bottom", fontsize=8, color=INK)
    a2.set_xticks(x, names, fontsize=8.5, color=INK)
    a2.set_ylabel("ESC mass estimate, g", color=INK2, fontsize=9)
    a2.set_ylim(0, 70)
    a2.set_title("Mass and rotating-assembly CG shift (ESTIMATES)", loc="left", fontsize=11,
                 color=INK)
    fig.tight_layout()
    fig.savefig(out / "od3_esc_fit_mass.png", facecolor=SURF)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "figures")
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    fig_current(args.out)
    fig_path(args.out)
    fig_thermal(args.out)
    fig_fit_mass(args.out)
    for n in ("od3_esc_current", "od3_esc_path", "od3_esc_thermal", "od3_esc_fit_mass"):
        print(f"wrote {args.out / (n + '.png')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
