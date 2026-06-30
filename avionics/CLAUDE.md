# Avionics Design — Claude Code Project Instructions

> *See the root `CLAUDE.md` for project-wide policies. This file provides specific guidance for avionics design, KiCad PCBs, capes, and microcontroller configuration.*

## Scope

This folder contains all electronics design and implementation: KiCad schematics and PCB layouts for avionics capes, microcontroller firmware, boot loaders, TPM configurations, and communications stack documentation. The avionics architecture is built on redundancy and failover across eight industrial SBCs distributed throughout the airframe.

## Onboard Avionics Architecture — 8-Node Cooperative System

**Platform:** Four pairs of **PocketBeagle2 Industrial SBCs** (8 nodes total, Rev R1 placement):
- All 8 nodes carry **Wash** (Flight Control and Sensor Cape) and **Zoë** (Communications, Logging, and Payload Cape)
- All 8 nodes carry **TPM** (Trusted Platform Module) for cryptographic operations

**Emma Transceiver Cape** (49 MHz Part 15 §15.235 + LoRa 915 MHz):
- Installed in **River's Room** (Bay C, starboard cargo) and **Simon's Medbay** (Bay D, middle section) only
- Emma Rev R1: adds LoRa, replaces JST GH 6P with P1+P2 socket rails
- Connects via P1+P2 socket rails on Wash and Zoë (as of Rev R1)

**Power Distribution — Kaylee (PDB):**
- Central location: inner neck of middle section, minimizes power run lengths to all four nacelles, all four avionics stacks, and the battery
- Interfaces with all four flight-control nodes for EDF and servo control

### Node Workload Balancing and PACE Failover

All Wash capes are identical and all Zoë capes are identical, but each stack has **primary and alternative tasking** with PACE prioritization (Primary, Alternative, Contingency, Emergency):

#### Shepherd's Room (Bay A) — Forward Avionics
**Primary tasking:** watchdog, fault detection, failover, authentication  
**Stack:** Wash + Zoë  
**Comms:** SiK primary / Wi-Fi secondary  
**PACE assignments:**
- Watchdog: **P**rimary
- Comms: **A**lternative
- Flight Control: **C**ontingency
- Payload Control: **E**mergency

#### Inara's Shuttle (Bay B) — Port Avionics
**Primary tasking:** camera, external sensors, high-bandwidth ground communications  
**Stack:** Wash + Zoë  
**Comms:** Wi-Fi primary / LoRa secondary (Note: LoRa moved to Emma boards on River/Simon in Rev R1)  
**PACE assignments:**
- Watchdog: **A**lternative
- Comms: **P**rimary
- Flight Control: **E**mergency
- Payload Control: **C**ontingency

#### River's Room (Bay C) — Starboard Avionics
**Primary tasking:** forward EDF control, nacelle tilt command/sync, resilient comms  
**Stack:** Wash + Zoë + **Emma** (49 MHz primary, LoRa secondary)  
**Comms:** 49 MHz (Part 15 §15.235) primary / LoRa 915 MHz secondary  
**PACE assignments:**
- Watchdog: **C**ontingency
- Comms: **E**mergency
- Flight Control: **P**rimary
- Payload Control: **A**lternative

#### Simon's Medbay (Bay D) — Aft Avionics
**Primary tasking:** aft EDF control, alternate watchdog, cargo/payload oversight  
**Stack:** Wash + Zoë + **Emma** (49 MHz primary, LoRa secondary)  
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

### Wash — Flight Control and Sensor Cape

Provides flight control input, sensor fusion, and motor speed control via PID:
- GPS receiver
- Inertial Measurement Unit (IMU)
- Compass / magnetometer
- Barometer / altimeter
- Anti-collision range sensors
- Airspeed sensor
- PID motor speed control for EDFs
- Nacelle tilt servo control

**Current revision:** Cape-A-2 (Rev R1)  
**Status:** Archived: Cape-A-1

### Zoë — Communications, Logging, and Payload Cape

Provides external communications, onboard logging, and payload interface:
- All four external radio transceivers (Wi-Fi, Zigbee, SiK/MAVLink, protocol stack software)
- Onboard data logging to hardware-enforced non-executable microSD card
- Payload I/O interfaces

**Current revision:** Cape-B-2 (Rev R1)  
**Planned (not yet in KiCad):** Rev R1 (remove LoRa, add P1+P2 passthrough rails matching Emma's pinout on River and Simon stacks)  
**Status:** Archived: Cape-B-1  
**LoRa note:** As of Rev R1, LoRa functionality migrated to Emma boards (River and Simon stacks only); Zoë.kicad_sch still carries JST-GH 6P Emma connector from earlier revision but this will be replaced with P1+P2 rails in the planned Rev R1 redesign.

### Emma — 49 MHz + LoRa Transceiver Cape (Rev R1)

Provides unlicensed-band communications for environments with restricted radio access:
- 49 MHz transceiver (47 CFR Part 15 §15.235 — unlicensed, suitable for high-RF-field environments)
- LoRa 915 MHz radio (Rev R1 addition)
- Galvanically isolated transceiver interfaces

**Current revision:** XCVR-49MHZ-2 Rev R1 (adds LoRa, replaces JST GH 6P with P1+P2 socket rails)  
**Installed in:** River's Room (Bay C) and Simon's Medbay (Bay D) only  
**Status:** Archived: XCVR-49MHZ-1, Cape-A-1, Cape-B-1

### Kaylee — Power Distribution Board (PDB)

Central power management and distribution:
- Battery management system
- 6V servo rail: TPS54540DDAR regulator (planned removal in Kaylee Rev A1; tilt servos to run on 5V rail)
- 5V main avionics rail
- EDF power distribution and PID control lines to all flight-control nodes

**Current revision:** Kaylee (pre-A1)  
**Planned (not yet in KiCad):** Rev A1 (remove 6V servo BEC; tilt servos to run on 5V rail with ~21 kg·cm capacity vs ~16 kg·cm tilt load requirement)  
**Location:** Inner neck of middle section (Kaylee's room), adjacent to Simon's Medbay

## PCB Design Standards

### Design Rules Checker (DRC) Workflow

Every schematic and PCB modification **must** be verified:

1. Open the schematic file in KiCad
2. Run **Electrical Rules Checker** (ERC) — resolve all violations and warnings
3. Open the PCB layout
4. Run **Design Rules Checker** (DRC) — resolve all violations and errors
5. Document any violations that cannot be resolved in `TODO.md` with the specific DRC rule and reason
6. Commit only after all DRC violations are either resolved or documented

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

---

For project-wide standards, see the root `CLAUDE.md`.
