#!/usr/bin/env python3
"""cooling_g1_figures.py -- every figure of the gate G1 Owner Decision Brief for the
fuselage cooling fan and tail EDF provisions (issue #290, WBS COOL-01).

Plan: docs/plans/2026-11-15-001-feat-fuselage-cooling-plan.md, unit U3, "G1 package".
Brief: docs/FUSELAGE_COOLING_LAYOUT_BRIEF.md.

All geometry comes from tools/rear_cone_layout_fit.py and the live Rev U meshes, so a
figure cannot drift from the layout.  A missing figure fails the run (exit 1).

The thermal figures use tools/node_thermal_forced_air.py with ONE stated approximation:
where a cargo-bay section is not a closed ring, the cavity is the closed-door outline less a
2 mm skin.  Plan unit U2 replaces that with the true closed section.  Every thermal input
is ASSUMED, so the thermal figures are PROVISIONAL.

Canon references [REF-CAD-003] (QMx blueprints) and [REF-CAD-002] (Nick Henning renders)
are NOT copied into any figure: the QMx pack is copyrighted and held for internal reference
only.  The canon figures draw the project mesh and name the reference sheet to compare.

Run:
    /usr/bin/python3 tools/cooling_g1_figures.py [--out docs/figures]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-15, per
         AGENTS.md section 3 AI attribution.
License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
         Figures it writes are CC-BY-SA-4.0 (AGENTS.md section 3: all images).
"""

import argparse
import io
import math
import os
import sys
import tarfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Ellipse, FancyArrowPatch, Rectangle  # noqa: E402

import hull_datums as hd  # noqa: E402
import rear_cone_layout_fit as rc  # noqa: E402
import sls_materials as sls  # noqa: E402

FIGURES = (
    "fbd", "airpath_fan", "airpath_edf", "upgrade_sequence", "walls", "rear_cone_sections",
    "clearances", "cg", "canon_side", "canon_aft", "canon_bow", "sizing", "fan_curve",
    "fan_electrical", "harness", "thermal_baseline", "flow_guides", "rcs_options",
)
META = {"Title": "Serenity-UAV fuselage cooling, gate G1", "Author": "Steve Griffing",
        "Copyright": "CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)",
        "Software": "tools/cooling_g1_figures.py"}
C = {"hull": "#555555", "edf": "#c0392b", "fan": "#2471a3", "ring": "#8e44ad",
     "tube": "#d68910", "intake": "#1e8449", "rcs": "#b03a2e", "baffle": "#117a65",
     "air": "#2e86c1", "note": "#333333"}
HEAD_HULL = os.path.join(REPO, "airframe", "stls", "fuselage", "head_cargo_shell24_2mm_merged.stl")
IN = 25.4


def inmm(mm, nd=2):
    return f"{mm / IN:.{nd}f} in ({mm:.1f} mm)"


def load(path):
    import trimesh
    if os.path.exists(path):
        return trimesh.load(path)
    with tarfile.open(path + ".tar.gz") as tz:
        return trimesh.load(io.BytesIO(tz.extractfile(tz.getmembers()[0]).read()),
                            file_type="stl")


def cut(mesh, origin, normal, ix, iy):
    """Section line segments as a list of (N, 2) arrays in the chosen axes."""
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        return []
    return [sec.vertices[e.points][:, (ix, iy)] for e in sec.entities]


def draw(ax, segs, color=None, lw=0.7):
    for s in segs:
        ax.plot(s[:, 0], s[:, 1], "-", color=color or C["hull"], lw=lw)


def side_base(ax, G, y0=430, y1=695):
    draw(ax, G["side"])
    ax.set_xlim(y0, y1)
    ax.set_ylim(75, 255)
    ax.set_aspect("equal")
    ax.set_xlabel("station Y, mm (aft to the right)")
    ax.set_ylabel("Z, mm")
    ax.grid(alpha=0.25)


def arrow(ax, p0, p1, color, lw=2.0, style="-|>"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=14, color=color,
                                 lw=lw, zorder=5))


def envelopes(ax, L, cfg):
    """Draw the proposal on a side section.  cfg: 'fan' or 'edf'."""
    z = L["z_axis"]
    r = L["shroud_od"] / 2
    ax.add_patch(Rectangle((L["ring_y0"], z - L["ring_od"] / 2), rc.RING_L, L["ring_od"],
                           fill=False, ec=C["ring"], lw=1.8, zorder=4))
    ax.plot([L["tube_y0"], L["tube_y1"]], [z + r, z + rc.NOZZLE_B / 2], color=C["tube"], lw=2)
    ax.plot([L["tube_y0"], L["tube_y1"]], [z - r, z - rc.NOZZLE_B / 2], color=C["tube"], lw=2)
    ax.plot([L["exit_y"]] * 2, [z - rc.NOZZLE_B / 2, z + rc.NOZZLE_B / 2], ":", color=C["tube"])
    for sgn in (1, -1):
        ax.plot([L["intake_y0"], L["intake_y1"]], [z + sgn * 62] * 2, color=C["intake"],
                lw=5 if cfg == "edf" else 2.5, solid_capstyle="butt",
                ls="-" if cfg == "edf" else (0, (1, 1)))
    ax.plot([L["rcs_y"]] * 2, [z + r, z + r + 9], color=C["rcs"], lw=3)
    ax.plot([L["rcs_y"]] * 2, [z - r, z - r - 9], color=C["rcs"], lw=3)
    if cfg == "fan":
        ax.add_patch(Rectangle((L["fan_y0"], z - 12.5), rc.FAN_DEPTH, 25, fc=C["fan"],
                               ec="k", zorder=6))
        ax.plot([L["fan_y0"]] * 2, [z - r, z + r], color=C["fan"], lw=3)
    else:
        ax.add_patch(Rectangle((L["edf_y0"], z - r), rc.X5_SHROUD_L, 2 * r, fill=False,
                               ec=C["edf"], lw=2, zorder=6))
        ax.add_patch(Rectangle((L["edf_y0"] + 14, z - 14), rc.X5_UNIT_L - 14, 28,
                               fc=C["edf"], alpha=0.45, ec=C["edf"], zorder=6))
        ax.plot([L["baffle_y"]] * 2, [z - 56, z + 56], color=C["baffle"], lw=3)


def save(fig, out, name):
    path = os.path.join(out, f"cooling_g1_{name}.png")
    fig.savefig(path, dpi=110, metadata=META)
    plt.close(fig)
    return path


# ---- figures ------------------------------------------------------------------------------
def fig_fbd(G, out):
    L, sz = G["L"], G["sz"]
    z = L["z_axis"]
    fig, ax = plt.subplots(figsize=(13, 7.5))
    side_base(ax, G, 480, 690)
    envelopes(ax, L, "edf")
    yr = L["edf_y0"] + 8
    arrow(ax, (yr + 45, z), (yr, z), C["edf"], 3)
    ax.text(yr + 2, z + 4, f"EDF thrust {sz['thrust_n'] / 4.44822:.2f} lbf ({sz['thrust_n']:.1f} N)"
            "\nASSUMED scaling", color=C["edf"], fontsize=9)
    edf = [p for p in G["parts"] if p[0] in ("X5 motor + custom rotor", "EDF shroud",
                                              "spider mount (bolted)")]
    w = sum(p[1] for p in edf) * 9.80665e-3
    yw = sum(p[1] * p[2] for p in edf) / sum(p[1] for p in edf)
    arrow(ax, (yw, z - 2), (yw, z - 40), "k", 2.5)
    ax.text(yw + 2, z - 38, f"EDF unit weight {w / 4.44822:.2f} lbf ({w:.2f} N) per g", fontsize=9)
    for sgn in (1, -1):
        arrow(ax, (L["ring_y0"] + 5, z + sgn * 62), (L["ring_y0"] + 5, z + sgn * 36), C["ring"])
    ax.text(L["ring_y0"] - 62, z + 66, "ring web reactions into the hull skin", color=C["ring"],
            fontsize=9)
    arrow(ax, (L["rcs_y"], z + 42), (L["rcs_y"], z + 66), C["rcs"])
    ax.text(L["rcs_y"] + 3, z + 60, f"RCS jet {sz['f_jet_n'] / 4.44822:.2f} lbf "
            f"({sz['f_jet_n']:.2f} N) each\nreaction on the hull is opposite", color=C["rcs"],
            fontsize=9)
    kt = 60.0 / (2 * math.pi * 3200.0)
    tq = kt * 50.0
    ax.annotate("", xy=(yr + 30, z + 14), xytext=(yr + 30, z - 14),
                arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=1.0", color="purple"))
    ax.text(yr + 44, z - 20, f"motor torque {tq * 8.8507:.2f} lbf-in ({tq:.3f} N-m)\nat the 50 A "
            "ESC limit (Kt from 3200 KV)", color="purple", fontsize=9)
    tau = sz["thrust_n"] / (3 * rc.WALL_LOAD * rc.RING_L)
    web = (G["meas"]["stations"][int(5 * round(L["ring_y0"] / 5))]["dia"] - L["ring_od"]) / 2
    sig = w * web / 3 / (rc.RING_L * rc.WALL_LOAD ** 2 / 6)
    allow = sls.PA_CF["tensile_ult_mpa"] * sls.Z_STRENGTH_PA_CF
    txt = (f"Ring webs: 3 x {rc.WALL_LOAD} mm x {rc.RING_L:.0f} mm, radial length {web:.0f} mm\n"
           f"  thrust shear {tau:.2f} MPa;  web bending per g {sig:.1f} MPa (weight on 3 webs)\n"
           f"  PA CF across layers {allow:.0f} MPa (84 MPa x Z factor {sls.Z_STRENGTH_PA_CF}) "
           "[REF-MAT-015]\n"
           f"  static margin at 1 g: {allow / max(sig, tau):.0f}x.  Landing and tail-strike "
           "load factors: requires verification.")
    ax.text(484, 82, txt, fontsize=8.5, family="monospace",
            bbox=dict(fc="white", ec="0.6"))
    ax.set_title("G1 statics: loads on the mounting ring, spider and fused tube "
                 "(EDF configuration governs; fan loads are negligible)")
    return save(fig, out, "fbd")


def _airpath(G, out, cfg):
    L = G["L"]
    z = L["z_axis"]
    fig, ax = plt.subplots(figsize=(13, 7))
    side_base(ax, G, 440, 690)
    envelopes(ax, L, cfg)
    for zz in (z + 25, z, z - 25):
        arrow(ax, (455, zz), (L["baffle_y"] - 3 if cfg == "edf" else 540, zz), C["air"], 1.6)
    if cfg == "fan":
        for zz in (z + 12, z - 12):
            arrow(ax, (545, zz), (L["fan_y0"] - 2, z + (zz - z) * 0.3), C["air"], 1.6)
        arrow(ax, (L["fan_y1"] + 2, z), (L["exit_y"] + 25, z), C["air"], 2.4)
        fig.text(0.5, 0.925, "FAN CONFIGURATION: all fan air comes from inside the fuselage. "
                 "Intake covers and RCS caps are closed (dotted green; red stubs capped).",
                 ha="center", fontsize=10)
        ax.text(L["fan_y0"] - 4, z + 36, "sealed adapter\n+ Delta fan", color=C["fan"],
                ha="center", fontsize=9)
    else:
        arrow(ax, (L["baffle_y"] + 2, z), (L["edf_y0"] - 3, z), C["air"], 1.2)
        for sgn in (1, -1):
            arrow(ax, (L["intake_y0"] + 15, z + sgn * 85), (L["intake_y0"] + 22, z + sgn * 62),
                  C["intake"], 2.4)
            arrow(ax, (L["intake_y0"] + 24, z + sgn * 55), (L["edf_y0"] - 3, z + sgn * 18),
                  C["intake"], 2.0)
        arrow(ax, (L["edf_y1"] - 20, z), (L["exit_y"] + 30, z), C["edf"], 2.8)
        fig.text(0.5, 0.905, "EDF CONFIGURATION: most air enters at the opened intakes (green). "
                 "The baffled insert meters cooling air from the interior (thin blue).\n"
                 "The EDF never runs below the minimum cooling throttle (plan KD7).",
                 ha="center", fontsize=10)
        ax.text(L["baffle_y"], z - 66, "baffled insert\n+ orifice plate", color=C["baffle"],
                ha="center", fontsize=9)
    ax.text(446, z + 30, "cooling air from the bow inlets,\npast every node", color=C["air"],
            fontsize=9, bbox=dict(fc="white", ec="none", alpha=0.8))
    ax.set_title(f"G1 function: air path, {cfg.upper()} configuration (centreline section)",
                 pad=38)
    return save(fig, out, f"airpath_{cfg}")


def fig_airpath_fan(G, out):
    return _airpath(G, out, "fan")


def fig_airpath_edf(G, out):
    return _airpath(G, out, "edf")


def fig_upgrade_sequence(G, out):
    L = G["L"]
    steps = (("1. As printed and flown", "fan",
              "Fan on the adapter. 4 intake covers and 4 RCS caps intact. Valve pads empty."),
             ("2. Remove the fan", None,
              "Unbolt the adapter and fan from the spider. Unplug the fan lead at the stern stack."),
             ("3. Cut covers and caps", "cut",
              "Cut 4 intake covers and 4 RCS caps on their scored grooves. Deburr. No hull print."),
             ("4. Fit the EDF parts", "edf",
              "Baffled insert, EDF on the spider, ESC, 4 valves + servos, GW-RCS. Leak check."))
    fig, axs = plt.subplots(2, 2, figsize=(15, 9.5))
    for ax, (title, cfg, note) in zip(axs.flat, steps):
        side_base(ax, G, 495, 680)
        if cfg in ("fan", "edf"):
            envelopes(ax, L, cfg)
        elif cfg == "cut":
            envelopes(ax, L, "edf")
            for sgn in (1, -1):
                ax.plot(L["intake_y0"] + 15, L["z_axis"] + sgn * 62, "x", ms=14, mew=3, color="r")
                ax.plot(L["rcs_y"], L["z_axis"] + sgn * (L["shroud_od"] / 2), "x", ms=12, mew=3,
                        color="r")
        else:
            ax.add_patch(Rectangle((L["ring_y0"], L["z_axis"] - L["ring_od"] / 2), rc.RING_L,
                                   L["ring_od"], fill=False, ec=C["ring"], lw=1.8))
        ax.set_title(title, fontsize=11)
        ax.text(497, 79, note, fontsize=8.5, bbox=dict(fc="white", ec="0.7"))
    fig.suptitle("G1 function: the Phase 11 upgrade sequence -- no hull reprint (plan R4)")
    fig.tight_layout()
    return save(fig, out, "upgrade_sequence")


def fig_walls(G, out):
    rows = (("mounting ring", rc.WALL_LOAD, rc.WALL_LOAD, "load-bearing, free-standing"),
            ("ring webs", rc.WALL_LOAD, rc.WALL_LOAD, "load-bearing, free-standing"),
            ("thrust tube + nozzle", rc.WALL_DEFAULT, rc.WALL_DEFAULT, "category not stated"),
            ("intake throat walls", rc.WALL_DEFAULT, rc.WALL_DEFAULT, "category not stated"),
            ("RCS stubs", rc.WALL_DEFAULT, rc.WALL_DEFAULT, "category not stated"),
            ("valve + servo pads", 3.0, rc.WALL_LOAD, "load-bearing, free-standing"),
            ("intake covers (membrane)", rc.WALL_FLOOR, rc.WALL_FLOOR, "non-load, span < 1 in"),
            ("RCS caps (membrane)", rc.WALL_FLOOR, rc.WALL_FLOOR, "non-load, span < 1 in"),
            ("fan adapter plate", rc.WALL_DEFAULT, rc.WALL_DEFAULT, "category not stated"))
    fig, ax = plt.subplots(figsize=(12, 6))
    y = np.arange(len(rows))
    ax.barh(y + 0.2, [r[1] for r in rows], 0.38, color=C["ring"], label="proposed wall")
    ax.barh(y - 0.2, [r[2] for r in rows], 0.38, color="0.7", label="minimum, any orientation")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r[0]}\n({r[3]})" for r in rows], fontsize=8.5)
    for i, r in enumerate(rows):
        ax.text(r[1] + 0.05, i + 0.2, f"{r[1] / IN:.3f} in ({r[1]:.1f} mm)", va="center", fontsize=8)
    ax.set_xlabel("wall thickness, mm")
    ax.invert_yaxis()
    ax.legend(loc="lower right")
    ax.set_title("G1 structural integrity: proposed walls against docs/SLS_MIN_WALL_THICKNESS.md\n"
                 "(print orientation not stated, so the 'any orientation' column governs)")
    fig.tight_layout()
    return save(fig, out, "walls")


def _xsec(ax, G, y, title):
    draw(ax, cut(G["mesh"], [0, y, 0], [0, 1, 0], 0, 2))
    ax.set_aspect("equal")
    ax.set_xlim(95, -95)  # +X is port; seen from aft, port is on the left
    ax.set_ylim(78, 250)
    ax.grid(alpha=0.25)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("X, mm (port on the left, seen from aft)")


def fig_rear_cone_sections(G, out):
    L = G["L"]
    z = L["z_axis"]
    fig, axs = plt.subplots(2, 3, figsize=(16, 10.5))
    spec = ((L["baffle_y"], "baffle station"), (L["intake_y0"] + 15, "intake station"),
            (L["ring_y0"] + 5, "ring + fan / EDF front"), (L["shroud_y1"], "shroud aft face + spider"),
            (L["rcs_y"], "RCS station"), (L["exit_y"] - 2, "just inside the exit plane"))
    for ax, (y, name) in zip(axs.flat, spec):
        _xsec(ax, G, y, f"Y {y:.0f}: {name}")
        st = G["meas"]["stations"].get(int(5 * round(y / 5)))
        if st:
            ax.add_patch(Ellipse((0, st["zc"]), st["dia"], st["dia"], fill=False, ec="0.5",
                                 ls=":", lw=1))
        if name.startswith("baffle"):
            ax.add_patch(Ellipse((0, z), 112, 112, fill=False, ec=C["baffle"], lw=2))
        if name.startswith("intake"):
            for az in rc.INTAKE_AZ:
                a = math.radians(az)
                ax.plot([62 * math.cos(a) * 0.86, 62 * math.cos(a) * 1.08],
                        [z + 62 * math.sin(a) * 0.86, z + 62 * math.sin(a) * 1.08],
                        color=C["intake"], lw=7, solid_capstyle="butt")
        if "ring" in name or "shroud" in name:
            ax.add_patch(Ellipse((0, z), L["shroud_od"], L["shroud_od"], fill=False,
                                 ec=C["edf"], lw=2))
            ax.add_patch(Ellipse((0, z), rc.ROTOR_D, rc.ROTOR_D, fill=False, ec=C["edf"], ls="--"))
        if "ring" in name:
            ax.add_patch(Ellipse((0, z), L["ring_od"], L["ring_od"], fill=False, ec=C["ring"], lw=2))
            ax.add_patch(Rectangle((-12.5, z - 12.5), 25, 25, fill=False, ec=C["fan"], lw=2))
            for az in (90, 210, 330):
                a = math.radians(az)
                ax.plot([L["ring_od"] / 2 * math.cos(a), 58 * math.cos(a)],
                        [z + L["ring_od"] / 2 * math.sin(a), z + 58 * math.sin(a)],
                        color=C["ring"], lw=2.5)
        if name.startswith("RCS"):
            ax.add_patch(Ellipse((0, z), 58, 58, fill=False, ec=C["tube"], lw=2))
            for az in rc.RCS_PATTERNS[rc.RCS_RECOMMENDED]:
                a = math.radians(az)
                arrow(ax, (29 * math.cos(a), z + 29 * math.sin(a)),
                      (70 * math.cos(a), z + 70 * math.sin(a)), C["rcs"], 2)
        if "exit" in name:
            ax.add_patch(Ellipse((0, z), rc.NOZZLE_A, rc.NOZZLE_B, fill=False, ec=C["tube"], lw=2))
    fig.suptitle("G1 interactions: rear cone cross-sections with the proposed envelopes, port and "
                 "starboard (dotted grey: largest circle the cavity holds)")
    fig.tight_layout()
    return save(fig, out, "rear_cone_sections")


def fig_clearances(G, out):
    L, m = G["L"], G["meas"]
    d_min, y_min = G["d_min"]
    gaps = (("shroud to hull, radial (min at Y %.0f)" % y_min, (d_min - L["shroud_od"]) / 2, 2.0),
            ("baffle to the stern stack aft face", L["baffle_y"] - rc.STERN_STACK_Y1, 2.0),
            ("intakes to the baffle", L["intake_y0"] - L["baffle_y"], 2.0),
            ("intakes to the EDF front face", L["edf_y0"] - L["intake_y1"], 0.0),
            ("motor tail to the exit plane", L["exit_y"] - L["edf_y1"], 0.0),
            ("skid tips (first tail contact, Y 689.8) aft of the exit", 689.8 - L["exit_y"], 0.0))
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 6.5), gridspec_kw={"width_ratios": [1.25, 1]})
    draw(ax, G["plan"])
    z = L["z_axis"]
    ax.set_aspect("equal")
    ax.set_xlim(470, 690)
    ax.set_ylim(-95, 95)
    ax.grid(alpha=0.25)
    ax.set_xlabel("station Y, mm")
    ax.set_ylabel("X, mm (+ port)")
    r = L["shroud_od"] / 2
    ax.add_patch(Rectangle((478, -30), rc.STERN_STACK_Y1 - 478, 60, fc="0.8", ec="k"))
    ax.text(479, 34, "stern stack", fontsize=8)
    ax.plot([L["baffle_y"]] * 2, [-56, 56], color=C["baffle"], lw=3)
    ax.add_patch(Rectangle((L["edf_y0"], -r), rc.X5_SHROUD_L, 2 * r, fill=False, ec=C["edf"], lw=2))
    ax.add_patch(Rectangle((L["edf_y0"] + 14, -14), rc.X5_UNIT_L - 14, 28, fc=C["edf"], alpha=0.45))
    for sgn in (1, -1):
        ax.plot([L["intake_y0"], L["intake_y1"]], [sgn * 62] * 2, color=C["intake"], lw=5)
        ax.plot([L["tube_y0"], L["tube_y1"]], [sgn * r, sgn * rc.NOZZLE_A / 2], color=C["tube"], lw=2)
    ax.set_title(f"plan section at the thrust axis (Z {z:.0f}); port and starboard are mirror images")
    y = np.arange(len(gaps))
    ax2.barh(y, [g[1] for g in gaps], color=[C["intake"] if g[1] >= g[2] else "r" for g in gaps])
    ax2.set_yticks(y)
    ax2.set_yticklabels([g[0] for g in gaps], fontsize=8.5)
    for i, g in enumerate(gaps):
        ax2.text(g[1] + 0.5, i, f"{g[1] / IN:.2f} in ({g[1]:.1f} mm), need {g[2]:.0f} mm",
                 va="center", fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlim(0, max(g[1] for g in gaps) * 1.9)
    ax2.set_xlabel("gap, mm")
    ax2.set_title("nearest gaps\n(aft gear bays are forward of Y 441: not in the rear cone)")
    notclosed = [yy for yy, s in sorted(m["stations"].items()) if not s["closed"]]
    fig.text(0.01, 0.01, f"Stations where the hull section is not a closed ring: {notclosed}. "
             "Y 560: a row of small holes in the skin; Y 650 and aft: the tail cap and its nozzle "
             "cluster.", fontsize=8.5)
    fig.suptitle("G1 interactions: clearances of the proposal")
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    return save(fig, out, "clearances")


def fig_cg(G, out):
    cg, parts = G["cg"], G["parts"]
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(13, 9), gridspec_kw={"height_ratios": [1, 1.5]})
    piv = cg["pivot_y"]
    pts = (("pivot", piv, "k"), ("CG now", cg["y0"], "0.4"),
           ("fan config", cg["y0"] + cg["fan"]["dy_mm"], C["fan"]),
           ("EDF config", cg["y0"] + cg["edf"]["dy_mm"], C["edf"]))
    ax.axvspan(piv - 6.4, piv + 6.4, color="#d5f5e3", label="working band +/-0.25 in (6.4 mm), ASSUMED")
    for i, (name, y, col) in enumerate(pts):
        ax.plot([y, y], [0, 1], color=col, lw=3)
        ax.text(y, 1.05 + 0.16 * (i % 2), f"{name}\nY {y:.1f}\n{(y - piv) / IN:+.2f} in "
                f"({y - piv:+.1f} mm)", ha="center", fontsize=8.5, color=col)
    ax.set_ylim(0, 1.75)
    ax.set_yticks([])
    ax.set_xlim(piv - 10, piv + 26)
    ax.set_xlabel("hover CG station Y, mm (aft to the right)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title(f"G1 weight and balance: hover CG against the tilt pivot (hover mass "
                 f"{cg['m0_g'] / 453.592:.2f} lbm ({cg['m0_g']:.0f} g))")
    names = [f"{p[0]} [{p[3]}]" for p in parts]
    mom = [p[1] * (p[2] - cg["y0"]) / 1000.0 for p in parts]
    cols = [C["fan"] if p[3] == "fan" else C["edf"] if p[3] == "edf" else "0.45" for p in parts]
    yy = np.arange(len(parts))
    ax2.barh(yy, mom, color=cols)
    ax2.set_yticks(yy)
    ax2.set_yticklabels(names, fontsize=8)
    for i, p in enumerate(parts):
        ax2.text(mom[i] + 0.1, i, f"{p[1] / 28.3495:.2f} oz ({p[1]:.1f} g) at Y {p[2]:.0f}",
                 va="center", fontsize=7.5)
    ax2.invert_yaxis()
    ax2.set_xlim(0, max(mom) * 1.6)
    ax2.set_xlabel("aft moment about the present CG, kg-mm  (grey: printed now and stays; "
                   "blue: fan only; red: Phase 11 only)")
    f, e = cg["fan"], cg["edf"]
    ax2.set_title(f"fan configuration +{f['dm_g'] / 453.592:.2f} lbm ({f['dm_g']:.0f} g), CG "
                  f"{f['dy_mm']:+.1f} mm;   EDF configuration +{e['dm_g'] / 453.592:.2f} lbm "
                  f"({e['dm_g']:.0f} g), CG {e['dy_mm']:+.1f} mm   (envelope estimates)",
                  fontsize=10)
    fig.tight_layout()
    return save(fig, out, "cg")


def fig_canon_side(G, out):
    L = G["L"]
    z = L["z_axis"]
    v = G["mesh"].vertices
    bins = np.arange(436, 692, 1.5)
    idx = np.digitize(v[:, 1], bins)
    top = [v[idx == i, 2].max() if (idx == i).any() else np.nan for i in range(1, len(bins))]
    bot = [v[idx == i, 2].min() if (idx == i).any() else np.nan for i in range(1, len(bins))]
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.fill_between(bins[:-1], bot, top, color="0.88")
    side_base(ax, G, 436, 695)
    for sgn in (1,):
        ax.add_patch(Rectangle((L["intake_y0"], z + 18), rc.INTAKE_L, rc.INTAKE_W, fc=C["intake"],
                               alpha=0.7))
        ax.add_patch(Rectangle((L["intake_y0"], z - 30), rc.INTAKE_L, rc.INTAKE_W, fc=C["intake"],
                               alpha=0.7))
    ax.text(L["intake_y0"] - 2, z + 46, "intakes (port pair shown;\nazimuth +135 and +195 deg)",
            color=C["intake"], fontsize=9)
    for dz in (20, -20):
        ax.plot(L["rcs_y"], z + dz, "o", ms=9, color=C["rcs"])
    ax.text(L["rcs_y"] - 16, z - 40, "RCS jets\n(port pair shown)", color=C["rcs"], fontsize=9)
    ax.plot([L["exit_y"]] * 2, [z - rc.NOZZLE_B / 2, z + rc.NOZZLE_B / 2], color=C["tube"], lw=4)
    ax.text(L["exit_y"] + 3, z + 26, f"nozzle exit plane Y {L['exit_y']:.0f}\n"
            f"{rc.NOZZLE_A / IN:.2f} x {rc.NOZZLE_B / IN:.2f} in", color=C["tube"], fontsize=9)
    ax.text(438, 250, "Compare with [REF-CAD-003] QMx Sheet 1 (port outboard profile) and "
            "[REF-CAD-002] nick-henning-close-back-combine.jpg.\n"
            f"Deviation: the tail cap and its nozzle cluster aft of Y {L['exit_y']:.0f} are replaced "
            "by the open fixed nozzle. Intake covers and RCS caps keep the skin closed until Phase 11.",
            fontsize=9, va="top")
    ax.set_title("G1 canonical shape: aft hull port profile with the proposed outer-mould-line "
                 "features (grey fill: full silhouette; lines: centreline section)")
    return save(fig, out, "canon_side")


def fig_canon_aft(G, out):
    L = G["L"]
    z = L["z_axis"]
    fig, ax = plt.subplots(figsize=(10, 10))
    for y, col in ((540, "0.75"), (L["rcs_y"], "0.45"), (L["exit_y"] + 8, "k")):
        draw(ax, cut(G["mesh"], [0, y, 0], [0, 1, 0], 0, 2), col, 0.8)
    ax.add_patch(Ellipse((0, z), rc.NOZZLE_A, rc.NOZZLE_B, fill=False, ec=C["tube"], lw=3))
    for az in rc.INTAKE_AZ:
        a = math.radians(az)
        ax.plot([62 * math.cos(a) * 0.9, 62 * math.cos(a) * 1.08],
                [z + 62 * math.sin(a) * 0.9, z + 62 * math.sin(a) * 1.08], color=C["intake"], lw=9,
                solid_capstyle="butt")
    for az in rc.RCS_PATTERNS[rc.RCS_RECOMMENDED]:
        a = math.radians(az)
        arrow(ax, (33 * math.cos(a), z + 33 * math.sin(a)), (58 * math.cos(a), z + 58 * math.sin(a)),
              C["rcs"], 2.5)
    ax.set_aspect("equal")
    ax.set_xlim(95, -95)
    ax.set_ylim(78, 250)
    ax.grid(alpha=0.25)
    ax.set_xlabel("X, mm (port on the left, seen from aft)")
    ax.set_ylabel("Z, mm")
    ax.text(93, 248, "light grey: bulb at Y 540   mid grey: RCS station   black: tail cap as built\n"
            "orange: fixed nozzle   green: 4 intakes   red: 4 RCS jets (recommended pattern)\n"
            "Compare with [REF-CAD-003] QMx Sheet 3 (stern elevation). The canon tail shows one "
            "large\nand four small exhausts in a recess; the open nozzle replaces that cluster.",
            fontsize=9, va="top")
    ax.set_title("G1 canonical shape: view from aft")
    return save(fig, out, "canon_aft")


def fig_canon_bow(G, out):
    head = G["head"]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
    draw(ax, cut(head, [0, 0, 0], [1, 0, 0], 1, 2))
    ax.set_xlim(-5, 130)
    ax.set_ylim(120, 290)
    ax.set_aspect("equal")
    ax.grid(alpha=0.25)
    ax.axvspan(20, 60, color=C["air"], alpha=0.15)
    ax.axvspan(46, 55, color="orange", alpha=0.35)
    ax.axvspan(80, 86, color="0.6", alpha=0.5)
    ax.text(21, 284, "vent path Y 20-60", color=C["air"], fontsize=9, va="top")
    ax.text(46, 124, "pitot hose\nturn", fontsize=8)
    ax.text(80, 124, "Observer-CN1\ntrunk", fontsize=8)
    ax.set_xlabel("station Y, mm")
    ax.set_ylabel("Z, mm")
    ax.set_title("head centreline section: bounds from docs/BAY_A_FWD_THERMAL.md sec 2")
    y_in = 32.0
    segs = cut(head, [0, y_in, 0], [0, 1, 0], 0, 2)
    draw(ax2, segs)
    pts = np.vstack(segs)
    zmid = (pts[:, 1].min() + pts[:, 1].max()) / 2
    half = np.abs(pts[np.abs(pts[:, 1] - zmid) < 4, 0]).max()
    for sgn in (1, -1):
        ax2.add_patch(Rectangle((sgn * half - (2 if sgn > 0 else 0), zmid - 12.5), 2, 25,
                                fc=C["air"], ec=C["air"]))
        arrow(ax2, (sgn * (half + 22), zmid), (sgn * (half + 3), zmid), C["air"], 2)
    ax2.set_aspect("equal")
    ax2.set_xlim(pts[:, 0].max() + 35, pts[:, 0].min() - 35)
    ax2.grid(alpha=0.25)
    ax2.set_xlabel("X, mm (port on the left, seen from aft)")
    ax2.set_title(f"head section at Y {y_in:.0f}: CANDIDATE bow inlet slots, each "
                  "0.98 x 0.63 in (25 x 16 mm)")
    fig.suptitle("G1 canonical shape: bow inlets. Candidate only -- position and canon fairing are "
                 "plan unit U6, not a G1 decision. Compare with [REF-CAD-003] QMx Sheet 3 (bow elevation).")
    fig.tight_layout()
    return save(fig, out, "canon_bow")


def fig_sizing(G, out):
    sz = G["sz"]
    areas = (("fan swept area", sz["fsa_mm2"], "0.5"),
             ("nozzle exit", math.pi / 4 * rc.NOZZLE_A * rc.NOZZLE_B, C["tube"]),
             ("intake required (1.2 x swept)", sz["intake_req_mm2"], "0.7"),
             ("intake provided (4 x 24 x 30)", sz["intake_have_mm2"], C["intake"]),
             ("repo scoop-capture figure", 3090.0, "0.85"),
             ("one RCS bore", math.pi / 4 * rc.RCS_BORE ** 2, C["rcs"]))
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
    y = np.arange(len(areas))
    ax.barh(y, [a[1] for a in areas], color=[a[2] for a in areas])
    ax.set_yticks(y)
    ax.set_yticklabels([a[0] for a in areas], fontsize=9)
    for i, a in enumerate(areas):
        ax.text(a[1] + 30, i, f"{a[1] / 645.16:.2f} in^2 ({a[1]:.0f} mm^2)", va="center", fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 4300)
    ax.set_xlabel("area, mm^2")
    ax.set_title(f"areas; intake margin {sz['intake_margin'] * 100:.0f} % over the bounding flow")
    ax2.axis("off")
    rows = (("station", "speed ft/s (m/s)", "Mach", "Reynolds"),
            ("intake throat", f"{sz['v_intake'] * 3.28084:.0f} ({sz['v_intake']:.0f})",
             f"{sz['mach_intake']:.2f}", "-"),
            ("rotor face", f"{sz['v_fan'] * 3.28084:.0f} ({sz['v_fan']:.0f})",
             f"{sz['mach_fan']:.2f}", "-"),
            ("nozzle exit", f"{sz['v_exit'] * 3.28084:.0f} ({sz['v_exit']:.0f})",
             f"{sz['mach_exit']:.2f}", f"{sz['re_exit']:.2e}"),
            ("open RCS jet", f"{sz['v_jet'] * 3.28084:.0f} ({sz['v_jet']:.0f})",
             f"{sz['mach_jet']:.2f}", f"{sz['re_jet']:.2e}"))
    t = ax2.table(cellText=rows, loc="upper center", cellLoc="center")
    t.scale(1, 1.8)
    t.auto_set_font_size(False)
    t.set_fontsize(9.5)
    ax2.text(0.0, 0.30,
             f"Bounding EDF flow {sz['q_cfm']:.0f} cfm ({sz['q_m3s']:.3f} m^3/s); thrust "
             f"{sz['thrust_n'] / 4.44822:.2f} lbf ({sz['thrust_n']:.1f} N).\n"
             "Method: static momentum theory, T = rho A_e V_e^2, at the nozzle exit area.\n"
             "Valid for incompressible flow; every Mach number here is below 0.3.\n"
             "ASSUMED: X5 thrust [REF-EDF-001] scaled to a 55 mm rotor at constant shaft power;\n"
             "intake ratio 1.2; bleed 15 % through 2 open jets; hub 28 mm.\n"
             f"One open jet: {sz['f_jet_n'] / 4.44822:.2f} lbf ({sz['f_jet_n']:.2f} N) at "
             f"{sz['rcs_arm_mm'] / IN:.1f} in ({sz['rcs_arm_mm']:.0f} mm) from the pivot = "
             f"{sz['m_jet_nm'] * 8.8507:.1f} lbf-in ({sz['m_jet_nm']:.2f} N-m).",
             fontsize=9.5, va="top", transform=ax2.transAxes)
    fig.suptitle("G1 flow sizing: fused intake area, tube and RCS bore against the bounding EDF "
                 "flow (plan R21) -- PROVISIONAL")
    fig.tight_layout()
    return save(fig, out, "sizing")


def fig_fan_curve(G, out):
    n, th = G["n"], G["thermal"]
    q = np.linspace(0, 0.122 / 60, 200)
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.plot(q * 2118.88, [n.fan_dp(x) for x in q], color=C["fan"], lw=2.5,
            label="Delta ASB02505SHA-AY6B at 5 V (digitized, REF-FAN-001 requires verification)")
    ax.plot(q * 2118.88, [n.system_dp(x, th["rho"], th["areas"]) for x in q], color="k", lw=2,
            label="system: bow inlets to the nozzle (1-D, K ASSUMED)")
    ax.plot(th["q"] * 2118.88, th["dp"], "o", ms=11, color="r")
    ax.annotate(f"operating point\n{th['q'] * 2118.88:.2f} cfm at {th['dp'] / 249.089:.3f} in H2O "
                f"({th['dp']:.1f} Pa)", (th["q"] * 2118.88, th["dp"]), (2.2, 35),
                arrowprops=dict(arrowstyle="->"), fontsize=10)
    qd = 0.5 * 1.225 * (25 * 0.514444) ** 2
    ax.axhline(qd, color="orange", ls="--")
    ax.text(0.05, qd + 2, f"dynamic pressure at 25 kt: {qd / 249.089:.2f} in H2O ({qd:.0f} Pa)",
            color="darkorange", fontsize=10)
    ax.set_xlabel("flow, cfm")
    ax.set_ylabel("pressure, Pa")
    ax.set_ylim(0, 110)
    ax.legend(loc="upper right", fontsize=8.5)
    ax.grid(alpha=0.3)
    ax.set_title("G1 flow sizing: fan curve against the stream. The fan works at a pressure far "
                 "below the outside\ndynamic pressure in forward flight, so outside flow governs "
                 "the stream at cruise (plan KTD6)")
    fig.tight_layout()
    return save(fig, out, "fan_curve")


def fig_fan_electrical(G, out):
    el = G["el"]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={"width_ratios": [1, 1.3]})
    ax.bar(["fan rated draw", "stern stack 5 V\nfan line budget"], [el["fan_a"], el["budget_a"]],
           color=["r" if el["fan_a"] > el["budget_a"] else C["fan"], "0.6"])
    for i, v in enumerate((el["fan_a"], el["budget_a"])):
        ax.text(i, v + 0.003, f"{v:.2f} A", ha="center", fontsize=11)
    ax.set_ylabel("current at 5 V, A")
    ax.set_ylim(0, 0.16)
    ax.set_title("fan load against the budget: SHORT by "
                 f"{(el['fan_a'] / el['budget_a'] - 1) * 100:.0f} %")
    ax2.axis("off")
    boxes = (("stern stack\nNoNFO-Pilot-PB2\nfan-drive output", 0.02), ("lead + connector\nrear cone",
             0.37), ("Delta fan\n5 V, 0.60 W\nrated", 0.72))
    for txt, x in boxes:
        ax2.add_patch(Rectangle((x, 0.55), 0.25, 0.3, fill=False, transform=ax2.transAxes))
        ax2.text(x + 0.125, 0.70, txt, ha="center", va="center", fontsize=9, transform=ax2.transAxes)
    for x in (0.27, 0.62):
        ax2.annotate("", (x + 0.10, 0.72), (x, 0.72), xycoords="axes fraction",
                     arrowprops=dict(arrowstyle="->", lw=2))
    ax2.annotate("", (0.27, 0.62), (0.72, 0.62), xycoords="axes fraction",
                 arrowprops=dict(arrowstyle="->", lw=1.5, ls="--", color="purple"))
    ax2.text(0.5, 0.57, "tach (requires verification)", color="purple", ha="center", fontsize=9,
             transform=ax2.transAxes)
    ax2.text(0.0, 0.45,
             f"Fan: {rc.FAN_W:.2f} W at {rc.FAN_V:.0f} V = {el['fan_a']:.2f} A (value carried in "
             "tools/node_thermal_forced_air.py).\n"
             f"Budget: {el['budget_a']:.2f} A, zone_contract.json power_5v.fan, basis "
             f"{el['budget_basis']}.\n\n"
             "REQUIRES VERIFICATION before layout (the maker's datasheet could not be fetched\n"
             "in this session):\n"
             "  1. rated and start-up current of the ASB02505SHA-AY6B;\n"
             "  2. whether this part number has a tach output. Plan R20 needs one, or a\n"
             "     current-sense fault detect on the fan-drive output in its place;\n"
             "  3. wire gauge and connector rating, with margin.",
             fontsize=9.5, va="top", transform=ax2.transAxes)
    fig.suptitle("G1 electrical: cooling fan on the stern stack fan-drive output (plan KD9, R20)")
    fig.tight_layout()
    return save(fig, out, "fan_electrical")


def fig_harness(G, out):
    L = G["L"]
    z = L["z_axis"]
    fig, ax = plt.subplots(figsize=(13, 7))
    side_base(ax, G, 470, 690)
    envelopes(ax, L, "fan")
    ax.add_patch(Rectangle((478, z - 38), rc.STERN_STACK_Y1 - 478, 76, fc="0.8", ec="k"))
    ax.text(479, z + 42, "stern stack", fontsize=9)
    zf = G["meas"]["stations"][540]["zc"] - G["meas"]["stations"][540]["dia"] / 2 + 6
    route = np.array([(rc.STERN_STACK_Y1, z - 30), (512, zf), (L["fan_y0"] - 14, zf),
                      (L["fan_y0"] - 3, z - 20), (L["fan_y0"] + 2, z - 13)])
    ax.plot(route[:, 0], route[:, 1], color="purple", lw=2.5)
    length = float(np.sum(np.hypot(*np.diff(route, axis=0).T)))
    ax.plot(L["fan_y0"], z - 20, "s", ms=9, color="purple")
    ax.text(515, zf - 12, f"fan lead along the bulb floor: {inmm(length)} routed, plus a\n"
            "1.0 in (25 mm) service loop at the fan. Tied at 2 printed saddles.", color="purple",
            fontsize=9)
    ax.text(L["fan_y0"] + 4, z - 30, "sealed grommet\nthrough the adapter", color="purple",
            fontsize=9)
    ax.text(472, 250, "Connector at the stern stack end, so the fan and adapter come out with the "
            "lead attached.\nAdapter to spider: 3 screws into the spider bosses; thread type, length "
            "and engagement are set with the spider in plan unit U5.\nBend radius, connector type and "
            "mating clearance: requires verification against the chosen connector.", fontsize=9,
            va="top")
    ax.set_title("G1 harness and mounting fit: cooling fan lead, pass-through and fasteners")
    return save(fig, out, "harness")


def fig_thermal_baseline(G, out):
    th = G["thermal"]
    rows = th["avg"]
    names = [r["name"].split(" (")[0] for r in rows]
    t = [r["t_bare"] for r in rows]
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.bar(names, [x * 9 / 5 + 32 for x in t],
           color=["r" if x > th["limit"] else C["intake"] for x in t])
    lim_f = th["limit"] * 9 / 5 + 32
    ax.axhline(lim_f, color="k", ls="--")
    ax.text(len(names) - 0.6, lim_f + 6, f"limit {lim_f:.0f} F ({th['limit']:.0f} C)", ha="right")
    for i, r in enumerate(rows):
        ax.text(i, t[i] * 9 / 5 + 32 + 5, f"{t[i] * 9 / 5 + 32:.0f} F\n({t[i]:.0f} C)\n"
                f"{r['v'] * 3.28084:.1f} ft/s", ha="center", fontsize=8.5)
    ax.set_ylabel("board temperature, F (average-power case)")
    ax.set_ylim(0, 470)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    ax.set_title(f"G1 thermal load: measured baseline, fan alone, open stream. Fan flow "
                 f"{th['q'] * 2118.88:.2f} cfm. Local air speed is shown under each value.\n"
                 "PROVISIONAL: every thermal input is ASSUMED; eight-pouch model; cargo cavity "
                 "approximated (plan unit U2 corrects it)")
    fig.tight_layout()
    return save(fig, out, "thermal_baseline")


def fig_flow_guides(G, out):
    th = G["thermal"]
    fig, ax = plt.subplots(figsize=(13, 6.5))
    keys = [a[0] for a in th["areas"]]
    area = [a[3] * 1e6 for a in th["areas"]]
    x = np.arange(len(keys))
    ax.bar(x, area, color="0.75", label="free area now")
    for g in th["guides"]:
        i = keys.index(g["station"])
        ax.bar(i, g["area_mm2"], color=C["air"], width=0.5,
               label="necked area a guide must give" if g is th["guides"][0] else None)
        ax.text(i, area[i] + 300, f"{g['node']}\nneeds {g['v_req'] * 3.28084:.1f} ft/s "
                f"({g['v_req']:.2f} m/s)\n-> {g['area_mm2'] / 645.16:.2f} in^2 "
                f"({g['area_mm2']:.0f} mm^2)", ha="center", fontsize=8.5, color=C["air"])
    ax.set_xticks(x)
    ax.set_xticklabels(keys)
    ax.set_ylabel("free flow area at the station, mm^2")
    ax.set_ylim(0, max(area) * 1.35)
    ax.legend(loc="upper left")
    ax.set_title("G1 thermal load: where printed flow guides go (plan KD12, unit U12).\n"
                 "Speed each failing node needs to pass the average case with no spreader, at the "
                 "present fan flow -- PROVISIONAL; the added pressure loss is not yet in the fan match")
    fig.tight_layout()
    return save(fig, out, "flow_guides")


def fig_rcs_options(G, out):
    L, sz = G["L"], G["sz"]
    z = L["z_axis"]
    fig, axs = plt.subplots(2, 2, figsize=(14, 13.5))
    for ax, (name, rows) in zip(axs.flat, G["patterns"].items()):
        _xsec(ax, G, L["rcs_y"], name + ("  (RECOMMENDED)" if name == rc.RCS_RECOMMENDED else ""))
        ax.add_patch(Ellipse((0, z), 58, 58, fill=False, ec=C["tube"], lw=2))
        for r in rows:
            a = math.radians(r["az"])
            col = C["intake"] if r["clear"] else "r"
            wedge = rc.jet_wedge(z, r["az"], r["r_skin"] + rc.JET_SKIP, r["r_skin"] + 60.0)
            ax.fill(*wedge.exterior.xy, color=col, alpha=0.22)
            arrow(ax, (29 * math.cos(a), z + 29 * math.sin(a)),
                  (r["r_skin"] + 30) * np.array([math.cos(a), math.sin(a)]) + np.array([0, z]),
                  col, 2.4)
            rr = min(r["r_skin"] + 46, 74.0)
            ax.text(rr * math.cos(a), z + rr * math.sin(a), "clear" if r["clear"] else "BLOCKED",
                    color=col, ha="center", va="center", fontsize=9, weight="bold",
                    bbox=dict(fc="white", ec="none", alpha=0.7, pad=1))
        for az in G["sectors"]:
            a = math.radians(az)
            ax.plot(90 * math.cos(a), z + 90 * math.sin(a), ".", color=C["intake"], ms=4)
    fig.suptitle(f"G1 decision OQ1: RCS jet stations at Y {L['rcs_y']:.0f}, seen from aft. Shaded: "
                 f"jet footprint, {rc.RCS_BORE:.0f} mm bore spreading at {rc.JET_HALF_ANGLE:.0f} deg "
                 "(ASSUMED).\nA jet is clear when its footprint meets no structure within "
                 f"{rc.JET_REACH / IN:.1f} in ({rc.JET_REACH:.0f} mm) of the skin. Green dots: every "
                 f"clear azimuth. One open jet: {sz['f_jet_n'] / 4.44822:.2f} lbf "
                 f"({sz['f_jet_n']:.2f} N) -- PROVISIONAL")
    fig.tight_layout(rect=(0, 0, 1, 0.95), h_pad=3.0)
    return save(fig, out, "rcs_options")


# ---- data -----------------------------------------------------------------------------------
def thermal_data():
    """Baseline node budget with the stated closed-door approximation of the cargo cavity."""
    import node_thermal_forced_air as n
    from shapely.ops import unary_union

    def cavity(y):
        rings = n._xz(n._hull_at(y), y, "interiors")
        best = max(rings, key=lambda q: q.area) if rings else None
        if best is None or best.area < 1000.0:
            return unary_union(n._xz(n._hull_at(y), y, "exterior")).convex_hull.buffer(-2.0)
        return best

    n.cavity_at = cavity
    inp = n.Inputs()
    areas = n.station_areas(inp)
    q, dp, rho = n.operating_point(inp, areas)
    avg, _ = n.budget(inp, "average", areas)
    nodes = {nd.name: nd for nd in n.nodes(inp)}
    guides = []
    for r in avg:
        if r["t_bare"] <= inp.t_limit_c:
            continue
        nd = nodes[r["name"]]
        lo, hi = 0.01, 60.0
        for _ in range(60):
            mid = (lo + hi) / 2
            t = n.board_temp(inp, n.h_flat_plate(mid)[0], r["t_air"], nd.p_avg, nd.exposed, 0.0)
            lo, hi = (mid, hi) if t > inp.t_limit_c else (lo, mid)
        key = n.NODE_STATION[r["name"].split()[0]]
        guides.append({"node": r["name"].split(" (")[0], "station": key, "v_req": hi,
                       "area_mm2": q / hi * 1e6})
    merged = {}
    for g in guides:  # nodes that share a station share one guide: the faster speed governs
        if g["station"] not in merged or g["v_req"] > merged[g["station"]]["v_req"]:
            merged[g["station"]] = g
    return n, {"areas": areas, "q": q, "dp": dp, "rho": rho, "avg": avg,
               "limit": inp.t_limit_c, "guides": list(merged.values())}


def gather():
    r = rc.evaluate()
    mesh = rc.load_aft_hull()
    n, th = thermal_data()
    return {"mesh": mesh, "head": load(HEAD_HULL), "L": r["layout"], "meas": r["meas"],
            "sz": r["sizing"], "parts": r["parts"], "cg": r["cg"], "el": r["electrical"],
            "patterns": r["patterns"], "sectors": r["sectors"], "d_min": r["d_min"], "n": n, "thermal": th,
            "side": cut(mesh, [hd.X_CL, 0, 0], [1, 0, 0], 1, 2),
            "plan": cut(mesh, [0, 0, r["layout"]["z_axis"]], [0, 0, 1], 1, 0)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=os.path.join(REPO, "docs", "figures"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    G = gather()
    missing = []
    for name in FIGURES:
        path = globals()["fig_" + name](G, args.out)
        ok = os.path.exists(path) and os.path.getsize(path) > 5000
        print(("wrote  " if ok else "MISSING ") + os.path.relpath(path, REPO))
        if not ok:
            missing.append(name)
    if missing:
        print("FAIL: missing figures:", ", ".join(missing))
        return 1
    print(f"OK: {len(FIGURES)} figures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
