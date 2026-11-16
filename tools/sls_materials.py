#!/usr/bin/env python3
"""sls_materials.py -- single source of SLS material properties for every
Serenity sizing / margin tool after the FDM CF-PETG -> SLS migration (2026-11-01).

Import, don't copy:  `from sls_materials import PA_CF, PA11, design`.

Values are the datasheet XY numbers, verbatim (ASTM column):
  PA_CF  DuraForm PA CF, 3DS-30108A (2023-10-31)        [REF-MAT-015]
  PA11   DuraForm PA11 Black (2025-03-04)               [REF-MAT-016]
  PA12   DuraForm PA12 Black (2025-04-03)               [REF-MAT-017]

`design(mat, key)` returns the value to size against when the build
orientation is NOT fixed: PA CF strengths x Z_STRENGTH_PA_CF (0.44) and moduli x
Z_MODULUS_PA_CF (0.35), because 3DS-30108A gives no Z data (fibre-filled SLS is
weakest across layers).  The factors come from the closest published 33 %
carbon-fibre PA12 data (see the constants below); they replaced the 0.5
ASSUMED placeholder on 2026-11-11 and remain ESTIMATE until coupons.
PA11 is used at face value: its sheet states "more
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

#: Legacy FDM CF-PETG bulk print density, g/mm^3.  Kept ONLY to convert masses that
#: were written down on the old FDM basis (tools/auw_ledger.py priced every printed
#: part at this value until Rev U).  Never price a Rev U SLS part with it.
RHO_FDM_BULK_G_MM3 = 1.05e-3


def rho_g_mm3(mat):
    """Datasheet solid density of an SLS material, g/mm^3 (ASTM D792)."""
    return mat["rho_g_cc"] * 1e-3


def sls_from_fdm_mass(mass_g, mat=None):
    """Convert a mass written on the FDM 1.05 g/cc basis to the same volume in SLS.

    Defaults to PA CF.  Volume is the same STL either way; only the density changes.
    """
    return mass_g * rho_g_mm3(mat or PA_CF) / RHO_FDM_BULK_G_MM3


# Build-axis (Z) knockdowns for PA CF, replacing the single 0.5 ASSUMED factor (2026-11-11).
# Source: reports/SLS Z axis strength.md.  The closest published proxy is ALM PA 603-CF (also 33 %
# carbon-fibre PA12, X values within ~2 % of 3DS-30108A), EOS datasheet page, ASTM D638:
# Z/X strength 37/85 = 0.44, Z/X modulus 3000/8600 = 0.35; Protolabs UK PA12 Carbon Filled Black
# (DIN EN ISO 527) corroborates (0.53, 0.35).  ESTIMATE: neither is DuraForm PA CF, the values are
# means, and no filled-SLS flexural Z data exist, so flexural values take the tensile ratios.
# Only X/Y/Z coupons on the production machine (docs/MATSPEC_SLS_PA_CF.md section 8) qualify them.
Z_STRENGTH_PA_CF = 0.44
Z_MODULUS_PA_CF = 0.35
Z_ELONGATION_PA_CF = 0.58     # Protolabs UK Z/X 2.2/3.2 (the lower of the two proxies)
#: In-plane but direction not controlled (Y): strength 0.65, modulus 0.41 (Protolabs UK, the lower).
Y_STRENGTH_PA_CF = 0.65
Y_MODULUS_PA_CF = 0.41
#: Kept for callers that want one number: the strength factor (the old 0.5 overstated Z by ~14 %).
Z_KNOCKDOWN_PA_CF = Z_STRENGTH_PA_CF
_STRENGTH_KEYS = ("tensile_ult_mpa", "flex_strength_mpa", "compressive_mpa")
_MODULUS_KEYS = ("tensile_mod_mpa", "flex_mod_mpa")


def design(mat, key):
    """Orientation-agnostic design value (PA CF knocked down for Z)."""
    v = mat[key]
    if mat is PA_CF:
        if key in _STRENGTH_KEYS:
            v *= Z_STRENGTH_PA_CF
        elif key in _MODULUS_KEYS:
            v *= Z_MODULUS_PA_CF
        elif key == "elong_break_pct":
            v *= Z_ELONGATION_PA_CF
    return v


if __name__ == "__main__":
    for m in (PA_CF, PA11, PA12):
        print(m["name"], {k: design(m, k) for k in m if k not in ("name", "ref")})
