---
title: Cargo-Ramp Intake, Tail EDF Cooling and Forward Relocation - Plan
type: feat
date: 2026-11-15
topic: ramp-intake-edf-cooling
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
execution: code
---

# Cargo-Ramp Intake, Tail EDF Cooling and Forward Relocation - Plan

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (owner; every product decision below is his). Requirements drafted by Claude (Anthropic) under the author's direction, using the `ce-brainstorm` skill, per `AGENTS.md` §3. AI-generated and not yet reviewed.
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Target repo:** `Serenity-UAV`. All paths are relative to that repo.
**Source issue:** GitHub issue #290, "fuselage cooling", and the owner's direction of 2026-11-15.

> **WARNING — engineering review required.** Every figure in this document is a planning estimate. A qualified engineer shall review and accept the analysis that follows from it before it is applied to flight hardware.

---

## Goal Capsule

- **Objective.** Make the tail EDF the fuselage's air mover from the first build. It draws all its air through the fuselage interior, by way of a louvred cargo ramp and the bow inlets. Move mass forward into the freed cargo bay so that the trim closes.
- **Product authority.** The owner (Stab-Rabbit-coding). His decisions of 2026-11-15, recorded under Key Decisions, override anything else here.
- **Supersedes.** The fan stage, fan adapter, intake covers, rear-bell intakes and baffled insert of `docs/plans/2026-11-15-001-feat-fuselage-cooling-plan.md`.
- **Open blockers.** None blocks planning. Three questions are deferred to planning with a stated default.

---

## Product Contract

### Summary

The tail EDF flies from the first build and is the only air mover in the fuselage. All its air passes through the interior: most enters at a louvred, screened forward cargo ramp, and the rest enters at the bow inlets that feed Bay A. The cargo bay becomes a sealed duct with one belly service hatch. Cargo moves to an external sling on a floor-mounted winch, with the line leaving the belly under the tilt pivot. The Flight Engineer box, winch, tail EDF speed controller, battery, RCS servos and Cargo Observer move forward to recover trim.

### Problem Frame

The measured thermal baseline shows that a small tail fan moves enough bulk air but too little local air: three nodes fail the average-power case. Two of them, the chin nodes, sit directly behind the forward cargo ramp, which is sealed today.

The earlier plan gave the tail EDF its own intakes in the rear bell and metered a small bleed of cooling air through a baffle. Almost all EDF air then bypassed the avionics.

The aircraft is aft-heavy. The hover CG is at station Y 351.2, which is 0.46 in (11.8 mm) aft of the tilt pivot at Y 339.4. Flying the EDF and RCS hardware from the first build adds an estimated 0.58 lbm (262 g) aft and moves the CG a further 0.35 in (8.8 mm).

Internal cargo occupies the centre of the fuselage, which is the only place where heavy boxes can move forward.

### Key Decisions

- KD1. **The forward cargo ramp is the tail EDF's main intake.** (session-settled: user-directed, 2026-11-15 — chosen over intake holes in the rear bell: all EDF air then cools the interior.) Governs R1, R2, R5.
- KD2. **The bow inlets stay, in parallel with the ramp.** (session-settled: user-directed, 2026-11-15 — chosen over a separate Bay A fan, ducting ramp air forward, and moving the Bay A nodes aft: Bay A sits upstream of the ramp and would get no air.) Governs R3.
- KD3. **There is no fan stage.** The tail EDF flies from the first build. (session-settled: user-directed, 2026-11-15 — chosen over a ramp cover with the Delta fan, and over an open ramp with a metering insert.) Governs R1, R8.
- KD4. **On the ground the EDF idles and the aircraft is restrained.** (session-settled: user-directed, 2026-11-15 — chosen over a ground cooling cart, a power-on time limit, and a standby fan.) Governs R9.
- KD5. **The cargo doors are fused shut, with one bolted belly service hatch.** There is no internal cargo. (session-settled: user-directed, 2026-11-15 — chosen over bolted door panels and over sealed actuated doors.) Governs R11, R12.
- KD6. **The ramp is a louvred panel on its canon outline, with a screen behind it.** (session-settled: user-directed, 2026-11-15 — chosen over a ramp lowered as a scoop and over a plain open hole.) Governs R5, R6.
- KD7. **The winch sits on the cargo floor, with its motor as far forward as it fits.** The load line leaves the belly under the tilt pivot. (session-settled: user-directed, 2026-11-15 — chosen over a fairlead under the empty hover CG: a slung load then pulls the CG toward the pivot and adds no pitching moment in hover.) Governs R13, R14, R15.
- KD8. **RCS is populated in the first build.** (session-settled: user-directed, 2026-11-15 — chosen over capped stubs with empty mounts, and over dropping RCS.) Governs R16, R17.
- KD9. **Priority when the intake limits the EDF: cooling, then RCS, then thrust.** Added thrust remains a goal. (session-settled: user-directed, 2026-11-15 — chosen over RCS first, and over a fixed thrust share that could force the ramp beyond its canon outline.) Governs R7, R10.
- KD10. **The EDF motor is mounted as a pusher, ahead of the rotor.** (session-settled: user-directed, 2026-11-15 — chosen over the motor behind the rotor in the exhaust.) Governs R18.
- KD11. **Six items move forward: the Flight Engineer box, the winch, the tail EDF speed controller, the battery, the RCS servos and the Cargo Observer.** (session-settled: user-directed, 2026-11-15 — chosen over moving all eight candidates: the aft nodes stay.) Governs R19, R20.
- KD12. **The stern stack becomes the single Pilot-NoNFO stack and stays aft of the pivot.** (session-settled: user-directed, 2026-11-15 — chosen over moving it forward into the cargo bay.) Governs R21.
- KD13. **Carried from the earlier plan.** The tail EDF is an XFly Galaxy X5 motor with a custom 2.165 in (55 mm) rotor. The EDF holds a minimum cooling throttle in hover, with nacelle tilt compensating its thrust. Printed flow guides raise local air speed at failing nodes. The thrust tube is fused into the aft hull. The owner sets the aft CG limit before hull geometry work. CFD is tied to the node thermal budget. (session-settled: user-directed, 2026-11-15, in `docs/plans/2026-11-15-001-feat-fuselage-cooling-plan.md` KD7, KD8, KD10, KD11, KD12, KD6.) Governs R4, R8, R22, R23.

### Requirements

**Air path**

- R1. The tail EDF shall be the only air mover in the fuselage, and all its air shall pass through the fuselage interior.
- R2. The forward cargo ramp shall admit most of the EDF air.
- R3. The bow inlets shall admit the air for Bay A, and that air shall join the ramp air in the cargo bay.
- R4. Printed flow guides shall direct the stream past each node that needs more local air speed.
- R5. The ramp intake shall keep the canon outline of the cargo ramp.
- R6. A screen behind the ramp louvres shall stop debris that could damage the avionics or the rotor.

**Cooling, RCS and thrust**

- R7. Every node shall stay under its temperature limit in the average-power case, at the minimum cooling throttle, in still air and at cruise airspeed.
- R8. The EDF shall run at no less than the minimum cooling throttle whenever the avionics are powered, in flight and in hover.
- R9. On the ground, the EDF shall run at the minimum cooling throttle with the aircraft restrained against its thrust.
- R10. The analysis shall state the tail EDF thrust that the intake and interior path leave, at each analysed throttle, against the EDF's free-air thrust.
- R24. The requirements shall state the aircraft's response to an EDF or speed-controller fault in flight, which leaves no forced air.

**Sealed cargo bay**

- R11. The cargo doors shall be part of the printed hull skin, with canon panel lines.
- R12. One bolted, gasketed belly hatch shall give service access to the cargo bay.
- R25. The cargo bay shall have no opening to outside air other than the ramp, the service hatch seal, the winch fairlead and the Cargo Observer orifices.

**Winch and sling load**

- R13. The cargo winch shall mount on the cargo bay floor, with its motor as far forward as it fits.
- R14. The load line shall leave the belly through a fairlead under the tilt pivot.
- R15. A small recess in the belly shall house the hook or magnet when the line is retracted.
- R26. The winch line and fairlead shall be kept clear of the air stream to the EDF, so that a slack line cannot reach the rotor.

**RCS**

- R16. Four RCS jets shall be fitted and working in the first build, with their valves, servos and gateway.
- R17. Each RCS jet shall have a clear discharge path past the dorsal pod, the skids and the skid crossbar.

**Tail EDF installation**

- R18. The EDF motor shall sit ahead of the rotor, on a shaft short enough to run below its first critical speed with margin.
- R22. The aft hull shall carry the mounting ring, the fused thrust tube and the fixed elliptical nozzle, 2.06 × 1.76 in (52.3 × 44.7 mm).

**Mass and trim**

- R19. The Flight Engineer box, the winch, the tail EDF speed controller, the battery, the RCS servos and the Cargo Observer shall move forward as far as fit and function allow.
- R20. The Cargo Observer shall view its subject through orifices in the belly.
- R21. The stern stack shall be the single Pilot-NoNFO stack, aft of the pivot.
- R23. The hover CG shall lie inside the aft limit that the owner sets, with and without a slung load.

### Acceptance Examples

- AE1. **Covers R1, R25.** Given the built configuration, when the enclosure check runs, then every path from outside air to the EDF passes through the fuselage interior, and the only openings are those R25 names.
- AE2. **Covers R7, R8.** Given hover at the minimum cooling throttle, when the coupled analysis runs, then every node passes the average-power case.
- AE3. **Covers R10.** Given each analysed throttle, when the analysis runs, then it reports installed thrust beside free-air thrust.
- AE4. **Covers R23.** Given the ledger with every moved and added part, when the hover CG is aft of the owner's limit, then the run fails and an Owner Decision Brief is written.
- AE5. **Covers R17.** Given the chosen RCS stations, when the jet-path check runs, then all four jets are clear.
- AE6. **Covers R14, R23.** Given a slung load on the line, when the ledger runs, then the loaded CG is no further from the pivot than the empty CG.

### Success Criteria

- Every node passes the average-power case, with stated margins and stated uncertainty.
- The RCS has stated pitch and yaw authority at the minimum cooling throttle.
- Installed tail thrust is reported, and the plan shows what was done to raise it inside the canon ramp outline.
- The hover CG is inside the owner's limit.
- The first build needs no later hull reprint to gain the EDF, the RCS or the winch.

### Scope Boundaries

**Not in scope**

- Internal cargo, and any door actuation.
- The Delta cooling fan, its adapter and its power circuit.
- Intakes in the rear bell, intake covers, RCS caps and the baffled insert.
- Moving the aft nodes or the stern stack forward.
- A long drive shaft from a motor in the cargo bay to the rotor.

**Deferred for later**

- Bench measurement of the ASSUMED thermal inputs, and a transient thermal model.
- Drawing and bench-testing the custom rotor and its shroud.
- Flight-control firmware for the minimum cooling throttle, the tilt trim and the RCS mixer.

### Dependencies and Assumptions

- **Measured baseline.** The fan operating point, node temperatures, rear-cone stations and the CG arm are in `docs/plans/2026-11-15-001-feat-fuselage-cooling-plan.md`, "Measured Baseline". Every thermal input is ASSUMED.
- **Ramp opening.** The sealed ramp fairing measures about 2.0 × 1.4 in (52 × 36 mm), or 2.9 in² (1,870 mm²), in `tools/cargo_layout_fit.py`. The rotor's swept area is about 2.7 in² (1,760 mm²), with an ASSUMED 1.1 in (28 mm) hub. Louvres and a screen reduce the open area.
- **Forward-move estimates.** Estimated CG gains, from `current-specification/auw_ledger.json`, with unverified destination stations:

| Item | Mass | CG gain |
| --- | --- | --- |
| Flight Engineer box with can, plate, shunt and fuses | 0.55 lbm (251 g) | 0.24 in (6.2 mm) |
| Battery, moved 1 in (25 mm) | 1.38 lbm (624 g) | 0.09 in (2.3 mm) |
| Winch | 0.33 lbm (150 g) | 0.08 in (1.9 mm) |
| RCS servos | 0.08 lbm (36 g) | 0.05 in (1.3 mm) |
| Cargo Observer | 0.13 lbm (60 g) | 0.04 in (1.1 mm) |
| Tail EDF speed controller | 0.08 lbm (35 g) | 0.04 in (1.0 mm) |

- **Trim is marginal on these estimates.** The six moves recover about 0.54 in (13.8 mm). The aircraft with the EDF and RCS starts about 0.81 in (20.6 mm) aft of the pivot. That leaves about 0.27 in (6.8 mm) aft, against an ASSUMED working band of ±0.25 in (6.4 mm). The Pilot-NoNFO merge and shorter power wiring are not yet counted.
- **Shaft critical speed.** The X5 motor turns up to about 71,000 rpm unloaded. A 0.16 in (4 mm) steel shaft runs clear of its first critical speed at 2 in (50 mm) unsupported, and inside its running range at 4 in (100 mm). Simply supported, ASSUMED properties, rotor overhang not counted.
- **RCS stations.** On the Rev U aft hull, a ventral jet is clear from station Y 628 aft. A straight dorsal jet is blocked by the dorsal pod neck. Source: `tools/rear_cone_layout_fit.py`.
- **Repo rules that change.** Root `AGENTS.md` §1 calls the tail EDF optional and deferred to Phase 11. This plan makes it part of the first build. The design-shift gate in `AGENTS.md` §10 requires the WBS record before any geometry change.
- **Affected documents.** `docs/CARGO_WINCH_SPECIFICATION.md`, `docs/CARGO_DOOR_GATEWAY_SPEC.md`, `docs/CARGO_SECTION_LAYOUT.md`, `docs/POWER_DISTRIBUTION.md`, `deferred/WBS.md`, and the stern stack plan `docs/plans/2026-11-14-001-feat-nonfo-pilot-pb2-stern-stack-plan.md`.

### Outstanding Questions

**Deferred to Planning**

- OQ1. **Thrust target.** Default: report installed thrust against free-air thrust, with no fixed share. The owner may set a share once the first analysis shows what the ramp leaves.
- OQ2. **Response to an EDF fault in flight.** Default for planning: shed radio transmit power, report the fault, and land. The owner confirms or changes it.
- OQ3. **RCS jet pattern.** Planning proposes four stations that meet R17 and gives pitch and yaw authority for each option.
- OQ4. **What the Cargo Observer watches** now that there is no internal cargo. Default: the sling load and the ground below, through the belly.

### Relationship to the Earlier Plan

`docs/plans/2026-11-15-001-feat-fuselage-cooling-plan.md` stays the record of the measured baseline and of the decisions carried in KD13. Its fan-stage units no longer apply. Planning this document decides whether to revise that plan in place or replace it.

The draft gate G1 tools, `tools/rear_cone_layout_fit.py` and `tools/cooling_g1_figures.py`, measure the rear cone and check RCS jet paths. Their intake, fan and baffle content is superseded.

### Sources

- Issue #290 and the owner's direction of 2026-11-15.
- `tools/cargo_layout_fit.py` for the ramp opening; `docs/CARGO_SECTION_LAYOUT.md` §5 for the ramp fairing.
- `current-specification/auw_ledger.json` for masses and stations.
- `tools/rear_cone_layout_fit.py` for rear-cone stations and RCS jet paths.
- `docs/references/` [REF-EDF-001], [REF-EDF-002] for the X5 unit.
