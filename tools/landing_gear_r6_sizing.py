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

  "1.5in"  belly clearance 38.1 mm (1.50 in) -- compact/default variant.
  "3.0in"  belly clearance 80.0 mm (3.15 in) -- extended variant, kept (not
           scrapped) for rough-field / extra-margin missions.

As of 2026-08-09 BOTH variants run the same hip->foot arm, R_H_BUILT = 80 mm,
and therefore the same crash dynamics; they differ only in belly clearance and
printed leg-frame length.  Two owner decisions got them there: the LG-10.2
15 mm hip recess (pivot moved into the bay so the pivot and wire anchors sit
inside the recess rather than outside the skin), and the extension of the
compact leg to the CANONICAL foot spread, which its old R_H 41.9 could not
reach.  See R_H_BUILT below for the full provenance.

Because the lever is now shared, the wire schedule is no longer solved against
a peak-deceleration target on one variant and reused on the other.  It is
solved against the CLEARANCE-LIMITED variant: the arrest must stop inside the
compact leg's 38.1 mm with RESIDUAL_MIN to spare.  That is the binding
constraint, and sizing to it directly is what stops a geometry change from
silently pushing the leg past bottoming.  The hip bending moment M = 2*P*r
remains R_H-independent (wire-side only), so the leg-frame section margin is
identical in both variants.

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
import sys

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

# LG-10.2 (2026-08-09, owner decision): the hip pivot moves INBOARD into the
# recessed bay.  tools/landing_gear_bay_station_fit.py measured the canonical
# hips sitting essentially ON the skin (+1.17 mm fore, -7.53 mm aft along the
# SS2.4a panel normal), which cannot produce a coherent bay once LG-10.3 cuts
# the wells open: the wire bosses land 16-20 mm OUTBOARD of the skin while the
# mounting flange has to sit inboard of it, so the bay renders as disconnected
# bodies.  Recessing the pivot puts the pivot and the wire anchors inside the
# bay box, which is also what [REF-CAD-002] shows.
#
# The FEET stay at their canonical QMx stations, so the hip->foot arm grows by
# the same amount: R_H += HIP_INBOARD.  A UNIFORM offset is used at all four
# corners deliberately -- a per-station offset would make the fore and aft legs
# different parts and break "one common leg part per variant" (SS11.1).
#
# ACCEPTED TRADE (owner, 2026-08-09): a longer lever makes the leg SOFTER, so
# peak deceleration falls but the arrest settles further.  The compact 1.5in
# variant pays for this out of the only clearance it has: residual clearance
# after settle drops 15.5 -> 7.4 mm.  The alternative -- holding F_leg constant
# by growing the ductile wire to d = 4.22 mm -- was offered and declined.  The
# single-ductile-wire-only fallback (SS4.7 safety note) does NOT close on the
# 1.5in variant either before or after this change, and is now further away.
HIP_INBOARD = 15.0         # mm, pivot recessed along the panel normal

# Historical hip->foot arms, kept so the provenance of R_H_BUILT is readable.
R_H_CANON = {"1.5in": 41.9, "3.0in": 65.0}

# CANONICAL FOOT SPREAD (2026-08-09, owner decision).  The 1.5in variant's feet
# sat ~23 mm INBOARD of their canonical QMx stations -- a defect that predates
# the recess: R_H 41.9 simply could not reach, and the WBS corner-station table
# quoted the 3.0in foot positions as if they covered both variants.  The compact
# leg is now extended to reach canon, which lands BOTH variants on the same
# hip->foot arm:
#
#   1.5in   41.9 --(+15 recess)--> 56.9 --(+23.1 canonical spread)--> 80.0
#   3.0in   65.0 --(+15 recess)------------------------------------> 80.0
#
# So the two variants now differ ONLY in belly clearance and leg-frame length:
# one lever, one wire schedule, one set of crash dynamics.  Feet land within
# 0.5 mm of the canonical stations for both.
R_H_BUILT = 80.0           # mm, shared hip->foot arm, both variants

LEG_VARIANTS = {
    # name: (as-built R_H mm, belly clearance mm) -- canonical_leg_r6_<name>.scad
    "1.5in": (R_H_BUILT, 38.1),
    "3.0in": (R_H_BUILT, 80.0),
}

# The ductile wire is now sized by the CLEARANCE-LIMITED variant, not by a peak
# deceleration target.  Extending the compact leg to canonical spread without
# re-sizing the wire would have made it BOTTOM OUT: at R_H 80 the old d 3.81
# wire needs 43.2 mm of settle and has 38.1 mm, so 2.20 J (11.8%) of a 4 ft
# arrest would arrive as a belly strike at 1.68 m/s -- equivalent to dropping
# the hull 143 mm flat onto its belly with no gear in the path, with the ductile
# fuse only 88% fired.  The wire therefore has to hold the settle inside the
# compact variant's clearance, which is what these two numbers say.
CLEARANCE_COMPACT = 38.1   # mm, the tighter of the two variants
RESIDUAL_MIN = 7.4         # mm, residual clearance after full settle.  This is
# the value accepted with the LG-10.2 recess; holding it here means the
# canonical-spread leg reproduces the accepted crash performance exactly
# (F_leg 609 N, settle 30.7 mm, 39.7/79.4 g) rather than trading it again.

DESIGN_VARIANT = "1.5in"   # the clearance-limited variant sets the schedule

# Wire materials (Rev R5 values carried forward)
SIGMA_FLOW_DUCTILE = 550.0    # MPa, ductile temper flow stress
SIGMA_WORK_SPRING = 900.0     # MPa, spring temper elastic working stress
RHO_STEEL = 7.85e-3            # g/mm^3
H0 = 3.5                       # mm, pre-bend rise (both wire types)
HMAX_FRAC = 0.35               # deepest usable bow rise as fraction of chord L
# (2-hinge plateau model validity limit)

# LG-18 mass reduction: axial bore through each thigh cylinder.  Sized against
# the SS4.6 section check below -- at M 48.8 N*m the solid section runs
# sigma 22.0 MPa (margin 1.25x), and the bore trades margin for mass:
#   bore 0 mm  Z 2219 mm^3  sigma 22.0 MPa  margin 1.25x   (solid)
#   bore 6 mm  Z 1926 mm^3  sigma 25.3 MPa  margin 1.09x   <- adopted
#   bore 8 mm  Z 1686 mm^3  sigma 28.9 MPa  margin 0.95x   FAILS
THIGH_BORE_D = 6.0             # mm

# CF-PETG structure allowable (Rev R5 SS4.6 convention: yield/2)
SIGMA_ALLOW_PETG = 27.5        # MPa

# Wire ends stay STRAIGHT so they can seat in socket bores: seat depth +
# 2 mm run-in per end.  Only the exposed mid-span carries the bow, so all
# stroke formulas run on the BOW SPAN B = L - 2*(seat + 2), not on L.
SEAT_DUCTILE = 8.0             # mm, socket seat depth per end (ductile)
SEAT_SPRING = 5.0              # mm, socket seat depth per end (spring)
END_RUN_IN = 2.0               # mm, straight run-in beyond the socket mouth

# Shortest bow span the jig can form reliably in either temper (LG-16): below
# this the straight seat ends and the bow run into each other and the formed
# rise stops being repeatable.  It is a MANUFACTURING floor, not a structural
# one -- with the corrected stroke relation below, both wires would otherwise
# solve shorter than this.
BOW_SPAN_MIN = 20.0            # mm

# Stroke reserve demanded of each wire type, as a multiple of the stroke the
# energy balance actually requires.  The spring pair carries the recoverable
# phase and has always been solved at 1.2x.  The DUCTILE pair is the
# last-resort structural fuse and is the only thing between the hull and the
# ground once the springs are through, so it is solved at 1.5x: a bow that
# reaches its plateau-model limit mid-arrest stops absorbing at constant force
# and spikes the deceleration.
STROKE_RESERVE_SPRING = 1.2
STROKE_RESERVE_DUCTILE = 1.5


def wire_stroke_available(b_mm: float) -> float:
    """Axial chord-shortening available on a bow span B before the bow
    exceeds the 2-hinge plateau-model validity limit h_max = HMAX_FRAC * B.

        Delta = 2 * (h_max^2 - h0^2) / B

    CORRECTED 2026-08-09 (docs/LANDING_GEAR_ANALYSIS.md SS4.5a).  The previous
    form divided by 2B where the two-hinge mechanism divides by B/2, making
    every result a factor of 4 LOW; `--derive-stroke` carries the SymPy proof.

    Correcting it does NOT reopen LG-17 (drop height) or the wire DIAMETER.
    Those come from the force/energy balance: `solve_ductile_wire` fixes P
    from the per-leg force target and d from P, and neither reads this
    function.  B is chosen AFTER d, purely to guarantee the bow can travel the
    required chord shortening -- so the only thing that moves is bow span, and
    with it stock length and wire mass.  See SS4.5a.
    """
    hmax = HMAX_FRAC * b_mm
    return 2.0 * (hmax**2 - H0**2) / b_mm


def solve_bow_span(stroke_mm: float, reserve: float) -> float:
    """Shortest formable bow span whose available stroke covers reserve *
    the required stroke.  Steps in 1 mm from the manufacturing floor."""
    bow = BOW_SPAN_MIN
    while wire_stroke_available(bow) < reserve * stroke_mm and bow < 120.0:
        bow += 1.0
    return bow


def fired_bow_rise(b_mm: float, stroke_mm: float) -> float:
    """Exact two-hinge bow rise after the chord has shortened by stroke_mm.

    Inverts Delta = 2*sqrt(l^2 - h0^2) - 2*sqrt(l^2 - h^2) with l = B/2.
    This is the "visibly bent" field-inspection dimension (H_DEF_* in the
    SCAD), and it must be read against the span it was solved on.
    """
    half = b_mm / 2.0
    root = math.sqrt(half**2 - H0**2) - stroke_mm / 2.0
    return math.sqrt(max(half**2 - root**2, 0.0))


def lg02_bay_attachment() -> None:
    """LG-02: bay-to-shell attachment margins, and why the backing plate exists.

    Landing is an IMPACT load, so the acceptance criterion is FOS >= 4.0
    against ultimate (general machinery practice for dynamic/impact; static
    would be 2.5).  Bolt-hole bearing is checked with a stress-concentration
    factor K_t = 3.0 for a circular hole in a plate.

    Geometry (LG-10.3, 2026-08-09): 4x M3 through-bolts on the bay frame's
    flange, following the trapezoidal aperture -- centres at +/-17.5 mm (mouth
    end) and +/-22.0 mm (head end) across the pin axis, 68 mm apart up the
    canted plane.  They pass through the frame, the 2 mm cargo wall and the
    5 mm reinforcing collar the merge tool grows around each well opening
    (merge_cargo_interior.py lg_well_features / lg_bay_features).

    Superseded: the Rev R6 "30 x 70 mm pattern on a solid plate" had no room
    for its own bolts -- at the head the aperture was 36 mm wide inside a
    40 mm plate, so the M3 centres at +/-15 fell INSIDE the opening.
    """
    # LG-17 CLOSED 2026-08-09 (owner decision): 4 ft crash height adopted.
    # F_leg and the hip moment both come from the clearance-driven schedule, so
    # both variants load this joint identically (shared R_H_BUILT lever).
    # Derived from the SAME solve main() uses -- this function previously
    # hardcoded p_wire, which is exactly how its published numbers went stale
    # through LG-17 and again through LG-10.2.
    u_leg = M_AUW_KG * G * 4.0 * FT * 0.5           # J, tail-down worst leg
    settle_max = CLEARANCE_COMPACT - RESIDUAL_MIN
    _d, _b, _l, p_wire, _s = solve_ductile_wire(
        u_leg / 2.0, u_leg * 1000.0 / settle_max, R_H_BUILT)
    f_leg = 2.0 * p_wire * R_WIRE / R_H_BUILT       # N, at the 4 ft schedule
    m_hip = 2.0 * p_wire * R_WIRE   # N*mm, hip moment (R_h-independent)
    lever = 68.0            # mm, bolt pattern extent up the canted plane
    n_bolt, n_row = 4, 2

    couple_row = m_hip / lever              # N per row
    tension = couple_row / n_row            # N per bolt
    shear = f_leg / n_bolt                  # N per bolt
    resultant = math.hypot(tension, shear)

    # M3 A2-70
    a_stress = 5.03                          # mm^2 tensile stress area
    su_bolt = 700.0                          # MPa
    cap_t = su_bolt * a_stress
    cap_v = 0.6 * su_bolt * a_stress

    sigma_bear = 70.0                        # MPa, CF-PETG bearing (SS4.6)
    tau_petg = 30.0                          # MPa, ~0.6 x 55 MPa yield
    kt_hole = 3.0
    d_bolt, d_head = 3.0, 5.5

    print("\n--- LG-02: bay -> shell attachment " + "-" * 40)
    print(f"  worst F_leg {f_leg:.0f} N; hip moment {m_hip/1000:.1f} N*m over a "
          f"{lever:.0f} mm bolt pattern")
    print(f"  per bolt: tension {tension:.0f} N, shear {shear:.0f} N, "
          f"resultant {resultant:.0f} N")
    print(f"  M3 A2-70 tension {cap_t:.0f} N -> FOS {cap_t/tension:.1f};  "
          f"shear {cap_v:.0f} N -> FOS {cap_v/shear:.1f}")

    # NOTE: K_t belongs on the NET-SECTION TENSION check, not on bearing.
    # Bearing is a contact/compressive allowable that already accounts for the
    # local condition; dividing it by K_t double-counts and understates every
    # stackup by 3x.
    print("\n  bolt-hole BEARING in CF-PETG (impact FOS target 4.0):")
    stackups = [
        ("bare 2 mm wall", 2.0),
        ("wall + 5 mm internal boss", 7.0),
        ("wall + boss + 3 mm backing plate", 10.0),
    ]
    fos_by_t = {}
    for label, t in stackups:
        cap = sigma_bear * d_bolt * t
        fos = cap / resultant
        fos_by_t[t] = fos
        verdict = "OK" if fos >= 4.0 else "FAILS impact criterion"
        print(f"    {label:34s} t={t:5.1f} mm  cap {cap:6.0f} N  "
              f"FOS {fos:4.2f}  {verdict}")

    # Net-section tension around the hole -- this IS where K_t = 3.0 applies.
    w_strip = 30.0                          # mm of plate width per bolt column
    t_net = 10.0
    a_net = (w_strip - d_bolt) * t_net
    sigma_net = kt_hole * tension / a_net
    allow = SIGMA_ALLOW_PETG
    print(f"\n  net-section tension at the hole (K_t = {kt_hole}): "
          f"{sigma_net:.1f} MPa vs {allow:.1f} MPa allowable "
          f"-> FOS {allow/sigma_net:.1f}")

    t_pull = 7.0
    cap_pull = math.pi * d_head * t_pull * tau_petg
    print(f"  head pull-through (M3 washer face Ø{d_head}, t={t_pull:.0f} mm): "
          f"{cap_pull:.0f} N vs {tension:.0f} N -> FOS {cap_pull/tension:.1f}")

    boss_only, with_plate = fos_by_t[7.0], fos_by_t[10.0]
    print(f"\n  => backing plate {'REQUIRED' if boss_only < 4.0 else 'optional'}: "
          f"the 5 mm boss alone reaches FOS {boss_only:.2f} on bearing")
    print(f"     ({'short of' if boss_only < 4.0 else 'meeting'} the 4.0 impact "
          f"criterion); 3 mm of backing plate takes it to {with_plate:.2f}.")


def derive_stroke_relation() -> None:
    """Symbolic re-derivation of the stroke <-> bow-rise relation (LG-13).

    Regression evidence for the factor-4 defect that wire_stroke_available()
    carried until 2026-08-09, and the source of the per-end socket slide that
    sets the LG-13 retention detail.  The defective form is reproduced inline
    below purely so the comparison table still proves the correction.  Needs SymPy:
    run under /usr/bin/python3, since the repo .venv is built with
    include-system-site-packages = false and hides the apt-installed sympy.
    """
    try:
        import sympy as sp
    except ImportError:
        print("  [skip] sympy unavailable -- run under /usr/bin/python3")
        return

    h, h0s, ll = sp.symbols("h h0 l", positive=True)
    chord = 2 * sp.sqrt(ll**2 - h**2)
    delta = chord.subs(h, h0s) - chord
    bsym = sp.Symbol("B", positive=True)
    series = sp.simplify(
        sp.series(delta, h, 0, 3).removeO().subs(ll, bsym / 2))

    print("\n--- LG-13: stroke <-> bow-rise derivation " + "-" * 33)
    print("  two-hinge exact : Delta = 2*sqrt(l^2-h0^2) - 2*sqrt(l^2-h^2),  l = B/2")
    print(f"  small-h series  : Delta ~ {series}")
    print("  script NOW uses : Delta = 2*(h^2 - h0^2)/B       (corrected)")
    print("  script UNTIL    : Delta = (h^2 - h0^2)/(2B)      <-- was 4x LOW")

    bb, hh0 = 55.0, H0
    lv = bb / 2.0
    print(f"\n  at the ductile design point B={bb:.0f} mm, h0={hh0:.1f} mm:")
    print(f"  {'h (mm)':>8} {'exact':>10} {'approx':>10} {'script':>10} {'ratio':>7}")
    for hv in (6.0, 10.0, 14.0, 19.2):
        ex = 2 * math.sqrt(lv**2 - hh0**2) - 2 * math.sqrt(lv**2 - hv**2)
        ap = 2 * (hv**2 - hh0**2) / bb
        sc = (hv**2 - hh0**2) / (2 * bb)
        print(f"  {hv:8.1f} {ex:10.3f} {ap:10.3f} {sc:10.3f} {ap / sc:7.2f}")

    # The stroke itself is energy-derived (s = U/P) and is IDENTICAL before and
    # after the correction -- only the span needed to deliver it changes.  Take
    # it from the same solver main() uses rather than a rounded literal: 3.24
    # rounds up across the 24 mm span boundary and would print 25 mm here.
    _d, _b, _l, _p, stroke = solve_ductile_wire(
        M_AUW_KG * G * 4.0 * FT * 0.5 / 2.0,
        800.0 * 4.0 / 6.0,
        R_H_CANON[DESIGN_VARIANT])
    b_now = solve_bow_span(stroke, STROKE_RESERVE_DUCTILE)
    print(f"\n  required stroke (U/P)            = {stroke:.2f} mm")
    print(f"  bow span, corrected + {STROKE_RESERVE_DUCTILE:.1f}x reserve  "
          f"= {b_now:.0f} mm  (was 55 mm; floor {BOW_SPAN_MIN:.0f} mm)")
    print(f"  available stroke on that span    = "
          f"{wire_stroke_available(b_now):.2f} mm "
          f"({wire_stroke_available(b_now) / stroke:.2f}x required)")
    print(f"  fired bow rise on that span      = "
          f"{fired_bow_rise(b_now, stroke):.2f} mm  (from h0 {H0:.1f} mm "
          f"-- this is H_DEF_DUCT in the SCAD)")
    print(f"  per-end slide into the socket    = {stroke / 2:.2f} mm "
          f"(seat {SEAT_DUCTILE:.0f} mm + {END_RUN_IN:.0f} mm run-in)")
    print("  => the seat SLIDES: retention must be a nylon-tipped drag screw,")
    print("     not a clamp.  See docs/LANDING_GEAR_ANALYSIS.md SS4.5a.")


def solve_ductile_wire(u_per_wire_j: float, f_leg_target_n: float, r_h: float):
    """Given per-wire energy demand and a target per-leg plateau force at
    hip arm r_h, return (d, bow, length, p_wire, stroke) for the ductile
    wire at bellcrank R_WIRE."""
    p_wire = f_leg_target_n * r_h / (2.0 * R_WIRE)        # N, per wire
    # invert P = 2*(sigma*d^3/6)/h0  ->  d = (3*P*h0/sigma)^(1/3)
    d = (3.0 * p_wire * H0 / SIGMA_FLOW_DUCTILE) ** (1.0 / 3.0)
    stroke = u_per_wire_j * 1000.0 / p_wire               # mm (U = P*s plateau)
    # shortest formable bow span whose available stroke covers the demand
    # plus the ductile reserve (SS4.5a)
    bow = solve_bow_span(stroke, STROKE_RESERVE_DUCTILE)
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

    # Both variants now share R_H_BUILT, so the schedule is solved on the
    # as-built lever directly -- the pre-recess indirection is gone.
    r_h_design = R_H_BUILT
    settle_max = CLEARANCE_COMPACT - RESIDUAL_MIN

    # Solve the ductile wire ONCE per drop schedule against the design
    # variant (3.0in, the historical design point), then report what the
    # SAME hardware does when reused in every other variant.
    for label, h_ft in [("6 ft", 6.0), ("4 ft", 4.0)]:
        u_leg_design = M_AUW_KG * G * h_ft * FT * 0.5      # tail-down, worst leg
        u_wire = u_leg_design / 2.0                        # ductile pair shares
        # design-point target: the leg must stop inside the compact
        # variant's belly clearance with RESIDUAL_MIN to spare.  F = U/s.
        f_leg_design = u_leg_design * 1000.0 / settle_max
        d, b, l, p_wire, _ = solve_ductile_wire(u_wire, f_leg_design, r_h_design)
        print(f"\n--- DUCTILE schedule solved for {label} tail-down at "
              f"{DESIGN_VARIANT} (R_h {r_h_design:.1f} mm, shared) " + "-" * 8)
        print(f"  design target  {f_leg_design:6.1f} N/leg "
              f"({f_leg_design/4.448:5.1f} lbf) -> wire P {p_wire:7.1f} N"
              f"   [settle <= {settle_max:.1f} mm of "
              f"{CLEARANCE_COMPACT:.1f} mm clearance]")
        print(f"  wire: d {d:5.2f} mm, bow span {b:4.0f} mm, stock "
              f"L {l:4.0f} mm (straight seat ends), h0 {H0} mm")
        stroke_d = (M_AUW_KG * G * h_ft * FT * 0.5 / 2.0) * 1000.0 / p_wire
        print(f"  stroke {stroke_d:.2f} mm required, "
              f"{wire_stroke_available(b):.2f} mm available "
              f"({wire_stroke_available(b)/stroke_d:.2f}x); fired bow rise "
              f"{fired_bow_rise(b, stroke_d):.2f} mm from h0 {H0:.1f} mm")
        print(f"  wire mass {wire_mass_g(d, l):.2f} g x8 = "
              f"{8*wire_mass_g(d, l):.1f} g/aircraft")
        # LG-18/LG-10 consequence: the exposed span between socket mouths is
        # what sets how far up the bay plate the wire boss sits, and hence the
        # bay plate length.  Reported here so the SCAD can be read off it.
        print(f"  bay boss station: exposed span {l - 2*SEAT_DUCTILE:.0f} mm "
              f"from the thigh socket mouth along CHORD_AZ "
              f"(sets BAY_PLATE_L; was 59 mm)")

        print(f"  This wire (P={p_wire:.0f} N) on the shared R_h "
              f"{R_H_BUILT:.0f} mm lever -- variants differ only in clearance:")
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
    # 1.2x stroke reserve so the spring never approaches the bow-model limit
    b_s = solve_bow_span(stroke_s, STROKE_RESERVE_SPRING)
    l_s = b_s + 2.0 * (SEAT_SPRING + END_RUN_IN)
    print(f"\n--- SPRING schedule (elastic phase, solved at {DESIGN_VARIANT}) "
          + "-" * 12)
    print(f"  per-leg elastic energy {u_spring_leg:.2f} J -> per wire "
          f"{u_spring_wire:.3f} J")
    print(f"  elastic-limit target {f_leg_el:.0f} N/leg -> wire P "
          f"{p_spring:.1f} N")
    print(f"  wire: d {d_s:.2f} mm, bow span {b_s:.0f} mm, stock L {l_s:.0f} "
          f"mm (straight seat ends), h0 {H0} mm, stroke "
          f"{stroke_s:.2f} mm (avail {wire_stroke_available(b_s):.2f}, "
          f"{wire_stroke_available(b_s)/stroke_s:.2f}x)")
    print(f"  bow rise at the elastic-limit stroke "
          f"{fired_bow_rise(b_s, stroke_s):.2f} mm  (H_DEF_SPRING in the SCAD)")
    print(f"  wire mass {wire_mass_g(d_s, l_s):.2f} g x8 = "
          f"{8*wire_mass_g(d_s, l_s):.1f} g/aircraft")
    print(f"  bay boss station: exposed span {l_s - 2*SEAT_SPRING:.0f} mm "
          f"along CHORD_AZ (was 27 mm)")
    print("  Reusing this wire in every variant:")
    for name, (r_h, clearance) in LEG_VARIANTS.items():
        f_leg = 2.0 * p_spring * R_WIRE / r_h
        settle_el = u_spring_leg * 1000.0 / f_leg
        print(f"    {name:6s} R_h {r_h:5.1f} mm: elastic-limit force "
              f"{f_leg:6.1f} N/leg, settle at limit {settle_el:4.1f} mm, "
              f"onset decel (level) {4*f_leg/w_n:5.1f} g")

    # Structure checks -- run at the ADOPTED drop schedule, per variant.
    # Hip bending moment M = 2*P*r is wire-side only (independent of R_h),
    # so the thigh margin is IDENTICAL across variants; everything else
    # that depends on F_leg (hip pin, lateral case, static stance) is
    # reported per variant.
    #
    # These were pinned to 6 ft with a hardcoded 800 N target, which was the
    # design point only until LG-17 closed at 4 ft (2026-08-09).  Under the
    # clearance-driven wire rule the retired 6 ft case now demands d 4.88 mm
    # and M 64.0 N*m, which OVERSTRESSES the thigh (sigma 28.8 vs 27.5 MPa,
    # margin 0.95x).  Reporting structure margins at a superseded drop height
    # is how a "passing" number outlives the decision that invalidated it.
    ADOPTED_DROP_FT = 4.0
    u_ref = M_AUW_KG * G * ADOPTED_DROP_FT * FT * 0.5
    d_ref, b_ref, l_ref, p_ref, _ = solve_ductile_wire(
        u_ref / 2.0, u_ref * 1000.0 / settle_max, R_H_BUILT)
    m_hip = 2.0 * p_ref * R_WIRE                            # N*mm, all variants
    d_cyl, c_ctr = 14.0, 18.0
    # LG-18: the thigh cylinders are BORED to save mass.  The bore is carried
    # here, not asserted in the SCAD, so the section margin is regenerated from
    # whatever diameter the geometry actually uses.  Set 0.0 for a solid thigh.
    d_bore = THIGH_BORE_D
    r_c = d_cyl / 2.0
    a_circ = math.pi * (r_c**2 - (d_bore / 2.0)**2)
    i_circ = math.pi * (d_cyl**4 - d_bore**4) / 64.0
    i_pair = 2.0 * (i_circ + a_circ * (c_ctr / 2.0)**2)
    i_web = d_cyl * c_ctr**3 / 12.0
    i_tot = i_pair + i_web
    c_out = c_ctr / 2.0 + r_c
    z_mod = i_tot / c_out
    sigma = m_hip / z_mod
    print(f"\n--- Structure checks ({ADOPTED_DROP_FT:.0f} ft adopted schedule, "
          f"both variants) " + "-" * 8)
    print(f"  thigh @hip: M {m_hip/1000:.1f} N*m (= 2*P*r, R_h-INDEPENDENT -- "
          f"same for every variant), section 2x{d_cyl:.0f} mm cyl @ "
          f"{c_ctr:.0f} mm ctrs (bore {d_bore:.0f}) + web -> Z {z_mod:.0f} "
          f"mm^3, sigma "
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
    if "--derive-stroke" in sys.argv:
        derive_stroke_relation()
    else:
        main()
        # lg02_bay_attachment() was defined but never invoked -- its numbers
        # were quoted in docs/LANDING_GEAR_ANALYSIS.md while nothing regenerated
        # them, so they silently went stale across LG-17 and LG-10.2.  It now
        # runs with every sizing pass.
        lg02_bay_attachment()
