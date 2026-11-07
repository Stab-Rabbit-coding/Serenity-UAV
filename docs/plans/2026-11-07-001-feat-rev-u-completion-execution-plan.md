---
title: Rev U Completion — Measurable Execution Path, Roadmap and Sprint Plan
date: 2026-11-07
type: feat
artifact_contract: ce-unified-plan/v1
artifact_readiness: plan
product_contract_source: owner request 2026-11-07
execution: mixed (agent sprints + owner decisions + physical build blocks)
---

# Rev U Completion — Measurable Execution Path, Roadmap and Sprint Plan

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (owner, request) — plan drafted by Claude
(Anthropic, Claude Opus 5.5) under the author's direction, using the `project-overseer`,
`product-management:roadmap-update` and `product-management:sprint-planning` skills.
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

## Goal Capsule

**Objective.** Take Serenity from its current Rev U state to *complete*: every design item closed,
every part procured and built, and the flight phases flown. The open items in the WBS/TODO federation
are the work list. This plan puts them in order, groups them into sprints that each fit one
5-hour token-capped session, and gives each sprint numbers that say whether it finished.

**Mode.** Governed (`AGENTS.md` + the `WBS.md`/`TODO.md` federation, `docs/WBS_FEDERATION.md`). This
plan creates no second task list. Every item it names lives in an owning `WBS.md`. A sprint closes
items there first, then regenerates `TODO.md` with `tools/gen_todo_from_wbs.py`, as `AGENTS.md` §10
requires.

**Product authority.** Owner (Stab-Rabbit-coding). Sprint order is a recommendation. Each owner-decision
gate (§5) needs the owner's word, and nothing here closes one.

**Status of this plan.** The plan is written down. No sprint after S0 has started. The project-overseer gates
apply: the owner reviews this file ("requirements done" → "approved") before S1 starts.

## 1. Definition of "complete"

"Complete" is a ladder of five levels, L1–L5 (not to be confused with the first-flight owner decisions D1–D5 in `docs/plans/2026-09-15-001-first-flight-readiness-plan.md`). Each level has a test you can run or a flight you can log.

| Level | Name | Done when (measurable) |
|---|---|---|
| **L1** | Design-complete | Agent-executable items in every subsystem `TODO.md` = 0. All CI jobs green. `pytest tools/tests` 0 failed. Every BOM row priced and mesh-synced (`check_bom_mesh_sync.py`: 0 drift, NOT COVERED = tooling only). Every PCB has DRC 0, ERC 0, Gerbers. |
| **L2** | Build-complete | Phases 0–4 in `graphical-build-guide/TODO.md` all checked from the physical build (photos/measurements recorded in the WBS). |
| **L3** | First flight | Phase 5 "Minimum Viable Flyer" in `graphical-build-guide/flight-phases/TODO.md` all checked, and every hard blocker in `docs/FIRST_FLIGHT_READINESS.md` §1 closed. |
| **L4** | Full system | Phases 6–8 checked (8-node architecture + ToF OA, cargo system, finishing). |
| **L5** | Envelope + autonomy | Phases 9–10 checked; Operator's Manual filled from flight data (OM-5). |

**Explicitly out of scope ("Won't" for Rev U):** Phase 11 aft EDF integration (`deferred/TODO.md`,
43 items). It stays in `deferred/` and is reported, not burned down.

## 2. Baseline (measured 2026-11-07, commit after 92dbfb45)

`python3 tools/wbs_burndown.py --json docs/plans/2026-11-07-001-burndown-baseline.json`

| File | Open | Mostly |
|---|---:|---|
| `airframe/TODO.md` | 10 | design (A) |
| `airframe/fuselage-joints/TODO.md` | 12 | design (A), 1 procurement |
| `airframe/fuselage-mid/TODO.md` | 80 | design (A), bench (P) for the winch |
| `airframe/landing-gear/TODO.md` | 21 | design (A) + coupon/drop tests (P) |
| `airframe/wings-nacelles/TODO.md` | 32 | design (A) + bench (P) |
| `avionics/TODO.md` | 85 | PCB layout (A), owner RF choices (O) |
| `avionics/emi-hardening/TODO.md` | 26 | specs + SCAD (A), bench (P) |
| `avionics/firmware/TODO.md` | 20 | code (A), bench (P) |
| `avionics/kicad/Observer/observer/TODO.md` | 34 | PCB + firmware (A), bench (P) |
| `avionics/rev-s1/TODO.md` | 3 | PCB (A) |
| `docs/TODO.md` | 31 | docs (A), compliance actions (O/P) |
| `gcs/TODO.md` | 35 | code + specs (A), procurement/tests (P) |
| `graphical-build-guide/TODO.md` | 141 | 56 SVG/sequence items (A), 85 build steps (P) |
| `graphical-build-guide/flight-phases/TODO.md` | 139 | flight tests (P) |
| `deferred/TODO.md` | 43 | out of scope |
| **Total (subsystem files)** | **712** open, 467 closed | root `WBS.md` (658 open) indexes many of these and also owns project-wide items (§0.x, §5, §6); reported on its own row |

Other baselines that sprints are measured against:

| Measure | Baseline | Command |
|---|---|---|
| Unit tests | 101 passed, **3 failed** (`test_nacelle_esc_service` ×2, `test_tail_strike_requirement::test_gear_tool_regression_at_13_lbm`; pre-existing) | `python3 -m pytest tools/tests -q` (≈ 2.5 min) |
| CI | no failed check suite on 92dbfb45 (PR #281) | GitHub Actions `ci.yml` |
| BOM printed rows with no mesh | 11 (winch ×6, node saddle, Hall hub, void formers, neck intake frame, 64 mm ESC covers) | `python3 tools/check_bom_mesh_sync.py` |
| 64 mm nacelle required parts unpublished | 4 (ESC covers) | `python3 tools/check_nacelle_deps.py` |
| Nacelle assembly clashes | spigot 0.095 in³ (1,562 mm³); pinion sweep 0.137 in³ (2,237 mm³); cable route none | `tools/nacelle64_assembly_check.py` |
| Pivot residual | +0.38 in (9.6 mm), not converged | `tools/nacelle_mass_cg_64.py` |
| Winch packaging | FAIL (no placement clears hull + layout) | `tools/winch_packaging_fit.py` |
| Cargo layout | FAIL, stale tool (old shell) | `tools/cargo_layout_fit.py` |

**Work classes.** Every item is one of: **A** agent-executable (CAD, PCB, code, docs, analysis);
**O** owner decision; **P** physical (procure, print, build, bench, flight), which the owner does and
the agent prepares and records. Each sprint's scope is A items only. O items are gates in front of
sprints. P items are grouped into build blocks (§7), and each block has an agent record sprint after it.

## 3. Roadmap (Now / Next / Later)

| Horizon | Theme | Outcome | Status |
|---|---|---|---|
| **Now** | S0 Record + plan | Findings recorded, plan and burndown in place | **Done** this session |
| **Now** | N — Nacelle mechanical close | Assembly clashes 0, cable route found, pivot converged, pods re-baked | Blocked on OD-1, OD-3, OD-4 |
| **Next** | H — Hull and cargo close | Winch built to an owner-chosen layout; doors, latches, Bay A, mid/rear bays | Blocked on OD-2 |
| **Next** | G — Landing gear close | LG design items closed, gear re-massed for the measured aircraft | OD-5, OD-7 |
| **Next** | A — Avionics fab-ready | Pilot, TACCO, Commo, FE, gateway, Observer: DRC 0, ERC 0, Gerbers | OD-6, OD-11, OD-12 |
| **Later** | F — Firmware | Phase-5 firmware set, then security buses, then autonomy | depends on A |
| **Later** | D — Docs, BOM, compliance | Every row priced, standards verified, Operator's Manual v1.0 | OD-13, OD-14 |
| **Later** | B — Build guide | Rev U build guide and SVG cards regenerated, stale Phase 0–4 steps reconciled | depends on N, H, G |
| **Later** | P — Physical blocks | L2 → L5 | owner |

## 4. Sprint mechanics

**Size.** One sprint = one session under the 5-hour token cap. Capacity is counted in points of about
30 minutes of agent work: 10 points per session. Plan **7 points** of scope, keep 1.5 for the close-out
ritual and 1.5 for overrun (70 % loading, per the sprint-planning skill). Heavy steps have known costs:
an OpenSCAD pod render ≈ 11 min of CPU (run in the background); the full pytest suite ≈ 2.5 min; a CI
round trip ≈ 6 min.

**Rules.**
1. One sprint goal, one sentence. If an owner decision it needs is not in, the sprint does not start;
   take the next ready sprint instead.
2. Scope is item IDs from an owning `WBS.md`. A sprint closes items there with full notes, then runs
   `gen_todo_from_wbs.py`.
3. Carry-over is honest: an unfinished item stays open with a dated note saying what is left.
4. Branch per `AGENTS.md`/session rules; never push to `main`.

**Close-out ritual (every sprint, in this order).** The requested `ce-*` skills (`/ce-setup`, `/ce-plan`,
`/ce-doc-review`, `/ce-code-review`, `/ce-compound`, `/ce-commit-push-pr`) are **not installed in this
environment** (checked 2026-11-07; no skill or command by those names). Until they are, each step uses
the equivalent below. The artefacts are the same ones the `ce-*` workflow writes: `docs/plans/` and
`docs/solutions/`.

| Step | Requested | Equivalent used | Measurable output |
|---|---|---|---|
| 1 | `/ce-doc-review` | Review every changed doc against `AGENTS.md` (units, citations, ≤70-char TODO lines) with the `engineering:documentation` skill; `gen_todo_from_wbs.py --check`; `precommit_index.py --check`; `sync_operators_manual.py --check` | all three checks exit 0; findings fixed or logged |
| 2 | `/ce-code-review` | `/code-review` (built-in) on the sprint diff at `medium` | findings fixed or answered; flake8 (100 col) + mypy clean on changed tools |
| 3 | `/ce-compound` | One `docs/solutions/<category>/<slug>.md` per reusable lesson (existing YAML frontmatter schema), plus `compounded:compounded-author` for procedures worth replaying | ≥ 1 solution doc, or a one-line note in the PR saying why none |
| 4 | `/ce-commit-push-pr` | Commit with the attribution trailers, `git push -u origin <branch>`, draft PR (or update the open one), subscribe to PR activity | CI green on the head commit |
| 5 | burndown | `python3 tools/wbs_burndown.py --baseline docs/plans/2026-11-07-001-burndown-baseline.json` | `closed+` (subsystem total) rises by at least the sprint's target; new findings recorded in the sprint raise `d_open` and are listed in the PR, never held back |

## 5. Owner-decision queue (gates)

| ID | Decision | Item | Needed before |
|---|---|---|---|
| OD-1 | Nozzle spigot vs cartridge: shorten cartridge 0.12 in (3 mm) or drop the spigot | NAC-64-ASM-01 | S1 |
| OD-2 | Winch layout: (a) aft/low spool + bridle, (b) right-angle/belt servo, (c) move tilt hardware, (d) two spools | WINCH-PKG-01 | S7 |
| OD-3 | ESC part and rating (70 A vs 80 A) | NAC-64-ESC-80A | S4 |
| OD-4 | Release the NAC-64-REBAKE hold | NAC-64-REBAKE | S3 |
| OD-5 | Hover ground-clearance margin / mandatory gear height | LG-HOVER-01 | S12 |
| OD-6 | Bay A forward thermal tier | BAYA-FWD-T1 | S21 |
| OD-7 | Nozzle strike during a full ductile-fuse arrest | LG-28 | S12 |
| OD-8 | Nozzle-servo gateway variant | D-NZ-1 | S5 |
| OD-9 | Wing SPAR-25-5 decision (§1.1.3.1) | SPAR-25-5 | S6 |
| OD-10 | Commo RF: 1553 coupling, 49 MHz channel list, re-baselined RF current, antenna-shell bond | avionics "Owner:" items | S16 |
| OD-11 | TPM path: SLB9672 vs OPTIGA Trust M on gateway + FE | avionics §1.9.2 | S18 |
| OD-12 | 2026-10-18 branch reconciliation | avionics "Reconcile 2026-10-18" | S21 |
| OD-13 | SLS vendor + quotes; source for part prices | BOM, §6.5 | S27 |
| OD-14 | PE review of the Operator's Manual v0.1 | docs §0.10.3 | S28 |
| OD-15 | Winch shed threshold vs maneuver envelope | fuselage-mid ★ | S7 |
| OD-16 | First-flight decisions D1–D4 and D6 (scope, nozzle datum, 3.0 in gear, hover T/W floor, XO board area; D5 decided) — D2 overlaps OD-9, D3 closes OD-5 | `docs/plans/2026-09-15-001-first-flight-readiness-plan.md` | S3 (D4 sets the T/W target), P4 |

## 6. Agent sprints

Notation: **Est.** = sessions, optimistic / most likely / pessimistic. **Exit** = what has to measure
true at close-out. **−n** = minimum number of items closed in the sprint (`closed+` in `wbs_burndown.py`; closures, not the net open count, so recording new findings never fails a sprint). Theme D items owned by the root `WBS.md` count on its row.

### S0 — Record findings and plan (this session) — DONE 2026-11-07
- Recorded NAC-64-ASM-01..04, the WA-R10 correction, WINCH-PKG-01 in the owning WBS files; the Rev U
  checkpoint (`docs/WBS.md` §6.5) records the assembly check.
- This plan, `tools/wbs_burndown.py` + baseline snapshot, the close-out ritual run once.
- Exit: `gen_todo --check` 0; indexes in sync; CI green.

### Theme N — Nacelle mechanical close (`airframe/wings-nacelles/WBS.md`)

**S1 — Clear the three assembly clashes.** Goal: the 64 mm nacelle assembles and tilts with zero
interference on both pod renders. Needs OD-1.
- NAC-64-ASM-01 (spigot/cartridge), NAC-64-ASM-02 (relieve the two blocks in the pinion channel),
  NAC-64-ASM-03 (restore the bay floor + stud bosses, open the pocket mouth).
- Exit: `nacelle64_assembly_check.py` on both renders: static overlaps only rib contact (≤ 0.001 in³ (15 mm³)),
  `pinion_pocket_mm3` = 0, sweep pod|pinion = 0 at every 5° step; `check_nacelle_deps.py` PASS. −3.
- Est. 1 / 1 / 2 (each pod render 11 min; render both in parallel in the background).

**S2 — Draw the 4 × 10 AWG route (WA-R10).** Goal: the bundle has a drawn, clearance-proven path from
the spar bore to the disconnect bay.
- Open an exit from the bore mouth (trunnion/collar side port or a spar-tip exit slot), route to the
  bay, set harness lengths; SPAR-20-WIREOD (record the measured or datasheet wire OD, cite it).
- Exit: `--stage cable` finds a route at r 0.32 in (8.14 mm) on both sides; routed length recorded;
  centreline bend radius ≥ 3 × wire OD (the repo's NASA-STD-8739.4A citation; verify the clause, per
  `REFERENCES.md`) at every bend. Both WA-R10 entries closed. −3.
- Est. 1 / 2 / 3.

**S3 — Pivot, gates and re-bake.** Needs OD-4.
- NAC-64-PIVOT-RC, NAC-64-GEOM-05 (port the trunnion/ESC-bay/mass gates to the 64 mm wrapper),
  NAC-64-REBAKE (both pods watertight), LG-HOVER-01 recompute.
- Exit: pivot residual ≤ 0.04 in (1.0 mm); `check_datum_drift.py` PASS; published pods watertight
  and equal in volume to the source render (±0.1 %); `auw_ledger.py --check` PASS. −4.
- Est. 1 / 1 / 2.

**S4 — ESC bays.** Needs OD-3.
- NAC-64-GEOM-02 (cooling ports), NAC-64-GEOM-03 (ESC covers from the scaled skin → 4 STLs),
  window structural allowance (section modulus with and without the windows), fix the two
  `test_nacelle_esc_service` failures.
- Exit: `check_nacelle_deps.py --strict-parts` PASS; BOM NOT COVERED −1 row; pytest failures 3 → 1. −3.
- Est. 1 / 1 / 2.

**S5 — Nozzle servo drive implementation.** Needs OD-8.
- Servo linkage + schedule tool (U2), ring stops/spring seat/slotted pull (U3), servo mount + pod
  pocket + flush cover (U4), BOM + REFERENCES (U7), NAC-MOULD-01, Makefile follow-up,
  `serenity_assembly.py` deleted-part placements, ASM-04 coverage (flaps, linkage, bearings).
- Exit: assembly check covers flaps and linkage across the full nozzle stroke and −5…135° with 0 mm³;
  `serenity_assembly.py` reports no COVERAGE GAP for the 64 mm nacelle. −7.
- Est. 1 / 2 / 3.

**S6 — Wings and spar.** Needs OD-9.
- Re-render/re-bake both wings (S1b OML), SPAR-02, SPAR-20-8, SPAR-20-9, SPAR-20-AERO,
  SPAR-20-TSCALE, SPAR-25-5/6, WA-R3/WA-R17 split-collar part, WA-R18 mass/CG/T-W.
- Exit: wings watertight; split collar has a mesh + BOM row; ledger T/W recomputed and recorded. −10.
- Est. 1 / 2 / 3.

### Theme H — Hull and cargo (`airframe/fuselage-mid`, `fuselage-joints`, `airframe/`)

**S7 — Winch, as decided.** Needs OD-2 and OD-15.
- Implement the chosen option; six Rev C STLs in `generate_cargo_mounts.py`; pedestal stations;
  containment checks (spec §3.10) on the assembly; refresh `cargo_layout_fit.py` to the one-piece hull.
- Exit: `winch_packaging_fit.py` exit 0; `cargo_layout_fit.py` PASS; BOM NOT COVERED −6. −8.
- Est. 1 / 2 / 3.

**S8 — Cargo doors.** U1 re-fit, DOOR-LATCH-1..6, DOOR-SEAM-1, SERVO-PLACE, SG90 bell-crank boss,
HULL-LEAK-04, PRINT-GW-DOOR-TRAY hardware.
- Exit: door pair assembles in the hull with 0 mm³ clash through its full swing (re-run the door
  check); latch spec items each closed with a mesh feature or a recorded reason. −8.
- Est. 1 / 1 / 2.

**S9 — Bay A forward and cargo-bay furniture.** BAYA-FWD-05..11, NODE-SADDLE, OBS-CARGO, HARN-CLIP/BHD,
GPS-ANT, TC-BOARD, ENC-DAUGHTER, 20D VERIFY.
- Exit: each part placed in the hull frame with 0 mm³ clash in `assembly_integrity_check.py`; BOM NOT
  COVERED −1 (node saddle). −12.
- Est. 1 / 2 / 2.

**S10 — Middle/rear bays.** FE room PDB mount, Simon bay, CF skid channels, COOL-01, HULL-FUSE-02,
LG-AFT-BOLT-01, light mounts, `flight_engineer_{battery,pdb}_tray.scad`, battery boss pattern +
swap hatch (emi-hardening items), retire or regenerate the legacy `head_shell24`/`cargo_sect_shell24`
STL items now that the one-piece hulls supersede them (close with a reason).
- Exit: middle/rear hull merged with the new features, watertight, mass within the plan G1–G3 gates
  or a recorded owner waiver. −15.
- Est. 1 / 2 / 3.

**S11 — Airframe record hygiene and placeholders.** FreeCAD catalog run, hull-frame placements for
VERIFY parts, `validate_stls.py` audit, placeholders ↔ BOM, rear skid SCAD, MA-1/MA-7, deprecate legacy
shell SCADs, fuselage-joints items (Book tray mount, door-servo pads, inner neck guidance).
- Exit: `validate_stls.py` 0 failures on live STLs; every PRINT-* row maps to an STL. −18.
- Est. 1 / 1 / 2.

### Theme G — Landing gear (`airframe/landing-gear/WBS.md`)

**S12 — Gear design close.** Needs OD-5, OD-7.
- LG-02, LG-13, LG-27, LG-29, LG-30, LG-REMASS, LG-18, LG-19, PROTO-LG-1, remaining-parts list,
  assembly + exploded views; fix `test_gear_tool_regression_at_13_lbm`.
- Exit: gear tools PASS at the S3 ledger AUW; pytest failures → 0. −12.
- Est. 1 / 2 / 3.

### Theme A — Avionics fab-ready (`avionics/*`, `avionics/kicad/Observer/observer`)

Measured by `tools/validate_kicad.py` counts per board.

- **S13 — Pilot DRC.** Clear 109 `clearance`, 96 `hole_clearance`, 44 `track_width`, the keepout; I2C1
  pull-ups; U-GPIO/C-GPIO and ESC-PWM placement. Exit: those four counts = 0. −7. Est. 1/2/3.
- **S14 — Pilot route + Gerbers.** 212 unconnected, ISOW §13.1 re-floorplan, SBUS/UART DIP, 1553
  connector, §14 connector table. Exit: unconnected 0, DRC 0, ERC 0, Gerbers generated. −8. Est. 2/3/4.
- **S15 — TACCO/XO.** Placement/DRC/routing/Gerbers, DTS drift, pinmux verification, 1553B→C docs
  sweep. Exit: DRC 0, ERC 0, Gerbers. −6. Est. 1/2/3.
- **S16 — Commo Rev T** (needs OD-10). Top-level schematic U1, coupling, layout, stub length, Gerbers,
  §15.235 pre-compliance checklist doc. Exit: DRC 0, ERC 0, Gerbers; checklist in `docs/`. −10. Est. 2/3/4.
- **S17 — Flight Engineer.** Last DRC, routing, Gerbers, dangling NCs, rev-S1 FE item, DRC
  accepted-violations record. Exit: DRC 0 (or documented accepted list), Gerbers. −5. Est. 1/1/2.
- **S18 — Gateway + trust module** (needs OD-11). MSPM0G351x errata/TRM, pinmux constants, support
  parts, PA0/PA1 pull-up, PA18 pull-down, thermal vias, lanes 3–4, gateway re-route, GW-DOOR-1..7 design
  items, SLB9672 ERC/DRC re-run. Exit: DRC 0, ERC 0 on the gateway; −16. Est. 2/2/3.
- **S19 — Observer PCB + mechanical.** sch↔pcb parity, 305 unrouted, Gerbers, mechanical integration
  items against the one-piece hulls, power-feed and laser unification docs. Exit: DRC 0, ERC 0, parity
  0, Gerbers. −15. Est. 2/3/4.
- **S20 — EMI and wiring specs.** Bus wiring specs (CAN FD, RS-485, 1553C, Ethernet ring, UART, I²C,
  DSHOT, PWM), Faraday enclosures, antenna-mount verification, magnetometer and Hall siting, U8. Exit:
  one spec section per bus in `avionics/emi-hardening/WBS.md`, each citing a catalogued REF-ID. −20.
  Est. 1/2/3.
- **S21 — Avionics close-out** (needs OD-6, OD-12). U1–U9 of plan 2026-08-25-001, BAYA-FWD-T2..T4,
  B1..B3, PCB mass roll-up into `airframe/README.md`, branch reconciliation. Exit: avionics `TODO.md`
  A-items 0. −20. Est. 2/2/3.

### Theme F — Firmware (`avionics/firmware`, Observer firmware, `gcs/`)

Each item lands with host-side unit tests; bench verification becomes a P item.

- **S22 — Phase-5 set.** IMU/baro fusion, GNSS parse, tilt PWM, ESC governor (BDSHOT), CAN FD
  heartbeat. Exit: unit tests pass in CI; clang-format clean. −5. Est. 1/2/3.
- **S23 — Buses and security.** 1553C BC/RT, RS-485 messaging, Ethernet RSTP, TPM HMAC, signed log,
  node election, MAVLink routing. Exit: tests pass; message formats documented. −8. Est. 2/3/4.
- **S24 — Autonomy and payload.** ToF manager, OA integration, waypoint mission, GPS cross-check,
  winch state machine, nacelle tilt command scheme. Exit: tests pass, including a simulated OA halt. −7.
  Est. 2/2/3.
- **S25 — Observer + GCS software.** MSPM0 control drivers, AM62A pipeline config scaffolding,
  `skipper_comms.c`, Skipper host spec, gimbal STL + wind-torque check. Exit: tests pass; gimbal
  STL watertight. −12. Est. 2/2/3.

### Theme D — Docs, BOM, compliance (`docs/WBS.md`, root §0.x)

- **S26 — Standards and citations.** §0.5 audit, §0.8 allowables, §0.12 SLS refs, §0.13 joint-torque
  section verification, ISO 53 / ISO 8752 clauses, 4130 finish spec. Exit: every touched citation has
  a validated URL + exact section in `REFERENCES.md`, or is marked "requires verification" with an
  open item; no section number is guessed. −12. Est. 1/2/3.
- **S27 — BOM complete** (needs OD-13). Price every row from a quote or a dated vendor page;
  EDF-DATA-01; bom JSON ↔ CSV sync. Exit: 0 rows at 0.00; `check_bom_mesh_sync.py` NOT COVERED =
  tooling only. −4. Est. 1/1/2.
- **S28 — Operator's Manual + compliance packets** (needs OD-14 for close). FAA Part 107/48 checklists,
  FCC §15.235 packet, nav-light compliance, OSHW self-cert draft, PDF render, `gen_todo --check` in
  pre-commit. Exit: `sync_operators_manual.py --check` PASS; v1.0 tagged after owner review. −12.
  Est. 1/2/2.

### Theme B — Build guide (`graphical-build-guide/*`)

- **S29 — Reconcile Phases 0–4 to Rev U.** Close or supersede (with reason) every step written for the
  FDM/four-section hull or the 50 mm nacelle (e.g. "nacelle bore caliper 55.0–56.0 mm", "4 mm CF pivot
  rod … MF104ZZ", the bevel/crown-pinion nozzle train). Rewrite them for SLS one-piece hulls, the 64 mm
  nacelle, trunnion + servo nozzle. BG-SEQ-1..6, BG-PLAN-1/2. Exit: no open step names a retired part
  (grep the retired list = 0 hits). −30 (supersessions). Est. 1/2/3.
- **S30 — Overview SVGs (Phase A 1–10) + pipeline.** Rebuild the silhouette pipeline, fix the four
  malformed SVGs. Exit: 10 overviews regenerated, all parse as XML. −13. Est. 1/2/2.
- **S31 — Cards Phase C + D (20).** Exit: 20 cards regenerated from the current meshes. −20. Est. 2/2/3.
- **S32 — Cards Phase E–F + flight-phase cards; re-audit REVN Phases 4–11.** Exit: every card
  regenerated; flight-phase test cards reconcile with the first-flight blockers and decisions D1–D5. −12. Est. 1/2/3.

### S33 — L1 design-complete audit
- Run every gate in `ci.yml`, the full pytest suite, `validate_stls.py`, `validate_kicad.py` on all
  boards, `wbs_burndown.py`. Recommend a Rev V pin per `AGENTS.md` §8 if the owner wants a letter at L1.
- Exit: the L1 row of §1 holds, item by item. Est. 1/1/2.

**Agent-sprint total:** 34 sprints (S0–S33) — optimistic 43, most likely **63**, pessimistic 93 sessions
(PERT expected ≈ 65 sessions; sum of the per-sprint estimates above). Planned burndown through S33: at
least 345 items closed or superseded (sum of the −n targets). The remainder are P items, closed in §7,
plus the 43 deferred Phase 11 items.

## 7. Physical build blocks (owner-executed; agent record sprint after each)

| Block | Content | Entry gate | Record sprint (agent) closes |
|---|---|---|---|
| P1 | Procurement, SLS quotes/orders, coupons (ASTM D3039/D695 CF plate, LG-11 CF-PETG, LG-15/16 wire), PMMA discs | L1 BOM priced (S27) | coupon data into the allowables DB; LG items |
| P2 | Print + Phases 0–4 build | P1 parts in hand | `graphical-build-guide/TODO.md` Phases 0–4 (≈ 85 items) with measurements |
| P3 | Bench: servo drive (U8), SPT5425LV winch, ESC thermal, AK7455 off-axis, 49 MHz isolation, Hall/ferrous spar, elastic + drop tests | P2 subassemblies | bench items across nacelle, LG, avionics, EMI |
| P4 | Phase 5 first flight | P3 PASS, Operator's Manual v1.0, Part 107/48 done | `flight-phases` Phase 5 (61) |
| P5 | Phases 6–8 | P4 | Phases 6–8 (55) |
| P6 | Phases 9–10, OM-5 flight values | P5 | Phases 9–10 (23); Operator's Manual flight values |

## 8. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Owner decisions arrive late | Sprints idle | The queue (§5) shows the need-by sprint; theme order lets the agent take any ready sprint |
| A design fix re-opens closed work (as the 64 mm hollowing did to WA-R10 and the bay) | Hidden regressions | Every sprint re-runs the assembly and layout tools that touch its parts, on both sides; findings go into the owning WBS the same day |
| Token cap hit mid-render | Lost sprint | Heavy renders in the background at sprint start; scope at 70 % |
| Unverified citations (NASA-STD-8739.4A, MMPDS, ISO clauses) | Wrong limits survive review | S26 verifies or marks "requires verification"; no section numbers guessed |
| P items depend on vendors | Calendar slip | P1 starts as soon as S27 lands; it does not wait for B-theme sprints |
| `ce-*` skills missing | Ritual drift | Equivalents in §4 until installed; same artefacts |

## 9. Tracking

- Burndown: `python3 tools/wbs_burndown.py --baseline docs/plans/2026-11-07-001-burndown-baseline.json`
  at every close-out; record `closed+`, `d_open` and the new findings in the sprint's PR description.
- Dashboard (project-overseer): count checkboxes per file; status markers `[x]` done, `[~]` in
  progress, `[!]` reopened, `[ ]` ready, `[X]` blocked by an OD.
- This plan is updated only by an owner-approved change (impact assessment first, per project-overseer
  change management).
