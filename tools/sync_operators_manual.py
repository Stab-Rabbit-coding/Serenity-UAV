#!/usr/bin/env python3
"""Keep docs/OPERATORS_MANUAL.md in step with the flight envelope and other limits.

WBS.md section 0.10.3 (requirement OM-3/OM-5, owner 2026-11-02): the Operator's
Manual shall be kept current with the flight envelope and the other limits by an
automatic polling script that runs in the commit chain and is updated with every
repository commit.  This is that script.

What it does, in order (one pass per commit):

1. POLL   -- hash every source the manual draws on (``WATCHED``) and compare with the
             per-file hashes recorded in the manual's sync stamp; report what changed.
2. VERIFY -- cross-check the single-source limits file
             ``current-specification/flight_limits.json`` against the tools and docs
             that restate it (drift gate; exit 1 on a mismatch, like
             ``tools/check_datum_drift.py``).  Retired values found in the key docs
             are reported as warnings.
3. RENDER -- recompute every derived figure (T/W, theta_hover, V_min, vertical T/W,
             density altitude, hover current and endurance) with the same physics as
             ``tools/flight_envelope_endurance.py`` and rewrite the manual's
             generated regions:

               <!-- AUTO:name -->  ...table...  <!-- /AUTO:name -->     whole blocks
               <!--V:key-->value<!--/V-->                               inline values

             Everything outside those markers is hand-written prose and is never
             touched.
4. STAMP  -- write the parent commit, the source digest and the per-file hashes.

Usage::

    /usr/bin/python3 tools/sync_operators_manual.py            # rewrite in place
    /usr/bin/python3 tools/sync_operators_manual.py --check    # exit 1 if stale (CI)
    /usr/bin/python3 tools/sync_operators_manual.py --stage    # rewrite + git add (hook)

Sources and physics: docs/flight_envelope.md (formulas), [REF-EDF-003] second sheet
(QF2822-2300KV: 2,370 gf, 24 V, 57.0 A, 1,368 W), [REF-FAA-002] 107.51 (regulatory
ceilings), docs/failsafe_thresholds.md, docs/POWER_DISTRIBUTION.md section 8.

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (requirement and direction).
Written by Claude Sonnet 5.5 (Anthropic) under the author's direction, 2026-11-02,
per AGENTS.md section 3 AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "docs" / "OPERATORS_MANUAL.md"
LIMITS = ROOT / "current-specification" / "flight_limits.json"

# Files the manual's content is derived from.  A change to any of them shows up in
# the POLL report and in the stamp.
WATCHED = [
    "current-specification/flight_limits.json",
    "current-specification/auw_ledger.json",
    "tools/flight_envelope_endurance.py",
    "tools/auw_ledger.py",
    "docs/flight_envelope.md",
    "docs/failsafe_thresholds.md",
    "docs/POWER_DISTRIBUTION.md",
    "docs/FIRST_FLIGHT_READINESS.md",
    "docs/CARGO_WINCH_SPECIFICATION.md",
    "graphical-build-guide/flight-phases/WBS.md",
]

# Retired values.  Found in the key docs -> warning (never blocks; plans and history
# legitimately keep them).  Found in the manual -> error.
RETIRED = [r"2400 ?KV", r"2,?135 ?gf", r"1,?265\.4", r"\b145 ?°", r"−5° to 140", r"-5 to 140"]
KEY_DOCS = ["README.md", "docs/flight_envelope.md", "docs/failsafe_thresholds.md"]

G0 = 9.80665
KT_PER_MS = 1.0 / 0.514444


def _load_endurance():
    """Import tools/flight_envelope_endurance.py (the repo's envelope physics)."""
    spec = importlib.util.spec_from_file_location(
        "flight_envelope_endurance", ROOT / "tools" / "flight_envelope_endurance.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _f(x: float, nd: int = 0) -> str:
    return f"{x:,.{nd}f}"


def _round(x: float, step: int) -> int:
    return int(round(x / step) * step)


def compute(lim: dict, E) -> dict[str, str]:
    """Every derived figure the manual quotes, as display strings."""
    fan, tilt, reg, fs, ops = (
        lim["fan"],
        lim["tilt"],
        lim["regulatory"],
        lim["failsafe"],
        lim["ops"],
    )
    n_fans = fan["n_per_nacelle"] * fan["n_nacelles"]
    t_total_gf = fan["thrust_gf"] * n_fans
    t_n = t_total_gf / 1000 * G0
    v: dict[str, str] = {}
    v["tilt_min"] = f"{tilt['min_deg']:+.0f}".replace("-", "−")
    v["tilt_max"] = f"{tilt['max_deg']:+.0f}"
    v["tilt_span"] = f"{tilt['max_deg'] - tilt['min_deg']:.0f}"
    v["fan_model"] = fan["model"]
    v["fan_ozf"] = f"{fan['thrust_ozf']:.2f}"
    v["fan_gf"] = _f(fan["thrust_gf"])
    v["fan_lbf"] = f"{fan['thrust_gf'] / 453.59237:.2f}"
    v["fan_n"] = f"{fan['thrust_gf'] / 1000 * G0:.1f}"
    v["fan_v"] = f"{fan['voltage_v']:.0f}"
    v["fan_a"] = f"{fan['current_a']:.1f}"
    v["fan_w"] = _f(fan["power_w"])
    v["esc_a"] = f"{fan['esc_a']}"
    v["tot_lbf"] = f"{t_total_gf / 453.59237:.2f}"
    v["tot_gf"] = _f(t_total_gf)
    v["tot_n"] = f"{t_n:.1f}"

    cases = {"pl": E.AUW_S1_G + E.PAYLOAD_G, "np": E.AUW_S1_G, "3c": E.AUW_S1_CELL3_G}
    for k, m in cases.items():
        v[f"auw_{k}_g"] = _f(m)
        v[f"auw_{k}_lbm"] = f"{m * E.LBM_PER_G:.2f}"
        tw = t_total_gf / m
        v[f"tw_{k}"] = f"{tw:.2f}"
        v[f"theta_{k}"] = f"{math.degrees(math.asin(1 / tw)):.1f}"
        v[f"bank_{k}"] = f"{math.degrees(math.acos(1 / tw)):.1f}"
        v[f"da1_{k}"] = _f(_round(E.isa_sigma_alt_ft(1 / tw), 100))
        for deg in (120, 130, int(tilt["max_deg"])):
            v[f"vtw_{k}_{deg}"] = f"{tw * math.sin(math.radians(deg)):.2f}"
        w_n = m * G0 / 1000
        for deg in (-5, 0, 10, 20, 30, 40):
            lreq = w_n - t_n * math.sin(math.radians(deg))
            vm = math.sqrt(2 * lreq / (E.RHO0 * E.S_WING * E.CL_MAX)) if lreq > 0 else 0.0
            v[f"vmin_{k}_{deg}"] = f"{vm * KT_PER_MS:.1f}"
    twf = ops["t_w_floor"]
    tw_pl = t_total_gf / cases["pl"]
    v["tw_floor"] = f"{twf:.1f}"
    v["da_floor"] = _f(_round(E.isa_sigma_alt_ft(twf / tw_pl), 100))

    for name, case in E.CASES.items():
        for tag, m, cap in (
            ("pl", cases["pl"], E.CAP_PAIR_AH),
            ("np", cases["np"], E.CAP_PAIR_AH),
            ("3c", cases["3c"], 6.0),
        ):
            cur = E.hover_current(m, case["v_load"], case["stack"])
            v[f"i_{name}_{tag}"] = f"{cur:.0f}"
            v[f"c_{name}_{tag}"] = f"{cur / cap:.0f}"
            v[f"t_{name}_{tag}"] = f"{E.endurance_s(m, cap, case):.0f}"
    air = sum(a for _, a, _, _ in E.MISSION)
    target = int(air * 1.30)
    v["target_s"] = str(target)
    v["target_min"] = f"{target / 60:.1f}"
    v["pct_plan"] = f"{float(v['t_PLANNING_pl']) / target * 100:.0f}"
    v["pct_nom"] = f"{float(v['t_NOMINAL_pl']) / target * 100:.0f}"
    v["tw_throttle70"] = f"{tw_pl * 0.49:.2f}"
    v["tw_half"] = f"{tw_pl * 0.5:.2f}"
    v["tw_pl_pct_loss"] = f"{(1 - 1 / tw_pl) * 100:.0f}"
    # regulatory / failsafe / ops passthrough
    v["vne"] = f"{reg['v_ne_kt']:.0f}"
    v["vne_ms"] = f"{reg['v_ne_kt'] * 0.514444:.0f}"
    v["agl_ft"] = f"{reg['max_agl_ft']:.0f}"
    v["agl_m"] = f"{reg['max_agl_ft'] * 0.3048:.0f}"
    v["vis"] = f"{reg['min_visibility_sm']:.0f}"
    v["cld_b"] = f"{reg['cloud_below_ft']:.0f}"
    v["cld_h"] = _f(reg["cloud_horizontal_ft"])
    for key, val in fs.items():
        if isinstance(val, (int, float)):
            v[f"fs_{key}"] = f"{val:g}"
    v["trans_ft"] = f"{ops['transition_floor_ft']:.0f}"
    v["trans_m"] = f"{ops['transition_floor_ft'] * 0.3048:.1f}"
    v["p5_trans_m"] = f"{ops['phase5_transition_min_m']:.0f}"
    v["p5_trans_ft"] = f"{ops['phase5_transition_min_m'] / 0.3048:.0f}"
    v["payload_oz"] = f"{ops['payload_oz']:.1f}"
    v["payload_g"] = f"{ops['payload_g']:.1f}"
    return v


def blocks(v: dict[str, str]) -> dict[str, str]:
    """Generated Markdown tables, keyed by AUTO block name."""
    b: dict[str, str] = {}
    b["config"] = "\n".join(
        [
            "| Item | Value | Source / status |",
            "| --- | --- | --- |",
            "| Length | 24.0 in (609 mm) | `README.md` Rev S figure — **hull scale under review; verify against `current-specification/`** |",
            "| Wingspan | 19.1 in (486 mm) | same |",
            "| Height | 7.93 in (201.5 mm) | same |",
            f"| Propulsion | 4 × 64 mm EDF, {v['fan_model']}, two per nacelle in tandem, co-rotating; {v['esc_a']} A ESCs | `current-specification/flight_limits.json`; [REF-EDF-003] |",
            f"| Rated thrust per fan | {v['fan_lbf']} lbf ({v['fan_ozf']} ozf, {v['fan_gf']} gf, {v['fan_n']} N) at {v['fan_a']} A, {v['fan_w']} W, {v['fan_v']} V, 100 % throttle | [REF-EDF-003] second sheet |",
            f"| Total nacelle thrust | {v['tot_lbf']} lbf ({v['tot_gf']} gf, {v['tot_n']} N) — **no tandem stacking loss applied** | `docs/flight_envelope.md` |",
            "| Battery | 6S, two cells (4.4 Ah pair) on a payload mission | `docs/flight_envelope.md`; `docs/BATTERY_SPLIT_OPTIONS.md` |",
            f"| AUW, two cells + {v['payload_oz']} oz payload | {v['auw_pl_lbm']} lbm ({v['auw_pl_g']} g) — **provisional** | `docs/flight_envelope.md` |",
            f"| T/W, two cells + payload | {v['tw_pl']} (design floor {v['tw_floor']}) | computed |",
            f"| Nacelle tilt range | {v['tilt_min']}° to {v['tilt_max']}° ({v['tilt_span']}° span); **0° = horizontal (cruise), 90° = vertical (hover)** | owner 2026-11-02; `current-specification/flight_limits.json` |",
            "| Payload | 8.0 oz (226.8 g) in a 4 in × 3 in × 3 in (102 × 76 × 76 mm) bay | `README.md` |",
        ]
    )
    b["reg_limits"] = "\n".join(
        [
            "| Limit | Value | Source |",
            "| --- | --- | --- |",
            f"| Groundspeed (V_NE) | ≤ {v['vne']} kt ({v['vne_ms']} m/s) | [REF-FAA-002 §107.51(a)] |",
            f"| Altitude | ≤ {v['agl_ft']} ft ({v['agl_m']} m) AGL, unless within 400 ft of a structure | [REF-FAA-002 §107.51(b)] |",
            f"| Visibility | ≥ {v['vis']} statute miles from the control station | [REF-FAA-002 §107.51(c)] |",
            f"| Cloud clearance | ≥ {v['cld_b']} ft below, ≥ {v['cld_h']} ft horizontal | [REF-FAA-002 §107.51(d)] |",
            "| Operating hours | Daylight, or civil twilight with anti-collision lighting | [REF-FAA-002 §107.29] |",
            "| Line of sight | Unaided VLOS by the RPIC or VO throughout the flight | [REF-FAA-002 §107.31] |",
            f"| Registration | Required above 0.55 lbm (250 g); this aircraft is {v['auw_pl_lbm']} lbm | [REF-FAA-001 §48.25] |",
        ]
    )
    b["design_limits"] = "\n".join(
        [
            "| Limit | Value | Basis |",
            "| --- | --- | --- |",
            f"| Never-exceed speed | {v['vne']} kt | The regulatory ceiling. **Not an aerodynamic limit.** Actual top speed not established. |",
            f"| Tilt range | {v['tilt_min']}° to {v['tilt_max']}° | Hard stops; above θ_hover the vertical T/W falls to {v['vtw_pl_135']} at {v['tilt_max']}° (Ch. 11) |",
            f"| Minimum T/W for flight | {v['tw_floor']} (hover control floor, WA-R18) | `docs/flight_envelope.md` §3.2 |",
            f"| Density altitude at T/W = {v['tw_floor']} | about {v['da_floor']} ft | First-order estimate; a hot-day launch at a moderate-elevation site can reach it |",
            f"| Transition sweep (90° ↔ 0°) | **Initiate no lower than {v['trans_ft']} ft ({v['trans_m']} m) AGL** | Conservative pre-validation policy [`docs/flight_envelope.md` §5] |",
            f"| Phase 5 first-flight transition | ≥ {v['p5_trans_m']} m ({v['p5_trans_ft']} ft) AGL | `graphical-build-guide/flight-phases/WBS.md` Phase 5 |",
            f"| Payload | ≤ {v['payload_oz']} oz ({v['payload_g']} g); the third battery cell shall not be carried on a payload mission | `docs/flight_envelope.md` |",
            "| 64 mm EDF RPM redline | **Not established** | `docs/flight_envelope.md` §2.2 |",
            f"| Crosswind | **Not established** (hover bank-authority bound ≈ {v['bank_pl']}° is not a limit) | `docs/flight_envelope.md` §4 |",
            "| Stall speed | **Not established** — CL_max unknown for the built wing section | `docs/flight_envelope.md` banner |",
        ]
    )
    b["powerplant"] = "\n".join(
        [
            "| Parameter | Value | Source |",
            "| --- | --- | --- |",
            f"| Cell voltage, normal | ≥ {v['fs_cell_warn_v']} V/cell ({v['fs_pack_warn_v']} V pack) | `docs/failsafe_thresholds.md` §1 |",
            f"| Low-battery warning | < {v['fs_cell_warn_v']} V/cell or < {v['fs_pack_warn_v']} V | same |",
            f"| **Return-to-home trigger** | < {v['fs_cell_rtl_v']} V/cell or < {v['fs_pack_rtl_v']} V | same |",
            f"| Emergency | < {v['fs_cell_emergency_v']} V/cell or < {v['fs_pack_emergency_v']} V | same |",
            f"| ESC rating | {v['esc_a']} A | owner 2026-11-02 |",
            f"| Per-fan current at full throttle | {v['fan_a']} A at {v['fan_v']} V | [REF-EDF-003] second sheet |",
            "| ESC over-current warning | > 35 A | `docs/POWER_DISTRIBUTION.md` §8.2 |",
            "| ESC over-current, critical | > 40 A for > 5 s | same |",
            "| ESC burst | > 55 A: that EDF is disarmed immediately | same |",
            f"| ESC thermal cutback / shutdown | {v['fs_esc_cutback_c']} °C / {v['fs_esc_shutdown_c']} °C **design target** | `docs/failsafe_thresholds.md` §4 |",
            "| Phase 5 pass criterion | All four ESCs ≤ 70 °C at full hover power | `graphical-build-guide/flight-phases/WBS.md` |",
        ]
    )
    mx = v["tilt_max"]
    b["tilt_table"] = "\n".join(
        [
            "| Tilt | Vertical T/W (two cells + payload) | Behavior (design estimate) |",
            "| --- | --- | --- |",
            f"| 90° | {v['tw_pl']} | Full hover |",
            f"| 120° | {v['vtw_pl_120']} | Backing thrust |",
            f"| 130° | {v['vtw_pl_130']} | Backing thrust |",
            f"| {mx}° (hard stop) | **{v['vtw_pl_135']}** | Thin margin over weight — hold only briefly |",
            f"| ≈ {v['theta_pl']}° | 1.00 | Critical angle: thrust equals weight |",
        ]
    )
    b["vmin_table"] = "\n".join(
        [
            "| Tilt | V_min, two cells + payload | V_min, two cells, no payload |",
            "| --- | --- | --- |",
        ]
        + [
            f"| {d}° | {v[f'vmin_pl_{d}']} kt | {v[f'vmin_np_{d}']} kt |"
            for d in (-5, 0, 10, 20, 30, 40)
        ]
    )
    b["battery_alerts"] = "\n".join(
        [
            "| Alert | Condition | Automatic action | Operator action |",
            "| --- | --- | --- | --- |",
            f"| WARN | < {v['fs_cell_warn_v']} V/cell or < {v['fs_pack_warn_v']} V | CAN FD warning; ground alert; log | Plan landing |",
            f"| CRITICAL | < {v['fs_cell_rtl_v']} V/cell or < {v['fs_pack_rtl_v']} V | Non-essential loads shed; return-to-home begins | **LAND** |",
            f"| EMERGENCY | < {v['fs_cell_emergency_v']} V/cell, < {v['fs_pack_emergency_v']} V, or hardware under-voltage latch | All non-propulsion loads off; **70 % throttle cap**; fault latch | **LAND IMMEDIATELY** |",
        ]
    )
    b["radio_loss"] = "\n".join(
        [
            "| Link | Timer | Automatic action |",
            "| --- | --- | --- |",
            f"| SiK 915 MHz / LoRa | **{v['fs_radio_loss_rtl_sik_lora_s']} s** | Return-to-home |",
            f"| 49 MHz AX.25 | **{v['fs_radio_loss_rtl_49mhz_s']} s** | Return-to-home |",
            "| Wi-Fi 5 GHz / Zigbee 2.4 GHz | **not established** | — |",
        ]
    )
    b["performance"] = "\n".join(
        [
            "| Parameter | Value | Status |",
            "| --- | --- | --- |",
            f"| AUW, two cells + payload | {v['auw_pl_lbm']} lbm ({v['auw_pl_g']} g) | Provisional |",
            f"| AUW, two cells, no payload | {v['auw_np_lbm']} lbm ({v['auw_np_g']} g) | Provisional |",
            f"| T/W (payload / no payload) | {v['tw_pl']} / {v['tw_np']} | Computed; no tandem loss |",
            f"| Hover current, two cells + payload | {v['i_PLANNING_pl']} A planning ({v['i_NOMINAL_pl']} A nominal) | Computed |",
            f"| Hover endurance to RTH trigger | {v['t_PLANNING_pl']} s planning ({v['t_NOMINAL_pl']} s nominal) with payload; {v['t_PLANNING_np']} s / {v['t_NOMINAL_np']} s without | Computed |",
            f"| Hover endurance, three cells, no payload | {v['t_PLANNING_3c']} s planning ({v['t_NOMINAL_3c']} s nominal) | Computed |",
            f"| Derived mission endurance target | {v['target_s']} s | **Not met** |",
            f"| Critical tilt angle | {v['theta_pl']}° ({v['theta_np']}° without payload) | Computed |",
            f"| Hover bank bound | {v['bank_pl']}° | Control-authority bound |",
            "| Max demonstrated crosswind | Not established | Phase 9 target ≥ 10 kt hover |",
            "| Transition altitude excursion target | ≤ 0.5 m | Post-tuning target; not demonstrated |",
        ]
    )
    return b


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:10] if path.exists() else "missing"


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def verify(lim: dict) -> tuple[list[str], list[str]]:
    """Drift gate.  Returns (errors, warnings)."""
    errs: list[str] = []
    warns: list[str] = []
    fan, tilt = lim["fan"], lim["tilt"]
    n = fan["n_per_nacelle"] * fan["n_nacelles"]

    ledger = (ROOT / "tools" / "auw_ledger.py").read_text()
    m = re.search(r"^THRUST_PER_FAN_GF\s*=\s*([\d.]+)", ledger, re.M)
    if not m or float(m.group(1)) != fan["thrust_gf"]:
        errs.append(
            f"tools/auw_ledger.py THRUST_PER_FAN_GF ({m.group(1) if m else '?'}) != "
            f"flight_limits.json fan.thrust_gf ({fan['thrust_gf']})"
        )
    lj = json.loads((ROOT / "current-specification" / "auw_ledger.json").read_text())
    if abs(lj.get("thrust_gf", 0) - fan["thrust_gf"] * n) > 0.5:
        errs.append(
            f"current-specification/auw_ledger.json thrust_gf ({lj.get('thrust_gf')}) is "
            f"stale vs {fan['thrust_gf'] * n:g}: rerun tools/auw_ledger.py --write"
        )
    nl = (ROOT / "tools" / "nozzle_servo_linkage.py").read_text()
    m = re.search(r"^TILT_LIMIT_DEG\s*=\s*([\d.]+)", nl, re.M)
    if not m or float(m.group(1)) != tilt["max_deg"]:
        errs.append(
            f"tools/nozzle_servo_linkage.py TILT_LIMIT_DEG != tilt.max_deg ({tilt['max_deg']})"
        )
    if abs(fan["thrust_ozf"] - fan["thrust_gf"] / 28.349523) > 0.01:
        errs.append("flight_limits.json fan.thrust_ozf and fan.thrust_gf disagree")
    if abs(fan["voltage_v"] * fan["current_a"] - fan["power_w"]) > 1.0:
        errs.append("flight_limits.json fan power != voltage x current")

    fs = (ROOT / "docs" / "failsafe_thresholds.md").read_text()
    f = lim["failsafe"]
    for label, token in (
        ("cell warn", f"{f['cell_warn_v']:.2f} V"),
        ("cell RTL", f"{f['cell_rtl_v']:.2f} V"),
        ("heartbeat", f"{f['heartbeat_timeout_ms']} ms"),
        ("SiK/LoRa timer", f"{f['radio_loss_rtl_sik_lora_s']} s"),
        ("ESC cutback", f"{f['esc_cutback_c']}"),
        ("ESC shutdown", f"{f['esc_shutdown_c']}"),
    ):
        if token not in fs:
            errs.append(f"docs/failsafe_thresholds.md no longer states {label} ({token})")

    env = (ROOT / "docs" / "flight_envelope.md").read_text()
    for token in (f"{fan['thrust_gf']:,.0f} gf", f"{tilt['max_deg']:+.0f}°".replace("+", "+")):
        if token not in env:
            warns.append(f"docs/flight_envelope.md does not state '{token}'")
    for doc in KEY_DOCS:
        text = (ROOT / doc).read_text()
        for pat in RETIRED:
            if re.search(pat, text):
                warns.append(f"{doc}: retired value /{pat}/ still present")
    return errs, warns


def render(text: str, v: dict[str, str], b: dict[str, str]) -> tuple[str, list[str]]:
    """Fill every AUTO block and inline value; return (new text, problems)."""
    problems: list[str] = []

    def blk(m: re.Match) -> str:
        name = m.group(1)
        if name not in b:
            problems.append(f"unknown AUTO block '{name}'")
            return m.group(0)
        return f"<!-- AUTO:{name} -->\n{b[name]}\n<!-- /AUTO:{name} -->"

    def inl(m: re.Match) -> str:
        key = m.group(1)
        if key not in v:
            problems.append(f"unknown inline value '{key}'")
            return m.group(0)
        return f"<!--V:{key}-->{v[key]}<!--/V-->"

    text = re.sub(r"<!-- AUTO:(\w+) -->\n.*?\n<!-- /AUTO:\1 -->", blk, text, flags=re.S)
    text = re.sub(r"<!--V:(\w+)-->.*?<!--/V-->", inl, text)
    return text, problems


STAMP_RE = re.compile(r"<!-- SYNC-STAMP\n.*?-->", re.S)


def parse_stamp(text: str) -> dict[str, str]:
    m = STAMP_RE.search(text)
    out: dict[str, str] = {}
    if m:
        for line in m.group(0).splitlines()[1 : -0 or None]:
            if ":" in line and not line.startswith("-->"):
                k, _, val = line.partition(":")
                out[k.strip()] = val.strip()
    return out


def make_stamp(parent: str, hashes: dict[str, str]) -> str:
    digest = hashlib.sha256(
        "".join(f"{k}{h}" for k, h in sorted(hashes.items())).encode()
    ).hexdigest()[:12]
    lines = ["<!-- SYNC-STAMP", f"parent commit: {parent}", f"source digest: {digest}"]
    lines += [f"{k}: {h}" for k, h in sorted(hashes.items())]
    lines.append("-->")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the manual is stale")
    ap.add_argument(
        "--stage", action="store_true", help="git add the manual after rewriting (hook)"
    )
    args = ap.parse_args()

    lim = json.loads(LIMITS.read_text())
    old = MANUAL.read_text()
    hashes = {p: sha(ROOT / p) for p in WATCHED}
    prev = parse_stamp(old)
    changed = [p for p in WATCHED if prev.get(p) not in (None, hashes[p])]
    if prev and changed:
        print("sync_operators_manual: sources changed since the last sync: " + ", ".join(changed))

    errs, warns = verify(lim)
    for w in warns:
        print(f"sync_operators_manual: warning: {w}")
    if errs:
        for e in errs:
            print(f"sync_operators_manual: DRIFT: {e}", file=sys.stderr)
        print(
            "sync_operators_manual: fix the source above or edit current-specification/"
            "flight_limits.json (the single source), then recommit.",
            file=sys.stderr,
        )
        return 1

    E = _load_endurance()
    v = compute(lim, E)
    new, problems = render(old, v, blocks(v))
    for p in problems:
        print(f"sync_operators_manual: ERROR: {p}", file=sys.stderr)
    if problems:
        return 1
    for pat in RETIRED:
        stripped = STAMP_RE.sub("", new)
        if re.search(pat, stripped):
            print(
                f"sync_operators_manual: ERROR: retired value /{pat}/ in the manual",
                file=sys.stderr,
            )
            return 1

    parent = git("rev-parse", "--short", "HEAD")
    stamp = make_stamp(parent, hashes)
    if STAMP_RE.search(new):
        new = STAMP_RE.sub(lambda _m: stamp, new)
    else:
        new = new.replace("<!-- markdownlint-disable", f"{stamp}\n<!-- markdownlint-disable", 1)

    if args.check:
        # Compare without the stamp's parent line, which differs by construction.
        strip = lambda t: re.sub(r"parent commit: \S+\n", "", t)  # noqa: E731
        if strip(new) != strip(old):
            print(
                "sync_operators_manual: docs/OPERATORS_MANUAL.md is stale; run "
                "tools/sync_operators_manual.py",
                file=sys.stderr,
            )
            return 1
        print("sync_operators_manual: manual is current")
        return 0

    if new != old:
        MANUAL.write_text(new)
        print(
            f"sync_operators_manual: updated docs/OPERATORS_MANUAL.md "
            f"({len(changed)} source change(s); parent {parent})"
        )
    else:
        print("sync_operators_manual: manual already current")
    if args.stage:
        subprocess.run(["git", "add", str(MANUAL)], cwd=ROOT, check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
