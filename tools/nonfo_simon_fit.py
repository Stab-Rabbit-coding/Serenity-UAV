#!/usr/bin/env python3
"""nonfo_simon_fit.py -- S34 gates for the NoNFO-Pilot-PB2 stern stack at Simon's med bay.

Replaces the CN4 + FC4 pouch pair in tools/middle_layout_fit.py with the one merged stack
(carrier on the bottom, PB2-I riding on top; plan KTD5) and runs the same check against the
published middle shell: hull clearance, the static gap, and pair overlaps with Kaylee. It then
sums the zone contract's mass and 5 V lines against plan R2 and prints a first thermal figure.

The zone contract is the copy in avionics/kicad/NoNFO-Pilot-PB2/zone_contract.json; the
canonical file is SecureControllers kicad/NoNFO-Pilot/PB2/zone_contract.json (copy-with-index).

Run:  python3 tools/nonfo_simon_fit.py            # both orientations; exit 1 if none passes
Needs trimesh, shapely and manifold3d, as middle_layout_fit.py does.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the author's direction,
2026-11-14, per AGENTS.md SS3 AI attribution.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import argparse
import contextlib
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACT = os.path.join(REPO, "avionics", "kicad", "NoNFO-Pilot-PB2", "zone_contract.json")
ALLOW = 1.0  # [ASSUMED] mm per side for the board edge, solder fillets and connector bodies
OLD = ("CN4 (XO) pouch", "FC4 (Pilot) pouch", "Simon cable zone", "Simon saddle")


def load_contract(path=CONTRACT):
    with open(path) as f:
        return json.load(f)


def stack_height(c):
    s = c["stack"]
    return (s["carrier_bottom_max"] + s["carrier_t"] + s["rail_insulator"]
            + s["pb2_max_height"] + s["hold_down_bridge"])


def stack_mass(c, board_t="t1.6"):
    m = c["mass_g"]
    tot = m["board_fr4_6L"][board_t]
    for k, v in m.items():
        if k != "board_fr4_6L" and v.get("g") is not None:
            tot += v["g"]
    return tot


def power_peak_w(c, volts=5.0):
    return volts * sum(v["a_peak"] for v in c["power_5v"].values())


def layout(c, portrait, dx=0.0, cable_side=+1):
    """middle_layout_fit's T6 layout with the merged stack in place of the pouch pair.

    dx shifts the stack in X (mm, + = port); cable_side +1 puts the harness zone on the port
    side of the stack, -1 on the starboard side.
    """
    import middle_layout_fit as mlf  # mesh libraries are needed only for the fit
    from cargo_layout_fit import box

    w, h = c["outline"]["w"] + 2 * ALLOW, c["outline"]["h"] + 2 * ALLOW
    sx, sz = (h, w) if portrait else (w, h)
    t = stack_height(c)
    x0, x1 = mlf.SIMON_XC + dx - sx / 2, mlf.SIMON_XC + dx + sx / 2
    z0, z1 = mlf.SIMON_ZC - sz / 2, mlf.SIMON_ZC + sz / 2
    y0, y1 = mlf.SIMON_Y0, mlf.SIMON_Y0 + t
    L = {k: v for k, v in mlf.layout_t6().items() if k not in OLD}
    for v in L.values():
        v["mates"] = tuple(m for m in v.get("mates", ()) if m not in OLD)
    L["NoNFO stack"] = dict(solid=box(x0, x1, y0, y1, z0, z1), gap=mlf.STATIC_GAP,
                            section="middle")
    L["NoNFO cable zone"] = dict(
        solid=(box(x1, x1 + mlf.NODE_CABLE, y0, y1, z0, z1) if cable_side > 0
               else box(x0 - mlf.NODE_CABLE, x0, y0, y1, z0, z1)), gap=mlf.STATIC_GAP,
        section="middle", mates=("NoNFO stack", "Simon trunk"))
    L["NoNFO saddle"] = dict(solid=box(x0 - 4.0, x1 + 4.0, y0, y1 + 2.0, 85.0, z0),
                             skin_seat=True, section="middle", mates=("NoNFO stack",))
    for v in L.values():
        if "Simon trunk" in v.get("mates", ()) and v is not L["NoNFO cable zone"]:
            v["mates"] = tuple(v["mates"]) + ("NoNFO cable zone",)
    return L, (x0, x1, y0, y1, z0, z1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--contract", default=CONTRACT)
    ap.add_argument("--verbose", action="store_true", help="print the full mesh report")
    a = ap.parse_args()
    import middle_layout_fit as mlf

    c = load_contract(a.contract)
    t = stack_height(c)
    slot = mlf.REAR_RESERVED_Y - mlf.SIMON_Y0
    print(f"Stack height {t:.2f} mm ({t / 25.4:.3f} in): target "
          f"{c['limits']['stack_height_target']} mm, Simon slot {slot:.1f} mm before the "
          f"Phase-11 rear cone")
    mid = mlf.load_middle()
    results = {}
    for name, portrait in (("landscape (3.40 in across)", False),
                           ("portrait (3.40 in tall)", True)):
        best = None
        for side in (+1, -1):
            for dx in (0.0, 1.0, -1.0, 2.0, -2.0, 3.0, -3.0, 5.0, -5.0):
                L, bb = layout(c, portrait, dx, side)
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    fails, pairs, _ = mlf.check_section(L, mid, [], "middle")
                ok = fails == 0 and pairs == 0 and bb[3] <= mlf.REAR_RESERVED_Y
                if best is None or (ok and not best[0]):
                    best = (ok, dx, side, fails, pairs, bb, out.getvalue())
                if ok:
                    break
            if best[0]:
                break
        ok, dx, side, fails, pairs, bb, rep = best
        results[name] = ok
        where = "port" if side > 0 else "starboard"
        print(f"\nFit, {name}: {'PASS' if ok else 'FAIL'} at X shift {dx:+.1f} mm, harness zone "
              f"{where} ({fails} envelope(s) foul the shell or gap, {pairs} pair overlap(s)); "
              f"box X{bb[0]:.1f}..{bb[1]:.1f} Y{bb[2]:.1f}..{bb[3]:.1f} Z{bb[4]:.1f}..{bb[5]:.1f}")
        if a.verbose or not ok:
            print(rep)
    lim = c["limits"]["stack_mass_g_max"]
    print("\nMass (pouched stack, R2 limit below %.0f g):" % lim)
    for bt in ("t1.6", "t1.0"):
        m = stack_mass(c, bt)
        print(f"  board {bt[1:]} mm: {m:.1f} g ({m / 453.592:.3f} lbm)  "
              f"{'PASS' if m < lim else 'FAIL'}; credit {m - lim:+.1f} g against the pair")
    p = power_peak_w(c)
    print(f"\n5 V peak load {p / 5.0:.2f} A, {p:.1f} W [ASSUMED lines marked in the contract]; "
          f"all of it ends as heat in the stack at {c['limits']['design_ambient_c']:.0f} C "
          f"design ambient (temperature rise needs the heat path, S40)")
    ok = any(results.values()) and stack_mass(c, "t1.6") < lim
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
