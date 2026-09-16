#!/usr/bin/env python3
"""tilt_actuator_options.py -- the three nacelle-tilt actuator options, side by
side, with every number derived from a cited input and the flight-domain
consequences spelled out.  Rev T5 trade, 2026-09-15.

Why
---
The Rev T5 single-start worm (Option 1) closes WA-R16 (self-locking hold)
but delivers ~24 deg/s at the nacelle -- fine for a mode change, useless for
vectoring, and on a lateral tandem pair the tilt actuator IS the hover pitch
and yaw actuator.  This tool puts the three candidate drives through the same
arithmetic so the owner can pick a rate requirement (TILT-CTL-05) with the
consequences in front of them.

Options
-------
  1  Single-start worm 40:1 on a Pololu 20D 25:1 CB 6V gearmotor (as built
     in tilt_actuator_bracket.scad).  Self-locking.  Slow.
  2  Four-start worm 10:1 (m1, O24) on a Pololu 25D HP 6V 9.7:1 gearmotor.
     Back-drivable; holding = closed loop while powered + a spring-applied
     friction brake for the unpowered case (part not yet designed).  Fast.
  3  Rev T4 baseline: 38T/38T m0.8 spur 1:1 driven by a DS3225 body carrying
     LibreServo_v4 (rotation-limit pin removed), on the 18 mm standoff pads.
     Back-drivable; same brake need.  Fastest; fouls the battery cradle.

Inputs (REF-IDs in REFERENCES.md; ASSUMED where marked)
-------------------------------------------------------
  * nacelle inertia about the pivot I = 7.189e-4 kg.m^2 -- docs/TILT_SPAR_
    ANALYSIS.md SS2.1.2 (lumped, pre-T4 masses; understates by the parts' own
    inertia, overstates by the T4 pod hollowing -- carried as cited)
  * grounded tilt torque 0.177 N.m at the nacelle -- same doc SS2.1 (inertia
    at 145 deg/0.5 s x6 + gravity bound); aero moment UNQUANTIFIED (TILT-CTL-06)
  * tip stage 14T/50T, i = 3.571 -- docs/TILT_DRIVE_CONTROL_SPEC.md SS1.1
  * Pololu 20D 25:1 CB 6V: 570 rpm, 1.6 kgf.cm stall, 2.9 A, 44 g -- REF-ACT-001
  * Pololu 25D HP 6V 9.7:1: 1000 rpm no-load, 810 rpm / 4.5 kgf.mm at max
    efficiency, 23 kgf.mm stall, 6.0 A, 95-110 g with encoder -- REF-ACT-002
  * DS3225: 0.13 s/60 deg and 24.5 kgf.cm at 6.8 V, 60 g -- avionics/
    datasheets/DS3225 datasheet.pdf (REFERENCES.md DS3225 row)
  * worm friction mu = 0.20 (printed PETG wheel / brass or PETG worm, dry) --
    ASSUMED; friction angle 11.3 deg.  Self-locking iff lead angle < friction
    angle (REF-STD-GEAR-002)
  * hover thrust = weight, AUW 3,911 g (README.md Phase 5-10; MA-1 says this
    is under-counted -- both carried), nacelle lateral spacing 430 mm
    (HULL_FRAME_REFERENCE.md nacelle X extents), pivot Z +69.09 (drive shaft)
  * z_cg: NOT RECORDED (LG-29) -- pitch moment is given per mm of pivot-CG
    vertical offset

Run:
    /usr/bin/python3 tools/tilt_actuator_options.py             # table
    /usr/bin/python3 tools/tilt_actuator_options.py --write     # + docs/TILT_ACTUATOR_OPTIONS.md
                                                                #   + tilt_actuator_options_params.scad

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the
author's direction, 2026-09-15, per `AGENTS.md` §3 AI attribution.
License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
"""

import argparse
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))

G = 9.80665
KGFCM = 0.0980665           # N.m per kgf.cm
I_NAC = 7.189e-4            # kg.m^2, about the pivot (cited)
T_LOAD = 0.177              # N.m grounded requirement at the nacelle (cited)
I_TIP = 50.0 / 14.0         # 3.571
ETA_TIP = 0.95              # spur pair, ASSUMED
MU = 0.20                   # ASSUMED, dry printed pair
AUW_G = 3911.0
AUW_HI_G = 3911.0 + 521.6   # MA-1 under-count
SPAN_MM = 430.0             # nacelle-to-nacelle lateral spacing
PIVOT_Z = 69.09
SIGMA_PETG = 54.0           # MPa flexural, REF-MAT-002 (plain PETG floor)
LEWIS_Y = 0.40              # ASSUMED, 40T 20 deg
FOS = 4.0


def worm_eta(lead_deg, mu=MU, drive=True):
    phi = math.degrees(math.atan(mu))
    lam = math.radians(lead_deg)
    ph = math.radians(phi)
    if drive:
        return math.tan(lam) / math.tan(lam + ph)
    # back-driving efficiency (negative => self-locking)
    return math.tan(lam - ph) / math.tan(lam)


OPTIONS = {
    1: dict(
        name="Single-start worm 40:1 + Pololu 20D 25:1 CB 6V",
        motor="Pololu #3712 (20D, 25:1, CB, 6 V) + #5660 encoder",
        motor_rpm_nl=570.0, motor_rpm_eff=440.0, motor_stall_kgfcm=1.6,
        motor_stall_A=2.9, motor_mass_g=44.0 + 6.0, motor_d=20.0,
        stage="worm", starts=1, wheel_n=40, worm_pd=18.0, module=1.0,
        mech_mass_g=17.7 + 2.3 + 6.9 + 3.0,      # bracket + worm + wheel + M3/inserts
        shell_delta_g=-53.5 + 6 * 3.9,             # pads removed, 6 foot bosses added
        reach_x=-138.75,                           # motor inboard face, port
        battery_ok=True, hold_unpowered=True, brake_needed=False,
    ),
    2: dict(
        name="Four-start worm 10:1 + Pololu 25D HP 6V 9.7:1 + brake",
        motor="Pololu #1571 (25D, 9.7:1, HP, 6 V, no encoder; AEAT-8800 on the worm collar)",
        motor_rpm_nl=1000.0, motor_rpm_eff=810.0, motor_stall_kgfcm=2.3,
        motor_stall_A=6.0, motor_mass_g=90.0, motor_d=25.0,
        stage="worm", starts=4, wheel_n=40, worm_pd=24.0, module=1.0,
        mech_mass_g=20.0 + 4.0 + 6.9 + 3.0 + 12.0,  # bigger cradle, worm, wheel, hw, brake (EST)
        shell_delta_g=-53.5 + 6 * 3.9,
        reach_x=-142.75,                            # O25 body, worm PD 24 -> mid-plane -126.25
        battery_ok=True, hold_unpowered=False, brake_needed=True,
    ),
    3: dict(
        name="Spur 1:1 (38T/38T m0.8) + DS3225 multi-turn (Rev T4)",
        motor="DS3225 body + LibreServo_v4, limit pin removed (SERVO-TILT)",
        motor_rpm_nl=60.0 / 0.13 / 6.0, motor_rpm_eff=60.0 / 0.13 / 6.0 * 0.8,
        motor_stall_kgfcm=24.5, motor_stall_A=2.3, motor_mass_g=60.0, motor_d=20.0,
        stage="spur", starts=None, wheel_n=38, worm_pd=None, module=0.8,
        mech_mass_g=10.6 + 2 * 4.2 + 3.0 + 12.0,     # bracket, 2 gears, hw, brake (EST)
        shell_delta_g=0.0,                           # pads stay (32.9 g standoffs, MA-5)
        reach_x=-158.5,
        battery_ok=False, hold_unpowered=False, brake_needed=True,
    ),
    # Rev T5e (2026-09-16) -- the BUILT configuration.  Option 2's O25 body
    # cannot clear the O42 wheel for any C or worm angle (T5d-1: the gap is
    # WORM_PD/2 - MOTOR_D/2 - m), and the worm's inboard reach caps WORM_PD
    # at 26; a six-start worm on the slower 20D keeps TILT-CTL-07.
    4: dict(
        name="Six-start worm 6.67:1 + Pololu 20D 25:1 CB 6V + brake (Rev T5e, built)",
        motor="Pololu #3712 (20D, 25:1, CB, 6 V, no encoder; AEAT-8800 on the worm collar)",
        motor_rpm_nl=570.0, motor_rpm_eff=440.0, motor_stall_kgfcm=1.6,
        motor_stall_A=2.9, motor_mass_g=44.0, motor_d=20.0,
        stage="worm", starts=6, wheel_n=40, worm_pd=26.0, module=1.0,
        mech_mass_g=16.3 + 6.0 + 6.9 + 3.0 + 2.1 + 10.0,  # bracket, worm, wheel, hw, guide, solenoid+pin (EST)
        shell_delta_g=-53.5 + 6 * 3.9,
        reach_x=-139.25,                            # O26 worm tip, mid-plane -125.25
        battery_ok=True, hold_unpowered=False, brake_needed=True,
    ),
}


def analyse(o):
    r = dict(o)
    if o["stage"] == "worm":
        lead = math.degrees(math.atan(o["starts"] * o["module"] / o["worm_pd"]))
        ratio = o["wheel_n"] / o["starts"]
        eta = worm_eta(lead)
        eta_back = worm_eta(lead, drive=False)
        self_lock = eta_back <= 0.0
        # friction angle at which the lock is lost; below ~6 deg lead the
        # lock survives any plausible lubricated pair, above it the lock is
        # CONDITIONAL on staying dry (mu >= tan(lead))
        r.update(lead_deg=lead, eta=eta, eta_back=eta_back, self_lock=self_lock,
                 mu_min_lock=math.tan(math.radians(lead)))
        r["C_mm"] = (o["wheel_n"] * o["module"] + o["worm_pd"]) / 2
    else:
        ratio, eta, self_lock = 1.0, 0.95, False
        r.update(lead_deg=None, eta=eta, eta_back=eta, self_lock=False, C_mm=30.4)
    r["ratio_fuse"] = ratio
    r["ratio_total"] = ratio * I_TIP
    # torques
    t_stall = o["motor_stall_kgfcm"] * KGFCM
    r["T_shaft_stall"] = t_stall * ratio * eta
    r["T_nac_stall"] = r["T_shaft_stall"] * I_TIP * ETA_TIP
    r["T_margin_stall"] = r["T_nac_stall"] / T_LOAD
    # wheel / gear tooth limit (Lewis, FOS 4, plain PETG floor)
    b = 5.0 if o["stage"] == "worm" else 6.0
    F_allow = SIGMA_PETG * b * o["module"] * LEWIS_Y / FOS       # N
    pd = o["wheel_n"] * o["module"]
    r["T_shaft_tooth"] = F_allow * pd / 2 / 1000.0                # N.m
    r["T_nac_tooth"] = r["T_shaft_tooth"] * I_TIP * ETA_TIP
    r["T_nac_limit"] = min(r["T_nac_stall"], r["T_nac_tooth"])
    r["limit_by"] = "tooth (Lewis)" if r["T_nac_tooth"] < r["T_nac_stall"] else "motor stall"
    # rates
    for tag, rpm in (("nl", o["motor_rpm_nl"]), ("eff", o["motor_rpm_eff"])):
        r[f"rate_{tag}"] = rpm / r["ratio_total"] * 6.0            # deg/s at the nacelle
    # Acceleration.  The nacelle's own inertia (7.19e-4 kg.m^2) is NOT what
    # limits it: the motor rotor's inertia reflected through ratio^2 (a
    # 20D rotor ~1e-7 kg.m^2 class x 25^2 x 40^2 x 3.571^2 ~ 1.4 kg.m^2 at
    # the nacelle for Opt 1) swamps it, so the drive accelerates at the
    # MOTOR's mechanical time constant, tau_m.  Pololu does not publish
    # tau_m; a 20-40 ms class value is ASSUMED for all three and carried as
    # a fixed 0.03 s added to every rate-limited move.  What the load
    # inertia does set is the torque it costs: I*alpha at the nacelle.
    TAU_M = 0.03
    w_max = math.radians(r["rate_nl"])
    r["alpha"] = w_max / TAU_M                                      # rad/s^2, motor-limited
    r["T_inertia_nac"] = I_NAC * r["alpha"]                         # N.m to accelerate the nacelle
    for ang in (5.0, 15.0, 90.0, 145.0):
        r[f"t_{int(ang)}"] = math.radians(ang) / w_max + TAU_M
    # small-signal bandwidth proxy: a +/-5 deg sinusoid is rate-limited above
    # f = rate / (2*pi*A)
    r["f_5deg"] = r["rate_nl"] / (2 * math.pi * 5.0)
    r["f_2deg"] = r["rate_nl"] / (2 * math.pi * 2.0)
    # back-drive torque needed at the nacelle to move the motor (powered off)
    if o["stage"] == "worm" and r["self_lock"]:
        r["T_backdrive"] = float("inf")
    else:
        # motor cogging/friction unknown -> report the reflected stall as the
        # UPPER bound and 0 as the lower; the honest figure is a bench item
        r["T_backdrive"] = 0.0
    # aircraft-level authority at hover thrust = weight
    W = AUW_G / 1000.0 * G
    for d in (2.0, 5.0, 10.0):
        r[f"a_x_{int(d)}"] = G * math.sin(math.radians(d))          # m/s^2, both nacelles
        r[f"N_yaw_{int(d)}"] = W * math.sin(math.radians(d)) * SPAN_MM / 2 / 1000.0   # N.m diff tilt
        r[f"M_pitch_per_mm_{int(d)}"] = W * math.sin(math.radians(d)) / 1000.0        # N.m per mm of (z_pivot - z_cg)
    # masses
    r["mass_per_side"] = o["motor_mass_g"] + o["mech_mass_g"]
    r["mass_pair"] = 2 * r["mass_per_side"] + o["shell_delta_g"]
    r["current_pair_stall"] = 2 * o["motor_stall_A"]
    return r


def fmt(v, nd=2):
    if v == float("inf"):
        return "inf (self-locking)"
    return f"{v:.{nd}f}"


def table(res):
    rows = [
        ("Fuselage stage ratio", lambda r: f"{r['ratio_fuse']:.1f}:1 ({r['stage']}" + (f", lead {r['lead_deg']:.1f} deg)" if r['lead_deg'] else ")")),
        ("Total ratio actuator -> nacelle", lambda r: f"{r['ratio_total']:.1f}:1"),
        ("Stage efficiency (drive / back-drive)", lambda r: f"{r['eta']*100:.0f} % / " + ("locked" if r['eta_back'] <= 0 else f"{r['eta_back']*100:.0f} %")),
        ("Unpowered hold (WA-R16)", lambda r: ("YES by geometry (locked for mu >= %.2f)" % r["mu_min_lock"]) if r["hold_unpowered"]
            else (("CONDITIONAL -- locked only while mu >= %.2f (dry); brake required for the lubricated/vibration case" % r["mu_min_lock"]) if r.get("mu_min_lock") else "NO -- brake required (part TBD)")),
        ("Nacelle rate, no-load", lambda r: f"{r['rate_nl']:.0f} deg/s"),
        ("Nacelle rate, motor max-efficiency point", lambda r: f"{r['rate_eff']:.0f} deg/s"),
        ("Torque at nacelle, motor stall", lambda r: f"{r['T_nac_stall']:.2f} N.m ({r['T_nac_stall']/KGFCM:.1f} kgf.cm) = {r['T_margin_stall']:.0f}x the 0.177 N.m load"),
        ("Torque limit at nacelle (governing)", lambda r: f"{r['T_nac_limit']:.2f} N.m, by {r['limit_by']}"),
        ("Angular accel (motor-limited, tau_m 0.03 s ASSUMED)", lambda r: f"{r['alpha']:.0f} rad/s^2; nacelle inertia costs {r['T_inertia_nac']:.3f} N.m"),
        ("Time +/-5 deg / +/-15 deg / 90 deg / 145 deg", lambda r: f"{r['t_5']:.2f} / {r['t_15']:.2f} / {r['t_90']:.2f} / {r['t_145']:.2f} s"),
        ("Rate-limit bandwidth, +/-2 deg / +/-5 deg", lambda r: f"{r['f_2']:.1f} Hz / {r['f_5deg']:.1f} Hz" if 'f_2' in r else f"{r['f_2deg']:.1f} Hz / {r['f_5deg']:.1f} Hz"),
        ("Motor inboard reach (port, hull X)", lambda r: f"{r['reach_x']:.1f} mm"),
        ("Battery cradle (X -197..-142) clear?", lambda r: "yes" if r["battery_ok"] else "NO -- 13.6 mm overlap"),
        ("Mass per side (motor + mechanism)", lambda r: f"{r['mass_per_side']:.0f} g"),
        ("Mass, both sides incl. shell delta", lambda r: f"{r['mass_pair']:+.0f} g vs Rev T4 shell"),
        ("Stall current, both motors (6 V bus)", lambda r: f"{r['current_pair_stall']:.1f} A"),
    ]
    hdr = "| Metric | " + " | ".join(f"Opt {k}" for k in res) + " |"
    sep = "|---|" + "---|" * len(res)
    out = [hdr, sep]
    for label, f in rows:
        out.append(f"| {label} | " + " | ".join(f(r) for r in res.values()) + " |")
    return "\n".join(out)


def domains(res):
    r1 = next(iter(res.values()))
    lines = [
        "| Flight domain | What the actuator must do | " + " | ".join(f"Opt {k}" for k in res) + " |",
        "|---|---|" + "---|" * len(res),
    ]
    def row(label, need, key):
        lines.append(f"| {label} | {need} | " + " | ".join(key(r) for r in res.values()) + " |")
    row("Hover attitude (pitch/yaw by vectoring)", "small +/-2..5 deg moves at a few Hz",
        lambda r: f"{r['f_5deg']:.1f} Hz @5 deg, {r['rate_nl']:.0f} deg/s")
    row("Hover translate (2/5/10 deg collective tilt)", f"a_x = {r1['a_x_2']:.2f}/{r1['a_x_5']:.2f}/{r1['a_x_10']:.2f} m/s^2 (all options, thrust-limited)",
        lambda r: f"reach 5 deg in {r['t_5']:.2f} s")
    row("Hover yaw (differential +/-5 deg)", f"N = {r1['N_yaw_5']:.2f} N.m at AUW {AUW_G:.0f} g",
        lambda r: f"{r['t_5']:.2f} s to command")
    row("Transition 0 -> 90 deg", "monotonic, iris scheduled (nozzle_linkage_check.py)",
        lambda r: f"{r['t_90']:.1f} s")
    row("Full sweep -5 -> 140 deg", "no requirement recorded (TILT-CTL-05)",
        lambda r: f"{r['t_145']:.1f} s")
    row("Cruise hold, powered", "hold against aero moment (unquantified, TILT-CTL-06)",
        lambda r: f"{r['T_nac_limit']:.1f} N.m available")
    row("Loss of actuator power", "hold (TILT_DRIVE_CONTROL_SPEC SS5.2)",
        lambda r: "holds (self-locking)" if r["hold_unpowered"] else ("holds only if dry (mu >= %.2f); brake required" % r["mu_min_lock"] if r.get("mu_min_lock") else "free -- brake required"))
    row("Hard landing 2.5 g", "inertial load nulled by pivot-at-CG; train sees 0.177 N.m bound",
        lambda r: f"{r['T_margin_stall']:.0f}x margin")
    return "\n".join(lines)


def write_scad(res, path):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("// tilt_actuator_options_params.scad -- GENERATED by tools/tilt_actuator_options.py\n"
                 "// --write.  Per-option geometry for tilt_actuator_options.scad.  Do not edit.\n"
                 "// License: CC BY 4.0\n")
        fh.write("OPT_MOTOR_D    = [0, %s];\n" % ", ".join(f"{r['motor_d']:.1f}" for r in res.values()))
        fh.write("OPT_WORM_PD    = [0, %s];\n" % ", ".join(f"{(r['worm_pd'] or 0):.1f}" for r in res.values()))
        fh.write("OPT_STARTS     = [0, %s];\n" % ", ".join(f"{(r['starts'] or 0)}" for r in res.values()))
        fh.write("OPT_WHEEL_N    = [0, %s];\n" % ", ".join(f"{r['wheel_n']}" for r in res.values()))
        fh.write("OPT_MODULE     = [0, %s];\n" % ", ".join(f"{r['module']:.2f}" for r in res.values()))
        fh.write("OPT_C          = [0, %s];\n" % ", ".join(f"{r['C_mm']:.2f}" for r in res.values()))
        fh.write("OPT_RATE_NL    = [0, %s];\n" % ", ".join(f"{r['rate_nl']:.1f}" for r in res.values()))
        fh.write("OPT_T_NAC      = [0, %s];\n" % ", ".join(f"{r['T_nac_limit']:.2f}" for r in res.values()))
        fh.write("OPT_MASS_PAIR  = [0, %s];\n" % ", ".join(f"{r['mass_pair']:.0f}" for r in res.values()))
        fh.write("OPT_T145       = [0, %s];\n" % ", ".join(f"{r['t_145']:.2f}" for r in res.values()))
        fh.write("OPT_T5         = [0, %s];\n" % ", ".join(f"{r['t_5']:.2f}" for r in res.values()))
        fh.write("OPT_LOCK       = [0, %s];\n" % ", ".join("true" if r["hold_unpowered"] else "false" for r in res.values()))
        fh.write("OPT_NAME       = [\"\", %s];\n" % ", ".join(f"\"{r['name']}\"" for r in res.values()))


def write_doc(res, path):
    body = f"""# Nacelle-Tilt Actuator Options — Rev T5 trade (GENERATED)

**Generated by** `tools/tilt_actuator_options.py --write` on 2026-09-16.
Edit the tool, not this file.  Geometry for each option renders from
`airframe/openscad/fuselage/cargo/tilt_actuator_options.scad` (`OPTION = 1|2|3|4`).

**Option 4 is the built configuration (Rev T5e, 2026-09-16).**  Option 2 was
the 2026-09-15 selection; it was retired the next day by finding T5d-1: a
motor coaxial with its worm clears the wheel tip by `WORM_PD/2 − MOTOR_D/2 − m`
whatever the centre distance or the worm's angle on the wheel, and the worm's
inboard reach against the battery cradle caps `WORM_PD` at 26 mm — so a Ø25
body can never clear the Ø42 wheel by more than −1.5 mm and a Ø20 body clears
it by 2.0 mm.  A six-start worm on the slower 20D keeps TILT-CTL-07.

> ⚠️ **ENGINEERING REVIEW REQUIRED** — every figure here is a derived estimate
> from the cited inputs listed in the tool's docstring; the aero moment about
> the tilt axis is unquantified (TILT-CTL-06), the nacelle inertia is the
> lumped pre-T4 figure, and the worm friction coefficient is ASSUMED 0.20.

## Options

1. **{res[1]['name']}** — {res[1]['motor']}.
2. **{res[2]['name']}** — {res[2]['motor']}.
3. **{res[3]['name']}** — {res[3]['motor']}.
4. **{res[4]['name']}** — {res[4]['motor']}.

## Views (from `tilt_actuator_options.scad`, `OPTION = n`)

| Option 1 | Option 2 | Option 3 | Option 4 (built) |
|---|---|---|---|
| ![opt1](img/tilt_option_1_front.png) | ![opt2](img/tilt_option_2_front.png) | ![opt3](img/tilt_option_3_front.png) | ![opt4](img/tilt_option_4_front.png) |
| ![opt1 iso](img/tilt_option_1_iso.png) | ![opt2 iso](img/tilt_option_2_iso.png) | ![opt3 iso](img/tilt_option_3_iso.png) | ![opt4 iso](img/tilt_option_4_iso.png) |

Looking aft from ahead: grey = hull ring sections at Y −10/20/46.6/80, brown =
root-flange keep-out, gold = battery in its cradle, green = mission payload at
the door crown, black lines = bridle hoist lines, blue = wheel on the drive
shaft, dark grey = motor, red = brake envelope (Opt 2/3) or overlap (Opt 3).

## Clearances (tools/cargo_layout_fit.py)

* Opt 1: `--option 1` PASS — every envelope 0 mm³ hit, ≥ 3 mm gap.
* Opt 2: `--option 2` — wheel, worm, battery clear; the Ø25 body reads
  50 mm³ inside the 3 mm gap at the bracket foot bosses (feet 0/1 must rise
  ~4 mm for this option).  Fits.
* Opt 3: DS3225 body X −158.5 overlaps the battery cradle (X ≥ −197.25) by
  13.6 mm on each side — does not fit with the Rev T5 battery station.
* Opt 4: the baseline of `tools/cargo_layout_fit.py` — PASS 2026-09-16 against
  the re-merged Rev T5e shell with the controller boards, chin nodes, chin
  shelf and Observer tray as envelopes; motor-to-wheel-tip 2.0 mm (both
  bracket-located; accepted in place of the 3 mm moving-part budget).

## Numbers

{table(res)}

Mass basis: motor mass from the datasheets; mechanism masses are the exported
STL volumes × 1.05 g/cm³ (Opt 1), scaled estimates (Opt 2 cradle, brake 12 g
EST), the Rev T4 BOM rows (Opt 3) and the exported Rev T5e STLs (Opt 4:
bracket 16.3, worm 6.0, wheel 6.9, guide 2.1 g; solenoid + pin 10 g EST).  Shell delta: the two DS3225 standoff
pads measure 53.5 g in the published Rev T4 shell; six 12 × 12 mm foot bosses
add 3.9 g each.

## Flight domains

{domains(res)}

Aircraft-level authority is thrust-limited and identical for all options —
what differs is how fast the command arrives.  Pitch moment from a collective
tilt δ is `W·sin δ · (z_pivot − z_cg)`; z_cg is not recorded (LG-29), so at
5° it is {res[1]['M_pitch_per_mm_5']:.3f} N·m per mm of vertical offset.

## Reading the table

* **Opt 1** holds unpowered by geometry and is the lightest, but at
  {res[1]['rate_nl']:.0f} deg/s it takes {res[1]['t_5']:.2f} s to move 5° — a
  {res[1]['f_5deg']:.1f} Hz rate limit.  That is a mode-change actuator, not a
  vectoring one.
* **Opt 2** keeps the Rev T5 packaging (motor along the wall, battery clear)
  and gives {res[2]['rate_nl']:.0f} deg/s, but the 4-start lead ({res[2]['lead_deg']:.1f}°)
  is above the friction angle, so the unpowered hold has to come from a brake
  that does not yet exist, and the 25D motor doubles the stall current.
* **Opt 3** is the fastest ({res[3]['rate_nl']:.0f} deg/s) and the most
  torque, but its body reaches to X {res[3]['reach_x']:.1f} — through the
  battery cradle — and it too needs a brake.

## Open items this trade creates

* TILT-CTL-05: adopt a nacelle rate / bandwidth requirement (owner).
* Brake design for Opt 2/3 (spring-applied, solenoid-released, on the drive
  shaft or the worm shaft).
* Bench: motor rotor inertia and worm friction — both neglected/assumed here.
"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    res = {k: analyse(o) for k, o in OPTIONS.items()}
    print(table(res))
    print()
    print(domains(res))
    if a.write:
        p1 = os.path.join(REPO, "airframe", "openscad", "fuselage", "cargo",
                          "tilt_actuator_options_params.scad")
        p2 = os.path.join(REPO, "docs", "TILT_ACTUATOR_OPTIONS.md")
        write_scad(res, p1)
        write_doc(res, p2)
        print("wrote", os.path.relpath(p1, REPO), "and", os.path.relpath(p2, REPO))


if __name__ == "__main__":
    main()
