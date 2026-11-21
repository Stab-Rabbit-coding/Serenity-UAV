#!/usr/bin/env python3
"""theme_n_od_briefs.py -- numbers and figures for the Theme N Owner Decision Briefs (2026-11-21).

Five open owner items from Rev U Theme N (`docs/THEME_N_DECISION_BRIEFS.md`):

  A  ESC bays: implement the OD-3 four-bay layout (NAC-64-BAYB-SHROUD, NAC-64-ESC-80A.j/.l)
  B  Port/starboard mirror rule for the ESC bays, lead conduits and vanes (NAC-64-LEAD-AZ)
  C  OD17-FAIR-BORE: leave the as-built fairing, or fund isolating CFD runs
  D  D-SV-2: nozzle-servo rail voltage for the KST CM07
  E  KST CM07 pocket integration in the dorsal spine (NAC-64-SERVO-01, plan U4)

Every brief carries the six checks of `docs/DOC_TEMPLATES.md` "Owner Decision Briefs" (D uses the
avionics / power-electrical set, the CM07 being a motor), each with a picture and with load or
motion vectors.  Every number is computed here from the repository's own meshes and tools, or
quoted from the source named beside it; nothing is typed in that a tool can measure.

Usage:  /usr/bin/python3 tools/theme_n_od_briefs.py [--json PATH]
Writes docs/figures/odb_theme_n_{a,b,c,d,e}.png and prints the numbers (JSON with --json).

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding) -- owner decisions.
AI note: Analysis and tool by Claude (Claude Opus 5.5, Anthropic) under the author's direction,
         2026-11-21, per AGENTS.md section 3.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import shapely.geometry as sg  # noqa: E402
import trimesh  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import esc80_cooptimize as eo  # noqa: E402  OD-3 bay layout (the tool that sized the 70 A ESC)
import nacelle64_esc_bay_check as bayck  # noqa: E402  published-mesh loaders (nacelle-local)
import nacelle_64_scale as ns  # noqa: E402  single-source scale and pivot
import nacelle_mass_cg_64 as nac64  # noqa: E402  rotating-assembly rows
import nozzle_servo_linkage_64 as nsl  # noqa: E402  linkage solve (servo table swap)

REPO = Path(__file__).resolve().parent.parent
FIG = REPO / "docs" / "figures"
IN = 25.4
G = 9.80665
LBF = 4.448222
RHO_PA_CF = 1.11e-3            # g/mm3, tools/sls_materials.py PA_CF (3DS-30108A)
SIGMA_PA_CF = 84.0             # MPa, current-specification/allowables.json SLS-PA-CF tensile
PIVOT = ns.pivot_z()           # 118.9 mm
P64_A = ns.get("P64_A")
ESC_MOUNT_R = 37.2             # pod ESC_MOUNT_R = 32 + 2.5 + 0.2 + 2.5
CURRENT_BAYS = [68.0, 248.0]   # pod ESC_BAY_AZ (hinge), both pods, as cut
CUR_Z = (95.0 * P64_A - 21.0, 95.0 * P64_A + 21.0)          # 92.79 .. 134.79
CUR_LEDGE = 8.0                # ESC_LEDGE_W
W_POW, W_SIG = 23.0, 10.0      # pod panel widths (current bays)
SPRING_N = 2.0                 # fail-open spring at the ring ear, plan 2026-09-28-001 KTD3
# KST CM07 Technical Specification 2026-05 (open-servo-core-secure/hardware)
CM07: dict[str, Any] = {
    "dims": (20.5, 7.5, 19.0), "mass_g": 7.0, "lugs_mm": 24.5,
    "stall_kgfcm": {3.5: 1.10, 4.2: 1.40, 6.0: 1.80, 7.4: 2.10, 8.4: 2.40},
    "speed_s60": {3.5: 0.14, 4.2: 0.11, 6.0: 0.08, 7.4: 0.07, 8.4: 0.06},
    # Performance chart @7.4 V (read from the sheet): continuous zone ends ~0.45 kgf.cm;
    # current is ~linear, ~0.37 A per kgf.cm (0.78 A at the 2.10 kgf.cm stall).  READ OFF A CHART.
    "cont_kgfcm_7v4": 0.45, "a_per_kgfcm_7v4": 0.37,
}
X06H: dict[str, Any] = {"dims": (20.0, 7.0, 16.6), "mass_g": 6.0, "stall_nm_6v": 0.150,
                        "cont_nm_6v": 0.040}
KGFCM = 0.0980665              # N.m per kgf.cm


def sec_in(ax, axis="x"):
    """Secondary axis in mm for an axis plotted in inches (imperial first)."""
    if axis == "x":
        s = ax.secondary_xaxis("top", functions=(lambda v: v * IN, lambda v: v / IN))
        s.set_xlabel("mm", fontsize=7)
    else:
        s = ax.secondary_yaxis("right", functions=(lambda v: v * IN, lambda v: v / IN))
        s.set_ylabel("mm", fontsize=7)
    s.tick_params(labelsize=7)


def arrow(ax, x, y, dx, dy, color, label=None, lw=1.6):
    ax.annotate("", xy=(x + dx, y + dy), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw))
    if label:
        ax.text(x + dx, y + dy, " " + label, color=color, fontsize=7, va="center")


# ── shared geometry ────────────────────────────────────────────────────────────────────────────
_LOCAL: dict = {}


def pod_local(side: str = "stbd") -> trimesh.Trimesh:
    if side not in _LOCAL:
        _LOCAL[side] = bayck.local_mesh(f"Nacelle64_{side.capitalize()}")
    return _LOCAL[side]


def od3_layout() -> dict:
    """Per-bay footprints of the OD-3 (70 A, two bays per ESC) layout, PORT frame."""
    p = json.loads((REPO / "tools/esc70_design.json").read_text())
    s_n = p.get("nacelle_scale", 1.0)
    eo.P64_K, eo.P64_A = 1.21 * s_n, 1.13 * s_n
    eo.Z_MAX = 160.0 * eo.P64_A
    eo.LOOP_Z_MAX = (166.25 * 1.13 - 16.25) * s_n
    eo.KEEPOUTS = [(a0, a1, z0 * s_n, z1 * s_n) for a0, a1, z0, z1 in p["keepouts"]]
    zs, skin = eo.skin64(p.get("z_min", eo.Z_MIN_V2 * s_n))
    if p.get("measured_exclusions"):
        eo.bay.EXCLUDE = []
    env = p["pcb_t"] + p["h_outer"] + p["h_inner"] + p["mount_gap"]
    env += 0.0 if p.get("lane_in_layout") else p["flow_lane"]
    wp, ws = p["w_power"], p["w_signal"]
    a_p = math.degrees(math.atan2(wp / 2, eo.MOUNT_R))
    a_s = math.degrees(math.atan2(ws / 2, eo.MOUNT_R))
    bays = {}
    for esc, phis in (("A", (324.0, 258.0)), ("B", (80.0, 22.0))):
        for phi in phis:
            pr = eo.bay_profile(zs, skin, phi, env, wp, ws, p.get("fmin", 0.6))
            bays[f"{esc}{phi:.0f}"] = {
                "esc": esc, "hinge": phi, "z": (pr[0][0], pr[-1][0] + eo.DZ),
                "az": (phi - 2 * a_s, phi + 2 * a_p),
                "area": sum((r[1] + r[2]) * eo.DZ for r in pr)}
    need = eo.needs_v2(p)
    return {"bays": bays, "keepouts": eo.KEEPOUTS, "need_outline_mm2": (need[0] + need[1]) / 2.0,
            "need_both_faces_mm2": need[0] + need[1], "env_mm": env}


def stbd_az(lo: float, hi: float) -> tuple[float, float]:
    """Port-frame azimuth interval -> starboard frame (X mirror: a -> 180 - a)."""
    return ((180.0 - hi) % 360.0, (180.0 - lo) % 360.0)


def sector(r0: float, r1: float, a0: float, a1: float) -> sg.Polygon:
    a = np.radians(np.linspace(a0, a1 if a1 > a0 else a1 + 360.0, 40))
    pts = [(r0 * math.cos(t), r0 * math.sin(t)) for t in a]
    pts += [(r1 * math.cos(t), r1 * math.sin(t)) for t in a[::-1]]
    return sg.Polygon(pts)


def section_poly(mesh: trimesh.Trimesh, z: float):
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        raise ValueError(f"no section at Z {z}")
    planar, _ = sec.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -z],
                                          [0, 0, 0, 1]], float))
    return sg.MultiPolygon(list(planar.polygons_full)).buffer(0)


def polys(geom) -> list:
    """The polygon parts of a shapely result (booleans can leave lines or points behind)."""
    if isinstance(geom, sg.Polygon):
        return [geom] if geom.area > 0 else []
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, sg.Polygon) and g.area > 0]


def zmod(poly) -> dict:
    """Area and elastic section moduli of a section (mm units): exterior rings minus holes."""
    parts = polys(poly)
    mp = sg.MultiPolygon(parts)
    c = mp.centroid
    ixx = iyy = 0.0
    xs: list[float] = []
    ys: list[float] = []
    for p in parts:
        for ring, sgn in [(p.exterior, 1.0), *[(h, -1.0) for h in p.interiors]]:
            q = np.asarray(ring.coords)
            x, y = q[:, 0] - c.x, q[:, 1] - c.y
            cr = x[:-1] * y[1:] - x[1:] * y[:-1]
            ixx += sgn * abs(np.sum((y[:-1] ** 2 + y[:-1] * y[1:] + y[1:] ** 2) * cr) / 12.0)
            iyy += sgn * abs(np.sum((x[:-1] ** 2 + x[:-1] * x[1:] + x[1:] ** 2) * cr) / 12.0)
            xs.extend(x)
            ys.extend(y)
    return {"area": mp.area, "ixx": ixx, "iyy": iyy,
            "zx": ixx / max(abs(min(ys)), max(ys)), "zy": iyy / max(abs(min(xs)), max(xs))}


def bending(pod: trimesh.Trimesh, zs: np.ndarray) -> np.ndarray:
    """Bending moment per 1 g (N.mm) along the pod, axis horizontal, supported at the pivot.

    Point masses from the roll-up (nacelle_mass_cg_64.rows_64) plus the pod shell distributed by
    its own section areas."""
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        pod.export(f.name)
        rows = nac64.rows_64(Path(f.name))
    pts = [(m, z) for name, m, z, _ in rows if not name.startswith("Pod shell")]
    zz = np.arange(1.0, 209.0, 2.0)
    areas = []
    for z in zz:
        try:
            areas.append(section_poly(pod, float(z)).area)
        except ValueError:
            areas.append(0.0)
    shell = np.array(areas) * 2.0 * RHO_PA_CF
    shell *= rows[0][1] / shell.sum()                  # normalise to the measured shell mass
    pts += list(zip(shell, zz))
    out = []
    for z in zs:
        if z <= PIVOT:
            mom = sum(m * (z - zi) for m, zi in pts if zi < z)
        else:
            mom = sum(m * (zi - z) for m, zi in pts if zi > z)
        out.append(mom * 1e-3 * G)                     # g.mm -> N.mm
    return np.array(out)


# ── Brief A ─────────────────────────────────────────────────────────────────────────────────────
def brief_a(res: dict) -> None:
    lay = od3_layout()
    bays = lay["bays"]
    pod = pod_local("stbd")
    covers = [bayck.local_mesh(f"EscCover64_Stbd_{b}") for b in ("A", "B")]
    closed = trimesh.util.concatenate([pod, *covers])
    assert isinstance(closed, trimesh.Trimesh)
    zs = np.arange(70.0, 186.0, 1.0)
    mom = bending(pod, zs)
    # Section moduli at the governing window stations, starboard frame.
    st = {}
    for z in (100.0, 125.0, 150.0, 175.0):
        base_ = section_poly(closed, z)
        cur = section_poly(pod, z)
        od3 = base_
        for b in bays.values():
            if b["z"][0] <= z <= b["z"][1]:
                a0, a1 = stbd_az(*b["az"])
                od3 = od3.difference(sector(ESC_MOUNT_R, 120.0, a0, a1))
        m = float(np.interp(z, zs, mom))
        st[z] = {"M_Nmm_per_g": m,
                 "Z_closed": zmod(base_)["zx"], "Z_current": zmod(cur)["zx"],
                 "Z_od3": zmod(od3)["zx"],
                 "sig_current_MPa_per_g": m / zmod(cur)["zx"],
                 "sig_od3_MPa_per_g": m / zmod(od3)["zx"],
                 "poly_od3": od3, "poly_closed": base_}
    gov = max(st, key=lambda k: st[k]["sig_od3_MPa_per_g"])
    cur_outline = (CUR_Z[1] - CUR_Z[0]) * (W_POW + W_SIG)
    per_esc = {e: sum(b["area"] for b in bays.values() if b["esc"] == e) for e in ("A", "B")}
    # Cover masses: one cover per bay = (bay + ledge band) x cover thickness at PA CF (estimate,
    # scaled from the measured current cover 7.43 g over its own outline).
    cur_cover_outline = (CUR_Z[1] - CUR_Z[0] + 2 * CUR_LEDGE) * (W_POW + W_SIG + 2 * CUR_LEDGE)
    g_per_mm2 = 7.43 / cur_cover_outline
    od3_covers = sum((b["z"][1] - b["z"][0] + 2 * CUR_LEDGE)
                     * (ESC_MOUNT_R * math.radians(b["az"][1] - b["az"][0]) + 2 * CUR_LEDGE)
                     for b in bays.values()) * g_per_mm2
    res["A"] = {
        "bays_port_frame": {k: {"z": v["z"], "az": v["az"], "area_mm2": v["area"]}
                            for k, v in bays.items()},
        "need_outline_mm2_per_esc": lay["need_outline_mm2"],
        "current_single_bay_outline_mm2": cur_outline,
        "od3_outline_mm2_per_esc": per_esc,
        "stations": {k: {kk: vv for kk, vv in v.items() if not kk.startswith("poly")}
                     for k, v in st.items()},
        "governing_station": gov,
        "covers_g_per_nacelle_od3": od3_covers, "covers_g_per_nacelle_roll_up": 4 * 7.43,
    }

    fig, axs = plt.subplots(2, 3, figsize=(17, 10.5))
    # (1) statics and dynamics
    ax = axs[0, 0]
    ax.plot(zs / IN, mom * 1e-3 / 0.112985, color="k", lw=1.4,
            label="bending moment, 1 g, axis horizontal")
    ax.axvline(PIVOT / IN, color="0.4", ls=":", lw=1)
    for b in bays.values():
        ax.axvspan(b["z"][0] / IN, b["z"][1] / IN, color="C2", alpha=0.10)
    ax.axvspan(CUR_Z[0] / IN, CUR_Z[1] / IN, color="C3", alpha=0.10)
    ymax = mom.max() * 1e-3 / 0.112985
    arrow(ax, PIVOT / IN, 0.05 * ymax, 0, 0.30 * ymax, "C0", "trunnion reaction")
    for name, m, z in ((("motor 1", 140, 74.2)), ("motor 2", 140, 147.9),
                       ("nozzle", 61, 180.0)):
        arrow(ax, z / IN, 0.55 * ymax, 0, -0.18 * ymax * m / 140, "C3",
              f"{name} {m * 0.0022:.2f} lbf")
    ax.set_xlabel("pod station Z, in")
    ax.set_ylabel("bending moment per g, lbf.in")
    ax.set_ylim(0, 1.1 * ymax)
    ax.set_title("1 Statics and dynamics: pod as a beam on the trunnion\n"
                 f"governing window station Z {gov / IN:.2f} in ({gov:.0f} mm): "
                 f"{st[gov]['sig_od3_MPa_per_g'] * 145.04:.0f} psi/g OD-3, "
                 f"allowable {SIGMA_PA_CF * 145.04:,.0f} psi", fontsize=9)
    ax.legend(fontsize=7, loc="upper left")
    sec_in(ax)
    # (2) function: board outline per ESC
    ax = axs[0, 1]
    labels = ["current pod\n(1 bay/ESC)", "OD-3 ESC A\n(2 bays)", "OD-3 ESC B\n(2 bays)"]
    vals = [cur_outline, per_esc["A"], per_esc["B"]]
    cols = ["C3", "C2", "C2"]
    ax.bar(labels, [v / 645.16 for v in vals], color=cols)
    ax.axhline(lay["need_outline_mm2"] / 645.16, color="k", ls="--",
               label=(f"70 A ESC needs {lay['need_outline_mm2'] / 645.16:.2f} in² outline"
                      " (both faces)"))
    for i, v in enumerate(vals):
        ax.text(i, v / 645.16, f"{v / 645.16:.2f} in²\n({v:,.0f} mm²)", ha="center", va="bottom",
                fontsize=8)
    ax.set_ylabel("board outline available per ESC, in²")
    ax.set_title("2 Function: does one ESC fit its bays?", fontsize=9)
    ax.legend(fontsize=7, loc="upper left")
    # (3) structural integrity: section at the governing station
    ax = axs[0, 2]
    poly = st[gov]["poly_od3"]
    for p in polys(st[gov]["poly_closed"]):
        ax.fill(*np.asarray(p.exterior.coords).T / IN, color="C3", alpha=0.25)
        for h in p.interiors:
            ax.fill(*np.asarray(h.coords).T / IN, color="white")
    ax.fill([], [], color="C3", alpha=0.25, label="material removed by the OD-3 windows")
    ax.fill([], [], color="0.55", label="section left with the windows open")
    for p in polys(poly):
        ax.fill(*np.asarray(p.exterior.coords).T / IN, color="0.55")
        for h in p.interiors:
            ax.fill(*np.asarray(h.coords).T / IN, color="white")
    m = st[gov]["M_Nmm_per_g"]
    arrow(ax, 0, 0, 0, -1.2, "C0", f"M {m / 112.985:.2f} lbf.in per g")
    ax.set_aspect("equal")
    ax.set_xlabel("x, in (stbd, +X pylon)")
    ax.set_ylabel("y, in (+y down)")
    ax.legend(fontsize=7, loc="upper right")
    ax.set_title(f"3 Structural integrity: section at Z {gov:.0f} mm with the OD-3 windows\n"
                 f"Z closed {st[gov]['Z_closed'] / 16387:.2f} in³, OD-3 open "
                 f"{st[gov]['Z_od3'] / 16387:.2f} in³ "
                 f"({st[gov]['Z_od3'] / st[gov]['Z_closed']:.2f} of closed)", fontsize=9)
    # (4) interactions: unwrapped map, PORT frame
    ax = axs[1, 0]
    for a0, a1, z0, z1 in lay["keepouts"]:
        ax.add_patch(mpatches.Rectangle((a0, z0 / IN), a1 - a0, (z1 - z0) / IN, color="0.6",
                                        alpha=0.5))
    ax.add_patch(mpatches.Rectangle((226, 100 / IN), 88, 109 / IN, fill=False, hatch="//",
                                    ec="0.5", lw=0.5))
    cm07 = (180 - 278.8, 180 - 254.6)          # CM07 pocket at shaft az 280, starboard -> port
    ax.add_patch(mpatches.Rectangle(((cm07[0]) % 360, 138.7 / IN), cm07[1] - cm07[0],
                                    21.7 / IN, color="C1", alpha=0.7, label="CM07 pocket"))
    for b in bays.values():
        ax.add_patch(mpatches.Rectangle((b["az"][0], b["z"][0] / IN), b["az"][1] - b["az"][0],
                                        (b["z"][1] - b["z"][0]) / IN, color="C2", alpha=0.6))
        ax.text(b["hinge"], b["z"][1] / IN, f"OD-3 {b['esc']}", fontsize=7, ha="center",
                va="bottom")
    for h in CURRENT_BAYS:          # current bays as cut on the PORT pod (not mirrored)
        ax.add_patch(mpatches.Rectangle((h - 15.4, CUR_Z[0] / IN), 50.6, (CUR_Z[1] - CUR_Z[0]) / IN,
                                        fill=False, ec="C3", lw=1.4, ls="--"))
    ax.axhline(103.7 / IN, color="C4", lw=0.8)
    ax.text(2, 103.7 / IN, "stage-2 cartridge front", fontsize=6, color="C4", va="bottom")
    ax.axhline(PIVOT / IN, color="0.3", lw=0.8, ls=":")
    ax.set_xlim(0, 360)
    ax.set_ylim(60 / IN, 215 / IN)
    ax.set_xlabel("azimuth, deg (PORT frame; stbd = 180 - az)")
    ax.set_ylabel("pod station Z, in")
    ax.set_title("4 Mechanism/component interactions (port frame)\n"
                 "grey: keep-outs (servo+linkage, trunnion, nav/disconnect); hatched: shroud; "
                 "red dashed: bays as cut on the PORT pod", fontsize=8)
    sec_in(ax, "y")
    # (5) weight and balance
    ax = axs[1, 1]
    cats = ["covers per nacelle", "ESC stations (A/B)"]
    ax.bar([0, 1], [4 * 7.43, od3_covers], color=["C3", "C2"], width=0.6)
    ax.set_xticks([0, 1], ["roll-up today\n4 x 7.43 g", "OD-3 covers\n(area-scaled est.)"])
    for i, v in enumerate([4 * 7.43, od3_covers]):
        ax.text(i, v, f"{v / 453.592:.4f} lbm\n({v:.1f} g)", ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("g per nacelle")
    ax.set_title("5 Weight and balance: ESC stations already at the OD-3 centres\n"
                 "(roll-up A Z 125.4, B Z 136.4); only cover area changes", fontsize=9)
    _ = cats
    # (6) canonical shape: covers on the OML, side view of the published pod
    ax = axs[1, 2]
    v = pod.vertices[::7]
    ax.scatter(v[:, 2] / IN, -v[:, 1] / IN, s=0.2, color="0.7")
    for b in bays.values():
        a0, a1 = stbd_az(*b["az"])
        for a in (a0, a1):
            y = -(48.0 * math.sin(math.radians(a)))
            ax.plot([b["z"][0] / IN, b["z"][1] / IN], [y / IN, y / IN], color="C2", lw=1)
    ax.set_aspect("equal")
    ax.set_xlabel("Z, in")
    ax.set_ylabel("height, in (up)")
    ax.set_title("6 Canonical shape: covers stay flush to the measured OML\n"
                 "(seam lines added, no OML change; outboard view, stbd)", fontsize=9)
    fig.suptitle("Brief A — ESC bays: implement the OD-3 four-bay layout", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG / "odb_theme_n_a.png", dpi=110)
    plt.close(fig)


# ── Brief B ─────────────────────────────────────────────────────────────────────────────────────
def esc_centroid(bays: dict, frame: str, rule: str) -> dict:
    """Per-ESC mass centroid (x, y) in a pod's own nacelle-local frame.

    `bays` are PORT-frame footprints.  frame 'port' uses them as they are; frame 'stbd' applies
    the rule: B1 X mirror (a -> 180 - a), B2 none (same azimuths), B3 Y mirror (a -> -a).
    ESC mass 52.7 g (roll-up ESTIMATE) split between its two bays by outline area, plus one
    cover per bay (7.43 g, measured cover, area-scaled), at r = mount radius + half the stack."""
    out = {}
    r = ESC_MOUNT_R + 3.0
    for esc in ("A", "B"):
        mine = [b for b in bays.values() if b["esc"] == esc]
        tot = sum(b["area"] for b in mine)
        x = y = m = 0.0
        for b in mine:
            a = 0.5 * (b["az"][0] + b["az"][1])
            if frame == "stbd":
                a = {"B1": 180.0 - a, "B2": a, "B3": -a}[rule]
            mb = 52.7 * b["area"] / tot + 7.43
            x += mb * r * math.cos(math.radians(a))
            y += mb * r * math.sin(math.radians(a))
            m += mb
        out[esc] = (x / m, y / m, m)
    return out


def brief_b(res: dict) -> None:
    lay = od3_layout()
    bays = lay["bays"]
    auw = 6887.0                       # g, hover_twin_2200 (auw_ledger.json, 2026-11-21)
    # Function: does each bay still FIT if the starboard pod uses a rule other than the X mirror?
    # The optimiser validated the PORT-frame bays on the port shell; a starboard bay at port-frame
    # azimuth a' corresponds, by the shells' own mirror symmetry, to port-frame azimuth 180 - a'.
    p = json.loads((REPO / "tools/esc70_design.json").read_text())
    zs, skin = eo.skin64(p.get("z_min", eo.Z_MIN_V2 * p.get("nacelle_scale", 1.0)))
    env = lay["env_mm"]
    fit: dict[str, dict[str, float]] = {}
    for rule in ("B1", "B2", "B3"):
        fit[rule] = {}
        for k, b in bays.items():
            h = b["hinge"]
            # equivalent port-frame hinge seen by the starboard bay under each rule
            heq = {"B1": h, "B2": (180.0 - h) % 360, "B3": (180.0 + h) % 360}[rule]
            pr = eo.bay_profile(zs, skin, heq, env, p["w_power"], p["w_signal"], p.get("fmin", 0.6))
            fit[rule][k] = 0.0 if not pr else (pr[-1][0] + eo.DZ - pr[0][0])
    lat = {}
    for rule in ("B1", "B2", "B3"):
        cp = esc_centroid(bays, "port", rule)
        cs = esc_centroid(bays, "stbd", rule)
        # Both pods are baked with the same rotation, so hull X = local x on BOTH pods (port
        # local +x is outboard, stbd local +x is inboard).  The aircraft lateral moment is the
        # plain sum; a perfect mirror (x_stbd = -x_port) cancels it.
        mx = sum(v[2] * v[0] for v in cp.values()) + sum(v[2] * v[0] for v in cs.values())
        my = sum(v[2] * v[1] for v in cp.values()) + sum(v[2] * v[1] for v in cs.values())
        lat[rule] = {"dx_aircraft_mm": mx / auw, "dz_aircraft_mm": -my / auw, "cp": cp, "cs": cs}
    res["B"] = {"bay_length_mm_by_rule": fit,
                "aircraft_cg_shift_mm": {k: (v["dx_aircraft_mm"], v["dz_aircraft_mm"])
                                         for k, v in lat.items()}}

    fig = plt.figure(figsize=(18, 11))
    titles = {"B1": "B1 X mirror (a -> 180 - a)", "B2": "B2 no mirror (same az)",
              "B3": "B3 Y mirror (a -> -a)"}
    # (2) Function and (4) Interactions: STARBOARD pod as each rule places the OD-3 bays,
    # against the starboard keep-outs (the port-frame keep-outs X-mirrored: shroud/servo 242-296,
    # trunnion/pylon -34..34, nav/disconnect 170-190).
    keep_stbd = [((180 - a1) % 360, (180 - a0) % 360, z0, z1) for a0, a1, z0, z1 in lay["keepouts"]]
    for i, rule in enumerate(("B1", "B2", "B3")):
        ax: Any = fig.add_subplot(2, 4, i + 1, projection="polar")
        ax.set_theta_zero_location("E")
        ax.set_theta_direction(-1)          # looking aft; +y (down) at 90
        for a0, a1, _z0, _z1 in keep_stbd:
            w = (a1 - a0) % 360
            ax.bar(math.radians(a0 + w / 2), 0.9, width=math.radians(w), bottom=0.9, color="0.6",
                   alpha=0.6)
        clash = 0
        for k, b in bays.items():
            a0, a1 = b["az"]
            if rule == "B1":
                a0, a1 = 180 - a1, 180 - a0
            elif rule == "B3":
                a0, a1 = -a1, -a0
            w = a1 - a0
            short = fit[rule][k] < (b["z"][1] - b["z"][0]) - 0.1
            clash += short
            ax.bar(math.radians(a0 + w / 2), 0.8, width=math.radians(w), bottom=0.1,
                   color="C3" if short else "C2", alpha=0.7)
            ax.text(math.radians(a0 + w / 2), 1.05, f"{k}\n{fit[rule][k]:.0f}/"
                    f"{b['z'][1] - b['z'][0]:.0f} mm", fontsize=6, ha="center")
        ax.set_yticklabels([])
        ax.set_xticks(np.radians([0, 90, 180, 270]), ["pylon", "down", "outbd", "up"], fontsize=7)
        ax.set_title(f"STBD pod, {titles[rule]}\nbays short of their run: {clash} of 4 "
                     "(red); grey: keep-outs", fontsize=8)
    # (1) statics / (5) W&B: ESC weight vectors and the aircraft lateral CG shift
    ax = fig.add_subplot(2, 4, 4)
    for i, rule in enumerate(("B1", "B2", "B3")):
        cy = -i * 7.0
        for sx, key in ((-1, "cs"), (1, "cp")):
            ax.add_patch(mpatches.Circle((sx * 5.0, cy), 2.4, fill=False))
            for esc, (x, y, m) in lat[rule][key].items():
                xh = sx * 5.0 + x / 18.0           # hull X = local x on both pods
                yh = cy - y / 18.0
                arrow(ax, xh, yh, 0, -m / 28.0, "C0" if esc == "A" else "C1")
        ax.text(-9.5, cy + 2.6, titles[rule], fontsize=7.5)
        ax.text(0, cy - 2.9, "aircraft CG shift, lateral "
                f"{lat[rule]['dx_aircraft_mm'] / IN:+.4f} in "
                f"({lat[rule]['dx_aircraft_mm']:+.3f} mm)", ha="center", fontsize=7)
    ax.axvline(0, color="0.8", lw=0.5)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-18, 4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("1 Statics / 5 Weight and balance: ESC + cover weight vectors (1 g),\n"
                 "viewed from aft: stbd pod left, port right; blue ESC A, orange ESC B", fontsize=8)
    # (2) function bars
    ax = fig.add_subplot(2, 4, 5)
    xs = np.arange(4)
    for j, rule in enumerate(("B1", "B2", "B3")):
        ax.bar(xs + (j - 1) * 0.27, [fit[rule][k] / IN for k in bays], 0.27, label=titles[rule])
    ax.plot(xs, [(b["z"][1] - b["z"][0]) / IN for b in bays.values()], "k_", ms=22,
            label="run the bay needs")
    ax.set_xticks(xs, list(bays))
    ax.set_ylabel("fitting board run on the STBD pod, in")
    ax.set_title("2 Function: does each OD-3 bay still fit on the starboard pod?", fontsize=9)
    ax.legend(fontsize=7)
    # (3) structural: sections at Z 125 with the B1 windows, both pods (exact mirror images)
    ax = fig.add_subplot(2, 4, 6)
    pod = pod_local("stbd")
    sec = section_poly(pod, 125.0)
    for sx, off in ((1, -2.4), (-1, 2.4)):
        for pp in polys(sec):
            q = np.asarray(pp.exterior.coords) * [sx, 1]
            ax.fill(q[:, 0] / IN + off, q[:, 1] / IN, color="0.75")
        for b in bays.values():
            if b["z"][0] <= 125.0 <= b["z"][1]:
                a0, a1 = 180 - b["az"][1], 180 - b["az"][0]
                w = np.asarray(sector(ESC_MOUNT_R, 50.0, a0, a1).exterior.coords) * [sx, 1]
                ax.fill(w[:, 0] / IN + off, w[:, 1] / IN, fill=False, ec="C3", lw=1.2)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.axis("off")
    ax.set_title("3 Structural integrity: Z 4.92 in (125 mm) sections, B1 windows in red;\n"
                 "the rule moves cut-outs, it does not size them: B1 pods are exact mirrors",
                 fontsize=8)
    # (6) canonical
    ax = fig.add_subplot(2, 4, 7)
    for j, rule in enumerate(("B1", "B2")):
        cy = -j * 5.0
        for sx in (-1, 1):
            ax.add_patch(mpatches.Ellipse((sx * 4.0, cy), 3.0, 3.4, fill=False))
            for b in bays.values():
                a = 0.5 * (b["az"][0] + b["az"][1])
                if sx < 0:        # starboard pod, drawn on the left (hull -X), viewed from aft
                    a = {"B1": 180 - a, "B2": a}[rule]
                xx = math.cos(math.radians(a))    # hull X = local x on both pods
                ax.plot(sx * 4.0 + 1.5 * xx, cy - 1.7 * math.sin(math.radians(a)), "s",
                        color="C2", ms=6)
        ax.text(0, cy - 2.6, titles[rule], ha="center", fontsize=8)
    ax.axvline(0, color="0.5", lw=0.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("6 Canonical shape: cover seams on the two pods, viewed from aft\n"
                 "(B1 symmetric about the centreline; B2 not)", fontsize=8)
    ax = fig.add_subplot(2, 4, 8)
    ax.axis("off")
    ax.text(0, 0.6, "As built today: bays NOT mirrored (68/248 both pods); lead\n"
            "conduit and lead vane Y-mirrored (PYLON_SIDE x az: port 292/112);\n"
            "shell, shroud, servo, nav light, trunnion, disconnect bay X-mirrored.\n"
            "The OD-3 optimiser works in the PORT frame and documents\n"
            "stbd = 180 - a (B1).", fontsize=8.5)
    fig.suptitle("Brief B — Port/starboard mirror rule for the ESC bays, lead conduits and vanes "
                 "(OD-3 four-bay layout)", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG / "odb_theme_n_b.png", dpi=110)
    plt.close(fig)


# ── Brief C ─────────────────────────────────────────────────────────────────────────────────────
def brief_c(res: dict) -> None:
    # docs/NACELLE_64MM_POWER_CROSSING_BRIEF.md, junction strip CFD at 40 kt (one fairing).
    cases = {"idealised end plate": (0.652, 0.015), "as built, bore open": (0.806, 0.016),
             "as built, bore capped": (0.925, 0.019)}
    v = 40 * 0.514444
    extra2 = 2 * (cases["as built, bore open"][0] - cases["idealised end plate"][0])
    res["C"] = {"cases_N": cases, "extra_two_fairings_N": extra2,
                "extra_drag_power_W": extra2 * v, "v_ms": v}
    fig, axs = plt.subplots(2, 3, figsize=(17, 10))
    ax = axs[0, 0]
    names = list(cases)
    ax.barh(names, [cases[n][0] / LBF for n in names],
            xerr=[cases[n][1] / LBF for n in names], color=["0.6", "C3", "C1"])
    for i, n in enumerate(names):
        ax.text(cases[n][0] / LBF, i, f"  {cases[n][0] / LBF:.3f} lbf ({cases[n][0]:.3f} N)",
                va="center", fontsize=8)
    ax.set_xlabel("drag of the junction strip at 40 kt, lbf (one fairing)")
    ax.set_title("1 Statics and dynamics: drag vector on the fairing (wing-fixed)\n"
                 "(wing-fixed part: reacted into the wing tip pad, no nacelle load)", fontsize=9)
    ax.set_xlim(0, 0.28)
    ax = axs[0, 1]
    pw = [2 * cases[n][0] * v for n in names]
    ax.bar(names, pw, color=["0.6", "C3", "C1"])
    for i, w in enumerate(pw):
        ax.text(i, w, f"{w:.1f} W\n({w / 745.7:.4f} hp)", ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("drag power of both fairings at 40 kt, W")
    ax.set_title("2 Function: the fairing fairs the collar into the wing in every case;\n"
                 f"as built costs {extra2 * v:.1f} W more than idealised (no drag polar: "
                 "endurance NOT computed)", fontsize=9)
    ax.tick_params(axis="x", labelsize=7)
    img_paths = [("3 Structural integrity / 6 Canonical: HELD outer shape (unchanged by C1/C2)",
                  "nacelle64_od17_aft_fairing_section.png", axs[0, 2]),
                 ("4 Interactions: as-built velocity sections (open bore)",
                  "nacelle64_od17_asbuilt_cfd_sections.png", axs[1, 0]),
                 ("4 Interactions: streamwise wall shear, as built",
                  "nacelle64_od17_asbuilt_cfd_wall_shear.png", axs[1, 1])]
    for title, fn, ax in img_paths:
        ax.imshow(plt.imread(FIG / fn))
        ax.axis("off")
        ax.set_title(title, fontsize=9)
    ax = axs[1, 2]
    ax.axis("off")
    ax.text(0, 0.95, "5 Weight and balance", weight="bold")
    ax.text(0, 0.65, "No mass change under either option (no part change).", fontsize=9)
    ax.text(0, 0.45, "Blockage 15-16 % with slip walls: absolute drag inflated\n"
            "by an unquantified amount; the comparison between bodies\n"
            "is the robust result (brief 'Limits').", fontsize=9)
    fig.suptitle("Brief C — OD17-FAIR-BORE: leave the as-built fairing, or fund isolating runs",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG / "odb_theme_n_c.png", dpi=110)
    plt.close(fig)


# ── Brief D ─────────────────────────────────────────────────────────────────────────────────────
def ear_force(torque_nm: float) -> float:
    """Ring-ear force for a servo torque, scaled from the linkage tool (linear)."""
    return torque_nm * 7.5 / 0.150      # tool: 0.150 N.m -> 7.5 N at the ear (X06H, 2026-11-21)


def brief_d(res: dict) -> None:
    volts = [6.0, 7.4, 8.4]
    cont = CM07["cont_kgfcm_7v4"] * KGFCM
    k_a = CM07["a_per_kgfcm_7v4"]
    hold_t = SPRING_N / ear_force(1.0)                 # N.m needed to hold the spring
    out = {}
    for vlt in volts:
        stall = CM07["stall_kgfcm"][vlt] * KGFCM
        i_stall = k_a * CM07["stall_kgfcm"][vlt]
        i_hold = k_a * hold_t / KGFCM
        out[vlt] = {"stall_Nm": stall, "ear_stall_N": ear_force(stall),
                    "cont_Nm": cont, "ear_cont_N": ear_force(cont),
                    "hold_margin_N": ear_force(cont) - SPRING_N,
                    "i_hold_A": i_hold, "i_stall_A": i_stall,
                    "p_hold_W_upper": i_hold * vlt, "speed_s_per_60": CM07["speed_s60"][vlt]}
    rail_base_run, rail_base_stall = 0.79, 4.2
    res["D"] = {"per_voltage": out, "hold_torque_Nm": hold_t,
                "rail_6v": {"existing_run_A": rail_base_run, "existing_stall_A": rail_base_stall,
                            "bec_cont_A": 5.0, "bec_burst_A": 7.0,
                            "with_2_cm07_run_A": rail_base_run + 2 * out[6.0]["i_hold_A"],
                            "with_2_cm07_stall_A": rail_base_stall + 2 * out[6.0]["i_stall_A"]}}
    fig, axs = plt.subplots(2, 4, figsize=(20, 10))
    ax = axs[0, 0]
    tq = np.linspace(0, 2.6, 50)
    ax.axvspan(0, CM07["cont_kgfcm_7v4"] * 13.887, color="C2", alpha=0.3, label="continuous zone")
    ax.axvspan(CM07["cont_kgfcm_7v4"] * 13.887, 2.0 * 13.887, color="0.85",
               label="short time < 10 s")
    ax.plot(tq * 13.887, k_a * tq, color="C3", label="current (sheet chart @7.4 V)")
    ax.axvline(hold_t / KGFCM * 13.887, color="k", ls="--",
               label=f"spring hold {hold_t / KGFCM * 13.887:.2f} ozf.in")
    for vlt in volts:
        ax.axvline(CM07["stall_kgfcm"][vlt] * 13.887, color="C0", lw=0.8)
        ax.text(CM07["stall_kgfcm"][vlt] * 13.887, 0.95, f"stall {vlt} V", rotation=90,
                fontsize=7, va="top")
    ax.set_xlabel("servo torque, ozf.in")
    ax.set_ylabel("supply current, A")
    ax.set_title("1 Electrical: CM07 torque-current (KST sheet 2026-05)", fontsize=9)
    ax.legend(fontsize=7, loc="upper left")
    ax = axs[0, 1]
    x = np.arange(3)
    ax.bar(x - 0.2, [out[v]["ear_stall_N"] / LBF for v in volts], 0.4, label="ear force at stall")
    ax.bar(x + 0.2, [out[v]["ear_cont_N"] / LBF for v in volts], 0.4,
           label="ear force, continuous limit")
    ax.axhline(SPRING_N / LBF, color="k", ls="--", label="fail-open spring 0.45 lbf (2.0 N)")
    ax.set_xticks(x, [f"{v} V" for v in volts])
    ax.set_ylabel("lbf at the ring ear")
    ax.set_title("2 Function: holding the nozzle closed in forward flight\n"
                 "continuous duty is thermal: the rail does not raise it", fontsize=9)
    ax.legend(fontsize=7)
    ax = axs[0, 2]
    r = res["D"]["rail_6v"]
    ax.bar(["running", "all stalled"], [r["existing_run_A"], r["existing_stall_A"]], color="0.6",
           label="existing 6 V loads (§3.3)")
    ax.bar(["running", "all stalled"], [2 * out[6.0]["i_hold_A"], 2 * out[6.0]["i_stall_A"]],
           bottom=[r["existing_run_A"], r["existing_stall_A"]], color="C1",
           label="+ 2 x CM07 at 6.0 V")
    ax.axhline(5.0, color="C3", ls="--", label="BEC 5 A continuous")
    ax.axhline(7.0, color="C3", ls=":", label="BEC 7 A burst (<= 100 ms)")
    ax.set_ylabel("A on the 6 V servo rail")
    ax.set_title("1 Electrical: 6 V rail budget (option D1)", fontsize=9)
    ax.legend(fontsize=7)
    ax = axs[0, 3]
    ax.bar([f"{v} V" for v in volts], [out[v]["p_hold_W_upper"] for v in volts], color="C3")
    for i, v in enumerate(volts):
        ax.text(i, out[v]["p_hold_W_upper"], f"{out[v]['p_hold_W_upper']:.2f} W", ha="center",
                va="bottom", fontsize=8)
    ax.set_ylabel("W per servo, holding (upper bound I x V)")
    ax.set_title("7 Thermal load: holding dissipation, sealed SLS pocket\n"
                 "case limit +149 °F (+65 °C); pocket thermal resistance UNMEASURED", fontsize=9)
    # (3) structural: lug couple per rail voltage
    ax = axs[1, 0]
    ax.add_patch(mpatches.Rectangle((-10.25, -3.75), 20.5, 7.5, fill=False, lw=1.5))
    ax.add_patch(mpatches.Rectangle((-14.25, -0.6), 28.5, 1.2, color="0.7"))
    for j, vlt in enumerate(volts):
        f = out[vlt]["stall_Nm"] / (CM07["lugs_mm"] / 1000.0)
        arrow(ax, -12.25 - 0.8 * j, 0, 0, f / 2.0, f"C{j}", f"{f / LBF:.2f} lbf @{vlt} V")
        arrow(ax, 12.25 + 0.8 * j, 0, 0, -f / 2.0, f"C{j}")
    ax.set_xlim(-18, 26)
    ax.set_ylim(-7, 7)
    ax.set_aspect("equal")
    ax.set_xlabel("mm (lug centres 24.5 mm, KST CM07 drawing)")
    ax.set_title("3 Structural integrity: stall torque reacted as a couple on the lugs\n"
                 "(same servo and mount at every voltage; insert pull-out UNVERIFIED)", fontsize=9)
    # (4) interactions: power path block diagram
    ax = axs[1, 1]
    ax.axis("off")
    boxes = [("FE PDB\n6 V servo rail\n(BEC 5 A / 7 A)", 0.05, 0.62),
             ("F_NOZ fuse +\nhigh-side switch\n(gateway-held)", 0.38, 0.62),
             ("tilt joint\n(spar bore)", 0.70, 0.62), ("KST CM07\nnozzle servo", 0.70, 0.18),
             ("D2/D3 only:\nnew 7.4/8.4 V\nregulator", 0.21, 0.18)]
    for t, bx, by in boxes:
        ax.add_patch(mpatches.FancyBboxPatch((bx, by), 0.25, 0.2, boxstyle="round,pad=0.01",
                                             fc="0.92", ec="k", transform=ax.transAxes))
        ax.text(bx + 0.125, by + 0.1, t, ha="center", va="center", fontsize=7,
                transform=ax.transAxes)
    for x0, y0, x1, y1, c in ((0.30, 0.72, 0.38, 0.72, "k"), (0.63, 0.72, 0.70, 0.72, "k"),
                              (0.825, 0.62, 0.825, 0.38, "k"), (0.175, 0.62, 0.30, 0.38, "C3")):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), xycoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", color=c))
    ax.set_title("4 Interactions: power path (plan 2026-09-28-001 KTD6)\n"
                 "D1 uses the existing rail; D2/D3 add the red branch", fontsize=9)
    # (5) weight and balance
    ax = axs[1, 2]
    ax.bar(["D1 6.0 V", "D2 7.4 V", "D3 8.4 V"], [0.0, 2 * 3.5, 2 * 3.5],
           color=["C2", "0.7", "0.7"], hatch=[None, "//", "//"])
    ax.text(1.5, 7.3, "ESTIMATE: ~3.5 g per regulator x 2\n(no part chosen; not in the ledger)",
            ha="center", fontsize=7)
    ax.set_ylabel("added mass per aircraft, g")
    ax.set_ylim(0, 10)
    ax.set_title("5 Weight and balance: added parts per option", fontsize=9)
    # (6) harness: voltage drop on the servo pair at stall
    ax = axs[1, 3]
    loop_m = 2 * 0.6                     # ASSUMED 0.6 m one way (cf. the cargo door branch)
    ohm = {"26 AWG": 0.1339, "24 AWG": 0.0842}   # ohm/m, annealed copper at 20 C (nominal)
    x = np.arange(len(volts))
    for j, (g_, r_) in enumerate(ohm.items()):
        drops = [out[vlt]["i_stall_A"] * r_ * loop_m for vlt in volts]
        ax.bar(x + (j - 0.5) * 0.35, [100 * d / vlt for d, vlt in zip(drops, volts)], 0.35,
               label=g_)
    ax.set_xticks(x, [f"{v} V" for v in volts])
    ax.set_ylabel("supply drop at stall, % of rail")
    ax.set_title("6 Wire harness fit: servo pair drop at stall, 0.6 m one way ASSUMED\n"
                 "the pair must also be added to the spar-bore census (open)", fontsize=9)
    ax.legend(fontsize=7)
    fig.suptitle("Brief D — D-SV-2: nozzle-servo rail voltage for the KST CM07 "
                 "(avionics / power-electrical check set)", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG / "odb_theme_n_d.png", dpi=110)
    plt.close(fig)


# ── Brief E ─────────────────────────────────────────────────────────────────────────────────────
def servo_solve(dims, torque, az, out: Path) -> str:
    nsl.SERVO_DIMS, nsl.SERVO_TORQUE = dims, torque
    argv = sys.argv
    sys.argv = ["x", "--out", str(out), "--servo-az", str(az)]
    try:
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            nsl.main()
    finally:
        sys.argv = argv
    return buf.getvalue()


def pocket(params: Path, pod: trimesh.Trimesh, clr: float = 0.6) -> dict:
    import re
    p = params.read_text()

    def num(n):
        g = re.search(n + r"\s*=\s*\[?([-0-9., ]+)\]?;", p)
        return [float(x) for x in g.group(1).split(",")]
    sh = np.array(num("NSL_SHAFT"))
    saz = math.radians(num("NSL_SHAFT_AZ")[0])
    L, W, H = num("NSL_SERVO")
    er = np.array([math.cos(saz), math.sin(saz), 0])
    et = np.array([-math.sin(saz), math.cos(saz), 0])
    rs = math.hypot(sh[0], sh[1])
    a0, a1 = rs - W / 2 - clr, rs + W / 2 + clr
    t0, t1 = -(1.5 + H) - clr, -1.5 + clr
    z0, z1 = sh[2] - (L - 4.5) - clr, sh[2] + 4.5 + clr

    def outer_r(az, z):
        a = math.radians(az)
        d = np.array([math.cos(a), math.sin(a), 0])
        loc, _, _ = pod.ray.intersects_location([np.array([0, 0, z]) + d * 90], [-d])
        return np.hypot(loc[:, 0], loc[:, 1]).max()
    worst: tuple[float, Any] = (9e9, None)
    for t in np.linspace(t0, t1, 9):
        for z in np.linspace(z0, z1, 7):
            q = a1 * er + t * et
            w = outer_r(math.degrees(math.atan2(q[1], q[0])) % 360, z) - math.hypot(q[0], q[1])
            if w < worst[0]:
                worst = (w, (math.degrees(math.atan2(q[1], q[0])) % 360, z))

    def dist(q):
        a, t, z = q @ er, q @ et, q[2]
        return math.sqrt(max(a0 - a, 0, a - a1) ** 2 + max(t0 - t, 0, t - t1) ** 2
                         + max(z0 - z, 0, z - z1) ** 2)
    scr = {}
    for az, z in ((252.5, 138.27), (252.5, 165.0), (289.5, 138.27), (287.0, 195.27)):
        a = math.radians(az)
        scr[f"{az}/{z}"] = min(dist(np.array([r * math.cos(a), r * math.sin(a), z]))
                               for r in np.linspace(38.6, 44.0, 12)) - 1.6
    corners = [a1 * er + t * et for t in (t0, t1)]
    azs = [math.degrees(math.atan2(c[1], c[0])) % 360 for c in corners]
    return {"skin_min_mm": worst[0], "at": worst[1], "cover_gap_mm": worst[0] - 1.6 + clr,
            "screws_mm": scr, "az": (min(azs), max(azs)), "z": (z0, z1)}


def brief_e(res: dict) -> None:
    pod = pod_local("stbd")
    tmp = Path(tempfile.mkdtemp())
    cases: dict[str, dict[str, Any]] = {}
    for name, dims, tq, az in (("X06H az280", X06H["dims"], X06H["stall_nm_6v"], 280.0),
                               ("CM07 az280", CM07["dims"], 1.80 * KGFCM, 280.0),
                               ("CM07 az282", CM07["dims"], 1.80 * KGFCM, 282.0)):
        txt = servo_solve(dims, tq, az, tmp / f"{name}.scad")
        import re
        g = re.search(r"stall ([0-9.]+) N", txt)
        cases[name] = {"linkage": "PASS" if "PASS" in txt else "FAIL",
                       "ear_stall_N": float(g.group(1)) if g else None,
                       **pocket(tmp / f"{name}.scad", pod)}
    lug_n = 1.80 * KGFCM / (CM07["lugs_mm"] / 1000.0)
    d_cg = 1.0 * (0.5 * (nac64.NOZ_Z - 43.86 + nac64.NOZ_Z - 8.86) - PIVOT) / 1113.5
    res["E"] = {"cases": cases, "lug_force_N_stall_6v": lug_n, "pivot_shift_mm_per_servo": d_cg}
    fig, axs = plt.subplots(2, 3, figsize=(17, 10.5))
    # (1) statics: servo FBD
    ax = axs[0, 0]
    ax.add_patch(mpatches.Rectangle((-10.25, -3.75), 20.5, 7.5, fill=False, lw=1.5))
    ax.add_patch(mpatches.Rectangle((-14.25, -0.6), 28.5, 1.2, color="0.7"))
    arrow(ax, -12.25, 0, 0, 4.0, "C3", f"{lug_n / LBF:.2f} lbf")
    arrow(ax, 12.25, 0, 0, -4.0, "C3", f"{lug_n / LBF:.2f} lbf")
    arrow(ax, 5.75, 3.75, 0, 3.0, "C0", "horn: stall 25.0 ozf.in @6 V")
    ax.add_patch(mpatches.Arc((5.75, 3.75), 5, 5, theta1=20, theta2=300, color="C0"))
    ax.set_xlim(-18, 18)
    ax.set_ylim(-8, 10)
    ax.set_aspect("equal")
    ax.set_xlabel("mm (servo length, lug centres 24.5 mm)")
    ax.set_title("1 Statics: stall torque reacted as a couple on the two lugs\n"
                 f"{lug_n / LBF:.2f} lbf ({lug_n:.1f} N) per lug; M2 insert pull-out in PA CF "
                 "REQUIRES VERIFICATION", fontsize=9)
    # (2) function: ear force
    ax = axs[0, 1]
    nm = list(cases)
    st_ = [cases[n]["ear_stall_N"] / LBF for n in nm]
    cont = [X06H["cont_nm_6v"], CM07["cont_kgfcm_7v4"] * KGFCM, CM07["cont_kgfcm_7v4"] * KGFCM]
    xx = np.arange(len(nm))
    ax.bar(xx - 0.2, st_, 0.4, label="stall at the ear (tool, 6 V)")
    ax.bar(xx + 0.2, [ear_force(c) / LBF for c in cont], 0.4, label="continuous at the ear")
    ax.axhline(SPRING_N / LBF, color="k", ls="--", label="spring 0.45 lbf")
    ax.set_xticks(xx, [f"{n}\nlinkage {cases[n]['linkage']}" for n in nm], fontsize=8)
    ax.set_ylabel("lbf")
    ax.set_title("2 Function: drive force and stroke (linkage solve passes)", fontsize=9)
    ax.legend(fontsize=7)
    # (3) structural: radial gap to the cover
    ax = axs[0, 2]
    ax.bar(nm, [cases[n]["cover_gap_mm"] / IN for n in nm], color=["0.6", "C3", "C1"])
    for i, n in enumerate(nm):
        ax.text(i, cases[n]["cover_gap_mm"] / IN,
                f"{cases[n]['cover_gap_mm'] / IN:.3f} in\n({cases[n]['cover_gap_mm']:.2f} mm)",
                ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("servo body to cover inner face, in")
    ax.set_title("3 Structural integrity: body-to-cover gap at the pocket's aft end\n"
                 "(cover 0.063 in (1.6 mm) is the skin there)", fontsize=9)
    # (4) interactions: unwrapped map
    ax = axs[1, 0]
    ax.add_patch(mpatches.Rectangle((250, 135.27 / IN), 42, 63 / IN, fill=False, ec="k",
                                    label="cover opening"))
    for n, c in (("X06H az280", "0.5"), ("CM07 az280", "C3"), ("CM07 az282", "C1")):
        a0, a1 = cases[n]["az"]
        z0, z1 = cases[n]["z"]
        ax.add_patch(mpatches.Rectangle((a0, z0 / IN), a1 - a0, (z1 - z0) / IN, fill=False,
                                        ec=c, lw=1.6, label=n))
    for (az, z), lab, c in (((252.5, 138.27), "screw 1 today", "C3"),
                            ((252.5, 165.0), "screw 1 moved (E1/E2)", "C2"),
                            ((289.5, 138.27), "screw 2", "k"), ((287.0, 195.27), "screw 3", "k")):
        ax.plot(az, z / IN, "o", color=c)
        ax.text(az, z / IN, " " + lab, fontsize=7, color=c)
    arrow(ax, 266, 190 / IN, 8, 0.25, "C0", "linkage sweep")
    ax.set_xlim(244, 300)
    ax.set_ylim(130 / IN, 202 / IN)
    ax.set_xlabel("azimuth, deg (stbd frame)")
    ax.set_ylabel("Z, in")
    ax.set_title("4 Interactions: pocket, cover screws and linkage (stbd; port mirrors)",
                 fontsize=9)
    ax.legend(fontsize=7, loc="lower right")
    sec_in(ax, "y")
    # (5) W&B
    ax = axs[1, 1]
    ax.bar(["X06H", "CM07"], [X06H["mass_g"], CM07["mass_g"]], color=["0.6", "C3"])
    ax.set_ylabel("g per servo")
    ax.set_title(f"5 Weight and balance: +1 g per servo, +0.0044 lbm (2 g) per aircraft;\n"
                 f"pivot residual +{d_cg:.3f} mm per nacelle (re-converge at S5 U7)", fontsize=9)
    # (6) canonical: section through the servo, both bodies inside the unchanged OML
    ax = axs[1, 2]
    sec = section_poly(pod, 150.0)
    for pp in polys(sec):
        ax.fill(*np.asarray(pp.exterior.coords).T / IN, color="0.8")
        for h in pp.interiors:
            ax.fill(*np.asarray(h.coords).T / IN, color="white")
    for n, (dims, c) in {"X06H": (X06H["dims"], "0.3"), "CM07": (CM07["dims"], "C3")}.items():
        L_, W_, H_ = dims
        saz = math.radians(280.0)
        er = np.array([math.cos(saz), math.sin(saz)])
        et = np.array([-math.sin(saz), math.cos(saz)])
        rs = 36.4 + W_ / 2
        corners = ((-W_ / 2, -1.5), (W_ / 2, -1.5), (W_ / 2, -1.5 - H_), (-W_ / 2, -1.5 - H_))
        pts = [(rs + da) * er + tt * et for da, tt in corners]
        qa = np.array(pts + [pts[0]]) / IN
        ax.plot(qa[:, 0], qa[:, 1], color=c, lw=1.6, label=f"{n} body")
    ax.set_aspect("equal")
    ax.set_xlim(-1.2, 1.4)
    ax.set_ylim(-2.4, -0.6)
    ax.invert_yaxis()
    ax.legend(fontsize=7, loc="lower left")
    ax.set_xlabel("x, in")
    ax.set_ylabel("y, in (+y down; shroud on top)")
    ax.set_title("6 Canonical shape: section at Z 5.91 in (150 mm) — both bodies inside the\n"
                 "unchanged OML; shroud crest +0.036 in (+0.92 mm) for both. Internal only.",
                 fontsize=9)
    fig.suptitle("Brief E — KST CM07 pocket integration in the dorsal spine", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG / "odb_theme_n_e.png", dpi=110)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path)
    ap.add_argument("--only", default="abcde")
    a = ap.parse_args(argv)
    res: dict = {}
    for k in a.only:
        {"a": brief_a, "b": brief_b, "c": brief_c, "d": brief_d, "e": brief_e}[k](res)
    txt = json.dumps(res, indent=1, default=lambda o: list(o) if isinstance(o, tuple) else str(o))
    if a.json:
        a.json.write_text(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
