# Serenity UAV — Avionics EMI Hardening TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"Everything is shiny, Cap'n. Not to fret. — Flight Engineer"*

---

#### 1.4.1 Faraday Enclosures
→ full detail: `WBS.md` §1.4.1

- [ ] PB2-I + Pilot Enclosure (Shepherd's Room / Inara's Shuttle
- [ ] PB2-I + XO Enclosure (all 4 bays — TACCO, plus Commo in River's…

#### 1.4.2. Antenna Placement and feedlines
→ full detail: `WBS.md` §1.4.2

- [ ] Zigbee 2.4 GHz antenna mount — BLOCKED, hardware gap confirmed
- [ ] Verify the 6 dorsal mount stations (Shepherd ×2, Inara ×2, River's…
- [ ] Verify the 2 flank mount lines (River's 49 MHz, port
- [ ] Verify the exact shoulder-height Z offset in FreeCAD against the…
- [ ] Confirm the port/starboard mount line also clears the wing roots…
- [ ] Bench-verify isolation between the two 49 MHz antennas (River's…

#### 1.4.3 internode communication wiring
→ full detail: `WBS.md` §1.4.3

- [ ] CAN FD — specify bus topology (linear trunk vs
- [ ] RS-485 — specify daisy-chain topology, termination, and connector…
- [ ] MIL-STD-1553B — specify bus controller / remote terminal wiring per…
- [ ] Ethernet — specify CPSW3G ring topology (node-to-node order), cable…

#### 1.4.4 flight control signal wiring
→ full detail: `WBS.md` §1.4.4

- [ ] UART — specify wiring for GPS (u-blox M10Q NMEA/UBX, §4.2)…
- [ ] I2C — specify wiring for IMU/barometer (ICM-42688-P, BMP388/390
- [ ] BDSHOT/DSHOT (ESC telemetry) — specify wiring for the ESC-PWM…
- [ ] PWM — specify wiring for nacelle tilt servo control (EHRPWM/PRU…

#### 1.4.5 power distribution — Flight Engineer (PDB) and battery
→ full detail: `WBS.md` §1.4.5

- [ ] Add FlightEngineer/battery boss pattern to `middle_canonical_shell24.…
- [ ] Add ventral battery-swap hatch cut to `middle_canonical_shell24.scad`
- [ ] Create `flight_engineer_battery_tray.scad`
- [ ] Create `flight_engineer_pdb_tray.scad`
- [ ] DRC accepted violations (document only — not fixable without PCB…
- [ ] Flight Engineer PCB — remaining layout tasks (BLOCKS fabrication):
- [ ] Update REVN_BUILD_GUIDE_24IN.md Phase 1 to include Flight Engineer +…

#### 1.4.6 ferromagnetic structural elements — magnetic-sensor siting
→ full detail: `WBS.md` §1.4.6

- [ ] Hall tilt-encoder ↔ ferrous spar (`HALL-TILT-ENC`)
- [ ] Flight magnetometer / compass siting
- [ ] Add the ferrous-spar note to the build guide so the…

---
