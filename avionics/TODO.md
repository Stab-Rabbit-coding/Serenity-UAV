# Serenity UAV — Avionics (Wash / Zoe / Emma Cape Hardware) TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"I'm a leaf on the wind — watch how I soar. — Wash"*

---

#### ***EM hardening Objective is to ensure safe and controlled operations in hostile em/rf environments such as the vicinity of radiating commercial broadcast, amateur radio and cellular towers.***
→ full detail: `WBS.md` §1.2a

- [ ] Reconcile Wash.md §14 field-connector table with the actual PCB
- [ ] Wire the MIL-1553 connector + transformer.
- [ ] Redesign the tamper mesh as a per-domain anti-tamper mesh (all…
- [ ] Carry the tamper signal over the link for the TPM-less boards.
- [ ] Route the rearranged capes.
- [ ] Clear residual DRC after mesh + routing
- [ ] Finish Wash PCB (CAPE-A-2) close-out pass:
- [ ] Add SBUS/UART DIP switch to Wash
- [ ] Generate Wash gerbers
- [ ] Generate Zoë gerbers
- [ ] Zigbee RF chain was never actually added to Zoë — PCB scope gap…
- [ ] FCC Part 15 §15.235 pre-compliance checklist for Emma
- [ ] EMI isolation validation checklist
- [ ] Merge `claude/cape-em-harsh-variants-9Yfr1` → master
- [ ] Design Faraday cages / boxes to protect all PCBs
- [ ] Specify / implement tightly twisted pair bonded shielded wiring…

### Wash footprint verification and schematic-first rebuild (2026-07-13/14)
→ full detail: `WBS.md` §1.2a

- [ ] Wash footprint-vs-datasheet verification — DONE 2026-07-13 (Cla…
- [ ] Wash SCHEMATIC-FIRST REBUILD — decided + started 2026-07-14 (us…
- [ ] Finish Wash PCB (CAPE-A-2) close-out pass:

### Fleet Trust Module + Tilt Encoder (2026-07-26)

→ full detail: `WBS.md` §1.9.1, §1.9.2

- [ ] AK7455 firmware zero-calibration over −5..90° sweep
- [ ] Shielded encoder-to-gateway + gateway-to-bus wiring per EMI spec
- [ ] Reconcile gen_kaylee.py drift from checked-in Kaylee.kicad_sch
- [ ] Remove obsolete J_ENC (AS5600 I²C) connector from Wash
- [ ] Fix Wash's own inline SLB9670 symbol's incorrect pin numbers
- [ ] Finish routing CAN-PERIPH-GW-1 PCB (47/296 nets still unrouted)
- [ ] Wash PB2-P2 header appears fully unwired in ERC — root cause TBD
- [ ] Wash full DRC/ERC clean-out (48 ERC + 76 DRC hard) + ISOW1412 swap
- [ ] Zoë full DRC/ERC clean-out (219 ERC + 154 DRC hard) + ISOW1412 swap
- [ ] Review/remove stray tracked _autosave-Zoë.kicad_pcb + .lck files
- [ ] Kaylee full PCB resync to trust-module schematic (213 DRC hard)
- [ ] Jayne PCB resync — RS-485/Section H never reached layout (124 DRC)
- [ ] Emma: route TPM/R/C to the SPI1/TPM_IRQN/TPM_RSTN nets on P1/P2

---