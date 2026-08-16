# Avionics Design — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for avionics design, KiCad PCBs, capes, and microcontroller configuration.*

## Scope

This folder contains all electronics design and implementation: KiCad schematics and PCB layouts for avionics capes, microcontroller firmware, boot loaders, TPM configurations, and communications stack documentation. The avionics architecture is built on redundancy and failover across eight industrial SBCs distributed throughout the airframe.

## Onboard Avionics Architecture — 8-Node Cooperative System

**Platform:** Four pairs of **PocketBeagle2 Industrial SBCs** (8 nodes total, Rev S placement,
established at Rev R1):
- All 8 nodes carry **Pilot** (Flight Control and Sensor Cape) and **TACCO** (Communications, Logging, and Payload Cape)
- All 8 nodes carry **TPM** (Trusted Platform Module) for cryptographic operations

**COMMO Transceiver Cape** (49 MHz Part 15 §15.235 + LoRa 915 MHz — see "Cape Naming and
Revision History" below for current build status):
- Installed in **River's Room** (Bay C, starboard cargo) and **Simon's Medbay** (Bay D, middle section) only

**Power Distribution — FlightEngineer (PDB):**
- Central location: inner neck of middle section, minimizes power run lengths to all four nacelles, all four avionics stacks, and the battery
- Interfaces with all four flight-control nodes for EDF and servo control

### Node Workload Balancing and PACE Failover

All Pilot capes are identical and all TACCO capes are identical, but each stack has **primary and alternative tasking** with PACE prioritization (Primary, Alternative, Contingency, Emergency):

#### Shepherd's Room (Bay A) — Forward Avionics
**Primary tasking:** watchdog, fault detection, failover, authentication  
**Stack:** Pilot + TACCO  
**Comms:** SiK primary / Wi-Fi secondary  
**PACE assignments:**
- Watchdog: **P**rimary
- Comms: **A**lternative
- Flight Control: **C**ontingency
- Payload Control: **E**mergency

#### Inara's Shuttle (Bay B) — Port Avionics
**Primary tasking:** camera, external sensors, high-bandwidth ground communications  
**Stack:** Pilot + TACCO  
**Comms:** Wi-Fi primary / LoRa secondary (LoRa is migrating from TACCO to COMMO on River/Simon —
see "Cape Naming and Revision History" below for current build status)  
**PACE assignments:**
- Watchdog: **A**lternative
- Comms: **P**rimary
- Flight Control: **E**mergency
- Payload Control: **C**ontingency

#### River's Room (Bay C) — Starboard Avionics
**Primary tasking:** forward EDF control, nacelle tilt command/sync, resilient comms  
**Stack:** Pilot + TACCO + **COMMO** (49 MHz primary; LoRa secondary migrating onto COMMO — see
"Cape Naming and Revision History" below for current build status)  
**Comms:** 49 MHz (Part 15 §15.235) primary / LoRa 915 MHz secondary  
**PACE assignments:**
- Watchdog: **C**ontingency
- Comms: **E**mergency
- Flight Control: **P**rimary
- Payload Control: **A**lternative

#### Simon's Medbay (Bay D) — Aft Avionics
**Primary tasking:** aft EDF control, alternate watchdog, cargo/payload oversight  
**Stack:** Pilot + TACCO + **COMMO** (49 MHz primary; LoRa secondary migrating onto COMMO — see
"Cape Naming and Revision History" below for current build status)  
**Comms:** 49 MHz (Part 15 §15.235) primary / SiK secondary  
**PACE assignments:**
- Watchdog: **A**lternative
- Comms: **C**ontingency
- Flight Control: **A**lternative
- Payload Control: **P**rimary

### Communication Protocols

**Onboard:**
- CAN FD (galvanically isolated at every node via Cape-A-2 and Cape-B-2)
- MIL-STD 1553 (legacy, being phased)
- RS-485 (galvanically isolated at every node)
- Ethernet (galvanically isolated at every node)

**External command and control (all four usable for autonomous or manual C2):**
- Wi-Fi at 5 GHz
- Zigbee at 2.4 GHz
- MAVLink / SiK at 915 MHz
- AX.25 on 49 MHz channel (47 CFR Part 15 §15.235 — unlicensed, not Part 95 RCRS)

**S-Bus:** Supported by avionics capes but not currently used.

## Cape Naming and Revision History

Board architecture, sch↔pcb parity status, and reconciliation progress change frequently and
are tracked at the source, not duplicated here. **For any board, the authoritative,
most-current status is that board's own `.md` file** under `avionics/kicad/<board>/` (e.g.
`Pilot.md`, `TACCO.md`, `COMMO.md`, `FlightEngineer.md`, `Observer.md`) plus the matching `TODO.md` §1.2
subsection — read those before starting work, and do not assume this file's stable-fact
summary below reflects today's as-built state.

### Pilot — Flight Control and Sensor Cape

Flight control input, sensor fusion, and PID motor speed control: GPS, IMU, compass,
barometer, anti-collision range sensors, airspeed sensor, EDF PID control, nacelle tilt servo
control. Current build designation: Cape-A-2. Status/history: `avionics/kicad/Pilot/Pilot.md`.

### TACCO — Communications, Logging, and Payload Cape

External communications, onboard logging, payload interface: all four external radio
transceivers, onboard data logging to hardware-enforced non-executable microSD, payload I/O.
Current build designation: Cape-B-2. Status/history: `avionics/kicad/TACCO/TACCO.md`, TODO.md
§1.2b.

### COMMO — 49 MHz + LoRa Transceiver Cape

Unlicensed-band communications for high-RF-field environments: 49 MHz transceiver (47 CFR
Part 15 §15.235) plus LoRa 915 MHz, both galvanically isolated. Installed only in River's Room
(Bay C) and Simon's Medbay (Bay D). Connects via P1+P2 socket rails (Rev R1; replaces the
legacy JST GH 6P). Status/history: `avionics/kicad/COMMO/COMMO.md`, TODO.md §1.2b.

### Observer — Cargo-Handling System and Nose/Cargo-Bay Vision, ToF & Laser Board

One integrated subsystem covering both the mechanical cargo-handling hardware (winch, latch,
cargo bay door) and the vision/ToF/laser sensing board. Historical references to "Vera" (an
earlier working name for the sensing board) refer to this same board.

**Observer is a standalone PCB — not a PocketBeagle 2 Industrial cape.** It does not use the
P1+P2 header stack and does not mount on a Pilot/TACCO node; it connects to the rest of the
airframe only via the shielded JST-GH Ethernet ring and CAN-FD trunk connectors, with its own
5V power input. One shared board design is installed at two physical locations: the bow
sensor pod (nose) and the cargo bay nadir FPV mount, the latter co-located with the mechanical
cargo-handling hardware it supervises. It supersedes the RunCam Nano 4 analog camera
(REF-SENSOR-001, superseded).

**Do not restate Observer's chip-level architecture, EMI hardening, or fabrication status here —
it has changed materially between doc passes and this section has gone stale before.**
Canonical source: `avionics/kicad/Observer/Observer.md`, TODO.md §1.2c (hardware) and §4.6
(firmware).

**Laser indicator:** single shared 520 nm green source; per-site optics and IEC 60825-1
class are a live engineering analysis, not a fixed spec — canonical source:
`docs/JAYNE_LASER_ANALYSIS.md` (current revision), TODO.md §1.2c.4.

### FlightEngineer — Power Distribution Board (PDB)

Battery management, EDF power distribution, and PID control-line routing to all
flight-control nodes. Location: inner neck of the middle section (FlightEngineer's room), adjacent to
Simon's Medbay — minimizes power-run length to all nacelles, all four stacks, and the battery.
Status/history (including the planned 6V-servo-BEC removal): `avionics/kicad/FlightEngineer/FlightEngineer.md`,
TODO.md §1.2b.

## PCB Design Standards

### Design Rules Checker (DRC) Workflow

Every schematic and PCB modification **must** be verified:

1. Open the schematic file in KiCad
2. Run **Electrical Rules Checker** (ERC) — resolve all violations and warnings
3. Open the PCB layout
4. Run **Design Rules Checker** (DRC) — resolve all violations and errors
5. Document any violations that cannot be resolved in `TODO.md` with the specific DRC rule and reason
6. Commit only after all DRC violations are either resolved or documented
7. All routing and component spacing will maintain 0.3mm minimum copper spacing (as enforced by the min_copper_edge_clearance DRC check) per [REF-IPC-001].

### Footprint and Component Placement

**Critical note:** PCBs are tightly packed. All final component footprint positions will be placed manually after PCBs are populated and nets are built by script.

- If a DRC violation requires repositioning a component footprint, **refer the action to the user**
- Other modifications (net routing, trace widening, via placement) are allowed without user confirmation

### Schematics and PCB Files

- Every cape requires:
    - Complete schematic file (`.kicad_sch`)
    - Complete PCB layout (`.kicad_pcb`)
    - Copper traces ready for production
    - Proper IC footprints for all components
    - Production-ready Gerber files

## Security and Cryptography Requirements

Every message, internal and external, must be:
- **Digitally signed** and authenticated
- **Logged** for forensic analysis
- **Timestamped** by the TPM

### TPM (Trusted Platform Module)

- Every node carries a TPM for cryptographic operations
- All keys are generated and stored on the TPM, never in software
- All messages are signed using TPM-held keys

### Data Logging

- Everything is logged: sensor data, CAN messages, MAVLink commands, camera feed, authentication events
- Logs are saved to **hardware-enforced non-executable microSD cards** (write-once, never executable)
- All logs are signed and timestamped

### Zero Trust Architecture Compliance

All avionics design shall comply with **NIST SP 800-207 Zero Trust Architecture** [REF-NIST-001 §2.1, §2.2, §3.3]:
- Assume breach: expect both external and internal attacks
- Verify every transaction: no implicit trust based on network location
- Authenticate every message and every node state change
- Least privilege: each node operates with minimum required permissions
- Micro-segmentation: isolate avionics bays with galvanic isolation and message authentication

## External Communications Regulations Compliance

All radio transmissions must comply with **FCC regulations**:

- **49 MHz band:** 47 CFR Part 15 §15.235 (unlicensed ISM, not Part 95 RCRS) — used for high-RF-field environments
- **915 MHz SiK/MAVLink:** 47 CFR Part 15 §15.247 (unlicensed ISM)
- **2.4 GHz Zigbee:** 47 CFR Part 15 §15.247 (unlicensed ISM)
- **5 GHz Wi-Fi:** 47 CFR Part 15 §15.407 (unlicensed UNII)

Citations: [REF-FCC-001, REF-FCC-002, REF-FCC-003]

## Work Tracking and Documentation

When modifying or creating cape designs:

1. Update the relevant `.kicad_sch` and `.kicad_pcb` files
2. Run ERC and DRC; document any violations in `TODO.md` with the reason
3. Update the cape description in `REFERENCES.md` if the design scope has changed
4. If planning a new cape revision, record it in `TODO.md` and cite this file
5. Keep `PROJECT_INDEX.md` up to date with new KiCad files
6. Archive old cape revisions in `archives/` with a note in `ARCHIVE_INDEX.md`
7. Check for component datasheets in the `avionics/datasheets` folder, kicad symbols in the `avionics/kicad/symbols` folder, and footprints in the `avionics/kicad/symbols/footprints` folder before searching online.
8. Use OEM Datasheets as authitative component references.

---

For project-wide standards, see the root `AGENTS.md`.
