# Serenity UAV — Avionics EMI Hardening TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"Everything is shiny, Cap'n. Not to fret. — FlightEngineer"*

---

#### 1.4.1 Faraday Enclosures
→ full detail: `WBS.md` §1.4

- [ ] PB2-I + Wash Enclosure
- [ ] PB2-I + TACCO Enclosure

#### 1.4.3 internode communication wiring
→ full detail: `WBS.md` §1.4

- [ ] CAN FD
- [ ] RS-485
- [ ] MIL-STD-1553B
- [ ] Ethernet

#### 1.4.4 flight control signal wiring
→ full detail: `WBS.md` §1.4

- [ ] UART
- [ ] I2C
- [ ] BDSHOT/DSHOT (ESC telemetry)
- [ ] PWM

#### 1.4.5 power distribution — FlightEngineer (PDB) and battery
→ full detail: `WBS.md` §1.4

- [ ] Add FlightEngineer/battery boss pattern to `middle_canonical_shell24.sc…
- [ ] Add ventral battery-swap hatch cut to `middle_canonical_shell24…
- [ ] Create `kaylee_battery_tray.scad`.
- [ ] Create `kaylee_pdb_tray.scad`.
- [ ] Update REVN_BUILD_GUIDE_24IN.md Phase 1

---