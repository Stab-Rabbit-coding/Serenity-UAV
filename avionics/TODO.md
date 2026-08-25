# Serenity UAV — Avionics (Pilot / XO / Commo Cape Hardware) TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"I'm a leaf on the wind — watch how I soar. — Pilot"*

---

### Avionics close-out: actuator bus, SG90/OSC, Observer pitot (2026-08-25)
→ full detail: `docs/plans/2026-08-25-001-finish-avionics-plan.md`

- [ ] U1: Retire Pilot J_ESC/J_SERVO PWM headers → CAN-FD/RS-485 trunk
- [ ] U2: LibreServo_v4 nacelle-tilt bus integration (GW-1 J_FLEX gap)
- [ ] U3: Open-Secure-ESC 50A/6S CAN-FD integration + governor rewrite
- [ ] U4: OpenServoCore SG90 TTL+CMAC bus finalize (re-check maturity gate)
- [ ] U5: Add Observer pitot-tube airspeed sensor; fix Pilot's stale claim
- [ ] U6: Fleet host+message auth wiring for ESC/servo/SG90 endpoints
- [ ] U7: Per-board ERC/DRC/gerber closeout (Pilot/XO/Commo/FE/Obs/GW-1)
- [ ] U8: Tamper-mesh creepage fix (Pilot fab blocker) + Faraday/shielding
- [ ] U9: REFERENCES.md + WBS/TODO closeout for all of the above

---

#### ***EM hardening Objective is to ensure safe and controlled operations in hostile em/rf environments such as the vicinity of radiating commercial broadcast, amateur radio and cellular towers.***
→ full detail: `WBS.md` §1.2a

- [ ] Reconcile Pilot.md §14 field-connector table with the actual PCB
- [ ] Wire the MIL-1553 connector + transformer.
- [ ] Redesign the tamper mesh as a per-domain anti-tamper mesh (all bays)
- [ ] Carry the tamper signal over the link for the TPM-less boards
- [ ] Route the rearranged capes (after mesh design)
- [ ] Clear residual DRC after mesh + routing
- [ ] Finish Pilot PCB (CAPE-A-2) close-out pass
- [ ] Add SBUS/UART DIP switch to Pilot
- [ ] Generate Pilot gerbers (post-DRC)
- [ ] Generate XO gerbers (post-DRC)
- [ ] Zigbee RF chain was never added to XO — PCB scope gap (deferred)
- [ ] FCC Part 15 §15.235 pre-compliance checklist for Commo
- [ ] EMI isolation validation checklist
- [ ] Merge `claude/cape-em-harsh-variants-9Yfr1` → master
- [ ] Design Faraday cages / boxes to protect all PCBs
- [ ] Specify / implement tightly twisted pair bonded shielded wiring…

### Pilot footprint verification and schematic-first rebuild (2026-07-13/14)
→ full detail: `WBS.md` §1.2a

- [ ] Pilot footprint-vs-datasheet verification — DONE 2026-07-13 (confirmed)
- [ ] Pilot SCHEMATIC-FIRST REBUILD — decided + started 2026-07-14 (user-initiated)
- [ ] Finish Pilot PCB (CAPE-A-2) close-out pass:

### Fleet Trust Module + Tilt Encoder (2026-07-26)

→ full detail: `WBS.md` §1.9.1, §1.9.2

- [ ] AK7455 firmware zero-calibration over −5..90° sweep
- [ ] Shielded encoder-to-gateway + gateway-to-bus wiring per EMI spec
- [ ] Reconcile gen_flight_engineer.py drift from checked-in FlightEngineer.kicad_sch
- [ ] Remove obsolete J_ENC (AS5600 I²C) connector from Pilot
- [ ] Fix Pilot's own inline SLB9672 symbol's incorrect pin numbers
- [ ] Re-run ERC/DRC after SLB9670→SLB9672 migration (no KiCad here)
- [ ] ★ SLB9672→OPTIGA Trust M on CAN-PERIPH-GW-1 + Flight Engineer only
- [ ] Swap XO's TPM footprint (wrong 4x4mm/0.4mm land, needs 5x5mm/0.5mm)
- [ ] Finish routing CAN-PERIPH-GW-1 PCB (47/296 nets still unrouted)
- [ ] Pilot PB2-P2 header appears fully unwired in ERC — root cause TBD
- [ ] Pilot full DRC/ERC clean-out (48 ERC + 76 DRC hard) + ISOW1412 swap
- [ ] XO full DRC/ERC clean-out (219 ERC + 154 DRC hard) + ISOW1412 swap
- [ ] Review/remove stray tracked _autosave-XO.kicad_pcb + .lck files
- [ ] Flight Engineer full PCB resync to trust-module schematic (213 DRC hard)
- [ ] Observer PCB resync — RS-485/Section H never reached layout (124 DRC)
- [ ] Commo: route TPM/R/C to the SPI1/TPM_IRQN/TPM_RSTN nets on P1/P2

---