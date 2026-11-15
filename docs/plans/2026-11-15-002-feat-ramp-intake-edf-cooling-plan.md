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
- KD14. **The tail EDF is the XFly Galaxy X5 50 mm unit with its stock rotor, in a printed pusher shroud.** (session-settled: user-directed, 2026-11-15 — the owner chose the QX 64 mm nacelle unit on the condition that it stay inside the controllable envelope; the hover trim estimate shows the QX needs a 1.57 in (40 mm) ventral RCS jet to hold trim to 50 % of control, against 1.02 in (26 mm) for the X5. Chosen over the QX 64 mm, and over the X5 motor with a custom 2.165 in (55 mm) rotor, which gains nothing installed. Supersedes the earlier plan's KD8.) Governs R18, R29, R30.
- KD15. **The ramp louvres are designed for low pressure loss.** (session-settled: user-directed, 2026-11-15 — chosen over ordinary louvres: installed thrust and RCS authority both fall with intake loss, and behind ordinary louvres the X5 also fails the 50 % trim criterion.) Governs R5, R6, R27, R30.
- KD16. **The ventral RCS jet sits at station Y 628 or further aft.** (session-settled: user-directed, 2026-11-15 — chosen over piping the jet through the skid crossbar, and over moving the crossbar forward 0.25 in (6.4 mm): the crossbar ends at about Y 627, the jet path is clear from Y 628 to Y 640, and no skid structure changes.) Governs R17, R32.
- KD13. **Carried from the earlier plan.** Nacelle tilt compensates the tail EDF thrust in hover. Printed flow guides raise local air speed at failing nodes. The thrust tube is fused into the aft hull. The owner sets the aft CG limit before hull geometry work. CFD is tied to the node thermal budget. (session-settled: user-directed, 2026-11-15, in `docs/plans/2026-11-15-001-feat-fuselage-cooling-plan.md` KD7, KD8, KD10, KD11, KD12, KD6.) Governs R4, R8, R22, R23.

### Requirements

**Air path**

- R1. The tail EDF shall be the only air mover in the fuselage, and all its air shall pass through the fuselage interior.
- R2. The forward cargo ramp shall admit most of the EDF air.
- R3. The bow inlets shall admit the air for Bay A, and that air shall join the ramp air in the cargo bay.
- R4. Printed flow guides shall direct the stream past each node that needs more local air speed.
- R5. The ramp intake shall keep the canon outline of the cargo ramp.
- R6. A screen behind the ramp louvres shall stop debris that could damage the avionics or the rotor.
- R27. The intake path, louvres and screen included, shall leave the tail EDF a stated pressure margin below the fan's stall point at full throttle.

**Cooling, RCS and thrust**

- R7. Every node shall stay under its temperature limit in the average-power case, at the minimum cooling throttle, in still air and at cruise airspeed.
- R8. In hover the tail EDF shall run at the throttle that pitch trim and RCS authority need. The estimate is full throttle at the present CG. A lower "minimum cooling throttle" applies only where the RCS is not needed.
- R9. On the ground, the EDF shall run at the minimum cooling throttle with the aircraft restrained against its thrust.
- R10. The analysis shall state the tail EDF thrust that the intake and interior path leave, at each analysed throttle, against the EDF's free-air thrust.
- R24. The requirements shall state the aircraft's response to a tail EDF, speed-controller or RCS fault in hover, which removes pitch control, and in forward flight, which removes forced cooling.

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
- R32. The ventral RCS jet shall be at station Y 628 or further aft, clear of the skid crossbar.

**Tail EDF installation**

- R18. The EDF motor shall sit ahead of the rotor, on a shaft short enough to run below its first critical speed with margin.
- R29. The tail EDF, its speed controller and the RCS shall be treated as flight-critical in hover: they are the only pitch trim and pitch control the aircraft has there.
- R30. Hover pitch trim shall use no more than 50 % of the pitch control moment, the criterion adopted in `docs/CG_RELOCATION_STUDY.md` §1.
- R31. The RCS shall give pitch authority in both directions about the trim point, and yaw authority.
- R33. The RCS jets shall be sized from the duct's total pressure and the jet path loss, so that hover pitch trim meets R30.
- R22. The aft hull shall carry the mounting ring, the fused thrust tube and the fixed elliptical nozzle, 2.06 × 1.76 in (52.3 × 44.7 mm).

**Mass and trim**

- R19. The Flight Engineer box, the winch, the tail EDF speed controller, the battery, the RCS servos and the Cargo Observer shall move forward as far as fit and function allow.
- R20. The Cargo Observer shall view its subject through orifices in the belly.
- R21. The stern stack shall be the single Pilot-NoNFO stack, aft of the pivot.
- R23. The hover CG shall lie inside the limit that the owner sets, with and without a slung load. The estimated window is 0.04 to 0.12 in (1.0 to 3.0 mm) aft of the pivot.
- R34. The bow shall have a trim pocket that takes real equipment first and ballast second, adjustable after the as-built CG is weighed.

### Acceptance Examples

- AE1. **Covers R1, R25.** Given the built configuration, when the enclosure check runs, then every path from outside air to the EDF passes through the fuselage interior, and the only openings are those R25 names.
- AE2. **Covers R7, R9.** Given the aircraft restrained on the ground at the minimum cooling throttle, when the coupled analysis runs, then every node passes the average-power case.
- AE7. **Covers R8, R30.** Given hover at the stated tail throttle, when the trim analysis runs, then pitch trim uses no more than 50 % of the pitch control moment.
- AE3. **Covers R10.** Given each analysed throttle, when the analysis runs, then it reports installed thrust beside free-air thrust.
- AE4. **Covers R23.** Given the ledger with every moved and added part, when the hover CG is aft of the owner's limit, then the run fails and an Owner Decision Brief is written.
- AE5. **Covers R17.** Given the chosen RCS stations, when the jet-path check runs, then all four jets are clear.
- AE6. **Covers R14, R23.** Given a slung load on the line, when the ledger runs, then the loaded CG is no further from the pivot than the empty CG.

### Success Criteria

- Every node passes the average-power case, with stated margins and stated uncertainty.
- The RCS has stated pitch and yaw authority at the hover tail throttle.
- Installed tail thrust is reported, and the plan shows what was done to raise it inside the canon ramp outline.
- The hover CG is inside the owner's limit.
- Hover pitch trim uses no more than 50 % of the pitch control moment, with the tail throttle it needs stated.
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
- Flight-control firmware for the tail throttle schedule, the tilt trim and the RCS mixer.

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

- **Hover trim and control limits, planning estimate.** Free-body model in hover: nacelle thrust acts at the tilt pivot (Y 339.4, Z 146.9); the tail EDF thrust acts on the tail axis (Z 165.2); weight acts at the CG. A CG aft of the pivot gives a nose-up moment W·d. Two things oppose it. The tail thrust and the nacelle tilt that cancels it form a nose-down couple on a 0.72 in (18.4 mm) arm. Downward RCS jets at the tail give a nose-down moment on an arm of about 11.5 in (291 mm). Nacelle tilt alone cannot trim pitch, because the pivot is 0.41 in (10.3 mm) below the CG. CG is recomputed from `current-specification/auw_ledger.json` with every change in this document applied; added masses and destination stations are ASSUMED.
- **RCS jet model.** Each jet is fed by the duct's total pressure through a scoop, so its speed is the nozzle speed divided by √(1 + K), with a path loss K ASSUMED at 1.0. Jet force is ρ·A·v². Open jets add exit area and lower the nozzle speed; the fan is held at constant flow power. An earlier estimate in this session used a fixed bleed fraction, which gave jet speeds above what the duct pressure can drive; its figures were too favourable and are replaced here.

| | XFly X5 50 mm | QX 64 mm |
| --- | --- | --- |
| Hover mass | 14.62 lbm (6,634 g) | 14.93 lbm (6,770 g) |
| CG aft of the pivot | 0.16 in (4.0 mm) | 0.32 in (8.1 mm) |
| Trim moment needed | 2.30 lbf·in (0.260 N·m) | 4.77 lbf·in (0.539 N·m) |
| Left after the thrust couple, full tail throttle, low-loss ramp | 0.99 lbf·in (0.112 N·m) | 2.64 lbf·in (0.298 N·m) |
| Single ventral jet bore that holds trim to 50 % of control | 1.02 in (26 mm) | 1.57 in (40 mm) |
| Same, with ordinary louvres | cannot be met | not run |

- **RCS layout that the estimate supports, X5, low-loss ramp, full tail throttle.** All four jets at station Y 634. Jet paths are clear there for bores up to 0.94 in (24 mm) at each azimuth below, checked on the Rev U aft hull with a spreading-jet footprint.

| Jet | Azimuth, seen from aft | Bore | Purpose |
| --- | --- | --- | --- |
| Ventral port, ventral starboard | 255° and 285°, 15° either side of straight down | 0.75 in (19 mm) each | Nose-down trim and control |
| Upper port, upper starboard | 135° and 45° | 0.55 in (14 mm) each | Nose-up control together; yaw when used one at a time |

| Result at the present CG, 0.16 in (4.0 mm) aft | Value |
| --- | --- |
| Ventral opening to trim | 42 % |
| Trim use of nose-down control | 50 % |
| Nose-down reserve | 1.01 lbf·in (0.114 N·m), 2.1 rad/s² |
| Nose-up reserve | 2.24 lbf·in (0.253 N·m), 4.6 rad/s² |
| Yaw moment from one upper jet | 0.52 lbf·in (0.059 N·m) |
| Tail thrust left at trim | 1.60 lbf (7.1 N), from 1.82 lbf (8.1 N) with jets closed |

- **What the estimate means.**
    - The 0.47 in (12 mm) jets assumed earlier cannot trim the aircraft.
    - The result is fragile at the present CG. At 90 % tail throttle with a single 0.94 in (24 mm) ventral jet, trim uses 87 % of control; at 80 % it cannot trim. Ordinary louvres cannot trim either.
    - CG position is the strongest lever. At 0.12 in (3.0 mm) aft of the pivot, the same jets trim at 21 % and the two reserves are equal. At 0.09 in (2.3 mm) aft, the thrust couple alone trims the aircraft at full tail throttle. Forward of about 0.04 in (1.0 mm) aft, nose-up reserve runs out.
    - The CG window that the estimate supports is 0.04 to 0.12 in (1.0 to 3.0 mm) aft of the pivot. The present estimate, 0.16 in (4.0 mm), is outside it by 0.04 in (1.0 mm).
    - A tail EDF fault in hover leaves the trim moment unopposed: with the present CG, about 4.7 rad/s² of pitch acceleration, or 30° in about half a second.
    - The QX 64 mm needs a 1.57 in (40 mm) ventral jet for the same criterion, which confirms KD14.
- **Bow trim, checked 2026-11-15.** Mass at the bow moves the CG about 0.002 in per gram (0.05 mm per gram). The nose has free room: a pocket of about 0.4 to 1.4 in² (240 to 890 mm²) in section from station Y 8 to Y 22, and 2.2 to 3.7 in² (1,430 to 2,410 mm²) from Y 30 to Y 50, measured on the head hull less the head layout envelopes.
    - **The ledger baseline is not reliable to 0.04 in (1 mm).** The nose Observer board, its camera, ToF and laser pods and the pitot parts are in `tools/head_layout_fit.py` but not in the ledger. `docs/CG_RELOCATION_STUDY.md` carries the board as an ASSUMED 2.1 oz (60 g); at its centroid, Y 59.8, that moves the CG 0.10 in (2.5 mm) forward. The ledger puts the Bay A nodes at Y 45.7, but the head layout puts them at Y 91 and Y 117, which moves the CG about 0.04 in (1.0 mm) aft. Net, the CG may already be near 0.10 in (2.5 mm) aft of the pivot, inside the window. WBS item BAYA-FWD-08 is the open ledger update.
    - **GNSS antenna.** The retention ring for the GNSS patch is on the cargo roof at Y 415.7; the patch itself is not in the ledger. An ASSUMED 0.5 oz (15 g) patch moved to the nose gives about 0.03 in (0.85 mm). It needs a sky view through a wall that passes GNSS signals, which carbon-filled PA may not.
    - **49 MHz loading coil.** The forward post and coil are 0.14 oz (4 g) at Y 155.7. Moved to the bow they give 0.003 in (0.08 mm), which is not worth it for trim. The move would lengthen the end-fed wire by about 5 in (125 mm).
    - **Ballast.** 1.2 oz (35 g) at Y 15 gives 0.07 in (1.7 mm). It is the last resort, sized on the bench after the as-built CG is weighed.
- **Not assessed.** Gust and ground-effect moments, RCS valve and EDF spool dynamics, and the transition from hover to forward flight. The pitch plant is a double integrator with a point-mass inertia of about 0.055 kg·m²; no loop has been tuned and no stability margin is claimed.
- **Installed thrust, planning estimate.** Constant shaft power, calibrated to each unit's free-air static thrust; louvre and screen losses ASSUMED. All units keep about 40 to 47 % of free-air thrust behind louvred ramp intake; a plain screened ramp keeps about 56 to 66 %.

| Unit | Free air | Louvred ramp | Plain screened ramp |
| --- | --- | --- | --- |
| XFly X5 50 mm, stock (chosen) | 2.73 lbf (12.2 N) | 1.27 lbf (5.7 N) | 1.82 lbf (8.1 N) |
| X5 motor, custom 55 mm rotor | 2.90 lbf (12.9 N) | 1.29 lbf (5.7 N) | 1.84 lbf (8.2 N) |
| QX 64 mm, 2300 KV | 5.22 lbf (23.2 N) | 2.03 lbf (9.0 N) | 2.93 lbf (13.0 N) |

- **Stall margin.** Behind louvres with an ASSUMED loss coefficient of 2.3 on 55 % open area, the X5 needs about 0.83 psi (5.7 kPa) of about 1.20 psi (8.3 kPa) available. The QX 64 mm would need all of its 1.25 psi (8.6 kPa).
- **QX 64 mm, for the record.** 1,368 W and 57 A at full throttle [REF-EDF-003]; about 0.26 lbm (118 g) heavier than the X5 installed; shroud lip OD 3.03 in (77 mm).
- **Shaft critical speed.** The X5 motor turns up to about 71,000 rpm unloaded.
- **RCS stations.** On the Rev U aft hull, the skid crossbar runs from about station Y 612 to Y 627. A ventral jet is clear from Y 628 to Y 640, with a stub of about 0.6 in (16 mm). A straight dorsal jet is blocked by the dorsal pod neck. The draft tool still places the RCS station at Y 621 and needs this change. Source: `tools/rear_cone_layout_fit.py`.
- **Repo rules that change.** Root `AGENTS.md` §1 calls the tail EDF optional and deferred to Phase 11. This plan makes it part of the first build. The design-shift gate in `AGENTS.md` §10 requires the WBS record before any geometry change.
- **Affected documents.** `docs/CARGO_WINCH_SPECIFICATION.md`, `docs/CARGO_DOOR_GATEWAY_SPEC.md`, `docs/CARGO_SECTION_LAYOUT.md`, `docs/POWER_DISTRIBUTION.md`, `deferred/WBS.md`, and the stern stack plan `docs/plans/2026-11-14-001-feat-nonfo-pilot-pb2-stern-stack-plan.md`.

### Outstanding Questions

**Deferred to Planning**

- OQ1. **Thrust target.** Default: report installed thrust against free-air thrust, with no fixed share. Planning estimate for the X5: about 1.3 lbf (5.7 N) behind ordinary louvres, about 1.8 lbf (8.1 N) behind a plain screened opening, against 2.7 lbf (12.2 N) free air.
- OQ5. **Hover endurance.** The tail EDF runs at or near full throttle in hover. Planning states the power this adds and the endurance it costs.
- OQ6. **Closing the CG window.** The present estimate is 0.04 in (1.0 mm) aft of the window, but the ledger omits the nose Observer and misplaces the Bay A nodes. Planning reconciles the ledger first, then moves the GNSS antenna to the nose if its signal path allows, then sizes bow ballast for what is left.
- OQ2. **Response to an EDF fault in flight.** Default for planning: shed radio transmit power, report the fault, and land. The owner confirms or changes it.
- OQ3. **RCS jet pattern and size.** The estimate supports two ventral jets at 255° and 285°, 0.75 in (19 mm) bore, and two upper jets at 45° and 135°, 0.55 in (14 mm) bore, all at station Y 634. Planning confirms it with the measured jet path loss, or moves the CG forward and shrinks the jets.
- OQ4. **What the Cargo Observer watches** now that there is no internal cargo. Default: the sling load and the ground below, through the belly.

### Relationship to the Earlier Plan

`docs/plans/2026-11-15-001-feat-fuselage-cooling-plan.md` stays the record of the measured baseline and of the decisions carried in KD13. Its fan-stage units no longer apply. Planning this document decides whether to revise that plan in place or replace it.

The draft gate G1 tools, `tools/rear_cone_layout_fit.py` and `tools/cooling_g1_figures.py`, measure the rear cone and check RCS jet paths. Their intake, fan and baffle content is superseded.

### Sources

- Issue #290 and the owner's direction of 2026-11-15.
- `tools/cargo_layout_fit.py` for the ramp opening; `docs/CARGO_SECTION_LAYOUT.md` §5 for the ramp fairing.
- `current-specification/auw_ledger.json` for masses and stations.
- `tools/rear_cone_layout_fit.py` for rear-cone stations and RCS jet paths.
- [REF-EDF-001], [REF-EDF-002] for the X5 unit; [REF-EDF-003] for the QX 64 mm unit compared against it.
- `docs/CG_RELOCATION_STUDY.md` §1 for the 50 % control-reserve criterion.
