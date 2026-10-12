#!/usr/bin/python3
"""Two-row energy-absorber wire layout pre-filter (BHD-02g / BHD-02k).

The Rev R6 absorber puts 4 wires (2 ductile O4.26, 2 spring O3.59; sized by
tools/landing_gear_r6_sizing.py) in ONE row of thigh sockets at 3.5 mm pitch
on a 6 mm crank.  That cannot be built: the wires are thicker than the
pitch, and four O4.9 socket bores need 19.6 mm across a 14 mm lug.  The fix
is two rows of two -- a ductile row and a spring row, each at its own crank
azimuth, 6 mm in-row pitch (y +/-3) -- keeping r = 6 and a 90 deg crank-to-
chord transmission angle per wire, so per-wire mechanics and the sizing are
unchanged.  The chord of a row at crank azimuth t points t + 90 (flexion
turns the thigh counter-clockwise in XZ, so the socket moves along t + 90 and
the chord SHORTENS -- compression, the wire bows).

This tool screens (t_D, t_S) in the swing plane (leg-local XZ, hip at the
origin) before any 3-D render, with the geometry restated from
airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad:

  1. each socket bore + 1 mm wall lies inside the thigh root (convex hull of
     the O9 hub and the two O14 lug spheres, leg_frame()) -- OR, with HORNS,
     on a crank horn (local boss) that clears the stop pin over the flex;
  2. the two rows' bores are >= 1 mm apart;
  3. each wire's swept band -- straight chord plus a swing-plane bow of up to
     H_DEF (5.70 ductile / 4.38 spring) on the radially-outward side, plus
     the wire radius and 0.5 mm -- clears the OTHER row's socket bore, the
     extension-stop cross-pin (O3.2 at 8 / STOP_PIN_AZ) and the thigh's stop
     tab (sector STOP_TAB_AZ1..2, r 3..10) at rest and at full flex;
  4. each row's boss cluster (boss mouth + O11 boss) stays out of the thigh's
     swept band (-48 deg at rest to -22 at FLEX_DEG, + 4 deg margin, twin
     O14 cylinders at +/-9 -> +/-16 mm half-width) beyond r 10.

Survivors are reported with the azimuth of each boss cluster, which is what
decides wing / hull / interior conflicts per corner (that part is the 3-D
census: tools/landing_gear_bay_function.py with -D overrides).

Run:  /usr/bin/python3 tools/lg_wire_layout_study.py [--stop AZ] [--step DEG]

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import math

import numpy as np

# --- restated from canonical_leg_r6_3_0in.scad (check against it on change) --
CRANK_R = 6.0
HUB_R = 4.5
KNEE = np.array([59.0, -66.0])
LUG_SPHERE_R, LUG_SPHERE_AT, LUG_PERP = 7.0, 14.0, 9.0      # leg_frame() root hull
STOP_PIN_R, STOP_PIN_RAD = 8.0, 1.6
STOP_TAB = (131.0, 146.0, 3.0, 10.0)
FLEX, FLEX_MARGIN = 22.0, 4.0
THIGH_HALF = 16.0          # twin O14 cylinders at +/-9 -> 16 mm half-width
BOSS_R = 5.5               # O11 wire boss
SOCK_CLR, WALL = 0.65, 1.0
ROWS = {"D": dict(d=4.26, L=40.0, seat=8.0, h=5.70),
        "S": dict(d=3.59, L=34.0, seat=5.0, h=4.38)}
END_RUN_IN = 2.0
HORNS = True               # allow a crank horn where the socket leaves the lug


def cross2(a, b) -> float:
    """z of the 2-D cross product a x b."""
    return float(a[0] * b[1] - a[1] * b[0])


def az(t):
    return np.array([math.cos(math.radians(t)), math.sin(math.radians(t))])


def lug_polygon(n=72):
    """Convex hull (2-D) of the hub circle and the two lug spheres."""
    axis = KNEE / np.linalg.norm(KNEE)
    perp = np.array([-axis[1], axis[0]])
    circles = [(np.zeros(2), HUB_R)] + [
        (LUG_SPHERE_AT * axis + s * LUG_PERP * perp, LUG_SPHERE_R) for s in (-1, 1)]
    pts = [c + r * az(360 * k / n) for c, r in circles for k in range(n)]
    pts = np.array(pts)
    # monotone-chain convex hull
    p = pts[np.lexsort((pts[:, 1], pts[:, 0]))]

    def half(seq):
        h = []
        for q in seq:
            while len(h) >= 2 and cross2(h[-1] - h[-2], q - h[-2]) <= 0:
                h.pop()
            h.append(q)
        return h
    lo, hi = half(p), half(p[::-1])
    return np.array(lo[:-1] + hi[:-1])


def inside_margin(poly, c):
    """Signed distance from c to the convex polygon edge (positive = inside)."""
    best = math.inf
    for a, b in zip(poly, np.roll(poly, -1, axis=0), strict=True):
        e = b - a
        nrm = np.array([e[1], -e[0]]) / np.linalg.norm(e)   # outward for CCW hull
        best = min(best, -float(np.dot(c - a, nrm)))
    return best


def seg_dist(p, a, b):
    ab = b - a
    t = np.clip(np.dot(p - a, ab) / np.dot(ab, ab), 0.0, 1.0)
    return float(np.linalg.norm(p - (a + t * ab)))


def wire_band(t, row, flex=0.0):
    """Chord segment (socket -> boss mouth) and the bow offset vector, at a flex."""
    r = ROWS[row]
    s = CRANK_R * az(t + flex)
    m = CRANK_R * az(t) + (r["L"] - 2 * r["seat"]) * az(t + 90)   # boss is bay-fixed
    return s, m, r


def band_clear(p, prad, t, row, flex=0.0):
    """Clearance from a circle (p, prad) to a wire's swept band (<0 = hit)."""
    s, m, r = wire_band(t, row, flex)
    u = (m - s) / np.linalg.norm(m - s)
    out = np.array([u[1], -u[0]])                  # right-hand normal ...
    if np.dot(out, s) < 0:                         # ... pointed radially outward
        out = -out
    rad = r["d"] / 2 + 0.5
    best = math.inf
    for k in np.linspace(0, 1, 9):                 # sample the bow sweep 0..h
        off = out * r["h"] * k
        best = min(best, seg_dist(p, s + off, m + off))
    return best - rad - prad


def sector_points(a1, a2, r1, r2):
    return [rr * az(aa) for aa in np.linspace(a1, a2, 7) for rr in np.linspace(r1, r2, 5)]


def evaluate(tD, tS, stop_az, poly):
    notes, ok = [], True
    rb = {k: (v["d"] + SOCK_CLR) / 2 for k, v in ROWS.items()}
    for row, t in (("D", tD), ("S", tS)):
        m = inside_margin(poly, CRANK_R * az(t)) - rb[row] - WALL
        if m < 0 and not HORNS:
            ok = False
            notes.append(f"{row} socket wall {m:+.1f}")
        elif m < 0:
            # CRANK HORN: a local boss (bore + 2 x WALL) on the hub carries the
            # socket.  It rides on the thigh, so it must clear the bay's stop
            # pin through the whole flex range (pin moves -flex relative).
            horn_r = rb[row] + WALL
            for fl in np.arange(0.0, FLEX + FLEX_MARGIN + 0.1, 2.0):
                g = np.linalg.norm(CRANK_R * az(t) - STOP_PIN_R * az(stop_az - fl)) \
                    - horn_r - STOP_PIN_RAD - 0.5
                if g < 0:
                    ok = False
                    notes.append(f"{row} horn hits stop pin at flex {fl:.0f}")
                    break
    gap = np.linalg.norm(CRANK_R * (az(tD) - az(tS))) - rb["D"] - rb["S"] - WALL
    if gap < 0:
        ok = False
        notes.append(f"socket gap {gap:+.1f}")
    pin = STOP_PIN_R * az(stop_az)
    tab = sector_points(stop_az + 13, stop_az + 28, STOP_TAB[2], STOP_TAB[3])
    worst = math.inf
    for row, t, other, to in (("D", tD, "S", tS), ("S", tS, "D", tD)):
        for fl in (0.0, FLEX + FLEX_MARGIN):
            c = [band_clear(CRANK_R * az(to + fl), rb[other], t, row, fl),
                 band_clear(pin, STOP_PIN_RAD, t, row, fl)]
            # the tab rides on the thigh: rotate it with the flex
            c += [band_clear(q @ np.array([[math.cos(math.radians(fl)), math.sin(math.radians(fl))],
                                           [-math.sin(math.radians(fl)), math.cos(math.radians(fl))]]),
                             0.0, t, row, fl) for q in tab]
            worst = min(worst, min(c))
    if worst < 0:
        ok = False
        notes.append(f"wire band clearance {worst:+.1f}")
    clusters = {}
    for row, t in (("D", tD), ("S", tS)):
        _s, m, r = wire_band(t, row)
        boss = m + (r["seat"] + 3) * az(t + 90) / 2
        a = math.degrees(math.atan2(boss[1], boss[0]))
        clusters[row] = (round(a, 1), round(float(np.linalg.norm(boss)), 1))
        for fl in np.arange(0.0, FLEX + FLEX_MARGIN + 0.1, 2.0):
            thigh_dir = az(-48.0 + fl)
            along = float(np.dot(boss, thigh_dir))
            across = abs(cross2(thigh_dir, boss))
            if along > 10 and across < THIGH_HALF + BOSS_R + 1.0:
                ok = False
                notes.append(f"{row} cluster in thigh sweep at flex {fl:.0f}")
                break
    return ok, notes, clusters, round(worst, 2)


# ---------------------------------------------------------------------------
# v2 screen (2026-10-11): real 2-D shapes.  The v1 cluster test modelled only
# the O11 boss against the thigh beyond r 10; in 3-D the 16 x 12 carrier slab
# of a "straight-down" row sat in the root lug's lower sphere (247 mm^3,
# census of D -175 / S 30).  v2 uses shapely polygons for the thigh outline
# swept 0..26 deg, each row's carrier rectangle and bosses, the wire bands
# with their bow, the crank horns swept with the thigh, and the stop pin.
# ---------------------------------------------------------------------------
CARRIER_H, CARRIER_T = 16.0, 12.0          # BAY_CARRIER_H (perp to chord), _T (along)
MARGIN = 1.0                               # mm, clearance demanded of every pair
HW_THIGH_SLACK = 2.5                       # mm^2 of projected overlap left to the 3-D census
_SWEPT_THIGH = []


def _unary(parts):
    return _shapely()[4](parts)


def _swept_thigh():
    if not _SWEPT_THIGH:
        _SWEPT_THIGH.append(swept(thigh_shape()))
    return _SWEPT_THIGH[0]


def _shapely():
    from shapely import affinity  # noqa: PLC0415
    from shapely.geometry import LineString, Point, Polygon  # noqa: PLC0415
    from shapely.ops import unary_union  # noqa: PLC0415
    return affinity, LineString, Point, Polygon, unary_union


_THIGH = []


def thigh_shape():
    """Cached for the run (see _thigh_shape_load)."""
    if not _THIGH:
        _THIGH.append(_thigh_shape_load())
    return _THIGH[0]


def _thigh_shape_load():
    """The thigh's XZ outline near the hip: the REAL rendered leg_frame() mesh
    projected onto the swing plane (r < 55), cached.  The hand-rebuilt outline
    below (thigh_shape_model) over-reported by ~2 mm at the upper cylinder
    (z 5.55 modelled vs 3.39 rendered, 2026-10-11), enough to reject the Rev R6
    row the 3-D census clears -- so the screen projects the real part."""
    import json  # noqa: PLC0415
    import os  # noqa: PLC0415
    import sys  # noqa: PLC0415
    from shapely import wkt  # noqa: PLC0415
    from shapely.geometry import Polygon  # noqa: PLC0415
    from shapely.ops import unary_union  # noqa: PLC0415
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    import landing_gear_bay_function as lgbf  # noqa: PLC0415
    import trimesh  # noqa: PLC0415
    defs = ("CRANK_AZ_D=-22", "CRANK_AZ_S=-22")
    path = lgbf.render(lgbf.SCAD, "aft", "leg (thigh+shin+foot)",
                       lgbf.FEATURES["leg (thigh+shin+foot)"][0], defs)
    cache = path + ".xz55v2.json"
    if os.path.exists(cache):
        return wkt.loads(json.load(open(cache, encoding="utf-8"))["wkt"])
    m = trimesh.load(path, force="mesh")
    v = m.vertices[:, [0, 2]]
    keep = np.any(np.linalg.norm(v[m.faces], axis=2) < 60.0, axis=1)   # clip, don't drop
    tris = [Polygon(v[f]) for f in m.faces[keep]]
    shp = unary_union([t for t in tris if t.area > 1e-9]).buffer(0)
    shp = shp.intersection(Polygon([(55 * math.cos(math.radians(a)), 55 * math.sin(math.radians(a)))
                                    for a in range(0, 360, 5)]))
    json.dump({"wkt": shp.wkt}, open(cache, "w", encoding="utf-8"))
    return shp


def thigh_shape_model():
    """Hand-rebuilt XZ outline (superseded by the mesh projection; kept for
    reference -- see thigh_shape())."""
    _a, LineString, Point, Polygon, unary_union = _shapely()
    axis = KNEE / np.linalg.norm(KNEE)
    perp = np.array([-axis[1], axis[0]])
    parts = [Polygon(lug_polygon()).buffer(0)]
    for sgn in (-1, 1):                    # twin main cylinders, O14
        parts.append(LineString([10 * axis + sgn * 9 * perp,
                                 KNEE + sgn * 9 * perp - 6 * axis]).buffer(7.0))
    parts.append(Polygon([12 * axis + 9 * perp, KNEE - 8 * axis + 9 * perp,
                          KNEE - 8 * axis - 9 * perp, 12 * axis - 9 * perp]))   # web
    parts.append(LineString([12 * axis + 10 * perp, KNEE - 24 * axis + 10 * perp]).buffer(2.5))
    parts.append(LineString([14 * axis - 9 * perp, KNEE - 26 * axis - 9 * perp]).buffer(2.0))
    parts.append(LineString([16 * axis + 12.5 * perp, KNEE - 20 * axis + 12.5 * perp]).buffer(1.1))
    tab = [rr * az(aa) for aa in np.linspace(STOP_TAB[0], STOP_TAB[1], 8)
           for rr in (STOP_TAB[2], STOP_TAB[3])]
    parts.append(Polygon(tab).convex_hull)
    return unary_union(parts).intersection(Point(0, 0).buffer(55.0))


def horn_shape(t, row):
    """Crank horn: hub + the WHOLE socket bore (mouth back `seat` along -chord),
    1.5 mm wall.  v2 first drew only the mouth circle; the bore's far end then
    left the part and, at crank 165, the seated wire end ran through the stop
    pin (42.5 mm^3 in the 3-D census, 2026-10-11)."""
    _a, _L, Point, _P, unary_union = _shapely()
    rb = (ROWS[row]["d"] + SOCK_CLR) / 2 + 1.5
    s0 = CRANK_R * az(t)
    s1 = s0 - ROWS[row]["seat"] * az(t + 90)
    return unary_union([Point(0, 0).buffer(HUB_R), Point(*s0).buffer(rb),
                        Point(*s1).buffer(rb)]).convex_hull


def swept(shape, a0=0.0, a1=FLEX + FLEX_MARGIN, step=2.0):
    affinity, _L, _Pt, _P, unary_union = _shapely()
    return unary_union([affinity.rotate(shape, a, origin=(0, 0))
                        for a in np.arange(a0, a1 + 1e-9, step)])


_PARTS = {}


def row_hardware(t, row):
    """(carrier+bosses polygon, wire band polygon) of a row at crank t, rest pose."""
    _a, LineString, _Pt, Polygon, unary_union = _shapely()
    r = ROWS[row]
    u = az(t + 90)
    out = az(t)
    s = CRANK_R * az(t)
    m = s + (r["L"] - 2 * r["seat"]) * u
    cc = m + ((r["seat"] + 3) / 2 - CARRIER_T / 4) * u
    car = Polygon([cc + a * u * CARRIER_T / 2 + b * out * CARRIER_H / 2
                   for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    boss = LineString([m - CARRIER_T / 2 * u, m + (r["seat"] + 3) * u]).buffer(BOSS_R)
    hard = unary_union([car, boss])
    _PARTS[(round(float(t), 3), row)] = (car, boss)
    # wire band: chord from socket to mouth, bowed outward up to h, + radius
    bands = [LineString([s + out * r["h"] * k, m + out * r["h"] * k]) for k in np.linspace(0, 1, 6)]
    # + the seated ends: the wire runs `seat` past each mouth, into the thigh
    # socket and into the boss bore
    bands += [LineString([s - r["seat"] * u, s]), LineString([m, m + r["seat"] * u])]
    band = unary_union([b.buffer(r["d"] / 2 + 0.5) for b in bands])
    return hard, band, s


def _tab_polygon(stop_az):
    """The thigh's extension-stop tab sector (stop + 13..28 deg, r 3..10)."""
    _a, _L, _Pt, Polygon, _u = _shapely()
    pts = [rr * az(aa) for aa in np.linspace(stop_az + 13, stop_az + 28, 8) for rr in (3.0, 10.0)]
    return Polygon(pts).convex_hull


def ear_shape(stop_az, back_x=0.0):
    """Clevis ear XZ outline (bay_clevis_ears): hull of the O14 hub boss, the
    O7.2 stop-pin boss and the 2 x 24 back block at BAY_BACK_X + 1.  The ears
    sit at |y| 7.5..10.5, clear of the thigh and wires in Y.  NOT a constraint
    on the row carriers: ears and carriers are the same printed bay part, so
    where they meet they simply union (kept for drawing / reference)."""
    _a, _L, Point, Polygon, unary_union = _shapely()
    blk = Polygon([(back_x + 1, -9), (back_x + 3, -9), (back_x + 3, 15), (back_x + 1, 15)])
    return unary_union([Point(0, 0).buffer(7.0), Point(*(STOP_PIN_R * az(stop_az))).buffer(3.6),
                        blk]).convex_hull


_OBST = {}


def station_obstacles(station: str, half_y: float = 15.0):
    """Swing-plane keep-out for a bay STATION: every cargo-context solid except
    the hull shell and the gear, cut to the bay's |y| <= 15 slab in the leg-
    local frame of BOTH corners of the station, projected onto XZ and unioned.
    (The shell is left to the 3-D census: a small pocket there is a hull edit,
    not a show-stopper.)  Cached per station for the run."""
    key = (station, half_y)
    if key in _OBST:
        return _OBST[key]
    import os  # noqa: PLC0415
    import sys  # noqa: PLC0415
    from shapely.geometry import Polygon  # noqa: PLC0415
    from shapely.ops import unary_union  # noqa: PLC0415
    from manifold3d import Manifold  # noqa: PLC0415
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    import cargo_bulkhead_context as cbc  # noqa: PLC0415
    import landing_gear_bay_function as lgbf  # noqa: PLC0415
    P = cbc.build()
    corners = lgbf.parse_corners(lgbf.SCAD)
    # slab = the widest bay hardware in Y: the row carrier, BAY_CARRIER_W 30 ->
    # |y| <= 15.  A 16 mm slab let door material at |y| 15..16 project onto a
    # carrier it never meets (3-D: 1.98 mm clear, 2-D: 41 mm^2 "overlap").
    box = Manifold.cube([120.0, 2 * half_y, 120.0]).translate([-60.0, -half_y, -60.0])
    swap = [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]          # (x,y,z) -> (x,z,y)
    polys = []
    for cn, c in corners.items():
        if lgbf.STATION[cn] != station:
            continue
        inv = np.linalg.inv(lgbf.corner_tf(c))[:3, :].tolist()
        for n, e in P.items():
            if n.startswith(("gear legs", "shell")):
                continue
            loc = e["m"].transform(inv) ^ box
            if loc.volume() <= 0.05:
                continue
            # project() returns outer AND hole rings: combine them even-odd, or
            # a hollow door outline fills in solid (found 2026-10-11)
            g = Polygon()
            for ring in loc.transform(swap).project().to_polygons():
                if len(ring) >= 3:
                    g = g.symmetric_difference(Polygon(np.asarray(ring)).buffer(0))
            polys.append(g)
    _OBST[key] = unary_union(polys) if polys else Polygon()
    return _OBST[key]


def evaluate2(tD, tS, stop_az, station=None):
    """v2 feasibility: returns (ok, notes, min clearance, cluster azimuths)."""
    _a, _L, Point, _P, unary_union = _shapely()
    th = thigh_shape()
    pin = Point(*(STOP_PIN_R * az(stop_az))).buffer(STOP_PIN_RAD)
    notes, gaps = [], []
    hw = {row: row_hardware(t, row) for row, t in (("D", tD), ("S", tS))}
    # The thigh outline is the projected REAL mesh (thigh_shape), swept ONCE and
    # cached; each candidate's horns are swept and added.  The candidate's own
    # scallops are not subtracted -- they only remove thigh material, so leaving
    # them in is conservative.
    moving = _unary([_swept_thigh(), swept(horn_shape(tD, "D")), swept(horn_shape(tS, "S"))])
    rb = {k: (v["d"] + SOCK_CLR) / 2 for k, v in ROWS.items()}
    sock_gap = np.linalg.norm(CRANK_R * (az(tD) - az(tS))) - rb["D"] - rb["S"] - WALL
    if sock_gap < 0:
        notes.append(f"sockets {sock_gap:+.1f}")
    for row in ("D", "S"):
        hard, band, s = hw[row]
        other = "S" if row == "D" else "D"
        ov = hard.intersection(moving).area
        # 2-D projection ignores Y, so it over-reports a few mm^2 that the 3-D
        # census clears (Rev R6 row: 1.8 mm^2 at flex 26 here, 0 mm^3 in 3-D).
        # Up to HW_THIGH_SLACK is passed on to the census to decide.
        g = [("hardware vs swept thigh+horns", MARGIN if ov <= HW_THIGH_SLACK
              else -ov),
             ("hardware vs other row hardware", hard.distance(hw[other][0])
              if not hard.intersects(hw[other][0]) else -1.0),
             ("hardware vs stop pin", hard.distance(pin)),
             ("band vs stop pin", band.distance(pin)),
             ("band vs other hardware", band.distance(hw[other][0])
              if not band.intersects(hw[other][0]) else -1.0),
             ("band vs other socket", band.distance(Point(*hw[other][2]).buffer(rb[other])))]
        # band vs the thigh EXCEPT its own root (scallop relief cuts the first 14 mm)
        near = Point(*s).buffer(14.0)
        g.append(("band vs thigh beyond scallop", band.difference(near).distance(th)
                  if not band.difference(near).intersects(th) else -1.0))
        for name, v in g:
            gaps.append(v)
            if v < MARGIN:
                notes.append(f"{row} {name} {v:+.1f}")
    # stop pin vs the swept thigh body (2026-10-11: at 290 the pin sat INSIDE
    # the root lug -- 98.6 mm^3 in the 3-D census).  The projected thigh carries
    # the base render's tab (131..146); remove it, add this candidate's tab
    # (stop + 13..28), and require the pin clear of the sweep everywhere except
    # the tab's own contact face, which is allowed to touch at rest.
    old_tab = _tab_polygon(118.0)
    body = th.difference(old_tab.buffer(0.3))
    pin_gap = pin.distance(swept(body))
    if pin_gap < 0.5:
        notes.append(f"stop pin vs swept thigh {pin_gap:+.1f}")
    new_tab = _tab_polygon(stop_az)
    tab_gap = new_tab.distance(_unary([hw["D"][0], hw["S"][0]]))
    if tab_gap < MARGIN:
        notes.append(f"stop tab vs row hardware {tab_gap:+.1f}")
    soft = []
    if station:
        # each kind of hardware against the cargo parts in ITS OWN Y slab: the
        # carrier spans |y| <= 15 (BAY_CARRIER_W 30), the bosses |y| <= 8.5
        # (rows at +/-3, O11), the wires |y| <= 5.2 -- one 15 mm slab put door
        # material at |y| 9..15 onto bosses it never meets (2026-10-11)
        for row, t in (("D", tD), ("S", tS)):
            car, boss = _PARTS[(round(float(t), 3), row)]
            for name, shp, hy in (("carrier", car, 15.0), ("bosses", boss, 8.5),
                                  ("wire band", hw[row][1], 5.2)):
                obst = station_obstacles(station, hy)
                gap = shp.distance(obst) if not shp.intersects(obst) else -shp.intersection(obst).area
                if gap < MARGIN:
                    # SOFT: the projection ignores how a round boss narrows away
                    # from its axis in Y, so it over-reports; ranked, and the 3-D
                    # census decides (aft 165/30: 2-D -14.6 mm^2, 3-D 0)
                    soft.append((f"{row} {name}", min(gap, 0.0)))
    # horns vs stop pin over the flex range (pin is bay-fixed, horns ride the thigh)
    for row, t in (("D", tD), ("S", tS)):
        sw = swept(horn_shape(t, row))
        if sw.distance(pin) < 0.5:
            notes.append(f"{row} horn vs stop pin {sw.distance(pin):+.1f}")
    cl = {}
    for row in ("D", "S"):
        c = np.array(hw[row][0].centroid.coords[0])
        cl[row] = (round(math.degrees(math.atan2(c[1], c[0])), 1), round(float(np.linalg.norm(c)), 1))
    cl["soft_mm2"] = round(-sum(g for _n, g in soft), 1)
    cl["soft_parts"] = sorted({n for n, g in soft if g < 0})
    return (not notes), notes, round(min(gaps), 2), cl


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stop", type=float, action="append",
                    help="stop-pin azimuth(s) to try (default: 118, the current)")
    ap.add_argument("--step", type=float, default=5.0)
    ap.add_argument("--v1", action="store_true", help="the v1 (circle) screen")
    a = ap.parse_args()
    if not a.v1:
        for stop in a.stop or [118.0]:
            print(f"\n== v2 screen, stop pin at {stop:g} deg")
            n = 0
            for tD in np.arange(-180, 180, a.step):
                for tS in np.arange(-180, 180, a.step):
                    if tD == tS:
                        continue
                    ok, notes, gap, cl = evaluate2(tD, tS, stop)
                    if ok:
                        n += 1
                        print(f"  t_D {tD:6.0f}  t_S {tS:6.0f}  clusters D {cl['D']} S {cl['S']}  "
                              f"min clearance {gap:+.2f} mm")
            print(f"  {n} feasible")
        return 0
    poly = lug_polygon()
    for stop in a.stop or [118.0]:
        print(f"\n== stop pin at {stop:g} deg (tab {stop + 13:g}..{stop + 28:g})")
        n = 0
        for tD in np.arange(-180, 180, a.step):
            for tS in np.arange(-180, 180, a.step):
                if tD == tS:
                    continue
                ok, notes, cl, worst = evaluate(tD, tS, stop, poly)
                if ok:
                    n += 1
                    print(f"  t_D {tD:6.0f}  t_S {tS:6.0f}  clusters D {cl['D']} S {cl['S']}  "
                          f"min wire clearance {worst:+.2f} mm")
        print(f"  {n} feasible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
