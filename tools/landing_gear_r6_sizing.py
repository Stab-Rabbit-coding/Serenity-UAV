#!/usr/bin/env python3
"""Serenity UAV -- Landing Gear Rev R6 sizing study (hip-pivot canonical leg).

Rev R6 replaces the Rev R5 rigid vertical post with a canonical articulated
leg (cylinder-cluster thigh, disc knee, slotted shin, disc ankle, tri-pad
foot) that pivots about a stainless hip pin inside a hull-flank bay.  The
Rev R5 energy-absorbing mechanism is retained unchanged in principle: two
SPRING bowed wires (elastic, recoverable) and two DUCTILE bowed wires
(plastic, sacrificial) per leg, each a straight wire with one shallow
pre-bend, loaded axially along its chord so the bow deepens.  What changes
is WHERE the wires act: they now span the hip joint at a small bellcrank
radius r, so the leg rotating about the hip converts millimetres of wire
stroke into tens of millimetres of hull settle -- dropping peak
deceleration from the Rev R5 ~1,000 g to a tunable 50-100 g.

Load-share correction vs Rev R5: the build CG sits at hull-frame
Y = +111.5 mm (nacelle pivot = canonical "Engine Pivots 360 deg" balance
centre), i.e. at 86% of the canonical wheelbase -- the AFT leg pair
carries ~86% of static load, so the Rev R5 even 1/4-per-leg energy split
was optimistic.  Rev R6 sizes one common wire schedule for the aft-leg
worst case.

Design references (see REFERENCES.md):
  REF-CAD-003  QMx Official Serenity Blueprints Reference Pack (2007),
               Sheet 5 "Ventral Surface Plan View" + "Detail of Landing
               Gear" -- canonical bay stations, leg articulation, tri-pad
               foot.
  REF-CAD-002  Nick Henning reference renders -- leg mechanical detail
               (cylinder-cluster thigh, disc joints), bay appearance.
  docs/LANDING_GEAR_ANALYSIS.md Rev R5 SS4.1 -- bowed-wire 2-hinge
               plateau model carried forward unchanged.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Fable 5, Anthropic) under the
          author's direction, 2026-07-21.  Per repository AGENTS.md AI
          attribution policy.
License : CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>
"""

import math

# ---------------------------------------------------------------------------
# Aircraft and mission constants
# ---------------------------------------------------------------------------
M_AUW_KG = 3.130          # Phase 11 all-up mass, 6.90 lbm (design case)
G = 9.807                 # m/s^2

FT = 0.3048               # m per ft
DROPS_FT = [6.0, 4.0]     # candidate full-AUW drop-test heights

# Hull-frame geometry (mm) -- canonical stations mapped from QMx Sheet 5
# (fore feet at 39.2% of hull length, aft feet at 63.9%, hull Y span
# -305.7 .. +384.3 measured from the baked shells)
Y_FOOT_FORE = -35.0
Y_FOOT_AFT = 135.0
Y_CG = 111.5              # nacelle pivot = balance centre (project memory)
WHEELBASE = Y_FOOT_AFT - Y_FOOT_FORE

# Hip-pivot lever geometry (mm)
R_H = 65.0                # horizontal hip-pin -> foot moment arm (swing plane)
R_WIRE = 6.0              # bellcrank radius, both wire pairs (M3 pin + walls)
CLEARANCE_MM = 38.1       # 1.5" provides safety
# Wire materials (Rev R5 values carried forward)
SIGMA_FLOW_DUCTILE = 550.0    # MPa, ductile temper flow stress
SIGMA_WORK_SPRING = 900.0     # MPa, spring temper elastic working stress
RHO_STEEL = 7.85e-3           # g/mm^3
H0 = 3.5                      # mm, pre-bend rise (both wire types)
HMAX_FRAC = 0.35              # deepest usable bow rise as fraction of chord L
# (2-hinge plateau model validity limit)

# CF-PETG structure allowable (Rev R5 SS4.6 convention: yield/2)
SIGMA_ALLOW_PETG = 27.5       # MPa

# Wire ends stay STRAIGHT so they can seat in socket bores: seat depth +
# 2 mm run-in per end.  Only the exposed mid-span carries the bow, so all
# stroke formulas run on the BOW SPAN B = L - 2*(seat + 2), not on L.
SEAT_DUCTILE = 8.0            # mm, socket seat depth per end (ductile)
SEAT_SPRING = 5.0             # mm, socket seat depth per end (spring)
END_RUN_IN = 2.0              # mm, straight run-in beyond the socket mouth


def wire_plateau_force_plastic(d_mm: float) -> float:
    """Ductile bowed-wire axial plastic-collapse plateau force, N.
    2-hinge model: P = 2*M/h0, M = sigma_f * d^3 / 6 (plastic modulus)."""
    m_crown = SIGMA_FLOW_DUCTILE * d_mm**3 / 6.0     # N*mm
    return 2.0 * m_crown / H0


def wire_limit_force_elastic(d_mm: float) -> float:
    """Spring bowed-wire axial force at first-yield elastic limit, N.
    P = 2*M/h0, M = sigma_w * pi * d^3 / 32 (elastic section modulus)."""
    m_crown = SIGMA_WORK_SPRING * math.pi * d_mm**3 / 32.0
    return 2.0 * m_crown / H0


def wire_stroke_available(b_mm: float) -> float:
    """Axial chord-shortening available on a bow span B before the bow
    exceeds the model validity limit h_max = HMAX_FRAC * B.
    s = (h_max^2 - h0^2) / (2B)."""
    hmax = HMAX_FRAC * b_mm
    return (hmax**2 - H0**2) / (2.0 * b_mm)


def solve_ductile_wire(u_per_wire_j: float, f_leg_target_n: float):
    """Given per-wire energy demand and target per-leg plateau force,
    return (demand, bow, length, p_wire, stroke) for the ductile wire at bellcrank R_WIRE."""
    p_wire = f_leg_target_n * R_H / (2.0 * R_WIRE)       # N, per wire
    # invert P = 2*(sigma*d^3/6)/h0  ->  d = (3*P*h0/sigma)^(1/3)
    demand = (3.0 * p_wire * H0 / SIGMA_FLOW_DUCTILE) ** (1.0 / 3.0)
    stroke = u_per_wire_j * 1000.0 / p_wire              # mm (U = P*s plateau)
    # shortest bow span bow whose available stroke covers the demand
    bow = 20.0
    while wire_stroke_available(bow) < stroke and bow < 120.0:
        bow += 1.0
    length = bow + 2.0 * (SEAT_DUCTILE + END_RUN_IN)            # full stock length
    return demand, bow, length, p_wire, stroke


def wire_mass_g(d_mm: float, l_mm: float) -> float:
    return math.pi / 4.0 * d_mm**2 * l_mm * RHO_STEEL


def main() -> None:
    w_n = M_AUW_KG * G
    share_aft = (Y_CG - Y_FOOT_FORE) / WHEELBASE / 2.0   # per aft leg
    share_fore = (Y_FOOT_AFT - Y_CG) / WHEELBASE / 2.0   # per fore leg

    print("=" * 74)
    print("Serenity UAV landing gear Rev R6 sizing -- hip-pivot canonical leg")
    print("=" * 74)
    print(f"AUW {M_AUW_KG:.3f} kg ({M_AUW_KG/0.45359:.2f} lbm), weight "
          f"{w_n:.1f} N ({w_n/4.448:.2f} lbf)")
    print(f"Feet Y: fore {Y_FOOT_FORE:+.0f} / aft {Y_FOOT_AFT:+.0f} mm; "
          f"CG Y {Y_CG:+.1f} mm; wheelbase {WHEELBASE:.0f} mm")
    print(f"Static share per leg: aft {share_aft*100:.1f}%  "
          f"fore {share_fore*100:.1f}%")
    print(f"Lever: R_h {R_H:.0f} mm, bellcrank r {R_WIRE:.1f} mm "
          f"(ratio {R_H/R_WIRE:.1f}:1)")

    print("\n--- Energy cases (KE = m*g*h, free drop) " + "-" * 32)
    rows = []
    for h_ft in DROPS_FT:
        ke = M_AUW_KG * G * h_ft * FT
        for case, share, n_legs in [("level 4-pt", share_aft, 4),
                                    ("tail-down 2-pt", 0.5, 2)]:
            u_leg = ke * share
            rows.append((h_ft, case, ke, u_leg, n_legs))
            print(f"{h_ft:.0f} ft  {case:<15} KE {ke:6.2f} J   worst leg "
                  f"{u_leg:6.2f} J   ({share*100:.1f}% share)")

    # Design case: 6 ft tail-down (envelopes 6 ft level-4pt aft share too)
    for label, (h_ft, u_leg_design) in [
            ("6 ft", (6.0, M_AUW_KG * G * 6.0 * FT * 0.5)),
            ("4 ft", (4.0, M_AUW_KG * G * 4.0 * FT * 0.5))]:
        u_wire = u_leg_design / 2.0                       # ductile pair shares
        # target plateau: keep tail-down peak near 50 g
        f_leg = 800.0 if label == "6 ft" else 800.0 * 4.0 / 6.0
        d, b, l, p_wire, stroke = solve_ductile_wire(u_wire, f_leg)
        settle = u_leg_design * 1000.0 / f_leg            # mm vertical
        rot = math.degrees(stroke / R_WIRE)               # hip rotation, deg
        g_taildown = 2.0 * f_leg / w_n
        g_level = 4.0 * f_leg / w_n
        print(f"\n--- DUCTILE schedule sized for {label} tail-down "
              + "-" * 32)
        print(f"  per-leg energy {u_leg_design:6.2f} J -> per wire "
              f"{u_wire:6.2f} J")
        print(f"  plateau force  {f_leg:6.1f} N/leg "
              f"({f_leg/4.448:6.1f} lbf) -> wire P {p_wire:7.1f} N")
        print(f"  wire: d {d:5.2f} mm, bow span {b:4.0f} mm, stock "
              f"L {l:4.0f} mm (straight seat ends), h0 {H0} mm, "
              f"stroke used {stroke:4.2f} mm "
              f"(avail {wire_stroke_available(b):4.2f})")
        print(f"  hull settle {settle:5.1f} mm of {CLEARANCE_MM:.0f} mm "
              f"clearance; hip rotation {rot:4.1f} deg")
        print(f"  peak decel: tail-down {g_taildown:5.1f} g, "
              f"level-4pt {g_level:5.1f} g")
        print(f"  wire mass {wire_mass_g(d, l):.2f} g x8 = "
              f"{8*wire_mass_g(d, l):.1f} g/aircraft")

    # Spring wires: elastic-phase, sized so spring pair absorbs the
    # ordinary-hard-landing energy fully elastically (Rev R5 3.51 J/leg kept)
    u_spring_leg = 3.51
    u_spring_wire = u_spring_leg / 2.0
    f_leg_el = 350.0
    p_spring = f_leg_el * R_H / (2.0 * R_WIRE)
    d_s = (16.0 * p_spring * H0 / (SIGMA_WORK_SPRING * math.pi)) ** (1/3.0)
    stroke_s = u_spring_wire * 1000.0 / p_spring
    b_s = 20.0
    # 1.2x stroke reserve so the spring never approaches the bow-model limit
    while wire_stroke_available(b_s) < 1.2 * stroke_s and b_s < 120.0:
        b_s += 1.0
    l_s = b_s + 2.0 * (SEAT_SPRING + END_RUN_IN)
    settle_el = stroke_s * R_H / R_WIRE
    print("\n--- SPRING schedule (elastic phase, both drop options) " + "-"*18)
    print(f"  per-leg elastic energy {u_spring_leg:.2f} J -> per wire "
          f"{u_spring_wire:.3f} J")
    print(f"  elastic-limit force {f_leg_el:.0f} N/leg -> wire P "
          f"{p_spring:.1f} N")
    print(f"  wire: d {d_s:.2f} mm, bow span {b_s:.0f} mm, stock L {l_s:.0f} "
          f"mm (straight seat ends), h0 {H0} mm, stroke "
          f"{stroke_s:.2f} mm (avail {wire_stroke_available(b_s):.2f})")
    print(f"  elastic settle at limit {settle_el:.1f} mm; onset decel "
          f"{4*f_leg_el/w_n:.1f} g (level)")
    print(f"  wire mass {wire_mass_g(d_s, l_s):.2f} g x8 = "
          f"{8*wire_mass_g(d_s, l_s):.1f} g/aircraft")

    # Static stance check
    m_stance = share_aft * w_n * R_H                      # N*mm at hip
    p_stance = m_stance / (4.0 * R_WIRE)                  # 4 wires engaged
    print("\n--- Stance / structure checks " + "-" * 43)
    print(f"  static aft-leg wire load {p_stance:.1f} N/wire "
          f"(vs ductile plateau ~4,300 N) -- stance is rigid")

    # Thigh bending at hip: stadium section, two D_CYL cylinders C_CTR apart
    f_leg = 800.0
    m_hip = f_leg * R_H                                   # N*mm
    d_cyl, c_ctr = 14.0, 18.0
    r_c = d_cyl / 2.0
    a_circ = math.pi * r_c**2
    i_circ = math.pi * d_cyl**4 / 64.0
    i_pair = 2.0 * (i_circ + a_circ * (c_ctr / 2.0)**2)
    i_web = d_cyl * c_ctr**3 / 12.0
    i_tot = i_pair + i_web
    c_out = c_ctr / 2.0 + r_c
    z_mod = i_tot / c_out
    sigma = m_hip / z_mod
    print(f"  thigh @hip: M {m_hip/1000:.1f} N*m, section 2x"
          f"{d_cyl:.0f} mm cyl @ {c_ctr:.0f} mm ctrs + web -> "
          f"Z {z_mod:.0f} mm^3, sigma {sigma:.1f} MPa "
          f"(allow {SIGMA_ALLOW_PETG} MPa, "
          f"margin {SIGMA_ALLOW_PETG/sigma:.2f}x)")

    # Hip pin: M3 stainless, double shear
    a_pin = math.pi / 4.0 * 3.0**2
    v_cap = 2.0 * 0.6 * 500.0 * a_pin                     # N (0.6*Su A2-70)
    print(f"  hip pin M3 SS double-shear capacity {v_cap:.0f} N vs "
          f"plateau {f_leg:.0f} N -> margin {v_cap/f_leg:.1f}x")

    # Bay boss bearing (per wire): annulus OD 12x10 wall around 6x5 bore
    a_bear = 12*10 - 6*5
    p_wire_max = f_leg * R_H / (2.0 * R_WIRE)
    print(f"  bay boss bearing 70 MPa x {a_bear} mm^2 = {70*a_bear} N vs "
          f"wire P {p_wire_max:.0f} N -> margin {70*a_bear/p_wire_max:.2f}x")

    # Lateral +/-15 deg case (Rev R5 SS4.8 convention)
    f_lat = f_leg * math.tan(math.radians(15.0))
    print(f"  lateral (+/-15 deg): {f_lat:.0f} N/leg into hip pin + "
          f"clevis side faces (pin margin above)")


if __name__ == "__main__":
    main()
