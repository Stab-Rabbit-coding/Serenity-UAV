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
deceleration from the Rev R5 ~1,000 g to a tunable range.

Load-share correction vs Rev R5: the build CG sits at hull-frame
Y = +111.5 mm (nacelle pivot = canonical "Engine Pivots 360 deg" balance
centre), i.e. at 86% of the canonical wheelbase -- the AFT leg pair
carries ~86% of static load, so the Rev R5 even 1/4-per-leg energy split
was optimistic.  Rev R6 sizes one common wire schedule for the aft-leg
worst case.

Two LEG LENGTH VARIANTS (2026-07-23): ground clearance is an AIRCRAFT
SAFETY spec (avoid a belly/tail strike, keep the hull clear of ground
debris during the landing/absorption stroke) -- NOT a requirement to pass
a cargo box underneath the parked aircraft.  Landing on top of a cargo
box, then winching/pulling it into the cargo bay, is an acceptable ops
concept and does not size the gear.  Two leg lengths are offered, sharing
one common bay/foot/wire BOM (only the printed leg-frame length differs):

  "1.5in"  hip->foot arm R_H = 41.9 mm, belly clearance 38.1 mm (1.50 in)
           -- compact/default variant.
  "3.0in"  hip->foot arm R_H = 65.0 mm, belly clearance 80.0 mm (3.15 in)
           -- extended variant, kept (not scrapped) for rough-field /
           extra-margin missions.

Because both variants share the SAME wire hardware (same P per wire), and
the hip bending moment M = 2*P*r is independent of R_H (wire-side only),
shortening the leg does NOT change the leg-frame structural margin -- it
trades ground clearance for a HIGHER peak deceleration and a SMALLER
settle-stroke reserve, since F_leg = 2*P*r/R_H is inversely proportional
to R_H for a fixed wire.  This script solves the wire schedule once
against the historical 3.0in design point (peak decel target), then
reports what the SAME hardware does when reused in the 1.5in leg.

Design references (see REFERENCES.md):
  REF-CAD-003  QMx Official Serenity Blueprints Reference Pack (2007),
               Sheet 5 "Ventral Surface Plan View" + "Detail of Landing
               Gear" -- canonical bay stations, leg articulation, tri-pad
               foot.
  REF-CAD-002  Nick Henning reference renders -- leg mechanical detail
               (cylinder-cluster thigh, disc joints), bay appearance.
  docs/LANDING_GEAR_ANALYSIS.md Rev R6 SS4.1 -- bowed-wire 2-hinge
               plateau model.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Fable 5, Anthropic) under the
          author's direction, 2026-07-21 (Rev R6), extended 2026-07-23 for
          the 1.5in/3.0in leg-length variant split.  Per repository
          AGENTS.md AI attribution policy.
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

# Hip-pivot lever geometry (mm).  Bellcrank radius r and bay hip mounting
# height are common to both leg-length variants -- only the leg frame
# below the hip changes length, so only R_H and ground clearance vary.
R_WIRE = 6.0               # bellcrank radius, both wire pairs (M3 pin + walls)
HIP_HULL_Z = 38.0          # hip pin height above the cargo belly (both variants)

LEG_VARIANTS = {
    # name: (R_H mm, belly clearance mm) -- see canonical_leg_r6_<name>.scad
    "1.5in": (41.9, 38.1),
    "3.0in": (65.0, 80.0),
}
DESIGN_VARIANT = "3.0in"   # variant the wire schedule is SOLVED against
# (historical design point); the other variant reuses the resulting
# hardware -- see header.

# Wire materials (Rev R5 values carried forward)
SIGMA_FLOW_DUCTILE = 550.0    # MPa, ductile temper flow stress
SIGMA_WORK_SPRING = 900.0     # MPa, spring temper elastic working stress
RHO_STEEL = 7.85e-3            # g/mm^3
H0 = 3.5                       # mm, pre-bend rise (both wire types)
HMAX_FRAC = 0.35               # deepest usable bow rise as fraction of chord L
# (2-hinge plateau model validity limit)

# CF-PETG structure allowable (Rev R5 SS4.6 convention: yield/2)
SIGMA_ALLOW_PETG = 27.5        # MPa

# Wire ends stay STRAIGHT so they can seat in socket bores: seat depth +
# 2 mm run-in per end.  Only the exposed mid-span carries the bow, so all
# stroke formulas run on the BOW SPAN B = L - 2*(seat + 2), not on L.
SEAT_DUCTILE = 8.0             # mm, socket seat depth per end (ductile)
SEAT_SPRING = 5.0              # mm, socket seat depth per end (spring)
END_RUN_IN = 2.0               # mm, straight run-in beyond the socket mouth


def wire_stroke_available(b_mm: float) -> float:
    """Axial chord-shortening available on a bow span B before the bow
    exceeds the model validity limit h_max = HMAX_FRAC * B.
    s = (h_max^2 - h0^2) / (2B)."""
    hmax = HMAX_FRAC * b_mm
    return (hmax**2 - H0**2) / (2.0 * b_mm)


def solve_ductile_wire(u_per_wire_j: float, f_leg_target_n: float, r_h: float):
    """Given per-wire energy demand and a target per-leg plateau force at
    hip arm r_h, return (d, bow, length, p_wire, stroke) for the ductile
    wire at bellcrank R_WIRE."""
    p_wire = f_leg_target_n * r_h / (2.0 * R_WIRE)        # N, per wire
    # invert P = 2*(sigma*d^3/6)/h0  ->  d = (3*P*h0/sigma)^(1/3)
    d = (3.0 * p_wire * H0 / SIGMA_FLOW_DUCTILE) ** (1.0 / 3.0)
    stroke = u_per_wire_j * 1000.0 / p_wire               # mm (U = P*s plateau)
    # shortest bow span whose available stroke covers the demand
    bow = 20.0
    while wire_stroke_available(bow) < stroke and bow < 120.0:
        bow += 1.0
    length = bow + 2.0 * (SEAT_DUCTILE + END_RUN_IN)      # full stock length
    return d, bow, length, p_wire, stroke


def wire_mass_g(d_mm: float, l_mm: float) -> float:
    return math.pi / 4.0 * d_mm**2 * l_mm * RHO_STEEL


def main() -> None:
    w_n = M_AUW_KG * G
    share_aft = (Y_CG - Y_FOOT_FORE) / WHEELBASE / 2.0    # per aft leg
    share_fore = (Y_FOOT_AFT - Y_CG) / WHEELBASE / 2.0    # per fore leg

    print("=" * 78)
    print("Serenity UAV landing gear Rev R6 sizing -- hip-pivot canonical leg")
    print("=" * 78)
    print(f"AUW {M_AUW_KG:.3f} kg ({M_AUW_KG/0.45359:.2f} lbm), weight "
          f"{w_n:.1f} N ({w_n/4.448:.2f} lbf)")
    print(f"Feet Y: fore {Y_FOOT_FORE:+.0f} / aft {Y_FOOT_AFT:+.0f} mm; "
          f"CG Y {Y_CG:+.1f} mm; wheelbase {WHEELBASE:.0f} mm")
    print(f"Static share per leg: aft {share_aft*100:.1f}%  "
          f"fore {share_fore*100:.1f}%")
    for name, (r_h, clearance) in LEG_VARIANTS.items():
        print(f"Variant {name}: R_h {r_h:.1f} mm, bellcrank r {R_WIRE:.1f} mm "
              f"(ratio {r_h/R_WIRE:.2f}:1), belly clearance {clearance:.1f} mm "
              f"({clearance/25.4:.2f} in)")

    print("\n--- Energy cases (KE = m*g*h, free drop) " + "-" * 35)
    for h_ft in DROPS_FT:
        ke = M_AUW_KG * G * h_ft * FT
        for case, share in [("level 4-pt", share_aft), ("tail-down 2-pt", 0.5)]:
            u_leg = ke * share
            print(f"{h_ft:.0f} ft  {case:<15} KE {ke:6.2f} J   worst leg "
                  f"{u_leg:6.2f} J   ({share*100:.1f}% share)")

    r_h_design, _ = LEG_VARIANTS[DESIGN_VARIANT]

    # Solve the ductile wire ONCE per drop schedule against the design
    # variant (3.0in, the historical design point), then report what the
    # SAME hardware does when reused in every other variant.
    for label, h_ft in [("6 ft", 6.0), ("4 ft", 4.0)]:
        u_leg_design = M_AUW_KG * G * h_ft * FT * 0.5      # tail-down, worst leg
        u_wire = u_leg_design / 2.0                        # ductile pair shares
        # design-point target: keep the DESIGN_VARIANT's tail-down peak
        # near 50 g at 6 ft (scaled proportionally at 4 ft)
        f_leg_design = 800.0 if label == "6 ft" else 800.0 * 4.0 / 6.0
        d, b, l, p_wire, _ = solve_ductile_wire(u_wire, f_leg_design, r_h_design)
        print(f"\n--- DUCTILE schedule solved for {label} tail-down at "
              f"{DESIGN_VARIANT} (R_h {r_h_design:.1f} mm) " + "-" * 8)
        print(f"  design target  {f_leg_design:6.1f} N/leg "
              f"({f_leg_design/4.448:5.1f} lbf) -> wire P {p_wire:7.1f} N")
        print(f"  wire: d {d:5.2f} mm, bow span {b:4.0f} mm, stock "
              f"L {l:4.0f} mm (straight seat ends), h0 {H0} mm")
        print(f"  wire mass {wire_mass_g(d, l):.2f} g x8 = "
              f"{8*wire_mass_g(d, l):.1f} g/aircraft")

        print(f"  Reusing this wire (P={p_wire:.0f} N) in every variant:")
        for name, (r_h, clearance) in LEG_VARIANTS.items():
            f_leg = 2.0 * p_wire * R_WIRE / r_h            # N, actual leg force
            settle = u_leg_design * 1000.0 / f_leg          # mm vertical
            stroke = u_wire * 1000.0 / p_wire                # mm at the wire
            rot = math.degrees(stroke / R_WIRE)              # hip rotation, deg
            g_taildown = 2.0 * f_leg / w_n
            g_level = 4.0 * f_leg / w_n
            residual = clearance - settle
            flag = "  ** TIGHT **" if residual < 0.25 * clearance else ""
            print(f"    {name:6s} R_h {r_h:5.1f} mm: F_leg {f_leg:6.1f} N "
                  f"({f_leg/4.448:5.1f} lbf), settle {settle:5.1f} mm of "
                  f"{clearance:5.1f} mm (residual {residual:5.1f} mm), "
                  f"rotation {rot:4.1f} deg, decel tail-down/level "
                  f"{g_taildown:5.1f} / {g_level:5.1f} g{flag}")

    # Spring wires: elastic-phase, sized so spring pair absorbs the
    # ordinary-hard-landing energy fully elastically (Rev R5 3.51 J/leg
    # kept), solved against the design variant.
    u_spring_leg = 3.51
    u_spring_wire = u_spring_leg / 2.0
    f_leg_el = 350.0
    p_spring = f_leg_el * r_h_design / (2.0 * R_WIRE)
    d_s = (16.0 * p_spring * H0 / (SIGMA_WORK_SPRING * math.pi)) ** (1 / 3.0)
    stroke_s = u_spring_wire * 1000.0 / p_spring
    b_s = 20.0
    # 1.2x stroke reserve so the spring never approaches the bow-model limit
    while wire_stroke_available(b_s) < 1.2 * stroke_s and b_s < 120.0:
        b_s += 1.0
    l_s = b_s + 2.0 * (SEAT_SPRING + END_RUN_IN)
    print(f"\n--- SPRING schedule (elastic phase, solved at {DESIGN_VARIANT}) "
          + "-" * 12)
    print(f"  per-leg elastic energy {u_spring_leg:.2f} J -> per wire "
          f"{u_spring_wire:.3f} J")
    print(f"  elastic-limit target {f_leg_el:.0f} N/leg -> wire P "
          f"{p_spring:.1f} N")
    print(f"  wire: d {d_s:.2f} mm, bow span {b_s:.0f} mm, stock L {l_s:.0f} "
          f"mm (straight seat ends), h0 {H0} mm, stroke "
          f"{stroke_s:.2f} mm (avail {wire_stroke_available(b_s):.2f})")
    print(f"  wire mass {wire_mass_g(d_s, l_s):.2f} g x8 = "
          f"{8*wire_mass_g(d_s, l_s):.1f} g/aircraft")
    print("  Reusing this wire in every variant:")
    for name, (r_h, clearance) in LEG_VARIANTS.items():
        f_leg = 2.0 * p_spring * R_WIRE / r_h
        settle_el = u_spring_leg * 1000.0 / f_leg
        print(f"    {name:6s} R_h {r_h:5.1f} mm: elastic-limit force "
              f"{f_leg:6.1f} N/leg, settle at limit {settle_el:4.1f} mm, "
              f"onset decel (level) {4*f_leg/w_n:5.1f} g")

    # Structure checks -- done ONCE at the 6 ft design point per variant.
    # Hip bending moment M = 2*P*r is wire-side only (independent of R_h),
    # so the thigh margin is IDENTICAL across variants; everything else
    # that depends on F_leg (hip pin, lateral case, static stance) is
    # reported per variant.
    d_ref, b_ref, l_ref, p_ref, _ = solve_ductile_wire(
        (M_AUW_KG * G * 6.0 * FT * 0.5) / 2.0, 800.0, r_h_design)
    m_hip = 2.0 * p_ref * R_WIRE                            # N*mm, all variants
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
    print("\n--- Structure checks (6 ft design point, both variants) "
          + "-" * 15)
    print(f"  thigh @hip: M {m_hip/1000:.1f} N*m (= 2*P*r, R_h-INDEPENDENT -- "
          f"same for every variant), section 2x{d_cyl:.0f} mm cyl @ "
          f"{c_ctr:.0f} mm ctrs + web -> Z {z_mod:.0f} mm^3, sigma "
          f"{sigma:.1f} MPa (allow {SIGMA_ALLOW_PETG} MPa, margin "
          f"{SIGMA_ALLOW_PETG/sigma:.2f}x)")

    a_pin = math.pi / 4.0 * 3.0**2
    v_cap = 2.0 * 0.6 * 500.0 * a_pin                       # N (0.6*Su A2-70)
    a_bear = 12 * 10 - 6 * 5
    for name, (r_h, clearance) in LEG_VARIANTS.items():
        f_leg = 2.0 * p_ref * R_WIRE / r_h
        m_stance = share_aft * w_n * r_h
        p_stance = m_stance / (4.0 * R_WIRE)
        f_lat = f_leg * math.tan(math.radians(15.0))
        print(f"  {name}: hip pin M3 SS double-shear {v_cap:.0f} N vs "
              f"F_leg {f_leg:.0f} N -> margin {v_cap/f_leg:.1f}x; "
              f"bay boss bearing {70*a_bear:.0f} N vs wire P {p_ref:.0f} N "
              f"-> margin {70*a_bear/p_ref:.2f}x; static stance "
              f"{p_stance:.1f} N/wire; lateral +/-15deg {f_lat:.0f} N/leg")


if __name__ == "__main__":
    main()
