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


def base_tc(upper, lower, samples=400):
    """Maximum t/c of the tabulated section at t_scale = 1.0.

    Reported so the solved thickness scales can be quoted as an ACTUAL
    thickness ratio rather than a bare multiplier -- 't_scale 2.19' means
    nothing to an aerodynamicist, 'tip t/c 26.6 %' means the section is no
    longer an S1223 (plan 003 RISK-1).
    """
    return max(surf_y(upper, x / samples) - surf_y(lower, x / samples)
               for x in range(1, samples))


def camber_midline(upper, lower, station_mm, chord):
    """Camber-midline height in mm at a station, with NO thickness scaling.

    This is the value the SCAD's spar_bore() centres on and the value the
    fuselage side needs for SPAR_Z: s1223_section() opens the thickness
    envelope about an UNSCALED camber line (Rev S1b), so the bore centre does
    not move when THICKNESS_SCALE changes.  Section.at()'s reported midline
    DOES carry the scale factor (see its docstring), so it is the wrong number
    to hand to the fuselage -- hence this separate, deliberately unscaled
    helper.
    """
    xq = station_mm / chord
    return (surf_y(upper, xq) + surf_y(lower, xq)) / 2.0 * chord


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


def solve_scale(sec, station, bore_d, target_wall):
    """Smallest t_scale that holds `target_wall` over the bore at `station`.

    Thickness scales linearly, so bisection is overkill -- but the midline
    moves with it too, so solve numerically rather than by ratio.

    Works for EITHER end station.  Through Rev S1b this solved the tip only,
    because the tip was the only station a Rev-R2-class D8.3 bore could
    threaten -- the root was 15.6 mm deep against an 8.3 mm bore and never
    came close to the floor.  The unified D20.4 spar
    (docs/plans/2026-08-29-003-...) breaks that assumption outright: at the
    28 mm station the ROOT section is 15.60 mm deep against a bore that needs
    22.72 mm, so the root OML now moves too -- the first revision in which it
    ever has.  A tip-only solver would have reported the tip figure and said
    nothing about a root that breaks out by 2.40 mm.  Hence the generalised
    name and the root row in main().

    The caller's Section is MUTATED (its t_scale is left at the bisection's
    last probe), so pass a throwaway instance -- same contract as before.
    """
    lo, hi = 0.5, 6.0
    for _ in range(80):
        mid_scale = (lo + hi) / 2.0
        sec.t_scale = mid_scale
        _d, _m, wu, wd = sec.at(station)
        if min(wu, wd) - bore_d / 2.0 < target_wall:
            lo = mid_scale
        else:
            hi = mid_scale
    return hi


# Retained under its original name: tools/wing_internal_clearance.py and the
# Rev S1b/U6 notes in wings_s1223_revo.scad both cite solve_tip_scale() by
# name.  Renaming it silently would break those citations' traceability.
def solve_tip_scale(tip, station, bore_d, target_wall):
    """Backward-compatible alias for solve_scale() -- see that docstring."""
    return solve_scale(tip, station, bore_d, target_wall)


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
    ap.add_argument("--t-root", type=float, default=None,
                    help="override THICKNESS_SCALE for the root section "
                         "(default: read from the wing SCAD)")
    ap.add_argument("--t-tip", type=float, default=None,
                    help="override THICKNESS_SCALE_TIP for the tip section "
                         "(default: read from the wing SCAD)")
    args = ap.parse_args()

    src = open(WING_SCAD).read()
    upper = scad_points(src, "S1223_UPPER")
    lower = scad_points(src, "S1223_LOWER")
    c_root = scad_scalar(src, "WING_CHORD_ROOT")
    c_tip = scad_scalar(src, "WING_CHORD_TIP")
    ts_root = (args.t_root if args.t_root is not None
               else scad_scalar(src, "THICKNESS_SCALE"))
    ts_tip = (args.t_tip if args.t_tip is not None
              else scad_scalar(src, "THICKNESS_SCALE_TIP"))
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
    # The conditional is hoisted OUT of the f-string deliberately.  A
    # replacement field spanning physical lines inside a single-quoted
    # f-string is PEP 701, i.e. Python 3.12+; CI lints on 3.11, where the
    # tokenizer ends the literal at the newline and reports
    # "unterminated string literal" (E999 / mypy [syntax]) -- which aborts the
    # whole lint run before any other file is checked.  Keep it hoisted.
    sweep_note = (
        "straight LE: constant-mm station is perpendicular to centreline"
        if sweep == 0.0 else
        "SWEPT LE: a constant-mm station is NOT perpendicular to the "
        "centreline -- resolve before trusting these numbers"
    )
    print(f"  WING_SWEEP_LE = {sweep:.1f} mm -> {sweep_note}")
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
        # BOTH ends are solved.  See solve_scale()'s docstring for why the
        # root row is no longer optional: a D20.4 bore breaks the root out
        # too, so reporting the tip alone would understate the OML change.
        need_root = solve_scale(Section("root", c_root, ts_root, upper, lower),
                                st, args.bore, args.min_wall)
        need_tip = solve_scale(Section("tip", c_tip, ts_tip, upper, lower),
                               st, args.bore, args.min_wall)
        v_root = ("as-built" if need_root <= ts_root + 1e-6
                  else "MORE THAN as-built")
        v_tip = ("as-built" if need_tip <= ts_tip + 1e-6
                 else "MORE THAN as-built")
        print(f"  -> root needs THICKNESS_SCALE     >= {need_root:.3f} "
              f"({v_root} {ts_root:.2f})   root t/c "
              f"{need_root * base_tc(upper, lower):.1%}")
        print(f"  -> tip  needs THICKNESS_SCALE_TIP >= {need_tip:.3f} "
              f"({v_tip} {ts_tip:.2f})   tip  t/c "
              f"{need_tip * base_tc(upper, lower):.1%}")
        # Unscaled camber-midline heights -- what spar_bore() centres on and
        # what the fuselage-side SPAR_Z must be derived from.
        m_root = camber_midline(upper, lower, st, c_root)
        m_tip = camber_midline(upper, lower, st, c_tip)
        print(f"  -> bore centre on the UNSCALED camber midline: "
              f"root +{m_root:.2f} mm / tip +{m_tip:.2f} mm above the "
              f"chord line")


if __name__ == "__main__":
    main()
