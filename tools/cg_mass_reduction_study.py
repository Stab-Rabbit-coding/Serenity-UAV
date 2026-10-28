#!/usr/bin/env python3
"""cg_mass_reduction_study.py -- rank mass reductions aft of the hover thrust
line (nacelle pivot, R2 Y 326.7) by pitch moment saved, reconcile the wiring
BOM against the routed harness, and report the cumulative CG.

Owner direction 2026-10-27: after the rail lever (+16.3 mm hover with the
routed harness, tools/cg_relocation_study.py) "cut weight aft first".

Every saving carries its basis: MEASURED (mesh / ledger), cited REF-ID, or
ASSUMED.  Nothing here edits the BOM or the layout tools.

Run:
    /usr/bin/python3 tools/cg_mass_reduction_study.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-10-27, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auw_ledger as al  # noqa: E402
import cg_relocation_study as crs  # noqa: E402
import head_layout_fit as hlf  # noqa: E402
import middle_layout_fit as mlf  # noqa: E402

PIVOT_Y = crs.PIVOT_Y
# Baseline: rail lever + routed harness (cg_relocation_study, commit 2c4ebb9f)
BASE_AUW_G = 6232.0
BASE_OFFSET_MM = 16.3
BASE_MOMENT = 101694.0  # g.mm, hover

# Skin plate deflection scales with t^-3 (plate bending); the 2.0 mm skin's
# figure, 0.054 mm at 28 m/s against a 0.5 mm limit, is recorded in
# head_shell24.scad's header from the 2026-05-26 structural analysis.
SKIN_DEFL_2MM, SKIN_DEFL_LIMIT = 0.054, 0.5
RHO_BRASS = 8.53  # g/cm^3, C26000 [REF-MAT-009]
RHO_AL = 2.70  # g/cm^3, 6061 [REF-MAT-007]; same figure as middle_layout_fit.can_mass()


def ledger_item(name_start):
    bom = al.bom_rows()
    base = al.printed_items() + al.nacelle_items() + al.station_items(bom) + al.gap_items()
    hits = [i for i in base if i.name.startswith(name_start)]
    m = sum(i.m for i in hits)
    return m, sum(i.m * i.cg[1] for i in hits) / m


def opportunities():
    rows = []

    def add(name, dm, y, basis, risk, take=True):
        rows.append(dict(name=name, dm=dm, y=y, mom=dm * (y - PIVOT_Y), basis=basis,
                         risk=risk, take=take))

    m, y = ledger_item("rear_shell24")
    for t, take in ((1.6, True), (1.2, False)):
        dm = m * (1 - t / 2.0)
        defl = SKIN_DEFL_2MM * (2.0 / t) ** 3
        add(f"rear shell wall 2.0 -> {t} mm", dm, y,
            f"mass MEASURED {m:.1f} g, scaled with wall (ASSUMED linear); skin deflection "
            f"{defl:.3f} mm vs {SKIN_DEFL_LIMIT} mm limit (t^-3 from the 2.0 mm figure)",
            "keep 2.0 mm at the skid-rod channels, ring pocket and collar lands; "
            + ("4 perimeters at 0.4 mm" if t >= 1.6 else
               "3 perimeters: handling/impact risk, print trial first"), take)
    m, y = ledger_item("middle_shell24")
    add("middle shell wall 2.0 -> 1.6 mm (skin panels only)", m * 0.2 * 0.5, y,
        f"mass MEASURED {m:.1f} g; half the shell is horseshoe ring/legs/hatch frame kept at "
        "2.0 mm (ASSUMED 50 % panel area)", "skid arms and hatch frame stay; verify panel area "
        "on the mesh before cutting")
    plate_brass = mlf.M_FE_PLATE * 0.8  # ASSUMED 80 % of the 25 g (ASSUMED) is the brass plate
    add("FE entry plate brass -> 6061-T6", plate_brass * (1 - RHO_AL / RHO_BRASS),
        0.5 * (mlf.FE_PLATE_Y0 + mlf.FE_PLATE_Y1),
        f"plate 25 g ASSUMED (middle_layout_fit M_FE_PLATE), brass share 80 % ASSUMED; "
        f"density ratio {RHO_AL}/{RHO_BRASS} [REF-MAT-007, REF-MAT-009]",
        "material order prefers Al over brass (AGENTS.md); conductive EMC entry plate "
        "keeps its bushings. FE UNDER STUDY (coordinator): not counted", take=False)
    can = mlf.can_mass()
    add("FE can 0.5 -> 0.3 mm 6061", can * (1 - 0.3 / mlf.FE_WALL),
        0.5 * (mlf.FE_CAN_Y0 + mlf.FE_CAN_Y1),
        f"can {can:.1f} g from middle_layout_fit.can_mass() (0.5 mm wall)",
        "absorption at the buck switching frequency halves again; WBS FE-CAN-05 EMC pass must "
        "accept it. A printed shell + 0.1 mm foil saves nothing (~30 g). FE UNDER STUDY "
        "(coordinator): not counted", take=False)
    m, y = ledger_item("Cargo Observer")
    add("cargo Observer -> remote camera head off the nose Observer", m - 5.0, y,
        "60 g ESTIMATE (ledger, no BOM row); remote head 5 g ASSUMED",
        "functional change, owner decision: MIPI CSI-2 over ~0.4 m needs a SerDes or a "
        "second Observer port; stereo-baseline cargo imager (OBSERVER_LASER_ANALYSIS §4.5) "
        "would be lost", take=False)
    # ledger correction (not a cut): ferrites at their node sites
    sites = (crs.BAYA_Y, 276.7, 416.2, 494.7)
    yd = sum(sites) / len(sites)
    rows.append(dict(name="ledger correction: FAR-FERRITE-4MM at the node sites", dm=0.0,
                     y=yd, mom=80.0 * (365.7 - yd),
                     basis="80 g BOM; ledger lumps them at Y 365.7 (ESTIMATE); 4 sites "
                           "(Bay A, chin, aft, Simon) equal shares",
                     risk="none (bookkeeping). Count unchanged: their basis was '4 per cage', "
                          "cages are now foil pouches -- EMC pass to decide",
                     take=True, correction=True))
    return rows


def wiring_bom():
    """Routed runs vs the two BOM rows (rail lever, FE at its ledger station)."""
    g6, g10 = crs.awg_g_per_mm(6), crs.awg_g_per_mm(10)
    fe_y = 467.7 - (mlf.FE_CAN_Y + mlf.FE_PLATE_Y) / 2
    fz = mlf.FE_ZC
    runs = []
    for nm, y1 in (("head cell", crs.HEAD_CELL_Y0 + hlf.CELL_L), ("cell 2", crs.CELL2_Y1)):
        L = (abs(fe_y - y1) + abs(fz - hlf.BAND_ZC)) * crs.ROUTE_SLACK
        runs.append(("WIRE-6AWG", f"{nm} -> FE, red + black", 2, L, g6))
    for side, (px, py, pz) in al.PIVOT.items():
        L = (abs(fe_y - py) + abs(px) + abs(fz - pz)) * crs.ROUTE_SLACK
        runs.append(("WIRE-10AWG", f"FE -> {side} nacelle ESCs (2), red + black", 4, L, g10))
    t3 = (abs(fe_y - al.PAYLOAD_ST[0][1]) + abs(fz - al.PAYLOAD_ST[0][2])) * crs.ROUTE_SLACK
    runs.append(("WIRE-6AWG-T3 (new)", "third cell (payload bay) -> FE J_BATT3", 2, t3, g6))
    return runs


def main():
    print(f"baseline (rail lever, routed harness): AUW {BASE_AUW_G:.0f} g, hover offset "
          f"{BASE_OFFSET_MM:+.1f} mm, moment {BASE_MOMENT:,.0f} g.mm\n")
    print("(1) WIRING BOM RECONCILIATION")
    print("    BOM now: WIRE-6AWG 60 g ('200 mm each red/black', single pack); WIRE-10AWG 80 g "
          "('1 m each red/black')")
    print(f"    bare copper alone: 10 AWG {crs.awg_g_per_mm(10) / crs.INSUL_FACTOR * 1000:.1f} g/m"
          f" -> 2 m = {crs.awg_g_per_mm(10) / crs.INSUL_FACTOR * 2000:.0f} g > the 80 g row")
    tot = {}
    for ref, what, n, L, g in wiring_bom():
        m = n * L * g
        tot[ref] = tot.get(ref, 0.0) + m
        print(f"    {ref:20s} {what:44s} {n} x {L:4.0f} mm = {n * L / 1000:.2f} m  {m:5.0f} g")
    for ref, m in tot.items():
        print(f"    proposed {ref:20s} total {m:5.0f} g ({m / 28.3495:.1f} oz)")
    print("    (6 AWG 160 g/m, 10 AWG 63 g/m: ASTM B258 diameter + Cu 8.89 g/cm3 REQUIRES "
          "VERIFICATION; +35 % insulation and 10 % slack ASSUMED)\n")
    print("(2) MASS REDUCTION AFT OF THE PIVOT, by moment saved")
    rows = sorted(opportunities(), key=lambda r: -r["mom"])
    for r in rows:
        tag = "CORRECTION" if r.get("correction") else ("TAKE" if r["take"] else "NOT COUNTED")
        print(f"  [{tag:10s}] {r['name']:58s} -{r['dm']:5.1f} g ({r['dm'] / 28.3495:.2f} oz) "
              f"at Y {r['y']:5.1f}  moment -{r['mom']:7,.0f} g.mm")
        print(f"      basis: {r['basis']}\n      risk:  {r['risk']}")
    print("  not proposed: harness gauge (no cited ampacity in REFERENCES.md; each 10 AWG "
          "feeder carries one ESC, 57.0 A at the QF2822 rated point [REF-EDF-003]); landing "
          "gear aft items (LG-LOADPATH open); node boards, pouches, bond straps (EMC); "
          "CF ring/thwart and collars (structural)\n")
    print("(3) CUMULATIVE")
    m_tot, mom_tot = BASE_AUW_G, BASE_MOMENT
    for r in rows:
        if not r["take"]:
            continue
        m_tot -= r["dm"]
        mom_tot -= r["mom"]
        print(f"  after {r['name']:58s} offset {mom_tot / m_tot:+6.2f} mm  AUW {m_tot:6.0f} g")
    r16 = next(r for r in rows if r["name"].endswith("1.6 mm"))
    for r in rows:
        if r["take"]:
            continue
        dm, dmom, verb = r["dm"], r["mom"], "also"
        if r["name"].endswith("1.2 mm"):  # alternative to 1.6 mm: count the increment only
            dm, dmom, verb = dm - r16["dm"], dmom - r16["mom"], "instead of 1.6 mm"
        print(f"  ... with {r['name']} {verb}: offset "
              f"{(mom_tot - dmom) / (m_tot - dm):+.2f} mm")
    nac = sum(i.m for i in al.nacelle_items())
    f = nac / m_tot
    off = mom_tot / m_tot
    ballast = mom_tot / (PIVOT_Y - 15)
    print(f"\n  residual {mom_tot:,.0f} g.mm: nose ballast at Y 15 {ballast:.0f} g,"
          f" or pivot move {off / (1 - f):.1f} mm aft (nacelle fraction {f:.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
