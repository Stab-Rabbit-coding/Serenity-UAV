#!/usr/bin/env python3
"""Draw the wing's root and tip sections with every internal bore, to scale.

The Rev R1a section figure (docs/img/wing_rev_r1a_sections.png) was made by
hand and had no generator in the repository, so it could not be brought back
into step when Rev S1b changed the tip thickness and Rev S1c moved both
cableways.  This replaces it with a script, so the figure is a rendering of the
SCAD rather than a drawing that happens to resemble it.

Everything is PARSED FROM THE SCAD SOURCE -- airfoil tables, chords, thickness
scales, and every bore station and diameter -- so the figure cannot drift from
the wing that actually gets built.  Section scaling follows Rev S1b: thickness
only, about the camber line, which is why bore centres sit on the UNSCALED
camber midline.

Companion to tools/wing_internal_clearance.py: that one decides whether the
layout is legal, this one shows what it looks like.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-18, per AGENTS.md AI attribution.
License : CC BY-SA 4.0  <https://creativecommons.org/licenses/by/4.0/>

Run: /usr/bin/python3 tools/wing_section_figure.py [--out PATH]
"""

import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib.patches import Circle    # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, SCRIPT_DIR)

from wing_internal_clearance import (      # noqa: E402
    interp, load_wing, MIN_WALL_MM,
)

DEFAULT_OUT = os.path.join(REPO_ROOT, "docs", "img", "wing_rev_s1c_sections.png")

# One colour per subsystem, shared by both panels.
BORE_STYLE = {
    "spar":    ("#c0392b", "rotating tilt-spar"),
    "EDF fwd": ("#2980b9", "EDF harness (double-D)"),
    "EDF aft": ("#2980b9", None),
    "AK7455":  ("#27ae60", "AK7455 encoder lead"),
}


def outline(section):
    """Section outline in mm: thickness scaled about the camber line."""
    xs, upper, lower = [], [], []
    for frac, _ in section.upper:
        camber = (interp(section.upper, frac) + interp(section.lower, frac)) / 2.0
        half = (interp(section.upper, frac) - interp(section.lower, frac)) / 2.0
        xs.append(frac * section.chord)
        upper.append((camber + half * section.t_scale) * section.chord)
        lower.append((camber - half * section.t_scale) * section.chord)
    return xs, upper, lower


def draw(ax, section, bores, span_f, title, xlim, ylim):
    xs, up, lo = outline(section)
    ax.fill_between(xs, lo, up, facecolor="#ecf0f1", edgecolor="#2c3e50",
                    linewidth=1.4, zorder=1)

    camber_x = [f * section.chord for f, _ in section.upper]
    camber_y = [section.midline(f * section.chord) for f, _ in section.upper]
    ax.plot(camber_x, camber_y, "--", color="#7f8c8d", linewidth=0.9,
            zorder=2, label="camber line (unscaled)")

    # Captions sit ABOVE the section on staggered rows with leader lines.
    # Below the section they either collided with each other (the bores are
    # close together in chord) or spilled outside the axes on the tip panel,
    # where the section is shallow; above it there is clear room on both.
    # Caption rows hang off the shared frame, not this section's own top,
    # so root and tip captions line up across the two panels.
    top = ylim[1] - 13.0
    for row, bore in enumerate(sorted(bores, key=lambda b: b.station(span_f))):
        colour, label = BORE_STYLE.get(bore.name, ("#8e44ad", bore.name))
        station = bore.station(span_f)
        centre = section.midline(station)
        ax.add_patch(Circle((station, centre), bore.r,
                            facecolor="white", edgecolor=colour,
                            linewidth=1.6, zorder=3,
                            label=label if label else None))
        wall = section.depth(station) / 2.0 - bore.r
        y_text = top + 3.0 + 4.2 * (row % 2)
        ax.annotate(f"{bore.name}  Ø{bore.d:g} @ {station:.2f}\nwall {wall:.2f} mm",
                    xy=(station, centre + bore.r), xytext=(station, y_text),
                    ha="center", va="bottom", fontsize=6.4, color=colour,
                    zorder=4,
                    arrowprops=dict(arrowstyle="-", color=colour,
                                    linewidth=0.6, shrinkA=1, shrinkB=1))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)

    ax.set_title(title, fontsize=9)
    ax.set_xlabel("chordwise station, mm aft of LE", fontsize=8)
    ax.set_ylabel("mm above chord line", fontsize=8)
    ax.set_aspect("equal")
    ax.tick_params(labelsize=7)
    ax.grid(True, linewidth=0.3, alpha=0.4)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=DEFAULT_OUT, help="output PNG path")
    args = ap.parse_args()

    wing = load_wing()
    root, tip, bores = wing["root"], wing["tip"], wing["bores"]

    # Both panels share one scale and one frame, so root and tip are directly
    # comparable by eye and equal-aspect axes cannot end up different heights
    # (which is what left a band of dead space between them).
    lows, highs = [], []
    for section in (root, tip):
        _xs, up, lo = outline(section)
        lows.append(min(lo))
        highs.append(max(up))
    xlim = (-4.0, max(root.chord, tip.chord) + 4.0)
    ylim = (min(lows) - 2.0, max(highs) + 13.0)

    fig, axes = plt.subplots(2, 1, figsize=(9.5, 6.6))
    draw(axes[0], root, bores, 0.0,
         f"ROOT  chord {root.chord:g} mm   thickness scale {root.t_scale:g}",
         xlim, ylim)
    draw(axes[1], tip, bores, 1.0,
         f"TIP  chord {tip.chord:g} mm   thickness scale {tip.t_scale:g}",
         xlim, ylim)

    handles, labels = axes[0].get_legend_handles_labels()
    seen, h2, l2 = set(), [], []
    for handle, label in zip(handles, labels):
        if label not in seen:
            seen.add(label)
            h2.append(handle)
            l2.append(label)
    axes[0].legend(h2, l2, fontsize=6.8, loc="lower right", framealpha=0.9)

    fig.suptitle("Serenity wing — S1223 internal bore layout (Rev S1c)\n"
                 "constant-mm stations; bores on the camber midline; "
                 f"min skin floor {MIN_WALL_MM:.2f} mm",
                 fontsize=10, y=0.985)
    # equal aspect leaves tall empty margins, so pack the axes explicitly
    # rather than letting tight_layout reserve room for the unused height.
    fig.tight_layout(rect=(0, 0, 1, 0.92), h_pad=0.6)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fig.savefig(args.out, dpi=170)
    print(f"wrote {os.path.relpath(args.out, REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
