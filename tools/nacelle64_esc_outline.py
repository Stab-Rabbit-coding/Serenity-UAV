#!/usr/bin/env python3
"""nacelle64_esc_outline.py -- the ESC board outline each G1 bay can actually hold, measured
against the real covers.

WHY THIS EXISTS
---------------
2026-11-23 (S4.4, WBS NAC-64-ESC-OUTLINE): the bay optimiser (tools/esc80_cooptimize.py
ring_width_fit) narrows a panel ring by ring and, for each ring, RE-TILTS the panel so it stays
tangent to the mount radius at its new centre.  A rigid PCB panel cannot change tilt along its
length: the real board keeps its nominal tilt and has its FAR edge cut back.  The re-tilted model
reads optimistic (ESC A logic bay 1,223 vs 1,034 mm2 per face) and dips the narrowed rings up to
1.3 mm into the seat near the hinge.  This tool measures the rigid-panel outline directly against
the printed covers (flat covers for ESC A, H1 housing-covers for ESC B), so the outline posted to
Open-Secure-ESC issue #23 is the one the parts allow.

METHOD
  For each bay and each panel (nominal tilt: inner face tangent to the mount radius at the panel's
  nominal centre), sample rays along the panel normal from the inner face, at 1 mm Z stations and
  across the panel from the hinge edge to the far edge.  Allowed stack = distance to the cover's
  inner surface - running clearance.  The usable width at a station is the contiguous run from the
  hinge edge whose allowed stack >= the bay envelope (PCB + parts both faces + mount + cooling
  lane).  Zero at the hinge means that station cannot hold the board.

Usage:  /usr/bin/python3 tools/nacelle64_esc_outline.py --cover BAY_INDEX=COVER.stl [...]
            [--json OUT] [--fig OUT.png]
        BAY_INDEX is the pod SCAD ESC_BAYS row (0 A power, 1 A logic, 2 B power, 3 B logic);
        covers are the renders of nacelle_esc_cover_64mm.scad -D RENDER_BAY=i, in the pod's
        render frame.
Requires: numpy, trimesh, matplotlib.

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

import nacelle64_esc_housing as hg

REPO = Path(__file__).resolve().parents[1]
DZ = 1.0  # [mm] Z station pitch
N_Y = 41  # samples across a panel, hinge to far edge
TOL = 0.01  # [mm] covers built to exactly envelope + clearance (H1) must read as fitting
# ESC_BAYS rows of nacelle_pod_64mm_tandem.scad, as (esc, role) into hg.G1_BAYS
BAY_ROWS = [("A", "power"), ("A", "logic"), ("B", "power"), ("B", "logic")]


def bay_of(index: int) -> tuple:
    esc, role = BAY_ROWS[index]
    return hg.G1_BAYS[esc][0 if role == "power" else 1], role, f"{esc} {role}"


def panel_outline(cover: trimesh.Trimesh, b: dict, env: float, clr: float = hg.COVER_CLR):
    """Usable width (mm) per Z station for the power and signal panels of bay `b`."""
    zs = np.arange(b["z"][0], b["z"][1] - DZ + 1e-6, DZ)
    out: dict = {"z": [float(z) for z in zs]}
    for w, a in hg.panel_angles(b):
        name = "power" if w == hg.W_POWER else "signal"
        n = np.array([math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0])
        t = np.array([-n[1], n[0], 0.0])
        hinge = -w / 2 if name == "power" else w / 2  # power panel sits on the +az side
        ys = np.linspace(hinge, -hinge, N_Y)
        o = np.array([n * (hg.MOUNT_R + 0.05) + t * y + [0, 0, z + DZ / 2] for z in zs for y in ys])
        d = np.tile(n, (len(o), 1))
        loc, idx, _ = cover.ray.intersects_location(o, d, multiple_hits=True)
        first = np.full(len(o), np.inf)
        np.fmin.at(first, idx, ((loc - o[idx]) * d[idx]).sum(1))
        allow = (first + 0.05 - clr).reshape(len(zs), len(ys))
        widths = []
        for k in range(len(zs)):
            ok = allow[k] >= env - TOL
            j = len(ys) if ok.all() else int(np.argmin(ok))
            widths.append(0.0 if j == 0 else float(abs(ys[j - 1] - hinge)))
        out[name] = widths
    out["area_per_face_mm2"] = float(DZ * (sum(out["power"]) + sum(out["signal"])))
    out["full_area_per_face_mm2"] = float(DZ * len(zs) * (hg.W_POWER + hg.W_SIGNAL))
    return out


def figure(path: Path, res: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, len(res), figsize=(4.2 * len(res), 7), sharey=False)
    ax = np.atleast_1d(ax)
    for a, (name, r) in zip(ax, res.items()):
        z = np.array(r["z"])
        a.fill_betweenx(z, 0, r["power"], color="#c05a00", alpha=0.6, step="post", label="power")
        a.fill_betweenx(
            z, 0, [-w for w in r["signal"]], color="#2a6fdb", alpha=0.6, step="post", label="signal"
        )
        a.plot([hg.W_POWER] * 2, [z[0], z[-1]], "k--", lw=0.8)
        a.plot([-hg.W_SIGNAL] * 2, [z[0], z[-1]], "k--", lw=0.8)
        a.axvline(0, color="k", lw=1.5)
        a.set_title(
            f"ESC {name}\n{r['area_per_face_mm2']:.0f} of {r['full_area_per_face_mm2']:.0f}"
            " mm2 per face",
            fontsize=10,
        )
        a.set_xlabel("distance from the hinge, mm (signal panel left)")
        a.invert_yaxis()
    ax[0].set_ylabel("Z from intake face, mm")
    ax[0].legend(loc="lower left", fontsize=8)
    fig.suptitle(
        "Usable ESC board outline per G1 bay (rigid panels, nominal tilt, 0.4 mm to the "
        "cover).  Analytical - ENGINEERING REVIEW REQUIRED",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=90)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="example: tools/nacelle64_esc_outline.py --cover 0=a_power.stl --cover "
        "1=a_logic.stl --json outline.json",
    )
    ap.add_argument("--cover", action="append", required=True, help="BAY_INDEX=COVER.stl")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--fig", type=Path)
    a = ap.parse_args(argv)
    res = {}
    for spec in a.cover:
        i, path = spec.split("=", 1)
        b, role, name = bay_of(int(i))
        r = panel_outline(trimesh.load_mesh(path, force="mesh"), b, hg.ENV[role])
        res[name] = r
        print(
            f"ESC {name} (az {b['az']}, Z {b['z'][0]}-{b['z'][1]}): "
            f"{r['area_per_face_mm2']:.0f} of {r['full_area_per_face_mm2']:.0f} mm2 per face "
            f"({100 * r['area_per_face_mm2'] / r['full_area_per_face_mm2']:.0f} %)"
        )
    if a.json:
        a.json.write_text(json.dumps(res, indent=1))
    if a.fig:
        figure(a.fig, res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
