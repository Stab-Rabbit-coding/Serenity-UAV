#!/usr/bin/env python3
"""sls_materials.py -- single source of SLS material properties for every
Serenity sizing / margin tool after the FDM CF-PETG -> SLS migration (2026-11-01).

Import, don't copy:  `from sls_materials import PA_CF, PA11, design`.

Values are the datasheet XY numbers, verbatim (ASTM column):
  PA_CF  DuraForm PA CF, 3DS-30108A (2023-10-31)        [REF-MAT-015]
  PA11   DuraForm PA11 Black (2025-03-04)               [REF-MAT-016]
  PA12   DuraForm PA12 Black (2025-04-03)               [REF-MAT-017]

`design(mat, key)` returns the value to size against when the build
orientation is NOT fixed: PA CF strengths and moduli are multiplied by
Z_KNOCKDOWN_PA_CF because 3DS-30108A gives no Z data (fibre-filled SLS is
weakest across layers).  0.5 is ASSUMED, the same placeholder WBS already
carries ("Obtain PA CF build-axis (Z) tensile and flexural data ... replacing
the 0.5 knockdown").  PA11 is used at face value: its sheet states "more
consistent isotropic performance" [REF-MAT-016].  No compressive or bearing
value is published for any of the three; COMPRESSIVE is set to the tensile
ultimate, flagged ASSUMED (polyamides are not weaker in compression than in
tension, but this is not a published allowable).

Material assignment rule (owner decisions 2026-10-31, plan 2026-10-31-002):
  PA CF -- everything stiffness-driven: hull shells, collars, nacelle pods,
           brackets, gears, trays, wing skins, gear leg frames.
  PA11  -- everything that must yield instead of break: gear feet and skids,
           snap/leaf springs whose strain exceeds PA CF's 3.8 % elongation,
           living hinges, impact bumpers.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (Stab-Rabbit-coding)
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction,
         2026-11-01.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

PA_CF = {
    "name": "DuraForm PA CF", "ref": "REF-MAT-015",
    "rho_g_cc": 1.11, "tensile_ult_mpa": 84.0, "tensile_mod_mpa": 8500.0,
    "elong_break_pct": 3.8, "flex_strength_mpa": 140.0, "flex_mod_mpa": 7000.0,
    "hdt_182_c": 177.0, "izod_notched_j_m": 52.0,
}
PA11 = {
    "name": "DuraForm PA11 Black", "ref": "REF-MAT-016",
    "rho_g_cc": 1.03, "tensile_ult_mpa": 51.0, "tensile_yield_mpa": 51.0,
    "tensile_mod_mpa": 1900.0, "elong_break_pct": 52.6, "elong_yield_pct": 26.3,
    "flex_strength_mpa": 56.0, "flex_mod_mpa": 1500.0, "hdt_182_c": 58.0,
    "izod_notched_j_m": 42.0,
}
PA12 = {
    "name": "DuraForm PA12 Black", "ref": "REF-MAT-017",
    "rho_g_cc": 1.00, "tensile_ult_mpa": 45.0, "tensile_mod_mpa": 1800.0,
    "elong_break_pct": 13.7, "flex_mod_mpa": 1500.0, "izod_notched_j_m": 35.0,
}
for _m in (PA_CF, PA11, PA12):
    _m["compressive_mpa"] = _m["tensile_ult_mpa"]  # ASSUMED, see docstring

Z_KNOCKDOWN_PA_CF = 0.5  # ASSUMED until Z coupons / vendor data (WBS)
_KNOCKED = ("tensile_ult_mpa", "tensile_mod_mpa", "flex_strength_mpa",
            "flex_mod_mpa", "compressive_mpa")


def design(mat, key):
    """Orientation-agnostic design value (PA CF knocked down for Z)."""
    v = mat[key]
    if mat is PA_CF and key in _KNOCKED:
        v *= Z_KNOCKDOWN_PA_CF
    return v


if __name__ == "__main__":
    for m in (PA_CF, PA11, PA12):
        print(m["name"], {k: design(m, k) for k in m if k not in ("name", "ref")})
