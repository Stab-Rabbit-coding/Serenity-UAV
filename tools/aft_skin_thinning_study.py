#!/usr/bin/env python3
"""aft_skin_thinning_study.py -- can the joined middle+rear SLS part use a thinner skin,
reinforced by an internal isogrid and/or foam, and what does it buy in hover CG?

Starts from the measured baseline (tools/aft_section_mass_audit.py,
docs/MASS_AUDIT_MIDDLE_REAR_SECTIONS.md) and the CG item list
(tools/sls_scale_trim_study.py).  Sizing checks, all closed-form:

  1. Crash-case bending moment along the part, M(y) = n*g*sum m_i (y_i - y) over every
     item aft of station y (plan 001 R7 design load factor n = 79.4), times the
     ultimate factor 1.5 [14 CFR 23.2230 / legacy 23.303 practice -- see REFERENCES].
  2. Skin bending stress in an equivalent circular tube, sigma = M / (pi R^2 t_m), where t_m
     is the membrane-equivalent thickness (skin + smeared ribs).
  3. Shell buckling in bending, classical sigma_cr = 0.605 E t / R with the NASA SP-8007
     (1968) bending knockdown gamma = 1 - 0.731 (1 - exp(-phi)), phi = sqrt(R/t)/16
     [REF-NASA-002].  Applied to the bare skin, which is conservative for a stiffened shell.
  4. Skin-pocket buckling between isogrid ribs: flat plate, simply supported, k = 4,
     sigma = k pi^2 E (t/b)^2 / (12 (1 - nu^2)), b = rib spacing (triangle height).
     Isogrid smeared rib thickness 3 b_r d / h follows the isogrid geometry of
     [REF-NASA-003]; this is a first-order smear, not the handbook's full method.
  5. Handling point load W on the skin: a simply supported circular plate with a central
     patch load, sigma = 3W/(2 pi t^2) [(1+nu) ln(a/r0) + 1] [REF-STR-001], where a is the
     pocket inradius h/3 and r0 is the contact radius.
  6. First bending mode of the aft part as a uniform cantilever from Y 436,
     f1 = (1.875^2 / 2 pi) sqrt(EI / (mu L^4)), with the shell mass plus the carried items
     smeared along it [REF-STR-001].

Material: DuraForm PA CF [3DS-30108A]: E = 7,000 MPa flexural (the lower of the tensile
and flexural moduli), sigma_u = 84 MPa tensile.  Z-direction (build-axis) values are not
published, so a 0.5 knockdown on strength is applied [ASSUMED].

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction, 2026-10-31.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import itertools
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sls_scale_trim_study as s

G = 9.80665
N_CRASH = 79.4           # plan 001 R7 design load factor
FS_ULT = 1.5             # ultimate factor
E = 7000.0               # MPa, PA CF flexural [3DS-30108A]
SU = 84.0                # MPa, PA CF tensile ultimate [3DS-30108A]
KZ = 0.5                 # build-axis strength knockdown [ASSUMED]
NU = 0.35                # Poisson ratio, nylon [ASSUMED]
RHO = 1.11e-3            # g/mm^3 PA CF
RHO_FOAM = 32.04e-6      # g/mm^3, 2 lb/ft^3 PU (FOAM-PU-2LB, bom_revS.csv)
Y0, Y1 = 436.0, 690.0    # joined part, the Y 436 joint to the tail
W_HANDLE = 89.0          # N (20 lbf) fingertip handling load [ASSUMED]
R_CONTACT = 5.0          # mm contact radius [ASSUMED]

# Baseline band masses at 1.05 g/cc (docs/MASS_AUDIT_MIDDLE_REAR_SECTIONS.md section 2.1)
# as (y_lo, mass_g, band_mean_t_mm, keep_full_wall).  Keep bands: the Y 436 joint land,
# the horseshoe ring (450-460, 480-490) and the ring-frame pocket (590-600).
# Owner, 2026-10-31: in the one-piece part the ring and skids are ONE continuous member,
# so there is no ring-to-skid attachment and the old stanchion bands (610-630) and the
# deleted collar lands (500-520) are no longer kept.
BANDS = [
    (436.7, 6.6, 1.54, True), (440, 18.5, 2.04, True), (450, 28.8, 2.37, True),
    (460, 31.6, 2.15, False), (470, 23.5, 1.82, False), (480, 35.8, 2.34, True),
    (490, 21.7, 2.63, False), (500, 16.7, 2.54, False), (510, 20.4, 2.63, False),
    (520, 13.8, 1.92, False), (530, 16.2, 2.10, False), (540, 17.1, 2.21, False),
    (550, 16.1, 2.03, False), (560, 13.6, 2.01, False), (570, 13.2, 2.07, False),
    (580, 13.3, 2.05, False), (590, 12.5, 1.90, True), (600, 12.3, 2.09, False),
    (610, 15.2, 2.42, False), (620, 15.8, 2.54, False), (630, 11.1, 2.00, False),
    (640, 10.4, 2.02, False), (650, 12.5, 2.11, False), (660, 11.6, 2.78, False),
    (670, 4.4, 2.49, False), (680, 1.9, 2.98, False),
]
# Skid-tube mass per band (g, 1.05 g/cc), measured: hollow tubes at X +/-35..58,
# Z 88..112, continuous from the ring (Y ~480) to Y ~665; total 56.9 g.  Held at full
# section in every band -- they carry the landing load, they are not skin.
SKID = {480: 1.5, 490: 7.3, 500: 3.3, 510: 4.4, 520: 2.9, 530: 2.8, 540: 2.8, 550: 2.9,
        560: 2.9, 570: 2.9, 580: 2.9, 590: 2.8, 600: 2.7, 610: 2.9, 620: 3.0, 630: 2.3,
        640: 2.2, 650: 2.2, 660: 2.0}
BRIDGE_G = 5637 * 1.05e-3
# Equivalent tube radius per station, R = (W + H) / 4 from the audit's section table.
RADIUS = [(440, 77), (460, 83), (480, 84), (500, 66), (520, 73), (560, 73), (600, 63),
          (640, 58), (680, 47)]
SHELLS = ("middle_shell24_2mm_repaired", "rear_shell24_2mm_repaired",
          "middle_rear_splice_collar")


def radius(y):
    """Linear interpolation of the equivalent tube radius (mm)."""
    for (ya, ra), (yb, rb) in zip(RADIUS, RADIUS[1:]):
        if ya <= y <= yb:
            return ra + (rb - ra) * (y - ya) / (yb - ya)
    return RADIUS[0][1] if y < RADIUS[0][0] else RADIUS[-1][1]


_ENTRIES = []


def entries():
    """Ledger CG items, built once (the build loads meshes)."""
    if not _ENTRIES:
        _ENTRIES.extend(s.entries())
    return _ENTRIES


def carried_items():
    """Ledger items aft of Y0 that are not hull shells: (m g, y)."""
    return [(m, y) for n, _k, m, y in entries() if y > Y0 and n not in SHELLS]


def part_mass(t_s, rib):
    """Joined-part mass (g, PA CF) and band list for skin t_s with an isogrid
    rib = (b_r, d, h) or None.  Acreage bands scale by t_eq / t_band."""
    t_eq = t_s + (3 * rib[0] * rib[1] / rib[2] if rib else 0.0)
    out = []
    for y, m, t, keep in BANDS:
        sk = SKID.get(int(y), 0.0)
        m2 = m if keep else sk + (m - sk) * min(1.0, t_eq / t)
        out.append((y + 5, m2 * RHO / 1.05e-3))
    out.append((509.0, BRIDGE_G * RHO / 1.05e-3))
    return sum(m for _y, m in out), out, t_eq


def moment(y, shell_bands):
    """Crash bending moment (N.mm) at station y, ultimate."""
    items = carried_items() + [(m, yy) for yy, m in shell_bands]
    return FS_ULT * N_CRASH * G * sum(m / 1000 * (yy - y) for m, yy in items if yy > y)


def check(t_s, rib, label):
    """Run checks 2-6 for one candidate; return the minimum margin and the mass."""
    mass, sb, t_eq = part_mass(t_s, rib)
    worst = (math.inf, None)
    for y in range(int(Y0) + 4, 680, 4):
        r = radius(y)
        m_y = moment(y, sb)
        sig = m_y / (math.pi * r * r * t_eq)
        phi = math.sqrt(r / t_s) / 16
        gam = 1 - 0.731 * (1 - math.exp(-phi))
        scr = gam * 0.605 * E * t_s / r
        allow = min(KZ * SU, scr)
        if rib:
            b = rib[2]
            spk = 4 * math.pi ** 2 * E * (t_s / b) ** 2 / (12 * (1 - NU ** 2))
            allow = min(allow, spk)
        ms = allow / sig - 1
        if ms < worst[0]:
            worst = (ms, y, sig, allow)
    a = rib[2] / 3 if rib else 40.0  # unstiffened: a 40 mm panel radius [ASSUMED]
    a = max(a, R_CONTACT * 1.01)
    sh = 3 * W_HANDLE / (2 * math.pi * t_s ** 2) * ((1 + NU) * math.log(a / R_CONTACT) + 1)
    ms_h = KZ * SU / sh - 1
    # First bending mode, uniform cantilever of length L, mean radius, membrane t_eq.
    L = Y1 - Y0
    rm = sum(radius(y) for y in range(int(Y0), int(Y1), 10)) / len(range(int(Y0), int(Y1), 10))
    ei = E * math.pi * rm ** 3 * t_eq                      # N.mm^2
    mu = (mass + sum(m for m, _ in carried_items())) / 1000 / L   # kg/mm
    f1 = 1.875 ** 2 / (2 * math.pi) * math.sqrt(ei * 1e3 / (mu * L ** 4))  # Hz (N=kg.m/s2)
    print(f"  {label:34s} t_eq {t_eq:4.2f}  part {mass:6.1f} g  MS_bend/buckle {worst[0]:+7.1f} "
          f"@Y{worst[1]}  MS_handle {ms_h:+5.2f}  f1 {f1:5.0f} Hz")
    return mass, sb


def cg_effect(sb, label):
    """Hover CG offset with the joined part replaced by these band masses."""
    es = [e for e in entries() if e[0] not in SHELLS] + [(f"band{y}", "PRINT", m, y) for y, m in sb]
    w = sum(e[2] for e in es)
    yc = sum(e[2] * e[3] for e in es) / w
    f = _nac_frac(es)
    print(f"     {label}: AUW {w:.0f} g, offset {yc - s.PIVOT:+.1f} mm; "
          f"with the single pivot 0.5 in aft {yc - s.PIVOT - 12.7 * (1 - f):+.1f} mm")


def _nac_frac(es):
    """Nacelle mass fraction: the nacelles ride the pivot when it moves."""
    return sum(e[2] for e in es if e[1] == "NACELLE") / sum(e[2] for e in es)


def main():
    print(f"Ultimate crash moment at Y {Y0:.0f}, baseline 2 mm part: "
          f"{moment(Y0 + 0.1, part_mass(2.0, None)[1]) / 1000:.1f} N.m")
    print("\nCandidates (PA CF, Z knockdown 0.5, handling 20 lbf on a 5 mm radius patch):")
    cands = [
        (2.0, None, "baseline 2.0 mm, no ribs"),
        (1.2, None, "1.2 mm unstiffened"),
        (1.0, None, "1.0 mm unstiffened"),
        (0.8, None, "0.8 mm unstiffened"),
        (0.8, (1.0, 4.0, 30.0), "0.8 + isogrid 1.0x4 @30"),
        (1.0, (1.0, 4.0, 30.0), "1.0 + isogrid 1.0x4 @30"),
        (1.0, (1.0, 4.0, 40.0), "1.0 + isogrid 1.0x4 @40"),
        (1.0, (1.2, 5.0, 45.0), "1.0 + isogrid 1.2x5 @45"),
        (1.2, (1.0, 4.0, 45.0), "1.2 + isogrid 1.0x4 @45"),
    ]
    res = {}
    for t, rib, lab in cands:
        res[lab] = check(t, rib, lab)
    print("\nHover CG (relocated baseline; joined part replaces middle+rear+collar):")
    for lab in ("baseline 2.0 mm, no ribs", "1.0 + isogrid 1.0x4 @30", "1.0 + isogrid 1.0x4 @40",
                "0.8 + isogrid 1.0x4 @30"):
        cg_effect(res[lab][1], lab)

    print("\nFoam fill (2 lb/ft3 PU) -- mass and moment cost:")
    for lab, vol, yc in (("rear cavity, full", 2.110e6, 586.7), ("middle cavity, full", 1.273e6, 473.2),
                         ("5 mm liner on rear acreage", 0.5 * 205195 * 0.7 * 5, 586.7)):
        m = vol * RHO_FOAM
        print(f"  {lab:28s} {m:5.1f} g at Y {yc:.0f}: +{m * (yc - s.PIVOT):6.0f} g.mm aft")


if __name__ == "__main__":
    main()
