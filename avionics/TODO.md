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

##### 1.2a.1 *Cape DRC / routing / ETH2 status (2026-06-12)* — see `avionics/kicad/README.md`
→ full detail: `WBS.md` §1.2a

- [ ] Verify/add I2C1 pull-ups (≈4.7 kΩ to +3V3 on SDA/SCL) — none on cape
- [ ] Finalise placement of U-GPIO/C-GPIO (added at a tentative location).
- [ ] Finalise ESC-PWM placement (added at a tentative location).
- [ ] Reconcile Pilot.md §14 field-connector table with the actual PCB…
- [ ] Wire the MIL-1553 connector + transformer
- [ ] Redesign the tamper mesh as a per-domain anti-tamper mesh (all 4…
- [ ] Carry the tamper signal over the link for the TPM-less boards
- [ ] Route the rearranged capes
- [ ] Clear residual DRC after mesh + routing (counts measured 2026-06-12…
- [ ] Finish Pilot PCB (CAPE-A-2) close-out pass:
- [ ] Add SBUS/UART DIP switch to Pilot — add a 2-position DIP (or…
- [ ] Generate Pilot gerbers — `CAPE-A-2.kicad_pcb` complete
- [ ] Generate XO gerbers — `CAPE-B-2.kicad_pcb` complete
- [ ] Zigbee RF chain was never actually added to XO
- [ ] Generate Commo gerbers — `XCVR-49MHZ-2.kicad_pcb` complete
- [ ] FCC Part 15 §15.235 pre-compliance checklist for Commo
- [ ] EMI isolation validation checklist — verify isolation barrier…
- [ ] Merge `claude/cape-em-harsh-variants-9Yfr1` → master after gerbers…
- [ ] Design Faraday cages / boxes to protect all PCBs
- [ ] Specify / implement tightly twisted pair bonded shielded wiring…

### Pilot footprint verification and schematic-first rebuild (2026-07-13/14)
→ full detail: `WBS.md` Pilot footprint verification and schematic-first rebuild (2026-07-13/14)

- [ ] Rebuild the 7 non-manufacturable Pilot footprints before fab
- [ ] Pilot SCHEMATIC-FIRST REBUILD — decided + started 2026-07-14 (user)

### §1.9.3 — Trust-Module MCU/TPM Retarget (MSPM0G351x-Q1 + SLB 9672), 2026-08-03
→ full detail: `WBS.md` §1.9.3

- [ ] Re-route the gateway MCU area
- [ ] Confirm MSPM0G351x-Q1 errata and TRM applicability
- [ ] Update firmware pinmux constants for the new family
- [ ] Add the missing MCU support parts per SLAAE76E Table 1-1
- [ ] Add a pull-up on the gateway's PA0/PA1 FLEX UART
- [ ] Pull PA18 down on the gateway and Observer
- [ ] Add thermal vias under the MCU exposed pad
- [ ] Resolve FlightEngineer's ground-net naming
- [ ] Clean up FlightEngineer's dangling no-connect flags
- [ ] Close the Observer sch↔pcb parity gap
- [ ] Place gateway lanes 3 and 4
- [ ] Decide whether Commo, Pilot and XO (formerly Emma, Wash, Zoë) follow…

## §1.10 — Avionics close-out plan (2026-08-25-001), unit index
→ full detail: `WBS.md` §1.10

- [ ] U1 — Retire Pilot `J_ESC`/`J_SERVO` PWM headers → CAN-FD/RS-485…
- [ ] U2 — LibreServo_v4 nacelle-tilt bus integration
- [ ] U3 — Open-Secure-ESC 50A/6S `CAN_485_faraday` integration + PID…
- [ ] U4 — OpenServoCore SG90 TTL+CMAC bus finalize
- [ ] U5 — Observer pitot-tube airspeed sensor (`J_PITOT`)
- [ ] U6 — Fleet host+message authentication wiring for ESC / tilt-servo /…
- [ ] U7 — Per-board ERC/DRC/gerber closeout (Pilot, XO, Commo, Flight…
- [ ] U8 — Pilot tamper-mesh creepage fix (13 DRC, 0.125 mm vs 8 mm
- [ ] U9 — REFERENCES.md, WBS/TODO and `avionics/AGENTS.md` closeout for…

### §1.9.2 — Fleet Trust Module (MCU + TPM + isolated CAN-FD + isolated RS-485)
→ full detail: `WBS.md` §1.9.2

- [ ] SLB9670→SLB9672 TPM migration — ERC/DRC not re-run, 2026-08-01
- [ ] ★ SLB9672 → OPTIGA™ Trust M, `CAN-PERIPH-GW-1` + Flight Engineer…
- [ ] `CAN-PERIPH-GW-1` PCB routing (updated 2026-07-26, post `N_STACKS=4`…
- [ ] Pilot: `PB2-P2` header appears fully unwired in ERC (all 36 pins…
- [ ] Pilot full DRC/ERC clean-out — not started
- [ ] XO full DRC/ERC clean-out — not started
- [ ] Flight Engineer full PCB resync — not started
- [ ] Observer PCB resync — not started

---
