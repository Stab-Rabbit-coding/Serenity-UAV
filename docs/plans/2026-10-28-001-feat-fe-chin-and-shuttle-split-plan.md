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
**Related:** `docs/plans/2026-10-26-002-feat-fe-multi-battery-pdb-plan.md` (plan 002, circuit content); `docs/CG_RELOCATION_STUDY.md` (CG basis); `docs/plans/2026-10-27-001-feat-middle-rear-layout-plan.md` (superseded in part: its KTD1 and U3/U4, the second cell aft, were already void; this plan's R2 now shares Simon's middle-neck region with CN2/CN3, so that plan's node placements are re-checked under R3 and R19).

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
- **Mirrored daughter pockets clear only in the aft shuttle hollows.** That's Y ~374–434, about 47–107 mm aft of the pivot (the R4 envelope, Y 386–406, sits 59–79 mm aft); the forward part holds the tilt drive and tilt-controller board.

### Key Decisions

- **Chin central board plus shuttle daughter boards.** (session-settled: user-directed — chosen over a single chin board and over a single chin board using ESC telemetry: the single board cannot hold the FE content.) Governs R1, R5, R7.
- **Low-profile fuses off the chin board.** (session-settled: user-directed — chosen over keeping the 150 A MAXI holder on the board: it alone exceeds the chin height budget.) Governs R14, R15.
- **Hard-soldered ESC feeders.** (session-settled: user-directed — chosen over branch connectors rated for 57 A: removes the largest branch parts.) Governs R9.
- **Foil-pouch shielding.** (session-settled: user-directed — chosen over a low-profile formed can or board-level shielding only: fits the 22 mm chin height and saves most of the can's mass.) Governs R4, R8.
- **Node distribution is a planning factor, ranked below volume, mass, balance, controllability and stability.** (session-settled: user-directed — the nodes were intended to be spread through the aircraft to limit single points of failure.) Governs R19.
- **FE swaps places with the chin node pair.** (session-settled: user-approved — chosen over leaving the FE in the neck: frees the chin, and the node pair fits the neck slot.) Governs R2, R3.

### Requirements

**Placement and envelopes**

- R1. The chin central board's bare footprint fits the chin-floor area now held by nodes CN2/CN3 (about 84 × 58 mm, Y 247.7–305.7); the pouch adds height only, inside the Z span of R14 (Z 146 up to the rail); and the board clears every gated solid in `tools/cargo_layout_fit.py`.
- R2. Nodes CN2 and CN3 relocate to the middle-neck slot the FE vacates and clear every gated solid in `tools/middle_layout_fit.py`.
- R3. After the move, CN2 and CN3 keep their bus roles; each bus stub stays within its bus's limit and termination positions are unchanged or the change is stated, and the added harness mass counts in R13's estimate (`docs/AVIONICS_PB2_REDESIGN.md`).
- R19. Node placement keeps the control nodes as physically distributed as practical, to limit common-mode loss (one strike, fire or fluid ingress disabling several nodes). Volume, mass, balance, controllability and stability take precedence; distribution is weighed after them.
- R4. Each shuttle daughter board's content fits one of the measured mirrored clear envelopes in the aft shuttle hollow (best measured: 20 × 35 × 25 mm at X ±36 Z 190–215 or X ±51 Z 133–158, Y 386–406), confirmed by a branch termination study (bus landing, two feeder solder pads, two fuses, two shunts and monitors) before the envelope is gated.
- R18. If no measured envelope holds the R4 content, the branch fuses move into the feeders off the board (the R15 pattern) and the daughter boards carry only shunts and monitors.
- R14. Each board meets a height stack: pouch, tallest back-side part, PCB and tallest top-side part together fit the measured Z span of its envelope (the chin span is capped by the cell rail above, Z 166.35).
- R15. The main fuse and the per-input fuses use low-profile parts and mount off the chin board, inline in the battery leads or on the battery cradles, whichever fits best per input.
- R16. Every board holds its power parts within their rated temperatures, including fuse derating, at the reconciled continuous current, with a stated heat path (copper spreader to the chin floor or a cradle, or an air path); the dissipation budget per board is reported.
- R5. All three boards are placed R2 solids with installed-position STLs and pass the head, cargo and middle gates and the symmetry check.

**Electrical content**

- R6. Across the three boards the FE keeps every function plan 002 assigns it: three switchable reverse-blocking inputs, third-cell-first priority with a fail-safe pair default, per-input and main fusing, the 5 V rails (including RAIL-2 / J_OBS), the 6 V rail, cell monitoring and the trust module.
- R7. The chin central board carries the battery input landings, combiner, main shunt, disconnect, the dual 5 V avionics BECs, the RAIL-2 5 V BEC with J_OBS, the 6 V BEC, cell monitoring and the trust module; each daughter board carries its nacelle's two ESC branches (fuse plus current monitor per branch).
- R20. With the fuses and input connectors off the board (R9, R15) and the plan 002 additions included, the chin board's projected courtyard fill is at most 70 % per side, the existing FE's front-side fill being 66 %.
- R8. Each board is shielded by a foil pouch bonded to chassis PGND, accepted under the FE EMC pass (FE-CAN-05).
- R9. ESC feeders solder to the daughter boards; each battery input's disconnect sits with its fuse on the cradle or inline (R15), and its lead solders or lugs to the chin board, so the chin board carries no input connectors.
- R10. Each ESC branch is fused and conductor-sized for its worst-case current, taken from the reconciled hover current (plan 002 R9).

**Interconnect**

- R11. One high-current bus per side connects the chin board to its daughter board, sized for that side's two branches.
- R12. Branch current and fault telemetry from both daughter boards reaches `pwr_fault` on the chin board.

**Mass and balance**

- R13. Before layout work, a moment estimate (FE pieces, the moved node pair, pouches replacing the can, the side buses and the re-derived harness) shows the new hover CG at least 3.0 mm forward of the +13.6 mm baseline; if it does not, the split is reconsidered before any board is laid out.
- R17. The ledger carries all three boards and the moved nodes at their installed stations with the routed harness re-derived, and the final hover CG meets R13's margin.

### Acceptance Examples

- AE1. Covers R1, R4, R5. The head, cargo and middle gates pass with the three boards and the moved node pair in place, and the port/starboard daughter boards mirror within 0.5 mm.
- AE2. Covers R12. A simulated branch overcurrent on the starboard daughter board appears in `pwr_fault` telemetry and isolates only that branch.
- AE3. Covers R13, R17. The pre-layout estimate and the final ledger both put hover CG at least 3.0 mm forward of +13.6 mm, and report harness mass and moment change.
- AE4. Covers R3, R6, R19. With the three boards and the moved node pair wired, every plan 002 FE function passes its bench check, every bus stub is within its limit with termination as stated, and the node distribution is reported against R19.

### Scope Boundaries

- Out: circuit-level design (combiner parts, FET selection, hover-current reconciliation, per-pack monitoring), which is plan 002.
- Out: PCB routing and final placement; the owner places tightly packed boards by hand (avionics/AGENTS.md).
- Out: merging each daughter board with that side's tilt-controller board. Recorded as a later option.

#### Deferred for later

- Merged daughter-plus-tilt-controller boards (one board per side in the shuttle pocket).
- ESC current telemetry replacing the branch monitors.

### Outstanding Questions

#### Deferred to Planning

- Whether the logic/BEC functions and the power daughter boards need different protection: the logic side is EMC-dominated (switching regulators, trust module, isolated buses), the daughter boards heat-dominated (fuses, shunts at tens of amps). The pouch decision may hold for the chin board while the daughter boards trade some shielding for a heat path, within R8 and R16.

- Low-profile alternatives for the other tall parts (shunts, magnetics, connectors) that keep each board within R14.

- How the 57 A rated-point branch current [REF-EDF-003] is handled once hover current is reconciled: carried continuously by the branch, or bounded by a stated throttle or time limit.

- Which measured envelope and orientation the daughter board uses (the clear volumes also admit a 30 × 40 × 14 mm flat board at X ±54 Z 136–150 and a 12 × 45 × 35 mm on-edge board at X ±45 Z 130–165), decided by the R4 termination study once plan 002 U1 fixes fuse and conductor sizes.
- How branch telemetry crosses to the chin board: the shared INA226 I²C bus run between boards, or a local bridge onto CAN.
- Service access to the chin board (doors open, cargo cell and payload out) and whether that is acceptable for routine maintenance.
