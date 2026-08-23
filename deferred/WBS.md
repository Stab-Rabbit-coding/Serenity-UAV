# Serenity UAV — Deferred Work (Phase 11+) Work Breakdown Structure

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches root indexes below. Close an item here first, then check it off in the
> root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control"). **&#9733; = the branch is on the critical path to first flight (Phase 5).**

*"We will rise again. — Mr. Universe"*

---

## Owned WBS branches — open-item summary

| Master § | Branch | Open | First flight |
|----------|--------|-----:|:------------:|
| §Phase11 | Phase 11 — Aft EDF Integration (Deferred) | 42 | — |
| §Phase12 | Phase 12 — Cargo-bay Range-Extender Battery Module (Deferred) | 6 | — |
| | **Total open (this subsystem)** | **48** | |

---


> **Phase 12 (Range-Extender Battery Module)** rides in the cargo bay on the same Observer hooks/release and adds a `J_BATT2` input to Flight Engineer — a cruise-range, not hover, enhancement. See the Observer cross-cutting map in [avionics/observer/TODO.md](../avionics/observer/TODO.md).


## §Phase11 — Aft EDF Integration (Deferred)

*(root `WBS.md` §Phase11)*

- [ ] Print `rear_neck_intake_shell24.stl` from `deferred/aft-edf/openscad/rear_neck_intake_shell24.scad`. Verify NECK_X ≈ 310mm alignment in slicer. **Scoop windows must be re-sized for the 55 mm EDF (reduced area).**
- [ ] Remove temporary window covers from existing neck shell, or swap in the new windowed shell if a plain shell was used for Phases 0–10.
- [ ] **Regenerate** `neck_intake_frame.scad` for the 55 mm intake area; print `neck_intake_frame.stl` (CF-PETG, 0.15mm, 40% gyroid, 4 walls).
- [ ] **Regenerate** `aft_edf_plenum.scad`: 55 mm circular EDF inlet + 4 RCS bleed taps (~15% flow); print `aft_edf_plenum.stl` (CF-PETG, 0.20mm, 20% gyroid) — EDF housing, treated as structural per CLAUDE.md Fabrication Standards.
- [ ] **Generate** `rear_nozzle_canonical.scad`: fixed canonical elliptical tail nozzle, exit 2.06×1.76 in (52.3×44.7 mm, ~1,836 mm²), hull-matched outer surface; print `rear_nozzle_canonical.stl` (CF-PETG, 0.15mm, 30%, 4 walls). **No iris, no servo.**
- [ ] **Generate** `rcs_distribution_manifold.scad` + `rcs_thruster_nozzle.scad` + `rcs_valve_bracket.scad`; print `rcs_distribution_manifold.stl` (×1, PETG), `rcs_thruster_nozzle.stl` (×4, CF-PETG), `rcs_valve_bracket.stl` (×4, CF-PETG).
- [ ] Run mesh watertightness verification on all regenerated STLs; report findings here and resolve.
- [ ] Dry-fit `neck_intake_frame.stl` into the resized scoop windows; registration tongues insert with ~0.2mm clearance (sand if tight).
- [ ] Verify aerodynamic orientation: intake lips face forward (−Y / nose-ward).
- [ ] Apply structural epoxy to tongues + shoulder flanges; press frame into position; clamp; cure 24h.
- [ ] Fillet all gaps between flange and hull; cure 2h.
- [ ] Dry-fit `aft_edf_plenum.stl`; verify intake arm alignment and 55mm EDF inlet centered.
- [ ] Bond plenum forward arms to intake frame exits; fillet joints; cure 2h.
- [ ] Bond `rcs_distribution_manifold.stl` to the 4 plenum bleed taps; route 4 bleed ducts to the RCS jet locations.
- [ ] Pressure-test: seal EDF face with tape; cover all but one scoop; shop-vac — confirm draft at EDF inlet and at all 4 RCS jets, no joint leakage.
- [ ] Bench-test 55mm EDF (correct rotation, no vibration).
- [ ] Install EDF retaining ring at station ~430mm inside Panel F; bond; cure 1h.
- [ ] Seat EDF in plenum 55mm inlet; press forward to retaining lip; bond with 4 dabs slow-cure epoxy.
- [ ] Route motor leads through Panel F to 50A ESC; route signal lead forward via MAIN-PWR conduit to Inara's shuttle (Bay B, FC2 PRU Ch.2).
- [ ] Install 50A ESC in Panel F bay; foam tape + cable tie. Cure 2h before applying thrust.
- [ ] Bond `rear_nozzle_canonical.stl` to the tail-cone exit (Panel F aft end), blending into the canonical hull outer mold line. **Fixed — no moving petals.**
- [ ] Install 4× `rcs_thruster_nozzle.stl` at their RCS stations; connect each to its bleed duct.
- [ ] Install 4× SG90-class proportional valves on `rcs_valve_bracket.stl`; link each valve to its RCS bleed duct.
- [ ] Calibrate RCS valves: 0% = closed (no bleed); 100% = full bleed jet. Map 2 jets to pitch, 2 to yaw.
- [ ] Bond permanent aft 49 MHz (Part 15 §15.235) wire post to top of the canonical tail nozzle (5-min epoxy).
- [ ] Remove temporary aft post from station ~580mm.
- [ ] Restring 49MHz top wire (~470mm) from forward post to nozzle aft post with ~20g tension.
- [ ] Enable ESC5 in FC2 firmware (PRU Ch.2); configure BDSHOT governor for the 55mm EDF.
- [ ] Add the 4 RCS proportional-valve channels to the attitude-control mixer; calibrate pitch/yaw authority via `governor_cal.py`.
- [ ] Add rear EDF to the forward-thrust (cruise) schedule — NOT the hover lift mixer.
- [ ] Verify all 5 ESC heartbeats on CAN FD; confirm FC2 cross-drive capability for ESC5.
- [ ] Bench-test RCS attitude authority; then forward-flight thrust test with the rear EDF at 60% throttle.
- [ ] All regenerated rear-EDF STLs pass mesh watertightness verification
- [ ] Intake frame tongues fully seated in the resized scoop windows
- [ ] Plenum + RCS manifold pressure-test passed (draft at EDF inlet and all 4 RCS jets; no leakage)
- [ ] EDF seated at station ~430mm, centerline ±2mm; rotation verified before sealing
- [ ] 50A ESC installed; ESC5 signal routed to FC2 PRU Ch.2
- [ ] Canonical nozzle bonded flush to hull outer mold line; exit 2.06×1.76 in verified
- [ ] All 4 RCS valves calibrated; pitch/yaw authority confirmed on bench
- [ ] 49MHz aft wire post on canonical nozzle; top wire re-strung at full ~470mm span
- [ ] Forward-thrust test passed; rear EDF NOT used for hover lift; ESC temps ≤70°C
- [ ] All 5 ESC telemetry visible on CAN FD; ESC temps ≤70°C at cruise power


## §Phase12 — Cargo-bay Range-Extender Battery Module (Deferred)

*(root `WBS.md` §Phase12)*

- [ ] **RBM module:** 6S LiPo (matched 4000 mAh recommended) + BQ76930-class BMS + ideal-diode
    ORing output, in a tray retained by the same Observer cargo hooks/release (jettisonable),
    with a keyed XT60 pigtail.
- [ ] **Flight Engineer input:** add `J_BATT2` (XT60) + `F_BATT2` + an ideal-diode / current-share
    combiner (LTC4359- or LTC4370-class — a NEW part family) OR-combining `J_BATT`/`J_BATT2`
    into VBAT: hot-swap-safe across SoC mismatch, reverse-blocking so a faulted/absent RBM
    can't drain or back-feed the main pack. (Flight Engineer board revision — not yet in KiCad.)
- [ ] **Current sharing:** same pack model + matched-SoC at takeoff (or LTC4370 to force
    balanced sharing); simple diode-ORing alone lets the higher-SoC pack hog.
- [ ] **Firmware (`pwr_fault`):** add a second-pack context (V/I/SoC over the existing
    telemetry) + combiner PGOOD/fault logging; on RBM fault, isolate and continue on the main
    pack (RTH).
- [ ] **W&B:** add the RBM to the §14 moment table; re-balance on the keel rail and verify on
    the physical CG rig before flight (a second ~750 g mass in the cargo bay shifts CG).
- [ ] **CAD:** RBM tray + retention on the cargo-bay payload envelope; verify cargo-door and
    Observer clearances.
