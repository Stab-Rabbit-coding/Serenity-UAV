#!/usr/bin/env python3
"""plot_battery_bay.py -- side and top views of the twin flat battery tray in
the one-piece head+cargo hull, with the optional 6S 1600 third pack, the CG
and thrust line, both Observer boards and their lines of sight, and every
cargo-bay item that could conflict (payload, hoist lines, winch, tilt
motors/worms, chin nodes, aft nodes, door gateway).

Geometry is read from the fit tools (no retyped positions):
tools/twin_head_pack_fit.py, tools/cargo_layout_fit.py, tools/head_layout_fit.py,
and the merged hull airframe/stls/fuselage/head_cargo_shell24_2mm_merged.stl.
Boxes are each item's axis-aligned bounds (a drawing aid; the fit itself is
proven on the real solids by twin_head_pack_fit.py).

Output: docs/figures/battery_bay_twin_tray.png

Run:
    /usr/bin/python3 tools/plot_battery_bay.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-31, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hull_datums as hd  # noqa: E402
import twin_head_pack_fit as t  # noqa: E402

c, h, clf = t.c, t.h, t.clf
OUT = os.path.join(c.REPO, "docs", "figures", "battery_bay_twin_tray.png")

# CG offsets from twin_head_pack_fit (after the 0.5 in pivot shift)
CG_F, CG_A = 2.4, 1.5
THIRD = dict(y0=302.0, y1=372.0, zc=190.0, w=42.0, h=41.0)  # bare-pack fit band

STYLE = {  # category: (face colour, edge colour, label)
    "pack": ("#2e7d32", "#1b5e20", "flight packs (2 x Tattu 6S 2200, flat)"),
    "third": ("#a5d6a7", "#2e7d32", "optional 6S 1600 (bare-pack fit, 1 mm)"),
    "tray": ("none", "#1565c0", "twin tray / stop / gate (PA CF)"),
    "corr": ("none", "#64b5f6", "loading corridor (pack slides fwd)"),
    "payload": ("#ffcc80", "#e65100", "payload envelope (3 x 4 x 3 in)"),
    "hoist": ("#d84315", "#d84315", "hoist lines / winch"),
    "tilt": ("#b39ddb", "#4527a0", "wing-tilt motors, worms, wheels"),
    "node": ("#90a4ae", "#37474f", "avionics nodes / gateway"),
    "obs": ("#f48fb1", "#ad1457", "Observer boards / trays"),
    "trunk": ("none", "#6d4c41", "nose avionics trunk (port channel)"),
}


def cat(name):
    n = name.lower()
    if "payload" in n:
        return "payload"
    if "hoist" in n or "winch" in n:
        return "hoist"
    if any(k in n for k in ("motor", "worm", "wheel", "gear", "bracket", "brake", "tilt")):
        return "tilt"
    if "observer" in n:
        return "obs"
    if any(k in n for k in ("node", "gateway", "cable", "bay a")):
        return "node"
    return None


def items():
    out = []
    L = clf.layout_t5()
    for k, e in list(L.items()):
        if k in ("battery", "battery cradle") or "cradle" in k:
            continue
        cg_ = cat(k)
        if cg_ is None:
            continue
        b = e["solid"].bounds
        out.append((k, cg_, b))
        if e.get("mirror"):
            out.append((k + " (stbd)", cg_, clf.mirror_x(e["solid"]).bounds))
    HL, _ = h.layout()
    for k, e in HL.items():
        cg_ = cat(k) or ("obs" if k.startswith(("camera", "ToF", "laser")) else None)
        if cg_ is None:
            continue
        out.append((k, cg_, e["solid"].bounds))
        if e.get("mirror"):
            out.append((e["mirror"], cg_, clf.mirror_x(e["solid"]).bounds))
    return out


def rect(ax, x0, x1, y0, y1, key, alpha=0.55, lw=1.0, ls="-"):
    fc, ec, _ = STYLE[key]
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=fc, edgecolor=ec,
                           alpha=alpha if fc != "none" else 1.0, lw=lw, ls=ls))


def outline(ax, mesh, origin, normal, ix, iy):
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        return
    for ent in sec.discrete:
        ax.plot(ent[:, ix], ent[:, iy], color="0.35", lw=0.6)


def main():
    hull = trimesh.load(t.MERGED)
    its = items()
    z0, z1 = t.TRAY_ZC - t.TRAY_H / 2, t.TRAY_ZC + t.TRAY_H / 2
    hw = t.TRAY_W / 2
    tl = hd.SPAR_Y
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 13))
    # ---------------- side view (Y aft, Z up), centreline cut -----------------
    outline(ax1, hull, [0, 0, 0], [1, 0, 0], 1, 2)
    for name, k, b in its:
        if k == "node" and abs(0.5 * (b[0][0] + b[1][0])) > 60:
            continue
        rect(ax1, b[0][1], b[1][1], b[0][2], b[1][2], k, alpha=0.35)
    rect(ax1, t.TRAY_Y0, t.TRAY_Y1, z0, z1, "pack", alpha=0.7)
    rect(ax1, t.TRAY_Y0 - t.STOP_T, t.TRAY_Y1, z0 - t.RAIL_T, z1 + t.RAIL_T, "tray", lw=1.6)
    rect(ax1, t.TRAY_Y1, t.CORRIDOR_Y1, t.CORRIDOR_ZC - t.TRAY_H / 2,
         t.CORRIDOR_ZC + t.TRAY_H / 2, "corr", ls="--")
    rect(ax1, THIRD["y0"], THIRD["y1"], THIRD["zc"] - THIRD["h"] / 2,
         THIRD["zc"] + THIRD["h"] / 2, "third", alpha=0.8)
    rect(ax1, 160, 300, t.TRUNK_Z0, t.TRUNK_Z1, "trunk", ls=":")
    # cargo Observer camera LOS: tray top edge -> clamshell aperture edges
    cam = np.array([clf.OBSERVER_Y0, clf.OBSERVER_Z0 + clf.OBSERVER_W])
    ap0, ap1 = clf.APERTURE_Y0, clf.APERTURE_Y0 + 106.0
    floor_z = 82.0
    for ye in (ap0, ap1 - 2):
        ax1.plot([cam[0], ye], [cam[1], floor_z], color="#ad1457", lw=1.2, ls="--")
    ax1.annotate("cargo Observer camera LOS\n(to clamshell aperture)", cam,
                 xytext=(cam[0] + 15, cam[1] + 50), color="#ad1457", fontsize=8,
                 arrowprops=dict(arrowstyle="-", color="#ad1457"))
    ax1.plot([ap0, ap1], [floor_z - 4, floor_z - 4], color="k", lw=3)
    ax1.text(0.5 * (ap0 + ap1), floor_z - 14, "clamshell aperture", ha="center", fontsize=8)
    # nose Observer sensor LOS (camera / ToF / laser axis, forward-down)
    face = h.bay_face()
    d = h.FLAT_N
    ax1.plot([face[1], face[1] + d[1] * 120], [face[2], face[2] + d[2] * 120],
             color="#ad1457", lw=1.2, ls="--")
    ax1.text(face[1] + 4, face[2] + 14, "nose Observer\nsensor LOS", color="#ad1457",
             fontsize=8)
    # thrust line and CGs
    for ax in (ax1, ax2):
        ax.axvline(tl, color="k", lw=1.5)
        ax.axvline(tl + CG_F, color="#c62828", lw=1.2, ls="--")
        ax.axvline(tl + CG_A, color="#ef6c00", lw=1.2, ls=":")
    ax1.text(tl - 2, 262, f"thrust line\nY {tl:.1f}", ha="right", fontsize=9)
    ax1.text(tl + CG_F + 2, 262, f"CG, 2 packs\n+{CG_F} mm", color="#c62828", fontsize=8)
    ax1.text(tl + CG_F + 2, 247, f"CG, + 6S 1600\n+{CG_A} mm", color="#ef6c00", fontsize=8)
    ax1.set_title("SIDE VIEW (centreline cut of the one-piece head+cargo hull; items "
                  "as bounding boxes, projected)")
    ax1.set_xlabel("Y, aft (mm, datum R2)")
    ax1.set_ylabel("Z, up (mm)")
    ax1.set_xlim(-5, 460)
    ax1.set_ylim(70, 290)
    ax1.set_aspect("equal")
    # ---------------- top view (Y aft, X port up), cut at the tray centre Z ---
    outline(ax2, hull, [0, 0, t.TRAY_ZC], [0, 0, 1], 1, 0)
    for name, k, b in its:
        rect(ax2, b[0][1], b[1][1], b[0][0], b[1][0], k, alpha=0.35)
    for s in (-1, 1):
        rect(ax2, t.TRAY_Y0, t.TRAY_Y1, s * t.LANE_X - t.LANE_W / 2,
             s * t.LANE_X + t.LANE_W / 2, "pack", alpha=0.7)
    rect(ax2, t.TRAY_Y0 - t.STOP_T, t.TRAY_Y1, -hw - t.RAIL_T, hw + t.RAIL_T, "tray", lw=1.6)
    rect(ax2, t.TRAY_Y1, t.CORRIDOR_Y1, -t.LANE_W / 2, t.LANE_W / 2, "corr", ls="--")
    rect(ax2, THIRD["y0"], THIRD["y1"], -THIRD["w"] / 2, THIRD["w"] / 2, "third", alpha=0.8)
    rect(ax2, 160, 300, t.TRUNK_X0, t.TRUNK_X1, "trunk", ls=":")
    ax2.annotate("", xy=(t.TRAY_Y1 - 30, t.LANE_X), xytext=(t.TRAY_Y1 - 30, 0),
                 arrowprops=dict(arrowstyle="->", color="#1565c0"))
    ax2.annotate("", xy=(t.TRAY_Y1 - 30, -t.LANE_X), xytext=(t.TRAY_Y1 - 30, 0),
                 arrowprops=dict(arrowstyle="->", color="#1565c0"))
    ax2.text(t.TRAY_Y1 - 26, 2, "step into lane", color="#1565c0", fontsize=8)
    ax2.set_title(f"TOP VIEW (hull cut at Z {t.TRAY_ZC:.0f}; port up)")
    ax2.set_xlabel("Y, aft (mm, datum R2)")
    ax2.set_ylabel("X, port (mm)")
    ax2.set_xlim(-5, 460)
    ax2.set_ylim(-105, 105)
    ax2.set_aspect("equal")
    handles = [Rectangle((0, 0), 1, 1, facecolor=v[0], edgecolor=v[1],
                         alpha=0.6 if v[0] != "none" else 1) for v in STYLE.values()]
    labels = [v[2] for v in STYLE.values()]
    handles += [plt.Line2D([], [], color="k"), plt.Line2D([], [], color="#c62828", ls="--"),
                plt.Line2D([], [], color="#ef6c00", ls=":"),
                plt.Line2D([], [], color="#ad1457", ls="--")]
    labels += ["hover thrust line (pivot, after 0.5 in shift)", "CG, 2 packs",
               "CG, 2 packs + 6S 1600", "sensor lines of sight"]
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8, frameon=False)
    fig.suptitle("Serenity UAV -- twin flat battery tray, one-piece head+cargo hull "
                 "(screening drawing, 2026-10-31; AI-generated, Claude Opus 5.5)", fontsize=11)
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=140)
    print(f"wrote {os.path.relpath(OUT, c.REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
