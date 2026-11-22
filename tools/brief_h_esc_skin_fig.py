#!/usr/bin/env python3
"""brief_h_esc_skin_fig.py -- six-check figure for Owner Decision Brief H (ESC bays, true skin).

WHY THIS EXISTS
---------------
WBS NAC-64-ESC-SKIN-RAY (2026-11-22): the ESC bay tools read the ventral skin as the dorsal one.
With the skin corrected the 70 A ESC does not fit inside the canonical 64 mm pod in any layout the
optimiser finds.  Brief H puts the ways out to the owner.  The numbers are copied into DATA with
their source so the figure is reproducible without the mesh runs:
  * optimiser variants: tools/esc80_cooptimize.py on tools/esc70_design_f1.json with the G1 pivot
    keep-outs (pivot Z 109.73) and the near-side skin, per variant;
  * blister heights: G1 bay panels (20 / 14 mm hinged, mount r 37.2 mm, stack 6.65 mm, skin wall
    1.9 mm) against the corrected skin grid;
  * as-built ESC covers: radial distance of the published cover vertices outside the scaled
    canonical OML;
  * V_NE 87 kt: current-specification/flight_limits.json (REF-FAA-002 sec. 107.51).

Usage:  /usr/bin/python3 tools/brief_h_esc_skin_fig.py [--out PATH]
Requires: matplotlib.

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
NEED = 2802.0  # mm2 per face per ESC (power 1,520 + logic 1,282)

DATA: dict[str, Any] = {
    # per-face fitted board area per ESC (A, B), mm2
    "fit": {
        "H1 G1 bays + ventral blister": (2883.0, 2773.0),
        "H2 inside the skin, best (16/12 mm panels)": (910.0, 1609.0),
        "H2 inside the skin, G1 settings": (622.0, 826.0),
    },
    "tch_c": {
        "H1 G1 bays + ventral blister": 73.8,
        "H2 inside the skin, best (16/12 mm panels)": 132.2,
    },
    # blister height needed for the G1 bays (max, mean), mm
    "blister": [
        ("ESC A power, port 336", 7.99, 0.19),
        ("ESC A logic, port 262", 2.51, 0.02),
        ("ESC B power, port 78", 5.52, 2.55),
        ("ESC B logic, port 136", 6.15, 4.06),
    ],
    "cover_proud_max": {"as-built ventral ESC cover": 11.52, "as-built dorsal ESC cover": 1.41},
    "vne_kt": 87.0,
    "bay_B_power_area_mm2": 60.3 * 34.0,
    "esc_cutback_c": 85.0,
}


def figure(out: Path) -> None:
    fig, ax = plt.subplots(2, 3, figsize=(19, 11.5))

    # 1 Statics: cover suction at V_NE
    a = ax[0, 0]
    v = DATA["vne_kt"] * 0.514444
    q = 0.5 * 1.225 * v * v  # Pa, sea level ISA
    area = DATA["bay_B_power_area_mm2"] * 1e-6
    f = q * area * 1.0 * 1.5  # Cp -1 (ASSUMED, conservative), x1.5 ultimate
    a.add_patch(plt.Rectangle((0.1, 0.35), 0.8, 0.12, color="#2a6fdb", alpha=0.5))
    for x in (0.2, 0.4, 0.6, 0.8):
        a.annotate("", (x, 0.75), (x, 0.48), arrowprops=dict(arrowstyle="-|>", color="r", lw=1.6))
    for x in (0.12, 0.88):
        a.annotate("", (x, 0.2), (x, 0.35), arrowprops=dict(arrowstyle="-|>", color="k", lw=1.6))
    a.text(
        0.1,
        0.82,
        f"suction q x Cp(-1) x 1.5 at V_NE {DATA['vne_kt']:.0f} kt:\n"
        f"q = {q / 6894.76:.3f} psi ({q:.0f} Pa) -> {f / 4.448:.2f} lbf ({f:.1f} N) on the\n"
        "ESC B power cover (2.4 x 1.3 in); reacted by the cover screws (black)",
        fontsize=9,
    )
    a.set_xlim(0, 1)
    a.set_ylim(0, 1.05)
    a.axis("off")
    a.set_title(
        "1  Statics - cover / blister air load (same for H1 and the as-built cover)",
        loc="left",
        fontsize=10,
    )

    # 2 Function: per-face area per ESC
    a = ax[0, 1]
    names = list(DATA["fit"])
    for i, n in enumerate(names):
        av, bv = DATA["fit"][n]
        a.bar(i - 0.18, av, 0.34, color="#3a7bd5")
        a.bar(i + 0.18, bv, 0.34, color="#e08a00")
        a.text(
            i,
            max(av, bv) + 60,
            f"{100 * av / NEED:.0f} / {100 * bv / NEED:.0f} %",
            ha="center",
            fontsize=8.5,
        )
    a.axhline(NEED, color="k", ls="--")
    a.text(1.55, NEED + 60, "needed per face, 2,802 mm2", fontsize=8)
    a.set_xticks(range(len(names)), [n.replace(" ", "\n", 2) for n in names], fontsize=8)
    a.set_ylabel("fitted board area per face, mm2 (blue ESC A, orange ESC B)")
    a.set_ylim(0, 3400)
    a.set_title("2  Function - does the 70 A ESC fit?", loc="left", fontsize=10)

    # 3 Structural: blister / cover proud heights
    a = ax[0, 2]
    lab = [b[0] for b in DATA["blister"]] + list(DATA["cover_proud_max"])
    mx = [b[1] for b in DATA["blister"]] + list(DATA["cover_proud_max"].values())
    mean = [b[2] for b in DATA["blister"]] + [float("nan")] * 2
    y = range(len(lab))
    a.barh(y, mx, color=["#8a8a8a"] * 4 + ["#c0007a", "#c0007a"])
    a.scatter(mean, y, color="k", zorder=3, label="mean over the board footprint")
    for i, m in enumerate(mx):
        a.text(m + 0.15, i, f"{m / IN:.2f} in ({m:.1f})", va="center", fontsize=8)
    a.set_yticks(list(y), lab, fontsize=8.5)
    a.set_xlabel("height proud of the canonical skin, mm")
    a.set_xlim(0, 14)
    a.legend(fontsize=8, loc="lower right")
    a.set_title(
        "3  Structural / shape - blister needed for the G1 bays (grey)\n"
        "vs what the as-built covers already stand proud (magenta)",
        loc="left",
        fontsize=10,
    )

    # 4 Mechanism: thermal and lead route
    a = ax[1, 0]
    t = DATA["tch_c"]
    k = list(t)
    a.bar(range(len(k)), [t[x] for x in k], color=["#3a7bd5", "#c03030"])
    a.axhline(DATA["esc_cutback_c"], color="r", ls="--")
    a.text(
        -0.4, DATA["esc_cutback_c"] + 2, "ESC thermal cut-back 185 F (85 C)", fontsize=8, color="r"
    )
    for i, x in enumerate(k):
        a.text(i, t[x] + 2, f"{t[x] * 9 / 5 + 32:.0f} F ({t[x]:.0f} C)", ha="center", fontsize=8.5)
    a.set_xticks(range(len(k)), [x.replace(" ", "\n", 2) for x in k], fontsize=8)
    a.set_ylabel("hotter ESC channel temperature, C (bay model)")
    a.set_title(
        "4  Mechanism / interactions - ESC temperature; H1 keeps the G1 lead-slot\n"
        "plan (motor-2 slot into ESC B's power bay)",
        loc="left",
        fontsize=10,
    )

    # 5 Weight and balance
    a = ax[1, 1]
    a.axis("off")
    a.text(0, 0.95, "5  Weight and balance", fontsize=10, fontweight="bold", va="top")
    a.text(
        0,
        0.84,
        "H1: blister skins add ~0.004-0.009 lbm (2-4 g) per nacelle (ESTIMATE: 2 mm SLS PA CF\n"
        "over ~4,000 mm2 of side wall); ventral, near the pivot station, so the CG and pivot move\n"
        "< 0.1 mm.  The G1 pivot (Z 109.73 mm) stands until the hollow-cavity fix\n"
        "(NAC-64-HOLLOW-SKIN) re-runs the pod mass, which moves it again.\n\n"
        "H2: no change from G1, but the boards do not fit.\n"
        "H3 (bigger nacelle, radial x1.22 on x1.06, ~x1.29): every pod station and mass grows;\n"
        "pod skin mass ~+65 % (area ~ scale^2), the pivot and hover reach re-converge.\n"
        "H4 (ESCs off the pod): -0.21 lbm (-95 g) per nacelle of ESC mass leaves the tilting\n"
        "group; the pivot moves forward; phase leads cross the tilt joint (study needed).",
        fontsize=9,
        va="top",
    )

    # 6 Canonical shape
    a = ax[1, 2]
    a.axis("off")
    a.text(0, 0.95, "6  Canonical shape", fontsize=10, fontweight="bold", va="top")
    a.text(
        0,
        0.84,
        "H1: two ventral blisters per nacelle over ESC B's bays, 0.10-0.24 in (2.6-6.2 mm)\n"
        "proud, plus trimmed panel corners on ESC A's bays.  Smaller than the bulge the\n"
        "as-built ventral ESC cover already has (up to 0.45 in / 11.5 mm), which the faulty\n"
        "skin model hid.  Departs from REF-CAD-003 on the belly; visible in profile.\n\n"
        "H2: none.  H3: silhouette kept, size grows (nacelle-to-fuselage proportion\n"
        "changes).  H4: none on the nacelle; a new bay in the wing root or fuselage.",
        fontsize=9,
        va="top",
    )
    fig.suptitle(
        "Brief H - the 70 A ESC on the corrected skin (starboard 64 mm nacelle; port "
        "mirrors).  Analytical, unreviewed - ENGINEERING REVIEW REQUIRED",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out, dpi=90)
    print(f"q at V_NE {q:.0f} Pa; cover design suction {f:.2f} N")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Six-check figure for Owner Decision Brief H.")
    ap.add_argument("--out", type=Path, default=REPO / "docs/figures/brief_h_esc_skin.png")
    a = ap.parse_args(argv)
    figure(a.out)
    print(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
