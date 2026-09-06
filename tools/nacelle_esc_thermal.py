#!/usr/bin/env python3
"""
nacelle_esc_thermal.py — where does the ESC heat go, and does any path work?

THE QUESTION
------------
Rev T4c put two Open-Secure-ESC boards into each nacelle, in bays cut into the
annulus of a printed CF-PETG pod.  The bay is a pocket in plastic.  A 50 A ESC
dissipating tens of watts into a pocket in plastic is a thermal problem that has
never been sized in this repository, and the covers' louvres were built as "a
route and an area, not a verified heat path" — that sentence is what this tool
exists to replace.

The owner's proposal is the reason it is worth doing properly: the 11-vane
STATOR SLEEVE has by far the largest forced-air wetted area of any part in the
pod, so it is the obvious heat sink.  That instinct is right about the SINK and
the analysis below confirms it — 0.25 K/W of convective resistance, which is
excellent.  **The sink was never the problem.  The path to it is.**

THERMAL CONDUCTIVITY OF CF-PETG — WHAT THIS REPOSITORY ACTUALLY KNOWS
---------------------------------------------------------------------
**Nothing.**  REF-MAT-002 is a mechanical-properties paper (ASTM D790/D695/
D648): flexural strength, modulus, hardness, Vicat, HDT.  It publishes no
thermal conductivity, and no other source in this repository does either.  A
figure of 0.25 W/m·K was quoted in `airframe/wings-nacelles/WBS.md` on
2026-09-06; it was an unsourced estimate stated as though established, and it is
corrected by this tool rather than repeated.

So k is swept, not assumed.  The plausible band, with reasoning:

    neat PETG                       ~0.20 W/m·K   (typical amorphous thermoplastic)
    20 % chopped CF, THROUGH-plane  ~0.25-0.45    fibres align IN-plane during
                                                  extrusion, so the through-plane
                                                  gain over neat resin is small
    20 % chopped CF, IN-plane       ~0.5-1.0      the fibres' own axis
    FDM porosity                    reduces both

The bay-floor path is THROUGH-plane — heat crosses the wall, not along it — so
the low end governs.  **The sweep below runs 0.15 to 1.20 W/m·K, and the
conclusion does not change anywhere in that range.**  That is the honest way to
answer a question whose input datum does not exist: show the answer is
insensitive to it.  A measured value would sharpen the numbers; it would not
change the decision.

LOAD CASE
---------
Dissipation is taken from Open-Secure-ESC's own copper sizing
(`docs/design-single-end-wire-egress-variant.md` §7, run 2026-08-31), not
re-derived here:

    six TPHR8504PL FETs, conduction   10.50 W at 50 A   (6 x 1.75 W)
    three phase pours, 2 oz            6.67 W at 50 A
    pour-edge gap fill, 7.5 mm         4.55 W at 50 A
    ---------------------------------------------------
    total                             21.72 W at 50 A

All three are I^2 R terms, so they scale with the square of current.  Hover is
28 A per ESC nominal (`docs/POWER_DISTRIBUTION.md`).

TWO THINGS THAT MAKE THIS OPTIMISTIC, both stated rather than buried:

1. **Switching loss is not in the 21.72 W.**  Those are conduction figures only.
   Switching loss does not scale as I^2 and is not published for this design.
2. **RDS(on) roughly doubles from 25 C to 125 C.**  The 1.75 W/FET is computed at
   the 0.7 mOhm typical (VGS = 10 V, 25 C).  A hot FET dissipates more, which
   makes it hotter — a positive feedback this steady-state network does not
   model.  Any design that lands close to the limit here is not close, it is
   over it.

Usage:
    /usr/bin/python3 tools/nacelle_esc_thermal.py
    /usr/bin/python3 tools/nacelle_esc_thermal.py --current 50 --verbose

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
Analysis and tool by Claude (Claude Opus 5, Anthropic) under the author's
direction, per AGENTS.md S3 "Attribution and Licensing".
License: CC BY 4.0 - creativecommons.org/licenses/by/4.0
"""

from __future__ import annotations

import argparse
import math
import sys

# ── FET, from the Toshiba datasheet (primary source) ─────────────────────────
# TPHR8504PL_datasheet_en_20191024.pdf, section 5 "Thermal Characteristics" and
# the electrical table.  Read directly from the PDF, not quoted from memory.
FET_RTH_CH_C = 0.88      # [K/W] channel-to-case, max, Tc = 25 C
FET_RTH_CH_A = 50.0      # [K/W] channel-to-ambient on glass-epoxy board (a)
FET_TCH_MAX = 175.0      # [C]   absolute channel temperature limit
FET_N = 6                # [count] FETs per ESC
FET_RDSON = 0.7e-3       # [ohm] typical, VGS = 10 V, ID = 50 A, 25 C

#: Design limit for the channel, as a fraction of the absolute maximum.  This is
#: an ENGINEERING JUDGEMENT declared here, not a code value: 125 C leaves 50 C of
#: margin on a 175 C part, which covers the RDS(on) feedback and the switching
#: loss that this model omits.
T_CH_DESIGN = 125.0

# ── Dissipation, from Open-Secure-ESC docs S7 ────────────────────────────────
P_FET_50A = 10.50        # [W] six FETs, conduction
P_POUR_50A = 6.67        # [W] three phase pours at 2 oz
P_GAP_50A = 4.55         # [W] pour-edge gap fill at 7.5 mm
I_REF = 50.0             # [A] the current those figures are quoted at
I_HOVER = 28.0           # [A] per ESC, sustained hover (POWER_DISTRIBUTION.md)

# ── Air ──────────────────────────────────────────────────────────────────────
RHO_AIR = 1.225          # [kg/m3] ISA sea level
K_AIR = 0.0263           # [W/m.K] at ~25 C
MU_AIR = 1.81e-5         # [Pa.s]
CP_AIR = 1005.0          # [J/kg.K]
PR_AIR = 0.71
T_AMBIENT = 25.0         # [C] design ambient

# ── Pod geometry (nacelle_pod_50mm_tandem.scad / edf_stator_sleeve.scad) ─────
ESC_W_POWER = 23.0e-3    # [m] power panel width — the conducting footprint
ESC_LEN = 62.0e-3        # [m] board length
BOARD_AREA = 2046e-6     # [m2] folded board area, one face
POD_DUCT_WALL = 2.5e-3   # [m] pod duct wall, r 27.7 -> 30.2
SLEEVE_WALL = 2.5e-3     # [m] stator sleeve wall, r 25 -> 27.5
FIT_GAP = 0.2e-3         # [m] radial air gap, sleeve OD 27.5 in a 27.7 bore
BAY_GAP = 4.0e-3         # [m] radial height of the bay cavity
BAY_WIDTH = 33.0e-3      # [m] folded board width

#: The cooling circuit's duct-side ports, mirrored from nacelle_esc_bay.scad.
#: They are the THROAT: 95 mm2 against 144 mm2 of skin-side louvre, so the
#: circuit is set by these and the louvres cannot choke it.
ESC_BLEED_N = 4
ESC_BLEED_D = 5.5e-3     # [m]

# ── EDF (BOM EDF-50-6S, XFly Galaxy X5 2627-KV3200) ──────────────────────────
EDF_THRUST_N = 12.16     # [N] 1240 gf per unit, static
NACELLE_THRUST_N = 21.84 # [N] 4.91 lbf per nacelle = 2 x 2.73 lbf x 0.90 stator
                         #     efficiency (nacelle_pod_50mm_tandem.scad header)
DUCT_AREA = math.pi * 0.025 ** 2   # [m2] Ø50 bore

#: Fraction of the total static pressure rise contributed by the FORWARD fan.
#: ASSUMED 0.5 — the two EDFs are the same unit and the header credits them with
#: equal thrust.  The sensitivity is reported rather than hidden, because this
#: assumption sets how far below ambient the inter-stage sits.
FWD_STAGE_FRACTION = 0.5

#: Cooling-circuit loss coefficient, in velocity heads on the throat.  ASSUMED
#: K = 3: roughly one head for the skin inlet, one for the bay and its turns, one
#: for the discharge.  This is the number a bench flow test or CFD would replace,
#: and it is the weakest input to the flow rate below.
CIRCUIT_K = 3.0

# ── Materials ────────────────────────────────────────────────────────────────
K_ALUMINIUM = 167.0      # [W/m.K] 6061-T6, typical
K_TIM = 3.0              # [W/m.K] typical filled silicone thermal pad
RHO_CF_PETG = 1.05e-3    # [g/mm3] repo bulk printed density
RHO_AL = 2.70e-3         # [g/mm3]


def dissipation(current_a: float) -> float:
    """Total ESC conduction loss at a given phase current.  I^2 R scaling."""
    return (P_FET_50A + P_POUR_50A + P_GAP_50A) * (current_a / I_REF) ** 2


def duct_velocity() -> float:
    """Duct velocity in hover, from momentum theory for a DUCTED fan.

    A constant-area duct discharging to ambient does not contract its wake, so
    the exit area equals the duct area and

        T = m_dot . Ve = rho . A . Ve^2   ->   Ve = sqrt(T / (rho.A))

    This is NOT the open-rotor actuator-disc result (v_h = sqrt(T/2.rho.A),
    references/propulsion.md S1), which assumes a contracting slipstream.  Using
    the open-rotor form here would overstate the velocity by sqrt(2).
    """
    return math.sqrt(NACELLE_THRUST_N / (RHO_AIR * DUCT_AREA))


def duct_stations() -> dict:
    """Static pressure at each duct station in hover, relative to ambient.

    THIS IS THE ANALYSIS THAT OVERTURNS THE REV T4d COOLING CIRCUIT.

    Incompressible, one-dimensional, bellmouth inlet (no separation loss), duct
    of constant area A discharging as a free jet:

        station 0  far field          V = 0     p = p0
        station 1  duct inlet         V = Ve    p = p0 - 0.5.rho.Ve^2
        ---- forward fan adds dp1 ----
        station 2  inter-stage        V = Ve    p = p1 + dp1
        ---- aft fan adds dp2 ----
        station 3  nozzle exit        V = Ve    p = p0     (free jet)

    Because station 3 is back at ambient and station 1 is below it, the fans'
    combined rise is exactly the inlet's dynamic head, and **every station inside
    the duct is at or below ambient**.  There is nowhere in this duct to bleed
    FROM.  A cooling circuit that takes air from the duct and vents it to the
    skin is not merely expensive — it flows backwards.

    Note the pressure rise accounts for only part of the thrust:
    dp_fan x A is the FAN's share, and the balance is inlet-lip suction
    (references/propulsion.md S3, "total thrust is fan thrust plus duct
    thrust").  Sizing a bleed from thrust/area conflates the two and overstates
    the available pressure by about 2x — which is the error this corrects.
    """
    ve = duct_velocity()
    q = 0.5 * RHO_AIR * ve ** 2
    dp_total = q                     # fans must restore the inlet depression
    dp_fwd = dp_total * FWD_STAGE_FRACTION
    return {
        "Ve": ve,
        "q": q,
        "dp_fan_total": dp_total,
        "p1_gauge": -q,                       # duct inlet, pre-fwd-fan
        "p2_gauge": -q + dp_fwd,              # inter-stage = AFT FAN INLET
        "p3_gauge": 0.0,                      # nozzle exit
        "fan_thrust": dp_total * DUCT_AREA,   # the fans' share
        "lip_thrust": NACELLE_THRUST_N - dp_total * DUCT_AREA,
        "mdot": RHO_AIR * DUCT_AREA * ve,
    }


def aspirated_flow(dp_drive: float, throat_area: float) -> tuple[float, float]:
    """Cooling mass flow and bay velocity for a given driving depression."""
    v_throat = math.sqrt(2 * dp_drive / (RHO_AIR * CIRCUIT_K))
    mdot = RHO_AIR * throat_area * v_throat
    v_bay = mdot / (RHO_AIR * BAY_GAP * BAY_WIDTH)
    return mdot, v_bay


def h_flat_plate(velocity: float, length: float) -> tuple[float, float, str]:
    """Convection coefficient on a flat plate, with the correlation named.

    Laminar below Re 5e5 (Blasius/Pohlhausen average), turbulent above.  Both are
    the standard flat-plate correlations; they are used because the vanes and the
    board are short plates in an external-type flow, not fully developed duct
    flow.  Returns (h, Re, which correlation).
    """
    re = RHO_AIR * velocity * length / MU_AIR
    if re < 5e5:
        nu = 0.664 * re ** 0.5 * PR_AIR ** (1 / 3)
        law = "laminar  Nu = 0.664 Re^0.5 Pr^(1/3)"
    else:
        nu = 0.037 * re ** 0.8 * PR_AIR ** (1 / 3)
        law = "turbulent Nu = 0.037 Re^0.8 Pr^(1/3)"
    return nu * K_AIR / length, re, law


def stator_wetted_area() -> float:
    """Wetted area of the stator sleeve in the duct flow, m2.

    11 twisted vanes spanning r 7 -> 26 mm over 25 mm of axial length, both
    faces; the twist (VANE_ANGLE_DEG 33) lengthens the surface by 1/cos(33).
    Plus the hub OD and the sleeve bore wall.
    """
    n_fins, r_in, r_out = 11, 7e-3, 26e-3
    axial, twist_deg = 25e-3, 33.0
    surf_len = axial / math.cos(math.radians(twist_deg))
    vanes = n_fins * 2 * (r_out - r_in) * surf_len
    hub = math.pi * 16e-3 * axial
    bore = math.pi * 50e-3 * 32.5e-3
    return vanes + hub + bore


def report(title: str, rows, note: str = "") -> None:
    print(f"\n{title}")
    print("  " + "-" * 74)
    total = 0.0
    for label, r in rows:
        total += r
        print(f"  {label:<52}{r:9.3f} K/W")
    print(f"  {'TOTAL':<52}{total:9.3f} K/W")
    if note:
        print(f"  {note}")
    return total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--current", type=float, default=None,
                    help="phase current per ESC, A (default: both hover and max)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    print("Serenity nacelle ESC thermal — where does the heat go?\n")
    v_duct = duct_velocity()
    a_stator = stator_wetted_area()
    h_stator, re_s, law_s = h_flat_plate(v_duct, 30e-3)

    print(f"  duct jet velocity            {v_duct:6.1f} m/s "
          f"(from T = rho.A.Ve^2, T = {EDF_THRUST_N} N over Ø50)")
    print(f"  stator wetted area           {a_stator * 1e6:6.0f} mm2 "
          f"= {a_stator * 1e4:.1f} cm2")
    print(f"  stator h                     {h_stator:6.0f} W/m2.K   [{law_s}, "
          f"Re {re_s:,.0f}]")
    r_stator_conv = 1.0 / (h_stator * a_stator)
    print(f"  stator convective resistance {r_stator_conv:6.3f} K/W   "
          f"<-- the sink is EXCELLENT; that was never the problem")

    i_hover = args.current if args.current else I_HOVER
    i_max = args.current if args.current else I_REF

    # ---------------------------------------------------------------- paths
    a_cond = ESC_W_POWER * ESC_LEN          # conducting footprint under the board
    print(f"\n  conducting footprint         {a_cond * 1e6:6.0f} mm2 "
          f"(23 x 62 power panel)")

    print("\n" + "=" * 78)
    print("A.  CONDUCT INTO THE STATOR SLEEVE — as built, all CF-PETG")
    print("=" * 78)
    print("  Swept over the whole plausible k, because this repository has no")
    print("  measured value.  The verdict is the same at every point in the band.")
    print(f"\n  {'k (W/m.K)':>10}{'pod wall':>11}{'air gap':>10}{'sleeve':>10}"
          f"{'stator':>10}{'TOTAL':>10}{'dT @21.7W':>12}")
    r_gap = FIT_GAP / (K_AIR * a_cond)
    for k in (0.15, 0.25, 0.40, 0.60, 1.20):
        r_pod = POD_DUCT_WALL / (k * a_cond)
        r_slv = SLEEVE_WALL / (k * a_cond)
        tot = r_pod + r_gap + r_slv + r_stator_conv
        print(f"  {k:>10.2f}{r_pod:>11.2f}{r_gap:>10.2f}{r_slv:>10.2f}"
              f"{r_stator_conv:>10.2f}{tot:>10.2f}{tot * 21.72:>11.0f} K")
    print(f"\n  The 0.2 mm AIR GAP alone is {r_gap:.2f} K/W — more than the stator")
    print("  sink and the pod wall combined at k = 1.2.  It is a running fit the")
    print("  sleeve has to slide through on its keys, so it cannot simply be")
    print("  filled: a thermal pad across a sliding joint shears on every service.")

    print("\n" + "=" * 78)
    print("B.  SAME PATH, ALUMINIUM WALLS + THERMAL PAD IN THE GAP")
    print("=" * 78)
    r_pod_al = POD_DUCT_WALL / (K_ALUMINIUM * a_cond)
    r_slv_al = SLEEVE_WALL / (K_ALUMINIUM * a_cond)
    r_tim = FIT_GAP / (K_TIM * a_cond)
    # Circumferential spreading in a 2.5 mm sleeve wall: heat enters over the
    # board's arc and must reach vanes distributed round 360 deg.  Modelled as
    # conduction along the wall to the mean vane, half the circumference away.
    arc = math.pi * 0.0263          # mean sleeve radius 26.3 mm
    r_spread = (arc / 4) / (K_ALUMINIUM * SLEEVE_WALL * 32.5e-3)
    report("  resistance chain",
           [("pod duct wall, 2.5 mm 6061", r_pod_al),
            ("thermal pad, 0.2 mm k=3", r_tim),
            ("sleeve wall, 2.5 mm 6061", r_slv_al),
            ("circumferential spreading to the vanes", r_spread),
            ("stator vanes to duct air", r_stator_conv)])
    r_b = r_pod_al + r_tim + r_slv_al + r_spread + r_stator_conv

    print("\n" + "=" * 78)
    print("C.  ASPIRATED COOLING — external skin inlet, discharge into the duct")
    print("=" * 78)
    st = duct_stations()
    print(f"  duct velocity (ducted-fan momentum theory) {st['Ve']:7.1f} m/s")
    print(f"  duct mass flow                             {st['mdot']:7.3f} kg/s")
    print(f"  fans' pressure rise                        {st['dp_fan_total']:7.0f} Pa")
    print(f"  of the {NACELLE_THRUST_N:.1f} N nacelle thrust: "
          f"{st['fan_thrust']:.1f} N from fan pressure, "
          f"{st['lip_thrust']:.1f} N from inlet-lip suction")
    print("\n  STATIC PRESSURE, gauge (relative to ambient):")
    for label, key in (("station 1  duct inlet, pre-fwd-fan", "p1_gauge"),
                       ("station 2  INTER-STAGE = aft-fan inlet", "p2_gauge"),
                       ("station 3  nozzle exit (free jet)", "p3_gauge")):
        print(f"    {label:<42}{st[key]:+8.0f} Pa")
    print("\n  Every station is at or below ambient.  THERE IS NOWHERE IN THIS")
    print("  DUCT TO BLEED FROM.  The inter-stage sits "
          f"{-st['p2_gauge']:.0f} Pa BELOW ambient, so")
    print("  it is a SUCTION source, not a pressure source — which is exactly")
    print("  what an aspirated cooling circuit wants.\n")

    throat = ESC_BLEED_N * math.pi * (ESC_BLEED_D / 2) ** 2
    print(f"  circuit throat (the duct-side holes) {throat * 1e6:6.0f} mm2 "
          f"at K = {CIRCUIT_K:.1f}")
    print(f"\n  {'throttle':>9}{'dp drive':>11}{'mdot':>11}{'bay V':>9}"
          f"{'% duct':>9}{'h':>8}{'R_conv':>9}")
    best_c = None
    for frac, name in ((1.00, "100 %"), (0.70, "70 %"), (0.50, "50 %")):
        # driving depression scales with Ve^2, i.e. with thrust, i.e. throttle
        dp = -st["p2_gauge"] * frac
        mdot, v_bay = aspirated_flow(dp, throat)
        h_b, _, _ = h_flat_plate(v_bay, ESC_LEN)
        r_conv = 1.0 / (h_b * 2 * BOARD_AREA)
        print(f"  {name:>9}{dp:>10.0f} Pa{mdot * 1e3:>9.2f} g/s{v_bay:>8.1f}"
              f"{100 * mdot / st['mdot']:>8.2f}%{h_b:>8.0f}{r_conv:>9.2f}")
        if frac == 1.0:
            best_c = (r_conv, mdot, 100 * mdot / st["mdot"])

    print("\n  THRUST COST.  The cooling air is INGESTED and then pumped by the")
    print("  aft fan, so it leaves with the jet and carries its own momentum out.")
    print("  What it misses is the FORWARD fan's work — it bypasses that stage —")
    print("  so the cost is the forward stage's share of the bypassed flow:")
    bypass = best_c[2] / 100.0
    cost_n = bypass * st["fan_thrust"] * FWD_STAGE_FRACTION \
        + bypass * st["lip_thrust"] * FWD_STAGE_FRACTION
    print(f"    bypass fraction              {100 * bypass:5.2f} % of duct flow")
    print(f"    thrust cost                  {cost_n:5.3f} N = "
          f"{100 * cost_n / NACELLE_THRUST_N:.2f} % of nacelle thrust")
    print("\n  Against the DISCARD circuit (take duct air, vent it to the skin):")
    print("    that air has been worked on and is then thrown away, so the whole")
    print(f"    bypassed momentum is lost — {100 * bypass * 2:.2f} % — and it cannot")
    print("    flow anyway, because the duct is below ambient everywhere.")

    print("\n" + "=" * 78)
    print("VERDICT — channel temperature at the design points")
    print("=" * 78)
    r_board = FET_RTH_CH_A / FET_N   # six FETs sharing one board, to local air
    print(f"  board-to-local-air, {FET_N} FETs in parallel on one board: "
          f"{r_board:.2f} K/W")
    print("  (Toshiba Rth(ch-a) = 50 K/W per FET on glass-epoxy board (a).  This")
    print("   already ASSUMES free air around the board — in a sealed bay there")
    print("   is none, which is why option A fails before its own path does.)\n")
    print(f"  {'case':<44}{f'{i_hover:.0f} A hover':>13}"
          f"{f'{i_max:.0f} A max':>13}")
    print("  " + "-" * 70)
    cases = [
        ("A  sealed bay, CF-PETG @ k=0.25", r_board
         + POD_DUCT_WALL / (0.25 * a_cond) + r_gap
         + SLEEVE_WALL / (0.25 * a_cond) + r_stator_conv),
        ("B  aluminium path to the stator + TIM", r_board + r_b),
        ("C  aspirated, skin inlet -> duct suction", r_board * 0.35 + best_c[0]),
    ]
    for label, r in cases:
        t_hov = T_AMBIENT + r * dissipation(i_hover)
        t_max = T_AMBIENT + r * dissipation(i_max)
        f_h = "OK " if t_hov <= T_CH_DESIGN else "OVER"
        f_m = "OK " if t_max <= T_CH_DESIGN else "OVER"
        print(f"  {label:<44}{t_hov:>8.0f} C {f_h}{t_max:>8.0f} C {f_m}")
    print(f"\n  dissipation: {dissipation(i_hover):.2f} W at {i_hover:.0f} A, "
          f"{dissipation(i_max):.2f} W at {i_max:.0f} A")
    print(f"  design limit {T_CH_DESIGN:.0f} C (declared judgement) against a "
          f"{FET_TCH_MAX:.0f} C absolute maximum")

    print("\n  Option C's board resistance is scaled by 0.35 because forced")
    print("  convection replaces the datasheet's natural-convection figure; that")
    print("  factor is an ESTIMATE and is the weakest number in this tool.")

    # ---------------------------------------------------------- mass of B
    sleeve_vol = 29497.0   # mm3, measured from edf_stator_sleeve.stl
    d_mass = sleeve_vol * (RHO_AL - RHO_CF_PETG)
    print(f"\n  Option B mass cost: stator sleeve {sleeve_vol * RHO_CF_PETG:.1f} g "
          f"CF-PETG -> {sleeve_vol * RHO_AL:.1f} g in 6061 "
          f"= +{d_mass:.1f} g each, +{2 * d_mass:.1f} g the pair")
    return 0


if __name__ == "__main__":
    sys.exit(main())
