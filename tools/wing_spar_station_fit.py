#!/usr/bin/env python3
"""Size the wing spar's chordwise station against the S1223 section it lives in.

The Rev R1a spar bore is a CONSTANT chordwise station in millimetres
(`SPAR_BORE_STATION`), parallel to the straight leading edge, not a constant
chord fraction -- a fraction-based bore walked 10.8 mm / 7.2 deg forward over
span and cut the "swept" cutout (airframe/wings-nacelles/WBS.md SS1.1.2).  That
makes the station a single number that must satisfy TWO very different sections
at once: the root (chord 129 mm) and the tip (chord 93 mm).  The same 45 mm
station is 35.0 % of root chord but 48.5 % of tip chord, and S1223 loses depth
fast aft of its ~20 % max-thickness point, so a station that is comfortable at
the root can break the bore out through the tip skin.

That is exactly the trap `THICKNESS_SCALE_TIP` was added for.  This tool makes
the trade visible instead of discovering it after a 6-hour print: for any
candidate station it reports, at root and tip, the section depth, the camber
midline the bore is centred on, and the minimum remaining skin wall above and
below a D12.3 spar -- then solves for the tip thickening a target wall needs.

The airfoil coordinates are PARSED FROM THE SCAD SOURCE, never re-typed here,
so the numbers describe the wing that actually gets built.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-16, per AGENTS.md AI attribution.
License : CC BY-SA 4.0  <https://creativecommons.org/licenses/by/4.0/>

Run: /usr/bin/python3 tools/wing_spar_station_fit.py [--station MM] [--pct P]
"""

import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
WING_SCAD = os.path.join(REPO_ROOT, "airframe", "openscad", "wings",
                         "wings_s1223_revo.scad")

# Minimum printable skin over the spar bore.  The Rev R1a root already runs at
# 1.16 mm (WBS SS1.1.2), which is ~2.9 extrusions at a 0.4 mm nozzle -- thin,
# but accepted and printed.  Hold that as the floor rather than inventing a
# new requirement mid-change.
MIN_WALL_MM = 1.16


def scad_scalar(src, name):
    """Read `NAME = <number>;` out of the SCAD source."""
    m = re.search(rf"^{name}\s*=\s*(-?[\d.]+)\s*;", src, re.M)
    if not m:
        sys.exit(f"could not find {name} in {WING_SCAD}")
    return float(m.group(1))


def scad_points(src, name):
    """Read a `NAME = [ [x, y], ... ];` coordinate table out of the SCAD."""
    m = re.search(rf"^{name}\s*=\s*\[(.*?)^\];", src, re.M | re.S)
    if not m:
        sys.exit(f"could not find {name} in {WING_SCAD}")
    pts = [(float(a), float(b)) for a, b in
           re.findall(r"\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\]", m.group(1))]
    if len(pts) < 10:
        sys.exit(f"{name} parsed as only {len(pts)} points -- format changed?")
    return pts


def surf_y(pts, xq):
    """Linear-interpolate surface y (t/c) at chord fraction xq.

    Mirrors the SCAD surf_y(): the point lists run in opposite x order, so each
    segment is tested both ways round.
    """
    for a, b in zip(pts, pts[1:]):
        if (a[0] <= xq <= b[0]) or (b[0] <= xq <= a[0]):
            if b[0] == a[0]:
                return a[1]
            return a[1] + (xq - a[0]) / (b[0] - a[0]) * (b[1] - a[1])
    return 0.0


class Section:
    """One span station's S1223 section."""

    def __init__(self, label, chord, t_scale, upper, lower):
        self.label, self.chord, self.t_scale = label, chord, t_scale
        self.upper, self.lower = upper, lower

    def at(self, station_mm):
        """(depth, midline, wall_up, wall_dn) in mm for a bore at station_mm.

        NOTE this applies t_scale uniformly, which is how the SCAD scaled the
        section before Rev S1b.  DEPTH and WALL are unaffected by that choice
        -- thickness-only scaling opens the envelope by the same factor -- so
        the fit numbers here remain correct either way.  Only the reported
        MIDLINE differs: under thickness-only scaling the camber line is not
        scaled, so the true bore centre is midline / t_scale.  See
        tools/wing_airfoil_variants.py for the camber comparison.
        """
        xq = station_mm / self.chord
        yu = surf_y(self.upper, xq) * self.chord * self.t_scale
        yl = surf_y(self.lower, xq) * self.chord * self.t_scale
        mid = (yu + yl) / 2.0
        return (yu - yl), mid, (yu - mid), (mid - yl)

    def frac(self, station_mm):
        return station_mm / self.chord


def solve_tip_scale(tip, station, bore_d, target_wall):
    """Smallest t_scale that holds `target_wall` over the bore at `station`.

    Thickness scales linearly, so bisection is overkill -- but the midline
    moves with it too, so solve numerically rather than by ratio.
    """
    lo, hi = 0.5, 6.0
    for _ in range(80):
        mid_scale = (lo + hi) / 2.0
        tip.t_scale = mid_scale
        _d, _m, wu, wd = tip.at(station)
        if min(wu, wd) - bore_d / 2.0 < target_wall:
            lo = mid_scale
        else:
            hi = mid_scale
    return hi


def row(sec, station, bore_d):
    depth, mid, wu, wd = sec.at(station)
    up, dn = wu - bore_d / 2.0, wd - bore_d / 2.0
    worst = min(up, dn)
    flag = "" if worst >= MIN_WALL_MM else ("  BREAKS OUT" if worst < 0
                                            else "  THIN")
    return (f"  {sec.label:<5} chord {sec.chord:5.1f}  {sec.frac(station):5.1%} "
            f"chord  t_scale {sec.t_scale:4.2f}  depth {depth:5.2f}  "
            f"midline {mid:+5.2f}  wall up {up:+5.2f} / dn {dn:+5.2f}{flag}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--station", type=float, action="append", default=None,
                    help="candidate station, mm aft of LE (repeatable)")
    ap.add_argument("--pct", type=float, action="append", default=None,
                    help="candidate station as %% of ROOT chord (repeatable)")
    ap.add_argument("--bore", type=float, default=None,
                    help="spar bore diameter, mm (default: SPAR_BORE_OD "
                         "from the wing SCAD)")
    ap.add_argument("--min-wall", type=float, default=MIN_WALL_MM,
                    help=f"target minimum skin wall, mm (default {MIN_WALL_MM})")
    ap.add_argument("--scan", action="store_true",
                    help="find the aft-most station the as-built tip "
                         "thickening still supports")
    args = ap.parse_args()

    src = open(WING_SCAD).read()
    upper = scad_points(src, "S1223_UPPER")
    lower = scad_points(src, "S1223_LOWER")
    c_root = scad_scalar(src, "WING_CHORD_ROOT")
    c_tip = scad_scalar(src, "WING_CHORD_TIP")
    ts_root = scad_scalar(src, "THICKNESS_SCALE")
    ts_tip = scad_scalar(src, "THICKNESS_SCALE_TIP")
    cur = scad_scalar(src, "SPAR_BORE_STATION")
    sweep = scad_scalar(src, "WING_SWEEP_LE")
    wing_bore = scad_scalar(src, "SPAR_BORE_OD")
    if args.bore is None:
        args.bore = wing_bore

    print("wing spar station fit -- S1223, parsed from "
          f"{os.path.relpath(WING_SCAD, REPO_ROOT)}")
    print(f"  root chord {c_root:.1f}  tip chord {c_tip:.1f}  "
          f"bore D{args.bore}  min wall {args.min_wall:.2f} mm")
    # A constant-mm station is parallel to the LE only while the LE is
    # straight; with sweep it would rake and stop being perpendicular to the
    # aircraft centreline, which the spar must be.
    print(f"  WING_SWEEP_LE = {sweep:.1f} mm -> "
          f"{'straight LE: constant-mm station is perpendicular to centreline'
             if sweep == 0.0 else
             'SWEPT LE: a constant-mm station is NOT perpendicular to the '
             'centreline -- resolve before trusting these numbers'}")
    if wing_bore != args.bore:
        print(f"  NOTE wing SPAR_BORE_OD is D{wing_bore} "
              f"(rotating spar); checking D{args.bore} instead")
    print(f"  current SPAR_BORE_STATION = {cur:.1f} mm "
          f"({cur / c_root:.1%} root chord, {cur / c_tip:.1%} tip chord)")

    if args.scan:
        # The tip is always the binding station (it is both shorter and, at a
        # constant mm station, a larger chord fraction), so walk aft until the
        # tip wall drops through the floor at the as-built thickening.
        print(f"\nscan: aft-most station at THICKNESS_SCALE_TIP = {ts_tip:.2f}"
              f", wall >= {args.min_wall:.2f} mm")
        best = None
        st = 5.0
        while st < c_tip:
            tip = Section("tip", c_tip, ts_tip, upper, lower)
            _d, _m, wu, wd = tip.at(st)
            if min(wu, wd) - args.bore / 2.0 >= args.min_wall:
                best = st
            elif best is not None:
                break
            st += 0.05
        if best is None:
            print("  no station satisfies the floor")
        else:
            print(f"  aft-most feasible station {best:.2f} mm = "
                  f"{best / c_root:.1%} root chord "
                  f"({best / c_tip:.1%} tip chord)")
            print(row(Section("root", c_root, ts_root, upper, lower),
                      best, args.bore))
            print(row(Section("tip", c_tip, ts_tip, upper, lower),
                      best, args.bore))
        return

    stations = list(args.station or [])
    stations += [p / 100.0 * c_root for p in (args.pct or [])]
    if not stations:
        stations = [cur, 0.30 * c_root, 0.35 * c_root]

    for st in stations:
        print(f"\nstation {st:.2f} mm aft of LE  "
              f"({st / c_root:.1%} root chord):")
        root = Section("root", c_root, ts_root, upper, lower)
        tip = Section("tip", c_tip, ts_tip, upper, lower)
        print(row(root, st, args.bore))
        print(row(tip, st, args.bore))
        need = solve_tip_scale(Section("tip", c_tip, ts_tip, upper, lower),
                               st, args.bore, args.min_wall)
        verdict = "as-built" if need <= ts_tip + 1e-6 else "MORE THAN as-built"
        print(f"  -> tip needs THICKNESS_SCALE_TIP >= {need:.3f} "
              f"({verdict} {ts_tip:.2f})")


if __name__ == "__main__":
    main()
