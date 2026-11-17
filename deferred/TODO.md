# Serenity UAV — Deferred Work (Phase 11+) TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"We will rise again. — Mr. Universe"*

---

## §Phase11 — Aft EDF Integration (Deferred)
→ full detail: `WBS.md` §Phase11

- [ ] Generate `rear_nozzle_canonical.scad`: fixed canonical elliptical…
- [ ] Generate `rcs_distribution_manifold.scad` + `rcs_thruster_nozzle.scad…
- [ ] Run mesh watertightness verification on all regenerated STLs
- [ ] Bench-test 55mm EDF (correct rotation, no vibration).
- [ ] Install EDF retaining ring at station ~430mm inside Panel F; bond
- [ ] Route motor leads through Panel F to 50A ESC
- [ ] Install 50A ESC in Panel F bay; foam tape + cable tie
- [ ] Bond `rear_nozzle_canonical.stl` to the tail-cone exit (Panel F aft…
- [ ] Install 4× `rcs_thruster_nozzle.stl` at their RCS stations
- [ ] Install 4× SG90-class proportional valves on `rcs_valve_bracket.stl`
- [ ] Calibrate RCS valves: 0% = closed (no bleed); 100% = full bleed jet
- [ ] Bond permanent aft 49 MHz (Part 15 §15.235) wire post to top of the…
- [ ] Remove temporary aft post from station ~580mm.
- [ ] Restring 49MHz top wire (~470mm) from forward post to nozzle aft…
- [ ] Enable ESC5 in FC2 firmware (PRU Ch.2); configure BDSHOT governor…
- [ ] GW-RCS — build the RCS valve gateway *(first build since 2026-11-16…
- [ ] Add the 4 RCS proportional-valve channels to the attitude-control…
- [ ] Add rear EDF to the forward-thrust (cruise) schedule
- [ ] Verify all 5 ESC heartbeats on CAN FD; confirm FC2 cross-drive…
- [ ] Bench-test RCS attitude authority; then forward-flight thrust test…
- [ ] All regenerated rear-EDF STLs pass mesh watertightness verification
- [ ] Plenum + RCS manifold pressure-test passed (draft at EDF inlet and…
- [ ] EDF seated at station ~430mm, centerline ±2mm
- [ ] 50A ESC installed; ESC5 signal routed to FC2 PRU Ch.2
- [ ] Canonical nozzle bonded flush to hull outer mold line
- [ ] All 4 RCS valves calibrated; pitch/yaw authority confirmed on bench
- [ ] 49MHz aft wire post on canonical nozzle; top wire re-strung at full…
- [ ] Forward-thrust test passed; rear EDF NOT used for hover lift
- [ ] All 5 ESC telemetry visible on CAN FD; ESC temps ≤70°C at cruise power

---
