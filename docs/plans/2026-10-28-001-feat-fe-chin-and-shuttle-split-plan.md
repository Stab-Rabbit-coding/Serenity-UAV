---
title: Flight Engineer Chin + Shuttle Split - Plan
type: feat
date: 2026-10-28
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
execution: code
---

# Flight Engineer Chin + Shuttle Split - Plan

**Author:** Claude (Claude Opus 5.5, Anthropic), under the direction of Stab-Rabbit-coding, per `AGENTS.md` §3.
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Related:** `docs/plans/2026-10-26-002-feat-fe-multi-battery-pdb-plan.md` (plan 002, circuit content); `docs/CG_RELOCATION_STUDY.md` (CG basis); `docs/plans/2026-10-27-001-feat-middle-rear-layout-plan.md` (superseded in part).

---

## Goal Capsule

- **Objective.** Re-package the Flight Engineer (FE) as a chin central board plus two mirrored shuttle daughter boards, so its mass and most of its heavy-gauge copper move toward the hover thrust line (nacelle pivot, R2 Y 326.7).
- **Product authority.** Owner decisions recorded below > `AGENTS.md` (datum R2, sourcing and NDA rules, standards vetting, material order) > plan 002 (what the FE must do electrically) > this plan (where and in what shape it lives).
- **Open blockers.** None for planning; the hover-current reconciliation (plan 002 U1) sizes the branch fuses and must land before layout.

---

## Product Contract

### Summary

Split the FE into three boards. The **chin central board** sits on the cargo chin floor between the two cells and carries the battery inputs, combiner, main protection, regulators, cell monitoring and trust module. Two **shuttle daughter boards**, one per side in the aft shuttle hollows, each carry their nacelle's two fused, monitored ESC branches with hard-soldered feeders. The chin node pair moves into the FE's old middle-neck slot.

### Problem Frame

The FE (225 g with its can) sits in the middle neck at Y 467.7, 141 mm aft of the pivot. With the rail-lever arrangement and the counted aft weight cuts the hover CG is still +13.6 mm aft of the thrust line (`docs/CG_RELOCATION_STUDY.md`). The routed harness carries about 301 g of 6 AWG battery leads and 10 AWG ESC feeders, all converging on the FE. Measured on 2026-10-28:

- **No free volume forward.** No FE-sized pocket exists forward: the head is full (Observer, Bay A, rail), and the pivot station is full (payload, cell band, tilt drive, cargo Observer).
- **The board is already double-sided.** `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_pcb` is 90 × 65 mm, 4 layers, 83 F.Cu + 70 B.Cu footprints, courtyard fill 66 % / 46 %. A single 84 × 58 mm chin board would run at 79 % / 56 % before plan 002 adds two more inputs, a third BEC and J_OBS, so one chin board cannot hold the content.
- **Mirrored daughter pockets clear only in the aft shuttle hollows.** That's Y ~374–434, about 60–85 mm aft of the pivot; the forward part holds the tilt drive and tilt-controller board.

### Key Decisions

- **Chin central board plus shuttle daughter boards.** (session-settled: user-directed — chosen over a single chin board and over a single chin board using ESC telemetry: the single board cannot hold the FE content.) Governs R1, R5, R7.
- **Hard-soldered ESC feeders.** (session-settled: user-directed — chosen over branch connectors rated for 57 A: removes the largest branch parts.) Governs R9.
- **Foil-pouch shielding.** (session-settled: user-directed — chosen over a low-profile formed can or board-level shielding only: fits the 22 mm chin height and saves most of the can's mass.) Governs R4, R8.
- **FE swaps places with the chin node pair.** (session-settled: user-approved — chosen over leaving the FE in the neck: frees the chin, and the node pair fits the neck slot.) Governs R2, R3.

### Requirements

**Placement and envelopes**

- R1. The chin central board fits the chin-floor envelope now held by nodes CN2/CN3 (about 84 × 58 × 22 mm including the pouch, Y 247.7–305.7, Z 146–168) and clears every gated solid in `tools/cargo_layout_fit.py`.
- R2. Nodes CN2 and CN3 relocate to the middle-neck slot the FE vacates and clear every gated solid in `tools/middle_layout_fit.py`.
- R3. The chin node move preserves those nodes' bus roles, termination and harness reach (`docs/AVIONICS_PB2_REDESIGN.md`).
- R4. Each shuttle daughter board fits a mirrored aft shuttle-hollow envelope (measured clear at 20 × 35 × 25 mm, X ±36 Z 190–215 or X ±51 Z 133–158, Y 386–406) including its pouch, port and starboard identical by mirror.
- R5. All three boards are placed R2 solids with installed-position STLs and pass the head, cargo and middle gates and the symmetry check.

**Electrical content**

- R6. Across the three boards the FE keeps every function plan 002 assigns it: three switchable reverse-blocking inputs, third-cell-first priority with a fail-safe pair default, per-input and main fusing, the 5 V rails (including RAIL-2 / J_OBS), the 6 V rail, cell monitoring and the trust module.
- R7. The chin central board carries the battery inputs, combiner, main fuse, main shunt, disconnect, regulators, cell monitoring and trust module; each daughter board carries its nacelle's two ESC branches (fuse plus current monitor per branch).
- R8. Each board is shielded by a foil pouch bonded to chassis PGND, accepted under the FE EMC pass (FE-CAN-05).
- R9. ESC feeders solder to the daughter boards; the battery inputs keep disconnectable connectors.
- R10. Each ESC branch is fused and conductor-sized for its worst-case current, taken from the reconciled hover current (plan 002 R9).

**Interconnect**

- R11. One high-current bus per side connects the chin board to its daughter board, sized for that side's two branches.
- R12. Branch current and fault telemetry from both daughter boards reaches `pwr_fault` on the chin board.

**Mass and balance**

- R13. The ledger carries all three boards and the moved nodes at their installed stations, and the routed harness is re-derived for the new endpoints; the hover CG improvement against the +13.6 mm baseline is reported.

### Acceptance Examples

- AE1. Covers R1, R4, R5. The cargo and middle gates pass with the three boards and the moved node pair in place, and the port/starboard daughter boards mirror within 0.5 mm.
- AE2. Covers R12. A simulated branch overcurrent on the starboard daughter board appears in `pwr_fault` telemetry and isolates only that branch.
- AE3. Covers R13. The ledger reports the hover CG, the harness mass and the moment change for the new arrangement.

### Scope Boundaries

- Out: circuit-level design (combiner parts, FET selection, hover-current reconciliation, per-pack monitoring), which is plan 002.
- Out: PCB routing and final placement; the owner places tightly packed boards by hand (avionics/AGENTS.md).
- Out: merging each daughter board with that side's tilt-controller board. Recorded as a later option.

#### Deferred for later

- Merged daughter-plus-tilt-controller boards (one board per side in the shuttle pocket).
- ESC current telemetry replacing the branch monitors.

### Outstanding Questions

#### Deferred to Planning

- How the 57 A rated-point branch current [REF-EDF-003] is handled once hover current is reconciled: carried continuously by the branch, or bounded by a stated throttle or time limit.

- Which daughter-board envelope and orientation to use (20 × 35 × 25 upright, 30 × 40 × 14 flat, or 12 × 45 × 35 on edge), decided by a branch footprint study once plan 002 U1 fixes the fuse and conductor sizes.
- How branch telemetry crosses to the chin board: the shared INA226 I²C bus run between boards, or a local bridge onto CAN.
- Service access to the chin board (doors open, cargo cell and payload out) and whether that is acceptable for routine maintenance.
