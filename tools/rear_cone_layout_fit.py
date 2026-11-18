#!/usr/bin/env python3
"""rear_cone_layout_fit.py -- rear-cone layout of the tail EDF (QX-Motor 64 mm, QF2822
2300 KV, 12-blade rotor, pusher), the fused thrust tube, the nozzle and the RCS jets
on the Rev U one-piece aft hull (plan 002 U5, TEDF-05; R16-R18, R22, R32, R33, R37, R38,
R42; KTD6, KTD8).  Rewritten 2026-11-17 for plan 002: the Delta fan, its adapter, the rear
bell intakes and the baffle of the superseded fan plan are gone.

What it does
  1. MEASURES the rear cone on the published merged aft hull: the thrust axis, the largest
     circle the cavity holds at each station, the nozzle exit plane, the skid crossbar's
     aft face, and the canon plate joints of the skin (grooves in the outer radius).
  2. PLACES the QX shroud as far aft as the hull holds it with the static gap, the rotor in
     it, the motor ahead of it (pusher, KD10), the mounting ring, the tube and the nozzle.
  3. CHECKS the rotor's first critical speed with the overhung rotor, the RCS scoops at
     Y 628 (KD20), the passage areas in the tube-to-skin gap at the scoop run and at each
     exhaust's forward edge, the scoop blockage, the printed webs between passages, a 3D
     spreading-jet check of each jet at its azimuth and aft cant (R17, R32), and each exhaust
     against the plate joints (KD19).  The jets come from tools/rcs_jets.py, the table
     hover_trim_rcs.py also flies (owner option B, 2026-11-18).
  4. Prints one table.  ONE limits list (`limits()`) drives the printout and the exit code.

Nothing here cuts or writes a mesh.  It is the proposal the owner decides at gate G1.

ASSUMED inputs are labelled on every run; any PASS that rests on one is PROVISIONAL.
FIRST CRITICAL SPEED (beam theory, derived here; no catalogued reference): an overhung point
mass m at distance a beyond the front bearing of a shaft simply supported over a span L has
stiffness k = 3 E I / (a^2 (L + a)) at the mass, so w_r = sqrt(k / m).  The shaft's own first
mode between the bearings is w_s = (pi / L)^2 sqrt(E I / (rho A)).  Dunkerley:
1 / w^2 = 1 / w_r^2 + 1 / w_s^2, a lower bound.  Gyroscopic stiffening of the disc is
ignored, which is conservative for forward whirl.  Failure mode: whirl at the critical
speed.  Not computed: shaft fatigue, bearing life (needs the bearing rating).

Run:
    /usr/bin/python3 tools/rear_cone_layout_fit.py [--json OUT.json]
Needs trimesh, shapely, rtree and numpy.  The aft hull is read from its tarball.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-15; rewritten for
         plan 002 U5 by Claude (Anthropic) 2026-11-17 and 2026-11-18, per AGENTS.md section 3.
License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import statistics
import sys
import tarfile
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import hull_datums as hd  # noqa: E402
import rcs_jets as rj  # noqa: E402
import sls_materials as sls  # noqa: E402

AFT_HULL = os.path.join(REPO, "airframe", "stls", "fuselage",
                        "middle_rear_shell24_2mm_merged.stl")
LEDGER = os.path.join(REPO, "current-specification", "auw_ledger.json")

# --- fixed by the owner, the plan or a cited document ------------------------------------
NOZZLE_A, NOZZLE_B = 52.3, 44.7  # mm, fixed elliptical exit, wide x tall (R22)
STERN_STACK_Y1 = 500.0  # aft face of the stern stack (tools/middle_layout_fit.py SIMON_Y1)
STATIC_GAP = 2.0  # mm, static part to fixed hull (cargo_layout_fit convention)
# QX-Motor 64 mm unit [REF-EDF-003]: shroud diameters 77 / 72.4 / 67.2 / 66.4 mm, shroud 45 mm,
# motor can 27.8 mm, overall motor 68.7 mm, body to mount face 58.0 mm, shaft 3.0 mm, 140 g.
QX_LIP_OD = 77.0  # QX shroud lip OD: the printed inlet bellmouth is held to the same OD
# Printed pusher shroud and stator from the nacelle 64 mm geometry (KTD6;
# airframe/openscad/nacelles/edf_motor_mount_64mm.scad): bore 64.0 mm (BORE_R 32.0), wall 2.5 mm,
# motor plate 3.0 mm (PLATE_T), rotor hub 1.0 mm from the plate (P64_GAP), rotor 10.7 mm long
# (rotor 2 at nacelle Z 104.2..114.9), 11 stator vanes of 18 mm chord on the plate.
SHROUD_OD = 64.0 + 2 * 2.5
PLATE_T, ROTOR_GAP, ROTOR_L, VANE_CHORD, N_VANES = 3.0, 1.0, 10.7, 18.0, 11
VANE_HUB_R, ROTOR_TIP_R = 14.3, 32.0
MOTOR_D, MOTOR_BODY_L, MOTOR_OVERALL_L, SHAFT_D = 27.8, 58.0, 68.7, 3.0
MOTOR_G = 140.0
KV, V_NOM, V_FULL = 2300.0, 22.2, 25.2  # rpm/V; 6S nominal and full pack (unloaded speed)
SCOOP_Y = 628.0  # RCS scoops, owner direction 2026-11-16 (KD20, R42)
VENTRAL_MIN_Y = 628.0  # KD16: ventral jets at Y 628 or further aft
RING_OD = 82.6  # mm, fan mounting ring OD 3.25 in (plan 002 "RCS plumbing")
BORE = rj.BORE_MM  # mm, RCS jet bore (plan 002 RCS sizing)
# The jet table is shared with hover_trim_rcs.py (tools/rcs_jets.py): owner option B
# (2026-11-18), one ventral jet at 270 deg on the centre belly panel, upper pair at 45/135.
JETS = rj.JETS
PLAN_JETS = rj.PLAN_JETS  # the plan's 245/295 pair, checked for comparison only
VENTRAL_CLEAR_Y = 635.0  # ventral exhausts clear the crossbar only from here aft (measured map)
JET_REACH = 150.0  # mm, 5.9 in: a jet shall meet no structure within this distance (R17)
WALL_MIN_PRINT = 1.5  # mm, interim SLS floor (owner option A 2026-11-11, AGENTS.md section 7,
# docs/SLS_MIN_WALL_THICKNESS.md); REF-MFG-001's 1.0 mm was superseded for this powder

# --- ASSUMED, labelled on every run ---------------------------------------------------------
ROTOR_G = 20.0  # g, rotor (ledger NACELLE note "20 g ASSUMED, weigh")
LIP_L = 8.0  # mm, axial length of the inlet bellmouth at the 77 mm lip OD
SHROUD_AFT_OF_ROTOR = 1.0  # mm, shroud bore aft of the rotor's aft face, to the shroud joint
SHROUD_FWD_OF_MOTOR = 5.0  # mm, inlet lip ahead of the motor's forward end
SHAFT_E = 200e9  # Pa, steel shaft
SHAFT_RHO = 7850.0  # kg/m^3, steel shaft
BEARING_SPAN = 20.0  # mm, between the motor's two bearings (not on the drawing)
BEARING_SET_IN = 3.0  # mm, front bearing inside the mount face
# Rotor CG beyond the motor mount face: through the 3 mm plate, the 1 mm gap, half the rotor.
ROTOR_CG_OUT = PLATE_T + ROTOR_GAP + ROTOR_L / 2.0
STOCK_CG_OUT = ROTOR_L / 2.0  # the stock QX unit: rotor straight on the motor face (comparison)
MOTOR_EFF = 0.85  # ASSUMED, as the nacelle stator note (edf_motor_mount_64mm.scad)
SPEED_FRACTION = 0.85  # loaded speed = 0.85 x KV x V x throttle (the nacelle tools' rule, ASSUMED)
CRIT_MARGIN_MIN = 1.25  # first critical over the top running speed
EXT_SHAFT_D = 4.0  # mm, the separate-shaft option (plan 002 "Shaft critical speed")
TUBE_R627 = 64.8 / 2.0  # mm, tube bore radius at Y 627 (plan 002 "RCS intake station")
TUBE_WALL = 1.6  # mm, gives the plan's 34.0 mm outer radius at Y 628
SIDE_WALL = 1.5  # mm, passage side walls (plan 002 hand estimate)
SCOOP_LIP_H = 3.5  # mm, inward scoop lip (plan: 3 to 4 mm)
BLOCKAGE_MAX = 0.08  # of the tube area (plan 002: "about 8 %")
PLAN_EXHAUST_Y = 632.0  # the plan's jets left the skin at about Y 632 (KD20 text)
JET_HALF = 12.0  # deg, free-jet spread half angle; swept 8 to 16 in the report
OWN_SKIN_DAZ, OWN_SKIN_DY, OWN_SKIN_DR = 30.0, 20.0, 1.0  # hits near the exhaust on the skin
GROOVE_DEPTH = 0.2  # mm, a dip in the outer radius deeper than this is a plate joint
# De-swirl (owner direction 2026-11-18): the scoops take the swirl out of the RCS bleed and a
# stator in the thrust tube takes it out of the main jet.
SCOOP_LIP_L = 4.0  # mm, ASSUMED axial length of a scoop mouth and its turning vane in the tube
TUBE_STATOR_SETBACK = 1.0  # mm, ASSUMED gap from the scoop lips to the vane leading edges
TUBE_VANE_T = WALL_MIN_PRINT  # vanes at the printed-wall floor (thinnest = least blockage)
HUB_FAIRING_Y0 = 0.5  # mm aft of the rotor: stationary hub fairing carried by the vanes
THROAT_MARGIN = 1.05  # ASSUMED: free area through the vanes and hub >= 1.05 x the nozzle area,
# so the vane row does not become the throat that sets the flow in place of the R22 nozzle
TAPER_Y0 = 627.0  # tube taper starts at the shroud joint (plan 002 planning contour, ASSUMED)

_MESH: dict = {}
_SEC: dict = {}


def load_aft_hull():
    """The merged aft hull, from the inflated STL or from its tarball."""
    if "m" in _MESH:
        return _MESH["m"]
    import trimesh
    if os.path.exists(AFT_HULL):
        m = trimesh.load(AFT_HULL)
    else:
        with tarfile.open(AFT_HULL + ".tar.gz") as tz:
            member = tz.getmembers()[0]
            m = trimesh.load(io.BytesIO(tz.extractfile(member).read()), file_type="stl")
    # Ray casts and section containment are only meaningful on a closed solid
    # (docs/solutions/logic-errors/mesh-boolean-layout-proofs-silent-zero-volumes-...).
    if not m.is_watertight or not m.volume > 0.0:
        raise SystemExit(f"aft hull mesh is not a closed solid (watertight {m.is_watertight}, "
                         f"volume {m.volume:.0f} mm3): the jet and section checks would be wrong")
    _MESH["m"] = m
    return m


def section_solid(mesh, y):
    """Material in the hull section at station y, as a shapely geometry in (X, Z)."""
    key = round(float(y), 2)
    if key in _SEC:
        return _SEC[key]
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    sec = mesh.section(plane_origin=[0.0, float(y), 0.0], plane_normal=[0.0, 1.0, 0.0])
    if sec is None:
        _SEC[key] = Polygon()
        return _SEC[key]
    p, T = sec.to_2D()
    out = []

    def world(coords):
        a = np.array(coords)
        w = (T @ np.c_[a, np.zeros(len(a)), np.ones(len(a))].T).T
        return np.c_[w[:, 0], w[:, 2]]

    for q in p.polygons_full:
        out.append(Polygon(world(q.exterior.coords),
                           [world(r.coords) for r in q.interiors]).buffer(0))
    _SEC[key] = unary_union(out)
    return _SEC[key]


def parts_of(solid) -> list:
    return list(solid.geoms) if hasattr(solid, "geoms") else [solid]


def main_skin(solid, z_axis):
    """The skin polygon: the one that rises highest above the axis (it carries the dorsal)."""
    gs = [g for g in parts_of(solid) if not g.is_empty]
    return max(gs, key=lambda g: (g.bounds[3] > z_axis + 30.0, g.area)) if gs else solid


def inscribed(solid, z_lo=130.0, z_hi=200.0, n=141):
    """Largest circle centred on the centreline that the cavity holds: (dia mm, centre Z)."""
    from shapely.geometry import Point
    best = (0.0, None)
    for z in np.linspace(z_lo, z_hi, n):
        pt = Point(hd.X_CL, z)
        if solid.contains(pt):
            continue
        d = solid.distance(pt)
        if d > best[0]:
            best = (d, float(z))
    return 2.0 * best[0], best[1]


def cavity_closed(solid, z_axis):
    """True when the air around the axis is walled in at this station."""
    from shapely.geometry import Point, box
    x0, z0, x1, z1 = solid.bounds
    frame = box(x0 - 5, z0 - 5, x1 + 5, z1 + 5)
    air = frame.difference(solid)
    pt = Point(hd.X_CL, z_axis)
    for g in parts_of(air):
        if g.contains(pt):
            return not g.intersects(frame.exterior)
    return False


def ellipse(z_axis, a, b):
    from shapely import affinity
    from shapely.geometry import Point
    return affinity.scale(Point(hd.X_CL, z_axis).buffer(1.0, 64), a / 2.0, b / 2.0)


def skin_radii(solid, z_axis, az_deg):
    """(inner, outer) radius of the main skin along azimuth az, from the thrust axis."""
    from shapely.geometry import LineString
    a = math.radians(az_deg)
    line = LineString([(hd.X_CL, z_axis),
                       (hd.X_CL + 300.0 * math.cos(a), z_axis + 300.0 * math.sin(a))])
    hit = line.intersection(main_skin(solid, z_axis))
    spans = []
    for g in parts_of(hit):
        if g.is_empty or g.length < 0.3:
            continue
        ds = [math.hypot(c[0] - hd.X_CL, c[1] - z_axis) for c in g.coords]
        spans.append((min(ds), max(ds)))
    spans.sort()
    return spans[0] if spans else (math.nan, math.nan)


def measure(mesh=None) -> dict[str, Any]:
    """Axis, inscribed diameters, nozzle exit, crossbar aft face, from the mesh."""
    from shapely.geometry import Point
    mesh = mesh or load_aft_hull()
    stations = {}
    for y in range(560, 671, 5):
        s = section_solid(mesh, float(y))
        d, zc = inscribed(s)
        stations[y] = {"dia": d, "zc": zc, "closed": cavity_closed(s, zc) if zc else False}
    zs = [stations[y]["zc"] for y in (620, 625, 630, 635, 640, 645) if stations[y]["zc"]]
    z_axis = float(np.mean(zs))
    exit_y = None
    grown = ellipse(z_axis, NOZZLE_A + 4.0, NOZZLE_B + 4.0)  # nozzle + 2 mm wall
    disc = Point(hd.X_CL, z_axis).buffer(45.0)
    for ye in np.arange(640.0, 672.0, 1.0):
        s = section_solid(mesh, float(ye)).intersection(disc)
        if s.is_empty:
            break
        if s.convex_hull.contains(grown):
            exit_y = float(ye)
    crossbar_aft = None
    for yc in np.arange(610.0, 640.0, 0.5):
        wide = [g for g in parts_of(section_solid(mesh, float(yc)))
                if g.bounds[3] < z_axis - 40.0 and (g.bounds[2] - g.bounds[0]) > 60.0]
        if wide:
            crossbar_aft = float(yc)
    return {"stations": stations, "z_axis": z_axis, "exit_y": exit_y,
            "crossbar_aft_y": crossbar_aft}


def inscribed_at(mesh, y):
    """Inscribed diameter at y.  A slice exactly on a coplanar seam can come back filled (seen at
    Y 614.0, open at 613.95 and 614.05, and a ray down the axis meets no wall there), so a
    filled reading is re-sliced 0.05 mm either side."""
    d = inscribed(section_solid(mesh, float(y)))[0]
    if d < 1.0:
        d = max(inscribed(section_solid(mesh, float(y) + dy))[0] for dy in (-0.05, 0.05))
    return d


SHROUD_JOINT_Y = SCOOP_Y - 1.0  # shroud ends at the joint just forward of the scoops (KD20)


def pusher_stack(joint_y=SHROUD_JOINT_Y) -> dict[str, float]:
    """The pusher stack, aft to forward, from the shroud joint (KD10, KTD6): rotor at the aft
    end, then the motor plate with its stator vanes, then the motor ahead, inside the shroud.
    The rotor-exit swirl is taken out downstream: by the scoops (RCS bleed) and by a stator
    in the thrust tube (main jet), owner direction 2026-11-18."""
    rotor_y1 = joint_y - SHROUD_AFT_OF_ROTOR
    rotor_y0 = rotor_y1 - ROTOR_L
    plate_y1 = rotor_y0 - ROTOR_GAP
    plate_y0 = plate_y1 - PLATE_T
    motor_y1 = plate_y0  # the motor's mount face bears on the plate; its shaft points aft
    motor_y0 = motor_y1 - MOTOR_BODY_L
    return {"rotor_y0": rotor_y0, "rotor_y1": rotor_y1, "rotor_y": 0.5 * (rotor_y0 + rotor_y1),
            "plate_y0": plate_y0, "plate_y1": plate_y1, "motor_face_y": motor_y1,
            "motor_y0": motor_y0, "vanes_y0": plate_y0 - VANE_CHORD, "vanes_y1": plate_y0,
            "shroud_y0": motor_y0 - SHROUD_FWD_OF_MOTOR, "shroud_y1": joint_y}


def shroud_profile_od(y, y0, y1):
    """OD of the shroud at station y: the inlet bellmouth at the lip OD, then the bore wall."""
    if y < y0 or y > y1:
        return 0.0
    return QX_LIP_OD if y < y0 + LIP_L else SHROUD_OD


def shroud_gap(mesh, y0, y1, step=1.0):
    """Smallest radial gap, shroud to hull, along the shroud from y0 to y1: (gap, Y)."""
    best = (1e9, None)
    for y in np.arange(y0, y1 + 0.01, step):
        g = (inscribed_at(mesh, y) - shroud_profile_od(y, y0, y1)) / 2.0
        if g < best[0]:
            best = (g, float(y))
    return best


def layout(meas) -> dict[str, float]:
    st = pusher_stack()
    face_y = st["motor_face_y"]
    return {
        "z_axis": meas["z_axis"], "exit_y": meas["exit_y"], **st,
        "ring_y0": face_y - 10.0, "ring_y1": face_y,  # fused ring at the motor plate plane
        "tube_y0": st["shroud_y1"], "tube_y1": meas["exit_y"],
    }


def rotor_swirl(theta=0.8):
    """Swirl at the rotor exit with no exit stator (the pusher's stator vanes sit AHEAD of the
    rotor, on the motor plate, so they do not straighten its exit swirl).  Euler: the total-
    pressure rise dp = rho U V_theta at the mean radius; axial speed = Q / annulus area.
    Uses tail_edf_flow.py's operating point (PROVISIONAL)."""
    import tail_edf_flow as tf
    r = tf.operate(tf.Inputs(), theta)
    rpm = SPEED_FRACTION * KV * V_NOM * theta
    r_m = 0.5 * (VANE_HUB_R + ROTOR_TIP_R) / 1e3
    u = rpm * 2.0 * math.pi / 60.0 * r_m
    v_t = r.dp_fan_pa / (tf.Inputs().rho * u)
    area = math.pi * ((ROTOR_TIP_R / 1e3) ** 2 - (VANE_HUB_R / 1e3) ** 2)
    v_a = r.flow_m3s / area
    return {"theta": theta, "rpm": rpm, "u_m": u, "v_theta": v_t, "v_axial": v_a,
            "swirl_deg": math.degrees(math.atan2(v_t, v_a)), "dp_fan": r.dp_fan_pa}


NACELLE_SOLIDITY = VANE_CHORD * N_VANES / (math.pi * (VANE_HUB_R + ROTOR_TIP_R))
# chord / pitch at the mean radius of the nacelle stator, which straightens the same rotor


def hub_r(y, y0, y_end):
    """Hub fairing radius: the rotor hub radius at y0, tapering as a straight cone (ASSUMED) to
    a point at y_end, so its half-angle is exactly the boat-tail angle the report prints."""
    if y < y0:
        return VANE_HUB_R
    if y >= y_end:
        return 0.0
    return VANE_HUB_R * (1.0 - (y - y0) / (y_end - y0))


def tube_free_ratio(y, exit_y, st, taper_y0=TAPER_Y0):
    """Free area at y (bore less hub fairing less vanes) over the nozzle area."""
    a, b = tube_bore_ab(y, exit_y, taper_y0)
    rh = hub_r(y, st["hub_y0"], st["hub_y1"])
    vanes = st["n"] * TUBE_VANE_T * (0.5 * (a + b) - rh) if st["le"] <= y <= st["te"] else 0.0
    return (math.pi * a * b - math.pi * rh * rh - vanes) / (math.pi / 4.0 * NOZZLE_A * NOZZLE_B)


def stator_min_ratio(exit_y, st, taper_y0=TAPER_Y0):
    """Smallest free-area ratio over the vanes and hub fairing (not the nozzle exit itself)."""
    end = max(st["te"], st["hub_y1"])
    ys = np.linspace(SHROUD_JOINT_Y, end, 241)
    rs = [tube_free_ratio(float(y), exit_y, st, taper_y0) for y in ys]
    i = int(np.argmin(rs))
    return rs[i], float(ys[i])


def tube_stator(exit_y, rotor_y1, taper_y0=TAPER_Y0, le=None):
    """The tube stator with the highest solidity that keeps the free area at THROAT_MARGIN x
    the nozzle: vanes at the printed floor, leading edge just aft of the scoop lips (or `le`),
    hub fairing from the rotor hub to a point.  Solidity is chord / pitch at the mean radius."""
    le = SCOOP_Y + SCOOP_LIP_L + TUBE_STATOR_SETBACK if le is None else le
    r_m = 0.5 * (VANE_HUB_R + TUBE_R627)
    best = None
    for n in range(5, 17):
        for chord in np.arange(4.0, exit_y - 1.0 - le + 0.01, 1.0):
            for hub_y1 in np.arange(le + 2.0, exit_y + 0.01, 1.0):
                st = {"n": n, "chord": float(chord), "le": le, "te": le + float(chord),
                      "hub_y0": rotor_y1 + HUB_FAIRING_Y0, "hub_y1": float(hub_y1)}
                ratio, y_min = stator_min_ratio(exit_y, st, taper_y0)
                if ratio < THROAT_MARGIN:
                    continue
                sol = float(n * chord / (2.0 * math.pi * r_m))
                key = (sol, hub_y1)  # prefer the longer (gentler) hub fairing at equal solidity
                if best is None or key > best[0]:
                    best = (key, {**st, "solidity": sol, "ratio": ratio, "ratio_y": y_min})
    if best is None:
        return None
    st = best[1]
    st["boat_tail_deg"] = math.degrees(math.atan2(VANE_HUB_R, st["hub_y1"] - st["hub_y0"]))
    return st


def scoop_deswirl(theta=0.8):
    """Swirl at the tube wall at the scoops, which each scoop mouth faces and its turning vane
    takes out.  Free vortex from the rotor's mean radius (V_theta r constant, ASSUMED); axial
    speed = Q over the bore less the hub fairing at Y 628."""
    import tail_edf_flow as tf
    sw = rotor_swirl(theta)
    r_m = 0.5 * (VANE_HUB_R + ROTOR_TIP_R)
    v_t = sw["v_theta"] * r_m / TUBE_R627
    area = math.pi * ((TUBE_R627 / 1e3) ** 2 - (VANE_HUB_R / 1e3) ** 2)
    v_a = tf.operate(tf.Inputs(), theta).flow_m3s / area
    return {"theta": theta, "v_theta": v_t, "v_axial": v_a,
            "yaw_deg": math.degrees(math.atan2(v_t, v_a))}


def tube_bore_ab(y, exit_y, taper_y0=TAPER_Y0):
    """Tube bore semi-axes (a wide, b tall) at y: the 64.8 mm bore held to taper_y0, then
    tapering straight in the ellipse axes to the nozzle at the exit plane (ASSUMED contour)."""
    t = min(1.0, max(0.0, (y - taper_y0) / (exit_y - taper_y0)))
    return (TUBE_R627 + t * (NOZZLE_A / 2.0 - TUBE_R627),
            TUBE_R627 + t * (NOZZLE_B / 2.0 - TUBE_R627))


def tube_outer_r(y, az_deg, exit_y, taper_y0=TAPER_Y0):
    """Tube outer radius at azimuth az_deg: the bore ellipse plus the wall."""
    a, b = tube_bore_ab(y, exit_y, taper_y0)
    th = math.radians(az_deg)
    r = a * b / math.hypot(b * math.cos(th), a * math.sin(th))
    return r + TUBE_WALL


def ring_room(mesh, meas):
    """Radial room outside the mounting ring by station; the last station with room >= 0."""
    rows, last = [], None
    for y in np.arange(595.0, 631.0, 5.0):
        room = (inscribed_at(mesh, y) - RING_OD) / 2.0
        rows.append((float(y), room))
        if room >= 0.0:
            last = float(y)
    return rows, last


# --- first critical speed -------------------------------------------------------------------
def critical_rpm(shaft_d_mm, span_mm, overhang_mm, rotor_g, with_rotor=True):
    """First critical speed, rpm (Dunkerley over the overhung rotor and the shaft's own mode)."""
    d, L, a = shaft_d_mm / 1e3, span_mm / 1e3, overhang_mm / 1e3
    i = math.pi * d ** 4 / 64.0
    area = math.pi * d ** 2 / 4.0
    w_s = (math.pi / L) ** 2 * math.sqrt(SHAFT_E * i / (SHAFT_RHO * area))
    if not with_rotor:
        return w_s * 60.0 / (2.0 * math.pi)
    k = 3.0 * SHAFT_E * i / (a * a * (L + a))
    w_r = math.sqrt(k / (rotor_g / 1e3))
    w = 1.0 / math.sqrt(1.0 / w_r ** 2 + 1.0 / w_s ** 2)
    return w * 60.0 / (2.0 * math.pi)


def top_rpm():
    return KV * V_FULL  # unloaded speed on a full pack: the highest the rotor can turn


def default_overhang():
    return BEARING_SET_IN + ROTOR_CG_OUT


def stock_overhang():
    return BEARING_SET_IN + STOCK_CG_OUT


def max_overhang(shaft_d_mm, margin=CRIT_MARGIN_MIN):
    """Longest overhang that keeps the critical-speed margin (mm)."""
    lo, hi = 0.5, 200.0
    if critical_rpm(shaft_d_mm, BEARING_SPAN, hi, ROTOR_G) / top_rpm() >= margin:
        return hi
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        ok = critical_rpm(shaft_d_mm, BEARING_SPAN, mid, ROTOR_G) / top_rpm() >= margin
        lo, hi = (mid, hi) if ok else (lo, mid)
    return lo


# --- RCS: passages, scoops, plate joints, 3D jet ------------------------------------------
def passage_area(mesh, L, a0, a1, y=SCOOP_Y + 3.0, n=46):
    """Passage area (mm^2) in the sector a0..a1 (deg) of the tube-to-skin gap at station y,
    less two side walls; trapezoid rule over n azimuth samples."""
    s = section_solid(mesh, y)
    area, gaps = 0.0, []
    da = math.radians((a1 - a0) / (n - 1))
    for k in range(n):
        az = a0 + (a1 - a0) * k / (n - 1)
        r_in = skin_radii(s, L["z_axis"], az)[0]
        r_t = tube_outer_r(y, az, L["exit_y"], L.get("taper_y0", TAPER_Y0))
        g = max(0.0, r_in - r_t)
        gaps.append(g)
        w = 0.5 if k in (0, n - 1) else 1.0
        area += w * 0.5 * (r_in ** 2 - r_t ** 2) * da if g > 0 else 0.0
    side = 2.0 * SIDE_WALL * statistics.mean(gaps)
    return max(0.0, area - side), min(gaps), max(gaps)


def passage_stations(jet):
    """Stations where a jet's passage must carry its exhaust area: the scoop-to-exhaust run
    (Y 631) and the exhaust's forward edge, where the whole jet flow still runs axially."""
    return (SCOOP_Y + 3.0, jet.y0)


def jet_passages(mesh, L, jet, sector=None):
    """{station: (area, gap min, gap max)} for the jet's passage sector."""
    a0, a1 = sector or jet.sector
    return {y: passage_area(mesh, L, a0, a1, y=y) for y in passage_stations(jet)}


def sector_needed(mesh, L, jet):
    """Smallest passage sector (deg), grown evenly about the jet's sector centre, whose area
    reaches the exhaust area at every passage station."""
    mid = 0.5 * (jet.sector[0] + jet.sector[1])
    for sec in np.arange(20.0, 140.1, 1.0):
        half = float(sec) / 2.0
        if all(a >= jet.area_mm2 for a, _, _ in
               jet_passages(mesh, L, jet, (mid - half, mid + half)).values()):
            return float(sec)
    return math.inf


VENTRAL_MAP_Y = (632.0, 635.0, 638.0, 641.0)
# both sides probed: the hull and the skid pods are not an exact mirror (learning
# docs/solutions/design-patterns/probe-the-published-hull-and-change-the-placement-class...)
VENTRAL_MAP_AZ = (245.0, 250.0, 255.0, 260.0, 265.0, 270.0, 275.0, 280.0, 285.0, 290.0,
                  295.0)


def ventral_clear_map(L, cant=25.0):
    """{(exhaust Y, azimuth): nearest obstacle or None}: where a bore-size ventral exhaust
    clears both the skid crossbar and the skid pods, port and starboard."""
    out = {}
    for y in VENTRAL_MAP_Y:
        for az in VENTRAL_MAP_AZ:
            j = jet_check(L, az, cant, y=y)
            out[(y, az)] = None if j["clear"] else j["nearest"]
    return out


def classify_hit(hit):
    """Name the obstacle a jet meets: None -> clear; the crossbar ends at Y 627.5 and the
    skid pods sit outboard of X +-30 (both measured on the aft hull)."""
    if hit is None:
        return "clear"
    _, (x, y, _z) = hit
    return "crossbar" if y < 629.0 else ("pod" if abs(x) > 30.0 else "other structure")


def annulus_gaps(mesh, L):
    """Tube-to-skin gap (mm) at each jet azimuth from Y 628 to Y 634."""
    out = {}
    for j in JETS:
        out[j.name] = {float(y): skin_radii(section_solid(mesh, float(y)), L["z_axis"],
                                            j.az_deg)[0]
                       - tube_outer_r(float(y), j.az_deg, L["exit_y"])
                       for y in (628, 630, 632, 634)}
    return out


def passage_webs(L, jets=None):
    """Printed web between neighbouring passages at the tube's outer radius, at the scoop
    station: [(jet a, jet b, web mm)] around the tube, smallest first."""
    jets = list(jets or JETS)
    ordered = sorted(jets, key=lambda j: j.sector[0] % 360.0)
    out = []
    for a, b in zip(ordered, ordered[1:] + ordered[:1]):
        gap = (b.sector[0] - a.sector[1]) % 360.0
        mid = (a.sector[1] + gap / 2.0) % 360.0
        out.append((a.name, b.name, math.radians(gap) * tube_outer_r(SCOOP_Y, mid,
                                                                     L["exit_y"])))
    return sorted(out, key=lambda w: w[2])


def scoop_blockage(L):
    """Inward scoop lips over the tube area at the scoop station: each lip SCOOP_LIP_H tall and
    as wide as the bore scaled by its exhaust area (ASSUMED proportional sizing)."""
    r_bore = TUBE_R627
    mouths = sum(SCOOP_LIP_H * BORE * j.area_mm2 / rj.BORE_AREA_MM2 for j in JETS)
    return mouths / (math.pi * r_bore ** 2)


def plate_joints(mesh, z_axis, y):
    """Azimuths (deg) of the canon plate joints: dips in the outer radius of the skin."""
    s = section_solid(mesh, y)
    rs = [skin_radii(s, z_axis, float(az))[1] for az in range(360)]
    out = []
    for i in range(360):
        win = [rs[(i + k) % 360] for k in range(-4, 5) if not math.isnan(rs[(i + k) % 360])]
        if not win or math.isnan(rs[i]):
            continue
        if statistics.median(win) - rs[i] > GROOVE_DEPTH:
            out.append(i)
    # merge neighbouring degrees into one joint line at the deepest point
    joints, run = [], []
    for a in out + [None]:
        if a is not None and (not run or a - run[-1] <= 1):
            run.append(a)
            continue
        if run:
            joints.append(float(min(run, key=lambda x: rs[x])))
        run = [a] if a is not None else []
    return joints


def _ang(d):
    return ((d + 180.0) % 360.0) - 180.0


def exhaust_fit(mesh, L, jet):
    """The trapezoidal exhaust on the skin (KD19).  A "centred" exhaust is the jet's area over
    its length, centred on its azimuth, with the joint shift each side edge needs.  A "panel"
    exhaust has its sides on the plate joints bounding the jet's panel at every station (owner
    option B): its area is measured by integrating the skin arc between the joints."""
    z = L["z_axis"]
    if jet.edges == "panel":
        ys = np.arange(jet.y0, jet.y1 + 0.01, 0.5)
        lo, hi = [], []
        for y in ys:
            js = plate_joints(mesh, z, float(y))
            near = [min(js, key=lambda j: abs(_ang(j - p)), default=math.nan) for p in jet.panel]
            ok = [not math.isnan(n) and abs(_ang(n - p)) <= 4.0 for n, p in zip(near, jet.panel)]
            lo.append(near[0] if ok[0] else math.nan)
            hi.append(near[1] if ok[1] else math.nan)
        lo_a, hi_a = np.array(lo), np.array(hi)
        for arr, p in ((lo_a, jet.panel[0]), (hi_a, jet.panel[1])):
            good = ~np.isnan(arr)  # a transverse rib station has no azimuthal dip: interpolate
            arr[:] = np.interp(ys, ys[good], arr[good]) if good.any() else p
        widths = []
        for y, a, b in zip(ys, lo_a, hi_a):
            s = section_solid(mesh, float(y))
            az = np.linspace(a, b, 25)
            rs = [skin_radii(s, z, float(t))[1] for t in az]
            widths.append(float(np.trapezoid(rs, np.radians(az))))
        area = float(np.trapezoid(widths, ys))
        return {"name": jet.name, "area_mm2": area, "width_mm": float(np.mean(widths)),
                "width_fwd": widths[0], "width_aft": widths[-1], "r_out": jet.r_mm,
                "edges": (float(lo_a.mean()), float(hi_a.mean())),
                "joint_span": (float(lo_a.min()), float(lo_a.max()), float(hi_a.min()),
                               float(hi_a.max())),
                "shifts": [], "kind": "panel"}
    s = section_solid(mesh, jet.y)
    r_out = skin_radii(s, z, jet.az_deg)[1]
    width = jet.area_mm2 / (jet.y1 - jet.y0)
    half_deg = math.degrees(width / 2.0 / r_out)
    edges = (jet.az_deg - half_deg, jet.az_deg + half_deg)
    joints = plate_joints(mesh, z, jet.y)
    shifts = []
    for e in edges:
        if not joints:
            shifts.append((e, math.nan, math.nan, math.nan))
            continue
        near = min(joints, key=lambda j: abs(_ang(j - e)))
        dd = _ang(near - e)
        shifts.append((e, near, dd, math.radians(abs(dd)) * r_out))
    return {"name": jet.name, "area_mm2": jet.area_mm2, "width_mm": width,
            "width_fwd": width, "width_aft": width, "r_out": r_out, "edges": edges,
            "shifts": shifts, "kind": "centred"}


def jet_rays(L, az_deg, cant_deg, y, half_deg, bore=BORE, nrad=3, nth=24):
    """Ray origins and directions of a spreading jet that leaves the skin as a disc of
    diameter `bore` (for a panel exhaust: its widest width, the conservative lateral extent)."""
    mesh = load_aft_hull()
    s = section_solid(mesh, y)
    r = skin_radii(s, L["z_axis"], az_deg)[1]
    a, c = math.radians(az_deg), math.radians(cant_deg)
    p = np.array([hd.X_CL + r * math.cos(a), y, L["z_axis"] + r * math.sin(a)])
    e = np.array([math.cos(c) * math.cos(a), math.sin(c), math.cos(c) * math.sin(a)])
    u = np.cross(e, [0.0, 1.0, 0.0])
    u /= np.linalg.norm(u)
    v = np.cross(e, u)
    origins, dirs = [p], [e]
    for i in range(1, nrad + 1):
        f = i / nrad
        h = math.radians(half_deg * f)
        for k in range(nth):
            th = 2.0 * math.pi * k / nth
            w = math.cos(th) * u + math.sin(th) * v
            origins.append(p + f * bore / 2.0 * w)
            d = math.cos(h) * e + math.sin(h) * w
            dirs.append(d / np.linalg.norm(d))
    return np.array(origins), np.array(dirs)


def own_skin(L, hit, az_jet, y_jet):
    """A hit on the main skin next to the exhaust is the jet's own exit, not an obstacle."""
    x, y, z = hit
    az = math.degrees(math.atan2(z - L["z_axis"], x - hd.X_CL)) % 360.0
    daz = abs(((az - az_jet + 180.0) % 360.0) - 180.0)
    if daz > OWN_SKIN_DAZ or abs(y - y_jet) > OWN_SKIN_DY:
        return False
    s = section_solid(load_aft_hull(), round(y * 2.0) / 2.0)
    r_out = skin_radii(s, L["z_axis"], az)[1]
    return math.hypot(x - hd.X_CL, z - L["z_axis"]) <= r_out + OWN_SKIN_DR


def jet_check(L, az_deg, cant_deg, y=PLAN_EXHAUST_Y, half_deg=JET_HALF, reach=JET_REACH,
              bore=BORE):
    """3D spreading-jet check: rays from the exhaust disc at the skin, out to `reach`; the
    first hit of each ray that is not the jet's own skin is an obstacle.  Returns the nearest
    obstacle."""
    mesh = load_aft_hull()
    o, d = jet_rays(L, az_deg, cant_deg, y, half_deg, bore=bore)
    o = o + d * 0.5
    loc, idx, _ = mesh.ray.intersects_location(o, d, multiple_hits=True)
    nearest = None
    blocked = set()
    for p_hit, i in zip(loc, idx):
        dist = float(np.linalg.norm(p_hit - o[i]))
        if dist > reach or own_skin(L, p_hit, az_deg, y):
            continue
        blocked.add(int(i))
        if nearest is None or dist < nearest[0]:
            nearest = (dist, [round(float(c), 1) for c in p_hit])
    return {"az": az_deg, "cant": cant_deg, "y": y, "half": half_deg, "rays": len(o),
            "blocked": len(blocked), "nearest": nearest, "clear": not blocked}


# --- mass and CG of the aft hardware (an envelope estimate, U9 replaces it) ----------------
def aft_parts(L) -> list[tuple[str, float, float, str]]:
    rho = sls.rho_g_mm3(sls.PA_CF)
    shroud = math.pi * (SHROUD_OD - 2.5) * 2.5 * (L["shroud_y1"] - L["shroud_y0"]) * rho
    ring = math.pi * (RING_OD - 3.0) * 3.0 * 10.0 * rho
    tube_l = L["tube_y1"] - L["tube_y0"]
    tube = math.pi * 2.0 * (TUBE_R627 + (NOZZLE_A + NOZZLE_B) / 8.0) * TUBE_WALL * tube_l * rho
    return [
        ("QF2822 motor", MOTOR_G, L["motor_face_y"] - MOTOR_BODY_L / 2.0, "REF-EDF-003"),
        ("QX 12-blade rotor", ROTOR_G, L["rotor_y"], "ASSUMED 20 g"),
        ("printed pusher shroud", shroud, (L["shroud_y0"] + L["shroud_y1"]) / 2.0,
         "envelope x PA CF"),
        ("mounting ring (fused)", ring, (L["ring_y0"] + L["ring_y1"]) / 2.0, "envelope"),
        ("motor plate + 11 stator vanes", 8.0, (L["vanes_y0"] + L["plate_y1"]) / 2.0,
         "ASSUMED 8 g"),
        ("thrust tube + nozzle (fused)", tube, (L["tube_y0"] + L["tube_y1"]) / 2.0, "envelope"),
        (f"{len(JETS)} scoops + passages + valves", len(JETS) * 5.0, SCOOP_Y + 3.0,
         "ASSUMED 5 g each"),
    ] + tube_stator_parts(L, rho)


def tube_stator_parts(L, rho) -> list[tuple[str, float, float, str]]:
    st = L.get("tube_stator")
    if not st:
        return []
    a, b = tube_bore_ab(0.5 * (st["le"] + st["te"]), L["exit_y"], L.get("taper_y0", TAPER_Y0))
    vanes = st["n"] * st["chord"] * TUBE_VANE_T * (0.5 * (a + b) - 0.5 * VANE_HUB_R) * rho
    slant = math.hypot(VANE_HUB_R, st["hub_y1"] - st["hub_y0"])
    hub = math.pi * VANE_HUB_R * slant * TUBE_VANE_T * rho  # cone shell at the floor
    return [(f"tube stator, {st['n']} vanes", vanes, 0.5 * (st["le"] + st["te"]),
             "envelope x PA CF"),
            ("hub fairing (shell)", hub, st["hub_y0"] + (st["hub_y1"] - st["hub_y0"]) / 3.0,
             "envelope x PA CF")]


def cg_shift(plist):
    with open(LEDGER, encoding="utf-8") as fh:
        c = json.load(fh)["configs"]["hover_twin_2200"]
    m0, y0 = c["mass_g"], c["cg"][1]
    dm = sum(p[1] for p in plist)
    dy = sum(p[1] * (p[2] - y0) for p in plist) / (m0 + dm)
    return {"m0": m0, "y0": y0, "dm": dm, "dy": dy}


def tube_contour_variant(mesh, L):
    """G1 trade: hold the 64.8 mm bore through a stator of the nacelle's solidity, then taper.
    Finds the latest taper start for which a stator reaches NACELLE_SOLIDITY at the margin, and
    what that costs the RCS passages (narrower tube-to-skin gap)."""
    for t0 in np.arange(TAPER_Y0, L["exit_y"] - 4.0, 1.0):
        st = tube_stator(L["exit_y"], L["rotor_y1"], taper_y0=float(t0))
        if st and st["solidity"] >= NACELLE_SOLIDITY:
            Lv = {**L, "taper_y0": float(t0)}
            pas = {j.name: min(a for a, _, _ in jet_passages(mesh, Lv, j).values())
                   for j in JETS}
            return {"taper_y0": float(t0), "stator": st, "passages": pas,
                    "taper_len": L["exit_y"] - float(t0)}
    return None


# --- evaluation -----------------------------------------------------------------------------
def jet_bore(e):
    """Disc diameter for the 3D jet check: the bore, or a wider exhaust's widest width."""
    return max(BORE, e["width_fwd"], e["width_aft"])


def evaluate() -> dict[str, Any]:
    mesh = load_aft_hull()
    meas = measure(mesh)
    if meas["exit_y"] is None:
        raise SystemExit("nozzle exit plane not found on the aft hull mesh: the tube, stator, "
                         "passages and jets cannot be placed (FAIL)")
    L = layout(meas)
    gap, gap_y = shroud_gap(mesh, L["shroud_y0"], L["shroud_y1"])
    rows, ring_last = ring_room(mesh, meas)
    crit = critical_rpm(SHAFT_D, BEARING_SPAN, default_overhang(), ROTOR_G)
    crit_stock = critical_rpm(SHAFT_D, BEARING_SPAN, stock_overhang(), ROTOR_G)
    swirl = {th: rotor_swirl(th) for th in (0.8, 1.0)}
    deswirl = {th: scoop_deswirl(th) for th in (0.8, 1.0)}
    L["tube_stator"] = tube_stator(L["exit_y"], L["rotor_y1"])
    contour = tube_contour_variant(mesh, L)
    exh = {j.name: exhaust_fit(mesh, L, j) for j in JETS}
    jets = {j.name: jet_check(L, j.az_deg, j.cant_deg, y=j.y, bore=jet_bore(exh[j.name]))
            for j in JETS}
    plan_jets = {j.name: jet_check(L, j.az_deg, j.cant_deg) for j in PLAN_JETS if j.ventral}
    radial = jet_check(L, 245.0, 0.0, y=634.0)  # plan check: a radial ventral jet at Y 634
    sweep = {h: {j.name: jet_check(L, j.az_deg, j.cant_deg, y=j.y, half_deg=h,
                                   bore=jet_bore(exh[j.name]))["clear"] for j in JETS}
             for h in (8.0, 16.0)}
    joints = {y: plate_joints(mesh, L["z_axis"], float(y)) for y in (628, 630, 632, 634)}
    pas = {j.name: jet_passages(mesh, L, j) for j in JETS}
    need = {j.name: sector_needed(mesh, L, j) for j in JETS}
    band = ventral_clear_map(L)
    plist = aft_parts(L)
    r = {"meas": meas, "layout": L, "gap": (gap, gap_y), "ring_rows": rows,
         "ring_last": ring_last, "crit_rpm": crit, "crit_stock_rpm": crit_stock,
         "swirl": swirl, "deswirl": deswirl, "contour": contour, "top_rpm": top_rpm(),
         "nom_rpm": KV * V_NOM, "max_overhang_3": max_overhang(SHAFT_D),
         "max_overhang_4": max_overhang(EXT_SHAFT_D), "jets": jets, "plan_jets": plan_jets,
         "radial": radial, "sweep": sweep, "joints": joints, "exhaust": exh, "passages": pas,
         "sector_needed": need, "ventral_band": band,
         "annulus": annulus_gaps(mesh, L), "webs": passage_webs(L),
         "blockage": scoop_blockage(L), "parts": plist, "cg": cg_shift(plist)}
    r["limits"] = limits(r)
    r["design_rules"] = design_rules(r)
    return r


def design_rules(r) -> list[tuple[str, bool]]:
    """Rules the layout holds by construction (printed, not gated: they cannot fail here)."""
    L = r["layout"]
    st = L["tube_stator"]
    up = [j for j in JETS if not j.ventral]
    return [
        ("scoops at Y 628 (KD20)", SCOOP_Y == 628.0),
        ("shroud ends at the joint, forward of the scoops", L["shroud_y1"] <= SCOOP_Y),
        ("pusher order: motor plate ahead of the rotor (KD10)",
         L["rotor_y0"] - L["plate_y1"] >= ROTOR_GAP),
        ("upper jets mirror port/starboard", len(up) == 2
         and abs(up[0].az_deg + up[1].az_deg - 180.0) < 1e-9),
        ("tube stator free area >= margin x nozzle (the search's own filter)",
         bool(st) and st["ratio"] >= THROAT_MARGIN),
    ]


def limits(r) -> list[tuple[str, float, str, float, str]]:
    """THE limits list: (name, value, comparison, limit, unit)."""
    L = r["layout"]
    out: list[tuple[str, float, str, float, str]] = [
        ("radial gap, shroud to hull", r["gap"][0], ">=", STATIC_GAP, "mm"),
        ("motor clear of the stern stack", L["motor_y0"] - STERN_STACK_Y1, ">=",
         STATIC_GAP, "mm"),
        ("rotor forward of the nozzle exit", L["exit_y"] - L["rotor_y1"], ">=", 0.0, "mm"),
        ("mounting ring ends where the hull still holds it",
         (r["ring_last"] or 0.0) - L["ring_y1"], ">=", 0.0, "mm"),
        ("first critical speed over the top running speed", r["crit_rpm"] / r["top_rpm"],
         ">=", CRIT_MARGIN_MIN, ""),
        ("scoop blockage of the tube", r["blockage"], "<=", BLOCKAGE_MAX, ""),
        ("tube stator found with the vane row clear of the throat",
         0.0 if L["tube_stator"] is None else 1.0, ">=", 1.0, ""),
        ("narrowest web between passages at least the minimum printed wall",
         r["webs"][0][2], ">=", WALL_MIN_PRINT, "mm"),
    ]
    for j in JETS:
        e = r["exhaust"][j.name]
        if j.ventral:
            out.append((f"ventral exhaust forward edge at or aft of Y {VENTRAL_MIN_Y:.0f} "
                        f"(KD16), {j.name}", j.y0 - VENTRAL_MIN_Y, ">=", 0.0, "mm"))
            out.append((f"ventral exhaust forward edge clear of the crossbar (Y "
                        f"{VENTRAL_CLEAR_Y:.0f}), {j.name}", j.y0 - VENTRAL_CLEAR_Y, ">=", 0.0,
                        "mm"))
        if e["kind"] == "panel":
            out.append((f"exhaust area on the panel matches the jet table, {j.name}",
                        abs(e["area_mm2"] / j.area_mm2 - 1.0), "<=", 0.03, ""))
        for y, (a, _, _) in r["passages"][j.name].items():
            out.append((f"passage area >= exhaust area at Y {y:.0f}, {j.name}", a, ">=",
                        j.area_mm2, "mm2"))
        out.append((f"3D jet path clear within {JET_REACH:.0f} mm, {j.name}",
                    float(r["jets"][j.name]["blocked"]), "<=", 0.0, "rays"))
    return out


def passed(limit):
    _, v, op, lim, _ = limit
    return v >= lim if op == ">=" else v <= lim


def report(r):
    L, m = r["layout"], r["meas"]
    print("REAR CONE LAYOUT, tail EDF (plan 002 U5), frame R2, mm.  PROVISIONAL.")
    print("ASSUMED: rotor 20 g; inlet lip 8 mm at 77 mm OD; bearing span 20 mm, set in 3 mm; steel "
          "shaft E 200 GPa; tube wall 1.6 mm; jet half-angle 12 deg; hub fairing a cone; "
          "scoop lip 3.5 mm; loaded speed 0.85 KV V; motor efficiency 0.85.")
    print(f"  thrust axis Z {m['z_axis']:.1f}; nozzle exit plane Y {L['exit_y']:.0f}; skid "
          f"crossbar aft face Y {m['crossbar_aft_y']}")
    print(f"  pusher shroud (nacelle 64 mm bore, {SHROUD_OD:.0f} mm OD, {QX_LIP_OD:.0f} mm inlet "
          f"lip) Y {L['shroud_y0']:.1f}..{L['shroud_y1']:.1f}; min gap {r['gap'][0]:.1f} mm "
          f"({r['gap'][0] / 25.4:.2f} in) at Y {r['gap'][1]:.0f}")
    print(f"  stack, forward to aft (air flows aft): motor Y {L['motor_y0']:.1f}.."
          f"{L['motor_face_y']:.1f}; stator vanes Y {L['vanes_y0']:.1f}..{L['vanes_y1']:.1f} "
          f"(on the plate, AHEAD of the rotor); plate Y {L['plate_y0']:.1f}..{L['plate_y1']:.1f};"
          f" rotor Y {L['rotor_y0']:.1f}..{L['rotor_y1']:.1f}; shroud joint Y "
          f"{L['shroud_y1']:.0f}; ring Y {L['ring_y0']:.0f}..{L['ring_y1']:.0f}; tube Y "
          f"{L['tube_y0']:.0f}..{L['tube_y1']:.0f}")
    for th, sw in r["swirl"].items():
        print(f"  rotor-exit swirl at {th:.0%} throttle, before any de-swirl: "
              f"{sw['swirl_deg']:.0f} deg (V_theta {sw['v_theta']:.0f} m/s on {sw['v_axial']:.0f} "
              f"m/s axial, {sw['rpm']:,.0f} rpm, Euler from dp {sw['dp_fan'] / 1e3:.1f} kPa) "
              f"reaches the scoops {SCOOP_Y - L['rotor_y1']:.0f} mm downstream; the reused "
              "plate stator is upstream and straightens nothing.")
    print("  room outside the mounting ring (OD 82.6 mm): " + ", ".join(
        f"Y {y:.0f} {room:+.1f}" for y, room in r["ring_rows"]) +
        f" mm; last station with room Y {r['ring_last']}")
    print(f"  first critical speed {r['crit_rpm']:,.0f} rpm, rotor on the 3 mm motor shaft "
          f"through the plate, overhang {default_overhang():.2f} mm; top speed "
          f"{r['top_rpm']:,.0f} rpm (unloaded, 25.2 V; {r['nom_rpm']:,.0f} at 22.2 V); margin "
          f"{r['crit_rpm'] / r['top_rpm']:.2f}.  Stock QX (rotor on the motor face, overhang "
          f"{stock_overhang():.2f} mm): {r['crit_stock_rpm']:,.0f} rpm, margin "
          f"{r['crit_stock_rpm'] / r['top_rpm']:.2f}")
    loaded = SPEED_FRACTION * KV * V_FULL
    print(f"  the same critical against the plan's 51,000 rpm: {r['crit_rpm'] / 51000.0:.2f}; "
          f"against the loaded full-pack speed {loaded:,.0f} rpm: {r['crit_rpm'] / loaded:.2f}. "
          "The four nacelle units use the same plate stack: if the bearing positions "
          "(ASSUMED here) hold, they carry the same margin; measure them (NAC-64-FIT-02).")
    print("  DE-SWIRL (owner direction 2026-11-18): the scoops take the swirl out of the RCS "
          "bleed; a stator in the thrust tube takes it out of the main jet.")
    for th, d in r["deswirl"].items():
        print(f"    at {th:.0%} throttle the wall swirl at the scoops is {d['yaw_deg']:.0f} deg "
              f"(V_theta {d['v_theta']:.0f} m/s, free vortex from the rotor mean radius, on "
              f"{d['v_axial']:.0f} m/s axial): each scoop mouth yaws that far into the swirl and "
              "its turning vane takes it out; the yaw sense follows the rotor hand (CW or CCW, "
              "REF-EDF-003 drawing shows both), not yet chosen.")
    st = L["tube_stator"]
    if st:
        print(f"    tube stator: {st['n']} vanes, {st['chord']:.0f} mm chord at the "
              f"{TUBE_VANE_T:.1f} mm wall floor, Y {st['le']:.0f}..{st['te']:.0f} (leading edge "
              f"{TUBE_STATOR_SETBACK:.0f} mm aft of the {SCOOP_LIP_L:.0f} mm scoop lips); hub "
              f"fairing r {VANE_HUB_R} mm from Y {st['hub_y0']:.1f} to a point at Y "
              f"{st['hub_y1']:.0f} (boat-tail {st['boat_tail_deg']:.0f} deg); least free area "
              f"{st['ratio']:.2f} x nozzle at Y {st['ratio_y']:.1f}; solidity "
              f"{st['solidity']:.2f} against the nacelle stator's {NACELLE_SOLIDITY:.2f} on the "
              "same rotor: the sparse stator, owner decision 2026-11-18 (planning taper kept); "
              "the residual swirl and roll torque go to CFD (U12).  Further aft the vane row "
              "would become the throat in place of the R22 nozzle.")
    else:
        print("    tube stator: NO vane row fits with the free area at "
              f"{THROAT_MARGIN} x the nozzle on the planning contour.")
    cv = r["contour"]
    if cv:
        cs = cv["stator"]
        print("    (declined 2026-11-18) tube contour: holding the 64.8 mm bore to Y "
              f"{cv['taper_y0']:.0f} "
              f"(taper {cv['taper_len']:.0f} mm to the nozzle) fits {cs['n']} vanes of "
              f"{cs['chord']:.0f} mm, solidity {cs['solidity']:.2f}; RCS passage areas then "
              + ", ".join(f"{n} {a:.0f}" for n, a in cv["passages"].items())
              + f" mm2 (against {math.pi / 4.0 * BORE ** 2:.0f} needed).")
    else:
        print("    (declined 2026-11-18) tube contour: no taper start reaches the nacelle "
              "solidity.")
    print(f"  longest overhang for margin {CRIT_MARGIN_MIN}: 3 mm shaft "
          f"{r['max_overhang_3']:.1f} mm; separate 4 mm shaft {r['max_overhang_4']:.1f} mm. "
          "Default: rotor on the motor shaft (owner decides at G1).")
    print("  plate joints (outer-radius grooves), deg: " + "; ".join(
        f"Y {y}: {', '.join(f'{a:.0f}' for a in js)}" for y, js in r["joints"].items()))
    print("  RCS jets (shared table tools/rcs_jets.py; owner option B 2026-11-18; scoops Y 628):")
    for jt in JETS:
        n = jt.name
        j, e = r["jets"][n], r["exhaust"][n]
        pas = "; ".join(f"Y {y:.0f} {a:.0f} mm2 (gap {g0:.1f}-{g1:.1f})"
                        for y, (a, g0, g1) in r["passages"][n].items())
        if e["kind"] == "panel":
            ed = (f"sides on the panel joints {e['edges'][0]:.1f}/{e['edges'][1]:.1f} deg "
                  f"(found {e['joint_span'][0]:.0f}-{e['joint_span'][1]:.0f} and "
                  f"{e['joint_span'][2]:.0f}-{e['joint_span'][3]:.0f}), "
                  f"{e['width_fwd']:.1f} mm wide forward to {e['width_aft']:.1f} mm aft, "
                  f"measured area {e['area_mm2']:.0f} mm2 (table {jt.area_mm2:.0f})")
        else:
            ed = f"{e['width_mm']:.1f} mm wide; " + ", ".join(
                f"edge {s[0]:.0f} -> joint {s[1]:.0f} ({s[3]:.1f} mm)" for s in e["shifts"])
        print(f"    {n}: az {jt.az_deg:.0f}, cant {jt.cant_deg:.0f}, exhaust Y {jt.y0:.0f}-"
              f"{jt.y1:.0f}; {'CLEAR' if j['clear'] else 'BLOCKED'} ({j['blocked']}/"
              f"{j['rays']} rays; nearest {j['nearest']}); passage {jt.sector[0]:.1f}-"
              f"{jt.sector[1]:.1f} deg: {pas}; {ed}")
    for n, j in r["plan_jets"].items():
        print(f"  plan comparison, {n} at Y {PLAN_EXHAUST_Y:.0f}: "
              f"{'CLEAR' if j['clear'] else 'BLOCKED'} ({j['blocked']}/{j['rays']} rays; "
              f"nearest {classify_hit(j['nearest'])} {j['nearest']})")
    rd = r["radial"]
    print(f"  plan check, radial ventral jet at Y 634: {'CLEAR' if rd['clear'] else 'BLOCKED'} "
          f"({rd['blocked']}/{rd['rays']} rays; nearest {rd['nearest']})")
    print("  half-angle sweep (clear?): " + "; ".join(
        f"{h:.0f} deg: " + ", ".join(f"{n} {'Y' if ok else 'N'}" for n, ok in s.items())
        for h, s in r["sweep"].items()))
    print("  tube-to-skin gap by station (mm): " + "; ".join(
        f"{n}: " + ", ".join(f"Y{y:.0f} {g:.1f}" for y, g in gs.items())
        for n, gs in r["annulus"].items()))
    print("  passage sector needed for the exhaust area at every station (deg; now): " +
          ", ".join(f"{jt.name} {r['sector_needed'][jt.name]:.0f} "
                    f"({jt.sector[1] - jt.sector[0]:.0f})" for jt in JETS))
    print("  ventral exhaust map, bore-size jet, 25 deg cant, both sides: Y by azimuth -> clear "
          f"or the obstacle (crossbar aft face Y {r['meas']['crossbar_aft_y']}; skid pods X "
          "+-34 to 56)")
    for y in VENTRAL_MAP_Y:
        cells = []
        for az in VENTRAL_MAP_AZ:
            hit = r["ventral_band"][(y, az)]
            cells.append(f"{az:.0f} {classify_hit(hit)}")
        print(f"    Y {y:.0f}: " + ", ".join(cells))
    print("  webs between passages at the tube (mm): " + ", ".join(
        f"{a}/{b} {w:.1f}" for a, b, w in r["webs"]) + f"; scoop blockage {r['blockage']:.1%}")
    print("  design rules (hold by construction; printed, not gated): " + "; ".join(
        f"{n} {'yes' if ok else 'NO'}" for n, ok in r["design_rules"]))
    print("  valve concepts for the G1 trade (layout only): A sliding shutter in each passage "
          "(axial room = the 6 mm scoop-to-exhaust run); B hinged skin-plate flap over each "
          "exhaust (hinge on a plate joint); C servos aft at Y 590-600 (room outside the ring "
          "above).  Control runs from the forward servos are cables (no pushrod room aft of the "
          "ring).")
    cg = r["cg"]
    print(f"  aft hardware {cg['dm']:.0f} g ({cg['dm'] / 453.592:.2f} lbm, envelope estimate): CG "
          f"{cg['dy']:+.1f} mm on hover_twin_2200 (the speed controller and RCS servos move "
          "forward and are not counted here)")
    print("\n  check | value | limit | result")
    ok = True
    for lim in r["limits"]:
        name, v, op, limv, unit = lim
        good = passed(lim)
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  {name}: {v:.3g} {op} {limv:.3g} {unit}")
    print("\nRESULT:", "PASS -- PROVISIONAL" if ok else "FAIL -- owner decision needed (G1 brief)")
    return ok


def jsonable(obj):
    """JSON-safe copy: tuple dict keys (the ventral map's (Y, az)) become "Y/az" strings."""
    if isinstance(obj, dict):
        return {("/".join(f"{x:g}" for x in k) if isinstance(k, tuple) else k): jsonable(v)
                for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    return obj


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", help="write the evaluation to this JSON file")
    args = ap.parse_args(argv)
    r = evaluate()
    ok = report(r)
    if args.json:
        dump = jsonable({k: v for k, v in r.items() if k not in ("meas",)})
        dump["limits"] = [list(x) + [passed(x)] for x in r["limits"]]
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(dump, f, indent=1, default=str)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
