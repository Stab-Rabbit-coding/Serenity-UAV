#!/usr/bin/env python3
"""Deconflict everything crowded into the wing-root zone of the cargo bulkhead.

Owner direction, 2026-08-23
---------------------------
The nacelle drive servos are **25 kgf.cm+ units inside the fuselage, mounted
against the port and starboard bulkheads**, each rotating one wing spar and the
nacelle keyed to it (`airframe/wings-nacelles/WBS.md` SS1.1.2 SPAR-01).  Their
mounts must clear the landing-gear bays, the port/starboard avionics bays, the
wing root mortise and the spar bearing seat -- **and the nacelle ESC and
nav-light cableways must not be blocked**.

The nav light is the easy one: it routes through the hollow spar's ~5 mm ID and
tilts with it (95 deg twist, `docs/TILT_SPAR_ANALYSIS.md` SS5).  The 40 A EDF ESC
feeds are far too big for that bore and run in their own double-D conduit in the
fixed wing, so they need an independent path through the bulkhead.

Everything below is one congested volume, which is why it is one tool: the same
obstruction set is reused for the servo body, the servo horn and all three
routes.  Duplicating that set across separate scripts is how the shell and the
wing drifted apart in the first place (Rev S1b reconciled the spar station
across them but not its diameter -- CARGO-02).

Two sides of the check
----------------------
OBSTRUCTIONS  -- solid things: servo body, servo horn swing, spar bearing seat,
                 wing root mortise, the WING ROOT TENON that enters it,
                 landing-gear bay seats, avionics bays.
ROUTES        -- volumes that must stay open: the EDF ESC double-D conduit, the
                 Hall/encoder conduit, and the spar bore that carries the
                 nav-light 3-core.

The tenon is modelled with its own "tenon pass-through" bores subtracted, not as
a plain block: `wing_one_side()` drills the EDF conduits axially through it.  A
plain-block tenon reports the cableway as blocked by its own wing.

The tenon also gets a FIT check against the mortise, which is a separate question
from interference -- the two are sized to match (30.0 x 20.0 in 30.8 x 20.8) but
are placed off different datums, so they can be individually correct and still not
assemble.

Every pairing is tested by boolean intersection.  A route that a solid eats into
is reported as blocked; two solids that merely share a face plane are reported
as flush, because features placed off a common datum are *expected* to meet
there and that is not a defect.

Geometry sources -- nothing is restated here that the design already owns:
    airframe/blender-scripts/merge_cargo_interior.py   shell features, stations
    airframe/openscad/wings/wings_s1223_revo.scad      conduit chord fractions,
                                                       S1223 camber midline
    tools/wing_spar_station_fit.py                     SCAD parsing + surf_y()
    REFERENCES.md REF-SENSOR-013                       servo body envelope

Run:
    /usr/bin/python3 tools/wing_root_deconflict.py

Use `/usr/bin/python3`: the repo `.venv` hides `trimesh` and `manifold3d`.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5, Anthropic) under the author's
         direction, per `AGENTS.md` SS3 "Attribution and Licensing".
License: CC BY-SA 4.0 - creativecommons.org/licenses/by-sa/4.0
"""

import os
import re
import sys

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "airframe", "blender-scripts"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import merge_cargo_interior as mci          # noqa: E402
import wing_spar_station_fit as wsf         # noqa: E402

# --- servo envelope, DS3225 datasheet (authoritative, owner 2026-08-23) ------
# avionics/datasheets/DS3225 datasheet.pdf, Dongguan City Dsservo Technology.
# DS3225 supersedes DS3218 for torque; both datasheets carry the same drawing
# and the same SS2-1 size, so this envelope is common to the body family.
# The four screws run parallel to the output shaft, so with the shaft along hull
# X the FLANGE lies in the Y-Z plane on the bulkhead and the 40.5 mm height is
# the INBOARD DEPTH.  Footprint on the wall is the flange: 54.5 (Y) x 20 (Z).
SERVO_L = mci.NSVMT_BODY_L          # 40.0  body length   -> hull Y
SERVO_W = mci.NSVMT_BODY_W          # 20.0  body width    -> hull Z
SERVO_DEPTH = mci.NSVMT_BODY_H      # 40.5  body height   -> hull X, inboard
SERVO_EAR_SPAN = mci.NSVMT_EAR_SPAN  # 54.5 flange overall, hull Y
SERVO_MASS_G = 60.0                 # datasheet SS2-2
HORN_SWING_R = 22.0

WING_CHORD_LINE_Z = 58.01       # hull Z of the wing chord line at the root
GAP_BUDGET = 3.0                # mm, minimum acceptable edge-to-edge clearance

# U6 (2026-08-25): boolean/mesh noise tolerance for intersection-volume tests.
# The published shell round-trips through a float32 binary STL (repair_exported
# in merge_cargo_interior.py), so a coincident boolean seam that is genuinely
# open can still report a sub-1e-5 mm^3 sliver on reload -- observed directly
# on the spar-bore route check post-U6-rebake (port 1.4e-06, stbd 1.0e-05
# mm^3).  `check_bulkhead_penetration()` already carries this exact tolerance
# (1.0 mm^3, "far below the ~1700 mm^3 an uncut wall leaves, and far above the
# noise"); `check_routes()`'s old bare `> 1e-6` had no such margin and flagged
# those slivers as BLOCKED.  One constant for both keeps them from disagreeing
# on what counts as noise.
BOOL_NOISE_TOL = 1.0            # mm^3, see note above
X_CL = -169.9                   # cargo centreline
PAYLOAD_W = 101.6               # mission payload width, CARGO-01


def to_man(tm):
    return Manifold(Mesh(tm.vertices.astype(np.float32), tm.faces.astype(np.uint32)))


def volume_of(man):
    g = man.to_mesh()
    if len(g.tri_verts) == 0:
        return 0.0
    return float(trimesh.Trimesh(
        vertices=np.asarray(g.vert_properties)[:, :3].astype(np.float64),
        faces=np.asarray(g.tri_verts).astype(np.int64), process=False).volume)


def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    b.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return b


def xcyl(y, z, x0, x1, r, sections=48):
    c = trimesh.creation.cylinder(radius=r, height=abs(x1 - x0), sections=sections)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    c.apply_translation(((x0 + x1) / 2.0, y, z))
    return c


def midline_mm():
    """S1223 camber midline in mm at a chord fraction, at the ROOT chord.

    Parsed from the wing SCAD through `wing_spar_station_fit`, so the airfoil
    table has exactly one definition in the repository.
    """
    with open(wsf.WING_SCAD, encoding="utf-8") as fh:
        src = fh.read()
    upper = wsf.scad_points(src, "S1223_UPPER")
    lower = wsf.scad_points(src, "S1223_LOWER")

    def at(xfr):
        mid = (wsf.surf_y(upper, xfr) + wsf.surf_y(lower, xfr)) / 2.0
        return mid * mci.WING_ROOT_CHORD
    return at


def route_stations():
    """(label, chord_fraction, [(y_offset, diameter), ...]) for each protected route.

    Rev S1c (feat/wing-spar-s1c-cableway-reroute) converted BOTH conduits from
    constant chord FRACTIONS to constant-mm STATIONS, matching the spar's own law:
    with a straight LE, two constant-mm bores hold the same separation at every
    span station, so taper cannot erode the web between them.  That is why the
    old `*_XFR` names are gone.  This reader takes the station constants and
    divides by the ROOT chord only to keep the rest of this tool -- which works at
    the root -- on one representation.
    """
    with open(wsf.WING_SCAD, encoding="utf-8") as fh:
        src = fh.read()
    chord = mci.WING_ROOT_CHORD
    cable_d = wsf.scad_scalar(src, "CABLE_BORE_D")
    cable_sep = wsf.scad_scalar(src, "CABLE_BORE_SEP")
    cable_stn = wsf.scad_scalar(src, "CABLE_BORE_STATION")
    hall_d = wsf.scad_scalar(src, "HALL_CABLE_D")
    hall_stn = wsf.scad_scalar(src, "HALL_CABLE_STATION")
    spar_bore = wsf.scad_scalar(src, "SPAR_BORE_OD")
    spar_stn = wsf.scad_scalar(src, "SPAR_BORE_STATION")
    # Each bore is camber-centred at ITS OWN chordwise station, so the two EDF
    # bores do not share a midline: at 22.75 and 32.25 mm the S1223 camber line
    # differs by ~0.8 mm.  Evaluating one midline for the pair puts both bores
    # off the shell's matching harness ports and reports phantom blockage.
    out = [
        ("EDF ESC conduit (40 A feeds)",
         [((cable_stn - cable_sep / 2) / chord, cable_d),
          ((cable_stn + cable_sep / 2) / chord, cable_d)]),
        ("Hall/encoder conduit", [(hall_stn / chord, hall_d)]),
        ("spar bore / nav-light 3-core", [(spar_stn / chord, spar_bore)]),
    ]
    # U5/KTD1 two-rod couple: both rod clearance bores are camber-centred at
    # their own station exactly like the bores above (see
    # wing_root_tie_rod_fwd_bore()/_aft_bore() in the wing SCAD). Root-only
    # embeds (40/42 mm), shorter than the PORT_INB..PORT_OUTB span this
    # reuses for the probe cylinder -- checking the wider span is the
    # conservative direction (more territory probed, never less).
    m = re.search(r'^TENON_LOAD_PATH\s*=\s*"([^"]+)"\s*;', src, re.M)
    if m and m.group(1) == "two_rod":
        rod_fwd_d = wsf.scad_scalar(src, "ROD_FWD_D")
        rod_fwd_stn = wsf.scad_scalar(src, "ROD_FWD_STATION")
        rod_aft_d = wsf.scad_scalar(src, "ROD_AFT_D")
        rod_aft_stn = wsf.scad_scalar(src, "ROD_AFT_STATION")
        out.append(("fwd tie-rod bore", [(rod_fwd_stn / chord, rod_fwd_d)]))
        out.append(("aft tie-rod bore", [(rod_aft_stn / chord, rod_aft_d)]))
    return out


def routes(side):
    """Protected-open volumes at the wing root, hull frame."""
    mid = midline_mm()
    inb = mci.PORT_INB if side == "port" else mci.STBD_INB
    outb = mci.PORT_OUTB if side == "port" else mci.STBD_OUTB
    lo, hi = min(inb, outb), max(inb, outb)
    # U5/KTD1: the tie-rods are ROOT-ONLY embeds, shorter than the main
    # spar's PORT_INB..PORT_OUTB span -- probing the wider span reads solid
    # wall beyond each rod's own embed as a false BLOCKED. Use each rod's
    # actual fuselage-side embed span instead (mci.ROD_*_*_INB/OUTB).
    rod_span = {
        "fwd tie-rod bore": (mci.ROD_FWD_PORT_INB, mci.ROD_FWD_PORT_OUTB) if side == "port"
        else (mci.ROD_FWD_STBD_INB, mci.ROD_FWD_STBD_OUTB),
        "aft tie-rod bore": (mci.ROD_AFT_PORT_INB, mci.ROD_AFT_PORT_OUTB) if side == "port"
        else (mci.ROD_AFT_STBD_INB, mci.ROD_AFT_STBD_OUTB),
    }
    out = []
    for label, bores in route_stations():
        for i, (xfr, d) in enumerate(bores):
            z = WING_CHORD_LINE_Z + mid(xfr)
            y = mci.WING_LE_ROOT_Y + xfr * mci.WING_ROOT_CHORD
            tag = label if len(bores) == 1 else f"{label} #{i + 1}"
            if label in rod_span:
                x0, x1 = rod_span[label]
                span_lo, span_hi = min(x0, x1), max(x0, x1)
            else:
                span_lo, span_hi = lo - 12.0, hi + 12.0
            out.append((tag, xcyl(y, z, span_lo, span_hi, d / 2.0)))
    return out


def tenon_params():
    """Wing root tenon, read from the wing SCAD.

    SCAD local frame at the root: X = chordwise, Y = thickness (about the CHORD
    LINE), Z = spanwise.  `fuselage_root_tab()` centres the tenon at 50 % root
    chord and at local Y = 0 -- i.e. on the chord line, NOT on `WING_ROOT_Z`.
    That distinction is the whole point of the fit check below.

    U5/KTD1 (2026-08-24): `WING_ROOT_TAB_W/H/L` are now a
    `TENON_LOAD_PATH`-conditional expression in the SCAD (locating-only under
    the default "two_rod" path, the original structural size under
    "enlarged_tenon"), not a plain literal `wsf.scad_scalar()` can parse.
    Read whichever branch's `_LOCATING`/`_ENLARGED` constants are actually
    active instead.
    """
    with open(wsf.WING_SCAD, encoding="utf-8") as fh:
        src = fh.read()
    m = re.search(r'^TENON_LOAD_PATH\s*=\s*"([^"]+)"\s*;', src, re.M)
    suffix = "_LOCATING" if (m and m.group(1) == "two_rod") else "_ENLARGED"
    return (wsf.scad_scalar(src, "WING_ROOT_TAB_W" + suffix),  # chordwise -> hull Y
            wsf.scad_scalar(src, "WING_ROOT_TAB_H" + suffix),  # thickness -> hull Z
            wsf.scad_scalar(src, "WING_ROOT_TAB_L" + suffix))  # insertion -> hull X


def tenon(side):
    """The wing root tenon as a solid, in hull coordinates.

    It is centred chordwise at 50 % root chord (hull Y) and on the wing CHORD
    LINE (hull Z = WING_CHORD_LINE_Z), and inserts `L` inboard from the root
    face.  The root face is taken at the measured skin, so the tenon occupies the
    wall and reaches `L` beyond it.
    """
    w, h, ln = tenon_params()
    y_c = mci.WING_LE_ROOT_Y + 0.50 * mci.WING_ROOT_CHORD
    z_c = WING_CHORD_LINE_Z
    face = wall_face_x(side)
    sign = -1.0 if side == "port" else +1.0        # inboard direction
    x0, x1 = sorted((face, face + sign * ln))
    solid = box(x0, x1, y_c - w / 2, y_c + w / 2, z_c - h / 2, z_c + h / 2)

    # The tenon is NOT a plain block: `wing_one_side()` drills a "tenon
    # pass-through" for any conduit whose chordwise station falls inside the
    # tenon, so the wire exits the inboard face instead of dead-ending in solid
    # material.  Modelling the tenon without those bores reports a cableway as
    # blocked by its own wing, which is wrong.
    #
    # Which conduit needs one is NOT fixed, so it must not be hardcoded.  Before
    # Rev S1c the EDF double-D sat at 0.48c, inside the tenon, and got the
    # pass-through; the reroute moved it forward to 22.75/32.25 mm -- clear of
    # the tenon -- and moved the sensor conduit to 54.0 mm, which is inside it.
    # The bore now follows the station, so a later reroute cannot silently
    # invert this again.
    man = to_man(solid)
    mid = midline_mm()
    y_lo, y_hi = y_c - w / 2.0, y_c + w / 2.0
    for _label, bores in route_stations():
        for xfr, d in bores:
            y = mci.WING_LE_ROOT_Y + xfr * mci.WING_ROOT_CHORD
            if not (y_lo - d / 2.0 < y < y_hi + d / 2.0):
                continue        # clear of the tenon; no pass-through cut
            z = WING_CHORD_LINE_Z + mid(xfr)
            man = man - to_man(xcyl(y, z, x0 - 2.0, x1 + 2.0, d / 2.0))
    g = man.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(g.vert_properties)[:, :3].astype(np.float64),
        faces=np.asarray(g.tri_verts).astype(np.int64), process=False)


def wall_face_x(side):
    """Measured hull X of the bulkhead's outer skin at the mortise station.

    Taken from the published shell rather than from `PORT_INB`/`PORT_OUTB`, which
    are deep-embed spans for bosses and are NOT the wall -- assuming they were is
    what produced CARGO-03.
    """
    shell = load_shell()
    v = shell.vertices
    band = ((np.abs(v[:, 1] - mci.WING_MORT_Y) < 3.0)
            & (np.abs(v[:, 2] - mci.WING_ROOT_Z) < 6.0))
    if side == "port":
        sel = band & (v[:, 0] > X_CL)
        return float(v[sel, 0].max()) if sel.any() else mci.PORT_INB
    sel = band & (v[:, 0] < X_CL)
    return float(v[sel, 0].min()) if sel.any() else mci.STBD_INB


def max_tenon_envelope(side="port"):
    """Largest tenon the airframe will actually accept, measured by bisection.

    Returns (max_width_mm, max_depth_mm, notes).  Growth is bounded by real
    parts, not by the mortise: the tenon LIVES in the mortise, and the D22 spar
    bearing boss shares a region the mortise already cuts, so neither counts as a
    collision.  What does count is the spar tube, the landing-gear bays, the
    servo, the avionics bay, and -- for depth -- the CARGO-01 payload envelope,
    because a tenon that protrudes past the wall is inside the cargo bay.
    """
    w0, h0, l0 = tenon_params()
    y_c = mci.WING_LE_ROOT_Y + 0.50 * mci.WING_ROOT_CHORD
    z_c = WING_CHORD_LINE_Z
    face = wall_face_x(side)
    y_fwd = y_c - w0 / 2.0
    spar_aft = mci.WING_SPAR_Y + 8.3 / 2.0
    pay_edge = X_CL + PAYLOAD_W / 2.0            # payload port face, centred

    real = [(lbl, sol) for lbl, sol in obstructions(side)
            if lbl not in ("wing root tenon", "wing root mortise",
                           "spar bearing seat")]
    real.append(("rotating spar tube", spar_tube(side)))

    def clashes(y0, y1, depth):
        t = box(face - depth, face, y0, y1, z_c - h0 / 2, z_c + h0 / 2)
        tm = to_man(t)
        return any(volume_of(tm ^ to_man(sol)) > 1.0 for _l, sol in real)

    lo, hi = y_c + w0 / 2.0, 120.0               # aft face sweep
    while hi - lo > 0.05:
        mid = (lo + hi) / 2.0
        lo, hi = (mid, hi) if not clashes(y_fwd, mid, l0) else (lo, mid)
    max_w = lo - y_fwd

    lo2, hi2 = l0, 40.0                          # depth sweep
    while hi2 - lo2 > 0.05:
        mid = (lo2 + hi2) / 2.0
        bad = clashes(y_fwd, y_c + w0 / 2.0, mid) or (face - mid) < pay_edge
        lo2, hi2 = (lo2, mid) if bad else (mid, hi2)
    max_l = lo2

    notes = {
        "fwd_room": y_fwd - spar_aft,   # forward growth available (spar bore)
        "wall_only_depth": 16.0,        # stay buried in the measured wall band
        "pay_edge": pay_edge,
        "face": face,
    }
    return max_w, max_l, notes


def tenon_fit_check(findings):
    """Does the tenon actually match the mortise it is cut to enter?"""
    w, h, ln = tenon_params()
    y_c = mci.WING_LE_ROOT_Y + 0.50 * mci.WING_ROOT_CHORD
    z_c = WING_CHORD_LINE_Z
    print("\nWing root tenon vs the mortise it enters")
    print(f"  tenon  {w:.1f} (Y) x {h:.1f} (Z) x {ln:.1f} (insertion), "
          f"centred Y {y_c:+.2f}  Z {z_c:+.2f}  [on the CHORD LINE]")
    print(f"  mortise {mci.MORT_W:.1f} (Y) x {mci.MORT_H:.1f} (Z), "
          f"centred Y {mci.WING_MORT_Y:+.2f}  Z {mci.WING_ROOT_Z:+.2f}"
          f"  [on WING_ROOT_Z]")
    print(f"\n  {'axis':>6s} {'tenon span':>18s} {'mortise span':>18s} "
          f"{'clearance each side':>20s}")
    ok = True
    for axis, t_c, t_s, m_c, m_s in (("Y", y_c, w, mci.WING_MORT_Y, mci.MORT_W),
                                     ("Z", z_c, h, mci.WING_ROOT_Z, mci.MORT_H)):
        t0, t1 = t_c - t_s / 2, t_c + t_s / 2
        m0, m1 = m_c - m_s / 2, m_c + m_s / 2
        lo, hi = t0 - m0, m1 - t1
        flag = "" if min(lo, hi) >= 0 else "   TENON FOULS THE MORTISE"
        if min(lo, hi) < 0:
            ok = False
        print(f"  {axis:>6s} {t0:+8.2f}..{t1:+8.2f} {m0:+8.2f}..{m1:+8.2f} "
              f"{lo:+9.2f} /{hi:+9.2f}{flag}")
    offset = mci.WING_ROOT_Z - z_c
    print(f"\n  tenon centre is {abs(offset):.2f} mm "
          f"{'below' if offset > 0 else 'above'} the mortise centre "
          f"(chord line {z_c:+.2f} vs WING_ROOT_Z {mci.WING_ROOT_Z:+.2f})")
    if not ok:
        findings.append(("both", "wing root tenon does not fit its mortise "
                                 f"(Z offset {abs(offset):.2f} mm)", 0.0))
    return ok


def servo_body(side):
    """Servo envelope on the bulkhead: flange footprint, body depth inboard.

    Uses the flange span in Y (54.5) rather than the bare body (40.0), because the
    ears are what the pad has to carry.  Depth is the 40.5 mm HEIGHT -- the axis
    the output shaft runs along -- not the 20 mm width.
    """
    inboard = mci.PORT_INB if side == "port" else mci.STBD_INB
    sign = -1.0 if side == "port" else +1.0
    x0, x1 = sorted((inboard, inboard + sign * SERVO_DEPTH))
    return box(x0, x1,
               mci.NSVMT_Y - SERVO_EAR_SPAN / 2.0,
               mci.NSVMT_Y + SERVO_EAR_SPAN / 2.0,
               mci.NSVMT_Z - SERVO_W / 2.0, mci.NSVMT_Z + SERVO_W / 2.0)


def servo_pad(side):
    """The PAD the shell adds, not the servo on it.

    The pad is shell material and can collide with things the servo body does
    not: it is wider than the servo in Y by design (ear reach + relief), so it
    reaches further toward the landing-gear bays.  Checking only the servo body
    would miss that.
    """
    inb = mci.PORT_INB if side == "port" else mci.STBD_INB
    outb = mci.PORT_OUTB if side == "port" else mci.STBD_OUTB
    lo, hi = min(inb, outb), max(inb, outb)
    return box(lo, hi,
               mci.NSVMT_Y - mci.NSVMT_PAD_W / 2, mci.NSVMT_Y + mci.NSVMT_PAD_W / 2,
               mci.NSVMT_Z - mci.NSVMT_PAD_H / 2, mci.NSVMT_Z + mci.NSVMT_PAD_H / 2)


def servo_horn(side):
    inboard = mci.PORT_INB if side == "port" else mci.STBD_INB
    sign = -1.0 if side == "port" else +1.0
    x = inboard + sign * (SERVO_W + 4.0)
    return xcyl(mci.NSVMT_Y, mci.NSVMT_Z, x - 4.0, x + 4.0, HORN_SWING_R, sections=64)


def obstructions(side):
    """Solid things in the wing-root zone, hull frame."""
    inb = mci.PORT_INB if side == "port" else mci.STBD_INB
    outb = mci.PORT_OUTB if side == "port" else mci.STBD_OUTB
    lo, hi = min(inb, outb), max(inb, outb)
    out = [
        ("servo body", servo_body(side)),
        ("servo horn swing", servo_horn(side)),
        ("spar bearing seat", xcyl(mci.WING_SPAR_Y, mci.WING_SPAR_Z,
                                   lo, hi, mci.WING_SPAR_BOSS_OD / 2.0)),
        ("wing root mortise", box(
            lo, hi,
            mci.WING_MORT_Y - mci.MORT_W / 2, mci.WING_MORT_Y + mci.MORT_W / 2,
            mci.WING_ROOT_Z - mci.MORT_H / 2, mci.WING_ROOT_Z + mci.MORT_H / 2)),
    ]
    out.append(("wing root tenon", tenon(side)))
    for label, hx, hy, hz, az, station in mci.LG_CORNERS:
        if (side == "port") != (hx > X_CL):
            continue
        org, ex, ey, ez = mci._plate_frame(hx, hy, hz, az, station)
        zb1 = mci.BAY_PLATE_ZB0 + mci.BAY_PLATE_L
        out.append((f"LG bay {label}", mci._plate_trap(
            org, ex, ey, ez, mci.BAY_PLATE_WB, mci.BAY_PLATE_W,
            mci.BAY_PLATE_ZB0, zb1, -mci.LG_SEAT_D - mci.COWL_H, 12.0)))
    av_x = mci.INARA_X if side == "port" else (2 * X_CL - mci.INARA_X)
    out.append((
        "avionics bay " + ("Inara" if side == "port" else "River (deferred)"),
        box(av_x - 35.0, av_x + 35.0, mci.INARA_Y - 30.0, mci.INARA_Y + 30.0,
            mci.DORSAL_Z_INB, mci.DORSAL_Z_TOP)))
    return out


def gap_between(a, b):
    """Edge-to-edge gap; 0.0 on overlap OR on a coplanar face-touch."""
    if volume_of(to_man(a) ^ to_man(b)) > 1e-6:
        return 0.0
    pa = trimesh.proximity.closest_point(a, b.vertices)[1].min()
    pb = trimesh.proximity.closest_point(b, a.vertices)[1].min()
    return float(min(pa, pb))


def penetration_check(shell_man, findings):
    """Do the wing-root penetrations actually pass THROUGH the bulkhead?

    A cut that lands outboard of the skin removes only air and leaves the wall
    intact behind it.  The cut region reads "empty" either way, so emptiness
    alone proves nothing -- the corridor must be swept from well inboard of the
    wall to well outboard of it, and THAT must be empty.
    """
    print("\nBulkhead penetration (does the cut actually go through?)")
    print(f"  {'penetration':>34s} {'cut X span':>18s} {'material in corridor':>21s}")
    y0 = mci.WING_MORT_Y - mci.MORT_W / 2
    y1 = mci.WING_MORT_Y + mci.MORT_W / 2
    z0 = mci.WING_ROOT_Z - mci.MORT_H / 2
    z1 = mci.WING_ROOT_Z + mci.MORT_H / 2
    cases = [
        ("wing root mortise, port", (mci.PORT_INB + 1.0, mci.PORT_OUTB - 10.0),
         box(-130.0, -60.0, y0, y1, z0, z1)),
        ("wing root mortise, stbd", (mci.STBD_OUTB + 8.0, mci.STBD_INB - 1.0),
         box(-280.0, -210.0, y0, y1, z0, z1)),
        # Print labels below MUST match the swept-corridor bounds actually
        # passed to xcyl() just beneath them.  They used to both read the
        # copy-pasted placeholder (-270.0, -70.0) -- identical for port AND
        # stbd, and matching neither the per-side sweep nor PORT_INB/OUTB /
        # STBD_INB/OUTB (-100/-60 and -240/-278).  That was purely a label
        # bug (the sweep itself always used the real -130..-55 / -285..-210
        # bounds below), but a stale label defeats the whole point of
        # printing the cut span for a human to sanity-check against the
        # wall brackets, so it is corrected to the real sweep bounds here.
        ("spar bore, port", (-130.0, -55.0),
         xcyl(mci.WING_SPAR_Y, mci.WING_SPAR_Z, -130.0, -55.0,
              mci.WING_SPAR_BORE_D / 2.0)),
        ("spar bore, stbd", (-285.0, -210.0),
         xcyl(mci.WING_SPAR_Y, mci.WING_SPAR_Z, -285.0, -210.0,
              mci.WING_SPAR_BORE_D / 2.0)),
    ]
    # Boolean noise on a ~900 k-face shell leaves sub-mm^3 slivers in a corridor
    # that is genuinely open, so a hard zero is the wrong test.  1 mm^3 is far
    # below the ~1700 mm^3 an uncut 2 mm wall leaves, and far above the noise.
    # Same constant check_routes() uses, so the two checks can't disagree.
    open_tol = BOOL_NOISE_TOL
    for label, (cx0, cx1), corridor in cases:
        left = volume_of(to_man(corridor) ^ shell_man)
        verdict = "THROUGH" if left <= open_tol else "BLIND -- wall not cut"
        if left > open_tol:
            findings.append((label.split(",")[1].strip(),
                             f"{label} does not penetrate the bulkhead", left))
        print(f"  {label:>34s} {cx0:8.1f}..{cx1:-7.1f} {left:16.1f} mm^3   {verdict}")


def pad_fit_check():
    """Does the servo footprint fit the pad the shell provides?"""
    print("\nPad fit (servo footprint vs the pad the shell provides)")
    print(f"  {'axis':>6s} {'servo needs':>12s} {'pad has':>9s} {'margin':>9s}")
    bad = []
    for axis, need, has in (("Y", SERVO_EAR_SPAN, mci.NSVMT_PAD_W),
                            ("Z", SERVO_W, mci.NSVMT_PAD_H)):
        margin = has - need
        if margin < 0:
            bad.append(axis)
        print(f"  {axis:>6s} {need:12.1f} {has:9.1f} {margin:+9.1f}"
              f"{'   UNDERSIZED' if margin < 0 else ''}")
    return bad


def spar_tube(side):
    """The rotating spar itself -- solid, and it occupies its bore.

    Anything else routed inside that bore collides with the spar, not with the
    shell, so the shell test alone would miss it.
    """
    with open(wsf.WING_SCAD, encoding="utf-8") as fh:
        od = wsf.scad_scalar(fh.read(), "SPAR_BORE_OD") - 0.30   # bore = OD + 0.15/side
    inb = mci.PORT_INB if side == "port" else mci.STBD_INB
    sign = 1.0 if side == "port" else -1.0
    return xcyl(mci.WING_SPAR_Y, mci.WING_SPAR_Z,
                inb, inb + sign * 200.0, od / 2.0)


def load_shell():
    p = os.path.join(REPO_ROOT, "airframe", "stls", "fuselage", "cargo",
                     "cargo_sect_shell24_2mm_repaired.stl")
    m = trimesh.load(p, force="mesh")
    m.merge_vertices()
    return m


def check_routes(side, findings, shell_man):
    """Protected routes against real material.

    Tested against the **published shell**, not against idealised primitives.
    That matters: the wing root mortise and the spar bore are VOIDS, so a route
    passing through them is using its intended path, and a primitive-based test
    reports those as blockages when they are the opposite.  The shell is ground
    truth for what material actually remains after the merge.

    The two things not in the shell are added explicitly: the servo (not shell
    geometry) and the rotating spar (occupies its own bore).
    """
    print(f"\n  ROUTES vs real material -- {side}")
    print(f"  {'route':>30s} {'obstruction':>26s} {'blocked mm^3':>13s}   verdict")
    extra = [("published cargo shell", None),
             ("servo body", servo_body(side)),
             ("servo horn swing", servo_horn(side)),
             ("rotating spar tube", spar_tube(side)),
             ("wing root tenon", tenon(side))]
    for rlabel, rsolid in routes(side):
        rman = to_man(rsolid)
        for olabel, osolid in extra:
            oman = shell_man if osolid is None else to_man(osolid)
            if olabel == "rotating spar tube" and rlabel.startswith("spar bore"):
                continue          # the spar is supposed to be in its own bore
            inter = volume_of(rman ^ oman)
            if inter > BOOL_NOISE_TOL:
                verdict = "BLOCKED"
                findings.append((side, f"{olabel} blocks {rlabel}", inter))
            else:
                verdict = "clear"
            print(f"  {rlabel:>30s} {olabel:>26s} {inter:13.1f}   {verdict}")


def check_solids(side, findings):
    """Servo body/horn against the other solids."""
    print(f"\n  SOLIDS vs solids -- {side}")
    print(f"  {'probe':>18s} {'neighbour':>26s} {'overlap mm^3':>13s} "
          f"{'gap mm':>8s}   verdict")
    probes = [("servo body", servo_body(side)), ("servo horn", servo_horn(side)),
              ("servo PAD", servo_pad(side))]
    others = [(lbl, s) for lbl, s in obstructions(side)
              if lbl not in ("servo body", "servo horn swing")]
    for plabel, psolid in probes:
        for olabel, osolid in others:
            inter = volume_of(to_man(psolid) ^ to_man(osolid))
            gap = gap_between(psolid, osolid)
            if inter > 1e-6:
                verdict = "INTERFERES"
                findings.append((side, f"{plabel} interferes with {olabel}", inter))
            elif gap <= 1e-3:
                verdict = "flush at the mounting plane (by construction)"
            elif gap < GAP_BUDGET:
                verdict = f"TIGHT (< {GAP_BUDGET:.0f} mm)"
                findings.append((side, f"{plabel} clears {olabel} by {gap:.2f} mm", 0.0))
            else:
                verdict = "clear"
            print(f"  {plabel:>18s} {olabel:>26s} {inter:13.1f} {gap:8.2f}   {verdict}")


def main():
    print("=== wing_root_deconflict.py ===")
    print(f"servo: DS3225 {SERVO_L} x {SERVO_W} x {SERVO_DEPTH} mm, "
          f"{SERVO_MASS_G:.0f} g, 24.5 kgf.cm @ 6.8 V  [datasheet]")
    print(f"  flange span {SERVO_EAR_SPAN} mm (Y); body depth {SERVO_DEPTH} mm inboard (X)")
    print(f"  bolt pattern {2 * mci.NSVMT_HOLE_S_Y:.1f} x {2 * mci.NSVMT_HOLE_S_Z:.1f} mm "
          f"(datasheet; bores {'LIVE' if mci.NSVMT_HOLES_ENABLED else 'gated off'})")

    mid = midline_mm()
    print("\nProtected routes at the wing root (hull frame)")
    print(f"  {'route':>30s} {'chord frac':>11s} {'Y':>8s} {'Z':>8s}")
    for label, bores in route_stations():
        for i, (xfr, d) in enumerate(bores):
            z = WING_CHORD_LINE_Z + mid(xfr)
            y = mci.WING_LE_ROOT_Y + xfr * mci.WING_ROOT_CHORD
            tag = label if len(bores) == 1 else f"{label} #{i + 1}"
            print(f"  {tag:>30s} {xfr:11.3f} {y:+8.2f} {z:+8.2f}   D{d:.1f}")

    shell = load_shell()
    print(f"\nshell: {len(shell.faces):,} faces, watertight={shell.is_watertight}")
    shell_man = to_man(shell)

    findings = []
    for side in ("port", "stbd"):
        check_solids(side, findings)
        check_routes(side, findings, shell_man)
    penetration_check(shell_man, findings)
    tenon_fit_check(findings)
    undersized = pad_fit_check()

    print()
    if not findings and not undersized:
        print("  CLEAR -- servo mounts deconflict and every cableway stays open")
        return
    print("  FINDINGS")
    seen = set()
    for side, msg, vol in findings:
        key = msg
        if key in seen:
            continue
        seen.add(key)
        extra = f"  ({vol:.1f} mm^3)" if vol else ""
        print(f"    {msg}{extra}")
    for axis in undersized:
        print(f"    servo pad UNDERSIZED in {axis}")
    sys.exit(1)


if __name__ == "__main__":
    main()
