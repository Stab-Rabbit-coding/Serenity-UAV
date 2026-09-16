# Serenity UAV — First-Flight Readiness: Open-Item Rollup

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0  
**Compiled:** 2026-09-15 by Claude (Claude Opus 5, Anthropic) under the author's
direction, from the `TODO.md` federation as regenerated that day by
`tools/gen_todo_from_wbs.py` (baseline Rev T, `docs/WBS.md` §6.4; head `48835ae`).
**Supersedes:** the 2026-07-05 snapshot of this file (Rev S, Opus 4.8), which had
carried two stale-warning banners since 2026-08-22.

> **First flight = master WBS Phase 5, "Minimum Viable Flyer."** CN1+FC1 (Shepherd's
> room / Bay A) and CN2+FC2 (Inara's shuttle / Bay B) installed and flying — a 4-node VTOL
> hover, then the Phase 5 test ladder. The aft EDF (Phase 11), the remaining 4 nodes
> (Phase 6), the cargo winch mechanism (Phase 7) and Observer vision (Phase 6+) are
> **not** first-flight gates. The cargo *doors* are (plan 2026-08-25-002 KTD2).
>
> **The ordered plan this report rolls up is
> [`docs/plans/2026-09-15-001-first-flight-readiness-plan.md`](plans/2026-09-15-001-first-flight-readiness-plan.md).**
> It opens with five owner decisions (D1–D5) that no agent can make; nothing below moves
> far until those are taken.

*"Define 'interesting.'" / "Oh God, oh God, we're all gonna die?" — Pilot & Skipper*

---

## 1. Hard blockers (each stops the build or the flight outright)

| # | Blocker | Where it lives | Unblocked by |
| --- | --- | --- | --- |
| 1 | **Mass truth.** BOM printed-part masses understated by +521.6 g (13.3 % AUW); category-level check suggests true AUW 5.6–5.8 kg vs the 3,911 g README figure; hover T/W ≈ 1.14–1.19 vs a 1.2 floor. Every downstream number cites this. | root `TODO.md` §0.8.1 MA-1/WA-R18; `docs/MASS_AUDIT_CARGO_WING_ROOT.md`; `docs/WBS.md` §0.10.2 item 3 | Plan A0 + decision D4 |
| 2 | **Nozzle drive datum.** KTD3's trunnion-fixed sun has no axial home in the as-built joint (bearing-stack margin **0.0 mm**); every lever is at a floor. | `airframe/wings-nacelles/TODO.md` §1.1.3.1 `[BLOCKED]`, §1.1.5 SPAR-25-5; `docs/NOZZLE_DRIVE_TRADE.md` "What is blocked" | Decision D2 (or D1 = hover-only, which pins the iris) |
| 3 | **Tilt actuator is the wrong device and the train is not self-locking.** Multi-turn reduction ⇒ gearmotor/stepper on the AK7455; WA-R16 has no holding provision. | root `TODO.md` §0.8 "Actuator re-select", §0.8.1 WA-R16; `docs/TILT_DRIVE_CONTROL_SPEC.md` §5.2/§7.3 | Decision D5 + plan A2 |
| 4 | **Landing gear.** The 1.5 in leg strikes the nozzle at `PIVOT_Z` 107.5; the 3.0 in leg clears by 33 mm but is not the active variant. | `airframe/landing-gear/TODO.md` LG-31, LG-HOVER-01 | Decision D3 |
| 5 | **Nacelle print-blocking.** `MOTOR_BOLT_R` 10.0 mm and a 3-arm spider against a 4-screw motor; bolt circle unpublished. | `airframe/wings-nacelles/TODO.md` §1.1.3.8 | Five minutes with a caliper on a real motor (plan A3) |
| 6 | **Pilot fab blocker.** Tamper mesh at 0.125 mm vs 8 mm creepage (13 DRC); 7 non-manufacturable footprints; PB2-P2 header unwired in ERC. | `avionics/TODO.md` §1.2a/§1.9.2; plan 001 U8 | Plan B2 |
| 7 | **Gateway unrouted.** MCU area dangling after the RHB-32 retarget; lanes 3/4 absent; 47/296 nets. | `avionics/TODO.md` §1.9.3 | Plan B3 |
| 8 | **Flight controller is a stub.** No governor, tilt command, IMU/baro fusion or GNSS. | `avionics/firmware/TODO.md` §4.2 | Plan C1 (after B1/B5) |
| 9 | **Build guide describes deleted hardware.** Phase 2/3 steps name the sector gear, bevel pair, crown pinion, MF104ZZ bearings and 4 mm pivot rod — none exist at Rev T. | `graphical-build-guide/TODO.md` Phases 2–3 | Plan A9 |

## 2. Critical-path branches — open counts (2026-09-15)

| Master § | Branch | Open | Owning TODO | First-flight scope note |
| --- | ---: | ---: | --- | --- |
| §0.8 / §0.8.1 | Allowables, actuator, wing-attach residuals | 10 + 13 | root | CF spar cert, actuator re-select, WA-R16/R18, MA-1 are all gates |
| §1.1.1 | Fuselage (joints / covers / mid) | 12 + 0 + 60 | `airframe/fuselage-*/TODO.md` | Doors, ramp fairing, access covers gate; winch (≈18 lines) is Phase 7 |
| §1.1.2–§1.1.5 | Wings, nacelles, tilt-spar, trunnion | 35 | `airframe/wings-nacelles/TODO.md` | Blockers 2, 3, 5 above; ESC-bay safety findings |
| §1.1.4 | Landing gear | 22 | `airframe/landing-gear/TODO.md` | Blocker 4; LG-15/16 wire, LG-06/14 tests |
| §1.1.5 | Placeholders / assembly | 10 | `airframe/TODO.md` | Hull-frame placements for VERIFY parts |
| §1.2a–d, §1.9, §1.10 | Avionics PCBs + close-out plan | 51 + 3 | `avionics/TODO.md`, `rev-s1` | Blockers 6, 7; Phase 5 set = Pilot ×2, XO ×2, FE, GW-1 ×2, ENC ×2 |
| §1.4 | EMI hardening beyond the PCBs | 26 | `avionics/emi-hardening/TODO.md` | Benign-environment maiden hover may precede full close-out — annotate the risk |
| §4.2–§4.4 | Firmware (FC / CN / both) | 7 + 8 + 5 | `avionics/firmware/TODO.md` | Blocker 8 |
| §4.5 | Skipper GCS | 34 | `gcs/TODO.md` | Minimum: QGC + SiK link (§4.5.2/3); gimbal/tracking are not gates |
| §5.1–§5.3 | Regulatory | 1 + 6 + 3 | `docs/TODO.md` | Registration, Part 107, nav lights, data plate are legal gates |
| Phase 0–4 | Physical build | 16 + 23 + 23 + 12 + 11 | `graphical-build-guide/TODO.md` | After blocker 9 |
| **Phase 5** | **Minimum Viable Flyer** | **61** | `graphical-build-guide/flight-phases/TODO.md` | The flight itself |

**Not on the path:** §1.2c Observer (34), §1.5 documentation (3), Phase 6–12 (126),
`deferred/` (48), §0.10 documentation audit residuals (7).

## 3. What changed since the 2026-07-05 snapshot

- **Wings Rev S1g:** the rotating 8 mm steel spar the old report described is gone; the
  spar is a bonded 20 × 16.3 mm CF tube, the root joint is socket + flange (FOS 29.2), the
  cargo bay stays clear, `wing_root_deconflict.py` is CLEAR.
- **Nacelles Rev S4c/S4d:** trunnion pivot on 2 × 6704ZZ with an integral 50T ring gear;
  pods hollowed (−179 g/pair); hinged ESC bays with four flush covers; 4 × 90° motor
  pattern; `PIVOT_Z` 107.5 after the ESC-aft lever proved not to exist.
- **Nozzle drive:** the passive wing-fixed-sun linkage is *solved* (crank 8.5 mm, pushrod
  48 mm, module 0.8, tooth FOS 4.43) and then found to have no axial home — blocker 2.
- **Landing gear:** sponson wells closed; 1.5 in leg not viable, 3.0 in retained.
- **Flaps:** 40 → 30 mm (plan 005 R1), +10 mm hover clearance; alternate flaps seal-lapped.
- **Mass:** the +521.6 g under-count (MA-1) was found; the old report's T/W 1.61 → README
  1.14 → provisional 1.19 after Rev S1g, all pending A0.
- **Documentation:** Rev T checkpoint pinned; TODO federation now generated from WBS.

## 4. How to use this report

1. Take decisions D1–D5 (plan §"Decisions the owner must make first").
2. Run plan stream A0 (mass truth) before anything that cites a mass, a torque or a T/W.
3. Work streams A–D per the plan's dependency graph; close items in the owning `WBS.md`,
   then `/usr/bin/python3 tools/gen_todo_from_wbs.py` to regenerate the open-items views.
4. Regenerate this report's counts from the `TODO.md` files when the plan is re-baselined;
   `WBS.md` is always authoritative, this is a rollup.
