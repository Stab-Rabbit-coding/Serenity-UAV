---
title: Split Battery, Head Rail and Head-Section Audit - Plan
type: feat
date: 2026-10-26
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-plan-bootstrap
execution: code
---

# Split Battery, Head Rail and Head-Section Audit - Plan

**Author:** Claude (Claude Opus 5.5, Anthropic), under the direction of Stab-Rabbit-coding, per `AGENTS.md` §3.
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Companion plan:** `docs/plans/2026-10-26-002-feat-fe-multi-battery-pdb-plan.md` (Flight Engineer PDB and power harnesses).

---

## Goal Capsule

- **Objective.** Replace the single 6S 4000 pack, which does not fit the cargo roof band, with two matched 6S 2200 cells: one in the existing cargo cradle and one in the head. The head cell rides a rail that extends the cradle through the head/cargo collar. Add an optional third cell in the payload box for extended flight. Audit and rebuild the head section so its contents are real solids that the gates check.
- **Authority.** Owner decisions recorded below > `AGENTS.md` (datum R2, standards vetting, sourcing, material order) > this plan > `docs/BATTERY_SPLIT_OPTIONS.md` (the trade this plan executes).
- **Stop conditions.** Stop and report if the head bay cannot hold the cell and its rail with the harness channel clear, if the cradle rail cannot pass the collar without cutting a structural ring, or if a gate shows a new clash that the plan cannot resolve at a shared parameter.
- **Tail ownership.** The executor commits per unit. The companion plan owns all electrical work (inputs, combiner, fuses, connectors, harness conductors).

---

## Product Contract

### Summary

Two matched cells in parallel replace one pack that cannot fit. The head cell moves the CG forward (+22.6 → about +14.3 mm behind the hover thrust line). It is serviced through the open cargo doors, so the head shell gets no new opening. A third cell can replace the cargo payload when endurance matters more than payload.

### Problem Frame

The verified Admiral Pro 6S 4000 (139 × 44 × 48 mm) fouls the cargo shell by 2,712–5,828 mm³ in either orientation (WBS BATT-02). The cargo roof band is 142 × 50 × 38 mm between the tilt brackets, the payload and the roof. The head has free volume (Y 110–232), but its contents are not modelled: the nose Observer board, the pitot line, camera, ToF and laser bores, node A and the nose avionics harness trunk exist only in documents or legacy-frame SCAD.

### Requirements

**Cells and placement**

- R1. The main supply is two matched 6S 2200 mAh cells of the same model, one in the cargo cradle and one in the head.
- R2. Each cell has a cited, live listing. The baseline is the Tattu R-Line 6S 2200 95C (116 × 34 × 38.5 mm, 321 g). A non-PRC equivalent is evaluated before purchase.
- R3. The cargo cell fits the existing cradle envelope (142 × 50 × 38 mm) on its side (34 mm vertical, 38.5 mm lateral) with no change to the cargo layout stations.
- R4. The head-cell station is the cell plus its sled and the stop/catch stack, forward of the collar (provisional Y about 105–235, fixed by U5), clear of the head contents and of the harness channel.

**Rail, stop, catch and sled**

- R5. The cradle is extended forward as a rail through the head/cargo splice collar into the head. Both cells ride it.
- R6. The head cell is inserted and removed through the open cargo doors only, using a sled with a pull lanyard. No new opening is made in the head shell.
- R7. A forward stop and a positive catch hold the head cell under the crash case. The catch shall not depend on the cargo cell behind it. The design load factor is **79.4 g** in every direction. That is the landing gear's peak hull deceleration for the adopted 4 ft (1.219 m) drop, level attitude, on the 3.0 in flight-article gear (`docs/LANDING_GEAR_ANALYSIS.md` §Rev R6 table, "Peak decel, 4 ft tail-down / level" = 39.7 g / 79.4 g; LG-17 closed 2026-08-09). The cell's inertial load is therefore about 56.2 lbf (250 N) at 321 g (0.708 lbm), before the U-unit FOS 3.0. The gear figure is vertical; the forward direction takes the same value as a declared bounding assumption, because the gear analysis gives no forward figure. Re-check this figure after LG-LOADPATH is decided, because that changes the wire plateau force (owner decision 2026-10-26).
- R8. Printed parts follow the owner's material order: printable composite first, then pre-cut composite, then metal only where a cited allowable requires it.

**Optional third cell**

- R9. An optional third cell (baseline Tattu R-Line v6.0 6S 1600 160C, 70 × 42 × 41 mm, 240 g) fits the payload keep-out (76.2 × 101.6 × 76.2 mm) and takes the place of the mission payload.
- R10. The third cell is retained by the payload hooks and release and is never carried together with a mission payload. It is non-jettisonable until the companion plan delivers the breakaway connector and the isolate-before-release sequence (companion U4, U5).

**Head-section audit and update**

- R11. Every head item is a placed R2 solid: the shell, the nose Observer board and its standoffs, the camera, ToF and laser bodies and bores, the pitot tube and line, node A (Bay A), the harness trunk channel, the head cell and the rail.
- R12. The head shell SCAD is migrated from its legacy axis frame to the R2 aircraft datum.
- R13. The head passes the joint census, the placement audit and a head context check with no unregistered clash and no port/starboard desync.
- R14. The mass ledger, BOM and assembly carry the new cells, rail, sled and catch at their installed stations.

**Air path and line of sight**

- R15. The pitot line and static port are air-path keep-out solids. The camera, ToF and laser have line-of-sight keep-outs through their apertures. Neither may be crossed by the rail, cell or harness.

> **WARNING**
>
> A loose LiPo in a crash can be punctured and burn. The head-cell catch is the only
> thing holding the cell off the nose avionics. It shall be sized to the
> crash load factor in R7 (79.4 g, from the gear design), not to a lower figure.

### Acceptance Examples

- AE1. Covers R6, R7. With the doors open and the payload and cargo cell removed, the head cell slides from the door opening to the stop and latches. A pull on the lanyard releases the catch and returns it.
- AE2. Covers R9, R10. The third cell occupies the payload hooks, so a mission payload has no hook to load on; the census flags the two together and reports the third cell inside the payload keep-out.
- AE3. Covers R4, R15. The head cell, rail and harness channel show zero clash against the Observer pocket, the pitot keep-out and the optical keep-outs.

### Scope Boundaries

- Electrical design (inputs, combiner, fuses, connectors, conductor gauge and routing) belongs to the companion plan. This plan reserves the harness channel and lead routing volume only.
- Gear work (LG-LOADPATH, the fuse) and F2 are out of scope.

#### Deferred to Follow-Up Work

- Physical weighing of a cell (BATT-01) and the bench C-rating test happen at procurement.

### Open Questions

- Q1 (deferred). Third-cell jettison: keep it non-jettisonable, or enable jettison once the companion plan's breakaway connector and isolate-before-release sequence exist?
- Q2 (resolved 2026-10-26, owner). Use the gear design's crash deceleration: 79.4 g (4 ft, level, 3.0 in gear), applied in every direction; see R7.
- Q3 (deferred). Minimum hover mission time that the split configuration must meet.

---

## Planning Contract

### Key Technical Decisions

- KTD1. Split the main pack into two matched cells, cargo plus head, in parallel. (session-settled: user-directed — chosen over a single low-profile pack: no verifiable thin 6S 4000 exists, and the split also moves the CG forward.)
- KTD2. Swap the head cell through the cargo doors on a rail extending the cradle. (session-settled: user-directed — chosen over a new head belly panel: no new hull opening.)
- KTD3. Migrate the head shell SCAD to the R2 datum as part of the audit. (session-settled: user-approved — chosen over modelling head contents as separate solids beside the legacy shell: only a migrated shell can be gated.)
- KTD4. Keep the Tattu baseline, but evaluate a non-PRC equivalent before purchase. (session-settled: user-approved — chosen over excluding Tattu outright: `AGENTS.md` §5 governs semiconductors, not cells.)
- KTD5. The head cell slides on its side (38.5 mm wide, 34 mm tall) inside a 40 × 36.5 mm box (0.75 mm lateral and 1.25 mm vertical clearance per side), centred on X 0. The box centre may sit anywhere from Z 169 to Z 187. Measured 2026-10-26 against the head shell, collar, cargo shell, cradle, chin shelf and tilt brackets for **Y 200–328 only**. Y 110–200 is provisional until U2 re-measures it against the R2 head solids.
- KTD6. The rail is the cradle's inverted U carried forward. Rail stations come from `tools/cargo_layout_fit.py` (single source). The cradle SCAD reads them; nothing is typed twice.
- KTD7. The catch is a sprung printed detent at the stop, released by the lanyard. A metal spring is used only if no printed spring meets R7 with a cited allowable.

### High-Level Technical Design

```mermaid
flowchart LR
    D[Open cargo doors<br/>payload out] --> C[Cargo cell out<br/>cam straps]
    C --> S[Head cell on sled<br/>lift into bracket gap]
    S --> R[Slide forward on rail<br/>through collar]
    R --> K[Stop + catch latch<br/>Y 110]
    K --> B[Cargo cell back<br/>in cradle]
    B --> P{Extended flight?}
    P -- yes --> T[Third cell on payload hooks]
    P -- no --> M[Mission payload on hooks]
```

### Sequencing

Head geometry first (U1–U3), then the rail and catch (U4–U5), then the cells and third cell (U6), then mass and gates (U7).

### Risks

- The head harness trunk (Ethernet, CAN) may need the same Z band as the rail at the collar. Mitigation: U3 sizes the trunk channel before U4 draws the rail.
- The head shell SCAD migration may expose the head reproducibility defect recorded in the R2 handoff (the published head lacks 3,517 mm³ in the nose). Mitigation: U1 reconciles against the published head before anything is regenerated.

---

## Implementation Units

### U1. Migrate the head shell to the R2 datum

**Goal:** The head shell SCAD and its build tool produce the published head in the R2 frame.
**Requirements:** R12.
**Dependencies:** none.
**Files:** `airframe/openscad/fuselage/head_shell24.scad`, `tools/build_head_shell.py`, `airframe/openscad/fuselage/bow_sensor_pod.scad`, `airframe/openscad/fuselage/access_panels_24in.scad`.
**Approach:**
1. Express every head station through `hull_datums.scad`; remove the legacy Y-as-dorsal axis frame (`TODO.md` §1.1.1 head/middle axis-bug items).
2. Reconcile against the published `head_shell24_2mm_repaired.stl` before regenerating; record the 3,517 mm³ nose difference and its cause.
3. Keep bow-pod part-local constants as a documented part-local exception, placed by one R2 transform.
**Patterns to follow:** the cargo shell R2 migration (`docs/handoffs/2026-10-20-aircraft-datum-r2-migration.md`).
**Test scenarios:**
- The regenerated head matches the published head within shell noise, or the difference is explained.
- `tools/check_datum_drift.py` passes with no new exemptions.
- `tools/verify_bow_pod.py` passes in R2.
**Verification:** drift gate PASS; head bounds equal the published head bounds.

### U2. Model the head contents as R2 solids

**Goal:** Every head item in R11 is a placed solid with its keep-outs, so the AE3 clash checks are meaningful.
**Requirements:** R11, R15.
**Dependencies:** U1.
**Files:** a new `tools/head_layout_fit.py` (single source of head stations, mirroring `tools/cargo_layout_fit.py`), a new `tools/head_bulkhead_context.py` (the head context check, modelled on `tools/cargo_bulkhead_context.py`), `airframe/FreeCAD-scripts/serenity_assembly.py`, `avionics/kicad/Observer/Observer.md`.
**Approach:**
1. Place the nose Observer board (25.4 × 69.85 mm) on standoffs aft of the bow faceplate, per `Observer.md` "Nose install".
2. Add camera, ToF and laser bodies and their line-of-sight cones through the apertures.
3. Add the pitot tube and line as an air-path keep-out to its sensor.
4. Place node A (Bay A) from its current ledger station.
5. Build the head context check and re-measure the KTD5 sliding band for Y 110–200 against the R2 head solids. If it does not clear, stop (Goal Capsule stop condition) before U3.
**Test scenarios:**
- Each solid is watertight and placed inside the head shell (placement audit CONTAIN).
- The optical keep-outs pass through their apertures with zero shell clash.
- The pitot keep-out is continuous from the tube to the sensor.
- The KTD5 band is clear for Y 110–200, or the stop condition fires.
**Verification:** placement audit PASS for every head part.

### U3. Size the head harness trunk channel

**Goal:** A reserved channel carries the nose avionics trunk aft past the head cell and through the collar.
**Requirements:** R4, R11.
**Dependencies:** U2.
**Files:** `tools/head_layout_fit.py`.
**Approach:** Route the trunk outside the KTD5 sliding band, with bend radius and service loop. Reserve a second route volume for the head cell's power lead to the collar. The companion plan sizes that lead.
**Test scenarios:**
- The trunk channel has zero clash with the rail sliding band at every station.
- The channel passes the collar opening.
**Verification:** head context check reports the trunk channel clear.

### U4. Extend the cradle into a rail through the collar

**Goal:** The cradle continues forward as a rail to a stop at Y 110.
**Requirements:** R5, R8.
**Dependencies:** U3.
**Files:** `airframe/openscad/fuselage/cargo/battery_cradle.scad`, `tools/cargo_layout_fit.py`, `airframe/stls/fuselage/cargo/battery_cradle.stl`, new head rail STL.
**Approach:**
1. Add rail stations to `tools/cargo_layout_fit.py`; the SCAD reads them (KTD6).
2. Split the rail at the collar into cargo and head pieces that key across the joint.
3. Bond the head piece to the head shell; it must not load the collar.
**Test scenarios:**
- The rail clears the collar, chin shelf and tilt brackets.
- The KTD5 sliding band is unobstructed from Y 328 to Y 110.
- Port and starboard symmetry SYNC.
**Verification:** cargo layout fit and bulkhead census show no new clash.

### U5. Design the stop, catch and lanyard sled

**Goal:** The head cell latches at the stop and releases by lanyard.
**Requirements:** R6, R7, R8.
**Dependencies:** U4.
**Files:** new `airframe/openscad/fuselage/head_cell_catch.scad`, a new statics section in `docs/BATTERY_MOUNT.md`.
**Approach:**
1. Size the catch for R7 at FOS 3.0 against cited CF-PETG data [REF-MAT-001 / REF-MAT-002].
2. Sled: a printed carrier with a pull tab and lanyard routed back to the door opening.
**Test scenarios:**
- Catch holds 3.0 × 15.7 N on cited allowables.
- Release force at the lanyard is below a one-hand pull, with the value recorded.
- The sled passes the KTD5 band through its whole travel.
**Verification:** statics recorded; geometry clears in the head context check.

### U6. Place the cells and the optional third cell

**Goal:** Cells are placed solids at their installed stations; the third cell is a payload-bay alternate.
**Requirements:** R1, R2, R3, R9, R10.
**Dependencies:** U5 for the head cell only; the cargo cell, third cell and listings need none.
**Files:** `tools/cargo_layout_fit.py`, `tools/cargo_bulkhead_context.py`, `airframe/FreeCAD-scripts/serenity_assembly.py`, `REFERENCES.md`.
**Approach:**
1. Cargo cell inside the existing cradle envelope with a shim (no station change).
2. Head cell at the stop.
3. Third cell as an alternate payload solid with a census rule that the payload and third cell are never both present.
4. Catalogue each cell listing in `REFERENCES.md` and record the non-PRC equivalent evaluation.
5. Reserve lead route volumes from the cargo cradle and from the payload bay to the Flight Engineer; these, with U3's head-lead route, are the companion plan's U4 inputs.
**Test scenarios:**
- Covers AE2. Payload and third cell present together is flagged.
- Third cell inside the payload keep-out.
- Cargo cell inside the cradle.
**Verification:** layout fit and census PASS for both payload configurations.

### U7. Mass, balance, gates and close-out

**Goal:** Ledger, BOM and gates reflect the new arrangement.
**Requirements:** R13, R14.
**Dependencies:** U6.
**Files:** `tools/auw_ledger.py`, `current-specification/auw_ledger.json`, `current-specification/bom_revT.csv`, `current-specification/bom_revT.json`, `WBS.md`, `airframe/fuselage-mid/WBS.md`.
**Approach:** Ledger configs `hover_split`, `extended_third_cell` and `heaviest_payload`. Run export, census, placement audit, bulkhead context and layout fit.
**Test scenarios:**
- Ledger CG and T/W match the options study within the rail and catch mass.
- BOM CSV and JSON parity holds.
- Hover endurance for the split and third-cell configurations, at the companion plan's reconciled hover current, meets a stated minimum mission time (owner to set).
**Verification:** all gates PASS or carry only registered pre-existing items; WBS BATT-02 closed.

---

## Verification Contract

- `/usr/bin/python3 tools/check_datum_drift.py` → PASS.
- `freecadcmd tools/export_assembly_meshes.py -- DIR`, then `tools/airframe_interface_census.py DIR --json` and `tools/placement_audit.py DIR` → no new CLASH or FAIL.
- `/usr/bin/python3 tools/cargo_layout_fit.py`, `tools/cargo_bulkhead_context.py` and the new head context check → no new foul, no DESYNC.
- `/usr/bin/python3 tools/auw_ledger.py --write` → PASS; BOM parity via the repo's edit-script pattern.

## Definition of Done

- Head shell in R2; every head item a placed solid with keep-outs.
- Rail, stop, catch and sled designed, exported and gated; the head cell swaps through the cargo doors per AE1.
- Cells and the optional third cell placed, catalogued and in the ledger and BOM.
- All gates pass with only registered pre-existing items; WBS updated; abandoned-attempt geometry removed.
