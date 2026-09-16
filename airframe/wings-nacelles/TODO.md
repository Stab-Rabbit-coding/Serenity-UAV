# Serenity UAV — Airframe Wings and Nacelles TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"Curse your sudden but inevitable betrayal."*

---

## §1.1.2 — Wings
→ full detail: `WBS.md` §1.1.2

- [ ] ASTM D3039/D695 coupon test for the CF-PLATE-2MM bending allowable…
- [ ] SPAR-02 — bulkhead servo mounts: deconflicted, but the pad is…

##### 1.1.2.1 *Rev R1a — spar straightened + camber-centered + EDF cableway (2026-07-07)*
→ full detail: `WBS.md` §1.1.2.1

- [ ] Re-render and re-bake both wings (Rev S1b OML change)

##### 1.1.3.1 *Nozzle*
→ full detail: `WBS.md` §1.1.3.1

- [ ] [OPEN — VERIFY] Mass/CG impact of the shingle
- [ ] [OPEN — VERIFY] Seal-flap aerodynamic step
- [ ] [OPEN — NO-GO, was VERIFY] Spatial RSSR linkage synthesis
- [ ] [OPEN — IMPLEMENT] Adopted nozzle drive: wing-fixed sun + nacelle…
- [ ] Re-hub `spar_crank()` onto the pinion
- [ ] [BLOCKED — needs an owner decision, do NOT assume resolved] The KTD3…
- [ ] [OPEN — parked, do NOT print] `nacelle_nozzle_sync_gears.scad`
- [ ] Pushrod clearance/interference check
- [ ] [OPEN — ACCEPTED RESIDUAL, not fixable by boss sizing] Hinge bosses…
- [ ] Spar-crank placement in serenity_assembly.py is first-pass (Y=0…
- [ ] User WIP `gear_option_compare.scad` / `gear_shell_compare.scad`…

##### 1.1.3.3 *FreeCAD Hull-Frame Placement (gear train, nozzle, sleeves)*
→ full detail: `WBS.md` §1.1.3.3

- [ ] [OPEN — DESIGN] Nozzle drive protrudes ~10 mm past the nacelle OD…

##### 1.1.3.7 *Rev S4 — fixed-spar trunnion, skewer removal, print readiness*
→ full detail: `WBS.md` §1.1.3.7

- [ ] [OPEN — WA-R10] The 4 × 10 AWG disconnect route is UNBLOCKED but not…
- [ ] [OPEN — FLIGHT SAFETY, LG-HOVER-01] Hover ground clearance is still…
- [ ] [OPEN — VERIFY] `serenity_assembly.py` still places the deleted parts

##### 1.1.3.8 *Rev S4c — hinged ESC bays, access covers, 90° motor pattern*
→ full detail: `WBS.md` §1.1.3.8

- [ ] [OPEN — PRINT-BLOCKING] `MOTOR_BOLT_R` is still 10.0 mm and still…
- [ ] [OPEN — NEW, and it is a safety item] The bay is now an unfiltered…
- [ ] [OPEN — the flow, not the geometry] Bay velocity is not verified
- [ ] 50 A sustained is not survivable on any path evaluated
- [ ] [OPEN — WA-R10] The 4 × 10 AWG route now EXISTS but is not drawn
- [ ] Window structural allowance

##### 1.1.3.6 *Tilt-Angle Feedback — Hall Sensor at the Wing/Nacelle Joint*
→ full detail: `WBS.md` §1.1.3.6

- [ ] [OPEN — cross-subsystem, rescoped 2026-07-26] `Pilot.md` §13 /…
- [ ] AK7455 off-axis bench validation — confirm the ring presents 10–70…

## §1.1.4 — Tilt-Spar Migration (20 mm fixed CF spar, trunnion pivot, belt drive)
→ full detail: `WBS.md` §1.1.4

- [ ] SPAR-20-8 (U8) — Re-datum the nozzle drive onto the fixed trunnion…
- [ ] SPAR-20-9 (U9) — Mass/CG/T-W re-derive (spar 96.2 → 67.5 g/pair, but…
- [ ] NAC-MOULD-01 — nacelle mould-line conformance + nozzle shortening
- [ ] SPAR-20-AERO — The re-lofted section is no longer S1223 (root 12.1 →…
- [ ] SPAR-20-TSCALE — `s1223_section()` carries a note that `t_scale` was…
- [ ] SPAR-20-ALLOW — No verified CF tube flexural allowable exists in…
- [ ] SPAR-20-WIREOD — `bom_revS.csv` records no OD for `WIRE-10AWG`

## §1.1.5 — Nacelle Trunnion Pivot and Tilt Drive
→ full detail: `WBS.md` §1.1.5

- [ ] SPAR-25-5 (U5) — BLOCKED 2026-09-10 on an owner decision (§1.1.3.1…
- [ ] SPAR-25-6 (U6) — Integration, load check, mass/CG, BOM, and the…

---
