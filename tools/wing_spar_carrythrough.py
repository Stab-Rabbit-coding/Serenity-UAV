#!/usr/bin/env python3
"""Does the rotating wing spar have to span the fuselage?  First-principles check.

Question (owner, 2026-08-23)
---------------------------
The 8 mm steel wing spars are to rotate **independently**, driven by the nacelle
servos, on two bearings each: one at the wingtip and one in the fuselage side.
Is there a structural requirement for the spars to carry through the fuselage --
and if not, does the section need a CF thwart or rib fore and aft of the cargo
bay to replace the carry-through's stiffness?

This matters beyond the wing: the spar is what obstructs the cargo bay
(CARGO-01, `airframe/fuselage-mid/WBS.md` SS1.1.1.2).  A spar that stops at the
fuselage wall clears the bay.

Model
-----
Per side the spar is an **overhung shaft**, not a beam spanning the ship:

        fuselage bearing        wingtip bearing      nacelle load line
             X_f  o---------------- L ----o------ a ------X  F
                  (in the wall)         (wing tip)     (duct axis)

with the nacelle load F applied on the overhang.  Statics give

    R_tip =  F (L + a) / L          (up, into the wing tip)
    R_fus = -F a / L                (down, into the fuselage wall)
    M_spar =  F a                   (maximum, at the wingtip bearing)

Both bearings sit at or outboard of the fuselage wall, so the spar is fully
determinate without a second inboard support.  Nothing about the spar's own
statics needs the far side of the ship.

What DOES cross the ship is the couple.  Each side delivers to its wall

    V_wall = F                      (vertical shear)
    M_wall = F d                    (roll couple about the hull Y axis)

and in symmetric flight the port and starboard couples are equal and opposite.
A conventional carry-through spar short-circuits that pair through a straight
member.  With independently rotating spars a straight member is impossible --
two coaxial shafts cannot be one rigid beam and still rotate independently --
so the couple has to be closed by the **section** instead: a ring frame, or a
transverse thwart.  This tool sizes that member and finds the stations where it
will actually fit.

Load cases
----------
AUW is taken from `README.md` (BOM-derived, Phase 5-10) rather than from
`docs/structural_analysis.md` SS2, whose back-calculated figure differs and whose
SS3-SS7 load cases are flagged in that document as stale (computed from a
superseded, doubled mass budget).  The 4 g limit factor (3 g gust + 1 g
maneuver) and the 1.5 ultimate factor are the ones structural_analysis.md SS3
states.

Geometry is measured from the baked STLs, not assumed.

Run:
    /usr/bin/python3 tools/wing_spar_carrythrough.py
    /usr/bin/python3 tools/wing_spar_carrythrough.py --stations   (thwart sites)

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Analysis implemented by Claude (model: Claude Opus 5, Anthropic) under
         the author's direction, per `AGENTS.md` SS3 "Attribution and Licensing".
License: CC BY-SA 4.0 - creativecommons.org/licenses/by-sa/4.0
"""

import math
import os
import sys

import numpy as np
import trimesh

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STL = {
    "shell": "airframe/stls/fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl",
    "wing_port": "airframe/stls/wings/wing_port_s1223_revo.stl",
    "nacelle_port": "airframe/stls/nacelles/nacelle_port_revs.stl",
}

sys.path.insert(0, os.path.join(REPO_ROOT, "airframe", "blender-scripts"))
import merge_cargo_interior as mci  # noqa: E402

# --- loads -----------------------------------------------------------------
G = 9.80665
AUW_KG = 3.911                      # README.md, Phase 5-10 BOM-derived AUW
N_NACELLES = 2                      # AGENTS.md propulsion baseline
LIMIT_FACTOR = 4.0                  # 3 g gust + 1 g maneuver
ULTIMATE_FACTOR = 1.5

# --- spar section ----------------------------------------------------------
# REV T1 (2026-08-29, plan 003 KTD1/KTD4): the spar is a FIXED 20 x 16.3 mm
# roll-wrapped CARBON FIBRE tube, not the Rev R2 8 x 1.5 rotating 4130 shaft.
# Three things change together and they are not independent:
#
#   * SECTION.  Z goes 42.6 -> 438.9 mm^3, a 10.3x increase, because the tube
#     is now sized by the WIRE BUNDLE it carries (tools/spar_bundle_fit.py),
#     not by the torque it transmits.  It transmits none: the nacelle pivots
#     on its own trunnion ring, so the spar carries bending only.
#   * MATERIAL.  CF was rejected in TILT_SPAR_ANALYSIS.md SS3.5 on a FUNCTIONAL
#     gate -- "delaminates at a keyway" -- not on strength.  A fixed spar has
#     no keyway and no bearing journal, so that gate does not apply and CF's
#     mass advantage becomes available: 67.5 g/pair against 96.2 g for the
#     steel it replaces, i.e. the bigger spar is also the LIGHTER one.
#   * LOAD PATH.  See report_spar_carrythrough_joint().
#
# ALLOWABLE IS UNVERIFIED.  300 MPa is the same deliberately conservative
# cross-ply stand-in CF_ALLOW uses for the thwart plate, carried over because
# the repo still has no ASTM D3039/D695 certificate for any CF stock (plan 003
# DEP-1; REFERENCES.md "requires verification").  Do not quote the FOS below
# as qualified.
SPAR_OD, SPAR_ID = 20.0, 16.3
SPAR_I = math.pi * (SPAR_OD ** 4 - SPAR_ID ** 4) / 64.0    # mm^4
SPAR_Z = SPAR_I / (SPAR_OD / 2.0)                          # mm^3
SPAR_ALLOW = 300.0                  # MPa -- REQUIRES VERIFICATION (DEP-1)
SPAR_RHO = 1.60e-3                  # g/mm^3, roll-wrapped CF

# Superseded Rev R2 section, retained so the comparison in the report is
# against a real previous figure rather than a remembered one.
LEGACY_OD, LEGACY_ID = 8.0, 5.0
LEGACY_Z = (math.pi * (LEGACY_OD ** 4 - LEGACY_ID ** 4) / 64.0) / (LEGACY_OD / 2.0)
LEGACY_RHO = 7.85e-3                # g/mm^3, AISI 4130
# MPa, 4130 normalized (typical -- MMPDS; tracked in the root work-tracking
# file SS0.8).  Retained: the legacy comparison row still cites it.
STEEL_YIELD = 460.0

# --- candidate thwart section ---------------------------------------------
THWART_T = 2.0                      # mm, CF-PLATE-2MM (already in the BOM)
THWART_H = 25.0                     # mm, depth in the plane of the section
# CF plate bending allowable.  `docs/structural_analysis.md` SS1 carries the repo's
# only CF basis -- sigma_u ~= 1500 MPa for UNIDIRECTIONAL pultruded stock, itself
# marked "supplier test certificates (ASTM D3039 / D695) must be obtained and
# verified before fabrication".  A cross-ply plate loaded in bending across the
# ship is NOT that layup, so 300 MPa is used here as a deliberately conservative
# stand-in, a factor of 5 below the unidirectional figure.  It is NOT a verified
# allowable: see REFERENCES.md "requires verification" and the root
# work-tracking file SS0.8.
CF_ALLOW = 300.0                    # MPa -- REQUIRES VERIFICATION
CF_ALLOW_UNI = 1500.0               # MPa -- structural_analysis.md SS1, also unverified


def load(key):
    return trimesh.load(os.path.join(REPO_ROOT, STL[key]), force="mesh")


def measure_geometry():
    """Spanwise stations, hull frame (X positive = port), from the baked STLs."""
    wing = load("wing_port")
    nac = load("nacelle_port")
    shell = load("shell")

    wing_tip_x = float(wing.bounds[1][0])            # tip face
    nac_axis_x = float(nac.bounds[0][0] + nac.bounds[1][0]) / 2.0
    # Port wall skin: the outboard-most shell material at the spar station.
    v = shell.vertices
    band = (np.abs(v[:, 1] - mci.WING_SPAR_Y) < 4.0) & \
           (np.abs(v[:, 2] - mci.WING_SPAR_Z) < 12.0) & (v[:, 0] > -170.0)
    wall_x = float(v[band, 0].max()) if band.any() else -85.0
    # Fuselage bearing seat: mid-way along the existing spar boss embed span.
    bearing_x = (mci.PORT_INB + mci.PORT_OUTB) / 2.0
    return {
        "wall_x": wall_x,
        "bearing_x": bearing_x,
        "wing_tip_x": wing_tip_x,
        "nac_axis_x": nac_axis_x,
        "L": wing_tip_x - bearing_x,
        "a": nac_axis_x - wing_tip_x,
        "d": nac_axis_x - wall_x,
        "spar_inboard_end": mci.PORT_INB,
    }


def spar_case(f_newton, geom):
    """Overhung-shaft reactions and spar bending for one side."""
    L, a = geom["L"], geom["a"]
    r_tip = f_newton * (L + a) / L
    r_fus = -f_newton * a / L
    m_spar = f_newton * a / 1000.0                 # N.m
    sigma = (m_spar * 1000.0) / SPAR_Z             # MPa
    return r_tip, r_fus, m_spar, sigma


def report_loads(geom):
    per_side_1g = AUW_KG * G / N_NACELLES
    limit = per_side_1g * LIMIT_FACTOR
    ultimate = limit * ULTIMATE_FACTOR

    print("\nLoad cases (per side; AUW 3.911 kg = 8.62 lbm, README.md)")
    print(f"  1 g, one nacelle carrying half AUW   {per_side_1g:7.1f} N "
          f"({per_side_1g / 4.44822:5.2f} lbf)")
    print(f"  limit  ({LIMIT_FACTOR:.0f} g gust + maneuver)        "
          f"{limit:7.1f} N ({limit / 4.44822:5.2f} lbf)")
    print(f"  ultimate (x{ULTIMATE_FACTOR})                     "
          f"{ultimate:7.1f} N ({ultimate / 4.44822:5.2f} lbf)")

    print("\nSpar as an overhung shaft (no carry-through)")
    print(f"  span  L (fuselage bearing -> wingtip)  {geom['L']:6.1f} mm")
    print(f"  overhang a (wingtip -> nacelle axis)   {geom['a']:6.1f} mm")
    print(f"  arm   d (wall -> nacelle axis)         {geom['d']:6.1f} mm")
    print(f"\n  section {SPAR_OD:.0f} x {SPAR_ID:.1f} CF (fixed, Rev T1):  "
          f"I {SPAR_I:.0f} mm^4   Z {SPAR_Z:.1f} mm^3")
    print(f"    superseded 8 x 1.5 4130 had Z {LEGACY_Z:.1f} mm^3 "
          f"-- section modulus up {SPAR_Z / LEGACY_Z:.1f}x")
    print(f"\n{'case':>10s} {'R_tip N':>9s} {'R_fus N':>9s} "
          f"{'M_spar N.m':>11s} {'sigma MPa':>10s} {'FOS':>6s}")
    for tag, f in (("1 g", per_side_1g), ("limit", limit), ("ultimate", ultimate)):
        r_tip, r_fus, m_spar, sigma = spar_case(f, geom)
        print(f"{tag:>10s} {r_tip:9.1f} {r_fus:9.1f} {m_spar:11.2f} "
              f"{sigma:10.1f} {SPAR_ALLOW / sigma:6.1f}")
    return limit, ultimate


def report_couple(geom, limit, ultimate):
    """The couple each side hands to its wall -- what a carry-through would close."""
    print("\nCouple delivered to each fuselage wall (what carry-through would close)")
    for tag, f in (("limit", limit), ("ultimate", ultimate)):
        m_wall = f * geom["d"] / 1000.0
        print(f"  {tag:>8s}:  V {f:6.1f} N   M {m_wall:6.2f} N.m "
              f"({m_wall * 8.85075:6.1f} lbf.in)")
    return ultimate * geom["d"] / 1000.0


def report_root_joint(geom, limit, ultimate):
    """Wing-root joint: two-rod couple (U5/KTD1 default) or enlarged tenon.

    Owner, 2026-08-23: "that mortise/tenon joint provides part of the structural
    joint at the wing root, since the wings don't rotate with the nacelles."
    That started the CARGO-03c investigation, which found the tenon
    under-strength as a structural joint (FOS 0.49 against the repo's only
    CF-PETG figure) and, per the owner's <15 MPa decision rule, routed the
    load to bonded CF rods instead.  A further 2026-08-24 refinement found a
    single rod insufficient (an aft rod matching the forward rod's diameter
    does not fit anywhere) and settled on a TWO-ROD couple, asymmetric
    diameter, with the tenon traded OUT of the load path entirely and
    restored to its original locating-only role.  This function now reports
    that two-rod couple under `TENON_LOAD_PATH = "two_rod"` (the wing SCAD's
    default), and falls back to the superseded single-tenon sizing sweep
    under `"enlarged_tenon"` so that alternate path stays reportable too.
    """
    import re
    wing_scad = os.path.join(REPO_ROOT, "airframe", "openscad", "wings",
                             "wings_s1223_revo.scad")
    with open(wing_scad, encoding="utf-8") as fh:
        src = fh.read()

    def scad(name):
        m = re.search(rf"^{name}\s*=\s*(-?[\d.]+)\s*;", src, re.M)
        return float(m.group(1))

    def scad_str(name):
        m = re.search(rf'^{name}\s*=\s*"([^"]+)"\s*;', src, re.M)
        return m.group(1)

    load_path = scad_str("TENON_LOAD_PATH")
    arm = geom["wing_tip_x"] - geom["wall_x"]        # tip bearing -> root face

    print("\nWing root joint (per side)")
    print(f"  TENON_LOAD_PATH = \"{load_path}\"")
    print(f"  tip bearing to root face  {arm:6.1f} mm")
    print(f"\n{'case':>10s} {'R_tip N':>9s} {'root M N.m':>11s}")
    for tag, f in (("limit", limit), ("ultimate", ultimate)):
        r_tip, _rf, _m, _s = spar_case(f, geom)
        m_root = r_tip * arm / 1000.0
        print(f"{tag:>10s} {r_tip:9.1f} {m_root:11.2f}")

    r_tip_ult, _rf, _m, _s = spar_case(ultimate, geom)
    m_ult = r_tip_ult * arm / 1000.0                  # N.m, ultimate root moment

    if load_path == "spar_carrythrough":
        report_spar_carrythrough_joint(scad, m_ult, ultimate)
        return

    if load_path == "two_rod":
        report_two_rod_couple(src, m_ult)
        return

    report_enlarged_tenon(src, scad, m_ult)


def report_spar_carrythrough_joint(scad, m_ult, v_ult):
    """Rev T1 default: the FIXED spar itself is the wing-root load path.

    WHAT CHANGED, AND WHY IT IS NOT JUST A BIGGER ROD

    Under Rev R2 the spar was a rotating drive shaft.  It rode bearings at both
    ends, so by definition it could not react a root MOMENT -- a bearing
    transmits shear, not moment -- which is precisely why the root moment had
    to be routed somewhere else: first into an enlarged tenon (CARGO-03c, found
    at FOS 0.49), then into a two-rod bonded couple (U5/KTD1, FOS 4.14).  Both
    of those existed to work AROUND a spar that structurally could not help.

    Rev T1 removes that constraint at the source.  The spar is fixed and bonded
    over its full span, so it is a moment-carrying member, and the load path
    becomes nacelle -> trunnion -> spar -> fuselage socket.  The tenon and the
    tie rods are no longer in it.  That is not a strength upgrade to the old
    joint; it is a different joint.

    WHY THE TIE RODS RETIRE RATHER THAN BEING KEPT AS BACKUP

    1. The forward rod is physically impossible.  It sat at station 14.0 at
       D8.2 (spanning 9.9..18.1); the Rev T1 spar bore spans 17.80..38.20.
       They overlap.  There is no clearance version of the old joint.
    2. The aft rod is possible but purposeless.  Its remaining job would be
       reacting wing TORSION about the spar axis, and that load is negligible:
       see the torsion check below.
    3. Keeping an unnecessary bonded rod is not free -- it is a second bonded
       interface competing for the same root volume as the spar socket, and a
       stress riser in the skin at the station where the section is already
       thinnest.

    THE SOCKET MODEL

    A rigid pin in an elastic socket develops a roughly triangular pressure
    distribution on each side of the reversal point, with the two resultants
    landing at L/3 from each end -- an effective couple arm of 2L/3.  That is
    the standard conservative idealisation and it is what is used here:

        F     = 3M / (2L) + V/2
        area  = D . L/3            (projected bearing, the repo's own
                                    CARGO-03c convention)
        sigma = F / area

    Note sigma goes as 1/L^2, so socket LENGTH is the only effective lever --
    doubling it quarters the stress.  Diameter appears only linearly.

    ALLOWABLE.  5 MPa, the repo's standing bond-limited CF-PETG figure
    (docs/structural_analysis.md SS7.3), the same one CARGO-03c and the two-rod
    couple were sized against.  It is a conservative working placeholder that
    predates any cited source.  REF-MAT-001 gives a real ASTM D695 BULK
    COMPRESSIVE figure for 20 %-CF-PETG of ~47-60 MPa, and bearing of a bonded
    tube against a socket wall is a compressive mode rather than the bond/peel
    mode 5 MPa was written to bound -- so this socket is very likely far more
    conservative than it looks.  It is NOT re-based here: overturning a
    standing repo allowable is an owner decision gated on the LG-11 coupon
    (root TODO SS1.1.4), not a side effect of a geometry change.  The sweep
    below shows what that coupon would buy.
    """
    d_sock = scad("TILT_SPAR_OD")
    allow = 5.0
    m_nmm = m_ult * 1000.0

    def sigma_at(L):
        f = 3.0 * m_nmm / (2.0 * L) + v_ult / 2.0
        return f, d_sock * L / 3.0, f / (d_sock * L / 3.0)

    print("\nSpar carry-through joint (Rev T1) -- the spar IS the root load path")
    print(f"  fixed CF spar {SPAR_OD:.0f} x {SPAR_ID:.1f}, Z {SPAR_Z:.1f} mm^3")
    sig_spar = m_nmm / SPAR_Z
    print(f"  spar bending at the ultimate root moment ({m_ult:.2f} N.m):")
    print(f"    sigma {sig_spar:.2f} MPa   FOS {SPAR_ALLOW / sig_spar:.1f} "
          f"vs the {SPAR_ALLOW:.0f} MPa stand-in  (UNVERIFIED, DEP-1)")
    print("    this is the CANTILEVER bound -- the whole root moment taken by")
    print("    the spar alone.  The two-support bound (nacelle load reacted")
    print("    between the wingtip clamp and the wall) gives only "
          f"{v_ult * 38.3 / 1000.0:.2f} N.m,")
    print(f"    sigma {v_ult * 38.3 / SPAR_Z:.2f} MPa.  The cantilever bound is "
          "quoted because it")
    print("    does not depend on the wing skin sharing load, which is not")
    print("    characterised for a bonded printed skin.")

    print(f"\n  fuselage-side socket sizing (D{d_sock:.0f} bonded, "
          f"projected bearing vs {allow:.0f} MPa):")
    print(f"    {'L mm':>6s} {'F N':>8s} {'area mm2':>9s} "
          f"{'sigma MPa':>10s} {'FOS':>6s}")
    for L in (20.0, 30.0, 40.0, 50.0, 55.0, 60.0):
        f, a, sg = sigma_at(L)
        print(f"    {L:6.0f} {f:8.1f} {a:9.1f} {sg:10.3f} {allow / sg:6.2f}")

    lo, hi = 5.0, 200.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if allow / sigma_at(mid)[2] < 4.0:
            lo = mid
        else:
            hi = mid
    print(f"    -> socket length for the SS3 FOS 4.0 target: {hi:.1f} mm")
    print("    -> REQUIREMENT ON THE FUSELAGE: a bonded socket of at least")
    print(f"       {hi:.0f} mm spanwise reach inboard of the wall at the spar")
    print("       station.  This is a JOINT REQUIREMENT this file publishes;")
    print("       the fuselage owns building it (see the fuselage-mid WBS).")

    # What the LG-11 coupon would buy, if it lands.
    for alt, why in ((15.0, "the owner's <15 MPa fusion-strength decision rule"),
                     (47.0, "REF-MAT-001 ASTM D695 bulk compressive, 20 % CF-PETG")):
        lo2, hi2 = 5.0, 200.0
        for _ in range(200):
            mid = (lo2 + hi2) / 2.0
            if alt / sigma_at(mid)[2] < 4.0:
                lo2 = mid
            else:
                hi2 = mid
        print(f"    (at {alt:.0f} MPa -- {why}: {hi2:.0f} mm would do)")

    # Torsion: the only job the retired aft tie rod could still have had.
    q = 0.5 * 1.225 * (40.0 * 0.514444) ** 2          # Pa, 40 kt cruise
    s_half = 19025e-6 / 2.0                           # m^2, one wing panel
    c_mean = 0.111                                    # m, mean chord
    m_aero = 0.25 * q * s_half * c_mean               # N.m, Cm ~ 0.25
    m_tors = m_aero * LIMIT_FACTOR * ULTIMATE_FACTOR
    tau = m_tors * 1000.0 / (2.0 * math.pi * (d_sock / 2.0) ** 2 * 40.0)
    print("\n  wing torsion about the spar axis (the retired aft rod's only")
    print("  remaining candidate job):")
    ult_factor = LIMIT_FACTOR * ULTIMATE_FACTOR
    print(f"    Cm 0.25 at 40 kt -> {m_aero:.4f} N.m; "
          f"ultimate (x{ult_factor:.0f}) {m_tors:.3f} N.m")
    print(f"    bond shear over a 40 mm socket {tau:.4f} MPa "
          f"-> FOS {allow / tau:.0f} vs {allow:.0f} MPa")
    print("    NOTE thrust contributes no torque here: the duct axis passes")
    print("    through the pivot, which is on the spar axis (plan 003 R12).")
    print("    -> the aft tie rod is not needed for torsion either.  Retired.")


def report_two_rod_couple(src, m_ult):
    """U5/KTD1 default: two bonded CF rods react the root moment as a couple.

    Each rod is idealised as a simple bonded PIN -- shear-transferring only,
    no moment restraint credited (conservative; the bond's rotational
    stiffness at the wing root is not characterised).  The main spar bearing
    does NOT participate in this reaction: the wing rides on a rotating
    CLEARANCE bore around the tilt spar there (wing_tip_spar_through_bore()/
    the fuselage-side spar clearance bore), so it transmits no moment back to
    the wing about this axis.  The only two reaction points for the applied
    moment are therefore the forward and aft rods.

    Pure statics for a moment M reacted by exactly two point forces (no
    third reaction, pin supports only) requires the forces to be EQUAL in
    magnitude and opposite in sign, regardless of where either rod sits
    relative to the main spar:

        F_fwd + F_aft = 0                      (sum of forces = 0)
        M + F_aft . (x_aft - x_fwd) = 0         (sum of moments = 0, about x_fwd)
        => |F_fwd| = |F_aft| = M / (x_aft - x_fwd)

    This supersedes the single-rod method (`couple force = M / separation
    from the main spar`) that WBS.md's CARGO-03c first-pass table used: that
    formula implicitly treated the SPAR ITSELF as the second reaction point
    for a lone rod.  With two dedicated rods and a spar that does not react
    this moment, the spar drops out of the force balance entirely and the
    two rods alone carry it, in equal and opposite shares -- not a 50/50
    split by "share of the moment" (bearing stress still differs sharply
    between the two, because the rods differ in diameter and embed), but an
    equal split of FORCE, which is what the physics actually gives for two
    pin reactions.
    """
    import re

    def scad(name):
        m = re.search(rf"^{name}\s*=\s*(-?[\d.]+)\s*;", src, re.M)
        return float(m.group(1))

    x_fwd, d_fwd, l_fwd = (scad("ROD_FWD_STATION"), scad("ROD_FWD_D"),
                           scad("ROD_FWD_EMBED"))
    x_aft, d_aft, l_aft = (scad("ROD_AFT_STATION"), scad("ROD_AFT_D"),
                           scad("ROD_AFT_EMBED"))
    x_spar = scad("SPAR_BORE_STATION")
    sep = x_aft - x_fwd                               # mm, rod-to-rod lever arm

    print("\nTwo-rod couple (bonded CF tie rods, U5/KTD1) -- ultimate case")
    print(f"  forward rod: station {x_fwd:.1f} mm from LE, D {d_fwd:.1f} mm "
          f"(nominal {d_fwd - 0.2:.0f} mm CF rod), embed {l_fwd:.1f} mm")
    print(f"  aft rod:     station {x_aft:.1f} mm from LE, D {d_aft:.1f} mm "
          f"(nominal {d_aft - 0.2:.0f} mm CF rod), embed {l_aft:.1f} mm")
    print(f"  main spar station {x_spar:.2f} mm (reference only -- the spar "
          f"bearing does not react this moment, see docstring)")
    print(f"  rod-to-rod separation (couple lever arm)  {sep:.2f} mm")

    m_ult_mm = m_ult * 1000.0                         # N.mm
    f_couple = m_ult_mm / sep                         # N, equal at both rods

    print(f"\n  ultimate root moment M = {m_ult:.2f} N.m")
    print(f"  F = M / separation = {m_ult_mm:.0f} / {sep:.2f} "
          f"= {f_couple:.1f} N  (equal magnitude, both rods)")

    # Bearing stress = force / projected bearing area (diameter x embed),
    # using the NOMINAL rod OD (the actual bearing surface), not the
    # clearance bore.  Matches the WBS.md CARGO-03c table's own convention
    # (verified: 469 N / (8 mm x 40 mm) = 1.47 MPa there).
    allow = 5.0   # MPa, structural_analysis.md SS7.3 bond-limited CF-PETG/epoxy
    target_fos = 4.0   # structural_analysis.md SS3 joint FOS target
    print(f"\n{'rod':>6s} {'D nom':>6s} {'embed':>7s} {'F N':>8s} "
          f"{'sigma MPa':>10s} {'FOS vs {:.0f} MPa'.format(allow):>14s}   verdict")
    for tag, d, embed in (("fwd", d_fwd - 0.2, l_fwd), ("aft", d_aft - 0.2, l_aft)):
        sigma = f_couple / (d * embed)
        fos = allow / sigma
        verdict = "PASS" if fos >= target_fos else "MARGINAL/FAIL"
        print(f"{tag:>6s} {d:6.1f} {embed:7.1f} {f_couple:8.1f} "
              f"{sigma:10.3f} {fos:14.2f}   {verdict}  "
              f"(target FOS {target_fos:.1f})")

    print("\n  Both figures use the projected-bearing convention sigma = F / (D . L),")
    print("  the repo's own CARGO-03c method, against the cited 5 MPa bond-limited")
    print("  CF-PETG/epoxy allowable (structural_analysis.md SS7.3) -- the socket")
    print("  wall is CF-PETG hull skin, so this is the correct allowable to cite,")
    print("  not a plain-PETG datasheet figure.")

    f_single = m_ult_mm / (x_spar - x_fwd)
    print("\n  Sanity check vs. the superseded single-rod method (rod alone reacting")
    print("  the full moment against the spar, F = M / (spar - rod station)): that")
    print(f"  gives F = {f_single:.1f} N at the forward station alone -- the two-rod")
    print(f"  couple's shared {f_couple:.1f} N is lower, as expected once a second")
    print("  rod actually shares the load instead of being checked in isolation.")


def report_enlarged_tenon(src, scad, m_ult):
    """Superseded path: TENON_LOAD_PATH = "enlarged_tenon".

    Preserves the original CARGO-03c single-tenon sizing sweep (couple
    reacted internally on the tenon's own top/bottom faces over its
    insertion depth) so the alternate, coupon-gated path stays reportable,
    per KTD1 ("keep the enlarged-tenon sizing documented/available, not
    deleted").
    """
    # WING_ROOT_TAB_W/H/L are now a TENON_LOAD_PATH-conditional expression in
    # the SCAD, not a plain literal -- read the underlying "_ENLARGED" values
    # this path actually resolves to instead.
    tab_w, tab_h, tab_l = (scad("WING_ROOT_TAB_W_ENLARGED"),
                           scad("WING_ROOT_TAB_H_ENLARGED"),
                           scad("WING_ROOT_TAB_L_ENLARGED"))

    print("\nEnlarged-tenon path (superseded default; coupon-gated, >= 15 MPa)")
    print(f"  tenon {tab_w:.0f} (Y) x {tab_h:.0f} (Z) x {tab_l:.0f} (insertion) mm")

    m_tenon = m_ult
    couple_arm = (2.0 / 3.0) * tab_l / 1000.0
    f_bear = m_tenon / couple_arm
    area = tab_w * (tab_l / 2.0)
    sigma = f_bear / area
    print(f"  ultimate: M {m_tenon:.2f} N.m  bearing {sigma:.2f} MPa  "
          f"FOS vs 5 MPa {5.0 / sigma:.2f}")

    need = 4.0 * sigma
    print(f"\n  For the SS3 FOS 4.0 target at the present {tab_l:.0f} mm insertion the")
    print(f"  bearing allowable would have to be >= {need:.1f} MPa.")

    sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
    import wing_root_deconflict as wrd
    max_w, max_l, notes = wrd.max_tenon_envelope()
    k = need * tab_w * tab_l ** 2

    print("\n  Airframe limits on the tenon (measured, port side):")
    print(f"    max width  {max_w:5.1f} mm  (forward face is capped by the spar bore --")
    print(f"                      only {notes['fwd_room']:.2f} mm of room forward, so all")
    print("                      growth is aft, to the aft landing-gear bay)")
    print(f"    max depth  {max_l:5.1f} mm  (inboard face reaches the CARGO-01 payload")
    print(f"                      envelope at X {notes['pay_edge']:.1f}; staying buried in")
    print(f"                      the wall instead caps it at "
          f"{notes['wall_only_depth']:.0f} mm)")

    print("\n  Insertion depth needed for FOS 4.0, at the present width and at the")
    print("  maximum the airframe allows:")
    print(f"\n  {'allowable MPa':>13s} {'depth @ W=' + format(tab_w, '.0f'):>16s} "
          f"{'depth @ W=' + format(max_w, '.1f'):>18s}   verdict")
    for allow in (5.0, 10.0, 15.0, 20.0, 30.0, 40.6, 60.0):
        d_now = math.sqrt(k / (allow * tab_w))
        d_max = math.sqrt(k / (allow * max_w))
        if d_max > max_l:
            verdict = "IMPOSSIBLE -- exceeds max depth even at max width"
        elif d_now > max_l:
            verdict = f"needs the wider tenon (>{max_l:.1f} mm at W={tab_w:.0f})"
        elif d_now <= tab_l:
            verdict = "fits as-built"
        else:
            verdict = "fits, deeper tenon"
        print(f"  {allow:13.1f} {d_now:13.1f} mm {d_max:15.1f} mm   {verdict}")

    floor = k / (max_w * max_l ** 2)
    print(f"\n  MAXIMUM TENON the airframe accepts: {max_w:.1f} x {max_l:.1f} mm"
          f" (W x insertion).")
    print("  At that size the joint reaches FOS 4.0 only if the coupon allowable is")
    print(f"  >= {floor:.1f} MPa.  Below that the tenon cannot be grown into")
    print("  compliance and the joint needs a different answer -- a bonded doubler,")
    print("  a second tenon, or a metal insert.")
    print(f"  Widening 30 -> {max_w:.1f} mm alone buys only "
          f"{(1 - math.sqrt(tab_w / max_w)) * 100:.0f} % off the required depth:")
    print("  width is linear in the sizing, depth is quadratic.")


def report_thwart(m_ultimate):
    """Size the transverse member that replaces the carry-through."""
    z_thwart = THWART_T * THWART_H ** 2 / 6.0
    print(f"\nReplacement member -- CF thwart {THWART_T:.0f} x {THWART_H:.0f} mm "
          f"(CF-PLATE-2MM stock)")
    print(f"  section modulus Z = {z_thwart:.0f} mm^3")
    print(f"\n  {'station pair':>26s} {'share':>7s} {'M N.m':>7s} "
          f"{'sigma MPa':>10s} {'FOS':>6s} {'FOS uni':>8s}")
    # Two frames straddling the spar station carry the couple in inverse
    # proportion to their distance from it.  Both stations below are measured
    # clear of every opening -- see clear_stations().
    y_spar = mci.WING_SPAR_Y
    for y_fore, y_aft in ((-40.0, 118.0), (-36.0, 114.0)):
        base = y_aft - y_fore
        for tag, y_f, share in (("fore", y_fore, (y_aft - y_spar) / base),
                                ("aft", y_aft, (y_spar - y_fore) / base)):
            m = m_ultimate * share
            sigma = m * 1000.0 / z_thwart
            print(f"  Y {y_fore:+6.1f} / {y_aft:+6.1f}  {tag:>4s} {share:7.2f} "
                  f"{m:7.2f} {sigma:10.1f} {CF_ALLOW / sigma:6.1f} "
                  f"{CF_ALLOW_UNI / sigma:8.1f}")
    print("\n  FOS column uses the conservative 300 MPa cross-ply stand-in;")
    print("  FOS uni uses structural_analysis.md SS1's 1500 MPa unidirectional")
    print("  figure.  NEITHER is a verified allowable -- obtain ASTM D3039/D695")
    print("  certificates for the actual plate before fabrication"
          " -- root work-tracking file SS0.8).")
    return z_thwart


def clear_stations():
    """Y stations where a full-width thwart would meet intact structure.

    A thwart has to land on skin that exists.  Measured, not assumed: the
    section is sectioned at 3 mm intervals and the belly and both flanks are
    tested for material independently, because the clamshell aperture opens the
    belly and the four landing-gear bays open the flanks at different stations.
    """
    mesh = load("shell")
    mesh.merge_vertices()
    v = mesh.vertices

    def count(y, xlo, xhi, zlo, zhi, tol=1.5):
        s = ((np.abs(v[:, 1] - y) < tol) & (v[:, 0] > xlo) & (v[:, 0] < xhi)
             & (v[:, 2] > zlo) & (v[:, 2] < zhi))
        return int(s.sum())

    def ring_closed(y):
        """A section that is one piece with at least one hole is a closed annulus."""
        sec = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
        if sec is None:
            return False
        p2, _ = sec.to_2D()
        polys = p2.polygons_full
        return len(polys) == 1 and sum(len(p.interiors) for p in polys) >= 1

    ap = mci.APERTURE
    print("\nObstructions a thwart must clear (hull Y)")
    print(f"  clamshell aperture (belly open) Y {ap[2]:+7.1f} .. {ap[3]:+7.1f}")
    for label, _hx, hy, _hz, _az, _st in mci.LG_CORNERS:
        print(f"  {label:10s} gear bay hip      Y {hy:+7.1f}")
    print(f"  wing spar station               Y {mci.WING_SPAR_Y:+7.1f}")
    print(f"  wing mortise station            Y {mci.WING_MORT_Y:+7.1f}")

    print("\n  measured clear bands (belly + both flanks intact):")
    bands, run = [], None
    for y in np.arange(-66.0, 127.0, 2.0):
        y = float(y)
        belly = count(y, ap[0], ap[1], -2.0, 12.0) > 30
        flanks = (count(y, -110.0, -78.0, 30.0, 60.0) > 20
                  and count(y, -262.0, -230.0, 30.0, 60.0) > 20)
        good = ring_closed(y) or (belly and flanks)
        if good and run is None:
            run = y
        elif not good and run is not None:
            bands.append((run, y - 2.0))
            run = None
    if run is not None:
        bands.append((run, 125.0))
    for lo, hi in bands:
        if hi - lo >= 4.0:
            print(f"    Y {lo:+7.1f} .. {hi:+7.1f}   ({hi - lo:5.1f} mm of station)")


def ring_bottom_chord_check():
    """Is the Y+30 CF ring actually a closed ring, or does the door aperture cut it?"""
    import add_structural_features as asf
    ap = mci.APERTURE
    print("\nCF ring frame at cargo Y +30 -- is it closed?")
    for xm, xx, zm, zx, ym, yx in asf.RING_POCKETS["cargo_Y30"]:
        overlaps = (xx > ap[0] and xm < ap[1] and yx > ap[2] and ym < ap[3]
                    and zx > ap[4] and zm < ap[5])
        kind = "bottom chord" if zx < 10 else (
            "top chord" if zm > 100 else "side chord")
        print(f"  {kind:13s} X {xm:8.1f}..{xx:8.1f}  Z {zm:6.1f}..{zx:6.1f}"
              f"   {'CUT AWAY by the clamshell aperture' if overlaps else 'intact'}")


def main():
    geom = measure_geometry()
    print("=== wing_spar_carrythrough.py ===")
    print("\nMeasured geometry (hull frame, port side; X positive = port)")
    print(f"  fuselage wall skin at spar station   X {geom['wall_x']:8.2f}")
    print(f"  spar bearing seat (boss mid-span)    X {geom['bearing_x']:8.2f}")
    print(f"  spar inboard end if it stops there   X {geom['spar_inboard_end']:8.2f}")
    print(f"  wing tip face (wingtip bearing)      X {geom['wing_tip_x']:8.2f}")
    print(f"  nacelle duct axis (load line)        X {geom['nac_axis_x']:8.2f}")

    limit, ultimate = report_loads(geom)
    report_root_joint(geom, limit, ultimate)
    m_ult = report_couple(geom, limit, ultimate)
    report_thwart(m_ult)
    if "--stations" in sys.argv:
        clear_stations()
        ring_bottom_chord_check()

    print("\nBay impact if the spar stops at the wall")
    bay_lo, bay_hi = -240.0, mci.PORT_INB
    print(f"  spar inboard end X {mci.PORT_INB:.1f}; bay clear span "
          f"X {bay_lo:.1f}..{bay_hi:.1f} = {bay_hi - bay_lo:.0f} mm")
    print("  the spar no longer crosses the bay -> CARGO-01's obstruction is removed")


if __name__ == "__main__":
    main()
