# Serenity UAV — Avionics Subsystem

**License:** CERN-OHL-W 2.0 (hardware) / CC BY-SA 4.0 (documentation, firmware, scripts) —
see [License](#license) below.  
**Current design revision:** tracked per board, not subsystem-wide — see "PCB Boards" below and
each board's own `avionics/kicad/<board>/<board>.md` status file for its current revision and
sch↔PCB parity state. `avionics/WBS.md` carries the subsystem-wide work breakdown (no changelog
section number is stable enough to cite here; search the file instead of citing a section).

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

- **Pilot** cape: flight control + sensor interface (Cape-A-2)
- **TACCO** cape: comms/logging/payload interface (Cape-B-2). "XO" is a legacy/internal working
  name still present in some script and file names (e.g. `gen_xo_sch.py`) — TACCO is the
  canonical current name; see `avionics/AGENTS.md` "Cape Naming and Revision History."
- Optional: **Commo** cape (49 MHz + SiK transceivers) — installed only on River's Room (Bay C) and
  Simon's Medbay (Bay D); see `avionics/AGENTS.md` for the current per-bay cape loadout.

**Flight Engineer** (Power Distribution Board) sits in the middle-section inner neck, minimizing
power-run length to all four nacelles and the battery.

**Observer** (standalone vision/ToF/laser board — not a PB2-I cape) installs at the nose and
cargo-bay mounting sites, connected via the Ethernet ring and CAN FD trunk. It shares the
Ethernet ring with the 8 PACE nodes but is not itself one of them, so the ring's actual physical
node count exceeds 8 — see `avionics/AGENTS.md` and `avionics/kicad/Observer/Observer.md`.

**Bus-Gateway** (CAN-PERIPH-GW-1) is a secure CAN-FD/RS-485 edge node that brings bus connectivity
to sensors/actuators that lack it natively — nacelle tilt Hall-effect encoders, SG90
micro-servos (winch, cargo door), and per-EDF ESC telemetry. It is deployed in multiple physical
instances (per-nacelle encoder gateway, per-EDF ESC gateway, cargo-door servo gateway); see
`avionics/kicad/Bus-Gateway/CAN-PERIPH-GW-1.md`. The Pilot/TACCO README bullets below describe
these signals as if read/driven locally; several have since moved to bus-networked control
through Bus-Gateway — check the per-board `.md` files for current wiring before assuming a
local GPIO/analog connection.

**Encoder** (ENC-NACELLE-1) is the nacelle tilt-angle sensor PCB (AK7455 off-axis magnetoresistive
encoder); it now reports over CAN-FD/RS-485 through Bus-Gateway rather than being read directly
by Pilot — see `avionics/kicad/Encoder/ENC-NACELLE-1.md`.

## Onboard Bus Architecture

| Bus | Protocol | Nodes | Purpose |
|-----|----------|-------|---------|
| CAN FD | 1 Mbps nominal / 8 Mbps data | 8 PACE nodes + Bus-Gateway instances + Observer | Primary telemetry, ESC heartbeat, sensor fusion, failover signaling |
| RS-485 | Half-duplex | 8 PACE nodes + Bus-Gateway instances | Backup command/telemetry (fallback if CAN FD fails) |
| Ethernet | RSTP ring | 8 PACE nodes (via Pilot's dual PHYs, J_ETH1/J_ETH2) + Observer | High-bandwidth sensor data, inter-node video/imaging streams |
| MIL-STD-1553C | Dual redundant buses | 8 PACE nodes | Deterministic real-time control (legacy compatibility, backup) |
| UART | Various | Cape headers | Serial debugging, bootloader, optional mission-specific sensors |

## External Comms (5 Independent Paths)

All five paths are **authenticated, signed, logged**. Availability differs by stack: every
stack's TACCO cape carries Wi-Fi, ZigBee, and mLRS; only River and Simon additionally carry a
Commo cape (49 MHz + SiK) — see root `AGENTS.md` §9 for the per-stack primary/secondary
assignment.

1. **Wi-Fi 5 GHz** — MAVLink to QGroundControl; primary for higher-bandwidth development
   flights; range limited (<500 m line-of-sight); all 4 stacks (TACCO)
2. **ZigBee 2.4 GHz** — MAVLink fallback; robust link in congested RF environments; all 4 stacks
   (TACCO, Murata Type 2EL module shared with Wi-Fi)
3. **mLRS (Seeed Wio-E5 / STM32WLE5)** — LoRa-class long-range link; all 4 stacks (TACCO). Moved
   here from TACCO's prior SiK radio in the 2026-09-21 relocation; serves as Shepherd's and
   Inara's long-range fallback since neither stack carries a Commo cape
4. **MAVLink/SiK 915 MHz** — Licensed ISM band; range ~5 km (open field, typical line-of-sight);
   **River and Simon only**, via Commo (RFD900ux-SMT) — moved here from TACCO in the same
   2026-09-21 relocation
5. **49 MHz (Part 15 §15.235)** — Unlicensed, extremely low power (~30 µW EIRP); **River and
   Simon only**, via Commo; forward and aft wire antennas (see `XCVR-49MHZ` in BOM); carries
   encrypted command/telemetry; requires FCC pre-compliance (energy-limited but not
   power-limited per Part 15)

## PCB Boards

Board revisions, sch↔PCB parity, ERC/DRC status, and exact IC/rail specs move fast and are
tracked at the source — each board's own `avionics/kicad/<board>/<board>.md`, cross-referenced
from `avionics/TODO.md` §1.2. The summaries below are architectural (what the board does, not
its exact current bring-up state); confirm specifics against the per-board `.md` before relying
on them for fab, BOM, or integration decisions.

### Pilot (Cape-A-2) — Flight Control + Sensors

- **Processor:** PocketBeagle2 Industrial (Cortex-A53, dual PRU real-time subsystem)
- **Sensors:** 9-DOF IMU, barometric altimeter, GPS (u-blox M10Q)
- **Motor Control:** 4× PWM outputs (ESC1–4) for nacelle EDFs; isolated gate drivers
- **Actuators/feedback:** tilt servo, door servo, and winch servo control, plus nacelle tilt
  angle feedback (AK7455 encoder) are being migrated to bus-networked control via Bus-Gateway
  rather than driven/read locally — see `avionics/kicad/Pilot/Pilot.md` and
  `avionics/kicad/Bus-Gateway/CAN-PERIPH-GW-1.md` for current wiring
- **Isolation:** galvanic isolation on external buses (CAN FD, RS-485, Ethernet)
- **Security:** TPM 2.0 (SLB9672) for attestation; CPLD write-blocker on log μSD
- Status: `avionics/kicad/Pilot/Pilot.md`

### TACCO (Cape-B-2) — Comms / Logging / Payload

- **Radio:** mLRS on a Seeed Wio-E5 (STM32WLE5) module, replacing this board's prior SiK radio
  in the 2026-09-21 relocation (SiK moved to Commo — see below); dedicated UART also serves the
  49 MHz transceiver module (XCVR-49MHZ-1/2). This board carries neither SiK nor LoRa/RFM95W now
- **Logging:** eMMC mass storage (OS + runtime logs); μSD slot (flight logs, write-blocked)
- **Payload Interface:** cargo door/winch servo and sensor-expansion I/O — see Pilot note above;
  much of this is moving to Bus-Gateway rather than local GPIO
- **Isolation:** galvanic isolation on all buses
- **Security:** TPM 2.0; CPLD write-blocker on μSD
- Status: `avionics/kicad/TACCO/TACCO.md`

### Commo — 49 MHz + SiK Transceiver

- **Radios:** 49 MHz transceiver (Si5351A-based tunable DDS/PLL, MMBT2222A + 2N3866 PA,
  ~30 µW max EIRP) **plus SiK (RFD900ux-SMT)**, relocated here from TACCO in the 2026-09-21
  radio swap in exchange for Commo's prior LoRa/RFM95W module (removed)
- **Installed only on:** River's Room (Bay C) and Simon's Medbay (Bay D) — maximizes antenna
  diversity and geographic spread for robust long-range comms
- **Isolation:** galvanic isolation
- **Known open item:** the existing hand-placed PCB layout has no contiguous free area for the
  SiK module without touching the Ethernet PHY footprint — a floorplan pass is still needed
  before fab; see status file
- Status: `avionics/kicad/Commo/Commo.md`

### Flight Engineer (Power Distribution Board)

- **Inputs:** Dual 6S LiPo battery rails (independent, cross-tied with fault-tolerant diodes)
- **Outputs:** 5V avionics rail, 6V servo rail, and a dedicated 5V Observer payload rail
  (`U_BEC_OBS` → `J_OBS`, separate from the shared avionics bus)
- **Protection:** 40A main fuses (one per battery rail); over-current monitoring
- **Security:** TPM 2.0 (SLB9672) + isolated CAN-FD/RS-485, per the zero-trust cape policy
- **Placement:** Middle-section inner neck (ventral, open access for field maintenance)
- Status: `avionics/kicad/FlightEngineer/FlightEngineer.md`

### Observer (Vision / ToF / Laser Board)

Standalone board (not a PB2-I cape); one shared design installed at two physical sites — bow
sensor pod (nose) and cargo-bay nadir FPV mount.

- **Vision:** TI AM62A7 SoC (PCM-071 SoM carrier) with ISP/VP8 encoder for onboard H.265 video
- **ToF Sensors:** TFmini-S UART (nose) + 12× VL53L5CX (8×2 Array) for obstacle avoidance and
  precision landing
- **Laser Indicator:** single shared 520 nm green source; per-site optics and IEC 60825-1 class
  are a live engineering analysis, not a fixed spec — see `docs/OBSERVER_LASER_ANALYSIS.md`
- **Comms:** Gigabit Ethernet (KSZ9477 switch), CAN FD, TPM 2.0 (SLB9672) for signed image
  metadata; an RS-485 addition is in the schematic but not yet synced to the PCB layout — see
  status file
- **Mounting:** Nose sensor pod + cargo-bay FPV housing; connected via shielded Ethernet ring
- Status: `avionics/kicad/Observer/Observer.md`

### Bus-Gateway (CAN-PERIPH-GW-1) — Secure CAN-FD/RS-485 Edge Node

- **Purpose:** brings authenticated bus connectivity to sensors/actuators without native bus
  interfaces — nacelle tilt Hall-effect encoders, SG90 micro-servos (winch, cargo door),
  per-EDF ESC telemetry
- **Security:** TPM 2.0 (SLB9672), isolated CAN-FD (ISOW1044) and RS-485 (ADM2795E)
- **Deployment:** multiple physical instances, one per gateway role (see status file for the
  current list)
- Status: `avionics/kicad/Bus-Gateway/CAN-PERIPH-GW-1.md`

### Encoder (ENC-NACELLE-1) — Nacelle Tilt Encoder PCB

- **Sensor:** AK7455 off-axis magnetoresistive tilt encoder, one per nacelle
- **Interface:** reports over CAN-FD/RS-485 through Bus-Gateway, not read directly by Pilot
- Status: `avionics/kicad/Encoder/ENC-NACELLE-1.md`

## Firmware

### Node Firmware (`avionics/firmware/`)

- **serenity-cn** (Comms Node) — runs on TACCO boards (all 8 nodes)
  - CAN FD heartbeat relay and telemetry forwarding
  - RS-485 backup messaging
  - Ethernet RSTP ring management  
  - Signed-log write via CPLD write-blocker
  - Radio (49 MHz, SiK, LoRa) telemetry encoding/decoding
  - Cargo control GPIO sequencing
  - MAVLink routing configuration

- **serenity-fc** (Flight Control) — runs on Pilot/Pilot boards (4× FC nodes: Shepherd, Inara, River, Simon)
  - ESC PID governor (nacelle thrust control)
  - Nacelle tilt servo PWM generation + sync across all 4 nacelles
  - IMU + barometer + GPS sensor fusion
  - 12× ToF sensor array fusion for obstacle avoidance
  - MIL-STD-1553C Bus Controller (Shepherd primary) / Remote Terminal (backup FC nodes)
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
| `WBS.md` | Avionics work breakdown structure |
| `TODO.md` | Avionics task tracker, federated from `WBS.md` — per-board status subsections |
| `kicad/` | KiCad source schematics and PCB layouts (all boards) |
| `kicad/Pilot/` | Pilot cape: schematic/PCB source, `Pilot.md` status file |
| `kicad/TACCO/` | TACCO cape: schematic/PCB source, `TACCO.md` status file |
| `kicad/Commo/` | Commo board: schematic/PCB source, `Commo.md` status file |
| `kicad/FlightEngineer/` | Flight Engineer PDB: schematic/PCB source, `FlightEngineer.md` status file |
| `kicad/Observer/` | Observer board specs, TI SoC bring-up scripts, laser/ToF driver code |
| `kicad/Bus-Gateway/` | Bus-Gateway (CAN-PERIPH-GW-1): schematic/PCB source, status file |
| `kicad/Encoder/` | Nacelle tilt encoder PCB (ENC-NACELLE-1): schematic/PCB source, status file |
| `firmware/` | C source code for Pilot/TACCO node firmware; CMake build system |
| `emi-hardening/` | EMI isolation analysis, shielding specs, harness routing rules |
| `rev-s1/` | Historical Rev S1 PCB redesign notes (superseded by later per-board revisions) |

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
