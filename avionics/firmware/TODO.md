# Serenity UAV — Avionics Node Firmware TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"That's a real shame, doctor. — Wash"*

---

### 4.2 — FC Node (Wash) — Phase 7 Firmware

- [ ] EDF ESC PID governor
- [ ] Nacelle tilt servo PWM generation
- [ ] IMU / barometer sensor fusion
- [ ] ToF sensor array management
- [ ] u-blox M10Q GNSS integration
- [ ] MIL-STD-1553B RT implementation
- [ ] TPM-bound attestation

### 4.3 — CN Node (Zoë) — Phase 7 Firmware

- [ ] CAN FD heartbeat and telemetry forwarding
- [ ] MIL-STD-1553B BC/RT tasks
- [ ] RS-485 inter-board messaging
- [ ] Ethernet RSTP ring management
- [ ] Signed-log write via CPLD write-blocker
- [ ] TPM-bound HMAC on all outbound AX.25 payloads
- [ ] Cargo control
- [ ] MAVLink routing configuration

### 4.4 — Both Nodes

- [ ] Node role election protocol
- [ ] Autonomous navigation
- [ ] OA integration
- [ ] GPS cross-check
- [ ] Security message signing

---