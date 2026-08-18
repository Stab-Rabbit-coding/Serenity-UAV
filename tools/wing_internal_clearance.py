#!/usr/bin/env python3
"""Check every internal bore in the wing against its neighbours and the skin.

`wing_spar_station_fit.py` sizes ONE bore (the spar) against the section it
lives in.  It cannot see the failure mode that Rev S1b introduced, because that
failure is between TWO bores: the spar is a constant chordwise station in
millimetres while the EDF harness double-D and the AK7455 sensor conduit were
constant chord FRACTIONS.  A constant-mm bore and a constant-fraction bore
converge as the chord tapers, so a pair that clears at the root can be fully
merged at the tip -- and nothing in the SCAD or in the single-bore fit tool
reports it.

Rev S1b moved `SPAR_BORE_STATION` 22.0 -> 45.15 mm without moving either
conduit, which put:

  * the forward Ø7 EDF conduit inside the Ø8.3 spar bore from 29.6 % span
    outboard (both conduits merged with the spar at the tip), and
  * the Ø3.5 AK7455 conduit (0.33c = 42.57 mm at the root) inside the spar
    bore at the root.

Routing 40 A EDF feeds through the same cavity as a rotating steel spar is not
a tolerance problem, it is a wiring fault, so this tool is fail-closed: it
exits non-zero on any violation and is meant to run before a wing re-render.

Checks, over a sampled span from root face to tip face:

  1. bore-to-bore  -- centre distance vs (r1 + r2 + MIN_WEB_MM)
  2. bore-to-skin  -- remaining S1223 skin above/below each bore vs MIN_WALL_MM
  3. tip termination -- each bore against the wingtip mount pad, which is PROUD
                      of the tip face.  A conduit that must EXIT the face into
                      the nacelle (the EDF pair) fails if the pad covers it; a
                      conduit that must FEED the sensor pocket in the pad (the
                      AK7455 lead) fails if it stops short of the pad instead.

Section geometry and every station/diameter are PARSED FROM THE SCAD SOURCE,
never re-typed here, so the numbers describe the wing that actually gets built.
Thickness scaling is applied the way Rev S1b's `s1223_section()` applies it --
about the camber line, thickness only -- so bore centres sit on the UNSCALED
camber midline (see tools/wing_spar_station_fit.py, which documents the same
distinction for its own reported midline).

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-18, per AGENTS.md AI attribution.
License : CC BY-SA 4.0  <https://creativecommons.org/licenses/by/4.0/>

Run: /usr/bin/python3 tools/wing_internal_clearance.py [--samples N] [--verbose]
"""

import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
WING_SCAD = os.path.join(REPO_ROOT, "airframe", "openscad", "wings",
                         "wings_s1223_revo.scad")

# Minimum printed web between two internal bores.  WALL_T in the wing SCAD is
# 2.5 mm (4 perimeters at a 0.6 mm nozzle); hold that between bores, where a
# thin web has skin on neither side to stiffen it.
MIN_WEB_MM = 2.5

# Minimum skin over a bore.  The Rev R1a root already runs 1.16 mm over the
# spar and prints, so hold that as the floor rather than inventing a new
# requirement mid-change -- same constant, same reasoning, as
# tools/wing_spar_station_fit.py.
MIN_WALL_MM = 1.16

# Clearance a harness conduit needs between its tip-face opening and the
# wingtip mount pad footprint.  The pad is PROUD of the tip face, so any
# overlap caps the conduit and the wires cannot reach the nacelle.
MIN_PAD_GAP_MM = 1.0


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
    pairs = re.findall(r"\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\]", m.group(1))
    return sorted((float(a), float(b)) for a, b in pairs)


def interp(table, xq):
    """Linear interpolation of a sorted (x, y) table at xq."""
    if xq <= table[0][0]:
        return table[0][1]
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x0 <= xq <= x1:
            if x1 == x0:
                return y0
            return y0 + (y1 - y0) * (xq - x0) / (x1 - x0)
    return table[-1][1]


class Section:
    """One S1223 station: chord, thickness scale, and the camber line."""

    def __init__(self, upper, lower, chord, t_scale):
        self.upper, self.lower = upper, lower
        self.chord, self.t_scale = chord, t_scale

    def midline(self, station_mm):
        """Bore-centre height, mm above the chord line (camber, UNSCALED)."""
        xq = station_mm / self.chord
        return (interp(self.upper, xq) + interp(self.lower, xq)) / 2.0 * self.chord

    def depth(self, station_mm):
        """Section depth, mm (thickness-only scaling about the camber line)."""
        xq = station_mm / self.chord
        return (interp(self.upper, xq) - interp(self.lower, xq)) * self.chord * self.t_scale


class Bore:
    """A spanwise bore: a chordwise station law, a diameter, and how it ends.

    `tip_end` says what the bore must do at the tip face, which decides how it
    is judged against the wingtip pad:

      "exit"  -- breaks out of the tip face into the nacelle harness port, so
                 the pad must NOT cover it (EDF double-D).
      "pocket"-- terminates under the pad and jogs into the sensor pocket, so
                 the pad MUST cover it (AK7455 lead).
      "through" -- runs through the pad by design (the spar); not judged here.
    """

    def __init__(self, name, diameter, root_station, tip_station, tip_end):
        self.name = name
        self.d = diameter
        self.root_station = root_station
        self.tip_station = tip_station
        self.tip_end = tip_end

    def station(self, f):
        """Chordwise station, mm aft of LE, at span fraction f."""
        return self.root_station + (self.tip_station - self.root_station) * f

    @property
    def r(self):
        return self.d / 2.0


def load_wing():
    """Parse the wing SCAD into sections and the list of internal bores."""
    with open(WING_SCAD, encoding="utf-8") as handle:
        src = handle.read()

    upper = scad_points(src, "S1223_UPPER")
    lower = scad_points(src, "S1223_LOWER")

    chord_root = scad_scalar(src, "WING_CHORD_ROOT")
    chord_tip = scad_scalar(src, "WING_CHORD_TIP")
    t_root = scad_scalar(src, "THICKNESS_SCALE")
    t_tip = scad_scalar(src, "THICKNESS_SCALE_TIP")

    root = Section(upper, lower, chord_root, t_root)
    tip = Section(upper, lower, chord_tip, t_tip)

    spar_station = scad_scalar(src, "SPAR_BORE_STATION")
    spar_d = scad_scalar(src, "SPAR_BORE_OD")

    cable_d = scad_scalar(src, "CABLE_BORE_D")
    cable_sep = scad_scalar(src, "CABLE_BORE_SEP")
    hall_d = scad_scalar(src, "HALL_CABLE_D")

    bores = [Bore("spar", spar_d, spar_station, spar_station, "through")]

    # The EDF double-D and the AK7455 conduit each take EITHER a constant-mm
    # station (…_STATION) or a legacy constant chord FRACTION (…_XFR).  Accept
    # both so this tool reports on the pre-fix source as well as the fixed one
    # -- that is the whole point of a regression check.
    def station_law(mm_name, frac_name, label):
        mm = re.search(rf"^{mm_name}\s*=\s*(-?[\d.]+)\s*;", src, re.M)
        if mm:
            value = float(mm.group(1))
            return value, value, f"{mm_name} = {value} mm (constant station)"
        frac = re.search(rf"^{frac_name}\s*=\s*(-?[\d.]+)\s*;", src, re.M)
        if frac:
            value = float(frac.group(1))
            return (chord_root * value, chord_tip * value,
                    f"{frac_name} = {value} c (CHORD FRACTION -- tapers)")
        sys.exit(f"could not find {mm_name} or {frac_name} for {label}")

    cable_root, cable_tip, cable_law = station_law(
        "CABLE_BORE_STATION", "CABLE_BORE_XFR", "EDF cableway")
    for sign, side in ((-1.0, "fwd"), (+1.0, "aft")):
        bores.append(Bore(f"EDF {side}", cable_d,
                          cable_root + sign * cable_sep / 2.0,
                          cable_tip + sign * cable_sep / 2.0, "exit"))

    hall_root, hall_tip, hall_law = station_law(
        "HALL_CABLE_STATION", "HALL_CABLE_XFR", "AK7455 conduit")
    bores.append(Bore("AK7455", hall_d, hall_root, hall_tip, "pocket"))

    pad_fwd_r = scad_scalar(src, "TIP_PAD_FWD_R") if re.search(
        r"^TIP_PAD_FWD_R\s*=", src, re.M) else scad_scalar(src, "TIP_PAD_OD") / 2.0
    pad_aft_r = scad_scalar(src, "TIP_PAD_AFT_R") if re.search(
        r"^TIP_PAD_AFT_R\s*=", src, re.M) else scad_scalar(src, "TIP_PAD_OD") / 2.0
    hall_sens_r = scad_scalar(src, "HALL_SENS_R")

    return {
        "root": root, "tip": tip, "bores": bores,
        "spar_station": spar_station,
        "pad_fwd_edge": spar_station - pad_fwd_r,
        "pad_aft_edge": spar_station + hall_sens_r + pad_aft_r,
        "laws": [f"spar        : SPAR_BORE_STATION = {spar_station} mm (constant station)",
                 f"EDF double-D: {cable_law}",
                 f"AK7455      : {hall_law}"],
    }


def check(wing, samples, verbose):
    """Run all three checks; return a list of violation strings."""
    root, tip, bores = wing["root"], wing["tip"], wing["bores"]
    violations = []

    def section_at(f):
        chord = root.chord + (tip.chord - root.chord) * f
        t_scale = root.t_scale + (tip.t_scale - root.t_scale) * f
        return Section(root.upper, root.lower, chord, t_scale)

    # ── 1. bore-to-bore ──────────────────────────────────────────────────────
    worst = {}
    for i in range(samples + 1):
        f = i / samples
        for a_idx, a in enumerate(bores):
            for b in bores[a_idx + 1:]:
                need = a.r + b.r + MIN_WEB_MM
                gap = abs(a.station(f) - b.station(f)) - need
                key = (a.name, b.name)
                if key not in worst or gap < worst[key][0]:
                    worst[key] = (gap, f)
    for (a_name, b_name), (gap, f) in sorted(worst.items()):
        status = "OK " if gap >= 0 else "FAIL"
        if verbose or gap < 0:
            print(f"  [{status}] web {a_name:<8s} <-> {b_name:<8s} "
                  f"{gap:+7.2f} mm (worst at {f * 100:5.1f} % span)")
        if gap < 0:
            violations.append(
                f"{a_name} and {b_name} are {-gap:.2f} mm closer than the "
                f"{MIN_WEB_MM:.1f} mm minimum web at {f * 100:.1f} % span"
                + (" -- the bores INTERSECT" if
                   abs(bores[0].r) and gap < -MIN_WEB_MM else ""))

    # ── 2. bore-to-skin ──────────────────────────────────────────────────────
    for bore in bores:
        worst_wall, worst_f = None, 0.0
        for i in range(samples + 1):
            f = i / samples
            sec = section_at(f)
            wall = sec.depth(bore.station(f)) / 2.0 - bore.r
            if worst_wall is None or wall < worst_wall:
                worst_wall, worst_f = wall, f
        status = "OK " if worst_wall >= MIN_WALL_MM else "FAIL"
        if verbose or worst_wall < MIN_WALL_MM:
            print(f"  [{status}] skin over {bore.name:<8s} "
                  f"{worst_wall:+7.2f} mm (worst at {worst_f * 100:5.1f} % span)")
        if worst_wall < MIN_WALL_MM:
            violations.append(
                f"{bore.name} leaves {worst_wall:.2f} mm of skin at "
                f"{worst_f * 100:.1f} % span, below the {MIN_WALL_MM:.2f} mm floor")

    # ── 3. tip termination vs the wingtip mount pad ──────────────────────────
    pad_fwd, pad_aft = wing["pad_fwd_edge"], wing["pad_aft_edge"]
    for bore in bores:
        if bore.tip_end == "through":
            continue          # the spar runs THROUGH the pad by design
        tip_fwd = bore.station(1.0) - bore.r
        tip_aft = bore.station(1.0) + bore.r

        if bore.tip_end == "exit":
            # Must break out of the tip face: the pad must not reach back over it.
            gap = pad_fwd - tip_aft
            ok = gap >= MIN_PAD_GAP_MM
            if verbose or not ok:
                print(f"  [{'OK ' if ok else 'FAIL'}] tip exit {bore.name:<8s} "
                      f"to pad fwd edge {gap:+7.2f} mm")
            if not ok:
                violations.append(
                    f"{bore.name} must exit the tip face but opens at "
                    f"{tip_aft:.2f} mm while the wingtip pad starts at "
                    f"{pad_fwd:.2f} mm -- the pad caps the conduit")
        else:
            # Must terminate INSIDE the pad footprint so its jog reaches the
            # sensor pocket.  Failing this means the lead surfaces in open skin.
            ok = tip_fwd >= pad_fwd and tip_aft <= pad_aft
            if verbose or not ok:
                print(f"  [{'OK ' if ok else 'FAIL'}] tip pocket {bore.name:<8s} "
                      f"opening {tip_fwd:.2f}..{tip_aft:.2f} mm inside pad "
                      f"{pad_fwd:.2f}..{pad_aft:.2f} mm")
            if not ok:
                violations.append(
                    f"{bore.name} must terminate under the wingtip pad "
                    f"({pad_fwd:.2f}..{pad_aft:.2f} mm) to reach the sensor "
                    f"pocket, but opens at {tip_fwd:.2f}..{tip_aft:.2f} mm")
    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--samples", type=int, default=200,
                    help="span sample count (default 200)")
    ap.add_argument("--verbose", action="store_true",
                    help="print passing checks too")
    args = ap.parse_args()

    wing = load_wing()
    print(f"wing internal clearance -- parsed from "
          f"{os.path.relpath(WING_SCAD, REPO_ROOT)}")
    print(f"  root chord {wing['root'].chord}  tip chord {wing['tip'].chord}  "
          f"t_scale {wing['root'].t_scale} -> {wing['tip'].t_scale}")
    print(f"  min web {MIN_WEB_MM} mm   min skin {MIN_WALL_MM} mm   "
          f"min pad gap {MIN_PAD_GAP_MM} mm")
    for law in wing["laws"]:
        print(f"  {law}")
    print()

    violations = check(wing, args.samples, args.verbose)

    print()
    if violations:
        print(f"FAIL -- {len(violations)} violation(s):")
        for v in violations:
            print(f"  * {v}")
        return 1
    print("PASS -- all bores clear each other, the skin, and the wingtip pad")
    return 0


if __name__ == "__main__":
    sys.exit(main())
