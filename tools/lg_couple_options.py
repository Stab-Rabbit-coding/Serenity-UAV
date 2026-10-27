#!/usr/bin/python3
"""Option A sub-forms: free-body, materials and packaging trade (LG-LOADPATH).

Owner 2026-10-27: Option A (balanced couple) is selected; keep the gear as
close to canon as possible.  QMx Sheet 5 "Detail of Landing Gear" [REF-CAD-003]
and the Henning renders [REF-CAD-002] show the upper leg as a bundle of
parallel cylinders (barrel + jack + accumulator) running along the strut from
a hull housing to a knee with two drum joints, on a three-toed foot.  Three
ways to build the couple are compared on the same load cases:

  A1 PUSH-PULL   per row, one TENSION and one COMPRESSION member either side
                 of the hip pin, both anchored INBOARD along the strut line
                 (reads as the canonical jack).  Tension = 6061-T6 axial fuse;
                 compression = 6061-T6 bowed wire (plastic hinges).
  A2 SPLIT       the study's geometry: antiparallel chords, both TENSION
                 fuses; the anchors are point-symmetric about the pin, so one
                 lies inboard and one outboard of it.
  A3 AXIAL JACK  shock path along the strut: a telescoping member whose line
                 passes through the foot contact, fuse inside it.

Free body (each option): isolate the thigh + lower leg (one rigid body in the
crash stroke).  External: foot reaction F (vertical, at R_H, FOOT_Z), member
forces at their attachment points, hip pin reaction.  2-D, three equations;
with the member forces fixed by the fuse plateau the pin reaction is
determinate.

Materials (cited only):
  6061-T6  Sy 276 MPa, Su 310 MPa, elongation 17 %, shear Su 207 MPa,
           density 2.70 g/cm^3  [REF-MAT-007]
  A228     230 ksi (1,586 MPa) min tensile (no published yield)  [REF-MAT-008]
  CF-PETG  47 MPa bulk compression, flat contact only  [REF-MAT-001]
Bowed-wire plateau P = 2 Mp / h, Mp = Sy d^3 / 6 (two-hinge mechanism; the
plastic-hinge length L_p = d is a design assumption, REQUIRES VERIFICATION by
the LG-15 bench firing).  Tension fuse: P = Sy A, gauge = 1.5 x stroke / elong.

Run:  /usr/bin/python3 tools/lg_couple_options.py [--svg PATH]

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-27, per AGENTS.md section 3 AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import math
import sys

import lg_bellcrank_fbd as fbd      # load cases, pin/liner/spreader sizing

SY, SU, ELONG, SS = 276.0, 310.0, 0.17, 207.0   # 6061-T6  [REF-MAT-007]
RHO = 2.70e-3                                   # g/mm^3   [REF-MAT-007]
SIG_PETG = 47.0                                 # MPa      [REF-MAT-001]
LBF = 4.44822
FLEX_RAD = math.radians(22.0)                   # hip rotation over the stroke
H0 = 3.5                                        # mm, bowed-wire pre-bend rise
SEAT = 10.0                                     # mm per end, seat + run-in
STRAIN_MARGIN = 1.5
THIGH = (59.0, -66.0)                           # knee, leg-local (leg SCAD)
APER_Z = (-38.0, 20.0)                          # bay aperture up the canted plate
LINER_DEPTH = 7.0                               # mm inboard (COWL_H)
HIP_ABOVE_BELLY = 38.0                          # mm (leg SCAD)


def tension_fuse(p, stroke):
    """6061-T6 axial fuse: diameter, gauge, mass (g) for plateau p (N)."""
    d = math.sqrt(4 * p / (math.pi * SY))
    gauge = STRAIN_MARGIN * stroke / ELONG
    return d, gauge, math.pi / 4 * d * d * (gauge + 2 * SEAT) * RHO


def bowed_fuse(p, stroke, span):
    """6061-T6 two-hinge bowed wire: d, rise at end, end/start force ratio, strain, g."""
    d = (3 * p * H0 / SY) ** (1 / 3)
    half = span / 2
    root = math.sqrt(half ** 2 - H0 ** 2) - stroke / 2
    hf = math.sqrt(max(half ** 2 - root ** 2, 0.0))
    eps = math.asin(hf / half) - math.asin(H0 / half)
    return d, hf, H0 / hf, eps, math.pi / 4 * d * d * (span + 2 * SEAT) * RHO


def pin_part(dem):
    """6061 hip pin (double shear) and ear liners: (pin d, liner t, margins)."""
    d = max(4, math.ceil(math.sqrt(dem / (2 * SS) * 4 / math.pi)))
    cap_pin = 2 * SS * math.pi / 4 * d * d
    t = 1.5
    cap_brg = 2 * t * d * SY
    return d, t, cap_pin / dem, cap_brg / dem


def spreader(p):
    """6061 disc under a member seat, sized to the CF-PETG flat-contact limit."""
    dia = 13.0
    while math.pi / 4 * dia * dia * SIG_PETG < 1.25 * p:
        dia += 1.0
    return dia, math.pi / 4 * dia * dia * SIG_PETG / p, math.pi / 4 * dia * dia * 1.5 * RHO


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--r", type=float, default=10.0, help="crank radius, mm")
    a = ap.parse_args(argv)
    C = fbd.cases()
    Fc, Fh = C["crash"]["F"], C["hier"]["F"]
    M = Fc * fbd.R_H                                     # N*mm about the hip
    r = a.r
    out = {}

    # ---------------- A1 push-pull ------------------------------------------
    p = M / (2 * r)                                      # each member of the couple
    stroke = r * FLEX_RAD
    dT, gT, mT = tension_fuse(p, stroke)
    dB, hf, ratio, eps, mB = bowed_fuse(p, stroke, 21.0)
    # Plateaus diverge as the bow deepens: tension flat (to necking, Su/Sy
    # 1.12 cap), bowed falls to H0/hf.  Mismatch flows through the pin.
    p_bow_end = p * ratio
    mism = max(p * (SU / SY) - p, p - p_bow_end)
    pin_dem = math.hypot(Fc, mism)
    pd, lt, mpin, mbrg = pin_part(1.25 * pin_dem)
    sd, msp, msm = spreader(p)
    anchor = math.hypot(r, gT + 2 * SEAT)
    out["A1 push-pull"] = dict(
        member=f"tension 6061 d{dT:.2f} gauge {gT:.1f} + bowed 6061 d{dB:.2f} span 21",
        P=p, stroke=stroke, pin=pin_dem, mism=mism, anchors="both inboard, along strut",
        anchor_r=anchor, fit="inside the hull along the strut line (canonical housing)",
        margins=dict(pin=mpin, liner=mbrg, spreader=msp,
                     bow_strain=ELONG / eps if eps else 0),
        mass=2 * (mT + mB) + 2 * 2 * msm, parts=2 * 2 + 2 * 2 + 3,
        canon="high: two parallel members along the strut read as barrel + jack",
        note=f"bowed plateau falls to {ratio:.2f} x start; mismatch {mism:.0f} N "
             f"goes through the pin; hinge strain {100 * eps:.1f} % (L_p = d assumed)")

    # ---------------- A1b push-pull, reversing sleeve -----------------------
    # The PUSH member is the same 6061 tension fuse inside a 6061 sleeve: the
    # sleeve takes the push and its far-end yoke pulls the fuse rod, so both
    # members are identical tension fuses with identical plateaus -> pure
    # couple.  The sleeve is the canonical jack barrel.  Sleeve sized for
    # compressive yield at 1.25 x the plateau; buckling needs E, which
    # REF-MAT-007's applied section does not give -> REQUIRES VERIFICATION.
    s_area = 1.25 * p / SY
    s_id = dT + 1.0
    s_od = math.ceil(math.sqrt(4 * s_area / math.pi + s_id ** 2))
    s_len = gT + 2 * SEAT + 10.0
    s_mass = math.pi / 4 * (s_od ** 2 - s_id ** 2) * s_len * RHO + 1.0   # + 1 g yoke
    pdb, ltb, mpinb, mbrgb = pin_part(1.25 * Fc)
    out["A1b push-pull, sleeve"] = dict(
        member=f"2 x tension 6061 d{dT:.2f} gauge {gT:.1f}; push side in 6061 sleeve "
               f"OD{s_od:.0f} x ID{s_id:.1f} x {s_len:.0f}",
        P=p, stroke=stroke, pin=Fc, mism=0.0, anchors="both inboard, along strut",
        anchor_r=math.hypot(r, s_len),
        fit="inside the hull along the strut line; needs the 3-D census (U1 gate)",
        margins=dict(pin=mpinb, liner=mbrgb, spreader=msp,
                     sleeve_yield=math.pi / 4 * (s_od ** 2 - s_id ** 2) * SY / p),
        mass=2 * 2 * mT + 2 * s_mass + 2 * 2 * msm, parts=2 * 2 + 2 * 2 + 2 + 3,
        canon="high: barrel (sleeve) + rod pair along the strut = canonical jack",
        note="identical fuses -> no plateau mismatch; sleeve buckling requires E (verify)")

    # ---------------- A2 split ---------------------------------------------
    p2 = M / (2 * r)
    dT2, gT2, mT2 = tension_fuse(p2, stroke)
    reach = math.hypot(r, gT2 + 2 * SEAT)                # each anchor from the pin
    lo_ok = reach < HIP_ABOVE_BELLY - 3                  # lower anchor above the belly?
    up_ok = reach < APER_Z[1] + LINER_DEPTH              # upper anchor in the liner?
    pd2, lt2, mpin2, mbrg2 = pin_part(1.25 * Fc)
    sd2, msp2, msm2 = spreader(p2)
    out["A2 split"] = dict(
        member=f"2 x tension 6061 d{dT2:.2f} gauge {gT2:.1f}", P=p2, stroke=stroke,
        pin=Fc, mism=0.0, anchors="point-symmetric: one inboard, one outboard",
        anchor_r=reach,
        fit=(f"anchors {reach:.0f} mm from the pin; the window is {APER_Z[0]:.0f}..+"
             f"{APER_Z[1]:.0f} mm with a {LINER_DEPTH:.0f} mm liner, hip {HIP_ABOVE_BELLY:.0f}"
             f" mm above the belly -> {'fits' if lo_ok and up_ok else 'DOES NOT FIT'}"),
        margins=dict(pin=mpin2, liner=mbrg2, spreader=msp2),
        mass=2 * 2 * mT2 + 2 * 2 * msm2, parts=2 * 2 + 2 * 2 + 3,
        canon="low: one anchor outboard of the skin, crossing members not in canon",
        note="pure couple; simplest mechanics")

    # ---------------- A3 axial jack ----------------------------------------
    fx, fz = fbd.R_H, -fbd.FOOT_Z
    ang = math.atan2(fx, fz)                             # strut line through the foot
    J = Fc / math.cos(ang)
    stroke3 = fbd.SETTLE_CRASH * math.cos(ang)
    dT3, gT3, mT3 = tension_fuse(J, stroke3)
    strut_len = math.hypot(fx, fz)
    pd3, lt3, mpin3, mbrg3 = pin_part(1.25 * J)
    tube = 2 * math.pi / 4 * (12 ** 2 - 10 ** 2) * strut_len * RHO   # 6061 12x1 telescoping pair
    out["A3 axial jack"] = dict(
        member=f"tension 6061 d{dT3:.2f}, gauge {gT3:.0f} mm needed", P=J, stroke=stroke3,
        pin=J, mism=0.0, anchors="hull housing on the strut line", anchor_r=strut_len,
        fit=(f"fuse gauge {gT3:.0f} mm vs strut {strut_len:.0f} mm -> "
             f"{'fits' if gT3 + 2 * SEAT < strut_len else 'DOES NOT FIT'}; "
             f"strut {math.degrees(ang):.0f} deg from vertical"),
        margins=dict(pin=mpin3, liner=mbrg3),
        mass=2 * mT3 / 2 + tube, parts=6,
        canon="highest: telescoping strut is the canonical upper leg",
        note=("long stroke at low force: a 6061 tension fuse needs a gauge longer "
              "than the leg; a compression crush absorber has no cited data here"))

    print("Crash, per leg: F %.0f N (%.1f lbf), E %.1f J, foot moment %.1f N*m (%.0f lbf*in)\n"
          % (Fc, Fc / LBF, C["crash"]["E"], M / 1000, M / 1000 * 8.8507))
    for k, v in out.items():
        print(f"== {k}")
        print(f"   members   {v['member']}")
        print(f"   member P  {v['P']:.0f} N ({v['P'] / LBF:.0f} lbf), stroke {v['stroke']:.1f} mm")
        print(f"   hip pin   {v['pin']:.0f} N ({v['pin'] / LBF:.0f} lbf)  [C0 today: 14,328 N]")
        print(f"   anchors   {v['anchors']}, {v['anchor_r']:.0f} mm from the pin")
        print(f"   packaging {v['fit']}")
        print("   margins   " + ", ".join(f"{m} {x:.2f}" for m, x in v["margins"].items()))
        print(f"   mass      {v['mass']:.1f} g/leg in fuses + spreaders/tubes "
              f"({4 * v['mass']:.0f} g/aircraft), {v['parts']} metal parts/leg")
        print(f"   canon     {v['canon']}")
        print(f"   note      {v['note']}\n")
    print(f"Hierarchy (leg-break F {Fh:.0f} N): every option's fuse plateau sets the foot "
          f"force at {Fc:.0f} N, {Fh / Fc:.2f} x below the leg break.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
