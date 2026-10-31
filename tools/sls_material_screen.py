#!/usr/bin/env python3
"""sls_material_screen.py -- screen the 3D Systems SLS nylons against the repo's
printed-part list.  Prints (1) figures of merit from the supplied datasheets and
(2) the mass effect of a per-part material assignment on both density bases.

Data: 3D Systems datasheets 3DS-30108A (PA CF, 10-23, preliminary), 3DS-30112A
(PA12 Black, 02-25), 3DS-30109A (PA11 Black, 02-25), ProX AF+ (10-17) and the
Material Selection Guide 3DS-30101D (03-23), all supplied by the owner.  CF-PETG
reference: docs/MASS_AUDIT_CARGO_WING_ROOT.md SS1 (flex modulus 6.67 GPa, REF-MAT-002;
solid 1.28 g/cc; ledger as-printed bulk 1.05 g/cc).

Two density bases are shown because the ledger prices every printed part at the
1.05 g/cc bulk density, while the mass audit itself says thin perimeter-only
sections are nearer the 1.28 g/cc solid density.  Weigh a printed 2 mm shell to
decide which holds.

Run:  python3 tools/sls_material_screen.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction,
2026-10-31, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "..", "current-specification", "auw_ledger.json")

# name: (density g/cc, flex modulus MPa, tensile modulus MPa, elongation % (break), notched Izod J/m)
MATS = {
    "CF-PETG (repo)": (1.28, 6670, None, None, None),
    "PA CF": (1.11, 7000, 8500, 3.8, 52),
    "PA12 Black": (1.00, 1500, 1800, 13.7, 35),
    "PA11 Black": (1.03, 1500, 1900, 52.6, 42),
    "ProX PA": (0.95, 1650, 1770, 22.0, 45),
    "ProX HST": (1.12, 3430, 4123, 4.3, 55),
    "ProX AF+": (1.31, 3710, 4340, 3.0, 54),
    "PAx Black": (1.04, 900, 1500, 100.0, 58),
}

BASE_BULK, BASE_SOLID = 1.05, 1.28  # ledger as-printed bulk; solid CF-PETG

# ledger PRINT ref -> material (None = leave on FDM CF-PETG)
ASSIGN = {
    "PRINT-HEAD-SHELL": "PA CF", "PRINT-CARGO-SECT": "PA CF",
    "PRINT-MIDDLE-CANONICAL": "PA CF", "PRINT-REAR-NECK-INTAKE": "PA CF",
    "PRINT-HEAD-CARGO-COLLAR": "PA CF", "PRINT-CARGO-MIDDLE-COLLAR": "PA CF",
    "PRINT-MIDDLE-REAR-COLLAR": "PA CF",
    "PRINT-WINGS-S1223": None,  # aero section unverified; keep FDM until verified
    "PRINT-LG-LEG-FRAME-3.0IN": "PA11 Black", "PRINT-LG-FOOT": "PA11 Black",
    "PRINT-LG-BAY-PLATE": "PA CF",  # must out-last the leg frame (fuse before mount)
    "PRINT-BATT-CRADLE": "PA CF", "PRINT-WING-ROOT-FLANGE": "PA CF",
    "PRINT-TILT-BRACKET": "PA CF",
    "PRINT-CARGO-DOOR-PORT": "PA11 Black", "PRINT-CARGO-DOOR-STBD": "PA11 Black",
    "PRINT-TILT-WHEEL": None, "PRINT-TILT-WORM": None,  # wear-critical; bench-test first
    "PRINT-DORSAL-ANTENNA-FIN": "PA12 Black", "PRINT-GPS-RETENTION": "PA12 Black",
    "PRINT-FPV-BEZEL": "PA12 Black",
}
DEFAULT = "PA CF"  # small brackets and shelves


def merit():
    print("figures of merit (higher is better)")
    print(f"{'material':16s} {'rho':>5s} {'E/rho':>7s} {'Eflex^1/3/rho':>14s} {'Etens^1/2/rho':>14s}"
          f" {'elong%':>7s} {'notchedJ/m':>11s}")
    for n, (rho, ef, et, el, iz) in MATS.items():
        panel = ef ** (1 / 3) / rho
        strut = (et ** 0.5 / rho) if et else float("nan")
        eor = (et / rho) if et else float("nan")
        print(f"{n:16s} {rho:5.2f} {eor:7.0f} {panel:14.1f} {strut:14.1f} "
              f"{(el if el is not None else float('nan')):7.1f} {(iz if iz else float('nan')):11.0f}")
    print("panel index = flex modulus^(1/3)/rho: equal-stiffness plate mass ~ 1/index")
    print("strut index = tensile modulus^(1/2)/rho")


def assign():
    rows = [r for r in json.load(open(LEDGER))["rows_hover"] if r["kind"] == "PRINT"]
    out = {}
    tot0 = 0.0
    for r in rows:
        mat = ASSIGN.get(r["ref"], DEFAULT if r["ref"] in ASSIGN else DEFAULT)
        tot0 += r["mass_g"]
        for basis_name, base in (("ledger bulk 1.05", BASE_BULK), ("solid 1.28", BASE_SOLID)):
            rho = MATS[mat][0] if mat else None
            m = r["mass_g"] if mat is None else r["mass_g"] * rho / base
            out.setdefault(basis_name, {}).setdefault(mat or "FDM CF-PETG (kept)", 0.0)
            out[basis_name][mat or "FDM CF-PETG (kept)"] += m
    print(f"\nprinted parts (ledger PRINT rows): {len(rows)} items, {tot0:.0f} g today")
    for basis_name, d in out.items():
        tot = sum(d.values())
        print(f"  basis {basis_name}: {tot:.0f} g ({tot - tot0:+.0f} g); " +
              ", ".join(f"{k} {v:.0f}" for k, v in sorted(d.items())))


if __name__ == "__main__":
    merit()
    assign()
