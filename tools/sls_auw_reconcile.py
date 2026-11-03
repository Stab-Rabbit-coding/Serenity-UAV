#!/usr/bin/env python3
"""sls_auw_reconcile.py -- part-by-part reconciliation of the aircraft AUW from FDM
CF-PETG to SLS, across every printed part on the aircraft (hull AND nacelles), for
every ledger configuration.

Why this exists: the 14.09 lbm "SLS" design mass used in plan 2026-10-31-002 was
built by re-pricing only the ledger's hull-side PRINT subtotal; the nacelles'
printed parts sit inside the NACELLE subtotal and were left at FDM density.  It was
also the heaviest-payload configuration, while 13.38 lbm is hover.  This tool
re-derives both figures openly.

Method (no new geometry):
  * Every printed part's VOLUME = ledger mass / RHO_PRINT (1.05 g/cc), because the
    ledger prices every printed part as STL volume x RHO_PRINT (tools/auw_ledger.py,
    tools/nacelle_mass_cg_64.py).  Volume is process-independent here: the SLS part
    is the same STL, printed fully dense.
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

ROOT = os.path.join(HERE, "..")
LB = 453.59237
RHO_LEDGER, RHO_FDM_SOLID = 1.05, 1.28
RHO = {"PA CF": 1.11, "PA11": 1.03, "PA12": 1.00}
# Material assignment for SLS (owner decisions 2026-10-31): PA11 at the impact
# points; everything else PA CF.  Ring + skids (Option B, PA11) are not yet a
# separate part -- they are still inside the rear/middle shells -- see SKID_G.
SLS_MATERIAL = {"lg_r6_common_foot": "PA11"}
SKID_G_LEDGER = 56.9   # g at 1.05, skid tubes inside the shells (MASS_AUDIT_MIDDLE_REAR)
NACELLE_PRINTED = ("Pod shell", "Stage-2 cartridge", "ESC access cover",
                   "Nozzle throat", "Unison ring", "nozzle flap", "Trunnion")


def ledger():
    with open(os.path.join(ROOT, "current-specification", "auw_ledger.json")) as f:
        return json.load(f)


def nacelle_printed_g():
    """Printed-part mass per nacelle at 1.05 g/cc, by row, from the nacelle roll-up."""
    pod = os.path.join(ROOT, "airframe", "stls", "nacelles", "nacelle_stbd_64mm.stl")
    rows = [(r[0], r[1]) for r in nac64.rows_64(nac64.Path(pod))]
    rows += [(r[0], r[1]) for r in nac64.ON_AXIS_64]
    return [(n, m) for n, m in rows
            if any(k.lower() in n.lower() for k in NACELLE_PRINTED) and "bearing" not in n.lower()]


def deltas():
    """(hull+nacelle mass change to FDM-solid, to SLS) in g, against the ledger."""
    d = ledger()
    hull = [r for r in d["rows_hover"] if r["kind"] == "PRINT"]
    nl = 2 * sum(m for _, m in nacelle_printed_g())
    hl = sum(r["mass_g"] for r in hull)
    hq = sum(r["mass_g"] / RHO_LEDGER * RHO[SLS_MATERIAL.get(r["name"], "PA CF")] for r in hull)
    d_solid = (hl + nl) * (RHO_FDM_SOLID / RHO_LEDGER - 1)
    d_sls = (hq - hl) + nl * (RHO["PA CF"] / RHO_LEDGER - 1)
    return d_solid, d_sls


def main():
    d = ledger()
    hull = [r for r in d["rows_hover"] if r["kind"] == "PRINT"]
    nac = nacelle_printed_g()
    print("HULL-SIDE PRINTED PARTS (ledger PRINT rows; volume = mass / 1.05)")
    print(f"  {'part':38s} {'FDM 1.05':>9s} {'FDM 1.28':>9s} {'SLS mat':>8s} {'SLS g':>7s} "
          f"{'d SLS-1.05':>10s}")
    tot = {"l": 0.0, "s": 0.0, "q": 0.0}
    for r in sorted(hull, key=lambda r: -r["mass_g"]):
        mat = SLS_MATERIAL.get(r["name"], "PA CF")
        m = r["mass_g"]
        q = m / RHO_LEDGER * RHO[mat]
        tot["l"] += m
        tot["s"] += m / RHO_LEDGER * RHO_FDM_SOLID
        tot["q"] += q
        if m >= 5:
            print(f"  {r['name'][:38]:38s} {m:9.1f} {m / RHO_LEDGER * RHO_FDM_SOLID:9.1f} "
                  f"{mat:>8s} {q:7.1f} {q - m:+10.1f}")
    print(f"  {'(all hull PRINT rows, incl. < 5 g)':38s} {tot['l']:9.1f} {tot['s']:9.1f} "
          f"{'':>8s} {tot['q']:7.1f} {tot['q'] - tot['l']:+10.1f}")
    print("\nNACELLE PRINTED PARTS (inside the NACELLE subtotal; x 2 nacelles)")
    nl = sum(m for _, m in nac)
    for n, m in nac:
        print(f"  {n[:38]:38s} {m:9.1f} {m / RHO_LEDGER * RHO_FDM_SOLID:9.1f} {'PA CF':>8s} "
              f"{m / RHO_LEDGER * 1.11:7.1f} {m / RHO_LEDGER * 1.11 - m:+10.1f}")
    nac_l, nac_s, nac_q = 2 * nl, 2 * nl / RHO_LEDGER * RHO_FDM_SOLID, 2 * nl / RHO_LEDGER * 1.11
    print(f"  {'both nacelles':38s} {nac_l:9.1f} {nac_s:9.1f} {'':>8s} {nac_q:7.1f} "
          f"{nac_q - nac_l:+10.1f}")
    skid_d = SKID_G_LEDGER / RHO_LEDGER * (RHO["PA11"] - RHO["PA CF"])
    d_fdm_solid = (tot["s"] - tot["l"]) + (nac_s - nac_l)
    d_sls = (tot["q"] - tot["l"]) + (nac_q - nac_l)
    print(f"\n  Option B skids in PA11 instead of PA CF: {skid_d:+.1f} g (not yet a separate part)")
    print("\nAUW BY CONFIGURATION (non-printed mass unchanged)")
    print(f"  {'configuration':24s} {'FDM ledger 1.05':>16s} {'FDM solid 1.28':>16s} "
          f"{'SLS (hull+nac)':>16s} {'SLS hull only*':>16s}")
    for k in ("hover_4000", "cargo_2800_payload", "heaviest_4000_payload"):
        m = d["configs"][k]["mass_g"]
        rows = (m, m + d_fdm_solid, m + d_sls, m + (tot["q"] - tot["l"]))
        print(f"  {k:24s} " + " ".join(f"{g:7.0f} g {g / LB:5.2f}" for g in rows))
    print("  * 'SLS hull only' reproduces the 14.09 lbm figure used in plan 002: it omitted the"
          " nacelle printed parts.")
    print(f"\n  printed mass on the aircraft at 1.05: hull {tot['l']:.0f} g + nacelles {nac_l:.0f} "
          "g"
          f" = {tot['l'] + nac_l:.0f} g ({(tot['l'] + nac_l) / LB:.2f} lbm)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
