#!/usr/bin/env python3
"""
esc80_cooptimize.py — score one 80 A ESC + 64 mm nacelle bay design point.

WHY THIS EXISTS  (WBS NAC-64-ESC-80A, owner 2026-10-03)
-------------------------------------------------------
The owner asked for two 6S / 80 A Open-Secure-ESC builds that sit against the
64 mm thrust tube: variant A with every wire leaving one end, and variant B with
the phase leads leaving the end opposite the pack and signal leads.  Both the
bay geometry and the ESC topology may be restacked, so neither side is fixed and
the two are co-optimised.  This file is the MEASUREMENT HARNESS for that loop
(ce-optimize): it reads a design point (JSON) and prints one JSON object of
metrics.  It is immutable during an optimisation run; only the design point
changes.

WHAT IT MEASURES
----------------
1. Bay fit, by REAL ray-cast.  The canonical 50 mm shell is scaled exactly as
   `nacelle_pod_64mm_tandem.scad` scales it (radial P64_K 1.21, axial P64_A
   1.13) and the hinged-panel corner test of `nacelle_esc_bay_fit.py` is reused
   unchanged, so the bay length is measured against the skin, not assumed.
2. Board length the ESC NEEDS, from courtyard areas measured on the as-placed
   50 A faceted board (Open-Secure-ESC builds/6s/50A/CAN_485_faraday_faceted,
   read with the kicad skill's analyze_pcb.py on 2026-10-03) — see AREA_50A —
   re-scaled for 80 A (more FETs, more shunts, larger terminals) and divided by
   a declared packing efficiency.
3. Channel temperature at 80 A, with the aspirated-lane convection model of
   `nacelle_esc_thermal.py` re-run on the 64 mm duct and the actual board area.
4. Pivot/CG shift of the rotating assembly, from the 929 g / Z 109.7 mm roll-up
   recorded in docs/NACELLE_64MM_VERIFICATION.md §5.
5. Creepage: the [OSE 9] Table 6 7.5 mm barrier, placed laterally (costs board
   WIDTH, 31.86 mm floor) or axially (costs board LENGTH).

WHAT IT DOES NOT DO
-------------------
It does not place footprints.  A design point that scores well here must still
be placed and routed in KiCad (facet_placement.py, then manual/autoroute) before
anything is claimed.  Every ESTIMATE / VERIFY constant below is labelled; none
may be quoted as a verified value.

Sources (Serenity-UAV REFERENCES.md REF-IDs; bracketed numbers are the same
documents' tags in Open-Secure-ESC REFERENCES.md, inherited via REF-ESC-001):
  REF-SEMI-001 / OSE [49] Toshiba TPHR8504PL datasheet rev 5.0.A — R_DS(on) 0.85 mOhm max at
       V_GS 10 V (§6); Rth(ch-c) 0.88 K/W (§5); SOP Advance(N) body
       4.90 x 6.10 mm, height 1.0 +/-0.1 mm, 0.111 g (p. 9); R_DS(on)
       temperature ratio read from Fig. 8.9 (graph read, ~1.65 at 125 C/25 C).
  REF-ESC-001 / OSE [9]  ADM2582E/ADM2587E Table 6 — 7.5 mm creepage
       (via Open-Secure-ESC docs/tools/isolation_envelope.py).
  REF-NASA-001 NASA-STD-8739.4A Chg 3 §7.2.19 Table 7-1 — harness bend radius.
  REF-EDF-003 — QF2822 thrust 20.9 N per fan (NACELLE_64MM_VERIFICATION.md §1).

Usage:
    /usr/bin/python3 tools/esc80_cooptimize.py tools/esc80_design.json

Author: Steve Griffing, PE(CSE), CISSP-ISSEP (Stab-Rabbit-coding)
Harness written by Claude (Claude Opus 5.5, Anthropic) under the author's
direction, 2026-10-03, per AGENTS.md attribution rules.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import contextlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nacelle_esc_bay_fit as bay      # noqa: E402  sibling tool, ray-cast + corner test
import nacelle_esc_thermal as thermal  # noqa: E402  sibling tool, lane convection

REPO = Path(__file__).resolve().parent.parent
# Per-user cache, 0700 (a predictable shared /tmp path could be pre-seeded by
# another user; np.load keeps allow_pickle=False regardless).
CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "serenity-esc80"
CACHE = CACHE_DIR / "esc80_skin64_cache.npz"

# ── 64 mm pod (nacelle_pod_64mm_tandem.scad) ─────────────────────────────────
P64_K = 1.21                 # radial scale of the canonical shell
P64_A = 1.13                 # axial stretch of the canonical shell
MOUNT_R = 37.2               # [mm] ESC_MOUNT_R — board inner face floor
DUCT_R_64 = 32.0             # [mm] P64_BORE_R
Z_MIN = 70.0 * P64_A         # bay limits scaled with the shell (50 mm tool 70..160)
Z_MAX = 160.0 * P64_A
DZ = 2.0

# ── Rotating assembly (NACELLE_64MM_VERIFICATION.md §5) ──────────────────────
ASSY_G = 929.0               # [g] per nacelle, incl. 2 x 42 g ASSUMED ESCs
CG_Z = 109.7                 # [mm] = PIVOT_Z
ESC_BASE_G = 42.0            # [g] each, the ASSUMED row being replaced
ESC_BASE_Z = 95.0 * P64_A    # [mm] the row's station (107.35)
HOVER_SLACK = 13.7 - 12.7    # [mm] hover clearance minus the 0.5 in floor
COVER_G_PER_MM = 4 * 6.99 / 2 * P64_K / 2 / 42.0   # [g/mm/bay] scaled cover row

# ── 50 A faceted board, as placed (courtyard mm2) ────────────────────────────
AREA_50A = {
    "fet_each": 252.6 / 6,       # Q1-Q6 TPHR8504PL courtyard
    "shunt_each": 88.7 / 3,      # R1-R3 2512
    "term_total": 309.3,         # J4A-C phase pads 5x10 + J5A/B 6 mm2 cups
    "power_other": 134.6 + 481.9,  # DRV8353S, INA240 x3, SH1, caps (F + B)
    "logic_other": 700.6,        # MCU, SE, isolated CAN + RS-485, passives
}
PARTS_50A = {"power_other": 13, "logic_other": 32, "term": 5}
ETA_50A_P = (252.6 + 88.7 + 309.3 + 134.6) / (23.0 * 89.51)   # 0.38, F face

# ── FET, [49] ────────────────────────────────────────────────────────────────
RDS_MAX_25 = 0.85e-3         # [ohm] V_GS 10 V
RDS_HOT_RATIO = 1.65         # Fig. 8.9 graph read, 125 C / 25 C — VERIFY on bench
RTH_CH_C = 0.88              # [K/W]
FET_G = 0.111                # [g]
T_CH_DESIGN = 125.0          # [C] declared judgement in nacelle_esc_thermal.py
T_AMB = 25.0                 # [C] same design ambient as nacelle_esc_thermal.py

# ── Creepage, [9] Table 6 via isolation_envelope.py ──────────────────────────
CREEP = 7.5                  # [mm]
CREEP_INSET = 1.43           # [mm] pour inset each side of the barrier
LATERAL_FLOOR = 31.86        # [mm] board width with the barrier across it

# ── ESTIMATES (labelled; diagnostics only, never gates) ──────────────────────
FR4_G_PER_MM3 = 1.85e-3      # ESTIMATE — typical FR-4 density, no repo source
CU_G_PER_MM3 = 8.96e-3       # copper density
OZ_MM = 0.0347               # 1 oz copper thickness
OTHER_G_PER_MM2 = 0.012      # ESTIMATE — non-FET part mass per courtyard mm2


# ── Sibling-module overrides ─────────────────────────────────────────────────
# nacelle_esc_bay_fit / nacelle_esc_thermal are written for the 50 mm pod and
# read module-level constants.  This tool re-points those constants at the
# 64 mm pod.  Every name it may touch is listed here, and overrides_64mm()
# snapshots and restores them, so nothing leaks to another caller in the same
# process (review 2026-10-03, maintainability P1).
_BAY_NAMES = ("W_POWER", "W_SIGNAL", "duct_r", "DUCT_WALL", "Z_MIN", "SKIN_WALL", "EXCLUDE")
_THERMAL_NAMES = ("DUCT_AREA", "NACELLE_THRUST_N", "BAY_WIDTH", "ESC_LEN")


@contextlib.contextmanager
def overrides_64mm(cover_t=2.5):
    """Apply the 64 mm pod constants to the sibling modules; restore on exit."""
    saved = ([(bay, n, getattr(bay, n)) for n in _BAY_NAMES]
             + [(thermal, n, getattr(thermal, n)) for n in _THERMAL_NAMES])
    try:
        bay.duct_r = lambda z: DUCT_R_64       # noqa: E731  64 mm bore everywhere
        bay.DUCT_WALL = MOUNT_R - DUCT_R_64    # so the d_in floor == ESC_MOUNT_R
        bay.Z_MIN = Z_MIN
        # access cover + running clearance (bay tool SKIN_WALL = cover 2.5 + 0.4)
        bay.SKIN_WALL = cover_t + 0.4
        thermal.DUCT_AREA = math.pi * (DUCT_R_64 / 1000.0) ** 2
        thermal.NACELLE_THRUST_N = 2 * 20.9 * 0.90
        yield
    finally:
        for mod, name, val in saved:
            setattr(mod, name, val)


def skin64(z_min=None):
    """Outer-skin radius on a (Z, az) grid for the 64 mm pod, cached."""
    z_lo = Z_MIN if z_min is None else z_min
    CACHE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    # key the cache on everything that shapes the grid, not just z_min
    key = f"K{P64_K}_A{P64_A}_dz{DZ}_n{bay.N_AZ_SAMPLE}_z{z_lo:.2f}_{Z_MAX:.2f}"
    cache = CACHE_DIR / f"esc80_skin64_{key}.npz"
    if cache.exists():
        d = np.load(cache, allow_pickle=False)
        return d["zs"], d["skin"]
    import trimesh
    mesh = trimesh.load_mesh(REPO / "airframe/stls/nacelles" / bay.SHELL["PORT"],
                             force="mesh")
    mesh.apply_translation([-bay.BORE_CX["PORT"], bay.BORE_CY, 0.0])
    mesh.apply_scale([P64_K, P64_K, P64_A])
    zs = np.arange(z_lo, Z_MAX + DZ / 2, DZ)
    az = np.arange(bay.N_AZ_SAMPLE) * 360.0 / bay.N_AZ_SAMPLE
    org, dirs = [], []
    for z in zs:
        for a in np.radians(az):
            org.append([250.0 * math.cos(a), 250.0 * math.sin(a), z])
            dirs.append([-math.cos(a), -math.sin(a), 0.0])
    loc, ray, _ = mesh.ray.intersects_location(np.asarray(org), np.asarray(dirs),
                                               multiple_hits=True)
    out = np.zeros(len(org))
    np.maximum.at(out, ray, np.hypot(loc[:, 0], loc[:, 1]))
    if (out == 0).any():
        raise ValueError(f"{(out == 0).sum()} rays missed the scaled shell")
    skin = out.reshape(len(zs), bay.N_AZ_SAMPLE)
    np.savez(cache, zs=zs, skin=skin)
    return zs, skin


def bays(zs, skin, w_pow, w_sig, envelope):
    """Longest run per hinge azimuth with the 64 mm floors; returns sorted rows."""
    # panel widths are per-call inputs of the bay tool (inside overrides_64mm)
    bay.W_POWER, bay.W_SIGNAL = w_pow, w_sig
    rows = []
    for phi in np.arange(0.0, 360.0, 2.0):
        best = None
        d = MOUNT_R
        while d < MOUNT_R + 6.0:
            if not bay.excluded(float(phi), d):
                ok = [bay.hinge_fits(skin, k, float(z), float(phi), d, envelope)
                      for k, z in enumerate(zs)]
                run = cur = s = st = en = 0
                for k, g in enumerate(ok):
                    if g:
                        if cur == 0:
                            s = k
                        cur += 1
                        if cur > run:
                            run, st, en = cur, s, k
                    else:
                        cur = 0
                if run and (best is None or run > best[0]):
                    best = (run, float(zs[st]), float(zs[en]) + DZ, d)
            d += 0.25
        if best:
            rows.append((float(phi), best[2] - best[1], best[1], best[2], best[3]))
    rows.sort(key=lambda r: -r[1])
    return rows


def pick_bays(rows, count, w_pow, w_sig, rib_deg=6.0):
    """Greedy: the `count` longest bays whose angular footprints do not overlap.

    Footprint of a hinged pair at hinge azimuth phi, inner face d:
    phi - 2*a_sig .. phi + 2*a_pow (nacelle_esc_bay_fit.py), plus a printed
    hoop rib of `rib_deg` between neighbours (ESTIMATE, 3 mm at R 37).
    """
    chosen = []
    for r in rows:
        d = r[4]
        a_p = math.degrees(math.atan2(w_pow / 2, d))
        a_s = math.degrees(math.atan2(w_sig / 2, d))
        lo, hi = r[0] - 2 * a_s - rib_deg / 2, r[0] + 2 * a_p + rib_deg / 2
        clash = False
        for c in chosen:
            for turn in (-360.0, 0.0, 360.0):
                if lo < c[1] + turn and hi > c[0] + turn:
                    clash = True
        if not clash:
            chosen.append((lo, hi, r))
        if len(chosen) == count:
            break
    return [c[2] for c in chosen]


def length_needed(p):
    """Board length each panel needs, mm, and part count."""
    n = p["fet_per_leg"]
    term = AREA_50A["term_total"] * p["term_area_scale"]
    power = (6 * n * AREA_50A["fet_each"]
             + 3 * p["shunt_per_phase"] * AREA_50A["shunt_each"]
             + term + AREA_50A["power_other"] + p.get("power_area_delta", 0.0))
    # package swaps: courtyard mm2 change vs the as-placed 50 A board, each
    # delta documented with its datasheet in the design point's "_swaps" note
    logic = AREA_50A["logic_other"] + p.get("logic_area_delta", 0.0)
    eta = p["packing_eta"]
    nb = p.get("bays_per_esc", 1)
    # with two bays per ESC each bay is one more hinged power + logic pair, so
    # the panel width available to each functional group doubles.
    l_pow = power / (eta * p["power_faces"] * p["w_power"] * nb)
    l_log = logic / (eta * p["logic_faces"] * p["w_signal"] * nb)
    iso = p["isolation"]
    if iso == "axial_two":            # two isolated domains in tandem
        l_log += 2 * (CREEP + 2 * CREEP_INSET)
    elif iso == "axial_shared":       # one shared isolated domain at the end
        l_log += CREEP + 2 * CREEP_INSET
    parts = (6 * n + 3 * p["shunt_per_phase"] + PARTS_50A["term"]
             + PARTS_50A["power_other"] + PARTS_50A["logic_other"])
    return l_pow, l_log, power, logic, parts


def egress_ok(p):
    """Terminal row widths for both owner variants, on the power panel."""
    s = math.sqrt(p["term_area_scale"])
    phase_w = 3 * 5.5 * s             # J4 pads 5.5 mm courtyard each
    pack_w = 2 * 8.5 * s              # J5 cups 8.5 mm courtyard each
    sig_w = 4.0                        # bus/signal pad row, ESTIMATE
    a = phase_w <= p["w_power"] and pack_w <= p["w_power"]        # opposite faces
    b = phase_w <= p["w_power"] and pack_w + sig_w <= p["w_power"] + p["w_signal"]
    return a, b


def thermal_tch(p, board_len, area_mm2=None):
    """Channel temperature at 80 A, aspirated lane, 64 mm duct."""
    n = p["fet_per_leg"]
    i = p["current_a"]
    r_hot = RDS_MAX_25 * RDS_HOT_RATIO
    p_fet_each = (i / n) ** 2 * r_hot             # OSE convention: full current
    p_fets = 6 * n * p_fet_each                    # (conservative, 50 A doc S7)
    k_i = (i / thermal.I_REF) ** 2
    p_pour = thermal.P_POUR_50A * k_i * (2.0 / p["copper_oz"]) * p["pour_squares_rel"]
    p_gap = thermal.P_GAP_50A * k_i * (2.0 / p["copper_oz"])
    p_tot = p_fets + p_pour + p_gap
    # duct area / thrust are set by overrides_64mm(); lane geometry is per call
    thermal.BAY_WIDTH = (p["w_power"] + p["w_signal"]) / 1000.0
    thermal.ESC_LEN = board_len / 1000.0
    st = thermal.duct_stations()
    throat = p["n_bleed"] * math.pi * (p["d_bleed"] / 2000.0) ** 2
    _, _, _, h, mdot = thermal.channel_flow(-st["p2_gauge"], p["flow_lane"] / 1000.0,
                                            throat)
    # model 2 passes the skin-FITTED board area; model 1 keeps nominal widths
    area = (area_mm2 if area_mm2 is not None else
            board_len * (p["w_power"] + p["w_signal"]) * p.get("bays_per_esc", 1)) * 1e-6
    r_conv = 1.0 / (h * 2 * area)
    dt_air = p_tot / (p.get("bays_per_esc", 1) * mdot * thermal.CP_AIR)
    tch = T_AMB + dt_air + p_tot * r_conv + p_fet_each * RTH_CH_C
    return tch, p_tot, p_fet_each, h, r_conv, dt_air


def esc_mass(p, board_len, power_a, logic_a):
    area = board_len * (p["w_power"] + p["w_signal"]) * p.get("bays_per_esc", 1)
    fr4 = area * p["pcb_t"] * FR4_G_PER_MM3
    cu = area * 4 * p["copper_oz"] * OZ_MM * CU_G_PER_MM3 * 0.8
    fets = 6 * p["fet_per_leg"] * FET_G
    other = (power_a + logic_a - 6 * p["fet_per_leg"] * AREA_50A["fet_each"]) \
        * OTHER_G_PER_MM2
    return fr4 + cu + fets + other


def cg_roll_up(m_esc, z_mean, cover_g):
    """Rotating-assembly mass and CG shift when the two 42 g ASSUMED ESC rows
    and the scaled 50 mm cover row are replaced by `m_esc` each (at `z_mean`)
    plus `cover_g` of covers.  Shared by both models."""
    base_cover = 4 * 6.99 / 2 * P64_K
    d_mz = 2 * m_esc * z_mean + cover_g * z_mean \
        - 2 * ESC_BASE_G * ESC_BASE_Z - base_cover * ESC_BASE_Z
    m_new = ASSY_G - 2 * ESC_BASE_G + 2 * m_esc - base_cover + cover_g
    return m_new, (CG_Z * ASSY_G + d_mz) / m_new - CG_Z


def main() -> int:
    p = json.loads(Path(sys.argv[1]).read_text())
    l_pow, l_log, power_a, logic_a, parts = length_needed(p)
    l_req = max(l_pow, l_log)
    stack = p["pcb_t"] + p["h_outer"] + p["h_inner"] + p["mount_gap"]
    zs, skin = skin64()
    rows = bays(zs, skin, p["w_power"], p["w_signal"], stack + p["flow_lane"])
    nb = p.get("bays_per_esc", 1)
    sel = pick_bays(rows, 2 * nb, p["w_power"], p["w_signal"])
    l_avail = min(b[1] for b in sel) if len(sel) == 2 * nb else 0.0
    margin = l_avail - l_req
    tch, p_tot, p_fet, h, r_conv, dt_air = thermal_tch(p, l_req)
    m_esc = esc_mass(p, l_req, power_a, logic_a)
    # every chosen bay is trimmed to l_req, centred in its free run
    z_c = [(b[2] + b[3]) / 2 for b in sel] if sel else [ESC_BASE_Z] * 2
    z_mean = sum(z_c) / len(z_c)
    cover = COVER_G_PER_MM * l_req * len(z_c)
    m_new, d_cg = cg_roll_up(m_esc, z_mean, cover)
    ega, egb = egress_ok(p)
    width_iso_ok = (p["isolation"] != "lateral"
                    or max(p["w_power"], p["w_signal"]) >= LATERAL_FLOOR)
    out = {
        "fit_margin_mm": round(margin, 2),
        "l_required_mm": round(l_req, 2),
        "l_power_mm": round(l_pow, 2),
        "l_logic_mm": round(l_log, 2),
        "l_bay_available_mm": round(l_avail, 2),
        "bays_per_esc": nb,
        "bays": [[round(x, 2) for x in b] for b in sel],
        "stack_mm": round(stack, 2),
        "cover_t_mm": p.get("cover_t", 2.5),
        "tch_c": round(tch, 1),
        "p_total_w": round(p_tot, 2),
        "p_fet_each_w": round(p_fet, 3),
        "h_lane_w_m2k": round(h, 0),
        "dt_air_k": round(dt_air, 1),
        "esc_mass_g_estimate": round(m_esc, 1),
        "assy_mass_g": round(m_new, 1),
        "d_cg_mm": round(d_cg, 2),
        "hover_slack_after_mm": round(HOVER_SLACK + d_cg, 2),
        "part_count": parts,
        "egress_a_ok": ega,
        "egress_b_ok": egb,
        "creepage_ok": width_iso_ok,
        "packing_eta": p["packing_eta"],
        "eta_50a_reference": round(ETA_50A_P, 3),
    }
    print(json.dumps(out, indent=1))
    return 0


# ═════════════════════════════════════════════════════════════════════════════
# MODEL 2  (owner direction 2026-10-03, after the first loop stopped 6.5 mm short)
#   * board OUTLINE follows the skin: each 2 mm ring gets the widest panel that
#     clears the skin, capped at the nominal width (a tapered/notched board end
#     instead of a rectangle) — "lengthen the bay" without entering any other
#     system's space, because the diagnosis showed both bay ends are SKIN-limited
#   * packing 0.75 on BOTH faces, with high-current pour runs and thermal-via
#     keep-outs counted as occupied area (owner)
#   * wiring-harness loop space reserved at every wire-exit end of the bay
#   * optional in-layout cooling lane and two bays per ESC
# Selected by "model": 2 in the design point; model 1 above is unchanged.
# ═════════════════════════════════════════════════════════════════════════════

# FET drain land, solid body 4.7 x 3.75 mm (OSE [50] p. 46): the opposite face
# under it carries the thermal-via field and cannot hold parts.
VIA_KEEPOUT_PER_FET = 4.7 * 3.75
# Phase pour 7.5 mm wide at 50 A, 2 oz; un-covered run pour-edge to terminal
# 15 mm (OSE docs/tools/conductor_sizing.py).  Scaled at constant current
# density (width x I/50).  ESTIMATE until conductor_sizing.py is re-run at 80 A.
POUR_W_50A = 7.5
POUR_RUN = 15.0


def ring_width_fit(skin, k, phi, d, env, w_nom, side):
    """Widest panel (<= w_nom) on `side` (+1 power, -1 signal) of a hinge at
    azimuth phi that clears the skin at ring k.  Bisection on the corner test."""
    def ok(w):
        a = math.degrees(math.atan2(w / 2.0, d))
        return bay.panel_fits(skin, k, 0.0, phi + side * a, w, d, env)
    if ok(w_nom):
        return w_nom
    lo, hi = 0.0, w_nom
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    return lo


# Volumes other systems own inside the annulus: (az_lo, az_hi, z_lo, z_hi) in
# the PORT-pod frame this tool uses (port = starboard mirrored in x, so a
# starboard azimuth a maps to 180 - a).  Default: the dorsal spine/shroud,
# solid down to r 34.9 over az 226..314 (symmetric about 270, so identical on
# both pods), from Z 100 to the nozzle housing (tools/dorsal_shroud_resize_64.py,
# AZ_L/AZ_R/Z_START/R_IN), which also contains the nozzle servo pocket
# (nacelle_nozzle_servo_64mm.scad NSV_SPINE_AZ 250..292, NSV_SPINE_Z 138..187).
# A design point may override with "keepouts".
KEEPOUTS = [(226.0, 314.0, 100.0, 209.0)]
KEEPOUT_RIB = 3.0      # [deg] printed wall between a bay and a keep-out


def _az_overlap(lo, hi, k_lo, k_hi):
    for turn in (-360.0, 0.0, 360.0):
        if lo < k_hi + turn and hi > k_lo + turn:
            return True
    return False


def in_keepout(az_lo, az_hi, z_lo, z_hi):
    """Does an angular x axial patch touch any keep-out (incl. rib margin)?"""
    return any(_az_overlap(az_lo - KEEPOUT_RIB, az_hi + KEEPOUT_RIB, a0, a1)
               and z_lo < z1 and z_hi > z0 for a0, a1, z0, z1 in KEEPOUTS)


def bay_profile(zs, skin, phi, env, wp, ws, fmin):
    """Per-ring fitted widths along the best contiguous run at hinge phi.

    A ring whose panel footprint enters a keep-out gets zero width, so the run
    stops there (it is another system's space, not a skin limit)."""
    d = MOUNT_R
    if bay.excluded(float(phi), d):
        return None
    a_p = math.degrees(math.atan2(wp / 2.0, d))
    a_s = math.degrees(math.atan2(ws / 2.0, d))
    prof = []
    for k, z in enumerate(zs):
        if in_keepout(phi - 2 * a_s, phi + 2 * a_p, float(z), float(z) + DZ):
            prof.append((float(z), 0.0, 0.0))
        else:
            prof.append((float(z), ring_width_fit(skin, k, phi, d, env, wp, +1),
                         ring_width_fit(skin, k, phi, d, env, ws, -1)))
    best, cur = [], []
    for row in prof:
        if row[1] >= fmin * wp and row[2] >= fmin * ws:
            cur.append(row)
            if len(cur) > len(best):
                best = list(cur)
        else:
            cur = []
    return best or None


def area_after_reserve(prof, fwd_mm, aft_mm):
    """Panel areas (power, signal) after reserving harness-loop length at the
    forward and aft wire-exit ends, and the remaining Z span."""
    z0 = prof[0][0] + fwd_mm
    z1 = prof[-1][0] + DZ - aft_mm
    a_p = a_s = 0.0
    for z, wp, ws in prof:
        lo, hi = max(z, z0), min(z + DZ, z1)
        if hi > lo:
            a_p += wp * (hi - lo)
            a_s += ws * (hi - lo)
    return a_p, a_s, max(0.0, z1 - z0), (z0, z1)


# Aft limit for harness-loop zones: the nozzle servo drive sits at
# NOZ_Z - 16.25 (nacelle_mass_cg_64.py row "Nozzle servo drive (V1)"); its
# azimuth is not yet fixed (plan U4), so no loop zone is credited aft of it.
LOOP_Z_MAX = 166.25 * P64_A - 16.25


def free_beyond(zs, skin, phi, prof, od, end):
    """Axial length beyond the board run (fwd: end=-1, aft: end=+1) in which a
    lead of diameter `od` still clears the duct wall and the cover, at the hinge
    azimuth — that is where a harness loop can live without costing board."""
    if end < 0:
        ks = [k for k, z in enumerate(zs) if z < prof[0][0]][::-1]
    else:
        ks = [k for k, z in enumerate(zs)
              if prof[-1][0] + DZ <= z and z + DZ <= LOOP_Z_MAX]
    run = 0.0
    for k in ks:
        if in_keepout(phi, phi, float(zs[k]), float(zs[k]) + DZ):
            break                       # a loop may not run into a keep-out
        if bay.skin_at(skin, k, phi) - bay.SKIN_WALL - MOUNT_R >= od:
            run += DZ
        else:
            break
    return run


def needs_v2(p):
    """Board area each functional group needs (mm2, both faces counted)."""
    n, i = p["fet_per_leg"], p["current_a"]
    eta = p["packing_eta"]
    term = AREA_50A["term_total"] * p["term_area_scale"]
    parts_p = (6 * n * AREA_50A["fet_each"]
               + 3 * p["shunt_per_phase"] * AREA_50A["shunt_each"]
               + term + AREA_50A["power_other"] + p.get("power_area_delta", 0.0))
    pour_w = POUR_W_50A * i / 50.0
    pours = (3 + 2) * pour_w * POUR_RUN          # 3 phase runs F + VM/GND runs B
    vias = 6 * n * VIA_KEEPOUT_PER_FET
    need_p = parts_p / eta + pours + vias
    parts_l = AREA_50A["logic_other"] + p.get("logic_area_delta", 0.0)
    barriers = {"axial_two": 2, "axial_shared": 1}.get(p["isolation"], 0)
    creep_len = barriers * (CREEP + 2 * CREEP_INSET)
    return need_p, parts_l / eta, creep_len, {"pours": pours, "vias": vias}


def loops_v2(p):
    """Harness-loop axial reservations (fwd, aft) per variant, mm.

    Loop length = minimum bend radius + in-bay bullet connector (NAC-64-SVC-01
    puts the phase bullets inside the bays).  Bend radius = k x conductor OD:
    NASA-STD-8739.4A Chg 3 §7.2.19 / Table 7-1 (p. 30) — harness of AWG 10 or
    smaller without coax: minimum 3 x OD, optimum 10 x OD; AWG 8 or larger:
    minimum 6 x OD.  Conductor ODs are design-point inputs marked VERIFY.
    Variant A (fwd-motor ESC): every lead leaves the FORWARD end.
    Variant B (aft-motor ESC): pack + signal forward, phases AFT.
    """
    ph = p["bend_k"] * p["phase_od"] + p["bullet_len"]
    pk = p["bend_k"] * p["pack_od"] + p.get("pack_bullet_len", p["bullet_len"])
    a = (max(ph, pk), p.get("loop_misc", 0.0))
    b = (pk, ph)
    return {"A": a, "B": b}


def bay_avail(p, zs, skin, by_phi, by_phi_pow, pow_env_differs, in_layout,
              b, fwd_r, aft_r, od_f, od_a, power=False):
    """Usable area of one bay after harness-loop reserves.

    Returns (power-panel area, signal-panel area, span, (z0, z1), lane cost,
    (fitted power width at the fwd end, at the aft end)).  A power bay with no
    run at the lower power-bay stack is unusable (all zeros), never silently
    swapped for the taller-envelope profile.
    """
    if power and pow_env_differs:
        pr = by_phi_pow.get(b[0])
        if pr is None:
            return (0.0, 0.0, 0.0, (0.0, 0.0), 0.0, (0.0, 0.0))
    else:
        pr = by_phi[b[0]]
    f_free = free_beyond(zs, skin, b[0], pr, od_f, -1) if fwd_r else 0.0
    a_free = free_beyond(zs, skin, b[0], pr, od_a, +1) if aft_r else 0.0
    a_p, a_s, span, zz = area_after_reserve(
        pr, max(0.0, fwd_r - f_free), max(0.0, aft_r - a_free))
    lane_cost = (p["lane_strip_w"] * span) if in_layout else 0.0
    ends = [w for z, w, _ in pr if zz[0] <= z + DZ and z <= zz[1]]
    end_w = (ends[0], ends[-1]) if ends else (0.0, 0.0)
    return (a_p, a_s, span, zz, lane_cost, end_w)


def _assess_v2(p, zs, skin, sel, by_phi, by_phi_pow, pow_env_differs, loops,
               order, nb, wp, ws, need_p, need_l, creep_len, in_layout):
    """Margins for one variant-to-bay assignment."""
    results = {}

    def avail_of(b, fwd_r, aft_r, od_f, od_a, power=False):
        return bay_avail(p, zs, skin, by_phi, by_phi_pow, pow_env_differs,
                         in_layout, b, fwd_r, aft_r, od_f, od_a, power)

    for esc, idx in order:
        fwd, aft = loops[esc]
        bay_ids = sel[idx * nb:(idx + 1) * nb] if len(sel) == 2 * nb else []
        if not bay_ids:
            results[esc] = None
            continue
        od_f = max(p["phase_od"], p["pack_od"]) if fwd else 0.0
        od_a = p["phase_od"] if aft else 0.0
        if nb == 1:
            avail = [avail_of(bay_ids[0], fwd, aft, od_f, od_a)]
        else:
            # Power bay carries the phase + pack leads; the logic bay only the
            # signal/bus leads (sig_od, no bullet, forward end).  Put the power
            # group in whichever of the two bays leaves it more area.
            sig = p["bend_k"] * p.get("sig_od", 2.0)
            cands = []
            for pw, lg in ((bay_ids[0], bay_ids[1]), (bay_ids[1], bay_ids[0])):
                ap = avail_of(pw, fwd, aft, od_f, od_a, power=True)
                al = avail_of(lg, sig, 0.0, p.get("sig_od", 2.0), 0.0)
                cands.append((min(2 * (ap[0] + ap[1]) - need_p,
                                  2 * (al[0] + al[1]) - need_l), ap, al, pw, lg))
            cands.sort(key=lambda c: -c[0])
            avail = [cands[0][1], cands[0][2]]
            bay_ids = [cands[0][3], cands[0][4]]
        if nb == 1:
            a_p, a_s, span, zz, lane, end_w = avail[0]
            pow_av = 2 * a_p - lane          # both faces of the power panel
            log_av = 2 * a_s - 2 * ws * creep_len
            m_pow = (pow_av - need_p) / (2 * wp)
            m_log = (log_av - need_l) / (2 * ws)
        else:                                # bay 1 = power, bay 2 = logic
            (p1, s1, span, zz, lane, end_w), (p2, s2, _, _, _, _) = avail
            pow_av = 2 * (p1 + s1) - lane
            log_av = 2 * (p2 + s2) - 2 * (wp + ws) * creep_len \
                - 2 * (wp + ws) * p.get("interconnect_loop", 6.0)
            m_pow = (pow_av - need_p) / (2 * (wp + ws))
            m_log = (log_av - need_l) / (2 * (wp + ws))
        results[esc] = {"margin_mm": round(min(m_pow, m_log), 2),
                        "m_power_mm": round(m_pow, 2), "m_logic_mm": round(m_log, 2),
                        "board_span_mm": round(span, 1),
                        "z_board": [round(zz[0], 1), round(zz[1], 1)],
                        "reserve_fwd_aft_mm": [round(fwd, 1), round(aft, 1)],
                        "bays_az": [b[0] for b in bay_ids],
                        "fitted_area_mm2": round(sum(a[0] + a[1] for a in avail), 0),
                        "end_power_w_mm": [round(end_w[0], 2), round(end_w[1], 2)],
                        "z_centre_mm": round(sum((a[3][0] + a[3][1]) / 2 for a in avail)
                                             / len(avail), 1)}

    return results


def merge_shroud(zs, skin, scad_path):
    """Raise the skin to the dorsal shroud's OUTER surface where it is higher.

    The shroud generator (tools/dorsal_shroud_resize_64.py) writes a starboard-
    frame polyhedron; this tool works in the port frame (port = starboard
    mirrored in x, az_port = 180 - az_stbd).  Outer radius per (Z ring, 1 deg)
    is the max point radius in that cell.  Only meaningful if the shroud is
    made hollow above the bay (an owner decision the run records)."""
    import re
    txt = Path(scad_path).read_text()
    body = txt[txt.index("points = [") + 10:txt.index("], faces")]
    pts = np.array([[float(v) for v in t.split(",")] for t in
                    re.findall(r"\[([-\d.]+,[-\d.]+,[-\d.]+)\]", body)])
    r = np.hypot(pts[:, 0], pts[:, 1])
    az = (180.0 - np.degrees(np.arctan2(pts[:, 1], pts[:, 0]))) % 360.0
    out = skin.copy()
    for k, z in enumerate(zs):
        m = (pts[:, 2] >= z) & (pts[:, 2] < z + DZ)
        if not m.any():
            continue
        cells = np.round(az[m]).astype(int) % bay.N_AZ_SAMPLE
        rmax = np.zeros(bay.N_AZ_SAMPLE)
        np.maximum.at(rmax, cells, r[m])
        out[k] = np.maximum(out[k], rmax)
    return out


# Forward limit for model 2: the aft face of the fixed Z 70.06 cavity bulkhead
# (CAVITY_BULKHEAD_Z[1] = 62 x 1.13, CAVITY_BULKHEAD_T 3.0).  The two webs at
# Z 74.35 / 139.85 are BAY-TIED (nacelle_pod_64mm_tandem.scad: "tied to the
# BAYS") and move with whatever bay this tool selects; forward of 70.06 is the
# 10 AWG disconnect bay, another system's space, so nothing here crosses it.
Z_MIN_V2 = 62.0 * P64_A + 3.0 / 2.0


def main_v2(p) -> int:
    global KEEPOUTS, P64_K, P64_A, LOOP_Z_MAX, Z_MAX
    # Uniform nacelle enlargement (owner 2026-10-05): the canonical shell and
    # every pod station scale by `nacelle_scale` about Z 0; the 64 mm duct and
    # the board mount radius (bore + walls) do NOT scale.  Keep-out Z bands
    # are pod stations, so they scale too.
    s_n = p.get("nacelle_scale", 1.0)
    P64_K, P64_A = 1.21 * s_n, 1.13 * s_n
    Z_MAX = 160.0 * P64_A
    LOOP_Z_MAX = (166.25 * 1.13 - 16.25) * s_n
    if "keepouts" in p:
        KEEPOUTS = [(a0, a1, z0 * s_n, z1 * s_n) for a0, a1, z0, z1 in p["keepouts"]]
    zs, skin = skin64(p.get("z_min", Z_MIN_V2 * s_n))
    if p.get("shroud_scad"):
        skin = merge_shroud(zs, skin, REPO / p["shroud_scad"])
    if p.get("measured_exclusions"):
        bay.EXCLUDE = []        # blanket 50 mm-tool sectors replaced by keepouts
    in_layout = p.get("lane_in_layout", False)
    stack = p["pcb_t"] + p["h_outer"] + p["h_inner"] + p["mount_gap"]
    env = stack + (0.0 if in_layout else p["flow_lane"])
    wp, ws = p["w_power"], p["w_signal"]
    nb = p.get("bays_per_esc", 1)
    need_p, need_l, creep_len, extra = needs_v2(p)
    loops = loops_v2(p)

    profs = []
    for phi in np.arange(0.0, 360.0, 2.0):
        pr = bay_profile(zs, skin, float(phi), env, wp, ws, p.get("fmin", 0.6))
        if pr:
            profs.append((float(phi), pr, sum(r[1] + r[2] for r in pr) * DZ))
    # Two bays per ESC: the power bay holds no isolators, so its outer face may
    # be lower than the logic bay's (h_outer_power, default = h_outer).
    env_pow = env - p["h_outer"] + p.get("h_outer_power", p["h_outer"])
    by_phi_pow = {}
    if nb == 2 and env_pow != env:
        for phi in np.arange(0.0, 360.0, 2.0):
            pr = bay_profile(zs, skin, float(phi), env_pow, wp, ws, p.get("fmin", 0.6))
            if pr:
                by_phi_pow[float(phi)] = pr
    profs.sort(key=lambda t: -t[2])
    rows = [(phi, len(pr) * DZ, pr[0][0], pr[-1][0] + DZ, MOUNT_R)
            for phi, pr, _ in profs]
    sel = pick_bays(rows, 2 * nb, wp, ws)
    if nb == 2 and len(sel) == 4:
        # each ESC takes two NEIGHBOURING bays (short inter-bay interconnect):
        # sort by azimuth and pick the pairing with the smaller total gap
        s4 = sorted(sel, key=lambda r: r[0])
        gap = lambda a, b: abs((a[0] - b[0] + 180) % 360 - 180)   # noqa: E731
        p1 = gap(s4[0], s4[1]) + gap(s4[2], s4[3])
        p2 = gap(s4[1], s4[2]) + gap(s4[3], s4[0])
        sel = s4 if p1 <= p2 else [s4[1], s4[2], s4[3], s4[0]]
    by_phi = {phi: pr for phi, pr, _ in profs}

    def assess(order):
        return _assess_v2(p, zs, skin, sel, by_phi, by_phi_pow, env_pow != env,
                          loops, order, nb, wp, ws, need_p, need_l, creep_len,
                          in_layout)

    def score(r):
        return min(v["margin_mm"] for v in r.values()) if all(r.values()) else -999.0

    # which side of the pod gets which variant is free: try both
    r1, r2 = assess((("A", 0), ("B", 1))), assess((("A", 1), ("B", 0)))
    results = r1 if score(r1) >= score(r2) else r2
    ok = all(results.values())
    margin = score(results)
    spans = [r["board_span_mm"] for r in results.values()] if ok else [0.0]
    if min(spans) <= 0:
        print(json.dumps({"model": 2, "fit_margin_mm": round(margin, 2),
                          "esc": results, "error": "no usable bay span"}, indent=1))
        return 2
    # Thermal is evaluated PER ESC on its own span and skin-fitted area, and the
    # hotter one is reported (review 2026-10-03: using the longest span and the
    # nominal widths flattered the binding ESC).
    therm = {}
    for esc, r in results.items():
        span_e, area_e = r["board_span_mm"], r["fitted_area_mm2"]
        if in_layout:
            q = dict(p, flow_lane=p["h_outer"], w_power=p["lane_strip_w"], w_signal=0.0)
            _, p_tot, p_fet, h, _, dt_air = thermal_tch(q, span_e)
            # convection only on the lane strip walls, not the whole board
            r_conv = 1.0 / (h * 2 * p["lane_strip_w"] * span_e * nb * 1e-6)
            tch_e = T_AMB + dt_air + p_tot * r_conv + p_fet * RTH_CH_C
        else:
            tch_e, p_tot, p_fet, h, r_conv, dt_air = thermal_tch(p, span_e, area_e)
        therm[esc] = (tch_e, p_tot, h, dt_air)
        r["tch_c"] = round(tch_e, 1)
        r["fwd_of_pivot"] = r["z_centre_mm"] < CG_Z
    hot = max(therm, key=lambda e: therm[e][0])
    tch, p_tot, h, dt_air = therm[hot]
    span = sum(spans) / len(spans)
    m_esc = esc_mass(p, span, need_p * p["packing_eta"], need_l * p["packing_eta"])
    # CG from each ESC's own (reserved) board centre, not the raw bay runs
    z_c = [r["z_centre_mm"] for r in results.values()]
    z_mean = sum(z_c) / len(z_c)
    cover = COVER_G_PER_MM * span * len(sel)
    m_new, d_cg = cg_roll_up(m_esc, z_mean, cover)
    # Egress against the FITTED power-panel width at each variant's exit end(s):
    # A exits forward only; B forward (pack) and aft (phases).
    s_t = math.sqrt(p["term_area_scale"])
    phase_w, pack_w = 3 * 5.5 * s_t, 2 * 8.5 * s_t
    ew_a, ew_b = results["A"]["end_power_w_mm"], results["B"]["end_power_w_mm"]
    ega = max(phase_w, pack_w) <= ew_a[0]
    egb = pack_w <= ew_b[0] and phase_w <= ew_b[1]
    out = {
        "model": 2,
        "fit_margin_mm": round(margin, 2),
        "esc": results,
        "need_power_mm2": round(need_p, 0),
        "need_logic_mm2": round(need_l, 0),
        "pour_mm2": round(extra["pours"], 0), "via_keepout_mm2": round(extra["vias"], 0),
        "stack_mm": round(stack, 2), "envelope_mm": round(env, 2),
        "tch_c": round(tch, 1), "p_total_w": round(p_tot, 2),
        "h_lane_w_m2k": round(h, 0), "dt_air_k": round(dt_air, 1),
        "esc_mass_g_estimate": round(m_esc, 1), "assy_mass_g": round(m_new, 1),
        "d_cg_mm": round(d_cg, 2),
        "cg_z_mm": round(CG_Z + d_cg, 2), "pivot_z_mm": CG_Z,
        "hover_slack_after_mm": round(HOVER_SLACK + d_cg, 2),
        "egress_a_ok": ega, "egress_b_ok": egb,
        "creepage_ok": p["isolation"] != "lateral",
        "packing_eta": p["packing_eta"],
    }
    print(json.dumps(out, indent=1))
    # Non-zero exit when the design point fails, so a caller cannot read a
    # printed result as a pass.
    passed = (margin >= 0 and tch <= T_CH_DESIGN and ega and egb
              and out["creepage_ok"] and HOVER_SLACK + d_cg >= 0)
    return 0 if passed else 1


if __name__ == "__main__":
    _p = json.loads(Path(sys.argv[1]).read_text())
    with overrides_64mm(_p.get("cover_t", 2.5)):
        sys.exit(main_v2(_p) if _p.get("model") == 2 else main())
