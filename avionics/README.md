# Serenity UAV — Avionics Subsystem

**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0  
**Current design revision:** Rev T (2026-09-06, see `docs/WBS.md` §6.4 for changelog)

> Avionics subsystem for the Serenity UAV: 8-node cooperative flight control,
> PACE failover architecture, EMI-hardened PCBs, multi-link comms (CAN FD, RS-485,
> Ethernet, 49 MHz / LoRa), and signed telemetry logging with hardware-enforced
> write protection.

## Architecture Overview

**8-Node PACE Failover System** (Primary / Alternative / Contingency / Emergency):

| Stack | Watchdog | Comms | Flight Control | Payload |
|-------|----------|-------|----------------|---------|
| Shepherd (Bay A) | P | A | C | E |
| Inara (Bay B) | A | P | E | C |
| River (Bay C) | C | E | P | A |
| Simon (Bay D) | A | C | A | P |

Each node runs a **PocketBeagle2 Industrial (PB2-I) SBC** carrying:
- **Pilot** cape: flight control + sensor interface (Cape-A-2, Rev S1)
- **XO** cape: comms/logging/payload interface (Cape-B-2, Rev S1)
- Optional: **Commo** cape (49 MHz + LoRa transceiver) on Shepherd and River only

**Flight Engineer** (Power Distribution Board) sits in the middle-section inner neck, minimizing
power-run length to all four nacelles and the battery.

**Observer** (standalone vision/ToF/laser board, Rev S1) installs at nose and cargo-bay mounting
sites, connected via the Ethernet ring and CAN FD trunk.

## Onboard Bus Architecture

| Bus | Protocol | Nodes | Purpose |
|-----|----------|-------|---------|
| CAN FD | 1 Mbps nominal / 8 Mbps data | 8 nodes | Primary telemetry, ESC heartbeat, sensor fusion, failover signaling |
| RS-485 | Half-duplex | 8 nodes | Backup command/telemetry (fallback if CAN FD fails) |
| Ethernet | RSTP ring | 8 nodes (via Pilot's dual PHYs, J_ETH1/J_ETH2) | High-bandwidth sensor data, inter-node video/imaging streams |
| MIL-STD-1553B | Dual redundant buses | All 8 nodes | Deterministic real-time control (legacy compatibility, backup) |
| UART | Various | Cape headers | Serial debugging, bootloader, optional mission-specific sensors |

## External Comms (4 Independent Paths)

All four paths are **authenticated, signed, logged**:

1. **Wi-Fi 5 GHz** — MAVLink to QGroundControl; primary for higher-bandwidth development
   flights; range limited (<500 m line-of-sight)
2. **ZigBee 2.4 GHz** — MAVLink fallback; robust link in congested RF environments
3. **MAVLink/SiK 915 MHz** — Licensed ISM band; range ~5 km (open field, typical line-of-sight);
   serves as secondary autonomous-mission link
4. **49 MHz (Part 15 §15.235)** — Unlicensed, extremely low power (~30 µW EIRP); forward and
   aft wire antennas (see `XCVR-49MHZ` in BOM); carries encrypted command/telemetry; requires
   FCC pre-compliance (energy-limited but not power-limited per Part 15)

## PCB Boards (Rev S1 Baseline)

### Pilot (Cape-A-2) — Flight Control + Sensors
- **Processor:** PocketBeagle2 Industrial (Cortex-A53, dual PRU real-time subsystem)
- **Sensors:** 9-DOF IMU, barometric altimeter, GPS (u-blox M10Q), 2× real-time tilt encoders
  (AK7455 magnetoresistive, off-axis / ferrous-through-shaft) for nacelle tilt feedback
- **Motor Control:** 4× PWM outputs (ESC1–4) for nacelle EDFs; isolated gate drivers
- **Actuators:** Servo outputs for tilt servos, door servo, winch servo
- **Isolation:** Galvanic isolation on all external buses (CAN FD, RS-485, Ethernet) via
  5 kV iso-gate chips and transformers (EMI-hardening per Rev S)
- **Security:** TPM 2.0 (SLB9672) for attestation; CPLD write-blocker on log μSD

### XO (Cape-B-2) — Comms / Logging / Payload
- **Radios:** SiK 915 MHz (RFD900x), LoRa SX1262 (optional expansion), dedicated UART for
  49 MHz transceiver module (XCVR-49MHZ-1/2)
- **Logging:** eMMC mass storage (OS + runtime logs); μSD slot (flight logs, write-blocked)
- **Payload Interface:** GPIO headers for cargo door/winch servo control, analog/digital
  sensor expansion (TCA9548A I²C multiplexer for ToF arrays, temp sensors, etc.)
- **Isolation:** 5 kV galvanic isolation on all buses
- **Security:** TPM 2.0; CPLD write-blocker on μSD

### Commo — 49 MHz + LoRa Transceiver
- **Dual radios:** 49 MHz transceiver (SI5351-based, tunable PLL, ~30 µW max EIRP) + LoRa
  SX1262 as secondary low-power link for extended range in Phase 10+
- **Installed only on:** Shepherd's room (Shepherd node, Bay A) and River's room (River node,
  Bay C) — maximizes antenna diversity and geographic spread for robust long-range comms
- **Isolation:** 5 kV galvanic isolation

### Flight Engineer (Power Distribution Board) — Rev S1
- **Inputs:** Dual 6S LiPo battery rails (independent, cross-tied with fault tolerant diodes)
- **Outputs:** Dedicated 5V / 5A BEC for servo/sensor rail; 12V tap for future expansion
- **Protection:** 40A main fuses (one per battery rail); over-current monitoring on 5V rail
- **Placement:** Middle-section inner neck (ventral, open access for field maintenance)

### Observer (Vision / ToF / Laser Board) — Rev S1
- **Vision:** TI AM62A7 SoC (PCM-071 SoM carrier) with ISP/VP8 encoder for onboard H.265 video
- **ToF Sensors:** TFmini-S UART (nose) + 12× VL53L5CX (8×2 Array) for obstacle avoidance and
  precision landing  
- **Laser Indicators:** Two Class 2 green (520 nm) laser modules — nose (safety-interlocked) +
  cargo bay (unrestricted; for payload crosshair metrology)
- **Comms:** Gigabit Ethernet (KSZ9477 switch), CAN FD, TPM 2.0 for signed image metadata
- **Mounting:** Nose sensor pod + cargo-bay FPV housing; connected via shielded Ethernet ring

## Firmware

### Node Firmware (`avionics/firmware/`)

- **serenity-cn** (Comms Node) — runs on XO/Cape-B boards (all 8 nodes)
  - CAN FD heartbeat relay and telemetry forwarding
  - RS-485 backup messaging
  - Ethernet RSTP ring management  
  - Signed-log write via CPLD write-blocker
  - Radio (49 MHz, SiK, LoRa) telemetry encoding/decoding
  - Cargo control GPIO sequencing
  - MAVLink routing configuration

- **serenity-fc** (Flight Control) — runs on Pilot/Cape-A boards (4× FC nodes: Shepherd, Inara, River, Simon)
  - ESC PID governor (nacelle thrust control)
  - Nacelle tilt servo PWM generation + sync across all 4 nacelles
  - IMU + barometer + GPS sensor fusion
  - 12× ToF sensor array fusion for obstacle avoidance
  - MIL-STD-1553B Bus Controller (Shepherd primary) / Remote Terminal (backup FC nodes)
  - Autonomous waypoint navigation (GPS + IMU)
  - failover detection and graceful mode transitions

### Ground Station Firmware (`gcs/`)

- **Skipper** (GCS PB2-I + comms node) — antenna gimbal tracking, telemetry decoding, mission
  planning interface; integrates QGroundControl via MAVLink-router

## Security & Integrity

- **Every message signed:** all CAN FD, RS-485, MIL-1553, and radio packets carry HMAC-SHA256
  signatures bound to TPM attestation keys (one per node)
- **Zero-trust comms:** every external command verified against key material before execution
- **Tamper-evident logging:** flight logs write to μSD via CPLD-mediated write-blocker
  (hardware-enforced, no post-flight modification)
- **EMI hardening:** all PCBs conform to NIST SP 800-207 (zero trust) and IEC 62368-1 creepage/
  clearance specs; all external connectors shielded; rated for operation in 500 W/m² RF
  environment

## Documentation Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Avionics subsystem policy: PCB design, firmware architecture, comms topology |
| `kicad/` | KiCad 9 source schematics and PCB layouts (all boards, production-ready) |
| `firmware/` | C source code for Pilot/XO node firmware; CMake build system |
| `kicad/Observer/` | Observer board specs, TI SoC bring-up scripts, laser/ToF driver code |
| `emi-hardening/` | EMI isolation analysis, shielding specs, harness routing rules |
| `rev-s1/` | Rev S1 PCB redesign notes: Commo/XO/Flight Engineer PCB evolution |

## References

- **Regulatory:** [REF-FAA-001] 14 CFR Part 48, [REF-FAA-002] Part 107, [REF-FAA-003] §91.209,
  [REF-FCC-001] 47 CFR Part 15, [REF-FCC-003] §15.235
- **Security:** [REF-NIST-001] NIST SP 800-207 (Zero Trust), [REF-NIST-002] SP 800-82 (Cybersecurity
  for Industrial Control Systems), [REF-NIST-003] SP 800-160 (Systems Security Engineering)
- **IC standards:** [REF-IEC-001] IEC 62368-1 (EMI / Creepage & Clearance), [REF-IEEE-001] IEEE 802.15.4
  (ZigBee)

See root [`REFERENCES.md`](../REFERENCES.md) for complete reference catalog.

## License

**Hardware (PCB schematics, layouts, Gerbers):** CERN-OHL-W 2.0  
**Firmware and Scripts:** CC BY-SA 4.0  
**All documentation:** CC BY-SA 4.0

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for full licensing details.

---

*"Can't stop the signal." — River Tam*
