#!/usr/bin/env python3
"""rear_cone_layout_fit.py -- rear-cone layout of the tail EDF (QX-Motor 64 mm, QF2822
2300 KV, 12-blade rotor, pusher), the fused thrust tube, the nozzle and the four RCS jets
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
     Y 628 (KD20), the passage areas in the tube-to-skin gap, the scoop blockage, the
     printed web between the ventral passages, a 3D spreading-jet check of each jet at its
     azimuth and aft cant (R17, R32), and each exhaust against the plate joints (KD19).
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
         plan 002 U5 by Claude (model: Claude Opus 5.5) 2026-11-17, per AGENTS.md section 3.
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
QX_LIP_OD, QX_BODY_OD, QX_SHROUD_L = 77.0, 72.4, 45.0
MOTOR_D, MOTOR_BODY_L, MOTOR_OVERALL_L, SHAFT_D = 27.8, 58.0, 68.7, 3.0
MOTOR_G = 140.0
KV, V_NOM, V_FULL = 2300.0, 22.2, 25.2  # rpm/V; 6S nominal and full pack (unloaded speed)
SCOOP_Y = 628.0  # RCS scoops, owner direction 2026-11-16 (KD20, R42)
VENTRAL_MIN_Y = 628.0  # KD16: ventral jets at Y 628 or further aft
RING_OD = 82.6  # mm, fan mounting ring OD 3.25 in (plan 002 "RCS plumbing")
BORE = 0.71 * 25.4  # mm, RCS jet bore (plan 002 RCS sizing)
JETS = (  # (name, azimuth deg from +X, aft cant deg): R32, KD20
    ("ventral 245", 245.0, 25.0), ("ventral 295", 295.0, 25.0),
    ("upper 45", 45.0, 0.0), ("upper 135", 135.0, 0.0))
SECTOR_DEG = 45.0  # passage sector per jet (plan 002 hand estimate)
JET_REACH = 150.0  # mm, 5.9 in: a jet shall meet no structure within this distance (R17)
WALL_MIN_PRINT = 1.0  # mm, "keep all features above 1mm thickness" [REF-MFG-001 p. 15]

# --- ASSUMED, labelled on every run ---------------------------------------------------------
ROTOR_G = 20.0  # g, rotor (ledger NACELLE note "20 g ASSUMED, weigh")
LIP_L = 8.0  # mm, axial length of the 77 mm lip; the rest of the shroud is the 72.4 mm body
ROTOR_FROM_LIP = 12.0  # mm, rotor plane aft of the shroud's forward (lip) face
SHAFT_E = 200e9  # Pa, steel shaft
SHAFT_RHO = 7850.0  # kg/m^3, steel shaft
BEARING_SPAN = 20.0  # mm, between the motor's two bearings (not on the drawing)
BEARING_SET_IN = 3.0  # mm, front bearing inside the mount face
ROTOR_CG_OUT = 5.0  # mm, rotor CG beyond the mount face
CRIT_MARGIN_MIN = 1.25  # first critical over the top running speed
EXT_SHAFT_D = 4.0  # mm, the separate-shaft option (plan 002 "Shaft critical speed")
TUBE_R627 = 64.8 / 2.0  # mm, tube bore radius at Y 627 (plan 002 "RCS intake station")
TUBE_WALL = 1.6  # mm, gives the plan's 34.0 mm outer radius at Y 628
SIDE_WALL = 1.5  # mm, passage side walls (plan 002 hand estimate)
SCOOP_LIP_H = 3.5  # mm, inward scoop lip (plan: 3 to 4 mm)
BLOCKAGE_MAX = 0.08  # of the tube area (plan 002: "about 8 %")
EXHAUST_Y = 632.0  # jets leave the skin from about Y 632 (plan 002 KD20 text)
EXHAUST_L = 10.0  # mm, axial length of each trapezoidal exhaust
JET_HALF = 12.0  # deg, free-jet spread half angle; swept 8 to 16 in the report
OWN_SKIN_DAZ, OWN_SKIN_DY, OWN_SKIN_DR = 30.0, 20.0, 1.0  # hits near the exhaust on the skin
GROOVE_DEPTH = 0.2  # mm, a dip in the outer radius deeper than this is a plate joint

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


def shroud_profile_od(y, y0):
    """OD of the shroud at station y for a shroud whose forward (lip) face is at y0."""
    if y < y0 or y > y0 + QX_SHROUD_L:
        return 0.0
    return QX_LIP_OD if y < y0 + LIP_L else QX_BODY_OD


def shroud_gap(mesh, y0, step=1.0):
    """Smallest radial gap, shroud to hull, along a shroud with its lip face at y0: (gap, Y)."""
    best = (1e9, None)
    for y in np.arange(y0, y0 + QX_SHROUD_L + 0.01, step):
        g = (inscribed_at(mesh, y) - shroud_profile_od(y, y0)) / 2.0
        if g < best[0]:
            best = (g, float(y))
    return best


SHROUD_JOINT_Y = SCOOP_Y - 1.0  # shroud ends at the joint just forward of the scoops (KD20)


def place_shroud(mesh, y_lo=560.0):
    """Lip-face station: the shroud ends at the shroud joint (Y 627) unless the hull holds it
    only further forward; returns (station, aftmost station that fits)."""
    fit = None
    for y0 in np.arange(y_lo, SHROUD_JOINT_Y - QX_SHROUD_L + 0.01, 1.0):
        if shroud_gap(mesh, float(y0), step=1.0)[0] >= STATIC_GAP:
            fit = float(y0)
    return fit, fit


def layout(meas, y0) -> dict[str, float]:
    exit_y = meas["exit_y"]
    rotor_y = y0 + ROTOR_FROM_LIP
    face_y = rotor_y - ROTOR_CG_OUT  # motor mount face toward the rotor (pusher)
    return {
        "z_axis": meas["z_axis"], "exit_y": exit_y,
        "shroud_y0": y0, "shroud_y1": y0 + QX_SHROUD_L, "rotor_y": rotor_y,
        "motor_face_y": face_y, "motor_y0": face_y - MOTOR_BODY_L,
        "ring_y0": face_y - 10.0, "ring_y1": face_y,  # ring at the motor mount plane
        "tube_y0": y0 + QX_SHROUD_L, "tube_y1": exit_y,
    }


def tube_outer_r(y, az_deg, exit_y):
    """Tube outer radius: the 64.8 mm bore at Y 627 tapering to the nozzle ellipse at the
    exit plane (ASSUMED straight in the ellipse axes), plus the wall."""
    t = min(1.0, max(0.0, (y - 627.0) / (exit_y - 627.0)))
    a = TUBE_R627 + t * (NOZZLE_A / 2.0 - TUBE_R627)
    b = TUBE_R627 + t * (NOZZLE_B / 2.0 - TUBE_R627)
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
def passage_area(mesh, L, az_deg, y=SCOOP_Y + 3.0, n=46):
    """Passage area (mm^2) in a SECTOR_DEG sector of the tube-to-skin gap at station y, less
    two side walls."""
    s = section_solid(mesh, y)
    half = SECTOR_DEG / 2.0
    area, gaps = 0.0, []
    da = math.radians(SECTOR_DEG / (n - 1))
    for k in range(n):
        az = az_deg - half + SECTOR_DEG * k / (n - 1)
        r_in = skin_radii(s, L["z_axis"], az)[0]
        r_t = tube_outer_r(y, az, L["exit_y"])
        g = max(0.0, r_in - r_t)
        gaps.append(g)
        area += 0.5 * (r_in ** 2 - r_t ** 2) * da if g > 0 else 0.0
    side = 2.0 * SIDE_WALL * statistics.mean(gaps)
    return max(0.0, area - side), min(gaps), max(gaps)


def sector_needed(mesh, L, az_deg):
    """Smallest passage sector (deg) whose area reaches the exhaust area."""
    global SECTOR_DEG
    need = math.pi / 4.0 * BORE ** 2
    keep = SECTOR_DEG
    try:
        for sec in np.arange(40.0, 90.1, 1.0):
            SECTOR_DEG = float(sec)
            if passage_area(mesh, L, az_deg)[0] >= need:
                return float(sec)
        return math.inf
    finally:
        SECTOR_DEG = keep


VENTRAL_MAP_Y = (632.0, 635.0, 638.0, 641.0)
VENTRAL_MAP_AZ = (245.0, 250.0, 255.0, 260.0, 265.0, 270.0)


def ventral_clear_map(L, cant=25.0):
    """{(exhaust Y, azimuth): nearest obstacle or None} for the 245 side (295 mirrors): where a
    ventral exhaust clears both the skid crossbar and the skid pods."""
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
    for name, az, _ in JETS:
        out[name] = {float(y): skin_radii(section_solid(mesh, float(y)), L["z_axis"], az)[0]
                     - tube_outer_r(float(y), az, L["exit_y"]) for y in (628, 630, 632, 634)}
    return out


def ventral_web_mm(L):
    """Printed web between the two ventral passages, at the tube's outer radius."""
    az = [a for n, a, _ in JETS if n.startswith("ventral")]
    gap_deg = abs(az[1] - az[0]) - SECTOR_DEG
    return math.radians(gap_deg) * tube_outer_r(SCOOP_Y, 270.0, L["exit_y"])


def scoop_blockage(L):
    """Four inward scoop lips (height x bore width) over the tube area at the scoop station."""
    r_bore = TUBE_R627
    return 4 * SCOOP_LIP_H * BORE / (math.pi * r_bore ** 2)


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


def exhaust_fit(mesh, L, joints, name, az_deg):
    """Trapezoidal exhaust of the bore's area: arc width from the required area over
    EXHAUST_L, centred on the jet azimuth; the joint shift each side edge needs."""
    s = section_solid(mesh, EXHAUST_Y)
    r_out = skin_radii(s, L["z_axis"], az_deg)[1]
    area = math.pi / 4.0 * BORE ** 2
    width = area / EXHAUST_L
    half_deg = math.degrees(width / 2.0 / r_out)
    edges = (az_deg - half_deg, az_deg + half_deg)
    shifts = []
    for e in edges:
        d = min(((j - e + 180.0) % 360.0) - 180.0 for j in joints) if joints else math.nan
        near = min(joints, key=lambda j: abs(((j - e + 180.0) % 360.0) - 180.0)) \
            if joints else math.nan
        dd = ((near - e + 180.0) % 360.0) - 180.0
        shifts.append((e, near, dd, math.radians(abs(dd)) * r_out))
        del d
    return {"name": name, "area_mm2": area, "width_mm": width, "r_out": r_out,
            "edges": edges, "shifts": shifts}


def jet_rays(L, az_deg, cant_deg, y, half_deg, nrad=3, nth=24):
    """Ray origins and directions of a spreading jet that leaves the skin as the bore."""
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
            origins.append(p + f * BORE / 2.0 * w)
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


def jet_check(L, az_deg, cant_deg, y=EXHAUST_Y, half_deg=JET_HALF, reach=JET_REACH):
    """3D spreading-jet check: rays from the bore at the skin, out to `reach`; the first hit of
    each ray that is not the jet's own skin is an obstacle.  Returns the nearest obstacle."""
    mesh = load_aft_hull()
    o, d = jet_rays(L, az_deg, cant_deg, y, half_deg)
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
    shroud = math.pi * (QX_BODY_OD - 2.0) * 2.0 * QX_SHROUD_L * rho
    ring = math.pi * (RING_OD - 3.0) * 3.0 * 10.0 * rho
    tube_l = L["tube_y1"] - L["tube_y0"]
    tube = math.pi * 2.0 * (TUBE_R627 + (NOZZLE_A + NOZZLE_B) / 8.0) * TUBE_WALL * tube_l * rho
    return [
        ("QF2822 motor", MOTOR_G, L["motor_face_y"] - MOTOR_BODY_L / 2.0, "REF-EDF-003"),
        ("QX 12-blade rotor", ROTOR_G, L["rotor_y"], "ASSUMED 20 g"),
        ("printed pusher shroud", shroud, (L["shroud_y0"] + L["shroud_y1"]) / 2.0,
         "envelope x PA CF"),
        ("mounting ring (fused)", ring, (L["ring_y0"] + L["ring_y1"]) / 2.0, "envelope"),
        ("thrust tube + nozzle (fused)", tube, (L["tube_y0"] + L["tube_y1"]) / 2.0, "envelope"),
        ("4 scoops + passages + valves", 4 * 5.0, SCOOP_Y + 3.0, "ASSUMED 5 g each"),
    ]


def cg_shift(plist):
    with open(LEDGER, encoding="utf-8") as fh:
        c = json.load(fh)["configs"]["hover_twin_2200"]
    m0, y0 = c["mass_g"], c["cg"][1]
    dm = sum(p[1] for p in plist)
    dy = sum(p[1] * (p[2] - y0) for p in plist) / (m0 + dm)
    return {"m0": m0, "y0": y0, "dm": dm, "dy": dy}


# --- evaluation -----------------------------------------------------------------------------
def evaluate() -> dict[str, Any]:
    mesh = load_aft_hull()
    meas = measure(mesh)
    y0, _ = place_shroud(mesh)
    if y0 is None:
        raise SystemExit("[rear_cone_layout_fit] no station holds the QX shroud with the gap")
    L = layout(meas, y0)
    gap, gap_y = shroud_gap(mesh, y0)
    rows, ring_last = ring_room(mesh, meas)
    crit = critical_rpm(SHAFT_D, BEARING_SPAN, default_overhang(), ROTOR_G)
    jets = {n: jet_check(L, az, cant) for n, az, cant in JETS}
    radial = jet_check(L, 245.0, 0.0, y=634.0)  # plan check: a radial ventral jet at Y 634
    sweep = {h: {n: jet_check(L, az, cant, half_deg=h)["clear"] for n, az, cant in JETS}
             for h in (8.0, 16.0)}
    joints = {y: plate_joints(mesh, L["z_axis"], float(y)) for y in (628, 630, 632, 634)}
    jmap = joints[630]
    exh = {n: exhaust_fit(mesh, L, jmap, n, az) for n, az, _ in JETS}
    pas = {n: passage_area(mesh, L, az) for n, az, _ in JETS}
    need = {n: sector_needed(mesh, L, az) for n, az, _ in JETS}
    band = ventral_clear_map(L)
    plist = aft_parts(L)
    r = {"meas": meas, "layout": L, "gap": (gap, gap_y), "ring_rows": rows,
         "ring_last": ring_last, "crit_rpm": crit, "top_rpm": top_rpm(),
         "nom_rpm": KV * V_NOM, "max_overhang_3": max_overhang(SHAFT_D),
         "max_overhang_4": max_overhang(EXT_SHAFT_D), "jets": jets, "radial": radial,
         "sweep": sweep, "joints": joints, "exhaust": exh, "passages": pas,
         "sector_needed": need, "ventral_band": band,
         "annulus": annulus_gaps(mesh, L), "web": ventral_web_mm(L),
         "blockage": scoop_blockage(L), "parts": plist, "cg": cg_shift(plist)}
    r["limits"] = limits(r)
    return r


def limits(r) -> list[tuple[str, float, str, float, str]]:
    """THE limits list: (name, value, comparison, limit, unit)."""
    L = r["layout"]
    out: list[tuple[str, float, str, float, str]] = [
        ("nozzle exit station found", 0.0 if L["exit_y"] is None else 1.0, ">=", 1.0, ""),
        ("radial gap, shroud to hull", r["gap"][0], ">=", STATIC_GAP, "mm"),
        ("shroud aft end forward of the scoops", SCOOP_Y - L["shroud_y1"], ">=", 0.0, "mm"),
        ("motor clear of the stern stack", L["motor_y0"] - STERN_STACK_Y1, ">=",
         STATIC_GAP, "mm"),
        ("rotor forward of the nozzle exit", L["exit_y"] - L["rotor_y"], ">=", 0.0, "mm"),
        ("mounting ring ends where the hull still holds it",
         (r["ring_last"] or 0.0) - L["ring_y1"], ">=", 0.0, "mm"),
        ("first critical speed over the top running speed", r["crit_rpm"] / r["top_rpm"],
         ">=", CRIT_MARGIN_MIN, ""),
        ("ventral exhausts at or aft of Y 628", EXHAUST_Y - VENTRAL_MIN_Y, ">=", 0.0, "mm"),
        ("scoops at Y 628", -abs(SCOOP_Y - 628.0), ">=", 0.0, "mm"),
        ("ventral web at least the minimum printed wall", r["web"], ">=", WALL_MIN_PRINT,
         "mm"),
        ("scoop blockage of the tube", r["blockage"], "<=", BLOCKAGE_MAX, ""),
        ("port and starboard ventral jets mirror", -abs((JETS[0][1] + JETS[1][1]) - 540.0),
         ">=", 0.0, "deg"),
        ("port and starboard upper jets mirror", -abs((JETS[2][1] + JETS[3][1]) - 180.0),
         ">=", 0.0, "deg"),
    ]
    for n, (a, gmin, _) in r["passages"].items():
        out.append((f"passage area >= exhaust area, {n}", a, ">=",
                    math.pi / 4.0 * BORE ** 2, "mm2"))
    for n, j in r["jets"].items():
        out.append((f"3D jet path clear within {JET_REACH:.0f} mm, {n}",
                    float(j["blocked"]), "<=", 0.0, "rays"))
    return out


def passed(limit):
    _, v, op, lim, _ = limit
    return v >= lim if op == ">=" else v <= lim


def report(r):
    L, m = r["layout"], r["meas"]
    print("REAR CONE LAYOUT, tail EDF (plan 002 U5), frame R2, mm.  PROVISIONAL.")
    print("ASSUMED: rotor 20 g; lip 8 mm; rotor 12 mm aft of the lip; bearing span 20 mm, set in "
          "3 mm; rotor CG 5 mm out; steel shaft E 200 GPa; tube wall 1.6 mm; exhaust at Y 632, "
          "10 mm long; jet half-angle 12 deg; scoop lip 3.5 mm.")
    print(f"  thrust axis Z {m['z_axis']:.1f}; nozzle exit plane Y {L['exit_y']:.0f}; skid "
          f"crossbar aft face Y {m['crossbar_aft_y']}")
    print(f"  shroud (QX, {QX_LIP_OD:.0f} mm lip / {QX_BODY_OD} mm body, {QX_SHROUD_L:.0f} mm) "
          f"Y {L['shroud_y0']:.0f}..{L['shroud_y1']:.0f}; min gap {r['gap'][0]:.1f} mm "
          f"({r['gap'][0] / 25.4:.2f} in) at Y {r['gap'][1]:.0f}")
    print(f"  rotor plane Y {L['rotor_y']:.0f}; motor (pusher, ahead) Y {L['motor_y0']:.0f}.."
          f"{L['motor_face_y']:.0f}; ring Y {L['ring_y0']:.0f}..{L['ring_y1']:.0f}; tube Y "
          f"{L['tube_y0']:.0f}..{L['tube_y1']:.0f}")
    print("  room outside the mounting ring (OD 82.6 mm): " + ", ".join(
        f"Y {y:.0f} {room:+.1f}" for y, room in r["ring_rows"]) +
        f" mm; last station with room Y {r['ring_last']}")
    print(f"  first critical speed {r['crit_rpm']:,.0f} rpm, rotor on the 3 mm motor shaft, "
          f"overhang {default_overhang():.0f} mm; top speed {r['top_rpm']:,.0f} rpm "
          f"(unloaded, 25.2 V; {r['nom_rpm']:,.0f} at 22.2 V); margin "
          f"{r['crit_rpm'] / r['top_rpm']:.2f}")
    print(f"  longest overhang for margin {CRIT_MARGIN_MIN}: 3 mm shaft "
          f"{r['max_overhang_3']:.1f} mm; separate 4 mm shaft {r['max_overhang_4']:.1f} mm. "
          "Default: rotor on the motor shaft (owner decides at G1).")
    print("  plate joints (outer-radius grooves), deg: " + "; ".join(
        f"Y {y}: {', '.join(f'{a:.0f}' for a in js)}" for y, js in r["joints"].items()))
    print("  RCS jets (scoops Y 628, exhausts Y 632):")
    for n, j in r["jets"].items():
        e = r["exhaust"][n]
        pa, gmin, gmax = r["passages"][n]
        sh = ", ".join(f"edge {s[0]:.0f} -> joint {s[1]:.0f} ({s[3]:.1f} mm)"
                       for s in e["shifts"])
        print(f"    {n}: {'CLEAR' if j['clear'] else 'BLOCKED'} ({j['blocked']}/{j['rays']} "
              f"rays; nearest {j['nearest']}); passage {pa:.0f} mm2 (gap {gmin:.1f}-"
              f"{gmax:.1f} mm) vs exhaust {e['area_mm2']:.0f} mm2; exhaust {e['width_mm']:.1f} "
              f"mm wide; {sh}")
    rd = r["radial"]
    print(f"  plan check, radial ventral jet at Y 634: {'CLEAR' if rd['clear'] else 'BLOCKED'} "
          f"({rd['blocked']}/{rd['rays']} rays; nearest {rd['nearest']})")
    print("  half-angle sweep (clear?): " + "; ".join(
        f"{h:.0f} deg: " + ", ".join(f"{n} {'Y' if ok else 'N'}" for n, ok in s.items())
        for h, s in r["sweep"].items()))
    print("  tube-to-skin gap by station (mm): " + "; ".join(
        f"{n}: " + ", ".join(f"Y{y:.0f} {g:.1f}" for y, g in gs.items())
        for n, gs in r["annulus"].items()))
    print("  passage sector needed for the exhaust area (deg, now 45): " + ", ".join(
        f"{n} {v:.0f}" for n, v in r["sector_needed"].items()))
    print("  ventral exhaust map, 245 side (295 mirrors), 25 deg cant: Y by azimuth -> clear "
          f"or the obstacle (crossbar aft face Y {r['meas']['crossbar_aft_y']}; skid pods X "
          "+-34 to 56)")
    for y in VENTRAL_MAP_Y:
        cells = []
        for az in VENTRAL_MAP_AZ:
            hit = r["ventral_band"][(y, az)]
            what = classify_hit(hit)
            cells.append(f"{az:.0f} {what}")
        print(f"    Y {y:.0f}: " + ", ".join(cells))
    print(f"  ventral web {r['web']:.1f} mm; scoop blockage {r['blockage']:.1%}")
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", help="write the evaluation to this JSON file")
    args = ap.parse_args(argv)
    r = evaluate()
    ok = report(r)
    if args.json:
        dump = {k: v for k, v in r.items() if k not in ("meas",)}
        dump["limits"] = [list(x) + [passed(x)] for x in r["limits"]]
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(dump, f, indent=1, default=str)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
