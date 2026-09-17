# Serenity UAV — Avionics Node Firmware TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"That's a real shame, doctor. — Pilot"*

---

### 4.2 — FC Node (Pilot) — Phase 7 Firmware
→ full detail: `WBS.md` §4.2

- [ ] EDF ESC PID governor — BDSHOT600 telemetry input on PRU-ICSS, EHRPWM…
- [ ] Nacelle tilt servo PWM generation — EHRPWM or PRU
- [ ] IMU / barometer sensor fusion — ICM-42688-P (SPI), BMP388/BMP390 (SPI)
- [ ] ToF sensor array management — VL53L5CX ×6 per node via TCA9548A I²C…
- [ ] u-blox M10Q GNSS integration — UART NMEA/UBX parse
- [ ] MIL-STD-1553B RT implementation — PRU-ICSS Manchester II…
- [ ] TPM-bound attestation — SLB9672 TPM 2.0 HMAC on all outbound…

### 4.3 — CN Node (XO) — Phase 7 Firmware
→ full detail: `WBS.md` §4.3

- [ ] CAN FD heartbeat and telemetry forwarding — broadcast 0x001–0x008…
- [ ] MIL-STD-1553B BC/RT tasks — BC on CN1 (standby), RT on CN2–CN4
- [ ] RS-485 inter-board messaging — structured message format…
- [ ] Ethernet RSTP ring management — CPSW3G bridge configuration
- [ ] Signed-log write via CPLD write-blocker — log records written as…
- [ ] TPM-bound HMAC on all outbound AX.25 payloads
- [ ] Cargo control — DRV8833 winch H-bridge, HX711 load cell (payload…
- [ ] MAVLink routing configuration — mavlink-router config

### 4.4 — Both Nodes
→ full detail: `WBS.md` §4.4

- [ ] Node role election protocol — CAN FD priority arbitration at boot
- [ ] Autonomous navigation — 3-waypoint GPS mission execution
- [ ] OA integration — ToF halt trigger feeds into navigation
- [ ] GPS cross-check — 4 GPS receivers (one per FC node)
- [ ] Security message signing — every inter-node CAN FD message signed

---
