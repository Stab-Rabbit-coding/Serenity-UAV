# Serenity UAV Cargo Winch System Specification

**Author:** Claude (Haiku 4.5), with user direction  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Revision:** A (2026-07-27)  
**Status:** Active Design Specification

---

## Overview

The cargo winch system is a mechanical-electrical subsystem responsible for safe lowering and raising of a 4" × 3" × 3" (102 × 76 × 76 mm) cargo payload during flight or hover. The system implements a **fail-safe architecture** where the default state (no power) is fully locked, and power is required to permit payload release.

**Key Design Principles:**
- **Fail-safe by design:** spring-loaded ratchet engages without power; power required to disengage
- **Overload protection:** if hoisting force exceeds available lift capacity, the winch unwinds slowly to shed the load and prevent UAV dynamic instability
- **Redundant spool support:** spool is supported at both ends to prevent cantilever bending under load, not hung from the motor shaft alone
- **Centralized control:** the CAN-PERPH-GW gateway both controls the servo and monitors the ratchet catch state

---

## Mechanical Assembly

### Motor

**Part Number:** STS3215 digital servo motor  
**Datasheet Reference:** [REF-SENSOR-012]  
**Motor Specifications:**
- Operating voltage: 4.8 V – 6.0 V (configured for 5.4 V nominal, per Kaylee RAIL-2)
- Torque: [consult datasheet for static/dynamic/stall torque]
- Speed: [consult datasheet for no-load RPM]
- Mass: [consult datasheet]
- Shaft type: standard servo spline
- Control interface: PWM (1000–2000 µs pulse width per servo standard)

**Mounting:** Integrated into `cargo_winch_motor_mount` (CF-PETG, printed assembly)

### Spool Assembly

**Spool Geometry:**
- Diameter: [to be confirmed from printed STL mesh]
- Material: PETG (printed)
- Cable capacity: sufficient for 1500+ mm unwind (payload ~1 m below fuselage during landing / hover maneuvers)
- Bearing support: **two flanged ball bearing supports at spool ends** (not shaft-hanging only)

**Bearing Specification:**
- Type: [TBD] flanged bearing, shaft bore to suit spool axle
- Support architecture: inboard bearing (left) + outboard bearing (right), both retained in printed bearing pockets bonded to cargo section interior
- Load rating: [TBD] minimum 50 lbf (222 N) radial at 1500 mm unwind (payload mass × gravity + pendulum dynamic)

### Safety Ratchet

**Ratchet Type:** Normal-open (fail-safe-locked) spring-loaded pawl and gear

**Engagement Behavior:**
- **Default (no power):** spring holds pawl engaged on spool drive gear; spool cannot rotate aft (winding)
- **With power (servo retracts catch):** pawl disengages from gear; spool free to rotate during controlled unwind

**Spring Specification:**
- Type: compression spring
- Force at rest: sufficient to hold pawl against spool drive gear with a minimum safety margin of 2:1 (total pawl force ≥ 2× expected payload retraction load)
- Pre-load: set such that ratchet holds under static 50 lbf (222 N) axial load without power
- Material: stainless steel (corrosion resistance; see AGENTS.md security/EMI hardening context)

**Pawl Geometry:**
- Drive gear teeth: conical or curved profile to ease disengagement
- Pawl tip radius: sized for ≤ 90° tooth angle to prevent jam during rapid disengagement
- Catch surface: hardened (case-hardened steel or equivalent) to resist wear

### Cable and Attachment

**Cable Type:** Dyneema UHMWPE (0.25 in / 6.35 mm diameter, rated ≥ 500 lbf / 2224 N minimum breaking strength)  
**Cable Attachment to Spool:** through-hole crimp or permanent splice (not releasable during flight)  
**Gondola Attachment:** QD-pin release (allows manual separation on ground) or permanently spliced depending on mission (TBD per Phase 8 payload integration)

---

## Control System

### Electrical Integration

**Power Rail:** RAIL-2 5V_JAYNE (Kaylee secondary BEC), ≥ 2.4 A typical / ~4.2 A peak per Phase 8 plan

**Control Gateway:** CAN-PERPH-GW (n=1 instance)

**Signal Connections:**
| Signal | Type | From/To | Function |
|--------|------|---------|----------|
| `WINCH_PWM` | Output | CAN-PERPH-GW → STS3215 | Servo position command (1000–2000 µs) |
| `RATCHET_SENSE` | Input | Ratchet limit switch → CAN-PERPH-GW | Pawl state feedback (engaged/disengaged) |
| `LOAD_SENSE` (Optional) | Input | Tension load cell → CAN-PERPH-GW | Payload mass monitoring (firmware-level overload trigger) |

**CAN-FD Bus:** All state/telemetry published over the shared CAN-FD trunk (Simon's Medbay is payload-primary per PACE table, with fallback to Shepherd watchdog for timeout/fault detection).

### Failsafe Behavior

#### Scenario 1: Normal Lowering (Hover Cargo Drop)

1. **Pre-drop state:** ratchet engaged (pawl held by spring); spool locked
2. **Operator command:** Ground Control Station (Malcolm) sends "DEPLOY_CARGO" via Wi-Fi → Shepherd (primary comms) → Simon (payload primary)
3. **Simon firmware:** sets `WINCH_STATE` = UNLOCKING; sends CAN-FD command to CAN-PERPH-GW
4. **CAN-PERPH-GW:** drives `WINCH_PWM` to 1500 µs (neutral) + signals servo to move 45° to retract catch
5. **Ratchet response:** spring-loaded pawl retracts; spool free to rotate
6. **Spool unwind:** payload descends at controlled rate (spool rotational speed set by servo PWM duty)
7. **Ground contact:** landing-gear switch closes → Simon halts servo; ratchet re-engages by spring
8. **Post-drop:** payload disconnected (manual / QD-pin); winch ready for next cycle

#### Scenario 2: Overload Protection (Force Exceeds Hoisting Capacity)

1. **During unwind:** payload mass or dynamic load exceeds the 50 lbf (222 N) lifting margin (e.g., snagged on terrain during low hover)
2. **CAN-PERPH-GW firmware detects:** `LOAD_SENSE` ADC input exceeds threshold (if load cell present) OR servo stall current exceeds 1.5 A for >500 ms
3. **Response:** CAN-PERPH-GW holds or slowly opens `WINCH_PWM` toward 2000 µs (full extend) at a de-rated ramp rate (≤ 5° servo rotation per second) → spool unwinds slowly
4. **Result:** cable unwinds and slack; payload descends/falls away; aircraft is not fouled by taut cable
5. **Telemetry:** CAN-PERPH-GW publishes `WINCH_STATE` = OVERLOAD to Simon; Simon logs event and alerts GCS

#### Scenario 3: Power Loss / Comms Failure

1. **Watchdog timeout:** Shepherd (primary watchdog per PACE table) detects loss of Simon heartbeat for >1 second
2. **Failsafe action:** Shepherd's firmware cuts power to the 5V_JAYNE rail (Kaylee BEC)
   - OR: CAN-PERPH-GW reverts to a default PWM hold (neutral ≈ 1500 µs) and does not command spool unlock
3. **Ratchet remains engaged** (spring-locked without power)
4. **Payload hanging:** safe state for glide descent or manual recovery

---

## Mechanical Design Tasks

### Current Status
- [x] `cargo_winch_motor_mount` (CF-PETG) — generated 2026-05-30, PR #21
- [x] `cargo_winch_spool` (PETG) — generated 2026-05-30, PR #21
- [ ] **Spool bearing pocket details** — bosses in `cargo_sect_shell24.scad` for bearing retention (left + right)
- [ ] **Ratchet gear profile** — design the spool drive gear (conical teeth for smooth engagement/disengagement)
- [ ] **Pawl lever and spring** — mechanical design with stress analysis (FOS ≥ 2 under max load)
- [ ] **Cable routing** — through-hole geometry from spool to cargo bay door/exit; strain relief at spool
- [ ] **Stress analysis** — FEA on spool axle + bearing mounts under 50 lbf (222 N) load at max unwind length (1500 mm)
- [ ] **Servo linkage** — mechanical design of pawl-return lever (servo torque × lever arm ≥ spring force + friction)
- [ ] **Testing checklist** — bench test ratchet locking/unlocking cycles at 5.4 V nominal; confirm spring hold over 100 cycles

### Manufacturing Notes
- **Bearing pockets:** sized for M3 grub-screw retention (integrated boss in printed shell, ref. `cargo_sect_shell24.scad` revision history)
- **Spool axle:** CF or stainless steel rod, both ends threaded for bearing inner races or snap-ring retention
- **Ratchet assembly:** assembled post-print; spring and pawl installed in a pocket carved into the spool or a separate cage bolted to spool OD
- **Cable exit:** smooth radius (~10 mm) to prevent fraying; strain relief clamp every 50 mm along internal cable run

---

## Electrical Integration

### Power Budget

**Winch subsystem power:**
- STS3215 servo (nominal 5.4 V, 1.5 A when moving, 0.2 A idle): ~8 W during unwind
- CAN-PERPH-GW (firmware running, PWM + CAN-FD): ~0.5 W
- Load cell ADC interface (optional, 100 mA @ 5.4 V): 0.5 W (if present)

**Total:** ~9 W peak, allocated to RAIL-2 5V_JAYNE per Phase 8 plan  
**Reserve margin:** 4.2 A − 1.8 A nom. = 2.4 A headroom (sufficient for servo surge + regulator transient losses)

### CAN-FD Message Protocol

**Published by CAN-PERPH-GW:**

```
WINCH_STATUS (ID: 0x7B0, 8 bytes, 10 Hz)
  Byte 0: WINCH_STATE enum
    0x00 = LOCKED (ratchet engaged, default)
    0x01 = UNLOCKING (servo moving, pawl retracting)
    0x02 = UNLOCKED (spool free to rotate)
    0x03 = OVERLOAD (load exceeded, unwinding slowly)
    0x04 = ERROR (fault detected)
  Byte 1: Servo position (0–255, mapping 1000–2000 µs)
  Bytes 2–3: Load cell ADC raw (if present; 0xFFFF = not installed)
  Bytes 4–5: Reserved
  Byte 6: Error flags (bit 0 = stall, bit 1 = comms timeout, bit 2 = load sensor fault)
  Byte 7: Checksum (HMAC-SHA256 truncated to 1 byte per CAN frame format)
```

**Subscribed by Simon (payload-primary) and Shepherd (watchdog backup):**

- Simon monitors `WINCH_STATUS` for state transitions and error flags; publishes `WINCH_COMMAND` to CAN-PERPH-GW
- Shepherd monitors `WINCH_STATUS` for overload/error states; initiates failsafe power cut if timeout >1 s

**Published by Simon:**

```
WINCH_COMMAND (ID: 0x7B1, 4 bytes, edge-triggered)
  Byte 0: Command enum
    0x00 = HOLD (servo neutral, maintain current ratchet state)
    0x01 = UNLOCK (servo move to pawl-retract position)
    0x02 = LOCK (servo move to pawl-engage position)
    0x03 = ABORT (cut power to servo, ratchet spring-engages)
  Byte 1: Payload (if applicable; e.g., unwind rate in % if firmware supports speed control)
  Bytes 2–3: Checksum
```

---

## References

[REF-SENSOR-012]: STS3215 Digital Servo Motor — Specification and Control Interface  
*Status: PENDING — datasheet at `docs/references/108090023_STS3215-C001_Datasheet.pdf`*

**Standards and Regulations:**
- [REF-NIST-001 §2.1, §3.3] — NIST SP 800-207 Zero Trust Architecture (applies to signed CAN-FD telemetry)
- [REF-ASTM-001] — ASTM F2910-22 § 4.3 "Cargo Handling and Release Systems" (if applicable to FAA certification path)

**Project References:**
- AGENTS.md § 1 (propulsion baseline, mass budgets)
- docs/POWER_DISTRIBUTION.md § 3.2.1 (Kaylee RAIL-2 5V_JAYNE architecture, cross-tie fusing)
- docs/JAYNE_LASER_ANALYSIS.md (related cargo-subsystem payloads and sensor integration)
- airframe/fuselage-mid/WBS.md § 1.1.1.2.1 (cargo handling geometry and STL generation)
- avionics/jayne/WBS.md § 1.2c (Jayne PCB Simon's Medbay payload-primary assignment)

---

## Open Items / TBD

- [ ] STS3215 datasheet review: confirm torque, speed, stall current, mass
- [ ] Load cell selection (optional): sensor range, ADC interface, calibration
- [ ] Ratchet gear tooth profile: conical vs. involute; tooth pitch; material (steel grade)
- [ ] Spring constant and pre-load: detailed FEA to confirm FOS ≥ 2
- [ ] Servo linkage ratio: lever arm length to ensure servo torque exceeds spring force
- [ ] Cable routing path: full length estimate from spool through cargo bay
- [ ] Overload threshold tuning: baseline at 50 lbf (222 N); may adjust post-bench test
- [ ] Payload release mechanism: manual QD pin vs. motorized solenoid (Phase 8 decision)
- [ ] Phase 8 build schedule: integration with cargo gondola shell and avionics harness

---

*"She's a good gun." — Jayne Cobb*

"Everything is shiny." — Kaylee Frye (winch power coordination)
