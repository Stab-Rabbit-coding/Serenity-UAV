#!/usr/bin/env python3
"""sls_auw_reconcile.py -- part-by-part reconciliation of the aircraft AUW between SLS
and FDM CF-PETG, across every printed part on the aircraft (hull AND nacelles), for
every ledger configuration.

Rev U (2026-11-07): the ledger (tools/auw_ledger.py) now prices every printed part
at its SLS datasheet solid density (tools/sls_materials.py: PA CF 1.11, PA11 1.03
g/cc), so the ledger IS the SLS figure.  This tool now recovers each part's volume
from the density the ledger used and shows what FDM CF-PETG would weigh instead
(bulk 1.05, solid 1.28).  deltas() returns (FDM-solid change, SLS change); the SLS
change is 0.0 by construction and is kept so callers that add it to the ledger
(tail_strike_requirement.py) cannot double count.

Why this exists: the 14.09 lbm "SLS" design mass used in plan 2026-10-31-002 was
built by re-pricing only the ledger's hull-side PRINT subtotal; the nacelles'
printed parts sit inside the NACELLE subtotal and were left at FDM density.  It was
also the heaviest-payload configuration, while 13.38 lbm is hover.  This tool
re-derives both figures openly.

Method (no new geometry):
  * Every printed part's VOLUME = ledger mass / the density the ledger used for it
    (PA CF 1.11, PA11 1.03 g/cc).  Volume is process-independent here: the FDM part
    is the same STL.
  * FDM is shown at two densities: the ledger's 1.05 (bulk, with infill) and solid
    1.28 (REF-MAT-002), because thin 2 mm walls print as perimeters only
    (docs/MASS_AUDIT_CARGO_WING_ROOT.md section 1).  Weighing one shell decides it.
  * SLS: each part gets its assigned material density [REF-MAT-015..017].
    PA CF 1.11 by default; PA11 1.03 for the gear feet (impact, plan 002 KTD3).
  * Mass items that are not printed (BOM, NACELLE hardware, GAP) are unchanged.

Run:  /usr/bin/python3 tools/sls_auw_reconcile.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction, 2026-10-31.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nacelle_mass_cg_64 as nac64  # noqa: E402
import sls_materials as sls  # noqa: E402  datasheet densities (single source)

ROOT = os.path.join(HERE, "..")
LB = 453.59237
RHO_FDM, RHO_FDM_SOLID = 1.05, 1.28
# Datasheet solid densities (3D Systems, ASTM D792) -- single source: sls_materials.py
RHO = {"PA CF": sls.PA_CF["rho_g_cc"], "PA11": sls.PA11["rho_g_cc"],
       "PA12": sls.PA12["rho_g_cc"]}
# Material assignment for SLS (owner decisions 2026-10-31): PA11 at the impact
# points; everything else PA CF.  Ring + skids (Option B, PA11) are not yet a
# separate part -- they are still inside the rear/middle shells -- see SKID_G.
SLS_MATERIAL = {"lg_r6_common_foot": "PA11"}
SKID_G_LEDGER = 56.9   # g at 1.05, skid tubes inside the shells (MASS_AUDIT_MIDDLE_REAR)
NACELLE_PRINTED = ("Pod shell", "Stage-2 cartridge", "ESC access cover",
                   "Nozzle throat", "Unison ring", "nozzle flap", "Trunnion")


def rho_ledger(name):
    """Density (g/cc) the ledger used for a hull PRINT row."""
    return RHO[SLS_MATERIAL.get(name, "PA CF")]


def ledger():
    with open(os.path.join(ROOT, "current-specification", "auw_ledger.json")) as f:
        return json.load(f)


def nacelle_printed_g():
    """Printed-part mass per nacelle at PA CF density, by row, from the nacelle roll-up."""
    pod = os.path.join(ROOT, "airframe", "stls", "nacelles", "nacelle_stbd_64mm.stl")
    rows = [(r[0], r[1]) for r in nac64.rows_64(nac64.Path(pod))]
    rows += [(r[0], r[1]) for r in nac64.ON_AXIS_64]
    return [(n, m) for n, m in rows
            if any(k.lower() in n.lower() for k in NACELLE_PRINTED) and "bearing" not in n.lower()]


def deltas():
    """(change to FDM-solid, change to SLS) in g, against the ledger.

    The ledger is already SLS, so the SLS change is exactly 0.0.
    """
    d = ledger()
    hull = [r for r in d["rows_hover"] if r["kind"] == "PRINT"]
    nl = 2 * sum(m for _, m in nacelle_printed_g())
    d_solid = sum(r["mass_g"] / rho_ledger(r["name"]) * RHO_FDM_SOLID - r["mass_g"]
                  for r in hull)
    d_solid += nl * (RHO_FDM_SOLID / RHO["PA CF"] - 1)
    return d_solid, 0.0


def main():
    d = ledger()
    hull = [r for r in d["rows_hover"] if r["kind"] == "PRINT"]
    nac = nacelle_printed_g()
    print("HULL-SIDE PRINTED PARTS (ledger PRINT rows, SLS datasheet densities)")
    print(f"  {'part':38s} {'SLS mat':>8s} {'SLS g':>7s} {'FDM 1.05':>9s} {'FDM 1.28':>9s}")
    tot = {"q": 0.0, "l": 0.0, "s": 0.0}
    for r in sorted(hull, key=lambda r: -r["mass_g"]):
        mat = SLS_MATERIAL.get(r["name"], "PA CF")
        q = r["mass_g"]
        vol = q / RHO[mat]
        tot["q"] += q
        tot["l"] += vol * RHO_FDM
        tot["s"] += vol * RHO_FDM_SOLID
        if q >= 5:
            print(f"  {r['name'][:38]:38s} {mat:>8s} {q:7.1f} {vol * RHO_FDM:9.1f} "
                  f"{vol * RHO_FDM_SOLID:9.1f}")
    print(f"  {'(all hull PRINT rows, incl. < 5 g)':38s} {'':>8s} {tot['q']:7.1f} "
          f"{tot['l']:9.1f} {tot['s']:9.1f}")
    print("\nNACELLE PRINTED PARTS (inside the NACELLE subtotal; x 2 nacelles)")
    nl = sum(m for _, m in nac)
    for n, q in nac:
        v = q / RHO["PA CF"]
        print(f"  {n[:38]:38s} {'PA CF':>8s} {q:7.1f} {v * RHO_FDM:9.1f} "
              f"{v * RHO_FDM_SOLID:9.1f}")
    nac_q = 2 * nl
    nac_l = nac_q / RHO["PA CF"] * RHO_FDM
    nac_s = nac_q / RHO["PA CF"] * RHO_FDM_SOLID
    print(f"  {'both nacelles':38s} {'':>8s} {nac_q:7.1f} {nac_l:9.1f} {nac_s:9.1f}")
    skid_d = SKID_G_LEDGER / RHO_FDM * (RHO["PA11"] - RHO["PA CF"])
    print(f"\n  Option B skids in PA11 instead of PA CF: {skid_d:+.1f} g (not yet a separate part)")
    d_fdm = (tot["l"] - tot["q"]) + (nac_l - nac_q)
    d_fdm_solid = (tot["s"] - tot["q"]) + (nac_s - nac_q)
    print("\nAUW BY CONFIGURATION (non-printed mass unchanged)")
    print(f"  {'configuration':24s} {'SLS ledger':>16s} {'FDM bulk 1.05':>16s} "
          f"{'FDM solid 1.28':>16s}")
    for k in ("hover_4000", "cargo_2800_payload", "heaviest_4000_payload"):
        m = d["configs"][k]["mass_g"]
        rows = (m, m + d_fdm, m + d_fdm_solid)
        print(f"  {k:24s} " + " ".join(f"{g:7.0f} g {g / LB:5.2f}" for g in rows))
    print(f"\n  printed mass on the aircraft, SLS: hull {tot['q']:.0f} g + nacelles {nac_q:.0f} g"
          f" = {tot['q'] + nac_q:.0f} g ({(tot['q'] + nac_q) / LB:.2f} lbm)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
