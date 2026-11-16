#!/usr/bin/env python3
"""rear_cone_layout_fit.py -- gate G1 layout of the fuselage cooling fan and the tail EDF
provisions in the rear cone of the Rev U one-piece aft hull (issue #290, WBS COOL-01).

Plan: docs/plans/2026-11-15-001-feat-fuselage-cooling-plan.md, unit U3.

What it does
  1. MEASURES the rear cone on the published merged aft hull: the thrust axis, the largest
     circle the cavity holds at each station, and the last station where the fixed
     elliptical nozzle still fits inside the tail skin.
  2. PLACES every envelope of the proposal from those measurements: nozzle exit, EDF unit
     (XFly Galaxy X5 motor, custom 2.165 in (55 mm) rotor, owner 2026-11-15), mounting
     ring, spider, thrust tube, Delta cooling fan and adapter, baffle station, intakes,
     RCS jets.
  3. CHECKS the proposal: radial clearance along the EDF, stern-stack gap, RCS jet
     impingement for each candidate pattern, intake and RCS bore sizing against a stated
     bounding EDF flow (plan R21), and the estimated mass and CG shift (plan KD11).
  4. Prints one table.  ONE limits list drives the printout and the exit code.

Nothing here cuts or writes a mesh.  It is the proposal the owner decides at gate G1.

ASSUMED inputs are labelled.  Any PASS that rests on one is PROVISIONAL.
  * The custom rotor and its shroud are not drawn.  The X5 50 mm unit's length and motor
    come from the vendor listing [REF-EDF-002]; thrust from the maker's page
    [REF-EDF-001].  Scaling them to a 55 mm rotor is ASSUMED.
  * EDF flow is from static momentum theory, T = rho * A_e * V_e^2 (computed here).
  * The intake-area ratio, the RCS bleed fraction and the free-jet spread angle are ASSUMED
    design values.

Run:
    /usr/bin/python3 tools/rear_cone_layout_fit.py [--json OUT.json]
Needs trimesh, shapely, rtree and numpy.  The aft hull is read from its tarball.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-15, per
         AGENTS.md section 3 AI attribution.
License: CERN-OHL-W-2.0 -- see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import argparse
import io
import json
import math
import os
import sys
import tarfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import hull_datums as hd  # noqa: E402
import sls_materials as sls  # noqa: E402

AFT_HULL = os.path.join(REPO, "airframe", "stls", "fuselage",
                        "middle_rear_shell24_2mm_merged.stl")
LEDGER = os.path.join(REPO, "current-specification", "auw_ledger.json")
ZONE = os.path.join(REPO, "avionics", "kicad", "NoNFO-Pilot-PB2", "zone_contract.json")

# --- fixed by the owner or by a repo document ---------------------------------------
NOZZLE_A, NOZZLE_B = 52.3, 44.7  # mm, fixed elliptical exit, wide x tall (AGENTS.md sec 1)
ROTOR_D = 55.0  # mm, custom rotor (owner 2026-11-15, plan KD8)
STERN_STACK_Y1 = 500.0  # aft face of the stern stack (tools/middle_layout_fit.py SIMON_Y1)
STATIC_GAP = 2.0  # mm, static part to fixed hull (cargo_layout_fit convention)
T_X5_GF = 1240.0  # gf, X5 50 mm combo maximum thrust [REF-EDF-001]
X5_UNIT_L = 76.0  # mm, X5 overall length including the motor [REF-EDF-002]
X5_SHROUD_L = 38.6  # mm, X5 shroud length [REF-EDF-002]
X5_TIP_GAP = 0.4  # mm, blade tip to shell [REF-EDF-002]
X5_MASS_G = 75.0  # g, X5 combo: EDF, lip and motor [REF-EDF-001]
FAN_FRAME, FAN_DEPTH = 25.0, 10.0  # mm, Delta ASB02505SHA-AY6B [REF-FAN-001, requires verification]
FAN_G = 5.6  # g [REF-FAN-001, requires verification]
FAN_W, FAN_V = 0.60, 5.0  # rated W and V [REF-FAN-001, requires verification]

# --- SLS walls, docs/SLS_MIN_WALL_THICKNESS.md (print orientation not yet stated) --------
WALL_LOAD = 2.8  # mm, load-bearing, free-standing, any orientation
WALL_DEFAULT = 2.0  # mm, category not stated
WALL_FLOOR = 1.5  # mm, non-load-bearing membrane (covers and caps, plan KTD3)

# --- ASSUMED design values (owner to confirm at G1) ------------------------------------
HUB_D = 28.0  # mm, rotor hub over the 2627 motor -- ASSUMED
MOTOR_TAIL_GAP = 4.0  # mm, motor tail to the exit plane -- ASSUMED
RING_L = 10.0  # mm, axial length of the hull-fused mounting ring -- ASSUMED
K_INTAKE = 1.20  # intake throat area / fan swept area -- ASSUMED design ratio
BLEED = 0.15  # RCS bleed fraction of EDF flow (deferred/WBS.md Phase 11: "~15 %")
JETS_OPEN = 2  # jets open at once at full bleed (one pitch, one yaw) -- ASSUMED
RCS_BORE = 12.0  # mm, proposed RCS pipe bore
INTAKE_N, INTAKE_W, INTAKE_L = 4, 24.0, 30.0  # count, width (around), length (along Y), mm
INTAKE_Y0 = 520.0  # forward edge of the intakes; aft of the baffle station
INTAKE_AZ = (45.0, 135.0, -15.0, 195.0)  # deg from +X (port), counter-clockwise seen from aft
BAFFLE_GAP = 5.0  # mm, baffle station aft of the stern stack -- ASSUMED
RHO_AIR = 1.225  # kg/m^3, sea-level standard
A_SOUND = 340.3  # m/s, sea-level standard
JET_REACH = 150.0  # mm, an RCS jet shall meet no structure within this distance of the skin
JET_SKIP = 6.0  # mm beyond the skin left out of the check: local ribs and skin relief
JET_HALF_ANGLE = 12.0  # deg, free-jet spread half angle -- ASSUMED
SKIN_MAX = 6.0  # mm; a thicker "skin" on the jet line means the jet would cross structure
STUB_MAX = 30.0  # mm, longest RCS stub from the tube wall to the skin -- ASSUMED
MIN_SKIN_T = 0.5  # mm, a ray segment thinner than this is a mesh sliver, not structure

# RCS patterns offered at G1: azimuths in deg from +X (port), counter-clockwise seen from aft.
RCS_PATTERNS = {
    "A plus (dorsal, port, ventral, stbd)": (90.0, 180.0, 270.0, 0.0),
    "B X (45 deg)": (45.0, 135.0, 225.0, 315.0),
    "C splayed X (upper 45, lower 75)": (45.0, 135.0, 255.0, 285.0),
    "D upper 45, lower 30 below horizontal": (45.0, 135.0, 210.0, 330.0),
}
RCS_RECOMMENDED = "D upper 45, lower 30 below horizontal"
RCS_Y_TOL = 8.0  # mm, the recommended pattern shall stay clear over this fore-and-aft band

_MESH = {}


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
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    sec = mesh.section(plane_origin=[0.0, y, 0.0], plane_normal=[0.0, 1.0, 0.0])
    if sec is None:
        return Polygon()
    p, T = sec.to_2D()
    out = []

    def world(coords):
        a = np.array(coords)
        w = (T @ np.c_[a, np.zeros(len(a)), np.ones(len(a))].T).T
        return np.c_[w[:, 0], w[:, 2]]

    for q in p.polygons_full:
        out.append(Polygon(world(q.exterior.coords),
                           [world(r.coords) for r in q.interiors]).buffer(0))
    return unary_union(out)


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
    parts = list(air.geoms) if hasattr(air, "geoms") else [air]
    pt = Point(hd.X_CL, z_axis)
    for g in parts:
        if g.contains(pt):
            return not g.intersects(frame.exterior)
    return False


def ellipse(z_axis, a, b):
    from shapely import affinity
    from shapely.geometry import Point
    return affinity.scale(Point(hd.X_CL, z_axis).buffer(1.0, 64), a / 2.0, b / 2.0)


def measure(mesh=None):
    """Axis, inscribed diameters and the nozzle exit station, from the mesh."""
    from shapely.geometry import Point
    mesh = mesh or load_aft_hull()
    stations = {}
    for y in range(500, 671, 5):
        s = section_solid(mesh, float(y))
        d, zc = inscribed(s)
        stations[y] = {"dia": d, "zc": zc, "closed": cavity_closed(s, zc) if zc else False}
    # thrust axis: the tail is a body of revolution about it; take the mean centre over
    # the aft bulb, where the section is closest to a circle
    zs = [stations[y]["zc"] for y in (620, 625, 630, 635, 640, 645) if stations[y]["zc"]]
    z_axis = float(np.mean(zs))
    # exit plane: the last station where the nozzle plus a default wall sits inside the
    # outline of the tail skin around the axis
    exit_y = None
    grown = ellipse(z_axis, NOZZLE_A + 2 * WALL_DEFAULT, NOZZLE_B + 2 * WALL_DEFAULT)
    disc = Point(hd.X_CL, z_axis).buffer(45.0)
    for y in np.arange(640.0, 672.0, 1.0):
        s = section_solid(mesh, float(y)).intersection(disc)
        if s.is_empty:
            break
        if s.convex_hull.contains(grown):
            exit_y = float(y)
    return {"stations": stations, "z_axis": z_axis, "exit_y": exit_y}


def layout(meas):
    """Every envelope of the proposal, derived from the measured stations."""
    exit_y = meas["exit_y"]
    edf_y0 = exit_y - MOTOR_TAIL_GAP - X5_UNIT_L
    shroud_id = ROTOR_D + 2 * X5_TIP_GAP
    shroud_od = shroud_id + 2 * WALL_DEFAULT
    return {
        "exit_y": exit_y, "z_axis": meas["z_axis"],
        "edf_y0": edf_y0, "edf_y1": edf_y0 + X5_UNIT_L,
        "shroud_y1": edf_y0 + X5_SHROUD_L, "shroud_id": shroud_id, "shroud_od": shroud_od,
        "ring_y0": edf_y0, "ring_y1": edf_y0 + RING_L,
        "ring_id": shroud_od, "ring_od": shroud_od + 2 * WALL_LOAD,
        "spider_y": edf_y0 + X5_SHROUD_L,  # motor-mount plane at the shroud aft face
        "tube_y0": edf_y0 + X5_SHROUD_L, "tube_y1": exit_y,
        "fan_y0": edf_y0, "fan_y1": edf_y0 + FAN_DEPTH,
        "baffle_y": STERN_STACK_Y1 + BAFFLE_GAP,
        "intake_y0": INTAKE_Y0, "intake_y1": INTAKE_Y0 + INTAKE_L,
        "rcs_y": edf_y0 + X5_SHROUD_L + 12.0,  # in the thrust tube, aft of the spider
    }


def min_inscribed(mesh, y0, y1, step=2.0):
    """Smallest inscribed diameter between two stations: (dia, at Y)."""
    best = (1e9, None)
    for y in np.arange(y0, y1 + 0.01, step):
        d, _ = inscribed(section_solid(mesh, float(y)))
        if d < best[0]:
            best = (d, float(y))
    return best


def jet_wedge(z_axis, az_deg, r0, r1):
    """Footprint of one RCS jet between radii r0 and r1 from the axis: the bore width at
    the skin, spreading at JET_HALF_ANGLE (ASSUMED free-jet spread)."""
    from shapely.geometry import Polygon
    a = math.radians(az_deg)
    ux, uz = math.cos(a), math.sin(a)
    nx, nz = -uz, ux

    def pt(d, off):
        return (hd.X_CL + d * ux + off * nx, z_axis + d * uz + off * nz)

    w0 = RCS_BORE / 2.0
    w1 = w0 + (r1 - r0) * math.tan(math.radians(JET_HALF_ANGLE))
    return Polygon([pt(r0, -w0), pt(r0, w0), pt(r1, w1), pt(r1, -w1)])


def jet_path(mesh, y, z_axis, az_deg, solid=None):
    """One RCS jet leaving the axis at azimuth az.  Returns the skin thickness on the jet
    line (mm) and the area of structure inside the jet footprint beyond the skin (mm^2).
    The jet is clear when the skin is thin enough to be a plain wall, the stub from the
    tube to the skin is no longer than STUB_MAX, and the footprint meets no structure
    within JET_REACH."""
    from shapely.geometry import LineString
    s = solid if solid is not None else section_solid(mesh, y)
    a = math.radians(az_deg)
    far = (hd.X_CL + 400.0 * math.cos(a), z_axis + 400.0 * math.sin(a))
    hit = LineString([(hd.X_CL, z_axis), far]).intersection(s)
    segs = list(hit.geoms) if hasattr(hit, "geoms") else [hit]
    spans = []
    for g in segs:
        if g.is_empty or g.length < MIN_SKIN_T:
            continue
        ds = [math.hypot(c[0] - hd.X_CL, c[1] - z_axis) for c in g.coords]
        spans.append((min(ds), max(ds)))
    spans.sort()
    if not spans:
        return {"az": az_deg, "skin_t": 0.0, "hit_mm2": 0.0, "r_skin": 0.0, "clear": False}
    r_in, r_out = spans[0]
    wedge = jet_wedge(z_axis, az_deg, r_out + JET_SKIP, r_out + JET_REACH)
    hit_area = wedge.intersection(s).area
    stub = r_out - (ROTOR_D / 2.0 + X5_TIP_GAP + WALL_DEFAULT)
    return {"az": az_deg, "skin_t": r_out - r_in, "hit_mm2": hit_area, "r_skin": r_out,
            "stub_mm": stub,
            "clear": (r_out - r_in) <= SKIN_MAX and hit_area < 1.0 and stub <= STUB_MAX}


def rcs_patterns(mesh, L):
    solid = section_solid(mesh, L["rcs_y"])
    return {name: [jet_path(mesh, L["rcs_y"], L["z_axis"], az, solid) for az in azs]
            for name, azs in RCS_PATTERNS.items()}


def clear_sectors(mesh, L, step=5):
    """Azimuths (deg) at the RCS station where a jet has a clear path."""
    solid = section_solid(mesh, L["rcs_y"])
    return [az for az in range(0, 360, step)
            if jet_path(mesh, L["rcs_y"], L["z_axis"], float(az), solid)["clear"]]


def sizing(L):
    """Bounding EDF flow and the areas sized to it (plan R21)."""
    a_exit = math.pi / 4.0 * NOZZLE_A * NOZZLE_B * 1e-6  # m^2
    # ASSUMED: same shaft power as the 50 mm unit; static thrust at constant power
    # scales with disc area to the 1/3 power (momentum theory)
    t_n = T_X5_GF * 9.80665e-3 * (ROTOR_D / 50.0) ** (2.0 / 3.0)
    v_exit = math.sqrt(t_n / (RHO_AIR * a_exit))
    q = v_exit * a_exit
    fsa = math.pi / 4.0 * (ROTOR_D ** 2 - HUB_D ** 2)  # mm^2
    v_fan = q / (fsa * 1e-6)
    intake_req = K_INTAKE * fsa
    intake_have = INTAKE_N * INTAKE_W * INTAKE_L
    a_bore = math.pi / 4.0 * RCS_BORE ** 2  # mm^2
    q_jet = BLEED * q / JETS_OPEN
    v_jet = q_jet / (a_bore * 1e-6)
    f_jet = RHO_AIR * q_jet * v_jet  # N, momentum flux of one open jet
    arm = (L["rcs_y"] - hd.SPAR_Y) * 1e-3
    nu = 1.46e-5  # m^2/s, air at 15 C
    return {
        "thrust_n": t_n, "q_m3s": q, "q_cfm": q * 2118.88, "v_exit": v_exit,
        "mach_exit": v_exit / A_SOUND, "re_exit": v_exit * (NOZZLE_B * 1e-3) / nu,
        "fsa_mm2": fsa, "v_fan": v_fan, "mach_fan": v_fan / A_SOUND,
        "intake_req_mm2": intake_req, "intake_have_mm2": intake_have,
        "intake_margin": intake_have / intake_req - 1.0,
        "v_intake": q / (intake_have * 1e-6), "mach_intake": q / (intake_have * 1e-6) / A_SOUND,
        "tube_area_ratio": (math.pi / 4.0 * NOZZLE_A * NOZZLE_B) / fsa,
        "rcs_bore_mm": RCS_BORE, "v_jet": v_jet, "mach_jet": v_jet / A_SOUND,
        "re_jet": v_jet * (RCS_BORE * 1e-3) / nu, "f_jet_n": f_jet,
        "m_jet_nm": f_jet * arm, "rcs_arm_mm": arm * 1e3,
    }


def _tube_g(d_mean, wall, length):
    return math.pi * d_mean * wall * length * sls.rho_g_mm3(sls.PA_CF)


def parts(L, meas):
    """Estimated mass and station of each added part: (name, g, Y, config, basis).
    config: 'both' = printed now and stays; 'fan' = fan configuration only;
    'edf' = Phase 11 only.  Volumes are envelope estimates, priced at the SLS PA CF
    solid density (tools/sls_materials.py); U9 replaces them with mesh masses."""
    rho = sls.rho_g_mm3(sls.PA_CF)
    d_hull = meas["stations"][int(5 * round(L["ring_y0"] / 5))]["dia"]
    web_len = max(0.0, (d_hull - L["ring_od"]) / 2.0)
    ring = _tube_g(L["ring_id"] + WALL_LOAD, WALL_LOAD, RING_L) \
        + 3 * web_len * WALL_LOAD * RING_L * rho
    tube = _tube_g((L["shroud_id"] + NOZZLE_A) / 2.0 + WALL_DEFAULT, WALL_DEFAULT,
                   L["tube_y1"] - L["tube_y0"])
    lip = 2 * (INTAKE_W + INTAKE_L) * 12.0 * WALL_DEFAULT * rho  # 12 mm deep throat wall
    stub = math.pi / 4.0 * ((RCS_BORE + 2 * WALL_DEFAULT) ** 2 - RCS_BORE ** 2) * 12.0 * rho
    pad = 20.0 * 12.0 * 3.0 * rho  # valve and servo mount pad, each
    adapter = (math.pi / 4.0 * L["ring_id"] ** 2 - FAN_FRAME ** 2) * WALL_DEFAULT * rho \
        + 4 * FAN_FRAME * FAN_DEPTH * WALL_FLOOR * rho
    d_baffle = meas["stations"][505]["dia"]
    baffle = math.pi / 4.0 * d_baffle ** 2 * WALL_DEFAULT * rho
    shroud = _tube_g(L["shroud_id"] + WALL_DEFAULT, WALL_DEFAULT, X5_SHROUD_L)
    ymid = (L["tube_y0"] + L["tube_y1"]) / 2.0
    return [
        ("mounting ring + 3 webs (fused)", ring, L["ring_y0"] + RING_L / 2, "both", "envelope"),
        ("thrust tube + nozzle (fused)", tube, ymid, "both", "envelope"),
        ("4 intake throats + covers (fused)", INTAKE_N * lip, L["intake_y0"] + INTAKE_L / 2,
         "both", "envelope; cover replaces skin"),
        ("4 RCS stubs + caps (fused)", 4 * stub, L["rcs_y"], "both", "envelope"),
        ("4 valve + servo pads (fused)", 4 * pad, L["rcs_y"] - 15.0, "both", "envelope"),
        ("spider mount (bolted)", 10.0, L["spider_y"], "both", "ASSUMED 10 g"),
        ("fan adapter (removable)", adapter, L["fan_y0"] + 5.0, "fan", "envelope"),
        ("Delta fan", FAN_G, L["fan_y0"] + 5.0, "fan", "REF-FAN-001, requires verification"),
        ("fan lead + connector", 3.0, (STERN_STACK_Y1 + L["fan_y0"]) / 2, "fan", "ASSUMED 3 g"),
        ("X5 motor + custom rotor", X5_MASS_G, L["edf_y0"] + 30.0, "edf",
         "REF-EDF-001 combo mass, ASSUMED for the custom unit"),
        ("EDF shroud", shroud, L["edf_y0"] + X5_SHROUD_L / 2, "edf", "envelope"),
        ("baffled insert", baffle, L["baffle_y"], "edf", "envelope"),
        ("ESC 50 A", 35.0, L["baffle_y"] + 20.0, "edf", "BOM ESC-50A-6S"),
        ("4 RCS valves + servos", 4 * 12.0, L["rcs_y"] - 15.0, "edf", "ASSUMED 12 g each"),
        ("GW-RCS board", 10.0, L["baffle_y"] + 20.0, "edf", "ASSUMED 10 g"),
    ]


def cg_estimate(plist):
    """CG shift of the hover configuration for the fan and the EDF configurations."""
    with open(LEDGER) as f:
        hov = json.load(f)["configs"]["hover_4000"]
    m0, y0 = hov["mass_g"], hov["cg"][1]
    out = {"m0_g": m0, "y0": y0, "pivot_y": hd.SPAR_Y, "aft_of_pivot0": y0 - hd.SPAR_Y}
    for cfg in ("fan", "edf"):
        sel = [p for p in plist if p[3] in ("both", cfg)]
        dm = sum(p[1] for p in sel)
        mom = sum(p[1] * (p[2] - y0) for p in sel)
        dy = mom / (m0 + dm)
        out[cfg] = {"dm_g": dm, "dy_mm": dy, "aft_of_pivot": y0 + dy - hd.SPAR_Y,
                    "moment_gmm": mom}
    return out


def electrical():
    """Fan load against the stern stack's 5 V fan line (plan R20)."""
    with open(ZONE) as f:
        z = json.load(f)
    budget = z["power_5v"]["fan"]["a_peak"]
    return {"fan_a": FAN_W / FAN_V, "budget_a": budget,
            "budget_basis": z["power_5v"]["fan"]["basis"]}


def evaluate():
    mesh = load_aft_hull()
    meas = measure(mesh)
    L = layout(meas)
    d_min, y_min = min_inscribed(mesh, L["edf_y0"], L["shroud_y1"])
    tube_min, tube_y = min_inscribed(mesh, L["tube_y0"], L["tube_y1"] - 2.0)
    pats = rcs_patterns(mesh, L)
    sz = sizing(L)
    pl = parts(L, meas)
    cg = cg_estimate(pl)
    el = electrical()
    rec = pats[RCS_RECOMMENDED]
    band = [jet_path(mesh, L["rcs_y"] + dy, L["z_axis"], az)["clear"]
            for dy in (-RCS_Y_TOL, 0.0, RCS_Y_TOL) for az in RCS_PATTERNS[RCS_RECOMMENDED]]
    band_clear = sum(band)
    sectors = clear_sectors(mesh, L)
    # ONE limits list: (name, value, comparison, limit, unit)
    limits = [
        ("nozzle exit station found", 0.0 if L["exit_y"] is None else 1.0, ">=", 1.0, ""),
        ("radial clearance, shroud to hull", (d_min - L["shroud_od"]) / 2.0, ">=",
         STATIC_GAP, "mm"),
        ("ring web length (ring must stand off the skin)",
         (meas["stations"][int(5 * round(L["ring_y0"] / 5))]["dia"] - L["ring_od"]) / 2.0,
         ">=", 0.0, "mm"),
        ("EDF front face aft of the intakes", L["edf_y0"] - L["intake_y1"], ">=", 0.0, "mm"),
        ("intakes aft of the baffle station", L["intake_y0"] - L["baffle_y"], ">=",
         STATIC_GAP, "mm"),
        ("baffle clear of the stern stack", L["baffle_y"] - STERN_STACK_Y1, ">=",
         STATIC_GAP, "mm"),
        ("motor tail inside the exit plane", L["exit_y"] - L["edf_y1"], ">=", 0.0, "mm"),
        ("intake area margin over the bounding flow", sz["intake_margin"], ">=", 0.0, ""),
        ("Mach number in an open RCS jet", sz["mach_jet"], "<=", 0.5, ""),
        ("Mach number at the nozzle exit", sz["mach_exit"], "<=", 0.5, ""),
        ("recommended RCS pattern: jets with a clear path",
         float(sum(r["clear"] for r in rec)), ">=", 4.0, "of 4"),
        ("recommended RCS pattern: clear paths over the station band", float(band_clear),
         ">=", float(len(band)), "of %d" % len(band)),
        ("fan current within the stern stack 5 V fan line", el["fan_a"], "<=",
         el["budget_a"], "A"),
    ]
    return {"meas": meas, "layout": L, "d_min": (d_min, y_min), "tube_min": (tube_min, tube_y),
            "patterns": pats, "sectors": sectors, "sizing": sz, "parts": pl, "cg": cg,
            "electrical": el,
            "limits": limits}


def passed(limit):
    _, v, op, lim, _ = limit
    return v >= lim if op == ">=" else v <= lim


def report(r):
    L, m, sz, cg = r["layout"], r["meas"], r["sizing"], r["cg"]
    print("REAR CONE LAYOUT, gate G1 (frame R2, mm).  PROVISIONAL: see ASSUMED inputs.")
    print(f"  thrust axis Z {m['z_axis']:.1f}; nozzle exit plane Y {L['exit_y']:.0f}")
    print("  largest circle on the centreline, by station:")
    for y in (500, 520, 540, 560, 580, 600, 620, 640, 650, 660):
        s = m["stations"][y]
        print(f"    Y {y}: {s['dia']:6.1f} mm ({s['dia'] / 25.4:.2f} in)"
              f"{'' if s['closed'] else '   [section not closed]'}")
    print(f"  EDF unit Y {L['edf_y0']:.1f}..{L['edf_y1']:.1f}; shroud OD {L['shroud_od']:.1f}; "
          f"ring Y {L['ring_y0']:.1f}..{L['ring_y1']:.1f}; tube Y {L['tube_y0']:.1f}.."
          f"{L['tube_y1']:.1f}")
    print(f"  baffle Y {L['baffle_y']:.0f}; intakes Y {L['intake_y0']:.0f}..{L['intake_y1']:.0f} "
          f"at {INTAKE_AZ} deg; RCS station Y {L['rcs_y']:.1f}")
    print(f"  bounding EDF flow {sz['q_cfm']:.0f} cfm ({sz['q_m3s']:.3f} m^3/s), thrust "
          f"{sz['thrust_n'] / 4.44822:.2f} lbf ({sz['thrust_n']:.1f} N) -- ASSUMED scaling")
    print(f"  intake area {sz['intake_have_mm2']:.0f} mm^2 vs {sz['intake_req_mm2']:.0f} required "
          f"(margin {sz['intake_margin'] * 100:.0f} %)")
    print(f"  RCS bore {RCS_BORE:.0f} mm: jet {sz['v_jet']:.0f} m/s, M {sz['mach_jet']:.2f}, "
          f"{sz['f_jet_n']:.2f} N at arm {sz['rcs_arm_mm']:.0f} mm = {sz['m_jet_nm']:.2f} N-m")
    print("  RCS patterns (jet path clear of structure beyond the skin):")
    for name, rows in r["patterns"].items():
        txt = ", ".join(f"{x['az']:.0f} deg {'clear' if x['clear'] else 'BLOCKED'}" for x in rows)
        print(f"    {name}: {txt}")
    print(f"    clear azimuths at the RCS station (deg): {r['sectors']}")
    print(f"  hover CG now Y {cg['y0']:.1f}, {cg['aft_of_pivot0']:.1f} mm aft of the pivot "
          f"(Y {cg['pivot_y']:.1f})")
    for cfg in ("fan", "edf"):
        c = cg[cfg]
        print(f"    {cfg} configuration: +{c['dm_g']:.0f} g ({c['dm_g'] / 453.592:.2f} lbm), CG "
              f"{c['dy_mm']:+.1f} mm, then {c['aft_of_pivot']:.1f} mm aft of the pivot")
    print("\n  check | value | limit | result")
    ok = True
    for lim in r["limits"]:
        name, v, op, limv, unit = lim
        good = passed(lim)
        ok = ok and good
        print(f"  {name}: {v:.2f} {op} {limv:.2f} {unit}  {'PASS' if good else 'FAIL'}")
    print("\nRESULT:", "PASS -- PROVISIONAL" if ok else "FAIL -- owner decision needed (G1 brief)")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", help="write the evaluation to this JSON file")
    args = ap.parse_args()
    r = evaluate()
    ok = report(r)
    if args.json:
        dump = {k: v for k, v in r.items()}
        stations = {str(k): v for k, v in r["meas"]["stations"].items()}
        dump["meas"] = {**r["meas"], "stations": stations}
        dump["limits"] = [list(x) + [passed(x)] for x in r["limits"]]
        with open(args.json, "w") as f:
            json.dump(dump, f, indent=1, default=float)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
