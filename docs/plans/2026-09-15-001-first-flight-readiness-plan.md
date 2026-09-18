---
title: "plan: Get Serenity to first flight (Phase 5) from the Rev T checkpoint"
date: 2026-09-15
plan_type: roadmap
execution: geometry+hardware+firmware+build
supersedes: docs/FIRST_FLIGHT_READINESS.md (2026-07-05 snapshot; now a rollup of this plan)
---

# plan: Get Serenity to first flight (Phase 5) from the Rev T checkpoint

**Target repo:** Serenity-UAV
**Baseline:** Rev T checkpoint (`docs/WBS.md` §6.4, 2026-09-06) plus everything landed
through commit `48835ae` (2026-09-10). Open-item counts below are taken from the
`TODO.md` files regenerated 2026-09-15 by `tools/gen_todo_from_wbs.py`.

*"I aim to misbehave." — Capt. Skipper Reynolds*

---

## What "first flight" means here

**First flight = master `WBS.md` Phase 5, "Minimum Viable Flyer":** CN1+FC1 (Bay A) and
CN2+FC2 (Bay B) installed, a 4-node VTOL hover, then the Phase 5 test ladder (tethered
hover → free hover 1 m → 3 m → nacelle transition ≥ 8 m → one forward-flight circuit).
**Not first-flight gates:** the remaining 4 nodes and Observer vision (Phase 6), the cargo
winch and doors' *mechanism* (Phase 7 — but the doors themselves are, see A6), the rear
EDF (Phase 11), the range-extender battery (Phase 12).

Two scope options are put to the owner in D1 below because they change the critical
path materially: a **hover-only first lift** (tethered + free hover, nacelles pinned at
90°) needs neither the nozzle drive nor the aero revalidation; the **full Phase 5 ladder**
(transition + circuit) needs both.

## Where the project actually is

| Domain | State at Rev T + 4 days | Open (TODO lines) |
| --- | --- | --- |
| Hull (4 shells, collars, LG bays) | Rev S baseline carried into T; all shells watertight; cargo doors / ramp / access covers **not** re-fit to current shell | fuselage-mid 60, joints 12, airframe 10 |
| Wings | Rev S1g fixed CF spar, root socket+flange built, `wing_root_deconflict.py` CLEAR; **actuator is the wrong kind of device** (multi-turn) and the train is **not self-locking** | wings-nacelles §1.1.2: 3 |
| Nacelles | Rev S4c/S4d trunnion, hollowed pods, hinged ESC bays; **nozzle drive is BLOCKED on an owner decision** (KTD3 datum, 0.0 mm axial margin); `MOTOR_BOLT_R` unverified (print-blocking); ESC bay has 3 open safety findings | wings-nacelles §1.1.3–§1.1.5: 32 |
| Landing gear | R6 legs, sponson wells CLOSED; **1.5 in leg is not viable** at `PIVOT_Z` 107.5, 3.0 in clears by 33 mm but is not yet the active variant (LG-31) | 22 |
| Mass / T/W | README says AUW 3,911 g, T/W ≈ 1.14; **MA-1 says printed parts are +521.6 g under-counted** and `docs/WBS.md` §0.10 says the true AUW may be 5.6–5.8 kg. Nothing downstream is trustworthy until this is closed | root §0.8.1: 13 |
| Avionics PCBs | Rev S schematics; **no board has clean DRC**; Pilot fab-blocked on tamper-mesh creepage; gateway MCU area unrouted after the RHB-32 retarget; actuator interface still PWM on paper | avionics 51, rev-s1 3, emi 26, observer 34 |
| Firmware | serenity-cn Phase 6 daemon done; **serenity-fc is a stub** — no governor, no tilt command, no IMU fusion, no GNSS | firmware 20 |
| Regulatory | Registration, Part 107 currency, nav lights, data plate all open; 49 MHz Part 15 pre-compliance open | docs §5.x: 10 |
| Physical build | Not started. Build-guide Phases 2/3 still describe the deleted gear train and 4 mm pivot rod | Phase 0–4: 85, Phase 5: 61 |

## Decisions the owner must make first (D-series)

None of these can be made by an agent; each unblocks a whole stream.

- **D1 — First-flight scope.** Hover-only first lift (nozzle pinned, no transition) or the
  full Phase 5 ladder. Hover-only removes A1 and A8 from the critical path.
- **D2 — Nozzle-drive datum** (`docs/NOZZLE_DRIVE_TRADE.md` "What is blocked"; WBS
  §1.1.3.1 `[BLOCKED]`, §1.1.5 SPAR-25-5). Pick (i) spend flux margin, (ii) spend wing
  geometry (grow the 4.0 mm joint gap), or (iii) reopen the datum — the linkage solve,
  gear sizing and tooth-stress work are datum-independent and carry over. Needed even for
  hover-only if the iris is to be pinned at a *known* area.
- **D3 — Make the 3.0 in landing-gear leg the active variant** (LG-31; the 1.5 in leg strikes
  the nozzle at the as-built pivot, §1.1.3.8). Closes LG-HOVER-01 by construction.
- **D4 — Hover T/W floor.** The record carries both "≥ 1.2 minimum" (WA-R18) and "T/W
  measured ≥ 1.10" (Phase 9 gate). State one number; it decides how much of W1..W8 is
  mandatory before first lift.
- **D5 — Tilt actuator class.** **DECIDED 2026-09-15, RE-CUT 2026-09-16 (Rev T5e):** Pololu 20D
  25:1 CB gearmotor + six-start worm 6.67:1 + spring-applied pin brake, own fused feeds (the
  25D / 4-start pick of 2026-09-15 could not clear the worm wheel — T5d-1); the controller is an
  Open-Secure-ESC build, not a LibreServo variant (2026-09-17, `docs/TILT_ACTUATOR_SELECTION.md` §4). D-T5-3 CLOSED (all four nodes placed in
  the cargo section). Residual: owner confirms the adopted rate requirement (TILT-CTL-07: 144 °/s
  no-load, 111 °/s at max efficiency).

## Work streams

Units are named so they can be started with `start <unit>` under the project-overseer
skill; each lists its owning WBS entry, so closure happens there first.

### Stream A — Airframe freeze (geometry → print-ready)

| Unit | What | Owner entry | Gate |
| --- | --- | --- | --- |
| **A0 Mass truth** | Reconcile the 23 under-counted printed rows (MA-1, +521.6 g), add the `Installed` flag (MA-7), fix `PRINT-BATT-TRAY` (MA-6), then re-derive AUW / CG / hover T/W once (WA-R18, SPAR-20-9, LG-32). Add the CI check MA-1 asks for. | root §0.8.1; `docs/MASS_AUDIT_CARGO_WING_ROOT.md` | A single AUW/CG ledger every other stream cites; T/W against D4 |
| **A1 Nozzle drive** *(full-ladder only)* | Execute D2; then SPAR-25-5 / re-hub `spar_crank()` / pushrod clearance / un-park `nacelle_nozzle_sync_gears.scad`; register in `serenity_assembly.py`. | wings-nacelles §1.1.3.1, §1.1.5 | `tools/nozzle_linkage_check.py` pass; iris reaches both stops over −5..140° |
| **A2 Tilt actuation** | ~~Execute D5; WA-R16; WA-R15a~~ **done 2026-09-15** (worm drive + brake, bracket/worm/wheel/brake-guide STLs, shell re-merged). Remaining: BRK-4 solenoid part, BRK-5 hold bench, TILT-CTL-02..08, LibreServo_v4.1-TC. | root §0.8/§0.8.1; `docs/TILT_ACTUATOR_SELECTION.md` | Train holds nacelle at 90° unpowered (bench); spec §8 items closed |
| **A3 Nacelle print-readiness** | Measure a real motor (bolt circle, 4-hole pattern, length, mass) and fix `MOTOR_BOLT_R` + spider; close the three ESC-bay safety findings (unfiltered path, bay velocity, 50 A sustained) and draw the WA-R10 disconnect route; NAC-MOULD-01 Stage 2 ovalising; register the trunnion in `serenity_assembly.py` and re-run the tilt sweep. | wings-nacelles §1.1.3.7, §1.1.3.8, §1.1.4 | `validate_stls.py`, `nacelle_mass_cg.py`, `nacelle_trunnion_fit.py` T1–T9 green |
| **A4 Landing gear** | Execute D3; LG-15/16 wire procurement + coupon; LG-02 backing plates; LG-27 touchdown attitude; LG-06/14 bench + drop tests. | landing-gear §1.1.4 | `landing_gear_wing_clearance.py --proud` CLEAR at 3.0 in; drop test FOS ≥ 4 |
| **A5 Wing attach hardware** | WA-R3/R17 split-collar pinch clamp (no part exists; blocks wing removal/refit). | root §0.8.1; `WING_ATTACH_INTERFACE.md` §5 | Part rendered, in BOM, in assembly |
| **A6 Fuselage closure** | Cargo clamshell doors re-fit to the current shell + SG90 bell-crank boss (plan 002 U1) — **still open**; ~~forward cargo-ramp fixed fairing (U2)~~ **done 2026-09-15**; ~~Inara/River access covers (U4)~~ superseded by D-T5-3. Plus the Rev T5 battery cradle + tilt brackets are now shell features (`docs/CARGO_SECTION_LAYOUT.md`). | fuselage-mid §1.1.1; plan 2026-08-25-002 | `cargo_bay_envelope.py` PASS; covers land on bosses |
| **A7 Material allowables** | CF spar tube ASTM D3039/D695 certificate (FOS 9.0 rests on an unverified 300 MPa stand-in); CF-PLATE-2MM coupon; measure the procured 10 AWG wire OD; REF-STD-GEAR-001 clause lookup. | root §0.8; `docs/TILT_SPAR_ANALYSIS.md` §3.6.3 | REF-MAT-* entries with validated sources |
| **A8 Aero revalidation** *(full-ladder only)* | XFOIL or transition-sensitive RANS at Re 1.3–1.8e5 on S1223/t17.7 and /t26.7; re-derive the 7.6 N cruise-lift figure and `docs/flight_envelope.md`. | root §0.8; wings-nacelles SPAR-20-AERO | Cruise CL, L/D with a stated method |
| **A9 Build-guide currency** | Rewrite build-guide Phase 2/3 steps (currently sector gear, bevel pair, crown pinion, MF104ZZ + 4 mm pivot rod — all deleted) to the trunnion / 6704ZZ / pushrod drive; then Phase 0 checks. | graphical-build-guide WBS Phase 2/3; docs §1.5 | No step names a retired part |

### Stream B — Avionics boards to fab

| Unit | What | Owner entry | Gate |
| --- | --- | --- | --- |
| **B1 Actuator trunk** | Plan 001 U1: retire `J_ESC`/`J_SERVO` PWM, put ESCs and tilt actuators on the isolated CAN-FD / RS-485 trunk; write the bus-topology decision down. | avionics §1.10 U1 | `kicad` ERC/DRC no new violations |
| **B2 Pilot fab blocker** | U8 tamper-mesh creepage (13 DRC, 0.125 vs 8 mm); the 7 non-manufacturable footprints; PB2-P2 unwired-header root cause; ISOW1412 swap. | avionics §1.2a, §1.9.2 | Pilot DRC 0 hard |
| **B3 Gateway** | §1.9.3: re-route the MCU area after the RHB-32 retarget, MCU support parts, PA0/PA1 pull-up, PA18 pull-down, thermal vias, lanes 3/4; OPTIGA Trust M swap; 47/296 nets. | avionics §1.9.2, §1.9.3 | GW-1 DRC 0 hard |
| **B4 XO + Flight Engineer** | XO DRC clean-out (219 ERC / 154 DRC) + TPM land fix; Flight Engineer full PCB resync (213 DRC). | avionics §1.9.2 | DRC 0 hard each |
| **B5 Bus integration** | U2 Open-Secure-ESC tilt controller (REF-ESC-001; replaced the LibreServo_v4 variant 2026-09-17) on the trunk — `J_FLEX` transceiver now winch-only; U3 Open-Secure-ESC frames + governor rewrite; U6 endpoint authentication mapping. | avionics §1.10 U2/U3/U6 | `secure-controller-assurance` mapping per endpoint |
| **B6 Gerbers** | U7 for the Phase 5 set: Pilot ×2, XO ×2, Flight Engineer, CAN-PERIPH-GW-1 ×2, ENC-NACELLE-1 ×2. Commo and Observer are Phase 6. | avionics §1.10 U7 | Gerbers + `emc` pre-compliance pass per board |

### Stream C — Firmware to a flyable stack

The firmware WBS labels this "Phase 7 firmware"; that is the *firmware* numbering and it
is required for *build* Phase 5 — a stub cannot hover.

| Unit | What | Owner entry |
| --- | --- | --- |
| **C1 FC core** | EDF governor over CAN-FD (after B1/B5), tilt command + AK7455 closed loop (after D5), IMU/baro fusion, u-blox M10Q. | firmware §4.2 |
| **C2 CN core** | CAN-FD heartbeat + telemetry forwarding, signed-log write via the CPLD write-blocker, MAVLink routing. | firmware §4.3 |
| **C3 Both** | Role election, security message signing; AK7455 zero-cal procedure over the drive-shaft field (WA-R13). | firmware §4.4; avionics §1.9.1 |
| **C4 Gateway** | `CAN-PERIPH-GW-1` tilt-encoder firmware — the calibration spec cites a `tilt_encoder.c` that does not exist (docs §0.10.1 item 4). | avionics WBS (new entry needed) |

### Stream D — Regulatory and range readiness

Registration (Part 48), Part 107 currency, nav-light compliance, data plate, LAANC / area
check (docs §5.2); 49 MHz Part 15 §15.235 pre-compliance or leave the 49 MHz sub-modules
off for Phase 5 (docs §5.1). Skipper GCS: at minimum a working QGC + SiK link (gcs §4.5.2/3).

### Stream E — Physical build

Build-guide Phases 0–4 (85 open lines) after A9 has made them true, then the Phase 5
ladder (61 lines). Print in the Rev T PLA prototype scale first
(`docs/PROTO_PRINT_DAVINCI_JR.md`) to catch fit issues before CF-PETG.

## Ordering and dependencies

```text
D1..D5 (owner, one sitting)
   │
   ├─ A0 Mass truth ──────────────┐  (everything below cites its ledger)
   │                              │
   ├─ A2 ─┬─ A3 ─┬─ A1 (if D1=full) ─┐
   ├─ A4 ─┤      │                  ├─ A9 → E (Phases 0–4)
   ├─ A5 ─┤      └─ A6 ─────────────┘
   ├─ A7 ─┘                                       ┐
   │                                              ├─ Phase 5 ladder
   ├─ B1 → B5 → C1/C2/C3 ────────────────────────┤
   ├─ B2, B3, B4 → B6 (fab) ─────────────────────┤
   ├─ C4                                          │
   └─ D (regulatory), A8 (if D1=full) ───────────┘
```

A0 is first because every later number (leg length, T/W, servo torque, wire gauge) is
downstream of it. A1/A8 drop out under a hover-only D1.

## Verification contract

```text
/usr/bin/python3 tools/gen_todo_from_wbs.py --check      # federation in sync
/usr/bin/python3 tools/precommit_index.py --check
/usr/bin/python3 tools/validate_stls.py
/usr/bin/python3 tools/wing_root_deconflict.py
/usr/bin/python3 tools/wing_internal_clearance.py
/usr/bin/python3 tools/wing_spar_carrythrough.py
/usr/bin/python3 tools/cargo_bay_envelope.py
/usr/bin/python3 tools/landing_gear_wing_clearance.py --proud
/usr/bin/python3 tools/nacelle_mass_cg.py                 # exits non-zero while any variant strikes
/usr/bin/python3 tools/nozzle_linkage_check.py            # A1 only
```

Not automatable: KiCad ERC/DRC per board (`kicad` skill), FreeCAD tilt sweep at
−5/0/45/90/140°, bench tests (LG-06/14, actuator holding, AK7455 window), thrust-stand T/W.

## Definition of done (Phase 5 entry)

1. One AUW/CG ledger, cited by README, BOM and every analysis doc; hover T/W ≥ the D4 floor.
2. Every Phase 5 printed part passes `validate_stls.py` and is registered in
   `serenity_assembly.py`; no build-guide step names a retired part.
3. Pilot ×2, XO ×2, Flight Engineer, GW-1 ×2, ENC-NACELLE-1 ×2 at DRC 0 hard with gerbers.
4. FC firmware hovers in a bench HIL or on the tethered rig; CN logs are write-blocked.
5. Registration number applied, nav lights verified, pre-flight ABCD card current.

## Sources

`WBS.md`, `docs/WBS.md` §0.8–§0.10, §6.4; `airframe/wings-nacelles/WBS.md` §1.1.3–§1.1.5;
`airframe/landing-gear/WBS.md`; `avionics/WBS.md` §1.9–§1.10; `avionics/firmware/WBS.md`;
`docs/NOZZLE_DRIVE_TRADE.md` (2026-09-10 tail); `docs/WING_ATTACH_INTERFACE.md` §5;
`docs/MASS_AUDIT_CARGO_WING_ROOT.md`; plans 2026-08-25-001/-002, 2026-08-26-001,
2026-08-29-004/-005, 2026-08-30-001, 2026-09-06-001.

*Plan drafted by Claude (Claude Opus 5, Anthropic) under the author's direction,
2026-09-15, per `AGENTS.md` §3 AI attribution.*
