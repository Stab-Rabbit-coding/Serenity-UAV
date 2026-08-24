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

# --- spar section, 8 mm OD x 1.5 mm wall (5 mm ID) AISI 4130 ---------------
SPAR_OD, SPAR_ID = 8.0, 5.0
SPAR_I = math.pi * (SPAR_OD ** 4 - SPAR_ID ** 4) / 64.0    # mm^4
SPAR_Z = SPAR_I / (SPAR_OD / 2.0)                          # mm^3
# MPa, 4130 normalized (typical -- MMPDS; tracked in the root work-tracking
# file SS0.8).
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
    print(f"\n  section 8 x 1.5 4130:  I {SPAR_I:.0f} mm^4   Z {SPAR_Z:.1f} mm^3")
    print(f"\n{'case':>10s} {'R_tip N':>9s} {'R_fus N':>9s} "
          f"{'M_spar N.m':>11s} {'sigma MPa':>10s} {'FOS':>6s}")
    for tag, f in (("1 g", per_side_1g), ("limit", limit), ("ultimate", ultimate)):
        r_tip, r_fus, m_spar, sigma = spar_case(f, geom)
        print(f"{tag:>10s} {r_tip:9.1f} {r_fus:9.1f} {m_spar:11.2f} "
              f"{sigma:10.1f} {STEEL_YIELD / sigma:6.1f}")
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
    """Split the wing-root reaction between the tenon and the spar bearing.

    Owner, 2026-08-23: "that mortise/tenon joint provides part of the structural
    joint at the wing root, since the wings don't rotate with the nacelles."  That
    is a load-path statement, and it contradicts `fuselage_root_tab()`'s own
    comment ("The tab provides radial restraint; the CF spar carries spanwise
    load") -- with SPAR-01 the spar no longer carries through, so spanwise load
    terminates at the wall and the tenon is part of how it gets there.

    The wing is supported at two points: the root tenon and the wingtip bearing on
    the spar.  Whatever the spar hands the wing at the tip, the tenon reacts at the
    root, and the spar's own fuselage-side bearing pushes back the other way.  The
    two are a couple, not a shared load.
    """
    import re
    wing_scad = os.path.join(REPO_ROOT, "airframe", "openscad", "wings",
                             "wings_s1223_revo.scad")
    with open(wing_scad, encoding="utf-8") as fh:
        src = fh.read()

    def scad(name):
        m = re.search(rf"^{name}\s*=\s*(-?[\d.]+)\s*;", src, re.M)
        return float(m.group(1))

    tab_w, tab_h, tab_l = (scad("WING_ROOT_TAB_W"), scad("WING_ROOT_TAB_H"),
                           scad("WING_ROOT_TAB_L"))
    arm = geom["wing_tip_x"] - geom["wall_x"]        # tip bearing -> root face

    print("\nWing root joint -- how the reaction splits (per side)")
    print(f"  tenon {tab_w:.0f} (Y) x {tab_h:.0f} (Z) x {tab_l:.0f} (insertion) mm"
          f"   [all three still marked VERIFY in the wing SCAD]")
    print(f"  tip bearing to root face  {arm:6.1f} mm")
    print(f"\n{'case':>10s} {'R_tip N':>9s} {'tenon V N':>10s} "
          f"{'tenon M N.m':>12s} {'bearing MPa':>12s} {'FOS vs 5':>9s}")
    for tag, f in (("limit", limit), ("ultimate", ultimate)):
        r_tip, r_fus, _m, _s = spar_case(f, geom)
        m_tenon = r_tip * arm / 1000.0
        # Moment reacted as a couple on the tenon's top/bottom faces over the
        # insertion depth; effective arm taken as 2/3 of the depth (triangular
        # bearing distribution), bearing area = width x half the depth.
        couple_arm = (2.0 / 3.0) * tab_l / 1000.0
        f_bear = m_tenon / couple_arm
        area = tab_w * (tab_l / 2.0)                 # mm^2
        sigma = f_bear / area
        print(f"{tag:>10s} {r_tip:9.1f} {r_tip:10.1f} {m_tenon:12.2f} "
              f"{sigma:12.2f} {5.0 / sigma:9.2f}")

    print("\n  The 5 MPa column is the repository's own BOND-limited CF-PETG/epoxy")
    print("  allowable (structural_analysis.md SS7.3).  A CF-PETG **bearing**")
    print("  allowable is NOT established anywhere in this repository, and bearing")
    print("  is the mode that governs a tenon in a slot -- so treat the FOS column")
    print("  as an order-of-magnitude screen, not a margin.  structural_analysis.md")
    print("  SS3 sets the joint FOS target at 4.0 (design-team judgment; no published")
    print("  FDM knockdown standard exists for CF-PETG).")

    # Invert the sizing so the answer does not depend on inventing an allowable:
    # bearing stress falls as 1/depth^2 (the couple arm and the bearing area both
    # grow with depth), so the depth needed for FOS 4.0 follows from whatever
    # allowable the coupon test eventually returns.
    r_tip, _rf, _m, _s = spar_case(ultimate, geom)
    sigma_ult = (r_tip * arm / 1000.0) / ((2.0 / 3.0) * tab_l / 1000.0) \
        / (tab_w * tab_l / 2.0)
    need = 4.0 * sigma_ult
    print(f"\n  For the SS3 FOS 4.0 target at the present {tab_l:.0f} mm insertion the")
    print(f"  bearing allowable would have to be >= {need:.1f} MPa.")

    # Bearing stress goes as 1/(W . L^2): depth is a QUADRATIC lever, width only a
    # linear one.  Both are capped by what the airframe will physically accept --
    # measured, not assumed, by wing_root_deconflict.max_tenon_envelope().
    sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
    import wing_root_deconflict as wrd
    max_w, max_l, notes = wrd.max_tenon_envelope()
    k = need * tab_w * tab_l ** 2            # = 4 * 3000 * M, the sizing constant

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
