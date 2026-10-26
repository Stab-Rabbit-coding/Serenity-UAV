#!/usr/bin/python3
"""Landing-gear DUCTILE FUSE wire: material trade on cited properties only.

Owner 2026-10-26: "the ductile wire fuse is supposed to fail non-elastically,
so spring steel might not be the best material ... seriously consider the
component properties."  The sizing tool specifies the fuse only as
"ductile-temper steel wire, flow stress ~550 MPa" with no source.  What the
fuse needs, and how each property is checked here:

  1. PLATEAU FORCE from the flow stress.  Two-hinge bowed wire (sizing tool
     SS4.5a): P = 2 M_p / h0, M_p = sigma d^3 / 6, so d = (3 P h0 / sigma)^(1/3).
     The wire is sized at the LOWER bound (yield) so it absorbs at least the
     design energy at the design plateau.
  2. PLATEAU SPREAD.  The bay, pin and thigh must survive the HIGHEST plateau
     the wire can produce: strain hardening drives the flow stress toward the
     ultimate, so the mount demand scales by Su / Sy.  A low Su/Sy (flat
     plateau) is what a fuse wants; a work-hardening material raises every
     mount demand by that ratio (owner failure hierarchy, LG-HIERARCHY).
  3. DUCTILITY.  The wire must not crack before it completes the stroke.
     Middle-hinge strain at full stroke: eps ~ (d/2) * (2 dphi) / L_p, with
     the plastic-hinge length L_p taken as one wire diameter (design-judgment
     assumption, REQUIRES VERIFICATION by a bench firing, LG-15), so
     eps ~ dphi.  Compared with the material's cited elongation.
  4. NO DUCTILE-BRITTLE TRANSITION.  Face-centred-cubic metals (aluminium,
     austenitic stainless, copper alloys) have none; plain carbon steels do.
     Noted, not computed.
  5. MASS.  Eight ductile wires per aircraft.
  6. Owner material order (2026-10-26): aluminium and brass before any steel.

Candidates are limited to cited properties: 6061-T6 [REF-MAT-007], annealed
304 per ASTM A240 minimums [REF-MAT-006], and ASTM A228 music wire
[REF-MAT-008] (spring temper -- included to show why it is wrong for a fuse;
its source publishes no yield, so its Sy is not available).  The current
uncited "550 MPa ductile steel" is shown for reference only.

Run:  /usr/bin/python3 tools/lg_fuse_material.py [--p-wire N] [--span MM]
Defaults are Option A of docs/LG_BELLCRANK_LOAD_PATH_STUDY.md (P 4,593 N per
wire, 21 mm bow span, 3.84 mm stroke).

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-26, per AGENTS.md section 3 AI attribution.
License: MIT (SPDX-License-Identifier: MIT) -- see tools/LICENSE.
"""

from __future__ import annotations

import argparse
import math
import sys

H0 = 3.5            # mm, pre-bend rise (sizing tool)
SEATS = 2 * (8.0 + 2.0)   # mm, seat + run-in per end (sizing tool SEAT_DUCTILE, END_RUN_IN)
N_WIRES = 8         # ductile wires per aircraft

# name: (Sy MPa, Su MPa, elongation, density g/mm^3, lattice, ref)
MATERIALS = {
    "6061-T6 aluminium": (276.0, 310.0, 0.17, 2.70e-3, "FCC", "REF-MAT-007"),
    "304 annealed (A240 min)": (205.0, 515.0, 0.40, 7.90e-3, "FCC", "REF-MAT-006"),
    "A228 music wire": (None, 1586.0, None, 7.90e-3, "BCC", "REF-MAT-008"),
    "uncited 'ductile steel 550'": (550.0, None, None, 7.85e-3, "BCC", "none"),
}


def hinge_strain(span, stroke):
    """Middle-hinge strain at full stroke, eps ~ dphi (L_p = d assumption)."""
    half = span / 2.0
    root = math.sqrt(half**2 - H0**2) - stroke / 2.0
    hf = math.sqrt(max(half**2 - root**2, 0.0))
    return math.asin(hf / half) - math.asin(H0 / half), hf


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--p-wire", type=float, default=4593.0, help="design plateau per wire, N")
    ap.add_argument("--span", type=float, default=21.0, help="bow span, mm")
    ap.add_argument("--stroke", type=float, default=3.84, help="required stroke, mm")
    a = ap.parse_args(argv)
    eps, hf = hinge_strain(a.span, a.stroke)
    length = a.span + SEATS
    print(f"Ductile fuse, P {a.p_wire:.0f} N per wire, bow span {a.span} mm, stroke "
          f"{a.stroke} mm: fired rise {hf:.2f} mm, middle-hinge strain ~{100 * eps:.1f} % "
          f"(L_p = d assumption)\n")
    print(f"{'material':30s} {'d mm':>6s} {'g/aircraft':>10s} {'Su/Sy':>6s} "
          f"{'elong.':>7s} {'eps margin':>10s} {'DBTT':>5s}  ref")
    for name, (sy, su, el, rho, lat, ref) in MATERIALS.items():
        if sy is None:
            print(f"{name:30s} {'--':>6s} {'--':>10s} {'--':>6s} {'--':>7s} {'--':>10s} "
                  f"{'yes' if lat == 'BCC' else 'none':>5s}  {ref}: no cited yield -- a "
                  f"spring temper, cannot be sized as a fuse")
            continue
        d = (3.0 * a.p_wire * H0 / sy) ** (1.0 / 3.0)
        mass = N_WIRES * math.pi / 4.0 * d * d * length * rho
        ratio = f"{su / sy:.2f}" if su else "--"
        elo = f"{100 * el:.0f} %" if el else "--"
        em = f"{el / eps:.1f}" if el else "--"
        print(f"{name:30s} {d:6.2f} {mass:10.1f} {ratio:>6s} {elo:>7s} {em:>10s} "
              f"{'yes' if lat == 'BCC' else 'none':>5s}  {ref}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
